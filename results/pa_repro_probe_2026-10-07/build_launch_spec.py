"""Write the dated launch spec for the same-state reproducibility probe (offline; LF bytes).

Executable, UPF and helper pins are copied from the launched fixed-geometry diagnostic
spec; the start tree is C2's outdir, pinned by the digest that C3's verified copy
recorded on 2026-10-06 (raw_mirror/runs/C3_warm_1e-10/setup_receipt.json).
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "results/pa_repro_probe_2026-10-07"
DIAG = ROOT / "results/pa_fixed_geometry_diag_2026-10-05"
BASE = "/anvil/projects/x-che260157/sts_pa_repro_probe_2026-10-07"
PARENT = json.loads((DIAG / "launch_spec.json").read_text(encoding="utf-8"))
C3_SETUP = json.loads((DIAG / "raw_mirror/runs/C3_warm_1e-10/setup_receipt.json").read_text(encoding="utf-8"))
DECKS = json.loads((ROOT / "runs/hea/pa_repro_probe_2026-10-07/decks/deck_receipt.json").read_text(encoding="utf-8"))
C2_OUTDIR = PARENT["base"] + "/runs/C2_warm_1e-8/outdir"


def sha(path: Path) -> str:
    data = path.read_bytes()
    if b"\r" in data:
        raise SystemExit(f"{path} is not LF")
    return hashlib.sha256(data).hexdigest()


def call(name):
    return {"name": name, "start": "checkpoint", "target_cycle": None,
            "deck": {"path": f"{BASE}/decks/{name}.in", "sha256": DECKS["decks"][name]["sha256"]}}


assert C3_SETUP["source_root"] == C2_OUTDIR and C3_SETUP["files"] == 282
assert sha(ROOT / "src/dft/pa_catalyst_retest.py") == PARENT["helper"]["sha256"]
spec = {
    "schema": "pa-fixed-geometry-diag-v1",
    "date": "2026-10-07",
    "target": PARENT["target"],
    "geometry": PARENT["geometry"],
    "decision_ref": "docs/research/pa-repro-probe-2026-10-07.md (Frank, 2026-10-07: \"Continue then. Do the probe.\")",
    "base": BASE,
    "controller": {"path": f"{BASE}/src/dft/pa_fixed_geometry_diag.py", "sha256": sha(ROOT / "src/dft/pa_fixed_geometry_diag.py")},
    "helper": {"path": f"{BASE}/src/dft/pa_catalyst_retest.py", "sha256": PARENT["helper"]["sha256"]},
    "slurm": {"path": f"{BASE}/anvil/92_pa_repro_probe.slurm", "sha256": sha(ROOT / "anvil/92_pa_repro_probe.slurm")},
    "pw_x": PARENT["pw_x"],
    "mpirun": PARENT["mpirun"],
    "upfs": PARENT["upfs"],
    "checkpoint": {"outdir": C2_OUTDIR, "tree_sha256": C3_SETUP["tree_sha256"],
                   "files": C3_SETUP["files"], "bytes": C3_SETUP["bytes"],
                   "meaning": "start state of C3: C2_warm_1e-8 outdir as copied by C3 on 2026-10-06"},
    "parallel_shape": PARENT["parallel_shape"],
    "per_call_seconds": 7200,
    "groups": {
        "probe": {"time_limit_seconds": 16200, "time_limit": "04:30:00", "max_cpu_su": 576,
                  "calls": [call("P1_C3_repeat"), call("P2_C3_repeat")]},
    },
    "hard_ceiling_cpu_su": 576,
    "estimate_cpu_su": {"probe": [165, 260], "total": [165, 260]},
    "estimate_basis": "C3_warm_1e-10 measured 2026-10-06: 2,321 s call wall (31 iterations to 9.1e-11 Ry) from the same start tree; copy and re-hash of the 15.2 GB tree about 40 s; two calls plus the start-tree digest is about 4,800 s = 170 SU; the upper end allows up to 50 iterations per call",
    "production_accepted": False,
    "automatic_retry": False,
    "requeue": False,
}
out = HERE / "launch_spec.json"
out.write_bytes((json.dumps(spec, indent=2) + "\n").encode("utf-8"))
print(sha(out))
