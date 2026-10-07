"""One-shot read-only status of the O1 job: no submit, cancel, release, retry or QE.

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
parent = pathlib.Path(%(parent)r)
jobs = %(jobs)r
ids = ",".join(jobs.values())
out = {"commands": {}}
for name, args in [
        ("squeue", ["squeue", "-h", "-u", "x-fcai3", "-o", "%%i|%%j|%%T|%%M|%%l|%%S|%%R"]),
        ("sacct", ["sacct", "-X", "-n", "-P", "-j", ids, "-o", "JobID,JobName,State,Elapsed,Start,End,ExitCode,CPUTimeRAW,NodeList"]),
        ("balance", ["bash", "-lc", "mybalance"])]:
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)
    out["commands"][name] = {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
receipt = parent / "trial_results" / "trial_receipt.json"
out["trial_results_exists"] = receipt.parent.exists()
if receipt.exists():
    data = json.loads(receipt.read_text())
    out["trial"] = {k: data.get(k) for k in ("scientific_status", "scheduler_status", "call_count", "elapsed_seconds", "error")}
    out["calls"] = [{k: c.get(k) for k in ("name", "kind", "status", "error")} for c in data.get("calls", [])]
    out["continuity"] = {k: (data.get("continuity") or {}).get(k) for k in ("max_abs_deltas", "tolerances", "within_tolerances")}
    out["conv_thr_carry"] = data.get("conv_thr_carry")
    out["pre_resume_action"] = (data.get("pre_resume_decision") or {}).get("action")
logs = sorted(parent.glob("o1_*.log"))
out["slurm_logs"] = {p.name: p.read_text(errors="replace")[-1500:] for p in logs}
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
        stdin.write(REMOTE % {"parent": SPEC["trial_parent"], "jobs": JOBS})
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
