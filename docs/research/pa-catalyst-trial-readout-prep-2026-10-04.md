# Catalyst P-A boundary trial: readout preparation, 2026-10-04

Status: Slurm job 21034683 was PENDING (reason Priority) at the last watcher read,
2026-10-04T10:18Z (`results/pa_catalyst_trial_2026-10-03/trial_watch_status.json` is the live
source). No trial result exists and none is claimed. This note covers the post-run readout
tooling and the two branches of the next decision. No pinned file is touched, nothing is
submitted, no Anvil access was used, and the branch proposals in sections 7 and 8 are
**UNADOPTED**: they are for Frank to approve, edit or reject.

Citation abbreviations used below (path:line, quoted verbatim in the tool output):
DOC = `docs/research/pa-catalyst-trial-2026-10-03.md`; REV = `results/pa_catalyst_trial_2026-10-03/independent_launch_review_final.md`;
REV1 = `independent_launch_review.md` (same directory); IMPL = `implementation_findings.md`; SBR = `source_boundary_review.md`;
SPEC = `launch_spec.json`; CTRL = `src/dft/pa_catalyst_trial.py`; ADP = `src/dft/pa_qe_adapter.py`;
ELIG = `docs/research/eligible-comparison-pa-readiness-2026-10-03.md`.

Scope reminder, from the approval itself: one job, whole 128-core node, 16 h / 2,048 CPU SU,
at most six sequential QE calls of at most 2 h, no retry, requeue, array or chaining; it does
not approve production relaxation, every-step P-A, S8 ranking or melt selection
(`docs/research/pa-catalyst-trial-2026-10-03.md:8-11`).

## 1. Inventory: what existed, what was missing

| Capability | Existing artifact | Gap |
|---|---|---|
| In-job verdict state machine; `trial_receipt.json`, per-arm `process_receipt.json` / `setup_receipt.json` / `parsed_receipt.json`, `allocation_before_call_NN.json`, `pre_resume_decision.json`, `reseed_lower_state_binding.json` | `src/dft/pa_catalyst_trial.py` (frozen, hash-pinned) | none; it emits only `PASS_ONE_BOUNDARY`, `HOLD`, `RESEED_BRANCH_ONLY`, `INCONCLUSIVE` (lines 934, 951, 970, 983) and never `FAIL` |
| Raw QE 7.5 parsing, trajectory comparison, fresh-vs-warm branch, consumption audit, BFGS reader | `src/dft/pa_qe_adapter.py` (frozen) | none; reused, not duplicated |
| Live read-only scheduler/arm watch | `results/pa_catalyst_trial_2026-10-03/watch_trial_readonly.py`, `trial_watch_status.json`, `trial_observations.jsonl` | records state and a 1.6 kB log tail only; no verdict, no SU |
| Pre-run staging, release, held validation | `pa-catalyst-remote-stage-…py`, `pa-catalyst-release-…py`, `pa-catalyst-held-validation-…py`, `publish_launch_handoff.py` | pre-run only |
| Offline regression, scientific verifiers, 9816 + 21 byte-pin check | `results/pa_catalyst_trial_2026-10-03/verify_trial_offline.py`, `baseline.json` | writes its receipt and verifier output into the pinned phase directory under a fixed label set (`initial`, `checked`, `release`; the first two are used), so a fresh run adds files there |
| Real-output replay | `replay_retained_raw.py` (tiny candidate only) | one arm, no table |
| Tiny-run readout | `results/s2_2026-09-25/full_text/sequential_2026-10-03/pa_tiny_raw_readout.py` | H2-specific asserts and paths; layout differs from the catalyst trial |
| Hash-pinned mirror | only the receipt format `pa_tiny_mirror_receipt.json` (path, size, sha256 per file, 66 rows); the transfer was ad hoc | no retained inventory/mirroring routine |
| Charged SU | tiny run kept `jobsu` text in `pa_tiny_final_accounting.json` | no parser, no cap check, no cross-check against sacct |
| PASS / FAIL / INCONCLUSIVE with citations; per-call table; readout writer | none | `readout_trial.py` below |

