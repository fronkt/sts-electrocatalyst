# Independent review of the S8 ranking proposal — 2026-09-19

The completed census supports a descriptive comparison of model-specific site distributions. It does not yet support the proposed physical explanation for p10, a validated alloy-performance ranking, or a melt selection. Keep the September 16 S8 disposition: computational validation and experimental feasibility continue; selection and prediction freeze remain open. The proposal is useful as a record of candidate rules explored after inspecting the census, subject to the corrections below. No new scientific rule or threshold is adopted here.

## 1. Separate a thermodynamic descriptor from current

The statement that measured fixed-current overpotential is set by a Tafel-weighted sum of the census site overpotentials is unsupported. The census eta is a CHE thermodynamic descriptor based on intermediate energies. It supplies neither transition-state barriers nor site-specific kinetic prefactors, coverages, accessible site densities or transfer coefficients. Thermodynamic potential-limiting and kinetic rate-limiting steps need not coincide; an adsorption-energy descriptor does not by itself determine current. [Razzaq and Exner, ACS Catalysis 2023](https://pubs.acs.org/doi/10.1021/acscatal.2c03997).

For illustration only, if independent site classes had measured kinetic laws `j_i(U) = a_i exp[(U-u_i)/b]` with a common slope parameter b, total current would contain the weighted sum `sum_i a_i exp(-u_i/b)`. Even under these restrictive assumptions, a fixed-current potential depends on the abundances/prefactors a_i and on the whole distribution. It is not generally the minimum or a fixed percentile. Here u_i cannot simply be replaced by the calculated thermodynamic eta without an additional, validated mapping. This is a mathematical counterexample to the proposed inference, not a new kinetic model for the samples.

A relevant complex-solid-solution study explicitly considers both site activity and site abundance when adding current contributions. Its experimental test is ORR on nanoparticles, so it motivates examining distributions but does not validate a 10th-percentile OER rule for an alloy button. [Löffler et al., Angewandte Chemie 2020](https://doi.org/10.1002/anie.201914666).

There is a second transfer problem. `screen_diagnostic.py` fixes a 2×2 rutile surface (lines 75, 132 and 256), with four sampled cus sites per decoration. S8 concerns prepared and activated polycrystalline alloy buttons. The correspondence between the model rutile surface and the operating oxidized surface is unestablished. Bulk alloy composition or bulk XRD alone does not identify which surface sites carry OER current. Consequently p10 may be retained as an explicitly exploratory model descriptor, not as a physically derived prediction of overpotential at a specified measured current. Do not substitute a fabricated Tafel slope or assumed site density to create that mapping.

## 2. Admission changes the population being ranked

Equal initial sampling is real: each of the six compositions has 120 MPA-0 site records over 30 decorations. Equal retained count is false. The proposal's rule should identify its population as `eta conditional on all_states_adsorbate_intact in this model`, and report retained count and supporting decorations alongside it.

| Composition | Initially sampled | Adsorbate-intact | Strict-intact |
| --- | ---: | ---: | ---: |
| Cu22Fe30Co32Mn15 | 120 | 38 | 33 |
| Cu26Ni9Cr31Co33 | 120 | 13 | 6 |
| Cu8Cr23Mn35Co34 | 120 | 16 | 4 |
| Fe25Co25Ni25Cr25 | 120 | 19 | 11 |
| Ni31Cr29Cu5Mn35 | 120 | 8 | 3 |
| Ni34Fe6Cu29Co31 | 120 | 15 | 15 |

The proposal's strict range of 3–15 is therefore incorrect; it is **3–33**. The phrase “all three adsorbates retained” is also incomplete: `site_integrity.py:283–288` requires force convergence, no dissociation, no migration and no desorption. The adsorption-only policy ignores the reconstruction flag and admits the inherited weak-binding tier. These are operational model classifications, not experimentally established active-site membership.

Unequal retained sample sizes do not make conditional quantiles mathematically incomparable. They change precision and highlight that different fractions of the original ensembles enter each estimate. Equalizing them by discarding good records would not solve conditioning on model validity. A composition with only a few admissible favorable sites can lead the conditional distribution while having a small admitted fraction; conversely, invalid classifications may reflect model failure rather than truly inactive sites.

Report the conditional distribution together with admission yield and the fraction `number(admitted and eta < 0.6 V)/120`. The latter is an **admitted low-descriptor fraction**, not an experimental active-site fraction; treating every rejected site as physically inactive would be another unsupported assumption. The proposed diagnostic calculation records both denominators without choosing a combined utility or changing the 0.6 V reporting threshold.

“Policy-robust” is the wrong label for leading several statistics within the adsorption-only policy. That is within-policy statistic stability. The policies themselves disagree. Similarly, “neither is wrong” overstates the physical standing of the all-sites distribution: it includes formal CHE values from chains that fail the intact-pathway checks. Its statistics remain useful diagnostics, but cannot have the same physical interpretation as an intact conventional pathway.

## 3. State the quantile definition and effective tail support

`s8_ranking_statistics.py:34` uses NumPy's default linear percentile method. It is not the twelfth-lowest of 120 observations. With one-based sorted values, `p10 = 0.1*x[12] + 0.9*x[13]` at n=120. NumPy documents `linear` as its default; the independent diagnostic uses the same convention explicitly. [NumPy percentile documentation](https://numpy.org/doc/stable/reference/generated/numpy.percentile.html).

After admission, Cu8 has n=16, so p10 is halfway between its second and third observations; Ni31 has n=8, so it is 30% of the minimum plus 70% of the second observation. Thus this rule can still depend on one or two decorations. A quantile is less extreme than the minimum in a large sample, but that alone does not establish robustness in these small retained samples. Pin `method='linear'`, report the bracketing values and seed/site identities, and check leave-one-decoration influence. A nearest-rank quantile would be a different statistic and should not silently replace this one.

## 4. Correct the ranking and bootstrap interpretation

Resampling complete decorations is a sensible way to retain dependence among four sites sharing a slab and clean reference. The new script resamples all 30 observed decoration clusters, including clusters with no admitted sites; this differs from the older secondary-policy bootstrap described in the September 13 census review, which conditioned on usable decorations. The two sets of frequencies must not be conflated.

There are two consequential implementation problems:

1. **Exact ties are broken by composition name.** `order_by()` at lines 61–63 uses stable sorting, and composition order is alphabetical at line 77. In the strict `share_below_0.6V` row, Cu26 has one qualifying site and the other five compositions have zero. Nevertheless the original output gives the zero-share Cu22 `P(rank<=2)=1.0`, because it wins the alphabetical zero-share tie. Its scientific rank is tied across positions 2–6 when Cu26's positive site is present, and tied across all six positions when that site is absent. Report tie groups and best/worst rank intervals, or adopt an explicitly declared tie-credit convention before using rank frequencies. The same defect affects printed total orders, Kendall comparisons and cross-model leader agreement for tied statistics.

2. **An empty composition disappears from the race.** Lines 117–124 assign None to a bootstrap sample with no admitted sites and remove it before ranking. The global denominator increases whenever any composition remains. The output therefore is not a probability that a composition has a particular rank in a fully defined six-composition ranking. With k nonempty decorations among 30, the empirical probability of an empty draw is `((30-k)/30)^30`. Record this missingness, the all-six-defined frequency and the comparison population. Do not silently classify undefined samples as ordinary losses, and do not claim a rank against an absent competitor is a resolved six-way comparison.

The independent review script provides tie-aware descriptive intervals and exact empirical empty probabilities; it does not replace the historical bootstrap outputs. A corrected bootstrap, if later needed, must keep its denominator and tie policy explicit and preserve the original results.

All bootstrap frequencies remain conditional on six selected compositions, the observed random-decoration construction, one fixed model and one integrity rule. They are not posterior probabilities of the true physical ranking, do not include unseen competitor sites or ML potential error, and do not cover the post-result choice among statistics/policies. Shared model and reference errors are not independent decoration noise. Numeric seed equality across different compositions is not enough to establish a paired physical sampling unit; the influence calculation omits one decoration in one composition at a time and holds the others fixed.

The displayed `1.00` is rounded: adsorption-only p10 rank-one frequency is 0.9973 in the JSON. Keep sufficient precision and evaluate any eventual threshold on unrounded values. The original script stores rank-one/top-two frequencies, not bootstrap intervals for p10, minimum and median; those intervals cannot be cited as already available from it.

## 5. Existing DFT and cross-model checks answer narrower questions

The nine-leg primary array comprises clean slab, reconstructed O start and unlifted O start at three selected Cr sites. The launch record explicitly states that no overpotential or composition ranking follows from those legs alone. It does not relax OH and OOH chains at all low-tail observations, determine their transition pathways, estimate the frequency of the motif, or validate the complete conditional p10 distribution. A surviving short Cr–O endpoint is useful evidence about that structural response; it cannot close the proposed full-pathway validity gate by itself. A failure similarly cannot erase every reconstructed site in every composition by analogy.

The sentence predicting that removal of the Cu8 reconstructed tail necessarily makes Cu26 lead both policies requires an explicit counterfactual calculation and a precisely defined removal rule; it is not established by the present tables. Any such calculation would be a sensitivity scenario, not a factual reclassification. The current full strict p25 point estimate even places Cu8 first, although Cu26 has the largest bootstrap rank-one frequency; distinguish the observed leader from the most frequent bootstrap leader.

The four-model twelve-site comparison uses shared initial site identities before filtering, but each model admits a different subset. For the adsorption-only rule, MPA-0 retains only one site each for Cu8 and Cu26 at twelve-site depth, whereas OMAT-0 retains eleven and five. Thus a filtered cross-model leader comparison combines energy differences, geometry changes, admission differences and unequal retained depth. Report these separately; a common-admitted-identity sensitivity analysis is possible if any adequate intersection exists, but would answer a narrower conditional question.

The selected-minimum cross-model follow-up reviewed on September 16 is additional evidence, not another unbiased census. It supports recurrence of the short contact while full-pathway integrity still differs. Neither agreement among related potentials nor one more 120-site model census guarantees physical correctness. The immediate priority remains the stated structural tests and accounting of what they do and do not validate, rather than converting model votes into a validation gate.

## 6. Thresholds, sample roles and comparator require a prospective protocol

The p10 choice and `P(rank<=2) >= 0.80` threshold appear after inspecting all the candidate results. They can be proposals for a future frozen selection policy, but are not independent confirmation on this census. No physical loss function or calibrated error rate presently justifies 0.80, and passing a top-two frequency threshold does not establish rank one or pairwise separation. Freeze the intended endpoint, failure handling, admission/quantile/tie definitions and validation design before later experimental outcomes; label this current comparison exploratory.

The “conservative second” label for a strict-intact leader is not established: excluding all reconstruction may discard real chemistry, and its retained samples are thin. Likewise a banked “poor anchor” is an intended design role, not proof of poor experimental activity. The final sample-role rule needs an overlap policy if the primary and conservative leaders are the same composition, and must specify how an unevaluable candidate is handled without opportunistically substituting a new favorite.

The September 16 disposition calls for matched poor-anchor/IrO2 benchmarks. The proposal's “IrO2 or NiFe-LDH” changes that comparator without a dated decision. Preserve the current IrO2 requirement unless a subsequent protocol explicitly changes it. NiFe-based materials cannot be treated as interchangeable with IrO2 across unspecified electrolyte conditions. A primary benchmarking study tests activity, stability and Faradaic efficiency under defined conditions and shows that catalyst comparisons depend materially on acidic versus alkaline media. [McCrory et al., JACS 2013](https://pubs.acs.org/doi/10.1021/ja407115p).

Specify the electrolyte, preparation/activation, current normalization, resistance treatment, independent material batches, replicate measurements, operating stability and oxygen-product check in the eventual materials-performance comparison. This defines the endpoint and uncertainty; it does not turn a calculated thermodynamic descriptor into a measured fixed-current overpotential. A frozen ordinal hypothesis may be testable as a discovery-loop prediction even when numerical equality is not claimed.

## Bounded next calculation and review disposition

`src/scripts/s8_ranking_review.py` reads the unchanged CSV and existing ranking JSON. It validates the 30×4 identity grid and source hash, independently checks all 18 point p10 values, records retained-site/decoration counts, empirical empty-draw probabilities, both low-descriptor denominators and tie groups, and evaluates 180 leave-one-decoration-out cases for adsorption-only p10. It writes a new `independent_review/diagnostics.json` and refuses an existing output. Six focused tests cover interpolated quantiles, tied site support, undefined quantiles/ranks, alphabetical tie invariance and empty-cluster probabilities. The isolated-background run completed all 18 p10 checks and all 180 influence cases; all six focused tests passed. The original proposal, calculation and result files remain unchanged.

Accept the census as descriptive evidence. Correct the physical inference, population labels, quantile wording, strict sample-count range, tie/undefined-rank handling and DFT/comparator scope before adopting an S8 rule. No additional model census, melt selection or physical-performance claim is authorized by this review.

### Inputs reviewed

- Proposal: `docs/research/s8-ranking-statistic-proposal-2026-09-19.md`, SHA256 `7fa1f3e3577bcdbee52e81245144053c1bf4e19c29a6daba0e0591600911548f`.
- Original script: `src/scripts/s8_ranking_statistics.py`, SHA256 `f0a9772380665b9cc10c1caf27067ec3fc8e0baa882c682214c08b28301b983e`.
- Original ranking JSON: `results/s8_ranking_statistic_2026-09-19/ranking_statistics.json`, SHA256 `e3a6c6565f91eaf8e33d0751ef80867d721d50f7b3c0ecb8bb5fddf9841de440`.
- Census CSV: `results/site_census_2026-09-06/readout_full/per_site.csv`, SHA256 `cae673682a7ee204fd128de08bd67657f4222e8f97146ef49fdbfb5a5d64e073`.

Supporting local records: `census-review-2026-09-13.md`, `census-cross-model-review-2026-09-16.md`, `research-decisions-2026-09-16.md`, `lowtail-primary-launch-2026-09-18.md`, `src/hea_oer/site_integrity.py` and `src/scripts/screen_diagnostic.py`. External sources above support only the claims beside their links; they do not determine a new selection rule.

## Completed independent diagnostics

The strongest positive finding survives a direct influence check: **Cu8Cr23Mn35Co34 remains the adsorption-only p10 leader in all 180 one-composition-at-a-time leave-one-decoration-out cases.** Omitting its own decorations changes p10 only from 0.381902 to 0.386624 V, around the full value 0.383548 V. This supports stability to deletion of any one observed decoration under this exact model/policy/statistic. It does not test another model, an unseen decoration, an admission reclassification or the physical electrode.

The p10-supporting Cu8 observations are Cr seed16/site2 at 0.380804 V and Cr seed26/site1 at 0.386293 V, with equal interpolation weight. Both have NORMAL OH/OOH and RECONSTRUCTION O in the unchanged census. The current DFT target is seed20/site2, the minimum, rather than either p10 bracketing site. A result at that minimum informs the motif hypothesis but cannot be described as direct validation of the two p10 supports.

| Composition | Adsorption-only retained / nonempty decorations | Admitted eta <0.6 V / all 120 | Adsorption-only empty-bootstrap probability | Strict nonempty decorations / empty probability |
| --- | ---: | ---: | ---: | ---: |
| Cu22Fe30Co32Mn15 | 38 / 25 | 0 / 120 | 4.52e-24 | 23 / 1.09e-19 |
| Cu26Ni9Cr31Co33 | 13 / 11 | 3 / 120 | 1.12e-6 | 5 / 0.004213 |
| Cu8Cr23Mn35Co34 | 16 / 11 | 10 / 120 | 1.12e-6 | 3 / 0.042391 |
| Fe25Co25Ni25Cr25 | 19 / 12 | 3 / 120 | 2.21e-7 | 9 / 2.25e-5 |
| Ni31Cr29Cu5Mn35 | 8 / 7 | 3 / 120 | 0.0003453 | 3 / 0.042391 |
| Ni34Fe6Cu29Co31 | 15 / 13 | 0 / 120 | 3.98e-8 | 13 / 3.98e-8 |

These exact empty probabilities refer to the empirical 30-draw decoration bootstrap, not failure probabilities for real samples. Empty draws are uncommon in the adsorption-only policy (largest 0.03453%) but material for strict Cu8/Ni31 (4.2391% each). They do not explain away Cu8's adsorption-only tail lead. They do require explicit bookkeeping when interpreting the sparse strict-policy frequencies.

Cu26's own-decoration deletion p10 spans 0.479192–0.599084 V and its rank spans 3–4; Ni31 spans 0.468273–0.586668 V with rank 2–4. The evidence distinguishes the stable observed Cu8 lead from the less stable ordering among its rivals. These are deletion-sensitivity ranges, not confidence intervals.

The unconditioned reporting denominator also retains Cu8's observed advantage: 10 admitted low-descriptor sites out of 120 (8.33%), versus 3/120 (2.50%) for Cu26, Ni31 and Fe25. This prevents its 62.5% conditional fraction from being read as 62.5% of the original sampled sites. No rejected site is reclassified as physically inactive, and no new selection score follows.

Tie-aware strict conditional-share ranks place Cu26 first and the five zero-share compositions tied across ranks 2–6. Thus the historical Cu22 top-two frequency of 1.0 is a sorting artifact, not a scientific finding about the poor anchor.

Evidence: `results/s8_ranking_statistic_2026-09-19/independent_review/diagnostics.json`, SHA256 `cd381f1bea14a6dfd2f66ffa58b74df4f21b05425e9f8f1f0d59cd848fd263c3`. Diagnostic script SHA256 `f9d25781feb53fdf0f1ad6d9ba3e7850cc5c0e17c5587f24b5d65d053ab21c00`. The file records every bracket identity, raw tie, undefined comparison population and deletion case. Commands: `python -m pytest tests/test_s8_ranking_review.py -q` and `python src/scripts/s8_ranking_review.py --out results/s8_ranking_statistic_2026-09-19/independent_review`.
