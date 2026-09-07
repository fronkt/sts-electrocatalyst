# HEA fixed-geometry SCF cost model

Extrapolation from banked np = 128 pw.x size descriptors to the nat 72-75 rutile(110) HEA cells.
Every input number is copied from the file cited beside it; every output is computed by
`src/dft/hea_cost_model.py`, which regenerates this file.

## 1. Inputs of record

| quantity | value | source |
|---|---|---|
| ranks per job | 128 | anvil/46_a0.slurm:46 |
| node memory | 237.0 GB | anvil/logs/a0_20419733_1.out:17 and a0_20419733_2.out:17 (`Memory Efficiency: 0.00% of 237.00 GB (1.85 GB/core)`) |
| shared-partition billing | max(cores, ceil(mem_GB/2)) SU/h | anvil/README.md:91 |
| ortho/atomic WALL ratio, planning | 1.2167 | the 2x1v OOH twin: runs/a0/pproj_cell/s0_OOH__2x1v_escape__u715_ortho.out WALL 473.78 s (:2530) / runs/a0/cell/s0_OOH__2x1v_escape__u715.out WALL 389.41 s (:2515) |
| ortho/atomic WALL ratio, 1x1 aggregate | 1.1834 | src/dft/build_pproj_cell.py:78 (four states aggregated; per-state table below) |
| ceiling factor | 3x planning | docs/43-prereg-week1-factorial.md:4453-4456 (q333 pair 317.4 core-h against ~55 planned, 5.8x) |
| planning SCF iterations | 42 | p90 of the banked local-TF / beta 0.3 nspin = 2 slab first-SCF survey (section 1b) |
| ceiling SCF iterations | 126 | 3x planning; the kill count of docs/92 section 7 |
| cutoffs | 80 / 640 Ry | runs/a0/cell/ref__2x1v__u715.in:15-16 |
| non-convergence precedent | Ru nspin = 2 ladder: 5,216.7 SU for 0 of 16 converged | docs/76-projector-generalization-decision-2026-09-03.md:214 |

Per-state ortho/atomic WALL ratios on the 1x1 cell (the aggregate 1.1834 is formed from these; the OOH state is the LOWEST of the four, the OH state the highest):

| state | atomic WALL (s) | ortho WALL (s) | ratio | sources |
|---|---|---|---|---|
| slab | 223.05 | 292.85 | 1.313 | runs/a0/p_proj/slab__u715_atomic.out:2332; runs/a0/p_proj/slab__u715_ortho.out:2376 |
| O | 722.24 | 782.18 | 1.083 | runs/s0/e_proj/s0_O__u715_atomic.out:1758 (np = 20); runs/s0/e_proj/s0_O__u715_ortho.out:1788 (np = 20) |
| OH | 185.39 | 298.33 | 1.609 | runs/a0/p_proj/s0_OH__u715_atomic.out:1846; runs/a0/p_proj/s0_OH__u715_ortho.out:2112 |
| OOH | 152.86 | 145.62 | 0.953 | runs/a0/p_proj/s0_OOH__u715_atomic.out:1851; runs/a0/p_proj/s0_OOH__u715_ortho.out:1880 |

UPF valences (electrons per atom), from the `atomic species   valence` table of a banked output:

| species | valence | source |
|---|---|---|
| Cr | 14 | runs/a0/cell/ref__2x1v__u715.out:114 |
| Mn | 15 | runs/Mn_slab/s0_OH.out:127 |
| Fe | 16 | runs/Fe_slab/s0_OOH.out:128 |
| Co | 17 | runs/Co_slab/s0_OH.out:126 |
| Ni | 18 | runs/Ni_slab/s0_OH.out:127 |
| Cu | 11 | runs/Cu_slab/s0_OH.out:121 |
| O | 6 | runs/a0/cell/ref__2x1v__u715.out:115 |
| H | 1 | runs/a0/p_proj/s0_OH__u715_atomic.out:125 |

Banked calibration SCFs (np = 128):

