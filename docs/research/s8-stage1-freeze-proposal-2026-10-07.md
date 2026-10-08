# S8 stage-1 melt freeze — proposal for the entrant's confirmation, 2026-10-07 (revised 2026-10-08)

Status: **proposed, not frozen, not deposited.** Frank's decisions of 2026-10-08 are recorded in place. Every item still marked **[CONFIRM]** needs his dated decision. The freeze takes effect only when the confirmed text is deposited (Zenodo, restricted, under concept 10.5281/zenodo.21963143, with a per-file manifest in `docs/deposits/`) **before the first ingot**, as required by roadmap §5 ("Retain the S8 freeze/deposit before first ingot") and the S8 rule "FREEZE BEFORE FIRE … No prediction may be revised after any measurement exists" (round-2 synthesis:600–626).

Revisions:
- 2026-10-07: five alloys and three prediction arms (Frank: "Add Fe25."). The four-alloy version is archived at [s8-stage1-freeze-proposal-2026-10-07-archive-four-alloy.md](s8-stage1-freeze-proposal-2026-10-07-archive-four-alloy.md).
- 2026-10-08: six alloys, arm C final, and the re-rank gate and IrO2 decisions. The five-alloy version is archived at [s8-stage1-freeze-proposal-2026-10-07-archive-five-alloy.md](s8-stage1-freeze-proposal-2026-10-07-archive-five-alloy.md).

Decisions of record (Frank, 2026-10-08):

| Decision | His words | Where |
|---|---|---|
| The September census is the re-rank of record, and S8 is a declared exploratory set | "Let's rerank gate." | §1, §1a |
| Ni34Fe6Cu29Co31 is melted in batch 1 as a sixth alloy | "Your call on Ni34" (decided in §2) | §2 |
| The same-bench comparison with IrO2 is a registered secondary outcome | "yes IrO2" | §1, §6 |

The practical plan is [s8-melt-plan-2026-10-07.md](s8-melt-plan-2026-10-07.md). The weigh sheet is [s8-weigh-sheet-2026-10-08.md](s8-weigh-sheet-2026-10-08.md).

## 1. Scope and design

Scope line [CONFIRM wording]: *"S8 is a declared exploratory validation set comparing three frozen predictions of OER activity for six alloys against one measurement: (A) the August 5 MLIP screen, dated by commit 96b1cb1; (B) the September MLIP site census, frozen here before the first ingot, which is also the re-rank of record for the selection; (C) DFT values computed before any OER measurement of these alloys. Apart from the registered same-bench comparison with IrO2, no alloy is claimed superior on the basis of this set."*

What the arms test:
- **A vs B.** Both use the same machine-learned potential (MACE-MPA-0). They differ in how much of each alloy's surface they sample (12 vs 120 sites) and in the statistic (best site vs the 10th percentile of adsorbate-intact sites). Comparing them asks whether broader site sampling predicts measured activity better.
- **C vs A and B.** Asks whether DFT refinement adds predictive value over the MLIP. Arm C's registered tests cannot be evaluated (§4), so it enters as an exploratory partial order over four alloys.

Arm A was recorded on 2026-08-05 (`docs/37-hea-screen-result-and-melt-list.md`, commit 96b1cb1) before any melt or measurement, and is not revised here. It was never deposited as a freeze, so it enters as a **dated historical prediction**, labelled as such.

**Blinding rule:** no OER measurement of any of the six alloys before two deposits:
- this freeze, which carries arm C's final readout (§4);
- the arm C extension's readout (§4b).

If the extension's readout is not deposited by **Oct 21** (roadmap sample-readiness date), OER measurements start anyway. The extension is then reported as not tested, and any later DFT result is labelled post hoc.

### 1a. Re-rank gate (dated decision)

The S8 rule of 2026-08-16 requires, before any melt, a re-score of the surviving candidates with the corrected protocol, "with corrected-DFT spot-checks on the best site of each of the top ~4 compositions" (round-2 synthesis:600).
- **Re-rank of record:** the September census, 120 sites per alloy under the adsorbate-intact policy (`docs/95-census-2-3-readout-2026-09-13.md`). It is arm B (§3).
- **DFT spot checks:** run as arm C, as fixed-geometry DFT+U single points at the census geometries ([s8-arm-c-dft-design-2026-10-07.md](s8-arm-c-dft-design-2026-10-07.md)).
  - Complete for two of the top four best sites: Cu8 s20/2 at 0.621 V (MLIP 0.362 V) and Ni31 s1/0 at 0.768 V (MLIP 0.440 V).
  - Cu26 s5/2 and Fe25 s2/0 did not converge within the registered single re-run round, and neither did the anchor's best site, Cu22 s27/3.
