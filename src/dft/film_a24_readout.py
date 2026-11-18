#!/usr/bin/env python3
"""Readout for amendment 24 (docs/research/film-dft-pilot-2026-11-14.md): the PBE+U ordering check (amendment
23 B) with its five failed states rerun in two stages.

Per state at PBE+U (U = 0 geometry):
  * converged in amendment 23 (conv_thr 1e-5): the A23U__RUN energy, band 0;
  * rerun: stage 1 (S1) is a conv_thr 1e-5 SCF run to its electron_maxstep (A23U__RUN for the NiOOH
    states, A24S__RUN for Fe0_OH and Fe0_OOH); stage 2 (A24U__RUN) restarts from S1's density at
    conv_thr 1e-3. QC: S1 converged (then S1's energy is used, band 0), or S1 ran to its electron_maxstep
    and its last 50 energies span <= 2 mRy; S2 converged; |E_S2 - mean(S1 last 50)| <= 2 mRy. The
    energy is E_S2 with a band of +/- 2 mRy.
  * every used point: every Ni low-spin (|m| < 1.6 muB); sign pattern and Fe moment reported.
Steps and eta carry the bands as intervals (each step's band is the sum of the bands of the two states
it involves; the gas references are exact). The ordering is "kept" if eta_Fe0's upper end is below
eta_Ni0's lower end, "reversed" if eta_Fe0's lower end is at or above eta_Ni0's upper end, else "not
determined". V1 (U = 0) is not changed by this readout.

  python src/dft/film_a24_readout.py [--runs DIR] [--base readout_u0.json] [--out a24.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src"))

from hea_oer.referencing import delta_G  # noqa: E402

_spec = importlib.util.spec_from_file_location("ffr", os.path.join(HERE, "film_followup_readout.py"))
ffr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ffr)

RY_EV = 13.605693122994
BAND_RY = 2e-3        # amendment 24: per rerun state, and the S1 stationarity and S1-S2 agreement limits
N_LAST = 50
EQ, G_TOTAL = 1.23, 4.92
CONVERGED_A23 = ("NiOOH__slab", "NiFeOOH__slab", "NiFeOOH__Fe0_O")
RERUN = {"NiOOH__Ni0_OH": "A23U", "NiOOH__Ni0_O": "A23U", "NiOOH__Ni0_OOH": "A23U",
         "NiFeOOH__Fe0_OH": "A24S", "NiFeOOH__Fe0_OOH": "A24S"}  # state -> its stage-1 run's prefix
SITES = {"NiOOH__Ni0": ("NiOOH", "Ni0"), "NiFeOOH__Fe0": ("NiFeOOH", "Fe0")}


def scf_trace(out):
    """Per-iteration total energies (Ry) of a pw.x scf output, whether it ended at maxstep, and its maxstep."""
    t = open(out, errors="replace").read()
    E = [float(x) for x in re.findall(r"(?m)^\s+total energy\s+=\s+(-?[\d.]+) Ry$", t)]
    stop = re.search(r"convergence NOT achieved after\s+(\d+) iterations", t)
    return E, (int(stop.group(1)) if stop else None)


def maxstep(inp):
    return int(re.search(r"electron_maxstep = (\d+)", open(inp).read()).group(1))


def stage1(runs, name):
    out, inp = (os.path.join(runs, name, name + s) for s in (".out", ".in"))
    if not os.path.exists(out):
        return dict(run=name, status="missing", ok=False)
    p = ffr.point(runs, name)
    if p["energy_ev"] is not None:
        return dict(run=name, status="converged", ok=True, energy_ev=p["energy_ev"], point=p)
    E, stopped = scf_trace(out)
    ms = maxstep(inp)
    last = E[-N_LAST:]
    rng = (max(last) - min(last)) if last else None
    ok = stopped == ms and len(E) >= N_LAST and rng is not None and rng <= BAND_RY
    return dict(run=name, status="ran to maxstep" if stopped == ms else "stopped early (no maxstep line)",
                iterations=len(E), maxstep=ms, last50_range_mry=None if rng is None else round(rng * 1e3, 3),
                last50_mean_ry=sum(last) / len(last) if last else None, ok=bool(ok))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="D:/sts-electrocatalyst/film_pilot/out/runs")
    ap.add_argument("--base", default=os.path.join(REPO, "results", "film_pilot_2026-11-14", "readout_u0.json"))
    ap.add_argument("--out", default=os.path.join(REPO, "results", "film_pilot_2026-11-14", "a24_pbeu.json"))
    a = ap.parse_args()
    st = json.load(open(a.base))["states"]
    gas = {g: st[g]["energy_ev"] for g in ("gas__H2O", "gas__H2")}
    rec, E, B = {}, {}, {}
    for state in ffr.B_STATES:
        run = st[state]["name"]
        r = dict(run=run)
        if state in CONVERGED_A23:
            p = ffr.point(a.runs, f"A23U__{run}")
            r.update(source="amendment 23 (conv_thr 1e-5)", point=p, energy_ev=p["energy_ev"], band_ev=0.0)
            used = p
        else:
            s1 = stage1(a.runs, f"{RERUN[state]}__{run}")
            r["stage1"] = s1
            if s1["status"] == "converged":
                used = s1["point"]
                r.update(source="stage 1 converged (conv_thr 1e-5)", energy_ev=used["energy_ev"], band_ev=0.0)
            else:
                p = ffr.point(a.runs, f"A24U__{run}")
                r["stage2"] = p
                agree = None
                if p["energy_ev"] is not None and s1.get("last50_mean_ry") is not None:
                    agree = abs(p["energy_ev"] / RY_EV - s1["last50_mean_ry"]) * 1e3
                    r["stage2_vs_stage1_mry"] = round(agree, 3)
                ok = s1["ok"] and p["energy_ev"] is not None and agree is not None and agree <= BAND_RY * 1e3
                r.update(source="stage 2 (conv_thr 1e-3)", energy_ev=p["energy_ev"] if ok else None,
                         band_ev=BAND_RY * RY_EV, stages_ok=bool(ok))
                used = p
        u0_pat = ffr.describe(ffr.symbols(os.path.join(a.runs, run, run + ".in")), st[state]["moments"])
        r.update(u0_pattern=u0_pat, pattern=used.get("pattern"), ni_max_abs=used.get("ni_max_abs"),
                 fe_moment=used.get("fe_moment"))
        r["pattern_changed"] = None if used.get("pattern") is None else used.get("pattern") != u0_pat
        r["low_spin"] = None if used.get("ni_max_abs") is None else used["ni_max_abs"] < ffr.NI_HIGH_SPIN
        r["evaluable"] = bool(r.get("energy_ev") is not None and r["low_spin"])
        if r["evaluable"]:
            E[state], B[state] = r["energy_ev"], r["band_ev"]
        rec[state] = r

    def site(film, tag, Es, Bs):
        names = {"slab": f"{film}__slab", **{sp: f"{film}__{tag}_{sp}" for sp in ("OH", "O", "OOH")}}
        if any(n not in Es for n in names.values()):
            return dict(evaluable=False, missing=[n for n in names.values() if n not in Es])
        dG = {sp: delta_G(Es[names["slab"]], Es[names[sp]], sp, gas["gas__H2O"], gas["gas__H2"])
              for sp in ("OH", "O", "OOH")}
        s = [dG["OH"], dG["O"] - dG["OH"], dG["OOH"] - dG["O"], G_TOTAL - dG["OOH"]]
        b = {k: Bs[n] for k, n in names.items()}
        sb = [b["OH"] + b["slab"], b["O"] + b["OH"], b["OOH"] + b["O"], b["OOH"] + b["slab"]]
        eta = max(s) - EQ
        lo, hi = max(x - y for x, y in zip(s, sb)) - EQ, max(x + y for x, y in zip(s, sb)) - EQ
        return dict(evaluable=True, dG={k: round(v, 3) for k, v in dG.items()}, steps=[round(x, 3) for x in s],
                    step_bands=[round(x, 3) for x in sb], eta=round(eta, 3), pls=s.index(max(s)) + 1,
                    eta_interval=[round(lo, 3), round(hi, 3)])

    sites = {k: site(f, m, E, B) for k, (f, m) in SITES.items()}
    E0 = dict({n: st[n]["energy_ev"] for n in ffr.B_STATES})
    sites0 = {k: site(f, m, E0, {n: 0.0 for n in E0}) for k, (f, m) in SITES.items()}
    for k, v in sites.items():
        if v["evaluable"]:
            v["shift_vs_u0"] = dict(dG={sp: round(x - sites0[k]["dG"][sp], 3) for sp, x in v["dG"].items()},
                                    eta=round(v["eta"] - sites0[k]["eta"], 3))
    fe, ni = sites["NiFeOOH__Fe0"], sites["NiOOH__Ni0"]
    order = None
    if fe["evaluable"] and ni["evaluable"]:
        order = ("kept" if fe["eta_interval"][1] < ni["eta_interval"][0] else
                 "reversed" if fe["eta_interval"][0] >= ni["eta_interval"][1] else "not determined")
    res = dict(amendment=24, base=a.base, runs=a.runs, band_ry=BAND_RY, states=rec, sites=sites,
               sites_u0_as_relaxed=sites0, ordering=order if order else "not determined")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="\n") as f:
        json.dump(res, f, indent=2, default=str)
    for s, r in rec.items():
        extra = ""
        if "stage1" in r:
            s1 = r["stage1"]
            extra = (f" S1 {s1['run']}: {s1['status']}, it {s1.get('iterations')}, last-50 range "
                     f"{s1.get('last50_range_mry')} mRy, ok {s1['ok']}; S2 {r.get('stage2', {}).get('status')}, "
                     f"S2-S1 {r.get('stage2_vs_stage1_mry')} mRy")
        print(f"{s:18s} {r['source']}: E {r.get('energy_ev')} band {round(r['band_ev'], 4)} eV, Ni max |m| "
              f"{r['ni_max_abs']}, Fe {r['fe_moment']}, pattern {r['pattern']} (U=0 {r['u0_pattern']}), "
              f"evaluable {r['evaluable']}{extra}")
    for k, v in sites.items():
        print(f"{k}: {v.get('dG')} steps {v.get('steps')} +/- {v.get('step_bands')} eta {v.get('eta')} "
              f"{v.get('eta_interval')} PLS {v.get('pls')} shift {v.get('shift_vs_u0')}"
              + ("" if v["evaluable"] else f" NOT EVALUABLE {v['missing']}"))
    print(f"ordering at PBE+U (U = 0 geometries, amendment 24): {res['ordering']}")


if __name__ == "__main__":
    main()
