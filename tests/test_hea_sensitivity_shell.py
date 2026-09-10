"""Actual numerical shells/helpers with tiny checkpoints and fake MPI/Slurm."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

from dft import hea_sensitivity_guard as guard
from test_hea_followup_shell import _fake_scf, _fake_projection, _pin_script
from test_hea_numerical_guard import snapshot, write_json
from test_hea_pilot_runner import ROOT, _bash, _shell_path, _write

SPEC_REL = Path("results/hea_sensitivity_2026-09-09/launch_spec.json")
RUNNER = "62_hea_sensitivity.slurm"
SUBMITTER = "63_submit_hea_sensitivity.sh"


@pytest.fixture
def batch(tmp_path):
    project, qe = tmp_path / "project", tmp_path / "qe"
    staged = project / "sts"
    runs = staged / "runs"
    directory = runs / guard.DIRECTORY
    directory.mkdir(parents=True)
    spec = json.loads((ROOT / SPEC_REL).read_text(encoding="utf-8"))
    inventory = json.loads((ROOT / guard.INVENTORY).read_text(encoding="utf-8"))
    payloads = tmp_path / "payloads"
    for job in spec["jobs"]:
        deck = directory / (job["job"] + ".in")
        deck.write_bytes((ROOT / "runs" / guard.DIRECTORY / deck.name).read_bytes())
        _write(payloads / (job["prefix"] + ".scf"), _fake_scf(deck.read_text(encoding="utf-8")))
    # Re-pin small mock source bytes only in this independent temporary workspace.
    for checkpoint in inventory["checkpoints"]:
        for entry in checkpoint["files"]:
            raw = ((ROOT / checkpoint["source_xml"]).read_bytes() if entry["path"] == "data-file-schema.xml" else (checkpoint["prefix"] + ":" + entry["path"] + "\n").encode())
            member = runs / checkpoint["dir"] / entry["path"]
            member.parent.mkdir(parents=True, exist_ok=True)
            member.write_bytes(raw)
            entry["size_bytes"] = len(raw)
            entry["sha256"] = hashlib.sha256(raw).hexdigest()
    for checkpoint in inventory["checkpoints"]:
        names = [checkpoint["source_xml"], checkpoint["source_input"]]
        names += [checkpoint["source_input"].replace(".run.in", suffix) for suffix in (".out", ".projwfc.out", ".qc.json")]
        for name in names:
            target = staged / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
    inventory_path = staged / guard.INVENTORY
    write_json(inventory_path, inventory)
    spec["source_checkpoints_sha256"] = hashlib.sha256(inventory_path.read_bytes()).hexdigest()
    spec_path = staged / SPEC_REL
    write_json(spec_path, spec)
    manifest = staged / guard.MANIFEST
    manifest.write_bytes((ROOT / guard.MANIFEST).read_bytes())
    rows = [f"{j['dir']} {j['job']} .in 8" for j in spec["jobs"]]
    Path(str(manifest) + ".lines").write_bytes(("\n".join(rows) + "\n").encode())
    _write(payloads / "projection.complete", _fake_projection())
    _write(payloads / "projection.partial", _fake_projection(74))
    paths = {"SPEC": spec_path}
    for variable, name in (("GUARD", "hea_sensitivity_guard.py"), ("COMMON_GUARD", "hea_numerical_guard.py"), ("QC", "hea_followup_qc.py"),
                           ("FORCE_AUDIT", "hea_force_audit.py")):
        target = staged / "src/dft" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / "src/dft" / name).read_bytes())
        paths[variable] = target
    scripts = staged / "anvil"
    scripts.mkdir()
    _write(scripts / "pseudo_md5_preflight_2026-08-23.md", "mock evidence")
    _write(project / "parity/PARITY_PASS", "mock parity")
    _write(qe / "bin/mpirun", r"""
        #!/bin/bash
        set -eu
        printf '%s\n' "$*" >> "$MOCK_MPI_LOG"
        while [ "$#" -gt 0 ]; do
          case "$1" in
            --oversubscribe) shift ;;
            -np|-n) shift 2 ;;
            pw.x|projwfc.x) exec "$@" ;;
            *) exit 97 ;;
          esac
        done
        exit 98
    """, executable=True)
    _write(qe / "bin/pw.x", r"""
        #!/bin/bash
        set -eu
        inp=''
        while [ "$#" -gt 0 ]; do
          case "$1" in -in) inp=$2; shift 2 ;; -nk) shift 2 ;; *) exit 96 ;; esac
        done
        prefix=$(sed -n "s/^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        scratch=$(sed -n "s/^[[:space:]]*outdir[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        wfc=$(sed -n "s/^[[:space:]]*startingwfc[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        [ "$(cat "$scratch/$prefix.save/charge-density.hdf5")" = "$prefix:charge-density.hdf5" ] || exit 92
        if [ "$wfc" = file ]; then
          [ "$(cat "$scratch/$prefix.save/wfcup8.hdf5")" = "$prefix:wfcup8.hdf5" ] || exit 91
        fi
        printf '%s\n' 'new density after SCF' > "$scratch/$prefix.save/charge-density.hdf5"
        for spin in up dw; do
          for k in 1 2 3 4 5 6 7 8; do
            printf '%s\n' 'new retained wavefunction' > "$scratch/$prefix.save/wfc${spin}${k}.hdf5"
          done
        done
        if [ "$MOCK_STARTUP" != missing_density ]; then
          echo 'The initial density is read from file'
        fi
        if [ "$wfc" = file ]; then
          echo 'Starting wfcs from file'
        else
          echo 'Starting wfcs are  224 randomized atomic wfcs'
        fi
        if [ "$MOCK_STARTUP" = fallback ]; then echo 'Cannot read wfcs: recomputing them from scratch'; fi
        if [ "$MOCK_SCF" = fail ]; then
          echo 'convergence NOT achieved after 300 iterations'
          echo 'JOB DONE.'
          exit 0
        fi
        cat "$MOCK_PAYLOADS/$prefix.scf"
    """, executable=True)
    _write(qe / "bin/projwfc.x", r"""
        #!/bin/bash
        set -eu
        cat "$MOCK_PAYLOADS/projection.$MOCK_PROJECTION"
    """, executable=True)
    _write(qe / "bin/sbatch", r"""
        #!/bin/bash
        printf '%s\n' "$@" > "$MOCK_SBATCH_LOG"
        echo 'Submitted batch job 123456'
    """, executable=True)
    _write(qe / "bin/scontrol", r"""
        #!/bin/bash
        printf '%s\n' "$@" > "$MOCK_RELEASE_LOG"
    """, executable=True)
    _write(qe / "bin/seff", "#!/bin/bash\nexit 0", executable=True)
    driver = project / "queue_r1.sh"
    _write(driver, r"""
        #!/bin/bash
        set -eu
        [ "$PREFLIGHT_ONLY" = 1 ] && [ "$LOG" = /dev/stdout ] || exit 81
        [ "$(grep -c '^# NP=128 NCONC=1$' "$1")" = 1 ] || exit 82
        printf '%s\n' "$@" > "$MOCK_DRIVER_LOG"
    """, executable=True)
    for variable, name in (("PW_BIN", "pw.x"), ("PROJ_BIN", "projwfc.x"), ("MPI_BIN", "mpirun")):
        paths[variable] = qe / "bin" / name
    for name in (RUNNER, SUBMITTER):
        _pin_script(ROOT / "anvil" / name, scripts / name, paths)
    exclude = next(line.split("=", 1)[1] for line in manifest.read_text().splitlines()
                   if line.startswith("# SUBMIT WITH EXCLUDE="))
    env = os.environ.copy()
    env.update(PROJECT=_shell_path(project), MANIFEST=_shell_path(manifest), RUNS=_shell_path(runs),
               QE_PREFIX=_shell_path(qe), PSEUDO_DIR=guard.base.PSEUDO_DIRECTORY, ACCT="mock", EXCLUDE=exclude,
               DRIVER=_shell_path(driver), NP="128", SLURM_ARRAY_TASK_ID="1", SLURM_JOB_ID="123456",
               SLURM_CPUS_ON_NODE="128", MOCK_PAYLOADS=_shell_path(payloads),
               MOCK_MPI_LOG=_shell_path(tmp_path / "mpi.log"), MOCK_SBATCH_LOG=_shell_path(tmp_path / "sbatch.log"),
               MOCK_RELEASE_LOG=_shell_path(tmp_path / "release.log"), MOCK_DRIVER_LOG=_shell_path(tmp_path / "driver.log"),
               MOCK_STARTUP="valid", MOCK_SCF="valid", MOCK_PROJECTION="complete")
    return dict(root=tmp_path, runs=runs, directory=directory, spec=spec, inventory=inventory,
                scripts=scripts, manifest=manifest, env=env, executable=_bash())


def run(case, submit=False, concurrency="1", **overrides):
    args = [_shell_path(case["scripts"] / (SUBMITTER if submit else RUNNER))]
    if submit:
        args += [_shell_path(case["manifest"]), concurrency]
    return subprocess.run([case["executable"], "-c", 'export PATH="$QE_PREFIX/bin:$PATH"; exec bash "$@"',
                           "mock-numerical", *args], cwd=case["root"], env=dict(case["env"], **overrides),
                          text=True, capture_output=True, timeout=40,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def launches(case):
    log = case["root"] / "mpi.log"
    return log.read_text().splitlines() if log.exists() else []


def save(case, row):
    job = case["spec"]["jobs"][row - 1]
    return case["directory"] / ("tmp_" + job["job"]) / (job["prefix"] + ".save")


def original_sources(case):
    return {cp["prefix"]: snapshot(case["runs"] / cp["dir"]) for cp in case["inventory"]["checkpoints"]}


@pytest.mark.parametrize("row", [1, 3, 5])
def test_success_retains_independent_full_checkpoint_for_each_arm(batch, row):
    originals = original_sources(batch)
    result = run(batch, SLURM_ARRAY_TASK_ID=str(row))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SENSITIVITY COMPLETE" in result.stdout
    assert original_sources(batch) == originals
    assert (save(batch, row) / "wfcup8.hdf5").read_text().strip() == "new retained wavefunction"
    assert (save(batch, row) / "wfcdw8.hdf5").is_file()
    assert (save(batch, row) / "charge-density.hdf5").read_text().strip() == "new density after SCF"
    job = batch["spec"]["jobs"][row - 1]["job"]
    assert json.loads((batch["directory"] / (job + ".qc.json")).read_text())["status"] == "COMPLETE"
    assert (batch["directory"] / (job + ".run.in")).read_bytes() == (batch["directory"] / (job + ".in")).read_bytes()
    assert (batch["directory"] / (job + ".clone_receipt.json")).is_file()
    assert len(launches(batch)) == 2
    assert all("-np 128" in command and "-nk 8" in command for command in launches(batch))


@pytest.mark.parametrize("mode", ["missing_density", "fallback"])
def test_bad_startup_stops_before_projection_and_keeps_both_checkpoints(batch, mode):
    originals = original_sources(batch)
    result = run(batch, MOCK_STARTUP=mode)
    assert result.returncode != 0
    assert "STARTUP QC FAILED" in result.stdout
    assert len(launches(batch)) == 1
    assert (save(batch, 1) / "wfcup8.hdf5").is_file()
    assert original_sources(batch) == originals


@pytest.mark.parametrize("stage", ["scf", "projection"])
def test_compute_failure_preserves_old_and_complete_new_scratch(batch, stage):
    originals = original_sources(batch)
    result = run(batch, **({"MOCK_SCF": "fail"} if stage == "scf" else {"MOCK_PROJECTION": "partial"}))
    assert result.returncode != 0, result.stdout + result.stderr
    assert len(launches(batch)) == (1 if stage == "scf" else 2)
    assert (save(batch, 1) / "wfcup8.hdf5").is_file()
    assert (save(batch, 1) / "charge-density.hdf5").is_file()
    assert original_sources(batch) == originals


def test_submitter_holds_exact_six_job_four_hour_sequential_batch(batch):
    result = run(batch, submit=True)
    assert result.returncode == 0, result.stdout + result.stderr
    args = (batch["root"] / "sbatch.log").read_text().splitlines()
    for flag in ("--hold", "--mem=237G", "--time=04:00:00", "--no-requeue", "--array=1-6%1"):
        assert args.count(flag) == 1
    assert args[args.index("-n") + 1] == "128"
    assert args[args.index("-N") + 1] == "1"
    assert args[-1] == _shell_path(batch["scripts"] / RUNNER)
    assert "3072" in result.stdout
    assert not (batch["root"] / "release.log").exists()
    assert not launches(batch)
    assert (batch["root"] / "driver.log").is_file()


@pytest.mark.parametrize("np_value,concurrency", [("64", "1"), ("128", "2")])
def test_submitter_rejects_expanded_resource_contract(batch, np_value, concurrency):
    result = run(batch, submit=True, concurrency=concurrency, NP=np_value)
    assert result.returncode != 0
    assert not (batch["root"] / "sbatch.log").exists()
    assert not launches(batch)


def test_corrupt_source_refused_before_mpi_or_destination_claim(batch):
    cp = batch["inventory"]["checkpoints"][0]
    (batch["runs"] / cp["dir"] / "paw.txt").write_bytes(b"source drift")
    result = run(batch)
    assert result.returncode != 0
    assert not launches(batch)
    assert not save(batch, 1).parent.exists()


def test_existing_output_refused_without_overwrite(batch):
    output = batch["directory"] / (batch["spec"]["jobs"][0]["job"] + ".out")
    output.write_bytes(b"previous attempt")
    result = run(batch)
    assert result.returncode != 0
    assert output.read_bytes() == b"previous attempt"
    assert not launches(batch)
    assert not save(batch, 1).parent.exists()


def test_guard_byte_drift_refused_before_mpi(batch):
    helper = batch["runs"].parent / "src/dft/hea_sensitivity_guard.py"
    helper.write_bytes(helper.read_bytes() + b"\n")
    result = run(batch)
    assert result.returncode != 0
    assert "pinned file differs" in result.stdout + result.stderr
    assert not launches(batch)


@pytest.mark.parametrize("stage", ["scf", "projection"])
def test_invalid_operation_is_rejected_in_either_compute_stage(batch, stage):
    job = batch["spec"]["jobs"][0]
    payload = Path(batch["env"]["MOCK_PAYLOADS"])
    if os.name == "nt":
        payload = batch["root"] / "payloads"
    path = payload / (job["prefix"] + ".scf" if stage == "scf" else "projection.complete")
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\nNote: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG\n")
    result = run(batch)
    assert result.returncode != 0
    assert len(launches(batch)) == (1 if stage == "scf" else 2)
    assert save(batch, 1).is_dir()
