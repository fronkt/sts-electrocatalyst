"""Write the dated launch spec for the fixed-geometry diagnostic (offline; LF bytes).

Pins come from the committed decks/controller/helper and from the launched retest
spec (pw.x, mpirun, UPF contents); the checkpoint digest is the terminal readout's
reconstructed candidate tree digest.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "results/pa_fixed_geometry_diag_2026-10-05"
BASE = "/anvil/projects/x-che260157/sts_pa_fixed_geometry_diag_2026-10-05"
TRIAL_OUT = "/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04/trial_results"
RETEST = json.loads((ROOT / "results/pa_catalyst_retest_readout_2026-10-05/launch_snapshot/launch_spec.json").read_text(encoding="utf-8"))
DECKS = json.loads((ROOT / "runs/hea/pa_fixed_geometry_diag_2026-10-05/decks/deck_receipt.json").read_text(encoding="utf-8"))
CHECKPOINT_TREE = "dc3637bce66f8c9d85bd7d29f77af40810302650b8eed1f02bdf9de83c98a32c"
HELPER_SHA = "b1c49d2d06c93fed4438d46491d8a01532f05cd6d8b6adfed90ca9689a65baf1"


def sha(path: Path) -> str:
    data = path.read_bytes()
    if b"\r" in data:
        raise SystemExit(f"{path} is not LF")
    return hashlib.sha256(data).hexdigest()


def deck(name: str) -> dict:
    return {"path": f"{BASE}/decks/{name}.in", "sha256": DECKS["decks"][name]["sha256"]}


def call(name, start, cycle):
    return {"name": name, "start": start, "target_cycle": cycle, "deck": deck(name)}


assert sha(ROOT / "src/dft/pa_catalyst_retest.py") == HELPER_SHA
spec = {
    "schema": "pa-fixed-geometry-diag-v1",
    "date": "2026-10-05",
    "target": "Cu8Cr23Mn35Co34__s20_site2",
    "geometry": "G2 = first resumed evaluation of job 21075231 (candidate checkpoint XML output positions)",
    "decision_ref": "docs/research/pa-fixed-geometry-diagnostic-2026-10-05.md (Frank, 2026-10-05: \"I approve the next DFT run\")",
    "base": BASE,
    "controller": {"path": f"{BASE}/src/dft/pa_fixed_geometry_diag.py", "sha256": sha(ROOT / "src/dft/pa_fixed_geometry_diag.py")},
    "helper": {"path": f"{BASE}/src/dft/pa_catalyst_retest.py", "sha256": HELPER_SHA},
    "slurm": {"path": f"{BASE}/anvil/91_pa_fixed_geometry_diag.slurm", "sha256": sha(ROOT / "anvil/91_pa_fixed_geometry_diag.slurm")},
    "pw_x": RETEST["pw_x"],
    "mpirun": RETEST["mpirun"],
    "upfs": [{"path": f"{TRIAL_OUT}/common_pseudo/{Path(pin['path']).name}", "sha256": pin["sha256"]} for pin in RETEST["upfs"]],
    "checkpoint": {"outdir": f"{TRIAL_OUT}/candidate_immutable/outdir", "tree_sha256": CHECKPOINT_TREE,
                   "files": 390, "bytes": 15225129073},
    "parallel_shape": {"nprocs": 128, "npool": 8, "ndiag": 16, "nthreads": 1},
    "per_call_seconds": 7200,
    "groups": {
        "replay": {"time_limit_seconds": 16200, "time_limit": "04:30:00", "max_cpu_su": 576,
                   "calls": [call("A_replay", "checkpoint", 2), call("B_ethr", "checkpoint", 3)]},
        "ladder": {"time_limit_seconds": 24300, "time_limit": "06:45:00", "max_cpu_su": 864,
                   "calls": [call("C1_warm_1e-6", "checkpoint", None), call("C2_warm_1e-8", "C1_warm_1e-6", None),
                             call("C3_warm_1e-10", "C2_warm_1e-8", None)]},
        "fresh": {"time_limit_seconds": 15600, "time_limit": "04:20:00", "max_cpu_su": 555,
                  "calls": [call("D1_fresh_1e-8", None, None), call("D2_fresh_1e-10", "D1_fresh_1e-8", None)]},
    },
    "hard_ceiling_cpu_su": 576 + 864 + 555,
    "estimate_cpu_su": {"replay": [130, 170], "ladder": [270, 370], "fresh": [245, 445], "total": [645, 985]},
    "estimate_basis": "job 21075231 measured: resumed evaluation 2 = 898.5 s CPU, resumed call (evaluations 2+3) = 2,549 s wall, fresh SCF = 65 s/iteration (50 iterations, 3,353 s), forces 63 s; tight-rung iteration counts extrapolated from the evaluation-3 residual tail (about 0.84 per iteration) and the fresh tail (about 0.77 per iteration)",
    "production_accepted": False,
    "automatic_retry": False,
    "requeue": False,
}
out = HERE / "launch_spec.json"
out.write_bytes((json.dumps(spec, indent=2) + "\n").encode("utf-8"))
print(sha(out))
