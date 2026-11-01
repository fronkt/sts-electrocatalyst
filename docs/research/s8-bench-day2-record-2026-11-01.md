# S8 bench, day 2 (2026-10-30): disks B1 and D1 (record of 2026-11-01)

Status: **blinded** (per code; the code key is private). The registered readout has been run on every file received so
far. Day 2026-10-30 **counts** on the bench's stated reference value (dated decision 2026-10-26,
[s8-oer-analysis-2026-10-19.md](s8-oer-analysis-2026-10-19.md)). Everything under "Exploratory" is outside the
registered endpoints. Under lock-rule item 3 ([s8-electrode-lock-rule-2026-10-16.md](s8-electrode-lock-rule-2026-10-16.md))
the numbers of an incomplete alloy are kept here, dated, and do not enter the report.

## What arrived

- **Files.** From the Tackett group, received 2026-11-01: one archive for code B (15 EC-Lab `.mpr` data files, 4 `.mps`
  settings files) and one `.mpr` file for code D. EC-Lab 11.62, device VSP, bench folder "SampleB_SameSetup". Measured
  2026-10-30: B1 from 16:28 to 20:17, D1 from 20:54 to 21:06. The raw files stay in the private data directory with a
  SHA-256 list; each exported table logs its source file's SHA-256, and the readout records the SHA-256 of every file it
  reads.
- **The bench's note.** Code B is finished and "performs well". On code D the first CVs worked and "may still be used for
  a quick comparison"; the next 2–3 trials gave noisy data (those files were not sent), and most code-D disks already
  show deformation or creases. The remaining disks are planned by Monday 2026-11-02.
- **Cell.** As on day 1 by the agreed routine (1 M KOH purged with argon, carbon counter, Hg/HgO reference, 1,600 rpm).
  Rotation and gas are not stored in the files and were not restated for this day. The settings fields (electrode area
  0.000 cm², blank electrolyte and reference) are ignored, as on day 1.
- **Sequence on B1.**
  1. 16:28: EIS and a CV with no cell connection (|Z| 22 kΩ at 200 kHz, zero current; the linked CV file holds no
     data). Failed.
  2. 16:45: 8 CVs at 50 mV/s, no live iR, while the window was set (upper vertex 0.30, 0.10, 0.65 V vs Hg/HgO; lower
     −1.25/−1.30 V; the last cycle partial).
  3. 16:55: EIS at 0.70 V vs Hg/HgO (R_hf 8.642 Ω); live compensation set to 85% of 8.6 Ω (Rcmp 7.310 Ω); 25 CVs,
     −1.25 to 0.75 V at 50 mV/s, under that compensation; then 4 LSV sweeps at 5 mV/s from −1.20 V. Sweeps 1 and 3 ran
     to 0.75 and 0.70 V; sweep 2 stopped at −0.56 V and sweep 4 at 0.53 V (both failed, before any oxygen current).
  4. 19:59: EIS at 0.70 V (R_hf 7.323 Ω); Rcmp 6.205 Ω (85%); 4 CVs, −1.30 to 0.70 V; C_dl CVs, −1.00 to −0.60 V vs
     Hg/HgO at 5, 10, 25, 50, 75 and 100 mV/s. The file name ("REPEAT") implies an earlier C_dl set that was not sent.
- **Sequence on D1.** 9 CVs at 50 mV/s, no live iR: upper vertex 0.65 V vs Hg/HgO for cycles 1–8 and 0.75 V for
  cycle 9, lower −1.25 to −1.35 V. No EIS, LSV or C_dl in the file sent.

## Registered readout (blinded)

Files: `results/s8_oer/day2_2026-10-30/readout_blinded_2026-11-01.json` and the manifest it read,
`manifest_2026-11-01.csv` (paths relative to the private data directory; tables exported with
`src/echem/s8_mpr_export.py`).

```
PYTHONPATH=src python src/echem/s8_oer_readout.py --manifest <data>/manifest.csv --lock 2026-11-03 \
    --ir-hw-verified "<the day-1 check; the day-2 check below>" --out <data>/readout/readout_blinded_2026-11-01.json
```

- **Statuses**, set from the instrument record before any value was read: the two no-connection runs and LSV sweeps 2
  and 4 (stopped before the programmed end) are failed; every other run is ok.
