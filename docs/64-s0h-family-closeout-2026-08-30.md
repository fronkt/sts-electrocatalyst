# docs/64 — S0(h) AFM relaxation family: execution closeout (2026-08-30)

**Status of this document:** post-hoc readout of a licensed family, written the
day the family reached its terminal state. Nothing here re-scores a registered
prediction. The licence is the dated `[AFM-SCOPE RESOLVED 2026-08-30:
STANDALONE_FOUR]` addendum at the bottom of docs/43 (4 relaxations + 4 GATE-1
children, S3-class); the obligation discharged is A8.5's owed S0(h) re-anchor
(docs/47). Primary artifacts: `runs/s0/h_afm_relax/` (decks, .outs, README with
the full attempt trail), commits `7994533 → f02cc02 → cc77ccf → 06ff871` and
this one.

## 1. Final state of the family, in one table

| registered job | attempts | terminal state | GATE-1 |
|---|---|---|---|
| ref__2x1v__afm__relax | 1 | **BANKED** (bfgs 2 steps, 15m39s QE WALL) | **PASS** (+0.028 meV, Δm 0.00) |
| s0_O__2x1v_off__afm__relax | 3 | **NOT_CONVERGED** (recorded gap) | never owed (no final geometry) |
| s0_OH__2x1v_off__afm__relax | 1 | **BANKED** (bfgs 2 steps, 44m51s QE WALL) | **PASS** (−0.090 meV, Δm +0.02) |
| s0_OOH__2x1v_off__afm__relax | 1 | **BANKED** (bfgs 3 steps, 2h48m QE WALL) | **PASS** (+0.302 meV, Δm −0.03) |

Arrays: 20238023 (wave 1), 20241317 (s0_O OOM retry), 20243152 (+20243319
retry: g1 children), 20243153 (s0_O rung-(ii) repair). Two of the ten
tasks that ran were OOM-killed in their first minutes, on two distinct nodes
(a120, a200 — see §5); each OOM was retried mechanically and neither recurred. Measured family cost: **1,067.9 SU** (70,851.6 → 69,783.7),
against the 4,000–7,600 SU STANDALONE_FOUR estimate quoted in the resolution
addendum.

## 2. The banked numbers

Comparators verified against primary sources: `h_afm_anchor/README.md`'s E_NM
column equals the final BFGS energy of each `runs/probe/Ru_cellsym/*.out` NM
relaxation to every printed digit, so relaxed-AFM vs those values is
relaxed-vs-relaxed.

| state | gain vs anchor SCF (meV) | ΔE vs NM-relaxed (meV) | max disp (Å) | final totmag |
|---|---|---|---|---|
| ref (clean slab) | −2.4 | −146.4 | 0.006 | −2.11 |
| s0_OH | −2.2 | −87.5 | 0.007 | −1.27 |
| s0_OOH | −8.8 | −120.1 | 0.023 | −0.12 |

- **Relaxed Δc_M = ΔE(\*OOH) − ΔE(\*OH) = −120.06 − (−87.55) = −32.51 → −32.5 meV**,
  vs docs/63 §4's fixed-geometry −25.9. The −6.6 meV deepening is exactly the
  difference of relaxation gains (−8.8 vs −2.2): the \*OOH state relaxes ~4×
  more than \*OH.
- Basin continuity is clean on all three: per-ionic-step converged totmag runs
  ref −2.09→−2.11, s0_OH −1.23→−1.27, s0_OOH −0.22→−0.12 — no sign flip, no
  A8.3 CONFOUND, and GATE-1's fresh-density children (≤0.302 meV, ≤0.03 μ_B
  from their relaxations) confirm no density-history dependence either.
- **P11 limit (ii) is discharged by measurement.** The registration called the
  fixed-geometry AFM single points "a lower bound on the effect" because the
  geometry was NM-relaxed. The bound's slack is now measured: 2–9 meV per
  state, and −6.6 meV on Δc_M.

## 3. What the numbers do NOT do (unchanged from docs/63 §4.1–4.3)

−32.5 meV is a **level at U = 0**. A7.3 scores a **swing across U ∈ [0, 9]**,
and by the A11.1 arithmetic a U-independent offset cancels exactly at any
size. Nothing in this family — fixed-geometry or relaxed — bounds A7.3's
error, and no version of it can (all decks are U = 0 in the 2×1v cell; A7.3's
rows are the 1×1 A0 grid across U). Only the docs/61 item 10 Ru AFM probe,
run at both U endpoints, acts on A7.3.

