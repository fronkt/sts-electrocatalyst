"""Read-only: pin round 4's start on Anvil and mirror the two PAW files it is rebuilt from.

Round 4 starts from the save round 3's Fe25 s25/2 O run wrote when QE stopped it. This lists that save and records
each file's size and sha256; its occup.txt must equal round 3's committed mirror. It also mirrors, sha256-checked,
the save's paw.txt and the paw.txt of the site's converged OH state (round 2's run, whose occup.txt round 3's
site_occupations.py mirrored): Fe 22's PAW block is taken from the latter. Writes start_sources.json and sources/.
Nothing on Anvil is changed.
"""
import datetime as dt
import hashlib
import json
import posixpath
import shlex
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECT = "/anvil/projects/x-che260157/"
R3_JOB = "O__atomic_moved_ndim16"
R3_SAVE = (PROJECT + "sts_arm_c_ext_r3_2026-10-09/runs/hea/arm_c_ext_r3_2026-10-09/Fe25Co25Ni25Cr25__s25_site2/tmp_"
           + R3_JOB + "/" + R3_JOB + ".save")
OH_JOB = "OH__atomic_moved"
OH_SAVE = (PROJECT + "sts_arm_c_ext_r2_2026-10-08/runs/hea/arm_c_ext_r2_2026-10-08/Fe25Co25Ni25Cr25__s25_site2/tmp_"
           + OH_JOB + "/" + OH_JOB + ".save")
MIRROR = (ROOT / "results/arm_c_ext_r3_2026-10-09/raw_mirror/runs/hea/arm_c_ext_r3_2026-10-09/Fe25Co25Ni25Cr25__s25_site2"
          / ("tmp_" + R3_JOB) / (R3_JOB + ".save/occup.txt"))
FETCH = {"r3_stop_paw.txt": R3_SAVE + "/paw.txt", "oh_paw.txt": OH_SAVE + "/paw.txt", "oh_occup.txt": OH_SAVE + "/occup.txt"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    fetched = {}
    try:
        _, out, err = client.exec_command("cd " + shlex.quote(R3_SAVE) + " && find . -maxdepth 1 -type f -printf '%s %f\\n'"
                                          " && sha256sum -- *", timeout=900)
        text, error = out.read().decode(), err.read().decode()
        sftp = client.open_sftp()
        (HERE / "sources").mkdir(exist_ok=True)
        for name, remote in FETCH.items():
            local = HERE / "sources" / name
            sftp.get(remote, str(local))
            _, out, _ = client.exec_command("sha256sum " + shlex.quote(remote), timeout=120)
            remote_sha = out.read().decode().split()[0]
            fetched[name] = {"remote": remote, "local": local.relative_to(ROOT).as_posix(), "sha256": sha(local.read_bytes()),
                             "match": remote_sha == sha(local.read_bytes())}
    finally:
        client.close()
    sizes, shas = {}, {}
    for line in text.splitlines():
        first, rest = line.split(None, 1)
        if first.isdigit():
            sizes[rest] = int(first)
        else:
            shas[rest.lstrip("*")] = first
    local = sha(MIRROR.read_bytes())
    result = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "save": R3_SAVE, "stderr": error,
              "files": {name: {"bytes": sizes.get(name), "sha256": shas.get(name)} for name in sorted(set(sizes) | set(shas))},
              "occup_mirror": MIRROR.relative_to(ROOT).as_posix(), "occup_mirror_sha256": local,
              "occup_matches_mirror": shas.get("occup.txt") == local, "fetched": fetched,
              "all_match": all(f["match"] for f in fetched.values()) and shas.get("paw.txt") == fetched["r3_stop_paw.txt"]["sha256"]}
    (HERE / "start_sources.json").write_bytes((json.dumps(result, indent=2) + "\n").encode())
    print(json.dumps({"files": sorted(result["files"]), "occup_matches_mirror": result["occup_matches_mirror"],
                      "all_match": result["all_match"]}))


if __name__ == "__main__":
    main()
