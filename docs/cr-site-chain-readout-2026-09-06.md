# Cr-site chains and competing OOH endpoints — 2026-09-06

Two complete Cr-centered adsorption chains expose a chemical-state distinction that force convergence alone misses. The equiatomic site retains metal-contacted OOH. The tested site in Ni31Cr29Cu5Mn35 instead favors an O2-like fragment with its hydrogen on a slab oxygen. Recovering all six OOH endpoints confirms these distinct branches and supplies a compact next DFT comparison.

This does not reverse a composition ranking. The historical leader's winning chain used seed 1; this diagnostic deliberately tests seed 0/site 0. The equiatomic seed 2/site 0 is its lone Cr center in the twelve-site pristine survey. Its formal CHE score, 0.453056552 V, reproduces the stored historical score within 4.6e-10 V. Numerical reproducibility is distinct from physical accuracy.

## Observed endpoints

All initial 24 relaxation executions meet the 0.05 eV/Angstrom constrained-force criterion: two clean slabs, eighteen adsorbate starts and the H2O/H2 pair in each process. Six additional OOH replays also converge. All six reproduce the initial energies within 1.14e-13 eV; both selected OOH structures reproduce their stored coordinates exactly. The replays recover missing coordinates and are not independent samples.

| Environment and OOH start | Energy above selected endpoint (eV) | O-O (Angstrom) | Distal O-H (Angstrom) | H-nearest slab O (Angstrom) | Proximal O-nearest metal (Angstrom) |
|---|---:|---:|---:|---:|---:|
| Equiatomic, builder | 0.031098 | 1.34313 | 1.00059 | 3.32370 | 4.70563 |
| Equiatomic, pull1.70 | 0.003010 | 1.37170 | 0.99260 | 3.63669 | 1.98256 |
| Equiatomic, pull2.10, selected | 0 | 1.37219 | 0.99281 | 3.64378 | 1.97541 |
| Ni31Cr29Cu5Mn35 seed 0, builder | 2.281833 | 1.33854 | 1.00210 | 4.87035 | 4.55679 |
| Ni31Cr29Cu5Mn35 seed 0, pull1.70 | 0.726033 | 1.23780 | 1.98236 | 0.98123 | 4.18063 |
| Ni31Cr29Cu5Mn35 seed 0, pull2.10, selected | 0 | 1.22994 | 3.30259 | 0.97113 | 3.40002 |

**Equiatomic:** both pulled-in endpoints retain short OOH-like O-O/O-H distances and a short proximal O-Cr contact. The builder endpoint retains OOH-like connectivity away from the surface: both fragment oxygens are more than 3.42 Angstrom from every substrate atom. It lies only **31.10 meV** above selected. This is a competing model electronic endpoint, not a measured adsorption free-energy gap or a resolved physical branch ordering. Finite force tolerance, model error, missing vibrational/entropic contributions and additional basins remain relevant.

**Tested leader-composition site:** the builder retains detached OOH-like geometry. Both pulled-in endpoints have a short O-O distance, no short fragment O-H bond, and H close to a slab oxygen. The geometry is consistent with an O2-like fragment plus protonated slab oxygen: O68 for pull1.70, O56 for selected pull2.10. Their model electronic energies differ by **0.72603 eV**. Both oxygens of the selected fragment are more than 3.29 Angstrom from every substrate atom. Its nearest metal happens to be Ni18; a 3.40 Angstrom distance does not demonstrate Ni adsorption or Cr-to-Ni physical migration. No sampled endpoint here supplies intact, metal-contacted OOH. Geometry alone establishes neither bond order nor oxygen production.

The initial site-evidence check consequently retains one eligible chain and one failed chain under its existing proximal metal-oxygen cutoff. The failed chain's formal 0.978079 V CHE value and negative third step remain in the raw readout for inspection. The defect is assigning the alternative endpoint an intact-OOH state/correction; an exergonic individual step is not intrinsically invalid. No replacement start or candidate minimum is substituted.

The equiatomic OH starts also span 1.31747 eV despite all meeting the force criterion. The clean slab's free-atom RMS displacement from the pristine builder is 0.171 Angstrom for the equiatomic decoration and 0.341 Angstrom for the leader-composition decoration. Fixed atoms stay fixed. These are endpoint displacement observations, not evidence of a new phase or a trajectory. The comparison therefore does not isolate a single local-composition mechanism from finite-cell composition, strain and structural response.

