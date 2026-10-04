"""Raw-bound offline adapter tests; no process, scheduler or QE execution."""
import copy
import hashlib
import math
import os
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/dft"))
import pa_qe_adapter as adapter


PARALLEL = {"nprocs": 128, "nthreads": 1, "ntasks": 1,
            "nbgrp": 1, "npool": 8, "ndiag": 16}
CELL = [[10., 0., 0.], [2., 12., 0.], [0., 0., 20.]]
POSITIONS = [[0., 0., 0.], [0., 0., 2.]]
FLAGS = [[0, 1, 1], [1, 1, 1]]


def source_text():
    return """&CONTROL
 calculation = 'relax'
 prefix = 'probe'
 outdir = './scratch'
 pseudo_dir = './pseudo'
 tprnfor = .true.
 forc_conv_thr = 2.0d-3
 nstep = 200
 max_seconds = 165000
/
&SYSTEM
 ibrav = 0
 nat = 2
 ntyp = 1
 ecutwfc = 40.0
 ecutrho = 320.0
 nspin = 1
 occupations = 'fixed'
/
&ELECTRONS
 conv_thr = 1.0d-6
 mixing_beta = 0.3
 startingwfc = 'atomic+random'
 startingpot = 'file'
 electron_maxstep = 300
/
&IONS
 ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
H 1.00794 H.UPF
CELL_PARAMETERS bohr
10 0 0
2 12 0
0 0 20
ATOMIC_POSITIONS bohr
H 0 0 0 0 1 1
H 0 0 2 1 1 1
K_POINTS gamma
"""


def geometry(positions=None):
    return {"unit": "bohr", "species": ["H", "H"],
            "positions": copy.deepcopy(positions or POSITIONS), "cell": copy.deepcopy(CELL),
            "fixed_flags": [[1-v for v in row] for row in FLAGS]}


def structure(positions):
    return '<atomic_structure nat="2" alat="10">' + '<atomic_positions>' + ''.join(
        '<atom name="H" index="{}">{}</atom>'.format(i, ' '.join(map(str, row)))
        for i, row in enumerate(positions, 1)) + '</atomic_positions><cell>' + ''.join(
        '<a{}>{}</a{}>'.format(i, ' '.join(map(str, row)), i) for i, row in enumerate(CELL, 1)) + '</cell></atomic_structure>'


def species_xml():
    return '<atomic_species ntyp="1"><species name="H"><mass>1.00794</mass><pseudo_file>H.UPF</pseudo_file></species></atomic_species>'


def evaluated_xml(positions, energy, *, output=False):
    convergence = '<scf_conv><convergence_achieved>true</convergence_achieved></scf_conv>'
    if output:
        convergence = '<convergence_info>' + convergence + '</convergence_info>'
    return (convergence + structure(positions) + '<total_energy><etot>{:.17g}</etot></total_energy>'.format(energy/2)
            + '<forces rank="2" dims="3 2">0 0 .05 0 0 -.05</forces>')


