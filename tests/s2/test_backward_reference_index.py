"""Derivation and truncated-prefix contracts for the backward-reference index."""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from s2.literature import backward_reference_index as bri

NUMBERED_GROUP = {
    "group_id": "doc_si-ref-1",
    "parent_doi": "10.1000/parent",
    "document_id": "doc_si",
    "document_role": "SUPPORTING_INFORMATION",
    "reference_label": "1",
    "reference_ordinal": None,
    "label_kind": "PRINTED_NUMERIC",
    "source_pdf_pages": [48],
    "source_text_line_start": 10,
    "source_text_line_end": 12,
    "bibliography_verbatim": "1 Zhang, Z.; Feng, C. Single-Atom\nCatalysts. Nat. Commun. 2020, 11, 1215–1223, DOI:\n10.1038/s41467-020-\n14917-6.",
    "excluded_layout_lines": [],
    "source_kind": "PRIMARY_INSPECTED_BIBLIOGRAPHY",
}
UNNUMBERED_GROUP = {
    "group_id": "doc_article-ref-u01",
    "parent_doi": "10.1000/parent2",
    "document_id": "doc_article",
    "document_role": "ARTICLE",
    "reference_label": None,
    "reference_ordinal": 1,
    "label_kind": "UNNUMBERED_AUTHOR_YEAR",
    "source_pdf_pages": [6],
    "source_text_line_start": 3,
    "source_text_line_end": 4,
    "bibliography_verbatim": "Kung, H. H. (1989). Transition metal oxides .\nAmsterdam: Elsevier Science.",
    "excluded_layout_lines": [],
    "source_kind": "PRIMARY_INSPECTED_BIBLIOGRAPHY",
}
DOCUMENTS = {
    "doc_si": {"document_id": "doc_si", "role": "SUPPORTING_INFORMATION", "label_kind": "PRINTED_NUMERIC"},
    "doc_article": {"document_id": "doc_article", "role": "ARTICLE", "label_kind": "UNNUMBERED_AUTHOR_YEAR"},
}


def test_numbered_group_with_printed_doi_is_transcribed_from_the_printed_text_only():
    record = bri.derive_occurrence(NUMBERED_GROUP, DOCUMENTS["doc_si"])
    assert record["occurrence_id"] == record["parent_reference_group"] == "doc_si-ref-1"
    assert record["reference_number"] == "1" and record["reference_ordinal"] is None
    assert record["subreference_letter"] is None
    assert record["bibliography_verbatim"].startswith("Zhang, Z.;")
    assert record["display_whitespace_normalized"] == (
        "Zhang, Z.; Feng, C. Single-Atom Catalysts. Nat. Commun. 2020, 11, 1215–1223, "
        "DOI: 10.1038/s41467-020- 14917-6.")
    assert record["explicit_doi_source_fragments"] == ["10.1038/s41467-020-\n14917-6"]
    assert record["explicit_dois_as_transcribed"] == ["10.1038/s41467-020-14917-6"]
    assert record["doi_basis"] == "DOI_PRINTED_IN_THIS_REFERENCE"
    assert record["doi_transcription_rule"] == bri.DOI_TRANSCRIPTION_RULE
    assert record["eligibility_status"] == "NOT_SCREENED"
    assert record["method_coding_status"] == "NOT_CODED"
    assert record["flags"] == []
    assert list(record)[:9] == [
        "occurrence_id", "parent_doi", "document_id", "document_role", "reference_number",
        "reference_ordinal", "label_kind", "subreference_letter", "parent_reference_group"]


def test_unnumbered_group_without_doi_keeps_ordinal_and_null_number():
    record = bri.derive_occurrence(UNNUMBERED_GROUP, DOCUMENTS["doc_article"], ["kept"])
    assert record["reference_number"] is None and record["reference_ordinal"] == 1
    assert record["bibliography_verbatim"] == UNNUMBERED_GROUP["bibliography_verbatim"]
    assert record["explicit_dois_as_transcribed"] == []
    assert record["explicit_doi_source_fragments"] == []
    assert record["doi_transcription_rule"] is None
    assert record["doi_basis"] == "NO_DOI_PRINTED_IN_THIS_REFERENCE"
    assert record["flags"] == ["kept"]


def test_label_and_doi_rules_fail_loudly_outside_their_scope():
    with pytest.raises(ValueError):
        bri.strip_label("(2) Other reference", "1", False)
    assert bri.strip_label("[7] Ref", "7", False) == "Ref"
    assert bri.extract_printed_doi("Appl. Phys. Lett. 2024, 125, DOI: https://doi.org/10.1063/5.\n0232445.") == (
        ["10.1063/5.\n0232445"], ["10.1063/5.0232445"])
    with pytest.raises(ValueError):
        bri.extract_printed_doi("A. 2020, doi:10.1000/abc. B. 2021, doi:10.1000/def.")
    with pytest.raises(ValueError):
        bri.extract_printed_doi("A. 2020, doi:10.1000/abc followed by more text.")


def _partial_text():
    complete = [bri.derive_occurrence(NUMBERED_GROUP, DOCUMENTS["doc_si"]),
                bri.derive_occurrence(UNNUMBERED_GROUP, DOCUMENTS["doc_article"])]
    prefix = {"schema": "x", "status": "s", "counts": {"reference_groups": 2},
              "reference_groups": [NUMBERED_GROUP, UNNUMBERED_GROUP]}
    head = json.dumps(prefix, ensure_ascii=False, separators=(",", ":"))[:-1]
    body = ",".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in complete)
    cut = json.dumps({"occurrence_id": "doc_si-ref-2", "bibliography_verbatim": "truncated mid str"},
                     separators=(",", ":"))[:-8]
    intact = head + "," + bri.OCCURRENCE_MARKER + body
    return intact + "," + cut, complete, intact + "]}"


def test_truncated_prefix_parser_recovers_sections_groups_and_complete_records():
    text, complete, _ = _partial_text()
    parsed = bri.parse_partial(text)
    assert list(parsed["prefix"]) == ["schema", "status", "counts", "reference_groups"]
    assert len(parsed["prefix"]["reference_groups"]) == 2
    assert parsed["occurrences"] == [dict(r) for r in complete]
    assert parsed["truncated"] is True
    assert parsed["truncated_record_id"] == "doc_si-ref-2"
    for record, group in zip(complete, (NUMBERED_GROUP, UNNUMBERED_GROUP)):
        assert bri.compare_records(bri.derive_occurrence(group, DOCUMENTS[group["document_id"]]), record) == []
    changed = dict(complete[0]); changed["display_whitespace_normalized"] = "other"
    assert bri.compare_records(bri.derive_occurrence(NUMBERED_GROUP, DOCUMENTS["doc_si"]), changed)


def test_complete_array_is_recognised_as_not_truncated():
    _, complete, whole = _partial_text()
    parsed = bri.parse_partial(whole)
    assert parsed["truncated"] is False and len(parsed["occurrences"]) == 2
