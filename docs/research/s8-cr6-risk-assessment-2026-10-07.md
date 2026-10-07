# S8 batch 1 — Cr(VI) and chemical-hazard risk assessment, 2026-10-07

Status: **draft for the supervisors' review and signature. Nothing is melted until it is signed and dated** (freeze proposal §7; docs/25 §5, which also expects the STS Rules Wizard's hazardous-activities paperwork; docs/37 §6).

Scope: the five batch-1 alloys of the [S8 melt plan](s8-melt-plan-2026-10-07.md), any re-melt, and an optional Ni34Fe6Cu29Co31 button, from weighing to waste. Exposure limits and waste codes below are the usual US references. Each site's Safety Data Sheets, chemical hygiene plan and EHS office have the final word.

## 1. Activities, sites and supervision

| Step | Site | Designated supervisor |
|---|---|---|
| Weigh pure-metal feedstock (Co, Cr, Cu, Fe, Mn, Ni; about 50 g in total) | Fort Wayne Metals (FWM) | TBD (FWM) |
| Arc-melt 10 g buttons under argon, flipped and remelted 4× | FWM | TBD (FWM) |
| Homogenization anneal under argon, then quench | FWM | TBD (FWM) |
| Wire-EDM cutting, grinding, polishing | FWM, or the electrochemistry lab | TBD |
| SEM-EDS and XRD | FWM or the electrochemistry lab | TBD |
| Electrode mounting, OER in 1 M KOH with an Hg/HgO reference, holds of up to 12 h | Purdue electrochemistry lab (pending confirmation) | TBD (Purdue) |
| Cr(VI) test of spent electrolyte (1,5-diphenylcarbazide) | Purdue electrochemistry lab | TBD (Purdue) |

The entrant works only under the designated supervisor's direct supervision. Equipment (arc melter, furnace, EDM, potentiostat) is run or supervised by the trained person at each site, following that site's training requirements.

## 2. Hazards

| Material or activity | Where | Hazard | Reference limit |
|---|---|---|---|
| **Chromium(VI) (chromate)** | Spent KOH electrolyte and rinse water from the four Cr-bearing alloys (22.6–31.5 at.% Cr; Cu22Fe30Co32Mn15 has none). At OER potentials in alkaline solution, Cr dissolves as chromate; the project's Pourbaix gate predicts chromate for every Cr-bearing candidate (docs/37) | Carcinogen (IARC Group 1), skin sensitizer, toxic | OSHA 29 CFR 1910.1026: PEL 5 µg/m³ (8 h TWA), action level 2.5 µg/m³ (airborne). In solution the exposure route is skin and eye contact, or aerosol |
| Manganese fume and condensate | Arc melting; Mn evaporates, which is why the charge carries extra Mn | Neurotoxic with chronic inhalation | OSHA PEL 5 mg/m³ ceiling; ACGIH TLV 0.02 mg/m³ respirable |
| Nickel and cobalt dust and fines | Feedstock handling, cutting, grinding, polishing; melter condensate | Skin and respiratory sensitizers; Ni compounds carcinogenic (IARC 1); Co metal probably carcinogenic (IARC 2A) | OSHA PEL: Ni 1 mg/m³; Co 0.1 mg/m³ |
| Copper fume | Arc melting | Metal fume fever | OSHA PEL 0.1 mg/m³ (fume) |
| Arc, heat and argon | Arc melter, furnace, quench | UV and arc flash; burns from ingots and the furnace; steam on quench; argon displaces oxygen in a confined space | — |
| Potassium hydroxide, 1 M | Electrolyte preparation and use | Corrosive; severe eye damage; dissolving solid KOH is exothermic | NIOSH REL 2 mg/m³ ceiling (aerosol) |
| Mercury | Hg/HgO reference electrode | Hg exposure only if the electrode breaks | OSHA 0.1 mg/m³ ceiling |
| Diphenylcarbazide test reagents | Cr(VI) test | Acetone (flammable); sulfuric acid (corrosive) | — |
| Epoxy and mounting resins | Electrode mounting | Skin sensitizers | — |
| EDM and polishing sludge | Cutting, polishing | Metal fines containing Cr, Ni, Co, Mn | — |

