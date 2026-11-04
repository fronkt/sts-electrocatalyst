# S8 bench, day 3 (2026-11-03): disks D2, E1 and F1 (record of 2026-11-04)

Status: the registered readout was run blinded on every file received, then keyed (the keyed output stays in the
private data directory with the key). Day 2026-11-03 **counts** on the bench's stated reference value (dated decision
2026-10-26, [s8-oer-analysis-2026-10-19.md](s8-oer-analysis-2026-10-19.md)). Every measured disk is used (dated decision
2026-11-01, lock 2026-11-05).

## What arrived

- **Files.** From the Tackett group, received 2026-11-04: one archive with three bench folders (`SampleD_New`,
  `SampleE_SameSetup`, `SampleF_SameSetup`) holding 53 EC-Lab `.mpr` data files (5 of them hold no data), with `.mgr`
  graph settings, `.mps` method settings and `.sta` status files, plus a photo of code-C disks. EC-Lab 11.62, device VSP.
  Measured 2026-11-03: E1 from 12:18 to 15:44, D2 from 20:07 to 21:48, F1 from 22:39 to 01:03 on 11-04 (one bench
  session, recorded as day 2026-11-03). The raw files stay in the private data directory with a SHA-256 list; each
  exported table logs its source file's SHA-256, and the readout records the SHA-256 of every file it reads.
- **The bench's note.** Codes D, E and F were measured. Code C was not: most of its disks showed corrosion and flaky
  deformation on both faces, and gave a connection error after fitting. The photo shows three code-C disks, one face
  with brown patches and one disk with a chipped edge and a pit. No repeats are possible before the report.
- **Disk D2.** The bench folder is named `SampleD_New`; it is taken as a second code-D disk (the day-2 file was D1).
  Not confirmed with the bench; it changes no value, since D1 has no LSV.
- **Not in hand.** D2's sequence `EISLSV_Final` (about 21:15, between the LSVs and the C_dl CVs) arrived as `.mgr`
  graph settings only, with no data files.
- **Cell.** As on days 1 and 2 by the agreed routine (1 M KOH, carbon counter, Hg/HgO reference, 1,600 rpm; rotation
  and gas are not stored in the files). The EIS before the activation CVs ran at open circuit on D2 (−0.496 V vs Hg/HgO)
  and F1 (−0.299 V), and at 0.70 V on E1; R_u is its high-frequency intercept in each case. The `.mps` settings files
  were saved after some runs and do not always match them (E1's first CV ran to −1.40/0.80 V; its `.mps` reads −1.40/
  0.75 V); windows and rates here are read from the data (`control/V`).

## Sequences

| Disk | Start | Sequence | Content |
|---|---|---|---|
| E1 | 12:18 | `CV1` | 18 CVs, −1.40 to 0.80 V vs Hg/HgO, 50 mV/s, no live iR; stopped (its LSV holds no data) |
| E1 | 12:44 | `EISMIRCVLSV` | EIS at 0.70 V (R_hf 7.785 Ω); live Rcmp 6.545 Ω; 21 CVs −1.30 to 0.75 V; 4 LSV sweeps −1.20 to 0.70 V at 5 mV/s, all to the programmed end |
| E1 | 13:46 | `EISCVLSVOnly` | EIS at 0.70 V (R_hf 6.657 Ω); CVs under Rcmp 5.695 Ω; stopped after 87 s (its LSV holds no data) |
| E1 | 13:55 | `EISCV-FinalLSV` | 3 CVs under Rcmp 5.950 Ω; one LSV sweep −1.20 to 0.70 V |
| E1 | 15:21 | `EISCV-Cdlscans` | EIS at open circuit (+0.050 V, R_hf 6.571 Ω); 3 CVs; C_dl CVs at 5–100 mV/s between −0.60 and −0.40 V, starting from and returning to open circuit |
| E1 | 15:40 | `CVFinal` | EIS at open circuit (R_hf 6.589 Ω); 3 CVs, no live iR |
| D2 | 20:07 | `CVEIS` | EIS stopped at 954 Hz (15 points); its CV holds no data |
| D2 | 20:09 | `EISMIRCVLSV` | EIS at open circuit (R_hf 9.347 Ω); live Rcmp 7.650 Ω; 21 CVs −1.30 to 0.75 V; 4 LSV sweeps −1.20 to 0.70 V, all to the programmed end |
| D2 | 21:39 | `CVCdl` | 3 CVs, no live iR; C_dl CVs at 5–100 mV/s, −0.90 to −0.70 V (an empty file of this sequence started at 21:34) |
| F1 | 22:39 | `EISMIRCVLSV` | EIS at open circuit (R_hf 5.357 Ω); live Rcmp 4.505 Ω; 21 CVs −1.30 to 0.75 V; 4 LSV sweeps −1.20 to 0.70 V, all to the programmed end |
| F1 | 23:53 | `CVCdlScans` | EIS at open circuit (R_hf 6.123 Ω); 3 CVs under Rcmp 5.950 Ω; C_dl CVs at 5–100 mV/s, −0.60 to −0.30 V |
| F1 | 00:50 | `CVCdlScansRepeat-toconfirm` | EIS at open circuit (R_hf 6.324 Ω); 3 CVs under Rcmp 5.355 Ω; the same C_dl set again (an empty LSV file started at 00:49:58) |

