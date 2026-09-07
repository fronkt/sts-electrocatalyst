from copy import deepcopy
import pytest
from dft.hea_validation_plan import prepare as prepare_plan, materialize, seal
from scripts.prepare_failure_benchmark import prepare
from hea_oer.failure_benchmark import evaluate


@pytest.fixture
def inputs(tmp_path):
    plan = prepare_plan()
    return plan, materialize(plan, tmp_path)


def test_known_geometry_does_not_become_dft_truth(inputs):
    plan, snapshot = inputs
    payload, evidence = prepare(plan, snapshot)
    assert len(payload['cases']) == 45
    assert sum(c['features']['geometry_status'] is not None for c in payload['cases']) == 6
    assert all(c['truth'] is None and c['ranking'] is None for c in payload['cases'])
    assert all(c['features']['ensemble_spread_ev'] is None for c in payload['cases'])
    assert evaluate(payload)['status'] == 'PENDING'
    assert len(evidence['cases']) == 45
    assert sum(c['split'] == 'heldout' for c in payload['cases']) == 12


@pytest.mark.parametrize('mutation', ['hash','slot','split','geometry'])
def test_snapshot_identity_and_slot_protection(inputs, mutation):
    plan, snapshot = inputs
    bad = deepcopy(snapshot)
    if mutation == 'hash': bad['plan_id'] = '0' * 64
    elif mutation == 'slot': bad['slots'].pop()
    elif mutation == 'split': bad['slots'][0]['split'] = 'targeted_audit'
    else:
        ready = next(s for s in bad['slots'] if s['status'] == 'ready')
        ready['states']['OOH']['geometry']['positions_A'][-1][0] += 1
    if mutation != 'hash': seal(bad, 'snapshot_id')
    with pytest.raises(ValueError): prepare(plan, bad)


def test_missing_feature_not_zero_or_clean_label(inputs):
    payload, evidence = prepare(*inputs)
    missing = [c for c in payload['cases'] if c['split'] == 'heldout']
    assert all(c['features'] == dict(converged=None, geometry_status=None, ensemble_spread_ev=None) for c in missing)


def test_clean_reference_hash_required_for_reconstruction(inputs):
    plan, snapshot = inputs
    bad = deepcopy(snapshot)
    ready = next(s for s in bad['slots'] if s['status'] == 'ready')
    ready['states']['slab']['geometry']['positions_A'][0][0] += 0.5
    seal(bad, 'snapshot_id')
    with pytest.raises(ValueError, match='clean-slab'):
        prepare(plan, bad)