- **Use:** the spot checks are reported, not used for selection. Roadmap §5 allows this for a declared exploratory validation set, which "can retain unresolved rankings, with a dated scope decision, frozen predictions and matched controls". The scope line above is that dated decision.
- **Departures recorded:** this dated decision departs from the S8 rule and the roadmap in three places.
  - The census is a fixed-protocol MLIP re-score, without the rule's "symmetry-released multi-start relaxations, fresh-density basin gates, stated coverage" (round-2 synthesis:603–604).
  - The DFT spot checks are complete for two of the top four best sites.
  - The melt set is the whole gated six: four candidates, one set member (§2) and the anchor. The rule asks for "Top 2–4 of the re-ranked list plus one predicted-poor anchor" (round-2 synthesis:607), and the roadmap sets "2–4 candidate alloys + a predicted-poor anchor" (roadmap §5).

## 2. Batch 1 samples

| Role | Composition (nominal at.%, `results/r4_gated.json`) | Why it is in the set |
|---|---|---|
| Candidate | Cu7.887 Cr22.634 Mn34.993 Co34.485 ("Cu8Cr23Mn35Co34") | Arm B leader; arm A 5th of 6 |
| Candidate | Ni31.115 Cr29.187 Cu5.169 Mn34.529 ("Ni31Cr29Cu5Mn35") | Arm A leader; arm B 2nd |
| Candidate | Fe25 Co25 Ni25 Cr25 (equimolar) | Arm A 2nd; arm B 4th |
| Candidate | Cu25.780 Ni9.393 Cr31.466 Co33.362 ("Cu26Ni9Cr31Co33") | Leader under arm B's secondary (strict-intact) statistic; 3rd under both primaries |
| Set member | Ni33.877 Fe5.962 Cu29.423 Co30.738 ("Ni34Fe6Cu29Co31") | The sixth gated alloy: arm A 4th, arm B 5th; no Cr or Mn. Added 2026-10-08 (below) |
| Anchor (predicted poor) | Cu22.116 Fe29.974 Co32.425 Mn15.484 ("Cu22Fe30Co32Mn15") | Last under both arms' primary statistics |
| Reference | IrO2, same cell and conditions, every bench day | Required reference (roadmap §5); registered secondary comparison (§6) |

Batch 1 is all six chemically clean ("gated") compositions. The five-alloy rule chose the K-set: arm A's two best, arm B's two best under its primary statistic, arm B's best under its secondary statistic, and the alloy ranked last by both arms as the anchor. Ni34, the one gated alloy that rule left out, is added.

**Ni34 decision (Frank, 2026-10-08: "Your call on Ni34"): melt it in batch 1.**
- Arm C cannot nominate it (§4), so it would otherwise never be measured, and batch 2 no longer exists.
- All six gated alloys are then made and measured in one batch, so no batch effect enters any comparison.
- It adds a sixth point to the exploratory order comparisons, and a second alloy without Cr.
- Cost: one more 200 g button, at least three more coupons, and about 20% more bench time.
- **K1 and K2 stay on the five alloys they were designed for** (§3). Ni34 enters only the exploratory comparisons, so adding a sample changes no primary test.

## 3. Frozen predictions

**Arm A (dated 2026-08-05):** best-of-12-sites predicted overpotential η (V), MACE-MPA-0, computational hydrogen electrode.

**Arm B (frozen here):**
- **Primary statistic:** the 10th-percentile η over adsorbate-intact sites (out of 120 per alloy; linear quantile convention, `results/s8_ranking_statistic_2026-09-19/ranking_statistics.md`), with the 90% bootstrap interval (`docs/95-census-2-3-readout-2026-09-13.md`, `--admit adsorbate-intact`).
- **Secondary statistic:** the strict-intact 10th percentile, reported but not tested.

