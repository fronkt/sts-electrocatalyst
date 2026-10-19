# B1: relaxed Cr projector comparison in the 2 × 1 cell (registered 2026-10-16, before any deck exists)

**Decision of record.** Frank, 2026-10-16: "Go ahead". This approved B1 of the DFT contingency plan
(sts-report `report/refine-logs/EXPERIMENT_PLAN.md`) with the conditions given to him the same day:
- the outcome may shrink the 0.173 V the report states;
- the readings below are fixed before any output exists;
- B1 is reported in whatever state it is at the Oct 25 data lock.

B2 (the two-site *OOH relaxation) is not run. B3 (the existing Ti spin check) needs no compute.

**Status.** Registered. No B1 deck has been built or submitted as of this line.

## Question

The registered fixed-geometry arm (docs/43 Amendment 13; readout docs/84; `docs/figs/pproj_cell_readout.json`) found
that switching the Hubbard projector from atomic to ortho-atomic moves η(CrO₂) by +0.1725 V at U = 7.15 eV in the
adopted 2 × 1 cell, with both legs limited by the same step. Both legs were single points on one byte-identical
geometry, so A13.5 item 2 left open "whether the split survives relaxation". B1 asks exactly that: **with each
projector relaxing its own geometry at U = 7.15 eV, how far apart are the two η values?**

This is a different estimand from Amendment 13's. docs/76 §6 and docs/78 §8 declined ortho relaxation because the
fixed-geometry claim *is* a difference between two treatments of one slab. B1 does not replace that result. The two
are always reported side by side: the fixed-geometry difference isolates the projector's electronic effect, and the
relaxed difference adds each projector's geometric response.

## Corrections to the 10-16 plan, found while mapping the inputs

- **No "+0.02 Å mirror-normal kick" exists in production.** The banked *O and *OH 2 × 1 decks (`__mir`) run with
  symmetry on and no kick. A 0.02 Å kick would also do nothing here: on a soft off-plane mode the restoring force at
  0.02 Å sits below the 2 × 10⁻³ Ry/bohr force threshold, so BFGS could stop on the plane. B1 instead uses the
  project's deposited off-plane minimum, |dy| ≥ 0.30 Å (`src/dft/build_s3.py:135`).
- **The start geometries were relaxed at U = 3.7 eV under the atomic projector**, not at 7.15 eV. The sources are
  `runs/probe/Cr_cellsym/*` for the clean slab, *O and *OH, and `runs/s3/Cr/s0_OOH__2x1v_escape.out` for *OOH. So
  both B1 legs relax away from a common start, and neither leg starts at its own minimum.
- **`src/dft/probe_decks.py` is not used.** It always writes `HUBBARD (atomic)`, and on the u715 decks, which end
  without a newline, it writes no Hubbard card at all. B1's builder edits the banked decks line by line instead.

## Design

**Sources.** The eight banked U = 7.15 eV single-point decks:
- `runs/a0/cell/{ref__2x1v, s0_O__2x1v_mir, s0_OH__2x1v_mir, s0_OOH__2x1v_escape}__u715.in` (atomic);
- `runs/a0/pproj_cell/<same stems>__u715_ortho.in` (ortho-atomic).

Each ortho deck differs from its atomic partner in exactly two lines: the prefix and the `HUBBARD` card.

**Edits, identical in both legs** (the builder refuses any other difference):
1. `calculation = 'scf'` → `'relax'`, and a new prefix.
2. `max_seconds` is set below the job wall, so pw.x stops cleanly before the runner's ceiling.
3. **Symmetry.**
   - The clean slab keeps its `nosym`/`noinv`, and the escaped *OOH keeps its `nosym`, as banked.
   - The *O and *OH decks gain `nosym = .true.`, matching the escaped *OOH convention, so no imposed symmetry holds
     the adsorbate.
4. **Off-plane start for the mirror decks.**
   - The outermost adsorbate atom (the O of *O, the H of *OH) is moved +0.30 Å along y, the mirror normal; the
     adsorbate sits on the y = 1.56305954 Å mirror.
   - The escaped *OOH already lies off the plane and the clean slab has no adsorbate, so neither is moved.

