# Catalyst P-A — fixed-geometry initialization / force-convergence diagnostic, 2026-10-05

## Decision of record

Frank, 2026-10-05: "Continue the next steps of pricing a fixed geometry.... I approve the next DFT run." This licenses the diagnostic below at the stated hard ceiling. It does not amend job 21075231, which remains **INCONCLUSIVE**; it does not change any registered P-A tolerance; it licenses no production relaxation, ranking or melt release.

## Question

At the first resumed evaluation of job 21075231 (global evaluation 2), the resumed force differs from the continuous control by **1.1464e−4 Ry/bohr** (Co atom 20, z), 11.46× the 1e−5 gate, at positions equal to 1.45e−10 bohr. Which mechanism produces that difference, and what initialization / convergence policy would make every-step P-A continuity attainable?

Competing explanations, frozen before launch:

| | Explanation | Evidence before launch |
|---|---|---|
| E1 | The restart's first Davidson threshold (ethr 1e−5 vs continuous 1e−6) sends the SCF down a different path | Confirmed difference: setup.f90:423–437 defaults file-potential ethr to 1e−5; run_pwscf.f90:334 sets 1e−6 between ionic steps; input.f90:998 sets ethr = diago_thr_init |
| E2 | Forces at conv_thr = 1e−6 are not converged to 1e−5, so any change of SCF path moves them by more than the gate | QE's own "Total SCF correction" is 3.105e−3 (control) and 3.271e−3 (resumed) Ry/bohr at evaluation 2, 0.000321 / 0.000413 at evaluation 3 (residual 8e−8), 4.074e−3 at evaluation 1. The 1.15e−4 discrepancy is about 27× smaller than QE's own estimate of the residual force error |
| E3 | Other restart state differs (Hubbard occupations read from occup.txt at printed precision, zeroed eigenvalues, density reconstruction) | Starting Hubbard traces match at displayed precision only |
| E4 | The restart path is not run-to-run reproducible | Control and candidate evaluation 1 agree to 1.45e−10 Ry/bohr (continuous path reproducible); restart path untested |
| E5 | Warm and fresh starts reach different electronic states | Fresh vs warm at evaluation-1 geometry: 0.149 meV/cell, max force spread 8.82e−4 Ry/bohr (Co 23 z), both at about 1e−6 residual |

## Geometry and target

Cu8Cr23Mn35Co34 seed20/site2, 72-atom clean slab. **G2** is the first resumed evaluation geometry: the bohr ATOMIC_POSITIONS block of the trial's resumed deck, equal to the frozen candidate checkpoint's XML output positions to 7.1e−15 bohr and to the control's evaluation-2 positions to 1.45e−10 bohr. Every arm evaluates G2 (B also continues one BFGS step to evaluation 3).

## Arms

Three independent singleton jobs, one per group, run in parallel. Calls inside a group run sequentially; a failed call skips only the calls that start from its outdir.

| Group | Arm | Start | Change from its trial template | Stop | Tests |
|---|---|---|---|---|---|
| replay | **A_replay** | verified copy of the frozen candidate checkpoint (tree dc3637bc…, 390 files, 15.2 GB) | resumed deck, outdir only | after global evaluation 2 (EXIT boundary) | E4 |
| replay | **B_ethr** | fresh verified checkpoint copy | A + `diago_thr_init = 1.0d-6` | after global evaluation 3 | E1 (and E3 by residual) |
| ladder | **C1_warm_1e-6** | checkpoint copy | resumed deck as `scf` / `from_scratch`; conv_thr 1e−6 | end of SCF | restart-vs-SCF path equivalence |
| ladder | **C2_warm_1e-8** | verified copy of C1 outdir | conv_thr 1e−8, electron_maxstep 80, scf_must_converge .false. | end of SCF | E2 |
| ladder | **C3_warm_1e-10** | verified copy of C2 outdir | conv_thr 1e−10, electron_maxstep 75, scf_must_converge .false. | end of SCF | converged reference F* |
| fresh | **D1_fresh_1e-8** | atomic + random (trial fresh deck) at G2 | conv_thr 1e−8, electron_maxstep 80, scf_must_converge .false. | end of SCF | E5 |
| fresh | **D2_fresh_1e-10** | verified copy of D1 outdir | file start, conv_thr 1e−10, electron_maxstep 75, scf_must_converge .false. | end of SCF | E5 |

Every deck is the retained, raw-manifest-pinned trial deck with only the listed lines changed (`deck_receipt.json` records each changed line; tests rebuild and compare). Same pw.x/mpirun/UPF pins, 128 MPI ranks, `-nk 8 -ndiag 16`, one thread, `max_seconds = 7080`, identical to job 21075231.

Source facts used by the design (QE 7.5): `from_scratch` with an existing outdir calls `clean_tempdir` (input.f90:131–132), which deletes only `prefix.update/.md/.bfgs/.fire` ([qe-7.5 Modules/io_files.f90](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/Modules/io_files.f90)), so C1 reads the checkpoint's distributed `.wfc` buffers (wfcinit.f90:126–150; checkpoint XML has `wf_collected=false`). With `scf_must_converge = .false.`, QE sets `conv_elec = .TRUE.` at the last allowed iteration (electrons.f90:881) and prints "convergence has been achieved", so a capped rung is identified only by iterations = electron_maxstep and XML residual ≥ conv_thr. QE tests `max_seconds` only at the start of an SCF iteration (electrons.f90:606), so the iteration caps are sized for the measured ≈ 62–77 s per tight-threshold iteration plus start-up, the first file-start iteration and forces: a capped 75/80-iteration rung finishes with forces about 750–1,100 s before the 7,080 s soft stop, instead of losing its forces to the time limit.

