"""Offline launch and collection regressions; no SSH, Slurm or scientific processes."""
import copy
import datetime as dt
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import lowtail_slab_scf_diag_launch as launch


@pytest.mark.parametrize("path", ["runs\\manifest.txt", "../x", "/x", "C:/x", "a//b", "a/./b"])
def test_nonportable_paths_refused(path):
    with pytest.raises(ValueError, match="POSIX"):
        launch.portable(path)


def test_actual_spec_has_five_pinned_posix_jobs_and_old_spec_is_refused():
    current = launch.spec()
    assert len(current["stages"][launch.STAGE]["jobs"]) == 5
    historical = ROOT / "results/lowtail_slab_scf_diag_2026-09-19/pre_portability_fix/launch_spec.json"
    with pytest.raises(ValueError, match="POSIX"):
        launch.validate_spec(json.loads(historical.read_text()))


def accounting(tasks=range(1, 6)):
    return "\n".join(f"123_{task}|COMPLETED|0:0|10|128" for task in tasks)


def test_terminal_denominator_requires_every_exact_task():
    assert launch.all_terminal(launch.parse_accounting(accounting(), "123"))
    assert not launch.all_terminal(launch.parse_accounting(accounting([1, 2, 5]), "123"))
    assert not launch.all_terminal(launch.parse_accounting(accounting().replace("COMPLETED", "RUNNING", 1), "123"))
    with pytest.raises(ValueError, match="unexpected"):
        launch.parse_accounting(accounting([1, 2, 3, 4, 6]), "123")
    with pytest.raises(ValueError, match="conflicting"):
        launch.parse_accounting(accounting() + "\n123_1|FAILED|10:0|10|128", "123")
    assert launch.all_terminal(launch.parse_accounting(accounting() + "\n123.batch|COMPLETED|0:0|10|128", "123"))


def test_missing_staging_and_ambiguous_submission_do_not_resubmit(tmp_path, monkeypatch):
    monkeypatch.setattr(launch, "RESULTS", tmp_path)
    with pytest.raises(ValueError, match="staged"):
        launch.submit(None)
    launch.write("boundary.json", {"commit": "abc"})
    monkeypatch.setattr(launch, "verify_transfer", lambda client=None: {})
    calls = []
    def command(client, args, **kwargs):
        calls.append(args[0])
        if args[0] == "bash":
            raise RuntimeError("SSH disconnected after submitting; outcome unknown")
        return {"stdout": "", "rc": 0}
    monkeypatch.setattr(launch, "command", command)
    with pytest.raises(RuntimeError, match="unknown"):
        launch.submit(None)
    assert launch.read("submission_intent.json")["status"] == "SUBMISSION_ATTEMPT_PENDING"
    with pytest.raises(ValueError, match="duplicate"):
        launch.submit(None)
    assert calls.count("bash") == 1


def held_fields():
    return dict(JobId="123", ArrayJobId="123", WorkDir=launch.PROJECT,
                JobState="PENDING", Reason="JobHeldUser", NumCPUs="128", NumTasks="128",
                Requeue="0", Account="che260157", ArrayTaskId="1-5%2", MinMemoryNode="237G",
                TimeLimit="02:30:00", Partition="shared", JobName=launch.JOB_NAME,
                NumNodes="1-1", Command=launch.REMOTE + "/" + launch.SLURM,
                UserId="x-fcai3(1234)", ExcNodeList="a[001-002]", **{"CPUs/Task": "1"})


@pytest.mark.parametrize("change", [{}, {"ArrayJobId": "124"}, {"CPUs/Task": "2"},
                                  {"NumNodes": "1-2"}, {"Command": "/wrong/" + launch.SLURM},
                                  {"WorkDir": "/tmp"}, {"ArrayTaskId": "1-6%2"}])
