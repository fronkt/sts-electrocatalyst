"""One-shot read-only query of Anvil scheduling limits for pricing arm C: no submit, cancel or QE.

Writes anvil_limits_<UTC stamp>.json beside this script (never overwrites).
"""
import datetime as dt
import json
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
COMMANDS = [
    ("partition", "scontrol show partition wholenode -o"),
    ("sinfo", "sinfo -p wholenode -h -o '%P|%l|%D|%a|%T'"),
    ("assoc", "sacctmgr -n -P show assoc user=x-fcai3 format=Account,Partition,MaxJobs,MaxSubmit,MaxWall,GrpTRES,MaxTRES,QOS"),
    ("qos", "sacctmgr -n -P show qos part-standard format=Name,MaxWall,MaxJobsPU,MaxSubmitPU,MaxTRESPU,Priority"),
    ("queue_pending", "squeue -p wholenode -h -t PD -o '%i' | wc -l"),
    ("queue_running", "squeue -p wholenode -h -t R -o '%i' | wc -l"),
    ("mine", "squeue -u x-fcai3 -h -o '%i|%j|%T|%M|%l|%R'"),
    ("balance", "mybalance"),
]


def main():
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    out = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "commands": {}}
    try:
        for name, command in COMMANDS:
            _, stdout, stderr = client.exec_command("bash -lc " + json.dumps(command), timeout=60)
            out["commands"][name] = {"command": command, "stdout": stdout.read().decode(),
                                     "stderr": stderr.read().decode(), "rc": stdout.channel.recv_exit_status()}
    finally:
        client.close()
    with (HERE / ("anvil_limits_" + stamp + ".json")).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(out, indent=2) + "\n")
    print("done", stamp, flush=True)


if __name__ == "__main__":
    main()
