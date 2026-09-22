"""Offline contracts for prospective partitions, preserved evidence and identity union."""
import json
from pathlib import Path
import socket
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from s2.literature import reconcile_plan as rp


def part(level="year", start="2020-01-01", end="2020-12-31", q=1):
    return rp.partition(q, start, end, level)


def item(i=1, published="2020-01-01"):
    return dict(id=f"https://openalex.org/W{i}", publication_date=published,
                display_name=f"Paper {i}")


def page(directory, partition, number, rows, total, cursor="*", nxt=None):
    directory.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(dict(results=rows, meta=dict(count=total, next_cursor=nxt))).encode()
    receipt = dict(database="openalex", params=rp.request_params(partition, cursor),
                   retrieved_utc="2026-09-20T00:00:00+00:00",
                   raw_sha256=rp.sha(raw), bytes=len(raw))
    (directory / f"page_{number:06d}.json").write_bytes(raw)
    (directory / f"page_{number:06d}.receipt.json").write_text(json.dumps(receipt), encoding="utf-8")


def successful(directory, partition, rows=None):
    rows = [item(published=partition["start"])] if rows is None else rows
    if rows:
        page(directory, partition, 1, rows, len(rows), nxt="next")
        page(directory, partition, 2, [], len(rows), cursor="next")
    else:
        page(directory, partition, 1, [], 0)
    return rp.validate_cached_partition(partition, directory)


def test_exact_queries_calendar_coverage_sort_and_maximum_date():
    from s2.literature import search
    leaves = rp.initial_partitions()
    assert len(leaves) == 64
    assert rp.QUERIES == search.QUERIES
    assert (rp.START, rp.END) == (search.START, search.END)
    rp.validate_cover(leaves)
    for leaf in leaves:
        request = rp.request_params(leaf)
        assert request["search"] == search.QUERIES[leaf["query_index"] - 1]
        assert request["per_page"] == 100 and request["cursor"] == "*"
        assert request["sort"] == "publication_date:asc,cited_by_count:asc"
    assert leaves[-1]["end"] == "2026-09-18"


def test_full_refinement_handles_leap_february_and_clipped_final_year():
    months = rp.split_partition(part())
    assert len(months) == 12
    february = months[1]
    days = rp.split_partition(february)
    assert len(days) == 29 and days[-1]["end"] == "2020-02-29"
    assert rp.split_partition(days[-1]) == []
    final_months = rp.split_partition(part(start="2026-01-01", end=rp.END))
    assert len(final_months) == 9
    assert len(rp.split_partition(final_months[-1])) == 18
    leaves = [p for p in rp.initial_partitions() if p != part()]
    leaves += months
    rp.validate_cover(leaves)


@pytest.mark.parametrize("change", ["missing", "duplicate", "overlap"])
def test_coverage_cannot_be_satisfied_by_partial_or_overlapping_leaves(change):
    leaves = rp.initial_partitions()
    if change == "missing":
        leaves.pop()
    elif change == "duplicate":
        leaves.append(leaves[0])
    else:
        leaves.extend(rp.split_partition(leaves[0]))
    with pytest.raises(ValueError, match="coverage"):
        rp.validate_cover(leaves)


def test_tampered_literal_or_partial_calendar_partition_is_rejected():
    bad = dict(part(), literal_query="broader query")
    with pytest.raises(ValueError):
        rp.request_params(bad)
    with pytest.raises(ValueError, match="complete calendar"):
        rp.partition(1, "2020-01-02", "2020-12-31", "year")


def test_valid_terminal_receipt_and_prior_failure_artifact_are_preserved(tmp_path):
    p = part()
    report = successful(tmp_path, p)
    assert report["status"] == "VALIDATED_OBSERVED_PARTITION"
    assert report["terminal_receipt"] and report["raw_records"] == 1
    assert len(report["page_pins"]) == 2
    failure = tmp_path / "page_000001.attempt_1.1.error.txt"
    failure.write_bytes(b"old transient failure")
    second = rp.validate_cached_partition(p, tmp_path)
    assert second["status"] == "VALIDATED_OBSERVED_PARTITION"
    assert second["preserved_failure_artifacts"][0]["sha256"] == rp.sha(failure.read_bytes())


def test_empty_partition_requires_real_zero_count_terminal_receipt(tmp_path):
    p = part()
    missing = rp.validate_cached_partition(p, tmp_path)
    assert missing["status"] == "UNRESOLVED_PARTITION"
    assert missing["next_action"] == "RETRIEVE_OR_RESUME"
    page(tmp_path, p, 1, [], 0)
    assert rp.validate_cached_partition(p, tmp_path)["status"] == "VALIDATED_OBSERVED_PARTITION"


