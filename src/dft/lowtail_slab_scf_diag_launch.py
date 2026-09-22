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
import math
import os
from pathlib import Path
import posixpath
import re
import shlex
import socket
import subprocess
import sys
import time
import uuid

import paramiko

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results/lowtail_slab_scf_diag_2026-09-19"
REMOTE = "/anvil/projects/x-che260157/sts"
PROJECT = "/anvil/projects/x-che260157"
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SPEC = "results/lowtail_slab_scf_diag_2026-09-19/launch_spec.json"
SLURM = "anvil/76_slab_scf_diag.slurm"
SUBMIT = "anvil/77_submit_slab_scf_diag.sh"
RUNNER = "src/dft/research_batch.py"
STAGE = "slab_scf_diag"
JOB_NAME = "research-" + STAGE
POPULATION = 5
TRACER = ROOT / "src/dft/qe_relax_trace.py"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write(name: str, value) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / name
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_bytes((json.dumps(value, indent=2, allow_nan=False) + "\n").encode())
    os.replace(temporary, path)


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
    return validate_spec(json.loads((ROOT / SPEC).read_text(encoding="utf-8")))



LOCAL_SOURCES = (
    "src/dft/lowtail_slab_scf_diag_launch.py", "src/dft/qe_relax_trace.py",
    "src/dft/research_batch.py", "src/dft/projection_qc.py",
    "src/dft/hea_force_audit.py", "src/dft/hea_panel_readout.py",
)
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY",
            "NODE_FAIL", "BOOT_FAIL", "PREEMPTED", "DEADLINE", "REVOKED", "SPECIAL_EXIT"}
SUFFIXES = (".out", ".run.in", ".qc.json", ".projwfc.in", ".projwfc.out", ".KILLED", ".REJECTED")
MAX_ARTIFACT_BYTES = 512 * 1024 * 1024
LOADED_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def portable(relative):
    if (not isinstance(relative, str) or not relative or "\\" in relative
            or ":" in relative or relative.startswith("/")
            or any(part in ("", ".", "..") for part in relative.split("/"))):
        raise ValueError("portable repository-relative POSIX path required: " + str(relative))
    return relative


def local(relative):
    portable(relative)
    path = ROOT / relative
    if path.is_symlink() or ROOT.resolve() not in path.resolve().parents:
        raise ValueError("path escapes repository: " + relative)
    return path


def validate_spec(value):
    if value.get("schema") != "research-batch-2026-09-16" or value.get("np") != 128:
        raise ValueError("unexpected diagnostic specification")
    group = value["stages"][STAGE]
    if len(group["jobs"]) != POPULATION:
        raise ValueError(f"population must contain {POPULATION} jobs")
    for relative in (*value["files"], group["manifest"]):
        portable(relative)
    identities = set()
    for job in group["jobs"]:
        portable(job["dir"])
        for key in ("job", "site"):
            if not re.fullmatch(r"[A-Za-z0-9_-]+", job[key]):
                raise ValueError("unsafe job identity")
        deck = "runs/" + job["dir"] + "/" + job["job"] + ".in"
        if value["files"].get(deck) != job["sha256"]:
            raise ValueError("diagnostic deck is not pinned")
        if deck in identities:
            raise ValueError("duplicate diagnostic job")
        identities.add(deck)
    return value


def snapshot():
    value = spec()
    pins = dict(value["files"])
    for relative in (*LOCAL_SOURCES, SPEC, SLURM, SUBMIT):
        pins.setdefault(relative, sha(local(relative).read_bytes()))
    assert_pins(pins)
    if pins[LOCAL_SOURCES[0]] != LOADED_SHA256:
        raise ValueError("launcher source changed since import")
    return pins


def assert_pins(pins):
    for relative, expected in pins.items():
        if sha(local(relative).read_bytes()) != expected:
            raise ValueError("pinned source/input changed: " + relative)


