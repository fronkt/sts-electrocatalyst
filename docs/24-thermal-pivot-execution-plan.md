# 24 — Thermal Pivot: Execution Plan (ML-Designed High-Dissipation Conductor)

> **Decision record + full execution plan** for the pivot away from the HEA-OER
> electrocatalyst (docs/12–23, now **parked**, §9) toward the thermal-dissipation
> lane, decided by the entrant **2026-07-01**. Grounded in two deep research
> passes (2024–2026 literature; sources §11). This document is to the thermal
> project what docs/12 + docs/16 were to catalysis.

| | |
|---|---|
| **Working title** | *Machine-Learning Co-Design of Composition and Processing for High-Strength, High-Dissipation Copper Conductors for AI Data-Center Power Delivery — Fabricated and Measured by the Entrant* |
| **One-line pitch** | AI compute is bottlenecked by getting power in and heat out; a physics-based κ oracle + Bayesian optimization designs Cu-Fe(-X) compositions *and* their wire-drawing/anneal schedules for that power-thermal path; the entrant melts, draws, and measures them at Fort Wayne Metals — targeting Cu-Nb-class performance at iron prices. |
| **Two anchor spikes** | **(1) Computational discovery:** a physics-decomposed κ(x) oracle (fine-tuned MLIP thermal MD + first-principles alloy resistivity) driving multi-objective BO — an architecture with no published precedent. **(2) Synthesis + testing:** a 100 % in-house melt → draw → anneal → measure loop at FWM, ~20–40 compositions over 2 active-learning rounds. |
| **Deadline chain** | Data freeze **early Oct 2026** → paper Oct → submit **Nov 5 2026**. Effective runway from today: **~13 weeks**. |

---

## 1. The application driver, and the physics reality check (why the objective is a Pareto front, not "highest κ")

**The application driver — AI compute.** The entrant's motivating problem is heat
in large AI datacenters. A GB200-class rack draws >100 kW; accelerator packages
exceed 1 kW each; and the industry is moving rack power to **800 VDC distribution
precisely because I²R heating in busbars, cables, and connectors has become a
first-order energy loss and cooling burden**. Every conductor in that power path
runs hot while carrying mechanical load — clamping stress, electromagnetic forces,
vibration, thermal-cycling fatigue — and pure copper softens and creeps under
exactly those conditions. The material question this project attacks is therefore
*the dissipation capacity of the datacenter power path per unit strength*: how
much of copper's conductivity (and, via Wiedemann-Franz, its thermal dissipation)
can be kept in a conductor strong enough to survive that environment. The same
FOM governs EV hairpin windings, high-field magnet coils, and rocket-nozzle
liners — cited as secondary markets, with the AI-infrastructure framing as the
paper's motivation section.

The naive goal — *the highest-thermal-conductivity material* — is *closed* for any
fabrication route this project has:

- **Pure Cu (~400 W/m·K) is the ceiling of meltable metals** (Ag ~429 is the only
  meltable thing above it). In Cu, electrons carry ~99 % of heat; **every solute
  atom scatters them** (Nordheim rule), so any *alloying* strictly lowers κ. You
  cannot "discover" a castable alloy with κ > Cu — this is physics, not a data gap.
- The genuinely higher-κ champions — diamond (~2000), c-BAs (~1300, §docs/04),
  graphene — are **not fabricable** by any route the entrant has.
- The commercial "heat-spreader" class (Cu-W, Cu-Mo, AlSiC) are **immiscible
  powder-metallurgy pseudo-alloys**: Cu boils before W melts. Arc/VIM **cannot
  fabricate the baseline class** — the T1 framing in docs/06 is hereby **struck**.
- Precedent confirms the trap: no "high-κ material" project cracked STS Top 40 in
  2021–2026 (docs/01 ceiling analysis).

**The open problem** is that pure Cu is mechanically inadequate exactly where
dissipation matters most — the datacenter power path above, plus EV hairpin
windings, high-field magnet coils, rocket-nozzle liners (NASA GRCop), fusion
first-wall conductors. These
applications need **strength ≥3× hard Cu while keeping most of its conductivity**.
That trade-off — the **strength–conductivity Pareto front** — is a real, active
research frontier with named state-of-the-art anchors, and *moving that front* is
the honest, judge-defensible version of "highest energy dissipation."

