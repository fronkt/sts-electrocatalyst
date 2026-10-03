# P-A restart probe — offline preparation, 2026-10-03

Frank elects the offline P-A repair/test before P-C. The production runner and
all A/B source artifacts stay unchanged. A log replay is not a repaired optimizer
and an offline test is not a production launch licence.

## Status and runtime choice

The bounded local inventory finds no pw.x/pw.exe/compiler/CMake/MPI/Docker on
PATH; WSL reports that it is not installed. This is not an exhaustive disk scan.
Anvil is preferred for the real test: its existing pinned QE7.5 environment
avoids a new local OS installation and tests the campaign build. Frank permits
Anvil if it is the suitable option, with a suggested bounded SU ceiling.

Proposed total ceiling:8 SU, one shared-partition job, four CPU cores, two hours,
memory at most6GB, one MPI rank/pool and one thread for every arm, sequentially.
The four allocated cores provide memory headroom, not concurrent trajectories.
No node-exclusive allocation, automatic retry, production slab, projection job
or allowance expansion. Confirm actual allocated/billing cores do not exceed4
before starting QE; retain Slurm allocation/accounting evidence. This is a
conservative ceiling, not a measured runtime estimate. Anvil charges shared jobs
by the larger CPU/memory allocation; even a one-core request on a node-exclusive
partition would charge the whole node. [Official accounting](https://docs.rcac.purdue.edu/userguides/anvil/jobs/)

Read-only access now passes through installed Git OpenSSH. QE package7.5
h19104ac_2 is present; executable SHA-256
1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1;
H.pbe-rrkjus_psl.1.0.0.UPF SHA-256
27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962.
The live CPU balance is36878.4SU; no queued/running user jobs. Shared is UP,
nonexclusive, CPU billing weight1, maximum1896MB/core, so6GB fits four cores.
These are current receipts, not the stale September balance. The reported
binary version and actual job allocation still need verification at execution.
The$50 literature budget does not cover this test.
No real QE invocation or new Slurm submission has occurred in this phase.

Pre-launch implementation check after source/input corrections:70 offline tests and7
subtests pass; the combined historical/new compute regressions pass261 tests and7
subtests. Coverage includes
a four-invocation process double, whole-tree sibling-history/WFC preservation,
separate checkpoint copies, missed-boundary/no-retry, actual scheduler billing
and invalid XML identity/units/status checks. These are not real-QE evidence.
The additive tiny runner and pinned88 wrapper remain separate from production.
The actual job's scheduler allocation is checked before the first QE call.
The initial independent review withheld release because failed or downgraded
copied arms could return0 and the saved checkpoint's UPF was unchecked. Those
gates now require normal convergence, negative-control history deletion/count0,
resumed inherited BFGS1/SCF2 with no fallback or fresh initialization, the exact
saved-UPF pin when present, pinned external UPF and a nonzero proposal. Adverse fixtures exercise these
conditions. The campaign binary/lib paths and one-thread environment are the
same for every arm. Initial test receipts remain separate from release checks.
The follow-up source review corrected an overly strict saved-UPF assumption:
clean-stop config/config-only does not copy UPFs into .save; only punch(all) does.
The runner checks the XML filename, pins the source UPF before every arm and
rejects a differing saved copy if one exists. An absent saved copy is recorded as
the supported arm-local-file fallback, without modifying the stopped checkpoint.
Every deck's pseudo_dir points to that arm's copied UPF, checked again after
copying; input/UPF manifests retain its path and hash. The shared external source
is not the consumed file. Restart may restore the candidate XML's pseudo_dir and
use that retained, equally pinned candidate-local copy on fallback; check the
actual read-path log. Directory paths differ, not pseudopotential contents.
[Checkpoint output](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/punch.f90),
[UPF fallback](https://github.com/QEF/q-e/blob/qe-7.5/Modules/read_pseudo.f90)
Independent final source review clears the tiny launcher, with fresh tests and
the final wrapper pin verified. Full real trajectory acceptance is still pending.

## Prospective three-arm protocol

Use H2 in a fixed cubic cell at a non-minimum separation, Gamma sampling and
explicit Cartesian bohr coordinates, subject to the retained hydrogen UPF and
binary preflight. This is an optimizer plumbing test, not electrocatalyst science
or validation of metastable-state checking. The system must require at least
three evaluated ionic geometries; an already-converged input cannot test restart.

1. Pin the actual executable SHA-256 and reported7.5 version, UPF SHA-256s,
   process/rank/pool/thread shape, all deck bytes and numerical settings. Keep
   independent scratch directories. Permit only documented restart_mode,
   outdir/prefix, arm-local pseudo_dir, stop controls and remaining-nstep differences between arms.
2. Run a continuous relaxation to convergence. Retain every evaluated geometry,
   converged SCF energy, force, BFGS counter/trust state and terminal outcome.
3. Run the candidate from the same start; during the first BFGS call,
   place prefix.EXIT and retain its path/timestamp and triggering output line.
   The observer uses the first number-of-BFGS-steps0 marker inside the call and
   retains its exact line/timestamp. Wait for QE's normal user-stop/checkpoint
   completion, not a process kill. Require exactly one evaluated XML step at
   that checkpoint; a missed boundary remains inconclusive without retry.
   Inspect the saved proposal and optimizer state before resumption. Stop timing
   cannot be inferred from JOB DONE or the later absence of EXIT.
   The initial new-trust-radius trigger was rejected at independent source review:
   it is only printed in the Wolfe-rejection branch with scf_iter>1, after a
   second XML step already exists. That cannot satisfy the one-step checkpoint.
4. Snapshot every file recursively under outdir and any distinct wfcdir with
   relative name, size and SHA-256 before resume. Preserve the complete snapshot;
   four density/XML files are not a restart contract. Resume using the same
   executable/settings/parallelization, restart_mode='restart' and the remaining
   nstep budget. QE7.5's nstep loop is per invocation, not a cumulative budget.
5. Copy that same checkpoint to isolated negative-control scratch. Run with
   from_scratch and confirm .bfgs deletion/no-file initialization and counter0.
   Preserve all three scratches and failed attempts. Do not execute retrieved
   archive scripts or change the historical checked runner.

The clean-stop boundary is important: QE checks for stop after electrons and
before move_ions, then checks again in the next SCF. An early EXIT prevents the
move. The step XML precedes move_ions and records the evaluated geometry; the
post-move config checkpoint holds the proposal. The last energy/force belongs
to the former, and the first resumed evaluation must match the latter.
[QE7.5 loop](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/run_pwscf.f90),
[SCF stop check](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/electrons.f90),
[stop handling](https://github.com/QEF/q-e/blob/qe-7.5/Modules/check_stop.f90)

The first optimizer call prints BFGS count0, saves count1, then moves. The first
resumed optimizer call should therefore print saved count1, with its SCF counter
advancing; do not require an immediate printed count2. Convergence can remove
.bfgs normally. A recognized user stop has XML exit_status255; shell return0
versus255 depends on the build. The marker, saved status, normal completion and
checkpoint are required together, not a shell return-code assumption.

## Acceptance, before repairing a production runner

Require clean converged SCFs, real negative-control reset, candidate checkpoint
consumption and advancing optimizer state, and ordered full-trajectory agreement
with continuous control. Reject restart-disabled fallback, missing checkpoint,
fresh-init BFGS banner or first resumed count0. An in-algorithm later history
reset is not by itself proof of from-scratch initialization; retain and interpret
it. Counts alone are insufficient: inspect history, inverse-Hessian/trust state
and saved geometry correspondence.
[Input fallback/cleanup](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/input.f90),
[optimizer state](https://github.com/QEF/q-e/blob/qe-7.5/Modules/bfgs_module.f90),
[official restart contract](https://www.quantum-espresso.org/Doc/INPUT_PW.html)

Proposed tiny-test tolerances, not production threshold changes: maximum absolute
energy difference1e-6 Ry, Cartesian position difference1e-5 bohr and force
difference1e-5 Ry/bohr at each corresponding evaluated step and endpoint. Require
equal ordered atom identities. No endpoint-only pass, interpolation, periodic
remapping or energy/proposal mismatch. Retain any repeated boundary evaluation
and explicit adjudication; do not silently discard a record to match lengths.

The additive pa_restart_diagnostic.py only summarizes retained logs and compares
reviewed trajectory transcriptions. Its source citations are shape-checked,
not opened/hash-verified by the comparator. It does not inspect checkpoint
contents, binaries, UPFs, actual exit status or stop receipts. Even a numerical
match is OFFLINE_TRANSCRIPTION_COMPARISON_ONLY, production_accepted=false and
real_qe_probe_pending=true. Tests of fixtures and old ArmA logs cannot satisfy
the real three-arm acceptance above. The checked receipt separately verifies
the eight original mirrored runtime/output hashes and corrects the initial
empty-regex extraction without replacing that initial receipt.

Only after real acceptance: additive repaired P-A runner, independent regression
review and a new dated production count/cost/cap proposal. A plumbing pass alone
does not validate P-A's fresh-SCF comparison/reseed behavior on the catalyst slab.
