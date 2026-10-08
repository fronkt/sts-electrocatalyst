"""Read-only probe of the round-2 Anvil root after an interrupted stage (no writes on Anvil).

The stage phase of launch_ops.py was killed mid-run on 2026-10-08 (the local machine ran low on memory), so
it wrote no stage_receipt.json. This lists what reached the root: every file with size and mode, the
uploaded densities' sha256 against the spec pins, and the queue. Writes stage_probe_<UTC stamp>.json here.
"""
import datetime as dt
import json
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
REMOTE = "/anvil/projects/x-che260157/sts_arm_c_ext_r2_2026-10-08"
SPEC = json.loads((HERE / "launch_spec.json").read_text(encoding="utf-8"))
DENSITY = "charge-density.hdf5"


def main():
    pins = {f"{REMOTE}/{j['scratch_source']['save_dir']}/{DENSITY}": j["scratch_source"]["files"][DENSITY]
            for j in SPEC["stages"]["r2_main"]["jobs"]}
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)

    def run(command, timeout=300):
        _, out, err = client.exec_command(command, timeout=timeout)
        return {"command": command, "stdout": out.read().decode(), "stderr": err.read().decode(),
                "rc": out.channel.recv_exit_status()}

    receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "root": REMOTE}
    try:
        receipt["root_exists"] = run(f"test -e {REMOTE}")["rc"] == 0
        if receipt["root_exists"]:
            listing = run(f"find {REMOTE} -printf '%y %s %m %p\\n'")
            receipt["listing"] = listing["stdout"].splitlines()
            present = [p for p in pins if any(line.endswith(" " + p) for line in receipt["listing"])]
            sums = run("sha256sum " + " ".join(present), timeout=900)["stdout"] if present else ""
            found = {line.split()[1]: line.split()[0] for line in sums.splitlines() if line.strip()}
            receipt["densities"] = {p: {"present": p in present, "sha256_matches_pin": found.get(p) == pins[p]} for p in pins}
            receipt["files"] = sum(1 for line in receipt["listing"] if line.startswith("f "))
        receipt["queue"] = run("squeue -h -u x-fcai3 -o '%i|%j|%T|%R'")["stdout"].splitlines()
    finally:
        client.close()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    with (HERE / ("stage_probe_" + stamp + ".json")).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"root_exists": receipt["root_exists"], "files": receipt.get("files"),
                      "densities_complete": sum(d["sha256_matches_pin"] for d in receipt.get("densities", {}).values()),
                      "densities_present": sum(d["present"] for d in receipt.get("densities", {}).values()),
                      "queue": receipt["queue"]}), flush=True)


if __name__ == "__main__":
    main()
