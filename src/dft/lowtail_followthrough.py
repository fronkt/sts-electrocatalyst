"""Read-only remote follow-through for the launched nine-leg Cr relaxation array.

Observe sacct every five minutes, mirror only small named scientific artifacts
once every task is terminal, and produce a pinned primary-only readout for review.
Never submit, restart, cancel, commit, push, or remove remote evidence.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shlex
import time
import uuid

from lowtail_launch_ops import connect, REMOTE, ROOT
from paramiko import SSHException

RELATIVE = "results/lowtail_dft_2026-09-18"
SUFFIXES = (".out", ".run.in", ".qc.json", ".projwfc.in", ".projwfc.out", ".KILLED", ".REJECTED")
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE", "PREEMPTED", "REVOKED", "SPECIAL_EXIT"}
READOUT_SOURCES = ("src/dft/lowtail_followthrough.py", "src/dft/lowtail_launch_ops.py",
                   "src/s2/lowtail_dft/lt_readout.py", "src/s2/lowtail_dft/lt_qe.py",
                   "src/s2/lowtail_dft/lt_geometry.py", "src/s2/lowtail_dft/lt_common.py")
MAX_ARTIFACT_BYTES = 512 * 1024 * 1024


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def local_path(root, relative):
    path = Path(root) / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts or Path(root).resolve() not in path.resolve().parents:
        raise ValueError("path escapes repository: " + relative)
    if path.is_symlink():
        raise ValueError("symlink is not eligible evidence: " + relative)
    return path


def startup_pins(root, spec, spec_relative=RELATIVE + "/launch_spec.json"):
    pins = dict(spec["files"])
    for name in list(pins):
        if sha(local_path(root, name).read_bytes()) != pins[name]:
            raise ValueError("launch pin differs at watcher startup: " + name)
    for name in (*READOUT_SOURCES, spec_relative, RELATIVE + "/deck_plan.json", RELATIVE + "/operating_decisions.json"):
        pins[name] = sha(local_path(root, name).read_bytes())
    if len(spec["jobs"]) != 9 or any(j["projector"] != "atomic" or j["role"] != "primary" for j in spec["jobs"]):
        raise ValueError("watcher scope is exactly nine primary atomic jobs")
    for job in spec["jobs"]:
        if pins.get(job["path"]) != job["sha256"]:
            raise ValueError("job input not pinned: " + job["path"])
    return pins


def assert_pins(root, pins):
    changed = [p for p, expected in pins.items() if not local_path(root, p).is_file() or sha(local_path(root, p).read_bytes()) != expected]
    if changed:
        raise ValueError("watched source/input changed: " + ", ".join(changed))


def acquire_lock(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    identity = dict(pid=os.getpid(), token=uuid.uuid4().hex, started_at=now())
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(identity, handle)
    except FileExistsError:
        raise RuntimeError("watcher lock already exists; no duplicate started: " + str(path))
    return identity


def release_lock(path, identity):
    path = Path(path)
    if path.exists() and json.loads(path.read_text())["token"] == identity["token"]:
        path.unlink()


def parse_sacct(text, array_id):
    if not re.fullmatch(r"\d+", str(array_id)):
        raise ValueError("numeric array id required")
    rows = {}
    for line in text.splitlines():
        fields = line.strip().split("|")
        if len(fields) < 5:
            if line.strip():
                raise ValueError("malformed sacct row")
            continue
        match = re.fullmatch(re.escape(str(array_id)) + r"_(\d+)", fields[0])
        if not match:
            continue  # array aggregate and .batch/.extern are not separate scientific legs
        task = int(match[1])
        if task not in range(1, 10):
            raise ValueError("unexpected array task")
        state = fields[1].split()[0].rstrip("+")
        record = dict(task=task, job_id=fields[0], state=state, exit_code=fields[2],
                      elapsed_seconds=int(fields[3] or 0), allocated_cpus=int(fields[4] or 0), terminal=state in TERMINAL)
        if task in rows and rows[task] != record:
            raise ValueError("conflicting accounting records for task " + str(task))
        rows[task] = record
    missing = sorted(set(range(1, 10))-set(rows))
    return dict(array_id=str(array_id), observed_at=now(), tasks=[rows[k] for k in sorted(rows)],
                missing_tasks=missing, all_terminal=not missing and all(r["terminal"] for r in rows.values()),
                terminal_count=sum(r["terminal"] for r in rows.values()),
                allocated_core_hours=sum(r["elapsed_seconds"]*r["allocated_cpus"]/3600 for r in rows.values()))


class RemoteObservationError(RuntimeError):
    pass


def observe(client, array_id):
    argv = ["sacct", "--array", "-n", "-P", "-X", "-j", str(array_id),
            "--format=JobID%80,State%30,ExitCode,ElapsedRaw,AllocCPUS"]
    _, out, err = client.exec_command(shlex.join(argv), timeout=60)
    stdout, stderr = out.read().decode(), err.read().decode()
    rc = out.channel.recv_exit_status()
    if rc:
        raise RemoteObservationError("read-only sacct failed: " + stderr)
    return dict(parse_sacct(stdout, array_id), raw_stdout=stdout, raw_stderr=stderr, command=argv)


def read_remote(sftp, remote):
    try:
        before = sftp.stat(remote)
    except FileNotFoundError:
        return None
    if before.st_size > MAX_ARTIFACT_BYTES:
        raise ValueError("scientific artifact exceeds bounded mirror size: " + remote)
    with sftp.open(remote, "rb") as handle:
        data = handle.read(MAX_ARTIFACT_BYTES + 1)
    after = sftp.stat(remote)
    if len(data) != before.st_size or after.st_size != before.st_size or after.st_mtime != before.st_mtime:
        raise ValueError("remote evidence changed during terminal mirror: " + remote)
    return data


def preserve_bytes(path, data):
    path = Path(path)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("local evidence differs; not overwritten: " + str(path))
        return "ALREADY_IDENTICAL"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
    if path.read_bytes() != data:
        raise OSError("mirrored evidence differs after write")
    return "MIRRORED"


def qc_problems(job, artifacts, task):
    reasons = []
    if task["state"] != "COMPLETED" or task["exit_code"] != "0:0":
        reasons.append("scheduler outcome " + task["state"] + "/" + task["exit_code"])
    if ".out" not in artifacts:
        return "TERMINAL_OUTPUT_MISSING", reasons + ["terminal task has no raw pw.x output"]
    if ".qc.json" not in artifacts:
        return "TERMINAL_QC_MISSING", reasons + ["terminal task has no QC receipt"]
    try:
        qc = json.loads(artifacts[".qc.json"].decode("utf-8"))
    except (ValueError, UnicodeError):
        return "QC_EVIDENCE_INVALID", reasons + ["malformed QC receipt"]
    for field, suffix in (("output_sha256", ".out"), ("runtime_sha256", ".run.in"),
                          ("projection_sha256", ".projwfc.out"), ("projection_input_sha256", ".projwfc.in")):
        expected = qc.get(field)
        if expected is not None and (suffix not in artifacts or sha(artifacts[suffix]) != expected):
            reasons.append("QC hash mismatch or missing artifact: " + field)
    if qc.get("input_sha256") != job["sha256"] or qc.get("job") != job["job"] or qc.get("site") != job["site"]:
        reasons.append("QC input or job identity differs")
    if qc.get("status") == "COMPLETE":
        for suffix in (".out", ".run.in", ".projwfc.in", ".projwfc.out"):
            if suffix not in artifacts:
                reasons.append("COMPLETE receipt lacks " + suffix)
        if not qc.get("output_sha256") or not qc.get("runtime_sha256"):
            reasons.append("COMPLETE receipt lacks required hashes")
        if ".KILLED" in artifacts or ".REJECTED" in artifacts:
            reasons.append("COMPLETE receipt conflicts with failure sidecar")
        if ".projwfc.out" in artifacts:
            from projection_qc import projection_check
            try:
                projection_check(artifacts[".projwfc.out"].decode("utf-8"), job["nat"])
            except (ValueError, UnicodeError) as error:
                reasons.append("projection evidence rejected: " + str(error))
    else:
        return "TERMINAL_QC_FAILED", reasons + ["QC status " + str(qc.get("status")), str(qc.get("reason", ""))]
    if reasons:
        return "SCHEDULER_FAILED" if reasons[0].startswith("scheduler") and len(reasons)==1 else "QC_EVIDENCE_INVALID", reasons
    return None, []


def mirror_terminal(client, root, spec, snapshot, result_dir):
    if not snapshot["all_terminal"] or len(snapshot["tasks"]) != 9:
        raise ValueError("mirror requires all nine tasks terminal")
    sftp = client.open_sftp()
    sftp.get_channel().settimeout(60)
    tasks = {r["task"]:r for r in snapshot["tasks"]}
    receipt, failures = [], {}
    try:
        for row, job in enumerate(spec["jobs"], 1):
            stem = "runs/" + job["manifest_dir"] + "/" + job["job"]
            artifacts, records = {}, []
            for suffix in SUFFIXES:
                relative = stem + suffix
                data = read_remote(sftp, REMOTE + "/" + relative)
                if data is None:
                    records.append(dict(path=relative, status="REMOTE_ABSENT"))
                    continue
                artifacts[suffix] = data
                try:
                    action = preserve_bytes(local_path(root, relative), data)
                except ValueError:
                    conflict = Path(result_dir) / "conflicts" / (job["site"] + "__" + job["job"] + suffix + "." + sha(data))
                    preserve_bytes(conflict, data)
                    raise
                records.append(dict(path=relative, status=action, bytes=len(data), sha256=sha(data)))
            status, reasons = qc_problems(job, artifacts, tasks[row])
            leg = dict(task=row, job=job["job"], site=job["site"], scheduler=tasks[row],
                       evidence_status=status or "VERIFIED_COMPLETE", reasons=reasons, files=records)
            receipt.append(leg)
            if status:
                failures[job["site"]+"/"+job["job"]] = dict(status=status, reasons=reasons, scheduler=tasks[row])
            # Each finished mirror is durable even if a later leg conflicts or connectivity drops.
            write_json(Path(result_dir)/"mirror_progress.json",dict(at=now(),array_id=snapshot["array_id"],legs=receipt))
    finally:
        sftp.close()
    return dict(at=now(),array_id=snapshot["array_id"],legs=receipt,terminal_failures=failures)


def primary_readout(root, spec, mirror, result_dir):
    import sys
    sys.path.insert(0, str(Path(root)/"src/s2/lowtail_dft"))
    readout = importlib.import_module("lt_readout")
    plan = readout.primary_plan(json.loads(local_path(root,RELATIVE+"/deck_plan.json").read_text()))
    if {(d["site"],d["job"],d["sha256"]) for d in plan["decks"]} != {(d["site"],d["job"],d["sha256"]) for d in spec["jobs"]}:
        raise ValueError("primary readout plan differs from launched inputs")
    decisions = json.loads(local_path(root,RELATIVE+"/operating_decisions.json").read_text())
    result = readout.readout(plan, decisions, Path(root)/"runs", Path(root), terminal_failures=mirror["terminal_failures"])
    if result["pending"]:
        failures = dict(mirror["terminal_failures"])
        for job in result["pending"]:
            failures[job] = dict(status="QC_EVIDENCE_INVALID", reasons=["scheduler is terminal but raw numerical evidence remains incomplete"])
        result = readout.readout(plan, decisions, Path(root)/"runs", Path(root), terminal_failures=failures)
    if sum(result["leg_counts"].values()) != 9 or result["pending"]:
        raise ValueError("terminal primary readout must contain nine terminal legs")
    result.update(array_id=mirror["array_id"], unrun_projector_controls="Nine ortho controls remain conditional and unrun; excluded from the nine-leg denominator.",
                  scientific_review="READY_FOR_REVIEW: independent scientific interpretation is still required")
    write_json(Path(result_dir)/"primary_readout.json",result)
    return result


def status_view(status, current=None):
    result = dict(status)
    stamp = status.get("last_observed_at")
    current = current or dt.datetime.now(dt.timezone.utc)
    age = (current-dt.datetime.fromisoformat(stamp)).total_seconds() if stamp else None
    result["observation_age_seconds"] = age
    result["observation_is_stale"] = age is None or age > status.get("poll_seconds",300)*3
    if result["observation_is_stale"] and status.get("state") in ("WATCHING", "RETRYING_REMOTE_OBSERVATION"):
        result["display_state"] = "STALE_OBSERVATION; scheduler state is not current"
    else:
        result["display_state"] = status.get("state")
    return result


def watch(root, array_id, *, poll_seconds=300, max_hours=240, once=False):
    if poll_seconds < 300 or not 0 < max_hours <= 720:
        raise ValueError("poll at most every five minutes; finite maximum of 720 hours")
    root = Path(root)
    result_dir = root/RELATIVE/"followthrough"
    identity = acquire_lock(result_dir/"active.lock")
    started = time.monotonic()
    status = dict(state="STARTING", array_id=str(array_id), started_at=now(), poll_seconds=poll_seconds,
                  max_hours=max_hours, pid=os.getpid(), last_observed_at=None,
                  scope="read-only scheduler and scientific artifacts; no submission, restart, commit or push")
    try:
        spec = json.loads(local_path(root,RELATIVE+"/launch_spec.json").read_text())
        submission = json.loads(local_path(root,RELATIVE+"/submission.json").read_text())
        if str(submission["job_id"]) != str(array_id):
            raise ValueError("array id differs from submission receipt")
        pins = startup_pins(root,spec)
        write_json(result_dir/"startup_pins.json",dict(at=now(),array_id=str(array_id),files=pins))
        while time.monotonic()-started < max_hours*3600:
            assert_pins(root,pins)
            client = None
            try:
                client = connect()
                snapshot = observe(client,array_id)
                status.update(state="WATCHING",heartbeat_at=now(),last_observed_at=snapshot["observed_at"],
                              terminal_count=snapshot["terminal_count"],missing_tasks=snapshot["missing_tasks"],last_error=None)
                write_json(result_dir/"scheduler_latest.json",snapshot)
                write_json(result_dir/"status.json",status_view(status))
                if snapshot["all_terminal"]:
                    assert_pins(root,pins)
                    mirror = mirror_terminal(client,root,spec,snapshot,result_dir)
                    write_json(result_dir/"mirror_receipt.json",mirror)
                    assert_pins(root,pins)
                    result = primary_readout(root,spec,mirror,result_dir)
                    status.update(state="READY_FOR_REVIEW",finished_at=now(),leg_counts=result["leg_counts"],
                                  readout=str(result_dir/"primary_readout.json"),
                                  independent_scientific_review="PENDING",conditional_ortho_controls="UNRUN")
                    write_json(result_dir/"status.json",status_view(status))
                    return 0
            except (OSError, EOFError, SSHException, RemoteObservationError) as error:
                status.update(state="RETRYING_REMOTE_OBSERVATION",heartbeat_at=now(),last_error=repr(error))
                write_json(result_dir/"status.json",status_view(status))
            finally:
                if client is not None:
                    client.close()
            if once:
                status.update(state="STOPPED_AFTER_ONE_OBSERVATION",finished_at=now())
                write_json(result_dir/"status.json",status_view(status))
                return 3
            time.sleep(poll_seconds)
        status.update(state="STOPPED_MONITOR_DEADLINE",finished_at=now(),meaning="Monitoring deadline reached; no calculation was stopped or inferred terminal.")
        write_json(result_dir/"status.json",status_view(status))
        return 4
    except Exception as error:
        status.update(state="STOPPED_REQUIRES_REVIEW",finished_at=now(),last_error=repr(error),
                      meaning="Watcher stopped; remote calculations and existing evidence were not modified.")
        write_json(result_dir/"status.json",status_view(status))
        raise
    finally:
        release_lock(result_dir/"active.lock",identity)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--array",default="20813525")
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--poll-seconds",type=int,default=300)
    p.add_argument("--max-hours",type=float,default=240)
    p.add_argument("--once",action="store_true")
    p.add_argument("--status",action="store_true")
    a=p.parse_args(argv)
    if a.status:
        status=json.loads((a.root/RELATIVE/"followthrough/status.json").read_text())
        print(json.dumps(status_view(status),indent=2),flush=True)
        return 0
    return watch(a.root,a.array,poll_seconds=a.poll_seconds,max_hours=a.max_hours,once=a.once)


if __name__ == "__main__":
    raise SystemExit(main())
