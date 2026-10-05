"""Offline supervisor adversaries and process doubles for pa_catalyst_retest; never launch QE/Slurm.

Sibling of test_pa_catalyst_trial.py (kept byte-for-byte for the frozen controller): same registered
sequence, shape and ceilings, bound to pa_qe_adapter_v2 and the 2026-10-04 spec.  The final section reads
real QE 7.5 logs through the supervisor's own regular expressions.
"""
import copy
import io
import json
import os
import pathlib
from pathlib import Path
import subprocess
import sys
import types
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/dft"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pa_catalyst_retest as trial
import pa_qe_adapter_v2 as adapter
import qe75_real_fixtures as real_files


SOURCE = Path(__file__).resolve().parents[1] / trial.SOURCE_DECK_SUFFIX
FIXTURES = Path(__file__).resolve().parents[1] / "tests/fixtures/qe75_real"


def replay_block():
    return {"root": str(FIXTURES), "logged_upf_dir": real_files.LOGGED_CONTROL_UPF_DIR,
            "files": [{"path": rel, "sha256": trial.sha256_file(FIXTURES / rel)} for rel in sorted(trial.REPLAY_FILES)],
            "expected": copy.deepcopy(trial.REPLAY_EXPECTED)}


def real_upf_pins():
    """{filename: sha256 of the uncompressed UPF} for the five UPFs the real control call consumed."""
    return {Path(row["fixture"]).name[:-3]: row["sha256"] for row in real_files.manifest()
            if row["fixture"].startswith("control/common_pseudo/")}


def spec_for(tmp_path):
    parent = tmp_path / "sts_pa_catalyst_retest_2026-10-04"
    parent.mkdir()
    source = parent / trial.SOURCE_DECK_SUFFIX
    source.parent.mkdir(parents=True)
    source.write_bytes(SOURCE.read_bytes())
    pins = [{"path": str(Path(module.__file__).absolute()),
             "sha256": trial.sha256_file(Path(module.__file__))}
            for module in (trial, adapter, adapter.contract)]
    return {"schema": "pa-catalyst-retest-v1", "date": "2026-10-04", "target": trial.TARGET,
            "source_deck": {"path": str(source), "sha256": trial.sha256_file(source)},
            "pw_x": {"path": str(parent / "pw.x"), "sha256": trial.QE_SHA256},
            "mpirun": {"path": str(parent / "mpirun"), "sha256": trial.MPI_SHA256},
            "source_review": {"path": str(parent / "source_review.md"), "sha256": "1" * 64},
            "dependencies": pins,
            "upfs": [{"path": str(parent / name), "sha256": "2" * 64}
                     for name in ("Co_pbe_v1.2.uspp.F.UPF", "cr_pbe_v1.5.uspp.F.UPF",
                                  "Cu.paw.z_11.ld1.psl.v1.0.0-low.upf", "mn_pbe_v1.5.uspp.F.UPF",
                                  "O.pbe-n-kjpaw_psl.0.1.UPF")],
            "initial_seed": {"root": trial.SEED_ROOT,
                "files": [{"path": name, "size_bytes": 1, "sha256": digest}
                          for name, digest in trial.SEED_FILES.items()]},
            "trial_parent": str(parent), "trial_root": str(parent / "trial_results"),
            "caps": copy.deepcopy(trial.CAPS), "parallel_shape": copy.deepcopy(trial.SHAPE),
            "allocation": {"account": "che260157", "partition": "wholenode", "cpus": 128,
                "tasks": 128, "cpus_per_task": 1, "billing": 128, "time_limit_seconds": 57600,
                "memory_gib": 200, "max_cpu_su": 2048}, "preflight_replay": replay_block(),
            "optional_negative_control": False}


def allocation_text(**changes):
    values = {"JobId": "123", "Account": "che260157", "Partition": "wholenode",
              "JobState": "RUNNING", "NumNodes": "1", "NumCPUs": "128", "NumTasks": "128",
              "CPUs/Task": "1", "Requeue": "0", "TimeLimit": "16:00:00", "RunTime": "00:00:01",
              "AllocTRES": "cpu=128,mem=200G,node=1,billing=128", "NodeList": "a001",
              "Restarts": "0", "BatchFlag": "1", "Dependency": "(null)"}
    values.update(changes)
    return " ".join(key + "=" + value for key, value in values.items())


@pytest.mark.parametrize("path,value", [
    (("caps", "max_calls"), 7), (("caps", "per_call_seconds"), 7201),
    (("caps", "qe_max_seconds"), 7100), (("caps", "aggregate_seconds"), 57601),
    (("caps", "cleanup_seconds"), 0), (("allocation", "memory_gib"), 201),
    (("allocation", "tasks"), 64), (("allocation", "max_cpu_su"), 2049),
    (("parallel_shape", "ntasks"), 128), (("parallel_shape", "npool"), 4),
    (("parallel_shape", "nthreads"), True), (("pw_x", "sha256"), "0" * 64),
    (("source_deck", "sha256"), "0" * 64),
])
def test_resource_or_identity_expansion_refused(tmp_path, path, value):
    spec = spec_for(tmp_path)
    spec[path[0]][path[1]] = value
    with pytest.raises(trial.TrialError):
        trial.validate_spec(spec)


def test_four_file_seed_is_initialization_not_history(tmp_path):
    spec = spec_for(tmp_path)
    assert trial.validate_spec(spec) is spec
    spec["initial_seed"]["files"].append({"path": "wfc1.hdf5", "size_bytes": 1, "sha256": "3" * 64})
    with pytest.raises(trial.TrialError, match="four-file"):
        trial.validate_spec(spec)


