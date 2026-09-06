"""Analytical geometry failures, boundary invariance and evidence preservation."""
from copy import deepcopy
from itertools import product
import json
import math
import numpy as np
import pytest
from ase import Atoms
from hea_oer.adsorbate_geometry import GeometryThresholds, analyze_adsorbate_geometry


def record(atoms):
    return dict(symbols=atoms.get_chemical_symbols(), positions_A=atoms.positions.tolist(), cell_A=atoms.cell.array.tolist(),
                pbc=atoms.pbc.tolist(), converged_by_force=True, max_constrained_force_eV_A=.01, fmax_target_eV_A=.05, energy_eV=-10.)


def example():
    slab = Atoms(['Cr','Ni','O'],positions=[[0,0,0],[5,0,0],[0,4,0]],cell=[20,20,20])
    positions = {'OH':[[0,0,2],[0,0,2.98]],'O':[[0,0,2]],'OOH':[[0,0,2],[1.4,0,2],[1.4,.98,2]]}
    states = {}
    for name, coords in positions.items():
        atoms = slab.copy()
        atoms += Atoms(name, positions=coords)
        states[name] = record(atoms)
    site = dict(seed=0,site_index=0,initial_binding_metal_index=0,relaxed_states=states,eta=.2)
    return dict(formula='synthetic',per_site_records=[site],decoration_records=[dict(seed=0,relaxed_slab=record(slab))],eta=.2)


def state(row,name='OOH'):
    return row['per_site_records'][0]['relaxed_states'][name]


def detail(row,name='OOH',**kwargs):
    return analyze_adsorbate_geometry(row,**kwargs)['sites'][0]['states'][name]


def geometries(row):
    return [row['decoration_records'][0]['relaxed_slab'],*row['per_site_records'][0]['relaxed_states'].values()]


def test_intact_geometry_and_input_preservation():
    row = example()
    original = deepcopy(row)
    result = analyze_adsorbate_geometry(row)
    d = result['sites'][0]['states']['OOH']
    assert d['geometry_status'] == 'observed'
    assert d['exploratory_screen'] == 'no_flags'
    assert d['distances_A'] == pytest.approx({'O_O_A':1.4,'distal_O_H_A':.98,'proximal_O_H_A':math.hypot(1.4,.98)})
    assert d['oxygen_metal_contacts']['proximal_O']['distance_A'] == pytest.approx(2)
    assert result['state_geometry_counts'] == {'observed':3,'unknown':0,'invalid':0}
    assert result['ranking_modified'] is result['eligibility_modified'] is result['chemistry_validated'] is False
    assert row == original
    assert json.loads(json.dumps(result,allow_nan=False)) == result


def test_o_o_separation_requests_inspection():
    row = example()
    state(row)['positions_A'][-2:] = [[3,0,2],[3,.98,2]]
    d = detail(row)
    assert d['distances_A']['O_O_A'] == pytest.approx(3)
    assert 'O_O_above_exploratory_window' in d['flags']
    assert d['geometry_status'] == 'observed'


def test_detached_o2_like_plus_protonated_slab_is_not_o_o_cleavage():
    row = example()
    state(row)['positions_A'][-3:] = [[0,0,5],[1.23,0,5],[0,4,.98]]
    d = detail(row)
    assert d['distances_A']['O_O_A'] == pytest.approx(1.23)
    assert d['H_nearest_slab_O']['distance_A'] == pytest.approx(.98)
    assert 'proximal_O_without_metal_contact_within_exploratory_threshold' in d['flags']
    assert 'H_closer_to_slab_O_than_adsorbate_O' in d['flags']
    assert not any(x.startswith('O_O_') for x in d['flags'])
    assert all(c['distance_A'] > 3 for c in d['oxygen_substrate_contacts'].values())
    assert d['numerical_metadata']['converged_by_force'] is True


def test_proximal_h_tautomer_is_not_automatically_invalid():
    row = example()
    state(row)['positions_A'][-1] = [0,.98,2]
    assert detail(row)['H_nearest_adsorbate_O'] == 'proximal_O'
    assert detail(row)['exploratory_screen'] == 'no_flags'


def test_periodicity_controls_distance():
    row = example()
    for rec in geometries(row):
        rec['cell_A'] = np.diag([10.,10.,10.]).tolist()
        rec['pbc'] = [True,True,True]
    state(row)['positions_A'][-3:] = [[9.5,0,2],[.9,0,2],[.9,.98,2]]
    assert detail(row)['distances_A']['O_O_A'] == pytest.approx(1.4)
    for rec in geometries(row):
        rec['pbc'] = [False,False,False]
    assert detail(row)['distances_A']['O_O_A'] == pytest.approx(8.6)


def test_changed_cell_or_pbc_is_not_silently_compared_to_reference():
    row = example()
    state(row)['pbc'] = [True,False,False]
    assert detail(row)['geometry_status'] == 'invalid'


