#!/bin/bash
# Scheduler-only continuation, dependent on successful array 20781967.
# The submitter independently requires all three complete, hash-verified QC receipts.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem=1G
#SBATCH -t 00:10:00
#SBATCH -J research-beef-release
#SBATCH -o logs/beef_release_%j.out
#SBATCH -e logs/beef_release_%j.out
set -euo pipefail
export PROJECT=/anvil/projects/x-che260157
cd "$PROJECT"
ROOT="$PROJECT/sts"
check_hash() { [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ] || { echo "REFUSE: hash $1"; exit 2; }; }
check_hash "$ROOT/anvil/73_submit_research_batch.sh" ccad03da0ba53a465b1fee7bcfda93dc4efae71e388aca99881c5dd17447bb0b
check_hash "$ROOT/anvil/72_research_batch.slurm" 41e85fe029bdcc122a4c1f5e6f024745f4d15a95b21d49ce887d9dc163fa6331
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
exec "$PYTHON" - <<'PY'
import datetime, json, pathlib, re, subprocess
root = pathlib.Path('/anvil/projects/x-che260157/sts')
result = root / 'results/research_launch_2026-09-16'
# Atomic lock prevents a second submission even if this gate is invoked twice.
(result / 'beef_release.lock').mkdir()
record = {'at': datetime.datetime.utcnow().isoformat() + 'Z', 'released': False}
def save():
    (result / 'beef_continuation.json').write_text(json.dumps(record, indent=2) + '\n')
def command(args):
    r = subprocess.run(args, capture_output=True, text=True, timeout=120)
    if r.returncode:
        raise RuntimeError(repr(args) + '\n' + r.stdout + '\n' + r.stderr)
    return r.stdout
try:
    output = command(['bash', str(root / 'anvil/73_submit_research_batch.sh'), 'beef_remaining'])
    record['submission_output'] = output
    found = re.findall(r'(?m)^(\d+)(?:;[A-Za-z0-9_.-]+)?$', output)
    if len(found) != 1:
        raise ValueError('Expected one held array ID')
    job = found[0]; record['job_id'] = job; save()
    description = command(['scontrol', 'show', 'job', '-o', job])
    record['held_description'] = description
    for expected in ['JobState=PENDING', 'Reason=JobHeldUser', 'NumCPUs=128', 'NumTasks=128',
                     'Requeue=0', 'MinMemoryNode=237G', 'Account=che260157',
                     'Partition=shared', 'TimeLimit=01:00:00', 'ArrayTaskThrottle=2']:
        if expected not in description:
            raise ValueError('Held resources differ: ' + expected)
    tasks = command(['squeue', '-h', '-r', '-j', job, '-o', '%i|%T|%C|%l|%R'])
    record['held_tasks'] = tasks
    rows = tasks.strip().splitlines()
    if len(rows) != 11 or any('|PENDING|128|' not in row or 'JobHeldUser' not in row for row in rows):
        raise ValueError('Expected eleven held 128-core tasks')
    command(['scontrol', 'release', job]); record['released'] = True; save()
    print('BEEF_REMAINING_RELEASED ' + job, flush=True)
except BaseException as error:
    record['error'] = repr(error); save()
    raise
PY
