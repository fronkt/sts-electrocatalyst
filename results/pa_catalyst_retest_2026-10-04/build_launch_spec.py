"""Write launch_spec.json for the corrected one-boundary re-test from the files it pins (refuses to overwrite).

Same physical inputs and resource shape as the approved 2026-10-03 trial (deck, pw.x, mpirun, five UPFs, four-file density
seed, one regular whole 128-core node, 16 h, <= 2,048 CPU SU, <= 200 GiB, <= 6 sequential calls each <= 2 h, no retry);
new schema, date, isolated remote parent, corrected dependency pins, new source review and the real-control PREFLIGHT replay.
Remote pins that are not repository files (pw.x, mpirun, UPFs, seed) are copied unchanged from the original spec.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = HERE / "launch_spec.json"
if TARGET.exists():
    raise SystemExit("launch_spec.json exists; refusing to overwrite")

ORIGINAL = json.loads((ROOT / "results/pa_catalyst_trial_2026-10-03/launch_spec.json").read_text(encoding="utf-8"))
ORIGINAL_SHA256 = "4bed5002a88857515940230b20ad59e6adc345e29d8567d5b9c5f5511b0b28a2"
assert hashlib.sha256((ROOT / "results/pa_catalyst_trial_2026-10-03/launch_spec.json").read_bytes()).hexdigest() == ORIGINAL_SHA256

OLD_PARENT = "/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03"
PARENT = "/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04"
FIXTURES = ROOT / "tests/fixtures/qe75_real"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def moved(entry):
    return {"path": entry["path"].replace(OLD_PARENT, PARENT), "sha256": entry["sha256"]}


import sys  # noqa: E402

sys.path.insert(0, str(ROOT / "src/dft"))
import pa_catalyst_retest as controller  # noqa: E402

spec = {
    "schema": "pa-catalyst-retest-v1",
    "date": "2026-10-04",
    "target": ORIGINAL["target"],
    "predecessor": {
        "slurm_job": "21034683", "slurm_state": "FAILED 3:0", "scientific_status": "INCONCLUSIVE",
        "charged_cpu_su": 102.8622, "spec_sha256": ORIGINAL_SHA256,
        "cause": "pa_qe_adapter.py:626 required an XML element lda_plus_u that QE 7.5 never writes",
        "readout": "docs/research/pa-catalyst-trial-readout-2026-10-04.md",
    },
    "decision_ref": "docs/research/pa-catalyst-retest-2026-10-04.md (decision of record, Frank, 2026-10-04: corrected re-test)",
    "source_deck": moved(ORIGINAL["source_deck"]),
    "pw_x": ORIGINAL["pw_x"],
    "mpirun": ORIGINAL["mpirun"],
    "upfs": ORIGINAL["upfs"],
    "dependencies": [
        {"path": PARENT + "/src/dft/pa_catalyst_retest.py", "sha256": sha(ROOT / "src/dft/pa_catalyst_retest.py")},
        {"path": PARENT + "/src/dft/pa_qe_adapter_v2.py", "sha256": sha(ROOT / "src/dft/pa_qe_adapter_v2.py")},
        {"path": PARENT + "/src/dft/pa_checked_contract.py", "sha256": sha(ROOT / "src/dft/pa_checked_contract.py")},
        {"path": PARENT + "/anvil/90_pa_catalyst_retest.slurm", "sha256": sha(ROOT / "anvil/90_pa_catalyst_retest.slurm")},
    ],
    "source_review": {"path": PARENT + "/results/pa_catalyst_retest_2026-10-04/source_xml_input_review.md",
                      "sha256": sha(HERE / "source_xml_input_review.md")},
    "preflight_replay": {
        "root": PARENT + "/tests/fixtures/qe75_real",
        "logged_upf_dir": "/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03/trial_results/common_pseudo/",
        "files": [{"path": rel, "sha256": sha(FIXTURES / rel)} for rel in sorted(controller.REPLAY_FILES)],
        "expected": controller.REPLAY_EXPECTED,
    },
    "initial_seed": ORIGINAL["initial_seed"],
    "trial_parent": PARENT,
    "trial_root": PARENT + "/trial_results",
    "allocation": ORIGINAL["allocation"],
    "caps": ORIGINAL["caps"],
    "parallel_shape": ORIGINAL["parallel_shape"],
    "optional_negative_control": ORIGINAL["optional_negative_control"],
    "production_accepted": False,
}
# The spec holds Linux paths; validate them with POSIX path semantics (Path('/anvil/..') is not absolute on Windows).
import pathlib  # noqa: E402

_windows_path = controller.Path
controller.Path = pathlib.PurePosixPath
try:
    controller.validate_spec(spec)
finally:
    controller.Path = _windows_path
TARGET.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"spec_sha256": sha(TARGET), "dependencies": {Path(d["path"]).name: d["sha256"][:12] for d in spec["dependencies"]}}, indent=1))
