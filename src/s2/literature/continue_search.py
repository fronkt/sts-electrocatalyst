"""Quota-aware continuation using the unchanged P-LIT pagination engine.

Use a separate output directory and the quiescent amended cache as --source.
This driver does not change search, deduplication, inclusion or scoring rules.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import io
import json
import math
from pathlib import Path
import sys
import time
import urllib.error
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from s2.literature import search

DRIVER_PATH = Path(__file__).resolve()
LOADED_DRIVER_SHA256 = search.file_sha(DRIVER_PATH)
EXPECTED_ENGINE_SHA256 = "824e5218744e4af1182a21db4bcb43c3dd9e0ae7885ed7581bfc3dee4bbdef19"
SAFE_HEADERS = {"date", "content-type", "retry-after", "x-rate-limit-limit", "x-rate-limit-interval"}


def now_utc():
    return datetime.now(timezone.utc)


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("cooldown timestamps must carry a timezone")
    return result.astimezone(timezone.utc)


def seconds(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) and result >= 0 else None
    except (ValueError, TypeError):
        return None


def retry_boundary(status, body, headers, received):
    """Return an operational deferral, never an eligibility/completeness decision."""
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    normalized = {k.lower(): v for k, v in headers.items()}
    boundaries = []
    header = normalized.get("retry-after")
    delay = seconds(header)
    if delay is not None:
        boundaries.append(received + timedelta(seconds=delay))
    elif header:
        try:
            boundary = parsedate_to_datetime(header)
            if boundary.tzinfo is not None:
                boundaries.append(boundary.astimezone(timezone.utc))
        except (ValueError, TypeError, OverflowError):
            pass
    delay = seconds(data.get("retryAfter"))
    if delay is not None:
        boundaries.append(received + timedelta(seconds=delay))
    exhausted = (status == 429 and data.get("dailyRemainingUsd") == 0
                 and not isinstance(data.get("dailyRemainingUsd"), bool)
                 and data.get("prepaidRemainingUsd") == 0
                 and not isinstance(data.get("prepaidRemainingUsd"), bool))
    if exhausted:
        # The observed provider promises midnight UTC. Use it only with that statement.
        if "midnight utc" in str(data.get("message", "")).lower():
            boundaries.append(received.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1))
        reason = "DEFERRED_API_BUDGET"
    elif status == 429:
        reason = "DEFERRED_RATE_LIMIT"
    elif 500 <= status < 600 and any(b > received for b in boundaries):
        reason = "DEFERRED_PROVIDER_RETRY"
    else:
        return None
    if not any(b > received for b in boundaries):
        boundaries.append(received + timedelta(seconds=60))
    return dict(reason=reason, next_allowed_utc=max(boundaries).isoformat())


class DeferredRequest(RuntimeError):
    pass


class CacheOnly:
    def __init__(self):
        self.missing = False

    def __call__(self, database, params):
        self.missing = True
        raise DeferredRequest("uncached page requires a later network pass")


class QuotaTransport:
    """A single durable OpenAlex cooldown covers every query in this run."""
    def __init__(self, out, fetch=search.get_response, clock=now_utc):
        self.out, self.fetch, self.clock = Path(out), fetch, clock
        self.path = self.out / "provider_cooldowns/openalex.json"
        self.deferred = None

    def current(self):
        if not self.path.exists():
            return None
        state = json.loads(self.path.read_text(encoding="utf-8"))
        if state.get("provider") != "openalex":
            raise ValueError("cooldown provider mismatch")
        if timestamp(state["next_allowed_utc"]) > self.clock():
            return state
        return None

    def persist(self, state):
        if self.path.exists():
            previous = json.loads(self.path.read_text(encoding="utf-8"))
            if timestamp(previous["next_allowed_utc"]) > timestamp(state["next_allowed_utc"]):
                return previous
        search.write_json(self.path, state)
        return state

    def __call__(self, database, params):
        if database != "openalex":
            raise ValueError("continuation transport is scoped to OpenAlex discovery")
        state = self.current()
        if state:
            self.deferred = state
            raise DeferredRequest(state["reason"] + "; see provider_cooldowns/openalex.json")
        try:
            return self.fetch(database, params)
        except urllib.error.HTTPError as error:
            received, body = self.clock(), error.read()
            headers = {k.lower(): v for k, v in (error.headers or {}).items() if k.lower() in SAFE_HEADERS}
            boundary = retry_boundary(error.code, body, headers, received)
            directory = self.out / "transport_failures"
            directory.mkdir(parents=True, exist_ok=True)
            name = uuid.uuid4().hex
            raw_path = directory / (name + ".body")
            raw_path.write_bytes(body)
            receipt = dict(provider=database, params=params, at=received.isoformat(), http_status=error.code,
                           raw_path=raw_path.relative_to(self.out).as_posix(), raw_sha256=search.sha(body),
                           response_headers=headers, deferral=boundary)
            search.write_json(directory / (name + ".receipt.json"), receipt)
            if boundary:
                self.deferred = self.persist(dict(provider=database, observed_utc=received.isoformat(),
                                                  evidence=receipt, **boundary))
                raise DeferredRequest(boundary["reason"] + "; see provider_cooldowns/openalex.json") from None
            # The engine keeps its existing bounded retries for ordinary failures.
            # Never propagate the private request URL or a consumed error stream.
            raise urllib.error.HTTPError(search.BASES[database], error.code, "HTTP request failed",
                                         headers, io.BytesIO(body)) from None


def seed_cooldown(source, transport):
    """Recover the existing deferral from hash-verified raw failure evidence."""
    for directory in sorted((source / "raw/openalex").glob("q*")):
        ledger = directory / "failures.jsonl"
        if not ledger.exists():
            continue
        bodies = {}
        for path in directory.glob("*.error.txt"):
            bodies.setdefault(search.file_sha(path), path)
        for line in ledger.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("http_status") != 429:
                continue
            raw = bodies.get(row.get("response_body_sha256"))
            if raw is None:
                raise ValueError("source quota failure has no hash-matched raw body")
            received = timestamp(row["at"])
            boundary = retry_boundary(429, raw.read_bytes(), {}, received)
            if boundary and timestamp(boundary["next_allowed_utc"]) > transport.clock():
                transport.persist(dict(provider="openalex", observed_utc=row["at"], **boundary,
                                       evidence=dict(source_ledger=str(ledger.resolve()),
                                                     raw_path=str(raw.resolve()), raw_sha256=search.file_sha(raw))))


def source_spec(source):
    if (source / ".search.lock").exists():
        raise ValueError("source cache is locked; verify its worker is stopped before continuation")
    value = json.loads((source / "search_spec.json").read_text(encoding="utf-8"))
    if value.get("schema") != "p-lit-search-spec-v2":
        raise ValueError("source must be the amended engine cache, not a continuation output; resume that output in place")
    expected = dict(queries=list(search.QUERIES), date_window=[search.START, search.END],
                    page_sizes=search.PAGE_SIZE, pipeline_sha256=EXPECTED_ENGINE_SHA256,
                    discovery_databases=["openalex"], decision_sha256=search.file_sha(search.DECISION),
                    amendment_sha256=search.file_sha(search.AMENDMENT))
    if any(value.get(k) != v for k, v in expected.items()):
        raise ValueError("source specification differs from the pinned amended protocol")
    for path in (source / "raw/openalex").glob("q*/page_*.json"):
        if path.name.endswith(".receipt.json"):
            counterpart = path.with_name(path.name.removesuffix(".receipt.json") + ".json")
        else:
            counterpart = path.with_name(path.stem + ".receipt.json")
        if not counterpart.is_file():
            raise ValueError("source cache has an orphan raw page or receipt; preserve and inspect before migration")
    return value


def run(source: Path, out: Path, fetch=search.get_response, clock=now_utc, delay=1.0, sleep=time.sleep):
    source, out = Path(source).resolve(), Path(out).resolve()
    if source == out or source in out.parents or out in source.parents:
        raise ValueError("continuation requires a separate, non-nested output directory")
    if not math.isfinite(delay) or delay < 0:
        raise ValueError("delay must be finite and nonnegative")
    with search.output_lock(out):
        engine_hash, driver_hash = search.file_sha(search.SOURCE_PATH), search.file_sha(DRIVER_PATH)
        if engine_hash != EXPECTED_ENGINE_SHA256 or engine_hash != search.LOADED_SOURCE_SHA256:
            raise RuntimeError("pinned pagination engine changed")
        if driver_hash != LOADED_DRIVER_SHA256:
            raise RuntimeError("continuation driver changed since import")
        original = source_spec(source)
        spec = dict(original, schema="p-lit-continuation-spec-v1", driver_sha256=driver_hash,
                    source_directory=str(source), source_spec_sha256=search.file_sha(source / "search_spec.json"),
                    quota_policy="provider-wide durable deferral; no paid-access or identity changes")
        path = out / "search_spec.json"
        if path.exists() and json.loads(path.read_text(encoding="utf-8")) != spec:
            raise ValueError("continuation specification changed; use a separate directory")
        if not path.exists():
            search.write_json(path, spec)
        if not (out / "cache_reuse.json").exists():
            search.reuse_openalex_cache(source, out)
        transport = QuotaTransport(out, fetch, clock)
        seed_cooldown(source, transport)
        db = search.connect_index(out / "candidate_index.sqlite")
        states = []
        try:
            # Verify/index every imported stream without probing the exhausted API.
            for index in range(1, 5):
                offline = CacheOnly()
                state = search.walk("openalex", index, out, db, delay=0, fetch=offline, sleep=lambda _: None)
                if offline.missing:
                    state["termination"] = "CACHED_PREFIX_VERIFIED"
                    state.pop("error", None)
                    state.pop("error_type", None)
                    search.write_json(out / f"raw/openalex/q{index:02d}/status.json", state)
                elif state.get("termination") == "REQUEST_OR_CACHE_FAILURE":
                    raise ValueError(f"query {index} cache validation failed; see its status.json")
                states.append(state)
            deferred = transport.current()
            if not deferred:
                for index in range(1, 5):
                    if states[index - 1].get("termination") != "CACHED_PREFIX_VERIFIED":
                        continue
                    states[index - 1] = search.walk("openalex", index, out, db, delay=delay,
                                                    fetch=transport, sleep=sleep)
                    if transport.deferred:
                        deferred = transport.deferred
                        break
            candidate_index = search.export_candidates(db, out)
            end_engine, end_driver = search.file_sha(search.SOURCE_PATH), search.file_sha(DRIVER_PATH)
            unchanged = (engine_hash, driver_hash) == (end_engine, end_driver)
            result = dict(schema="p-lit-continuation-readout-v1", updated_utc=clock().isoformat(), streams=states,
                          discovery_databases=["openalex"], amended_protocol=True,
                          database_search_complete=unchanged and all(s["status"] == "COMPLETE_API_ENUMERATION" for s in states),
                          candidate_index=candidate_index, pipeline_sha256=engine_hash, pipeline_end_sha256=end_engine,
                          driver_sha256=driver_hash, driver_end_sha256=end_driver,
                          pipeline_status="SOURCE_UNCHANGED" if unchanged else "SOURCE_CHANGED_DURING_RUN",
                          operation_status=deferred["reason"] if deferred else "RETRIEVAL_PASS_ENDED",
                          deferral=deferred, inclusion_list_frozen=False, methods_coded=0,
                          limitations=["API enumeration is not proof of complete literature coverage or article eligibility.",
                                       "Count drift, duplicate or unresolved provider identities remain unresolved under the original engine.",
                                       "Complementary discovery, inclusion, Crossref DOI validation and method coding remain separate obligations."])
            search.write_json(out / "search_readout.json", result)
            if not unchanged:
                raise RuntimeError("source changed during continuation; completion refused")
            return result
        finally:
            db.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args(argv)
    result = run(args.source, args.out, delay=args.delay)
    print(json.dumps({key: result[key] for key in ("operation_status", "database_search_complete", "candidate_index", "deferral")}))
    return 0 if result["database_search_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
