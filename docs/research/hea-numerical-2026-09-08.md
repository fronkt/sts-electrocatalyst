# Paired SCF refinement and bounded ortho recovery — 2026-09-08

This stage separates numerical refinement of four accepted electronic states from two attempts to recover unconverged states. It follows the [completed spin/projector panel](hea-followup-2026-09-07.md) and its [full readout](../../results/hea_followup_2026-09-07/completion_readout.json). The geometry is the retained seed-0 leader endpoint pair; it is not the historical seed-1 winning chain.

## Existing source states

The four fragment-start SCFs all have accepted energy/force records and complete 75-atom projections. Values below are from their banked `.out` and `.qc.json` files in [the controls directory](../../runs/hea/controls_2026-09-07/). They are baseline observations, not results of the new calculations.

| Endpoint / projector | SCF iterations | E (eV) | Max free force (eV/Å) | Total / absolute magnetization (μB/cell) | Fragment moment (μB) |
|---|---:|---:|---:|---:|---:|
| Builder / atomic | 44 | -108250.559308 | 1.44339 | 36.00 / 64.09 | HO₂ -1.0422 |
| Pull 2.10 / atomic | 43 | -108252.609348 | 1.41197 | 40.00 / 65.98 | O₂ +2.0314 |
| Builder / ortho | 57 | -108253.983496 | 1.45152 | 38.10 / 65.31 | HO₂ +1.0479 |
| Pull 2.10 / ortho | 40 | -108256.113254 | 1.41244 | 40.00 / 67.03 | O₂ +2.0240 |

Atom indices here are zero-based: appended O atoms are 72 and 73, and H is 74. Builder HO₂ moments include all three. In the pulled endpoint H has transferred to slab O56, so its small moment (+0.0050 atomic; +0.0051 ortho) is reported separately from O₂. These are Löwdin population moments, not exact spin quantum numbers. Forces on all coordinates peak at 2.99229, 2.98462, 2.91929 and 2.89738 eV/Å in table order; 28 atoms are fully fixed and 47 are free.

Each final Hubbard record contains all 23 Hubbard atoms (QE indices 1–23) and 46 spin-resolved occupation matrices. The reported sums of occupied Hubbard levels are 146.1271, 145.9404, 133.4059 and 133.3628 in table order. Retain the individual matrices and eigenvalues for state comparisons. These projector-dependent populations are neither oxidation states nor a common charge scale across the two projector definitions.

For the matched fragment-start pairs, ΔE = E(pull) − E(builder) is **-2.050039444 eV (atomic)** and **-2.129758057 eV (ortho)**. The difference between these gaps is -0.079718613 eV. Absolute energies from different Hubbard projector Hamiltonians must not be subtracted to rank those Hamiltonians. Even the gap comparison includes different converged magnetic states, so it is sampled model/state sensitivity, not a pure projector-error estimate.

The ortho fragment-start builder is **0.422816098 eV lower** than the ortho baseline builder, whose HO₂ moment was -0.0041 μB; the fragment start instead gives +1.0479 μB. Thus HO₂ spin quenching is not unavoidable with ortho projectors. This is evidence of initialization-dependent electronic basins, without a magnetic-ground-state claim. Likewise, the atomic fragment builder is only 0.000293747 eV below its atomic pilot baseline, but its HO₂ moment flips from +1.0430 to -1.0422 μB and total magnetization changes from 38.09 to 36.00 μB. Energy proximity alone does not establish the same state.

## Six-job first stage

The [plan](../../results/hea_numerical_2026-09-08/plan.json), [launch specification](../../results/hea_numerical_2026-09-08/launch_spec.json) and [source checkpoint inventory](../../results/hea_numerical_2026-09-08/source_checkpoints.json) define the exact lineage and file hashes. The four refinements precede the two recovery attempts in the manifest.

| New job | Source state | Electronic setting | Wavefunction initialization |
|---|---|---|---|
| `hn__leader_builder__atomic__tight` | `hc__leader_builder__atomic__fragment` | `conv_thr=1e-8` | file |
| `hn__leader_pull2.10__atomic__tight` | `hc__leader_pull2.10__atomic__fragment` | `conv_thr=1e-8` | file |
| `hn__leader_builder__ortho__tight` | `hc__leader_builder__ortho__fragment` | `conv_thr=1e-8` | file |
| `hn__leader_pull2.10__ortho__tight` | `hc__leader_pull2.10__ortho__fragment` | `conv_thr=1e-8` | file |
| `hn__leader_pull2.10__ortho__recover_baseline` | `hc__leader_pull2.10__ortho__baseline` | `mixing_beta=0.1`, `conv_thr=1e-6` | atomic+random |
| `hn__leader_builder__ortho__recover_metal_alternating` | `hc__leader_builder__ortho__metal_alternating` | `mixing_beta=0.1`, `conv_thr=1e-6` | atomic+random |

All six explicitly use `restart_mode=from_scratch` and `startingpot=file`. Refinements keep source `mixing_beta=0.3`; recovery changes it from 0.3 to 0.1. Geometry, positional flags, species order, pseudopotentials, Hubbard U/projector, charge, collinear spin treatment, 80/640 Ry cutoffs, 4×2×1 mesh and MV smearing of 0.01 Ry remain fixed. Independent input comparison found the complete ATOMIC_SPECIES-through-HUBBARD card region byte-identical to each source, with changes confined to initialization, private outdir and the listed SCF setting. All six source/input hashes match the plan.

## Saved-state semantics and startup audit

