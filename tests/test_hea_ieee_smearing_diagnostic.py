"""Smearing reproduction: original accepted tight source, exact deck, strict rank QC."""
import json
import os
from pathlib import Path

import pytest

from dft import hea_ieee_smearing_diagnostic as diag
from test_hea_followup_shell import _pin_script
from test_hea_sensitivity_shell import batch as sensitivity_batch, original_sources
from test_hea_pilot_runner import ROOT, _shell_path, _write


@pytest.fixture
def diagnostic(sensitivity_batch):
    case = sensitivity_batch
    staged = case["runs"].parent
    directory = case["runs"] / diag.DIRECTORY
    directory.mkdir()
    original = case["directory"] / (diag.ORIGINAL_JOB + ".in")
    (directory / (diag.JOB + ".in")).write_bytes(original.read_bytes())
    manifest = staged / diag.MANIFEST
    manifest.write_bytes((ROOT / diag.MANIFEST).read_bytes())
    Path(str(manifest) + ".lines").write_bytes(
        (diag.DIRECTORY + " " + diag.JOB + " .in 8\n").encode())
    helper = staged / "src/dft/hea_ieee_smearing_diagnostic.py"
    helper.write_bytes((ROOT / "src/dft/hea_ieee_smearing_diagnostic.py").read_bytes())
    wrapper = case["scripts"] / "hea_ieee_smearing_rank.sh"
    wrapper.write_bytes((ROOT / "anvil/hea_ieee_smearing_rank.sh").read_bytes())
    qe = case["root"] / "qe"
    # Real wrapper invocations for ranks 0 and 7. Other ranks have empty streams;
    # no real MPI or repeated physical calculation is needed for stream assembly.
    _write(qe / "bin/mpirun", r"""
        #!/bin/bash
        set -u
        printf '%s\n' "$*" >> "$MOCK_MPI_LOG"
        while [ "$#" -gt 0 ]; do
          case "$1" in --oversubscribe) shift ;; -np) [ "$2" = 128 ] || exit 99; shift 2 ;; *) break ;; esac
        done
        [ "$1" = bash ] || exit 98
        rc=0
        OMPI_COMM_WORLD_SIZE=128 OMPI_COMM_WORLD_RANK=0 "$@" || rc=$?
        OMPI_COMM_WORLD_SIZE=128 OMPI_COMM_WORLD_RANK=7 "$@" || rc=$?
        for rank in {0..127}; do
          [ "$rank" = 0 ] || [ "$rank" = 7 ] && continue
          if [ "$MOCK_MISSING_RANK" = "$rank" ]; then continue; fi
          printf -v name 'rank%03d.stderr' "$rank"
          : > "$DIAG_RANK_DIR/$name"
        done
        if [ "$MOCK_LAUNCHER" = invalid ]; then echo 'IEEE_INVALID_FLAG launcher diagnostic' >&2; fi
        exit "$rc"
    """, executable=True)
    # Nonzero rank emits the diagnostic flag only on stderr. Rank zero keeps the
    # realistic finite SCF/Lowdin fixture inherited from sensitivity lifecycle tests.
    for name in ("pw.x", "projwfc.x"):
        path = qe / "bin" / name
        text = path.read_text(encoding="utf-8")
        stage = "scf" if name == "pw.x" else "projection"
        injected = (
            'if [ "${OMPI_COMM_WORLD_RANK:-0}" != 0 ]; then\n'
            '  if [ "$MOCK_IEEE_STAGE" = "' + stage + '" ]; then\n'
            '    echo "Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG" >&2\n'
            '  fi\n  exit 0\nfi\n')
        _write(path, text.replace("set -eu\n", "set -eu\n" + injected, 1), executable=True)
    paths = {
        "SPEC": staged / diag.SPEC, "MANIFEST": manifest,
        "FROZEN": staged / "src/dft/hea_numerical_guard.py",
        "SENSITIVITY": staged / "src/dft/hea_sensitivity_guard.py",
        "GUARD": helper, "QC": staged / "src/dft/hea_followup_qc.py",
        "FORCE_AUDIT": staged / "src/dft/hea_force_audit.py", "WRAPPER": wrapper,
        "MPI": qe / "bin/mpirun", "PW": qe / "bin/pw.x", "PROJECTION": qe / "bin/projwfc.x",
    }
    for name in ("64_hea_ieee_smearing.slurm", "65_submit_hea_ieee_smearing.sh"):
        _pin_script(ROOT / "anvil" / name, case["scripts"] / name, paths)
    env = case["env"].copy()
    env.update(MANIFEST=_shell_path(manifest), MOCK_IEEE_STAGE="none", MOCK_MISSING_RANK="none",
               MOCK_LAUNCHER="none")
    env["EXCLUDE"] = next(line.split("=", 1)[1] for line in manifest.read_text().splitlines()
                          if line.startswith("# SUBMIT WITH EXCLUDE="))
    return dict(case, directory=directory, manifest=manifest, env=env, paths=paths)


