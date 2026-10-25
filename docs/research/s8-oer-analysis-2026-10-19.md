# S8 electrode analysis: from potentiostat files to K1, K2 and the IrO₂ comparison (2026-10-19)

**Status.** Committed before any OER measurement of the six alloys. The last recorded status is "Nothing measured yet"
(Frank, 2026-10-12; [lock rule](s8-electrode-lock-rule-2026-10-16.md)). Frank, 2026-10-19: "do 1-3 and 5", where item 3
was this analysis code, committed before any data. The choices in "Choices the freeze leaves open" are proposed. Frank
confirms or changes them before the first measurement, in a dated line here. After data exist, the code changes only
to fix a bug, and each fix is recorded below with its reason.

- **Code:** `src/echem/s8_oer_readout.py`. Synthetic campaign: `src/echem/s8_oer_synthetic.py`.
- **Tests:** `tests/test_s8_oer_readout.py` (35 tests). They cover:
  - recovery of known η, Tafel slope, C_dl and drift;
  - the export styles and every refusal below;
  - the lock-rule cases, spares and time order;
  - the classifiers, with exact-binary threshold cases;
  - Ni34 not moving the threshold;
  - the frozen predictions, checked against the freeze's tables.
- **What the tests cannot check.** The generator shares the readout's iR export convention (choice 4), so no test can
  check that convention. The bench check in choice 4 does.

## What the freeze already fixes (§3, §6, deposited 10.5281/zenodo.23327000)

- **Endpoints.** The primary endpoint is η at 10 mA cm⁻² (geometric), from an LSV at 5 mV s⁻¹ after a fixed CV
  activation. R_u comes from EIS before each LSV, with 90% iR compensation. Secondary endpoints are η at 1 mA cm⁻², the
  steady-state Tafel slope from potential holds, C_dl-normalized activity and the 12 h drift.
- **RHE conversion.** E_RHE = E_Hg/HgO + 0.098 + 0.059 pH, calibrated each bench day.
- **Replicates.** At least 3 coupons per alloy over at least 2 bench days, with IrO₂ and a blank each day.
- **Criterion.** A difference counts only if it exceeds twice the pooled coupon-to-coupon SD.
- **What is judged.** K1, K2, the per-alloy IrO₂ classes and the exploratory items, all with arms A, B, C and the C
  extension's predicted values. The code holds those values as constants, and a test checks them against §3.
- **Ni34.** It enters only the exploratory comparisons and "changes no primary test" (§2).
- **Partial data.** The lock rule decides what is reported when the data are incomplete.

## Choices the freeze leaves open (proposed; for Frank to confirm before the first measurement)

