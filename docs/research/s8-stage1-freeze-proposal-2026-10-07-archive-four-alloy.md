> **Archived 2026-10-07.** This is the four-alloy version of `s8-stage1-freeze-proposal-2026-10-07.md` as committed in 18a4bc1. It was superseded the same day by the five-alloy, three-arm revision (Frank, 2026-10-07: "Add Fe25."). It was never frozen or deposited.

# S8 stage-1 melt freeze — proposal for the entrant's confirmation, 2026-10-07

Status: **proposed, not frozen, not deposited.** Every item marked **[CONFIRM]** needs Frank's dated decision. The freeze takes effect only when the confirmed text is deposited (Zenodo, restricted, under concept 10.5281/zenodo.21963143, with a per-file manifest in `docs/deposits/`) **before the first ingot**, as required by roadmap §5 ("Retain the S8 freeze/deposit before first ingot") and the S8 rule "FREEZE BEFORE FIRE … No prediction may be revised after any measurement exists" (round-2 synthesis:600–626).

## 1. Scope and design (dated scope line [CONFIRM])

Proposed scope line: *"S8 is a declared exploratory validation set with a two-stage selection-method comparison. Stage 1 freezes MLIP-only (MACE-MPA-0 census) predictions for four alloys before the first ingot. Stage 2 freezes DFT-informed predictions for the same alloys before any OER measurement of them is seen. The measured OER activity is compared against both frozen predictions. No alloy is claimed superior on the basis of this set."*

Why two stages: lab time and computation run in parallel. The stage-1 ingots can be melted and characterized while the DFT relaxation protocol is still being certified (O1, docs/research/pa-catalyst-o1-2026-10-07.md). The comparison asks whether DFT refinement predicts measured activity better than the MLIP screen alone.

Blinding rule: no OER measurement of a stage-1 candidate or the anchor before the stage-2 deposit. Melting, composition and phase checks, electrode preparation and electrochemistry dry runs on IrO2 and blanks may proceed.

Fallback [CONFIRM date]: if stage 2 is not deposited by **Oct 21** (roadmap sample-readiness date), OER measurements start anyway. The stage-2 comparison is then reported as *not tested*, and any later DFT result is labelled post hoc.

## 2. Stage-1 samples

| Role | Composition (nominal at.%, `results/r4_gated.json`) | Why |
|---|---|---|
| Candidate | Cu7.887 Cr22.634 Mn34.993 Co34.485 ("Cu8Cr23Mn35Co34") | Adsorbate-intact p10 leader; leader in all 180 leave-one-decoration-out cases |
| Candidate | Ni31.115 Cr29.187 Cu5.169 Mn34.529 ("Ni31Cr29Cu5Mn35") | Second under adsorbate-intact p10 |
| Candidate | Cu25.780 Ni9.393 Cr31.466 Co33.362 ("Cu26Ni9Cr31Co33") | Strict-intact p10 leader; spans the statistic disagreement |
| Anchor (predicted poor) | Cu22.116 Fe29.974 Co32.425 Mn15.484 ("Cu22Fe30Co32Mn15") | Last under adsorbate-intact p10, median and mean |
| Reference | IrO2, same cell and conditions, every bench day | Required reference (roadmap §5) |

Selection rule, as applied to the six census compositions: the two best under the primary statistic, the best under the secondary statistic if not already included, and the worst under the primary statistic as the anchor. Ties and missing cases do not arise for these six. Not included: Fe25Co25Ni25Cr25 (adsorbate-intact p10 rank 4) and Ni34Fe6Cu29Co31 (rank 5). [CONFIRM: optional fifth melt, Fe25Co25Ni25Cr25 as a literature-comparable alloy.]

## 3. Frozen stage-1 predictions

Primary statistic: the adsorbate-intact policy's 10th-percentile predicted OER overpotential over admitted sites (linear quantile convention, `ranking_statistics.md`), with the 90% bootstrap interval (docs/95:1072–1079).

| Alloy | n admitted | p10 (V) | 90% interval | Median (V) | Strict-intact p10 (n) |
|---|---|---|---|---|---|
| Cu8Cr23Mn35Co34 | 16 | **0.384** | [0.362, 0.404] | 0.542 | 0.728 (4) |
| Ni31Cr29Cu5Mn35 | 8 | **0.473** | [0.440, 0.835] | 0.811 | 0.968 (3) |
| Cu26Ni9Cr31Co33 | 13 | **0.502** | [0.449, 0.703] | 0.725 | 0.659 (6) |
| Cu22Fe30Co32Mn15 | 38 | **0.831** | [0.797, 0.887] | 1.204 | 0.848 (33) |

Expected ordinal outcomes for the measured endpoint, where "<" means a lower overpotential, i.e. more active:

