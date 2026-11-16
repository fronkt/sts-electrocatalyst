> Archived 2026-11-16: master plan before the round-2 set was narrowed from six melts to three (R0, R1, R3). Current file: `isef-2027-master-plan-2026-11-14.md`.

# ISEF 2027 + paper: master continuation plan (2026-11-14)

Consolidates three earlier files, which stay as they are:
- `isef-2027-round2-plan.md` (11-10): film hypothesis, 6-melt round-2 set, bench budget
- `isef-2027-full-throughput-continuation-2026-11-10.md` (11-10 night): 9-alloy Cr ladder, gates, characterization stack
- `isef-2027-continuation-audit-2026-11-10.md` (11-10 night): critique of the two above

Adds: Frank's 11-14 processing study (as-cast vs worked), the Thermo-Calc route through a Pitt
computational materials scientist, and a merged alloy set.

Status labels: **DECIDED** = Frank said so; **PROPOSED** = in a plan, not yet picked; **NEW** = 11-14.

**Update 2026-11-16.** NEIRSEF 2027 is **Saturday, February 6, 2027**; registration (Senior Division:
research plan, abstract, ISEF forms) and the fee are due **January 22, 2027**
(https://www.pfw.edu/etcs/science-fair/schedules). Frank (11-16): not everything (all new melts plus
processed vs not) will be finished by February 6; the project keeps improving after the regional fair,
up to ISEF. Sections 7, 8 and 10 now split the work into Stage 1 (by Feb 6) and Stage 2 (Feb 6 to
ISEF). Round-2 melt request: `docs/research/isef-round2-melt-plan-2026-11-16.md` + weigh sheet. The
melt pick does not wait on the film-DFT pilot (section 5). Version before this update:
`isef-2027-master-plan-archive-2026-11-16-pre-feb6.md`.

---

## 0. Where round 1 stands

- Six alloys melted and cast at FWM, homogenized 1,050 C / 24 h + water quench, machined to 5.00 mm
  (0.196 cm2) RDE disks. Five measured by Josh, one disk each, Oct 24 - Nov 3.
- eta10 (first sweep, 90% iR): Fe25 0.313, Ni31 0.316, Cu22 0.365, Ni34 0.369, Cu8 > 0.393 V (bound).
  Cu26 not measured (corroded, flaky faces, connection error).
- Two pre-registered screen rankings: the 12-site best-site ranking held at the top; the 120-site
  p10 ranking's leader (Cu8) came last.
- Main mechanistic finding: every alloy that was cycled grew an oxyhydroxide film (Fe25 current at
  1.624 V rose 4.8x over 39 CVs; Ni31 redox wave 2.9 -> 9.5 mC/cm2). The electrode is the film, not
  the alloy surface the DFT modeled.
- Four of six alloys are multiphase (Cu8, Cu26, Cu22, Ni31); Fe25 and Ni34 single FCC.

## 1. Bench work on existing disks (Josh / Tackett group) - no new melts

