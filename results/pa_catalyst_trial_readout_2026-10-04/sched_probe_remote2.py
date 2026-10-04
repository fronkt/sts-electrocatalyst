"""Read-only: `jobsu 21034683` (positional job id) and `mybalance` on Anvil; creates nothing."""
import json
import subprocess

out = {"job_id": "21034683", "readonly": True, "commands": {}}
for name, cmd in (("jobsu", "jobsu 21034683 2>&1"), ("mybalance", "mybalance 2>&1")):
    p = subprocess.run(["bash", "-lc", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=40)
    out["commands"][name] = {"cmd": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
print(json.dumps(out))
