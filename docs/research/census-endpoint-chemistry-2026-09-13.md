# Saved-endpoint chemistry — 2026-09-13

The full census supports four reconstructed Cr-site alloy minima, not six. The other two minima have desorbed OOH endpoints. Short Cr–O bonds accompany substantial upward motion of Cr and elongation of its original axial lattice-O contact. This establishes a recurring structural motif in the saved model endpoints; it does not establish a bond order, catalytic stability, or a causal energy benefit from reconstruction.

## Population and verification

The analysis covers 720 unique MPA-0 sites: 30 decorations × four sites for each of the six gated alloys. Exact raw-input hashes, normalized hashes against the banked readout, all 720 CHE reconstructions and independent periodic O–metal distance checks are in `results/site_census_2026-09-06/chemistry_2026-09-13/endpoint_audit.json`. The reusable script is `src/scripts/census_endpoint_audit.mjs`; import `audit(repoRoot)` to reproduce it. Cells are verified orthogonal before component-wise minimum-image geometry. No original result or integrity rule was changed. An independent agent separately recomputed the winner geometries, top-twelve counts and O-energy sensitivity.

## What actually moves

| Alloy | Seed/site | Initial metal | η, V | O–metal, Å | Largest free-slab displacement, Å | OOH category |
|---|---|---|---:|---:|---:|---|
| Ni31Cr29Cu5Mn35 | 1/0 | Cr | 0.439996 | 1.591 | 0.847 (Cr) | NORMAL |
| Fe25Co25Ni25Cr25 | 2/0 | Cr | 0.453057 | 1.589 | 0.799 (Cr) | NORMAL |
| Cu26Ni9Cr31Co33 | 5/2 | Cr | 0.449168 | 1.598 | 0.597 (Cr) | NORMAL |
| Ni34Fe6Cu29Co31 | 13/2 | Ni | 0.607166 | 2.084 | 0.564 (O) | DESORPTION |
| Cu8Cr23Mn35Co34 | 20/2 | Cr | 0.362220 | 1.593 | 0.793 (Cr) | NORMAL |
| Cu22Fe30Co32Mn15 | 15/0 | Mn | 0.455949 | 1.991 | 0.249 (O) | DESORPTION |

For the four Cr minima, Cr itself is the most displaced slab atom (0.597–0.847 Å), mainly normal to the surface. Its original axial lattice-O distance increases from 1.711–1.804 Å to 2.547–2.758 Å; four lateral O contacts remain near 1.85–2.03 Å while the appended O forms a 1.589–1.598 Å contact. The evidence supports axial coordination rearrangement with a short Cr–O contact. Geometry alone does not establish Cr=O bond order or oxidation state. The integrity flag is caused by slab-atom displacement above the unchanged 0.50 Å threshold, not by the short bond itself.

Ni34 instead has a lattice oxygen as its largest displacement (0.564 Å); its Ni moves only 0.258 Å. Cu22 has no O-state reconstruction (maximum 0.249 Å). Both have OOH desorption and proton transfer, so neither minimum represents an intact conventional OOH sequence under the saved classification.

## Is the motif concentrated in the low tail?

Lowest twelve sites are a descriptive, post-hoc equal-size tail, not a new admission policy.

| Alloy | Cr sites / 12 | O reconstruction category / 12 | OOH desorption / 12 | All-state adsorbate-intact / 12 |
|---|---:|---:|---:|---:|
| Ni31Cr29Cu5Mn35 | 5 | 5 | 5 | 3 |
| Fe25Co25Ni25Cr25 | 9 | 10 | 6 | 4 |
| Cu26Ni9Cr31Co33 | 10 | 7 | 8 | 3 |
| Ni34Fe6Cu29Co31 | 0 | 3 | 8 | 2 |
| Cu8Cr23Mn35Co34 | 11 | 11 | 4 | 8 |
| Cu22Fe30Co32Mn15 | 0 | 1 | 9 | 3 |

The strongest enrichment is Cu8 (11/12 Cr). Reconstruction category counts can differ from the independent displacement flag because desorption, dissociation and migration take precedence in the category label. The JSON reports both, plus within-alloy Cr/non-Cr and reconstructed/non-reconstructed populations. These are confounded observational comparisons, not paired estimates of a reconstruction effect.

## Energy interpretation and the useful next calculation

At fixed OH and OOH energies, changing ΔG(O) by x shifts CHE step 2 by +x and step 3 by −x, leaving steps 1 and 4 unchanged. For Cu8 the step energies are 1.578366, 1.592220, 1.366134 and 0.383281 eV. Its current η is therefore only 0.013854 V above the OH-imposed floor of 0.348366 V. This limits further O-only improvement; it does not estimate how much reconstruction helped relative to an unavailable unreconstructed endpoint. The old leader is already OH-limited, so further O stabilization cannot improve its η at fixed OH/OOH.

Ni31, Fe25 and Cu8 have higher-energy builder O endpoints (1.94–2.03 eV above the selected endpoint) with 3.21–3.40 Å contacts. Substituting those energies raises calculated η dramatically, but those endpoints are desorbed and their full alternate coordinates were not retained: they are not intact unreconstructed controls. Cu26 reaches short O contacts from all three starts within 0.00573 eV. Thus the current files demonstrate different basins but do not isolate a reconstruction energy.

Existing matched historical targets already show that the O reconstruction category survives all three other models for Ni31 and Fe25; MP-0 gives desorbed OOH in both. Model disagreement therefore involves the complete pathway, not simply whether Cr lifts.

The next bounded diagnostic uses the newly found minima at Cu26 seed 5/site 2, Ni34 seed 13/site 2, Cu8 seed 20/site 2 and Cu22 seed 15/site 0 under OMAT-0, MP-0 and MATPES. Existing seed-1 Ni31 and seed-2 Fe25 targets are reused. Each new job retains all four sites of its selected decoration, with the target fixed before execution. This is 12 jobs, at most 432 adsorbate relaxations, 12 clean-slab relaxations and 24 gas relaxations. Two workers × two threads, with a 24-hour stop, gives a nominal 96 scheduled core-hour ceiling; it is not a measured cost or promised duration.

Model runs begin from each model’s own relaxed clean slab with identical seeded chemistry and the historical multistart protocol. They test robustness of selected sites after model-specific relaxation; they do not separate geometry effects from model energy effects. A later fixed-geometry cross-evaluation and a constrained structural coordinate scan would be needed for that separation. No new DFT or large candidate campaign follows automatically.

## Limits and remaining work

The saved minima are thermodynamic descriptor outputs, not measured electrode performance or evidence of reversibility. Full pathway integrity, numerical force convergence, correlated model errors, selection on MPA-0 minima, and reconstruction/OOH basin changes remain relevant. The energy-blind DFT pilot retains its original membership. New results will be written separately under `results/census_cross_model_2026-09-13/`, followed by a matched-target readout; review of those outcomes remains pending.
