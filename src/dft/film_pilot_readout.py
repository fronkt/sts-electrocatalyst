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
    # species labels such as Ni2 (amendments 7-9: a separate starting moment) are the element
    if [re.sub(r"\d+$", "", r[0]) for r in rows] != atoms.get_chemical_symbols():
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


RY_EV = 13.605693122994
TOL_RY = 1e-3      # amendment 9: same-solution and reproduction tolerance (13.6 meV)
M_SIGN = 0.25      # muB: smaller moments carry no sign in a configuration pattern
METALS = {"Ni", "Fe", "Co"}
# amendment 9, Ni(Fe)OOH candidate configurations (pw.x 1-based atoms; Fe = atom 6, the Fe site):
# (sign of Fe, set of Ni antiparallel to the bulk-like bottom Ni, atom 1)
NIFE_CFG = {"C1": ("+", frozenset({5, 29, 30})), "C2": ("-", frozenset()), "C3": ("+", frozenset({5, 29})),
            "C4": ("+", frozenset({30})),  # C4: Fe0_OH_r4's first SCF (2026-11-16); rule 1 adds every pattern seen
            "C5": ("-", frozenset({30})),  # C5: where the clean slab's C2 single point landed (amendment 11)
            "C6": ("+", frozenset({5}))}   # C6: the pattern Fe0_OOH's relaxation ended in (rule 1, 16:18Z)


def bang_energies(out):
    """Every '!' total energy (Ry) in a pw.x output, in order."""
    if not os.path.exists(out):
        return []
    return [float(x) for x in re.findall(r"(?m)^!\s+total energy\s+=\s+(\S+)\s+Ry", open(out, errors="replace").read())]


def pattern(symbols, moments):
    """Configuration pattern: (sign of each metal with |m| >= M_SIGN relative to atom 1, as a sorted
    tuple of (1-based index, sign)). Atom 1 is a fixed bottom-layer metal in every film."""
    s = 1.0 if moments[0] >= 0 else -1.0
    return tuple((i + 1, "+" if s * m > 0 else "-") for i, (el, m) in enumerate(zip(symbols, moments))
                 if el in METALS and abs(m) >= M_SIGN)


def nife_label(symbols, moments):
    """C1/C2/C3 for a Ni(Fe)OOH pattern, else a description of the pattern."""
    p = dict(pattern(symbols, moments))
    fe = next((i + 1 for i, el in enumerate(symbols) if el == "Fe"), None)
    neg = frozenset(i for i, sg in p.items() if sg == "-" and symbols[i - 1] == "Ni")
    key = (p.get(fe, "0"), neg)
    for k, v in NIFE_CFG.items():
        if v == key:
            return k
    return f"other(Fe{key[0]}, Ni- {sorted(neg)})"


def choose_run(runs, links):
    """Amendment 9 rerun rule over a chain [run, run_r2, ...]: a rerun replaces its predecessor if the
    predecessor completed no SCF, or if it started from the predecessor's last geometry and its first
    energy is at most TOL_RY above the predecessor's last (the same solution). Otherwise the run with
    the lower last energy is used. Returns (name, notes)."""
    from ase.io import read
    cur, notes = links[0], []
    for nxt in links[1:]:
        p_out, n_out = (os.path.join(runs, n, n + ".out") for n in (cur, nxt))
        pe, ne = bang_energies(p_out), bang_energies(n_out)
        if not ne:
            notes.append(f"{nxt}: no completed SCF; {cur} stands"); continue
        if not pe:
            notes.append(f"{nxt} replaces {cur} (predecessor completed no SCF)"); cur = nxt; continue
        try:
            start = read(os.path.join(runs, nxt, nxt + ".in"), format="espresso-in").positions
            last = final_atoms(os.path.join(runs, cur, cur + ".in"), p_out).positions
            same_geom = start.shape == last.shape and float(np.abs(start - last).max()) < 1e-3
        except Exception:
            same_geom = False
        if same_geom:
            d = (ne[0] - pe[-1]) * 1000
            if ne[0] <= pe[-1] + TOL_RY:
                notes.append(f"{nxt} replaces {cur} (same solution: first energy {d:+.2f} mRy vs its last)")
                cur = nxt
            else:
                notes.append(f"{nxt} landed {d:+.2f} mRy above {cur}'s last energy at the same geometry; {cur} stands")
        else:
            # amendment 12: sibling reruns (e.g. Ni0_OOH r4 BFGS and r5 FIRE, both from r3's last
            # geometry): a converged relaxation is preferred over one that did not converge, since
            # QC needs one; otherwise the lower last energy
            conv = {n: qe_qc.trusted_energy_ev(os.path.join(runs, n, n + ".out"),
                                               os.path.join(runs, n, n + ".in")) is not None for n in (cur, nxt)}
            if conv[cur] != conv[nxt]:
                low = nxt if conv[nxt] else cur
                notes.append(f"{nxt} did not start from {cur}'s last geometry; {low} is the converged one and is used")
            else:
                low = nxt if ne[-1] < pe[-1] else cur
                notes.append(f"{nxt} did not start from {cur}'s last geometry; the lower last energy ({low}) is used")
            cur = low
    return cur, notes


