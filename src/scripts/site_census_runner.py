"""Queue runner for the 2026-09-06 site-integrity census (docs/91).

Launches up to N (default 4) concurrent ``screen_diagnostic.py run`` subprocesses, each with
``--threads 2``, hidden (CREATE_NO_WINDOW on Windows), stdout+stderr appended to a
per-manifest log under results/site_census_2026-09-06/logs/; a worker count with
N x 2 > cpu_count is refused, not capped. The children inherit the environment plus
TORCHINDUCTOR_CACHE_DIR=<census dir>/torch-cache and PYTHONUNBUFFERED=1. Queue order is fixed by
site_census_plan.expected_stems(): CENSUS-1 gated six, CENSUS-1 other six,
ENDMEMBER-2x2, CENSUS-2 (three models x gated six, then three models x other six),
CENSUS-3 seed blocks. A restart resumes every unfinished manifest with ``--resume``;
a stale ``<result>.lock`` whose recorded pid is dead is removed before relaunch (the
diagnostic refuses to start while a lock exists). A status JSON is refreshed at least every
60 s. Touching the stop file stops new launches; a stop file containing the word KILL also
terminates the running subprocesses.

    python src/scripts/site_census_runner.py --dry-run      # print the plan
    python src/scripts/site_census_runner.py --start        # run in the foreground
    python src/scripts/site_census_runner.py --detach       # spawn itself hidden with --start
    python src/scripts/site_census_runner.py --status       # summarise status.json
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from scripts import site_census_plan as plan  # noqa: E402

DIAGNOSTIC = ROOT / "src/scripts/screen_diagnostic.py"
THREADS = 2  # the measured protocol; --resume refuses a different thread count
POLL_SECONDS = 5
STATUS_SECONDS = 60
CREATE_NO_WINDOW = 0x08000000
STILL_ACTIVE = 259


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def pid_alive(pid):
    """True when a process with this pid is still running (Windows via kernel32, else kill 0)."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return False
            return code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def rel(path):
    """Repo-relative string when the path is inside the repo, else the absolute path."""
    path = Path(path)
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def result_status(out):
    if not out.exists():
        return None
    try:
        return json.loads(out.read_text(encoding="utf-8")).get("status")
    except (OSError, ValueError):
        return "unreadable"


class Job:
    def __init__(self, stem):
        self.stem = stem
        self.info = plan.parse_stem(stem)
        self.manifest = plan.manifest_path(stem)
        self.out = plan.result_path(stem)
        self.log = plan.log_path(stem)
        self.model_file = plan.model_path(self.info["tag"])
        self.proc = None
        self.pid = None
        self.started = None
        self.finished = None
        self.exit_code = None
        self.state = "queued"
        self.note = ""

    @property
    def lock(self):
        return self.out.with_name(self.out.name + ".lock")

    def seconds(self):
        if self.started is None:
            return None
        end = self.finished if self.finished is not None else time.time()
        return round(end - self.started, 1)

    def command(self):
        cmd = [sys.executable, str(DIAGNOSTIC), "run", "--manifest", str(self.manifest),
               "--model-file", str(self.model_file), "--device", "cpu",
               "--threads", str(THREADS), "--out", str(self.out)]
        if self.out.exists():
            cmd.append("--resume")
        return cmd

    def record(self):
        return dict(stem=self.stem, arm=self.info["arm"], tag=self.info["tag"],
                    formula=self.info["formula"], block=self.info["block"], state=self.state,
                    pid=self.pid, started=self.started, finished=self.finished,
                    seconds=self.seconds(), exit_code=self.exit_code,
                    result_status=result_status(self.out), note=self.note,
                    manifest=rel(self.manifest), result=rel(self.out), log=rel(self.log))


def build_jobs():
    stems = plan.queue_order([p.stem for p in plan.MANIFEST_DIR.glob("*.json")])
    if not stems:
        raise FileNotFoundError("no manifests under " + str(plan.MANIFEST_DIR))
    jobs = [Job(s) for s in stems]
    for job in jobs:
        status = result_status(job.out)
        if status in ("complete", "complete_with_errors"):
            job.state = "done" if status == "complete" else "done_with_errors"
            job.note = "result present before this runner started"
        elif job.lock.exists():
            pid = job.lock.read_text(encoding="utf-8").strip()
            if pid_alive(pid):
                job.state = "external"
                job.note = f"lock held by live pid {pid}; not launched by this runner"
            else:
                job.note = f"stale lock (pid {pid} dead) will be removed before launch"
        if not job.model_file.exists():
            job.state = "error"
            job.note = "model file missing: " + str(job.model_file)
    return jobs


