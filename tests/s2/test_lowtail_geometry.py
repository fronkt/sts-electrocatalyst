"""Periodic geometry, force projections and basin labels of the low-tail track."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "s2" / "lowtail_dft"))

import lt_geometry as geo  # noqa: E402

CELL = [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 20.0]]
TH = dict(lift_min_A=0.5, axial_break_A=2.1758, desorbed_min_A=3.0)


def test_orthogonal_cell_required_and_minimum_image():
    with pytest.raises(ValueError):
        geo.cell_lengths([[10.0, 0.1, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 20.0]])
    np.testing.assert_allclose(geo.mic([9.5, -9.0, 11.0], CELL), [-0.5, 1.0, -9.0])
    assert geo.distance([[0.2, 0.0, 0.0], [9.9, 0.0, 0.0]], 0, 1, CELL) == pytest.approx(0.3)


def test_pair_force_signs():
    pos = [[5, 5, 8.0], [5, 5, 9.6]]
    f = [[0, 0, 1.0], [0, 0, -1.0]]
    r = geo.pair_forces(f, pos, CELL, 0, 1)
    assert r["site_normal_eV_A"] == 1.0 and r["site_normal_direction"] == "away from slab"
    assert r["bond_stretch_eV_A"] == pytest.approx(-2.0)      # both pushed together: shortens M-O
    assert r["pair_normal_eV_A"] == pytest.approx(0.0)
    r2 = geo.pair_forces([[0, 0, -0.5], [0, 0, 0.5]], pos, CELL, 0, 1)
    assert r2["bond_stretch_eV_A"] == pytest.approx(1.0) and r2["site_normal_direction"] == "toward slab"


def test_axial_forces_sign():
    pos = [[5, 5, 8.0], [5, 5, 6.2]]           # axial O below the metal
    r = geo.axial_forces([[0, 0, 1.0], [0, 0, 0.6]], pos, CELL, 0, 1)
    assert r["axial_stretch_eV_A"] == pytest.approx(0.4)      # metal pulled up faster than O: lengthens
    r = geo.axial_forces([[0, 0, -1.0], [0, 0, 0.6]], pos, CELL, 0, 1)
    assert r["axial_stretch_eV_A"] == pytest.approx(-1.6)


def test_axial_decomposition_separates_bond_compression_from_the_axial_contact():
    # metal at z 8, axial O below at 6.2, appended O above at 9.6 (indices 0, 1, 2)
    pos = [[5, 5, 8.0], [5, 5, 6.2], [5, 5, 9.6]]
    symbols = ["Cr", "O", "O"]
    # Cr=O compression pushes Cr up (+1.0) and O down (-1.0); axial O pushed up toward Cr (+0.6)
    f = [[0, 0, 1.0], [0, 0, 0.6], [0, 0, -1.05]]
    two_atom = geo.axial_forces(f, pos, CELL, 0, 1)
    d = geo.axial_decomposition(f, pos, symbols, CELL, 0, 1, ads_o=2)
    assert d["u_z"] == pytest.approx(-1.0) and d["unit_members"] == [0, 2]
    assert two_atom["axial_stretch_eV_A"] == pytest.approx(0.4)                 # the two-atom difference says "opens"
    assert d["site_away_from_axial_eV_A"] - d["axial_O_toward_site_eV_A"] == pytest.approx(two_atom["axial_stretch_eV_A"])
    assert d["axial_O_toward_site_eV_A"] == pytest.approx(0.6)
    assert d["unit_toward_axial_eV_A"] == pytest.approx(0.05)                     # unit net force points down, toward O
    m_cr, m_o = geo.atomic_mass("Cr"), geo.atomic_mass("O")
    assert d["unit_mass_amu"] == pytest.approx(m_cr + m_o)
    assert d["relative_acceleration_eV_A_amu"] == pytest.approx(-0.6 / m_o - 0.05 / (m_cr + m_o))
    assert d["gap_first_order"] == "closing"
    clean = geo.axial_decomposition([[0, 0, 1.0], [0, 0, -0.6], [0, 0, 0]], pos, symbols, CELL, 0, 1)
    assert clean["unit_members"] == [0] and clean["gap_first_order"] == "opening"


def test_axial_oxygen_is_the_one_below():
    symbols = ["Cr", "O", "O", "O"]
    clean = [[5, 5, 8.0], [5, 5, 6.2], [7, 5, 8.0], [5, 5, 9.9]]
    ax = geo.axial_oxygen(symbols, clean, 0, CELL, 4)
    assert ax["index"] == 1 and ax["clean_distance_A"] == pytest.approx(1.8)


@pytest.mark.parametrize("lift, axial, dads, onsite, label", [
    (0.8, 2.6, 1.59, True, "RECONSTRUCTED"),
    (0.1, 1.8, 1.63, True, "UNRECONSTRUCTED"),
    (0.8, 1.9, 1.60, True, "MIXED_UNASSIGNED"),
    (0.2, 2.4, 1.60, True, "MIXED_UNASSIGNED"),
    (0.8, 2.6, 3.2, True, "O_OFF_SITE"),
    (0.8, 2.6, 1.6, False, "O_OFF_SITE"),
    (0.5, 2.1758, 1.6, True, "RECONSTRUCTED"),
])
def test_basin_labels(lift, axial, dads, onsite, label):
    assert geo.basin(lift, axial, dads, onsite, TH) == label


def test_force_agreement_excludes_fixed_components():
    fd = [[1.0, 0, 0], [0, 0, 2.0]]
    fm = [[100.0, 0, 0], [0, 0, 1.0]]
    mask = [[0, 0, 0], [1, 1, 1]]
    r = geo.force_agreement(fd, fm, mask)
    assert r["n_free_components"] == 3 and r["n_free_atoms"] == 1
    assert r["component_mae_eV_A"] == pytest.approx(1.0 / 3)
    assert r["max_atom_vector_difference_eV_A"] == pytest.approx(1.0)
