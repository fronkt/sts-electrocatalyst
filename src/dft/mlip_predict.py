"""Predict eta for the metals we have NOT paid DFT for, before deciding what to buy.

Why this exists
---------------
docs/32 + the 2026-08-02 repair leave the tier at n = 5, and the exact permutation
arithmetic makes that a dead end: at n = 5 only a *perfect* ordering reaches p < 0.05,
and MACE-MPA-0's single error is the Ru/Ir pair our own DFT separates by 6 mV against a
measured tier resolution of ~0.17 V. At n = 6 that same single error gives rho = 0.943,
p = 0.017. So the binding constraint is the number of metals, not the model.

Three metals have complete builder inputs but no usable DFT: Ni (s0_O/s0_OH POISONED),
Co (s0_O/s0_OOH never converged), Cu (only 2 of 6 states, both POISONED). Buying one is
~$4 of GPU-box time. This module spends $0 first to answer which one is worth buying,
and hands back a *pre-registered* prediction so the DFT becomes a test rather than a fit.

A sixth point only buys power if it lands OUTSIDE the 0.78-0.89 V cluster that already
holds {Ir, Ru, Mn}. One more member of that cluster adds a coin-flip pair and nothing else.

Three things it measures
------------------------
1. **Validation on the five knowns.** The same protocol, run against metals whose DFT
   eta we have. Without this the predictions carry no error bar.
2. **Prediction for Ni / Co / Cu.**
3. **The constraint float-tie, priced.** docs/30 found the mid-plane layer was assigned
   by rounding, so the free-atom count varies by metal. It is not spread evenly:

       Cr Mn Fe Cu Ru Ir   11 free   [2,3,4,5,10,12,13,14,15,16,17]
       Co                    8 free
       Ni                    7 free

   Six of eight share one mask -- and the two exceptions are exactly the two candidates
   for the sixth point. Buying Ni or Co as-shipped would add a point relaxed under
   different freedom than the five it is being ranked against, i.e. inject a systematic
   into the very quantity the gate measures. Re-running Ni/Co on the canonical mask
   costs 4 jobs each instead of 2 (their existing TRUSTWORTHY states are on the wrong
   mask too), so the size of this bias decides whether n = 6 costs ~$4 or ~$9.

Multi-start, and why
--------------------
Single-start relaxation from the builder geometry is exactly what produced the three
defects the repair campaign had to pay to fix: Mn/Fe *OOH never left the builder's
~3.07 A placement, and Cr *O stalled at 2.016 A. Each adsorbate state is therefore
started from the builder geometry *and* from rigidly pulled-in copies at M-O = 1.70 and
2.10 A; the lowest relaxed energy wins. This is the cheap half of what cost $2.64 in DFT.

    PYTHONPATH=src python src/dft/mlip_predict.py validate
    PYTHONPATH=src python src/dft/mlip_predict.py predict --out results/r3_predict.json
    PYTHONPATH=src python src/dft/mlip_predict.py maskbias
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dft.mlip_eval import che_from_energies, dft_reference, final_frames  # noqa: E402
from dft.mlip_eval import exact_two_sided_p, spearman  # noqa: E402

N_SLAB = 18
#: the free-atom mask six of the eight metals share; the reference scheme
CANONICAL_FREE = [2, 3, 4, 5, 10, 12, 13, 14, 15, 16, 17]
DIRNAME = {"Cr": "Cr_slab", "Mn": "Mn_slab", "Fe": "Fe_slab", "Co": "Co_slab",
           "Ni": "Ni_slab", "Cu": "Cu_slab", "Ru": "Ru_anchor", "Ir": "Ir_anchor"}
KNOWN = ["Cr", "Mn", "Fe", "Ru", "Ir"]          # have a QC-gated DFT eta
UNKNOWN = ["Ni", "Co", "Cu"]                    # have builder inputs only
ADS_STATES = ["s0_O", "s0_OH", "s0_OOH"]
#: pulled-in restart distances (A). 1.70 is the median M-O across the five knowns;
#: 2.10 covers the weakly-bound minimum the Fe *OOH repair proved is real.
PULL_TO = (1.70, 2.10)


def read_state(dirname: str, state: str):
    """Builder geometry + its if_pos constraints, straight from the QE input."""
    from ase.io import read
    return read(os.path.join("runs", dirname, state + ".in"), format="espresso-in")


def free_indices(atoms) -> list[int]:
    fixed = set(atoms.constraints[0].index.tolist()) if atoms.constraints else set()
    return [i for i in range(min(len(atoms), N_SLAB)) if i not in fixed]


def apply_mask(atoms, free: list[int]):
    """Return a copy with only `free` slab atoms mobile (adsorbate always mobile)."""
    from ase.constraints import FixAtoms
    a = atoms.copy()
    a.set_constraint(FixAtoms(indices=[i for i in range(N_SLAB) if i not in set(free)]))
    return a


def cus_index(atoms, metal: str) -> int:
    """Metal atom the adsorbate actually sits on, found rather than assumed."""
    ads = atoms[N_SLAB].position
    cand = [(math.dist(ads, a.position), i) for i, a in enumerate(atoms[:N_SLAB])
            if a.symbol == metal]
    return min(cand)[1]


def starts(atoms, metal: str):
    """Builder geometry plus rigidly pulled-in copies. Labelled for the log."""
    out = [("builder", atoms.copy())]
    if len(atoms) <= N_SLAB:
        return out
    c = cus_index(atoms, metal)
    cpos = atoms[c].position
    v = atoms[N_SLAB].position - cpos
    d0 = float((v @ v) ** 0.5)
    for target in PULL_TO:
        a = atoms.copy()
        shift = v * (target / d0 - 1.0)         # rigid translation of the whole adsorbate
        for k in range(N_SLAB, len(atoms)):
            a[k].position = a[k].position + shift
        out.append((f"pull{target:.2f}", a))
    return out


def relax(calc, atoms, fmax=0.05, steps=300):
    from ase.optimize import BFGS
    a = atoms.copy()
    a.calc = calc
    opt = BFGS(a, logfile=None)
    opt.run(fmax=fmax, steps=steps)
    return a, opt.get_number_of_steps()


def best_state(calc, atoms, metal: str, fmax=0.05, verbose=True):
    """Relax every start, keep the lowest-energy result. Returns (Atoms, info)."""
    best, log = None, []
    for tag, s in starts(atoms, metal):
        a, n = relax(calc, s, fmax=fmax)
        e = a.get_potential_energy()
        d = (min(math.dist(a[N_SLAB].position, p.position)
                 for p in a[:N_SLAB] if p.symbol == metal) if len(a) > N_SLAB else None)
        log.append(dict(start=tag, steps=n, energy=e, m_o=None if d is None else round(d, 3)))
        if best is None or e < best[0].get_potential_energy():
            best = (a, tag)
        if verbose:
            print(f"      {tag:<9} {n:>4} steps  E {e:>12.4f}"
                  + (f"  M-O {d:.3f}" if d is not None else ""), flush=True)
    return best[0], dict(chosen=best[1], starts=log)


def gas_energies(calc, frames: dict) -> dict:
    """Common H2/H2O reference, MACE-relaxed. Identical across metals by construction."""
    out = {}
    for s in ("H2", "H2O"):
        a, n = relax(calc, frames[f"Cr_slab/{s}"])
        out[s] = a.get_potential_energy()
        print(f"  gas {s:<4} {n:>4} steps  E {out[s]:>12.4f}", flush=True)
    return out


def predict_metal(calc, metal: str, frames: dict, gas: dict, free=None, fmax=0.05) -> dict:
    """Full CHE chain for one metal from its builder inputs."""
    d = DIRNAME[metal]
    E, qc = dict(gas), {}
    for s in ["slab"] + ADS_STATES:
        at = read_state(d, s)
        mask = free if free is not None else free_indices(at)
        at = apply_mask(at, mask)
        print(f"    {metal}/{s}", flush=True)
        a, info = best_state(calc, at, metal, fmax=fmax)
        E[s] = a.get_potential_energy()
        qc[s] = info
    r = che_from_energies(E)
    r["qc"] = qc
    r["free_atoms"] = len(free if free is not None else free_indices(read_state(d, "slab")))
    return r


def load_calc(model: str):
    from mace.calculators import mace_mp
    print(f"loading MACE '{model}' (cpu) ...", flush=True)
    return mace_mp(model=model, device="cpu", default_dtype="float64")


def _table(rows, ref=None):
    print(f"\n{'':5}{'dG_OH':>9}{'dG_O':>9}{'dG_OOH':>9}{'descr':>9}{'pls':>5}{'eta':>9}"
          + ("{:>11}".format("DFT eta") if ref else ""))
    for m, r in rows:
        line = (f"{m:<5}{r['dG_OH']:>9.3f}{r['dG_O']:>9.3f}{r['dG_OOH']:>9.3f}"
                f"{r['dG_O'] - r['dG_OH']:>9.3f}{r['pls']:>5}{r['eta']:>9.3f}")
        if ref and m in ref:
            line += f"{ref[m]['eta']:>11.3f}"
        print(line)


def cmd_validate(args):
    """Run the prediction protocol on metals whose answer we already know."""
    calc = load_calc(args.model)
    frames = final_frames(args.frames)
    ref = dft_reference(args.root)
    gas = gas_energies(calc, frames)
    pred = {m: predict_metal(calc, m, frames, gas, fmax=args.fmax) for m in KNOWN}
    _table([(m, pred[m]) for m in KNOWN], ref)
    pe = [pred[m]["eta"] for m in KNOWN]
    re_ = [ref[m]["eta"] for m in KNOWN]
    rho = spearman(pe, re_)
    mae = sum(abs(a - b) for a, b in zip(pe, re_)) / len(pe)
    print(f"\n  from BUILDER geometries, multi-start, no DFT input whatsoever:")
    print(f"  Spearman rho(eta) = {rho:+.3f}  exact two-sided p = "
          f"{exact_two_sided_p(rho, len(KNOWN)):.4f}   eta MAE = {mae:.3f} V")
    print("\n  This is the error bar on every number `predict` reports.")
    if args.out:
        json.dump(dict(pred=pred, ref=ref, rho_eta=rho, mae_eta=mae,
                       protocol="builder-start, multi-start, MACE-relaxed"),
                  open(args.out, "w"), indent=2)
        print(f"-> {args.out}")
    return 0


def cmd_predict(args):
    calc = load_calc(args.model)
    frames = final_frames(args.frames)
    gas = gas_energies(calc, frames)
    metals = args.limit.split(",") if args.limit else UNKNOWN
    pred = {m: predict_metal(calc, m, frames, gas, fmax=args.fmax) for m in metals}
    _table([(m, pred[m]) for m in metals])
    print("\n  as-shipped constraint masks (free slab atoms):")
    for m in metals:
        print(f"    {m}: {pred[m]['free_atoms']}"
              + ("" if pred[m]["free_atoms"] == len(CANONICAL_FREE) else "   <-- NOT canonical (11)"))
    ref = dft_reference(args.root)
    cluster = sorted(ref[m]["eta"] for m in ("Ir", "Ru", "Mn"))
    print(f"\n  the unresolved DFT cluster spans {cluster[0]:.3f}-{cluster[-1]:.3f} V; a sixth")
    print("  point inside it adds a coin-flip pair and no resolving power.")
    for m in metals:
        e = pred[m]["eta"]
        where = "INSIDE the cluster" if cluster[0] - 0.1 <= e <= cluster[-1] + 0.1 else "outside"
        print(f"    {m}: predicted {e:.3f} V -- {where}")
    if args.out:
        json.dump(pred, open(args.out, "w"), indent=2)
        print(f"-> {args.out}")
    return 0


def cmd_maskbias(args):
    """Price the constraint float-tie: same metal, as-shipped mask vs canonical."""
    calc = load_calc(args.model)
    frames = final_frames(args.frames)
    gas = gas_energies(calc, frames)
    metals = args.limit.split(",") if args.limit else ["Ni", "Co"]
    print("\nSame metal, same geometries, only the free-atom mask differs.")
    rows = []
    for m in metals:
        shipped = free_indices(read_state(DIRNAME[m], "slab"))
        print(f"\n  {m}: as-shipped {len(shipped)} free {shipped}")
        a = predict_metal(calc, m, frames, gas, free=shipped, fmax=args.fmax)
        print(f"\n  {m}: canonical  {len(CANONICAL_FREE)} free {CANONICAL_FREE}")
        b = predict_metal(calc, m, frames, gas, free=CANONICAL_FREE, fmax=args.fmax)
        rows.append((m, a, b))
    print(f"\n{'':5}{'eta(shipped)':>14}{'eta(canonical)':>16}{'delta':>9}")
    for m, a, b in rows:
        print(f"{m:<5}{a['eta']:>14.3f}{b['eta']:>16.3f}{b['eta'] - a['eta']:>+9.3f}")
    worst = max(abs(b["eta"] - a["eta"]) for _, a, b in rows)
    print(f"\n  largest shift {worst:.3f} V, against a tier resolution of ~0.17 V.")
    print("  If this exceeds ~0.05 V, Ni/Co cannot reuse their existing TRUSTWORTHY")
    print("  states and n=6 costs 4 jobs per metal rather than 2.")
    if args.out:
        json.dump({m: dict(shipped=a, canonical=b) for m, a, b in rows},
                  open(args.out, "w"), indent=2)
        print(f"-> {args.out}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn, helptext in (
            ("validate", cmd_validate, "run the protocol on the five known metals"),
            ("predict", cmd_predict, "predict eta for Ni/Co/Cu"),
            ("maskbias", cmd_maskbias, "price the constraint float-tie")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--frames", default="data/qe_frames.extxyz")
        p.add_argument("--root", default="runs")
        p.add_argument("--model", default="medium-mpa-0")
        p.add_argument("--fmax", type=float, default=0.05)
        p.add_argument("--limit", default="")
        p.add_argument("--out", default="")
        p.set_defaults(func=fn)
    a = ap.parse_args()
    raise SystemExit(a.func(a))


if __name__ == "__main__":
    main()