def verify_boundary_bytes(commit, pins):
    if not re.fullmatch(r"[0-9a-f]{40}", str(commit)):
        raise ValueError("full pushed boundary commit required")
    for relative, expected in pins.items():
        data = subprocess.check_output(["git", "show", commit + ":" + portable(relative)], cwd=ROOT)
        if sha(data) != expected or data != local(relative).read_bytes():
            raise ValueError("local execution/input differs from pushed boundary: " + relative)


def verify_transfer(client=None):
    transfer, boundary = read("transfer.json"), read("boundary.json")
    if not transfer or not boundary or transfer.get("commit") != boundary.get("commit"):
        raise ValueError("matching staged boundary receipt required")
    expected = snapshot()
    verify_boundary_bytes(boundary["commit"], expected)
    if transfer.get("pins") != expected:
        raise ValueError("staged source/input pins differ")
    paths = list(dict.fromkeys([*spec()["files"], SPEC, SLURM, SUBMIT]))
    recorded = {row["path"]: row["sha256"] for row in transfer["files"]}
    if recorded != {path: expected[path] for path in paths}:
        raise ValueError("staging receipt is incomplete")
    if client is not None:
        result = command(client, ["sha256sum", "--", *[REMOTE + "/" + path for path in paths]])
        remote = {}
        for line in result["stdout"].splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})\s+(\S+)", line)
            if not match or match[2] in remote:
                raise ValueError("malformed remote checksum inventory")
            remote[match[2]] = match[1]
        if remote != {REMOTE + "/" + path: expected[path] for path in paths}:
            raise ValueError("remote staged bytes differ")
    return expected


def parse_accounting(text, job_id):
    if not re.fullmatch(r"\d+", str(job_id)):
        raise ValueError("numeric array id required")
    tasks = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        fields = line.strip().split("|")
        if len(fields) != 5:
            raise ValueError("malformed accounting row")
        match = re.fullmatch(re.escape(str(job_id)) + r"_(\d+)", fields[0])
        if not match:
            continue
        task = int(match[1])
        if task not in range(1, POPULATION + 1):
            raise ValueError("unexpected diagnostic task")
        state = fields[1].split()[0].rstrip("+")
        record = dict(job_id=fields[0], state=state, exit=fields[2],
                      elapsed_s=int(fields[3] or 0), allocated_cpus=int(fields[4] or 0),
                      terminal=state in TERMINAL)
        if record["elapsed_s"] < 0 or record["allocated_cpus"] < 0:
            raise ValueError("negative accounting value")
        if task in tasks and tasks[task] != record:
            raise ValueError("conflicting accounting task")
        tasks[task] = record
    return tasks


def all_terminal(tasks):
    return set(tasks) == set(range(1, POPULATION + 1)) and all(task["terminal"] for task in tasks.values())


def remote_bytes(sftp, path):
    try:
        before = sftp.stat(path)
    except FileNotFoundError:
        return None
    if before.st_size > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact exceeds mirror bound")
    with sftp.open(path, "rb") as handle:
        data = handle.read(MAX_ARTIFACT_BYTES + 1)
    after = sftp.stat(path)
    if (len(data) != before.st_size or after.st_size != before.st_size
            or after.st_mtime != before.st_mtime):
        raise ValueError("remote artifact changed during terminal collection")
    return data