def test_held_identity_and_resources_are_exact(tmp_path, monkeypatch, change):
    monkeypatch.setattr(launch, "RESULTS", tmp_path)
    spec = launch.spec()
    spec["exclusions"] = "a001,a002"
    monkeypatch.setattr(launch, "spec", lambda: spec)
    fields = dict(held_fields(), **change)
    def command(client, args, **kwargs):
        return {"stdout": "a001\na002\n" if args[2] == "hostnames" else
                " ".join(f"{key}={value}" for key, value in fields.items()), "rc": 0}
    monkeypatch.setattr(launch, "command", command)
    if change:
        with pytest.raises(RuntimeError, match="held"):
            launch.inspect_held(None, "123")
    else:
        assert not launch.inspect_held(None, "123")["mismatches"]


def test_remote_byte_drift_and_local_conflict_are_refused(tmp_path):
    path = tmp_path / "raw.out"
    assert launch.preserve(path, b"first") == "MIRRORED"
    assert launch.preserve(path, b"first") == "ALREADY_IDENTICAL"
    with pytest.raises(ValueError, match="refusing overwrite"):
        launch.preserve(path, b"changed")
    assert path.read_bytes() == b"first"
    class Sftp:
        calls = 0
        def stat(self, path):
            self.calls += 1
            return SimpleNamespace(st_size=3, st_mtime=self.calls)
        def open(self, path, mode):
            return io.BytesIO(b"abc")
    with pytest.raises(ValueError, match="changed"):
        launch.remote_bytes(Sftp(), "/raw.out")


@pytest.fixture
def evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(launch, "ROOT", tmp_path)
    monkeypatch.setattr(launch, "RESULTS", tmp_path / "results")
    job = dict(dir="hea/site", job="probe", site="site", scf_seconds=7200,
               projection_seconds=900, max_iterations=126)
    deck = """&CONTROL
 calculation = 'scf'
 prefix = 'probe'
 outdir = './tmp'
 pseudo_dir = './pseudo'
/
&SYSTEM
 nat = 1
/
&ELECTRONS
 conv_thr = 8.08d-8
/
ATOMIC_SPECIES
 O 15.999 O.UPF
ATOMIC_POSITIONS angstrom
 O 0 0 0 1 1 1
"""
    path = tmp_path / "runs/hea/site/probe.in"
    path.parent.mkdir(parents=True)
    path.write_bytes(deck.encode())
    job["sha256"] = launch.sha(deck.encode())
    runtime, scratch = launch.runtime_text(job)
    output = """running on 128 processor cores
number of atoms/cell = 1
Self-consistent Calculation
 iteration # 1 ecut= 80.00 Ry beta=0.10
 estimated scf accuracy < 0.00000001 Ry
!    total energy = -10.00000000 Ry
 convergence has been achieved in 1 iterations
Forces acting on atoms (cartesian axes, Ry/au):
 atom 1 type 1 force = 0.01000000 0.00000000 0.00000000
Total force = 0.010000
PWSCF : 5.00s CPU 5.00s WALL
JOB DONE.
"""
    artifacts = {".out": output.encode(), ".run.in": runtime.encode(),
                 ".projwfc.in": ("&PROJWFC\n prefix = 'probe'\n outdir = '" + scratch + "'\n lsym = .true.\n/\n").encode(),
                 ".projwfc.out": b"projection fixture"}
    qc = dict(stage=launch.STAGE, row=1, job="probe", status="COMPLETE",
              input_sha256=job["sha256"], output_sha256=launch.sha(artifacts[".out"]),
              runtime_sha256=launch.sha(artifacts[".run.in"]),
              scf_process=dict(rc=0, stop_reason=None, wall_seconds=6),
              projection_process=dict(rc=0, stop_reason=None, wall_seconds=2))
    artifacts[".qc.json"] = json.dumps(qc).encode()
    paths = {}
    for suffix, data in artifacts.items():
        paths[suffix] = tmp_path / ("probe" + suffix)
        paths[suffix].write_bytes(data)
    import projection_qc
    monkeypatch.setattr(projection_qc, "projection_check", lambda text, nat: {"nat": nat})
    task = launch.parse_accounting(accounting([1]), "123")[1]
    return job, artifacts, paths, task, qc


