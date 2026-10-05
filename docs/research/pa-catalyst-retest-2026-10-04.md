# Catalyst P-A one-boundary re-test: corrected package prepared, not submitted (2026-10-04)

Status: the correction, the real-output tests, the dated spec and the held-submit scripts are prepared locally. **Nothing was staged on
Anvil, nothing was submitted, no QE ran, no file on Anvil was created or changed, nothing was committed or pushed by this phase.** Frank
gives a separate go before anything touches Anvil. The first trial (job 21034683, INCONCLUSIVE, 102.86 CPU SU) is untouched and stays
the record of its own outcome; this package does not turn it into a pass.

Citation abbreviations: ADP = `src/dft/pa_qe_adapter.py` (first trial, pin `25546421...`); V2 = `src/dft/pa_qe_adapter_v2.py`;
CTRL = `src/dft/pa_catalyst_trial.py`; RT = `src/dft/pa_catalyst_retest.py`; PH = `results/pa_catalyst_retest_2026-10-04/`;
READOUT = `docs/research/pa-catalyst-trial-readout-2026-10-04.md`; QE = the cached official QE 7.5 source under
`results/pa_catalyst_trial_2026-10-03/qe_source/`.

## 1. Decision of record

Frank, in session, 2026-10-04, chose "Corrected re-test" over P-C or stopping. The approved plan, verbatim as presented to him:

> "Fix the parser (accept QE 7.5's tag layout, fix david/davidson). Replace the synthetic test files with real QE 7.5 Hubbard XML: this run's control output plus the 19 files in runs/a0/pproj6. Check the fresh-SCF parsing against real output first, at no SU cost. Then a new dated spec and review, then ONE job: same 16 h / 2,048 SU cap, no retries, expected ~430-540 SU. I come back for your go before submitting."

How each clause stands:

| Clause | State |
|---|---|
| Fix the parser: QE 7.5 tag layout | done in V2 (section 5) |
| Fix david/davidson | done in V2: `QE75_XML_CANONICAL`, rules quoted from the QE source (section 5) |
| Replace synthetic test files with real QE 7.5 Hubbard XML: control output plus the 19 pproj6 files | done as additional real-file suites in `tests/test_pa_qe_adapter_v2_real.py` on fixtures copied from those files; the old synthetic fixture is corrected and proven to contain only elements real QE writes (section 6) |
| Check fresh-SCF parsing against real output first, at no SU | done for everything a real file exists for; the remaining gap is stated in section 10 |
| New dated spec and review | spec written, `PH/launch_spec.json`; review of the source facts `PH/source_xml_input_review.md`; the independent review is a step still to come (section 11) |
| ONE job, same cap, no retries, ~430-540 SU | specified, not submitted; envelope in section 9 |
| Frank's go before submitting | no submission, no staging; the scripts refuse to run without the receipts that follow his go |

## 2. Root cause (from READOUT section 2, re-checked)

ADP:626 `value(dftu, "lda_plus_u", True)` requires an XML element that QE 7.5 never writes. QE writes `<dftU new_format="true">` with children
`lda_plus_u_kind`, `Hubbard_U`, `U_projection_type` (`Modules/qexsd_init.f90:510`, `Modules/qes_init_module.f90` `qes_init_dftU`); its own reader
takes the flag from the presence of the block (`Modules/qexsd_copy.f90:403`). The synthetic fixture of the first trial's tests invented the element.
Re-checked against a byte-identical copy of the first adapter (`dryrun/scratch/pa_qe_adapter_FROZEN_COPY.py`, sha `25546421...`): on the real control
XML `_check_xml_input` refuses with `one XML lda_plus_u required`, reproducing the job's error at zero SU.

## 3. How frozen code was handled

Project convention, from earlier phases: a corrected runner is a **sibling file kept as its own pinned file**, "so that the batches pinned to the original
runner keep their bytes" (docstrings of `research_batch_seeded.py`, `research_batch_checked.py`; `pa_checked_contract.py`), with its own tests, and every
phase adds a new dated directory with its own pins. The historical byte pins (9,816 tracked + 21 unrelated files, `results/pa_catalyst_trial_2026-10-03/baseline.json`)
do not list ADP or CTRL, but the first spec pins ADP and CTRL by hash, the first review and the readout cite lines inside them, and
`results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py` asserts text at `ADP.splitlines()[844]`.

