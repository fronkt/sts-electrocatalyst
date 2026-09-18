"""Paths, hashing, deterministic JSON, and a rate-limited on-disk HTTP cache.

Every network response used by F8 is written to disk before it is read, and the
analysis reads only the cached copy, so a re-run over a populated cache is
byte-identical and needs no network (``offline=True`` makes a cache miss an
error instead of a fetch).

No personal address is sent to any API: requests carry a project User-Agent
only (the same choice ``src/lit/verify_dois.py`` documents).
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "results" / "s2_2026-09-16" / "f8"
USER_AGENT = ("sts-electrocatalyst-f8-clearance/0.1 "
              "(+https://github.com/fronkt/sts-electrocatalyst)")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path, root: Path = REPO) -> str:
    """Repo-relative POSIX path (absolute POSIX path if outside the repo)."""
    p = Path(path).resolve()
    try:
        return p.relative_to(root.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def dumps(obj) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dumps(obj))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def read_lines(path: Path) -> list[str]:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


_KEY_BAD = re.compile(r"[^A-Za-z0-9._-]+")
KEY_STEM_MAX = 56   # readable part of a cache file name; the sha1 tag carries uniqueness


def cache_key(text: str, prefix: str = "") -> str:
    """Readable, collision-safe file stem for an identifier or URL.

    The readable part is capped at ``KEY_STEM_MAX`` characters so that the longest
    cache path stays near 125 characters below the repository root and a checkout
    under a long root does not hit the Windows 260-character path limit.
    """
    stem = _KEY_BAD.sub("_", text.lower()).strip("_")
    tag = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"{(prefix + stem)[:KEY_STEM_MAX]}__{tag}"


_TAGGED = re.compile(r"^(?P<left>.*)__(?P<tag>[0-9a-f]{10})$")


def _split_cache_name(name: str) -> tuple[str, str]:
    """(key, suffix) for a cache file name: suffix is '.meta.json' or the body extension."""
    if name.endswith(".meta.json"):
        return name[:-len(".meta.json")], ".meta.json"
    key, dot, ext = name.rpartition(".")
    return (key, "." + ext) if dot else (name, "")


def migrate_cache_names(cache_dir: Path) -> list[tuple[str, str]]:
    """Rename cache files written under the earlier 120-character key rule.

    The sha1 tag is computed from the full identifier under both rules, so the new
    name is the old readable part cut to ``KEY_STEM_MAX`` plus the same tag. Bytes
    are untouched. A name collision is an error, never an overwrite.
    """
    renamed = []
    root = Path(cache_dir)
    if not root.exists():
        return renamed
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        key, suffix = _split_cache_name(p.name)
        m = _TAGGED.match(key)
        if not m or len(m.group("left")) <= KEY_STEM_MAX:
            continue
        target = p.with_name(f"{m.group('left')[:KEY_STEM_MAX]}__{m.group('tag')}{suffix}")
        if target.exists():
            raise RuntimeError(f"cache rename collision: {p.name} -> {target.name}")
        p.rename(target)
        renamed.append((p.name, target.name))
    return renamed


@dataclass
class Response:
    url: str
    status: int
    body: bytes
    content_type: str
    fetched_utc: str
    body_path: Path

    def json(self):
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


RETRY_STATUSES = {0, 406, 408, 425, 429, 500, 502, 503, 504}


class CacheMiss(RuntimeError):
    pass


class Fetcher:
    """GET with a per-instance minimum interval and a write-before-read cache.

    ``secret_headers`` are sent but never written to the cache metadata.
    """

    def __init__(self, cache_dir: Path, min_interval: float = 0.3,
                 offline: bool = False, timeout: float = 60.0):
        self.cache_dir = Path(cache_dir)
        self.min_interval = min_interval
        self.offline = offline
        self.timeout = timeout
        self._last = 0.0
        self.n_network = 0
        self.n_cached = 0
        self.used: set[Path] = set()     # body files read or written by this instance

    def _paths(self, key: str, ext: str):
        return (self.cache_dir / f"{key}.{ext}", self.cache_dir / f"{key}.meta.json")

    def get(self, url: str, key: str, ext: str = "json", accept: str | None = None,
            headers: dict | None = None, secret_headers: dict | None = None,
            retries: int = 3) -> Response:
        body_path, meta_path = self._paths(key, ext)
        meta = None
        if meta_path.exists() and body_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta["status"] in RETRY_STATUSES and not self.offline:
                meta = None                  # transient or negotiation failure: fetch again
        if meta is not None:
            body = body_path.read_bytes()
            if sha256_bytes(body) != meta["sha256"]:
                raise RuntimeError(f"cache body hash mismatch for {body_path}")
            self.n_cached += 1
            self.used.add(body_path)
            return Response(meta["url"], meta["status"], body, meta.get("content_type", ""),
                            meta["fetched_utc"], body_path)
        if self.offline:
            raise CacheMiss(url)
        hdrs = {"User-Agent": USER_AGENT}
        if accept:
            hdrs["Accept"] = accept
        hdrs.update(headers or {})
        all_hdrs = dict(hdrs)
        all_hdrs.update(secret_headers or {})
        status, body, ctype = 0, b"", ""
        for attempt in range(retries + 1):
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            req = urllib.request.Request(url, headers=all_hdrs)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    status, body, ctype = r.status, r.read(), r.headers.get("Content-Type", "")
                break
            except urllib.error.HTTPError as e:
                status, body, ctype = e.code, e.read() or b"", e.headers.get("Content-Type", "")
                if e.code in RETRY_STATUSES and attempt < retries:
                    time.sleep(5.0 * (attempt + 1))
                    continue
                break
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                if attempt < retries:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                raise RuntimeError(f"transport failure for {url}: {e}") from e
        self.n_network += 1
        fetched = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        body_path.parent.mkdir(parents=True, exist_ok=True)
        body_path.write_bytes(body)
        meta = {"url": url, "status": status, "content_type": ctype, "fetched_utc": fetched,
                "sha256": sha256_bytes(body), "bytes": len(body),
                "request_headers": hdrs}
        meta_path.write_text(dumps(meta), encoding="utf-8")
        self.used.add(body_path)
        return Response(url, status, body, ctype, fetched, body_path)


def pdf_text_pages(path: Path) -> list[str]:
    """Page texts of a PDF (PyMuPDF), one string per page."""
    import fitz  # PyMuPDF

    with fitz.open(path) as doc:
        return [page.get_text() for page in doc]
