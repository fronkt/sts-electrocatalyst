"""F8: prototype rules, CIF analysis, claim evaluation, Table SI-1 arithmetic."""
import pytest

from s2.f8 import structures as S
from s2.f8 import zpe

TABLE_SI1 = """Table SI-1: Zero Point Energy (ZPE) and entropy corrections [25]

  TS T∆S ZPE ∆ZPE ∆ZPE – T∆S
H2O 0,67 0 0,56 0 0
*OH + ½ H2 0,20 -0,47 0,44 -0,12 0,35
*O + H2 0,41 -0,27 0,34 -0,22 0,05
½ O2 + H2 0,73 0,05 0,32 -0,24 -0,29
H2 0,41   0,27
½ O2 0,32   0,05
O* 0   0,07
HO* 0   0,30
H* 0   0,17


""".splitlines()


def test_classify_rules():
    assert S.classify(136, {"a"}, {"f"}) == "rutile"
    assert S.classify(58, {"a"}, {"g"}) == "CaCl2"
    assert S.classify(60, {"c"}, {"d"}) == "alpha-PbO2"
    assert S.classify(164, {"a"}, {"d"}) == "CdI2"
    assert S.classify(154, {"b"}, {"c"}) == "alpha-quartz"
    assert S.classify(136, {"a"}, {"g"}) == "sg136"      # wrong anion site is not rutile
    assert S.classify(186, {"b"}, {"a", "b"}) == "sg186"


def _cif(sg, lattice, species, coords):
    from pymatgen.core import Structure
    from pymatgen.io.cif import CifWriter
    s = Structure.from_spacegroup(sg, lattice, species, coords)
    return str(CifWriter(s))


def test_analyse_cif_rutile_and_cacl2():
    from pymatgen.core import Lattice

    rut = _cif("P4_2/mnm", Lattice.tetragonal(4.737, 3.186), ["Sn", "O"], [[0, 0, 0], [0.307, 0.307, 0]])
    r = S.analyse_cif(rut, "Sn")
    assert r["sg_number_computed"] == 136 and r["prototype"] == "rutile"
    assert r["cation_wyckoff"] == ["a"] and r["anion_wyckoff"] == ["f"] and r["anion_per_cation"] == 2.0
    cacl = _cif("Pnnm", Lattice.orthorhombic(4.486, 4.537, 3.138), ["Pt", "O"], [[0, 0, 0], [0.28, 0.33, 0]])
    c = S.analyse_cif(cacl, "Pt")
    assert c["sg_number_computed"] == 58 and c["prototype"] == "CaCl2"
    ca = _cif("Pnnm", Lattice.orthorhombic(6.24, 6.43, 4.20), ["Ca", "Cl"], [[0, 0, 0], [0.275, 0.325, 0]])
    h = S.analyse_cif(ca, "Ca", anion="Cl")
    assert h["prototype"] == "CaCl2" and h["anion"] == "Cl" and h["anion_per_cation"] == 2.0


def test_formal_d_count():
    assert S.formal_d_count("Sn", 4)["d_count_outer"] == 10
    assert S.formal_d_count("Ge", 4)["d_count_outer"] == 10
    assert S.formal_d_count("Os", 4)["d_count_outer"] == 4
    assert S.formal_d_count("Pt", 4)["d_count_outer"] == 6
    assert S.formal_d_count("Ti", 4)["d_count_outer"] == 0


def test_ambient_status():
    assert S.ambient_status(0.0, "at high pressure")["ambient_pressure"] is True
    assert S.ambient_status(2.5e7, "")["ambient_pressure"] is False
    assert S.ambient_status(None, "Structure refinement of GeO2 polymorphs at high pressures")[
        "ambient_pressure"] is False
    assert S.ambient_status(None, "The crystal structure of quartz-like GeO2")["ambient_pressure"] is True


def _cod(entries):
    return {"X": {"entries": entries}}


def _e(cid, proto, ambient=True, mineral=None, chemname=None, title=None):
    return {"cod_id": cid, "prototype": proto, "ambient_pressure": ambient, "mineral": mineral,
            "chemname": chemname, "title": title, "sg_symbol_computed": "sg", "authors": "A", "year": "2000",
            "journal": "J", "doi": None, "pressure_kPa": None}


