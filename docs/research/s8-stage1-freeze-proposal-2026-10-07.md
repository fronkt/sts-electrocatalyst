# S8 stage-1 melt freeze — proposal for the entrant's confirmation, 2026-10-07

Status: **proposed, not frozen, not deposited.** Every item marked **[CONFIRM]** needs Frank's dated decision. The freeze takes effect only when the confirmed text is deposited (Zenodo, restricted, under concept 10.5281/zenodo.21963143, with a per-file manifest in `docs/deposits/`) **before the first ingot**, as required by roadmap §5 ("Retain the S8 freeze/deposit before first ingot") and the S8 rule "FREEZE BEFORE FIRE … No prediction may be revised after any measurement exists" (round-2 synthesis:600–626).

Revision: five alloys and three prediction arms (Frank, 2026-10-07: "Add Fe25."). The four-alloy version is archived at [s8-stage1-freeze-proposal-2026-10-07-archive-four-alloy.md](s8-stage1-freeze-proposal-2026-10-07-archive-four-alloy.md). The practical melt plan is [s8-melt-plan-2026-10-07.md](s8-melt-plan-2026-10-07.md).

## 1. Scope and design (dated scope line [CONFIRM])

Proposed scope line: *"S8 is a declared exploratory validation set comparing three frozen predictions of OER activity for five alloys against one measurement: (A) the August 5 MLIP screen, dated by commit 96b1cb1; (B) the September MLIP site census, frozen here before the first ingot; (C) DFT-informed predictions, frozen before any OER measurement of these alloys is seen. No alloy is claimed superior on the basis of this set."*

What the arms test:
- **A vs B.** Both use the same machine-learned potential (MACE-MPA-0). They differ in how much of each alloy's surface they sample (12 vs 120 sites) and in the statistic (best site vs the 10th percentile of adsorbate-intact sites). Comparing them asks whether broader site sampling predicts measured activity better.
- **C vs A and B.** Asks whether DFT refinement adds predictive value over the MLIP.

Arm A was recorded on 2026-08-05 (`docs/37-hea-screen-result-and-melt-list.md`, commit 96b1cb1) before any melt or measurement, and is not revised here. It was never deposited as a freeze, so it enters as a **dated historical prediction**, labelled as such.

**Blinding rule:** no OER measurement of any of the five alloys before the arm-C deposit. Melting, composition and phase checks, electrode preparation, and electrochemistry dry runs on IrO2 and blanks may proceed.

**Fallback [CONFIRM date]:** if arm C is not deposited by **Oct 21** (roadmap sample-readiness date), OER measurements start anyway. Arm C is then reported as *not tested*, and any later DFT result is labelled post hoc.

## 2. Batch 1 samples

| Role | Composition (nominal at.%, `results/r4_gated.json`) | Why it is in the set |
|---|---|---|
| Candidate | Cu7.887 Cr22.634 Mn34.993 Co34.485 ("Cu8Cr23Mn35Co34") | Arm B leader; arm A 4th of 5 |
| Candidate | Ni31.115 Cr29.187 Cu5.169 Mn34.529 ("Ni31Cr29Cu5Mn35") | Arm A leader; arm B 2nd |
| Candidate | Fe25 Co25 Ni25 Cr25 (equimolar) | Arm A 2nd; arm B 4th |
| Candidate | Cu25.780 Ni9.393 Cr31.466 Co33.362 ("Cu26Ni9Cr31Co33") | Leader under arm B's secondary (strict-intact) statistic; 3rd under both primaries |
| Anchor (predicted poor) | Cu22.116 Fe29.974 Co32.425 Mn15.484 ("Cu22Fe30Co32Mn15") | Last under both arms' primary statistics |
| Reference | IrO2, same cell and conditions, every bench day | Required reference (roadmap §5) |

Selection rule, as applied to the six chemically clean ("gated") compositions:
- arm A's two best;
- arm B's two best under its primary statistic;
- arm B's best under its secondary statistic;
- the alloy ranked last by both arms as the anchor.

Ties and missing cases do not arise for these six. That yields five alloys. The sixth, Ni34Fe6Cu29Co31 (arm A 4th, arm B 5th, no Cr), is not melted in batch 1 [CONFIRM: optional sixth melt, see §4].

## 3. Frozen predictions

