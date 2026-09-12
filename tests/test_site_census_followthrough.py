import json
from pathlib import Path

import pytest

from scripts import site_census_followthrough as follow


@pytest.fixture
def census(tmp_path):
    base = tmp_path / 'census'
    (base / 'manifests').mkdir(parents=True)
    (base / 'results').mkdir()
    jobs = []
    for i in range(103):
        stem = f'job{i}'
        follow.write(base / 'manifests' / f'{stem}.json', {'manifest_id': stem})
        follow.write(base / 'results' / f'{stem}_result.json', {'manifest_id': stem, 'status': 'complete'})
        jobs.append({'stem': stem, 'state': 'done'})
    follow.write(base / 'status.json', {'counts': {'done': 103}, 'jobs': jobs})
    return base


def test_completion_requires_raw_identity_and_clean_results(census):
    assert follow.completion(census)
    target = census / 'results/job0_result.json'
    follow.write(target, {'manifest_id': 'job0', 'status': 'complete_with_errors'})
    with pytest.raises(RuntimeError, match='not complete'):
        follow.completion(census)
    follow.write(target, {'manifest_id': 'wrong', 'status': 'complete'})
    with pytest.raises(RuntimeError, match='identity'):
        follow.completion(census)


def test_incomplete_and_inconsistent_status(census):
    status = follow.read(census / 'status.json')
    status['counts'] = {'done': 102, 'running': 1}
    follow.write(census / 'status.json', status)
    assert not follow.completion(census)
    status['counts'] = {'done': 103}
    status['jobs'][0]['state'] = 'running'
    follow.write(census / 'status.json', status)
    with pytest.raises(RuntimeError, match='disagree'):
        follow.completion(census)
    status['jobs'][0]['state'] = 'error'
    follow.write(census / 'status.json', status)
    with pytest.raises(RuntimeError, match='failed'):
        follow.completion(census)


def test_exact_command_order_and_parameters(tmp_path):
    stages, report = follow.commands(tmp_path, tmp_path / 'census', '2026-09-13')
    assert [s[0] for s in stages] == ['census', *follow.POLICIES, 'compare', 'report']
    assert '--partial' not in sum([s[1] for s in stages], [])
    for name, command, target in stages[1:6]:
        assert command[command.index('--B') + 1] == '10000'
        assert command[command.index('--seed') + 1] == '0'
        assert command[command.index('--admit') + 1] == name
        assert target == tmp_path / 'census/readout' / follow.rr_name(name)
    report_command = stages[-1][1]
    assert report_command[report_command.index('--rr-dir') + 1] == str(tmp_path / 'census/readout')
    assert report == tmp_path / 'docs/95-census-2-3-readout-2026-09-13.md'


def test_rc3_requires_complete_coverage_and_insufficiency(tmp_path):
    path = tmp_path / 'rr.json'
    payload = {'status': 'insufficient_decorations', 'coverage': {
        'expected': ['a'], 'present': ['a', 'nongated'], 'missing': [],
        'refused': [], 'unverified': False, 'partial': False}}
    follow.write(path, payload)
    follow.check_returncode(3, path)
    payload['coverage']['missing'] = ['a']
    follow.write(path, payload)
    with pytest.raises(RuntimeError, match='coverage'):
        follow.check_returncode(3, path)
    with pytest.raises(RuntimeError, match='exit 2'):
        follow.check_returncode(2, path)


def prepare(monkeypatch, census):
    pin = census / 'frozen.txt'
    pin.write_text('original')
    monkeypatch.setattr(follow, 'source_paths', lambda *_: [pin])
    monkeypatch.setattr(follow, 'process_preflight', lambda: None)
    return pin


def test_no_overwrite_retains_error(monkeypatch, census, tmp_path):
    prepare(monkeypatch, census)
    out = census / 'readout_full'
    out.mkdir()
    sentinel = out / 'old.json'
    sentinel.write_text('original')
    with pytest.raises(RuntimeError, match='refusing existing'):
        follow.run(tmp_path, census)
    assert sentinel.read_text() == 'original'
    assert follow.read(census / 'followthrough_2026-09-12/status.json')['status'] == 'ERROR'
    with pytest.raises(RuntimeError, match='existing attempt'):
        follow.run(tmp_path, census)


