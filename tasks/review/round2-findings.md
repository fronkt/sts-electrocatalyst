# Round-2 verification findings (fix round), 2026-08-09

launchable lanes: NONE

## Still unfixed

### U1 — 1A-cellsym — [2] ionic-step counts assumed BELOW the measured 1x1 values (ruling: "Re-quote every row from the measured counts")

46 of 49 relaxations are re-quoted correctly, but the three `ref__2x1v` rows bypass `steps_2x1()` entirely and are hardcoded at 5 ionic steps with `measured_1x1_steps=None` -- below the measured 1x1 clean-slab relaxation of 16 (Cr) / 12 (Ir) / 12 (Ru). The fixer's proof sentence, "all 49 relaxations match ceil(n x 1.5) or n with 0 rows below their own measured count", is false: 3 rows have no measured count at all and sit 3.2-4.8x below the block's own rule. Because `max_seconds` is 2x the estimate, Cr `ref__2x1v` -- the GATE C job -- carries a 13.9 h cap against a job the block's own STEP_MULT would cost at 24 steps / 66.7 h. If it needs more than ~10 steps it stops on the cap, prints JOB DONE without `bfgs converged`, and GATE C stays PENDING until a human deletes the .out. (The new pre-flight makes that loud rather than silent, which bounds the damage to ~14 wasted box-hours plus an intervention.)

