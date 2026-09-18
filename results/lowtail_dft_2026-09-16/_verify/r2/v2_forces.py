"""Independent verifier: DFT total forces at MACE census endpoints (winner chain,
Ni31Cr29Cu5Mn35 seed 1 / site 0), site metrics, axial two-body split, MACE
re-evaluation, winner electronic adsorption energies. Written from the task text;
no track code imported."""
import hashlib, json, re, sys
from pathlib import Path
import numpy as np
from ase import Atoms
from ase.data import atomic_masses, atomic_numbers
from ase.geometry import get_distances

ROOT = Path(__file__).resolve().parents[4]
RY_EV = 13.605693122994
BOHR_A = 0.529177210903
F_CONV = RY_EV / BOHR_A

CENSUS = ROOT / "results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json"
WDIR = ROOT / "runs/hea/winner_2026-09-10"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parse_deck(path):
    txt = Path(path).read_text()
    cell = []
    lines = txt.splitlines()
    i = [k for k, l in enumerate(lines) if l.strip().startswith("CELL_PARAMETERS")][0]
    assert "angstrom" in lines[i]
    for k in range(1, 4):
        cell.append([float(x) for x in lines[i + k].split()])
    j = [k for k, l in enumerate(lines) if l.strip().startswith("ATOMIC_POSITIONS")][0]
    assert "angstrom" in lines[j]
    nat = int(re.search(r"nat\s*=\s*(\d+)", txt).group(1))
    sym, pos, ifp = [], [], []
    for l in lines[j + 1:j + 1 + nat]:
        t = l.split()
        sym.append(t[0]); pos.append([float(x) for x in t[1:4]])
        ifp.append([int(x) for x in t[4:7]] if len(t) >= 7 else [1, 1, 1])
    return sym, np.array(pos), np.array(cell), np.array(ifp)


def parse_forces(path):
    txt = Path(path).read_text(errors="replace")
    lines = txt.splitlines()
    heads = [k for k, l in enumerate(lines) if "Forces acting on atoms (cartesian axes, Ry/au)" in l]
    assert len(heads) == 1, (path, len(heads))
    F = []
    k = heads[0] + 1
    while k < len(lines):
        l = lines[k]
        m = re.match(r"\s*atom\s+(\d+)\s+type\s+\d+\s+force\s+=\s+(\S+)\s+(\S+)\s+(\S+)", l)
        if m:
            F.append([float(m.group(i)) for i in (2, 3, 4)])
        elif F and l.strip() == "":
            # blank line after the block
            if k + 1 < len(lines) and "atom" not in lines[k + 1]:
                break
        k += 1
    n_contrib = len(re.findall(r"contrib\.\s+to forces|contribution\s+to forces", txt))
    E = re.findall(r"^!\s+total energy\s+=\s+(\S+)\s+Ry", txt, re.M)
    return np.array(F) * F_CONV, float(E[-1]) * RY_EV, n_contrib


def rec_atoms(rec):
    return rec["symbols"], np.array(rec["positions_A"]), np.array(rec["cell_A"]), rec.get("fixed_atom_indices", []), rec.get("energy_eV")


def dist_vec(p1, p2, cell):
    D, d = get_distances(p1[None, :], p2[None, :], cell=cell, pbc=[True, True, True])
    return float(d[0, 0]), D[0, 0]


census = json.loads(CENSUS.read_text())
row = census["results"][0]["row"]
slab_rec = [d for d in row["decoration_records"] if d["seed"] == 1][0]["relaxed_slab"]
site_rec = [s for s in row["per_site_records"] if s["seed"] == 1 and s["site_index"] == 0][0]
geoms = {"slab": slab_rec, **{k: site_rec["relaxed_states"][k] for k in ("OH", "O", "OOH")}}
census_E = {"slab": slab_rec["energy_eV"], **{k: site_rec["relaxed_states"][k]["energy_eV"] for k in ("OH", "O", "OOH")}}

