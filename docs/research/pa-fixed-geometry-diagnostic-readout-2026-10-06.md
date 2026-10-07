# Catalyst P-A — fixed-geometry diagnostic readout, 2026-10-06

Design of record: [pa-fixed-geometry-diagnostic-2026-10-05.md](pa-fixed-geometry-diagnostic-2026-10-05.md). Job 21075231 remains **INCONCLUSIVE**; nothing here amends it or any registered P-A tolerance.

## Verdict

The 11.46× force discrepancy at the first resumed evaluation is ordinary SCF force scatter at conv_thr = 1e−6. At the fixed geometry G2:

- every pair of conv_thr 1e−6 evaluations differs by **6.6e−5 to 1.8e−4 Ry/bohr**. That covers control, resumed, an exact replay of the resumed restart, the ethr-matched restart and an SCF-mode start from the same checkpoint;
- all of them sit **3.5e−4 to 4.0e−4 Ry/bohr** from the forces converged to 1e−10.

Matching the startup Davidson threshold does not restore continuity. The P-A force gate of 1e−5 Ry/bohr is about 7–18× tighter than the run-to-run precision of the forces it compares. It is also about 2× tighter than the agreement of two independent paths converged to 1e−10. No initialization fix at conv_thr 1e−6 can meet it.

Registered readings:

| Reading | Result |
|---|---|
| R1 | **UNAVAILABLE** (A_replay excluded by the controller, see below) |
| R2 | **ETHR_INSUFFICIENT** |
| R3 | **UNRESOLVED_REFERENCE** |
| R4 | **SCF_PATH_DIFFERS_FROM_RESTART_PATH** |
| R5 | **DISTINCT_OR_UNRESOLVED_STATE** |

The informative comparisons below explain R3 and R5. They are labelled as informative wherever they go beyond a registered rule.

## Execution and accounting

| Job | Group | Anvil EDT start / end | Elapsed | Scheduler | CPU SU |
|---|---|---|---|---|---:|
| 21105325 | replay | Oct 6 05:41:09 / 06:41:00 | 0:59:51 | FAILED 3:0 (controller: A_replay FAILED) | 127.68 |
| 21105326 | ladder | Oct 6 10:04:00 / 11:20:22 | 1:16:22 | COMPLETED | 162.92 |
| 21105327 | fresh | Oct 6 06:34:47 / 08:48:43 | 2:13:56 | COMPLETED | 285.72 |
| **Total** | | | | | **576.32** |

- **Cost against plan:** the 645–985 SU estimate and 1,995 SU hard ceiling were not reached.
- **Balance:** 36,421.4 before launch and 35,845.1 after (`mybalance`). The difference equals the parent CPUTimeRAW sum.
- **Allocation:** one whole node, 128 CPUs, 200G per job.
- **Scheduler actions:** no retry, requeue or new job.
- **Checkpoint:** the frozen checkpoint tree was unchanged after both groups that copied it (dc3637bc…, 390 files).
- **Mirror:** the 70 mirrored files match their remote sha256.

| Call | Status | Call wall s | Iterations | XML residual (Ry) | QE SCF correction (Ry/bohr) |
|---|---|---:|---:|---:|---:|
| A_replay | FAILED (failure marker) | 875 | 12 | 8.07e−7 | 3.04e−3 |
| B_ethr | COMPLETED | 2,559 | 12 + 23 | 7.34e−7 / 7.29e−8 | 2.71e−3 / 2.38e−4 |
| C1_warm_1e-6 | COMPLETED | 854 | 12 | 7.85e−7 | 2.80e−3 |
| C2_warm_1e-8 | COMPLETED | 1,229 | 17 | 9.55e−9 | 1.12e−4 |
| C3_warm_1e-10 | COMPLETED | 2,321 | 31 | 9.11e−11 | 1.9e−5 |
| D1_fresh_1e-8 | COMPLETED, **capped** (80 = electron_maxstep) | 5,474 | 80 | 1.12e−8 | 2.13e−4 |
| D2_fresh_1e-10 | COMPLETED | 2,514 | 34 | 8.77e−11 | 1.8e−5 |

Every warm start printed "Starting wfcs from file" and "The initial density is read from file" with no fallback; D1 started from atomic + random as designed. C3's residual paused near 4e−9 for several iterations and then converged.

## A_replay classification

