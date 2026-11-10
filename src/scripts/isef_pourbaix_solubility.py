"""Equilibrium solubility of each alloy metal at alkaline OER conditions (ISEF round 2, step P1).

The September gate (src/dft/pourbaix_multi.py) asks one yes/no question at a fixed
dissolved-ion concentration of 1e-6 M: is each cation in a solid or an ion?  That
answer flips for any metal whose equilibrium solubility happens to sit near 1e-6 M,
and at pH 14 Ni and Co do sit there, so the gate scored the most active measured alloy
(Fe25Co25Ni25Cr25) as 75% soluble.

This script asks the question the yes/no answer depends on instead: for each metal,
what dissolved-ion concentration c* must the electrolyte reach before a solid becomes
the stable phase at (pH, V)?  A metal with c* far above what one electrode can put into
the cell (Section "scale" below) keeps dissolving: it leaches from the surface. A metal
with c* far below it stays as a solid oxide or oxyhydroxide.

Scale: a 5 mm disk (0.196 cm2) carrying a film ~50 monolayers thick (~1e15 sites/cm2
per monolayer) holds ~1e16 atoms ~ 1.6e-8 mol. Dissolved into ~100 mL of electrolyte
that is ~2e-7 M. So c* >> 1e-6 M means the element cannot be retained in the film by
saturating the electrolyte; c* << 1e-8 M means it is retained.

Inputs: the cached Materials Project Pourbaix entries (results/r2_mp_cache.json,
Persson 2012 scheme, fetched 2026-07-31). No network access.

    PYTHONPATH=src python src/scripts/isef_pourbaix_solubility.py \
        --out results/isef_round2_2026-11-10/pourbaix_solubility.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dft.pourbaix_r2 import rhe_to_she  # noqa: E402

METALS = ["Fe", "Co", "Ni", "Cr", "Mn", "Cu"]
PH = 14.0
#: 1.23 V = equilibrium; 1.53 / 1.63 V = the measured eta10 range (0.30-0.40 V).
V_RHE = [1.23, 1.53, 1.63]
LOG_C = np.round(np.arange(-12.0, 0.01, 0.25), 2)

#: The six melted alloys, nominal at.% (bench key), and their measured outcome.
ALLOYS = {
    "Fe25": {"Fe": 25, "Co": 25, "Ni": 25, "Cr": 25},
    "Ni31": {"Ni": 31.115, "Cr": 29.187, "Cu": 5.169, "Mn": 34.529},
    "Cu22": {"Cu": 22.116, "Fe": 29.974, "Co": 32.425, "Mn": 15.484},
    "Ni34": {"Ni": 33.877, "Fe": 5.962, "Cu": 29.423, "Co": 30.738},
    "Cu8": {"Cu": 7.887, "Cr": 22.634, "Mn": 34.993, "Co": 34.485},
    "Cu26": {"Cu": 25.780, "Ni": 9.393, "Cr": 31.466, "Co": 33.362},
}


def entries(cache: dict, el: str):
    from pymatgen.analysis.pourbaix_diagram import PourbaixEntry
    return [PourbaixEntry.from_dict(d) for d in cache["pourbaix"][el]]


def is_ion(entry) -> bool:
    return str(getattr(entry, "phase_type", "")).lower().startswith("ion")


def scan(cache: dict, el: str) -> dict:
    """Stable entry at each (log c, V) for one metal; c* = lowest c with a solid stable."""
    from pymatgen.analysis.pourbaix_diagram import PourbaixDiagram
    ents = entries(cache, el)
    out = {}
    for v in V_RHE:
        v_she = float(rhe_to_she(v, PH))
        rows = []
        for lc in LOG_C:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pbx = PourbaixDiagram(ents, conc_dict={el: float(10 ** lc)})
            st = pbx.get_stable_entry(PH, v_she)
            rows.append(dict(log_c=float(lc), stable=st.name, ion=is_ion(st)))
        solid_at = [r["log_c"] for r in rows if not r["ion"]]
        log_cstar = min(solid_at) if solid_at else None  # None: ion even at 1 M
        if log_cstar is not None and log_cstar <= LOG_C[0]:
            log_cstar_txt = f"<= {LOG_C[0]}"
        elif log_cstar is None:
            log_cstar_txt = "> 0 (ion even at 1 M)"
        else:
            log_cstar_txt = f"{log_cstar:.2f}"
        solid_name = next((r["stable"] for r in rows if not r["ion"]), None)
        ion_name = next((r["stable"] for r in rows if r["ion"]), None)
        out[f"{v:.2f}"] = dict(log_cstar=log_cstar, log_cstar_txt=log_cstar_txt,
                               solid=solid_name, ion=ion_name, rows=rows)
    return out


def classify(log_cstar) -> str:
    if log_cstar is None or log_cstar >= -6.0:
        return "leaches"
    if log_cstar <= -8.0:
        return "retained"
    return "marginal"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="results/r2_mp_cache.json")
    ap.add_argument("--out", default="results/isef_round2_2026-11-10/pourbaix_solubility.json")
    a = ap.parse_args()
    cache = json.load(open(a.cache))
    per_metal = {}
    for el in METALS:
        per_metal[el] = scan(cache, el)
        cells = "  ".join(f"{v} V: log c* {per_metal[el][v]['log_cstar_txt']:>22} "
                          f"({per_metal[el][v]['solid']} | {per_metal[el][v]['ion']})"
                          for v in per_metal[el])
        print(f"{el:>2}  {cells}", flush=True)

    print("\nRetained cation fraction per alloy (at.%-weighted; marginal counted as retained):")
    per_alloy = {}
    for name, comp in ALLOYS.items():
        tot = sum(comp.values())
        rec = {}
        for v in ["1.23", "1.53", "1.63"]:
            cls = {el: classify(per_metal[el][v]["log_cstar"]) for el in comp}
            kept = sum(x for el, x in comp.items() if cls[el] != "leaches") / tot
            rec[v] = dict(classes=cls, retained_fraction=round(kept, 3),
                          retained_film={el: round(x / sum(comp[e] for e in comp if cls[e] != "leaches"), 3)
                                         for el, x in comp.items() if cls[el] != "leaches"}
                          if kept > 0 else {})
        per_alloy[name] = rec
        r = rec["1.53"]
        print(f"  {name:>5}  1.53 V: retained {r['retained_fraction']*100:5.1f}%  "
              f"film (renormalized) {r['retained_film']}  leaches: "
              f"{[el for el, c in r['classes'].items() if c == 'leaches']}")

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(dict(pH=PH, V_RHE=V_RHE, log_c_grid=[float(x) for x in LOG_C],
                   cache=a.cache, thresholds=dict(leaches=">= -6", retained="<= -8"),
                   per_metal=per_metal, per_alloy=per_alloy), open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
