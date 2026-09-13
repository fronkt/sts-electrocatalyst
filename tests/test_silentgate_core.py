"""Scientific behavior, including incomplete data and the elected ALL quantifier."""
from silentgate.classify import classify

def record(steps, **extra):
    return dict(force_steps=steps,adsorbate_indices=[1,2],unidentified=False,n_symops=2,forc_conv_thr=.001,**extra)

def test_all_atoms_and_steps_are_required_for_one_common_axis():
    r=classify(record([{1:[1.,0.,2.],2:[0.,1.,2.]}]))
    assert r['locked_force_only'] is False and r['locked_axes']==[]
    r=classify(record([{1:[1.,-0.,2.],2:[1.,0.,2.]},{1:[1.,0.,2.],2:[1.,1e-12,2.]}]))
    assert r['locked_force_only'] is False

def test_signed_zero_and_both_lateral_axes():
    r=classify(record([{1:[-0.,0.,2.],2:[0.,-0.,2.]}]))
    assert r['locked_axes']==['x','y'] and r['verdict']=='LOCKED'

def test_missing_atom_or_step_is_unscorable_not_negative():
    for steps in [[],[{1:[1.,0.,2.]}],[{1:[1.,0.,2.],2:[1.,0.,2.]},{}]]:
        r=classify(record(steps))
        assert r['verdict']=='unscorable' and r['locked_force_only'] is None

def test_no_symmetry_can_disagree_with_force_only():
    raw=record([{1:[1.,0.,2.],2:[1.,0.,2.]}]);raw['n_symops']=1
    r=classify(raw)
    assert r['locked_force_only'] is True and r['locked_two_witness'] is False
    assert r['witness_disagreement'] is True
    assert r['directions']['y']['classification']=='ON_PLANE'

def test_noise_floor_boundary_is_explored_but_tiny_nonzero_is_not_locked():
    r=classify(record([{1:[.001/20,1e-8,2.],2:[.001/20,1e-8,2.]}]))
    assert r['directions']['x']['classification']=='EXPLORED'
    assert not r['locked_force_only']

def test_unknown_header_does_not_manufacture_two_witness_evidence():
    raw=record([{1:[1.,0.,2.],2:[1.,0.,2.]}]);raw['n_symops']=None
    r=classify(raw)
    assert r['locked_two_witness'] is None and r['unscorable']
    assert classify(raw,force_only=True)['verdict']=='LOCKED'

def test_nonfinite_forces_and_parser_failures_remain_unscorable():
    r=classify(record([{1:[float('nan'),0.,2.],2:[1.,0.,2.]}]))
    assert r['unscorable']
    r=classify(record([{1:[1.,0.,2.],2:[1.,0.,2.]}],force_issues=['truncated block']))
    assert r['locked_force_only'] is None


def test_any_atom_negative_control_is_distinct_from_all_atom_run_rule():
    r=classify(record([{1:[1.,0.,2.],2:[0.,1.,2.]}]))
    assert r['locked_force_only'] is False
    assert r['locked_any_atom_force_only'] is True
    assert r['per_atom_directions']['1']['y']['exact_zero_every_step_all_atoms']

def test_oc20_force_only_has_no_noise_floor_or_on_plane_label():
    raw=record([{1:[1.,1e-10,2.],2:[1.,1e-10,2.]}]);raw['n_symops']=None
    r=classify(raw,force_only=True)
    assert r['noise_floor'] is None
    assert r['directions']['y']['classification']=='not-LOCKED'
