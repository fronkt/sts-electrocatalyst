"""Prospective P-LIT date partitions and offline receipt validation; no transport.

Prepare a new manifest (does not retrieve pages):
  python src/s2/literature/reconcile_plan.py --source OLD_CACHE --out NEW_PLAN

Future retrieval must use a separate banked runner. This module never imports or
changes the active search engine, its caches, or its completeness flags.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re

QUERIES = (
    "rutile oxygen evolution", "RuO2 oxygen evolution", "IrO2 oxygen evolution",
    "rutile oxide computational hydrogen electrode",
)
START, END = "2011-01-01", "2026-09-18"
# 2026-09-22: the secondary key is numeric. OpenAlex rejected its own continuation cursor
# ("Pagination error. Invalid cursor value") whenever a display_name sort key carried an
# apostrophe; cursors built from date, citation count and the provider id paginate.
SORT = "publication_date:asc,cited_by_count:asc"
PAGE_SIZE = 100
BASE = "https://api.openalex.org/works"
DOCUMENTATION = {
    "sort": "https://help.openalex.org/api/sorting/",
    "paging": "https://help.openalex.org/api/paging/",
    "filters": "https://help.openalex.org/api/filtering/",
}
LIMITATION = (
    "Observed cursor/count/identity consistency is not an immutable API snapshot "
    "or proof of global P-LIT completion. Equal date/citation-count sort keys can tie; "
    "records and query membership can change without a count change."
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    with path.open("rb") as handle:
        digest = hashlib.sha256()
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
        return digest.hexdigest()


def iso_day(value: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("date must be YYYY-MM-DD")
    return date.fromisoformat(value)


def provider_id(value) -> str | None:
    match = re.fullmatch(r"(?:https?://openalex\.org/)?(W[1-9]\d*)",
                         str(value or ""), re.IGNORECASE)
    return "https://openalex.org/" + match[1].upper() if match else None


def partition(query_index: int, start: str, end: str, level: str) -> dict:
    if type(query_index) is not int or not 1 <= query_index <= len(QUERIES):
        raise ValueError("unregistered query index")
    first, last = iso_day(start), iso_day(end)
    if not iso_day(START) <= first <= last <= iso_day(END):
        raise ValueError("partition outside registered window")
    if level == "year":
        expected = (date(first.year, 1, 1), min(date(first.year, 12, 31), iso_day(END)))
    elif level == "month":
        after = (first.replace(year=first.year + 1, month=1, day=1) if first.month == 12
                 else first.replace(month=first.month + 1, day=1))
        expected = (first.replace(day=1), min(after - timedelta(days=1), iso_day(END)))
    elif level == "day":
        expected = (first, first)
    else:
        raise ValueError("unknown partition level")
    if (first, last) != expected:
        raise ValueError("partition must be a complete calendar unit clipped to the window")
    return dict(partition_id=f"q{query_index:02d}_{level}_{start}_{end}",
                query_index=query_index, literal_query=QUERIES[query_index - 1],
                start=start, end=end, level=level)


def checked(part: dict) -> dict:
    expected = partition(part["query_index"], part["start"], part["end"], part["level"])
    if part != expected:
        raise ValueError("partition manifest differs from its registered definition")
    return expected


def initial_partitions() -> list[dict]:
    return [partition(q, f"{year}-01-01", min(f"{year}-12-31", END), "year")
            for q in range(1, 5) for year in range(2011, 2027)]


def split_partition(part: dict) -> list[dict]:
    checked(part)
    if part["level"] == "day":
        return []
    first, last = iso_day(part["start"]), iso_day(part["end"])
    result = []
    while first <= last:
        if part["level"] == "year":
            after = (date(first.year + 1, 1, 1) if first.month == 12
                     else date(first.year, first.month + 1, 1))
            end, level = min(after - timedelta(days=1), last), "month"
        else:
            end, level = first, "day"
        result.append(partition(part["query_index"], first.isoformat(), end.isoformat(), level))
        first = end + timedelta(days=1)
    return result


def request_params(part: dict, cursor: str = "*") -> dict:
    checked(part)
    if not isinstance(cursor, str) or not cursor:
        raise ValueError("cursor must be a nonempty provider token")
    return dict(search=part["literal_query"],
                filter=f"from_publication_date:{part['start']},to_publication_date:{part['end']}",
                sort=SORT, per_page=PAGE_SIZE, cursor=cursor)


def validate_cover(leaves: list[dict]) -> None:
    """Require exactly the complete, disjoint window for every literal query."""
    for part in leaves:
        checked(part)
    for query_index in range(1, 5):
        expected = iso_day(START)
        for part in sorted((p for p in leaves if p["query_index"] == query_index),
                           key=lambda p: p["start"]):
            if iso_day(part["start"]) != expected:
                raise ValueError("partition coverage has a gap, overlap or duplicate")
            expected = iso_day(part["end"]) + timedelta(days=1)
        if expected != iso_day(END) + timedelta(days=1):
            raise ValueError("partition coverage does not reach the registered end")


def validate_cached_partition(part: dict, directory: Path) -> dict:
    """Validate one attempt's immutable successful pages; never fetch or alter it.

    Receipt schema matches search.fetch_page: database, params, retrieved_utc,
    raw_sha256, bytes. Raw and receipt files must be sequential from page_000001.
    Prior request-failure artifacts are retained as hashes, not silently erased.
    Byte/request integrity failures raise; observed enumeration problems are
    explicit unresolved results with complete original occurrence references.
    """
    checked(part)
    receipts = sorted(directory.glob("page_*.receipt.json"))
    expected_names = [f"page_{i:06d}.receipt.json" for i in range(1, len(receipts) + 1)]
    if [p.name for p in receipts] != expected_names:
        raise ValueError("page receipt gap or unexpected name")
    raw_files = {p.name for p in directory.glob("page_*.json")
                 if not p.name.endswith(".receipt.json")}
    if raw_files != {name.replace(".receipt.json", ".json") for name in expected_names}:
        raise ValueError("orphan raw page or missing raw page")
    cursor, terminal = "*", False
    seen_cursors = {"*"}
    totals, occurrences, issues, pins = [], [], [], []
    previous_date = None
    for number, receipt_path in enumerate(receipts, 1):
        if terminal:
            raise ValueError("cached pages exist after a terminal receipt")
        receipt_raw = receipt_path.read_bytes()
        receipt = json.loads(receipt_raw)
        raw_path = receipt_path.with_name(receipt_path.name.replace(".receipt.json", ".json"))
        raw = raw_path.read_bytes()
        raw_hash = sha(raw)
        if (receipt.get("database") != "openalex"
                or receipt.get("params") != request_params(part, cursor)
                or receipt.get("raw_sha256") != raw_hash
                or type(receipt.get("bytes")) is not int or receipt["bytes"] != len(raw)):
            raise ValueError("cached request or byte hash mismatch")
        retrieved = datetime.fromisoformat(str(receipt.get("retrieved_utc", "")).replace("Z", "+00:00"))
        if retrieved.tzinfo is None:
            raise ValueError("retrieval timestamp must carry a timezone")
        body = json.loads(raw)
        rows, meta = body.get("results"), body.get("meta")
        if not isinstance(rows, list) or len(rows) > PAGE_SIZE or not isinstance(meta, dict):
            raise ValueError("malformed cached result page")
        total = meta.get("count")
        if type(total) is not int or total < 0 or "next_cursor" not in meta:
            raise ValueError("malformed total or missing next_cursor")
        nxt = meta["next_cursor"]
        if nxt is not None and (not isinstance(nxt, str) or not nxt):
            raise ValueError("malformed continuation cursor")
        if nxt is not None:
            if nxt in seen_cursors:
                issues.append("REPEATED_CURSOR")
            seen_cursors.add(nxt)
        totals.append(total)
        pins.append(dict(raw_path=str(raw_path), raw_sha256=raw_hash,
                         receipt_path=str(receipt_path), receipt_sha256=sha(receipt_raw)))
        for offset, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError("malformed work record")
            ident = provider_id(row.get("id"))
            if ident is None:
                issues.append("INVALID_PROVIDER_ID")
            try:
                published = iso_day(row.get("publication_date"))
            except (ValueError, TypeError):
                published = None
            if published is None or not iso_day(part["start"]) <= published <= iso_day(part["end"]):
                issues.append("INVALID_OR_OUT_OF_PARTITION_DATE")
            if published is not None:
                if previous_date is not None and published < previous_date:
                    issues.append("PUBLICATION_DATE_ORDER_VIOLATION")
                previous_date = published
            occurrences.append(dict(provider_id=ident, query_index=part["query_index"],
                                    partition_id=part["partition_id"], page=number,
                                    item_index=offset, raw_page=str(raw_path), raw_sha256=raw_hash,
                                    record_sha256=sha(json.dumps(row, sort_keys=True).encode()),
                                    publication_date=row.get("publication_date")))
        # The live API can terminate on a nonempty final page. Exhaustion is
        # the explicit null cursor; exact counts and identities remain required.
        terminal = nxt is None
        if not rows and nxt is not None:
            issues.append("EMPTY_NONTERMINAL_PAGE")
        cursor = nxt
    counts = Counter(row["provider_id"] for row in occurrences if row["provider_id"])
    duplicates = sorted(ident for ident, count in counts.items() if count > 1)
    if duplicates:
        issues.append("DUPLICATE_PROVIDER_ID")
    if len(set(totals)) > 1:
        issues.append("CHANGING_TOTAL")
    if terminal and totals and totals[-1] != len(occurrences):
        issues.append("TOTAL_RAW_COUNT_MISMATCH")
    if not terminal:
        issues.append("MISSING_TERMINAL_RECEIPT")
    failures = [dict(path=str(p), sha256=file_sha(p)) for p in sorted(directory.glob("*"))
                if p.is_file() and (p.name == "failures.jsonl" or ".error." in p.name)]
    stable = bool(receipts) and not issues
    instability = set(issues) - {"MISSING_TERMINAL_RECEIPT"}
    children = split_partition(part) if instability else []
    return dict(partition=part,
                status="VALIDATED_OBSERVED_PARTITION" if stable else "UNRESOLVED_PARTITION",
                reported_totals=sorted(set(totals)), raw_records=len(occurrences),
                unique_provider_ids=len(counts), duplicate_provider_ids=duplicates,
                terminal_receipt=terminal, issues=sorted(set(issues)), page_pins=pins,
                preserved_failure_artifacts=failures, occurrences=occurrences,
                proposed_child_partitions=children,
                next_action=("NONE" if stable else "SUBDIVIDE_COMPLETE_UNIT" if children
                             else "UNRESOLVED_DAY" if instability else "RETRIEVE_OR_RESUME"),
                limitation=LIMITATION)


def reconcile_identities(old: list[dict], new: list[dict]) -> dict:
    """Keep both sides and their occurrence references; never delete old-only IDs."""
    groups = defaultdict(lambda: {"old": [], "new": []})
    unresolved = []
    for origin, rows in (("old", old), ("new", new)):
        for row in rows:
            ident = provider_id(row.get("provider_id"))
            if ident is None:
                unresolved.append(dict(origin=origin, occurrence=row))
            else:
                groups[ident][origin].append(row)
    union = []
    for ident, sides in sorted(groups.items()):
        before = sorted({row["query_index"] for row in sides["old"]})
        after = sorted({row["query_index"] for row in sides["new"]})
        union.append(dict(provider_id=ident,
                          membership="BOTH" if before and after else "OLD_ONLY" if before else "NEW_ONLY",
                          old_query_indices=before, new_query_indices=after,
                          query_membership_changed=bool(before and after and before != after),
                          occurrences=sides))
    return dict(identity_union=union, unresolved_identity_occurrences=unresolved,
                counts=dict(old_unique=sum(bool(x["old_query_indices"]) for x in union),
                            new_unique=sum(bool(x["new_query_indices"]) for x in union),
                            union_unique=len(union)),
                missing_old_ids_are_not_exclusions=True)


def validate_reconciliation(reports: list[dict], old_occurrences: list[dict]) -> dict:
    """Validate leaf coverage and identities, not eligibility or global completion."""
    validate_cover([row["partition"] for row in reports])
    new = [occ for report in reports for occ in report["occurrences"]]
    counts = Counter((row["query_index"], row["provider_id"]) for row in new if row["provider_id"])
    duplicates = [dict(query_index=q, provider_id=ident, occurrences=count)
                  for (q, ident), count in sorted(counts.items()) if count > 1]
    consistent = all(r["status"] == "VALIDATED_OBSERVED_PARTITION" for r in reports) and not duplicates
    return dict(status="OBSERVED_PARTITION_ENUMERATION_CONSISTENT" if consistent else "UNRESOLVED",
                cross_partition_or_within_partition_duplicates=duplicates,
                identity_reconciliation=reconcile_identities(old_occurrences, new),
                global_p_lit_complete=False, limitation=LIMITATION)


def prepare_plan(source: Path, out: Path) -> dict:
    source, out = source.resolve(), out.resolve()
    if out == source or source in out.parents or out in source.parents:
        raise ValueError("plan output must be separate from the preserved source")
    if out.exists():
        raise FileExistsError("use a new output directory; no existing artifact is overwritten")
    names = ["search_spec.json", "search_readout.json", "candidates.jsonl"]
    names += [p.relative_to(source).as_posix() for p in sorted((source / "raw/openalex").glob("q*/status.json"))]
    pins = {name: file_sha(source / name) for name in names}
    spec = json.loads((source / "search_spec.json").read_text(encoding="utf-8"))
    if spec.get("queries") != list(QUERIES) or spec.get("date_window") != [START, END]:
        raise ValueError("source changes the registered queries or date window")
    old = []
    with (source / "candidates.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            candidate = json.loads(line)
            for occurrence in candidate["source_occurrences"]:
                if occurrence["database"] == "openalex":
                    q = occurrence["query_index"]
                    if type(q) is not int or not 1 <= q <= 4:
                        raise ValueError("old occurrence has unregistered query index")
                    old.append(dict(provider_id=occurrence["metadata"].get("source_identifier"),
                                    query_index=q, candidate_id=candidate["candidate_id"],
                                    raw_page=occurrence["raw_page"], raw_sha256=occurrence["raw_sha256"],
                                    page=occurrence["page"], item_index=occurrence["item_index"]))
    if pins != {name: file_sha(source / name) for name in names}:
        raise ValueError("source changed while the plan was prepared")
    parts = initial_partitions()
    validate_cover(parts)
    plan = dict(schema="p-lit-reconciliation-plan-v1", prepared_utc=datetime.now(timezone.utc).isoformat(),
                state="PROSPECTIVE_NOT_RETRIEVED", queries=list(QUERIES), date_window=[START, END],
                provider="openalex", endpoint=BASE, page_size=PAGE_SIZE, sort=SORT,
                partitions=[dict(partition=p, initial_request=request_params(p)) for p in parts],
                preserved_source=dict(directory=str(source), files_sha256=pins,
                                      validation="Pinned prior export; old enumeration flags remain untouched."),
                source_sha256=file_sha(Path(__file__)), documentation=DOCUMENTATION,
                refinement="Unstable year to complete months; unstable month to complete days; unstable day unresolved.",
                terminal_rule="Explicit next_cursor null; empty or nonempty final results; exact counts and identities required.",
                count_tolerance=0, new_requests_made=0, global_p_lit_complete=False,
                limitation=LIMITATION)
    old_union = reconcile_identities(old, [])
    out.mkdir(parents=True)
    for name, value in (("plan.json", plan), ("old_identity_inventory.json", old_union)):
        with (out / name).open("x", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    plan = prepare_plan(args.source, args.out)
    print(json.dumps(dict(state=plan["state"], partitions=len(plan["partitions"]),
                          requests=0, global_p_lit_complete=False)))


if __name__ == "__main__":
    main()
