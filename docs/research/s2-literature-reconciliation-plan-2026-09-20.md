# P-LIT prospective enumeration reconciliation — 2026-09-20

The existing broad-window cache has count drift and duplicate identities. This operational plan checks the same four literal OpenAlex queries in smaller complete date partitions. It retains the old observations; it does not reinterpret their completion flags. No new OpenAlex request or retrieval worker is part of this preparation.

The [September 18 scientific rule](s2-operating-decisions-2026-09-18.md#p-lit-prospective-search-and-coding-choices) and [retrieval amendment](s2-literature-retrieval-amendment-2026-09-18.md) remain unchanged. Crossref remains DOI-specific bibliographic validation. This plan changes enumeration order and partitions, not query words, the full date window, eligibility, the registered hypothesis, or UNKNOWN handling.

## Preparation and review

- [x] Specify all four literal queries and the complete inclusive window, 2011-01-01 through 2026-09-18.
- [x] Specify complete disjoint calendar-year partitions, with full month/day subdivision when observations are unstable.
- [x] Add a standalone manifest builder and offline page-receipt validator without importing or editing the active engine/worker.
- [x] Add focused offline tests for coverage, clipping/leap dates, receipts/cursors, count drift, identity failures, identity union and preserved old evidence.
- [x] Run the focused suite and prepare the prospective manifest from the quiescent preserved cache: 30 tests pass; all 64 initial partitions retained; zero requests.
- [ ] Review and bank the note, source, tests and manifest before any new retrieval implementation or run.

The implementation is [reconcile_plan.py](../../src/s2/literature/reconcile_plan.py), with [offline tests](../../tests/s2/test_literature_reconcile_plan.py). The preparation command is:

```powershell
python -m pytest tests/s2/test_literature_reconcile_plan.py -q
python src/s2/literature/reconcile_plan.py --source results/s2_2026-09-19/literature_openalex_continuation --out results/s2_2026-09-20/reconciliation_plan
```

The output directory must be new and separate from the old cache. Preparation pins the prior search specification, readout, candidate export and available stream-status files, verifies they did not change while read, and retains the old identity/occurrence inventory. The source export is pinned as historical evidence; it is not newly certified as complete or as a raw-cache audit. The existing raw pages and their receipts remain at their recorded locations.

## Exact enumeration contract

Each of the four unchanged queries receives 16 initial calendar-year partitions: 2011 through 2025 in full, plus January 1 through September 18, 2026. These 64 partitions exactly cover the registered window separately for each query. Every request uses `per_page=100`, initial `cursor=*`, and `sort=publication_date:asc,display_name:asc`. Each later cursor is taken from the preceding response. Any repeated non-null cursor token within an attempt, including a return to the initial `*`, leaves pagination unresolved even when IDs and counts agree. The [OpenAlex sorting documentation](https://help.openalex.org/api/sorting/) lists these fields and comma-separated sort keys; [date filtering](https://help.openalex.org/api/filtering/) supports the paired publication-date boundaries.

Successful raw pages and receipts use the existing naming/schema convention: `page_000001.json` and `page_000001.receipt.json`, then consecutive page numbers. Receipts must include the exact query/filter/sort/page-size/cursor parameters, database, timezone-aware retrieval timestamp, raw byte count and SHA-256. Each raw response must retain the complete result objects and explicit count/cursor metadata. Different attempts use separate directories; no bad attempt is repaired by replacing its raw pages.

A partition passes only if its page chain is intact, all observed totals are identical and equal to the raw record count, all provider work IDs are valid and unique, returned publication dates lie within that partition in nondecreasing order, and a terminal receipt exists. There is no count tolerance, top-N cutoff, or deduplication that can conceal repeated source rows. A missing page or transport interruption remains resumable and unresolved; a byte/request mismatch is a hard integrity error.

The prospective terminal rule requires both an explicitly null `next_cursor` and empty `results`, as described in the [current paging documentation](https://help.openalex.org/api/paging/). A nonempty null-cursor response is preserved but remains unresolved under this rule. A shorter nonterminal page is not a substitute for the terminal receipt. Prior failed requests may coexist with a subsequently verified successful chain; their failure artifacts remain recorded.

A year with observed count, identity, ordering, or termination instability is subdivided into every month intersecting that year. An unstable month is subdivided into every day. Child partitions must cover the entire parent without gaps or overlaps, including leap days and the clipped final month. The original unstable attempt stays preserved. A day that remains unstable stays unresolved; no smaller interval or relaxed threshold is silently substituted. Incomplete retrieval without instability is resumed rather than treated as a completed or omitted partition.

Final leaf validation requires exact disjoint coverage of all four full windows. Provider IDs must also be unique across all leaves of a given query: a publication-date edit could otherwise move a work between partitions and leave local counts looking consistent. Appearance in different literal queries is legitimate and retained.

## Identity reconciliation and scientific limits

The identity union retains old-only, new-only and shared provider IDs, all their source occurrence references, changed query memberships, and unresolved identifiers. Old-only records remain candidates for investigation, not exclusions or deletions. The registered DOI/title-year-author candidate reconciliation and publication-date conflict review still occur separately against the preserved metadata and primary sources. These helpers do not change candidate or inclusion lists.

The strongest validator status is `OBSERVED_PARTITION_ENUMERATION_CONSISTENT`. It means the preserved observations meet this prospective contract. It is not proof of an immutable OpenAlex snapshot: records can change during or between requests, equal date/title sort keys can tie, and compensating additions/removals can preserve counts. Differences between old and new identities still require reconciliation, with both sets retained. This procedure reduces observable enumeration instability but cannot guarantee universal database coverage.

All manifest and validation summaries explicitly retain `global_p_lit_complete=false`. Complete P-LIT coverage additionally requires the registered known-source candidates, the one-generation backward-reference searches from included papers, bibliographic/date reconciliation, independent primary-source eligibility decisions and unresolved-access accounting. No method-reporting fields or hypothesis outcome are coded by this tool.

A future separately banked retrieval runner must honor the provider-wide cooldown and failure policy, use these immutable partition attempts and the existing source-boundary discipline, and preserve transport failures. There is no live transport, quota override, scheduler, or worker launch in this module. The currently pinned broad-window engine and its worker remain untouched.

## Validation record

The focused suite passed all 30 tests on the verified isolated background desktop. Preparation against the current real cache succeeded with 64 partitions and zero requests. The old identity inventory retains 28,226 unique provider work IDs, including all source occurrences; these are provider IDs, not the 28,191 DOI/title-deduplicated candidate keys. Source files were unchanged while read. The [execution record](../../results/s2_2026-09-20/reconciliation_plan/verification.json) pins the tested source and test-file hashes. The manifest remains `PROSPECTIVE_NOT_RETRIEVED`; no reconciliation collector is running.