1. **The pooled SD.** It is the within-alloy disk-to-disk SD, pooled over the complete K-set alloys:
   √(Σ(nᵢ − 1)sᵢ² / Σ(nᵢ − 1)), with up to 10 degrees of freedom. Ni34 is left out so that it changes no primary test
   (§2). The same yardstick serves every comparison: K1, K2, IrO₂ (Ni34's included) and the leaders. A pairwise SD from
   two alloys of 3 disks would have only 4 degrees of freedom.
2. **The comparison.** Two alloys are compared by the difference of their mean η₁₀ against twice the pooled SD. A
   difference exactly at the threshold does not count.
3. **η at a current is read at the last upward crossing on the anodic sweep.** That is the point after which the
   current stays above the target. A Ni(OH)₂/NiOOH-type redox peak can cross 1 mA cm⁻² before OER does, so the first
   crossing is reported beside the last one. The two are flagged when they differ by more than 5 mV. η is E − 1.23 V.
4. **iR.** The code removes (0.90 − instrument share) × I × R_u, so 90% is applied once in total. This is right only if
   the exported Ewe already excludes the instrument's live compensation.
   - If it does not, η is under-corrected on days with live compensation: by about 8 mV at 85% live, 1.96 mA and 5 Ω.
   - So the readout refuses any run with live compensation unless `--ir-hw-verified` records how the export convention
     was checked. The check is a dummy cell of known resistance on the bench potentiostat, or the lab's statement.
   - The simplest alternative: the lab records R_u and applies no live compensation (`ir_hw_pct` = 0).
5. **A sweep that never reaches 10 mA cm⁻²** gives that disk no η₁₀. It is reported (`no_eta10_disks`, also printed)
   and does not count toward completeness. *Alternative for Frank:* treat the value as censored at the sweep's maximum
   η. A very inactive alloy could otherwise end up "not evaluated" rather than "least active". The bench plan asks for
   sweeps to at least 10 mA cm⁻², which makes this case unlikely.
6. **Time order** is the day, then the manifest row within that day, whatever order the rows are written in.
   - A disk's primary sweep is its first ok sweep on a counted day, on or before the lock.
   - A repeat is reported and never averaged in, so no run is picked by its result.
   - A spare (`AS`–`FS`) counts as one of its alloy's disks.
   - Tafel and drift take the disk's first ok run of that technique.
7. **Counted day.** A bench day counts if its first ok IrO₂ sweep reaches 10 mA cm⁻² and it has an ok blank sweep.
   That IrO₂ sweep is the day's reference. *(Amended 2026-10-25, see the dated decisions below: a day counts with a
   measured RHE calibration; IrO₂ and blanks are optional.)*
8. **IrO₂ comparison.** Each complete alloy's mean is compared with the mean of the references from the days its
   counted disks were measured, using the same threshold. The classes are lower, not distinguishable and higher. The
   C_dl-normalized version is reported per disk as specific activity, with no class.
9. **K2 classes.** Supported: Cu22 is higher than each of the other four K-set alloys. Contradicted: Cu22 is lower than
   at least one of them. Unresolved: anything else.
10. **Tafel slope.** The steady current is the mean over the last 20% of each hold of at least 30 s. The fit uses the
    holds between 0.05 and 10 mA cm⁻², at least 3 of them.
11. **C_dl.**
    - The point per scan rate is half the anodic minus cathodic current, each branch's current averaged over the
      central 20% of the window. Both branches must cover that band, or there is no point.
    - C_dl is the slope against scan rate, from at least 3 rates, one disk on one day.
    - The roughness factor uses C_s = 0.040 mF cm⁻². Specific activity is j at η = 0.35 V divided by the roughness
      factor.
    - The C_s value is the middle of the 0.020–0.060 mF cm⁻² range used for flat surfaces in alkaline electrolyte. Its
      primary source is still to be confirmed before the report cites one.
12. **Drift.** The slope of the iR-corrected potential over the 12 h hold, after its first 10 min.
13. **Spearman ρ.** Computed with average ranks, only when every alloy the arm ranks is complete (A and B: 6, C: 4, the C
    extension: 5). It is exploratory.
14. **Incomplete alloys.**
    - Their means, SDs and other numbers are kept under `kept_not_reported` and are null everywhere else in the readout.
    - Figure 8 draws an arm's predicted-against-measured points only when that arm's ρ exists.
    - This follows lock-rule item 3.

## Refusals (the readout stops and names the run)

- **Manifest fields.** A missing field the technique needs: `status`, `file`, `R_u_ohm`, `ir_hw_pct` (write 0 if
  none), the RHE calibration, `scan_rate_mV_s` for C_dl, or `area_cm2` for the lab's IrO₂ electrode. Coded disks
  default to the 0.19635 cm² face.
- **Calibration.** An RHE calibration outside 0.85–1.00 V, or more than one calibration on one day.
- **Manifest values.** A day that is not a date, an unknown sample code or technique, or a duplicate run_id.
- **Unreadable rows.** More than max(5, 1%) unreadable rows in a file. Fewer are dropped and counted (`rows_dropped`).
- **Sweep selection.** An LSV file must hold exactly one anodic sweep in the selected cycle, unless the manifest's
  `sweep` names one (added 2026-10-25). The readout stops on:
  - more than one sweep with none named, or none, or fewer sweeps than the one named;
  - a cycle requested from a file without a cycle column;
  - several linked techniques (`Ns`) in one file;
  - fewer than 20 points;
  - no positive current, which suggests a cathodic-positive export.
