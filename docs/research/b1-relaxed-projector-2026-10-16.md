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

## Stage 2 outcome and readout, 2026-10-19 (array 21509674)

- **Ran.** All 8 terminal SCFs finished COMPLETE in 7–20 min each (21:29–21:59 EDT, 10-18), with no IEEE_INVALID and
  no unconverged SCF.
- **Billed.** 198.8 SU (`mybalance` 11,210.0 → 11,011.2). B1 in all has used 4,113.0 of its 7,488 SU ceiling.
- **Readout.** `PYTHONPATH=src python src/dft/b1_relaxed_projector_readout.py --json
  docs/figs/b1_relaxed_projector_readout.json` exits 2 (UNRESOLVED). No η is computed for either leg.

| State | Leg (selected relaxation) | GATE-1 (meV) | vs banked SP (meV) | μB/cell | Endpoint |
|---|---|---|---|---|---|
| slab | atomic (stage 1) | +0.01 | −404.3 | 24.00 | — |
| slab | ortho (stage 1) | +0.01 | −494.0 | 24.00 | — |
| *O | atomic (stage 1) | 0.00 | −601.4 | 22.00 | intact; Cr–O 1.670 Å; off plane, \|dy\| 0.109 Å |
| *O | ortho (T1) | +0.01 | −741.6 | 22.00 | intact; Cr–O 1.666 Å; off plane, \|dy\| 0.154 Å |
| *OH | atomic (T1) | 0.00 | n/a (banked SP flagged) | 23.00 | intact; Cr–O 1.924 Å; off plane, \|dy\| O 0.091, H 0.300 Å |
| *OH | ortho (T1) | 0.00 | −960.9 | 23.00 | intact; Cr–O 1.979 Å; off plane, \|dy\| O 0.975, H 1.260 Å |
| *OOH | atomic (stage 1) | **−27.05** | −1,286.0 | 22.81 | **not intact**: nearest Cr–O 3.500 Å, H 2.687 Å from its O, O–O 1.223 Å |
| *OOH | ortho (T1) | **−22.25** | −1,716.4 | 22.83 | **not intact**: nearest Cr–O 3.727 Å, H 2.482 Å from its O, O–O 1.223 Å |

Column notes:
- **GATE-1** is the terminal SCF minus the relaxation's final energy.
- **vs banked SP** is the terminal SCF minus the banked U = 7.15 eV single point at the same projector. It includes the
  slab's own relaxation at U = 7.15 eV, so for *O and *OH it is not the off-plane gain alone.

**Branch.** No mismatch: every pair agrees within 0.02 μB.

**What the readings give.** Under both projectors the *OOH endpoint is desorbed (Cr–O ≥ 3.00 Å) and dissociated (H
more than 1.15 Å from its own O). Under the registered chemistry reading this is a **chemical result**, not a numerical
failure:
- neither *OOH leg gives an η;
- so no relaxed pair and no Δη_relaxed exist, and no band applies.

The fixed-geometry pair (0.9240 / 1.0965 V, Δη +0.1725 V) is unchanged; it remains a fixed-geometry result.

**How the *OOH came apart.** The trajectory comes from the printed geometries
(scratch analysis using the readout's own `chemistry`/`dist` functions).
- **Start, both legs:** the banked fixed-geometry *OOH, the U = 3.70 eV atomic relaxation, is intact (Cr–O 2.013 Å,
  O–O 1.339 Å, H 1.036 Å from its O and 1.612 Å from a lattice O).
- **Atomic leg:**
  - H transfer: by ionic step 15–20 the H has moved onto the lattice O (1.08 → 1.00 Å).
  - O₂ formation: O–O shortens to 1.22–1.23 Å, an O₂-like bond, by step 25.
  - Lift-off: the O₂ rises off the Cr (2.29 → 3.50 Å).
- **Ortho leg (T1):** the same sequence, about five steps earlier.
- **Energy:** it falls by 1.259 eV over the atomic leg's 50 SCFs, rising once, by 29.7 meV. Over the 60 SCFs of the
  ortho T1 leg it falls by 1.410 eV from its own start and never rises.
- **Same failure mode as the alloy screen:** the MLIP screen's dominant one (H on a lattice O, O₂ gone; 573 and 525 of
  720 *OOH), here in DFT+U at U = 7.15 eV under both projectors.

