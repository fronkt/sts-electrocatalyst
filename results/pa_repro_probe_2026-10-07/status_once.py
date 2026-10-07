"""One-shot read-only status of the submitted jobs: no submit, cancel, release, retry or QE.

Writes status_snapshot_<UTC stamp>.json beside this script (never overwrites).
"""
import datetime as dt
import json
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
SPEC = json.loads((HERE / "launch_spec.json").read_text(encoding="utf-8"))
JOBS = json.loads((HERE / "submit_receipt.json").read_text(encoding="utf-8"))["jobs"]
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
REMOTE = r'''
import json, pathlib, subprocess
base = pathlib.Path(%(base)r)
jobs = %(jobs)r
ids = ",".join(jobs.values())
out = {"commands": {}, "groups": {}}
for name, args in [
        ("squeue", ["squeue", "-h", "-u", "x-fcai3", "-o", "%%i|%%j|%%T|%%M|%%l|%%S|%%R"]),
        ("squeue_start", ["squeue", "-h", "--start", "-u", "x-fcai3", "-o", "%%i|%%j|%%T|%%S|%%R"]),
        ("sacct", ["sacct", "-X", "-n", "-P", "-j", ids, "-o", "JobID,JobName,State,Elapsed,Start,End,ExitCode,CPUTimeRAW"]),
        ("balance", ["bash", "-lc", "mybalance"])]:
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)
    out["commands"][name] = {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
for job in jobs.values():
    p = subprocess.run(["scontrol", "show", "job", job, "-o"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True, timeout=30)
    fields = dict(x.split("=", 1) for x in p.stdout.split() if "=" in x)
    out["commands"]["scontrol:" + job] = {k: fields.get(k) for k in
        ("JobState", "Reason", "Priority", "SubmitTime", "EligibleTime", "StartTime", "EndTime", "TimeLimit", "NodeList", "SchedNodeList")}
groups = base / "groups"
out["groups_dir_exists"] = groups.exists()
if groups.exists():
    for g in sorted(groups.iterdir()):
        row = {"entries": sorted(x.name for x in g.iterdir())}
        receipt = g / "group_receipt.json"
        if receipt.exists():
            data = json.loads(receipt.read_text())
            row["calls"] = [{k: c.get(k) for k in ("name", "status", "error")} for c in data.get("calls", [])]
            row["all_calls_completed"] = data.get("all_calls_completed")
        out["groups"][g.name] = row
logs = sorted(base.glob("diag_*.log"))
out["slurm_logs"] = {p.name: p.read_text(errors="replace")[-1500:] for p in logs}
runs = base / "runs"
if runs.exists():
    for r in sorted(runs.iterdir()):
        log = r / "stdout.log"
        if log.exists():
            text = log.read_text(errors="replace").splitlines()
            out.setdefault("run_tails", {})[r.name] = {
                "bytes": log.stat().st_size,
                "last_accuracy": [x for x in text if "estimated scf accuracy" in x][-3:],
                "iterations": sum(1 for x in text if x.strip().startswith("iteration #")),
                "done": any("JOB DONE." in x for x in text)}
print(json.dumps(out))
'''


def main():
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    try:
        stdin, stdout, stderr = client.exec_command(PYTHON + " -B -", timeout=120)
        stdin.write(REMOTE % {"base": SPEC["base"], "jobs": JOBS})
        stdin.channel.shutdown_write()
        text, err, rc = stdout.read().decode(), stderr.read().decode(), stdout.channel.recv_exit_status()
    finally:
        client.close()
    receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "rc": rc, "stderr": err,
               "jobs": JOBS, "remote": json.loads(text) if rc == 0 else text}
    with (HERE / ("status_snapshot_" + stamp + ".json")).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print("status rc", rc, flush=True)
    if rc:
        raise SystemExit(err)


if __name__ == "__main__":
    main()
