"""Offline quota and cache-boundary checks for the additive P-LIT driver."""
from datetime import datetime, timedelta, timezone
from email.message import Message
import io
import json
from pathlib import Path
import sys
import urllib.error

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from s2.literature import continue_search as driver
from s2.literature import search

START = datetime(2026, 9, 19, 0, 20, 0, tzinfo=timezone.utc)


def quota_body(retry=85200):
    return json.dumps(dict(message="Insufficient budget. Resets at midnight UTC.", retryAfter=retry,
                           dailyRemainingUsd=0, prepaidRemainingUsd=0)).encode()


def error(status=429, body=None, headers=None):
    message = Message()
    for key, value in (headers or {}).items():
        message[key] = str(value)
    return urllib.error.HTTPError("https://private.example?api_key=SECRET", status, "SECRET", message,
                                  io.BytesIO(body if body is not None else quota_body()))


def response(rows, count, cursor):
    return json.dumps(dict(results=rows, meta=dict(count=count, next_cursor=cursor))).encode(), {}


def item(index):
    return dict(id=f"https://openalex.org/W{index}", doi=f"https://doi.org/10.123/{index}",
                display_name=f"Article {index}", publication_year=2020, publication_date="2020-01-01",
                authorships=[dict(author=dict(display_name="A Author"))], type="article")


def source_cache(tmp_path, terminal=False):
    source = tmp_path / "source"
    source.mkdir()
    search.write_json(source / "search_spec.json", dict(schema="p-lit-search-spec-v2", queries=list(search.QUERIES),
                      date_window=[search.START, search.END], page_sizes=search.PAGE_SIZE,
                      pipeline_sha256=driver.EXPECTED_ENGINE_SHA256, discovery_databases=["openalex"],
                      decision_sha256=search.file_sha(search.DECISION), amendment_sha256=search.file_sha(search.AMENDMENT)))
    for index in range(1, 5):
        params = search.params_for("openalex", search.QUERIES[index - 1], "*")
        search.fetch_page("openalex", params, source / f"raw/openalex/q{index:02d}", 1,
                          fetch=lambda d, p, i=index: response([item(i)], 1 if terminal else 2, None if terminal else f"q{i}-next"))
    return source


def test_retry_boundaries_and_missing_budget_fields():
    boundary = driver.retry_boundary(429, quota_body(), {}, START)
    assert boundary == dict(reason="DEFERRED_API_BUDGET", next_allowed_utc="2026-09-20T00:00:00+00:00")
    assert driver.retry_boundary(429, b'{}', {}, START)["reason"] == "DEFERRED_RATE_LIMIT"
    assert driver.retry_boundary(429, b'not json', {}, START)["next_allowed_utc"] == (START + timedelta(seconds=60)).isoformat()
    assert driver.retry_boundary(500, b'{}', {}, START) is None


@pytest.mark.parametrize("headers,body,expected", [
    ({"Retry-After": "600"}, b'{}', 600),
    ({"Retry-After": "Sat, 19 Sep 2026 00:40:00 GMT"}, b'{}', 1200),
    ({"Retry-After": "120"}, b'{"retryAfter":600}', 600),
    ({"Retry-After": "600"}, b'{"retryAfter":120}', 600),
    ({"Retry-After": "garbage"}, b'{"retryAfter":-2}', 60),
])
def test_header_and_body_minimum_waits_are_not_truncated(headers, body, expected):
    boundary = driver.retry_boundary(429, body, headers, START)
    assert driver.timestamp(boundary["next_allowed_utc"]) == START + timedelta(seconds=expected)


def test_persisted_provider_cooldown_blocks_all_queries_and_restart(tmp_path):
    calls = []
    def fetch(database, params):
        calls.append(params)
        raise error(headers={"Authorization": "SECRET", "Retry-After": "85200"})
    transport = driver.QuotaTransport(tmp_path, fetch, lambda: START)
    for query in search.QUERIES:
        with pytest.raises(driver.DeferredRequest):
            transport("openalex", search.params_for("openalex", query, "next"))
    assert len(calls) == 1
    resumed = driver.QuotaTransport(tmp_path, lambda *_: pytest.fail("must not request"), lambda: START + timedelta(hours=1))
    with pytest.raises(driver.DeferredRequest):
        resumed("openalex", search.params_for("openalex", search.QUERIES[0], "next"))
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert b"SECRET" not in path.read_bytes()
    assert len(list((tmp_path / "transport_failures").glob("*.body"))) == 1


def test_short_429_defers_once_and_resumes_exact_cursor(tmp_path):
    clock = [START]
    calls = []
    def fetch(database, params):
        calls.append(params["cursor"])
        if len(calls) == 1:
            raise error(body=b'{}', headers={"Retry-After": "2"})
        return response([item(1)], 1, None)
    transport = driver.QuotaTransport(tmp_path, fetch, lambda: clock[0])
    params = search.params_for("openalex", search.QUERIES[0], "same+/=cursor")
    with pytest.raises(driver.DeferredRequest):
        transport("openalex", params)
    clock[0] += timedelta(seconds=2)
    assert transport("openalex", params)[0]
    assert calls == ["same+/=cursor", "same+/=cursor"]


