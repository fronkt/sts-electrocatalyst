# S8 processing plan: from cast rod to electrode, 2026-10-17

**Status.** Working plan for turning the six batch-1 castings into electrodes. It changes no frozen value. Frozen values are quoted from the [stage-1 freeze](s8-stage1-freeze-proposal-2026-10-07.md) (published 2026-10-12, 10.5281/zenodo.23327000) and the [melt plan](s8-melt-plan-2026-10-07.md). Each addition here is marked:
- **record:** an extra measurement or record; it changes nothing frozen;
- **departure:** it would change a frozen value, so it needs Frank's dated line before any OER measurement.

> **Revised 2026-10-17, same day.** Frank's melt photos show that Fort Wayne Metals cast **rods** from a 250 g crucible melt, not 200 g buttons, and that much of the metal went to scrap that can come back for testing ([melt record](s8-melt-record-2026-10-17.md)). The button version is archived at [s8-processing-plan-2026-10-17-archive-button-version.md](s8-processing-plan-2026-10-17-archive-button-version.md).

## Where things stand (2026-10-17)

| Item | State | Source |
|---|---|---|
| Castings | All six melted and cast as rods (FWM IDs ARC00149–ARC00154). Ni31 and Cu22 cast badly (thin, necked or stepped sections); Cu26 is two short pieces with a copper-coloured skin; Cu8, Fe25 and Ni34 are full-length rods | [melt record](s8-melt-record-2026-10-17.md) |
| Scrap | "A lot of it has been scrapped, but we can get those scraps back to test" (Frank) | Frank, 2026-10-17 |
| Melt dates | Labels: Cu8 10/8, Cu26 10/12, Fe25/Ni34/Cu22 10/13, Ni31 10/14. Freeze §1b records Cu8, Ni31 and Fe25 on 10-09 and 10-12. To confirm with Song | melt record |
| Any anneal | Not recorded | |
| OER measurements | None recorded | [lock rule](s8-electrode-lock-rule-2026-10-16.md) |
| Machining request to Song Cai (FWM) | Sent 2026-10-13, written for buttons (cores through the button height). Needs restating for rods (step 7). No reply recorded | Frank's Gmail |
| Tackett, 2026-10-13 | Machine the samples to Pine's quick-change disk (AFED) drawing: "If you can get something close, that should be ok." One rotator, so samples run one at a time. Timeline "a little tight" | Frank's paste |
| Electrode format | Open: rotating insert, or the frozen potted stationary disk | freeze §6 format rule |
| Lab location | Open: the 2026-10-07 ship-to is Purdue (Forney Hall), and Tackett's signature now reads University of Pittsburgh | |
| Data lock | Oct 25 | lock rule |

Pine's drawing is vendor material and stays out of this repository. FWM has it from the 2026-10-13 email.

## Material rule (record)

- **Rods make disks.** Only sound rod at least 5.5 mm across becomes electrodes, and the composition acceptance (step 6) is done on rod material.
- **Scraps take the destructive tests:** the as-cast reference (step 2) and the local-melting check (step 3). That leaves all the sound rod for disks, which matters most for Ni31.
- Scrap is used only if it is labelled by alloy. If a scrap is crucible remnant (the last metal to freeze, possibly reacted with the crucible), its composition is not taken as the alloy's.

## Sequence for each alloy

### 1. Log the castings (record)

- Photograph every piece (done 2026-10-17; photos held privately).
- For each piece, measure:
  - mass (0.01 g);
  - length;
  - diameter, with calipers at least every 2 cm;
  - **the sound length at least 5.5 mm across** (no necks, laps, cracks or visible pores). This sets how many 5.00 mm disks the alloy can give (step 7).
- **Mn check from mass.** It works only if every piece is weighed, scrap included. The total against the charge then bounds the Mn loss, as in the archived button version. Otherwise Mn is judged by EDS (step 6).

### 2. As-cast reference (record)

- Use a scrap piece of the alloy, or, if there is none, a 2 mm transverse slice cut from the end of a rod.
- Polish it, take BSE images and an EDS map, and measure the secondary dendrite arm spacing λ.
- Rods cast into a mold freeze faster than a 200 g button, so λ should be finer, and the 24 h anneal more complete (step 4). The measurement decides.
- Keep the piece as the as-cast reference for the report.

