from datetime import datetime, timedelta, timezone
import json

from src.s2.literature import reconcile_until_complete as loop

NOW = datetime(2026, 9, 22, 0, 5, tzinfo=timezone.utc)
ERROR = {"schema": "p-lit-reconciliation-pass-error-v1", "pass_id": "x"}


def summary(status, requests):
    return {"operation_status": status, "requests_this_pass": requests, "leaf_status": "UNRESOLVED"}


def test_integrity_error_wins_over_everything():
    assert loop.decide(2, ERROR, summary("PAGE_BUDGET_REACHED", 100), NOW + timedelta(days=1), NOW) == "STOPPED_INTEGRITY_ERROR"
    assert loop.decide(1, ERROR, None, None, NOW) == "STOPPED_INTEGRITY_ERROR"


def test_exit_zero_is_complete():
    assert loop.decide(0, {"schema": "p-lit-reconciliation-readout-v1"}, summary("RETRIEVAL_PASS_ENDED", 3), None, NOW) == "COMPLETE"


def test_future_boundary_defers_and_past_boundary_does_not():
    assert loop.decide(2, None, summary("DEFERRED_API_BUDGET", 19), NOW + timedelta(hours=23), NOW) == "DEFERRED"
    assert loop.decide(2, None, summary("PAGE_BUDGET_REACHED", 100), NOW - timedelta(seconds=1), NOW) == "CONTINUE"


def test_no_request_without_boundary_stops():
    assert loop.decide(2, None, summary("RETRIEVAL_PASS_ENDED", 0), None, NOW) == "STOPPED_NO_FURTHER_REQUESTS"


def test_request_failure_retries_after_idle():
    assert loop.decide(2, None, summary("REQUEST_FAILED", 4), None, NOW) == "RETRY_AFTER_IDLE"


def test_boundary_takes_the_latest_of_both_cooldowns(tmp_path):
    out, cache = tmp_path / "out", tmp_path / "cache"
    for directory, when in ((out, "2026-09-22T00:00:00+00:00"), (cache, "2026-09-23T00:00:00+00:00")):
        (directory / "provider_cooldowns").mkdir(parents=True)
        (directory / "provider_cooldowns" / "openalex.json").write_text(
            json.dumps({"provider": "openalex", "reason": "DEFERRED_API_BUDGET", "next_allowed_utc": when}), encoding="utf-8")
    when, record = loop.boundary(out, cache)
    assert when == datetime(2026, 9, 23, tzinfo=timezone.utc)
    assert record["next_allowed_utc"] == "2026-09-23T00:00:00+00:00"
    assert loop.boundary(tmp_path / "none", tmp_path / "none2") is None
