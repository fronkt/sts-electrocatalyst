"""R2, second half: the multi-element Pourbaix gate for HEA candidates.

docs/31 built single-element diagrams and closed with the honest admission that the
part an actual HEA needs was not done:

    "No multi-element diagram. Only single-element Pourbaix diagrams were built. The
     Fe-Ni-Co-Mn quaternary that an actual HEA needs (MultiEntry combinatorics, the
     expensive part) is **not** done."                          -- docs/31 s7

and with the requirement that follows from it:

    "Any future screening objective must be activity x dG_pbx."  -- docs/31 s8.3

This module is that half. It needs no new network access: `pourbaix_r2.fetch_mp`
already cached the per-element Pourbaix entry sets for all eight metals, and a
multi-element diagram is built by pooling them at the candidate's own cation ratios.

What it measures, and why this metric
-------------------------------------
The tempting thing to compute is dG_pbx of "the HEA oxide" against the hull. That
would require an entry for a phase nobody has made and MP does not hold -- exactly
the mistake docs/31 s5 refused to make for rutile CoO2/NiO2/CuO2, where it declined
to emit a number about a nonexistent phase.

So the question is turned around into one the data can actually answer:

    **At OER operating conditions, what fraction of this composition's cations is
    thermodynamically soluble?**

Build the Pourbaix hull at the candidate's cation ratios, read off the stable phase
assemblage at (pH, V), and add up the cation moles sitting in aqueous ions rather
than solids. That is a real, quantitative, MP-backed number -- and it is the one that
decides whether a melt slot is worth spending, because a composition that dissolves
half of itself under load is not an electrode however good its descriptor looks.

Standing caveats, inherited from docs/31 s7 and not repaired here
-----------------------------------------------------------------
* **Bulk, not surface.** These are bulk equilibria. The real cus row is O-covered and
  has its own surface Pourbaix diagram (Hansen 2008). A bulk-unstable oxide can
  persist behind a passivating or self-healing surface.
* **Thermodynamics, not rates.** dG_pbx > 0 says "will decompose if it can", never
  "will decompose fast". IrO2 and RuO2 both dissolve measurably during OER.
* **Concentration convention.** Everything at 1e-6 M, the MP convention. Windows
  widen ~59 mV/decade per edge with dissolved-ion concentration.
* **0 K, PBE+U solids + experimental aqueous ions**, Persson 2012 scheme.

    PYTHONPATH=src python src/dft/pourbaix_multi.py melt-set
    PYTHONPATH=src python src/dft/pourbaix_multi.py gate --screen results/r4_screen.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dft.pourbaix_r2 import DEFAULT_CONC_M, fetch_mp, rhe_to_she  # noqa: E402

#: OER operating points, V vs RHE. 1.23 is the equilibrium potential; 1.53 is a
#: realistic operating potential (eta = 0.30 V). Both are pH-independent on RHE.
U_EQ_RHE = 1.23
U_OP_RHE = 1.53
#: 1 M KOH is the electrolyte in the docs/15 s4 protocol -> alkaline is the operating
#: condition of record for this campaign. pH 0 is carried for contrast only.
PH_OPERATING = 14.0
PH_CONTRAST = 0.0

CACHE = "results/r2_mp_cache.json"


def _entries(cache: dict, elements) -> list:
    from pymatgen.analysis.pourbaix_diagram import PourbaixEntry
    missing = [el for el in elements if el not in cache.get("pourbaix", {})]
    if missing:
        raise KeyError(f"no cached Pourbaix entries for {missing}; run pourbaix_r2.py run")
    out = []
    for el in elements:
        out += [PourbaixEntry.from_dict(d) for d in cache["pourbaix"][el]]
    return out


def hea_diagram(cache: dict, elements, fractions, conc_M: float = DEFAULT_CONC_M):
    """Pourbaix hull at a candidate's own cation ratios. This is the expensive call."""
    from pymatgen.analysis.pourbaix_diagram import PourbaixDiagram
    comp = {el: float(f) for el, f in zip(elements, fractions) if f > 0}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return PourbaixDiagram(_entries(cache, list(comp)), comp_dict=comp,
                               conc_dict={el: conc_M for el in comp},
                               filter_solids=True)


