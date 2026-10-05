"""Exact-path publication of the reviewed re-test package.  PREPARED, NOT RUN.

Run only after (1) verify_retest_offline.py ran with label `checked` and succeeded, and (2) the independent review wrote
independent_launch_review_final.md in this directory with the line `Decision: GO_ONE_BOUNDARY_RETEST_PRELAUNCH`.
Stages explicit paths only (never `git add .`), checks that no tracked file outside the list is modified, verifies the staged
blobs byte for byte, commits with a one-line message (no co-author trailer), pushes, verifies the remote head, and writes
publication_final.json with the blob pins the stage script needs.  It submits nothing and starts no QE.
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess

PHASE = pathlib.Path(__file__).resolve().parent
ROOT = PHASE.parents[1]
PHASE_REL = 'results/pa_catalyst_retest_2026-10-04'
BRANCH = 'r0-catalysis-revival'
RECEIPT = PHASE / 'publication_final.json'
ENV = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never', GCM_GUI_PROMPT='0')
MESSAGE = ('Add corrected one-boundary catalyst re-test (unsubmitted): QE 7.5 XML adapter v2 with real-output tests, '
           'PREFLIGHT replay of the real control call, dated spec and held-submit scripts')
FIXED = ['src/dft/pa_qe_adapter_v2.py', 'src/dft/pa_catalyst_retest.py', 'tests/test_pa_qe_adapter_v2.py',
         'tests/test_pa_qe_adapter_v2_real.py', 'tests/test_pa_catalyst_retest.py', 'tests/test_pa_catalyst_retest_scripts.py',
         'tests/qe75_real_fixtures.py', 'anvil/90_pa_catalyst_retest.slurm', 'docs/research/pa-catalyst-retest-2026-10-04.md', 'tasks/todo.md', 'results/pa_catalyst_trial_readout_prep_2026-10-04/.gitattributes',
         'results/pa_catalyst_trial_readout_prep_2026-10-04/readout_trial.py',
         'results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py',
         'results/pa_catalyst_trial_readout_prep_2026-10-04/launch_sources.py',
         'results/pa_catalyst_trial_readout_prep_2026-10-04/launch_snapshot.json']
EXTRA_PINNED = ['.gitattributes', 'src/dft/pa_checked_contract.py',
                'runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in']
# receipts written by later steps, never part of the reviewed package
LATER = ('publication', 'commit_paths', 'remote_stage', 'submission', 'held_validation', 'release', 'retest_observations',
         'retest_watch_status')
EXACT_BYTES_PREFIXES = (PHASE_REL + '/', 'tests/fixtures/qe75_real/',
                        'results/pa_catalyst_trial_readout_prep_2026-10-04/')  # `* -text` directories: the blob must equal the file


def digest(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def package_paths():
    paths = list(FIXED)
    for base in (ROOT / 'tests/fixtures/qe75_real', PHASE,
                 ROOT / 'results/pa_catalyst_trial_readout_prep_2026-10-04/launch_snapshot'):
        for current, directories, files in os.walk(str(base)):
            directories[:] = sorted(d for d in directories if d != '__pycache__')
            for name in sorted(files):
                rel = pathlib.Path(current, name).relative_to(ROOT).as_posix()
                if base == PHASE and (name.startswith(LATER) or name.endswith('.tmp')):
                    continue
                paths.append(rel)
    return sorted(set(paths))


def main():
    assert not RECEIPT.exists(), 'a publication receipt already exists; retain it'
    report = {'scope': 'REVIEWED_ONE_BOUNDARY_RETEST_PRELAUNCH_PACKAGE', 'successful': False, 'commands': [], 'new_jobs_submitted': 0,
              'qe_executed': False, 'production_accepted': False}

    def git(*args, timeout=60, binary=False):
        command = ['git', '-c', 'credential.interactive=never', *args]
        p = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True, timeout=timeout, creationflags=0x08000000)
        row = {'args': command, 'returncode': p.returncode}
        if not binary:
            row.update(stdout=p.stdout.decode('utf-8', 'replace'), stderr=p.stderr.decode('utf-8', 'replace'))
        report['commands'].append(row)
        assert p.returncode == 0, row
        return p.stdout if binary else p.stdout.decode('utf-8').strip()

    try:
        checked = json.loads((PHASE / 'offline_release_lf.json').read_text(encoding='utf-8'))
        assert checked['successful'] and checked['label'] == 'release_lf'
        for rel, pin in checked['code_pins'].items():
            assert digest(ROOT / rel) == pin, 'tested byte drift: ' + rel
        review = PHASE / 'independent_launch_review_final.md'
        assert 'Decision: GO_ONE_BOUNDARY_RETEST_PRELAUNCH' in review.read_text(encoding='utf-8')
        reviewed = json.loads((PHASE / 'independent_launch_review_final_pins.json').read_text(encoding='utf-8'))
        assert reviewed['decision'] == 'GO_ONE_BOUNDARY_RETEST_PRELAUNCH'
        assert reviewed['checked_receipt_sha256'] == digest(PHASE / 'offline_release_lf.json'), 'independent review receipt is stale'
        assert reviewed['code_pins'] == checked['code_pins'], 'independent review does not bind the verified package'
        for rel, pin in reviewed['code_pins'].items():
            assert digest(ROOT / rel) == pin, 'independently reviewed byte drift: ' + rel
        report['final_review_sha256'] = digest(review)
        report['final_review_pins_sha256'] = digest(PHASE / 'independent_launch_review_final_pins.json')
        report['checked_receipt_sha256'] = digest(PHASE / 'offline_release_lf.json')
        spec = importlib.util.spec_from_file_location('retest_verifier_for_publication', PHASE / 'verify_retest_offline.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        report['before'] = verifier.preserve()
        report['base_head'] = git('rev-parse', 'HEAD')
        assert git('branch', '--show-current') == BRANCH
        assert not git('diff', '--cached', '--name-only'), 'prior staged work'
        paths = package_paths()
        assert set(git('diff', '--name-only').splitlines()) <= set(FIXED), 'tracked edits outside the reviewed package'
        for rel in paths:
            assert (ROOT / rel).is_file(), 'package path missing: ' + rel
        (PHASE / 'commit_paths.json').write_text(json.dumps({'paths': paths + [PHASE_REL + '/commit_paths.json']}, indent=2) + '\n', encoding='utf-8')
        paths = sorted(set(paths + [PHASE_REL + '/commit_paths.json']))
        report['paths'] = paths
        report['local_pins'] = {rel: digest(ROOT / rel) for rel in paths}
        git('add', '-f', '--', *paths)
        assert set(git('diff', '--cached', '--name-only').splitlines()) == set(paths), 'staged path set differs'
        git('-c', 'core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol', 'diff', '--cached', '--check')
        report['staged_blob_pins'] = {}
        for rel in paths:
            blob = git('show', ':' + rel, binary=True)
            data = (ROOT / rel).read_bytes()
            if rel.startswith(EXACT_BYTES_PREFIXES):
                assert blob == data, 'exact-byte path changed by Git: ' + rel
            else:
                assert blob in (data, data.replace(b'\r\n', b'\n')), 'unexpected staged bytes: ' + rel
            report['staged_blob_pins'][rel] = {'sha256': hashlib.sha256(blob).hexdigest(), 'bytes': len(blob)}
        git('commit', '-m', MESSAGE, timeout=90)
        report['commit'] = git('rev-parse', 'HEAD')
        git('push', 'origin', BRANCH, timeout=180)
        remote = git('ls-remote', 'origin', 'refs/heads/' + BRANCH, timeout=90).split()[0]
        assert remote == report['commit']
        report['remote_commit'] = remote
        report['additional_blob_pins'] = {}
        for rel in EXTRA_PINNED:
            blob = git('show', 'HEAD:' + rel, binary=True)
            report['additional_blob_pins'][rel] = {'sha256': hashlib.sha256(blob).hexdigest(), 'bytes': len(blob)}
        assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
        report['after'] = verifier.preserve()
        for rel, pin in report['local_pins'].items():
            if rel != PHASE_REL + '/commit_paths.json':
                assert digest(ROOT / rel) == pin, 'post-publication drift: ' + rel
        report['successful'] = True
    except BaseException as exc:
        report['error'] = repr(exc)
        raise
    finally:
        RECEIPT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'successful': True, 'commit': report['commit'], 'remote_commit': report['remote_commit'],
                      'explicit_paths': len(paths), 'preserved': report['after'], 'new_jobs_submitted': 0}, indent=2))


if __name__ == '__main__':
    main()
