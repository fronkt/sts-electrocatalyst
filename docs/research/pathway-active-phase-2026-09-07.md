# Pathway and operating-surface follow-up — 2026-09-07

These are additions to the current program. The census and its frozen readout remain intact. Source protocols: docs/91 and docs/92; operating condition from src/dft/pourbaix_multi.py is pH 14, 1.53 V RHE, with 1.23 V RHE as equilibrium and 1e-6 M aqueous-ion activity convention. The existing multi-element bulk Pourbaix gate already exists; repeating it is not a new active-surface test.

## Balanced pathway calculation

Use src/hea_oer/pathway_audit.py with results/hea_rigor_2026-09-07/bridge_cycle_template.json. The ordered cycle is clean -> O_cus+H_bridge -> O_cus -> O2_cus+H_bridge -> H_bridge+O2(g) -> clean+O2(g). Its bookkeeping consumes two waters and releases four proton/electron pairs. The explicit oxygen-release step has zero electron transfer: an uphill chemical step cannot be eliminated by raising the CHE potential. No limiting potential is reported while any required free energy is missing. This is a proposed sequence to test, not evidence that those intermediates exist.

Use a common slab, surface composition, calculator, spin protocol and molecular reference. Cumulative state energies include appropriate solvation/vibrational/entropy corrections for their actual chemical identity; the conventional OOH correction is not silently applied to O2+H_bridge or a detached radical. The final standard-state CHE energy is 4.92 eV. A reference-id string identifies the matched calculation family; it is not independent verification of physical equivalence.

The CENSUS-1b O2-binding diagnostic cannot supply the missing protonated-slab or O_cus+H_bridge free energies. Prepare those from geometries with a verified proton acceptor and test force convergence, chemical identity and spin. An oxygen molecule still interacting with the slab is not a separately referenced gas molecule. Compare the direct four-PCET route with the explicitly released-O2 route only after both are balanced and endpoints are validated. NEB or constrained proton-transfer scans follow validated minima; no finite-temperature rate or electrochemical kinetic claim follows from this CHE bookkeeping.

The route is motivated by Svane and Rossmeisl, not a novel pathway claim: https://doi.org/10.1002/anie.202201146 . Their rutile treatment includes transfer to bridge oxygen; its physical validity must be established for these different 3d-rich compositions.

## Operating surface: distinguish the existing bulk gate from the missing surface test

1. Use the preselected validation/audit compositions; do not choose the surface model because it improves activity. Begin with the exact retained decorations and record surface area, cation inventory and all fixed atoms.
2. Compare clean, OH-covered and O-covered terminations at pH 14 over 1.23, 1.53 and 1.73 V RHE, with explicit coverage fractions and arrangements. At least two arrangements at partial coverage are necessary to reveal lateral interactions; the endpoint set is a starting design, not an exhaustive surface ensemble. Use the same cation slab reference and surface grand potential per area. In neutral CHE, RHE already absorbs the ideal proton/electron pH term: do not add it a second time. Field, solvent and non-PCET pH effects require explicit treatment and are not captured by this grid.
3. Add a matched vacancy and a surface/subsurface cation-swap pair at the selected motif, retaining total cation composition for segregation comparisons. Oxygen-vacancy comparisons need an explicit oxygen/water reservoir. A single vacancy or swap cannot establish equilibrium disorder.
4. Investigate chemically plausible mixed oxyhydroxide/spinel alternatives for these Ni/Co/Fe/Mn/Cr-rich compositions. Those need their own equilibrated structures, balanced composition/reservoir references, and convergence checks. Metal-alloy Omega/delta formability and the imposed rutile screen do not establish oxide/oxyhydroxide stability. Short MACE trajectories alone do not settle phase selection.
5. Combine bulk dissolution tendency with surface energetics while retaining metastability and kinetic limits. Co-Cr spinel reconstruction is motivating evidence, not a result for these rutile slabs: https://www.nature.com/articles/s41467-025-65626-x .

Scientific decisions: if endpoints lose the claimed identity under DFT, retain the failure and analyze the resulting chemistry rather than re-labeling its energy as OOH. If a different surface phase is favored, report rutile results as conditional and evaluate the alternative before a materials-ranking claim. If relevant energy differences remain unresolved under controls, keep candidates tied. Stable computed endpoints remain hypotheses about the operating electrode until physically validated.

## Verification

The pathway tests cover balanced conventional and bridge inventories, missing energy, reference mixing, nonregenerated surfaces, lost hydrogen and potential-independent uphill release. The force audit separately checks real SCF ordering, atom indices/types, Cartesian fixed-coordinate masks and Ry/bohr conversion. All synthetic numbers are confined to software tests. No new pathway, phase or DFT accuracy result is implied by passing them.
