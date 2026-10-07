# Catalyst P-A — O1 one-boundary re-test under precision-referenced tolerances, 2026-10-07

## Decision of record

Frank, 2026-10-07: "Ok do O1." This licenses option O1 of the [continuity-protocol options memo](pa-continuity-protocol-options-2026-10-07.md): one new run of the registered one-boundary re-test with continuity tolerances set from measured SCF precision. The cost ceiling is stated below.

- Job 21075231 stays **INCONCLUSIVE**, and its data are not re-scored.
- This run licenses no production relaxation, ranking or melt release.

## What changes, and what does not

O1 repeats the launched re-test (`docs/research/pa-catalyst-retest-2026-10-04.md`, job 21075231) call for call:

1. control relaxation, three evaluations;
2. candidate stopped after evaluation 1;
3. isolated fresh-start SCF at the evaluated geometry;
4. pre-resume decision;
5. resumed relaxation from a copy of the immutable checkpoint, evaluations 2–3;
6. the registered negative control.

Everything else also stays the same: deck, seed, executables, pseudopotentials, MPI shape, per-call ceiling (7,200 s), QE `max_seconds` (7,080), failure-marker rules, real-control preflight replay and resource validation.

The frozen modules keep their bytes. O1 runs two pinned siblings: `src/dft/pa_catalyst_o1.py` and `src/dft/pa_qe_adapter_o1.py`. Their complete diffs are in `results/pa_catalyst_o1_2026-10-07/{controller_o1_vs_retest,adapter_o1_vs_v2}.diff`, and the tests confine them line by line.

| Changed | Re-test (21075231) | O1 |
|---|---|---|
| Continuity tolerances (maximum component, every compared evaluation) | 1e−6 Ry, 1e−5 bohr, 1e−5 Ry/bohr | **3e−5 Ry, 1e−3 bohr, 5e−4 Ry/bohr** |
| Identity checks (resume geometry = saved proposal, settings, cell) | 1e−5 bohr and exact | unchanged |
| conv_thr carry-over | not checked | **the last `new conv_thr` printed by the candidate must equal the resumed deck's conv_thr (relative 1e−9); otherwise INCONCLUSIVE** |
| Schema, date, Anvil parent | retest-v1, 2026-10-04, `sts_pa_catalyst_retest_2026-10-04` | o1-v1, 2026-10-07, `sts_pa_catalyst_o1_2026-10-07` |
| Wall / CPU-SU ceiling | 16 h / 2,048 SU | **8 h / 1,024 SU** |

### Why these tolerances

Each tolerance sits inside the window between measured SCF noise at conv_thr 1e−6 and the scale of every restart defect that would change a result. Sources: the [fixed-geometry diagnostic readout](pa-fixed-geometry-diagnostic-readout-2026-10-06.md) and the 21075231 control.

| Quantity | Measured noise (no defect) | O1 tolerance | Defect scale |
|---|---|---|---|
| Force | 6.6e−5 to 1.8e−4 Ry/bohr between any two SCF paths at one geometry; 6.7e−5 for an exact restart replay | 5e−4 Ry/bohr (¼ of forc_conv_thr 2e−3) | A lost or reset BFGS history changes the next step by a large fraction of a 1.9–2.2e−2 bohr step; the other electronic basin is 94.7 meV away |
| Position (next step) | 1.06e−4 bohr (B vs control); 6.8e−5 (21075231 resumed) | 1e−3 bohr (5% of a BFGS step) | as above |
| Energy | ≤ 1.9e−7 Ry at one geometry; 2.5e−6 (B) and 5.0e−6 Ry (21075231 resumed) at the next step | 3e−5 Ry (0.41 meV; 1/25 of δ = 10 meV) | 17–25 meV per BFGS step; 94.7 meV basin |

Why the carry-over check is needed: QE tightens conv_thr as a relaxation proceeds. A resumed deck that starts at 1e−6 while the continuous run has already tightened would compare different precisions. At this boundary (after evaluation 1), 21075231's candidate printed `new conv_thr = 1.0e−6`, equal to the resumed deck, so the check passes there. It is registered so that the rule is recorded and enforced.

## Registered readings

The reading comes from the controller's own `trial_receipt.json`, applied by `src/dft/pa_catalyst_o1_readout.py`:

