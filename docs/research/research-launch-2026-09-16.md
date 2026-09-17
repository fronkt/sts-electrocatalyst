# Approved research launch — 2026-09-16

The current [operating decisions](research-decisions-2026-09-16.md) approve the fixed historical HEA panel/pilot, Ru pseudopotential controls and the base Ru/Ir/Ti BEEF program. S8 permits feasibility work and holds a superior-melt selection; no current ranking is promoted to physical validation.

The scientific code, decisions, reviewed cross-model results, original pending projection output and lessons are pushed in commit `3a5f707230432a54410006e98e0694c146f56c34`. All 201 focused tests passed; builders verify all 48 input decks unchanged. The initial Windows-only fixture line-ending failure was corrected without weakening the execution guard. Remote transfer verified 66 files against the committed bytes; remote Python 3.9 compilation and both shell syntax checks passed.

| Array | Work | Tasks | Scheduler limit per task | State at last check |
|---|---|---:|---|---|
| 20781971 | HEA historical branch panel | 10 | 6 hours, 128 CPUs | Released; pending priority |
| 20781972 | HEA two retained-chain pilot | 12 | 6 hours, 128 CPUs | Released; pending priority |
| 20781970 | Ru GBRV pseudopotential controls | 12 | 35 minutes, 128 CPUs | Released; pending priority |
| 20781967 | BEEF H2, H2O and Ru bare-slab capability checks | 3 | 1 hour, 128 CPUs | Released; pending priority |

All 37 task allocations were inspected while held, then released. No new DFT result exists at this snapshot. Scheduler estimates are tentative, recorded in `results/research_launch_2026-09-16/queue_estimates.log`.

The remaining eleven BEEF tasks are authorized, with a one-hour scheduler limit each. `anvil/74_release_beef.slurm` submits them only after the complete three-task preflight array succeeds and the submitter independently verifies all three QC receipts and their input/output hashes. It then inspects the eleven held allocations before release. Its own ten-minute, one-CPU allocation is only a submission coordinator (at most 1/6 CPU SU); no DFT executes there. A failed preflight prevents expansion. No replacement gases or truncated member ensemble are allowed.

The initial 37 jobs have a combined scheduler ceiling of 18,176 CPU SU; the eleven conditional tasks add 1,408, for 19,584 plus at most 1/6 for the coordinator. These are maximum reservations, not expected usage. The initial balance was 53,217.8 CPU SU. Each HEA SCF also has its tighter individual time/iteration bound; all attempts preserve raw output and scratch.

Evidence: `results/research_launch_2026-09-16/boundary.json`, `transfer.json`, `submission.json`, `launch_spec.json`, `tests.json` and startup snapshots. Completion, actual charged time and scientific readouts remain pending. The September 13 cross-model completion is separately reviewed and banked; it does not supply a unique validated winner.

## Automatic continuation armed

Coordinator job **20782047** is submitted and released with dependency `afterok:20781967_*` (all preflight array tasks). Slurm confirms one CPU, 1 GB, ten minutes, no requeue, account che260157 and PENDING/Dependency. The coordinator script was pushed as 197e429 before transfer and submission; its shell syntax and exact transfer hash pass. Its separate receipt is `results/research_launch_2026-09-16/continuation_gate.json`. The remaining eleven scientific tasks are not yet submitted and will receive their own array ID only after successful preflight and QC.