| Alloy | A: best of 12 | B: p10 [90% interval] (n admitted) | B: median | B secondary: strict p10 (n) |
|---|---|---|---|---|
| Cu8Cr23Mn35Co34 | 0.756 | **0.384** [0.362, 0.404] (16) | 0.542 | 0.728 (4) |
| Ni31Cr29Cu5Mn35 | **0.440** | 0.473 [0.440, 0.835] (8) | 0.811 | 0.968 (3) |
| Fe25Co25Ni25Cr25 | 0.453 | 0.554 [0.468, 0.834] (19) | 1.117 | 0.903 (11) |
| Cu26Ni9Cr31Co33 | 0.479 | 0.502 [0.449, 0.703] (13) | 0.725 | **0.659** (6) |
| Ni34Fe6Cu29Co31 | 0.726 | 0.739 [0.679, 0.912] (15) | 0.962 | 0.739 (15) |
| Cu22Fe30Co32Mn15 | 0.796 | 0.831 [0.797, 0.887] (38) | 1.204 | 0.848 (33) |

**Arm C (final 2026-10-08, §4):** DFT+U η (V) with the computational hydrogen electrode, weighted over the alloy's two support sites, or from one site when only one is complete.

| Alloy | C (V) | Basis |
|---|---|---|
| Cu26Ni9Cr31Co33 | 0.613 | one site (s1/0) |
| Ni31Cr29Cu5Mn35 | 0.934 | two sites |
| Cu22Fe30Co32Mn15 | 0.942 | one site (s24/3) |
| Ni34Fe6Cu29Co31 | 1.281 | one site (s29/1) |
| Cu8Cr23Mn35Co34, Fe25Co25Ni25Cr25 | none | no complete support site |

Predicted orders, where "<" means a lower overpotential, i.e. more active:

| Arm | Order |
|---|---|
| A | Ni31 < Fe25 < Cu26 < Ni34 < Cu8 < Cu22 |
| B primary | Cu8 < Ni31 < Cu26 < Fe25 < Ni34 < Cu22 |
| B secondary | Cu26 < Cu8 < Ni34 < Cu22 < Fe25 < Ni31 |
| C (exploratory, four alloys) | Cu26 < Ni31 < Cu22 < Ni34 |

Registered hypotheses for the measured endpoint. K1 and K2 are judged on the five K-set alloys; Ni34 is excluded from them by rule (§2).

- **K1 (primary; decides between arms A and B):** the position of Cu8 relative to Ni31 and Fe25. Arm B predicts Cu8 more active than both. Arm A predicts both more active than Cu8. Each pairwise difference is judged against the criterion in §6, and outcomes are classed as follows:

  | Outcome class | Measured result |
  |---|---|
  | B-consistent | Cu8 more active than both |
  | A-consistent | Cu8 less active than both |
  | Mixed or unresolved | anything else |

- **K2 (primary; shared by A and B):** Cu22 is the least active of the five K-set alloys.
- **Exploratory:**
  - arm B's leader (Cu8 most active of the six; its interval lies below all five others);
  - arm A's leader (Ni31 most active);
  - each arm's full order over the alloys it ranks (A and B: six; C: four);
  - Ni34's measured position.
- **Chance levels under a random order:**

  | Event | Probability |
  |---|---|
  | K1 B-consistent | 1/3 |
  | K1 A-consistent | 1/3 |
  | K2: Cu22 last of the five | 1/5 |
  | Any named alloy first of the six | 1/6 |
  | Cu8 first and Cu22 last, of the six | 1/30 |
  | A full order of the six | 1/720 |

Uncertainty frozen with the predictions:
- **Screener error is larger than most gaps.** Validation MAE is 99.6–129.6 mV and not held-out (candidate-ranking adequacy :25).
  - With that error on each value, two alloys are separated only if their gap exceeds twice the error, 199–259 mV (adequacy :21).
  - In the six-alloy orders of arms A and B (primary), no adjacent gap clears 259 mV. Only Cu26 to Ni34 in arm A (247 mV) clears 199 mV; Fe25 to Ni34 in arm B is 184 mV.
  - For K2, Cu22 trails the next-worst K-set alloy by 40 mV in arm A (Cu8) and by 277 mV in arm B (Fe25), so only arm B's K2 margin is separated.
  - A full order would need an error below half the smallest adjacent gap: 6.5 mV for arm A, 14.6 mV for arm B.
- **The models disagree.** At twelve shared sites, four MLIP models name 2–4 different leaders.
- **Cu8's lead is narrow and Cr-based.** Its arm-B p10 rests on two reconstructed-Cr sites (seed16/site2, seed26/site1).
- **The descriptor favours Cr more than experiment does.** The DFT reference panel the MLIP was validated against (rutile endmembers, `tier_v2`) puts CrO2 first: η 0.330 V, ahead of IrO2 at 0.781 V and RuO2 at 0.787 V. That inverts the experimental ordering (docs/36:191). K1 therefore also tests whether the descriptor's Cr preference survives in a real alloy.
- **DFT sits above the MLIP.** At the six sites with complete DFT, DFT η is 0.10–0.52 V higher than the MLIP's, by a site-dependent amount (arm C design doc §7).
- **Predictions are ordinal only.** The computational-hydrogen-electrode descriptor leaves out kinetics, surface reconstruction and conductivity.

