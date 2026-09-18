# Historical HEA panel and retained-pilot readout — 2026-09-17

**Final readout of all 22 approved legs, through the 14:07:54 UTC scheduler/QC snapshot.** Fifteen are COMPLETE, five stopped at the SCF iteration ceiling, and two are REJECTED for IEEE_INVALID_FLAG. The branch panel accounts for six complete, three ceiling stops and one numerical rejection out of ten; the retained pilot accounts for nine complete, two ceiling stops and one numerical rejection out of twelve. No failed endpoint contributes an energy, no failed projector is replaced by its partner, and no DFT retry is part of this readout.

The completed atomic-projector leader pair supports MACE's direction of energy change from detached HO2 to O2 in the cell plus a proton on the slab. It does not establish an adsorbed *OOH intermediate or validate a low-overpotential composition. The proton-acceptor gap falls outside the frozen comparison band under both projectors, and the final ortho-atomic leg reverses the atomic/MACE acceptor preference. Large forces on free substrate atoms and the unresolved ortho-atomic oxygen-fragment spin prevent interpreting these configurations as DFT minima or comparing projectors as if the same electronic state were established.

## Scope and checks

The inputs are the historical September 6 geometries: equiatomic Fe25Co25Ni25Cr25, seed 2/site 0, and Ni31Cr29Cu5Mn35, seed 0/site 0. They are the frozen docs/92 branch panel and two retained chains. The leader label names that historical composition; this seed/site is not its historical minimum. The Fe25 seed 2/site 0 *O geometry overlaps one of the four low-tail reconstructed Cr minima, and the Ni31 seed 0/site 0 *O is also reconstructed. These fixed-coordinate calculations provide local forces at those endpoints; they do not test persistence under DFT relaxation, validate the newer census ranking, or sample the separate outcome-blind mixed-composition pilot. This scope clarification follows the September 18 coordinate audit.

The September 16 operating decisions retain both Hubbard projectors, the original MP U set and FM starts, fixed geometries and cells, 80/640 Ry cutoffs, and the original per-state k mesh. All 22 terminal input hashes match the approved launch specification. For all 15 COMPLETE legs, the mirrored raw SCF, runtime input and projection hashes match their QC receipts, and an independent raw-output energy extraction matches the receipt energy exactly. The five ceiling stops retain KILLED sidecars; the two numerical exceptions retain REJECTED sidecars. These checks and independent arithmetic are in [hea_independent_verification.json](../../results/research_readout_2026-09-17/hea_independent_verification.json).

The operational COMPLETE count means the required numerical artifacts passed their checks. It does not mean the surface is stationary, the magnetic ground state is identified, or a material is validated. Conversely, an iteration-ceiling stop is a numerical outcome of this bounded attempt, not evidence that the structure is physically impossible.

## Frozen comparisons

| Quantity | Rule retained from the pre-run contract |
|---|---|
| Branch electronic gap and per-adsorbate deltaG residual | WITHIN if absolute residual <=0.250 eV; otherwise OUTSIDE. This is the inherited MACE single-point MAE comparison, not an HEA-calibrated confidence interval. |
| Branch sign comparison | Score only if the absolute MACE gap exceeds 0.250 eV. The equiatomic 0.031098 eV pair has no scored sign comparison. |
| Ordinary four-state AEM overpotential | Compare absolute residual to 0.164 V only for complete, chemically applicable chains. The 0.12955764753597102 V relaxed-pipeline number is secondary. |
| Desorbed third state | Ordinary AEM overpotential is undefined. Do not apply the 0.40 eV *OOH correction to the O2-in-cell plus slab-H endpoint. |
| Fragment moment | Flag SPIN-STATE UNRESOLVED if the absolute projected region moment differs from the free-species reference by at least 0.5 muB, or the table is absent. |
| Residual forces | 0.05 eV/angstrom is the existing stationarity diagnostic, not a new acceptance or model-accuracy threshold. |

Sources: docs/92 sections 4–5, [operating decisions](research-decisions-2026-09-16.md), and the frozen [readout](../../src/dft/hea_panel_readout.py). The 0.250 eV and 0.164 V values are read from docs/33; the secondary eta comparison is read from the banked R4 validation file.

## Branch energies

All differences use E(B)-E(A), at the exact frozen coordinates, with 1 Ry = 13.605693122 eV. No gas reference is needed within these equal-inventory pairs.

