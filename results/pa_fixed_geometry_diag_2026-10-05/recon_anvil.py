"""Read-only Anvil reconnaissance before the fixed-geometry diagnostic (no writes, no jobs)."""
import json, shlex
from pathlib import Path
import paramiko

OUT = Path("results/pa_fixed_geometry_diag_2026-10-05/recon_anvil.json")
P = "/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04"
cmds = {
    "mybalance": "mybalance",
    "squeue": "squeue -u x-fcai3 -o '%i|%j|%T|%M|%l|%D|%C'",
    "trial_results_ls": f"ls -la {P}/trial_results {P}/trial_results/candidate_immutable {P}/trial_results/candidate_immutable/outdir | head -40",
    "immutable_save": f"ls -la {P}/trial_results/candidate_immutable/outdir/slab_c5low__pa_boundary.save | head -20; du -sh {P}/trial_results/candidate_immutable",
    "immutable_wfc_count": f"ls {P}/trial_results/candidate_immutable/outdir | sed 's/[0-9]*$//' | sort | uniq -c",
    "restart_scf": f"cat {P}/trial_results/candidate_immutable/outdir/slab_c5low__pa_boundary.restart_scf 2>&1 | head -2 | cut -c1-200",
    "quota": "myquota 2>&1 | head -20",
    "src_ls": f"ls -la {P}/src/dft {P}/anvil | head -30",
    "git_head": f"cd {P} && (git rev-parse HEAD 2>&1; git status --short 2>&1 | head -5)",
    "free_gb_project": "df -h /anvil/projects/x-che260157 | tail -1",
}
c = paramiko.SSHClient()
c.load_host_keys(str(Path.home() / ".ssh/known_hosts"))
c.set_missing_host_key_policy(paramiko.RejectPolicy())
c.connect("anvil.rcac.purdue.edu", username="x-fcai3", key_filename=str(Path.home() / ".ssh/id_ed25519"),
          allow_agent=False, look_for_keys=False, timeout=20, banner_timeout=20, auth_timeout=20)
res = {}
for k, cmd in cmds.items():
    _, o, e = c.exec_command(cmd, timeout=120)
    res[k] = {"cmd": cmd, "stdout": o.read().decode(), "stderr": e.read().decode(), "rc": o.channel.recv_exit_status()}
c.close()
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print("ok")
