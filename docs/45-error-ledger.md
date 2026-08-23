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
| 1 | Symmetry trap (mirror-plane saddle) | 0.291 V on Ir η (1x1); collapses to −0.018 eV at 2x1v half-coverage (verified from raw outputs 2026-08-16). **Cr 2x1v, 0.5 ML (block 1C, 2026-08-23): an out-of-plane H-carried imaginary mode at i244.7 / i242.8 cm⁻¹ at δ = 0.01 / 0.02 Å — reproducible to 0.8 %, 37 SCFs in one basin at conv_thr 1e-10; H y-curvature negative and quadratic in δ. Analyzer verdict UNDERPOWERED (δ 0.01) / VOID (δ 0.02) because its σ_F is propagated from H−Hᵀ, which here is the forward-difference anharmonic (y,xz) block (doubles exactly with δ), not force noise (measured 2e-7 Ry/bohr from mirror identities). Instrument question → entrant, docs/49 §5** | MEASURED, coverage-conditional | 1C Hessian i167 cm⁻¹ (Ir 1x1); **docs/49 (Cr 2x1v)**; runs/probe/*_cellsym; round-2 synthesis provenance header | P-SYMCOV (A8, owed); **σ_F estimator + am.2/Q4 collision (drafted as docs/47 §A8.7 2026-08-23; entrant's re-authoring owed)** | S3 |
| 2 | Magnetic multistability (basin set at step 1, dragged by pot_extrapolation) | 175 meV Cr *OOH; −405 meV Co *OH; 1.86 µB / −1.19 eV Cr *OOH off-arm confound. **Same-machine, run-to-run (2026-08-22, docs/46): one Cr *OOH deck, two Anvil runs bit-identical at SCF iteration 1, converged to M = 11.00 and 14.90 µB, 8.29 meV apart — not reproducible on a fixed platform; GATE-1 children above their parents by 8.29 / 47.77 meV are this** | MEASURED (in-house); prevalence TRANSFERRED (Fahmy >7,843 MP entries, arXiv:2509.05909) | GATE-1 audits; docs/41; **docs/46 panel + addendum** | A5 spin-seed rules; A8 (owed — basin CONFOUND rule drafted docs/47 §A8.3) | S3 + S0(h) |
| 3 | Estimator bias (η = max − mean exactly, ≥0 by construction, under imposed 4.92 eV) | exact identity; excess vanishes at pls crossing; Cr production U 7 meV from a crossing | MEASURED (algebraic + curves) | LIT-1 ladder; round-2 §6 item 4 | P-PLS (A7, owed) | S6 |
| 4 | Projector pairing (atomic vs ortho-atomic at same U) | +1.45 eV in U value; η consequence BLIND | NOT MEASURED (fires this week) | build history; Xu Table 1 | P-PROJ (A7, owed) | S0(e) |
| 5 | Convergence-failure selection (unconverged states silently dropped) | Co *OOH 4 failures, Ni *OOH 5 | MEASURED as counts; rate now a registered budget row | run logs | A8 (owed) | S3 |

## B. Known-but-unpriced errors (the field knows; nobody prices them)

| # | Class | Size | Status | Evidence | Governed by | Addressed in |
|---|---|---|---|---|---|---|
| 6 | Hubbard-U fragility | 1.12 V on η(Cr); 1.11 eV descriptor span; 0.447 eV intercept span | MEASURED (4-pt ladder; dense grid owed) — **fired P7, withdrew the headline** | docs/41 P7; LIT-1 memo (+ 2026-08-16 correction of record: undoped) | P-FLOOR-U (A7, owed); A6 | S4 (A0) |
| 7 | Coverage / cell (identical variables in one-cus-site 1x1) | 6/9 rows > 0.10 eV (1A); Ir *OOH −0.285 → −0.018 eV | MEASURED (1A) → crossed design owed | docs/43 1A verdict ADOPT_2X1V | A8 (owed) | S3 contrast leg |
| 8 | XC functional | not yet measured here | NOT MEASURED (gated on S0(a) four-deck test) | — | A10 (owed, Sep 18) | S5, "XC only" row |
| 9 | Solvation | ~0.3 eV in c_M at O coverage vs ~0.1 at OH (Gauthier, read from paper) | TRANSFERRED — never measured here; registered as the non-additivity prediction | 10.1021/acs.jpcc.7b02383 | A8/A9 (owed) | zero-compute registration |

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
| **A8** | S3 protocol (off-plane = nosym + displacement, noinv pending S0(b), dy ladder, GATE-1 depth, CONFOUND rule, P-SYMCOV) | NOT DRAFTED | Aug 24, before first S3 deck launches |
| **A9** | external-census controls (P-CTRL: OC20 negative / own-corpus positive), scope limits | NOT DRAFTED | Aug 22, before any corpus is parsed |
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
| S0 | nine capability gates, ~35 box-h | A7 (DEPOSITED) | **DECKS BUILT + ADVERSARIALLY VERIFIED 2026-08-16** (runs/s0/, 29/29 registered jobs, est 33.7 box-h; launch awaits LIT-2/3 drain on box 47662258 — two QUEUE_ALL_DONE lines — or explicit PARK; SnO2 arm additionally gated on the Sn pseudo being present on-box, see runs/s0/i_cutoff_ladder/PSEUDOS_NEEDED.txt; a_beef deck iv is wave-2 after SELECT-WINNER) |
| S1 | silentgate v0.1: entrant-written core, pluggable readers, CI controls | A9 (owed Aug 22) | blocked on A9 |
| S2 | external census: Xu 810 lock/direction map, span_U halves, Divanis delta-curve, pymatgen+atomate paired audit; literature-coding audit RESTORED | A9 (owed Aug 22) | blocked on A9 |
| S3 | tier_v3 crossed coverage x symmetry x basin, 8 metals; second spin seeds RESTORED beyond *OOH-only where triage allows; dy ladder; Cr 1C + re-Hessian at escape | A8 (owed Aug 24) | decks buildable now, launch Aug 26 |
| S4 | A0 dense U grid 1x1 + Cr 2x1v cell rider RESTORED + bulk hp.x Cr+Ti RESTORED (atomic projector) + slab hp.x one relaunch under 72 h cap RESTORED | A6 + A7 (DEPOSITED) | clear after S0(e)/P-PROJ |
| S5 | BEEF-vdW sigma, Ru/Ir/Ti; extension to +U metals if clean | A10 (owed Sep 18, gated S0(a)) | gated |
| S6 | floor/excess, four estimators, n=7 statistics repair, P-SYMCOV scoring, r4 re-rank hook for S8 | A7 P-PLS/P-FLOOR-U + A8 | after data |
| S7 | freeze, figure pack, pre-submission assertions; arXiv preprint RESTORED as post-freeze option | — | Oct 8–15 |
| S8 | make->measure: re-rank gate -> freeze predictions -> melt 2–4 + poor anchor + IrO2 same-bench -> Purdue OER; ONE figure iff complete by freeze | S8 addendum (ccb1806); freeze deposit owed before first ingot | re-rank gate first |

Box-hour repricing of the restored scopes is owed alongside A8 (the restored items
add roughly 300–500 box-h; still trivially affordable).
