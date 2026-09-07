"""Mock only the scheduler/driver; exercise real approved-deck hash guards."""
from pathlib import Path
import os
import subprocess

import pytest

from test_hea_pilot_runner import ROOT, DIRECTORY, JOB, OTHER_JOB, _shell_path, _write, pilot

SUBMITTER = ROOT / "anvil/54_submit_hea_pilot.sh"
MANIFEST_NAME = "m_controls_2026-09-07_pilot_approved.txt"


@pytest.fixture
def submission(pilot):
    project = pilot["root"] / "project"
    _write(project / "parity/PARITY_PASS", "mock parity evidence")
    scripts = pilot["root"] / "anvil"
    scripts.mkdir()
    script = scripts / SUBMITTER.name
    script.write_bytes(SUBMITTER.read_bytes())
    (scripts / "53_hea_pilot.slurm").write_bytes((ROOT / "anvil/53_hea_pilot.slurm").read_bytes())
    _write(scripts / "pseudo_md5_preflight_2026-08-23.md", "mock evidence marker")
    for job in (JOB, OTHER_JOB):
        # Exercise pinned SHA256 against actual approved inputs, never alter originals.
        (pilot["directory"] / (job + ".in")).write_bytes((ROOT / "runs" / DIRECTORY / (job + ".in")).read_bytes())
    manifest = pilot["root"] / MANIFEST_NAME
    _write(manifest, f"# SUBMIT WITH EXCLUDE=a024,a120\n{DIRECTORY} {JOB} .in 8\n{DIRECTORY} {OTHER_JOB} .in 8")
    driver = pilot["root"] / "driver.sh"
    _write(driver, r"""
        #!/bin/bash
        set -eu
        [ "$PREFLIGHT_ONLY" = 1 ] && [ "$LOG" = /dev/stdout ] || exit 81
        printf '%s\n' "$@" > "$MOCK_DRIVER_LOG"
        exit "$MOCK_DRIVER_RC"
    """, executable=True)
    _write(pilot["prefix"] / "bin/sbatch", r"""
        #!/bin/bash
        set -eu
        printf '%s\n' "$@" > "$MOCK_SBATCH_LOG"
        echo 'Submitted batch job 123456'
    """, executable=True)
    _write(pilot["prefix"] / "bin/scontrol", r"""
        #!/bin/bash
        printf '%s\n' "$@" > "$MOCK_RELEASE_LOG"
    """, executable=True)
    pilot["env"].update(PROJECT=_shell_path(project), ACCT="mock-account", EXCLUDE="a024,a120",
        DRIVER=_shell_path(driver), MOCK_DRIVER_RC="0", MOCK_DRIVER_LOG=_shell_path(pilot["root"] / "driver.log"),
        MOCK_SBATCH_LOG=_shell_path(pilot["root"] / "sbatch.log"), MOCK_RELEASE_LOG=_shell_path(pilot["root"] / "release.log"))
    return dict(pilot, project=project, scripts=scripts, submitter=script, manifest=manifest)


def run_submission(submission, concurrency="1", **env):
    # Put temporary scheduler mocks first, as the runner does with QE. Shell text
    # has no interpolated paths; every path is a separate argument or env value.
    return subprocess.run([submission["executable"], "-c", 'export PATH="$QE_PREFIX/bin:$PATH"; exec bash "$@"',
                           "mock-submit", _shell_path(submission["submitter"]), _shell_path(submission["manifest"]), concurrency],
                          cwd=submission["root"], env=dict(submission["env"], **env), text=True,
                          capture_output=True, timeout=20,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def test_submitter_requests_exact_held_four_hour_sequential_pilot(submission):
    result = run_submission(submission)
    assert result.returncode == 0, result.stdout + result.stderr
    args = (submission["root"] / "sbatch.log").read_text().splitlines()
    for option in ("--hold", "--time=04:00:00", "--no-requeue", "--array=1-2%1", "--exclude=a024,a120"):
        assert args.count(option) == 1
    assert args[args.index("-N") + 1] == "1"
    assert args[args.index("-n") + 1] == "128"
    assert args[-1] == _shell_path(submission["scripts"] / "53_hea_pilot.slurm")
    assert not (submission["root"] / "release.log").exists()
    assert not (submission["root"] / "mpi.log").exists()
    assert (submission["root"] / "driver.log").read_text().splitlines() == [
        _shell_path(submission["manifest"]), "128", "1"]


@pytest.mark.parametrize("mutation", ["np", "concurrency", "row", "one_row", "duplicate_row", "basename",
    "parity", "pseudo_evidence", "not_licensed", "exclude_header", "exclude_node", "driver", "missing_deck", "changed_deck", "stale_output"])
def test_submitter_refuses_contract_and_inherited_preflight_failures(submission, mutation):
    env, concurrency = {}, "1"
    manifest = submission["manifest"]
    content = manifest.read_text()
    if mutation == "np": env["NP"] = "64"
    elif mutation == "concurrency": concurrency = "2"
    elif mutation == "row": _write(manifest, content.replace(JOB + " .in 8", JOB + " .in 7"))
    elif mutation == "one_row": _write(manifest, content.replace(f"{DIRECTORY} {OTHER_JOB} .in 8\n", ""))
    elif mutation == "duplicate_row": _write(manifest, content.replace(OTHER_JOB, JOB))
    elif mutation == "basename":
        replacement = manifest.with_name("other-manifest.txt")
        replacement.write_bytes(manifest.read_bytes())
        submission["manifest"] = replacement
    elif mutation == "parity": (submission["project"] / "parity/PARITY_PASS").unlink()
    elif mutation == "pseudo_evidence": (submission["scripts"] / "pseudo_md5_preflight_2026-08-23.md").unlink()
    elif mutation == "not_licensed": _write(manifest, "# NOT LICENSED\n" + content)
    elif mutation == "exclude_header": _write(manifest, content.replace("# SUBMIT WITH EXCLUDE=a024,a120\n", ""))
    elif mutation == "exclude_node": env["EXCLUDE"] = "a024"
    elif mutation == "driver": env["MOCK_DRIVER_RC"] = "17"
    elif mutation == "missing_deck": (submission["directory"] / (JOB + ".in")).unlink()
    elif mutation == "changed_deck":
        deck = submission["directory"] / (JOB + ".in")
        deck.write_bytes(deck.read_bytes() + b"! altered approved input\n")
    elif mutation == "stale_output": _write(submission["directory"] / (JOB + ".out"), "incomplete retained run")
    result = run_submission(submission, concurrency, **env)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "REFUSE:" in result.stdout + result.stderr
    assert not (submission["root"] / "sbatch.log").exists()
    assert not (submission["root"] / "release.log").exists()
    assert not (submission["root"] / "mpi.log").exists()
    assert (submission["root"] / "driver.log").exists() == (mutation == "driver")
