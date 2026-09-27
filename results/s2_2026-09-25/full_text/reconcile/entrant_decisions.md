# P-LIT full-text screening: rulings the entrant decides (FT4)

The third reads raised 72 questions (52 in the first round, 9 after the 2026-09-26 retrieval, 7 after the second 2026-09-26 retrieval, 4 after the 2026-09-27 retrieval) (`third_read/third_read.jsonl`, field `entrant_question`). They reduce to ten rule-level rulings.
- Each ruling is made once and then applied mechanically to every record it covers.
- That includes NEEDS_SI records that turn on the same point. Most NEEDS_SI rows give ΔG_RDS / ΔG_max but never write "η".
- The current reading in each item is the adjudicator's best reading under instruction v3. It is not a ruling.
- All ten rulings were adopted by the entrant on 2026-09-27 and written into `eligibility_instructions.md` as v4 (v3 kept as `eligibility_instructions_v3.md`). Every record they can change is re-read under v4 (`v4_read.py`).

## D-A. What counts as a reported CHE η (E6)
1. **Largest step minus 1.23 eV, not called an overpotential.** This covers ΔG_RDS, ΔG_max or ΔG_loss at U = 1.23 V, or ΔG_max − 1.23.
   - Records: R0003, S26608, S27035, S29195, S01896, S01698, S27052, S28435, S11646, S24020 (an "energy barrier" at U = 1.23 V). It also decides many NEEDS_SI rows.
   - Current reading: mixed; some ELIGIBLE, some NEEDS_SI.
   - Ruling: ADOPTED 2026-09-27 (operational amendment to E6). Accept an author-evaluated CHE-equivalent: max step − 1.23 eV, or the largest step at U = 1.23 V, when the CHE steps and the surface are identifiable. Recorded as eta_form "equivalent", separate from a labelled η. Not enough: a lone ΔG_RDS the reader must convert, a generic "energy barrier", raw adsorption energies, a transition-state barrier. The v3 (original-rule) membership is kept for a sensitivity analysis.
2. **η obtained through the scaling relation.** ΔG_O − ΔG_OH goes through ΔG_OOH = ΔG_OH + 3.2 eV, and *OOH is never computed.
   - Records: S12709, S15489, S16427.
   - Current reading: ELIGIBLE.
   - Ruling: ADOPTED 2026-09-27. Yes, when the authors report η for the qualifying surface from their computed inputs and a stated scaling relation. Recorded as eta_form "scaling". A generic scaling volcano with no result for the surface does not count.
3. **η shown only symbolically, relatively or graphically.** Examples: "η_A > η_B" labelled on a diagram, Δη against strain, a point on an η volcano with no number.
   - Records: S15804, S17514, S21244, S22425, S26669, R0102 (only a 0.03 V difference between computed η, no absolute values in the main text), S24393 (a figure plots "theoretical overpotential" per model; the text gives only 0.46–0.66 eV RDS "energy barriers").
   - Current reading: ELIGIBLE.
   - Ruling: ADOPTED 2026-09-27. Yes, when explicitly identified as the authors' CHE result for identifiable surfaces (labelled η plot, plotted Δη, η_A > η_B as a finding). Recorded as graphical/relative; no number invented. A conceptual sketch, unlabelled volcano point or background inequality does not count.
4. **A potential that is not a CHE step η.** Examples: the applied potential at which every step turns downhill, or a value read off an activity model at a current.
   - Records: R0101, S29447, S27345 (volcano-apex η plus per-surface limiting potentials), S22122 (a "kinetic overpotential" from the electron-transfer steps only, leaving out a larger O2-desorption barrier on a dual-site diagram).
   - Current reading: R0101 NEEDS_SI; S29447 and S22122 ELIGIBLE.
   - Ruling: ADOPTED 2026-09-27. Split by definition, not label: an explicit minimum CHE limiting potential U_L counts under ruling 1; a chosen potential where steps happen to be downhill, a universal volcano apex, a current-dependent kinetic overpotential or an activation barrier does not. S22122 goes to SI review (a chemical desorption step does not by itself make the descriptor non-CHE).

