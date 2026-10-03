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

## Prospective three-arm protocol

Use H2 in a fixed cubic cell at a non-minimum separation, Gamma sampling and
explicit Cartesian bohr coordinates, subject to the retained hydrogen UPF and
binary preflight. This is an optimizer plumbing test, not electrocatalyst science
or validation of metastable-state checking. The system must require at least
three evaluated ionic geometries; an already-converged input cannot test restart.

1. Pin the actual executable SHA-256 and reported7.5 version, UPF SHA-256s,
   process/rank/pool/thread shape, all deck bytes and numerical settings. Keep
   independent scratch directories. Permit only documented restart_mode,
   outdir/prefix, stop controls and remaining-nstep differences between arms.
2. Run a continuous relaxation to convergence. Retain every evaluated geometry,
   converged SCF energy, force, BFGS counter/trust state and terminal outcome.
3. Run the candidate from the same start; after the first BFGS move begins,
   place prefix.EXIT and retain its path/timestamp and triggering output line.
   Wait for QE's normal user-stop/checkpoint completion, not a process kill.
   Inspect the saved proposal and optimizer state before resumption. Stop timing
   cannot be inferred from JOB DONE or the later absence of EXIT.
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
