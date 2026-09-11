# HEA census: completed baseline and model arms, partial extended sampling — 2026-09-11

## Scope and verification

The [19:38:16 UTC snapshot](../../results/site_census_2026-09-06/readout_partial_2026-09-11/execution.json) contains 89 of 103 terminal manifests: all 12 CENSUS-1 baseline compositions, all 36 CENSUS-2 alternate-model runs, the one seven-endmember manifest, and 40 of 54 CENSUS-3 extended-decoration blocks. The 1,063 retained site rows include 144 baseline sites and 144 sites for each alternate model. All 14 unfinished manifests belong to CENSUS-3. The original `readout/` files remain unchanged; this snapshot does not replace a final complete readout.

The unchanged `site_census_readout.py` applies the frozen geometry and admission rules of [docs/91](../91-prereg-site-integrity-census-2026-09-06.md). The [independent file-only check](../../results/site_census_2026-09-06/readout_partial_2026-09-11/independent_verification.json) confirms all 89 result hashes and manifest identities, all 103 manifest hashes, the three frozen readout/classifier source hashes, and all five original readout hashes. Independent aggregation reproduces the 12 baseline reproduction verdicts, 48 model minima, model spreads, 576 baseline/model convergence records, and four ranking-rule orders. It is not a second implementation of the periodic-geometry classifier. No bootstrap or new calculator evaluation was needed for this readout.

## Completed baseline: reproduction is not chemical validity

All six previously gated compositions reproduce their historical minimum descriptor and winner bonds within the stated tolerances. Across the full twelve-composition pool, eight reproduce and four do not. Cr33Co5Ni29Cu33 shifts by +0.002101 V and fails the bond test. Mn31Ni31Co33Cu6, Mn34Cu7Fe33Cr27, and Co5Cu33Ni28Mn34 retain nearly identical minimum descriptors but their winning OOH metal–oxygen distances shift by −0.111534, +0.034776, and +0.004375 Å, respectively, beyond the 0.001 Å tolerance. An unchanged limiting step can conceal a changed endpoint. These cases remain in every denominator; the historical checkpoint/platform identity caveat is unresolved. See [reproduction.json](../../results/site_census_2026-09-06/readout_partial_2026-09-11/reproduction.json).

The historical Ni31Cr29Cu5Mn35 winner is seed 1, site 0, centered on Cr. Its OOH is bound and force-converged, with O–O = 1.379778 Å, Cr–O = 1.971091 Å, and hydrogen on the adsorbate. Thus the seed-0 transferred/desorbed OOH diagnostic does not describe the historical winner. The winner's complete chain passes the adsorbate-intact rule but fails the strict intact rule because its O state is classified as surface reconstruction. It has no force-unconverged adsorbate state in MACE; this does not imply DFT force convergence.

The result is not typical of the sampled baseline pool. Only 23/144 chains (16.0%) are adsorbate-intact and 17/144 (11.8%) strictly intact. OOH hydrogen transfer occurs at 115/144 sites (79.9%); OOH desorption at 104/144 (72.2%). These are overlapping classifications, not additive categories. Only 8/144 sites contain a force-unconverged retained state, so force convergence alone does not explain or screen out the integrity problem. These fractions describe the enumerated sites of the historical pool, not a random sample of operating surfaces.

## Integrity-dependent ranking

Each value below is a minimum over qualifying sites among the same twelve CENSUS-1 sites per composition; it is not a DFT prediction or a resolved ranking. Values are descriptor-defined eta in V. “Excluded” means no site qualifies, not a numerical eta.

| Composition | All sites | Adsorbate-intact | Strict intact |
|---|---:|---:|---:|
| Ni31Cr29Cu5Mn35 | 0.439996 | 0.439996 | Excluded |
| Fe25Co25Ni25Cr25 | 0.453057 | 0.453057 | 1.272342 |
| Cu26Ni9Cr31Co33 | 0.479192 | 0.479192 | Excluded |
| Ni34Fe6Cu29Co31 | 0.725842 | 1.083496 | 1.083496 |
| Cu8Cr23Mn35Co34 | 0.755768 | 0.755768 | 0.755768 |
| Cu22Fe30Co32Mn15 | 0.795653 | 0.795653 | 1.209540 |

Adsorbate-integrity admission moves Ni34Fe6Cu29Co31 from fourth to sixth, with Kendall tau-a = 0.733333 against the historical six-composition order. The original top-three order survives this filter, but its 13.060 and 26.135 mV gaps are not thereby resolved. Strict integrity excludes two compositions, so no six-composition tau is assigned. Because reconstruction affects the historical winner and the equiatomic reference, strict exclusion must be reported alongside, not substituted for, the adsorbate-only reading.

The frozen `two_pathway` rule retains the original six-composition order. It filters the OOH endpoint label and reuses the retained four-step arithmetic; it is not independent validation of stable endpoints, a complete bridge mechanism, or its kinetics. The existing O2-fragment records enter only a diagnostic and change no ranking value. See [ranking.json](../../results/site_census_2026-09-06/readout_partial_2026-09-11/ranking.json).

## Completed model comparison

Every model below has 144 retained sites under the same composition/seed/site scope, with its own relaxed geometries. Differences therefore include both energy-model and endpoint-basin effects.

| Model | Strict-intact chains | Adsorbate-intact chains | Sites with unconverged states | OOH desorption |
|---|---:|---:|---:|---:|
| MPA-0 | 17 | 23 | 8 | 104 |
| OMAT-0 | 75 | 91 | 3 | 39 |
| MP-0 | 44 | 51 | 2 | 87 |
| MATPES-r2SCAN-OMAT-ft | 74 | 96 | 7 | 23 |

The four-model range of minimum eta spans 0.084149–0.759853 V across compositions. It is 0.136612 V for the historical leader and 0.551850 V for the equiatomic composition, compared with their 0.013060 V historical separation. These ranges demonstrate model sensitivity, not calibrated error bars, independent ensemble uncertainty, or evidence that the model with the most intact endpoints is correct. Matched-coordinate DFT energies and forces remain necessary to distinguish those explanations.

## Remaining dependencies and compute priorities

CENSUS-3 remains incomplete and unequally sampled: the first four gated compositions have 120 sites each, Cu8Cr23Mn35Co34 has 60, and Cu22Fe30Co32Mn15 has 12. Their current minima must not be compared as equal-depth results. Finish the remaining blocks, then apply the fixed distribution and [rank-resolution readouts](2026-09-06-rank-resolution-spec.md), including all admission policies, decoration clustering, unresolved boundaries, and missing-data denominators. No final second-wave ranking or new preferred catalyst follows from this snapshot.

Keep major candidate-focused DFT relaxation, ranking-driven panel expansion, and mechanistic campaigns on hold until that interpretation is complete. Existing DFT analysis, reference verification, and bounded numerical/debugging work can continue in parallel because they do not require a newly selected winner. The unchanged twelve-chain validation pilot answers a separate transferability question: its composition/seed/site slots were fixed before new census outcomes, and completed CENSUS-1 supplies its coordinates. Preserve those slots and the four-composition held-out boundary; do not replace unfavorable or force-unconverged cases using the census. Its readiness is not an instruction to launch the remaining panel en masse. The next candidate-focused scope should address the observed integrity, reconstruction, and model-disagreement questions, with the full census uncertainty and measured DFT cost made explicit.