def preserve(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("local evidence differs; refusing overwrite: " + str(path))
        return "ALREADY_IDENTICAL"
    with path.open("xb") as handle:
        handle.write(data)
    return "MIRRORED"


def runtime_text(job):
    text = local("runs/" + job["dir"] + "/" + job["job"] + ".in").read_text(encoding="utf-8")
    scratch = REMOTE + "/runs/" + job["dir"] + "/tmp_" + job["job"]
    for field, value in (("outdir", scratch), ("pseudo_dir", PROJECT + "/pseudo")):
        text, count = re.subn(r"(?m)^(\s*" + field + r"\s*=\s*)'[^']*'",
                              lambda m: m[1] + "'" + value + "'", text)
        if count != 1:
            raise ValueError("runtime rewrite is not unique")
    return text, scratch


def identity_problems(job, row, artifacts):
    reasons = []
    for suffix in (".out", ".run.in", ".qc.json"):
        if suffix not in artifacts:
            reasons.append("identity unverified: missing " + suffix)
    qc = None
    if ".qc.json" in artifacts:
        try:
            qc = json.loads(artifacts[".qc.json"].decode("utf-8"))
            if (not isinstance(qc, dict) or qc.get("stage") != STAGE or qc.get("row") != row
                    or qc.get("job") != job["job"] or qc.get("input_sha256") != job["sha256"]):
                reasons.append("QC input/job identity mismatch")
            if isinstance(qc, dict):
                for key, suffix in (("output_sha256", ".out"), ("runtime_sha256", ".run.in"),
                                    ("projection_sha256", ".projwfc.out"), ("projection_input_sha256", ".projwfc.in")):
                    if qc.get(key) is not None and (suffix not in artifacts or qc[key] != sha(artifacts[suffix])):
                        reasons.append("QC hash mismatch " + key)
        except (ValueError, UnicodeError):
            reasons.append("malformed QC identity")
    if ".run.in" in artifacts:
        expected, _ = runtime_text(job)
        if artifacts[".run.in"] != expected.encode("utf-8"):
            reasons.append("runtime deck differs from the permitted path-only rewrite")
    return reasons


def validate_evidence(job, row, artifacts, paths, task):
    reasons = identity_problems(job, row, artifacts)
    if task["state"] != "COMPLETED" or task["exit"] != "0:0" or task["allocated_cpus"] != 128:
        reasons.append("scheduler did not complete cleanly at 128 ranks")
    required = (".out", ".run.in", ".qc.json", ".projwfc.in", ".projwfc.out")
    for suffix in required:
        if suffix not in artifacts:
            reasons.append("missing artifact " + suffix)
    if ".KILLED" in artifacts or ".REJECTED" in artifacts:
        reasons.append("failure sidecar present")
    if reasons:
        return reasons
    try:
        qc = json.loads(artifacts[".qc.json"].decode("utf-8"))
        if (qc.get("status") != "COMPLETE" or qc.get("stage") != STAGE
                or qc.get("row") != row or qc.get("job") != job["job"]
                or qc.get("input_sha256") != job["sha256"]):
            reasons.append("QC completion or input/job identity mismatch")
        for key, suffix in (("output_sha256", ".out"), ("runtime_sha256", ".run.in")):
            if qc.get(key) != sha(artifacts[suffix]):
                reasons.append("QC hash mismatch " + key)
        expected, scratch = runtime_text(job)
        if artifacts[".run.in"] != expected.encode("utf-8"):
            reasons.append("runtime deck differs from the permitted path-only rewrite")
        projection_input = ("&PROJWFC\n prefix = '" + job["job"] + "'\n outdir = '" + scratch
                            + "'\n lsym = .true.\n/\n")
        if artifacts[".projwfc.in"] != projection_input.encode("utf-8"):
            reasons.append("projection input identity mismatch")
        for key, cap in (("scf_process", job["scf_seconds"]), ("projection_process", job["projection_seconds"])):
            process = qc.get(key, {})
            wall = process.get("wall_seconds")
            if (process.get("rc") != 0 or process.get("stop_reason") is not None
                    or not isinstance(wall, (int, float)) or isinstance(wall, bool)
                    or not math.isfinite(wall) or not 0 <= wall <= cap):
                reasons.append("invalid or over-limit " + key)
        import hea_force_audit
        import hea_panel_readout
        import projection_qc
        import qe_relax_trace
        audit = hea_force_audit.audit_text(expected, artifacts[".out"].decode("utf-8"))
        if audit["status"] != "VALID_SCF":
            reasons.append("SCF force evidence rejected")
        canonical = hea_panel_readout.parse_out(paths[".out"])
        if (canonical["status"] != "CONVERGED" or canonical.get("cores") != 128
                or canonical.get("wall_s") is None or canonical["wall_s"] > job["scf_seconds"]):
            reasons.append("canonical SCF evidence or execution shape rejected")
        trace = qe_relax_trace.trace(paths[".out"])
        cycles = trace["cycles"]
        threshold = re.findall(r"(?m)^\s*conv_thr\s*=\s*([0-9.eEdD+-]+)", expected)
        target = float(threshold[0].replace("d", "e").replace("D", "e")) if len(threshold) == 1 else None
        if (len(cycles) != 1 or cycles[0]["converged_in"] is None
                or cycles[0]["last_iteration_started"] > job["max_iterations"]
                or cycles[0]["converged_in"] > job["max_iterations"]
                or cycles[0]["acc_last_Ry"] is None or target is None
                or not cycles[0]["acc_last_Ry"] < target):
            reasons.append("SCF target or iteration limit not met")
        nat = int(re.search(r"(?m)^\s*nat\s*=\s*(\d+)", expected)[1])
        projection_qc.projection_check(artifacts[".projwfc.out"].decode("utf-8"), nat)
    except (ValueError, KeyError, TypeError, IndexError, UnicodeError, AttributeError, RuntimeError) as error:
        reasons.append("invalid scientific evidence: " + str(error))
    return reasons


def wait(deadline: dt.datetime, poll: int = 600) -> None:
    if deadline.tzinfo is None or poll <= 0:
        raise ValueError("timezone-aware deadline and positive poll required")
    attempts = []
    while True:
        if dt.datetime.now(dt.timezone.utc) >= deadline:
            raise RuntimeError("host wait deadline reached")
        client = None
        try:
            client = connect()
            out = command(client, ["hostname"])
            attempts.append(dict(at=now(), ok=True, host=out["stdout"].strip()))
            write("wait.json", dict(attempts=attempts, reachable_at=now()))
            return
        except (OSError, paramiko.SSHException, RuntimeError) as error:
            attempts.append(dict(at=now(), ok=False, error=str(error)[:300]))
            write("wait.json", dict(attempts=attempts, reachable_at=None))
        finally:
            if client is not None:
                client.close()
        remaining = (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds()
        if remaining <= 0:
            raise RuntimeError("host unreachable before deadline")
        time.sleep(min(poll, remaining))


def stage(client) -> None:
    pins = snapshot()
    boundary = read("boundary.json")
    if not boundary:
        raise ValueError("boundary.json (pushed commit) is required before staging")
    commit = boundary["commit"]
    remote_ref = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/r0-catalysis-revival"],
                                         cwd=ROOT, text=True).split()[0]
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, remote_ref], cwd=ROOT).returncode:
        raise ValueError("launch boundary is not pushed")
    verify_boundary_bytes(commit, pins)
    if read("submission.json") or read("submission_intent.json"):
        raise ValueError("submission exists or is uncertain; refusing a duplicate")
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

    receipt = dict(at=now(), commit=commit, pins=pins, files=[], checks=[])
    for relative in dict.fromkeys([*spec()["files"], SPEC, SLURM, SUBMIT]):
        portable(relative)
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
                backup = RESULTS / "prestage" / (relative + "." + prior)
                preserve(backup, old)
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
    receipt["checks"].append(command(client, [PYTHON, REMOTE + "/" + RUNNER, "--spec", REMOTE + "/" + SPEC,
                                              "--root", REMOTE, "--stage", STAGE, "--pseudo", PROJECT + "/pseudo", "--preflight"]))
    assert_pins(pins)
    write("transfer.json", receipt)


