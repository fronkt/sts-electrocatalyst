"""Bounded additive retrieval for a banked P-LIT reconciliation plan.

CLI requires a separately banked launch-pins JSON and its trusted SHA-256.
No scheduler, quota override, inclusion decision, or global completion claim.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from s2.literature import reconcile_plan as plan
from s2.literature import search
from s2.literature import continue_search as quota

CODE_PATHS = {
    "runner_sha256": Path(__file__).resolve(),
    "planner_sha256": Path(plan.__file__).resolve(),
    "engine_sha256": search.SOURCE_PATH,
    "quota_sha256": quota.DRIVER_PATH,
}
LOADED_CODE_SHA256 = {key: search.file_sha(path) for key, path in CODE_PATHS.items()}
PIN_KEYS = set(CODE_PATHS) | {"plan_sha256", "old_inventory_sha256"}


def now_utc():
    return datetime.now(timezone.utc)


def stamp(clock):
    value = clock()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat()


def immutable(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"immutable artifact collision: {path}")
        return
    with path.open("xb") as handle:
        handle.write(raw)


def immutable_json(path, value):
    immutable(path, (json.dumps(value, indent=2, ensure_ascii=False,
                                allow_nan=False) + "\n").encode("utf-8"))


def check_pins(directory, expected):
    if set(expected) != PIN_KEYS or any(
            not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v)
            for v in expected.values()):
        raise ValueError("launch pins require exactly the six lowercase SHA-256 fields")
    actual = {key: search.file_sha(path) for key, path in CODE_PATHS.items()}
    if actual != LOADED_CODE_SHA256:
        raise RuntimeError("source changed since import")
    if (actual["engine_sha256"] != search.LOADED_SOURCE_SHA256
            or actual["engine_sha256"] != quota.EXPECTED_ENGINE_SHA256
            or actual["quota_sha256"] != quota.LOADED_DRIVER_SHA256):
        raise RuntimeError("engine or quota import boundary differs")
    actual.update(plan_sha256=search.file_sha(directory / "plan.json"),
                  old_inventory_sha256=search.file_sha(directory / "old_identity_inventory.json"))
    if actual != expected:
        raise ValueError("launch pin mismatch")
    return actual


def load_plan(directory, expected):
    check_pins(directory, expected)
    manifest = json.loads((directory / "plan.json").read_bytes())
    required = dict(schema="p-lit-reconciliation-plan-v1", state="PROSPECTIVE_NOT_RETRIEVED",
                    queries=list(plan.QUERIES), date_window=[plan.START, plan.END],
                    provider="openalex", endpoint=plan.BASE, page_size=plan.PAGE_SIZE,
                    sort=plan.SORT, source_sha256=expected["planner_sha256"])
    if any(manifest.get(key) != value for key, value in required.items()):
        raise ValueError("plan differs from the banked reconciliation contract")
    if (type(manifest.get("count_tolerance")) is not int or manifest["count_tolerance"] != 0
            or type(manifest.get("new_requests_made")) is not int or manifest["new_requests_made"] != 0
            or manifest.get("global_p_lit_complete") is not False):
        raise ValueError("plan changes tolerance or prospective state")
    parts = plan.initial_partitions()
    if manifest.get("partitions") != [
            dict(partition=p, initial_request=plan.request_params(p)) for p in parts]:
        raise ValueError("plan must contain all 64 unchanged calendar-year partitions")
    plan.validate_cover(parts)
    inventory = json.loads((directory / "old_identity_inventory.json").read_bytes())
    old = [occ for row in inventory["identity_union"] for occ in row["occurrences"]["old"]]
    old += [row["occurrence"] for row in inventory["unresolved_identity_occurrences"]
            if row["origin"] == "old"]
    for row in old:
        if type(row.get("query_index")) is not int or not 1 <= row["query_index"] <= 4:
            raise ValueError("old inventory has an unregistered query")
    if inventory != plan.reconcile_identities(old, []):
        raise ValueError("old inventory is not an intact old-only identity union")
    return manifest, old


def separate(a, b):
    return a != b and a not in b.parents and b not in a.parents


def check_provider_cache(directory):
    value = json.loads((directory / "search_spec.json").read_bytes())
    if (value.get("schema") not in ("p-lit-continuation-spec-v1", "p-lit-search-spec-v2")
            or value.get("queries") != list(plan.QUERIES)
            or value.get("date_window") != [plan.START, plan.END]
            or value.get("pipeline_sha256") != search.LOADED_SOURCE_SHA256
            or value.get("discovery_databases") != ["openalex"]):
        raise ValueError("provider cache is not the registered broad OpenAlex cache")


class SharedProvider:
    """Reuse unchanged quota policy; both collectors see the longest deferral.

    The caller holds the provider cache's normal .search.lock throughout.
    Only cooldown metadata/history is published back; raw broad pages and
    readouts are never modified.
    """
    def __init__(self, out, provider_cache, fetch, clock):
        self.local = quota.QuotaTransport(out, fetch, clock)
        self.shared = quota.QuotaTransport(provider_cache, fetch, clock)

    def sync(self):
        states = []
        for transport in (self.local, self.shared):
            if not transport.path.exists():
                continue
            raw = transport.path.read_bytes()
            value = json.loads(raw)
            if value.get("provider") != "openalex" or not isinstance(value.get("reason"), str):
                raise ValueError("malformed provider cooldown")
            quota.timestamp(value["next_allowed_utc"])
            immutable(transport.path.parent / "history" / (search.sha(raw) + ".json"), raw)
            value.setdefault("evidence_directory", str(transport.out.resolve()))
            states.append(value)
        if states:
            state = max(states, key=lambda x: quota.timestamp(x["next_allowed_utc"]))
            for transport in (self.local, self.shared):
                transport.persist(state)
        return self.local.current()

    def __call__(self, database, params):
        self.sync()
        try:
            return self.local(database, params)
        finally:
            # Preserve a new quota/retry boundary even when fetching raises.
            self.sync()


def partition_directory(out, part):
    return out / "raw/openalex" / part["partition_id"] / "attempt_000001"


def scan_tree(out):
    """Validate every existing prefix before the first new request."""
    reports, leaves = {}, []

    def visit(part):
        report = plan.validate_cached_partition(part, partition_directory(out, part))
        reports[part["partition_id"]] = report
        if report["proposed_child_partitions"]:
            for child in report["proposed_child_partitions"]:
                visit(child)
        else:
            leaves.append(report)
    for part in plan.initial_partitions():
        visit(part)
    root = out / "raw/openalex"
    if root.exists():
        for directory in root.iterdir():
            if (not directory.is_dir() or directory.name not in reports
                    or any(p.name != "attempt_000001" or not p.is_dir() for p in directory.iterdir())):
                raise ValueError("unregistered partition or attempt directory")
    plan.validate_cover([r["partition"] for r in leaves])
    return reports, leaves


def update_tree(out, reports, leaves, part):
    report = plan.validate_cached_partition(part, partition_directory(out, part))
    reports[part["partition_id"]] = report
    position = next(i for i, r in enumerate(leaves)
                    if r["partition"]["partition_id"] == part["partition_id"])
    children = report["proposed_child_partitions"]
    replacement = []
    for child in children:
        value = plan.validate_cached_partition(child, partition_directory(out, child))
        reports[child["partition_id"]] = value
        replacement.append(value)
    leaves[position:position + 1] = replacement or [report]


def record_failure(directory, params, page, error, clock):
    """Keep failure accounting without private URLs or exception messages."""
    directory.mkdir(parents=True, exist_ok=True)
    failure = dict(database="openalex", params=params, page=page, at=stamp(clock),
                   error_type=type(error).__name__)
    if isinstance(error, urllib.error.HTTPError):
        body = error.read()
        name = f"page_{page:06d}.{uuid.uuid4().hex}.error.txt"
        immutable(directory / name, body)
        failure.update(http_status=error.code, response_body_sha256=search.sha(body),
                       raw_path=name)
    with (directory / "failures.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(failure, allow_nan=False) + "\n")
    return failure


def save_response(directory, params, number, raw, headers, clock):
    """Same successful receipt fields as search.fetch_page, without retries.

    Commit bytes before semantic validation so a malformed HTTP-200 response
    remains inspectable. An interrupted raw/receipt pair is refused on resume.
    """
    if not isinstance(raw, bytes) or not isinstance(headers, dict):
        raise ValueError("transport must return raw bytes and a header dictionary")
    raw_path = directory / f"page_{number:06d}.json"
    receipt_path = directory / f"page_{number:06d}.receipt.json"
    if raw_path.exists() or receipt_path.exists():
        raise ValueError("refusing to replace an existing response")
    receipt = dict(database="openalex", params=params,
                   url=plan.BASE + "?" + urllib.parse.urlencode(params),
                   retrieved_utc=stamp(clock), raw_sha256=search.sha(raw), bytes=len(raw),
                   response_headers={k.lower(): v for k, v in headers.items()
                                     if k.lower() in quota.SAFE_HEADERS},
                   successful_attempt=1, previous_failures=[])
    immutable(raw_path, raw)
    immutable_json(receipt_path, receipt)


def finish(out, pass_id, reports, leaves, old, operation, requests, deferral, clock, pins, check_boundary):
    leaf_validation = plan.validate_reconciliation(leaves, old)
    # Parent occurrences are evidence even after an unstable unit subdivides.
    all_new = [occ for report in reports.values() for occ in report["occurrences"]]
    union = plan.reconcile_identities(old, all_new)
    directory = out / "passes" / pass_id
    artifacts = {}
    for name, value in (("partition_reports.json", list(reports.values())),
                        ("leaf_validation.json", leaf_validation),
                        ("identity_reconciliation.json", union)):
        path = directory / name
        immutable_json(path, value)
        artifacts[name] = dict(path=path.relative_to(out).as_posix(), sha256=search.file_sha(path))
    result = dict(schema="p-lit-reconciliation-readout-v1", pass_id=pass_id,
                  updated_utc=stamp(clock), operation_status=operation,
                  requests_this_pass=requests, deferral=deferral,
                  leaf_status=leaf_validation["status"], leaf_partitions=len(leaves),
                  validated_leaves=sum(r["status"] == "VALIDATED_OBSERVED_PARTITION" for r in leaves),
                  partition_reports=len(reports),
                  old_occurrences=len(old), new_occurrences_including_unstable_parents=len(all_new),
                  identity_counts=union["counts"], artifacts=artifacts, pins=pins,
                  global_p_lit_complete=False, database_search_complete=False,
                  inclusion_list_frozen=False, limitation=plan.LIMITATION)
    check_boundary()
    immutable_json(directory / "readout.json", result)
    search.write_json(out / "summary.json", result)
    search.write_json(out / "last_pass.json", result)
    return result


def run(plan_dir, out, provider_cache, *, expected_pins, page_budget=100,
        fetch=search.get_response, clock=now_utc, sleep=time.sleep, delay=1.0):
    plan_dir, out, provider_cache = map(lambda p: Path(p).resolve(), (plan_dir, out, provider_cache))
    if (not separate(out, plan_dir) or not separate(out, provider_cache)
            or not separate(plan_dir, provider_cache)):
        raise ValueError("plan, output and provider cache must be separate, non-nested directories")
    if type(page_budget) is not int or page_budget < 0:
        raise ValueError("page budget must be a nonnegative integer")
    if isinstance(delay, bool) or not math.isfinite(delay) or not 0 <= delay <= 60:
        raise ValueError("inter-request delay must be finite and between zero and 60 seconds")
    stamp(clock)
    # The two independent normal engine locks also exclude the broad collector.
    with search.output_lock(out), search.output_lock(provider_cache):
        manifest, old = load_plan(plan_dir, expected_pins)
        historical = Path(manifest["preserved_source"]["directory"]).resolve()
        if not separate(out, historical):
            raise ValueError("output overlaps the historical source")
        check_provider_cache(provider_cache)
        spec = dict(schema="p-lit-reconciliation-run-v1", pins=expected_pins,
                    plan_directory=str(plan_dir), provider_cache=str(provider_cache),
                    historical_source=manifest["preserved_source"],
                    historical_export_pins_are_not_current_live_cache_requirements=True,
                    refinement=manifest["refinement"], limitation=plan.LIMITATION)
        immutable_json(out / "run_spec.json", spec)
        pass_id, requests = uuid.uuid4().hex, 0
        active = None
        try:
            reports, leaves = scan_tree(out)

            def counted_fetch(database, params):
                nonlocal requests
                # Pin checking is immediately before each actual network request.
                check_pins(plan_dir, expected_pins)
                requests += 1
                return fetch(database, params)

            provider = SharedProvider(out, provider_cache, counted_fetch, clock)
            provider.sync()
            quota.seed_cooldown(provider_cache, provider.local)
            deferral = provider.sync()
            operation = "RETRIEVAL_PASS_ENDED"
            while True:
                pending = next((r for r in leaves if r["next_action"] == "RETRIEVE_OR_RESUME"), None)
                if pending is None:
                    break
                if requests >= page_budget:
                    operation = "PAGE_BUDGET_REACHED"
                    break
                deferral = provider.sync()
                if deferral:
                    operation = deferral["reason"]
                    break
                part = pending["partition"]
                directory = partition_directory(out, part)
                number = len(pending["page_pins"]) + 1
                cursor = "*"
                if pending["page_pins"]:
                    cursor = json.loads(Path(pending["page_pins"][-1]["raw_path"]).read_bytes())["meta"]["next_cursor"]
                params = plan.request_params(part, cursor)
                active = dict(partition_id=part["partition_id"], page=number)
                if requests and delay:
                    sleep(delay)
                try:
                    raw, headers = provider("openalex", params)
                except quota.DeferredRequest as error:
                    record_failure(directory, params, number, error, clock)
                    deferral = provider.sync()
                    operation = deferral["reason"] if deferral else "DEFERRED_REQUEST"
                    # Include this pass's failure artifacts in the final report.
                    reports[part["partition_id"]] = plan.validate_cached_partition(part, directory)
                    leaves[leaves.index(pending)] = reports[part["partition_id"]]
                    break
                except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as error:
                    record_failure(directory, params, number, error, clock)
                    operation = "REQUEST_FAILED"
                    reports[part["partition_id"]] = plan.validate_cached_partition(part, directory)
                    leaves[leaves.index(pending)] = reports[part["partition_id"]]
                    break
                save_response(directory, params, number, raw, headers, clock)
                update_tree(out, reports, leaves, part)
            check_pins(plan_dir, expected_pins)
            # Revalidate all bytes and tree leaves once before publishing the result.
            reports, leaves = scan_tree(out)
            return finish(out, pass_id, reports, leaves, old, operation, requests,
                          deferral, clock, expected_pins,
                          lambda: check_pins(plan_dir, expected_pins))
        except Exception as error:
            failure = dict(schema="p-lit-reconciliation-pass-error-v1", pass_id=pass_id,
                           operation_status="INTEGRITY_OR_MALFORMED_RESPONSE_ERROR",
                           error_type=type(error).__name__, active_request=active,
                           requests_this_pass=requests, updated_utc=stamp(clock),
                           global_p_lit_complete=False, inclusion_list_frozen=False)
            immutable_json(out / "passes" / pass_id / "error.json", failure)
            search.write_json(out / "last_pass.json", failure)
            raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--provider-cache", type=Path, required=True)
    parser.add_argument("--pins", type=Path, required=True)
    parser.add_argument("--pins-sha256", required=True)
    parser.add_argument("--page-budget", type=int, default=100)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args(argv)
    raw = args.pins.read_bytes()
    if search.sha(raw) != args.pins_sha256:
        raise ValueError("launch-pins file differs from the externally supplied hash")
    result = run(args.plan, args.out, args.provider_cache, expected_pins=json.loads(raw),
                 page_budget=args.page_budget, delay=args.delay)
    print(json.dumps({k: result[k] for k in ("operation_status", "requests_this_pass",
                     "leaf_status", "validated_leaves", "leaf_partitions", "global_p_lit_complete")}))
    return 0 if result["leaf_status"] == "OBSERVED_PARTITION_ENUMERATION_CONSISTENT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
