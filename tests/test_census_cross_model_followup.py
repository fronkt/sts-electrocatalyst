"""Failure-path checks for the bounded target follow-up; no model execution."""
import json
from pathlib import Path
import sys
import pytest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from scripts import census_cross_model_followup as follow

@pytest.mark.parametrize('name', ['results/x_result.json','results/x_result.json.lock','launch.json','status.json','target_readout.json'])
def test_fresh_guard_refuses_resume_or_existing_run(tmp_path, name):
    follow.require_fresh(tmp_path)
    p=tmp_path/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text('{}')
    with pytest.raises(FileExistsError): follow.require_fresh(tmp_path)

def test_absent_selected_site_is_retained_as_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(follow,'ROOT',tmp_path)
    base=tmp_path/'follow'; (base/'results').mkdir(parents=True)
    sel={'selected':[{'formula':'Cr','seed':20,'target_site_index':2}], 'reused':[], 'models':['omat0']}
    (base/'results/omat0__Cr_result.json').write_text(json.dumps({'results':[{'formula':'Cr','status':'evaluated','row':{'per_site_records':[]}}]}))
    for _ in range(2):
        result=follow.readout(base,sel)
        assert not result['complete']
        assert 'selected target absent' in result['missing'][0]
    assert len(list(base.glob('target_readout_partial_*.json')))==2
    assert not (base/'target_readout.json').exists()

def test_unproduced_result_remains_in_denominator(monkeypatch,tmp_path):
    monkeypatch.setattr(follow,'ROOT',tmp_path)
    base=tmp_path/'follow';base.mkdir()
    result=follow.readout(base,{'selected':[{'formula':'Cr','seed':20,'target_site_index':2}],'reused':[],'models':['omat0']})
    assert not result['complete'] and len(result['missing'])==1 and not result['targets']

def test_changed_pinned_input_refused_before_model_access(monkeypatch,tmp_path):
    monkeypatch.setattr(follow,'ROOT',tmp_path)
    (tmp_path/'selection.json').write_text('{}')
    (tmp_path/'input_pins.json').write_text(json.dumps({'source.json':'bad-hash'}))
    (tmp_path/'source.json').write_text('{}')
    with pytest.raises(ValueError,match='input hash mismatch'):
        follow.preflight(tmp_path)