New files under `results/pa_catalyst_trial_readout_prep_2026-10-04/`:

- `readout_trial.py`: the read-only readout (verdict JSON, markdown table, criteria with file:line citations).
- `remote_inventory_snippet.py`: stdlib read-only remote inventory for the hash-pinned mirror (never run against Anvil from here).
- `run_regression.py`: re-runs the existing suites, both scientific verifiers and the byte-pin check while writing only inside this directory.
- `tiny_replay.py` and `tiny_replay_output/`: the same raw layers replayed over the retained real tiny run.
- `test_readout_trial.py`: tests of the above.

## 2. The readout tool

`python results/pa_catalyst_trial_readout_prep_2026-10-04/readout_trial.py --mirror DIR --sacct FILE [--scontrol FILE] [--jobsu FILE] [--remote-inventory FILE] [--balance-before SU] [--out NEWDIR]`

It reads a local mirror and saved scheduler text only; it opens no network connection, calls
no Slurm command, runs no QE, writes nothing into the mirror or repository, and `--out`
refuses to overwrite. Layers:

1. Scheduler: `sacct -P` text in the watcher's column set (header form also accepted, extra columns such as MaxRSS ignored or kept). Terminal-state set is the watcher's (`watch_trial_readonly.py:11-12`, drift-tested). Charged SU is `ElapsedRaw x billing / 3600`; `CPUTimeRAW / 3600` and the `jobsu` figure are shown beside it. Allocation shape, memory, GPU TRES, elapsed against 57,600 s and charged SU against 2,048 are checked against the pinned `launch_spec.json`.
2. Controller receipts: per-call state, stop reason, return code, wall time, per-call cap flag, supervisor flags, SCF counters, optimizer counts, XML exit status, energies; allocation receipts re-validated through the frozen `validate_allocation` with the 7,200 s + 120 s reservation shown.
3. Raw layer, independent of the receipts: tolerant summaries of each arm's `stdout.log` and `data-file-schema.xml` (SCF convergence, `!` energies, wall, SCF-cycle and BFGS counters, startup `.bfgs` deletion, user stop, failure markers, iteration 127) and the MPI/thread/pool/ELPA header bound through the adapter's own `_raw_parallel`. By default each arm is also re-parsed with the frozen `read_qe_arm`, the continuity comparison re-run with `compare_trajectories`, the fresh-minus-warm drop recomputed with the adapter's strict-inequality expression, and the reseed binding re-run with the controller's `validate_reseed_binding`. `--no-rederive` leaves a verdict marked `RECEIPT_ONLY`.
4. Mirror integrity: every mirrored file is hashed; an optional remote inventory is compared (rows the remote side did not hash are size-checked and reported separately, never as hash matches); `--print-mirror-selection` lists the lightweight remote paths the readout needs (no wavefunctions, no charge densities).

Outcome labels: `PASS`, `INCONCLUSIVE`, `RESEED_BRANCH_ONLY`, `UNMAPPED`, `NOT_READY` (no terminal sacct), `EVIDENCE_GAP` (required files missing). `FAIL` is never assigned automatically, because the registered criteria never define it (section 4, OQ1); where it is a plausible reading it appears under `candidate_labels` of an `UNMAPPED` outcome.

### Outcome mapping (every row quotes the registered text; the JSON and markdown repeat each quote with file:line)

