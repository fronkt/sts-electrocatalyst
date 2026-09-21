"""Complete and structurally verify a one-generation backward-reference index.

Usage:
  python src/s2/literature/backward_reference_index.py --dir results/s2_2026-09-21/backward_reference_extension

The directory holds ``reference_occurrences.json.partial``, a single-line JSON
file cut off inside its ``reference_occurrences`` array. Its earlier sections,
the complete ``reference_groups`` array and every occurrence record before the
cut are intact. This module

  1. recovers the intact prefix, the group records and the complete occurrence
     records (the truncated final record is discarded);
  2. derives exactly one occurrence record per group from the group record, the
     document record and the printed text (label stripped, whitespace-normalized
     display text, DOI transcribed only where a DOI string is literally printed);
  3. compares the derived records field for field with the preserved complete
     records; any disagreement in a derived field fails the run;
  4. recomputes the ``counts`` block and compares it with the recorded block;
  5. cross-checks the independent boundary map and the block file hashes;
  6. writes ``reference_occurrences.json`` and ``structural_verification.json``.

Review ``flags`` are annotations, not derivable from the printed text: they are
carried unchanged from a preserved record where one exists and are empty
otherwise, and the outputs say so. The partial file is never modified.
Standard library only; no network access.
"""
from __future__ import annotations

import argparse
from collections import Counter, OrderedDict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

PARTIAL_NAME = "reference_occurrences.json.partial"
OUTPUT_NAME = "reference_occurrences.json"
BOUNDARY_NAME = "reference_boundaries_independent.json"
VERIFICATION_NAME = "structural_verification.json"
OCCURRENCE_MARKER = '"reference_occurrences":['

DOI_TRANSCRIPTION_RULE = (
    "Only remove DOI-internal extraction whitespace, any printed resolver prefix "
    "and terminal sentence period; no external lookup."
)
DOI_PRINTED = "DOI_PRINTED_IN_THIS_REFERENCE"
DOI_ABSENT = "NO_DOI_PRINTED_IN_THIS_REFERENCE"
TITLE_STATUS = "Printed title retained without external enrichment"
BASE_ELIGIBILITY = "PROVISIONAL_REVIEWED_SUBSET_NOT_GLOBAL_FREEZE"
IDENTITY_STATUS = "UNRESOLVED_NO_EXTERNAL_LOOKUP"
ELIGIBILITY_STATUS = "NOT_SCREENED"
METHOD_STATUS = "NOT_CODED"
UNNUMBERED = "UNNUMBERED_AUTHOR_YEAR"
FINAL_STATUS = "PROVISIONAL_ONE_GENERATION_DISCOVERY_ONLY"
ANNOTATION_FIELDS = ("flags",)

DOI_START = re.compile(r"10\.\s*\d{4,9}\s*/")
DOI_FULL = re.compile(r"10\.\d{4,9}/\S+")
WEB_LOCATOR = re.compile(r"^L\d+@P[\d-]+: ")

LIMITS = [
    "Complete means every reference in the six retained bibliography blocks (four "
    "articles and the two accessible supplements), not complete corpus discovery or "
    "complete supplement coverage: the five Lim supplement files (two DOCX tables, "
    "three TIFF images) and the Lee supplement PDF (HTTP 403) were not retrieved and "
    "their reference contents remain unknown.",
    "The Lee article block is a preserved web transcription of the institutional PDF "
    "text with web line and zero-indexed page locators; no local PDF bytes or full-text "
    "hash exist for it and no visual inspection is claimed.",
    "PDF text extraction can distort accents, ligatures, spacing and hyphenation. Raw "
    "block copies and line/page locators permit independent comparison; no typography, "
    "spelling, year or title repair is applied and conflicting printed years remain as "
    "printed.",
    "Printed DOIs are transcribed only where a DOI string is literally printed in the "
    "reference; removing extraction whitespace, a printed resolver prefix and a terminal "
    "period is the only transformation. No DOI inference, external lookup or identity "
    "deduplication is performed.",
    "Lee reference 44 holds parallel English and German journal statements under one "
    "printed label and remains one occurrence; no lettered subreferences occur in these "
    "six blocks, so every subreference_letter is null.",
    "Every occurrence is NOT_SCREENED for eligibility and NOT_CODED for method. This "
    "index does not freeze the candidate or inclusion population and establishes no "
    "P-LIT proportion or verdict.",
    "One generation means only these four base papers; a cited paper does not become a "
    "new reference-expansion source in this pass.",
    "Review flags are preserved on the occurrence records that were complete in the "
    "partial file. Records completed from group records carry an empty flags list that "
    "records the absence of a flag review, not the absence of anomalies.",
]


