"""Independent verifier for lowtail (a): registry, DFT parse, geometry match, projections, energies.

Written from the task text and the banked readouts; does not import src/s2/lowtail_dft.
"""
import glob
import hashlib
import json
import os
import re
import sys

import numpy as np

ROOT = r"C:\Users\frank\sts-electrocatalyst"
os.chdir(ROOT)
RY = 13.605693122994  # CODATA 2018 Rydberg in eV
BOHR = 0.529177210903  # CODATA 2018 bohr in A
F_CONV = RY / BOHR


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def J(p):
    return json.load(open(p, encoding="utf-8"))


# ---------------------------------------------------------------- registry
status = {}


def put(job, st, why, recorded_sha=None):
    assert job not in status, job
    status[job] = dict(status=st, why=why, recorded_sha=recorded_sha)


w = J("results/hea_continuation_2026-09-11/winner_readout.json")
for e in w["endpoints"]:
    put(e["job"], e["status"], e.get("reasons"), e["files"]["output"]["sha256_bytes"])
p = J("results/hea_pilot_2026-09-07/completion_readout.json")
for j in p["jobs"]:
    put(j["job"], "ACCEPTED" if j["status"] == "VALID_SCF" else j["status"], j.get("reasons"), j["output"]["sha256_bytes"])
f = J("results/hea_followup_2026-09-07/completion_readout.json")
spec = J("results/hea_followup_2026-09-07/launch_spec.json")["jobs"]
for e in f["endpoints"]:
    if e["source"] == "followup":
        put(e["job"], "ACCEPTED", [], None)
for t in f["failed_tasks"]:
    put(spec[t - 1]["job"], "REJECTED", ["followup failed task %d" % t])
n = J("results/hea_numerical_2026-09-08/status_2026-09-09_2228/readout.json")
for e in n["endpoints"]:
    put(e["job"], e["status"], e.get("reasons"), ((e.get("files") or {}).get("output") or {}).get("sha256_bytes"))
r = J("results/hea_sensitivity_2026-09-09/status_2026-09-10_verified/atomic_replacement_readout.json")
put(r["builder"]["job"], r["builder"]["status"], r["builder"].get("reasons"), r["builder"]["files"]["output"]["sha256_bytes"])
s = J("results/hea_sensitivity_2026-09-09/status_2026-09-10_verified/readout.json")
for e in s["endpoints"]:
    put(e["job"], e["status"], e.get("reasons"), ((e.get("files") or {}).get("output") or {}).get("sha256_bytes"))
for pj in sorted(glob.glob("runs/hea/convergence_probe_2026-09-10/*.probe.json")):
    d = J(pj)
    put(d["job"], d["scientific_status"], [d["diagnostic_status"]] + d["qc_reasons"])
for pj in sorted(glob.glob("runs/hea/ieee_smearing_2026-09-10/*.diagnostic.json")):
    d = J(pj)
    put(d["job"], d["new_endpoint_status"], [d["diagnostic_status"]] + d["scf_reasons"])
for pj in sorted(glob.glob("runs/hea/ieee_init_2026-09-11/*.diagnostic.json")):
    d = J(pj)
    put(d["job"], "NO_SCF", [d["diagnostic_status"]])

outs = sorted(x.replace("\\", "/") for x in glob.glob("runs/hea/**/*.out", recursive=True)
              if not x.endswith(".projwfc.out") and "lowtail" not in x)
jobs_on_disk = {os.path.basename(o)[:-4]: o for o in outs}
unid = sorted(set(jobs_on_disk) - set(status))
missing = sorted(set(status) - set(jobs_on_disk))
counts = {}
for k, v in status.items():
    counts[v["status"]] = counts.get(v["status"], 0) + 1
reg = dict(n_outputs=len(outs), unidentified=unid, readout_jobs_without_output=missing, counts=counts)

# markers in outputs of excluded jobs
markers = {}
for job, v in status.items():
    if v["status"] == "ACCEPTED":
        continue
    txt = open(jobs_on_disk[job], encoding="utf-8", errors="replace").read()
    markers[job] = dict(status=v["status"], why=v["why"],
                        ieee_invalid="IEEE_INVALID" in txt, conv_not="convergence NOT achieved" in txt,
                        max_cpu="Maximum CPU time exceeded" in txt, n_bang=len(re.findall(r"^!\s+total energy", txt, re.M)),
                        job_done="JOB DONE" in txt)


