"""Read-only sftp copy of named small files under the O1 trial parent into a new local folder.

Usage: python fetch_readonly.py <local folder name> <path relative to base> ...
Refuses an existing folder and any remote file over 50 MB; records remote and local sha256.
"""
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
BASE = json.loads((HERE / "launch_spec.json").read_text(encoding="utf-8"))["trial_parent"]
LIMIT = 50 * 1024 * 1024


def main(folder, paths):
    target = HERE / folder
    target.mkdir()
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    rows = []
    try:
        sftp = client.open_sftp()
        for rel in paths:
            remote = BASE + "/" + rel
            row = {"path": rel}
            try:
                size = sftp.stat(remote).st_size
                if size > LIMIT:
                    raise ValueError("over 50 MB: %d" % size)
                local = target / rel
                local.parent.mkdir(parents=True, exist_ok=True)
                sftp.get(remote, str(local))
                _, out, _ = client.exec_command("sha256sum " + remote, timeout=60)
                remote_sha = out.read().decode().split()[0]
                local_sha = hashlib.sha256(local.read_bytes()).hexdigest()
                row.update({"bytes": size, "sha256": local_sha, "matches_remote": local_sha == remote_sha})
            except (OSError, ValueError, IndexError) as exc:
                row["error"] = repr(exc)
            rows.append(row)
    finally:
        client.close()
    receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "base": BASE, "files": rows}
    (target / "fetch_receipt.json").write_bytes((json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
    print("fetched", sum("sha256" in r for r in rows), "of", len(rows), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