| Observed | Label | Basis |
|---|---|---|
| Controller `PASS_ONE_BOUNDARY` and every gate corroborated: all calls validated, registered sequence control, candidate, fresh, resumed, negative; resource caps; per-call allocation receipts; boundary counts 1/3/2 and cycle sequences; 1e-6 Ry first threshold; continuity within tolerance on three ordered evaluations; negative control startup deletion with count 0; production flags false; no integrity flag | `PASS` | DOC:46-47 "1e-6Ry energy,1e-5bohr"; DOC:59, REV:67-68; DOC:40; `pa_catalyst_trial.py:970` |
| Controller `PASS_ONE_BOUNDARY` but any gate not corroborated | `UNMAPPED` (candidates PASS, INCONCLUSIVE) | gate named in the reasons |
| A call that timed out, stalled at SCF iteration 127, hit a failure marker or solver limit, was never finished (job killed), or exceeded 7,200 s | `INCONCLUSIVE` (prestated) | REV:134 "A solver limit, HEA4", REV:136, SBR:298 |
| Early natural convergence, nstep exhaustion, missed or skipped boundary | `INCONCLUSIVE` (prestated) | DOC:61 "Early convergence, nstep exhaustion", REV:70, SBR:39 |
| Fresh reference stalled or failed (controller `HOLD`) | `INCONCLUSIVE` (prestated, via the process rule); detail HOLD | DOC:39 "fresh reference holds continuation" plus REV:134 |
| Reseed attempted but first evaluated energy not bound to the lower fresh state or not strictly >10 meV below warm | `INCONCLUSIVE` (prestated) | IMPL:24-25, REV1:36-37, DOC:41-43 |
| Aggregate 16 h reached; allocation refused (resource problem) | `INCONCLUSIVE` (prestated) | REV:134-136, `pa_catalyst_trial.py:981` |
| Raw-validation refusal (UPF, settings, shape, XML) before any usable result; refusal before the first call; Slurm log refusal with no receipt | `INCONCLUSIVE` (controller record only) | DOC:82-83 says "reject"; label from `pa_catalyst_trial.py:876`, `:1023` (OQ8) |
| Controller `RESEED_BRANCH_ONLY` | `RESEED_BRANCH_ONLY` | DOC:36-37, DOC:49-50 (OQ4) |
| All calls validated, continuity not within tolerance | `UNMAPPED` (candidates FAIL, INCONCLUSIVE) | DOC:46-48, DOC:106, `pa_catalyst_trial.py:964,983` (OQ1) |
| Resumed call valid but saved optimizer state not consumed | `UNMAPPED` (candidates FAIL, INCONCLUSIVE) | `pa_qe_adapter.py:1246` (OQ2) |
| Controller `HOLD` without a call-level failure | `UNMAPPED` (candidate INCONCLUSIVE) | DOC:39 (OQ3) |
| Failed negative control after valid continuity | `INCONCLUSIVE`, question OQ5 raised | SPEC:55 vs `pa_catalyst_trial.py:965-970` |

Slurm status is reported separately and never changes the scientific label (DOC:105). By the
frozen exit mapping (`pa_catalyst_trial.py:1021`), a non-PASS result exits 3 and Slurm shows
FAILED 3:0, a refusal exits 2, and only a PASS shows COMPLETED 0:0.

## 3. Procedure when 21034683 reaches a terminal state

All commands below are read-only and are for the session that holds the SSH route (the watcher's
`ssh.exe`, key and remote Python 3.9 path apply). They have not been run.

