# Catalyst P-A — O1 and reproducibility-probe readout, 2026-10-07

Designs of record: [O1](pa-catalyst-o1-2026-10-07.md) (job 21159532) and the [same-state reproducibility probe](pa-repro-probe-2026-10-07.md) (job 21157910). Job 21075231 remains **INCONCLUSIVE**; nothing here amends it or any registered tolerance.

## Verdict

| Run | Registered reading |
|---|---|
| **O1** | **CONTINUITY_PASS**. One stop/resume boundary at the registered geometry shows no restart defect larger than the O1 tolerances |
| **Probe PR1** (same-state reproducibility) | **INCOMPLETE**. P1 is excluded: the controller marked it FAILED on a gfortran IEEE_INVALID_FLAG exit note |
| **Probe PR2** (path vs noise) | **INCOMPLETE**, same cause |

- **O1 differences:** O1's resumed run differs from the continuous control by the same amounts 21075231 measured. The reading changed because the registered tolerances changed, and those tolerances were set from measured SCF precision before launch.
- **Detection:** the run's own negative control is a real lost-history defect, and it lands 4–9× outside every O1 tolerance. The tolerances therefore still detect the defect they exist for.
- **Probe:** the one valid probe pair, C3 vs P2, already bounds PR1. Same input, same start files, and the forces still differ by **6.2e−6 Ry/bohr**.

## Execution and accounting

| Job | Run | Anvil EDT start / end | Elapsed | Scheduler | Node | CPU SU |
|---|---|---|---|---|---|---:|
| 21157910 | probe | Oct 7 04:24:36 / 05:44:34 | 1:19:58 | FAILED 3:0 (controller: P1 FAILED) | a918 | 170.60 |
| 21159532 | O1 | Oct 7 05:48:40 / 09:37:49 | 3:49:09 | COMPLETED | a637 | 488.85 |
| **Total** | | | | | | **659.45** |

- **Cost against plan:**
  - probe: estimate 165–260 SU, ceiling 576;
  - O1: estimate 350–550 SU, ceiling 1,024.
- **Balance:** 35,845.1 before launch, 35,185.7 after (`mybalance`, 14:23 UTC). The difference equals the CPUTimeRAW sum.
- **Scheduler actions:** none beyond the plan. No retry, requeue or new job, and the controllers submitted nothing.
- **Mirrors:** probe 21 files, O1 55 files, every one matching its remote sha256 (`terminal_collection.json` in each results folder).

## O1

### Registered conditions

| Condition | Result |
|---|---|
| Calls | control, candidate, fresh, resumed, negative: all NUMERICAL_RECEIPT_VALIDATED. No IEEE_INVALID, OVERFLOW or DIVIDE_BY_ZERO note in any stderr |
| Pre-resume decision | **RESUME_CANDIDATE**: warm − fresh = −0.14 meV (δ = 10 meV). Checkpoint d03cfddb… unchanged across the fresh check |
| conv_thr carry-over | equal: the candidate printed `new conv_thr = 1.0e−6` after evaluation 1, and the resumed deck uses 1e−6 |
| Negative control | BFGS history deleted at startup ("deleted, as requested"), optimizer count 0 |
| Continuity | all three ordered evaluations within tolerance (table below) |

| Evaluation | Comparison | ΔE (Ry) | Δposition (bohr) | max ΔF (Ry/bohr) | Largest force component |
|---|---|---:|---:|---:|---|
| 1 | control vs candidate (before the stop) | 3.1e−10 | 0 | 1.3e−10 | Co13 y |
| 2 | control vs resumed (first after the resume) | 1.41e−7 | 1.3e−10 | 6.12e−5 | Co13 z |
| 3 | control vs resumed | 1.69e−7 | 6.40e−5 | 8.74e−5 | Co20 z |
| | **O1 tolerance** | **3e−5** | **1e−3** | **5e−4** | |
| | largest / tolerance | 0.006 | 0.064 | 0.17 | |

Further results:

- **Same electronic state at every evaluation (informative).** Hubbard traces agree within 3e−5, and total magnetization is identical at stdout resolution (0.01).
- **After the resume.** The resumed run tightened conv_thr to 8.34e−8 and then 6.87e−8; the control tightened to 8.35e−8 and 6.83e−8.
- **Per-call wall time:**

  | Call | Wall time (s) |
  |---|---:|
  | control | 2,932 |
  | candidate | 564 |
  | fresh | 3,399 |
  | resumed | 2,514 |
  | negative | 3,716 |

- **Flags not validated by this run.** The receipt keeps `every_step_pa_validated`, `terminal_fresh_acceptance_validated` and `production_accepted` false.

### Same behaviour as 21075231; different tolerances

