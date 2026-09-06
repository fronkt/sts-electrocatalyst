"""Recover all OOH endpoints from the exact retained clean slabs and original starts."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time

os.environ.setdefault("TORCHINDUCTOR_CACHE_DIR", str(Path(tempfile.gettempdir()) / "sts-torch-cache"))
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from scripts.screen_diagnostic import identity, sha256_file, validate_manifest, checkpoint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("equiatomic", "leader"), required=True)
    parser.add_argument("--model-file", type=Path, required=True)
    parser.add_argument("--folder", type=Path, required=True)
    args = parser.parse_args()
    source = args.folder / (args.arm + "_result.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    manifest = validate_manifest(data["manifest"])
    if data["status"] != "complete" or identity(data["results"]) != data["results_sha256"]:
        raise ValueError("original chain incomplete or altered")
    if sha256_file(args.model_file) != manifest["model"]["sha256_bytes"]:
        raise ValueError("model identity changed")
    for relative, expected in manifest["implementation_sha256_lf"].items():
        if sha256_file(ROOT / relative, normalize_lf=True) != expected:
            raise ValueError("implementation changed: " + relative)
    target = args.folder / (args.arm + "_ooh_replay.json")
    if target.exists():
        raise FileExistsError(target)
    import torch
    torch.set_num_threads(2)
    from ase import Atoms
    from ase.constraints import FixAtoms
    from hea_oer.relax import make_mace_calculator, relax
    from hea_oer.adsorption import _screen_structure_record
    from hea_oer.surfaces_rutile import adsorbate_starts, binding_metal_index, m_o_distance
    row = data["results"][0]["row"]
    site = row["per_site_records"][0]
    record = row["decoration_records"][0]["relaxed_slab"]
    if record["other_constraint_types"]:
        raise ValueError("unsupported slab constraints")
    slab = Atoms(record["symbols"],positions=record["positions_A"],cell=record["cell_A"],pbc=record["pbc"])
    if record["fixed_atom_indices"]:
        slab.set_constraint(FixAtoms(indices=record["fixed_atom_indices"]))
    output = {"schema": "ooh-start-replay-v1", "arm": args.arm, "status": "running",
              "source_result_sha256_lf": sha256_file(source, normalize_lf=True),
              "manifest_id": manifest["manifest_id"], "model": manifest["model"],
              "environment": data["environment"], "fmax_eV_A": .05, "steps": 300,
              "sampling": "Exact original three starts on retained relaxed slab; no new candidate or adsorption-site sampling",
              "attempts": [], "script_sha256_lf": sha256_file(__file__,normalize_lf=True)}
    checkpoint(target, output)
    calc = make_mace_calculator(str(args.model_file), device="cpu", dtype="float64")
    originals = {a["start"]:a for a in site["start_records"]["OOH"]}
    started = time.monotonic()
    for tag, initial in adsorbate_starts(slab, "OOH", site["site_xy_A"]):
        t0 = time.monotonic()
        energy, atoms = relax(initial, calc, fmax=.05, steps=300)
        geometry = _screen_structure_record(atoms,.05)
        nearest = int(binding_metal_index(atoms, len(slab)))
        geometry.update(energy_eV=energy,final_binding_metal_index=nearest,final_binding_metal=atoms[nearest].symbol)
        output["attempts"].append({"start":tag,"energy_eV":energy,"geometry":geometry,
          "proximal_MO_A":float(m_o_distance(atoms,len(slab))),
          "original_energy_eV":originals[tag]["energy_eV"],
          "replay_minus_original_eV":energy-originals[tag]["energy_eV"],
          "seconds":time.monotonic()-t0})
        output["attempts_sha256"] = identity(output["attempts"])
        checkpoint(target,output)
        print(json.dumps({"arm":args.arm,"start":tag,"seconds":time.monotonic()-t0,"energy_difference_eV":energy-originals[tag]["energy_eV"]}),flush=True)
    output["status"] = "complete"
    output["seconds"] = time.monotonic()-started
    checkpoint(target,output)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
