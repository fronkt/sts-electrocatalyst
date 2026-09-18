"""(a) Zero-compute DFT vs MACE-MPA-0 at identical coordinates on banked HEA single points.

Population: every banked pw.x output under runs/hea (lt_sources.registry). An output is
used only when its own readout ACCEPTED it, its bytes match the recorded hash, this
module's strict parser reads exactly one converged SCF and one complete total-force block,
and its input coordinates, cell, species and constraints equal a retained MACE endpoint.

Geometries (all MACE-MPA-0 float64 endpoints, retained coordinates):
  * Ni31Cr29Cu5Mn35 seed 1 / site 0 (census-selected historical winner): clean slab, OH, O,
    OOH from results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json;
  * Ni31Cr29Cu5Mn35 seed 0 / site 0 OOH: the census-selected pull2.10 endpoint and the
    builder-start endpoint of the same multistart, from
    results/cr_site_chains_2026-09-06/leader_ooh_replay.json (the replay reproduces the census
    start energies; both checks are recorded);
  * final retained Fe25Co25Ni25Cr25 seed 2/site 0 and Ni31Cr29Cu5Mn35 seed 0/site 0
    clean/OH/O states, the equiatomic OOH endpoint and leader pull1.70 endpoint;
  * the census gas references H2O and H2 (12 A box).
MACE is evaluated at those coordinates with the census checkpoint (sha256 checked),
or reused from a prior hashed record whose checkpoint, source geometry and evaluator agree.

Usage: python src/s2/lowtail_dft/lt_zero_compute.py [--out results/lowtail_dft_2026-09-18/zero_compute]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lt_geometry as geo  # noqa: E402
import lt_qe as qe  # noqa: E402
import lt_sources as src  # noqa: E402
from lt_common import ROOT, RY_TO_EV, evidence, read_json, rel, sha256_file, write_json  # noqa: E402

CENSUS_NI31 = ROOT / "results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json"
CENSUS_FE25 = ROOT / "results/site_census_2026-09-06/results/mpa0__Fe25Co25Ni25Cr25_result.json"
REPLAY = ROOT / "results/cr_site_chains_2026-09-06/leader_ooh_replay.json"
DFT_GAS = {"H2O": ROOT / "runs/Cr_slab/H2O.out", "H2": ROOT / "runs/Cr_slab/H2.out"}
REF_COEFFS_SOURCE = ROOT / "src/hea_oer/referencing.py"
DESORBED_SOURCE = ROOT / "src/hea_oer/data.py"
OUT = ROOT / "results/lowtail_dft_2026-09-18/zero_compute"
MATCH_TOL_A = 1e-8


def ref_coefficients() -> dict:
    """Stoichiometric H2O/H2 coefficients, parsed from src/hea_oer/referencing.py (_REF_COEFFS)."""
    import re
    text = REF_COEFFS_SOURCE.read_text(encoding="utf-8")
    m = re.search(r"_REF_COEFFS\s*=\s*\{([^}]*)\}", text)
    pairs = re.findall(r'"(\w+)":\s*\(([-\d.]+),\s*([-\d.]+)\)', m.group(1))
    return {k: (float(a), float(b)) for k, a, b in pairs}


def desorbed_min_A() -> float:
    import re
    m = re.search(r"^M_O_DESORBED_MIN\s*=\s*([\d.]+)", DESORBED_SOURCE.read_text(encoding="utf-8"), re.M)
    return float(m.group(1))


def _geom(record, **extra):
    g = dict(symbols=list(record["symbols"]), positions=[list(map(float, p)) for p in record["positions_A"]],
             cell=[list(map(float, r)) for r in record["cell_A"]], pbc=list(record["pbc"]),
             fixed=sorted(int(i) for i in record.get("fixed_atom_indices", [])),
             stored_energy_eV=float(record["energy_eV"]))
    g.update(extra)
    return g


def geometries() -> tuple[dict, dict]:
    winner = src.census_site(CENSUS_NI31, 1, 0)
    leader = src.census_site(CENSUS_NI31, 0, 0)
    replay = read_json(REPLAY)
    checks = {}
    geoms = {}
    wsite = winner["site"]
    site_w = int(wsite["initial_binding_metal_index"])
    clean_w = winner["slab"]["positions_A"]
    geoms["winner_slab"] = _geom(winner["slab"], chain="winner", state="slab", site_index=site_w, ads_o=None,
                                 clean_positions=clean_w,
                                 source=dict(file=rel(CENSUS_NI31), pointer="results[0].row.decoration_records[seed=1].relaxed_slab"))
    for st in ("OH", "O", "OOH"):
        rec = wsite["relaxed_states"][st]
        geoms[f"winner_{st}"] = _geom(rec, chain="winner", state=st, site_index=site_w, ads_o=len(clean_w),
                                      clean_positions=clean_w, census_final_binding_metal_index=rec["final_binding_metal_index"],
                                      source=dict(file=rel(CENSUS_NI31), pointer=f"results[0].row.per_site_records[seed=1,site=0].relaxed_states.{st}"))
    lsite = leader["site"]
    site_l = int(lsite["initial_binding_metal_index"])
    clean_l = leader["slab"]["positions_A"]
    attempts = {a["start"]: a for a in replay["attempts"]}
    for start in ("builder", "pull2.10", "pull1.70"):
        rec = attempts[start]["geometry"]
        geoms[f"leader_OOH_{start}"] = _geom(rec, chain="leader", state=f"OOH_{start}", site_index=site_l, ads_o=len(clean_l),
                                             clean_positions=clean_l,
                                             source=dict(file=rel(REPLAY), pointer=f"attempts[start={start}].geometry"))
    census_ooh = lsite["relaxed_states"]["OOH"]
    pull = geoms["leader_OOH_pull2.10"]
    checks["leader_pull2.10_equals_census_selected_OOH"] = bool(
        pull["positions"] == census_ooh["positions_A"] and pull["symbols"] == census_ooh["symbols"]
        and pull["cell"] == census_ooh["cell_A"] and pull["fixed"] == sorted(census_ooh["fixed_atom_indices"]))
    census_starts = {r["start"]: r["energy_eV"] for r in lsite["start_records"]["OOH"]}
    checks["leader_start_energy_replay_minus_census_eV"] = {
        s: attempts[s]["energy_eV"] - census_starts[s] for s in ("builder", "pull2.10")}
    checks["replay_model_sha256_equals_census"] = replay["model"]["sha256_bytes"] == winner["model"]["sha256_bytes"]
    # The final panel/pilot contributes two additional reconstructed Cr sites.
    # Their clean/OH/O states and the equiatomic retained OOH are census endpoints;
    # the leader's retained OOH already has the replay key above.
    for chain, path, seed in (("equiatomic", CENSUS_FE25, 2), ("leader", CENSUS_NI31, 0)):
        c = src.census_site(path, seed, 0)
        if c["model"]["sha256_bytes"] != winner["model"]["sha256_bytes"]:
            raise ValueError(f"{chain}: census checkpoint differs from the winner checkpoint")
        clean = c["slab"]["positions_A"]
        site_index = int(c["site"]["initial_binding_metal_index"])
        for state in (("slab", "OH", "O", "OOH") if chain == "equiatomic" else ("slab", "OH", "O")):
            record = c["slab"] if state == "slab" else c["site"]["relaxed_states"][state]
            pointer = (f"results[0].row.decoration_records[seed={seed}].relaxed_slab" if state == "slab" else
                       f"results[0].row.per_site_records[seed={seed},site=0].relaxed_states.{state}")
            geoms[f"{chain}_{state}"] = _geom(record, chain=chain, state=state, site_index=site_index,
                                              ads_o=None if state == "slab" else len(clean), clean_positions=clean,
                                              source=dict(file=rel(path), pointer=pointer))
    for name in ("H2O", "H2"):
        rec = winner["gas"][name]
        geoms[f"gas_{name}"] = _geom(rec, chain="gas", state=name, site_index=None, ads_o=None, clean_positions=None,
                                     source=dict(file=rel(CENSUS_NI31), pointer=f"results[0].row.gas_reference_records.{name}"))
    return geoms, dict(checks=checks, model=winner["model"], census_environment=winner["environment"])


def match_geometry(parsed_input: dict, geoms: dict):
    best = None
    for name, g in geoms.items():
        if parsed_input["elements"] != g["symbols"] or len(g["positions"]) != parsed_input["nat"]:
            continue
        dpos = float(np.max(np.abs(np.array(parsed_input["positions"]) - np.array(g["positions"]))))
        dcell = float(np.max(np.abs(np.array(parsed_input["cell"]) - np.array(g["cell"]))))
        if parsed_input["fixed"] != g["fixed"]:
            continue
        exact = parsed_input["positions"] == g["positions"] and parsed_input["cell"] == g["cell"]
        if max(dpos, dcell) <= MATCH_TOL_A and (best is None or max(dpos, dcell) < best[1]):
            best = (name, max(dpos, dcell), exact)
    return best


def dft_gas() -> dict:
    winner = read_json(src.READOUTS["winner"])
    out = {}
    for name, path in DFT_GAS.items():
        text = qe.read_text(path)
        nat = qe.header_numbers(text)["nat"]
        relax = qe.parse_relax(text, nat)
        recorded = winner["gas_references"][name]
        reasons = []
        if recorded["status"] != "COMPATIBLE_EXISTING_REFERENCE" or recorded["qc"]["verdict"] != "TRUSTWORTHY":
            reasons.append("winner readout did not accept this gas reference")
        if sha256_file(path) != recorded["files"]["output"]["sha256_bytes"]:
            reasons.append("gas output bytes differ from the winner readout record")
        if not relax["bfgs_converged"] or relax["scf_failures"] or relax["job_done"] != 1 or relax["final_energy_Ry"] is None:
            reasons.append("relaxation not cleanly converged under this parser")
        out[name] = dict(evidence=evidence(path), status="ACCEPTED" if not reasons else "REJECTED", reasons=reasons,
                         energy_Ry=relax["final_energy_Ry"], energy_eV=relax["final_energy_Ry"] * RY_TO_EV,
                         winner_readout_energy_eV=recorded["energy_eV"])
    return out


def site_block(g: dict, forces: np.ndarray, desorbed_cut: float) -> dict | None:
    """Site metal, appended O (if any) and axial lattice O: geometry and force projections."""
    if g.get("site_index") is None:
        return None
    pos = g["positions"]
    site = g["site_index"]
    axial = geo.axial_oxygen(g["symbols"], g["clean_positions"], site, g["cell"], len(g["clean_positions"]))
    block = dict(site_index=site, site_symbol=g["symbols"][site],
                 axial_O=dict(index=axial["index"], clean_distance_A=axial["clean_distance_A"],
                              distance_A=geo.distance(pos, site, axial["index"], g["cell"])),
                 axial=geo.axial_forces(forces, pos, g["cell"], site, axial["index"]))
    ads = g.get("ads_o")
    bound = False
    if ads is not None:
        nearest, dmin = geo.nearest(g["symbols"], pos, ads, g["cell"], want=lambda s: s not in ("O", "H"))
        bound = bool(nearest == site and dmin < desorbed_cut)
        block.update(adsorbate_O_index=ads,
                     adsO_nearest_metal=dict(index=nearest, symbol=g["symbols"][nearest], distance_A=dmin),
                     adsO_bound_to_site=bound,
                     geometry=geo.site_geometry(g["symbols"], pos, g["cell"], site, ads, g["clean_positions"], axial["index"]),
                     pair=geo.pair_forces(forces, pos, g["cell"], site, ads))
    # the appended O joins the site unit only when it is bonded to the site metal
    block["axial_two_body"] = geo.axial_decomposition(forces, pos, g["symbols"], g["cell"], site, axial["index"],
                                                      ads_o=ads if bound else None)
    return block


PENDING_CHAINS = (
    ("Fe25Co25Ni25Cr25__s2_site0", "results/site_census_2026-09-06/results/mpa0__Fe25Co25Ni25Cr25_result.json", 2, 0),
    ("Ni31Cr29Cu5Mn35__s0_site0", "results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json", 0, 0),
)
RESEARCH_PILOT_MANIFEST = ROOT / "runs/m_research_2026-09-16_hea_pilot.txt"


def pending_endpoint_decks() -> list:
    """Retained pilot O-state decks, with terminal acceptance from the final readout."""
    rows = []
    by_output = {e["output"]: e for e in src.final_entries()}
    manifest = RESEARCH_PILOT_MANIFEST.read_text(encoding="utf-8").splitlines()
    for tag, census, seed, site in PENDING_CHAINS:
        c = src.census_site(ROOT / census, seed, site)
        O = c["site"]["relaxed_states"]["O"]
        s = int(c["site"]["initial_binding_metal_index"])
        lift = float(geo.mic(np.array(O["positions_A"][s]) - np.array(c["slab"]["positions_A"][s]), O["cell_A"])[2])
        for proj in ("atomic", "ortho"):
            deck = ROOT / "runs/hea/pilot_retained" / tag / f"O__{proj}.in"
            parsed = qe.parse_input(qe.read_text(deck))
            equal = (parsed["positions"] == O["positions_A"] and parsed["elements"] == O["symbols"]
                     and parsed["cell"] == O["cell_A"] and parsed["fixed"] == sorted(O["fixed_atom_indices"]))
            row_text = f"hea/pilot_retained/{tag} O__{proj} .in 8"
            out = deck.with_suffix(".out")
            final = by_output.get(rel(out))
            rows.append(dict(deck=evidence(deck), census=rel(ROOT / census), seed=seed, site=site, site_index=s,
                             site_symbol=O["symbols"][s], census_site_lift_z_A=lift,
                             coordinates_equal_census_O_endpoint=bool(equal),
                             in_approved_manifest=row_text in manifest, approved_manifest=rel(RESEARCH_PILOT_MANIFEST),
                             local_output_present=out.exists(),
                             status=final["status"] if final else "UNIDENTIFIED",
                             readout_status=final["readout_status"] if final else None,
                             readout=final["readout"] if final else None,
                             output=evidence(out) if out.exists() else None,
                             reasons=final["reasons"] if final else ["output has no final readout entry"]))
    return rows


def force_summary(forces: np.ndarray, if_pos, symbols, positions, top: int = 5) -> dict:
    f = np.asarray(forces)
    mask = np.asarray(if_pos, dtype=float)
    free_norm = np.linalg.norm(f * mask, axis=1)
    order = [int(i) for i in np.argsort(-free_norm, kind="stable")[:top]]
    return dict(fmax_free_eV_A=float(free_norm.max()), fmax_all_eV_A=float(np.linalg.norm(f, axis=1).max()),
                top_free_atoms=[dict(index=i, symbol=symbols[i], z_A=float(positions[i][2]), norm_eV_A=float(free_norm[i]))
                                for i in order])


def _record_at_source(source: dict) -> dict:
    """Resolve the explicit source pointers used by this track, including gas references."""
    doc = read_json(ROOT / source["file"])
    pointer = source["pointer"]
    match = re.fullmatch(r"attempts\[start=(.+)\]\.geometry", pointer)
    if match:
        hits = [a["geometry"] for a in doc["attempts"] if a["start"] == match.group(1)]
    else:
        row = doc["results"][0]["row"]
        slab = re.fullmatch(r"results\[0\]\.row\.decoration_records\[seed=(\d+)\]\.relaxed_slab", pointer)
        state = re.fullmatch(r"results\[0\]\.row\.per_site_records\[seed=(\d+),site=(\d+)\]\.relaxed_states\.(\w+)", pointer)
        gas = re.fullmatch(r"results\[0\]\.row\.gas_reference_records\.(\w+)", pointer)
        if slab:
            hits = [d["relaxed_slab"] for d in row["decoration_records"] if d["seed"] == int(slab.group(1))]
        elif state:
            hits = [s["relaxed_states"][state.group(3)] for s in row["per_site_records"]
                    if s["seed"] == int(state.group(1)) and s["site_index"] == int(state.group(2))]
        elif gas:
            hits = [row["gas_reference_records"][gas.group(1)]]
        else:
            raise ValueError(f"unsupported MACE geometry source pointer: {pointer}")
    if len(hits) != 1:
        raise ValueError(f"MACE geometry source pointer is not unique: {pointer}")
    return hits[0]


def reusable_mace(path: Path, geoms: dict, census_sha: str) -> tuple[dict, dict]:
    """Reuse only float64 results with the same checkpoint and unchanged geometry sources.

    The Sept16 record predates geometry fingerprints. Its input manifest hashes the
    source files and the single-point implementation; the exact source pointer,
    atom count, constraints and stored energy must also match the current geometry.
    """
    path = Path(path)
    old = read_json(path)
    manifest_path = path.parent / "input_manifest.json"
    if sha256_file(manifest_path) != old["manifest_sha256"]:
        raise ValueError("MACE reuse input manifest hash differs from its readout")
    manifest = read_json(manifest_path)
    if old.get("mace_dtype") != "float64" or old["mace_checkpoint"].get("sha256") != census_sha:
        raise ValueError("MACE reuse requires the same float64 census checkpoint")
    hashes = {item["path"]: item["sha256"] for item in manifest["inputs"] + manifest["implementation"]}
    mace_path = HERE / "lt_mace.py"
    if hashes.get(rel(mace_path)) != sha256_file(mace_path):
        raise ValueError("MACE single-point implementation differs from the reuse record")
    reused = {}
    for name, g in geoms.items():
        if name not in old["mace_geometries"]:
            continue
        source = dict(source=g["source"], chain=g["chain"], state=g["state"], nat=len(g["symbols"]), n_fixed=len(g["fixed"]))
        if source != old["geometry_sources"].get(name):
            raise ValueError(f"{name}: MACE reuse geometry source metadata changed")
        source_path = ROOT / g["source"]["file"]
        if hashes.get(rel(source_path)) != sha256_file(source_path):
            raise ValueError(f"{name}: MACE reuse geometry source bytes changed")
        source_geometry = _geom(_record_at_source(g["source"]))
        if any(g[k] != value for k, value in source_geometry.items()):
            raise ValueError(f"{name}: MACE reuse coordinates differ from the hashed source record")
        m = old["mace_geometries"][name]
        forces = np.asarray(m["forces_eV_A"], dtype=float)
        mask = [[0, 0, 0] if i in g["fixed"] else [1, 1, 1] for i in range(len(g["symbols"]))]
        if (forces.shape != (len(g["symbols"]), 3) or not np.all(np.isfinite(forces))
                or not np.isfinite(m["energy_eV"]) or m["stored_energy_eV"] != g["stored_energy_eV"]
                or m["if_pos"] != mask):
            raise ValueError(f"{name}: malformed or mismatched MACE reuse evaluation")
        reused[name] = dict(energy_eV=m["energy_eV"], forces_eV_A=forces)
    return reused, dict(readout=evidence(path), input_manifest=evidence(manifest_path), geometries=sorted(reused))


def run(out_dir: Path, checkpoint: Path, threads: int = 2, calc=None, reuse_mace: Path | None = None) -> dict:
    import lt_mace

    geoms, geom_checks = geometries()
    reg = src.registry()
    desorbed_cut = desorbed_min_A()
    coeffs = ref_coefficients()

    # ---- DFT realizations
    realizations, excluded = [], []
    for e in reg["entries"]:
        if e["status"] != "ACCEPTED":
            excluded.append(dict(job=e["job"], output=e["output"], status=e["status"], reasons=e["reasons"], readout=e["readout"]))
            continue
        in_path, out_path = ROOT / e["input"], ROOT / e["output"]
        parsed = qe.parse_input(qe.read_text(in_path))
        if parsed["calculation"] != "scf":
            excluded.append(dict(job=e["job"], status="EXCLUDED", reasons=["input is not a fixed-geometry scf"]))
            continue
        match = match_geometry(parsed, geoms)
        if match is None:
            excluded.append(dict(job=e["job"], output=e["output"], status="EXCLUDED",
                                 reasons=["input coordinates do not equal a retained MACE endpoint"]))
            continue
        scf = qe.parse_scf(qe.read_text(out_path), parsed["nat"])
        if scf["status"] != "VALID_SCF":
            excluded.append(dict(job=e["job"], output=e["output"], status="EXCLUDED",
                                 reasons=["accepted by its readout but not by this strict parser: " + "; ".join(scf["reasons"])]))
            continue
        p = parsed["params"]
        realizations.append(dict(
            job=e["job"], geometry=match[0], coordinate_match=dict(exact=match[2], max_abs_difference_A=match[1]),
            projector=e.get("projector"), variant=e.get("variant"), series=e.get("series", "g"),
            readout=e["readout"], input=evidence(in_path), output=evidence(out_path),
            settings=dict(ecutwfc_Ry=p["ecutwfc"], ecutrho_Ry=p["ecutrho"], degauss_Ry=p["degauss"],
                          conv_thr_Ry=p["conv_thr"], hubbard_card=parsed["hubbard_card"],
                          startingwfc=p["startingwfc"], startingpot=p["startingpot"]),
            record_settings=bool(p["ecutwfc"] == 80.0 and p["ecutrho"] == 640.0 and p["degauss"] == 0.01),
            if_pos=parsed["if_pos"], energy_eV=scf["energy_eV"], iterations=scf["iterations"],
            total_magnetization_muB=scf["total_muB"], absolute_magnetization_muB=scf["absolute_muB"],
            n_contribution_blocks=scf["n_contribution_blocks"], forces_eV_A=scf["forces_eV_A"],
            pair_partner=e.get("pair_partner")))

    # ---- MACE, one geometry at a time
    census_sha = geom_checks["model"]["sha256_bytes"]
    injected_calculator = calc is not None
    if not injected_calculator:
        checkpoint_evidence = dict(path=str(checkpoint), sha256=sha256_file(checkpoint), census_sha256=census_sha)
        if checkpoint_evidence["sha256"] != census_sha:
            raise ValueError("checkpoint bytes differ from the census record")
    else:
        checkpoint_evidence = dict(path="injected calculator (test)", sha256=None, census_sha256=census_sha)
    reused, reuse_evidence = reusable_mace(reuse_mace, geoms, census_sha) if reuse_mace is not None else ({}, None)
    mace = {}
    for name in geoms:
        g = geoms[name]
        if name in reused:
            r = reused[name]
        else:
            if calc is None:
                calc = lt_mace.load_calculator(checkpoint, census_sha, threads)
            r = lt_mace.single_point(calc, g["symbols"], g["positions"], g["cell"], g["pbc"])
        mask = np.ones((len(g["symbols"]), 3), dtype=int)
        for i in g["fixed"]:
            mask[i] = 0
        mace[name] = dict(energy_eV=r["energy_eV"], stored_energy_eV=g["stored_energy_eV"],
                          energy_minus_stored_eV=r["energy_eV"] - g["stored_energy_eV"],
                          forces_eV_A=r["forces_eV_A"], if_pos=mask.tolist(),
                          **force_summary(r["forces_eV_A"], mask, g["symbols"], g["positions"]))

    # ---- per realization comparison
    rows = []
    for rz in realizations:
        g = geoms[rz["geometry"]]
        m = mace[rz["geometry"]]
        fd = rz["forces_eV_A"]
        row = dict({k: v for k, v in rz.items() if k not in ("forces_eV_A", "if_pos")})
        row["DFT"] = force_summary(fd, rz["if_pos"], g["symbols"], g["positions"])
        row["MACE"] = dict(fmax_free_eV_A=m["fmax_free_eV_A"], fmax_all_eV_A=m["fmax_all_eV_A"])
        row["agreement_free"] = geo.force_agreement(fd, m["forces_eV_A"], rz["if_pos"])
        dsite = site_block(g, fd, desorbed_cut)
        msite = site_block(g, m["forces_eV_A"], desorbed_cut)
        if dsite is not None:
            free_norms = np.linalg.norm(np.asarray(fd) * np.asarray(rz["if_pos"]), axis=1)
            row["site"] = dict({k: v for k, v in dsite.items() if k not in ("axial", "pair", "axial_two_body")},
                               DFT=dict(dsite["axial"], **dsite.get("pair", {})),
                               MACE=dict(msite["axial"], **msite.get("pair", {})),
                               DFT_axial_two_body=dsite["axial_two_body"], MACE_axial_two_body=msite["axial_two_body"],
                               site_rank_by_DFT_free_force=int(np.sum(free_norms > free_norms[dsite["site_index"]]) + 1))
        row["DFT_forces_eV_A"] = np.asarray(fd).tolist()
        rows.append(row)

    # ---- energies: winner chain electronic adsorption energies per realization projector
    gas_dft = dft_gas()
    gas_mace = {k: mace[f"gas_{k}"]["energy_eV"] for k in ("H2O", "H2")}
    by_key = {}
    for rz in realizations:
        by_key[(rz["geometry"], rz["projector"], rz["series"], rz["variant"])] = rz
    chain = []
    gas_ok = all(v["status"] == "ACCEPTED" for v in gas_dft.values())
    for proj in ("atomic", "ortho"):
        E = {st: by_key.get((f"winner_{st}", proj, "g", "baseline")) for st in ("slab", "OH", "O", "OOH")}
        if not gas_ok or any(v is None for v in E.values()):
            chain.append(dict(projector=proj, status="NOT AVAILABLE",
                              reasons=["gas reference rejected" if not gas_ok else "missing accepted state"]))
            continue
        ads = {}
        for st in ("OH", "O", "OOH"):
            a, b = coeffs[st]
            d_dft = E[st]["energy_eV"] - E["slab"]["energy_eV"] - (a * gas_dft["H2O"]["energy_eV"] + b * gas_dft["H2"]["energy_eV"])
            d_mace = mace[f"winner_{st}"]["energy_eV"] - mace["winner_slab"]["energy_eV"] - (a * gas_mace["H2O"] + b * gas_mace["H2"])
            ads[st] = dict(DFT_eV=d_dft, MACE_eV=d_mace, DFT_minus_MACE_eV=d_dft - d_mace)
        steps = {}
        for lo, hi in (("OH", "O"), ("O", "OOH")):
            d = ads[hi]["DFT_eV"] - ads[lo]["DFT_eV"]
            mm = ads[hi]["MACE_eV"] - ads[lo]["MACE_eV"]
            steps[f"{hi}_minus_{lo}"] = dict(DFT_eV=d, MACE_eV=mm, DFT_minus_MACE_eV=d - mm)
        banked = read_json(src.READOUTS["winner"])["electronic_chains"]["electronic_adsorption_eV"][proj]
        for st in ads:
            ads[st]["winner_readout_DFT_eV"] = banked[st]
            ads[st]["DFT_minus_winner_readout_eV"] = ads[st]["DFT_eV"] - banked[st]
        chain.append(dict(projector=proj, status="COMPUTED", electronic_adsorption=ads, consecutive_differences=steps,
                          jobs={st: E[st]["job"] for st in E}))

    # ---- energies: leader OOH endpoint pairs
    pairs = []
    dE_mace = mace["leader_OOH_pull2.10"]["energy_eV"] - mace["leader_OOH_builder"]["energy_eV"]
    leader = [rz for rz in realizations if rz["geometry"] in ("leader_OOH_builder", "leader_OOH_pull2.10")]
    keyed = {}
    for rz in leader:
        keyed.setdefault((rz["series"], rz["projector"], rz["variant"]), {})[rz["geometry"]] = rz
    for key in sorted(keyed):
        pair = keyed[key]
        if set(pair) == {"leader_OOH_builder", "leader_OOH_pull2.10"}:
            b, p = pair["leader_OOH_builder"], pair["leader_OOH_pull2.10"]
            pairs.append(dict(series=key[0], projector=key[1], variant=key[2], builder=b["job"], pull2_10=p["job"],
                              record_settings=b["record_settings"] and p["record_settings"],
                              dE_DFT_eV=p["energy_eV"] - b["energy_eV"], dE_MACE_eV=dE_mace,
                              DFT_minus_MACE_eV=p["energy_eV"] - b["energy_eV"] - dE_mace, pairing="same series/projector/variant"))
    for rz in leader:
        if rz.get("pair_partner"):
            partner = [x for x in leader if x["job"] == rz["pair_partner"]]
            if len(partner) == 1:
                b, p = (rz, partner[0]) if rz["geometry"].endswith("builder") else (partner[0], rz)
                pairs.append(dict(series="hd+hn", projector=rz["projector"], variant="ieee_repro builder + tight pull",
                                  builder=b["job"], pull2_10=p["job"], record_settings=b["record_settings"] and p["record_settings"],
                                  dE_DFT_eV=p["energy_eV"] - b["energy_eV"], dE_MACE_eV=dE_mace,
                                  DFT_minus_MACE_eV=p["energy_eV"] - b["energy_eV"] - dE_mace,
                                  pairing=f"replacement pair named by {rel(src.READOUTS['replacement'])}"))
    unpaired = sorted({rz["job"] for rz in leader} - {j for pr in pairs for j in (pr["builder"], pr["pull2_10"])})

    result = dict(
        schema="lowtail-zero-compute-dft-vs-mace-v1",
        question="At identical coordinates, do DFT forces support or oppose the MACE Cr lift / short Cr-O endpoint?",
        conventions=dict(normal="+z, from fixed bottom layers toward the adsorbate side",
                         site_normal_negative="pushes the site metal back toward the slab",
                         bond_stretch="(F_O - F_M).u with u from metal to O; negative shortens the contact",
                         axial_stretch="(F_axialO - F_M).u with u from metal to axial O; a two-atom difference that also carries the M=O compression force on M, so its sign alone does not say whether the axial contact opens",
                         axial_two_body="axial O vs site unit (site metal + appended O when bonded to it): relative_acceleration = F_axialO.u/m_axialO - F_unit.u/m_unit, negative closes the mass-weighted axial gap at first order; masses from ase.data",
                         forces="QE total forces only (block after 'Forces acting on atoms'); per-term contribution blocks never read",
                         free_components="if_pos of the DFT input; fixed atoms excluded from free metrics",
                         agreement_metrics="MACE forces at its own endpoints are relaxation residuals (free fmax <= 0.05 eV/A), so free-component MAE/RMSE mainly measure the DFT force at the MACE endpoint",
                         desorbed_cut_A=desorbed_cut, desorbed_cut_source=f"{rel(DESORBED_SOURCE)} M_O_DESORBED_MIN"),
        mace_checkpoint=checkpoint_evidence, mace_dtype="float64", mace_threads=threads,
        mace_reuse=reuse_evidence,
        geometry_checks=geom_checks["checks"],
        population=dict(banked_outputs=len(reg["entries"]) + len(reg["unidentified"]),
                        accepted_by_own_readout=sum(e["status"] == "ACCEPTED" for e in reg["entries"]),
                        used=len(realizations), excluded=len(excluded), unidentified=len(reg["unidentified"])),
        final_batch_population=dict(physical_outputs=sum(e.get("series") == "final" for e in reg["entries"]),
                                    used=sum(r["series"] == "final" for r in realizations),
                                    reused_OOH_aliases=sum(len(e.get("readout_aliases", [])) for e in reg["entries"])),
        excluded=excluded, unidentified=reg["unidentified"],
        mace_geometries={k: {kk: vv for kk, vv in v.items() if kk != "forces_eV_A"} | dict(forces_eV_A=np.asarray(v["forces_eV_A"]).tolist())
                         for k, v in mace.items()},
        geometry_sources={k: dict(source=v["source"], chain=v["chain"], state=v["state"], nat=len(v["symbols"]),
                                  n_fixed=len(v["fixed"])) for k, v in geoms.items()},
        realizations=rows, dft_gas=gas_dft, winner_chain_energies=chain,
        pending_endpoint_single_points=pending_endpoint_decks(),
        leader_OOH_pairs=pairs, leader_unpaired_realizations=unpaired,
        limitations=[
            "A single-point force is the local gradient of DFT energy at the MACE coordinates; it is not a relaxation, does not locate a DFT minimum and does not show whether the lifted basin exists in DFT.",
            "Forces on the site metal and the O are coupled to the 44-47 other free atoms; the sign of one component does not predict the relaxed displacement of that atom.",
            "The mass-weighted axial first-order gap response varies by site: closing at the historical winner and Fe25 seed-2 O endpoint, weakly opening at Ni31 seed-0. Clean slabs also have large forces, so these local projections do not predict the relaxed axial contact or establish a basin.",
            "Large DFT forces are present on atoms far from the site (top-layer bridging O, subsurface O and metals) in every state including the clean slab, so the fixed MACE geometry is not near a DFT stationary point anywhere in the slab.",
            "Energy differences between fixed MACE geometries include each geometry's own DFT relaxation energy and magnetic-state dependence; they are not relaxed reaction energies or overpotentials.",
            "Three sites carry accepted reconstructed O endpoints: Ni31Cr29Cu5Mn35 seed 1/site 0 and seed 0/site 0, and Fe25Co25Ni25Cr25 seed 2/site 0; the seed-0 OOH pair contains no Cr-O bond. Cu8Cr23Mn35Co34 still has no DFT force measurement in this population.",
        ])
    out_dir = Path(out_dir)
    manifest = dict(schema="lowtail-zero-compute-manifest-v1",
                    inputs=[evidence(CENSUS_NI31), evidence(CENSUS_FE25), evidence(REPLAY), evidence(REF_COEFFS_SOURCE), evidence(DESORBED_SOURCE)]
                    + [v["evidence"] for v in gas_dft.values()]
                    + list(reg["readouts"].values())
                    + [dict(role="dft_input", job=r["job"], **r["input"]) for r in rows]
                    + [dict(role="dft_output", job=r["job"], **r["output"]) for r in rows],
                    population_registry=reg,
                    all_output_evidence=[dict(job=e["job"], status=e["status"], **evidence(ROOT / e["output"]))
                                         for e in reg["entries"] if e["output"] is not None],
                    all_input_evidence=[dict(job=e["job"], status=e["status"], **evidence(ROOT / e["input"]))
                                        for e in reg["entries"] if e["input"] is not None],
                    mace_reuse=reuse_evidence,
                    implementation=[evidence(p) for p in sorted(HERE.glob("lt_*.py"))],
                    mace_checkpoint=checkpoint_evidence)
    result["manifest_sha256"] = write_json(out_dir / "input_manifest.json", manifest)
    write_json(out_dir / "zero_compute_readout.json", result)
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--checkpoint", type=Path, default=None)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--reuse-mace", type=Path, help="reuse hashed prior evaluations at unchanged source geometries")
    args = ap.parse_args(argv)
    import lt_mace
    result = run(args.out, args.checkpoint or lt_mace.DEFAULT_CHECKPOINT, args.threads, reuse_mace=args.reuse_mace)
    print(f"used {result['population']['used']} accepted realizations; excluded {result['population']['excluded']}; "
          f"unidentified {result['population']['unidentified']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
