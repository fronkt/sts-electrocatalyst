# Rank resolution of the R4 site census: pre-stated readout and worked power table (2026-09-06)

**Status.** Research input that accompanies the pre-registration docs/91-prereg-site-integrity-census-2026-09-06.md. It is not a docs/43 amendment; nothing here moves a banked number, licenses a deck, scores a prediction, or takes a body-figure row. It is written after the 2026-09-06 exploratory results existed (docs/candidate-ranking-adequacy-2026-09-06.md, docs/site-evidence-continuation-2026-09-06.md, docs/cr-site-chain-readout-2026-09-06.md and the retained chains under results/cr_site_chains_2026-09-06/, which section 6 uses as its fixture) and after docs/76:290 closed "any MLIP re-screen" in a document that states at docs/76:5 that it is not a registration; it therefore shares docs/91's standing as an explicit new research choice, not a continuation of anything licensed. The blind boundary is the commit that carries this file together with docs/91 and results/site_census_2026-09-06/MANIFESTS.sha256, recorded before any census process starts (the A12.R9 pattern, docs/43:3458-3466); the readout columns and the interpretation rules of sections 3-4 are fixed at that commit and are applied by the command of record to whatever the census returns. The worked power tables of section 5 are computed from banked values alone and are a result in their own right.

> [RANK-RESOLUTION BLIND BOUNDARY: commit ________ , dated ________ ; no result file existed under results/site_census_2026-09-06/results/ at that commit]

Implementation: `src/hea_oer/rank_resolution.py` (pure numpy/scipy; `ase` only for the neighbour count), CLI `src/scripts/rank_resolution_readout.py`, tests `tests/test_rank_resolution.py` (24 tests). Output of record once the census lands: `results/site_census_2026-09-06/readout/rank_resolution.json` plus the markdown tables on stdout, one file per admission policy and one `--compare` file. `results/` is gitignored wholesale (.gitignore:14; the trap docs/76:190-192 records for r4_melt_list.json), so each readout JSON is force-added with the readout commit, exactly as results/cr_site_chains_2026-09-06/ and results/ranking_adequacy_2026-09-06/ were, and its `sha256_lf` is recorded in the docs/93 readout.

## 1. Inputs of record

- **The banked screen**: `results/ranking_adequacy_2026-09-06/inputs/r4_screen_box.json` (12 rows; `n_sites` 4, `seeds` [0, 1, 2]; per row `eta` = the minimum over 12 sites, `eta_mean`, `eta_std` = population standard deviation over the 12 sites, `eta_max`, `bonds.seed`, `bonds.site_metal`, `desorbed`). No per-site record survives in that file (`src/scripts/screen_mace.py:126` strips `all_bonds`), which is why a census is needed at all.
- **The six gated candidates** in banked (ascending-`eta`) order, from `results/ranking_adequacy_2026-09-06/inputs/r4_gated.json`:

| rank | composition | eta (V) | eta_std (V) | eta_mean (V) | winning seed / metal / desorbed |
|---|---|---|---|---|---|
| 1 | Ni31Cr29Cu5Mn35 | 0.43999606379672596 | 0.3241490799729384 | 0.9103271635814684 | 1 / Cr / [] |
| 2 | Fe25Co25Ni25Cr25 | 0.4530565517906915 | 0.3285840051032546 | 1.046721011508203 | 2 / Cr / [] |
| 3 | Cu26Ni9Cr31Co33 | 0.4791918878366763 | 0.27299855829648617 | 0.9160231162663569 | 1 / Cr / [] |
| 4 | Ni34Fe6Cu29Co31 | 0.7258416193876736 | 0.19446118295446618 | 1.0010824005112011 | 2 / Ni / [] |
| 5 | Cu8Cr23Mn35Co34 | 0.7557679418652832 | 0.13523748906747102 | 1.0584795255004185 | 2 / Co / [] |
| 6 | Cu22Fe30Co32Mn15 | 0.7956532031025425 | 0.18412911957317757 | 1.0877867773988446 | 0 / Co / [] |

