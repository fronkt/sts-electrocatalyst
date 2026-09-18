"""The registered enumerator, run unmodified; no symmetry is computed on its output here."""
from __future__ import annotations

import hashlib
import inspect
import itertools
import re

import numpy as np
import pymatgen.analysis.adsorption as _adsorption
from pymatgen.analysis.adsorption import AdsorbateSiteFinder
from pymatgen.core import Molecule, Structure

from .registered import ADSORBATES, ENUM_FIND_ARGS, ENUM_REPEAT

SITE_TYPES = ("ontop", "bridge", "hollow")


def enumerator_internal_tolerances() -> dict:
    """The tolerances the registered call uses internally, read from the installed pymatgen.

    find_adsorption_sites(distance=2.0) leaves symm_reduce and near_reduce at their defaults.
    symm_reduce(threshold) takes its operations from SpacegroupAnalyzer(self.slab, <symprec>)
    and matches positions with in_coord_list_pbc(atol=threshold) in FRACTIONAL coordinates.
    """
    sig = inspect.signature(AdsorbateSiteFinder.find_adsorption_sites).parameters
    src = inspect.getsource(AdsorbateSiteFinder.symm_reduce)
    m = re.search(r"SpacegroupAnalyzer\(self\.slab,\s*([0-9.eE+-]+)\)", src)
    match_frac = bool(re.search(r"in_coord_list_pbc\(.*atol=threshold\)", src)
                      and re.search(r"coords_set = \[self\.slab\.lattice\.get_fractional_coords", src))
    with open(_adsorption.__file__, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    return dict(symm_reduce_default=sig["symm_reduce"].default, near_reduce_default=sig["near_reduce"].default,
                no_obtuse_hollow_default=sig["no_obtuse_hollow"].default,
                symm_reduce_symprec=float(m.group(1)) if m else None,
                symm_reduce_matches_fractional_coords_at_threshold=match_frac,
                pymatgen_adsorption_py_sha256=digest)


def min_adsorbate_image_distance(structure, ads_idx: list[int], reach: int = 3) -> dict:
    """Shortest distance between an adsorbate atom and an adsorbate atom of an in-plane
    periodic image (translations n1*a + n2*b, (n1, n2) != (0, 0)). Geometry only."""
    a, b = (np.array(structure.lattice.matrix[k], dtype=float) for k in (0, 1))
    xyz = structure.cart_coords
    best = (float("inf"), None)
    for n1, n2 in itertools.product(range(-reach, reach + 1), repeat=2):
        if (n1, n2) == (0, 0):
            continue
        t = n1 * a + n2 * b
        for i in ads_idx:
            for j in ads_idx:
                d = float(np.linalg.norm(xyz[i] - (xyz[j] + t)))
                if d < best[0] - 1e-12:
                    best = (d, (structure[i].species_string, structure[j].species_string, n1, n2))
    return dict(distance_A=best[0], pair=[best[1][0], best[1][1]], image=[best[1][2], best[1][3]])


def adsorbate_molecule(name: str) -> Molecule:
    species, coords = ADSORBATES[name]
    return Molecule(species, coords)


def enumerate_configs(slab, name: str) -> list[dict]:
    """AdsorbateSiteFinder(slab).generate_adsorption_structures(mol, repeat=[1,1,1],
    find_args={"distance": 2.0}) -- the registered call -- plus a site-type label.

    The label comes from find_adsorption_sites with the same find_args: the enumerator
    places configuration i at sites["all"][i], and "all" concatenates ontop, bridge,
    hollow in that order. The label is checked against the placed first adsorbate atom.
    """
    mol = adsorbate_molecule(name)
    asf = AdsorbateSiteFinder(slab)
    sites = asf.find_adsorption_sites(**ENUM_FIND_ARGS)
    structs = AdsorbateSiteFinder(slab).generate_adsorption_structures(
        mol, repeat=ENUM_REPEAT, find_args=ENUM_FIND_ARGS)
    labels = [t for t in SITE_TYPES for _ in sites[t]]
    if len(structs) != len(sites["all"]) or len(labels) != len(structs):
        raise RuntimeError(f"enumerator count {len(structs)} != site count {len(sites['all'])}")
    n_slab = len(slab)
    records = []
    for i, st in enumerate(structs):
        ads_idx = [j for j, s in enumerate(st) if s.properties.get("surface_properties") == "adsorbate"]
        if ads_idx != list(range(n_slab, n_slab + len(mol))):
            raise RuntimeError(f"config {i}: adsorbate indices {ads_idx} not appended after the slab")
        first = st[ads_idx[0]].coords
        if not np.allclose(first, sites["all"][i], atol=1e-6):
            raise RuntimeError(f"config {i}: first adsorbate atom not at enumerated site")
        records.append(dict(index=i, site_type=labels[i],
                            site_cart_A=[float(x) for x in sites["all"][i]],
                            n_slab_atoms=n_slab, adsorbate_indices=ads_idx, structure=st))
    return records


def record_to_json(rec: dict) -> dict:
    out = {k: v for k, v in rec.items() if k != "structure"}
    out["structure"] = rec["structure"].as_dict()
    return out


def record_from_json(d: dict) -> dict:
    out = dict(d)
    out["structure"] = Structure.from_dict(d["structure"])
    return out


def site_type_counts(records: list[dict]) -> dict:
    return {t: sum(1 for r in records if r["site_type"] == t) for t in SITE_TYPES}


def min_image_distance_over_configs(records: list[dict]) -> dict:
    """The shortest adsorbate-image contact over every configuration of one adsorbate."""
    rows = [dict(index=r["index"], **min_adsorbate_image_distance(r["structure"], r["adsorbate_indices"]))
            for r in records]
    worst = min(rows, key=lambda x: x["distance_A"])
    return dict(min_distance_A=worst["distance_A"], at_config=worst["index"], pair=worst["pair"],
                image=worst["image"], max_over_configs_A=max(x["distance_A"] for x in rows))


def max_config_difference(a: list[dict], b: list[dict]) -> float:
    """Largest Cartesian coordinate difference between two same-length config lists (inf if
    counts, species or site types differ)."""
    if len(a) != len(b):
        return float("inf")
    worst = 0.0
    for ra, rb in zip(a, b):
        sa, sb = ra["structure"], rb["structure"]
        if ra["site_type"] != rb["site_type"] or len(sa) != len(sb) or \
                [s.species_string for s in sa] != [s.species_string for s in sb]:
            return float("inf")
        if not np.allclose(sa.lattice.matrix, sb.lattice.matrix, atol=1e-8):
            return float("inf")
        worst = max(worst, float(np.abs(sa.cart_coords - sb.cart_coords).max()))
    return worst
