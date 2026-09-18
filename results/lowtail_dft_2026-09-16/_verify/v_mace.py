"""Independent MACE-MPA-0 checks: stored energies at 8 geometries, site forces, relaxations from deck starts.

Does not import src/s2/lowtail_dft. One structure at a time.
"""
import gc
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = r"C:\Users\frank\sts-electrocatalyst"
os.chdir(ROOT)
CK = Path.home() / ".cache" / "mace" / "macempa0mediummodel"
CENSUS_SHA = "75428afe3a1d7d8062e19bcaabd5c433623cabf308242ec9fb493e38604fb638"


def J(p):
    return json.load(open(p, encoding="utf-8"))


ck_sha = hashlib.sha256(CK.read_bytes()).hexdigest()
assert ck_sha == CENSUS_SHA, ck_sha
import torch  # noqa: E402
from ase import Atoms  # noqa: E402
from ase.constraints import FixAtoms  # noqa: E402
from ase.optimize import BFGS  # noqa: E402
from mace.calculators import mace_mp  # noqa: E402

torch.set_num_threads(2)
calc = mace_mp(model=str(CK), device="cpu", default_dtype="float64")


def atoms_of(rec, fixed=True):
    a = Atoms(symbols=rec["symbols"], positions=rec["positions_A"], cell=rec["cell_A"], pbc=rec["pbc"])
    if fixed and rec.get("fixed_atom_indices"):
        a.set_constraint(FixAtoms(indices=rec["fixed_atom_indices"]))
    return a


def mic(v, cell):
    L = np.diag(np.array(cell))
    return v - L * np.round(v / L)


out = dict(checkpoint_sha256=ck_sha)
mode = sys.argv[1] if len(sys.argv) > 1 else "sp"

cen = J("results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json")
row = cen["results"][0]["row"]
site1 = [x for x in row["per_site_records"] if x["seed"] == 1 and x["site_index"] == 0][0]
slab1 = [x for x in row["decoration_records"] if x["seed"] == 1][0]["relaxed_slab"]
rep = {a["start"]: a for a in J("results/cr_site_chains_2026-09-06/leader_ooh_replay.json")["attempts"]}
site0 = [x for x in row["per_site_records"] if x["seed"] == 0 and x["site_index"] == 0][0]

if mode == "sp":
    G = {"winner_slab": slab1, "winner_OH": site1["relaxed_states"]["OH"], "winner_O": site1["relaxed_states"]["O"],
         "winner_OOH": site1["relaxed_states"]["OOH"], "leader_builder": rep["builder"]["geometry"],
         "leader_pull2.10": rep["pull2.10"]["geometry"], "gas_H2O": row["gas_reference_records"]["H2O"],
         "gas_H2": row["gas_reference_records"]["H2"]}
    census_start = {r_["start"]: r_["energy_eV"] for r_ in site0["start_records"]["OOH"]}
    res = {}
    for name, rec in G.items():
        a = atoms_of(rec, fixed=False)
        a.calc = calc
        E = float(a.get_potential_energy())
        F = np.array(a.get_forces(), copy=True)
        mask = np.ones_like(F)
        for i in rec.get("fixed_atom_indices", []):
            mask[i] = 0
        fn = np.linalg.norm(F * mask, axis=1)
        res[name] = dict(E=E, stored=rec["energy_eV"], dE=E - rec["energy_eV"], fmax_free=float(fn.max()),
                         Fz16=float(F[16, 2]) if len(F) > 16 else None)
        a.calc = None
        del a
        gc.collect()
        print(name, res[name], flush=True)
    res["leader_builder_replay_minus_census_start"] = rep["builder"]["energy_eV"] - census_start["builder"]
    res["mace_pull_minus_builder"] = res["leader_pull2.10"]["E"] - res["leader_builder"]["E"]
    out["sp"] = res
    json.dump(out, open("results/lowtail_dft_2026-09-16/_verify/v_mace_sp.json", "w"), indent=1)

