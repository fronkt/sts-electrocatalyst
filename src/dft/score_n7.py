"""Score the tier once Ni and/or Co land, against the predictions frozen in docs/34.

Two separate questions, and it is important not to blur them:

  1. **Did the pre-registered prediction hold?** MACE-MPA-0 said eta(Ni) = 1.200 V and
     eta(Co) = 0.883 V with a validated error bar of 0.150 V, recorded before the box was
     rented. This is a genuine out-of-sample test, and it is the stronger claim available
     to the campaign because it cannot be fitted after the fact.

  2. **Does the R3 gate clear at the new n?** Spearman rho between the screener's eta and
     the DFT tier's eta, with an EXACT permutation p (never asymptotic -- n <= 7 here).

The gate arithmetic, and why n mattered more than the model (docs/34 s1):

    n=5   rho must be 1.000        zero ranking errors tolerated
    n=6   rho >= 0.886             two
    n=7   rho >= 0.821             five

MACE's single standing error is Ru vs Ir, a pair our own DFT separates by 6 mV against a
~0.17 V tier resolution -- i.e. at n=5 the gate asked it to reproduce an ordering the
reference cannot resolve. Each new metal is predicted to bring its own unresolvable pair
(Ni sits 0.063 V from Fe, Co 0.009 V from Mn), which is exactly why n=7 is worth more
than n=6: three unresolvable pairs still clear at p = 0.0123.

    PYTHONPATH=src python src/dft/score_n7.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dft.mlip_eval import che_from_energies, exact_two_sided_p, spearman  # noqa: E402

DIRNAME = {"Cr": "Cr_slab", "Mn": "Mn_slab", "Fe": "Fe_slab", "Co": "Co_slab",
           "Ni": "Ni_slab", "Ru": "Ru_anchor", "Ir": "Ir_anchor"}
STATES = ["slab", "s0_O", "s0_OH", "s0_OOH", "H2O", "H2"]
ESTABLISHED = ["Cr", "Mn", "Fe", "Ru", "Ir"]
NEW = ["Ni", "Co"]

#: frozen in docs/34 s3 BEFORE the DFT was commissioned. Do not edit to match results.
PREREGISTERED = {"Ni": 1.200, "Co": 0.883}
PREREG_MAE = 0.150
#: the DFT cluster that a new point must fall outside of to add resolving power
CLUSTER = (0.781, 0.892)
#: docs/32 s2, the tier's own measured differential resolution
RESOLUTION = 0.17


def dft_eta(root: str, metals) -> dict:
    """QC-gated eta per metal. A metal with any rejected state is simply absent.

    Falls back to the bounded identity (`eta_bounded`) for a metal whose `*OOH` job
    failed but whose `*OH`/`*O` are QC-clean. Without that fallback this scorer
    reports "nothing to score" on the very campaign it was written for: both Ni and
    Co `*OOH` jobs died, which is precisely why the bound exists (docs/35 s3).
    """
    from dft.eta_bounded import BOUNDED, bounded_eta
    from dft.qe_qc import trusted_energy_ev

    out = {}
    for m in metals:
        d = os.path.join(root, DIRNAME[m])
        E = {s: trusted_energy_ev(os.path.join(d, s + ".out"),
                                  os.path.join(d, s + ".in")) for s in STATES}
        if not any(v is None for v in E.values()):
            out[m] = dict(che_from_energies(E), source="chain")
            continue
        for metal, dirname, partial in BOUNDED:
            if metal != m:
                continue
            w = bounded_eta(root, dirname, partial)
            if w is not None:
                out[m] = w
    return out


def unresolvable_pairs(eta: dict, tol: float = RESOLUTION) -> list[tuple]:
    ms = sorted(eta, key=lambda m: eta[m]["eta"])
    return [(ms[i], ms[i + 1]) for i in range(len(ms) - 1)
            if abs(eta[ms[i]]["eta"] - eta[ms[i + 1]]["eta"]) <= tol]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="runs")
    ap.add_argument("--pred", default="results/r3_predict_nicocu.json")
    ap.add_argument("--validation", default="results/r3_predict_validation.json")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    ref = dft_eta(a.root, ESTABLISHED + NEW)
    landed = [m for m in NEW if m in ref]
    print(f"DFT tier: n = {len(ref)}   established {sorted(set(ref) & set(ESTABLISHED))}"
          f"   new {landed or 'none yet'}")
    if not landed:
        print("\nNeither Ni nor Co has a complete QC-passing chain yet. Nothing to score.")
        return 0

    # ---- 1. the pre-registered test -------------------------------------------------
    print(f"\n{'='*72}\n1. PRE-REGISTERED PREDICTION (docs/34 s3, frozen before the run)\n{'='*72}")
    print(f"{'':4}{'predicted':>11}{'DFT':>10}{'error':>9}   within 1 MAE ({PREREG_MAE} V)?")
    for m in landed:
        p, d = PREREGISTERED[m], ref[m]["eta"]
        ok = abs(p - d) <= PREREG_MAE
        print(f"{m:<4}{p:>11.3f}{d:>10.3f}{p-d:>+9.3f}   {'YES' if ok else 'NO -- prediction missed'}")
        inside = CLUSTER[0] - 0.1 <= d <= CLUSTER[1] + 0.1
        print(f"      lands {'INSIDE' if inside else 'outside'} the unresolved "
              f"{CLUSTER[0]:.3f}-{CLUSTER[1]:.3f} V cluster"
              f"{'  (adds no resolving power)' if inside else ''}")
        print(f"      pls = {ref[m]['pls']} (predicted 2; eta touches dG_OOH only if pls = 3)")

    # ---- 2. the gate ----------------------------------------------------------------
    pred = json.load(open(a.pred)) if os.path.exists(a.pred) else {}
    val = json.load(open(a.validation)) if os.path.exists(a.validation) else {}
    mlip = {m: v["eta"] for m, v in val.get("pred", {}).items()}
    mlip.update({m: v["eta"] for m, v in pred.items() if m in ref})
    ms = [m for m in ref if m in mlip]
    if len(ms) < 3:
        print("\nnot enough paired points to score the gate")
        return 0

    rho = spearman([mlip[m] for m in ms], [ref[m]["eta"] for m in ms])
    p = exact_two_sided_p(rho, len(ms))
    n = len(ms)
    need = {5: 1.000, 6: 0.886, 7: 0.821}.get(n)
    print(f"\n{'='*72}\n2. R3 GATE at n = {n}\n{'='*72}")
    print(f"{'':4}{'MACE':>9}{'DFT':>9}{'err':>8}")
    for m in sorted(ms, key=lambda x: ref[x]["eta"]):
        print(f"{m:<4}{mlip[m]:>9.3f}{ref[m]['eta']:>9.3f}{mlip[m]-ref[m]['eta']:>+8.3f}")
    mae = sum(abs(mlip[m] - ref[m]["eta"]) for m in ms) / len(ms)
    print(f"\n  Spearman rho(eta) = {rho:+.4f}   exact two-sided p = {p:.4f}   eta MAE = {mae:.3f} V")
    if need:
        print(f"  gate at n={n} needs rho >= {need:.3f}  ->  **{'MET' if p < 0.05 else 'NOT MET'}**")

    up = unresolvable_pairs(ref)
    print(f"\n  pairs the DFT tier cannot resolve (< {RESOLUTION} V apart): "
          + (", ".join(f"{x}/{y}" for x, y in up) or "none"))
    print("  a ranking 'error' on one of those is the reference's limit, not the model's.")

    res = dict(n=n, rho_eta=rho, p_exact=p, mae_eta=mae, dft=ref, mlip=mlip,
               prereg={m: dict(predicted=PREREGISTERED[m], dft=ref[m]["eta"],
                               error=PREREGISTERED[m] - ref[m]["eta"],
                               within_1_mae=abs(PREREGISTERED[m] - ref[m]["eta"]) <= PREREG_MAE)
                       for m in landed},
               unresolvable_pairs=up)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=2)
        print(f"\n-> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
