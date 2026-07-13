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

## 5. Slab + adsorbate workflow (built, validated, **first run in progress**)

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

The ordered CrO₂ endmember uses a **1×1 supercell → 18-atom CrO₂(110) slab** (nat=18; identical physics to
a 2×2 but ~3.6× cheaper — the 2×2/72-atom cell is only needed for HEA disorder, not ordered endmembers).
The best-guess **H pseudo `H.pbe-rrkjus_psl.1.0.0.UPF` works** (gas H₂ converged) — open item resolved.

### Run lessons (CrO₂, 2026-06-27/28)

- **`nosym` doubles the k-points for a high-symmetry clean slab.** The symmetric clean slab aborts in
  `checkallsym` during relaxation (fixing the bottom half breaks the top↔bottom mirror), so it needs
  `nosym=.true. noinv=.true.`. But that also discards the *in-plane* symmetry the adslabs keep → the clean
  slab went to **36 irreducible k-points vs 15** for the adslabs. The clean slab is therefore the most
  expensive job, not the cheapest. → **always run it alone with the full core count**, never starved
  alongside an adslab (8 starved ranks gave ~22 min/SCF-iter and the magnetic SCF sloshed badly).
- **Add `mixing_mode='local-TF'` for slabs.** The magnetic-metal clean-slab SCF charge-sloshed (accuracy
  bounced 0.13→25 Ry early). `local-TF` is the standard cure for long-wavelength slab sloshing — now baked
  into `write_slab_input` in `qe_slab.py` (helps every future slab/SQS).
- Adslabs relax fine **without** `nosym` (the adsorbate lowers symmetry naturally): `s0_OH` 6 ionic steps,
  `s0_O` 27 steps, both `JOB DONE`. Per-adslab relax ≈ 1.5–2 h on this box.

## 6. Status (CrO₂ parity point — paused for box switch)

> **⚠ RETRACTED (2026-07-05, see §10 + [docs/26](26-endmember-parity-checkpoint.md) §4):** the
> `s0_OH`/`s0_OOH` energies below and the η = 2.03 V derived from them came from silently
> unconverged relaxations (`JOB DONE` with SCF failures; final forces 17–66× threshold). The
> corrected, converged CrO₂ value is **η = 1.726 V**.

Endmember **CrO₂(110)**, run dir `runs/Cr_slab/` (snapshot pulled local; box `/workspace/Cr_slab_snapshot.tgz`).
**4 of 6 energies done and saved locally**, 2 deferred to a cheaper CPU box:

| job | state | total energy (Ry) |
|---|---|---|
| H₂ (gas) | ✓ JOB DONE | −2.33323818 |
| H₂O (gas) | ✓ JOB DONE | −44.04119711 |
| `s0_OH` adslab | ✓ JOB DONE (6 ionic) | −1594.87205599 |
| `s0_O` adslab | ✓ JOB DONE (27 ionic) | −1593.59436879 |
| `s0_OOH` adslab | ✗ stopped at ionic 7 (scf 2.5e-4) | re-run on cheap box |
| clean `slab` | ✗ not started | re-run on cheap box |

η needs all six → **cannot compute yet**; finish `s0_OOH` + `slab` on the next box, then `eta` (§7c).
The 2×5090 box was wound down (idle GPU billing wasteful for CPU DFT); jobs stopped, box idle.

- **QE tier stood up + validated** (CrO₂ SCF, mag 4.00 μB). ✓
- **Convergence: DONE** → locked **80 Ry / 640 Ry / 6×6×8**. ✓
- **Slab+adsorbate workflow: BUILT + 4/6 of the first parity point computed.** ◑
- **Next:** finish CrO₂ (`s0_OOH`+`slab`) → first DFT η; then MO₂ endmembers (Mn/Fe/Co/Ni/Cu) + SQS of the
  top 3–5 HEAs; run UMA on the *same* structures → the UMA↔DFT parity plot ([docs/22](22-multifidelity-dft-calibration.md) §6).

## 8. Endmember parity run — RTX 5090 box, the 30.7-vCPU cap lesson (2026-06-30)

