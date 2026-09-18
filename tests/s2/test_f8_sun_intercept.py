"""F8: quote location in PDF text, arXiv/APS parsing, 3.18 / 0.12 line census."""
import json

from s2.f8 import intercept_floor as IF
from s2.f8 import sun2004


def test_find_quotes_handles_hyphenation_and_ligatures():
    pages = [
        "intro text",
        "At this point we would further like to emphasize that the struc-\ntural relaxation allowed for any "
        "symmetry breaking at the surface. This was found to be crucial to obtain the correct energetics and "
        "structures, which often involve sig-",
        "the energy gain by the tilting\nis 0.1 eV/H atom compared to the higher-symmetry, up-\nright conﬁguration.",
    ]
    q = sun2004.find_quotes(pages)
    assert q["symmetry_breaking_allowed"]["page"] == 2
    assert q["crucial"]["page"] == 2
    assert q["tilt_energy"]["page"] == 3
    assert "upright configuration" in q["tilt_energy"]["match"]


def test_find_quotes_absent_is_none():
    q = sun2004.find_quotes(["nothing relevant"])
    assert all(v is None for v in q.values())


def test_published_version_requires_identity_not_merely_matching_quote():
    first = ("PHYSICAL REVIEW B 70, 235402 (2004)\nQiang Sun, Karsten Reuter, Matthias Scheffler\n"
             "DOI: 10.1103/PhysRevB.70.235402")
    assert all(sun2004.version_of_record_checks([first]).values())
    assert not all(sun2004.version_of_record_checks([first.replace("2004", "2003")]).values())
    assert not all(sun2004.version_of_record_checks([first.replace("Qiang Sun", "Someone Else")]).values())
    assert not all(sun2004.version_of_record_checks([first.replace("10.1103", "10.0000")]).values())
    assert not any(sun2004.version_of_record_checks([]).values())


def test_parse_arxiv_atom():
    xml = ("<feed><title>q</title><entry><id>http://arxiv.org/abs/cond-mat/0309714v1</id>"
           "<published>2003-09-30T15:37:23Z</published><title>Hydrogen adsorption at RuO2(110)</title>"
           "<summary> The oxide surface </summary><author><name>Qiang Sun</name></author>"
           "<author><name>Karsten Reuter</name></author></entry></feed>")
    a = sun2004.parse_arxiv_atom(xml)
    assert a["published"].startswith("2003-09-30") and a["authors"] == ["Qiang Sun", "Karsten Reuter"]
    assert a["summary"] == "The oxide surface"


def test_parse_aps_page_dates_and_abstract():
    html = ('<meta content="The oxide surface binds H$_2$." property="og:description" />'
            "<div>Received 17 September 2003</div><span>Published 2 December, 2004</span>")
    m = sun2004.parse_aps_page(html)
    assert m == {"received": "2003-09-17", "published": "2004-12-02",
                 "abstract": "The oxide surface binds H$_2$."}


def test_jaccard_ignores_tex():
    assert sun2004.jaccard("oxide surface hydrogen", "oxide surface hydrogen $\\mathrm{Ru}$") == 1.0
    assert sun2004.jaccard("alpha beta", "gamma delta") == 0.0


def test_patterns():
    p318, p012 = IF.PATTERNS["intercept_3.18"], IF.PATTERNS["value_0.12"]
    assert p318.search("pooled 3.18 ± 0.12 eV") and not p318.search("3.185 eV")
    assert p012.search("a widened ±0.12 V η gate") and p012.search("≈0.12 V")
    assert p012.search("the ~0.12 V code-to-code floor") and p012.search("code-level floor")
    assert not p012.search("0.125 V") and not p012.search("10.12 eV")
    # ranges, millivolts and the floor named in words
    assert p012.search("a third data point for the ≈0.12-0.30 V irreducible band")
    assert p012.search("0.12–0.3 eV") and p012.search("±120 mV") and p012.search("irreducible band")
    assert not p012.search("range ≤ 0.12 μ_B") and not p012.search("0.12 % of the balance")
    assert not p012.search("1120 mV") and not p012.search("15 irreducible k-points")


def test_sweep_lists_bare_values_the_patterns_miss(tmp_path):
    (tmp_path / "a.md").write_text("range ≤ 0.12 μ_B\n±0.12 V gate\nnothing\n0.125 V\n", encoding="utf-8")
    rows = IF.sweep([tmp_path / "a.md"], root=tmp_path)
    assert [(r["file"], r["line"]) for r in rows] == [("a.md", 1)]


def test_classify_line_file_and_unclassified(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("x\nz = (c_M − 3.18)/0.12 gate\nfoo 3.18 bar\n", encoding="utf-8")
    (tmp_path / "docs" / "gen.json").write_text(json.dumps({"t": "3.18 ± 0.12 eV"}), encoding="utf-8")
    paths = [tmp_path / "docs" / "a.md", tmp_path / "docs" / "gen.json"]
    rows = IF.hits(paths, root=tmp_path)
    classes = {"files": [{"glob": "docs/gen.json", "class": "GENERATED_COPY"}],
               "lines": [{"file": "docs/a.md", "line": 2, "fragment": "(c_M − 3.18)/0.12",
                          "class": "LIVE_QUANTITATIVE"}]}
    out = IF.classify(rows, classes, root=tmp_path)
    by = {(r["file"], r["line"]): r for r in out}
    assert by[("docs/a.md", 2)]["class"] == "LIVE_QUANTITATIVE" and by[("docs/a.md", 2)]["quantitative_use"]
    assert by[("docs/a.md", 3)]["class"] == "UNCLASSIFIED"
    assert by[("docs/gen.json", 1)]["class"] == "GENERATED_COPY"
    s = IF.summarise(out)
    assert s["n_unclassified"] == 1 and s["n_quantitative_lines"] == 1 and s["n_matching_lines"] == 3


def test_classify_fragment_mismatch(tmp_path):
    (tmp_path / "a.md").write_text("3.18 changed text\n", encoding="utf-8")
    rows = IF.hits([tmp_path / "a.md"], root=tmp_path)
    out = IF.classify(rows, {"files": [], "lines": [{"file": "a.md", "line": 1, "fragment": "original",
                                                      "class": "DISPOSITION"}]}, root=tmp_path)
    assert out[0]["class"] == "FRAGMENT_MISMATCH"
