"""Build the ENDMEMBER-2x2 manifest (docs/91) from results/.../inputs/r4_validate.json.

screen_diagnostic.prepare() reads a source with a ``rows`` list; r4_validate.json carries its
seven endmember predictions under ``pred`` (keyed by metal) and has no ``rows``, so
prepare() cannot read it as --source (it fails on ``data["rows"]`` with KeyError: 'rows'
before writing anything). This wrapper builds a manifest of the same
screen-diagnostic-v1 schema with screen_diagnostic's own identity, hashing and validation
functions (imported read-only; nothing in that file is modified), with candidates
Cr100 .. Ir100 as single-element compositions, fraction exactly 1.0, seed 0, one cus site,
2x2 supercell, fmax 0.05, 300 steps, float64. screen_diagnostic.py run accepts the result
unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from scripts import screen_diagnostic as diagnostic  # noqa: E402
from scripts.site_census_plan import ENDMEMBERS, VALIDATE_SOURCE  # noqa: E402


def prepare_endmembers(source, model_file, *, metals=ENDMEMBERS, seeds=(0,), n_sites=1,
                       fmax=.05, steps=300):
    source, model_file = Path(source), Path(model_file)
    data = json.loads(source.read_text(encoding="utf-8"))
    if data.get("status") != "complete":
        raise ValueError("source validation run must be complete")
    if data.get("n_sites") != 1 or data.get("supercell") != [2, 2] or data.get("fmax") != fmax:
        raise ValueError("source validation protocol differs from the requested protocol")
    pred = data["pred"]
    candidates = []
    for metal in metals:
        row = pred[metal]
        label = row["formula"]
        if label != metal + "100":
            raise ValueError(f"unexpected endmember label {label} for {metal}")
        comp = {"elements": [metal], "fractions": [1.0]}
        candidates.append(dict(formula=label, candidate_id=diagnostic.identity(comp), **comp))
    result = dict(
        schema=diagnostic.SCHEMA,
        purpose="Validation-endmember 2x2 geometry supply for a DFT cell test; not held-out evaluation or melt selection",
        source={"filename": source.name, "sha256_lf": diagnostic.sha256_file(source, normalize_lf=True)},
        model={"historical_label": data.get("model"), "filename": model_file.name,
               "sha256_bytes": diagnostic.sha256_file(model_file),
               "historical_weight_identity_established": False},
        implementation_sha256_lf={p: diagnostic.sha256_file(ROOT / p, normalize_lf=True)
                                  for p in diagnostic.IMPLEMENTATION},
        protocol={"mode": "diagnostic", "seeds": list(seeds), "n_sites": n_sites,
                  "supercell": [2, 2], "fmax_eV_A": fmax, "steps": steps,
                  "dtype": "float64", "surface": "rutile",
                  "aggregation": "legacy minimum retained, no QC replacement",
                  "sampling_role": "fixed diagnostic; no composition generalization"},
        candidates=candidates,
        work_estimate={"clean_slab_relaxations": len(candidates) * len(seeds),
                       "adsorbate_relaxations_upper": len(candidates) * len(seeds) * n_sites * 9,
                       "gas_relaxations_per_process": 2,
                       "wall_time_estimate_seconds": None},
    )
    result["manifest_id"] = diagnostic.identity(result)
    return diagnostic.validate_manifest(result)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=VALIDATE_SOURCE)
    parser.add_argument("--model-file", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    manifest = prepare_endmembers(args.source, args.model_file)
    diagnostic.write_json_new(args.out, manifest)
    print(manifest["manifest_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