## Next sequential DFT comparison

The immediate probe is **four fixed geometries**, specified in [dft_branch_panel.json](../results/cr_site_chains_2026-09-06/dft_branch_panel.json):

1. Equiatomic selected metal-contacted OOH versus builder detached OOH. Model electronic E(detached)-E(contacted) = +0.031097709 eV.
2. Leader-composition seed-0 builder detached OOH versus selected OO-plus-slab-H endpoint. Model electronic E(OO+H_slab)-E(detached OOH) = -2.281832858 eV.
3. Optional fifth geometry: leader pull1.70, comparing proton acceptor O68 against O56 (+0.726032806 eV in MACE).

Within each pair, atom inventory, cell, periodicity and fixed-atom indices match. Branch electronic energy differences therefore need no gas or clean-slab reference; they do not supply DFT CHE overpotentials. Use one explicit electronic-structure protocol across a pair, including pseudopotentials, functional, U/projector policy, spin initialization, charge, cutoffs, k mesh and boundary treatment. Four or five distinct fixed geometries are not a forecast of total jobs after spin starts or retries. No DFT jobs ran here.

First compare the DFT and MACE branch gaps at these exact coordinates. Then relax both branches under the same DFT/spin protocol, separating fixed-geometry disagreement from relaxation effects. If distinct minima remain, kinetics requires a subsequent path calculation. No retained metal-contacted intact OOH exists for the tested leader site; such a control would need an explicitly identified initial configuration and cannot be presented as an observed minimum.

The next ordinary environment remains fixed as equiatomic seed 2/site 1, pristine Ni, independently of its unobserved energy. It cannot replace the failed Cr-site chain. The branch comparison above has priority because it directly challenges the intermediate assignment behind the descriptor before a larger screen.

## Method and limits

Exact source fractions, pristine Cr-site identities, source/model hashes and matching calculation protocols are checked. Both arms use the existing MACE-MPA-0 checkpoint, float64, CPU, two PyTorch threads and BFGS with a 300-step limit. First-chain evaluation times are 511.016 and 854.829 seconds; OOH replay loops take 178.297 and 495.328 seconds. Processes overlapped, so these are not serial performance benchmarks. The calculations use imposed rutile slabs, not identified activated electrode phases.

The standalone geometry audit retains ordered site identities, periodic minimum-image distances, contact ties, explicit exploratory thresholds and numerical metadata separately. ASE's geometry routines handle skew cells ([ASE implementation](https://docs.ase-lib.org/_modules/ase/geometry/geometry.html)). Thresholds are inspection rules, not universal bond definitions, and do not change legacy eligibility or ranking. Initially only selected starts retained coordinates; the separate OOH replays recover all six OOH endpoints. Nonwinning OH/O geometries remain unavailable.

Internal proton relocation preserves atom inventory, so the alternative configuration can have a valid calculated total energy while needing a different intermediate label and thermochemical treatment. Bridging-oxygen-assisted OOH deprotonation has precedent on Ir-modified RuO2 in acid; it does not establish a mechanism in these alkaline HEA models ([Wu et al., 2024](https://www.nature.com/articles/s41467-024-54798-7)). Cooperative centers in activated alkaline LDHs likewise motivate inspection of multiple short metal contacts without identifying the chemistry of these rutiles ([Dionigi et al., 2020](https://www.nature.com/articles/s41467-020-16237-1)).

## Verification and artifacts

Raw results, paired CHE readout, six-branch geometry readout and eighteen coordinate exports are in [results/cr_site_chains_2026-09-06](../results/cr_site_chains_2026-09-06). JSON retains full coordinate precision; extxyz positions have eight decimal places and pass atom-order, cell, periodicity and constraint read-back checks. Corruption tests reject altered exact fractions, selected-start labels, source/protocol identities, duplicate starts, injected gas states, mismatched replay coordinates and unavailable executed-code hashes.

The executed replay script is preserved as recover_ooh_starts_recorded.py. Its environment field was copied from the initial chain and is explicitly labeled source-only in the readout; a contemporaneous independent environment check matches the initial chain. The current recovery runner records actual runtime metadata and reserves its output exclusively. The replay readout preserves the executed script hash separately from current code and does not treat equal energies as proof of equal coordinates for the originally unretained endpoints.

All work runs on the verified separate Codex_STS_Background desktop. Final test counts, file hashes, protected-path checks and execution records are in verification.json.
