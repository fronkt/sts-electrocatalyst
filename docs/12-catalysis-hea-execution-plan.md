# 12 — Execution Plan: ML-Designed High-Entropy-Alloy OER Electrocatalyst

**The project in one sentence:** Use a machine-learning pipeline (pretrained
oxide-adsorption GNN + multi-objective active learning) to design an
earth-abundant high-entropy alloy that, once melted at Fort Wayne Metals and
electrochemically activated, catalyzes the alkaline oxygen-evolution reaction
(OER) at an overpotential matching or beating a NiFe-LDH benchmark — closing the
full **design → fabricate → measure → beat-baseline** loop that distinguishes STS
Finalists from Scholars.

> This is the detailed spec for shortlist framing **08 #1**. The week-by-week
> checklist lives in [`../tasks/plan-catalysis-hea.md`](../tasks/plan-catalysis-hea.md).
> Execution is still gated on the four logistics answers in
> [`../tasks/todo.md`](../tasks/todo.md) — **do not start the melt request until
> the FWM and potentiostat gates are confirmed.**

---

## 1. Scientific framing

### The problem
Green hydrogen from water electrolysis is bottlenecked at the **anode** by the
sluggish 4-electron OER. The best acidic OER catalysts need **iridium** (scarce,
~$5k/oz); the field's grand challenge is **earth-abundant, scaling-relation-
breaking** anodes. Conventional catalysts are pinned to a volcano plot with a
hard thermodynamic floor of **~0.37 V** overpotential because the binding
energies of *OH, *O, *OOH are linearly correlated and cannot be tuned
independently.

