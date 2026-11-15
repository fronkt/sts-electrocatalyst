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


def final_atoms(inp, out):
    """Cell and species from the input deck, positions from the output's last ATOMIC_POSITIONS
    block (pw.x's 'final coordinates' after a converged relax). ase's espresso-out reader is not
    used: it asserts on these spin-polarised QE 7.5 outputs ((2, 0) eigenvalue blocks vs 9 k)."""
    from ase.io import read
    atoms = read(inp, format="espresso-in")
    txt = open(out, errors="replace").read()
    starts = [m.end() for m in re.finditer(r"ATOMIC_POSITIONS \(angstrom\)\n", txt)]
    if not starts:
        raise ValueError("no ATOMIC_POSITIONS block in the output")
    rows = [r.split() for r in txt[starts[-1]:].split("\n")[:len(atoms)]]
    if [r[0] for r in rows] != atoms.get_chemical_symbols():
        raise ValueError("species in the last ATOMIC_POSITIONS block do not match the input")
    atoms.positions = np.array([[float(x) for x in r[1:4]] for r in rows])
    return atoms


def ionic_steps(runs, name):
    out = os.path.join(runs, name, name + ".out")
    return len(re.findall(r"^!", open(out, errors="replace").read(), re.M)) if os.path.exists(out) else 0


def state_record(runs, job, prior_steps=0):
    """prior_steps: ionic steps of the earlier runs this one restarted from (same relaxation)."""
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
    try:
        atoms = final_atoms(inp, out)
    except Exception as e:  # e.g. a run stopped before its first geometry; it has no trusted energy anyway
        rec.update(intact=False, warnings=[f"no final geometry: {type(e).__name__}: {e}"]); return rec
    s = job["site_index"]
    if site is not None and len(site) == len(atoms):
        rec["mag_site"] = site[s]
    d_site = float(np.linalg.norm(atoms.positions[N_SLAB] - atoms.positions[s]))
    rec["n_ionic_chain"] = rec["n_ionic"] + prior_steps
    chk = ads_qc.check_structure(atoms, job["site_metal"], n_slab=N_SLAB, n_ionic=rec["n_ionic_chain"])
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
    # Reruns that changed only SCF mixing (amendment 2): same structure, same converged energy
    # target, so the rerun's energy stands in for the original state.
    # Amendment 3: _r2/_r3 also cover restarts from the last geometry and a fixed-moment rerun;
    # a later suffix overrides an earlier one when both have a trusted energy.
    dirs = set(os.listdir(args.runs)) if os.path.isdir(args.runs) else set()
    for j in list(jobs):
        sufs = sorted((int(m.group(1)), d) for d in dirs
                      if (m := re.fullmatch(re.escape(j["name"]) + r"_r(\d+)", d)))
        for _, d in sufs:  # ascending, so the latest trusted rerun wins below
            jobs.append(dict(j, name=d, rerun_of=j["name"]))
    # A rerun restarted from its predecessor's last geometry (amendments 3, 4, 6) or, for a U-ramp
    # rerun, from the input geometry after a predecessor that never finished a step; either way the
    # relaxation's step count is the sum over the chain up to and including the run itself.
    chain = {}
    for j in jobs:
        base = j.get("rerun_of", j["name"])
        chain.setdefault(base, []).append(j["name"])
    recs = {}
    for j in jobs:
        links = chain[j.get("rerun_of", j["name"])]
        prior = sum(ionic_steps(args.runs, n) for n in links[:links.index(j["name"])])
        recs[j["name"]] = state_record(args.runs, j, prior_steps=prior)
    E = {n: r.get("energy_ev") for n, r in recs.items()}
    # Each registered state is evaluated on ONE run, energy and integrity alike: the latest
    # rerun with a trusted energy, else the original.
    eff = {}
    for j in jobs:
        if j.get("rerun_of") and E.get(j["name"]) is not None:
            eff[j["rerun_of"]] = j["name"]
    use = lambda n: eff.get(n, n)  # noqa: E731
    EH2O, EH2 = E.get(use("gas__H2O")), E.get(use("gas__H2"))

    sites = {}
    for j in jobs:
        if j["kind"] != "adslab" or j.get("rerun_of"):
            continue
        key = j["name"].rsplit("_", 1)[0]
        sites.setdefault(key, dict(film=j["film"], metal=j["site_metal"], states={}))
        sites[key]["states"][j["species"]] = use(j["name"])
    for key, s in sites.items():
        slab_name = use(f"{s['film']}__slab")
        slab = E.get(slab_name)
        names = s["states"]
        s["runs_used"] = [slab_name, *names.values()]
        bad = [n for n in [slab_name, use("gas__H2O"), use("gas__H2"), *names.values()]
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
