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
