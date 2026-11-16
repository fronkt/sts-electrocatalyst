# ISEF round-2 melt plan, 2026-11-16

**Deadline it is built around.** NEIRSEF 2027 is **Saturday, February 6, 2027**; teacher and student
registration (Senior Division: research plan, abstract, ISEF forms) and the fee are due **January 22,
2027** (https://www.pfw.edu/etcs/science-fair/schedules, checked 2026-11-16). Round-2 testing therefore
fits in January, so the disks should reach the bench by about December 18.

**Set: three melts, R1, R2, R3** (200 g rods as in round 1), plus free commercial rod stock. Frank
(2026-11-16): narrow the round to three alloys. Earlier versions: six melts
(`isef-round2-melt-plan-archive-2026-11-16-six-melts.md`) and R0/R1/R3
(`isef-round2-melt-plan-archive-2026-11-16-r0-r1-r3.md`). Status: it becomes the request when Frank
sends it to FWM. Weigh targets: [isef-round2-weigh-sheet-2026-11-16.md](isef-round2-weigh-sheet-2026-11-16.md).

**No remelts of round-1 alloys.** Frank has leftover round-1 rod of every alloy (Frank, 2026-11-16).
- **Cu26 (ARC00150):** new disks from the leftover rod, replacing the disk that corroded. That is the
  same material as round 1, so it completes round 1 for Paper B without a remelt. Its as-made
  composition is already known: about 9 at.% Cu low, with Cu-rich pools to about 100 um.
- **Fe25 (ARC00151) and Ni34 (ARC00152):** the processing study (P1, P2 below).

**Why these three.**
- **R3** is the one alloy where the predictors disagree outright: the old screen ranked it last of 12,
  while the film rule puts it on top.
- **R1 and R2** leave the same film as Fe25 (Fe33 Co33 Ni33). With Fe25, they put 0, 14.3 and 25 at.%
  Cr on one Fe:Co:Ni backbone. That tests whether Cr does anything besides leaching out, and how C_dl
  scales with how much Cr leaves.
- All three are single FCC at 1,050 C in both open CALPHAD databases, so phase count is not a confound.

**Dropped 2026-11-16 (aims kept in `src/scripts/weigh_sheet_round2.py` for round 3):**
- R4 Ni86Cu14, Ni31's single-phase film twin. Gate 2 (iron-free KOH) may settle the Ni31 question first.
- R5 Mn31Ni31Co33Cu6, the mid-range anchor and the weakest case of the six.

What the cut costs: R3 is the only new film composition in round 2, so the trend test of the film rule
(and the film-DFT vs film-rule comparison) moves to round 3, with R5 and R4 as the first candidates.

**Not chosen earlier:** the 9-alloy Cr ladder (tasks/isef-2027-full-throughput-continuation-2026-11-10.md).
It was built to find a Cr percolation threshold that round-1 data don't support (Ni34, with no Cr or
Mn, activated as strongly as Fe25). R1 + R2 + Fe25 ask the Cr question with two melts.

## 1. What to melt (200 g per charge) and what comes from leftover rod

| Code | Alloy (at.% aim) | Why it is in the set | Film left after Cr/Mn leach | Film Ni+Fe | Phases at 1,050 C (open CALPHAD) |
|---|---|---|---|---|---|
| R1 | Fe33.3Co33.3Ni33.3 (FeCoNi) | Fe25 without Cr: same film, different bulk | Fe33 Co33 Ni33 | 0.67 | 1 FCC (both databases) |
| R2 | Co28.6Cr14.3Fe28.6Ni28.6 (CoCr0.5FeNi) | Cr midpoint between R1 (0) and Fe25 (25) | Fe33 Co33 Ni33 | 0.67 | 1 FCC (both) |
| R3 | Ni34Fe29Mn30Co7 | sharpest test: the old screen ranked it last of 12, the film rule puts it on top | Ni49 Fe41 Co10 | 0.90 | 1 FCC (both) |
| Cu26 | Cu25.8Ni9.4Cr31.5Co33.4 aim (leftover round-1 rod, ARC00150) | completes round 1 (Paper B); no remelt | Co49 Cu38 Ni14 (aim) | 0.14 | 3 (sigma + FCC + Cu-rich FCC), as measured in round 1 |
| P1 | Fe25Co25Ni25Cr25 (leftover round-1 rod, ARC00151) | processing study: as-cast vs homogenized vs cold-worked vs recrystallized | Fe33 Co33 Ni33 | 0.67 | 1 FCC (measured, round 1) |
| P2 | Ni33.9Fe6.0Cu29.4Co30.7 (leftover round-1 rod, ARC00152) | processing-study partner with no Cr or Mn: separates "work speeds Cr leaching" from "work changes film growth" | same as bulk | 0.40 | 1 FCC (measured, round 1) |