@pytest.mark.parametrize("counts,expected", [
    ([1, 2], "CHANGING_TOTAL"),
    ([2, 2], "TOTAL_RAW_COUNT_MISMATCH"),
])
def test_count_drift_has_no_tolerance_and_proposes_all_months(tmp_path, counts, expected):
    p = part()
    page(tmp_path, p, 1, [item()], counts[0], nxt="next")
    page(tmp_path, p, 2, [], counts[1], cursor="next")
    report = rp.validate_cached_partition(p, tmp_path)
    assert report["status"] == "UNRESOLVED_PARTITION"
    assert expected in report["issues"]
    assert len(report["proposed_child_partitions"]) == 12


def test_daily_instability_stays_unresolved_instead_of_relaxing_rule(tmp_path):
    p = part("day", "2020-01-01", "2020-01-01")
    page(tmp_path, p, 1, [item()], 2, nxt="next")
    page(tmp_path, p, 2, [], 2, cursor="next")
    report = rp.validate_cached_partition(p, tmp_path)
    assert report["next_action"] == "UNRESOLVED_DAY"
    assert not report["proposed_child_partitions"]


@pytest.mark.parametrize("rows,issue", [
    ([item(), item()], "DUPLICATE_PROVIDER_ID"),
    ([dict(item(), id=None)], "INVALID_PROVIDER_ID"),
    ([dict(item(), id="https://openalex.org/A1")], "INVALID_PROVIDER_ID"),
    ([item(published="2019-12-31")], "INVALID_OR_OUT_OF_PARTITION_DATE"),
    ([item(published="2020-01-02"), item(2)], "PUBLICATION_DATE_ORDER_VIOLATION"),
])
def test_counts_do_not_hide_identity_or_partition_problems(tmp_path, rows, issue):
    report = successful(tmp_path, part(), rows)
    assert report["status"] == "UNRESOLVED_PARTITION" and issue in report["issues"]
    assert len(report["occurrences"]) == len(rows)


@pytest.mark.parametrize("first_next,second_next", [("*", "end"), ("next", "next")])
def test_repeated_cursor_cannot_pass_with_distinct_ids_and_consistent_counts(tmp_path, first_next, second_next):
    p = part()
    page(tmp_path, p, 1, [item(1)], 2, nxt=first_next)
    page(tmp_path, p, 2, [item(2)], 2, cursor=first_next, nxt=second_next)
    page(tmp_path, p, 3, [], 2, cursor=second_next)
    report = rp.validate_cached_partition(p, tmp_path)
    assert report["terminal_receipt"] and report["reported_totals"] == [2]
    assert report["raw_records"] == report["unique_provider_ids"] == 2
    assert report["issues"] == ["REPEATED_CURSOR"]
    assert report["status"] == "UNRESOLVED_PARTITION"
    assert len(report["proposed_child_partitions"]) == 12


@pytest.mark.parametrize("full_final_page", [False, True])
def test_nonempty_null_cursor_is_a_terminal_receipt_when_counts_and_ids_agree(tmp_path, full_final_page):
    p = part()
    if full_final_page:
        page(tmp_path, p, 1, [item()], 101, nxt="next")
        page(tmp_path, p, 2, [item(i) for i in range(2, 102)], 101, cursor="next")
    else:
        page(tmp_path, p, 1, [item()], 1)
    report = rp.validate_cached_partition(p, tmp_path)
    assert report["terminal_receipt"]
    assert report["status"] == "VALIDATED_OBSERVED_PARTITION"
    assert report["raw_records"] == report["unique_provider_ids"] == (101 if full_final_page else 1)
    assert len(report["page_pins"]) == (2 if full_final_page else 1)
    assert not report["issues"]


@pytest.mark.parametrize("totals,issue", [
    ([1, 2], "CHANGING_TOTAL"),
    ([3, 3], "TOTAL_RAW_COUNT_MISMATCH"),
])
def test_nonempty_terminal_page_cannot_hide_count_drift(tmp_path, totals, issue):
    p = part()
    page(tmp_path, p, 1, [item()], totals[0], nxt="next")
    page(tmp_path, p, 2, [item(2)], totals[1], cursor="next")
    report = rp.validate_cached_partition(p, tmp_path)
    assert report["terminal_receipt"]
    assert report["status"] == "UNRESOLVED_PARTITION"
    assert issue in report["issues"]


@pytest.mark.parametrize("mutation", ["hash", "query", "cursor", "timezone", "count_bool", "missing_cursor"])
def test_malformed_or_mismatched_receipt_cannot_validate(tmp_path, mutation):
    p = part()
    successful(tmp_path, p)
    target = tmp_path / "page_000002.receipt.json"
    receipt = json.loads(target.read_text())
    if mutation == "hash":
        (tmp_path / "page_000002.json").write_bytes(b"{}")
    elif mutation == "query":
        receipt["params"]["search"] = "different"
    elif mutation == "cursor":
        receipt["params"]["cursor"] = "*"
    elif mutation == "timezone":
        receipt["retrieved_utc"] = "2026-09-20T00:00:00"
    else:
        raw_path = tmp_path / "page_000002.json"
        body = json.loads(raw_path.read_bytes())
        if mutation == "count_bool":
            body["meta"]["count"] = True
        else:
            del body["meta"]["next_cursor"]
        raw = json.dumps(body).encode()
        raw_path.write_bytes(raw)
        receipt.update(raw_sha256=rp.sha(raw), bytes=len(raw))
    target.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ValueError):
        rp.validate_cached_partition(p, tmp_path)