Done here, additively: `src/dft/pa_qe_adapter_v2.py` and `src/dft/pa_catalyst_retest.py` are new siblings (diffs against the frozen files in
`PH/adapter_v2_vs_frozen.diff`, `PH/controller_retest_vs_frozen.diff`); `src/dft/pa_checked_contract.py` is unchanged and re-pinned. The frozen controller cannot run
a second job in any case: it hard-codes the schema, the date `2026-10-03` and the parent directory name and refuses an existing output root.
No existing file was modified, moved or deleted by this phase.

**Finding to resolve before publication.** While this phase was being prepared, another session in the same worktree repaired the first adapter **in place**
and pushed it: commits `9639eaa` ("Repair QE7.5 Hubbard XML validation ...") and `dbdbca9`, origin `r0-catalysis-revival` now at `bf07807`; phase
`results/pa_xml_repair_2026-10-04/`, note `docs/research/pa-xml-repair-2026-10-04.md`. Their change makes `lda_plus_u` optional-if-present, requires `new_format="true"`
and refuses `Hubbard_Um/V/back`; it edits ADP (13 lines), `tests/test_pa_qe_adapter.py` (2 lines) and adds `tests/test_pa_qe_schema_repair.py`. Consequences:

* ADP in the worktree is now `5e77b8b3...`, no longer the launch pin `25546421...`. The original survives byte-identical in `results/pa_xml_repair_2026-10-04/launch_adapter_original.py`
  and in `dryrun/scratch/pa_qe_adapter_FROZEN_COPY.py`; the first trial's spec, review and readout now refer to bytes that are only in history and in those copies.
* One of the 74 readout-tool tests fails in the live tree: `test_registered_call_table_matches_controller_source` (`ADP.splitlines()[844]` moved by the six added lines). The other session
  deselects it and its citation sibling and checks both against the original snapshot; this phase does the same (section 7).
* The in-place repair does not fix david/davidson, disk_io, verbosity or input_dft, does not bind the operational fields, and is not wired to a controller that can
  take a new spec. V2 is a superset on the validator side and independent of it. V2 differs in one choice: it refuses any `<lda_plus_u>` child outright (QE 7.5 never writes it) where the in-place
  repair accepts one that is unique and true. Both accept every real file.
* Recommendation: pin V2 and RT in the new spec (done), leave the in-place edit as it is, and do not use ADP for anything else in this trial. If Frank prefers a single lineage, the decision
  is between (a) keeping both, (b) retiring the in-place edit by a revert commit, which restores the historical pins and the 74/74 readout tests; it is his call and nothing here depends on it,
  except that `publish_reviewed_package.py` refuses to run while any tracked file is modified in the worktree.

## 4. Real-output audit (zero SU)

Full tables: `PH/audit_table.md` (the readable view of `PH/audit_real_outputs.json`; script `PH/audit_real_outputs.py`). Corpora, all QE 7.5: **CONTROL** the control call of job 21034683
(deck, stdout, stderr, XML, `.bfgs`); **SCF19** the 19 `calculation='scf'` Hubbard XML with deck and log in `runs/a0/pproj6`; **FRESH21** 21 September 72-atom 128-rank fresh SCF
logs (15 converged, 6 stopped at SCF iteration 127); **SEG21** 21 September one-step from-scratch relax logs; **TINY** the four retained one-process H2 arms (clean stop, continuous, resumed with
`restart_mode='restart'`, from-scratch negative control). Which of the 19 pproj6 files are scf and which carry forces: all 19 are `calculation='scf'`, exit status 0, converged, and all 19 carry
`<output><forces>` (the decks set `tprnfor`).

