# HEA DFT continuation after the pilot — 2026-09-07

The next batch tests whether the fixed-geometry ordering of the two retained Ni31Cr29Cu5Mn35 seed-0 endpoints survives electronic-state and Hubbard-projector choices. It completes the two-projector × two-metal-start × two-fragment-start factorial: 14 new SCFs plus the two accepted atomic baselines from array 20470747. These are distinct from the historical seed-1 winning chain.

The exact existing input bytes and ordered jobs are in results/hea_followup_2026-09-07/launch_spec.json; detailed mappings and costs are in plan.json. Every comparison has both endpoints. The original 48-control menu, pilot inputs and outputs remain unchanged.

Resources: NP128/nk8, one job at a time, four hours per task, no requeue or automatic retry. The SCF planning estimate is 2619.09 core-hours; it excludes projection and uncalibrated spin-start iteration overhead. The completed pilot used 290.99 core-hours. The requested allocation ceiling is 7168 core-hours for this batch; this is not a forecast. Available CPU balance before submission: 58853.7 SU.

The new runner retains the established MPI layout. It checks the frozen spec, validator and scientific input hashes at task start, then requires a valid finite SCF and complete ordered forces. Projection must contain a complete ordered atom-resolved charge/spin table before wavefunction cleanup. Any failure retains scratch. Runtime input differs only in scratch and pseudopotential paths and the operational max_seconds=13200 setting, reserving a nominal 20 minutes within the four-hour allocation for exit/projection. QE stopping at that limit is a failed attempt, not a successful SCF; Slurm enforces the outer cap. This margin is not a guarantee against an abrupt scheduler stop.

Readout: retain all starts, including failures and higher-energy states. For each matched projector/start compute E(pull2.10)-E(builder), then its difference from the appropriate baseline. Within each projector report the lowest endpoint energies found among the four starts, their magnetic textures and paired gap; this does not prove a magnetic ground state. Compare paired gaps across projectors, never absolute total energies across different projector Hamiltonians to choose a winner. Using the same inherited U with different projectors tests model dependence, not transferable-U calibration. Forces above 0.05 eV/A remain a stationarity diagnostic and are not SCF failures.

The sequence after this batch is:

1. Check paired tighter-SCF convergence on the electronic basins found here, then cutoff/smearing sensitivity and a joint tighter-setting confirmation. Retain changed electronic basins explicitly.
2. Reassess memory before the denser k mesh. The pilot exceeded the old memory estimate; a 6×3 mesh needs a measured resource plan and a same-mesh nk4 baseline to separate decomposition sensitivity.
3. DFT-relax both endpoints under the selected numerical protocol, fixed cell and original slab constraints. Require ionic/SCF/force convergence and a fresh connectivity audit; retain distinct basins and failed attempts.
4. Apply the validated protocol to the actual seed-1 winning chain and frozen discovery/held-out panel before revising a shortlist. All 12 frozen composition selections now have coordinates; two discovery states remain MACE-unconverged and must stay in the records.

