# P-LIT bounded reconciliation retrieval — 2026-09-21

The additive runner implements the [prospective reconciliation contract](s2-literature-reconciliation-plan-2026-09-20.md) without editing the pinned broad-window engine or continuation worker. It retrieves the four unchanged literal queries over the complete registered window in date partitions. It does not decide eligibility, code method reporting, freeze inclusion, or claim global P-LIT completion.

## Plan and launch boundary

The intended input is the separately prepared [September 21 plan](../../results/s2_2026-09-21/reconciliation_plan/plan.json) and its old identity inventory. Preparation followed exhaustion of all four broad-window cursors; all four broad streams still have observed count drift. The historical source export has 31,392 candidate keys and 38,127 occurrences. Candidate keys are not interchangeable with unique provider work IDs.

The runner requires a separately banked launch-pins JSON containing exactly six lowercase SHA-256 values:

- runner_sha256: src/s2/literature/reconcile_search.py
- planner_sha256: src/s2/literature/reconcile_plan.py
- engine_sha256: src/s2/literature/search.py
- quota_sha256: src/s2/literature/continue_search.py
- plan_sha256: the selected plan.json
- old_inventory_sha256: its old_identity_inventory.json

The SHA-256 of this launch-pins file must also be supplied independently at launch. Preparing or hashing a file alone does not establish a pushed boundary: the source, plan, inventory, and launch manifest must be reviewed and banked before retrieval. Source hashes are checked against the imported modules, the existing engine pin, and the externally supplied manifest. The same pins are checked before each actual fetch and again after the final artifact export before publishing the accepted pass readout.

The plan's historical export pins describe its frozen old inventory. The runner deliberately does not require the mutable broad export to remain at that historical version forever. It neither silently refreshes that inventory nor treats it as the newest broad export. A new old-inventory boundary requires a new banked plan and a separate reconciliation output directory. The September 21 plan supplies the current frozen boundary for this run.

The command interface is:

    python src/s2/literature/reconcile_search.py --plan PLAN_DIRECTORY --out NEW_OR_MATCHING_RUN_DIRECTORY --provider-cache BROAD_CACHE --pins BANKED_LAUNCH_PINS_JSON --pins-sha256 TRUSTED_MANIFEST_SHA256 --page-budget 100

All directories must be separate rather than nested. The default inter-request delay is one second; --delay may configure this operational spacing. --page-budget limits actual transport attempts, including failed requests. A zero budget is an offline validation/export pass. The Python run() interface also accepts injected fetch, clock, and sleep functions for offline verification.

## Locking, provider limits, and failures

The runner holds both its own output .search.lock and the broad cache's normal .search.lock for the entire pass. An existing lock stops it before requesting data; it never removes another collector's lock. This prevents the broad worker and reconciliation runner from consuming the same provider allowance concurrently.

The unchanged QuotaTransport captures response bodies, safe headers, and failure receipts. The runner shares the latest provider cooldown with the broad cache and archives exact prior cooldown bytes in hash-named history files before advancement. The shared state records the directory containing its original transport evidence. Shared state is checked again immediately before each actual request, including after an inter-request delay. No new key, paid override, identity rotation, or quota bypass is introduced.

A quota or provider retry boundary stops the finite pass and publishes the boundary to both caches. Other HTTP/network failures also stop the pass after preserving the failure evidence. There is no sleeping supervisor or automatic retry loop in this module. A later separately invoked pass resumes the same intact successful prefix when the provider permits it. Operational delays and page budgets do not alter query content or scientific thresholds.

Only cooldown metadata and its history are published to the broad cache. Broad raw pages, receipts, status files, candidate exports, and readouts are untouched.

## Cache and refinement behavior

Each partition uses raw/openalex/PARTITION_ID/attempt_000001/. Successful raw bytes and the exact existing receipt schema are retained under consecutive page numbers. Receipt identity includes the exact query, date filter, sort, page size, cursor, retrieval time, response byte count, and SHA-256. An intact prefix resumes at its recorded next cursor; previously completed pages are never fetched again or replaced.

