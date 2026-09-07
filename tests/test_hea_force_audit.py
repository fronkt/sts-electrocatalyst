"""Failure cases for fixed-geometry SCF forces, including Cartesian constraints."""
from pathlib import Path
import pytest
from dft.hea_force_audit import audit_text, audit_files, RY_BOHR_TO_EV_A

IN = """&CONTROL
 calculation='scf'
/
&SYSTEM
 nat=2
/
ATOMIC_SPECIES
 O 15.999 O.UPF
 H 1.008 H.UPF
ATOMIC_POSITIONS angstrom
 O 0 0 0 0 0 0
 H 0 0 1 0 0 1
K_POINTS gamma
"""
OUT = """number of atoms/cell = 2
! total energy = -2.0D+01 Ry
convergence has been achieved in 3 iterations
Forces acting on atoms (cartesian axes, Ry/au):
 atom 1 type 1 force = 1.0 2.0 3.0
 atom 2 type 2 force = 9.0 9.0 1.0D-03
 Total force = 9.9
 JOB DONE.
"""


def test_cartesian_mask_and_units():
    r = audit_text(IN, OUT)
    assert r['status'] == 'VALID_SCF'
    assert r['geometry_stationarity'] == 'WITHIN_THRESHOLD'
    assert r['fmax_free_ev_A'] == pytest.approx(0.001 * RY_BOHR_TO_EV_A)
    assert r['fmax_all_ev_A'] > 300
    assert r['n_free_components'] == 1
    assert r['per_atom'][1]['free_force_ev_A'][:2] == [0, 0]


def test_force_is_geometry_diagnostic_not_bad_scf():
    r = audit_text(IN, OUT.replace('1.0D-03', '0.1'))
    assert r['status'] == 'VALID_SCF'
    assert r['geometry_stationarity'] == 'ABOVE_THRESHOLD'


@pytest.mark.parametrize('term', ['convergence NOT achieved', 'Program stopped by user request',
                                 'Maximum CPU time exceeded', 'Error in routine', 'MPI_ABORT'])
def test_failure_overrides_job_done(term):
    assert audit_text(IN, OUT + term)['status'] == 'REJECTED'


@pytest.mark.parametrize('out', [OUT + OUT, OUT.replace('atom 2', 'atom 1'),
    OUT.replace('type 2', 'type 1'), OUT.replace('1.0D-03', 'NaN'),
    OUT.replace(' atom 2 type 2 force = 9.0 9.0 1.0D-03\n', ''),
    OUT.replace('Total force', 'Missing force'), OUT.replace('cell = 2', 'cell = 3'),
    OUT.replace('convergence has been achieved in 3 iterations', ''),
    OUT.replace('convergence has been achieved in 3 iterations\n', '') +
      'convergence has been achieved in 3 iterations'])
def test_ambiguous_or_malformed_completed_output_rejected(out):
    assert audit_text(IN, out)['status'] == 'REJECTED'


def test_pending_output():
    assert audit_text(IN, None)['status'] == 'PENDING'
    assert audit_text(IN, OUT.replace('JOB DONE.', ''))['status'] == 'PENDING'


@pytest.mark.parametrize('deck', [IN.replace("'scf'", "'relax'"), IN.replace('0 0 1\n', '0 2 1\n'),
    IN.replace('nat=2', 'nat=3'), IN.replace('H 0 0 1', 'H nan 0 1')])
def test_bad_input_is_not_silently_assumed_all_free(deck):
    with pytest.raises(ValueError):
        audit_text(deck, OUT)


def test_all_fixed_is_not_stationary_claim():
    r = audit_text(IN.replace('H 0 0 1 0 0 1', 'H 0 0 1 0 0 0'), OUT)
    assert r['geometry_stationarity'] == 'NO_FREE_COORDINATES'
    assert r['fmax_free_ev_A'] is None


def test_no_flags_means_all_free_and_comments_ignored():
    r = audit_text(IN.replace('0 0 0 0 0 0', '0 0 0 ! fixed flags omitted')
                  .replace('0 0 1 0 0 1', '0 0 1'), OUT)
    assert r['n_free_components'] == 6
    assert r['fmax_free_ev_A'] == r['fmax_all_ev_A']


def test_files_record_identity_and_missing_output(tmp_path):
    inp = tmp_path / 'sample.in'
    inp.write_text(IN)
    r = audit_files(inp, tmp_path / 'sample.out')
    assert len(r['input']['sha256_bytes']) == 64
    assert r['output']['sha256_bytes'] is None


@pytest.mark.parametrize('threshold', [0, -1, float('nan'), float('inf'), True])
def test_invalid_threshold(threshold):
    with pytest.raises(ValueError):
        audit_text(IN, OUT, threshold)


def test_ambiguous_calculation_assignments_rejected():
    with pytest.raises(ValueError):
        audit_text(IN.replace("calculation='scf'", "calculation='scf'\ncalculation='relax'"), OUT)
