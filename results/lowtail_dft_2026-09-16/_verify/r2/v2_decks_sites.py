"""Independent verifier: deck contents vs census coordinates and settings of record; census Cr
minima lift/3-D displacement/axial distances; MACE BFGS from the O_unrecon deck starts."""
import hashlib, json, math, re, sys
from pathlib import Path
import numpy as np
from ase import Atoms
from ase.constraints import FixAtoms
from ase.geometry import get_distances

ROOT = Path(__file__).resolve().parents[4]
CEN = ROOT / "results/site_census_2026-09-06/results"
SITES = {
    "Cu8Cr23Mn35Co34__s20_site2": ("mpa0_ext__Cu8Cr23Mn35Co34__s18-20_result.json", 20, 2),
    "Ni31Cr29Cu5Mn35__s1_site0": ("mpa0__Ni31Cr29Cu5Mn35_result.json", 1, 0),
    "Fe25Co25Ni25Cr25__s2_site0": ("mpa0__Fe25Co25Ni25Cr25_result.json", 2, 0),
    "Cu26Ni9Cr31Co33__s5_site2": ("mpa0_ext__Cu26Ni9Cr31Co33__s03-05_result.json", 5, 2),
}
U_REC = {"Cr": 3.7, "Mn": 3.9, "Fe": 5.3, "Co": 3.32, "Ni": 6.2}


def load(fn, seed, site):
    d = json.loads((CEN / fn).read_text())
    rows = [r for r in d["results"] if r.get("status") == "evaluated"]
    for r in rows:
        row = r["row"]
        slabs = [x for x in row["decoration_records"] if x["seed"] == seed]
        ps = [x for x in row["per_site_records"] if x["seed"] == seed and x["site_index"] == site]
        if slabs and ps:
            return slabs[0]["relaxed_slab"], ps[0], hashlib.sha256((CEN / fn).read_bytes()).hexdigest()
    raise KeyError((fn, seed, site))


def dist(a, b, cell):
    D, d = get_distances(np.array([a]), np.array([b]), cell=cell, pbc=True)
    return float(d[0, 0]), D[0, 0]


def parse_deck(p):
    t = p.read_text()
    lines = t.splitlines()
    nat = int(re.search(r"nat\s*=\s*(\d+)", t).group(1))
    j = [k for k, l in enumerate(lines) if l.startswith("ATOMIC_POSITIONS")][0]
    sym = [l.split()[0] for l in lines[j + 1:j + 1 + nat]]
    pos = np.array([[float(x) for x in l.split()[1:4]] for l in lines[j + 1:j + 1 + nat]])
    ifp = np.array([[int(x) for x in l.split()[4:7]] for l in lines[j + 1:j + 1 + nat]])
    i = [k for k, l in enumerate(lines) if l.startswith("CELL_PARAMETERS")][0]
    cell = np.array([[float(x) for x in lines[i + k].split()] for k in (1, 2, 3)])
    hub = re.findall(r"^U (\w+)-3d ([\d.]+)", t, re.M)
    hubhead = re.search(r"^HUBBARD \(([\w-]+)\)", t, re.M).group(1)
    kp = lines[[k for k, l in enumerate(lines) if l.startswith("K_POINTS")][0] + 1].split()
    s = dict(calc=re.search(r"calculation = '(\w+)'", t).group(1), ion=re.search(r"ion_dynamics = '(\w+)'", t).group(1),
             forc=re.search(r"forc_conv_thr = (\S+)", t).group(1), nstep=re.search(r"nstep = (\d+)", t).group(1),
             ecutwfc=re.search(r"ecutwfc = (\S+)", t).group(1), ecutrho=re.search(r"ecutrho = (\S+)", t).group(1),
             degauss=re.search(r"degauss = (\S+)", t).group(1), conv_thr=re.search(r"conv_thr = (\S+)", t).group(1),
             maxstep=re.search(r"electron_maxstep = (\d+)", t).group(1), mixing=re.search(r"mixing_mode = '(\S+)'", t).group(1),
             beta=re.search(r"mixing_beta = (\S+)", t).group(1), nspin=re.search(r"nspin = (\d)", t).group(1),
             hub=dict((a, float(b)) for a, b in hub), hubhead=hubhead, kpts=kp, max_seconds=re.search(r"max_seconds = (\d+)", t).group(1))
    return sym, pos, ifp, cell, s