- **H1 (primary):** Cu8Cr23Mn35Co34 is the most active of the four. Its interval [0.362, 0.404] lies below all three others.
- **H2 (primary):** Cu22Fe30Co32Mn15 is the least active of the four. Its interval lies above Cu8's and Cu26's, and overlaps Ni31's upper tail.
- **H3 (exploratory):** the full primary order Cu8 < Ni31 < Cu26 < Cu22. Ni31 and Cu26 overlap, so this order is low-confidence.
- **Secondary statistic order (reported, not tested):** Cu26 < Cu8 < Cu22 < Ni31 (strict-intact p10).

Uncertainty, frozen with the predictions:
- **Screener error is larger than the gaps.** Validation MAE is 99.6–129.6 mV and not held-out (candidate-ranking adequacy :25). That is larger than every gap except to the anchor, and a full order would need an error below 6.5 mV.
- **The models disagree.** At twelve sites the four MLIPs name 2–4 different leaders.
- **Cu8's p10 rests on two sites** (seed16/site2, seed26/site1). They are reconstructed-Cr sites.
- **The descriptor does not determine current.** The CHE overpotential leaves out kinetics, surface reconstruction and conductivity, so predictions are ordinal only.
- **Chance level.** Under a random ordering of four alloys, H1 and H2 hold together with probability 1/12 (8.3%), and H3 with 1/24 (4.2%).

## 4. Stage-2 commitment (registered now)

Stage 2 deposits DFT-informed predictions for the same four alloys, as a dated version of this freeze, before any OER measurement of them is seen. Its procedure is defined at stage 2 because it depends on the P-A protocol outcome (O1). If stage 2 nominates an alloy not in stage 1, that alloy goes in a second melt batch. That batch also re-melts the anchor (and, if feasible, one stage-1 candidate) as a bridge, so batch effects are measured rather than confounded.

## 5. Processing [CONFIRM values]

- **Weigh sheet:** freshly computed for these exact compositions; historical sheets and `weigh_sheet.py`'s built-in round-1 set are not reused. Basis: 10 g ingots, Mn over-charge **+4%** (tool default; historical range 3–5%).
- **Arc melting** (Fort Wayne Metals, supervised): Ar, flip and remelt **4×**.
- **Homogenization:** **1,050 °C, 24 h, Ar** (historical 1,000–1,100 °C), then quench.
- **Acceptance:** SEM-EDS composition within **±2 at.%** of nominal per element, and XRD phases recorded. A sample out of tolerance is re-melted once. If it is still out, it is kept, flagged, and analysed at its measured composition. It is never replaced by a different composition.
- **Batch:** all four stage-1 alloys are melted and annealed in one batch on the same day, with the same feedstock lots, recorded.

## 6. Electrochemistry [CONFIRM values]

- **Cell:** 1 M KOH (one batch for the campaign), Hg/HgO reference calibrated to RHE each bench day (E_RHE = E_Hg/HgO + 0.098 + 0.059·pH), graphite counter.
- **Electrode:** mounted coupon, epoxy-masked geometric area, defined polish.
- **Primary endpoint:** η at 10 mA cm⁻² (geometric) from LSV after a fixed CV activation, with R_u measured by EIS before each LSV and **90%** iR compensation.
- **Secondary endpoints:** Tafel slope, C_dl-normalized activity, 12 h hold at 10 mA cm⁻² (drift in mV/h), and post-mortem XRD/SEM-EDS.
- **Electrolyte check:** Cr(VI) in the spent electrolyte (diphenylcarbazide).
- **Replicates:** **≥ 3 coupons per alloy**, measured in randomized order across **≥ 2 bench days**. Each bench day also runs IrO2 and a blank. The unit of replication is the coupon, and batch is recorded.
- **Ordinal analysis:** each alloy's mean η is compared with H1–H3. Pairwise differences are judged against the coupon-to-coupon SD, and Spearman ρ against both predicted orders is reported (exploratory, n = 4).
- **Open:** the O2 / Faradaic-efficiency method required for an OER activity claim (roadmap §5) is not yet specified [CONFIRM].

## 7. Safety (blocking)

A dated, mentor-signed Cr(VI) risk assessment is required before the first melt (docs/25:133–138, docs/37:157–159). **None exists in the repo.** Three of the four alloys contain 22.6–31.5 at.% Cr. The assessment must cover:
- Cr and Mn fume and dust during melting and polishing;
- Cr(VI) formation in alkaline OER and the disposal of spent KOH as Cr(VI) hazardous waste;
- KOH handling.

The lab supervisor and mentor names are still "TBD" in docs/16 [CONFIRM].

## 8. Before the deposit

1. Frank confirms or edits every **[CONFIRM]** item and the scope line.
2. The Cr(VI) risk assessment is written and signed.
3. The weigh sheet is computed for the confirmed compositions.
4. Deposit the confirmed freeze: Zenodo restricted version, manifest, and a dated line in docs/45 and docs/43. Then melt.

This also resolves the conflict between research-decisions 2026-09-16 (":45", no deposit task as an execution gate) and roadmap §5 (deposit before first ingot): the later roadmap governs, and the deposit is made.