**Arm A (dated 2026-08-05):** best-of-12-sites predicted overpotential η (V), MACE-MPA-0, computational hydrogen electrode.

**Arm B (frozen here):**
- **Primary statistic:** the 10th-percentile η over adsorbate-intact sites (out of 120 per alloy; linear quantile convention, `results/s8_ranking_statistic_2026-09-19/ranking_statistics.md`), with the 90% bootstrap interval (`docs/95-census-2-3-readout-2026-09-13.md` T2).
- **Secondary statistic:** the strict-intact 10th percentile, reported but not tested.

| Alloy | A: best of 12 | B: p10 [90% interval] (n admitted) | B: median | B secondary: strict p10 (n) |
|---|---|---|---|---|
| Cu8Cr23Mn35Co34 | 0.756 | **0.384** [0.362, 0.404] (16) | 0.542 | 0.728 (4) |
| Ni31Cr29Cu5Mn35 | **0.440** | 0.473 [0.440, 0.835] (8) | 0.811 | 0.968 (3) |
| Fe25Co25Ni25Cr25 | 0.453 | 0.554 [0.468, 0.834] (19) | 1.117 | 0.903 (11) |
| Cu26Ni9Cr31Co33 | 0.479 | 0.502 [0.449, 0.703] (13) | 0.725 | **0.659** (6) |
| Cu22Fe30Co32Mn15 | 0.796 | 0.831 [0.797, 0.887] (38) | 1.204 | 0.848 (33) |

Predicted orders, where "<" means a lower overpotential, i.e. more active:

| Arm | Order |
|---|---|
| A | Ni31 < Fe25 < Cu26 < Cu8 < Cu22 |
| B primary | Cu8 < Ni31 < Cu26 < Fe25 < Cu22 |
| B secondary | Cu26 < Cu8 < Cu22 < Fe25 < Ni31 |

Registered hypotheses for the measured endpoint:

- **K1 (primary; decides between arms A and B):** the position of Cu8 relative to Ni31 and Fe25. Arm B predicts Cu8 more active than both. Arm A predicts both more active than Cu8. Each pairwise difference is judged against the criterion in §6, and outcomes are classed as follows:

  | Outcome class | Measured result |
  |---|---|
  | B-consistent | Cu8 more active than both |
  | A-consistent | Cu8 less active than both |
  | Mixed or unresolved | anything else |

- **K2 (primary; shared by A and B):** Cu22 is the least active of the five.
- **Exploratory:** arm B's leader (Cu8 most active; its interval lies below all four others), arm A's leader (Ni31 most active), and each arm's full order.
- **Chance levels for five alloys under a random order:**

  | Event | Probability |
  |---|---|
  | Any named alloy is first | 1/5 |
  | Cu22 is last | 1/5 |
  | Cu8 is first and Cu22 is last | 1/20 |
  | A full order | 1/120 |
  | K1 B-consistent | 1/3 |
  | K1 A-consistent | 1/3 |

Uncertainty frozen with the predictions:
- **Screener error is larger than the gaps.** Validation MAE is 99.6–129.6 mV and not held-out (candidate-ranking adequacy :25). That is larger than every gap except to the anchor. A full order would need an error below 6.5 mV.
- **The models disagree.** At twelve shared sites, four MLIP models name 2–4 different leaders.
- **Cu8's lead is narrow and Cr-based.** Its arm-B p10 rests on two reconstructed-Cr sites (seed16/site2, seed26/site1).
- **The descriptor favours Cr more than experiment does.** The DFT reference panel the MLIP was validated against (rutile endmembers, `tier_v2`) puts CrO2 first: η 0.330 V, ahead of IrO2 at 0.781 V and RuO2 at 0.787 V. That inverts the experimental ordering (docs/36:191). K1 therefore also tests whether the descriptor's Cr preference survives in a real alloy.
- **Predictions are ordinal only.** The CHE descriptor leaves out kinetics, surface reconstruction and conductivity.

## 4. Arm C (stage 2) and batch 2 — registered now

**Arm C.** It deposits DFT-informed predictions for the five alloys, as a dated version of this freeze, before any OER measurement of them is seen. Its procedure is defined at stage 2 because it depends on the P-A protocol outcome (O1, job 21159532).

