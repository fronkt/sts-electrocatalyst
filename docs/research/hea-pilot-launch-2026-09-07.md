# Approved HEA DFT pilot — 2026-09-07

The user approved the prepared two-job atomic-projector leader endpoint pilot. Exact scope and input hashes are in results/hea_pilot_2026-09-07/approval.json. The separate approved manifest keeps the original prepared bundles reproducible. Only the two retained seed-0 endpoint configurations run; this does not validate the historical seed-1 winning chain.

Anvil preflight: che260157 CPU balance 59,144.7 SU; queue empty at the recorded check. Six UPFs match the prepared hashes, QE is 7.5 h19104ac_2, the existing queue driver matches local bytes, and the parity marker is present. No existing original or companion attempt was found. Anvil is an established staged run tree without a Git checkout, so exact committed files are transferred after the local push, with byte verification before execution.

The dedicated pilot runner keeps the established NP128/nk8 launch shape and inline projection. It adds a four-hour scheduler limit, stricter completion checks, refusal of prior scratch/output, and preservation of wavefunctions when SCF, projection or density retention fails. The dedicated submitter preserves the original parity, licensing, exclusion and driver-preflight guards. It submits exactly two tasks, concurrency one, initially held; accepted Slurm settings are checked before release. Original runners and scientific decks are unchanged.

Four hours includes SCF, projection and cleanup. The 332.936 core-hour planning figure models only SCF; the 1024 requested core-hour bound covers two four-hour jobs at128 cores, excluding retries and site-specific billing changes. There are no automatic retries or expansion. The earlier 3x wall/126-iteration monitoring suggestions are diagnostic review triggers, not a running watchdog; Slurm enforces the four-hour bound.

Readout requirements: independently check SCF convergence, finite final energy and force tables, matching runtime input and UPF hashes, completed projection with local moments, and scheduler accounting. A Slurm COMPLETED status alone is insufficient. Report paired E(pull2.10)-E(builder) only after both acceptable SCFs; magnetic ground state, pathway free energies, relaxed ranking and catalytic performance remain unresolved.

Scheduler hold/release behavior: https://slurm.schedmd.com/sbatch.html and https://slurm.schedmd.com/scontrol.html.

Verification before staging: both Bash syntax checks passed; 28 runner mock tests and 16 submitter mock tests passed on Windows/Git Bash, plus 50 existing controls/force tests and the exact frozen controls-bundle check. Independent review found no substantive errors. All149 protected scientific files matched their starting hashes. The original46/47 launch scripts, driver, prepared smoke manifest and smoke request are unchanged.
