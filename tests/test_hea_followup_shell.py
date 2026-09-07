"""Follow-up shell integration: real frozen decks/guards/QC, fake MPI and scheduler.

Only pytest temporary files are mutated. No DFT or Slurm command is invoked.
The temporary launch scripts pin the copied real helper/spec bytes, allowing
these tests to run both before and after the repository scripts are pinned.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

import pytest

from dft.hea_force_audit import input_atoms
from test_hea_pilot_runner import ROOT, DIRECTORY, _bash, _shell_path, _write

SPEC_REL = Path("results/hea_followup_2026-09-07/launch_spec.json")
MANIFEST_REL = Path("runs/hea/m_controls_2026-09-07_followup_approved.txt")
RUNNER = "55_hea_followup.slurm"
SUBMITTER = "56_submit_hea_followup.sh"


def _pin_script(source, destination, paths):
    text = source.read_text(encoding="utf-8")
    for variable, path in paths.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        text, count = re.subn(r'(?m)^(check_hash "\$' + variable + r'" )\S+$',
                             lambda match: match[1] + digest, text)
        assert count == 1, (source, variable)
    text, count = re.subn(r'(?m)^PYTHON=.*$',
                         lambda _: 'PYTHON="' + _shell_path(Path(sys.executable)) + '"', text)
    assert count == 1, source
    _write(destination, text)


def _fake_scf(deck):
    labels, _, types = input_atoms(deck)
    assert len(labels) == 75
    # A deliberately nonstationary geometry still has valid, complete SCF output.
    rows = [f" atom {i} type {kind} force = 0.100000 0.000000 0.000000"
            for i, kind in enumerate(types, 1)]
    return "\n".join(["number of atoms/cell = 75", "! total energy = -8000.0 Ry",
        "convergence has been achieved in 7 iterations",
        "total magnetization = 38.0 Bohr mag/cell",
        "absolute magnetization = 64.0 Bohr mag/cell",
        "Forces acting on atoms (cartesian axes, Ry/au):", *rows,
        " Total force = 0.1", " JOB DONE.", ""])


def _fake_projection(nat=75):
    rows = []
    for i in range(1, nat + 1):
        rows += [f" Atom # {i}: total charge = 6.0000, s = 2.0000, p = 4.0000,",
                 " spin up = 3.5000, s = 1.0000, p = 2.5000,",
                 " spin down = 2.5000, s = 1.0000, p = 1.5000,",
                 " polarization = 1.0000, s = 0.0000, p = 1.0000,"]
    return "\n".join([" Lowdin Charges:", *rows, " Spilling Parameter: 0.0022", " JOB DONE.", ""])


@pytest.fixture
def followup(tmp_path):
    project, prefix = tmp_path / "project", tmp_path / "qe"
    staged = project / "sts"
    directory = staged / "runs" / DIRECTORY
    directory.mkdir(parents=True)
    spec_path = staged / SPEC_REL
    spec_path.parent.mkdir(parents=True)
    spec_path.write_bytes((ROOT / SPEC_REL).read_bytes())
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    assert len(spec["jobs"]) == 14
    manifest = staged / MANIFEST_REL
    manifest.write_bytes((ROOT / MANIFEST_REL).read_bytes())
    rows = [f"{r['dir']} {r['job']} {r['suffix']} {r['nk']}" for r in spec["jobs"]]
    _write(Path(str(manifest) + ".lines"), "\n".join(rows))
    payloads = tmp_path / "payloads"
    for row in spec["jobs"]:
        deck = directory / (row["job"] + ".in")
        deck.write_bytes((ROOT / "runs" / row["dir"] / deck.name).read_bytes())
        _write(payloads / (row["job"] + ".scf"), _fake_scf(deck.read_text(encoding="utf-8")))
    _write(payloads / "projection.complete", _fake_projection())
    _write(payloads / "projection.partial", _fake_projection(74))
    _write(payloads / "projection.no_lowdin", " JOB DONE.")
    paths = {"SPEC": spec_path}
    for variable, name in (("GUARD", "hea_followup_guard.py"),
                           ("QC", "hea_followup_qc.py"), ("FORCE_AUDIT", "hea_force_audit.py")):
        target = staged / "src/dft" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / "src/dft" / name).read_bytes())
        paths[variable] = target
    scripts = staged / "anvil"
    scripts.mkdir()
    for name in (RUNNER, SUBMITTER):
        _pin_script(ROOT / "anvil" / name, scripts / name, paths)
    _write(scripts / "pseudo_md5_preflight_2026-08-23.md", "mock evidence marker")
    _write(project / "parity/PARITY_PASS", "mock parity marker")
    pseudo = project / "pseudo"
    pseudo.mkdir()
    _write(prefix / "bin/mpirun", r"""
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
    _write(prefix / "bin/pw.x", r"""
        #!/bin/bash
        set -eu
        inp=''
        while [ "$#" -gt 0 ]; do
          case "$1" in -in) inp=$2; shift 2 ;; -nk) shift 2 ;; *) exit 96 ;; esac
        done
        prefix=$(sed -n "s/^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        scratch=$(sed -n "s/^[[:space:]]*outdir[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        [ -n "$prefix" ] && [ -n "$scratch" ] || exit 94
        mkdir -p "$scratch/$prefix.save"
        printf '%s\n' 'mock metadata' > "$scratch/$prefix.save/data-file-schema.xml"
        if [ "$MOCK_SCF_MODE" != missing_density ]; then
          printf '%s\n' 'mock density' > "$scratch/$prefix.save/charge-density.dat"
        fi
        printf '%s\n' 'irreplaceable mock wavefunction' > "$scratch/$prefix.save/wfc1.dat"
        printf '%s\n' "$scratch/$prefix.save/wfc1.dat" > "$MOCK_WFC_RECORD"
        if [ "$MOCK_SCF_MODE" = partial_force ]; then
          sed '/atom 75 type /d' "$MOCK_PAYLOADS/$prefix.scf"
        else
          cat "$MOCK_PAYLOADS/$prefix.scf"
        fi
    """, executable=True)
    _write(prefix / "bin/projwfc.x", r"""
        #!/bin/bash
        set -eu
        wfc=$(cat "$MOCK_WFC_RECORD")
        [ -f "$wfc" ] || exit 93
        printf '%s\n' 'projection saw intact wavefunction' > "$MOCK_PROJECTION_RECORD"
        cat "$MOCK_PAYLOADS/projection.$MOCK_PROJ_MODE"
    """, executable=True)
    _write(prefix / "bin/sbatch", r"""
        #!/bin/bash
        printf '%s\n' "$@" > "$MOCK_SBATCH_LOG"
        echo 'Submitted batch job 123456'
    """, executable=True)
    _write(prefix / "bin/scontrol", r"""
        #!/bin/bash
        printf '%s\n' "$@" > "$MOCK_RELEASE_LOG"
    """, executable=True)
    _write(prefix / "bin/seff", "#!/bin/bash\nexit 0", executable=True)
    driver = project / "queue_r1.sh"
    _write(driver, r"""
        #!/bin/bash
        set -eu
        [ "$PREFLIGHT_ONLY" = 1 ] && [ "$LOG" = /dev/stdout ] || exit 81
        printf '%s\n' "$@" > "$MOCK_DRIVER_LOG"
    """, executable=True)
    exclude = next(line.split("=", 1)[1] for line in manifest.read_text().splitlines()
                   if line.startswith("# SUBMIT WITH EXCLUDE="))
    env = os.environ.copy()
    env.update(PROJECT=_shell_path(project), MANIFEST=_shell_path(manifest),
        RUNS=_shell_path(staged / "runs"), QE_PREFIX=_shell_path(prefix), PSEUDO_DIR=_shell_path(pseudo),
        ACCT="mock-account", EXCLUDE=exclude, DRIVER=_shell_path(driver), NP="128",
        SLURM_ARRAY_TASK_ID="1", SLURM_JOB_ID="123456", SLURM_CPUS_ON_NODE="128",
        MOCK_PAYLOADS=_shell_path(payloads),
        MOCK_MPI_LOG=_shell_path(tmp_path / "mpi.log"), MOCK_WFC_RECORD=_shell_path(tmp_path / "wavefunction.txt"),
        MOCK_PROJECTION_RECORD=_shell_path(tmp_path / "projection.txt"), MOCK_SCF_MODE="success", MOCK_PROJ_MODE="complete",
        MOCK_SBATCH_LOG=_shell_path(tmp_path / "sbatch.log"), MOCK_RELEASE_LOG=_shell_path(tmp_path / "release.log"),
        MOCK_DRIVER_LOG=_shell_path(tmp_path / "driver.log"))
    return dict(root=tmp_path, directory=directory, project=project, staged=staged, spec_path=spec_path,
                spec=spec, manifest=manifest, scripts=scripts, env=env, executable=_bash())


