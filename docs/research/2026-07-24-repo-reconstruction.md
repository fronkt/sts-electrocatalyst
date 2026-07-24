# Deep-Research Report 1/4 — STS2027 Catalysis Campaign Reconstruction

> **Provenance:** produced 2026-07-23/24 by a repo-analysis agent reading docs/12–26, run
> artifacts, and git history of fronkt/STS2027. One of four parallel surveys distilled into
> [docs/28](../28-electrocatalyst-revival-plan.md). Verbatim archive.

## 1. SCIENTIFIC GOAL & THESIS

**Project (docs/12, docs/16):** "Machine-Learning-Guided Discovery of an Earth-Abundant High-Entropy-Alloy Oxygen-Evolution Electrocatalyst, Validated by Self-Fabrication and Calibrated Against Experiment." Screen the earth-abundant 3d-metal HEA composition space for **alkaline OER (1 M KOH)** activity; melt the picks personally at Fort Wayne Metals; measure at Purdue; beat/match a **NiFe-LDH baseline (~250–300 mV @ 10 mA cm⁻²)**.

- **Hypothesis (docs/12 §1, verbatim intent):** an ML-selected, earth-abundant HEA in the **Fe–Co–Ni–(Cr/Mn/Cu)** space will, after in-situ reconstruction to an (oxy)hydroxide skin, show η@10 mA cm⁻² within ±20 mV of or below NiFe-LDH with zero PGMs, and the ML ranking will correlate with the measured ranking (Spearman ρ with error bars).
- **Physics angle:** HEA multi-element cus-site distributions may partially decouple the *OH/*OOH scaling relation (ΔG_OOH ≈ ΔG_OH + 3.2 eV) that pins ordered surfaces to the η ≈ 0.37 V volcano floor.
- **Candidate space:** Fe–Co–Ni–Cr–Mn–Cu simplex, gated by empirical single-phase formability (VEC, δ, ΔH_mix, ΔS_mix, Ω). UMA round-1 shortlist: **Fe32Ni17Co34Mn18** (headline, Cr-free, η_best 0.78 V), Cr21Ni24Co15Cu6Fe33, Cr8Fe34Mn9Ni23Co27, Co24Fe24Ni35Mn17; diverse sweep added **Cr6Fe33Ni27Mn34** (cheapest, $6.25/kg) and Co20Ni20Cr20Mn20Cu20. DFT reference set: the six rutile **MO₂ endmembers, M ∈ {Cr, Mn, Fe, Co, Ni, Cu}**; then SQS approximants of the top 3–5 HEAs (never reached).
- **Intended STS-level claim (docs/22 §2):** "DFT validates/corrects the UMA ranking" — explicitly NOT "DFT found a different global winner." Three pre-registered honest outcomes (agree / disagree / partial), all reportable. The actual outcome was "disagree" — see §4/§5.

## 2. PIPELINE DESIGN

Multi-fidelity funnel (docs/22 §"proposer → UMA → QE → melt"): **heuristic prior (CPU) → UMA `uma-s-1p1` universal MLIP screen (thousands of compositions, GPU) → Quantum ESPRESSO PBE+U DFT (top 3–5 + endmember reference set, entrant-run) → melt + measure at FWM/Purdue**, with calibration gates (Spearman ρ + parity plot) between each tier.

- **UMA role:** cheap screen; absolute η distrusted (OC20 head is metal-dominated, oxides are OOD); only the *ranking* trusted — the DFT tier exists exactly to test that trust (docs/22 §1).
- **DFT role:** calibrate UMA (parity plot, ρ + CI, re-ranking table) and "DFT-bless" the melt list (docs/22 §6–7). Endmember parity was a hard **go/no-go gate before the round-2 melt** (docs/22 §8).
- **BO/AL loop:** multi-objective BO (`Ax`/`BoTorch`, qNEHVI) over activity × cost × formability; round-2 active learning conditioned on measured η (`src/hea_oer/active_learning.py::propose_round2`) — never triggered (blocked on experiment).
- **Phases (tasks/plan-catalysis-hea.md):** Phase 0 setup → Phase 1 ML round-1 (DONE) → Phase 1.5 DFT calibration tier (partially done, see §4) → Phase 2 fabrication/characterization (never started) → Phase 3 OER round-1 EC (never started) → Phase 4 AL round-2 + stability (never started) → Phase 5 write. Defining docs: docs/12 (execution plan), docs/22 (DFT protocol), docs/13/14 (UMA results + compute log), docs/15 (melt/test plan), docs/23 (DFT log), docs/26 (final checkpoint), docs/19/20/21 (compute-only fallbacks).

## 3. EXACT DFT METHODOLOGY

- **Code:** **Quantum ESPRESSO `pw.x` v7.5** (conda-forge build, OpenMPI 5.0.10, ELPA, HDF5). No VASP (no license). The commit-70f5521 knobs (Davidson beta=0.05, ndim=16, maxstep=800) are QE `&ELECTRONS` settings: `diagonalization='david'`, `mixing_beta=0.05`, `diago_david_ndim` bump, `electron_maxstep=800`. NB: apt QE 6.7 is unusable (glibc buffer-overflow crash on input read; docs/23 §1).
- **Functional:** PBE + U (Dudarev), via the **QE ≥7.1 `HUBBARD (atomic)` card** (not `lda_plus_u`). **U_eff (eV): Cr 3.7, Mn 3.9, Fe 5.3, Co 3.32, Ni 6.2, Cu 0** — Materials-Project–calibrated (Jain 2011 / Wang 2006) (docs/22 §4, docs/23 §1).
- **Pseudopotentials:** SSSP Efficiency (PBE), from apt `quantum-espresso-data-sssp` at `/usr/share/espresso/pseudo`. Named: O `O.pbe-n-kjpaw_psl.0.1.UPF` (PAW), Cr `cr_pbe_v1.5.uspp.F.UPF` (GBRV USPP), H `H.pbe-rrkjus_psl.1.0.0.UPF`; Mn/Co/Ni GBRV USPP, Fe/Cu PAW psl (docs/23 §1, §5).
- **Cutoffs:** **ecutwfc 80 Ry / ecutrho 640 Ry (dual 8)** — locked by CrO₂ bulk sweep to <1 meV/atom (80→90 Ry = 0.4 meV; docs/23 §4, `results/cro2_dft_convergence.csv`).
- **k-points:** bulk **6×6×8** (6×6×8→8×8×12 = 0.4 meV/atom). Slabs: auto-scaled, 1 point along vacuum — adslabs **9×4×1** MP automatic (from `runs/Cr_slab/s0_OH.in`); gas refs Γ. MPI k-pools: `-nk 4` adslabs / `-nk 6` clean slabs (clean slab has `nosym=.true. noinv=.true.` → 36 irreducible k-pts vs 15, most expensive job).
- **Spin:** nspin=2, starting_magnetization 0.6 on metal; FM start (bulk CrO₂ validated at 4.00 μB/cell = 2.0 μB/Cr, correct d² FM half-metal). Smearing Marzari–Vanderbilt, degauss 0.01 Ry. `mixing_mode='local-TF'` for slabs (cure for magnetic-slab charge sloshing; baked into `qe_slab.py`).
- **Slab model:** rutile **MO₂(110)**, 1×1 surface cell, **18-atom slab** (6 M + 12 O; adslab nat=19–21), 3 cation layers; cell 2.916 × 6.252 × 25.009 Å → ~16 Å vacuum; bottom cation layer + its O shell fixed (`if_pos 0 0 0`; 7 of 18 atoms in s0_OH). **No dipole correction — deliberate, to match the UMA setup** (docs/26 §3). Geometry identical to the UMA-relaxed inputs (only the relaxer differs).
- **Adsorbates/pathway:** *OH, *O, *OOH on the single cus site (s0); standard 4-step OER via **CHE**; ΔGᵢ from ΔE + fixed ZPE−TΔS corrections **{OH: 0.35, O: 0.05, OOH: 0.40} eV** (Man 2011/Valdés 2008; `src/hea_oer/referencing.py::ZPE_TS_CORRECTION`); η = max(ΔG₁…₄)/e − 1.23 V.
- **Gas references (shared across all endmembers):** H₂ = **−2.33323818 Ry**, H₂O = **−44.04119711 Ry** (commit 78396b5; docs/26 §1).
- **Convergence/optimization:** `conv_thr 1e-6` Ry SCF; BFGS relax, `forc_conv_thr 2.0d-3` Ry/bohr (all 46 committed inputs), `nstep 200`, production `mixing_beta 0.3`, `electron_maxstep 200`. Escalation recipes in §5 below. Post-hoc acceptance criterion (docs/26 §1): `JOB DONE` AND zero `convergence NOT achieved` AND final total force norm ≤ ~0.005 Ry/bohr.
- **Solvation:** none (not documented anywhere — pure vacuum slabs).

## 4. WHAT COMPLETED

**UMA screening (docs/13, docs/14, all 2026-06-26, RTX 5090):**
- Run A, metal fcc(111): 3000 sampled → 2470 single-phase → top-24 UMA'd in 833 s; ρ(heuristic, UMA)=0.236; unphysical η 2.7–4.9 V (proxy only).
- Run B, rutile(110) multi-site: top-12, 4 cus sites each, 1899 s; **Fe32Ni17Co34Mn18 #1, η_best 0.78 V**, descriptor 1.75 eV; ρ(heuristic, rutile) = **−0.09**.
- Run C, diverse sweep: 4000 → 3304 single-phase → max-min diverse 30, 5795 s; headline holds (identical 0.78 V, lowest top-tier η_std 0.26); new find Cr6Fe33Ni27Mn34.
- UMA η for all six endmembers: **Cr 1.147 / Fe 1.105 / Mn 2.347 / Ni 2.382 / Co 2.389 / Cu 2.418 V** (`runs/<M>_slab/uma_eta.json`).

**QE tier stand-up:** engine validation SCF (3.6 min, mag 4.00 μB, +U active via `force_hub`); full convergence sweep (11 SCFs, all converged) → locked 80/640/6×6×8.

**CrO₂ parity anchor:** first DFT η computed as **2.03 V (later RETRACTED — unconverged)**; corrected converged value **1.726 V**.

**Endmember parity campaign (2026-07-01 → 07-13) — the keystone deliverable (docs/26):** 4/6 endmembers converged:

| Endmember | η_UMA (V) | η_DFT (V) | DFT ΔG_OH / ΔG_O / ΔG_OOH (eV) | Limiting step |
|---|---|---|---|---|
| MnO₂ | 2.347 | **0.892** | 1.907 / 4.029 / 4.989 | 2 (*OH→*O) |
| FeO₂ | 1.105 | 1.263 | 2.134 / 4.627 / 5.221 | 2 |
| CrO₂ | 1.147 | 1.726 | 1.518 / 4.474 / 4.799 | 2 |
| NiO₂ | 2.382 | 1.751 | 2.516 / 5.497 / 5.202 | 2 |

**Parity stats (n=4):** Spearman ρ = 0.400 (p = 0.60), Pearson r = −0.2157 (p = 0.784), MAE = 0.706 eV, mean bias (UMA−DFT) = +0.337 eV (`docs/figs/uma_dft_parity.json/.png`). Per-adsorbate data exists on both sides: DFT ΔGs above; UMA per-step in `runs/<M>_slab/uma_eta.json` (e.g. Cr UMA dG_OH 1.259 / dG_O 0.934 / dG_OOH 3.311, limiting step 3 — vs DFT step 2; UMA over-binds *O by ~3.5 eV on Cr). **Conclusion: UMA cannot rank rutile-oxide OER** — its worst endmember (Mn 2.35 V) is DFT's best (0.89 V). All four DFT points limited by step 2; UMA reshapes the whole free-energy landscape, not a correctable offset.

## 5. WHAT FAILED & WHY

**The QC crisis (docs/26 §4, commit da87f7e):** first full pass "completed" 20/20 jobs but **12/16 needed adslab relaxations were silently unconverged** — `pw.x` prints `JOB DONE`/exit 0 even when mid-relax SCF hits `electron_maxstep`; final forces 0.017–0.066 Ry/bohr (17–66× threshold). **Retracted values (never quote): Cr 2.03 V (the original PR #15 headline), interim Mn 1.57 V, Co 1.68 V.** Corrected: Cr 2.03→1.726; Mn 1.57→0.892 (one bad *OOH geometry, ΔG_OOH 6.83→4.99 eV, flipped the element's story). Fix: queue now logs `SCF_FAIL` + `F_LAST` per job; acceptance is a documented human check.

**Convergence-escalation ladder (docs/26 §5), 4×3 adslabs:** attempt 1 production Davidson β=0.3 → 4/16; attempt 2 (`build_restarts.py`, β=0.1, maxstep 500, seeded from last BFGS geometry) → +7; attempt 3 (`build_attempt3.py`, CG diagonalization, min-force seed) → 0 converged but diagnostic, **31 h to fail on Co *O**; attempt 4 (`build_attempt4.py`, Davidson β=0.05 ndim 16 maxstep 800) → +2 (Cr *OH, Mn *OOH); attempt 5 (`.in.lastshot`, β=0.03 ndim 20 maxstep 1500) → +1 (Ni *OOH, 24.2 h, F=0.0034).

**Co/Cu exclusion — spin/charge multistability (docs/26 §6, pre-registered time-box 2026-07-12):**
- **CoO₂:** *O and *OOH failed all four recipes (0-for-4 each). Smoking gun: CG re-evaluated a geometry Davidson scored at F=0.0098 and got **F=0.050** — two solvers converge to *different self-consistent spin states* at identical nuclear coordinates → forces irreproducible → BFGS cannot converge. System property, not tuning failure.
- **CuO₂:** *O oscillated/stalled at F=0.020 over a 30 h relax; *OH died on the first SCF twice under different recipes; *OOH did converge (F=0.003). 2/3 adsorbates missing ⇒ no η.
- Degauss/smearing bumps rejected (breaks ΔG consistency within an element). ~17 failed relaxation attempts total across 4 recipes.

**Operational failures:** stdin-drain queue bug (OpenMPI drained the here-string job list — 9 h idle; fixed b3eecdd `</dev/null`), a `pkill -f` friendly-fire (2.5 h), two vast.ai account pauses (Jul 10, 11; ~12 h each + salvage), restart-seeding lesson (seed from **min-force** geometry, never last BFGS proposal), `nproc` lying on cgroup-capped containers (see §8).

## 6. WHAT WAS NEVER LAUNCHED

(Nuance: the 20-job endmember queue **was** in fact launched and completed 2026-07-13 — docs/24 §9 initially said "do not launch" but the parity close-out superseded that; memory claiming it never launched is stale. What genuinely never ran:)

- **SQS/ordered-approximant DFT of the top 3–5 HEAs** (docs/22 §5 set 2/3; `icet`/`mcsqs` structures never built) — the endmember gate failed first, mooting it.
- **Consensus melt list / any melt:** no alloy was ever melted; the reserved FWM slot transferred to thermal round-0 Cu-Fe melts (docs/24 §9).
- **All experiment:** NiFe-LDH baseline synthesis, electrochemistry, stability, post-mortem — none started (potentiostat never booked).
- **Round-2 active learning** (`propose_round2`) — blocked on measured η forever.
- **OC22 models:** docs/12 planned OC22 EquiformerV2/GemNet-OC; actual runs used only UMA `uma-s-1p1` with the **oc20** task. OC22/omat cross-checks and oxyhydroxide (NiOOH/FeOOH) terminations: listed as "optional next", never run.
- **docs/21 fallback (generative + DFT HER discovery):** full plan drafted — conditional flow-matching generator (symmc-flow stack; MatterGen fine-tune fallback at a Week-2 pilot gate), condition on ΔG_H* ≈ 0 (ΔG_H* = ΔE_H + 0.24 eV), generate 10⁴–10⁵ → UMA screen (one-adsorbate swap) → DFT top 10–20, OCx24 experimental benchmark, budget ~$1,200–3,800. **Nothing executed** — no pilot, no data pull, no *H backend swap. It was gated on the main project's Week-9 go/no-go, which never arrived. docs/19 = the fallback shortlist; docs/20 = its deep-research brief.

## 7. DOCUMENTED LIMITATIONS & OPEN QUESTIONS

- **n=4 parity is statistically weak** (p=0.60) — the docs themselves report it as "indistinguishable from chance" and lean on the rank inversion (Mn) as the story, not the ρ.
- **Descriptor-only thermodynamic η** — no kinetics/barriers; η from max-ΔG step only.
- **Model surface:** rutile(110) is not the true reconstructed oxyhydroxide; FeO₂/CoO₂/NiO₂/CuO₂ are **non-ground-state rutiles** (model values on the rutile trend; flagged docs/13, docs/16 §8, docs/22 §5).
- **No dipole correction** (deliberate UMA-matching, but a real physics omission for asymmetric adslabs); **no solvation**; fixed ZPE−TΔS constants rather than computed vibrations; single cus site (n_sites=1) on the 1×1 endmember cells.
- **Stability never assessed** — no Pourbaix, no dissolution, no energy-above-hull on the DFT side; Cr(VI) leaching flagged only as a lab-safety risk.
- **Functional:** PBE+U with MP-calibrated U values; no HSE/RPBE cross-check (docs/21 mentions RPBE for the HER fallback, never used here). Co/Cu multistability itself is flagged as a reportable pathology "the multi-fidelity literature hand-waves past."
- **Revival prescription (docs/26 §7):** either an MLIP fine-tuned on oxide+U data, or DFT-heavy screening at ~1–5 box-days/composition — unaffordable at 3000-candidate scale.
- Housekeeping still open: revoke the HF token (frankcai222) — flagged pending in docs/23 §9 and docs/24 §9.

## 8. COMPUTE FOOTPRINT

- **UMA (2026-06-26):** Vast.ai RTX 5090 (32 GB, driver 580, CUDA 13.0), torch 2.8.0+cu128, fairchem-core 2.21.0. 833 s (24 fcc111 comps) / 1899 s (12 rutile × 4 sites) / 5795 s (30 × 4); ~35 s/candidate metal, GPU shared with batterycv.
- **QE box 1:** Threadripper PRO 7975WX 32C/64T, 125 GB, 2× idle RTX 5090 (wound down as wasteful). Bulk SCF 3.6 min; heaviest convergence point ~9 min on 24 ranks; per-adslab relax ~1.5–2 h.
- **QE box 2 (192.3.91.246, RTX 5090, shared with OptiGrain):** the **cgroup cap lesson** — `nproc` said 256 but `cpu.max` = 3071999/100000 → 30.72 vCPU; 240 ranks gave ~525 s/SCF-iter, right-sized 24 ranks gave ~40 s/SCF-iter at 99 % efficiency (~12× speedup). Destroyed after relocation.
- **Endmember campaign boxes:** two Vast.ai CPU containers each cgroup-capped at **15.36 vCPU** (`nproc` lied: 64 and 192); NP=12, NCONC=1. Box A 120.238.149.205 (Mn/Fe/Cu + Cr redo; later repurposed for MuST), box B 137.175.76.24 (Co/Ni; destroyed). **Wall time 2026-07-01→07-13 (~12.5 days)**; longest job Ni *OOH 24.2 h; CG failure on Co *O 31 h; Cu *O 30 h stall. DFT screening cost priced at ~1–5 box-days/composition.
- **Dollar spend: not documented** — only budget estimates (docs/12 §9: ~$100–300 UMA GPU, ~$150–400 DFT CPU). No actual invoices/hourly rates recorded anywhere in the repo.

## 9. FILE MAP (paths relative to repo root)

**Docs (catalysis line):** `docs/08-catalysis.md` (lane briefing) · `docs/12-catalysis-hea-execution-plan.md` (master spec) · `docs/13-round1-uma-results.md` · `docs/14-compute-log.md` (UMA compute log) · `docs/15-round1-melt-test-plan.md` · `docs/16-project-overview.md` (dossier) · `docs/17-fwm-weigh-sheet.md` · `docs/18-competitive-benchmark.md` · `docs/19-computational-fallback.md` · `docs/20-fallback-bestbet-her-discovery.md` · `docs/21-fallback-execution-plan.md` (HER fallback) · `docs/22-multifidelity-dft-calibration.md` (DFT protocol) · `docs/23-dft-compute-log.md` (DFT log, closed) · `docs/26-endmember-parity-checkpoint.md` (final checkpoint + retraction record). Parking decision: `docs/24-thermal-pivot-execution-plan.md` §9.

**Figures/results:** `docs/figs/uma_dft_parity.png` + `.json` (keystone) · `results/cro2_dft_convergence.csv` · `results/round1_uma{,_rutile,_rutile_sweep}_candidates.csv` + volcano PNGs.

**Code:** `src/hea_oer/` (screen: `adsorption.py`, `surfaces_rutile.py`, `phase_stability.py`, `referencing.py` [ZPE_TS_CORRECTION], `descriptors.py`, `active_learning.py`, `relax.py`) · `src/scripts/run_round1_uma.py` (round-1 driver) · `src/dft/` (`gen_rutile.py`, `run_convergence.sh`, `qe_slab.py` [build/eta], `run_slab_dft.sh`, `queue_dft.sh` [throttled queue + SCF_FAIL/F_LAST], `build_restarts.py`/`build_attempt3.py`/`build_attempt4.py` [escalation builders], `uma_endmembers.py`/`uma_slab_eta.py` [UMA side of parity], `parity_plot.py`, `setup_newbox.sh` [box redeploy]).

**Run artifacts:** `runs/{Cr,Mn,Fe,Ni,Co,Cu}_slab/` — all `.in` + escalation variants (`.in.restart/.attempt3/.attempt4/.resume/.lastshot`), final `.out` + full `.out.attempt*` failure trail, `manifest.json`, `uma_eta.json` (all six), `dft_eta.json` (Cr/Mn/Fe/Ni only) · `runs/Cr_slab_snapshot.tgz` (mid-campaign box snapshot). Gas refs `H2.out`/`H2O.out` in each element dir.

**Tasks:** `tasks/plan-catalysis-hea.md` (phase tracker, frozen mid-Phase-1.5) · `tasks/plan-her-discovery.md` (fallback tracker, untouched) · `tasks/todo-archive-2026-07-01-pre-thermal-pivot.md` · `tasks/lessons.md`.

**Git:** catalysis history is fully merged to `main` (PR #15 merge `3cab658` landed the `dft-cro2-checkpoint` branch: `da87f7e` QC crisis, `abd78c7` attempt-3, `70f5521` attempt-4, `704f848` final parity, `78396b5` evidence archive [~1 M lines of `.out`], `d5a1a8c` docs/26).