### Why HEAs
High-entropy alloys present a near-continuous distribution of multi-element
active sites, so their adsorption-energy *distributions* can partially decouple
the *OH/*OOH scaling relation that caps ordered surfaces. Under anodic OER
conditions a 3d-transition-metal HEA **self-reconstructs** into a catalytically
active (oxy)hydroxide skin — so the melted alloy is a *precursor*, and the active
phase is the in-situ-formed surface oxide. This reconstruction is a feature, not
a bug, and is a compelling story for judges.

### Hypothesis (sharp, falsifiable)
> An ML-selected, earth-abundant high-entropy composition in the
> **Fe–Co–Ni–(Cr/Mn/Cu)** space will, after activation, exhibit an OER
> overpotential at 10 mA cm⁻² (geometric) **within ±20 mV of, or below, a
> NiFe-LDH benchmark** measured under identical conditions, while containing **zero
> platinum-group metals**; and the ML-predicted activity ranking of the
> synthesized compositions will correlate with the measured ranking
> (Spearman ρ to be reported with error bars).

### What "winning" looks like (define before starting)
| Tier | Concrete result |
|---|---|
| **Scholar floor** | A working ML→fabricate→measure pipeline; ≥3 HEA compositions made and benchmarked vs NiFe-LDH with clean triplicate data + honest ML-vs-experiment correlation, even if none beat the baseline. |
| **Finalist stretch** | At least one ML-designed composition **matches or beats** NiFe-LDH on η@10 mA cm⁻², survives a ≥12 h stability hold, with post-mortem evidence of the reconstructed active phase, AND the ML ranking demonstrably guided the discovery (not luck). |

---

## 2. Locked scope decisions (kill ambiguity)

- **Reaction:** **Alkaline OER in 1 M KOH.** *Not* acidic OER (needs Ir, harsh
  stability), *not* CO₂RR/NRR (product-quantification overhead, NRR artifacts).
- **Baseline:** **NiFe-layered double hydroxide (NiFe-LDH)** — the universally
  accepted earth-abundant alkaline-OER benchmark (~250–300 mV @ 10 mA cm⁻²).
  Synthesized in-house by co-precipitation *and/or* a commercial reference.
- **Composition space:** earth-abundant 3d metals **Fe, Co, Ni, + Cr/Mn/Cu**
  (optionally Al as a leachable porosity former). **No platinum-group metals** —
  the abundance angle is the whole "so what."
- **Primary metric:** **overpotential η at 10 mA cm⁻²** (geometric, iR-corrected,
  vs RHE). **Secondary:** Tafel slope (mV/dec), ECSA-normalized activity,
  chronopotentiometric stability, ML-vs-experiment rank correlation.
- **Candidate budget:** **3–4 compositions in round 1**, **1–2 in round 2**
  (one active-learning iteration). Keep it small — the melt and the
  characterization are the time sinks.
- **Safety/SRC:** KOH (corrosive), possible **Cr(VI) leaching** under anodic
  potential (hazardous-waste handling), metal-dust during electrode prep. Build
  the SRC/Risk-Assessment paperwork in early (mentor-signed).

---

## 3. The ML pipeline (the student's core intellectual contribution)

This is what makes the project *yours*, not a fabrication exercise. Four stages:

**(a) Surface model & descriptor.**
Use a **pretrained oxide-adsorption GNN from the Open Catalyst 2022 (OC22)**
model zoo (e.g., EquiformerV2 / GemNet-OC via the `fairchem`/OCP library) to
predict adsorption free energies of **\*OH, \*O, \*OOH** on candidate
(oxy)hydroxide / spinel / rocksalt surface terminations. Convert to the standard
4-step OER free-energy diagram and compute the **theoretical overpotential**
η_theo = max(ΔG₁…ΔG₄)/e − 1.23 V, using the activity descriptor **ΔG(\*O) −
ΔG(\*OH)**. OC22 is oxide-specific — the right dataset for a reconstructed-oxide
OER surface (OC20 metals are a secondary cross-check).

**(b) Composition → structure enumeration.**
For each candidate composition, build representative special-quasirandom or
small-supercell surface slabs (`pymatgen` + `ASE`), sampling site occupancies to
get an **adsorption-energy distribution**, not a single value. Aggregate (e.g.,
the favorable tail) into a composition-level activity score.

**(c) Phase-stability / single-phase filter.**
A metallic precursor that FWM can melt must be (near) single-phase. Score each
composition with **empirical HEA formability rules** — valence-electron
concentration (VEC), atomic-size mismatch δ, mixing enthalpy ΔH_mix (Miedema),
ΔS_mix, and the Ω parameter — and, if Thermo-Calc/`pycalphad` access exists, a
CALPHAD single-phase check. Compositions predicted to be multi-phase or brittle
are down-weighted.

**(d) Multi-objective active learning.**
Optimize over the composition simplex with **multi-objective Bayesian
optimization** (`Ax`/`BoTorch`, qNEHVI acquisition) trading off: predicted
activity (↑), earth-abundance/cost (↑), single-phase formability (↑). Round 1
proposes 3–4 compositions from the ML prior. After the measured η values come
back, **retrain/condition the surrogate on real data** and propose 1–2 refined
compositions for round 2 — this closed AL loop, with experimental feedback, is
the methodological novelty.

**Honest framing for the paper/judges:** ML here is a **screening prior that
ranks where to look**, not an oracle — SRO, reconstruction, and surface
restructuring mean the predicted η is approximate. The project's contribution is
the *calibrated* ML-guided search plus the experimental confirmation, reported
with the correlation and its failure modes.

### Compute & software stack
| Purpose | Tool |
|---|---|
| Pretrained OER descriptors | `fairchem` (OCP) — OC22 EquiformerV2 / GemNet-OC |
| Structures / slabs / adsorbates | `pymatgen`, `ASE` |
| Phase-stability features | empirical HEA rules + `pycalphad` (or Thermo-Calc if available) |
| Active learning | `Ax` / `BoTorch` (multi-objective qNEHVI) |
| Compute | Vast.ai GPU (cu128 index per workflow notes) or Purdue HPC |

---

## 4. Fabrication plan (Fort Wayne Metals — the unfair advantage)

- **Route:** arc-melt / vacuum-induction button or small ingot of each round-1
  composition (3–4), homogenization anneal (e.g., ~1000–1100 °C, time per
  composition) to dissolve segregation. Wire-draw only if a high-surface-area
  geometry is wanted; bulk button is simpler for an electrode.
- **Deliverable from FWM:** small dense ingots/coupons + nominal-composition
  certificate. **FWM provides a fabrication *service*; the composition choices
  and the science are the student's** (important for STS independence).
- **Critical-path warning:** the melt + anneal + delivery is the **longest lead
  item.** Submit the round-1 request in **Week 1**, the moment the ML round-1
  shortlist exists (or even a provisional list, refined before melting).
- **Electrode prep (at Purdue):** cut/mount coupons, polish to a defined finish,
  define geometric area (mask/epoxy), electrical contact. Alternative: powderize
  + drop-cast ink onto glassy carbon / Ni foam if bulk-electrode area is too
  small.

---

## 5. Characterization & electrochemistry (Purdue)

**Structural / compositional (confirm what FWM made):**
- **XRD** — single-phase vs multi-phase, lattice parameter.
- **SEM-EDS** — homogeneity + actual vs nominal composition (HEAs segregate).
- Optional **XPS** pre/post-OER — surface oxidation-state / reconstruction
  evidence.

**Electrochemistry (the heart of the result):**
- **Cell:** 3-electrode, 1 M KOH, Hg/HgO reference (+ RHE calibration), Pt or
  graphite counter (graphite preferred to avoid Pt redeposition artifacts).
- **Reference conversion:** E_RHE = E_Hg/HgO + 0.098 + 0.059·pH.
- **Activation:** cyclic voltammetry conditioning to form the active
  (oxy)hydroxide before benchmarking.
- **Measurements (per sample, in triplicate for error bars):**
  - **LSV** (iR-corrected, 85–95% from EIS R_s) → **η @ 10 mA cm⁻²**.
  - **Tafel slope** from the LSV/stepped data (mechanistic signature).
  - **ECSA** via double-layer capacitance (C_dl) → intrinsic vs geometric
    activity (separates "more area" from "better sites").
  - **EIS** at the OER onset → charge-transfer resistance.
  - **Stability:** chronopotentiometry @ 10 (and/or 100) mA cm⁻² for **≥12 h**
    (24–100 h if time allows); report η drift.
  - **Post-mortem** XRD/SEM-EDS(/XPS) → document the reconstructed active phase.
- **Controls:** bare glassy carbon, NiFe-LDH baseline, and ≥1 binary/ternary
  sub-alloy for ablation ("does the *high-entropy* part actually help?").

---

## 6. Risk register & mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| **FWM melt slips the schedule** (critical path) | Med–High | Submit Week 1; provisional compositions; reduce round-1 count to 3; have a powder/co-precipitation fallback to make an oxide directly if metal slips entirely. |
| Potentiostat/instrument booking delay | Med | Book in Week 0–1; reserve recurring slots; cross-train on the baseline first. |
| HEA is multi-phase / brittle / segregated | Med | Phase-stability filter up front; XRD/EDS gate before testing; anneal; pick more forgiving compositions (Cantor-adjacent). |
| ML prediction doesn't correlate with experiment | Med | This is still a *publishable, honest* result (calibration study) — the Scholar floor doesn't depend on the model being right, only rigorous. |
| Reproducibility / iR / RHE-calibration errors | Med | Triplicate; documented iR correction; fresh reference calibration each session; report standard deviations. |
| Cr(VI) leaching hazard | Low–Med | SRC risk assessment; hazardous-waste handling; consider Cr-free variant (Fe-Co-Ni-Mn-Cu). |
| No time for round-2 melt | Med | Present round-1 experiment + round-2 as a *computational* prediction with the AL loop demonstrated; still a complete story. |
| Scope creep (HER + OER + CO₂RR) | High (self-inflicted) | **One reaction, one baseline, one metric.** Locked in §2. |

---

## 7. STS ~20-page paper outline (write as you go)

1. **Abstract** (½ pg)
2. **Introduction** — green H₂, OER bottleneck, Ir scarcity, scaling-relation
   floor, HEA promise + self-reconstruction, the gap, your hypothesis. (~2.5 pg)
3. **Objectives & hypothesis** (½ pg)
4. **Methods** — (a) ML pipeline: data (OC22), model, descriptor, slab sampling,
   phase-stability filter, active learning; (b) alloy fabrication; (c)
   characterization; (d) electrochemistry protocol + controls. (~5 pg)
5. **Results** — ML predictions/ranking; structure (XRD/EDS); OER performance
   (η, Tafel, ECSA, EIS); stability + post-mortem reconstruction;
   **ML-vs-experiment correlation**. (~6 pg, figure-heavy)
6. **Discussion** — why it works (scaling-relation circumvention, reconstruction),
   ML calibration honesty + failure modes, limitations. (~2.5 pg)
7. **Conclusion & future work** (½ pg)
8. **References** (not counted toward the limit per current rules — confirm).

Figure plan: (F1) concept schematic; (F2) ML pipeline + predicted volcano/ranking;
(F3) XRD/SEM-EDS; (F4) LSV overpotentials vs baseline; (F5) Tafel + ECSA; (F6)
stability + post-mortem; (F7) predicted-vs-measured correlation.

---

## 8. Independence & sponsor notes (STS judging)

- **Yours (defend in the interview):** the hypothesis, the ML pipeline design,
  the composition-selection logic, the active-learning loop, the data analysis,
  the interpretation.
- **Service/access (acknowledge, don't claim as your science):** FWM's melting,
  the mentor's lab/instrument access, any technician-run measurement.
- Keep a **dated lab notebook / git history** of the ML code and decisions — it
  is the evidence of independent intellectual contribution.

---

## 9. Rough budget

| Item | Est. |
|---|---|
| GC electrodes, Hg/HgO reference, Nafion, KOH, Ni foam, NiFe precursors, consumables | ~$500–1,500 |
| Compute (Vast.ai GPU, a few hundred GPU-hr) | ~$100–300 |
| Alloy melting (FWM) | in-kind / service |
| Characterization (Purdue) | in-kind / facility access |

---

## 10. Go / no-go checkpoints

- **End Week 2:** FWM melt request submitted + accepted; potentiostat booked; ML
  round-1 shortlist exists. *If not → escalate or fall back to a co-precipitated
  HE-oxide route that needs no melt.*
- **End Week 6:** samples in hand, single-phase confirmed by XRD. *If multi-phase
  → re-anneal or down-select.*
- **End Week 9:** round-1 OER data complete with error bars. *Go/no-go on round-2
  melt vs computational round-2.*
- **Early October (Week 14):** **DATA FREEZE.** No new experiments — write.
