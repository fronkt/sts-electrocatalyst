"""One-shot read-only probe before designing the arm-C extension: retained save directories at the four
Cu8/Fe25 support sites in both arm-C roots, project quota, allocation balance and queue. No writes on Anvil."""
import datetime as dt
import json
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
ROOTS = {"production": "/anvil/projects/x-che260157/sts_arm_c_2026-10-07/runs/hea/arm_c_2026-10-07",
         "rerun": "/anvil/projects/x-che260157/sts_arm_c_2026-10-07_rerun/runs/hea/arm_c_2026-10-07_rerun"}
SITES = ["Cu8Cr23Mn35Co34__s16_site2", "Cu8Cr23Mn35Co34__s26_site1",
         "Fe25Co25Ni25Cr25__s13_site0", "Fe25Co25Ni25Cr25__s25_site2"]
COMMANDS = [("myquota", "bash -lc myquota"), ("mybalance", "bash -lc mybalance"),
            ("squeue", "squeue -h -u x-fcai3 -o '%i|%j|%T|%M|%R'")]
for root_name, root in ROOTS.items():
    for site in SITES:
        COMMANDS.append((root_name + ":" + site,
                         "cd " + root + "/" + site + " 2>/dev/null && for d in tmp_*; do "
                         "for s in \"$d\"/*.save; do [ -d \"$s\" ] && find \"$s\" -maxdepth 1 -type f "
                         "-not -name 'wfc*' -printf '%p %s\\n'; done; done"))

client = paramiko.SSHClient()
client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
client.set_missing_host_key_policy(paramiko.RejectPolicy())
client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
               allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
out = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "commands": {}}
try:
    for name, command in COMMANDS:
        _, stdout, stderr = client.exec_command(command, timeout=180)
        out["commands"][name] = {"command": command, "stdout": stdout.read().decode(),
                                 "stderr": stderr.read().decode(), "rc": stdout.channel.recv_exit_status()}
finally:
    client.close()
with (HERE / "seed_probe.json").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps(out, indent=2) + "\n")
print("done", flush=True)
