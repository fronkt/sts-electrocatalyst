"""F8: text normalisation, BibTeX round trip, registrar records, field comparison, cache."""
import json

import pytest

from s2.f8 import bib, bibcheck
from s2.f8.common import KEY_STEM_MAX, CacheMiss, Fetcher, cache_key, migrate_cache_names, sha256_bytes
from s2.f8.registry import Record, from_crossref, from_datacite
from s2.f8.textnorm import clean_markup, fold, norm_pages, title_key


def test_clean_markup_sub_and_mathml():
    raw = "Atomistic Insights into the Activity of Hollandite IrO\n                    <sub>2</sub>\n   Surfaces"
    assert clean_markup(raw) == "Atomistic Insights into the Activity of Hollandite IrO2 Surfaces"
    mml = ('Hydrogen adsorption on<mml:math xmlns:mml="x"><mml:mi>Ru</mml:mi><mml:msub><mml:mi>O</mml:mi>'
           '<mml:mn>2</mml:mn></mml:msub><mml:mo>(</mml:mo><mml:mn>110</mml:mn><mml:mo>)</mml:mo>'
           '</mml:math>: Density-functional calculations')
    assert clean_markup(mml) == "Hydrogen adsorption on RuO2(110): Density-functional calculations"
    assert clean_markup("A &amp; B") == "A & B"


def test_fold_and_pages():
    assert fold("Nørskov") == "norskov"
    assert fold("García-Mota") == "garciamota"
    assert norm_pages("4827–4833") == "4827-4833"
    assert title_key("<i>Ab initio</i> random") == title_key("ab initio RANDOM")


def test_bib_parse_roundtrip_and_escape():
    text = "@article{k1,\n  title = {A {nested} title},\n  author = {Xu},\n  doi = {10.1/x_y}\n}\n"
    (e,) = bib.parse(text)
    assert e.key == "k1" and e.fields["title"] == "A {nested} title" and e.line == 1
    out = bib.format_entry("article", "k2", [("title", "R&D 5% #1"), ("doi", "10.1/x_y"), ("volume", "")])
    (e2,) = bib.parse(out)
    assert e2.fields["title"] == r"R\&D 5\% \#1"
    assert e2.fields["doi"] == "10.1/x_y"          # verbatim field, not escaped
    assert "volume" not in e2.fields               # empty values dropped


def _cr_msg(**kw):
    m = {"title": ["IrO\n<sub>2</sub>\nSurfaces"], "author": [
        {"family": "Lee", "given": "A", "sequence": "first"}, {"family": "Kim", "given": "B"}],
        "container-title": ["Advanced Science"], "volume": "13", "article-number": "e14939",
        "published-online": {"date-parts": [[2025, 12]]}, "published-print": {"date-parts": [[2026, 1]]},
        "issued": {"date-parts": [[2025, 12]]}, "type": "journal-article", "issue": "3",
        "publisher": "Wiley"}
    m.update(kw)
    return m


def test_from_crossref_year_precedence_and_article_number():
    r = from_crossref("10.1/a", _cr_msg())
    assert r.year == 2026                           # print wins over online
    assert r.pages == "e14939"
    assert r.title == "IrO2 Surfaces"
    assert r.first_family == "Lee"


def test_compare_entry_statuses_and_flags():
    rec = from_crossref("10.1/a", _cr_msg())
    e = bib.Entry("article", "lee", {"title": "IrO\n<sub>2</sub>\nSurfaces", "author": "Lee", "year": "2026",
                                     "journal": "Advanced Science", "volume": "13", "pages": "e14939"})
    c = bibcheck.compare_entry(e, rec)
    assert set(c["fields"].values()) == {"MATCH"}
    assert {"AUTHORS_TRUNCATED", "ISSUE_MISSING", "PRINT_ONLINE_YEAR_SPLIT",
            "TITLE_MARKUP_OR_WHITESPACE_IN_BIB"} <= set(c["flags"])
    e.fields["title"] = "IrO2 Surfaces"
    assert bibcheck.compare_entry(e, rec)["fields"]["title"] == "MARKUP"
    e.fields["title"] = "iro2 surfaces"
    assert bibcheck.compare_entry(e, rec)["fields"]["title"] == "CASE"
    e.fields["title"] = "Multifunctional robotic fish"
    e.fields["year"] = "2025"
    c = bibcheck.compare_entry(e, rec)
    assert c["fields"]["title"] == "MISMATCH" and c["fields"]["year"] == "MISMATCH"


