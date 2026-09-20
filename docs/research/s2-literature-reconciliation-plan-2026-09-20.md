# P-LIT prospective enumeration reconciliation — 2026-09-20

The existing broad-window cache has count drift and duplicate identities. This operational plan checks the same four literal OpenAlex queries in smaller complete date partitions. It retains the old observations; it does not reinterpret their completion flags. No new OpenAlex request or retrieval worker is part of this preparation.

The [September 18 scientific rule](s2-operating-decisions-2026-09-18.md#p-lit-prospective-search-and-coding-choices) and [retrieval amendment](s2-literature-retrieval-amendment-2026-09-18.md) remain unchanged. Crossref remains DOI-specific bibliographic validation. This plan changes enumeration order and partitions, not query words, the full date window, eligibility, the registered hypothesis, or UNKNOWN handling.

## Preparation and review

- [x] Specify all four literal queries and the complete inclusive window, 2011-01-01 through 2026-09-18.
- [x] Specify complete disjoint calendar-year partitions, with full month/day subdivision when observations are unstable.
- [x] Add a standalone manifest builder and offline page-receipt validator without importing or editing the active engine/worker.
- [x] Add focused offline tests for coverage, clipping/leap dates, receipts/cursors, count drift, identity failures, identity union and preserved old evidence.
- [x] Run the initial focused suite and prepare the original prospective manifest: 30 tests passed; all 64 initial partitions retained; zero requests.
- [x] Review and bank the initial note, source, tests and manifest in 784d5a2, preserving that boundary as history.
- [x] Check actual terminal responses and correct the prospective terminal rule before any new retrieval: 33 tests pass; the revised manifest retains 64 partitions and zero requests. No reconciliation requests or live runner.

The implementation is [reconcile_plan.py](../../src/s2/literature/reconcile_plan.py), with [offline tests](../../tests/s2/test_literature_reconcile_plan.py). The corrected preparation used:

```powershell
python -m pytest tests/s2/test_literature_reconcile_plan.py -q
python src/s2/literature/reconcile_plan.py --source results/s2_2026-09-19/literature_openalex_continuation --out results/s2_2026-09-20/reconciliation_plan_terminal_revision
```

The [corrected manifest](../../results/s2_2026-09-20/reconciliation_plan_terminal_revision/plan.json) supersedes the [initial prospective manifest](../../results/s2_2026-09-20/reconciliation_plan/plan.json) for future retrieval. The initial manifest and its 30-test verification remain preserved in the original directory and pushed commit 784d5a2. The corrected directory is separate and pins the revised validator; no earlier manifest or response is replaced.

The output directory must be new and separate from the old cache; the command above records completed preparation and cannot overwrite its existing output. Preparation pins the prior search specification, readout, candidate export and available stream-status files, verifies they did not change while read, and retains the old identity/occurrence inventory. The source export is pinned as historical evidence; it is not newly certified as complete or as a raw-cache audit. The existing raw pages and their receipts remain at their recorded locations.

## Exact enumeration contract

Each of the four unchanged queries receives 16 initial calendar-year partitions: 2011 through 2025 in full, plus January 1 through September 18, 2026. These 64 partitions exactly cover the registered window separately for each query. Every request uses `per_page=100`, initial `cursor=*`, and `sort=publication_date:asc,display_name:asc`. Each later cursor is taken from the preceding response. Any repeated non-null cursor token within an attempt, including a return to the initial `*`, leaves pagination unresolved even when IDs and counts agree. The [OpenAlex sorting documentation](https://help.openalex.org/api/sorting/) lists these fields and comma-separated sort keys; [date filtering](https://help.openalex.org/api/filtering/) supports the paired publication-date boundaries.

Successful raw pages and receipts use the existing naming/schema convention: `page_000001.json` and `page_000001.receipt.json`, then consecutive page numbers. Receipts must include the exact query/filter/sort/page-size/cursor parameters, database, timezone-aware retrieval timestamp, raw byte count and SHA-256. Each raw response must retain the complete result objects and explicit count/cursor metadata. Different attempts use separate directories; no bad attempt is repaired by replacing its raw pages.

A partition passes only if its page chain is intact, all observed totals are identical and equal to the raw record count, all provider work IDs are valid and unique, returned publication dates lie within that partition in nondecreasing order, and a terminal receipt exists. There is no count tolerance, top-N cutoff, or deduplication that can conceal repeated source rows. A missing page or transport interruption remains resumable and unresolved; a byte/request mismatch is a hard integrity error.

The corrected prospective terminal rule requires an explicitly null `next_cursor`; `results` may be empty or nonempty, including a full 100-row final page. Every final-page record is indexed before terminal status is assigned. A missing or malformed cursor is not a terminal receipt. A short page with a non-null cursor remains nonterminal; an empty page with a non-null cursor leaves the attempt unresolved. Cached pages after a null-cursor terminal receipt are an integrity error. Exact count equality, unchanged totals, valid unique identities, date ordering and receipt integrity remain required for a partition to pass. Prior failed requests may coexist with a subsequently verified successful chain; their failure artifacts remain recorded.

This is an empirical compatibility correction. The [official paging documentation](https://help.openalex.org/api/paging/), checked on September 20, still describes termination with both a null cursor and empty results. The preserved broad-window query 1 page 223 instead has 91 results and an explicit null cursor; query 2 page 68 has 95 results and an explicit null cursor. The [response observations](../../results/s2_2026-09-20/reconciliation_plan_terminal_revision/terminal_response_observations.json) pin both raw-page and receipt hashes. With no next cursor available, requiring another empty page would reject these terminal response shapes indefinitely.

The correction does not validate those existing streams. Query 1 retains 22,291 raw rows, changing totals ending at 22,265, and duplicate identities; query 2 retains 6,795 raw rows and changing totals ending at 6,796. Both remain unresolved under the unchanged count and identity requirements. The initial manifest's empty-and-null rule remains historical evidence; the separately pinned corrected manifest governs any future reconciliation attempt.

A year with observed count, identity, ordering, or termination instability is subdivided into every month intersecting that year. An unstable month is subdivided into every day. Child partitions must cover the entire parent without gaps or overlaps, including leap days and the clipped final month. The original unstable attempt stays preserved. A day that remains unstable stays unresolved; no smaller interval or relaxed threshold is silently substituted. Incomplete retrieval without instability is resumed rather than treated as a completed or omitted partition.

Final leaf validation requires exact disjoint coverage of all four full windows. Provider IDs must also be unique across all leaves of a given query: a publication-date edit could otherwise move a work between partitions and leave local counts looking consistent. Appearance in different literal queries is legitimate and retained.

## Identity reconciliation and scientific limits

The identity union retains old-only, new-only and shared provider IDs, all their source occurrence references, changed query memberships, and unresolved identifiers. Old-only records remain candidates for investigation, not exclusions or deletions. The registered DOI/title-year-author candidate reconciliation and publication-date conflict review still occur separately against the preserved metadata and primary sources. These helpers do not change candidate or inclusion lists.

The strongest validator status is `OBSERVED_PARTITION_ENUMERATION_CONSISTENT`. It means the preserved observations meet this prospective contract. It is not proof of an immutable OpenAlex snapshot: records can change during or between requests, equal date/title sort keys can tie, and compensating additions/removals can preserve counts. Differences between old and new identities still require reconciliation, with both sets retained. This procedure reduces observable enumeration instability but cannot guarantee universal database coverage.

All manifest and validation summaries explicitly retain `global_p_lit_complete=false`. Complete P-LIT coverage additionally requires the registered known-source candidates, the one-generation backward-reference searches from included papers, bibliographic/date reconciliation, independent primary-source eligibility decisions and unresolved-access accounting. No method-reporting fields or hypothesis outcome are coded by this tool.

A future separately banked retrieval runner must honor the provider-wide cooldown and failure policy, use these immutable partition attempts and the existing source-boundary discipline, and preserve transport failures. There is no live transport, quota override, scheduler, or worker launch in this module. The currently pinned broad-window engine and its worker remain untouched.

## Validation record

The corrected focused suite passed all 33 tests on the verified isolated background desktop. The terminal regressions include a nonempty single-page result, a multipage chain ending with 100 rows, and count drift even when the final total equals the raw row count. The [corrected execution record](../../results/s2_2026-09-20/reconciliation_plan_terminal_revision/verification.json) pins the tested source SHA-256 `b6dac6d110389051c2ffc240b056b071c28dccc1baa0a62aaffec9028bb57d73` and the test-file hash; it also retains the earlier 32-test run. The [initial 30-test execution record](../../results/s2_2026-09-20/reconciliation_plan/verification.json) remains unchanged.

Corrected preparation against the preserved cache succeeded with 64 partitions and zero requests. Its old identity inventory is byte-identical to the initial inventory and retains 28,226 unique provider work IDs, including all source occurrences; these are provider IDs, not the 28,191 DOI/title-deduplicated candidate keys. Source files were unchanged while read. The corrected manifest remains `PROSPECTIVE_NOT_RETRIEVED` with `global_p_lit_complete=false`; no reconciliation retrieval runner or new request is part of this preparation.
