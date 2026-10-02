"""Local safety checks for public retrieval receipts; no network access."""
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import recover_public_next as recovery


class PublicRecoveryTests(unittest.TestCase):
    def record(self):
        return {"sid": "S_TEST", "doi": "10.1234/test",
                "exact_doi_results": [{"pmcid": "PMC123"}]}

    def xml(self, href="supp.pdf"):
        return (f'<article><front><article-meta>'
                f'<article-id pub-id-type="doi">10.1234/test</article-id>'
                f'<article-id pub-id-type="pmcid">PMC123</article-id>'
                f'<supplementary-material xlink:href="{href}" '
                f'xmlns:xlink="http://www.w3.org/1999/xlink" />'
                f'</article-meta></front></article>').encode()

    def test_retain_is_idempotent_and_refuses_different_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "evidence.bin"
            recovery.retain(path, b"first")
            recovery.retain(path, b"first")
            with self.assertRaises(ValueError):
                recovery.retain(path, b"different")
            self.assertEqual(path.read_bytes(), b"first")

    def run_recovery(self, temp, replies):
        with patch.object(recovery, "OUT", pathlib.Path(temp)), patch.object(
                recovery, "fetch", side_effect=replies):
            return recovery.recover(self.record())

    def write_checkpoint(self, temp, receipt):
        dest = pathlib.Path(temp) / "files" / "S_TEST"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "recovery.json").write_text(json.dumps(receipt), encoding="utf-8")
        return dest

    def test_doi_mismatch_is_unresolved(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = self.run_recovery(temp, [self.xml(), json.dumps({"doi": "10.1234/other"}).encode()])
            self.assertEqual(receipt["outcome"], "RECOVERY_UNRESOLVED")
            self.assertIn("Cloud DOI mismatch", receipt["error"])

    def test_attachment_checksum_mismatch_is_unresolved(self):
        metadata = {"doi": "10.1234/test", "media_urls": [
            "https://pmc-oa-opendata.s3.amazonaws.com/PMC123.1/supp.pdf?md5=0000"],
            "pdf_url": "https://pmc-oa-opendata.s3.amazonaws.com/PMC123.1/main.pdf?md5=0000"}
        with tempfile.TemporaryDirectory() as temp:
            receipt = self.run_recovery(temp, [self.xml(), json.dumps(metadata).encode(), b"not the declared bytes"])
            self.assertEqual(receipt["outcome"], "RECOVERY_UNRESOLVED")
            self.assertIn("Cloud checksum mismatch", receipt["error"])

    def test_declared_path_traversal_is_rejected_before_download(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = self.run_recovery(temp, [self.xml("../outside.pdf")])
            self.assertEqual(receipt["outcome"], "RECOVERY_UNRESOLVED")
            self.assertIn("Unsafe local filename/member", receipt["error"])
            self.assertFalse((pathlib.Path(temp) / "files" / "outside.pdf").exists())

    def test_valid_unresolved_checkpoint_is_retained_without_retry(self):
        receipt = {"screen_id": "S_TEST", "doi": "10.1234/test", "pmcid": "PMC123",
                   "outcome": "RECOVERY_UNRESOLVED", "file_hashes": {}}
        with tempfile.TemporaryDirectory() as temp:
            self.write_checkpoint(temp, receipt)
            with patch.object(recovery, "OUT", pathlib.Path(temp)), patch.object(recovery, "fetch") as fetch:
                self.assertEqual(recovery.recover(self.record()), receipt)
                fetch.assert_not_called()

    def test_checkpoint_identity_and_outcome_are_required(self):
        for key, value in (("screen_id", "OTHER"), ("doi", "10.1234/other"),
                           ("pmcid", "PMC999"), ("outcome", "UNKNOWN")):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as temp:
                receipt = {"screen_id": "S_TEST", "doi": "10.1234/test", "pmcid": "PMC123",
                           "outcome": "RECOVERY_UNRESOLVED", "file_hashes": {}}
                receipt[key] = value
                self.write_checkpoint(temp, receipt)
                with patch.object(recovery, "OUT", pathlib.Path(temp)), patch.object(recovery, "fetch"):
                    with self.assertRaises(ValueError):
                        recovery.recover(self.record())

    def test_completed_checkpoint_replays_only_after_all_required_hashes_match(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = pathlib.Path(temp) / "files" / "S_TEST"
            names = ("S_TEST.xml", "cloud_metadata.json", "S_TEST_main.pdf",
                     "S_TEST_main.txt", "S_TEST_si.txt", "supp.pdf")
            hashes = {}
            for name in names:
                data = ("evidence:" + name).encode()
                (dest / name).parent.mkdir(parents=True, exist_ok=True)
                (dest / name).write_bytes(data)
                hashes[name] = recovery.sha(data)
            receipt = {"screen_id": "S_TEST", "doi": "10.1234/test", "pmcid": "PMC123",
                       "outcome": "RECOVERED_DECLARED_INVENTORY", "file_hashes": hashes,
                       "declared_supplements": [{"hrefs": ["supp.pdf"]}],
                       "attachments": [{"filename": "supp.pdf"}]}
            self.write_checkpoint(temp, receipt)
            with patch.object(recovery, "OUT", pathlib.Path(temp)), patch.object(recovery, "fetch") as fetch:
                self.assertEqual(recovery.recover(self.record()), receipt)
                fetch.assert_not_called()

    def test_checkpoint_hash_keys_and_values_are_validated_before_replay(self):
        unsafe_names = ("../outside", "..\\outside", "C:outside", "/outside", "sub/file")
        for name in unsafe_names:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                receipt = {"screen_id": "S_TEST", "doi": "10.1234/test", "pmcid": "PMC123",
                           "outcome": "RECOVERY_UNRESOLVED", "file_hashes": {name: "a" * 64}}
                self.write_checkpoint(temp, receipt)
                with patch.object(recovery, "OUT", pathlib.Path(temp)), patch.object(recovery, "fetch"):
                    with self.assertRaises(ValueError):
                        recovery.recover(self.record())
        with tempfile.TemporaryDirectory() as temp:
            receipt = {"screen_id": "S_TEST", "doi": "10.1234/test", "pmcid": "PMC123",
                       "outcome": "RECOVERY_UNRESOLVED", "file_hashes": {"S_TEST.xml": "not-a-hash"}}
            self.write_checkpoint(temp, receipt)
            with patch.object(recovery, "OUT", pathlib.Path(temp)), patch.object(recovery, "fetch"):
                with self.assertRaises(ValueError):
                    recovery.recover(self.record())

    def test_source_and_declared_names_must_be_simple_members(self):
        for sid in ("../S_TEST", "..\\S_TEST", "C:S_TEST", "/S_TEST"):
            with self.subTest(sid=sid), tempfile.TemporaryDirectory() as temp:
                record = self.record()
                record["sid"] = sid
                with patch.object(recovery, "OUT", pathlib.Path(temp)), patch.object(recovery, "fetch") as fetch:
                    with self.assertRaises(ValueError):
                        recovery.recover(record)
                    fetch.assert_not_called()
        for name in ("..\\outside.pdf", "C:outside.pdf", "/outside.pdf"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                receipt = self.run_recovery(temp, [self.xml(name)])
                self.assertEqual(receipt["outcome"], "RECOVERY_UNRESOLVED")
                self.assertIn("Unsafe local filename/member", receipt["error"])


if __name__ == "__main__":
    unittest.main()