> **Pre-empted judge question ("why not just use copper?"):** because at 400 MPa
> copper is at its strength limit and softens above ~200 °C; the entire conductor
> industry exists to buy back strength without losing κ. The project's FOM makes
> this quantitative from slide 1.

## 2. Objective, baselines, and the win condition

**Design space:** deformation-processed Cu-Fe(-X) in-situ metal-metal composites
(X ∈ {Ag, Cr, Zr, P, Mg} microalloying, ≤~2 at.%), plus the thermomechanical
schedule: drawing/rolling true strain η and intermediate-anneal (T, t) steps.
Cu-Fe is explicitly the low-cost alternative to Cu-Nb (Fe ≈ 1/50 the price of Nb).

**Figure of merit:** the (σ_el [%IACS], UTS [MPa]) Pareto plot with named anchors,
plus the scalar **σ×UTS product**; thermal headline via **κ = Smith-Palmer(σ)**
(±5–10 % for Cu alloys, §5) with direct LFA validation on finalists.

| Anchor (measured/published) | UTS (MPa) | %IACS | σ×UTS | κ_WF (W/m·K) |
|---|---|---|---|---|
| Hard-drawn pure Cu | ~430 | ~97 | ~41,700 | ~385 |
| **C18150 Cu-Cr-Zr (commercial)** | 450–545 | 80–90 | ~42,500 | ~320–350 |
| Best published Cu-14Fe | 907 | 54.3 | ~49,000 | ~215 |
| Cu-Nb microcomposite (SOTA, $$$) | 1000–1200 | 60–65 | ~65,000 | ~240–255 |
| Cu-24Ag (SOTA, $$$) | 1500 | 65 | ~97,500 | ~255 |

**Win condition (Finalist-grade):** any entrant-made Cu-Fe(-X) point **above the
published Cu-Fe Pareto** — concretely **≥700 MPa at ≥60 %IACS** (κ_WF ≈ 235–250
W/m·K), i.e., Cu-Nb-class dissipation-per-strength at ~1/50 the raw-material cost.
**Scholar floor:** the validated oracle + ≥10 alloys measured with an honest
predicted-vs-measured calibration (Spearman ρ + CI), even if no point beats the front.

**Hypothesis (sharp, falsifiable — the docs/16 §3 pattern):**

> A physics-decomposed thermal-transport oracle (κ_e from first-principles alloy
> resistivity + κ_L from fine-tuned MLIP thermal MD), combined with batch
> multi-objective Bayesian optimization over Cu-Fe(-X) composition *and*
> thermomechanical schedule, will (a) locate a composition/schedule whose measured
> (UTS, %IACS) lies above the published Cu-Fe Pareto front, and (b) rank the
> synthesized compositions' conductivities in agreement with measurement
> (**Spearman ρ reported with CI**) — with all predictions **frozen in git before
> each melt round** (the docs/15 §2 protocol, ported).

## 3. Spike 1 — the computational discovery engine

The 2024–26 SOTA pieces all exist separately; **no published work assembles them
into one experimentally-closed loop for thermal-management alloys** (research pass
§11; closest precedents — Rao *Science* 2022 Invar-HEA loop [CTE, not κ]; BIRDSHOT
batch-BO [mechanical, not thermal]; every Cu-alloy ML paper uses
literature-regression oracles, not physics simulation). That assembly is the
novelty claim, and it decomposes exactly like the catalysis funnel did:

```
proposer               oracle (physics, entrant-run)                 confirm (real)
qNEHVI batch BO   →    κ_e: KKR-CPA residual ρ (MuST) → WF       →   melt/draw/anneal
over (x, schedule)     κ_L: fine-tuned NEP + GPUMD HNEMD             σ (4-pt), UTS, HV
                       strength: lit-calibrated surrogate + HV        XRD/SEM/EDS @ FWM
                  ◄──────────── retrain on measured (σ, UTS) ────────────┘
```

1. **Electronic channel (dominant, ~90 %+ of κ):** KKR-CPA residual resistivity
   across the composition grid via **MuST** (open-source, CPU, minutes–hours per
   composition) + Matthiessen's rule for the phonon-limited host term → κ_e via
   Wiedemann-Franz. Calibrated against the entrant's own 4-point measurements —
   FWM wire makes ρ measurement essentially free and precise. *(A learned
   ρ(composition) model for 3d-metal solid solutions, trained on CPA + own data,
   is itself a small publishable gap.)*
