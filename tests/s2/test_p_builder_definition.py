"""P-BUILDER operational definition on synthetic structures (no census family is touched)."""
import numpy as np
import pytest
from pymatgen.core import Lattice, Structure

from s2.p_builder.census import adsorbate_indices, analyse_configuration, minus_one_directions
from s2.p_builder.slabs import clean_slab_symmetry


def toy(ads_species, ads_cart):
    """One-atom-per-cell square 'slab' (a = 3 A, c = 20 A) with adsorbate atoms appended."""
    lat = Lattice.from_parameters(3.0, 3.0, 20.0, 90, 90, 90)
    s = Structure(lat, ["Pt"], [[0, 0, 0.25]], site_properties={"surface_properties": ["surface"]})
    for sp, xyz in zip(ads_species, ads_cart):
        s.append(sp, xyz, coords_are_cartesian=True, properties={"surface_properties": "adsorbate"})
    return s


def z0():
    return 0.25 * 20.0 + 2.0


def test_ontop_upright_is_retained_with_lateral_zeroes():
    r = analyse_configuration(toy(["O", "H"], [[0, 0, z0()], [0, 0, z0() + 0.98]]))
    assert r["retained"]
    lat = {tuple(abs(x) for x in d) for d in r["zeroed_lateral_directions_cart"]}
    assert (1.0, 0.0, 0.0) in lat and (0.0, 1.0, 0.0) in lat
    assert all(abs(d[2]) < 1e-6 for d in r["zeroed_directions_cart"])


def test_general_position_is_not_retained():
    r = analyse_configuration(toy(["O"], [[0.37 * 3, 0.21 * 3, z0()]]))
    assert not r["retained"] and r["space_group"] == "P1"


def test_bridge_on_mirror_is_retained():
    r = analyse_configuration(toy(["O"], [[1.5, 0.0, z0()]]))
    assert r["retained"]


def test_bent_ooh_is_never_retained_even_on_a_4mm_site():
    ooh = np.array([[0, 0, 0], [1.29, 0, 0.7], [1.29, 0.9, 1.0]]) + [0, 0, z0()]
    r = analyse_configuration(toy(["O", "O", "H"], ooh.tolist()))
    assert not r["retained"] and r["n_adsorbate_invariant_ops"] == 0


def test_op_must_fix_every_adsorbate_atom():
    # O on the 4mm axis, H displaced along x: the mirror y -> -y fixes both, x -> -x does not
    r = analyse_configuration(toy(["O", "H"], [[0, 0, z0()], [0.5, 0, z0() + 0.8]]))
    assert r["retained"]
    lat = {tuple(abs(x) for x in d) for d in r["zeroed_lateral_directions_cart"]}
    assert lat == {(0.0, 1.0, 0.0)}


def test_minus_one_eigen_rules():
    c3 = np.array([[np.cos(2 * np.pi / 3), -np.sin(2 * np.pi / 3), 0],
                   [np.sin(2 * np.pi / 3), np.cos(2 * np.pi / 3), 0], [0, 0, 1]])
    c4 = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=float)
    assert minus_one_directions(c3) == []
    assert minus_one_directions(c4) == []
    assert minus_one_directions(np.diag([1.0, -1.0, 1.0])) == [[0.0, 1.0, 0.0]]
    assert len(minus_one_directions(np.diag([-1.0, -1.0, 1.0]))) == 2
    assert minus_one_directions(np.eye(3)) == []


def test_operation_set_comparison_on_a_clean_toy():
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    from s2.p_builder.slabs import same_operation_sets
    clean = toy([], [])
    a = SpacegroupAnalyzer(clean, symprec=1e-3).get_symmetry_operations()
    b = SpacegroupAnalyzer(clean, symprec=0.1).get_symmetry_operations()
    assert same_operation_sets(a, b)["identical"]
    assert not same_operation_sets(a, b[:-1])["identical"]
    rec = clean_slab_symmetry(clean, enumerator_symprec=0.1)
    assert rec["at_enumerator_symprec"]["operation_set_identical_to_census_symprec"]


def test_min_image_distance_on_a_toy():
    from s2.p_builder.enumeration import min_adsorbate_image_distance
    s = toy(["O", "O", "H"], (np.array([[0, 0, 0], [1.29, 0, 0.7], [1.29, 0.9, 1.0]]) + [0, 0, z0()]).tolist())
    d = min_adsorbate_image_distance(s, [1, 2, 3])
    assert abs(d["distance_A"] - float(np.hypot(3.0 - 1.29, 0.7))) < 1e-9 and d["pair"] == ["O", "O"]


def test_adsorbate_identification_and_clean_slab_guard():
    clean = toy([], [])
    with pytest.raises(ValueError):
        adsorbate_indices(clean)
    assert clean_slab_symmetry(clean)["n_operations"] > 1
    with pytest.raises(ValueError):
        clean_slab_symmetry(toy(["O"], [[0, 0, z0()]]))
