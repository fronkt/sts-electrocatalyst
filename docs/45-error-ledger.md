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