Everything else is unchanged: the 14 fixed bottom atoms, cutoffs, smearing, mixing, k-mesh, spin start, the
forc_conv_thr of 2.0 × 10⁻³ Ry/bohr, nstep = 200, BFGS, and the pseudopotentials.

**Stage 1: eight relaxations.**
- Each runs on one wholenode node (128 ranks, npool 8) through the pinned seeded runner as a stage of kind
  `relax`, with the 126-iteration SCF ceiling.
- A leg stopped by a ceiling or a failure marker never becomes a result.

**Stage 2: a terminal fresh-start SCF at each converged endpoint** (GATE-1, docs/43:310-313).
- Its deck is the stage-1 deck with `calculation = 'scf'`, a new prefix and the final coordinates, built
  mechanically after stage 1 and pinned before submission.
- The η values come from these terminal SCFs.
- If a terminal SCF lands at least 5 meV below its relaxation's final energy, the state is relaxed once more from
  that SCF inside the ceiling. If that is not possible, the state is unresolved.

## Readings, fixed now

The scorer `src/dft/b1_relaxed_projector_readout.py` follows `pproj_cell_readout.py`: the same gas references,
`hea_oer.referencing`, ZPE/TS constants and `oer_overpotential`. It is committed before any B1 output exists.

- **Δη_relaxed = η(ortho, relaxed) − η(atomic, relaxed).** The bands are A13.3's, inherited:
  - |Δη| > 0.10 V: the projector effect **survives relaxation**;
  - |Δη| < 0.03 V: it **collapses** under relaxation;
  - in between: **intermediate**, never rounded.
- **Limiting step.** It is compared between the legs. If the legs differ, Δη is split into electronic and ZPE/TS
  constant parts, as in A13.6. The 0.487 V convention applies: any number that rests on a limiting-step change
  travels with its split.
- **Magnetization.** A difference of 0.5 μB or more in total magnetization between paired legs is a BRANCH
  MISMATCH, reported and never averaged away.
- **Adsorbate chemistry.** Each endpoint is classified with `hea_oer.site_integrity.DEFAULT_THRESHOLDS`:
  - M–O < 3.00 Å means not desorbed;
  - H counts as bonded within 1.15 Å of its own O;
  - for *OOH, O–O ≤ 1.60 Å means not cleaved.

  A desorbed, dissociated or cleaved endpoint is a **chemical result**: it is reported, and that leg gives no η.
- **Off-plane outcome (reported, not scored).** For *O and *OH under each projector, the report gives the
  adsorbate's |dy| from the mirror at the endpoint and the energy relative to the banked mirror single point at the
  same U and projector. It says whether the adsorbate returned to the plane (|dy| < 0.05 Å) or settled off it.
- **Numerical failure means unresolved, never small.** All four states under both projectors are reported, or the
  arm is reported as incomplete; a partial set is never scored.
- **The fixed-geometry pair is printed beside the relaxed pair:** 0.9240 / 1.0965 V, Δη +0.1725 V, both limited by
  the same step.

## Reporting rule

B1 enters the DFT-only manuscript (sts-report) in whatever state it is at the Oct 25 data lock:
- **Complete:** the relaxed pair, the band and the limiting steps.
- **Incomplete:** one clause saying a relaxed repeat was unresolved or still running at the lock.

The experiment-version manuscript is not changed by B1 unless Frank asks.

## Budget

- **Live balance:** CPU 15,124.2 SU (`mybalance`, 2026-10-17 03:43Z). GPU is not used.
- **Ceiling 7,488 SU**, unchanged from the plan:

  | Part | Calculation | SU |
  |---|---|---|
  | Stage 1 | 8 tasks × 6 h × 128 | 6,144 |
  | Stage 2 | 8 tasks × 45 min × 128 | 768 |
  | One repair wave | | 576 |

- **Expected cost.** The *OOH escape relaxation at U = 3.7 eV took 34 BFGS steps in 1 h 37 min at 128 ranks. At 1–3 h
  per leg, stage 1 should use about 1,000–3,100 SU, and stage 2 about 200 SU.
