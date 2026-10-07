# Catalyst P-A — continuity-protocol options for the entrant's decision, 2026-10-07

Status: options memo, no compute. The entrant decides (open item in `tasks/todo.md`, 2026-10-06). Nothing here amends job 21075231 (INCONCLUSIVE) or any registered tolerance. Whichever option is chosen runs as a new, separately approved experiment.

## What the continuity gate is for

P-A is a checked relaxation. After each ionic step the relaxation stops at the evaluated geometry and a fresh-start SCF runs there. The relaxation is reseeded only if the fresh state is more than δ = 10 meV lower or the warm SCF stalls. Otherwise it resumes with its inherited state ([eligible-comparison readiness](eligible-comparison-pa-readiness-2026-10-03.md) §P-A; [stall protocol plan](lowtail-stall-robust-protocol-plan-2026-09-22.md)).

Every step is therefore a stop/resume. The continuity gate certifies that a stop/resume without a reseed does not change the relaxation: the resumed trajectory must match a continuous one. The registered gate is 1e−6 Ry energy, 1e−5 bohr positions and 1e−5 Ry/bohr force, on the maximum Cartesian component of every compared evaluation.

## Measured facts that bound any tolerance

Noise floor: what stop/resume-free runs disagree by at conv_thr 1e−6 (G2, 72-atom slab, 128 ranks):

| Quantity | Measured spread | Source |
|---|---|---|
| Force, same geometry, any two SCF paths | 6.6e−5 to 1.8e−4 Ry/bohr (5 runs, 10 pairs) | [diagnostic readout](pa-fixed-geometry-diagnostic-readout-2026-10-06.md) |
| Force, exact replay of the same restart | 6.7e−5 Ry/bohr | same |
| Energy, same geometry | ≤ 1.9e−7 Ry | same |
| Next-step positions after a 9.2e−5 force difference | 1.06e−4 bohr (B vs control, evaluation 3) | R2 |
| Next-step energy | 2.5e−6 Ry (0.034 meV) | R2 |
| Force offset of every 1e−6 SCF from converged | 3.5–4.0e−4 Ry/bohr | R3 informative |
| Force agreement of two paths at 1e−10 | 1.84e−5 Ry/bohr | R5 |

Defect scale: what a real stop/resume defect looks like here (control of job 21075231):

| Defect | Signature |
|---|---|
| BFGS history lost or reset (the September Arm A failure mode) | The next step changes by a large fraction of a BFGS step. Measured steps: 1.9e−2 and 2.2e−2 bohr max displacement, −25.5 and −17.3 meV |
| Electronic state reconstructed into the other basin | 94.7 meV (Co 20 orbital state); Hubbard traces change by ≫ 1e−3 |
| Relaxation stop criterion | forc_conv_thr = 2e−3 Ry/bohr |

The registered force gate (1e−5) sits 7–18× **below** the noise floor. The defects that matter sit 1–3 decades **above** it, so there is a usable window between the two.

Costs (128 cores, 0.0356 SU/s):

| Item | Time | Cost |
|---|---|---|
| Relaxation step at conv_thr 1e−6 | 480–1,500 s per evaluation plus about 64 s of forces | about 34 SU per step (control: 3 evaluations = 102.5 SU) |
| Fresh check | 3,385–4,680 s | 120–166 SU |
| Tightening one state from 1e−6 to 1e−10 | 3,550 s | about 126 SU |
| Re-test 21075231 | | 353.9 SU |
| Diagnostic | | 576.3 SU |

## Options

