# Catalyst P-A boundary trial: readout of Slurm job 21034683, 2026-10-04

Status: the one approved job has ended. The controller recorded **INCONCLUSIVE** after the first of its
registered calls, with the error `one XML lda_plus_u required`. The charge was **102.86 CPU SU**. This note
records the outcome, the cause with file:line evidence, a zero-SU offline dry-run of the one-line correction
against the real control output, the hash-pinned mirror, what the pre-stated documents say happens after a
non-pass, and the cost envelope of one corrected re-run of the same trial. **No scientific acceptance
decision is made here, nothing was submitted or re-run, and no production run is proposed.** Sections 7
and 9 list the choices that return to Frank.

Citation abbreviations (path:line): DOC = `docs/research/pa-catalyst-trial-2026-10-03.md`;
PREP = `docs/research/pa-catalyst-trial-readout-prep-2026-10-04.md`; ADP = `src/dft/pa_qe_adapter.py`;
CTRL = `src/dft/pa_catalyst_trial.py`; QE = the cached official QE 7.5 source under
`results/pa_catalyst_trial_2026-10-03/qe_source/`; MIR = `results/pa_catalyst_trial_readout_2026-10-04/mirror/`.

## 1. Outcome

| Item | Value |
|---|---|
| Readout label | **INCONCLUSIVE**, label basis `FROZEN_CONTROLLER_RECORD_ONLY`, call class `RAW_VALIDATION_REFUSED`, open question OQ8 (`readout/readout_verdict.json`, `readout/readout_table.md`) |
| Controller receipt | `scientific_status` INCONCLUSIVE, `scheduler_status` COMPLIANT, `call_count` 1, `error` "one XML lda_plus_u required" (`MIR/trial_results/trial_receipt.json`) |
| Calls run | 1 of the registered sequence (control). Candidate, fresh, resumed and negative never started; the restart carry-over, the fresh-versus-warm decision and the continuity comparison were therefore not tested at all |
| Slurm | FAILED, exit 3:0, Start 2026-10-04T09:38:38, End 10:26:51, ElapsedRaw 2,893 s, 128 CPUs, `billing=128,cpu=128,mem=200G,node=1`; the `.batch` step is FAILED 3:0, `.extern` COMPLETED 0:0 (`scheduler/sacct.txt`) |
| Exit code meaning | 3 is the frozen controller's "non-PASS result" exit (CTRL:1021) |
| Resource checks | allocation shape, memory, no GRES, elapsed within 16 h, charge within 2,048 SU: all ok. The call's allocation receipt was compliant with 57,591 s remaining (`allocation_before_call_01.json`) |
| Raw QE facts for the one call | QE 7.5, MPI 128 / 1 thread / 8 pools / ELPA 4*4, JOB DONE, "Program stopped by user request", XML exit status 255, three SCF evaluations converged in 3, 12 and 23 iterations, SCF cycles [1, 2, 3], no failure marker, no stall, first threshold 1.0E-06, PWSCF wall 2,874.61 s, controller process time 2,883.94 s (cap 7,200 s), stop requested at 2,860.2 s on the registered boundary |
| Scientific status | none: no acceptance, rejection or continuity statement follows, because the call that would have carried it was refused by the validator after QE had finished |

### Charged SU

