"""Regression checks for the additive, independently reviewed recovery layer."""
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import recovery_state


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        isolated = tempfile.TemporaryDirectory()
        self.addCleanup(isolated.cleanup)
        for name in ("DOWNLOAD_SI_RULINGS", "PRIORITY_SI_RULINGS"):
            patcher = patch.object(recovery_state, name, pathlib.Path(isolated.name) / (name + ".missing"))
            patcher.start()
            self.addCleanup(patcher.stop)

    def entry(self):
        row = {"screen_id": "TEST", "text_ok": True, "disposition": "ELIGIBLE", "form": "journal",
               "eta_form": "numeric", "eta_derivation": "direct", "eta_note": None,
               "secondary": None, "provenance": None}
        row.update({"E" + str(n): {"v": "YES"} for n in range(1, 7)})
        return {"row": row, "reason": "test",
                "review": "test", "independent_reads": ["pass1", "pass2"], "si_complete": True}

    def load(self, records):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "rulings.json"
            path.write_text(json.dumps({"records": records}), encoding="utf-8")
            with patch.object(recovery_state, "RULINGS", path), patch.object(recovery_state, "FOLLOWUP_RULINGS", pathlib.Path(temp) / "missing2"), patch.object(recovery_state, "CONTINUATION_RULINGS", pathlib.Path(temp) / "missing3"), patch.object(recovery_state, "NEXT_PUBLIC_RULINGS", pathlib.Path(temp) / "missing4"), patch.object(recovery_state, "MIXED_SI_RULINGS", pathlib.Path(temp) / "missing5"), patch.object(recovery_state, "independent_rows", return_value=[dict(records[0]["row"]), dict(records[0]["row"])]):
                return recovery_state.recovery_decisions()

    def test_missing_layer_leaves_existing_state_alone(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(recovery_state, "RULINGS", pathlib.Path(temp) / "missing"), patch.object(recovery_state, "FOLLOWUP_RULINGS", pathlib.Path(temp) / "missing2"), patch.object(recovery_state, "CONTINUATION_RULINGS", pathlib.Path(temp) / "missing3"), patch.object(recovery_state, "NEXT_PUBLIC_RULINGS", pathlib.Path(temp) / "missing4"), patch.object(recovery_state, "MIXED_SI_RULINGS", pathlib.Path(temp) / "missing5"):
                self.assertEqual(recovery_state.recovery_decisions(), {})

    def test_additive_layers_and_cross_layer_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            old = pathlib.Path(temp) / "old.json"
            new = pathlib.Path(temp) / "new.json"
            first, second = self.entry(), self.entry()
            second["row"]["screen_id"] = "OTHER"
            old.write_text(json.dumps({"records": [first]}), encoding="utf-8")
            new.write_text(json.dumps({"records": [second]}), encoding="utf-8")
            with patch.object(recovery_state, "RULINGS", old), patch.object(recovery_state, "FOLLOWUP_RULINGS", new), patch.object(recovery_state, "CONTINUATION_RULINGS", pathlib.Path(temp) / "missing3"), patch.object(recovery_state, "NEXT_PUBLIC_RULINGS", pathlib.Path(temp) / "missing4"), patch.object(recovery_state, "MIXED_SI_RULINGS", pathlib.Path(temp) / "missing5"), patch.object(recovery_state, "independent_rows", side_effect=lambda e: [dict(e["row"]), dict(e["row"])]):
                self.assertEqual(set(recovery_state.recovery_decisions()), {"TEST", "OTHER"})
                new.write_text(json.dumps({"records": [first]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    recovery_state.recovery_decisions()

    def test_continuation_layer_and_duplicate_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            old, follow, cont = [pathlib.Path(temp) / n for n in ("old.json", "follow.json", "cont.json")]
            entries = [self.entry() for _ in range(3)]
            for sid, entry, path in zip(("OLD", "FOLLOW", "CONT"), entries, (old, follow, cont)):
                entry["row"]["screen_id"] = sid
                path.write_text(json.dumps({"records": [entry]}), encoding="utf8")
            with patch.object(recovery_state, "RULINGS", old), patch.object(recovery_state, "FOLLOWUP_RULINGS", follow), patch.object(recovery_state, "CONTINUATION_RULINGS", cont), patch.object(recovery_state, "NEXT_PUBLIC_RULINGS", pathlib.Path(temp) / "missing4"), patch.object(recovery_state, "MIXED_SI_RULINGS", pathlib.Path(temp) / "missing5"), patch.object(recovery_state, "independent_rows", side_effect=lambda e: [dict(e["row"]), dict(e["row"])]):
                self.assertEqual(set(recovery_state.recovery_decisions()), {"OLD", "FOLLOW", "CONT"})
                cont.write_text(json.dumps({"records": [entries[0]]}), encoding="utf8")
                with self.assertRaises(ValueError):
                    recovery_state.recovery_decisions()

    def test_next_public_layer_additivity_and_cross_layer_duplicate_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = [pathlib.Path(temp) / name for name in ("old.json", "follow.json", "cont.json", "next.json")]
            entries = [self.entry() for _ in paths]
            for sid, entry, path in zip(("OLD", "FOLLOW", "CONT", "NEXT"), entries, paths):
                entry["row"]["screen_id"] = sid
                path.write_text(json.dumps({"records": [entry]}), encoding="utf-8")
            with patch.object(recovery_state, "RULINGS", paths[0]), patch.object(recovery_state, "FOLLOWUP_RULINGS", paths[1]), patch.object(recovery_state, "CONTINUATION_RULINGS", paths[2]), patch.object(recovery_state, "NEXT_PUBLIC_RULINGS", paths[3]), patch.object(recovery_state, "MIXED_SI_RULINGS", pathlib.Path(temp) / "missing5"), patch.object(recovery_state, "independent_rows", side_effect=lambda e: [dict(e["row"]), dict(e["row"])]):
                self.assertEqual(set(recovery_state.recovery_decisions()), {"OLD", "FOLLOW", "CONT", "NEXT"})
                paths[3].write_text(json.dumps({"records": [entries[0]]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    recovery_state.recovery_decisions()

    def test_mixed_si_layer_is_additive_and_rejects_cross_layer_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            old = pathlib.Path(temp) / "old.json"
            mixed = pathlib.Path(temp) / "mixed.json"
            first, second = self.entry(), self.entry()
            first["row"]["screen_id"] = "OLD"
            second["row"]["screen_id"] = "MIXED"
            old.write_text(json.dumps({"records": [first]}), encoding="utf-8")
            mixed.write_text(json.dumps({"records": [second]}), encoding="utf-8")
            with patch.object(recovery_state, "RULINGS", old), patch.object(recovery_state, "FOLLOWUP_RULINGS", pathlib.Path(temp) / "missing2"), patch.object(recovery_state, "CONTINUATION_RULINGS", pathlib.Path(temp) / "missing3"), patch.object(recovery_state, "NEXT_PUBLIC_RULINGS", pathlib.Path(temp) / "missing4"), patch.object(recovery_state, "MIXED_SI_RULINGS", mixed), patch.object(recovery_state, "independent_rows", side_effect=lambda e: [dict(e["row"]), dict(e["row"])]):
                self.assertEqual(set(recovery_state.recovery_decisions()), {"OLD", "MIXED"})
                mixed.write_text(json.dumps({"records": [first]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    recovery_state.recovery_decisions()

    def test_download_si_layer_is_additive_and_rejects_cross_layer_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            old = pathlib.Path(temp) / "old.json"
            downloads = pathlib.Path(temp) / "downloads.json"
            first, second = self.entry(), self.entry()
            first["row"]["screen_id"] = "OLD"
            second["row"]["screen_id"] = "DOWNLOAD"
            second["source"] = "downloaded SI review 2026-10-02: independent reads reviewed"
            old.write_text(json.dumps({"records": [first]}), encoding="utf-8")
            downloads.write_text(json.dumps({"records": [second]}), encoding="utf-8")
            with patch.object(recovery_state, "RULINGS", old), \
                    patch.object(recovery_state, "FOLLOWUP_RULINGS", pathlib.Path(temp) / "missing2"), \
                    patch.object(recovery_state, "CONTINUATION_RULINGS", pathlib.Path(temp) / "missing3"), \
                    patch.object(recovery_state, "NEXT_PUBLIC_RULINGS", pathlib.Path(temp) / "missing4"), \
                    patch.object(recovery_state, "MIXED_SI_RULINGS", pathlib.Path(temp) / "missing5"), \
                    patch.object(recovery_state, "DOWNLOAD_SI_RULINGS", downloads), \
                    patch.object(recovery_state, "independent_rows", side_effect=lambda e: [dict(e["row"]), dict(e["row"])]):
                self.assertEqual(set(recovery_state.recovery_decisions()), {"OLD", "DOWNLOAD"})
                downloads.write_text(json.dumps({"records": [first]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    recovery_state.recovery_decisions()

    def test_optional_source_label_must_be_nonempty(self):
        entry = self.entry()
        entry["source"] = "downloaded SI review 2026-10-02"
        self.assertEqual(self.load([entry])["TEST"]["source"], entry["source"])
        entry["source"] = " "
        with self.assertRaises(ValueError):
            self.load([entry])

    def test_priority_si_layer_is_additive_and_rejects_cross_layer_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            old, priority = [pathlib.Path(temp) / name for name in ("old.json", "priority.json")]
            first, second = self.entry(), self.entry()
            first["row"]["screen_id"] = "OLD"
            second["row"]["screen_id"] = "PRIORITY"
            second["source"] = "manual priority SI 2026-10-03: independent reads reviewed"
            old.write_text(json.dumps({"records": [first]}), encoding="utf-8")
            priority.write_text(json.dumps({"records": [second]}), encoding="utf-8")
            with patch.object(recovery_state, "RULINGS", old), \
                    patch.object(recovery_state, "FOLLOWUP_RULINGS", pathlib.Path(temp) / "missing2"), \
                    patch.object(recovery_state, "CONTINUATION_RULINGS", pathlib.Path(temp) / "missing3"), \
                    patch.object(recovery_state, "NEXT_PUBLIC_RULINGS", pathlib.Path(temp) / "missing4"), \
                    patch.object(recovery_state, "MIXED_SI_RULINGS", pathlib.Path(temp) / "missing5"), \
                    patch.object(recovery_state, "PRIORITY_SI_RULINGS", priority), \
                    patch.object(recovery_state, "independent_rows", side_effect=lambda e: [dict(e["row"]), dict(e["row"])]):
                self.assertEqual(set(recovery_state.recovery_decisions()), {"OLD", "PRIORITY"})
                priority.write_text(json.dumps({"records": [first]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    recovery_state.recovery_decisions()

    def test_alias_reads_and_outside_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = pathlib.Path(temp)
            (base / "folder").mkdir()
            row = self.entry()["row"]
            (base / "pass.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
            entry = self.entry()
            entry["independent_reads"] = ["pass.jsonl", "folder/../pass.jsonl"]
            with patch.object(recovery_state, "HERE", base):
                with self.assertRaises(ValueError):
                    recovery_state.independent_rows(entry)
                with self.assertRaises(ValueError):
                    recovery_state.evidence_path("../outside.json")

    def test_two_distinct_reads_required(self):
        entry = self.entry()
        entry["independent_reads"] = ["pass1", "pass1"]
        with self.assertRaises(ValueError):
            self.load([entry])

    def test_duplicate_record_rejected(self):
        with self.assertRaises(ValueError):
            self.load([self.entry(), self.entry()])

    def test_review_and_usable_text_required(self):
        for field, value in (("review", ""), ("reason", "")):
            entry = self.entry()
            entry[field] = value
            with self.assertRaises(ValueError):
                self.load([entry])
        entry = self.entry()
        entry["row"]["text_ok"] = False
        with self.assertRaises(ValueError):
            self.load([entry])

    def test_checklist_uses_new_review_not_historical_wrong_text(self):
        from si_checklist import deciding
        entry = self.entry()
        with patch.object(recovery_state, "recovery_decisions", return_value={"TEST": entry}):
            result = deciding({"screen_id": "TEST", "v5_source": "public evidence recovery 2026-10-01"}, {}, {}, {}, {}, {}, {})
        self.assertEqual(result, [entry["row"]])

    def test_field_disagreement_needs_exact_recorded_choice(self):
        entry = self.entry()
        reads = [dict(entry["row"]), dict(entry["row"], eta_derivation="equivalent")]
        entry["field_adjudication"] = "unrelated nonempty text"
        self.assertTrue(recovery_state.validate_fields(entry, reads))
        entry["field_decisions"] = {"eta_derivation": {"value": "direct", "reason": "source label"}}
        self.assertEqual(recovery_state.validate_fields(entry, reads), [])
        entry["row"]["eta_derivation"] = "scaling"
        self.assertTrue(recovery_state.validate_fields(entry, reads))

    def test_agreed_fields_cannot_be_silently_changed(self):
        entry = self.entry()
        reads = [dict(entry["row"]), dict(entry["row"])]
        entry["row"]["eta_form"] = "relative"
        self.assertTrue(recovery_state.validate_fields(entry, reads))

    def test_custom_disagreement_note_needs_exact_value_and_reason(self):
        entry = self.entry()
        reads = [dict(entry["row"]), dict(entry["row"], eta_note="reader note")]
        entry["row"]["eta_note"] = "reviewed note"
        entry["field_decisions"] = {"eta_note": {"value": "wrong value", "reason": "source"}}
        self.assertTrue(recovery_state.validate_fields(entry, reads))
        entry["field_decisions"]["eta_note"]["value"] = "reviewed note"
        self.assertEqual(recovery_state.validate_fields(entry, reads), [])

    def test_incomplete_row_and_non_yes_eta_are_rejected(self):
        entry = self.entry()
        del entry["row"]["E5"]
        with self.assertRaises(ValueError):
            self.load([entry])
        entry = self.entry()
        entry["row"]["E6"]["v"] = "UNCLEAR"
        with self.assertRaises(ValueError):
            self.load([entry])

    def test_loader_enforces_field_checks_before_state_generation(self):
        with patch.object(recovery_state, "validate_fields", return_value=["field mismatch"]):
            with self.assertRaises(ValueError):
                self.load([self.entry()])
        entry = self.entry()
        reads = [dict(entry["row"]), dict(entry["row"], disposition="UNRESOLVED")]
        self.assertTrue(recovery_state.validate_fields(entry, reads))


if __name__ == "__main__":
    unittest.main()
