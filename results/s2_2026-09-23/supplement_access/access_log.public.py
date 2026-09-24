"""Shared fetch-and-record helper for the Lim/Lee supplement access check.

Every request (success or failure) is appended to receipts.jsonl with URL,
HTTP status, content-type, bytes, sha256 and UTC time; the response body is
saved under bodies/ so failures remain inspectable evidence.
Legal, public routes only. No login, no shadow libraries.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import time
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parent
BODIES = OUT / "bodies"
RECEIPTS = OUT / "receipts.jsonl"
UA = "sts-electrocatalyst-literature-access/1.0 (mailto:<contact-email-redacted>)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA})
_last = {"t": 0.0}
MIN_GAP = 1.5  # seconds between requests (polite)


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:120]


def fetch(label: str, url: str, route: str, target: str, params=None, headers=None,
          ext: str = "body", method: str = "GET", retries: int = 2, note: str = "",
          json_body=None) -> dict:
    """Request url, save body, append receipt. Retries with backoff on 429/5xx/network."""
    BODIES.mkdir(parents=True, exist_ok=True)
    attempt = 0
    rec: dict = {}
    while True:
        gap = time.time() - _last["t"]
        if gap < MIN_GAP:
            time.sleep(MIN_GAP - gap)
        at = dt.datetime.now(dt.timezone.utc).isoformat()
        rec = {"label": label, "target": target, "route": route, "method": method,
               "requested_url": url, "params": params, "requested_utc": at,
               "attempt": attempt + 1, "note": note, "json_body": json_body}
        try:
            r = SESSION.request(method, url, params=params, headers=headers, json=json_body,
                                timeout=60, allow_redirects=True)
            _last["t"] = time.time()
            body = r.content
            rec.update({
                "http_status": r.status_code,
                "response_url": r.url,
                "redirect_chain": [h.url for h in r.history],
                "content_type": r.headers.get("Content-Type"),
                "content_disposition": r.headers.get("Content-Disposition"),
                "retry_after": r.headers.get("Retry-After"),
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
            })
            path = BODIES / f"{_safe(label)}.a{attempt + 1}.{ext}"
            path.write_bytes(body)
            rec["path"] = path.relative_to(OUT).as_posix()
            status = r.status_code
        except requests.RequestException as exc:
            _last["t"] = time.time()
            rec.update({"http_status": None, "error": f"{type(exc).__name__}: {exc}"})
            status = None
        with RECEIPTS.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        transient = status is None or status == 429 or (status is not None and status >= 500)
        if transient and attempt < retries:
            wait = 5 * (2 ** attempt)
            ra = rec.get("retry_after")
            if ra and str(ra).isdigit():
                wait = max(wait, min(int(ra), 120))
            time.sleep(wait)
            attempt += 1
            continue
        return rec


def body_of(rec: dict) -> bytes:
    p = rec.get("path")
    return (OUT / p).read_bytes() if p else b""


def json_of(rec: dict):
    try:
        return json.loads(body_of(rec).decode("utf-8"))
    except Exception:
        return None