| Quantity | 21075231 (historical re-read) | O1 | 21075231 tolerance | O1 tolerance |
|---|---:|---:|---:|---:|
| max ΔF, evaluation 2 | 1.15e−4 | 6.12e−5 | 1e−5 | 5e−4 |
| max ΔF, evaluation 3 | 6.99e−5 | 8.74e−5 | 1e−5 | 5e−4 |
| ΔE, evaluation 3 | 5.04e−6 | 1.69e−7 | 1e−6 | 3e−5 |
| Δposition, evaluation 3 | 6.77e−5 | 6.40e−5 | 1e−5 | 1e−3 |

Under the 21075231 tolerances, O1's forces would have failed again, by 8.7×. The two runs agree on what a defect-free restart looks like at conv_thr 1e−6: forces within about 1e−4 Ry/bohr and positions within about 7e−5 bohr. This is the scatter the [fixed-geometry diagnostic](pa-fixed-geometry-diagnostic-readout-2026-10-06.md) measured at one geometry: 6.6e−5 to 1.8e−4.

### Sensitivity (informative): the negative control against the tolerances

The negative control resumes from a copy of the same checkpoint with the BFGS history deleted. Its first evaluation therefore sits at the control's evaluation-2 geometry, and its second follows a step taken without history (`informative_negative.json`).

| Pair | ΔE (Ry) | Δposition (bohr) | max ΔF (Ry/bohr) | Multiple of O1 tolerance (E / pos / F) |
|---|---:|---:|---:|---|
| control e2 vs negative e1 (same geometry) | 4.3e−8 | 1.3e−10 | 1.84e−4 | 0.001 / 0.000 / 0.37 |
| control e3 vs negative e2 (after the history-free step) | 2.66e−4 | 4.87e−3 | 2.10e−3 | **8.9 / 4.9 / 4.2** |

What the two rows show:

- **Same geometry.** The 1.84e−4 force difference is ordinary conv_thr 1e−6 scatter, the top of the diagnostic's range, at 0.37 of the tolerance.
- **One step later.** The lost history moves the geometry by 4.9e−3 bohr and the energy by 3.6 meV. All three tolerances catch it.
- **Separation.** On each metric, the passing restart sits 24× (force), 76× (position) and about 1,600× (energy) below this defect.

### What the pass licenses

It certifies one stop/resume boundary, after evaluation 1 at the registered geometry, under the O1 tolerances. Per the design, it licenses only a separately costed production relaxation. It does not certify every-step P-A, a lower-state reseed or terminal fresh acceptance. The DFT predictions of S8 arm C still need production relaxations, references and adsorption energies ([S8 freeze proposal §4](s8-stage1-freeze-proposal-2026-10-07.md)).

## Reproducibility probe

### Calls

| Call | Controller | SCF | Start | Wall |
|---|---|---|---|---:|
| P1_C3_repeat | **FAILED** (failure marker) | CONVERGED, 31 iterations, 9.3e−11 Ry, `JOB DONE`, return code 0 | valid: files read, tree fcbbe4ab… verified | 2,255 s |
| P2_C3_repeat | COMPLETED | CONVERGED, 32 iterations, 8.1e−11 Ry | valid, same verified tree | 2,433 s |
| C3_warm_1e−10 (diagnostic, job 21105326, a558) | COMPLETED | CONVERGED, 31 iterations, 9.1e−11 Ry | valid | 2,321 s |

**Why P1 is FAILED.** One rank's exit note reads `IEEE_INVALID_FLAG IEEE_UNDERFLOW_FLAG IEEE_DENORMAL`; P1's stderr has 63 notes, all other notes are underflow or denormal only. The controller saw the marker 0.3 s before the call ended, so the note was printed at exit, after the SCF had converged and the files were written. The unchanged failure rule (`IEEE_(INVALID|OVERFLOW|DIVIDE_BY_ZERO)_FLAG`) fails the call. The start tree was unchanged after both copies.

### Registered readings

Both readings are **INCOMPLETE**, as registered for "P1 or P2 not valid".

The valid data still bound PR1. The C3 vs P2 pair is cross-node (a558 / a918) and differs by **6.17e−6 Ry/bohr** (Co22 y) and 3.9e−10 Ry. Its printed accuracy sequences first differ at iteration 7. Since s is the maximum over the three pairs, s ≥ 6.17e−6, which is above the half-gate line of 5e−6. Whatever P1 had shown, PR1 could not have been IDENTICAL_PATH or REPRODUCIBLE_BELOW_HALF_GATE.

PR2 depends on P1 and is not determined by the valid data.

### Informative: P1 included

These are the probe readout's own checks and comparison applied to P1 (valid start, one converged SCF; `informative_distances.json`). They are not registered readings.