0. Interim check while the job is RUNNING (the handoff's "actual allocation and raw headers" step): the same command with a partial mirror and a RUNNING `sacct` row prints `NOT_READY` plus the live per-call table, the re-validated `allocation_before_call_NN.json` receipts and the raw MPI128 / 1 thread / 8 pool / ELPA 4x4 header binding per started call. The controller's receipt status is a placeholder until it finishes and is labelled as such.
1. Wait for the watcher's terminal state or an accounting row; a pending-accounting row is not terminal.
2. Scheduler text (run without `-n` to keep the header so extra columns parse):
   `sacct -P -j 21034683 --format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,ReqMem,AllocTRES,CPUTimeRAW,MaxRSS,Start,End`; `scontrol show job 21034683 -o` while it is still visible; `jobsu` as for the tiny job (confirm its flag with `jobsu -h`); the balance table. Save each as a local text file.
3. Remote inventory: `python3 - /anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03 --include trial_results --include trial_21034683.log < remote_inventory_snippet.py > remote_inventory.json` (files above 50 MB are listed by size without a login-node hash).
4. Mirror the paths from `readout_trial.py --print-mirror-selection` into a local directory that preserves the relative layout (`trial_results/...`, `trial_21034683.log`). Binary checkpoints stay on Anvil, as for the tiny run.
5. `readout_trial.py --mirror <dir> --sacct … --jobsu … --remote-inventory remote_inventory.json --balance-before 36878.2 --out results/pa_catalyst_trial_readout_<date>/`.
6. `run_regression.py <new label>` to re-prove the 9816 + 21 pins, both verifiers and the suites after the readout files land.
7. Frank reads the headline, the open questions it names and the SU block, and chooses the branch in section 7 or 8. No rerun, no production or melt release follows automatically (DOC:107).

## 4. Where the registered criteria are silent or ambiguous (surfaced, not decided)

- **OQ1 / OQ2, the missing FAIL.** DOC:106 asks for "a source-bound numerical pass, failure or inconclusive result", but the document defines only the tolerances (DOC:46-48) and the inconclusive causes (DOC:61, REV:134). The frozen controller records any tolerance miss or audit failure as `INCONCLUSIVE` (`pa_catalyst_trial.py:964,960,983`) and never emits a failure status. A clean tolerance miss, or valid calls whose resume did not consume the saved optimizer state, is therefore `UNMAPPED` with candidates FAIL / INCONCLUSIVE.
- **OQ3.** A HOLD that is not caused by a failed call (for example an unchanged-checkpoint check) has no stated label (DOC:39 says only that continuation is held).
- **OQ4.** Whether `RESEED_BRANCH_ONLY` counts as a trial pass. DOC:36-37 says to report it separately; DOC:49-50 forbids splicing it into a continuity pass.
- **OQ5.** The negative control is `optional_negative_control: true` in the spec (SPEC:55), yet the frozen controller runs it before assigning PASS (`pa_catalyst_trial.py:965-970`), so a failed control demotes an otherwise valid continuity pass. The doc does not say whether that is intended.
- **OQ6.** Which SU is of record: `ElapsedRaw x billing / 3600`, `CPUTimeRAW`, or `jobsu`. On the tiny job the exact product is 0.13778 and `jobsu` printed 0.1376 (rounded hours); the readout shows all three and picks none.
- **OQ7.** Whether a controller-ordered Slurm FAILED 3:0 counts as a scheduler-side failure. DOC:105 only requires the two outcomes to be retained separately; the tiny job's FAILED 2:0 coexisted with a scientific pass (`pa-tiny-restart-readout-2026-10-03.md:58-62`).
- **OQ8.** Raw-validation refusals are recorded INCONCLUSIVE by the controller, while DOC:82-83 uses "reject" without a label.
- Interpretive notes, not criteria: a PASS validates continuity at one boundary only; unless the fresh state lands strictly more than 10 meV lower, the real reseed branch stays unvalidated (DOC:49-50, SBR:287). A fresh state that lands higher never triggers a reseed (DOC:38), yet the September arm saw fresh checks 11.9 and 25.5 meV above the trajectory (`lowtail-stall-robust-arms-readout-2026-09-25.md:58-60`); the readout always prints the signed warm-minus-fresh figure so that gap is visible. QE tightens `conv_thr` after the first ionic step (the retained log prints 1.0E-06, then 8.34E-08), so the 1e-6 Ry threshold is checked for control, candidate, fresh, reseed and negative only, as the controller does (`pa_catalyst_trial.py:857`), not for the resumed call.

## 5. Sanity envelope for the trial's own charge (retained evidence, not a prediction or licence)

From the matched September low-state warm relaxation, cumulative cycle ends of the first
three evaluations are 480.0, 1,121.6 and 2,498.7 s, and one fresh SCF at a tighter target
took 3,485 s (`source_boundary_review.md:289-295`). Control 2,498.7 s, candidate 480.0 s, fresh up
to 3,485 s, resumed two evaluations 2,018.7 s, negative control 2,498.7 s sum to 10,981 s,
about 390 SU at 128 ranks, before per-call startup, 120 s cleanup allowances and checkpoint
copies. The cap is 2,048 SU (SPEC:48) and "the maximum cost is a cap, not a runtime
prediction" (`eligible-comparison-pa-readiness-2026-10-03.md:120`). A charge far above this
envelope is worth explaining before the branch decision.

## 6. Measured costs banked in the repository (used only in sections 7 and 8)

Cu8Cr23Mn35Co34 seed20/site2 clean slab, 72 atoms, 128 ranks, Arm A job 20862968; wall seconds
are the `PWSCF ... WALL` line of the 85 mirrored segment and fresh-check outputs under
`results/lowtail_low_state_restart_2026-09-22/checked2/outputs/Cu8Cr23Mn35Co34__s20_site2/segments/`;
SU = core-hours = seconds x 128 / 3,600 (`lowtail-generalization-sizing-2026-09-22.md:26`).

| Block | n | Mean s | Mean SU | Range s |
|---|---|---|---|---|
| warm one-step segment, steps 1-20 | 20 | 764.5 | 27.2 | 428.2 - 1,053.0 |
| fresh check at 8.08e-8 Ry, converged | 15 | 3,669.6 | 130.5 | 3,384.9 - 4,680 |
| fresh check, stopped at the 127-iteration ceiling (timed) | 5 of 6 | 6,228 | 221.4 | 6,000 - 6,420 |
| accepted step = warm + fresh (steps 1-20 with both timed) | 19 | 4,958.0 | 176.3 | n/a |

Six of the 21 fresh checks stalled (steps 10, 12, 16, 19, 20, 21; step 19 has no timing line);
the job's own elapsed was 115,537 s, about 4,108 SU (`lowtail-stall-robust-arms-readout-2026-09-25.md:24,77`).
The earlier plan priced a fresh SCF at 3,485 s (124 SU) and a warm step at 40-70 SU
(`lowtail-stall-robust-protocol-plan-2026-09-22.md:39`); the measured warm step is cheaper and
the measured fresh stall share is what the plan did not price. Other banked 128-rank costs:
fixed-geometry clean-slab SCF 128 SU (Cu8) and 80 SU (Ni31); clean-slab relaxation leg 538 SU to
failure; adsorbate relaxation legs 1,109 and 1,194 SU (`lowtail-generalization-sizing-2026-09-22.md:26`).

## 7. UNADOPTED: if the outcome is PASS (corroborated, continuity at one boundary)

Nothing here is submitted or licensed. What the documents say must come first:

1. Record the trial's actual SU, balance and outcome with this readout: **trial charged SU = ______ (fill from the readout), balance after = 36,878.2 minus that** (DOC:90, `pa-tiny-restart-readout-2026-10-03.md:11`).
2. "Acceptance can license a subsequent separately costed production relaxation; it cannot create a converged reference or electronic ground-state guarantee" (`eligible-comparison-pa-readiness-2026-10-03.md:171-172`). A PASS covers one boundary, not every-step checking, terminal fresh acceptance, or a validated reseed (DOC:49-51; ELIG:162).
3. An additive production P-A runner that interleaves the fresh check and reseed with the verified restart contract without overwriting optimizer history, scratch or proposal/energy correspondence (`pa-tiny-restart-readout-2026-10-03.md:73-75`), its branch/reseed state machine and checkpoint coverage tested independently (same file, line 76), and an independent regression review (`pa-offline-restart-probe-2026-10-03.md:154-156`).
4. A fresh A11.R3 count / cost / cap and boundary review before any slab rerun (`sequential-evidence-compute-readiness-2026-10-03.md:107-108`), as its own dated line with every count exact (`docs/43-prereg-week1-factorial.md:2113`; template at `:5042`).
5. A decision, already flagged by the documents as a review item, on what a failed fresh reference does in every-step mode: P-A-v2 HOLDs an unreferenced step (`eligible-comparison-pa-readiness-2026-10-03.md:71,84-87`), and 6 of 21 September fresh checks stalled.
6. Beyond this proposal: production references, matched adsorption and free-energy conventions, uncertainty-aware ranking, population freeze and melt stock constraints still precede any melt candidate (DOC:129-131; ELIG:173-175). S8 stays held.

Proposed next step (parameters carried over from the September plan, priced from section 6):
a P-A-v2 every-step checked relaxation of the same slab from the cycle-5 low state, one job on a whole
128-core node, a fresh-start SCF at 8.08e-8 Ry after each accepted step (DOC:26), re-seed on a drop of
strictly more than 10 meV, at most 40 accepted steps and at most 10 re-seeds, stopping at total force
below 0.002 Ry/bohr (`lowtail-stall-robust-protocol-plan-2026-09-22.md:32`).

| Accepted steps N | Planning SU, measured mix (N x 176.3) | Planning SU if every fresh check converges (N x 157.7) | Ceiling SU (N x 265.7: slowest warm 1,053 s + slowest stalled fresh 6,420 s) |
|---|---|---|---|
| 10 | 1,763 | 1,577 | 2,657 |
| 20 (plan basis) | 3,526 | 3,153 | 5,314 |
| 40 (plan cap; the ceiling also carries 10 re-seeds at 37.4 SU each, 374 SU) | 7,051 | 6,306 | 11,003 |

- Wall at 128 ranks: 3,526 SU is 27.5 h; 11,003 SU is 86.0 h. The September Arm A used a 72 h cap (9,216 SU); the wholenode wall limit has not been checked here and is not recorded in the repository.
- The September plan priced N = 20 at about 3,600 SU planning and N = 40 at about 8,500 SU ceiling (`lowtail-stall-robust-protocol-plan-2026-09-22.md:43`); the measured stall share is what raises the ceiling.
- Spend after the ceiling: 36,878.2 minus the trial's charged SU minus 11,003 (about 25,875 minus the trial's charge, if N = 40 is chosen).
- Replace the Arm A means with the trial's own per-call walls (fresh call at 1e-6 Ry, warm evaluations on a restart) once known; the table above is the pre-trial measured basis.
- This is a numerical protocol outcome, not a census result or adsorption reference; a converged trajectory would be a checked trajectory, not a ground-state claim (plan section 6).

