"""Public Caltech article recovery; preserve all prior reading copies and outputs.

The download URL and MD5 are linked by the repository record, not guessed.
PDFs and extracted full texts stay local. Nothing here assigns a verdict.
"""
import csv
import datetime as dt
import hashlib
import json
import pathlib
import urllib.parse

import fitz
import requests

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "evidence_recovery_2026-10-01"
URL = "https://authors.library.caltech.edu/records/yetrt-39j08/files/acs_2Ejpcc_2E5b00861.pdf?download=1"
PAGE = "https://authors.library.caltech.edu/records/yetrt-39j08"
MD5 = "3815583f6b460568836d6457cb34a32d"


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def capture_baseline():
    p = D / "baseline.json"
    if p.exists():
        return
    paths = list((HERE / "si_read").rglob("*.out.jsonl"))
    paths += [HERE / "si_read" / name for name in
              ("pass_1.jsonl", "pass_2.jsonl", "third_read.jsonl", "queue.csv")]
    paths += [HERE / "eligibility_instructions.md", HERE / "reconcile" / "si_adjudications_2026-09-29.json"]
    records = list(csv.DictReader((HERE / "reconcile" / "current_state.csv").open(encoding="utf-8")))
    checklist = list(csv.DictReader((HERE / "si_checklist.csv").open(encoding="utf-8")))
    p.write_text(json.dumps({"captured_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                            "files": {q.relative_to(HERE).as_posix(): digest(q) for q in sorted(paths)},
                            "records": records, "checklist": checklist}, indent=1) + "\n", encoding="utf-8")


def fetch():
    # Public redirects are restricted to the repository and its documented storage.
    url = URL
    for _ in range(5):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in (
                "authors.library.caltech.edu", "s3.us-west-2.amazonaws.com"):
            raise ValueError("Unexpected non-public repository redirect")
        r = requests.get(url, timeout=45, allow_redirects=False,
                         headers={"User-Agent": "sts-plit-public-recovery/1.0"})
        if r.status_code in (301, 302, 303, 307, 308):
            url = urllib.parse.urljoin(url, r.headers["Location"])
            continue
        r.raise_for_status()
        return r.content
    raise ValueError("Too many public repository redirects")


def main():
    D.mkdir(exist_ok=True)
    capture_baseline()
    dest = D / "files" / "S01741"
    dest.mkdir(parents=True, exist_ok=True)
    p = dest / "main_caltech.pdf"
    body = p.read_bytes() if p.exists() else fetch()
    if not body.startswith(b"%PDF-") or hashlib.md5(body).hexdigest() != MD5:
        raise ValueError("Caltech PDF signature or repository MD5 mismatch")
    doc = fitz.open(stream=body, filetype="pdf")
    first = doc[0].get_text()
    if "Electronic Structure of IrO" not in first or "10.1021/acs.jpcc.5b00861" not in "\n".join(q.get_text() for q in doc):
        raise ValueError("Article title/DOI mismatch")
    if not p.exists():
        p.write_bytes(body)
    text = "\n".join("[main Caltech PDF p. %d]\n%s" % (i + 1, q.get_text()) for i, q in enumerate(doc))
    t = dest / "main.txt"
    if t.exists() and t.read_text(encoding="utf-8") != text:
        raise ValueError("Do not overwrite differing recovered text")
    if not t.exists():
        t.write_text(text, encoding="utf-8")
    meta = {"screen_id": "S01741", "doi": "10.1021/acs.jpcc.5b00861", "status": "IDENTITY_VERIFIED",
            "record_url": PAGE, "download_url": URL, "repository_md5": MD5,
            "file": p.relative_to(HERE).as_posix(), "sha256": digest(p), "bytes": len(body),
            "pages": doc.page_count, "text": t.relative_to(HERE).as_posix(), "text_sha256": digest(t),
            "identity": "Title, authors, journal and printed DOI match the Caltech DOI record.",
            "prior_wrong_file": "files/S01741.pdf", "prior_wrong_file_sha256": digest(HERE / "files" / "S01741.pdf"),
            "prior_wrong_text_sha256": digest(HERE / "text" / "S01741.txt"),
            "existing_correct_si": "files_si/S01741_SI1.pdf",
            "existing_correct_si_sha256": digest(HERE / "files_si" / "S01741_SI1.pdf")}
    (D / "s01741_recovery.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
