"""Regression tests for the additive, explicitly approved policy layer."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from policy_reconciliation import merge_adjudications, policy_adjudications


CASE_CRITERIA = {
    "S25856": "E4", "S26411": "E4", "S02708": "E3", "S05004": "E3",
    "S16323": "E6", "S26256": "E6", "S27700": "E6",
}
CASE_VERDICTS = {
    "S25856": "UNCLEAR", "S26411": "UNCLEAR", "S02708": "NO", "S05004": "YES",
    "S16323": "UNCLEAR", "S26256": "UNCLEAR", "S27700": "UNCLEAR",
}
CASE_IDS = list(CASE_CRITERIA)


def approved_document():
    records = []
    for sid, criterion in CASE_CRITERIA.items():
        row = {
            "screen_id": sid,
            "choice": "approved scoped choice",
            "question_resolved": True,
            "reason": "Recorded evidence supports this case-scoped interpretation.",
            "review": ["independent primary review", "reconciliation review"],
            "date": "2026-10-02",
            "criteria": {criterion: {"v": CASE_VERDICTS[sid], "where": "main: section", "excerpt": "Verbatim source passage."}},
        }
        if sid == "S05004":
            row["fields"] = {"secondary": None, "provenance": None}
        records.append(row)
    return {
        "status": "ADOPTED",
        "date": "2026-10-02",
        "approval": {"answer": "Approve the proposed seven choices", "case_ids": CASE_IDS},
        "records": records,
    }


class PolicyReconciliationTests(unittest.TestCase):
    def write_doc(self, directory, document):
        path = Path(directory) / "approved_policy_adjudications.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def test_missing_file_is_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(policy_adjudications(Path(directory) / "absent.json"), {})

    def test_approved_exact_scope_loads_with_entry_date(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = policy_adjudications(self.write_doc(directory, approved_document()))
        self.assertEqual(set(rows), set(CASE_IDS))
        self.assertEqual(rows["S02708"]["criteria"]["E3"]["v"], "NO")
        self.assertEqual(rows["S05004"]["fields"], {"secondary": None, "provenance": None})
        self.assertEqual(rows["S05004"]["entry_date"], "2026-10-02")

    def test_pending_or_refused_scope_is_rejected(self):
        for mutate in (
            lambda d: d.update(status="PROPOSED"),
            lambda d: d["approval"].update(answer="Not approved"),
            lambda d: d["approval"].update(case_ids=CASE_IDS[:-1]),
            lambda d: d["records"].pop(),
        ):
            document = approved_document()
            mutate(document)
            with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
                policy_adjudications(self.write_doc(directory, document))

    def test_duplicates_and_unsupported_decisions_are_rejected(self):
        duplicate = approved_document()
        duplicate["records"].append(copy.deepcopy(duplicate["records"][0]))
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            policy_adjudications(self.write_doc(directory, duplicate))

        unsupported = approved_document()
        unsupported["records"][0]["criteria"]["E6"] = {"v": "YES", "where": "main", "excerpt": "text"}
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            policy_adjudications(self.write_doc(directory, unsupported))

        eta = approved_document()
        eta["records"][3]["fields"]["eta_form"] = "numeric"
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            policy_adjudications(self.write_doc(directory, eta))

    def test_duplicate_review_references_are_rejected(self):
        document = approved_document()
        document["records"][0]["review"] = ["same review", "same review"]
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            policy_adjudications(self.write_doc(directory, document))

    def test_mutation_capable_record_overrides_are_rejected(self):
        document = approved_document()
        document["records"][0]["text_ok"] = False
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            policy_adjudications(self.write_doc(directory, document))

    def test_merge_refuses_overlap_and_preserves_history(self):
        historical_row = {"screen_id": "OLD", "reason": "original"}
        historical = {"OLD": historical_row}
        historical_before = copy.deepcopy(historical)
        approved = {"NEW": {"screen_id": "NEW", "entry_date": "2026-10-02"}}
        merged = merge_adjudications(historical, approved)
        self.assertEqual(historical, historical_before)
        self.assertEqual(merged["OLD"], historical_row)
        self.assertEqual(merged["NEW"]["entry_date"], "2026-10-02")
        with self.assertRaises(ValueError):
            merge_adjudications(historical, {"OLD": {"screen_id": "OLD"}})


if __name__ == "__main__":
    unittest.main()
