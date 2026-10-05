# Independent catalyst boundary-trial launch review

Initial review status: HOLD for the findings below and final verification gates.
This is a read-only implementation/source review, not an actual catalyst trial,
QE restart pass, production acceptance, or permission for additional compute.
No processes, jobs, network, Git or SSH were run by this reviewer.

## Reviewed initial bytes

| Artifact | SHA256 |
|---|---|
| src/dft/pa_qe_adapter.py | 63cbc757ec8fe12b5435f59150c03694271b9595e650be866640c9b724038656 |
| src/dft/pa_catalyst_trial.py | 40c2d24f82c61c2131e4f0bce562b5c7d4587204c0a945bb4a6d02b7c7a0d5ec |
| tests/test_pa_qe_adapter.py | 9426a77cab5c1107a5624fa12da60af3d309f8ec409356033ddb3bbfb53349d0 |
| tests/test_pa_catalyst_trial.py | 9715267d8844dd5dcd81c1f8faf388cedc96a71984fc0f23b3f17a759ce4914e |
| anvil/89_pa_catalyst_boundary_trial.slurm | 0ff3deac8c28537a197020e832903f61d47864113406c616f9f9462bb5cc1ed3 |
| source_boundary_review.md | 7efb6e27d9859eff629df0cc6dfcd90ef9e17b74819e9500ee398b5e432addac |
| initial launch_spec.json | 41b71fa531dc6d10e4537119dc1b4d5351b39448c9b7869c931de5163e81b849 |
| offline_initial.json | 6a661bc64bc2534eb97cefee8d2322ee5d1442755f528e8545043b9d82dcfcc7 |

Both modules and both tests were read completely. The wrapper, trial authority,
initial launch_spec.json, initial offline receipt and official source mapping
were also read. The source memo retains all 27 successful cached source/build
pins and the independent 72-atom seed XML/deck geometry/cell/constraint check.

## Consolidated initial findings

1. P1, observed reseed state is not yet validated. Controller 852–859 marks
   genuine_lower_state_reseed_validated after one converged from-scratch optimizer
   call seeded by the lower fresh density, without comparing that observed first
   energy with the lower fresh result. Atomic+random WFC initialization could
   converge back to the original higher state. The orchestration double's fresh
   energy is -100 while reseed is -99 (test 440–444), yet the reseed branch test
   accepts it. Before asserting genuine lower-state reseed validation, bind its
   actual first geometry/settings and energy to the lower fresh result within
   the registered energy tolerance. Failure must remain inconclusive/attempted,
   not a genuine lower-state pass or a continuity splice.

2. P1, the actual diagonalization subgroup is not bound. The adapter validates
   XML parallel shape and the controller pins launch arguments, but neither
   checks stdout's actual MPI/thread/pool and ELPA subgroup. QE's XML ndiag is
   populated with bandgroup processor count, not independent orthogonalization
   subgroup evidence (source memo). Historical catalyst stdout explicitly reports
   MPI128, threads1, npool8, proc/nbgrp/npool/nimage16 and ELPA4*4. Require and
   retain the actual registered catalyst runtime fields for each arm, with
   missing/mismatched-field adversaries. Preserve scaled tiny replay scope rather
   than imposing catalyst4*4 on an unrelated two-process fixture.

3. P2, first saved optimizer sanity is incomplete. read_bfgs validates finite
   full token count, transformed prior/gradient and counters, but does not check
   the positive saved nr_step_length, integer tr_min_hit, or inactive fixed-cell/
   non-FCP slots. First-boundary fixtures currently accept nr_step_length zero.
   Source bfgs_module312–319 zeros inactive pos/grad tails, 552 computes the NR
   length, 576–577 rejects unreasonably short length, and 844–854 saves these
   fields. Enforce these first-boundary checks or avoid claiming the stronger
   sanity validation. Full history remains copied/hash-preserved independently.

4. P2, cleanup waits are not collectively deadline-bounded. run_arm begins hard
   teardown at7180, then permits teardown waits, a process wait, and potentially
   two capture joins with further teardowns. Their conservative total can exceed
   7200 before within_per_call_cap detects it. The existing timeout test mocks
   instantaneous teardown. Aggregate reservation7320 is conservative, but does
   not itself enforce a literal7200 per-call including teardown. Bound waits to
   the remaining per-call deadline, or reserve sufficient earlier cleanup time;
   add a delayed-cleanup adversary. Killing a launcher must not be treated as
   proof that its owned remaining rank/stream group disappeared.

These are the complete initial-cycle findings from the reviewed artifacts;
the final pass must inspect their resolution together with updated pins and
fresh receipts rather than accepting only a narrative response.

## Coherent implementation features

The source-supported cycle1/cycle3 observer is anchored, uses one owned EXIT,
retains the global resumed2/3 sequence, and checks exact post-stop XML counts.
nstep30 leaves a spare iteration; MAX_XML_STEPS=0 is an environment control.
The adapter separates evaluated XML steps from the saved proposal, masks printed
forces before comparing XML/BFGS, transforms fractional optimizer positions
with the complete cell, and compares every ordered frame without dropping or
periodic remapping. Direct raw checks bind species/UPFs, U species/orbital/eV,
atomic projectors, spin starts, smearing mv and width, cutoffs, mesh and constraints.
Fresh geometry is the first evaluation; resume geometry is the saved proposal.

The fresh branch decision is written before any continuation. Failed/missing
fresh holds; a strict >10meV drop selects an intentional new-history branch;
otherwise continuation audits saved counters and all three frames. The copied
history negative control uses real startup deletion/count0, not a banner or
terminal cleanup. Full recursive checkpoint inventories include directories,
WFC/siblings and immutable copies, with link/special/hardlink refusal. Conda
external executable hardlinks are a narrow read-only exception with rehashing.

The wrapper requests only one wholenode128-task/1-thread/200G/16h/no-requeue job.
The controller separately checks actual RUNNING Slurm CPU/billing128, node1,
memory<=200GiB, no array/restart/dependency, total2048CPU SU, <=six sequential
calls, and a full7320 remaining reservation before each call. Source, executable,
MPI, UPF, seed and dependency pins are reopened; stale EXIT is rejected.
No automatic retry, trajectory splice, production or melt release is present.

## Verification evidence and remaining gates

The retained offline_initial.json reports 83 evidence tests, 451 compute tests,
seven passing subtests, three Windows filesystem skips, both scientific
verifiers, and unchanged9816tracked/21unrelated baseline. Its recorded module/
test pins match the initial reviewed bytes. This reviewer read that receipt;
the reviewer did not independently execute those tests. They are offline
implementation/process-double results, not catalyst runtime proof.

Before a release decision, review the corrected frozen bytes and spec pins,
the final fresh local verification receipt, Linux filesystem guard exercise,
raw tiny Linux adapter replay, and isolated checkout identity. Actual live
allocation, checkpoint consumption, evaluated-count and scientific acceptance
remain runtime gates after any preparation-only release. No final GO is given
by this initial review.
