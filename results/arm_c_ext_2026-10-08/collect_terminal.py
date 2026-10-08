"""Read-only terminal collection: sacct accounting plus the small scientific files.

Mirrors every run's runtime input, output, projection output, QC receipt and stop marker, and
every Slurm log, into raw_mirror/, recording each file's remote and local sha256. Wavefunction
and charge-density binaries stay on Anvil.
"""
import datetime as dt
import hashlib
import json
import posixpath
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
JOBS = json.loads((HERE / "submit_receipt.json").read_text())["jobs"]
BASE = "/anvil/projects/x-che260157/sts_arm_c_ext_2026-10-08"
MIRROR = HERE / "raw_mirror"
SMALL = (".run.in", ".out", ".qc.json", ".KILLED", ".REJECTED", ".projwfc.in", ".log")


def connect():
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    return client


def run(client, command, timeout=300):
    _, out, err = client.exec_command(command, timeout=timeout)
    return out.read().decode(), err.read().decode(), out.channel.recv_exit_status()


client = connect()
receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "jobs": JOBS, "files": []}
ids = ",".join(JOBS.values())
receipt["sacct"] = run(client, "sacct -n -P -j " + ids + " -o JobID,JobName,State,Elapsed,Start,End,ExitCode,CPUTimeRAW,AllocTRES,TimeLimit,NodeList")[0]
receipt["mybalance"] = run(client, "mybalance")[0]
listing, _, _ = run(client, "cd " + BASE + " && find runs logs -type f -not -path '*/tmp_*' -size -50M -printf '%s %p\\n'")
sftp = client.open_sftp()
for line in sorted(listing.splitlines()):
    size, rel = line.split(" ", 1)
    if not rel.endswith(SMALL):
        continue
    local = MIRROR / rel
    local.parent.mkdir(parents=True, exist_ok=True)
    sftp.get(posixpath.join(BASE, rel), str(local))
    remote_sha = run(client, "sha256sum " + posixpath.join(BASE, rel))[0].split()[0]
    local_sha = hashlib.sha256(local.read_bytes()).hexdigest()
    receipt["files"].append({"path": rel, "bytes": int(size), "remote_sha256": remote_sha, "local_sha256": local_sha,
                             "match": remote_sha == local_sha})
client.close()
receipt["all_match"] = all(f["match"] for f in receipt["files"])
(HERE / "terminal_collection.json").write_bytes((json.dumps(receipt, indent=2) + "\n").encode())
print(json.dumps({"files": len(receipt["files"]), "all_match": receipt["all_match"]}))
