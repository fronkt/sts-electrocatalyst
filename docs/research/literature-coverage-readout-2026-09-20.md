# Literature coverage progress — 2026-09-20

Coverage remains incomplete. The current cache retains 29,986 source occurrences and 28,191 deduplicated candidate keys, an increase of 8,378 candidates since the previous snapshot. No candidate or inclusion population is frozen, and method-reporting fields remain uncoded.

## Database discovery and preservation

| Literal query | Pages | Raw records | Observed state |
|---|---:|---:|---|
| rutile oxygen evolution | 223 | 22,291 | Cursor exhausted; changing totals and repeated IDs prevent completeness |
| RuO2 oxygen evolution | 68 | 6,795 | Cursor exhausted; changing totals prevent completeness |
| IrO2 oxygen evolution | 8 | 800 | Interrupted at provider-wide quota boundary |
| rutile oxide computational hydrogen electrode | 1 | 100 | Incomplete; same provider boundary |

The [incremental archive](../../results/s2_2026-09-20/literature_cache_delta/manifest.json) retains 223 new or changed files in six compressed shards (39,570,098 bytes), reusing 400 byte-identical files from the previous snapshot. Archive, member and reused-source hashes were verified. The complete [review-order queue](../../results/s2_2026-09-20/eligibility_queue/README.md) retains every candidate; title signals choose reading order only and exclude nothing.

The [prospective reconciliation procedure](s2-literature-reconciliation-plan-2026-09-20.md) has 30 passing tests and a real-cache manifest with 64 complete year partitions, exact date coverage, unchanged literal queries, explicit count/identity/cursor checks and complete month/day refinement for unstable intervals. It preserves old/new identity unions and leaves unstable days unresolved. Preparation used zero network requests. This is an offline plan and validator; its new retrieval runner is still required. The existing broad-window collector cannot by itself repair the already observed count drift.

## Complementary and primary-source evidence

The [independently reviewed identity reconciliation](complementary-identity-review-2026-09-20.md) preserves all 120 original identity keys and 271 citation occurrences. Of these, 103 keys / 237 occurrences resolve to 81 canonical identities; 17 keys / 34 occurrences remain partial or unresolved. All 25 Divanis references and ten arXiv identities were checked, with six supported preprint/journal relations retained. Exact Crossref checks cover 72 identities; the Zenodo dataset is verified in DataCite rather than mislabeled invalid after its Crossref 404. Citation errors and uncertain joins stay visible.

The [joint eligibility subset](../../results/s2_2026-09-20/reviewed_eligibility_subset.json) reconciles two independent passes on ten previously identified papers: four satisfy eligibility pending the global freeze, one is excluded because its calculation arm is not rutile (110), and five remain unresolved. This is a reviewed subset, not the total eligible population. The four supported cases are Man, Feng, Xu and Garcia-Mota. Divanis's original TiO2(110) calculation arm has an explicitly graphical overpotential, but the inspected sources do not yet settle its polymorph. A perspective title alone does not settle eligibility.

[Article/SI access evidence](literature-access-review-2026-09-20.md) now includes verified official Tripkovic, Exner and Xu supplements. Xu's 68-page journal supplement is distinct from its earlier Zenodo release. Three publisher-linked Wiley supplements still return HTTP 403; Feng's SI, Mom's article and Gauthier's final-version equivalence remain gaps. Inico's publisher first-publication date (July 19, 2024) conflicts with Crossref's online date (September 12); both are retained and both fall within the registered window.

The [one-generation reference pass](backward-reference-pass-2026-09-20.md) retains 180 numbered reference groups / 217 split citation occurrences from the four provisionally eligible base articles and available Xu SI. It preserves original text, numbered/lettered labels, page/line anchors, file hashes and explicit identifiers. Missing Man, Feng and Garcia-Mota supplements still leave their reference coverage open. No recursive expansion or method coding occurred.

## Continuation

The user chose scheduled quota resets. Supervisor PID 30280 is waiting for the retained provider boundary: September 21 at 00:00:30 UTC, or Sunday September 20 at 8:00:30 p.m. EDT. A task follow-up is active daily at 8:20 p.m. EDT to inspect actual progress and continue the full coverage work; it stays quiet on unchanged, non-actionable state. It must detect a stopped or exhausted collector rather than equate its exit with completed coverage.

Remaining work is enumeration and drift reconciliation; identity/version/date resolution; primary-source eligibility across the full candidate union; one-generation references from every eligible base-discovery paper; and independent reconciliation before the population freeze. A bounded primary review of the next 29 work-order candidates is in progress separately. Unknown access and ambiguous membership remain open. No primary reporting proportion or hypothesis verdict is available yet.