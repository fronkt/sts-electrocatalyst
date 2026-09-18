"""The registered operational definition (docs/43 :1902).

An operation of SpacegroupAnalyzer(structure, symprec=1e-3) is adsorbate-invariant when it
maps every adsorbate atom onto itself mod lattice (distance < 1e-3 A) and has a -1
eigenvalue (a force component it forces to zero). A configuration is retained when it has
at least one such operation.
"""
from __future__ import annotations

import numpy as np
from pymatgen.analysis.adsorption import get_mi_vec
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from .registered import EIGEN_TOL, SELF_MAP_TOL_A, SYMPREC


def adsorbate_indices(structure) -> list[int]:
    props = structure.site_properties.get("surface_properties")
    if props is None:
        raise ValueError("structure has no surface_properties; cannot identify adsorbate atoms")
    idx = [i for i, p in enumerate(props) if p == "adsorbate"]
    if not idx:
        raise ValueError("no adsorbate atoms")
    return idx


def _maps_onto_itself(structure, op, i: int) -> bool:
    q = op.operate(structure[i].coords)
    frac = structure.lattice.get_fractional_coords(q)
    d = structure.lattice.get_all_distances(frac, structure[i].frac_coords)[0][0]
    return bool(d < SELF_MAP_TOL_A)


def minus_one_directions(rotation: np.ndarray) -> list[list[float]]:
    w, v = np.linalg.eig(rotation)
    out = []
    for k in range(3):
        if abs(w[k] + 1) < EIGEN_TOL:
            vec = np.real(v[:, k])
            vec = vec / np.linalg.norm(vec)
            # canonical sign: first component with |x| > 1e-6 positive
            for x in vec:
                if abs(x) > 1e-6:
                    vec = vec if x > 0 else -vec
                    break
            out.append([round(float(x), 6) for x in vec])
    return out


def analyse_configuration(structure, symprec: float = SYMPREC) -> dict:
    ads = adsorbate_indices(structure)
    sga = SpacegroupAnalyzer(structure, symprec=symprec)
    ops = sga.get_symmetry_operations(cartesian=True)
    normal = get_mi_vec(structure)
    invariant = []
    for op in ops:
        dirs = minus_one_directions(op.rotation_matrix)
        if not dirs:
            continue
        if all(_maps_onto_itself(structure, op, i) for i in ads):
            invariant.append(dirs)
    zeroed = sorted({tuple(d) for dirs in invariant for d in dirs})
    lateral = [list(d) for d in zeroed if abs(float(np.dot(d, normal))) < 1e-6]
    return dict(space_group=sga.get_space_group_symbol(), n_operations=len(ops),
                n_adsorbate_invariant_ops=len(invariant), retained=len(invariant) > 0,
                zeroed_directions_cart=[list(d) for d in zeroed], zeroed_lateral_directions_cart=lateral)


def census_family(records_by_ads: dict) -> dict:
    """records_by_ads: {adsorbate: [config records with 'structure' and 'site_type']}."""
    out = {}
    for ads, recs in records_by_ads.items():
        rows = []
        for r in recs:
            a = analyse_configuration(r["structure"])
            rows.append(dict(index=r["index"], site_type=r["site_type"], **a))
        n = len(rows)
        k = sum(1 for x in rows if x["retained"])
        by_type = {}
        for t in ("ontop", "bridge", "hollow"):
            sub = [x for x in rows if x["site_type"] == t]
            by_type[t] = dict(n=len(sub), retained=sum(1 for x in sub if x["retained"]))
        out[ads] = dict(n_configurations=n, retained=k, rate=(k / n if n else None),
                        n_space_group_P1=sum(1 for x in rows if x["space_group"] == "P1"),
                        by_site_type=by_type, configurations=rows)
    return out
