"""Checks that a valid ruling cannot mask corrupted rebuilt state or checklist."""
import unittest
import json
import pathlib
import tempfile
import hashlib
from unittest.mock import patch

from verify_evidence_recovery import (row_errors, rebuilt_errors, checklist_errors, all_fragments_present,
                                     policy_rebuilt_errors, validate_recovery_evidence)
from verify_si_round import recovery_validation


class VerificationTests(unittest.TestCase):
    TEXT = "Primary source evidence long enough for verbatim verification."

    def ruling(self):
        row = {"screen_id": "TEST", "doi": "10.test/paper", "text_ok": True,
               "disposition": "ELIGIBLE", "exclude_criterion": None, "form": "journal",
               "eta_form": "relative", "eta_derivation": "equivalent", "eta_note": None,
               "secondary": None, "provenance": None, "note": "Model identified."}
        row.update({"E" + str(n): {"v": "YES", "where": "main", "excerpt": self.TEXT} for n in range(1, 7)})
        return {"row": row, "si_complete": True}

    def write_recovery_fixture(self, root):
        (root / "source").mkdir(parents=True)
        (root / "reads").mkdir()
        main = root / "source" / "main.txt"
        si = root / "source" / "si.txt"
        binary = root / "source" / "article.bin"
        main.write_text(self.TEXT, encoding="utf-8")
        si.write_text("Supplementary source text.", encoding="utf-8")
        binary.write_bytes(b"pinned article source")
        entry = self.ruling()
        entry["row"]["screen_id"] = "TEST"
        entry["source"] = "downloaded SI review 2026-10-02: independent reads reviewed"
        entry["independent_reads"] = ["reads/pass1.out.jsonl", "reads/pass2.out.jsonl"]
        entry["source_metadata"] = "source/metadata.json"
        entry["field_decisions"] = {}
        for n in (1, 2):
            (root / "reads" / f"pass{n}.in.jsonl").write_text(json.dumps({
                "screen_id": "TEST", "doi": entry["row"]["doi"], "text": "source/main.txt",
                "si_text": "source/si.txt", "si_complete": True,
            }) + "\n", encoding="utf-8")
            (root / "reads" / f"pass{n}.out.jsonl").write_text(json.dumps(entry["row"]) + "\n", encoding="utf-8")
        pinned = [main, si, binary]
        metadata = {
            "doi": entry["row"]["doi"],
            "files": [{"file": p.relative_to(root).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                      for p in pinned],
            "text": "source/main.txt",
            "text_sha256": hashlib.sha256(main.read_bytes()).hexdigest(),
        }
        (root / "source" / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
        return entry

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

    def test_rebuilt_errors_uses_entry_source_and_historical_fallback(self):
        entry = self.ruling()
        row = {"doi": entry["row"]["doi"], "v5_decision": "ELIGIBLE", "v5_final": "ELIGIBLE",
               "si_read": "recovery reviewed", "v5_question": "False", "v5_step": "",
               "v5_source": "downloaded SI review 2026-10-02: independent reads reviewed"}
        for key in ("form", "eta_form", "eta_derivation", "eta_note", "secondary", "provenance"):
            row["v5_" + key] = entry["row"][key] or ""
        entry["source"] = row["v5_source"]
        self.assertEqual(rebuilt_errors(row, entry, {}, {}), [])
        entry.pop("source")
        row["v5_source"] = "public evidence recovery 2026-10-01: independent reads reviewed"
        self.assertEqual(rebuilt_errors(row, entry, {}, {}), [])

    def test_shared_recovery_validation_rejects_tampered_source_and_assessment(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            entry = self.write_recovery_fixture(root)
            recoveries = {"TEST": entry}
            with patch("verify_evidence_recovery.HERE", root), \
                    patch("verify_evidence_recovery.evidence_path", lambda name: root / name), \
                    patch("verify_evidence_recovery.check", return_value=[]), \
                    patch("verify_evidence_recovery.verified", return_value=True):
                errors, _, reads = validate_recovery_evidence(recoveries)
                self.assertEqual(errors, [])
                self.assertEqual(reads, 2)
                (root / "source" / "article.bin").write_bytes(b"changed source")
                errors, _, _ = validate_recovery_evidence(recoveries)
                self.assertTrue(any("recovered file hash mismatch" in str(e) for e in errors))
                (root / "source" / "article.bin").write_bytes(b"pinned article source")
                output = root / "reads" / "pass2.out.jsonl"
                damaged = entry["row"] | {"E3": {"v": "YES", "where": "main", "excerpt": "fabricated evidence"}}
                output.write_text(json.dumps(damaged) + "\n", encoding="utf-8")
                errors, _, _ = validate_recovery_evidence(recoveries)
                self.assertTrue(any("E3: excerpt not present in source" in str(e) for e in errors))

    def test_si_round_shared_validation_rejects_tampered_current_state(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            entry = self.write_recovery_fixture(root)
            ruling = entry["row"]
            row = {"screen_id": "TEST", "doi": ruling["doi"], "v5_decision": "ELIGIBLE",
                   "v5_final": "ELIGIBLE", "v5_source": entry["source"], "v5_step": "",
                   "si_read": "recovery reviewed", "v5_question": "False"}
            for key in ("form", "eta_form", "eta_derivation", "eta_note", "secondary", "provenance"):
                row["v5_" + key] = ruling[key] or ""
            with patch("verify_evidence_recovery.HERE", root), \
                    patch("verify_evidence_recovery.evidence_path", lambda name: root / name), \
                    patch("verify_evidence_recovery.check", return_value=[]), \
                    patch("verify_evidence_recovery.verified", return_value=True):
                errors, _, reads = recovery_validation([row], {"TEST": entry}, {}, {})
                self.assertEqual(errors, [])
                self.assertEqual(reads, 2)
                row["v5_eta_derivation"] = "scaling"
                errors, _, _ = recovery_validation([row], {"TEST": entry}, {}, {})
                self.assertTrue(any("rebuilt state differs" in str(e) for e in errors))

    def test_explicit_si_metadata_rejects_unpinned_read_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            entry = self.write_recovery_fixture(root)
            metadata_path = root / "source" / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata.update(si_text="source/si.txt", si_text_sha256=hashlib.sha256((root / "source" / "si.txt").read_bytes()).hexdigest())
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            with patch("verify_evidence_recovery.HERE", root), \
                    patch("verify_evidence_recovery.evidence_path", lambda name: root / name), \
                    patch("verify_evidence_recovery.check", return_value=[]), \
                    patch("verify_evidence_recovery.verified", return_value=True):
                self.assertEqual(validate_recovery_evidence({"TEST": entry})[0], [])
                alternate = root / "source" / "unpinned.txt"
                alternate.write_text("Supplementary source text.", encoding="utf-8")
                input_path = root / "reads" / "pass2.in.jsonl"
                inp = json.loads(input_path.read_text(encoding="utf-8"))
                inp["si_text"] = "source/unpinned.txt"
                input_path.write_text(json.dumps(inp) + "\n", encoding="utf-8")
                self.assertTrue(any("read paths differ" in str(e) for e in validate_recovery_evidence({"TEST": entry})[0]))

    def test_checklist_content_and_duplicates_not_only_ids(self):
        previous = [{"screen_id": "TEST", "doi": "10.test/paper"}]
        self.assertEqual(checklist_errors(previous, previous, {}), [])
        self.assertTrue(checklist_errors([dict(previous[0], doi="wrong")], previous, {}))
        self.assertTrue(checklist_errors(previous * 2, previous, {}))
        self.assertEqual(checklist_errors([], previous, {"TEST": self.ruling()}), [])

    def test_policy_overlay_exact_state_and_evidence(self):
        original = self.ruling()["row"]
        original.update(entrant_question="Unresolved scientific choice", eta_form=None, eta_derivation=None)
        original["E6"]["v"] = "NO"
        original.update(disposition="EXCLUDE", exclude_criterion="E6")
        ruling = {"screen_id": "TEST", "date": "2026-10-02", "question_resolved": True,
                  "criteria": {"E3": {"v": "NO", "where": "main", "excerpt": self.TEXT}}}
        current = {"doi": original["doi"], "v5_decision": "EXCLUDE:E3", "v5_final": "EXCLUDE:E3",
                   "v5_source": "SI read: third read; SI adjudication 2026-10-02", "v5_step": "",
                   "si_read": "third read", "v5_question": "False", "v5_form": "journal"}
        current.update({"v5_" + key: "" for key in ("eta_form", "eta_derivation", "eta_note", "secondary", "provenance")})
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for directory in ("si_read", "text", "text_si"):
                (root / directory).mkdir()
            (root / "si_read" / "third_read.jsonl").write_text(json.dumps(original) + "\n", encoding="utf-8")
            (root / "si_texts.csv").write_text("screen_id,si_complete\nTEST,True\n", encoding="utf-8")
            (root / "text" / "TEST.txt").write_text(self.TEXT, encoding="utf-8")
            (root / "text_si" / "TEST.txt").write_text("", encoding="utf-8")
            with patch("verify_evidence_recovery.HERE", root):
                self.assertEqual(policy_rebuilt_errors(current, ruling, {}, {}), [])
                current["v5_question"] = "True"
                self.assertTrue(policy_rebuilt_errors(current, ruling, {}, {}))
                current["v5_question"] = "False"
                ruling["criteria"]["E3"]["excerpt"] = "Unseen fabricated evidence"
                self.assertTrue(policy_rebuilt_errors(current, ruling, {}, {}))


if __name__ == "__main__":
    unittest.main()
