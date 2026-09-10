"""Real winner guard/QC with temporary MPI and scheduler mocks; no real compute."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from test_hea_pilot_runner import _bash, _shell_path, _write
from test_hea_followup_shell import _fake_scf, _fake_projection
from test_hea_winner_guard import ROOT, SPEC_REL, stage
from dft import hea_winner_guard as guard

RUNNER = "66_hea_winner.slurm"
SUBMITTER = "67_submit_hea_winner.sh"


@pytest.fixture
def winner(tmp_path):
    project = tmp_path / "project"
    staged = project / "sts"
    spec = stage(staged)
    spec_path = staged / SPEC_REL
    directory = staged / "runs" / guard.DIRECTORY
    pseudo = project / "pseudo"
    pseudo.mkdir()
    for item in spec["pseudopotentials"]:
        raw = ("test potential " + item["path"]).encode()
        (pseudo / item["path"]).write_bytes(raw)
        item["sha256"] = hashlib.sha256(raw).hexdigest()
    spec_path.write_text(json.dumps(spec), encoding="utf-8", newline="\n")
    prefix = tmp_path / "qe"
    paths = {"SPEC": spec_path}
    for variable, filename in (
        ("GUARD", "hea_winner_guard.py"), ("COMMON_GUARD", "hea_followup_guard.py"),
        ("QC", "hea_followup_qc.py"), ("FORCE_AUDIT", "hea_force_audit.py"),
    ):
        source = ROOT / "src/dft" / filename
        target = staged / "src/dft" / filename
        text = source.read_text(encoding="utf-8")
        if variable == "GUARD":
            text = text.replace(guard.PSEUDO_DIR, _shell_path(pseudo))
        _write(target, text)
        paths[variable] = target
    payloads = tmp_path / "payloads"
    # Rows 7 and 8 are the original 75-atom OOH endpoints.
    for entry in spec["jobs"][6:]:
        deck = directory / (entry["job"] + ".in")
        _write(payloads / (entry["job"] + ".scf"), _fake_scf(deck.read_text(encoding="utf-8")))
    _write(payloads / "projection", _fake_projection())
    _write(prefix / "bin/mpirun", r"""
        #!/bin/bash
        set -eu
        printf '%s\n' "$*" >> "$MOCK_MPI_LOG"
        [ "$1" = --oversubscribe ] && shift
        [ "$1" = -np ] && [ "$2" = 128 ] && shift 2
        exec "$@"
    """, executable=True)
    _write(prefix / "bin/pw.x", r"""
        #!/bin/bash
        set -eu
        [ "$1" = -nk ] && [ "$2" = 8 ] && [ "$3" = -in ]
        inp=$4
        prefix=$(sed -n "s/^[[:space:]]*prefix[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        scratch=$(sed -n "s/^[[:space:]]*outdir[[:space:]]*=[[:space:]]*'\([^']*\)'.*/\1/p" "$inp")
        save="$scratch/$prefix.save"
        mkdir -p "$save"
        for name in data-file-schema.xml occup.txt paw.txt; do
          printf '%s\n' 'retained evidence' > "$save/$name"
        done
        if [ "$MOCK_MODE" != missing_density ]; then
          printf '%s\n' 'retained density' > "$save/charge-density.hdf5"
        fi
        for spin in up dw; do
          for k in 1 2 3 4 5 6 7 8; do
            printf '%s\n' 'irreplaceable wavefunction' > "$save/wfc$spin$k.hdf5"
          done
        done
        if [ "$MOCK_MODE" = partial_force ]; then
          sed '/atom 75 type /d' "$MOCK_PAYLOADS/$prefix.scf"
        else
          cat "$MOCK_PAYLOADS/$prefix.scf"
        fi
        if [ "$MOCK_MODE" = ieee ]; then echo 'IEEE_INVALID_FLAG' >&2; fi
    """, executable=True)
    _write(prefix / "bin/projwfc.x", r"""
        #!/bin/bash
        set -eu
        cat "$MOCK_PAYLOADS/projection"
        if [ "$MOCK_MODE" = projection_ieee ]; then echo 'IEEE_INVALID_FLAG' >&2; fi
    """, executable=True)
    _write(prefix / "bin/sbatch", r"""
        #!/bin/bash
        printf '%s\n' "$@" > "$MOCK_SBATCH_LOG"
        echo 'Submitted batch job 123456'
    """, executable=True)
    _write(prefix / "bin/seff", "#!/bin/bash\nexit 0", executable=True)
    for variable, filename in (("PW_BIN", "pw.x"), ("PROJ_BIN", "projwfc.x"), ("MPI_BIN", "mpirun")):
        paths[variable] = prefix / "bin" / filename
    scripts = staged / "anvil"
    for name in (RUNNER, SUBMITTER):
        text = (ROOT / "anvil" / name).read_text(encoding="utf-8")
        text = text.replace(guard.PSEUDO_DIR, _shell_path(pseudo))
        for variable, target in paths.items():
            pattern = r'(?m)^(check_hash "\$' + variable + r'" )\S+$'
            text, count = re.subn(pattern, lambda m: m[1] + hashlib.sha256(target.read_bytes()).hexdigest(), text)
            assert count == 1, variable
        text, count = re.subn(r"(?m)^PYTHON=.*$",
            lambda _: 'PYTHON="' + _shell_path(Path(sys.executable)) + '"', text)
        assert count == 1
        _write(scripts / name, text)
    _write(scripts / "pseudo_md5_preflight_2026-08-23.md", "test identity record")
    _write(project / "parity/PARITY_PASS", "test parity")
    driver = project / "queue_r1.sh"
    _write(driver, r"""
        #!/bin/bash
        [ "$PREFLIGHT_ONLY" = 1 ] && [ "$LOG" = /dev/stdout ]
    """, executable=True)
    manifest = staged / guard.MANIFEST
    exclude = next(line.split("=", 1)[1] for line in manifest.read_text().splitlines()
                   if line.startswith("# SUBMIT WITH EXCLUDE="))
    env = dict(os.environ, PROJECT=_shell_path(project), RUNS=_shell_path(staged / "runs"),
        MANIFEST=_shell_path(manifest), QE_PREFIX=_shell_path(prefix), PSEUDO_DIR=_shell_path(pseudo),
        NP="128", ACCT="test-account", EXCLUDE=exclude, DRIVER=_shell_path(driver),
        SLURM_ARRAY_TASK_ID="7", SLURM_JOB_ID="123456", SLURM_CPUS_ON_NODE="128",
        MOCK_MODE="success", MOCK_PAYLOADS=_shell_path(payloads),
        MOCK_MPI_LOG=_shell_path(tmp_path / "mpi.log"),
        MOCK_SBATCH_LOG=_shell_path(tmp_path / "sbatch.log"))
    return dict(root=tmp_path, project=project, staged=staged, spec=spec, directory=directory,
                scripts=scripts, prefix=prefix, env=env, manifest=manifest)


def run(case, submit=False, concurrency="1", **env):
    args = [_shell_path(case["scripts"] / (SUBMITTER if submit else RUNNER))]
    if submit:
        args += [_shell_path(case["manifest"]), concurrency]
    return subprocess.run([_bash(), "-c",
        'export PATH="$QE_PREFIX/bin:$PATH"; exec bash "$@"', "mock-winner", *args],
        cwd=case["root"], env=dict(case["env"], **env), text=True, capture_output=True, timeout=30,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def retained(case):
    entry = case["spec"]["jobs"][6]
    save = case["directory"] / ("tmp_" + entry["job"]) / (entry["job"] + ".save")
    assert len(list(save.glob("wfc*.hdf5"))) == 16
    assert (save / "wfcup1.hdf5").read_text().strip() == "irreplaceable wavefunction"
    return save


def test_success_retains_full_checkpoint_and_prior_row_does_not_block_next(winner):
    first = run(winner)
    assert first.returncode == 0, first.stdout + first.stderr
    retained(winner)
    entry = winner["spec"]["jobs"][6]
    output = winner["directory"] / (entry["job"] + ".out")
    before = output.read_bytes()
    second = run(winner, SLURM_ARRAY_TASK_ID="8")
    assert second.returncode == 0, second.stdout + second.stderr
    assert output.read_bytes() == before
    qc = json.loads((winner["directory"] / (entry["job"] + ".qc.json")).read_text())
    assert qc["status"] == "COMPLETE"
    assert qc["scf"]["geometry_stationarity"] == "ABOVE_THRESHOLD"
    assert run(winner).returncode != 0
    assert output.read_bytes() == before


@pytest.mark.parametrize("mode,launches", [
    ("ieee", 1), ("partial_force", 1), ("projection_ieee", 2), ("missing_density", 2),
])
def test_failed_scf_projection_or_retention_never_clears_scratch(winner, mode, launches):
    result = run(winner, MOCK_MODE=mode)
    assert result.returncode != 0, result.stdout + result.stderr
    retained(winner)
    assert len((winner["root"] / "mpi.log").read_text().splitlines()) == launches


def test_submitter_requests_only_eight_held_bounded_jobs(winner):
    result = run(winner, submit=True)
    assert result.returncode == 0, result.stdout + result.stderr
    args = (winner["root"] / "sbatch.log").read_text().splitlines()
    for item in ("--hold", "--time=04:00:00", "--mem=237G", "--no-requeue",
                 "--array=1-8%1", "--job-name=hea-winner"):
        assert args.count(item) == 1
    assert args[args.index("-n") + 1] == "128"
    assert not (winner["root"] / "mpi.log").exists()
    assert "4096" in result.stdout


def test_submitter_refuses_expanded_concurrency(winner):
    assert run(winner, submit=True, concurrency="2").returncode != 0
    assert not (winner["root"] / "sbatch.log").exists()


def test_changed_binary_refused_before_mpi(winner):
    binary = winner["prefix"] / "bin/pw.x"
    binary.write_bytes(binary.read_bytes() + b"\n")
    assert run(winner).returncode != 0
    assert not (winner["root"] / "mpi.log").exists()
