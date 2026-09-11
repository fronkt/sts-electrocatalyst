# HEA continuation: thirteen calculations and census-gated next work

## Outcome and cost

The thirteen calculations released September 10 are terminal. Eight historical-winner single points pass the existing raw SCF/projection checks and exact runtime-input checks. Four capped solver probes remain nonconverged, and the separate smearing reproduction again reports `IEEE_INVALID_FLAG` on MPI rank 0. No rejected attempt has been promoted to an accepted endpoint. The numerical controls yielded diagnostic information, not five repaired scientific results.

| Array | Scope | Scientific outcome | Allocated core-h |
|---|---|---|---:|
| 20563386, tasks 1–8 | Historical winner, four states × two projectors | Eight accepted fixed-geometry audits | 687.893 |
| 20563390, tasks 1–4 | Precision/mixing recovery probes | Four capped nonconvergences | 456.391 |
| 20563376, task 1 | Fragment-derived smearing reproduction | Reproduced invalid flag; rejected | 75.093 |
| Total | 13 tasks | 8 accepted audits, 5 rejected diagnostics | 1,219.378 |

Costs use scheduler elapsed seconds × allocated CPUs / 3600, not active-CPU estimates. See [accounting](../../results/hea_continuation_2026-09-11/collection_verified/accounting.json) and [memory observations](../../results/hea_continuation_2026-09-11/collection_verified/memory.json). Peak batch RSS is roughly 120–130 million KiB, below the 237 GiB request; these failures are not recorded as out-of-memory events. The collected balance is 53,220.9 CPU core-hours remaining and 150 unused GPU units, not a request to spend either balance.

## Historical winner: a useful projector comparison, not a relaxed ranking

The [machine-readable readout](../../results/hea_continuation_2026-09-11/winner_readout.json) checks all eight raw SCF and projection outputs against stored QC, frozen inputs, exact runtime bytes, potential identities, and complete pairwise coordinates/cells/constraints. All eight SCFs converge in 36–40 iterations under the specified `1e-6` Ry criterion. Coordinates are the frozen historical Ni31Cr29Cu5Mn35 seed-1/site-0 chain, not the seed-0 transferred/desorbed diagnostic geometry.

Existing neutral, non-spin-polarized molecular H2/H2O references under `runs/Cr_slab` have matching H/O pseudopotentials, PBE and 80/640 Ry cutoffs. Their final energies are −2.3332381771 and −44.0411971100 Ry. All molecular SCFs and BFGS relaxation checks pass; maximum free forces are 0.004403 and 0.018517 eV/Å. The references are suitable for this electronic bookkeeping, but no new molecular cell-size or force-convergence study was performed. Both projector branches share the same references, so reference energies cancel in the reported branch differences.

| State | Atomic electronic adsorption energy (eV) | Ortho electronic adsorption energy (eV) | Ortho − atomic (eV) |
|---|---:|---:|---:|
| OH | 1.647769 | 1.695119 | +0.047351 |
| O | 3.249079 | 3.354156 | +0.105077 |
| OOH | 4.418320 | 4.451866 | +0.033547 |

These values use the existing H2/H2O reference convention without vibrational or entropy corrections. They are not adsorption free energies. Absolute slab energies under the two Hubbard projector definitions must not be mistaken for a preference between physical structures; the matched-chain adsorption differences are the relevant comparison here.

The unrelaxed maximum free-atom forces remain large: 1.562/1.530 eV/Å for slab, 1.660/1.588 for OH, 1.583/1.519 for O and 1.566/1.505 for OOH, atomic/ortho respectively. Total magnetizations are 37.32/37.57, 36.29/36.54, 35.35/35.61 and 36.30/36.56 μB. The readout retains atom-resolved force, charge, moment and Hubbard-occupation comparisons; these are diagnostics in the original coordinate/spin frame, not automatic magnetic-basin assignments. The electronic convergence does not imply DFT force convergence or validate MACE geometry, an overpotential, a cross-composition ordering, or the ground-state magnetic branch.