A_replay converged at G2, printed forces, stopped at the registered boundary (global cycle 2) and reached JOB DONE with return code 0. The controller nevertheless recorded FAILED. The reason is that 3 MPI ranks printed gfortran's exit note `The following floating-point exceptions are signalling: IEEE_INVALID_FLAG IEEE_DENORMAL`, which the pinned helper's failure-marker pattern matches.

That note appears in no other run: none of the four trial runs and none of the other six diagnostic calls. Every other run shows only underflow/denormal notes. An invalid floating-point operation therefore occurred somewhere in this restart, and its location is unknown. Under the registered validity rule A is excluded, and R1 is not read. A's numbers appear below only as informative values.

## Registered readings

**R2 — startup threshold (E1).** B (diago_thr_init = 1e−6; first ethr confirmed 1.0e−6) vs the continuous control:

- Evaluation 2: max |ΔF| = **9.18e−5 Ry/bohr** (Co 21 z) and |ΔE| = 8.2e−8 Ry.
- Evaluation 3: 6.56e−5 Ry/bohr. The BFGS step then moved positions by 1.06e−4 bohr and |ΔE| = 2.5e−6 Ry.
- Reading: **ETHR_INSUFFICIENT**.
- B vs A at evaluation 2, informative: 1.40e−4. The threshold changes the SCF path, but it does not make the path continuous with the control's.

**R3 — force precision (E2).**
- Reference F* = C3 (converged, not capped).
- Precision bound max |F_C3 − F_C2| = **1.42e−4** > 5e−6, so the reading is **UNRESOLVED_REFERENCE**.
- The design assumed the 1e−8 rung would already lie near F*. It does not: C2's forces are still 1.4e−4 from C3.
- Distances to F*:

| Evaluation | conv_thr | max \|F − F*\| Ry/bohr |
|---|---|---:|
| Control, evaluation 2 | 1e−6 | 3.71e−4 |
| Resumed, evaluation 2 | 1e−6 | 4.00e−4 |
| B, evaluation 2 | 1e−6 | 3.66e−4 |
| C1 | 1e−6 | 3.58e−4 |
| C2 | 1e−8 | 1.42e−4 |

**R4 — SCF path vs restart path.** C1 vs resumed evaluation 2: **9.61e−5**, so the reading is **SCF_PATH_DIFFERS_FROM_RESTART_PATH**.

**R5 — warm vs fresh state (E5).** D2 vs C3:

| Quantity | Value |
|---|---|
| max \|ΔF\| | 1.84e−5 (Co 23 z) |
| \|ΔE\| | 7.1e−10 Ry (0.0096 meV) |
| max \|ΔTr[ns]\| | 3e−5 |
| \|Δ total magnetization\| | 5.1e−5 |
| \|Δ absolute magnetization\| | 4.5e−5 |
| Capped | neither run |

The reading is **DISTINCT_OR_UNRESOLVED_STATE**. Every state criterion passes and only the force criterion fails, by 1.84×. That margin matches both runs' own SCF force correction (1.8e−5 / 1.9e−5).

## What the numbers show (informative)

Pairwise max |ΔF| among the five conv_thr 1e−6 evaluations of G2, in Ry/bohr (`informative_distances.json`, same parser and XML):

| | resumed | A (excluded) | B | C1 |
|---|---:|---:|---:|---:|
| control | 1.15e−4 | 7.66e−5 | 9.18e−5 | 8.40e−5 |
| resumed | | 6.72e−5 | 1.78e−4 | 9.61e−5 |
| A | | | 1.40e−4 | 6.63e−5 |
| B | | | | 1.06e−4 |

1. **The trial failure sits inside the ordinary scatter.** The original 1.15e−4 is one value in a 6.6e−5 to 1.8e−4 spread. That spread includes a replay of the identical restart: A vs resumed, same deck, checkpoint, binary and layout, gives **6.72e−5** and |ΔE| = 1.4e−7 Ry. The continuous path did reproduce itself to 1.45e−10 in the trial (control vs candidate evaluation 1). So the restart path carries a run-to-run component that the loose SCF amplifies to about 1e−4.
2. **Every 1e−6 force shares a large offset from converged.** All lie 3.5–4.0e−4 from both C3 and D2, with energies 1.35–1.53e−6 Ry above. This agrees in magnitude with QE's own SCF correction (2.7–3.3e−3 Ry/bohr total-force norm).
3. **Force error falls slowly with conv_thr.** Measured against the converged pair:

   | conv_thr | Force error, Ry/bohr |
   |---|---|
   | 1e−6 | ≈ 3.6–4.0e−4 |
   | 1e−8 | 1.4–1.8e−4 (C2, and D1 capped at 1.1e−8) |
   | 1e−10 | 1.84e−5 (C3 vs D2) |

   Two independent paths at 1e−10 agree on energy to 7e−10 Ry, but on force only to 1.8e−5.
