"""Read-only fetch for the arm-C extension (no writes on Anvil).

For each of the five converged seed states: sha256 of the four retained save files and a local
copy of occup.txt and paw.txt (Hubbard occupations, PAW becsum). For each of the eleven target
states: a local copy of the same two files from its last failed attempt, used only as a layout
reference (array sizes and per-atom patterns). The 150 MB densities stay on Anvil.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
PROD = "/anvil/projects/x-che260157/sts_arm_c_2026-10-07/runs/hea/arm_c_2026-10-07"
RERUN = "/anvil/projects/x-che260157/sts_arm_c_2026-10-07_rerun/runs/hea/arm_c_2026-10-07_rerun"
SEEDS = {
    "Cu8Cr23Mn35Co34__s16_site2__O__atomic_ndim16": (RERUN, "Cu8Cr23Mn35Co34__s16_site2", "O__atomic_ndim16"),
    "Cu8Cr23Mn35Co34__s26_site1__OH__atomic": (PROD, "Cu8Cr23Mn35Co34__s26_site1", "OH__atomic"),
    "Fe25Co25Ni25Cr25__s13_site0__slab__atomic_ndim16": (RERUN, "Fe25Co25Ni25Cr25__s13_site0", "slab__atomic_ndim16"),
    "Fe25Co25Ni25Cr25__s25_site2__OOH__atomic": (RERUN, "Fe25Co25Ni25Cr25__s25_site2", "OOH__atomic"),
    "Fe25Co25Ni25Cr25__s25_site2__slab__atomic": (PROD, "Fe25Co25Ni25Cr25__s25_site2", "slab__atomic"),
}
TARGETS = {
    "Cu8Cr23Mn35Co34__s16_site2": ("slab", "OH", "OOH"),
    "Cu8Cr23Mn35Co34__s26_site1": ("slab", "O", "OOH"),
    "Fe25Co25Ni25Cr25__s13_site0": ("OH", "O", "OOH"),
    "Fe25Co25Ni25Cr25__s25_site2": ("OH", "O"),
}
SAVE_FILES = ("charge-density.hdf5", "data-file-schema.xml", "occup.txt", "paw.txt")
FETCH = ("occup.txt", "paw.txt")


def save_dir(root, site, job):
    return f"{root}/{site}/tmp_{job}/{job}.save"


client = paramiko.SSHClient()
client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
client.set_missing_host_key_policy(paramiko.RejectPolicy())
client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
               allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "seeds": {}, "references": {}}
try:
    sftp = client.open_sftp()
    for seed_id, (root, site, job) in SEEDS.items():
        remote = save_dir(root, site, job)
        _, out, err = client.exec_command("cd " + remote + " && sha256sum " + " ".join(SAVE_FILES), timeout=300)
        text, rc = out.read().decode(), out.channel.recv_exit_status()
        if rc:
            raise SystemExit("sha256sum failed for " + remote + ": " + err.read().decode())
        shas = {line.split()[1]: line.split()[0] for line in text.splitlines() if line.strip()}
        local = HERE / "seed_files" / seed_id
        local.mkdir(parents=True, exist_ok=False)
        for name in FETCH:
            sftp.get(remote + "/" + name, str(local / name))
            if hashlib.sha256((local / name).read_bytes()).hexdigest() != shas[name]:
                raise SystemExit("download mismatch: " + seed_id + "/" + name)
        receipt["seeds"][seed_id] = {"save_dir": remote, "sha256": shas}
    for site, states in TARGETS.items():
        for state in states:
            job = state + "__atomic_ndim16"
            remote = save_dir(RERUN, site, job)
            local = HERE / "reference_files" / (site + "__" + job)
            local.mkdir(parents=True, exist_ok=False)
            row = {"save_dir": remote, "sha256": {}, "missing": []}
            for name in FETCH:
                try:
                    sftp.stat(remote + "/" + name)
                except FileNotFoundError:
                    row["missing"].append(name)  # a stopped attempt need not leave a save
                    continue
                sftp.get(remote + "/" + name, str(local / name))
                row["sha256"][name] = hashlib.sha256((local / name).read_bytes()).hexdigest()
            receipt["references"][site + "__" + job] = row
finally:
    client.close()
with (HERE / "seed_fetch.json").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps(receipt, indent=2) + "\n")
print("seeds", len(receipt["seeds"]), "references", len(receipt["references"]), flush=True)
