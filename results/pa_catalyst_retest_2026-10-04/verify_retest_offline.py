"""Fresh offline regression and scientific/preservation gate for the corrected re-test; never launches QE.

Usage: python verify_retest_offline.py initial|checked|release   (each label writes its own offline_<label>.json once)

Checks, in one run: the historical byte pins (the 9,816 tracked + 21 unrelated files of the first trial's baseline) before and
after; the retained frozen artifacts of the first trial; the evidence suites; the compute suites of the first trial plus the new
re-test suites; the readout-tool tests; both scientific verifiers; the cached QE source pins; the mutation-check and cost receipts;
and that the re-test code, tests, fixtures and spec did not change while the run was in progress.
"""
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import unittest
import urllib.request
from pathlib import Path

PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[1]
FT = ROOT / 'results/s2_2026-09-25/full_text'
FIRST = ROOT / 'results/pa_catalyst_trial_2026-10-03'
PHASE_REL = 'results/pa_catalyst_retest_2026-10-04'
FROZEN_COPY = ROOT / 'results/pa_catalyst_trial_readout_2026-10-04/dryrun/scratch/pa_qe_adapter_FROZEN_COPY.py'
FROZEN_ADAPTER_SHA256 = '255464215aa898d0c9d34317a1be9b16fb27ba6d35108e0ca78215331a628879'
FROZEN_PINS = {  # artifacts of the first trial that stay byte-identical (repository path -> SHA-256)
    'src/dft/pa_catalyst_trial.py': 'd00656aa0e7e666f75900190ccc703c1fd0fee8293738a311ea9ab5880b368ce',
    'src/dft/pa_checked_contract.py': '67412c8363877f0a6407e382a4d3c33c6c0f6dac7b1f5de3e3968bf77755ae39',
    'anvil/89_pa_catalyst_boundary_trial.slurm': '0ff3deac8c28537a197020e832903f61d47864113406c616f9f9462bb5cc1ed3',
    'results/pa_catalyst_trial_2026-10-03/launch_spec.json': '4bed5002a88857515940230b20ad59e6adc345e29d8567d5b9c5f5511b0b28a2',
    'results/pa_catalyst_trial_2026-10-03/source_boundary_review.md': '7efb6e27d9859eff629df0cc6dfcd90ef9e17b74819e9500ee398b5e432addac',
}
CODE_FILES = ['src/dft/pa_qe_adapter_v2.py', 'src/dft/pa_catalyst_retest.py', 'src/dft/pa_checked_contract.py',
              'anvil/90_pa_catalyst_retest.slurm', 'tests/test_pa_qe_adapter_v2.py', 'tests/test_pa_qe_adapter_v2_real.py',
              'tests/test_pa_catalyst_retest.py', 'tests/test_pa_catalyst_retest_scripts.py', 'tests/qe75_real_fixtures.py',
              'tests/fixtures/qe75_real/manifest.json', PHASE_REL + '/launch_spec.json', PHASE_REL + '/source_xml_input_review.md',
              PHASE_REL + '/pa-catalyst-retest-remote-stage-2026-10-04.py', PHASE_REL + '/pa-catalyst-retest-submit-held-2026-10-04.py',
              PHASE_REL + '/pa-catalyst-retest-held-validation-2026-10-04.py', PHASE_REL + '/pa-catalyst-retest-release-2026-10-04.py',
              PHASE_REL + '/watch_retest_readonly.py',
              'results/pa_catalyst_trial_readout_prep_2026-10-04/readout_trial.py',
              'results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py',
              'results/pa_catalyst_trial_readout_prep_2026-10-04/launch_sources.py',
              'results/pa_catalyst_trial_readout_prep_2026-10-04/launch_snapshot.json',
              'results/pa_catalyst_trial_readout_prep_2026-10-04/.gitattributes',
              'docs/research/pa-catalyst-retest-2026-10-04.md', PHASE_REL + '/provenance.md', PHASE_REL + '/publish_reviewed_package.py', PHASE_REL + '/verify_retest_offline.py']
COMPUTE_TESTS = ['tests/test_pa_qe_adapter.py', 'tests/test_pa_catalyst_trial.py', 'tests/test_pa_catalyst_watch.py',
                 'tests/test_pa_checked_contract.py', 'tests/test_pa_restart_diagnostic.py', 'tests/test_pa_tiny_restart_probe.py',
                 'tests/test_pa_tiny_raw_readout.py', 'tests/test_pa_tiny_readonly_watch.py', 'tests/test_research_batch_checked.py',
                 'tests/test_research_batch_seeded.py', 'tests/test_lowtail_batch_launch.py']