def arm(tmp_path, name, *, kind="candidate", evaluations=1, energy=-100., start_cycle=1,
        positions=None):
    directory = tmp_path / name
    directory.mkdir()
    pseudo = tmp_path / 'H.UPF'
    if not pseudo.exists():
        pseudo.write_bytes(b'pinned hydrogen pseudopotential')
    source = tmp_path / 'source.in'
    if not source.exists():
        source.write_text(source_text(), encoding='utf-8')
    expected = adapter.parse_deck(source)
    expected['upf_pins'] = {'H.UPF': hashlib.sha256(pseudo.read_bytes()).hexdigest()}
    initial = copy.deepcopy(positions or POSITIONS)
    deck = adapter.render_trial_deck(source_text(), arm_kind=kind, prefix='probe',
                                     outdir=directory/'scratch', pseudo_dir=tmp_path,
                                     geometry=geometry(initial))
    infile = directory/'input.in'
    infile.write_text(deck, encoding='utf-8')
    points = [copy.deepcopy(initial) for _ in range(evaluations)]
    for i, point in enumerate(points):
        point[1][2] += i * .1
    proposal = copy.deepcopy(points[-1])
    proposal[1][2] += .1
    md5 = hashlib.md5(pseudo.read_bytes()).hexdigest()
    log = ('Program PWSCF v.7.5 starts\n'
           'Parallel version (MPI & OpenMP), running on 128 processor cores\n'
           'Number of MPI processes: 128\nThreads/MPI process: 1\n'
           'K-points division: npool = 8\n'
           'R & G space division: proc/nbgrp/npool/nimage = 16\n'
           'ELPA distributed-memory algorithm (size of sub-group: 4*4 procs)\n'
           'convergence threshold = 1.0E-6\n'
           'PseudoPot. # 1 for H read from file: ' + str(pseudo) + '\nMD5 check sum: ' + md5 + '\n')
    if kind in ('negative', 'negative-fresh'):
        log += 'probe.bfgs deleted, as requested\n'
    for i, point in enumerate(points):
        log += ('Self-consistent Calculation\n! total energy = {:.8f} Ry\n'.format(energy-i*.01)
                + 'Forces acting on atoms (cartesian axes, Ry/au):\n'
                + 'atom 1 type 1 force = 99.0 0.0 .1\natom 2 type 1 force = 0.0 0.0 -.1\n')
        if kind != 'fresh':
            cycle = start_cycle+i
            log += 'number of scf cycles = {}\nnumber of bfgs steps = {}\n'.format(cycle, cycle-1)
            next_point = points[i+1] if i+1 < evaluations else proposal
            log += 'ATOMIC_POSITIONS (bohr)\n' + ''.join('H '+ ' '.join(map(str, row)) + '\n' for row in next_point)
    log += ('Program stopped by user request\n' if kind != 'fresh' else '') + 'JOB DONE.\n'
    xml_input = ('<input><control_variables><calculation>{}</calculation><restart_mode>{}</restart_mode>'
                 '<prefix>probe</prefix><outdir>{}</outdir><pseudo_dir>{}</pseudo_dir><nstep>30</nstep>'
                 '<max_seconds>7080</max_seconds><forces>true</forces><forc_conv_thr>.001</forc_conv_thr></control_variables>').format(
                     'scf' if kind == 'fresh' else 'relax', 'restart' if kind == 'resumed' else 'from_scratch', directory/'scratch', tmp_path)
    xml_input += (species_xml()+structure(initial)+'<free_positions dims="3 2">0 1 1 1 1 1</free_positions>'
                  '<electron_control><conv_thr>5.0e-7</conv_thr><mixing_beta>.3</mixing_beta><max_nstep>300</max_nstep></electron_control>'
                  '<basis><gamma_only>true</gamma_only><ecutwfc>20</ecutwfc><ecutrho>160</ecutrho></basis>'
                  '<spin><lsda>false</lsda><noncolin>false</noncolin><spinorbit>false</spinorbit></spin>'
                  '<ion_control><ion_dynamics>bfgs</ion_dynamics></ion_control>'
                  '<bands><occupations>fixed</occupations></bands><k_points_IBZ><nk>1</nk></k_points_IBZ>'
                  '<dft><functional>PBE</functional></dft></input>')
    xml = ('<espresso Units="Hartree atomic units"><general_info><creator NAME="PWSCF" VERSION="7.5"/></general_info>'
           '<parallel_info>'+''.join('<{}>{}</{}>'.format(k, v, k) for k, v in PARALLEL.items())+'</parallel_info>'+xml_input)
    if kind == 'fresh':
        xml += '<output>'+evaluated_xml(points[0], energy, output=True)+species_xml()+'</output><exit_status>0</exit_status>'
    else:
        xml += ''.join('<step>'+evaluated_xml(point, energy-i*.01)+'</step>' for i, point in enumerate(points))
        xml += '<output>'+structure(proposal)+species_xml()+'</output><exit_status>255</exit_status>'
    xml += '</espresso>'
    (directory/'stdout.log').write_text(log, encoding='utf-8')
    (directory/'stderr.log').write_text('', encoding='utf-8')
    (directory/'data-file-schema.xml').write_text(xml, encoding='utf-8')
    return directory, expected


def parse_arm(directory, expected, count=1, fresh=False):
    return adapter.read_qe_arm(directory/'input.in', directory/'stdout.log', directory/'stderr.log',
                               directory/'data-file-schema.xml', {'returncode': 0, 'timed_out': False},
                               expected_settings=expected, expected_parallel=PARALLEL,
                               expected_exit='normal_scf' if fresh else 'clean_stop', expected_evaluations=count)


def checkpoint(tmp_path):
    out = tmp_path/'checkpoint'
    (out/'probe.save').mkdir(parents=True)
    (out/'probe.save'/'data-file-schema.xml').write_bytes(b'xml')
    (out/'probe.bfgs').write_bytes(b'full optimizer')
    (out/'sibling.update').write_bytes(b'update')
    (out/'empty').mkdir()
    wave = tmp_path/'wave'
    wave.mkdir()
    (wave/'wfc.dat').write_bytes(b'wfc')
    return out, wave


