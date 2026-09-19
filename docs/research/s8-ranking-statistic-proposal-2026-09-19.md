# S8 ranking statistic — candidates on the completed census, and a proposal for the dated line (2026-09-19)

The S8 disposition of 2026-09-16 holds melt selection until, among other things, the composition-selection rule and its ranking statistic are defined and the actual predictions are frozen before any validation sample is prepared. The census of 2026-09-13 showed why: the six fully sampled compositions have different leaders under the minimum, the mean and the median, and the low tail contains reconstructed Cr sites and adsorbate loss. This note computes, with no new compute, how the six compositions order under six candidate statistics and three admission policies, with a decoration-level bootstrap for the stability of each order, and proposes one rule for the entrant's dated line. It selects no melt, freezes nothing and changes no census value.

Source: `results/site_census_2026-09-06/readout_full/per_site.csv` (MACE-MPA-0, 30 decorations x 4 sites = 120 sites per composition; the three other models at the shared twelve CENSUS-1 sites). Calculation: `src/scripts/s8_ranking_statistics.py`; tables and bootstrap in `results/s8_ranking_statistic_2026-09-19/` (B = 10,000 resamples of the 30 decorations, seed 0).

## Why the statistic matters physically

A measured overpotential at fixed current on a polycrystalline button is set by the most active accessible sites: the current is a Tafel-weighted sum over sites, so the low tail of the site distribution governs activity while the mean and median describe a typical site. The minimum is an extreme-value statistic: it depends on how many sites were sampled, and the census bootstrap showed the banked 12-site leader had P(rank 1) = 0.0 at 120 sites. A low quantile (the 10th percentile is the twelfth-lowest of 120 sites) keeps the tail meaning with less single-site fragility. The descriptor itself only has meaning on sites that keep the *OH, *O and *OOH chemistry intact; desorbed or reconstructed sites are either different chemistry or model artefacts, which is what the admission policies express.

## What the census says (MACE-MPA-0, 120 sites per composition)

Policy `all` (every site, n = 120):

| statistic | order (best first) | leader P(rank 1) |
|---|---|---:|
| min | Cu8Cr23Mn35Co34 < Ni31Cr29Cu5Mn35 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 < Ni34Fe6Cu29Co31 | 1.00 |
| p10 | Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Ni31Cr29Cu5Mn35 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 | 0.66 |
| p25 | Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 < Fe25Co25Ni25Cr25 < Ni31Cr29Cu5Mn35 < Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | 0.98 |
| median | Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 < Ni31Cr29Cu5Mn35 | 1.00 |
| mean | Cu26Ni9Cr31Co33 < Cu8Cr23Mn35Co34 < Ni34Fe6Cu29Co31 < Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 | 1.00 |

Policy `adsorbate_intact` (all three adsorbates retained; n = 8 to 38 sites):

| statistic | order (best first) | leader P(rank 1) |
|---|---|---:|
| min | Cu8Cr23Mn35Co34 < Ni31Cr29Cu5Mn35 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 | 1.00 |
| p10 | same order | 1.00 |
| p25 | Cu8 < Ni31 < Cu26 < Fe25 < Cu22 < Ni34 | 0.97 |
| median | Cu8 < Cu26 < Ni31 < Ni34 < Fe25 < Cu22 | 0.80 |
| mean | Cu8 < Cu26 < Ni31 < Ni34 < Fe25 < Cu22 | 0.90 |

Policy `intact` (strict integrity, n = 3 to 15 sites): Cu26Ni9Cr31Co33 leads under five of six statistics with P(rank 1) between 0.49 and 0.64; Cu8Cr23Mn35Co34 keeps only four sites and Ni31Cr29Cu5Mn35 three.

Cross-model check on the shared twelve sites: the four models name two to four distinct leaders under every statistic (four under the minimum). At twelve sites the ranking is model-dependent under every candidate rule; the 120-site result exists for MACE-MPA-0 only.

## Reading

- The leader flip reported in the census is a flip between tail statistics and central statistics under the `all` policy: the tail (min, p10, share of sites below 0.6 V) names Cu8Cr23Mn35Co34, the centre (p25, median, mean) names Cu26Ni9Cr31Co33, each with high bootstrap stability. They are answering different questions, and neither is wrong.
- Under `adsorbate_intact` the order is the one policy-robust order in the table: Cu8Cr23Mn35Co34 leads every statistic with P(rank 1) at least 0.80, and Ni31Cr29Cu5Mn35 or Cu26Ni9Cr31Co33 is second. The site counts are small (16 for Cu8, 8 for Ni31), and the Cu8 low tail is the reconstructed-Cr population whose DFT basin is exactly what array 20813525 is testing. If those sites turn out not to be adsorbate-intact basins in DFT, this policy loses the Cu8 tail and Cu26Ni9Cr31Co33 leads under both policies.
- Under strict `intact` almost nothing survives, and the surviving leader is weak. Strict integrity as a ranking policy is too thin at this sampling depth to rank anything.
- The cross-model disagreement at twelve sites is not resolved by any statistic. A ranking claim needs either a 120-site census under at least one more model or an explicit statement that the ranking is a MACE-MPA-0 result.

## Proposal for the dated S8 line (a draft; the rule is the entrant's)

1. Ranking statistic of record: the 10th percentile of the site overpotential over adsorbate-intact sites, at equal site count (120 sites per composition, MACE-MPA-0), reported beside the minimum and the median so the tail and the centre are always read together.
2. Stability gate: decoration-bootstrap P(rank at most 2) of at least 0.80 for any composition named as a leader.
3. Validity gate: the leader's low-tail site type must survive the DFT relaxation test as an adsorbate-intact basin before the leader is frozen. Until array 20813525 and any follow-up read out, no leader is frozen.
4. Model gate: the twelve-site leaders of all four models are reported with the rule's result; a leader that no other model reproduces at twelve sites is labelled MACE-MPA-0-only.
5. Melt set shape under S8 (four buttons plus an IrO2 or NiFe-LDH benchmark): the rule's leader; the strict-intact leader as the conservative second; the banked poor anchor Cu22Fe30Co32Mn15 for dynamic range; and the equiatomic Fe25Co25Ni25Cr25 as the reference composition. Predictions frozen per composition: p10, minimum and median with bootstrap intervals, plus the predicted rank order, deposited before the first ingot.

Under the present numbers and gates 1 to 4, the rule would name Cu8Cr23Mn35Co34 as the provisional leader and Cu26Ni9Cr31Co33 as the conservative second, with the validity gate open. That is the state to test, not a selection.

## What is not claimed

No composition is selected for melting, no prediction is frozen, no deposit is made, and no superiority claim follows from a MACE-MPA-0 census whose low-tail sites are still under DFT test and whose ranking other models do not reproduce at twelve sites.
