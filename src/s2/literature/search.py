"""Resumable registered P-LIT searches with raw pages and explicit completeness.

Run from the repository root:
  python src/s2/literature/search.py --out results/s2_2026-09-18/literature --discover
  python src/s2/literature/search.py --out results/s2_2026-09-18/literature

After the dated retrieval amendment is banked, use a separate directory:
  python src/s2/literature/search.py --amended --out results/s2_2026-09-18/literature_openalex --reuse-openalex-cache results/s2_2026-09-18/literature

The first command inventories page-one counts only and is explicitly incomplete.
The second walks every remaining available page, with no top-N cutoff. Failed or
interrupted streams remain incomplete; rerunning resumes from verified cached pages.
No article inclusion decisions or method-reporting codes are inferred here.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone

SOURCE_PATH = Path(__file__).resolve()
LOADED_SOURCE_SHA256 = hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest()
ROOT = Path(__file__).resolve().parents[3]
DECISION = ROOT / "docs/research/s2-operating-decisions-2026-09-18.md"
AMENDMENT = ROOT / "docs/research/s2-literature-retrieval-amendment-2026-09-18.md"
QUERIES = (
    "rutile oxygen evolution", "RuO2 oxygen evolution", "IrO2 oxygen evolution",
    "rutile oxide computational hydrogen electrode",
)
START, END = "2011-01-01", "2026-09-18"
DATABASES = ("openalex", "crossref")
BASES = {"openalex": "https://api.openalex.org/works", "crossref": "https://api.crossref.org/works"}
PAGE_SIZE = {"openalex": 100, "crossref": 1000}
API_DOCUMENTATION = {
    "openalex": "https://help.openalex.org/api/paging/",
    "crossref": "https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".writing")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


@contextmanager
def output_lock(out: Path):
    """One writer per output directory; an interrupted worker leaves an inspectable lock."""
    out.mkdir(parents=True, exist_ok=True)
    path = out / ".search.lock"
    owner = json.dumps(dict(pid=os.getpid(), started_utc=utc(), token=os.urandom(16).hex())).encode()
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise RuntimeError(f"search output is locked: {path}; inspect the owner before removing a stale lock") from error
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(owner)
        yield
    finally:
        if path.exists() and path.read_bytes() == owner:
            path.unlink()


def params_for(database: str, query: str, cursor: str) -> dict:
    if database == "openalex":
        return {"search": query, "filter": f"from_publication_date:{START},to_publication_date:{END}",
                "per_page": PAGE_SIZE[database], "cursor": cursor}
    return {"query.bibliographic": query, "filter": f"from-pub-date:{START},until-pub-date:{END}",
            "rows": PAGE_SIZE[database], "cursor": cursor}


def unpack(database: str, data: dict) -> tuple[list, int, str | None, bool]:
    if database == "openalex":
        rows, total, nxt = data["results"], data["meta"]["count"], data["meta"]["next_cursor"]
        done = not rows or nxt is None
    else:
        msg = data["message"]
        rows, total, nxt = msg["items"], msg["total-results"], msg.get("next-cursor")
        done = len(rows) < PAGE_SIZE[database] or nxt is None
    if not isinstance(rows, list) or not isinstance(total, int) or total < 0:
        raise ValueError("malformed result list or total count")
    if not done and not nxt:
        raise ValueError("full page has no continuation cursor")
    return rows, total, nxt, done


def get_response(database: str, params: dict, timeout: float = 90) -> tuple[bytes, dict]:
    # Credentials never enter receipts, public query URLs or exception messages.
    private = dict(params)
    key = os.environ.get("OPENALEX_API_KEY") if database == "openalex" else None
    if key:
        private["api_key"] = key
    url = BASES[database] + "?" + urllib.parse.urlencode(private)
    request = urllib.request.Request(url, headers={"User-Agent": "sts-electrocatalyst/P-LIT-metadata-2026-09-18",
                                                   "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(), {k: v for k, v in response.headers.items()
                                 if k.lower() in ("date", "content-type", "retry-after", "x-rate-limit-limit", "x-rate-limit-interval")}


def fetch_page(database: str, params: dict, directory: Path, page: int, fetch=get_response, sleep=time.sleep) -> dict:
    raw_path, receipt_path = directory / f"page_{page:06d}.json", directory / f"page_{page:06d}.receipt.json"
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        raw = raw_path.read_bytes()
        if receipt["params"] != params or receipt["database"] != database or receipt["raw_sha256"] != sha(raw):
            raise ValueError("cached page request or byte hash mismatch")
        return {"data": json.loads(raw), "receipt": receipt, "raw_path": raw_path}
    if raw_path.exists():
        raise ValueError("orphan raw page has no receipt; preserve and inspect it before resuming")
    directory.mkdir(parents=True, exist_ok=True)
    errors = []
    for attempt in range(1, 7):
        raw = None
        try:
            raw, headers = fetch(database, params)
            data = json.loads(raw)
            unpack(database, data)
            receipt = dict(database=database, params=params, url=BASES[database] + "?" + urllib.parse.urlencode(params),
                           retrieved_utc=utc(), raw_sha256=sha(raw), bytes=len(raw), response_headers=headers,
                           successful_attempt=attempt, previous_failures=errors)
            # Raw bodies are immutable after their completion receipt is written.
            raw_path.write_bytes(raw)
            write_json(receipt_path, receipt)
            return {"data": data, "receipt": receipt, "raw_path": raw_path}
        except urllib.error.HTTPError as error:
            status = error.code
            body = error.read()
            failure = dict(at=utc(), attempt=attempt, http_status=status, response_body_sha256=sha(body))
            (directory / f"page_{page:06d}.attempt_{attempt}.{time.time_ns()}.error.txt").write_bytes(body)
            retry = status == 429 or 500 <= status < 600
            delay_header = error.headers.get("Retry-After", "") if error.headers else ""
            delay = min(60.0, float(delay_header)) if delay_header.isdigit() else min(60.0, 2 ** attempt)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError, KeyError) as error:
            failure = dict(at=utc(), attempt=attempt, error_type=type(error).__name__)
            if raw is not None:
                failure["response_body_sha256"] = sha(raw)
                (directory / f"page_{page:06d}.attempt_{attempt}.{time.time_ns()}.error.txt").write_bytes(raw)
            retry, delay = True, min(60.0, 2 ** attempt)
        errors.append(failure)
        with (directory / "failures.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(database=database, params=params, page=page, **failure)) + "\n")
        if not retry or attempt == 6:
            raise RuntimeError(f"{database} page {page} request failed; see failures.jsonl")
        sleep(delay)
    raise AssertionError("unreachable")


def text_key(value) -> str:
    plain = html.unescape(re.sub(r"<[^>]*>", " ", str(value or "")))
    return " ".join(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", plain).casefold()))


def doi_key(value) -> str | None:
    value = urllib.parse.unquote(str(value or "")).strip().lower()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value)
    return value if value.startswith("10.") and "/" in value else None


def metadata(database: str, item: dict) -> dict:
    if database == "openalex":
        dates = {"publication_date": item.get("publication_date")}
        author_rows = item.get("authorships") or []
        first = (author_rows[0].get("author") or {}).get("display_name") if author_rows else None
        title = item.get("display_name") or item.get("title") or ""
        doi = doi_key(item.get("doi"))
        ident = item.get("id")
        year = item.get("publication_year")
        kind = item.get("type")
    else:
        dates = {key: item[key].get("date-parts") for key in ("published-online", "published-print", "published", "issued")
                 if isinstance(item.get(key), dict)}
        first_row = (item.get("author") or [{}])[0]
        first = " ".join(str(first_row.get(k) or "") for k in ("given", "family")).strip() or first_row.get("name")
        title = (item.get("title") or [""])[0]
        doi = doi_key(item.get("DOI"))
        ident = item.get("DOI") or item.get("URL")
        starts = [parts[0] for parts in dates.values() if parts and parts[0]]
        year = min((parts[0] for parts in starts), default=None)
        kind = item.get("type")
    return dict(doi=doi, title=title, publication_year=year, first_author=first, publication_dates=dates,
                source_identifier=ident, type=kind,
                date_note="Preserve source precision and online/print dates; first-publication eligibility needs screening.")


def candidate_key(meta: dict, database: str, item: dict) -> tuple[str, str]:
    if meta["doi"]:
        return "doi:" + meta["doi"], "DOI"
    title, author, year = text_key(meta["title"]), text_key(meta["first_author"]), meta["publication_year"]
    if title and author and year is not None:
        return "title-year-author:" + json.dumps([title, year, author], ensure_ascii=False), "normalized title/year/first-author"
    ident = meta["source_identifier"] or sha(json.dumps(item, sort_keys=True).encode())
    return f"unresolved:{database}:{ident}", "insufficient metadata; source identity retained separately"


def connect_index(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.executescript("""
      CREATE TABLE IF NOT EXISTS candidates (key TEXT PRIMARY KEY, candidate_id TEXT UNIQUE, method TEXT, metadata TEXT);
      CREATE TABLE IF NOT EXISTS occurrences (
        source TEXT PRIMARY KEY, key TEXT NOT NULL, database_name TEXT, query_index INTEGER,
        page INTEGER, item_index INTEGER, raw_page TEXT, raw_sha256 TEXT, metadata TEXT);
      CREATE INDEX IF NOT EXISTS occurrences_key ON occurrences(key);
      CREATE TABLE IF NOT EXISTS source_identifiers (
        source TEXT PRIMARY KEY, database_name TEXT, query_index INTEGER, identity TEXT,
        identity_status TEXT NOT NULL DEFAULT 'UNRESOLVED');
      CREATE INDEX IF NOT EXISTS stream_identities ON source_identifiers(database_name, query_index, identity);
    """)
    if "identity_status" not in {row[1] for row in db.execute("PRAGMA table_info(source_identifiers)")}:
        db.execute("ALTER TABLE source_identifiers ADD COLUMN identity_status TEXT NOT NULL DEFAULT 'UNRESOLVED'")
    return db


def index_page(db: sqlite3.Connection, database: str, query_index: int, page: int, rows: list, cached: dict, root: Path):
    raw_rel = cached["raw_path"].relative_to(root).as_posix()
    for i, item in enumerate(rows):
        meta = metadata(database, item)
        key, method = candidate_key(meta, database, item)
        value = json.dumps(meta, sort_keys=True, ensure_ascii=False)
        ident = sha(key.encode())[:24]
        db.execute("INSERT OR IGNORE INTO candidates VALUES (?,?,?,?)", (key, ident, method, value))
        source = f"{database}/q{query_index}/p{page}/i{i}"
        db.execute("INSERT OR IGNORE INTO occurrences VALUES (?,?,?,?,?,?,?,?,?)",
                   (source, key, database, query_index, page, i, raw_rel, cached["receipt"]["raw_sha256"], value))
        provider_id = meta["doi"] if database == "crossref" else meta["source_identifier"]
        if database == "openalex":
            match = re.fullmatch(r"(?:https?://openalex\.org/)?(W\d+)", str(provider_id or ""), re.IGNORECASE)
            provider_id = "https://openalex.org/" + match[1].upper() if match else None
        identity_status = "PROVIDER_ID" if provider_id else "UNRESOLVED"
        identity = provider_id or "unresolved:" + sha(json.dumps(item, sort_keys=True).encode())
        db.execute("INSERT INTO source_identifiers VALUES (?,?,?,?,?) ON CONFLICT(source) DO UPDATE SET "
                   "identity=excluded.identity, identity_status=excluded.identity_status",
                   (source, database, query_index, identity, identity_status))
    db.commit()


def walk(database: str, query_index: int, root: Path, db: sqlite3.Connection, discover=False,
         delay=1.0, fetch=get_response, sleep=time.sleep) -> dict:
    directory = root / "raw" / database / f"q{query_index:02d}"
    status_path = directory / "status.json"
    if discover and status_path.exists():
        previous = json.loads(status_path.read_text(encoding="utf-8"))
        if previous.get("status") == "COMPLETE_API_ENUMERATION":
            discover = False  # Validate all cached pages; never downgrade an already completed stream.
    query = QUERIES[query_index - 1]
    state = dict(database=database, query_index=query_index, literal_query=query, date_window=[START, END],
                 status="INCOMPLETE", pages=0, returned_records=0, reported_totals=[], termination=None)
    cursor, page, seen = "*", 1, set()
    try:
        while True:
            cached = fetch_page(database, params_for(database, query, cursor), directory, page, fetch, sleep)
            rows, total, nxt, done = unpack(database, cached["data"])
            record_hash = sha(json.dumps(rows, sort_keys=True).encode())
            index_page(db, database, query_index, page, rows, cached, root)
            state["pages"] = page
            state["returned_records"] += len(rows)
            if total not in state["reported_totals"]:
                state["reported_totals"].append(total)
            state["last_retrieved_utc"] = cached["receipt"]["retrieved_utc"]
            if rows and record_hash in seen:
                state["termination"] = "REPEATED_PAGE_WITHOUT_PROGRESS"
                break
            seen.add(record_hash)
            if done:
                state.update(status="COMPLETE_API_ENUMERATION", termination="API_EXHAUSTED")
                if state["returned_records"] != total or len(state["reported_totals"]) != 1:
                    state["status"] = "ENUMERATED_WITH_COUNT_DRIFT"
                break
            if discover:
                state["termination"] = "DISCOVERY_FIRST_PAGE_ONLY"
                break
            write_json(status_path, state)
            cursor, page = nxt, page + 1
            if not (directory / f"page_{page:06d}.receipt.json").exists():
                sleep(delay)
    except (RuntimeError, ValueError, KeyError, OSError) as error:
        state.update(termination="REQUEST_OR_CACHE_FAILURE", error_type=type(error).__name__, error=str(error))
    indexed, resolved, unique = db.execute(
        "SELECT count(*), count(CASE WHEN identity_status='PROVIDER_ID' THEN 1 END), "
        "count(DISTINCT CASE WHEN identity_status='PROVIDER_ID' THEN identity END) "
        "FROM source_identifiers WHERE database_name=? AND query_index=?",
        (database, query_index)).fetchone()
    duplicates = [dict(identity=identity, occurrences=n) for identity, n in db.execute(
        "SELECT identity,count(*) AS n FROM source_identifiers WHERE database_name=? AND query_index=? AND identity_status='PROVIDER_ID' "
        "GROUP BY identity HAVING n>1 ORDER BY identity", (database, query_index))]
    state.update(indexed_source_records=indexed, unique_provider_identifiers=unique,
                 unresolved_provider_identity_records=indexed - resolved,
                 duplicate_source_records=resolved - unique, duplicate_provider_identifiers=duplicates)
    if state["status"] == "COMPLETE_API_ENUMERATION" and duplicates:
        state["status"] = "ENUMERATED_WITH_DUPLICATES"
    if state["status"] == "COMPLETE_API_ENUMERATION" and indexed != resolved:
        state["status"] = "ENUMERATED_WITH_UNRESOLVED_IDENTITIES"
    state["updated_utc"] = utc()
    write_json(status_path, state)
    return state


def export_candidates(db: sqlite3.Connection, root: Path) -> dict:
    count = conflicts = 0
    target = root / "candidates.jsonl"
    with target.with_name(target.name + ".writing").open("w", encoding="utf-8") as handle:
        for key, ident, method, representative in db.execute("SELECT * FROM candidates ORDER BY candidate_id"):
            occurrences = []
            variants = {}
            for source, _, database, query_index, page, item_index, raw_page, raw_hash, metadata_json in db.execute(
                    "SELECT * FROM occurrences WHERE key=? ORDER BY source", (key,)):
                m = json.loads(metadata_json)
                for field in ("title", "publication_year", "first_author", "publication_dates", "type"):
                    variants.setdefault(field, set()).add(json.dumps(m[field], ensure_ascii=False, sort_keys=True))
                occurrences.append(dict(database=database, query_index=query_index, page=page, item_index=item_index,
                                        raw_page=raw_page, raw_sha256=raw_hash, metadata=m))
            differing = {k: [json.loads(v) for v in sorted(vals)] for k, vals in variants.items() if len(vals) > 1}
            conflicts += bool(differing)
            row = dict(candidate_id=ident, dedup_key=key, dedup_method=method, metadata=json.loads(representative),
                       conflicting_metadata=differing, source_occurrences=occurrences,
                       inclusion_status="NOT_SCREENED", method_coding_status="NOT_CODED")
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            count += 1
    os.replace(target.with_name(target.name + ".writing"), target)
    return dict(candidates=count, candidates_with_metadata_variants=conflicts,
                source_occurrences=db.execute("SELECT count(*) FROM occurrences").fetchone()[0],
                file=target.name, sha256=file_sha(target))


def reuse_openalex_cache(source: Path, out: Path) -> dict:
    """Copy verified raw pages to an additive amended run; never modify the original inventory."""
    source, out = source.resolve(), out.resolve()
    if source == out:
        raise ValueError("amended cache must use a separate output directory")
    original = json.loads((source / "search_spec.json").read_text(encoding="utf-8"))
    if original["queries"] != list(QUERIES) or original["date_window"] != [START, END]:
        raise ValueError("reuse source has different literal queries or date window")
    copied = []
    for receipt_path in sorted((source / "raw/openalex").glob("q*/page_*.receipt.json")):
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        page = int(receipt_path.name.split(".")[0].split("_")[1])
        query_index = int(receipt_path.parent.name[1:])
        expected = params_for("openalex", QUERIES[query_index - 1], receipt["params"]["cursor"])
        if receipt["database"] != "openalex" or receipt["params"] != expected:
            raise ValueError("reuse page request differs from the registered OpenAlex request")
        raw_path = receipt_path.parent / f"page_{page:06d}.json"
        if file_sha(raw_path) != receipt["raw_sha256"]:
            raise ValueError("reuse page byte hash mismatch")
        for path in (raw_path, receipt_path):
            target = out / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.read_bytes() != path.read_bytes():
                raise ValueError("amended cache already has different bytes")
            if not target.exists():
                shutil.copyfile(path, target)
        copied.append(dict(path=raw_path.relative_to(source).as_posix(), sha256=receipt["raw_sha256"]))
    proof = dict(source=str(source), source_spec_sha256=file_sha(source / "search_spec.json"), copied_pages=copied)
    write_json(out / "cache_reuse.json", proof)
    return proof


def run(out: Path, discover=False, databases=DATABASES, query_indices=(1, 2, 3, 4), delay=1.0,
        amended=False, reuse_from: Path | None = None) -> dict:
    with output_lock(out):
        source_hash = file_sha(SOURCE_PATH)
        if source_hash != LOADED_SOURCE_SHA256:
            raise RuntimeError("pipeline source changed since import; restart with a banked source revision")
        return _run_locked(out, discover, databases, query_indices, delay, amended, reuse_from, source_hash)


def _run_locked(out: Path, discover, databases, query_indices, delay, amended, reuse_from, source_hash) -> dict:
    discovery_databases = ("openalex",) if amended else DATABASES
    if amended and any(d != "openalex" for d in databases):
        raise ValueError("amended discovery uses OpenAlex; Crossref is reserved for DOI validation")
    spec = dict(schema="p-lit-search-spec-v2", queries=list(QUERIES), databases=list(DATABASES),
                pipeline_sha256=source_hash,
                date_window=[START, END], page_sizes=PAGE_SIZE, documentation=API_DOCUMENTATION,
                decision_path=DECISION.relative_to(ROOT).as_posix(), decision_sha256=sha(DECISION.read_bytes()),
                scope="Database metadata search only. Complementary known-source/reference discovery and primary-text inclusion/coding remain pending.")
    if amended:
        spec.update(discovery_databases=list(discovery_databases),
                    amendment_path=AMENDMENT.relative_to(ROOT).as_posix(), amendment_sha256=file_sha(AMENDMENT),
                    superseded_inventory="results/s2_2026-09-18/literature", crossref_role="DOI-specific validation of included candidates")
    spec_path = out / "search_spec.json"
    if spec_path.exists() and json.loads(spec_path.read_text(encoding="utf-8")) != spec:
        raise ValueError("search specification differs from the existing run; choose a separate output directory")
    if not spec_path.exists():
        write_json(spec_path, spec)
    if reuse_from is not None:
        if not amended:
            raise ValueError("cache transfer is supported only for the additive amended run")
        reuse_openalex_cache(reuse_from, out)
    db = connect_index(out / "candidate_index.sqlite")
    try:
        for database in databases:
            for index in query_indices:
                state = walk(database, index, out, db, discover, delay)
                print(json.dumps(state), flush=True)
        statuses = []
        for database in discovery_databases:
            for index in range(1, 5):
                path = out / "raw" / database / f"q{index:02d}" / "status.json"
                statuses.append(json.loads(path.read_text(encoding="utf-8")) if path.exists() else
                                dict(database=database, query_index=index, status="NOT_STARTED"))
        candidate_index = export_candidates(db, out)
        end_hash = file_sha(SOURCE_PATH)
        source_unchanged = end_hash == source_hash
        result = dict(schema="p-lit-metadata-search-v2", updated_utc=utc(), streams=statuses,
                      discovery_databases=list(discovery_databases), amended_protocol=amended,
                      database_search_complete=source_unchanged and all(s["status"] == "COMPLETE_API_ENUMERATION" for s in statuses),
                      candidate_index=candidate_index,
                      pipeline_sha256=source_hash, pipeline_end_sha256=end_hash,
                      pipeline_status="SOURCE_UNCHANGED" if source_unchanged else "SOURCE_CHANGED_DURING_RUN",
                      inclusion_list_frozen=False, methods_coded=0,
                      limitations=["API enumeration is not proof of complete literature coverage or article eligibility.",
                                   ("Original Crossref broad queries remain incomplete; DOI-specific validation is still pending."
                                    if amended else "Literal Crossref bibliographic queries may return broad fuzzy matches; every result remains a candidate."),
                                   "Metadata/date conflicts and missing fields are preserved for primary-source screening.",
                                   "Complementary registered known-source and one-level reference discovery remain pending."])
        write_json(out / "search_readout.json", result)
        if not source_unchanged:
            raise RuntimeError("pipeline source changed during retrieval; evidence preserved with incomplete status")
        return result
    finally:
        db.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--discover", action="store_true", help="first page per stream only; explicitly incomplete")
    parser.add_argument("--database", choices=DATABASES, action="append")
    parser.add_argument("--query", type=int, choices=range(1, 5), action="append")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--amended", action="store_true", help="OpenAlex-only discovery under the dated retrieval amendment")
    parser.add_argument("--reuse-openalex-cache", type=Path, help="original discovery directory; copied and hash-checked additively")
    args = parser.parse_args(argv)
    if args.delay < 0:
        parser.error("delay cannot be negative")
    databases = tuple(args.database or (("openalex",) if args.amended else DATABASES))
    result = run(args.out, args.discover, databases, tuple(args.query or (1, 2, 3, 4)), args.delay,
                 amended=args.amended, reuse_from=args.reuse_openalex_cache)
    return 0 if result["database_search_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