def decision_args(tmp_path, fresh=None):
    out, wave = checkpoint(tmp_path)
    before = adapter.checkpoint_inventory(out, wave)
    paths = {'restart_outdir': out, 'restart_wfcdir': wave,
             'fresh_outdir': fresh['input']['operations']['outdir'] if fresh else tmp_path/'isolated-fresh',
             'fresh_wfcdir': None}
    return before, paths


def test_constraints_are_inverted_per_coordinate_and_units_explicit(tmp_path):
    source = tmp_path/'source.in'
    source.write_text(source_text(), encoding='utf-8')
    record = adapter.parse_deck(source)
    assert record['geometry']['fixed_flags'] == [[1, 0, 0], [0, 0, 0]]
    assert record['qe_if_pos'] == FLAGS
    assert record['geometry']['cell'] == CELL
    assert record['conv_thr_Ry'] == 1e-6


@pytest.mark.parametrize('change', [
    lambda t: t.replace('conv_thr = 1.0d-6', 'conv_thr = 1.0d-6\n conv_thr = 1.0d-6'),
    lambda t: t.replace('ATOMIC_POSITIONS bohr', 'ATOMIC_POSITIONS crystal'),
    lambda t: t.replace('H 0 0 0 0 1 1', 'h 0 0 0 0 1 1'),
    lambda t: t.replace('H.UPF', '../H.UPF'),
    lambda t: t.replace('10 0 0', 'nan 0 0'),
    lambda t: t.replace('H 0 0 0 0 1 1', 'H 0 0 0 1 1'),
])
def test_malformed_source_fails_closed(tmp_path, change):
    source = tmp_path/'source.in'
    source.write_text(change(source_text()), encoding='utf-8')
    with pytest.raises(adapter.AdapterError):
        adapter.parse_deck(source)


def test_render_preserves_common_settings_and_declares_initialization(tmp_path):
    source = tmp_path/'source.in'
    source.write_text(source_text(), encoding='utf-8')
    baseline = adapter.parse_deck(source)
    for kind in ('control', 'resumed', 'negative', 'fresh', 'reseed'):
        rendered = tmp_path/(kind+'.in')
        rendered.write_text(adapter.render_trial_deck(source_text(), arm_kind=kind, prefix='probe',
                           outdir=tmp_path/kind, pseudo_dir=tmp_path, geometry=geometry()), encoding='utf-8')
        current = adapter.parse_deck(rendered)
        assert current['settings_identity'] == baseline['settings_identity']
        assert current['operations']['startingwfc'] == ('file' if kind == 'resumed' else 'atomic+random')
        assert current['operations']['startingpot'] == ('atomic' if kind == 'fresh' else 'file')


def test_raw_xml_energy_force_units_and_proposal_are_distinct(tmp_path):
    directory, expected = arm(tmp_path, 'candidate')
    record = parse_arm(directory, expected)
    assert record['evaluations'][0]['energy_Ry'] == -100.
    assert record['evaluations'][0]['forces_Ry_bohr'] == [[0., 0., .1], [0., 0., -.1]]
    assert record['proposal_geometry']['positions'] != record['evaluations'][0]['geometry']['positions']
    assert record['parallel'] == PARALLEL
    assert record['runtime_parallel']['elpa_subgroup'] == [4, 4]
    assert record['runtime_parallel']['matched_lines']['elpa_subgroup']['source']['line_start'] >= 1
    assert record['production_accepted'] is False
    assert record['evaluations'][0]['source']['line_start'] >= 1


