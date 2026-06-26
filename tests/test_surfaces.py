"""HEA slab construction + adsorbate placement (geometry only; no calculator)."""
from collections import Counter

from ase.constraints import FixAtoms

from hea_oer.composition import Composition
from hea_oer.surfaces import build_fcc111_hea, add_oer_adsorbate


def cantor():
    return Composition.equiatomic(["Co", "Cr", "Fe", "Mn", "Ni"])


def test_slab_size_and_decoration():
    slab = build_fcc111_hea(cantor(), size=(3, 3, 4), seed=0)
    assert len(slab) == 36
    counts = Counter(slab.get_chemical_symbols())
    assert set(counts) == {"Co", "Cr", "Fe", "Mn", "Ni"}
    assert sum(counts.values()) == 36
    assert all(6 <= n <= 9 for n in counts.values())  # ~7.2 each, largest-remainder


def test_bottom_two_layers_fixed():
    slab = build_fcc111_hea(cantor(), size=(3, 3, 4), seed=0)
    fix = [c for c in slab.constraints if isinstance(c, FixAtoms)]
    assert len(fix) == 1
    assert len(fix[0].get_indices()) == 18  # bottom 2 of 4 layers × 9


def test_decoration_is_deterministic():
    a = build_fcc111_hea(cantor(), seed=0).get_chemical_symbols()
    b = build_fcc111_hea(cantor(), seed=0).get_chemical_symbols()
    assert a == b


def test_adsorbate_atom_counts():
    slab = build_fcc111_hea(cantor(), seed=0)
    n = len(slab)
    assert len(add_oer_adsorbate(slab, "O")) == n + 1
    assert len(add_oer_adsorbate(slab, "OH")) == n + 2
    assert len(add_oer_adsorbate(slab, "OOH")) == n + 3


def test_adsorbate_sits_above_surface():
    slab = build_fcc111_hea(cantor(), seed=0)
    ztop = slab.positions[:, 2].max()
    out = add_oer_adsorbate(slab, "OH")
    assert out.positions[-2, 2] > ztop      # binding O above the top layer
    assert out.get_chemical_symbols()[-2:] == ["O", "H"]