out = dict(sites={}, decks={}, minima={})
for tag, (fn, seed, site) in SITES.items():
    slab, ps, h = load(fn, seed, site)
    Os = ps["relaxed_states"]["O"]
    cs, cp, cc = slab["symbols"], np.array(slab["positions_A"]), np.array(slab["cell_A"])
    os_, op = Os["symbols"], np.array(Os["positions_A"])
    si = ps["initial_binding_metal_index"]
    assert cs[si] == "Cr", tag
    # axial O: O in clean slab nearest to site Cr and below it
    cand = [(dist(cp[si], cp[i], cc)[0], i) for i in range(len(cs)) if cs[i] == "O" and cp[i, 2] < cp[si, 2]]
    ax = min(cand)[1]
    ads = len(cs)
    lift = op[si, 2] - cp[si, 2]
    disp = dist(op[si], cp[si], cc)[0]
    rec = dict(census_sha=h, site_index=si, axial=ax, clean_axial=min(cand)[0], O_axial=dist(op[si], op[ax], cc)[0],
               lift=lift, disp3d=disp, CrO=dist(op[si], op[ads], cc)[0], O_state_binding=Os.get("final_binding_metal_index"))
    out["minima"][tag] = rec
    if tag.startswith("Cu26"):
        continue
    fixed = set(slab["fixed_atom_indices"])
    for state in ("slab", "O_recon", "O_unrecon"):
        for proj in ("atomic", "ortho"):
            p = ROOT / "runs/hea/lowtail_validation_2026-09-16" / tag / f"{state}__{proj}.in"
            sym, pos, ifp, cell, s = parse_deck(p)
            if state == "slab":
                ref_s, ref_p = cs, cp
            elif state == "O_recon":
                ref_s, ref_p = os_, op
            else:
                ref_s = cs + ["O"]
                ref_p = np.vstack([cp, cp[si] + np.array([0, 0, 1.635])])
            mask = np.array([[0, 0, 0] if i in fixed else [1, 1, 1] for i in range(len(sym))])
            elems = sorted(set(sym) - {"O", "Cu"})
            chk = dict(md5=hashlib.md5(p.read_bytes()).hexdigest(), symbols=sym == ref_s, pos_max_abs=float(np.abs(pos - ref_p).max()),
                       cell=bool(np.array_equal(cell, cc)), ifpos=bool(np.array_equal(ifp, mask)),
                       U_ok=s["hub"] == {e: U_REC[e] for e in elems}, no_Cu_U="Cu" not in s["hub"],
                       hubhead=s["hubhead"], proj_ok=(s["hubhead"] == "atomic") == (proj == "atomic"), settings=s)
            if state == "O_unrecon":
                chk["O_height"] = float(pos[-1, 2] - pos[si, 2])
                chk["nearest_other"] = min(dist(pos[-1], pos[i], cell)[0] for i in range(len(sym) - 1) if i != si)
            out["decks"][f"{tag}/{state}__{proj}"] = chk
lifts = {k: v["clean_axial"] for k, v in out["minima"].items()}
out["axial_break"] = (max(v["clean_axial"] for v in out["minima"].values()) + min(v["O_axial"] for v in out["minima"].values())) / 2

# MACE from the O_unrecon starts (census protocol: BFGS fmax 0.05, 300 steps, FixAtoms)
if "--mace" in sys.argv:
    from mace.calculators import mace_mp
    from ase.optimize import BFGS
    import torch
    torch.set_num_threads(2)
    calc = mace_mp(model=str(Path.home() / ".cache/mace/macempa0mediummodel"), device="cpu", default_dtype="float64")
    out["mace"] = {}
    for tag in list(SITES)[:3]:
        fn, seed, site = SITES[tag]
        slab, ps, _ = load(fn, seed, site)
        sym, pos, ifp, cell, s = parse_deck(ROOT / "runs/hea/lowtail_validation_2026-09-16" / tag / "O_unrecon__atomic.in")
        a = Atoms(sym, positions=pos, cell=cell, pbc=True)
        a.set_constraint(FixAtoms(indices=slab["fixed_atom_indices"]))
        a.calc = calc
        opt = BFGS(a, logfile=None)
        opt.run(fmax=0.05, steps=300)
        cp = np.array(slab["positions_A"]); cc = np.array(slab["cell_A"])
        si = ps["initial_binding_metal_index"]; ax = out["minima"][tag]["axial"]
        E = float(a.get_potential_energy())
        p = a.get_positions()
        out["mace"][tag] = dict(steps=opt.get_number_of_steps(), E_minus_census_O=E - ps["relaxed_states"]["O"]["energy_eV"],
                                lift=float(p[si, 2] - cp[si, 2]), axial=dist(p[si], p[ax], cc)[0], CrO=dist(p[si], p[-1], cc)[0])
        print(tag, out["mace"][tag], flush=True)
        del a, opt

Path(__file__).with_name("v2_decks_sites.json").write_text(json.dumps(out, indent=1, default=str))
for k, v in out["minima"].items():
    print(k, {x: (round(y, 4) if isinstance(y, float) else y) for x, y in v.items() if x != "census_sha"})
print("axial_break", out["axial_break"])
for k, v in out["decks"].items():
    print(k, v["md5"], v["symbols"], v["pos_max_abs"], v["cell"], v["ifpos"], v["U_ok"], v["no_Cu_U"], v["hubhead"], v["proj_ok"],
          v["settings"]["calc"], v["settings"]["ion"], v["settings"]["forc"], v["settings"]["nstep"], v["settings"]["kpts"], v["settings"]["ecutwfc"], v["settings"]["ecutrho"], v["settings"]["maxstep"], v.get("O_height"), v.get("nearest_other"))