@pytest.mark.parametrize('target,before,after', [
    ('data-file-schema.xml', 'Hartree atomic units', 'Ry units'),
    ('data-file-schema.xml', '<nprocs>128</nprocs>', '<nprocs>64</nprocs>'),
    ('data-file-schema.xml', '<mixing_beta>.3</mixing_beta>', '<mixing_beta>.1</mixing_beta>'),
    ('data-file-schema.xml', '<max_nstep>300</max_nstep>', '<max_nstep>301</max_nstep>'),
    ('data-file-schema.xml', '<functional>PBE</functional>', '<functional>RPBE</functional>'),
    ('data-file-schema.xml', '<lsda>false</lsda>', '<lsda>true</lsda>'),
    ('data-file-schema.xml', '<atom name="H" index="1">', '<atom name="h" index="1">'),
    ('data-file-schema.xml', '<forces rank="2" dims="3 2">0 0 .05', '<forces rank="2" dims="3 2">0 0 .5'),
    ('data-file-schema.xml', '<exit_status>255</exit_status>', '<exit_status>0</exit_status>'),
    ('stdout.log', 'JOB DONE.', 'missing'),
    ('stdout.log', 'Program stopped by user request', 'bfgs converged in 1'),
    ('stdout.log', 'MD5 check sum:', 'missing checksum:'),
    ('stdout.log', 'Number of MPI processes: 128', 'Number of MPI processes: 64'),
    ('stdout.log', 'Threads/MPI process: 1', 'Threads/MPI process: 2'),
    ('stdout.log', 'running on 128 processor cores', 'running on 64 processor cores'),
    ('stdout.log', 'K-points division: npool = 8', 'K-points division: npool = 4'),
    ('stdout.log', 'proc/nbgrp/npool/nimage = 16', 'proc/nbgrp/npool/nimage = 32'),
    ('stdout.log', 'size of sub-group: 4*4 procs', 'size of sub-group: 2*2 procs'),
    ('stdout.log', 'ELPA distributed-memory algorithm (size of sub-group: 4*4 procs)', 'missing ELPA subgroup'),
    ('stdout.log', 'H 0.0 0.0 2.1', 'H 0.0 0.0 2.2'),
])
def test_raw_adversaries_reject_invalid_arm(tmp_path, target, before, after):
    directory, expected = arm(tmp_path, 'candidate')
    file = directory/target
    text = file.read_text(encoding='utf-8')
    assert before in text
    file.write_text(text.replace(before, after), encoding='utf-8')
    with pytest.raises(adapter.AdapterError):
        parse_arm(directory, expected)


def test_full_snapshot_and_copy_preserve_distinct_wfc_and_empty_directories(tmp_path):
    out, wave = checkpoint(tmp_path)
    saved = adapter.snapshot_checkpoint(out, tmp_path/'immutable', wfcdir=wave)
    cloned = adapter.copy_checkpoint(saved, tmp_path/'resume-out', wfcdir=tmp_path/'resume-wave')
    assert saved['content_sha256'] == cloned['content_sha256']
    assert (tmp_path/'resume-out'/'empty').is_dir()
    assert {r['path'] for r in cloned['inventory']['outdir']['files']} == {
        'probe.save/data-file-schema.xml', 'probe.bfgs', 'sibling.update'}
    with pytest.raises(adapter.AdapterError):
        adapter.copy_checkpoint(saved, tmp_path/'resume-out', wfcdir=tmp_path/'again-wave')
    (Path(saved['snapshot']['outdir'])/'sibling.update').write_bytes(b'drift')
    with pytest.raises(adapter.AdapterError):
        adapter.copy_checkpoint(saved, tmp_path/'other-out', wfcdir=tmp_path/'other-wave')


def test_snapshot_refuses_overlap_and_symlink(tmp_path):
    out, wave = checkpoint(tmp_path)
    with pytest.raises(adapter.AdapterError):
        adapter.snapshot_checkpoint(out, out/'child', wfcdir=wave)
    try:
        (out/'link').symlink_to(out/'probe.bfgs')
    except (OSError, NotImplementedError):
        pytest.skip('platform does not permit filesystem symlinks')
    with pytest.raises((adapter.AdapterError, ValueError)):
        adapter.snapshot_checkpoint(out, tmp_path/'immutable', wfcdir=wave)


@pytest.mark.parametrize('alias_location', ['outdir', 'wfcdir', 'outside'])
def test_checkpoint_inventory_and_snapshot_refuse_hardlink_aliases(tmp_path, alias_location):
    out, wave = checkpoint(tmp_path)
    alias = {'outdir': out/'alias', 'wfcdir': wave/'alias',
             'outside': tmp_path/'external-alias'}[alias_location]
    try:
        os.link(str(out/'sibling.update'), str(alias))
    except (OSError, NotImplementedError):
        pytest.skip('platform does not permit filesystem hardlinks')
    with pytest.raises(adapter.AdapterError, match='hardlink|inode alias'):
        adapter.checkpoint_inventory(out, wave)
    destination = tmp_path/'immutable'
    with pytest.raises(adapter.AdapterError, match='hardlink|inode alias'):
        adapter.snapshot_checkpoint(out, destination, wfcdir=wave)
    assert not destination.exists()


def test_checkpoint_copy_refuses_external_hardlink_to_immutable_source(tmp_path):
    out, wave = checkpoint(tmp_path)
    saved = adapter.snapshot_checkpoint(out, tmp_path/'immutable', wfcdir=wave)
    try:
        os.link(str(Path(saved['snapshot']['outdir'])/'sibling.update'), str(tmp_path/'external-alias'))
    except (OSError, NotImplementedError):
        pytest.skip('platform does not permit filesystem hardlinks')
    destination = tmp_path/'resumed'
    with pytest.raises(adapter.AdapterError, match='hardlink|inode alias'):
        adapter.copy_checkpoint(saved, destination, wfcdir=tmp_path/'resumed-wave')
    assert not destination.exists()