@pytest.mark.parametrize("changes", [
    {"Account": "other"}, {"Partition": "shared"}, {"JobState": "PENDING"},
    {"NumCPUs": "256"}, {"NumTasks": "1"}, {"CPUs/Task": "128"}, {"Requeue": "1"},
    {"ArrayJobId": "123"}, {"NumNodes": "2"}, {"TimeLimit": "16:00:01"},
    {"AllocTRES": "cpu=128,mem=201G,node=1,billing=128"},
    {"AllocTRES": "cpu=128,mem=200G,node=1,billing=256"},
    {"AllocTRES": "cpu=128,node=1,billing=128"},
    {"AllocTRES": "cpu=128,mem=200G,node=1,billing=128,gres/gpu=1"},
    {"NodeList": "(null)"}, {"RunTime": "16:00:00"},
    {"Restarts": "1"}, {"BatchFlag": "0"}, {"Dependency": "afterok:123"},
])
def test_live_adverse_allocations_refused(changes):
    with pytest.raises(trial.TrialError):
        trial.validate_allocation(allocation_text(**changes), "123")


def test_actual_allocation_and_xml_tasks_are_distinct():
    receipt = trial.validate_allocation(allocation_text(), "123")
    assert receipt["fields"]["NumTasks"] == "128"
    assert trial.SHAPE["ntasks"] == 1
    assert receipt["allocated_tres"]["billing"] == "128"
    assert receipt["remaining_seconds"] == 57599


def test_budget_reserves_full_call_and_cleanup_without_shrinking():
    value = object.__new__(trial.Trial)
    value.start, value.calls, value.active, value.clock = 0, 0, False, lambda: 0
    with pytest.raises(trial.TrialError, match="full registered"):
        value.budget({"remaining_seconds": 7319})
    value.budget({"remaining_seconds": 7320})
    value.calls = 6
    with pytest.raises(trial.TrialError):
        value.budget({"remaining_seconds": 50000})
    value.calls, value.active = 0, True
    with pytest.raises(trial.TrialError, match="parallel"):
        value.budget({"remaining_seconds": 50000})
    value.active, value.clock = False, lambda: 50281
    with pytest.raises(trial.TrialError):
        value.budget({"remaining_seconds": 50000})


def test_spec_requires_exact_external_pin(tmp_path):
    path = tmp_path / "launch_spec.json"
    path.write_text(json.dumps(spec_for(tmp_path)), encoding="utf-8")
    with pytest.raises(trial.TrialError):
        trial.load_spec(path, "")
    assert trial.load_spec(path, trial.sha256_file(path))["target"] == trial.TARGET
    with pytest.raises(trial.TrialError, match="changed"):
        trial.load_spec(path, "0" * 64)


def test_complete_checkpoint_preserves_nested_files_and_empty_directories(tmp_path):
    source = tmp_path / "scratch"
    (source / "save" / "nested").mkdir(parents=True)
    (source / "empty").mkdir()
    (source / "save" / "nested" / "wfc.hdf5").write_bytes(b"all-wavefunction-bytes")
    (source / "history.bfgs").write_bytes(b"history")
    before = trial.inventory(source)
    copied = trial.copy_tree(source, tmp_path / "copy")
    assert copied["source_before"] == copied["source_after"] == before
    assert copied["destination"]["sha256"] == before["sha256"]
    assert "empty" in copied["destination"]["directories"]
    assert (tmp_path / "copy" / "save" / "nested" / "wfc.hdf5").read_bytes() == b"all-wavefunction-bytes"
    with pytest.raises(trial.TrialError, match="exists"):
        trial.copy_tree(source, tmp_path / "copy")
    with pytest.raises(trial.TrialError):
        trial.copy_tree(source, source / "alias")


def test_distinct_wfc_tree_is_required_in_snapshot(tmp_path):
    outdir, wave = tmp_path / "outdir", tmp_path / "wave"
    outdir.mkdir()
    wave.mkdir()
    (outdir / "data.xml").write_bytes(b"XML")
    (wave / "wfc.dat").write_bytes(b"distinct-WFC")
    copied = trial.copy_checkpoint(outdir, tmp_path / "snapshot", wave)
    assert copied["wfcdir"] is not None
    assert copied["copies"]["wfcdir"]["destination"]["files"][0]["path"] == "wfc.dat"
    with pytest.raises(trial.TrialError, match="overlaps"):
        trial.checkpoint_inventory(outdir, outdir)


def test_changed_source_during_copy_is_retained_and_refused(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / "state").write_bytes(b"first")
    original = trial._copy_ordinary_tree
    def mutate(*args, **kwargs):
        result = original(*args, **kwargs)
        (source / "state").write_bytes(b"changed")
        return result
    monkeypatch.setattr(trial, "_copy_ordinary_tree", mutate)
    with pytest.raises(trial.TrialError, match="source mutation"):
        trial.copy_tree(source, tmp_path / "failed-copy")
    assert (tmp_path / "failed-copy" / "state").read_bytes() == b"first"


def test_checkpoint_symlinks_and_hardlinks_refused(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "state").write_bytes(b"state")
    try:
        os.link(source / "state", source / "alias")
    except OSError:
        pytest.skip("filesystem cannot exercise hardlinks")
    with pytest.raises(trial.TrialError, match="hardlinked|alias"):
        trial.inventory(source)


