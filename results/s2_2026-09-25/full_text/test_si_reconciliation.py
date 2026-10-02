"""Regression checks for explicit SI reconciliation, never scientific verdict inference."""
import copy
import unittest
from unittest.mock import patch

from current_state import adjudicated_row, derive, final, si_adjudications


def sample_row():
    row = {c: {"v": "YES", "where": "test", "excerpt": "test"} for c in ("E1", "E2", "E3", "E4", "E5", "E6")}
    row.update(text_ok=True, eta_form="numeric", eta_derivation="equivalent", eta_note="test", form="journal")
    return row


class ReconciliationTests(unittest.TestCase):
    def test_history_unchanged_and_non_yes_fields_cleared(self):
        row = sample_row()
        before = copy.deepcopy(row)
        result = adjudicated_row(row, {"criteria": {"E6": {"v": "UNCLEAR"}}})
        self.assertEqual(row, before)
        self.assertEqual(result["E6"]["v"], "UNCLEAR")
        self.assertTrue(all(result[k] is None for k in ("eta_form", "eta_derivation", "eta_note")))

    def test_only_explicitly_resolved_question_is_closed(self):
        row = sample_row()
        row["entrant_question"] = "pending question"
        before = copy.deepcopy(row)
        still_open = adjudicated_row(row, {"question_resolved": False})
        self.assertEqual(still_open["entrant_question"], "pending question")
        closed = adjudicated_row(row, {"question_resolved": True})
        self.assertNotIn("entrant_question", closed)
        self.assertEqual(row, before)

    def test_date_does_not_rescue_wrong_text(self):
        row = sample_row()
        row.update(text_ok=False, E2={"v": "UNCLEAR"})
        decision, _ = final("TEST", "UNRESOLVED", row, {"TEST": {"first_publication": "2020-01-01", "flag": ""}})
        self.assertEqual(decision, "UNRESOLVED")

    def test_date_does_not_rescue_unclear_e6_with_si(self):
        row = sample_row()
        row.update(E2={"v": "UNCLEAR"}, E6={"v": "UNCLEAR"})
        decision, _ = final("TEST", "UNRESOLVED", row, {"TEST": {"first_publication": "2020-01-01", "flag": ""}}, si_whole=True)
        self.assertEqual(decision, "UNRESOLVED")

    def test_absent_si_remains_needed(self):
        row = sample_row()
        row["E6"] = {"v": "UNCLEAR"}
        self.assertEqual(derive(row), "NEEDS_SI")

    def test_field_only_correction_keeps_eligibility(self):
        result = adjudicated_row(sample_row(), {"fields": {"eta_form": "relative", "eta_derivation": "direct", "eta_note": None}})
        self.assertEqual(derive(result), "ELIGIBLE")
        self.assertEqual(result["eta_form"], "relative")

    def test_explicit_adjudications_have_evidence_and_review(self):
        for sid, ruling in si_adjudications().items():
            self.assertTrue(ruling["reason"], sid)
            self.assertTrue(ruling["review"], sid)
            for criterion in ruling.get("criteria", {}).values():
                self.assertIn(criterion["v"], ("YES", "NO", "UNCLEAR"), sid)
                self.assertTrue(criterion["where"], sid)
                self.assertTrue(criterion["excerpt"], sid)

    def test_checklist_keeps_main_only_si_triage_correction(self):
        from si_checklist import deciding, tier, verdicts
        row = sample_row()
        st = {"screen_id": "S22122", "v5_source": "SI read: third read; v5 triage A"}
        with patch("si_checklist.jsonl", return_value={"S22122": row}), patch("si_checklist.si_adjudications", return_value={}):
            result = deciding(st, {}, {}, {}, {}, {}, {})
        self.assertEqual(result[0]["E6"]["v"], "UNCLEAR")
        self.assertEqual(tier(verdicts(result), False), 1)
        self.assertEqual(row["E6"]["v"], "YES")

    def test_checklist_applies_explicit_si_ruling(self):
        from si_checklist import deciding
        st = {"screen_id": "TEST", "v5_source": "SI read: third read; SI adjudication 2026-09-29"}
        with patch("si_checklist.jsonl", return_value={"TEST": sample_row()}), patch("si_checklist.si_adjudications", return_value={"TEST": {"criteria": {"E6": {"v": "UNCLEAR"}}}}):
            result = deciding(st, {}, {}, {}, {}, {}, {})
        self.assertEqual(result[0]["E6"]["v"], "UNCLEAR")
        self.assertIsNone(result[0]["eta_form"])


if __name__ == "__main__":
    unittest.main()