def test_public_snapshot_rechecks_opened_file_link_count(tmp_path, monkeypatch):
    from types import SimpleNamespace
    out, wave = checkpoint(tmp_path)
    original = os.fstat
    def raced_file(descriptor):
        info = original(descriptor)
        return SimpleNamespace(st_mode=info.st_mode, st_dev=info.st_dev,
                               st_ino=info.st_ino, st_nlink=2)
    monkeypatch.setattr(adapter.os, 'fstat', raced_file)
    with pytest.raises(adapter.AdapterError, match='opened checkpoint file'):
        adapter.snapshot_checkpoint(out, tmp_path/'immutable', wfcdir=wave)


@pytest.mark.skipif(sys.platform == 'win32', reason='POSIX FIFO fixture')
def test_special_checkpoint_file_is_refused(tmp_path):
    import os
    out, wave = checkpoint(tmp_path)
    os.mkfifo(str(out/'special'))
    with pytest.raises((adapter.AdapterError, ValueError)):
        adapter.snapshot_checkpoint(out, tmp_path/'immutable', wfcdir=wave)


@pytest.mark.parametrize('drop,action', [(0., 'RESUME_CANDIDATE'), (-20., 'RESUME_CANDIDATE'),
                                         (10., 'RESUME_CANDIDATE'), (10.001, 'RESEED_CANDIDATE')])
def test_predecision_is_one_sided_and_never_accepts_before_resume(tmp_path, drop, action):
    candidate_dir, expected = arm(tmp_path, 'candidate')
    fresh_dir, _ = arm(tmp_path, 'fresh', kind='fresh', energy=-100.-drop/adapter.RY_MEV)
    candidate, fresh = parse_arm(candidate_dir, expected), parse_arm(fresh_dir, expected, fresh=True)
    before, paths = decision_args(tmp_path, fresh)
    result = adapter.pre_resume_decision(candidate, fresh, before, before, scratch_paths=paths)
    assert result['action'] == action
    assert result['production_accepted'] is False
    wanted = candidate['proposal_geometry'] if action == 'RESUME_CANDIDATE' else candidate['evaluations'][0]['geometry']
    assert result['next_geometry'] == wanted


def test_missing_failed_fresh_and_caps_hold_without_resume(tmp_path):
    candidate_dir, expected = arm(tmp_path, 'candidate')
    candidate = parse_arm(candidate_dir, expected)
    before, paths = decision_args(tmp_path)
    assert adapter.pre_resume_decision(candidate, None, before, before, scratch_paths=paths)['action'] == 'HOLD'
    fresh_dir, _ = arm(tmp_path, 'fresh', kind='fresh')
    fresh = parse_arm(fresh_dir, expected, fresh=True)
    paths['fresh_outdir'] = fresh['input']['operations']['outdir']
    assert adapter.pre_resume_decision(candidate, fresh, before, before, scratch_paths=paths,
                                       remaining_segments=0)['action'] == 'HOLD'
    fresh['evaluations'][0]['energy_Ry'] -= .01
    with pytest.raises(adapter.AdapterError, match='modified'):
        adapter.pre_resume_decision(candidate, fresh, before, before, scratch_paths=paths)


def test_immutable_checkpoint_and_raw_source_drift_cannot_pass(tmp_path):
    candidate_dir, expected = arm(tmp_path, 'candidate')
    fresh_dir, _ = arm(tmp_path, 'fresh', kind='fresh')
    candidate, fresh = parse_arm(candidate_dir, expected), parse_arm(fresh_dir, expected, fresh=True)
    before, paths = decision_args(tmp_path, fresh)
    (Path(before['outdir']['root'])/'sibling.update').write_bytes(b'drift')
    after = adapter.checkpoint_inventory(paths['restart_outdir'], paths['restart_wfcdir'])
    assert adapter.pre_resume_decision(candidate, fresh, before, after, scratch_paths=paths)['action'] == 'HOLD'
    (Path(before['outdir']['root'])/'sibling.update').write_bytes(b'update')
    (fresh_dir/'stdout.log').write_text('changed after parsing', encoding='utf-8')
    with pytest.raises(adapter.AdapterError, match='drifted'):
        adapter.pre_resume_decision(candidate, fresh, before, before, scratch_paths=paths)


