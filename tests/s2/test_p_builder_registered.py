"""P-BUILDER: the constants used are the registered ones (docs/43 :1902, t2.py)."""
import ast
import re

from s2.p_builder import registered as R
from s2.p_builder.structures import rutile_handbuilt, rutile_matches_cod


def _t2_calls():
    tree = ast.parse(R.T2_PY.read_text(encoding="utf-8"))
    calls = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            calls.setdefault(name, []).append(node)
    return tree, calls


def test_slabgenerator_kwargs_match_t2():
    _, calls = _t2_calls()
    (sg,) = calls["SlabGenerator"]
    kw = {k.arg: ast.literal_eval(k.value) for k in sg.keywords}
    assert kw == R.SLABGEN_KWARGS
    assert ast.literal_eval(sg.args[1]) == (1, 1, 0)


def test_enumerator_call_matches_t2():
    _, calls = _t2_calls()
    (gen,) = calls["generate_adsorption_structures"]
    kw = {k.arg: ast.literal_eval(k.value) for k in gen.keywords}
    assert kw == {"repeat": R.ENUM_REPEAT, "find_args": R.ENUM_FIND_ARGS}
    (sga,) = calls["SpacegroupAnalyzer"]
    assert ast.literal_eval(sga.keywords[0].value) == R.SYMPREC


def test_adsorbate_geometries_match_t2():
    src = R.T2_PY.read_text(encoding="utf-8")
    assert '("OH", Molecule(["O","H"],[[0,0,0],[0,0,0.98]]))' in src
    assert '("OOH", Molecule(["O","O","H"],[[0,0,0],[1.29,0,0.7],[1.29,0.9,1.0]]))' in src
    assert R.ADSORBATES["OH"][1] == [[0, 0, 0], [0, 0, 0.98]]
    assert R.ADSORBATES["OOH"][1] == [[0, 0, 0], [1.29, 0, 0.7], [1.29, 0.9, 1.0]]


def test_docs43_line_1902_registers_the_same_arguments():
    line = R.DOCS43.read_text(encoding="utf-8").splitlines()[1901]
    assert line.startswith("**Two numbers, never one product**")
    for s in ['generate_adsorption_structures(mol, repeat=[1,1,1], find_args={"distance": 2.0})',
              "`[[0,0,0],[1.29,0,0.7],[1.29,0.9,1.0]]`", "SpacegroupAnalyzer(structure, symprec=1e-3)",
              "min_slab_size=9., min_vacuum_size=15., center_slab=True, primitive=True",
              "a = 4.4919, c = 3.1066, u = 0.3058", "distance < 1e-3"]:
        assert s in line, s
    assert re.search(r"d_OH = 0\.98 Å, upright", line)


def test_rutile_handbuilt_cell_is_cod_9007541():
    chk = rutile_matches_cod(R.PRESTATE_DIR / R.FAMILIES["rutile110"]["provenance_cif"])
    assert chk["parameters_equal"] and chk["sites_equal"]
    assert len(rutile_handbuilt()) == 6


def test_blind_family_list():
    assert R.BLIND_FAMILIES == ("perovskite001", "spinel001", "fcc111")
