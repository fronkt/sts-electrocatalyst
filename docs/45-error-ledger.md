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
| 1 | Symmetry trap (mirror-plane saddle) | 0.291 V on Ir η (1x1); collapses to −0.018 eV at 2x1v half-coverage (verified from raw outputs 2026-08-16) | MEASURED, coverage-conditional | 1C Hessian i167 cm⁻¹; runs/probe/*_cellsym; round-2 synthesis provenance header | P-SYMCOV (A8, owed) | S3 |
| 2 | Magnetic multistability (basin set at step 1, dragged by pot_extrapolation) | 175 meV Cr *OOH; −405 meV Co *OH; 1.86 µB / −1.19 eV Cr *OOH off-arm confound | MEASURED (in-house); prevalence TRANSFERRED (Fahmy >7,843 MP entries, arXiv:2509.05909) | GATE-1 audits; docs/41 | A5 spin-seed rules; A8 (owed) | S3 + S0(h) |
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
| A1–A5 | blocks 1A/1B/1C, LIT | committed + deposited | done |
| **A6** | A0 cell scope + U-by-cell interaction | committed (2214b68); **Zenodo deposit OUTSTANDING — launch gate for block 6A** | before first 6A job |
| **A7** | P-PROJ, P-PLS, P-FLOOR-U, nine S0 capability gates, phase-reality ledger | **NOT DRAFTED** (specified in round-2 synthesis §8 only) | **Aug 18, before ANY new job** |
| **A8** | S3 protocol (off-plane = nosym + displacement, noinv pending S0(b), dy ladder, GATE-1 depth, CONFOUND rule, P-SYMCOV) | NOT DRAFTED | Aug 24, before first S3 deck launches |
| **A9** | external-census controls (P-CTRL: OC20 negative / own-corpus positive), scope limits | NOT DRAFTED | Aug 22, before any corpus is parsed |
| **A10** | BEEF row | NOT DRAFTED; gated on S0(a) | Sep 18 |
| **S8 freeze** | melt-set predictions frozen before first melt | registered as rule (round-2 addendum ccb1806); deposit owed before first ingot | before first melt |

**The binding sequence right now:** Frank re-authors + deposits A7 (by Aug 18) and
deposits A6 → S0's nine gates run → A8/A9 deposited → S3 decks launch Aug 26.
Until A7 is deposited, no new job may launch — that is the campaign's own rule
(docs/43: "an interaction test registered after the grid is read is not a test").