## 8. UNADOPTED: if the outcome is FAIL, INCONCLUSIVE, HOLD, RESEED_BRANCH_ONLY or UNMAPPED

What the documents pre-state:

- No hidden rerun: the trial reports its result and actual SU "without a hidden rerun" (DOC:107); the approval is for exactly one job (DOC:8-9); early convergence, nstep exhaustion, a missed boundary, a solver limit, a stall or a resource problem is inconclusive and "teardown cannot justify exceeding authority or launching a replacement" (DOC:61, REV:134-136, SBR:298-299). Unused cap is not permission for another job (`pa-tiny-restart-readout-2026-10-03.md:80`).
- Production, every-step P-A, S8 and melt selection stay unlicensed (DOC:10, DOC:51, ELIG:162).
- The only pre-stated alternative path: if P-A does not work, P-C (a fresh-start SCF at every step under an external BFGS driver) is "the next arm", and it is "the fallback if P-A's warm SCFs stall too often" (`lowtail-stall-robust-protocol-plan-2026-09-22.md:35,24`). After the September arms the choice between P-C and repairing P-A's BFGS carry-over and rerunning was left to the entrant, and "any launch needs a new dated line" (`lowtail-stall-robust-arms-readout-2026-09-25.md:73,81`). This trial is that carry-over repair test, so a non-pass returns the same choice to Frank. The documents do not say which to take.

