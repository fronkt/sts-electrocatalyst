"""Read-only: mirror the Hubbard occupations (occup.txt) of the converged states at round 3's two sites.

Round 3's readout sets each stalled run's last occupations against its start. These files let them be set against
every converged state at the site as well (the stalled-run check under Round 3's "Checks written down before any
result"). The accepted run of each state comes from readout.json; its recipe gives the Anvil root. Writes
site_occupations/<root>/<site>/<job>.occup.txt and site_occupations.json with each file's remote and local sha256.
"""
import datetime as dt
import hashlib
import json
import posixpath
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
PLAN = json.loads((HERE / "ext_plan.json").read_text(encoding="utf-8"))
READOUT = json.loads((HERE / "readout.json").read_text(encoding="utf-8"))
PROJECT = "/anvil/projects/x-che260157/"
ROOTS = {"production": "sts_arm_c_2026-10-07/runs/hea/arm_c_2026-10-07",
         "ndim16": "sts_arm_c_2026-10-07_rerun/runs/hea/arm_c_2026-10-07_rerun",
         "seeded": "sts_arm_c_ext_r2_2026-10-08/runs/hea/arm_c_ext_r2_2026-10-08"}
LOCAL = HERE / "site_occupations"


def accepted_states():
    """(site, state, recipe, job) of every accepted state at the plan's sites."""
    sites = {Path(row["site_dir"]).name for row in PLAN["selection"]}
    found = []
    for site in READOUT["sites"]:
        name = Path(site["dir"]).name
        if name in sites:
            found += [(name, state, v["recipe"], v["job"]) for state, v in site["states"].items() if v["accepted"]]
    return sorted(found)


def main():
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "files": []}
    try:
        sftp = client.open_sftp()
        for site, state, recipe, job in accepted_states():
            remote = posixpath.join(PROJECT, ROOTS[recipe], site, "tmp_" + job, job + ".save", "occup.txt")
            local = LOCAL / Path(ROOTS[recipe]).name / site / (job + ".occup.txt")
            local.parent.mkdir(parents=True, exist_ok=True)
            sftp.get(remote, str(local))
            _, out, _ = client.exec_command("sha256sum " + remote, timeout=60)
            remote_sha = out.read().decode().split()[0]
            local_sha = hashlib.sha256(local.read_bytes()).hexdigest()
            receipt["files"].append({"site": site, "state": state, "recipe": recipe, "job": job, "remote": remote,
                                     "local": local.relative_to(HERE).as_posix(), "sha256": local_sha,
                                     "match": remote_sha == local_sha})
    finally:
        client.close()
    receipt["all_match"] = all(f["match"] for f in receipt["files"])
    (HERE / "site_occupations.json").write_bytes((json.dumps(receipt, indent=2) + "\n").encode())
    print(json.dumps({"files": len(receipt["files"]), "all_match": receipt["all_match"]}))


if __name__ == "__main__":
    main()
