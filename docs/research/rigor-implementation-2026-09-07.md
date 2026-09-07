# Rigor work alongside the census — 2026-09-07

## Scientific result available now

The frozen census readout reproduces both completed composition minima. Ni31Cr29Cu5Mn35 is 0.4399960638886986 V versus 0.43999606379672596 V in the historical MACE screen (difference 9.20e-11 V). Its uniquely matched historical winner is seed 1/site 0 on Cr: OOH is bound (nearest metal distance 1.97109 A), O-O is 1.37978 A, hydrogen remains on the adsorbate, and all three states meet the force criterion. The O intermediate triggers the pre-stated reconstruction flag. Thus the winner is adsorbate-intact under the census rule but not intact under the stricter rule that includes reconstruction. These are MLIP diagnostics, not DFT validation or electrode performance. The equiatomic minimum reproduces within 4.52e-10 V. Both winners retain adsorbate-intact OOH; the previous seed-0 leader anomaly cannot be generalized to the historical winner.

Evidence: results/hea_rigor_2026-09-07/census_snapshot/reproduction.json and per_site.json. The snapshot is partial: two of 103 manifests and 24 sites; no full-pool ranking is claimed. Source result files are the complete leader/equiatomic census records, and their normalized hashes accompany the readout. The running census code, manifests and protocol are unchanged.

## Validation selection fixed before materialization

Boundary commit be7d72b fixes results/hea_validation_2026-09-07/plan.json and its preparation code. It contains 12 composition-only-selected chain slots (8 discovery, 4 held out from future DFT-label fitting), plus two previously examined chains and the historical winner as separate targeted audits. Both partitions cover all six elements. This is a first-stage pilot, not a proof of ranking accuracy. The fixed expansion is all three seeds/four sites per composition with the same group partition. Changes informed by held-out labels require a fresh evaluation set.

The separate geometry snapshot contains 5 ready chain slots, 20 ready state slots, 18 unique geometries and 40 pending state slots. No missing site was replaced by a more favorable one. Ready includes retained unconverged or chemically changed structures for diagnosis; it does not mean chemically validated.

## DFT controls

runs/hea/controls_2026-09-07/requests.json binds 48 control requests on four retained endpoints and both Hubbard projectors. Eight are exact baseline twins and can reuse the corresponding original calculation after matching input/output checks; the other 40 are additional spin/numerical controls. Split species preserve elemental U and pseudopotentials and stay within the banked QE build's 10-species limit. The 6x3x1 mesh uses 4 MPI pools; its modeled memory 185.4 GB is within the 237 GB node. A same-mesh baseline at that decomposition is needed before tight numerical certification or if decomposition sensitivity appears.

Planning is 10,557.4 core-hours for all 48, or 9,017.3 incremental with all 8 original baselines reused. These extrapolations are not measured HEA costs. Unknown spin-basin, SCF and projection overhead remains. The initial two-job atomic smoke is 332.9 core-hours planned. Proposed Slurm limit 4 h/job gives 1024 requested core-hours for two 128-core jobs, excluding retries and site-specific billing changes; nothing automatically launches or expands.

The full/smoke manifests remain NOT LICENSED. Existing anvil/47_submit_a0.sh:54-61 refuses them until the user's HEA settings election. The concrete smoke parameters are in results/hea_rigor_2026-09-07/smoke_request.json. After authorization, SBATCH_TIMELIMIT=04:00:00 overrides the batch script's 48 h setting; confirm the accepted TimeLimit in Slurm before execution. This environment behavior is documented at https://slurm.schedmd.com/sbatch.html . The existing submitter's printed 48 h worst-case figure does not account for that environment override. No remote state or allocation balance was asserted or modified in this session.

## Diagnostics and follow-up

src/dft/hea_force_audit.py reads one completed fixed-geometry SCF, verifies full ordered atom/type force tables, masks each Cartesian constraint, converts Ry/bohr to eV/A, and keeps high geometry residuals separate from SCF failures. A real banked Cr output passes its parser and has free-coordinate fmax 1.3319 eV/A; this is an existing fixed-geometry result, not a newly discovered bad SCF or a relaxed-geometry claim. Its input/output byte hashes accompany the check. The caller must still establish runtime-deck correspondence.

src/scripts/prepare_failure_benchmark.py maps the selection snapshot to 45 adsorbate-state cases. Fifteen have geometry/convergence features; every DFT truth, ranking value and unavailable ensemble spread remains null. Benchmark status is PENDING. Discovery, audit and held-out metrics remain separate, and selective-risk curves retain whole tied-score groups. Geometry flags are predictors and cannot label their own success. The prospective 0.10 eV reference-error criterion and 0.05 eV ranking tolerance are diagnostic choices, not calibrated probabilities; see failure-benchmark-design-2026-09-07.md.

src/hea_oer/pathway_audit.py checks balanced ordered CHE cycles, common references and surface regeneration. The bridge template includes a potential-independent O2-release step and remains PENDING without its free energies. No missing branch is filled with the conventional OOH correction. Actual endpoint/phase calculations still need scientifically validated geometries and the corresponding computational runs. The active-surface matrix and dependencies are in pathway-active-phase-2026-09-07.md; the existing bulk Pourbaix gate is explicitly distinguished from surface stability.

## Verification

Full suite: 855 passed, 8 skipped, with 57 existing spglib deprecation warnings. A clean staged checkout passes 130 focused tests and both prepared deck bundles reproduce exactly there. All 149 protected files match their starting hashes. Scoped LF attributes preserve byte-verified artifacts in Windows checkouts. The review caught and resolved missing Fe coverage, species-limit and memory issues, truthy regeneration flags, ambiguous QE calculation declarations and a missing clean-slab hash check. Final test counts and commit are recorded in tasks/todo.md and the verification artifact. No census process or original DFT input was changed.

## Ready validation inputs

runs/hea/validation_2026-09-07/inventory.json resolves the snapshot into 120 projector-specific state slots: 40 ready and 80 pending. The 40 ready slots map to 36 distinct inputs: 16 exact existing inputs are referenced and 20 new inputs are in m_validation.txt; four slots are aliases. New inputs alone have a planning estimate of 3,736.1 core-hours and maximum modeled memory 87.2 GB. The 3x cost/memory scenarios are extrapolations, not enforced resource caps. All remain NOT LICENSED.

To update readiness after more compositions finish, retain this snapshot and materialize to a new output path using the committed plan, then use a separate validation output directory. Benchmark inputs likewise use a new output directory. Do not silently overwrite this partial snapshot or mix held-out labels into development.
