"""Informative (unregistered) sensitivity check: the negative control against the O1 tolerances.

The negative control resumes from a copy of the same checkpoint with the BFGS history deleted
at startup, so its first evaluation sits at the control's evaluation-2 geometry and its second
follows a history-free step. Pairing control 2-3 with negative 1-2 shows how far a real
lost-history defect lands from the tolerances. Never changes the registered reading.
"""
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\frank\sts-electrocatalyst")
sys.path.insert(0, str(ROOT / "src/dft"))
import pa_fixed_geometry_readout as r  # noqa: E402
from pa_catalyst_o1_readout import O1_TOLERANCES, XML  # noqa: E402

HERE = ROOT / "results/pa_catalyst_o1_2026-10-07"
TRIAL = HERE / "raw_mirror/trial_results"
OUT = HERE / "informative_negative.json"

control = r.parse_arm(TRIAL / "control", TRIAL / "control" / XML)["evaluations"]
negative = r.parse_arm(TRIAL / "negative", TRIAL / "negative/checkpoint_copy" / XML)["evaluations"]
rows = []
for k, (left, right) in enumerate(zip(control[1:], negative), 2):
    c = r.compare(left, right)
    rows.append({"control_evaluation": k, "negative_evaluation": k - 1, "metrics": c["metrics"],
                 "max_force_component": c["max_force_component"],
                 "ratio_to_O1": {key: c["metrics"][key] / O1_TOLERANCES[key] for key in O1_TOLERANCES},
                 "max_hubbard_trace_delta": c["max_hubbard_trace_delta"],
                 "total_magnetization_delta": c["total_magnetization_delta"]})
result = {"note": "informative sensitivity check, not a registered reading",
          "o1_tolerances": O1_TOLERANCES, "pairs": rows,
          "energies_Ry": {"control": [e["energy_Ry"] for e in control], "negative": [e["energy_Ry"] for e in negative]}}
OUT.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
for row in rows:
    print("control e%d vs negative e%d:" % (row["control_evaluation"], row["negative_evaluation"]),
          " ".join("%s=%.3e (x%.2f)" % (k, row["metrics"][k], row["ratio_to_O1"][k]) for k in O1_TOLERANCES))