- **Live iR compensation** without `--ir-hw-verified` (choice 4).

A run that really failed gets a non-"ok" status with its reason. That decision is made blinded, before unblinding.

## Blinding

The bench measures disks coded A–F, and the key is private. Without `--key` the readout is per code. It includes
completeness, means, the IrO₂ classes and an SD pooled over every complete code; that SD is marked provisional,
because which code is Ni34 is unknown. It contains nothing that needs an alloy's identity.

**Order of use:**
1. Run the readout blinded.
2. Settle every data-quality question at that stage: statuses, re-runs, spares.
3. Unblind once, with the key.

## Run manifest

The manifest is a CSV with one row per potentiostat file, transcribed from the lab's run log. Lines starting with `#`
are comments; a comment containing "SYNTHETIC" marks synthetic data.

| Column | Meaning |
|---|---|
| `run_id` | unique name |
| `file` | path relative to the manifest; empty only for rows recorded without analysis (EIS, activation) |
| `sample` | disk code `A1`–`F3`, spare `AS`–`FS`, `IrO2` or `blank` |
| `day` | bench day, YYYY-MM-DD |
| `technique` | `lsv`, `hold`, `cdl`, `stability`, `eis` or `activation` |
| `scan_rate_mV_s` | scan rate (required for `cdl`) |
| `rhe_offset_V` | E_RHE − E_Hg/HgO measured that day, one value per day; if empty, `pH` is used through the freeze's formula, and the readout records which |
| `pH` | electrolyte pH, used only when `rhe_offset_V` is empty |
| `R_u_ohm` | R_u from the EIS before this run |
| `ir_hw_pct` | % iR compensation the instrument applied live (0 if none; at most 150; above 90 is flagged as over-compensation and added back) |
| `area_cm2` | required for IrO₂; default 0.19635 for coded disks |
| `rpm`, `cycle` | rotation; the cycle to use (default: the last) |
| `sweep` | for a file holding several anodic sweeps: which one (1 = the first); empty when the file holds one |
| `status` | `ok`, or the reason the run fails a check (the run is then reported, not used) |
| `notes` | free text |

**Files.** The readout reads BioLogic EC-Lab text exports (`.mpt`, dot or comma decimals) and CSV/TXT tables whose
header names time, potential and current. Native `.mpr` files must be exported to text first. Current is read in mA
unless the column name says A.

## Use

```
PYTHONPATH=src python src/echem/s8_oer_readout.py --manifest <data>/manifest.csv --lock <lock date> --out results/s8_oer/readout_blinded.json
PYTHONPATH=src python src/echem/s8_oer_readout.py --manifest <data>/manifest.csv --lock <lock date> --key <private key> [--ir-hw-verified "<how>"] --out results/s8_oer/readout.json
```

- **Lock date.** The registered lock was 2026-10-25 (lock rule); the dated line of 2026-10-25 moved it to 2026-11-03.
  The readout reports whether `--lock` matches it. Moving the lock is Frank's decision and needs a dated line.
- **Native .mpr files.** `src/echem/s8_mpr_export.py` writes them out unchanged as CSV under EC-Lab's column names, and
  logs each source file's SHA-256. `--concat` joins consecutive techniques of one sequence, such as a series of holds
  saved one file per step, into one table.
- **Figure 8.** The report's `fig8_alloy_test.py` reads `results/s8_oer/readout.json`. Until data exist, it draws a
  synthetic campaign under a SYNTHETIC banner.

## Review before the first commit (2026-10-19)

