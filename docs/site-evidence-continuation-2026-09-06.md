# Site evidence and scientific continuation — 2026-09-06

The useful scientific target is a selection method whose claimed improvements survive changes in adsorption motif, numerical treatment, and working surface. The present rutile minimum-score list has not established that transfer. The new diagnostic software makes its weak links measurable; it is not a new density functional or evidence of an iridium-beating electrode.

## New structural observation

A calculator-free survey rebuilt all 12 historical target compositions with the current rutile builder, exact stored fractions, seeds 0/1/2 and four cus sites per decoration. Each cell has 24 cations and 72 atoms. This is a present-builder reconstruction; historical per-site coordinates were not retained, so it is not proof of the exact historical site roster.

| Historical nominal position among the six retained rows | Composition label | Current pristine Cr-centered sites out of 12 | Target-to-cell discrepancy |
|---|---|---:|---|
| 1 | Ni31Cr29Cu5Mn35 | 5 | Ni8Cr7Cu1Mn8 on 24 cations; maximum fraction change 2.219 percentage points |
| 2 | Fe25Co25Ni25Cr25 | 1 | Six of each cation; exact quarter fractions |
| 3 | Cu26Ni9Cr31Co33 | 5 | Cu6Ni2Cr8Co8; maximum fraction change 1.867 percentage points |

The historical best-site labels of all three are Cr. Equal total site counts therefore do not imply equal sampling of the motif class that determines the score. The first composition also exposes no Cu-centered cus site in these 12 positions; Cu remains in the cell and can affect neighboring sites. Across the 12 targets, the largest component-fraction discrepancy is 2.372 percentage points. These are geometric observations, not activity measurements.

**Interpretation.** The leading comparison may mix a composition effect with a favorable-tail sampling effect. It is not established that either dominates. The equiatomic composition's lone sampled Cr center is an especially informative diagnostic target: compare its local environment and adsorption chain with the several Cr environments in the nominal leader. Additional random seeds test the sampled distribution; a stratified central-metal comparison tests a different, conditional question. A stratified minimum cannot silently replace the original population statistic, and motif counts are not equilibrium surface populations.

A continuous nominal composition variable also controls the Vegard lattice while cation counts change in discrete steps. Thus a score difference can arise from lattice strain, a changed finite-cell composition, or a changed local arrangement. A composition study should record all three; matching only rounded formula strings is insufficient.

## Implemented diagnostic

The explicit-composition runner consumes exact fractions from a named source file, retains their ordering, pins current checkpoint bytes and source hashes, and records the sampling protocol. Historical model-weight equivalence remains unestablished. Outputs are separate from the historical ranking. Exclusive locks, finite serialization and candidate checkpoints protect interrupted runs; caught exceptions retain partial site evidence. Resume retains recorded failures instead of retrying them out of the denominator. Partial in-memory recovery does not recover a killed process's unfinished candidate.

The backend retains clean/adsorbate/gas energies, force records, all attempted-start summaries, selected geometries, and initial/final binding partners. The evidence analysis reconstructs CHE from absolute energies and applies every explicit OH/O/OOH correction to every site before choosing a minimum. It preserves ties, unknown or failed chains, the original minimum, and decoration-removal sensitivity. A secondary eligible-only statistic remains separately labeled.

Here, eligibility is a limited record/numerical check: force convergence, energy consistency and the existing metal–oxygen distance screen. It does not establish intact OOH, a complete basin search, the correct active phase, or accuracy. A failed nonwinning start can hide an unlocated lower basin. A change of binding partner between intermediates raises a pathway/locality question but does not automatically invalidate the thermodynamic energies.

The retained OOH geometry has appended atom order proximal O, distal O, H. Before a DFT chain is interpreted as a single-site adsorbate-evolution mechanism, inspect O–O and both O–H distances, the H-to-nearest-slab-O contact, and both O-to-metal contacts with periodic minimum-image distances. Proton transfer, O–O cleavage and migration cannot be excluded by proximal O–metal distance alone. A negative fourth CHE step is not intrinsically impossible; individual steps may be exergonic in an overall endergonic cycle.

## The next discriminating calculations

The diagnostic panel should include the leading Cr-dependent pair, Ni34Fe6Cu29Co31, and the Co-led Cu22Fe30Co32Mn15 anchor. The six-row manifest retains the complete current clean roster so the smaller panel can expand without a newly sampled pool. These are previously inspected compositions, so the work is exploratory.

For an initial three-composition DFT fidelity pilot, use Fe25Co25Ni25Cr25, Ni34Fe6Cu29Co31 and Cu22Fe30Co32Mn15. Allocate two site slots per composition before seeing DFT energies: the model's nominal winning site and one deterministic energy-blind comparison site from the remainder. Keep selected failed/unknown chains visible; if a site is unusable, retain that outcome rather than quietly substituting a favorable alternative. For three compositions, six complete site chains require 18 adsorbate calculations, 3–6 distinct clean-slab references, and two shared gas references: 23–26 fixed-geometry calculations, depending on slab sharing. These are distinct structure/single-point evaluations before additional spin starts, retries or relaxations, not a total job count or cost forecast. Adding Ni31Cr29Cu5Mn35 expands the pilot to eight chains and 30–34 distinct fixed-geometry evaluations.