# match decks to census geometries
decks = sorted(WDIR.glob("g_*__*.run.in"))
match = {}
for dk in decks:
    sym, pos, cell, ifp = parse_deck(dk)
    for st, rec in geoms.items():
        s2, p2, c2, fixed, _ = rec_atoms(rec)
        if s2 == sym and p2.shape == pos.shape and np.array_equal(p2, pos) and np.array_equal(c2, cell):
            fixmask = np.array([[0, 0, 0] if i in set(fixed) else [1, 1, 1] for i in range(len(sym))])
            assert np.array_equal(fixmask, ifp), dk
            proj = "atomic" if "__atomic" in dk.name else "ortho"
            match[(st, proj)] = dk
print("matched", sorted(match))
assert len(match) == 8

clean_sym, clean_pos, clean_cell, _, _ = rec_atoms(slab_rec)
SITE, AX, ADS = 16, 40, 72
assert clean_sym[SITE] == "Cr" and clean_sym[AX] == "O"


def mass(sym):
    return atomic_masses[atomic_numbers[sym]]


# MACE
from mace.calculators import mace_mp
import torch
torch.set_num_threads(2)
MODEL = Path.home() / ".cache/mace/macempa0mediummodel"
calc = mace_mp(model=str(MODEL), device="cpu", default_dtype="float64")
mace = {}
for st, rec in geoms.items():
    s, p, c, fixed, _ = rec_atoms(rec)
    a = Atoms(s, positions=p, cell=c, pbc=True)
    a.calc = calc
    mace[st] = dict(E=float(a.get_potential_energy()), F=a.get_forces().copy(), fixed=set(fixed))

res = {"model_sha256": sha(MODEL), "rows": []}
for (st, proj), dk in sorted(match.items()):
    out = Path(str(dk).replace(".run.in", ".out"))
    sym, pos, cell, ifp = parse_deck(dk)
    F, E, ncontrib = parse_forces(out)
    assert F.shape == pos.shape
    free = ifp.astype(bool)
    Ffree = np.where(free, F, 0.0)
    norms = np.linalg.norm(Ffree, axis=1)
    freeatoms = [i for i in range(len(sym)) if free[i].all()]
    rank = sorted(freeatoms, key=lambda i: -norms[i]).index(SITE) + 1
    top = int(np.argmax(norms))
    Fm = mace[st]["F"]
    Fm_free = np.where(free, Fm, 0.0)
    r = dict(state=st, proj=proj, deck=str(dk.relative_to(ROOT)), out_sha=sha(out), E_eV=E, n_contrib_mentions=ncontrib,
             dft_free_fmax=float(norms.max()), top=f"{sym[top]}{top}", mace_free_fmax=float(np.linalg.norm(Fm_free, axis=1).max()),
             site_rank=rank, n_free=len(freeatoms))
    lift = pos[SITE, 2] - clean_pos[SITE, 2]
    disp3d, _ = dist_vec(pos[SITE], clean_pos[SITE], cell)
    dAX, vAX = dist_vec(pos[SITE], pos[AX], cell)
    r.update(lift=float(lift), disp3d=float(disp3d), d_axial=float(dAX), Fz_site=float(F[SITE, 2]), Fz_site_mace=float(Fm[SITE, 2]),
             Fz_ax=float(F[AX, 2]))
    uAX = vAX / dAX
    r["axial_stretch"] = float((F[AX] - F[SITE]) @ uAX)
    bonded = st != "slab"
    if bonded:
        dO, vO = dist_vec(pos[SITE], pos[ADS], cell)
        uO = vO / dO
        r.update(d_ads=float(dO), Fz_ads=float(F[ADS, 2]), bond_stretch=float((F[ADS] - F[SITE]) @ uO),
                 pair_Fz=float(F[SITE, 2] + F[ADS, 2]))
    # two-body along u (site -> axial O)
    for tag, FF in (("DFT", F), ("MACE", Fm)):
        unit = [SITE, ADS] if bonded else [SITE]
        m_unit = sum(mass(sym[i]) for i in unit)
        m_ax = mass(sym[AX])
        F_unit = sum(FF[i] for i in unit)
        ax_toward = float(-(FF[AX] @ uAX))
        unit_toward = float(F_unit @ uAX)
        site_away = float(-(FF[SITE] @ uAX))
        rel = float((FF[AX] @ uAX) / m_ax - (F_unit @ uAX) / m_unit)
        r[f"{tag}_twobody"] = dict(u_z=float(uAX[2]), unit=unit, m_unit=m_unit, ax_toward_site=ax_toward,
                                   unit_toward_ax=unit_toward, site_away_from_ax=site_away, rel_acc=rel,
                                   identity_check=float(ax_toward * 0 + (FF[AX] - FF[SITE]) @ uAX - (-ax_toward - (-site_away)) ))
    res["rows"].append(r)