**Free FWM rod stock (no melting):** Ni 200 and 316L first (the regional-fair benchmark: nickel is what
alkaline anodes are made of), then 304, Alloy 600, Alloy 690 if offcuts exist. Rod at least 5.5 mm across,
about 3 cm of each.

P1 and P2 come from the same round-1 ingots as the disks Josh already measured, so the processing
study's homogenized state (H) links directly to the round-1 data and the December repeats, and the
composition is already checked (SEM-EDS; both single FCC). Only the as-cast (AC) state needs material
that was never annealed. If either alloy's leftover rod is too short (section 2, "Material needed"),
melt a 200 g charge of that alloy only, at the round-1 aim.

## 2. Route (same as round 1 unless marked)

1. **Melt.** Argon arc melt, flip and remelt at least 3 times, cast to rod as in round 1 (about 8-11 mm
   across, 20-25 cm long).
   - **Mn (R3): charge +25% Mn** (round 1 charged +4% and lost roughly 13-25% of the charged Mn,
     from SEM-EDS spot estimates on Cu8 and Cu22). With +25%, any loss between 13% and 27% lands within
     +/-2 at.% of the aim (table in the weigh sheet). Bury the Mn under the other pieces and keep arc
     time after the first melt short. Changing the melting practice changes the loss, so tell us if it
     differs from round 1.
   - **No hot working (new).** Round-1 Cu8 split when hot rolled at 850 C.
2. **As-cast pieces.** Before homogenizing, cut about 2 cm off every rod as the as-cast reference.
   For P1 and P2, the AC state (3 disks + a metallography slice, about 4 cm) comes from leftover
   round-1 rod that was never annealed.
3. **Homogenize** (Frank): 1,050 C / 24 h in Ar, water quench; all charges except the AC pieces.
   Cu26: the leftover ARC00150 rod is half homogenized, half as-cast (Frank, 2026-11-16). The 4 disks
   come from the homogenized half, so they match the round-1 disk. The as-cast half stays uncut in
   reserve (Stage 2 option: a Cu26 AC-vs-H pair, or a metallography slice showing whether homogenizing
   shrank the Cu-rich pools).
4. **Cold work, P1 and P2 only (new).** Cold swage or draw part of each homogenized rod to about 6 mm
   (about 64% area reduction from 10 mm), no anneal = state CW. Rolling is acceptable if swaging is not
   available; round rod is preferred because its slices fit the RDE holder directly.
5. **Recrystallize, P1 and P2 only (Frank).** Hardness series on small CW coupons at 700 / 800 / 900 /
   1,000 C for 1 h, water quench; the lowest temperature that fully softens sets the RX anneal for the
   disk stock.
6. **Machine.** 5.00 mm diameter x 4.00 mm disks by wire EDM, as in round 1. Remove at least 0.1 mm from
   each working face, then grind and polish.
   - R1, R2, R3: 4 disks each.
   - Cu26 (homogenized half of the leftover ARC00150 rod): 4 disks.
   - P1, P2: 3 disks per state (AC, H, CW, RX) plus a hardness/metallography slice per state.
   - Benchmarks: 2-3 disks each.
7. **As-made check before testing.** SEM-EDS area analyses (at least 3 fields at 250x or lower), checking for Zn from the brass EDM wire. Chip ICP-OES from top and bottom if FWM can run it. XRD.
   Acceptance: every element within +/-2 at.% of the aim; Mn (R3) is the likely miss.

