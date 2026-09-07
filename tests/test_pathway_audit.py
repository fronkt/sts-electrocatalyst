from copy import deepcopy
import pytest
from hea_oer.pathway_audit import evaluate_cycle


def cycle(bridge=False):
    names = ['clean', 'O+Hb' if bridge else 'OH', 'O', 'O2+Hb' if bridge else 'OOH', 'clean+O2gas']
    return {'schema': 'oer-pathway-audit-v1', 'reference_id': 'same-slab-hamiltonian', 'states': [
        dict(id=name, delta_O=o, delta_H=h, G0_eV=g, reference_id='same-slab-hamiltonian',
             energy_evidence='synthetic-test', surface_regenerated=i == 4)
        for i, (name, o, h, g) in enumerate(zip(names, [0,1,1,2,2], [0,1,0,1,0], [0,1.1,2.7,3.7,4.92]))]}


@pytest.mark.parametrize('bridge', [False, True])
def test_balanced_four_step_and_potential(bridge):
    result = evaluate_cycle(cycle(bridge), 1.23)
    assert result['status'] == 'COMPLETE'
    assert result['limiting_potential_V'] == pytest.approx(1.6)
    assert result['overpotential_V'] == pytest.approx(0.37)
    assert sum(s['delta_G_eV'] for s in result['steps']) == pytest.approx(0, abs=1e-14)


def test_unmeasured_bridge_does_not_get_ooh_correction_or_eta():
    doc = cycle(True)
    doc['states'][1]['G0_eV'] = None
    result = evaluate_cycle(doc)
    assert result['status'] == 'PENDING'
    assert result['overpotential_V'] is None
    assert len(result['missing_energy_steps']) == 2


def test_uphill_chemical_release_cannot_be_fixed_by_potential():
    doc = cycle(True)
    extra = deepcopy(doc['states'][3])
    extra.update(id='Hb+O2gas', G0_eV=4.0)
    doc['states'].insert(4, extra)
    result = evaluate_cycle(doc, 99.0)
    assert result['status'] == 'CHEMICAL_STEP_UPHILL'
    assert result['limiting_potential_V'] is None
    assert result['steps'][3]['delta_G_eV'] == pytest.approx(0.3)


def test_downhill_chemical_release_kept_as_zero_electron_step():
    doc = cycle(True)
    extra = deepcopy(doc['states'][3])
    extra.update(id='Hb+O2gas', G0_eV=3.6)
    doc['states'].insert(4, extra)
    assert evaluate_cycle(doc)['status'] == 'COMPLETE'


@pytest.mark.parametrize('mutation', ['nonregenerated','bad_terminal','lost_H','mixed_reference','nan','no_evidence'])
def test_invalid_cycle(mutation):
    doc = cycle()
    if mutation == 'nonregenerated': doc['states'][-1]['surface_regenerated'] = False
    if mutation == 'bad_terminal': doc['states'][-1]['G0_eV'] = 4.9
    if mutation == 'lost_H': doc['states'][1]['delta_H'] = 0
    if mutation == 'mixed_reference': doc['states'][2]['reference_id'] = 'different-slab'
    if mutation == 'nan': doc['states'][2]['G0_eV'] = float('nan')
    if mutation == 'no_evidence': doc['states'][2].pop('energy_evidence')
    with pytest.raises(ValueError): evaluate_cycle(doc)


@pytest.mark.parametrize('bad_flag', ['false', 'true', 1, 0, None])
def test_surface_regeneration_requires_boolean_true(bad_flag):
    doc = cycle()
    doc['states'][-1]['surface_regenerated'] = bad_flag
    with pytest.raises(ValueError): evaluate_cycle(doc)
