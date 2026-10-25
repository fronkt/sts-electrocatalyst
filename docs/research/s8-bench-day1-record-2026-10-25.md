# S8 bench, day 1 (2026-10-24): disk A1 (record of 2026-10-25)

Status: **blinded** (per code; the code key is private). The registered readout has been run on these files; the day is
**not counted** yet, because the bench has not supplied its RHE calibration (choice 7 as amended on 2026-10-25,
[s8-oer-analysis-2026-10-19.md](s8-oer-analysis-2026-10-19.md)). Everything under "Exploratory" is outside the
registered endpoints. Under lock-rule item 3 ([s8-electrode-lock-rule-2026-10-16.md](s8-electrode-lock-rule-2026-10-16.md))
the numbers of an incomplete alloy are kept here, dated, and do not enter the report.

## What arrived

- **Files.** From the Tackett group (Forney Hall, Purdue), received 2026-10-25: 18 EC-Lab `.mpr` data files, 3 `.mgr`
  settings files and one photograph of the disk after the run. EC-Lab 11.62. One disk, A1, measured 2026-10-24 from 12:04
  to 16:47. The raw files stay in the private data directory; each exported table logs its source file's SHA-256, and the
  readout records the SHA-256 of every file it reads.
- **Cell.** 1 M KOH purged with argon, carbon rod counter electrode, Hg/HgO reference, 1,600 rpm. Electrolyte, electrodes
  and reference are in the file names; the argon purge and the rotation rate come from the bench (rotation is not stored
  in the files).
- **Not in the files.** No RHE calibration, no IrO2 run, no blank. The settings fields hold a stale EC-Lab template
  (reference "SCE", electrolyte "NaCl (0.2M)", electrode "Au/Pd", comment "Fe(CN)6 5 mM", electrode area 0.001 cm²) and are
  ignored; the file names and the bench's account govern. One settings file (`SampleA_EIS-MIR-LSV_04`) has no data file.
- **Sequence on A1.**
  1. Activation: 63 CVs at 50 mV/s, no live iR. The window widened during the first ~15 cycles to −1.25 to 0.75 V vs Hg/HgO.
  2. 3 CVs, −1.25 to 0.70 V, live compensation Rcmp = 6.545 Ω.
  3. 4 LSV sweeps, −1.20 to 0.70 V at 5 mV/s, back to back in one file; each starts in the hydrogen-evolution region.
  4. EIS at 0.70 V vs Hg/HgO (R_hf 5.558 Ω, so Rcmp was 118% of it).
  5. 2 CVs set to 0.75 V that stopped near 0.717 V with 250 mA excursions: current runaway under over-compensation
     (status failed; not an analysed technique).
  6. C_dl CVs, −0.10 to 0.20 V at 5, 10, 25, 50, 75 and 100 mV/s.
  7. Four 15-min holds at 0.64, 0.66, 0.68 and 0.70 V vs Hg/HgO, Rcmp = 4.42 Ω.
  8. EIS at 0.70 V (R_hf 5.398 Ω) and 4 CVs.
- **Photograph.** The face is dark brown-purple after the run; the side wall is unchanged.

## Registered readout (blinded)

Files: `results/s8_oer/day1_2026-10-24/readout_blinded_2026-10-25.json` and the manifest it read,
`manifest_2026-10-25.csv` (paths relative to the private data directory; tables exported with
`src/echem/s8_mpr_export.py`, the four holds joined with `--concat`).

```
PYTHONPATH=src python src/echem/s8_oer_readout.py --manifest <data>/manifest.csv --lock 2026-11-03 \
    --ir-hw-verified "<the check below>" --out <data>/readout/readout_blinded_2026-10-25.json
```

- **Day 2026-10-24 not counted** (calibration: pH formula, pH 14). A1 therefore has no primary sweep, and code A has 0
  of the 3 disks it needs. When the bench's calibration arrives, `rhe_offset_V` is filled in, the day counts, and every
  η moves by (measured offset − 0.924 V).
- **Run-level values** (offset 0.924 V; 90% iR in total; kept, not reported):

  | Run | η₁₀ (V) | η₁ (V) | j at η = 0.35 V (mA cm⁻²) | Redox flags |
  |---|---|---|---|---|
  | sweep 1 (the primary once the day counts) | 0.3650 | 0.3223 | 4.78 | none |
  | sweep 2 (repeat) | 0.3660 | 0.3222 | 4.65 | none |
  | sweep 3 (repeat) | 0.3661 | 0.3229 | 4.52 | none |
  | sweep 4 (repeat) | 0.3669 | 0.3233 | 4.37 | none |

