"""Offline retrieval contracts; real network is forbidden throughout."""
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace
import urllib.error

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from s2.literature import reconcile_plan as rp
from s2.literature import reconcile_search as rs


NOW = datetime(2026, 9, 21, 1, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("offline tests must never create a network socket")
    monkeypatch.setattr(socket, "socket", forbidden)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def response(rows=(), total=0, nxt=None):
    return json.dumps(dict(results=list(rows), meta=dict(count=total, next_cursor=nxt))).encode(), {}


def item(params, ident="W900"):
    published = params["filter"].split(",")[0].split(":")[1]
    return dict(id="https://openalex.org/" + ident, publication_date=published,
                display_name="A complete preserved paper", doi="https://doi.org/example")


def pins(directory):
    return dict(rs.LOADED_CODE_SHA256, plan_sha256=rs.search.file_sha(directory / "plan.json"),
                old_inventory_sha256=rs.search.file_sha(directory / "old_identity_inventory.json"))


@pytest.fixture
def fixture(tmp_path):
    provider = tmp_path / "broad"
    provider.mkdir()
    dump(provider / "search_spec.json", dict(
        schema="p-lit-continuation-spec-v1", queries=list(rp.QUERIES),
        date_window=[rp.START, rp.END], pipeline_sha256=rs.search.LOADED_SOURCE_SHA256,
        discovery_databases=["openalex"]))
    dump(provider / "search_readout.json", dict(database_search_complete=False))
    old = []
    for number in (900, 901):
        old.append(dict(candidate_id=str(number), source_occurrences=[dict(
            database="openalex", query_index=1, metadata=dict(source_identifier=f"W{number}"),
            raw_page="raw/openalex/q01/page_000001.json", raw_sha256="a" * 64,
            page=1, item_index=number - 900)]))
    (provider / "candidates.jsonl").write_text(
        "\n".join(json.dumps(r) for r in old) + "\n", encoding="utf-8")
    directory = tmp_path / "plan"
    rp.prepare_plan(provider, directory)
    return SimpleNamespace(plan=directory, out=tmp_path / "run", provider=provider,
                           expected=pins(directory))


def execute(f, fetch, budget=1, **kwargs):
    return rs.run(f.plan, f.out, f.provider, expected_pins=f.expected,
                  page_budget=budget, fetch=fetch, clock=lambda: NOW, delay=0, **kwargs)


def artifact(f, result, name):
    entry = result["artifacts"][name]
    path = f.out / entry["path"]
    assert rs.search.file_sha(path) == entry["sha256"]
    return json.loads(path.read_bytes())


def test_all_64_years_use_exact_registered_requests_and_never_claim_global_complete(fixture):
    calls = []
    def fetch(database, params):
        assert database == "openalex"
        calls.append(params)
        return response()
    result = execute(fixture, fetch, 64)
    assert calls == [rp.request_params(p) for p in rp.initial_partitions()]
    assert result["leaf_status"] == "OBSERVED_PARTITION_ENUMERATION_CONSISTENT"
    assert result["validated_leaves"] == result["leaf_partitions"] == 64
    assert result["requests_this_pass"] == 64
    assert result["global_p_lit_complete"] is False
    assert result["database_search_complete"] is False
    assert not result["inclusion_list_frozen"]
    leaf = artifact(fixture, result, "leaf_validation.json")
    assert leaf["status"] == "OBSERVED_PARTITION_ENUMERATION_CONSISTENT"
    assert not (fixture.provider / ".search.lock").exists()
    assert not (fixture.out / ".search.lock").exists()


def test_page_budget_resume_uses_exact_cursor_and_keeps_completed_bytes(fixture):
    calls = []
    def first(database, params):
        calls.append(params)
        return response([item(params)], 2, "opaque-token")
    result = execute(fixture, first)
    raw = fixture.out / "raw/openalex" / rp.initial_partitions()[0]["partition_id"] / "attempt_000001/page_000001.json"
    original = raw.read_bytes()
    def second(database, params):
        calls.append(params)
        assert params["cursor"] == "opaque-token"
        return response([item(params, "W902")], 2)
    resumed = execute(fixture, second)
    assert result["operation_status"] == resumed["operation_status"] == "PAGE_BUDGET_REACHED"
    assert resumed["validated_leaves"] == 1 and resumed["requests_this_pass"] == 1
    assert raw.read_bytes() == original
    union = artifact(fixture, resumed, "identity_reconciliation.json")
    assert union["counts"] == dict(old_unique=2, new_unique=2, union_unique=3)
    both = next(r for r in union["identity_union"] if r["provider_id"].endswith("W900"))
    assert both["membership"] == "BOTH" and len(both["occurrences"]["new"]) == 1
    receipt = json.loads(raw.with_name("page_000001.receipt.json").read_bytes())
    assert set(receipt) == {"database", "params", "url", "retrieved_utc", "raw_sha256",
                           "bytes", "response_headers", "successful_attempt", "previous_failures"}


def test_timeout_stops_pass_and_resumes_intact_prefix_without_refetch(fixture):
    count = 0
    def interrupted(database, params):
        nonlocal count
        count += 1
        if count == 1:
            return response([item(params)], 1, "end")
        raise TimeoutError("private-url-must-not-appear")
    failed = execute(fixture, interrupted, 5)
    assert failed["operation_status"] == "REQUEST_FAILED" and failed["requests_this_pass"] == 2
    ledger = next(fixture.out.glob("raw/openalex/*/attempt_000001/failures.jsonl"))
    assert "private-url" not in ledger.read_text()
    def resumed(database, params):
        assert params["cursor"] == "end"
        return response([], 1)
    result = execute(fixture, resumed)
    assert result["validated_leaves"] == 1
    reports = artifact(fixture, result, "partition_reports.json")
    assert reports[0]["preserved_failure_artifacts"]


@pytest.mark.parametrize("target", ["out", "provider"])
def test_existing_collector_lock_prevents_every_request(fixture, target):
    directory = getattr(fixture, target)
    directory.mkdir(exist_ok=True)
    (directory / ".search.lock").write_text("another collector")
    with pytest.raises(RuntimeError, match="locked"):
        execute(fixture, lambda *_: pytest.fail("request despite another collector"))
    assert (directory / ".search.lock").read_text() == "another collector"


def test_nested_collector_cannot_enter_while_fetching(fixture):
    def fetch(database, params):
        with pytest.raises(RuntimeError, match="locked"):
            execute(fixture, lambda *_: pytest.fail("duplicate request"))
        assert (fixture.provider / ".search.lock").exists()
        return response()
    assert execute(fixture, fetch)["requests_this_pass"] == 1


def test_shared_existing_cooldown_blocks_and_preserves_prior_state(fixture):
    state = dict(provider="openalex", reason="DEFERRED_RATE_LIMIT",
                 next_allowed_utc="2026-09-21T02:00:00+00:00", evidence=dict(test="old"))
    path = fixture.provider / "provider_cooldowns/openalex.json"
    dump(path, state)
    old = path.read_bytes()
    result = execute(fixture, lambda *_: pytest.fail("quota bypass"))
    assert result["requests_this_pass"] == 0
    assert result["operation_status"] == "DEFERRED_RATE_LIMIT"
    history = path.parent / "history" / (rs.search.sha(old) + ".json")
    assert history.read_bytes() == old
    assert json.loads((fixture.out / "provider_cooldowns/openalex.json").read_bytes())["evidence_directory"] == str(fixture.provider)


@pytest.mark.parametrize("status,body,headers,reason", [
    (429, b'{"dailyRemainingUsd":0,"prepaidRemainingUsd":0,"message":"resets at midnight UTC"}',
     {}, "DEFERRED_API_BUDGET"),
    (503, b'{"error":"temporary"}', {"Retry-After": "120"}, "DEFERRED_PROVIDER_RETRY"),
])
def test_quota_policy_captures_failure_and_publishes_deferral(fixture, status, body, headers, reason):
    def fetch(*args):
        raise urllib.error.HTTPError("https://secret/?api_key=private", status, "bad",
                                     headers, io.BytesIO(body))
    result = execute(fixture, fetch, 10)
    assert result["operation_status"] == reason and result["requests_this_pass"] == 1
    raw = next((fixture.out / "transport_failures").glob("*.body"))
    assert raw.read_bytes() == body
    shared = json.loads((fixture.provider / "provider_cooldowns/openalex.json").read_bytes())
    assert shared["reason"] == reason
    assert shared["evidence_directory"] == str(fixture.out)
    assert shared["evidence"]["raw_sha256"] == rs.search.sha(body)
    again = execute(fixture, lambda *_: pytest.fail("shared quota not retained"), 10)
    assert again["requests_this_pass"] == 0


def test_http_failure_without_retry_boundary_ends_after_one_request(fixture):
    def fetch(*args):
        raise urllib.error.HTTPError("https://secret/?api_key=private", 503, "bad", {}, io.BytesIO(b"offline"))
    result = execute(fixture, fetch, 10)
    assert result["requests_this_pass"] == 1 and result["operation_status"] == "REQUEST_FAILED"
    assert len(list((fixture.out / "transport_failures").glob("*.body"))) == 1
    assert "private" not in next(fixture.out.glob("raw/openalex/*/attempt_000001/failures.jsonl")).read_text()


def test_unstable_parent_subdivides_every_month_and_keeps_parent_occurrences(fixture):
    count = 0
    def fetch(database, params):
        nonlocal count
        count += 1
        if count == 1:
            return response([item(params, "W903")], 2)  # exact terminal count mismatch
        assert params["filter"] == "from_publication_date:2011-01-01,to_publication_date:2011-01-31"
        return response([item(params, "W904")], 1)
    result = execute(fixture, fetch, 2)
    assert result["leaf_partitions"] == 75 and result["validated_leaves"] == 1
    reports = artifact(fixture, result, "partition_reports.json")
    parent = reports[0]
    assert parent["issues"] == ["TOTAL_RAW_COUNT_MISMATCH"]
    assert len(parent["proposed_child_partitions"]) == 12
    union = artifact(fixture, result, "identity_reconciliation.json")
    assert any(r["provider_id"].endswith("W903") for r in union["identity_union"])
    leaf = artifact(fixture, result, "leaf_validation.json")
    assert not any(r["provider_id"].endswith("W903") for r in leaf["identity_reconciliation"]["identity_union"])
    assert result["new_occurrences_including_unstable_parents"] == 2


def test_unstable_month_refines_all_days_and_unstable_day_is_retained(fixture):
    def fetch(database, params):
        return response([item(params)], 2)
    result = execute(fixture, fetch, 3)
    reports = artifact(fixture, result, "partition_reports.json")
    assert result["leaf_partitions"] == 105  # 64 - 1 + 12 - 1 + 31
    daily = next(r for r in reports if r["partition"]["level"] == "day" and r["raw_records"])
    assert daily["next_action"] == "UNRESOLVED_DAY"
    assert daily["proposed_child_partitions"] == []
    union = artifact(fixture, result, "identity_reconciliation.json")
    paper = next(r for r in union["identity_union"] if r["provider_id"].endswith("W900"))
    assert len(paper["occurrences"]["new"]) == 3


def test_repeated_cursor_refines_without_repeating_provider_request(fixture):
    result = execute(fixture, lambda db, p: response([item(p)], 1, "*"))
    report = artifact(fixture, result, "partition_reports.json")[0]
    assert "REPEATED_CURSOR" in report["issues"]
    assert result["requests_this_pass"] == 1 and result["leaf_partitions"] == 75


def test_invalid_id_remains_unresolved_occurrence_when_parent_refines(fixture):
    result = execute(fixture, lambda db, p: response([dict(item(p), id=None)], 1))
    union = artifact(fixture, result, "identity_reconciliation.json")
    assert len(union["unresolved_identity_occurrences"]) == 1
    assert union["unresolved_identity_occurrences"][0]["origin"] == "new"


@pytest.mark.parametrize("change", ["raw_hash", "cursor", "orphan", "unregistered_attempt"])
def test_corrupt_cache_is_refused_before_any_further_request(fixture, change):
    execute(fixture, lambda db, p: response([item(p)], 1, "next"))
    directory = next(fixture.out.glob("raw/openalex/*/attempt_000001"))
    raw = directory / "page_000001.json"
    receipt = directory / "page_000001.receipt.json"
    if change == "raw_hash":
        raw.write_bytes(b"{}")
    elif change == "cursor":
        value = json.loads(receipt.read_bytes())
        value["params"]["cursor"] = "wrong"
        dump(receipt, value)
    elif change == "orphan":
        receipt.unlink()
    else:
        (directory.parent / "attempt_000002").mkdir()
    with pytest.raises(ValueError):
        execute(fixture, lambda *_: pytest.fail("corrupt cache caused a request"))
    error = json.loads((fixture.out / "last_pass.json").read_bytes())
    assert error["operation_status"] == "INTEGRITY_OR_MALFORMED_RESPONSE_ERROR"
    assert error["requests_this_pass"] == 0


@pytest.mark.parametrize("raw", [b"{", b'{"results":[5],"meta":{"count":1,"next_cursor":null}}',
                               b'{"results":[],"meta":{"count":true,"next_cursor":null}}'])
def test_malformed_success_is_preserved_and_stops_without_skipping(fixture, raw):
    with pytest.raises((ValueError, TypeError)):
        execute(fixture, lambda *_: (raw, {}), 10)
    kept = next(fixture.out.glob("raw/openalex/*/attempt_000001/page_000001.json"))
    assert kept.read_bytes() == raw
    error = json.loads((fixture.out / "last_pass.json").read_bytes())
    assert error["requests_this_pass"] == 1
    with pytest.raises((ValueError, TypeError)):
        execute(fixture, lambda *_: pytest.fail("malformed cache skipped"))


@pytest.mark.parametrize("target", ["plan", "inventory", "runner_pin"])
def test_externally_expected_pins_reject_tampering(fixture, target):
    if target == "runner_pin":
        fixture.expected["runner_sha256"] = "0" * 64
    else:
        path = fixture.plan / ("plan.json" if target == "plan" else "old_identity_inventory.json")
        path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="pin"):
        execute(fixture, lambda *_: pytest.fail("pin mismatch requested data"))