RETEST_TESTS = ['tests/test_pa_qe_adapter_v2.py', 'tests/test_pa_qe_adapter_v2_real.py', 'tests/test_pa_catalyst_retest.py',
                'tests/test_pa_catalyst_retest_scripts.py']
READOUT_TESTS = ['results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py']



def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def preserve():
    """The first trial's historical byte pins: 9,816 tracked and 21 unrelated files."""
    baseline = json.loads((FIRST / 'baseline.json').read_text(encoding='utf-8'))
    for row in baseline['tracked_pins'] + baseline['untracked_pins']:
        path = ROOT / row['path']
        if not path.is_file() or path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
            raise ValueError('historical/unrelated byte drift: ' + row['path'])
    return {'tracked_files': len(baseline['tracked_pins']), 'unrelated_files': len(baseline['untracked_pins']), 'errors': []}


def frozen_lineage():
    """The first trial's frozen artifacts, and the state of the worktree adapter relative to the launch pin."""
    result = {'retained_launch_adapter_sha256': digest(FROZEN_COPY)}
    assert result['retained_launch_adapter_sha256'] == FROZEN_ADAPTER_SHA256, 'retained launch adapter differs from its pin'
    for rel, pin in FROZEN_PINS.items():
        assert digest(ROOT / rel) == pin, 'first-trial artifact changed: ' + rel
    current = digest(ROOT / 'src/dft/pa_qe_adapter.py')
    result['worktree_pa_qe_adapter_sha256'] = current
    result['worktree_pa_qe_adapter_equals_launch_pin'] = current == FROZEN_ADAPTER_SHA256
    result['first_trial_pins_verified'] = sorted(FROZEN_PINS)
    return result


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def pytest_run(tests, extra=()):
    process = subprocess.run([sys.executable, '-B', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *extra, *tests], cwd=ROOT,
                             capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=1500, creationflags=0x08000000)
    tail = [line for line in process.stdout.splitlines() if re.search(r'\d+ (passed|failed)', line)]
    counts = {key: int(number) for number, key in re.findall(r'(\d+) (passed|failed|skipped|deselected|subtests passed|errors?)', tail[-1])} if tail else {}
    failed = [line.split(' ', 1)[1].split(' - ')[0] for line in process.stdout.splitlines() if line.startswith('FAILED ')]
    return {'args': ['pytest', '-q', *extra, *tests], 'returncode': process.returncode, 'summary': tail[-1] if tail else None,
            'counts': counts, 'failed': failed, 'stdout_tail': process.stdout[-1200:], 'stderr_tail': process.stderr[-400:]}




