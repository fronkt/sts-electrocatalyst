"""Informative (unregistered) same-state distances with P1_C3_repeat included.

P1's controller status is FAILED (failure marker: a gfortran IEEE_INVALID_FLAG exit note on one
rank), so the registered readings exclude it and read INCOMPLETE. This re-read applies the
probe readout's own start and convergence checks to P1 and reports the pairs; it never changes
the registered reading.
"""
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\frank\sts-electrocatalyst")
sys.path.insert(0, str(ROOT / "src/dft"))
import pa_fixed_geometry_readout as r  # noqa: E402
import pa_repro_probe_readout as p  # noqa: E402

HERE = ROOT / "results/pa_repro_probe_2026-10-07"
PROBE = HERE / "raw_mirror"
DIAG = ROOT / "results/pa_fixed_geometry_diag_2026-10-05/raw_mirror"
OUT = HERE / "informative_distances.json"

dirs = {"C3_warm_1e-10": DIAG / "runs/C3_warm_1e-10", "P1_C3_repeat": PROBE / "runs/P1_C3_repeat",
        "P2_C3_repeat": PROBE / "runs/P2_C3_repeat", "D2_fresh_1e-10": DIAG / "runs/D2_fresh_1e-10"}
checks, points = {}, {}
for name, directory in dirs.items():
    arm = r.parse_arm(directory, directory / p.XML)
    evaluation = arm["evaluations"][0]
    checks[name] = {"start_valid": arm["start"]["valid"], "evaluations": len(arm["evaluations"]),
                    "status": evaluation["status"]}
    points[name] = evaluation
nodes = {"C3_warm_1e-10": p.node_of(DIAG / "groups/ladder/allocation_03_before_launch.json"),
         "P1_C3_repeat": p.node_of(PROBE / "groups/probe/allocation_01_before_launch.json"),
         "P2_C3_repeat": p.node_of(PROBE / "groups/probe/allocation_02_before_launch.json"),
         "D2_fresh_1e-10": None}
pairs = {}
for a, b in itertools.combinations(dirs, 2):
    row = p.pair(points[a], points[b])
    row["nodes"] = [nodes[a], nodes[b]]
    pairs[a + "|" + b] = row
same_state = [k for k in pairs if "D2" not in k]
s = max(pairs[k]["force_Ry_bohr"] for k in same_state)
e = max(pairs[k]["energy_Ry"] for k in same_state)
result = {"note": "informative, not a registered reading; P1_C3_repeat is excluded from PR1/PR2 by its controller "
                  "status (FAILED, failure marker)",
          "checks": checks, "nodes": nodes, "summaries": {k: r.summary(v) for k, v in points.items()},
          "same_state_max_force_Ry_bohr": s, "same_state_max_energy_Ry": e,
          "half_gate_Ry_bohr": p.HALF_GATE, "half_path_spread_Ry_bohr": pairs["C3_warm_1e-10|D2_fresh_1e-10"]["force_Ry_bohr"] / 2,
          "pairs": pairs}
OUT.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
print(json.dumps(checks))
print("%-30s %10s %10s %10s %6s %s" % ("pair", "maxdF", "dE", "trace", "div@", "where / nodes"))
for k, v in pairs.items():
    m = v["max_force_component"]
    print("%-30s %10.3e %10.3e %10.1e %6s %s%d %s %s" % (k, v["force_Ry_bohr"], v["energy_Ry"], v["max_hubbard_trace_delta"],
                                                         v["first_accuracy_divergence"], m["species"], m["atom"], m["axis"], v["nodes"]))
print("same-state s = %.3e, e = %.3e; half gate %.1e; half path spread %.3e" % (s, e, p.HALF_GATE, result["half_path_spread_Ry_bohr"]))
