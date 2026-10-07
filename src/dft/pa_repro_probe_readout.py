"""Offline readout for the same-state reproducibility probe; never runs QE or touches Anvil.

Applies the readings registered in docs/research/pa-repro-probe-2026-10-07.md to
P1_C3_repeat and P2_C3_repeat (this probe) and C3_warm_1e-10 / D2_fresh_1e-10 (the
fixed-geometry diagnostic), with the diagnostic's parser and comparison unchanged.
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pa_fixed_geometry_readout as r

XML = "outdir/slab_c5low__pa_boundary.save/data-file-schema.xml"
PROBES = ("P1_C3_repeat", "P2_C3_repeat")
HALF_GATE = r.GATE["force_Ry_bohr"] / 2


def first_divergence(left: list, right: list):
    """1-based SCF iteration where the printed accuracy sequences first differ; None if identical."""
    for i, (a, b) in enumerate(zip(left, right), 1):
        if a != b:
            return i
    return None if len(left) == len(right) else min(len(left), len(right)) + 1


def pair(left: dict, right: dict) -> dict:
    c = r.compare(left, right)
    return {"force_Ry_bohr": c["metrics"]["force_Ry_bohr"], "energy_Ry": c["metrics"]["energy_Ry"],
            "position_bohr": c["metrics"]["position_bohr"], "max_force_component": c["max_force_component"],
            "max_hubbard_trace_delta": c["max_hubbard_trace_delta"],
            "total_magnetization_delta": c["total_magnetization_delta"],
            "iterations": [left["iterations"], right["iterations"]],
            "first_accuracy_divergence": first_divergence(left["accuracy_sequence_Ry"], right["accuracy_sequence_Ry"])}


def node_of(allocation: Path):
    """Node of a call, from the controller's scontrol record taken just before launch."""
    if not allocation.exists():
        return None
    text = json.loads(allocation.read_text(encoding="utf-8"))["stdout"]
    hits = set(re.findall(r"(?:^|\s)NodeList=([A-Za-z0-9_\[\],-]+)", text))
    return hits.pop() if len(hits) == 1 else None


def readings(runs: dict, d2: dict, nodes: dict = None) -> dict:
    """runs: name -> evaluation for C3 and every valid, converged probe call; nodes: name -> node."""
    nodes = nodes or {}
    pairs = {a + "|" + b: pair(runs[a], runs[b]) for a, b in itertools.combinations(sorted(runs), 2)}
    for key, value in pairs.items():
        a, b = key.split("|")
        value["nodes"] = [nodes.get(a), nodes.get(b)]
        value["same_node"] = None if None in value["nodes"] else nodes[a] == nodes[b]
    path = pair(runs["C3_warm_1e-10"], d2) if "C3_warm_1e-10" in runs else None
    complete = all(name in runs for name in PROBES) and "C3_warm_1e-10" in runs
    out = {"pairs": pairs, "path_pair_C3_vs_D2": path, "complete": complete}
    if not complete:
        out["PR1_same_state_reproducibility"] = "INCOMPLETE"
        out["PR2_path_vs_noise"] = "INCOMPLETE"
        return out
    spread = max(p["force_Ry_bohr"] for p in pairs.values())
    energy = max(p["energy_Ry"] for p in pairs.values())
    out["same_state_max_force_Ry_bohr"] = spread
    out["same_state_max_energy_Ry"] = energy
    out["probe_pair_P1_P2"] = pairs["P1_C3_repeat|P2_C3_repeat"]["force_Ry_bohr"]
    out["nodes"] = {k: nodes.get(k) for k in runs}
    for label, flag in (("same_node_max", True), ("cross_node_max", False)):
        hits = [v["force_Ry_bohr"] for v in pairs.values() if v["same_node"] is flag]
        out[label] = max(hits) if hits else None
    out["PR1_same_state_reproducibility"] = (
        "IDENTICAL_PATH" if spread <= r.IDENTICAL_FORCE and energy <= r.IDENTICAL_FORCE
        else "REPRODUCIBLE_BELOW_HALF_GATE" if spread <= HALF_GATE
        else "RUN_TO_RUN_NOISE_AT_GATE_SCALE")
    out["PR2_path_vs_noise"] = ("PATH_SPREAD_WITHIN_RUN_TO_RUN_NOISE" if spread >= path["force_Ry_bohr"] / 2
                                else "PATH_SPREAD_EXCEEDS_RUN_TO_RUN_NOISE")
    return out


def load(directory: Path, status: dict, excluded: dict):
    name = directory.name
    if status.get(name) != "COMPLETED":
        excluded[name] = "controller status " + str(status.get(name))
        return None
    try:
        arm = r.parse_arm(directory, directory / XML)
    except (OSError, ValueError, StopIteration, KeyError, IndexError, TypeError, ET.ParseError) as exc:
        excluded[name] = "parse error: " + repr(exc)
        return None
    if not arm["start"]["valid"]:
        excluded[name] = "invalid start: " + json.dumps(arm["start"])
        return None
    evaluation = arm["evaluations"][0]
    if len(arm["evaluations"]) != 1 or evaluation["status"] != "CONVERGED":
        excluded[name] = "not one converged SCF: " + evaluation["status"]
        return None
    return evaluation


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True, help="probe raw_mirror (runs/, groups/)")
    parser.add_argument("--diag", type=Path, required=True, help="diagnostic raw_mirror (runs/, groups/)")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    status = {}
    for mirror in (args.probe, args.diag):
        for receipt in sorted(mirror.glob("groups/*/group_receipt.json")):
            for row in json.loads(receipt.read_text(encoding="utf-8"))["calls"]:
                status[row["name"]] = row.get("status")
    excluded, runs = {}, {}
    for directory in [args.diag / "runs/C3_warm_1e-10"] + [args.probe / "runs" / n for n in PROBES]:
        if not (directory / "stdout.log").exists():
            excluded[directory.name] = "not run"
            continue
        evaluation = load(directory, status, excluded)
        if evaluation is not None:
            runs[directory.name] = evaluation
    d2 = load(args.diag / "runs/D2_fresh_1e-10", status, excluded)
    if d2 is None:
        raise SystemExit("D2 reference unavailable: " + excluded["D2_fresh_1e-10"])
    nodes = {"C3_warm_1e-10": node_of(args.diag / "groups/ladder/allocation_03_before_launch.json")}
    for index, name in enumerate(PROBES, 1):
        nodes[name] = node_of(args.probe / "groups/probe" / ("allocation_%02d_before_launch.json" % index))
    result = {"schema": "pa-repro-probe-readout-v1", "controller_status": status, "excluded": excluded,
              "summaries": {k: r.summary(v) for k, v in runs.items()}, "D2_summary": r.summary(d2),
              "readings": readings(runs, d2, nodes)}
    args.out.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({k: v for k, v in result["readings"].items() if k != "pairs" and k != "path_pair_C3_vs_D2"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