def _parts(entry):
    """(sub-entry, weight) pairs — a MultiEntry decomposes, a plain entry does not."""
    subs = getattr(entry, "entry_list", None)
    if not subs:
        return [(entry, 1.0)]
    weights = getattr(entry, "weights", None) or [1.0] * len(subs)
    return list(zip(subs, weights))


def soluble_fraction(entry, elements) -> dict:
    """Cation-mole fraction of `entry` sitting in aqueous ions rather than solids.

    Weighted by how much of each cation the assemblage actually holds, so a phase
    that dissolves a minor constituent is not scored like one that dissolves the
    matrix.
    """
    metals = set(elements)
    tot, soluble = 0.0, 0.0
    per_phase = []
    for sub, w in _parts(entry):
        comp = sub.composition
        n = sum(float(comp[el]) for el in comp if el.symbol in metals) * float(w)
        if n <= 0:
            continue
        is_ion = str(getattr(sub, "phase_type", "")).lower().startswith("ion")
        tot += n
        soluble += n if is_ion else 0.0
        per_phase.append(dict(formula=sub.composition.reduced_formula,
                              phase="ion" if is_ion else "solid",
                              cation_moles=round(n, 4)))
    return dict(soluble_cation_fraction=(soluble / tot if tot else float("nan")),
                phases=sorted(per_phase, key=lambda p: -p["cation_moles"]))


def assess(cache: dict, elements, fractions, pH: float = PH_OPERATING,
           v_rhe: float = U_OP_RHE, conc_M: float = DEFAULT_CONC_M,
           pbx=None) -> dict:
    """Stable assemblage + soluble cation fraction at one (pH, V vs RHE) point."""
    pbx = pbx if pbx is not None else hea_diagram(cache, elements, fractions, conc_M)
    v_she = float(rhe_to_she(v_rhe, pH))
    stable = pbx.get_stable_entry(pH, v_she)
    out = soluble_fraction(stable, elements)
    out.update(pH=pH, V_RHE=v_rhe, V_SHE=round(v_she, 4),
               stable_entry=getattr(stable, "name", str(stable)))
    return out


def assess_composition(cache: dict, elements, fractions, points=None,
                       conc_M: float = DEFAULT_CONC_M) -> dict:
    """Full stability record for one composition — one hull, several operating points."""
    points = points or [(PH_OPERATING, U_EQ_RHE), (PH_OPERATING, U_OP_RHE),
                        (PH_CONTRAST, U_OP_RHE)]
    pbx = hea_diagram(cache, elements, fractions, conc_M)  # built once, reused
    rows = [assess(cache, elements, fractions, pH, v, conc_M, pbx=pbx) for pH, v in points]
    operating = next(r for r in rows if r["pH"] == PH_OPERATING and r["V_RHE"] == U_OP_RHE)
    return dict(
        elements=list(elements), fractions=[float(f) for f in fractions],
        conc_M=conc_M, points=rows,
        soluble_at_operating=operating["soluble_cation_fraction"],
        stable_at_operating=operating["stable_entry"],
    )


def _fmt(rec: dict) -> str:
    lines = []
    for r in rec["points"]:
        solids = [p["formula"] for p in r["phases"] if p["phase"] == "solid"]
        ions = [p["formula"] for p in r["phases"] if p["phase"] == "ion"]
        lines.append(
            f"    pH {r['pH']:>4.0f}  {r['V_RHE']:.2f} V RHE   "
            f"soluble {r['soluble_cation_fraction']*100:5.1f}%   "
            f"solids: {','.join(solids) or '-':<28} ions: {','.join(ions) or '-'}")
    return "\n".join(lines)


#: The docs/15 s1 melt set, whose ACTIVITY ranking R0 voided. Stability is a separate
#: axis and was never computed for any of them, so it is worth knowing regardless of
#: what replaces the ranking.
MELT_SET_V1 = [
    ("Fe32Ni17Co34Mn18", ["Fe", "Ni", "Co", "Mn"], [0.32, 0.17, 0.34, 0.17]),
    ("Cr6Fe33Ni27Mn34", ["Cr", "Fe", "Ni", "Mn"], [0.06, 0.33, 0.27, 0.34]),
    ("Mn19Fe12Ni35Co16Cr18", ["Mn", "Fe", "Ni", "Co", "Cr"], [0.19, 0.12, 0.35, 0.16, 0.18]),
    ("Co20Ni20Cr20Mn20Cu20", ["Co", "Ni", "Cr", "Mn", "Cu"], [0.2, 0.2, 0.2, 0.2, 0.2]),
    ("Cr19Co28Fe25Ni28", ["Cr", "Co", "Fe", "Ni"], [0.19, 0.28, 0.25, 0.28]),
    ("FeCoNi", ["Fe", "Co", "Ni"], [1 / 3, 1 / 3, 1 / 3]),
]


