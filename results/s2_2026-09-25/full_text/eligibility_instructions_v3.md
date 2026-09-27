<!-- Archived 2026-09-27: instruction v3, superseded by v4 (entrant rulings of 2026-09-27, reconcile/entrant_decisions.md). Kept for the original-rule sensitivity comparison. -->

# Full-text eligibility — instructions (identical for pass 1 and pass 2)

You decide whether each paper belongs to a registered review population by reading its full text. You decide **eligibility only**.

## Population

The population is primary research articles first published **2011-01-01 through 2026-09-18** that **calculate the oxygen evolution reaction (OER) on a rutile-oxide (110) surface** and **report a computational-hydrogen-electrode (CHE) overpotential** in the article or its supporting information.

- Comparative or multi-material computational studies qualify whatever the authors call them.
- Reviews, perspectives and purely experimental work do not qualify.
- Studies with no rutile (110) calculation do not qualify.
- Studies that do not report a CHE overpotential do not qualify.

## Criteria

Judge each criterion from the paper itself. For each, give a verdict of `YES`, `NO` or `UNCLEAR`, plus the location (page, section or figure) and a short verbatim excerpt of 40 words or fewer that supports it.

- **E1 — primary research article.**
  - Not a review, perspective, editorial, erratum, peer-review report or book.
  - Not a conference abstract or thesis. For those, note the form and whether the text names a journal article that carries the work.
  - Reusing published data alone (no new calculation by these authors) is `UNCLEAR`. Say so in the note.
- **E2 — first publication date 2011-01-01 to 2026-09-18.** Use the dates printed on the paper where available.
- **E3 — the authors themselves calculate OER.** This means they compute the OER intermediates (*OH, *O, *OOH or equivalent) or the steps with DFT or a similar electronic-structure method. Quoting or plotting other groups' numbers is not enough.
- **E4 — the surface is a rutile-structured oxide.** Examples: RuO2, IrO2, TiO2 (rutile), SnO2, MnO2 (β/rutile), PbO2, VO2(R), CrO2, doped or mixed rutile phases, and "rutile-type" solid solutions.
  - The rutile polymorph must be stated or plainly established.
  - A (110) facet alone does not establish rutile.
  - Anatase, perovskite, spinel, amorphous or other polymorphs mean `NO`.
- **E5 — OER is calculated on a (110) surface.** The OER intermediates or steps (E3) are computed on a rutile (110) surface, alone or with other facets.
  - A (110) slab used only for other purposes does not satisfy E5. Examples: electronic structure, PDOS, adsorption of other species, or stability.
  - If the main text does not state which facet the OER was computed on, answer `UNCLEAR`. If E1–E4 are `YES`, the disposition is then `NEEDS_SI`.
- **E6 — a CHE overpotential is reported.**
  - A numerical theoretical or limiting overpotential (η) from the free-energy steps counts.
  - So does an explicitly marked graphical η, such as an η arrow or a labelled η on a free-energy diagram or volcano.
  - The following are `NO`, or `UNCLEAR` if you cannot tell:
    - ΔG values from which *you* could compute η but the paper does not;
    - instructions on how to compute η;
    - an experimental or applied operating overpotential;
    - G_max or other descriptors.
  - If the main text points to the SI for the overpotential and the SI is not in your file, answer `UNCLEAR` and say "in SI".

## Disposition (exactly one)

- `ELIGIBLE`: all six criteria are `YES`.
- `EXCLUDE`: at least one criterion is clearly `NO`. Give `exclude_criterion` as the **first** failing criterion (E1 to E6), and quote the excerpt that establishes it.
- `NEEDS_SI`: either E1–E4 are `YES` and the OER facet is not stated in the main text (E5 `UNCLEAR`), or E1–E5 are `YES` and the main text does not report a CHE overpotential. The population counts an overpotential reported in the article *or its SI*, so such a paper is never excluded on E6 from the main text alone. The exception is when the SI is part of your file: then decide E6 from it.
- `UNRESOLVED`: anything else that cannot be settled from the text. Explain in `note`.

A paper whose file is unreadable, truncated or the wrong paper is `UNRESOLVED` with the reason. **Never** exclude for missing access.

## Rules

- Read the paper yourself. Do not write keyword scripts or code that assigns verdicts. Code may be used only to print the text and to check your output file's format.
- Judge each paper only from its own text. Do not use outside lists, other screeners' outputs or memory of the paper.
- **Do not record method details.** Symmetry settings, imaginary-mode or phonon checks, magnetic-state checks and data deposition are out of scope, even if you notice them. The output has no fields for them.
- Keep excerpts verbatim and short.

## Output (JSONL, one line per paper, same order as the batch)

```
{"screen_id": "...", "doi": "...", "text_ok": true,
 "E1": {"v": "YES|NO|UNCLEAR", "where": "...", "excerpt": "..."},
 "E2": {...}, "E3": {...}, "E4": {...}, "E5": {...}, "E6": {...},
 "disposition": "ELIGIBLE|EXCLUDE|NEEDS_SI|UNRESOLVED",
 "exclude_criterion": "E1..E6 or null", "note": "<= 40 words"}
```

When the disposition is `EXCLUDE`, you may stop evaluating the criteria after the first clear `NO`. Give the remaining criteria as `{"v": "NOT_ASSESSED"}`.
