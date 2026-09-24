# Title/abstract pre-screen — instructions (identical for pass A and pass B)

You screen literature records for a registered review. The **population** is primary research first published 2011-01-01 through 2026-09-18 that **calculates the oxygen evolution reaction (OER) on a rutile-oxide (110) surface and reports a computational-hydrogen-electrode (CHE) overpotential** in the article or its SI. Comparative or multi-material calculations qualify. Reviews, purely experimental work, other surfaces, and work without a reported CHE overpotential do not qualify.

This is only a **pre-screen** on title, abstract and metadata. It decides which records go to full-text review. It is **not** an eligibility decision.

## Labels (exactly one per record)

- `CLEARLY_IRRELEVANT` — the title/abstract/metadata make it plain that the work cannot contain an OER calculation on a rutile-oxide surface. Examples: a different field (tribology, medicine, geology, optics with no electrocatalysis), purely experimental synthesis/characterisation with no computation mentioned **and** nothing suggesting DFT, a non-rutile material family only (e.g. perovskites, spinels, MOFs, carbon) with no rutile oxide in view, HER/ORR/CO2RR-only work with no OER, battery or photovoltaic work with no OER.
- `POSSIBLY_RELEVANT` — anything that could plausibly contain such a calculation, including in the SI: any DFT/first-principles/computational electrocatalysis on oxides; any OER work on RuO2, IrO2, TiO2, SnO2, MnO2, other rutile or rutile-derived oxides (doped, mixed, alloyed, "rutile-type"); experimental OER papers on rutile oxides that mention calculations, theory, descriptors, scaling relations or overpotential estimates; reviews (they are excluded later on full text, but flag them so the full-text step records the reason).
- `LIKELY_RELEVANT` — the title/abstract explicitly indicate DFT/CHE-style OER calculations on a rutile oxide (e.g. "(110)", "theoretical overpotential", "adsorption energies of OH/O/OOH", "computational hydrogen electrode", "scaling relations" with RuO2/IrO2/rutile).

## Rules

- **When in doubt, do not use CLEARLY_IRRELEVANT.** A missing abstract, a non-English record, a vague title, or a missing "(110)"/"CHE" is never enough by itself. A record with no abstract gets CLEARLY_IRRELEVANT only if its title alone is unmistakably outside the field.
- Judge each record independently from its own fields. Do not use outside lists or other screeners' outputs.
- Do not judge publication date, article type or access — later steps handle those.
- Do not record method details (symmetry, magnetism, imaginary modes, data deposition); only the label and a short reason.

## Output (JSONL, one line per input record, same order)

`{"screen_id": "...", "doi": "...", "label": "CLEARLY_IRRELEVANT|POSSIBLY_RELEVANT|LIKELY_RELEVANT", "reason": "<= 25 words"}`
