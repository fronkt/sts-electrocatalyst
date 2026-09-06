"""Read the paired, hypothesis-driven Cr-site calculations without re-ranking compositions."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from ase import Atoms
from ase.constraints import FixAtoms
from ase.io import read, write
from ase.geometry import find_mic

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from scripts.screen_diagnostic import IMPLEMENTATION, identity, validate_manifest
from hea_oer.site_evidence import analyze_site_evidence
from hea_oer.adsorbate_geometry import analyze_adsorbate_geometry
from hea_oer.composition import Composition
from hea_oer.surfaces_rutile import build_rutile110_hea, cus_site_xy, binding_metal_index, add_oer_adsorbate_at

STATES = ("OH", "O", "OOH")
EXPECTED = {"equiatomic": ("Fe25Co25Ni25Cr25", 2), "leader": ("Ni31Cr29Cu5Mn35", 0)}


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_arm(folder, arm):
    result_path = folder / (arm + "_result.json")
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    manifest = validate_manifest(payload["manifest"])
    if set(manifest["implementation_sha256_lf"]) != set(IMPLEMENTATION):
        raise ValueError("incomplete implementation identity: " + arm)
    for relative, expected_hash in manifest["implementation_sha256_lf"].items():
        if file_hash(ROOT / relative) != expected_hash:
            raise ValueError("analysis dependency differs from run: " + relative)
    external = json.loads((folder / (arm + "_manifest.json")).read_text(encoding="utf-8"))
    if manifest != external or payload["manifest_id"] != manifest["manifest_id"]:
        raise ValueError("manifest mismatch: " + arm)
    if payload["results_sha256"] != identity(payload["results"]):
        raise ValueError("result hash mismatch: " + arm)
    if payload["status"] != "complete" or len(payload["results"]) != 1:
        raise ValueError("one completed evaluation required: " + arm)
    result = payload["results"][0]
    if result["status"] != "evaluated":
        raise ValueError("evaluation did not complete: " + arm)
    formula, seed = EXPECTED[arm]
    if result["formula"] != formula or result["candidate_id"] != manifest["candidates"][0]["candidate_id"]:
        raise ValueError("candidate identity mismatch: " + arm)
    protocol = manifest["protocol"]
    if protocol["seeds"] != [seed] or protocol["n_sites"] != 1 or protocol["steps"] != 300 or protocol["fmax_eV_A"] != 0.05:
        raise ValueError("unexpected declared protocol: " + arm)
    if len(manifest["candidates"]) != 1:
        raise ValueError("one manifest candidate required: " + arm)
    candidate = manifest["candidates"][0]
    source = ROOT / "results/r4_screen_box.json"
    if file_hash(source) != manifest["source"]["sha256_lf"]:
        raise ValueError("source data identity mismatch: " + arm)
    source_rows = [r for r in json.loads(source.read_text(encoding="utf-8"))["rows"] if r["formula"] == formula]
    if len(source_rows) != 1 or any(candidate[k] != source_rows[0][k] for k in ("formula", "elements", "fractions")):
        raise ValueError("exact source composition mismatch: " + arm)
    row = result["row"]
    if any(row[k] != candidate[k] for k in ("formula", "elements", "fractions")):
        raise ValueError("row composition mismatch: " + arm)
    if len(row["per_site_records"]) != 1:
        raise ValueError("unexpected observed site roster: " + arm)
    site = row["per_site_records"][0]
    if (site["seed"], site["site_index"]) != (seed, 0):
        raise ValueError("unexpected site identity: " + arm)
    pristine = build_rutile110_hea(Composition(tuple(candidate["elements"]), tuple(candidate["fractions"])),
                                  supercell=(2, 2), seed=seed)
    xy = cus_site_xy(pristine, n_sites=1)[0]
    center = binding_metal_index(add_oer_adsorbate_at(pristine, "O", xy), len(pristine))
    if pristine[center].symbol != "Cr" or not np.allclose(xy, site["site_xy_A"], rtol=0, atol=1e-10):
        raise ValueError("pristine Cr site identity mismatch: " + arm)
    if row["decoration_records"][0]["relaxed_slab"]["symbols"] != pristine.get_chemical_symbols():
        raise ValueError("relaxed slab atom identity mismatch: " + arm)
    evidence = analyze_site_evidence(row, [])
    if evidence != result["site_evidence"] or not evidence["coverage"]["complete"]:
        raise ValueError("evidence reconstruction mismatch: " + arm)
    if set(site["relaxed_states"]) != set(STATES) or set(row["gas_reference_records"]) != {"H2O", "H2"}:
        raise ValueError("unexpected adsorbate or gas state roster: " + arm)
    energy = site["energies_eV"]
    refs = {"OH": energy["H2O"] - 0.5 * energy["H2"], "O": energy["H2O"] - energy["H2"],
            "OOH": 2 * energy["H2O"] - 1.5 * energy["H2"]}
    offsets = {"OH": 0.35, "O": 0.05, "OOH": 0.40}
    derived = {s: energy[s] - energy["slab"] - refs[s] + offsets[s] for s in STATES}
    residual = max(abs(derived[s] - site["dG_" + s]) for s in STATES)
    if residual > 1e-7:
        raise ValueError("absolute-energy CHE mismatch: " + arm)
    attempts = {}
    for state in STATES:
        selected = site["bonds"][state + "_start"]
        entries = site["start_records"][state]
        if len(entries) != 3 or {a["start"] for a in entries} != {"builder", "pull1.70", "pull2.10"} or min(a["energy_eV"] for a in entries) != energy[state]:
            raise ValueError("start roster or selected minimum mismatch: " + arm)
        matched = [a for a in entries if a["start"] == selected]
        if len(matched) != 1:
            raise ValueError("selected start identity missing or duplicated: " + arm)
        snapshot = site["relaxed_states"][state]
        for key in ("energy_eV", "converged_by_force", "max_constrained_force_eV_A",
                    "fmax_target_eV_A", "final_binding_metal_index", "final_binding_metal", "force_readout"):
            if matched[0][key] != snapshot[key]:
                raise ValueError("selected start disagrees with selected geometry metadata: " + arm)
        if snapshot["energy_eV"] != energy[state]:
            raise ValueError("selected geometry energy mismatch: " + arm)
        attempts[state] = [{"start": a["start"], "selected": a["start"] == selected,
                            "energy_eV": a["energy_eV"], "above_selected_eV": a["energy_eV"] - energy[state],
                            "force_eV_A": a["max_constrained_force_eV_A"],
                            "converged_by_force": a["converged_by_force"],
                            "proximal_MO_A": a["bond_length_A"],
                            "nearest_metal_index": a["final_binding_metal_index"],
                            "nearest_metal": a["final_binding_metal"]} for a in entries]
    slab_record = row["decoration_records"][0]["relaxed_slab"]
    n_slab = len(pristine)
    fixed = slab_record["fixed_atom_indices"]
    free = [i for i in range(n_slab) if i not in fixed]
    distortion = {}
    comparisons = {"clean_from_pristine": (np.asarray(slab_record["positions_A"]), pristine.positions)}
    for state in STATES:
        comparisons[state + "_slab_from_clean"] = (np.asarray(site["relaxed_states"][state]["positions_A"][:n_slab]),
                                                       np.asarray(slab_record["positions_A"]))
    for label, (end, start) in comparisons.items():
        _, lengths = find_mic(end - start, slab_record["cell_A"], pbc=slab_record["pbc"])
        distortion[label] = {"free_atom_rms_displacement_A": float(np.sqrt(np.mean(lengths[free] ** 2))),
                             "free_atom_max_displacement_A": float(max(lengths[free])),
                             "fixed_atom_max_displacement_A": float(max(lengths[fixed])) if fixed else None,
                             "interpretation": "Endpoint minimum-image displacement; not a trajectory or reconstruction criterion."}
        if fixed and max(lengths[fixed]) > 1e-8:
            raise ValueError("fixed slab atom moved: " + arm)
    summary = {"formula": formula, "candidate_id": result["candidate_id"], "seed": seed, "site_index": 0,
               "candidate_seconds": result["seconds"], "result_sha256_lf": file_hash(result_path),
               "dG_eV": derived, "che_residual_eV": residual,
               "che": evidence["baseline"]["site_values"][0], "site_evidence": evidence,
               "slab_displacements": distortion,
               "selected_geometry_audit": analyze_adsorbate_geometry(row), "attempts": attempts,
               "interpretation": "One targeted environment; not the minimum across the composition's full site roster."}
    return payload, summary


def export_coordinates(payload, arm, folder):
    row = payload["results"][0]["row"]
    site = row["per_site_records"][0]
    records = {"slab": row["decoration_records"][0]["relaxed_slab"],
               **{s: site["relaxed_states"][s] for s in STATES},
               **{s: row["gas_reference_records"][s] for s in ("H2O", "H2")}}
    inventory = []
    folder.mkdir(parents=True, exist_ok=True)
    for state, record in records.items():
        if record["other_constraint_types"]:
            raise ValueError("cannot round-trip unsupported constraints")
        atoms = Atoms(symbols=record["symbols"], positions=record["positions_A"],
                      cell=record["cell_A"], pbc=record["pbc"])
        if record["fixed_atom_indices"]:
            atoms.set_constraint(FixAtoms(indices=record["fixed_atom_indices"]))
        atoms.info.update(arm=arm, state=state, energy_eV=record["energy_eV"],
                          force_converged=record["converged_by_force"])
        target = folder / (arm + "_" + state + ".extxyz")
        if target.exists():
            raise FileExistsError(target)
        write(target, atoms, format="extxyz")
        restored = read(target, format="extxyz")
        if restored.get_chemical_symbols() != record["symbols"] or not np.array_equal(restored.pbc, atoms.pbc):
            raise ValueError("coordinate roundtrip identity failure")
        if not np.allclose(restored.positions, atoms.positions, rtol=0, atol=6e-9) or not np.allclose(restored.cell, atoms.cell, rtol=0, atol=1e-10):
            raise ValueError("coordinate roundtrip precision failure")
        fixed = sorted(i for c in restored.constraints for i in c.get_indices())
        if fixed != record["fixed_atom_indices"]:
            raise ValueError("coordinate roundtrip constraint failure")
        inventory.append({"file": target.name, "sha256_lf": file_hash(target), "n_atoms": len(atoms),
                          "force_converged": record["converged_by_force"], "roundtrip_verified": True})
    return inventory


def analyze(folder, output_folder):
    payloads, arms = {}, {}
    for arm in EXPECTED:
        payloads[arm], arms[arm] = load_arm(folder, arm)
    a, b = payloads["equiatomic"], payloads["leader"]
    for key in ("source", "model", "implementation_sha256_lf"):
        if a["manifest"][key] != b["manifest"][key]:
            raise ValueError("paired calculations differ in " + key)
    if {k: v for k, v in a["manifest"]["protocol"].items() if k != "seeds"} != {k: v for k, v in b["manifest"]["protocol"].items() if k != "seeds"}:
        raise ValueError("paired protocol mismatch")
    if a["environment"] != b["environment"]:
        raise ValueError("paired environment mismatch")
    ea, eb = [payloads[k]["results"][0]["row"]["per_site_records"][0]["energies_eV"] for k in EXPECTED]
    gas_delta = {s: eb[s] - ea[s] for s in ("H2O", "H2")}
    step_delta = [y - x for x, y in zip(arms["equiatomic"]["che"]["che_steps_eV"], arms["leader"]["che"]["che_steps_eV"])]
    output = {"schema": "paired-cr-site-readout-v1", "scope": "Two hypothesis-driven, pristine-Cr-centered sites",
              "environment": a["environment"], "model": a["manifest"]["model"], "arms": arms,
              "leader_minus_equiatomic": {"che_step_differences_eV": step_delta,
                "eta_difference_V": arms["leader"]["che"]["eta_V"] - arms["equiatomic"]["che"]["eta_V"],
                "gas_energy_differences_eV": gas_delta,
                "interpretation": "Formal CHE arithmetic on the retained endpoints. Numerical and geometry assessments remain separate; this delta does not establish a resolved physical ordering."},
              "claims": {"composition_ranking": False, "DFT_validation": False, "electrode_activity": False,
                         "kinetic_barrier": False, "all_start_geometry_audited": False},
              "next_ordinary_environment": {"formula": "Fe25Co25Ni25Cr25", "seed": 2, "site_index": 1,
                "pristine_center": "Ni", "selection": "Fixed independently of its unobserved energy; no substitution for a failed Cr chain."},
              "geometry_export_note": "Selected model coordinates for inspection and later protocol design; numerical and chemical status remain attached. Exact coordinates remain in the input JSON; extxyz position precision is eight decimals."}
    output_folder.mkdir(parents=True, exist_ok=False)
    output["coordinate_inventory"] = {arm: export_coordinates(payloads[arm], arm, output_folder / "structures") for arm in EXPECTED}
    output["analysis_sha256_lf"] = {str(p.relative_to(ROOT)).replace("\\", "/"): file_hash(p) for p in
        (Path(__file__).resolve(), ROOT / "src/hea_oer/adsorbate_geometry.py", ROOT / "src/hea_oer/site_evidence.py")}
    (output_folder / "readout.json").write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.input_dir, args.out_dir)
    print(json.dumps(result["leader_minus_equiatomic"], indent=2))