- **Day 2026-10-30 counted** (calibration: bench, 0.924 V).
- **B1** (offset 0.924 V; 90% iR in total; kept, not reported):

  | Run | η₁₀ (V) | η₁ (V) | j at η = 0.35 V (mA cm⁻²) | Redox flags |
  |---|---|---|---|---|
  | sweep 1 (primary) | 0.3160 | 0.1139 | 30.4 | none |
  | sweep 3 (repeat) | 0.3154 | 0.1061 | 31.2 | none |

- **B1's η₁ is not an oxygen-evolution value.** A pre-OER oxidation wave (Ni(II)/Ni(III)-type, by its potential)
  crosses 1 mA cm⁻² near 1.34 V vs RHE, and the current then stays above 1 mA cm⁻² until oxygen evolution takes over. With a single upward crossing,
  the readout's redox flag (first against last crossing) cannot fire. The rule is unchanged; the secondary endpoint is
  read with this in mind.
- **R_u.** The manifest uses the EIS before the activation CVs (8.642 Ω, 35 min before the first sweep; there is no
  EIS between the CVs and the LSVs), so the instrument share is 84.6%. With the next EIS (7.323 Ω, 2 h after the LSVs)
  instead, η₁₀ of sweep 1 would be 0.3184 V (+2.4 mV).
- **C_dl** 0.0258 mF (6 rates, r² 0.992); roughness factor 3.3 at C_s = 0.040 mF cm⁻²; specific activity
  9.3 mA cm⁻². The window differs from A1's (see Exploratory), so these do not compare with A1's.
- **Tafel slope: none** (no holds on B1).
- **D1** has no LSV, so no η₁₀.
- **Codes.** A has 1 of the 3 disks it needs (A1), B 1 (B1), C–F none. No alloy is complete; K1 and K2 are not
  evaluated.

**The live-iR export check on day 2 (choice 4).** Under live compensation (Rcmp 7.310 Ω) the exported Ewe follows the
programmed potential to within 0.52 mV in the 25 CVs and 1.06 mV in the LSVs, while Rcmp × I reaches 484 and 382 mV.
Ewe therefore again excludes the compensated drop, as on day 1. The matched-current fit of day 1 is not repeated: no
uncompensated steady CVs sit beside the compensated ones (the 8 uncompensated CVs ran before the surface activated).
This sentence is appended to the `--ir-hw-verified` text stored in the readout.

## Exploratory (not registered)

Script `src/scripts/s8_bench_exploratory.py --day 2026-10-30` (day 2 added; the day-1 output is unchanged, byte for
byte); output `results/s8_oer/day2_2026-10-30/exploratory.json` and five `exploratory_*.png` figures. Potentials on
0.924 V.

- **The surface kept changing, as on A1.** EIS at 0.70 V vs Hg/HgO, R_s + (R_ct ‖ CPE): R_ct 10.8 → 4.7 Ω and
  effective capacitance 0.18 → 0.96 mF between 16:55 (before activation) and 19:59, while the current at that
  potential rose from 4.0 to 7.0 mA. R_hf fell from 8.64 to 7.32 Ω.
- **Activation.** Under live compensation, the current at 0.70 V vs Hg/HgO rose from 47 mA cm⁻² on cycle 1 to
  138 mA cm⁻² on cycle 25 and levelled after about cycle 20, within a cycle-to-cycle scatter of about ±5%.
- **A growing oxyhydroxide film.** On the cathodic branch (the anodic wave sits under the oxygen foot) the
  reduction wave peaks near 1.31 V vs RHE. Its charge rose from 2.9 mC cm⁻² on cycle 1 to 9.5 mC cm⁻² on cycle 26,
  and was 13.0 mC cm⁻² two hours later. At one electron per site, 9.5 mC cm⁻² is 99 nmol cm⁻², about 50 monolayers.
- **Activity follows the film.** The current at 0.70 V divided by the wave charge stays between 13.4 and
  18.3 mA mC⁻¹ on every cycle; log current against log charge has slope 0.79 (r = 0.975). So activation added
  electroactive oxyhydroxide more than it made each site more active, and the activity per unit charge fell by about
  15% as the film thickened.
- **Turnover.** With every wave site active, each turns over at least 0.73 s⁻¹ at η = 0.35 V (A1: 0.67 s⁻¹, with a
  factor-of-two uncertainty in its charge). The lower bounds agree; B1 carries about five times A1's wave charge.
