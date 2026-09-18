"""pw.x readers of the low-tail track: total forces only, strict SCF evidence, relax descriptors."""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "s2" / "lowtail_dft"))
sys.path.insert(0, str(ROOT / "src" / "dft"))

import lt_common  # noqa: E402
import lt_qe as qe  # noqa: E402

DECK = """&CONTROL
  calculation = 'scf'
  prefix = 'x'
  forc_conv_thr = 2.0d-3
/
&SYSTEM
  ibrav = 0
  nat = 3
  ntyp = 3
  ecutwfc = 80.0
  ecutrho = 640.0
  degauss = 0.01
  starting_magnetization(1) = 0.6
/
&ELECTRONS
  conv_thr = 1.0d-6
/
ATOMIC_SPECIES
  Cr1  51.996  cr.UPF
  Cr2  51.996  cr.UPF
  O  15.999  o.UPF
CELL_PARAMETERS angstrom
  5.0  0.0  0.0
  0.0  6.0  0.0
  0.0  0.0  20.0
ATOMIC_POSITIONS angstrom
  Cr1  0.0  0.0  5.0  0 0 0
  Cr2  2.5  3.0  5.0
  O  2.5  3.0  6.6  1 1 1
K_POINTS automatic
  4 2 1 0 0 0
"""


def force_rows(values):
    return "\n".join(f"     atom {i + 1:4d} type  1   force = {v[0]:14.8f}{v[1]:14.8f}{v[2]:14.8f}" for i, v in enumerate(values))


def scf_output(total, contrib=None, extra="", energies=("-100.00000000",), job_done=1):
    parts = ["     number of atoms/cell      =            3",
             "     number of electrons       =        34.00",
             "     number of Kohn-Sham states=           20",
             "     total magnetization       =     2.00 Bohr mag/cell",
             "     absolute magnetization    =     3.50 Bohr mag/cell"]
    for e in energies:
        parts.append(f"!    total energy              =    {e} Ry")
    parts.append("     convergence has been achieved in  12 iterations")
    parts.append("     Forces acting on atoms (cartesian axes, Ry/au):")
    parts.append("")
    parts.append(force_rows(total))
    if contrib is not None:
        parts.append("     The non-local contrib.  to forces")
        parts.append(force_rows(contrib))
        parts.append("     The ionic contribution  to forces")
        parts.append(force_rows(contrib))
    parts.append("")
    parts.append("     Total force =     0.100000     Total SCF correction =     0.000000")
    parts.append("     init_run     :     30.15s CPU     30.15s WALL (       1 calls)")
    parts.append("     electrons    :   1761.74s CPU   1805.45s WALL (       1 calls)")
    parts.append("     forces       :     53.36s CPU     55.14s WALL (       1 calls)")
    parts.append("     PWSCF        :  30m46.15s CPU  31m33.31s WALL")
    parts.append(extra)
    parts += ["   JOB DONE."] * job_done
    return "\n".join(parts) + "\n"


TOTAL = [[0.1, -0.2, 0.3], [0.0, 0.01, -0.04], [-0.1, 0.19, -0.26]]
CONTRIB = [[9.0, 9.0, 9.0]] * 3


def test_constants_are_those_of_the_accepting_parser():
    text = (ROOT / "src/dft/hea_force_audit.py").read_text(encoding="utf-8")
    assert f"RY_TO_EV = {lt_common.RY_TO_EV!r}" in text
    assert f"RY_BOHR_TO_EV_A = {lt_common.RY_BOHR_TO_EV_A!r}" in text


def test_failure_vocabulary_equals_followup_qc():
    import hea_followup_qc
    assert qe.FAILURES.pattern == hea_followup_qc.FAILURES.pattern
    assert qe.FAILURES.flags & re.I


def test_total_forces_read_and_contribution_blocks_ignored():
    rec = qe.parse_scf(scf_output(TOTAL, contrib=CONTRIB), 3)
    assert rec["status"] == "VALID_SCF", rec["reasons"]
    assert rec["n_contribution_blocks"] == 2
    np.testing.assert_allclose(rec["forces_eV_A"], np.array(TOTAL) * lt_common.RY_BOHR_TO_EV_A)
    assert rec["energy_eV"] == pytest.approx(-100.0 * lt_common.RY_TO_EV)
    assert rec["iterations"] == 12 and rec["total_muB"] == 2.0 and rec["absolute_muB"] == 3.5
    assert rec["timers"]["electrons"]["wall_s"] == 1805.45
    assert rec["timers"]["PWSCF_wall_s"] == pytest.approx(1893.31)
    assert rec["header"]["nbnd"] == 20


@pytest.mark.parametrize("mutate, reason", [
    (lambda t: t.replace("     atom    3 type  1   force", "     atom    4 type  1   force"), "ordered rows"),
    (lambda t: t.replace(force_rows(TOTAL).split("\n")[2] + "\n", "", 1), "ordered rows"),
    (lambda t: t.replace("   JOB DONE.", "Note: IEEE_INVALID_FLAG\n   JOB DONE."), "failure markers"),
    (lambda t: t.replace("   JOB DONE.", "     convergence NOT achieved after 300 iterations: stopping\n   JOB DONE."), "failure markers"),
    (lambda t: t.replace("   JOB DONE.\n", ""), "JOB DONE"),
])
def test_strict_scf_refusals(mutate, reason):
    rec = qe.parse_scf(mutate(scf_output(TOTAL)), 3)
    assert rec["status"] == "REJECTED"
    assert any(reason in r for r in rec["reasons"]), rec["reasons"]
    assert rec["forces_eV_A"] is None