def main(label):
    if label not in {'initial', 'checked', 'release', 'release_lf'}:
        raise ValueError('explicit distinct verification label required')
    receipt_path = PHASE / ('offline_' + label + '.json')
    if receipt_path.exists():
        raise ValueError('refuse overwrite of earlier verification receipt')
    report = {'scope': 'ONE_BOUNDARY_RETEST_PRELAUNCH_ONLY', 'label': label, 'new_jobs_submitted': 0, 'qe_executed': False,
              'anvil_writes': 0, 'production_accepted': False, 'successful': False}
    try:
        report['before'] = preserve()
        report['frozen_lineage'] = frozen_lineage()
        before_pins = {p: digest(ROOT / p) for p in CODE_FILES}

        def offline(*args, **kwargs):
            raise RuntimeError('offline verification refuses URL requests')
        urllib.request.urlopen = offline
        sys.path.insert(0, str(FT))
        suite = unittest.TestSuite()
        for directory in [FT, FT / 'download_si_review_2026-10-02', FT / 'download_si_review_2026-10-03',
                          ROOT / 'results/pa_integration_2026-10-03']:
            suite.addTests(unittest.TestLoader().discover(str(directory), pattern='test_*.py'))
        evidence = unittest.TextTestRunner(verbosity=1).run(suite)
        report['evidence_tests'] = {'tests_run': evidence.testsRun, 'successful': evidence.wasSuccessful(),
                                    'failures': len(evidence.failures), 'errors': len(evidence.errors)}
        report['compute_tests_first_trial_suites'] = pytest_run(COMPUTE_TESTS)
        report['retest_tests'] = pytest_run(RETEST_TESTS)
        readout = pytest_run(READOUT_TESTS)
        report['readout_tool_tests'] = readout
        print(report['compute_tests_first_trial_suites']['stdout_tail'], report['retest_tests']['stdout_tail'], flush=True)
        original = module('retest_original_launch_sources', ROOT / 'results/pa_catalyst_trial_readout_prep_2026-10-04/launch_sources.py')
        report['historical_launch_snapshot'] = original.verify_snapshot(ROOT)
        report['code_pins'] = {p: digest(ROOT / p) for p in CODE_FILES}
        if report['code_pins'] != before_pins:
            raise ValueError('re-test code, tests, fixtures or spec changed while verification ran')
        assert evidence.wasSuccessful(), 'evidence suites failed'
        assert report['compute_tests_first_trial_suites']['returncode'] == 0, 'first-trial compute suites failed'
        assert report['retest_tests']['returncode'] == 0, 'new re-test suites failed'
        assert readout['returncode'] == 0, 'historical readout snapshot-bound tests failed'
        if label in {'checked', 'release', 'release_lf'}:
            wrapper = subprocess.run(['bash', '-n', str(ROOT / 'anvil/90_pa_catalyst_retest.slurm')], capture_output=True, text=True)
            assert wrapper.returncode == 0, wrapper.stderr
            report['wrapper_syntax'] = 'bash -n ok'
            mutation = json.loads((PHASE / 'mutation_checks.json').read_text(encoding='utf-8'))
            assert mutation['all_caught'] and mutation['adapter_sha256'] == digest(ROOT / 'src/dft/pa_qe_adapter_v2.py'), 'mutation receipt is stale'
            report['mutation_checks'] = {'mutations': len(mutation['mutations']), 'all_caught': True}
            audit = json.loads((PHASE / 'audit_real_outputs.json').read_text(encoding='utf-8'))
            assert all(row['result'] == 'ACCEPTED' for row in audit['scf_pairs']) and audit['control_clean_stop']['result'] == 'ACCEPTED'
            report['audit'] = {'scf_pairs_accepted': len(audit['scf_pairs']), 'control': 'ACCEPTED'}
            assert (PHASE / 'cost_envelope.json').is_file()
        scientific = module('retest_scientific_verifier', FT / 'verify_evidence_recovery.py')
        assert Path(scientific.__file__).resolve() == (FT / 'verify_evidence_recovery.py').resolve()
        fresh = PHASE / ('scientific_' + label)
        fresh.mkdir(exist_ok=False)
        result = scientific.main(baseline_dir=FT / 'download_si_review_2026-10-03/code_validation_checked', output_dir=fresh)
        rounds = module('retest_round_verifier', FT / 'verify_si_round.py')
        rounds.AUDIT = fresh / 'si_round_verification.json'
        rounds.main(require_audits=True)
        report['scientific_verifiers_pass'] = True
        report['registered_recovery_reads'] = result['independent_reads']
        with (FT / 'reconcile/current_state.csv').open(encoding='utf-8', newline='') as stream:
            rows = list(csv.DictReader(stream))
        with (FT / 'si_checklist.csv').open(encoding='utf-8', newline='') as stream:
            checklist = list(csv.DictReader(stream))
        assert len(rows) == 2496 and len(checklist) == 144
        report['canonical_rows'], report['checklist_rows'] = len(rows), len(checklist)
        source_files, failed_rows = [], []
        for receipt in sorted(FIRST.glob('qe_source*retrieval.json')):
            for row in json.loads(receipt.read_text(encoding='utf-8'))['files']:
                if 'sha256' not in row:
                    failed_rows.append(dict(row, receipt=receipt.name))
                    continue
                path = FIRST / 'qe_source' / row['path']
                assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256']
                source_files.append(row['path'])
        assert len(set(source_files)) == 27
        report['qe_source_files_verified'] = len(set(source_files))
        report['after'] = preserve()
        report['successful'] = True
    except BaseException as exc:
        report['error'] = repr(exc)
        raise
    finally:
        receipt_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in {'compute_tests_first_trial_suites', 'retest_tests', 'readout_tool_tests', 'code_pins'}},
                     indent=2))
    return report


if __name__ == '__main__':
    main(sys.argv[1])
