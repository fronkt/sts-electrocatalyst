#!/usr/bin/env python3
"""Readout for the film-model DFT pilot against the registered criteria
(docs/research/film-dft-pilot-2026-11-14.md).

Per state: strict qe_qc energy, adsorbate integrity (bound to its site, *OOH intact),
ionic-step count, final total and site magnetic moments. Per site: CHE dG and eta.
Then V1 (Fe site < NiOOH Ni site) and V2 (CoOOH < NiOOH). A state that fails QC makes its
site "not evaluable"; nothing is imputed.

  python src/dft/film_pilot_readout.py --runs D:/sts-electrocatalyst/film_pilot/out/runs
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src"))
from hea_oer.descriptors import oer_overpotential  # noqa: E402
from hea_oer.referencing import delta_G  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


qe_qc = _load("qe_qc")
ads_qc = _load("adsorbate_qc")
N_SLAB = 48


def magnetics(outfile):
    txt = open(outfile, errors="replace").read()
    tot = re.findall(r"total magnetization\s+=\s+([-\d.]+)", txt)
    blocks = txt.split("Magnetic moment per site")
    site = None
    if len(blocks) > 1:
        site = [float(m) for m in re.findall(r"magn=\s*([-\d.]+)", blocks[-1].split("\n\n")[0])]
    return (float(tot[-1]) if tot else None), site


def state_record(runs, job):
    from ase.io import read
    name = job["name"]
    out = os.path.join(runs, name, name + ".out")
    inp = os.path.join(runs, name, name + ".in")
    rec = dict(name=name, kind=job["kind"])
    if not os.path.exists(out):
        rec.update(status="missing"); return rec
    scan = qe_qc.scan(out, inp if os.path.exists(inp) else None)
    rec.update(qc=scan["verdict"], energy_ev=qe_qc.trusted_energy_ev(out, inp if os.path.exists(inp) else None),
               n_ionic=len(re.findall(r"^!", open(out, errors="replace").read(), re.M)))
    tot, site = magnetics(out)
    rec["mag_total"] = tot
    if job["kind"] != "adslab":
        return rec
    atoms = read(out, format="espresso-out", index=-1)
    s = job["site_index"]
    if site is not None and len(site) == len(atoms):
        rec["mag_site"] = site[s]
    d_site = float(np.linalg.norm(atoms.positions[N_SLAB] - atoms.positions[s]))
    chk = ads_qc.check_structure(atoms, job["site_metal"], n_slab=N_SLAB, n_ionic=rec["n_ionic"])
    rec.update(d_site_O=round(d_site, 3), tier=chk["tier"], warnings=chk["reasons"])
    intact = chk["tier"] != "desorbed" and d_site <= ads_qc.M_O_DESORBED_MIN
    if job["species"] == "OOH":
        p = atoms.positions[N_SLAB:]
        d_oo = float(np.linalg.norm(p[1] - p[0])); d_oh = float(np.linalg.norm(p[2] - p[1]))
        rec.update(d_OO=round(d_oo, 3), d_OH=round(d_oh, 3))
        intact = intact and d_oo < 1.65 and d_oh < 1.25
    rec["intact"] = bool(intact)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="D:/sts-electrocatalyst/film_pilot/out/runs")
    ap.add_argument("--manifest", default=os.path.join(REPO, "runs", "film_pilot_2026-11-14", "manifest.json"))
    ap.add_argument("--out", default=os.path.join(REPO, "results", "film_pilot_2026-11-14", "readout.json"))
    args = ap.parse_args()
    jobs = json.load(open(args.manifest))["jobs"]
    recs = {j["name"]: state_record(args.runs, j) for j in jobs}
    E = {n: r.get("energy_ev") for n, r in recs.items()}
    EH2O, EH2 = E.get("gas__H2O"), E.get("gas__H2")

    sites = {}
    for j in jobs:
        if j["kind"] != "adslab":
            continue
        key = j["name"].rsplit("_", 1)[0]
        sites.setdefault(key, dict(film=j["film"], metal=j["site_metal"], states={}))
        sites[key]["states"][j["species"]] = j["name"]
    for key, s in sites.items():
        slab = E.get(f"{s['film']}__slab")
        names = s["states"]
        bad = [n for n in [f"{s['film']}__slab", "gas__H2O", "gas__H2", *names.values()]
               if E.get(n) is None or (recs[n]["kind"] == "adslab" and not recs[n].get("intact"))]
        if bad:
            s.update(evaluable=False, failed=bad); continue
        dG = {sp: delta_G(slab, E[n], sp, EH2O, EH2) for sp, n in names.items()}
        r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        s.update(evaluable=True, dG={k: round(v, 3) for k, v in dG.items()},
                 eta=round(r.overpotential, 3), pls=r.potential_limiting_step)

    def eta(k):
        return sites.get(k, {}).get("eta")

    e_ni, e_fe, e_co = eta("NiOOH__Ni0"), eta("NiFeOOH__Fe0"), eta("CoOOH__Co0")
    v1 = None if None in (e_ni, e_fe) else bool(e_fe < e_ni)
    v2 = None if None in (e_ni, e_co) else bool(e_co < e_ni)
    result = dict(states=recs, sites=sites, V1_fe_beats_nioooh=v1, V2_co_beats_niooh=v2)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="\n") as f:
        json.dump(result, f, indent=2)

    for n, r in recs.items():
        extra = "" if r["kind"] != "adslab" else (
            f" d(site-O)={r.get('d_site_O')} tier={r.get('tier')} intact={r.get('intact')}"
            f" mag_site={r.get('mag_site')} {'; '.join(r.get('warnings', []))}")
        print(f"{n:22s} {r.get('qc', r.get('status')):12s} E={r.get('energy_ev')} steps={r.get('n_ionic')}"
              f" mag={r.get('mag_total')}{extra}")
    for k, s in sites.items():
        print(f"SITE {k:16s}", s.get("dG"), "eta", s.get("eta"), "PLS", s.get("pls"),
              "" if s["evaluable"] else f"NOT EVALUABLE: {s['failed']}")
    print(f"V1 (Fe site < NiOOH Ni site): {v1}   V2 (CoOOH < NiOOH): {v2}")


if __name__ == "__main__":
    main()