# --------------------------------------------------------------------------- utilities
def say(text: str) -> None:
    """Print ASCII-safe text (the console may be cp1252)."""
    print(text.encode("ascii", "backslashreplace").decode("ascii"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ----------------------------------------------------------------- partial-file parser
def parse_partial(text: str) -> dict:
    """Recover the intact prefix and complete occurrence records of a cut-off file.

    Returns ``prefix`` (every top-level section before the occurrences array),
    ``occurrences`` (complete records, in order), ``truncated`` (True when the
    array was cut off) and ``truncated_record_id`` (the id printed in the cut
    record, when visible).
    """
    marker_at = text.rfind(OCCURRENCE_MARKER)
    if marker_at < 0:
        raise ValueError("occurrence array marker not found")
    head = text[:marker_at].rstrip()
    if not head.endswith(","):
        raise ValueError("prefix does not end at a section boundary")
    prefix = json.loads(head[:-1] + "}", object_pairs_hook=_reject_duplicate_keys)
    decoder = json.JSONDecoder()
    position = marker_at + len(OCCURRENCE_MARKER)
    occurrences: list[dict] = []
    truncated = True
    remainder = ""
    while True:
        while position < len(text) and text[position].isspace():
            position += 1
        if position >= len(text):
            break
        if text[position] == "]":
            truncated = False
            break
        try:
            record, end = decoder.raw_decode(text, position)
        except json.JSONDecodeError:
            remainder = text[position:]
            break
        occurrences.append(record)
        position = end
        while position < len(text) and text[position].isspace():
            position += 1
        if position < len(text) and text[position] == ",":
            position += 1
    truncated_id = None
    match = re.search(r'"occurrence_id"\s*:\s*"([^"]*)"', remainder)
    if match:
        truncated_id = match.group(1)
    return {
        "prefix": prefix,
        "occurrences": occurrences,
        "truncated": truncated,
        "truncated_record_id": truncated_id,
    }


def _reject_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate keys in a JSON object: %r" % sorted(
            key for key, count in Counter(keys).items() if count > 1))
    return dict(pairs)


# ---------------------------------------------------------------------- derivation
def strip_label(verbatim: str, label, unnumbered: bool) -> str:
    """Remove the printed label prefix ``(N)``, ``[N]`` or ``N`` and following space."""
    if unnumbered:
        if label is not None:
            raise ValueError("unnumbered reference carries a label %r" % (label,))
        return verbatim
    if label is None:
        raise ValueError("numbered reference without a label")
    for candidate in ("(%s)" % label, "[%s]" % label, "%s" % label):
        if verbatim.startswith(candidate):
            rest = verbatim[len(candidate):]
            if rest == "" or rest[0].isspace():
                return rest.lstrip()
    raise ValueError("label %r not printed at the start of %r" % (label, verbatim[:40]))


def extract_printed_doi(text: str) -> tuple[list[str], list[str]]:
    """Return (source fragments, transcribed DOIs) for a DOI literally printed in text.

    The fragment runs from the printed ``10.`` to the end of the reference, less
    trailing whitespace and one terminal period; the transcription removes the
    fragment's extraction whitespace. A printed resolver prefix precedes ``10.``
    and is therefore never part of the fragment. Anything the rule does not cover
    (a second DOI, text after the DOI, more than one wrap) raises.
    """
    matches = list(DOI_START.finditer(text))
    if not matches:
        return [], []
    if len(matches) > 1:
        raise ValueError("more than one printed DOI start in %r" % text[-80:])
    fragment = text[matches[0].start():].rstrip()
    if fragment.endswith("."):
        fragment = fragment[:-1]
    if " " in fragment or fragment.count("\n") > 1:
        raise ValueError("printed DOI is not the terminal token of %r" % text[-80:])
    doi = "".join(fragment.split())
    if not DOI_FULL.fullmatch(doi):
        raise ValueError("printed DOI fragment %r is not a DOI" % fragment)
    return [fragment], [doi]


