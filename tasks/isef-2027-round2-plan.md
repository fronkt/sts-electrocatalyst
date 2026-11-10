# ISEF 2027: round 2 plan (2026-11-10)

## The story this round adds

Round 1 tested two screen rankings on five alloys: the 12-site ranking held at the top, the
120-site ranking's leader (Cu8) came last. Round 2 closes the loop:

1. **Diagnose.** In 1 M KOH the electrode is a film grown from the alloy, not the modeled
   surface. Thermodynamics says Cr and Mn dissolve out of it; Ni, Fe, Co and Cu stay.
2. **New hypothesis.** Activity follows the Ni + Fe content of that leached film.
3. **Predict blind, then test.** Register the predictions for Cu26 (remelt), five new alloys
   and an iron-free KOH control before any of them are measured.
4. **Corrected compute.** Descriptors on film (oxyhydroxide) models, audited with silentgate,
   registered with the same deadline.

## What the 2026-11-10 analysis found

### P1 Pourbaix solubility (done)
`src/scripts/isef_pourbaix_solubility.py` -> `results/isef_round2_2026-11-10/pourbaix_solubility.json`.
Cached MP entries, pH 14. For each metal, c* = the lowest dissolved-ion concentration at which
a solid is stable. One disk's film dissolved into ~100 mL is ~2e-7 M, so c* above ~1e-6 M
means the metal leaches.

