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
| 3 | Estimator bias (η = max − mean exactly, ≥0 by construction, under imposed 4.92 eV) | exact identity; excess vanishes at pls crossing; Cr production U 7 meV from a crossing | MEASURED (algebraic + curves) | LIT-1 ladder; round-2 §6 item 4 | P-PLS (A7, owed) | S6 |
| 4 | Projector pairing (atomic vs ortho-atomic at same U) | +1.45 eV in U value; η consequence BLIND | NOT MEASURED (fires this week) | build history; Xu Table 1 | P-PROJ (A7, owed) | S0(e) |
| 5 | Convergence-failure selection (unconverged states silently dropped) | Co *OOH 4 failures, Ni *OOH 5 | MEASURED as counts; rate now a registered budget row | run logs | A8 (owed) | S3 |

## B. Known-but-unpriced errors (the field knows; nobody prices them)

| # | Class | Size | Status | Evidence | Governed by | Addressed in |
|---|---|---|---|---|---|---|
| 6 | Hubbard-U fragility | 1.12 V on η(Cr); 1.11 eV descriptor span; 0.447 eV intercept span | MEASURED (4-pt ladder; dense grid owed) — **fired P7, withdrew the headline** | docs/41 P7; LIT-1 memo (+ 2026-08-16 correction of record: undoped) | P-FLOOR-U (A7, owed); A6 | S4 (A0) |
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
| S1 | silentgate v0.1: entrant-written core, pluggable readers, CI controls | A9 (owed Aug 22) | blocked on A9 |
| S2 | external census: Xu 810 lock/direction map, span_U halves, Divanis delta-curve, pymatgen+atomate paired audit; literature-coding audit RESTORED | A9 (owed Aug 22) | blocked on A9 |
| S3 | tier_v3 crossed coverage x symmetry x basin, 8 metals; second spin seeds RESTORED beyond *OOH-only where triage allows; dy ladder; Cr 1C + re-Hessian at escape | A8 (owed Aug 24) | decks buildable now, launch Aug 26 |
| S4 | A0 dense U grid 1x1 + Cr 2x1v cell rider RESTORED + bulk hp.x Cr+Ti RESTORED (atomic projector) + slab hp.x one relaunch under 72 h cap RESTORED | A6 + A7 (DEPOSITED) | clear after S0(e)/P-PROJ |
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
