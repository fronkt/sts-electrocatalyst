"""R4-prep: re-screen the HEA space with the MACE screener, and validate the SCREEN.

Why this exists
---------------
The melt set frozen in docs/15 s1 was ranked by **UMA rutile**, and R0 voided that
ranking: no out-of-box UMA head ranks rutile MO2(110) OER (best oc25 rho = +0.400,
p = 0.52; docs/29 s8). Those compositions remain perfectly good meltable objects, but
"the ML-predicted best" is no longer a claim anyone can defend about them, and a
frozen prediction table built on a void ranking would contaminate the campaign's
central contribution -- the predicted-vs-measured correlation.

docs/35 established a replacement: MACE-MPA-0, un-fine-tuned and free, ranks the
QC-gated DFT tier at rho = +0.857, exact p = 0.0238, eta MAE 0.172 V at n = 7. This
module turns that result into a screen.

Two commands, and the order matters
-----------------------------------
``validate`` runs the **seven endmembers through the screening path's own slabs** --
pymatgen-cleaved 2x2 rutile(110), Vegard lattice constants, MACE relaxation, the same
multi-start adsorbate protocol the HEAs will get -- and scores rho against the DFT
tier of record. This is deliberately a different question from docs/35, which scored
MACE on the DFT tier's *own* 18-atom cells. That measured the model. This measures the
**pipeline**: slab construction, cus-site finding, adsorbate placement, relaxation and
CHE referencing, end to end, exactly as the HEA screen will run them. A model that
ranks well on someone else's geometries can still be wrecked by a builder defect --
which is not hypothetical here, see below.

``screen`` then ranks HEA compositions. It refuses to run unless a validation record
exists, because an unvalidated screen produces a melt list that means nothing.

The defect this protocol exists to avoid
----------------------------------------
`surfaces._adsorbate` sets the initial adsorbate height above the slab's *topmost*
atoms. On rutile(110) those are the bridging-O rows, which stand above the cus metal
row, so the adsorbate lands 3.08-3.13 A off the metal it is supposed to bind -- past
the 3.00 A desorption cut, i.e. **already desorbed at the start**. From that placement
the 2026-07 DFT campaign trapped Cr's `*O` 1.396 eV above its true minimum and left
`*OOH` desorbed on Mn, Fe and Ni: four chemically-wrong structures that passed every
numerical QC check, cost $2.64 to repair, and were each caught by MACE first.

The HEA path inherited that placement verbatim. Screening thousands of compositions
through it would have reproduced the defect on every one of them, with no DFT tier
to catch it. `surfaces_rutile.adsorbate_starts` is the remedy: every state is relaxed
from the builder placement *and* from rigid pull-ins at M-O = 1.70 / 2.10 A, lowest
energy wins, and the winning bond length is recorded so a desorbed "minimum" cannot
enter a melt list silently.

Site sampling
-------------
For a **pure** endmember the 2x2 supercell's four cus sites are related by lattice
translation and are therefore energetically identical, so `validate` samples one site
and loses nothing -- a 4x saving. ``check-equivalence`` verifies that claim rather
than asserting it. HEA compositions get the full multi-site treatment, because there
the sites differ chemically and the spread across them *is* the hypothesis.

    PYTHONPATH=src python src/scripts/screen_mace.py validate --out results/r4_validate.json
    PYTHONPATH=src python src/scripts/screen_mace.py check-equivalence --metal Cr
    PYTHONPATH=src python src/scripts/screen_mace.py screen --n-candidates 24 \
        --validation results/r4_validate.json --out results/r4_screen.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np  # noqa: E402

from hea_oer.adsorption import get_backend  # noqa: E402
from hea_oer.composition import Composition, sample_compositions  # noqa: E402
from hea_oer.data import DEFAULT_ELEMENTS, M_O_DESORBED_MIN  # noqa: E402
from hea_oer.descriptors import oer_overpotential  # noqa: E402
from hea_oer.phase_stability import phase_stability  # noqa: E402

#: the seven metals with a DFT eta of record (docs/35 s1)
ENDMEMBERS = ["Cr", "Mn", "Fe", "Co", "Ni", "Ru", "Ir"]

#: rho the screen must reach to be worth ranking HEAs with. At n = 7 the exact
#: two-sided permutation test gives p < 0.05 for rho >= 0.821 (docs/33 s6).
GATE_RHO = 0.821
GATE_N = 7


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def dft_tier(root: str = "runs") -> dict:
    from dft.eta_bounded import reference_tier
    return reference_tier(root)


def spearman(a, b) -> float:
    from dft.mlip_eval import spearman as _s
    return _s(list(a), list(b))


def exact_p(rho: float, n: int) -> float:
    from dft.mlip_eval import exact_two_sided_p
    return exact_two_sided_p(rho, n)


def evaluate(backend, comp: Composition) -> dict:
    """One composition through the screen. Returns a record, never raises for chemistry."""
    t0 = time.time()
    dG_OH, dG_O, dG_OOH = backend.predict(comp)
    oer = oer_overpotential(dG_OH, dG_O, dG_OOH)
    rec = backend.site_records.get(comp.formula(), {})
    return dict(
        formula=comp.formula(),
        dG_OH=dG_OH, dG_O=dG_O, dG_OOH=dG_OOH,
        descriptor=dG_O - dG_OH,
        eta=oer.overpotential, pls=oer.potential_limiting_step,
        seconds=round(time.time() - t0, 1),
        **{k: v for k, v in rec.items() if k != "all_bonds"},
    )


def _checkpoint(path: str, payload: dict) -> None:
    if not path:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2, default=str)


# --------------------------------------------------------------------------- validate

def cmd_validate(args) -> int:
    ref = dft_tier(args.root)
    metals = args.limit.split(",") if args.limit else ENDMEMBERS
    metals = [m for m in metals if m in ref]
    _log(f"DFT tier of record: n = {len(ref)}; validating on {metals}")
    _log("this scores the PIPELINE (own slabs, own placement), not the model")

    backend = get_backend("mace", model=args.model, surface="rutile",
                          n_sites=1, size=(2, 2, 4), fmax=args.fmax, seed=args.seed)
    rows, done = {}, []
    for m in metals:
        _log(f"  {m}: building rutile(110) 2x2, relaxing ...")
        rec = evaluate(backend, Composition((m,), (1.0,)))
        rows[m] = rec
        done.append(m)
        _log(f"  {m}: eta = {rec['eta']:.3f} V (DFT {ref[m]['eta']:.3f})  pls {rec['pls']}"
             f"  M-O {rec.get('bonds', {})}  {rec['seconds']}s")
        _checkpoint(args.out, dict(status="running", model=args.model,
                                   pred=rows, dft={k: v["eta"] for k, v in ref.items()}))

    ms = [m for m in done if m in ref]
    pe = [rows[m]["eta"] for m in ms]
    de = [ref[m]["eta"] for m in ms]
    rho, mae = spearman(pe, de), sum(abs(a - b) for a, b in zip(pe, de)) / len(ms)
    p = exact_p(rho, len(ms))
    met = bool(rho >= GATE_RHO and p < 0.05 and len(ms) >= GATE_N)

    print(f"\n{'':5}{'MACE':>9}{'DFT':>9}{'err':>8}   M-O(*O/*OH/*OOH)")
    for m in sorted(ms, key=lambda x: ref[x]["eta"]):
        b = rows[m].get("bonds", {})
        bond = "  ".join(f"{b.get(s, float('nan')):.2f}" for s in ("O", "OH", "OOH"))
        flag = "  <-- DESORBED" if rows[m].get("desorbed") else ""
        print(f"{m:<5}{rows[m]['eta']:>9.3f}{ref[m]['eta']:>9.3f}"
              f"{rows[m]['eta']-ref[m]['eta']:>+8.3f}   {bond}{flag}")
    print(f"\n  PIPELINE Spearman rho(eta) = {rho:+.4f}   exact two-sided p = {p:.4f}"
          f"   eta MAE = {mae:.3f} V")
    print(f"  gate: rho >= {GATE_RHO} at n >= {GATE_N} and p < 0.05  ->  "
          f"**{'MET' if met else 'NOT MET'}**")
    print("\n  For reference, docs/35 scored the same model on the DFT tier's own")
    print("  18-atom cells at rho = +0.857 / p = 0.0238 / MAE 0.172 V. A gap between")
    print("  that and the number above is the pipeline's contribution, not the model's.")

    _checkpoint(args.out, dict(status="complete", model=args.model, gate_met=met,
                               rho_eta=rho, p_exact=p, mae_eta=mae, n=len(ms),
                               pred=rows, dft={k: v["eta"] for k, v in ref.items()},
                               protocol="screen-own-slabs, multi-start, MACE-relaxed",
                               n_sites=1, supercell=[2, 2], fmax=args.fmax))
    if args.out:
        print(f"\n-> {args.out}")
    return 0


# ------------------------------------------------------------------ check-equivalence

def cmd_check_equivalence(args) -> int:
    """Verify the claim that lets `validate` sample one cus site instead of four."""
    _log(f"{args.metal}: 4 cus sites on a pure 2x2 slab should be translation-equivalent")
    backend = get_backend("mace", model=args.model, surface="rutile",
                          n_sites=4, size=(2, 2, 4), fmax=args.fmax, seed=args.seed)
    rec = evaluate(backend, Composition((args.metal,), (1.0,)))
    r = backend.site_records[rec["formula"]]
    print(f"\n  n_sites = {r['n_sites']}   eta min {r['eta_min']:.4f}  "
          f"mean {r['eta_mean']:.4f}  max {r['eta_max']:.4f}  std {r['eta_std']:.4f} V")
    ok = r["eta_std"] < args.tol
    print(f"  spread {'<' if ok else '>='} {args.tol} V  ->  "
          f"**{'EQUIVALENT — one site is sufficient' if ok else 'NOT EQUIVALENT'}**")
    if not ok:
        print("  `validate` samples one site; if these are not equivalent that is unsound.")
    _checkpoint(args.out, dict(metal=args.metal, equivalent=ok, tol=args.tol, **r))
    return 0 if ok else 1


# ----------------------------------------------------------------------------- screen

def cmd_screen(args) -> int:
    if args.validation and os.path.exists(args.validation):
        v = json.load(open(args.validation))
        if v.get("status") != "complete":
            _log(f"REFUSING: {args.validation} is {v.get('status')}, not complete")
            return 2
        if not v.get("gate_met") and not args.force:
            _log(f"REFUSING: pipeline gate NOT met (rho={v.get('rho_eta'):+.3f}, "
                 f"p={v.get('p_exact'):.4f}). An unvalidated screen produces a melt")
            _log("list that means nothing. Re-run validate, or pass --force to override.")
            return 2
        _log(f"pipeline validated: rho={v.get('rho_eta'):+.3f} p={v.get('p_exact'):.4f}")
    elif not args.force:
        _log(f"REFUSING: no validation record at {args.validation}. Run `validate` first.")
        return 2

    elements = args.elements or list(DEFAULT_ELEMENTS)
    _log(f"sampling {args.n_samples} compositions over {elements}")
    comps = sample_compositions(elements, n_samples=args.n_samples, seed=args.seed)

    # --- free analytic prefilter: only single-phase solid solutions can be melted ---
    keep = []
    for c in comps:
        m = phase_stability(c)
        if m.single_solid_solution:
            keep.append((c, m))
    _log(f"single-phase (Hume-Rothery/Omega-delta): {len(keep)} / {len(comps)}")
    if not keep:
        _log("nothing single-phase; widen the sampler")
        return 1

    # --- diverse pick, unbiased by any activity prior ---
    vecs = [c.vector(elements) for c, _ in keep]
    chosen = [0]
    while len(chosen) < min(args.n_candidates, len(keep)):
        best_i, best_d = None, -1.0
        for i in range(len(keep)):
            if i in chosen:
                continue
            d = min(float(np.linalg.norm(vecs[i] - vecs[j])) for j in chosen)
            if d > best_d:
                best_d, best_i = d, i
        chosen.append(best_i)
    pool = [keep[i] for i in chosen]
    _log(f"diverse pool: {len(pool)} candidates -> MACE (multi-site, multi-start)")

    seeds = tuple(int(s) for s in args.seeds.split(",")) if args.seeds else (args.seed,)
    _log(f"pooling cus sites over {len(seeds)} decoration(s) {seeds} x {args.n_sites} sites")
    backend = get_backend("mace", model=args.model, surface="rutile",
                          n_sites=args.n_sites, size=(2, 2, 4), fmax=args.fmax,
                          seed=args.seed, seeds=seeds)
    rows = []
    for i, (c, m) in enumerate(pool, 1):
        _log(f"  [{i}/{len(pool)}] {c.formula()}")
        rec = evaluate(backend, c)
        rec.update(single_phase=bool(m.single_solid_solution), phase=m.phase_tendency,
                   delta_pct=m.delta, omega=m.omega, vec=m.vec,
                   elements=list(c.elements), fractions=[float(f) for f in c.fractions])
        rows.append(rec)
        _log(f"      eta_best {rec['eta']:.3f} V  spread {rec.get('eta_std', 0):.3f}"
             f"  {rec['seconds']}s" + ("  DESORBED" if rec.get("desorbed") else ""))
        _checkpoint(args.out, dict(status="running", model=args.model,
                                   validation=args.validation, rows=rows))

    rows.sort(key=lambda r: r["eta"])
    clean = [r for r in rows if not r.get("desorbed")]
    print(f"\n{'':<26}{'eta_best':>10}{'spread':>9}{'descr':>9}{'pls':>5}   flags")
    for r in rows:
        print(f"{r['formula']:<26}{r['eta']:>10.3f}{r.get('eta_std', 0):>9.3f}"
              f"{r['descriptor']:>9.3f}{r['pls']:>5}   "
              + (",".join(r.get("desorbed", [])) or "-"))
    print(f"\n  {len(clean)}/{len(rows)} candidates chemically clean "
          f"(every winning state bound below {M_O_DESORBED_MIN} A)")
    print("  ORDERING only — docs/34's out-of-sample test missed eta(Co) by +0.339 V,")
    print("  2.3x the validated bar. Do not quote a candidate's absolute eta.")

    _checkpoint(args.out, dict(status="complete", model=args.model,
                               validation=args.validation, n_sampled=len(comps),
                               n_single_phase=len(keep), n_screened=len(rows),
                               n_sites=args.n_sites, rows=rows))
    if args.out:
        print(f"\n-> {args.out}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--model", default="medium-mpa-0")
        p.add_argument("--fmax", type=float, default=0.05)
        p.add_argument("--seed", type=int, default=0)
        p.add_argument("--root", default="runs")
        p.add_argument("--out", default="")

    v = sub.add_parser("validate", help="score the SCREEN against the DFT tier")
    common(v); v.add_argument("--limit", default="")
    v.set_defaults(func=cmd_validate)

    e = sub.add_parser("check-equivalence", help="verify one-site sampling is sound")
    common(e); e.add_argument("--metal", default="Cr"); e.add_argument("--tol", type=float, default=0.01)
    e.set_defaults(func=cmd_check_equivalence)

    s = sub.add_parser("screen", help="rank HEA compositions")
    common(s)
    s.add_argument("--elements", nargs="+", default=None)
    s.add_argument("--n-samples", type=int, default=4000)
    s.add_argument("--n-candidates", type=int, default=24)
    s.add_argument("--n-sites", type=int, default=4)
    s.add_argument("--seeds", default="0,1,2",
                   help="comma-separated decorations to pool cus sites over. One 2x2 "
                        "slab exposes 4 cus sites and which elements occupy them is an "
                        "accident of the shuffle, so a single decoration samples the "
                        "site distribution the HEA hypothesis is about far too thinly.")
    s.add_argument("--validation", default="results/r4_validate.json")
    s.add_argument("--force", action="store_true",
                   help="screen even without a passing validation record")
    s.set_defaults(func=cmd_screen)

    a = ap.parse_args()
    raise SystemExit(a.func(a))


if __name__ == "__main__":
    main()
