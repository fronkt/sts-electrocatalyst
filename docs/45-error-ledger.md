# 45 — The consolidated error ledger

**Created 2026-08-16.** One table for every error class this campaign has identified,
with its measured size, evidence pointer, governance status, and the compute stage that
addresses it. This is the research-infrastructure view of "the error budget" — the
concept docs/43 references but never consolidates. Status vocabulary (registered once,
round-2 synthesis §8): **MEASURED / BOUNDED / TRANSFERRED / NOT MEASURED.** The token
"structurally zero" is struck (refuted before any job ran).

**This document is NOT a pre-registration.** Thresholds live in docs/43 and its
amendments; per P-AUTHORSHIP every threshold statement is re-authored by Frank before
deposit. This ledger tracks what exists and what is owed.

---

## A. Silent errors (no warning anywhere in a converged output)

| # | Class | Size (measured) | Status | Evidence | Governed by | Addressed in |
|---|---|---|---|---|---|---|
| 1 | Symmetry trap (mirror-plane saddle) | 0.291 V on Ir η (1x1); collapses to −0.018 eV at 2x1v half-coverage (verified from raw outputs 2026-08-16). **Cr 2x1v, 0.5 ML (block 1C, 2026-08-23): an out-of-plane H-carried imaginary mode at i244.7 / i242.8 cm⁻¹ at δ = 0.01 / 0.02 Å — reproducible to 0.8 %, 37 SCFs in one basin at conv_thr 1e-10; H y-curvature negative and quadratic in δ. Analyzer verdict UNDERPOWERED (δ 0.01) / VOID (δ 0.02) because its σ_F is propagated from H−Hᵀ, which here is the forward-difference anharmonic (y,xz) block (doubles exactly with δ), not force noise (measured 2e-7 Ry/bohr from mirror identities). Instrument question ADOPTED 2026-08-23 (docs/43 A8.7, DOI 10.5281/zenodo.22072991): σ_F = mirror-identity reading (b), Q4b demoted to reported; re-scored docs/49 §7 — CONFIRMED at both δ against the i50 floor, reading-(a) label (UNDERPOWERED/VOID) carried alongside** | MEASURED, coverage-conditional | 1C Hessian i167 cm⁻¹ (Ir 1x1); **docs/49 (Cr 2x1v)**; runs/probe/*_cellsym; round-2 synthesis provenance header | P-SYMCOV (A8, owed); **σ_F estimator + am.2/Q4 collision (drafted as docs/47 §A8.7 2026-08-23; entrant's re-authoring owed)** | S3 |
| 2 | Magnetic multistability (basin set at step 1, dragged by pot_extrapolation) | 175 meV Cr *OOH; −405 meV Co *OH; 1.86 µB / −1.19 eV Cr *OOH off-arm confound. **Same-machine, run-to-run (2026-08-22, docs/46): one Cr *OOH deck, two Anvil runs bit-identical at SCF iteration 1, converged to M = 11.00 and 14.90 µB, 8.29 meV apart — not reproducible on a fixed platform; GATE-1 children above their parents by 8.29 / 47.77 meV are this** | MEASURED (in-house); prevalence TRANSFERRED (Fahmy >7,843 MP entries, arXiv:2509.05909) | GATE-1 audits; docs/41; **docs/46 panel + addendum** | A5 spin-seed rules; A8 (owed — basin CONFOUND rule drafted docs/47 §A8.3) | S3 + S0(h) |
| 3 | Estimator bias (η = max − mean exactly, ≥0 by construction, under imposed 4.92 eV) | exact identity; excess vanishes at pls crossing; Cr production U 7 meV from a crossing | MEASURED (algebraic + curves) | LIT-1 ladder; round-2 §6 item 4 | **P-PLS (A7.2) SCORED 2026-08-29: CONFIRMED, 5 of 6 metals flip (Cr, Fe, Ir, Mn, Ru); Ti flat. Robustness banked: Fe and Ru rest on a SINGLE row each, inside a measured error class, so the >=3 threshold is carried by exactly 3 robust members (Cr, Ir, Mn) with zero margin** | S6 |
| 4 | Projector pairing (atomic vs ortho-atomic at same U) | +1.45 eV in U value; **η consequence MEASURED: 0.4869 V at Xu's Cr U** | **MEASURED — docs/figs/pproj_readout.json verdict FIRES; the A0 readout uses it to stamp PROJECTOR-MISMATCHED on every Xu-anchor row and exclude them from the A6.3 test (a0main_readout.py)** | build history; Xu Table 1; pproj_readout.json | P-PROJ (A7) FIRED | S0(e) |
| 5 | Convergence-failure selection (unconverged states silently dropped) | Co *OOH 4 failures, Ni *OOH 5 | MEASURED as counts; rate now a registered budget row | run logs | A8 (owed) | S3 |
| 6 | **Literature-premise reversal** (a cited *experimental* ground state is overturned after the premise is baked into decks and prose) | RuO2 bulk ordered moment: asserted ~0.05 muB (Berlijn 2017, neutron); measured **<=4.8(2)e-4 muB** (Hiraishi, PRL 132, 166702 (2024), muSR) and **<=1.4e-4 muB bulk** (Kessler, arXiv:2405.10820, muSR+neutron, re-assigning the neutron peak to multiple scattering) -- **67-357x below**. Consequence measured in-house: gate (h) puts AFM **80-144 meV below NM** and moves adsorption energies **33-64 meV** (docs/43:1638-1644) | **MEASURED (literature) + MEASURED (in-house consequence)**; scope = BULK long-range order, surface (110) moments NOT excluded | Hiraishi arXiv:2403.10028; Kessler arXiv:2405.10820; Smolyanyuk PRB 109, 134424 (2024) | docs/41 "Correction of record -- 2026-09-03" (rebuke of `qe_slab.py:44-48` WITHDRAWN; Liang 2022 downgraded to hypothesis); gate-(h) relaxations remain HOLD, now as a **sensitivity arm** -- entrant's dated line owed | S0(h) + the report |

## B. Known-but-unpriced errors (the field knows; nobody prices them)

| # | Class | Size | Status | Evidence | Governed by | Addressed in |
|---|---|---|---|---|---|---|
| 6 | Hubbard-U fragility | 1.12 V on η(Cr); 1.11 eV descriptor span; 0.447 eV intercept span (4-pt ladder) — **dense grid now measures Cr's intercept span at 0.687 eV over U = 0 → 9** | **MEASURED — dense grid CLOSED 2026-08-29 at 6 metals; P-FLOOR-U (A7.3) SCORED: NOT MET at 3 of 6 vs registered ≥4. Read with a7_3.conditionality: the 3-over/3-under split is exactly the nspin=2/nspin=1 partition, and Ru is 15.5 meV from flipping the verdict — inside the still-open NM-vs-AFM class (33–64 meV) whose re-run is owed** — **fired P7, withdrew the headline** | docs/41 P7; LIT-1 memo (+ 2026-08-16 correction of record: undoped) | P-FLOOR-U (A7, owed); A6 | S4 (A0) |
| 7 | Coverage / cell (identical variables in one-cus-site 1x1) | 7/9 rows > 0.10 eV (1A; corrected 2026-08-23 from “6/9” — deposited A8.1 docs/43:1514 “7 of 9”, cellsym_readout.json cell rows 7 EXCEEDS / 2 WITHIN; docs/54 §6 item 15); Ir *OOH −0.285 → −0.018 eV | MEASURED (1A) → crossed design owed | docs/43 1A verdict ADOPT_2X1V | A8 (owed) | S3 contrast leg |
| 8 | XC functional | not yet measured here | NOT MEASURED (gated on S0(a) four-deck test) | — | A10 (owed, Sep 18) | S5, "XC only" row |
| 9 | Solvation | ~0.3 eV in c_M at O coverage vs ~0.1 at OH (Gauthier, read from paper) | TRANSFERRED — never measured here; registered as the non-additivity prediction | 10.1021/acs.jpcc.7b02383 | **A8 (docs/47 A8.2 carries it as an appendix prediction, 2026-08-23; A9 was the fallback)** | zero-compute registration |

## C. Structural results (not errors; bounds on what any screen can claim)

- **Scaling-floor lemma:** η ≥ c_M/2 − 1.23 V exactly; verified to 1e-9. No protocol
  fix can pass it. Floor/excess decomposition registered for pls ∈ {2,3} only.
- **Closed negatives (measured zeros — results, not gaps):** dipole correction; ESM at
  bc1 (duplicates the dipole correction); FM initialisation on AFM anchors (collapses
  to NM, tests nothing); MLIP fine-tuning on locked frames (F_y ≡ 0 blind spot;
  Warford & Csányi mechanism, arXiv:2601.21056).

## D. Amendment status for the compute steps — what is owed, by date

| Amendment | Governs | Status | Deadline |
|---|---|---|---|
| A1–A5 | blocks 1A/1B/1C, LIT | committed; no per-amendment DOI was ever recorded — now covered by the combined A1–A7 deposit | done |
| A6 | A0 cell scope + U-by-cell interaction | committed (2214b68); deposited in the combined A1–A7 record — 6A launch gate DISCHARGED | done 2026-08-16 |
| A7 | P-PROJ, P-PLS, P-FLOOR-U, nine S0 capability gates, phase-reality ledger | drafted (d1032e5) + **DEPOSITED: 10.5281/zenodo.21963144** (restricted; flip to open at submission) | done 2026-08-16 |
| **A8** | S3 protocol (off-plane = nosym + displacement, noinv pending S0(b), dy ladder, GATE-1 depth, CONFOUND rule, P-SYMCOV) + Anvil migration + measured cost + block 1C's σ_F instrument question | **ADOPTED + DEPOSITED 2026-08-23** — entrant reviewed docs/52 and adopted every drafted proposal; appended to docs/43 (2e61bf0, verified 1c09c38); **DOI 10.5281/zenodo.22072991**. Open in the deposited text: the A8.1/A8.5 AFM-scope line (gate-(h) HOLD), --bind-to, walltime value | Aug 24, before first S3 deck launches |
| **A9** | external-census controls (P-CTRL as a gate: OC20 negative / in-house 9-of-9 + 0-of-11 positive), detector scope + authorship boundary, the Xu/Divanis/pymatgen/lit census deliverables, both outcomes pre-stated, scope limits | **ADOPTED + DEPOSITED 2026-08-23** — same version as A8, **DOI 10.5281/zenodo.22072991**; OC20 fixed to val_id first-500-lexical; z-gate withdrawn as correction of record. Open in the deposited text: CI mechanism, Xu repair (a)/(b), P-BUILDER values, P-LIT values, six-row displacement + claim sentence (Sep 20), molecule jobs | Aug 22 (**overdue**), before any corpus is parsed |
| **A10** | BEEF row | NOT DRAFTED; gated on S0(a) | Sep 18 |
| **S8 freeze** | melt-set predictions frozen before first melt | registered as rule (round-2 addendum ccb1806); deposit owed before first ingot | before first melt |

**The binding sequence (updated 2026-08-16):** A1–A7 deposited as one restricted
Zenodo record, 10.5281/zenodo.21963144 — S0's nine gates are CLEAR TO LAUNCH.
Next deposits owed: A9 by Aug 22 (before any corpus parse), A8 by Aug 24 (before
first S3 deck), S8 melt-set freeze before the first ingot. Governance per A7.7:
amendments are AI-drafted disclosed infrastructure; the report paraphrases, never
copies.

---

## E. Program board (added 2026-08-16) — the reconciled S0–S8, cuts-reverted

The single current answer to "what is the plan." Scopes below INCLUDE the
budget-motivated cuts reverted by the 2026-08-16 addendum; physics kills stay dead
(ESM, 2x1o, bare symmetry-rate threshold, perturb_only_atom-as-cost-cut, n=25,
Wander/Kitchin, OC22 symmetry arm, MOOH phases, MLIP fine-tuning).

| Stage | Scope (as reconciled) | Governed by | Status |
|---|---|---|---|
| S0 | nine capability gates, ~35 box-h | A7 (DEPOSITED) | **CLOSED 2026-08-22** (25/25 runnable jobs on Vast, verdicts a–i recorded; docs/47 A8.0). The SnO₂ arm of gate (i) — precondition-deferred, never closed — **launched on Anvil 2026-08-23, job 20094699** after the Sn pseudo filename fix (docs/51); **PASS 1.188 meV/atom banked same day**; A7.5's Mom-2014 cus-site condition **CONFIRMED 2026-08-23 (docs/53)** — SnO₂ admission now awaits only the entrant's declaration |
| S1 | silentgate v0.1: entrant-written core, pluggable readers, CI controls | A9 (**DEPOSITED 2026-08-23**, DOI 10.5281/zenodo.22072991) | **UNBLOCKED 2026-08-23** — no longer blocked on A9; now gated only on the entrant-written core (A9.1 authorship boundary). AI-permitted here: tests, fixtures, CI workflow, packaging metadata |
| S2 | external census: Xu 810 lock/direction map, span_U halves, Divanis delta-curve, pymatgen+atomate paired audit; literature-coding audit RESTORED | A9 (**DEPOSITED 2026-08-23**, DOI 10.5281/zenodo.22072991) | **UNBLOCKED 2026-08-23.** A9.7 post-DOI acts 1-3 DONE same day (zip 6,989/6,989 blobs + 815/815 SHA-1s; header validation 4/4 count-first on RuO2; OC20 `is2res_val_id_trajectories.tar` md5-matched, 24,945 members, first-500 drawn + sha256 manifest). **Act 4 (the census) waits on the entrant's silentgate** |
| S3 | tier_v3 crossed coverage x symmetry x basin, 8 metals; second spin seeds RESTORED beyond *OOH-only where triage allows; dy ladder; Cr 1C + re-Hessian at escape | A8 (**DEPOSITED 2026-08-23**, DOI 10.5281/zenodo.22072991) | **LAUNCHED** — waves 1-4 + rounds 3-11 ran Aug 23-27 under the deposited protocol. Open in the deposited text: gate-(h)/AFM scope (**HOLD, 0 built**), `--bind-to`, walltime value |
| S4 | A0 dense U grid 1x1 + Cr 2x1v cell rider RESTORED + bulk hp.x Cr+Ti RESTORED (atomic projector) + slab hp.x one relaunch under 72 h cap RESTORED | A6 + A7 (DEPOSITED) | **EXECUTED — A0-main closed 2026-08-29 at 6 metals x 4 states; A6.3 INVERTED, A7.2 CONFIRMED, A7.3 NOT MET, A5.1(b) scored on its own quantities. S0(e)/P-PROJ fired and is banked** |
| S5 | BEEF-vdW sigma, Ru/Ir/Ti; extension to +U metals if clean | A10 (owed Sep 18, gated S0(a)) | gated |
| S6 | floor/excess, four estimators, n=7 statistics repair, P-SYMCOV scoring, r4 re-rank hook for S8 | A7 P-PLS/P-FLOOR-U + A8 | after data |
| S7 | freeze, figure pack, pre-submission assertions; arXiv preprint RESTORED as post-freeze option | — | Oct 8–15 |
| S8 | make->measure: re-rank gate -> freeze predictions -> melt 2–4 + poor anchor + IrO2 same-bench -> Purdue OER; ONE figure iff complete by freeze | S8 addendum (ccb1806); freeze deposit owed before first ingot | re-rank gate first |
| LIT-2 (A5.2/A5.7) | coarsened-Qiu termination ladder: 3 new relaxations + reused 1A rungs; GATE-1 children on the Cr rows | A5 (DEPOSITED) | Cr rows converged 2026-08-14 (banked 2026-08-23); Cr `__g1` children **launched 2026-08-23, job 20094768**; Ru `cov_2OH` output LOST (never pulled before box destroyed) → re-run as a fresh realisation, job 20094762 (landed 2026-08-23, 11 BFGS steps, banked). **A5.2 READOUT COMPLETE (scorer src/dft/lit2_readout.py + runs/probe/lit2_readout_2026-08-23.{txt,json}): RuO2 benchmark FAIL — ordering (i) TRUE, both transition potentials ~0.45 V below Qiu's brackets (1.009 vs 1.50±0.25, 0.837 vs 1.24±0.25) → Cr column = vacuum-CHE-only with the discrepancy attached; Cr conditional-on-termination FLAG = OFF (−0.042 eV/site vs −0.1 at U* = 1.560 V). Registered two-sided outcome; gates nothing. Cr mixed off arm VOID under §1 (+68.6 meV above mir) — search-failure comparability check = entrant's (C1)** |

Box-hour repricing of the restored scopes is owed alongside A8 (the restored items
add roughly 300–500 box-h; still trivially affordable).

**S3 wave-1 execution record (2026-08-24).** Arrays 20097663 (canary 3/3) + 20097688 (52):
**37/55 converged clean** (all Fe, 13/14 Mn, Cr escape 35-step + basin SCF, Ti ref+OH pair,
the mirror-symmetrized mir arms verified live — pw.x reports `2 Sym. Ops.` on every mir deck).
Two failure classes, neither silent (A8.4): (1) **node a024 OOM-killed 11 of its 12 tasks**
(0/43 kills on 21 other nodes; the survivor was the smallest SCF) — infrastructure, decks
unmodified, resubmitted as array 20101963 with `ExcNodeList=a024` (the `SBATCH_EXCLUDE` env
var was silently ignored by Anvil's sbatch — applied post-submit via `scontrol update`;
failed attempts preserved as `.out.attempt1`). (2) **7 SCF non-convergences on healthy
nodes, 5x Co / 2x Ni** — error class 5 exactly as A8.4 predicted for the magnetically
frustrated states. Ladder: rung (i) neighbour-density restart UNAVAILABLE — 42_s3_wave1.slurm
`rm -rf`s every scratch post-task, so no converged density survives (recorded here; a
retention rider for wave 2 is an entrant call) → rung (ii) `mixing_beta` 0.3 → 0.15 as
`.retry_bh.in` decks (only-beta-differs asserted at build; commit 0f530a7). A second failure
on any `.retry_bh` row goes to rung (iii): NOT_CONVERGED, plotted as a gap. Per-metal
per-state failure rates land in the S6 report as A8.4 requires. Wave-1 burn ~6.5k SU
(balance 92.4k).

**Retry-1 outcome (array 20101963, 2026-08-24): 9/18 converged -> 46/55.** All four Ti
decks, Mn s0_OH 1x1_k8, Ni ref and Ni s0_O mir were pure a024 victims (converged unmodified
elsewhere); both rung-(ii) 1x1_off decks converged at beta 0.15 (Co s0_O 19 steps, Ni s0_O
15 steps) — the ladder works where frustration is mild. **Rung (iii) NOT_CONVERGED, recorded
and plotted as gaps (no further compute under the ladder): Co s0_OH__1x1_off, Co
s0_O/s0_OH/s0_OOH__2x1v_mir, Ni s0_OOH__2x1v_mir.** Four a024-masked decks whose first real
attempt (beta 0.3, healthy nodes) then hit electron_maxstep — Co ref__2x1v, Co
s0_OH/s0_OOH__2x1v_off, Ni s0_OOH__2x1v_off — are fresh class-5 members at rung (ii):
array 20107835, ExcNodeList baked in via the new 43_submit EXCLUDE hook (73fa710). Co
ref__2x1v is load-bearing: if it exhausts the ladder, every Co 2x1v adsorption energy loses
its reference and the Co 2x1v column is all gaps. A8.4's 20% flag will fire at S6 for Co
*OH/*OOH and Ni *OOH (the amendment's own predicted population).

**Retry-2 outcome (array 20107835, 2026-08-24): 0/4 — ladder exhausted; wave-1 FINAL 46/55.**
All four hit electron_maxstep=200 at beta 0.15 with zero ionic steps -> **rung (iii)
NOT_CONVERGED. Wave-1 gap census (9, all Co/Ni): Co ref__2x1v, Co s0_OH__1x1_off, Co
s0_O/s0_OH/s0_OOH__2x1v_mir, Co s0_OH/s0_OOH__2x1v_off, Ni s0_OOH__2x1v_mir/off.**
Failure signatures (from the attempt records): **Co ref__2x1v is a NEAR-MISS, not a
diverger — monotonic creep to 2.63e-6 vs the 1e-6 threshold at step 200, magnetization
stable at 22.92 mu_B**; a fresh run at beta 0.15 with electron_maxstep raised (a registered-
recipe parameter, so an ENTRANT dated line, not a ladder rung) would very likely converge it
and restore the reference for the whole Co 2x1v column (currently: every Co 2x1v adsorption
energy is a gap for want of this one deck). Co s0_OH__2x1v_off stalls flat at 2.1e-5; Co
s0_OOH__2x1v_off at ~6.4e-4; Ni s0_OOH__2x1v_off oscillates 5e-4..1.6e-3 with wandering
near-zero magnetization (-0.58 -> -0.41) — the classic Ni *OOH frustration A8.4 cites.
These three look like genuine multistability, not step-starvation. Attempts preserved
through .attempt1/.attempt2; the .out on disk is the final (beta 0.15) attempt.

**Wave-2 execution record (array 20114094, 2026-08-24): 51/56 Slurm-complete, 5 OOM — ALL
on node a088** (5/5 kill rate there, 0/51 elsewhere): a SECOND sick node after a024, same
signature. Retried unmodified in array 20118525 with EXCLUDE=a024,a088 (the 43_submit hook,
exclusion verified a[024,088]); an RCAC ticket about both nodes is the entrant's call.
Convergence sweep of the 51: **34/36 __g1 children converged, 15/15 hess SCFs converged.**
A8.3 scoring (child − parent): **33/34 AGREE within +1 meV** — GATE-1 reproducibility holds
broadly. One REFUSAL: **Ni s0_O__1x1_off__g1 at +85.10 meV above its (beta-0.15) parent**
→ the registered second attempt from the parent's converged density is running as a
retention chain (see below). Two children landed BELOW their parents — **Fe
s0_OOH__1x1_off__g1 at −384.30 meV and Mn s0_OOH__2x1v_off__g1 at −20.62 meV**: a fresh-
density SCF at the parent's own final geometry found a DEEPER electronic state, i.e. those
two parents relaxed in metastable electronic states (the Cr *OOH class of docs/41). A8.3's
letter refuses only above-parent children; **which number banks for these two rows is an
interpretive call = entrant's** (precedent: the Cr_basin energy-of-record ruling). Two
children non-convergent on healthy nodes (Co s0_O__1x1_off__g1, Ni s0_OH__2x1v_off__g1) →
A8.4 rung (ii), own-beta halved (0.15→0.075, 0.3→0.15), in array 20118525.

**A8.3 density-retention chains (array 20119469, commit 362aa17):** replay parent with
scratch retained → child SCF startingpot='file' from the replay's .save. Discharges the
Ni refusal above and the 2 owed Cr_lit3 refused-child re-runs (docs/54:324). Replay
energies are parity evidence only, never banked (A8.8); each replay-vs-banked delta is a
free A8.5-style same-machine parity datum.

**Wave-2 retry outcome (array 20118525, 2026-08-24): 5/5 a088-OOM decks converged
unmodified off the sick node** — hess set now **19/19 complete** (displaced energies
+~0.9 meV over the escape minimum, sane), Ti s0_OOH__2x1v_mir__g1 AGREE (+0.002 meV).
The 2 rung-(ii) children failed again at halved beta → **rung (iii): Co s0_O__1x1_off__g1
and Ni s0_OH__2x1v_off__g1 NOT_CONVERGED; their parents' GATE-1 status = UNVERIFIED**
(neither AGREE nor REFUSED — the fresh-density audit cannot run; flag for S6). Wave-2
child census closes: **34 AGREE / 1 REFUSED-in-chain (Ni s0_O__1x1_off) / 2 UNVERIFIED
= 37.** Cold-start failures keep clustering on Co/Ni where the parents' warm relax
trajectories succeeded — consistent with the metastable-electronic-state theme.

**A8.3 chains outcome (array 20119469, 2026-08-24): all three second attempts AGREE —
no MULTISTABLE recordings; the banked parent energies STAND.** Ni s0_O__1x1_off__g1
from density: −2598.63677183 = **+0.019 meV** vs banked parent (was +85.10 cold-start);
Cr oosh__1x1_off_magp__g1: **+0.002 meV** (was +8.29); Cr s0_OOH__1x1_yaw90_magm__g1:
**+0.001 meV** (was +47.77). **The LIT-3 BASIN_DRIFT question closes: cold-start
electronic-metastability artifacts, basins fine.** Replay parity data: Cr oosh replay
+0.026 meV and Cr yaw90 replay −0.52 meV vs banked; the **Ni replay branch-diverged**
(−2598.63335298, mag 8.01, +46.5 meV above banked mag-4.3 state) — same deck, same
machine, different electronic branch, yet the child STILL relaxed into the banked state
from that density (which strengthens the AGREE verdict: even a wrong-branch warm start
finds the banked minimum at the parent geometry; only the atomic-superposition cold start
does not). Provenance nuance recorded: chain-1's density was the replay's (mag-8 branch),
not literally the parent's own — the A8.3 letter is satisfied by the child reproducing the
banked energy within 1 meV at the parent geometry. Ni 1x1_off now has direct evidence of
>= 2 electronic branches (more Co/Ni metastability, the docs/41 class).

**1C esc re-Hessian readout (2026-08-24, runs/s3/Cr/hessian_result_esc_2026-08-24.json):
i244.7 DOES NOT SURVIVE the escape.** All 9 adsorbate-block modes REAL at the escaped
geometry (softest 85.3 cm-1, O38-carried; analyzer verdict REFUTED = no unstable adsorbate
direction, gate-clean 0/0, robust at the docs/49 reading-(b) floor of record i50 AND at the
fallback asymmetry sigma_F). The mirror geometry was a SADDLE; the escape descended
-150.8 meV into a genuine minimum in the SAME magnetic state (M = 23.00 everywhere — the
docs/41 metastable-magnetic trap did not recur; purely geometric). Physical signature: O-H
stretch 3415.9 -> 2588.4 cm-1 + stiffened H out-of-plane modes = the H found a hydrogen-
bond acceptor (H y-displacement 0.865 A off the old plane). Semantics: this does NOT
contradict docs/49 s7c CONFIRMED (which says the MIRROR geometry is a saddle) — together
they are the saddle -> minimum pair. Fallback sigma_F 1.66e-6 is 18x below the mirror
geometry's 2.99e-5, independently confirming s4b's forward-difference-anharmonicity
diagnosis. Which energy banks for Cr *OOH 2x1v (mir saddle -3188.70497 / escape minimum
-3188.71606 / banked off -3188.79232, still 76 meV deeper) = S6/entrant.

**Round-3 launch (array 20123293, 2026-08-24, docs/55).** The entrant delegated the four
parked calls by criterion ("most scientific impact... if it's compute, no matter, go
ahead") — rulings recorded in docs/55: (1) Fe/Mn below-parent drift rows take the docs/52
C9 §5-strict arm (re-relax IN the deeper state: `__basin` decks = the `__g1` child with
scf→relax, diff vs original parent = exactly {prefix, starting coordinates}); (2) dated
recipe line `electron_maxstep 200→500` at last-attempted beta on the 9 rung-(iii) gaps +
2 rung-(iii) `__g1` children (`.retry_ms.in`, one-token diff vs `.retry_bh.in`,
assert-verified; NOT a ladder rung — ladder exhausted, attempts preserved); (3) Cr *OOH
2×1v mir arm energy of record = the escape minimum −3188.71606 Ry (saddle −3188.70497
retained as diagnostic; mir-vs-off gap now quoted minimum-to-minimum, 76.3 meV); (4) RCAC
ticket DRAFTED (anvil/rcac_ticket_draft_2026-08-24.md) — submission is the entrant's.
Node check 2026-08-24: a024 ALLOCATED / a088 MIXED — back in the general pool, never
drained, no evidence of repair; EXCLUDE=a024,a088 verified on 20123293 (ExcNodeList=
a[024,088]). Mechanics note: the driver's stale-out gate correctly refused the 11 reopened
rows while their rung-(iii) NOT_CONVERGED records held the canonical `.out` names — those
records were renamed to the next `.out.attemptN` (nothing deleted; mirrored in git) and
preflight then passed 13/13. Worst-case burn 79.9k SU at 48 h; expected ~5-13k. Every
newly converged relax owes a `__g1` child (wave 4). Until the Fe/Mn loop closes, both
rows are PENDING-RERELAX in S6-facing tables (parent and child both quoted, neither
final).

**S6 analysis block (workflow wf_2ca82c9d-eaa, 12 agents, 2026-08-24): docs/56 written; every
dimension adversarially re-derived from raw .outs.** Readout: src/dft/s3_readout.py (byte-
deterministic, sha-verified twice) -> runs/s3/readout/s3_readout_2026-08-24.json — 149 rows,
109 cells, 87 with an energy of record; the 57 external docs/54 rows all reproduce to 5e-8 Ry.
Dimension scripts committed: s3_nonadditivity.py, s3_confound_check.py, p_symcov_score.py.
Verifier verdicts: P-SYMCOV REPRODUCED; A8.1 bins REPRODUCED; CONFOUND census and A8.4 table
REFUTED at the summary level only (both artifact files were already correct; corrections
printed in docs/56 as [CORRECTED] — e.g. cell-pair class 47 not 42, SCF-fail split Co 17 +
Ni 7 not 18+6). Headlines, all tagged and none interpreted: (1) P-SYMCOV both-coverage count
= EXACTLY 5 of 8 (Cr, Mn, Fe, Ru, Ir) — sits ON the registered >=5 branch and flips to 3 if
the OPEN tier_v2 1x1 mirror-member ruling (docs/54:406-411) voids the nosym rows: the single
highest-leverage open call in the analysis. (2) A8.1: 13 definitive rows -> 6 NON-ADDITIVE
(exactly the 1A inconclusive set) + 7 at <=0.10 eV with no deposited bin name; Fe *O at
+0.1104 eV rides the same OPEN mirror-member call. (3) CONFOUND census over 137 pairs: 39
flagged / 42 within / 56 not-evaluable; docs/54:147's Cr *OH 1x1 CONFOUNDED verdict is NOT
reproducible from the printed moments (both 11.00) — entrant check owed; Cr *OOH 2x1v
CONFOUND-vs-R3 recorded as RECORD-CONFLICT, unresolved. (4) A8.4 at rung-(iii) close fires
Co ref / Co *O / *OH / *OOH / Ni *OOH on the row basis; the attempt basis adds Ni *OH at
25.0% — numerator/denominator basis is unregistered, entrant's call. 25 spec ambiguities
carried forward in docs/56 (A8.1 bin-scheme coexistence, P-SYMCOV 'large' cut, per-metal
state aggregation, ref-as-state, infrastructure kills in the rate, ...).

**GATE-1 census CORRECTION (found by the block's verify pass, confirmed independently):
the three wave-1 basin __g1 children were never in the wave-2 census.** Scored 2026-08-24:
Co s0_OH__basin_g1 +0.02 meV AGREE, Cr s0_OOH__basin_g1 +0.00 meV AGREE, **Ni
s0_OH__basin_g1 = +177.10 meV ABOVE its parent (M 7.12 vs parent 4.15) — REFUSED-candidate**
(docs/43:1589-1592), the same cold-start electronic-branch signature as the three discharged
chains. Registered second attempt launched from the parent's converged density: **chain-2,
job 20124032** (runs/chains/m_chains2.txt, builder src/dft/build_retention_chain2.py —
cross-dir variant, decks in runs/probe/Ni_basin/, refused first attempt untouched at
runs/s3/Ni/s0_OH__basin_g1.out; EXCLUDE=a024,a088). Full-S3 GATE-1 census pending that
chain: **37 AGREE / 1 REFUSED-in-chain (Ni basin *OH) / 2 UNVERIFIED (round 3).**

**Chain-2 outcome (job 20124032, 2026-08-24): AGREE — the Ni basin refusal discharges.**
Replay reproduces the banked parent at +0.017 meV in the SAME state (M 4.15; unlike
chain-1's Ni replay, no branch divergence), and the fromparent child lands **+0.012 meV
vs the banked parent, M 4.15 → AGREE** (was +177.10 meV / M 7.12 cold-start). The
docs/54:205 Ni *OH 1×1 mir energy-of-record row STANDS. Replay energy is parity evidence
only (A8.8). Full-S3 GATE-1 census now: **38 AGREE / 0 REFUSED / 2 UNVERIFIED** — the two
UNVERIFIED parents await their round-3 maxstep children (array 20123293, in flight). All
four A8.3 refusals to date have now resolved AGREE via density retention: cold-start
electronic metastability, zero MULTISTABLE recordings.

## Round 3 drained (array 20123293, 2026-08-25) — 4/13; the failure mode is now NAMED

All 13 tasks Slurm-COMPLETED (last 2026-08-25T06:01:34); outputs pulled md5-matched
(`s3_round3_outs.tgz` = `265d71ab80da508c8e99eb24009fd44d` both ends), extracted into the
13 slots vacated at 9ebedff (predecessors preserved `.attempt2`/`.attempt3`, A8.8 clean).

**Converged 4/13.** `Co ref__2x1v` (**the maxstep-500 entrant ruling worked — the Co 2×1v
reference exists**, −4578.38410421 Ry), `Co s0_OH__1x1_off` (−2331.98669493),
`Co s0_OOH__2x1v_mir` (−4662.69189747), `Fe s0_OOH__1x1_off__basin` (−2558.16677357).

**The 9 failures are not one population — they split 6 / 1 / 2, and the split is the
finding.** Ruling 2 (electron_maxstep 200 → 500) did not fail on these rows; it moved them
from "stall/oscillation" (the 2026-08-24 rung-(iii) reading) to *measurably creeping*:

| deck | it. | last accuracy (Ry) | beta | class |
|---|---|---|---|---|
| Co s0_OH__2x1v_mir | 500 | 8.80e-5 | 0.15 | creep |
| Co s0_O__2x1v_mir | 500 | 4.31e-5 | 0.15 | creep |
| Ni s0_OOH__2x1v_mir | 500 (bfgs 3) | 3.43e-5 | 0.15 | creep |
| Co s0_OH__2x1v_off | 500 | 1.85e-5 | 0.15 | creep |
| Co s0_OOH__2x1v_off | 500 | 1.14e-5 | 0.15 | creep |
| Ni s0_OH__2x1v_off__g1 | 500 | 6.41e-4 | 0.15 | creep (slow) |
| Mn s0_OOH__2x1v_off__basin | 200 (bfgs 17) | **5.3e-7** | 0.30 | **never got 500** |
| Co s0_O__1x1_off__g1 | 500 | 6.78e-3 | 0.07 | sick |
| Ni s0_OOH__2x1v_off | 500 | **9.43e-2** | 0.15 | sick (M 4.19 vs ~13 — branch flip) |

Six rows sit 11–88× above a 1e-6 Ry `conv_thr` after 500 iterations with no oscillation —
the Co-ref NEAR-MISS creep signature (docs/45, 2026-08-24 final) generalised to the whole
Co/Ni 2×1v block. **This is a ceiling on iterations, not a broken deck.** The two "sick"
rows are different in kind: `Ni s0_OOH__2x1v_off` collapsed to M = 4.19 μB against ~13 μB
everywhere else on Ni — an electronic-branch flip, the same family as the four A8.3
cold-start refusals, and the density-retention instrument (`build_retention_chain2.py`) is
the matching tool, not more iterations.

**`Mn s0_OOH__2x1v_off__basin` is a registration slip, not a physics result:** ruling 1's
basin re-relaxes were built at the ORIGINAL `electron_maxstep = 200` / beta 0.30 while
ruling 2 raised the rescue decks to 500. It died at 5.3e-7 Ry — *below* `conv_thr` — on
QE's tighter-`ethr` restart at iteration 200, after 17 BFGS steps and still descending.
Any re-run at 500 almost certainly closes it.

**Both below-parent findings are CONFIRMED, and both went deeper than their `__g1` children.**
The §5-strict re-relaxes were built to test whether the wave-2 below-parent children were
noise. They are not:

| row | parent (banked) | `__g1` child | §5-strict re-relax | re-relax vs parent |
|---|---|---|---|---|
| Fe s0_OOH__1x1_off | −2558.13528265 | −384.3 meV | −2558.16677357 (**converged**) | **−428.5 meV** (−44.2 vs child) |
| Mn s0_OOH__2x1v_off | −3617.09868891 | −20.6 meV | −3617.10180292 (bfgs 17, not conv.) | −42.4 meV (−21.8 vs child) |

The Fe row is converged and lands **428.5 meV below the banked parent** — the banked
`Fe s0_OOH__1x1_off` energy-of-record is a metastable-parent artifact, not the minimum,
and the gap is far outside anything the A8.3 ±1 meV gate was built to police. The Mn row
reproduces the same direction at 42.4 meV and had not stopped descending. **Banking these
as replacements is the entrant call already parked on 2026-08-24 (A8.8 no-replacement);
what round 3 removes is the "it might be noise" option.**

**Co 2×1v column is still not assemblable.** With the reference restored the column holds
ref ✓, `*O`-off ✓, `*OOH`-mir ✓ — no arm carries `*O`+`*OH`+`*OOH` together (off is missing
`*OH`/`*OOH`; mir is missing `*O`/`*OH`). All four missing rows are creepers in the table
above, so the column is one iteration-ceiling ruling away from closing, not one physics
question away.

**GATE-1 census unchanged at 38 AGREE / 0 REFUSED / 2 UNVERIFIED** — both round-3 `__g1`
rescues (`Co s0_O__1x1_off__g1`, `Ni s0_OH__2x1v_off__g1`) failed again, so the two
UNVERIFIED parents stay UNVERIFIED. A8.4 rung-(iii) count rises accordingly.

---

## CORRECTION (2026-08-25, same day): the round-3 triage above is WRONG, and the reason is an unregistered parameter

The entry above classifies 6 of the 9 round-3 failures as "creepers ... an iteration
ceiling, not broken decks" and hands the entrant a decision to raise `electron_maxstep`
from 500 to 1000-1500 across all six. That work was started by trying to *size* the bump —
fit the tail decay rate of each failure and extrapolate the iterations needed to reach
`conv_thr`. The fit refused to converge on an answer, which is what exposed the following.

### QE was never holding these runs to the `conv_thr` in the deck

`upscale` is not set in **any** deck in this repository (0 files match). Quantum ESPRESSO's
default is `upscale = 100`, which means that during a `relax` it **tightens `conv_thr` as
the forces converge**, down to a floor of `conv_thr/upscale` = 1e-6/100 = **1e-8**,
printing the new value at the end of each BFGS step:

```
     scf convergence threshold =      1.0E-06     <- the registered value, block 1
     new conv_thr            =       0.0000010000 Ry
     new conv_thr            =       0.0000006572 Ry
     new conv_thr            =       0.0000002791 Ry   <- block 4 ran under THIS
```

So `Ni s0_OOH__2x1v_mir` reporting "convergence NOT achieved" after reaching
**3.2e-7 Ry** — three times *better* than the deck's stated `conv_thr = 1.0d-6` — is not a
contradiction and not an ethr artifact. By BFGS step 4 it was being held to 2.79e-7 and
fell 15% short of it. The same mechanism, run to its floor, explains the Mn row: at BFGS
step 20 `Mn s0_OOH__2x1v_off__basin` was being held to **1.0e-8** and reached 5.0e-7.

**This retracts the "registration slip" paragraph above.** The Mn basin deck's
`electron_maxstep = 200` was real but was never the binding constraint — re-running it at
500, the decision parked as ENTRANT DECISION 2, would not have converged it. It was 50x
short of a threshold that no deck in this project has ever declared.

### What this does to the banked ladder: nothing bad, and the methods text is now wrong in our favour

Effective `conv_thr` at the last SCF of every banked converged S3 relax:

| | rows |
|---|---|
| banked converged relaxes | 42 |
| met a threshold **tighter** than the registered 1e-6 | **39** |
| tightest effective threshold reached | **1.0e-8 Ry** |
| met exactly 1e-6 | 3 — `ref__2x1v`-class rows with 0 BFGS steps (no ionic motion → no tightening) |

Every banked number is therefore converged **at least as tightly as advertised, and 39 of
42 are 100x tighter**. No re-banking is owed and no result is invalidated. What *is* owed
is a methods correction: the protocol description says the SCF threshold is 1e-6 Ry, and
the runs actually met 1e-8 almost uniformly. **Frank re-authors that sentence** — it is a
threshold claim in the report, not infrastructure.

Two causes were checked and cleanly ruled out before landing on this one:

- **`ecutrho` under-convergence for the USPP species.** `ecutrho = 640.0` against
  `ecutwfc = 80.0` is 8x, correct for ultrasoft. Ruled out.
- **`negative rho` poisoning the density.** Identical magnitude (3-5e-4) in the failed
  rows *and* in `Co s0_O__2x1v_off` / `Co s0_OOH__2x1v_mir` / `Co ref__2x1v`, which all
  converged to 1e-8 in the same cell with the same cutoffs. Ruled out.

That last rule-out carries the important positive result: **the fixed point is reachable
in these cells.** The failures are not decks that cannot converge; they are decks that
cannot find it from where they were started.

### Corrected triage — `src/dft/scf_triage.py`

The tool classifies each non-convergent SCF block on the **progress rate of the running
minimum**, not on flatness (these runs jitter 15-30% between iterations while making no
progress, so a flatness test misreads them), and against the threshold **actually in
force** for that block:

```
deck                                     blk   eff_thr   min_acc  @it      last    n   dM60  class
Co/s0_O__2x1v_mir.out                      1  1.00e-06  4.29e-05  488  4.31e-05  500   0.41  SLOW
Co/s0_OH__2x1v_mir.out                     1  1.00e-06  6.37e-06  246  8.80e-05  500   0.08  STALLED
Co/s0_OH__2x1v_off.out                     1  1.00e-06  1.84e-05  491  1.85e-05  500   0.04  STALLED
Co/s0_OOH__2x1v_off.out                    1  1.00e-06  1.13e-05  486  1.14e-05  500   0.07  STALLED
Co/s0_O__1x1_off__g1.out                   1  1.00e-06  9.60e-04  244  6.78e-03  500   0.33  STALLED
Mn/s0_OOH__2x1v_off__basin.out            20  1.00e-08  5.00e-07   34  5.30e-07  200   0.01  UNREG_THR
Ni/s0_OOH__2x1v_mir.out                    4  2.79e-07  3.20e-07  125  3.43e-05  500   0.22  UNREG_THR
Ni/s0_OH__2x1v_off__g1.out                 1  1.00e-06  1.53e-05  123  6.41e-04  500   0.78  BRANCH
Ni/s0_OOH__2x1v_off.out                    1  1.00e-06  2.55e-03  139  9.43e-02  500   2.41  BRANCH
```

| class | n | what it means | registered remedy |
|---|---|---|---|
| **SLOW** | **1** | running min still improving >2x per 150 iterations | **the only class `electron_maxstep` can fix** |
| **STALLED** | 4 | min improved <2x over the last 150 it., magnetization stable to <0.1 μB — a self-consistency floor with a saturated Broyden history | **A8.4 rung (i)**, restart from density with a fresh mixing space |
| **BRANCH** | 2 | magnetization unstable over the tail (0.78 and 2.41 μB) | **A8.3 density retention** from the parent |
| **UNREG_THR** | 2 | met the *registered* 1e-6 (5.0e-7, 3.2e-7); refused only by the tightened threshold | set `upscale` |

**ENTRANT DECISION 1 as written above is refuted.** It would have spent ~3,000 SU raising
`electron_maxstep` on six decks of which **one** is iteration-limited. The other five are
flat or oscillating: `Co s0_OH__2x1v_off` moved from 1.836e-5 to 1.851e-5 across its final
24 iterations, and `Co s0_OOH__2x1v_off`'s running minimum improved by less than 2x over
its last 150 — another 1,000 iterations of either buys nothing. **ENTRANT DECISION 2 is
refuted** for the reason given above.

Note that four of the five STALLED/SLOW rows completed **zero** BFGS steps — the first SCF
never converged, so no ionic relaxation happened at all. The loss in those decks is not
energy precision (1.1e-5 Ry = 0.155 meV, already inside the A8.3 ±1 meV gate); it is that
the geometry never moved.

### Corrected decision set

- **R1 (registered parameter, new):** declare `upscale` explicitly. `upscale = 1.0` holds
  every relax to the registered `conv_thr = 1e-6` and is what the two UNREG_THR rows need
  (both are already below 1e-6). Consequence to weigh: the 39 banked rows met 1e-8, so
  new rows at 1e-6 are 100x looser than their siblings — numerically irrelevant against a
  1 meV = 7.35e-5 Ry gate, but it is a protocol-uniformity claim and therefore Frank's.
  Both UNREG_THR rows also need restarting from their last geometry, not from scratch
  (Mn is 20 BFGS steps in) — `build_restarts.py` / `build_basin_restarts.py` precedent.
- **R2 (registered parameter):** `electron_maxstep` 500 → 1500 for **`Co s0_O__2x1v_mir`
  only**. One deck, ~500 SU, replacing a six-deck ~3,000 SU decision.
- **R3 (A8.8, unchanged):** the Fe/Mn below-parent minima. Round 3 removed the noise
  option; the Fe gap is 428.5 meV, 400x the gate width. Note the Mn number is now better
  qualified than it was this morning — it stopped at 5.0e-7 Ry against a 1e-8 goalpost,
  i.e. it was *converged by the registered criterion* when it was cut off, and it was
  still descending.
- **R4 (no ruling needed, registered mechanics):** the 4 STALLED rows to A8.4 rung (i) and
  the 2 BRANCH rows to A8.3 chains. `Co s0_O__1x1_off__g1` and `Ni s0_OH__2x1v_off__g1`
  both have banked converged parents, so both take a proper parent→child retention chain
  — which is the path that closes **GATE-1 UNVERIFIED to zero**.

`Ni s0_OOH__2x1v_off` (BRANCH, dM 2.41 μB) is a primary relax with no parent to seed from
and is the one row with no registered remedy in hand; it is the natural A8.4 rung-(iii)
NOT_CONVERGED gap candidate if a self-seeded staged restart fails.

### Round 4 LAUNCHED — Anvil array 20135148, 2026-08-25

`runs/chains/m_round4.txt`, 5 rows, `anvil/44_chain.slurm` via `45_submit_chains.sh`,
array `1-5%3`, `EXCLUDE=a024,a088`. Balance at launch **83,845.8 SU**.

Both sick nodes were checked immediately before submitting and both were `MIXED` —
still in the general pool, never drained (the RCAC ticket in
`anvil/rcac_ticket_draft_2026-08-24.md` is still unsent). Their documented kill rates
are 11/12 on a024 and 5/5 on a088 against 0/51 elsewhere, and a node kill during a
chain's *replay* step discards the whole task, so the exclusion is not optional here.

**Pre-flight found a real defect in rows 1-2 and it was fixed before any SU was spent**
(commit `9f9123e`). The two A8.3 children were being built from `__g1.in`, the wave-2
base deck — but both children have failed three times and the A8.4 ladder escalated
their mixing at every rung:

| child | attempt 1 (`.in`) | attempt 2 (`.retry_bh`) | attempt 3 (`.retry_ms`) |
|---|---|---|---|
| `Co s0_O__1x1_off__g1` | beta 0.15 / maxstep 200 | beta 0.075 | beta 0.075 / 500 |
| `Ni s0_OH__2x1v_off__g1` | beta 0.30 / maxstep 200 | beta 0.15 | beta 0.15 / 500 |

Seeding the base deck would have handed the parent's converged density to the *least*
robust of three already-failed configurations, and would have made the retention test a
two-variable one — density and mixing changed together, so a failure would have been
uninterpretable. It was also inconsistent with rows 3-5, which already seed the
`.retry_ms` deck of record. `mixing_beta` and `electron_maxstep` are convergence-*path*
parameters: they decide whether the fixed point is reached, never where it is, so taking
the robust one costs nothing and cannot move a banked number. Each child now differs
from its own last failed attempt in exactly one thing — where it starts. `base_of()`
strips `.retry_ms`, so all five manifest rows are byte-identical to the previous build.

Verified before launch:

- all 10 decks differ from their source by **prefix + `startingpot = 'file'`** (children)
  or **prefix only** (replays) or **prefix + `calculation` + `conv_thr`** (seeds), by
  `difflib` opcode assertion in the builder and again by hand-diff;
- geometry md5 of `.in` vs `.retry_ms.in` identical for both A8.3 children;
- the 4 source decks byte-identical local ↔ Anvil; all 11 staged files md5-identical
  local ↔ Anvil after the push;
- all 4 referenced UPFs present in `$PROJECT/pseudo` at exact case
  (`Co_pbe_v1.2.uspp.F.UPF`, `H.pbe-rrkjus_psl.1.0.0.UPF`, `ni_pbe_v1.4.uspp.F.UPF`,
  `O.pbe-n-kjpaw_psl.0.1.UPF`) — the 2026-08-20 Ti incident and the SnO2 case-mismatch
  trap are both in this class;
- all 10 target `.out` slots free on Anvil **and** locally (A8.8);
- `128 % nk == 0` on every row, `PARITY_PASS` present, pseudo preflight evidence present.

`scf` decks carrying a leftover `&IONS` namelist are not a hazard: QE ignores it and
275 such decks in this repo already reached `JOB DONE`.

**Replay baselines** — the replay energy is A8.5-style parity evidence and is never
banked (A8.8). It must reproduce:

| row | banked parent |
|---|---|
| `Co s0_O__1x1_off` | `-2330.66171228 Ry` |
| `Ni s0_OH__2x1v_off` | `-5157.23065359 Ry` |

**Cost.** Measured comparables: the two parents relaxed in 2,487 s and 3,939 s; the three
prior chain tasks ran 17 min, 35 min, 1 h 30, 1 h 52. Expect ~1.5-3 h per task, i.e.
**~1,000-2,000 SU for the set**. The ceiling is the 48 h Slurm cap × 5 = 30,720 SU, which
the per-deck `max_seconds = 165000` makes unreachable in practice.

**What lands.** Rows 1-2 are the two remaining GATE-1 UNVERIFIED children; if both
converge, the GATE-1 census goes 38 AGREE / 0 REFUSED / **0 UNVERIFIED**. Rows 3-5 test
whether a manufactured density with a fresh Broyden history rescues the STALLED rows —
a negative result there is now interpretable, because the only difference from the run
being remedied is the starting density.

Still not launched and still Frank's: **R1** (`upscale`) and **R2** (`electron_maxstep`
500 → 1500 on `Co s0_O__2x1v_mir` alone), plus `Ni s0_OOH__2x1v_off`, which is gated on
R1 because its only viable density source is its own mirror arm.

### Round 4 chain 1 RESULT (2026-08-25): the replay found a state 76.7 meV BELOW the banked parent, and this INVERTS the chain-1 reading above

`20135148_1` completed in 40:31. The three numbers, `Co s0_O__1x1_off`:

| | E (Ry) | vs banked parent | BFGS steps | final magtot |
|---|---|---|---|---|
| **banked parent** | −2330.66171228 | — | 18 | 11.69 μB |
| replay | −2330.66734894 | **−76.69 meV** | 17 | 11.24 μB |
| child `__fp` (from replay density) | −2330.66737233 | **−77.01 meV** | 0 | 11.24 μB |

The child agrees with its density source to **−0.32 meV** — inside the ±1 meV A8.3 gate,
so density retention did exactly what it is supposed to do. What it agrees *with* is the
problem: both sit ~77 meV below the energy of record.

**The divergence is at the first SCF, before any ionic motion.** First `!` energies at the
identical starting geometry are −2330.65270105 (parent) and −2330.65844970 (replay),
**78.21 meV apart**. The magnetization trajectories are bit-identical for five iterations
and split at the sixth:

```
iteration    1      2      3      4      5      6
parent     26.07  26.74   6.61   8.70   8.67  12.71
replay     26.07  26.74   6.61   8.70   8.67  12.89   <- split
```

After that the two ladders relax in parallel, 18 vs 17 BFGS steps, offset by a nearly
constant 5.6 mRy the whole way down. This is **branch selection, not convergence**: no
tightening of `conv_thr` reaches it, because both branches are fully converged solutions.

Provenance consistent with the mechanism: the banked parent ran on **a081** (an earlier
attempt on a033), the replay on **a156**. `--bind-to` appears nowhere in the S3 launch
path — it is the **A8.6 undecided registration item** (docs/43:1668-1679, docs/48), so
mpirun binds at its own default and MPI reduction order is not pinned across nodes.
Five iterations of bit-identical arithmetic followed by a split is the signature of
floating-point non-associativity amplified by an unstable mixing trajectory.

#### Zero-SU audit: every repeated run of an identical deck in the repository

| deck | banked | repeat | ΔE (meV) | mag banked | mag repeat |
|---|---|---|---|---|---|
| `probe/Cr_lit3/oosh__1x1_off_magp` | −1636.57118655 | −1636.57118461 | +0.03 | 11.00 | 11.00 |
| `probe/Cr_lit3/s0_OOH__1x1_yaw90_magm` | −1636.56961270 | −1636.56965110 | −0.52 | 11.00 | 11.00 |
| `probe/Ni_basin/s0_OH` | −2599.99940826 | −2599.99940698 | +0.02 | 4.15 | 4.15 |
| `s3/Ni/s0_OH__2x1v_off` | −5157.23065359 | −5157.23065903 | −0.07 | 14.41 | 14.41 |
| **`s3/Ni/s0_O__1x1_off`** | −2598.63677322 | −2598.63335298 | **+46.53** | 4.33 | **8.01** |
| **`s3/Co/s0_O__1x1_off`** | −2330.66171228 | −2330.66734894 | **−76.69** | 11.69 | **11.24** |

The rule is clean and has no exceptions in six pairs: **when the magnetization matches,
the energy reproduces to ≤0.52 meV; when it differs, the energy differs by tens of meV.**
pw.x's arithmetic is reproducible here. Which magnetic solution the first SCF falls into
is not. Two of six repeated decks (33%) landed in a different branch.

#### Why this inverts the reading recorded above

The chain-1 (Ni) entry concluded that a branch-diverged replay *strengthened* the AGREE
verdict — "even a wrong-branch warm start finds the banked minimum at the parent geometry."
That held because in the Ni case the divergent branch was **higher** (+46.5 meV, mag 8.01)
and the child fell back out of it into the banked mag-4.3 state, matching the banked parent
to +0.019 meV.

The Co case is the mirror image and does not support that conclusion:

- the divergent branch is **lower**, not higher;
- the child **stays in it** rather than falling back;
- so the warm start did not find the banked minimum — it found a better one.

The Ni datum is consistent with "the banked parent is right and the divergent branch is a
metastable artifact." The Co datum says the banked parent **is** the metastable artifact,
for that deck. One instance of each means the prior sentence generalised from n = 1.

#### What this does to round 4 row 1

Row 1 does **not** close a GATE-1 UNVERIFIED. It converts one into a below-parent
question. The A8.3 letter — child reproduces the banked energy within 1 meV at the parent
geometry — is not satisfied at −77.01 meV; it is failed in the direction that says the
energy of record is too high. The GATE-1 census therefore does **not** go to 38 / 0 / 0 on
this array; row 2 (`Ni s0_OH__2x1v_off`, replay parity −0.07 meV, clean) can still close
its own.

**This is a third below-parent case and it belongs to R3**, alongside the Fe (−428.5 meV)
and Mn rows. It is the strongest of the three as evidence, and different in kind: Fe and
Mn came from `__basin` decks *built* to re-relax in a deeper state, so a deeper answer was
the expected outcome. Here **the parent's own deck, re-run unmodified, reached the deeper
state on its own.** That is not a different question being asked — it is the same question
returning a different answer.

Nothing is banked and nothing is decided here. R3 now covers three rows, and the entrant
call it needs has grown a second half: not only *which* energy is of record when a child
lands below its parent, but whether a banked relax whose deck is demonstrably branch-
unstable can stand on a single run at all. The related open items are **S0(h)** (RuO2
anchors run in the wrong magnetic state → ADOPT AFM, re-run owed), the docs/41
metastable-magnetic class, and **A8.6** (`--bind-to` undecided), which is no longer only a
performance question — it is the knob that decides reduction order, and reduction order is
what selected the branch here.

Round 4 continues: `20135148_2` (Ni A8.3, replay parity clean) and `_3`/`_4` (rung-(i)
self-seeds) running, `_5` pending. Cost so far ~417 SU.

### Round 4 rows 2-4 scored (2026-08-25). Row 2 is a textbook A8.3 success. Rows 3-4 FAILED, and the failure is partly a defect in how I built the seed.

#### Row 2 — `Ni s0_OH__2x1v_off__g1`: GATE-1 UNVERIFIED → AGREE

| | E (Ry) | mag | SCF iters | outcome |
|---|---|---|---|---|
| banked parent | −5157.23065359 | 14.41 | 250 | converged |
| replay | −5157.23065903 | 14.41 | 249 | **−0.07 meV** vs banked |
| child, cold start (3rd attempt, `.retry_ms`) | — | **12.24** | 500 | NOT_ACHIEVED |
| child `__fp`, from parent density | −5157.23065325 | **14.41** | **12** | **+0.005 meV** vs banked |

A child that failed three cold-start attempts converged in **12 iterations** from the
parent's density and reproduced the banked energy to **5 μeV**. Note the cold start was
also in the wrong magnetic branch (12.24 vs 14.41 μB) and the density fixed that too —
the same branch-selection mechanism as the Co row, here caught and corrected rather than
banked. This is the A8.3 remedy working exactly as written.

#### Rows 3-4 — rung (i) self-seed FAILED, and it could not have succeeded

| deck | phase | min acc | @it | last | n | outcome |
|---|---|---|---|---|---|---|
| `Co s0_OH__2x1v_mir` | cold | 6.37e-6 | 246 | 8.80e-5 | 500 | FAILED |
| `Co s0_OH__2x1v_mir` | **fromseed** | 7.92e-6 | 152 | 4.40e-4 | 500 | **FAILED** |
| `Co s0_OH__2x1v_off` | cold | 1.836e-5 | 491 | 1.851e-5 | 500 | FAILED |
| `Co s0_OH__2x1v_off` | **fromseed** | 1.893e-5 | 362 | 1.993e-4 | 500 | **FAILED** |

Both seeded runs reach essentially the same floor as their cold starts (within 25% and 3%)
and then drift *away* from it. The seeded runs are **less** stable, not more: the
magnetization span over the tail goes 0.08 → 0.25 μB for `s0_OH__2x1v_off`.

**The reason is a defect in `SEED_CONV_THR`, which is mine.** I set it to `1.0d-4` to
guarantee the seed step would converge, because a non-convergent replay aborts the whole
chain task at `44_chain.slurm`. But 1e-4 is **looser than the floor these decks already
reach unaided**:

| deck | floor reached cold | seed threshold | seed is looser by |
|---|---|---|---|
| `s0_OH__2x1v_mir` | 6.37e-6 | 1.0e-4 | **15.7×** |
| `s0_OH__2x1v_off` | 1.836e-5 | 1.0e-4 | **5.4×** |
| `s0_OOH__2x1v_off` | 1.132e-5 | 1.0e-4 | **8.8×** |

So the "good density" handed over was *worse* than where the cold run gets on its own. The
step threw information away. The feasibility assertion I added to the builder proved the
seed would converge; it never asked whether converging at that threshold was worth
anything. Those are different questions and I only encoded the first.

**Consequence for the hypothesis.** The ledger entry above attributed the STALLED rows to
"a saturated mixing history, not a physics problem" and rows 3-5 were built to test it.
They do **not** test it cleanly: the run changed two things at once — a fresh Broyden
history (helps) and a degraded starting density (hurts) — and came out flat. The saturated-
history hypothesis is therefore **untested, not refuted**. Recording it that way rather
than claiming a refutation.

**What is established.** `Co s0_OH__2x1v_off`'s cold run is a confirmed limit cycle, not a
slow descent: accuracy oscillates inside a 2% band (1.836e-5 … 1.875e-5) across its last
~30 iterations while the magnetization sits pinned at 24.24 ± 0.01 μB. The triage's
STALLED classification holds.

**And self-seeding is dead as a general remedy**, for a reason worth stating plainly:
*you cannot manufacture a better density from a run that cannot converge.* A self-seed's
ceiling is the failing run's own floor. It can only ever help when the loose threshold is
still tighter than where the cold run stalls, which is not this case and, by construction,
will rarely be. This does not touch the `Ni s0_OOH__2x1v_off` plan, whose seed is a
*different, converging* deck (its mirror arm) — cross-arm seeding is unaffected.

#### The clean test the ladder never ran — and this repo already knows the answer

`mixing_ndim` is the Broyden history depth. It is **unset in every S3 deck**, so QE's
default of 8 has been in force throughout — the same shape of omission as `upscale`. The
A8.4 ladder escalated `mixing_beta` three times (0.3 → 0.15 → 0.075) and never once
touched the history depth, which is the parameter the "saturated history" diagnosis
actually names.

The earlier R1 slab campaign in this repository did use it, in 26 decks:

| configuration | where | outcome |
|---|---|---|
| `mixing_ndim = 12`, `mixing_beta = 0.2`, `local-TF` | the standard shape (`Co_slab`, `Ni_slab`, stageA/stageB) | converged |
| **`mixing_ndim = 16`, `mixing_beta = 0.05`, `local-TF`** | **the "attempt4" escalation** | converged `Cr_slab/s0_OH`, `Mn_slab/s0_OOH`, `Co_slab/s0_O` |

So this project's own history has an escalation rung for exactly this failure mode on
exactly these metals, and S3 never used it. **Recommended as R5 (registered parameter,
Frank's call): add `mixing_ndim = 16` to the three STALLED decks, at the beta they already
carry or at the attempt4 pairing of 0.05.** It is one deck-line, it costs ~3 tasks, and
unlike the self-seed it varies the one thing the diagnosis points at. No doc in `docs/`
records a rationale for `mixing_ndim`, so the value would need registering rather than
inheriting.

#### Ledger

Task 5 (`Co s0_OOH__2x1v_off`) still running at the time of writing; its seed had not
handed over yet. It tests the same flawed seed design and is expected to fail the same
way — left to run because it is ~250 SU and a third consistent negative is worth having on
a pre-registered record. Balance 82,783.0 SU. Nothing from rows 3-5 is bankable; the row-2
child is the only new number of record, and it is an AGREE, not a new energy.

#### Row 5 — the seed itself failed, for a second and independent reason: loosening `conv_thr` loosens `ethr`

`20135148_5` ended `FAILED` at 02:14:50 with `CHAIN FAIL: replay non-convergent`. The
child never ran. I predicted in the entry above that row 5 would "fail the same way" as
rows 3-4 — it did not. Rows 3-4 failed at the child; row 5 failed at the **seed**.

`Co s0_OOH__2x1v_off.seed.out`: 500 iterations, `convergence NOT achieved`, best accuracy
**3.40e-4**, last 4.42e-3 — it never reached its own 1e-4 target and was wandering upward
when it stopped. The builder's feasibility assertion had predicted it would cross 1e-4 at
iteration 260.

**Why the prediction was invalid.** `conv_thr` does not only set the stopping criterion;
it sets the floor for `ethr`, the iterative-diagonalization accuracy. Measured, same deck,
same geometry:

| run | `conv_thr` | `ethr` floor reached |
|---|---|---|
| cold relax `s0_OOH__2x1v_off.out` | 1.0e-6 | **3.14e-9** |
| seed `s0_OOH__2x1v_off.seed.out` | 1.0e-4 | **9.43e-8** (30× looser) |

and the trajectories separate accordingly:

| run | it 50 | it 150 | it 300 | min |
|---|---|---|---|---|
| cold relax (1e-6) | 1.05e-3 | 2.16e-4 | 3.22e-5 | **1.13e-5** |
| seed (1e-4) | 1.33e-3 | 6.10e-3 | 2.92e-3 | **3.40e-4** |

The cold run descends; the seed run gets *worse* after iteration 50 and never recovers. A
30× looser diagonalization floor cannot resolve the near-degenerate states this system
sits on, so the SCF that a tighter `conv_thr` was successfully descending simply stops
descending.

This is the mirror image of the `upscale` finding. There, an unset parameter silently
**tightened** `conv_thr` during relax and made runs look like failures when they had met
the registered criterion. Here, deliberately **loosening** `conv_thr` broke a run that
was otherwise progressing. In both cases the lesson is the same: in QE, `conv_thr` is not
an isolated stopping rule — it propagates into the accuracy of the machinery underneath it.

**The precise bug in my feasibility assertion**, for the lessons file: it predicted the
seed run's behaviour from the *cold relax's* accuracy history. But that history was
produced at a 30× tighter `ethr` floor. A 1e-4 run and a 1e-6 run of the same deck are
not the same dynamical system, so one's trace cannot certify the other's. The assertion
tested "does a trajectory exist that crosses 1e-4" when the question was "does *this*
trajectory converge."

#### Round 4 final tally — array 20135148, 1,132.8 SU (83,845.8 → 82,713.0)

| row | deck | result |
|---|---|---|
| 1 | `Co s0_O__1x1_off` A8.3 | chain ran clean; replay + child **−77 meV below the banked parent** in a different magnetic branch → **R3 below-parent case, does NOT close GATE-1** |
| 2 | `Ni s0_OH__2x1v_off` A8.3 | **AGREE +0.005 meV**, converged in 12 iterations from the parent density, correct branch → **GATE-1 UNVERIFIED → AGREE** |
| 3 | `Co s0_OH__2x1v_mir` rung (i) | FAILED at the child — seed density looser than the cold floor |
| 4 | `Co s0_OH__2x1v_off` rung (i) | FAILED at the child — same |
| 5 | `Co s0_OOH__2x1v_off` rung (i) | **FAILED at the seed** — loose `conv_thr` → 30× loose `ethr` |

One row of five did what the manifest said it would. The other four are informative
rather than productive: one produced a finding that outranks the round's stated purpose
(branch instability in the banked ladder), and three retired the self-seed idea for good.

**A8.8 status: clean.** Row 5's child deck `s0_OOH__2x1v_off.fromseed.in` never ran and
its `.out` slot is free; no banked result was touched by any row.

**Housekeeping:** `44_chain.slurm` deliberately keeps scratch on `CHAIN FAIL`, so
`runs/s3/Co/tmp_chain_s0_OOH__2x1v_off__fs` (**5.6 GB**) is still on `$PROJECT`. It holds
the seed's non-converged density and has no diagnostic value the `.out` does not already
carry. `$PROJECT` is at 28.7 GB of 5 TB so there is no pressure, and the runner `rm -rf`s
the path at the start of any re-run — left in place rather than deleted unprompted.

---

## Round 5 scored — array 20141568 (2026-08-25/26). `mixing_ndim = 16` works, and one Anvil node destroyed a third of the round.

Launched 2026-08-25 17:16 UTC, 11 tasks, `--array=1-11%4`, `EXCLUDE=a024,a088`.
Balance 82,713.0 → 81,204.0 SU with three tasks still live.

| # | row | node | result |
|---|---|---|---|
| 1 | `Co s0_O__2x1v_mir` ndim16 + maxstep 1500 | a192 | RUNNING — see R2 below |
| 2 | `Co s0_OH__2x1v_mir` ndim16 | a195 | **CONVERGED**, 18 BFGS steps, scf 8.5e-09 |
| 3 | `Co s0_OH__2x1v_off` ndim16 | **a196** | OUT_OF_MEMORY — infrastructure, no science |
| 4 | `Co s0_OOH__2x1v_off` ndim16 | a201 | FAILED, first SCF never converged |
| 5 | `Ni s0_OOH__2x1v_mir` ndim16 | **a196** | OUT_OF_MEMORY — infrastructure, no science |
| 6 | `Ni s0_OOH__2x1v_off` ndim16 | **a196** | OUT_OF_MEMORY — infrastructure, no science |
| 7 | `Mn s0_OOH__2x1v_off__basin` ndim16 | **a196** | CANCELLED by me — hung 1h44m, see below |
| 8 | `Co ref__2x1v__g1` | a117 | RUNNING |
| 9 | `Co s0_OH__1x1_off__g1` | a201 | **AGREE +0.026 meV** |
| 10 | `Co s0_OOH__2x1v_mir__g1` | a201 | BRANCH MISMATCH +747.4 meV |
| 11 | `Fe s0_OOH__1x1_off__basin__g1` | a091 | BRANCH MISMATCH +7.4 meV |

### The one-line fix worked, and it is a clean controlled experiment

`Co s0_OH__2x1v_mir` had failed three cold attempts and a staged self-seed. With
`mixing_ndim = 16` it converged in 18 BFGS steps to a final scf accuracy of **8.5e-09**.
QE echoes the parameter, so the control is visible in the outputs themselves:

| | `number of iterations used` | mixing | threshold | outcome |
|---|---|---|---|---|
| `.out.attempt3` | **8** local-TF | beta 0.15 | 1.0e-06 | 500 iters, NOT achieved |
| `.out` (round 5) | **16** local-TF | beta 0.15 | 1.0e-06 | **bfgs converged** |

Same threshold, same beta, same mixing mode, same geometry. The Broyden history depth is
the only difference and it is the difference between failure and 8.5e-09. This is the rung
the A8.4 ladder never had: it escalated `mixing_beta` three times (0.3 → 0.15 → 0.075) and
never touched the depth, which is the parameter the "saturated history" diagnosis names.
The saturated-history hypothesis, recorded as **untested** after round 4 confounded it, is
now **supported** — by the test that varies only the one thing.

`Co s0_OOH__2x1v_off` (row 4) had the same treatment and still failed: one SCF cycle,
500 iterations, last accuracy 2.0e-3. ndim=16 is not universal. Its next rung is the
attempt-4 pairing from the R1 slab campaign, `mixing_beta` 0.15 → 0.05, which is the only
part of that pairing still untried.

### Row 1 answers R2 in the negative, and reclassifies its own triage

`Co s0_O__2x1v_mir` was the single deck triaged **SLOW**, and the maxstep 500 → 1500 rider
was built to ask whether it merely needed more room. At 746 iterations it has its answer:

| | min accuracy | at iteration | behaviour after |
|---|---|---|---|
| `.out.attempt3` (ndim 8, maxstep 500) | 4.287e-05 | — | flat |
| `.out` (ndim 16, maxstep 1500) | **1.628e-05** | ~100 | drifts *up*, now ~3.5e-04 |

ndim=16 bought a 2.6× lower floor and still fell 16× short of 1e-6, then wandered away from
its own minimum for 640 iterations. **The deck is STALLED, not SLOW** — the triage
misclassified it, and the extra 1000 iterations are being spent to establish that rather
than to converge it. Left running deliberately: it is a pre-registered test on a healthy
node and stopping it early because the answer looks obvious is precisely the move this
campaign's discipline exists to prevent. Cost of finishing ≈ 384 SU.

### Node a196 cost four rows and ~430 SU, and it is Slurm's own diagnosis

Tasks 3, 5, 6 all died `OUT_OF_MEMORY` (exit 0:125) on **a196**, at MaxRSS 8.65–8.70 GB —
while the round's *healthy* runs peaked at 30.8–46.8 GB. They were not using too much
memory; they were killed early on a node that had none to give:

```
NodeName=a196  State=ALLOCATED+DRAIN  CPULoad=166.18  RealMemory=257400  FreeMem=384
Reason=NHC: Terminated by signal SIGTERM. [root@2026-08-25T19:55:48]
```

A 128-core node at load 166 with **384 MB free**, drained by Purdue's own node health check
during our array. Task 7 (`Mn s0_OOH__2x1v_off__basin`) was still scheduled onto it, wrote
a 9,912-byte header and then produced **zero SCF iterations in 1h45m** — the identical
header-only signature (9,905 / 9,912 / 9,986 bytes) as its two OOM'd siblings, which had
already been reaped. I cancelled it. It had 46 h of walltime left and would have burned
~5,900 SU producing nothing.

This is not a science result and none of these four rows tell us anything about
`mixing_ndim`. They re-run unchanged.

**Consequence for the RCAC ticket** (`anvil/rcac_ticket_draft_2026-08-24.md`, still
unsent): the draft rested on a024/a088 sitting `MIXED` in the pool, which is suggestive but
circumstantial. a196 is not circumstantial — it is a drain reason string, a timestamp inside
our array, three OOM kills at an eighth of normal usage and a fourth job hung to a
standstill. **a196 joins the EXCLUDE list**, and the ticket now has a concrete incident to
report rather than an anomaly to describe.

### The `__g1` children: the branch rule holds at 9 pairs and has still never failed

| stem | ΔE (meV) | Δmagtot | Δmagabs | verdict |
|---|---|---|---|---|
| `Co s0_OH__1x1_off` | **+0.026** | +0.00 | +0.00 | **AGREE** |
| `Co s0_OOH__2x1v_mir` | +747.449 | **+4.73** | +3.70 | BRANCH MISMATCH |
| `Fe s0_OOH__1x1_off__basin` | +7.395 | **+4.00** | +0.03 | BRANCH MISMATCH |

Round 4's audit established the rule over six repeated-deck pairs: *magnetization matches →
energy reproduces to ≤0.52 meV; magnetization differs → tens of meV.* These three are the
seventh, eighth and ninth pairs and the rule survives all of them. It is now the single
most reliable regularity in this campaign, and it is the reason a `__g1` child must never
be scored on energy alone.

The Fe row is worth reading closely. Δmagtot is **exactly +4.00** while Δmagabs is +0.03 —
the local moments are unchanged in size and roughly 2 μB of moment has flipped from down to
up. That is not a convergence artifact; it is a *different magnetic configuration at the same
geometry*, 7.4 meV away. The Co row, at +4.73/+3.70 and 747 meV, is a genuinely different
and much worse state.

Neither is a GATE-1 refusal of the banked energy. Both are cold SCF starts landing in the
wrong basin, which is exactly the failure the A8.3 density-retention remedy exists for and
exactly what it fixed for `Ni s0_OH__2x1v_off__g1` in round 4 (three cold failures and the
wrong branch at 12.24 vs 14.41 μB → 12 iterations from the parent density and +0.005 meV).
Both parents are banked and converged, so both children get that remedy in round 6.
No parent `.save` survives, so each needs the full replay: ≈371 SU (Co, 2h39m parent) and
≈111 SU (Fe, 47m parent).

### Round 5 net

**Two rows of eleven produced a bankable answer** — row 2's convergence and row 9's AGREE.
Four were destroyed by hardware. Two are branch mismatches with a known remedy. One is a
real negative (row 4). Two are still running.

The round's purpose was to test one hypothesis with one deck-line, and on the rows that
were allowed to run it did: **`mixing_ndim = 16` converged a deck that four previous
attempts could not, with every other parameter held fixed.**

**A8.8 status: clean.** Round 5's dead `.out` files land on filenames whose previous
contents were already archived to `.out.attempt<N>` before launch. Nothing banked was
touched. The four re-runs and row 4's new rung will archive their round-5 `.out` the same
way before they start.

---

## Round 6 scored — arrays 20143254 + 20143262 (2026-08-26). `mixing_ndim = 16` does NOT generalise, and the retry ladder has been discarding real work.

Round 5's remnants and all of round 6 are now terminal. Balance 81,204.0 → **79,275.4 SU**
(1,928.6 spent).

### Correction to the round-5 entry above

That entry called `mixing_ndim = 16` a confirmed fix and said the saturated-Broyden
hypothesis was "now supported". The narrow claim stands — `Co s0_OH__2x1v_mir` converged
with the history depth as the only change from a failed attempt at identical beta,
threshold and mixing mode. **The general claim does not.** With five more decks tested at
ndim = 16, the score is **1 converged of 6**:

| deck | ndim 16 result | min accuracy | best prior |
|---|---|---|---|
| `Co s0_OH__2x1v_mir` | **CONVERGED** 8.5e-09 | — | 6.37e-06 |
| `Co s0_O__2x1v_mir` (+maxstep 1500) | failed | 1.628e-05 | 2.833e-05 |
| `Co s0_OH__2x1v_off` | failed | 2.470e-05 | 1.836e-05 (**worse**) |
| `Ni s0_OOH__2x1v_off` | failed | 6.523e-05 | 2.555e-03 |
| `Co s0_OOH__2x1v_off` (+beta 0.05) | failed | 9.26e-06 | 1.132e-05 |
| `Mn`, `Ni ..._mir` | lost to node a220 | — | — |

I generalised from one row. The honest statement is that ndim = 16 fixed one deck, helped
two, and made one worse.

### The finding that matters: the ladder has been throwing away converged ionic steps

Scoring the failures by *ionic* progress rather than by SCF accuracy changes the picture
completely. Counting completed BFGS steps across every attempt of each failing deck:

| deck | attempt1 | attempt2 | attempt3 | attempt4 | attempt5 | round 6 |
|---|---|---|---|---|---|---|
| `Co s0_OOH__2x1v_off` | 0 | **14** | 0 | 0 | 0 | 0 |
| `Ni s0_OOH__2x1v_off` | 0 | **1** | 0 | 0 | 0 | 0 |
| `Ni s0_OOH__2x1v_mir` | 2 | 2 | **3** | 0 | — | — |
| `Mn s0_OOH__2x1v_off__basin` | **19** | 0 | — | — | — | — |
| `Co s0_O__2x1v_mir` | 0 | 0 | 0 | **0** | — | — |
| `Co s0_OH__2x1v_off` | 0 | 0 | 0 | 0 | **0** | 0 |

`Co s0_OOH__2x1v_off` got **14 converged ionic steps** on its second attempt, at the
*original* `mixing_beta = 0.3`. Every rung of the A8.4 ladder since — beta 0.15/200, beta
0.15/500, ndim 16, ndim 16 + beta 0.05 — restarted from the ORIGINAL geometry and got
stuck in the first SCF. Four escalations and roughly 1,000 SU were spent re-running the
hardest step of a trajectory whose 14th step was already sitting in an archived file.

**This is a defect in my own builder, not just in the ladder.** `build_s3_round5.py`
splices from `job + '.out'` — the most recent attempt — and never scans
`job + '.out.attempt*'`. It happened to be right for Mn (19 steps, attempt1, which was
still the current `.out` at the time) and for `Ni ..._mir` (3 steps, attempt3), and wrong
for the one deck where the deepest attempt had been archived several rungs earlier.

### And attempt2 was not a mixing failure at all

When `Co s0_OOH__2x1v_off` attempt2 stopped, it had completed 14 ionic steps and QE was
holding it to **`new conv_thr = 4.10e-8`** — the unset `upscale` (default 100) tightening
the registered 1e-6 by a factor of 24 — with the run having reached 3e-8. It failed the
15th cycle against a threshold it never agreed to.

That is the **UNREG_THR** mechanism, and it means the row was triaged into STALLED on the
evidence of later attempts that had been crippled by starting over. `Ni s0_OOH__2x1v_mir`
is the same shape: 3 ionic steps, held to 2.79e-7, reached 3.2e-7. **R1 — declare
`upscale` — remains the cleaner fix for these rows and is still Frank's call.** Round 7
does what can be done without a ruling.

### Two decks have never completed a single ionic step

`Co s0_O__2x1v_mir` (4 attempts at 200/200/500/1500 iterations) and `Co s0_OH__2x1v_off`
(5 attempts) have **zero** ionic steps between them. There is no geometry to resume from
and the mixing ladder is exhausted. These need R1, a new registered call (starting
magnetization, diagonalization algorithm), or acceptance as an A8.4 rung-(iii)
NOT_CONVERGED gap. Not built into round 7.

R2 is also answered, in the negative: `Co s0_O__2x1v_mir` ran the full 1500 iterations,
reached its minimum near iteration 100 and drifted upward for the remaining 1400. **The
deck was misclassified SLOW; it is STALLED.**

### The chains: one clean closure, one reproducibility failure

**`Fe s0_OOH__1x1_off__basin` — GATE-1 CLOSED.**

| | E (Ry) | magtot | magabs | vs banked |
|---|---|---|---|---|
| banked parent | −2558.16677357 | 22.98 | 27.59 | — |
| replay | −2558.16677716 | 22.98 | 27.59 | **−0.049 meV** |
| child `__fp` | −2558.16677325 | 22.98 | 27.59 | **+0.004 meV** |

A +7.395 meV branch mismatch closed to **4 μeV** with the magnetization identical across
all three runs. This is the A8.3 remedy working exactly as designed, and it is the second
clean demonstration after `Ni s0_OH__2x1v_off__g1` in round 4.

**`Co s0_OOH__2x1v_mir` — CHAIN FAIL: replay non-convergent.** The parent's own deck,
re-run unmodified, reproduced the parent's magnetization trajectory bit-for-bit for three
values (53.79 / 55.78 / 25.00) and then **failed to converge at all**: 500 iterations in
cycle 1, min 2.477e-5, ending at magtot 19.98. The parent converged cycle 1 in 135
iterations and completed 22 cycles.

This is round 4's branch instability with a worse outcome. There, the replay found a
*different* converged solution; here it finds *no* converged solution. **`Co
s0_OOH__2x1v_mir`'s banked energy currently cannot be reproduced on demand**, which is
directly R3's second half — whether a banked relax whose deck is demonstrably unstable
can stand on a single run — and another argument for settling A8.6 (`--bind-to`).

### The fourth `__g1` child also failed

`Co ref__2x1v__g1` (round 5 task 8, 3h10m): 500 iterations, no convergence, magtot **24.11**
against the parent's 21.66. Wrong branch and no fixed point. Its parent is banked and
converged, so it takes the A8.3 remedy in round 7. Wave-4 children stand at **2 closed of
4** — `Co s0_OH__1x1_off` (+0.026 meV) and `Fe s0_OOH__1x1_off__basin` (+0.004 meV).

### Node a220 — a fourth bad node, and a different shape from a196

Round 6 lost two rows to `OUT_OF_MEMORY` on **a220**, at MaxRSS **35.1 GB** against a
granted `mem=237G`. Unlike a196, a220 shows no DRAIN and no NHC record — `State=MIXED`,
`CPULoad=4.35`, 32 GB free when checked afterwards. It is the a024/a088 shape: silently
bad, still in the general pool.

Checked and ruled out: our own array tasks were **not** co-scheduled. Every task on both
a196 and a220 started within ten seconds of the previous one *ending* on that node, so the
kills are not our jobs colliding with each other.

The branch rule is now **10 for 10** with the Fe chain: matching magnetization reproduces
the energy to ≤0.52 meV; differing magnetization differs by tens to hundreds of meV.

---

## Round 7 scored — arrays 20148093 + 20148101 (2026-08-26). Resuming from the deepest geometry converged a deck six attempts could not.

### The result the round was built to test

**`Co s0_OOH__2x1v_off` CONVERGED.** `bfgs converged`, 22 ionic steps, no NOT-achieved
cycle, min accuracy **3.9e-09** against a final `new conv_thr` of 1.0e-08, in **1h34m**
(≈201 SU) on a157.

| | E (Ry) | ionic steps | outcome |
|---|---|---|---|
| attempt2 (base deck, beta 0.3) | −4662.65158111 | 14 | stopped at `new conv_thr = 4.10e-8` |
| attempts 3–6 (the A8.4 ladder) | — | **0 each** | stuck in the first SCF |
| **round 7 resume** | **−4662.68039155** | **22** | **converged** |

The resumed run descended a further **392 meV** below attempt2's last banked ionic energy,
so those 14 steps were genuinely partway rather than nearly done. Six attempts and roughly
1,000 SU of mixing escalation failed on this deck; resuming it from the geometry it had
already reached converged it on the first try at the *original* `mixing_beta = 0.3`.

This confirms the round-6 diagnosis in the strongest form available: **the deck was never a
mixing problem. It was a restart problem.** The A8.4 ladder had been re-running the hardest
step of a trajectory that was most of the way down.

### Round 7's chain 1 makes the `Co s0_OOH__2x1v_mir` reproducibility failure worse

Adding `mixing_ndim = 16` to the replay did not rescue it — it made it worse:

| replay | ndim | min accuracy | outcome |
|---|---|---|---|
| round 6 | 8 (default) | 2.477e-05 | 500 iterations, no convergence |
| round 7 | 16 | **4.24e-04** | 480+ iterations, wandering (5.5e-3 → 9.8e-3 → 6.6e-3 → 1.2e-2) |

**Two independent replays of that parent's own deck have now failed to converge at all.**
This is no longer a convergence-tuning problem to escalate: the banked energy for
`Co s0_OOH__2x1v_mir` cannot be reproduced on demand, which is R3's second half and a
direct argument for settling A8.6 (`--bind-to`). Not re-run in round 8.

### Node a223 — the fifth, and the measurement that identifies the fault

Four of round 7's six rows died `OUT_OF_MEMORY` on **a223**. The kills are not random:

| node | tasks killed | MaxRSS at kill | spread |
|---|---|---|---|
| a196 | 3 | 8.65 / 8.66 / 8.70 GB | 0.5 % |
| a220 | 2 | 35.06 / 35.14 GB | 0.24 % |
| a223 | 4 | 16.93 / 16.94 / 16.95 / 16.95 GB | **0.1 %** |

Each bad node kills at its own tight ceiling. Every one of these jobs was granted
`mem=237G`, and the same work on a healthy node peaks at 30–48 GB and finishes —
`20148093_3` peaked at **47.7 GB** on a157 and converged while its three siblings died on
a223 at 16.9 GB. A repeatable 16.94 GB kill under a 237 GB grant is a **per-node shortfall
between the memory Slurm believes is allocatable and the memory the node can deliver**, not
a footprint problem on our side.

Five nodes are now excluded (a024, a088, a196, a220, a223) and each of the last three
submissions has found a new one, so exclusion is not converging. Running tally: roughly
**1,100 SU lost to kills**, plus the ~5,900 SU the a196 hang would have burned unattended.

**Deliberately NOT mitigated by shrinking the job.** The obvious lever is `-nk` pooling,
which would cut memory several-fold. It also changes the parallel decomposition and
therefore MPI reduction order — and round 4 established that reduction order is what selects
the magnetic branch here. Changing it on production rows to dodge a cluster fault would
trade a scheduling problem for a physics one. `disk_io` is the one memory knob that cannot
move a number, and it is held in reserve.

The RCAC ticket draft now leads with the ceiling table.

### Round 8 launched — arrays 20149862 (wave, 3 rows) + 20149866 (chain, 1)

Pure re-runs of what a223 killed, decks unchanged, `EXCLUDE=a024,a088,a196,a220,a223`.
Preflight `lines=3 to_run=3 already_done=0 stale=0 bad=0`. The chain is the last owed
wave-4 child, `Co ref__2x1v__g1`.

**A8.8 note:** `runs/s3/Co/ref__2x1v.out` is the **banked parent** (1,847,613 B) and was
explicitly excluded from the archive step — the chain's dead file is
`ref__2x1v.replay.out` (10,131 B), archived to `.replay.out.attempt1`. Both the banked
parent and the newly converged `s0_OOH__2x1v_off.out` were verified intact afterwards.

---

## Round 8 scored — arrays 20149862 + 20149866 (2026-08-26). The second resume win, and the replay failures are real.

Balance 79,275.4 → **77,052.1 SU** (2,223.3 spent). All three wave rows completed with **no
OOM** — the five-node exclude list held.

### `Ni s0_OOH__2x1v_off` CONVERGED — the row that had no remedy

**41 ionic steps, `bfgs converged`**, min accuracy 5.0e-09 at the 1e-08 upscale floor,
E = −5198.77050468 Ry, magtot 7.89 / magabs 22.05.

This is the row `runs/chains/m_round4.txt` recorded as *"BRANCH, no parent to seed from —
the one row with no registered remedy in hand; A8.4 rung-(iii) NOT_CONVERGED gap candidate."*
It had **one** banked ionic step, in attempt2, which four later rungs discarded. Resuming
from that single step ran 41 more and converged. It never needed a remedy; it needed a
restart.

Two for two on the resume recipe, on decks that between them survived ten failed attempts.

### The two that did not finish, and why they differ

**`Mn s0_OOH__2x1v_off__basin` is working.** It picked up attempt1's 19th step
(−3617.10180292) and carried it three further to **−3617.10197097** at identical
magnetization (34.76 / 47.87), converging every SCF cycle to the 1e-08 floor (min 6.0e-09).
It stopped in cycle 4. It just needs more ionic steps.

**This breaks the round-7 selector, and the builder now says so.** `deepest_attempt()`
chose by *most ionic steps*, which would pick attempt1 (19) over the round-8 run (3) and
silently discard three steps — because **once resumes chain, step count stops tracking
depth**. `build_s3_round9.py` selects by *lowest final energy within a magnetic branch* and
asserts no same-branch run is deeper than the one chosen. Its census output makes the choice
auditable:

```
s0_OOH__2x1v_off__basin.out            ionic=3   E=-3617.10197097  mag=34.76   <- chosen
s0_OOH__2x1v_off__basin.out.attempt1   ionic=19  E=-3617.10180292  mag=34.76
```

**`Ni s0_OOH__2x1v_mir` was hurt by `mixing_ndim = 16`**, and the history is one-way:

| run | ndim | ionic | final magtot | magabs | min accuracy |
|---|---|---|---|---|---|
| attempt1 | 8 | 2 | 9.87 | 20.54 | 7.3e-07 |
| attempt2 | 8 | 2 | 13.72 | 19.21 | 3.8e-07 |
| attempt3 | 8 | 3 | 13.78 | 19.34 | 3.2e-07 |
| round 8 | **16** | **0** | **−0.27** | 25.70 | 2.2e-04 |

At ndim 8 it sat in a 9.9–13.8 μB branch and descended to 3.2e-07 against an
upscale-tightened 2.79e-07 — an UNREG_THR row that is nearly there. At ndim 16 it collapsed
into a near-compensated state (magtot −0.27 with magabs 25.70: large moments cancelling) and
completed no ionic steps at all. Round 9 resumes it from attempt3 **using attempt3's own
deck**, i.e. with ndim removed.

Running score for `mixing_ndim = 16`: **1 converged of 7**, and now two decks made
measurably worse. It is not a general remedy and should not be added to further decks
without a specific reason.

### `Co ref__2x1v`'s replay failed too — but it is SLOW, not STALLED

Round 8's replay of the last owed wave-4 child's parent did not converge, but it was still
descending monotonically when it hit the iteration wall:

```
... 4.56e-06  4.52e-06  4.45e-06  4.04e-06  3.81e-06   <- iteration 500, target 1e-06
```

The banked parent converged cycle 1 in **324** iterations; the replay was at 3.81e-06 after
500. Same first-three magnetization values as the parent (58.53 / 59.99 / 20.08), diverging
at the fourth (54.82 vs 54.81) — the familiar reduction-order split, here costing
convergence speed rather than the branch. Round 9 re-runs it at `electron_maxstep = 1500`,
changing exactly two lines from the parent deck (prefix, maxstep).

### A cheap explanation, tested and discarded

Before building round 9 I checked whether the banked parents had been **warm started** from
leftover scratch — which would have explained every replay failure at once and put the
banked numbers' provenance in question. It is false. Both parents and all replays report
`Initial potential from superposition of free atoms`, and `anvil/42_s3_wave1.slurm` line 59
`rm -rf`s the scratch directory before every job. **The parents are genuine cold starts and
the replay failures are real.**

### Round 9 launched — 20150995 (wave, 2 rows) + 20151000 (chain, 1)

`EXCLUDE=a024,a088,a196,a220,a223`, preflight `lines=2 to_run=2 ... bad=0`, 5 files
md5-verified. Both splices reproduce their source `.out` block with **zero frozen atoms
moved**; the Ni splice shows one atom differing by 1e-09 / 5e-09 Å, which is the deck's
8-decimal format against the output's 10 — a rounding artifact at the tolerance boundary,
not a defect.

**Still open and Frank's:** `Co s0_OOH__2x1v_mir` (two replays failed, ndim made it worse —
R3/A8.6); `Co s0_O__2x1v_mir` and `Co s0_OH__2x1v_off` (zero ionic steps ever, no geometry
to resume from — R1 or a new registered call); R1 `upscale` itself, which would directly
close `Ni s0_OOH__2x1v_mir` and `Co s0_OOH__2x1v_off`-class rows.

## Round 9 scored, and the diagnosis inverted -- arrays 20150995 (wave, 2) + 20151000 (chain, killed)

Round 9 returned two wave rows and one chain that had to be killed. Scoring them
truthfully required re-measuring the whole S3 tree, and that re-measurement
overturned three things this ledger has been asserting, including one I asserted
earlier the same day. The corrections are set out at the end of this section.

### What the two wave rows did

`Mn s0_OOH__2x1v_off__basin` -- **converged, in the wrong branch, and should be
refused.** 13 ionic steps, `bfgs converged`, JOB DONE, notconv 0, minimum SCF
accuracy 3.3e-09. But magtot sits at **35.00** for all 13 steps against the
34.76 of the trajectory it was spliced from, and its step 1 came back at
-3617.09797298 against attempt5's step-3 -3617.10197097 -- **+54.395 meV at
essentially the same geometry**, one BFGS step apart. A descending BFGS step
cannot raise the energy by 54 meV, so the branch changed at step 1. Its final
energy is +39.167 meV above attempt5's and +36.880 meV above attempt1's.

Under A8.3 (`docs/43:1589-1592`), a result landing more than 1 meV above is
**refused**, not banked. This one is 39x that. It is not the continuation it was
asked for and it does not supersede the 34.76 numbers.

`Ni s0_OOH__2x1v_mir` -- **failed, informatively.** Resuming from attempt3's own
geometry with attempt3's own deck collapsed magtot from 27.94 to 3.23 inside 41
iterations, then oscillated between 1.37 and 2.16 for the remaining ~460 and
completed no ionic step. Best accuracy 2.2e-04.

### The chain was killed at 9 h 50 m, and killing it was right

`Co ref__2x1v`'s replay at `electron_maxstep 1500` reached ionic step 3 in 9 h
50 m (~1250 SU) and was heading for the 48 h wall (~6144 SU). Its step-1 SCF is
bit-identical to the banked parent's for three iterations (58.53, 59.99, 20.08)
and splits at **iteration 4 of 325** -- 496 iterations before `electron_maxstep
= 500` could ever bind. So the raised maxstep was not the operative variable and
never could have been. By step 3 it sat 110.839 meV **above** the banked energy
of record at magtot 23.60 against 21.66.

`docs/43:1584-1588` already rules on exactly this shape: a fixed-geometry re-run
sitting *above* its own relaxed parent is "backwards, **so it is a diagnostic,
not a result**". The chain could not have produced a scoreable child, because
the child would have been measured against a replay that is not the parent.
Killed; the replay output is preserved as `ref__2x1v.replay_ms.out.attempt1`
(1,320,015 B). The banked parent `ref__2x1v.out` is untouched at 1,847,613 B,
md5 `0a81fd3a86484b988c4fb476fbcf2521`.

### GATE-1 measured across all 35 pairs on disk

A GATE-1 child is an `scf` at its parent's final relaxed geometry, so child and
parent are at byte-identical coordinates by construction and every pair is an
exact replicate. Measured over all 35:

| population | n | min \|dE\| | median | max |
|---|---|---|---|---|
| dmagtot <= 0.01 | 29 | 0.0007 meV | 0.004 meV | **0.044 meV** |
| dmagtot >= 0.18 | 6 | **7.394 meV** | 78 meV | 747 meV |

**Zero overlap; the gap is a factor of 168.** Magnetization agreement is not
merely correlated with energy agreement, it is equivalent to it. The branch rule
is no longer a tally of anecdotes -- it is a measured bimodal separation with
the decision boundary anywhere in [0.044, 7.394] meV. The 0.05 uB tolerance in
use sits inside the empty gap and is therefore not a tuned number.

### Three banked parents are in an EXCITED magnetic branch

Of the six mismatches, three have the child **below** its parent, at the
parent's own geometry, with both sides converged (notconv 0) and geometry
verified byte-identical to full precision, 0 differing atoms:

| row | parent E (Ry) | child E (Ry) | child - parent | magtot parent -> child |
|---|---|---|---|---|
| `Fe s0_OOH__1x1_off` | -2558.13528265 | -2558.16352817 | **-384.300 meV** | 24.46 -> 22.98 |
| `Co s0_O__1x1_off` | -2330.66171228 | -2330.66737233 | **-77.009 meV** | 11.69 -> 11.24 |
| `Mn s0_OOH__2x1v_off` | -3617.09868891 | -3617.10020414 | **-20.616 meV** | 35.00 -> 34.82 |

This is the pre-registered BASIN_DRIFT case, and the protocol already says what
happens next (`docs/43:311-314`): "If that SCF lands >= 5 meV lower, the state is
re-relaxed from it and the loop repeats until GATE-1 passes", with the GATE-1
SCF energy becoming the corrected value (`docs/43:787-790`). All three clear the
5 meV trigger by 4x, 15x and 77x. Every dG computed from those three parents
inherits the error; the Fe row at 0.384 eV is larger than the overpotential
differences the study exists to resolve.

Note this contradicts the campaign census recorded at `docs/45:255-256`
("38 AGREE / 0 REFUSED / 2 UNVERIFIED"). Reconciling the two is owed.

### THE HEADLINE: the retry ladder has been chasing an undeclared threshold

QE's `upscale` (an `&IONS` variable, default 100, never set in any deck)
silently tightens `conv_thr` between ionic steps toward a 1e-08 floor. Every S3
deck registers `conv_thr = 1.0d-6`. Measured directly from the raw iteration
traces of the three rows that have consumed the retry ladder:

| run | failing cycle | iterations burned | min accuracy reached | threshold actually in force | iterations that MET the registered 1.0e-06 | first at |
|---|---|---|---|---|---|---|
| `Ni s0_OOH__2x1v_mir` att3 | 4 | 500 | 3.2e-07 | 2.791e-07 | **40** | iter 52 |
| `Mn s0_OOH__2x1v_off__basin` att1 | 20 | 200 | 5.0e-07 | 1.0e-08 | **124** | iter 11 |
| `Mn s0_OOH__2x1v_off__basin` att5 | 4 | 500 | 6.0e-08 | 1.0e-08 | **489** | iter 9 |

Read the last two columns. **Each of these runs had already satisfied the
threshold the protocol registered -- 40, 124 and 489 times -- and was refused
each time by a threshold up to 100x tighter that no deck ever declared.** Mn
attempt5 met the registered criterion on 489 of its 500 iterations.

QE tests `estimated scf accuracy < conv_thr` at every iteration and exits at the
first crossing. With `upscale = 1.0` holding each run to its own registered
1.0e-06, `Ni s0_OOH__2x1v_mir` closes at cycle 4 iteration 52 and
`Mn s0_OOH__2x1v_off__basin` closes at cycle 20 iteration 11 -- **in the 34.76
branch, the lower one**. Neither is a physics failure. Neither ever was.

Rounds 4 through 9 spent roughly 6,800 SU on beta scans, `mixing_ndim` scans,
geometry resumes, replays and density chains against rows that were converging
all along by the registered criterion.

**R1 (`upscale = 1.0`) is a registered call and remains the entrant's.** The
change is one line in `&IONS`. It alters no functional, cell, cutoff or k-mesh;
it restores conformance with the `conv_thr` the protocol deposited rather than
departing from it. This ledger records the measurement, not the ruling.

### Infrastructure amendment (2026-08-26): converged densities are now retained

`anvil/42_s3_wave1.slurm` and `anvil/44_chain.slurm` deleted every charge
density they ever produced -- an unconditional `rm -rf` on the scratch. That
density is the only thing that pins a magnetic branch for a child run, so A8.3
has had to re-derive it by replaying a whole parent relax. Measured on this
tree: a parent replay costs 41 min to 7 h 47 m (Co ref__2x1v ~1000 SU) against
a median 6 min (~13 SU) for the child SCF itself, and lands in the parent's
branch 2 times in 5.

Both scripts now keep `<prefix>.save` (~76 MB; the multi-GB bulk is `.mix*` /
`.wfc*` and still goes with the scratch) for any run whose every SCF converged.
Cost is ~0.0015% of the 5 TB project quota per run, currently at 0.8% used. No
calculation changes. This is why the one A8.3 chain that failed --
`Co s0_O__1x1_off__g1.fromparent`, -77.009 meV at dmagtot 0.45 -- failed: its
replay was 0.45 off the parent and the seeded child faithfully inherited the
replay's branch, the same 0.45, exactly as a correctly seeded child should.

### Round 10 launched -- array 20161825, 5 rows, `1-5%1`

`EXCLUDE=a024,a088,a196,a220,a223`; preflight `lines=5 to_run=5 already_done=0
stale=0 bad=0`; 8 files md5-verified both sides. Every row is a GATE-1 child
re-rolled under a new prefix, each deck differing from the one on disk in
exactly one line -- the prefix -- verified line-by-line at build time, so
nothing is overwritten (A8.8).

*Group A, bank the anchor (3 rows).* Re-run the child that already found the
lower state, on the three BASIN_DRIFT rows above. Confirms the lower state
reproduces and retains its density as the seed for the registered re-relax.

*Group B, re-roll for the parent's branch (2 rolls, 1 row).*
`Co s0_OOH__2x1v_mir__g1` is the mirror case: the parent is right (magtot 20.13,
bfgs converged) and the child sits 747.449 meV above it at 24.86. A8.3's
registered remedy is a re-run *from the parent's density*, which does not exist
and whose replay has now failed three times; these two cold rolls are therefore
evidence toward the MULTISTABLE disposition A8.3 names, not the registered
remedy itself.

Not built: `Co ref__2x1v__g1` -- its cold child ran 500 iterations, completed no
SCF cycle, and sat at magtot 24.11 against the parent's 21.66; three later
attempts have all fallen into a 23.5-24.1 region that will not converge. It
wants a `starting_magnetization` near the parent's converged moments, which is a
new registered call.

### Corrections to this ledger and to statements made earlier today

1. **"R1 would not close `Ni s0_OOH__2x1v_mir`" -- WITHDRAWN.** Said earlier
   today on the basis of that row's *last* printed accuracy (3.431e-05 at
   iteration 500). QE converges on the *first* iteration below threshold, and
   the cycle's minimum is 3.2e-07 with 40 iterations below the registered
   1.0e-06. The ledger's original claim was right and stands.

2. **"The lower 34.76 branch is the one that will not converge" -- WITHDRAWN.**
   It converges readily: attempt1 shows 19 consecutive converged SCF cycles,
   cycles 4-19 reaching the 1e-08 floor in 9 to 15 iterations each. It dies on
   the iteration budget against the undeclared threshold, not on the physics.

3. **"The banked `Co ref__2x1v` reference cannot be reproduced" -- WITHDRAWN as
   stated.** Round 8's replay (`ref__2x1v.replay.out`, same maxstep as the
   banked deck) reaches E = -4578.38296625 and magtot 22.58 at step 1 against
   the banked -4578.38297855 and 22.50: **0.167 meV and 0.08 uB**. It was marked
   non-convergent only because its residual was still descending. One of two
   replays reproduces the reference; the correct statement is that reproduction
   is unreliable, not impossible.

4. **The branch rule's tight bound was quoted as 0.52 meV.** Measured over all
   29 matched-magnetization GATE-1 pairs it is **0.044 meV**, twelve times
   tighter.

5. **A first pass at a replicate census grouped relax parents with their SCF
   children** -- its geometry hash collided on the frozen `0 0 0` atoms, which
   are identical between a parent's initial and final coordinates. Any
   "replicate" statistic derived from it is void; the numbers above come from
   full-precision all-atom comparison with the calculation type held fixed.

### Addendum -- how much of the campaign the `upscale` trap actually touches

Swept every `.out` under `runs/` carrying `convergence NOT achieved`, and for
each one asked a single question: in the cycle that failed, did the run ever
reach the threshold **its own deck registered**, while being held to a tighter
one QE had silently substituted?

**60 non-convergent outputs. 10 of them -- 17% -- had already met the registered
`conv_thr = 1.0e-06`, and were refused anyway.** Across five elements and both
the S3 tree and the older `*_slab` probe trees:

| dir | file | iters | min acc | held to | declared | iters meeting declared | first at | run after |
|---|---|---|---|---|---|---|---|---|
| `s3/Mn` | `s0_OOH__2x1v_off__basin.out.attempt5` | 500 | 6.0e-08 | 1.00e-08 | 1.0e-06 | **489** | 9 | 491 |
| `Co_slab` | `s0_O.out.attempt3` | 500 | 1.1e-07 | 8.99e-08 | 1.0e-06 | **471** | 30 | 470 |
| `Cr_slab` | `s0_OH.out.attempt2` | 500 | 7.4e-07 | 5.87e-08 | 1.0e-06 | 3 | 33 | 467 |
| `s3/Ni` | `s0_OOH__2x1v_mir.out.attempt3` | 500 | 3.2e-07 | 2.79e-07 | 1.0e-06 | **40** | 52 | 448 |
| `s3/Mn` | `s0_OOH__2x1v_off__basin.out.attempt1` | 200 | 5.0e-07 | 1.00e-08 | 1.0e-06 | **124** | 11 | 189 |
| `Co_slab` | `s0_OOH.out.attempt1` | 200 | 2.6e-07 | 1.27e-07 | 1.0e-06 | **47** | 15 | 185 |
| `Cu_slab` | `s0_OOH.out` | 200 | 5.7e-07 | 2.18e-07 | 1.0e-06 | 12 | 36 | 164 |
| `Cr_slab` | `s0_OH.out.attempt1` | 200 | 9.6e-07 | 9.66e-08 | 1.0e-06 | 2 | 40 | 160 |
| `s3/Ni` | `s0_OOH__2x1v_mir.out.attempt2` | 200 | 8.8e-07 | 6.57e-07 | 1.0e-06 | 1 | 94 | 106 |
| `Co_slab` | `s0_OH.out.attempt1` | 200 | 7.5e-07 | 1.13e-07 | 1.0e-06 | 16 | 185 | 15 |

**2,695 SCF iterations were run after the registered criterion had already been
met** -- order 1,900-5,700 SU on these cells.

Two honest qualifications, because the rows are not equivalent:

- **Five would close solidly under R1**, with the registered threshold met on
  40 to 489 iterations: both `Mn s0_OOH__2x1v_off__basin` attempts,
  `Ni s0_OOH__2x1v_mir` attempt3, `Co_slab s0_O` attempt3, `Co_slab s0_OOH`
  attempt1.
- **Five would close marginally**, meeting it on only 1 to 16 iterations
  (`Cr_slab s0_OH` x2, `Cu_slab s0_OOH`, `Ni s0_OOH__2x1v_mir` attempt2,
  `Co_slab s0_OH` attempt1). R1 would declare these converged, but on a
  criterion they only just satisfy; they should be re-run rather than banked
  from the existing output.

Worth separate note: `Cu_slab s0_OOH.out` is on this list. The campaign record
has Cu carrying no usable data; its `*OOH` run met the registered threshold 12
times before being refused.

The remaining 50 non-convergent outputs are genuine -- they never reached
1.0e-06 at all -- and R1 does nothing for them.

## Round 10 -- array 20161825. BASIN_DRIFT independently confirmed; a sixth bad node; and my retention patch was 30-60x wrong

Five GATE-1 children re-rolled under new prefixes, each deck differing from the
one on disk in exactly one line. 3 completed, 1 OOM-killed on a new node, 1 was
still running when this was written.

### Group A -- the BASIN_DRIFT rows reproduce exactly

| row | re-roll E (Ry) | vs first child | dmagtot | vs BANKED PARENT |
|---|---|---|---|---|
| `Fe s0_OOH__1x1_off__g1__r2` | -2558.16352818 | **-0.0001 meV** | 0.000 | **-384.300 meV** |
| `Mn s0_OOH__2x1v_off__g1__r2` | -3617.10020423 | **-0.0012 meV** | 0.000 | **-20.617 meV** |
| `Co s0_O__1x1_off__g1__r2` | (no `!` energy) | -- | -- | -- |

Fe converged in 26 iterations and Mn in 28, both `notconv 0`, both landing on
their first child's energy to **0.1 and 1.2 micro-eV** at identical
magnetization. Two independent runs, on a different day, agreeing to a part in
10^10 of the total energy.

**So the BASIN_DRIFT finding is confirmed, not an artifact.** `Fe
s0_OOH__1x1_off` and `Mn s0_OOH__2x1v_off` are banked 384.300 meV and 20.617 meV
**above** a reproducible state at their own final geometry. Under
`docs/43:311-314` both trigger the registered re-relax loop, and under
`docs/43:787-790` the GATE-1 SCF energy is the corrected value. The anchor
densities for that re-relax are now on disk.

`Co s0_O__1x1_off__g1__r2` did **not** reproduce: 200 iterations, `convergence
NOT achieved`, no `!` energy at all, and magtot 11.95 against the first child's
11.24 and the parent's 11.69 -- a *third* state at the same geometry. Its
density was correctly not retained (the gate requires every SCF converged). The
-77.009 meV result for that row therefore stands on one observation only, and
is the weakest of the three.

### Group B -- `Co s0_OOH__2x1v_mir` is heading for MULTISTABLE

`__r2` was OOM-killed on **a050** at 13 iterations. `__r3` reached iteration 212
at magtot **23.74** against the parent's 20.13, accuracy 5.3e-05 against a 1e-06
target -- the same 23.5-24.9 high-spin region every other attempt on this cell
has fallen into (`__g1` cold 24.86, `ref__2x1v` replays 23.56 / 23.60 / 24.11).
A8.3's registered remedy is a re-run from the parent's density, which does not
exist and whose replay has now failed three times; the disposition A8.3 names
for that case is MULTISTABLE, both numbers recorded, neither banked.

### A sixth bad node: a050

| node | tasks killed | MaxRSS at kill | spread |
|---|---|---|---|
| a196 | 3 | 8.65, 8.66, 8.70 GB | 0.5 % |
| a220 | 2 | 35.06, 35.14 GB | 0.24 % |
| a223 | 4 | 16.93, 16.94, 16.95, 16.95 GB | 0.1 % |
| **a050** | **1** | **33.62 GB** | (single sample) |

a050 was not in the exclusion list and killed a job whose three siblings had
just completed on a095. Six nodes now, a new one on each of the last four
submissions. `anvil/rcac_ticket_draft_2026-08-24.md` updated.

### CORRECTION -- the retention patch was 30-60x wrong on size

Earlier today I patched `anvil/42_s3_wave1.slurm` and `anvil/44_chain.slurm` to
retain `<prefix>.save`, and justified it at "~76 MB, ~0.0015% of quota per run".
**That figure came from inspecting FAILED runs' scratch saves, which are
incomplete.** The first two real retentions came in at **2.4 GB and 4.5 GB**,
because a completed run's save carries the wavefunctions:

| | whole `.save` | `wfc*.hdf5` | density payload |
|---|---|---|---|
| Fe `s0_OOH__1x1_off__g1__r2` | 2.4 GB | 2.505 GB (36 files) | **42 MB** |
| Mn `s0_OOH__2x1v_off__g1__r2` | 4.5 GB | 4.744 GB (20 files) | **72 MB** |

`startingpot='file'` reads only the charge density. Wavefunctions would serve
`startingwfc='file'` and `restart_mode='restart'`, **both of which this campaign
forbids** (`build_s3_wave2.py:FORBIDDEN_RESTART`). So retaining them was not
just 30-60x too expensive, it was storing the one thing the protocol bans using.

Both scripts now copy every file in the save except `wfc*`, and verify
`data-file-schema.xml` landed before swapping the copy into place. The two
existing saves were trimmed in place, **2.4 G -> 44 M and 4.5 G -> 74 M**, and
both still verify: the schema's `etot` doubles to exactly the run's own Ry
energy (-2558.16352818 and -3617.10020423) at matching magnetization
(22.977, 34.823). The original "76 MB" number was accidentally right about the
density and wrong about what the patch actually copied.

### Round 10 Group B closed: the children are not losing a lottery, they cannot win it

`s0_OOH__2x1v_mir__g1__r3` converged in 273 iterations, `notconv 0`, JOB DONE, at
E = -4662.62789719 and magtot **23.95** / magabs 26.23. Against the banked parent
(-4662.69189747, magtot 20.13, magabs 22.91) that is **+870.768 meV** at
dmagtot 3.82 -- a BRANCH MISMATCH, and *worse* than the original cold child's
+747.449 meV at 24.86.

So three independent cold `scf` runs at that parent's final relaxed geometry:

| run | result |
|---|---|
| `__g1` (round 5) | magtot 24.86, **+747.449 meV** |
| `__g1__r2` (round 10) | OOM-killed on a050 at 13 iterations |
| `__g1__r3` (round 10) | magtot 23.95, **+870.768 meV** |

**and the SCF magnetization trajectories say why.** Every cold start at the
relaxed geometry is inside the 23-25 uB region by roughly iteration 30 and never
leaves it (`__g1` 24.56 at it 30; `__r3` 24.32 at it 30, settling 23.4-23.9 for
240 more). The parent, by contrast, reached magtot **19.81 at ionic step 1** --
cold, first try, from the ORIGINAL geometry -- and then walked 19.81 -> 20.13
across 22 ionic steps carrying its own density forward. `Co ref__2x1v` has the
identical shape: 22.50 at step 1 from the original geometry, 21.66 by step 10.

**The reachable magnetic branch is a property of the geometry the SCF cold-starts
from.** From the original geometry the low branch is reachable and has been
reached repeatedly -- mir at 19.81 / 19.79 / 19.98 (3 of 5), ref at 22.50 / 22.58
(2 of 3). From the relaxed geometry it has never been reached, in three tries.

This retires the "R3 / A8.6, the banked energy cannot be reproduced on demand"
framing for this row. The branch **is** reproducible from the geometry that
reaches it; what is not reproducible is reaching it from somewhere else. Note
also that `s0_OOH__2x1v_mir.replay.out`, which this ledger recorded as a failed
replay, in fact landed at magtot 19.98 -- **in the parent's branch**. It failed
on convergence (stalled at 2.5e-05, and genuinely stalled: its accuracy rose
after iteration 100 rather than descending), not on branch.

### Round 11 launched -- array 20166408, 3 rows, `1-3%3`

Re-anchor runs. Each re-runs the deck of record for one open wave-4 parent under
a new prefix; nothing is replaced (A8.8) and the banked `.out` files were
md5-verified untouched before submission (`s0_OOH__2x1v_mir.out` 2,164,902 B
`09481705...`, `ref__2x1v.out` 1,847,613 B `0a81fd37...`). The point is not to
restate a parent's energy -- it is to produce, and this time KEEP, a converged
density at the relaxed geometry in the parent's own branch.

| row | nk | seeks | cost |
|---|---|---|---|
| `Co s0_OOH__2x1v_mir__reanchor` | 8 | magtot ~19.8 | ~340 SU |
| `Co s0_OOH__2x1v_mir__reanchor__b` | 8 | magtot ~19.8 | ~340 SU |
| `Co ref__2x1v__reanchor` | 16 | magtot ~22.5 | ~1000 SU |

Two rolls of `mir` because it is cheap and lands low 3 times in 5; one of `ref`
because it is 7 h 47 m. A roll that lands high is banked as evidence and no child
is run from it. Round 12 then runs the `__g1.fromparent` children, which already
exist on disk carrying `startingpot='file'` (both verified at build time),
against whichever seeds landed -- and a seeded child inherits its seed's branch,
which is what the two A8.3 successes demonstrated (Fe to 0.004 meV, Ni to 0.019
meV, both at matching magnetization).

`EXCLUDE=a024,a050,a088,a196,a220,a223` -- a050 added after it OOM-killed
round 10's `__r2` at MaxRSS 33.62 GB while three siblings completed on a095.

**Process note.** The first submission was REFUSED by the driver preflight:
`wrong-np-for-manifest ... declares NP=128 NCONC=3, invoked with NP=128 NCONC=1`.
`NCONC` in a manifest header is the DRIVER's concurrency, which
`anvil/43_submit_s3_wave1.sh:68` hardcodes to 1; the Slurm ARRAY concurrency is
the separate `%$CONC` second argument (line 76). Every prior manifest declares
`NCONC=1`, and round 8 ran `1-3%3` with that declaration. The header was
corrected and the three decks regenerate byte-identical (md5 unchanged). The
guard did exactly its job.

## Round 11 -- array 20166408. Zero seeds from three rolls; a refuted correlation; and the real bottleneck is not compute

Three re-anchor rolls, all COMPLETED in Slurm, none usable. Slurm COMPLETED is
not convergence and `JOB DONE` is not success (docs/26 s4): all three printed
`convergence NOT achieved`, so the retention gate (`scf_fail -eq 0`) correctly
kept nothing. Cost ~1,103 SU; balance 75,207.7 -> 74,104.9.

| roll | nk | ionic steps | plateau magtot | outcome |
|---|---|---|---|---|
| `s0_OOH__2x1v_mir__reanchor` | 8 | **8 converged**, 9th failed | **20.37 (LOW)** | stalled cycle 9 at 500 iters |
| `s0_OOH__2x1v_mir__reanchor__b` | 8 | 0 | 21.90 | first SCF stalled, 500 iters |
| `ref__2x1v__reanchor` | 16 | 0 | 23.39 | first SCF stalled, 500 iters |

### Row 1 reached the low branch and then stalled anyway

`__reanchor` tracked the banked parent closely -- magtot 21.47 -> 19.98 -> 19.86
-> 20.24 ... -> 20.37 against the parent's 19.81 -> 20.13 -- and converged eight
consecutive ionic steps, every one of them cleanly. Cycle 9 then ran 500
iterations with **min accuracy 6.8e-06 and zero iterations below the registered
1.0e-06**. So this failure is NOT the upscale pattern: the registered threshold
was never met, and R1 would not have rescued it.

The upscale tightening is nonetheless visible and measured here for the first
time on a healthy run. `new conv_thr` walked 1.0e-06 -> 5.526e-07 -> 3.250e-07
-> 1.416e-07 -> 1.345e-07 -> 8.66e-08 -> 7.12e-08 -> 4.16e-08, so cycle 9 was
being asked for 24x the registered tolerance. Iterations run vs first crossing
of the registered 1e-6, per cycle:

| cycle | ran | crossed 1e-6 at | wasted |
|---|---|---|---|
| 1 | 69 | 69 | 0 |
| 2 | 20 | 20 | 0 |
| 3 | 39 | 37 | 2 |
| 4 | 18 | 16 | 2 |
| 5 | 22 | 15 | 7 |
| 6 | 17 | 12 | 5 |
| 7 | 23 | 16 | 7 |
| 8 | 28 | 16 | 12 |
| 9 | 500 | never | -- |

**35 of 236 iterations wasted, 15 %.** That is the honest size of R1 on a run
that converges: a modest efficiency win, growing with ionic step as upscale
tightens, and worth nothing on a genuine stall. This CORRECTS the framing that
R1 is "the highest-value registered call": it rescues the ~10 of 60 outputs that
did cross the registered threshold and were failed anyway, and it trims ~15 %
off the healthy ones. It does not fix rows 2 and 3, whose FIRST SCF -- run at
the deck's own 1e-6, before any upscale tightening exists -- stalled at 5.6e-05
and 1.0e-05 with zero crossings.

### A correlation proposed and REFUTED by its own data

Working hypothesis on seeing rows 2 and 3 roll high and stall: in this cell the
high-spin branch is the non-convergent one, so "wrong branch" and "does not
converge" are one phenomenon. **Refuted.** Censused all 24 Co `2x1v` outputs:
`s0_O__2x1v_off` (25.23), `s0_OH__2x1v_mir` (24.31), `ref__2x1v.replay_ms`
(23.59) and `s0_OOH__2x1v_mir__g1__r3` (23.93) are all high and ALL CONVERGED,
while `s0_OOH__2x1v_mir.replay` (20.16) is low and FAILED. Plateau magnetization
is not comparable across adsorbates in the first place -- ref, *O, *OH and *OOH
carry genuinely different moments -- and within a single row both branches both
converge and fail. No correlation. Recorded because it was nearly asserted.

### Infrastructure: a 5.2 GB save the corrected patch did not catch

`Co/dens/s0_OOH__2x1v_mir__g1__r3.save` was retained at **5.2 GB**, wavefunctions
included, after the density-only correction was already in the repo. Cause:
Slurm snapshots the batch script at SUBMIT time, and round 10 was submitted
before the correction landed, so that array ran the uncorrected block. Trimmed
in place, **5.2 G -> 79 M**, and verified: the schema's `etot`
(-2.331313948596418E+003) doubles to -4662.62789719 Ry, exactly the run's own
final energy. Rule of record: **a mid-flight patch to a `.slurm` file does not
reach an already-submitted array.**

### Disposition: the seeding attempt has run out of registered moves

Rounds 5, 10 and 11 have now tried to put `Co s0_OOH__2x1v_mir__g1` and
`Co ref__2x1v__g1` on their parents' branch by cold SCF (3 attempts, all high),
by re-anchor (3 rolls, none convergent), and by replay (5 attempts across both
rows). Round 10 established the mechanism: the reachable branch is a property of
the geometry the SCF cold-starts from, and no cold start at the relaxed geometry
has ever reached the parent's branch. **GATE-1 as registered -- a cold
fresh-density SCF at the relaxation's own final coordinates -- therefore cannot
be satisfied for these two rows, and the obstruction is in the test, not in the
parents.** That is a finding about a registered instrument and its disposition
is the entrant's, not an AI's. A8.3's named outcome for exactly this case is
MULTISTABLE: both numbers recorded, neither banked (docs/43:1589-1592), and it
costs 0 SU.

The one untried lever remains one line and is registered input, not
infrastructure: every attempt has used the COLD `starting_magnetization`
(Co 0.4). Setting it near the parent's converged per-site moments would make the
low branch the intended target instead of a 3-in-5 lottery, at ~13 SU for a
single-SCF child. It changes a registered input and must be declared as a
branch-selection aid rather than a result, so it is Frank's call and is NOT
taken here.

## Correction of record, 2026-08-27: three stale stage rows that read as a blocked critical path

**The error.** On 2026-08-27 this ledger's own §E table still carried `A9 (owed Aug 22)`
/ `blocked on A9` on rows S1 and S2, and `A8 (owed Aug 24)` / `launch Aug 26` on S3.
Read together with the filenames `docs/47-amendment-8-DRAFT.md` and
`docs/50-amendment-9-DRAFT.md`, and with `docs/52`'s 66 open decision rows, this
supports a confident and entirely wrong conclusion: that the campaign's critical path
was stalled on two undeposited amendments, five and three days overdue.

**The fact.** A8 and A9 were both **ADOPTED by the entrant and DEPOSITED on 2026-08-23**
as one Zenodo version, **DOI 10.5281/zenodo.22072991**, appended to `docs/43` at commit
2e61bf0 (verified 1c09c38). All 18 `A8.*`/`A9.*` sections are present in the registered
`docs/43` (1,973 lines). Rows :51-52 of this same ledger say so explicitly. Both DRAFT
files carry, in their own headers, `Status: ADOPTED by the entrant 2026-08-23 (reviewed
via docs/52; "they pass with me") and appended to docs/43`. `docs/52` was compiled
2026-08-23 **before** that adoption and is a historical index, not a live queue.

**Three traps, worth naming because each is re-triggerable.**
1. A `-DRAFT` suffix survives adoption here by convention — the draft file is kept
   verbatim as the historical artifact and the registered text moves into `docs/43`.
   **The filename is not the status; the file's own header line is.**
2. A status TABLE goes stale silently while the prose sections around it are appended
   to. This ledger is append-only by habit, so its tables are the one part that rots.
3. A decision sheet compiled before an adoption reads exactly like an open queue after
   it. `docs/52` has no adoption stamp on its face.

**What was actually open on 2026-08-27**, from the deposited text rather than the stale
rows: in A8 — the gate-(h)/AFM scope line (**HOLD, 0 built**, docs/43:1645), `--bind-to`,
the walltime value; in A9 — the CI mechanism, the Xu repair (a)/(b) election, P-BUILDER
and P-LIT values, the six-row displacement and claim sentence (Sep 20), the two molecule
jobs. S1 is gated on the entrant-written core, not on a deposit. S2's A9.7 acts 1-3 were
discharged 2026-08-23; **act 4, the census, waits on `silentgate`.**

**Rule adopted here:** before reporting any stage as blocked, the block must be read
from the DEPOSITED text (`docs/43`) or from a file header carrying a status line —
never from a filename, and never from a table cell alone.

The three §E rows are corrected in place with this entry as their provenance.

## S3 remaining-work inventory, 2026-08-27 (14-agent fan-out, adversarially verified)

`docs/54`'s matrix predates waves 1-4 and rounds 3-11, so it is stale on exactly the
rows that matter. Six inventory agents (one per metal) were each refuted by a paired
verifier. **The verify pass caught a fabricated evidence line** -- one agent reported
"Final scf block present" on all ten Mn relaxations; `grep -ic 'final scf'` returns 0 on
every one of them and `grep -ril` returns nothing repo-wide. Four of six metals came
back CORRECTED. Nothing below is relayed on an agent's word alone; every number here
was re-measured directly.

| metal | BUILD rows | converged | failed | built-not-run | deck missing |
|---|---|---|---|---|---|
| Cr | 23 | 20 | 0 | 0 | 3 |
| Mn | 16 | 14 | 0 | 0 | 2 |
| Fe | 11 | 10 | 0 | 0 | 1 |
| Co | 10 | 7 | 2 | 0 | 1 |
| Ni | 10 | 8 | 1 | 0 | 1 |
| Ti | 7 | 7 | 0 | 0 | 0 |
| **total** | **77** | **66** | **3** | **0** | **8** |

**Nothing is built-and-waiting.** Every deck that exists has been run.

### All 8 missing decks are blocked on an open registration decision -- none is mine to build

| family | count | blocked by |
|---|---|---|
| `__magm` second seed (Mn, Fe, Co, Ni) | 4 | no registered numeric recipe. A8.1 names none (docs/43:1516); the implemented LIT-3 reading `starting_magnetization(O) = -0.5` is flagged NEEDS FRANK'S SIGN-OFF (`runs/probe/lit3_manifest.json:71`); BUILD-T is launchable only after the triage line (docs/54 s6 items 2-3) |
| `__ns` (Cr, Mn) | 2 | the decks' class (SCF vs relax) is unstated, so they cannot be built as specified (docs/54 s6 item 2); parked at `m_s3_wave1.txt:8`. `starting_ns_eigenvalue` appears in ZERO decks repo-wide |
| dy-ladder rungs (Cr) | 2 | rungs {0.10, 0.25, 0.50} A live only in synthesis:258; deposited A8 carries the ladder by name alone (docs/43:1483-1484), and mapping a y-translation ladder onto a polyatomic *OOH start is unspecified (docs/54 s6 item 7) |

Building any of these would mean inventing a registered parameter. They are held.

### The 3 remaining failures are ONE failure class, and R1 does not touch it

| row | iters | min accuracy | crossed registered 1e-6 |
|---|---|---|---|
| `Co s0_O__2x1v_mir` (corner C) | 1500 | 1.628e-05 | **0** |
| `Co s0_OH__2x1v_off` (corner B) | 500 | 2.470e-05 | **0** |
| `Ni s0_OOH__2x1v_mir` (corner C, att7) | 500 | 2.172e-04 | **0** |

All three die on their **first** SCF cycle, at the deck's own registered `conv_thr =
1.0d-6`, with **no `new conv_thr` line yet printed** -- upscale has not engaged, so
`upscale = 1.0` (R1) is irrelevant to every one of them. R1 remains worth its one line
for the ~10 of 60 outputs that did cross and were failed anyway, and for the ~15 %
iteration trim measured on `__reanchor`; it is not a fix for these.

**What HAS been tried on `Ni s0_OOH__2x1v_mir`, across seven attempts:** `mixing_beta`
0.3 -> 0.15 (all four retry variants), `electron_maxstep` 200 -> 500 (three), `mixing_ndim`
= 16 (one), and a displaced geometry (two). **`starting_magnetization` was never moved**
-- it reads `(1)=0.0 (2)=0.3 (3)=0.0` in the base deck and in all seven attempts.

That is the same lever left untried on the two open Co children. **Every remaining S3
failure and both open GATE-1 rows now point at one line of registered input.** It is a
registered-input change and therefore the entrant's call, not infrastructure.

### CORRECTION -- a false alarm on a banked reference, resolved

The Mn verifier reported that `runs/s3/Mn/ref__2x1v.out` "performed NO relaxation" --
`bfgs converged in 1 scf cycles and 0 bfgs steps` on a `calculation = 'relax'` deck --
and implied the banked -3532.71646890 Ry is unsound. **The run is legitimately
converged.** QE's own report: `Energy error = 2.4E-05 Ry` (< 1.0E-04) and `Gradient
error = 1.7E-03 Ry/Bohr` (< 2.0E-03). Atoms 1, 2, 7, 9, 10 and 12 carry `0 0 0` in the
deck, and the max |force| over FREE coordinates only is **0.001721 Ry/bohr** -- exactly
QE's reported gradient error. The input geometry was already at the minimum for its free
coordinates. Zero bfgs steps is the correct outcome, not a defect.

### But it exposes a registered premise that is FALSE in QE 7.5

Chasing that alarm required checking whether pw.x masks frozen-atom forces. The
registered A9.1 reader rule (docs/43:1834) states, as its reason:

> "atoms with any `if_pos = 0` are excluded from every exact-zero count and their number
> reported (**pw.x prints the if_pos-masked force, so a fixed coordinate reads exactly
> zero for a reason that is not symmetry**)."

**Measured, 5 outputs across 5 metals, 78 frozen atoms: not one prints all-three-exactly-
zero.** `Mn/ref__2x1v` 14 frozen / 0 zero; `Cr/s0_OOH__2x1v_escape` 14/0; `Ti/ref__2x1v`
14/0; `Fe/s0_O__2x1v_mir` 14/0; `Ni/s0_OH__2x1v_mir` 22/0. Frozen atoms print their full
unmasked force -- e.g. Mn atom 12 (`0 0 0`) prints z = 0.04355221 Ry/bohr.

The clause's **action** is unaffected and remains conservative: a frozen atom's force is
not evidence about symmetry either way, so excluding it is right. What is wrong is the
stated **reason**, and it inverts a risk assessment: frozen atoms were named as a source
of false LOCKED positives, and in this build they cannot be one. The live risk runs the
other way -- any detector that *infers* which atoms are frozen from exact-zero forces
would find none. This matters now because `silentgate`'s registered adsorbate rule is
built on it and the entrant is about to write that reader. **Disposition is the
entrant's: this is a factual correction to a deposited clause's parenthetical, not a
threshold, and it is reported, not acted on.**

### S1 harness state (AI-permitted work, none of it started)

`.github/` does not exist; there is no `pyproject.toml`, `setup.py` or `silentgate/`
package -- re-verified 2026-08-27, still true four days after A9.0 recorded it. Both
registered CI controls are therefore unwritten, and A9.2 makes them a GATE that "voids
rather than caveats." The authorship boundary, quoted at docs/43:1840: core =
`silentgate/readers/*`, `census.py`, `classify.py`, `direction.py`, `cli.py`, "written
and committed only by the entrant" -- the constraint binds the COMMIT, so an AI-authored
patch committed under the entrant's name would violate it. AI may write tests, fixtures,
the CI workflow, review comments, and `pyproject` metadata / version string /
entry-point declaration and "nothing wider." A CI helper that parses `pwscf.out` force
blocks is a reader; writing one under any name would be authoring core.

---

## S1 CI harness BUILT, 2026-08-27 — and two registered facts corrected on the way

The S1 line above is now superseded in one respect: `.github/` exists. Nineteen files
were written under the A9.1 :1840 permitted list (tests, fixtures, the CI workflow,
narrow packaging) and one hand-off document, `docs/57-s1-ci-handoff-2026-08-27.md`,
which carries the file list for the AI-use log, the six open decisions, and the
golden-file protocol. Nothing under `silentgate/` was written — not one file, including
`__init__.py`, which is not on the five-entry core list and could have been written
inside the letter of the rule. What is unchanged from the line above: **the core is
still entrant-written, and the controls still cannot run without it.**

The face is red and says exactly why: `core_present ABSENT`, `disjointness FAIL`
(no AI-use log exists and its path is unregistered), and six controls `NOT MEASURED` in
the registered vocabulary of :1868. Two of the six open decisions block CI today — the
OC20 transport (:1868, open at adoption) and the AI-use log's path (named as an
obligation five times in docs/43, given a path nowhere).

**The design rule that shaped all of it: no shadow reader.** The obvious test suite
computes the expected census independently and asserts the core reproduces it. That
would have meant writing a per-atom / per-axis / per-step force-block parser — which is
`silentgate/readers/*` — and would have put a second, unreviewed detector in the repo,
leaving *whose census is right?* with no registered answer. So the fixture manifest
records structural facts only (hashes, byte counts, marker lines, block counts) and
numeric expectations enter later as golden files the entrant generates and reviews. The
same rule is why `.github/ci/silentgate-invocation.toml` is entirely blank: hard-coding
a command line and a JSON shape would design `cli.py`'s interface, and `cli.py` is core.

### (a) A9.1 :1834's `if_pos` rationale is false for QE 7.5 — re-measured, and stronger

The section above reported this from a 78-atom check. Re-measured from scratch
2026-08-27 over five deck/output pairs in five metals, **every ionic step of each run:
704 frozen-atom force observations, and not one prints all three components exactly
zero.** `runs/s3/Mn/ref__2x1v.in` atom 12, flagged `0 0 0`, prints z = 0.04355221
Ry/bohr; the largest frozen-atom component observed is 0.08723744 in
`runs/Cr_slab/s0_O.out`. If the mask were applied, a `0 0 0` atom would read
`0.00000000` on all three axes.

Sharper than before: a frozen atom **can** print an exact zero on one axis —
`runs/Cr_slab/s0_O.out` atom 1 reads `0.00000000 0.00000000 0.08723744` — but that is
the symmetry witness doing its job, which is the *opposite* of what the parenthetical
claims. Disposition unchanged and still the entrant's.

### (b) The pw.x symmetry header has FOUR textual forms here, and the registered "both forms" has never been tested

A9.1 :1830 registers that the reader "accepts both forms by regex and logs the form
encountered per file", where "both" means pw.x 7.5's count-first form and the
count-**last** form shown in `symops_audit.py`'s own docstring. Censused over all 515
tracked outputs:

| form | files |
|---|---|
| `N Sym. Ops. (no inversion) found ( N have fractional translation)` | 128 |
| `N Sym. Ops., with inversion, found` | 21 |
| `N Sym. Ops. (no inversion) found` | 13 |
| `N Sym. Ops., with inversion, found ( N have fractional translation)` | 11 |
| `No symmetry found` (no header line) | 312 |
| neither marker | 30 |

**Zero** use the count-last form. A regex anchored on `(no inversion)` misses 32 of the
173 files carrying a header; the legacy `SYMOPS = r"^\s*(\d+)\s+Sym\. Ops\."` survives
all four, which is worth knowing before v0.1 rewrites it. And A9.7's act-2 dated line
(2026-08-23, the first parse) already looked for the count-last form in the Xu deposit
and recorded that all four validated RuO2 files are count-first. So the both-forms rule
stands but has been exercised against **no real count-last data anywhere** — 0 in-house,
0 in the four Xu files read — and P-XU's six blind metals cannot rule it out. Pinned in
the fixture manifest so "accepts both forms" is never read as "tested on both forms".

### Two bugs the harness found in itself

Writing the end-to-end tests surfaced two defects in the AI-written CI, both fixed:
`run_controls.py` substituted paths into the command string *before* `shlex.split`, so a
Windows path reached the tool with its backslashes eaten; and `core_present` tested only
that `silentgate/` was a directory, so an **empty** directory would have read PRESENT
and let the face claim an instrument that does not exist. It now names all five module
paths. Both are recorded because the second is the exact failure shape A9.2 exists to
catch — a gate reporting a state it has not verified.

### The tripwires are one-sided on purpose

S3 is live and adding outputs. A corpus check that fired on every legitimate new run
would train the reader to ignore CI, and being ignored is the only way a gate actually
fails. So the suite fails when a tracked output **disappears**, when a fixture's content
changes, or when an **unrecognised symmetry-header form appears**; ordinary growth is
printed and allowed. Regenerate the manifest with
`tests/silentgate/fixtures/regenerate_manifest.py` and commit the diff.

State: `pytest tests/silentgate` → 40 passed, 6 skipped (the six skips are the open
decisions, which bind once the core exists). Whole repo → 129 passed, 6 skipped; the
pre-existing 100 unchanged. `run_controls.py`, `run_oc20.py` and `check_disjoint.py` all
exit 1, as a registered gate whose instrument is unwritten should.

### The harness was audited adversarially, and 24 findings held

A 42-agent audit (5 finders x 4 dimensions + paired refuters, every finding sent to a
verifier told to refute it) returned **24 confirmed, 13 refuted**. All 24 are fixed. The
three that matter:

**(1) The one assertion :1840 registers CI to perform was evadable by a backslash.**
`check_disjoint.py`'s token regex excluded `\`, so a core path written the way Windows
prints it -- `silentgate\census.py`, and the entrant's machine is Windows -- was chopped
into fragments that matched nothing, and the assertion PASSED. The `normalise()` call that
folds backslashes to slashes was unreachable dead code. Prefixed forms evaded it too
(`a/silentgate/cli.py` from a pasted diff). Both fixed, with regression tests. Also fixed:
an AI-use log that EXISTS but names no file used to pass with "0 path token(s)" -- the same
vacuous pass a MISSING log is refused for, reached through the front door -- and `find_log`
returned only the FIRST matching log, silently answering the open question "is it one file
or many" and letting a core path in log #2 through.

**(2) A green gate over an empty set.** `populations.txt` was read without validating its
size while every printed denominator was a string literal. Deleting the 11 `nosym_present`
lines made the face print "force-only LOCKED 0/11", "20/20 partition" and "20/20 agree" as
MEASURED/PASS, RESULT: GREEN, exit 0, with zero of the registered QE negative-control runs
scored. Sizes are now asserted against the registered 9 and 11 and every denominator is
computed. This is the exact fail-open shape A9.2 exists to catch, found inside the thing
built to catch it.

**(3) Half the OC20 threshold was unimplemented, and the verified sample was never tied to
the scored one.** :1856 registers the 0.00 % rate *"and the per-step exact-zero count over
all unconstrained atoms and axes is reported alongside"*; the count had no schema field and
no consumer. Separately, `run_oc20.py` hash-verified the 500 drawn files and then accepted
any 500 records as "the val_id first-500" -- verification and measurement never met. Both
fixed; the census must now name the same 500 files.

Also fixed: seven wrong line citations (the registered "accepts both forms by regex" rule is
at **:1836**, not :1830, cited wrongly in five files; the run-level ALL-atoms rule is at
**:1830**, not :1826; the AI-use log's five mentions are :1322/:1443/:1445/:1828/:1840, and
:1447 was double-counting one sentence); a malformed `disjoint.json` crashed the face before
printing anything, exactly when the disjointness check is what misbehaved; on `pull_request`
the face stamped the ephemeral merge SHA, which exists in no branch and is garbage-collected,
defeating :1868's "carries the commit hash ... at that commit"; `upload-artifact@v4` 409s on
a job re-run without `overwrite: true`, which is the interaction the entrant will use most
while the face is red; a test asserted core ABSENCE unconditionally and would have failed the
day the core landed; and three registered "reported alongside" quantities (`unidentified`,
`n_if_pos_excluded`, `header_form`) were declared in the schema with no consumer, so filling
them in would have changed nothing. The face now prints them.

**And the audit's fairest hit: this was the repo's first CI and it ran none of the repo's
own tests.** The only green signal was "the new harness is internally consistent." A
`repo-tests` job now runs the fourteen pre-existing modules that cover the code which
produced the campaign's numbers, in its own job so a failure there is never mistaken for a
control regression.

### DISCLOSURE: an AI script censused F_x on the P-CTRL populations before v0.1 exists

The audit's most important finding is not a bug. Choosing the thirteen fixtures required
knowing which files carry which trap, and an AI survey script -- written 16:51 on
2026-08-27, about forty minutes before the first CI file -- got that by parsing every pw.x
force block under `runs/` per atom, per axis, over every ionic step. It is preserved with
its output at `docs/research/ai-survey-2026-08-27/`.

Writing it was permitted and, in terms, anticipated: **:1445 lists "sweeps" among what the
AI-use log records**, and nothing under `silentgate/` was written. What needs the entrant's
ruling is narrower: the sweep measured two quantities the registered text calls
not-yet-measured.

> :1858 -- "it passes today on y ... and is **unmeasured on x** until v0.1 reports it."
> :1864 -- "**F_x was never censused by the current code and is reported by v0.1**."

Over the 20 registered P-CTRL runs: **3 of the 9** `nosym`-absent lock x on every step --
`Cr_slab/s0_O.out`, `Ir_anchor/s0_O.out`, `Ru_anchor/s0_O.out`, all `n_symops = 4`, exactly
the 1x1 *O class :1864 predicts locks x by inference -- and **0 of the 11** `nosym`-present
lock x. The registered prediction is confirmed. The y figures (9/9, 0/11) are NOT new;
:1858, :1864 and :1964 already register them as the published record. The x half is what
changed status.

Why it is worth a dated line: F4 (:1848) makes P-CTRL a gate precisely because "the detector
is wrong in the same direction as the finding; every number flows through code written by
the person who believes the trap is real." A control whose expected answer is published
before the detector is written is weaker than one whose answer is not. That is a reason to
disclose, not a reason the numbers are wrong. Nothing in CI is scored against them, no test
asserts them, and a test forbids the harness from referencing the survey at all. Registered
as the seventh open question, `ai_x_census_disclosure`.

The same survey is why the fixture manifest's `pins` prose says things like "LOCKED on both
lateral axes". An earlier draft of that file claimed in its header to contain no verdicts
while its own prose stated several; the header now says where the prose came from and that
no test reads it.

State after the audit: `pytest tests/silentgate` -> 46 passed, 7 skipped; whole repo -> 146
passed, 7 skipped, the pre-existing 100 unchanged. 22 AI-produced files plus the hand-off.

## A0 wave 1 — arrays 20178325 + 20178326 (2026-08-27), and what "the A0 compute is done" actually covered (2026-08-28)

**The premise correction first.** The session opened on "the A0 compute is done." It was not:
`sacct` since 2026-08-27 showed exactly 22 `a0` tasks — A0-cell's 16 (20178325) and
P-PROJ's 6 (20178326) — an empty queue, and `runs/a0/main/` holding 140 staged `.in`
with zero `.out`. Commit `74323dd` says so in its own subject line ("staged, not yet
submitted"); nothing after it submitted. The registered core of block 6A — the 140-SCF
eta(U) grid — had never run. **Submitted 2026-08-28 as array `20183040` (1-140%6),**
preflight `lines=140 to_run=140 stale=0 bad=0`. The trap for the ledger: *a commit that
builds and stages a manifest reads, a day later, as a commit that launched it.* The only
cure is the one used here — read the queue and the `.out` census, not the commit log.

**P-PROJ scored: the A7.1 prediction FIRES at 5x threshold.** |d-eta(Cr)| = **0.487 V**
against the registered 0.10 V trigger — atomic eta 1.155 V (pls 2) vs ortho-atomic
1.642 V (pls 1) at byte-identical geometry and U = 7.15 eV. The projector choice moves
eta by half a volt AND flips which step limits. All four pairs branch-matched (magtot
12/12, 11/11, 10/10, 11/11); per-state dE(atomic-ortho) spans +3.02 to +4.00 eV; the
banked S0 *O pair's +0.27021297 Ry reproduced to <0.0001 meV. Consequences, per the
registration: the fifth grid point is PROJECTOR-MISMATCHED, the whole grid runs in ONE
projector (atomic), the projector delta is its own labelled sub-row — and the label now
extends by the same logic to the Ru 6.73 / Ir 5.91 Xu anchor rows of A0-main.
`src/dft/pproj_readout.py`, `docs/figs/pproj_readout.json`.

**A0-cell wave 1: 15/16 clean; the 16th is a NEW bad node, a049.** Task 9
(`s0_OH__2x1v_mir__u0.0`) died OUT_OF_MEMORY at SCF iteration 5 — 3 oom_kills on a
237 GB grant against QE's own 29.21 GB estimate, while its 15 siblings finished in
6-13 min on other nodes. That is the docs/45 per-node-ceiling signature, and a049 is
**bad node #7** (a024, a050, a088, a196, a220, a223, now a049). Attempt preserved as
`.out.oom_attempt1`; retry = `20183041_9` with a049 excluded. Extraction control on the
15: every base SCF reproduces its source relaxation to <=0.01 meV.

**A6.2 partial signal, verdict withheld.** On the three complete shared U points the
2x1v descriptor sits below the 1x1 one and the gap GROWS with U: dD = -0.233 / -0.304 /
-0.346 eV at U = 1.85 / 3.70 / 5.00. If the trend holds to the endpoints, I_U lands
negative past the -0.30 bin — **"not separable", against the registered additive
prior.** `a0cell_readout.py` refuses to print a span over a subset; the verdict waits
for the u0.0 retry and the u715 rung (array `20183150`, built AFTER P-PROJ scored,
labelled PROJECTOR-MISMATCHED, atomic projector).

**One number worth its own line:** the 1x1 leg (inherited ladder + P-PROJ atomic fifth
point) reproduces P7's withdrawn headline exactly — eta(U=0) - eta(base) = 1.452 -
0.330 = **1.122 V** on five points. A0-main's 19-point Cr arm now has to locate the
crossing inside it.

## A0 wave 2 -- the verdicts, the four-verifier audit, and three traps (2026-08-28)

The cell arrays (20183041_9 retry + 20183150 u715 rung) and A0-main's Cr block
(76/76) landed overnight; both readouts were scored and then adversarially
verified by four independent agents before banking
(docs/figs/a0_verification_findings_2026-08-28.txt). Zero numeric errors; five
distinct defects, all fixed same-day. The traps worth remembering:

1. **`| grep` eats exit codes.** a0main_readout.py crashed on Ru's gap rows
   (a 2-tuple unpack over 3-tuples introduced by the gap_why patch) and the
   banked JSON was silently a stale revision -- unnoticed because the run was
   piped through `grep -E "GAPS|VERDICT|..."`, whose exit code masked the
   ValueError and whose pattern dropped the traceback. Run readouts PLAIN,
   check `$?`, and only then filter.
2. **A control between byte-identical decks is a determinism check, not a
   control.** The A0-main u000 decks differ from the probe u0.0/base decks only
   in the prefix line, so the 0.003-meV "extraction control" measured SCF
   re-run determinism. Renamed honestly in script + JSON; the genuine
   geometry round-trip control is the a0cell one (base SCF vs source
   relaxation, drifts <= 0.01 meV).
3. **A bound quoted across two windows is not a confirmation.** The grid's
   1.177 V swing lives on U in [0,9]; P7's withdrawn 1.122 V headline lived on
   [0,7.15], where the 0.5-step grid reads only 1.072 V (it straddles the eta
   minimum near the 3.87 eV crossing). And eta is still rising at the U=9
   edge, so 1.177 is itself edge-limited. The readout now prints both windows
   and refuses the "confirms" phrasing.
4. **Labels must travel into the artifact, not just the stdout header.** The
   2x1v apex crossing (5.33 eV) is interpolated INTO the PROJECTOR-MISMATCHED
   U=7.15 rung -- on clean points D(2x1v) never reaches 1.6. The
   CELL-CONDITIONAL verdict survives without the rung (clean-point shift
   bound >= 1.13 eV > 1.0; clean-point I_U = -0.155, same INCONCLUSIVE bin),
   and the JSONs now carry the label + robustness fields so no reader has to
   open pproj_readout.json to learn it.

Also recorded: Cr grid magnetization is integer-pinned across all 19 U points
(slab 12, s0_O 10, s0_OH 11, s0_OOH 11; absolute magnetization smooth) -- no
branch hops behind the smooth eta(U); the OOM-retried cell u0.0 SCF is the same
branch as the killed attempt (iteration-1 energy equal to 2e-8 Ry). Stray
runs/probe/Cr/CRASH is a leftover mkdir failure from an earlier s0_OOH__u0.0
attempt; the surviving output passes QC -- file kept as-is.

## A0 wave 3 -- the full grid, A6.3 INVERTED, and a correction of record owed (2026-08-28)

Array 20183040 completed 140/140 (zero SCF failures, zero A6.5(2) events; the
wave-2 "staged but not yet run" Ru s0_O u673 anchor ran 28 Aug 08:00 and feeds
the banked row). `a0main_readout` scored the two remaining registered readouts;
four adversarial verifiers (rederive / registration / qc-mag / refute,
wf_5bd5616f-7e4) audited BEFORE banking: 0 BLOCKER, 6 MAJOR (all
disclosure/robustness, all fixed same-day -- full reports and the fix list in
docs/figs/a0_verification_findings_2026-08-28.txt, wave-3 section).

**A6.3 VERDICT: INVERTED at U = {4.5, 6.0, 7.5, 9.0}** (margins +0.021 /
+0.177 / +0.340 / +0.464 V). Only U=9.0 clears the top of every measured error
class, so the binary registered prediction rides on that point outright; the
holds-side margins (<=0.031 V) are all below A5.1(b)'s registered 0.20 eV
floor, so the ordering was never POSITIVELY resolved at any U -- production
U=0 included. Refuter's verdict: INVERTED SURVIVES, and is in-model volcano
physics (Ir starts on the 1.6 eV apex, D=1.642 at U=0, and climbs the
weak-binding leg pls 2; Ru approaches the apex from the strong-binding side),
corroborated by the Xu anchor rows reproducing Xu 2015's ordering restoration.
**A7.2: CONFIRMED** (>=3 of 6 metals flip: Cr [3.5,4], Ir [3,4.5] --
saddle-conditional bracket -- and Ru [7.5,9]; unrun metals can only add flips).

**CORRECTION OF RECORD OWED (Frank):** A6.3 registers the grid over "Ru and Ir
as well as the 3d metals", and A7.2/A7.3 name Mn, Fe, Ti as blind metals; the
arm as built runs Cr/Ru/Ir only. The Cr 19 / Ru 7+1 / Ir 7+1 allocation was
chosen by the entrant 2026-08-27 with no dated amendment, against docs/43's
own scope-change rule (~~:279~~ — see CORRECTION below). The readout now discloses the shortfall
(caveats.coverage_shortfall); a dated correction/amendment recording the
roster decision is owed, and whatever stays unscored at the Oct 15 freeze is
WITHDRAWN-UNSCORED under A7.7, not quietly dropped.

> **CORRECTION 2026-08-29 (wave-5 audit).** The citation `docs/43:279` above is
> **retracted**. Line 279 is the fourth row of the 1B hp.x internal-gate table
> ("symmetry-equivalent perturbed atoms | agree within 0.05 eV | an inconsistent
> projector or k-set") and says nothing about scope. The governing rule is
> **docs/43:4-5** — "Nothing in this document may be edited after that deposit;
> corrections go in a dated addendum at the bottom with the reason" — which is
> what makes an undated roster change a defect. (Amendment 5 at docs/43:932 was
> proposed as the replacement pointer and is **also wrong for this purpose**: it
> governs the five DEFERRED literature items D3/D5/D7/D9/D10, not scope
> generally. docs/59 §1 currently cites 932 alone; that citation is narrower
> than the claim it supports and should read 4-5.) The underlying finding — the
> allocation was chosen with no dated amendment — **stands unchanged**; only the
> registration pointer was wrong. Wave-4 fixed this in docs/59 and did not look
> for the second copy here, because its finding was scoped to that file alone.

New traps for the pattern file:
1. **A binary "X at points P" verdict hides that the points are not equally
   credible.** Bank the per-point margins and name which points carry the
   verdict against the measured error classes; do not present four inversions
   when one clears the error bar.
2. **A "cancels by construction" claim has a regime.** "Identical gas refs =>
   no cross-metal eta difference" is true only when both metals share a pls;
   every inverted A6.3 point pairs Ir pls 2 with Ru pls 3, where the absolute
   H2O reference enters one-for-one. State the scope of a cancellation, not
   just the cancellation.
3. **Labels must travel is not once-per-campaign** -- the same trap banked in
   wave 2 for a0cell recurred the SAME DAY in a0main (anchor rows were bare
   `anchor: true` in the JSON). Check every artifact a scorer writes, not the
   one the trap was found in.
4. **A duplicated physical constant is a fork in the road** -- qe_qc's
   truncated RY_EV (13.605693122) is what every banked eV number used, while
   the scorer declared the full 13.605693122994 for one print. Single-source
   it (done); never let two precisions of one constant coexist.
5. **nspin=1 is a measured caveat, not a default** -- gate (h) had already
   adopted AFM with a 33-64 meV class; margins under that class are
   state-conditional and must say so where the number is used.

## A0 tranches 2b/3 -- the first convergence failures, the pilot verdict, and a one-byte lesson (2026-08-29)

Array 20196817 (tranche 2, Mn/Fe, 59 tasks) and array 20196856 (tranche 3
stage 1, TiO2 geometry chain, 4 tasks) both drained COMPLETED. Strict QC: 57
of 59 tranche-2 SCFs clean with Lowdin populations; 3 of 4 Ti relaxations
cleanly converged.

**Fe s0_OOH pilot verdict (rule registered pre-launch in build_a0main_w2.py):
ALL THREE GUESSES PASS.** m010/m030/m070 all land 0.019-0.023 meV from the
banked relax reference -34804.1641 eV (gate: 5 meV), all at totmag 22.98 --
the relax branch; the 0.5-start trap (+276.60 meV, totmag 23.86) is escaped by
ANY of the three guesses, and the three collapse to one state within 0.004
meV. Closest wins mechanically: m010 -> starting_magnetization(1) = 0.1 on all
8 ladder rungs (build_a0main_w2b.py re-derives the verdict from the outputs
via strict qe_qc and refuses to build on disagreement). The ladder's u530 rung
is byte-identical to the winning pilot deck except the prefix line -- the
determinism control.

**First A0 convergence failures (A6.5(2) finally fires, where it predicted):**
Fe s0_O u300 (accuracy ~1e-3 Ry oscillating, totmag drifting 22.44 -> 22.25)
and u450 (oscillating 1.8e-6 -> 1.1e-5 Ry around conv_thr 1e-6) both stopped
at 200 iterations -- mid-window between U = 1.5 and 5.3, exactly where
A6.5(2) registered that convergence would be worst. Escalation rung (i)
applied: s0_O__u300__r1 restarts from the retained u150 density,
s0_O__u450__r1 from u530 (u300/u450 are each other's nearest neighbours but
both failed). Runner 48_a0_repair.slurm = 46 + a density-seeding step, KEEPING
the inline projwfc -- routing repairs through the S3 chain runner would have
silently reproduced the LIT-1 no-Lowdin failure A6.5(1) exists to prevent.
A8.4 note: Fe s0_O pre-repair failure rate is 2/8 = 25%, over the 20% line;
reported either way, and the failed .outs stay on disk.

**Ti s0_OOH relax failed** (SCF after the first ionic step, 200 iterations,
accuracy 0.0097 Ry and still falling; zero bfgs steps). Rung (i) is
inapplicable to a relaxation (no neighbouring-U point exists; the failed run
retained no density), so rung (ii): s0_OOH_r1 halves mixing_beta to 0.15 and
continues from the last trajectory geometry, spliced VERBATIM with pw.x's own
constraint flags (14/21 atoms had moved, max 0.076 A -- the walk had started).
If r1 fails too: rung (iii), NOT_CONVERGED; A7.3's registered text already
conditions its denominator on "a converged *OOH geometry", so the readout
shrinks instead of blocking.

New traps for the pattern file:
6. **A line-wise diff cannot certify "byte-identical".** `U_LINE`'s `\s*$`
   swallows the file's final newline when the U card is the last line, so
   every tranche-2 nonzero-U deck is one byte short of its source -- and the
   zip-over-splitlines assert was structurally blind to it. QE is indifferent
   and every energy stands; but the production-U decks' "byte-identical
   except the prefix line" claim was literally false by one byte.
   Tranches 2b/3 restore the newline and assert `a == b` on full strings.
   When the claim is bytes, compare bytes.
7. **A repair path can silently lose an invariant the main path carries.**
   The obvious repair route (44_chain.slurm) has no projwfc step; using it
   would have stripped exactly the Lowdin populations A6.5(1) mandates, on
   exactly the points (magnetically frustrated, mid-U) where the valence
   story matters most. When a side path substitutes for the main path, diff
   their guarantees, not just their outputs.

## A0 tranche 2c -- the second escalation round (2026-08-29)

**Rung (i) worked once and failed once, and the difference is physical.**
Fe s0_O u300, seeded from the retained u150 density, converged in 202 s and
landed at totmag 22.90 -- off the 22.25 the unseeded run had been drifting
toward. u450, seeded from u530, held 21.98 and oscillated between ~1e-4 and
~8e-2 Ry for most of its 200 iterations, reaching ~1.2-4e-5 Ry only over the
final ~17 and never conv_thr 1e-6. The moments across the whole ladder say why: 18.91,
21.36, 22.90 up to u300, then 21.98, 21.99, 22.00, 21.99 from u530 on. u450
is the crossing point between two nearly degenerate branches, and a density
seed can put a point ON a branch but cannot break a tie between two. Rung
(ii) (halve beta) now runs from BOTH converged neighbours, with the lower
converged energy pre-declared as the banked point.

**The diagnosis that mattered was geometric, and grep found it, not the SCF
log.** The Ti s0_OOH relax kept failing its SCF, which reads like a numerics
problem. It is not. `qe_slab.py` starts every Ti adsorbate ~3.1-3.2 A off
the nearest Ti; *O and *OH walked DOWN into 1.735 A and 1.829 A bonds over
36 and 56 ionic steps, while *OOH walked UP -- 3.167 -> 3.263 -> 3.325 ->
3.414 A over its three steps -- into the desorbed-radical region, where the
chain's nspin = 1 convention cannot spin-split the half-occupied state. The
plateau-with-spikes limit cycle is the symptom; the starting height is the
cause. Fix: re-anchor the adsorbate to the mean of Ti's own two converged
Ti-O bond lengths and restart, alongside a plain continuation.

New traps for the pattern file:
8. **Check whether the "fix" is already on before proposing it.** The
   obvious escalation for a charge-sloshing SCF is `mixing_mode =
   'local-TF'`. It had been on campaign-wide since `qe_slab.py:175` -- a
   grep that took ten seconds and would have made the whole escalation a
   no-op had it been shipped. An earlier grep of the same deck had MISSED
   it, because the pattern listed `mixing_beta` and not `mixing_mode`; the
   absence of a hit for a key you never searched for reads exactly like the
   key being absent. When a diagnosis rests on a setting NOT being present,
   grep for that setting by name.
9. **A convergence failure can be a measurement, not an error.** Three
   ionic steps of a relaxation is not evidence that a species does not
   bind -- the two states that DID converge on the same surface needed 36
   and 56. But the direction of travel over those three steps was the whole
   diagnosis. Read the trajectory, not just the last line.
10. **Escalating a ladder past its last registered rung is a decision, not
   a repair.** `mixing_ndim` and `electron_maxstep` are not rungs A6.5(2)
   names. They are declared as a dated extension whose authority is bounded
   by construction: it can only FILL the gap rung (iii) would leave, so if
   it fails the recorded outcome is byte-for-byte what (iii) alone would
   have recorded. Bound the amendment by what it can change, not by
   promising restraint.
11. **A gate token that looks like a parameter.** `43_submit_s3_wave1.sh`
   runs the driver's dry preflight with concurrency hard-coded to 1, and the
   driver then refuses any manifest whose header declares a different
   `NCONC` -- so the header's NCONC is a preflight TOKEN, unrelated to the
   `%cap` the array is actually submitted at. A manifest honestly declaring
   the concurrency it wanted (2) was refused; declaring 1 and submitting at
   %2 is the campaign's established (if unobvious) pattern. The refusal was
   loud and cost nothing, which is the system working -- but the header now
   says what the field is, so the next reader does not have to rediscover it.

## Wave-4 audit before banking tranche 2c (2026-08-29)

59 agents: 5 auditors on distinct dimensions, one adversarial refuter per
finding, one completeness critic. 53 findings raised, **38 refuted, 15
survived**, plus 9 from the sweep. The refutation rate (72%) is the point of
the pattern: most plausible-sounding findings die on contact with the files,
and the ones that live are worth the whole run.

**The BLOCKER, found independently by three dimensions.** The readout's
repair-selection branch collapsed "has not run yet" into "failed", so a row
whose registered repairs were still in flight banked the sentence *"all 3
registered repairs also failed"* — i.e. that the A6.5(2) ladder was EXHAUSTED
and rung (iii) NOT_CONVERGED had been reached. The `lost` list already carried
the distinction; the message threw it away and used `len(cand)`. The same
script got it right for Ti two hundred lines away. Fixed: pending and failed
are now counted and phrased separately, and only an all-failed set may say
"A6.5(2)(iii)".

**A prediction was being omitted while its sibling was reported.** A7.2 and
A7.3 are scored from the SAME banked rows. The readout computed and reported
A7.2 (CONFIRMED) and computed no A7.3 at all — and A7.3, once computed, stands
at 3 of 5 against a registered threshold of ≥4. Reporting the one that passes
and silently omitting the one that does not is the exact failure pre-
registration exists to prevent, and no auditor was even assigned to it: the
completeness critic found it by asking what nobody had been asked. A7.3 now
scores in the artifact, and Ti's *OOH convergence is named as the deciding
metal.

New traps for the pattern file:
12. **"Not yet run" and "failed" are different claims, and code that merges
   them will eventually publish the wrong one.** The distinction survived all
   the way to the message-formatting line and died there. When a status string
   is assembled from a richer structure, check that every distinction the
   structure makes is still present in the string.
13. **Fixing a conflation can create its own.** Splitting "control FAIL" from
   "control INCOMPLETE" introduced a third case neither branch handled: a
   control deck that RAN and produced no energy. `_final_ry` returns None for a
   missing file and for a file whose SCF died, so a convergence event was about
   to be reported as pending data — the mirror image of the bug just fixed, in
   the code written to fix it.
14. **An affirmative claim over an empty measurement.** With zero scored rows
   Ti printed "no pls flip inside the measured band" and banked `pls_flips: []`
   — byte-identical to what a complete, genuinely flat grid banks. A consumer
   reading that field could not tell "measured, no flip" from "nothing
   measured".
15. **A causal claim the instrument cannot see.** The gap line asserted "not
   yet run; not a convergence event" for holes whose actual cause was two
   failed relaxations upstream. The readout reads one directory and cannot
   know why a deck is absent; it now says only what it can see, and looks up
   the relaxation when there is one to look up.
16. **Check a number's interval before quoting it as a plateau.** "Plateaued at
   ~1.5e-5 Ry for all 200 iterations" was written from the tail of the file.
   The run actually oscillated between ~1e-4 and ~8e-2 Ry for most of those 200
   iterations and only reached ~1.5e-5 in the last ~17. Reading the last screen
   of a log and describing it as the whole run is a distinct error from
   misreading a number.
17. **A defence that contradicts the design two sentences later.** "Changing
   where the walk STARTS cannot bias where it ENDS" was written to show the
   re-anchored Ti deck was not outcome-tuned — immediately above a selection
   rule that exists to report the basin gap between two different starts. If
   the start could not bias the end there would be no gap and no reason to
   build the deck. The true defence is narrower and checkable: the distance is
   computed mechanically, the rule was fixed first, and no energy was known.

Note on scope: `runs/a0/m_a0_repairs2.txt` is left exactly as launched, with
its original header wording, because it is the record of what actually ran.
The corrections above are made in the builder docstring, docs/59 and here.

## A0 wave 5 (Ti stage 3 landed; A7.2/A7.3 closed) — 2026-08-29

47-agent adversarial audit over the Ti *OOH landing and the two verdicts scored
off its rows: 38 findings raised, 26 refuted, 7 survived, 7 more from the
completeness critic. Five verifier agents died on API safeguards; their findings
were re-checked by hand rather than counted as refuted. Traps 18–24 below.

18. **A self-test that re-derives NUMBERS will sail over a corrupted NARRATIVE.**
    `build_a0main_w2c.rederive()` re-derives every quantitative docstring claim
    from disk and dies on disagreement — and it passed while the surrounding
    prose said the *opposite* of what happened, attributing the u530 branch's
    non-convergence to the sibling that converged. The corruption was introduced
    by *applying trap 16's correction*: a two-line string replacement collapsed
    into `"converged in 202 s andscillated"`. Guard: after applying a text
    correction, **re-read the replaced span**. The edit succeeding is not
    evidence the result is well-formed, and a numeric self-test will not catch it.

19. **A registered threshold applied to the wrong quantity still looks
    registered.** A5.1(b) leg 2's 0.20 eV floor is a **G_max gap**
    (docs/43:958-964); the readout applied it to `eta(Ir) - eta(Ru)` and never
    evaluated leg 1 at all. Because the *number* was registered, nobody re-read
    what it was registered **on**. Scoring it correctly reversed the shape of the
    finding: legs 1+2 pass exactly where the ordering INVERTS (U ≥ 4.5) and fail
    exactly where it "holds", so the banked sentence "the ordering was never
    positively resolved at any measured U" was withdrawn. Guard: when quoting a
    registered threshold, quote the **quantity** in the same breath.

20. **A verdict that is a bare count can hide a perfect confound.** A7.3 scored
    3 of 6 over the floor. The 3 over are *exactly* the 3 nspin=2 decks; the 3
    under are *exactly* the 3 nspin=1 decks. A count cannot show that, and the
    status field read as settled while Ru sat 15.5 meV from flipping the verdict
    — inside a measured, still-open error class (33–64 meV) whose re-run is owed.
    Guard: bank the partition and the distance-to-threshold beside any count.

21. **Bypassing the canonical path silently drops the side effect that path
    owns.** `build_a0main_w3b` wrote a probe deck through `write_probe` instead
    of `cmd_build`, which is the only code that appends to `probe_manifest.json`.
    The state that DECIDES A7.3 was therefore invisible to `probe_eta.py` and
    escaped GATE 1 entirely, while a live script printed "No variant has a
    complete slab + OH + O + OOH set yet" with the converged output on disk.
    Guard: if you bypass a builder, enumerate its side effects and reproduce them.

22. **"Not emitted by X" is vacuous when nothing is emitted by X.** A hand-written
    caveat isolated the Ti *OOH provenance as "the only geometry not emitted by
    `gen_rutile.py`" — but `gen_rutile.py` emits 6-atom bulk SCF cells and no
    slab or adsorbate at all, so the sentence was true of every row and isolated
    nothing. The real module is `qe_slab.py`, placement in
    `hea_oer/surfaces_rutile.py`. Guard: a uniqueness claim needs the negative
    case checked, not just the positive one.

23. **A fixed defect can recur in a sibling path that never inherited the fix.**
    `surfaces_rutile.adsorbate_starts` documents *OOH left desorbed on Mn, Fe and
    Ni in the 2026-07 campaign and exists as the remedy, with registered pull-in
    distances `PULL_TO = (1.70, 2.10)`. The MACE screening path uses it; the DFT
    deck path (`qe_slab.py`) calls single-start `add_oer_adsorbate_at` and never
    inherited it — which is why TiO2 *OOH failed twice at ~3.2 Å. The repair
    anchor (1.7819 Å) landed inside the registered `PULL_TO` window, i.e. the
    campaign's own remedy re-derived by hand. Guard: when a defect recurs, grep
    for an existing fix before building a new one.

24. **A fragility test must ask what happens if the row is REMOVED.** The first
    version of the A7.2 census-robustness check flagged any pls value occurring
    exactly once, which marked Mn fragile — but Mn has three distinct pls values,
    so losing any one still leaves a flip. Membership rests on a single row only
    when there are exactly two pls values and one is a singleton (Fe, Ru).
    Guard: test the counterfactual, not the shape.

## A0-SPIN Stage 0 (2026-08-30) — two traps from a control set that ran, converged, and could not be scored

Array `20221409`, 10/10 COMPLETED. Full readout: docs/62. The machinery passed
(index rule 8/8, symmetry/k-set guard 10/10, P11 reproduction 8/8 to 0.0437 meV
across a 32× decomposition change, Δc_M(0) to 0.052 meV against a 15.5 meV
decision, variational floor fired once on the Ir slab exactly as predicted).
These two traps are what it cost to find that out.

25. **A control's acceptance criterion can be unsatisfiable by a property of the
    state it runs on — and the job will still run, converge, and exit 0:0.**
    docs/61 §A11.7 required both null-seed Ti decks to "reproduce the banked
    nspin = 1 Ti energies with totmag ≈ 0". `Ti slab` (144 electrons, closed
    shell) did exactly that: totmag −0.00 at all 25 iterations, +0.339 meV.
    `Ti s0_OOH` (157 electrons, odd) **cannot**: its unpolarised solution is
    unstable, so from a genuinely zero seed the SCF broke symmetry on QE's own
    randomised starting wavefunctions (totmag 0.00 → 0.43 → 1.00, locked 1.04)
    and fell 153.07 meV. Calling that a FAIL is a category error — the deck did
    not violate the control, the control was not a statement that could be true
    of that deck. Nothing in the exit code, the convergence, or the guard output
    says so; only reading the electron count and the totmag trajectory does.
    **Guard: before registering a control criterion, check it is satisfiable
    against each deck's own physics — here, electron parity and the stability of
    the reference solution — not merely against the code path.** The corollary
    is the good news: a criterion that cannot be met is often measuring something
    better, and the honest move is to re-register it as what it is (docs/62
    §5.2 splits it into an index-rule leg that passes and a stability leg that is
    reported, not scored), never to score the run against the words as written.

26. **The metal with the smallest margin is not the metal with the most
    information, and an amendment written around the former can sequence the
    latter last.** docs/61 is built end to end around Ru's 15.5 meV: §A11.0 opens
    on it, §A11.1's reframe exists to keep a large spin effect from being read as
    a large score change on it, §A11.10 sequences Ru first and Ti last. Stage 0
    then measured a 153.07 meV single-state spin instability on **Ti**, which is
    larger than the entire 112.5 meV Ti would have to travel to cross the floor,
    against Ru's total measured c_M effect of 7.094 meV. Proximity to a threshold
    ranked the metals; sensitivity to the treatment being tested did not, and
    nobody had measured it. **Guard: when an arm exists to price a treatment,
    rank the legs by the expected size of the treatment effect, not by each leg's
    distance to the threshold — and if the two rankings disagree, say so in the
    registration.** Note what this does *not* license: the A11.1 cancellation is
    arithmetic and still binds, three of D_Ti's four terms are unrun, and a
    U-independent offset cancels exactly. The trap is about *where to look*, not
    about what has been shown.

**27. An energy-only conv_thr can "converge" an SCF at very different magnetic
moments when the magnetization landscape is flat -- the converged flag does not
pin the magnetic state.** (2026-08-30, S0(h) s0_O AFM; mechanism corrected by
the docs/64 verification pass, which REFUTED the first draft's "mixing selects
a distinct solution" reading.) Three formally converged endpoints exist at the
byte-identical geometry: anchor totmag -1.62 (E = -3302.93769258 Ry),
attempt-2 -1.70 (-0.151 meV vs anchor), r1 under halved mixing -1.90
(-0.710 meV vs anchor) -- a 0.28 mu_B moment spread across 0.71 meV, with r1's
moment still drifting monotonically (-1.82 -> -1.90 over its last ~20
iterations) when conv_thr = 1.0e-6 Ry (0.014 meV) fired. The moment is nearly
a zero mode: shifting it ~0.3 mu_B costs under 1 meV, so the energy criterion
cannot pin it, and where the SCF stops depends on solver path and run history.
Corollaries: (a) a converged energy from a repaired or re-mixed deck is not
automatically comparable to its siblings -- check the moment's STATIONARITY
(plateau over the closing iterations), not just the flag; (b) on such a state,
deeper relaxation compounds the drift and the BFGS walks -- recording
NOT_CONVERGED beats escalating to a rung that "succeeds" by banking an
unpinned row silently.

## The 2026-08-31 directive session — freeze amended, every open election executed, and one supersession

**Dated correction rows (2026-08-31):**

- **S7 re-key.** The §E S7 row's "Oct 8–15" window re-keys to the amended
  P-DISPOSITION date: S7 (freeze, figure pack, pre-submission assertions) now ends at
  the entrant's REPORT LOCK line, backstop Nov 5 2026 8:00 pm ET (docs/43 dated
  addendum of 2026-08-31, recorded from the entrant's verbatim directive; docs/66 §1).
  The sweep stays self-executing at the backstop.
- **Ledger-wide re-key.** Every "Oct 15" elsewhere in this ledger (the §E S7 row
  above; the narrative use at :2147) reads through the same amendment; no threshold,
  scoring rule, or other registered date moved (Sep 18 A10 and the Sep 20
  displacement decision are independent and unchanged).
- **Supersession (docs/60 §10).** docs/60 §10's MAY-NOT "treat 'NOT MET' as an A7.7
  disposition" is narrowed by docs/43 A11.R2's dated supplement: the bare status
  token still takes no disposition row; the registered middle-band disposition is
  SCORED — MIDDLE BAND / NOT MET, reported only with its count and
  a7_3.conditionality, never bare.
- **Supersession (docs/63 §6).** docs/63 §6's MAY bullet — the "exceeds … so 'NOT MET
  is not settled'" phrasing — is superseded on that point by the restated
  level-vs-swing sentence of record (docs/43 A11.R3, [DOCS/60 §6 FACT 2 RESTATED
  2026-08-31]): the AFM levels (−25.9/−32.5 meV at U = 0) neither bound nor close
  Ru's 15.5 meV required SWING; "not settled" stands on the unmeasured U-dependence,
  pending the item-10 probe. Conclusion unchanged (docs/63:230).
- **Elections index.** All docs/65 rows elected under the entrant's 2026-08-31
  directive; record and verification provenance in docs/66; instruments: docs/43
  A11 + addendum, docs/59 §3c GRANTED, docs/67 (Mn AFM arm design).

## A11 wave-1 drain — a sick node, an instrument whose whitelist predated its own evidence, and an over-pull (2026-09-01)

**Dated correction rows (2026-09-01):**

- **Node a171 is sick; exclude it.** Every one of the four tasks Slurm placed on a171 on
  2026-08-31 died or hung, and none of the other 102 did: 20262064_3 / 20262064_6 /
  20262090_1 were OOM-killed at zero SCF iterations (Slurm epilogue: `error: Detected 2
  oom_kill events in StepId=20262071.batch` and `Detected 1 oom_kill event in
  StepId=20265928.batch`; `prterun noticed that process rank 0 ... exited on signal 9`),
  and 20262091_1 ran 19 h 11 min at zero iterations with its `.out` untouched for 23 h
  (`scontrol show node a171`: FreeMem=333 MB of RealMemory 257,400 MB, CPULoad 325.17 on
  128 CPUs — something outside our job held the node's memory). Cancelled by hand at
  2026-09-01 19:06 EDT after ≈2,450 SU of idle burn; the standing EXCLUDE list is now
  `a024,a049,a050,a088,a196,a220,a223,a171` (+ a120,a200 at submit time). **Rule:** a task
  whose wall-clock exceeds its siblings' by an order of magnitude with zero iterations is
  not "slow", it is dead — check `.out` mtime and `scontrol show node` at the first status
  read, not the second day. **Rule:** the four partial `.out`s were moved to
  `<stem>.out.a171_2026-08-31` BEFORE re-queueing; a re-run overwriting a first attempt
  would have deleted the only evidence that there was one (the 2026-08-29 lesson, applied).
  RCAC ticket text, for the entrant to send if wanted: "Node a171 in the shared partition
  had FreeMem 333 MB with CPULoad 325 while allocated to a single 128-rank job at
  2026-09-01 23:04 UTC; three prior jobs on it were OOM-killed at start (IDs above). Please
  check for leaked processes / drain it."
- **The census whitelist predated the evidence it would read.** `a0spin_census.py` CEN-d
  admitted only `.in`/`.out` (+ skipped `.projwfc.out`) under `runs/a0/spin/<M>/`, so the
  first census on the drained tree REFUSED on `<stem>.lowdin.txt` — the campaign's own
  registered A6.5(1) artifact, banked 235× under runs/a0/main. Also unlisted: the runner's
  `.projwfc.in` and the attempt class above. Fixed by CLASS (test S8; a stray `.csv` and an
  undated `.attempt1` still die), and controlled: run A = the census as first committed with
  the sidecars moved aside; run B2 = the widened code on the full tree; **identical on every
  scored field.** **Rule:** when you commit a readout before its evidence exists, enumerate
  the classes the *pipeline* will deposit beside that evidence (extractor outputs, runner
  inputs, preserved attempts), not just the classes that exist at commit time — and keep a
  run-A/run-B identity check as the price of any post-hoc widening.
- **Over-pull.** The pull list took `*.run.in` (the runner's per-job scratch copy with
  `outdir`/`pseudo_dir` rewritten) — 106 files no banked tree carries. Deleted locally; the
  docs/62 pull shape (`.out`, `.projwfc.out`, `.projwfc.in`, and now `.lowdin.txt` produced
  here) is the shape. Slurm logs are not a repo class either; they live in the session
  scratchpad and their decisive lines are quoted above.
- **Physics rows banked today** (numbers in docs/68): 0 of 15 spin-polarised Ru SCFs
  converge at U = 9 (11 FM-seeded 1×1 + 4 AFM 2×1v), resolving every (Ru, state, u900)
  cell to EQUALISED-BY-SELECTION(nspin=1) under the registered rule and making A7.3
  conditionality fact (2) a measured sentence; Ir slab u000 contingency FIRES (three seeds
  +0.58–0.60 meV above the floor) → 0.05 extension built and queued, u900 does not fire;
  Mn E1: P-A +664.6 meV, P-B +1,219.5 meV above FM with AFM solutions genuinely held →
  measured null, FM stands, MN-AFM-CORE does not trigger.

## A11.R6 — the pre-named ladder ran and returned nothing; a negative that had to be bought (2026-09-02)

**Dated rows (2026-09-02):**

- **The ladder is exhausted and the cells did not move.** 16 rows × 2 rungs, 32 SCFs,
  5,216.7 SU: rung 1 (β 0.15 / 400 steps) 0 of 16; rung 2 (β 0.075 / ndim 16 / 600 steps)
  0 of 16. Every (Ru, state, u900) cell stays EQUALISED-BY-SELECTION(nspin=1); the
  a7_3_spin table is byte-identical to the pre-ladder FINAL census. Outcome (a) of the
  three A11.R6 pre-interpreted it. **The registration bought exactly what it was written
  to buy: the right to say "and two pre-registered escalations" instead of "we did not
  try".** Cost of that clause: 5,216.7 SU, 8 % of the remaining balance.
- **The decisive number is a control, not the failures.** The nspin = 1 twins in the same
  cell, geometry, code and threshold converge in **25 iterations at 5.9e-7 Ry**, while the
  spin-polarised rows spend 1,200 iterations across three mixing settings and never come
  within **595×** of the same threshold. Without that twin the result reads as "our mixer
  struggled"; with it, it is a statement about the solution space. **Rule: when reporting a
  non-convergence, always find and quote the nearest converging neighbour that differs in
  exactly one setting.** The campaign already had this control on disk (it was the NM leg
  of the S0(h) probe) and nearly wrote the weaker sentence.
- **Deeper mixing history is not monotone.** Rung 2's best accuracy beat rung 1's on 10 of
  16 rows and was **worse on 6**. A ladder whose rungs are "more of the same damping" cannot
  be assumed to improve a row; the ladder's value was that both rungs were **named before
  either ran**, so the 6 regressions are data rather than an invitation to a third rung.
- **A pre-interpreted registration removes the temptation at the moment it appears.** When
  16 of 16 failed a second time the obvious next move (occupation-matrix control, a smaller
  U, a different mixer) was already out of scope by the entrant's own dated line. That is
  the mechanism working: the decision was made when nothing was known, so the outcome could
  not select the method. Any further rung now requires a new dated line and must disclose
  that it was chosen after seeing this.
- **The 15→16 count.** docs/68 §2 quoted "0 of 15" while the sixteenth row was still
  running; corrected the same day in docs/68 §2/§8, docs/58, docs/60, docs/63 and
  tasks/todo.md. **Rule: never quote a census whose population still has a job in the
  queue — say "0 of 15 terminal, 1 running".**

## 2026-09-02 (later) — I mixed two conventions for the same distance, in the paragraph that names both (2026-09-02)

docs/68 §8 reported the spin-equalised census and wrote "Ru gains 3.5 meV and stops 4.3 meV
short", "Ti gains 8.4 meV", "Ir loses 4.6 meV". Those are `0.10 V − span/2` read as meV.
The campaign's distance-to-floor convention, set in docs/60 §6 and used for the number
every later document quotes, is **twice** that: `2 × (0.10 V − span/2)`, the change in
|Δc_M| the metal would need — which is why Ru's as-built distance is **15.5 meV** and not
7.8. So the paragraph put 4.3 meV in the reader's hand while the sentence beside it, and
every other document, said 15.5 — a factor-of-two comparison the reader is invited to make
and cannot make correctly. docs/63 §6 and docs/60 §6 both *forbid* exactly this
level-vs-swing mixing, in the same campaign, about the same metal.

Worse, the table one line above carried `D_M` in eV, and under the correct convention **the
change in distance IS D_M** (Ru −0.0070 eV → 15.5 → 8.5 meV). The right numbers were
already in the row; the prose restated them in a different unit and lost the identity.

Found by the docs/70 completeness critic, then re-derived from the banked census before
anything was changed. Corrected in place with a dated note (docs/68 §8, docs/70 §8.5).

**Rules.**

- **A distance needs its convention stated at the point of use, not inferred from a sibling
  document.** One clause — "distances are 2 × (0.10 V − span/2) throughout" — would have
  made the error impossible and is now in the text.
- **When a table already carries a quantity, the prose must reuse it, not re-derive it.**
  The re-derivation is where the unit slipped; the identity `Δdistance = D_M` would have
  caught it instantly.
- **A convention error survives every numerical check.** The census was byte-identical
  across three runs, all assertions PASS, and the arithmetic was right — the error lived
  entirely in what the number was *called*. Verification that only re-runs the pipeline
  cannot see this class; only a reader comparing two documents can.

## Correction of record, 2026-09-03: the RuO₂ magnetic ground state — the literature reversed in 2024 and this repo still asserted the 2017 claim as fact

**The error.** In three places — `docs/41:268-271`, `docs/41:275-277`, `docs/41:512-515` — and in
**deck-generating code** at `src/dft/probe_decks.py:250-253`, the campaign asserted as established
fact that RuO₂ is an itinerant antiferromagnet, on Berlijn et al., PRL 118, 077201 (2017). docs/41
went further and used the premise to call `qe_slab.py:44-48`'s "itinerant and non-magnetic" comment
**"factually wrong"**. A grep for `altermagnet|muSR|Hiraishi|Kessler|Smolyanyuk` across `docs/`
returned exactly one hit before today — `docs/68:311`, a *prohibition* on discussing altermagnetism,
not a citation. The 2024 reversal was absent from the record for roughly two years of literature.

**What the measurements say.** Three sources, each opened and its abstract read on 2026-09-03
before this row was written:

| source | bound on the ordered Ru moment | vs the ≈ 0.05 μ_B diffraction value |
|---|---|---|
| Hiraishi et al., **PRL 132, 166702 (2024)** (arXiv:2403.10028), μSR on single crystals, 5–400 K, muon sites computed to exclude accidental cancellation | **≤ 4.8(2)×10⁻⁴ μ_B** | **104× below** |
| Keßler et al., **arXiv:2405.10820**, μSR **+** neutron diffraction | **≤ 1.4×10⁻⁴ μ_B** (bulk), ≤ 7.5×10⁻⁴ μ_B (films); prior neutron peak re-assigned to **multiple scattering** | **357× / 67× below** |
| Smolyanyuk, Mazin, Garcia-Gassull & Valentí, **PRB 109, 134424 (2024)** (arXiv:2310.06909), DFT+U | stoichiometric RuO₂ is described by a **smaller U than the U required to have magnetism**; Ru vacancies aid a magnetic state | supplies the mechanism |

Hiraishi's verbatim conclusion: "*the AFM order, as reported, is unlikely to exist in the bulk
crystal.*"

**Scope, so the correction does not over-claim in the other direction.** What is refuted is **bulk
long-range order**. Surface moments on a (110) slab are a different question and a bulk μSR bound
does not exclude them. Every sentence in the report reading "RuO₂ is non-magnetic" must carry
"in the bulk".

**What changes.** docs/41's "for RuO₂ that is factually wrong" is **WITHDRAWN** — the code comment
it rebuked is the reading the bulk evidence supports. Liang, Bieberle-Hütter & Brocks, JPCC 126,
1337 (2022) is **downgraded from mechanism to hypothesis**: its 0.41–0.49 V rests on an AFM
ordering the bulk evidence excludes, so its ~0.3 eV can no longer be cited as the known cause of
the Ru descriptor deficit. The production convention for Ru — nspin = 1, U = 0 — is **unchanged and
better supported than when it was chosen**.

**What does not change.** No banked number moves. Every P7 and S0(h) energy is a measurement of
what a magnetic SCF solution does to adsorption energies at this protocol, and that stays true
whichever solution nature picks. The `spin` deck variant emits byte-identical decks: the two code
edits made today are **comment-only, 28 inserted lines and 0 deleted**, verified by
`git diff --unified=0 | grep -vc '^+\s*#'` returning 0 and by the full suite at 293 passed / 8
skipped.

**And it strengthens the campaign.** Gate (h) returned **4/4 ADOPT_AFM** on the RuO₂ anchors — the
AFM solution **80–144 meV below** NM under this campaign's Hamiltonian — and adsorption energies
move **33–64 meV** when the anchor is AFM (docs/43:1638-1644). That is no longer an adoption of an
experimental ground state. It is **the campaign's own thesis instantiated on its benchmark anchor,
with an independent experimental check**: the method prefers, by 80–144 meV, a magnetic state that
experiment excludes at the 10⁻⁴ μ_B level, and the answer moves 33–64 meV because of it. It is the
strongest silent-premise example in the ledger, and it is not on a proxy.

**Open, and the entrant's to write.** The four gate-(h) 2×1v AFM relaxations stay on HOLD
(0 built; scope resolved 2026-08-30 as STANDALONE_FOUR). Their justification has changed — they
would relax into a state the bulk evidence excludes — so they are now a **sensitivity arm** rather
than a ground-state adoption. This row supplies the new information and decides nothing.

**Flagged post-hoc, registered against nothing.** A11.R6's 0-of-16 non-convergence of spin-polarised
Ru at U = 9, against nspin = 1 twins converging in 25 iterations (docs/68 §2, §11), is *consistent*
with Smolyanyuk's high-U-artifact picture. Observed after the fact; no prediction scores it.

**Rules.**

- **A cited experimental fact has a shelf life, and a pre-registration freezes the citation, not
  the world.** This premise was three years old at deposit and two years stale at the time of
  writing. **Any load-bearing experimental claim in the report gets a re-check of its citing
  literature before submission** — not a re-read of the original paper, which will not have
  changed, but a forward search for what cited it since.
- **A premise asserted in code outlives the document that justified it.** The claim survived in
  `probe_decks.py` where no document audit would look. **Deck-generating comments that assert
  physics are part of the record and get audited with it.**
- **Withdraw the rebuke, not just the claim.** The most damaging sentence was not "RuO₂ is AFM" but
  "for RuO₂ that is *factually wrong*" aimed at a correct comment — an error that reads as
  authority. Corrections must name the sentence that was aimed at someone else's work.

*Surfaced by the docs/70 ideation round as hole H-1 (docs/70:96-114). Sources verified this session,
not carried from the workflow.*