def optimizer_values():
    """A complete ndim1 state with a nonzero inverse metric and NR step.

    QE initializes inv_hess=inv_metric.  The active 3x3 metric is the Gram
    matrix of CELL; its inverse and the inactive cell/FCP metric blocks remain
    positive even though inactive position/gradient slots are zero.
    """
    dimension = 16
    values = [0.] * (dimension*dimension+4*dimension+6)
    gram = [[sum(a*b for a, b in zip(left, right)) for right in CELL] for left in CELL]
    inverse = [[148./14400., -20./14400., 0.],
               [-20./14400., 100./14400., 0.], [0., 0., 1./400.]]
    hessian = [[0.] * dimension for _ in range(dimension)]
    for atom in range(2):
        for i in range(3):
            for j in range(3):
                hessian[3*atom+i][3*atom+j] = inverse[i][j]
    for block in range(3):
        for i in range(3):
            for j in range(3):
                hessian[6+3*block+i][6+3*block+j] = gram[i][j]/96.
    hessian[-1][-1] = 1.
    first = 4*dimension+4
    values[first:first+dimension*dimension] = [hessian[i][j] for j in range(dimension) for i in range(dimension)]
    values[-1] = math.sqrt(2.)*.1
    return values


def test_saved_fractional_state_uses_full_nonorthogonal_cell(tmp_path):
    dimension = 16
    values = optimizer_values()
    values[3:6] = [.2, .25, .1]
    values[dimension+3:dimension+6] = [-1., -2.6, -6.]
    values[2*dimension:2*dimension+4] = [1., 1., 0., -100.]
    values[-1] = math.sqrt(.14)
    path = tmp_path/'probe.bfgs'
    path.write_text(' '.join(map(str, values)), encoding='utf-8')
    evaluated = {'geometry': geometry([[0., 0., 0.], [2.5, 3., 2.]]), 'energy_Ry': -100.,
                 'forces_Ry_bohr': [[0., 0., 0.], [.1, .2, .3]]}
    record = adapter.read_bfgs(path, nat=2, cell_bohr=CELL, evaluated=evaluated)
    assert record['prior_positions_bohr'][1] == [2.5, 3., 2.]
    assert record['scf_count'] == record['bfgs_count'] == 1
    assert record['prior_fractional_gradient_Ry'][1] == [-1., -2.6, -6.]
    assert record['nr_step_length_bohr'] > 0
    assert record['inactive_tail_max_abs'] == 0
    with pytest.raises(adapter.AdapterError):
        adapter.read_bfgs(path, nat=3, cell_bohr=CELL)


def saved_history(path):
    dimension = 16
    values = optimizer_values()
    values[5] = .1
    values[dimension+2] = -2.
    values[dimension+5] = 2.
    values[2*dimension:2*dimension+4] = [1., 1., 0., -100.]
    path.write_text(' '.join(map(str, values)), encoding='utf-8')


@pytest.mark.parametrize('length', [0., -1., 1e-17])
def test_saved_optimizer_requires_source_positive_step_length(tmp_path, length):
    values = optimizer_values()
    values[-1] = length
    path = tmp_path/'probe.bfgs'
    path.write_text(' '.join(map(str, values)), encoding='utf-8')
    with pytest.raises(adapter.AdapterError, match='step length'):
        adapter.read_bfgs(path, nat=2, cell_bohr=CELL)


@pytest.mark.parametrize('offset', [6, 16+6, 2*16+4+6, 3*16+4+6])
def test_saved_optimizer_rejects_inactive_current_and_history_tails(tmp_path, offset):
    values = optimizer_values()
    values[offset] = 1e-10
    path = tmp_path/'probe.bfgs'
    path.write_text(' '.join(map(str, values)), encoding='utf-8')
    with pytest.raises(adapter.AdapterError, match='inactive cell/FCP'):
        adapter.read_bfgs(path, nat=2, cell_bohr=CELL)


def test_observed_resume_consumption_is_separate_and_requires_raw_history(tmp_path):
    candidate_dir, expected = arm(tmp_path, 'candidate')
    fresh_dir, _ = arm(tmp_path, 'fresh', kind='fresh')
    candidate, fresh = parse_arm(candidate_dir, expected), parse_arm(fresh_dir, expected, fresh=True)
    before, paths = decision_args(tmp_path, fresh)
    saved_path = Path(before['outdir']['root'])/'probe.bfgs'
    saved_history(saved_path)
    before = adapter.checkpoint_inventory(paths['restart_outdir'], paths['restart_wfcdir'])
    saved = adapter.read_bfgs(saved_path, nat=2, cell_bohr=CELL, evaluated=candidate['evaluations'][0])
    resume_dir, _ = arm(tmp_path, 'resumed', kind='resumed', evaluations=2, start_cycle=2,
                        positions=candidate['proposal_geometry']['positions'])
    resume = parse_arm(resume_dir, expected, 2)
    result = adapter.audit_consumption(candidate, fresh, saved, resume, before, before, scratch_paths=paths)
    assert result['action'] == 'ACCEPT'
    assert result['production_accepted'] is False
    assert result['raw_consumption_audit']['passed'] is True
    copied = copy.deepcopy(saved)
    copied['scf_count'] = 2
    with pytest.raises(adapter.AdapterError):
        adapter.audit_consumption(candidate, fresh, copied, resume, before, before, scratch_paths=paths)
    log = (resume_dir/'stdout.log').read_text(encoding='utf-8')
    (resume_dir/'stdout.log').write_text(log.replace('convergence threshold', 'probe.bfgs deleted, as requested\nconvergence threshold'), encoding='utf-8')
    reset = parse_arm(resume_dir, expected, 2)
    with pytest.raises(adapter.AdapterError, match='consume'):
        adapter.audit_consumption(candidate, fresh, saved, reset, before, before, scratch_paths=paths)