| Item | Why | Status |
|---|---|---|
| 1-2 repeat disks each: Fe25, Ni31, Cu22, Ni34, Cu8 | error bars; Fe25 vs Ni31 (3 mV) is a tie at n = 1 | DECIDED (paper needs it) |
| Cu8 swept to 10 mA/cm2 | eta10 is a bound now | PROPOSED |
| C_dl on every disk, each in its own non-faradaic window (Josh's method) | ECSA-normalized activity beside geometric | PROPOSED |
| Steady-state Tafel ladder (CP 1, 2.5, 5, 10, 25, 50 mA/cm2, 90 s/step) | LSV Tafel overlaps the redox wave; EIS-implied slopes are 1.3-1.6x the LSV values already sent to Josh | PROPOSED |
| **Gate 1**: 1.35 V hold vs shallow CV (1.00-1.65 V) vs deep CV (-0.38-1.65 V), on Fe25 and Ni34 | Does Cr leaching build the film, or does deep HER-OER cycling grow it on any alloy? Ni34 (no Cr/Mn) grew Q_redox 4.3x under deep cycling. Go/no-go for the Cr-ladder idea | PROPOSED, top priority |
| **Gate 2**: iron-free KOH (PTFE cell, ICP-MS-certified KOH, separated counter), Fe25 vs Ni31, then 10 uM Fe3+ spike | Ni31's film has no Fe yet ties Fe25; R_ct x I dropped only on Ni31, the signature of electrolyte Fe uptake | PROPOSED, top priority |
| Stability hold (10 mA/cm2, hours) + electrolyte ICP | Is leaching self-limiting? Needed for any Energy claim | PROPOSED |
| Protocol v2: activation 1.00-1.65 V only, daily RHE calibration | removes the deep-cycling confound for all round-2 disks | PROPOSED |
| Ask Josh: can Frank run disks under supervision; can repeats use a shorter protocol? | bench hours are the bottleneck (section 7) | OPEN |

## 2. New alloys from FWM

### 2.1 Two competing designs on file
- **Film-hypothesis set (11-10 afternoon, 6 melts):** Cu26 remelt, FeCoNi, CoCr0.5FeNi, Ni86Cu14,
  Ni34Fe29Mn30Co7, Mn31Ni31Co33Cu6.
- **Cr-ladder set (11-10 night, 9 melts):** Ni75Fe25, Ni67.5Fe22.5Cr10, Ni63Fe21Cr16, Ni60Fe20Cr20
  (quenched + aged SRO pair), Ni57Fe19Cr24, Ni52.5Fe17.5Cr30, Ni70Cr30, Ni52.5Fe17.5Mn30, FeCoNi.
  Built to measure a Cr "percolation threshold"; the 11-11 review found round-1 data don't support
  that threshold, and Frank thought the Materials Science framing behind it was a bad move.

### 2.2 Merged recommendation (6 melts + free stock) - RECOMMENDED; melt request written 11-16 (`docs/research/isef-round2-melt-plan-2026-11-16.md`), becomes the pick when Frank sends it to FWM

| # | Alloy (at.%) | Role |
|---|---|---|
| R0 | Cu26Ni9Cr31Co33 (remelt) | **DECIDED**: completes round 1; old button was ~9 at.% Cu low with Cu pools to ~100 um |
| R1 | FeCoNi | Fe25 with Cr removed; in both designs |
| R2 | CoCr0.5FeNi (Cr 14.3) | with R1 (Cr 0) and Fe25 (Cr 25), a 3-point Cr ladder on a fixed Fe:Co:Ni backbone - the ladder question at 2 melts instead of 6 |
| R3 | Ni34Fe29Mn30Co7 | in both designs; old screen ranked it last of 12, film hypothesis puts it on top - sharpest test; also the Mn comparator |
| R4 | Ni86Cu14 | Ni31's film twin, single phase; drop if Gate 2 settles the Ni31 question first |
| R5 | Mn31Ni31Co33Cu6 | mid-range anchor |
| free | FWM rod/offcuts >= 5 mm: Ni 200, 316L, 304, Alloy 600, Alloy 690 | commercial benchmarks under the same protocol (the Energy-category comparison); Ni 200 = what alkaline anodes are made of |

All six melts are single FCC at 1,050 C in the open CALPHAD databases (MatCalc mc_fe; LibreCalphad
where it covers them). Same route as round 1 (3x argon melt, 1,050 C / 24 h, WQ), 4 disks each.

### 2.3 Melt-side items
- Weigh Mn high: round-1 Mn melts lost ~22% of their Mn (Cu8 35 -> 29.5 at.%); ~36 at.% weighed lands near 30.
  11-16 weigh sheet: +25% Mn mass (R3 charged at 34.9 at.%), which lands within +/-2 at.% of the aim
  for any loss of 13-27% of the charged Mn (`docs/research/isef-round2-weigh-sheet-2026-11-16.md`).
- Chip ICP-OES (top and bottom of each ingot) for bulk composition; SEM-EDS **area** analyses + XRD
  for the as-made check.
- Register predictions (film-hypothesis table, Fe-free KOH, ICP) before any round-2 disk is measured.
- Scholar / Web of Science novelty check on R3, R5 and the round-1 compositions (promised to Josh).

## 3. NEW: processing study - as-cast vs worked, same composition

### 3.1 Question
Does the processing state of the bulk alloy change OER activity or activation at fixed composition?
Frank's hypothesis: mechanical work stored in the metal (dislocations, twins) gives better OER.
Practical angle: real alkaline electrodes (Ni mesh, sheet, foam) are wrought, not cast, so the
worked state is the one an electrolyzer would use.

### 3.2 Design (one ingot per alloy, split, so composition is identical across states)

| State | Route | What changes |
|---|---|---|
| AC | as-cast, no homogenization | dendritic segregation, casting porosity |
| H | 1,050 C / 24 h + WQ (= current disks) | baseline; coarse grains, low dislocation density |
| CW | H, then cold rolled or swaged/drawn (~60-70% reduction), disks cut, no anneal | high dislocation density (roughly 1e15 m^-2 vs <1e12 annealed), deformation twins, texture |
| RX | CW + short recrystallization anneal (temperature set by a hardness-vs-T check; ~800-900 C, 1 h for CoCrFeNi) + WQ | fine grains + annealing twins, low dislocation density |

Comparisons: CW vs RX = stored work (dislocations) at similar grain size; RX vs H = grain size;
AC vs H = segregation.

Alloys: **Fe25** (CoCrFeNi: best round-1 performer, single FCC, very ductile, round-1 baseline exists)
and **Ni34** (single FCC, no Cr or Mn). The pair is a 2x2: if work helps only Fe25, it acts by
speeding Cr leaching (dislocations as fast dissolution paths); if it helps both, it acts on film
growth itself. Multiphase alloys are out: FWM's alloy 149 (= Cu8) split when hot rolled at 850 C.

### 3.3 Confounds and how each is handled
1. **The polishing layer.** Mechanical grinding/polishing cold-works the top few um of every disk,
   including the current "as-cast" ones. Finish all states with a long vibratory colloidal-silica
   polish (EBSD-grade), verify with EBSD pattern quality, and keep one standard-polish set as an
   extra condition. **Cheap pilot on existing material:** re-polish a tested Fe25 disk, then compare
   standard polish vs EBSD-grade polish. If surface deformation matters, it shows here first.
2. **The film may erase the bulk.** Every alloy grew a thick oxyhydroxide film. Bulk defects may
   change how fast the film forms more than how good it ends up. Report first-sweep eta10, cycles
   to a <2% plateau, Q_redox growth, and post-activation eta10 separately.
3. **Texture.** Rolling/drawing textures the disk face, and OER on CoCrFeNi depends on facet
   (advs.202404095 used a {100} crystal). Measure texture (XRD intensity ratios or EBSD) per state.
4. **Roughness / ECSA.** Normalize by C_dl; report geometric and ECSA-normalized activity.
5. **Hydrogen.** Worked metal traps more H; deep cycling into HER would load it. Use Protocol v2
   (1.00-1.65 V) only.
6. **Cutting damage / EDM recast + brass Zn.** Removed by the final polish; check EDS for Zn.
7. **Radial gradient in drawn rod.** Disk face spans it; map hardness across the radius.

### 3.4 Quantify the processing state (each disk or a sister piece)
- Vickers microhardness (cheap dislocation proxy; also sets the RX temperature)
- XRD peak broadening (Williamson-Hall: microstrain, crystallite size), using the existing MAUD workflow
- EBSD: grain size, twin fraction, KAM/GND density, texture
- Optional: DSC stored-energy release on heating a CW chip

### 3.5 Predictions to register before measuring
- H1 (Frank): CW more active than RX and H (eta10 lower by more than 2x pooled disk SD) and activates faster.
- H2 (grain boundaries): RX ~ CW, both more active than H.
- H3 (film erases bulk): differences only in first sweep / activation rate; post-activation,
  ECSA-normalized activity within 2x SD.
- Mechanism: CW - RX difference larger in Fe25 than in Ni34 if work acts through Cr leaching.

### 3.6 Bench cost
Full: 2 alloys x 4 states x 2 disks = 16 disks (~75 h at 4.7 h/disk). Minimum: Fe25 x {H, CW, RX}
x 2 = 6 disks (~28 h) + the polish pilot (2 disks, ~10 h).

### 3.7 To do
- [ ] Literature + novelty check (cold work / SPD / dislocation density vs OER in bulk alloys and HEAs), refute-passed
- [ ] FWM: one extra ingot each of Fe25 and Ni34 large enough to split 4 ways; which working route (rolling vs swaging/drawing), reduction %
- [ ] Polish pilot on a re-polished tested Fe25 disk
- [ ] Optional thermal sibling: Ni60Fe20Cr20 quenched vs 575 C / 72 h aged (SRO) from the Cr-ladder design

## 4. Characterization

| Item | Why | Priority |
|---|---|---|
| DSC 700-1,150 C on as-cast Cu22 / Cu8 chips | mc_fe predicts 18.4% liquid in Cu22 at 1,050 C: incipient melting vs Cu immiscibility | 2 |
| Raw EDS re-quantification + Zn (1.01 / 8.63 keV) check | Ni-in-Cu artifact; brass-wire recast | 1 (zero cost) |
| Post-OER SEM-EDS, same-kV tested vs virgin sister disk (5/7/10/15 kV) | film composition, Cr/Mn depletion | 2 |
| Angle-resolved XPS, unsputtered (Purdue) | oxidation states in the film | 2 |
| Electrolyte ICP-MS (15-20 mL PTFE cell) | which elements leach, how much | 1 (with Gates) |
| In-situ Raman (<= 0.5 mW, under potential) | NiOOH vs Cr2O3 bands | 3 |
| FIB-STEM film-thickness pair | bounds the film depth | 3 |
| Synchrotron XRD (+ XAS if beamtime) | phase fractions; Cu22's unmatched FCC (a = 3.600 A); film chemistry | 3, Frank's plan |
| Thermal-oxide control (4 states on one alloy) | 11-11 review: shrink or drop | 3 |

## 5. Compute (supporting role)

- **Thermo-Calc TCHEA** via a Pitt computational materials scientist;
  Purdue's license is MSE-held (PIER, app@ecn.purdue.edu), so a seat would have to be bought.
  Ask: equilibrium phases at 1,050 C for the 6 round-1 alloys (designed + measured compositions) and
  the round-2 picks; phase fraction vs T (500-1,400 C); solidus + Scheil for Cu22 / Cu8 / Cu26;
  raw tables + TC/database versions. Fallback: open databases (5 of 6 phase counts right).
  For the processing study: recrystallization is not a CALPHAD output, but phase stability at the
  RX anneal temperature is.
- Pourbaix rerun with experimental Ni(OH)2 / NiOOH data (MP's Ni entry contradicts our data).
- Zero-cost reanalysis: EIS transmission-line refit (Ni31 n = 0.716); R_ct x I tracker on all EIS.
- Lattice dealloying model (percolation + SRO + passivation) only if Gate 1 supports Cr leaching.
- **Oxide DFT ranking - OPEN (Frank 11-14 wants it kept for choosing melts).** The STS version
  (bulk-composition rutile MO2(110) sites) is not reused as a selector:
  - It modeled a surface that does not survive: its predicted winners were Cr oxo sites, and Cr
    leaches as chromate at OER potentials while an oxyhydroxide film grows.
  - Where it finished, the order was wrong: best-site DFT put Cu8 (0.621 V) ahead of Ni31 (0.768 V);
    measured, Ni31 was best and Cu8 last. The 120-site p10 leader (Cu8) came last; the 12-site
    ranking got the top two right.
  - Uncertainty exceeds the signal: Cr's eta moves 1.12 V across Hubbard-U choices (Ru 0.50, Ti 0.25,
    Ir 0.03 V); swapping the ML potential moved compositions 0.01-0.28 V and reordered them
    (Kendall tau 0.2). Measured eta10 spread across five alloys is at least 0.08 V (Cu8 is a bound); Fe25 vs Ni31 is 3 mV.
  - Proposed role instead: **film-model DFT** on (Ni,Fe,Co,Cu)OOH at the composition left after Cr/Mn
    leach (round-2 plan item C3), run as a third registered predictor beside CALPHAD (phase gate) and
    the film Ni+Fe rule, with the U band reported. Prefer melts where the predictors disagree (R3).
    If it beats the film rule on round 2, it earns the selector role for round 3.
  - Limits: cannot see electrolyte Fe uptake, film thickness/porosity, activation rate, or
    dislocations (processing study is experiment-only); NiFe(Co)OOH trends are already in the literature.
  - Timing: a film pilot (Ni(Cu)OOH for Ni31 / R4) to size the Anvil SU cost; it will not finish
    before the ~Nov 24 melt pick, so it registers predictions before the January bench instead.
  - 11-16: the pilot running on AWS (NiOOH / Ni(Fe)OOH / CoOOH, `docs/research/film-dft-pilot-2026-11-14.md`)
    only tests the model (V1 gate); it computes no candidate alloy, so the round-2 melts do not depend
    on it. If V1 passes, production runs need the melt list (the round-2 film compositions) and
    register a ranking before the January bench; if that ranking beats the film Ni+Fe rule, it picks
    round 3 (Stage 2).

## 6. Papers and ISEF

- **Paper B (experimental), with Josh + Dr. Tackett** - DECIDED (Josh agreed 11-10). Josh wants a
  virtual meeting the week of 11-16 or 11-23, eta10 / Tafel / activity order vs DFT, and a novelty
  check. Possible co-authors still to settle: Xiaoming Wang, the Pitt contact if TCHEA results go in.
  Suggestion: keep round 1 completed (six alloys, repeats, Cu26, C_dl, Fe-free KOH) as this paper so
  it doesn't wait on round 2; round 2 + processing feed ISEF and a follow-up.
- **Paper A (computational: silentgate + rutile/MLIP audit)** - PROPOSED: submit Dec-Jan so ISEF can
  cite it as under review. 11-16 suggestion: move it to February-March, after NEIRSEF. It is still
  under review by ISEF in May, and December-January belong to the bench and the regional poster.
- **ISEF category** - OPEN: Frank leaning Energy (11-11), not Materials Science. For Energy: Ni 200 /
  316L benchmark under the same protocol, long hold + ICP, Co-free argument. The processing study
  fits either category.
- **Framing**: drop "beats IrO2" as a headline (drop-cast ink vs bulk alloy is not equal-area);
  drop the HER numbers (first ~2 s of a sweep), "RF_eff / 89x dielectric jump", and the hot 6 M KOH
  electrolyzer. A 1 M KOH room-temperature two-electrode cell can stay as a display.

## 7. Bench budget (one rotator, ~4.7 h/disk)

| Block | Disks | Hours |
|---|---|---|
| Repeats, 5 alloys x 2 | 10 | 47 |
| Cu26 x 3 | 3 | 14 |
| Gates 1 + 2 | ~8 | ~38 |
| Round 2, 5 new x 2-3 | 10-15 | 47-71 |
| Commercial benchmarks (Ni 200, 316L) x 2 | 4 | 19 |
| Processing study (min / full) | 8 / 18 | 38 / 85 |
| Stability holds | - | 20-36 |
| **Total** | **~43-58** | **~220-310** |

This is more than one person's bench time before NEIRSEF (Feb 6), so the work runs in two stages
(11-16, Frank: keep improving after the regional fair, up to ISEF).

**Stage 1: by February 6 (~165 h core + ~19 h stretch)**

| Block | When | Disks | Hours |
|---|---|---|---|
| Gates 1 + 2 on existing disks | Dec | ~8 | ~38 |
| Repeats, 5 alloys x 2 (+ Cu8 sweep to 10 mA/cm2) | Dec | 10 | 47 |
| Round 2: R0-R5 x 2 | Jan | 12 | 56 |
| Ni 200 + 316L x 2 | Jan | 4 | 19 |
| Stretch: Fe25 (P1) H vs CW x 2 | Jan | 4 | 19 |

January order: R3, R1, Ni 200 + 316L, R2, R0, R5, R4, then P1 H vs CW (melt plan section 4).
Whether Stage 1 fits depends on rotator time: Josh's hours, and whether Frank can run disks
under his supervision (section 9, item 5). That is the biggest lever.

**Stage 2: February 6 to ISEF (May)**
- Full processing study (P1 + P2, 4 states x 2-3 disks) and the polish-layer control
- Third disks on round 2; stability + ICP holds (is leaching self-limiting?)
- XPS / Raman / FIB, synchrotron if beamtime; SRO pair and thermal-oxide control only if they still answer a question
- Round 3 melts, chosen by whichever predictor won round 2 (film rule or film DFT)
- Paper B; Paper A submission

## 8. Timeline (NEIRSEF = Sat Feb 6, 2027; updated 11-16)

| When | What |
|---|---|
| Nov 16-24 | Send the melt request to FWM (6 melts at 200 g, cold work of leftover round-1 Fe25 / Ni34 rod, Ni 200 / 316L stock); Tackett/Josh call (December bench, Frank on the rotator, iron-free KOH supplies); film-pilot V1 readout, then terminate the AWS box; novelty check on R3 / R5; register round-2 predictions; ask the Pitt contact |
| Nov 25 - Dec 23 | Josh (+ Frank?): Gates 1 + 2, repeats, Cu8 sweep, C_dl, polish pilot. FWM: melts, then Frank homogenizes; machining; P1/P2 cold work + RX hardness series. Film-DFT production on the round-2 films if V1 passes and compute is approved |
| by ~Dec 18 | R0-R5 + benchmark disks to Josh |
| Jan 4-29 | Round-2 bench (2 disks each, Stage 1 order); as-made SEM-EDS / XRD |
| Jan 22 | NEIRSEF registration: research plan, abstract, ISEF forms, fee (through the teacher) |
| Jan 30 | Data freeze for the regional poster |
| Feb 1-5 | Poster, print, speaker notes |
| **Feb 6** | **NEIRSEF** |
| Feb - May | Stage 2 (section 7); HSEF (~Apr 3, unverified); ISEF (May) |

## 9. Open decisions (Frank)
1. Alloy set: merged 6 (section 2.2) or the Cr ladder. 11-16: melt request written for the merged 6
2. Processing study: alloys (Fe25 + Ni34 suggested), working route, reduction %. 11-16: in the melt
   request as P1 + P2, cold swage/draw to ~6 mm (~64%), FWM to confirm route. 11-16 later: P1 + P2 =
   Frank's leftover round-1 Fe25 / Ni34 rod (no new melt); same ingots as the round-1 disks
3. ISEF category: Energy vs Materials Science
4. Paper split: round 1 now vs one paper after round 2
5. Can Frank run disks himself under Josh's supervision
6. Oxide DFT: film-model predictor (section 5) or not at all

## 10. Do broadly, filter for the poster (Frank 11-14)

Run the work broadly; decide at the January 30 data freeze what the regional (NEIRSEF, Feb 6) poster
shows, then rebuild the board for ISEF with the Stage 2 data. Last year's ISEF board went
deep into a computational pipeline and judges lost the thread. The Indiana STS poster
(experimental only, photo-led) took first place, which supports the same approach.

- **Filter rule (Feb):** a panel stays on the board only if it answers the one question and a
  non-specialist gets it in ~30 s. Everything else goes to the paper, the notebook, and Q&A backup.
- **The one question (draft):** these alloys rebuild themselves into a film in KOH; does predicting
  that film, and controlling it through processing, tell us which cheap alloys work?
- **Likely board:** how the alloys were made (photos) -> the surprise (film growth) -> the blind
  test on new alloys -> as-cast vs worked -> benchmark vs nickel / stainless / published IrOx.
  Compute = at most one panel, in plain words ("I predicted which alloys would work; here is how
  the prediction did").
- **Likely off the board (paper / Q&A only):** Hubbard-U sensitivity, symmetry-lock detector, EIS
  model fits, R_ct x I, percolation modeling.
- Run order follows poster value per bench hour, so whatever is finished by January 30 is the strongest part.
- If the processing study isn't ready by February 6, the regional board shows it as "in progress" at most;
  it becomes an ISEF panel after Stage 2.

### Processing study run order (section 3)
1. Now: polish pilot on a re-polished tested Fe25 disk (ask FWM's metallography lab whether a
   vibratory polisher or electropolishing is available).
2. With the round-2 melt request: one extra ingot each of Fe25 and Ni34, sized for 4 states x
   3 disks + metallography pieces; ask FWM rolling vs swaging/drawing to ~5 mm rod (rod slices fit
   the RDE insert directly). 11-16 melt request: P1 + P2 come from Frank's leftover round-1 Fe25 /
   Ni34 rod (no new melt; the H state then links to the round-1 disks and the December repeats);
   swage/draw to ~6 mm (~64%), then machine to 5.00 mm. Needs ~15 cm sound rod per alloy, ~4 cm of it
   never annealed (AC); a 200 g melt of one alloy only if its leftovers fall short.
3. Split each ingot: AC piece cut before homogenizing; Frank homogenizes the rest; FWM cold works
   part (~60-70%); Frank anneals part of that (RX temperature from a hardness series on small
   coupons, e.g. 700 / 800 / 900 / 1,000 C for 1 h).
4. Per state: hardness, optical/EBSD grains, XRD peak width. Register predictions.
5. January bench: 2 disks per state, Protocol v2. 11-16: by Feb 6 only P1 H vs CW (stretch); the
   full 2 alloys x 4 states runs in Stage 2.