def test_datacite_journal_compares_against_publisher():
    rec = from_datacite("10.5281/zenodo.1", {"titles": [{"title": "Data"}], "creators": [
        {"familyName": "Cai", "givenName": "F"}], "publicationYear": 2026, "publisher": "Zenodo",
        "types": {"resourceTypeGeneral": "Dataset"}})
    e = bib.Entry("misc", "cai", {"title": "Data", "author": "Cai", "year": "2026", "journal": "Zenodo"})
    assert bibcheck.compare_entry(e, rec)["fields"]["journal"] == "MATCH"


def test_corrected_entry_has_full_authors_and_parses():
    rec = from_crossref("10.1/a", _cr_msg())
    out = bibcheck.corrected_entry(bib.Entry("article", "lee"), rec)
    (e,) = bib.parse(out)
    assert e.fields["author"] == "Lee, A and Kim, B"
    assert e.fields["number"] == "3" and e.fields["title"] == "IrO2 Surfaces"


def test_fetcher_offline_cache(tmp_path):
    f = Fetcher(tmp_path, offline=True)
    with pytest.raises(CacheMiss):
        f.get("https://example.org/x", "k", "json")
    body = b'{"a": 1}'
    (tmp_path / "k.json").write_bytes(body)
    (tmp_path / "k.meta.json").write_text(json.dumps({"url": "https://example.org/x", "status": 200,
                                                      "fetched_utc": "t", "sha256": sha256_bytes(body)}))
    r = f.get("https://example.org/x", "k", "json")
    assert r.json() == {"a": 1} and f.n_cached == 1 and f.n_network == 0
    (tmp_path / "k.json").write_bytes(b"tampered")
    with pytest.raises(RuntimeError):
        f.get("https://example.org/x", "k", "json")


def test_cache_key_is_stable_and_distinct():
    assert cache_key("10.1/A(95)") == cache_key("10.1/A(95)")
    assert cache_key("10.1/a_b") != cache_key("10.1/a.b")
    long_a = "formula=SnO2&_fields=" + "x" * 300
    long_b = "formula=SnO2&_fields=" + "x" * 299 + "y"
    ka, kb = cache_key(long_a, "mp_summary_"), cache_key(long_b, "mp_summary_")
    assert len(ka) <= KEY_STEM_MAX + 12 and ka != kb and ka.startswith("mp_summary_formula_sno2")


def test_migrate_cache_names_renames_legacy_keys(tmp_path):
    import hashlib
    text = "formula=PtO2&_fields=material_id,formula_pretty,symmetry,energy_above_hull,is_stable,theoretical"
    tag = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    stem = "mp_summary_" + "formula_pto2__fields_material_id_2cformula_pretty_2csymmetry_2cenergy_above_hull_2cis"
    legacy = f"{stem}__{tag}"
    body = b'{"data": []}'
    (tmp_path / f"{legacy}.json").write_bytes(body)
    (tmp_path / f"{legacy}.meta.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cod_1008935.cif").write_bytes(b"cif")
    renamed = migrate_cache_names(tmp_path)
    assert len(renamed) == 2
    new = f"{stem[:KEY_STEM_MAX]}__{tag}"
    assert (tmp_path / f"{new}.json").read_bytes() == body and (tmp_path / f"{new}.meta.json").exists()
    assert (tmp_path / "cod_1008935.cif").exists()
    assert migrate_cache_names(tmp_path) == []           # idempotent
    (tmp_path / f"{legacy}.json").write_bytes(body)      # a second copy under the old name collides
    with pytest.raises(RuntimeError):
        migrate_cache_names(tmp_path)


def test_manifest_fails_instead_of_skipping(tmp_path, monkeypatch):
    from s2.f8 import run
    monkeypatch.setattr(run, "OUT", tmp_path)
    monkeypatch.setattr(run, "REPO", tmp_path)
    cache = tmp_path / "crossref_cache"
    cache.mkdir()
    (tmp_path / "source_cache").mkdir()
    body = b"{}"
    (cache / "k.json").write_bytes(body)
    (cache / "k.meta.json").write_text(json.dumps({"url": "u", "status": 200, "fetched_utc": "t",
                                                   "sha256": sha256_bytes(body)}), encoding="utf-8")
    (cache / "stale.json").write_bytes(body)
    (cache / "stale.meta.json").write_text(json.dumps({"url": "v", "status": 406, "fetched_utc": "t",
                                                       "sha256": sha256_bytes(body)}), encoding="utf-8")
    m = run.manifest([], {cache / "k.json"})
    assert m["n_cached_responses"] == 1 and m["n_cached_responses_not_read_this_run"] == 1
    with pytest.raises(RuntimeError):                     # a body read this run that the walk did not list
        run.manifest([], {cache / "k.json", cache / "missing.json"})
    with pytest.raises(RuntimeError):                     # an unreadable repository input
        run.manifest([tmp_path / "no-such-input.md"], set())
    (cache / "orphan.json").write_bytes(body)             # a body without metadata
    with pytest.raises(RuntimeError):
        run.manifest([], {cache / "k.json"})


