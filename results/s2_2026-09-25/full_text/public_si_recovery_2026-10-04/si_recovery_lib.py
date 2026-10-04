"""Shared helpers for the 2026-10-04 public SI recovery round (retrieval only; no screening decisions).

Rules enforced here (task brief of 2026-10-04):
  * plain HTTP GET only: no browser automation, no proxy/EZproxy/Purdue, no keyed publisher API,
    no shadow library, no CAPTCHA/challenge bypass, no paid API.
  * honest User-Agent; per-host spacing; a publisher host that answers 401/403/429 or serves a challenge
    page is marked GATED in host_gates.json and is not requested again by any script of this phase.
  * every route attempt is appended to search_log.jsonl (outcome in the fixed six-value vocabulary).
  * the OpenAlex key is read from ~/.config/openalex/api_key at request time and never logged or saved.
  * existing files are never touched; everything is written under this phase directory.
"""
import datetime as dt
import hashlib
import json
import pathlib
import re
import time
import urllib.parse

import requests

PHASE = pathlib.Path(__file__).resolve().parent
FT = PHASE.parent
LOG = PHASE / "search_log.jsonl"
GATES = PHASE / "host_gates.json"
FILES = PHASE / "files"
META = PHASE / "metadata"
UA = "sts-plit-si-recovery/1.0 (systematic-review retrieval of open-access supplementary information)"
OUTCOMES = ("recovered", "main-only", "wrong-version", "gated", "not-found", "no-SI-evidence")
API_HOSTS = {"api.crossref.org", "api.openalex.org", "www.ebi.ac.uk", "api.datacite.org", "zenodo.org",
             "api.semanticscholar.org", "export.arxiv.org", "api.figshare.com", "api.unpaywall.org",
             "api.biorxiv.org", "api.core.ac.uk", "eutils.ncbi.nlm.nih.gov"}
CHALLENGE = re.compile(r"just a moment|client challenge|attention required|are you a robot|captcha|"
                       r"perfdrive|access denied|enable javascript and cookies|verify you are human|"
                       r"request unsuccessful|px-captcha|cf-chl", re.I)
STRICT = re.compile(r"recaptcha/challengepage|just a moment|client challenge|px-captcha|cf-chl|perfdrive|"
                    r"pardon our interruption|verify you are human|are you a robot|attention required", re.I)
_last = {}
_session = requests.Session()
_session.headers["User-Agent"] = UA


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def host_of(url):
    return urllib.parse.urlsplit(url).netloc.lower()


FAMILIES = ("wiley.com", "sciencedirect.com", "elsevier.com", "els-cdn.com", "acs.org", "springer.com",
            "nature.com", "iop.org", "aip.org", "sciopen.com")


def gate_key(host):
    for fam in FAMILIES:
        if host == fam or host.endswith("." + fam):
            return fam
    return host


def gates():
    try:
        return json.loads(GATES.read_text(encoding="utf-8"))
    except Exception:
        return {}


def gate_host(host, why):
    g = gates()
    g.setdefault(gate_key(host), {"first_blocked_at": now(), "why": why, "first_host": host})
    GATES.write_text(json.dumps(g, indent=1), encoding="utf-8")


def openalex_key():
    p = pathlib.Path.home() / ".config" / "openalex" / "api_key"
    return p.read_text().strip() if p.exists() else None


def unpaywall_email():
    p = pathlib.Path.home() / ".config" / "unpaywall" / "email"
    return p.read_text().strip() if p.exists() else None


