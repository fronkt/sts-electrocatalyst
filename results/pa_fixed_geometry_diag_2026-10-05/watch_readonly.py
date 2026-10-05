"""Read-only watch of the three diagnostic jobs: sacct/squeue only, never a Slurm write.

Appends one observation per poll to watch_observations.jsonl and exits when every job
is terminal, after a 36-hour deadline, or after 5 consecutive collection failures.
"""
import datetime as dt
import json
import time
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
JOBS = json.loads((HERE / "submit_receipt.json").read_text())["jobs"]
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED", "BOOT_FAIL", "DEADLINE"}
POLL, DEADLINE, MAX_FAILURES = 300, 36 * 3600, 5


def connect():
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    return client


def observe():
    client = connect()
    try:
        ids = ",".join(JOBS.values())
        _, out, _ = client.exec_command("sacct -X -n -P -j " + ids + " -o JobID,JobName,State,Elapsed,Start,End,ExitCode,CPUTimeRAW", timeout=60)
        rows = [line.split("|") for line in out.read().decode().splitlines() if line.strip()]
        return {"at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "jobs": {r[0]: {"name": r[1], "state": r[2].split()[0], "elapsed": r[3], "start": r[4], "end": r[5],
                                "exit": r[6], "cpu_time_raw": r[7]} for r in rows}}
    finally:
        client.close()


start, failures = time.monotonic(), 0
while True:
    try:
        row = observe()
        failures = 0
    except Exception as exc:
        failures += 1
        row = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "collection_error": str(exc)}
    with (HERE / "watch_observations.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row) + "\n")
    states = [j["state"] for j in row.get("jobs", {}).values()]
    if len(states) == len(JOBS) and all(s in TERMINAL for s in states):
        print("ALL TERMINAL", json.dumps(row), flush=True)
        break
    if failures >= MAX_FAILURES or time.monotonic() - start > DEADLINE:
        print("WATCH STOPPED", failures, flush=True)
        break
    time.sleep(POLL)
