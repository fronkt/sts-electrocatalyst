# 28 — Electrocatalyst Revival: Literature-Calibrated Upgrade Plan

**Date:** 2026-07-24
**Status:** PROPOSED — awaiting Frank's gate before any compute spend
**Supersedes:** the parking decision in [docs/24 §9](24-thermal-pivot-execution-plan.md) (thermal lane dropped by owner decision 2026-07-23). The HEA-OER campaign (docs/12–23, 26) is un-parked.
**Inputs:** four parallel literature/repo surveys run 2026-07-23/24, archived in full under `docs/research/`:
[repo reconstruction](research/2026-07-24-repo-reconstruction.md) ·
[oxide-OER DFT methodology](research/2026-07-24-methodology-survey.md) ·
[universal-MLIP fine-tuning](research/2026-07-24-mlip-finetuning-survey.md) ·
[rutile results + stability landscape](research/2026-07-24-rutile-landscape-stability-survey.md).
All citations verified against publisher/arXiv/OA landing pages; none sourced from Sci-Hub.

---

## 1. Where the project actually stands (corrected record)

Contrary to the parked-project shorthand, the endmember DFT queue **was launched and completed** (2026-07-01 → 07-13, ~12.5 box-days). Done:

- UMA round-1 screen (runs A/B/C, docs/13–14) with shortlist headed by Fe32Ni17Co34Mn18.
- QE PBE+U tier stood up and convergence-locked (80/640 Ry, 6×6×8; docs/23).
- 4/6 rutile endmembers converged with QC-audited retraction trail (docs/26):
  η_DFT = Mn 0.892 / Fe 1.263 / Cr 1.726 / Ni 1.751 V, all step-2 (*OH→*O) limited.
- UMA-vs-DFT parity: Spearman 0.400 (p=0.60), Pearson −0.216, MAE 0.706 eV → recorded
  conclusion "UMA cannot rank rutile OER"; Co/Cu excluded on spin multistability.

Never run: SQS HEA-approximant DFT, any melt/experiment, round-2 AL, OC22-model cross-checks, oxyhydroxide terminations, docs/21 HER fallback.

The four surveys below change the interpretation of almost every one of these results.

## 2. Finding 1 — the UMA parity verdict is CONFOUNDED (wrong task head)

The entire UMA campaign (screen + parity) ran `uma-s-1p1` with **`task_name="oc20"`** — the head that emulates **RPBE adsorption energies on metals**. The correct head for our chemistry is **`oc22`** (PBE+U oxide **total** energies), which only exists in the `uma-s-1p2` / `uma-s-1p2p1` checkpoints. OC22's training data (Tran et al., arXiv:2206.08917; ACS Catal. 10.1021/acscatal.2c05426) is *literally our system*: VASP PBE+U with Materials-Project U (same scheme as our QE tier), spin-polarized, **4,318 rutile systems incl. unary/binary rutiles, with O*/OH*/OOH* OER intermediates in-distribution**.

A **negative Pearson** (−0.22) is the signature of a reference/settings mismatch, not a capability ceiling — a capability-limited model gives noisy-positive correlation, not anti-correlation. The published failure-mode literature (Loveday, Kaźmierczak & López, ACS Catal. 2026, 10.1021/acscatal.5c08945) puts out-of-box universal-MLIP oxide adsorption errors at ~0.5 eV MAE — our 0.71 eV is in the documented regime — and states that for such cases **"fine-tuning is expected to be mandatory."** Abandonment was the one option the literature does not support.

**Consequence:** before any other conclusion is quoted, re-run parity with `uma-s-1p2p1` + `task_name="oc22"` and a single consistent reference chain (same H₂/H₂O gas references, same magnetic-state selection on both sides). Cost: ≤1 box-day. Possible outcome per the field's experience: Spearman recovers to ~0.6–0.8 with zero training.

## 3. Finding 2 — five of six endmembers are not real electrodes (stability gate missing)

| Endmember | Rutile ambient phase? | Under OER potentials | Verdict |
|---|---|---|---|
| β-MnO₂ | **YES** (pyrolusite) | dissolves in acid; workable neutral/alkaline | only physically meaningful endmember |
| CrO₂ | metastable (CVD-only; decomposes to Cr₂O₃) | oxidizes to soluble CrO₄²⁻ at all pH | dissolves — non-viable |
| FeO₂ | **NO** — pyrite-type, stable only >74 GPa | n/a | fictitious ambient phase |
| CoO₂ | layered (delithiated LiCoO₂), not rutile | reconstructs to CoOOH | wrong polymorph |
| NiO₂ | layered (delithiated LiNiO₂), not rutile | reconstructs to NiOOH | wrong polymorph |
| CuO₂ | does not exist as bulk (Cu(IV) unfavorable) | n/a | nonexistent |