def test_semantic_plan_tamper_cannot_be_authorized_by_rehash_alone(fixture):
    path = fixture.plan / "plan.json"
    value = json.loads(path.read_bytes())
    value["partitions"].pop()
    dump(path, value)
    fixture.expected = pins(fixture.plan)
    with pytest.raises(ValueError, match="64"):
        execute(fixture, lambda *_: pytest.fail("incomplete plan requested data"))


def test_source_change_during_request_keeps_response_but_refuses_success(fixture, monkeypatch, tmp_path):
    copy = tmp_path / "runner_copy.py"
    copy.write_bytes(rs.CODE_PATHS["runner_sha256"].read_bytes())
    monkeypatch.setitem(rs.CODE_PATHS, "runner_sha256", copy)
    def fetch(*args):
        copy.write_bytes(copy.read_bytes() + b"\n# changed\n")
        return response()
    with pytest.raises(RuntimeError, match="changed"):
        execute(fixture, fetch)
    assert len(list(fixture.out.glob("raw/openalex/*/attempt_000001/page_*.receipt.json"))) == 1
    assert not (fixture.out / "summary.json").exists()


def test_frozen_old_inventory_is_not_replaced_by_new_broad_export(fixture):
    dump(fixture.provider / "search_readout.json", dict(database_search_complete=False, new_run=True))
    (fixture.provider / "candidates.jsonl").write_text("", encoding="utf-8")
    result = execute(fixture, lambda *_: pytest.fail("zero-budget pass requested data"), 0)
    assert result["old_occurrences"] == 2
    assert result["identity_counts"]["old_unique"] == 2


