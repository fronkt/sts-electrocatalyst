"""Cancel the held r1 main array after the failed canary (Frank, 2026-10-08: "repair").

The r1 main array pins the r1 seed files, so the repair (round 2) cannot reuse it. Refuses unless the array
is still pending and held; writes cancel_receipt.json beside this script (never overwrites).
"""
import datetime as dt
import json
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
MAIN = json.loads((HERE / "submit_receipt.json").read_text(encoding="utf-8"))["jobs"]["ext_main"]


def run(client, command):
    _, stdout, stderr = client.exec_command(command, timeout=60)
    text, err = stdout.read().decode(), stderr.read().decode()
    return {"command": command, "rc": stdout.channel.recv_exit_status(), "stdout": text, "stderr": err}


def main():
    if (HERE / "canary_check.json").exists() and json.loads((HERE / "canary_check.json").read_text())["passed"]:
        raise SystemExit("the canary passed: not cancelling")
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "job": MAIN, "steps": []}
    try:
        before = run(client, f"squeue -h -j {MAIN} -o '%i|%T|%r'")
        receipt["steps"].append(before)
        rows = [r.split("|") for r in before["stdout"].split()]
        if before["rc"] or not rows or any(r[1:] != ["PENDING", "JobHeldUser"] for r in rows):
            raise SystemExit("REFUSE: the main array is not pending and held: " + before["stdout"])
        receipt["steps"].append(run(client, f"scancel {MAIN}"))
        receipt["steps"].append(run(client, f"sacct -X -n -P -j {MAIN} -o JobID,State"))
    finally:
        client.close()
    states = [line.split("|")[1] for line in receipt["steps"][-1]["stdout"].split()]
    receipt["cancelled"] = bool(states) and all(s.startswith("CANCELLED") for s in states)
    with (HERE / "cancel_receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"job": MAIN, "cancelled": receipt["cancelled"], "states": states}), flush=True)
    if not receipt["cancelled"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
