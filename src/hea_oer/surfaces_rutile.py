"""Build HEA rutile MO2(110) slabs (pymatgen) and enumerate cus active sites.

This is the physically-faithful oxide surface the README and the Man et al. (2011)
universal OER scaling relations target. Unlike the metal fcc(111) proxy
([`surfaces`]) or the simple rocksalt(100) model ([`surfaces_oxide`]), the
rutile(110) termination is *termination-sensitive* — it must expose the
characteristic bridging-O rows and 5-coordinate **cus** (coordinatively
unsaturated) metal rows that bind *OH/*O/*OOH. We use `pymatgen`'s `SlabGenerator`
to cleave the correct stoichiometric, symmetric slab, decorate the cation
sublattice with the alloy composition, and enumerate the **distribution of cus
sites** (each with a different local cation environment) — the multi-site sampling
that encodes the HEA scaling-relation-breaking hypothesis (docs/12 §3b).

`pymatgen` is an OPTIONAL dependency: only this module imports it, so the CPU
heuristic round-1, the tests, and the metal/rocksalt backends stay pymatgen-free.

Honest caveats: UMA's OC20 head is metal-dominated (oxide adsorption partly
out-of-distribution); FeO2/CoO2/NiO2/CuO2 are not ground-state rutiles, so their
lattice entries are model values consistent with the rutile trend.
"""
from __future__ import annotations

import numpy as np
from ase import Atoms
from ase.build import add_adsorbate
from ase.constraints import FixAtoms

from .composition import Composition
from .surfaces import _adsorbate, _decorate_symbols

#: rutile MO2 lattice constants (a, c) in Å. CrO2 / β-MnO2 are experimental rutile;
#: Fe/Co/Ni/Cu/Al are model values on the rutile trend (a≈4.45, c≈3.0).
RUTILE_AC = {
    "Cr": (4.421, 2.916), "Mn": (4.404, 2.876),
    "Fe": (4.500, 3.000), "Co": (4.460, 2.990), "Ni": (4.440, 2.985),
    "Cu": (4.470, 3.000), "Al": (4.480, 2.950),
    # benchmark-electrode anchors, experimental rutile constants (Bolzan et al.,
    # Acta Cryst. B53, 373 (1997), 10.1107/S0108768197001468) -- see docs/29 s2
    "Ru": (4.492, 3.107), "Ir": (4.498, 3.154),
}
_RUTILE_U = 0.305  # internal O parameter (P4_2/mnm, Wyckoff 4f)


def _vegard_ac(comp: Composition) -> tuple[float, float]:
    a = sum(f * RUTILE_AC[el][0] for el, f in zip(comp.elements, comp.fractions))
    c = sum(f * RUTILE_AC[el][1] for el, f in zip(comp.elements, comp.fractions))
    return float(a), float(c)


def _rutile_bulk(a: float, c: float, metal: str = "Ti"):
    from pymatgen.core import Lattice, Structure

    u = _RUTILE_U
    coords = [
        [0.0, 0.0, 0.0], [0.5, 0.5, 0.5],                 # M (2a)
        [u, u, 0.0], [1 - u, 1 - u, 0.0],                 # O (4f)
        [0.5 + u, 0.5 - u, 0.5], [0.5 - u, 0.5 + u, 0.5],
    ]
    species = [metal, metal, "O", "O", "O", "O"]
    return Structure(Lattice.from_parameters(a, a, c, 90, 90, 90), species, coords)


def _pick_rutile110(slabs):
    """Pick the stoichiometric (O:M = 2), symmetric bridging-O-terminated slab."""
    def is_stoich(s):
        frac = s.composition.get_atomic_fraction("O")
        return abs(frac - 2.0 / 3.0) < 1e-3
    sym_stoich = [s for s in slabs if is_stoich(s) and s.is_symmetric()]
    pool = sym_stoich or [s for s in slabs if is_stoich(s)] or slabs
    return min(pool, key=lambda s: len(s))  # smallest valid cell


