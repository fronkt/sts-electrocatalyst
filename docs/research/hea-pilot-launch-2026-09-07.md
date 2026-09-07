# Approved HEA DFT pilot — 2026-09-07

The user approved the prepared two-job atomic-projector leader endpoint pilot. Exact scope and input hashes are in results/hea_pilot_2026-09-07/approval.json. The separate approved manifest keeps the original prepared bundles reproducible. Only the two retained seed-0 endpoint configurations run; this does not validate the historical seed-1 winning chain.

Anvil preflight: che260157 CPU balance 59,144.7 SU; queue empty at the recorded check. Six UPFs match the prepared hashes, QE is 7.5 h19104ac_2, the existing queue driver matches local bytes, and the parity marker is present. No existing original or companion attempt was found. Anvil is an established staged run tree without a Git checkout, so exact committed files are transferred after the local push, with byte verification before execution.

The dedicated pilot runner keeps the established NP128/nk8 launch shape and inline projection. It adds a four-hour scheduler limit, stricter completion checks, refusal of prior scratch/output, and preservation of wavefunctions when SCF, projection or density retention fails. The dedicated submitter preserves the original parity, licensing, exclusion and driver-preflight guards. It submits exactly two tasks, concurrency one, initially held; accepted Slurm settings are checked before release. Original runners and scientific decks are unchanged.

Four hours includes SCF, projection and cleanup. The 332.936 core-hour planning figure models only SCF; the 1024 requested core-hour bound covers two four-hour jobs at 128 cores, excluding retries and site-specific billing changes. There are no automatic retries or expansion. The earlier 3x wall/126-iteration monitoring suggestions are diagnostic review triggers, not a running watchdog; Slurm enforces the four-hour bound.

Readout requirements: independently check SCF convergence, finite final energy and force tables, matching runtime input and UPF hashes, completed projection with local moments, and scheduler accounting. A Slurm COMPLETED status alone is insufficient. Report paired E(pull2.10)-E(builder) only after both acceptable SCFs; magnetic ground state, pathway free energies, relaxed ranking and catalytic performance remain unresolved.

Scheduler hold/release behavior: https://slurm.schedmd.com/sbatch.html and https://slurm.schedmd.com/scontrol.html.

Verification before staging: both Bash syntax checks passed; 28 runner mock tests and 16 submitter mock tests passed on Windows/Git Bash, plus 50 existing controls/force tests and the exact frozen controls-bundle check. Independent review found no substantive errors. All 149 protected scientific files matched their starting hashes. The original 46/47 launch scripts, driver, prepared smoke manifest and smoke request are unchanged.

Launch: committed and pushed as 069d26b before transfer. All seven staged files match their committed SHA256s. The guarded driver preflight reported two runnable inputs, zero stale/bad inputs, and NP128/NCONC1. Array 20470747 was submitted held at 09:20:04 UTC and released at 09:21:12 UTC after exact checks: tasks 1-2, throttle 1, four-hour TimeLimit, 128 CPUs/tasks, 1 CPU/task, shared partition, 237G memory, billing 128, Requeue=0, expected node exclusions. The remote manifest and .lines are read-only (0444) during execution. Receipts are in results/hea_pilot_2026-09-07/.

Initial scheduler inspection at 09:21:38 UTC: both tasks PENDING for Priority; no QE output exists yet. Execution, SCF/projection validation, measured memory/cost and the paired endpoint readout remain pending. This completes preparation and submission, not the scientific evaluation.

Final launch checkpoint at 09:23:11 UTC: both tasks still PENDING/Priority, with no QE outputs. All 149 protected scientific files still match. The current launch status and census checkpoint are in results/hea_pilot_2026-09-07/launch_status.json.

Census checkpoint at 09:23:49 UTC: three completed, four running, 96 queued. The newly completed Ni34Fe6Cu29Co31 record is retained in its existing result path with the SHA256 in launch_status.json; no ranking or DFT interpretation is attached to this checkpoint.

## Completion checked 2026-09-07 at 18:49 UTC

Both jobs completed with exit code 0: builder ran 11:11:19–12:26:45 UTC (4526 s, 87 SCF iterations), pull2.10 ran 12:27:21–13:28:19 UTC (3658 s, 53 iterations). Total allocation use is 290.9867 core-hours, including projection, against 332.9357 planned for SCF alone and the 1024 requested bound. Current CPU allocation balance is 58,853.7 SU; the Anvil queue is empty.

The approved input hashes match, runtime inputs differ only in declared scratch/pseudopotential paths, and all six UPF checksums printed by QE match. Both outputs pass the existing fixed-geometry SCF/force audit. Both projections contain a complete 75-atom Lowdin table and JOB DONE; runner logs confirm successful density retention. Full output files and runtime inputs are retained at their actual job paths with transfer hashes.

The maximum free-coordinate force is 1.44459 eV/A for builder and 1.41502 eV/A for pull2.10, above the diagnostic 0.05 eV/A stationarity threshold. These are valid SCFs at fixed MLIP coordinates, not DFT minima. DFT relaxation remains necessary before a relaxed-geometry claim. The fixed-geometry atomic-projector E(pull2.10)-E(builder) is -2.053398 eV; this alone does not establish a reaction pathway, magnetic ground state, or candidate ranking. The fragment Lowdin moments are 1.0430 muB for HO2 and 1.9838 muB for O2, with the transferred H kept separate.

Evidence: results/hea_pilot_2026-09-07/completion_readout.json and completion_transfer.json. No further jobs or retries were submitted during this status check.
