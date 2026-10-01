"""Checks that a valid ruling cannot mask corrupted rebuilt state or checklist."""
import unittest

from verify_evidence_recovery import row_errors, rebuilt_errors, checklist_errors, all_fragments_present


class VerificationTests(unittest.TestCase):
    TEXT = "Primary source evidence long enough for verbatim verification."

    def ruling(self):
        row = {"screen_id": "TEST", "doi": "10.test/paper", "text_ok": True,
               "disposition": "ELIGIBLE", "exclude_criterion": None, "form": "journal",
               "eta_form": "relative", "eta_derivation": "equivalent", "eta_note": None,
               "secondary": None, "provenance": None, "note": "Model identified."}
        row.update({"E" + str(n): {"v": "YES", "where": "main", "excerpt": self.TEXT} for n in range(1, 7)})
        return {"row": row, "si_complete": True}

    def test_valid_schema_and_all_criteria_excerpts(self):
        entry = self.ruling()
        self.assertEqual(row_errors(entry["row"], self.TEXT, True), [])
        entry["row"]["E4"]["excerpt"] = "Different unseen source excerpt entirely."
        self.assertTrue(row_errors(entry["row"], self.TEXT, True))

    def test_every_joined_fragment_and_pdf_ligatures(self):
        self.assertFalse(all_fragments_present("…", self.TEXT))
        self.assertFalse(all_fragments_present(self.TEXT + " … Missing second passage.", self.TEXT))
        self.assertTrue(all_fragments_present("As a first step … electronic structure", "As a ﬁrst step in electronic structure"))

    def test_field_word_limits_and_reanalysis_provenance(self):
        row = self.ruling()["row"]
        row["note"] = "word " * 41
        self.assertTrue(row_errors(row, self.TEXT, True))
        row["note"] = "Model identified."
        row["eta_note"] = "word " * 26
        self.assertTrue(row_errors(row, self.TEXT, True))
        row["eta_note"] = None
        row["secondary"] = "reanalysis"
        self.assertTrue(row_errors(row, self.TEXT, True))

    def test_unresolved_excerpts_enums_and_disposition_checked(self):
        row = self.ruling()["row"]
        row["E6"]["v"] = "UNCLEAR"
        row.update(disposition="UNRESOLVED", eta_form=None, eta_derivation=None)
        self.assertEqual(row_errors(row, self.TEXT, True), [])
        row["E6"]["excerpt"] = "Different unseen source excerpt entirely."
        self.assertTrue(row_errors(row, self.TEXT, True))
        row["E6"]["excerpt"] = self.TEXT
        row["form"] = "invalid"
        self.assertTrue(row_errors(row, self.TEXT, True))
        row["form"] = "journal"
        row["disposition"] = "ELIGIBLE"
        self.assertTrue(row_errors(row, self.TEXT, True))

    def test_reviewed_sid_does_not_allow_wrong_rebuilt_fields(self):
        entry = self.ruling()
        row = {"doi": entry["row"]["doi"], "v5_decision": "ELIGIBLE", "v5_final": "ELIGIBLE",
               "si_read": "recovery reviewed", "v5_question": "False", "v5_step": "",
               "v5_source": "public evidence recovery 2026-10-01: independent reads reviewed"}
        for key in ("form", "eta_form", "eta_derivation", "eta_note", "secondary", "provenance"):
            row["v5_" + key] = entry["row"][key] or ""
        self.assertEqual(rebuilt_errors(row, entry, {}, {}), [])
        row["v5_eta_derivation"] = "scaling"
        self.assertTrue(rebuilt_errors(row, entry, {}, {}))
        row["v5_eta_derivation"] = "equivalent"
        row["v5_final"] = "UNRESOLVED"
        self.assertTrue(rebuilt_errors(row, entry, {}, {}))

    def test_checklist_content_and_duplicates_not_only_ids(self):
        previous = [{"screen_id": "TEST", "doi": "10.test/paper"}]
        self.assertEqual(checklist_errors(previous, previous, {}), [])
        self.assertTrue(checklist_errors([dict(previous[0], doi="wrong")], previous, {}))
        self.assertTrue(checklist_errors(previous * 2, previous, {}))
        self.assertEqual(checklist_errors([], previous, {"TEST": self.ruling()}), [])


if __name__ == "__main__":
    unittest.main()
