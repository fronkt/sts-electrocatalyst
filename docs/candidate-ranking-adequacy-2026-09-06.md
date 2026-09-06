# Candidate ranking adequacy — 2026-09-06

The present list is a hypothesis-generating ranking of imposed rutile models. An adequate selection system must demonstrate which comparisons it can support, preserve the evidence behind them, and improve decisions on compositions unavailable during tuning. Reproducible numerical results alone do not establish this transfer.

This review continues from Anvil banking commit 571695a. It does not elect S8, replace a frozen prediction, or supply a student submission. The current alkaline target is retained pending any explicit change.

## What the current data actually support

The screen contains 12 compositions, each summarized over 3 decorations and 4 sites. Six winning chains have no stored desorption flag. The stability join attaches equilibrium Pourbaix annotations; it applies no dissolved-fraction acceptance threshold. Neither these annotations nor the empirical formability filter establishes retained electrode mass, lifetime, or an achieved phase.

The top three model scores all depend on Cr-containing winning sites. Adjacent score gaps are:

| Nominal comparison | Gap (mV) | Critical common independent half-width (mV) |
|---|---:|---:|
| Ni31Cr29Cu5Mn35 vs Fe25Co25Ni25Cr25 | 13.060 | 6.530 |
| Fe25Co25Ni25Cr25 vs Cu26Ni9Cr31Co33 | 26.135 | 13.068 |
| Cu26Ni9Cr31Co33 vs Ni34Fe6Cu29Co31 | 246.650 | 123.325 |
| Ni34Fe6Cu29Co31 vs Cu8Cr23Mn35Co34 | 29.926 | 14.963 |
| Cu8Cr23Mn35Co34 vs Cu22Fe30Co32Mn15 | 39.885 | 19.943 |

These are model-score comparisons, not measured overpotentials. If every candidate error were independently bounded by +/- b, a strict pair ordering would require gap > 2b. Equality permits a tie. A shared scalar score bias cancels; shared OH/O/OOH corrections must instead pass through CHE and the site-selection calculation.

Thus a complete six-way order requires a demonstrated bound below 6.53 mV under that error model. A coarse top-three/bottom-three separation requires a bound below 123.32 mV. **Neither bound is established.** They quantify the evidence required, not the evidence already held. The top three can all be first under hypothetical +/-25 mV errors. That supports reporting an unresolved set under that scenario rather than inventing a unique winner.

The historical validation MAE is 129.56 mV against the embedded tier-v1 targets. Applying the same seven predictions to the tier-v2 nominal values gives 99.59 mV. Co and Ni retain bounded-reference semantics, including Ni's open upper bound. These seven endmembers informed model selection; the rescore supplies no new held-out validation. A lower MAE against changed targets is not evidence of improved physical prediction. Model-selection bias is an established reason to keep final evaluation separate from tuning: [Cawley and Talbot, 2010](https://www.jmlr.org/papers/v11/cawley10a.html).

MAE is not a per-candidate error limit, and site standard deviation is not a confidence interval. The earlier phrase "one resolvable boundary" should be read as **one much larger nominal gap** until pairwise errors are measured. Equal sampling depth removes one comparability problem but does not validate ordering across unequal site distributions.

The banked melt list and the current selector also differ: the current corrected spacing rule replaces Cu26Ni9Cr31Co33 with Ni34Fe6Cu29Co31. The audit reports both; neither is adopted here.

## Implemented now

- The screening backend retains every site's seed, index, coordinates, three adsorption free energies, eta/PLS, winning starts, distances and desorption flags. Each decoration retains realized cation counts/fractions and its relaxed clean slab.
- Winning relaxed adsorbate structures retain symbols, positions, cell, periodicity and fixed-atom indices. Cached constrained forces supply a numerical force check without requesting another model evaluation. Missing or stale forces stay unknown. Other constraint types are identified rather than assumed restartable.
- The legacy winner and aggregation rule are unchanged. A desorbed or unconverged winner is not silently replaced by a more convenient start. The retained evidence now permits a separately specified acceptance policy and an audit of alternatives.
- The ranking sensitivity helper reports all pair gaps, strict partial orders and possible ordinal positions for explicit hypothetical error budgets. It never substitutes MAE or site spread for a calibrated bound.
- The dataset audit checks CHE reconstruction, source/gated consistency, reference drift, selection-version drift and site-data availability. If full site records exist, it computes leave-one-decoration-out minimum sensitivity. That remains a sampling diagnostic, not experimental uncertainty.