def test_stop_and_source_drift_before_execution(monkeypatch, census, tmp_path):
    pin = prepare(monkeypatch, census)
    status = follow.read(census / 'status.json')
    status['counts'] = {'done': 102, 'running': 1}
    follow.write(census / 'status.json', status)
    monkeypatch.setattr(follow.time, 'sleep', lambda _: pin.write_text('changed'))
    with pytest.raises(RuntimeError, match='changed'):
        follow.run(tmp_path, census, wait=True)
    assert not (census / 'readout_full').exists()


def test_lock_excludes_another_owner(tmp_path):
    with follow.exclusive_lock(tmp_path / 'lock'):
        with pytest.raises(OSError):
            with follow.exclusive_lock(tmp_path / 'lock'):
                pytest.fail('second owner entered')


def test_nonzero_child_retains_receipt_and_stops(monkeypatch, census, tmp_path):
    prepare(monkeypatch, census)
    calls = []

    class FailedChild:
        returncode = 2

        def __init__(self, command, **kwargs):
            calls.append(command)

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def poll(self):
            return 2

    monkeypatch.setattr(follow.subprocess, 'Popen', FailedChild)
    with pytest.raises(RuntimeError, match='exit 2'):
        follow.run(tmp_path, census)
    assert len(calls) == 1
    state = census / 'followthrough_2026-09-12'
    assert follow.read(state / '00_census.receipt.json')['returncode'] == 2
    assert follow.read(state / 'status.json')['status'] == 'ERROR'


def test_existing_rank_refused(monkeypatch, census, tmp_path):
    prepare(monkeypatch, census)
    (census / 'readout').mkdir()
    old = census / 'readout/rank_resolution_intact.json'
    old.write_text('old')
    with pytest.raises(RuntimeError, match='refusing existing'):
        follow.run(tmp_path, census)
    assert old.read_text() == 'old'
    assert not (census / 'readout_full').exists()


def test_success_runs_all_stages_and_stops_at_review(monkeypatch, census, tmp_path):
    prepare(monkeypatch, census)
    calls = []

    class SuccessChild:
        returncode = 0

        def __init__(self, command, **kwargs):
            calls.append(command)
            assert kwargs['env']['OMP_NUM_THREADS'] == '1'
            if '--out-dir' in command:
                out = Path(command[command.index('--out-dir') + 1])
                out.mkdir()
                header = {'partial': False, 'missing': [], 'manifests_read': {
                    f'job{i}': {'status': 'complete'} for i in range(103)}}
                for name in follow.ARTIFACTS:
                    follow.write(out / name, header)
            else:
                out = Path(command[command.index('--out') + 1])
                out.parent.mkdir(exist_ok=True)
                if '--admit' in command:
                    follow.write(out, {'status': 'complete', 'coverage': {
                        'expected': ['a'], 'present': ['a'], 'missing': [],
                        'refused': [], 'unverified': False, 'partial': False}})
                elif '--compare' in command:
                    follow.write(out, {'comparison': True})
                else:
                    out.write_text('# READOUT: the complete readout of today\n'
                                   '`partial: false`\n**103 manifests read, 0 listed missing**\n')

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def poll(self):
            return 0

    monkeypatch.setattr(follow.subprocess, 'Popen', SuccessChild)
    assert follow.run(tmp_path, census) == 0
    assert len(calls) == 8
    assert [c[c.index('--admit') + 1] for c in calls if '--admit' in c] == list(follow.POLICIES)
    state = census / 'followthrough_2026-09-12'
    status = follow.read(state / 'status.json')
    assert status['status'] == 'READY_FOR_REVIEW'
    assert status['scientific_approval'] is False
    assert len(follow.read(state / 'output_hashes.json')) == 12
