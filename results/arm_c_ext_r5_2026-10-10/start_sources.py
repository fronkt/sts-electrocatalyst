"""Read-only: pin round 5's start on Anvil and mirror the PAW file it is rebuilt from.

Round 5 starts from the save the production run of the Fe25 s25/2 slab wrote when it converged (arm C, 2026-10-07).
This lists that save and records the size of each file and the sha256 of the four the start uses. They must equal
the pins round 1 recorded for this save (seed_fetch.json), and its occup.txt round 3's mirror of it
(site_occupations/). It also mirrors the save's paw.txt, sha256-checked: Fe 22's PAW block in it is replaced by the
converged OH state's (round 4's sources/oh_paw.txt). Writes start_sources.json and sources/. Nothing on Anvil is
changed.
"""
import datetime as dt
import hashlib
import json
import shlex
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROJECT = "/anvil/projects/x-che260157/"
SITE = "Fe25Co25Ni25Cr25__s25_site2"
JOB = "slab__atomic"
SAVE = PROJECT + "sts_arm_c_2026-10-07/runs/hea/arm_c_2026-10-07/" + SITE + "/tmp_" + JOB + "/" + JOB + ".save"
USED = ("charge-density.hdf5", "data-file-schema.xml", "occup.txt", "paw.txt")
ROUND_1 = json.loads((ROOT / "results/arm_c_ext_2026-10-08/seed_fetch.json").read_text(encoding="utf-8"))
ROUND_1_PINS = ROUND_1["seeds"][SITE + "__" + JOB]
MIRROR = ROOT / "results/arm_c_ext_r3_2026-10-09/site_occupations/arm_c_2026-10-07" / SITE / (JOB + ".occup.txt")
FETCH = {"slab_paw.txt": SAVE + "/paw.txt"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if ROUND_1_PINS["save_dir"] != SAVE:
        raise SystemExit("round 1 pinned a different save")
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    fetched = {}
    try:
        command = ("cd " + shlex.quote(SAVE) + " && find . -maxdepth 1 -type f -printf '%s %f\\n' && sha256sum -- "
                   + " ".join(USED))
        _, out, err = client.exec_command(command, timeout=900)
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
    result = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "save": SAVE, "stderr": error,
              "listing": dict(sorted(sizes.items())),
              "files": {name: {"bytes": sizes.get(name), "sha256": shas.get(name)} for name in USED},
              "round_1_pins": "results/arm_c_ext_2026-10-08/seed_fetch.json",
              "matches_round_1": all(shas.get(name) == ROUND_1_PINS["sha256"][name] for name in USED),
              "occup_mirror": MIRROR.relative_to(ROOT).as_posix(), "occup_mirror_sha256": local,
              "occup_matches_mirror": shas.get("occup.txt") == local, "fetched": fetched}
    result["all_match"] = (result["matches_round_1"] and result["occup_matches_mirror"]
                           and all(f["match"] for f in fetched.values())
                           and shas.get("paw.txt") == fetched["slab_paw.txt"]["sha256"])
    (HERE / "start_sources.json").write_bytes((json.dumps(result, indent=2) + "\n").encode())
    print(json.dumps({"files": sorted(result["listing"]), "matches_round_1": result["matches_round_1"],
                      "occup_matches_mirror": result["occup_matches_mirror"], "all_match": result["all_match"]}))


if __name__ == "__main__":
    main()