### 3. Check for local melting at 1,050 °C (record; Cu-bearing alloys, on scrap)

**Why.** In the Cu alloys the last metal to freeze is Cu-rich, and in three of them it is also Mn-rich. Cu–Mn has a congruent melting minimum near 873 °C at about 38 at.% Mn (refs 1, 2). Cu–Cr has a eutectic near 1,076 °C (ref 3). If those regions melt locally during the anneal, they leave pores and Cu-rich films. Dissolved Co, Cr, Fe and Ni raise these temperatures, so local melting is possible but not certain.

| Alloy | Concern | Check |
|---|---|---|
| Cu22Fe30Co32Mn15 | Cu-rich and Mn-rich last liquid; Fe and Co barely dissolve Cu | Yes |
| Cu26Ni9Cr31Co33 | Cu–Cr margin about 26 °C; copper-coloured skin shows Cu separating | Yes |
| Cu8Cr23Mn35Co34 | Cu-rich and Mn-rich last liquid | Yes |
| Ni31Cr29Cu5Mn35 | 5% Cu in a Ni-rich matrix | If step 2 shows separate Cu-rich pockets |
| Ni34Fe6Cu29Co31 | Cu-rich; Ni dissolves Cu; no Mn or Cr | If step 2 shows separate Cu-rich pockets |
| Fe25Co25Ni25Cr25 | No Cu | No |