def group_family(group: dict) -> str:
    if "source_web_line_start" in group:
        return "web"
    if "reference_ordinal" in group:
        return "extended"
    return "simple"


def derive_occurrence(group: dict, document: dict, preserved_flags=None) -> dict:
    """Derive the single occurrence record of a citation group."""
    family = group_family(group)
    unnumbered = group.get("label_kind") == UNNUMBERED
    label = group["reference_label"]
    reference_number = None if unnumbered else label
    verbatim = strip_label(group["bibliography_verbatim"], label, unnumbered)
    fragments, dois = extract_printed_doi(verbatim)
    if family == "web":
        label_kind = document["label_kind"]
        ordinal = None
    else:
        label_kind = group.get("label_kind")
        ordinal = group.get("reference_ordinal")

    record = OrderedDict()
    record["occurrence_id"] = group["group_id"]
    record["parent_doi"] = group["parent_doi"]
    record["document_id"] = group["document_id"]
    record["document_role"] = group["document_role"]
    record["reference_number"] = reference_number
    if family != "simple":
        record["reference_ordinal"] = ordinal
        record["label_kind"] = label_kind
    record["subreference_letter"] = None
    record["parent_reference_group"] = group["group_id"]
    record["source_pdf_pages"] = list(group["source_pdf_pages"])
    record["source_text_line_start"] = group["source_text_line_start"]
    record["source_text_line_end"] = group["source_text_line_end"]
    if family == "web":
        for field in ("source_web_line_start", "source_web_line_end",
                      "reference_block_line_start", "reference_block_line_end"):
            record[field] = group[field]
    record["bibliography_verbatim"] = verbatim
    record["display_whitespace_normalized"] = normalize_ws(verbatim)
    record["explicit_dois_as_transcribed"] = dois
    if family != "simple":
        record["explicit_doi_source_fragments"] = fragments
        record["doi_transcription_rule"] = DOI_TRANSCRIPTION_RULE if dois else None
    record["doi_basis"] = DOI_PRINTED if dois else DOI_ABSENT
    record["title_resolution_status"] = TITLE_STATUS
    record["source_kind"] = group["source_kind"]
    if family == "web":
        record["source_access_basis"] = group["source_access_basis"]
    record["discovery_generation"] = 1
    record["base_eligibility_status"] = BASE_ELIGIBILITY
    record["identity_validation_status"] = IDENTITY_STATUS
    record["eligibility_status"] = ELIGIBILITY_STATUS
    record["method_coding_status"] = METHOD_STATUS
    record["flags"] = list(preserved_flags) if preserved_flags is not None else []
    return record


def compare_records(derived: dict, preserved: dict) -> list[str]:
    """Field-for-field comparison; returns a list of mismatch descriptions."""
    problems = []
    derived_keys = list(derived.keys())
    preserved_keys = list(preserved.keys())
    if derived_keys != preserved_keys:
        problems.append("field set/order differs: derived=%s preserved=%s"
                        % (derived_keys, preserved_keys))
    for key in preserved_keys:
        if key in ANNOTATION_FIELDS:
            continue
        if key not in derived:
            continue
        if derived[key] != preserved[key]:
            problems.append("%s: derived=%r preserved=%r"
                            % (key, derived[key], preserved[key]))
    return problems


