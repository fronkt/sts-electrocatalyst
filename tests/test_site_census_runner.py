"""Tests for src/scripts/site_census_runner.py: adopted workers, status-write retry, power flag.

The runner exited on 2026-09-07 when os.replace on status.json met a reader holding the file
open (WinError 5), leaving four workers orphaned. These tests pin the three behaviours added
in response: the replace waits out the reader and a final failure never ends the queue; a
live lock holder is adopted into the slot count and reclassified from its result file when it
ends; the power-throttling hint is cleared on the runner's own process.
"""
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scripts import site_census_runner as runner  # noqa: E402

STEM_A = "mpa0__Ni31Cr29Cu5Mn35"
STEM_B = "mpa0__Fe25Co25Ni25Cr25"


def make_job(tmp_path, stem, state="queued"):
    job = runner.Job(stem)
    job.out = tmp_path / f"{stem}_result.json"
    job.log = tmp_path / f"{stem}.log"
    job.manifest = tmp_path / f"{stem}.json"
    job.state = state
    return job


def write_result(job, status):
    job.out.write_text(json.dumps({"status": status, "results": []}), encoding="utf-8")


def make_runner(monkeypatch, tmp_path, jobs, workers=1):
    monkeypatch.setattr(runner, "build_jobs", lambda: jobs)
    monkeypatch.setattr(runner, "disable_power_throttling", lambda pid: False)
    return runner.Runner(workers, status_file=tmp_path / "status.json", stop_file=tmp_path / "STOP")


# -- replace_with_retry -----------------------------------------------------------------

def test_replace_with_retry_waits_out_a_reader(tmp_path, monkeypatch):
    temp, target = tmp_path / "s.tmp", tmp_path / "s.json"
    temp.write_text("new", encoding="utf-8")
    target.write_text("old", encoding="utf-8")
    real = os.replace
    calls = []

    def flaky(src, dst):
        calls.append(1)
        if len(calls) < 3:
            raise PermissionError(5, "Access is denied")
        real(src, dst)

    monkeypatch.setattr(runner.os, "replace", flaky)
    runner.replace_with_retry(temp, target, attempts=10, delay=0)
    assert len(calls) == 3
    assert target.read_text(encoding="utf-8") == "new"
    assert not temp.exists()


def test_replace_with_retry_raises_after_attempts(tmp_path, monkeypatch):
    def always(src, dst):
        raise PermissionError(32, "sharing violation")

    monkeypatch.setattr(runner.os, "replace", always)
    with pytest.raises(PermissionError):
        runner.replace_with_retry(tmp_path / "a", tmp_path / "b", attempts=3, delay=0)


def test_write_status_survives_a_locked_target(tmp_path, monkeypatch):
    job = make_job(tmp_path, STEM_A)
    r = make_runner(monkeypatch, tmp_path, [job])

    def locked(temp, target, attempts=0, delay=0):
        raise PermissionError(5, "Access is denied")

    monkeypatch.setattr(runner, "replace_with_retry", locked)
    r.write_status(force=True)  # must not raise
    assert r.last_status == 0.0, "a deferred write leaves last_status old so the next poll retries"
    assert (tmp_path / "status.json.tmp").exists()
    assert not (tmp_path / "status.json").exists()


def test_write_status_counts_adopted_workers(tmp_path, monkeypatch):
    a = make_job(tmp_path, STEM_A)
    a.lock.write_text("12345", encoding="utf-8")
    a.adopt("12345")
    b = make_job(tmp_path, STEM_B)
    r = make_runner(monkeypatch, tmp_path, [a, b])
    r.write_status(force=True)
    payload = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))
    assert payload["counts"] == {"external": 1, "queued": 1}
    rec = next(j for j in payload["jobs"] if j["stem"] == STEM_A)
    assert rec["pid"] == 12345 and rec["seconds"] is not None and "adopted" in rec["note"]


# -- adopted workers ----------------------------------------------------------------------

def test_adopted_worker_occupies_the_slot_then_hands_it_over(tmp_path, monkeypatch):
    a = make_job(tmp_path, STEM_A)
    a.lock.write_text("12345", encoding="utf-8")
    a.adopt("12345")
    b = make_job(tmp_path, STEM_B)
    r = make_runner(monkeypatch, tmp_path, [a, b], workers=1)

    alive = {"12345": True}
    monkeypatch.setattr(runner, "pid_alive", lambda pid: alive.get(str(pid), False))

    class FakeProc:
        def __init__(self):
            self.polls = 0

        def poll(self):
            self.polls += 1
            return None if self.polls < 2 else 0

    class Sink:
        def write(self, text):
            pass

        def close(self):
            pass

    launched = []

    def fake_launch(job):
        launched.append(job.stem)
        job.proc = FakeProc()
        job._handle = Sink()
        job.pid = 777
        job.started = 1.0
        job.state = "running"
        write_result(job, "complete")

    monkeypatch.setattr(r, "launch", fake_launch)

    ticks = []

    def scripted_sleep(seconds):
        ticks.append(seconds)
        if len(ticks) == 1:
            # the adopted worker held the only slot through the first poll: nothing launched
            assert launched == []
            alive["12345"] = False
            write_result(a, "complete")
        if len(ticks) > 5:
            raise AssertionError("loop did not terminate")

    monkeypatch.setattr(runner.time, "sleep", scripted_sleep)
    code = r.loop()
    assert code == 0
    assert a.state == "done" and "adopted pid 12345" in a.note
    assert launched == [STEM_B] and b.state == "done"
    payload = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))
    assert payload["counts"] == {"done": 2}


def test_adopted_worker_that_ends_incomplete_is_requeued_for_resume(tmp_path, monkeypatch):
    a = make_job(tmp_path, STEM_A)
    a.lock.write_text("12345", encoding="utf-8")
    a.adopt("12345")
    write_result(a, "running")
    r = make_runner(monkeypatch, tmp_path, [a])
    monkeypatch.setattr(runner, "pid_alive", lambda pid: False)
    assert r.check_external(a) is True
    assert a.state == "queued" and "--resume" in a.note and a.pid is None
    assert "--resume" in a.command(), "the result stub exists, so the relaunch resumes"


def test_adopted_worker_still_alive_is_left_alone(tmp_path, monkeypatch):
    a = make_job(tmp_path, STEM_A)
    a.lock.write_text("12345", encoding="utf-8")
    a.adopt("12345")
    r = make_runner(monkeypatch, tmp_path, [a])
    monkeypatch.setattr(runner, "pid_alive", lambda pid: True)
    assert r.check_external(a) is False
    assert a.state == "external"


def test_launch_adopts_a_lock_that_appeared_after_planning(tmp_path, monkeypatch):
    a = make_job(tmp_path, STEM_A)
    r = make_runner(monkeypatch, tmp_path, [a])
    a.lock.write_text("4242", encoding="utf-8")
    monkeypatch.setattr(runner, "pid_alive", lambda pid: True)
    r.launch(a)
    assert a.state == "external" and a.external_pid == 4242 and a.proc is None


# -- power throttling ---------------------------------------------------------------------

def test_disable_power_throttling_on_own_process():
    result = runner.disable_power_throttling(os.getpid())
    assert result is (os.name == "nt")


@pytest.mark.parametrize("pid", [None, "x", 0, -1])
def test_disable_power_throttling_rejects_bad_pids(pid):
    assert runner.disable_power_throttling(pid) is False
