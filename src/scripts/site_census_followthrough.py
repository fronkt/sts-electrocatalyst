"""One-shot, failure-retaining completion of the frozen September 6 census.

Run with --wait to remain idle until all 103 jobs finish. No model evaluation,
submission, retry, overwrite, or scientific acceptance is performed here.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
POLICIES = ('all', 'no-desorbed', 'intact', 'adsorbate-intact', 'two-pathway')
ARTIFACTS = ('per_site.csv', 'per_site.json', 'reproduction.json', 'ranking.json', 'distribution.json')


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def hashes(paths):
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def write(path, payload, exclusive=False):
    with path.open('x' if exclusive else 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write('\n')


@contextmanager
def exclusive_lock(path):
    with path.open('a+b') as handle:
        if handle.tell() == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def completion(census):
    """Cheap status gate first; then independently check every raw result identity."""
    status = read(census / 'status.json')
    jobs = status.get('jobs', [])
    if len(jobs) != 103 or len({j['stem'] for j in jobs}) != 103:
        raise RuntimeError('expected exactly 103 unique jobs')
    counts = status.get('counts', {})
    if status.get('stop') or any(j.get('state') in ('error', 'failed') for j in jobs):
        raise RuntimeError('census stopped or failed')
    if counts.get('done') != 103 or any(v for k, v in counts.items() if k != 'done'):
        return False
    if any(j.get('state') != 'done' for j in jobs):
        raise RuntimeError('job states disagree with counts')
    manifests = {p.stem: p for p in (census / 'manifests').glob('*.json')}
    if set(manifests) != {j['stem'] for j in jobs}:
        raise RuntimeError('manifest/job coverage differs')
    for stem, path in manifests.items():
        result = read(census / 'results' / (stem + '_result.json'))
        if result.get('status') != 'complete':
            raise RuntimeError(f'{stem}: raw result not complete')
        identity = read(path).get('manifest_id')
        if not identity or result.get('manifest_id') != identity:
            raise RuntimeError(f'{stem}: manifest identity differs')
    return True


def process_preflight():
    import psutil
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['pid'] == os.getpid():
            continue
        try:
            command = ' '.join(process.info['cmdline'] or []).lower()
            if not command and 'python' in (process.info['name'] or '').lower():
                raise RuntimeError('cannot inspect Python process command')
            if any(name in command for name in (
                'screen_diagnostic', 'site_census_readout', 'rank_resolution_readout', 'site_census_report'
            )):
                raise RuntimeError(f'conflicting worker/readout process {process.pid}')
        except psutil.NoSuchProcess:
            continue


def source_paths(root, census):
    # Pin imported scientific implementations as well as the entry points.
    paths = list((root / 'src/hea_oer').glob('*.py'))
    paths += [root / 'src/scripts' / (name + '.py') for name in (
        'site_census_followthrough', 'site_census_plan', 'site_census_readout',
        'rank_resolution_readout', 'site_census_report')]
    paths += [root / p for p in (
        'docs/91-prereg-site-integrity-census-2026-09-06.md',
        'docs/research/2026-09-06-rank-resolution-spec.md',
        'docs/93-census-1-readout-2026-09-07.md', 'docs/94-census-1b-readout-2026-09-07.md')]
    paths += list((root / 'results/ranking_adequacy_2026-09-06/inputs').glob('*.json'))
    paths += list((census / 'manifests').glob('*.json'))
    paths += [census / 'MANIFESTS.sha256', census / 'o2_fragment/o2_records.json']
    paths += [census / 'readout' / name for name in ARTIFACTS]
    return paths


def rr_name(policy):
    return 'rank_resolution' + ('' if policy == 'all' else '_' + policy) + '.json'


def commands(root, census, date):
    out = census / 'readout_full'
    ranks = census / 'readout'
    gated = root / 'results/ranking_adequacy_2026-09-06/inputs/r4_gated.json'
    def cmd(name, *args):
        return [sys.executable, str(root / 'src/scripts' / (name + '.py')), *map(str, args)]
    stages = [('census', cmd('site_census_readout', '--manifest-dir', census / 'manifests',
        '--result-dir', census / 'results', '--out-dir', out,
        '--o2-records', census / 'o2_fragment/o2_records.json'), None)]
    for policy in POLICIES:
        target = ranks / rr_name(policy)
        stages.append((policy, cmd('rank_resolution_readout', '--results', census / 'results',
            '--gated', gated, '--B', '10000', '--seed', '0', '--admit', policy, '--out', target), target))
    stages.append(('compare', cmd('rank_resolution_readout', '--compare',
        *[ranks / rr_name(p) for p in POLICIES], '--out', ranks / 'rank_resolution_compare.json'), None))
    report = root / 'docs' / f'95-census-2-3-readout-{date}.md'
    stages.append(('report', cmd('site_census_report', '--census-dir', census,
        '--readout-dir', out, '--rr-dir', ranks, '--title-date', date, '--out', report), None))
    return stages, report


def check_returncode(code, rr_path):
    if rr_path is not None and code in (0, 3):
        data = read(rr_path)
        coverage = data.get('coverage', {})
        if (not coverage.get('expected') or not set(coverage['expected']).issubset(coverage.get('present', []))
                or any(coverage.get(k) for k in ('missing', 'refused', 'unverified', 'partial'))):
            raise RuntimeError('rank readout lacks complete verified coverage')
        expected_status = 'insufficient_decorations' if code == 3 else 'complete'
        if data.get('status') != expected_status:
            raise RuntimeError('rank exit/status disagreement')
    elif code != 0:
        raise RuntimeError(f'readout failed with exit {code}')


def run(root, census, wait=False, poll_seconds=30):
    state = census / 'followthrough_2026-09-12'
    state.mkdir(exist_ok=True)
    with exclusive_lock(state / 'runner.lock'):
        if (state / 'pins.json').exists():
            raise RuntimeError('existing attempt retained; review it before another attempt')
        frozen = hashes(source_paths(root, census))
        write(state / 'pins.json', {'time': stamp(), 'pid': os.getpid(), 'sha256': frozen}, True)
        result_pins = {}
        def guard():
            if (census / 'STOP').exists() or (state / 'STOP').exists():
                raise RuntimeError('STOP requested')
            if hashes(source_paths(root, census)) != frozen:
                raise RuntimeError('frozen source/spec/input/history changed')
            if result_pins and hashes(list((census / 'results').glob('*_result.json'))) != result_pins:
                raise RuntimeError('sealed result bytes changed')
        try:
            while True:
                guard()
                if completion(census):
                    break
                write(state / 'status.json', {'time': stamp(), 'status': 'WAITING_FOR_COMPLETE_CENSUS'})
                if not wait:
                    return 2
                time.sleep(poll_seconds)
            process_preflight()
            guard()
            result_pins = hashes(list((census / 'results').glob('*_result.json')))
            write(state / 'result_pins.json', result_pins, True)
            stages, report = commands(root, census, datetime.now(timezone.utc).date().isoformat())
            rank_outputs = [census / 'readout' / rr_name(p) for p in POLICIES]
            rank_outputs.append(census / 'readout/rank_resolution_compare.json')
            if (census / 'readout_full').exists() or report.exists() or any(p.exists() for p in rank_outputs):
                raise RuntimeError('refusing existing readout_full/report output')
            write(state / 'commands.json', stages, True)
            env = dict(os.environ, OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
                       NUMEXPR_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')
            for index, (name, command, rr_path) in enumerate(stages):
                guard()
                process_preflight()
                if '--out' in command and Path(command[command.index('--out') + 1]).exists():
                    raise RuntimeError(f'refusing existing output for {name}')
                write(state / 'status.json', {'time': stamp(), 'status': 'RUNNING', 'stage': name})
                start = stamp()
                with (state / f'{index:02d}_{name}.log').open('x', encoding='utf-8') as log:
                    with subprocess.Popen(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT) as child:
                        try:
                            while child.poll() is None:
                                try:
                                    child.wait(timeout=5)
                                except subprocess.TimeoutExpired:
                                    guard()
                            code = child.returncode
                        except BaseException:
                            child.terminate()
                            try:
                                child.wait(timeout=10)
                            except subprocess.TimeoutExpired:
                                child.kill()
                                child.wait()
                            raise
                write(state / f'{index:02d}_{name}.receipt.json',
                      {'start': start, 'end': stamp(), 'command': command, 'returncode': code}, True)
                guard()
                check_returncode(code, rr_path)
                if name == 'census':
                    for artifact in ARTIFACTS:
                        path = census / 'readout_full' / artifact
                        if not path.is_file():
                            raise RuntimeError(f'missing census artifact {artifact}')
                        if path.suffix == '.json':
                            data = read(path)
                            manifests = data.get('manifests_read', {})
                            if (data.get('partial') is not False or data.get('missing') != []
                                    or len(manifests) != 103
                                    or any(v.get('status') != 'complete' for v in manifests.values())):
                                raise RuntimeError('full readout lacks 103 complete manifests')
                if name == 'report':
                    content = report.read_text(encoding='utf-8')
                    if ('the complete readout' not in content.splitlines()[0]
                            or '`partial: false`' not in content
                            or '**103 manifests read, 0 listed missing**' not in content):
                        raise RuntimeError('report completion banner missing')
            outputs = list((census / 'readout_full').glob('*')) + rank_outputs + [report]
            write(state / 'output_hashes.json', hashes(outputs), True)
            write(state / 'status.json', {'time': stamp(), 'status': 'READY_FOR_REVIEW',
                  'report': str(report), 'scientific_approval': False})
            return 0
        except Exception as exc:
            write(state / 'status.json', {'time': stamp(), 'status': 'ERROR', 'error': str(exc)})
            raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wait', action='store_true')
    parser.add_argument('--poll-seconds', type=float, default=30)
    args = parser.parse_args(argv)
    if not 1 <= args.poll_seconds <= 60:
        parser.error('--poll-seconds must be between 1 and 60')
    return run(ROOT, ROOT / 'results/site_census_2026-09-06', args.wait, args.poll_seconds)


if __name__ == '__main__':
    raise SystemExit(main())
