"""Guarded launch and collection of the clean-slab SCF diagnostic on Anvil.

Phases (each writes its own receipt under results/lowtail_slab_scf_diag_2026-09-19/):

    wait     poll SSH until the login nodes answer (maintenance) or the deadline passes
    stage    upload the pinned bytes of the pushed boundary commit; back up any differing
             remote non-deck file; refuse a differing remote deck; run the remote preflight
    submit   run anvil/77_submit_slab_scf_diag.sh (held array); record balance and queue
    inspect  compare the held job's scheduler fields with the specification; never release
             on a mismatch
    release  scontrol release after a passing inspection
    watch    poll sacct until all five tasks are terminal (or the deadline), then mirror
             raw outputs, QC receipts and stop markers and trace every output
    auto     wait -> stage -> submit -> inspect -> release -> watch, stopping at the first
             failure and leaving a held job held

The launcher never resubmits an existing launch, never edits a deck, never restarts a
calculation and never turns a stopped SCF into a result.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import posixpath
import re
import shlex
import socket
import subprocess
import sys
import time

import paramiko

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results/lowtail_slab_scf_diag_2026-09-19"
REMOTE = "/anvil/projects/x-che260157/sts"
PROJECT = "/anvil/projects/x-che260157"
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SPEC = "results/lowtail_slab_scf_diag_2026-09-19/launch_spec.json"
SLURM = "anvil/76_slab_scf_diag.slurm"
SUBMIT = "anvil/77_submit_slab_scf_diag.sh"
STAGE = "slab_scf_diag"
JOB_NAME = "research-" + STAGE
TRACER = ROOT / "src/dft/qe_relax_trace.py"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write(name: str, value) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / name).write_bytes((json.dumps(value, indent=2, allow_nan=False) + "\n").encode())


def read(name: str):
    path = RESULTS / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def connect(timeout: int = 20) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3",
                   key_filename=str(Path.home() / ".ssh/id_ed25519"), allow_agent=False,
                   look_for_keys=False, timeout=timeout, banner_timeout=timeout, auth_timeout=timeout)
    return client


def command(client, args, timeout: int = 300, check: bool = True) -> dict:
    text = args if isinstance(args, str) else shlex.join(map(str, args))
    _, out, err = client.exec_command(text, timeout=timeout)
    result = dict(command=text, stdout=out.read().decode(errors="replace"),
                  stderr=err.read().decode(errors="replace"), rc=out.channel.recv_exit_status(), at=now())
    print(json.dumps({k: (v if k != "stdout" else v[-1500:]) for k, v in result.items()}), flush=True)
    if check and result["rc"]:
        raise RuntimeError(json.dumps(result)[:4000])
    return result


def spec() -> dict:
    return json.loads((ROOT / SPEC).read_text(encoding="utf-8"))


def wait(deadline: dt.datetime, poll: int = 600) -> None:
    attempts = []
    while True:
        try:
            client = connect()
            out = command(client, ["hostname"])
            client.close()
            attempts.append(dict(at=now(), ok=True, host=out["stdout"].strip()))
            write("wait.json", dict(attempts=attempts, reachable_at=now()))
            return
        except (OSError, socket.error, paramiko.SSHException, RuntimeError) as error:
            attempts.append(dict(at=now(), ok=False, error=str(error)[:300]))
            write("wait.json", dict(attempts=attempts, reachable_at=None))
            if dt.datetime.now(dt.timezone.utc) >= deadline:
                raise RuntimeError("host unreachable before deadline")
            time.sleep(poll)


def stage(client) -> None:
    boundary = read("boundary.json")
    if not boundary:
        raise ValueError("boundary.json (pushed commit) is required before staging")
    commit = boundary["commit"]
    remote_ref = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/r0-catalysis-revival"],
                                         cwd=ROOT, text=True).split()[0]
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, remote_ref], cwd=ROOT).returncode:
        raise ValueError("launch boundary is not pushed")
    if read("submission.json"):
        raise ValueError("already submitted")
    queue = command(client, ["squeue", "-u", "x-fcai3", "-h", "-o", "%i|%j|%T"])
    if JOB_NAME in queue["stdout"]:
        raise ValueError("a diagnostic job is already queued")
    sftp = client.open_sftp()
    sftp.get_channel().settimeout(120)

    def mkdirs(path):
        try:
            sftp.stat(path)
        except FileNotFoundError:
            mkdirs(posixpath.dirname(path))
            sftp.mkdir(path)

    receipt = dict(at=now(), commit=commit, files=[], checks=[])
    for relative in list(spec()["files"]) + [SPEC, SLURM, SUBMIT]:
        data = subprocess.check_output(["git", "show", commit + ":" + relative], cwd=ROOT)
        if data != (ROOT / relative).read_bytes():
            raise ValueError("worktree differs from pushed launch: " + relative)
        dest = REMOTE + "/" + relative
        mkdirs(posixpath.dirname(dest))
        prior = None
        try:
            with sftp.open(dest, "rb") as handle:
                old = handle.read()
            prior = hashlib.sha256(old).hexdigest()
            if old != data:
                if relative.endswith(".in"):
                    raise ValueError("remote deck differs: " + relative)
                backup = RESULTS / "prestage" / relative
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup.write_bytes(old)
        except FileNotFoundError:
            pass
        tmp = dest + ".upload_20260919"
        with sftp.open(tmp, "wb") as handle:
            handle.write(data)
        with sftp.open(tmp, "rb") as handle:
            if handle.read() != data:
                raise ValueError("upload mismatch")
        sftp.posix_rename(tmp, dest)
        with sftp.open(dest, "rb") as handle:
            if handle.read() != data:
                raise ValueError("staged mismatch")
        receipt["files"].append(dict(path=relative, sha256=hashlib.sha256(data).hexdigest(), prior_sha256=prior))
    sftp.close()
    for script in (SLURM, SUBMIT):
        receipt["checks"].append(command(client, ["bash", "-n", REMOTE + "/" + script]))
    receipt["checks"].append(command(client, [PYTHON, REMOTE + "/src/dft/research_batch.py", "--spec", REMOTE + "/" + SPEC,
                                              "--root", REMOTE, "--stage", STAGE, "--pseudo", PROJECT + "/pseudo", "--preflight"]))
    write("transfer.json", receipt)


def submit(client) -> str:
    if read("submission.json"):
        raise ValueError("already submitted")
    balance = command(client, ["mybalance"])
    queue = command(client, ["squeue", "-u", "x-fcai3", "-h", "-o", "%i|%j|%T"])
    if JOB_NAME in queue["stdout"]:
        raise ValueError("a diagnostic job is already queued")
    result = command(client, ["bash", REMOTE + "/" + SUBMIT], timeout=900)
    lines = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
    job_id = lines[-1] if lines and re.fullmatch(r"\d+", lines[-1]) else None
    if not job_id:
        raise RuntimeError("no job id in submit output")
    write("submission.json", dict(at=now(), job_id=job_id, submission=result, balance=balance,
                                  queue_before=queue, released=False))
    return job_id


def inspect_held(client, job_id: str) -> dict:
    s = spec()
    stage_spec = s["stages"][STAGE]
    result = command(client, ["scontrol", "show", "job", "-o", job_id])
    fields = dict(re.findall(r"(?:^|\s)([A-Za-z][A-Za-z0-9_]*)=(\S+)", result["stdout"]))
    n = len(stage_spec["jobs"])
    minutes = stage_spec["wall_minutes"]
    needed = dict(JobState="PENDING", Reason="JobHeldUser", NumCPUs="128", NumTasks="128", Requeue="0",
                  Account="che260157", ArrayTaskId=f"1-{n}%{stage_spec['concurrency']}", MinMemoryNode="237G",
                  TimeLimit=f"{minutes // 60:02d}:{minutes % 60:02d}:00", Partition="shared", JobName=JOB_NAME)
    mismatches = {k: fields.get(k) for k, v in needed.items() if fields.get(k) != v}
    if fields.get("NumNodes") not in ("1", "1-1"):
        mismatches["NumNodes"] = fields.get("NumNodes")
    if not fields.get("Command", "").endswith(SLURM):
        mismatches["Command"] = fields.get("Command")
    expanded = command(client, ["scontrol", "show", "hostnames", fields.get("ExcNodeList", "")])["stdout"].split()
    if sorted(expanded) != sorted(s["exclusions"].split(",")):
        mismatches["ExcNodeList"] = expanded
    inspection = dict(at=now(), job_id=job_id, fields=fields, needed=needed, mismatches=mismatches, raw=result)
    write("held_inspection.json", inspection)
    if mismatches:
        raise RuntimeError("held inspection mismatch; job left held: " + json.dumps(mismatches))
    return inspection


def release(client) -> None:
    receipt = read("submission.json")
    if not receipt:
        raise ValueError("nothing submitted")
    if receipt.get("released"):
        raise ValueError("already released")
    inspection = inspect_held(client, receipt["job_id"])
    result = command(client, ["scontrol", "release", receipt["job_id"]])
    after = command(client, ["scontrol", "show", "job", "-o", receipt["job_id"]])
    receipt.update(released=True, released_at=now(), final_held_inspection=inspection, release=result, after=after)
    write("submission.json", receipt)


def watch(deadline: dt.datetime, poll: int = 600) -> None:
    receipt = read("submission.json")
    if not receipt or not receipt.get("released"):
        raise ValueError("no released submission to watch")
    job_id = receipt["job_id"]
    jobs = spec()["stages"][STAGE]["jobs"]
    while True:
        try:
            client = connect()
            acct = command(client, ["sacct", "--array", "-n", "-P", "-X", "-j", job_id,
                                    "--format=JobID%80,State%30,ExitCode,ElapsedRaw,AllocCPUS"])
            client.close()
        except (OSError, socket.error, paramiko.SSHException, RuntimeError) as error:
            write("watch.json", dict(at=now(), error=str(error)[:300]))
            if dt.datetime.now(dt.timezone.utc) >= deadline:
                raise
            time.sleep(poll)
            continue
        tasks = {}
        for line in acct["stdout"].splitlines():
            parts = line.split("|")
            m = re.fullmatch(job_id + r"_(\d+)", parts[0])
            if m:
                state = parts[1].split()[0]
                tasks[int(m.group(1))] = dict(state=state, exit=parts[2], elapsed_s=int(parts[3] or 0),
                                              terminal=state in ("COMPLETED", "FAILED", "CANCELLED", "TIMEOUT",
                                                                 "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED"))
        record = dict(at=now(), job_id=job_id, tasks=tasks, all_terminal=len(tasks) == len(jobs) and all(t["terminal"] for t in tasks.values()))
        write("watch.json", record)
        if record["all_terminal"]:
            collect(tasks)
            return
        if dt.datetime.now(dt.timezone.utc) >= deadline:
            raise RuntimeError("watch deadline reached before all tasks were terminal")
        time.sleep(poll)


def collect(tasks: dict) -> None:
    jobs = spec()["stages"][STAGE]["jobs"]
    client = connect()
    sftp = client.open_sftp()
    sftp.get_channel().settimeout(300)
    out_dir = RESULTS / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    mirrored = []
    for row, job in enumerate(jobs, start=1):
        base = REMOTE + "/runs/" + job["dir"] + "/" + job["job"]
        for suffix in (".out", ".run.in", ".qc.json", ".KILLED", ".REJECTED"):
            try:
                with sftp.open(base + suffix, "rb") as handle:
                    data = handle.read()
            except FileNotFoundError:
                continue
            local = out_dir / (job["job"] + "__" + job["site"] + suffix)
            local.write_bytes(data)
            mirrored.append(dict(row=row, job=job["job"], site=job["site"], suffix=suffix,
                                 sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), task=tasks.get(row)))
    sftp.close()
    client.close()
    outputs = sorted(str(p) for p in out_dir.glob("*.out"))
    trace_file = RESULTS / "traces.json"
    if outputs:
        subprocess.run([sys.executable, str(TRACER), "--quiet", "--out", str(trace_file)] + outputs, check=True, cwd=ROOT)
    readout = dict(at=now(), mirrored=mirrored, tasks=tasks, traces=str(trace_file.relative_to(ROOT)).replace("\\", "/"),
                   scope="Numerical diagnostic outcomes; no relaxed slab, adsorption reference or census result")
    for rec in (json.loads(trace_file.read_text(encoding="utf-8")) if trace_file.exists() else []):
        c = rec["cycles"][0] if rec["cycles"] else {}
        readout.setdefault("summary", []).append(dict(
            file=rec["file"], converged_in=c.get("converged_in"), n_iter=c.get("n_iter"), acc_min_Ry=c.get("acc_min_Ry"),
            acc_last_Ry=c.get("acc_last_Ry"), first_iter_below=c.get("first_iter_below"), tmag_last=c.get("tmag_last"),
            job_done=rec["job_done"], wall_s=rec["wall_last_s"]))
    write("readout.json", readout)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("wait", "stage", "submit", "inspect", "release", "watch", "auto"))
    parser.add_argument("--wait-deadline", default="2026-09-21T12:00:00+00:00")
    parser.add_argument("--watch-deadline", default="2026-09-25T12:00:00+00:00")
    parser.add_argument("--poll", type=int, default=600)
    args = parser.parse_args(argv)
    wait_deadline = dt.datetime.fromisoformat(args.wait_deadline)
    watch_deadline = dt.datetime.fromisoformat(args.watch_deadline)
    if args.phase == "wait":
        wait(wait_deadline, args.poll)
        return 0
    if args.phase == "watch":
        watch(watch_deadline, args.poll)
        return 0
    if args.phase == "auto":
        wait(wait_deadline, args.poll)
        if not read("submission.json"):
            client = connect()
            try:
                if not read("transfer.json"):
                    stage(client)
                job_id = submit(client)
                inspect_held(client, job_id)
                release(client)
            finally:
                client.close()
        elif not read("submission.json").get("released"):
            raise RuntimeError("a submission exists but was not released; inspect manually")
        watch(watch_deadline, args.poll)
        return 0
    client = connect()
    try:
        if args.phase == "stage":
            stage(client)
        elif args.phase == "submit":
            submit(client)
        elif args.phase == "inspect":
            inspect_held(client, read("submission.json")["job_id"])
        elif args.phase == "release":
            release(client)
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