| Reading | Conditions |
|---|---|
| **CONTINUITY_PASS** | The pre-resume decision is RESUME_CANDIDATE. Every compared evaluation (control 1–3 vs candidate 1 + resumed 2–3) is within the O1 tolerances. The conv_thr carry-over is equal. The negative control behaves as registered in the re-test: startup history deletion and optimizer count 0, so the controller status is PASS_ONE_BOUNDARY |
| **CONTINUITY_FAIL** | The carry-over is equal and any compared value is outside an O1 tolerance |
| **INCONCLUSIVE** | Any of: a call failed or was refused; a failure marker, including the unchanged `IEEE_(INVALID\|OVERFLOW\|DIVIDE_BY_ZERO)_FLAG` rule; the carry-over is unavailable or unequal; the pre-resume decision is HOLD or a reseed (continuity is not tested on those branches); any other controller error |

Hubbard-trace and magnetization deltas are reported informatively, never in the reading. They come from re-reading the same ordered evaluations with the fixed-geometry parser. A relaxation's stdout prints magnetization to 0.01.

**Interpretation limits.**
- CONTINUITY_PASS certifies one stop/resume boundary at the registered geometry: no restart defect larger than the O1 tolerances.
- It licenses only a separately costed production relaxation, as before. References, adsorption and an uncertainty-aware ranking still precede the melt.
- It does not certify every-step P-A or terminal fresh acceptance.
- The historical 21075231 data re-read through this readout give INCONCLUSIVE: no carry record, and the tolerances of that time. Their numbers do lie inside the O1 tolerances (`results/pa_catalyst_o1_2026-10-07/historical_reread_21075231.json`, labelled historical). That is not a result, and the run must stand on its own.

## Budget

| Item | Value |
|---|---|
| Estimate | 350–550 CPU SU |
| Estimate basis | 21075231 measured 353.92 SU for control, candidate, fresh and resumed (9,954 s); the negative control adds three evaluations from the copied checkpoint, about 100 SU |
| Ceiling | **1,024 SU** (8:00:00 × 128 cores) |
| Balance before launch | 35,845.1 SU (`mybalance`, 2026-10-07). The reproducibility probe (job 21157910, ceiling 576 SU) may run concurrently |

The controller launches a call only with at least 7,320 s of allocation left, so an 8-hour limit admits the registered calls with margin: about 2.8 h measured before the negative control.

## Risks

- **IEEE_INVALID exit note.** It appeared in 1 of 11 recent runs (A_replay) and fails a call under the unchanged failure rule. That would make the run INCONCLUSIVE at partial cost.
- **Thin margins.** The tolerances rest on few samples: n = 5 paths at evaluation 2, and n = 2 at the next step. The energy tolerance was raised before launch from the options memo's 1e−5 to 3e−5 Ry. The memo's "4×" margin was computed against B's 2.5e−6 Ry. 21075231's own evaluation-3 difference, 5.0e−6 Ry, left only 2×, enough for ordinary SCF scatter to fail a defect-free restart. 3e−5 Ry gives 6× over that measured difference. It stays at least 3× below the smallest defect signature considered (a fraction of a 17–25 meV BFGS step, ≥ 1e−4 Ry) and at 1/25 of δ.
- **Defects below the tolerances.** A defect smaller than the tolerances passes; at that size it would not change an adsorption energy.

## Execution and stop rules

1. **Stage.** Copy the exact pinned bytes of a pushed commit to `/anvil/projects/x-che260157/sts_pa_catalyst_o1_2026-10-07`, read-only: the sibling controller and adapter, the unchanged contract, the Slurm script `anvil/93_pa_catalyst_o1.slurm`, the source deck, the source review, the spec and the 12 real-control replay fixtures.
2. **Preflight.** Run the controller's own `--preflight` on Anvil: every pin plus the zero-SU replay of the real control call, then `mybalance`, a queue check (only the probe allowed) and the remote spec sha.
3. **Submit and release.** One `sbatch --hold --no-requeue`, held-shape validation, one release. No array, dependency, retry or requeue.
4. **Afterwards.** One-shot read-only status, terminal accounting with NodeList, a small-file mirror, and the registered readout.

Spec: `results/pa_catalyst_o1_2026-10-07/launch_spec.json`. Tests: `tests/test_pa_catalyst_o1.py`.

## Pre-launch review

An independent review found no blocker. Its fixes are folded in:

- the controller's pinned docstring states the registered 3e−5 Ry energy tolerance;
- staging reads and verifies every committed blob, and checks every target is absent, before it writes anything on Anvil;
- validation and release require exactly one submitted job;
- the readout returns a verdict only from a receipt dated 2026-10-07 whose continuity record carries the registered O1 tolerances, and a PASS also requires a validated negative-control call.

The energy tolerance was raised from 1e−5 to 3e−5 Ry before launch (see "Thin margins").
