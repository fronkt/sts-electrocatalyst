# 15 — Round-1 melt & test plan (FWM melt → Purdue OER)

Operationalizes the execution plan ([docs/12](12-catalysis-hea-execution-plan.md)
§4–5) for the **actual ML round-1 shortlist** ([docs/13](13-round1-uma-results.md)).
This is the concrete protocol for the first make→measure loop and **freezes the ML
predictions** so the ML-vs-experiment correlation (the STS contribution) is honest.

## 1. What to melt (and why these)

The pipeline's diverse shortlist is all *predicted-good* (η 0.78–1.15 V). A
correlation study needs **dynamic range**, so the round-1 melt set deliberately adds
a predicted-poor anchor and an ablation alloy:

| # | Composition (at.%) | Role | Frozen ML rank | Pred. best-site η (V) | Pred. descriptor (eV) |
|---|---|---|---|---|---|
| 1 | **Fe32Ni17Co34Mn18** | headline (Cr-free, nearest apex) | 1 | 0.78 | 1.75 |
| 2 | Cr21Ni24Co15Cu6Fe33 | shortlist (diverse) | 4 | 1.03 | 1.38 |
| 3 | Cr8Fe34Mn9Ni23Co27 | shortlist (diverse) | 5 | 1.15 | 2.38 |
| 4 | Co24Fe24Ni35Mn17 | shortlist (diverse) | 8 | 1.15 | 2.34 |
| 5 | Cr19Co28Fe25Ni28 | **predicted-poor anchor** (correlation range) | 12 (last) | 2.96 | −0.57 |
| 6 | FeCoNi (equiatomic) | **ablation** — drop the HEA aspect | n/a | — | — |

Controls (not melted): **NiFe-LDH** baseline (co-precipitation or commercial) and
**bare glassy carbon**. The melt set spans predicted η 0.78→2.96 V across 5 HEAs +
1 ternary, so the predicted-vs-measured rank correlation has real dynamic range.

> **Pre-melt gate (do this first):** the heuristic prior was found *uncorrelated*
> with rutile (ρ=−0.09), so the shortlist is "best of the 12 evaluated," not "best
> of all single-phase." Strongly consider the **broader rutile sweep**
> ([docs/14](14-compute-log.md) §4) before locking the melt set — a better candidate
> may sit outside the evaluated 12.

## 2. Freeze the prediction (independence evidence)

Before any melt, commit this table to git (done here) so the **predicted ranking is
timestamped** and cannot be retrofitted to the data. The correlation in §6 compares
*this frozen ranking* to measured η. Keep a dated lab notebook alongside (docs/12 §8).

## 3. Fabrication (Fort Wayne Metals — student-run)

Per docs/12 §4. For each of the 5 HEAs + the ternary:
1. **Weigh** elemental feedstock to target at.% (convert to mass via molar mass).
   **Mn over-charge ~3–5 %**: Mn evaporates during arc melting — verify final
   composition by EDS, not nominal.
2. **Arc/button melt** (round-1, fast), flip + remelt ≥3× for homogeneity.
3. **Homogenization anneal** ~1000–1100 °C (dissolve dendritic segregation).
4. **On-site gate (FWM, no travel):** **XRD** (single-phase FCC? — all 6 predicted
   FCC) + **SEM-EDS** (actual vs nominal; HEAs segregate). *Multi-phase → re-anneal
   or drop that composition before spending an EC slot.*
5. **Electrode:** cut/mount coupon, polish to defined finish, mask a known geometric
   area (epoxy), electrical contact. Fallback: powderize → ink on glassy carbon / Ni
   foam if bulk area is too small.

## 4. Electrochemistry (Purdue — the result)

Per docs/12 §5. 3-electrode, **1 M KOH**, Hg/HgO ref (+ RHE calibration), graphite
counter (avoid Pt redeposition). E_RHE = E_Hg/HgO + 0.098 + 0.059·pH.

Per sample, **in triplicate** (fresh electrode each):
- **Activate**: CV conditioning to form the active (oxy)hydroxide skin.
- **LSV** (iR-corrected, 85–95 % from EIS R_s) → **η @ 10 mA cm⁻²** (primary metric).
- **Tafel slope** (mechanism); **ECSA** via C_dl (intrinsic vs geometric); **EIS** at onset.
- **Stability**: chronopotentiometry @ 10 mA cm⁻², **≥12 h** on the round-1 best; report η drift.
- **Post-mortem** XRD/SEM-EDS (±XPS) → document the reconstructed active phase.

## 5. Controls & ablation (does the *high-entropy* part help?)

- **NiFe-LDH** + **bare GC** every session (benchmark + blank).
- **FeCoNi ternary** vs the Mn/Cr-containing HEAs: isolates whether multi-element
  disorder actually lowers η (the scaling-relation-breaking hypothesis).

## 6. The contribution — ML-vs-experiment correlation

For the 5 HEAs (+ ternary if predicted): plot **measured η@10** vs **frozen
predicted best-site η**, report **Spearman ρ and Pearson r with error bars**
(triplicate std). Three honest outcomes, all publishable:
- ρ high → the rutile-UMA prior *guided* the discovery (Finalist story).
- ρ low but a candidate still beats NiFe-LDH → useful catalyst + a calibration
  lesson (model failure modes).
- ρ low and none beat baseline → rigorous negative/calibration result (Scholar floor).

The predicted-poor anchor (#5) is what gives ρ statistical meaning over 5–6 points.

## 7. Go / no-go & safety

- **End melt week:** ≥3 HEAs single-phase by XRD → proceed; else re-anneal/down-select.
- **End EC week:** triplicate η for all + baseline → compute ρ → decide **round-2
  melt vs computational round-2** (`active_learning.propose_round2`).
- **Safety/SRC (mentor-signed, file early):** 1 M KOH (corrosive); **Cr(VI)** leaching
  under anodic potential for the Cr-bearing alloys (hazardous-waste handling) — note
  the headline pick **Fe32Ni17Co34Mn18 is Cr-free**, the cleanest first melt; metal
  dust during electrode prep.

## 8. Definition of done (round-1)

≥3 ML-shortlist HEAs made, single-phase-confirmed, and benchmarked vs NiFe-LDH with
clean triplicate η@10, Tafel, ECSA, a ≥12 h hold on the best, post-mortem phase
evidence, and the **predicted-vs-measured ρ reported with error bars**.
