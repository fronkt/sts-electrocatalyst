"""Publish the exact reviewed operational roadmap without running research jobs."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/sts_roadmap_2026-10-05'
GIT = 'C:/Program Files/Git/cmd/git.exe'
BRANCH = 'r0-catalysis-revival'
EXPECTED_HEAD = 'e0e304f6069c8df3603fc12e374db484ab3f0bd7'
ROADMAP = 'docs/research/sts-roadmap-2026-10-05.md'
BASE = 'results/sts_roadmap_2026-10-05/'
PATHS = [
    'tasks/todo.md', ROADMAP,
    BASE + 'status_snapshot.json', BASE + 'roadmap_basis.json',
    BASE + 'official_dates.json', BASE + 'roadmap_independent_review.md',
    BASE + 'roadmap_independent_review.json', BASE + 'bank_roadmap.py',
]
ENV = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never', GCM_GUI_PROMPT='0')

def git(*args):
    r = subprocess.run([GIT, '-c', 'credential.interactive=never', *args],
                       cwd=ROOT, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=0x08000000, timeout=180)
    if r.returncode:
        raise RuntimeError('git ' + ' '.join(args) + ': ' + r.stderr.decode('utf-8', 'replace'))
    return r.stdout

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(data):
    return set(data.decode('utf-8').splitlines())

assert git('branch', '--show-current').decode().strip() == BRANCH
assert git('rev-parse', 'HEAD').decode().strip() == EXPECTED_HEAD
assert not git('diff', '--cached', '--name-only').strip(), 'Index already contains other work'
assert names(git('diff', '--name-only')) <= {'tasks/todo.md'}, 'Other tracked edits exist'
review = json.loads((OUT / 'roadmap_independent_review.json').read_text(encoding='utf-8'))
basis = json.loads((OUT / 'roadmap_basis.json').read_text(encoding='utf-8'))
assert review['decision'] == 'GO_OPERATIONAL_ROADMAP_ONLY' and review['blocking_findings'] == []
assert review['new_compute_authorized'] is False and review['physical_sample_preparation_authorized'] is False
assert review['current_scientific_trial_complete'] is False
for relative, key in [
    (ROADMAP, 'roadmap_sha256'),
    (BASE + 'status_snapshot.json', 'status_snapshot_sha256'),
    (BASE + 'roadmap_basis.json', 'roadmap_basis_sha256'),
    (BASE + 'official_dates.json', 'official_dates_sha256'),
]:
    assert digest(ROOT / relative) == review[key], relative + ' drifted after review'
assert digest(OUT / 'roadmap_independent_review.json') == 'ff7b819ed749eebfe007676ac575b4706ccd45c52fc86c9185a7fb19abbba487'
assert digest(OUT / 'roadmap_independent_review.md') == 'be2546cc7bb8402f3b2e5ad8f41e9cfe32d0fa38618f01cb022cef9d4482f311'
assert len(basis['local_source_sha256']) == 13
for relative, expected in basis['local_source_sha256'].items():
    assert digest(ROOT / relative) == expected, relative + ' source pin changed'
assert digest(OUT / 'status_snapshot.json') == basis['status_snapshot_sha256']
assert basis['calendar_dates_are_proposed_targets'] is True
assert basis['new_compute_authorized'] is False
assert basis['submission_authorized'] is False

# This checked item records the publication performed below; any failure is retained
# in the hidden worker log and publication must be reconciled before reporting done.
todo = ROOT / 'tasks/todo.md'
text = todo.read_text(encoding='utf-8')
old = '- [ ] Record results and publish the explicit planning paths to GitHub.'
assert text.count(old) == 1
text = text.replace(old, '- [x] Record results and publish the explicit planning paths to GitHub. Reviewed roadmap and frozen receipts; explicit paths only; remote commit equality checked by bank_roadmap.py.')
with todo.open('w', encoding='utf-8', newline='') as stream:
    stream.write(text)

git('add', '-f', '--', *PATHS)
assert names(git('diff', '--cached', '--name-only')) == set(PATHS), 'Staged path set differs'
git('-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol', 'diff', '--cached', '--check')
for relative in PATHS:
    staged = git('show', ':' + relative)
    local = (ROOT / relative).read_bytes()
    assert staged == local or staged == local.replace(b'\r\n', b'\n'), relative + ' staged bytes differ'

message = 'Map remaining DFT, melt and STS phases with dated gates and budget unknowns'
print(git('commit', '-m', message).decode('utf-8', 'replace'), flush=True)
commit = git('rev-parse', 'HEAD').decode().strip()
print(git('push', 'origin', BRANCH).decode('utf-8', 'replace'), flush=True)
remote = git('ls-remote', 'origin', 'refs/heads/' + BRANCH).decode().split()[0]
assert remote == commit, 'Remote branch does not match roadmap commit'
assert not git('diff', '--name-only').strip(), 'Tracked working tree changed'
assert not git('diff', '--cached', '--name-only').strip(), 'Index changed'
receipt = {
    'schema': 'sts-roadmap-publication-v1',
    'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'publication_succeeded': True, 'commit': commit, 'remote_commit': remote,
    'branch': BRANCH, 'explicit_paths': PATHS,
    'roadmap_sha256': review['roadmap_sha256'],
    'source_pins_verified': 13, 'review_decision': review['decision'],
    'new_compute_or_sample_work': False,
    'anvil_runtime_checkout_changed': False,
}
(OUT / 'publication.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, indent=2), flush=True)