def test_resume_refuses_different_launch_manifest_even_with_valid_new_hashes(fixture):
    execute(fixture, lambda *_: response())
    path = fixture.plan / "plan.json"
    value = json.loads(path.read_bytes())
    value["prepared_utc"] = "2026-09-21T00:00:00+00:00"
    dump(path, value)
    fixture.expected = pins(fixture.plan)
    with pytest.raises(ValueError, match="collision"):
        execute(fixture, lambda *_: pytest.fail("different launch reused cache"))


def test_cli_rejects_untrusted_pins_file_before_run(fixture, tmp_path):
    pinfile = tmp_path / "launch.json"
    dump(pinfile, fixture.expected)
    with pytest.raises(ValueError, match="externally supplied"):
        rs.main(["--plan", str(fixture.plan), "--out", str(fixture.out),
                 "--provider-cache", str(fixture.provider), "--pins", str(pinfile),
                 "--pins-sha256", "0" * 64])


def test_boundary_change_during_export_refuses_success_pointer(fixture, monkeypatch):
    original = rs.immutable_json
    def change_after_export(path, value):
        original(path, value)
        if path.name == "identity_reconciliation.json":
            manifest = fixture.plan / "plan.json"
            manifest.write_bytes(manifest.read_bytes() + b" ")
    monkeypatch.setattr(rs, "immutable_json", change_after_export)
    with pytest.raises(ValueError, match="pin"):
        execute(fixture, lambda *_: response())
    assert not (fixture.out / "summary.json").exists()
    assert json.loads((fixture.out / "last_pass.json").read_bytes())["requests_this_pass"] == 1