def test_external_hardlinked_binary_accepts_exact_read_pin_but_mutable_aliases_fail(tmp_path):
    executable = tmp_path / "pw.x"
    executable.write_bytes(b"pinned immutable external runtime")
    try:
        os.link(executable, tmp_path / "conda-package-cache-peer")
    except OSError:
        pytest.skip("filesystem cannot exercise external runtime hardlinks")
    pin = {"path": str(executable), "sha256": trial.sha256_file(executable)}
    assert executable.stat().st_nlink == 2
    checked = trial.verify_pin(pin, "pw_x", allow_external_hardlinks=True)
    assert checked["sha256"] == pin["sha256"]
    with pytest.raises(trial.TrialError, match="unaliased"):
        trial.verify_pin(pin, "mutable trial input")
    with pytest.raises(trial.TrialError, match="hardlinked|alias"):
        trial.inventory(tmp_path)
    executable.write_bytes(b"runtime drift through either linked name")
    with pytest.raises(trial.TrialError, match="changed"):
        trial.verify_pin(pin, "pw_x", allow_external_hardlinks=True)


def test_thread_and_xml_history_environment():
    env = trial.thread_environment()
    assert env["MAX_XML_STEPS"] == "0"
    assert env["OMP_DYNAMIC"] == "FALSE"
    assert all(env[name] == "1" for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "BLIS_NUM_THREADS"))


class Clock:
    def __init__(self):
        self.value = 0
    def __call__(self):
        return self.value
    def sleep(self, seconds):
        self.value += seconds


class FakeProcess:
    pid = 918273
    def __init__(self, clock, text, *, finish=0.02):
        self.clock, self.finish = clock, finish
        self.stdout, self.stderr = io.StringIO(text), io.StringIO("")
        self.returncode = None
    def poll(self):
        if self.clock.value >= self.finish:
            self.returncode = 255
        return self.returncode
    def wait(self, timeout=None):
        if self.poll() is None:
            raise subprocess.TimeoutExpired("fake", timeout)
        return self.returncode


@pytest.fixture
def immediate_streams(monkeypatch):
    original = trial.StreamCapture
    class ImmediateCapture(original):
        def __init__(self, *args):
            super().__init__(*args)
            self.thread = types.SimpleNamespace(start=self._read, join=lambda **kwargs: None,
                                                is_alive=lambda: False)
    monkeypatch.setattr(trial, "StreamCapture", ImmediateCapture)


def test_process_double_registers_cycle1_single_exit_and_immediate_streams(tmp_path, immediate_streams):
    clock = Clock()
    proc = FakeProcess(clock, "number of scf cycles = 1\nnumber of bfgs steps = 0\n", finish=0.05)
    popen = Mock(return_value=proc)
    receipt = trial.run_arm(name="candidate", argv=["mpirun", "pw.x"], cwd=tmp_path,
        prefix=trial.PREFIX, target_cycle=1, env={}, clock=clock, sleep=clock.sleep, popen=popen)
    assert receipt["stop_reason"] == "registered-evaluated-boundary"
    assert receipt["stop_observed_cycles"] == [1]
    assert (tmp_path / (trial.PREFIX + ".EXIT")).exists()
    assert (tmp_path / "stdout.log").read_text().startswith("number of scf cycles = 1")
    assert popen.call_args.kwargs["start_new_session"] is True


@pytest.mark.parametrize("text,expected", [
    ("iteration # 127\n! total energy = -7551 Ry\n", "HEA4-SCF-iteration-127"),
    ("Error in routine x\n", "failure-marker"),
    ("number of scf cycles = 2\n", "missed-evaluated-boundary"),
    ("number of scf cycles = 1\nnumber of scf cycles = 2\n", "missed-evaluated-boundary"),
    ("Maximum CPU time exceeded\n", "solver-time-or-nstep-limit"),
])
def test_process_double_failure_or_missed_boundary_cannot_be_accepted(tmp_path, text, expected, immediate_streams):
    clock = Clock()
    proc = FakeProcess(clock, text, finish=0.1)
    receipt = trial.run_arm(name="candidate", argv=["pw.x"], cwd=tmp_path, prefix=trial.PREFIX,
        target_cycle=1, env={}, clock=clock, sleep=clock.sleep, popen=Mock(return_value=proc))
    assert receipt["stop_reason"] == expected
    assert receipt["production_accepted"] is False


def test_hard_timeout_tears_down_only_owned_process_group(tmp_path, monkeypatch, immediate_streams):
    clock = Clock()
    proc = FakeProcess(clock, "", finish=99999)
    teardown = Mock(side_effect=lambda owned, **kwargs: setattr(owned, "returncode", -9) or {"owned_process_group": owned.pid})
    monkeypatch.setattr(trial, "teardown_process_group", teardown)
    def sleep(_):
        clock.value += 60
    receipt = trial.run_arm(name="fresh", argv=["pw.x"], cwd=tmp_path, prefix=trial.PREFIX,
        target_cycle=None, env={}, clock=clock, sleep=sleep, popen=Mock(return_value=proc))
    assert receipt["timed_out"] is True
    assert receipt["elapsed_seconds"] <= 7200
    teardown.assert_called_once_with(proc, deadline=7200, clock=clock)


def test_registered_stop_can_finish_cleanup_after_qe_soft_limit_within_hard_cap(tmp_path, immediate_streams):
    clock = Clock()
    proc = FakeProcess(clock, "number of scf cycles = 1\n", finish=7100)
    def sleep(_):
        clock.value += 10
    receipt = trial.run_arm(name="candidate", argv=["pw.x"], cwd=tmp_path, prefix=trial.PREFIX,
        target_cycle=1, env={}, clock=clock, sleep=sleep, popen=Mock(return_value=proc))
    assert receipt["stop_reason"] == "registered-evaluated-boundary"
    assert receipt["timed_out"] is False
    assert receipt["within_per_call_cap"] is True
    assert receipt["elapsed_seconds"] == 7100