Two consequences:

1. **The Co/Cu SCF failures were physics, not tuning.** Rutile CoO₂/CuO₂ are electronically frustrated fictitious phases; two solvers finding different self-consistent spin states at identical coordinates is what that looks like. Reframe from "failed jobs" to "the calculation diagnosing an unphysical phase" — with the published cures (occupation-matrix control, U-ramping, quasi-annealing; Allen & Watson, PCCP 2014, 10.1039/C4CP01083C) available if we still want converged model values.
2. **Any screening claim must be gated by aqueous stability.** The standard framework: computed Pourbaix ΔG_pbx (Persson et al., PRB 2012, 10.1103/PhysRevB.85.235438; Wang et al., npj Comput. Mater. 2020, 10.1038/s41524-020-00430-3 — both live in the Materials Project Pourbaix app, i.e., mostly free to us). The modern template that does activity+stability+cost jointly with an OC22 model is Tran et al. 2024 (arXiv:2311.00784, Nanoscale 10.1039/d4nr01390e) — 4,119 oxides screened. That paper is the blueprint for our funnel.

Note the alignment with the original HEA thesis (docs/12): the hypothesis always was that the *reconstructed (oxy)hydroxide skin* is the active surface in alkaline OER. The rutile tier is a calibration/model tier — the surveys say to state that explicitly and add oxyhydroxide-termination spot-checks (the "optional next" in docs/22 that never ran).

## 4. Finding 3 — DFT methodology upgrades, ranked by cost

Free (reanalysis of existing data):
- **F1. Volcano reporting.** Report each endmember as a position on the Man 2011 volcano (descriptor ΔG_O−ΔG_OH; apex ≈1.5–1.6 eV; scaling floor η≈0.37 V) with RuO₂(110) 0.37–0.42 V / IrO₂(110) 0.56 V as anchors (Rossmeisl 2007, 10.1016/j.jelechem.2006.11.008; Man 2011, 10.1002/cctc.201000397). Our Mn 0.89 V is literature-plausible for pristine β-MnO₂ (~0.7–1.0+ V band).
- **F2. G_max(η) descriptor** alongside η_thermo — computed from the free-energy diagrams we already have (Exner, ACS Catal. 2021/2023; Acc. Chem. Res. 2024, 10.1021/acs.accounts.4c00048, OA).
- **F3. Honest error bars**: ±0.2–0.4 V per η; differences <0.2 V between metals are not meaningful; rankings not absolute activities (Jones/Teschner/Piccinin, Chem. Rev. 2024, 10.1021/acs.chemrev.4c00171, OA).

Moderate (targeted re-runs):
- **M1. U-sensitivity.** We used MP thermochemical U (Cr 3.7 / Mn 3.9 / Fe 5.3 / Co 3.32 / Ni 6.2 / Cu 0). The closest comparable rutile-OER studies use linear-response U nearly 2× larger (Cr 7.15, Mn 6.63 eV; Xu/Kitchin JPCC 2015, 10.1021/jp511426q; Lim et al., Front. Energy Res. 2021, 10.3389/fenrg.2021.606313 — fully OA) and show U choice re-ranks the volcano. Re-run Mn + Cr at the linear-response U; if the ranking holds, that's a robustness claim; if it flips, that's a finding.
- **M2. Magnetic-state protocol.** β-MnO₂ is AFM (we ran FM starts everywhere); CrO₂ FM half-metal is correct. Initialize each slab from its bulk magnetic ground state; use OMC/U-ramping for the multistable cases; report η(spin-state) spread. (Liang et al., JPCC 2022, 10.1021/acs.jpcc.1c08700 shows termination/magnetism swings RuO₂ η by ~0.4–0.5 V.)
- **M3. Dipole correction + implicit solvation** (currently: neither; vacuum asymmetric slabs). Cheap in QE (`dipfield`, environ).
- **M4. Surface-Pourbaix resting termination.** At OER potentials the cus row is O-covered — computing η on the clean surface biases it (Hansen 2008, 10.1039/b803956a; IrO₂(110) resting-state work, ACS Omega 2025, 10.1021/acsomega.5c10410). A handful of coverage calculations per metal.