def test_complete_qc_is_independently_accepted(evidence):
    job, artifacts, paths, task, _ = evidence
    assert launch.validate_evidence(job, 1, artifacts, paths, task) == []


@pytest.mark.parametrize("fault", ["missing_projection", "wrong_row", "bad_hash", "altered_runtime",
                                   "stopped", "iteration_127", "severe_ieee", "wall_limit", "weak_target"])
def test_complete_receipt_cannot_override_bad_evidence(evidence, fault):
    job, artifacts, paths, task, qc = evidence
    if fault == "missing_projection":
        del artifacts[".projwfc.out"]
    elif fault == "wrong_row":
        qc["row"] = 2
    elif fault == "bad_hash":
        qc["output_sha256"] = "wrong"
    elif fault == "altered_runtime":
        artifacts[".run.in"] = artifacts[".run.in"].replace(b"8.08d-8", b"1.00d-6")
        qc["runtime_sha256"] = launch.sha(artifacts[".run.in"])
    elif fault == "stopped":
        artifacts[".KILLED"] = b"SCF iteration ceiling"
    elif fault == "wall_limit":
        qc["scf_process"]["wall_seconds"] = 7201
    else:
        if fault == "iteration_127":
            artifacts[".out"] = artifacts[".out"].replace(b"iteration # 1 ", b"iteration # 127 ")
        elif fault == "severe_ieee":
            artifacts[".out"] += b"Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG\n"
        else:
            artifacts[".out"] = artifacts[".out"].replace(b"0.00000001 Ry", b"0.00000090 Ry")
        qc["output_sha256"] = launch.sha(artifacts[".out"])
        paths[".out"].write_bytes(artifacts[".out"])
    artifacts[".qc.json"] = json.dumps(qc).encode()
    assert launch.validate_evidence(job, 1, artifacts, paths, task)


def test_collection_keeps_all_five_missing_terminal_legs(tmp_path, monkeypatch):
    monkeypatch.setattr(launch, "ROOT", tmp_path)
    monkeypatch.setattr(launch, "RESULTS", tmp_path / "results")
    jobs = [dict(dir=f"hea/site{i}", job="probe", site=f"site{i}", max_iterations=126) for i in range(5)]
    monkeypatch.setattr(launch, "spec", lambda: {"stages": {launch.STAGE: {"jobs": jobs}}})
    monkeypatch.setattr(launch, "assert_pins", lambda pins: None)
    monkeypatch.setattr(launch, "remote_bytes", lambda *args: None)
    sftp = SimpleNamespace(get_channel=lambda: SimpleNamespace(settimeout=lambda _: None), close=lambda: None)
    client = SimpleNamespace(open_sftp=lambda: sftp, close=lambda: None)
    monkeypatch.setattr(launch, "connect", lambda: client)
    result = launch.collect(launch.parse_accounting(accounting(), "123"), {})
    assert result["population"] == len(result["legs"]) == 5
    assert result["accepted"] == 0
    assert all("missing artifact .out" in leg["reasons"] for leg in result["legs"])


def test_default_wait_extends_beyond_official_outage_and_bad_poll_refused(monkeypatch):
    deadlines = []
    monkeypatch.setattr(launch, "wait", lambda deadline, poll: deadlines.append(deadline))
    launch._main(["wait"])
    assert deadlines[0] == dt.datetime(2026, 9, 23, 12, tzinfo=dt.timezone.utc)
    with pytest.raises(SystemExit):
        launch._main(["wait", "--poll", "0"])


def test_concurrent_launcher_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(launch, "RESULTS", tmp_path)
    (tmp_path / ".launcher.lock").write_text("{}")
    with pytest.raises(RuntimeError, match="already active"):
        launch.main(["auto"])


def test_source_pin_change_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(launch, "ROOT", tmp_path)
    (tmp_path / "source.py").write_bytes(b"changed")
    with pytest.raises(ValueError, match="pinned"):
        launch.assert_pins({"source.py": launch.sha(b"original")})