def test_teardown_waits_share_remaining_literal_deadline(tmp_path, monkeypatch):
    clock = Clock()
    clock.value = 7198
    waits, signals = [], []
    class UnreapedProcess:
        pid = 812345
        def poll(self):
            return None
        def wait(self, *, timeout):
            waits.append(timeout)
            clock.value += timeout
            raise subprocess.TimeoutExpired("owned fake process", timeout)
    monkeypatch.setattr(trial.os, "killpg", lambda pid, sig: signals.append((pid, sig)), raising=False)
    if not hasattr(trial.signal, "SIGKILL"):
        monkeypatch.setattr(trial.signal, "SIGKILL", 9, raising=False)
        signals_enum = trial.signal.Signals
        monkeypatch.setattr(trial.signal, "Signals", lambda value:
            types.SimpleNamespace(name="SIGKILL") if value == 9 else signals_enum(value))
    result = trial.teardown_process_group(UnreapedProcess(), deadline=7200, clock=clock)
    assert waits == [2]
    assert clock.value == 7200
    assert (812345, trial.signal.SIGKILL) in signals
    assert result["deadline_exhausted"] is True
    assert result["unreaped_leader"] is True


def test_slow_teardown_and_both_stalled_pipes_cannot_extend_literal_cap(tmp_path, monkeypatch):
    clock = Clock()
    proc = FakeProcess(clock, "number of scf cycles = 1\n", finish=99999)
    joins = []
    class StalledCapture:
        def __init__(self, pipe, destination):
            self.text = pipe.read()
            self.error = None
            destination.write_text(self.text, encoding="utf-8")
            self.thread = types.SimpleNamespace(start=lambda: None, join=self.join, is_alive=lambda: True)
        def get(self):
            return self.text
        def join(self, *, timeout):
            joins.append(timeout)
            clock.value += timeout
    def popen(*args, **kwargs):
        clock.value = 7190  # Even delayed process setup cannot replenish cleanup time.
        return proc
    def slow_teardown(owned, *, deadline, clock):
        clock.value += min(8, max(0, deadline - clock()))
        owned.returncode = -9
        return {"owned_process_group": owned.pid}
    teardown = Mock(side_effect=slow_teardown)
    monkeypatch.setattr(trial, "StreamCapture", StalledCapture)
    monkeypatch.setattr(trial, "teardown_process_group", teardown)
    result = trial.run_arm(name="candidate", argv=["pw.x"], cwd=tmp_path, prefix=trial.PREFIX,
        target_cycle=1, env={}, clock=clock, sleep=clock.sleep, popen=popen)
    assert result["elapsed_seconds"] == 7200
    assert result["within_per_call_cap"] is True
    assert result["timed_out"] is True and "remained open" in result["supervisor_error"]
    assert joins == [2, 0, 0, 0]
    teardown.assert_called_once_with(proc, deadline=7200, clock=clock)


def execution_double(spec, *, render=None, process_changes=None, scf_counts=None):
    process_changes = process_changes or {}
    facade = types.SimpleNamespace(
        parse_deck=adapter.parse_deck, render_trial_deck=render or adapter.render_trial_deck,
        validate_upfs=lambda *args: {}, require_expected_first_threshold=lambda *args: True)
    def read(*args, **kwargs):
        parsed = adapter.parse_deck(args[0])
        return {"scf_counts": scf_counts if scf_counts is not None else [1],
                "first_conv_thr_Ry": 1e-6, "optimizer_counts": [0],
                "xml_settings_identity": "3" * 64, "evidence_sha256": "4" * 64,
                "evaluations": [{"geometry": geometry(0)}], "proposal_geometry": geometry(1),
                "input": parsed}
    facade.read_qe_arm = read
    def run(**kwargs):
        cwd = kwargs["cwd"]
        (cwd / "stdout.log").write_text("number of bfgs steps = 0\n", encoding="utf-8")
        (cwd / "stderr.log").write_text("", encoding="utf-8")
        return dict({"returncode": 255, "timed_out": False, "within_per_call_cap": True,
                     "stop_reason": "registered-evaluated-boundary"}, **process_changes)
    runner = Mock(side_effect=run)
    value = trial.Trial(spec, adapter=facade, runner=runner, clock=lambda: 0)
    value.root.mkdir()
    value.allocation = Mock(return_value={"remaining_seconds": 57599})
    value.verify_sources = Mock()
    def init(outdir):
        outdir.mkdir()
        return {"full_continuity_checkpoint": False}
    value.initialize_density = init
    return value, runner


def test_actual_deck_operational_controls_and_command_shape_checked_before_launch(tmp_path):
    value, runner = execution_double(spec_for(tmp_path))
    result = value.execute("candidate", kind="candidate", target_cycle=1,
                           expected_cycles=[1], expected_steps=1)
    kwargs = runner.call_args.kwargs
    assert kwargs["argv"][1:3] == ["-np", "128"]
    assert kwargs["argv"][4:8] == ["-nk", "8", "-ndiag", "16"]
    assert kwargs["env"]["MAX_XML_STEPS"] == "0"
    actual = adapter.parse_deck(value.root / "candidate" / "input.in")
    assert actual["operations"]["nstep"] == 30
    assert actual["operations"]["max_seconds"] == 7080
    assert actual["settings_identity"] == value.expected_settings["settings_identity"]
    assert "outdir" not in result["raw"]  # Never mutate the raw-evidence digest.
    assert value.calls == 1 and value.allocation.call_count == 2


@pytest.mark.parametrize("old,new", [
    ("nspin = 2", "nspin = 1"), ("mixing_beta = 0.3", "mixing_beta = 0.2"),
    ("max_seconds = 7080", "max_seconds = 7000"), ("nstep = 30", "nstep = 3"),
    ("startingwfc = 'atomic+random'", "startingwfc = 'file'"),
])
def test_adverse_rendered_deck_refused_before_any_qe_call(tmp_path, old, new):
    def render(*args, **kwargs):
        return adapter.render_trial_deck(*args, **kwargs).replace(old, new)
    value, runner = execution_double(spec_for(tmp_path), render=render)
    with pytest.raises(trial.TrialError):
        value.execute("candidate", kind="candidate", target_cycle=1, expected_cycles=[1], expected_steps=1)
    assert value.calls == 0
    runner.assert_not_called()


