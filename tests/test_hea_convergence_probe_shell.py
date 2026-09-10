"""Actual Bash lifecycle with fake MPI/Slurm and tiny independent checkpoints."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from test_hea_convergence_probe import ROOT, batch, iteration, STARTUP
from test_hea_followup_shell import _fake_scf, _fake_projection
from test_hea_pilot_runner import _bash, _shell_path, _write
from dft import hea_convergence_probe_guard as guard

RUNNER = "68_hea_convergence_probe.slurm"
SUBMITTER = "69_submit_hea_convergence_probe.sh"


@pytest.fixture
def probes(batch, tmp_path):
    project = tmp_path / "project"
    staged = project / "sts"
    for name in ("runs", "results"):
        shutil.copytree(tmp_path / name, staged / name)
    spec_path = staged / "results/hea_convergence_probe_2026-09-10/launch_spec.json"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(batch["spec_path"], spec_path)
    directory = staged / "runs" / guard.DIRECTORY
    manifest = staged / guard.MANIFEST
    qe = tmp_path / "qe"
    payloads = tmp_path / "payloads"
    paths = {"SPEC": spec_path, "MANIFEST": manifest}
    for variable, filename in (("GUARD", "hea_convergence_probe_guard.py"),
                               ("FROZEN", "hea_numerical_guard.py"),
                               ("QC", "hea_followup_qc.py"), ("FORCE", "hea_force_audit.py")):
        target = staged / "src/dft" / filename
        text = (ROOT / "src/dft" / filename).read_text(encoding="utf-8")
        if variable == "GUARD":
            text, count = re.subn(r'(?m)^SOURCE_SPEC_SHA256 = "[a-f0-9]+"$',
                'SOURCE_SPEC_SHA256 = "' + guard.SOURCE_SPEC_SHA256 + '"', text)
            assert count == 1
        _write(target, text)
        paths[variable] = target
    for job in batch["spec"]["jobs"]:
        deck = (directory / (job["job"] + ".in")).read_text()
        converged = STARTUP + "".join(iteration(i, 1e-7 if i == 7 else 1e-4) for i in range(1, 8)) + _fake_scf(deck)
        _write(payloads / (job["job"] + ".success"), converged)
    capped = STARTUP + "".join(iteration(i) for i in range(1, 61))
    capped += "convergence NOT achieved after 60 iterations\nJOB DONE.\n"
    _write(payloads / "capped", capped)
    _write(payloads / "projection", _fake_projection())
    _write(qe / "bin/mpirun", r"""
        #!/bin/bash
        set -eu
        printf '%s\n' "$*" >> "$MOCK_MPI_LOG"
        [ "$1" = --oversubscribe ] && shift
        [ "$1" = -np ] && [ "$2" = 128 ] && shift 2
        exec "$@"
    """, executable=True)
    _write(qe / "bin/pw.x", r"""
        #!/bin/bash
        set -eu
        [ "$1" = -nk ] && [ "$2" = 8 ] && [ "$3" = -in ]
        inp=$4
        grep -q '^  electron_maxstep = 60$' "$inp"
        grep -q '^  max_seconds = 3300$' "$inp"
        prefix=$(sed -n "s/^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        scratch=$(sed -n "s/^[[:space:]]*outdir[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        save="$scratch/$prefix.save"
        [ "$(cat "$save/charge-density.hdf5")" = "$prefix:charge-density.hdf5" ]
        printf '%s\n' 'new density after probe' > "$save/charge-density.hdf5"
        printf '%s\n' 'irreplaceable partial wavefunction' > "$scratch/partial.wfc"
        job=${inp%.run.in}
        if [ "$MOCK_MODE" = capped ]; then
          cat "$MOCK_PAYLOADS/capped"
          exit 0
        fi
        for spin in up dw; do
          for k in 1 2 3 4 5 6 7 8; do
            printf '%s\n' 'retained wavefunction' > "$save/wfc$spin$k.hdf5"
          done
        done
        cat "$MOCK_PAYLOADS/$job.success"
        if [ "$MOCK_MODE" = ieee ]; then echo IEEE_INVALID_FLAG >&2; fi
    """, executable=True)
    _write(qe / "bin/projwfc.x", r"""
        #!/bin/bash
        set -eu
        cat "$MOCK_PAYLOADS/projection"
    """, executable=True)
    _write(qe / "bin/sbatch", r"""
        #!/bin/bash
        printf '%s\n' "$@" > "$MOCK_SBATCH_LOG"
        echo 'Submitted batch job 123456'
    """, executable=True)
    for variable, name in (("MPI", "mpirun"), ("PW", "pw.x"), ("PROJECTION", "projwfc.x")):
        paths[variable] = qe / "bin" / name
    scripts = staged / "anvil"
    for filename in (RUNNER, SUBMITTER):
        text = (ROOT / "anvil" / filename).read_text(encoding="utf-8")
        for variable, target in paths.items():
            pattern = r'(?m)^(check_hash "\$' + variable + r'" )\S+$'
            text, count = re.subn(pattern, lambda m: m[1] + hashlib.sha256(target.read_bytes()).hexdigest(), text)
            assert count == (1 if filename == RUNNER or variable in ("SPEC", "MANIFEST", "GUARD") else 0)
        text, count = re.subn(r"(?m)^PYTHON=.*$", lambda _: 'PYTHON="' + _shell_path(Path(sys.executable)) + '"', text)
        assert count == 1
        _write(scripts / filename, text)
    _write(scripts / "pseudo_md5_preflight_2026-08-23.md", "test pseudo evidence")
    _write(project / "parity/PARITY_PASS", "test parity")
    driver = project / "queue_r1.sh"
    _write(driver, r"""
        #!/bin/bash
        set -eu
        [ "$PREFLIGHT_ONLY" = 1 ] && [ "$LOG" = /dev/stdout ]
        printf '%s\n' "$@" > "$MOCK_PREFLIGHT_LOG"
    """, executable=True)
    exclude = next(line.split("=", 1)[1] for line in manifest.read_text().splitlines()
                   if line.startswith("# SUBMIT WITH EXCLUDE="))
    env = dict(os.environ, PROJECT=_shell_path(project), RUNS=_shell_path(staged / "runs"),
               MANIFEST=_shell_path(manifest), QE_PREFIX=_shell_path(qe),
               PSEUDO_DIR=guard.frozen.PSEUDO_DIRECTORY, ACCT="test-account", EXCLUDE=exclude,
               DRIVER=_shell_path(driver), NP="128", AFTERANY="345678", SLURM_ARRAY_TASK_ID="1",
               MOCK_MODE="success", MOCK_PAYLOADS=_shell_path(payloads),
               MOCK_MPI_LOG=_shell_path(tmp_path / "mpi.log"),
               MOCK_SBATCH_LOG=_shell_path(tmp_path / "sbatch.log"),
               MOCK_PREFLIGHT_LOG=_shell_path(tmp_path / "preflight.log"))
    return dict(root=tmp_path, staged=staged, directory=directory, manifest=manifest,
                scripts=scripts, spec=batch["spec"], env=env)


def run(case, submit=False, concurrency="1", **env):
    args = [_shell_path(case["scripts"] / (SUBMITTER if submit else RUNNER))]
    if submit:
        args += [_shell_path(case["manifest"]), concurrency]
    return subprocess.run([_bash(), "-c", 'export PATH="$QE_PREFIX/bin:$PATH"; exec bash "$@"',
                           "mock-probe", *args], cwd=case["root"], env=dict(case["env"], **env),
                          text=True, capture_output=True, timeout=30,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def result_record(case, row=1):
    job = case["spec"]["jobs"][row-1]
    return json.loads((case["directory"] / (job["job"] + ".probe.json")).read_text())


def test_runner_success_and_completed_sibling_allow_serial_progress(probes):
    result = run(probes)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result_record(probes)["scientific_status"] == "COMPLETE"
    first = probes["spec"]["jobs"][0]
    output = probes["directory"] / (first["job"] + ".out")
    before = output.read_bytes()
    result = run(probes, SLURM_ARRAY_TASK_ID="2")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result_record(probes, 2)["scientific_status"] == "COMPLETE"
    assert output.read_bytes() == before
    assert run(probes).returncode != 0
    assert output.read_bytes() == before


@pytest.mark.parametrize("mode,status", [("capped", "CAPPED_NONCONVERGENCE"), ("ieee", "OTHER_REJECTION")])
def test_failed_scf_never_runs_projection_or_deletes_checkpoint(probes, mode, status):
    result = run(probes, MOCK_MODE=mode)
    assert result.returncode == 16, result.stdout + result.stderr
    record = result_record(probes)
    assert record["scientific_status"] == "REJECTED" and record["diagnostic_status"] == status
    assert len((probes["root"] / "mpi.log").read_text().splitlines()) == 1
    job = probes["spec"]["jobs"][0]
    scratch = probes["directory"] / ("tmp_" + job["job"])
    assert (scratch / "partial.wfc").read_text().strip() == "irreplaceable partial wavefunction"
    assert (scratch / (job["prefix"] + ".save") / "charge-density.hdf5").read_text().strip() == "new density after probe"
    assert not (probes["directory"] / (job["job"] + ".projwfc.out")).exists()
    if mode == "capped":
        assert record["complete_iterations"] == 60


def test_submitter_holds_four_one_hour_serial_tasks_behind_explicit_predecessor(probes):
    result = run(probes, submit=True)
    assert result.returncode == 0, result.stdout + result.stderr
    args = (probes["root"] / "sbatch.log").read_text().splitlines()
    for item in ("--hold", "--time=01:00:00", "--mem=237G", "--no-requeue", "--array=1-4%1",
                 "--dependency=afterany:345678", "--job-name=hea-convergence-probe"):
        assert args.count(item) == 1
    assert args[args.index("-n") + 1] == "128"
    assert "512 core-h" in result.stdout
    assert not (probes["root"] / "mpi.log").exists()


@pytest.mark.parametrize("overrides", [{"AFTERANY": ""}, {"AFTERANY": "345678;false"},
                                       {"AFTERANY": "-1"}, {"NP": "64"}])
def test_bad_dependency_or_rank_request_never_reaches_scheduler(probes, overrides):
    result = run(probes, submit=True, **overrides)
    assert result.returncode != 0
    assert not (probes["root"] / "sbatch.log").exists()
    assert not (probes["root"] / "mpi.log").exists()


def test_concurrency_expansion_refused(probes):
    assert run(probes, submit=True, concurrency="2").returncode != 0
    assert not (probes["root"] / "sbatch.log").exists()