Resumed the 5 remaining MO₂ endmembers (Mn/Fe/Co/Ni/Cu) on a **new Vast.ai box** (`192.3.91.246`,
RTX 5090, **shared with OptiGrain** — its FastAPI backend lives here too, never touched). Goal: the
4 DFT jobs/endmember (`s0_O`/`s0_OH`/`s0_OOH` + clean `slab`), reusing CrO₂'s metal-independent gas
refs (H₂/H₂O copied in → 4 jobs not 6). 20 jobs total → the 5 DFT η's that complete the 6-point
UMA↔DFT parity (UMA η already computed for all 6: Cr 1.15 / Fe 1.10 / Mn 2.35 / Ni 2.38 / Co 2.39
/ Cu 2.42).

**The trap — `nproc` lies on a capped container.** First launch ran all 5 endmembers in parallel,
5×48 = **240 `pw.x` ranks**. `nproc` reports **256**, `cpuset` allows `0-255` — but the container's
cgroup-v2 `cpu.max` is **`3071999 100000` → a hard CFS quota of 30.72 vCPUs**. So:

| layout | ranks | useful CPU | s / SCF-iter |
|---|---|---|---|
| parallel-5 | 240 | ~30 cores (8× oversubscribed → thrash) | **~525** |
| queue, 4×24 | 96 | ~30 cores (3× oversubscribed) | ~100 |
| **queue, 2×12** | **24** | **~24 cores @ 99% eff** | **~40** |

Past the ~30-core quota, extra ranks don't compute — they thrash (context-switch + MPI spin-wait),
and useful work stays pinned at ~30 cores regardless. **~12× speedup just from right-sizing ranks to
the real (cgroup) core budget, not the advertised `nproc`.** Always read
`/sys/fs/cgroup/cpu.max` (and `vast-capabilities`) before sizing MPI on a rented container; this also
explains why CrO₂ ran fine at NP=24 single-job (it happened to match the cap).

**Driver:** `src/dft/queue_dft.sh M-list, NP, NCONC` — a throttled queue (each job clears its own
`./tmp`, runs `pw.x` at NP ranks, ≤ NCONC concurrent, logs `DONE M/job … <wall>s` + `QUEUE_ALL_DONE`
to `/workspace/queue_dft.log`). Launched as `bash queue_dft.sh 12 2` (24 ranks, under the 30.7 cap,
proven nk=4/6 divisibility); measured **~40 s/SCF-iter at 99% core efficiency** (vs ~525 at 240 ranks).

**Parity tooling:** `src/dft/parity_plot.py` reads `runs/<M>_slab/{uma,dft}_eta.json`, pairs single-site
η, reports Spearman ρ + Pearson r + MAE, draws `docs/figs/uma_dft_parity.png`. Dry-run OK (1/6 paired:
CrO₂ DFT 2.03 vs UMA 1.15); the 5 endmember DFT η's are the only missing inputs.

