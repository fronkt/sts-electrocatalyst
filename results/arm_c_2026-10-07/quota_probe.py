"""One-shot read-only query before staging arm C: project quota, root absence, QE binary sha256."""
import datetime as dt
import json
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
COMMANDS = [
    ("myquota", "bash -lc myquota"),
    ("root", "test -e /anvil/projects/x-che260157/sts_arm_c_2026-10-07 && echo EXISTS || echo ABSENT"),
    ("qe_sha", "sha256sum /anvil/projects/x-che260157/qe/env/bin/pw.x /anvil/projects/x-che260157/qe/env/bin/projwfc.x "
               "/anvil/projects/x-che260157/qe/env/bin/mpirun"),
]

client = paramiko.SSHClient()
client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
client.set_missing_host_key_policy(paramiko.RejectPolicy())
client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
               allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
out = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "commands": {}}
try:
    for name, command in COMMANDS:
        _, stdout, stderr = client.exec_command(command, timeout=120)
        out["commands"][name] = {"command": command, "stdout": stdout.read().decode(),
                                 "stderr": stderr.read().decode(), "rc": stdout.channel.recv_exit_status()}
finally:
    client.close()
with (HERE / "quota_probe.json").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps(out, indent=2) + "\n")
print("done", flush=True)