**Material needed for P1 and P2.** The AC piece (about 4 cm), the H stock (about 3 cm), the CW stock
(about 6 cm of 10 mm rod, which swages to about 16 cm of 6 mm rod for the CW disks, the RX disks and the
four hardness coupons), plus trim. That is about 15 cm of sound rod per alloy from the leftovers
(about 4 cm of it never annealed). Fallback if the homogenized rod is too short to swage: cold roll it
flat to about 4 mm thick (about 60%) and wire-EDM the disks straight out of the plate (working face =
rolling plane). Skull pieces and already-cut disks are not usable as CW stock. Cu26 needs about 2.5 cm
of the homogenized half for 4 disks.

## 3. Schedule to February 6

| When | What |
|---|---|
| by Nov 24 | Request to FWM: three melts (R1, R2, R3), Cu26 disks from leftover rod, cold work of the leftover Fe25 / Ni34 rod, rod stock |
| early Dec | Melts; Frank homogenizes (24 h) |
| by ~Dec 18 | R1, R2, R3, Cu26 and benchmark disks to Josh. P1/P2 cold work and RX later in December |
| Jan 4-29 | Round-2 bench, 2 disks each, in the order below |
| Jan 22 | NEIRSEF registration: research plan, abstract, ISEF forms, fee |
| Jan 30 | Data freeze for the regional poster |
| Feb 6 | NEIRSEF |
| after Feb 6 | Third disks, full processing study (both alloys, 4 states), holds + ICP, XPS / Raman / FIB, round 3 (R5, R4 first) |

## 4. January bench order (2 disks each, Protocol v2: activation 1.00-1.65 V only)

Ordered by poster value per bench hour, so whatever is done by January 30 is the strongest set.

| Order | Disks | Hours (4.7 h/disk) | Why |
|---|---|---|---|
| 1. R3 | 2 | 9.4 | the blind test with the clearest prediction |
| 2. R1 | 2 | 9.4 | same film as Fe25, no Cr |
| 3. Ni 200 + 316L | 4 | 18.8 | the benchmark judges understand |
| 4. R2 | 2 | 9.4 | completes the 3-point Cr ladder |
| 5. P1 H vs CW | 4 | 18.8 | first look at Frank's processing hypothesis; needs the CW rod back by early January |
| 6. Cu26 (leftover rod) | 2 | 9.4 | completes round 1 (Paper B); could move into December if the disks are ready |
| **Total** | **16** | **~75** | |

If time is left before January 30: a third disk each of R3 and R1 (~9 h).

December, on existing disks, before any of this: Gates 1 + 2, repeats, the Cu8 sweep to 10 mA/cm2
(about 85-100 h; master plan sections 1 and 7).

## 5. Predictions to register before the first round-2 disk is measured

- **Film Ni+Fe rule** (tasks/isef-2027-round2-plan.md, P2 table): R3 in the top group with Fe25/Ni31;
  R1 and R2 equal to Fe25 per ECSA (within 2x pooled disk SD), with C_dl rising with Cr
  (R1 < R2 < Fe25); Cu26 at or below the Ni34/Cu22 pair.
- **Film-model DFT,** only if the pilot passes its V1 gate (docs/research/film-dft-pilot-2026-11-14.md):
  a ranking of the round-2 films (R3's, and the Fe33 Co33 Ni33 film that R1, R2 and Fe25 share),
  registered separately before the January bench.
- **Processing (P1, P2):** H1-H3 of master plan section 3.5.

## 6. Questions for FWM

1. Melter and hearth (water-cooled Cu arc?), number of remelts, and Mn practice in round 1.
2. 200 g per charge, as in round 1.
3. Cold swaging or drawing of the leftover round-1 Fe25 (ARC00151) and Ni34 (ARC00152) rod to about 6 mm (or cold rolling), and the reduction FWM can reach without an intermediate anneal.
4. Ni 200, 316L, 304, Alloy 600, Alloy 690 rod offcuts at least 5.5 mm across.
5. SEM-EDS area mode, chip ICP-OES and XRD access for the as-made check.
6. Can the melts happen by early December?
