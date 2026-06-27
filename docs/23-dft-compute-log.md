# 23 — DFT compute log (Quantum ESPRESSO calibration tier)

Dated, reproducible record of the first-principles tier ([docs/22](22-multifidelity-dft-calibration.md)) —
the DFT analogue of [docs/14](14-compute-log.md). Entrant-run on rented Vast.ai compute, no VASP
license. Code: `src/dft/gen_rutile.py` (input generator) + `src/dft/run_convergence.sh` (sweep driver).

## 1. Environment

| Component | Value / note |
|---|---|
| Box | Vast.ai — AMD Ryzen Threadripper PRO 7975WX (**32C/64T**), 125 GB RAM, 2× RTX 5090 (idle; DFT is CPU) |
| OS | Ubuntu 24.04.4 LTS (unprivileged container) |
| **DFT engine** | **Quantum ESPRESSO `pw.x` v7.5** (conda-forge), MPI build (OpenMPI 5.0.10) + OpenMP, ELPA, HDF5 |
| Install | micromamba → `micromamba create -p /workspace/qe/env -c conda-forge qe` |
| Pseudopotentials | **SSSP Efficiency** via apt `quantum-espresso-data-sssp` → `/usr/share/espresso/pseudo` |
| Pseudos used | O `O.pbe-n-kjpaw_psl.0.1.UPF` (PAW); Cr `cr_pbe_v1.5.uspp.F.UPF` (GBRV USPP). (Mn/Co/Ni = GBRV USPP; Fe/Cu = PAW psl — for the other endmembers.) |
| Method | PBE + U (Dudarev), spin-polarized, MV smearing 0.01 Ry; U_eff Cr 3.7 eV (MP-calibrated) |

**Install lesson (→ [[feedback_vast_workflow]]):** the Ubuntu apt `quantum-espresso` **6.7** build
crashes at input-read with glibc `*** buffer overflow detected ***` (SIGABRT) on any input — a distro
hardening bug, unusable. **conda-forge QE 7.5** is the clean path. Two gotchas: `micromamba run` does
not wire PATH (use `export PATH=<env>/bin:$PATH; LD_LIBRARY_PATH=<env>/lib`); and **QE ≥7.1 replaced
`lda_plus_u`/`Hubbard_U(i)` with the `HUBBARD (atomic)` card** — the generator emits the new card.

## 2. System (convergence test)

**Rutile CrO₂** — a genuine ground-state rutile (P4₂/mnm) and one of the alloy metals, so it is a
faithful first endmember. Experimental geometry (a = 4.421 Å, c/a = 0.6596, O internal u = 0.3023),
held **fixed** (scf only) so energy differences are pure basis/k-point convergence. 6 atoms/cell
(2 Cr + 4 O). PBE+U(Cr 3.7), nspin = 2, starting magnetization 0.6/Cr.

## 3. Validation SCF (passed)

`pw.x` v7.5, ecutwfc 60 Ry / ecutrho 480 Ry, k 4×4×6, 8 MPI ranks (`-nk 2`):
- **JOB DONE**, exit 0; SCF converged; wall ≈ 3.6 min.
- **Total magnetization = 4.00 μB/cell** = 2.0 μB per Cr → correct physics for the Cr⁴⁺ (d²) FM
  half-metal. `force_hub` present in the timing report → the +U (HUBBARD card) is active.
- Confirms the engine + pseudos + HUBBARD card + CHE-ready setup all work end-to-end.

## 4. Convergence sweep

Driver: `src/dft/run_convergence.sh` (FORMULA=CrO2, NP=24, NK=4). ecutwfc swept 40→100 Ry at fixed
k 6×6×8 (dual 8); then k-grid swept at fixed ecutwfc 80 / ecutrho 640. Target: per-atom energy stable
to ≈1 meV (tight proxy for the <50 meV η target once slabs are run). Output:
`/workspace/qe/runs/CrO2_conv/convergence.csv`.

**Done 2026-06-27** — all 11 SCFs converged (`conv=1`); magnetization a steady **4.00 μB/cell**
throughout (robust). CSV: `results/cro2_dft_convergence.csv`.

**ecutwfc sweep** (k fixed 6×6×8, dual 8):

| ecutwfc (Ry) | ecutrho (Ry) | E/atom (eV) | ΔE/atom vs next (meV) |
|---|---|---|---|
| 40 | 320 | −1173.3656 | −24.7 |
| 50 | 400 | −1173.3903 | −5.0 |
| 60 | 480 | −1173.3953 | −6.1 |
| 70 | 560 | −1173.4014 | −3.0 |
| **80** | **640** | **−1173.4044** | **−0.4** |
| 90 | 720 | −1173.4048 | −0.4 |
| 100 | 800 | −1173.4052 | — |

**k-grid sweep** (ecutwfc 80 Ry, ecutrho 640 Ry):

| k-grid | E/atom (eV) | ΔE/atom vs next (meV) |
|---|---|---|
| 2×2×3 | −1173.3942 | −8.3 |
| 4×4×6 | −1173.4025 | −1.9 |
| **6×6×8** | **−1173.4044** | **+0.4** |
| 8×8×12 | −1173.4040 | — |