def test_ordinary_5xx_keeps_bounded_engine_retry_and_raw_body(tmp_path):
    calls, sleeps = [], []
    def fetch(database, params):
        calls.append(1)
        if len(calls) < 3:
            raise error(503, b'{"message":"temporary"}')
        return response([item(1)], 1, None)
    transport = driver.QuotaTransport(tmp_path, fetch, lambda: START)
    cached = search.fetch_page("openalex", search.params_for("openalex", search.QUERIES[0], "*"),
                              tmp_path / "pages", 1, fetch=transport, sleep=sleeps.append)
    assert len(calls) == 3 and sleeps == [2, 4]
    assert cached["receipt"]["successful_attempt"] == 3
    assert not transport.path.exists()
    assert len(list((tmp_path / "pages").glob("*.error.txt"))) == 2


def test_5xx_retry_after_defers_instead_of_shortening_wait(tmp_path):
    transport = driver.QuotaTransport(tmp_path, lambda *_: (_ for _ in ()).throw(error(503, b'{}', {"Retry-After": "3600"})), lambda: START)
    with pytest.raises(driver.DeferredRequest):
        transport("openalex", {})
    assert transport.current()["reason"] == "DEFERRED_PROVIDER_RETRY"


def test_migration_seeds_existing_quota_without_any_new_request(tmp_path):
    source = source_cache(tmp_path)
    directory = source / "raw/openalex/q01"
    body = quota_body()
    (directory / "page_000002.attempt_1.error.txt").write_bytes(body)
    (directory / "failures.jsonl").write_text(json.dumps(dict(at=START.isoformat(), http_status=429,
                                  response_body_sha256=search.sha(body))) + "\n", encoding="utf-8")
    before = {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    result = driver.run(source, tmp_path / "out", fetch=lambda *_: pytest.fail("existing quota must suppress requests"), clock=lambda: START, delay=0)
    assert result["operation_status"] == "DEFERRED_API_BUDGET"
    assert result["candidate_index"]["candidates"] == result["candidate_index"]["source_occurrences"] == 4
    assert [s["returned_records"] for s in result["streams"]] == [1, 1, 1, 1]
    assert not result["database_search_complete"] and not result["inclusion_list_frozen"] and result["methods_coded"] == 0
    assert before == {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    for raw in source.glob("raw/openalex/q*/page_*.json"):
        assert raw.read_bytes() == (tmp_path / "out" / raw.relative_to(source)).read_bytes()


def test_run_stops_remaining_streams_then_resumes_after_reset(tmp_path):
    source = source_cache(tmp_path)
    out = tmp_path / "out"
    calls = []
    def quota(database, params):
        calls.append(params["cursor"])
        raise error()
    first = driver.run(source, out, fetch=quota, clock=lambda: START, delay=0)
    assert calls == ["q1-next"] and first["operation_status"] == "DEFERRED_API_BUDGET"
    driver.run(source, out, fetch=lambda *_: pytest.fail("cooldown"), clock=lambda: START, delay=0)
    def finish(database, params):
        index = search.QUERIES.index(params["search"]) + 1
        calls.append(params["cursor"])
        return response([item(index + 10)], 2, None)
    final = driver.run(source, out, fetch=finish, clock=lambda: START + timedelta(days=1), delay=0)
    assert calls == ["q1-next", "q1-next", "q2-next", "q3-next", "q4-next"]
    assert final["database_search_complete"] and final["candidate_index"]["candidates"] == 8
    assert final["methods_coded"] == 0
    rows = [json.loads(line) for line in (out / "candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(r["inclusion_status"] == "NOT_SCREENED" and r["method_coding_status"] == "NOT_CODED" for r in rows)


@pytest.mark.parametrize("repeated_page", [False, True])
def test_drift_and_duplicates_do_not_become_complete(tmp_path, repeated_page):
    source = source_cache(tmp_path)
    def finish(database, params):
        index = search.QUERIES.index(params["search"]) + 1
        row = item(index)
        if not repeated_page:
            row["display_name"] += " revised metadata"
        return response([row], 3, None)
    result = driver.run(source, tmp_path / "out", fetch=finish, clock=lambda: START, delay=0)
    assert not result["database_search_complete"]
    expected = "INCOMPLETE" if repeated_page else "ENUMERATED_WITH_COUNT_DRIFT"
    termination = "REPEATED_PAGE_WITHOUT_PROGRESS" if repeated_page else "API_EXHAUSTED"
    assert all(s["status"] == expected and s["termination"] == termination
               and s["duplicate_source_records"] == 1 and s["reported_totals"] == [2, 3]
               for s in result["streams"])
    assert result["candidate_index"]["source_occurrences"] == 8


def test_cache_tampering_fails_before_network(tmp_path):
    source = source_cache(tmp_path)
    (source / "raw/openalex/q01/page_000001.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="byte hash mismatch"):
        driver.run(source, tmp_path / "out", fetch=lambda *_: pytest.fail("no network"), clock=lambda: START)


def test_missing_quota_body_fails_closed(tmp_path):
    source = source_cache(tmp_path)
    (source / "raw/openalex/q01/failures.jsonl").write_text(json.dumps(dict(at=START.isoformat(), http_status=429,
                               response_body_sha256="missing")) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="hash-matched raw body"):
        driver.run(source, tmp_path / "out", fetch=lambda *_: pytest.fail("no network"), clock=lambda: START)


def test_driver_and_engine_pins_refuse_changed_sources(tmp_path, monkeypatch):
    source = source_cache(tmp_path)
    real = search.file_sha
    monkeypatch.setattr(search, "file_sha", lambda p: "changed" if p == driver.DRIVER_PATH else real(p))
    with pytest.raises(RuntimeError, match="driver changed"):
        driver.run(source, tmp_path / "out", fetch=lambda *_: pytest.fail("no network"))
    monkeypatch.setattr(search, "file_sha", lambda p: "changed" if p == search.SOURCE_PATH else real(p))
    with pytest.raises(RuntimeError, match="engine changed"):
        driver.run(source, tmp_path / "out", fetch=lambda *_: pytest.fail("no network"))


def test_driver_change_during_fetch_preserves_evidence_but_refuses_completion(tmp_path, monkeypatch):
    source = source_cache(tmp_path)
    changed = [False]
    real = search.file_sha
    monkeypatch.setattr(search, "file_sha", lambda p: "changed" if changed[0] and p == driver.DRIVER_PATH else real(p))
    def fetch(database, params):
        changed[0] = True
        return response([item(99)], 2, None)
    with pytest.raises(RuntimeError, match="source changed during"):
        driver.run(source, tmp_path / "out", fetch=fetch, clock=lambda: START, delay=0)
    result = json.loads((tmp_path / "out/search_readout.json").read_text(encoding="utf-8"))
    assert result["pipeline_status"] == "SOURCE_CHANGED_DURING_RUN" and not result["database_search_complete"]


def test_same_directory_active_source_and_changed_spec_refused(tmp_path):
    source = source_cache(tmp_path, terminal=True)
    with pytest.raises(ValueError, match="separate"):
        driver.run(source, source)
    (source / ".search.lock").write_text("owner", encoding="utf-8")
    with pytest.raises(ValueError, match="source cache is locked"):
        driver.run(source, tmp_path / "out")
    (source / ".search.lock").unlink()
    driver.run(source, tmp_path / "out", fetch=lambda *_: pytest.fail("terminal cached streams"))
    path = tmp_path / "out/search_spec.json"
    spec = json.loads(path.read_text(encoding="utf-8"))
    spec["driver_sha256"] = "changed"
    search.write_json(path, spec)
    with pytest.raises(ValueError, match="specification changed"):
        driver.run(source, tmp_path / "out")


def test_continuation_source_is_rejected_without_losing_its_active_cooldown(tmp_path):
    source = source_cache(tmp_path)
    prior = tmp_path / "prior"
    driver.run(source, prior, fetch=lambda *_: (_ for _ in ()).throw(error()), clock=lambda: START, delay=0)
    before = (prior / "provider_cooldowns/openalex.json").read_bytes()
    with pytest.raises(ValueError, match="not a continuation output"):
        driver.run(prior, tmp_path / "next", fetch=lambda *_: pytest.fail("must not evade cooldown"), clock=lambda: START)
    assert (prior / "provider_cooldowns/openalex.json").read_bytes() == before
    resumed = driver.run(source, prior, fetch=lambda *_: pytest.fail("existing output retains cooldown"), clock=lambda: START)
    assert resumed["operation_status"] == "DEFERRED_API_BUDGET"


@pytest.mark.parametrize("orphan_kind", ["raw", "receipt"])
def test_source_orphan_page_or_receipt_refuses_migration_before_network(tmp_path, orphan_kind):
    source = source_cache(tmp_path)
    directory = source / "raw/openalex/q01"
    if orphan_kind == "raw":
        orphan = directory / "page_000002.json"
        orphan.write_bytes(response([item(9)], 2, None)[0])
    else:
        orphan = directory / "page_000002.receipt.json"
        search.write_json(orphan, dict(raw_sha256="missing"))
    before = orphan.read_bytes()
    with pytest.raises(ValueError, match="orphan raw page or receipt"):
        driver.run(source, tmp_path / "out", fetch=lambda *_: pytest.fail("no re-request"), clock=lambda: START)
    assert orphan.read_bytes() == before
    assert not (tmp_path / "out/cache_reuse.json").exists()