An independent review found two blockers, now fixed:
- **One empty cell.** A single empty cell turned the threshold into NaN and every class into "not distinguishable".
  Unreadable rows are now dropped and counted, and NaN raises in `compare` and `pooled_sd`.
- **Ni34 in the pool.** Ni34's spread set the K1/K2 threshold. The pool is now the K-set only (choice 1).

Also fixed:
- time order (choice 6);
- sweep and segment selection;
- required manifest fields;
- the C_dl midpoint clamp;
- the live-iR refusal;
- incomplete alloys' numbers;
- day normalization;
- calibration checks;
- tests that passed without testing their claim.

The tests then found one more: an unreadable cycle number was cast to a garbage integer. Every column used now counts
toward the unreadable rows.

**After the first commit, still before any data (2026-10-19).** Commit 6bb3d49 was pushed with one failing test,
because a shell pipeline hid pytest's exit code. The failure was C_dl recovered 2% low on one synthetic disk. Each
point read one interpolated current, which carries the full per-point noise.
- **Fix.** Each branch's current is now averaged over the central 20% of the window (choice 11).
- **Check.** Over five synthetic noise seeds, the worst roughness-factor error is 0.34% (2.0% before), and all 35 tests
  pass.

## Dated decisions, 2026-10-25 (Frank), after one disk was measured

**What already exists.** One disk of code A was measured on 2026-10-24 (Tackett group, Purdue, BioLogic EC-Lab 11.62), the
day before this line. Nobody ran IrO2 or a blank that day. Under choice 7 as amended below (item 4), the day counts once the
bench supplies its RHE calibration. Its files are kept as received.

1. **Lock date.** The data lock moves from 2026-10-25 to **2026-11-03**, the deadline the bench was given on 10-22. The
   lock rule (s8-electrode-lock-rule-2026-10-16.md) is otherwise unchanged. The readout is run with `--lock 2026-11-03`.
2. **Electrode format.** Rotating inserts (5.00 mm faces, wire-EDM cut, Pine-type RDE holder) at **1,600 rpm**, in
   **1 M KOH purged with argon**, against a carbon counter electrode and an Hg/HgO reference. The frozen potted stationary disk
   is not used.
3. **Blinding departure.** On 2026-10-25 I sent the operator (a) the element set of each code and (b) the three registered
   predicted orders (arm B primary, arm A, and the arm C DFT+U order), while codes B-F were still unmeasured. From that day
   on, the operator is no longer blind to the prediction. The code-to-alloy key with compositions was not sent. Statuses and
   re-run decisions are still made blinded in the readout (run blinded, then unblind once).
4. **The 14 readout choices** (s8-oer-analysis-2026-10-19.md) are **confirmed as proposed**, with these specifics:
   - Choice 4 (iR): the bench uses live compensation (EC-Lab MIR). In the 10-24 files the exported Ewe follows the
     programmed potential to within 0.9 mV, while I x Rcmp reaches about 70 mV. So the exported Ewe already excludes the
     compensated drop, and the code's formula applies with `ir_hw_pct` = 100 x Rcmp / R_u per run. This is the
     `--ir-hw-verified` record. The bench was asked to keep Rcmp near 85% of the R_u measured before each LSV.
   - Choice 5: a sweep that never reaches 10 mA cm-2 gives no eta_10 (not censored).
   - The RHE calibration is the bench's value for each day. If one is missing, the day uses 0.098 + 0.059 pH, flagged.
   - **Choice 7 amended:** a bench day counts if it has a valid RHE calibration. A blank is run once on the bench setup and
     again only if the holder or electrolyte batch changes; it is not required per day. IrO2 is used when it exists but is
     not required. If no same-bench IrO2 is run, the freeze §6 IrO2 comparison is not evaluable as registered, and the
     report compares measured eta_10 with published IrO2 values in 1 M KOH as descriptive context only (departure from
     freeze §6). The readout's counted-day check changes to match (recorded under "Changes after data").
