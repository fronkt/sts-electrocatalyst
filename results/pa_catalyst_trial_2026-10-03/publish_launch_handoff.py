"""Retain launch-only metadata and publish exact paths; never run or retry QE."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[1]
BACKGROUND = Path('C:/Users/frank/AppData/Local/Temp/sts-background-2026-09-06')
TARGET = PHASE / 'launch_handoff_publication.json'
assert not TARGET.exists(), 'retain previous publication; no automatic repeat'
ENV = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never',
           GCM_GUI_PROMPT='0')
REPORT = {'successful': False, 'commands': [], 'job_id': '21034683',
          'scope': 'LAUNCH_METADATA_ONLY', 'new_jobs_submitted': 0,
          'qe_executed_by_this_helper': False, 'automatic_retry': False,
          'production_accepted': False}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def git(*args, timeout=45, binary=False):
    command = ['git', '-c', 'credential.interactive=never', *args]
    p = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True,
                       timeout=timeout, creationflags=0x08000000)
    row = {'args': command, 'returncode': p.returncode}
    if not binary:
        row.update(stdout=p.stdout.decode('utf-8', 'replace'),
                   stderr=p.stderr.decode('utf-8', 'replace'))
    REPORT['commands'].append(row)
    assert p.returncode == 0, (command, row.get('stderr'))
    return p.stdout if binary else p.stdout.decode('utf-8').strip()


try:
    spec = importlib.util.spec_from_file_location(
        'launch_only_preservation', PHASE / 'verify_trial_offline.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    REPORT['before'] = verifier.preserve()
    checked = json.loads((PHASE / 'offline_checked.json').read_text())
    assert checked['successful']
    for rel, pin in checked['code_pins'].items():
        assert digest(ROOT / rel) == pin, 'frozen implementation drift: ' + rel
    assert digest(PHASE / 'independent_launch_review_final.md') == (
        '0d8c4e0ea2eb4775fe5bf233326f8d5c86c765bb133ce1163cb9c2c49761d587')
    assert git('rev-parse', 'HEAD') == 'b9f0208ee6f3cd71d0201d03b964b5c23f53d644'
    assert git('branch', '--show-current') == 'r0-catalysis-revival'
    assert not git('diff', '--cached', '--name-only'), 'preserve other staged work'

    published = json.loads((PHASE / 'publication_final.json').read_text())
    assert published['successful'] and published['commit'] == published['remote_commit']
    assert published['commit'] == 'b9f0208ee6f3cd71d0201d03b964b5c23f53d644'
    submission = json.loads((PHASE / 'submission.json').read_text())
    validation = json.loads((PHASE / 'held_validation_checked.json').read_text())
    release = json.loads((PHASE / 'release.json').read_text())
    assert submission['job_id'] == validation['job_id'] == release['job_id'] == '21034683'
    assert validation['returncode'] == release['returncode'] == 0
    assert json.loads(validation['stdout'])['held_shape_validated']
    assert json.loads(release['stdout'])['released']
    watcher_log = (BACKGROUND / 'pa-catalyst-watch-2026-10-03.log').read_bytes()
    assert watcher_log.startswith(b'Verified background desktop: Codex_STS_Background')
    observation_lines = (PHASE / 'trial_observations.jsonl').read_bytes().splitlines()
    complete_rows = []
    for line in observation_lines:
        try:
            complete_rows.append(json.loads(line))
        except (ValueError, UnicodeError):
            pass  # A concurrently appended incomplete row is not evidence.
    assert complete_rows and complete_rows[-1]['returncode'] == 0
    latest = complete_rows[-1]
    observed = json.loads(latest['stdout'])
    assert observed['job_id'] == '21034683' and observed['readonly']
    snapshot = PHASE / 'launch_handoff_snapshot.json'
    assert not snapshot.exists(), 'immutable launch snapshot already exists'
    snapshot.write_text(json.dumps({
        'snapshot_utc': datetime.now(timezone.utc).isoformat(),
        'job_id': '21034683', 'implementation_commit': published['commit'],
        'watcher_desktop_verified': True, 'latest_complete_observation': latest,
        'final_scientific_outcome_pending': True, 'final_cpu_su_pending': True,
        'compute_cpu_su_ceiling': 2048, 'literature_estimate_usd': 1.1105254,
        'literature_ceiling_usd': 50, 'new_paid_literature_calls': 0,
        'production_accepted': False, 'no_retry_authorized': True,
        'frozen_code_pins': checked['code_pins'], 'preserved': REPORT['before'],
    }, indent=2) + '\n', encoding='utf-8')

    helper_names = [
        'pa-catalyst-remote-stage-2026-10-03.py',
        'pa-catalyst-held-validation-2026-10-03.py',
        'pa-catalyst-release-2026-10-03.py',
        'pa-catalyst-watch-2026-10-03.json',
    ]
    for name in helper_names:
        source, destination = BACKGROUND / name, PHASE / name
        assert source.is_file() and not destination.exists()
        destination.write_bytes(source.read_bytes())
        assert digest(destination) == digest(source)

    files = ['publication_final.json', 'remote_stage.json', 'submission_intent.json',
             'submission.json', 'held_validation_checked.json', 'release.json',
             'launch_handoff_snapshot.json', 'publish_launch_handoff.py', *helper_names]
    paths = sorted(['results/pa_catalyst_trial_2026-10-03/' + p for p in files] + [
        'docs/research/pa-catalyst-trial-2026-10-03.md', 'tasks/todo.md'])
    REPORT['paths'] = paths
    assert set(git('diff', '--name-only').splitlines()) == {
        'docs/research/pa-catalyst-trial-2026-10-03.md', 'tasks/todo.md'}, 'unrelated edits'
    git('add', '-f', '--', *paths)
    assert set(git('diff', '--cached', '--name-only').splitlines()) == set(paths)
    git('-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol',
        'diff', '--cached', '--check')
    REPORT['local_pins'] = {rel: digest(ROOT / rel) for rel in paths}
    REPORT['staged_blob_pins'] = {}
    for rel in paths:
        blob, data = git('show', ':' + rel, binary=True), (ROOT / rel).read_bytes()
        if rel.startswith('results/pa_catalyst_trial_2026-10-03/'):
            assert blob == data, 'receipt byte transformation: ' + rel
        else:
            assert blob in (data, data.replace(b'\r\n', b'\n')), 'unexpected Git transformation'
        REPORT['staged_blob_pins'][rel] = {
            'sha256': hashlib.sha256(blob).hexdigest(), 'bytes': len(blob)}
    git('commit', '-m', 'Record approved singleton catalyst trial launch and read-only watch', timeout=90)
    REPORT['commit'] = git('rev-parse', 'HEAD')
    git('push', 'origin', 'r0-catalysis-revival', timeout=180)
    remote = git('ls-remote', 'origin', 'refs/heads/r0-catalysis-revival', timeout=90).split()[0]
    assert remote == REPORT['commit'], 'remote SHA mismatch'
    REPORT['remote_commit'] = remote
    assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
    REPORT['after'] = verifier.preserve()
    for rel, pin in REPORT['local_pins'].items():
        assert digest(ROOT / rel) == pin, 'postpublication byte drift: ' + rel
    for rel, pin in checked['code_pins'].items():
        assert digest(ROOT / rel) == pin, 'frozen implementation drift after handoff: ' + rel
    REPORT['successful'] = True
except BaseException as exc:
    REPORT['error'] = repr(exc)
    raise
finally:
    TARGET.write_text(json.dumps(REPORT, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: REPORT[k] for k in ['successful', 'commit', 'remote_commit',
      'job_id', 'after', 'new_jobs_submitted', 'production_accepted']}, indent=2), flush=True)
