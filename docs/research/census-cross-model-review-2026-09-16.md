# Cross-model selected-site review — 2026-09-16

The twelve-job follow-up completed on 2026-09-13 at 22:56:10 UTC, exit 0, in 15,725.83 seconds (4.368 hours). All twelve jobs produced complete four-site records. The short Cr–O motif survives the model changes, but full-pathway chemistry and ordering remain model-dependent; these results do not identify a superior melt.

## Evidence and verification

The new outputs are `results/census_cross_model_2026-09-13/results/*_result.json`; `target_readout.json` includes twelve fresh targets and six reused targets, with all 18 identities matched and none missing. Independent file-only verification checked all 94 frozen input hashes, all 18 readout source hashes, the three cached checkpoint byte hashes, candidate fractions/seed/site/metal identities, target CHE arithmetic from raw energies and periodic O–metal distances. Maximum discrepancies were 1.78e-15 eV and 3.56e-15 Å. Machine-readable evidence is `review_2026-09-16.json` in the same result directory.

All 54 chosen states across the 18 matched targets met the saved force criterion. Among the 144 chosen states across all 48 new sites, five non-target states did not: MATPES Cu26 seed5 sites0/3 OOH; MP-0 Cu8 seed20 site1 OH; OMAT-0 Ni34 seed13 site1 O and OOH. Seven of 432 alternative starts were unconverged. All twelve clean slabs and 24 gas references converged. Exit 0 therefore establishes queue completion, not universal force convergence. No failed state was replaced or retried.

Realized configured-thread time, summed job elapsed time × two threads, was 17.023 hours; this is not measured CPU utilization. The original ceiling was 96 scheduled core-hours. The frozen `selection.json` retains its original PREPARED_NOT_STARTED text; launch, status and completion files establish the subsequent execution history.

## Matched-target descriptor values

Units are volts. † marks at least one adsorbate-nonintact state in that model, so the number is a formal CHE descriptor, not an intact conventional pathway. MPA-0 minima were the selection source, not held-out outcomes. Its Ni34 and Cu22 targets also have nonintact OOH.

| Selected alloy target | MPA-0 | OMAT-0 | MP-0 | MATPES |
|---|---:|---:|---:|---:|
| Ni31Cr29Cu5Mn35 | 0.439996 | 0.746215 | 0.529393† | 0.572702 |
| Fe25Co25Ni25Cr25 | 0.453057 | 0.691501 | 1.016321† | 0.350384 |
| Cu26Ni9Cr31Co33 | 0.449168 | 0.514806 | 0.719714 | 0.567414 |
| Ni34Fe6Cu29Co31 | 0.607166† | 1.202078† | 1.146666† | 1.169022 |
| Cu8Cr23Mn35Co34 | 0.362220 | 0.509589 | 0.842930† | 0.629047 |
| Cu22Fe30Co32Mn15 | 0.455949† | 1.395534 | 1.049551 | 2.577262† |

At the four Cr targets all twelve alternative-model O contacts are 1.559–1.581 Å. Cu8 shows O reconstruction in all three alternatives (maximum slab displacement 0.590, 0.822 and 0.589 Å for OMAT-0, MP-0 and MATPES), but MP-0 desorbs OOH and transfers H. Its O multistarts agree within 0.00238 eV, whereas its MP-0 OOH starts span 2.017 eV: basin selection in the full pathway remains material.

Cu26 retains all adsorbates under all four models, the only selected target to do so. MATPES gives a short 1.572 Å O–Cr contact with maximum O-state slab displacement 0.438 Å, below the unchanged 0.50 Å reconstruction threshold; its OH state instead crosses that threshold. Do not describe this O endpoint as classified reconstruction, or treat threshold category disagreement as disappearance of the short contact. All six new Cu26/Cu8 O multistart groups reach short contacts with energy spreads below 0.00430 eV.

Ni34 has OOH desorption in OMAT-0 and MP-0, while MATPES retains it; all three alternatives give η around 1.15–1.20 V. Cu22 retains OOH under OMAT-0/MP-0 but dissociates it under MATPES, with formal η from 1.05 to 2.58 V. The new models do not rescue the low MPA-0 descriptors of those non-Cr minima as a robust intact pathway.

Among targets allowing surface reconstruction but requiring intact adsorbates, OMAT-0 leads with Cu8 (0.509589) only 0.005217 V ahead of Cu26; MP-0 leads with Cu26 (0.719714); MATPES leads with Fe25 (0.350384). If all reconstruction is excluded, the surviving targets are only Cu22 for OMAT-0/MP-0 and Ni34 for MATPES. Those filtered survivors are not winners of the full census.

## Implication for the next work

The recurrence makes an MPA-0-only structural artifact less likely, but related model errors, model-specific clean geometries and post-hoc selection prevent physical validation. Fixed-geometry cross-evaluation and DFT structural checks should resolve whether the short-contact basin is supported by electronic structure and whether OOH remains intact. The separately approved numerical/DFT controls can proceed while preserving frozen energy-blind pilot membership; favorable census targets must not substitute for that pilot. Continue feasibility research with no claimed superior melt and no validated rank claim.
