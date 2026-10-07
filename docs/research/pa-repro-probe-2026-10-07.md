# Catalyst P-A — same-state reproducibility probe at conv_thr 1e−10, 2026-10-07

## Decision of record

Frank, 2026-10-07: "Continue then. Do the probe." This licenses option 3 of the [fixed-geometry diagnostic readout](pa-fixed-geometry-diagnostic-readout-2026-10-06.md): two tight SCFs from one electronic state, at the stated hard ceiling. It does not amend job 21075231 (INCONCLUSIVE) or any registered P-A tolerance. It does not choose a protocol and licenses no relaxation, ranking or melt release.

## Question

At G2 and conv_thr 1e−10, two independent paths agree on force only to **1.84e−5 Ry/bohr**: C3 (warm, from the checkpoint through 1e−6 and 1e−8) and D2 (fresh, atomic + random through 1e−8). The other limits are 7.1e−10 Ry on energy and 3e−5 on Hubbard traces. A tolerance for any tight-boundary continuity protocol depends on what sets that 1.84e−5:

- **(N) run-to-run noise.** The same input from the same state does not repeat. The trial already showed this at conv_thr 1e−6: an exact replay of the resumed restart differed by 6.7e−5, while two from-scratch runs agreed to 1.45e−10.
- **(P) start-path dependence.** Each start converges deterministically, but to a different point inside the 1e−10 tolerance.

## Design

| Call | Start | Deck |
|---|---|---|
| **P1_C3_repeat** | Its own verified copy of C2's outdir: the exact tree C3 started from (fcbbe4ab…, 282 files, 15,205,248,011 bytes) | C3's launched deck (0f861223…) with only `outdir` changed |
| **P2_C3_repeat** | Another fresh verified copy of the same tree (never P1's output) | Same, with its own `outdir` |

Both calls run in one singleton job, sequentially, on one node. This gives three same-state samples: P1, P2, and C3 itself.

- **Same-node vs cross-node:** P1 vs P2 is a same-node pair, and P1 or P2 vs C3 is a cross-node pair (C3 ran in job 21105326).
- **What is reused unchanged:** the controller, helper, executables, pseudopotentials, MPI shape (128 ranks, `-nk 8 -ndiag 16`, one thread), `max_seconds = 7080`, `electron_maxstep = 75` and `scf_must_converge = .false.` all come from the diagnostic. The controller gains only the registered `probe` group.
- **Checks before any call:** the C2 outdir's full tree digest is verified at preflight and again by the controller.

## Registered readings

These use the diagnostic's parser and comparison unchanged: XML forces and energies in Ry and Ry/bohr, all 72×3 components. A run counts only if all of the following hold:
- the controller marks it COMPLETED;
- its start is valid ("Starting wfcs from file", "The initial density is read from file", no fallback);
- its single SCF is CONVERGED, not capped at 75 iterations.

Let s = the largest max |ΔF| over the three pairs among {C3, P1, P2}, and e = the largest |ΔE|.

- **PR1 — same-state reproducibility:**

  | Condition | Reading |
  |---|---|
  | s ≤ 1e−8 and e ≤ 1e−8 | **IDENTICAL_PATH** |
  | otherwise, s ≤ 5e−6 (half the gate) | **REPRODUCIBLE_BELOW_HALF_GATE** |
  | otherwise | **RUN_TO_RUN_NOISE_AT_GATE_SCALE** |
  | P1 or P2 not valid | **INCOMPLETE** |

- **PR2 — path vs noise:**

  | Condition | Reading |
  |---|---|
  | s ≥ ½ × 1.84e−5 | **PATH_SPREAD_WITHIN_RUN_TO_RUN_NOISE** — (N) can explain the C3–D2 spread |
  | otherwise | **PATH_SPREAD_EXCEEDS_RUN_TO_RUN_NOISE** — (P) dominates |
  | P1 or P2 not valid | **INCOMPLETE** |

- **Reported with each pair:** the same-node pair, the cross-node maximum, energies, Hubbard traces, magnetization, iteration counts, and the first SCF iteration at which the printed accuracy sequences differ. That last one is descriptive only: identical printed sequences are necessary, but not sufficient, for an identical path.

**How the readings feed the protocol decision.** IDENTICAL_PATH or REPRODUCIBLE_BELOW_HALF_GATE together with PATH_SPREAD_EXCEEDS_RUN_TO_RUN_NOISE would mean the tight-boundary tolerance must cover start-path dependence, about 1.8e−5. That suggests a tolerance of a stated multiple of it, or a common start for both sides of the comparison. RUN_TO_RUN_NOISE_AT_GATE_SCALE would mean no tolerance below the measured noise is meaningful at conv_thr 1e−10. Either result is input to Frank's protocol choice and is not adopted automatically.

## Budget

Allocation CHE260157 balance before launch: 35,845.1 CPU SU (`mybalance` on 2026-10-07; preflight re-reads it).

| Group | Slurm limit | Hard ceiling | Estimate |
|---|---:|---:|---:|
| probe | 4:30:00 | **576 SU** | 165–260 SU |

- **Estimate basis:** C3 measured 2,321 s of call wall time (31 iterations to 9.1e−11 Ry) from this exact tree. Two calls plus copies and tree digests come to about 4,800 s, or 170 SU. The upper end allows up to 50 iterations per call.
- **Why the time limit is set this high:** the controller launches a call only with at least 7,320 s of allocation remaining. This is so a stalled first call cannot leave the second without its full 7,200 s ceiling.

## Execution and stop rules

- **Staging:** exact pinned bytes from a pushed commit go to `/anvil/projects/x-che260157/sts_pa_repro_probe_2026-10-07` and are made read-only.
- **Preflight:** Python 3.9 import, every pin, the full start-tree digest, an empty queue and `mybalance`.
- **Launch:** one `sbatch --hold --no-requeue` job, then held-shape validation, then one release. No array, dependency, retry or requeue.
- **Read-only inputs:** the diagnostic's C2 outdir is only read.
- **Afterwards:** one-shot read-only status checks, then terminal accounting, the small-file mirror and the registered readout (`src/dft/pa_repro_probe_readout.py`).

Spec: `results/pa_repro_probe_2026-10-07/launch_spec.json`. Decks: `runs/hea/pa_repro_probe_2026-10-07/decks/`. Tests: `tests/test_pa_repro_probe.py`.

## Pre-launch review

An independent review found no blocker. Its fixes are folded in:

- the readout now requires the controller's COMPLETED status, so a run with no recorded status is excluded;
- every pair is labelled with the nodes read from the controller's scontrol records (C3 ran on a558), so same-node and cross-node spreads are reported from the record, not assumed;
- the time-fit test now checks the real slack, at least 900 s for the digest and copies after a full-cap P1;
- the pinned modules are LF in `.gitattributes`;
- the parse-error exclusions and docstrings are corrected.

The old diagnostic's launch scripts are historical and are not re-run: they assume the three original groups and the old controller pin.