- docs/76 §Cost records a billed-to-measured factor of 1.658 on earlier arrays. The ceiling is enforced by the job
  walls, not by that estimate.

## Pre-launch review, folded 2026-10-16 (before submission)

- **Review.** Codex `gpt-6.1-sol` (xhigh, read-only; `results/b1_relaxed_projector_2026-10-16/PRELAUNCH_REVIEW.md`)
  found the decks, timing, hashes and launch gates correct.
- **Scorer changes.** Four were made before any output exists:
  - banked references are checked against the runner's numerical-failure markers;
  - an unregistered H criterion is removed;
  - unresolved arms report every available diagnostic;
  - the fixed η pair is printed.
- **A pre-existing caveat it surfaced.** The banked atomic *OH single point behind the fixed-geometry 0.1725 V,
  `runs/a0/cell/s0_OH__2x1v_mir__u715.out`, carries an `IEEE_INVALID_FLAG` note. Under B1's policy that run would be
  rejected. B1's relaxed atomic *OH leg is an independent value.
- **Scorer test.** With the banked single points standing in for the terminal SCFs, the scorer reproduces Δη
  +0.1725164 V exactly.

## Launch, 2026-10-17 UTC (Frank, 2026-10-16: "launch B1 on Anvil")

- **Steps:** staged from 6a3da59 (15 files, sha256-verified, read-only); preflight passed; held array **21411373**
  (`1-8%8`, 06:00:00, wholenode, 128 cores) validated, then released.
- **Preflight checks:** runner VALID, imports OK, QE binaries matched, `mybalance` 15,124.2 SU, empty queue, 0.7 TB free.
- **Ceiling:** 6,144 SU for this stage.
- **Receipts:** `results/b1_relaxed_projector_2026-10-16/*_receipt.json`.

## Stage 1 outcome, 2026-10-18 (array 21411373; outputs collected, nothing scored)

- **Ran.** Task 1 backfilled at 17:25Z on 10-17; tasks 2–8 ran 01:24–04:53Z on 10-18. Billed 1,653.2 SU
  (`mybalance` 15,124.2 → 13,471.0), equal to the summed sacct walls × 128.
- **Runner COMPLETE, BFGS converged (4 legs):**

  | Leg | Ionic steps (SCF cycles) | Max SCF iterations | Wall |
  |---|---|---|---|
  | clean slab, atomic | 18 | 23 | 1 h 35 min |
  | clean slab, ortho-atomic | 17 | 27 | 2 h 01 min |
  | *O, atomic | 23 | 27 | 1 h 31 min |
  | *OOH, atomic | 50 | 26 | 3 h 28 min |

- **KILLED at the 126-iteration SCF ceiling (3 legs): *O, *OH and *OOH under ortho-atomic.**
  - Each stopped in the SCF of ionic step 3 (*O, *OH) or 4 (*OOH). Every earlier SCF converged.
  - pw.x tightens `conv_thr` during a relaxation (to 8.4 × 10⁻⁸ Ry at the *OOH step 4). The *O and *OOH SCFs
    stalled near 10⁻⁶ and 5 × 10⁻⁷ Ry, with the total energy jittering by about 10⁻⁴ Ry. The *OH SCF reached
    6.8 × 10⁻⁵ Ry by iteration 10, then rose to 10⁻² Ry.
  - Total magnetization stayed at 22 or 23 μB throughout, so no magnetic flip was involved.
  - The paired atomic legs met the same tightened thresholds in 10–20 iterations at every step.
- **REJECTED (1 leg): *OH, atomic.**
  - BFGS converged in 22 ionic steps and JOB DONE printed once, but the exit notice carries `IEEE_INVALID_FLAG`.
  - The same flag is on the banked atomic *OH single point (`runs/a0/cell/s0_OH__2x1v_mir__u715.out`).
  - None of the other seven banked U = 7.15 eV single points, and none of the other seven B1 outputs, carries it.