- **C_dl** 0.191 mF (6 rates, r² 0.997); roughness factor 24.3 at C_s = 0.040 mF cm⁻².
- **Tafel slope: none.** Two of the four holds fall inside the registered 0.05–10 mA cm⁻² window (3.10 and
  8.35 mA cm⁻²); the readout needs at least three.
- **Flags.** All four LSV runs carry `ir_overcompensated` (instrument share 117.8%, added back to 90%).

**The live-iR export check (choice 4).** Under live compensation the exported Ewe follows the programmed potential to
within 0.91 mV, while Rcmp × I reaches 71 mV on the anodic side (122 mV at the cathodic start). At matched current (5,
10, 20 and 30 mA cm⁻²; activation cycles 61–63 against compensated cycles 2–3, 24 points), the compensated CVs sit
below the uncompensated ones by a + R·I with R = 7.48 Ω, a = 0.6 mV, r² = 0.9994. An offset linear in I through about
zero is what applied compensation left out of Ewe gives; with no compensation applied the curves would coincide. The
"Changes after data" entry of 2026-10-25 quotes 0.9 mV + 7.45 Ω from one cycle pair; the 24-point fit agrees. R exceeds
Rcmp by about 0.9 Ω, which fits R_u having fallen by that much between the two runs (the later EIS read 5.6 Ω).

## Exploratory (not registered)

Script `src/scripts/s8_bench_exploratory.py`; output `results/s8_oer/day1_2026-10-24/exploratory.json` and four
`exploratory_*.png` figures. Potentials on the pH-formula offset.

- **The surface kept changing through the day.** EIS at 0.70 V vs Hg/HgO, fitted as R_s + (R_ct ‖ CPE) (residual 1.3%):
  R_ct 8.44 → 4.68 Ω and effective capacitance 0.26 → 0.70 mF between 13:48 and 16:41, while the current at that
  potential rose from 2.9 to 5.2 mA.
- **Activation.** After the window reached its final range, the uncompensated current at 0.70 V vs Hg/HgO peaked at
  cycle 25 (17.3 mA cm⁻²) and was 4% lower by cycle 63.
- **LSV.** Tafel slope between 1 and 10 mA cm⁻² on each sweep: 39.8, 41.0, 40.5 and 40.8 mV/dec (live compensation
  only).
- **Holds.** Tail current 3.10, 8.35, 18.5 and 30.2 mA cm⁻². Against the first 20% of each hold the tail is +143%,
  +18%, +15% and −8%, so the first holds were still activating. Hold over LSV at the same potential: 1.53, 1.30, 1.00 and
  0.60. A line through the two holds inside the window gives 45.4 mV/dec; this is not the registered slope.
- **Pre-OER oxidation wave** in the last CV: peak at 1.21 V vs RHE, in the region of the Co(II)/Co(III) and
  Ni(II)/Ni(III) couples. Charge 1.94 mC cm⁻² over 1.15–1.52 V on a linear baseline (it includes a second broad wave
  near 1.3–1.47 V, so the figure is good to about a factor of two). At one electron per site that is about 20 nmol cm⁻²,
  of order ten monolayers: an electroactive film many layers thick, not a single surface layer.
- **Turnover.** If every one of those sites evolves oxygen, each turns over at least 0.67 s⁻¹ at η = 0.35 V (a lower
  bound; fewer active sites means a higher turnover).

**Reading.** The activity measured is that of a hydrous oxide/oxyhydroxide film grown from the alloy, and it depends on
the disk's history. Three explanations for the fall in R_ct and rise in capacitance during the day compete:
1. the film thickened or roughened under cycling and holds;
2. gas coverage changed;
3. iron from the electrolyte was taken up, a known activator of Ni and Co oxyhydroxides.

A blank and, if needed, a run in purified KOH would separate the third from the first two. None of this changes a
registered rule: the primary sweep is each disk's first, and every disk gets the same routine.

## Notes for the campaign

- **Protocol difference on A1.** A1's activation (63 cycles, window widened during the first ~15) differs from the
  ~20-cycle routine adopted on 2026-10-25 for later disks. Activity was flat within 4% after about 20 cycles in the final
  window, so the effect on η₁₀ is expected to be small; A1 stays its alloy's disk under choice 6.
- **Asked of the bench on 2026-10-25:** the day's RHE calibration, compensation near 85% of the R_u measured before
  each LSV, IrO2 if possible, one blank per setup.
- **Not asked:** holds at lower potentials. Without at least three holds in the window, the registered Tafel slope stays
  empty for that disk.