The projector sensitivity is material relative to the small historical descriptor separation, but it cannot be converted directly into a corrected separation between compositions: only one composition's chain was audited here, at fixed geometries. There is no justified new winner or final DFT ranking.

## Failure interpretation and the smallest next computation

The [convergence-probe readout](hea-convergence-probe-readout-2026-09-11.md) resolves the four capped histories. The tight initial diagonalization threshold becomes looser after iteration 1, so this was not a persistent tight-eigensolver test. Pull-state residual spikes correlate with global spin excursions, but late occupation trajectories are unavailable. Occupation instability remains a hypothesis, not a diagnosed code defect. The proposed one-hour, 128-core broader-smearing probe is documented with prospective stopping rules; it is **not submitted** in this phase. No unchanged long recovery is warranted.

The [rank-level smearing audit](../../results/hea_continuation_2026-09-11/smearing_verified.json) independently reconstructs the raw capture and verifies the clone receipt. The invalid flag recurs on rank 0. A single new setup-only diagnostic, [frozen here](../../results/hea_ieee_init_2026-09-11/launch_spec.json), changes only `nstep=200` to `0` and `max_seconds=13200` to `480`. It retains the accepted source checkpoint in an independent directory, uses the same pinned executable and 128-rank/eight-pool layout, and has one task, no retry, no projection and a ten-minute Slurm ceiling: **21.333 core-hours maximum**. Submission is held until resource, byte-identity and source checks pass.

The QE 7.5 `nstep=0` branch exits after setup/config-init, before `init_run`, SCF and forces. Thus it tests whether the invalid flag can already occur in this early setup/shutdown path. It does **not** prove density or wavefunction files were read successfully. Positive branch evidence requires this run's config-init output and XML exit status 255, complete rank streams, exact controls and absence of SCF activity. All outcomes are `DIAGNOSTIC_ONLY`; a clean result narrows the suspect interval but does not clear the original full-SCF failure. [QE 7.5 run_pwscf source](https://github.com/QEF/q-e/blob/qe-7.5/PW/src/run_pwscf.f90#L148-L159), [QE control reference](https://www.quantum-espresso.org/Doc/INPUT_PW.html).

## Census dependency

The [dated partial census interpretation](hea-census-partial-readout-2026-09-11.md) covers the completed CENSUS-1/2 arms and 40/54 extended CENSUS-3 blocks. At the 19:38 UTC snapshot, 89/103 manifests were terminal; all 14 outstanding manifests were CENSUS-3. The original readout remains unchanged. The intact-OOH historical winner fails the strict whole-chain integrity policy because its O state reconstructs. Model-dependent minimum-descriptor ranges exceed the historical leader/reference separation, and current extended sampling is unequal. These observations strengthen the need for full census interpretation before ranking-driven expenditure; they do not themselves choose a new candidate.

Continue the existing census runner and finish its frozen equal-depth, integrity-aware and rank-resolution readouts. Hold large candidate-focused DFT relaxations, ranking expansion and mechanistic campaigns until that decision. The energy-blind validation pilot remains a separate transferability experiment with unchanged composition/seed/site membership and held-out boundary. Completed CENSUS-1 supplies its coordinates; its prepared inputs do not authorize a blanket launch.

## Verification record

The [transfer receipt](../../results/hea_continuation_2026-09-11/collection_verified/transfers.json) records 221 source-hashed files, including all eight winner SCF/projection records, all four probe histories and all 128 smearing rank streams. An independent readout reproduces all adsorption shifts, energies and moments. The [final winner regressions](../../results/hea_continuation_2026-09-11/winner_tests_v3.json) pass 83 tests. The earlier Windows shell-fixture failure was a long temporary-path limit, not deleted checkpoint data; the unchanged shell tests pass under the shorter test directory. The independent census check verifies all 89 result hashes and preserves all five original readout hashes. Setup-diagnostic regression, staging, held-job and release receipts reside in `results/hea_ieee_init_2026-09-11/` as each step is verified.