def test_evaluate_claims_binary_verdicts(tmp_path, monkeypatch):
    doc = tmp_path / "d.md"
    doc.write_text("line one\nPtO2 is not rutile here\n", encoding="utf-8")
    monkeypatch.setattr(S, "REPO", tmp_path)
    cod = _cod([_e("1", "CaCl2", ambient=False, title="beta-Pt O2: high pressure"), _e("2", "CdI2")])
    mp = {"X": {"docs": [{"sg_number": 58, "e_above_hull_eV_atom": 0.0}, {"sg_number": 136,
                                                                       "e_above_hull_eV_atom": 0.04}]}}
    base = {"formula": "X", "file": "d.md", "line": 2, "fragment": "not rutile", "assertion": "a"}
    claims = [
        {**base, "id": "c1", "subclaims": [
            {"id": "ok", "text": "t", "checks": [{"kind": "cod_type_absent", "formula": "X", "type": "rutile"},
                                                 {"kind": "mp_lowest_ehull", "formula": "X", "not_sg_number": 136}]},
            {"id": "gap", "text": "t", "checks": [{"kind": "not_checkable", "reason": "no text"}],
             "narrowed": {"text": "n", "checks": [{"kind": "mp_lowest_ehull", "formula": "X", "sg_number": 58}]}},
            {"id": "beta", "text": "t", "checks": [{"kind": "cod_type_present", "formula": "X", "type": "CaCl2",
                                                    "name_regex": r"β|\bbeta\b"}]},
            {"id": "alpha", "text": "t", "checks": [{"kind": "cod_type_present", "formula": "X", "type": "CdI2",
                                                     "name_regex": r"α|\balpha\b"}]},
            {"id": "mixed", "text": "t", "checks": [{"kind": "cod_type_present", "formula": "X", "type": "CdI2",
                                                     "ambient": True},
                                                    {"kind": "not_checkable", "reason": "r"}]},
            {"id": "d10", "text": "t", "checks": [{"kind": "formal_d_count", "element": "Sn", "oxidation_state": 4,
                                                   "expected": 10}]},
        ]},
        {**base, "id": "lost", "fragment": "absent text", "subclaims": [
            {"id": "lost-sub", "text": "t", "checks": [{"kind": "cod_type_present", "formula": "X", "type": "CdI2"}]}]},
    ]
    out = {sc["id"]: sc for c in S.evaluate_claims(claims, cod, mp, {}) for sc in c["subclaims"]}
    assert {sc["verdict"] for sc in out.values()} <= {"CLEARED", "EXCLUDED"}
    assert out["ok"]["verdict"] == "CLEARED"
    assert out["gap"]["verdict"] == "EXCLUDED" and out["gap"]["reason"] == "no text"
    assert out["gap"]["narrowed"]["verdict"] == "CLEARED"
    assert out["beta"]["verdict"] == "CLEARED"
    assert out["alpha"]["verdict"] == "EXCLUDED" and "0 matching records" in out["alpha"]["reason"]
    assert out["mixed"]["verdict"] == "EXCLUDED"          # one gap excludes a sub-claim with a passing test
    assert out["d10"]["verdict"] == "CLEARED"
    assert out["lost-sub"]["verdict"] == "EXCLUDED" and "fragment not found" in out["lost-sub"]["reason"]


def test_table_si1_parse_and_convention():
    t = zpe.parse_table_si1(TABLE_SI1)
    assert t["order"] == ["H2O", "*OH + ½ H2", "*O + H2", "½ O2 + H2", "H2", "½ O2", "O*", "HO*", "H*"]
    assert t["rows"]["*OH + ½ H2"] == [0.20, -0.47, 0.44, -0.12, 0.35]
    assert not any("OOH" in k for k in t["rows"])
    cols = zpe.species_columns(t)
    assert cols["H2O"] == {"TS": 0.67, "ZPE": 0.56} and cols["HO*"] == {"TS": 0.0, "ZPE": 0.30}
    # *OH: 0.30 - [(0.56 - 0.67) - 0.5 (0.27 - 0.41)] = 0.34 (table prints 0.35)
    assert zpe.corr_from_species(0.30, "OH", cols) == pytest.approx(0.34, abs=1e-9)
    assert zpe.corr_from_species(0.07, "O", cols) == pytest.approx(0.04, abs=1e-9)
    # inverse: +0.40 on *OOH needs ZPE - TS(HOO*) = 0.40 + 2(-0.11) - 1.5(-0.14) = 0.39
    assert zpe.implied_adsorbate(0.40, "OOH", cols) == pytest.approx(0.39, abs=1e-9)
    assert zpe.corr_from_species(zpe.implied_adsorbate(0.40, "OOH", cols), "OOH", cols) == \
        pytest.approx(0.40, abs=1e-12)


def test_pdf_token_census_counts():
    pages = ["no ZPE here 0.40 and\n0.40", "zero point energy; zero-point"]
    c = zpe.pdf_token_census(pages, [r"0\.40", r"\bZPE\b", r"zero[- ]point"])
    assert c[r"0\.40"]["n"] == 2 and c[r"\bZPE\b"]["n"] == 1 and c[r"zero[- ]point"]["n"] == 2


def test_registered_delta_is_read_from_docs43():
    d = zpe.registered_delta()
    assert d["reference_eV"] == pytest.approx(0.35) and d["range_eV"] == [0.0, 0.10]