def main_u0(args, jobs):
    """Amendment 9 readout: U = 0 runs (u0__NAME, reruns u0__NAME_rK), each state in the lowest of its
    relaxed energy and its fixed-geometry configuration single points (CK__RUN); V1/V2 also as relaxed."""
    dirs = set(os.listdir(args.runs)) if os.path.isdir(args.runs) else set()
    recs, use, notes = {}, {}, {}
    for j in jobs:
        if j["kind"] == "adslab" and j["name"].split("__")[1].startswith("Ni1"):
            continue  # enters no criterion; not run at U = 0 (amendment 9)
        base = j["name"] if j["kind"] == "gas" else "u0__" + j["name"]
        reruns = []
        for d in dirs:
            m = re.fullmatch(re.escape(base) + r"_r(\d+)", d)
            if m:
                reruns.append((int(m.group(1)), d))
        links = [base] + [d for _, d in sorted(reruns)]
        name, nt = choose_run(args.runs, links)
        use[j["name"]], notes[j["name"]] = name, nt
        rec = state_record(args.runs, dict(j, name=name))
        rec["chain"] = links
        out, inp = (os.path.join(args.runs, name, name + s) for s in (".out", ".in"))
        if j["kind"] != "gas" and os.path.exists(out):
            from ase.io import read
            sym = read(inp, format="espresso-in").get_chemical_symbols()
            _, mom = magnetics(out)
            rec["moments"] = mom
            if mom and len(mom) == len(sym):
                neg = [i for i, sg in pattern(sym, mom) if sg == "-"]
                rec["config"] = (nife_label(sym, mom) if j["film"] == "NiFeOOH" else
                                 f"antiparallel {neg}" if neg else "all parallel")
            sps = []
            for k in sorted(d for d in dirs if re.fullmatch(r"C\d__" + re.escape(name), d)):
                so, si = (os.path.join(args.runs, k, k + s) for s in (".out", ".in"))
                e = qe_qc.trusted_energy_ev(so, si) if os.path.exists(so) else None
                _, sm = magnetics(so) if os.path.exists(so) else (None, None)
                got = nife_label(sym, sm) if sm and len(sm) == len(sym) else None
                target = k.split("__")[0]
                # amendment 11: a trusted single point counts as the configuration it landed in (a
                # converged SCF of the state at its relaxed geometry), not as its target if it left it
                sps.append(dict(run=k, target=target, landed=got, energy_ev=e,
                                counts=bool(e is not None and got is not None)))
            rec["single_points"] = sps
            own = [s for s in sps if s["counts"] and s["target"] == s["landed"] == rec.get("config")]
            if own and rec.get("energy_ev") is not None:
                rec["own_config_check_mry"] = round((own[0]["energy_ev"] - rec["energy_ev"]) / RY_EV * 1000, 3)
            cand = [(rec.get("energy_ev"), "relaxed")] + [(s["energy_ev"], s["run"]) for s in sps if s["counts"]]
            cand = [c for c in cand if c[0] is not None]
            if rec.get("energy_ev") is not None and cand:
                rec["energy_lowest_ev"], rec["lowest_from"] = min(cand)
        recs[j["name"]] = rec

    def site_eta(film, metal_tag, key):
        names = {sp: f"{film}__{metal_tag}_{sp}" for sp in ("OH", "O", "OOH")}
        need = [f"{film}__slab", "gas__H2O", "gas__H2", *names.values()]
        E = {n: (recs[n].get(key) if recs[n]["kind"] != "gas" else recs[n].get("energy_ev"))
             if recs[n].get("energy_ev") is not None else None for n in need}
        bad = [n for n in need if E[n] is None or (recs[n]["kind"] == "adslab" and not recs[n].get("intact"))]
        if bad:
            return dict(evaluable=False, failed=bad)
        dG = {sp: delta_G(E[f"{film}__slab"], E[n], sp, E["gas__H2O"], E["gas__H2"]) for sp, n in names.items()}
        r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        return dict(evaluable=True, dG={k: round(v, 3) for k, v in dG.items()}, eta=round(r.overpotential, 3),
                    pls=r.potential_limiting_step)

    sites, verdict = {}, {}
    for key in ("energy_lowest_ev", "energy_ev"):
        tag = "lowest" if key == "energy_lowest_ev" else "as_relaxed"
        s = {k: site_eta(f, m, key) for k, (f, m) in
             {"NiOOH__Ni0": ("NiOOH", "Ni0"), "NiFeOOH__Fe0": ("NiFeOOH", "Fe0"), "CoOOH__Co0": ("CoOOH", "Co0")}.items()}
        sites[tag] = s
        e = {k: v.get("eta") for k, v in s.items()}
        verdict[tag] = dict(
            V1=None if None in (e["NiOOH__Ni0"], e["NiFeOOH__Fe0"]) else bool(e["NiFeOOH__Fe0"] < e["NiOOH__Ni0"]),
            V2=None if None in (e["NiOOH__Ni0"], e["CoOOH__Co0"]) else bool(e["CoOOH__Co0"] < e["NiOOH__Ni0"]))
    v1 = verdict["lowest"]["V1"]
    v1_final = (None if v1 is None or verdict["as_relaxed"]["V1"] is None else
                "configuration-sensitive (not a pass)" if v1 != verdict["as_relaxed"]["V1"] else
                ("pass" if v1 else "fail"))
    result = dict(model="PBE (U = 0), amendment 9", runs_used=use, rerun_notes=notes, states=recs,
                  sites=sites, verdicts=verdict, V1=v1_final)
    out = args.out.replace(".json", "_u0.json") if args.out.endswith("readout.json") else args.out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="\n") as f:
        json.dump(result, f, indent=2)
    for n, r in recs.items():
        sp = "; ".join(f"{s['target']}->{s['landed']} E={s['energy_ev']}" for s in r.get("single_points", []))
        print(f"{n:20s} run={use[n]:26s} {r.get('qc', r.get('status')):10s} E={r.get('energy_ev')} "
              f"steps={r.get('n_ionic')} config={r.get('config')} intact={r.get('intact')} "
              f"lowest={r.get('energy_lowest_ev')} ({r.get('lowest_from')}) own-check={r.get('own_config_check_mry')}"
              + (f" SP: {sp}" if sp else ""))
        for t in notes[n]:
            print(f"    {t}")
    for tag, s in sites.items():
        for k, v in s.items():
            print(f"SITE[{tag}] {k:14s}", v.get("dG"), "eta", v.get("eta"), "PLS", v.get("pls"),
                  "" if v["evaluable"] else f"NOT EVALUABLE: {v['failed']}")
        print(f"[{tag}] V1: {verdict[tag]['V1']}   V2: {verdict[tag]['V2']}")
    print(f"V1 (registered, amendment 9): {v1_final}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="D:/sts-electrocatalyst/film_pilot/out/runs")
    ap.add_argument("--manifest", default=os.path.join(REPO, "runs", "film_pilot_2026-11-14", "manifest.json"))
    ap.add_argument("--out", default=os.path.join(REPO, "results", "film_pilot_2026-11-14", "readout.json"))
    ap.add_argument("--model", choices=["u0", "pbeu"], default="u0",
                    help="u0 = the registered model since amendment 9; pbeu = the superseded PBE+U runs (report only)")
    args = ap.parse_args()
    jobs = json.load(open(args.manifest))["jobs"]
    if args.model == "u0":
        return main_u0(args, jobs)
    print("PBE+U runs: superseded by amendment 9 (B, U = 0); reported only, not a criterion readout")
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