| Metal | 1.23 V | 1.53 V | 1.63 V | Reading |
|---|---|---|---|---|
| Cr | ion at 1 M | ion at 1 M | ion at 1 M | leaches as CrO4^2- (robust) |
| Mn | 10^-7.5 (MnO2) | ion at 1 M | ion at 1 M | leaches as MnO4^- at OER potentials (robust) |
| Fe | 10^-7.0 | 10^-6.75 | 10^-1.75 | retained at eta 0.30 V, marginal; ferrate by 0.40 V |
| Co | 10^-4.5 | 10^-9.5 | 10^-11.25 | retained (CoOOH) |
| Cu | 10^-5.5 | 10^-10.5 | <= 10^-12 | retained (MP's solid is "Cu2O3", a DFT phase; treat only as "a Cu oxide") |
| Ni | 10^-3.25 | 10^-3.25 | 10^-3.75 | MP says leaches; **contradicted by our data** (Ni31's Ni redox wave grew over 25 cycles) -> treated as retained |

Consequence: the September gate (`src/dft/pourbaix_multi.py`, 1e-6 M yes/no) scored Fe25 as 75%
soluble only because of the Ni entry. Its Cr and Mn calls stand.

### P2 Leached-film hypothesis (POST HOC on five alloys)
`src/scripts/isef_film_hypothesis.py` -> `results/isef_round2_2026-11-10/film_hypothesis.json`.

| Alloy | Film after Cr/Mn leave | Film Ni+Fe | eta10 (V) |
|---|---|---|---|
| Ni31 | Ni86 Cu14 | 0.86 | 0.316 |
| Fe25 | Fe33 Co33 Ni33 | 0.67 | 0.313 |
| Ni34 | Ni34 Co31 Cu29 Fe6 | 0.40 | 0.369 |
| Cu22 | Co38 Fe36 Cu26 | 0.35 | 0.365 |
| Cu8 | Co81 Cu19 | 0.00 | > 0.393 |

The film Ni+Fe ranking reproduces the measured groups ({Ni31, Fe25} > {Ni34, Cu22} > Cu8).
Spearman rho = 0.80 if the two within-tie orders are counted (p = 0.10, n = 5). It was built
after seeing the data, so it counts for nothing until round 2 tests it.

A second reading falls out: Ni31's film holds no Fe, yet it ties the best alloy. Pure Ni
oxyhydroxide is a poor OER catalyst unless it picks up Fe from unpurified KOH (Trotochaud et al.,
JACS 2014). So Ni31's activity may come partly from electrolyte Fe. The iron-free KOH run decides.

### P3 Phase filter (empirical part done; CALPHAD pending)
The screen's solid-solution rule (Omega >= 1.1, delta <= 6.6%) passed all six alloys; four
separated. Checked against the six measured outcomes:
- **VEC >= 8.0 (Guo 2011, FCC only)** flags Ni31 (7.85) and Cu8 (7.78), both multiphase. Correct for 2 of 2.
- **Cu rejection.** Cu22 and Cu26 (VEC 8.8, 8.7) separated; Ni34 (Cu29!) did not. The Cu-to-matrix
  mixing enthalpy (Takeuchi-Inoue pairs, matrix-weighted) is 8.3, 8.3 and 5.6 kJ/mol. A cutoff
  between them fits, but it is fitted to these three, so it is a hypothesis, not a validated rule.
- CALPHAD check: see section "CALPHAD" below.

## Round-2 alloys (proposal; Frank picks)

All are FCC by VEC and use Cu only with a Ni-rich matrix (Cu-matrix enthalpy <= 4.7 kJ/mol,
below Ni34's 5.6). Predictions are from the film hypothesis; register them before measuring.

| # | Alloy (at.%) | Role | Film | Film Ni+Fe | Registered prediction |
|---|---|---|---|---|---|
| R0 | Cu26Ni9Cr31Co33 (remelt) | completes round 1 | Co49 Cu38 Ni14 | 0.14 | eta10 above the Ni34/Cu22 pair; at or below Cu8's |
| R1 | Fe33Co33Ni33 | film twin of Fe25; Cr = 0 | same as Fe25 | 0.67 | ECSA-normalized activity equals Fe25's (within 2x pooled disk SD) |
| R2 | Co28.6Cr14.3Fe28.6Ni28.6 (CoCr0.5FeNi) | Cr series midpoint | same as Fe25 | 0.67 | same as R1; Cdl rises with Cr (leaching roughens) |
| R3 | Ni86Cu14 | film twin of Ni31, single-phase bulk | same as Ni31 | 0.86 | ECSA-normalized activity equals Ni31's |
| R4 | Ni34Fe29Mn30Co7 | discriminator: the MACE screen ranked it last of 12 (0.872 V, dissociated *OOH) | Ni49 Fe41 Co10 | 0.90 | in the top group with Fe25/Ni31 |
| R5 | Mn31Ni31Co33Cu6 | mid-range anchor from the same screen | Co47 Ni44 Cu9 | 0.44 | groups with Ni34/Cu22 |

Iron-free KOH (purified per Trotochaud 2014) on Ni31, R3, Fe25, R1: **prediction** Ni31 and R3
lose more activity (larger eta10 increase) than Fe25 and R1. If Ni31 does not drop, its film is
active without electrolyte Fe and the hypothesis needs revising.

ICP of the electrolyte after a stability hold: **prediction** Cr and Mn appear in proportion to
bulk content; Ni, Co and Cu stay near the detection limit; Fe low at 1.53 V.

Why this set:
- n rises from 5 to 11 measured alloys. Spearman then needs rho of about 0.5-0.6 for p < 0.05,
  instead of a perfect 1.0 at n = 5.
- Two twin pairs (R1/Fe25, R3/Ni31) test the hypothesis directly: different bulk, same film.
  R3 also removes the bulk-phase confound (Ni31 is two-phase).
- R4 is where the old screen and the new hypothesis disagree most: that is the sharpest test.
- R1, R2 and R3 are well-known alloys (controls, not novelty claims). R4 and R5 still need a
  Scholar/Web of Science novelty check.
- Mn-bearing melts lost Mn at FWM (Cu8 came out 5.3-5.7 at.% low). The film prediction does not
  depend on Mn (it leaches), but ask FWM about Mn excess and measure the as-made composition.

## Work items

### A. Bench, existing disks (Josh / Tackett group, or Frank under supervision)
- [ ] Repeat disks: Fe25, Ni31, Cu22, Ni34, Cu8 (at least 1 more each; 2 more for error bars)
- [ ] Cu8: extend the sweep until 10 mA/cm2 so eta10 is a value, not a bound
- [ ] Cdl (ECSA) on every disk; report activity per ECSA beside per geometric area
- [ ] Iron-free KOH: Ni31, Fe25 (then R1, R3)
- [ ] Stability hold (e.g. 10 mA/cm2, several hours) + ICP-OES/MS of the electrolyte on Fe25, Ni31, Cu8
- [ ] Ask Josh: can Frank run disks himself under supervision? Can the 4.7 h/disk protocol be shortened for repeats?

### B. New alloys (FWM)
- [ ] Frank picks the round-2 set (table above or a change)
- [ ] Novelty check (Scholar / WoS) on the picks
- [ ] CALPHAD check on the picks (below)
- [ ] Register predictions (P2 table, iron-free KOH, ICP) before any round-2 disk is measured
- [ ] FWM: Cu26 remelt + 5 melts, same route (3x argon melt, 1,050 C 24 h, WQ), 4 disks each; ask about Mn excess
- [ ] As-made check: SEM-EDS area analyses (the +/-2 at.% test needs area, not spots), XRD

### C. Characterization
- [ ] Synchrotron XRD (Frank's plan): phase fractions by Rietveld; Cu22's unmatched FCC phase (a = 3.600 A)
- [ ] Post-OER surface: XPS (Cr, Mn depletion; Ni/Fe/Co states), SEM-EDS on tested disks
- [ ] If beamtime allows: XAS on post-OER disks (Ni/Co/Fe K edges; Cr(VI)); this is what tells the
      DFT which film to model
- [ ] Optional: Raman during OER (NiOOH bands)

### D. Compute
- [x] P1 Pourbaix solubility per metal
- [x] P2 film hypothesis (post hoc) + predictions for the round-2 set
- [x] P3a empirical phase rules vs the six outcomes
- [ ] P3b CALPHAD check (database search running)
- [ ] C3 film-model DFT: (Ni,Fe,Co,Cu)OOH slabs at each predicted film composition; OER descriptor;
      silentgate audit on every output; pilot one film (R3 / Ni31: Ni(Cu)OOH) to size the SU cost;
      register the ranking before round-2 data. Anvil CHE260157 (check `mybalance`)
- [ ] C4 replace MP's Ni aqueous/solid entries with experimental Ni(OH)2/NiOOH data and rerun P1

### E. Frank only
- [ ] Regional fair date (sets every deadline below)
- [ ] ISEF paperwork before new experiments (Form 1C for Purdue and FWM; Form 3 for KOH); ask the SRC
      how the June-November work counts
- [ ] Solo entry (STS rule 4.a bars presenting it as a team until 2027-06-01); decide the origami team project
- [ ] Synchrotron: which facility/beamline, and whether XAS on post-OER disks is possible

## Bench budget (one rotator, ~4.7 h per disk)

| Block | Disks | Hours |
|---|---|---|
| Repeats, 5 existing alloys x 2 | 10 | 47 |
| Cu26 x 3 | 3 | 14 |
| Round 2, 5 alloys x 3 | 15 | 71 |
| Iron-free KOH x 4 | 4 | 19 |
| Stability holds x 3 (extra) | - | ~20-36 |
| **Total** | **32** | **~170-190** |

Minimum for ISEF (if bench time is short): 1 repeat each (5), Cu26 x 2, round 2 x 2 (10),
iron-free KOH on Ni31 + Fe25 (2) = 19 disks, ~90 h.

## Timeline (work back from the regional fair date; dates below are targets)

| When | What |
|---|---|
| Nov 10-24 | Frank picks round 2; CALPHAD + novelty check; registration written; FWM melt slot requested; forms |
| Nov-Dec | Repeats and iron-free KOH on existing disks (Josh); C3 pilot on Anvil |
| Dec | FWM melts + homogenize + machine (round 1 took ~2-3 weeks) |
| Jan | Round-2 bench; C3 production; synchrotron XRD |
| Feb | Analysis, poster, regional fair |
| Mar-May | XAS / post-OER characterization if beamtime lands; ISEF May 2027 |

## CALPHAD

(pending: database search result)
