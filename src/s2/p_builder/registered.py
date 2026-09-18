"""Registered arguments (docs/43 A9.3.5, :1902) and the 2026-09-16 per-family values.

Everything the census depends on is a constant here so that the prestate, the census
and the tests read one definition. Values quoted from docs/43 carry the line number.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DOCS43 = REPO / "docs" / "43-prereg-week1-factorial.md"
T2_PY = REPO / "docs" / "research" / "2026-08-15-sampling" / "t2.py"
PRESTATE_DIR = REPO / "results" / "s2_2026-09-16" / "p_builder_prestate"
DECISION_DOC = REPO / "docs" / "research" / "s2-operating-decisions-2026-09-16" / "p-builder.md"
CODE_DIR = Path(__file__).resolve().parent

# 2026-09-16 decision: SlabGenerator receives the source file's cell as deposited. The family
# Miller indices are conventional-cubic-cell indices and SlabGenerator reads (hkl) in the basis
# of the cell it is given, so no primitive or standard-cell reduction precedes it.
BULK_CELL_SETTING = ("source cell as deposited (COD conventional cell; registered hand-built rutile cell); "
                     "no primitive or standard-cell reduction before SlabGenerator")

# docs/43 :1902 -- "SlabGenerator(min_slab_size=9., min_vacuum_size=15., center_slab=True,
# primitive=True)"; t2.py also passes lll_reduce=False, which is the pymatgen default.
SLABGEN_KWARGS = dict(min_slab_size=9.0, min_vacuum_size=15.0, center_slab=True,
                      lll_reduce=False, primitive=True)

# docs/43 :1902 -- "AdsorbateSiteFinder(slab).generate_adsorption_structures(mol,
# repeat=[1,1,1], find_args={"distance": 2.0})"
ENUM_REPEAT = [1, 1, 1]
ENUM_FIND_ARGS = {"distance": 2.0}

# docs/43 :1902 -- "SpacegroupAnalyzer(structure, symprec=1e-3)"; an operation is
# adsorbate-invariant when it maps every adsorbate atom onto itself mod lattice
# (distance < 1e-3) and has a -1 eigenvalue.
SYMPREC = 1e-3
SELF_MAP_TOL_A = 1e-3
# Eigenvalue tolerance: not stated in docs/43; t2.py (the registered run) uses 1e-6.
EIGEN_TOL = 1e-6

# docs/43 :1902 -- O; OH (d_OH = 0.98 A, upright); OOH bent as in t2.py
# ([[0,0,0],[1.29,0,0.7],[1.29,0.9,1.0]]).
ADSORBATES = {
    "O": (["O"], [[0.0, 0.0, 0.0]]),
    "OH": (["O", "H"], [[0.0, 0.0, 0.0], [0.0, 0.0, 0.98]]),
    "OOH": (["O", "O", "H"], [[0.0, 0.0, 0.0], [1.29, 0.0, 0.7], [1.29, 0.9, 1.0]]),
}
ADSORBATE_ORDER = ("O", "OH", "OOH")

# docs/43 :1902 -- hand-built RuO2 rutile cell a = 4.4919, c = 3.1066, u = 0.3058.
RUTILE_A, RUTILE_C, RUTILE_U = 4.4919, 3.1066, 0.3058

# Surface-site height threshold AdsorbateSiteFinder uses by default (pymatgen); used here
# only to describe a termination, never to change the enumerator.
ASF_DEFAULT_HEIGHT_A = 0.9

# Per-family values fixed by the 2026-09-16 operating decision
# (docs/research/s2-operating-decisions-2026-09-16/p-builder.md).
# termination: either {"slab_index": i} (the registered t2.py selection) or
# {"surface_species": {...}} -- the species multiset of the AdsorbateSiteFinder surface
# sites of the top surface; exactly one generated slab must match.
FAMILIES = {
    "rutile110": dict(
        label="rutile(110)", formula="RuO2", miller=(1, 1, 0),
        source="handbuilt", structure_file="structures/rutile_RuO2_handbuilt.cif",
        provenance_cif="structures/cod_9007541_RuO2.cif", cod_id=9007541,
        termination={"slab_index": 0}, blind=False),
    "perovskite001": dict(
        label="perovskite(001)", formula="SrTiO3", miller=(0, 0, 1),
        source="cod", structure_file="structures/cod_9006864_SrTiO3.cif", cod_id=9006864,
        termination={"surface_species": {"O": 2, "Ti": 1}}, blind=True),
    "spinel001": dict(
        label="spinel(001)", formula="Co3O4", miller=(0, 0, 1),
        source="cod", structure_file="structures/cod_9005887_Co3O4.cif", cod_id=9005887,
        termination={"surface_species": {"Co": 2, "O": 4}}, blind=True),
    "fcc111": dict(
        label="fcc(111)", formula="Pt", miller=(1, 1, 1),
        source="cod", structure_file="structures/cod_9008480_Pt.cif", cod_id=9008480,
        termination={"surface_species": {"Pt": 4}}, blind=True),
}
FAMILY_ORDER = ("rutile110", "perovskite001", "spinel001", "fcc111")
BLIND_FAMILIES = tuple(k for k in FAMILY_ORDER if FAMILIES[k]["blind"])