Separate three questions:

1. **Surrogate energy error:** evaluate DFT on the retained geometries with one explicit, coherent protocol and consistent gas references. Analyze signed step-energy errors and pairwise changes, including ordinary environments.
2. **Geometry/basin error:** re-relax selected complete chains under that same DFT protocol, with documented spin and starting-state checks. Separate the energy correction at fixed geometry from the relaxation correction.
3. **Electrode transfer:** compare that modeled phase with evidence about the activated electrode. An improved match to DFT is surrogate fidelity; an improved match to physical measurements is a different claim.

The existing general slab writer contains fixed atomic-projector and metal-specific U defaults. Its command-line path also rebuilds pristine geometry from rounded composition labels. It should not silently define this pilot. A mixed-site queue must consume retained atom coordinates and state explicitly the pseudopotentials, projector convention, U policy, spin treatment, cutoffs, k mesh, charge, boundary conditions and single-point versus relaxation role. Only vary a protocol choice in a paired comparison that preserves the other choices.

The q333 result establishes the tested numerical stability of bulk U, not a surface-appropriate U or electrode accuracy. The strongest reason for another DFT calculation is to distinguish these failure mechanisms, not to collect a finer convergence number with no effect on a materials decision.

## Novelty and the deliverable

Broad AI-guided high-entropy OER discovery is occupied prior art. Zhou and colleagues already combined spectroscopy, generative inverse design and robotic OER synthesis/testing, with experimental optimization of a candidate: [Nature Synthesis, 2026](https://www.nature.com/articles/s44160-025-00983-5), independently accessible [author-institution abstract](https://research.birmingham.ac.uk/en/publications/a-practical-inverse-design-approach-for-high-entropy-catalysts-us/). This review uses the abstract and publication record; it does not assert details of the full evaluation.

The stronger candidate contribution here is a controlled demonstration that a documented DFT correction/failure policy changes and improves selection on new compositions, compared with both the legacy best-site score and a simple composition/processing baseline. Record ordering errors, useful selection improvement, compute cost and abstention together. A policy that avoids every hard case does not demonstrate useful discovery. This is a testable contribution proposal, not an established priority claim.

A physically motivated extension is a precursor-to-active-surface bridge. Operando work on NiFe/CoFe LDHs found activated gamma phases and cooperative metal centers; it does not identify the phases of these melts: [Dionigi et al., 2020](https://www.nature.com/articles/s41467-020-16237-1). An exploratory composition/processing/activation dataset can test whether DFT descriptors add value before attempting an exhaustive reconstruction model. A genuinely prospective pre-melt predictor cannot use post-activation measurements from its own confirmation samples as inputs.

My recommendation is to prioritize a small, decisive transfer test and an inspectable ranking tool over a larger unvalidated composition screen. The deliverable should show the candidate's exact modeled composition and motif, evidence quality, correction sensitivity, unresolved comparisons and the reason for any abstention. A later matched alkaline comparison should include IrO2 and NiFe, sustained oxygen output/Faradaic efficiency, and independent preparation batches. Beating IrO2 alone would not establish superiority to the stronger relevant alkaline alternatives.

## Artifacts and execution

The artifacts in results/site_diagnostic_2026-09-06 contain the geometry survey, both model attempts (one import failure and one feasibility success), and the six-candidate manifest. No fully relaxed pilot or new DFT calculation ran in this phase. The successful execution took 78.625 seconds end-to-end (77.641 seconds inside candidate evaluation): gas H2O and H2 met the 0.05 eV/A force criterion; the clean slab and all nine attempted adsorbate starts did not after the deliberately limited two steps. The selected chain is failed, with zero eligible and zero unknown sites. Its finite eta is not a usable candidate prediction. Completion is never substituted for convergence. See verification.json for execution and tests.

The first real-model attempt failed during import, before an energy evaluation. The installed MACE dependency chain reached PyTorch's cache-path code, whose username lookup attempted the Unix-only pwd module in this Windows background environment. Setting TORCHINDUCTOR_CACHE_DIR to an explicit task cache permits a retry without changing packages or weights. The failed attempt remains recorded separately.

Reproduction from the repository root:

    python results/site_diagnostic_2026-09-06/structure_survey.py --out results/site_diagnostic_2026-09-06/structure_survey-reproduced.json
    python src/scripts/screen_diagnostic.py run --manifest results/site_diagnostic_2026-09-06/six_candidate_manifest.json --model-file <local-checkpoint> --out <new-output.json> --max-candidates 1

On this Windows environment, set a task-specific TORCHINDUCTOR_CACHE_DIR before the model import. The runner checks checkpoint and implementation identities before execution. A model or source change requires a new manifest; the historical results remain separate.
