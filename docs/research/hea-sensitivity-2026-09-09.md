# Atomic exception diagnosis and paired numerical sensitivity — September 9, 2026

The next experiments address two different uncertainties from the [completed numerical stage](hea-numerical-2026-09-08.md): an unexplained invalid-operation flag in the atomic builder, and unmeasured cutoff/smearing sensitivity of the accepted ortho endpoint pair. Both endpoints retain the seed-0 geometry and original positional constraints. The accepted ortho gap is -2.129781595 eV; free-coordinate forces near 1.4 eV/Å show that neither geometry is a DFT minimum. These controls do not revise candidate ranking.

## Experiments and order

One bounded atomic reproduction uses the original accepted atomic fragment checkpoint and the exact previously rejected tight input bytes, in a separate working directory. It retains the same pw.x/projwfc.x/MPI binaries, NP128/nk8, OMP1 and four-hour limit. The only intended execution change is stderr capture for every MPI rank. Raw stdout, launcher stderr and all rank stderr files remain available; strict QC sees their combined contents. A clean reproduction would not clear the original flagged attempt. Repeated invalid operation requires operation-level diagnosis, potentially an exception-trapping diagnostic build. There is no automatic retry.

The six ortho jobs follow in a serial array with an afterany dependency on the diagnostic, so a diagnostic failure does not block independent numerical science. Each pair starts from the same two accepted tight checkpoints, copied independently into private destinations.

| Pair | Wavefunction cutoff (Ry) | Density cutoff (Ry) | MV width (Ry) |
|---|---:|---:|---:|
| Existing accepted reference | 80 | 640 | 0.010 |
| Wavefunction cutoff | 100 | 640 | 0.010 |
| Charge-density cutoff | 80 | 800 | 0.010 |
| Smearing width | 80 | 640 | 0.005 |

All six retain conv_thr=1e-8 Ry, mixing_beta=0.3, a 4×2×1 unshifted mesh, Hubbard parameters/projectors, pseudopotentials, cell, atom order, geometry and positional masks. Exact input differences are the private outdir and the single named parameter. The [launch specification](../../results/hea_sensitivity_2026-09-09/launch_spec.json), [input comparison](../../results/hea_sensitivity_2026-09-09/input_audit.json), and [source inventory](../../results/hea_sensitivity_2026-09-09/source_checkpoints.json) retain identities and hashes.

## Initialization and scientific interpretation

These are new SCFs with from_scratch and file-initialized density/wavefunctions. QE 7.5's readers support larger reciprocal-space arrays and zero-padding on cutoff increases. However, the collected-wavefunction reader lacks general compatibility checks; a successful file read alone does not certify exact basis embedding or basin preservation. The guard verifies source metadata and unchanged geometry, cell, k sampling, spin and species; final force, spin and occupation diagnostics determine whether comparisons support a common sampled branch. [QE 7.5 binary reader](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/Modules/io_base.f90), [collected-wavefunction reader](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/pw_restart_new.f90).

For every accepted endpoint, report changes in energy, free-coordinate force vectors, magnetization, per-atom/fragment Löwdin moments, and Hubbard occupation matrices/eigenvalues. Pair differences require both endpoints to pass raw SCF/projection QC, exact runtime-input checks and checkpoint/startup checks. A partial or rejected pair has no accepted energy gap. Preserve state changes as possible competing electronic solutions; do not relabel them numerical error.