Every existing partition is validated before the first request. Hash, receipt, cursor-chain, malformed-record, missing-pair, and unexpected-attempt errors are hard stops. A malformed HTTP-200 response is retained with its receipt, then rejected; later invocations refuse that invalid prefix. Transport failure artifacts coexist with successful pages and remain part of the partition report.

Only a validator finding of observable enumeration instability triggers subdivision. An unstable year creates every intersecting month; an unstable month creates every day. Incomplete pagination without observed instability remains resumable. An unstable day stays unresolved. Parent attempts and their complete source occurrences remain preserved after subdivision. All final leaves must still cover the exact four full windows without gaps or overlaps.

Each pass exports two deliberately different views. leaf_validation.json checks the final complete date partition cover and same-query provider-ID uniqueness. identity_reconciliation.json preserves the old inventory plus every new occurrence from all attempts, including unstable parents. partition_reports.json retains the full refinement tree and failure evidence. The summary's partition_reports counts reports, including virtual unstarted partitions; it is not a count of requests or attempted partitions.

A provider ID repeated across leaves of one query leaves the overall enumeration unresolved even if each leaf's local count and cursor checks pass. If all leaves are locally complete, the runner makes no further automatic requests to repair that discrepancy. A subsequent pass reports the same unresolved evidence without endlessly re-fetching it.

## Readouts and limits

Pass artifacts and readouts are immutable under passes/PASS_ID/; mutable summary.json and last_pass.json identify the latest accepted readout or error. Integrity failures preserve an error receipt and raise. When a prior accepted summary exists, it may remain as historical state; last_pass.json identifies the newer failure and its pass ID. An export interrupted by a pin change is not accepted as a successful pass.

The strongest leaf status remains OBSERVED_PARTITION_ENUMERATION_CONSISTENT. This is a statement about preserved observations, not an immutable API snapshot or complete scientific coverage. Old-only IDs remain evidence, not exclusions. Every accepted summary keeps global_p_lit_complete=false, database_search_complete=false, and inclusion_list_frozen=false. Registered known-source coverage, backward references, identity/date reconciliation, primary-source eligibility, access resolution, and scientific coding remain separate work.

The CLI returns zero only for observed leaf consistency; incomplete, quota-deferred, day-unstable, or cross-leaf-duplicate enumeration returns two with its readout. Integrity failures raise and must be investigated before another retrieval attempt.

## Offline verification

The focused suite covers all 64 requests, exact cursor resume, interrupted retrieval, raw/receipt integrity, malformed successful responses, repeated cursors, identity failures, complete year/month/day refinement, retained unstable-parent occurrences, external plan/source pins, source changes during fetch and export, competing locks, provider failures and shared cooldowns, a cooldown arriving between requests, and cross-leaf duplicates with no automatic re-fetch.

Verification command:

    python -m pytest tests/s2/test_literature_reconcile_search.py tests/s2/test_literature_reconcile_plan.py tests/test_literature_continuation.py -q

The focused suite passed all 87 tests on the verified desktop with unchanged source and test hashes across execution. The source boundaries and result are recorded in [reconciliation_offline_tests_launch.json](../../results/s2_2026-09-21/reconciliation_offline_tests_launch.json). The earlier reconciliation_offline_tests.json checkpoint overlapped the last source edit and is preserved as invalidated evidence. This note does not itself record a live reconciliation request or a scientific completion decision.

Before the launch boundary, the two new files were normalized to their declared LF line endings and one final newline; executable tokens are unchanged. The exact launch bytes passed the same 87 tests and a fresh zero-request real-cache preflight. Earlier passing evidence and its pins remain historical. Current launch pins are [reconciliation_launch_pins_v2.json](../../results/s2_2026-09-21/reconciliation_launch_pins_v2.json), SHA-256 `d3d361e0268edc1e56499222695c99ff9d7ab60b736851d89903946c58015cec`.
