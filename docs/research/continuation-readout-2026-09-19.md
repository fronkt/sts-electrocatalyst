# Research continuation — 2026-09-19

At the 02:54 UTC scheduler check, array 20813525 had one failed clean-slab leg, one completed reconstructed-O leg and seven pending legs (`ReqNodeNotAvail`; the next leg also showed reserved maintenance). The collector was healthy at 03:07 UTC, observing the same two terminal legs. No additional calculation or retry was submitted.

## Cr endpoint and failed reference

The two terminal raw outputs, QC receipts and scratch inventories are preserved with hashes in `results/lowtail_dft_2026-09-18/interim_20260919/terminal_mirror.json`. Runtime decks and full projection output remain local/remote under the existing banking policy; their hashes are retained.

An independent parse of the completed Cu8Cr23Mn35Co34 seed20/site2 reconstructed-O output confirms all 73 final coordinates, 22 converged SCF cycles, BFGS convergence, a maximum free force component of 0.00185093 Ry/bohr and effectively unchanged fixed coordinates. The final Cr–O distance is **1.561960 Å**. The input, runtime, output and QC byte identities are recorded in `endpoint_check.json`.

This is evidence that a short Cr–O endpoint persists under this DFT recipe from the reconstructed start. It does not establish a vibrational minimum, preference over the unreconstructed start, an adsorption energy or an HEA winner. The clean slab failed and the alternative start is still queued.

The failed slab completed four SCF cycles and three BFGS steps. In cycle five QE required **8.08e-8 Ry**, and all 126 completed residual estimates exceeded that target. Its minimum was 3.6e-7 Ry; the supervisor stopped as iteration 127 began. Review identified overcounting in the original trace and unsupported mechanism/progress wording. The dated correction in `lowtail-clean-slab-scf-stall-2026-09-19.md` withdraws those interpretations and the proposed go/no-go for six original-geometry tests that stop at 1e-6 Ry. The failed primary leg stays in its original denominator.

## Literature work during the quota wait

The amended retrieval has **20,000 source occurrences and 19,813 deduplicated metadata candidates**. All four streams are incomplete. Query 1 has two repeated provider IDs and a reported total that changed from 22,256 to 22,257; completing its cursor later will not by itself establish exhaustive coverage. No inclusion list is frozen and no method codes are assigned.

All 469 response, receipt, error, specification and candidate-export files at this stop are preserved in 13 ZIP shards under `results/s2_2026-09-19/literature_cache_snapshot/`: 528,469,865 original bytes, 83,712,949 compressed bytes. Every archive member was compared byte-for-byte with its original, successful-page receipt hashes were checked, and every source hash was checked again after compression. The SQLite index is reconstructible and excluded. The original cache and pinned search engine remain unchanged.

The preserved daily-budget response advertises the next reset at **2026-09-20 00:00 UTC (September 19, 8 p.m. EDT)**. This is an API retry boundary, not a guaranteed completion time. The complementary inventory now preserves 271 citation occurrences and 120 unresolved-or-DOI identity keys from the five registered source entries. These are discovery leads, not 120 distinct eligible papers. Source line contexts, citation and access joins, and local candidate-file hashes passed independent checks. Six exact source snapshots are archived so historical checkout line-ending rules cannot obscure their recorded hashes.

## Next dependencies

Read each remaining primary Cr leg after it terminates, keeping numerical failures explicit. Complete the unchanged metadata cursor sequence when the API permits, reconcile coverage uncertainty, then complete eligibility and the registered one-generation backward-reference pass before freezing the inclusion list and coding methods. The claim-sentence checkpoint remains September 20 and must use only evidence available then.

## Operational continuation and verification

The additive `src/s2/literature/continue_search.py` is adopted for retrieval continuation after the quota reset. It retains the exact original `search.py` engine hash and every scientific query, date, identity and completeness rule. It uses a separate output directory, a durable provider-wide cooldown and explicit source/driver pins. Active source caches, changed specifications, orphan raw/receipt pairs and migration from another continuation are refused; an existing continuation is resumed in place. No paid access is enabled.

The focused parser, continuation and pinned-engine suite passed **44 tests**. An integration pass against the real cache, with its network transport replaced by a function that refuses every request, made **zero network calls**, reproduced the candidate export byte-for-byte and left every original cache hash unchanged. It recorded `DEFERRED_API_BUDGET` through `2026-09-20T00:00:01.025335Z`; the extra second preserves the latest observed server minimum. This is a completed preflight, not an actively running retrieval worker. Its readout and verification receipt are under `results/s2_2026-09-19/`.

The corrected SCF parser was also checked against all four raw outputs used in the earlier diagnosis, with matching output hashes and unchanged residual trajectories. The reviewed traces preserve the original traces and distinguish 126 completed updates from the started iteration 127 in both stopped slab attempts. No relaxation acceptance criterion changed.

To continue metadata retrieval at or after the recorded boundary, run the pinned additive driver with source `results/s2_2026-09-18/literature_openalex` and output `results/s2_2026-09-19/literature_openalex_continuation` on the verified background desktop. Before-boundary invocations defer without network calls. The original source cache stays unchanged; the snapshot archive provides its exact-byte backup. A source revision requires a separately reviewed migration rather than pretending the old driver identity still applies.
