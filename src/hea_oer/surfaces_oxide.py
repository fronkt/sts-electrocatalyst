"""Build HEA *oxide* slabs (rocksalt MO(100)) and place OER adsorbates.

Why this exists: a bare metal fcc(111) slab ([`surfaces.build_fcc111_hea`]) over-binds
O, so every candidate lands on the strong-binding leg far from the volcano apex and
the absolute overpotential is unphysical (see docs/13). The OER-active phase of a
3d-metal HEA is its in-situ (oxy)hydroxide; this module models a tractable *model
oxide* surface instead — **rocksalt MO(100)**, the stable non-polar cleavage of the
3d monoxides (NiO/CoO/FeO/MnO) — with the cation sublattice decorated by the alloy
composition and a coordinatively-unsaturated (cus) surface metal as the active site.

Energies still come from UMA's OC20 adsorption head (no oxide-specific UMA head
exists). rocksalt(100) keeps the octahedral-derived 5-coordinate binding motif that
the universal *OH/*O/*OOH scaling relations (Man et al. 2011) — which set the
volcano in `descriptors.py` — were built on.

Honest caveats (carry to the paper): (i) UMA OC20 is metal-dominated, so oxide
adsorption is partly out-of-distribution; (ii) rocksalt(100) is a model surface, not
the true layered oxyhydroxide; (iii) Cr/Cu rocksalt monoxides are not ground states,
so their lattice entries are model values.
"""
from __future__ import annotations

import numpy as np
from ase import Atoms
from ase.build import bulk, surface, add_adsorbate
from ase.constraints import FixAtoms

from .composition import Composition
from .surfaces import _adsorbate, _decorate_symbols  # reuse adsorbate geometry + decoration

#: rocksalt monoxide lattice constants, Å. NiO/CoO/FeO/MnO are experimental rocksalt
#: (CRC / wüstite); Cr/Cu/Al are model values (their stable oxides are not rocksalt).
ROCKSALT_A = {
    "Mn": 4.445, "Fe": 4.326, "Co": 4.260, "Ni": 4.177,
    "Cr": 4.160, "Cu": 4.270, "Al": 4.040,
}


def _vegard_a(comp: Composition) -> float:
    return float(sum(f * ROCKSALT_A[el] for el, f in zip(comp.elements, comp.fractions)))


def build_rocksalt100_hea(
    comp: Composition,
    size: tuple[int, int, int] = (2, 2, 4),
    vacuum: float = 7.5,
    seed: int = 0,
) -> Atoms:
    """A decorated, bottom-fixed rocksalt MO(100) HEA-oxide slab (deterministic for `seed`).

    The (100) planes are non-polar mixed M/O checkerboards; the cation sites are
    decorated with the composition (largest-remainder counts + seeded shuffle), O
    sites are left as O, and the bottom half is fixed.
    """
    mo = bulk("MgO", "rocksalt", a=_vegard_a(comp), cubic=True)
    slab = surface(mo, (1, 0, 0), layers=size[2], vacuum=vacuum)
    slab = slab.repeat((size[0], size[1], 1))

    syms = slab.get_chemical_symbols()
    metal_idx = [i for i, s in enumerate(syms) if s != "O"]
    for i, s in zip(metal_idx, _decorate_symbols(comp, len(metal_idx), seed)):
        syms[i] = s
    slab.set_chemical_symbols(syms)

    z = slab.positions[:, 2]
    zmid = (z.min() + z.max()) / 2.0
    slab.set_constraint(FixAtoms(mask=z < zmid))  # fix bottom half
    return slab


def cus_metal_site(slab: Atoms) -> tuple[float, float, int]:
    """(x, y, idx) of the topmost surface metal — the cus OER active site."""
    syms = np.array(slab.get_chemical_symbols())
    z = slab.positions[:, 2]
    metal = np.where(syms != "O")[0]
    idx = int(metal[np.argmax(z[metal])])
    return float(slab.positions[idx][0]), float(slab.positions[idx][1]), idx


def add_oer_adsorbate_oxide(slab: Atoms, species: str, site_index: int | None = None) -> Atoms:
    """Return a copy of `slab` with *OH/*O/*OOH placed atop the cus surface metal."""
    ads, height = _adsorbate(species)
    if site_index is None:
        x, y, _ = cus_metal_site(slab)
    else:
        x, y = float(slab.positions[site_index][0]), float(slab.positions[site_index][1])
    out = slab.copy()
    add_adsorbate(out, ads, height=height, position=(x, y), mol_index=0)
    return out