**Relocated for cost (2026-07-01).** The queue validated healthy on the 5090 box, but that box is an
**RTX 5090 running CPU-only DFT → the GPU bills idle** (same waste flagged in [[feedback_vast_workflow]]).
Since OptiGrain didn't need the box overnight, the run was **stopped and is being moved to a cheap
CPU-only box** — inputs, the 7 pseudopotentials, and CrO₂'s gas refs are all pulled local (the 5090 can
be destroyed). Redeploy recipe: `src/dft/setup_newbox.sh` (micromamba QE 7.5 → pseudos →
`runs/<M>_slab/*.in`) then `queue_dft.sh <metals> <NP> <NCONC>` sized to the new box's `cpu.max`.
Wall-time unchanged (~1–1.5 days; a 16–32-core CPU box ≈ the 5090's capped 30 cores) — the win is cost.

## 9. Status & next steps (2026-07-01)

**Done:** CrO₂ parity anchor (η_DFT 2.03 vs η_UMA 1.15 — **value later retracted as unconverged, see §10**);
UMA η for all 6 endmembers (Fe 1.10 & Cr 1.15 best; Mn/Ni/Co/Cu 2.35–2.42); the throttled-queue +
parity tooling, both validated; the `nproc`-vs-cgroup-cap lesson recorded.

**Blocking the deliverable:** the 5 endmember **DFT** η's (Mn/Fe/Co/Ni/Cu). Awaiting a cheap CPU box.

**Next steps (in order):**
1. On the new CPU box: `setup_newbox.sh`, check `cat /sys/fs/cgroup/cpu.max`, launch `queue_dft.sh`
   sized to the real cap (~24 ranks). ~1–1.5 days for the 20 jobs.
2. Pull the 20 `.out` back; copy CrO₂'s `H2.out`/`H2O.out` into each `runs/<M>_slab/`; run
   `qe_slab.py eta --outdir runs/<M>_slab` ×5 → 5 `dft_eta.json`.
3. `python src/dft/parity_plot.py runs` → **the 6-point UMA↔DFT parity** (Spearman ρ + Pearson r + MAE
   + `docs/figs/uma_dft_parity.png`) — the keystone calibration deliverable.
4. Interpret: does UMA *rank* the endmembers like DFT+U (ρ), even though it over-binds absolutely? That
   decides whether UMA's screen is trustworthy for the melt down-select, or needs a DFT re-rank.
5. Housekeeping: revoke the HF token (frankcai222, still live); tear down boxes; merge to main.

## 10. Campaign complete (2026-07-13) — log closed

The endmember run finished 2026-07-13 after a 12-day, 5-attempt-deep convergence
campaign across two CPU boxes. **Full story, final numbers, retraction record, and
exclusion protocol: [docs/26 — Endmember Parity Checkpoint](26-endmember-parity-checkpoint.md).**
Headline: converged DFT η **Mn 0.892 < Fe 1.263 < Cr 1.726 ≈ Ni 1.751 V** (Co/Cu
excluded, spin/charge multistability); 4-point parity vs UMA Spearman ρ = 0.40
(p = 0.6), MAE = 0.71 eV → **UMA cannot rank rutile-oxide OER**. Figure:
`docs/figs/uma_dft_parity.png`. This log is closed; the catalysis project is
parked per [docs/24](24-thermal-pivot-execution-plan.md) §9.

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

# (b) slab + adsorbate, fresh start on a new box (needs ase+pymatgen+repo):
pip install ase pymatgen          # into the QE env or a venv
NP=<cores> NK=4 NSITES=1 REPO=$PWD bash src/dft/run_slab_dft.sh Cr   # endmember CrO2(110)
# -> writes runs/Cr_slab/dft_eta.json (eta_min/mean/std/max), comparable to the UMA site_records

# (c) RESUME the paused CrO2 point (4/6 already done) on the cheaper box:
#   1. restore the snapshot into the run dir (skip the giant tmp/ — QE regenerates it):
scp runs/Cr_slab_snapshot.tgz  newbox:/workspace/qe/runs/   # or re-pull from old box first
ssh newbox 'cd /workspace/qe/runs && mkdir -p Cr_slab && tar -xzf Cr_slab_snapshot.tgz -C Cr_slab'
#   2. the loop SKIPS the 4 JOB-DONE outputs and runs only s0_OOH + slab. IMPORTANT: run the
#      clean slab ALONE on all cores (it has 36 k-pts, see §5) — do the two sequentially, full -np:
ssh newbox 'cd /workspace/qe/runs/Cr_slab; export PATH=<qe-env>/bin:$PATH LD_LIBRARY_PATH=<qe-env>/lib:$LD_LIBRARY_PATH; OMP_NUM_THREADS=1 \
  mpirun --allow-run-as-root -np <cores> pw.x -nk 4 -in s0_OOH.in > s0_OOH.out 2>&1; \
  OMP_NUM_THREADS=1 mpirun --allow-run-as-root -np <cores> pw.x -nk 8 -in slab.in > slab.out 2>&1'
#   3. pull s0_OOH.out + slab.out back into local runs/Cr_slab/, then compute eta LOCALLY:
PYTHONPATH=src python src/dft/qe_slab.py eta --outdir runs/Cr_slab   # -> runs/Cr_slab/dft_eta.json
```
