"""Stage the exact published checkpoint into a NEW isolated Anvil checkout and run PREFLIGHT there.

PREPARED, NOT RUN.  Writing to Anvil needs Frank's separate go.  The script clones into
/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04 (which must not exist), checks out the
published commit sparsely, verifies every staged blob byte-for-byte, runs `bash -n` on the wrapper and the
controller's own PREFLIGHT (which now replays the real control call through the staged adapter), and reads
`mybalance`, `squeue`, `scontrol show partition` and `myquota`.  It submits nothing and starts no QE.

Input: publication_final.json in this directory, written by publish_reviewed_package.py after the independent
review and the offline verification.  Output: remote_stage.json here and remote_stage_receipt.json on Anvil.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

PHASE = pathlib.Path(__file__).resolve().parent
ROOT = PHASE.parents[1]
PHASE_REL = 'results/pa_catalyst_retest_2026-10-04'
SPEC_REL = PHASE_REL + '/launch_spec.json'
REMOTE_BASE = '/anvil/projects/x-che260157'
REMOTE_NAME = 'sts_pa_catalyst_retest_2026-10-04'
SSH = ['C:/Program Files/Git/usr/bin/ssh.exe', '-i', 'C:/Users/frank/.ssh/id_ed25519', '-o', 'BatchMode=yes',
       '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=12', 'x-fcai3@anvil.rcac.purdue.edu']
REMOTE_PYTHON = '/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'
EXTRA_PATHS = ['.gitattributes', 'src/dft/pa_checked_contract.py',
               'runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in']

REMOTE_BODY = r'''
import hashlib, json, os, pathlib, subprocess, sys
base = pathlib.Path(base_dir); root = base / remote_name
assert root.parent.resolve() == base.resolve() and root.name == remote_name
assert not root.exists() and not root.is_symlink(), 'no existing checkout or output may be overwritten'
r = {'successful': False, 'commit': commit, 'commands': {}, 'pins': [], 'new_jobs_submitted': 0, 'qe_executed': False,
     'production_accepted': False}
env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
def run(name, args, timeout=60, input=None):
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env,
                       timeout=timeout, input=input)
    r['commands'][name] = {'args': args, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    assert p.returncode == 0, (name, p.stderr)
    return p.stdout
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()
try:
    run('clone', ['git', '-c', 'credential.interactive=never', 'clone', '--filter=blob:none', '--no-checkout', '--single-branch',
                  '--branch', 'r0-catalysis-revival', 'https://github.com/fronkt/sts-electrocatalyst.git', str(root)], timeout=140)
    run('sparse', ['git', '-C', str(root), 'sparse-checkout', 'set', '--no-cone', '--stdin'],
        input='\n'.join('/' + p for p in sorted(pins)) + '\n')
    run('checkout', ['git', '-C', str(root), 'checkout', '--detach', commit], timeout=90)
    assert run('head', ['git', '-C', str(root), 'rev-parse', 'HEAD']).strip() == commit
    for rel, pin in pins.items():
        path = root / rel
        assert path.is_file() and not path.is_symlink() and path.stat().st_nlink == 1, rel
        assert path.stat().st_size == pin['bytes'] and digest(path) == pin['sha256'], 'staged byte mismatch: ' + rel
        r['pins'].append(dict(path=rel, **pin))
    spec = root / spec_rel
    assert digest(spec) == spec_sha256, 'staged spec differs from the reviewed spec'
    run('wrapper_syntax', ['bash', '-n', str(root / 'anvil/90_pa_catalyst_retest.slurm')])
    run('preflight', [sys.executable, str(root / 'src/dft/pa_catalyst_retest.py'), '--spec', str(spec), '--spec-sha256', spec_sha256,
                      '--preflight'], timeout=120)
    preflight = json.loads(r['commands']['preflight']['stdout'])
    assert preflight['status'] == 'PREFLIGHT_PASS' and preflight['real_control_replay']['replayed'] is True
    r['preflight_real_control_replay'] = preflight['real_control_replay']
    run('balance', ['bash', '-lc', 'mybalance'], timeout=20)
    run('queue', ['squeue', '-h', '-u', 'x-fcai3', '-o', '%i|%T|%j|%C|%R'])
    run('partition', ['scontrol', 'show', 'partition', 'wholenode', '-o'])
    run('quota', ['bash', '-lc', 'myquota'], timeout=20)
    assert not r['commands']['queue']['stdout'].strip(), 'existing job requires a scoped queue check before submission'
    assert not (root / 'trial_results').exists()
    assert not list(root.glob('pa_replay_*')), 'PREFLIGHT replay scratch must be gone'
    r['successful'] = True
except BaseException as exc:
    r['error'] = repr(exc)
    raise
finally:
    if root.is_dir():
        (root / 'remote_stage_receipt.json').write_text(json.dumps(r, indent=2) + '\n')
    print(json.dumps(r, indent=2))
'''


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def build(published):
    """Return (remote program text, pins) from a successful publication receipt; touches nothing."""
    assert published['successful'] and published['commit'] == published['remote_commit']
    pins = dict(published['staged_blob_pins'], **published['additional_blob_pins'])
    for rel in EXTRA_PATHS:
        assert rel in pins, 'stage pin missing: ' + rel
    spec_sha256 = published['local_pins'][SPEC_REL]
    header = ('commit=%r\npins=%r\nbase_dir=%r\nremote_name=%r\nspec_rel=%r\nspec_sha256=%r\n'
              % (published['commit'], pins, REMOTE_BASE, REMOTE_NAME, SPEC_REL, spec_sha256))
    compile(header + REMOTE_BODY, '<retest-stage>', 'exec')
    return header + REMOTE_BODY, pins


def main():
    target = PHASE / 'remote_stage.json'
    assert not target.exists(), 'a stage receipt already exists; retain it'
    published = json.loads((PHASE / 'publication_final.json').read_text(encoding='utf-8'))
    program, pins = build(published)
    for rel, pin in published['local_pins'].items():
        assert digest(ROOT / rel) == pin, 'local byte drift since publication: ' + rel
    print('Stage exact published checkpoint', published['commit'], 'without QE or job calls', flush=True)
    p = subprocess.run(SSH + [REMOTE_PYTHON], input=program, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=420, creationflags=0x08000000)
    result = {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr, 'published_commit': published['commit'],
              'read_only_historical_sources': True, 'new_jobs_submitted': 0, 'qe_executed': False}
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Remote stage returncode', p.returncode, flush=True)
    if p.returncode:
        print(p.stderr[-5000:], flush=True)
    assert p.returncode == 0 and json.loads(p.stdout)['successful']


if __name__ == '__main__':
    sys.exit(main())
