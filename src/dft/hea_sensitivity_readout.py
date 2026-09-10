"""Paired cutoff/smearing sensitivity with exact source and output provenance.

Reuses the numerical readout's raw force/projection/Hubbard checks. Printed QE
F and -TS are retained separately; no zero-smearing extrapolation or automatic
numerical accuracy / electronic-basin classification is performed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re

try:
    from . import hea_sensitivity_guard as guard
    from . import hea_numerical_readout as numerical
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import hea_sensitivity_guard as guard
    import hea_numerical_readout as numerical

SCHEMA = "hea-sensitivity-readout-v1"
ARMS = ("wfc", "rho", "smearing")
ENDPOINTS = ("builder", "pull2.10")
EXPECTED = ["hs__leader_" + endpoint + "__ortho__" + arm
            for arm in ARMS for endpoint in ENDPOINTS]
ARM_SETTINGS = {"wfc": {"ecutwfc": 100.0, "ecutrho": 640.0, "degauss": 0.01},
                "rho": {"ecutwfc": 80.0, "ecutrho": 800.0, "degauss": 0.01},
                "smearing": {"ecutwfc": 80.0, "ecutrho": 640.0, "degauss": 0.005}}
SOURCE_HASH_FIELDS = {"output": "source_output_sha256", "projection": "source_projection_sha256",
                      "qc": "source_qc_sha256", "input": "source_input_sha256"}
RY_TO_EV = numerical.force.RY_TO_EV


def thermodynamics(text):
    """Read final eight-decimal Ry terms; check only their print-rounding identity."""
    patterns = {
        "free_energy_Ry": r"^!\s+total energy\s*=\s*(" + numerical.force.NUM + r")\s+Ry\s*$",
        "minus_ts_Ry": r"^\s*smearing contrib\. \(-TS\)\s*=\s*(" + numerical.force.NUM + r")\s+Ry\s*$",
        "internal_energy_Ry": r"^\s*internal energy E=F\+TS\s*=\s*(" + numerical.force.NUM + r")\s+Ry\s*$",
    }
    values = {}
    for field, pattern in patterns.items():
        matches = re.findall(pattern, text, re.M)
        if len(matches) != 1:
            raise ValueError("exactly one finite final QE thermodynamic term required: " + field)
        values[field] = numerical.force.number(matches[0])
    # Each of F, -TS and E is printed to eight decimal Ry places in QE7.5.
    if abs(values["free_energy_Ry"] - values["minus_ts_Ry"] - values["internal_energy_Ry"]) > 1.500001e-8:
        raise ValueError("printed F, -TS and internal E are inconsistent")
    values.update({key[:-3] + "_eV": value * RY_TO_EV for key, value in list(values.items())})
    values["interpretation"] = "QE finite-smearing F, its printed -TS contribution and E=F+TS; internal E is not an extrapolated zero-smearing energy"
    return values


def _source_metadata(terms, audit, metadata):
    """Connect accepted raw parent output to its frozen converged checkpoint XML."""
    if metadata.get("converged") is not True:
        raise ValueError("source checkpoint XML is not converged")
    for raw_key, xml_key in (("free_energy_Ry", "energy_hartree"),
                             ("minus_ts_Ry", "smearing_contribution_hartree")):
        value = metadata[xml_key]
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("source XML thermodynamic value is not finite")
        # QE raw energy rounding: half of 0.5e-8 Ry, expressed in Hartree.
        if abs(terms[raw_key] / 2 - value) > 2.5001e-9:
            raise ValueError("source raw energy differs from frozen checkpoint XML: " + xml_key)
    for key in ("total_moment_muB", "absolute_moment_muB"):
        raw, saved = audit["scf"][key], metadata[key]
        if raw is None or type(saved) not in (int, float) or not math.isfinite(saved) or abs(raw-saved) > 0.005000001:
            raise ValueError("source raw magnetization differs from checkpoint XML: " + key)


def _complete_terms(record, folder, source_checkpoint=None, metadata=None):
    if record["status"] != "ACCEPTED":
        return record
    try:
        if source_checkpoint is not None:
            for kind, field in SOURCE_HASH_FIELDS.items():
                if record["files"][kind]["sha256_bytes"] != source_checkpoint[field]:
                    raise ValueError("source artifact differs from frozen hash: " + kind)
        raw = (folder / (record["job"] + ".out")).read_bytes()
        if hashlib.sha256(raw).hexdigest() != record["files"]["output"]["sha256_bytes"]:
            raise ValueError("raw output changed during readout")
        text = raw.decode("utf-8")
        terms = thermodynamics(text)
        if source_checkpoint is not None:
            record["startup"] = numerical.startup_evidence(text, "tight")
            _source_metadata(terms, record["audit"], metadata)
            record["source_artifact_hashes_match"] = True
            record["source_checkpoint_metadata_match"] = True
        record["thermodynamics"] = terms
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        record.update(status="REJECTED", reasons=[str(exc)], audit=None, hubbard=None,
                      thermodynamics=None)
    return record


def _pair_terms(originals, targets):
    result = {}
    for label, field in (("free_energy", "free_energy_eV"), ("minus_ts", "minus_ts_eV"),
                         ("internal_energy", "internal_energy_eV")):
        source_gap = originals[1]["thermodynamics"][field] - originals[0]["thermodynamics"][field]
        target_gap = targets[1]["thermodynamics"][field] - targets[0]["thermodynamics"][field]
        result[label] = dict(source_gap_eV=source_gap, target_gap_eV=target_gap,
                             delta_gap_eV=target_gap-source_gap)
    return result


def build_readout(root, spec_path):
    root = Path(root).resolve(strict=True)
    spec_path = Path(spec_path)
    bundle = guard.load_bundle(spec_path, root / "runs")
    spec, checkpoints = bundle["spec"], bundle["checkpoints"]
    if [job["job"] for job in spec["jobs"]] != EXPECTED:
        raise ValueError("readout requires exact ordered six sensitivity jobs")
    sources = {}
    for source_job, checkpoint in checkpoints.items():
        path = numerical.guard._path(root, checkpoint["source_input"])
        folder = path.parent
        record = numerical.accepted_endpoint(folder, source_job)
        sources[source_job] = _complete_terms(record, folder, checkpoint,
                                              bundle["metadata"][source_job])
    required_sources = {"hn__leader_" + endpoint + "__ortho__tight" for endpoint in ENDPOINTS}
    if set(sources) != required_sources:
        raise ValueError("exactly the two accepted ortho tight source states are required")
    endpoints = []
    for job in spec["jobs"]:
        arm = job["arm"]
        endpoint = "builder" if job["job"] == "hs__leader_builder__ortho__" + arm else "pull2.10"
        if arm not in ARMS or job["source_job"] != "hn__leader_" + endpoint + "__ortho__tight":
            raise ValueError("sensitivity arm/source lineage mismatch")
        folder = numerical.guard._path(root, "runs/" + job["dir"])
        prepared_path = folder / (job["job"] + ".in")
        prepared_raw = prepared_path.read_bytes()
        if hashlib.sha256(prepared_raw).hexdigest() != job["sha256"]:
            raise ValueError("prepared input changed during readout")
        checkpoint = checkpoints[job["source_job"]]
        receipt = dict(schema="hea_sensitivity_clone_v1", job=job["job"], prefix=job["prefix"],
                       source_job=job["source_job"], arm=arm, source=checkpoint["dir"],
                       destination=job["dir"] + "/tmp_" + job["job"] + "/" + job["prefix"] + ".save",
                       source_checkpoints_sha256=spec["source_checkpoints_sha256"], files=checkpoint["files"])
        record = numerical.accepted_endpoint(folder, job["job"], prepared_raw.decode("utf-8"), "tight",
                                              (folder / (job["job"] + ".clone_receipt.json"), receipt))
        record = _complete_terms(record, folder)
        record.update(source_job=job["source_job"], endpoint=endpoint, projector="ortho", arm=arm,
                      prepared_input=numerical.evidence(prepared_path))
        endpoints.append(record)
    indexed = {row["job"]: row for row in endpoints}
    pairs = []
    for arm in ARMS:
        targets = [indexed["hs__leader_" + endpoint + "__ortho__" + arm] for endpoint in ENDPOINTS]
        originals = [sources[row["source_job"]] for row in targets]
        pair = dict(arm=arm, settings=ARM_SETTINGS[arm], status="PENDING", source_gap_eV=None,
                    target_gap_eV=None, delta_gap_eV=None, thermodynamic_gap_terms=None, endpoints=[])
        if all(row["status"] == "ACCEPTED" for row in originals):
            pair["source_gap_eV"] = originals[1]["audit"]["scf"]["energy_eV"] - originals[0]["audit"]["scf"]["energy_eV"]
        if all(row["status"] == "ACCEPTED" for row in originals + targets):
            pair["target_gap_eV"] = targets[1]["audit"]["scf"]["energy_eV"] - targets[0]["audit"]["scf"]["energy_eV"]
            pair["delta_gap_eV"] = pair["target_gap_eV"] - pair["source_gap_eV"]
            pair["endpoints"] = [numerical.endpoint_difference(a, b) for a, b in zip(originals, targets)]
            pair["thermodynamic_gap_terms"] = _pair_terms(originals, targets)
            pair["status"] = "COMPLETE"
        elif any(row["status"] == "REJECTED" for row in originals + targets):
            pair["status"] = "REJECTED"
        pairs.append(pair)
    counts = {status.lower(): sum(row["status"] == status for row in endpoints)
              for status in ("ACCEPTED", "PENDING", "REJECTED")}
    source_counts = {status.lower(): sum(row["status"] == status for row in sources.values())
                     for status in ("ACCEPTED", "PENDING", "REJECTED")}
    complete = all(pair["status"] == "COMPLETE" for pair in pairs)
    rejected = counts["rejected"] > 0 or source_counts["rejected"] > 0 or any(pair["status"] == "REJECTED" for pair in pairs)
    result = dict(schema=SCHEMA, checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  status="REJECTED" if rejected else "COMPLETE" if complete else "PENDING",
                  batch_readout_complete=complete, counts=counts, source_counts=source_counts,
                  spec=numerical.evidence(spec_path),
                  source_inventory=numerical.evidence(numerical.guard._path(root, spec["source_checkpoints"])),
                  endpoints=endpoints, sources=list(sources.values()), pairs=pairs,
                  gap_definition="QE F(pull2.10)-F(builder), finite-smearing total-energy functional",
                  numerical_accuracy_status="NOT_INFERRED", electronic_basin_status="NOT_INFERRED",
                  limitations=[
                      "Two endpoint states at one retained seed-0 geometry; no candidate ranking, magnetic ground-state, or relaxed thermodynamic claim.",
                      "Each pair varies only the declared cutoff or smearing setting, but initialization and final electronic-state sensitivity still require interpretation.",
                      "A changed wavefunction cutoff changes the basis; file initialization is an approximate warm start, not exact interrupted continuation.",
                      "Printed -TS and internal E=F+TS are diagnostics; no zero-smearing energy extrapolation is performed.",
                      "No calibrated error bound follows from single-setting comparisons; joint settings and k-point checks remain separate work.",
                      "Large residual forces can coexist with valid fixed-geometry SCFs. Signed force/moment/Hubbard differences do not automatically classify the electronic basin.",
                      "Checkpoint clone receipts and frozen source hashes are verified; actual remote clone/retention and executable/pseudopotential identities use retained launch evidence."])
    json.dumps(result, allow_nan=False)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build_readout(args.root, args.spec)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, allow_nan=False)
            handle.write("\n")
    except (OSError, ValueError, KeyError) as exc:
        print("REFUSE: " + str(exc))
        return 2
    print(json.dumps(dict(status=result["status"], counts=result["counts"], source_counts=result["source_counts"],
                          batch_readout_complete=result["batch_readout_complete"])))
    return 2 if result["status"] == "REJECTED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