| SCF | nat | electrons | KS states | k-points | npool | V (bohr^3) | RAM/proc (MB) | RAM total (GB) | WALL (s) | iterations | lines |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ref__2x1v__u715 (atomic) | 36 | 312 | 187 | 16 | 8 | 6153.8249 | 303.54 | 32.33 | 522.67 | 22 | runs/a0/cell/ref__2x1v__u715.out (nat :51, nelec :53, nbnd :54, V :50, kpts :166, PW/G :42, RAM :189/:191, iters :2647, WALL :2747) |
| s0_OOH__2x1v_escape__u715 (atomic) | 39 | 325 | 196 | 10 | 8 | 6153.8249 | 299.19 | 31.78 | 389.41 | 26 | runs/a0/cell/s0_OOH__2x1v_escape__u715.out (nelec :51, nbnd :52, V :48, kpts :180, G :193, RAM :197/:199, iters :2412, WALL :2515) |
| s0_OH__u715_atomic (1x1, atomic) | 20 | 163 | 98 | 15 | 4 | 3076.9124 | 79.14 | 8.69 | 185.39 | 30 | runs/a0/p_proj/s0_OH__u715_atomic.out (nelec :52, nbnd :53, V :49, kpts :162, G :180, RAM :184/:186, iters :1762, WALL :1846) |
| runs/a0/pproj_cell/s0_OOH__2x1v_escape__u715_ortho.out (ortho twin of the nat 39 row) | 39 | 325 | 196 | 10 | 8 | 6153.8249 | 299.19 | 31.78 | 473.78 | 27 | iters :2426, WALL :2530 |

Plane waves per k-point at the reference: 84555 (runs/a0/cell/ref__2x1v__u715.out:42, third G-vector column); dense G-vectors 1682519 (:42 / :185). Both scale with cell volume at fixed cutoff.

## 1b. SCF iteration survey of the banked nspin = 2 slab outputs

Every pw.x output under runs/ (runs/hea excluded) with nat >= 18 and a printed magnetisation: 664 files; first SCF converged in 594 of them, and 72 files carry `convergence NOT achieved`. Nearest-rank percentiles of the first-SCF iteration count:

| subset | n | min | median | p75 | p90 | max |
|---|---|---|---|---|---|---|
| all nspin = 2 slab outputs | 594 | 11 | 28.0 | 36 | 46 | 525 |
| local-TF, mixing_beta 0.3 (the setting of every deck here) | 564 | 11 | 27.0 | 36 | 42 | 174 |

Banked first SCFs above the planning count (42): 76 of 594; above the ceiling count (126): 9 of 594; never converged: 72 of 664. The three calibration points (22, 26, 30 iterations) sit at or below the median; the largest banked cells (nat >= 36) show:

| first-SCF iterations | nat | output |
|---|---|---|
| 67 | 37 | runs/s3/Co/s0_O__2x1v_off.out |
| 68 | 39 | runs/s3/Co/s0_OOH__2x1v_mir__g1.out |
| 69 | 39 | runs/s3/Co/s0_OOH__2x1v_mir__reanchor.out |
| 70 | 37 | runs/s0/h_afm_relax/s0_O__2x1v_off__afm__relax__r1.out |
| 136 | 39 | runs/s3/Co/s0_OOH__2x1v_mir.out |
| 273 | 39 | runs/s3/Co/s0_OOH__2x1v_mir__g1__r3.out |
| 325 | 36 | runs/s3/Co/ref__2x1v.out |
| 525 | 36 | runs/s3/Co/ref__2x1v.replay_ms.out |

PLANNING_ITERS is fixed at 42 in the source; the survey's live p90 is 42 (equal). No banked SCF is a five-3d-species disordered slab; the survey bounds the single-metal precedent, not this arm.

## 2. The model

With the reference SCF `ref__2x1v__u715` as the anchor, for a target cell:

- electrons = sum of UPF valences; KS states by the pw.x rule `nbnd = NINT(1.2 * NINT(nelec/2))`, which reproduces every banked pair checked (312->187, 325->196, 318->191, 319->192, 163->98, 162->97, 181->109, 168->101, 348->209; runs/a0/cell/*.out, runs/a0/p_proj/s0_OH__u715_atomic.out:52-53, runs/a0/main/Mn/slab__u750.out, runs/a0/main/Fe/s0_OOH__u750.out, runs/a0/main/Ru/slab__u000.out, runs/s3/Co/ref__2x1v__g1.out);
- k-points = full mesh of the k-mesh rule (nosym + noinv); LSDA doubles the list; per-pool load k_local = ceil(2 k / npool);
- f_V = V / V_ref, f_B = nbnd / nbnd_ref, f_K = k_local / k_local_ref, f_P = (ranks per pool)_ref / (ranks per pool);
- **model A (envelope, planning):** wall per SCF iteration = t_ref x f_V x f_B^2 x f_K x f_P (subspace/orthogonalisation-dominated);
- **model B (floor):** wall per SCF iteration = t_ref x f_V x f_B x f_K x f_P (FFT-dominated);
- per-SCF wall = per-iteration wall x 42 iterations; core-h = wall x 128 / 3600; ortho = atomic x 1.2167; ceiling = 3 x planning (= 126 iterations at the model-A rate);
- memory per process = m_ref x max(f_V f_B f_K f_P, f_V f_P) (the wavefunction-dominated and density-dominated limits); total = per-process x 128 (envelope) and m_tot_ref x the same factor (scaled).

Calibration of the model on the three banked points (prediction from the reference; residual = predicted / observed):

| SCF | t/iter observed (s) | model A (s) | A/obs | model B (s) | B/obs | RAM/proc observed (MB) | RAM/proc model (MB) | model/obs | nbnd rule |
|---|---|---|---|---|---|---|---|---|---|
| ref__2x1v__u715 (atomic) | 23.76 | 23.76 | 1.00 | 23.76 | 1.00 | 303.54 | 303.54 | 1.00 | 187 vs 187 |
| s0_OOH__2x1v_escape__u715 (atomic) | 14.98 | 19.57 | 1.31 | 18.68 | 1.25 | 299.19 | 303.54 | 1.01 | 196 vs 196 |
| s0_OH__u715_atomic (1x1, atomic) | 6.18 | 3.26 | 0.53 | 6.23 | 1.01 | 79.14 | 79.54 | 1.01 | 98 vs 98 |

Model A under-predicts the 1x1 point (0.53, through f_P = 0.5: ideal within-pool scaling to 32 ranks is not realised on a 1x1 cell) and over-predicts the nat 39 point (1.31); model B fits both within 25 %. For the HEA cells f_P = 1 (nk = 8, as the reference), so the two models differ only through the extra factor f_B = 2.2, and model A is kept as the planning envelope on the cost-miss precedent; model B is the floor.

## 3. Extrapolation to the retained 75-atom HEA cells

### equiatomic_pull2.10 (75-atom OOH cell)

Source geometry: `results/cr_site_chains_2026-09-06/equiatomic_ooh_replay.json /attempts/2/geometry`; composition {"Cr": 6, "Ni": 6, "Co": 6, "Fe": 6, "O": 50, "H": 1}; cell volume 1888.2197 A^3 = 12742.34 bohr^3; k-mesh 4 2 1 -> 8 k-points (full mesh), nk = 8, ranks per pool 16, k_local 2 (LSDA).

| descriptor | value |
|---|---|
| electrons | 691 |
| KS states (rule) | 415 |
| plane waves per k-point (V-scaled) | 175083 |
| dense G-vectors (V-scaled) | 3483886 |
| f_V, f_B, f_K, f_P | 2.0706, 2.2193, 0.5000, 1.0000 |
| per-iteration wall, model A / B (s) | 121.14 / 54.59 |
| **atomic, per SCF: planning / floor / ceiling (core-h)** | **180.9 / 81.5 / 542.7** (planning wall 1.41 h at 42 iterations) |
| **ortho, per SCF: planning / floor / ceiling (core-h)** | **220.1 / 99.2 / 660.3** (planning wall 1.72 h) |
| memory per process, planning / ceiling (MB) | 697.4 / 2092.3 |
| memory total at np = 128, envelope / scaled / ceiling (GB) | 87.2 / 74.3 / 261.5 |
| billing at planning memory | max(128, ceil(87.2/2) = 44) = 128 SU/h, core-bound, fits the 237 GB node |
| billing at ceiling memory | max(128, ceil(261.5/2) = 131) = 131 SU/h, MEMORY-bound, EXCEEDS the 237 GB node |

### leader_pull2.10 (75-atom OOH cell)

Source geometry: `results/cr_site_chains_2026-09-06/leader_ooh_replay.json /attempts/2/geometry`; composition {"Mn": 8, "Ni": 8, "Cr": 7, "Cu": 1, "O": 50, "H": 1}; cell volume 1833.4445 A^3 = 12372.70 bohr^3; k-mesh 4 2 1 -> 8 k-points (full mesh), nk = 8, ranks per pool 16, k_local 2 (LSDA).

| descriptor | value |
|---|---|
| electrons | 674 |
| KS states (rule) | 404 |
| plane waves per k-point (V-scaled) | 170004 |
| dense G-vectors (V-scaled) | 3382822 |
| f_V, f_B, f_K, f_P | 2.0106, 2.1604, 0.5000, 1.0000 |
| per-iteration wall, model A / B (s) | 111.47 / 51.60 |
| **atomic, per SCF: planning / floor / ceiling (core-h)** | **166.5 / 77.1 / 499.4** (planning wall 1.30 h at 42 iterations) |
| **ortho, per SCF: planning / floor / ceiling (core-h)** | **202.5 / 93.7 / 607.6** (planning wall 1.58 h) |
| memory per process, planning / ceiling (MB) | 659.2 / 1977.7 |
| memory total at np = 128, envelope / scaled / ceiling (GB) | 82.4 / 70.2 / 247.2 |
| billing at planning memory | max(128, ceil(82.4/2) = 42) = 128 SU/h, core-bound, fits the 237 GB node |
| billing at ceiling memory | max(128, ceil(247.2/2) = 124) = 128 SU/h, core-bound, EXCEEDS the 237 GB node |

## 4. Arm totals (per-deck sums; the figure each manifest prints)

Branch panel (runs/hea/branch_panel): 5 geometries x {atomic, ortho} = 10 SCFs on 75-atom cells. Pilot on the two retained chains (runs/hea/pilot_retained): 2 chains x {slab 72, OH 74, O 73, OOH 75 atoms} x 2 projectors = 16 states, of which the four OOH decks are byte-identical (except prefix) to the panel decks `equiatomic_pull2.10` and `leader_pull2.10` and are NOT built again: the pilot readout reads those four panel outputs, so the pilot runs 12 SCFs. Per-deck figures below come from each state's own geometry.

| deck | projector | nat | electrons | KS states | planning (core-h) | floor | ceiling | RAM envelope (GB) | note |
|---|---|---|---|---|---|---|---|---|---|
| equiatomic_pull2.10 | atomic | 75 | 691 | 415 | 180.9 | 81.5 | 542.7 | 87.2 |  |
| equiatomic_pull2.10 | ortho | 75 | 691 | 415 | 220.1 | 99.2 | 660.3 | 87.2 |  |
| equiatomic_builder | atomic | 75 | 691 | 415 | 180.9 | 81.5 | 542.7 | 87.2 |  |
| equiatomic_builder | ortho | 75 | 691 | 415 | 220.1 | 99.2 | 660.3 | 87.2 |  |
| leader_builder | atomic | 75 | 674 | 404 | 166.5 | 77.1 | 499.4 | 82.4 |  |
| leader_builder | ortho | 75 | 674 | 404 | 202.5 | 93.7 | 607.6 | 82.4 |  |
| leader_pull2.10 | atomic | 75 | 674 | 404 | 166.5 | 77.1 | 499.4 | 82.4 |  |
| leader_pull2.10 | ortho | 75 | 674 | 404 | 202.5 | 93.7 | 607.6 | 82.4 |  |
| leader_pull1.70 | atomic | 75 | 674 | 404 | 166.5 | 77.1 | 499.4 | 82.4 |  |
| leader_pull1.70 | ortho | 75 | 674 | 404 | 202.5 | 93.7 | 607.6 | 82.4 |  |
| Fe25Co25Ni25Cr25__s2_site0/slab | atomic | 72 | 678 | 407 | 174.0 | 79.9 | 522.0 | 85.5 |  |
| Fe25Co25Ni25Cr25__s2_site0/slab | ortho | 72 | 678 | 407 | 211.7 | 97.3 | 635.1 | 85.5 |  |
| Fe25Co25Ni25Cr25__s2_site0/OH | atomic | 74 | 685 | 412 | 178.3 | 80.9 | 534.9 | 86.5 |  |
| Fe25Co25Ni25Cr25__s2_site0/OH | ortho | 74 | 685 | 412 | 216.9 | 98.5 | 650.8 | 86.5 |  |
| Fe25Co25Ni25Cr25__s2_site0/O | atomic | 73 | 684 | 410 | 176.6 | 80.5 | 529.7 | 86.1 |  |
| Fe25Co25Ni25Cr25__s2_site0/O | ortho | 73 | 684 | 410 | 214.8 | 98.0 | 644.5 | 86.1 |  |
| Fe25Co25Ni25Cr25__s2_site0/OOH | atomic | 75 | 691 | 415 | 180.9 | 81.5 | 542.7 | 87.2 | REUSED: panel deck equiatomic_pull2.10__atomic (not counted) |
| Fe25Co25Ni25Cr25__s2_site0/OOH | ortho | 75 | 691 | 415 | 220.1 | 99.2 | 660.3 | 87.2 | REUSED: panel deck equiatomic_pull2.10__ortho (not counted) |
| Ni31Cr29Cu5Mn35__s0_site0/slab | atomic | 72 | 661 | 397 | 160.7 | 75.7 | 482.2 | 81.0 |  |
| Ni31Cr29Cu5Mn35__s0_site0/slab | ortho | 72 | 661 | 397 | 195.6 | 92.1 | 586.7 | 81.0 |  |
| Ni31Cr29Cu5Mn35__s0_site0/OH | atomic | 74 | 668 | 401 | 164.0 | 76.5 | 492.0 | 81.8 |  |
| Ni31Cr29Cu5Mn35__s0_site0/OH | ortho | 74 | 668 | 401 | 199.5 | 93.1 | 598.6 | 81.8 |  |
| Ni31Cr29Cu5Mn35__s0_site0/O | atomic | 73 | 667 | 401 | 164.0 | 76.5 | 492.0 | 81.8 |  |
| Ni31Cr29Cu5Mn35__s0_site0/O | ortho | 73 | 667 | 401 | 199.5 | 93.1 | 598.6 | 81.8 |  |
| Ni31Cr29Cu5Mn35__s0_site0/OOH | atomic | 75 | 674 | 404 | 166.5 | 77.1 | 499.4 | 82.4 | REUSED: panel deck leader_pull2.10__atomic (not counted) |
| Ni31Cr29Cu5Mn35__s0_site0/OOH | ortho | 75 | 674 | 404 | 202.5 | 93.7 | 607.6 | 82.4 | REUSED: panel deck leader_pull2.10__ortho (not counted) |

| arm | SCFs | planning (core-h) | floor (core-h) | ceiling (core-h) | 48 h walltime cap (SU) |
|---|---|---|---|---|---|
| branch panel (2 equiatomic + 3 leader geometries, both projectors) | 10 | 1909.0 | 873.8 | 5727.0 | 61440 |
| pilot on the two retained chains (slab, OH, O in both projectors; OOH read from the panel) | 12 | 2255.7 | 1042.0 | 6767.2 | 73728 |
| both arms | 22 | 4164.7 | 1915.8 | 12494.2 | 135168 |

The walltime cap is what anvil/47_submit_a0.sh:108-109 prints (N x 128 x 48 SU); it is a cap, not a forecast. Balance context: 59,473.5 SU on 2026-09-05 (docs/88-a10-signature-sheet-2026-09-05.md:245, `mybalance`) before the 11.41 core-h of the gate-(e) pair (docs/90-small-arms-readout-2026-09-06.md:352-355) and the q333 pair.

## 5. What the model does not cover

- The SCF iteration count on a five-3d-species disordered slab with a ferromagnetic start has no precedent in this tree; section 1b bounds it from the single-metal record only. The planning figure assumes 42 iterations, the ceiling 126; `electron_maxstep = 300` in the decks caps a non-convergent SCF at 7.1x the planning wall, which is why a kill rule is proposed as an entrant slot in docs/92.
- The ortho-atomic x nspin = 2 x five-species combination has never run; the 1.2167 ratio is one 2x1v OOH pair, and the 1x1 per-state ratios span 0.953-1.609.
- projwfc.x (run inline by anvil/46_a0.slurm on a converged point) is not costed; on the banked Ru u750 row it added 28.45 s to 442.81 s of pw.x for four SCFs (docs/89-ru-pseudopotential-control-DRAFT.md:215).
- Memory at the ceiling exceeds the 237 GB node for both cells; if the planning memory is exceeded by more than ~2.6x the job cannot run at 128 ranks on one node as designed. nk = 4 halves the density-part share per process and is the fallback, not the plan.
