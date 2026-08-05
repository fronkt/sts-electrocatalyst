"""R3: evaluate an MLIP against the QC-gated DFT tier on the CHE observable.

Why this exists
---------------
docs/29 established that no out-of-box UMA head ranks rutile OER (oc22 rho = -1.00).
`e0_stage0.py` then showed the failure cannot be a reference-energy artefact, because
the CHE reference is stoichiometrically closed and projects out every composition-
linear term. So the question R3 has to answer is whether *fine-tuning on our own QE
trajectories* fixes the local chemistry -- relative *O vs *OH binding across metals.

Two properties of the Stage 0 result shape this module:

  * **No recalibration is needed or allowed.** A foundation model trained on a
    different functional, different pseudopotentials, even a different energy zero can
    be compared to our PBE+U dG directly: the offset cancels exactly. Anyone "aligning"
    the energies first is fitting noise.
  * **Energy MAE is not the gate.** E0 alone can shrink MAE a long way while leaving
    every eta identical. The gate is the CHE observable.

What it measures
----------------
Single-point energies on the **DFT-relaxed** geometries, which isolates the model's
energetics from its relaxation behaviour. That is the cleaner first question: a model
that cannot rank dG on the correct geometry will not be rescued by relaxing it itself.
(Relaxed-geometry evaluation is the follow-up, not a substitute -- flagged in the
output so the two never get confused.)

Targets, all QC-gated (`qe_qc.trusted_energy_ev`):

  * 15 adsorption free energies -- 5 metals x {*OH, *O, *OOH}. The primary metric:
    3x the data of the eta ranking, and not degenerate.
  * 5 overpotentials, and their Spearman rho. The headline number, but weak: docs/32
    measured the DFT tier's own differential resolution at ~0.17 V, which makes
    {Mn, Ru, Ir} a tie rather than an ordering.

Usage
-----
    PYTHONPATH=src python src/dft/mlip_eval.py baseline --model medium-mpa-0
    PYTHONPATH=src python src/dft/mlip_eval.py baseline --model medium --limit Cr,Ru
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hea_oer.referencing import delta_G  # noqa: E402
from hea_oer.descriptors import oer_overpotential  # noqa: E402

#: metals with a complete, QC-passing DFT CHE chain (docs/30, docs/32)
EVALUABLE = ["Cr", "Mn", "Fe", "Ru", "Ir"]
#: directory suffix per metal
DIRNAME = {"Cr": "Cr_slab", "Mn": "Mn_slab", "Fe": "Fe_slab",
           "Ru": "Ru_anchor", "Ir": "Ir_anchor"}
STATES = ["slab", "s0_O", "s0_OH", "s0_OOH", "H2O", "H2"]


def final_frames(extxyz: str) -> dict:
    """Last (most-relaxed) frame per source, as ase.Atoms."""
    from ase.io import read
    best: dict = {}
    for at in read(extxyz, ":"):
        src = at.info["source"]
        step = int(at.info.get("step", 0))
        if src not in best or step > best[src][0]:
            best[src] = (step, at)
    return {k: v[1] for k, v in best.items()}


def che_from_energies(E: dict) -> dict:
    """dG_OH/dG_O/dG_OOH + eta from a dict of six total energies (eV)."""
    dG = {s: delta_G(E["slab"], E[k], s, E["H2O"], E["H2"])
          for s, k in (("OH", "s0_OH"), ("O", "s0_O"), ("OOH", "s0_OOH"))}
    r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
    return dict(dG_OH=dG["OH"], dG_O=dG["O"], dG_OOH=dG["OOH"],
                eta=r.overpotential, pls=r.potential_limiting_step)


def dft_reference(root: str = "runs") -> dict:
    """QC-gated DFT truth per metal. Never falls back to an ungated energy."""
    from dft.qe_qc import trusted_energy_ev
    out = {}
    for m in EVALUABLE:
        d = os.path.join(root, DIRNAME[m])
        E = {}
        for s in STATES:
            E[s] = trusted_energy_ev(os.path.join(d, s + ".out"),
                                     os.path.join(d, s + ".in"))
        if any(v is None for v in E.values()):
            missing = [s for s, v in E.items() if v is None]
            raise SystemExit(f"{m}: QC rejected {missing} -- refusing to build a target")
        out[m] = che_from_energies(E)
    return out


def spearman(a, b):
    def rank(x):
        order = sorted(range(len(x)), key=lambda i: x[i])
        r = [0.0] * len(x)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    ra, rb = rank(a), rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    da = sum((ra[i] - ma) ** 2 for i in range(n)) ** 0.5
    db = sum((rb[i] - mb) ** 2 for i in range(n)) ** 0.5
    return num / (da * db) if da and db else 0.0


def exact_two_sided_p(rho_obs: int | float, n: int) -> float:
    """Exact permutation p (no asymptotics). n<=8 only; that is all we ever have.

    Counts the upper tail and doubles it, which is the correct two-sided p **only
    because the null distribution of rho is symmetric about 0** -- and therefore only
    if the tail is measured from |rho|. Taking rho_obs at face value made this return
    ~1.0 for any negative correlation (nearly every permutation exceeds a negative
    rho), which is silently wrong rather than loudly wrong.

    Every use in the campaign until 2026-08-05 was on the positive R0/R3 gate, where
    abs() is the identity, so no published number changes. The first negative
    correlation measured -- activity vs solubility across the screen, rho = -0.657 --
    is what exposed it.
    """
    from itertools import permutations
    from math import factorial
    r = abs(float(rho_obs))
    ref = list(range(n))
    cnt = 0
    for p in permutations(ref):
        d2 = sum((ref[i] - p[i]) ** 2 for i in range(n))
        if 1 - 6 * d2 / (n * (n * n - 1)) >= r - 1e-12:
            cnt += 1
    return min(1.0, 2 * cnt / factorial(n))


def evaluate(calc, frames: dict, metals=None) -> dict:
    """Single-point the calculator on DFT-relaxed geometries; return CHE per metal."""
    metals = metals or EVALUABLE
    got = {}
    for m in metals:
        d = DIRNAME[m]
        E = {}
        for s in STATES:
            key = f"{d}/{s}"
            at = frames.get(key)
            if at is None:
                E = None
                print(f"  {m}: missing frame {key}", file=sys.stderr)
                break
            a = at.copy()
            a.calc = calc
            E[s] = a.get_potential_energy()
        if E:
            got[m] = che_from_energies(E)
    return got


def report(pred: dict, ref: dict, label: str,
           mode: str = "single-point on DFT-relaxed geometries") -> dict:
    # `mode` is passed explicitly by the relaxed path. Labelling a model-relaxed run as
    # single-point would misrepresent which half of the problem the model actually
    # solved -- a single-point on the DFT geometry is handed the answer to the other.
    metals = [m for m in EVALUABLE if m in pred]
    print(f"\n{'='*78}\n{label}\n  mode: {mode}\n{'='*78}")
    print(f"{'':4} {'dG_OH':>16} {'dG_O':>16} {'dG_OOH':>16} {'eta':>16}")
    print(f"{'':4} {'pred    dft':>16} {'pred    dft':>16} {'pred    dft':>16} {'pred    dft':>16}")
    errs = defaultdict(list)
    for m in metals:
        p, r = pred[m], ref[m]
        cells = []
        for k in ("dG_OH", "dG_O", "dG_OOH", "eta"):
            errs[k].append(p[k] - r[k])
            cells.append(f"{p[k]:>7.3f} {r[k]:>7.3f}")
        print(f"{m:4} " + " ".join(f"{c:>16}" for c in cells))

    print(f"\n{'metric':<26}{'MAE':>9}{'max|err|':>10}{'signed mean':>13}")
    for k in ("dG_OH", "dG_O", "dG_OOH"):
        e = errs[k]
        print(f"  {k:<24}{sum(map(abs,e))/len(e):>9.3f}{max(map(abs,e)):>10.3f}{sum(e)/len(e):>13.3f}")
    allads = errs["dG_OH"] + errs["dG_O"] + errs["dG_OOH"]
    print(f"  {'ALL 15 adsorption dG':<24}{sum(map(abs,allads))/len(allads):>9.3f}"
          f"{max(map(abs,allads)):>10.3f}{sum(allads)/len(allads):>13.3f}")
    e = errs["eta"]
    print(f"  {'eta':<24}{sum(map(abs,e))/len(e):>9.3f}{max(map(abs,e)):>10.3f}{sum(e)/len(e):>13.3f}")

    pe = [pred[m]["eta"] for m in metals]
    re_ = [ref[m]["eta"] for m in metals]
    rho = spearman(pe, re_)
    print(f"\n  Spearman rho(eta) = {rho:+.3f}   n = {len(metals)}   "
          f"exact two-sided p = {exact_two_sided_p(rho, len(metals)):.4f}")
    print(f"  descriptor rho    = {spearman([pred[m]['dG_O']-pred[m]['dG_OH'] for m in metals], [ref[m]['dG_O']-ref[m]['dG_OH'] for m in metals]):+.3f}"
          "   (dG_O - dG_OH; OOH-independent)")
    print("\n  NOTE: docs/32 puts the DFT tier's own differential resolution at ~0.17 V,")
    print("  so {Mn, Ru, Ir} are a tie in the truth. Read rho(eta) with that in mind;")
    print("  the 15-point adsorption-dG MAE is the better-powered metric.")
    return dict(pred=pred, ref=ref, rho_eta=rho,
                mae_dG=sum(map(abs, allads)) / len(allads),
                mae_eta=sum(map(abs, e)) / len(e), metals=metals)


def evaluate_relaxed(calc, frames: dict, metals=None, fmax=0.05, steps=200) -> dict:
    """Relax with the model, then take its energies -- the like-for-like UMA test.

    The stored UMA records (runs/*/uma_eta_1p2_oc22.json) come from UMA relaxing each
    structure itself (their `qc` blocks log 16-52 optimizer steps), so a single-point
    on DFT-relaxed geometry is NOT comparable to them: it hands the model the answer
    to the geometry half of the problem. This function does what UMA did.

    Constraints mirror the DFT exactly -- the bottom-half `free == 0` atoms stay fixed
    (the `free` array is carried per frame by qe_frames). fmax = 0.05 eV/A matches the
    DFT forc_conv_thr of 2e-3 Ry/au = 0.0514 eV/A.
    """
    from ase.constraints import FixAtoms
    from ase.optimize import BFGS
    metals = metals or EVALUABLE
    got, qc = {}, {}
    for m in metals:
        d = DIRNAME[m]
        E, info = {}, {}
        for s in STATES:
            at = frames.get(f"{d}/{s}")
            if at is None:
                E = None
                break
            a = at.copy()
            if "free" in a.arrays and s not in ("H2", "H2O"):
                a.set_constraint(FixAtoms(mask=[f == 0 for f in a.arrays["free"]]))
            a.calc = calc
            opt = BFGS(a, logfile=None)
            opt.run(fmax=fmax, steps=steps)
            f = a.get_forces()
            # report fmax over FREE atoms only (pw.x prints unconstrained forces too)
            mask = [fr != 0 for fr in a.arrays["free"]] if "free" in a.arrays else [True] * len(a)
            fm = max((sum(c * c for c in fv) ** 0.5) for fv, k in zip(f, mask) if k)
            E[s] = a.get_potential_energy()
            info[s] = dict(steps=opt.get_number_of_steps(), fmax_final=round(float(fm), 4),
                           converged=bool(fm <= fmax))
            print(f"  {m}/{s:<6} {opt.get_number_of_steps():>4} steps  fmax {fm:.4f}"
                  f"{'' if fm <= fmax else '   NOT CONVERGED'}", flush=True)
        if E:
            got[m] = che_from_energies(E)
            qc[m] = info
    return got, qc


def cmd_relaxed(args):
    frames = final_frames(args.frames)
    ref = dft_reference(args.root)
    metals = args.limit.split(",") if args.limit else EVALUABLE
    from mace.calculators import mace_mp
    print(f"loading MACE foundation model '{args.model}' (cpu) ...", flush=True)
    calc = mace_mp(model=args.model, device="cpu", default_dtype="float64")
    pred, qc = evaluate_relaxed(calc, frames, metals, fmax=args.fmax)
    res = report(pred, ref, f"MACE foundation '{args.model}', NO fine-tuning",
                 mode=f"MODEL-RELAXED by the MLIP itself (fmax={args.fmax} eV/A, DFT "
                      f"FixAtoms mirrored) -- directly comparable to the stored UMA records")
    res["relax_qc"] = qc
    unconv = [f"{m}/{s}" for m, d in qc.items() for s, v in d.items() if not v["converged"]]
    print(f"\n  relaxations not converged: {unconv or 'none'}")
    if args.out:
        json.dump(res, open(args.out, "w"), indent=2)
        print(f"-> {args.out}")
    return 0


def cmd_baseline(args):
    frames = final_frames(args.frames)
    ref = dft_reference(args.root)
    metals = args.limit.split(",") if args.limit else EVALUABLE
    from mace.calculators import mace_mp
    print(f"loading MACE foundation model '{args.model}' (cpu) ...", flush=True)
    calc = mace_mp(model=args.model, device="cpu", default_dtype="float64")
    pred = evaluate(calc, frames, metals)
    res = report(pred, ref, f"MACE foundation '{args.model}', NO fine-tuning")
    if args.out:
        json.dump(res, open(args.out, "w"), indent=2)
        print(f"\n-> {args.out}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("baseline", help="out-of-box foundation model, no fine-tune")
    b.add_argument("--frames", default="data/qe_frames.extxyz")
    b.add_argument("--root", default="runs")
    b.add_argument("--model", default="medium-mpa-0")
    b.add_argument("--limit", default="")
    b.add_argument("--out", default="")
    b.set_defaults(func=cmd_baseline)
    r = sub.add_parser("relaxed", help="model relaxes the structures itself (UMA-comparable)")
    r.add_argument("--frames", default="data/qe_frames.extxyz")
    r.add_argument("--root", default="runs")
    r.add_argument("--model", default="medium-mpa-0")
    r.add_argument("--limit", default="")
    r.add_argument("--fmax", type=float, default=0.05)
    r.add_argument("--out", default="")
    r.set_defaults(func=cmd_relaxed)
    a = ap.parse_args()
    raise SystemExit(a.func(a))


if __name__ == "__main__":
    main()
