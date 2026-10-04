"""Read-only watcher parsing; no SSH, scheduler mutation or QE."""
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).resolve().parents[1]/'results/pa_catalyst_trial_2026-10-03/watch_trial_readonly.py'
SPEC=importlib.util.spec_from_file_location('catalyst_trial_watch',PATH)
watch=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(watch)

@pytest.mark.parametrize('state',['PENDING','RUNNING','COMPLETED','FAILED','TIMEOUT','OUT_OF_MEMORY'])
def test_only_exact_parent_job_accounting_selects_state(state):
    raw='123.batch|COMPLETED|0:0\n123|'+state+'|0:0\n999|RUNNING|0:0\n'
    assert watch.scheduler_state(raw,'123')==state

def test_missing_accounting_is_not_completion():
    assert watch.scheduler_state('123.batch|COMPLETED|0:0\n','123')=='ACCOUNTING_PENDING'
    assert watch.scheduler_state('','123')=='ACCOUNTING_PENDING'
    assert watch.scheduler_state('123||0:0','123')=='ACCOUNTING_PENDING'

def test_cancelled_suffix_is_retained_as_terminal():
    assert watch.scheduler_state('123|CANCELLED by 456|0:0','123')=='CANCELLED'
    assert watch.scheduler_state('123|FAILED+|1:0','123')=='FAILED'

def test_non_singleton_id_refused_before_any_process():
    with pytest.raises(AssertionError):watch.main('123_4')