Expensive (only for finalists): explicit-water/AIMD solvation, LOM vacancy pathways (Grimaud 2017, 10.1038/nchem.2695; Exner pitfalls 2021), constant-potential GC-DFT (Melander 2019, 10.1063/1.5047829).

## 5. Finding 4 — the screener is salvageable by fine-tuning, and the training data already exists

The field's small-data evidence is unambiguous:
- CLAM (JACS Au 2025, 10.1021/jacsau.5c01112): OC20+OC22-pretrained GemNet-OC, active-learning fine-tune at **3–10 DFT points/loop** → adsorption MAE 0.230 → **0.012 eV**.
- MACE fine-tuned for catalysis (arXiv:2605.09394): **0.30 eV MAE on rutile IrO₂ OER** polymorphs.
- Fine-tuning-strategy study (Tompa et al., arXiv:2606.12704): naive fine-tune is optimal for narrow single-family tasks; LR 1e-3 (MACE) / 4e-4 head-only (UMA); **zero weight decay; E0 reinitialization is the single most important knob** (2–3× force-RMSE swing).
- Expected with 200–500 in-domain points: MAE < 0.1 eV, **Spearman 0.85–0.95**.

**Key asset:** the archived endmember campaign (commit 78396b5, ~1M lines of QE `.out` incl. every failed-attempt trajectory) is an in-domain training set already on disk — first fine-tune costs ~zero new DFT. Hardware: single RTX 4090/5090 vast box, single-digit GPU-hours (UMA-small = 6.6M active params; MACE-medium similar class). Fallbacks if fine-tuning underdelivers: Δ-learning/GP recalibration on frozen descriptors (~50 points lifts ranking), or MLIP-as-prescreener + DFT top-k (the Loveday-sanctioned framing).

UMA has no native uncertainty → use a MACE/committee ensemble for the active-learning acquisition signal.

## 6. Where the novelty is (survey-identified, currently unclaimed)

1. **Spin-multistability-resolved rutile OER screening** — no published paper resolves magnetic-state ambiguity across the 3d rutile (110) series; our Co/Cu failure trail is the seed. (Strongest pure-methodology angle.)
2. **Stability-filtered activity map** — activity × ΔG_pbx Pareto over earth-abundant compositions; the flagship papers gesture at it, none publish it endmember-resolved for the 3d set.
3. **MLIP benchmark-plus-fine-tune** — "out-of-box UMA (oc20 AND oc22 heads) cannot rank rutile-MO₂ OER; task-correction + N-point fine-tune restores Spearman X→Y" is a recognized contribution class (CatBench, Cell Rep. Phys. Sci. 2025, 10.1016/j.xcrp.2025.102847; Loveday 2026) — but only publishable after the oc22 retest rules out the artifact.
4. **"Why the pristine-slab descriptor breaks for 3d rutiles"** — the honest critical study combining our η values + Pourbaix nonexistence + reconstruction/LOM. Safest fallback; inoculates against the exact critique an STS judge would raise.

The heavily-mined space to avoid claiming: 3d dopants in RuO₂/IrO₂ for acidic OER (incl. a 2025 GC-DFT study of our exact 9-dopant set in RuO₂, J. Catal. 10.1016/j.jcat.2025.115963-range) and generic alkaline mixed-oxide screens (Science 2016, 10.1126/science.aaf1525, ~3,500 oxides).

## 7. Proposed revival plan (gated; sized to STS Nov 5, data freeze ~mid-Oct)