Each attempt retains its **source QE prefix inside a fresh private outdir**. QE resolves the save directory using both fields; preserving the prefix avoids renaming internal state files. Make independent copies rather than links to the original state, and preserve the source checkpoint unchanged. [QE 7.5 path handling](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/Modules/io_files.f90).

The four accepted sources each have a complete `.save` directory, including 16 collected spin/k-point HDF5 wavefunction files. Their new SCFs initialize both density and wavefunctions from these copied states. This is a new SCF at a tighter target. QE reserves `restart_mode=restart` for continuing interrupted calculations, with compatible execution layout; it is not needed to seed a new SCF from a completed state. [QE input manual](https://www.quantum-espresso.org/Doc/INPUT_PW.html), [collected-wavefunction reader](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/pw_restart_new.f90).

The two failed sources retain `.save/charge-density.hdf5`, `data-file-schema.xml`, `paw.txt` and `occup.txt`, but lack the same complete collected-wavefunction set. Copy those four files and regenerate randomized atomic wavefunctions. Do not import their old distributed raw wavefunctions, mixing history or restart files. This is one **density/Hubbard warm-start recovery** per case, with changed mixing and fresh wavefunctions/history; it is not an exact interrupted continuation or a mixing-only experiment. The failed parent has no accepted final energy for a convergence delta.

With file density initialization, QE reads the saved spin density, Hubbard occupation matrices from `occup.txt`, and PAW state from `paw.txt`. Its reader disables replacement of those loaded Hubbard populations by starting occupation guesses. Use the same projector and species/atom ordering as the source. Keep `mixing_fixed_ns=0` at its default so occupations can evolve; do not add magnetization or occupation constraints. A warm start seeds a basin but cannot guarantee its preservation. [QE 7.5 saved-density reader](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/io_rho_xml.f90), [SCF driver](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/electrons.f90).

Check startup positively: both modes must report reading the initial density from file; refinements must report wavefunctions from file, and recovery must report randomized atomic wavefunctions. Missing density or wavefunctions can cause QE to fall back to atomic initialization instead of stopping. Reject such fallback for the intended lineage even if the resulting SCF converges. Preserve the starting Hubbard occupation block alongside its final block. [QE 7.5 potential initialization](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/potinit.f90), [wavefunction initialization](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/wfcinit.f90).

## Readout and subsequent decisions

For each accepted refinement report the endpoint energy change, all-coordinate and free-coordinate force-vector changes, total and absolute magnetization changes, per-atom/fragment Löwdin moments, and Hubbard occupation/eigenvalue changes against its exact parent. Compute the pair-gap change only after both endpoints are accepted. Label a changed electronic basin **BRANCH MISMATCH**; do not describe its energy difference as numerical error or identical-state agreement. Preserve raw outputs and projection/QC provenance.

The four accepted source forces remain about 1.41–1.45 eV/Å on free coordinates. SCF convergence and complete projections therefore do not establish geometric stationarity. The existing 0.05 eV/Å flag is a stationarity diagnostic, not calibrated numerical accuracy. This stage introduces no arbitrary accuracy pass threshold. Assess convergence against the energy/force scale needed for the intended comparison and the later tighter-setting sequence.

If the two recovery attempts converge, compare each with its appropriate accepted ortho partner while retaining its revised initialization lineage; do not silently fill the original factorial as if the first attempt succeeded. Numerical refinement of the already accepted fragment pairs can proceed independently of recovering those two missing starts. Neither branch proves exhaustive magnetic-state coverage.

The next ordered controls are paired cutoff and smearing changes, a joint tighter setting, then a denser commensurate k mesh after memory calibration and a decomposition baseline if pool layout changes. Smearing width and k sampling need joint assessment. Follow with fixed-cell DFT relaxation of the original constrained endpoints, tracking branch identity and force convergence. Only then extend to the actual seed-1 winning chain and the frozen eight-discovery/four-held-out validation chains. Current seed-0, fixed-geometry evidence cannot establish candidate ranking, catalytic overpotential, a kinetic pathway or a relaxed thermodynamic endpoint gap.

## Execution bounds and verification

The six jobs use NP128/nk8, concurrency one, four hours per task and no requeue. The allocation ceiling is 3072 core-hours. The corresponding parent attempts used 1361.671 core-hours in total; that is a historical comparator, not a forecast for these different initializations and tighter targets. The live preflight showed an empty user queue, 56068.9 CPU SU available and 4.7 TB free on the project filesystem.

All six checkpoint inventories are pinned by SHA256 (63,557,395,807 bytes total). Preparation copies regular files into a fresh private scratch directory and verifies the destination bytes before MPI. Full source and new scratch remain available on success or failure. The four-hour cap includes copying and projection; QE max_seconds=13200 reserves a nominal twenty minutes but does not guarantee all overhead fits.

Independent input/source checks passed for all six cases: local inputs and outputs match remote hashes; source XML agrees on atoms, cell, species, pseudopotentials, cutoffs, mesh and NP/nk; the only new input changes are those stated above. The four tight sources explicitly report collected wavefunctions, while both failed sources report uncollected wavefunctions. Launcher/QC tests and final held-resource verification follow below.

Verification before submission: 148 execution/QC/force tests passed with two Windows symlink skips; 27 numerical-readout tests passed; both shell syntax checks passed. Real source outputs reproduce six accepted source/partner records, both baseline fragment gaps and two explicitly unresolved source histories. Independent scientific and execution reviews passed. The runtime input now comes from an exact verified snapshot after checkpoint copying. Readout comparison allows up to four units in the last place only for derived force norms to account for observed Python/platform rounding; raw hashes, force components, energies and projected populations remain exact. No scientific accuracy threshold is implied.