| Pair/projector | A -> B | DFT gap (eV) | MACE gap (eV) | DFT minus MACE (eV) | Frozen comparison |
|---|---|---:|---:|---:|---|
| Leader/atomic | detached HO2 -> O2 in cell + H on slab O56 | -2.060637 | -2.281833 | +0.221195 | SIGN AGREES / WITHIN |
| Acceptor/atomic | O2 in cell + H on O56 -> O2 in cell + H on O68 | +0.310107 | +0.726033 | -0.415926 | SIGN AGREES / OUTSIDE |
| Equiatomic/both | intact *OOH on Cr16 -> detached HO2 | — | +0.031098 | — | Both comparisons lack a usable endpoint; no number |
| Leader/ortho-atomic | detached HO2 -> O2 in cell + H on O56 | — | -2.281833 | — | Detached-HO2 leg stopped; no number |
| Acceptor/ortho-atomic | O56 -> O68 endpoint | -0.275016 | +0.726033 | -1.001049 | SIGN REVERSES / OUTSIDE |

The first atomic comparison says DFT also favors the desorbed/deprotonated endpoint among these two specified configurations. It does not show that either endpoint is a relaxed minimum, that a transition between them is accessible, or that this branch supplies a valid four-step adsorbate-evolution pathway. The atomic acceptor comparison retains the preference for O56 while failing the quantitative band; the ortho-atomic comparison favors O68 instead. Their gap difference is 0.585123 eV. Three of the six predeclared pair/projector comparisons have usable endpoints: one residual is WITHIN and two are OUTSIDE; two signs agree and one reverses. The remaining three comparisons stay unscored. Neither the successful atomic sign nor its one WITHIN residual substitutes for the missing partner-projector comparison.

## Spin and force interpretation

| Completed leader endpoint | Atomic projected region moment (muB) | Ortho-atomic projected region moment (muB) | Free-species reference |
|---|---:|---:|---|
| Detached HO2, builder | +1.0426 | no usable leg | 1 |
| O2 in cell + H on O56, pull2.10 | -2.0021 | -0.7635 | 2 |
| O2 in cell + H on O68, pull1.70 | +1.9811 | -1.9775 | 2 |

The region contains the original adsorbate atoms 72–74; after proton transfer the H belongs to the slab environment. The frozen diagnostic uses this region consistently. For pull2.10, the atomic leg matches the triplet-sized magnitude and the ortho leg misses it by 1.2365 muB. The final pull1.70 ortho leg has a triplet-sized magnitude, so its acceptor contrast is against an O56 counterpart that fails the frozen spin diagnostic. This is direct evidence that matching geometry alone has not matched the fragment's electronic state. Projected moments are partition-dependent diagnostics, not measured oxidation states; the result is consistent with differing spin/charge solutions without identifying their cause. Even the two atomic triplet-sized endpoints have opposite signed alignment, so matching the free-species magnitude does not establish an equivalent magnetic configuration or the ground state.

All 15 COMPLETE structures have maximum free-component force norms of 1.2618–1.5706 eV/angstrom, about 25–31 times the 0.05 diagnostic. In every case the maximum is on a free substrate atom, including the clean slabs. The mismatch therefore extends beyond the detached fragment. The retained equiatomic clean slab has 1.5100 eV/angstrom, and the leader clean slab has 1.5313 (atomic) and 1.4750 (ortho) eV/angstrom. A model-force-converged structure is not stationary under these DFT protocols. This establishes a geometry/force mismatch, not the outcome of a future DFT relaxation and not, by itself, the fate of the newer census Cr reconstruction.

The same-coordinate comparison is explicit: the cached MACE leader clean-slab maximum constrained force is 0.040426 eV/angstrom, versus DFT atomic 1.531251; for retained *O it is 0.042414, versus 1.499240. Both MACE records report force convergence at 0.05 eV/angstrom. The input positions exactly match the cached arrays in [leader_result.json](../../results/cr_site_chains_2026-09-06/leader_result.json), under `results[0].row.decoration_records[0].relaxed_slab` and `results[0].row.per_site_records[0].relaxed_states.O`. The corresponding DFT sources are [slab__atomic.out](../../runs/hea/pilot_retained/Ni31Cr29Cu5Mn35__s0_site0/slab__atomic.out) and [O__atomic.out](../../runs/hea/pilot_retained/Ni31Cr29Cu5Mn35__s0_site0/O__atomic.out).

For retained *O, the atomic-projector DFT force vectors on zero-based Cr16 and adsorbate O72 are respectively **(+0.021866, -0.218147, +0.985373)** and **(-0.074938, +0.178835, -0.919756) eV/angstrom**. Cr has an upward and O a downward force component at these coordinates. These are local energy-gradient directions; the relaxed outcome is unmeasured. In particular, the present fixed-geometry data do not establish that DFT removes the short Cr–O reconstruction.