## 4. Arm C — as built and final

**Design.** Fixed-geometry DFT+U single points (Quantum ESPRESSO 7.5, 72-atom rutile(110) slabs) at the census geometries of 16 sites: two weighted support sites per alloy, plus best sites. That is 64 SCFs, plus one registered re-run round of every failed SCF ([s8-arm-c-dft-design-2026-10-07.md](s8-arm-c-dft-design-2026-10-07.md) §3–§7). It used 17,399.8 SU of the approved 23,680.

**Readout.** `results/arm_c_2026-10-07/readout.json` and, final, `results/arm_c_2026-10-07_rerun/readout.json` (commit 2229549):
- 40 of 64 SCFs accepted and 6 of 16 sites complete. The values are in §3.
- Cu8 and Fe25 have no value, because neither of their support sites is complete.
- Registered readings: **K1, K2 and the Ni34 batch-2 nomination are NOT_EVALUABLE_UNDER_ARM_C.** The rule allows one re-run round, so these readings are final.
- No later relaxation of the acceptance rule changes this. Each support site of Cu8 and Fe25 has at least one SCF that never settled (design doc §7).

**How arm C enters S8.** Its registered tests are reported as not evaluable. Its partial order over four alloys (§3) was computed before any OER measurement and is frozen here as an exploratory prediction. Ni31 and Cu22 differ by 8 mV, far inside DFT+U error.

**Batch 2: none.** Ni34, the only alloy arm C could have nominated, is in batch 1 (§2), and arm C cannot nominate in any case. No later batch is part of S8.

### 4b. Arm C extension (exploratory)

Decision (Frank, 2026-10-08): "Let's rerun DFT for those and get values for them."
- **Scope:** the 11 SCFs still missing at Cu8's and Fe25's support sites:
  - Cu8 s16/2: slab, OH, OOH;
  - Cu8 s26/1: slab, O, OOH;
  - Fe25 s13/0: OH, O, OOH;
  - Fe25 s25/2: OH, O.
- **Recipe:** chosen for the observed failure modes (magnetic-state wandering and stalls). It is fixed, with its acceptance rule, before launch in the extension's design record.
- **Status:** the extension was decided after the arm C readout, so it cannot change arm C's registered readings, which stay final.
- **What it can add:** values for Cu8 and Fe25, a six-alloy DFT order, and DFT readings of K1 and K2. All are exploratory predictions, frozen when the extension's readout is deposited, before any OER measurement.

## 5. Processing [CONFIRM values]

- **Weigh sheet:** freshly computed for the six compositions at **200 g per button** ([s8-weigh-sheet-2026-10-08.md](s8-weigh-sheet-2026-10-08.md)), about 1.2 kg of metal for batch 1.
  - The basis is what Fort Wayne Metals will melt (Song Cai, 2026-10-07: "We will melt a 200 gram for each alloy. they will be ~2” diameter button").
  - Historical sheets, the 10 g sheet of 2026-10-07 and `weigh_sheet.py`'s built-in round-1 set are not reused.
  - Mn over-charge **+4%** (tool default; historical range 3–5%) [CONFIRM with FWM for a 200 g button].
- **Arc melting** (Fort Wayne Metals, supervised): Ar, flip and remelt **4×** within each melt.
- **Homogenization:** **1,050 °C, 24 h, Ar** (historical 1,000–1,100 °C), then quench [CONFIRM with FWM].
- **Acceptance:**
  - SEM-EDS composition within **±2 at.%** of nominal per element, and XRD phases recorded.
  - A sample out of tolerance is re-melted once.
  - If it is still out, it is kept, flagged, and analysed at its measured composition.
  - It is never replaced by a different composition.
- **Batch 1:** all six alloys are melted and annealed in one batch, with the same feedstock lots, recorded.

## 6. Electrochemistry [CONFIRM values]