def test_local_collector_bytes_must_match_pushed_boundary(tmp_path, monkeypatch):
    monkeypatch.setattr(launch, "ROOT", tmp_path)
    relative = "src/dft/qe_relax_trace.py"
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_bytes(b"uncommitted parser change")
    calls = []
    def git_show(args, **kwargs):
        calls.append(args)
        return b"pushed parser"
    monkeypatch.setattr(launch.subprocess, "check_output", git_show)
    with pytest.raises(ValueError, match="pushed boundary"):
        launch.verify_boundary_bytes("a" * 40, {relative: launch.sha(path.read_bytes())})
    assert calls[0][-1] == "a" * 40 + ":" + relative


def test_failed_qc_identity_is_checked_without_projection(evidence):
    job, artifacts, paths, task, qc = evidence
    task.update(state="FAILED", exit="10:0")
    qc.update(status="KILLED", row=2)
    del qc["output_sha256"]
    del qc["runtime_sha256"]
    del artifacts[".projwfc.out"]
    artifacts[".qc.json"] = json.dumps(qc).encode()
    reasons = launch.validate_evidence(job, 1, artifacts, paths, task)
    assert "QC input/job identity mismatch" in reasons
    assert launch.identity_problems(job, 1, artifacts)
    qc["row"] = 1
    artifacts[".qc.json"] = json.dumps(qc).encode()
    assert launch.identity_problems(job, 1, artifacts) == []
    artifacts[".run.in"] += b"unexpected runtime bytes"
    assert "runtime deck differs from the permitted path-only rewrite" in launch.identity_problems(job, 1, artifacts)


@pytest.mark.parametrize("error", [OSError("SFTP interrupted"), EOFError("SFTP interrupted"), ValueError("evidence collision")])
def test_terminal_collection_retries_transport_only(tmp_path, monkeypatch, error):
    monkeypatch.setattr(launch, "RESULTS", tmp_path)
    launch.write("submission.json", dict(job_id="123", released=True))
    monkeypatch.setattr(launch, "verify_transfer", lambda: {})
    monkeypatch.setattr(launch, "assert_pins", lambda pins: None)
    monkeypatch.setattr(launch, "connect", lambda: SimpleNamespace(close=lambda: None))
    monkeypatch.setattr(launch, "command", lambda *args, **kwargs: {"stdout": accounting()})
    monkeypatch.setattr(launch.time, "sleep", lambda _: None)
    calls = []
    def collect(tasks, pins):
        calls.append(tasks)
        if len(calls) == 1:
            raise error
    monkeypatch.setattr(launch, "collect", collect)
    deadline = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=1)
    if isinstance(error, ValueError):
        with pytest.raises(ValueError, match="collision"):
            launch.watch(deadline, poll=1)
        assert len(calls) == 1
    else:
        launch.watch(deadline, poll=1)
        assert len(calls) == 2
        assert "SFTP interrupted" in launch.read("collection_error.json")["error"]


def test_expired_watch_never_attempts_a_connection(tmp_path, monkeypatch):
    monkeypatch.setattr(launch, "RESULTS", tmp_path)
    launch.write("submission.json", dict(job_id="123", released=True))
    monkeypatch.setattr(launch, "verify_transfer", lambda: {})
    monkeypatch.setattr(launch, "connect", lambda: pytest.fail("expired watch attempted SSH"))
    with pytest.raises(RuntimeError, match="deadline"):
        launch.watch(dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1), poll=1)
    with pytest.raises(ValueError, match="timezone-aware"):
        launch.watch(dt.datetime(2026, 9, 25), poll=1)


def test_array_task_field_matches_scontrol_for_single_and_multi_task_arrays():
    assert launch.array_task_field(5, 2) == "1-5%2"
    assert launch.array_task_field(2, 2) == "1-2%2"
    assert launch.array_task_field(1, 1) == "1%1"