class Runner:
    def __init__(self, workers, status_file=plan.STATUS_FILE, stop_file=plan.STOP_FILE):
        cpu = os.cpu_count() or 1
        if workers < 1 or workers * THREADS > cpu:
            raise ValueError(f"workers x {THREADS} threads must not exceed {cpu} CPUs")
        self.workers = workers
        self.status_file = status_file
        self.stop_file = stop_file
        self.jobs = build_jobs()
        self.runner_pid = os.getpid()
        self.started = now()
        self.last_status = 0.0

    # -- environment for the children --------------------------------------------------
    def child_env(self):
        env = dict(os.environ)
        # Explicit inductor cache: the Windows background environment reached torch's
        # cache-path code, which imports the Unix-only pwd module (docs/site-evidence-
        # continuation-2026-09-06.md:61). Same remedy as results/cr_site_chains_2026-09-06/run_chains.py.
        env.setdefault("TORCHINDUCTOR_CACHE_DIR", str(plan.CENSUS_DIR / "torch-cache"))
        env.setdefault("PYTHONUNBUFFERED", "1")
        return env

    def stop_requested(self):
        if not self.stop_file.exists():
            return None
        try:
            text = self.stop_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        return "KILL" if "KILL" in text.upper() else "STOP"

    def launch(self, job):
        plan.RESULT_DIR.mkdir(parents=True, exist_ok=True)
        plan.LOG_DIR.mkdir(parents=True, exist_ok=True)
        if job.lock.exists():
            pid = job.lock.read_text(encoding="utf-8").strip()
            if pid_alive(pid):
                job.state = "external"
                job.note = f"lock held by live pid {pid}"
                return
            job.lock.unlink()
            job.note = f"stale lock removed (pid {pid} dead)"
        cmd = job.command()
        flags = CREATE_NO_WINDOW if os.name == "nt" else 0
        handle = open(job.log, "a", encoding="utf-8")
        handle.write(f"\n=== {now()} launch: {' '.join(cmd)}\n")
        handle.flush()
        job.proc = subprocess.Popen(cmd, cwd=str(ROOT), stdout=handle, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, env=self.child_env(),
                                    creationflags=flags)
        job._handle = handle
        job.pid = job.proc.pid
        job.started = time.time()
        job.state = "running"

    def reap(self, job):
        code = job.proc.poll()
        if code is None:
            return False
        job.exit_code = code
        job.finished = time.time()
        job._handle.write(f"=== {now()} exit {code}\n")
        job._handle.close()
        status = result_status(job.out)
        if code == 0 and status == "complete":
            job.state = "done"
        elif code == 1 and status == "complete_with_errors":
            job.state = "done_with_errors"
        else:
            job.state = "error"
            job.note = f"exit {code}, result status {status}"
        return True

    def running(self):
        return [j for j in self.jobs if j.state == "running"]

    def queued(self):
        return [j for j in self.jobs if j.state == "queued"]

    def write_status(self, force=False):
        if not force and time.time() - self.last_status < STATUS_SECONDS:
            return
        counts = {}
        for job in self.jobs:
            counts[job.state] = counts.get(job.state, 0) + 1
        payload = dict(schema="site-census-runner-status-v1", updated=now(),
                       runner_started=self.started, runner_pid=self.runner_pid,
                       workers=self.workers, threads_per_job=THREADS,
                       stop=self.stop_requested(), counts=counts,
                       jobs=[job.record() for job in self.jobs])
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        temp = self.status_file.with_name(self.status_file.name + ".tmp")
        temp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
        os.replace(temp, self.status_file)
        self.last_status = time.time()

    def kill_running(self):
        for job in self.running():
            try:
                job.proc.terminate()
            except OSError:
                pass

    def loop(self):
        self.write_status(force=True)
        while True:
            changed = False
            for job in self.running():
                changed |= self.reap(job)
            stop = self.stop_requested()
            if stop == "KILL":
                self.kill_running()
            if stop is None:
                while len(self.running()) < self.workers and self.queued():
                    self.launch(self.queued()[0])
                    changed = True
            self.write_status(force=changed)
            if not self.running() and (stop is not None or not self.queued()):
                break
            time.sleep(POLL_SECONDS)
        self.write_status(force=True)
        return 0 if all(j.state in ("done", "done_with_errors", "external") for j in self.jobs) else 1


def print_plan(jobs):
    print(f"{'#':>3} {'state':<10} {'arm':<16} {'stem':<44} model")
    for k, job in enumerate(jobs, 1):
        print(f"{k:>3} {job.state:<10} {job.info['arm']:<16} {job.stem:<44} {job.model_file.name}"
              + (f"  [{job.note}]" if job.note else ""))
    print(f"{len(jobs)} manifests; queue order fixed by site_census_plan.expected_stems()")


def print_status(status_file):
    payload = json.loads(status_file.read_text(encoding="utf-8"))
    print(f"updated {payload['updated']}  counts {payload['counts']}  stop {payload['stop']}")
    for job in payload["jobs"]:
        if job["state"] in ("running", "error"):
            print(f"  {job['state']:<8} {job['stem']:<44} pid {job['pid']} {job['seconds']} s {job['note']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--threads", type=int, default=THREADS,
                        help="must be 2: the measured protocol and the --resume identity")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--detach", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    if args.threads != THREADS:
        parser.error(f"--threads must be {THREADS}; every census result must carry the same environment for --resume")
    if args.status:
        print_status(plan.STATUS_FILE)
        return 0
    if args.detach:
        cmd = [sys.executable, str(Path(__file__).resolve()), "--start", "--workers", str(args.workers)]
        plan.LOG_DIR.mkdir(parents=True, exist_ok=True)
        handle = open(plan.LOG_DIR / "runner.log", "a", encoding="utf-8")
        flags = CREATE_NO_WINDOW if os.name == "nt" else 0
        proc = subprocess.Popen(cmd, cwd=str(ROOT), stdout=handle, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, creationflags=flags)
        print(f"runner detached, pid {proc.pid}; status at {plan.STATUS_FILE}")
        return 0
    runner = Runner(args.workers)
    if args.dry_run or not args.start:
        print_plan(runner.jobs)
        return 0
    return runner.loop()


if __name__ == "__main__":
    raise SystemExit(main())
