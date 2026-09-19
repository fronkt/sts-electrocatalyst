"""Run the pinned quota-aware continuation driver until the metadata search completes.

This wrapper makes no network request itself.  It invokes
``continue_search.py`` (which defers with zero requests before its recorded
provider boundary), reads the driver's own readout and cooldown records, and
sleeps until the recorded ``next_allowed_utc`` before invoking it again.  It
stops when ``database_search_complete`` is true, when the deadline passes, when
the pass budget is spent, or when the driver fails without recording a
boundary.  Search, deduplication, inclusion and scoring rules are untouched.

Usage:
    python src/s2/literature/continue_until_complete.py \
        --source results/s2_2026-09-18/literature_openalex \
        --out results/s2_2026-09-19/literature_openalex_continuation \
        --state results/s2_2026-09-19/literature_continuation_passes.json
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

DRIVER = Path(__file__).with_name("continue_search.py")


def now() -> datetime:
    return datetime.now(timezone.utc)


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--deadline-utc", default="2026-09-25T00:00:00+00:00")
    ap.add_argument("--max-passes", type=int, default=10)
    ap.add_argument("--idle-retry-seconds", type=float, default=900.0)
    args = ap.parse_args(argv)
    out, state_path = Path(args.out), Path(args.state)
    deadline = parse_ts(args.deadline_utc)
    state = read_json(state_path) or {"passes": [], "driver": str(DRIVER).replace("\\", "/")}
    state.update(source=args.source, out=args.out, deadline_utc=deadline.isoformat(), pid=__import__("os").getpid())

    def save(status: str, note: str = "") -> None:
        state.update(status=status, note=note, updated_utc=now().isoformat())
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")

    save("RUNNING")
    while len(state["passes"]) < args.max_passes:
        if now() >= deadline:
            save("STOPPED_DEADLINE")
            return 3
        cooldown = read_json(out / "provider_cooldowns" / "openalex.json")
        if cooldown and parse_ts(cooldown["next_allowed_utc"]) > now():
            wake = min(parse_ts(cooldown["next_allowed_utc"]) + timedelta(seconds=30), deadline)
            save("WAITING_FOR_BOUNDARY", "sleeping until " + wake.isoformat())
            while now() < wake:
                time.sleep(min(300.0, max(1.0, (wake - now()).total_seconds())))
            continue
        started = now()
        proc = subprocess.run([sys.executable, str(DRIVER), "--source", args.source, "--out", args.out],
                              capture_output=True, text=True)
        readout = read_json(out / "search_readout.json") or {}
        cooldown = read_json(out / "provider_cooldowns" / "openalex.json")
        record = {"started_utc": started.isoformat(), "finished_utc": now().isoformat(), "rc": proc.returncode,
                  "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:],
                  "database_search_complete": readout.get("database_search_complete"),
                  "streams": [{"q": s.get("query_index"), "pages": s.get("pages"), "records": s.get("returned_records"),
                               "status": s.get("status"), "termination": s.get("termination")} for s in readout.get("streams", [])],
                  "cooldown": cooldown}
        state["passes"].append(record)
        if readout.get("database_search_complete") is True:
            save("COMPLETE")
            return 0
        if cooldown and parse_ts(cooldown["next_allowed_utc"]) > now():
            save("DEFERRED", cooldown.get("reason", ""))
            continue
        if proc.returncode != 0:
            save("STOPPED_DRIVER_ERROR", "driver exited " + str(proc.returncode) + " without a future boundary")
            return 2
        save("INCOMPLETE_RETRY", "driver returned without completion or boundary; idle retry")
        time.sleep(args.idle_retry_seconds)
    save("STOPPED_PASS_BUDGET")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