4. **The warm/fresh spread recorded in the trial was precision, not a second basin.** Its 8.82e−4 at about 1e−6 shrinks to 1.84e−5 at 1e−10, and Hubbard traces and total magnetization agree to 3e−5 and 5.1e−5.

## Competing explanations after the diagnostic

| | Explanation | Status |
|---|---|---|
| E1 | Startup ethr difference | Not sufficient (R2 registered). |
| E2 | Finite SCF force precision at conv_thr 1e−6 | Strongly supported by every comparison above. The registered R3 is UNRESOLVED only because the 1e−8 rung was not close enough to bound the reference at 5e−6. The reference's two-path agreement (1.84e−5) is still about 20× smaller than the 1e−6 forces' offset. |
| E3 | Other restart state (occup.txt precision, eigenvalues) | Not isolated. Hubbard traces agree to ≤ 8e−5 among the 1e−6 evaluations. Their 7e−4 to 1.1e−3 offset from the tight rungs also follows conv_thr, so E2 already accounts for the magnitude. |
| E4 | Restart path not reproducible | Indicated by A vs resumed (6.72e−5), but A is excluded from R1. The source of the run-to-run component, and of A's IEEE_INVALID signal, is unknown. |
| E5 | Warm and fresh reach different states | Not supported: same energy, traces and magnetization. The force difference is at the 1e−10 precision floor (R5 registered as unresolved). |

## Consequences and next steps

The trial's registered continuity comparison requires 1e−5 Ry/bohr between forces whose measured run-to-run precision at conv_thr 1e−6 is about 1e−4. It fails for any change of SCF path, including a bit-level replay of the same restart. Fixing initialization (ethr, start mode) cannot make it pass.

Any revision is a prospective protocol change, run as a new experiment with its own approval. Measured options:

1. **Tighten the boundary SCF and set the tolerance from measured precision.** Evaluate continuity at conv_thr 1e−10, which cost 2,321 s for C3 from a 1e−8 state. Set the force tolerance to a stated multiple of the measured two-path spread: 1.84e−5 Ry/bohr, so for example 5e−5. Measured cost: tightening a 1e−6 state through 1e−8 to 1e−10 took 1,229 + 2,321 s, about 126 SU at 128 cores.
2. **Keep conv_thr 1e−6 but compare at the measured precision.** That needs a force tolerance of at least 2e−4 Ry/bohr, which barely discriminates against the 3.6–4.0e−4 offset. This is weak.
3. **First measure same-path reproducibility at 1e−10.** Two restarts from one state would show whether the precision floor is path- or round-off-limited before a tolerance is chosen. This is small: about 80 SU per tight SCF from a 1e−8 state (C3 measured).

Separately, the IEEE_INVALID signal seen only in A_replay is unexplained. It can be probed without new compute only by reading QE's restart path; a recompute would need approval.

## Sources

Files are under `results/pa_fixed_geometry_diag_2026-10-05/`:

- [registered readout](../../results/pa_fixed_geometry_diag_2026-10-05/readout.json)
- [informative distances](../../results/pa_fixed_geometry_diag_2026-10-05/informative_distances.json) and their script
- [terminal accounting and mirror receipt](../../results/pa_fixed_geometry_diag_2026-10-05/terminal_collection.json)
- the mirrored runs and group receipts in `raw_mirror/`
- the status snapshots and watch observations
- the interim readout from the six finished calls (`interim_2026-10-06_readout/`), which gave the same R2 before C3 finished

The trial comparison inputs are under `results/pa_catalyst_retest_readout_2026-10-05/raw_mirror/trial_results/`. The local watcher stopped on 2026-10-05 at 23:13Z (killed by the host for low memory) and was not restarted; one-shot read-only status checks replaced it.