## Retained-chain consequences

Neither equiatomic projector has all four usable states. The atomic chain lacks clean slab, OH and OOH; the ortho chain lacks O. Its ordinary AEM overpotential and the 0.164 V fidelity comparison are therefore unscored.

Both leader projector chains are numerically complete, but their third state is O2 in the cell plus H on the slab, not *OOH. Independent arithmetic with the banked DFT gas references gives:

| Leader quantity | Atomic DFT (eV) | Ortho-atomic DFT (eV) | MACE (eV) | Atomic / ortho residual (eV) |
|---|---:|---:|---:|---|
| deltaG_OH | 2.413955 | 2.381259 | 2.208079 | +0.205876 WITHIN / +0.173180 WITHIN |
| deltaG_O | 3.816203 | 4.035844 | 3.593139 | +0.223064 WITHIN / +0.442705 OUTSIDE |
| Third-state electronic adsorption difference, without the *OOH correction | 2.808016 | 3.335397 | no *OOH fidelity comparison | — |

The final ortho *O leg therefore adds a quantitatively OUTSIDE oxygen-adsorption comparison; three of the four leader OH/O residuals are WITHIN. This small, selected set supplies no population accuracy estimate.

The first three increments under the frozen mixed electronic/free-energy bookkeeping are **2.413955, 1.402249, -1.008187 eV** for atomic and **2.381259, 1.654585, -0.700446 eV** for ortho-atomic. Their maxima minus 1.23 V are **1.183955 V** and **1.151259 V**, respectively. These are nominal partial-ladder lower bounds under that convention, not ordinary AEM overpotentials. The fourth step is unmeasured, and a consistent free-energy correction for the desorbed third endpoint is also unmeasured; they are not calibrated bounds on experimental OER performance. The historical MACE value 0.978079 V remains visible only as AEM bookkeeping on a non-*OOH state.

Of four chain/projector comparisons, zero support an ordinary AEM overpotential score: the equiatomic chains are numerically incomplete and the leader AEM chain is chemically inapplicable. Filling a missing energy from the other projector, a rejected endpoint, or a different historical realization would change the comparison and is not done.

## Reproduction and realized cost

The primary scorer is run as:

~~~powershell
python src/dft/hea_panel_readout.py --json results/hea_readout_2026-09-17/readout.json
~~~

The [canonical primary readout](../../results/hea_readout_2026-09-17/readout.json) agrees with the independent checks for all 22 statuses, all 15 usable raw Ry energies, and 25 numerical/spin comparisons. The largest arithmetic difference is 5.93e-12 eV from conversion/subtraction order; every band, sign and chain-eligibility conclusion agrees. Results are recorded in [hea_independent_verification.json](../../results/research_readout_2026-09-17/hea_independent_verification.json).

Two reporting-parser corrections were necessary: accepting valid QE wall-time strings without seconds, and excluding the exact benign underflow/denormal notice from the generic severe-exception pattern. The two IEEE_INVALID rejections remain excluded, and the frozen scoring rules are unchanged. The [original scorer](../../results/research_readout_2026-09-17/original_hea_panel_readout.py), failed reporting output and [timing-only intermediate](../../results/hea_readout_2026-09-17/readout_timing_fix_only.json) remain archived. The [final readout receipt](../../results/research_readout_2026-09-17/hea_readout_final.json) supersedes those reporting attempts; no DFT calculation was rerun.

The final [scheduler ledger](../../results/research_readout_2026-09-17/scheduler_final.json) records an empty queue and **3,098.31 elapsed core-hours** for all 22 HEA tasks: 1,570.95 for the ten-leg panel and 1,527.36 for the twelve-leg pilot. These figures sum elapsed seconds times allocated CPUs and include all failed attempts. They are separate from the 4,164.7 core-hour planning figure and the larger hard allocation cap.

Observed force-phase overhead matters for future pricing: at the same frozen pull1.70 coordinates, [the ortho-atomic output](../../runs/hea/branch_panel/leader_pull1.70__ortho.out) records 854.77 seconds in forces, including 841.13 seconds in Hubbard forces; [the atomic output](../../runs/hea/branch_panel/leader_pull1.70__atomic.out) records 55.98 and 41.91 seconds, respectively. This is one observed pair, not a general hardware benchmark, but shows why SCF iteration cost alone misses material work.

S8 remains at computational/experimental feasibility with no superiority claim. Resolving the current numerical, force and spin limitations and directly testing the newer census-selected reconstructed sites are distinct scientific tasks; this historical panel does not complete those validations. No retries or additional DFT runs were launched for this readout.