*Evidence:* Re-count of `Total force` blocks in the production outputs: Cr/Ir/Ru slab.out = 16/12/12. Audit of cellsym_manifest.json: `[('no-measured-basis','Cr','ref__2x1v',5), ('no-measured-basis','Ir','ref__2x1v',5), ('no-measured-basis','Ru','ref__2x1v',5)]`; all other 46 relaxations satisfy steps_est == ceil(measured x 1.5) or == measured, and every basis value reproduces my independent recount exactly (Cr *O/*OH/*OOH 12/44/82, Ir 34/30/60, Ru 27/33/68 -- the review's 82/44/68/60 reproduce). Manifest rows: Cr ref__2x1v steps=5 est=6.9 h cap=13.9 h basis_measured=None. src/dft/build_cellsym_pilot.py:787-800.

### U2 — 1A-cellsym — [3](b) Cr magnetic-basin control -- one fresh-density fixed-geometry SCF per Cr 2x1 relaxation, required to agree to <= 5 meV (docs/43 s2-A.3(b))

The decks are emitted and the emitter correctly refuses until every parent carries `bfgs converged` -- that half is real. But NOTHING evaluates the 5 meV agreement. `cmd_score` never opens a `__g1` output (grep for 'g1' inside cmd_score returns nothing), and `pairs` stamps a verdict of OK from the relaxation energies alone: `ok = _scoreable(mir, mir_calc) and _scoreable(off, "relax")`. docs/43 P12 defines the readout quantity as dE_sym = E(off-plane, GATE-1-passed) - E(mirror, GATE-1-passed); as coded, a Cr pair whose GATE-1 SCF disagrees by 200 meV is reported OK provided its magnetisation happens to match to 0.1 uB. The same is true of the registered spectator contingency (|dy| > 0.02 A after ref__2x1o converges): it is stored as JSON state with status OPEN, and no code measures it. The module's own comment at line 1046 says "A declared threshold that no code evaluates is the failure this whole fix round is about" -- and then leaves two of them unevaluated.

*Evidence:* grep 'g1' src/dft/build_cellsym_pilot.py -> only lines 992/1026/1434, all inside cmd_gate1 or the manifest text; none in cmd_score (lines 1075-1226). src/dft/build_cellsym_pilot.py:1126 is the OK path. grep 'spectator_contingency|0.02' -> only PREREG (157), a deck note (814) and manifest JSON fields (1412-1424); no measurement. Confirmed live: `--gate1` emits 14 decks from synthetic converged parents and refuses with "refusing to emit any GATE-1 deck; 1 of 14 ... s0_OOH__2x1o_off: no `bfgs converged` (JOB DONE present: True)" when one parent is mutated -- so (b)'s emission is fixed and only its scoring is missing.

### U3 — 1A-cellsym — [5] CELL_MULT -- "ADOPT, AND MEASURE IT ... Replace the assumption with the measurement before quoting a budget"

The quoting half is fully fixed (5.5 planning / 8.0 ceiling / 4.0 explicitly labelled the floor, and est_hours uses 5.5). The measurement half is not done: m_cellmult.txt holds 3 emitted-but-unrun SCFs and every hour in cellsym_manifest.json is still quoted from the assumption. The fix round's own standing instruction 3 forbade running it, so this is not the fixer's fault -- but the ruling's precondition ("before quoting a budget") is not met, nothing in the artifacts enforces that manifest C runs before A and B, and the JSON's own cost line is stale by 3x: `cost="3 SCFs x 1200 s at NP=20/NCONC=1, ~1 box-hour"` while CELLMULT_MAX_SECONDS = 3600 and the m_cellmult.txt header says "Budget it as <= 3 box-hours, expect ~1.5".

*Evidence:* cellsym_manifest.json pending_measurements[0].cost = '3 SCFs x 1200 s at NP=20/NCONC=1, ~1 box-hour'; src/dft/build_cellsym_pilot.py:590 CELLMULT_MAX_SECONDS = 3600; runs/probe/m_cellmult.txt header line 3 'Three fixed-geometry SCFs, max_seconds = 3600'. status field correctly reads 'PENDING -- decks emitted, not run'.

### U4 — 1A-cellsym — [3](a) Cr magnetic-basin control — mir/off pairs must agree to 0.1 mu_B or be CONFOUNDED (docs/43 s2-A.3(a))

cmd_score gates on TOTAL magnetisation only. It computes and stores d_absolute_magnetization and then never thresholds it (build_cellsym_pilot.py:1146). docs/43 s2-A.3 names the failure it is protecting against: "the 2x1 admits antiferromagnetic orderings along [001] the 1x1 cannot represent". An AFM rearrangement at fixed net moment has dM_total = 0 and a large dM_abs, so it passes. GATE C and GATE C-2 are worse — they compare total magnetisation only (line 1191) and do not even record absolute magnetisation on the gate row.

*Evidence:* Measured, not argued. I ran `--score` against synthetic pw.x outputs in scratch (manifest copied, real code, no repo file touched). Row returned: {'metal':'Cr','state':'s0_OOH','arm':'2x1v','dE_sym_eV':-0.3,'d_total_magnetization':0.0,'d_absolute_magnetization':2.0,'verdict':'OK'} — a 2.0 mu_B basin change carrying a -0.300 eV shift (the size of the whole Ir symmetry escape, -0.291 eV) is scored OK and enters the symmetry statistics. Control with dM_total = 0.30 correctly returns CONFOUNDED, so the code path works; it is pointed at the wrong quantity. Same run: GATE C-2 Cr returned PASS with dE_meV = 0.0 and a 4.0 mu_B absolute-magnetisation mismatch (10.0 vs 2x3.0).

### U5 — 1A-cellsym — [3](b) one fresh-density fixed-geometry SCF per Cr 2x1 relaxation, required to agree to <= 5 meV

`--gate1` emits the 14 decks and records the PARENT energy and magnetisation, but no code anywhere evaluates the 5 meV comparison. `cmd_score` never opens a `__g1.out` and never reads `cellsym_gate1_manifest.json`; `cellsym_readout.json` has no GATE-1 section. The registered threshold has an emitter and a recorder and no evaluator — which is verbatim the defect the fixer's own `--score` docstring says this fix round exists to remove.

*Evidence:* `grep -n "g1\|gate1" src/dft/build_cellsym_pilot.py` returns 14 hits, all inside cmd_gate1, the argparse block and the manifest text; none in cmd_score (lines 1075-1226). I drove cmd_gate1 to completion in scratch with 14 synthetic converged parents: it emitted 14 decks + m_cellsym_gate1.txt + cellsym_gate1_manifest.json, whose first row is {'job':'ref__2x1v__g1','parent_final_energy_ev':-16797.15,'parent_total_magnetization':6.0,...} — parent-side only, no child field, no tolerance test.

### U6 — 1A-cellsym — [6] one manifest at one NP; the critical path is a single job that renting boxes cannot shorten

Fixed for Cr, not for Ir/Ru. Manifest A's own longest job is 121.2 h at NP=4 (Ru s0_OOH__2x1v_off and 2x1o_off), and it is a single job at NP=4 with NCONC=5, so more boxes cannot shorten it either — the exact structure finding [6] blocked. The manifest A header asserts the opposite in words: "none of them is the critical path" (build_cellsym_pilot.py:1265, copied verbatim into m_cellsym_a_np4.txt). The fixer's report compounds it: "Manifest A packs to ~40 h on 8 boxes" divides 1589.2 h by 40 slots, but with 36 jobs and 40 slots every job starts at t=0 and the wall clock is the longest job, 121.2 h = 5.05 days — 3x the quoted figure.

*Evidence:* cellsym_manifest.json manifests.A = {n_jobs 36, np 4, nconc 5, sum_hours 1589.2, longest_job_hours 121.2}. Builder stdout table: `| 2x1v | Ru | *OOH | off | 39 | 4 4 1 | 4 | A | 4 | 102 | 121.2 | 872467 |`. 36 jobs <= 8 boxes x NCONC 5 = 40 concurrent slots, so wall = max = 121.2 h, not 1589.2/40 = 39.7 h.

### U7 — 1B-hpx — [12] builder re-registered the gate — the widening is gone, but a SECOND in-code copy of a registered threshold survives and contradicts docs/43

The adjudication's governing rule is "Replace every in-code rule with a POINTER to docs/43; delete the copies. Do not reconcile them." The external-window copy is genuinely gone. But C:\Users\frank\sts-electrocatalyst\src\dft\build_hp_validation.py:188 still states a registered threshold in code, at a DIFFERENT value from the pre-registration, and attributes it to docs/43: `#: TiO2 q-mesh ladder. Internal criterion I1 is |U(4x4x4) - U(3x3x3)| <= 0.10 eV`. docs/43 line 276 registers `q-mesh convergence | ΔU < 0.2 eV vs the next finer mesh`, and AMENDMENT 1 §4-A does not touch it. This is finding [12]'s exact failure mode — two mutually inconsistent registrations of the same gate, one of them sitting in a build artifact — surviving in a different clause of the same section. It is tightened rather than widened, so it is less damaging than the original, but a registered threshold is not moved in either direction without a stated reason, and a judge reading the code beside docs/43 finds the code claiming to quote a pre-registration that says something else. Related: the same file cites "docs/43's criterion I5" (line 613) and "internal criterion I2" (line 636); docs/43 defines no criteria named I1/I2/I2b/I5 anywhere — those labels come from the FIRST round's rejected in-code registration. Line 44 also copies the 0.05 eV figure, which at least matches docs/43 but contradicts the file's own stated policy at lines 32-36 ("The numbers are deliberately not repeated here").

*Evidence:* grep over the lane: `grep -n "0.10 eV|0.2 eV|1e-3" src/dft/build_hp_validation.py src/dft/queue_hp.sh runs/hp_costmodel/cost_model.json runs/hp_tio2/m_hp_tio2.txt runs/hp_costmodel/m_hp_costmodel.txt` returns exactly two hits, build_hp_validation.py:44 (0.05 eV, matches docs/43 §4-A.4) and build_hp_validation.py:188 (0.10 eV, contradicts docs/43 §4's 0.2 eV). `grep -n "I1\b|I2b|I5\b" docs/43-prereg-week1-factorial.md` returns zero criterion labels. The window fix itself checks out: `grep -c "3.0, 7.0\|2.0, 8.0"` = 0 in both build_hp_validation.py and cost_model.json, and `git diff HEAD -- docs/43-prereg-week1-factorial.md` is empty with the last touching commit still 0244f4e.

### U8 — 1B-hpx — [20] the run directories do not exist on the box — the adjudicated first half ("Upload and verify") has not been done

The adjudication reads "ADOPT. Upload and verify, plus a pre-flight in queue_hp.sh...". The pre-flight half is done and proven. The upload half is not: `/workspace/sts/runs` on box 47025043 still contains exactly one entry, `probe`, and `/workspace/queue_hp.sh` does not exist on the box. The block is therefore not launchable as it stands. This is not a defect in the code — the fixer flagged it explicitly under "What needs uploading" and the danger the finding described (a false-clean `QUEUE_HP_ALL_DONE` banner on a queue that ran nothing) is now impossible — but the finding is not closed until the rsync happens, and I am reporting state, not intent. The fixer's verification hash is correct: I reproduced `3287918bd6810c3044560d9c750a2bfa` over the 47 files (the fixer's figure is the GNU/Linux `md5sum` two-space format; Git Bash's binary-mode ` *` marker gives a different aggregate, which is why a naive re-check on Windows disagrees).

*Evidence:* `ssh -p 25042 root@ssh1.vast.ai 'ls /workspace/sts/runs'` → `probe`. `ls -la /workspace/queue_hp.sh` → no such file. Running the REAL manifest against the REAL runs dir reproduces the original finding and shows the pre-flight catching it: `RUNS=/workspace/sts/runs bash queue_hp.sh m_hp_tio2.txt 20 1 --preflight-only` → 23 × `PREFLIGHT line N: missing directory /workspace/sts/runs/hp_tio2`, then `PREFLIGHT_FAIL 23 problem(s); nothing launched`, rc=1 (and the same for m_hp_costmodel, 8 lines, rc=1). Local mirror check with the directories present: both real manifests return `PREFLIGHT_OK` at their documented settings — `m_hp_tio2.txt 20 1` → 23 lines / 3 distinct (dir,prefix); `m_hp_costmodel.txt 18 1` → 8 lines / 2 distinct. Hash: `md5sum runs/hp_tio2/* runs/hp_costmodel/* | sed 's/ \*/  /' | sort -k2 | md5sum` = 3287918bd6810c3044560d9c750a2bfa, 47 files, zero CR bytes in all 47.

### U9 — 1B-hpx — [12] delete the in-code copies of the registered gate; replace with a pointer to docs/43

The external window was correctly removed, but a *different* copy of a registered threshold survived in the same file and it contradicts docs/43 — tightened 2x, with no reason given, which is the exact defect [12] was about. Shipped artifacts also cite criterion labels ("I1", "I2", "I2b", "I5") that appear nowhere in the pre-registration; "criterion I5" is the stated justification for 3 new decks and 3 new manifest lines, and a judge going to docs/43 for it finds nothing.

*Evidence:* C:\Users\frank\sts-electrocatalyst\src\dft\build_hp_validation.py:188 — "Internal criterion I1 is |U(4x4x4) - U(3x3x3)| <= 0.10 eV". docs/43:276 registers "q-mesh convergence | ΔU < 0.2 eV vs the next finer mesh". `grep -nE '\bI[1-5]\b|n_pert|find_atpert' docs/43-prereg-week1-factorial.md` returns only two lines, both in §4-A, neither naming I1/I2/I2b/I5. The fixer's proof for [12] only grepped for `3.0, 7.0` / `2.0, 8.0`, so it could not have caught this.

### U10 — 1B-hpx — [11] take the slab timing at a general, non-Γ q

The sym arm's q#3 deck is correct and the fixer's deviation from the ruling (q#3 not q#2) is right — I re-derived the 3x2x1 sym q-list independently and q#2=(0,½,0) does keep the full 4-op small group, N_k=15, identical to Γ. But the fix was then applied mechanically to the nosym arm, where every q has N_k=36 and the model itself says the general-q deck differs from Γ by 3%. `crslab_nosym__hp_1atomq_q3` is therefore a ~10 wall-hour re-measurement of a point the manifest already measures. The guard written to stop exactly this class of mistake cannot fire (see new_problems).

*Evidence:* `B.q_table((3,2,1), (9,4,1), _SLAB_OPS_NOSYM)` -> every row n_k=36. cost_model.json slab row "nosym: as production runs today" reports gamma_understatement 1.03. m_hp_costmodel.txt header itself prints nosym_q1 [3.8, 9.5, 18.8] h and nosym_q3 [4.1, 9.9, 19.2] h.

### U11 — 1B-hpx — [17] gate on the artifact, not on a string the binary never prints

Per-rung the gate is genuinely fixed (pre-clean -> run -> rename -> grep the .dat), and the directory-wide `ls *.dat | wc -l` is gone. The batch-level signal is not fixed: hp.x writes `<prefix>.Hubbard_parameters.dat` even after "Convergence has not been reached" (the script's own header documents this for FeO2), so ARTIFACT=1 is reachable on a non-converged response — which is precisely the CrO2 arm's registered failure mode (docs/43 §4-A.3: "a finite U with ZERO 'Convergence has not been reached' lines"). The new terminal banner reports only U_DECKS/WITH_ARTIFACT and never NOTCONV, so a batch in which every U came from a stalled linear response prints a clean tail.

*Evidence:* queue_hp.sh:252 `[ "$hasu" -gt 0 ] && [ "$nu" -gt 0 ] && artifact=1` — NOTCONV is logged at :266 but never enters `artifact`, and the banner at :293 carries only `U_DECKS=$want WITH_ARTIFACT=$got`. Binary check on the box: `grep -ac 'Convergence has not been reached' /workspace/qe/env/bin/hp.x` = 1, so the string is real and reachable.

### U12 — 1C-hessian — [24] REFUTED made reachable ("both gate-clean REFUTED now reaches R3 TRIGGERED - the branch that could never fire")

REFUTED is reachable only below sigma_F ~ 4e-6 Ry/bohr, i.e. 2.5x BELOW the design noise sigma_F = 1.0e-5 that this same file says conv_thr = 1e-10 delivers. At the design noise the UNDERPOWERED verdict added for [31] outranks and shadows both REFUTED and AMBIGUOUS, so docs/43 §3's R3 branch still cannot fire. The fix for [31] silently un-did the fix for [24]. The fixer measured the i121 cm^-1 floor and reported it as the [31] fix working, but never connected it to [24] and never states that the pilot as designed cannot return its own falsifying answer.

*Evidence:* Driving hessian_analyze.score_state on the real Ir manifest with an all-real true spectrum (1200/500/250 cm^-1 y block), 60 seeds per noise level: sigma_F=3.5e-6 -> REFUTED 60/60; 4.0e-6 -> REFUTED 53/60, UNDERPOWERED 7/60; 5.0e-6 -> REFUTED 15/60; 1.0e-5 (DESIGN) -> REFUTED 0/60, UNDERPOWERED 60/60. A separate 400-seed sweep at design noise: 397 UNDERPOWERED, 3 VOID (Q5), 0 REFUTED, 0 AMBIGUOUS. An i300 cm^-1 in-plane imaginary mode at design noise also reports UNDERPOWERED, not AMBIGUOUS.

### U13 — 1C-hessian — [22]/[29] electron_maxstep 200 -> 120: "all 19 emitted decks carry electron_maxstep = 120; guard fires on 200."

There is no guard on 200. build_hessian_pilot.py:715 accepts 30 <= electron_maxstep <= 200 inclusive, and verify_emitted checks the emitted text against args.electron_maxstep rather than against 120, so the refusal message that names 200 can never fire. 120 is a default, not a guard.

*Evidence:* `PYTHONPATH=src python src/dft/build_hessian_pilot.py --electron-maxstep 200 --out <scratch>` exits 0 and writes 19 decks; `grep electron_maxstep <scratch>/Ir_hess/s0_OOH__hess_ref.in` -> `electron_maxstep = 200`.

### U14 — 1C-hessian — [22]/[29] "Cost, measured, replacing the extrapolation"

The measured Ir number is correct and well sourced, but build_hessian_pilot.py:771-772 prints it verbatim for ANY state, including Cr, with the words "on this exact deck". Cr is nspin=2, +U, 36 k-points; the file's own docstring (lines 217-220) says Cr has NOT been timed at these settings, is ~2.4x Ir per iteration, and must be timed before the arm is sized. So the builder's own printed budget contradicts its own docstring for the arm that is not measured.

*Evidence:* Building Cr with `--cell-verdict-1a "TEST STRING"` prints: "measured: 20.95 s per SCF iteration and 30 iterations at NP=20/-nk 4 on this exact deck, so 19 SCFs = 3.4 h wall at NCONC=1." Independent recompute using the file's own factors: 2.4x per iteration x (36/32) k-points x 30 iters x 19 jobs = 8.9-9.2 h, i.e. the printed number is low by ~2.6x. (The review's own basis, 332 s/iter Cr vs 124.5 s/iter Ir = 2.67x, gives 8.9 h.)

### U15 — 1C-hessian — [27] "the ym decks buy only an independent noise realisation ... Kept anyway, because docs/43 §3-A.8 registers the ±y central difference for its sqrt(2) gain."

There is no independent noise realisation and no sqrt(2) gain. The fixer's own byte check proves the ym deck is the EXACT mirror of the yp deck; two deterministic pw.x runs on mirror-related inputs produce mirror-related forces including their SCF convergence error, so F_y(-d) = -F_y(+d) and H[y_a,y_b] = -F_yb(+d)/d - algebraically identical to the one-sided difference. The variance is the same, not sqrt(2) smaller. AXES_PURPOSE and the builder docstring restate the sqrt(2) claim as fact. (docs/43 §3-A.8 also states it; that is a pre-registration defect I cannot ask you to edit, but the code should not repeat it as measured.)

*Evidence:* Independent permutation- and periodicity-aware check on the emitted decks: mirroring each s0_OOH__hess_a{19,20,21}yp.in by y -> 2*4.77084945 - y (mod b = 6.36113260) and matching to the ym deck gives max atom mismatch 8.88e-16 A on all three pairs, slab included. 2*y_cus = 1.5*b exactly, so the mirror also maps the FFT grid onto itself.

## Newly introduced by the fix

### N1 — 1A-cellsym — src/dft/build_cellsym_pilot.py:147

The PREREG dict is advertised as a pointer, but 6 of its 11 anchors are phrases that stop just short of the number they pin, so `_prereg_check()` detects a deleted clause and NOT a changed threshold. The docstring's claim -- "the anchor is here so the number cannot silently drift away from the clause it claims to implement" -- is false for monatomic_offplane_min_dy_A (0.30), spectator_contingency_dy_A (0.02), cr_pair_magnetisation_tol_bohrmag (0.1), cr_gate1_scf_tol_meV (5.0), gate_c_energy_tol_meV (5.0), production_cell_decision_eV (0.10) and sign_rule_max_positive_dE_sym_eV (0.02). Only `states`, `cr_2x1_kmesh` and `gate_c_magnetisation_tol_bohrmag` embed their value in the anchor.

*Why it ruins the result:* The governing rule of this fix round is that in-code rules become pointers so a rule cannot be read in whichever version suits the result. A value copy that survives a change to docs/43 is exactly that second version. Today all 11 values match docs/43 verbatim (I checked every one against the text), so nothing is currently wrong -- but the mechanism that is supposed to keep it that way does not work, and the file states that it does.

*Fix:* Extend each anchor string through the number it pins, e.g. anchor "members of each Cr pair must agree to within **0.1" instead of "...agree to within", and "a y-translation of ≥ 0.30" instead of "y-translation of". Two entries already do this; make the other six match. DEMONSTRATED: I copied docs/43 to scratch, changed five registered thresholds (pair tol 0.1->0.5 uB, min dy 0.30->0.60 A, GATE-1 5->1 meV, production-cell 0.10->0.25 eV, sign rule 0.02->0.10 eV) and the builder produced all 56 decks with rc=0 and no warning -- decks whose 0.35 A kick would then violate the pre-registration it claims to implement.

### N2 — 1A-cellsym — src/dft/build_cellsym_pilot.py:1457

The new `--score` readout certifies docs/43 §2's registered replication gate (Ir *OOH 1x1 off-plane must reproduce dE_sym = -0.291 +/- 0.05 eV) using the very run the gate exists to replicate: ALREADY_ON_DISK (line 223) redirects the Ir and Ru 1x1 off-plane arms to runs/probe/{Ir,Ru}_orient/s0_OOH__yaw90.out, so cmd_score subtracts the original P10 pair and returns -0.291323 by construction. The manifest records this as `validated`.

*Why it ruins the result:* The gate cannot fail. docs/43 §2 calls it "a pipeline control" whose miss "voids the block and the pipeline is debugged before anything else is read" -- a control that re-reads its own answer controls nothing, and the adjudication applied exactly this standard to block 1B finding [13] ("A hard gate that cannot fail is not a gate"). The reuse pre-dates this fix round, but the new readout is what turns it into a recorded PASS.

*Fix:* Either rebuild and re-run Ir `s0_OOH__1x1_off` through the current emitter (~10.3 h at NP=4 by the module's own figure, against a 1589 h manifest A) and score the gate against that, or state in cellsym_manifest.json that the replication gate is satisfied by reuse and is therefore not an independent control. Do not report it as `validated`.

### N3 — 1A-cellsym — src/dft/build_cellsym_pilot.py:996

cmd_gate1 sets `d["nosym"] = j["sym"] == "off"`, but the build path sets nosym for sym in ("off","off_fixed","none") (line 692). `ref__2x1v` is emitted with sym="none", so the parent relaxation runs nosym=.true./noinv=.true. at 16 k-points while its GATE-1 child runs with symmetry ON at 9. The guard does not catch it: it is called with sym="mir_fixed" for anything that is not "off", and mir_fixed only asserts that nosym is ABSENT.

*Why it ruins the result:* GATE-1's single job is to certify that a relaxation's energy is reproducible from a fresh density AT THE SAME SETTINGS to 5 meV. For the 2x1v reference — the denominator of every 2x1v adsorption energy and the subject of GATE C — the check now moves the symmetry treatment and the k-set at the same time. A >5 meV disagreement cannot be attributed, and a <5 meV agreement certifies nothing.

*Fix:* Mirror the build path exactly: `d["nosym"] = j["sym"] in ("off","none")`, and pass sym="off_fixed" for the "none" parent so the guard re-checks nosym+noinv on the emitted bytes.

### N4 — 1A-cellsym — src/dft/queue_r1.sh:93

The stale test is calculation-aware, but when the `calculation` value fails the `'[a-z-]+'` single-quoted regex at line 90 the empty `calc` falls into the `*)` branch, which only needs a `!    total energy` line. A relax .out contains that at every ionic step, so a truncated relaxation is classified as complete. The default branch of the gate is the permissive one.

*Why it ruins the result:* Measured on the box: a deck written `calculation = "relax"` with a .out containing `Maximum CPU time exceeded`, `!    total energy`, `JOB DONE` and NO `bfgs converged` returned `already_done=1 stale=0 bad=0`, rc=0 — the pre-flight waves it through and run_one SKIPs it forever. The single-quoted control on the identical .out returned PREFLIGHT_STALE, rc=3. This is the finding-[8] failure surviving inside the gate built to stop it. The 56 decks in this lane all use single quotes so it does not fire today; the fallback direction is wrong for the next deck family.

*Fix:* Make the unknown-calculation branch the STRICT one (require `bfgs converged` unless calc is positively identified as a single-point), and abort with PREFLIGHT_BAD if the calculation keyword cannot be extracted at all.

### N5 — 1A-cellsym — src/dft/queue_r1.sh:61

The pre-flight validates NP % nk, dir, input, CR bytes, malformed lines and stale .out, but not three things it already has in hand: (a) nk <= the k-points pw.x will have; (b) duplicate (dir, job) lines; (c) NP x NCONC against /sys/fs/cgroup/cpu.max, which run_one already cats into the QUEUE_START line.

*Why it ruins the result:* Measured on the box, all three returned PREFLIGHT_OK rc=0: `nk=8` on a 9-k-point deck at NP=8 (pw.x aborts at runtime after the pre-flight has declared the wave safe); the same `probe/T j1` line twice at NCONC=2 (two mpirun ranks writing the same j1.run.in and j1.out in the same cwd, and the first to finish `rm -rf`s the other's outdir mid-run); and NP=48 x NCONC=2 = 96 ranks on 23.04 usable cores, the docs/23 s8 12x-thrash configuration.

*Fix:* Add the three checks to preflight(). (c) is two lines against cpu.max and is the one with a measured 12x cost in this project's history.

### N6 — 1A-cellsym — src/dft/queue_r1.sh:89

`max_seconds` is now baked into every deck at 2x the estimate AT THE NP OF ITS MANIFEST, but NP is a runtime argument and nothing binds a manifest to it. Running manifest B at NP=4 passes pre-flight cleanly.

*Why it ruins the result:* Measured: `PREFLIGHT_ONLY=1 bash q.sh /workspace/m_cellsym_b_cr_np20.txt 4 5` returns `lines=17 to_run=17 bad=0 stale=0`, rc=0. Those decks carry caps computed at NP=20 (e.g. 1,227,442 s for s0_OOH__2x1v_off against a 511 h NP=4 estimate); at NP=4 the cap fires at ~67% of the work and pw.x exits with JOB DONE and no `bfgs converged`. Before this round the wrong NP only made a job slow; now it silently truncates it after ~14 days of box time. Same hazard in the other direction: the caps are a function of CELL_MULT and MAG_MULT, which cellsym_manifest.json itself marks PENDING — settling them rebuilds all 56 decks with new bytes, so manifest C must be run and the constants settled BEFORE anything is launched or the whole tree has to be re-uploaded mid-wave.

*Fix:* Put the intended NP/NCONC in the manifest as a `# NP=20 NCONC=1` directive and have the pre-flight refuse when the command line disagrees; or emit max_seconds as a wall-clock budget independent of NP.

### N7 — 1A-cellsym — src/dft/build_cellsym_pilot.py:590

The m_cellmult binding leg is designed to hit its cap without converging (CELLMULT_MAX_SECONDS = 3600 buys 10-14 iterations against the 26 the Cr 1x1 needed; the builder's own table costs that leg at 1.6 h = 5760 s). An SCF stopped that way prints no `!    total energy`, so the new pre-flight classifies the deck that did exactly its job as stale.

*Why it ruins the result:* Measured on the box with a synthetic capped .out for s0_OH__2x1o_mir__cellmult: `PREFLIGHT_STALE ... calc=scf JOB_DONE-without-a-defensible-result ... delete <out> and requeue from its own \`Begin final coordinates\`` and rc=3 for the whole manifest. An SCF has no `Begin final coordinates`, and the .out IS the measurement — the `total cpu time spent up to now` increments the entire cost model is pending on. The instruction printed by the abort destroys the artifact. Separately, the queue's own DONE line for that leg will read rc=0 JOB_DONE=1 SCF_FAIL=0 F_LAST=na, indistinguishable from success (hard rule 3).

*Fix:* Mark manifest C's legs as expected-to-cap (an `# EXPECT_CAP` directive the pre-flight honours), and change the stale message so it never tells an operator to delete an .out that is itself the deliverable.

### N8 — 1A-cellsym — runs/probe/cellsym_manifest.json:1394

pending_measurements[0].cost still reads "3 SCFs x 1200 s at NP=20/NCONC=1, ~1 box-hour" while CELLMULT_MAX_SECONDS is 3600 and the m_cellmult.txt header says "Budget it as <= 3 box-hours, expect ~1.5". The machine-readable field was not updated when the cap was tripled.

*Why it ruins the result:* cellsym_manifest.json is the artifact a later reader trusts over a comment in a text file. A 3x-low cost on the one wave the whole cost model is blocked on is the project's standing failure mode (hard rule 6) in the exact field created to record it.

*Fix:* Interpolate CELLMULT_MAX_SECONDS into the string instead of hard-coding 1200.

### N9 — 1A-cellsym — src/dft/build_cellsym_pilot.py:749

`steps_2x1` is presented as a guard ("refusing to build: ... below the measured 1x1 count") but with STEP_MULT_2X1 = 1.5 it is `ceil(n*1.5) < n`, which is false for every n >= 1. It cannot fire in production; it only fires if someone edits the constant, which is what the fixer's mutation test did. Relatedly, est_bracket_np4 varies MAG_MULT and CELL_MULT but holds STEP_MULT_2X1 fixed at 1.5 at BOTH ends, so the published "1815-6702 single-job hours" bracket does not bracket the step count at all.

*Why it ruins the result:* Finding [13] in the sibling lane is exactly this: a gate that cannot fail is not a gate. And the unbracketed quantity is the one finding [2] was about. Cr s0_O 2x1 is costed at 18 ionic steps (ceil(12 x 1.5)) for a 37-38 atom cell spliced from an *O-covered half and a clean half — the Cr 1x1 CLEAN slab alone took 16 steps from a much better start. At STEP_MULT 2.0 the ceiling goes from 6702 to ~8900 NP=4 job-hours.

*Fix:* Either drop the pretence that it is a gate (call it an assertion on the constant), or make it a real one — e.g. refuse if STEP_MULT_2X1 < 1.0 at import time — and put STEP_MULT into est_bracket_np4 so the published bracket is a bracket.

### N10 — 1A-cellsym — src/dft/build_cellsym_pilot.py:1173

For Cr only, GATE C and the new GATE C-2 compare a RELAXED 2x1 energy against a FIXED-GEOMETRY 1x1 baseline. `ref__2x1v` and `s0_O__2x1o_mir` are relaxations at 4 4 1; their Cr baselines are `slab__1x1_k8` and `s0_O__1x1_k8`, single-point SCFs at 8 4 1 evaluated at geometries relaxed at 9 4 1. The builder's own note on ref__2x1v concedes the point: "For Cr the mesh also changes (9 4 1 does not fold), so it is not exactly stationary." Ir and Ru are clean (both sides relaxed, mesh folds exactly).

*Why it ruins the result:* Any relaxation energy released by the 9->8 mesh change appears as a systematic negative dE and is read as a GATE C / GATE C-2 failure, with nothing in cellsym_readout.json distinguishing "the cell construction is wrong" from "the 1x1 geometry was not stationary at the folded mesh". GATE C-2 is worse than GATE C because it is a 38-atom adsorbate cell with far more soft modes than a clean slab, and GATE C-2 is new this round — the *O addition's own control is the one most likely to fail for a reason that is not the failure it tests for.

*Fix:* For Cr, either relax the 1x1 baselines at 8 4 1 (three more cheap 1x1 relaxations) or make ref__2x1v / s0_O__2x1o_mir fixed-geometry SCFs so both sides of the gate are at the same protocol; and record the gate's failure reason as MESH_RELAXATION vs CELL_MISMATCH rather than a bare FAIL.

### N11 — 1A-cellsym — runs/probe/Cr_cellsym/s0_O__1x1_off.in:1

The new Cr 1x1 *O pair (added to close finding [1]) compares a production mirror row that ran with plain mixing against an off row that carries `mixing_mode = 'local-TF'`. runs/Cr_slab/{s0_O,s0_OH,s0_OOH}.in carry no mixing_mode; write_probe hardcodes local-TF; the difference is whitelisted in _ALLOWED_DIFFS. It is declared in the docstring, but for *O and *OH it is now a second variable inside a scored pair. (Cr *OOH is clean — runs/probe/Cr_basin/s0_OOH.in already uses local-TF. Ir/Ru anchors already use local-TF.)

*Why it ruins the result:* Mixing mode does not move a converged energy but it does select which SCF solution you converge to, which is precisely docs/41 s6f's finding and the reason Cr is on this list at all. The only guard against it is the CONFOUNDED test — which, per the first unfixed item above, is blind to a fixed-net-moment basin change. The two defects compound on exactly the metal and exactly the pair that matter.

*Fix:* Either re-run the Cr 1x1 *O and *OH mirror rows through the same emitter (two cheap 1x1 relaxations), or, at minimum, gate the pair on absolute magnetisation so the mixing-induced basin change cannot pass silently.

### N12 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\runs\hp_costmodel\cost_model.json:726

The CrO2-arm cost note says "The measured-anchored model says 20-50 min at NP=20 including its SCF", but the row's own bracket is core_h_floor 4.7 / plan 10.5 / ceiling 19.9, which at NP=20 is 14 / 32 / 60 min. Neither 20 nor 50 is an endpoint of anything the model computes; only the plan figure (wall_min_at_np20 = 32.0) is derived.

*Why it ruins the result:* This is the one lane whose deliverable is an honest cost, written to correct a project whose estimates come in low every time (hard rule 6). The prose under-quotes the model's own ceiling by 17%, and it is the sentence a reader will quote because it is the one written in English rather than JSON.

*Fix:* Quote the row: "14 / 32 / 60 min at NP=20 (floor / plan / ceiling), including its SCF", or delete the prose range and point at wall_min_at_np20.

### N13 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\runs\hp_costmodel\m_hp_costmodel.txt:11

The header says "Launch the sym arm first and read its wall clock before paying for nosym", but the RUN AS line four rows below is `bash queue_hp.sh m_hp_costmodel.txt 18 1`, which runs all 8 lines — both nosym timing decks included — in one command. By the manifest's own projections that is 4.0 + 7.4 + 9.5 + 9.9 = ~31 plan wall-hours plus two production SCFs, and queue_hp.sh emits no max_seconds and has no stopping point between the arms.

*Why it ruins the result:* An operator following the only executable instruction in the file commits the nosym arm before the sym number exists, which is the precise decision the header exists to prevent. The adjudication for [19] did specify that command, so this is not a rule violation — but the file now argues with itself, and the expensive reading is the one that is copy-pasteable.

*Fix:* Split into m_hp_costmodel_sym.txt and m_hp_costmodel_nosym.txt with two RUN AS lines, or comment out the two nosym timing lines and say in the header that they are uncommented after the sym wall clock is read.

### N14 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\queue_hp.sh:291

The end-of-run banner counts are greps over the whole persistent log, not over this batch: `want=$(grep -ac 'HP_DONE .* EXPECT=U ' "$LOG")`. $LOG defaults to /workspace/queue_hp.log and is shared by every manifest. Running m_hp_tio2 (13 U-producing decks) and then m_hp_costmodel (zero U-producing decks) makes the costmodel batch report U_DECKS=13 WITH_ARTIFACT=n inherited from the TiO2 run.

*Why it ruins the result:* This is a weaker instance of the defect [17] was raised about — a count taken over a scope wider than the job, so a batch's summary line describes something other than that batch. The per-job gate, which is what [17] actually attacked, is now correct, and the banner is labelled "(log-wide counts)", so this is disclosure-grade rather than fatal. /workspace/queue_hp.log does not yet exist, so the first batch will be clean and the second will not.

*Fix:* Capture `wc -l < "$LOG"` before the driver loop and tail from there, or write each batch's HP_DONE lines to a per-manifest log and count that.

### N15 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\queue_hp.sh:245

`NU=` is presented as a count of Hubbard U values but the awk counts every line whose last field is a decimal number from the `Hubbard U parameters:` marker to end of file. A real 2-Ti .dat gives NU=12: 2 U rows plus the 2-row chi0, chi, chi0^{-1}, chi^{-1} and Hubbard matrices that follow in the same file.

*Why it ruins the result:* Only used as `nu > 0` for the artifact gate, so the gate is correct, and `uval` still picks the first U row correctly (measured 4.8434, matching the .dat). But a log field that reads as "12 Hubbard U values were produced for a 2-atom cell" is the kind of number that gets copied into a table later.

*Fix:* Stop the awk at the first blank line after the U table, or rename the field to NUMLINES.

### N16 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\runs\hp_costmodel\m_hp_costmodel.txt:33

`crslab_nosym__hp_1atomq_q3` is projected at 9.9 plan wall-hours, but the model's own q_table gives it N_k = 36 — identical to nosym Γ — and the corresponding table row reports gamma_understatement = 1.03. It is ~10 wall-hours to measure a point the model already says differs from the Γ deck by 3%.

*Why it ruins the result:* It is not wrong (with nosym there is no symmetry left to lose, so all q genuinely cost the same up to the k+q doubling in the NSCF), and it does test the n_LR assumption a second time. But it is the single most expensive line in the manifest and the header sells it as the general-q measurement, which for the nosym arm it structurally cannot be.

*Fix:* State in the header that nosym_q3 is an n_LR replicate, not a symmetry probe, and that the sym pair (q1 vs q3, N_k 15 vs 27) is the only arm where the Γ-understatement is measurable — or drop it and spend the 10 hours on the sym arm.

### N17 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\build_hp_validation.py:356

`_validate_symmetry_model`'s docstring says "Twenty-two integers, every one of them printed by QE on this box". The function returns 26 (7 rutile nq + 5 slab sym nq + 3 slab nosym nq + 10 printed-k + 1 slab printed-k), and the module docstring, cost_model.json and the terminal banner all say 26.

*Why it ruins the result:* Cosmetic, but it is a count in a docstring whose entire purpose is to certify a count, in a file that just spent a review round on numbers that did not match their stated source.

*Fix:* Change to twenty-six, or derive the word from the same sum the function returns.

### N18 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\queue_hp.sh:212

`flock -x 9` has no failure check and the script does not `set -e`. If flock were absent the shell prints `command not found` to stderr (which is not captured in $LOG) and the rung proceeds completely unserialised — the exact state findings [9]/[18] describe, with no trace in the log.

*Why it ruins the result:* Latent only: I confirmed `/usr/bin/flock` (util-linux 2.39.3) and bash 5.2.21 on box 47025043, so the serialisation is real today. It matters if the container image is ever rebuilt.

*Fix:* `flock -x 9 || { echo "HP_ABORT $d/$hp reason=no_flock" >> "$LOG"; exit 4; }`.

### N19 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\build_hp_validation.py:1154

The nspin=2 cost factor is counted twice in every slab row. `cell_factor` (line 1139, and the identical derivation at 1022-1025) is (slab core-s per SCF iteration per k) / (TiO2 core-s per SCF iteration per k) = 82.67/0.36 = 229.6. The numerator comes from runs/Cr_slab/slab.out, which is an nspin=2 run (slab.in: `nspin = 2`, `nosym`, k 9 4 1, printed 36 k = per-spin); the denominator is TiO2 at nspin=1. So cell_factor already contains the ~2x spin cost. `_atomq_core_s(..., SPIN_UPLIFT[k], cell_factor)` then multiplies by SPIN_UPLIFT (1.6/2.0/2.5) a second time.

*Why it ruins the result:* Block 1B's deliverable is the cost model, and every number block 3Y's go/no-go rests on is ~2x too high: sym 3x2x1 2473 core-h (4.5 box-days) is really ~1237 (2.2 days), nosym 6361 -> ~3181, the 'cheapest defensible variant' 291 -> ~146, and the m_hp_costmodel.txt header's 4.0/7.4/9.5/9.9 plan wall-hours are really ~2.0/3.7/4.8/5.0. A factor-2 error in the direction of 'unaffordable' can kill a block that is affordable. Note the bulk CrO2 and 2C rows are NOT affected — they run with cell_factor=1.0, so the error is confined to exactly the rows the review said were load-bearing.

*Fix:* Divide cell_factor by the spin factor it already contains, or (cleaner) derive cell_factor from an nspin=1 slab reference, or drop SPIN_UPLIFT from the slab rows only and say so. Whichever is chosen, add an assertion that no cost term multiplies two factors derived from the same measurement pair.

### N20 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\build_hp_validation.py:860

The guard added to protect the [11] fix cannot fail. `if qi == 3 and row['gamma']: raise SystemExit('the general-q slab timing deck landed on Gamma')` — `row['gamma']` is `qidx == (0,0,0)`, and `_mesh_orbits` iterates i,j,k from 0 so (0,0,0) is always orbit #1. I enumerated every mesh up to 5x5x3 against all three op sets: there is no mesh in which Γ is not the first orbit, so `qrows[2]['gamma']` is False by construction.

*Why it ruins the result:* This is finding [13]'s pathology — a hard gate that cannot fail — recommitted inside the code written to fix finding [11], in the same round. It also failed to catch the live case it should have caught: on the nosym arm q#3 is not Γ but has the identical N_k (36) and therefore the identical LR cost, so the deck it guards buys 3%.

*Fix:* Guard on cost-equivalence, not on the Γ label: `if row['n_k'] <= qrows[0]['n_k']: raise` (this fires on the nosym arm today, and would have fired on the review's proposed q#2 for the sym arm).

### N21 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\queue_hp.sh:291

The new terminal banner counts log-wide over an append-only log. `want=$(grep -ac 'HP_DONE .* EXPECT=U ' "$LOG")` / `got=$(grep -ac 'HP_DONE .* EXPECT=U ARTIFACT=1 ' "$LOG")` scan the whole of /workspace/queue_hp.log, which accumulates across both manifests and across every re-run.

*Why it ruins the result:* It is the directory-wide `ls *.dat | wc -l` of finding [17] in log form. Demonstrated: a log holding two successful rungs followed by a re-run in which all four decks produced nothing prints `QUEUE_HP_ALL_DONE U_DECKS=4 WITH_ARTIFACT=2` — the terminal line of the log claims half the batch succeeded when none of it did. The '(log-wide counts)' annotation is honest but the number is still the last thing an operator reads.

*Fix:* Accumulate per-run counters in the driver loop (or record the log byte offset at QUEUE_HP_START and `tail -c +$off` before grepping), and add NOTCONV to the banner.

### N22 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\queue_hp.sh:224

Nothing in this lane bounds a wall clock. No deck sets `max_seconds` (0 of 44 .in files), the slab and CrO2 SCFs carry the inherited `electron_maxstep = 200` at `conv_thr = 1.0d-10`, no deck sets `niter_max` so hp.x uses its default of 100 linear-response iterations, and the queue wraps mpirun with no timeout.

*Why it ruins the result:* The cost model's plan assumes n_LR = 25 on a magnetic metal and calls 40 the ceiling; the binary's ceiling is 100. Recomputed with the same model, a single `crslab_nosym__hp_1atomq_q3` rung at n_LR=100 is 674 core-h = 37.5 wall-hours at NP=18 (18.7 h after the spin correction above), against the 9.9 h the manifest header advertises. Separately, two 18-atom magnetic-metal SCFs at 1e-10 that stall burn 200 x 165 s = 9.2 wall-hours each before HP_ABORT. Adjudication [8] ('emit max_seconds at ~2x the corrected estimate') and [22] ('electron_maxstep ~ 120 so a stall costs 11 h not 18.4 h') are the same hazard, adjudicated in other lanes and not applied here.

*Fix:* Emit `max_seconds` in both slab SCFs and the CrO2 SCF at ~2x the modelled cost, drop electron_maxstep to ~120, and pass `niter_max` explicitly (the builder's `hp_namelist` already accepts it and never uses it) so the manifest header's quoted hours are an actual bound.

### N23 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\queue_hp.sh:175

`scf_once` decides to skip on a string in `${scf}.out` alone: `grep -aq "convergence has been achieved"`. It never checks that `<outdir>/<prefix>.save` still exists — and the script's own footer (line 299) instructs the operator to `rm -rf $RUNS/*/tmp_* $RUNS/*/.hp_*.lock` when the batch is scored.

*Why it ruins the result:* Follow the file's own cleanup instruction and then re-run one rung: every line logs SCF_SKIP and then hp.x dies because there is no charge density, 23 times. It is gating on a string in a file written by a previous process — the failure mode this whole script exists to prevent, one function above the one that fixes it.

*Fix:* Require both: the converged string AND `[ -s "${outdir}/${prefix}.save/charge-density.dat" ]` (or the .xml), else re-run the SCF.

### N24 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\runs\hp_tio2\scf__cro2.in

The CrO2 arm's magnetism is asserted on the input side (five build-time guards on `nspin = 2`, `starting_magnetization(1) = 0.6`, smearing) and captured nowhere on the output side. `scf_once` logs only rc/CONV/SCF_FAIL/seconds — no total magnetisation, no absolute magnetisation, no Fermi level, no gap.

*Why it ruins the result:* docs/43 §4-A.3 buys this arm to exercise the magnetic, metallic branch. If the SCF converges to a low-moment or nonmagnetic solution the arm silently becomes a second closed-shell run and a GO would license block 2C on evidence it does not have — while the log looks identical. Block 1A's adjudication [3] established exactly this rule ('record total and absolute magnetisation for every Cr job'). I ran the deck on the box for 45 s and it is in fact magnetic (total 4.00 μB/cell = 2 μB/Cr, absolute 5.08 and falling, 16 Sym. Ops., 50 k, U(Cr-3d) printed, Cr UPF found) — but nothing in the shipped pipeline would have told anyone that.

*Fix:* Add to scf_once's log line: `MAG=$(grep -a 'total magnetization' "${scf}.out" | tail -1 | awk '{print $4}')` and the absolute equivalent, and make the CrO2 arm's pass condition include a non-zero moment.

### N25 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\runs\hp_costmodel\m_hp_costmodel.txt

Eight decks on disk are unreachable from any manifest, and the two arms are no longer measured symmetrically. The costmodel manifest lines are hardcoded string literals in main() (build_hp_validation.py:1332-1339) rather than generated from `cost_files`, so the deck list and the manifest can drift silently. Orphans: hp_costmodel/crslab_{sym,nosym}__hp_qmesh_q421.in, _q941.in, crslab_sym__hp_qmesh_q111.in, crslab_nosym__hp_qmesh_q321.in, and hp_tio2/hp_1atomq__atomic{,_q2}.in.

*Why it ruins the result:* `crslab_sym__hp_qmesh_q321` IS in the manifest and `crslab_nosym__hp_qmesh_q321` is not, so the production-cutoff q-count is re-verified for one arm of a two-arm comparison whose entire purpose is 'measure what symmetry buys' rather than assume it. These are ~3 s counting decks that already exist on disk; there is no cost argument for omitting them. Counts do reconcile otherwise: 29 + 18 = 47 files, 23 + 8 = 31 manifest lines, 26 + 16 = 42 decks, 8 orphans.

*Fix:* Generate both manifests from the written-file list (as the TiO2 one already is), and add the four missing q-mesh counting lines.

### N26 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\runs\hp_tio2\m_hp_tio2.txt:5

The TiO2 manifest header quotes no cost at all. Its only cost statement is 'Counting decks (hp_npert/hp_npert3/hp_qmesh) exit in ~3 s', while the costmodel manifest header now carries per-deck wall hours. Recomputing independently from the shipped model: batch 76.4 core-h + CrO2 arm 10.5 + the q3 timing rung 0.55 + 13 counting decks at NP=20 ~0.22 = ~87.7 core-h plan, ~113 core-h ceiling — 4.4 to 5.7 wall-hours at NP=20, not counting the unbounded-stall exposure above.

*Why it ruins the result:* An operator told 'RUN AS: bash queue_hp.sh m_hp_tio2.txt 20 1' with '~3 s' as the only number in the header launches a job that owns the box for most of a working day. This lane's own header text for the other manifest gives the reason: 'an operator who launches the manifest expecting everything else exits in seconds finds that out eight hours in.'

*Fix:* Print the same floor/plan/ceiling block in the TiO2 manifest header, and state the manifest total, not just the batch subtotal (the fixer's report quotes 76.4 core-h, which is the batch row and excludes the CrO2 arm, the timing rung and the counting decks).

### N27 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\runs\hp_costmodel\crslab_sym__hp_1atomq_q3.in:7

`perturb_only_atom(1) = .true.` perturbs the bottom-layer Cr at z = 9.378 Å, which carries if_pos flags `0 0 0` — the frozen, bulk-like side of the slab. The surface Cr are atoms 5 and 6 (z = 15.605 and 15.882). The cost table's recommended cheapest variant is explicitly 'perturb only the surface pair'.

*Why it ruins the result:* The single measurement the file calls 'the ONE measurement block 3Y must not be committed without' is taken on a different atom than the one the recommended production variant perturbs. N_k is unaffected — I checked the site stabiliser and every Cr is fixed by all four ops of the Pmm2 group (m_x about x=0, m_y and C2 about y=b/4), so the k-reduction is identical — but n_LR is not, and n_LR is the model's own declared largest unknown. A surface Cr's linear response converges more slowly than a coordinatively saturated bulk-like one, so the timing is biased low in exactly the variable the deck exists to pin down.

*Fix:* Emit the general-q timing deck with `perturb_only_atom(5)`, or ship both — the marginal cost is one more LR solve and it converts the model's dominant assumption into a measured surface/subsurface ratio.

### N28 — 1B-hpx — C:\Users\frank\sts-electrocatalyst\src\dft\build_hp_validation.py:396

`CHI_SYMMETRY_IS_AN_IDENTITY['evidence']` cites 'QE 7.5 HP/src/hp_postproc.f90, SUBROUTINE reconstruct_full_chi ... an unconditional chi_(na,nb) = 0.5*(chi_(na,nb)+chi_(nb,na)) loop'. There is no QE source tree on box 47025043: `/workspace/qe` contains only `env`, and `find / -name hp_postproc.f90` returns nothing. The binary does contain the compiled-in symbols `reconstruct_full_chi` (2 hits) and `hp_postproc` (3), which confirms the routines exist but says nothing about what the loop does.

*Why it ruins the result:* docs/43 §4-A.4 registers the demotion as conditional: 'Whether the printed χ is pre- or post-symmetrisation is settled by reading one completed iverbosity = 2 run', and 'Keep docs/43's 0.05 relative tolerance if the printed χ turns out to be pre-symmetrisation'. The conditional has been resolved to a hardcoded constant in a shipped build artifact on evidence that is not reproducible on the machine the campaign runs on, before the registered measurement was made. For an entry whose top disqualification risk is citation integrity, that is the wrong shape of provenance.

*Fix:* Either restate the evidence as an upstream source citation with a version and line reference that a reader can check, or leave the constant marked PENDING and resolve it from the first find_atpert=4 rung's preserved .chi.dat — which the queue now keeps, so the measurement is available for the price of reading it.

### N29 — 1C-hessian — C:\Users\frank\sts-electrocatalyst\src\dft\build_hessian_pilot.py:715

The fixer's report claims "guard fires on 200" for electron_maxstep. It does not. The CLI check is `if not (30 <= args.electron_maxstep <= 200)`, so 200 is INSIDE the accepted band. Measured: `--electron-maxstep 200` exits 0 and writes 19 decks each carrying `electron_maxstep = 200`, with the manifest recording 200. verify_emitted only checks the emitted deck against whatever the operator asked for, so it cannot catch this either.

*Why it ruins the result:* Finding [22]'s substance IS fixed (the default is 120 and all 19 shipped decks carry 120, byte-verified), so nothing launchable is wrong today. But the stated verification is false, and the CLI's upper bound is exactly the inherited value Trap 1 exists to cut. An operator who reads the report will believe a regression to 200 is impossible when a single flag does it silently.

*Fix:* Either lower the accepted band to e.g. 30..150, or delete the claim. If 200 is to stay reachable it should require an explicit escape flag, not the ordinary --electron-maxstep.

### N30 — 1C-hessian — C:\Users\frank\sts-electrocatalyst\src\dft\build_hessian_pilot.py:727

The Cr hold's release predicate is unchecked free text. Demonstrated: `--states Cr --cell-verdict-1a "2x1-vacant REQUIRED; the 1x1 cell is INADMISSIBLE"` builds 19 decks from runs/probe/Cr_basin (the 1x1 geometry), stamps `cell_label = "1x1"`, `verdict_scope = "q = 0, 1x1 cell, 1 ML"`, and records that verbatim string in the manifest as the authorisation. VERDICT_SCOPE and cell_label are module constants, not derived from the source cell.

*Why it ruins the result:* docs/43 §3-A.7 does not just say "hold Cr", it says "held until block 1A returns its cell verdict, THEN RUN IT IN THE CHOSEN PRODUCTION CELL." As built, the flag records a verdict without ever testing that the cell being Hessian'd is the one the verdict chose — so the single most likely way for the 1.338 A coverage artifact to reach the report is to pass the flag after 1A rules the 1x1 cell out. It is the exact failure §3-A.7 exists to prevent, with a paper trail that reads as compliance.

*Fix:* Derive cell_label/coverage/VERDICT_SCOPE from the source deck's CELL_PARAMETERS (a/b vs the 1x1 lattice) instead of hardcoding, and refuse unless the emitted cell matches a --cell-label the operator must also pass. At minimum, refuse if the recorded 1A verdict string does not contain the cell_label the build is actually using.

### N31 — 1C-hessian — C:\Users\frank\sts-electrocatalyst\src\dft\build_hessian_pilot.py:771

The queue-summary line applies the Ir-measured 643 s/SCF to whatever states were built: `print(... f"{total} SCFs = {total * 643 / 3600:.1f} h wall")`. Measured: a Cr build prints "19 SCFs = 3.4 h wall at NCONC=1" even though the docstring three screens above says Cr "has NOT been timed at these settings" and is ~2.4x Ir per iteration at equal k — i.e. the honest figure is >= 8 h at 36 k-points, nspin=2, +U.

*Why it ruins the result:* It reintroduces the exact pattern lessons.md 2026-08-05 documents three times (a cost taken from a cheaper system and quoted for a harder one) and violates hard rule 6, inside the one file that was just rewritten to state a measured basis for every number. The prose says 'time one Cr SCF first'; the printout says 3.4 h, and the printout is what gets copied into a plan.

*Fix:* Print the extrapolation only for states whose per-iteration cost has been measured; for the others print 'NOT TIMED at these settings — time one SCF before sizing this arm' instead of a number.

### N32 — 1C-hessian — C:\Users\frank\sts-electrocatalyst\src\dft\hessian_analyze.py:522

Q4b (`asym_H > OUTLIER_FACTOR * rms_asym`) is a hard gate that returns VOID and it has no absolute floor and no clause in docs/43 (§3-A.4 registers ONE replacement gate: an absolute threshold on max|H_ij - H_ji|). Demonstrated: on a Hessian I built symmetric to machine precision, Q4b fired with "Q4b element (a21x,a21y) asymmetry 4.441e-16 eV/A^2 is 6.0x the rms — uniform noise cannot do that", VOIDing a state whose only defect was being too clean. The same max-over-block-vs-3-sigma construction in Q5 (line 545) carries a ~5% false-VOID rate on 18 independent noise elements.

*Why it ruins the result:* A gate that can VOID the pilot on a ratio of two round-off numbers is a false-negative generator, and VOID now stops the campaign decision outright. Real pw.x forces are printed to 8 decimals so rms_asym will not be at 1e-16 in production, which is why I am not calling this blocking — but Q4b is also the one gate in the file with no docs/43 clause behind it, and finding [28](6) was precisely 'gates that exist only in the code'. It predates this fix round and was not among the 31.

*Fix:* Give Q4b an absolute floor (fire only if asym_H also exceeds a few x the propagated sigma_H, e.g. 3*sqrt(2)*sigma_H), and either register the outlier criterion in a future amendment or demote it to a reported diagnostic like the withdrawn relative gate.

### N33 — 1C-hessian — src/dft/hessian_analyze.py:522

Q4b is a gate that cannot fire on the failure it names. It tests max|H_ij - H_ji| > 5 x rms(|H_ij - H_ji|) over the 36 off-diagonal pairs, but the max and the rms come from the SAME sample, so the statistic is capped at 6/sqrt(k) where k is the number of corrupted pairs. One bad job corrupts an entire ROW of H = 8 off-diagonal pairs, ceiling 6/sqrt(8) = 2.12, against a threshold of 5.0. Its own failure text says "One of the jobs feeding {ci} or {cj} is bad" - the exact condition it is structurally incapable of detecting.

*Why it ruins the result:* This is finding [13]'s pattern (a hard gate that cannot fail) reproduced in lane 1C and not caught by the 31. It leaves Q4a - a bulk sigma_F cap - as the only detector of a single contaminated job, and Q4a needs a ~30x-design corruption before it trips. Between 1x and 30x, a bad job passes every gate.

*Fix:* Compare each |H_ij - H_ji| to an ABSOLUTE threshold derived from the design sigma_F (e.g. 3 x sqrt(2) x sigma_F/delta) rather than to the rms of the same sample; or test per-ROW mean asymmetry, which is what a single bad job actually produces. Measured: with one job (a20yp) offset by 10x/100x/1000x the design noise, max/rms = 2.62 / 2.18 / 2.13 - it DECREASES toward the 2.12 ceiling as the corruption grows, and Q4b never fires.

### N34 — 1C-hessian — src/dft/hessian_analyze.py:500

The entire Q4 noise model is computed from the OFF-DIAGONAL asymmetry (`off = np.abs(H - H.T)[np.triu_indices_from(H, 1)]`), so it is completely blind to errors in the diagonal of H - and the diagonal is what sets the sign of the curvature and therefore the verdict. A force error confined to the displaced coordinate's own component contributes exactly zero to H - H.T and zero to the measured sigma_F, so no gate sees it. For Ir, nspin = 1, Q3 is explicitly "NOT APPLICABLE", so there is no other per-displacement physical check at all.

*Why it ruins the result:* It permits a FALSE CONFIRMED - the campaign's headline saddle-point claim - from one bad force component with zero gate failures. Measured on the real Ir manifest at sigma_F = 1e-6 with a true all-real spectrum (correct answer REFUTED): offsetting F_y on atom 21 in the a21yp deck by 0/1e-3/1e-2/1e-1 Ry/bohr leaves the reported sigma_F bit-identical at 8.87e-07 every time; at 1e-2 the verdict flips to CONFIRMED with a reported i1435 cm^-1 out-of-plane imaginary mode and 0 gate failures, and at 1e-1 to i5767 cm^-1, still 0 gate failures.

*Fix:* Use the six ym decks for what they are actually good for. Because the ym deck is the exact mirror of the yp deck (verified to 8.9e-16 A), symmetry forces F_y(ym) = -F_y(yp) and F_x/F_z(ym) = +F_x/F_z(yp) atom by atom. Add a gate that checks those two identities on the raw force blocks: it is free, exact, per-deck, and it is the only available test of the diagonal. Also check that F_y is zero in all 12 +/-x and +/-z decks.

### N35 — 1C-hessian — src/dft/hessian_analyze.py:293

`if o["nk"] != ref["nk"]` dereferences the reference record unconditionally. If the reference .out is missing while any displacement .out exists, parse_scf_out returned {path, exists: False} for the reference and this raises KeyError: 'nk'. Q0 and Q3 use ref.get(...) and are safe; Q2 does not.

*Why it ruins the result:* This is precisely the scenario the fixer just closed by hand - queue_r1.sh skipping the reference job on a stale 'JOB DONE' - and in that scenario the analyser crashes with a traceback instead of returning VOID. The fixer's proof ("running the analyser on the real runs/probe/Ir_hess (no outputs yet) prints PILOT INVALID") only exercises the all-missing case, where every job hits the `continue` above and ref["nk"] is never reached.

*Fix:* Guard the reference before the loop: if not ref["exists"], append a Q1/Q2 failure naming the reference and skip the nk comparison (or use ref.get("nk")). Reproduced: score_state on 18 valid displacement records + a missing reference -> KeyError: 'nk' at hessian_analyze.py:293.

### N36 — 1C-hessian — src/dft/build_hessian_pilot.py:601

`cell_label="1x1"`, `coverage_ML=1.0` and `VERDICT_SCOPE = "q = 0, 1x1 cell, 1 ML"` are hardcoded constants, not derived from the emitted geometry, while `--cell-verdict-1a` accepts any string and unlocks the build. docs/43 §3-A.7 requires Cr to be run "in the chosen production cell", but the flag records a string and changes nothing: the source is still runs/probe/Cr_basin (a 1x1 relaxation) and the manifest still asserts 1x1 / 1 ML.

*Why it ruins the result:* The scope stamp exists to stop a coverage artifact being read as the symmetry trap. As built it is an assertion, not a measurement, so if 1A returns 2x1 and someone repoints STATES["Cr"]["rundir"], every Cr verdict is stamped and printed "q = 0, 1x1 cell, 1 ML" while being computed in a 2x1 cell - a mislabelled artifact on exactly the axis the stamp was invented for. The HELD marker's own regeneration command has the same defect: it says "then runs it in the chosen production cell" and then gives `--out runs/probe`, which rebuilds the same 1x1 decks.

*Fix:* Derive cell_label and coverage_ML from deck["cell"] (compare a and b against the known 1x1 lattice) and refuse if they disagree with the recorded --cell-verdict-1a; the builder already measures the min-image contact from geometry, so the machinery is there. Verified: `--states Cr --cell-verdict-1a "TEST STRING - not a real 1A verdict"` writes 20 files whose manifest reads cell_label 1x1, coverage_ML 1.0, verdict_scope "q = 0, 1x1 cell, 1 ML", cell_verdict_1a "TEST STRING - not a real 1A verdict".

### N37 — 1C-hessian — runs/probe/m_hess.txt:6

The 19 decks and the manifest are not on the box. /workspace/sts/runs/probe/Ir_hess contains only the three renamed throwaway files (.in/.out/.run.in) and /workspace/sts/runs/probe/m_hess.txt does not exist. The manifest's five-line BEFORE-LAUNCHING header covers stale .out files but says nothing about uploading, and neither the manifest nor the report includes an upload + md5 step.

*Why it ruins the result:* The lane's deliverable is a queue line that cannot run. With the repo's own launcher (src/dft/queue_r1.sh, 2.5 kB, no pre-flight) a missing manifest makes `while read ... done < "$MANIFEST"` fail and the script still prints QUEUE_ALL_DONE - a silent no-op. It is currently masked only by a DIFFERENT launcher that another lane wrote onto the box (/workspace/queue_r1.sh, 8.8 kB, with PREFLIGHT/stale checks) and that is NOT in the repo, so re-uploading the repo copy would remove the protection.

*Fix:* Add the upload + md5-verify step to the lane's hand-off, and either ship the box's pre-flight launcher into src/dft/queue_r1.sh or state in the manifest header that the box copy is required. Evidence: `ls /workspace/sts/runs/probe/Ir_hess/` shows 3 files, all *.THROWAWAY-*; `ls /workspace/sts/runs/probe/m_hess.txt` -> No such file; /workspace/queue_r1.log already logged `PREFLIGHT_BAD missing-input /workspace/sts/runs/probe/Ir_hess/s0_OOH__hess_ref.in` at 19:43 UTC.

### N38 — 1C-hessian — src/dft/hessian_analyze.py:287

Q1's conv_thr check is `if o["scf_accuracy"] is not None and o["scf_accuracy"] > thr`. An .out with no `estimated scf accuracy` line skips the check entirely rather than failing it - missing evidence is scored as a pass.

*Why it ruins the result:* It is the same shape as the defect [21] was raised about: absence of a measurement scoring as a clean gate. Verified: 19 synthetic outputs identical to a passing set except that the accuracy line is absent score REFUTED with 0 gate failures. (Low probability in practice - pw.x prints the line whenever it prints `!` - but the gate should demand the line, not tolerate its absence.)

*Fix:* Make a missing `estimated scf accuracy` a Q1 failure: `if o["scf_accuracy"] is None or o["scf_accuracy"] > thr`.

### N39 — 1C-hessian — src/dft/hessian_analyze.py:597

The stated precedence rationale is wrong on its face and the implemented precedence suppresses a real observation. The score_state docstring justifies CONFIRMED > UNDERPOWERED by saying UNDERPOWERED "must outrank the two not-seen verdicts and only those" - but AMBIGUOUS is not a not-seen verdict; it means an above-floor imaginary mode WAS seen, just in-plane. As coded UNDERPOWERED outranks it.

*Why it ruins the result:* A genuine in-plane instability is reported as blindness. Verified: a true i300 cm^-1 in-plane imaginary mode at design noise returns UNDERPOWERED, and the printed reason mentions only the y-mode floor, never the i300 mode. Both route to "no campaign decision", so the campaign outcome is unchanged, but the per-state scientific record loses the observation.

*Fix:* Either order AMBIGUOUS above UNDERPOWERED, or keep the order and have the UNDERPOWERED reason string name any above-floor imaginary modes that were found.

### N40 — 1C-hessian — src/dft/hessian_analyze.py:679

The PARTIAL PILOT branch hardcodes the sentence "(docs/43 §3-A.7 holds Cr until block 1A returns its cell verdict)" no matter which registered state is missing, so scoring Cr alone would print "Not scored: Ir (docs/43 §3-A.7 holds Cr ...)".

*Why it ruins the result:* Cosmetic today (only Ir is buildable), but it is a false provenance sentence in a document whose whole value is provenance, and it becomes live the moment Cr is released and Ir is re-run.

*Fix:* Build the parenthetical from the missing state's own STATES[...] hold reason instead of a literal.

