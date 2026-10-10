"""One-shot read-only status of the arm-C extension round-4 array: no submit, cancel, release, retry or QE.

Writes status_snapshot_<UTC stamp>.json beside this script (never overwrites).
"""
import datetime as dt
import json
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
JOBS = json.loads((HERE / "submit_receipt.json").read_text(encoding="utf-8"))["jobs"]
REMOTE = "/anvil/projects/x-che260157/sts_arm_c_ext_r4_2026-10-10"
PYTHON = "/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3"
SCRIPT = r'''
import json, pathlib, subprocess, sys
root = pathlib.Path(sys.argv[1])
jobs = json.loads(sys.argv[2])
ids = ",".join(jobs.values())
out = {"commands": {}, "receipts": {}}
for name, args in [
        ("squeue", ["squeue", "-h", "-u", "x-fcai3", "-o", "%i|%j|%T|%M|%l|%R"]),
        ("sacct", ["sacct", "-X", "-n", "-P", "-j", ids, "-o", "JobID,JobName,State,Elapsed,ExitCode,CPUTimeRAW,NodeList"]),
        ("balance", ["bash", "-lc", "mybalance"])]:
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=60)
    out["commands"][name] = {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
for qc in sorted((root / "runs").rglob("*.qc.json")):
    data = json.loads(qc.read_text())
    out["receipts"][str(qc.relative_to(root / "runs"))] = {
        "status": data.get("status"), "reason": data.get("reason"),
        "energy_Ry": (data.get("scf") or {}).get("energy_Ry"), "iterations": (data.get("scf") or {}).get("iterations"),
        "wall_seconds": (data.get("scf_process") or {}).get("wall_seconds")}
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
        command = " ".join([PYTHON, "-B", "-", REMOTE, "'" + json.dumps(JOBS) + "'"])
        stdin, stdout, stderr = client.exec_command(command, timeout=180)
        stdin.write(SCRIPT)
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
