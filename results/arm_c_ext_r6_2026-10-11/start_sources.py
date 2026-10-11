"""Read-only: pin round 6's starts on Anvil and mirror the occupations its screen and rebuilt files use.

Round 6 restarts the slab and the OH at Ni31 s1/0 and Cu26 s1/0, each from the save its accepted run wrote when it
converged (arm C, 2026-10-07). For each of those four saves this lists the save, records the size of each file and
the sha256 of the four the start uses, and mirrors its occup.txt and paw.txt. For the screen it also mirrors the
occup.txt of the accepted slab and OH at the other value sites (Ni31 s10/2, Cu22 s24/3, Ni34 s29/1); Fe25 s25/2's
are committed already (round 5's mirror and round 3's site_occupations/). The accepted run of each state comes
from round 5's readout; a re-run accepted for the state puts its save under the re-run root. Every mirrored file is
sha256-checked against Anvil. Writes start_sources.json and sources/. Nothing on Anvil is changed.
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
READOUT = json.loads((ROOT / "results/arm_c_ext_r5_2026-10-10/readout.json").read_text(encoding="utf-8"))
PROJECT = "/anvil/projects/x-che260157/"
ROOTS = {"production": "sts_arm_c_2026-10-07/runs/hea/arm_c_2026-10-07",
         "rerun": "sts_arm_c_2026-10-07_rerun/runs/hea/arm_c_2026-10-07_rerun"}
STARTS = ("Ni31Cr29Cu5Mn35__s1_site0", "Cu26Ni9Cr31Co33__s1_site0")
SCREEN = ("Ni31Cr29Cu5Mn35__s10_site2", "Cu22Fe30Co32Mn15__s24_site3", "Ni34Fe6Cu29Co31__s29_site1")
STATES = ("slab", "OH")
USED = ("charge-density.hdf5", "data-file-schema.xml", "occup.txt", "paw.txt")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def accepted(site, state):
    """The accepted run of one state at one site, and the root its save is under."""
    row = next(s for s in READOUT["sites"] if Path(s["dir"]).name == site)
    job = row["states"][state]["job"]
    if not row["complete"] or any(a["job"] == job and a["accepted"] for a in row.get("extension_attempts", [])):
        raise SystemExit(f"{site} {state}: expected a complete site whose state comes from arm C")
    layer = "rerun" if any(a["job"] == job and a["accepted"] for a in row.get("rerun_attempts", [])) else "production"
    return job, layer


def main():
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    saves = {}
    try:
        sftp = client.open_sftp()
        for site in STARTS + SCREEN:
            for state in STATES:
                job, layer = accepted(site, state)
                save = PROJECT + ROOTS[layer] + "/" + site + "/tmp_" + job + "/" + job + ".save"
                entry = {"site": site, "state": state, "job": job, "layer": layer, "save": save, "fetched": {}}
                if site in STARTS:
                    command = ("cd " + shlex.quote(save) + " && find . -maxdepth 1 -type f -printf '%s %f\\n' && "
                               "sha256sum -- " + " ".join(USED))
                    _, out, err = client.exec_command(command, timeout=900)
                    text, entry["stderr"] = out.read().decode(), err.read().decode()
                    sizes, shas = {}, {}
                    for line in text.splitlines():
                        first, rest = line.split(None, 1)
                        if first.isdigit():
                            sizes[rest] = int(first)
                        else:
                            shas[rest.lstrip("*")] = first
                    entry["listing"] = dict(sorted(sizes.items()))
                    entry["files"] = {name: {"bytes": sizes.get(name), "sha256": shas.get(name)} for name in USED}
                for name in (("occup.txt", "paw.txt") if site in STARTS else ("occup.txt",)):
                    remote = posixpath.join(save, name)
                    local = HERE / "sources" / site / (job + "." + name)
                    local.parent.mkdir(parents=True, exist_ok=True)
                    sftp.get(remote, str(local))
                    _, out, _ = client.exec_command("sha256sum " + shlex.quote(remote), timeout=120)
                    remote_sha = out.read().decode().split()[0]
                    digest = sha(local.read_bytes())
                    entry["fetched"][name] = {"remote": remote, "local": local.relative_to(ROOT).as_posix(),
                                              "sha256": digest, "match": remote_sha == digest}
                saves[site + "/" + state] = entry
    finally:
        client.close()
    for entry in saves.values():
        ok = all(f["match"] for f in entry["fetched"].values())
        if "files" in entry:  # a start: every used file listed and hashed, and the mirrors are those files
            ok = ok and all(f["sha256"] and f["bytes"] for f in entry["files"].values()) and all(
                entry["files"][name]["sha256"] == f["sha256"] for name, f in entry["fetched"].items())
        entry["all_match"] = ok
    result = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readout": "results/arm_c_ext_r5_2026-10-10/readout.json",
              "saves": saves, "all_match": all(e["all_match"] for e in saves.values())}
    (HERE / "start_sources.json").write_bytes((json.dumps(result, indent=2) + "\n").encode())
    print(json.dumps({"saves": len(saves), "all_match": result["all_match"]}))


if __name__ == "__main__":
    main()
