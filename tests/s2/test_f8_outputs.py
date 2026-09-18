"""F8: invariants of the written outputs (skipped when results/ has not been built)."""
import json

import pytest

from s2.f8.common import OUT, REPO, sha256_file

SUMMARY = OUT / "summary.json"
pytestmark = pytest.mark.skipif(not SUMMARY.exists(), reason="run `python -m s2.f8.run` first")


def _load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_every_line_classified_and_every_fragment_found():
    s = _load("summary.json")
    assert s["intercept_floor"]["summary"]["n_unclassified"] == 0
    st = _load("structures.json")
    assert all(c["located"]["found"] for c in st["claims"])
    assert all(m["category"] != "UNCLASSIFIED" for m in st["mentions"])
    assert st["curated_mentions_not_matched_by_scan"] == []


def test_structure_evidence_counts_on_face():
    st = _load("structures.json")
    for f, c in st["cod"].items():
        assert c["n_parsed"] + c["n_unparsed"] == c["n_returned"], f


def test_bib_denominators_close():
    d = _load("bib_crossref_diff.json")["summary"]
    assert d["n_with_doi"] + d["n_without_doi"] == d["n_entries"]
    assert sum(d["states"].values()) == d["n_entries"]
    assert d["n_corrected_entries_written"] == d["n_entries"] + len(d["added"])


def test_corrected_bib_parses_and_has_no_markup():
    from s2.f8 import bib
    entries = bib.parse((OUT / "references.crossref.bib").read_text(encoding="utf-8"))
    d = _load("bib_crossref_diff.json")["summary"]
    assert len(entries) == d["n_corrected_entries_written"]
    assert all("<" not in e.fields.get("title", "") and "\n" not in e.fields.get("title", "") for e in entries)
    keys = [e.key for e in entries]
    assert len(keys) == len(set(keys))


def test_manifest_hashes_match_current_cache_and_cover_every_file():
    m = _load("manifest.json")
    listed = {**m["cached_responses"], **m["cached_responses_not_read_this_run"]}
    for path, rec in listed.items():
        assert sha256_file(REPO / path) == rec["sha256"], path
    on_disk = {p.relative_to(REPO).as_posix() for d in ("crossref_cache", "source_cache")
               for p in (OUT / d).rglob("*") if p.is_file() and not p.name.endswith(".meta.json")}
    assert on_disk == set(listed)


def test_cache_paths_stay_short():
    longest = max(len(p.relative_to(REPO).as_posix()) for p in OUT.rglob("*") if p.is_file())
    assert longest <= 130, longest


BINARY = {"CLEARED", "EXCLUDED"}


def test_verdicts_are_binary_everywhere():
    s = _load("summary.json")
    v = s["verdicts"]
    assert set(v["sun_reuter_scheffler_2004"].values()) <= BINARY
    assert set(v["structure_subclaims"].values()) <= BINARY
    assert set(v["structure_narrowed_forms"].values()) <= BINARY
    assert v["ooh_plus_0.40"] in BINARY
    for name in ("summary.json", "structures.json", "sun2004.json"):
        text = (OUT / name).read_text(encoding="utf-8")
        assert "CLEARED_IN_PART" not in text and "NOT_VERIFIED" not in text, name
    sun = _load("sun2004.json")
    assert sun["claim_verdicts"] == {"SUN-crucial-statement-by-these-authors": "CLEARED",
                                     "SUN-same-wording-in-PRB-70-235402": "CLEARED"}
    vor = sun["version_of_record"]
    assert all(vor["identity_checks"].values()) and vor["identified_as_version_of_record"]
    assert vor["quotes"]["crucial"]["page"] == 2
    claim_rows = [r for r in sun["citing_lines"] if r["role"] == "CLAIM"]
    assert claim_rows and all(r["verdicts"] == sun["claim_verdicts"] for r in claim_rows)
    st = _load("structures.json")
    assert all(sc["verdict"] in BINARY for c in st["claims"] for sc in c["subclaims"])


def test_floor_range_line_is_counted():
    rows = _load("intercept_floor.json")["rows"]
    hit = [r for r in rows if r["file"] == "docs/research/2026-08-15-lit-sweep-lens-digest.md" and r["line"] == 356]
    assert len(hit) == 1 and hit[0]["quantitative_use"]


def test_docs28_label_echoes_and_note_labels():
    d = _load("docs28_doi_audit.json")
    fixed = {e["line"] for e in d["label_echoes"] if e["correction_applies"]}
    assert {60, 116} <= fixed
    note = (REPO / "docs/research/f8-clearance-2026-09-16.md").read_text(encoding="utf-8")
    assert "journal carries line breaks" not in note


def test_quotes_and_verdicts_present():
    s = _load("summary.json")
    assert s["sun2004"]["quotes"]["crucial"] is not None
    assert s["verdicts"]["docs28_corrected_dois"]["catbench"]
    assert s["verdicts"]["docs28_corrected_dois"]["jcat"]