# ------------------------------------------------------------------------ checks
def recompute_counts(prefix: dict, occurrences: list[dict]) -> OrderedDict:
    documents = prefix["documents"]
    components = prefix["incomplete_components"]
    counts = OrderedDict()
    counts["base_papers"] = len(prefix["base_dois"])
    counts["article_documents"] = sum(1 for d in documents if d["role"] == "ARTICLE")
    counts["accessible_si_documents"] = sum(
        1 for d in documents if d["role"] == "SUPPORTING_INFORMATION")
    counts["reference_groups"] = len(prefix["reference_groups"])
    counts["reference_occurrences"] = len(occurrences)
    counts["article_occurrences"] = sum(
        1 for o in occurrences if o["document_role"] == "ARTICLE")
    counts["si_occurrences"] = sum(
        1 for o in occurrences if o["document_role"] == "SUPPORTING_INFORMATION")
    counts["explicit_doi_occurrences"] = sum(
        1 for o in occurrences if o["explicit_dois_as_transcribed"])
    counts["unnumbered_article_occurrences"] = sum(
        1 for o in occurrences
        if o["document_role"] == "ARTICLE" and o.get("label_kind") == UNNUMBERED)
    counts["incomplete_si_parent_bundles"] = len(components)
    counts["known_unretrieved_supplementary_files"] = sum(
        len(c["declared_files"]) if "declared_files" in c else 1 for c in components)
    counts["web_only_article_documents"] = sum(
        1 for d in documents if d["role"] == "ARTICLE" and d["source_pdf"] is None)
    counts["externally_resolved_reference_identities"] = sum(
        1 for o in occurrences if o["identity_validation_status"] != IDENTITY_STATUS)
    counts["method_coded_records"] = sum(
        1 for o in occurrences if o["method_coding_status"] != METHOD_STATUS)
    return counts


def expected_sequence_intact(document: dict, groups: list[dict]) -> bool:
    if document.get("label_kind") == UNNUMBERED or document.get("expected_label_sequence") is None:
        return [g["reference_ordinal"] for g in groups] == document["expected_reference_ordinal_sequence"]
    return [g["reference_label"] for g in groups] == document["expected_label_sequence"]


def strip_layout(raw_span: str, group: dict, document: dict) -> str:
    """Remove layout the boundary map deliberately retains inside a raw span."""
    excluded = {entry["text"] for entry in group.get("excluded_layout_lines", [])}
    excluded.update(entry["text"] for entry in document.get("excluded_layout_lines", []))
    prefixes = [entry["excluded_prefix"]
                for entry in document.get("partial_line_layout_removals", [])]
    kept = []
    for line in raw_span.split("\n"):
        line = WEB_LOCATOR.sub("", line)
        for prefix in prefixes:
            if line.startswith(prefix):
                line = line[len(prefix):]
        if line in excluded or not line.strip():
            continue
        kept.append(line)
    return "\n".join(kept)


def boundary_group_key(group: dict) -> str:
    number = group["reference_ordinal"] if group.get("label_kind") == UNNUMBERED \
        else int(group["reference_label"])
    return "%s:%d" % (group["document_id"], number)


def crosscheck_boundary_map(prefix: dict, boundary: dict, directory: Path) -> dict:
    documents = {d["document_id"]: d for d in prefix["documents"]}
    map_groups = {g["group_id"]: g for g in boundary["groups"]}
    map_docs = {d["document_id"]: d for d in boundary["documents"]}
    index_by_doc: dict[str, list[dict]] = {}
    for group in prefix["reference_groups"]:
        index_by_doc.setdefault(group["document_id"], []).append(group)

    per_document = OrderedDict()
    mismatches = []
    containment_agreements = 0
    line_agreements = 0
    trailing_extensions = []
    for document_id, groups in index_by_doc.items():
        map_doc = map_docs.get(document_id)
        map_count = map_doc["group_count"] if map_doc else None
        map_spans = [g for g in boundary["groups"] if g["document_id"] == document_id]
        block_path = directory / Path(documents[document_id]["reference_block"]).name
        block_text = block_path.read_bytes().decode("utf-8").replace("\r\n", "\n")
        joined = "".join(g["raw_span_with_layout"]
                         for g in sorted(map_spans, key=lambda g: g["reference_number"]))
        entry = OrderedDict()
        entry["index_groups"] = len(groups)
        entry["boundary_map_groups"] = map_count
        entry["group_count_matches"] = map_count == len(groups) == len(map_spans)
        entry["block_sha256_matches_boundary_map"] = (
            map_doc is not None
            and map_doc["reference_block_sha256"] == documents[document_id]["reference_block_sha256"])
        entry["raw_spans_reconstruct_block"] = joined == block_text
        agreements = 0
        lines_agree = 0
        extended = []
        for group in groups:
            key = boundary_group_key(group)
            span = map_groups.get(key)
            if span is None:
                mismatches.append("%s: no boundary-map group %s" % (group["group_id"], key))
                continue
            raw = span["raw_span_with_layout"]
            verbatim = normalize_ws(group["bibliography_verbatim"])
            cleaned = normalize_ws(strip_layout(raw, group, documents[document_id]))
            if verbatim in cleaned:
                agreements += 1
            else:
                mismatches.append("%s: bibliography_verbatim not contained in raw span %s"
                                  % (group["group_id"], key))
            category = source_line_category(span, group, raw, verbatim, documents[document_id])
            if category == "exact":
                lines_agree += 1
            elif category == "trailing_layout_extension":
                extended.append(group["group_id"])
            else:
                mismatches.append("%s: source text lines differ from boundary map %s"
                                  % (group["group_id"], key))
        entry["raw_span_containment_agreements"] = agreements
        entry["source_line_exact_agreements"] = lines_agree
        entry["source_line_trailing_layout_extensions"] = extended
        containment_agreements += agreements
        line_agreements += lines_agree
        trailing_extensions.extend(extended)
        per_document[document_id] = entry
        if not (entry["group_count_matches"] and entry["block_sha256_matches_boundary_map"]
                and entry["raw_spans_reconstruct_block"]):
            mismatches.append("%s: document-level boundary-map disagreement %s"
                              % (document_id, json.dumps(entry)))
    return {
        "per_document": per_document,
        "containment_agreements": containment_agreements,
        "source_line_agreements": line_agreements,
        "trailing_layout_extensions": trailing_extensions,
        "mismatches": mismatches,
    }