def test_three_evaluation_trajectory_requires_every_ordered_record(tmp_path):
    directory, expected = arm(tmp_path, 'control', kind='control', evaluations=3)
    frames = parse_arm(directory, expected, 3)['evaluations']
    assert adapter.compare_trajectories(frames, copy.deepcopy(frames))['within_tolerances']
    wrong = copy.deepcopy(frames)
    wrong[1]['energy_Ry'] += .00001
    assert not adapter.compare_trajectories(frames, wrong)['within_tolerances']
    with pytest.raises(adapter.AdapterError):
        adapter.compare_trajectories(frames, wrong[:2])
    with pytest.raises(adapter.AdapterError):
        adapter.compare_trajectories(frames, list(reversed(frames))[:2])


def scientific_arm(tmp_path):
    directory, old_expected = arm(tmp_path, 'science')
    scientific_source = (source_text().replace('nspin = 1', 'nspin = 2\n starting_magnetization(1) = .4\n nosym = .true.\n noinv = .true.')
                         .replace("occupations = 'fixed'", "occupations = 'smearing'\n smearing = 'mv'\n degauss = .01")
                         .replace('K_POINTS gamma', 'K_POINTS automatic\n4 2 1 0 0 0\nHUBBARD (atomic)\nU H-1s 3.32'))
    source = tmp_path/'scientific-source.in'
    source.write_text(scientific_source, encoding='utf-8')
    expected = adapter.parse_deck(source)
    expected['upf_pins'] = old_expected['upf_pins']
    (directory/'input.in').write_text(adapter.render_trial_deck(scientific_source, arm_kind='candidate', prefix='probe',
                                         outdir=directory/'scratch', pseudo_dir=tmp_path, geometry=geometry()), encoding='utf-8')
    xml_path = directory/'data-file-schema.xml'
    xml = xml_path.read_text(encoding='utf-8')
    xml = (xml.replace('<mass>1.00794</mass>', '<mass>1.00794</mass><starting_magnetization>.4</starting_magnetization>')
           .replace('<gamma_only>true</gamma_only>', '<gamma_only>false</gamma_only>')
           .replace('<lsda>false</lsda>', '<lsda>true</lsda>')
           .replace('<occupations>fixed</occupations>', '<occupations>smearing</occupations><smearing degauss=".005">mv</smearing>')
           .replace('<k_points_IBZ><nk>1</nk></k_points_IBZ>', '<k_points_IBZ><monkhorst_pack nk1="4" nk2="2" nk3="1" k1="0" k2="0" k3="0"/></k_points_IBZ>')
           .replace('<dft><functional>PBE</functional></dft>', '<dft><functional>PBE</functional><dftU new_format="true">'
                    '<lda_plus_u_kind>0</lda_plus_u_kind><U_projection_type>atomic</U_projection_type>'
                    '<Hubbard_U specie="H" label="1s">{:.17g}</Hubbard_U></dftU></dft>'.format(3.32/(2*adapter.RY_EV)))
           .replace('</input>', '<symmetry_flags><nosym>true</nosym><noinv>true</noinv></symmetry_flags></input>'))
    xml_path.write_text(xml, encoding='utf-8')
    return directory, expected


def test_scientific_source_xml_hubbard_units_smearing_grid_and_magnetic_start(tmp_path):
    directory, expected = scientific_arm(tmp_path)
    raw = parse_arm(directory, expected)
    assert raw['settings_identity'] == expected['settings_identity']
    assert raw['input']['settings']['hubbard']['rows'] == [['U', 'H-1s', '3.32']]


