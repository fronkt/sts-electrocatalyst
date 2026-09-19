# S8 ranking statistic — candidates on the completed census, and a proposal for the dated line (2026-09-19)

**Dated correction, 2026-09-19:** the [independent review](s8-ranking-independent-review-2026-09-19.md) supersedes the original physical interpretation and the unqualified ranking-frequency claims. Historical tables below retain the original calculation; exact ties were alphabetically ordered and bootstrap draws with an empty composition omitted that competitor. Those frequencies are not corrected six-way ranking probabilities. The candidate rule is exploratory and remains unadopted.

The S8 disposition of 2026-09-16 holds melt selection until, among other things, the composition-selection rule and its ranking statistic are defined and the actual predictions are frozen before any validation sample is prepared. The census of 2026-09-13 showed why: the six fully sampled compositions have different leaders under the minimum, the mean and the median, and the low tail contains reconstructed Cr sites and adsorbate loss. This note computes, with no new compute, how the six compositions order under six candidate statistics and three admission policies, with a decoration-level bootstrap for the stability of each order, and proposes one rule for the entrant's dated line. It selects no melt, freezes nothing and changes no census value.

Source: `results/site_census_2026-09-06/readout_full/per_site.csv` (MACE-MPA-0, 30 decorations x 4 sites = 120 sites per composition; the three other models at the shared twelve CENSUS-1 sites). Calculation: `src/scripts/s8_ranking_statistics.py`; tables and bootstrap in `results/s8_ranking_statistic_2026-09-19/` (B = 10,000 resamples of the 30 decorations, seed 0).

## Why the statistic matters physically

The site overpotential here is a CHE thermodynamic descriptor. It does not supply kinetic barriers, prefactors, coverages or accessible site densities, so it cannot by itself determine current or physically justify p10 as a fixed-current electrode prediction. The 2×2 rutile model has not been established as the operating surface of the proposed alloy buttons. A low quantile is an exploratory descriptor of a model-specific distribution.

The implemented p10 uses NumPy's linear interpolation: at n=120 it is 0.1 times the twelfth plus 0.9 times the thirteenth sorted observation. After adsorption-only admission, n varies from 8 to 38; Cu8 has 16 records and its p10 lies halfway between the second and third. Admission checks force convergence, dissociation, migration and desorption, with reconstruction excluded only by the strict policy. These operational labels do not establish experimental site activity.

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

Policy `intact` (strict integrity, n = 3 to 33 sites): Cu26Ni9Cr31Co33 leads under five of six statistics with P(rank 1) between 0.49 and 0.64; Cu8Cr23Mn35Co34 keeps only four sites and Ni31Cr29Cu5Mn35 three.

Cross-model check on the shared twelve sites: the four models name two to four distinct leaders under every statistic (four under the minimum). At twelve sites the ranking is model-dependent under every candidate rule; the 120-site result exists for MACE-MPA-0 only.

## Reading after independent review

- The all-sites distribution has different tail and central leaders, but includes chains that fail intact-pathway checks. Its formal CHE values remain diagnostics; their physical interpretation differs from an intact conventional pathway.
- Within the adsorption-only policy, Cu8 leads the observed statistics. Its p10 lead survives all 180 leave-one-decoration-out checks, including each of its own 30 decorations. This is within-policy stability, not agreement across policies or physical validation. The p10 brackets are seed16/site2 and seed26/site1; the current Cu8 DFT target is seed20/site2.
- Strict-policy retained counts range from 3 to 33. Cu8 and Ni31 each have only three supporting decorations and an empirical empty-bootstrap probability of 4.239%. Exact ties and missing competitors require explicit handling before interpreting ranking frequencies.
- Cross-model filtered comparisons combine energy, geometry and admission differences. Another model or one converged O endpoint does not alone validate a composition ranking or the full OH/O/OOH pathway.

## Candidate rule remains open

The original p10 rule and 0.80 top-two frequency threshold were explored after inspecting this census. They remain proposals, with no calibrated physical loss function or independent confirmation. A future frozen rule must specify the admission population, linear quantile convention, tie treatment, empty-sample denominator, sample-role overlap and an endpoint appropriate to the intended experimental comparison. Report retained sites/decorations and admitted low-descriptor sites out of all 120 beside any conditional descriptor.

The current O/clean-slab DFT array tests selected structural responses, not all low-tail OH/O/OOH chains or the entire p10 distribution. No counterfactual Cu26 lead after removal of reconstructed Cu8 sites is established here. Bootstrap intervals for p10/minimum/median are also not present in the original ranking-frequency output.

The controlling September 16 S8 disposition retains the matched poor anchor and IrO2 comparator. The previous suggestion of substituting NiFe-LDH did not adopt such a change. Likewise, a strict-policy leader is not yet an experimentally established conservative second. Selection and prediction freeze remain open under that disposition.

## What is not claimed

No composition is selected for melting, no prediction is frozen, no deposit is made, and no superiority claim follows from a MACE-MPA-0 census whose low-tail sites are still under DFT test and whose ranking other models do not reproduce at twelve sites.
