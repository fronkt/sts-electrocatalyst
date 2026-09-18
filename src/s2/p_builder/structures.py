"""Source structures for the four P-BUILDER families.

rutile(110) uses the registered hand-built RuO2 cell (docs/43 :1902; t2.py). The other
three families use Crystallography Open Database entries, committed byte-for-byte under
results/s2_2026-09-16/p_builder_prestate/structures/. No Materials Project access is used.
"""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import numpy as np
from pymatgen.core import Lattice, Structure
from pymatgen.io.cif import CifParser, CifWriter

from .registered import FAMILIES, RUTILE_A, RUTILE_C, RUTILE_U

COD_URL = "https://www.crystallography.net/cod/{id}.cif"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rutile_handbuilt() -> Structure:
    """The t2.py cell, site order and coordinates unchanged."""
    a, c, u = RUTILE_A, RUTILE_C, RUTILE_U
    return Structure(Lattice.tetragonal(a, c), ["Ru", "Ru", "O", "O", "O", "O"],
                     [[0, 0, 0], [.5, .5, .5], [u, u, 0], [1 - u, 1 - u, 0],
                      [.5 + u, .5 - u, .5], [.5 - u, .5 + u, .5]])


def write_rutile_cif(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    CifWriter(rutile_handbuilt()).write_file(str(path))


def fetch_cod(cod_id: int, dest: Path, timeout: float = 60.0) -> str:
    """Download a COD CIF verbatim; returns its sha256."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(COD_URL.format(id=cod_id), timeout=timeout) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _first_block(path: Path) -> dict:
    d = CifParser(str(path)).as_dict()
    return next(iter(d.values()))


def _num(value) -> float:
    return float(str(value).split("(")[0])


def cif_provenance(path: Path) -> dict:
    """Bibliographic and cell fields read from a COD CIF (as deposited)."""
    b = _first_block(path)
    authors = b.get("_publ_author_name", [])
    if isinstance(authors, str):
        authors = [authors]
    title = " ".join(str(b.get("_publ_section_title", "")).split())
    out = dict(
        cod_id=int(b.get("_cod_database_code")),
        authors=authors,
        title=title,
        journal=b.get("_journal_name_full"),
        volume=b.get("_journal_volume"),
        year=b.get("_journal_year"),
        pages="-".join(x for x in (b.get("_journal_page_first"), b.get("_journal_page_last")) if x),
        doi=b.get("_journal_paper_doi"),
        space_group_HM=b.get("_symmetry_space_group_name_H-M"),
        space_group_number=int(b["_space_group_IT_number"]) if "_space_group_IT_number" in b else None,
        a_A=_num(b["_cell_length_a"]), b_A=_num(b["_cell_length_b"]), c_A=_num(b["_cell_length_c"]),
        temperature_K=_num(b["_diffrn_ambient_temperature"]) if "_diffrn_ambient_temperature" in b else None,
        amcsd_code=b.get("_database_code_amcsd"),
        atom_sites=[dict(label=l, x=_num(x), y=_num(y), z=_num(z)) for l, x, y, z in zip(
            b["_atom_site_label"], b["_atom_site_fract_x"], b["_atom_site_fract_y"], b["_atom_site_fract_z"])],
    )
    return out


def rutile_matches_cod(cod_cif: Path, tol: float = 1e-6) -> dict:
    """Check the registered hand-built cell against COD 9007541 (a, c, u and the full structure)."""
    prov = cif_provenance(cod_cif)
    o_sites = [s for s in prov["atom_sites"] if s["label"].startswith("O")]
    u_cod = o_sites[0]["x"] if o_sites else float("nan")
    cod_struct = Structure.from_file(str(cod_cif))
    hand = rutile_handbuilt()
    same_lattice = np.allclose(cod_struct.lattice.abc, hand.lattice.abc, atol=tol)
    # every hand-built site has a COD-expanded site of the same species at the same position
    def has(site):
        for other in cod_struct:
            if other.species_string == site.species_string:
                d = cod_struct.lattice.get_all_distances(other.frac_coords, site.frac_coords)[0][0]
                if d < 1e-4:
                    return True
        return False
    return dict(
        a_cod=prov["a_A"], c_cod=prov["c_A"], u_cod=u_cod,
        a_registered=RUTILE_A, c_registered=RUTILE_C, u_registered=RUTILE_U,
        parameters_equal=bool(abs(prov["a_A"] - RUTILE_A) < tol and abs(prov["c_A"] - RUTILE_C) < tol
                              and abs(u_cod - RUTILE_U) < tol),
        n_sites_cod=len(cod_struct), n_sites_registered=len(hand),
        sites_equal=bool(same_lattice and len(cod_struct) == len(hand) and all(has(s) for s in hand)),
    )


def load_bulk(family: str, prestate_dir: Path) -> Structure:
    spec = FAMILIES[family]
    if spec["source"] == "handbuilt":
        return rutile_handbuilt()
    return Structure.from_file(str(prestate_dir / spec["structure_file"]))