Cost basis for the options (priced from section 6; every launch needs its own dated A11.R3 line):

| Option | What it needs first | Cost basis |
|---|---|---|
| Corrected one-boundary re-test of the same restart protocol | a cause-specific correction with its source review (boundary or observer changes need `source_boundary_review.md`-grade review), a new dated line | cap no higher than the trial's own 2,048 SU; best price estimate is the trial's own charged SU: **______ (fill)** |
| P-C: one fresh-start SCF per step | an external BFGS driver (none exists: plan table "driver only", line 20), offline tests, independent review | per step 130.5 SU if the fresh SCF converges, 221.4 SU if it stalls; measured mix over 20 timed fresh checks 153.2 SU; N = 20 planning 3,064 SU; N = 40 ceiling at the slowest stalled check (228.3 SU) 9,131 SU. The 6-of-21 stall share would hit every step |
| Stop protocol work and keep the evidence | none | zero further SU; S8 hold unchanged |

By outcome: `INCONCLUSIVE` from a call-level cause names that cause in the readout and returns to the
table above; `RESEED_BRANCH_ONLY` means the lower-state branch was numerically bound while continuity
stayed unvalidated (DOC:36-37,49-50), so the continuity half of the boundary question is open; `UNMAPPED`
needs Frank's label first (OQ1-OQ4).

