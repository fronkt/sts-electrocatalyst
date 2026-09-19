# Offline research during the Anvil outage — 2026-09-19

This pass advances source reconciliation, scientific interpretation and the prepared diagnostic's deployment checks. It changes no frozen DFT deck, acceptance threshold, census result or adopted selection rule. No additional DFT job was submitted.

## Compute timing and current evidence

Purdue's September 18 reminder confirms Anvil is unavailable until **Monday, September 21 at 8 p.m. EDT (September 22 00:00 UTC)**. CPU/GPU services and storage are affected; jobs do not run or start during the outage. This official endpoint supersedes using the earlier observed reservation end as a reopening prediction. Queue estimates from before maintenance are not guaranteed start times. [Official outage notice](https://rcac.purdue.edu/news/7788).

Array 20813525 has one failed clean slab and one completed reconstructed-O relaxation in its last confirmed evidence. The completed endpoint has Cr–O 1.561960 Å; the failed slab has no converged adsorption reference. Tasks 3–9 were last confirmed queued. The read-only collector is alive, but its last successful observation remains September 19 04:08 UTC; its September 19 22:10 UTC heartbeat reports a remote timeout and explicitly stale observations. There is no new DFT result to interpret during this check.

The literature worker's API-boundary wait is separate from the cluster outage. Its earliest continuation is September 20 00:00 UTC (September 19, 8 p.m. EDT), subject to provider availability. The existing worker and queued primary array remain unchanged.

## Useful scientific progress

**S8 ranking:** all 18 independently calculated p10 values agree with the original point estimates. Cu8 retains its adsorption-only p10 lead through all 180 leave-one-decoration-out cases. Omitting one of its own decorations gives p10 0.381902–0.386624 V. The two interpolation supports are Cr seed16/site2 and seed26/site1, each with reconstructed O; the current Cu8 DFT target is the minimum at seed20/site2. Thus the current array tests the motif hypothesis but not those particular p10 supports directly.

The review also corrects the physical interpretation and uncertainty accounting. These CHE descriptors do not determine measured current. Retained populations are unequal, exact ties acquired alphabetical ranks, and bootstrap draws could omit empty competitors. Strict Cu8/Ni31 each have three supporting decorations and 4.239% empirical empty-draw probability. Neither another ML model nor one converged O endpoint establishes a validated composition ranking. The [review](s8-ranking-independent-review-2026-09-19.md) and [corrected proposal](s8-ranking-statistic-proposal-2026-09-19.md) keep the original results, prospective rule and experimental comparator distinct. No melt is selected.

**Claim support:** independent recounting confirms 70/810 nontrivial headers and **50 LOCKED detector outputs**, all in the four-layer class. The corrected worksheet had conflated the two counts. The 50 final-force-positive paths equal the 50 LOCKED paths in this corpus; their predicates remain distinct. The final-force result is still 50 successes, 496 failures and 80 unknowns out of 626. Layer-class association does not establish a causal thickness effect, and the controls do not establish a universal zero false-positive rate. The [evidence audit](claim-evidence-audit-2026-09-19.md) carries these limits beside the separate S6 outcomes. The September 20 re-test remains open.

**Primary source reconciliation:** eight article PDFs and two SI PDFs have checked DOI/title/author identities, ten preserved exact-DOI Crossref responses, and independently verified local/raw-response hashes. Five complete Divanis references now link additively to canonical identities. No OpenAlex quota was consumed, no publisher PDF is included in this batch, and every record remains NOT_SCREENED / NOT_CODED. Version ambiguity, incomplete article/SI bundles and date precision remain explicit in `results/s2_2026-09-19/primary_identity_review/identity_review.json`. No reporting-rate numerator changes.

## Diagnostic readiness

The five prepared fixed-geometry SCFs remain unchanged. A path-only correction removes Windows separators from the Linux deployment manifest/specification and wrappers. Original files remain under `pre_portability_fix/`; the specification is identical after separator normalization. Exact-byte attributes also prevent the pinned Cu8 positions JSON from changing on Git checkout.

The launcher review addresses staged-byte identity, held-resource inspection, ambiguous submissions, duplicate execution, terminal task accounting, immutable mirroring and scientific evidence validation. Failed or missing tasks stay visible in the five-task readout. A residual crossing is distinct from accepted convergence. The wait deadline extends beyond the official maintenance window. The focused test results and any remaining implementation limits are recorded in the diagnostic preflight review and verification receipt. Live scheduler acceptance remains untested during the outage; prepared does not mean submitted.

## Next dependencies

1. Continue registered literature discovery when the API budget permits, then reconcile the remaining identities and complete required article/SI access. Freeze inclusion before primary method coding.
2. Perform the scheduled September 20 claim re-test against the evidence that has actually landed, retaining the failed exposure prediction and separate parameter-sensitivity findings.
3. After Anvil returns, obtain fresh accounting and collect all nine primary legs. Compare clean references and alternative starts only when they exist and pass their scientific gates. Use the prepared five-SCF diagnostic to distinguish convergence behavior at its fixed geometries; it supplies no adsorption energy by itself.
4. Before S8 selection, settle the prospective ranking/admission/uncertainty rule and experimental endpoint. The p10 support mismatch is a concrete validation-design issue; it does not authorize extra jobs or reclassify sites.

Verification: 190 diagnostic/SCF/parser tests and six ranking tests passed. All 20 launch/input pins match the committed boundary, and all 25 original batch artifact paths match their staged bytes. The reviewed batch is pushed as `4792397`; the local diagnostic boundary is updated without starting a launcher.