**For docs/61 decision item 3 (the entrant's):** P-SPIN-DELTA's proposed
threshold was 0.033 eV, justified from the adsorption-energy class (the wrong
quantity — docs/63 §4.2 re-anchored it through c_M to 0.026 eV). The relaxed
measurement now lands the c_M level at **0.0325 eV ≈ 0.033**: numerically the
original figure, reachable through the correct quantity. Live options:
0.026 (fixed-geometry c_M level) or 0.033 (relaxed c_M level — keeps the
registered number, replaces its justification). Either way the amendment must
state it is a level standing proxy for a swing.

## 4. The s0_O record: NOT_CONVERGED, and what the three attempts measured

- Attempt 1: OOM on a120 after 7m46s elapsed (sacct), first-SCF wfc init
  (node fault; evidence
  `.out.attempt1-oom-a120`).
- Attempt 2 (a131, 1h59m): steps 1–2 converged with the moment walking −1.62
  (anchor) → −1.70 → −1.98; the 3rd SCF touched accuracy 1.45e-6 (conv_thr
  1.0e-6) at iteration 21, bounced, and spin-sloshed — totmag mostly −1.6 ↔ −2.6 with excursions to
  −1.29 and −2.61 — to the 200-iteration ceiling. JOB DONE printed; Slurm said COMPLETED (the
  docs/26 §4 trap). Evidence `.out.attempt2-scf-maxstep`.
- Attempt 3 = rung (ii) of the A6.5(2) ladder **by analogy** (mixing_beta
  0.3 → 0.15, a two-line deck diff, exit pre-stated in the manifest header):
  failed **earlier** (2nd SCF). Its first SCF "converged" at totmag **−1.90**
  (E −0.710 meV vs the anchor's −1.62 row at the byte-identical geometry;
  attempt 2's first SCF: −1.70, −0.151 meV) with the moment still drifting
  monotonically (−1.82 → −1.90 over the closing ~20 iterations) when the
  energy criterion fired. This document's own verification pass REFUTED the
  first-draft reading that halved mixing "selected a different magnetic
  solution": three converged flags at one geometry spanning 0.28 μ_B across
  0.71 meV is ONE nearly-flat magnetization landscape whose moment an
  energy-only conv_thr (1.0e-6 Ry = 0.014 meV) cannot pin (docs/45 **trap
  27**, as corrected).

Verdict, per the pre-stated rung (iii): **NOT_CONVERGED, reported as a gap.**
The s0_O AFM state at and near the NM-relaxed geometry has an unpinnable
moment — its magnetization landscape is flat at the sub-meV scale over
~0.3 μ_B — so every SCF stops somewhere else along the drift and the BFGS
walks; the campaign's second state-property SCF instability (docs/45 trap 25
pattern; Stage 0's Ti s0_OOH spontaneous symmetry breaking is the first).
Consequences:

- The **fixed-geometry** s0_O AFM anchor row (−80.3 meV vs NM, banked in
  h_afm_anchor) is unaffected and remains the family's s0_O number, now with
  the recorded caveat that its relaxed correction is unmeasurable at this
  protocol.
- The relaxed 4-step CHE row for the AFM anchor cannot be assembled (steps
  2–3 need \*O); the relaxed Δc_M does not need it and is unaffected.
- The instability is itself evidence for the open NM-vs-AFM class discussion
  (docs/59 §3c, docs/61): on the \*O state specifically, the anchor's moment
  is unpinned at the sub-meV scale — a flat magnetic landscape, which is the
  sharpest form of the "magnetic treatment matters and is not settled" point
  that discussion turns on.

## 5. Infrastructure observations (for the RCAC ticket decision)

Two early-phase OOM kills on two distinct nodes (a120, a200 — and a200 later ran
the r1 repair for its full 1h44m with no OOM, so its fault is intermittent,
not a dead node), each with sampled MaxRSS far under the 237 GB
allocation (18 G, 52 G), each in the first minutes, and each retry succeeding
elsewhere unchanged. Sibling batch-step MaxRSS, transcribed from sacct
2026-08-30 (not otherwise on disk): wave-1 tasks 75.1 / 18.1 / 49.4 / 50.0 GB.
The Slurm-elapsed figures and node names in this document are likewise sacct
transcriptions; QE WALL times are quoted where a .out is on disk. The end
balance 69,783.7 SU is a mybalance transcription (che260157 CPU row,
2026-08-30). If a third early OOM lands, send the drafted ticket
(anvil/rcac_ticket_draft_2026-08-24.md) with the node list and timestamps.

## 6. Report scoping

**MAY report:** the §1 table and attempt trail; the §2 panel, its GATE-1
confirmation, and relaxed Δc_M = −32.5 meV as the AFM re-anchor's c_M level at
U = 0; P11 limit (ii) discharged with measured slack; the s0_O NOT_CONVERGED
verdict with its two-solution evidence; traps 25–27; the SU cost.

**MAY NOT report:** any use of −32.5 (or −25.9, or 33–64) meV as a bound on
A7.3's error (§3); any relaxed s0_O AFM energy (none exists; attempt energies
are unconverged and MUST NOT be quoted as energies); the r1 first-SCF −1.90
row as a banked energy (it is diagnostic evidence of the flat-moment
landscape only, and its moment was non-stationary at the convergence flag);
any statement that A6.5(2) covers S0(h) (the repair was analogy, recorded as
such); the A7.3 census unchanged — this family never touches A7.2/A7.3
scoring.

**Open items this touches (the entrant's, unchanged in ownership):** docs/61
items 3 (threshold re-anchor — new §3 option) and 10 (Ru AFM probe — now the
only live path to A7.3); docs/59 §3c (the s0_O instability is new evidence);
the docs/62 §5.2 authorisation; A7.7 disposition.
