"""Regression tests for the QC gate that guards every energy in this project.

`qe_qc` exists because pw.x prints "JOB DONE." on runs that produced nothing usable.
Three distinct ways that has happened here, each of which cost real analysis:

  1. SCF failure  -- "convergence NOT achieved ... stopping" then JOB DONE.
     Cost: eta(NiO2) = 1.751 V was published internally, then retracted (docs/30),
     and with it the docs/29 s4b "NiO2 breaks *OOH/*OH scaling" claim.
  2. nstep exhaustion -- relax hits `nstep` and stops with un-relaxed geometry.
  3. User stop -- a `<outdir>/<prefix>.EXIT` flag makes pw.x quit gracefully and
     still print JOB DONE. Found 2026-07-31 stopping a stalled Ni job on purpose;
     the queue logged `rc=0 JOB_DONE=1 SCF_FAIL=0` for it.

Mode 3 also revealed that `n_ionic == 0` was buying a TRUSTWORTHY verdict on a file
with a null energy. That clause is only meant to admit genuine scf-only runs, so the
tests below pin BOTH directions: a real scf-only gas reference must still pass, and a
relax killed inside ionic step 1 must not.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dft import qe_qc  # noqa: E402

BANNER = """
     Program PWSCF v.7.5 starts on 31Jul2026 at 12: 0: 0
     number of atoms/cell      =            4
"""
JOB_DONE = """
=------------------------------------------------------------------------------=
   JOB DONE.
=------------------------------------------------------------------------------=
"""


def _force_block(forces, total):
    """A 'Forces acting on atoms' block; pw.x prints these UNCONSTRAINED."""
    out = ["", "     Forces acting on atoms (cartesian axes, Ry/au):", ""]
    for i, (fx, fy, fz) in enumerate(forces, 1):
        out.append(f"     atom    {i} type  1   force =    {fx:.8f}   {fy:.8f}   {fz:.8f}")
    out.append("")
    out.append(f"     Total force =    {total:.6f}     Total SCF correction =     0.000001")
    return "\n".join(out)


def _scf_ok(energy):
    return (f"\n     convergence has been achieved in  12 iterations\n"
            f"\n!    total energy              =   {energy:.8f} Ry\n")


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8", newline="\n")
    return str(p)


# input with 4 atoms, bottom 2 frozen (if_pos 0 0 0) -- the slab convention here
INPUT_FROZEN_BOTTOM = """&CONTROL
  calculation = 'relax'
/
ATOMIC_POSITIONS crystal
Ru  0.0 0.0 0.10  0 0 0
Ru  0.5 0.5 0.20  0 0 0
O   0.0 0.5 0.70
O   0.5 0.0 0.80
K_POINTS automatic
 4 4 1 0 0 0