def test_cross_leaf_duplicate_ids_remain_unresolved_without_repeat_fetch(fixture):
    result = execute(fixture, lambda database, params: response([item(params)], 1), 64)
    assert result["validated_leaves"] == result["leaf_partitions"] == 64
    assert result["leaf_status"] == "UNRESOLVED"
    leaf = artifact(fixture, result, "leaf_validation.json")
    assert leaf["cross_partition_or_within_partition_duplicates"]
    resumed = execute(fixture, lambda *_: pytest.fail("locally complete leaves refetched"), 100)
    assert resumed["requests_this_pass"] == 0
    assert resumed["leaf_status"] == "UNRESOLVED"
    assert not resumed["global_p_lit_complete"]


def test_cooldown_arriving_during_delay_prevents_second_actual_fetch(fixture):
    calls = []
    def fetch(database, params):
        calls.append(params)
        return response([item(params)], 1, "next-token")
    def delay(seconds):
        assert seconds == 1
        dump(fixture.provider / "provider_cooldowns/openalex.json", dict(
            provider="openalex", reason="PROVIDER_BUDGET_EXHAUSTED",
            next_allowed_utc="2026-09-22T00:00:00+00:00"))
    result = rs.run(fixture.plan, fixture.out, fixture.provider, expected_pins=fixture.expected,
                    page_budget=10, fetch=fetch, clock=lambda: NOW, sleep=delay, delay=1)
    assert len(calls) == result["requests_this_pass"] == 1
    assert result["operation_status"] == "PROVIDER_BUDGET_EXHAUSTED"
