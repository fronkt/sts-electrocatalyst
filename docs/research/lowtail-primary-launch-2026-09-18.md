# Primary Cr relaxation launch — 2026-09-18

The user instructed continuation after the nine-primary-relaxation proposal. This authorizes the nine atomic-projector legs at three Cr sites: Cu8Cr23Mn35Co34 seed20/site2, Ni31Cr29Cu5Mn35 seed1/site0 and Fe25Co25Ni25Cr25 seed2/site0. Each site has the clean slab, the reconstructed census *O endpoint and the unlifted *O start. All eighteen prepared input decks remain byte-identical; the nine ortho controls remain outside this launch.

## Scientific question and interpretation

The question is whether constrained DFT+U relaxation from both *O starts retains the lifted Cr basin. The completed fixed-coordinate evidence now covers 65 historical/new outputs: 46 accepted realizations, 19 excluded and zero unidentified. The three available reconstructed Cr sites show local short Cr–O bond compression; the axial-gap response differs between sites. These gradients do not establish a DFT minimum or select a census winner. See the [refreshed force analysis](lowtail-dft-validation-refresh-2026-09-18.md).

The September 16 geometry, Hubbard U, FM start, k mesh, cutoffs, constraint mask and basin thresholds remain fixed. The 0.4811 eV energy-order margin is a historical OOH spin-start spread, not a calibrated uncertainty for the new O basins. A failed clean-slab leg leaves any MACE-referenced lift explicitly provisional. No overpotential or composition ranking follows from these nine legs alone.

## Bounded execution

The original prepared route `46_a0.slurm` cannot enforce the registered stop/scratch rules. The authorized route is `anvil/75_lowtail_relaxation.slurm` with `src/dft/lowtail_batch.py`, using the reviewed process supervisor from `research_batch.py`. The fixed-coordinate September 16 launch contract remains separate.

- One array, nine tasks, concurrency one; 128 MPI ranks, eight pools, 237 GiB memory, existing ten-node exclusion list, no requeue or automatic retry.
- Stop when any ionic step begins SCF iteration 127 or its frozen leg wall is reached (54,236–58,347 seconds). Preserve scratch and raw output on every outcome; a stopped leg supplies no scientific energy or basin.
- Projection is bounded at 1,800 seconds per successful relaxation. Retain wavefunctions, density and XML.
- Scheduler limit is 1,005 minutes per task, including projection and shutdown allowance. Expected relaxation cost from the refreshed model is 5,424.3 core-hours; all refreshed atomic ceilings fit within the original per-leg limits.
- Frozen relaxation ceilings sum to 17,925.23 core-hours; projection allowance adds at most 576.00. The scheduler ceiling, including unused per-row padding, is 19,296.00 core-hours. Live balance before launch was 49,906.9 CPU SU; submission rechecks it. GPU allocation is unused.

The runtime preflight checks pinned source/input bytes, manifest order, pseudopotential MD5s, prior outputs/scratch and primary-only membership. Submission is held until actual Slurm resources and exclusions pass inspection, then the array is released. Local staging reads exact bytes from the pushed boundary commit and verifies remote copies.

## Acceptance and evidence

The readout now calls the repaired canonical parser directly. It no longer rewrites IEEE exception notices or patches the wall parser. Benign underflow/denormal notes pass; severe, mixed or unknown notices reject. A leg needs explicit BFGS convergence, finite and consistent SCF/final energies, complete final force/coordinate records in the correct order, unchanged fixed atoms and the registered componentwise force threshold. Successful process exit alone is insufficient.

Independent checks found consistent BFGS/SCF/energy/force counts in 98 banked converged relaxations. All Cartesian force components and energies from the 15 newly accepted fixed-coordinate outputs agree exactly with an independent extraction. Focused tests cover malformed and severe outputs, stop limits, stale artifacts, scratch preservation and successful projection/density retention.

Machine-readable records are under `results/lowtail_dft_2026-09-18/`: `launch_spec.json`, `operating_decisions.json`, `deck_plan.json`, `cost_refresh.json`, `independent_acceptance_audit.json`, `boundary.json`, `transfer.json`, `submission.json` and `startup.json`. Submission/startup files are populated only after those acts occur. Scientific results remain pending until the raw relaxation outputs pass the readout.

## Released array and collection

Array **20813525** was released after held-resource inspection. Task 1, the Cu8Cr23Mn35Co34 seed20/site2 clean slab, started on `a072` at 04:34:03 UTC on September 18. Tasks 2–9 wait on the concurrency-one limit. The first raw output confirms electronic iterations are advancing; it is not a converged result. A Slurm one-node request appears as `NumNodes=1-1` while pending; the inspected guard accepts that exact range and no larger range. No duplicate array was submitted.

After its source is banked, `src/dft/lowtail_followthrough.py --array 20813525` observes accounting every five minutes for at most 240 hours. It requires all nine explicit task records to be terminal before mirroring the named output, runtime-input, QC, projection and failure artifacts. It pins source/input bytes at startup, refuses conflicting local evidence, checks QC identities and parses the projection. Terminal missing/failed evidence stays a failure in the nine-leg denominator. The nine unrun ortho controls are outside this primary readout.

The local watcher records current state under `results/lowtail_dft_2026-09-18/followthrough/`; `--status` checks the age of the last observation. It stops at `READY_FOR_REVIEW` after collection and numerical scoring. It never restarts calculations or launches controls. Independent scientific interpretation remains a separate step. The focused watcher and readout suite passed **56 tests**; the receipt and first-output observation are preserved under `verification/`.