| | Change | What it certifies | Cost / calendar | Main risk | Depends on the running probe? |
|---|---|---|---|---|---|
| **O1 Precision-referenced gate** | Re-run the re-test design unchanged at conv_thr 1e−6 with new registered tolerances set inside the noise–defect window: force 5e−4 Ry/bohr (about 3× the largest measured spread, ¼ of forc_conv_thr), positions 1e−3 bohr (about 10× the measured carry-over, 5% of a BFGS step), energy 1e−5 Ry (0.14 meV, 1/70 of δ). The state checks stay: Hubbard traces ≤ 1e−3, magnetization ≤ 0.01 | Stop/resume introduces no defect larger than 5% of a BFGS step or 0.14 meV, which covers the history-loss and state-switch modes | about 350 SU; about 1 day including queue | Tolerances rest on few samples (n = 5 at evaluation 2, n = 1 at evaluation 3). A defect below them passes, and would also be immaterial at that size | No |
| **O2 Noise-suppressed validation** | Same comparison, but every compared evaluation runs at conv_thr 1e−10 (upscale fixed so QE's adaptive tightening cannot differ). Force tolerance about 5e−5 (≈ 2.5× the 1.84e−5 two-path spread) | The restart code is transparent with SCF noise removed. The certificate transfers to production at 1e−6 because the restart code is the same | 700–1,000 SU; 1–2 days | Strongest claim, highest cost. Pointless if same-state SCFs do not repeat | **Yes**: worth it only if PR1 = IDENTICAL_PATH or REPRODUCIBLE_BELOW_HALF_GATE |
| **O3 Endpoint equivalence** | Run a stop/resume relaxation and a continuous one to forc_conv_thr. Accept on final energy within 1 meV, same state, both converged and geometry within 1e−2 bohr | The question that matters for adsorption energies: does stop/resume change the answer? | 1,700–2,500 SU; 2–4 days | Too slow for the Oct 13–15 freeze. A trajectory-level defect that happens to converge to the same end passes, which is acceptable for the science | No |
| **O4 Side-car checks** | Stop interrupting the relaxation. It runs as one long call; each completed step's geometry gets its fresh SCF in a parallel job; only a flagged step (> 10 meV) triggers the existing intentional reseed (roll back to that step, reset history). No unflagged step is ever a stop/resume, so the continuity question disappears | Nothing new needs certifying except the rollback/reseed path, which is an intentional discontinuity | Same fresh-check SU as P-A, but run in parallel (shorter wall time); new driver code (1–2 days) plus a 300–500 SU validation | New code right before the freeze. The per-call 7,200 s cap must be lifted for the relaxation (30 steps ≈ 8–17 h in one job). Up to about 2 wasted steps after a flagged one | No |

Two policy items stay open under every option and must be fixed in the chosen design:

1. **Adaptive conv_thr.** QE tightens conv_thr during a relaxation (the next conv_thr printed after evaluation 2 was 8.4e−8 in both arms). A resumed deck must start at the continuous run's current value, not the deck's 1e−6, or later comparisons mix precisions.
2. **Persistent vs reconstructed electronic state** (re-test readout recommendation 3). The unexplained IEEE_INVALID signal in A_replay, the only one in 11 runs, is a residual risk for O1 and O2. An offline read of QE's restart path can bound it without compute.

## Recommendation

**O1 now, O4 later.**

O1 is the only option that fits the Oct 13–15 freeze. It costs about one re-test. Its tolerances are justified from both sides: above the measured noise, and far below every defect that would change a result. The existing terminal fresh acceptance still guards the endpoint.

If P-A becomes the production workhorse after the freeze, O4 is the cleaner architecture: it removes per-step stop/resume, and with it the continuity question, instead of certifying it.

O2 is worth its cost only if the running probe returns IDENTICAL_PATH or REPRODUCIBLE_BELOW_HALF_GATE and a near-registered-strength certificate is wanted. O3 is the most direct test, but it does not fit the calendar.

## If O1 is chosen

1. A design doc freezes the O1 tolerances and the adaptive-conv_thr carry-over rule before launch. A second numerical comparison is not allowed.
2. The re-test controller, decks and readout are reused, with the tolerance constants and the conv_thr carry-over as the only changes. Tests are added for both.
3. Pricing (about 350 SU, ceiling about 1,000 SU), held submit, validation and one release follow the usual procedure.
4. Readout: PASS licenses only the separately costed production relaxation, as before. References, adsorption and ranking still precede the melt.
