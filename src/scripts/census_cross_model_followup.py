"""Bounded post-hoc follow-up using the unchanged diagnostic and census queue.
No automatic retries; new results stay separate from the original census.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def preflight(base):
    from scripts.screen_diagnostic import validate_manifest
    from scripts import site_census_plan as plan
    selection = json.loads((base / 'selection.json').read_text())
    pins = json.loads((base / 'input_pins.json').read_text())
    for rel, expected in pins.items():
        if sha(ROOT / rel) != expected:
            raise ValueError('input hash mismatch: ' + rel)
    expected = {tag + '__' + item['formula']: (tag, item)
                for item in selection['selected'] for tag in selection['models']}
    if len(expected) != 12 or set(p.stem for p in (base / 'manifests').glob('*.json')) != set(expected):
        raise ValueError('expected exactly 12 frozen follow-up manifests')
    for stem, (tag, item) in expected.items():
        m = validate_manifest(json.loads((base / 'manifests' / (stem + '.json')).read_text()))
        p = m['protocol']
        if p['seeds'] != [item['seed']] or p['n_sites'] != 4 or p['steps'] != 300 or p['fmax_eV_A'] != .05:
            raise ValueError('protocol differs from selection')
        if len(m['candidates']) != 1 or m['candidates'][0]['formula'] != item['formula']:
            raise ValueError('candidate differs from selection')
        if sha(plan.model_path(tag)) != m['model']['sha256_bytes']:
            raise ValueError('model differs from frozen manifest')
    return selection

def require_fresh(base):
    if any((base/'results').glob('*_result.json')) or any((base/'results').glob('*.lock')):
        raise FileExistsError('fresh launch refuses existing results or locks')
    if (base/'target_readout.json').exists() or (base/'launch.json').exists() or (base/'status.json').exists():
        raise FileExistsError('follow-up already started or has a final readout')

def readout(base, selection):
    from hea_oer.site_integrity import classify_row
    rows, missing = [], []
    original = ROOT / 'results/site_census_2026-09-06/results'
    targets = selection['selected'] + [dict(x, target_site_index=x['site_index']) for x in selection['reused']]
    for item in targets:
        source = base / 'results' if item in selection['selected'] else original
        for tag in selection['models']:
            p = source / (tag + '__' + item['formula'] + '_result.json')
            if not p.exists():
                missing.append(str(p.relative_to(ROOT))); continue
            raw = json.loads(p.read_text())
            records = [r for r in raw['results'] if r['formula'] == item['formula'] and r['status'] == 'evaluated']
            if not records:
                missing.append(str(p.relative_to(ROOT)) + ': no evaluated record'); continue
            row = records[0]['row']
            site = next((s for s in row.get('per_site_records', []) if s['seed'] == item['seed'] and s['site_index'] == item['target_site_index']), None)
            if site is None:
                missing.append(str(p.relative_to(ROOT)) + ': selected target absent'); continue
            cls = next(s for s in classify_row(row)['sites'] if s['seed'] == item['seed'] and s['site_index'] == item['target_site_index'])
            # Same seeded chemistry, not merely equal site numbers, is required.
            old_stem = item.get('source_manifest', 'mpa0__' + item['formula'])
            old = json.loads((original / (old_stem + '_result.json')).read_text())['results'][0]['row']
            old_site = next(s for s in old['per_site_records'] if s['seed'] == item['seed'] and s['site_index'] == item['target_site_index'])
            new_clean = next(d['relaxed_slab'] for d in row['decoration_records'] if d['seed'] == item['seed'])
            old_clean = next(d['relaxed_slab'] for d in old['decoration_records'] if d['seed'] == item['seed'])
            composition_ok = row['elements'] == old['elements'] and row['fractions'] == old['fractions']
            identity_ok = composition_ok and new_clean['symbols'] == old_clean['symbols'] and site['initial_binding_metal_index'] == old_site['initial_binding_metal_index'] and all(site['relaxed_states'][sp]['symbols'] == old_site['relaxed_states'][sp]['symbols'] for sp in ('OH', 'O', 'OOH'))
            rows.append(dict(formula=item['formula'], model=tag, source=str(p.relative_to(ROOT)), sha256=sha(p), matched_site_identity=identity_ok, target=cls, steps_eV=[site['dG_OH'],site['dG_O']-site['dG_OH'],site['dG_OOH']-site['dG_O'],4.92-site['dG_OOH']], all_starts=site['start_records'], decoration_controls=classify_row(row)['sites'], interpretation='matched target diagnostic' if identity_ok else 'NOT COMPARABLE: atom identity differs'))
    result = dict(role='post-hoc selected target diagnostic; no rank validation', targets=rows, missing=missing, complete=len(rows)==18 and not missing, all_available_targets_comparable=all(r['matched_site_identity'] for r in rows) if rows else False)
    from scripts.screen_diagnostic import write_json_new
    name = 'target_readout.json' if result['complete'] else 'target_readout_partial_' + str(time.time_ns()) + '_' + uuid.uuid4().hex + '.json'
    write_json_new(base / name, result)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check','run','readout'])
    parser.add_argument('--base', type=Path, default=ROOT/'results/census_cross_model_2026-09-13')
    args = parser.parse_args()
    base = args.base.resolve()
    os.environ['SITE_CENSUS_DIR'] = str(base)
    selection = preflight(base)
    if args.command == 'check':
        from scripts.site_census_runner import Runner
        require_fresh(base)
        jobs = Runner(2).jobs
        if len(jobs) != 12 or any(j.state != 'queued' for j in jobs):
            raise ValueError('check requires 12 fresh jobs')
        print('Verified 12 frozen fresh manifests, model hashes, 2 workers, 2 threads each')
        return 0
    if args.command == 'readout':
        print(json.dumps(readout(base, selection))); return 0
    import psutil
    battery = psutil.sensors_battery()
    if battery is not None and not battery.power_plugged:
        raise RuntimeError('Laptop must be plugged in before this run')
    # Fresh-only launch: recovery after interruption is a separate decision.
    require_fresh(base)
    from scripts.site_census_runner import Runner
    from scripts.screen_diagnostic import write_json_new
    runner = Runner(2)
    if len(runner.jobs) != 12 or any(j.state != 'queued' for j in runner.jobs):
        raise ValueError('refusing nonfresh queue')
    start = time.time()
    write_json_new(base/'launch.json', dict(start_epoch=start,deadline_epoch=start+86400,pid=os.getpid(),workers=2,threads_per_worker=2,role='post-hoc selected-site diagnostic'))
    finished = threading.Event()
    def deadline():
        while not finished.wait(5):
            if time.time() >= start + 86400:
                (base/'STOP').write_text('KILL\n'); return
    watcher = threading.Thread(target=deadline, daemon=True)
    watcher.start()
    try:
        code = runner.loop()
    finally:
        finished.set()
        runner.kill_running()
    result = readout(base, selection)
    write_json_new(base/'completion.json',dict(exit_code=code,elapsed_seconds=time.time()-start,readout_complete=result['complete']))
    return code

if __name__ == '__main__':
    raise SystemExit(main())
