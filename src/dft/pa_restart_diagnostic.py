"""Offline P-A diagnostics; never a production acceptance or launch authority.

Replay retained inputs/logs and compare explicitly evaluated geometries. A real
QE7.5 continuous/split/negative-control probe, checkpoint review and fresh launch
specification remain mandatory. This module does not execute QE or alter scratch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"
TOLERANCES = {"energy_Ry": 1e-6, "positions_bohr": 1e-5, "forces_Ry_bohr": 1e-5}
FAILURE = re.compile(
    r"convergence NOT achieved|Error in routine|MPI_ABORT|SIGTERM|SIGINT|"
    r"SIGSEGV|Segmentation fault|Floating point exception|IEEE_(?:INVALID|OVERFLOW|"
    r"DIVIDE_BY_ZERO)_FLAG|forrtl:\s*severe", re.I)


def number(text):
    value = float(text.replace("D", "e").replace("d", "e"))
    if not math.isfinite(value):
        raise ValueError("nonfinite numerical evidence")
    return value


def input_mode(text):
    # The tiny-probe contract requires one explicit assignment, not QE defaults.
    uncommented = "\n".join(line.split("!", 1)[0] for line in text.splitlines())
    values = re.findall(r"\brestart_mode\s*=\s*['\"]([^'\"]+)['\"]",
                        uncommented, re.I)
    if len(values) != 1 or values[0].lower() not in {"from_scratch", "restart"}:
        raise ValueError("exactly one explicit valid restart_mode required")
    return values[0].lower()


def inspect_segment(input_text, output_text):
    mode = input_mode(input_text)
    versions = re.findall(r"Program PWSCF v\.([0-9.]+)", output_text)
    if versions != ["7.5"]:
        raise ValueError("one QE7.5 output required")
    counts = [int(v) for v in re.findall(r"number of bfgs steps\s*=\s*(\d+)", output_text)]
    radii = [number(v) for v in re.findall(r"new trust radius\s*=\s*(" + NUM + r")\s*bohr", output_text)]
    deleted = bool(re.search(r"\.bfgs deleted, as requested", output_text, re.I))
    disabled = bool(re.search(r"restart disabled:\s*needed files not found", output_text, re.I))
    reset = deleted or (bool(counts) and counts[0] == 0)
    if mode == "restart":
        diagnosis = ("RESTART_REJECTED" if reset or disabled else
                     "CONTINUATION_UNPROVEN")
    else:
        diagnosis = "HISTORY_RESET" if reset else "NO_RESET_EVIDENCE"
    return {
        "scope": "OFFLINE_DIAGNOSTIC_ONLY", "production_accepted": False,
        "real_qe_probe_pending": True, "restart_mode": mode, "qe_version": "7.5",
        "bfgs_deleted": deleted, "restart_disabled": disabled,
        "bfgs_counts": counts, "trust_radii_bohr": radii,
        "clean_user_stop_marker": bool(re.search(r"Program stopped by user request", output_text, re.I)),
        "failure_markers": FAILURE.findall(output_text),
        "job_done": "JOB DONE." in output_text, "diagnosis": diagnosis,
        "limitations": "Log markers alone do not prove checkpoint consumption or successful relaxation.",
    }


def vectors(value, key):
    if not isinstance(value, list) or not value:
        raise ValueError("nonempty atom matrix required: " + key)
    for row in value:
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError("three Cartesian components required: " + key)
        for item in row:
            if type(item) not in (int, float) or not math.isfinite(item):
                raise ValueError("finite numeric components required: " + key)
    return value


def evaluation(record):
    if record.get("geometry_role") != "evaluated" or record.get("scf_converged") is not True:
        raise ValueError("converged evaluated geometry required, not a proposal")
    if type(record.get("energy_Ry")) not in (int, float) or not math.isfinite(record["energy_Ry"]):
        raise ValueError("finite evaluated energy required")
    p = vectors(record.get("positions_bohr"), "positions_bohr")
    f = vectors(record.get("forces_Ry_bohr"), "forces_Ry_bohr")
    species = record.get("species")
    if (not isinstance(species, list) or len(species) != len(p) or len(f) != len(p)
            or any(not isinstance(s, str) or not s for s in species)):
        raise ValueError("atom/species/force count mismatch")
    # Bind every transcription to retained raw evidence, without claiming its
    # semantic accuracy is established by a hash. Independent review is required.
    source = record.get("source")
    if (not isinstance(source, dict) or not isinstance(source.get("path"), str)
            or not source["path"] or not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", ""))
            or type(source.get("line_start")) is not int or source["line_start"] < 1
            or type(source.get("line_end")) is not int or source["line_end"] < source["line_start"]):
        raise ValueError("raw source hash and exact line interval required")
    return record


def compare_evaluations(continuous, split):
    """Ordered full trajectory comparison; source transcriptions need review.

    Duplicate boundary evaluations must be adjudicated outside this comparator,
    with the original record retained. No interpolation, permutation, alignment,
    endpoint-only comparison or periodic coordinate remapping is performed.
    """
    if (not isinstance(continuous, list) or not isinstance(split, list)
            or len(continuous) < 3 or len(continuous) != len(split)):
        raise ValueError("matching full trajectories with at least three evaluations required")
    maxima = dict.fromkeys(TOLERANCES, 0.0)
    atom_order = None
    for left, right in zip(continuous, split):
        left, right = evaluation(left), evaluation(right)
        if atom_order is None:
            atom_order = left["species"]
        if left["species"] != atom_order or right["species"] != atom_order:
            raise ValueError("atom identity/order changed")
        maxima["energy_Ry"] = max(maxima["energy_Ry"], abs(left["energy_Ry"] - right["energy_Ry"]))
        for key in ("positions_bohr", "forces_Ry_bohr"):
            delta = max(abs(a-b) for la, ra in zip(left[key], right[key]) for a,b in zip(la,ra))
            maxima[key] = max(maxima[key], delta)
    matched = all(maxima[key] <= tolerance for key,tolerance in TOLERANCES.items())
    return {"scope": "OFFLINE_TRANSCRIPTION_COMPARISON_ONLY", "production_accepted": False,
            "real_qe_probe_pending": True, "evaluations": len(continuous),
            "within_proposed_tolerances": matched, "max_abs_deltas": maxima,
            "proposed_tolerances": TOLERANCES.copy(),
            "independent_source_and_checkpoint_review_required": True}


def inspect_files(input_path, output_path):
    a, b = Path(input_path), Path(output_path)
    result = inspect_segment(a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8"))
    result["sources"] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (a,b)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_files(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()