- **R0 — Kill the artifact (≤1 box-day, ~$5–15).** `uma-s-1p2p1` + `oc22` re-parity on the existing 4 endmembers with a unified reference chain; pull a few OC22 rutile structures as in-distribution anchors. GATE: Spearman ≥0.8 → UMA usable as-is (skip to R2 screening); 0.5–0.8 → R3 fine-tune; still ~0 → the negative result is real and becomes headline finding #3/#4.
- **R1 — DFT hygiene (~1–2 CPU-box-weeks, parallel with R0).** F1–F3 reanalysis (free); M1 U-sensitivity (Mn, Cr); M2 magnetic protocol incl. AFM β-MnO₂ and OMC-based Co rescue (time-boxed 1 week like last time); M3 dipole + implicit solvation spot-check on Mn.
- **R2 — Stability gate (mostly free).** MP Pourbaix ΔG_pbx for all six endmembers + candidate HEA oxide/oxyhydroxide products; integrate stability into the screening objective (Tran-2024-style multi-criterion).
- **R3 — Fine-tuned screener (single GPU-days).** Convert archived QE trajectories → ASE-LMDB/extxyz; naive fine-tune MACE-OMAT (LR 1e-3, E0 reestimated) and/or UMA-small head-only (LR 4e-4); held-out endmember Spearman ≥0.8 gate; then re-screen the HEA composition space with activity+stability+cost objective; optional CLAM-style AL loop (3–10 DFT/loop).
- **R4 — HEA tier + write.** SQS approximants of top-3 compositions DFT-blessed; oxyhydroxide-termination spot-check for the alkaline story; melt decision at FWM = Frank's call; STS report framing = Frank's call (AI-assistance rules, docs/25).

Rough runway: R0 this week; R1–R2 by mid-Aug; R3 by end-Aug; R4 Sep → data freeze mid-Oct. Fits, with slack.

## 8. Housekeeping carried forward

- Revoke the flagged HF token (frankcai222) — still pending from docs/23 §9; needed anyway before pulling the gated `facebook/UMA` checkpoint with a fresh token.
- Repo is on `thermal-round0` with uncommitted thermal-run edits; this doc should land on a catalysis branch off `main` — branch/commit choice left to Frank.
- Box B (137.175.76.24) already unreachable/destroyed; no live compute.

## 9. Citation ledger (key verified sources)

Foundations: Nørskov 2004 (10.1021/jp047349j) · Rossmeisl 2007 (10.1016/j.jelechem.2006.11.008) · Man 2011 (10.1002/cctc.201000397).
Rutile DFT practice: Xu/Kitchin 2015 (10.1021/jp511426q) · Lim 2021 (10.3389/fenrg.2021.606313, OA) · Swathilakshmi 2023 r2SCAN+U (10.1021/acs.jctc.3c00030) · García-Mota 2012 Co+U (10.1021/jp306303y) · Allen & Watson OMC 2014 (10.1039/C4CP01083C) · Liang AFM-RuO₂ 2022 (10.1021/acs.jpcc.1c08700).
Beyond-CHE: Hansen 2008 Pourbaix (10.1039/b803956a) · Exner G_max 2021/2023/2024 (10.1021/acscatal.0c03865 / 10.1021/acscatal.2c03997 / 10.1021/acs.accounts.4c00048) · Grimaud LOM 2017 (10.1038/nchem.2695) · Melander GC-DFT 2019 (10.1063/1.5047829) · Jones/Piccinin Chem. Rev. 2024 (10.1021/acs.chemrev.4c00171, OA).
Stability: Persson 2012 (10.1103/PhysRevB.85.235438) · Wang SCAN-Pourbaix 2020 (10.1038/s41524-020-00430-3) · Tran OC22 screen 2024 (arXiv:2311.00784 / 10.1039/d4nr01390e).
MLIP: UMA (arXiv:2506.23971; HF `facebook/UMA`) · OC22 (arXiv:2206.08917) · Loveday/López failure modes 2026 (10.1021/acscatal.5c08945, PMC) · CatBench 2025 (10.1016/j.xcrp.2025.102847) · CLAM 2025 (10.1021/jacsau.5c01112) · MACE-catalysis (arXiv:2605.09394) · fine-tune strategies (arXiv:2606.12704) · fairchem docs (fair-chem.github.io, v2.21.0).
Landscape: Lin Cr-Ru 2019 (10.1038/s41467-018-08144-3, PMC) · Zhou/Sargent 2016 (10.1126/science.aaf1525) · Sci. Adv. rutile BO 2025 (10.1126/sciadv.adw0894) · Nat. Mater. perovskite AL 2023 (10.1038/s41563-023-01707-w).
Paywalled-no-OA items flagged for Purdue library pull: Man 2011 numeric tables · Grimaud 2017 · Exner ACS Catal. 2021/2023 · Tripković 2018 (10.1021/acs.jpcc.7b07660) · J. Catal. 2025 GC-DFT doped-RuO₂ · JACS 2024/2025 doped-RuO₂ screens.
