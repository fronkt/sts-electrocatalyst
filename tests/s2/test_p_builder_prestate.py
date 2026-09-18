"""P-BUILDER prestate: hashes, denominators, decision record, blindness guard, determinism."""
import json
import re
from fractions import Fraction

import numpy as np
import pytest

from s2.p_builder import decision
from s2.p_builder.enumeration import enumerate_configs, enumerator_internal_tolerances, max_config_difference
from s2.p_builder.registered import ADSORBATE_ORDER, DECISION_DOC, FAMILY_ORDER, PRESTATE_DIR, REPO
from s2.p_builder.run_census import load_prestate_configs, verify_manifest
from s2.p_builder.structures import sha256_file

DEN = json.loads((PRESTATE_DIR / "denominators.json").read_text(encoding="utf-8"))
DEC = json.loads((PRESTATE_DIR / "decision.json").read_text(encoding="utf-8"))


def test_manifest_matches_census_inputs_and_code():
    chk = verify_manifest(PRESTATE_DIR)
    assert chk["mismatches"] == {} and chk["n_census_inputs"] == 27 and chk["n_code_files"] == 10


def test_manifest_records_versions_and_inputs():
    man = json.loads((PRESTATE_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert man["inputs_sha256"]["docs/research/2026-08-15-sampling/t2.py"] == sha256_file(
        REPO / "docs/research/2026-08-15-sampling/t2.py")
    for k in ("pymatgen", "numpy", "scipy", "spglib", "python"):
        assert man["versions"][k]
    for rel, h in man["prestate_sha256"].items():
        assert sha256_file(PRESTATE_DIR / rel) == h, rel


def test_denominators_equal_config_files():
    for fam in FAMILY_ORDER:
        rec = DEN["families"][fam]
        ns = set()
        for ads in ADSORBATE_ORDER:
            data = json.loads((PRESTATE_DIR / rec["adsorbates"][ads]["configs_file"]).read_text(encoding="utf-8"))
            assert len(data) == rec["adsorbates"][ads]["n_configurations"]
            assert sum(rec["adsorbates"][ads]["site_types"].values()) == len(data)
            ns.add(len(data))
        assert len(ns) == 1  # same sites for every adsorbate


def test_denominator_values():
    got = {f: DEN["families"][f]["adsorbates"]["O"]["n_configurations"] for f in FAMILY_ORDER}
    assert got == {"rutile110": 10, "perovskite001": 5, "spinel001": 13, "fcc111": 4}


def test_structure_hashes_recorded():
    for fam in FAMILY_ORDER:
        b = DEN["families"][fam]["bulk"]
        assert b["sha256"] == sha256_file(PRESTATE_DIR / b["file"])


def test_decision_json_is_the_decision_module():
    assert DEC == json.loads(json.dumps(decision.decision_record(DEN)))


@pytest.mark.parametrize("retained,n,k,expected", [
    (9, 10, 9, "HELD"), (5, 10, 9, "FALSIFIED"), (6, 10, 9, "NOT HELD / NOT FALSIFIED"),
    (8, 13, 8, "HELD"), (7, 13, 8, "NOT HELD / NOT FALSIFIED"), (6, 13, 8, "FALSIFIED"),
    (2, 4, 4, "FALSIFIED"), (3, 4, 4, "NOT HELD / NOT FALSIFIED")])
def test_verdict_rule(retained, n, k, expected):
    assert decision.verdict(retained, n, k) == expected
    assert (Fraction(retained, n) <= decision.F_LINE) == (expected == "FALSIFIED")


def test_reading_is_recorded_with_the_pooled_alternative():
    assert DEC["reading"]["decision"].startswith("per adsorbate")
    assert "pooled" in DEC["reading"]["alternative_named"]
    pooled = {f: DEC["families"][f]["pooled_reading_not_used"] for f in FAMILY_ORDER}
    assert pooled["spinel001"]["fraction"] == "16/39" and pooled["spinel001"]["at_or_below_half_line"]
    assert pooled["spinel001"]["min_upright_retained_above_half_line_if_pooled"] == 10
    assert pooled["rutile110"]["fraction"] == "18/30" and not pooled["rutile110"]["at_or_below_half_line"]
    assert [pooled[f]["at_or_below_half_line"] for f in FAMILY_ORDER] == [False, False, True, False]


def _used_names(src):
    import ast
    names = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
    return names


def test_enumeration_and_prestate_never_touch_the_census():
    for name in ("enumeration.py", "prestate.py", "structures.py", "decision.py", "registered.py"):
        used = _used_names((REPO / "src/s2/p_builder" / name).read_text(encoding="utf-8"))
        assert "SpacegroupAnalyzer" not in used, name
        assert not used & {"census", "analyse_configuration", "census_family"}, name


@pytest.mark.parametrize("fam", FAMILY_ORDER)
def test_enumerator_is_deterministic_on_saved_slab(fam):
    from pymatgen.core.surface import Slab
    slab = Slab.from_dict(json.loads((PRESTATE_DIR / "slabs" / f"{fam}.json").read_text(encoding="utf-8")))
    assert max_config_difference(enumerate_configs(slab, "O"), load_prestate_configs(PRESTATE_DIR, fam, "O")) == 0.0


def test_enumerator_internals_and_reduction_group():
    live = enumerator_internal_tolerances()
    assert live == DEN["enumerator_internal"]
    assert (live["symm_reduce_symprec"], live["symm_reduce_default"]) == (0.1, 0.01)
    assert live["symm_reduce_matches_fractional_coords_at_threshold"] is True
    for fam in FAMILY_ORDER:
        cs = DEN["families"][fam]["clean_slab_symmetry"]
        e = cs["at_enumerator_symprec"]
        assert e["symprec"] == 0.1 and e["operation_set_identical_to_census_symprec"] is True
        assert e["n_operations"] == cs["n_operations"]


def test_coverage_per_family():
    got = {f: DEN["families"][f]["coverage"]["adsorbates_per_top_metal_atom"] for f in FAMILY_ORDER}
    assert got == {"rutile110": "1/2", "perovskite001": "1/1", "spinel001": "1/2", "fcc111": "1/4"}


def test_primitive_input_alternative():
    pt = DEN["families"]["fcc111"]["primitive_input_alternative"]
    assert pt["shares_source_cartesian_frame"] and pt["primitive_bulk_n_sites"] == 1
    assert abs(abs(float(np.dot(pt["plane_normal_deposited_cell"], pt["plane_normal_primitive_cell"]))) - 1) < 1e-5
    (c,) = pt["candidates"]
    assert c["n_configurations"] == 4 and c["site_types"] == {"ontop": 1, "bridge": 1, "hollow": 2}
    assert abs(c["reduced_in_plane_basis"]["shortest_A"] - 2.7741) < 1e-3
    o1o2 = float(np.hypot(1.29, 0.7))
    assert c["OOH_min_image_distance"]["min_distance_A"] < o1o2 + 0.2
    assert DEN["families"]["fcc111"]["adsorbates"]["OOH"]["min_adsorbate_image_distance"]["min_distance_A"] > 4.0
    sp = DEN["families"]["spinel001"]["primitive_input_alternative"]
    assert sp["shares_source_cartesian_frame"]
    dot = abs(float(np.dot(sp["plane_normal_deposited_cell"], sp["plane_normal_primitive_cell"])))
    assert abs(dot - 1 / np.sqrt(3)) < 1e-5  # primitive (001) is a cubic {111} plane
    assert all(abs(x["reduced_in_plane_basis"]["angle_deg"] - 60) < 1e-6 for x in sp["candidates"])


def test_decision_doc_carries_the_numbers():
    doc = DECISION_DOC.read_text(encoding="utf-8")
    for fam in FAMILY_ORDER:
        d = DEC["families"][fam]
        n = DEN["families"][fam]["adsorbates"]["O"]["n_configurations"]
        st = DEN["families"][fam]["adsorbates"]["O"]["site_types"]
        row = f"| {DEN['families'][fam]['label']} |"
        lines = [l for l in doc.splitlines() if l.startswith(row)]
        assert lines, fam
        joined = " ".join(lines)
        assert f"{n}" in joined and d["X"]["fraction"] in joined, fam
        assert f"{st['ontop']}/{st['bridge']}/{st['hollow']}" in joined, fam


def test_decision_doc_names_every_slab_config_and_structure_file_by_full_sha256():
    doc = DECISION_DOC.read_text(encoding="utf-8")
    named = dict(re.findall(r"^\| `(results/s2_2026-09-16/p_builder_prestate/[^`]+)` \| `([0-9a-f]{64})` \|$", doc, flags=re.M))
    on_disk = {p.relative_to(REPO).as_posix(): sha256_file(p) for d in ("slabs", "configs", "structures")
               for p in sorted((PRESTATE_DIR / d).glob("*"))}
    assert named == on_disk and sum(1 for k in named if "/slabs/" in k) == 8


def test_decision_doc_tables_are_the_rendered_tables():
    doc = DECISION_DOC.read_text(encoding="utf-8").splitlines()
    rendered = (PRESTATE_DIR / "tables.md").read_text(encoding="utf-8").splitlines()
    header = {i - 1 for i, l in enumerate(rendered) if l.startswith("|---")}
    rows = [l for i, l in enumerate(rendered) if l.startswith("| ") and i not in header]
    rows += [l for l in rendered if l.startswith("> ")]
    missing = [l for l in rows if l not in doc]
    assert not missing, missing[:2]


def test_ooh_bound_and_reduced_basis():
    ob = DEC["OOH_bound"]
    assert all(ob["holds"].values())
    assert abs(ob["O2_max_shift_A"] - 2.58) < 1e-9 and abs(ob["H_mirror_shift_A"] - 1.8) < 1e-9
    sp = DEN["families"]["spinel001"]["slab"]["reduced_in_plane_basis"]
    assert abs(sp["lengths_A"][0] - sp["lengths_A"][1]) < 1e-6 and abs(sp["angle_deg"] - 90) < 1e-6