**Converged production setting (LOCKED):** **ecutwfc = 80 Ry, ecutrho = 640 Ry (dual 8), k = 6×6×8**
for the bulk rutile MO₂ cell — both knobs flat to **< 1 meV/atom** beyond this point (80→90 = 0.4 meV;
6×6×8→8×8×12 = 0.4 meV). For **slabs**, scale the in-plane k-grid down with the surface supercell and
use **1 k-point in the vacuum axis** (+ dipole correction); the cutoffs carry over unchanged. Heaviest
run (8×8×12) ≈ 9 min on 24 ranks; the converged 80/640/6×6×8 point ≈ 4 min.

## 5. Slab + adsorbate workflow (built, locally validated, ready to run)

The real parity work — `src/dft/qe_slab.py` (+ driver `src/dft/run_slab_dft.sh`). It **reuses the exact
UMA slab geometry and CHE referencing**, so only the relaxer differs (QE here vs the UMA MLIP there) →
a fair, method-vs-method parity:

- `build` reuses `hea_oer.surfaces_rutile` (`build_rutile110_hea`/`cus_site_xy`/`add_oer_adsorbate_at`)
  to emit QE `relax` inputs for the clean slab, the \*OH/\*O/\*OOH adslabs on each cus site, and the
  gas H₂O/H₂ refs (+ a manifest), at the locked **80 Ry / 640 Ry**, nspin=2 + PBE+U via the HUBBARD card,
  bottom half fixed (`if_pos 0 0 0`), k-grid auto-scaled for the surface cell, **no dipole correction
  (deliberately matching UMA).**
- `eta` parses the relaxed energies and calls the **same** `referencing.delta_G` + `descriptors.oer_overpotential`
  the UMA backend uses → a per-site η distribution (`eta_min/mean/std/max`) directly comparable to the UMA
  `site_records`.

**Validated locally (no QE needed):** `build Cr` emits a correct **72-atom CrO₂(110)** slab (identical to
the UMA cell) + adslabs + gas; `py_compile` clean; the writers/helpers unit-checked. **Not yet run** — the
relaxations (heavy: a magnetic +U slab relax each) wait for a **cheap high-core CPU box** (the 2×5090 box
was torn down — DFT is CPU-only, no reason to pay GPU rates).

**Open item:** the **H pseudopotential filename** (`H.pbe-rrkjus_psl.1.0.0.UPF`, best-guess) — the driver
checks every referenced UPF exists and aborts with a clear message if SSSP names H differently; fix
`ELEMENTS["H"]` in `qe_slab.py` if so. Next-box setup: conda-forge QE 7.x + `pip install ase pymatgen` +
the repo (`PYTHONPATH=$REPO/src`).

## 6. Status

- **QE tier stood up + validated** (CrO₂ SCF, mag 4.00 μB). ✓
- **Convergence: DONE** → locked **80 Ry / 640 Ry / 6×6×8**. ✓
- **Slab+adsorbate workflow: BUILT + locally validated**, ready to run on a CPU box. ✓
- **Next:** run `run_slab_dft.sh Cr` → first DFT η; then the other MO₂ endmembers (parity anchors) and the
  SQS approximants of the top 3–5 HEAs; run UMA on the *same* structures → the UMA↔DFT parity plot
  ([docs/22](22-multifidelity-dft-calibration.md) §6).

## 7. Reproduce

```bash
# on a CPU box with conda-forge QE 7.x + SSSP pseudos in /usr/share/espresso/pseudo:
export PATH=<qe-env>/bin:$PATH; export LD_LIBRARY_PATH=<qe-env>/lib:$LD_LIBRARY_PATH

# (a) bulk convergence (DONE):
python3 src/dft/gen_rutile.py CrO2 --ecutwfc 60 --ecutrho 480 --kpts 4 4 6 \
  --pseudo-dir /usr/share/espresso/pseudo \
  --m-upf cr_pbe_v1.5.uspp.F.UPF --o-upf O.pbe-n-kjpaw_psl.0.1.UPF -o cro2.in
mpirun --allow-run-as-root -np 8 pw.x -nk 2 -in cro2.in > cro2.out
FORMULA=CrO2 NP=24 NK=4 PSEUDO_DIR=/usr/share/espresso/pseudo \
  M_UPF=cr_pbe_v1.5.uspp.F.UPF O_UPF=O.pbe-n-kjpaw_psl.0.1.UPF \
  GEN=$PWD/src/dft/gen_rutile.py bash src/dft/run_convergence.sh

# (b) slab + adsorbate -> DFT eta (NEXT; needs ase+pymatgen+repo):
pip install ase pymatgen          # into the QE env or a venv
NP=24 NK=4 NSITES=1 REPO=$PWD bash src/dft/run_slab_dft.sh Cr   # endmember CrO2(110)
# -> writes runs/Cr_slab/dft_eta.json (eta_min/mean/std/max), comparable to the UMA site_records
```