**Batch 2.** It is melted only if arm C nominates an alloy that is not in batch 1. Within the census that can only be Ni34Fe6Cu29Co31.
- **Contents:** the nominated alloy plus a re-melt of the anchor Cu22, and, if feasible, one batch-1 alloy. The re-melts act as bridges, so batch effects are measured rather than confounded.
- **Deadline:** if batch 2 cannot be melted, characterized and measured before the Oct 25 data-lock checkpoint, the nominated alloy is reported as an untested prediction.

[CONFIRM option: melt Ni34Fe6Cu29Co31 in batch 1 as a sixth alloy. Every census alloy would then be in one batch, which removes the census route to batch 2.]

## 5. Processing [CONFIRM values]

- **Weigh sheet:** freshly computed for these exact compositions. Historical sheets and `weigh_sheet.py`'s built-in round-1 set are not reused. Basis: 10 g ingots (about 50 g of metal for batch 1), Mn over-charge **+4%** (tool default; historical range 3–5%).
- **Arc melting** (Fort Wayne Metals, supervised): Ar, flip and remelt **4×** within each melt.
- **Homogenization:** **1,050 °C, 24 h, Ar** (historical 1,000–1,100 °C), then quench.
- **Acceptance:**
  - SEM-EDS composition within **±2 at.%** of nominal per element, and XRD phases recorded.
  - A sample out of tolerance is re-melted once.
  - If it is still out, it is kept, flagged, and analysed at its measured composition.
  - It is never replaced by a different composition.
- **Batch 1:** all five alloys are melted and annealed in one batch on the same day, with the same feedstock lots, recorded.

## 6. Electrochemistry [CONFIRM values]

- **Cell:** 1 M KOH (one batch for the campaign), Hg/HgO reference calibrated to RHE each bench day (E_RHE = E_Hg/HgO + 0.098 + 0.059·pH), graphite counter.
- **Electrode:** mounted coupon, epoxy-masked geometric area, defined polish.
- **Primary endpoint:** η at 10 mA cm⁻² (geometric) from LSV after a fixed CV activation, with R_u measured by EIS before each LSV and **90%** iR compensation.
- **Secondary endpoints:** Tafel slope, C_dl-normalized activity, 12 h hold at 10 mA cm⁻² (drift in mV/h), and post-mortem XRD/SEM-EDS.
- **Electrolyte check:** Cr(VI) in the spent electrolyte (diphenylcarbazide).
- **Replicates:** **≥ 3 coupons per alloy** (≥ 15 in total), measured in randomized order across **≥ 2 bench days**. Each bench day also runs IrO2 and a blank. The unit of replication is the coupon, and batch is recorded.
- **Analysis:** K1 and K2 are judged on mean η, with a pairwise difference counted only if it exceeds twice the pooled coupon-to-coupon SD [CONFIRM criterion]. Spearman ρ of the measured order against each arm's order is reported (exploratory, n = 5).
- **Open:** the O2 / Faradaic-efficiency method required for an OER activity claim (roadmap §5) is not yet specified [CONFIRM].

## 7. Safety (blocking)

A dated, mentor-signed Cr(VI) risk assessment is required before the first melt (docs/25:133–138, docs/37:157–159). **None exists in the repo.** Four of the five alloys contain 22.6–31.5 at.% Cr; Cu22Fe30Co32Mn15 has none. The assessment must cover:
- Cr and Mn fume and dust during melting and polishing;
- Cr(VI) formation in alkaline OER and the disposal of spent KOH as Cr(VI) hazardous waste;
- KOH handling.

The lab supervisor and mentor names are still "TBD" in docs/16 [CONFIRM].

**Draft, 2026-10-07:** [s8-cr6-risk-assessment-2026-10-07.md](s8-cr6-risk-assessment-2026-10-07.md) covers these three hazards, plus Ni/Co dust, the Hg/HgO reference and the waste streams. It still needs the supervisors' names, signatures and dates.

## 8. Before the deposit

1. Frank confirms or edits every **[CONFIRM]** item and the scope line.
2. The Cr(VI) risk assessment is written and signed.
3. The weigh sheet is computed for the confirmed compositions.
4. Deposit the confirmed freeze: Zenodo restricted version, manifest, and a dated line in docs/45 and docs/43. Then melt.

This also resolves the conflict between research-decisions 2026-09-16 (":45", no deposit task as an execution gate) and roadmap §5 (deposit before first ingot): the later roadmap governs, and the deposit is made.