res["mace_energy_minus_census"] = {st: mace[st]["E"] - census_E[st] for st in geoms}

# electronic adsorption energies (DFT) with runs/Cr_slab gas references
def gasE(p):
    t = Path(p).read_text(errors="replace")
    return float(re.findall(r"^!\s+total energy\s+=\s+(\S+)\s+Ry", t, re.M)[-1]) * 13.605693122


RY_SCORER = 13.605693122
EH2O = gasE(ROOT / "runs/Cr_slab/H2O.out"); EH2 = gasE(ROOT / "runs/Cr_slab/H2.out")
ads = {}
for proj in ("atomic", "ortho"):
    E = {}
    for st in geoms:
        out = Path(str(match[(st, proj)]).replace(".run.in", ".out"))
        t = out.read_text(errors="replace")
        E[st] = float(re.findall(r"^!\s+total energy\s+=\s+(\S+)\s+Ry", t, re.M)[-1]) * RY_SCORER
    dOH = E["OH"] - E["slab"] - (EH2O - 0.5 * EH2)
    dO = E["O"] - E["slab"] - (EH2O - EH2)
    dOOH = E["OOH"] - E["slab"] - (2 * EH2O - 1.5 * EH2)
    ads[proj] = dict(OH=dOH, O=dO, OOH=dOOH, O_minus_OH=dO - dOH, OOH_minus_O=dOOH - dO)
mE = {k: v["E"] for k, v in mace.items()}
mH2O = row["gas_reference_records"]["H2O"]["energy_eV"]; mH2 = row["gas_reference_records"]["H2"]["energy_eV"]
mOH = mE["OH"] - mE["slab"] - (mH2O - 0.5 * mH2)
mO = mE["O"] - mE["slab"] - (mH2O - mH2)
mOOH = mE["OOH"] - mE["slab"] - (2 * mH2O - 1.5 * mH2)
ads["MACE"] = dict(OH=mOH, O=mO, OOH=mOOH, O_minus_OH=mO - mOH, OOH_minus_O=mOOH - mO)
res["electronic_adsorption"] = ads
Path(__file__).with_name("v2_forces.json").write_text(json.dumps(res, indent=1))
for r in res["rows"]:
    print(r["state"], r["proj"], "fmax %.3f/%.3f top %s rank %d/%d lift %.3f disp %.3f dAX %.3f Fz_site %+.3f (MACE %+.3f) Fz_ax %+.3f axial %+.3f" % (
        r["dft_free_fmax"], r["mace_free_fmax"], r["top"], r["site_rank"], r["n_free"], r["lift"], r["disp3d"], r["d_axial"], r["Fz_site"], r["Fz_site_mace"], r["Fz_ax"], r["axial_stretch"]),
        ("dO %.3f FzO %+.3f bond %+.3f pair %+.3f" % (r["d_ads"], r["Fz_ads"], r["bond_stretch"], r["pair_Fz"])) if "d_ads" in r else "")
    for tag in ("DFT", "MACE"):
        t = r[f"{tag}_twobody"]
        print("   ", tag, "unit", t["unit"], "ax->site %+.3f unit->ax %+.3f site_away %+.3f rel %+.4f" % (t["ax_toward_site"], t["unit_toward_ax"], t["site_away_from_ax"], t["rel_acc"]))
print(json.dumps(res["mace_energy_minus_census"]))
print(json.dumps(ads, indent=1))