| Arm type | Real file(s) for the parse path | Required tag, attribute or literal | Result |
|---|---|---|---|
| control, candidate, negative, reseed (relax, clean stop) | CONTROL (full chain); TINY clean stop | all 54 distinct `_one(parent, tag)` lookups of `read_qe_arm`; every one found exactly once; the 3 `<step>` records and `<output>` proposal; exit status 255 | PASS |
| same | CONTROL | `dftU` layout: one `dftU`, `new_format="true"`, children `lda_plus_u_kind`/`Hubbard_U`/`U_projection_type`, U 3.32/3.70/3.90 eV | **MISMATCH in ADP** (requires `lda_plus_u`, never written); PASS in V2 |
| same | CONTROL | log: banner `7.5`, `JOB DONE.`, 5 UPF reads + MD5, 3 energies, 3 force blocks, 3 proposal blocks, SCF-cycle/BFGS counters, header `128 / 1 thread / 8 pools / ELPA 4*4`, threshold `1.0E-06` | PASS (READOUT section 5 chain re-run end to end through V2) |
| same | CONTROL `.bfgs` | `read_bfgs`: dimension 226, counters 3/3/0, zero inactive tails | PASS |
| fresh (`calculation='scf'`, `normal_scf`) | SCF19 XML + deck + log; FRESH21 logs | `output/convergence_info/scf_conv`, `output/total_energy/etot`, `output/forces` (dims 3 x nat), `output/atomic_structure`, exit status 0, no `<step>`; all 53 lookups found once on all 19 | PASS; 19 of 19 accepted end to end by `read_qe_arm(expected_exit='normal_scf')`, 4 with real UPF reads and MD5 (Cr, Mn slab and O), 15 with the UPF read stubbed (UPF files not on hand), the runtime-header check stubbed because those runs used 128 ranks, 4 pools, serial diagonalization |
| fresh | FRESH21 (72 atoms, 128 ranks) | header lines `npool 8`, `proc/nbgrp/npool/nimage 16`, `ELPA 4*4`, banner, no failure marker (only `IEEE_UNDERFLOW_FLAG IEEE_DENORMAL` notes), one energy, one force block, no ionic counters | PASS |
| fresh | SCF19 / SEG21 / FRESH21 | controller regexes: `FAILURE` hits 0 of 65 logs; `TIME_FAILURE` hits only in SEG21 (20 of 21: QE's `maximum number of steps` at `nstep=1`, not a registered arm); `HEA4` iteration-127 rule fires on exactly the 6 stalled FRESH21 logs | PASS |
| resumed (`restart_mode='restart'`) | TINY resumed (serial) | XML identity equal to the clean-stop, continuous and scratch arms; counters start at the saved count + 1; `restart_mode` XML `restart` | PASS for H2; **no real 72-atom restart file exists** |
| negative (from scratch on a copied checkpoint) | TINY negative; SEG21 | `.bfgs deleted, as requested` at startup, optimizer count 0 | PASS for H2 and as a log literal in SEG21; no catalyst-scale arm file |
| reseed | none | same parse path as the control | no real file |

Deck strings that QE rewrites (canonicalization map from the cached QE source, `QE75_XML_CANONICAL`; quoted lines in `PH/audit_table.md` section 3 and `PH/source_xml_input_review.md` section 2):

| Deck string | XML string | QE source | ADP | V2 |
|---|---|---|---|---|
| `diagonalization = 'david'` (QE default) | `davidson` | `PW/src/pw_init_qexsd_input.f90:477-481` | would refuse (latent; the registered deck sets none) | accepts |
| `disk_io = 'default'` (QE default) | `low` | `Modules/qexsd_input.f90:85-89` | would refuse (latent) | accepts |
| `verbosity = 'default'` | `low` | `Modules/qexsd_input.f90:80-84` | not compared | accepts |
| `input_dft = 'pbe'` | `PBE` | `PW/src/pw_init_qexsd_input.f90:203-211` | would refuse (latent) | accepts |
| smearing aliases (`cold`, `m-v`, ...) | `mv`, `mp`, `gaussian`, `fd` | `PW/src/set_occupations.f90:135-157` | handled | handled, now verified against the source text |
| `mixing_mode`, `ion_dynamics`, `occupations`, `calculation`, `restart_mode`, `prefix`, `U_projection_type` | verbatim | see review | literal | literal, with a rule entry |

("Would refuse" is measured: the first adapter with only the dry-run's one-line `lda_plus_u` patch, on the real control XML with the one extra explicit assignment; `PH/audit_table.md` section 3.)

Everything else the audit found: `nstep` is the internal value (1 for scf, 30 for the relax arms) and is correctly excluded from the cross-arm identity; the four real H2 arms
(clean stop, continuous, resumed, scratch) share one XML identity; the real relax control and a real scf file differ in `<input>` only in the six declared operational fields and in fields set by their different decks.
The 19 pproj6 decks use the `ortho-atomic` projector, outside the registered `atomic` scope: ADP and V2 both refuse them by design, and the tests widen `HUBBARD_PROJECTORS` inside the test only.

## 5. Fixes in V2

1. DFT+U: exactly one `dftU`, `new_format="true"`, children limited to `lda_plus_u_kind`, `Hubbard_U`, `U_projection_type` (any other child, `lda_plus_u` included, fails closed), `lda_plus_u_kind == 0`,
   `U_projection_type == atomic`, species/shell/eV values equal to the deck within 1e-10 eV.
2. Canonicalization: every deck-string comparison goes through `QE75_XML_CANONICAL`; a compared key without a rule raises; `expected_xml_strings(deck)` lists them and runs in PREFLIGHT, so a missing rule fails at zero SU.
3. Operational binds: `calculation`, `restart_mode`, `prefix`, `max_seconds` of each arm's XML are compared with that arm's own deck (they are excluded from the cross-arm identity, so nothing tied them to the deck before). `verbosity` is compared with its rule.
4. `HUBBARD_PROJECTORS = ("atomic",)` as a module constant, so tests can read real `ortho-atomic` files through the production parser without widening the production scope.
5. Controller RT, besides the registered identity (schema `pa-catalyst-retest-v1`, date `2026-10-04`, parent `sts_pa_catalyst_retest_2026-10-04`, dependency names, V2 import): **PREFLIGHT replays the real control call** of job 21034683 through the staged adapter
   (fixture files pinned in the spec, decompressed into a scratch directory under the new parent, read with `read_qe_arm(clean_stop, 3 evaluations)` and `read_bfgs`; required result: scf counters `[1, 2, 3]`, saved optimizer `3/3/0`, XML identity `3bd17094...32f0`;
   the scratch directory is removed). The stage and release scripts and the job's own first step run it, so a validator/schema mismatch with real output, or a Python-3.9 incompatibility on Anvil, fails at zero SU. Replaying the first adapter through the same gate
   reproduces `one XML lda_plus_u required` (tested).

## 6. Tests

| Suite | File | Content | Result |
|---|---|---|---|
| Real-output regression | `tests/test_pa_qe_adapter_v2_real.py` | control call end to end, its `.bfgs`, Hubbard layout, canonical variants against the real XML, 19 scf pairs (input, output node, end to end), 4 pairs with real UPF reads, real 72-atom fresh logs, real H2 restart arms, QE-source quotes and alias table, 12 in-test mutants | 100 passed |
| Ported synthetic | `tests/test_pa_qe_adapter_v2.py` | the first trial's adapter tests with the corrected Hubbard fixture, plus: an invented `lda_plus_u` is refused, `david` is compared as `davidson`, and `test_synthetic_fixtures_use_only_elements_real_qe_writes` (every element and attribute of every synthetic XML occurs in the real vocabulary of 24 real XML files (control, four H2 arms, 19 scf)) | 75 passed, 2 skipped (Windows symlink and FIFO fixtures) |
| Controller | `tests/test_pa_catalyst_retest.py` | the first trial's supervisor tests re-bound to RT, identity refusal of the frozen schema/date/parent, PREFLIGHT replay accept/refuse (drifted fixture, wrong UPF pins, frozen adapter), real-log regexes of the supervisor | 99 passed |
| Scripts | `tests/test_pa_catalyst_retest_scripts.py` | each remote program compiles; only its step's commands; once-only guards; no reference to the first trial's checkout; spec resources equal the approved trial | 14 passed |

Fixtures: `tests/fixtures/qe75_real/` (92 deterministic gzip copies, 3.5 MB; manifest with original path, bytes and SHA-256; originals untouched; a test re-hashes every decompressed fixture and, when the original is present, the original too).
`runs/a0/pproj6/**/dens/` is git-ignored, so those 19 XML files were untracked until copied.

Mutation checks (`PH/run_mutation_checks.py`, `PH/mutation_checks.json`, scratch tree, 12 mutations of V2, each must fail a real-file test): **12 of 12 caught.**
Reintroducing the `lda_plus_u` requirement (the original defect) fails 53 real-file tests, the first being `test_real_control_call_is_accepted_end_to_end`. The other mutants: literal `david`, `disk_io`, `verbosity`, `input_dft` compares, unregistered Hubbard content accepted,
`new_format` not required, operational binds dropped, production scope widened to `ortho-atomic`, Hubbard U values not compared, projector not compared, `cold` alias removed.

## 7. Regression

`PH/verify_retest_offline.py initial` (receipt `PH/offline_initial.json`, scientific output `PH/scientific_initial/`), run on the worktree at HEAD `bf07807`, which includes the other session's in-place repair of ADP. Nothing was run on Anvil.

| Check | Result |
|---|---|
| Historical byte pins (first trial baseline), before and after the run | 9,816 tracked + 21 unrelated files, 0 errors both times |
| First-trial frozen artifacts: CTRL, `pa_checked_contract.py`, wrapper 89, first spec, first source review | unchanged (hash-checked); the retained launch adapter copy equals the pin `25546421...` |
| `src/dft/pa_qe_adapter.py` in the worktree | `5e77b8b3...`, **differs from the launch pin** (the other session's in-place repair; section 3) |
| Evidence unittest discovery | 83 tests, 0 failures, 0 errors |
| Compute suites of the first trial (11 files, as in READOUT section 10, current worktree) | 491 passed, 3 skipped, 7 subtests passed (same counts as before) |
| New re-test suites (4 files) | 288 passed, 2 skipped: `test_pa_qe_adapter_v2.py` 75 passed + 2 skipped (Windows symlink and FIFO fixtures, as in the first trial), `test_pa_qe_adapter_v2_real.py` 100, `test_pa_catalyst_retest.py` 99, `test_pa_catalyst_retest_scripts.py` 14 |
| Readout-tool tests | **73 passed, 1 failed** in the live tree: `test_registered_call_table_matches_controller_source`, whose literal `ADP.splitlines()[844]` moved with the other session's six added lines. Its logic and the citation test (71 citations) pass against the byte-identical launch adapter (`dryrun/scratch/pa_qe_adapter_FROZEN_COPY.py`, `25546421...`): all registered call-table lines, `PREFIX`, `5.1e-8` at line 845. On unmodified ADP the 74 tests are expected to pass; that full pytest run was not repeated on a reverted tree because no existing file was touched |
| Scientific verifiers | both pass; 42 registered recovery reads; 2,496 canonical rows, 144 checklist rows; 27 cached QE source files match their retrieval receipts |
| Mutation checks (`PH/mutation_checks.json`) | 12 of 12 mutants caught by real-file tests (against V2 `63655f45...`, unchanged since) |
| Re-test code, tests, fixtures, spec, scripts (19 files) | byte-identical before and after the run |
| Tracked files modified in the worktree at the end | none (`git status`); untracked: the new files of this phase |

Python 3.9 (Anvil's interpreter): V2, RT and the contract parse under the 3.9 grammar (`ast.parse(feature_version=(3, 9))`) and use no API newer than 3.9; they were run only under the local Python 3.12, and the remote PREFLIGHT replay is the first run under 3.9.

## 8. Spec diff against the first trial

`PH/launch_spec.json` (schema `pa-catalyst-retest-v1`, SHA-256 4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435) against `results/pa_catalyst_trial_2026-10-03/launch_spec.json` (`4bed5002...`):

| Field | First trial | Re-test |
|---|---|---|
| schema, date | `pa-catalyst-trial-v1`, 2026-10-03 | `pa-catalyst-retest-v1`, 2026-10-04 |
| isolated remote parent / output root | `.../sts_pa_catalyst_2026-10-03` / `.../trial_results` | `/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04` / `.../trial_results` (not created; the controller refuses an existing root) |
| dependency pins | `pa_catalyst_trial.py` `d00656aa`, `pa_qe_adapter.py` `25546421`, `pa_checked_contract.py` `67412c83`, wrapper `89_...slurm` `0ff3deac` | `pa_catalyst_retest.py` `b1c49d2d`, `pa_qe_adapter_v2.py` `63655f45`, `pa_checked_contract.py` `67412c83` (unchanged), wrapper `90_pa_catalyst_retest.slurm` `d30ca93f` |
| source review pin | `source_boundary_review.md` `7efb6e27` | `PH/source_xml_input_review.md` (the stop/optimizer review of the first trial stays in force) |
| new fields | none | `predecessor`, `decision_ref`, `preflight_replay` (12 pinned fixture files, expected result) |
| source deck, `pw_x`, `mpirun`, five UPFs, four-file density seed, target | pinned | unchanged (same hashes; deck path moved to the new parent) |
| allocation, caps, parallel shape, negative control | 1 node, 128 CPUs and billing, 16 h, 2,048 SU, 200 GiB, 6 calls <= 7,200 s, 7,080 s QE stop, `128/1/1/1/8/16`, negative control on | unchanged |
| wrapper | job `pa-catalyst-boundary`, log `trial_%j.log`, `pa_catalyst_trial.py` | job `pa-catalyst-retest`, log `retest_%j.log`, `pa_catalyst_retest.py`; every `#SBATCH` resource line identical |

## 9. Cost envelope

`PH/cost_envelope.py` -> `PH/cost_envelope.json`; arithmetic from the measured control call (2,883.94 s = 102.54 SU; job charged 2,893 s = 102.8622 SU), the READOUT section 8 call costs, 0.035556 SU/s on a 128-core whole node.

| Path | Seconds in calls | SU | SU with an idle allowance for checkpoint copying and hashing (30 min on the RESUME path as in READOUT section 8; 10 min on HOLD and RESEED, which copy less) |
|---|---|---|---|
| RESUME, fresh at 3,385 s / 3,670 s / 4,680 s | 12,173 / 12,458 / 13,468 | 432.8 / 443.0 / 478.9 | 496.8 / 507.0 / 542.9 |
| HOLD (fresh stalls, killed near 6,420 s) | 9,884 | 351.4 | 372.8 |
| RESEED (one reseed evaluation about 600 s) | 7,734 | 275.0 | 296.3 |

Cumulative on the RESUME mean path: 102.5 after the control, 123.2 after the candidate, 253.7 after the fresh SCF, 340.4 after the resume, 443.0 after the negative control. Range of the plan, 430-540 SU, holds: 275-543 SU, at most 26.5 % of the 2,048 SU cap; wall clock about 3.5 h of 16 h.
Projected CPU balance from the 36,775.4 SU of READOUT: 36,500 (floor) to 36,232 (ceiling); 34,727 at the cap. The live balance is read again by the stage and submit scripts (>= 2,048 SU required).
Counted from the code, the checkpoint handling is 22 SHA-256 passes over the 15.07 GB checkpoint and 3 full copies (each `copy_checkpoint` is 5 passes plus one copy; the rest are decision inventories): 332 GB hashed; at an assumed 0.5-1.5 GB/s that is 4-13 minutes, 9.5-26.8 SU, inside the 30-minute allowance. Unmeasured.
Base rate from the real September logs: 6 of 21 fresh SCFs stalled at iteration 127 (a different set of geometries); each repeated validator mismatch would cost 103 SU at the control call, 245-290 SU at the fresh call, which is what the PREFLIGHT replay is for.

## 10. What remains unverified

* A real `calculation='scf'` XML from the catalyst deck itself (none exists): the fresh path is verified on 19 real scf Hubbard files of other decks, the 72-atom fresh logs (no XML), and the QE source. The cross-arm XML identity of the fresh arm against the control is inferred, not observed.
* A real restart log at 72 atoms and 128 ranks: only the serial H2 restart is real. The resumed arm's wavefunction/optimizer carry-over, the negative control and the reseed arm at catalyst scale are untested; supervisor timing and EXIT behaviour of the later calls are untested on real runs.
* The carry-over hypothesis itself, the warm-versus-fresh decision and the reseed branch: not reached by job 21034683 and not tested by anything above.
* Checkpoint copy/hash time (arithmetic only), whether the fresh SCF stalls (28.6 % of September fresh SCFs) or converges lower.
* V2 and RT under Anvil's Python 3.9: not run here; the remote PREFLIGHT replay runs them on the real control at zero SU.
* The post-run readout tool (`readout_trial.py`) is bound to the first trial's names (`SPEC_REL`, `CTRL`, `ADP`); a re-test-aware copy is needed before the post-run readout, not before submission.
* No independent review of V2, RT, the spec or the scripts yet.

## 11. Steps left before submission

1. Frank reads this note; decides the lineage question of section 3.
2. Independent review of V2, RT, the spec, the scripts and `PH/source_xml_input_review.md`; its decision file `PH/independent_launch_review_final.md` must contain `Decision: GO_ONE_BOUNDARY_RETEST_PRELAUNCH`.
3. `python PH/verify_retest_offline.py checked` (receipt `PH/offline_checked.json`; runs the gate again plus `bash -n` on the wrapper and the stale-receipt checks).
4. `python PH/publish_reviewed_package.py`: commit and push of explicit paths only (refuses while any tracked file is modified); writes `PH/publication_final.json`.
5. Frank's go for Anvil. `python PH/pa-catalyst-retest-remote-stage-2026-10-04.py`: new isolated checkout of the published commit, byte pins, `bash -n`, remote PREFLIGHT including the real-control replay, `mybalance`, `squeue`, partition, quota.
6. Live balance check (inside steps 5 and 7; >= 2,048 SU) and singleton queue check.
7. Frank's go for submission. `pa-catalyst-retest-submit-held-2026-10-04.py` (one held `sbatch`, once-only intent file), then `pa-catalyst-retest-held-validation-2026-10-04.py`, then `pa-catalyst-retest-release-2026-10-04.py` (one `scontrol release`), then `watch_retest_readonly.py --job-id N`.

## 12. Files

New only. Source and tests: `src/dft/pa_qe_adapter_v2.py`, `src/dft/pa_catalyst_retest.py`, `anvil/90_pa_catalyst_retest.slurm`, `tests/test_pa_qe_adapter_v2.py`, `tests/test_pa_qe_adapter_v2_real.py`, `tests/test_pa_catalyst_retest.py`,
`tests/test_pa_catalyst_retest_scripts.py`, `tests/qe75_real_fixtures.py`, `tests/fixtures/qe75_real/**`. This note. `PH/`: `launch_spec.json`, `build_launch_spec.py`, `source_xml_input_review.md`, `audit_real_outputs.py/.json`, `audit_table.md`, `render_audit_table.py`,
`run_mutation_checks.py`, `mutation_checks.json`, `cost_envelope.py/.json`, `capture_pins.py`, `pins.json`, `build_fixtures.py`, `adapter_v2_vs_frozen.diff`, `controller_retest_vs_frozen.diff`, `verify_retest_offline.py`,
`offline_initial.json`, `scientific_initial/`, `publish_reviewed_package.py`, `pa-catalyst-retest-remote-stage-2026-10-04.py`, `...-submit-held-...py`, `...-held-validation-...py`, `...-release-...py`, `watch_retest_readonly.py`, `.gitattributes`.
`results/` is git-ignored (`.gitignore` line 14): the phase files are published with `git add -f` on explicit paths by `publish_reviewed_package.py`.

## 13. Continuation review and original launch binding (2026-10-04)

The user requested independent review, exact original-launch readout checks, fresh verification and explicit-path publication. Anvil staging and submission remain separate user approvals. The lineage question is resolved by keeping the repaired current adapter and the additive V2 separately: historical checks load all 13 original source/document/deck files from implementation commit b9f0208ee6f3cd71d0201d03b964b5c23f53d644, verified against launch publication pins. The snapshot manifest itself has fixed SHA-256 dcb15854775caa79577ee6eb6b623dc135d4de487e3c2b027949f8c5da2ade0b.

Historical readout citations now resolve to fixed coordinates in that snapshot. The original trial document had three fewer header lines than the later version used by the readout; historical_citation_rebinding.json records the explicit coordinate correction. The loader imports the exact original controller, adapter and contract independently of cached live modules, and the readout records the full source manifest. Spec overrides with different bytes are refused. Default spec and deck use original snapshot bytes. Previous failed verification receipts and the original readout code are retained; the original trial remains INCONCLUSIVE. Fresh full readout pytest must pass without waived or deselected assertions.

Independent review found a check-then-write race in the new submission scripts. Local and remote intent files now use exclusive creation and durable flush before submission or release. A second concurrent invocation cannot issue a second sbatch, release again, or overwrite the owner’s receipt. The watcher also counts inner scheduler collection errors toward its three-failure stop, while accepting terminal accounting if scontrol has purged the job. These changes affect launch safeguards and observation only.

Verification and final independent gate receipts follow under PH; publication retains exact reviewed source/test/spec/script bytes and untouched historical evidence. Expected cost is still 275–543 CPU SU, ceiling 2,048 SU / 16 h, no automatic retries. No Anvil stage or submission has been run during this continuation.

Focused verification retained two preparation failures: the initial original-document citation offset and a threshold-literal test that also counted a source line numbered 16 as a resource constant. Citation tuples are now excluded only from that numerical-literal scan; genuine scientific/resource literals remain checked. The full fresh gate reruns every historical readout test, with no exception for these preparation failures.
