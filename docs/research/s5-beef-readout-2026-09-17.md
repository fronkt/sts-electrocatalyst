# S5 BEEF-vdW readout — 2026-09-17

The approved base S5 experiment is complete: all fourteen outputs passed QC, all three metals are scoreable, and all three sample standard deviations of member-wise overpotential are below 0.25 V. P-BEEF is **CONFIRMED under Ladder B: 3/3 below 0.25 V; 0/3 at or above 0.30 V**. This is an XC ensemble result at fixed geometry for non-magnetic Ru/Ir/Ti, not a calibrated prediction error or an uncertainty bound for the HEA screen.

## Results

Each metal uses 2,000 common coefficient rows across its bare slab, OH, O, OOH, H2 and H2O. The sample standard deviation uses ddof=1 after taking the CHE maximum separately for every member. The nominal column is the unperturbed self-consistent BEEF-vdW energy result; the ensemble mean is a separate statistic.

| Metal | Nominal eta, V | Ensemble mean eta, V | sigma(eta), V | Below 0.25 V | Member limiting steps 1 / 2 / 3 / 4 |
|---|---:|---:|---:|---|---|
| Ru | 0.890653 | 0.918913 | 0.167314 | Yes | 0 / 0 / 1805 / 195 |
| Ir | 0.671082 | 0.725665 | 0.199404 | Yes | 0 / 0 / 473 / 1527 |
| Ti | 1.269756 | 1.267405 | 0.090813 | Yes | 1 / 1999 / 0 / 0 |

Ru is limited by step 3 in 90.25% of members and step 4 in 9.75%. Ir switches between step 3 (23.65%) and step 4 (76.35%); its nominal step is 4. Ti remains step-2-limited in 1,999/2,000 members, with one step-1 member. These branch switches are why the estimator takes the maximum within each member instead of fixing the nominal limiting step. The 2,000 functional draws are not 2,000 independent calculations or material samples.

The nominal CHE steps (eV) are:

| Metal | Step 1 | Step 2 | Step 3 | Step 4 |
|---|---:|---:|---:|---:|
| Ru | 0.465983 | 0.977897 | 2.120653 | 1.355467 |
| Ir | 0.071789 | 1.331660 | 1.615469 | 1.901082 |
| Ti | 1.521947 | 2.499756 | 0.787730 | 0.110566 |

## Scientific scope and comparison

The result meets the frozen numerical confirmation criterion. It does not show that XC uncertainty is negligible: the measured spread is about 0.091–0.199 V, covers only the specified endmember surfaces and geometries, and does not calibrate error against experiment or higher-level electronic structure.

The approved same-metal comparison is descriptive. Recomputed from `docs/figs/a0main_readout.json`:

| Metal | sigma_BEEF(eta), V | Absolute eta change U=0 to U=9, V | Grid max-minus-min, V | U points |
|---|---:|---:|---:|---:|
| Ru | 0.167314 | 0.496847 | 0.496847 | 8 |
| Ir | 0.199404 | 0.026593 | 0.197865 | 8 |
| Ti | 0.090813 | 0.245885 | 0.245885 | 7 |

The BEEF sigma is smaller than the U endpoint change for Ru and Ti; for Ir it is larger than the endpoint change and approximately the grid span. A standard deviation over functional draws and a finite change over a chosen U interval are different quantities. Further, the banked A0-main U grid deliberately uses the historical **1x1 cell**, whereas S5 uses **2x1v half coverage** at its fixed PBE geometries; the historical Ir 1x1 chain also retains its known mirror-saddle conditionality. These comparisons do not isolate or rank physical error sources at a common geometry and coverage. No Cr result enters the three-metal denominator.

## Execution and QC

The H2, H2O and Ru bare-slab preflight passed before the eleven-task production continuation (array 20782479). All fourteen SCFs completed with one finite final SCF energy, convergence evidence, JOB DONE, a complete finite 2,000-value QE emission block and 32 ordered finite XC contributions. There were no excluded metals, failed shared gases or substituted outputs. Known UNDERFLOW/DENORMAL notices are retained; the parser rejects severe or unknown IEEE flags, routine errors, truncated blocks and missing convergence.

The frozen inputs prescribe fresh self-consistent BEEF-vdW densities, nspin=1 and U=0, followed by ensemble evaluation. Ru/Ir/Ti use the existing mir adsorbate geometries and bare references; the 36-atom 2x1v slab has one adsorbate, so no factor of two is applied to adsorption energies. H2/H2O use their own fixed-geometry BEEF calculations in the approximately 12 Å Martyna–Tuckerman isolated box. PBE-generated pseudopotentials are used with the explicit input_dft override. BEEF-driven structural relaxation, symmetry-arm dependence, finite-temperature structural sampling and pseudopotential consistency are not measured by this sigma.

The sum of recorded SCF process wall times is 4,510.107 seconds. At 128 allocated ranks this corresponds to 160.359 allocated core-hours during those processes; this is neither measured CPU utilization nor the final scheduler-billed total, which includes job setup/teardown. SCF iteration counts span 6–38.

## Reproduction and independent verification

The operating decision is `docs/research/research-decisions-2026-09-16.md`; the unchanged estimator is `src/dft/p_beef_readout.py`, SHA-256 `0351f0b1fb4058caf7c644910e2560f5fdd0d4fa06d25199f72fddaf796a1962`. Run from the repository with Python 3.12.10, ASE 3.28.0 and NumPy 2.3.5:

```text
python src/dft/p_beef_readout.py --base runs/s5 --output <new-readout.json>
python -m pytest -q tests/test_p_beef_readout.py
```

The output path must be new: the script refuses to overwrite a prior readout. The focused suite passed **37 tests**. Raw `.out` and corresponding `.qc.json` files remain under `runs/s5/{Ru,Ir,Ti,gas}`. Their source/runtime/output hashes match the frozen launch and completion records. All fourteen input hashes and the estimator hash independently match `results/research_launch_2026-09-16/launch_spec.json`.

Primary results are `results/s5_beef_2026-09-17/readout.json`. The same directory contains `environment.json`, `tests.txt`, the exact 2000-by-32 coefficient matrix `coefficients.f64` (float64 little-endian, row-major), and `independent_review.json`. Matrix SHA-256 is `d82844d77fa371acd84c9164209f3a2ee9c8ba1f3e09c93393b7ce54e77b1012`; it matches the matrix fingerprint in the primary readout. ASE generator and covariance-source hashes are also recorded there.

An independent JavaScript read of all fourteen raw outputs applied that saved matrix using scalar dot products, reconstructed CHE steps directly, took each member maximum and used Welford sample variance. All 6,000 member overpotentials agree with the production estimator within 1.49e-11 V, all three limiting-step histograms agree exactly, and sigma differences are below 1.31e-13 V. The input/output/runtime hash checks passed for all fourteen jobs. No scientific admission threshold or denominator changed.

QE emits the 32 basis terms in its Ry energy convention; these and the SCF total are converted using the campaign factor 13.605693122 eV/Ry. The actual QE/libbeef basis and the ASE coefficient convention were checked: the final correlation coefficient is the negative of the preceding one, and the ensemble is a 32-term dot product. ASE returns the SCF total plus the perturbation, so the baseline is included exactly once. QE's separate 2,000-number block supplies only emission/count/finiteness QC for this preselected estimator. See the primary implementations in [QE 7.5 beef.f90](https://raw.githubusercontent.com/QEF/q-e/qe-7.5/PW/src/beef.f90), [libbeef beefun.c](https://raw.githubusercontent.com/vossjo/libbeef/master/src/beefun.c) and the recorded installed `ase/dft/bee.py`.