def submit(client) -> str:
    if read("submission.json") or read("submission_intent.json"):
        raise ValueError("submission exists or is uncertain; refusing a duplicate")
    pins = verify_transfer(client)
    balance = command(client, ["mybalance"])
    queue = command(client, ["squeue", "-u", "x-fcai3", "-h", "-o", "%i|%j|%T"])
    if JOB_NAME in queue["stdout"]:
        raise ValueError("a diagnostic job is already queued")
    write("submission_intent.json", dict(at=now(), status="SUBMISSION_ATTEMPT_PENDING", pins=pins,
                                         commit=read("boundary.json")["commit"]))
    result = command(client, ["bash", REMOTE + "/" + SUBMIT], timeout=900)
    lines = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
    job_id = lines[-1] if lines and re.fullmatch(r"\d+", lines[-1]) else None
    if not job_id:
        raise RuntimeError("no job id in submit output")
    write("submission.json", dict(at=now(), job_id=job_id, submission=result, balance=balance,
                                  queue_before=queue, released=False))
    write("submission_intent.json", dict(at=now(), status="SUBMITTED", job_id=job_id))
    return job_id


def array_task_field(n: int, concurrency: int) -> str:
    """scontrol prints a held array as 1-N%C for N > 1 and as 1%C for a single task."""
    return f"1-{n}%{concurrency}" if n > 1 else f"1%{concurrency}"


