"""Explicit reviewed recovery decisions; no scientific verdict inference.

Dated reads are separate from the completed SI round and its prior adjudications.
Only an independently reviewed full row may supersede a current v5 decision.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
RULINGS = HERE / "evidence_recovery_2026-10-01" / "reviewed_decisions.json"
FOLLOWUP_RULINGS = HERE / "public_followup_2026-10-01" / "reviewed_decisions.json"
CONTINUATION_RULINGS = HERE / "openai_public_si_continuation_2026-10-01" / "reviewed_decisions.json"
NEXT_PUBLIC_RULINGS = HERE / "public_screening_next_2026-10-01" / "reviewed_decisions.json"
MIXED_SI_RULINGS = HERE / "mixed_si_review_2026-10-02" / "reviewed_decisions.json"
READ_FIELDS = ("form", "eta_form", "eta_derivation", "eta_note", "secondary", "provenance")


def evidence_path(name):
    path = (HERE / name).resolve()
    if not path.is_relative_to(HERE.resolve()):
        raise ValueError("Recovery path outside evidence root")
    return path


def validate_fields(entry, reads):
    """Require exact, field-specific choices when independent evidence differs."""
    errors = []
    chosen_row = entry["row"]
    for row in reads:
        if any((row.get("E" + str(n)) or {}).get("v") != chosen_row["E" + str(n)]["v"] for n in range(1, 7)) or any(
                row.get(k) != chosen_row.get(k) for k in ("disposition", "exclude_criterion")):
            errors.append("criterion/disposition disagreement requires a further reviewed read")
    decisions = entry.get("field_decisions", {})
    for field in READ_FIELDS:
        observed = {row.get(field) for row in reads}
        chosen = entry["row"].get(field)
        if len(observed) == 1:
            if chosen not in observed:
                errors.append(field + ": ruling differs from agreed reads")
        else:
            decision = decisions.get(field, {})
            if not decision.get("reason") or "value" not in decision or decision["value"] != chosen:
                errors.append(field + ": explicit value/reason required")
            # A revised explanatory note is permitted, but not a new enum value
            # that neither independent reader supported.
            if field != "eta_note" and chosen not in observed:
                errors.append(field + ": ruling value absent from independent reads")
    return errors


def independent_rows(entry):
    sid = entry["row"]["screen_id"]
    rows = []
    seen = set()
    for name in entry["independent_reads"]:
        path = evidence_path(name)
        if path in seen:
            raise ValueError("Recovery read aliases are not independent: " + sid)
        seen.add(path)
        found = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(found) != 1 or found[0].get("screen_id") != sid or found[0].get("doi") != entry["row"].get("doi"):
            raise ValueError("Recovery independent-read identity mismatch: " + sid)
        rows.extend(found)
    return rows


def recovery_decisions():
    entries = []
    for path in (RULINGS, FOLLOWUP_RULINGS, CONTINUATION_RULINGS, NEXT_PUBLIC_RULINGS, MIXED_SI_RULINGS):
        if path.exists():
            entries.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
    result = {}
    for entry in entries:
        sid = entry["row"]["screen_id"]
        if sid in result:
            raise ValueError("Duplicate recovery decision: " + sid)
        reads = entry.get("independent_reads", [])
        if not entry.get("reason") or not entry.get("review") or len(set(reads)) < 2:
            raise ValueError("Unreviewed recovery decision: " + sid)
        if entry["row"].get("text_ok") is not True:
            raise ValueError("Recovery must have usable reviewed text: " + sid)
        row = entry["row"]
        if any((row.get("E" + str(n)) or {}).get("v") not in ("YES", "NO", "UNCLEAR", "NOT_ASSESSED") for n in range(1, 7)):
            raise ValueError("Incomplete recovery criteria: " + sid)
        if any(field not in row for field in READ_FIELDS) or row.get("disposition") not in ("ELIGIBLE", "EXCLUDE", "NEEDS_SI", "UNRESOLVED"):
            raise ValueError("Incomplete recovery row: " + sid)
        if row["E6"]["v"] != "YES" and any(row[field] is not None for field in ("eta_form", "eta_derivation", "eta_note")):
            raise ValueError("Non-YES E6 carries eta fields: " + sid)
        errors = validate_fields(entry, independent_rows(entry))
        if errors:
            raise ValueError("Invalid recovery fields for " + sid + ": " + "; ".join(errors))
        result[sid] = entry
    return result