- **Lab:** the Tackett group, Purdue (reply of 2026-10-07). Stationary electrodes only; the lab's students run the measurements.
- **Cell:** 1 M KOH (one batch for the campaign), Hg/HgO reference calibrated to RHE each bench day (E_RHE = E_Hg/HgO + 0.098 + 0.059·pH), graphite counter.
- **Electrode:** a 5.00 mm disk (0.196 cm² face) with a silver-painted back wire, potted in epoxy and polished flush, so the exposed area is the disk face (melt plan, "Electrode format").
- **Primary endpoint:** η at 10 mA cm⁻² (geometric) from LSV at **5 mV s⁻¹** after a fixed CV activation, with R_u measured by EIS before each LSV and **90%** iR compensation.
- **Secondary endpoints:**
  - η at 1 mA cm⁻², which is less disturbed by bubbles on a stationary electrode;
  - the steady-state Tafel slope from constant-potential holds;
  - C_dl-normalized activity;
  - a 12 h hold at 10 mA cm⁻² (drift in mV/h), on at least one coupon per alloy if channel time is short;
  - post-mortem XRD/SEM-EDS.
- **Registered secondary outcome: comparison with IrO2** (Frank, 2026-10-08: "yes IrO2").
  - For each alloy, its mean η at 10 mA cm⁻² is compared with the mean of the IrO2 runs on the same bench, using the criterion below.
  - Outcome classes per alloy: lower than IrO2, not distinguishable, or higher than IrO2.
  - The C_dl-normalized comparison is reported alongside it, because a polished alloy disk and an IrO2 electrode differ in real surface area. The IrO2 electrode is the lab's own, and its format is recorded.
  - Caveats frozen with it: IrO2 is a weak benchmark in alkaline solution (the lab's own note; a Ni or NiFe standard may be added as an extra column). The alloy surfaces become oxyhydroxides in KOH, so a result describes that surface, not the bare alloy.
- **Electrolyte check:** Cr(VI) in the spent electrolyte (diphenylcarbazide).
- **Replicates:** **≥ 3 coupons per alloy** (≥ 18 in total), measured in randomized order across **≥ 2 bench days**. Each bench day also runs IrO2 and a blank. The unit of replication is the coupon, and batch is recorded.
- **Analysis:** K1, K2 and the IrO2 comparison are judged on mean η. A difference counts only if it exceeds twice the pooled coupon-to-coupon SD [CONFIRM criterion]. Spearman ρ of the measured order against each arm's order is reported over the alloys each arm ranks (A and B: six; C: four); it is exploratory.
- **O2 / Faradaic efficiency [CONFIRM]:**
  - The lab advises against O2 quantification for the main set.
  - One bare 5.0 mm disk per alloy is supplied for the optional EC-MS O2 measurement, Cu8 first.
  - Without it, currents are reported as anodic activity in the OER window, checked by the Tafel slope. An OER-specific claim is limited to alloys measured by EC-MS, because roadmap §5 requires an O2 method for an OER activity claim.

## 7. Safety (blocking)

A dated, mentor-signed Cr(VI) risk assessment is required before the first melt (docs/25:133–138, docs/37:157–159). Four of the six alloys contain 22.6–31.5 at.% Cr; Cu22Fe30Co32Mn15 and Ni34Fe6Cu29Co31 have none. The assessment must cover:
- Cr and Mn fume and dust during melting and polishing;
- Cr(VI) formation in alkaline OER and the disposal of spent KOH as Cr(VI) hazardous waste;
- KOH handling.

[s8-cr6-risk-assessment-2026-10-07.md](s8-cr6-risk-assessment-2026-10-07.md) covers these three hazards, plus Ni/Co dust, the Hg/HgO reference and the waste streams, for six 200 g buttons. It still needs the supervisors' names, signatures and dates [CONFIRM names].

## 8. Before the deposit

1. Frank confirms or edits the remaining **[CONFIRM]** items: the scope wording, the processing values with FWM, the electrochemistry values and the O2 framing.
2. The weigh sheet is computed for the six compositions at 200 g: done ([s8-weigh-sheet-2026-10-08.md](s8-weigh-sheet-2026-10-08.md)).
3. Deposit the confirmed freeze with arm C's readout: Zenodo restricted version, manifest, and a dated line in docs/45 and docs/43.
4. The Cr(VI) risk assessment is signed and dated. Then melt.
5. Before any OER measurement, deposit the arm C extension's readout as a further version, or apply the Oct 21 fallback (§1).

This also resolves the conflict between research-decisions 2026-09-16 (":45", no deposit task as an execution gate) and roadmap §5 (deposit before first ingot): the later roadmap governs, and the deposit is made.
