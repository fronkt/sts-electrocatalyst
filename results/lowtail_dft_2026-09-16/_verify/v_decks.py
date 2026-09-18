"""Independent deck checks for lowtail (b). Uses repo src/dft/hea_deck.render_deck (not the track's code)."""
import hashlib
import json
import os
import re
import sys

import numpy as np

ROOT = r"C:\Users\frank\sts-electrocatalyst"
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "src", "dft"))
sys.path.insert(0, os.path.join(ROOT, "src"))
import hea_deck  # noqa: E402

D = "runs/hea/lowtail_validation_2026-09-16"
SITES = [("Cu8Cr23Mn35Co34__s20_site2", "results/site_census_2026-09-06/results/mpa0_ext__Cu8Cr23Mn35Co34__s18-20_result.json", 20, 2),
         ("Ni31Cr29Cu5Mn35__s1_site0", "results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json", 1, 0),
         ("Fe25Co25Ni25Cr25__s2_site0", "results/site_census_2026-09-06/results/mpa0__Fe25Co25Ni25Cr25_result.json", 2, 0)]
U = {"Cr": 3.7, "Mn": 3.9, "Fe": 5.3, "Co": 3.32, "Ni": 6.2}
FM = {"Cr": 0.6, "Mn": 0.5, "Fe": 0.5, "Co": 0.4, "Ni": 0.3, "Cu": 0.2, "O": 0.0}
res = {}
all_files = sorted(os.listdir(D))
for tag, path, seed, site in SITES:
    doc = json.load(open(path, encoding="utf-8"))
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    rows = [r for r in doc["results"] if r["status"] == "evaluated"]
    assert len(rows) == 1
    rw = rows[0]["row"]
    ps = [p for p in rw["per_site_records"] if p["seed"] == seed and p["site_index"] == site]
    decs = [d for d in rw["decoration_records"] if d["seed"] == seed]
    assert len(ps) == 1 and len(decs) == 1
    ps, slab = ps[0], decs[0]["relaxed_slab"]
    m = ps["initial_binding_metal_index"]
    O = ps["relaxed_states"]["O"]
    unrec_pos = [list(p) for p in slab["positions_A"]] + [[slab["positions_A"][m][0], slab["positions_A"][m][1], slab["positions_A"][m][2] + 1.635]]
    geoms = {"slab": (slab["symbols"], slab["positions_A"], slab["cell_A"], slab["fixed_atom_indices"]),
             "O_recon": (O["symbols"], O["positions_A"], O["cell_A"], O["fixed_atom_indices"]),
             "O_unrecon": (slab["symbols"] + ["O"], unrec_pos, slab["cell_A"], slab["fixed_atom_indices"])}
    site_res = dict(census_sha256=sha, site_metal=slab["symbols"][m], site_index=m, formula=rw["formula"],
                    O_desorbed_flag=rw.get("desorbed"), site_desorbed=ps.get("desorbed"),
                    O_final_binding=O["final_binding_metal_index"], O_converged=O["converged_by_force"],
                    slab_converged=slab["converged_by_force"], O_fixed_equal_slab=sorted(O["fixed_atom_indices"]) == sorted(slab["fixed_atom_indices"]),
                    O_cell_equal_slab=O["cell_A"] == slab["cell_A"], n_fixed=len(slab["fixed_atom_indices"]),
                    O_bonds=ps["bonds"], dG=dict(OH=ps["dG_OH"], O=ps["dG_O"], OOH=ps["dG_OOH"], eta=ps["eta"]))
    for st, (sy, pos, cell, fx) in geoms.items():
        for pj in ("atomic", "ortho"):
            fn = f"{D}/{tag}/{st}__{pj}.in"
            actual = open(fn, "rb").read()
            prefix = f"lt__{tag}__{st}__{pj}"
            exp = hea_deck.render_deck(prefix, sy, pos, cell, fx, pj)
            exp_relax = exp.replace("  calculation = 'scf'\n", "  calculation = 'relax'\n", 1)
            txt = actual.decode()
            smag = {int(i): float(v) for i, v in re.findall(r"starting_magnetization\((\d+)\)\s*=\s*([\d.]+)", txt)}
            spec_block = txt.split("ATOMIC_SPECIES\n")[1].split("CELL_PARAMETERS")[0].split("\n")
            order = [l.split()[0] for l in spec_block if l.strip()]
            fm_ok = all(abs(smag[i + 1] - FM[sp]) < 1e-12 for i, sp in enumerate(order))
            ulines = dict(re.findall(r"^U (\w+)-3d ([\d.]+)$", txt, re.M))
            u_ok = {k: float(v) for k, v in ulines.items()} == {sp: U[sp] for sp in order if sp in U}
            card = re.findall(r"^HUBBARD \(([\w-]+)\)$", txt, re.M)
            res[fn] = dict(bytes_equal_render=(actual.decode() == exp_relax), n_calc_lines=len(re.findall("calculation", txt)),
                           relax=("calculation = 'relax'" in txt), bfgs=("ion_dynamics = 'bfgs'" in txt),
                           kpts=("4 2 1 0 0 0" in txt), cut=("ecutwfc = 80.0" in txt and "ecutrho = 640.0" in txt),
                           fm_ok=fm_ok, u_ok=u_ok, card=card, forc=("forc_conv_thr = 2.0d-3" in txt), nstep=("nstep = 200" in txt),
                           cr_lf=b"\r" not in actual, md5=hashlib.md5(actual).hexdigest(),
                           diff_lines=[(a, b) for a, b in zip(exp.splitlines(), txt.splitlines()) if a != b][:4])
    res[tag] = site_res

# manifests
for mf in ("m_lowtail_validation_2026-09-16.txt", "m_lowtail_validation_projector_control_2026-09-16.txt"):
    t = open(f"{D}/{mf}", encoding="utf-8").read()
    rows = [l for l in t.splitlines() if l and not l.startswith("#")]
    md5s = {}
    for l in t.splitlines():
        mm = re.match(r"^#\s+(\S+__s\d+_site\d)\s+(\S+)\s+(\d+)\s+.*\s([0-9a-f]{32})$", l)
        if mm:
            md5s[(mm.group(1), mm.group(2))] = mm.group(4)
    md5_ok = all(hashlib.md5(open(f"{D}/{k[0]}/{k[1]}.in", "rb").read()).hexdigest() == v for k, v in md5s.items())
    res[mf] = dict(first_line=t.splitlines()[0], rows=len(rows), md5_rows=len(md5s), md5_ok=md5_ok,
                   not_licensed_grep=bool(re.search("not licensed", t, re.I)),
                   exclude=re.findall(r"^# SUBMIT WITH EXCLUDE=(.*)$", t, re.M),
                   check=hea_deck.check_manifest_text(t) if hasattr(hea_deck, "check_manifest_text") else None)
res["dir_listing"] = all_files
json.dump(res, open("results/lowtail_dft_2026-09-16/_verify/v_decks.json", "w"), indent=1, default=str)
for k, v in res.items():
    print(k, v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk not in ("dG",)})
