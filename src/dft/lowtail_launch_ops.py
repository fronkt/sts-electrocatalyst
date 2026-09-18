"""Stage pushed bytes, inspect held resources, then release the primary Cr array.

Local execution uses the project's isolated Windows background worker.
Each phase writes an independent receipt; it never resubmits an existing launch.
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
import subprocess

import paramiko

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results/lowtail_dft_2026-09-18"
REMOTE = "/anvil/projects/x-che260157/sts"
PROJECT = "/anvil/projects/x-che260157"
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SPEC = "results/lowtail_dft_2026-09-18/launch_spec.json"
SCRIPT = "anvil/75_lowtail_relaxation.slurm"


def write(name, value):
    (RESULTS / name).write_bytes((json.dumps(value, indent=2, allow_nan=False) + "\n").encode())


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def connect():
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3",
                   key_filename=str(Path.home() / ".ssh/id_ed25519"), allow_agent=False,
                   look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    return client


def command(client, args, timeout=90):
    text = args if isinstance(args, str) else shlex.join(map(str, args))
    _, out, err = client.exec_command(text, timeout=timeout)
    result = dict(command=text, stdout=out.read().decode(), stderr=err.read().decode(), rc=out.channel.recv_exit_status())
    print(json.dumps(result), flush=True)
    if result["rc"]:
        raise RuntimeError(json.dumps(result))
    return result


def preflight(client):
    return command(client, [PYTHON, REMOTE + "/src/dft/lowtail_batch.py", "--spec", REMOTE + "/" + SPEC,
                           "--root", REMOTE, "--pseudo", PROJECT + "/pseudo", "--preflight"])


def stage(client, spec):
    boundary = json.loads((RESULTS / "boundary.json").read_text())
    commit = boundary["commit"]
    remote_ref = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/r0-catalysis-revival"], cwd=ROOT, text=True).split()[0]
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, remote_ref], cwd=ROOT).returncode:
        raise ValueError("launch boundary is not pushed")
    if (RESULTS / "submission.json").exists():
        raise ValueError("already submitted")
    sftp = client.open_sftp()
    sftp.get_channel().settimeout(60)
    def mkdirs(path):
        try:
            sftp.stat(path)
        except FileNotFoundError:
            mkdirs(posixpath.dirname(path))
            sftp.mkdir(path)
    receipt = dict(at=now(), commit=commit, files=[], checks=[])
    for relative in list(spec["files"]) + [SPEC, SCRIPT]:
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
        tmp = dest + ".upload_20260918"
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
    receipt["checks"].append(command(client, ["bash", "-n", REMOTE + "/" + SCRIPT]))
    receipt["checks"].append(preflight(client))
    write("transfer.json", receipt)


def inspect_held(client, job_id, spec):
    result = command(client, ["scontrol", "show", "job", "-o", job_id])
    text = result["stdout"]
    fields = dict(re.findall(r"(?:^|\s)([A-Za-z][A-Za-z0-9_]*)=(\S+)", text))
    needed = dict(JobState="PENDING", Reason="JobHeldUser", NumCPUs="128", NumTasks="128", Requeue="0",
                  Account="che260157", ArrayTaskId="1-9%1", MinMemoryNode="237G",
                  Partition="shared", WorkDir=REMOTE, ArrayJobId=job_id)
    for key, value in needed.items():
        if fields.get(key) != value:
            raise ValueError(f"held resource mismatch {key}: {fields.get(key)} != {value}")
    if fields.get("NumNodes") not in ("1", "1-1"):
        raise ValueError("held node range is not exactly one node")
    minutes = spec["wall_minutes"]
    if fields.get("TimeLimit") != f"{minutes//60:02}:{minutes%60:02}:00":
        raise ValueError("held wall differs")
    if not set(spec["exclusions"].split(",")).issubset(set(fields.get("ExcNodeList", "").split(","))):
        # Slurm can compress node lists; expand before comparison.
        expanded = command(client, ["scontrol", "show", "hostnames", fields.get("ExcNodeList", "")])["stdout"].split()
        if not set(spec["exclusions"].split(",")).issubset(expanded):
            raise ValueError("missing excluded nodes")
    if fields.get("Command") != REMOTE + "/" + SCRIPT:
        raise ValueError("held command differs")
    return result


def submit(client, spec):
    if (RESULTS / "submission.json").exists():
        raise ValueError("existing submission receipt: no duplicate launch")
    preflight(client)
    balance = command(client, "mybalance")
    match = re.search(r"^che260157\s+CPU\s+\S+\s+\S+\s+\S+\s+(\S+)", balance["stdout"], re.M)
    if not match or float(match[1]) < spec["scheduler_ceiling_core_hours"]:
        raise ValueError("insufficient current balance")
    queue = command(client, ["squeue", "-u", "x-fcai3", "-h", "-o", "%i|%j|%T"])
    if "lowtail-primary" in queue["stdout"]:
        raise ValueError("existing lowtail array")
    command(client, ["test", "-f", PROJECT + "/parity/PARITY_PASS"])
    command(client, ["mkdir", "-p", REMOTE + "/logs"])
    result = command(client, ["sbatch", "--parsable", "--hold", "--no-requeue", "--account=che260157",
        "--partition=shared", "--nodes=1", "--ntasks=128", "--mem=237G", f"--time={spec['wall_minutes']}",
        "--array=1-9%1", "--exclude=" + spec["exclusions"], "--job-name=lowtail-primary",
        "--chdir=" + REMOTE, "--export=ALL,PROJECT=" + PROJECT, REMOTE + "/" + SCRIPT])
    job_id = result["stdout"].strip().split(";")[0]
    if not job_id.isdigit():
        raise ValueError("unexpected sbatch id")
    receipt = dict(at=now(), job_id=job_id, submission=result, balance=balance, queue_before=queue, released=False)
    write("submission.json", receipt)
    receipt["held_inspection"] = inspect_held(client, job_id, spec)
    write("submission.json", receipt)


def release(client, spec):
    receipt = json.loads((RESULTS / "submission.json").read_text())
    if receipt["released"]:
        raise ValueError("already released")
    inspection = inspect_held(client, receipt["job_id"], spec)
    preflight(client)
    result = command(client, ["scontrol", "release", receipt["job_id"]])
    receipt.update(released=True, released_at=now(), final_held_inspection=inspection, release=result)
    write("submission.json", receipt)
    write("startup.json", dict(at=now(), state=command(client, ["squeue", "-j", receipt["job_id"], "-o", "%i|%T|%M|%R"])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("stage", "submit", "release"))
    args = parser.parse_args()
    spec = json.loads((ROOT / SPEC).read_text())
    client = connect()
    try:
        {"stage": stage, "submit": submit, "release": release}[args.phase](client, spec)
    finally:
        client.close()


if __name__ == "__main__":
    main()
