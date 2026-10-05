"""Read-only proof that the held job has exactly the approved shape.  PREPARED, NOT RUN.

Slurm shows the pending one-node bound as `1-1`, not `1` (the first trial's inspection failed on exactly that and
retained the failure); both spellings are accepted here, with the requested TRES, time, requeue and dependency
fields checked in full.  Only `scontrol show job` runs on Anvil.
"""
import json
import pathlib
import subprocess
import sys

PHASE = pathlib.Path(__file__).resolve().parent
PHASE_REL = 'results/pa_catalyst_retest_2026-10-04'
REMOTE_ROOT = '/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04'
SSH = ['C:/Program Files/Git/usr/bin/ssh.exe', '-i', 'C:/Users/frank/.ssh/id_ed25519', '-o', 'BatchMode=yes',
       '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=12', 'x-fcai3@anvil.rcac.purdue.edu']
REMOTE_PYTHON = '/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'

REMOTE_BODY = r'''
import json, pathlib, re, subprocess
root = pathlib.Path(remote_root); phase = root / phase_rel
original = json.loads((phase / 'submission_remote.json').read_text())
assert original['job_id'] == job and original['successful'] and original['held']
p = subprocess.run(['scontrol', 'show', 'job', job, '-o'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=20)
assert p.returncode == 0
f = dict(re.findall(r'(?:^|\s)([^\s=]+)=([^\s]+)', p.stdout))
expected = {'JobId': job, 'JobState': 'PENDING', 'Reason': 'JobHeldUser', 'Account': 'che260157', 'Partition': 'wholenode',
            'JobName': 'pa-catalyst-retest', 'NumCPUs': '128', 'NumTasks': '128', 'CPUs/Task': '1', 'TimeLimit': '16:00:00',
            'Requeue': '0', 'Restarts': '0', 'BatchFlag': '1', 'Dependency': '(null)', 'Exclusive': 'NODE', 'OverSubscribe': 'NO'}
assert all(f.get(k) == v for k, v in expected.items()), {k: f.get(k) for k in expected}
assert not any(k.startswith('Array') for k in f)
assert f['NumNodes'] in {'1', '1-1'}, 'pending node bounds must both equal 1'
assert dict(piece.split('=', 1) for piece in f['ReqTRES'].split(',')) == {'cpu': '128', 'mem': '200G', 'node': '1', 'billing': '128'}
assert f['Command'] == str(root / 'anvil/90_pa_catalyst_retest.slurm') and f['WorkDir'] == str(root)
r = {'successful': True, 'job_id': job, 'held_shape_validated': True, 'raw_scontrol': p.stdout, 'pending_num_nodes_raw': f['NumNodes'],
     'max_cpu_su': 2048, 'new_jobs_submitted': 0, 'qe_executed': False, 'production_accepted': False}
(phase / 'held_validation_checked_remote.json').write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(r, indent=2))
'''


def build(job):
    assert job.isdigit()
    header = 'job=%r\nremote_root=%r\nphase_rel=%r\n' % (job, REMOTE_ROOT, PHASE_REL)
    compile(header + REMOTE_BODY, '<retest-held-validation>', 'exec')
    return header + REMOTE_BODY


def main():
    target = PHASE / 'held_validation_checked.json'
    assert not target.exists()
    submitted = json.loads((PHASE / 'submission.json').read_text(encoding='utf-8'))
    job = submitted['job_id']
    p = subprocess.run(SSH + [REMOTE_PYTHON], input=build(job), capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=40, creationflags=0x08000000)
    result = {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr, 'job_id': job, 'new_jobs_submitted': 0, 'qe_executed': False}
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Held singleton validation returncode', p.returncode, 'job', job)
    assert p.returncode == 0 and json.loads(p.stdout)['successful']


if __name__ == '__main__':
    sys.exit(main())