if mode == "relax":
    SITES = [("Cu8Cr23Mn35Co34__s20_site2", "results/site_census_2026-09-06/results/mpa0_ext__Cu8Cr23Mn35Co34__s18-20_result.json", 20, 2),
             ("Ni31Cr29Cu5Mn35__s1_site0", "results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json", 1, 0),
             ("Fe25Co25Ni25Cr25__s2_site0", "results/site_census_2026-09-06/results/mpa0__Fe25Co25Ni25Cr25_result.json", 2, 0)]
    which = sys.argv[2]
    tag, path, seed, site = [s_ for s_ in SITES if s_[0] == which][0]
    d = J(path)
    rw = [r_ for r_ in d["results"] if r_["status"] == "evaluated"][0]["row"]
    ps = [p for p in rw["per_site_records"] if p["seed"] == seed and p["site_index"] == site]
    assert len(ps) == 1
    ps = ps[0]
    slab = [x for x in rw["decoration_records"] if x["seed"] == seed][0]["relaxed_slab"]
    Ost = ps["relaxed_states"]["O"]
    m = ps["initial_binding_metal_index"]
    cell = slab["cell_A"]
    clean = np.array(slab["positions_A"])
    # axial O: clean-slab lattice O bonded to site from below
    cands = []
    for j, sy in enumerate(slab["symbols"]):
        if sy != "O":
            continue
        v = mic(clean[j] - clean[m], cell)
        dd = np.linalg.norm(v)
        if dd < 2.4:
            cands.append((v[2] / dd, dd, j))
    ax = min(cands)[2]

    def site_geo(pos):
        pos = np.array(pos)
        lift = mic(pos[m] - clean[m], cell)[2]
        dax = np.linalg.norm(mic(pos[ax] - pos[m], cell))
        o = len(clean)
        dO = np.linalg.norm(mic(pos[o] - pos[m], cell))
        metals = [j for j, sy in enumerate(slab["symbols"]) if sy not in ("O", "H")]
        near = min(metals, key=lambda j: np.linalg.norm(mic(pos[o] - pos[j], cell)))
        return dict(lift=float(lift), d_axial=float(dax), d_CrO=float(dO), nearest_metal=int(near))

    unrec = dict(symbols=slab["symbols"] + ["O"], cell_A=cell, pbc=slab["pbc"],
                 positions_A=[list(p) for p in slab["positions_A"]] + [[slab["positions_A"][m][0], slab["positions_A"][m][1], slab["positions_A"][m][2] + 1.635]],
                 fixed_atom_indices=slab["fixed_atom_indices"])
    # nearest other atom to the new O
    pos = np.array(unrec["positions_A"])
    dn = min(np.linalg.norm(mic(pos[j] - pos[-1], cell)) for j in range(len(clean)) if j != m)
    res = dict(tag=tag, site_metal=slab["symbols"][m], site_index=m, axial=ax, n_fixed=len(slab["fixed_atom_indices"]),
               census_O_final_binding=Ost["final_binding_metal_index"], recon=site_geo(Ost["positions_A"]),
               clean_axial=float(np.linalg.norm(mic(clean[ax] - clean[m], cell))), unrecon_nearest_other=float(dn))
    # compare with deck coordinates (my own parse)
    for st, rec in (("O_unrecon", unrec), ("O_recon", Ost), ("slab", slab)):
        for projn in ("atomic", "ortho"):
            L = open(f"runs/hea/lowtail_validation_2026-09-16/{tag}/{st}__{projn}.in", encoding="utf-8").read().splitlines()
            ai = [i for i, l in enumerate(L) if l.startswith("ATOMIC_POSITIONS")][0]
            ci = [i for i, l in enumerate(L) if l.startswith("CELL_PARAMETERS")][0]
            nat = len(rec["symbols"])
            P = [[float(x) for x in L[ai + 1 + k].split()[1:4]] for k in range(nat)]
            S = [re.sub(r"\d+$", "", L[ai + 1 + k].split()[0]) for k in range(nat)]
            IF = [L[ai + 1 + k].split()[4:7] for k in range(nat)]
            fixed = [k for k in range(nat) if IF[k] == ["0", "0", "0"]]
            C = [[float(x) for x in L[ci + 1 + k].split()] for k in range(3)]
            nat_line = int(re.search(r"nat\s*=\s*(\d+)", "\n".join(L)).group(1))
            res[f"deck_{st}_{projn}"] = dict(nat_ok=nat_line == nat, pos_maxdiff=float(np.max(np.abs(np.array(P) - np.array(rec["positions_A"])))),
                                           pos_exact=P == [list(map(float, p)) for p in rec["positions_A"]],
                                           sym_ok=S == rec["symbols"], fixed_ok=fixed == sorted(rec["fixed_atom_indices"]),
                                           cell_exact=C == rec["cell_A"], partial_if=[k for k in range(nat) if IF[k] not in (["0", "0", "0"], ["1", "1", "1"])])
    for st, rec in (("O_recon", Ost), ("O_unrecon", unrec)):
        a = atoms_of(rec)
        a.calc = calc
        opt = BFGS(a, logfile=None)
        conv = opt.run(fmax=0.05, steps=300)
        E = float(a.get_potential_energy())
        res[st] = dict(E=E, steps=int(opt.nsteps), converged=bool(conv), E_minus_census_O=E - Ost["energy_eV"], **site_geo(a.get_positions()))
        a.calc = None
        del a, opt
        gc.collect()
        print(st, res[st], flush=True)
    json.dump(res, open(f"results/lowtail_dft_2026-09-16/_verify/v_mace_relax_{tag}.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("deck_")}, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k.startswith("deck_")}))
