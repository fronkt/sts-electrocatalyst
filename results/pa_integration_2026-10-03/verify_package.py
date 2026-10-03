"""Offline evidence/compute regressions and exact prior-byte preservation."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
import urllib.request
from collections import Counter

PHASE = Path(__file__).resolve().parent
REPO = PHASE.parents[1]
FT = REPO / 'results/s2_2026-09-25/full_text'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024*1024), b''):
            h.update(data)
    return h.hexdigest()


def preserve(baseline):
    errors = []
    for item in baseline['tracked_pins'] + baseline['untracked_pins']:
        path = REPO / item['path']
        if not path.is_file() or path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            errors.append(item['path'])
    if errors:
        raise ValueError('historical/unrelated bytes changed: ' + repr(errors))
    return {'tracked_files':len(baseline['tracked_pins']),
            'unrelated_untracked_files':len(baseline['untracked_pins']), 'errors':[]}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write(name, report):
    (PHASE/name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


def main():
    def forbidden(*args, **kwargs):
        raise RuntimeError('offline package forbids URL requests')
    urllib.request.urlopen = forbidden
    baseline = json.loads((PHASE/'baseline.json').read_text(encoding='utf-8'))
    before = preserve(baseline)
    extract = load('pa_package_extract_verified', PHASE/'extract_evidence.py')
    outputs = [extract.main()['outputs'] for _ in range(2)]
    if outputs[0] != outputs[1]:
        raise ValueError('extraction is not deterministic')
    sys.path.insert(0, str(FT))
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for directory in (FT, FT/'download_si_review_2026-10-02', FT/'download_si_review_2026-10-03', PHASE):
        suite.addTests(loader.discover(str(directory), pattern='test_*.py'))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    evidence_tests = {'tests_run':result.testsRun, 'successful':result.wasSuccessful(),
                      'failures':len(result.failures), 'errors':len(result.errors)}
    write('evidence_tests.json', evidence_tests)
    if not result.wasSuccessful():
        raise ValueError('offline evidence tests fail')
    paths = ['tests/test_pa_checked_contract.py', 'tests/test_pa_restart_diagnostic.py',
             'tests/test_pa_tiny_restart_probe.py', 'tests/test_pa_tiny_raw_readout.py',
             'tests/test_pa_tiny_readonly_watch.py', 'tests/test_research_batch_checked.py',
             'tests/test_research_batch_seeded.py', 'tests/test_lowtail_batch_launch.py']
    command = [sys.executable,'-B','-m','pytest','-q',*paths]
    process = subprocess.run(command,cwd=REPO,capture_output=True,text=True,
                             encoding='utf-8',errors='replace',timeout=300,
                             creationflags=0x08000000)
    compute_tests = {'command':command,'returncode':process.returncode,
                     'stdout':process.stdout,'stderr':process.stderr,
                     'qe_or_remote_jobs_executed':False,
                     'implementation_sha256':sha(REPO/'src/dft/pa_checked_contract.py'),
                     'tests_sha256':sha(REPO/'tests/test_pa_checked_contract.py')}
    write('compute_tests.json', compute_tests)
    print(process.stdout)
    if process.returncode:
        raise ValueError('offline compute tests fail: '+process.stderr)
    import verify_evidence_recovery
    scientific = verify_evidence_recovery.main(
        baseline_dir=FT/'download_si_review_2026-10-03/code_validation_checked',output_dir=PHASE)
    import verify_si_round
    verify_si_round.AUDIT = PHASE/'si_round_verification.json'
    verify_si_round.main(require_audits=True)
    after = preserve(baseline)
    with (FT/'reconcile/current_state.csv').open(encoding='utf-8',newline='') as stream:
        current = list(csv.DictReader(stream))
    with (FT/'si_checklist.csv').open(encoding='utf-8',newline='') as stream:
        checklist = list(csv.DictReader(stream))
    counts = Counter(r['v5_final'] for r in current)
    if len(current)!=2496 or len(checklist)!=144 or counts['ELIGIBLE']!=178 or counts['NEEDS_SI']!=89 or counts['UNRESOLVED']!=121:
        raise ValueError('canonical scientific counts differ')
    git = subprocess.run(['git','status','--porcelain','--untracked-files=no'],cwd=REPO,
                         capture_output=True,text=True,timeout=60,creationflags=0x08000000)
    if git.returncode or any(not line.endswith(' tasks/todo.md') for line in git.stdout.splitlines()):
        raise ValueError('unexpected tracked change: '+git.stdout+git.stderr)
    report = {'scope':'OFFLINE_EXTRACTION_AND_PA_CONTRACT_ONLY',
              'before':before,'after':after,'evidence_tests':evidence_tests,
              'compute_tests_returncode':process.returncode,'extraction_outputs':outputs,
              'deterministic_extraction':True,'records':len(current),'checklist_records':len(checklist),
              'v5_counts':dict(counts),'verified_recovery_reads':scientific['independent_reads'],
              'canonical_screening_or_checklist_changes':0,'new_paid_external_api_calls':0,
              'new_qe_or_slurm_jobs':0,'production_accepted':False,
              'budget_estimate_usd':baseline['budget_estimate_usd'],
              'tracked_status_before_commit':git.stdout,'errors':[]}
    write('package_verification.json', report)
    print(json.dumps(report,indent=2))
    return report


if __name__ == '__main__':
    main()
