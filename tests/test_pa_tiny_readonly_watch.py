"""Read-only watcher safety fixtures; no SSH, scheduler call or QE execution."""
import hashlib
import importlib.util
import io
import json
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

SOURCE=Path(__file__).resolve().parents[1]/'results/s2_2026-09-25/full_text/sequential_2026-10-03/pa_tiny_readonly_watch.py'


@pytest.fixture
def watch(tmp_path,monkeypatch):
    spec=importlib.util.spec_from_file_location('tiny_readonly_watch',SOURCE)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module,'PHASE',tmp_path)
    return module


def test_status_cannot_accept_production(watch):
    watch.status(state='COMPLETED',production_accepted=True)
    receipt=json.loads((watch.PHASE/'pa_tiny_watch_status.json').read_text(encoding='utf-8'))
    assert receipt['production_accepted'] is False
    assert receipt['readonly'] and receipt['automatic_qe_retry'] is False


def test_observe_preserves_raw_readonly_receipt(watch,monkeypatch):
    data={'job_id':'21024848','commands':{'queue':{'stdout':'pending'}}}
    def remote(args,**kwargs):
        assert args[:len(watch.SSH)]==watch.SSH
        assert 'sbatch' not in kwargs['input'] and 'scontrol\',\'release' not in kwargs['input']
        compile(kwargs['input'],'<remote-fixture>','exec')
        return SimpleNamespace(returncode=0,stdout=json.dumps(data),stderr='fixture warning')
    monkeypatch.setattr(watch.subprocess,'run',remote)
    assert watch.observe()==data
    rows=(watch.PHASE/'pa_tiny_observations.jsonl').read_text(encoding='utf-8').splitlines()
    assert len(rows)==1 and json.loads(rows[0])['stderr']=='fixture warning'


def test_mirror_verifies_complete_file_set_and_bytes(watch,monkeypatch):
    content=b'raw QE fixture\n'
    name='probe_21024848.log'
    rows=[{'path':name,'size':len(content),'sha256':hashlib.sha256(content).hexdigest()}]
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as tar:
        member=tarfile.TarInfo(name);member.size=len(content)
        tar.addfile(member,io.BytesIO(content))
    calls=[]
    def remote(args,**kwargs):
        calls.append(args)
        if 'input' in kwargs:
            compile(kwargs['input'],'<inventory-fixture>','exec')
            return SimpleNamespace(returncode=0,stdout=json.dumps(rows),stderr='')
        assert args[-1].startswith('tar -c -C '+watch.REMOTE+' ')
        kwargs['stdout'].write(stream.getvalue())
        return SimpleNamespace(returncode=0,stderr=b'')
    monkeypatch.setattr(watch.subprocess,'run',remote)
    assert watch.mirror()==1 and len(calls)==2
    receipt=json.loads((watch.PHASE/'pa_tiny_mirror_receipt.json').read_text(encoding='utf-8'))
    assert receipt['all_pins_match'] and receipt['full_trajectory_review_pending']
    assert receipt['production_accepted'] is False
    with pytest.raises(AssertionError,match='overwrite'):watch.mirror()


def test_unsafe_mirror_top_level_is_refused(watch,monkeypatch):
    monkeypatch.setattr(watch.subprocess,'run',lambda *a,**kw:SimpleNamespace(
        returncode=0,stdout=json.dumps([{'path':'../evil','size':1,'sha256':'0'*64}]),stderr=''))
    with pytest.raises(AssertionError):watch.mirror()
    assert not (watch.PHASE/'pa_tiny_raw.tar').exists()


def test_terminal_collection_is_not_scientific_acceptance(watch,monkeypatch):
    data={'commands':{'accounting':{'stdout':'21024848|COMPLETED|0:0\n'},'queue':{'stdout':''}}}
    monkeypatch.setattr(watch,'observe',lambda:data)
    monkeypatch.setattr(watch,'mirror',lambda:7)
    watch.main()
    receipt=json.loads((watch.PHASE/'pa_tiny_watch_status.json').read_text(encoding='utf-8'))
    assert receipt['state']=='TERMINAL_MIRRORED' and receipt['full_trajectory_review_pending']
    assert receipt['production_accepted'] is False