| Figure | Value |
|---|---|
| `ElapsedRaw x billing / 3600` = 2,893 x 128 / 3,600 | **102.8622 SU** (readout's charged figure) |
| `CPUTimeRAW / 3600` = 370,304 / 3,600 | 102.8622 SU |
| `jobsu 21034683` ("CPU SUs Already Used", hours rounded to 0.8036) | 102.8608 SU (`scheduler/jobsu.txt`) |
| `mybalance` CPU balance | 36,878.2 before, 36,775.4 after (difference 102.8 at one decimal; `scheduler/mybalance.txt`) |
| Cap | 2,048 SU, so 5.0 % of the cap was charged |

The SU of record is not defined by the registered documents (PREP OQ6). All three figures agree to 0.0014 SU.
Slurm's `scontrol show job` and `squeue` no longer list the job ("Invalid job id specified"), so no
`--scontrol` text was passed to the readout.

## 2. Root cause, with evidence

The adapter requires an XML element that QE 7.5 never writes.

1. ADP:626 `value(dftu, "lda_plus_u", True)` inside `_check_xml_common_source`, reached from `_check_xml_input`
   (ADP:538) from `read_qe_arm` (ADP:807). `value` calls `_one(parent, tag)` (ADP:547-548); `_one` raises
   `AdapterError("one XML " + name + " required")` when it does not find exactly one child (ADP:410-413).
2. The real control XML (`MIR/trial_results/control/outdir/slab_c5low__pa_boundary.save/data-file-schema.xml`,
   lines 150-158, QE 7.5, SHA-256 `3b556aa7...0b699d`) has this input `<dft>` block, and no `<lda_plus_u>`
   element anywhere in the file (0 occurrences):

   ```
   <dftU new_format="true">
     <lda_plus_u_kind>0</lda_plus_u_kind>
     <Hubbard_U specie="Co" label="3d">1.220077496231744E-001</Hubbard_U>
     <Hubbard_U specie="Cr" label="3d">1.359724920499233E-001</Hubbard_U>
     <Hubbard_U specie="Mn" label="3d">1.433223564850543E-001</Hubbard_U>
     <U_projection_type>atomic</U_projection_type>
   </dftU>
   ```
3. QE source: the writer `qes_init_dftU` takes `new_format, lda_plus_u_kind, Hubbard_Occ, Hubbard_U, ...,
   U_projection_type, ...` and has no `lda_plus_u` argument (QE `Modules/qes_init_module.f90:1228-1231`,
   `lda_plus_u_kind` at :1238 and :1265). It is called from `Modules/qexsd_init.f90:510`. QE's own XML reader
   derives the flag from presence of the block, `lda_plus_u = dft_obj%dftU_ispresent`
   (`Modules/qexsd_copy.f90:403`), so the registered meaning of "Hubbard U is on" is the presence of `<dftU>`.
4. The unit-test fixture hides this. `tests/test_pa_qe_adapter.py:531-533` builds its Hubbard case by string
   substitution on the H2 fixture XML and inserts `<dftU><lda_plus_u>true</lda_plus_u><lda_plus_u_kind>0...`,
   an element that no real QE 7.5 file contains; the fixture's deck line is at :517 (`HUBBARD (atomic)`, `U H-1s 3.32`).
5. Nothing before the launch exercised a Hubbard deck against real QE output. The real tiny run
   (`results/s2_2026-09-25/full_text/sequential_2026-10-03/pa_tiny_raw`, 65 files) is H2, `calculation='relax'`
   only, and none of its files contains `HUBBARD`, `dftU`, `lda_plus_u` or `Hubbard_U`. Real Hubbard XML did
   exist in the repository before the launch: 19 QE 7.5 files `runs/a0/pproj6/*/dens/*.save/data-file-schema.xml`
   carry `<dftU>` and none carries `<lda_plus_u>`.
6. How it ended: CTRL:850-854 calls `read_qe_arm`; the exception is caught at CTRL:875-878 (call status
   INCONCLUSIVE, error text kept), propagates to `run()` (CTRL:982-984, trial status INCONCLUSIVE), and
   `main` returns 3 (CTRL:1021). The candidate call was never launched, which is why the job ended after
   48 minutes of its 16-hour allocation. The retry rule (no hidden rerun) is not engaged by this: nothing re-ran.

The failure is a validator/schema mismatch at the parse step. QE itself finished normally.

## 3. Hash-pinned mirror (read-only on Anvil)

Remote root `/anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03`, scope `trial_results` plus
`trial_21034683.log`. The stdlib snippet `results/pa_catalyst_trial_readout_prep_2026-10-04/remote_inventory_snippet.py`
(SHA-256 `38d7de77...a4ba32`, unmodified) was piped over ssh to the remote Python 3.9; it lists and reads only.
Two passes (`remote_inventory.json`, `remote_inventory_pass2.json`) are byte-identical, so the tree did not
change while the mirror was taken.

| Quantity | Value |
|---|---|
| Files / bytes inventoried | **403 files, 15,230,260,163 bytes** (15.2 GB), 0 symlinks, no `.EXIT` file anywhere |
| SHA-256 recorded on the remote | 274 files (every file at or below the snippet's 50 MiB limit), 10,246,639 bytes |
| Size only (no login-node hash) | 129 files: 128 per-rank `.wfcN` (15,070,248,960 bytes, about 118 MB each) and `charge-density.hdf5` (149,764,564 bytes) |
| Per-rank files below the limit, hashed on the remote but not copied | 128 `.mixN` (0 bytes each) and 127 `.restart_scfN` (2,583,942 bytes in total) |
| Copied to `MIR` | **19 files, 7,662,697 bytes**: `trial_21034683.log`, `trial_receipt.json`, `allocation_before_call_01.json`, the 5 UPFs in `common_pseudo/`, and for `control/`: `input.in`, `stdout.log`, `stderr.log`, `process_receipt.json`, `setup_receipt.json`, `.bfgs`, `.update`, `.restart_scf`, `data-file-schema.xml`, `occup.txt`, `paw.txt` |
| Not copied | 384 files, 15,222,597,466 bytes (the 15 GB bulk, inventoried only) |
| Verification | all 19 copied files match the remote SHA-256 and size, in both inventory passes: 0 mismatches, 0 local files outside the inventory (`mirror_verification_pass1.json`, `mirror_verification_pass2.json`) |

Transfer was per-file `scp` (not a tar pipe). An independent end-to-end check: the controller's own
`process_receipt.json` recorded SHA-256 for `stdout.log` and `stderr.log` at 14:26:51 UTC, and both equal
the remote inventory hashes and the local copies. The bulk (wavefunctions and charge density) is not hashed
anywhere and stays on Anvil; the 15.2 GB remains in the project directory untouched.

## 4. Scheduler and readout run

`readout_trial.py` ran on the mirror with the saved `sacct`, `jobsu` and `--remote-inventory` records and
`--balance-before 36878.2` (outputs in `readout/`). Its own findings, in addition to the label:

- scheduler checks all ok; Slurm exit versus controller: "controller wrote a non-PASS result (CTRL:1021 exit 3)";
- per-call table: control, INCONCLUSIVE, `RAW_VALIDATION_REFUSED`, stop reason `registered-evaluated-boundary`,
  rc 0, process 2,883.94 s, SCF log 3 converged / 0 not converged / max iteration 23, SCF cycles [1, 2, 3]
  equal to the registered [1, 2, 3], XML exit 255, raw header MPI128 / thr1 / npool8 / ELPA [4, 4];
- raw re-derivation through the frozen adapter fails on the control with `AdapterError: one XML lda_plus_u required`,
  the same error the controller recorded; no integrity flag, no mirror gap, no citation drift;
- criteria: `SEQUENCE` PARTIAL_PREFIX, `REJECT_LIST` NOT_MET, `BOUNDARY_COUNTS`, `FIRST_THRESHOLD`,
  `CONTINUITY_TOL` NOT_EVALUATED (no validated call), `NO_PRODUCTION` MET, `SCHED_*` MET.

One quirk of the readout tool, not affecting the label: its `RAW_BINDING` criterion prints MET here because that
criterion is evaluated only over validated calls and there are none; the control's failed re-derivation is
recorded under `rederivation.arms.control.error`.

## 5. Zero-SU offline dry-run of the one-line correction

Scratch only, inside `dryrun/` (nothing outside the new directory was touched; the frozen files are unchanged).
`dryrun/scratch/pa_qe_adapter.py` is a copy of ADP with exactly one line replaced (diff in
`dryrun/adapter_patch.diff`): ADP:626 `value(dftu, "lda_plus_u", True)` is turned into a comment. The checks
`lda_plus_u_kind == 0`, `U_projection_type == source unit`, and the `Hubbard_U` species / shell / eV comparison
(1e-10 eV) are kept. `pa_qe_adapter_FROZEN_COPY.py` is a byte-identical copy of the frozen adapter (SHA-256
`25546421...628879`, equals ADP and the `launch_spec.json` pin) used to reproduce the original failure; the
contract module copy is also hash-identical to its pin.

`dryrun/dryrun_control.py` replays the controller's control-call acceptance chain (CTRL:837-871) on the real
mirrored files, with the same arguments the controller used (`expected_parallel = SHAPE`,
`expected_exit = "clean_stop"`, `expected_evaluations = 3`, the pinned UPF map, the source deck bound to its
spec hash). Result in `dryrun/dryrun_control_result.json`:

| # | Check (controller reference) | Frozen adapter | Single-line patch |
|---|---|---|---|
| 1 | Process contract flags: not timed out, within 7,200 s, no supervisor/capture error, no failure marker, no HEA4 stall, no solver limit (CTRL:840-844) | PASS | PASS |
| 2 | `stop_reason == registered-evaluated-boundary` (CTRL:845-846) | PASS | PASS |
| 3 | No stale `.EXIT` after shutdown (CTRL:847-849); none in the mirror or in the full remote inventory | PASS | PASS |
| 4 | `read_qe_arm`: raw input / log / XML / process validation, 3 evaluated steps, clean stop (CTRL:850-854, ADP:761-914) | **FAIL**, `AdapterError: one XML lda_plus_u required` | PASS |
| 5 | Global SCF counters equal the registered `[1, 2, 3]` (CTRL:855-856) | not reached | PASS |
| 6 | First-boundary SCF threshold equals 1e-6 Ry (CTRL:857-858, ADP:917-920): log 1.0E-06, deck 1e-06 | not reached | PASS |
| 7 | Control XML settings identity recorded for later arms (CTRL:859-860): `3bd17094...32f0` | not reached | PASS |
| 8 | Source pins checkable offline (CTRL:872, 714-723): the five `common_pseudo` UPFs equal their `launch_spec.json` SHA-256 pins; the repo copies of the three dependency modules equal their pins | PASS | PASS |

**With only this one change the control call would have been accepted and the controller would have gone
on to launch the candidate call.** No further latent mismatch exists in the control call's validation.

Margins for the individual checks inside check 4 (`dryrun/dryrun_evidence.json`, adapter line ranges):

| Internal check | Measured on the real file |
|---|---|
| Deck re-parse equals the source settings identity (ADP:777-779) | equal |
| Return code in {0, 255}, not timed out (ADP:783-784) | rc 0, not timed out |
| No failure regex hit in stdout plus stderr, "JOB DONE." present (ADP:785-786) | 0 hits; stderr is only 8,472 bytes of two `Note: ... IEEE_DENORMAL / IEEE_UNDERFLOW_FLAG` lines, which the failure regex does not match |
| Exactly one QE 7.5 banner (ADP:787-788) | ["7.5"] |
| XML units, creator NAME / VERSION (ADP:793-797) | "Hartree atomic units", PWSCF 7.5 |
| XML `parallel_info` equals the registered shape (ADP:798-805) | nprocs 128, nthreads 1, ntasks 1, nbgrp 1, npool 8, ndiag 16 |
| Raw runtime header: MPI, threads, pools, ELPA 4*4 (ADP:806, 706-758) | all five header lines matched once |
| XML `input` against the actual deck and source settings (ADP:807, 510-643) | PASS after the patch; 38 distinct XML lookups, each found exactly once; Hubbard U (XML Ha x 2 x Ry_eV): Co-3d 3.32, Cr-3d 3.70, Mn-3d 3.90 eV, equal to the deck's HUBBARD card within 4.4e-16 eV |
| 3 `<step>` evaluations converged, force dimensions 3 x 72 (ADP:810-816, 474-488) | 3 steps |
| Clean-stop evidence: exit 255, relax, "Program stopped by user request"; no "bfgs converged in"; no "maximum number of steps" (ADP:817-823) | satisfied |
| No "Maximum CPU time / wall time" (ADP:837-838) | absent |
| Evaluated count equals 3 (ADP:839-840) | 3 |
| Log versus XML energies, bound 5.1e-8 Ry (ADP:841-846) | max 4.6e-9 Ry |
| Three force blocks of 72 atoms, species order, masked log force versus XML, bound 5.1e-8 (ADP:847-864) | 3 x 72 rows, max 5.0e-9 Ry/bohr |
| Logged proposal geometries cover each move and the saved XML proposal (ADP:865-882) | 3 blocks, max differences 9.4e-11 bohr |
| First evaluation at the input geometry (ADP:883-884) | 7.1e-15 bohr |
| No fixed coordinate moved (28 fully fixed atoms) (ADP:885-889) | max drift 3.6e-14 bohr |
| Threshold present, five UPF reads with MD5 and pinned SHA-256 (ADP:894-898, 683-703) | 1.0E-06; five reads matched against the mirrored `common_pseudo` |

### Adjacent probes on the same real files (not part of the control call's own chain)

- `read_bfgs` (ADP:1088-1146; the controller calls it on the candidate checkpoint, CTRL:903) on the real control
  `.bfgs` against the third evaluated step: PASS. Dimension 226 (3 x 72 + 10), counters scf 3 / bfgs 3 / gdiis 0,
  inactive tail 0.0, trust-radius resets 0, saved energy equal to the third evaluated energy
  (-7551.869475892178 Ry), gradient correspondence to 1e-8. The candidate-stage reader therefore parses a real
  72-atom QE 7.5 optimizer file; the controller's candidate-specific counters (1, 1, 0) were not testable here.
- `compare_trajectories` (ADP:1308-1329) on the real control evaluations against themselves: runs, trivially
  within tolerance (reader sanity only, not a continuity result).
- `_xml_evaluation` on the real `<output>` node of the relax stop: FAIL, `XML evaluation has no converged SCF`.
  This is **not informative**: that node is a post-move proposal (`output/convergence_info/scf_conv/convergence_achieved`
  is `false`, there is no `output/forces`), not the node type of a converged SCF. See section 6.

### Tag audit against the real XML

An AST walk of ADP finds 94 tag, attribute or comparison references. Compared against the tag and attribute
names present in the real control XML, exactly one required element is absent: **`lda_plus_u` at ADP:626**.
The other 15 flagged names are not XML requirements and are false positives of the naive comparison: the input
namelist names `control`, `electrons`, `ions`, `system` (ADP:176), the deck card `HUBBARD` (ADP:206), the
exclusion list `max_xml_steps`, `wfcdir`, `startingpot`, `startingwfc` (ADP:497, 501), the optional zero-checked
tags `Hubbard_J`, `Hubbard_J0`, `Hubbard_alpha`, `Hubbard_alpha_back`, `Hubbard_beta` (ADP:639), and the root
attribute `Units` (ADP:793, which passes). Tags the adapter requires that real QE 7.5 does contain were
confirmed present, including `lda_plus_u_kind`, `U_projection_type`, `Hubbard_U` with `specie` / `label`,
`monkhorst_pack` with `nk1..k3`, `starting_magnetization`, `symmetry_flags/nosym,noinv`, `ion_control/ion_dynamics`,
`parallel_info` and `exit_status`.

One class of risk that is not triggered by this deck: several `value()` comparisons are literal string matches
against the deck (for example `diagonalization`, ADP:565-570), whereas QE canonicalizes some inputs (input
`david` is written as `davidson`, `PW/src/pw_init_qexsd_input.f90:477`; the real XML shows `davidson`).
`_schema_smearing` (ADP:424-439) handles that for smearing only. The registered deck sets no `diagonalization`.

## 6. What the offline dry-run cannot reach

These are not claimed mismatches, only paths with no real-file evidence:

- Candidate, resumed, negative: same adapter path as the control, but the saved-checkpoint logic
  (`pre_resume_decision`, `audit_consumption`, `compare_trajectories` on split runs, `contract.decide_segment`) needs
  the candidate checkpoint and the fresh arm; the 15 GB control checkpoint is retained on Anvil but was not
  mirrored (the controller does not read it).
- Fresh arm (`calculation='scf'`, `expected_exit="normal_scf"`): `_xml_evaluation(output, ...)` (ADP:826-833) needs
  `output/convergence_info/scf_conv`, `output/total_energy/etot` and `output/forces`. QE writes `output/forces`
  only when `lforce .and. conv_elec` (QE `PW/src/pw_restart_new.f90:740`); the deck has `tprnfor = .true.`, so a
  converged SCF is expected to carry it, but no real QE 7.5 `calculation='scf'` output exists locally for this
  or the tiny run, so this path has only ever run against the synthetic fixture
  (`tests/test_pa_qe_adapter.py:147-149`).
- Cross-arm XML identity (ADP:808-809): later arms must equal the control's complete XML `input` minus the
  declared operational fields; only the control exists. One calculation-dependent candidate was checked in
  source: `disk_io` is written as "low" when the input is `default` regardless of the calculation
  (QE `Modules/qexsd_input.f90:85-86`), so it cannot differ between a relax and an scf arm.
- Supervisor timing for calls after the first, and the cost of copying and hashing the 15 GB checkpoint between
  calls.

## 7. What the pre-stated documents say after a non-pass

PREP sections 7-8 (both marked UNADOPTED there) and the registered DOC, applied to this outcome:

- No hidden rerun: the trial reports its result and actual SU "without a hidden rerun" (DOC:107); the approval is
  for exactly one job (DOC:8-9); teardown cannot justify exceeding authority or launching a replacement
  (`independent_launch_review_final.md:136`); unused cap is not permission for another job
  (`pa-tiny-restart-readout-2026-10-03.md:80`). The job ended with about 15.2 hours of its allocation unused;
  that is not a licence to continue, and nothing was continued.
- Production relaxation, every-step P-A, S8 ranking and melt selection stay unlicensed (DOC:10, DOC:51,
  `eligible-comparison-pa-readiness-2026-10-03.md:162`). `production_accepted` is false in the receipt.
- The choice returns to Frank (PREP:175). PREP:181-183 lists the three options with their prerequisites: a
  corrected one-boundary re-test (needs a cause-specific correction with source review and a new dated A11.R3
  line; cap not above the trial's 2,048 SU), P-C (fresh-start SCF per step; needs an external BFGS driver that
  does not exist), or stop protocol work and keep the evidence (zero further SU, S8 hold unchanged).
- What this outcome adds to that choice: PREP:175 frames a non-pass as the result of the restart carry-over test.
  This trial never reached the carry-over test, so it is silent on whether the optimizer-state carry-over works,
  and it gives no evidence for P-C versus a repaired P-A.
- Mechanics of a corrected re-test, from the documents and the code: the correction changes
  `src/dft/pa_qe_adapter.py` (a hash-pinned dependency in `launch_spec.json`) and the fixture at
  `tests/test_pa_qe_adapter.py:531-533`; both are frozen and untouched here. The frozen controller refuses an
  existing output root (`preflight`, CTRL:546), so a re-run needs a new spec, a new dated line and a new output
  root; the present 15.2 GB output is not reused by it.

## 8. Cost envelope of one corrected re-run of the same trial

Basis: the measured control call (this job), and, for the fresh call that was never run, the banked September
Arm A figures (PREP section 6). SU = seconds x 128 / 3,600 = 0.03556 SU per second, whole-node billing.

Measured in this job: control process 2,883.94 s = 102.54 SU; the job as charged 2,893 s = 102.86 SU. Cumulative
QE times at the end of each SCF were 478.8, 1,283.6 and 2,782.1 s (convergence in 3, 12, 23 iterations);
forces cost about 64 s per evaluation (`forces` 192.56 s over 3 calls). These are 0 %, 14 % and 11 % above the
September low-state cycle ends quoted in PREP:109-111 (480.0, 1,121.6, 2,498.7 s), so the control call ran
15 % longer than the pre-trial planning figure of 2,498.7 s.

| Call | Basis | Seconds | SU |
|---|---|---|---|
| control | measured | 2,884 | 102.5 |
| candidate (stop after SCF 1) | measured: 478.8 s to SCF 1 plus forces, start and teardown | about 580 | about 21 |
| fresh SCF at the evaluated geometry | not measured here; September converged fresh checks at the tighter 8.08e-8 Ry: 3,385-4,680 s, mean 3,670 s (the registered target here is the looser 1e-6 Ry) | 3,385 / 3,670 / 4,680 | 120 / 130 / 166 |
| resumed (two evaluations) | measured control evaluations 2 and 3 plus restart start-up | about 2,440 | about 87 |
| negative control (3 evaluations) | taken equal to the control | about 2,884 | about 102.5 |

| Path through the trial | Total seconds | Total SU |
|---|---|---|
| Full RESUME path, fresh at 3,385 s | 12,173 | **433** |
| Full RESUME path, fresh at the 3,670 s mean | 12,458 | **443** |
| Full RESUME path, fresh at 4,680 s | 13,468 | **479** |
| Same, plus 30 min of idle billed time for 15 GB checkpoint copies and hashing (an assumed allowance, not measured) | 13,973-15,268 | 497-543 |
| HOLD path (fresh stalls and is killed near 6,420 s) | 9,884 | 351 |
| RESEED path (control, candidate, fresh at the mean, one reseed evaluation of about 600 s) | 7,734 | 275 |

Reading: a corrected re-run of the same trial is of the order of **430-540 SU** on the RESUME path, about 21-27 %
of the 2,048 SU / 16 h cap, and would leave the CPU balance near 36,230-36,340 SU from today's 36,775.4. The
pre-trial planning sum of 390 SU (PREP section 5) was priced from a control call 15 % shorter than measured.
The first call alone (the one that has now been measured) is about 103 SU, so a second validator mismatch
discovered at the control step would again cost about 103 SU; one discovered at the fresh step would cost about
245-290 SU (about 350 SU if that fresh call stalls and is killed). The cap is the approved ceiling, not a runtime prediction. Whether the allowance for copies and
hashing is large enough can only be measured by running the later calls.

## 9. Questions that return to Frank (not decided here)

1. Label for a validator refusal after a complete, clean control run (PREP OQ8, extended). The controller records
   INCONCLUSIVE; DOC:82-83 says "reject" without a label; no FAIL is defined anywhere. The readout reports what
   the controller recorded and does not choose.
2. The section 7 choice: corrected one-boundary re-test (cost in section 8, prerequisites in section 7), P-C, or
   stop. This trial did not test the carry-over hypothesis, so it does not favour any of them.
3. Whether the retained 15.2 GB control output should stay on Anvil unchanged; nothing was deleted or moved.

## 10. Files, access log and regression

New files only, in `results/pa_catalyst_trial_readout_2026-10-04/` (listed relative to it) and this note:

- `mirror/` (19 mirrored files with the remote layout), `mirror_copy_list.txt`, `remote_inventory.json`,
  `remote_inventory_pass2.json`, `remote_inventory_run_utc.txt`, `remote_inventory_pass2_run_utc.txt`,
  `remote_inventory*.stderr.txt`, `remote_inventory_snippet.sha256`, `verify_mirror.py`,
  `mirror_verification_pass1.json`, `mirror_verification_pass2.json`
- `scheduler/` (`sacct.txt`, `sacct_watcher_format_nheader.txt`, `jobsu.txt`, `mybalance.txt`, `sched_probe.json`,
  `sched_probe2.json`, stderr) and `sched_probe_remote.py`, `sched_probe_remote2.py`
- `readout/readout_verdict.json`, `readout/readout_table.md`
- `dryrun/` (`scratch/` adapter copies, `adapter_patch.diff`, `dryrun_control.py`, `dryrun_control_result.json`,
  `latent_probes.py`, `latent_probes_result.json`, `dryrun_evidence.py`, `dryrun_evidence.json`)

Anvil access, all read-only, over key-authenticated ssh to the login node: two stdlib size listings
(`os.walk` + `lstat`), the inventory snippet twice (reads and hashes files up to 50 MiB, 10.2 MB), one probe
running `sacct`, `scontrol show job`, `squeue`, `jobsu`, `mybalance`, and `scp` of the 19 files. `jobsu -h` and
`jobsu -j` were run once by mistake: that tool takes a positional job id, so it passed the flag to `sacct` and
printed errors; the correct call is `jobsu 21034683`. No `sbatch`, `srun`, `scancel`, `scontrol update`, no file
created, changed or removed on Anvil, no QE run, no paid API call. Nothing in `results/pa_catalyst_trial_2026-10-03/`
(where the watcher recorded its last state, FAILED, at 14:27:39 UTC) or any frozen file was modified; no `git add`,
commit or push was run (only read-only `git status` / `rev-parse`).

Regression after the readout (`results/pa_catalyst_trial_readout_prep_2026-10-04/run_regression.py post_readout`, receipt
`regression_post_readout.json`, verifier output `scientific_post_readout/`, HEAD 580ec48 on `r0-catalysis-revival`):

| Check | Result |
|---|---|
| Byte pins before and after | 9,816 tracked + 21 unrelated files, 0 errors both times |
| Frozen code pins (adapter, controller, tests, wrapper, spec, source review, replay, watcher, verifier) | unchanged |
| Evidence unittest discovery | 83 tests, 0 failures, 0 errors |
| Compute suites (eleven files) | 491 passed, 3 skipped, 7 subtests passed |
| Readout tool tests | 74 passed |
| Scientific verifiers | both pass; 42 registered recovery reads |
| Tracked files dirty before / after | none / none |

These counts equal the `final3` run recorded in PREP section 9. `results/` is listed in `.gitignore` (line 14), so the
new `results/pa_catalyst_trial_readout_2026-10-04/` directory is not tracked unless its paths are added explicitly.
