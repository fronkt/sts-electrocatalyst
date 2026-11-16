#!/usr/bin/env python
"""FWM weigh sheet for the ISEF round-2 melt request (2026-11-16).

Six round-2 melts (R0-R5, tasks/isef-2027-master-plan-2026-11-14.md section 2.2). The processing
study (section 3) uses leftover round-1 Fe25 and Ni34 rod, so it needs no new melt (Frank, 2026-11-16).

    PYTHONPATH=src/scripts python src/scripts/weigh_sheet_round2.py \
        > docs/research/isef-round2-weigh-sheet-2026-11-16.md

Basis: 200 g per charge, as in round 1 (200 g rods; Frank, 2026-11-16).
Mn over-charge: +25% Mn mass. Round 1 charged +4% and lost roughly 13-25% of the charged Mn
(SEM-EDS spot estimates, Cu8 and Cu22). Charging Mn x 1.25 lands within +/-2 at.% of a 30-31 at.%
Mn target for any loss between ~13% and ~27% of the charged Mn (checked below), so the as-made
composition check, not the over-charge, is what certifies the melt.
"""
from __future__ import annotations

from weigh_sheet import MOLAR_MASS, mass_breakdown

BASIS_G = 200.0
MN_OVERCHARGE_PCT = 25.0

# (code, name, role, {element: at.%})
MELTS = [
    ("R0", "Cu26Ni9Cr31Co33", "round-1 alloy C, fresh melt at the same aim (completes round 1)",
     {"Cu": 25.780, "Ni": 9.393, "Cr": 31.466, "Co": 33.362}),
    ("R1", "FeCoNi", "Fe25 without Cr (Cr 0 on the Fe:Co:Ni backbone)",
     {"Fe": 100 / 3, "Co": 100 / 3, "Ni": 100 / 3}),
    ("R2", "CoCr0.5FeNi", "Cr 14.3 at.%, midpoint between R1 and Fe25",
     {"Co": 200 / 7, "Cr": 100 / 7, "Fe": 200 / 7, "Ni": 200 / 7}),
    ("R3", "Ni34Fe29Mn30Co7", "sharpest test: old screen ranked it last, film rule puts it on top",
     {"Ni": 34, "Fe": 29, "Mn": 30, "Co": 7}),
    ("R4", "Ni86Cu14", "single-phase twin of Ni31's leached film",
     {"Ni": 86, "Cu": 14}),
    ("R5", "Mn31Ni31Co33Cu6", "mid-range anchor",
     {"Mn": 31, "Ni": 31, "Co": 33, "Cu": 6}),
]


def final_mn(x_target: float, k: float, loss: float) -> float:
    """At.% Mn after melting when Mn moles are charged x k and a fraction `loss` of charged Mn evaporates."""
    x = x_target / 100
    mn = x * k * (1 - loss)
    return 100 * mn / (mn + (1 - x))


def main() -> None:
    k = 1 + MN_OVERCHARGE_PCT / 100
    out = []
    w = out.append
    w("# ISEF round-2 weigh sheet, 2026-11-16")
    w("")
    w(f"Reproduce with `PYTHONPATH=src/scripts python src/scripts/weigh_sheet_round2.py`. Basis **{BASIS_G:.0f} g** per charge; "
      f"**+{MN_OVERCHARGE_PCT:.0f}% Mn** over-charge (round 1 used +4% and came out Mn-low). "
      "Mass fraction w_i = x_i M_i / sum_j x_j M_j; nominal mass = basis x w_i. "
      "The at.% is the aim; the as-made composition is measured after melting (chip ICP-OES or SEM-EDS area analyses).")
    w("")
    totals: dict[str, float] = {}
    for code, name, role, comp in MELTS:
        bd = mass_breakdown(comp, BASIS_G)
        mbar = sum(f * MOLAR_MASS[el] for el, (f, _) in bd.items())
        w(f"## {code}: {name}")
        w(f"*{role}*  -  mean molar mass {mbar:.3f} g/mol  -  charge {BASIS_G:.1f} g")
        w("")
        w("| Element | at.% | wt.% | Nominal mass (g) | **Weigh target (g)** |")
        w("|---|---|---|---|---|")
        s_nom = s_tgt = 0.0
        for el, (f, m) in bd.items():
            tgt = m * k if el == "Mn" else m
            s_nom += m
            s_tgt += tgt
            totals[el] = totals.get(el, 0.0) + tgt
            note = f" (+{MN_OVERCHARGE_PCT:.0f}% Mn)" if el == "Mn" else ""
            w(f"| {el} | {100 * f:.3f} | {100 * m / BASIS_G:.3f} | {m:.3f} | **{tgt:.3f}**{note} |")
        w(f"| **Sum** | 100.000 | 100.000 | {s_nom:.3f} | **{s_tgt:.3f}** |")
        if "Mn" in comp:
            xmn = 100 * bd["Mn"][0]
            rows = ", ".join(f"{int(L * 100)}% loss -> {final_mn(xmn, k, L):.1f}" for L in (0.10, 0.13, 0.20, 0.25, 0.27, 0.30))
            w("")
            w(f"Expected Mn after melting (aim {xmn:.1f} at.%): {rows} at.%.")
        w("")
    w(f"## Feedstock for all {len(MELTS)} charges")
    w("")
    w("| Element | Weigh total (g) |")
    w("|---|---|")
    for el in sorted(totals):
        w(f"| {el} | {totals[el]:.1f} |")
    w(f"| **Sum** | **{sum(totals.values()):.1f}** |")
    w("")
    w("Allow extra for one re-melt of any charge that misses +/-2 at.% (most likely R3 and R5 on Mn, R0 on Cu).")
    print("\n".join(out))


if __name__ == "__main__":
    main()