def test_label_echoes_links_same_label_and_resolves_by_topic(monkeypatch):
    rows = [
        {"line": 3, "doi": "10.1021/acscatal.0c03865", "state": "RESOLVED",
         "flags": ["LABEL_YEAR_NOT_IN_REGISTRAR_YEARS"], "label_years": [2021, 2023], "registrar_years": [2020],
         "label_author_match": ["exner"], "journal": "ACS Catalysis",
         "title": "A Universal Descriptor for the Screening of Electrode Materials"},
        {"line": 3, "doi": "10.1021/acscatal.2c03997", "state": "RESOLVED", "flags": [], "label_years": [2021, 2023],
         "registrar_years": [2023], "journal": "ACS Catalysis", "title": "G_max"},
    ]
    lines = ["- **F2. G_max descriptor** from the diagrams (Exner, ACS Catal. 2021/2023; Acc. Chem. Res. 2024)",
             "LOM pathways (Grimaud 2017; Exner pitfalls 2021)",
             "Exner G_max 2021/2023 (10.1021/acscatal.0c03865 / 10.1021/acscatal.2c03997)",
             "Paywalled items: Man 2011 tables · Exner ACS Catal. 2021/2023 · Tripkovic 2018"]
    other = {"DOI": "10.1021/acscatal.1c03893", "title": ["Chlorine Evolution on Pt Single Atoms"],
             "container-title": ["ACS Catalysis"], "issued": {"date-parts": [[2021]]},
             "author": [{"family": "Lim"}, {"family": "Exner"}]}
    monkeypatch.setattr(bibcheck, "search", lambda _f, _q: [other])
    out = {e["line"]: e for e in bibcheck.label_echoes(lines, rows, None)}
    assert sorted(out) == [1, 2, 4]
    assert out[1]["status"] == "SAME_LABEL" and out[1]["resolution"] == "TOPIC_MATCH"
    assert out[1]["source_line_title_words"] == ["descriptor"] and out[1]["correction_applies"]
    assert out[1]["other_works_same_author_journal_year"]["2021"][0]["author_position"] == 2
    assert out[2]["status"] == "AUTHOR_AND_YEAR_ONLY" and not out[2]["correction_applies"]
    assert out[4]["resolution"] == "SAME_LABEL_STRING_AS_LINE_1" and out[4]["correction_applies"]
    assert rows[0]["wrong_label_years"] == [2021]


def test_docs28_audit_flags(monkeypatch):
    recs = {
        "10.1021/acscatal.0c03865": Record("10.1021/acscatal.0c03865", "crossref", 200, title="A Universal Descriptor",
                                          authors=[{"family": "Exner"}], year_print=2020, year_issued=2020,
                                          journal="ACS Catalysis"),
        "10.1016/j.jcat.2025.115963": Record("10.1016/j.jcat.2025.115963", "crossref", 200,
                                            title="Contents continued", journal="Journal of Catalysis"),
    }

    def fake_lookup(_f, doi):
        return recs.get(doi, Record(doi, "none", 404))
    monkeypatch.setattr(bibcheck, "lookup", fake_lookup)
    lines = ["Beyond-CHE: Exner G_max 2021 (10.1021/acscatal.0c03865) · x",
             "a 2025 GC-DFT study, J. Catal. 10.1016/j.jcat.2025.115963-range) and more"]
    rows = bibcheck.audit_docs28(lines, None)
    assert rows[0]["state"] == "RESOLVED"
    assert "LABEL_YEAR_NOT_IN_REGISTRAR_YEARS" in rows[0]["flags"]
    assert rows[0]["label_author_match"] == ["exner"]
    assert rows[1]["state"] == "NOT_FOUND" and rows[1]["doi"] == "10.1016/j.jcat.2025.115963-range"
    assert rows[1]["stem_record"]["title"] == "Contents continued"
    assert rows[1]["stem_record"]["n_authors"] == 0


def test_normalise_doi_trailing_punctuation():
    assert bibcheck.normalise_doi("10.1016/0039-6028(95)01252-4),") == "10.1016/0039-6028(95)01252-4"
    assert bibcheck.normalise_doi("10.1021/JP047349J**") == "10.1021/jp047349j"