@pytest.mark.parametrize("changes", [
    {"timed_out": True}, {"within_per_call_cap": False}, {"supervisor_error": "broken pipe"},
    {"HEA4_stall_observed": True}, {"failure_marker_observed": True},
    {"stop_reason": "missed-evaluated-boundary"},
])
def test_failed_actual_call_retains_receipt_and_never_retries(tmp_path, changes):
    value, runner = execution_double(spec_for(tmp_path), process_changes=changes)
    with pytest.raises(trial.TrialError):
        value.execute("candidate", kind="candidate", target_cycle=1, expected_cycles=[1], expected_steps=1)
    assert value.calls == 1 and runner.call_count == 1
    assert value.receipt["calls"][0]["status"] == "INCONCLUSIVE"
    assert (value.root / "trial_receipt.json").exists()


def test_negative_requires_actual_startup_deletion_not_initializer_header(tmp_path):
    value, runner = execution_double(spec_for(tmp_path), scf_counts=[1, 2, 3])
    with pytest.raises(trial.TrialError, match="actual startup deletion"):
        value.execute("negative", kind="negative", target_cycle=3,
                      expected_cycles=[1, 2, 3], expected_steps=3, geometry=adapter.parse_deck(SOURCE)["geometry"])
    assert runner.call_count == 1


def geometry(value):
    return {"unit": "bohr", "species": ["Cu"], "positions": [[value, 0, 0]],
            "cell": [[10, 0, 0], [0, 10, 0], [0, 0, 10]], "fixed_flags": [[0, 0, 0]]}


class OrchestrationDouble(trial.Trial):
    def __init__(self, spec, action, *, fresh_failure=False, fail_resume=False,
                 reseed_energy=-100.0, fail_reseed=False):
        self.spec, self.root, self.calls, self.active = spec, Path(spec["trial_root"]), 0, False
        self.clock, self.start = lambda: 1, 0
        self.order, self.arguments = [], []
        self.action, self.fresh_failure, self.fail_resume = action, fresh_failure, fail_resume
        self.reseed_energy, self.fail_reseed = reseed_energy, fail_reseed
        self.receipt = {"calls": [], "scientific_status": "INCONCLUSIVE", "scheduler_status": "COMPLIANT",
                        "production_accepted": False}
        self.adapter = types.SimpleNamespace(
            contract=adapter.contract, _validate_arm=Mock(), _geometry_matches=adapter._geometry_matches,
            read_bfgs=lambda *args, **kwargs: {"scf_count": 1, "bfgs_count": 1},
            checkpoint_inventory=lambda out, wave=None: trial.checkpoint_inventory(Path(out), Path(wave) if wave else None),
            pre_resume_decision=self.decide,
            audit_consumption=lambda *args, **kwargs: {"raw_consumption_audit": {"passed": True}},
            compare_trajectories=lambda left, right: {"within_tolerances": True, "evaluations": len(left)})
    def common_upfs(self):
        pass
    def verify_sources(self):
        pass
    def decide(self, warm, fresh, *args, **kwargs):
        self.order.append("decision")
        assert self.order[-2] == "fresh"
        return {"action": "HOLD" if fresh is None else self.action, "production_accepted": False}
    def execute(self, name, **kwargs):
        self.order.append(name)
        self.arguments.append((name, kwargs))
        self.calls += 1
        self.receipt["calls"].append({"name": name})
        if name == "fresh" and self.fresh_failure:
            raise trial.TrialError("fresh SCF failed")
        if name == "resumed" and self.fail_resume:
            raise trial.TrialError("resume failed; no retry")
        if name == "reseed" and self.fail_reseed:
            raise trial.TrialError("reseed failed; no retry")
        outdir = self.root / name / "outdir"
        outdir.mkdir(parents=True)
        (outdir / "history.bfgs").write_bytes(b"whole optimizer history")
        (outdir / "data.xml").write_bytes(b"whole XML history")
        (outdir / "nested").mkdir()
        (outdir / "nested" / "wfc.dat").write_bytes(b"complete WFC")
        counts = kwargs["expected_cycles"]
        frames = [{"geometry": geometry(cycle-1), "energy_Ry": -100 + cycle} for cycle in counts]
        if name == "fresh":
            frames = [{"geometry": geometry(0), "energy_Ry": -100}]
        elif name == "reseed":
            frames[0]["energy_Ry"] = self.reseed_energy
        source = adapter._source(outdir / "data.xml")
        for frame in frames:
            frame.update(status="CONVERGED", geometry_role="evaluated", energy_unit="Ry",
                         geometry_unit="bohr", settings_identity="5" * 64, source=copy.deepcopy(source))
        return {"raw": {"evaluations": frames, "proposal_geometry": geometry(1),
                        "settings_identity": "5" * 64, "xml_settings_identity": "6" * 64,
                        "sources": {"xml": source}},
                "outdir": str(outdir), "wfcdir": None}


def thaw(path):
    if path.exists():
        for child in path.rglob("*"):
            child.chmod(0o700 if child.is_dir() else 0o600)
        path.chmod(0o700)


