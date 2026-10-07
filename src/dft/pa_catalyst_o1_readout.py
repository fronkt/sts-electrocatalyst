"""Offline readout for the O1 one-boundary re-test; never runs QE or touches Anvil.

The registered reading (docs/research/pa-catalyst-o1-2026-10-07.md) comes from the
controller's own trial_receipt.json: its continuity record (tolerances in force), the
conv_thr carry-over check, the pre-resume decision and the call statuses. Separately and
informatively, the same ordered evaluations are re-read with the fixed-geometry parser to
report Hubbard-trace and magnetization deltas; those never change the registered reading.
"""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pa_fixed_geometry_readout as r

XML = "outdir/slab_c5low__pa_boundary.save/data-file-schema.xml"
O1_TOLERANCES = {"energy_Ry": 3e-5, "position_bohr": 1e-3, "force_Ry_bohr": 5e-4}


def registered_reading(receipt: dict) -> dict:
    continuity = receipt.get("continuity") or {}
    carry = receipt.get("conv_thr_carry")
    action = (receipt.get("pre_resume_decision") or {}).get("action")
    calls = {c.get("name"): c.get("status") for c in receipt.get("calls", [])}
    reasons = []
    # The verdict must come from this dated run and the registered O1 tolerances, not from defaults.
    registered = receipt.get("date") == "2026-10-07" and continuity.get("tolerances") == O1_TOLERANCES
    if not registered:
        reasons.append("receipt date or continuity tolerances are not the registered O1 values")
    if registered and receipt.get("scientific_status") == "PASS_ONE_BOUNDARY" \
            and continuity.get("within_tolerances") is True and (carry or {}).get("equal") is True \
            and action == "RESUME_CANDIDATE" and calls.get("negative") == "NUMERICAL_RECEIPT_VALIDATED":
        reading = "CONTINUITY_PASS"
    elif registered and continuity.get("within_tolerances") is False and (carry or {}).get("equal") is True:
        reading = "CONTINUITY_FAIL"
        reasons.append("ordered evaluations outside the registered tolerances")
    else:
        reading = "INCONCLUSIVE"
        if action != "RESUME_CANDIDATE":
            reasons.append("pre-resume decision " + str(action))
        if carry is None:
            reasons.append("conv_thr carry-over check absent")
        elif carry.get("equal") is not True:
            reasons.append("conv_thr carry-over unavailable or unequal")
        if "within_tolerances" not in continuity:
            reasons.append("no continuity comparison")
        failed = {k: v for k, v in calls.items() if v != "NUMERICAL_RECEIPT_VALIDATED"}
        if failed:
            reasons.append("calls not validated: " + json.dumps(failed, sort_keys=True))
        if receipt.get("error"):
            reasons.append("controller error: " + str(receipt["error"]))
    return {"reading": reading, "reasons": reasons, "scientific_status": receipt.get("scientific_status"),
            "tolerances_in_force": continuity.get("tolerances"), "max_abs_deltas": continuity.get("max_abs_deltas"),
            "ordered_differences": continuity.get("ordered_differences"), "conv_thr_carry": carry,
            "pre_resume_action": action, "calls": calls,
            # PASS_ONE_BOUNDARY already requires the negative control's startup deletion and count 0.
            "negative_control_status": calls.get("negative")}


def informative(trial: Path) -> dict:
    """Same ordered pairing as the controller (control 1-3 vs candidate 1 + resumed 2-3), with state deltas."""
    control = r.parse_arm(trial / "control", trial / "control" / XML)["evaluations"]
    candidate = r.parse_arm(trial / "candidate", trial / "candidate" / XML)["evaluations"]
    resumed = r.parse_arm(trial / "resumed", trial / "resumed/checkpoint_copy" / XML)["evaluations"]
    split = candidate + resumed
    if len(control) != 3 or len(split) != 3:
        raise ValueError("ordered evaluations are not 3 + 3")
    rows = []
    for k, (left, right) in enumerate(zip(control, split), 1):
        c = r.compare(left, right)
        rows.append({"evaluation": k, "metrics": c["metrics"], "max_force_component": c["max_force_component"],
                     "within_O1": {key: c["metrics"][key] <= O1_TOLERANCES[key] for key in O1_TOLERANCES},
                     "max_hubbard_trace_delta": c["max_hubbard_trace_delta"],
                     "total_magnetization_delta": c["total_magnetization_delta"],
                     "same_state_by_traces": (c["max_hubbard_trace_delta"] is not None
                                              and c["max_hubbard_trace_delta"] <= r.STATE_TRACE),
                     # Relaxation stdout prints magnetization to 0.01, so one print unit equals the limit.
                     "same_state_by_magnetization": (c["total_magnetization_delta"] is not None
                                                     and c["total_magnetization_delta"] <= r.STATE_MAGNETIZATION + 1e-9)})
    return {"note": "informative: fixed-geometry parser re-read; never changes the registered reading",
            "o1_tolerances": O1_TOLERANCES, "evaluations": rows,
            "all_within_O1": all(all(row["within_O1"].values()) for row in rows)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial", type=Path, required=True, help="mirrored trial_results directory")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--historical", action="store_true",
                        help="label the output as a re-read of earlier data, never an O1 result")
    args = parser.parse_args(argv)
    receipt = json.loads((args.trial / "trial_receipt.json").read_text(encoding="utf-8"))
    result = {"schema": "pa-catalyst-o1-readout-v1", "historical": args.historical,
              "date": receipt.get("date"), "registered": registered_reading(receipt)}
    try:
        result["informative"] = informative(args.trial)
    except (OSError, ValueError, StopIteration, KeyError, IndexError, TypeError, ET.ParseError) as exc:
        result["informative"] = {"error": repr(exc)}
    if args.historical:
        result["label"] = "HISTORICAL RE-READ: not an O1 result; the original verdict stands"
    args.out.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"historical": args.historical, "reading": result["registered"]["reading"],
                      "all_within_O1_informative": result["informative"].get("all_within_O1")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
