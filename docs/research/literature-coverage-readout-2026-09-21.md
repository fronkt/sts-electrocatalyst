# Literature coverage progress — 2026-09-21

All four broad OpenAlex query cursors reached their terminal pages. The preserved export now contains **31,392 candidate keys and 38,127 source occurrences**, an increase of **3,201 keys and 8,141 occurrences** from the September 20 snapshot. Every one of the 28,191 prior candidate IDs remains present. Count drift in all four streams still prevents a complete enumeration claim. Eligibility reconciliation and population freeze remain open; method-reporting fields stay uncoded.

| Query index in registered order | Pages | Raw records | Observed total counts |
|---|---:|---:|---|
| 1 | 223 | 22291 | 22256, 22257, 22265 |
| 2 | 68 | 6795 | 6794, 6796 |
| 3 | 52 | 5143 | 5138, 5143, 5144 |
| 4 | 39 | 3898 | 3892, 3897 |

The old supervisor stopped at its ten-pass budget after three HTTP 503 deferrals. Its stopped ledger is retained in [prior_supervisor_stopped.json](../../results/s2_2026-09-21/prior_supervisor_stopped.json). After the recorded retry boundary and confirmed process exit, one finite continuation pass resumed the unchanged cache. It ended with all cursors exhausted and exit 2 because the scientific enumeration flag remains false. There is no longer a running broad-search supervisor; its exit must not be treated as completed literature coverage.

The [before-retry archive](../../results/s2_2026-09-21/literature_cache_before_retry/manifest.json) and [after-retry archive](../../results/s2_2026-09-21/literature_cache_after_retry/manifest.json) preserve the new raw pages, failure evidence and metadata, with verified hash chains back to prior snapshots. The [current full queue](../../results/s2_2026-09-21/eligibility_queue/README.md) retains every candidate. Previously reviewed subsets remain separate evidence; the discovery queue's UNREVIEWED marker does not reverse them.

The [fresh prospective plan](../../results/s2_2026-09-21/reconciliation_plan/plan.json) pins the completed broad-search snapshot and its entire old occurrence inventory. Its 64 initial date partitions use the unchanged queries and full registered window. The separate bounded runner passed independent review and 87 offline tests. A real-cache preflight made zero requests and retained all 38,127 old occurrences / 31,429 provider IDs. Exact code/plan/inventory pins are in reconciliation_launch_pins_v2.json; this verified boundary is banked before any live reconciliation request. Broad pages/readouts remain immutable during reconciliation; only shared provider cooldown metadata may advance, retaining its history.

The reference extension covers the four additional eligible base papers, with official Neto and Dickens supplements now locally accessible. Lee direct article/SI downloads still return 403; the article's institutional PDF is readable through the web tool. Lim's official article and XML are accessible, but XML names five supplemental files through relative links without usable download destinations. These access gaps remain unresolved.

The daily 8:20 p.m. EDT follow-up remains active. It should use the current reconciliation runner state and shared cooldown after the runner's banked boundary, not repeatedly relaunch the exhausted broad cursors. Coverage still requires partition/identity reconciliation, complete primary eligibility across the full candidate union, one-generation reference discovery and independent adjudication before the registered freeze. No P-LIT method-reporting proportion or verdict is available.