- **LSV shape.** Between 1 and 10 mA cm⁻² the sweeps run along the tail of the Ni wave (178–180 mV/dec, not a kinetic
  slope). Between 10 and 100 mA cm⁻² the slope is 73 mV/dec with live compensation only, and 65 or 86 mV/dec after
  the registered 90% correction with R_u = 8.642 or 7.323 Ω: the slope depends on which R_u held during the sweeps.
  Above about 150 mA cm⁻² the current oscillates (bubble release).
- **C_dl window.** The C_dl CVs ran at −1.00 to −0.60 V vs Hg/HgO (−0.08 to 0.32 V vs RHE), not the routine's −0.10
  to 0.20 V (0.82 to 1.12 V vs RHE) used on A1. The mean current is cathodic at every rate (−3 to −7 µA, hydrogen
  evolution at the lower end), and the fit's zero-rate intercept is 1.2 µA. The window lies below the oxyhydroxide
  couple, where the film is reduced and poorly conducting; the EIS capacitance at 0.70 V is 37 times larger.
- **D1.** The current at 0.60 V vs Hg/HgO rose over the first 4 cycles (0.82 → 1.96 mA cm⁻²) and then fell 8% by
  cycle 9 (1.81). At the top of cycle 9 (0.75 V vs Hg/HgO) it reached 5.94 mA cm⁻² at η = 0.434–0.435 V (iR-free over
  B1's R_u range on the same setup). The current there includes charging and redox current, so in this state D1's
  η₁₀ exceeds about 0.43 V. High-frequency current noise is 0.4–0.6 µA in cycles 1–8 and 2.0 µA in cycle 9: this file is
  clean, and the noisy trials are not in hand.
- **Across disks** (single disks on different days; not registered): η₁₀ is 0.365 V on A1, 0.316 V on B1 and above
  about 0.43 V on D1. In uncompensated CVs at 0.65 V vs Hg/HgO the currents fall in the same order: B1 5.9–7.9 mA cm⁻²
  on cycles 5–7 (before its activation), A1 4.1–4.4 from cycle 23 on, D1 2.1–2.2 on cycles 3–9.

**Reading.** B1's activity is that of a thick oxyhydroxide film grown from the alloy during cycling; its activation
is a growth in electroactive charge. Whether other metals leave the film under oxygen evolution or iron from the
electrolyte enters it is not settled by these files; a post-test composition of the face, or a run in purified KOH,
would separate the two.

## Notes for the campaign

- **Protocol differences on B1** against the 2026-10-25 routine: activation CVs under live compensation (A1's had
  none) and 25 of them; no EIS between the activation and the LSVs; 4 sweeps, 2 stopped early; the C_dl window; no
  holds (allowed: holds on one disk per code). The primary sweep is unaffected (choice 6).
- **Not in hand:** the first C_dl set on B1, any runs between 17:51 and 19:59, and code D's noisy trials. Statuses for
  those are decided blinded, from the files, when they arrive.
- **Completeness at the lock (open, Frank).** An alloy is complete with at least 3 disks over at least 2 counted days.
  The order given to the bench on 2026-10-25 (B, D, E, then C, then two more disks of A, then F) gives codes B–F one
  disk each, so by the 2026-11-03 lock only code A can be complete, and K1, K2 and every ranking are not evaluable as
  registered. Either the registered outcome stands (the report says the measurements were not complete at the lock),
  or a dated departure, written before the remaining disks are measured, sets what single-disk values may show.

## Update 2026-11-01 (later): every measured disk used

Frank withdrew the lock rule's completeness requirement the same day (dated decision of 2026-11-01 in
s8-oer-analysis-2026-10-19.md; the "kept, not reported" status and the open question above no longer apply). Rerun:
`results/s8_oer/day2_2026-10-30/readout_blinded_2026-11-01_all-data.json` (lock 2026-11-05). Codes A and B are
measured (n = 1 each: η₁₀ 0.3650 and 0.3160 V), C–F not yet; criterion basis `ordering` (no replicate disks, so no
pooled SD). Every disk value is as in the earlier readout.

## Update 2026-11-01 (later): codes A, B and D unblinded for the report

At Frank's request to report code B's result, codes A, B and D were unblinded the same day, and their values went into
the report (Section 4.6) under alloy names. The code-to-alloy map stays in the private key. Codes C, E and F stay
blinded; runs of every code are still accepted or rejected from the instrument record before their values are read.