def inspect_held(client, job_id: str) -> dict:
    if not re.fullmatch(r"\d+", str(job_id)):
        raise ValueError("numeric array id required")
    s = spec()
    stage_spec = s["stages"][STAGE]
    result = command(client, ["scontrol", "show", "job", "-o", job_id])
    if len([line for line in result["stdout"].splitlines() if line.strip()]) != 1:
        raise ValueError("held inspection requires one unambiguous job record")
    fields = dict(re.findall(r"(?:^|\s)([A-Za-z][A-Za-z0-9_/]*)=(\S+)", result["stdout"]))
    n = len(stage_spec["jobs"])
    minutes = stage_spec["wall_minutes"]
    needed = dict(JobId=str(job_id), ArrayJobId=str(job_id), WorkDir=PROJECT,
                  **{"CPUs/Task": "1"}, JobState="PENDING", Reason="JobHeldUser", NumCPUs="128", NumTasks="128", Requeue="0",
                  Account="che260157", ArrayTaskId=array_task_field(n, stage_spec["concurrency"]), MinMemoryNode="237G",
                  TimeLimit=f"{minutes // 60:02d}:{minutes % 60:02d}:00", Partition="shared", JobName=JOB_NAME)
    mismatches = {k: fields.get(k) for k, v in needed.items() if fields.get(k) != v}
    if fields.get("NumNodes") not in ("1", "1-1"):
        mismatches["NumNodes"] = fields.get("NumNodes")
    if fields.get("Command") != REMOTE + "/" + SLURM:
        mismatches["Command"] = fields.get("Command")
    if not re.fullmatch(r"x-fcai3\(\d+\)", fields.get("UserId", "")):
        mismatches["UserId"] = fields.get("UserId")
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
    verify_transfer(client)
    inspection = inspect_held(client, receipt["job_id"])
    result = command(client, ["scontrol", "release", receipt["job_id"]])
    receipt.update(released=True, released_at=now(), final_held_inspection=inspection, release=result)
    write("submission.json", receipt)
    receipt["after"] = command(client, ["scontrol", "show", "job", "-o", receipt["job_id"]])
    write("submission.json", receipt)