**Quantities are small.**
- Metal: about 50 g for batch 1.
- Electrolyte: one prepared batch of 1 M KOH, sized by the lab (expected ≤ 1 L).
- Chromate: microgram to milligram amounts per cell. As an order of magnitude, a 0.196 cm² face losing 1 µm of alloy releases about 0.05 mg of Cr.

The diphenylcarbazide test measures the actual amount.

## 3. Controls

**Melting and annealing (FWM):**
- Closed arc-melter chamber with argon purge and backfill.
- Arc viewed only through the melter's shade window.
- Buttons and chamber cooled before opening.
- Condensate cleaned by wet wipe or HEPA vacuum, never by dry sweeping.
- Gloves and eye protection; respiratory protection as FWM requires.
- Furnace under argon; heat-resistant gloves and a face shield for loading and the quench.
- The site's oxygen monitoring or ventilation for argon.

**Cutting, grinding, polishing:**
- Wet methods only, with local exhaust where available.
- Nitrile gloves and eye protection.
- Sludge and spent abrasive collected (§4).
- Hands washed before leaving the area; no food or drink.

**Electrochemistry and Cr(VI):**
- KOH prepared by a trained person in a fume hood, with splash goggles, nitrile gloves and a lab coat.
- Cells run closed, in a hood or on a ventilated bench.
- Eyewash and shower within reach, and a caustic spill kit present.
- The Hg/HgO electrode handled over a tray; a mercury spill kit available.
- From the first use of a Cr-bearing electrode, all electrolyte, rinse water and wipes are treated as containing Cr(VI).
- Diphenylcarbazide tests run on aliquots in the hood; test solutions go to waste.

**Training and paperwork:**
- Each site's orientation and chemical-hygiene training before work starts.
- The SDS read for each material listed above.
- This assessment signed and dated before the first melt; the STS hazardous-activities form completed from it.

## 4. Waste

| Stream | Contents | Handling (site EHS decides the final codes) |
|---|---|---|
| Spent electrolyte and rinse water | KOH (pH ≈ 14), chromate, dissolved Mn/Co/Ni/Cu/Fe | Closed, labelled hazardous-waste container ("potassium hydroxide, chromate — corrosive, toxic"). Likely RCRA D002 (corrosive) and D007 (chromium). Never down the drain |
| Diphenylcarbazide test solutions | Acid, acetone, chromate | Separate labelled container; acid and organic kept apart |
| EDM and polishing sludge, used abrasives | Metal fines (Cr, Ni, Co, Mn, Cu, Fe) | Collected as metal-bearing waste under FWM or lab procedure |
| Melter condensate wipes, contaminated gloves and wipes | Mn/Cu-rich oxide dust; traces of chromate | Sealed bag, solid hazardous waste |
| Broken Hg/HgO electrode | Mercury | Mercury spill kit; EHS pickup |

**Measuring lab (Tackett group, Purdue ChemE; his email of 2026-10-07):** the lab has no dedicated Cr(VI) disposal method yet but will handle it on site: a separate waste container, with Purdue's waste-removal staff told about it. Nothing is shipped back. Send them this assessment and the expected chromate range so the container can be set up before the first alloy measurement.

## 5. Emergencies

| Event | Response |
|---|---|
| KOH or chromate on skin or in eyes | Flush with water for 15 min (eyewash or shower), remove contaminated clothing, tell the supervisor, seek medical care for eye exposure |
| Spill | Caustic spill kit for KOH; chromate liquids absorbed and collected as hazardous waste |
| Broken reference electrode | Mercury kit, and notify the site EHS |
| Burns, arc flash, oxygen deficiency | Site emergency procedures |

**Residual risk** with the controls above: low. The quantities are gram-scale metal and milligram-scale chromate, all handled in closed equipment.

## 6. Sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| Entrant | Frank Cai | | |
| Designated supervisor, Fort Wayne Metals (melting, annealing, cutting) | | | |
| Designated supervisor, Purdue electrochemistry lab | | | |
| Mentor of record, if different | | | |