- **Adjacent gaps of the banked order** (V, from the `eta` column): 0.01306048799396553, 0.026135336045984836, 0.24664973155099723, 0.029926322477609624, 0.03988526123725933; in mV these are the 13.060 / 26.135 / 246.650 / 29.926 / 39.885 of `docs/candidate-ranking-adequacy-2026-09-06.md:15-19`, whose critical common independent half-widths are 6.530 / 13.068 / 123.325 / 14.963 / 19.943 mV. `docs/76-projector-generalization-decision-2026-09-03.md:166-168` states the same five gaps against the pipeline MAE of 0.0996 V and the per-site `eta_std` of 0.135-0.329 V as "exactly one resolvable boundary of five".
- **The same five pairs under the `eta_mean` column** (what the mean rule orders today, from the box alone): 0.1363938479267347, -0.13069789524184616, 0.08505928424484421, 0.05739712498921734, 0.02930725189842609 V. The second pair is INVERTED under the mean (Cu26Ni9Cr31Co33 has the lower mean). No box column gives a median or a 10th-percentile gap.
- **The census layout** (`src/scripts/site_census_plan.py:16-20, :119-120`; docs/91 §3): every result lands at `results/site_census_2026-09-06/results/<stem>_result.json`, one file per manifest, 103 stems in `results/site_census_2026-09-06/MANIFESTS.sha256` (12 `mpa0__<formula>`, 54 `mpa0_ext__<formula>__sNN-NN`, 12 each of `omat0__`, `mp0__`, `matpes__`, and `endmember_2x2__mpa0`; the twelve `mh1__` manifests were removed before the hash list was written, docs/91 §1). Four checkpoints score the same (formula, seed) pairs; a manifest's checkpoint is `model.filename` + `model.sha256_bytes`, never `model.historical_label`, which reads `medium-mpa-0` in every manifest (docs/91 §1 and §4 risk 6; lines 32 and 84 of the file as it stood at 22:53 on 2026-09-06, docs/91 being edited alongside this file).
- **The census schema** (`screen-diagnostic-v1`, as retained in `results/cr_site_chains_2026-09-06/{equiatomic,leader}_result.json`): top-level `manifest_id`, `manifest.model.{filename, sha256_bytes}`, `status`; `results[].row.per_site_records[]` with `seed, site_index, site_xy_A, dG_OH, dG_O, dG_OOH, eta, pls, bonds.site_metal, relaxed_states, initial_binding_metal(_index), desorbed`; `results[].row.decoration_records[]` with `seed, cation_counts, relaxed_slab{symbols, positions_A, cell_A, pbc}`. The planned census is 12 compositions x 3 seeds x 4 sites under MACE-MPA-0, later 27 more seeds for the six gated compositions (30 decorations, 120 sites each).
- **The fixture available today**: the two retained chains, one decoration and one site each: Fe25Co25Ni25Cr25 seed 2 site 0 (Cr, eta 0.4530565522419163 V, no desorption) and Ni31Cr29Cu5Mn35 seed 0 site 0 (Cr, eta 0.9780789066094675 V, OOH desorbed onto Ni). The equiatomic site reproduces the banked row within 4.512248352739334e-10 V; the leader site is not the banked seed-1 winner and differs from the banked row by 0.5380828428127415 V.

## 2. Definitions

