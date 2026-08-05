"""Geometry tests for the rutile(110) HEA screening path.

The subject here is `adsorbate_starts`, which exists because single-start relaxation
from the builder placement produced four chemically-wrong structures in the DFT tier
(Cr `*O` trapped at 2.016 A; `*OOH` desorbed on Mn, Fe and Ni), each of which passed
every numerical QC check and cost real money to repair. The HEA screen inherited the
same placement, so these tests pin both the defect and the remedy.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hea_oer.composition import Composition  # noqa: E402
from hea_oer.data import M_O_DESORBED_MIN  # noqa: E402

pymatgen = pytest.importorskip("pymatgen", reason="rutile slabs need pymatgen")

from hea_oer.surfaces_rutile import (  # noqa: E402
    PULL_TO, adsorbate_starts, binding_metal_index, build_rutile110_hea,
    cus_site_xy, m_o_distance,
)

SPECIES = ("O", "OH", "OOH")


@pytest.fixture(scope="module")
def slab():
    comp = Composition(("Fe", "Ni", "Co", "Mn"), (0.32, 0.17, 0.34, 0.17))
    return build_rutile110_hea(comp, supercell=(2, 2), seed=0)


@pytest.fixture(scope="module")
def site(slab):
    return cus_site_xy(slab, n_sites=1)[0]


def test_desorption_threshold_tracks_adsorbate_qc():
    """The two copies of the threshold must never drift apart.

    `dft.adsorbate_qc` owns it and documents its falsification history; `hea_oer.data`
    carries a copy so the library needs no dependency on the campaign scripts.
    """
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "dft"))
    import adsorbate_qc

    assert M_O_DESORBED_MIN == adsorbate_qc.M_O_DESORBED_MIN


@pytest.mark.parametrize("species", SPECIES)
def test_builder_placement_is_too_far_out(slab, site, species):
    """Regression witness for the defect, not an aspiration.

    On rutile(110) the topmost atoms are the bridging-O rows, so a height set above
    the slab maximum puts the adsorbate well off the cus metal. docs/34 s4b measured
    3.07-3.13 A on the endmember inputs. If this test ever fails because the builder
    got fixed, `adsorbate_starts` is cheap insurance rather than a necessity -- but
    the multi-start is still what proves the minimum.
    """
    starts = adsorbate_starts(slab, species, site)
    tag, atoms = starts[0]
    assert tag == "builder"
    assert m_o_distance(atoms, len(slab)) > 2.5


@pytest.mark.parametrize("species", SPECIES)
def test_pull_in_starts_hit_their_target_distance(slab, site, species):
    starts = adsorbate_starts(slab, species, site)
    assert [t for t, _ in starts] == ["builder", "pull1.70", "pull2.10"]
    for target, (_, atoms) in zip(PULL_TO, starts[1:]):
        assert m_o_distance(atoms, len(slab)) == pytest.approx(target, abs=1e-6)


@pytest.mark.parametrize("species", ("OH", "OOH"))
def test_pull_in_is_rigid(slab, site, species):
    """Only the adsorbate's position changes — its internal geometry must not.

    A pull-in that distorted the molecule would be comparing different species at
    different distances, and the lowest-energy pick would be meaningless.
    """
    starts = adsorbate_starts(slab, species, site)
    n = len(slab)

    def internal(atoms):
        pos = atoms.positions[n:]
        return np.array([np.linalg.norm(p - pos[0]) for p in pos[1:]])

    ref = internal(starts[0][1])
    for _, atoms in starts[1:]:
        np.testing.assert_allclose(internal(atoms), ref, atol=1e-10)


def test_slab_atoms_are_untouched_by_pull_in(slab, site):
    starts = adsorbate_starts(slab, "OOH", site)
    n = len(slab)
    ref = starts[0][1].positions[:n]
    for _, atoms in starts[1:]:
        np.testing.assert_allclose(atoms.positions[:n], ref, atol=1e-12)


def test_binding_partner_is_a_metal_not_an_oxygen(slab, site):
    """On rutile(110) the bridging O rows are the closest atoms by height, so a naive
    nearest-neighbour search would bind the adsorbate to an O and report nonsense."""
    for species in SPECIES:
        _, atoms = adsorbate_starts(slab, species, site)[0]
        idx = binding_metal_index(atoms, len(slab))
        assert atoms[idx].symbol != "O"
        assert idx < len(slab)


def test_pull_in_start_is_bound_by_the_desorption_criterion(slab, site):
    """The remedy has to actually clear the bar the defect failed."""
    for species in SPECIES:
        for _, atoms in adsorbate_starts(slab, species, site)[1:]:
            assert m_o_distance(atoms, len(slab)) < M_O_DESORBED_MIN


def test_hea_cus_sites_carry_different_elements(slab):
    """The multi-site sampling only means something if the sites differ chemically."""
    sites = cus_site_xy(slab, n_sites=4)
    assert len(sites) >= 2
    symbols = set()
    for xy in sites:
        _, atoms = adsorbate_starts(slab, "O", xy)[0]
        symbols.add(atoms[binding_metal_index(atoms, len(slab))].symbol)
    assert len(symbols) >= 2, f"all cus sites are {symbols} — decoration may be broken"