## Registered readings

Comparisons use XML energies/forces converted to Ry and Ry/bohr, all 72×3 components in fixed order, the unchanged gate (1e−6 Ry, 1e−5 bohr, 1e−5 Ry/bohr) and the parser in `src/dft/pa_fixed_geometry_readout.py`. That parser reproduces all three banked trial comparisons and the warm/fresh spread exactly before launch.

- **R1 (E4)**: A vs resumed evaluation 2. Max |ΔF| ≤ 1e−8 and |ΔE| ≤ 1e−8 Ry → REPRODUCIBLE; passes the gate only → REPRODUCIBLE_AT_GATE_ONLY; otherwise NOT_REPRODUCIBLE.
- **R2 (E1)**: B vs control at evaluations 2 and 3; INCOMPLETE if B did not complete both evaluations. Evaluation-2 max |ΔF| ≤ 1e−8 and both evaluations pass the gate → ETHR_RESTORES_IDENTICAL_PATH; both pass the gate → ETHR_RESTORES_REGISTERED_CONTINUITY; otherwise ETHR_INSUFFICIENT. B vs A at evaluation 2 measures the ethr effect directly.
- **R3 (E2)**: F* = C3 forces; its precision bound is max |F_C3 − F_C2|. If the bound exceeds 5e−6 → UNRESOLVED_REFERENCE. A capped reference is reported as such (`reference_capped`). Otherwise, if the larger of max |F_control,eval2 − F*| and max |F_resumed,eval2 − F*| exceeds 1e−5 → CONV_THR_1e-6_BELOW_GATE_PRECISION (the registered gate is tighter than the force precision of the registered conv_thr). Otherwise → CONV_THR_1e-6_WITHIN_GATE_PRECISION. Each rung's distance to F* is reported; together with QE's SCF correction they give the conv_thr a 1e−5 gate requires.
- **R4**: C1 vs resumed evaluation 2. Max |ΔF| ≤ 1e−8 → SCF_PATH_EQUALS_RESTART_PATH; otherwise SCF_PATH_DIFFERS_FROM_RESTART_PATH (informative).
- **R5 (E5)**: D2 vs C3. Max |ΔF| ≤ 1e−5, max |ΔTr[ns]| ≤ 1e−3 per atom and spin, and |Δ total magnetization| ≤ 0.01 → SAME_ELECTRONIC_STATE; otherwise (including missing Hubbard traces or magnetization) DISTINCT_OR_UNRESOLVED_STATE, with the energy difference and both rungs' capped status reported.

Validity: a reading uses only arms that the controller recorded as COMPLETED and whose start is valid; a failed or unparseable arm is listed as excluded and never aborts the other readings. Every arm whose deck reads file state must print "Starting wfcs from file" / "The initial density is read from file" and no fallback message; a capped rung is reported with its achieved XML residual and never as converged.

Interpretation limits: a single geometry and target. R2 = identical path would show that ethr alone separates the two runs here, not that a longer protocol is accepted. R3 = below-gate precision would mean the gate must be paired with a tighter boundary conv_thr (or a tolerance set from measured SCF precision) as a prospective protocol change, reported as a new experiment.

## Budget

Allocation CHE260157 balance before launch: **36,421.4 CPU SU** (`mybalance`, 2026-10-05). Each call keeps run_arm's literal 7,200-second ceiling; a call launches only with ≥ 7,320 s of allocation remaining.

| Group | Slurm limit | Hard ceiling | Estimate |
|---|---:|---:|---:|
| replay | 4:30:00 | 576 SU | 130–170 SU |
| ladder | 6:45:00 | 864 SU | 270–370 SU |
| fresh | 4:20:00 | 555 SU | 245–445 SU |
| **Total** | | **1,995 SU** | **645–985 SU** |

Basis (job 21075231, measured): resumed evaluation 2 = 898.5 s CPU; the resumed call (evaluations 2 + 3) = 2,549 s wall; fresh SCF ≈ 65 s per iteration (50 iterations, 3,353 s); forces ≈ 63 s. Tight-rung iteration counts are extrapolated from the evaluation-3 residual tail (≈ 0.84 per iteration below 5e−7) and the fresh tail (≈ 0.77). Checkpoint copies (15.2 GB each, hashed while copying and re-hashed) add a few minutes per copy. The 1e−10 rungs may stall at a residual floor (earlier Cu8 relaxations stalled near 1.4e−7); they then cap at their electron_maxstep and report the achieved residual.

## Execution and stop rules

An independent pre-launch review found no blocker. Its fixes are folded in:

- iteration caps sized to the `max_seconds` check;
- a SIGTERM handler, so receipts are saved;
- no launch while any pw.x survives or after an incomplete teardown;
- solver-limit and per-call-cap flags checked;
- time fit checked before any copy;
- all pins (including the Slurm script) verified before the group directory is created;
- readout INCOMPLETE and exclusion rules.

Exact pinned bytes staged to `/anvil/projects/x-che260157/sts_pa_fixed_geometry_diag_2026-10-05`. Three `sbatch --hold --no-requeue` submissions (one per group, group time limits above), held-shape validation, one release each. No array, dependency, automatic retry or requeue. Remote frozen trial evidence is only read. Read-only watch until terminal; then terminal accounting, small-file mirror and the registered readout.

Spec: `results/pa_fixed_geometry_diag_2026-10-05/launch_spec.json`. Controller: `src/dft/pa_fixed_geometry_diag.py`. Decks: `runs/hea/pa_fixed_geometry_diag_2026-10-05/decks/`. Readout: `src/dft/pa_fixed_geometry_readout.py`. Tests: `tests/test_pa_fixed_geometry_diag.py`.