def log(sid, doi, route, url, status, outcome, note, **extra):
    assert outcome in OUTCOMES, outcome
    row = {"screen_id": sid, "doi": doi, "route": route, "url": url, "at_utc": now(),
           "http_status": status, "outcome": outcome, "note": note}
    row.update(extra)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def fetch(url, params=None, headers=None, timeout=40, spacing=None, stream=False, secret_param=None):
    """GET with per-host spacing and gate memory. Returns dict(status, ctype, content, text, error, gated,
    url_logged).  `secret_param` is {name: value} appended to the request but never returned or logged."""
    host = host_of(url)
    url_logged = url + (("?" + urllib.parse.urlencode(params)) if params else "")
    if gate_key(host) in gates() and host not in API_HOSTS:
        return {"status": None, "gated": True, "skipped": True, "error": "host gated earlier in this phase",
                "url_logged": url_logged, "content": b"", "text": "", "ctype": ""}
    gap = spacing if spacing is not None else (1.2 if host in API_HOSTS else 8.0)
    wait = _last.get(host, 0) + gap - time.time()
    if wait > 0:
        time.sleep(wait)
    p = dict(params or {})
    if secret_param:
        p.update(secret_param)
    try:
        r = _session.get(url, params=p, headers=headers, timeout=timeout, stream=stream, allow_redirects=True)
        _last[host] = time.time()
        out = {"status": r.status_code, "ctype": r.headers.get("Content-Type", ""), "url_logged": url_logged,
               "final_url": r.url if not secret_param else url_logged, "error": None, "gated": False, "resp": r}
        if stream:
            return out
        out["content"] = r.content
        out["text"] = r.text if ("text" in out["ctype"] or "json" in out["ctype"] or "xml" in out["ctype"]) else ""
        head = out["text"][:6000]
        if host not in API_HOSTS and (r.status_code in (401, 403, 429) or
                                      (r.status_code == 503) or (CHALLENGE.search(head) and r.status_code != 200)
                                      or (CHALLENGE.search(head) and len(r.content) < 20000)
                                      or (r.status_code == 200 and "html" in out["ctype"] and STRICT.search(head))):
            out["gated"] = True
            gate_host(host, "HTTP %s %s" % (r.status_code, (out["ctype"] or "")[:40]))
        return out
    except Exception as e:  # network error
        _last[host] = time.time()
        return {"status": None, "gated": False, "error": "%s: %s" % (type(e).__name__, str(e)[:200]),
                "url_logged": url_logged, "content": b"", "text": "", "ctype": ""}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sniff(first_bytes):
    if first_bytes.startswith(b"%PDF"):
        return "pdf"
    if first_bytes.startswith(b"PK\x03\x04"):
        return "zip/ooxml"
    if first_bytes.startswith(b"\xd0\xcf\x11\xe0"):
        return "ole(doc)"
    if first_bytes[:15].lower().startswith((b"<!doctype html", b"<html")):
        return "html"
    return "other"


def download(url, dest, max_bytes=300 * 1024 * 1024, headers=None, spacing=None):
    """Stream a file to dest (under FILES). Returns dict with status, bytes, sha256, kind, or error."""
    f = fetch(url, headers=headers, stream=True, spacing=spacing, timeout=90)
    if f.get("error") or f.get("gated") or f["status"] != 200:
        f["bytes"] = 0
        if f.get("resp") is not None:
            try:
                head = f["resp"].content[:3000].decode("utf-8", "ignore")
            except Exception:
                head = ""
            host = host_of(url)
            if host not in API_HOSTS and (f["status"] in (401, 403, 429) or CHALLENGE.search(head)):
                f["gated"] = True
                gate_host(host, "HTTP %s on download" % f["status"])
        return f
    r = f["resp"]
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    h = hashlib.sha256()
    first = b""
    with open(dest, "wb") as fh:
        for chunk in r.iter_content(1 << 16):
            if not first:
                first = chunk[:16]
            total += len(chunk)
            if total > max_bytes:
                break
            h.update(chunk)
            fh.write(chunk)
    f.update({"bytes": total, "sha256": h.hexdigest(), "kind": sniff(first), "path": str(dest)})
    f.pop("resp", None)
    return f


def jget(url, params=None, secret_param=None, spacing=None, headers=None):
    f = fetch(url, params=params, secret_param=secret_param, spacing=spacing, headers=headers)
    f.pop("resp", None)
    j = None
    if f["status"] == 200 and f["text"]:
        try:
            j = json.loads(f["text"])
        except Exception:
            j = None
    f["json"] = j
    return f


def save_meta(name, obj):
    META.mkdir(exist_ok=True)
    (META / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
