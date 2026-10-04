"""Fresh offline regression, scientific verifiers and byte-pin check, writing only inside this directory.

Mirrors results/pa_catalyst_trial_2026-10-03/verify_trial_offline.py (same suites, same verifiers, same
byte-pin baseline) without writing receipts or scientific output into that or any other existing
directory.  Reuse it after the trial to prove the readout did not disturb the pinned tree.  Never
launches QE, Slurm or SSH, and refuses URL requests.
"""
import importlib.util
import json
import re
import subprocess
import sys
import unittest
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHASE = ROOT / "results/pa_catalyst_trial_2026-10-03"
FT = ROOT / "results/s2_2026-09-25/full_text"
sys.dont_write_bytecode = True

CODE_FILES = ["src/dft/pa_qe_adapter.py", "src/dft/pa_catalyst_trial.py", "tests/test_pa_qe_adapter.py",
              "tests/test_pa_catalyst_trial.py", "tests/test_pa_catalyst_watch.py",
              "anvil/89_pa_catalyst_boundary_trial.slurm",
              "results/pa_catalyst_trial_2026-10-03/source_boundary_review.md",
              "results/pa_catalyst_trial_2026-10-03/launch_spec.json",
              "results/pa_catalyst_trial_2026-10-03/replay_retained_raw.py",
              "results/pa_catalyst_trial_2026-10-03/watch_trial_readonly.py",
              "results/pa_catalyst_trial_2026-10-03/verify_trial_offline.py"]
COMPUTE_TESTS = ["tests/test_pa_qe_adapter.py", "tests/test_pa_catalyst_trial.py", "tests/test_pa_catalyst_watch.py",
                 "tests/test_pa_checked_contract.py", "tests/test_pa_restart_diagnostic.py",
                 "tests/test_pa_tiny_restart_probe.py", "tests/test_pa_tiny_raw_readout.py",
                 "tests/test_pa_tiny_readonly_watch.py", "tests/test_research_batch_checked.py",
                 "tests/test_research_batch_seeded.py", "tests/test_lowtail_batch_launch.py"]
MY_TESTS = ["results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py"]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def git(*args):
    process = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return process.stdout.strip().splitlines()


def pytest_run(tests):
    process = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests], cwd=ROOT,
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    summary = [line for line in process.stdout.splitlines() if re.search(r"\d+ passed", line)]
    return {"args": ["pytest", "-q", *tests], "returncode": process.returncode,
            "summary": summary[-1] if summary else None, "stdout_tail": process.stdout[-1500:], "stderr_tail": process.stderr[-500:]}


def main(label):
    receipt_path = HERE / ("regression_%s.json" % label)
    if receipt_path.exists():
        raise ValueError("refuse overwrite of an earlier regression receipt")
    verify = load("verify_trial_offline_readonly", PHASE / "verify_trial_offline.py")
    report = {"scope": "READOUT_PREP_REGRESSION_ONLY", "label": label, "qe_executed": False, "new_jobs_submitted": 0,
              "successful": False, "head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current")}
    try:
        report["git_status_before"] = git("status", "--porcelain")
        report["tracked_dirty_before"] = git("diff", "--name-only")
        report["before"] = verify.preserve()
        before_pins = {p: verify.digest(ROOT / p) for p in CODE_FILES}

        def offline(*args, **kwargs):
            raise RuntimeError("offline verification refuses URL requests")
        urllib.request.urlopen = offline
        sys.path.insert(0, str(FT))
        suite = unittest.TestSuite()
        for directory in [FT, FT / "download_si_review_2026-10-02", FT / "download_si_review_2026-10-03",
                          ROOT / "results/pa_integration_2026-10-03"]:
            suite.addTests(unittest.TestLoader().discover(str(directory), pattern="test_*.py"))
        evidence = unittest.TextTestRunner(verbosity=1).run(suite)
        report["evidence_tests"] = {"tests_run": evidence.testsRun, "successful": evidence.wasSuccessful(),
                                    "failures": len(evidence.failures), "errors": len(evidence.errors)}
        report["compute_tests"] = pytest_run(COMPUTE_TESTS)
        report["readout_tool_tests"] = pytest_run(MY_TESTS)
        scientific = load("readout_prep_scientific_verifier", FT / "verify_evidence_recovery.py")
        fresh = HERE / ("scientific_%s" % label)
        fresh.mkdir(exist_ok=False)
        result = scientific.main(baseline_dir=FT / "download_si_review_2026-10-03/code_validation_checked", output_dir=fresh)
        rounds = load("readout_prep_round_verifier", FT / "verify_si_round.py")
        rounds.AUDIT = fresh / "si_round_verification.json"
        rounds.main(require_audits=True)
        report["scientific_verifiers_pass"] = True
        report["registered_recovery_reads"] = result["independent_reads"]
        report["code_pins_unchanged"] = {p: verify.digest(ROOT / p) for p in CODE_FILES} == before_pins
        report["after"] = verify.preserve()
        report["git_status_after"] = git("status", "--porcelain")
        report["tracked_dirty_after"] = git("diff", "--name-only")
        report["successful"] = (evidence.wasSuccessful() and report["compute_tests"]["returncode"] == 0
                                and report["readout_tool_tests"]["returncode"] == 0 and report["code_pins_unchanged"])
    except BaseException as exc:
        report["error"] = repr(exc)
        raise
    finally:
        receipt_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("git_status_before", "git_status_after")}, indent=2))
    return report


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "run1")
