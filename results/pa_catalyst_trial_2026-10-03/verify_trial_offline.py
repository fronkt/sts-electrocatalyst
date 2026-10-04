"""Fresh offline regression and scientific/preservation gate; never launch QE."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
import urllib.request

PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parents[1]
FT = ROOT / 'results/s2_2026-09-25/full_text'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def preserve():
    baseline = json.loads((PHASE/'baseline.json').read_text(encoding='utf-8'))
    for row in baseline['tracked_pins'] + baseline['untracked_pins']:
        path = ROOT / row['path']
        if not path.is_file() or path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
            raise ValueError('historical/unrelated byte drift: '+row['path'])
    return {'tracked_files':len(baseline['tracked_pins']),
            'unrelated_files':len(baseline['untracked_pins']), 'errors':[]}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def main(label):
    if label not in {'initial', 'checked', 'release'}:
        raise ValueError('explicit distinct verification label required')
    receipt_path = PHASE / ('offline_'+label+'.json')
    if receipt_path.exists():
        raise ValueError('refuse overwrite of earlier verification receipt')
    report = {'scope':'ONE_BOUNDARY_TRIAL_PRELAUNCH_ONLY', 'label':label,
              'new_jobs_submitted':0, 'qe_executed':False, 'production_accepted':False,
              'successful':False}
    try:
        report['before'] = preserve()
        files = ['src/dft/pa_qe_adapter.py','src/dft/pa_catalyst_trial.py',
                 'tests/test_pa_qe_adapter.py','tests/test_pa_catalyst_trial.py',
                 'tests/test_pa_catalyst_watch.py',
                 'anvil/89_pa_catalyst_boundary_trial.slurm',
                 'results/pa_catalyst_trial_2026-10-03/source_boundary_review.md',
                 'results/pa_catalyst_trial_2026-10-03/launch_spec.json',
                 'results/pa_catalyst_trial_2026-10-03/replay_retained_raw.py',
                 'results/pa_catalyst_trial_2026-10-03/watch_trial_readonly.py',
                 'results/pa_catalyst_trial_2026-10-03/verify_trial_offline.py']
        before_pins = {p:digest(ROOT/p) for p in files}
        def offline(*args, **kwargs):
            raise RuntimeError('offline verification refuses URL requests')
        urllib.request.urlopen = offline
        sys.path.insert(0, str(FT))
        suite = unittest.TestSuite()
        for directory in [FT, FT/'download_si_review_2026-10-02',
                          FT/'download_si_review_2026-10-03', ROOT/'results/pa_integration_2026-10-03']:
            suite.addTests(unittest.TestLoader().discover(str(directory), pattern='test_*.py'))
        evidence = unittest.TextTestRunner(verbosity=1).run(suite)
        report['evidence_tests'] = {'tests_run':evidence.testsRun,'successful':evidence.wasSuccessful(),
                                    'failures':len(evidence.failures),'errors':len(evidence.errors)}
        tests = ['tests/test_pa_qe_adapter.py','tests/test_pa_catalyst_trial.py',
                 'tests/test_pa_catalyst_watch.py',
                 'tests/test_pa_checked_contract.py','tests/test_pa_restart_diagnostic.py',
                 'tests/test_pa_tiny_restart_probe.py','tests/test_pa_tiny_raw_readout.py',
                 'tests/test_pa_tiny_readonly_watch.py','tests/test_research_batch_checked.py',
                 'tests/test_research_batch_seeded.py','tests/test_lowtail_batch_launch.py']
        args = [sys.executable,'-B','-m','pytest','-q',*tests]
        process = subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',
                                 errors='replace',timeout=300,creationflags=0x08000000)
        report['compute_tests'] = {'args':args,'returncode':process.returncode,
                                   'stdout':process.stdout,'stderr':process.stderr}
        print(process.stdout, flush=True)
        report['code_pins'] = {p:digest(ROOT/p) for p in files}
        if report['code_pins'] != before_pins:
            raise ValueError('implementation/tests changed while verification ran')
        if not evidence.wasSuccessful() or process.returncode:
            raise ValueError('offline regression did not pass')
        if label == 'checked':
            raw = json.loads((PHASE/'raw_replay_checked.json').read_text())
            assert raw['successful'] and not raw['qe_executed']
            assert raw['adapter_sha256'] == before_pins['src/dft/pa_qe_adapter.py']
            linux = json.loads((PHASE/'linux_guards_checked2.json').read_text())
            assert linux['returncode'] == 0
            linux_result = json.loads(linux['stdout'])
            assert linux_result['successful'] and not linux_result['qe_executed']
            for path, pin in linux_result['code_pins'].items():
                assert digest(ROOT/path) == pin
            report['actual_raw_replay_pass'] = True
            report['linux_guard_checks'] = len(linux_result['checks'])
        scientific = module('catalyst_trial_scientific_verifier', FT/'verify_evidence_recovery.py')
        assert Path(scientific.__file__).resolve() == (FT/'verify_evidence_recovery.py').resolve()
        fresh = PHASE / ('scientific_'+label)
        fresh.mkdir(exist_ok=False)
        result = scientific.main(baseline_dir=FT/'download_si_review_2026-10-03/code_validation_checked',
                                 output_dir=fresh)
        rounds = module('catalyst_trial_round_verifier', FT/'verify_si_round.py')
        rounds.AUDIT = fresh/'si_round_verification.json'
        rounds.main(require_audits=True)
        report['scientific_verifiers_pass'] = True
        report['registered_recovery_reads'] = result['independent_reads']
        with (FT/'reconcile/current_state.csv').open(encoding='utf-8',newline='') as stream:
            rows = list(csv.DictReader(stream))
        with (FT/'si_checklist.csv').open(encoding='utf-8',newline='') as stream:
            checklist = list(csv.DictReader(stream))
        assert len(rows) == 2496 and len(checklist) == 144
        report['canonical_rows'] = len(rows)
        report['checklist_rows'] = len(checklist)
        report['source_files'] = []
        failed_source_rows = []
        for receipt in sorted(PHASE.glob('qe_source*retrieval.json')):
            for row in json.loads(receipt.read_text(encoding='utf-8'))['files']:
                if 'sha256' not in row:
                    failed_source_rows.append(dict(row, receipt=receipt.name))
                    continue
                path = PHASE/'qe_source'/row['path']
                assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256']
                report['source_files'].append(row)
        assert len({p['path'] for p in report['source_files']}) == 27
        report['unsuccessful_source_locations_retained'] = failed_source_rows
        report['after'] = preserve()
        report['successful'] = True
    except BaseException as exc:
        report['error'] = repr(exc)
        raise
    finally:
        receipt_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in {'compute_tests','source_files'}},indent=2))
    return report


if __name__ == '__main__':
    main(sys.argv[1])
