"""Read-only scheduler snapshot of the arrays the prepared manifests are sequenced after.

Runs one sacct query over ssh with BatchMode (no job is submitted, cancelled or modified) and
records the command, raw output and UTC time. For every task that has left the queue (any state
other than PENDING / RUNNING) it maps the task to its deck through the approved launch
specification (stage = JobName without the 'research-' prefix, row = array task id) and reads,
read-only, that deck's .KILLED / .REJECTED sidecars and .qc.json receipt plus the per-SCF
'convergence has been achieved' lines of its output. Usage:
  python src/s2/lowtail_dft/lt_anvil_snapshot.py [--out results/lowtail_dft_2026-09-16/anvil_queue_snapshot_r2.json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lt_common import ROOT, evidence, read_json, write_json  # noqa: E402

HOST = "x-fcai3@anvil.rcac.purdue.edu"
ARRAYS = ("20781971", "20781972")
FIELDS = ("job", "name", "state", "exit_code", "elapsed_s", "cpus", "start", "end")
REMOTE = ("TZ=UTC sacct -j " + ",".join(ARRAYS) +
          " --allocations --parsable2 --noheader --format=JobID,JobName%40,State,ExitCode,ElapsedRaw,AllocCPUS,Start,End; date -u")
LAUNCH_SPEC = ROOT / "results/research_launch_2026-09-16/launch_spec.json"
SUBMISSION = ROOT / "results/research_launch_2026-09-16/submission.json"


def ssh(command: str, timeout: int = 90) -> dict:
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", HOST, command]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return dict(command=" ".join(cmd[:-1]) + " " + shlex.quote(command), rc=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    except (OSError, subprocess.TimeoutExpired) as error:
        return dict(command=" ".join(cmd[:-1]) + " " + shlex.quote(command), rc=None, stdout="", stderr=str(error))


def remote_root() -> str:
    """Project root on Anvil, read from the recorded submission of the research batch script."""
    text = SUBMISSION.read_text(encoding="utf-8")
    roots = set(re.findall(r"Command=(\S+)/anvil/72_research_batch\.slurm", text))
    if len(roots) != 1:
        raise ValueError(f"expected one remote root in {SUBMISSION}, found {sorted(roots)}")
    return roots.pop()


def terminal_task_command(rows: list, spec: dict, root: str) -> tuple[str, list]:
    parts, tasks = [], []
    for r in rows:
        if r["state"] in ("PENDING", "RUNNING") or "_" not in r["job"] or not r["name"].startswith("research-"):
            continue
        stage, task = r["name"][len("research-"):], r["job"].split("_", 1)[1]
        if stage not in spec["stages"] or not task.isdigit():
            continue
        job = spec["stages"][stage]["jobs"][int(task) - 1]
        base = f"{root}/runs/{job['dir']}/{job['job']}"
        tasks.append(dict(task=r["job"], stage=stage, row=int(task), dir=job["dir"], deck=job["job"], input_sha256=job["sha256"],
                          scf_seconds=job.get("scf_seconds"), max_iterations=job.get("max_iterations"), remote_base=base))
        q = shlex.quote
        parts.append(f"echo '=== {r['job']}'; for x in .KILLED .REJECTED .qc.json; do [ -f {q(base)}$x ] && "
                     f"{{ echo \"--- $x\"; cat {q(base)}$x; echo; }}; done; "
                     f"[ -f {q(base + '.out')} ] && {{ echo '--- scf'; grep -n 'convergence has been achieved\\|convergence NOT achieved\\|IEEE_INVALID' "
                     f"{q(base + '.out')} | head -20; }}")
    return "; ".join(parts), tasks


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "results/lowtail_dft_2026-09-16/anvil_queue_snapshot_r2.json")
    args = ap.parse_args(argv)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    rec = ssh(REMOTE)
    rows = [dict(zip(FIELDS, line.split("|"))) for line in rec["stdout"].splitlines() if line.startswith(ARRAYS)]
    rows = [r for r in rows if len(r) == len(FIELDS)]
    spec = read_json(LAUNCH_SPEC)
    command, tasks = terminal_task_command(rows, spec, remote_root())
    detail = ssh(command) if command else None
    write_json(args.out, dict(schema="lowtail-anvil-queue-snapshot-v2", read_only=True, requested_at_utc=started, arrays=list(ARRAYS),
                              sacct=rec, rows=rows, terminal_tasks=tasks, terminal_task_files=detail,
                              launch_spec=evidence(LAUNCH_SPEC), submission=evidence(SUBMISSION)))
    print("\n".join("|".join(r.values()) for r in rows) or rec["stderr"])
    if detail:
        print(detail["stdout"])
    return 0 if rec["rc"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
