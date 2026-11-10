"""CALPHAD phase check at the homogenization temperature (ISEF round 2, step P3b).

Question: does an open CALPHAD database reproduce the phase outcome of the six melted
alloys (homogenized 1,050 C / 24 h, water-quenched), and if so, what does it say about
the round-2 candidates?

Databases (downloads in D:/sts-electrocatalyst/calphad/, untrusted data, never executed):
  mc_fe  MatCalc mc_fe v2.062 (ODbL), patched for pycalphad; all 15 binaries of
         Co-Cr-Cu-Fe-Mn-Ni assessed, but validated only for steel-like dilute
         compositions (Cu < 1, Co < 3, Cr/Mn < 25, Ni < 26 wt%). Equiatomic HEAs are an
         extrapolation.
  mf     LibreCalphad mf-steel (MIT, commit a7dace2); better Co-Cr-Fe-Mn-Ni description,
         but no Co-Cu parameters -> results for alloys holding both Co and Cu are skipped.

Measured outcome (report Section 3.7, Table 2): Fe25 and Ni34 single FCC; Ni31 and Cu22
two phases (Ni31: FCC + Cr-rich BCC); Cu8 three (incl. sigma); Cu26 three (Cu-rich pools).

    D:/sts-electrocatalyst/.venv-isef/Scripts/python.exe -I \
        src/scripts/isef_calphad_check.py --db mc_fe --out results/isef_round2_2026-11-10/calphad_mc_fe.json
"""
from __future__ import annotations

import argparse
import json
import os
import time
import warnings

import numpy as np

ROOT = "D:/sts-electrocatalyst/calphad"
DBS = {
    "mc_fe": f"{ROOT}/patched-2026-11-10/mc_fe_v2062_CoCrCuFeMnNi_pycalphad.tdb",
    "mf": f"{ROOT}/downloads-2026-11-10/mf-steel_a7dace2.tdb",
}
#: Metallic solution phases + the intermetallics that can form from these six elements.
#: Ordered variants (BCC_B2, GAMMA_PRIME) are left out: the order-disorder link was not
#: carried into the patched mc_fe file. Only one sigma model per database.
WANT = {
    "mc_fe": ["LIQUID", "FCC_A1", "BCC_A2", "HCP_A3", "SIGMA", "ALPHA_MN", "BETA_MN",
              "CHI_A12", "LAVES_PHASE", "C15_LAVES", "MU_PHASE_I", "R_PHASE", "CR3MN5",
              "MNNI", "MNNI2"],
    # mf-steel names its solution phases by their partitioned (order-disorder) models.
    "mf": ["LIQUID", "FCC_L12", "BCC_4SL", "HCP_L12", "SIGMA_D8B", "CBCC_A12", "CUB_A13",
           "CHI_A12", "LAVES_C14", "LAVES_C15", "MU2_D85", "R_COCRMO", "CR3MN5", "MNNI2"],
}
#: alpha-Mn (A12) is a Mn phase. In mc_fe its Co-Cu-Ni parameters are not assessed, and the
#: first run made it 48% of Ni34 and Cu26, which hold no Mn. --alpha-mn-needs-mn drops the
#: A12 phase for Mn-free alloys.
ALPHA_MN_NAMES = {"ALPHA_MN", "CBCC_A12"}
T_HOMOG = 1050.0 + 273.15

MEASURED = {
    "Fe25": "1: FCC", "Ni34": "1: FCC", "Ni31": "2: FCC + Cr-rich BCC", "Cu22": "2",
    "Cu8": "3 (incl. sigma)", "Cu26": "3 (Cu-rich pools)",
}
ALLOYS = {
    "Fe25": {"FE": 25, "CO": 25, "NI": 25, "CR": 25},
    "Ni34": {"NI": 33.877, "FE": 5.962, "CU": 29.423, "CO": 30.738},
    "Ni31": {"NI": 31.115, "CR": 29.187, "CU": 5.169, "MN": 34.529},
    "Cu22": {"CU": 22.116, "FE": 29.974, "CO": 32.425, "MN": 15.484},
    "Cu8": {"CU": 7.887, "CR": 22.634, "MN": 34.993, "CO": 34.485},
    "Cu26": {"CU": 25.780, "NI": 9.393, "CR": 31.466, "CO": 33.362},
    "FeCoNi": {"FE": 1, "CO": 1, "NI": 1},
    "CoCr0.5FeNi": {"CO": 2, "CR": 1, "FE": 2, "NI": 2},
    "Ni86Cu14": {"NI": 86, "CU": 14},
    "Ni34Fe29Mn30Co7": {"NI": 34, "FE": 29, "MN": 30, "CO": 7},
    "Mn31Ni31Co33Cu6": {"MN": 31, "NI": 31, "CO": 33, "CU": 6},
}


def run(dbkey: str, names, T: float, alpha_mn_needs_mn: bool = False) -> dict:
    from pycalphad import Database, equilibrium, variables as v
    from pycalphad.core.utils import filter_phases
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        db = Database(DBS[dbkey])
    out = {}
    for name in names:
        comp = ALLOYS[name]
        if dbkey == "mf" and "CO" in comp and "CU" in comp:
            out[name] = dict(skipped="no Co-Cu parameters in mf-steel")
            print(f"{name:>16}  skipped (no Co-Cu in mf-steel)", flush=True)
            continue
        els = sorted(comp)
        tot = sum(comp.values())
        x = {el: comp[el] / tot for el in els}
        comps = els + ["VA"]
        phases = [p for p in WANT[dbkey] if p in filter_phases(db, comps)]
        if alpha_mn_needs_mn and "MN" not in comp:
            phases = [p for p in phases if p not in ALPHA_MN_NAMES]
        conds = {v.T: T, v.P: 101325, v.N: 1}
        for el in els[1:]:  # first element is the dependent one
            conds[v.X(el)] = x[el]
        t0 = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            eq = equilibrium(db, comps, phases, conds)
        ph = eq.Phase.values.squeeze()
        npf = eq.NP.values.squeeze()
        xs = eq.X.values.squeeze()  # (vertex, component)
        comp_names = list(eq.component.values)
        rows = []
        for i, p in enumerate(ph):
            if not p or np.isnan(npf[i]) or npf[i] < 1e-4:
                continue
            rows.append(dict(phase=str(p), fraction=round(float(npf[i]), 4),
                             x={c: round(float(xs[i, j]), 3) for j, c in enumerate(comp_names)}))
        rows.sort(key=lambda r: -r["fraction"])
        out[name] = dict(T_K=T, phases_considered=phases, assemblage=rows,
                         n_phases=len(rows), seconds=round(time.time() - t0, 1),
                         measured=MEASURED.get(name))
        desc = "; ".join(f"{r['phase']} {r['fraction']:.2f} "
                         f"({', '.join(f'{k}{v_:.2f}' for k, v_ in r['x'].items() if v_ > 0.05)})"
                         for r in rows)
        print(f"{name:>16}  {len(rows)} phase(s): {desc}   | measured: {MEASURED.get(name, '-')}",
              flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", choices=list(DBS), required=True)
    ap.add_argument("--T", type=float, default=T_HOMOG)
    ap.add_argument("--alloys", nargs="*", default=list(ALLOYS))
    ap.add_argument("--alpha-mn-needs-mn", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run(a.db, a.alloys, a.T, a.alpha_mn_needs_mn)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(dict(db=a.db, path=DBS[a.db], T_K=a.T, alpha_mn_needs_mn=a.alpha_mn_needs_mn,
                   results=res), open(a.out, "w"), indent=1)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
