# A stall-robust relaxation protocol for the DFT+U slabs — research plan, 2026-09-22

Status: PLAN. Nothing here is licensed; the experiment below runs only under a dated A11.R3 line with the counts and costs stated in §4. Scope: the numerical protocol for relaxations on the census slabs; no threshold, projector, U value, magnetic start or basin rule of record changes.

## 1. What is established (docs/research/lowtail-clean-slab-scf-stall-2026-09-19.md, readouts of 2026-09-22)

1. On the Cu8Cr23Mn35Co34 seed20 site2 clean slab, two self-consistent states coexist at one geometry, 94.7 meV apart, differing only by an orbital reorientation of two minority-spin d electrons on one surface Co (atom 20). The higher state is stationary with a residual floor of 3.5e-7 Ry under local-TF and plain mixing and cannot meet the production threshold 8.08e-8 Ry; the lower state meets thresholds down to 4.3e-8 Ry in 12 to 34 iterations.
2. The state travels with the density and Hubbard occupations: a seeded SCF reproduces either state in one to three iterations with fresh wavefunctions; the retained densities of the two other stalls (Cu8 unreconstructed-O, Fe25 clean slab) are likewise stationary with residual floors of 2.5e-6 and 1.2e-5 Ry.
3. A relaxation carries its state from one ionic step to the next. Restarted from the low state, the Cu8 slab relaxed six steps and 94 meV, retained the Co-20 configuration, and stalled again at the seventh step with a milder residual floor (1.4e-7 Ry) that is not the same single-site flip. Re-seeding once is therefore not a protocol.
4. On array 20813525, of five terminal legs three stopped at the SCF ceiling and two completed; every stall has the same signature (stationary energy, residual floor, no drift).

The production protocol has no state check: an SCF that converges at a loose early threshold in a higher state passes, and an SCF that cannot converge in that state stops the leg. Both outcomes silently leave the forces of a metastable electronic state in the trajectory.

## 2. Candidate mechanisms in this build (pw.x 7.5, HUBBARD card, atomic projector)

