"""Polite HTTP GET helper with raw-byte retention and receipts.

Every response body is saved under raw/ (or files/ for documents) named by
its sha256 prefix; a receipt row (URL, status, UTC time, content type,
bytes, sha256, local path) is appended to receipts.jsonl.
Rate limit: at most ~4 requests/s globally, exponential backoff on 429/5xx.
"""
import hashlib
import json
import pathlib
import time
import datetime
import urllib.parse

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
FILES = ROOT / "files"
RECEIPTS = ROOT / "receipts.jsonl"
MAILTO = "<contact-email-redacted>"
UA = f"sts-electrocatalyst-literature-review/1.0 (mailto:{MAILTO})"
_last = [0.0]


def _sleep_rate():
    dt = time.time() - _last[0]
    if dt < 0.25:
        time.sleep(0.25 - dt)
    _last[0] = time.time()


def get(url, label, kind="raw", ext=None, accept=None, max_tries=4, timeout=60):
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    tries = 0
    while True:
        tries += 1
        _sleep_rate()
        t = datetime.datetime.now(datetime.timezone.utc).isoformat()
        rec = {"label": label, "request_url": url, "requested_utc": t, "attempt": tries}
        try:
            r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        except Exception as e:  # network error
            rec.update({"status": None, "error": repr(e)})
            _append(rec)
            if tries < max_tries:
                time.sleep(2 ** tries)
                continue
            return rec, None
        body = r.content
        sha = hashlib.sha256(body).hexdigest()
        ctype = r.headers.get("Content-Type", "")
        if ext is None:
            if "pdf" in ctype:
                e = ".pdf"
            elif "json" in ctype:
                e = ".json"
            elif "html" in ctype:
                e = ".html"
            elif "xml" in ctype:
                e = ".xml"
            else:
                e = ".bin"
        else:
            e = ext
        d = FILES if kind == "file" else RAW
        d.mkdir(parents=True, exist_ok=True)
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in label)[:60]
        p = d / f"{safe}__{sha[:16]}{e}"
        p.write_bytes(body)
        rec.update({
            "status": r.status_code,
            "response_url": r.url,
            "content_type": ctype,
            "bytes": len(body),
            "sha256": sha,
            "local_path": str(p.relative_to(ROOT.parents[2])).replace("\\", "/"),
            "is_pdf_magic": body[:5] == b"%PDF-",
        })
        _append(rec)
        if r.status_code in (429, 500, 502, 503, 504) and tries < max_tries:
            time.sleep(2 ** (tries + 1))
            continue
        return rec, body


def _append(rec):
    with open(RECEIPTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def q(s):
    return urllib.parse.quote(s, safe="")