@pytest.mark.parametrize("action,expected_order,status", [
    ("RESUME_CANDIDATE", ["control", "candidate", "fresh", "decision", "resumed"], "PASS_ONE_BOUNDARY"),
    ("HOLD", ["control", "candidate", "fresh", "decision"], "HOLD"),
    ("RESEED_CANDIDATE", ["control", "candidate", "fresh", "decision", "reseed"], "RESEED_BRANCH_ONLY"),
])
def test_fresh_precedes_branch_and_reseed_is_intentional_reset(tmp_path, monkeypatch, action, expected_order, status):
    monkeypatch.setattr(trial, "preflight", lambda *args: {"status": "PREFLIGHT_PASS"})
    harness = OrchestrationDouble(spec_for(tmp_path), action)
    try:
        result = harness.run()
        assert harness.order == expected_order
        assert result["scientific_status"] == status
        assert result["production_accepted"] is False
        if action == "RESUME_CANDIDATE":
            name, args = harness.arguments[-1]
            assert name == "resumed" and args["expected_cycles"] == [2, 3]
            assert args["geometry"] == geometry(1)
            assert result["continuity"]["evaluations"] == 3
        if action == "RESEED_CANDIDATE":
            name, args = harness.arguments[-1]
            assert args["geometry"] == geometry(0)
            assert "checkpoint" not in args and "seed_fresh" in args
            assert result["intentional_history_reset"] is True
            assert result["continuity_validated"] is False
            assert result["reseed_branch_attempted"] is True
            assert result["genuine_lower_state_reseed_validated"] is True
            assert result["reseed_lower_state_binding"]["passed"] is True
    finally:
        thaw(harness.root)


def test_failed_fresh_is_hold_with_no_resume_or_reseed(tmp_path, monkeypatch):
    monkeypatch.setattr(trial, "preflight", lambda *args: {})
    harness = OrchestrationDouble(spec_for(tmp_path), "RESUME_CANDIDATE", fresh_failure=True)
    try:
        result = harness.run()
        assert result["scientific_status"] == "HOLD"
        assert harness.order == ["control", "candidate", "fresh", "decision"]
        assert harness.calls == 3
    finally:
        thaw(harness.root)


def test_failed_resume_retains_failure_without_retry(tmp_path, monkeypatch):
    monkeypatch.setattr(trial, "preflight", lambda *args: {})
    harness = OrchestrationDouble(spec_for(tmp_path), "RESUME_CANDIDATE", fail_resume=True)
    try:
        result = harness.run()
        assert result["scientific_status"] == "INCONCLUSIVE"
        assert result["scheduler_status"] == "COMPLIANT"
        assert harness.order.count("resumed") == 1
        assert harness.calls == 4
        assert "no retry" in result["error"]
        assert (harness.root / "trial_receipt.json").exists()
    finally:
        thaw(harness.root)


def test_optional_negative_copies_history_only_after_valid_resume(tmp_path, monkeypatch):
    monkeypatch.setattr(trial, "preflight", lambda *args: {})
    spec = spec_for(tmp_path)
    spec["optional_negative_control"] = True
    harness = OrchestrationDouble(spec, "RESUME_CANDIDATE")
    try:
        result = harness.run()
        assert harness.order == ["control", "candidate", "fresh", "decision", "resumed", "negative"]
        assert harness.calls == 5 and result["scientific_status"] == "PASS_ONE_BOUNDARY"
        _, args = harness.arguments[-1]
        assert args["checkpoint"]["immutable"] is True and args["geometry"] == geometry(1)
    finally:
        thaw(harness.root)


def test_density_reseed_returning_upper_state_retains_attempt_without_retry(tmp_path, monkeypatch):
    monkeypatch.setattr(trial, "preflight", lambda *args: {})
    harness = OrchestrationDouble(spec_for(tmp_path), "RESEED_CANDIDATE", reseed_energy=-99.0)
    try:
        result = harness.run()
        assert harness.order == ["control", "candidate", "fresh", "decision", "reseed"]
        assert harness.calls == 4 and harness.order.count("reseed") == 1
        assert result["scientific_status"] == "INCONCLUSIVE"
        assert result["reseed_branch_status"] == "RESEED_ATTEMPT"
        assert result["reseed_branch_attempted"] is True
        assert result["genuine_lower_state_reseed_validated"] is False
        assert result["continuity_validated"] is False
        assert result["production_accepted"] is False
        binding = result["reseed_lower_state_binding"]
        assert binding["raw_source_binding_validated"] is True
        assert binding["reseed_first_energy_Ry"] == binding["warm_first_energy_Ry"]
        assert binding["matches_fresh_energy"] is False
        assert (harness.root / "reseed_lower_state_binding.json").exists()
    finally:
        thaw(harness.root)


def test_reseed_failure_retains_attempt_flag_before_invocation(tmp_path, monkeypatch):
    monkeypatch.setattr(trial, "preflight", lambda *args: {})
    harness = OrchestrationDouble(spec_for(tmp_path), "RESEED_CANDIDATE", fail_reseed=True)
    try:
        result = harness.run()
        assert result["scientific_status"] == "INCONCLUSIVE"
        assert result["reseed_branch_status"] == "RESEED_ATTEMPT"
        assert result["reseed_branch_attempted"] is True
        assert result["genuine_lower_state_reseed_validated"] is False
        assert harness.calls == 4 and harness.order.count("reseed") == 1
    finally:
        thaw(harness.root)


def binding_arms(tmp_path, *, warm_energy=-99.0, fresh_energy=-100.0, reseed_energy=-100.0):
    arms = []
    for name, energy in (("warm", warm_energy), ("fresh", fresh_energy), ("reseed", reseed_energy)):
        xml = tmp_path / (name + ".xml")
        xml.write_text("source-bound first evaluated state\n", encoding="utf-8")
        source = adapter._source(xml)
        frame = {"geometry": geometry(0), "energy_Ry": energy, "status": "CONVERGED",
                 "geometry_role": "evaluated", "energy_unit": "Ry", "geometry_unit": "bohr",
                 "settings_identity": "5" * 64, "source": copy.deepcopy(source)}
        arms.append({"evaluations": [frame], "settings_identity": "5" * 64,
                     "xml_settings_identity": "6" * 64, "sources": {"xml": source}})
    facade = types.SimpleNamespace(contract=adapter.contract, _validate_arm=Mock(),
                                  _geometry_matches=adapter._geometry_matches)
    return arms, facade


