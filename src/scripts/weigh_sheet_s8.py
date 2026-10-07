#!/usr/bin/env python
"""Weigh sheet for the S8 batch-1 melt set (docs/research/s8-melt-plan-2026-10-07.md).

Reuses weigh_sheet.mass_breakdown and its IUPAC molar masses unchanged; the round-1
MELT_SET in weigh_sheet.py is historical and is not used. Compositions are the exact
at.% of results/r4_gated.json. The basis and Mn over-charge are the freeze proposal's
[CONFIRM] values (10 g per button, +4% Mn).

    PYTHONPATH=src/scripts python src/scripts/weigh_sheet_s8.py > docs/research/s8-weigh-sheet-2026-10-07.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from weigh_sheet import MOLAR_MASS, mass_breakdown

ROOT = Path(__file__).resolve().parents[2]
GATED = ROOT / "results/r4_gated.json"
BATCH_1 = [
    ("Cu8Cr23Mn35Co34", "candidate (census leader)"),
    ("Ni31Cr29Cu5Mn35", "candidate (August screen leader)"),
    ("Fe25Co25Ni25Cr25", "candidate (August screen #2)"),
    ("Cu26Ni9Cr31Co33", "candidate (strict-policy leader)"),
    ("Cu22Fe30Co32Mn15", "anchor (predicted poor by both MLIP arms)"),
]


def compositions() -> dict:
    rows = {row["formula"]: row for row in json.loads(GATED.read_text(encoding="utf-8"))["rows"]}
    out = {}
    for name, _ in BATCH_1:
        elements = re.findall(r"[A-Z][a-z]?", name)
        fractions = rows[name]["fractions"]
        if len(elements) != len(fractions) or abs(sum(fractions) - 1) > 1e-9:
            raise SystemExit("composition record does not match " + name)
        out[name] = {el: 100 * f for el, f in zip(elements, fractions)}
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--basis", type=float, default=10.0, help="charge mass per button (g)")
    parser.add_argument("--mn-overcharge", type=float, default=4.0, help="extra Mn, %% (evaporation)")
    args = parser.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # pragma: no cover
        pass
    basis, extra = args.basis, args.mn_overcharge
    out = ["# S8 batch-1 weigh sheet, 2026-10-07", "",
           f"Status: proposed; basis **{basis:.1f} g** per button and **+{extra:.0f}% Mn** are [CONFIRM] values in the "
           "[stage-1 freeze proposal](s8-stage1-freeze-proposal-2026-10-07.md). Nothing is melted before the freeze is deposited. "
           "Compositions are the exact at.% of `results/r4_gated.json`; molar masses are IUPAC standard atomic weights "
           "(`src/scripts/weigh_sheet.py`). Reproduce with `PYTHONPATH=src/scripts python src/scripts/weigh_sheet_s8.py`.", "",
           "Mass fraction w_i = x_i M_i / Σ_j x_j M_j; nominal mass = basis × w_i; the Mn weigh target adds the over-charge. "
           "The at.% is the design target: verify the actual composition by SEM-EDS after melting.", ""]
    totals = {}
    for name, role in BATCH_1:
        at = compositions()[name]
        breakdown = mass_breakdown(at, basis)
        molar = sum(at[el] / 100 * MOLAR_MASS[el] for el in at)
        out += [f"## {name}", f"*{role}*  ·  mean molar mass {molar:.3f} g/mol  ·  charge {basis:.1f} g", "",
                "| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |",
                "|---|---|---|---|---|---|"]
        weigh_total = 0.0
        for el in at:
            _, mass = breakdown[el]
            target = mass * (1 + extra / 100) if el == "Mn" else mass
            totals[el] = totals.get(el, 0.0) + target
            weigh_total += target
            cell = f"**{target:.3f}** (+{extra:.0f}% Mn)" if el == "Mn" else f"**{target:.3f}**"
            out.append(f"| {el} | {at[el]:.3f} | {MOLAR_MASS[el]:.3f} | {100 * mass / basis:.3f} | {mass:.3f} | {cell} |")
        out += [f"| **Σ** | 100.000 | — | 100.000 | {basis:.3f} | **{weigh_total:.3f}** |", ""]
    out += ["## Feedstock for one batch-1 melt of all five", "",
            "| Element | Weigh total (g) |", "|---|---|"]
    out += [f"| {el} | {mass:.3f} |" for el, mass in sorted(totals.items())]
    out += [f"| **Σ** | **{sum(totals.values()):.3f}** |", "",
            "Allow extra for possible re-melts (one per alloy that misses ±2 at.%; most likely the two ~35 at.% Mn alloys).", "",
            "**Safety:** four of the five alloys contain 22.6–31.5 at.% Cr (Cu22Fe30Co32Mn15 has none). A dated, "
            "mentor-signed Cr(VI) risk assessment is required before the first melt (freeze proposal §7)."]
    print("\n".join(out))


if __name__ == "__main__":
    main()