def test_orphan_gap_and_post_terminal_pages_fail_closed(tmp_path):
    p = part()
    (tmp_path / "page_000001.json").write_bytes(b"{}")
    with pytest.raises(ValueError, match="orphan"):
        rp.validate_cached_partition(p, tmp_path)
    page(tmp_path, p, 1, [], 0)
    page(tmp_path, p, 2, [], 0, cursor="next")
    with pytest.raises(ValueError, match="after a terminal"):
        rp.validate_cached_partition(p, tmp_path)
    (tmp_path / "page_000001.receipt.json").unlink()
    with pytest.raises(ValueError, match="gap"):
        rp.validate_cached_partition(p, tmp_path)


def test_identity_union_preserves_old_only_new_only_and_query_discrepancies():
    old = [dict(provider_id="W1", query_index=1, raw_page="old1"),
           dict(provider_id="W2", query_index=1, raw_page="old2"),
           dict(provider_id=None, query_index=2, raw_page="old-unknown")]
    new = [dict(provider_id="https://openalex.org/W2", query_index=3, raw_page="new2"),
           dict(provider_id="W3", query_index=1, raw_page="new3")]
    result = rp.reconcile_identities(old, new)
    assert result["counts"] == dict(old_unique=2, new_unique=2, union_unique=3)
    assert [r["membership"] for r in result["identity_union"]] == ["OLD_ONLY", "BOTH", "NEW_ONLY"]
    assert result["identity_union"][1]["query_membership_changed"]
    assert result["identity_union"][0]["occurrences"]["old"] == [old[0]]
    assert result["unresolved_identity_occurrences"] == [dict(origin="old", occurrence=old[2])]


def test_cross_partition_identity_migration_remains_unresolved(tmp_path):
    reports = []
    for p in rp.initial_partitions():
        # Same valid provider ID appears in different years; every local count still agrees.
        rows = [item(published=p["start"])] if p["query_index"] == 1 else []
        reports.append(successful(tmp_path / p["partition_id"], p, rows))
    report = rp.validate_reconciliation(reports, [])
    assert report["status"] == "UNRESOLVED"
    assert report["cross_partition_or_within_partition_duplicates"]
    assert report["global_p_lit_complete"] is False


def test_all_consistent_partitions_still_do_not_claim_global_completion(tmp_path):
    reports = [successful(tmp_path / p["partition_id"], p, []) for p in rp.initial_partitions()]
    report = rp.validate_reconciliation(reports, [])
    assert report["status"] == "OBSERVED_PARTITION_ENUMERATION_CONSISTENT"
    assert report["global_p_lit_complete"] is False


def source_cache(path):
    path.mkdir()
    (path / "search_spec.json").write_text(json.dumps(dict(
        queries=list(rp.QUERIES), date_window=[rp.START, rp.END])), encoding="utf-8")
    (path / "search_readout.json").write_text('{"status":"ENUMERATED_WITH_COUNT_DRIFT"}')
    occurrence = dict(database="openalex", query_index=1, page=1, item_index=0,
                      raw_page="raw/openalex/q01/page_000001.json", raw_sha256="a" * 64,
                      metadata=dict(source_identifier="W1"))
    candidate = dict(candidate_id="candidate1", source_occurrences=[occurrence])
    (path / "candidates.jsonl").write_text(json.dumps(candidate) + "\n", encoding="utf-8")


def test_prepare_is_offline_additive_and_never_claims_coverage(tmp_path, monkeypatch):
    source, out = tmp_path / "old", tmp_path / "plan"
    source_cache(source)
    before = {p.name: p.read_bytes() for p in source.iterdir()}
    monkeypatch.setattr(socket, "socket", lambda *a, **k: pytest.fail("no network permitted"))
    plan = rp.prepare_plan(source, out)
    assert plan["state"] == "PROSPECTIVE_NOT_RETRIEVED"
    assert plan["new_requests_made"] == 0 and not plan["global_p_lit_complete"]
    assert len(plan["partitions"]) == 64
    assert before == {p.name: p.read_bytes() for p in source.iterdir()}
    union = json.loads((out / "old_identity_inventory.json").read_text())
    assert union["counts"]["old_unique"] == 1
    with pytest.raises(FileExistsError):
        rp.prepare_plan(source, out)
    with pytest.raises(ValueError, match="separate"):
        rp.prepare_plan(source, source / "nested")