The old R4 files and shards contain summaries rather than individual site energies/geometries. The added fields cannot reconstruct those missing historical records. A new screen realization is needed to obtain them, with the old screen retained as history.

## How to make the next ranking adequate

**1. Define the decision endpoint.** Continue with the current alkaline OER context unless it is explicitly changed. Specify a sustained operating point after a standardized activation and durability protocol. Compare matched IrO2 and NiFe benchmark electrodes using the same electrolyte, loading/area convention and resistance correction. Current alone can include oxidation or dissolution; oxygen/Faradaic-efficiency evidence is needed for an OER-advantage claim. Standardized comparative benchmarking has direct precedent in [McCrory et al., 2015](https://pubmed.ncbi.nlm.nih.gov/25668483/).

**2. Recover the model evidence before enlarging the search.** Re-realize a diagnostic subset with the new retention, including Cr-led, Co-led and Ni-dependent cases. Preserve all sites and numerical/chemical failures. Compare multiple starts and decoration removals. Select DFT checks across low-score and ordinary environments, not only the most favorable tail. Complete relevant chains or establish defensible bounds; if no physically valid adsorbed OOH minimum exists, record the branch as unresolved or inapplicable instead of forcing one or silently imputing a scaling value.

**3. Validate mixed compositions and complete protocols.** Keep every site, decoration and trajectory sibling of a held-out composition together. Use a fixed baseline and assess signed pairwise errors on the held-out mixed-site calculations. Pure-metal offsets cannot be assumed to transfer to arbitrary local alloy environments. Jointly propagate protocol choices across candidates and all retained sites; do not subtract a correction only from yesterday's winning motif if another site can become the winner. A shared-bias model should be tested, not assumed to cancel.

**4. Bridge precursor to the working electrode.** The physically relevant state may be a reconstructed (oxy)hydroxide. Operando observations and DFT demonstrate activated gamma phases and cooperative metal centers for NiFe/CoFe LDHs, without identifying the phase of these particular melts: [Dionigi et al., 2020](https://www.nature.com/articles/s41467-020-16237-1). Bulk XRD does not by itself identify a thin active shell. A new active-phase DFT comparison is scientifically useful but reopens MOOH physics currently cut from the program board; it requires an explicit scope decision.

A practical bridge can begin empirically: standardize precursor composition, processing and activation on exploratory samples, then compare a simple composition-plus-processing predictor with that same predictor augmented by DFT descriptors. The project need not solve every reconstruction mechanism before testing whether DFT helps select better electrodes.

**5. Freeze a genuinely prospective comparison.** Fit the precursor-to-surface mapping, if used, on exploratory samples. Freeze predictions for new compositions before fabrication. Feeding measured post-activation surface information from a held-out melt into a model is useful diagnosis, but cannot count as pre-melt selection. Evaluate paired ordering, useful selection improvement and the frequency of abstention. Use independent preparation/melt batches, with electrodes nested within batches; repeat scans do not supply independent material samples.

A mixed selection of promising and informative candidates is appropriate while uncertainty is unresolved. Sample count should follow observed between-batch variability and the useful performance difference; a small pilot alone does not justify narrow prediction intervals. Keep equilibrium stability, measured dissolution and sustained oxygen output as distinct quantities.

## Immediate sequence and scope

The two Anvil numerical arms are banked. The current independent task is to obtain trustworthy site-level evidence and a prospective validation design, while S1/S2 proceeds under its existing entrant-only boundary. The candidate-quality work does not require another Cr q-mesh refinement first.

S8 still needs the entrant's disposition, and its existing rule is top 2-4 after the re-rank gate, a predicted-poor anchor and same-bench IrO2. The diagnostic subset and active-phase/empirical comparisons above refine possible next work; they are not a new elected melt set. They become a prospective experiment only through the appropriate dated scope decision and freeze before any ingot.

## Reproduce the audit

The four input snapshots retain the contents of the original untracked R4 files, with CRLF normalized to LF. The audit records their hashes, the tracked reference-tier hash and implementation hashes. The source inputs and current code are enough to reproduce the diagnostic without a model download or new DFT:

    python src/scripts/ranking_adequacy.py --input-dir results/ranking_adequacy_2026-09-06/inputs --out results/ranking_adequacy_2026-09-06/audit-reproduced.json

Artifacts: results/ranking_adequacy_2026-09-06/audit.json and inputs/. Tests: test_ranking_sensitivity.py, test_ranking_adequacy.py, test_screen_site_records.py. Final verification is recorded in verification.json and the dated task review.