@pytest.mark.parametrize('before,after', [
    ('<U_projection_type>atomic</U_projection_type>', '<U_projection_type>ortho-atomic</U_projection_type>'),
    ('label="1s"', 'label="2s"'),
    ('specie="H"', 'specie="Co"'),
    ('<lda_plus_u_kind>0</lda_plus_u_kind>', '<lda_plus_u_kind>1</lda_plus_u_kind>'),
    ('<starting_magnetization>.4</starting_magnetization>', '<starting_magnetization>.5</starting_magnetization>'),
    ('degauss=".005"', 'degauss=".01"'),
    ('>mv</smearing>', '>gaussian</smearing>'),
    ('>mv</smearing>', '>cold</smearing>'),
    ('nk1="4"', 'nk1="3"'),
    ('k1="0"', 'k1="1"'),
    ('<noinv>true</noinv>', '<noinv>false</noinv>'),
])
def test_physical_xml_changes_cannot_hide_behind_matching_deck_hash(tmp_path, before, after):
    directory, expected = scientific_arm(tmp_path)
    path = directory/'data-file-schema.xml'
    original = path.read_text(encoding='utf-8')
    assert before in original
    path.write_text(original.replace(before, after), encoding='utf-8')
    with pytest.raises(adapter.AdapterError):
        parse_arm(directory, expected)


def test_initial_four_file_seed_is_never_full_restart(tmp_path):
    source = tmp_path/'seed'
    source.mkdir()
    pins = {}
    for filename in adapter.SEED_FILES:
        (source/filename).write_bytes(filename.encode('ascii'))
        pins[filename] = hashlib.sha256((source/filename).read_bytes()).hexdigest()
    result = adapter.seed_initialization(source, tmp_path/'initial.save', pins)
    assert result['full_restart_checkpoint'] is False
    assert result['kind'] == 'INITIAL_ELECTRONIC_DENSITY_ONLY'
    assert {p.name for p in (tmp_path/'initial.save').iterdir()} == adapter.SEED_FILES
    with pytest.raises(adapter.AdapterError):
        adapter.seed_initialization(source, tmp_path/'initial.save', pins)


@pytest.mark.parametrize('source,canonical', [
    ('mv', 'mv'), ('cold', 'mv'), ('Marzari-Vanderbilt', 'mv'),
    ('MP', 'mp'), ('Gaussian', 'gaussian'), ('F-D', 'fd'),
])
def test_official_schema_smearing_canonical_aliases(source, canonical):
    assert adapter._schema_smearing(source) == canonical


def test_terminal_cleanup_is_distinct_from_startup_reset(tmp_path):
    directory, expected = arm(tmp_path, 'candidate')
    log = directory/'stdout.log'
    log.write_text(log.read_text(encoding='utf-8')+'probe.bfgs deleted, as requested\n', encoding='utf-8')
    raw = parse_arm(directory, expected)
    assert raw['startup_history_deleted'] is False
    negative, _ = arm(tmp_path, 'negative', kind='negative')
    reset = parse_arm(negative, expected)
    assert reset['startup_history_deleted'] is True
    assert reset['optimizer_counts'][0] == 0


def test_retained_one_process_serial_shape_does_not_require_catalyst_elpa(tmp_path):
    directory, expected = arm(tmp_path, 'serial')
    log_path = directory/'stdout.log'
    log = log_path.read_text(encoding='utf-8')
    log = (log.replace('running on 128 processor cores', 'running on 1 processor cores')
           .replace('Number of MPI processes: 128', 'Number of MPI processes: 1')
           .replace('K-points division: npool = 8\n', '')
           .replace('R & G space division: proc/nbgrp/npool/nimage = 16\n', '')
           .replace('ELPA distributed-memory algorithm (size of sub-group: 4*4 procs)', 'a serial algorithm will be used'))
    log_path.write_text(log, encoding='utf-8')
    xml_path = directory/'data-file-schema.xml'
    xml = xml_path.read_text(encoding='utf-8')
    for key, value in PARALLEL.items():
        xml = xml.replace('<{0}>{1}</{0}>'.format(key, value), '<{0}>1</{0}>'.format(key))
    xml_path.write_text(xml, encoding='utf-8')
    raw = adapter.read_qe_arm(directory/'input.in', log_path, directory/'stderr.log', xml_path,
                              {'returncode': 0, 'timed_out': False}, expected_settings=expected,
                              expected_parallel={key: 1 for key in PARALLEL}, expected_evaluations=1)
    assert raw['runtime_parallel']['diagonalization_algorithm'] == 'serial'
    assert raw['runtime_parallel']['elpa_subgroup'] is None
    assert raw['runtime_parallel']['npool'] == 1
    assert set(raw['runtime_parallel']['inferred_serial_defaults']) == {'npool', 'proc_per_band_pool_image'}
