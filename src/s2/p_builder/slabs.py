"""Slabs with the registered SlabGenerator arguments and the fixed terminations."""
from __future__ import annotations

from collections import Counter

import numpy as np
from pymatgen.analysis.adsorption import AdsorbateSiteFinder, get_mi_vec
from pymatgen.core.surface import Slab, SlabGenerator
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from .registered import SLABGEN_KWARGS, SYMPREC


def generate_slabs(bulk, miller) -> list[Slab]:
    return SlabGenerator(bulk, tuple(miller), **SLABGEN_KWARGS).get_slabs()


def surface_species(slab: Slab) -> dict:
    asf = AdsorbateSiteFinder(slab)
    return dict(sorted(Counter(s.species_string for s in asf.surface_sites).items()))


def select_termination(slabs: list[Slab], termination: dict) -> tuple[int, Slab]:
    if "slab_index" in termination:
        i = termination["slab_index"]
        return i, slabs[i]
    want = dict(sorted(termination["surface_species"].items()))
    hits = [(i, s) for i, s in enumerate(slabs) if surface_species(s) == want]
    if len(hits) != 1:
        raise ValueError(f"termination {want} matched {len(hits)} of {len(slabs)} slabs")
    return hits[0]


def _o_neighbours(slab: Slab, i: int, r: float = 2.3) -> int:
    site = slab[i]
    if "O" not in {s.species_string for s in slab}:  # elemental metal: all neighbours within 3.0 A
        return len(slab.get_neighbors(site, 3.0))
    other = "O" if site.species_string != "O" else None
    if other is None:  # oxygen: count metal neighbours
        return sum(1 for n in slab.get_neighbors(site, r) if n.species_string != "O")
    return sum(1 for n in slab.get_neighbors(site, r) if n.species_string == "O")


def reduced_in_plane_basis(slab: Slab) -> dict:
    """Lagrange-Gauss reduction of the in-plane lattice (a, b): shortest basis, lengths and angle."""
    a = np.array(slab.lattice.matrix[0], dtype=float)
    b = np.array(slab.lattice.matrix[1], dtype=float)
    for _ in range(100):
        if np.dot(b, b) < np.dot(a, a):
            a, b = b, a
        mu = round(float(np.dot(a, b) / np.dot(a, a)))
        if mu == 0:
            break
        b = b - mu * a
    la, lb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    ang = float(np.degrees(np.arccos(np.clip(np.dot(a, b) / (la * lb), -1, 1))))
    return dict(lengths_A=[la, lb], angle_deg=ang, shortest_A=min(la, lb))


def describe_slab(slab: Slab, height: float = 0.9) -> dict:
    """Geometry of a clean slab: thickness and vacuum along the surface normal, top sites."""
    n = get_mi_vec(slab)
    h = np.array([float(np.dot(s.coords, n)) for s in slab])
    span = float(h.max() - h.min())
    period = float(abs(np.dot(slab.lattice.matrix[2], n)))
    order = np.argsort(-h, kind="stable")
    top = [dict(index=int(i), species=slab[i].species_string, depth_A=round(float(h.max() - h[i]), 4),
                n_neighbours_2p3A=_o_neighbours(slab, int(i)))
           for i in order if h.max() - h[i] <= height + 1e-9]
    bottom_depth = [dict(index=int(i), species=slab[i].species_string, height_A=round(float(h[i] - h.min()), 4),
                         n_neighbours_2p3A=_o_neighbours(slab, int(i)))
                    for i in order[::-1] if h[i] - h.min() <= height + 1e-9]
    return dict(
        n_atoms=len(slab), formula=slab.composition.formula,
        miller_index=list(slab.miller_index), shift=float(slab.shift),
        lattice_abc_A=[float(x) for x in slab.lattice.abc],
        lattice_angles_deg=[float(x) for x in slab.lattice.angles],
        surface_cell_area_A2=float(np.linalg.norm(np.cross(slab.lattice.matrix[0], slab.lattice.matrix[1]))),
        reduced_in_plane_basis=reduced_in_plane_basis(slab),
        atom_span_along_normal_A=span,
        vacuum_gap_along_normal_A=period - span,
        c_period_along_normal_A=period,
        surface_species=surface_species(slab),
        top_sites_within_0p9A=top,
        bottom_sites_within_0p9A=bottom_depth,
        neighbour_rule=("oxide metal: O neighbours within 2.3 A; O: metal neighbours within 2.3 A; "
                        "elemental metal: all neighbours within 3.0 A"),
    )


def top_metal_atoms(slab: Slab) -> int:
    """Metal atoms among the AdsorbateSiteFinder surface sites of the top surface (one cell)."""
    return sum(v for k, v in surface_species(slab).items() if k != "O")


def same_operation_sets(ops_a, ops_b, tol: float = 1e-3) -> dict:
    """Fractional operation sets compared as (rotation, translation mod 1)."""
    def key_match(p, q):
        if not np.allclose(p.rotation_matrix, q.rotation_matrix, atol=1e-6):
            return None
        d = np.asarray(p.translation_vector, dtype=float) - np.asarray(q.translation_vector, dtype=float)
        return float(np.abs(d - np.round(d)).max())
    worst = 0.0
    for group, other in ((ops_a, ops_b), (ops_b, ops_a)):
        for p in group:
            diffs = [x for x in (key_match(p, q) for q in other) if x is not None]
            if not diffs or min(diffs) > tol:
                return dict(identical=False, max_translation_diff_frac=None)
            worst = max(worst, min(diffs))
    return dict(identical=len(ops_a) == len(ops_b), max_translation_diff_frac=worst)


def clean_slab_symmetry(slab: Slab, enumerator_symprec: float | None = None) -> dict:
    """Space group of the CLEAN slab only (no adsorbate): the layer group the X argument uses.

    The registered enumerator already analyses the clean slab (its symm_reduce step, at its
    own symprec); when that symprec is given, its operation set is compared with the census
    symprec's. Refuses any structure carrying an adsorbate site.
    """
    props = slab.site_properties.get("surface_properties")
    if props is not None and "adsorbate" in props:
        raise ValueError("clean_slab_symmetry refuses a structure with adsorbate sites")
    sga = SpacegroupAnalyzer(slab, symprec=SYMPREC)
    ops = sga.get_symmetry_operations(cartesian=True)
    n = get_mi_vec(slab)
    lateral = 0
    for op in ops:
        # operations preserving the surface normal (the only ones an adsorbate can keep)
        if np.allclose(op.rotation_matrix @ n, n, atol=1e-6):
            lateral += 1
    out = dict(symprec=SYMPREC, space_group_symbol=sga.get_space_group_symbol(),
               space_group_number=sga.get_space_group_number(), point_group=sga.get_point_group_symbol(),
               n_operations=len(ops), n_operations_preserving_normal=lateral)
    if enumerator_symprec is not None:
        sga_e = SpacegroupAnalyzer(slab, symprec=enumerator_symprec)
        cmp = same_operation_sets(sga.get_symmetry_operations(), sga_e.get_symmetry_operations())
        out["at_enumerator_symprec"] = dict(symprec=enumerator_symprec,
                                            space_group_symbol=sga_e.get_space_group_symbol(),
                                            n_operations=len(sga_e.get_symmetry_operations()),
                                            operation_set_identical_to_census_symprec=cmp["identical"],
                                            max_translation_diff_frac=cmp["max_translation_diff_frac"])
    return out