- **Site row.** One record per (composition, seed, site) of one model file; a table in which one (composition, seed) carries rows from two model files, or two model files at all, is refused (`check_single_model`). A site is *admitted* under the primary policy `all` (the banked rule: every site counts, the legacy winner is retained regardless of quality). The secondary policies are the site sets of docs/91 readout (c), which names four rules (banked / intact-only / adsorbate-intact-only / two-pathway; docs/91 §2 (c), line 63 as it stood at 22:53 on 2026-09-06), as `src/hea_oer/site_integrity.py` defines them at readout time, and the definition in force is written into every readout JSON (`settings.admit_definition`): `no-desorbed` (no species' winning M-O distance reached the 3.00 A cut); `intact` (`all_states_intact`: OH, O and OOH all NORMAL and force-converged); `adsorbate-intact` (`all_states_adsorbate_intact`: not desorbed, not dissociated, not migrated, converged; the slab-reconstruction flag ignored); `two-pathway` (`pathway` in {cus, bridge}: the OOH state is *OOH or *O2+H_b; the site eta is the retained four-step value under either label, and the P-CENSUS-1b *O2 record is a diagnostic that enters no rule). No policy replaces a site eta. Every secondary readout is reported; none replaces the banked rule. Kendall tau-a of each census order against the banked order is reported per policy; docs/91 (c) reports the same tau for its own three rules from `site_census_readout.py`.
- **Composition statistic.** `min` (banked), `median`, `p10` (10th percentile, numpy linear interpolation), `mean`, over admitted sites.
- **Reproduction.** Per composition, the census `min` over every site of the banked seeds 0, 1, 2 (the cus eta, regardless of admission policy; the minimum decreases with the number of sites drawn, so the second wave's seeds 3-29 never enter this comparison) against the banked `eta`; the bar |difference| <= 1e-6 V is inherited from docs/91 readout (a) (docs/91 §2 (a), line 52 as it stood at 22:53 on 2026-09-06), not set here. The same rule of docs/91 (c) applies to the `min` statistic of T2: a 120-site minimum is not comparable to the 12-site banked one, and the min-rule rows of T2-T4 for the second wave are read as the rank statistics of that wave, not as re-screen values.
- **Cluster bootstrap.** B replicates with a fixed seed. Within each composition the D usable decorations are resampled with replacement; every site of a drawn decoration travels with it; the statistic is recomputed. Interval = central percentile interval at the stated level. With D decorations there are only C(2D-1, D) distinct resamples: 10 at D = 3, 5.9e16 at D = 30. Under `min` the bootstrap of an extreme is not consistent (Bickel and Freedman 1981), so its order frequencies are *descriptive*; under `mean`/`median` they are ordinary bootstrap estimates; under `p10` with fewer than ~50 sites the statistic is itself near-extreme (with 12 sites its numpy position is 1.1, the second-lowest site plus a tenth of the distance to the third) and the same caveat applies.
- **Rank-probability matrix.** P(composition i has rank r) over replicates, rank 1 best; pairwise P(stat_i < stat_j) with ties split; P(banked rank) per composition.
- **Adjacent-gap order probability.** For each adjacent pair (a, b) of the *banked* order, P(stat_b - stat_a > 0) over replicates, with the interval of the replicate gap and the observed gap under that rule.
- **Decorations needed.** Two compositions with i.i.d. normal site overpotentials, standard deviations (s_a, s_b) = the observed population site spreads, a location shift equal to the observed gap *under the rule in question*, n = 4 sites per decoration, target P. `mean`: N = (s_a^2 + s_b^2)(z/gap)^2, z = 1.6448536269514722 at 0.95, D = ceil(N/4), exact for normal sites. `min`, `median`, `p10`: the sample statistic is simulated exactly through the joint law of consecutive uniform order statistics (U_(k) ~ Beta(k, N-k+1); U_(k+1) | U_(k) = U_(k) + (1-U_(k)) Beta(1, N-k); David and Nagaraja 2003 §2.2) and the normal quantile transform, 20000 common random draws, scanned on a geometric grid of D up to 10000 and bisected; the same bisection at P +/- 2 binomial standard errors (0.0015 at 0.95) gives the *Monte-Carlo bracket* that is reported beside every simulated count, and a count is read as its bracket, not as an integer. The large-sample closed forms (quantile variance c sigma^2/N with c = pi/2 = 1.5707963267948966 for the median and 0.09/phi(z_0.1)^2 = 2.922109751150291 for p10; the Gumbel leading order log10 N = (z pi)^2 (s_a^2 + s_b^2) / (12 gap^2 ln 10) for the minimum, valid only for s_a = s_b) are carried as reference columns only. When s_a != s_b every order statistic other than the mean drifts with depth, so the order at depth is decided by the spread and not by the location: the flag `order_reverses_at_depth` is set whenever P at 10000 decorations falls more than 0.01 below the best P on the grid, whether or not a D was found, and a saturated search reports P(10000) and the best P on the grid.
- **Variance components.** One-way random-effects decomposition of site eta into within-decoration and between-decoration variance with the ICC (Searle, Casella and McCulloch 1992, section 3.6).
- **Ridge model.** The Svane and Rossmeisl 2022 construction: neighbour counts of each metal within the cutoff of the cus cation (periodic images counted; the distance ladder on the two retained slabs is 2.87-3.01 A for the chain partner, 3.42-3.60 A for six corner-sharing cations, then 4.36-4.38 A, so 3.8 A closes two shells), plus a one-hot of the centre metal, leave-one-out R^2 and residual sigma for targets eta, dG_OH, dG_O, dG_OOH. Below the site floor the fit is reported as `insufficient_sites`; below p + 2 = 14 sites as `underdetermined` with no coefficients.

## 3. The readout table, fixed now

Command of record, from the repository root, once every P-CENSUS-1 (and, for the second wave, P-CENSUS-3) stem has landed:

    python src/scripts/rank_resolution_readout.py --results results/site_census_2026-09-06/results/ --gated results/ranking_adequacy_2026-09-06/inputs/r4_gated.json --B 10000 --seed 0 --admit all --out results/site_census_2026-09-06/readout/rank_resolution.json

run once per admission policy (`--admit all` primary; `--admit no-desorbed`, `--admit intact`, `--admit adsorbate-intact`, `--admit two-pathway` secondary, each to its own `--out`, e.g. `rank_resolution_intact.json`), then

    python src/scripts/rank_resolution_readout.py --compare results/site_census_2026-09-06/readout/rank_resolution.json results/site_census_2026-09-06/readout/rank_resolution_intact.json ... --out results/site_census_2026-09-06/readout/rank_resolution_compare.json

Input guards, all fail-closed: only stems matching `--stems` (default `mpa0__*,mpa0_ext__*`, i.e. the MACE-MPA-0 P-CENSUS-1 and P-CENSUS-3 manifests; the endmember and ensemble stems are excluded) are read; a result whose `manifest_id` differs from `manifests/<stem>.json`, whose stem is absent from `MANIFESTS.sha256`, or whose status is not `complete`/`complete_with_errors` is refused and listed under `coverage.refused`; two model files in one table are refused (exit 2); when any expected stem of the selected set is missing the readout refuses to run unless `--partial`, and a partial readout carries `status: partial` with the missing stems under `coverage.missing`. Exit 3 with the message `insufficient decorations` if any composition has fewer than the minimum usable decorations; the census statistics are still written, no interval is invented.

| table | columns | rule |
|---|---|---|
| T1 census | composition, decorations (usable), sites (admitted), declared decorations x sites, bootstrap support C(2D-1, D) | coverage is complete when observed = declared for every composition and `coverage.missing` is empty |
| T2 statistics | composition, banked rank, banked eta, abs(census min - banked eta), reproduction verdict, then for each of min / median / p10 / mean: value [interval]; below it the census order per rule with Kendall tau-a against the banked order | see R7 |
| T3 rank matrix | composition x rank 1..K, E[rank], banked rank, label, for every rule | a rank is STABLE when P(banked rank) >= the target |
| T4 adjacent gaps | pair, rule, observed gap under that rule, P(order), gap interval, verdict, decorations needed [Monte-Carlo bracket] or the saturated report | see R1-R3 |
| T5 variance components | composition, sites, decorations, site sd (population), within sd, between sd, ICC | see R4 |
| T6 ridge | target, sites, status, R^2 in-sample, R^2 LOO, sigma in-sample, sigma LOO | see R5 |
| T7 banked reference | the five banked pairs x four rules: decorations needed on each rule's own banked gap (min: eta; mean: eta_mean; median/p10: no box estimate) and on a hypothetical shift equal to the banked min gap; the Gumbel column printed only for s_a = s_b | reproduces section 5 tables A and A' at readout time, seed 0 |
| T8 comparison (`--compare`) | pair, rule, verdict and P(order) under every policy, POLICY-DEPENDENT flag | see R6 |

## 4. Interpretation rules

These rules are fixed at the blind-boundary commit. Their numerical settings are elective and are listed separately below.

- **R1 (boundary verdict).** An adjacent boundary is RESOLVED under a rule when P(order preserved) >= the target in T4; UNRESOLVED otherwise. The screen is reported as "resolving k of 5 boundaries under the mean rule, k' under the median and k'' under the min rule", each on that rule's own observed gap. The min-rule count is labelled descriptive (section 2); the mean and median counts are the calibrated ones; the p10 count is labelled near-extreme whenever the admitted site count is below 50. No verdict is read from the point gap alone.
- **R2 (inversion).** If the observed gap under a rule is <= 0 the pair is reported as INVERTED under that rule, with no decorations-needed figure; the banked (min-rule) order stays the reference order of every table.
- **R3 (depth).** Decorations needed are reported at the target from the observed gap and the observed pair spreads, as a count with its Monte-Carlo bracket. A saturated search (no D <= 10000) is reported as "not resolvable by this statistic at <= 10000 decorations" together with P at 10000 and the best P on the grid; a pair whose P falls with depth (`order_reverses_at_depth`) is reported as SPREAD-DECIDED, under whichever rule it happens. All figures assume normal i.i.d. sites and are lower bounds on the depth under any heavier left tail.
- **R4 (clustering).** If any composition's ICC in T5 exceeds the ICC band, the i.i.d. site model behind R3 understates the depth and every decorations-needed figure for pairs involving that composition is reported as a lower bound; the between-decoration sd is then the quantity to sample down.
- **R5 (local composition).** The ridge fit is descriptive. It is reported only when status is `ok`; sigma_LOO at or above the pooled site sd is read as "nearest-neighbour composition does not explain the site spread"; no R^2 threshold is a success criterion.
- **R6 (policy dependence).** A boundary whose R1 verdict differs between the admission policies is reported as POLICY-DEPENDENT by the `--compare` readout, with every policy's P value (T8).
- **R7 (no movement).** No banked value changes. The census `min` over the banked seeds per composition is the reproduction check of T2 against the banked `eta` at the bar inherited from docs/91 §2 (a) (1e-6 V; the retained equiatomic site reproduces within 4.5e-10 V); a difference above the bar is reported as NOT REPRODUCED for that composition, not as a new number, and the composition stays in every table with that label.

**Elective settings (draft, not inherited).** None of the following values is taken from a source the readout cites: `docs/candidate-ranking-adequacy-2026-09-06.md:13-21` reasons with "gap > 2b", `docs/76:166-168` compares gaps with the MAE, and neither states a probability target, an ICC band or a site floor. Each value scores nothing, is applied only as an interpretation label, and may be re-authored by the entrant in a dated line before the command of record runs; the CLI flag beside each is where the elected value goes.

| slot | setting | draft value | flag |
|---|---|---|---|
| [RANK-1 order-probability target: ______] | P(order) at which a boundary is RESOLVED and a rank STABLE | 0.95 | `--target-prob` |
| [RANK-2 interval level: ______] | central percentile interval of the bootstrap | 0.90 | `--level` |
| [RANK-3 ICC band: ______] | ICC above which R4 applies | 0.2 | applied at reading |
| [RANK-4 ridge site floor: ______] | sites below which the ridge is `insufficient_sites` (p + 2 = 14 is the algebraic floor) | 30 | `RIDGE_MIN_SITES` |
| [RANK-5 neighbour cutoff: ______] | cation neighbour cutoff | 3.8 A | `--cutoff-A` |
| [RANK-6 ridge penalty: ______] | ridge alpha | 1.0 | `--alpha` |
| [RANK-7 minimum decorations: ______] | usable decorations per composition below which no interval is reported | 2 | `--min-decorations` |
| [RANK-8 replicates and seed: ______] | bootstrap B and seed | 10000, 0 | `--B`, `--seed` |
| [RANK-9 depth ceiling and reversal tolerance: ______] | grid ceiling of the decorations-needed scan; P drop that flags SPREAD-DECIDED | 10000; 0.01 | `max_decorations`, `REVERSAL_TOLERANCE` |
| [RANK-10 near-extreme floor: ______] | admitted sites below which p10 is labelled near-extreme | 50 | `P10_NEAR_EXTREME_SITES` |

Inherited, not elective: the reproduction bar 1e-6 V (docs/91 §2 (a)); the admission site sets (docs/91 §2 (b)-(c) through `site_integrity.py`); the banked order, gaps and spreads (section 1); n = 4 sites per decoration (the box's `n_sites`).

## 5. Worked power table from the banked values

Assumptions, all of them: site overpotentials i.i.d. normal within a composition with sigma = the banked population `eta_std`; the banked gap *under the rule in question* is the true location shift between the two compositions' site distributions (the min rule on the `eta` gaps, the mean rule on the `eta_mean` gaps; the median and p10 have no box gap and appear only under the hypothetical shift of table A'); no between-decoration variance (ICC = 0); n = 4 sites per decoration; target P = 0.95; simulated rules from 20000 common random draws with seed 0 (binomial standard error 0.0015 at P = 0.95; every simulated count carries its bracket), tables C and D from 200000 draws (0.0011 at P = 0.5); grid ceiling 10000 decorations. The `min` and `p10` figures test the left tail of a distribution whose right tail is known to be heavy (`eta_max` 1.2084361647422632-1.5299527848516243 V over the gated six), so they are the least robust entries here.

**Uncertainty of sigma.** Each `eta_std` is a population standard deviation of 12 sites (`src/hea_oer/adsorption.py:351`, ddof = 0). The chi-square 90 % interval on sigma from 12 sites (11 degrees of freedom, quantiles 19.67513757268249 and 4.574813079322224) spans x0.7809652937308015 to x1.6195857463859953 of the estimate, i.e. x0.610 to x2.623 on sigma^2; every decorations-needed figure scales with sigma^2, so a mean-rule count of 845 is 516-2216 across that band, and the band is printed beside every mean-rule count below as "(band lo-hi)". The counts are quoted as the code returns them so that T7 reproduces them; the band is the statement of precision.

**Table A. Decorations needed at 0.95, each rule on its own banked gap, pair-specific banked spreads (s_a, s_b), 4 sites per decoration.** "sat." = not reached at 10000 decorations; P(10000) and the best P on the grid are then given; "rev." = `order_reverses_at_depth`.

| pair (banked order) | s_a / s_b (V) | min-rule gap (V) | min [bracket] | mean-rule gap (V) | mean (band) |
|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | 0.3241 / 0.3286 | 0.013060 | sat., P(10000) = 0.489, best 0.516 at D = 1, rev. | 0.136394 | 8 (31 sites; band 5-21) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | 0.3286 / 0.2730 | 0.026135 | 790 [680, 912] (P = 0.9500) | -0.130698 | INVERTED |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | 0.2730 / 0.1945 | 0.246650 | 2 [2, 2] (P = 0.962) | 0.085059 | 11 (43 sites; band 7-28) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | 0.1945 / 0.1352 | 0.029926 | 17 [16, 18] (P = 0.951) | 0.057397 | 12 (47 sites; band 8-31) |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | 0.1352 / 0.1841 | 0.039885 | sat., P(10000) = 0.005, best 0.487 at D = 1, rev. | 0.029307 | 42 (165 sites; band 26-108) |

**Table A'. Decorations needed at 0.95 under a hypothetical location shift equal to the banked min gap, every rule** (exact simulation for min, median and p10, with the large-sample closed form in parentheses for reference; mean closed form with its sigma band). This table is what the earlier "every rule on the min gap" figures were; it is hypothetical for every rule but the min.

| pair | min [bracket] | mean (band) | median [bracket] (closed form) | p10 [bracket] (closed form) |
|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | sat., P(10000) = 0.489, rev. | 845 (band 516-2216) | 1331 [1284, 1375] (1327) | 7748 [7477, 8012] (2469) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | 790 [680, 912] | 181 (band 111-475) | 286 [274, 296] (284) | 38 [36, 39] (529) |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | 2 [2, 2] | 2 (band 1-4) | 2 [2, 2] (2) | 2 [2, 2] (4) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | 17 [16, 18] | 43 (band 26-112) | 67 [65, 70] (67) | 10 [9, 10] (124) |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | sat., P(10000) = 0.005, rev. | 23 (band 14-59) | 35 [33, 36] (35) | sat., P(10000) = 0.000, best 0.497 at D = 1, rev. (65) |

The p10 closed form is not calibrated at these depths: simulating P(order) at its own counts 2469 / 529 / 4 / 124 / 65 gives 0.824 / 1.000 / 0.997 / 1.000 / 0.179 instead of 0.95. With s_a != s_b the 10th percentile drifts with depth exactly as the minimum does (pair 5: P falls from 0.452 at 12 sites to 0.269 at 120 and 0.125 at 400), and with 12 sites it is a near-extreme order statistic. The Gumbel closed form for the minimum (log10 N = 1207.0, 258.2, 1.8, 60.5, 31.7 for the five pairs) assumes s_a = s_b and is not printed beside a simulated count in T7 unless the spreads are equal.

**Table B. Decorations needed at 0.95 with one common spread at each end of the gated range, hypothetical shift = the banked min gap.**

| pair | gap (V) | sigma = 0.1352: min | mean | sigma = 0.3286: min | mean |
|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | 0.013060 | sat., P(10000) = 0.607 | 146 (581 sites) | sat., P(10000) = 0.548 | 857 (3425 sites) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | 0.026135 | sat., P(10000) = 0.701 | 37 (145 sites) | sat., P(10000) = 0.589 | 214 (856 sites) |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | 0.246650 | 1 [1, 1] (P = 0.964) | 1 (2 sites) | 943 [666, 1533] (P = 0.950) | 3 (10 sites) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | 0.029926 | sat., P(10000) = 0.727 | 28 (111 sites) | sat., P(10000) = 0.602 | 164 (653 sites) |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | 0.039885 | sat., P(10000) = 0.786 | 16 (63 sites) | sat., P(10000) = 0.633 | 92 (368 sites) |

**Table C. P(order preserved) at the banked depth, 3 decorations x 4 sites = 12 sites per composition, pair-specific spreads.** Columns 2-3: each rule on its own banked gap (min simulated, 200000 draws; mean closed form). Column 4: the min rule with the mean-rule gap as the shift (what the minimum would do if the box's mean gaps were the true location shifts). Columns 5-8: every rule under the hypothetical min-gap shift.

| pair | min (own) | mean (own) | min at the mean gap | min (hyp.) | mean (hyp.) | median (hyp.) | p10 (hyp.) |
|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | 0.509 | 0.847 | 0.692 | 0.509 | 0.539 | 0.533 | 0.517 |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | 0.684 | 0.145 | 0.427 | 0.684 | 0.584 | 0.572 | 0.681 |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | 0.978 | 0.810 | 0.871 | 0.978 | 0.995 | 0.984 | 0.990 |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | 0.828 | 0.799 | 0.877 | 0.828 | 0.669 | 0.644 | 0.823 |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | 0.384 | 0.672 | 0.352 | 0.384 | 0.727 | 0.695 | 0.452 |

**Table D. P(order preserved) against depth (D = 3 / 30 / 100 decorations = 12 / 120 / 400 sites).** min on its own gap (simulated); mean on its own gap (closed form); mean and p10 under the hypothetical min-gap shift.

| pair | min (own) | mean (own) | mean (hyp.) | p10 (hyp.) |
|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | 0.509 / 0.504 / 0.500 | 0.847 / 0.999 / 1.000 | 0.539 / 0.622 / 0.714 | 0.517 / 0.543 / 0.576 |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | 0.684 / 0.833 / 0.890 | 0.145 / 0.000 / 0.000 | 0.584 / 0.749 / 0.889 | 0.681 / 0.930 / 0.996 |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | 0.978 / 0.999 / 1.000 | 0.810 / 0.997 / 1.000 | 0.995 / 1.000 / 1.000 | 0.990 / 1.000 / 1.000 |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | 0.828 / 0.972 / 0.991 | 0.799 / 0.996 / 1.000 | 0.669 / 0.917 / 0.994 | 0.823 / 0.998 / 1.000 |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | 0.384 / 0.179 / 0.099 | 0.672 / 0.920 / 0.995 | 0.727 / 0.972 / 1.000 | 0.452 / 0.269 / 0.125 |

Across the sigma band the mean-rule value at D = 30 on its own gap is 0.977-1.000 (pair 1), 0.000-0.019 (pair 2), 0.957-1.000 (pair 3), 0.949-1.000 (pair 4) and 0.807-0.964 (pair 5).

### What the tables say today

1. **At the banked depth the rules do not agree on which boundaries resolve, and only the min rule resolves one.** Under the min rule on its own gaps exactly one boundary reaches 0.95, Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 (0.978; the other four sit at 0.384-0.828), which is `docs/76:166-168`'s "one resolvable boundary of five" restated as a probability. Under the mean rule on its own gaps none does (0.847 / 0.145 / 0.810 / 0.799 / 0.672) and the second boundary is INVERTED (table A, R2). Only under the hypothetical shift of table A' would every rule resolve the same single boundary.
2. **The planned 3 x 4 census cannot change any of these verdicts**: it samples the same depth as the box (12 sites per composition), and table C is the expected outcome at that depth. Its value is the per-site record (which sites, which decorations, which failures, whether the banked minima sit on intact sites), not resolution.
3. **The min rule does not resolve small gaps at any depth, and is spread-decided at two of the five boundaries.** For Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 and Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 the min-rule P *falls* with depth (0.509 -> 0.500 and 0.384 -> 0.179 -> 0.099 at 12 / 120 / 400 sites; 0.489 and 0.005 at 10000 decorations) because the composition banked as worse has the larger site spread and the minimum of the wider distribution goes lower; both are SPREAD-DECIDED under R3. The two min-rule counts that do resolve (17 [16, 18] for the 29.9 mV pair, 790 [680, 912] for the 26.1 mV pair) are of the same kind with the sign reversed: the banked-better composition is the wider one, and the location shift is not what resolves them. With the box's own mean gaps as the shift the minimum orders the five pairs at 0.692 / 0.427 / 0.871 / 0.877 / 0.352 (table C column 4): the banked top three are a statement about spreads, not about which composition has the better sites.
4. **Under the mean rule on its own gaps the second wave (30 decorations, 120 sites) resolves the first, third and fourth boundaries (0.999 / 0.997 / 0.996), brings the fifth to 0.920 (42 decorations needed) and leaves the second inverted (0.000).** The mean-rule order of the gated six is therefore not the banked order, and what the census can settle at 30 decorations is that inversion, not the 13 mV min-rule gap. Under the hypothetical shift of table A' the same wave would leave the 13 mV and 26 mV boundaries unresolved (0.622 and 0.749), which is the statement the earlier draft made and which holds only for that hypothetical.
5. **The site spread is the lever.** Table B: at sigma = 0.1352 V the 26 mV gap needs 37 decorations under the mean; at 0.3286 V it needs 214. Whether the banked spreads are inflated by desorbed, migrated or reconstructed sites is exactly what the secondary admission readouts (R6) and the variance decomposition (R4) will show.
6. **The p10 closed form is not usable as a count.** Section 5 table A' and the calibration line under it: the exact count is 3.1x the closed form for the 13 mV pair and 0.07-0.08x for the 26 mV and 29.9 mV pairs, and the fifth pair saturates and reverses where the closed form says 65. Every p10 count in T4/T7 comes from the exact simulation; the closed form is a reference column.

## 6. What the two retained chains give today

Running the CLI on `results/cr_site_chains_2026-09-06/` with `--stems '*'` (the chain files are not census stems) returns exit 3 with `insufficient decorations: Fe25Co25Ni25Cr25 (1), Ni31Cr29Cu5Mn35 (1)`; the model is read from the payload manifests (`macempa0mediummodel`, sha256 75428afe3a1d7d8062e19bcaabd5c433623cabf308242ec9fb493e38604fb638); T2 carries the two single-site values (0.4531 and 0.9781 V) with REPRODUCED (4.512248352739334e-10 V) for the equiatomic site and NOT REPRODUCED (0.5380828428127415 V) for the leader site, which is the seed-0 site and not the banked seed-1 winner; no interval, no rank matrix; Kendall tau-a of the two-composition census order against the banked order is -1. Under `--admit intact` neither site is admitted (the O state of both is flagged RECONSTRUCTION by the classifier, free-atom maximum displacement 0.7991360510865592 A and 0.9520902671023659 A); under `--admit adsorbate-intact` and `--admit two-pathway` the equiatomic site is admitted (pathway `cus`) and the leader site is not (OOH DESORPTION, pathway `undefined`). The neighbour counts within 3.8 A of the Cr centre (index 16 in both slabs) are Co 4, Fe 4 (equiatomic, seed 2) and Ni 4, Cr 3, Cu 1 (leader, seed 0), eight neighbours each; the ridge fit is `underdetermined` (2 sites for 12 features; 14 needed, ~30 before it is meaningful). The variance decomposition reports `insufficient decorations` for both. T7 reproduces table A / A' for the first pair (the only adjacent pair present). All of this is the intended behaviour on one decoration. The command of record run today against `results/site_census_2026-09-06/results/` returns exit 2 (`no usable result JSON ... for stems ['mpa0__*', 'mpa0_ext__*']`), since no result has landed.

## 7. Reproduction

    python -m pytest tests/test_rank_resolution.py
    python src/scripts/rank_resolution_readout.py --results results/cr_site_chains_2026-09-06 --stems '*' --B 1000 --out <scratch>/rank_resolution.json   # exit 3

Tables A, A' and B are `hea_oer.rank_resolution.decorations_needed((s_a, s_b), gap, 4, rule, 0.95, rng_seed=0, n_sim=20000, max_decorations=10000)` over the five banked pairs (table A / A' is also the CLI's `banked_reference` block whenever the box snapshot is present); tables C and D are `order_probability(rule, gap, s_a, s_b, N, n_sim=200000, rng=numpy.random.default_rng(0))` at N = 12, 120, 400; the sigma band is `scipy.stats.chi2.ppf(0.95, 11)` and `chi2.ppf(0.05, 11)` with sigma_lo = sigma sqrt(12 / 19.675), sigma_hi = sigma sqrt(12 / 4.575). Simulated counts are Monte-Carlo calls and move within their brackets between random streams (an earlier stream gave 726 where the current one gives 790 [680, 912] for the second pair); the closed-form entries are exact.