def run(case, submit=False, concurrency="1", **env):
    # The numerical harness accepts a mutable module-level RUNNER constant; avoid
    # changing it and invoke the same subprocess mechanics directly.
    import subprocess
    args = [_shell_path(case["scripts"] / ("65_submit_hea_ieee_smearing.sh" if submit
                                           else "64_hea_ieee_smearing.slurm"))]
    if submit:
        args += [_shell_path(case["manifest"]), concurrency]
    return subprocess.run([case["executable"], "-c", 'export PATH="$QE_PREFIX/bin:$PATH"; exec bash "$@"',
                           "mock-ieee", *args], cwd=case["root"], env=dict(case["env"], **env),
                          text=True, capture_output=True, timeout=60,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def launches(case):
    log = case["root"] / "mpi.log"
    return log.read_text().splitlines() if log.exists() else []


def result_record(case):
    return json.loads((case["directory"] / (diag.JOB + ".diagnostic.json")).read_text())


def retained(case):
    return case["directory"] / ("tmp_" + diag.ORIGINAL_JOB) / (diag.PREFIX + ".save")


def test_clean_reproduction_projects_and_preserves_both_histories(diagnostic):
    original = original_sources(diagnostic)
    result = run(diagnostic)
    assert result.returncode == 0, result.stdout + result.stderr
    record = result_record(diagnostic)
    assert record["diagnostic_status"] == "CLEAN_REPRODUCTION"
    assert record["new_endpoint_status"] == "COMPLETE"
    assert record["prior_flagged_run_reclassified"] is False
    assert original_sources(diagnostic) == original
    assert (retained(diagnostic) / "wfcup8.hdf5").is_file()
    assert len(launches(diagnostic)) == 2
    for stage in ("scf", "projection"):
        names = diag.stage_names(stage)
        raw = diagnostic["directory"] / names["ranks"]
        assert len(list(raw.glob("rank*.stderr"))) == 128
        audit = json.loads((diagnostic["directory"] / names["audit"]).read_text())
        assert audit["collection_complete"] is True
    assert (diagnostic["directory"] / (diag.JOB + ".run.in")).read_bytes() == (
        diagnostic["directory"] / (diag.JOB + ".in")).read_bytes()


def test_invalid_flag_on_nonzero_rank_rejects_clean_looking_stdout(diagnostic):
    original = original_sources(diagnostic)
    result = run(diagnostic, MOCK_IEEE_STAGE="scf")
    assert result.returncode != 0
    assert len(launches(diagnostic)) == 1
    raw_stdout = (diagnostic["directory"] / (diag.JOB + ".stdout")).read_text()
    assert "JOB DONE" in raw_stdout and "IEEE_INVALID_FLAG" not in raw_stdout
    assert "IEEE_INVALID_FLAG" in (diagnostic["directory"] / (diag.JOB + ".rank_stderr/rank007.stderr")).read_text()
    assert "IEEE_INVALID_FLAG" in (diagnostic["directory"] / (diag.JOB + ".out")).read_text()
    record = result_record(diagnostic)
    assert record["diagnostic_status"] == "IEEE_INVALID_REPRODUCED"
    assert record["invalid_ranks"] == [7]
    assert record["new_endpoint_status"] == "REJECTED"
    assert original_sources(diagnostic) == original
    assert retained(diagnostic).is_dir()


def test_projection_rank_flag_keeps_clean_scf_but_endpoint_incomplete(diagnostic):
    result = run(diagnostic, MOCK_IEEE_STAGE="projection")
    assert result.returncode != 0
    assert len(launches(diagnostic)) == 2
    record = result_record(diagnostic)
    assert record["diagnostic_status"] == "CLEAN_REPRODUCTION"
    assert record["new_endpoint_status"] == "INCOMPLETE"
    assert "IEEE_INVALID_FLAG" in (diagnostic["directory"] / (diag.JOB + ".projwfc.out")).read_text()
    assert retained(diagnostic).is_dir()


def test_missing_rank_stream_prevents_acceptance(diagnostic):
    result = run(diagnostic, MOCK_MISSING_RANK="127")
    assert result.returncode != 0
    assert len(launches(diagnostic)) == 1
    record = result_record(diagnostic)
    assert record["rank_capture_complete"] is False
    assert record["new_endpoint_status"] == "REJECTED"
    audit = json.loads((diagnostic["directory"] / (diag.JOB + ".rank_audit.json")).read_text())
    assert audit["missing_ranks"] == [127]


def test_launcher_stderr_is_included_in_strict_qc(diagnostic):
    result = run(diagnostic, MOCK_LAUNCHER="invalid")
    assert result.returncode != 0
    assert len(launches(diagnostic)) == 1
    record = result_record(diagnostic)
    assert record["diagnostic_status"] == "IEEE_INVALID_REPRODUCED"
    assert record["invalid_ranks"] == []
    assert "launcher diagnostic" in (diagnostic["directory"] / (diag.JOB + ".out")).read_text()


@pytest.mark.parametrize("mode", ["fail"])
def test_nonconverged_scf_retains_every_stream_and_blocks_projection(diagnostic, mode):
    original = original_sources(diagnostic)
    result = run(diagnostic, MOCK_SCF=mode)
    assert result.returncode != 0
    assert len(launches(diagnostic)) == 1
    assert result_record(diagnostic)["diagnostic_status"] == "OTHER_FAILURE"
    assert original_sources(diagnostic) == original
    assert retained(diagnostic).is_dir()


def test_projection_incomplete_retains_clean_scf_diagnosis(diagnostic):
    result = run(diagnostic, MOCK_PROJECTION="partial")
    assert result.returncode != 0
    record = result_record(diagnostic)
    assert record["diagnostic_status"] == "CLEAN_REPRODUCTION"
    assert record["new_endpoint_status"] == "INCOMPLETE"


def test_held_single_task_has_four_hour_no_retry_bound(diagnostic):
    result = run(diagnostic, submit=True)
    assert result.returncode == 0, result.stdout + result.stderr
    args = (diagnostic["root"] / "sbatch.log").read_text().splitlines()
    for flag in ("--hold", "--mem=237G", "--time=04:00:00", "--no-requeue", "--array=1-1%1"):
        assert args.count(flag) == 1
    assert args[args.index("-n") + 1] == "128"
    assert "512" in result.stdout
    assert not (diagnostic["root"] / "release.log").exists()
    assert not launches(diagnostic)


@pytest.mark.parametrize("variable", ["PW", "MPI", "WRAPPER", "FROZEN", "SENSITIVITY"])
def test_changed_binary_or_helper_refused_before_clone(diagnostic, variable):
    path = diagnostic["paths"][variable]
    path.write_bytes(path.read_bytes() + b"\n")
    result = run(diagnostic)
    assert result.returncode != 0
    assert "pinned file differs" in result.stdout + result.stderr
    assert not launches(diagnostic)
    assert not retained(diagnostic).parent.exists()


def test_input_changed_during_long_clone_refused(diagnostic, monkeypatch):
    real_hash = diag.frozen._stream_hash
    changed = False
    def mutate(path):
        nonlocal changed
        value = real_hash(path)
        if not changed and diag.DIRECTORY.split("/")[-1] in str(path):
            changed = True
            deck = diagnostic["directory"] / (diag.JOB + ".in")
            deck.write_bytes(deck.read_bytes() + b"! changed\n")
        return value
    monkeypatch.setattr(diag.frozen, "_stream_hash", mutate)
    with pytest.raises(ValueError, match="byte-identical"):
        diag.prepare(diagnostic["runs"])
    assert changed and retained(diagnostic).is_dir()
    assert not (diagnostic["directory"] / (diag.JOB + ".run.in")).exists()


def test_changed_source_and_stale_attempt_are_refused(diagnostic):
    checkpoint = next(cp for cp in diagnostic["inventory"]["checkpoints"] if cp["prefix"] == diag.PREFIX)
    (diagnostic["runs"] / checkpoint["dir"] / "paw.txt").write_bytes(b"source drift")
    with pytest.raises(ValueError, match="source checkpoint"):
        diag.prepare(diagnostic["runs"])
    assert not retained(diagnostic).parent.exists()
    stale = diagnostic["directory"] / (diag.JOB + ".rank_stderr")
    stale.mkdir()
    with pytest.raises(ValueError, match="preexisting"):
        diag.validate(diagnostic["runs"])


@pytest.mark.parametrize("env", [{"NP": "64"}, {"SLURM_ARRAY_TASK_ID": "2"}])
def test_runner_cannot_expand_single_case(diagnostic, env):
    result = run(diagnostic, **env)
    assert result.returncode != 0
    assert not launches(diagnostic)
    assert not retained(diagnostic).parent.exists()


def test_stream_reassembly_never_overwrites_raw_or_combined_evidence(diagnostic):
    assert run(diagnostic).returncode == 0
    names = diag.stage_names("scf")
    before = {key: (diagnostic["directory"] / names[key]).read_bytes()
              for key in ("stdout", "launcher", "combined")}
    with pytest.raises(FileExistsError):
        diag.assemble(diagnostic["runs"], "scf")
    for key, raw in before.items():
        assert (diagnostic["directory"] / names[key]).read_bytes() == raw


def test_clean_outputs_without_retained_wavefunction_are_not_complete(diagnostic):
    assert run(diagnostic).returncode == 0
    (retained(diagnostic) / "wfcup8.hdf5").unlink()
    (diagnostic["directory"] / (diag.JOB + ".diagnostic.json")).unlink()
    record = diag.summarize(diagnostic["runs"], 0, 0)
    assert record["diagnostic_status"] == "CLEAN_REPRODUCTION"
    assert record["new_endpoint_status"] == "INCOMPLETE"
    assert record["retention_complete"] is False
    assert "wfcup8.hdf5" in record["retained_missing"]


@pytest.mark.parametrize("mutation", ["raw_stderr", "rank_metadata", "clone_receipt", "combined_missing"])
def test_summary_rereads_and_binds_every_evidence_layer(diagnostic, mutation):
    assert run(diagnostic).returncode == 0
    directory = diagnostic["directory"]
    if mutation == "raw_stderr":
        (directory / (diag.JOB + ".rank_stderr/rank007.stderr")).write_bytes(b"IEEE_INVALID_FLAG\n")
    elif mutation == "rank_metadata":
        path = directory / (diag.JOB + ".rank_audit.json")
        record = json.loads(path.read_text())
        record["ranks"][7]["flags"] = ["IEEE_INVALID_FLAG"]
        path.write_text(json.dumps(record), encoding="utf-8")
    elif mutation == "clone_receipt":
        path = directory / (diag.JOB + ".clone_receipt.json")
        record = json.loads(path.read_text())
        record["input_sha256"] = "0" * 64
        path.write_text(json.dumps(record), encoding="utf-8")
    else:
        (directory / (diag.JOB + ".out")).unlink()
    (directory / (diag.JOB + ".diagnostic.json")).unlink()
    record = diag.summarize(diagnostic["runs"], 0, 0)
    assert record["new_endpoint_status"] == "REJECTED"
    assert record["diagnostic_status"] == "OTHER_FAILURE"
    assert record["evidence_errors"]


def test_final_acceptance_recheck_controls_runner_success(diagnostic):
    projection = diagnostic["paths"]["PROJECTION"]
    text = projection.read_text()
    text = text.replace('cat "$MOCK_PAYLOADS/projection.$MOCK_PROJECTION"',
                        'echo "IEEE_INVALID_FLAG late raw evidence" >> "$MOCK_LATE_SCF_STREAM"\n'
                        'cat "$MOCK_PAYLOADS/projection.$MOCK_PROJECTION"')
    _write(projection, text, executable=True)
    _pin_script(ROOT / "anvil/64_hea_ieee_smearing.slurm",
                diagnostic["scripts"] / "64_hea_ieee_smearing.slurm", diagnostic["paths"])
    result = run(diagnostic, MOCK_LATE_SCF_STREAM=_shell_path(
        diagnostic["directory"] / (diag.JOB + ".rank_stderr/rank007.stderr")))
    assert result.returncode != 0
    assert "CLEAN REPRODUCTION: current endpoint complete" not in result.stdout
    record = result_record(diagnostic)
    assert record["new_endpoint_status"] == "REJECTED"
    assert any("differs from raw streams" in error for error in record["evidence_errors"])


def test_exact_original_deck_and_original_accepted_checkpoint(diagnostic):
    case = diagnostic
    ctx = diag.prepare(case["runs"])
    assert ctx["original_job"]["job"] == diag.ORIGINAL_JOB
    assert ctx["checkpoint"]["source_job"] == diag.SOURCE_JOB
    assert ctx["checkpoint"]["dir"].startswith("hea/numerical_2026-09-08/")
    original = case["runs"] / "hea/sensitivity_2026-09-09" / (diag.ORIGINAL_JOB + ".in")
    assert (case["directory"] / (diag.JOB + ".run.in")).read_bytes() == original.read_bytes()
    receipt = json.loads((case["directory"] / (diag.JOB + ".clone_receipt.json")).read_text())
    assert receipt["source_job"] == diag.SOURCE_JOB
    assert receipt["original_job"] == diag.ORIGINAL_JOB
    assert receipt["destination"].startswith(diag.DIRECTORY + "/")
    assert len(receipt["files"]) == 27
    for entry in receipt["files"]:
        source = case["runs"] / receipt["source"] / entry["path"]
        cloned = case["runs"] / receipt["destination"] / entry["path"]
        assert cloned.read_bytes() == source.read_bytes()
        assert not source.samefile(cloned)


def test_old_failed_smearing_output_does_not_block_isolated_reproduction(diagnostic):
    old = diagnostic["runs"] / "hea/sensitivity_2026-09-09" / (diag.ORIGINAL_JOB + ".out")
    old.write_bytes(b"rejected previous attempt IEEE_INVALID_FLAG\n")
    assert run(diagnostic).returncode == 0
    assert old.read_bytes() == b"rejected previous attempt IEEE_INVALID_FLAG\n"


def test_changed_source_acceptance_evidence_refused_before_clone(diagnostic):
    source = next(cp for cp in diagnostic["inventory"]["checkpoints"]
                  if cp["source_job"] == diag.SOURCE_JOB)
    path = diagnostic["runs"].parent / source["source_input"].replace(".run.in", ".qc.json")
    path.write_bytes(b'{"status": "REJECTED"}\n')
    with pytest.raises(ValueError, match="source raw/QC hash mismatch"):
        diag.prepare(diagnostic["runs"])
    assert not retained(diagnostic).parent.exists()


def test_reproduction_cannot_change_smearing_or_geometry(diagnostic):
    path = diagnostic["directory"] / (diag.JOB + ".in")
    path.write_bytes(path.read_bytes().replace(b"degauss = 0.005", b"degauss = 0.01"))
    with pytest.raises(ValueError, match="byte-identical"):
        diag.prepare(diagnostic["runs"])
    assert not retained(diagnostic).parent.exists()