def cmd_melt_set(args) -> int:
    cache = fetch_mp(args.cache)
    out = {}
    for name, els, fr in MELT_SET_V1:
        print(f"\n{name}  ({'-'.join(els)})", flush=True)
        try:
            rec = assess_composition(cache, els, fr, conc_M=args.conc)
            print(_fmt(rec), flush=True)
            out[name] = rec
        except Exception as e:  # a hull that will not build is a result, not a crash
            print(f"    FAILED: {type(e).__name__}: {e}", flush=True)
            out[name] = dict(error=f"{type(e).__name__}: {e}",
                             elements=els, fractions=fr)
        if args.out:
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
            json.dump(out, open(args.out, "w"), indent=2)

    ok = {k: v for k, v in out.items() if "soluble_at_operating" in v}
    if ok:
        print(f"\n{'':<26}{'soluble @ pH14/1.53V':>22}")
        for k, v in sorted(ok.items(), key=lambda kv: kv[1]["soluble_at_operating"]):
            print(f"{k:<26}{v['soluble_at_operating']*100:>21.1f}%")
        print("\n  Lower is better. This is a BULK thermodynamic statement at 1e-6 M;")
        print("  it says what will decompose if it can, not how fast, and it cannot")
        print("  see a passivating surface. docs/31 s7.")
    if args.out:
        print(f"\n-> {args.out}")
    return 0


def cmd_gate(args) -> int:
    """Attach stability to a screen's activity ranking — the activity x dG_pbx join."""
    if not os.path.exists(args.screen):
        print(f"no screen at {args.screen}; run screen_mace.py screen first")
        return 2
    screen = json.load(open(args.screen))
    rows = [r for r in screen.get("rows", []) if not r.get("desorbed")]
    if not rows:
        print("screen has no chemically clean rows to gate")
        return 1
    cache = fetch_mp(args.cache)
    out = []
    for i, r in enumerate(rows[: args.limit or len(rows)], 1):
        print(f"[{i}] {r['formula']}", flush=True)
        try:
            rec = assess_composition(cache, r["elements"], r["fractions"], conc_M=args.conc)
            print(_fmt(rec), flush=True)
            out.append(dict(r, stability=rec,
                            soluble_at_operating=rec["soluble_at_operating"]))
        except Exception as e:
            print(f"    FAILED: {type(e).__name__}: {e}", flush=True)
            out.append(dict(r, stability={"error": f"{type(e).__name__}: {e}"}))
        if args.out:
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
            json.dump(dict(source=args.screen, rows=out), open(args.out, "w"), indent=2)

    scored = [r for r in out if r.get("soluble_at_operating") is not None]
    print(f"\n{'':<26}{'eta_best':>10}{'soluble':>10}")
    for r in sorted(scored, key=lambda x: x["eta"]):
        print(f"{r['formula']:<26}{r['eta']:>10.3f}{r['soluble_at_operating']*100:>9.1f}%")
    print("\n  Activity ORDERS; stability GATES. A low-eta candidate that dissolves is")
    print("  not a melt candidate -- that tension is the HEA thesis's whole subject.")
    if args.out:
        print(f"\n-> {args.out}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn, helptext in (
            ("melt-set", cmd_melt_set, "assess the docs/15 melt set"),
            ("gate", cmd_gate, "join stability onto a MACE screen")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--cache", default=CACHE)
        p.add_argument("--conc", type=float, default=DEFAULT_CONC_M)
        p.add_argument("--out", default="")
        if name == "gate":
            p.add_argument("--screen", default="results/r4_screen.json")
            p.add_argument("--limit", type=int, default=0)
        p.set_defaults(func=fn)
    a = ap.parse_args()
    raise SystemExit(a.func(a))


if __name__ == "__main__":
    main()