Starting magnetizations are unconstrained initial guesses; projector and relaxation semantics follow the [QE input manual](https://www.quantum-espresso.org/Doc/INPUT_PW.html) and [Hubbard input guide](https://www.quantum-espresso.org/Doc/user_guide_PDF/Hubbard_input.pdf). No new pass/fail accuracy threshold, catalytic eta, kinetic mechanism or ranking follows from this submission.

Census checkpoint at 20:34 UTC: primary 12/12 compositions complete (144 sites), all seven 2×2 endmembers complete, four OMAT-0 jobs active. The original protected scientific code/manifests/decks match their recorded bytes; only the previously documented runner-recovery implementation differs from the older 149-file snapshot.

Verification and launch status: pending below.

Runtime preflight: the system Python is 3.6.8, so the batch explicitly uses the already-installed Python 3.9.5 at /apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3. Direct interpreter/import checks passed without loading modules or changing the QE environment. All six pseudopotential MD5s match the pilot, and selected companion/original-equivalent job paths show no prior attempts.

Local verification: 197 passed, three Windows symlink cases skipped. This covers the new guard and QC, both real pilot outputs, follow-up shell integration, original pilot regressions, and existing force/control tests. Both Bash syntax checks and the exact 48-control bundle check passed. All 200 protected current scientific/pilot file hashes match. Independent scientific and execution reviews found no remaining launch defect.

Anvil driver preflight at 20:51 UTC refused the initial resource comment because it appended explanatory text to the exact NP/NCONC directive. No scheduler job was submitted. The resource values and scientific decks are unchanged; the manifest now places the directive on its own line. The guard receives a matching format regression before the repeat preflight. The initial transfer and refusal are retained separately.

Header correction verification: 67 focused checks passed, three Windows symlink cases skipped; both Bash syntax checks passed. The exact header requirement now lives in the guarded preflight. The correction changes launch metadata and its guard only; all 14 scientific input bytes and the four-hour/concurrency-one limits are unchanged.

## Submission and initial status

Corrected commit 4b4c3f0 was pushed before the final 22-file transfer. Every staged file matches its committed bytes. The actual Anvil driver accepted all 14 inputs with zero stale/bad records, and the deployed Python 3.9 validator accepted both real pilot outputs with 75 ordered atoms each.

Array **20484293** was submitted held at 20:57:44 UTC and released at **21:02:36 UTC** after verifying all 14 tasks, throttle one, 128 CPUs/tasks, one CPU/task, exactly one node (Slurm expresses the request as 1-1), shared partition, 237G memory, four-hour limits, no requeue, and the exact exclusions. Manifest and .lines are read-only. All 22 staged hashes were rechecked immediately before release.

The immediate release snapshot shows all 14 tasks PENDING; no new scientific result is claimed. A transient verification-channel stall was resolved by closing each bounded SSH channel explicitly; only the stalled local verification helper was stopped. The held array was not resubmitted. Both the original resource-header refusal and held-check evidence are retained.

All 200 protected current scientific and pilot files still match. The 14 jobs complete the next electronic-state test when their outputs pass the recorded QC; numerical sensitivity, relaxation and candidate validation remain dependent work. Launch evidence and the pending paired readout are in results/hea_followup_2026-09-07/.

## Status and retention repair — 2026-09-08 03:55 UTC

Array 20484293 has one scientifically valid recovered endpoint, one nonconverged SCF, one running task and eleven tasks pending under the concurrency-one limit. Slurm records the first two tasks as FAILED; the first status reflects a retention defect after successful SCF and projection. This is a partial readout, not a completed factorial.

Task 1, ortho/baseline builder, converged in 78 iterations (final estimated SCF accuracy 9.7e-7 Ry) and passed complete 75-atom force/projection QC. Its free-coordinate maximum force is 1.44956 eV/A, so the geometry is not a DFT minimum. QE completed both executables, but the runner required charge-density.dat when this installation saves charge-density.hdf5. The density copy and source scratch were intact. All 11 non-wavefunction files matched their source SHA256 hashes; XML parsing, nonempty density and HDF5 signature checks passed before promoting the pending density directory. No DFT was repeated and all scratch/wavefunctions remain preserved. Historical Slurm exit 14 is unchanged.

The fixed builder geometry has projected HO2 atom moments -0.0023, -0.0019 and +0.0001 muB (sum -0.0041), compared with +1.0430 muB in the atomic-projector pilot. Total/absolute magnetization is 37.08/64.62 muB versus 38.09/64.08 in the pilot. This single converged follow-up shows projector sensitivity in the fragment's projected electronic character. It does not establish a physical singlet, the correct electronic state or a magnetic ground state; the remaining initial-spin controls are needed. Absolute total energies across different projector Hamiltonians are not a selection criterion.

Task 2, ortho/baseline pull2.10, exhausted max_seconds=13200 without SCF convergence (about 265 iterations; last estimated accuracy 9.3777e-4 Ry against the 1e-6 Ry target). The runner correctly rejected it despite JOB DONE. No accepted final energy or projection is available; scratch/restart data are preserved and no retry was submitted. Consequently the ortho baseline paired energy gap remains unavailable.

At 03:55:30 UTC, task 3 (atomic/metal_alternating builder) is RUNNING on a206, about 1 h 37 min in, at iteration 114 with latest estimated SCF accuracy 1.644e-5 Ry. Tasks 4-14 remain PENDING/JobArrayTaskLimit. No new paired gap or candidate-ranking update follows yet.

The future local runner now accepts either nonempty DAT or HDF5 density. Seventeen shell-integration checks passed, including HDF5-only success and empty-density rejection; Bash syntax checks passed. The active array retains Slurm's original copied runner, so subsequent converged tasks may encounter the same retention flag and require file-only recovery. No running/queued scientific settings or scheduler jobs were changed.

Both stopped jobs' runtime decks differ from their frozen inputs only by the declared scratch/pseudopotential paths and operational time limit; all printed pseudopotential MD5s match the pilot. All 12 downloaded raw/input/QC/log files match remote SHA256 hashes. Status snapshots, recovery hashes, identity checks and test results are retained in results/hea_followup_2026-09-07/status_2026-09-08_0347/. The pending paired readout distinguishes scientific validity from scheduler failure. Next: finish the remaining controls, inspect electronic basins and record all failures before selecting any explicit convergence-recovery attempt or proceeding to paired numerical tests.