| Pair | Nodes | max ΔF (Ry/bohr) | ΔE (Ry) | Hubbard trace | First accuracy divergence |
|---|---|---:|---:|---:|---:|
| C3 vs P1 | a558 / a918 | 1.34e−6 | 2.7e−10 | 1e−5 | iteration 8 |
| C3 vs P2 | a558 / a918 | 6.17e−6 | 3.9e−10 | 1e−5 | 7 |
| P1 vs P2 | a918 / a918 | 4.83e−6 | 1.1e−10 | 1e−5 | 7 |
| C3 vs D2 (warm vs fresh path) | a558 / — | 1.84e−5 | 7.1e−10 | 3e−5 | 1 |
| P1 vs D2 | a918 / — | 1.95e−5 | 9.8e−10 | 3e−5 | 1 |
| P2 vs D2 | a918 / — | 2.24e−5 | 1.09e−9 | 4e−5 | 1 |

With P1 counted, s = 6.17e−6 and e = 3.9e−10. That falls in the RUN_TO_RUN_NOISE_AT_GATE_SCALE band for PR1, just above 5e−6, and in the PATH_SPREAD_EXCEEDS_RUN_TO_RUN_NOISE band for PR2 (6.17e−6 < ½ × 1.84e−5 = 9.21e−6).

What this shows:

- **Same input, same files, different result.** At conv_thr 1e−10, the same deck from the same verified files does not repeat. Every pair, including the same-node P1–P2 pair, diverges in the printed accuracy at iteration 7–8, and the final forces end 1.3e−6 to 6.2e−6 apart. The variation is run to run, not a node difference. Candidate mechanisms are run-dependent reduction order in the parallel sums and run-time library algorithm selection; this probe cannot separate them.
- **Start path is the larger effect.** The warm-versus-fresh spread (1.8e−5 to 2.2e−5) is 3–4× the same-state spread. Start-path dependence is the larger part of the C3–D2 difference, but run-to-run noise is about a third of it.
- **Consequence for a tight-boundary protocol.** Any continuity tolerance at conv_thr 1e−10 needs to sit at about 2e−5 Ry/bohr or above, or both sides must share a start. The registered 1e−5 gate is below the warm-versus-fresh spread at conv_thr 1e−10. At conv_thr 1e−6, which is O1's precision, the scatter is 6e−5 to 1.8e−4, and O1's 5e−4 covers it.

## The IEEE_INVALID exit note

It has now appeared in 2 of 18 recent calls:
- the 4 calls of 21075231;
- the 7 diagnostic runs;
- the 2 probe runs;
- the 5 O1 calls.

| Call | Ranks with the note | Effect on the numbers |
|---|---|---|
| A_replay | 3 | none visible |
| P1 | 1 | none visible: P1 sits 1.3e−6 from C3, closer than the clean P2 (6.2e−6) |

The note records that an invalid operation (for example 0/0 or the square root of a negative number) happened somewhere on that rank. It does not say where, and the flag may have been raised in a branch whose result is never used. Under the registered rule it fails the call. At about 1 in 9 calls, that is a material retry cost for production.

## Open decisions (Frank)

**Decision of record, 2026-10-07.** Frank: "Continue it. OK With me." This accepts the IEEE_INVALID recommendation in item 2: the rule stays unchanged for production, and the budget allows about 11% re-runs. It also starts the design and pricing in item 1. No production SU is approved by this decision.

1. **Production relaxation.** O1's pass licenses a separately costed design and SU estimate for the arm-C production relaxations. Arm C must be deposited before OER, with Oct 21 as the fallback date.
2. **The IEEE_INVALID rule for production.**
   - *Recommendation:* keep the rule unchanged and budget for about 11% re-runs. The alternative is a registered amendment made before production, for example failing only on a non-finite energy, force or position. Weakening a failure rule after it has bitten twice is the kind of post-hoc change the registration exists to prevent.
   - *Optional diagnostic:* a short run with `-ffpe-trap=invalid` would locate the source. It is costly to reproduce at a rate of about 1 in 9.
3. **Tight-boundary (1e−10) protocol: not needed now that O1 has passed.** If one is wanted later, its tolerance should cover start-path dependence (≥ about 2e−5 Ry/bohr), or both sides should share a start.

## Files

- **O1:** `results/pa_catalyst_o1_2026-10-07/`
  - `readout.json` (registered);
  - `informative_negative.{py,json}`;
  - `terminal_collection.json`;
  - `raw_mirror/`;
  - status snapshot.
- **Probe:** `results/pa_repro_probe_2026-10-07/`
  - `readout.json` (registered);
  - `informative_distances.{py,json}`;
  - `terminal_collection.json`;
  - `raw_mirror/`;
  - status snapshots.