def source_line_category(span: dict, group: dict, raw: str, verbatim: str,
                         document: dict) -> str:
    """Classify the boundary map's source lines against the index group's lines.

    ``exact``: identical start and end lines (both null for the web-only block).
    ``trailing_layout_extension``: same start line, the map's end line lies
    beyond the index's, and the index's own line range already contains the
    whole citation, so the extra lines are retained page layout after it.
    Anything else is a mismatch.
    """
    map_start, map_end = span["source_text_start_line"], span["source_text_end_line"]
    idx_start, idx_end = group["source_text_line_start"], group["source_text_line_end"]
    if (map_start, map_end) == (idx_start, idx_end):
        return "exact"
    if None in (map_start, map_end, idx_start, idx_end):
        return "mismatch"
    if map_start != idx_start or map_end <= idx_end:
        return "mismatch"
    own_lines = "\n".join(raw.split("\n")[:idx_end - idx_start + 1])
    if verbatim in normalize_ws(strip_layout(own_lines, group, document)):
        return "trailing_layout_extension"
    return "mismatch"


# -------------------------------------------------------------------------- main
def run(directory: Path) -> int:
    partial_path = directory / PARTIAL_NAME
    boundary_path = directory / BOUNDARY_NAME
    output_path = directory / OUTPUT_NAME
    verification_path = directory / VERIFICATION_NAME
    failures: list[str] = []

    parsed = parse_partial(partial_path.read_bytes().decode("utf-8"))
    prefix = parsed["prefix"]
    preserved = parsed["occurrences"]
    groups = prefix["reference_groups"]
    documents = {d["document_id"]: d for d in prefix["documents"]}
    say("partial file: %d group records, %d complete occurrence records, truncated=%s (%s)"
        % (len(groups), len(preserved), parsed["truncated"], parsed["truncated_record_id"]))

    # 1. derive one occurrence per group, carrying preserved review flags
    preserved_by_id = {o["occurrence_id"]: o for o in preserved}
    if len(preserved_by_id) != len(preserved):
        failures.append("duplicate occurrence ids among preserved records")
    derived = []
    for group in groups:
        kept = preserved_by_id.get(group["group_id"])
        flags = kept["flags"] if kept is not None else None
        derived.append(derive_occurrence(group, documents[group["document_id"]], flags))

    # 2. overlap comparison
    compared = 0
    mismatch_details = []
    carried_flags = 0
    for record in derived:
        kept = preserved_by_id.get(record["occurrence_id"])
        if kept is None:
            continue
        compared += 1
        if kept["flags"]:
            carried_flags += 1
        for problem in compare_records(record, kept):
            mismatch_details.append("%s :: %s" % (record["occurrence_id"], problem))
    for detail in mismatch_details:
        say("MISMATCH " + detail)
    say("overlap: %d records compared, %d field mismatches, %d records with review flags "
        "carried (not derived)" % (compared, len(mismatch_details), carried_flags))
    if mismatch_details:
        failures.append("%d overlap field mismatches" % len(mismatch_details))
    unmatched = set(preserved_by_id) - {g["group_id"] for g in groups}
    if unmatched:
        failures.append("preserved occurrences without a group: %s" % sorted(unmatched))

    # 3. identifiers and sequences
    group_ids = [g["group_id"] for g in groups]
    occurrence_ids = [o["occurrence_id"] for o in derived]
    if len(set(group_ids)) != len(group_ids):
        failures.append("duplicate group ids")
    if len(set(occurrence_ids)) != len(occurrence_ids):
        failures.append("duplicate occurrence ids")
    groups_by_doc: dict[str, list[dict]] = {}
    for group in groups:
        groups_by_doc.setdefault(group["document_id"], []).append(group)
    sequence_ok = {}
    for document_id, doc_groups in groups_by_doc.items():
        document = documents[document_id]
        intact = expected_sequence_intact(document, doc_groups)
        counts_ok = (document["reference_group_count"] == len(doc_groups)
                     and document["occurrence_count"] == len(doc_groups))
        sequence_ok[document_id] = intact and counts_ok
        if not sequence_ok[document_id]:
            failures.append("%s: label sequence or document counts not intact" % document_id)

    # 4. counts
    recomputed = recompute_counts(prefix, derived)
    recorded = prefix["counts"]
    say("counts recorded:   " + json.dumps(recorded))
    say("counts recomputed: " + json.dumps(recomputed))
    counts_agree = dict(recorded) == dict(recomputed) and list(recorded) == list(recomputed)
    if not counts_agree:
        failures.append("counts block disagrees with the recorded block")

    # 5. block hashes and boundary map
    block_hashes = OrderedDict()
    for document_id, document in documents.items():
        actual = sha256_file(directory / Path(document["reference_block"]).name)
        block_hashes[document_id] = actual == document["reference_block_sha256"]
        if not block_hashes[document_id]:
            failures.append("%s: reference block sha256 differs from documents record" % document_id)
    boundary = json.loads(boundary_path.read_bytes().decode("utf-8"))
    boundary_result = crosscheck_boundary_map(prefix, boundary, directory)
    for detail in boundary_result["mismatches"]:
        say("BOUNDARY " + detail)
    say("boundary map: %d/%d raw-span containment agreements, %d exact source-line "
        "agreements, %d spans extended only by trailing page layout, %d mismatches"
        % (boundary_result["containment_agreements"], len(groups),
           boundary_result["source_line_agreements"],
           len(boundary_result["trailing_layout_extensions"]),
           len(boundary_result["mismatches"])))
    if boundary_result["mismatches"] or len(boundary["groups"]) != len(groups):
        failures.append("boundary map cross-check failed")

    if failures:
        for failure in failures:
            say("FAIL " + failure)
        return 1

    # 6. write the completed index
    completed = OrderedDict()
    for key, value in prefix.items():
        if key == "reference_groups":
            continue
        completed[key] = value
        if key == "status":
            completed["status"] = FINAL_STATUS
            completed["completed_utc"] = utc_now()
            completed["completion_note"] = (
                "The reference_occurrences array was completed from the %d preserved "
                "reference_group records after the single-line partial file was cut off "
                "inside the record for %s; %d previously complete occurrence records agree "
                "field for field with the records derived from their groups. Records for "
                "groups without a preserved occurrence follow the field conventions of the "
                "latest preserved records (reference_ordinal, label_kind and DOI provenance "
                "fields); Lee records add the group's web-line and block-line locators and "
                "source_access_basis. Review flags are carried from preserved records only; "
                "the %d completed records carry an empty flags list."
                % (len(groups), parsed["truncated_record_id"], compared,
                   len(groups) - compared))
    completed["reference_groups"] = groups
    completed["reference_occurrences"] = derived
    completed["limits"] = LIMITS
    output_path.write_bytes(
        (json.dumps(completed, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))

    # 7. structural verification
    verification = OrderedDict()
    verification["schema"] = "sts.p_lit.backward_reference_structural_check.v1"
    verification["checked_utc"] = utc_now()
    verification["scope"] = (
        "Read-only checks of artifact structure, block hashes, label sequences, "
        "independent boundary-map agreement and field-for-field agreement between "
        "preserved and derived occurrence records; not a scientific screen, identity "
        "resolution or visual audit.")
    verification["source_json"] = _repo_relative(output_path)
    verification["source_json_sha256"] = sha256_file(output_path)
    verification["partial_source"] = _repo_relative(partial_path)
    verification["partial_source_sha256"] = sha256_file(partial_path)
    verification["partial_complete_occurrence_records"] = len(preserved)
    verification["partial_truncated_record"] = parsed["truncated_record_id"]
    verification["reference_group_count"] = len(groups)
    verification["occurrence_count"] = len(derived)
    verification["unique_group_ids"] = len(set(group_ids))
    verification["unique_occurrence_ids"] = len(set(occurrence_ids))
    doc_entries = []
    for document_id, doc_groups in groups_by_doc.items():
        entry = OrderedDict()
        entry["document_id"] = document_id
        entry["document_role"] = documents[document_id]["role"]
        entry["label_kind"] = documents[document_id].get("label_kind", "PRINTED_NUMERIC")
        entry["reference_groups"] = len(doc_groups)
        entry["occurrences"] = sum(1 for o in derived if o["document_id"] == document_id)
        entry["preserved_occurrences"] = sum(
            1 for o in preserved if o["document_id"] == document_id)
        entry["explicit_doi_occurrences"] = sum(
            1 for o in derived
            if o["document_id"] == document_id and o["explicit_dois_as_transcribed"])
        entry["expected_sequence_intact"] = sequence_ok[document_id]
        entry["block_hash_matches"] = block_hashes[document_id]
        entry["pdf_pages"] = sorted({p for g in doc_groups for p in g["source_pdf_pages"]})
        entry["boundary_map"] = boundary_result["per_document"][document_id]
        doc_entries.append(entry)
    verification["documents"] = doc_entries
    verification["overlap_comparison"] = OrderedDict([
        ("records_compared", compared),
        ("field_mismatches", len(mismatch_details)),
        ("mismatch_details", mismatch_details),
        ("annotation_fields_carried_not_derived", list(ANNOTATION_FIELDS)),
        ("records_with_preserved_review_flags", carried_flags),
        ("completed_records_without_flag_review", len(groups) - compared),
    ])
    verification["counts_agreement"] = OrderedDict([
        ("recorded", recorded), ("recomputed", recomputed), ("agree", counts_agree)])
    verification["boundary_map"] = OrderedDict([
        ("path", _repo_relative(boundary_path)),
        ("sha256", sha256_file(boundary_path)),
        ("groups", len(boundary["groups"])),
        ("per_document_group_counts_agree", all(
            e["group_count_matches"] for e in boundary_result["per_document"].values())),
        ("raw_spans_reconstruct_all_blocks", all(
            e["raw_spans_reconstruct_block"] for e in boundary_result["per_document"].values())),
        ("raw_span_containment_agreements", boundary_result["containment_agreements"]),
        ("source_line_exact_agreements", boundary_result["source_line_agreements"]),
        ("source_line_trailing_layout_extensions", boundary_result["trailing_layout_extensions"]),
        ("trailing_layout_extension_note",
         "For these groups the map's raw span retains page header/footer lines after the "
         "citation, so its end line exceeds the index's; the index's own line range "
         "contains the whole citation text."),
        ("mismatches", boundary_result["mismatches"]),
    ])
    verification["explicit_doi_occurrences"] = recomputed["explicit_doi_occurrences"]
    verification["network_requests"] = 0
    verification["coverage_complete"] = False
    verification["method_status"] = METHOD_STATUS
    verification_path.write_bytes(
        (json.dumps(verification, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    say("wrote %s and %s" % (output_path.name, verification_path.name))
    say("RESULT PASS: %d occurrences, %d overlap records compared, 0 mismatches"
        % (len(derived), compared))
    return 0


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", required=True, type=Path,
                        help="directory holding %s" % PARTIAL_NAME)
    args = parser.parse_args(argv)
    return run(args.dir)


if __name__ == "__main__":
    sys.exit(main())