5. **Per-disk routine from 2026-10-25 on**, kept identical for every disk: EIS; about 20 activation CVs in the bench's
   window (-1.25 to 0.75 V vs Hg/HgO, 50 mV/s); EIS; 2 LSV sweeps at 5 mV/s; C_dl CVs (6 rates, -0.10 to 0.20 V vs Hg/HgO);
   holds on one disk per code only; one blank per setup (item 4); IrO2 if the bench can run it. Each disk's primary sweep stays its first ok sweep
   (choice 6).
6. **Readout fix owed before it runs** (recorded under "Changes after data" when made): the bench's LSV files hold several
   sweeps with no cycle column, which the readout currently refuses. The fix lets the manifest name the sweep (first sweep =
   primary) and leaves every other rule unchanged.

## Changes after data (bug fixes only, each with its reason)

**2026-10-25, after the bench's first files (disk A1, 2026-10-24), before any readout of them.** Each change follows the
dated decisions above or the form of the bench's files; no decision rule moves.

1. **Named sweep.** The bench's LSV files hold several sweeps back to back, with no cycle column, which the readout
   refused. A new manifest column, `sweep`, names the anodic sweep to use (1 = the first). Several sweeps with none
   named still stop the readout, so no sweep is ever picked by the code. Each sweep is its own manifest row; the first
   ok one on a counted day stays the disk's primary sweep (choice 6), and the others are reported as repeats.
2. **Counted day (choice 7 as amended).** A day counts when every analysed run used that day has a measured RHE
   calibration. IrO₂ and blanks are no longer required. The day's first ok IrO₂ sweep that reaches 10 mA cm⁻² is still
   its reference when one exists. An alloy's IrO₂ comparison uses the references of its days where they exist, lists
   the days without one, and is not evaluated when there are none. `counted_day_rule`, each day's `calibration` and
   the list of blank runs are written to the readout.
3. **Instrument share above 90%.** On 2026-10-24 the bench's live compensation was Rcmp = 6.545 Ω against an R_u of
   5.558 Ω from the EIS right after the LSVs, a share of 118%. The manifest check allowed at most 90%, a plausibility
   bound. The correction itself, E − (0.90 − share) × I × R_u, is exact for any share when the exported Ewe excludes
   the compensated drop, so a share above 0.90 is added back to the registered 90%. The bound is now 150%, to catch
   typing errors, and each run above 90% is flagged (`ir_overcompensated`).
4. **Registered lock** set to 2026-11-03, per the dated decisions.
5. **Export of native files.** `src/echem/s8_mpr_export.py` (new) writes the bench's `.mpr` files out unchanged as
   CSV, which the readout already reads.

**The export check for live iR (choice 4)**, recorded with `--ir-hw-verified`, rests on two observations in the
2026-10-24 files:
- Under live compensation the exported Ewe follows the programmed potential to within 0.9 mV, while Rcmp × I reaches
  about 70 mV. So Ewe does not include the compensated drop.
- At matched current, the compensated CVs (Rcmp 6.545 Ω, cycles 2–3) sit below the uncompensated activation CVs
  (cycles 61–63, about 25 min earlier) by 0.9 mV + 7.45 Ω × I over 5–30 mA cm⁻². The offset is linear in I with a
  near-zero intercept, as expected only if the compensation was applied and left out of Ewe. Had it not been applied,
  the two would coincide.

**Check.** The sweep-selection test now also checks that a named sweep of a multi-sweep file gives the single sweep's
η₁₀, and that a sweep number beyond the file stops the readout. New tests: a day without IrO₂ or blank still counts;
a day on the pH formula alone does not; with no IrO₂ at all, K1 and K2 are unchanged and the IrO₂ comparison is not
evaluated; shares of 0, 85% and 118% all leave the registered 10% residual; 117.8% is accepted and flagged; 151%, a
negative share and sweep 0 are refused. The test of the old rule (a day without IrO₂ does not count) was replaced by
the first of these. All 41 tests pass.
