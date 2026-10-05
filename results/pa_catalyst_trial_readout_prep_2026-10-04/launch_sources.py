"""Hash-verified sources of original job 21034683; never substitute the live tree."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

COMMIT = 'b9f0208ee6f3cd71d0201d03b964b5c23f53d644'
MANIFEST_REL = 'results/pa_catalyst_trial_readout_prep_2026-10-04/launch_snapshot.json'
MANIFEST_SHA256 = 'dcb15854775caa79577ee6eb6b623dc135d4de487e3c2b027949f8c5da2ade0b'
SNAPSHOT_REL = 'results/pa_catalyst_trial_readout_prep_2026-10-04/launch_snapshot'

def verify_snapshot(repo):
    repo = Path(repo)
    data = (repo / MANIFEST_REL).read_bytes()
    if hashlib.sha256(data).hexdigest() != MANIFEST_SHA256:
        raise ValueError('original launch snapshot manifest drift')
    manifest = json.loads(data)
    if manifest['commit'] != COMMIT or manifest['job_id'] != '21034683':
        raise ValueError('original launch identity drift')
    for rel, pin in manifest['files'].items():
        if Path(rel).is_absolute() or '..' in Path(rel).parts or pin['snapshot_path'] != SNAPSHOT_REL + '/' + rel:
            raise ValueError('original launch snapshot path escapes its root')
        p = repo / pin['snapshot_path']
        if p.is_symlink() or not p.is_file():
            raise ValueError('original launch snapshot missing or linked: ' + rel)
        raw = p.read_bytes()
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise ValueError('original launch source byte drift: ' + rel)
    return manifest

def source_path(rel, repo):
    manifest = verify_snapshot(repo)
    if rel not in manifest['files']:
        raise ValueError('source is absent from original launch snapshot: ' + rel)
    return Path(repo) / manifest['files'][rel]['snapshot_path']

def load_modules(repo):
    manifest = verify_snapshot(repo)
    def load(name, rel):
        p = Path(repo) / manifest['files'][rel]['snapshot_path']
        spec = importlib.util.spec_from_file_location(name, p)
        module = importlib.util.module_from_spec(spec)
        previous = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous
        return module
    # The adapter imports the bare contract name; temporarily bind its exact launch copy,
    # then restore the live module cache. Never trust an earlier bare-name import.
    contract = load('pa_launch_contract_' + COMMIT, 'src/dft/pa_checked_contract.py')
    missing = object()
    old = sys.modules.get('pa_checked_contract', missing)
    sys.modules['pa_checked_contract'] = contract
    try:
        adapter = load('pa_launch_adapter_' + COMMIT, 'src/dft/pa_qe_adapter.py')
    finally:
        if old is missing:
            sys.modules.pop('pa_checked_contract', None)
        else:
            sys.modules['pa_checked_contract'] = old
    controller = load('pa_launch_controller_' + COMMIT, 'src/dft/pa_catalyst_trial.py')
    return controller, adapter
