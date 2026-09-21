"""Run the banked P-LIT reconciliation runner pass by pass until it finishes.

This wrapper makes no network request itself.  It invokes
``reconcile_search.py`` with the banked plan, output, provider cache and launch
pins, reads the runner's own ``summary.json`` / ``last_pass.json`` and the
shared provider cooldown, and sleeps until the recorded ``next_allowed_utc``
before invoking it again.  It never removes a lock, never edits a plan or pin
and never changes a query.  It stops when the runner reports observed leaf
consistency (exit 0), when the runner records an integrity error, when a pass
makes no request and records no future boundary, when the deadline passes or
when the pass budget is spent.

Usage:
    python src/s2/literature/reconcile_until_complete.py \
        --plan results/s2_2026-09-21/reconciliation_plan \
        --out results/s2_2026-09-21/literature_reconciliation \
        --provider-cache results/s2_2026-09-19/literature_openalex_continuation \
        --pins results/s2_2026-09-21/reconciliation_launch_pins_v2.json \
        --pins-sha256 d3d361e0268edc1e56499222695c99ff9d7ab60b736851d89903946c58015cec \
        --state results/s2_2026-09-21/reconciliation_continuation_passes.json
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

DRIVER = Path(__file__).with_name("reconcile_search.py")
COOLDOWN = Path("provider_cooldowns") / "openalex.json"
LOCK = ".search.lock"


def now() -> datetime:
    return datetime.now(timezone.utc)


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def boundary(out: Path, provider_cache: Path):
    """Latest recorded next_allowed_utc across the runner's own and the shared cooldown."""
    latest = None
    for directory in (out, provider_cache):
        record = read_json(directory / COOLDOWN)
        if not record or "next_allowed_utc" not in record:
            continue
        when = parse_ts(record["next_allowed_utc"])
        if latest is None or when > latest[0]:
            latest = (when, record)
    return latest


def decide(rc: int, last_pass, summary, boundary_at, at: datetime) -> str:
    """Classify a finished runner pass.  Pure function so it can be tested offline."""
    if last_pass and last_pass.get("schema") == "p-lit-reconciliation-pass-error-v1":
        return "STOPPED_INTEGRITY_ERROR"
    if rc == 0:
        return "COMPLETE"
    if boundary_at is not None and boundary_at > at:
        return "DEFERRED"
    status = (summary or {}).get("operation_status")
    requests = (summary or {}).get("requests_this_pass", 0)
    if status == "PAGE_BUDGET_REACHED":
        return "CONTINUE"
    if requests == 0:
        return "STOPPED_NO_FURTHER_REQUESTS"
    if status == "REQUEST_FAILED":
        return "RETRY_AFTER_IDLE"
    return "RETRY_AFTER_IDLE"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--provider-cache", required=True)
    ap.add_argument("--pins", required=True)
    ap.add_argument("--pins-sha256", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--page-budget", type=int, default=100)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--deadline-utc", default="2026-09-28T00:00:00+00:00")
    ap.add_argument("--max-passes", type=int, default=40)
    ap.add_argument("--idle-retry-seconds", type=float, default=900.0)
    ap.add_argument("--lock-wait-seconds", type=float, default=600.0)
    args = ap.parse_args(argv)
    out, provider_cache, state_path = Path(args.out), Path(args.provider_cache), Path(args.state)
    deadline = parse_ts(args.deadline_utc)
    state = read_json(state_path) or {"passes": [], "driver": str(DRIVER).replace("\\", "/")}
    state.update(plan=args.plan, out=args.out, provider_cache=args.provider_cache, pins=args.pins,
                 pins_sha256=args.pins_sha256, deadline_utc=deadline.isoformat(), pid=os.getpid())

    def save(status: str, note: str = "") -> None:
        state.update(status=status, note=note, updated_utc=now().isoformat())
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")

    save("RUNNING")
    idle_retries = 0
    while len(state["passes"]) < args.max_passes:
        if now() >= deadline:
            save("STOPPED_DEADLINE")
            return 3
        latest = boundary(out, provider_cache)
        if latest and latest[0] > now():
            wake = min(latest[0] + timedelta(seconds=30), deadline)
            save("WAITING_FOR_BOUNDARY", "sleeping until " + wake.isoformat())
            while now() < wake:
                time.sleep(min(300.0, max(1.0, (wake - now()).total_seconds())))
            continue
        if (out / LOCK).exists() or (provider_cache / LOCK).exists():
            save("WAITING_FOR_OTHER_COLLECTOR", "a .search.lock is present; never removed here")
            time.sleep(args.lock_wait_seconds)
            continue
        if hashlib.sha256(Path(args.pins).read_bytes()).hexdigest() != args.pins_sha256:
            save("STOPPED_PIN_MISMATCH", "launch-pins file differs from the supplied hash")
            return 5
        started = now()
        proc = subprocess.run([sys.executable, str(DRIVER), "--plan", args.plan, "--out", args.out,
                               "--provider-cache", args.provider_cache, "--pins", args.pins,
                               "--pins-sha256", args.pins_sha256, "--page-budget", str(args.page_budget),
                               "--delay", str(args.delay)], capture_output=True, text=True)
        summary = read_json(out / "summary.json")
        last_pass = read_json(out / "last_pass.json")
        latest = boundary(out, provider_cache)
        verdict = decide(proc.returncode, last_pass, summary, latest[0] if latest else None, now())
        record = {"started_utc": started.isoformat(), "finished_utc": now().isoformat(), "rc": proc.returncode,
                  "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:], "verdict": verdict,
                  "summary": {k: (summary or {}).get(k) for k in ("pass_id", "operation_status", "requests_this_pass",
                                                                  "leaf_status", "validated_leaves", "leaf_partitions")},
                  "last_pass_id": (last_pass or {}).get("pass_id"),
                  "boundary": latest[1] if latest else None}
        state["passes"].append(record)
        if verdict == "COMPLETE":
            save("COMPLETE")
            return 0
        if verdict == "STOPPED_INTEGRITY_ERROR":
            save(verdict, "runner recorded an integrity error; inspect last_pass.json before any retry")
            return 2
        if verdict == "STOPPED_NO_FURTHER_REQUESTS":
            save(verdict, "runner made no request and recorded no boundary; enumeration needs inspection")
            return 6
        if verdict == "DEFERRED":
            idle_retries = 0
            save("DEFERRED", (latest[1] or {}).get("reason", "") if latest else "")
            continue
        if verdict == "CONTINUE":
            idle_retries = 0
            save("CONTINUE", "page budget reached; next pass follows")
            continue
        idle_retries += 1
        if idle_retries >= 3:
            save("STOPPED_REPEATED_FAILURE", "three consecutive passes failed without a boundary")
            return 7
        save("INCOMPLETE_RETRY", "runner returned without completion or boundary; idle retry")
        time.sleep(args.idle_retry_seconds)
    save("STOPPED_PASS_BUDGET")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