def test_triclinic_mic_against_explicit_lattice_enumeration():
    row = example()
    cell = np.array([[10.,0,0],[9.,2.,0],[0,0,20.]])
    delta = np.array([.49,.49,0]) @ cell
    prox = np.array([1.,1.,5.])
    for rec in geometries(row):
        rec['cell_A'] = cell.tolist()
        rec['pbc'] = [True,True,False]
    state(row)['positions_A'][-3:] = [prox.tolist(),(prox+delta).tolist(),(prox+delta+[0,0,.98]).tolist()]
    expected = min(np.linalg.norm(delta+np.array([i,j,0]) @ cell) for i,j in product(range(-3,4),repeat=2))
    assert detail(row)['distances_A']['O_O_A'] == pytest.approx(expected)
    assert expected < np.linalg.norm(delta)/5


def test_translation_invariance():
    row = example()
    baseline = detail(row)
    for rec in geometries(row):
        rec['positions_A'] = (np.asarray(rec['positions_A'])+[17.1,-8.4,3.3]).tolist()
    assert detail(row)['distances_A'] == pytest.approx(baseline['distances_A'])


def test_nearest_partner_change_and_ties_are_not_physical_migration_claims():
    row = example()
    state(row,'OH')['positions_A'][-2:] = [[5,0,2],[5,0,2.98]]
    b = analyze_adsorbate_geometry(row)['sites'][0]['binding_changes']
    assert b['cross_state_unique_partners_differ'] is True
    assert b['changed_nearest_index_states'] == ['OH']
    row = example()
    for rec in geometries(row):
        rec['positions_A'][:2] = [[-1,0,0],[1,0,0]]
    result = analyze_adsorbate_geometry(row)['sites'][0]
    assert result['states']['OOH']['oxygen_metal_contacts']['proximal_O']['nearest_indices'] == [0,1]
    assert result['binding_changes']['cross_state_unique_partners_differ'] is None


def test_two_oxygen_metal_contacts_are_not_automatic_failure():
    row = example()
    for rec in geometries(row):
        rec['positions_A'][1] = [1.4,0,0]
    d = detail(row)
    assert d['oxygens_have_different_unique_nearest_metals'] is True
    assert d['exploratory_screen'] == 'no_flags'


@pytest.mark.parametrize('key',['positions_A','symbols','cell_A','pbc'])
def test_missing_geometry_unknown(key):
    row = example()
    state(row).pop(key)
    result = analyze_adsorbate_geometry(row)
    assert result['sites'][0]['site_id'] == 'seed=0/site=0'
    assert result['sites'][0]['states']['OOH']['geometry_status'] == 'unknown'
    assert result['sites'][0]['binding_changes']['cross_state_unique_partners_differ'] is None


@pytest.mark.parametrize('change',[
    lambda r:r['positions_A'][-1].__setitem__(0,math.nan),
    lambda r:r['positions_A'][-1].__setitem__(0,True),
    lambda r:r.update(positions_A=[[0,0,0]]),
    lambda r:r.update(pbc=[1,0,0]),
    lambda r:r.update(cell_A=[[0,0,0]]*3,pbc=[True,False,False]),
    lambda r:r['symbols'].__setitem__(-1,'O'),
    lambda r:r['symbols'].__setitem__(0,'Fe'),
])
def test_invalid_geometry_fails_closed(change):
    row = example()
    change(state(row))
    assert detail(row)['geometry_status'] == 'invalid'
    assert detail(row)['exploratory_screen'] == 'unknown'
    json.dumps(analyze_adsorbate_geometry(row),allow_nan=False)


def test_missing_clean_reference_and_failed_force_remain_separate():
    row = example()
    state(row)['converged_by_force'] = False
    assert detail(row)['exploratory_screen'] == 'no_flags'
    assert detail(row)['numerical_metadata']['converged_by_force'] is False
    row['decoration_records'] = []
    assert analyze_adsorbate_geometry(row)['state_geometry_counts'] == {'observed':0,'unknown':3,'invalid':0}


def test_site_order_and_duplicate_identity():
    row = example()
    other = deepcopy(row['per_site_records'][0])
    other['site_index'] = 8
    other['relaxed_states'] = {}
    row['per_site_records'].insert(0,other)
    assert [s['site_id'] for s in analyze_adsorbate_geometry(row)['sites']] == ['seed=0/site=8','seed=0/site=0']
    row['per_site_records'].append(deepcopy(other))
    with pytest.raises(ValueError,match='duplicate site identity'):
        analyze_adsorbate_geometry(row)


def test_threshold_changes_flags_not_raw_distances():
    row = example()
    baseline = detail(row)
    changed = detail(row,thresholds=GeometryThresholds(oo_max_A=1.3))
    assert changed['distances_A'] == baseline['distances_A']
    assert 'O_O_above_exploratory_window' in changed['flags']


@pytest.mark.parametrize('values',[dict(oo_min_A=-1),dict(oo_max_A=math.inf),dict(oh_max_A=.6),dict(metal_contact_max_A=True),dict(nearest_tie_tolerance_A=1)])
def test_invalid_thresholds_rejected(values):
    with pytest.raises(ValueError):
        GeometryThresholds(**values)