2. **Lattice channel:** start from a universal NEP (NEP89/UNEP-v1 — ~10⁷
   atom-steps/s on the 5090; MACE-class is 10³–10⁴× too slow for this), fine-tune
   on **~500–1500 QE frames** (SQS + perturbed-MD cells of the Cu-Fe(-X) family —
   the QE/Vast/SSSP workflow from docs/22–23 ports wholesale), then **HNEMD in
   GPUMD** (32k+ atoms, ~10 ns; ~10 GPU-h/composition; spectral quantum correction;
   driving-force + size convergence documented). Sanity anchors: pure-Cu phonon
   dispersion + published UNEP-v1 metal κ values.
   **Known trap, stated up front:** raw foundation MLIPs **underestimate κ by
   ~50 % median** (PES softening, arXiv:2408.00755); few-frame fine-tuning restores
   2–7 % — the before/after is itself a figure.
3. **The guaranteed methods deliverable — a "metallic κ_SRME":** the κ_SRME
   benchmark in Matbench Discovery covers **insulators only**; no metallic-alloy κ
   benchmark exists. Benchmarking foundation models (NEP89, MACE-MP, MatterSim,
   eSEN) vs the fine-tuned NEP vs **the entrant's own measured κ/ρ** on the 5–10
   alloys actually melted is citable methods work **even if every discovered alloy
   is unremarkable** — this replaces docs/19–21 as the project's built-in parachute.
4. **Optimization layer:** batch multi-objective BO (**qNEHVI**, BoTorch/Ax,
   BIRDSHOT-style) over composition × schedule; batches of 5–8 sized to FWM melt
   throughput; 2 experimental rounds. Strength comes from a literature-calibrated
   surrogate (Hall-Petch/filament-spacing scaling for DPMMCs) refined on round-0
   hardness — **the oracle does κ from physics; strength is learned from the loop.**
   *(This split is honest and defensible: strength of a drawn composite is
   processing-history physics no simulation reaches in 13 weeks.)*

**What is deliberately out of scope (traps):** Fe-rich/Invar-type low-CTE targets —
magnetovolume physics that spin-free MLIPs and standard QHA **cannot** capture
(CTE, if reported at all, is *measured*, never computed); EPW/Perturbo-class
phonon-limited transport (ordered crystals only); phonon–electron scattering in MD
(argue smallness in concentrated alloys, cite the UNEP-v1 metals paper);
classical-statistics caveat (minor at 300 K: Cu θ_D ≈ 343 K, documented).

**Compute budget (fits local 5090 + modest Vast):** QE fine-tune set 300–600 GPU-h
(or CPU-equivalent, ~$150–400) · NEP training 20–50 GPU-h · HNEMD 40–60 comps ×
~10 GPU-h ≈ 400–600 GPU-h · MuST CPA sweep: CPU-days (~$50; **the already-rented
15-vCPU CPU box can be repurposed for exactly this**) · QHA/NPT spot checks ~40
GPU-h. **Total ≈ 1000–1300 GPU-h ≈ continuous local 5090 + $400–900 Vast.**

## 4. Spike 2 — the synthesis + testing loop (100 % in-house)

