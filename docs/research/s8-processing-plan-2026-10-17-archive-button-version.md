> **Archived 2026-10-17.** Superseded the same day by [s8-processing-plan-2026-10-17.md](s8-processing-plan-2026-10-17.md) after Frank's melt photos showed that Fort Wayne Metals cast rods from a 250 g crucible melt, not 200 g buttons ([melt record](s8-melt-record-2026-10-17.md)). This copy is the button version as of commit 73305fe, unchanged below this note.

# S8 processing plan: from button to electrode, 2026-10-17

**Status.** Working plan for turning the six batch-1 buttons into electrodes. It changes no frozen value. Frozen values are quoted from the [stage-1 freeze](s8-stage1-freeze-proposal-2026-10-07.md) (published 2026-10-12, 10.5281/zenodo.23327000) and the [melt plan](s8-melt-plan-2026-10-07.md). Each addition here is marked:
- **record:** an extra measurement or record; it changes nothing frozen;
- **departure:** it would change a frozen value, so it needs Frank's dated line before any OER measurement.

## Where things stand (2026-10-17)

| Item | State | Source |
|---|---|---|
| Cu8Cr23Mn35Co34, Ni31Cr29Cu5Mn35, Fe25Co25Ni25Cr25 | Melted 2026-10-09 and 2026-10-12. Charges, remelts and any anneal not recorded | freeze §1b |
| Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31, Cu22Fe30Co32Mn15 | Melted by 2026-10-17 (Frank, 2026-10-17: "All alloys were melted."). Dates, charges, remelts and any anneal not recorded | Frank |
| OER measurements | None recorded | [lock rule](s8-electrode-lock-rule-2026-10-16.md) |
| Machining request to Song Cai (FWM) | Sent 2026-10-13: 5 mm × 4 mm wire-EDM cores after the 1,050 °C / 24 h homogenization, about 0.1 mm off the front face, 3 + 1 spare per alloy plus an offcut. No reply recorded | Frank's Gmail |
| Tackett, 2026-10-13 | Machine the samples to Pine's quick-change disk (AFED) drawing: "If you can get something close, that should be ok." One rotator, so samples run one at a time. Timeline "a little tight" | Frank's paste |
| Electrode format | Open: rotating insert, or the frozen potted stationary disk | freeze §6 format rule |
| Lab location | Open: the 2026-10-07 ship-to is Purdue (Forney Hall), and Tackett's signature now reads University of Pittsburgh | |
| Data lock | Oct 25 | lock rule |

Pine's drawing is vendor material and stays out of this repository. FWM has it from the 2026-10-13 email.

## Sequence for each button

### 1. Log the as-melted button (record)

- Stamp or scribe a button ID. Photograph both sides and note which side faced the hearth.
- Weigh to 0.01 g and compare with the charge on the [weigh sheet](s8-weigh-sheet-2026-10-08.md). Mn accounts for most of the evaporation, so the mass loss is an upper bound on the Mn loss (spatter also counts).
- **Mn pre-check from the mass.** The +4% Mn over-charge is 2.73 g (Cu8, Ni31) and 1.17 g (Cu22), so a button whose Mn loss equals the over-charge weighs 200.0 g. Each extra gram lost lowers Mn by about 0.33 at.% (Cu8, Ni31) or 0.45 at.% (Cu22). A button of at least 199.0 g therefore has a mean Mn within about −0.5 to +0.9 at.% of target, well inside ±2 at.%, before any EDS. This assumes spatter has the bulk composition.

### 2. Cut an as-cast slice (record)

- Before any anneal, cut one 3 mm slice from the rim (wire EDM or a wet abrasive saw).
- Polish one piece. Take BSE images and an EDS map at the top, middle and bottom, and measure the secondary dendrite arm spacing λ. λ decides how much the 24 h anneal can do (step 4).
- Keep one piece as the as-cast reference for the report. The rest goes to step 3.
- For every button: the same, if it has not been annealed. If it has, record what was done (temperature, time, atmosphere, cooling) and go to step 5.

### 3. Check for local melting at 1,050 °C (record; the five Cu-bearing alloys)

