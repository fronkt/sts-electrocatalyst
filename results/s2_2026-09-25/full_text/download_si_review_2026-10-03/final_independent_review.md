# Final independent closure review — 2026-10-03

## Recommendation

**GO for the scoped five-package reconciliation and verified rebuild, with the scientific holds below retained.** This is not a new policy ruling, a broader scientific certification, or authorization to release/melt the held cases.

## Observed receipts

The latest files present in `scientific_final_checked/` are timestamped 2026-10-03 18:59 UTC. `regression.json` reports 78 tests, zero failures/errors. `deterministic_rebuild.json` records two identical hashes for all four rebuilt outputs, `network_disabled: true`, and the forced checklist IDs `S29721,S10090,S22807,S26024`. `verification.json`, `si_round_verification.json`, and `phase_verification.json` each report 2,496 records, 144 checklist records, and no errors. The phase receipt has exactly five changed rows: S24094, S28435, S29420, S29447, and S29636; it preserves 421 baseline historical files and all 21 unrelated DFT files. It reports 10 initial and 15 total source assessments across eight preserved original output files. The assessment history totals those 15 assessment records (10 initial + five additional); transcription repairs and one-row views are correctly excluded from the count.

The phase receipt outcomes are S29420 and S29447 **ELIGIBLE**; S29636, S24094, and S28435 **UNRESOLVED**. The checklist is retained at 144 records, including the four forced IDs above. The recorded budget is unchanged: lifetime cap $50, tracked $1.1105254, and zero new paid external API calls. `baseline.json` pins the restored Oct 2 `scientific_final/phase_verification.json` to `a09f8a7e7edda53c779f37f3188c452fffc18cd0ca55aa12d98aec5fc1d42cdf`; the Oct 3 phase verifier reports no historical-file errors.

## Scientific/adjudication boundary

- S29447's E6/η basis is the explicit main-text p. 7 assignment of each site's maximum ΔG1–4 at 0 V vs RHE to that site's limiting potential, with the SI CHE/RHE definition and Table S3 values. The selected derivation is the author-reported equivalent. The 1.5 V activity statement, Fig. 10 ranking, and D4 author-highlight ranking are not substituted for that assignment; no 1.23 V subtraction or new η calculation is introduced.
- S28435 remains E5/E6 UNCLEAR and UNRESOLVED. C01 identifies the experimental rutile diffraction card, but no computed OER facet is thereby assigned. The η-symbol/barrier wording question remains deferred; the YES dissenting assessments remain in the record. S29636 and S24094 remain E6 UNCLEAR under the documented missing computational potential/reference conditions.
- S29420's source-read E2 is UNCLEAR, while the recorded existing DOI-matched date reconciliation is in-window; its numeric main/SI η discrepancy is retained without correction or averaging. Thus its ELIGIBLE final state is consistent with the documented external date check, not a silent change to the source excerpt.

## Verification limits / pending boundaries

The phase verifier checks exact scope, source identity/binary/text pins and read joins, frozen historical fields/files, unrelated DFT hashes, checklist retention, forced IDs, assessment counts, and budget. The rebuild runs offline and deterministically. These receipts do not independently adjudicate scientific criteria; manual source review and the explicit `reviewed_decisions.json`/`adjudication_spec.json` remain the scientific basis. In particular, the verifier does not itself infer a facet or resolve the deferred η-label question.

`source_read_gate.json` confirms five identities and complete SI packages for reading, but records incomplete DOCX page-layout rendering and an unexecuted ACS embedded Origin/OLE object. Those are format limitations, not claims that hidden object contents or all Word layout semantics were independently verified. Preserve them as limitations; they do not change the stated holds or authorize additional inference.

The evidence-recovery receipt is named `scientific_final_checked/verification.json` (not `evidence_recovery_verification.json`). No missing receipt was treated as passing, and no verdict, policy, or release state was changed in this review.
