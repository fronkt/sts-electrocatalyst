"""Record the exact bytes of everything the re-test pins, plus the frozen artifacts it must not disturb (refuses to overwrite)."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = HERE / "pins.json"
if TARGET.exists():
    raise SystemExit("pins.json exists; refusing to overwrite")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, encoding="utf-8").stdout.strip()


corrected = ["src/dft/pa_qe_adapter_v2.py", "src/dft/pa_catalyst_retest.py", "src/dft/pa_checked_contract.py",
             "anvil/90_pa_catalyst_retest.slurm", "tests/test_pa_qe_adapter_v2.py", "tests/test_pa_qe_adapter_v2_real.py",
             "tests/test_pa_catalyst_retest.py", "tests/test_pa_catalyst_retest_scripts.py", "tests/qe75_real_fixtures.py",
             "tests/fixtures/qe75_real/manifest.json",
             "results/pa_catalyst_retest_2026-10-04/launch_spec.json", "results/pa_catalyst_retest_2026-10-04/source_xml_input_review.md"]
frozen = {
    "launch_adapter_original (retained byte-identical copy)": "results/pa_catalyst_trial_readout_2026-10-04/dryrun/scratch/pa_qe_adapter_FROZEN_COPY.py",
    "pa_catalyst_trial.py": "src/dft/pa_catalyst_trial.py",
    "89_pa_catalyst_boundary_trial.slurm": "anvil/89_pa_catalyst_boundary_trial.slurm",
    "first trial launch_spec.json": "results/pa_catalyst_trial_2026-10-03/launch_spec.json",
    "first trial source_boundary_review.md": "results/pa_catalyst_trial_2026-10-03/source_boundary_review.md",
    "first trial baseline.json (9,816 tracked + 21 unrelated pins)": "results/pa_catalyst_trial_2026-10-03/baseline.json",
}
report = {"head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
          "corrected": {rel: {"sha256": sha(ROOT / rel), "bytes": (ROOT / rel).stat().st_size} for rel in corrected},
          "frozen_first_trial": {label: {"path": rel, "sha256": sha(ROOT / rel)} for label, rel in frozen.items()},
          "worktree_src_dft_pa_qe_adapter_py": {"sha256": sha(ROOT / "src/dft/pa_qe_adapter.py"),
                                                "note": "equals the launch pin only if no other session has repaired it in place"}}
TARGET.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({k: (v if k in ("head", "branch") else "...") for k, v in report.items()}))