The finite-smearing total energy contains a smearing contribution. Report the printed -TS term separately and compare consistent quantities across widths; no zero-width energy extrapolation is inferred from this two-width check. Smearing also interacts with k sampling, so a smaller width is not by itself evidence of higher accuracy. [QE input description](https://www.quantum-espresso.org/Doc/INPUT_PW.html), [QE energy bookkeeping](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/electrons.f90).

## Resources and continuation

Each task has 128 ranks, eight pools, a four-hour allocation and QE max_seconds=13200. The six sensitivity jobs have a 3072 core-hour ceiling; the single diagnostic adds 512, giving 3584 total. The serial dependency keeps the combined workload at one job at a time. This ceiling is not a runtime forecast. The accepted ortho reference pair used 138.489 core-hours, a historical comparator only. Preflight at 2026-09-10T02:37:55 UTC (September 9, 22:37:55 EDT) found an empty user queue, 54906.5 CPU SU available, and 4.7 TB free.

The two accepted checkpoints contain 54 files totaling 31,628,678,473 bytes; three separate copies per endpoint total 94,886,035,419 bytes before new output growth. Full original and new scratch remain retained. QE reported roughly 106.47 GB total estimated RAM for the reference. A 25% cutoff increase gives an approximate 1.40 plane-wave/grid scaling factor and roughly 149 GB under simple proportional scaling; this is not a measured peak. The 237 GB allocation remains the cap, with actual memory inspected before any denser mesh.

After these independent controls finish, assess accepted pair gaps and state continuity before choosing a joint tighter setting. Then calibrate memory for a denser commensurate k mesh, with a same-mesh baseline if MPI pool layout changes. Proceed to fixed-cell DFT relaxation under the original positional constraints once the numerical protocol is supported. The actual seed-1 winner and frozen discovery/held-out chains follow that validation. Neither SCF convergence nor fixed-geometry energy ordering establishes relaxed thermodynamics, overpotential or a kinetic pathway.

## Verification and execution

All 270 targeted tests passed, with two Windows symlink skips: 37 sensitivity runner/readout checks, 210 source-guard/shared-parser checks, and 23 diagnostic lifecycle checks. Five shell syntax checks and Python syntax checks passed; prior scientific helpers, runners and input/output directories have no changes. Independent scientific and execution reviews passed.

The diagnostic tests include a nonzero-rank invalid flag, missing rank capture, launcher stderr, altered raw evidence/receipt, incomplete retention and a late evidence failure after projection. Final scheduler success requires the final evidence summary to accept the complete new endpoint. The prior flagged endpoint always remains rejected. The sensitivity tests preserve unavailable pairs and reject changed source identities, metadata, input parameters, startup fallback and invalid flags.

The [verification record](../../results/hea_sensitivity_2026-09-09/verification.json) pins the deployment files and test results. The [pre-run readout](../../results/hea_sensitivity_2026-09-09/pending_readout.json) has two accepted sources, six pending targets and no new paired gaps. The verified staging and release are recorded below; no new scientific result is claimed.

## Submission and initial scheduler state

Implementation commit 63539b4b8932ba426594b3fe9694ef326ba8e1d6 was verified on GitHub before staging. All 30 deployment/dependency files match on Anvil. Both actual Python 3.9 preflights verified the full accepted checkpoint inventories; all five Bash syntax checks passed on the cluster. The QE and MPI binaries match their recorded identities.

Diagnostic array **20543029** (one task) and sensitivity array **20543035** (six tasks) were submitted held. Slurm confirmed NP128, eight pools from the frozen inputs/runner, concurrency one, 237G memory, shared partition, four-hour limits, no requeue and all ten requested node exclusions. The scripts copied into Slurm match the committed runner bytes exactly. The sensitivity array has an **afterany:20543029** dependency.

Both holds were released at **2026-09-10T03:00:35.159160 UTC (September 9, 23:00:35 EDT)**, after another complete deployment-hash check. The dependent sensitivity array was released first; it cannot start until the diagnostic ends.

At **2026-09-10T03:01:16 UTC (September 9, 23:01:16 EDT)**, the diagnostic was PENDING and all six sensitivity tasks were PENDING/Dependency. No new SCF output or checkpoint-clone receipt existed in the initial snapshot. Actual file startup, convergence, rank-attributed exception outcome, projection acceptance, pair-gap sensitivity and realized allocation remain pending. The launch establishes execution readiness, not scientific completion.

The [staging receipt](../../results/hea_sensitivity_2026-09-09/staging_receipt.json), [held resource/script checks](../../results/hea_sensitivity_2026-09-09/held_submission.json), [release record](../../results/hea_sensitivity_2026-09-09/release.json), and [initial status](../../results/hea_sensitivity_2026-09-09/initial_status.json) retain the execution evidence. The next readout must keep rejected or incomplete endpoints out of paired comparisons, inspect electronic-state continuity, and assess independent sensitivity before selecting the joint-setting and k-mesh experiments.

The final live check at **2026-09-10T03:04:58 UTC (September 9, 23:04:58 EDT)** found the diagnostic PENDING/Priority and all six sensitivity tasks PENDING/Dependency, with no new SCF output. All six live pseudopotential files match the SHA256 identities in both accepted ortho checkpoints. The [startup and pseudopotential snapshot](../../results/hea_sensitivity_2026-09-09/startup_status.json) retains these checks.