def build_rutile110_hea(
    comp: Composition,
    min_slab_size: float = 8.0,
    vacuum: float = 13.0,
    supercell: tuple[int, int] = (2, 2),
    seed: int = 0,
) -> Atoms:
    """A decorated, bottom-fixed rutile(110) HEA-oxide slab as ASE `Atoms`.

    pymatgen cleaves the correct stoichiometric/symmetric (110) termination; the
    cation sublattice is decorated with the composition (largest-remainder +
    seeded shuffle); the bottom half is fixed for relaxation.
    """
    from pymatgen.core.surface import SlabGenerator
    from pymatgen.io.ase import AseAtomsAdaptor

    a, c = _vegard_ac(comp)
    bulk = _rutile_bulk(a, c)
    sg = SlabGenerator(bulk, (1, 1, 0), min_slab_size=min_slab_size,
                       min_vacuum_size=vacuum, center_slab=True, lll_reduce=True,
                       primitive=False)
    slab = _pick_rutile110(sg.get_slabs(symmetrize=False))
    slab.make_supercell([[supercell[0], 0, 0], [0, supercell[1], 0], [0, 0, 1]])

    metal_idx = [i for i, site in enumerate(slab) if site.specie.symbol != "O"]
    for i, s in zip(metal_idx, _decorate_symbols(comp, len(metal_idx), seed)):
        slab.replace(i, s)

    atoms = AseAtomsAdaptor.get_atoms(slab)
    z = atoms.positions[:, 2]
    zmid = (z.min() + z.max()) / 2.0
    # A symmetric rutile(110) slab puts a whole layer EXACTLY on the mid-plane, so a
    # bare `z < zmid` decides those atoms on float64 noise: the 2026-07 endmember
    # inputs came out with 11 free atoms for Cr/Mn/Fe/Cu/Ru, 7 for Ni, 10 for Ir and
    # 8 for Co -- and for Co and Ir the split fell *within* the mid-layer, giving two
    # crystallographically equivalent atoms different constraints. Tolerancing the
    # comparison frees the whole mid-layer, which is both symmetry-respecting and
    # what the majority of the archived runs happened to get. See docs/30.
    tol = 1e-6 * max(1.0, abs(zmid))
    atoms.set_constraint(FixAtoms(mask=z < zmid - tol))  # fix strictly-bottom half
    return atoms


def _o_coordination(atoms: Atoms, cutoff: float = 2.4) -> np.ndarray:
    """# of O atoms within `cutoff` Å of each atom (PBC-aware, fast)."""
    from ase.neighborlist import neighbor_list

    i, j = neighbor_list("ij", atoms, cutoff)
    syms = np.array(atoms.get_chemical_symbols())
    is_O = syms == "O"
    counts = np.zeros(len(atoms), dtype=int)
    np.add.at(counts, i, is_O[j])
    return counts


def cus_site_xy(atoms: Atoms, n_sites: int = 4, cutoff: float = 2.4) -> list[tuple[float, float]]:
    """(x, y) of up to `n_sites` distinct top cus metals (5-coordinate surface M).

    Cus = surface metal whose O-coordination is one less than the bulk maximum,
    sitting in the top half of the slab. Sorted by height, de-duplicated in-plane.
    """
    syms = np.array(atoms.get_chemical_symbols())
    z = atoms.positions[:, 2]
    coord = _o_coordination(atoms, cutoff)
    metal = np.where(syms != "O")[0]
    bulk_cn = int(np.max(coord[metal])) if len(metal) else 6
    top = metal[(z[metal] > (z.min() + z.max()) / 2.0) & (coord[metal] == bulk_cn - 1)]
    if len(top) == 0:  # fall back to the most-undercoordinated top-half metals
        th = metal[z[metal] > (z.min() + z.max()) / 2.0]
        top = th[np.argsort(coord[th])][: max(1, n_sites)]
    order = top[np.argsort(-z[top])]
    out: list[tuple[float, float]] = []
    seen: set[tuple[int, int]] = set()
    for idx in order:
        x, y = float(atoms.positions[idx][0]), float(atoms.positions[idx][1])
        key = (round(x, 1), round(y, 1))
        if key not in seen:
            seen.add(key)
            out.append((x, y))
        if len(out) >= n_sites:
            break
    return out


def add_oer_adsorbate_at(atoms: Atoms, species: str, xy: tuple[float, float]) -> Atoms:
    """Return a copy of `atoms` with *OH/*O/*OOH placed atop the cus site at `xy`."""
    ads, height = _adsorbate(species)
    out = atoms.copy()
    add_adsorbate(out, ads, height=height, position=(float(xy[0]), float(xy[1])), mol_index=0)
    return out