def _run(case, submit=False, concurrency="1", **env):
    script = case["scripts"] / (SUBMITTER if submit else RUNNER)
    args = [_shell_path(script)]
    if submit:
        args += [_shell_path(case["manifest"]), concurrency]
    # Resolve only temporary scheduler/QE mocks; scripts use the pinned real Python.
    return subprocess.run([case["executable"], "-c", 'export PATH="$QE_PREFIX/bin:$PATH"; exec bash "$@"',
        "mock-followup", *args], cwd=case["root"], env=dict(case["env"], **env), text=True,
        capture_output=True, timeout=30,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def _job(case, row=1):
    return case["spec"]["jobs"][row - 1]["job"]


def _launches(case):
    path = case["root"] / "mpi.log"
    return path.read_text().splitlines() if path.exists() else []


def _preserved(case, row=1):
    job = _job(case, row)
    save = case["directory"] / ("tmp_" + job) / (job + ".save")
    assert (save / "wfc1.dat").read_text().strip() == "irreplaceable mock wavefunction"
    assert (save / "data-file-schema.xml").is_file()
    assert (save / "charge-density.dat").is_file()
    assert not (case["directory"] / "dens" / (job + ".save")).exists()


def test_submitter_holds_exact_fourteen_job_sequential_allocation(followup):
    result = _run(followup, submit=True)
    assert result.returncode == 0, result.stdout + result.stderr
    args = (followup["root"] / "sbatch.log").read_text().splitlines()
    for flag in ("--hold", "--time=04:00:00", "--no-requeue", "--array=1-14%1"):
        assert args.count(flag) == 1
    assert args[args.index("-N") + 1] == "1"
    assert args[args.index("-n") + 1] == "128"
    assert args[-1] == _shell_path(followup["scripts"] / RUNNER)
    assert "7168" in result.stdout
    assert not (followup["root"] / "release.log").exists()
    assert not _launches(followup)
    assert (followup["root"] / "driver.log").read_text().splitlines() == [
        _shell_path(followup["manifest"]), "128", "1"]


@pytest.mark.parametrize("target", ["deck", "spec"])
def test_submitter_rejects_changed_frozen_identity_before_preflight(followup, target):
    path = followup["spec_path"] if target == "spec" else followup["directory"] / (_job(followup) + ".in")
    path.write_bytes(path.read_bytes() + b"\n")
    result = _run(followup, submit=True)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "REFUSE:" in result.stdout + result.stderr
    for name in ("driver.log", "sbatch.log", "release.log", "mpi.log"):
        assert not (followup["root"] / name).exists()


@pytest.mark.parametrize("target", ["selected_deck", "other_deck", "spec"])
def test_runner_rejects_queue_time_tampering_before_mpi(followup, target):
    assert _run(followup, submit=True).returncode == 0
    path = followup["spec_path"] if target == "spec" else followup["directory"] / (
        _job(followup, 1 if target == "selected_deck" else 14) + ".in")
    path.write_bytes(path.read_bytes() + b"\n")
    result = _run(followup)
    assert result.returncode != 0, result.stdout + result.stderr
    assert not _launches(followup)
    assert not (followup["directory"] / ("tmp_" + _job(followup))).exists()


def test_completed_previous_row_does_not_block_valid_high_force_next_row(followup):
    first = _run(followup)
    assert first.returncode == 0, first.stdout + first.stderr
    first_output = followup["directory"] / (_job(followup) + ".out")
    original = first_output.read_bytes()
    second = _run(followup, SLURM_ARRAY_TASK_ID="2")
    assert second.returncode == 0, second.stdout + second.stderr
    assert first_output.read_bytes() == original
    launches = _launches(followup)
    assert len(launches) == 4
    for line, program in zip(launches, ("pw.x", "projwfc.x", "pw.x", "projwfc.x")):
        assert f"-np 128 {program} -nk 8 -in " in line
    for row in (1, 2):
        job = _job(followup, row)
        record = json.loads((followup["directory"] / (job + ".qc.json")).read_text())
        assert record["status"] == "COMPLETE"
        assert record["scf"]["status"] == "VALID_SCF"
        assert record["scf"]["geometry_stationarity"] == "ABOVE_THRESHOLD"
        assert record["scf"]["fmax_free_ev_A"] > 2
        assert record["projection"]["nat"] == 75
        assert [a["index"] for a in record["projection"]["atoms"]] == list(range(75))
        runtime = (followup["directory"] / (job + ".run.in")).read_text()
        assert re.findall(r"max_seconds\s*=\s*(\d+)", runtime) == ["13200"]
        save = followup["directory"] / "dens" / (job + ".save")
        assert (save / "data-file-schema.xml").is_file()
        assert (save / "charge-density.dat").is_file()
        assert not list(save.glob("wfc*"))
        assert not (followup["directory"] / ("tmp_" + job)).exists()


@pytest.mark.parametrize("mode", ["partial", "no_lowdin"])
def test_incomplete_projection_preserves_wavefunctions_and_blocks_retention(followup, mode):
    result = _run(followup, MOCK_PROJ_MODE=mode)
    assert result.returncode != 0, result.stdout + result.stderr
    assert len(_launches(followup)) == 2
    _preserved(followup)
    if mode == "partial":
        record = json.loads((followup["directory"] / (_job(followup) + ".qc.json")).read_text())
        assert record["status"] == "REJECTED"


def test_partial_force_table_stops_before_projection_and_preserves_scratch(followup):
    result = _run(followup, MOCK_SCF_MODE="partial_force")
    assert result.returncode != 0, result.stdout + result.stderr
    assert len(_launches(followup)) == 1
    _preserved(followup)
    assert not (followup["root"] / "projection.txt").exists()
    record = json.loads((followup["directory"] / (_job(followup) + ".scf_qc.json")).read_text())
    assert record["status"] == "REJECTED"


@pytest.mark.parametrize("suffix", [".scf_qc.json", ".qc.json"])
def test_stale_qc_is_rejected_before_any_compute_or_overwrite(followup, suffix):
    stale = followup["directory"] / (_job(followup) + suffix)
    stale.write_bytes(b"retained prior diagnostic\n")
    result = _run(followup)
    assert result.returncode != 0, result.stdout + result.stderr
    assert not _launches(followup)
    assert stale.read_bytes() == b"retained prior diagnostic\n"


@pytest.mark.parametrize("np_value,concurrency", [("64", "1"), ("128", "2")])
def test_resource_overrides_cannot_expand_the_followup(followup, np_value, concurrency):
    result = _run(followup, submit=True, concurrency=concurrency, NP=np_value)
    assert result.returncode != 0
    assert not (followup["root"] / "sbatch.log").exists()
    assert not _launches(followup)


def test_missing_density_prevents_success_cleanup_after_valid_projection(followup):
    result = _run(followup, MOCK_SCF_MODE="missing_density")
    assert result.returncode != 0, result.stdout + result.stderr
    assert len(_launches(followup)) == 2
    job = _job(followup)
    scratch_save = followup["directory"] / ("tmp_" + job) / (job + ".save")
    assert (scratch_save / "wfc1.dat").read_text().strip() == "irreplaceable mock wavefunction"
    assert (scratch_save / "data-file-schema.xml").is_file()
    assert not (scratch_save / "charge-density.dat").exists()
    assert not (followup["directory"] / "dens" / (job + ".save")).exists()
    assert "RETENTION FAILED" in result.stdout
