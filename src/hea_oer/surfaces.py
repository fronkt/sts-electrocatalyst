"""Build HEA fcc(111) slabs and place OER adsorbates (*OH, *O, *OOH).

Surface model: a 4-layer fcc(111) slab whose sites are decorated with the alloy
composition (deterministic largest-remainder counts + seeded shuffle), bottom two
layers fixed. Adsorbates sit at a representative top-layer metal site.

NOTE (honest): this is a *metal-surface* screening proxy. The true OER-active
phase of a 3d HEA is its in-situ-reconstructed (oxy)hydroxide. Metal-surface
adsorption energies in the standard *OH/*O/*OOH framework are a recognized,
tractable screening descriptor (OC20 domain, where UMA is strongest); a rutile-
oxide (110) surface is the natural future refinement.
"""
from __future__ import annotations

import numpy as np
from ase import Atoms
from ase.build import fcc111, add_adsorbate
from ase.constraints import FixAtoms

from .composition import Composition

#: fcc lattice constants, Å (γ/fcc allotrope; Cr/Mn fcc values are approximate).
FCC_A = {
    "Fe": 3.589, "Co": 3.545, "Ni": 3.524,
    "Cr": 3.620, "Mn": 3.780, "Cu": 3.615, "Al": 4.050,
}


def _vegard_a(comp: Composition) -> float:
    return float(sum(f * FCC_A[el] for el, f in zip(comp.elements, comp.fractions)))


def _decorate_symbols(comp: Composition, n: int, seed: int) -> list[str]:
    """Assign n site symbols matching the composition as closely as possible
    (largest-remainder rounding), then shuffle deterministically."""
    raw = np.array(comp.fractions) * n
    counts = np.floor(raw).astype(int)
    for idx in np.argsort(-(raw - counts))[: n - counts.sum()]:
        counts[idx] += 1
    syms: list[str] = []
    for el, c in zip(comp.elements, counts):
        syms += [el] * int(c)
    rng = np.random.default_rng(seed)
    rng.shuffle(syms)
    return syms


def build_fcc111_hea(
    comp: Composition,
    size: tuple[int, int, int] = (3, 3, 4),
    vacuum: float = 7.5,
    seed: int = 0,
) -> Atoms:
    """A decorated, bottom-fixed fcc(111) HEA slab (deterministic for `seed`)."""
    slab = fcc111("Ni", size=size, a=_vegard_a(comp), vacuum=vacuum)  # placeholder symbol
    slab.set_chemical_symbols(_decorate_symbols(comp, len(slab), seed))
    z = slab.positions[:, 2]
    layer_z = np.sort(np.unique(np.round(z, 3)))
    cut = layer_z[1] + 0.1 if len(layer_z) >= 2 else layer_z[0] + 0.1  # fix bottom 2 layers
    slab.set_constraint(FixAtoms(mask=z < cut))
    return slab


def _adsorbate(species: str) -> tuple[Atoms, float]:
    """Return (adsorbate Atoms with binding atom first, initial height in Å)."""
    if species == "O":
        return Atoms("O", positions=[[0.0, 0.0, 0.0]]), 1.85
    if species == "OH":
        return Atoms("OH", positions=[[0.0, 0.0, 0.0], [0.7, 0.0, 0.7]]), 1.90
    if species == "OOH":
        return Atoms("OOH", positions=[[0.0, 0.0, 0.0], [1.1, 0.0, 0.9], [1.4, 0.0, 1.85]]), 1.90
    raise ValueError(f"unknown OER species {species!r}")


def top_site_xy(slab: Atoms, site_index: int | None = None) -> tuple[float, float, int]:
    """Pick a top-layer site (default: nearest the cell center). Returns (x, y, idx)."""
    z = slab.positions[:, 2]
    top = np.where(z > z.max() - 0.1)[0]
    if site_index is None:
        centre = (slab.cell[0][:2] + slab.cell[1][:2]) / 2.0
        xy = slab.positions[top][:, :2]
        idx = int(top[np.argmin(np.linalg.norm(xy - centre, axis=1))])
    else:
        idx = int(site_index)
    return float(slab.positions[idx][0]), float(slab.positions[idx][1]), idx


def add_oer_adsorbate(slab: Atoms, species: str, site_index: int | None = None) -> Atoms:
    """Return a copy of `slab` with *OH/*O/*OOH placed atop a top-layer site."""
    ads, height = _adsorbate(species)
    x, y, _ = top_site_xy(slab, site_index)
    out = slab.copy()
    add_adsorbate(out, ads, height=height, position=(x, y), mol_index=0)
    return out