def watch(deadline: dt.datetime, poll: int = 600) -> None:
    if deadline.tzinfo is None or poll <= 0:
        raise ValueError("timezone-aware deadline and positive poll required")
    receipt = read("submission.json")
    if not receipt or not receipt.get("released"):
        raise ValueError("no released submission to watch")
    pins = verify_transfer()
    job_id = receipt["job_id"]
    write("collector_startup.json", dict(at=now(), job_id=job_id, pins=pins))
    while True:
        if dt.datetime.now(dt.timezone.utc) >= deadline:
            raise RuntimeError("watch deadline reached before collection completed")
        assert_pins(pins)
        client = None
        try:
            client = connect()
            acct = command(client, ["sacct", "--array", "-n", "-P", "-X", "-j", job_id,
                                    "--format=JobID%80,State%30,ExitCode,ElapsedRaw,AllocCPUS"])
        except (OSError, paramiko.SSHException, RuntimeError) as error:
            write("watch_error.json", dict(at=now(), error=str(error)[:300]))
            if dt.datetime.now(dt.timezone.utc) >= deadline:
                raise
            time.sleep(min(poll, max(0, (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds())))
            continue
        finally:
            if client is not None:
                client.close()
        tasks = parse_accounting(acct["stdout"], job_id)
        record = dict(at=now(), job_id=job_id, tasks=tasks, raw=acct,
                      missing_tasks=sorted(set(range(1, POPULATION + 1)) - set(tasks)),
                      all_terminal=all_terminal(tasks))
        write("watch.json", record)
        if record["all_terminal"]:
            try:
                collect(tasks, pins)
                return
            except (OSError, EOFError, paramiko.SSHException) as error:
                write("collection_error.json", dict(at=now(), error=str(error)[:300]))
                if dt.datetime.now(dt.timezone.utc) >= deadline:
                    raise
        if dt.datetime.now(dt.timezone.utc) >= deadline:
            raise RuntimeError("watch deadline reached before all tasks were terminal")
        time.sleep(min(poll, max(0, (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds())))


def collect(tasks: dict, pins=None) -> dict:
    if not all_terminal(tasks):
        raise ValueError(f"collection requires the exact {POPULATION} terminal tasks")
    pins = snapshot() if pins is None else pins
    assert_pins(pins)
    jobs = spec()["stages"][STAGE]["jobs"]
    client = connect()
    sftp = None
    legs, traces = [], []
    try:
        sftp = client.open_sftp()
        sftp.get_channel().settimeout(300)
        for row, job in enumerate(jobs, start=1):
            base = REMOTE + "/runs/" + job["dir"] + "/" + job["job"]
            artifacts, paths, files = {}, {}, []
            for suffix in SUFFIXES:
                data = remote_bytes(sftp, base + suffix)
                if data is None:
                    files.append(dict(suffix=suffix, status="REMOTE_ABSENT"))
                    continue
                path = RESULTS / "outputs" / job["site"] / (job["job"] + suffix)
                action = preserve(path, data)
                artifacts[suffix], paths[suffix] = data, path
                files.append(dict(suffix=suffix, path=path.relative_to(ROOT).as_posix(),
                                  status=action, sha256=sha(data), bytes=len(data)))
            identity_reasons = identity_problems(job, row, artifacts)
            reasons = validate_evidence(job, row, artifacts, paths, tasks[row])
            leg = dict(task=row, job=job["job"], site=job["site"], scheduler=tasks[row],
                       evidence_status="QC_EVIDENCE_INVALID" if reasons else "VERIFIED_COMPLETE",
                       reasons=reasons, files=files, tier_2_accepted=not reasons,
                       input_identity_verified=not identity_reasons, identity_reasons=identity_reasons)
            if ".out" in paths:
                import qe_relax_trace
                try:
                    trace = qe_relax_trace.trace(paths[".out"])
                except (ValueError, KeyError, TypeError, OverflowError) as error:
                    trace = dict(file=str(paths[".out"]), cycles=[], trace_error=str(error))
                    leg["trace_error"] = str(error)
                    leg["tier_2_accepted"] = False
                traces.append(trace)
                cycle = trace["cycles"][0] if len(trace["cycles"]) == 1 else {}
                eligible = [record for record in cycle.get("iteration_records", [])
                            if record["iteration"] <= job["max_iterations"] and record["accuracy_Ry"] is not None]
                leg["diagnostic_trace"] = dict(
                    completed_iterations=cycle.get("n_iter"), started_iterations=cycle.get("n_iter_started"),
                    first_iter_below=cycle.get("first_iter_below"), acc_min_Ry=cycle.get("acc_min_Ry"),
                    acc_last_Ry=cycle.get("acc_last_Ry"),
                    tier_1_crossing_observed=(any(record["accuracy_Ry"] < 1e-6 for record in eligible)
                                               if not identity_reasons and "trace_error" not in trace else None),
                    interpretation="Residual crossing only; failed or partial output is not an accepted SCF result")
            legs.append(leg)
            write("collection_progress.json", dict(at=now(), legs=legs, expected_legs=5))
    finally:
        if sftp is not None:
            sftp.close()
        client.close()
    assert_pins(pins)
    write("traces.json", traces)
    readout = dict(at=now(), status="READY_FOR_REVIEW", population=POPULATION, legs=legs,
                   accepted=sum(leg["tier_2_accepted"] for leg in legs), tasks=tasks, pins=pins,
                   scope="Numerical diagnostic outcomes; no relaxed slab, adsorption reference or census result")
    write("readout.json", readout)
    return readout


def add_batch_options(parser) -> None:
    """The five module constants of the 2026-09-19 diagnostic remain the defaults; another
    batch of the same research-batch schema names its own results directory, specification,
    wrappers, stage and population.  Receipts, locks and pins then live under that directory."""
    parser.add_argument("--results", default=None, help="repository-relative results directory")
    parser.add_argument("--spec", default=None, help="repository-relative launch specification")
    parser.add_argument("--slurm", default=None, help="repository-relative slurm wrapper")
    parser.add_argument("--submit", default=None, help="repository-relative submit script")
    parser.add_argument("--stage", default=None, help="stage name inside the specification")
    parser.add_argument("--runner", default=None, help="repository-relative batch runner the wrappers execute")
    parser.add_argument("--population", type=int, default=None, help="exact number of array tasks")


def configure(argv) -> None:
    pre = argparse.ArgumentParser(add_help=False)
    add_batch_options(pre)
    opts, _ = pre.parse_known_args(argv)
    if opts.results is not None:
        globals()["RESULTS"] = ROOT / portable(opts.results)
    for key in ("spec", "slurm", "submit", "runner"):
        if getattr(opts, key) is not None:
            globals()[key.upper()] = portable(getattr(opts, key))
    if opts.stage is not None:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", opts.stage):
            raise ValueError("unsafe stage name")
        globals()["STAGE"] = opts.stage
        globals()["JOB_NAME"] = "research-" + opts.stage
    if opts.population is not None:
        if not 1 <= opts.population <= 64:
            raise ValueError("population out of range")
        globals()["POPULATION"] = opts.population


def _main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("wait", "stage", "submit", "inspect", "release", "watch", "auto"))
    add_batch_options(parser)
    parser.add_argument("--wait-deadline", default="2026-09-23T12:00:00+00:00")
    parser.add_argument("--watch-deadline", default="2026-09-25T12:00:00+00:00")
    parser.add_argument("--poll", type=int, default=600)
    args = parser.parse_args(argv)
    wait_deadline = dt.datetime.fromisoformat(args.wait_deadline)
    watch_deadline = dt.datetime.fromisoformat(args.watch_deadline)
    if args.poll <= 0 or wait_deadline.tzinfo is None or watch_deadline.tzinfo is None:
        parser.error("positive poll interval and timezone-aware deadlines required")
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
                else:
                    verify_transfer(client)
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


def main(argv=None) -> int:
    configure(sys.argv[1:] if argv is None else argv)
    RESULTS.mkdir(parents=True, exist_ok=True)
    lock = RESULTS / ".launcher.lock"
    token = uuid.uuid4().hex
    try:
        with lock.open("x", encoding="utf-8") as handle:
            json.dump(dict(pid=os.getpid(), token=token, at=now()), handle)
    except FileExistsError as error:
        raise RuntimeError("launcher already active or lock needs inspection") from error
    try:
        return _main(argv)
    finally:
        if lock.exists() and json.loads(lock.read_text())["token"] == token:
            lock.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
