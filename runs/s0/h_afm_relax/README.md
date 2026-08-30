# S0 gate (h) — AFM relaxations, GATE-1 children, and the s0_O casualty record

Family licensed by the dated `[AFM-SCOPE RESOLVED 2026-08-30: STANDALONE_FOUR]`
addendum at the bottom of docs/43 (4 relaxations + 4 GATE-1 children, S3-class).
Decks built by `src/dft/build_h_afm_relax.py`; every deck in this directory is a
minimal audited diff of a committed parent (assertion series A/G/R in the builder).

## Wave 1 — the four relaxations (array 20238023, 2026-08-30)

| job | outcome | totmag (anchor → per-step converged) | verdict |
|---|---|---|---|
| ref__2x1v__afm__relax | COMPLETED 17m | −2.09 → −2.09, −2.11, −2.11 | BANKED (bfgs 2 steps) |
| s0_O__2x1v_off__afm__relax | **OOM on a120 at 07:46** | — (died in first-SCF wfc init) | retried (below) |
| s0_OH__2x1v_off__afm__relax | COMPLETED 45m | −1.21 → −1.23, −1.27, −1.27 | BANKED (bfgs 2 steps) |
| s0_OOH__2x1v_off__afm__relax | COMPLETED 2h49m | −0.24 → −0.22, −0.19, −0.14, −0.12 | BANKED (bfgs 3 steps) |

No sign flips anywhere — no A8.3 CONFOUND in the three banked rows. Relaxation
gains vs the anchor SCFs: −2.4 / −2.2 / −8.8 meV (ref / OH / OOH); max atomic
displacement 0.006 / 0.007 / 0.023 Å. P11 limit (ii)'s "single point at an
NM-relaxed geometry is a lower bound" is therefore a measured 2–9 meV correction.

**Relaxed Δc_M = −32.5 meV** (vs docs/63 §4's fixed-geometry −25.9; the −6.6 meV
deepening is the *OOH state relaxing 4× more than *OH). Still a level at U = 0:
docs/63 §4.1's swing-vs-level caveat travels unchanged, and no number from this
family bounds A7.3.

## The s0_O casualty record

- **attempt 1** (`.out.attempt1-oom-a120`): task 20238023_2, OOM-killed on node
  a120 at 07:46 during first-SCF wavefunction initialization (last line
  "Starting wfcs are 220 randomized atomic wfcs"; sampled MaxRSS 18 G of 237 G).
  Node fault or spike — the two larger adsorbate decks finished at ~50 G peaks.
  Mechanical retry, same registered deck (m_h_afm_relax_retry2.txt), a120
  excluded.
- **attempt 2** (`.out.attempt2-scf-maxstep`): array 20241317 on a131, ran
  1h59m, **`convergence NOT achieved after 200 iterations` in the 3rd SCF** —
  pw.x still prints JOB DONE (the docs/26 §4 trap) and Slurm says COMPLETED.
  Steps 1–2 converged with the moment walking −1.62 (anchor) → −1.70 → −1.98;
  the 3rd SCF touched accuracy 1.45e-6 at iteration 21 (conv_thr = 1.0e-6),
  bounced, and spin-sloshed (totmag −1.6 ↔ −2.6, absmag climbing 5.1 → 5.7) for
  the remaining 180 iterations. A magnetic-solution oscillation, not a slow
  grind — the campaign's second state-property SCF instability (docs/45 trap 25
  pattern; cf. Stage 0's Ti s0_OOH spontaneous symmetry breaking, docs/62 §4).
- **attempt 3** (`__relax__r1`, pending): the committed relax deck with
  **mixing_beta halved 0.3 → 0.15** and a fresh prefix — exactly two lines.
  This transplants rung (ii) of the A6.5(2) repair ladder ("halve the mixing
  beta"), registered for non-convergent A0 points, **by analogy — the A0
  registration does not cover S0(h) and no claim is made that it does**.
  mixing_beta is solver machinery, not a registered quantity. **If r1 also
  fails, rung (iii) is the exit: the s0_O relaxed row is recorded
  NOT_CONVERGED and reported as a gap — no third solver attempt.** The moment
  drift already on record (0.36 μ_B by step 2) goes to the A8.3/CONFOUND
  discussion at scoring time regardless of how r1 ends.

## GATE-1 children (`__g1`)

Deposited rule docs/43:311-314: every relaxation with a converged final geometry
gets a fresh-density fixed-geometry SCF at its own final coordinates. Three are
owed and built (`--gate1 --quarantine s0_O__2x1v_off__afm`); the s0_O child is
**deferred, not skipped** — it becomes owed the moment a repair attempt
converges. Each child is the banked ANCHOR deck at the relaxation's final
coordinates with a fresh prefix: frozen rows byte-identical to the committed
parent, moving rows changed only in their three coordinate fields.

Scoring at landing (also in m_h_afm_g1.txt's header): ≥ 5 meV below its
relaxation → BASIN_DRIFT re-relax loop; > 1 meV above → A8.3 refusal;
totmag > 0.1 μ_B off the relaxation's final value → CONFOUNDED.