- **Preferred: DSC.** About 50 mg of scrap, 10 K/min to 1,150 °C under Ar. The onset of the first endotherm is the local melting temperature. Pass if it is at or above 1,075 °C (a 25 °C margin).
- **Without DSC: a 1 h trial.** One furnace run at 1,050 °C for all trial pieces together, with the same atmosphere as step 4, then a water quench, a section, and BSE at 500–2,000×. Fail if it shows rounded pores or re-solidified pockets in the interdendritic regions, or Cu-rich films along grain boundaries, that the as-cast reference does not show.
- **Scrap makes a conservative test.** A scrap that cooled slowly is coarser and more segregated than the rods, so if it does not melt, the rods will not.
- **Pass:** step 4 as frozen. **Fail:** stop that alloy. The schedule is set from the measured onset (a departure, needing Frank's dated line).
- **A low-temperature pre-hold is not a fix.** With the diffusion data in step 4, diffusion at 850 °C is about 50–200 times slower than at 1,050 °C, so 12 h at 850 °C moves atoms only 0.3–1.3 µm. A pre-hold helps only just below the measured onset.

### 4. Homogenize (frozen: 1,050 °C, 24 h, Ar, then quench; freeze §5)

- **One furnace run for all six** (freeze §5: "all six alloys are melted and annealed in one batch").
- **One temperature for all six (frozen).** Freeze §5 gives a single schedule, and one load needs one temperature.
  - The ceiling is set by the Cu alloys (step 3). Cu26's Cu–Cr margin is about 26 °C.
  - Fe25Co25Ni25Cr25 (no Cu, no Mn) melts far above 1,050 °C and could take a hotter anneal. It also diffuses slowest of the measured alloys (CoCrFeNi rows below). Its four elements usually segregate only weakly on casting, so 1,050 °C should still be enough; step 2 measures it.
  - A per-alloy temperature would be a departure: a second load, and different thermal histories for the alloys being compared.
- **Rods fit sealed tubes (record).** Cut the sound sections into lengths that fit a quartz tube, one tube per alloy. Back-fill with Ar and add Ti getter chips. The alloys never touch.
- **Getters and wraps never touch the samples (record).**
  - Ti (or Zr) getter chips sit in their own alumina cup or foil packet. Ti forms liquid with Ni and Cu below 1,050 °C (Ti–Ni eutectic about 942 °C), and Co is close, so a chip touching a sample would melt into it.
  - **Stainless steel foil wrap** (Frank's question, 2026-10-17) is acceptable as an oxidation barrier, especially in an air furnace:
    - Use a grade rated above 1,050 °C.
    - A separator between sample and foil (alumina paper, a small alumina boat, or an inner wrap of Ta or Mo foil) stops the foil diffusion-bonding to the sample. Without one, the foil exchanges Fe, Ni, Cr, Mn and Cu with the outer tens of µm. Machining removes that ("fine too, since we'll machine the surface off": Zonkai, 2026-10-17, relayed by Frank).
    - **Exception: Ni31's thin sections.** Turning them to 5.00 mm may remove only about 0.25 mm per side. Keep them off the foil (on ceramic, or loosely wrapped), and check the affected depth on a cross-section after the anneal.
    - Flush the pouch with Ar before folding it shut, and put Ti chips inside, separated from the samples.
    - No paper, charcoal or other carbon inside: Cr and Mn would pick up carbon.
    - Use one pouch per alloy, labelled by position on the tray (marker ink burns off).
  - **Setup available (Frank, 2026-10-17):** an argon furnace and stainless foil; no Ta or Mo foil.
    - Purge well with Ar before heating, and keep it flowing for the 24 h.
    - Samples sit on ceramic if the shop has any (an alumina boat or plate, a crucible, or ceramic fibre paper), under a loose stainless foil tent. The tent's Cr takes up residual O₂ and keeps Mn vapour near the samples.
    - Without ceramic, a direct wrap is acceptable for the thick rods, not for Ni31's thin pieces.
    - Ti chips, if used, go in their own stainless foil packet beside the samples.
  - **Setup chosen (Frank, 2026-10-17):** a stainless steel boat with stainless wires to pull it in and out of the argon furnace, and Ti chips as oxygen getters, not touching the samples.
    - **Alloys apart.** Alloys do not touch each other in the boat: space them out, or use bent-wire dividers.
    - **Marks that survive the heat.** Ink burns off, so mark the alloys with filed notches or different cut lengths on ends that are cut off later, and record the key. Cu8, Fe25 and Ni34 are similar long rods.
    - **The pull.** Use a doubled or heavy wire, since stainless softens at 1,050 °C. Rehearse the pull while cold, and keep a large water bucket at the furnace mouth so the boat goes from the hot zone into the water within about 10 s. Wear a face shield and gloves.
    - **Ti chips.** They sit near the Ar inlet, on a sacrificial scrap of stainless foil rather than on the sample boat, because Ti can stick to or react with stainless at 1,050 °C.
    - **Optional:** a loose stainless foil lid, and Ni31's pieces resting on bent wires so they touch the boat only at a few points (its usable metal is the thick stubs).
  - **Record exactly what was used:** furnace atmosphere, foil grade, separator, getter. Freeze §5 says "Ar". An Ar-flushed pouch in an air furnace keeps the samples under Ar, but write it down as such.
  - **Quench with the foil on:** drop the pouch into the water and open it underwater; a single loose wrap lets water in fast. The few extra seconds do not matter for σ, which forms over hours.
- **Argon, not vacuum (record).** Mn has the highest vapour pressure of the six elements. Under vacuum it evaporates freely; under argon its loss is limited by diffusion through the gas.
- **Temperature (record).** Thermocouple at the load. Count the 24 h from the load reaching 1,040 °C. Overshoot no more than 10 °C. Keep the trace.
- **Quench (frozen; details are a record).** Break the tubes in agitated water. A rod 8–11 mm across cools quickly through its whole section. The quench keeps the 1,050 °C state; σ phase and other intermetallics form at lower temperatures in Cr- and Mn-rich alloys.

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
- **Coarse dendrites (λ of 50–100 µm) are not.** Between 2% and 96% is left.
- Rod castings should be at the fine end; step 2 measures λ, and step 6 measures what is left.
- **Option (a departure; Frank's call): a longer hold if λ is above about 40 µm.** 72 h triples Dt (λ = 50 µm, Cr in CoCrFeMnNi: 24% left becomes 1.4%), but it costs two days.
- **Default:** keep 24 h as frozen, and report the residual segregation as part of the material state.

**Does it matter for OER?** The 5 mm face spans hundreds of dendrite arms, so each disk averages to the rod's composition. Residual segregation changes the surface locally; it is reported as a property of the material ("homogenized cast alloy, residual segregation X at.%"). Disk-to-disk differences come mainly from where along the rod a disk was cut, which annealing does not remove; step 7 handles that.

### 5. Trim (record)

- Cut about 5 mm off each end of every sound section: the shrinkage end, the chill end, and any stub or broken tip.
- Cut out laps, necks, cracks and pitted lengths (Ni31, Cu22).
- The as-cast surface comes off in step 7, when the rod is turned down to 5.00 mm.

### 6. Acceptance checks (frozen; freeze §5)

The frozen checks:
- SEM-EDS composition within ±2 at.% of nominal for every element, and XRD phases recorded.
- A miss is re-melted once. If it misses again, it is kept, flagged and analysed at its measured composition. It is never replaced by another composition.

Added (record):
- **Where.** A transverse slice from each end of the sound section, and from the middle if it is longer than 6 cm, because the two ends of a rod can differ. On each slice, take at least 3 area fields (centre, mid-radius, edge), each at least 0.5 × 0.5 mm, at 20 kV. Judge pass/fail on the mean per element, and report mean ± SD.
- **EDS overlaps.** The K lines of neighbouring elements overlap: Cr Kβ with Mn Kα, Mn Kβ with Fe Kα, Fe Kβ with Co Kα, Co Kβ with Ni Kα. Standardless EDS on these alloys can be off by 1–2 at.% for major elements, which is comparable to the tolerance. A result within 1 at.% of a limit gets a second method (XRF or ICP-OES) if FWM has one.
- **Residual segregation.** An EDS line scan at least 5λ long (λ from step 2) on each slice. A complete homogenization leaves no dendrite contrast in BSE and a flat profile. Report max − min per element.
- **BSE: what to look for in these castings.**
  - Internal porosity and laps (Ni31, Cu22).
  - Cu-rich phase (Cu26, Cu22, Ni34).
  - Undissolved Cr particles (Ni31).
  - Oxide or carbide inclusions from the crucible.
  - Any sign of local melting.
- **XRD may not be possible at FWM; EDS will be (Frank, 2026-10-17).**
  - Acceptance pass/fail is EDS only, so it is unaffected. XRD is a record ("XRD phases recorded"), and no decision before OER depends on it.
  - Keep one polished homogenized slice per alloy for XRD elsewhere (Purdue, the electrochemistry lab or PFW), any time before the report lock.
  - Only if no XRD is done before the report does it become a departure, needing a dated line.
  - Meanwhile, BSE and EDS maps show second phases and their composition. EBSD, if FWM's SEM has it, identifies crystal structure (FCC, BCC, σ) on the same slice.
- **XRD on a polished transverse slice, 20–100° 2θ.**
  - Under Cu Kα, Cr, Mn, Fe and Co fluoresce and raise the background. Use an energy-discriminating detector, or a Co or Mo tube, if one is available.
  - A Cu-rich FCC phase (a = 3.615 Å) sits close to the matrix peaks (about 3.56–3.60 Å). In the five Cu alloys, scan slowly around (111) and (200) to look for a shoulder.
- **A re-melt** gets its own anneal, recorded as a separate load.

### 7. Make the disks (frozen: at least 3 test + 1 spare per alloy, 5.00 mm × 4.00 mm, 0.196 cm² face; freeze §6, melt plan)

- **Turn or centerless-grind** the trimmed sound section down to 5.00 mm, to the drawing's diameter tolerance, then part off 4.00 mm slices. Wire EDM also works. Turning removes the outer 1.5–3 mm: the as-cast skin, the Mn-depleted layer, the fume coating and Cu26's copper-coloured skin.
- The working face is a **transverse cross-section** of the rod.
- **Material needed per alloy:** 6 disks × (4 mm + about 1 mm kerf) = about 30 mm of sound rod at least 5.5 mm across, plus about 10 mm for the acceptance slices. That is **about 4 cm**.

| Alloy | From the photos (to be measured) |
|---|---|
| Cu8Cr23Mn35Co34 | Full-length rod: enough |
| Fe25Co25Ni25Cr25 | Full-length rod: enough |
| Ni34Fe6Cu29Co31 | Full-length rod: enough, avoiding the lapped length |
| Cu26Ni9Cr31Co33 | Two short pieces: probably enough; measure |
| Cu22Fe30Co32Mn15 | Thick section: probably enough; check inside for pores |
| **Ni31Cr29Cu5Mn35** | **Thin sections may be below 5 mm; only the stubs and bulges may qualify. At risk** |

- **If an alloy is short:** fewer disks (3 test disks is the frozen minimum; the spare goes first), or a re-melt of the same composition. That is Frank's call and needs a dated line; it is a new casting, not a new composition. Ni31 is in K1, so a short Ni31 decides K1.
- **Which disks become test disks (record).** Take the test disks from consecutive positions in the middle of the longest sound section. Record each disk's distance from the rod's bottom end. Disks from the ends become spares. This keeps end-to-end differences out of the disk-to-disk SD, which is the yardstick of every comparison (2× pooled SD, freeze §6). This rule must be fixed before any measurement.
- Label each disk on its back face with alloy and position (for example `CU8-R1-075` = rod 1, 75 mm from the bottom).
- Cu8 also supplies the optional EC-MS disk (freeze §6).

### 8. Prepare the working face (frozen: polished below any machining damage, the same finish on every disk; melt plan)

- Remove at least 0.1 mm from the working face. After EDM this takes off the recast layer and the Cu/Zn picked up from brass wire; after turning it removes the parting marks.
- **The same sequence for every disk:** SiC 320, 600, 1200 (wet), then 3 µm diamond, then 0.05 µm alumina on a cloth. The drawing allows either a 0.05 µm polish or a 600-grit face; use one for all.
- **Clean:** 5 min ultrasonic in DI water, then 5 min in ethanol; dry.
- **Consistency (record):** the same person, day and consumables for every disk, written down.
- **Drawing checks:** face flatness, parallelism to the back, and the back-edge chamfer.
- **Diameter (record).** Measure each one with a micrometer, three readings.
- **Ask the lab** whether they re-polish with 0.05 µm alumina just before each run (common RDE practice). If so, that last step happens there, and every disk starts from a fresh surface.
- **Storage:** each disk in its own labelled vial, in a desiccator. Polish all the disks of a batch on the same day, so they age alike.

### 9. Mount (depends on the format choice; freeze §6 rule)

| | Rotating insert | Potted stationary disk (frozen fallback) |
|---|---|---|
| Mounting | None; press-fit at the lab | Silver-paint back wire, continuity checked before potting, epoxy over the edges and back, polished flush |
| Tolerance | The drawing's diameter tolerance | None |
| Throughput | One rotator, one disk at a time | Parallel channels, if the lab has them |
| Bubbles at 10 mA cm⁻² | Cleared by rotation | Present; η at 1 mA cm⁻² is the cleaner secondary |

- **Steps 1–8 don't wait for the choice:** the disks are the same either way. The choice is needed before step 9, by about Oct 22.
- **Potted:** a 4 mm tall disk can be potted as it is (the freeze specifies a 5.00 mm disk, not its thickness).
- **Insert:** test-fit one disk per alloy in the shroud on arrival.

### 10. Ship (record)

- Confirm where the rotator and Jyotisman Rath are (Purdue or Pitt) before shipping. If Pitt, freeze §6's lab line ("the Tackett group, Purdue") needs a dated correction.
- If Purdue, hand delivery from Fort Wayne (about a 2 h drive) is fastest.
- Pack one vial per disk, face up and padded, with a packing list (disk ID, position, diameter). Commit a copy of the list here.

### 11. Records before the first OER measurement

- **Freeze §1b:** how the castings were made, and the confirmed melt dates (the labels and §1b disagree; [melt record](s8-melt-record-2026-10-17.md)).
- **Freeze §6 format rule:** the format chosen, Tackett's answer and the reason, in a dated line.
- **Any re-melt or short alloy:** a dated line.
- **Per alloy (record):** piece masses and sound lengths, the furnace load and trace, the DSC or trial result, λ, the EDS table, XRD, and the disk map.
- **Optional (record):**
  - A seeded random run order (alloy × bench day), committed before the disks arrive, so that alloy and day are not confounded on one rotator.
  - Coded vial labels (A–F), with the key kept by Frank, so the operators don't know the predictions.

## Schedule against the Oct 25 data lock

Best case, starting Monday:

| Day | Work |
|---|---|
| Mon 10-19 | Get the scraps back. Measure every rod and its sound length; decide on a Ni31 re-melt. As-cast references and DSC or 1 h trials on scrap. Restate the machining request for rods |
| Tue 10-20 | Trial SEM in the morning; homogenization run in (24 h). A Ni31 re-melt, if chosen, happens now and needs its own anneal |
| Wed 10-21 | Quench, trim, acceptance slices, EDS and XRD; turning starts |
| Thu 10-22 | Turning and parting, face prep; format decision |
| Fri 10-23 | Final polish (and potting, if stationary); delivery |
| Sat–Sun 10-24/25 | First measurements |

Rotator time needed, assuming about 2 h per disk for activation CV, EIS, LSV and Tafel holds (to be confirmed with the lab):
- **Full set:** 18 test disks (about 36 h), plus IrO₂ and a blank each bench day, plus a 12 h hold on at least one disk per alloy (72 h). That is about 4.5–5 days of continuous rotator time.
- **K1 only** (Cu8, Ni31, Fe25): 9 disks (about 18 h) plus 3 holds (36 h), about 2.5 days.

Even in the best case the first measurement is on Oct 24. Neither set can be complete by Oct 25, so under the lock rule (2026-10-16) every comparison would be reported as not evaluated. A Ni31 re-melt adds at least a day to Ni31.

## Decisions for Frank

1. **The lock date, now, before any data exist.** Moving it before any measurement does not depend on the data. The STS entry is due about Nov 5.
2. **Ni31: re-melt or not, on Monday, once its sound length is measured.** Ni31 is in K1. If it can't give at least 3 sound disks, K1 needs a new Ni31 casting.
3. **Electrode format, by Oct 22.** With the Oct 25 lock, only stationary disks on parallel channels could come close. With a later lock, the rotating insert is the cleaner measurement.
4. **A longer anneal**, if λ is above about 40 µm. It costs two days.
5. **A new anneal schedule**, if step 3 shows local melting.

## Questions for Song (only what is not yet recorded)

- **The melt:** melter (arc or induction), crucible material, charge mass per alloy (the 250 g crucible), how the rods were cast (mold diameter, drop, suction or pour), and the number of remelts.
- **Ni31 (ARC00154) and Cu22 (ARC00153):** what went wrong during melting or casting?
- **Scrap:** what went to scrap for each alloy (crucible remnant, failed pours, trimmed ends), and can all of it come back, labelled by alloy?
- **Dates:** are the label dates (10/8, 10/12, 10/13, 10/14) the melt dates? §1b records Cu8, Ni31 and Fe25 on 10-09 and 10-12.
- **Anneal:** was any casting annealed?
- **Equipment:** is a DSC available? Can FWM seal quartz tubes, or run a flowing-Ar furnace with a water quench? Can FWM turn or centerless-grind rods to 5.00 mm and part off 4.00 mm slices?

The anneal plan, the Mn over-charge, the hold and the safety items are not re-asked; Song knows them from in-person talks (Frank, 2026-10-08).

## Open items from other documents

- Cr(VI) risk assessment: supervisor names, signatures and dates are still blank (freeze §7). The anneal, machining and polishing steps are listed in it.
- Post-mortem XRD and SEM-EDS after OER (freeze §6): keep the spare disks, the scraps and the as-cast and homogenized slices as references.

## References

1. Cu–Mn congruent minimum at 34.6 wt% Mn and 873 °C: as-cast Cu–Mn alloy study, Purdue open-access dissertation 431, https://docs.lib.purdue.edu/open_access_dissertations/431
2. Congruent point at 34.6 ± 1.4 wt% (about 38 ± 2 at.%) Mn, after Goken (1993), as cited in US patent 10,507,520.
3. Cu–Cr eutectic at 1,076 °C (about 1.3–1.5 wt% Cr): NASA NTRS 19850007567.
4. M. Vaidya, S. Trubel, B.S. Murty, G. Wilde, S.V. Divinski, J. Alloys Compd. 688 (2016) 994–1001, doi:10.1016/j.jallcom.2016.07.239.
5. M. Vaidya, K.G. Pradeep, B.S. Murty, G. Wilde, S.V. Divinski, Acta Mater. 146 (2018) 211–224, doi:10.1016/j.actamat.2017.12.052.
6. S.V. Divinski, A. Pokoev, N. Esakkiraja, A. Paul, "A mystery of 'sluggish diffusion' in high-entropy alloys: the truth or a myth?", arXiv:1804.03465, Table 4.