def test_reseed_matching_fresh_within_tolerance_still_needs_strict_warm_drop(tmp_path):
    conversion = adapter.contract.RY_MEV
    arms, facade = binding_arms(tmp_path, warm_energy=0.0,
        fresh_energy=-10.001 / conversion, reseed_energy=-9.999 / conversion)
    result = trial.validate_reseed_binding(*arms, adapter=facade)
    assert result["matches_fresh_energy"] is True
    assert result["still_strictly_lower_than_warm"] is False
    assert result["passed"] is False


@pytest.mark.parametrize("adversary", ["nan", "geometry", "settings", "xml_settings", "xml_drift", "wrong_xml_source"])
def test_reseed_binding_rejects_nonfinite_different_geometry_settings_or_source(tmp_path, adversary):
    arms, facade = binding_arms(tmp_path)
    reseed = arms[2]
    if adversary == "nan":
        reseed["evaluations"][0]["energy_Ry"] = float("nan")
    elif adversary == "geometry":
        reseed["evaluations"][0]["geometry"] = geometry(1)
    elif adversary == "settings":
        reseed["settings_identity"] = "7" * 64
    elif adversary == "xml_settings":
        reseed["xml_settings_identity"] = "7" * 64
    elif adversary == "xml_drift":
        Path(reseed["sources"]["xml"]["path"]).write_text("changed raw XML\n", encoding="utf-8")
    else:
        reseed["evaluations"][0]["source"] = arms[1]["sources"]["xml"]
    result = trial.validate_reseed_binding(*arms, adapter=facade)
    assert result["passed"] is False and result["production_accepted"] is False
    assert facade._validate_arm.call_count == 3


# ---------------------------------------------------------------- identity of the re-test (it cannot be mistaken for the frozen trial)

@pytest.mark.parametrize("path,value", [
    (("schema",), "pa-catalyst-trial-v1"), (("date",), "2026-10-03"),
    (("trial_parent",), "/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03"),
])
def test_frozen_trial_identity_is_refused_by_the_retest_controller(tmp_path, path, value):
    spec = spec_for(tmp_path)
    if path[0] == "trial_parent":
        spec["trial_parent"] = value
        spec["trial_root"] = value + "/trial_results"
    else:
        spec[path[0]] = value
    with pytest.raises(trial.TrialError):
        trial.validate_spec(spec)


def test_dependency_pins_must_name_the_corrected_modules(tmp_path):
    spec = spec_for(tmp_path)
    for pin in spec["dependencies"]:
        if Path(pin["path"]).name == "pa_qe_adapter_v2.py":
            pin["path"] = pin["path"].replace("pa_qe_adapter_v2.py", "pa_qe_adapter.py")
    with pytest.raises(trial.TrialError, match="dependency pins required"):
        trial.validate_spec(spec)


def test_default_adapter_is_the_corrected_module(tmp_path):
    value = trial.Trial(spec_for(tmp_path), clock=lambda: 0)
    assert value.adapter.__name__ == "pa_qe_adapter_v2"
    assert Path(value.adapter.__file__).name == "pa_qe_adapter_v2.py"


def test_registered_deck_strings_all_have_canonical_rules_before_any_call_is_paid_for():
    deck = adapter.parse_deck(SOURCE)
    expected = adapter.expected_xml_strings(deck)
    assert set(expected) == {"calculation", "restart_mode", "prefix", "mixing_mode", "ion_dynamics",
                             "occupations", "functional", "U_projection_type"}
    assert expected["calculation"] == "relax" and expected["restart_mode"] == "from_scratch"
    assert expected["mixing_mode"] == "local-TF" and expected["ion_dynamics"] == "bfgs"
    assert expected["occupations"] == "smearing" and expected["functional"] == "PBE"
    assert expected["U_projection_type"] == "atomic"


def test_checked_in_retest_spec_passes_validation_and_pins_the_corrected_modules():
    spec_path = Path(__file__).resolve().parents[1] / "results/pa_catalyst_retest_2026-10-04/launch_spec.json"
    if not spec_path.is_file():
        pytest.skip("retest spec not present")
    original, trial.Path = trial.Path, pathlib.PurePosixPath  # the spec holds Linux paths
    try:
        spec = trial.validate_spec(json.loads(spec_path.read_text(encoding="utf-8")))
    finally:
        trial.Path = original
    names = {Path(pin["path"]).name: pin["sha256"] for pin in spec["dependencies"]}
    root = Path(__file__).resolve().parents[1]
    for name in ("pa_catalyst_retest.py", "pa_qe_adapter_v2.py", "pa_checked_contract.py"):
        assert names[name] == trial.sha256_file(root / "src/dft" / name), name
    assert spec["trial_parent"] == "/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04"
    assert spec["caps"] == trial.CAPS and spec["parallel_shape"] == trial.SHAPE
    assert spec["allocation"]["max_cpu_su"] == 2048 and spec["allocation"]["time_limit_seconds"] == 57600


# ---------------------------------------------------------------- the supervisor's own regular expressions on real QE 7.5 logs

@pytest.fixture(scope="module")
def real(tmp_path_factory):
    return real_files.materialize(tmp_path_factory.mktemp("qe75_real_controller"))


