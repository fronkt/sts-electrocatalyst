# Full-text eligibility — instructions v4 (2026-09-27; identical for every read)

v4 applies the entrant's rulings of 2026-09-27 (`reconcile/entrant_decisions.md`). v3 is kept as `eligibility_instructions_v3.md`.

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
  - A genuine review or perspective is `NO` even when it contains new calculations. Judge the form from both the journal's label and the content; when they disagree, say so in the note.
  - Reusing published data alone (no new calculation in this study) is `UNCLEAR`. Say so in the note, and set `secondary` (see Output) when the authors re-analyse their own earlier calculations.
- **E2 — first publication date 2011-01-01 to 2026-09-18.** Use the first-publication (online or print) date printed on the paper. Received and accepted dates, and a year inside the DOI, are not publication dates. If no publication date is printed, answer `UNCLEAR`; dates are then settled from publisher and Crossref records outside this read.
- **E3 — the authors themselves calculate OER in this study.** This means they compute the OER intermediates (*OH, *O, *OOH or equivalent) or the steps with DFT or a similar electronic-structure method.
  - Quoting or plotting numbers from other work is not enough. A citation next to a value does not settle who computed it: check the methods, captions and SI text in your file.
  - Declared approximations are allowed, for example *OOH from a stated scaling relation (ΔG_OOH = ΔG_OH + 3.2 eV) or cycle closure.
  - Re-analysis of the authors' own earlier calculations with no new calculation is `NO` for the primary population; set `secondary` to `"reanalysis"`.
  - Computing only part of the cycle (a surface Pourbaix diagram of *OH/*O, one PCET step, intermediates only for spectra) can satisfy E3 if the OER intermediates are computed, but it does not by itself satisfy E6. A two-electron peroxide pathway is not O2 evolution.
- **E4 — the surface is a rutile-structured oxide.** Examples: RuO2, IrO2, TiO2 (rutile), SnO2, MnO2 (β/rutile), PbO2, VO2(R), CrO2, doped or mixed rutile phases, and "rutile-type" solid solutions.
  - The rutile polymorph must be stated or plainly established **for the computed model**.
  - Plainly established: a phase-specific diffraction card identified with rutile (e.g. RuO2 PDF/JCPDS 43-1027, IrO2 15-0870, SnO2 41-1445, TiO2 rutile 21-1276), an explicitly rutile structure reference or CIF, or a stated unit cell and atomic arrangement that is rutile. Quote the evidence.
  - Not enough on its own: "tetragonal", the formula ("RuO2"), "RuO2(110)"/"IrO2(110)", or generic CUS/bridge labels. Then E4 is `UNCLEAR`.
  - The evidence must belong to the computed model, not only to another component of the experimental sample.
  - Anatase, perovskite, spinel, amorphous or other polymorphs mean `NO`.
- **E5 — OER is calculated on a (110) surface.** The OER intermediates or steps (E3) are computed on a rutile (110) surface, alone or with other facets. Doped or mixed rutile (110) models count.
  - A periodic slab is not required. A nanoparticle facet, cluster or interface counts only when the paper shows that the computed OER site represents rutile (110). An arbitrary molecular cluster, a metal particle on a rutile support, or an oxide–oxyhydroxide site is `NO`. "Commercial IrO2" with no computed model is `NO`.
  - A (110) slab used only for other purposes does not satisfy E5. Examples: electronic structure, PDOS, adsorption of other species, or stability.
  - If the main text does not state which facet the OER was computed on, answer `UNCLEAR`. If E1–E4 are `YES`, the disposition is then `NEEDS_SI`.
- **E6 — a CHE overpotential is reported for the qualifying rutile (110) model.** SI counts equally.
  - A numerical theoretical or limiting overpotential (η) from the free-energy steps counts.
  - **Reported equivalent (v4):** the paper evaluates the largest reaction free-energy step minus 1.23 eV (or the largest step at U = 1.23 V), or states a minimum CHE limiting potential U_L, and the CHE free-energy steps and the surface are identifiable. Set `eta_form` to `"equivalent"`. Check that it is a step between intermediates, not a transition-state barrier. A lone ΔG_RDS at U = 0 that you would have to convert yourself does not count.
  - **Scaling-derived η** counts when the authors report it for the qualifying surface from their computed inputs. Set `eta_form` to `"scaling"`.
  - **Graphical, relative or symbolic η** counts when it is explicitly labelled as the authors' CHE result for identifiable surfaces: an η arrow or labelled η on a diagram, volcano or bar plot, a plotted Δη, or "η_A > η_B" as a finding. Set `eta_form` to `"graphical"` or `"relative"`. Never invent a number.
  - The η must belong to the rutile (110) model. An η given only for another facet, or for a non-rutile component, does not count.
  - The following are `NO`, or `UNCLEAR` if you cannot tell:
    - ΔG values from which *you* would have to pick a pathway and compute η;
    - a generic "energy barrier" not identified as the CHE maximum step at equilibrium;
    - instructions on how to compute η;
    - an experimental or applied operating overpotential, a current-dependent kinetic overpotential, or an activation barrier;
    - a chosen potential at which the steps happen to be downhill, or a universal volcano-apex optimum;
    - a conceptual sketch, an unlabelled volcano point, or an inequality stated as background;
    - a GC-DFT η alone (grand-canonical DFT is not CHE unless a CHE result is also given).
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
 "exclude_criterion": "E1..E6 or null",
 "eta_form": "numeric|equivalent|scaling|graphical|relative|null",
 "secondary": "reanalysis|null",
 "note": "<= 40 words"}
```

`eta_form` records how the qualifying η is reported (null when E6 is not YES). `secondary` marks re-analysis of the authors' own earlier calculations.

When the disposition is `EXCLUDE`, you may stop evaluating the criteria after the first clear `NO`. Give the remaining criteria as `{"v": "NOT_ASSESSED"}`.