The decisive logistics upgrade over both the catalysis plan and old T1: **every
measurement of the primary FOM happens at FWM** — no Purdue booking on the
critical path (the catalysis plan's #1 live risk, docs/16 §10).

- **Melt:** arc-melt 10–20 g Cu-Fe(-X) buttons (water-cooled hearth, Ti getter —
  routine; Cu-Fe is fully castable, unlike Cu-W); VIM for larger heats
  (CuCrZr-class VIM is standard industrial practice; phosphor-copper deoxidation
  0.02–0.05 %, O < 5 ppm). **Confirm week 1:** Cu feedstock (OFHC) + Fe/Ag/Cr/Zr
  master alloys on site.
- **Process:** the FWM crown jewel — cold roll/swage → wire draw to true strain
  η ≈ 2–5 with **intermediate anneals as design variables** (a 2025 result shows
  anneal schedules can raise Cu-Fe strength *and* conductivity simultaneously —
  the schedule dimension is live and under-optimized; it is ML's second axis).
- **Measure (all in-house):** 4-point wire resistivity (**ASTM B193**, <1 % error)
  and/or eddy-current %IACS; tensile UTS (wire tensile is FWM bread-and-butter);
  hardness; XRD (phases), SEM/EDS (Fe filament morphology vs η — the microstructure
  panel figure). **Screening proxy loop:** hardness + eddy-current on cold-rolled
  button slices → **3–6 compositions/day**; full melt→draw→anneal→test route
  ~1–2 weeks/batch for finalists.
- **Round structure:** round 0 (calibration, ~6–8 melts: pure-Cu control, C18150
  clone control, Cu-{2,6,10,14}Fe spine, 1–2 microalloyed) → round 1 (BO batch,
  ~8–10) → round 2 (BO batch incl. schedule co-design, ~8–10) → **3–6 finalists
  through the full wire route**. ~20–40 compositions total in ~8 weeks — matches
  published throughput for arc-button campaigns.
- **External validation (nice-to-have, not critical-path):** LFA thermal
  diffusivity at Purdue on 2–3 finalists + both controls (button → 10/12.7 mm ×
  1–3 mm disc works) to pin the Smith-Palmer κ band; dilatometry CTE as a
  packaging aside. Book early, but **nothing blocks on it**.

## 5. Measurement honesty (the κ story)

κ is *reported*, not just implied: **κ = L·T·σ + C (Smith-Palmer)**, the standard
alloy-class-calibrated Wiedemann-Franz form, accurate to **5–10 % for Cu alloys**
(electron-dominated conduction). The paper states the band, cites the validation
literature, and **anchors it with direct LFA on 2–3 samples** — this σ→κ +
spot-validation package is publication-grade practice, not a shortcut. Every κ
claim carries error bars from (σ error ⊕ Smith-Palmer band ⊕ LFA anchor residual).

## 6. Week-by-week plan (2026-07-01 → Nov 5)

| Wk | Dates | Compute spike | Synthesis spike | Gate |
|---|---|---|---|---|
| 1 | Jul 1–7 | Lock plan; assemble literature Pareto DB (anchors §2); MuST install on CPU box | **Confirm FWM Cu feedstock + melt slot; confirm eddy-current/%IACS + wire tensile SOPs**; order feedstock | **G0: FWM confirms Cu capability** |
| 2–3 | Jul 8–21 | KKR-CPA sweep v1 (κ_e grid); QE fine-tune data gen starts (SQS cells, Vast); strength surrogate v0 from lit | **Round-0 melts** (~6–8: controls + Cu-Fe spine); ρ SOP validated vs handbook Cu; hardness/eddy proxy loop shakedown | G1: measured ρ(pure Cu) within 2 % of handbook |
| 3–5 | Jul 15–Aug 4 | NEP fine-tune + validation (Cu phonons, PES-softening before/after); first HNEMD κ_L batch | Round-0 full characterization; XRD/SEM baseline | G2: fine-tuned NEP reproduces Cu κ_L & published UNEP metal values |
| 5–6 | Aug 3–14 | **Oracle v1 frozen** → qNEHVI **round-1 batch (frozen in git)** | **Round-1 melts** (~8–10); begin draw+anneal matrix on round-0 best | G3: predictions committed before melt |
| 7–9 | Aug 17–Sep 4 | Retrain on round-1 (σ, UTS); schedule co-design enters the design space; **round-2 batch frozen** | **Round-2 melts**; full wire route on 3–6 finalists | G4: round-2 in the furnace by Sep 1 |
| 9–11 | Sep 7–25 | Metallic-κ benchmark chapter (foundation vs fine-tuned vs measured); calibration stats (ρ, CI) | Finalist tensile/σ; **LFA validation trip** (booked earlier); SEM filament-vs-η panel | G5: Pareto plot with own points |
| 12 | Sep 28–Oct 2 | **DATA FREEZE (early Oct — hard, per docs/01)** | | |
| 13–17 | Oct | ≤20-page paper + essays (generalist-legible); figures §8 | | Nov 5 submit |

**Slack analysis:** the two spikes are parallel by construction — melts never wait
on compute (round-0 is heuristic-designed), and compute never waits on melts
(benchmark chapter is melt-independent). Single-point-of-failure = FWM Cu
capability, hence G0 in week 1; fallback if FWM cannot source Cu quickly is
starting the spine from commercial Cu-Fe feedstock and reserving custom melts for
rounds 1–2.

## 7. STS positioning

| Tier | What it takes | Odds read |
|---|---|---|
| **Scholar floor** | Working oracle + ≥10 entrant-made alloys measured vs named baselines + honest ρ calibration — even if the Pareto front doesn't move | Very safe: the lane is empty (no ML-alloy or thermal-alloy entry appeared at STS/ISEF 2023–26 at all) |
| **Finalist stretch** | A point above the published Cu-Fe Pareto (≥700 MPa @ ≥60 %IACS) **and** the frozen-prediction record showing ML guided it; the metallic-κ benchmark as the methods spine | Real: fastest in-house loop of any lane considered, industrial-scale personal fabrication story no other entrant can tell |

- **Structural difference from every prior STS thermal entry:** they made a
  composite and measured κ; this project ships a *discovery method* (physics
  oracle + BO), an *industrial process co-design*, and a *benchmark contribution*,
  with κ as the application story — the docs/01 prescription for breaking the
  thermal ceiling, executed.
- **Routing:** materials science / engineering-materials category, framed as an
  alloy discovery powered by ML (the Rezaei mis-routing lesson, docs/10).
- **Differentiate in the paper:** Rao *Science* 2022 (closed loop, but generative
  + CTE objective + national-lab resources), BIRDSHOT (batch BO, mechanical
  objectives), Cu-alloy ML papers (regression oracles, no physics simulation in
  the loop, no processing co-design). The novelty sentence: *"first
  experimentally-closed discovery loop whose thermal-transport oracle is computed
  from physics (CPA electronic + MLIP-MD lattice) rather than regressed from
  literature data, and the first to co-design composition with the wire-drawing/
  anneal schedule."*
- **Independence story unchanged** from docs/16 §9 — entrant conceives, computes,
  melts, draws, measures; mentors supervise; self-funded; dated git history.
- **Three honest outcomes, all reportable** (the docs/15 §6 pattern): oracle ranks
  well → ML-guided discovery; oracle misranks but a Pareto point lands → useful
  material + calibration lesson; neither → rigorous negative result + the
  benchmark chapter stands on its own.

## 8. Deliverables & figures

1. **F1 — Pareto plot:** (UTS, %IACS) with all named anchors + entrant's points,
   κ_WF right-axis; the headline figure.
2. **F2 — oracle parity:** predicted vs measured σ (and κ via LFA anchors), ρ + CI;
   round-coloured to show AL improvement.
3. **F3 — metallic-κ benchmark:** foundation models vs fine-tuned NEP vs
   experiment (the κ_SRME-for-metals table/figure).
4. **F4 — PES-softening before/after fine-tune** (phonon DOS + κ_L shift).
5. **F5 — microstructure:** SEM of Fe filament refinement vs draw strain, tied to
   the strength model.
6. **F6 — AL trajectory:** hypervolume / best-point vs round, with frozen-prediction
   timestamps.
7. Code + data: `src/thermo/` (oracle, BO, analysis), `runs/` (HNEMD/CPA logs),
   measurement CSVs, all PR'd with the established provenance discipline.

## 9. Disposition of the catalysis project (docs/12–23)

**Parked, not deleted** — it is 100 % preserved in git and remains a substantial
standalone artifact (round-1 UMA screen incl. the ρ=−0.09 bias catch, the QE tier
with locked convergence, the CrO₂ UMA↔DFT parity anchor showing a 0.89 V
disagreement). Actions:

- **Do not launch** the 20-job endmember DFT queue (saves 2–3 box-days); merge or
  close **PR #15** (dft-cro2-checkpoint) to preserve the CrO₂ anchor on main.
- **Repurpose the rented 15-vCPU CPU box for MuST KKR-CPA** (it is billing either
  way) or tear it down until week 2.
- The FWM melt slot reserved for the HEA set (~this week) **transfers to round-0
  Cu-Fe melts** — same furnace, different feedstock (G0 confirms).
- Revoke the HF token (frankcai222) — still pending from docs/23 §9.
- If the thermal loop stalls catastrophically before ~Sep 1, un-parking catalysis
  (whose compute is done and only needs melts + EC) remains a last-resort fallback,
  gated on the potentiostat that was its original weakness.

## 10. Risk register

| Risk | L | Impact | Mitigation |
|---|---|---|---|
| FWM can't source/melt Cu quickly (G0) | low | slips round-0 | Week-1 confirm; commercial Cu-Fe feedstock fallback; arc buttons need only ~10–20 g |
| Oxygen pickup in Cu melts → κ artefacts | med | noisy σ | Ti getter (arc), phosphor-Cu deoxidation (VIM), O-insensitive eddy-current screening + density checks |
| Fine-tuned NEP still misses alloy κ_L | med | oracle degrades to κ_e-only | κ_e dominates (~90 %+); report κ_L with UQ; benchmark chapter documents it either way |
| WF/Smith-Palmer challenged by judges | med | credibility | LFA anchors on finalists + stated ±5–10 % band + citations; σ itself is exact |
| Strength surrogate wrong early | high | round-1 batch suboptimal | Round-0 hardness recalibrates before round-1 freeze; BO is robust to noisy objectives |
| Draw/anneal schedule space too big | med | unfocused round 2 | Constrain to 3 anneal temps × 2 times × 2 strains around FWM's standard practice |
| Time: 2 AL rounds don't fit | med | one round only | One round still satisfies the hypothesis; round 2 is upside |
| "Engineering, not science" perception | med | judging | The oracle physics + benchmark + calibration statistics are the science; §7 framing |

## 11. Key sources (research passes, 2026-07-01)

**Computational:** UNEP-v1 metals κ via HNEMD ([arXiv:2505.13179](https://arxiv.org/html/2505.13179), [Nat. Commun. 2024](https://www.nature.com/articles/s41467-024-54554-x)) · foundation-MLIP κ underestimation + few-frame fine-tune ([arXiv:2408.00755](https://arxiv.org/html/2408.00755v2)) · NEP89 ([arXiv:2504.21286](https://arxiv.org/html/2504.21286v1)) · GPUMD 4.0 + HNEMD tutorial ([arXiv:2401.16249](https://arxiv.org/html/2401.16249v2)) · MuST KKR-CPA ([github.com/mstsuite/MuST](https://github.com/mstsuite/MuST)) · WF validity ([APL 2024](https://pubs.aip.org/aip/apl/article/125/25/252201/3326062)) · Rao Invar-HEA loop ([Science 2022](https://www.science.org/doi/10.1126/science.abo4940)) · BIRDSHOT ([arXiv:2405.08900](https://arxiv.org/pdf/2405.08900)) · MFBO best practices ([Nat. Comput. Sci. 2025](https://www.nature.com/articles/s43588-025-00822-9)).
**Materials/experimental:** Cu-Fe DPMMC reviews ([Sage 2022](https://journals.sagepub.com/doi/10.1177/14644207221090534), [JOM 2025](https://link.springer.com/article/10.1007/s11837-025-07815-z)) · Cu-20Fe anneal-schedule result ([JISR Int. 2025](https://link.springer.com/article/10.1007/s42243-025-01507-3)) · Cu-Nb ([J. Appl. Phys. 2022](https://pubs.aip.org/aip/jap/article/132/4/045105/2837320)) · Cu-Ag high-field wires ([Acta Mater.](https://www.sciencedirect.com/science/article/abs/pii/S1359645496002480)) · Smith-Palmer κ–σ ([orig.](https://www.sciencedirect.com/science/article/abs/pii/0017931065900864), [Klemens & Williams](https://journals.sagepub.com/doi/abs/10.1179/imtr.1986.31.1.197)) · ASTM B193 · Cu-alloy ML/BO prior art ([Mater. Res. Lett. 2024](https://www.tandfonline.com/doi/full/10.1080/21663831.2024.2424933), [Sci. Data 2025](https://www.nature.com/articles/s41597-025-06295-9)) · W-Cu casting impossibility ([MDPI 2025](https://www.mdpi.com/2075-4701/15/2/197)) · STS/ISEF precedent scan (docs/01, docs/10; STS 2025/2026 finalist lists).
