"""Informative (unregistered) pairwise distances among the finished G2 evaluations."""
import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\frank\sts-electrocatalyst")
sys.path.insert(0, str(ROOT / "src/dft"))
import pa_fixed_geometry_readout as r  # noqa: E402

XML = "outdir/slab_c5low__pa_boundary.save/data-file-schema.xml"
TRIAL = ROOT / "results/pa_catalyst_retest_readout_2026-10-05/raw_mirror/trial_results"
RUNS = ROOT / "results/pa_fixed_geometry_diag_2026-10-05/raw_mirror/runs"
OUT = RUNS.parents[1] / "informative_distances.json"

control = r.parse_arm(TRIAL / "control", TRIAL / "control" / XML)
resumed = r.parse_arm(TRIAL / "resumed", TRIAL / "resumed/checkpoint_copy" / XML)
arms = {name: r.parse_arm(RUNS / name, RUNS / name / XML) for name in
        ("A_replay", "B_ethr", "C1_warm_1e-6", "C2_warm_1e-8", "C3_warm_1e-10", "D1_fresh_1e-8", "D2_fresh_1e-10")}
points = {"control_e2": control["evaluations"][1], "resumed_e2": resumed["evaluations"][0],
          "A_e2": arms["A_replay"]["evaluations"][0], "B_e2": arms["B_ethr"]["evaluations"][0],
          "C1": arms["C1_warm_1e-6"]["evaluations"][0], "C2": arms["C2_warm_1e-8"]["evaluations"][0], "C3": arms["C3_warm_1e-10"]["evaluations"][0],
          "D1": arms["D1_fresh_1e-8"]["evaluations"][0], "D2": arms["D2_fresh_1e-10"]["evaluations"][0]}
names = list(points)
matrix = {}
for i, a in enumerate(names):
    for b in names[i + 1:]:
        c = r.compare(points[a], points[b])
        matrix[a + "|" + b] = {"force": c["metrics"]["force_Ry_bohr"], "energy": c["metrics"]["energy_Ry"],
                               "position": c["metrics"]["position_bohr"],
                               "at": "%s%d %s" % (c["max_force_component"]["species"], c["max_force_component"]["atom"],
                                                   c["max_force_component"]["axis"]),
                               "trace": c["max_hubbard_trace_delta"], "mag": c["total_magnetization_delta"]}
result = {"note": "informative, not a registered reading; A_replay is excluded from R1 by the controller status",
          "summaries": {k: r.summary(v) for k, v in points.items()}, "pairs": matrix}
OUT.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
print("%-22s %10s %10s %s" % ("pair", "maxdF", "dE", "where"))
for k, v in matrix.items():
    print("%-22s %10.3e %10.3e %s pos=%.1e" % (k, v["force"], v["energy"], v["at"], v["position"]))