- **State under the readings above.** Four of eight legs failed numerically, so B1 is **unresolved**. Stage 2 is
  not built. Any rerun would change registered settings (mixing or the SCF threshold schedule) or the
  failure-marker rule, so the next step is Frank's.

## Repair, registered 2026-10-18 before any repair deck exists (Frank: "Repair")

**Decision of record.** Offered the same morning: stop with the registered "unresolved" clause, or repair the failed
legs with changed SCF mixing (about 1,600 SU expected, about 3,300 SU cap). The atomic *OH leg was flagged as staying
rejected unless a rerun comes out clean, because the failure-marker rule is not changed. Frank: "Repair".

**What is repaired, and how.** Each failed leg is continued from where stage 1 left it, with BFGS restarted:
- **The three ortho-atomic adsorbate legs** restart from the geometry of their stalled SCF, which is the last
  `ATOMIC_POSITIONS` block their stage-1 output printed.
- **The atomic *OH leg** restarts from its converged final coordinates. Its stage-1 run converged, so the
  continuation should only confirm the endpoint. It counts only if it carries no failure marker.

**Recipes.** Each repair deck is its stage-1 deck with only these changes:
- the new geometry;
- a new prefix;
- `max_seconds` set for its wall;
- the mixing below.

| Recipe | `mixing_mode` | `mixing_beta` | `mixing_ndim` |
|---|---|---|---|
| Stage 1 (unchanged legs) | local-TF | 0.3 | 8 (default) |
| T1 | local-TF | 0.1 | 16 |
| T2 | plain | 0.1 | 16 |

T2 tests whether the local-TF preconditioner is behind the stall or the *OH flag.

Everything else stays as in stage 1:
- `conv_thr` 10⁻⁶ Ry and pw.x's default tightening during relaxation;
- the 126-iteration SCF ceiling;
- forc_conv_thr, nstep, symmetry, spin start, cutoffs, k-mesh, fixed atoms and the projectors;
- the failure-marker rule.

**Launch (one package, two arrays, both of runner kind `relax`):**

| Array | Legs | Wall | Cap (SU) |
|---|---|---|---|
| ortho | *O, *OH and *OOH ortho-atomic, T1 | 8 h | 3,072 |
| short | *OH atomic, T1 and T2 | 1 h | 256 |

As first registered, the ortho legs were split into an 8 h array (*OOH) and a 5 h array (*O, *OH). They were merged
before any deck was built. A one-task array would have needed a held-shape check that launch_ops has not been tested
on. The merge raises only the cap; billing follows the actual run time.

**Selection, fixed now.** For each of the eight legs, the relaxation that feeds stage 2 is the first COMPLETE one in
this order: stage 1, then T1, then T2.
- A T1 ortho continuation that fails gets one T2 continuation, from the last geometry it printed, if the ceiling
  allows.
- A leg with no COMPLETE relaxation leaves B1 unresolved.
- No other reruns are made.

**Legs kept from stage 1.** The atomic *O and *OOH legs and both clean-slab legs keep their stage-1 relaxations.
Mixing changes only how the SCF reaches its solution, not the solution itself. The GATE-1 terminal SCFs still test
every endpoint.

**Stage 2 and readings.** Stage 2 is unchanged: a fresh-start terminal SCF at each selected endpoint, with the deck's
mixing inherited from its relaxation. The readings are unchanged. The scorer is changed only to read each leg's
selected relaxation and its terminal SCF.

**Budget.**
- Stage 1 used 1,653.2 SU.
- This repair is capped at 3,328 SU, with stage 2 at 768 SU (8 × 45 min).
- That makes 5,749.2 SU in all, inside the registered 7,488 SU ceiling, which leaves 1,738.8 SU for a T2 fallback or
  a GATE-1 re-relaxation.
- Expected use: about 1,450 SU for the repair and 200 SU for stage 2.

**Reporting.** If B1 completes, the report says three ortho-atomic legs and the atomic *OH leg were completed by
continuation with stronger SCF damping after numerical failures.