## 9. Verification

Command: `python -B results/pa_catalyst_trial_readout_prep_2026-10-04/run_regression.py final3`
(receipt `regression_final3.json`, verifier output `scientific_final3/`), at HEAD b3b64ce on
`r0-catalysis-revival`, tracked worktree clean before and after, `git status` unchanged by the run.
It re-uses the byte-pin baseline and the suites of `verify_trial_offline.py` without writing into any
existing directory.

| Check | Result |
|---|---|
| Evidence unittest discovery (four directories, URL requests refused) | 83 tests, 0 failures, 0 errors |
| Compute suites (`pytest -q` over the eleven files listed in `verify_trial_offline.py`) | 491 passed, 3 skipped, 7 subtests passed (the three Windows filesystem skips) |
| Scientific verifiers (`verify_evidence_recovery.py` and `verify_si_round.py --require-audits`) | both pass; 42 registered recovery reads |
| Byte pins before / after | 9,816 tracked + 21 unrelated files, 0 errors both times |
| Frozen code pins (adapter, controller, tests, wrapper, spec, source review, replay, watcher, verifier) | unchanged |
| New readout tests (`test_readout_trial.py`) | 74 passed |

The 74 readout tests cover: all 71 citations of the 29 criteria resolving at their pinned line (and drift reporting);
the watcher's terminal-state set and `sacct` format; the registered call table against the controller
source; real tiny accounting (state FAILED 2:0, 124 s, 4 CPUs, 0.13778 SU against `jobsu` 0.1376);
the 66-file tiny mirror against its retained pins; raw summaries of the four real tiny arms against the
documented tiny facts (8/1/5/7 converged steps, status 255 on the stopped arm, startup `.bfgs` deletion
only on the negative control); the frozen adapter re-deriving the real tiny candidate and failing closed
on three adversarial settings; the real 72-atom, 128-rank September log (SCF cycles 1-6, BFGS counts 0-5,
iteration 127 kill, MPI128 / 8 pools / ELPA 4x4 header binding, mutated headers refused); and
catalyst-layout scenarios run through the real `Trial.run()` state machine with process doubles:
PASS, PASS withheld on each of nine independently corrupted gates, resource-cap breach, reseed validated,
upper-state reseed, HOLD with and without a call failure, continuity miss, unconsumed checkpoint, killed
call at the time limit, HEA4 stall, timeout, failure marker, solver limit, missed boundary, early
convergence, raw-validation refusal, failed negative control, aggregate cap, refused allocation,
non-terminal job, interim RUNNING readout, refusal before the first call, missing receipt, missing XML,
tampered XML energy, remote-inventory mismatch, read-only behaviour and `--out` overwrite refusal.
Mutating the tool (halved SU, constant failure class, relabelled continuity case, dropped resource or continuity gate)
makes the tests fail, including the strict-versus-non-strict 10 meV comparison tested at exactly 10 meV. The catalyst-arm adapter re-derivation has only been run on a real tiny arm and
synthetic files, not on real 72-atom XML, which does not exist until the job writes it; if it errors on
the first real mirror, `--no-rederive` still gives a `RECEIPT_ONLY` verdict and the error is named.

## 10. New files

All new; no existing file was modified or removed.

- `docs/research/pa-catalyst-trial-readout-prep-2026-10-04.md` (this note)
- `results/pa_catalyst_trial_readout_prep_2026-10-04/readout_trial.py`
- `results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py`
- `results/pa_catalyst_trial_readout_prep_2026-10-04/remote_inventory_snippet.py`
- `results/pa_catalyst_trial_readout_prep_2026-10-04/run_regression.py`
- `results/pa_catalyst_trial_readout_prep_2026-10-04/tiny_replay.py` and `tiny_replay_output/` (`tiny_replay_readout.json`, `tiny_replay_readout.md`)
- regression receipts and verifier output under the same directory