# ---------------------------------------------------------------- QE parsing
def parse_in(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    nat = int(re.search(r"\bnat\s*=\s*(\d+)", "\n".join(lines)).group(1))
    calc = re.search(r"calculation\s*=\s*'(\w+)'", "\n".join(lines)).group(1)
    ci = [i for i, l in enumerate(lines) if l.strip().upper().startswith("CELL_PARAMETERS")]
    ai = [i for i, l in enumerate(lines) if l.strip().upper().startswith("ATOMIC_POSITIONS")]
    assert len(ci) == 1 and len(ai) == 1 and "angstrom" in lines[ci[0]].lower() and "angstrom" in lines[ai[0]].lower()
    cell = [[float(x) for x in lines[ci[0] + k].split()] for k in (1, 2, 3)]
    sym, pos, ifp = [], [], []
    for k in range(nat):
        t = lines[ai[0] + 1 + k].split()
        sym.append(re.sub(r"[\d_]+$", "", t[0]))
        pos.append([float(x) for x in t[1:4]])
        ifp.append([int(x) for x in t[4:7]] if len(t) >= 7 else [1, 1, 1])
    return dict(nat=nat, calc=calc, cell=cell, symbols=sym, positions=pos, if_pos=ifp)


ATOM = re.compile(r"^\s*atom\s+(\d+)\s+type\s+\d+\s+force\s*=\s*(\S+)\s+(\S+)\s+(\S+)\s*$")


def parse_out(path, nat):
    L = open(path, encoding="utf-8", errors="replace").read().splitlines()
    bang = [l for l in L if re.match(r"^!\s+total energy\s*=", l)]
    hdr = [i for i, l in enumerate(L) if "Forces acting on atoms (cartesian axes, Ry/au)" in l]
    conv = sum("convergence has been achieved" in l for l in L)
    bad = [l for l in L if ("IEEE_INVALID" in l or "convergence NOT achieved" in l or "Maximum CPU time" in l)]
    if len(bang) != 1 or len(hdr) != 1 or conv != 1 or bad:
        return dict(ok=False, n_bang=len(bang), n_hdr=len(hdr), conv=conv, bad=len(bad))
    E = float(bang[0].split("=")[1].split()[0]) * RY
    F = {}
    i = hdr[0] + 1
    while len(F) < nat and i < len(L):
        m = ATOM.match(L[i])
        if m:
            F[int(m.group(1))] = [float(m.group(k)) * F_CONV for k in (2, 3, 4)]
        elif "Total force" in L[i] or "contrib" in L[i]:
            break
        i += 1
    assert sorted(F) == list(range(1, nat + 1)), path
    tm = [l for l in L if "total magnetization" in l]
    return dict(ok=True, E=E, F=np.array([F[k] for k in range(1, nat + 1)]),
                total_mag=float(tm[-1].split("=")[1].split()[0]) if tm else None)


# ---------------------------------------------------------------- geometries
cen = J("results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json")
row = cen["results"][0]["row"]
site1 = [x for x in row["per_site_records"] if x["seed"] == 1 and x["site_index"] == 0][0]
slab1 = [x for x in row["decoration_records"] if x["seed"] == 1][0]["relaxed_slab"]
site0 = [x for x in row["per_site_records"] if x["seed"] == 0 and x["site_index"] == 0][0]
slab0 = [x for x in row["decoration_records"] if x["seed"] == 0][0]["relaxed_slab"]
rep = {a["start"]: a for a in J("results/cr_site_chains_2026-09-06/leader_ooh_replay.json")["attempts"]}
G = {"winner_slab": slab1}
for st in ("OH", "O", "OOH"):
    G["winner_" + st] = site1["relaxed_states"][st]
G["leader_builder"] = rep["builder"]["geometry"]
G["leader_pull2.10"] = rep["pull2.10"]["geometry"]
G["gas_H2O"] = row["gas_reference_records"]["H2O"]
G["gas_H2"] = row["gas_reference_records"]["H2"]
geom_meta = dict(site1_index=site1["initial_binding_metal_index"], site0_index=site0["initial_binding_metal_index"],
                 pull_equals_census_OOH=(G["leader_pull2.10"]["positions_A"] == site0["relaxed_states"]["OOH"]["positions_A"]))


def match(inp):
    hits = []
    for name, g in G.items():
        if g["symbols"] != inp["symbols"]:
            continue
        fixed = sorted(i for i, fp in enumerate(inp["if_pos"]) if fp == [0, 0, 0])
        partial = [i for i, fp in enumerate(inp["if_pos"]) if fp not in ([0, 0, 0], [1, 1, 1])]
        if partial:
            continue
        exact = (inp["positions"] == g["positions_A"] and inp["cell"] == g["cell_A"]
                 and fixed == sorted(g["fixed_atom_indices"]))
        if exact:
            hits.append(name)
    return hits


def mic(v, cell):
    L = np.diag(np.array(cell))
    return v - L * np.round(v / L)


def proj(geom_name, pos, F, cell, n_clean, clean):
    site = 16
    pos = np.array(pos)
    clean = np.array(clean)
    # axial O: lattice O below the site in the clean slab, nearest with negative dz
    cands = []
    for j in range(n_clean):
        if G["winner_slab"]["symbols"][j] != "O":
            continue
        v = mic(clean[j] - clean[site], cell)
        d = np.linalg.norm(v)
        if d < 2.4 and v[2] < 0:
            cands.append((v[2] / d, d, j))
    ax = min(cands)[2]
    out = dict(axial_index=ax, n_axial_candidates=len(cands))
    lift = mic(pos[site] - clean[site], cell)[2]
    vax = mic(pos[ax] - pos[site], cell)
    uax = vax / np.linalg.norm(vax)
    out.update(lift=float(lift), d_axial=float(np.linalg.norm(vax)), Fz_site=float(F[site, 2]), Fz_axial=float(F[ax, 2]),
               axial_stretch=float((F[ax] - F[site]) @ uax))
    if len(pos) > n_clean:
        o = n_clean
        vo = mic(pos[o] - pos[site], cell)
        u = vo / np.linalg.norm(vo)
        out.update(ads_index=o, d_CrO=float(np.linalg.norm(vo)), Fz_O=float(F[o, 2]),
                   bond_stretch=float((F[o] - F[site]) @ u), pair_Fz=float(F[o, 2] + F[site, 2]),
                   F_site_along_bond=float(F[site] @ u), F_O_along_bond=float(F[o] @ u))
    return out


rows = []
for job in sorted(status):
    v = status[job]
    o = jobs_on_disk[job]
    rec = dict(job=job, status=v["status"], out_sha=sha(o), recorded_sha=v["recorded_sha"])
    if v["status"] != "ACCEPTED":
        rows.append(rec)
        continue
    inpath = o[:-4] + ".run.in" if os.path.exists(o[:-4] + ".run.in") else o[:-4] + ".in"
    inp = parse_in(inpath)
    rec["in"] = inpath
    rec["calc"] = inp["calc"]
    rec["hash_ok"] = (v["recorded_sha"] is None) or (v["recorded_sha"] == rec["out_sha"])
    hits = match(inp)
    rec["geometry"] = hits
    po = parse_out(o, inp["nat"])
    rec["parse_ok"] = po["ok"]
    if not po["ok"] or len(hits) != 1:
        rec["parse"] = {k: po[k] for k in po if k != "F"}
        rows.append(rec)
        continue
    F = po["F"]
    mask = np.array(inp["if_pos"], dtype=float)
    fn = np.linalg.norm(F * mask, axis=1)
    rec.update(E=po["E"], total_mag=po["total_mag"], fmax_free=float(fn.max()), argmax=int(fn.argmax()),
               argmax_sym=inp["symbols"][int(fn.argmax())])
    if hits[0].startswith("winner"):
        rec["site"] = proj(hits[0], inp["positions"], F, inp["cell"], len(slab1["symbols"]), slab1["positions_A"])
        rec["site_rank"] = int(np.sum(fn > fn[16]) + 1)
        rec["n_free"] = int((mask.sum(axis=1) > 0).sum())
    if hits[0].startswith("leader"):
        rec["Fz_Cr16"] = float(F[16, 2])
        rec["Fz_site0"] = float(F[site0["initial_binding_metal_index"], 2])
    rec["projector"] = "atomic" if "atomic" in job else "ortho"
    rows.append(rec)

# pairs: same prefix/projector/variant
acc = [x for x in rows if x["status"] == "ACCEPTED" and x.get("parse_ok") and len(x.get("geometry", [])) == 1]
lead = {x["job"]: x for x in acc if x["geometry"][0].startswith("leader")}
pairs = []
for j, x in lead.items():
    if "__leader_builder__" in j:
        pj = j.replace("__leader_builder__", "__leader_pull2.10__")
        if pj in lead:
            pairs.append(dict(builder=j, pull=pj, dE=lead[pj]["E"] - x["E"]))
# replacement pair
rb, rp = r["builder"]["job"], r["pull"]["job"]
if rb in lead and rp in lead:
    pairs.append(dict(builder=rb, pull=rp, dE=lead[rp]["E"] - lead[rb]["E"], replacement=True))
paired = {p_["builder"] for p_ in pairs} | {p_["pull"] for p_ in pairs}
unpaired = sorted(set(lead) - paired)

# compare with banked followup pair gaps
banked = {(p_["builder"], p_["pull"]): p_["gap_eV"] for p_ in f["pairs"]}
for p_ in pairs:
    k = (p_["builder"], p_["pull"])
    if k in banked:
        p_["banked_gap"] = banked[k]
        p_["banked_minus_mine"] = banked[k] - p_["dE"]

# DFT gas references: last '!' energy from converged relax
gas = {}
for name in ("H2O", "H2"):
    t = open(f"runs/Cr_slab/{name}.out", encoding="utf-8", errors="replace").read()
    assert "bfgs converged" in t and "JOB DONE" in t
    Es = re.findall(r"^!\s+total energy\s*=\s*(\S+)\s+Ry", t, re.M)
    fe = re.findall(r"Final energy\s*=\s*(\S+)\s+Ry", t)
    gas[name] = dict(last_bang=float(Es[-1]) * RY, final=(float(fe[-1]) * RY if fe else None), sha=sha(f"runs/Cr_slab/{name}.out"),
                     winner_readout_sha=w["gas_references"][name]["files"]["output"]["sha256_bytes"],
                     winner_readout_E=w["gas_references"][name]["energy_eV"])

coef = {"OH": (1.0, -0.5), "O": (1.0, -1.0), "OOH": (2.0, -1.5)}
chain = {}
byg = {}
for x in acc:
    if x["geometry"][0].startswith("winner"):
        byg[(x["geometry"][0], x["projector"])] = x
for projn in ("atomic", "ortho"):
    Eslab = byg[("winner_slab", projn)]["E"]
    ads = {}
    for st in ("OH", "O", "OOH"):
        a, b = coef[st]
        ads[st] = byg[("winner_" + st, projn)]["E"] - Eslab - (a * gas["H2O"]["last_bang"] + b * gas["H2"]["last_bang"])
    ads["O-OH"] = ads["O"] - ads["OH"]
    ads["OOH-O"] = ads["OOH"] - ads["O"]
    ads["banked"] = w["electronic_chains"]["electronic_adsorption_eV"][projn]
    chain[projn] = ads

out = dict(registry=reg, markers=markers, geom_meta=geom_meta, rows=rows, pairs=pairs, unpaired=unpaired, gas=gas, chain=chain,
           consts=dict(RY=RY, F_CONV=F_CONV))
json.dump(out, open("results/lowtail_dft_2026-09-16/_verify/v_zero.json", "w"), indent=1, default=float)
print(json.dumps(reg, indent=1))
print("accepted parsed+matched:", len(acc))
for x in rows:
    if x["status"] == "ACCEPTED":
        print(x["job"][:40], x["projector"] if "projector" in x else "", x.get("geometry"), x.get("hash_ok"), x.get("parse_ok"), x.get("calc"),
              round(x.get("fmax_free", -1), 3), x.get("argmax_sym"), x.get("argmax"))