**GATE-1 on *OOH, not acted on.**
- **What it found:** both *OOH terminal SCFs found an electronic solution 22–27 meV below the relaxation's end, with
  the moment going from 23.00 to 22.81/22.83 μB.
- **What the rule says:** relax once more from that SCF inside the ceiling.
- **Why it is not run:** it cannot give either leg an η. A re-relaxation descends from an endpoint where the O₂ is
  3.5–3.7 Å off the Cr and the H sits 0.98 Å from a lattice O. Rebuilding *OOH would need the H to climb back over the
  ~1.3 eV it released.
- **Status:** left for Frank. A cap of 2 × 6 h × 128 = 1,536 SU fits in the 3,375 SU left under the ceiling.

**Reporting (DFT-only manuscript).** The registered rule names "complete" and "incomplete". This outcome is the
chemical result the readings tell the report to state. It goes in:
- Section 4.4: the relaxed repeat gave no pair because *OOH decomposed under both projectors, and four of the eight
  relaxations finished only after a restart with stronger SCF damping;
- the Figure 6h caption: one clause;
- the Conclusion's "Next" sentence.

The experiment-version manuscript is not changed.

## GATE-1 re-relaxation of *OOH, registered 2026-10-19 before any deck exists (Frank: "do the extra OOH relaxation")

**Decision of record.**
- **Offered:** the registered GATE-1 re-relaxation of both *OOH legs, up to 1,536 SU. It was flagged as unable to
  produce an η unless the H returns to its O.
- **Frank:** "do the extra OOH relaxation".

**What is run.** One re-relaxation per *OOH leg, `s0_OOH__2x1v_escape__u715_{atomic,ortho}_rerelax`.
- **Deck:** the leg's terminal SCF deck, with three lines changed:
  - `calculation = 'scf'` → `'relax'`;
  - a new prefix;
  - `max_seconds`.
- **Kept unchanged:** positions, if_pos flags, mixing (stage-1 for atomic, T1 for ortho), thresholds, `&IONS`, k-mesh,
  spin start.
- **Start:** fresh, with no density copy. The first SCF of the relaxation has the terminal SCF's inputs, so it should
  find the same electronic state. That is the sense in which it relaxes "from that SCF".
- **Check, reported and not gating:** the first SCF energy and total magnetization against the terminal SCF
  (−43355.8529 eV at 22.81 μB atomic; −43364.2673 eV at 22.83 μB ortho).
- **Run settings:** one wholenode node per leg, as one 2-task array; 6 h wall (`scf_seconds` 20,700,
  `max_seconds` 20,000); the 126-iteration SCF ceiling. No automatic retries.

**Reading** (the chemistry thresholds and the GATE-1 rule are unchanged). The re-relaxed endpoint is classified with
`hea_oer.site_integrity.DEFAULT_THRESHOLDS`, as before.
- **Not intact:** the chemical result is final for that leg. No η exists, and GATE-1 is closed, since it only guards
  an η.
- **Intact:**
  - a fresh-start terminal SCF follows (2 × 45 min, 192 SU cap), and the leg's η comes from it;
  - if that SCF again lands ≥ 5 meV below the re-relaxation's final energy, the state is unresolved, with no second
    re-relaxation.
- **Re-relaxation not COMPLETE** (ceiling, failure marker or wall): the state is unresolved. The stage-2 chemistry is
  still reported.

**Scorer change, made before any re-relaxation output exists.**
- **Inputs:** `b1_relaxed_projector_readout.py` reads `_rerelax`, and `_rescf` if one is run, for a leg whose stage-2
  SCF triggered GATE-1. It takes the re-relaxed endpoint's chemistry from that output's final coordinates.
- **Verdict label:** the scorer labels an arm whose only blockers are chemical results `NO_PAIR_CHEMICAL` instead of
  `UNRESOLVED`. Exit 2 and "never scored" are unchanged.

**Budget.** B1 has used 4,113.0 SU against the 7,488 SU ceiling, which leaves 3,375.0 SU.

| Part | SU |
|---|---|
| This re-relaxation, cap | 1,536 |
| Possible terminal SCF, cap | 192 |
| **Total cap** | **1,728** |

**Reporting.** The DFT-only sentences change only if the outcome changes.
- If both endpoints stay not intact, Section 4.4 gains no new claim.
- The restart and re-relaxation are recorded here.