def test_real_control_log_is_clean_and_reaches_the_registered_boundary(real):
    out = (real / "control/stdout.log").read_text(encoding="utf-8")
    err = (real / "control/stderr.log").read_text(encoding="utf-8")
    assert [int(m.group(1)) for m in trial.SCF_CYCLE.finditer(out)] == [1, 2, 3]
    assert not trial.FAILURE.search(out + "\n" + err) and not trial.TIME_FAILURE.search(out + "\n" + err)
    assert max(int(m.group(1)) for m in trial.SCF_ITERATION.finditer(out)) == 23
    assert "IEEE_UNDERFLOW_FLAG" in err or "IEEE_DENORMAL" in err  # harmless notes are not failures


def test_real_fresh_logs_distinguish_a_converged_scf_from_the_iteration_127_stall(real):
    converged = (real / "fresh_logs/slab_c5low__checked.fresh3.out").read_text(encoding="utf-8")
    stalled = (real / "fresh_logs/slab_c5low__checked.fresh10.out").read_text(encoding="utf-8")
    assert not trial.FAILURE.search(converged) and not trial.TIME_FAILURE.search(converged)
    assert max(int(m.group(1)) for m in trial.SCF_ITERATION.finditer(converged)) < 127
    assert max(int(m.group(1)) for m in trial.SCF_ITERATION.finditer(stalled)) >= 127  # the supervisor's HEA4 rule fires
    assert not trial.SCF_CYCLE.search(converged)  # a fixed-geometry SCF has no ionic-cycle counter


def test_real_controller_receipt_fields_that_the_acceptance_chain_reads(real):
    receipt = json.loads((real / "control/process_receipt.json").read_text(encoding="utf-8"))
    for key in ("timed_out", "within_per_call_cap", "supervisor_error", "capture_error", "failure_marker_observed",
                "HEA4_stall_observed", "solver_limit_observed", "stop_reason", "returncode"):
        assert key in receipt or key in ("supervisor_error", "capture_error")
    assert receipt["stop_reason"] == "registered-evaluated-boundary" and receipt["returncode"] == 0
    assert receipt["within_per_call_cap"] is True and receipt["timed_out"] is False


# ---------------------------------------------------------------- PREFLIGHT replays the real control call (zero SU)

FROZEN_COPY = Path(__file__).resolve().parents[1] / "results/pa_catalyst_trial_readout_2026-10-04/dryrun/scratch/pa_qe_adapter_FROZEN_COPY.py"
FROZEN_SHA256 = "255464215aa898d0c9d34317a1be9b16fb27ba6d35108e0ca78215331a628879"


def replay_spec(tmp_path):
    spec = spec_for(tmp_path)
    spec["upfs"] = [{"path": str(Path(pin["path"]).parent / name), "sha256": real_upf_pins()[name]}
                    for pin in spec["upfs"] for name in [Path(pin["path"]).name]]
    return spec


def test_preflight_replay_accepts_the_real_control_call_through_the_staged_adapter(tmp_path):
    spec = replay_spec(tmp_path)
    trial.validate_spec(spec)
    result = trial.replay_real_control(spec, adapter)
    assert result["replayed"] is True and result["evaluations"] == 3 and result["scf_counts"] == [1, 2, 3]
    assert result["saved_optimizer_counters"] == [3, 3, 0]
    assert result["xml_settings_identity"] == trial.REAL_CONTROL_XML_IDENTITY
    assert not list(Path(spec["trial_parent"]).glob("pa_replay_*")), "the replay scratch directory must not outlive PREFLIGHT"


def test_preflight_replay_reproduces_the_original_refusal_with_the_frozen_adapter(tmp_path):
    """The frozen adapter of job 21034683 rejects the same real file; the PREFLIGHT gate would have stopped it at 0 SU."""
    import hashlib
    import importlib.util
    if not FROZEN_COPY.is_file():
        pytest.skip("retained frozen adapter copy absent")
    assert hashlib.sha256(FROZEN_COPY.read_bytes()).hexdigest() == FROZEN_SHA256
    module_spec = importlib.util.spec_from_file_location("frozen_adapter_for_replay_test", FROZEN_COPY)
    frozen = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(frozen)
    with pytest.raises(frozen.AdapterError, match="one XML lda_plus_u required"):
        trial.replay_real_control(replay_spec(tmp_path), frozen)


def test_preflight_replay_refuses_a_fixture_that_drifted(tmp_path):
    spec = replay_spec(tmp_path)
    for entry in spec["preflight_replay"]["files"]:
        if entry["path"] == "control/data-file-schema.xml.gz":
            entry["sha256"] = "0" * 64
    with pytest.raises(trial.TrialError, match="changed"):
        trial.replay_real_control(spec, adapter)


def test_preflight_replay_refuses_unregistered_pseudopotentials(tmp_path):
    spec = replay_spec(tmp_path)
    spec["upfs"][0]["sha256"] = "9" * 64
    with pytest.raises(trial.TrialError, match="not the registered pins"):
        trial.replay_real_control(spec, adapter)


@pytest.mark.parametrize("mutate", [
    lambda s: s.pop("preflight_replay"),
    lambda s: s["preflight_replay"]["files"].pop(),
    lambda s: s["preflight_replay"]["expected"].update(evaluations=2),
    lambda s: s["preflight_replay"].update(logged_upf_dir="/anvil/projects/x"),
    lambda s: s["preflight_replay"]["files"].append({"path": "control/extra.gz", "sha256": "1" * 64}),
])
def test_spec_requires_exactly_the_registered_real_control_replay(tmp_path, mutate):
    spec = spec_for(tmp_path)
    mutate(spec)
    with pytest.raises(trial.TrialError, match="preflight replay"):
        trial.validate_spec(spec)
