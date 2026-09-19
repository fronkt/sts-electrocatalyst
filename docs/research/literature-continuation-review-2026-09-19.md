# P-LIT continuation review — 2026-09-19

**Recommendations for execution; no scientific protocol change is adopted here.** This file-only review does not modify the pinned search engine, cached responses, candidate list, inclusion decisions or method codes. The September 18 operating decisions and retrieval amendment remain controlling.

## What the current evidence establishes

`results/s2_2026-09-18/literature_openalex/search_readout.json`, timestamped `2026-09-19T00:34:12Z`, reports 20,000 source occurrences and 19,813 metadata candidates, with 21 candidates carrying metadata variants. Query 1 has 19,700 occurrences, 19,698 distinct provider IDs, two duplicated provider IDs (`W4385415328`, `W4391229757`), and reported totals of 22,256 and 22,257. Queries 2–4 each have only their initial 100 records. All four streams remain incomplete; no inclusion list is frozen and no methods are coded.

The preserved query-1 page-198 attempt-6 error body explicitly reports `dailyRemainingUsd=0`, `prepaidRemainingUsd=0`, `retryAfter=85191`, and a midnight-UTC reset. Its failure receipt is at `2026-09-19T00:20:09Z`, placing that advertised reset near `2026-09-20T00:00:00Z` (September 19, 8 p.m. EDT). This is an advertised retry boundary, not evidence that a request has succeeded after it.

In `src/s2/literature/search.py`, `fetch_page()` truncates numeric HTTP `Retry-After` to 60 seconds, ignores JSON-body `retryAfter`, and retries six times. `_run_locked()` then continues to the other query streams after `walk()` records a request failure. The result was six daily-budget failures for query 1 and additional failures for queries 2–4. This is an operational retry defect; it does not justify changing the scientific search, buying access or rotating identities.

## Useful work while the API budget waits

Prepare a source-occurrence inventory from the already registered complementary sources:

| Source | Exact local locator or identity | Work available now |
| --- | --- | --- |
| Xu 2015 | DOI `10.1021/jp511426q`, also cited in both syntheses | Locate the cached article/SI and retain bibliographic identity and access receipts. |
| Man 2011 | DOI `10.1002/cctc.201000397`, also Divanis reference [1] | Locate the cached article/SI and retain bibliographic identity and access receipts. |
| Divanis 2020 ESI | `docs/research/2026-08-15-sampling/divanis_esi.txt`, page S29 | Transcribe all 25 numbered references with source positions. References [1]–[24] are the table's source articles; [25] is a methodological citation. Preserve both roles; do not silently omit [25] or assume any reference is eligible. |
| First synthesis | `docs/research/2026-08-15-lit-sweep-round1-synthesis.md` | Inventory every identifiable cited work, including unverified and non-topical citations, retaining its original locator and verification caveat. |
| Second synthesis | `docs/research/2026-08-15-lit-sweep-round2-synthesis.md` | Do the same independently; preserve citations shared with the first synthesis as separate discovery occurrences. |

Use additive files such as `results/s2_2026-09-19/literature_complementary/sources.json`, `citation_occurrences.jsonl` and `access_inventory.jsonl`. Record source-file hash, page/line or reference number, verbatim citation identity, stated DOI/URL, normalized identity, available local article/SI files and hashes, retrieval/access status, and ambiguity notes. Reuse the existing DOI and title/year/first-author identity rules, but retain unresolved identities and all discovery edges. A synthesis's assertion is a discovery lead, not primary evidence for eligibility or a methods code.

Primary-text/SI acquisition and bibliographic reconciliation can proceed from those fixed leads without consuming OpenAlex search calls. Leave `inclusion_status=NOT_SCREENED` and `method_coding_status=NOT_CODED` during this preparatory pass. Do not populate symmetry, vibrations or magnetism fields opportunistically while locating sources.

Once base discovery and the candidate procedure are settled, apply the unchanged inclusion rule. Inspect references once from each included **base** paper; record the parent paper and reference number for every addition. Newly discovered references do not seed a second generation, consistent with the prohibition on recursive expansion. Resolve those candidates, Crossref DOI validation and access uncertainties before freezing the final inclusion/exclusion list and starting method coding. An unavailable necessary source remains unresolved, not a negative reporting result.

## Smallest sound quota repair

Retain `search.py` and the original output directory at their pinned revision. Bank a versioned continuation driver and its execution record before using it in a separate output directory. It may reuse the existing parsing, indexing, cache-verification and export functions; record both the pinned engine hash and new driver hash, and copy verified raw pages/receipts additively using the existing cache-transfer contract. Do not quietly monkeypatch behavior while claiming only the old engine hash describes execution.

The driver/transport needs one provider-wide cooldown shared by all four streams:

1. Before a network request, check a persisted `next_allowed_utc`. Cached-page validation remains available during cooldown; no HTTP request is needed to learn that the same budget is still exhausted.
2. On HTTP 429, preserve the raw body, response headers, request parameters, UTC time and hashes. Parse JSON `retryAfter` and HTTP `Retry-After` (seconds or HTTP-date). Distinguish explicit exhausted daily budget from a short rate limit; missing fields are not evidence of a daily exhaustion. Do not truncate the server's minimum wait. If multiple valid retry boundaries are present, use the latest.
3. For exhausted budget or a server delay unsuitable for an active worker, persist the boundary and exit the retrieval pass promptly. Suppress requests for the remaining streams, export the accumulated candidates, and label the operation `DEFERRED_API_BUDGET` or `DEFERRED_RATE_LIMIT`. Keep scientific completeness false. Preserve previous stream statuses and cursors instead of pretending an unattempted stream newly failed.
4. A later invocation before the boundary makes zero requests and reports the existing deferral. At/after the boundary, resume the exact next cursor with one request; a new quota response updates the deferral. Ordinary transient errors retain bounded retries without weakening cache, source-hash or completeness checks. A free-tier reset is not a promise of enough budget to finish every stream that day.

Focused verification should cover: body-only daily `retryAfter`; numeric and HTTP-date headers; conflicting boundaries; a daily 429 on query 1 causing zero requests on queries 2–4; restart during cooldown causing zero requests; successful resume at the unchanged cursor; ordinary short 429 and 5xx handling; malformed error bodies; exact cached bytes after migration; driver/source hash refusal; and unchanged candidate identities, unknowns and query/date parameters. No live paid-access test is necessary.

## Count drift must remain visible

Finish the existing cursor sequence when permitted, but a terminal cursor cannot repair the already observed changing totals and duplicated IDs. The current amended procedure correctly requires an unresolved-completeness result in that situation. Deduplication repairs the candidate union, not evidence that no records were skipped. Report raw occurrences, unique provider IDs, duplicate identities, all observed totals, retrieval interval and terminal evidence together; do not equate 19,813 candidates with 19,813 eligible papers.

An optional later reconciliation pass must be prospective and additive: preserve the first crawl, repeat the same literal query/date window in a separate run, compare complete provider-ID sets, and retain their union with discovery provenance. Agreement is evidence of stability, not proof of an immutable database snapshot; disagreement leaves coverage unresolved. Date partitions or different sorting are new retrieval procedures requiring an explicit dated operational amendment, not silent fixes to the present run. Do not introduce a top-N cutoff, drop duplicated records, privilege a convenient total, or change the >0.80 prediction to force completion.

The next concrete steps are therefore complementary-source inventory now, a tested and banked quota-aware continuation, cursor completion after the advertised reset, then an explicit assessment of the remaining coverage uncertainty before inclusion-list freeze. No P-LIT hypothesis verdict is justified yet.
