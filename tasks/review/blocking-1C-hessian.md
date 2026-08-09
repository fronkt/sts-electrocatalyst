# Blocking findings — 1C-hessian

Verbatim from the 2026-08-09 adversarial review (6 verifiers, 31 blocking,
all six verdicts FIX_FIRST). Numbering is global across all three lanes.

## [21] src/dft/hessian_analyze.py:499
**lens:** Computational-catalysis referee: does the 1C deck set measure what it claims (an

**Problem.** campaign_verdict() never inspects gate_failures. A state that fails Q1-Q5 is scored AMBIGUOUS, AMBIGUOUS is not CONFIRMED, and the function then returns the R3 branch. I demonstrated this: I fed it 19 synthetic outputs whose only defect was 'estimated scf accuracy = 5e-9' (i.e. conv_thr 1e-10 not reached). Result: 19 gate failures, verdict AMBIGUOUS on both states, and campaign_verdict printed verbatim 'NEITHER CONFIRMED -> R3 TRIGGERED. Do not spend the 378 SCFs.'

**Why it ruins the result.** conv_thr = 1e-10 has never been reached anywhere in this project (see the next finding). A pure compute failure is therefore indistinguishable, at the campaign-decision layer, from a genuine scientific null. The output of the pilot would be 'the lead contribution has no proof' and block 2B would be cancelled on an artifact.

**Proposed fix.** campaign_verdict must return 'PILOT INVALID - N gate failures, no campaign decision' whenever any scored state has non-empty gate_failures. Only gate-clean CONFIRMED / REFUTED states may feed the BOTH / ONE / NEITHER branches. Mirror the same sentence into PREREG's CAMPAIGN DECISION section.

---

## [22] src/dft/build_hessian_pilot.py:499
**lens:** Computational-catalysis referee: does the 1C deck set measure what it claims (an

**Problem.** conv_thr = 1.0d-10 is unvalidated on this system. The deepest 'estimated scf accuracy' ever printed in this repo is 2.1e-9 (runs/Ir_anchor/s0_OOH.out final cycle), 5.7e-9 (runs/probe/Cr_basin/s0_OOH.out final cycle) and 8.6e-9 (runs/probe/Ir_orient/s0_OOH__yaw90.out final cycle) - and all three are BFGS-tightened cycles restarting from an extrapolated density, not from-scratch SCFs. The '+12 iterations' comes from extrapolating a measured 0.35 decades/iteration four further decades. electron_maxstep = 200 is inherited unchanged.

**Why it ruins the result.** If the Cr SCFs stall in the deep tail (characteristic for a metallic nspin=2 +U slab), each burns 200 x 332 s = 18.4 h and prints 'convergence NOT achieved'. 19 Cr jobs = 350 job-hours against a 75 h estimate (4.6x, the exact lessons.md failure mode), Q1 fails all of them, and via the previous finding that failure fires R3. There is also no cheap retreat: at conv_thr = 1e-9 the 3-sigma O-mode floor is ~55 cm^-1, i.e. at the declared i50 threshold, so the ladder really is 1e-10 or 1e-12.

**Proposed fix.** Release ONE job first - probe/Cr_hess s0_OOH__hess_ref - and read its accuracy trace before the other 37. It is the single cheapest de-risk and it doubles as the missing GATE-1 check below. Also set electron_maxstep ~120 in the hess decks so a stall costs 11 h not 18.4 h.

---

## [23] src/dft/build_hessian_pilot.py:439
**lens:** Computational-catalysis referee: does the 1C deck set measure what it claims (an

**Problem.** The reference SCF is never checked against the state it claims to be. The manifest records reference_relax_energy_ev but no source-relaxation magnetisation, and hessian_analyze.py prints that energy (line 524) without ever gating on it. Q3 compares each displacement to the REFERENCE only - all 19 jobs start from a fresh atomic superposition, so they can agree with each other while collectively sitting in the wrong basin.

**Why it ruins the result.** docs/41 s6c found exactly this failure on exactly this state: Cr *OOH's relaxation ran at M = 11.80 mu_B while a fresh SCF at identical coordinates found M = 11.00 and 175 meV lower. Cr_basin's own final state is M = 11.00, |M| = 20.09, E = -1636.48392834 Ry. If the 19 fresh starts land elsewhere, every gate passes and 75 job-hours produce the Hessian of an electronic state that is not the one eta(Cr) = 0.330 V was computed in. Note this check is free and exact: nosym only disables symmetry REDUCTION, so the 15 irreducible k-points ARE the 8x4x1 / 9x4x1 mesh and the reference energy is directly comparable to the relaxation's final energy.

**Proposed fix.** Record source_final_energy_ev, source_final_total_mag, source_final_abs_mag in the manifest. Add Q0 to hessian_analyze.py: |E_ref - E_relax| <= 10 meV, and for nspin=2 |M_ref - M_relax| <= 0.1 mu_B. Failure voids the state; do not score it.

---

## [24] src/dft/hessian_analyze.py:481
**lens:** Computational-catalysis referee: does the 1C deck set measure what it claims (an

**Problem.** REFUTED is effectively unreachable. `elif inplane or soft:` routes ANY imaginary eigenvalue below its own floor to AMBIGUOUS. I confirmed empirically: an otherwise all-real spectrum carrying one eigenvalue at i5 cm^-1 (10x below the declared i50 floor, 6x below the 3-sigma measured floor) returns AMBIGUOUS, not REFUTED. PREREG is self-contradictory on this point: REFUTED (line 168) is defined as 'no imaginary mode ... reaches its own EFFECTIVE floor', which is the same condition as AMBIGUOUS clause (b) (line 175) 'imaginary modes only below their EFFECTIVE floor'.

**Why it ruins the result.** A 9x9 partial Hessian containing three near-zero frustrated modes, evaluated at a point with 0.9-1.8e-3 Ry/au residual in-plane gradient, will very often throw one slightly negative eigenvalue. docs/43 s3's declared consequence is keyed on the words 'both pilot states come back REFUTED', so as coded that branch never fires and the null result is reported as AMBIGUOUS - the precise quiet-reframing docs/43 says it exists to prevent.

**Proposed fix.** Route `soft` to REFUTED, naming the sub-floor modes in the reason string; only `inplane` (significant, f_y < 0.90) is AMBIGUOUS. Rewrite PREREG clause (b) to match.

---

## [25] docs/43-prereg-week1-factorial.md:199
**lens:** Computational-catalysis referee: does the 1C deck set measure what it claims (an

**Problem.** docs/43 s3 (mtime 13:49) ALREADY contains a pre-registration for block 1C. PREREG in hessian_analyze.py (mtime 13:54) is a different rule and the builder's instruction is to 'paste it into docs/43'. Changes: y-character threshold 0.50 -> 0.90; REFUTED band 'no imaginary mode above 20 cm^-1' -> 'nothing reaches its effective floor'; the Hessian-symmetry relative gate max|H_ij-H_ji|/max|H_ij| <= 0.05 demoted from a HARD 'a failed gate voids the state' to Q4c ADVISORY; magnetic exclusions 'more than 2 of 18 voids the state' -> any single exclusion voids (build_hessian leaves NaN -> AMBIGUOUS); Q5 and the 3-sigma per-mode floor are new.

**Why it ruins the result.** The methodological selling point of this whole campaign is pre-registration. Overwriting a registered rule with a different one minutes before launch, with no dated amendment, is what a hostile referee leads with - and one of the changes (demoting the 5% symmetry gate from a void condition to advisory) loosens the rule.

**Proposed fix.** Do not overwrite s3. Append 's3-A, amendment 1, 2026-08-09, before any 1C job ran', list every change and its direction, and archive the pre-amendment docs/43 per the repo's archive rule. Record the honest reason the 5% relative gate was replaced: max|D_ij| is dominated by the OH stretch (~48 eV/A^2/amu), so 5% of it is ~2.4 against an expected asymmetry of ~0.05 - the gate is toothless, and the absolute Q4a is genuinely stronger.

---

## [26] runs/probe/Cr_hess/hess_manifest.json:1
**lens:** Computational-catalysis referee: does the 1C deck set measure what it claims (an

**Problem.** The Cr arm is not measuring *OOH on CrO2(110); it is measuring a proton-shared hydrogen-bonded chain at 1 ML. Computed from the emitted geometry (a = 2.9160 A): H21...O19(+1,0) = 1.338 A, with O20-H21 = 1.062 A and O20...O19(+1,0) = 2.399 A - a low-barrier hydrogen bond to the neighbouring adsorbate's anchor oxygen along the cus row. Ir is the same class but milder: O19...O20(+1,0) = 2.516 A, H21...O20(+1,0) = 2.554 A.

**Why it ruins the result.** The two out-of-plane modes most likely to come back imaginary are the OOH yaw and the H torsion, and on Cr both are governed by the image H-bond rather than by the mirror constraint the paper is about - a CONFIRMED on Cr would be attributed to the symmetry trap when its cause is the 1x1 coverage. A proton in a 2.40 A O...O bond is also the worst possible case for a harmonic central difference. And block 1A is concurrently testing whether the 1x1 cell is admissible at all; if it is not, this Hessian is void.

**Proposed fix.** State the coverage and the 1.338 A contact in the registered text. Scope every verdict to 'at q = 0 in the on-record 1x1 cell at 1 ML'. Add to the REFUTED wording, alongside the existing 'confined to the adsorbate' caveat, that an all-real Gamma-point spectrum in a 1x1 cell does not exclude an instability at another wavevector. Preferably hold 1C until 1A returns its cell verdict.

---

## [27] runs/probe/m_hess.txt:4
**lens:** Computational-catalysis referee: does the 1C deck set measure what it claims (an

**Problem.** 6 of the 38 SCFs carry exactly zero information and a further 24 measure a block the rule itself declares non-diagnostic. Verified at the byte level: for every adsorbate atom and both states, s0_OOH__hess_a{N}ym.in is the EXACT mirror image (y -> 2*y_cus - y, slab included, all 8 written decimals) of s0_OOH__hess_a{N}yp.in - so F(-delta_y) = sigma F(+delta_y) and the 'ym' runs are redundant. Also verified: every +/-x and +/-z deck is still exactly mirror-symmetric, so F_y = 0 by symmetry in all 12 of them, all 18 y/xz cross elements of H are structurally zero, and Q5 cannot fail - it is a noise measurement dressed as a physics gate. By PREREG's own exact-decoupling argument f_y is 0 or 1, so the 6x6 in-plane block cannot produce an f_y >= 0.90 mode and cannot change the verdict.

**Why it ruins the result.** The pre-registered question is answered by 3 displacements + 1 reference per state = 8 SCFs. On the builder's own measured basis (Ir 124.5 s/iter x 35 iters = 1.21 h; Cr 332 s/iter x 43 iters = 3.97 h) that is Ir 4.84 h + Cr 15.86 h = 20.7 job-hours against 98.3 - 78 job-hours, 79%, spent on nothing the verdict can use. The strictly zero-information part alone (the six 'ym' decks) is 15.5 job-hours. Nothing is lost: the one-sided y difference is still second-order accurate because F_y is odd in y, and its noise floor rises only from 18 to 21 cm^-1, still 2.4x below the declared i50 floor that actually governs.

**Proposed fix.** Emit y-only for the pilot (add --axes), or at minimum delete the six 'ym' decks and their manifest lines. Keeping the +/-y central difference for the sqrt(2) noise gain is 7 SCFs/state = 36.2 job-hours, still a 63% saving. If the in-plane block is kept, PREREG must say it is being bought for the block-2B ZPE/-TS table (plan line 135), not for the verdict - 2B does need the full 18, 1C does not.

---

## [28] docs/43-prereg-week1-factorial.md:199
**lens:** QE mechanics + queue mechanics + pre-registration integrity: will pw.x accept th

**Problem.** docs/43 §3 (P14) is ALREADY a committed pre-registration of block 1C (commit 11b7b04, `git status` shows it unmodified), and the new `PREREG` in src/dft/hessian_analyze.py:100-207 contradicts it in six places. (1) y-character: docs/43 line 233 says >=50%, PREREG uses FY_MIN=0.90 (hessian_analyze.py:88). (2) CONFIRMED floor: docs/43 says a fixed |omega| >= 50 cm^-1; PREREG uses max(50, 3*sigma) which I measured at i111 cm^-1 on an H-carried mode at the design sigma_F. (3) REFUTED: docs/43 line 235 says 'no imaginary mode above 20 cm^-1'; the 20 cm^-1 band does not exist anywhere in the code. (4) Hessian symmetry: docs/43 line 224 makes relative asymmetry <= 0.05 a HARD gate that 'voids the state'; hessian_analyze.py:439-441 demotes exactly that test to 'Q4c advisory' and substitutes new Q4a/Q4b. (5) magnetic exclusions: docs/43 line 227 tolerates up to 2 of 18; the code voids on the first one (NaN -> AMBIGUOUS, line 398). (6) Q1, Q2 and Q5 exist only in the code. build_hessian_pilot.py:166-168 then instructs the operator to paste PREREG into docs/43, which would create a third, conflicting copy inside the same file.

**Why it ruins the result.** docs/43 is the deposited pre-registration of record and hessian_analyze.py's own docstring (line 11-12) says a disagreement with it 'is a reportable defect'. Whichever way the 38 jobs come out, a judge or referee can point at the other rule and call the scoring post-hoc — and item (4) is a LOOSENING of a registered hard gate, which is the indefensible direction. This is the one defect that cannot be repaired after the jobs run.

**Proposed fix.** Before launch, pick one rule. Either reconcile PREREG to docs/43 §3 verbatim, or append a dated addendum to docs/43 that supersedes §3 with PREREG verbatim, states the reason, and records that it was written before any 1C job ran. Then delete the 'paste into docs/43' instruction at build_hessian_pilot.py:166-168 so a third copy cannot appear.

---

## [29] src/dft/build_hessian_pilot.py:132
**lens:** QE mechanics + queue mechanics + pre-registration integrity: will pw.x accept th

**Problem.** No SCF in this repository has ever been converged to 1e-10. Every measured cycle stops at conv_thr = 1e-6, and the deepest `estimated scf accuracy` that exists anywhere in runs/ is 5.7e-9 Ry. The '+12 iterations' comes from extrapolating the asymptotic rate — which is real, I re-measured it at 0.355 decades/iter (Ir yaw90 cycle 53) and 0.347 (Cr_basin cycle 3) — but both are measured on relax cycles starting from an EXTRAPOLATED density, and neither run was ever asked to go below 1e-8. Supporting risk I could not verify: QE clamps its Davidson threshold at ethr = MAX(ethr, 1e-13); with nelec = 169 (I read this off my own Cr smoke run) the target ethr = 0.1*conv_thr/nelec = 5.9e-14 is ALREADY clamped at conv_thr = 1e-10, so the last decades run against a fixed diagonalisation floor — the classic place an `estimated scf accuracy` plateau appears. Assumption 3 in the builder's own report admits this is unmeasured.

**Why it ruins the result.** If the SCFs plateau, `electron_maxstep = 200` runs to exhaustion: 200 x 124.5 s = 6.9 h per Ir job and 200 x 332 s = 18.4 h per Cr job = 481 job-hours = ~4 box-days at NCONC=5, which is 4.9x the 98 h budget, and it returns no Hessian at all. It fails in the exact silent way lessons.md documents three times: pw.x prints 'convergence NOT achieved ... stopping' AND 'JOB DONE', queue_r1.sh logs it as done, and any re-run SKIPS the job because queue_r1.sh:33 greps the stale .out for JOB DONE.

**Proposed fix.** Run ONE job to completion before launching the other 37: `bash queue_r1.sh` on a one-line manifest for probe/Ir_hess s0_OOH__hess_ref at NP=4 nk=4, ~1.3 h. Read (i) iterations actually needed to reach 1e-10, (ii) whether the accuracy plateaus, (iii) the printed `ethr` (this also settles whether the pre-registered 1e-12 escalation is reachable at all). This is lessons.md 2026-08-05 rule 1 verbatim — the same lesson records a 5 h probe that would have saved a 62-hour commitment.

---

## [30] src/dft/hessian_analyze.py:499
**lens:** QE mechanics + queue mechanics + pre-registration integrity: will pw.x accept th

**Problem.** `campaign_verdict` counts only verdict == 'CONFIRMED'. Every quality-gate failure routes to AMBIGUOUS (score_state:470-472). So two states that failed a gate for a purely technical reason produce 'NEITHER CONFIRMED -> R3 TRIGGERED. Do not spend the 378 SCFs' — identical to a genuine null result. I reproduced this: injecting a single 'convergence NOT achieved' into one of 19 synthetic .out files yields AMBIGUOUS for that state.

**Why it ruins the result.** One unconverged job, one lost .out, or one magnetic-basin excursion on each state is enough to fire the pre-registered branch that reweights the lead contribution away from the saddle-point proof and cancels block 2B. The correct response to a gate failure is 'rerun the failed jobs', not R3, and once the rule is deposited you cannot choose that after the fact.

**Proposed fix.** Add a fourth per-state verdict (VOID / INCONCLUSIVE) for 'Q1-Q5 failed', distinct from AMBIGUOUS (= gates passed, spectrum does not decide). Make the R3 branch in campaign_verdict require every state to be CONFIRMED-or-REFUTED, i.e. gates passed. Declare VOID's response as 'rerun the failing jobs' in PREREG.

---

## [31] src/dft/hessian_analyze.py:86
**lens:** QE mechanics + queue mechanics + pre-registration integrity: will pw.x accept th

**Problem.** The pilot is underpowered against exactly the mode it exists to detect, and the frozen rule reads that blindness as a null result. The out-of-plane modes of *OOH are H-dominated (torsion/wag). I ran the analyser end-to-end on a synthetic 9x9 Hessian carrying a known i116.6 cm^-1 H-carried out-of-plane mode: at the DESIGN sigma_F = 1e-5 Ry/bohr the effective floor on that mode comes out i111 cm^-1 — it barely survives. At sigma_F = 3e-5, which is still comfortably inside Q4a's 5 x 1e-5 pass band, the floor is ~i190 cm^-1 and 6 of 8 seeds return AMBIGUOUS. Separately, PREREG line 127 states the H-carried noise as '~70 cm^-1', which is the 1-sigma figure; the rule scores at 3 sigma, so the number a reader needs is ~111 cm^-1.

**Why it ruins the result.** A run can pass Q1-Q5 and still be structurally incapable of resolving an i50-i190 cm^-1 H-carried mode — the physically most likely signature of the symmetry trap on *OOH. PREREG then scores that as 'NEITHER CONFIRMED -> R3 TRIGGERED' and the campaign kills a 378-SCF block on a power failure it has mislabelled as evidence of absence.

**Proposed fix.** Pre-register a power criterion alongside the gates: after Q4, compute the effective floor of the highest-f_y mode; if it exceeds a declared value (i80 cm^-1 is the natural choice given the declared i50), score the state UNDERPOWERED and declare the response as the tighter-conv_thr rerun, not R3. Also correct the '~70 cm^-1' in PREREG line 127 to the 3-sigma number the rule actually uses.

---