"""


# --------------------------------------------------------------------------- masks
def test_free_mask_reads_if_pos_and_stops_at_next_card(tmp_path):
    inp = _write(tmp_path, "j.in", INPUT_FROZEN_BOTTOM)
    assert qe_qc.free_mask(inp) == [False, False, True, True]


def test_free_mask_none_when_input_absent(tmp_path):
    assert qe_qc.free_mask(str(tmp_path / "nope.in")) is None


# ------------------------------------------------------------------- happy paths
def test_converged_relax_is_trustworthy(tmp_path):
    txt = (BANNER + _scf_ok(-100.5) + _force_block(
        [(0, 0, 0.0), (0, 0, 0.0), (0.0, 0.0, 0.0009), (0.0, 0.0, -0.0011)], 0.0014)
        + "\n     bfgs converged in  12 scf cycles and  11 bfgs steps\n"
        + "     Final energy   =    -100.50000000 Ry\n" + JOB_DONE)
    out = _write(tmp_path, "j.out", txt)
    _write(tmp_path, "j.in", INPUT_FROZEN_BOTTOM)
    rec = qe_qc.scan(out, str(tmp_path / "j.in"))
    assert rec["verdict"] == "TRUSTWORTHY", rec["reasons"]
    assert qe_qc.trusted_energy_ev(out) == pytest.approx(-100.5 * qe_qc.RY_EV)


def test_genuine_scf_only_run_still_passes(tmp_path):
    """The H2/H2O gas references are calculation='scf': no ionic steps, no BFGS line.

    This is the case the `n_ionic == 0` clause exists for. Narrowing that clause to
    close the user-stop hole must not break it -- the CHE chain needs these energies.
    """
    txt = BANNER + _scf_ok(-32.25) + JOB_DONE
    out = _write(tmp_path, "h2.out", txt)
    rec = qe_qc.scan(out)
    assert rec["n_ionic"] == 0
    assert rec["verdict"] == "TRUSTWORTHY", rec["reasons"]
    assert qe_qc.trusted_energy_ev(out) == pytest.approx(-32.25 * qe_qc.RY_EV)


# ------------------------------------------------- the three false-success modes
def test_mode1_scf_failure_with_job_done_is_poisoned(tmp_path):
    """docs/26 s4: this exact shape produced the retracted eta(NiO2) = 1.751 V."""
    txt = (BANNER + _scf_ok(-100.0) + _force_block(
        [(0, 0, 0), (0, 0, 0), (0.0, 0.0, 0.014), (0.0, 0.0, -0.012)], 0.02)
        + "\n     convergence NOT achieved after 200 iterations: stopping\n" + JOB_DONE)
    out = _write(tmp_path, "j.out", txt)
    _write(tmp_path, "j.in", INPUT_FROZEN_BOTTOM)
    rec = qe_qc.scan(out, str(tmp_path / "j.in"))
    assert rec["job_done"] is True          # pw.x said it was fine
    assert rec["verdict"] == "POISONED"     # we do not
    assert qe_qc.trusted_energy_ev(out, str(tmp_path / "j.in")) is None


def test_mode2_nstep_exhausted_is_poisoned(tmp_path):
    txt = (BANNER + _scf_ok(-100.0) + _force_block(
        [(0, 0, 0), (0, 0, 0), (0, 0, 0.004), (0, 0, -0.004)], 0.006)
        + "\n     The maximum number of steps has been reached.\n" + JOB_DONE)
    out = _write(tmp_path, "j.out", txt)
    rec = qe_qc.scan(out)
    assert rec["verdict"] == "POISONED"


def test_mode3_user_stop_with_job_done_is_not_trustworthy(tmp_path):
    """2026-07-31, Ni_slab/s0_O: killed inside ionic step 1 via the .EXIT flag.

    No ionic step finished, so there is no energy and no force block -- yet the file
    ends in "JOB DONE." and the queue logged rc=0 JOB_DONE=1 SCF_FAIL=0, satisfying
    the first two clauses of the docs/30 s7 acceptance criterion.
    """
    txt = (BANNER
           + "\n     iteration #  85     ecut=    80.00 Ry     beta= 0.10\n"
           + "     estimated scf accuracy    <       0.00020662 Ry\n"
           + "\n     Program stopped by user request\n" + JOB_DONE)
    out = _write(tmp_path, "j.out", txt)
    rec = qe_qc.scan(out)
    assert rec["job_done"] is True
    assert rec["user_stopped"] is True
    assert rec["n_ionic"] == 0
    assert rec["energy_ry"] is None
    assert rec["verdict"] != "TRUSTWORTHY"
    assert qe_qc.trusted_energy_ev(out) is None


def test_no_energy_can_never_be_trustworthy(tmp_path):
    """The invariant behind the mode-3 fix, tested without the user-stop marker.

    A truncated file with n_ionic == 0 and a null energy must not pass on the
    strength of the scf-only clause alone.
    """
    out = _write(tmp_path, "j.out", BANNER + JOB_DONE)
    rec = qe_qc.scan(out)
    assert rec["energy_ry"] is None
    assert rec["verdict"] != "TRUSTWORTHY"
    assert qe_qc.trusted_energy_ev(out) is None


# ------------------------------------------------------------- constrained forces
def test_fmax_is_measured_over_free_atoms_only(tmp_path):
    """pw.x prints forces on FIXED atoms too, and they are huge by construction.

    A converged Cr adslab read 2.03 eV/A over all atoms and 0.047 eV/A over the free
    ones. Judging the raw block would reject every correct slab in the campaign.
    """
    txt = (BANNER + _scf_ok(-100.0) + _force_block(
        [(0, 0, 0.5), (0, 0, -0.4),          # frozen bottom: enormous, irrelevant
         (0, 0, 0.0009), (0, 0, -0.0011)],   # free top: converged
        0.64)
        + "\n     bfgs converged in  12 scf cycles and  11 bfgs steps\n" + JOB_DONE)
    out = _write(tmp_path, "j.out", txt)
    inp = _write(tmp_path, "j.in", INPUT_FROZEN_BOTTOM)
    rec = qe_qc.scan(out, inp)
    assert rec["n_free"] == 2
    assert rec["fmax_free_ry_au"] == pytest.approx(0.0011)
    assert rec["verdict"] == "TRUSTWORTHY", rec["reasons"]

    # ... and with no input to supply the mask, it must fall back to judging every
    # atom, i.e. fail closed rather than silently trusting a half-relaxed slab.
    rec_nomask = qe_qc.scan(out)
    assert rec_nomask["fmax_free_ry_au"] == pytest.approx(0.5)
    assert rec_nomask["verdict"] == "POISONED"


def test_free_atom_fmax_above_audit_threshold_is_poisoned(tmp_path):
    txt = (BANNER + _scf_ok(-100.0) + _force_block(
        [(0, 0, 0), (0, 0, 0), (0, 0, 0.05), (0, 0, -0.02)], 0.06)
        + "\n     bfgs converged in  12 scf cycles and  11 bfgs steps\n" + JOB_DONE)
    out = _write(tmp_path, "j.out", txt)
    inp = _write(tmp_path, "j.in", INPUT_FROZEN_BOTTOM)
    rec = qe_qc.scan(out, inp)
    assert rec["fmax_free_ry_au"] == pytest.approx(0.05)
    assert rec["verdict"] == "POISONED"


def test_missing_file(tmp_path):
    rec = qe_qc.scan(str(tmp_path / "absent.out"))
    assert rec["verdict"] == "MISSING"
    assert qe_qc.trusted_energy_ev(str(tmp_path / "absent.out")) is None
