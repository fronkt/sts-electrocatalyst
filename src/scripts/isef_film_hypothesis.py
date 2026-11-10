"""Leached-film hypothesis (ISEF round 2, step P2). POST HOC on the five measured alloys.

Idea: in 1 M KOH at OER potentials the electrode is not the alloy surface the screen
modeled but an oxide/oxyhydroxide film grown from it. Metals whose equilibrium
solubility is far above what one disk can saturate (isef_pourbaix_solubility.py) leave
the film; the rest stay. If activity is set by the film, the measured order should
follow the film's Ni + Fe fraction (NiFe oxyhydroxides are the most active
earth-abundant alkaline OER films; Co and Cu oxyhydroxides are less active).

Which metals leave, at 1.53 V vs RHE, pH 14:
  Cr -> CrO4^2-  (ion even at 1 M: robust)
  Mn -> MnO4^-   (ion even at 1 M: robust)
  Ni -> the cached MP data put Ni(OH)3^- above NiO up to ~5e-4 M, i.e. "leaches".
        Overridden: Ni31's pre-OER Ni redox wave grew over 25 activation cycles
        (report Section 4.6), which requires Ni to stay in the film. Treated as retained.
  Fe, Co, Cu -> retained (log c* <= -6.75).

This was formulated after the electrode data were seen, so it scores 0 as evidence.
Its use is to make prospective, registered predictions: Cu26 (to be remelted) and the
round-2 alloys.

    PYTHONPATH=src python src/scripts/isef_film_hypothesis.py
"""
from __future__ import annotations

import json
import os

from scipy.stats import spearmanr

LEACH = {"Cr", "Mn"}           # robust from the Pourbaix scan
NI_OVERRIDE = "retained"       # MP says leaches; the measured redox wave says retained

#: eta10 (V), one disk each, first sweep, 90% iR (report Section 4.6). Cu8 is a lower bound.
MEASURED = {"Fe25": 0.313, "Ni31": 0.316, "Cu22": 0.365, "Ni34": 0.369, "Cu8": None}
CU8_LOWER_BOUND = 0.393
#: Repeat-sweep spread (report): differences below this are ties.
TIE_V = 0.0047

ALLOYS = {
    # measured set (nominal at.%, bench key)
    "Fe25": {"Fe": 25, "Co": 25, "Ni": 25, "Cr": 25},
    "Ni31": {"Ni": 31.115, "Cr": 29.187, "Cu": 5.169, "Mn": 34.529},
    "Cu22": {"Cu": 22.116, "Fe": 29.974, "Co": 32.425, "Mn": 15.484},
    "Ni34": {"Ni": 33.877, "Fe": 5.962, "Cu": 29.423, "Co": 30.738},
    "Cu8": {"Cu": 7.887, "Cr": 22.634, "Mn": 34.993, "Co": 34.485},
    # not measured: remelt
    "Cu26": {"Cu": 25.780, "Ni": 9.393, "Cr": 31.466, "Co": 33.362},
    # round-2 candidates (tasks/isef-2027-round2-plan.md)
    "FeCoNi": {"Fe": 100 / 3, "Co": 100 / 3, "Ni": 100 / 3},
    "CoCr0.5FeNi": {"Co": 2 / 7 * 100, "Cr": 1 / 7 * 100, "Fe": 2 / 7 * 100, "Ni": 2 / 7 * 100},
    "Ni86Cu14": {"Ni": 86, "Cu": 14},
    "Ni34Fe29Mn30Co7": {"Ni": 34, "Fe": 29, "Mn": 30, "Co": 7},
    "Mn31Ni31Co33Cu6": {"Mn": 31, "Ni": 31, "Co": 33, "Cu": 6},
}


def film(comp: dict) -> dict:
    kept = {el: x for el, x in comp.items() if el not in LEACH}
    tot = sum(kept.values())
    return {el: round(x / tot, 3) for el, x in kept.items()}


def main() -> int:
    rows = {}
    for name, comp in ALLOYS.items():
        f = film(comp)
        nife = f.get("Ni", 0) + f.get("Fe", 0)
        fe_in_nife = f.get("Fe", 0) / nife if nife else 0.0
        leached = sum(x for el, x in comp.items() if el in LEACH) / sum(comp.values())
        rows[name] = dict(film=f, nife_fraction=round(nife, 3),
                          fe_share_of_nife=round(fe_in_nife, 3),
                          leached_cation_fraction=round(leached, 3))
        print(f"{name:>16}  film {f}  Ni+Fe {nife:.2f}  Fe/(Ni+Fe) {fe_in_nife:.2f}  "
              f"leached {leached * 100:4.1f}%")

    # Post-hoc rank check on the five measured alloys (Cu8 at its lower bound, i.e. last).
    names = list(MEASURED)
    eta = [MEASURED[n] if MEASURED[n] is not None else CU8_LOWER_BOUND + 0.05 for n in names]
    nife = [rows[n]["nife_fraction"] for n in names]
    rho, p = spearmanr([-x for x in nife], eta)
    print(f"\nPOST HOC, n = 5: Spearman rho(-film Ni+Fe, eta10) = {rho:.2f} (p = {p:.3f}); "
          f"measured ties (< {TIE_V * 1000:.1f} mV): Fe25~Ni31, Cu22~Ni34")
    out = "results/isef_round2_2026-11-10/film_hypothesis.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(dict(status="POST HOC on the measured five; prospective for the rest",
                   leach=sorted(LEACH), ni=NI_OVERRIDE, measured_eta10_V=MEASURED,
                   cu8_lower_bound_V=CU8_LOWER_BOUND, spearman_post_hoc=dict(rho=rho, p=p),
                   rows=rows), open(out, "w"), indent=1)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
