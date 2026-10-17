"""Download B1 stage-1 artifacts from Anvil (read-only there): each job's .out, .qc.json, .run.in, .projwfc.in,
.projwfc.out and any .KILLED/.REJECTED marker, plus the array logs. Local copies are created, never overwritten.

Usage: python results/b1_relaxed_projector_2026-10-16/collect.py
"""
import json
import posixpath
import stat
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "results/b1_relaxed_projector_2026-10-16"
SPEC = json.loads((HERE / "launch_spec.json").read_text(encoding="utf-8"))
REMOTE = "/anvil/projects/x-che260157/sts_b1_relaxed_projector_2026-10-16"
SUFFIXES = (".out", ".qc.json", ".run.in", ".projwfc.in", ".projwfc.out", ".KILLED", ".REJECTED")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    client = paramiko.SSHClient()
    client.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
                   allow_agent=False, look_for_keys=False, timeout=30, banner_timeout=30, auth_timeout=30)
    sftp = client.open_sftp()
    got, summary = [], {}
    try:
        for job in SPEC["stages"]["b1_relax"]["jobs"]:
            rdir = posixpath.join(REMOTE, "runs", job["dir"])
            ldir = ROOT / "runs" / job["dir"]
            for suffix in SUFFIXES:
                remote = posixpath.join(rdir, job["job"] + suffix)
                try:
                    sftp.stat(remote)
                except FileNotFoundError:
                    continue
                local = ldir / (job["job"] + suffix)
                if local.exists():
                    continue
                sftp.get(remote, str(local))
                got.append(local.relative_to(ROOT).as_posix())
            qc = ldir / (job["job"] + ".qc.json")
            summary[job["job"]] = json.loads(qc.read_text(encoding="utf-8")) if qc.exists() else None
        logs = ROOT / "results/b1_relaxed_projector_2026-10-16/logs"
        logs.mkdir(exist_ok=True)
        for entry in sftp.listdir_attr(posixpath.join(REMOTE, "logs")):
            if stat.S_ISREG(entry.st_mode) and not (logs / entry.filename).exists():
                sftp.get(posixpath.join(REMOTE, "logs", entry.filename), str(logs / entry.filename))
                got.append("results/b1_relaxed_projector_2026-10-16/logs/" + entry.filename)
    finally:
        client.close()
    print(f"downloaded {len(got)} files")
    for name, rec in summary.items():
        if rec is None:
            print(f"{name}: no receipt")
            continue
        relax = rec.get("relaxation") or {}
        print(f"{name}: {rec['status']}"
              + (f" ({rec.get('reason')})" if rec.get("reason") else "")
              + (f"; steps {relax.get('ionic_steps')}, max SCF it {relax.get('maximum_scf_iteration')}, "
                 f"E {relax.get('final_energy_Ry')} Ry, wall {rec.get('scf_process', {}).get('wall_seconds', 0):.0f} s"
                 if relax else ""))


if __name__ == "__main__":
    main()