## Statuses

Set from the instrument record (points, programmed window, sweep ends, EIS span) before any endpoint was read:

- **Failed:** the five files with no data (E1 `CV1_02_LSV`, E1 `EISCVLSVOnly_04_LSV`, D2 `CVEIS_02_CV`,
  D2 `CVCdl_08_CV`, F1 `CVCdlScansRepeat-toconfirm_04_LSV`) and D2's first EIS (stopped at 954 Hz).
- **Repeat, not pooled:** F1's second C_dl set. The readout fits all of a disk's ok C_dl rows from one day together, and
  a repeat is never averaged in, so the second set carries the status `repeat` and is reported below on its own.
- **Ok:** every other run. One flag was checked and dropped: E1's 10 mV/s C_dl file first looked current-free (largest
  |I| under 1 µA), but it holds 1,708 distinct nonzero currents, as small as a 10 mV/s non-faradaic current should be.
- The private code key was opened on 2026-11-04, to check which alloys K2 involves, before these statuses were set.
  The statuses rest on file structure alone (no data, a stopped run), and the element set of each code had been known
  since 2026-10-25.

## Export change (made before any value of E1's C_dl was seen)

E1's C_dl CVs start at open circuit (+0.05 V vs Hg/HgO), cycle between the programmed vertices −0.60 and −0.40 V, and
return to open circuit. The readout takes a C_dl window from the full range of the selected cycle, so the open-circuit
legs moved the centre of the band to −0.275 V, outside the cycling, and every rate returned "a branch does not cover
the central band of the window". `src/echem/s8_mpr_export.py` gained `--window LO HI`, which keeps only the rows whose
programmed potential lies between the vertices (1 mV tolerance; tests in `tests/test_s8_mpr_export.py`); E1's six C_dl
tables were exported again that way (`*_window.csv`, about 900 of about 1,700 rows dropped from each, logged in
`export_log.json`). The readout is unchanged. D2's and F1's C_dl CVs start inside their windows and need no trimming.

## Registered readout

Files: `results/s8_oer/day3_2026-11-03/readout_blinded_2026-11-04.json` and the manifest it read,
`manifest_2026-11-04.csv` (paths relative to the private data directory). The keyed readout
(`readout_KEYED_PRIVATE_2026-11-04.json`) stays in the private data directory.

```
PYTHONPATH=src python src/echem/s8_oer_readout.py --manifest <data>/manifest.csv --lock 2026-11-05 \
    --ir-hw-verified "<days 1-2 text; the day-3 check below>" --out <data>/readout/readout_blinded_2026-11-04.json
```

- **Day 2026-11-03 counted** (calibration: bench, 0.924 V).
- **The live-iR export check on day 3 (choice 4).** Under live compensation (Rcmp 4.505–7.650 Ω) the exported Ewe
  follows the programmed potential to within 0.96 mV in the LSVs and 1.13 mV in the CVs, while Rcmp × |I| reaches 322
  and 376 mV. Ewe therefore again excludes the compensated drop. Appended to the stored `--ir-hw-verified` text.
