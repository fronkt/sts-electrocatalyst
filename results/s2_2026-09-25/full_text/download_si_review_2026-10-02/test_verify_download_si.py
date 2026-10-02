"""Mutation tests for downloaded-source identity and reading-path joins."""
import copy
import unittest

from verify_phase import input_link_errors, source_link_errors


class SourceJoinTests(unittest.TestCase):
    def setUp(self):
        self.gate = {"screen_id": "TEST", "doi": "10.test/correct", "main_text": "main.txt",
                     "si_text": "si.txt", "main_sha256": "main-pin", "si_sha256": "si-pin",
                     "source_pins": [{"file": "main.pdf", "sha256": "binary-pin"}]}
        self.meta = {"screen_id": "TEST", "doi": "10.test/correct", "text": "main.txt",
                     "si_text": "si.txt", "text_sha256": "main-pin", "si_text_sha256": "si-pin",
                     "si_complete": True, "identity_verified": True,
                     "files": [{"file": "main.pdf", "sha256": "binary-pin"}]}
        self.ruling = {"row": {"screen_id": "TEST", "doi": "10.test/correct"}, "si_complete": True}
        self.input = {"screen_id": "TEST", "doi": "10.test/correct", "text": "main.txt", "si_text": "si.txt"}

    def test_valid_identity_and_reading_joins(self):
        self.assertEqual(source_link_errors(self.gate, self.ruling, self.meta), [])
        self.assertEqual(input_link_errors(self.gate, self.input), [])

    def test_consistent_wrong_doi_cannot_bypass_verified_gate(self):
        self.ruling["row"]["doi"] = self.meta["doi"] = self.input["doi"] = "10.test/wrong"
        self.assertTrue(source_link_errors(self.gate, self.ruling, self.meta))
        self.assertTrue(input_link_errors(self.gate, self.input))

    def test_metadata_text_path_and_hash_mutations(self):
        for field in ("text", "si_text", "text_sha256", "si_text_sha256", "screen_id"):
            with self.subTest(field=field):
                meta = copy.deepcopy(self.meta)
                meta[field] = "wrong"
                self.assertTrue(source_link_errors(self.gate, self.ruling, meta))

    def test_reading_path_or_identity_mutation(self):
        for field in ("text", "si_text", "doi", "screen_id"):
            with self.subTest(field=field):
                inp = copy.deepcopy(self.input)
                inp[field] = "wrong"
                self.assertTrue(input_link_errors(self.gate, inp))

    def test_completeness_and_binary_pin_mutations(self):
        self.ruling["si_complete"] = False
        self.assertTrue(source_link_errors(self.gate, self.ruling, self.meta))
        self.ruling["si_complete"] = True
        for field in ("si_complete", "identity_verified", "files"):
            with self.subTest(field=field):
                meta = copy.deepcopy(self.meta)
                meta[field] = [] if field == "files" else False
                self.assertTrue(source_link_errors(self.gate, self.ruling, meta))


if __name__ == "__main__":
    unittest.main()
