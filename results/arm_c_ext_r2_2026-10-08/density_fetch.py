"""Read-only fetch of the inputs for the round-2 density move (no writes on Anvil).

Downloads into density_inputs/ (local only, never committed; sizes and sha256 recorded in density_fetch.json):
- each seed save's charge-density.hdf5 and data-file-schema.xml, checked against the r1 pins (seed_fetch.json);
- the converged saves used to test the move offline: Cu8Cr23Mn35Co34 s20/2, all four states (production).
  Fe25Co25Ni25Cr25 s25/2 slab and OOH are seeds already;
- the UPF file of every species in the target and seed decks.
"""
import datetime as dt
import hashlib
import json
import re
import time
from pathlib import Path

import paramiko

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R1 = ROOT / "results/arm_c_ext_2026-10-08"
OUT = HERE / "density_inputs"
PROJECT = "/anvil/projects/x-che260157"
PRODUCTION = PROJECT + "/sts_arm_c_2026-10-07/runs/hea/arm_c_2026-10-07"
VALIDATION_SITE = "Cu8Cr23Mn35Co34__s20_site2"
FILES = ("charge-density.hdf5", "data-file-schema.xml")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sources():
    """(local id, remote save dir, pinned sha256 or None) for every density to fetch."""
    seeds = json.loads((R1 / "seed_fetch.json").read_text(encoding="utf-8"))["seeds"]
    rows = [(key, value["save_dir"], value["sha256"]) for key, value in sorted(seeds.items())]
    for state in ("slab", "OH", "O", "OOH"):
        job = state + "__atomic"
        rows.append((f"{VALIDATION_SITE}__{job}", f"{PRODUCTION}/{VALIDATION_SITE}/tmp_{job}/{job}.save", None))
    return rows


def pseudopotentials():
    decks = sorted((ROOT / "runs/hea/arm_c_2026-10-07").rglob("*.in"))
    names = set()
    for deck in decks:
        text = deck.read_text()
        block = text.split("ATOMIC_SPECIES", 1)[1].split("\n\n", 1)[0].split("CELL_PARAMETERS", 1)[0]
        names.update(m.group(1) for m in re.finditer(r"^\s*\w+\s+[0-9.]+\s+(\S+\.(?:UPF|upf))\s*$", block, re.M))
    return sorted(names)


def main():
    rows = sources()
    upfs = pseudopotentials()
    remote = [f"{save}/{name}" for _, save, _ in rows for name in FILES] + [f"{PROJECT}/pseudo/{n}" for n in upfs]
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
    receipt = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "readonly": True, "densities": {}, "pseudopotentials": {}}
    try:
        _, stdout, stderr = client.exec_command("sha256sum " + " ".join(remote), timeout=600)
        listing, err = stdout.read().decode(), stderr.read().decode()
        if stdout.channel.recv_exit_status():
            raise SystemExit("remote sha256sum failed: " + err)
        remote_sha = {line.split()[1]: line.split()[0] for line in listing.splitlines()}
        sftp = client.open_sftp()

        def fetch(path, target, pinned=None):
            target.parent.mkdir(parents=True, exist_ok=True)
            start = time.time()
            sftp.get(path, str(target))
            seconds = time.time() - start
            local = sha256(target)
            if local != remote_sha[path] or (pinned is not None and local != pinned):
                raise SystemExit(f"sha256 mismatch for {path}")
            return {"remote": path, "bytes": target.stat().st_size, "sha256": local, "seconds": round(seconds, 1)}

        for name in upfs:
            receipt["pseudopotentials"][name] = fetch(f"{PROJECT}/pseudo/{name}", OUT / "pseudo" / name)
        print("pseudopotentials", len(upfs), flush=True)
        for key, save, pins in rows:
            receipt["densities"][key] = {
                name: fetch(f"{save}/{name}", OUT / key / name, pins[name] if pins else None) for name in FILES}
            print(key, {n: v["seconds"] for n, v in receipt["densities"][key].items()}, flush=True)
    finally:
        client.close()
    with (HERE / "density_fetch.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    print("fetched", len(receipt["densities"]), "densities,", len(receipt["pseudopotentials"]), "pseudopotentials", flush=True)


if __name__ == "__main__":
    main()