## D-B. Rutile "plainly established" (E4)
5. **Rutile never named.** Instead the paper gives one of: "tetragonal" with rutile lattice constants, a JCPDS/PDF card (e.g. 40-1290), a Ru_cus/O_br (110) termination, or a bare "IrO2(110)".
   - Records: S06823, S09470, S10090, S14755, S16392, S17871, S17878, S18369, S20021, S21915, S24149, S25113, S27052, S28435, S30165, R0085 and S20253 (bare IrO2(110) / RuO2(110)), S30769 (RuO2(110) with CUS/bridge sites, "rutile" absent from the main text), S22870 and S22871 (crystalline MnRuOx (110) built on RuO2, JCPDS 43-1027), S23547 (RuO2 indexed to PDF#43-1027), S26062 (RuO2 named with no polymorph or facet; current reading NEEDS_SI). Split cases: S21140 (VO2) and S24832 (mixed anatase/rutile support).
   - Current reading: mostly ELIGIBLE, i.e. rutile taken as established.
   - Ruling: ADOPTED 2026-09-27. Accept convincing structural evidence tied to the computed model: a phase-specific diffraction card identified with rutile (e.g. RuO2 PDF 43-1027), an explicit rutile structure reference/CIF, or a stated rutile cell and arrangement. "Tetragonal", the formula, "RuO2(110)"/"IrO2(110)" or generic CUS/bridge labels alone do not establish E4 (UNCLEAR). Evidence for another sample component does not transfer to the model.

## D-C. Whose surface and which facet (E5)
6. **Must the reported η belong to the (110) surface?** Some papers compute (110) but give numeric η only for another facet or a doped site; others give (110) only in SI figures.
   - Records: R0101, S18369, S18534, S22425, S30039, S20680 (0.33 V η is for Ir nanoparticles on rutile SSO; the IrO2(110) value is a 1.66 eV PDS in SI Table S10), S28092 (CHE η 0.39–0.50 eV for "most facets"; the only number stated for (110) is a GC-DFT η, which also raises whether GC-DFT counts as CHE).
   - Current reading: mixed.
   - Ruling: ADOPTED 2026-09-27. Yes: the η must belong to the qualifying rutile (110) model; doped/mixed rutile (110) counts; SI counts. An η only for another facet or component does not qualify. GC-DFT alone is not CHE. S28092: check Figure S6 for a CHE result that includes (110).
7. **Not a periodic (110) slab.** Examples: the (110) site of a nanoparticle, a molecular cluster mimicking TiO2(110), a supported cluster, an oxide–oxyhydroxide interface, "commercial IrO2" with no model described.
   - Records: S02821, S03555, S11646, S15908, S21627, S24832.
   - Current reading: S15908 ELIGIBLE; the others EXCLUDE or UNRESOLVED.
   - Ruling: ADOPTED 2026-09-27. No blanket periodic-slab rule. A nanoparticle facet, cluster or interface counts only when the paper shows the OER site represents rutile (110) and the η belongs to it. Arbitrary molecular clusters, metal particles on rutile, oxide–oxyhydroxide sites and "commercial IrO2" with no computed model do not. Missing model detail goes to SI/UNRESOLVED.

## D-D. What counts as "calculating OER" (E3)
8. **Only part of the cycle computed.** Examples: a surface Pourbaix diagram of *OH/*O only, one PCET step, intermediates relaxed only to simulate spectra.
   - Records: S19174, S22135, S25750, S28806, S13904 (2e⁻ water-oxidation volcano whose O2-selectivity region rests on computed OH* binding).
   - Current reading: EXCLUDE, except S22135 which is NEEDS_SI.
   - Ruling: ADOPTED 2026-09-27. A Pourbaix diagram, one PCET step or spectra-only intermediates do not establish eligibility by themselves; such a paper may pass E3 and fail E6, so the exclusion is labelled by the criterion that actually fails. Declared scaling/cycle-closure approximations are allowed. A 2e⁻ peroxide pathway is not O2 evolution.
9. **The authors' own earlier DFT, or a value stated next to citations.** Some papers re-analyse free energies from their own previous paper with no new calculation; others give a "calculated" η right after citing other work.
   - Records: R0079, R0120, S07802, S24149.
   - Current reading: R0120 ELIGIBLE; the others UNRESOLVED or NEEDS_SI.
   - Ruling: ADOPTED 2026-09-27. Verify provenance from methods, captions and SI; a nearby citation settles nothing. Primary population: qualifying calculations done in the current study. Pure re-analysis of the authors' earlier calculations goes to a separately recorded secondary set (field `secondary: reanalysis`). Quotation never qualifies. R0120: read the SI.

## D-E. Forms and dates (E1, E2)
10. **Non-article forms and date gaps.**
   - S25109 is a journal-labelled Review that contains new DFT η on rutile (110). Current reading: EXCLUDE:E1. S28707 raises the same point: a self-labelled Perspective with new DFT/MLIP calculations (current reading: EXCLUDE:E3). S20463 is a journal-labelled Paper that calls itself a perspective and adds minor new calculations (current reading: EXCLUDE:E1).
   - S03415, S03632, S03734 and S28890 are theses or reports tied to journal articles or preprints. These go to version linking (FT0), which is mechanical: a form linked to a journal article collapses into that article. No ruling is needed unless you disagree with that.
   - S28488 has no printed date; the DOI shows a 2026 manuscript number. Current reading: UNRESOLVED. S27727 is the same kind of case: no printed date, journal venue and DOI only (current reading: ELIGIBLE); `date_check.py` settles it from Crossref/OpenAlex dates.
   - Ruling 10: ADOPTED 2026-09-27. Genuine reviews and perspectives are EXCLUDE:E1 even with new calculations (form judged from label and content; the exclusion reason is corrected to E1 where the note said no calculation). Dates: publisher first-online/print date, then DOI-matched Crossref, OpenAlex as corroboration; received/accepted dates and DOI years are not publication dates; a conflict across a window edge stays UNRESOLVED. Theses/preprints link to the journal article and count once.
   - S31172 is already settled: it is the right record, and EXCLUDE:E1 stands.

## Not a ruling: text quality
- S14778: the body text is shift-encoded, so the E4 NO rests on a text that cannot be read. It goes to re-retrieval (RERETRIEVE) with the other corrupted texts, not to a ruling.

## Record answers adopted 2026-09-27
- S23547: E4 YES if PDF#43-1027 is tied to the modelled RuO2 phase (it identifies rutile RuO2); Zn-doped (110) is in scope.
- S26062: "RuO2" alone establishes neither rutile nor the facet; stays UNRESOLVED pending SI.
- S24020: Research Square preprint of the Nature Communications article 10.1038/s41467-025-62665-2 (census record S26608). Version-linked; counted once, through S26608. The 0.72 eV (110) step at U = 1.23 V counts under ruling 1 if the figure/methods confirm the CHE reading.
- S24393: E6 YES. Figure 1D is captioned "Theoretical overpotential"; section 4.5 gives the methods. The separate 0.46–0.66 eV "energy barriers" are not needed.

## v5 rulings — adopted 2026-09-27 (answers to the v4-triage questions)

After the v4 re-read, 137 records raised 14 new rule-level questions (`reconcile/v4_questions_triage.md`, D1–D14). The entrant adopted v5 on 2026-09-27 with these explicit conditions, verbatim:

> Yes—adopt v5, dated September 27, 2026, with these explicit conditions:
> - Q3: adopt the conditional v5 rule. Accept an author-reported comparison of the actual maximum CHE reaction steps at a common documented potential, with matching reference conditions and standard one-electron CHE dependence. Generic "lower barriers," arbitrary steps, and comparisons reconstructed by us do not qualify. If those conditions are unclear, leave the record unresolved.
> - Q10: adopt v5's verified-no-SI exception. E6 may be NO after complete article review when publisher evidence confirms no SI exists. An apparently irrelevant SI contents list is insufficient. Existing but inaccessible SI remains unresolved.
> - Adopt the remaining recommendations. Preserve v3/v4 instructions and decisions, document the changes, and apply v5 consistently before freezing membership.

("Q3" is triage D4 and "Q10" is triage D10.) The rulings below go into `eligibility_instructions.md` as v5; v4 is kept as `eligibility_instructions_v4.md` and v3 as `eligibility_instructions_v3.md`. Items marked AMENDMENT change adopted v4 text; the others clarify it.

- **D1 (46 records) — rutile evidence from the sample.** Counts for the model when the paper documents the connection (the model represents that characterized catalyst, a caption or methods sentence ties the structure to the model, or the doped model's parent is the identified rutile phase) and nothing contradicts it. A shared formula, a technique name, or evidence for another component is not a connection; an assumed shared polymorph leaves E4 UNCLEAR. Not applied to the 46 records as a group.
- **D2 (9) — Pourbaix or spectra only. AMENDMENT (E5 wording).** Species studied as OER intermediates satisfy E3 even when the analysis is stability or spectra, and E5 when on rutile (110); E6 then decides. The E5 "other purposes" exclusion now covers only (110) calculations without the qualifying OER intermediates or steps.
- **D3 (17) — partial or other-purpose adsorbates.** One new intermediate, adsorption energy or PCET step used to investigate water/hydroxide oxidation to O2 satisfies E3. Calculations only for other reactions, photo-holes, generic benchmarks, reused dataset entries, pretrained-model predictions or PDOS-only structures do not. OER studied as a competing reaction counts.
- **D4 (15) — author-reported comparison of maximum steps. AMENDMENT (entrant's condition above).** Counts as a relative η when the authors report the comparison of the actual largest one-electron CHE steps at a common documented potential with matching reference conditions; otherwise the record stays unresolved.
- **D5 (11) — unstated potential.** A value unambiguously assigned to a diagram or caption explicitly at U = 1.23 V (RHE) counts under ruling 1; the magnitude of a value never shows its reference potential.
- **D6 (9) — rutile named in passing.** Referential meaning decides: a sentence identifying the material actually modelled as rutile counts; generic mentions, cited titles and background do not.
- **D7 (7) — standalone forms. AMENDMENT (E1 form ruling, fills a gap D3 left).** A complete primary-research preprint counts (form "preprint", posting date as first publication); a standalone technical report does not. A later out-of-window journal version does not replace in-window preprint evidence.
- **D8 (5) — clusters and single atoms.** A specific statement or mapping figure that a cluster represents rutile (110) suffices; a single atom in a bridging-O vacancy of a persisting rutile (110) surface is an atom-modified rutile (110) model that can qualify.
- **D9 (5) — rutile-type phases.** β-PbO2 establishes E4 after an identity check (not E5 by itself); "similar to rutile" does not; a distorted-rutile phase of another crystal system (monoclinic WO2) is not in the population (no scope extension adopted); a rutile (110)-derived overlayer can qualify. Every model in a paper, benchmarks included, is checked before a NO.
- **D10 (4) — no SI. AMENDMENT (entrant's condition above).** E6 may be NO after complete article review when publisher evidence confirms no SI exists (source and date recorded). A contents list is not enough; existing but inaccessible SI stays unresolved.
- **D11 (4) — re-analysis flag. AMENDMENT (ruling 9's secondary-set definition).** `secondary: reanalysis` covers original re-analysis of own, external or mixed data, with a separate `provenance` field. Primary membership is unchanged.
- **D12 (2) — author-labelled overpotential at U = 0.** Counts as an author-reported η with the inconsistency recorded; a U = 0 "energy barrier", even in volts, does not.
- **D13 (2) — ΔG_max spanning steps.** Counts only when it is the largest single one-electron step between adjacent intermediates.
- **D14 (1) — η descriptors.** `eta_form` (presentation) and `eta_derivation` (direct/equivalent/scaling) are recorded separately; v4 values are migrated by a fixed map.

**Public supporting information (entrant, 2026-09-27, verbatim):** "Public SI: yes. Download freely available SI directly from official publisher pages, slowly, using the existing rate limits and retrieval logs. No Purdue proxy is needed for public files. Respect access blocks and leave unsuccessful downloads unresolved." Implemented in `retrieve_si_public.py`.
