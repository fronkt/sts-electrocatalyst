"""Load explicitly approved, narrowly scoped SI policy adjudications.

This is an additive reconciliation layer: it validates recorded human decisions
and never infers a scientific verdict from source text.
"""
import json
import pathlib


HERE = pathlib.Path(__file__).resolve().parent
POLICY_ADJUDICATION_FILE = (
    HERE / "mixed_si_review_2026-10-02" / "approved_policy_adjudications.json"
)
EXPECTED_CASES = {
    "S25856", "S26411", "S02708", "S05004", "S16323", "S26256", "S27700",
}
ALLOWED_CRITERIA = {
    "S02708": {"E3"},
    "S05004": {"E3"},
    "S25856": {"E4"},
    "S26411": {"E4"},
    "S16323": {"E6"},
    "S26256": {"E6"},
    "S27700": {"E6"},
}
EXPECTED_VERDICTS = {
    "S02708": {"E3": "NO"},
    "S05004": {"E3": "YES"},
    "S25856": {"E4": "UNCLEAR"},
    "S26411": {"E4": "UNCLEAR"},
    "S16323": {"E6": "UNCLEAR"},
    "S26256": {"E6": "UNCLEAR"},
    "S27700": {"E6": "UNCLEAR"},
}
ALLOWED_FIELDS = {
    "S05004": {"secondary", "provenance"},
}
VERDICTS = {"YES", "NO", "UNCLEAR"}
APPROVAL_ANSWER = "Approve the proposed seven choices"
ALLOWED_RECORD_KEYS = {
    "screen_id", "date", "choice", "criteria", "fields", "reason", "review",
    "question_resolved", "prior_row", "approval_scope", "coordinate_receipt",
}


def _require(condition, message):
    if not condition:
        raise ValueError("Invalid approved policy adjudications: " + message)


def validate_policy_document(document):
    """Validate the approval, exact case scope, evidence, and permitted deltas."""
    _require(isinstance(document, dict), "top level must be an object")
    _require(document.get("status") == "ADOPTED", "status must be ADOPTED")
    _require(document.get("date") == "2026-10-02", "date must be 2026-10-02")
    approval = document.get("approval")
    _require(isinstance(approval, dict), "explicit approval is required")
    _require(approval.get("answer") == APPROVAL_ANSWER, "approval answer does not match")
    case_ids = approval.get("case_ids")
    _require(isinstance(case_ids, list), "approval.case_ids must be a list")
    _require(all(isinstance(sid, str) for sid in case_ids), "approval.case_ids must contain strings")
    _require(len(case_ids) == len(set(case_ids)), "duplicate approved case id")
    _require(set(case_ids) == EXPECTED_CASES, "approval scope must be exactly the seven approved cases")

    records = document.get("records")
    _require(isinstance(records, list), "records must be a list")
    ids = [r.get("screen_id") for r in records if isinstance(r, dict)]
    _require(len(ids) == len(records), "every record must be an object")
    _require(all(isinstance(sid, str) for sid in ids), "record screen_id values must be strings")
    _require(len(ids) == len(set(ids)), "duplicate record screen_id")
    _require(set(ids) == EXPECTED_CASES, "records must cover exactly the seven approved cases")

    for record in records:
        sid = record["screen_id"]
        _require(set(record) <= ALLOWED_RECORD_KEYS, f"{sid}: unsupported record field")
        _require(record.get("date", "2026-10-02") == "2026-10-02", f"{sid}: record date must be 2026-10-02")
        _require(isinstance(record.get("choice"), str) and record["choice"].strip(), f"{sid}: choice required")
        _require(record.get("question_resolved") is True, f"{sid}: question_resolved must be true")
        _require(isinstance(record.get("reason"), str) and record["reason"].strip(), f"{sid}: reason required")
        review = record.get("review")
        _require(isinstance(review, list) and len(review) >= 2, f"{sid}: at least two review references required")
        _require(all(isinstance(ref, str) and ref.strip() for ref in review), f"{sid}: review references must be nonempty strings")
        _require(len(set(review)) >= 2, f"{sid}: review references must be distinct")

        criteria = record.get("criteria", {})
        _require(isinstance(criteria, dict), f"{sid}: criteria must be an object")
        _require(set(criteria) == ALLOWED_CRITERIA[sid], f"{sid}: unsupported or missing criterion")
        for criterion, evidence in criteria.items():
            _require(criterion in {"E1", "E2", "E3", "E4", "E5", "E6"}, f"{sid}: invalid criterion name")
            _require(isinstance(evidence, dict), f"{sid}/{criterion}: evidence must be an object")
            _require(set(evidence) == {"v", "where", "excerpt"}, f"{sid}/{criterion}: unsupported evidence fields")
            _require(evidence.get("v") in VERDICTS, f"{sid}/{criterion}: invalid verdict")
            _require(evidence["v"] == EXPECTED_VERDICTS[sid][criterion], f"{sid}/{criterion}: verdict is outside approved choice")
            _require(isinstance(evidence.get("where"), str) and evidence["where"].strip(), f"{sid}/{criterion}: where required")
            _require(isinstance(evidence.get("excerpt"), str) and evidence["excerpt"].strip(), f"{sid}/{criterion}: excerpt required")

        fields = record.get("fields", {})
        _require(isinstance(fields, dict), f"{sid}: fields must be an object")
        allowed = ALLOWED_FIELDS.get(sid, set())
        _require(set(fields) <= allowed, f"{sid}: unsupported field update")
        _require(all(value is None for value in fields.values()), f"{sid}: field values may only clear permitted fields")

    return document


def policy_adjudications(path=None):
    """Return approved records keyed by ID; absent policy input is a no-op."""
    source = pathlib.Path(path) if path is not None else POLICY_ADJUDICATION_FILE
    if not source.exists():
        return {}
    document = validate_policy_document(json.loads(source.read_text(encoding="utf-8")))
    entry_date = document["date"]
    return {
        record["screen_id"]: dict(record, entry_date=record.get("date", entry_date))
        for record in document["records"]
    }


def merge_adjudications(historical, approved):
    """Merge additive layers, refusing to silently supersede a historical ruling."""
    merged = dict(historical)
    overlap = set(merged) & set(approved)
    _require(not overlap, "policy records overlap historical adjudications: " + ", ".join(sorted(overlap)))
    merged.update(approved)
    return merged
