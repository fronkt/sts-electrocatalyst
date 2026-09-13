# Census review — 2026-09-13

The banked six-composition order does not survive the prescribed census comparisons. Cu8Cr23Mn35Co34 has the lowest observed all-sites minimum; Cu26Ni9Cr31Co33 leads the all-sites mean and median. Admission policy and model choice materially affect the results, so the census supports no unique policy-independent or DFT-validated winner.

This is a post-hoc review of [docs/95](../95-census-2-3-readout-2026-09-13.md), using the unchanged full census and five B=10000, seed=0 rank outputs. The original automated report is preserved at `results/site_census_2026-09-06/review_2026-09-13/original/95-census-2-3-readout-2026-09-13.md` (SHA256 `fe0207639b6645bf35e85133a2cbe025307b3d996dbc463102f0bd14e41d61e4`). Original follow-through pins describe that snapshot; the reviewed docs/95 adds a notice linking here. Its tables and numerical outputs remain unchanged.

## Verification

All 145 pinned source/input/history files, 103 raw result files and 12 emitted outputs matched their recorded SHA256 before review changes. All eight stages returned 0. The full readout covers 103/103 manifests, with no missing results. Independent reconstruction checked 1,231 sites / 3,693 retained geometries, every CSV field against JSON, all CHE overpotentials, 186 distribution values, twelve model spreads and the timing sums. No numerical discrepancy was found.

All six gated banked values reproduce within 4e-8 V. Across the wider twelve-composition historical set, 11/12 reproduce at 1e-6 V; Cr33Co5Ni29Cu33 differs by +0.0021007795 V, as already reported. These are distinct reproduction populations.

## Corrections to the automated report

**Merged declaration metadata:** T1 in each of the five policy sections incorrectly carries the first result batch's declaration of 3 decorations / 12 total sites. Each gated composition actually declares ten disjoint batches, or **30 decorations / 120 total sites**, matching the observed counts. No stems are missing: full coverage is complete. The column's “decorations x sites” label is also misleading because the second number is a total, not sites per decoration. These are reporting defects. The bootstrap uses the actual usable-decoration arrays, correctly 30 under all-sites admission. The CLI fix aggregates each distinct source's declarations and retains missing-site detection; the original rank files are preserved as the inputs to this review.

**Directory references:** Current full-census statistics in docs/95 come from `readout_full/`; rank-resolution JSONs come from `readout/`. References to the historical docs/93 readout and quoted frozen commands retain their original literal paths. The broad shorthand sentence near the end of docs/95 must be read with these exceptions.

**Cost:** 1,744,845.943 seconds / 484.68 hours is the sum of retained candidates' recorded elapsed durations. It is not measured CPU/core-hours or a complete accounting of abandoned work. Suspension may affect elapsed durations. The 144.11-hour first-launch-to-last-exit window includes downtime. No numeric timing table changes.

## What the rank results support

| Composition | All-sites minimum, V | Seed / site |
|---|---:|---|
| Cu8Cr23Mn35Co34 | 0.362219538 | 20 / 2 |
| Ni31Cr29Cu5Mn35 | 0.439996064 | 1 / 0 |
| Cu26Ni9Cr31Co33 | 0.449168494 | 5 / 2 |
| Fe25Co25Ni25Cr25 | 0.453056552 | 2 / 0 |
| Cu22Fe30Co32Mn15 | 0.455948791 | 15 / 0 |
| Ni34Fe6Cu29Co31 | 0.607166077 | 13 / 2 |

This observed order has Kendall tau-a 0.2 against the banked order. No composition retains its original banked rank with frequency at least 0.95 in the primary all/min bootstrap. That statement does not extend to every statistic: under all/p10, Cu22 retains its original sixth rank with frequency 0.9684.

Cu8 ranks first in all 10,000 recorded all/min replicates; the old leader ranks first in none. These are Monte Carlo frequencies conditional on the observed decorations, six compositions, one model and one admission rule. The reproducible audit at `results/site_census_2026-09-06/review_2026-09-13/exact_min_bootstrap_audit.mjs` evaluates the finite empirical distributions directly and pins its input. Independent exact enumeration of the empirical minimum distributions gives Cu8 probability 0.9999101754 and the old leader 0.0000583505. All 10,000 Cu8 wins is therefore plausible (probability about 0.4073 under that empirical model). Eight distinct Cu8 decorations contain sites below every rival's observed minimum. This is strong observed lower-tail separation, while resampling observed data cannot reveal better unseen competitor sites. The frozen specification already labels extrema-bootstrap uncertainty descriptive.

Two of the five original adjacent boundaries are RESOLVED and two INVERTED for all/min. The labels have different criteria: RESOLVED requires preserved-order frequency at least 0.95, whereas INVERTED requires only an observed nonpositive gap. Fe25 → Cu26 is a point-order inversion whose 90% gap interval crosses zero (−0.093923 to +0.026135 V). Eleven of twenty boundary/statistic verdicts change across admission policies; these twenty are five original neighbours times four statistics, not twenty independent candidate pairs.

Admission filtering changes both the eligible structures and the available sampling depth. Cu8 has only four strict-intact sites across three usable decorations, versus 120 sites / 30 decorations under all; its strict-intact minimum rank-1 frequency is 0.0102. The all-sites winning structures of both Cu8 and the old leader fail strict integrity because their O state reconstructs, while remaining adsorbate-intact. Secondary-policy bootstrap conditions on usable decorations and does not account for uncertainty in the frequency of unusable decorations.

The original twelve-site draw strongly affects the banked minima. Cu8 improves from 0.755768 to 0.362220 V with expanded sampling; the original top two minima remain their best among all 120 sites. “Lucky/unlucky” is an informal description of this sensitivity, not an estimated population luck probability. The expected twelve-site minimum in the distribution output averages twelve individual sites sampled without replacement; it is neither the median draw nor a sample of three whole decorations.

## Research implications

First resolve endpoint chemistry and reconstruction for the relevant low-eta structures, and examine why model and integrity-policy conclusions disagree. Preserve the energy-blind pilot selection independently of favorable new minima. The existing pilot/DFT evidence and its acceptance criteria remain separate; this review does not authorize a new compute campaign or substitute the census order for a validated electrode ranking.

Review disposition: descriptive census calculations accepted with the metadata/path/cost errata above. The historical follow-through status remains READY_FOR_REVIEW with scientific_approval false, documenting its automated stopping point; this dated review records the subsequent assessment without changing that receipt.