def test_two_energies_refused_for_a_single_point():
    rec = qe.parse_scf(scf_output(TOTAL, energies=("-100.0", "-100.1")), 3)
    assert rec["status"] == "REJECTED"


@pytest.mark.parametrize("flags, accepted", [
    ("IEEE_UNDERFLOW_FLAG IEEE_DENORMAL", True),
    ("IEEE_INVALID_FLAG", False),
    ("IEEE_UNDERFLOW_FLAG IEEE_INVALID_FLAG", False),
    ("IEEE_DIVIDE_BY_ZERO", False),
    ("UNRECOGNIZED_FLAG", False),
])
def test_numerical_notices_keep_unknown_or_fatal_flags(flags, accepted):
    note = f"Note: The following floating-point exceptions are signalling: {flags}"
    result = qe.parse_scf(scf_output(TOTAL, extra=note), 3)
    assert (result["status"] == "VALID_SCF") == accepted


def test_extra_final_coordinate_row_is_rejected():
    text = ("Begin final coordinates\nATOMIC_POSITIONS (angstrom)\n"
            "Cr 0 0 0\nO 0 0 1\nO 0 0 2\nO 0 0 3\nEnd final coordinates\n")
    assert qe.final_coordinates(text, 3) is None


def test_input_parse_spin_labels_and_flags():
    p = qe.parse_input(DECK)
    assert p["symbols"] == ["Cr1", "Cr2", "O"] and p["elements"] == ["Cr", "Cr", "O"]
    assert p["if_pos"] == [[0, 0, 0], [1, 1, 1], [1, 1, 1]] and p["fixed"] == [0]
    assert p["params"]["forc_conv_thr"] == 2.0e-3
    assert p["calculation"] == "scf" and p["cell"][2][2] == 20.0
    with pytest.raises(ValueError):
        qe.parse_input(DECK.replace("  O  2.5  3.0  6.6  1 1 1\n", ""))


@pytest.mark.parametrize("token, seconds, resolution", [
    ("31m33.31s", 1893.31, 0.01), ("7h47m", 28020.0, 60.0), ("1d10h27m", 124020.0, 60.0), ("55.14s", 55.14, 0.01)])
def test_clock_tokens(token, seconds, resolution):
    s, r = qe._wall_seconds(token)
    assert s == pytest.approx(seconds) and r == resolution


def test_relax_descriptors_and_final_coordinates():
    blocks = scf_output(TOTAL).replace("   JOB DONE.\n", "")
    text = (blocks + scf_output(TOTAL).split("     Forces acting")[0].split("!")[0]
            + "!    total energy              =    -100.10000000 Ry\n"
            + "     convergence has been achieved in   5 iterations\n"
            + "     Forces acting on atoms (cartesian axes, Ry/au):\n\n" + force_rows([[0, 0, 0.001]] * 3) + "\n\n"
            + "     bfgs converged in   2 scf cycles and   1 bfgs steps\n"
            + "     End of BFGS Geometry Optimization\n\n     Final energy             =    -100.1000000000 Ry\n"
            + "Begin final coordinates\n\nATOMIC_POSITIONS (angstrom)\nCr1 0.0 0.0 5.0 0 0 0\nCr2 2.5 3.0 5.3\nO 2.5 3.0 6.9\n"
            + "End final coordinates\n\n   JOB DONE.\n")
    r = qe.parse_relax(text, 3)
    assert r["bfgs_converged"] and r["bfgs_scf_cycles"] == 2 and r["bfgs_steps"] == 1
    assert r["scf_iterations"] == [12, 5] and len(r["force_blocks"]) == 2
    assert r["final_energy_Ry"] == -100.1
    assert r["final_coordinates"]["symbols"] == ["Cr1", "Cr2", "O"]
    assert r["final_coordinates"]["positions"][1] == [2.5, 3.0, 5.3]


def test_real_winner_O_forces_equal_the_stored_audit():
    stem = ROOT / "runs/hea/winner_2026-09-10/g_80ebe76a616d61d6fecca57d1cd6c2ef27990771fbc3db9a8cfea6a4bf228e5c__atomic"
    parsed = qe.parse_input(qe.read_text(stem.with_name(stem.name + ".run.in")))
    rec = qe.parse_scf(qe.read_text(stem.with_name(stem.name + ".out")), parsed["nat"])
    assert rec["status"] == "VALID_SCF" and rec["n_contribution_blocks"] == 0
    stored = json.loads(stem.with_name(stem.name + ".qc.json").read_text(encoding="utf-8"))["scf"]["per_atom"]
    np.testing.assert_allclose(rec["forces_eV_A"], [a["force_ev_A"] for a in stored], rtol=0, atol=1e-12)
    assert qe.free_fmax(rec["forces_eV_A"], parsed["if_pos"]) == pytest.approx(
        json.loads(stem.with_name(stem.name + ".qc.json").read_text(encoding="utf-8"))["scf"]["fmax_free_ev_A"], abs=1e-12)