**Why.** In the Cu alloys the last metal to freeze is Cu-rich, and in three of them it is also Mn-rich. Cu–Mn has a congruent melting minimum near 873 °C at about 38 at.% Mn (refs 1, 2). Cu–Cr has a eutectic near 1,076 °C (ref 3). If those regions melt locally during the anneal, they leave pores and Cu-rich films, which is worse than the as-cast state. Dissolved Co, Cr, Fe and Ni raise these temperatures, so local melting is possible but not expected.

| Alloy | Concern | Check |
|---|---|---|
| Cu8Cr23Mn35Co34, Ni31Cr29Cu5Mn35, Cu22Fe30Co32Mn15 | Cu-rich and Mn-rich last liquid | Yes |
| Cu26Ni9Cr31Co33 | Cu–Cr eutectic about 26 °C above the anneal | Yes |
| Ni34Fe6Cu29Co31 | Cu-rich, no Mn or Cr | Yes (cheap) |
| Fe25Co25Ni25Cr25 | No Cu | No |

- **Preferred: DSC.** About 50 mg of as-cast metal, 10 K/min to 1,150 °C under Ar. The onset of the first endotherm is the local melting temperature. Pass if it is at or above 1,075 °C (a 25 °C margin).
- **Without DSC: a 1 h trial.** 1 h at 1,050 °C in the same furnace and atmosphere, water quench, section, BSE at 500–2,000×. Fail if it shows rounded pores or re-solidified pockets in the interdendritic regions, or Cu-rich films along grain boundaries, that the as-cast slice does not show.
- **Pass:** step 4 as frozen. **Fail:** stop that button. The schedule is then set from the measured onset (a departure, needing Frank's dated line).
- **A low-temperature pre-hold is not a fix.** With the diffusion data in step 4, diffusion at 850 °C is about 50–200 times slower than at 1,050 °C, so 12 h at 850 °C moves atoms only 0.3–1.3 µm. A pre-hold helps only just below the measured onset.

### 4. Homogenize (frozen: 1,050 °C, 24 h, Ar, then quench; freeze §5)

- **One load** for every button not yet annealed (freeze §5: "all six alloys are melted and annealed in one batch"). All six are melted, so all six can go in together.
- **One temperature for all six (frozen).** Freeze §5 gives a single schedule, not one per alloy, and one load needs one temperature.
  - The ceiling is set by the Cu alloys: their last-to-freeze regions melt lowest (step 3). Cu26's Cu–Cr margin is about 26 °C.
  - Fe25Co25Ni25Cr25 (no Cu, no Mn) melts far above 1,050 °C and could take a hotter anneal. It also diffuses slowest of the measured alloys (CoCrFeNi rows below). Its four elements usually segregate only weakly on casting, so 1,050 °C should still be enough; step 2 measures it.
  - A per-alloy temperature would be a departure: a second load, and different thermal histories for the alloys being compared.
- **Argon, not vacuum (record).** Mn has the highest vapour pressure of the six elements. Under vacuum it evaporates freely; under argon its loss is limited by diffusion through the gas. Use flowing high-purity Ar with Ti getter chips upstream, or a sealed quartz tube back-filled with Ar if the 51 mm buttons fit.
- **Temperature (record).** Thermocouple at the load. Count the 24 h from the load reaching 1,040 °C. Overshoot no more than 10 °C, because Cu26's Cu–Cr margin is about 26 °C. Keep the trace.
- **Separation (record).** Buttons must not touch each other. Stand them on an alumina plate or Mo/Ta foil.
- **Quench (frozen; details are a record).** Agitated water, with no more than 10 s from furnace to water. The quench keeps the 1,050 °C state; σ phase and other intermetallics form at lower temperatures in Cr- and Mn-rich alloys.
- **Mass after the quench (record).**

**What 24 h at 1,050 °C can do (record).** These are bulk tracer diffusion coefficients from radiotracer measurements on CoCrFeNi and CoCrFeMnNi (refs 4, 5), using the Arrhenius parameters tabulated in ref 6 (Table 4), evaluated at 1,323 K. The fraction of segregation left is exp(−4π²Dt/λ²), for a sinusoidal profile whose wavelength λ is the dendrite arm spacing.

| Alloy measured | Element | D at 1,050 °C (m²/s) | √(Dt), 24 h (µm) | Left at λ = 20 µm | 50 µm | 100 µm |
|---|---|---|---|---|---|---|
| CoCrFeNi | Cr | 7.4e-16 | 8.0 | 0.002 | 0.36 | 0.78 |
| CoCrFeNi | Fe | 5.4e-16 | 6.8 | 0.010 | 0.48 | 0.83 |
| CoCrFeNi | Ni | 1.1e-16 | 3.1 | 0.38 | 0.86 | 0.96 |
| CoCrFeNi | Co | 1.5e-16 | 3.6 | 0.27 | 0.81 | 0.95 |
| CoCrFeMnNi | Mn | 2.9e-15 | 15.9 | 0.000 | 0.02 | 0.37 |
| CoCrFeMnNi | Cr | 1.1e-15 | 9.5 | 0.000 | 0.24 | 0.70 |
| CoCrFeMnNi | Fe | 8.2e-16 | 8.4 | 0.001 | 0.33 | 0.76 |
| CoCrFeMnNi | Co | 3.5e-16 | 5.5 | 0.05 | 0.62 | 0.89 |
| CoCrFeMnNi | Ni | 6.2e-16 | 7.3 | 0.005 | 0.43 | 0.81 |

These numbers are proxies. None of the six alloys is one of these two, Cu is not in the table, and interdiffusion differs from tracer diffusion.

How to read the table:
- **Fine dendrites (λ ≈ 20 µm) are removed.** At most 5% of the segregation is left, except Ni and Co in CoCrFeNi (27–38%).
- **Coarse dendrites (λ of 50–100 µm) are not.** Between 2% and 96% is left. The top of a 200 g button cools slowest and has the coarsest dendrites.
- So step 2 measures λ, and step 6 measures what is left.
- **Option (a departure; Frank's call): a longer hold if λ is above about 40 µm.** 72 h triples Dt (λ = 50 µm, Cr in CoCrFeMnNi: 24% left becomes 1.4%), but it costs two days that the Oct 25 lock cannot absorb.
- **Default:** keep 24 h as frozen, and report the residual segregation as part of the material state.

**Does it matter for OER?** The 5 mm face spans about 100–250 dendrite arms across, so each disk averages to the button's composition. Residual segregation changes the surface locally: Cr-rich dendrite cores sit next to Cu- and Mn-rich interdendritic regions. It is reported as a property of the material ("homogenized cast alloy, residual segregation X at.%"). Disk-to-disk differences come mainly from where in the button a disk was cut (macro-segregation), which annealing does not remove; step 7 handles that.

### 5. Trim and section (record)

- Remove at least 1 mm from the top, bottom and rim. This takes off:
  - the oxide scale;
  - the Mn-depleted skin (Mn's diffusion distance in 24 h is about 16 µm, plus evaporation);
  - the hearth chill zone;
  - the top shrinkage.
- Cut one 3 mm slab through the centre, top to bottom. This is the acceptance offcut for step 6.
- Mark the core positions on both halves, and photograph them before cutting.

### 6. Acceptance checks (frozen; freeze §5)

The frozen checks:
- SEM-EDS composition within ±2 at.% of nominal for every element, and XRD phases recorded.
- A miss is re-melted once. If it misses again, it is kept, flagged and analysed at its measured composition. It is never replaced by another composition.

Added (record):
- **EDS fields.** At least 6 area fields, each at least 0.5 × 0.5 mm, at 20 kV, on the slab: top, middle and bottom, each at the centre and the edge. Judge pass/fail on the mean per element, and report mean ± SD.
- **EDS overlaps.** The K lines of neighbouring elements overlap: Cr Kβ with Mn Kα, Mn Kβ with Fe Kα, Fe Kβ with Co Kα, Co Kβ with Ni Kα. Standardless EDS on these alloys can be off by 1–2 at.% for major elements, which is comparable to the tolerance. A result within 1 at.% of a limit gets a second method (XRF or ICP-OES) if FWM has one.
- **Residual segregation.** An EDS line scan at least 5λ long (λ from the as-cast slice, step 2) at the top (coarsest) and at mid-height. A complete homogenization leaves no dendrite contrast in BSE and a flat profile, so the scan length comes from the as-cast λ. Report max − min per element.
- **BSE.** Second phases (Cu-rich, σ), porosity, and any sign of local melting.
- **XRD on a polished face, 20–100° 2θ.**
  - Under Cu Kα, Cr, Mn, Fe and Co fluoresce and raise the background. Use an energy-discriminating detector, or a Co or Mo tube, if one is available.
  - A Cu-rich FCC phase (a = 3.615 Å) sits close to the matrix peaks (about 3.56–3.60 Å). In the five Cu alloys, scan slowly around (111) and (200) to look for a shoulder.
- **A re-melted button** gets its own anneal, recorded as a separate load.

### 7. Cut the electrodes (frozen: at least 3 test + 1 spare per alloy, 5.00 mm × 4.00 mm cylinders, 0.196 cm² face, wire EDM; freeze §6, melt plan)

- Wire-EDM cores parallel to the button axis, at least 3 mm from the rim and from the acceptance slab. Use a rough cut plus skim passes to reach the drawing's diameter tolerance.
- Slice the cores to 4.00 mm. After trimming, each core gives two or three cylinders.
- **Which positions become test disks (record).** Take all test cylinders from **mid-height**, from cores spread around the button. Top and bottom differ most from each other (chill zone, coarse top dendrites, macro-segregation). Taking every test disk from one height keeps those differences out of the disk-to-disk SD, which is the yardstick of every comparison (2× pooled SD, freeze §6). Spreading the cores around the button still samples the whole button. Top and bottom cylinders become spares. This rule must be fixed before any measurement.
- Label each cylinder on its back face with alloy, core and height (for example `CU8-K2-M`).
- Cut 6 per alloy: 3 test, 1 spare, and 1 or 2 more so a damaged disk can be replaced from the same height. Cu8 also supplies the optional EC-MS disk (freeze §6).

### 8. Prepare the working face (frozen: one face polished below the EDM recast layer, the same finish on every disk; melt plan)

- Remove at least 0.1 mm from the working face. This takes off the EDM recast layer and the Cu/Zn picked up from brass wire.
- **The same sequence for every disk:** SiC 320, 600, 1200 (wet), then 3 µm diamond, then 0.05 µm alumina on a cloth. The drawing allows either a 0.05 µm polish or a 600-grit face; use one for all.
- **Clean:** 5 min ultrasonic in DI water, then 5 min in ethanol; dry.
- **Consistency (record):** the same person, day and consumables for every disk, written down.
- **Drawing checks:** face flatness, parallelism to the back, and the back-edge chamfer.
- **Diameter (record).** Measure each one with a micrometer, three readings. The area error is small (±0.02 mm gives ±0.8%), but the record removes it.
- **Ask the lab** whether they re-polish with 0.05 µm alumina just before each run (common RDE practice). If so, that last step happens there, and every disk starts from a fresh surface.
- **Storage:** each disk in its own labelled vial, in a desiccator. Polish all the disks of a batch on the same day, so they age alike.

### 9. Mount (depends on the format choice; freeze §6 rule)

| | Rotating insert | Potted stationary disk (frozen fallback) |
|---|---|---|
| Mounting | None; press-fit at the lab | Silver-paint back wire, continuity checked before potting, epoxy over the edges and back, polished flush |
| Tolerance | The drawing's diameter tolerance | None |
| Throughput | One rotator, one disk at a time | Parallel channels, if the lab has them |
| Bubbles at 10 mA cm⁻² | Cleared by rotation | Present; η at 1 mA cm⁻² is the cleaner secondary |

- **Steps 1–8 don't wait for the choice:** the cylinders are the same either way. The choice is needed before step 9, by about Oct 22.
- **Potted:** a 4 mm tall cylinder can be potted as it is (the freeze specifies a 5.00 mm disk, not its thickness).
- **Insert:** test-fit one disk per alloy in the shroud on arrival.

### 10. Ship (record)

- Confirm where the rotator and Jyotisman Rath are (Purdue or Pitt) before shipping. If Pitt, freeze §6's lab line ("the Tackett group, Purdue") needs a dated correction.
- If Purdue, hand delivery from Fort Wayne (about a 2 h drive) is fastest.
- Pack one vial per disk, face up and padded, with a packing list (disk ID, position, diameter). Commit a copy of the list here.

### 11. Records before the first OER measurement

- Freeze §1b: how the first three buttons were processed.
- Freeze §6 format rule: the format chosen, Tackett's answer and the reason, in a dated line.
- **Per button (record):** masses, furnace load and trace, the DSC or trial result, λ, the EDS table, XRD, and the disk map.
- **Optional (record):**
  - A seeded random run order (alloy × bench day), committed before the disks arrive, so that alloy and day are not confounded on one rotator.
  - Coded vial labels (A–F), with the key kept by Frank, so the operators don't know the predictions.

## Schedule against the Oct 25 data lock

Best case, starting Monday:

| Day | Work |
|---|---|
| Mon 10-19 | Song: melt dates and processing of all six buttons. Log masses, cut as-cast slices, run DSC or the 1 h trials |
| Tue 10-20 | Trial SEM in the morning; homogenization load in (24 h) |
| Wed 10-21 | Quench, trim, acceptance slab, EDS and XRD; EDM starts |
| Thu 10-22 | EDM and slicing, face prep; format decision |
| Fri 10-23 | Final polish (and potting, if stationary); delivery |
| Sat–Sun 10-24/25 | First measurements |

Rotator time needed, assuming about 2 h per disk for activation CV, EIS, LSV and Tafel holds (to be confirmed with the lab):
- **Full set:** 18 test disks (about 36 h), plus IrO₂ and a blank each bench day, plus a 12 h hold on at least one disk per alloy (72 h). That is about 4.5–5 days of continuous rotator time.
- **K1 only** (Cu8, Ni31, Fe25): 9 disks (about 18 h) plus 3 holds (36 h), about 2.5 days.

Even in the best case the first measurement is on Oct 24. Neither set can be complete by Oct 25, so under the lock rule (2026-10-16) every comparison would be reported as not evaluated.

## Decisions for Frank

1. **The lock date, now, before any data exist.** Moving it before any measurement does not depend on the data. The STS entry is due about Nov 5.
2. **Electrode format, by Oct 22.** With the Oct 25 lock, only stationary disks on parallel channels could come close. With a later lock, the rotating insert is the cleaner measurement.
3. ~~**K1 first?**~~ Resolved 2026-10-17: all six are melted, so all six go in one load as frozen.
4. **A longer anneal**, if λ is above about 40 µm. It costs two days.
5. **A new anneal schedule**, if step 3 shows local melting.

## Questions for Song (only what is not yet recorded)

- When were Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 and Cu22Fe30Co32Mn15 melted?
- For all six: the charged masses, the number of remelts, the button masses, and whether any anneal was done (temperature, time, atmosphere, cooling).
- Is a DSC available at FWM?
- The furnace: argon flow or sealed? A thermocouple at the load? A water quench tank next to it?
- The 2026-10-13 questions (EDM diameter tolerance, timing), if still open.

The anneal plan, the Mn over-charge, the hold and the safety items are not re-asked; Song knows them from in-person talks (Frank, 2026-10-08).

## Open items from other documents

- Cr(VI) risk assessment: supervisor names, signatures and dates are still blank (freeze §7). The anneal, EDM and polishing steps are listed in it.
- Post-mortem XRD and SEM-EDS after OER (freeze §6): keep the spare disks and the as-cast and homogenized offcuts as references.

## References

1. Cu–Mn congruent minimum at 34.6 wt% Mn and 873 °C: as-cast Cu–Mn alloy study, Purdue open-access dissertation 431, https://docs.lib.purdue.edu/open_access_dissertations/431
2. Congruent point at 34.6 ± 1.4 wt% (about 38 ± 2 at.%) Mn, after Goken (1993), as cited in US patent 10,507,520.
3. Cu–Cr eutectic at 1,076 °C (about 1.3–1.5 wt% Cr): NASA NTRS 19850007567.
4. M. Vaidya, S. Trubel, B.S. Murty, G. Wilde, S.V. Divinski, J. Alloys Compd. 688 (2016) 994–1001, doi:10.1016/j.jallcom.2016.07.239.
5. M. Vaidya, K.G. Pradeep, B.S. Murty, G. Wilde, S.V. Divinski, Acta Mater. 146 (2018) 211–224, doi:10.1016/j.actamat.2017.12.052.
6. S.V. Divinski, A. Pokoev, N. Esakkiraja, A. Paul, "A mystery of 'sluggish diffusion' in high-entropy alloys: the truth or a myth?", arXiv:1804.03465, Table 4.