**Repair launch, 2026-10-18.**
- **Steps:** staged from 13a26d8 (13 files, sha256-verified, read-only); preflight passed.
- **Preflight checks:** runner VALID on both arrays, imports OK, QE binaries matched, `mybalance` 13,471.0 SU, empty
  queue, 0.6 TB free.
- **Arrays:** held arrays **21475905** (`b1r_ortho`, 1-3%3, 08:00:00) and **21475906** (`b1r_short`, 1-2%2,
  01:00:00) validated (ceiling 3,328 SU), then released.
- **Receipts:** `results/b1_repair_2026-10-18/*_receipt.json`.

## Repair outcome, 2026-10-18 (arrays 21475905 and 21475906; outputs collected, nothing scored)

All five continuations finished COMPLETE with BFGS converged. None printed IEEE_INVALID; the only floating-point
notices are DENORMAL and UNDERFLOW.

| Continuation | Array task | Ionic steps | Max SCF iterations | Final energy (Ry) | Runner wall (s) |
|---|---|---|---|---|---|
| `s0_OOH__2x1v_escape__u715_ortho_relax_t1` | 21475905_1 | 60 | 47 | −3187.21322784 | 25,241 |
| `s0_O__2x1v_mir__u715_ortho_relax_t1` | 21475905_2 | 26 | 46 | −3144.25229012 | 10,503 |
| `s0_OH__2x1v_mir__u715_ortho_relax_t1` | 21475905_3 | 66 | 79 | −3145.61672831 | 26,553 |
| `s0_OH__2x1v_mir__u715_atomic_relax_t1` | 21475906_1 | 1 | 48 | −3145.01357772 | 633 |
| `s0_OH__2x1v_mir__u715_atomic_relax_t2` | 21475906_2 | 1 | 33 | −3145.01357712 | 487 |

- **Selection (registered order):** T1 for all three ortho-atomic adsorbate legs and for atomic *OH. The T2
  fallback was not needed, so no further continuation was run.
- **Atomic *OH:** T1 and T2 agree to 6 × 10⁻⁷ Ry. The flag recurred in neither rerun, so this test does not tie
  the stage-1 IEEE_INVALID to local-TF mixing.
- **Magnetization:** at the relaxation level, each state's final total magnetization is the same under the two
  projectors: slab 24, *O 22, *OH 23, *OOH 23 μB/cell. The registered branch check is applied to the terminal SCFs.
- **Billed:** 2,261.0 SU (balance 13,471.0 → 11,210.0; elapsed 17.66 node-h), against the 3,328 SU cap. The
  1,450 SU expectation was low because the two long ortho legs each ran about 7 h.
- **B1 to date:** 3,914.2 SU used. Adding the 768 SU stage-2 cap gives 4,682.2 SU, inside the 7,488 SU ceiling.
- **Files:** outputs, receipts and logs are committed at 6029a0c.

## Stage 2 launch, 2026-10-19 UTC (2026-10-18 21:23 EDT)

`src/dft/b1_terminal_scf_build.py` built eight fresh-start terminal SCF decks:
- four from stage-1 relaxations (both slab legs, atomic *O, atomic *OOH);
- four from repair T1 relaxations (ortho *O, *OH, *OOH, and atomic *OH).

Each deck differs from its relaxation deck only in `calculation`, `prefix`, `max_seconds` and the positions. Mixing is
inherited.
- **Spec:** `results/b1_terminal_scf_2026-10-17/launch_spec.json`, sha256 9b945f97…; Slurm `anvil/103_b1_scf.slurm`.
- **Wall:** 45 min (SCF 1,980 s, projection 600 s). The first, fresh-start SCF of each T1 relaxation took about
  640 s.
- **Steps:** staged from 1c6f4b9 (14 files, sha256-verified, read-only); preflight passed.
- **Preflight checks:** runner VALID, imports OK, QE binaries matched, `mybalance` 11,210.0 SU, empty queue, 0.6 TB
  free.
- **Array:** held array **21509674** (`b1_scf`, 1-8%8, 00:45:00) validated (ceiling 768 SU), then released.
- **Receipts:** `results/b1_terminal_scf_2026-10-17/*_receipt.json`.