- **R_u and instrument share.** E1 7.785 Ω (84.1%), D2 9.347 Ω (81.8%), F1 5.357 Ω (84.1%), each from the EIS just
  before the activation CVs, about 30 min before the first sweep; E1's later single sweep uses the 13:46 EIS (6.657 Ω,
  89.4%).
- **LSV endpoints** (90% iR in total; potentials on 0.924 V):

  | Disk | Run | η₁₀ (V) | η₁ (V) | j at η = 0.35 V (mA cm⁻²) | Sweep end |
  |---|---|---|---|---|---|
  | E1 | sweep 1 (primary) | 0.3134 | 0.2721 | 49.2 | |
  | E1 | sweeps 2, 3, 4 (repeats) | 0.3116, 0.3113, 0.3099 | 0.2715, 0.2710, 0.2704 | 67.3, 62.6, 81.0 | |
  | E1 | 13:55 single sweep (repeat) | 0.3138 | 0.2721 | 45.4 | |
  | F1 | sweep 1 (primary) | 0.3690 | 0.3124 | 4.98 | |
  | F1 | sweeps 2, 3, 4 (repeats) | 0.3668, 0.3647, 0.3643 | 0.3108, 0.3092, 0.3076 | 5.35, 5.78, 6.00 | |
  | D2 | sweep 1 (primary) | none | 0.3238 | 1.90 | 6.38 mA cm⁻² at η 0.393 V |
  | D2 | sweeps 2, 3, 4 (repeats) | none | 0.3217, 0.3206, 0.3194 | 2.01, 2.05, 2.10 | 7.19, 7.33, 7.43 mA cm⁻² at η 0.393 V |

  No redox flag fired. On every disk the repeats run slightly more active than the primary sweep (E1 by 3.5 mV, F1 by
  4.7 mV at sweep 4): activation was still going on.
- **C_dl** (reported only): D2 0.0853 mF (6 rates, r² 0.996; −0.90 to −0.70 V vs Hg/HgO, 0.02 to 0.22 V vs RHE);
  E1 0.0093 mF (6 rates, r² 0.999; −0.60 to −0.40 V, 0.32 to 0.52 V vs RHE); F1 0.0430 mF (6 rates, r² 0.991; −0.60
  to −0.30 V, 0.32 to 0.62 V vs RHE). Each window differs from A1's (−0.10 to 0.20 V) and B1's, and all three lie below
  the oxyhydroxide couples, so the roughness factors and specific activities in the readout do not compare across
  disks. F1's repeat set is not yet fitted on its own.
- **Tafel slope: none** (no holds on day 3).
- **Codes.** A, B, E and F are measured (n = 1 each). D has disks but no η₁₀: D1 has no LSV and D2's sweeps end
  below 10 mA cm⁻². C has no disk. Criterion basis `ordering` (no replicate disks).
- **Keyed readout.** K1 and K2 come out `not_evaluated`, both for lack of code D's η₁₀ (K2 also lacks code C's).
  The measured order over the four alloys with η₁₀ is codes E, B, A, F; the exploratory items are in the keyed file.

## Readings by bound (beyond the coded gate)

The coded gate needs an η₁₀ for every alloy K1 or K2 involves. A sweep that ends below 10 mA cm⁻² still bounds η₁₀
from below, with no value imputed: D2's η₁₀ exceeds 0.393 V on every sweep (and D1's exceeds about 0.43 V, from its
day-2 CVs, exploratory). Every measured η₁₀ (0.313 to 0.369 V) lies below 0.393 V. Under the key this decides both
tests on the ordering basis:

- **K1:** code D is less active than both alloys it is compared with, by more than 0.077 V: the A-consistent pattern.
- **K2:** code D is less active than the alloy K2 names, so K2 is contradicted. One K-set alloy less active than it is
  enough, so code C's missing value cannot change this.

Whether the report states K1 and K2 by bound is Frank's decision; the coded readout is unchanged.

- **The top two are not resolved.** Codes E and B differ by 2.7 mV, one disk each, on different days. That is the size
  of B1's change between its two R_u choices (2.4 mV) and smaller than E1's drift over its four sweeps (3.5 mV). The
  readout prints the leader as distinguishable only because the ordering basis has a zero threshold.

## Still open

- D2's `EISLSV_Final` data files.
- The exploratory script (`s8_bench_exploratory.py`) has not been run on day 3.
- F1's repeat C_dl set, fitted on its own.