| Id | Protocol | What it does | Cost per ionic step | Changes a registered setting? |
|---|---|---|---|---|
| P-A | Checked relaxation | After each converged ionic step, a fresh-start SCF (atomic+random wavefunctions, atomic density) at the same geometry; if it lies more than δ below the relaxation's SCF, or if the relaxation's SCF stalls, the relaxation is re-seeded from the fresh density at that geometry and the step is repeated. δ = 10 meV, pre-stated. | one extra SCF (≈3,500 s fresh, ≈125 core-h) per accepted step; a re-seed repeats one step | no: only the driver changes; deck bytes of each SCF are the production deck with the seed lines |
| P-B | Occupation-fixed start | `mixing_fixed_ns = 15` in `&ELECTRONS`: the Hubbard occupation matrices are held at their starting values for the first 15 iterations of each SCF, so the density settles before the orbital configuration is allowed to move. | none | adds one `&ELECTRONS` line to the deck template (the hea_deck `_ALLOWED` list must admit it); no threshold, U, projector or start changes |
| P-C | Fresh start every step | External BFGS driver with a fresh-start SCF at every geometry, no carried density. | every SCF is fresh (≈2×) | no deck change; driver only |
| P-D | Threshold floor | `upscale` limited so `conv_thr` never tightens below 1e-7 Ry. | none | changes the registered convergence behaviour; rejected: the stationary states sit at 1.4e-7 to 3.5e-7 Ry, so they would still fail or, at a looser floor, be accepted with their wrong energies |
| P-E | Reactive re-seed only | As P-A but the fresh-start check runs only after a stall. | small | misses steps that converged in a higher state at a loose threshold (the production run's first four cycles did exactly that) |

P-D and P-E are excluded by the evidence. P-C is P-A without the comparison and at double cost; it is the fallback if P-A's warm SCFs stall too often. P-B is the only cheap knob and is testable on one leg.

## 3. The experiment: the Cu8 clean slab, the one geometry with a known low state

Two arms, both starting at the cycle-5 coordinates from the low-state density (as array 20851756 did), production settings otherwise, HEA-4 supervision per SCF (iteration 127 stop, KILLED, scratch preserved).

| Arm | Leg | Design | Pre-stated success |
|---|---|---|---|
| A | `slab_c5low__checked` | P-A: relaxation in segments of one BFGS step (`nstep` per segment, BFGS history continued from the retained `.bfgs` file with `restart_mode = 'restart'`); after each segment a fresh-start SCF at the new geometry; re-seed on a drop of more than δ or on a stall; at most 40 segments and at most 10 re-seeds | BFGS converged (total force < 0.002 Ry/bohr, the deck's `forc_conv_thr`) within the caps, every accepted step's energy within δ of its fresh-start check; the readout reports steps, stalls, re-seeds, extra SCFs, the final energy and geometry, and atom 20's spin-down diagonal per step |
| B | `slab_c5low__fixedns15` | P-B: the seeded relaxation of array 20851756 repeated with `mixing_fixed_ns = 15`, one pw.x process | either BFGS converged within the caps, or a stall at a later step than the seventh; the readout reports at which step and residual it stops and whether atom 20's configuration is retained |

A leg that stops is read as a numerical outcome (steps, residual, state) exactly as the readouts of 2026-09-22 were; neither arm produces a census result, an adsorption reference or a claim. If Arm A converges, the protocol is applied to the remaining Cr-site legs under a new dated line; if it does not, P-C is the next arm.

## 4. Counts and cost (HEA-7), for the dated line

Basis: a fresh-start Cu8 clean-slab SCF at 128 ranks took 3,485 s (124 core-h); a warm SCF in the low state 12 to 34 iterations, about 1,100 to 2,000 s (40 to 70 core-h); BFGS steps to convergence on this slab unknown, planned 20 (the array's planning basis), ceiling 40.

| Arm | Legs | pw.x processes | Planning core-h | Ceiling core-h | Scheduler cap |
|---|---|---|---|---|---|
| A | 1 | up to 40 relax segments + 40 fresh SCFs + 10 re-seeds | 20 × (55 + 124) ≈ 3,600 | 40 × (70 + 124) + 10 × 70 ≈ 8,500 | one task, 4,320 minutes (72 h) at 128 ranks = 9,216 core-h, or two chained tasks of 2,160 minutes |
| B | 1 | 1 | 590 | 1,668 (46,000 s + 900 s projection) | one task, 780 minutes = 1,664 core-h |
| both | 2 | | ≈ 4,200 | ≈ 10,200 | ≈ 10,900 |

Balance at 18:45 UTC: 43,410 SU, with 3,674 planning / 12,101 ceiling core-h still committed to array 20813525 tasks 6 to 9. The row (12 legs, 7,124 / 22,995) is not affordable at ceiling on top of this experiment until the array's remaining legs have drawn their actual cost.

## 5. Implementation, offline before any launch

1. Driver: a `checked_relax` stage kind in `src/dft/research_batch_seeded.py` (sibling file unchanged for every existing kind): segment loop, fresh-start SCF deck derived from the segment geometry with the five known substitutions, energy comparison, re-seed by the existing content-pinned scratch seed, per-step receipts (energies, residuals, iterations, atom-20 diagonal from `occup.txt`), the HEA-4 supervisor on every pw.x process, and a leg wall ceiling. Tests with process doubles for: comparison and re-seed logic, the re-seed cap, the segment cap, receipts, and that no stopped SCF is ever read as an energy.
2. Decks: Arm B needs `mixing_fixed_ns` admitted by the template's allowed substitutions; a builder like `lowtail_low_state_restart.py` renders both arms with byte checks.
3. Specification, manifests, wrappers and launcher options as for the batches of 2026-09-22; the launcher's population and inspector already handle one-task arrays.
4. Readout: per-step tables from the receipts; comparison of Arm A's accepted energies with Arm B's; the Co-20 diagonal per step.

Estimated time: implementation and offline tests one working day; Arm B reads out within 13 hours of launch, Arm A within one to three days. The melt-set freeze (S8) waits on this by the entrant's election of 2026-09-22 and moves to the week of Sep 28 at the earliest.

## 6. What this plan does not do

It does not change U values, projectors, magnetic starts, thresholds, cutoffs, smearing or the kill rule; it does not license any leg; it does not touch arrays 20813525, 20840139, 20845364, 20851753 or 20851756; it does not make the generalization row licensable; and it does not claim that a converged Arm A geometry is the ground-state geometry, only that every accepted step was checked against a fresh start at δ.
