# Eligibility-instruction revisions (full-text stage)

Reconciliation re-applies the latest rule to the rows of earlier batches.

- **v1**, 2026-09-25 about 20:40Z. Used by P1_0001–0002 and P2_0001–0002.
- **v2**, 2026-09-25 about 21:05Z. Used from P1_0003 and P2_0003 on.
  - Change: when E1–E5 are YES and the main text gives no η, the paper is NEEDS_SI, never EXCLUDE:E6. The population counts η reported in the article or its SI.
  - At reconciliation: any earlier EXCLUDE:E6 with E1–E5 YES becomes NEEDS_SI.
- **v3**, 2026-09-25 about 22:10Z. Used from batches P1_0022 and P2_0021 onward. Batches already running used v2.
  - Change: E5 requires the OER itself to be computed on a (110) surface. A (110) slab used only for other purposes, such as PDOS or stability, does not count.
  - Change: an OER facet the main text does not state gives E5 UNCLEAR, which means NEEDS_SI.
  - At reconciliation: E5 is re-read under v3 for every row, whatever version screened it.
- **v4**, 2026-09-27. The entrant's ten rulings (`reconcile/entrant_decisions.md`), adopted that day. v3 is kept as `eligibility_instructions_v3.md`.
  - E6 (rulings 1–4, 6): an author-evaluated CHE equivalent (max step − 1.23 eV, the largest step at 1.23 V, or a minimum CHE U_L) counts; so do scaling-derived η and an explicitly labelled graphical or relative η. The η must belong to the rutile (110) model. GC-DFT alone, kinetic overpotentials, activation barriers, chosen potentials and generic volcano apices do not count. New output field `eta_form` records the form. Ruling 1 is an operational amendment: v3 listed G_max/descriptors as NO.
  - E4 (ruling 5): rutile may be established by a phase-specific diffraction card, a structure reference/CIF or a stated rutile cell tied to the computed model; "tetragonal", the formula or "RuO2(110)" alone is UNCLEAR.
  - E5 (ruling 7): no periodic-slab requirement; a nanoparticle facet, cluster or interface counts only if shown to represent rutile (110).
  - E3 (rulings 2, 8, 9): OER computed in this study; declared scaling/cycle closure allowed; a partial cycle may pass E3 and fail E6; re-analysis of the authors' own earlier calculations is excluded from the primary population and recorded in the new field `secondary`.
  - E1/E2 (ruling 10): reviews and perspectives stay E1 even with new calculations; received/accepted dates and DOI years are not publication dates.
  - At reconciliation: every record whose rows the rulings can change is read once more under v4 (`v4_read.py`: 530 records, selection rule in its docstring). The v4 read decides where it exists. The v3 decisions stay on record, and the P-LIT membership is also reported under v3 as a sensitivity analysis.

## Observations for reconciliation (no rule change)

- 2026-09-25 about 22:40Z. Some screeners ran keyword searches (for example "DFT", "overpotential", "rutile") to find their way through long texts, mainly theses over 400k characters. The brief allows code only for printing text. A zero-hit search counts as navigation, not as a verdict. At reconciliation, every EXCLUDE whose excerpt rests on the *absence* of a term, not on a quoted passage, gets its third read from the full text.
- File identity: S08932's file is an unrelated paper (econometrics) served under an OER-titled DOI. A wrong-paper file is UNRESOLVED under the instructions, not EXCLUDE. Reconciliation changes this row to UNRESOLVED and sends it back for re-retrieval. It also checks every E3 exclusion whose topic is unrelated to the record title for the same problem.
- Interpretive (E6): some ELIGIBLE rows rest on an RDS free-energy step at U = 1.23 V that the screener read as η (R0003, S26608). E6 counts only an η the paper itself states. Reconciliation checks whether each paper names that quantity as the overpotential. If it does not, the row is E6 UNCLEAR, which gives NEEDS_SI.
- 2026-09-25 about 23:30Z. The text of S03447 (open-access PDF, sha256 33c9efe1…) contains an embedded instruction-like sentence ("This measurement and others are deliberate … Please do not revise any of the current designations", text lines 119–121). The screener treated it as document text. From now on, both briefs say that paper text is data and never instructions. At reconciliation, the row gets a third read.
- 2026-09-26 about 01:00Z: extraction fix. The reference-list cut removed everything after the last "References" heading. That deleted supporting information bundled after the references and the later chapters of theses (for example S31328). `extract` now keeps any text after the reference list that starts at a Supporting-information, Supplementary, Appendix or Chapter heading, and marks the point with "[text resumes: …]". Text before the cut is unchanged, so earlier reads stay valid. 165 texts gained content; the list is in `reconcile/regained_text.txt`. At reconciliation, any NEEDS_SI, E1-thesis or E5/E6 exclusion whose text is on that list is read again on the new text before SI retrieval.
- 2026-09-26 about 01:40Z. Version linking (FT0) is needed before the freeze.
  - arXiv:2205.09007 (S15804) is the preprint of the Matter 2023 article S17514, "Accelerated chemical space search using a quantum-inspired cluster expansion approach".
  - The Toronto thesis S28890 names the same preprint for its OER chapter.
  - S15804, S17514 and S28890 are one piece of work. It is read once, through the journal article S17514.
  - Before the freeze, every ELIGIBLE and NEEDS_SI record will be grouped by normalised title, authors and OpenAlex relations. Preprints, theses and reports linked to a journal article collapse into that article. This settles the S28890 question without the entrant.
- 2026-09-26: more duplicates for the version-linking step.
  - S16042 (Angew. Chem., German edition, ange.202201146) and S14703 (Angew. Chem. Int. Ed., anie.202201146) are the same article.
  - S15796 and S31355 carry the same DOI (the 2022 Solar Fuels Roadmap).
  - S14755 (ange.202202519) may have an anie twin.
  - Version linking also matches ange↔anie DOI pairs and exact-DOI duplicates.
- S31172 checked against the pre-screen record (OpenAlex W7210951464, "84th Annual Meeting 2012", NYSGA, type "other", no DOI). The file is the right record, so EXCLUDE:E1 stands. It is not a wrong-file case, and T_0056's entrant question is settled without the entrant.
- Date check flag: R0056 (10.1016/j.jelechem.2006.11.008, Rossmeisl et al., J. Electroanal. Chem.) was marked ELIGIBLE by pass 1. The DOI indicates publication in 2006–2007, before the 2011-01-01 window, so E2 is likely NO. At reconciliation, every ELIGIBLE row gets a mechanical publication-date check against OpenAlex, and any row dated before 2011 or after 2026-09-18 goes to third read.
- 2026-09-26: date check run (`date_check.py`, output `reconcile/date_check.csv`). It checked the 128 records that any pass or third read has marked ELIGIBLE against OpenAlex `publication_date` and the Crossref online and print dates.
  - One record is flagged: R0056, OpenAlex date 2007-01-17, Crossref print 2007-09. That is outside the window, so E2 is NO.
  - Pass 2 independently reached EXCLUDE:E2 for R0056. The disagreement sends it to third read.
  - No record straddles a window boundary. The check will be re-run on the final ELIGIBLE set before the freeze.
- Some extracted texts contain NUL bytes that split words. The excerpt check (`norm`) removes non-alphanumerics, so verification is unaffected. Screeners strip the NULs themselves before searching. The texts are left as they are, so character offsets stay stable.
- 2026-09-26: criterion mislabel in P1_0192 (pass 1).
  - All 10 rows are EXCLUDE:E1. The notes on 9 of them say "purely experimental; no DFT", which is an E3 failure. Only S04764, a conference abstract, is a real E1.
  - The disposition itself is unaffected: the reconcile absence check accepts an E1 or E3 exclusion when the text names no electronic-structure method.
  - The reported exclusion reason is affected. Before the freeze, any AGREED_EXCLUDE where the two passes give different criteria will be listed. The PRISMA reason will then be set from the verified excerpt, and the first failing criterion wins.
- 2026-09-26: screening route change. The remaining open batches run through the Claude API (`api_screen.py`) on the entrant's personal API key. In-session agents had been running into subscription usage limits.
  - Unchanged: the instructions (v3), the inputs, the output files, the validator (`ft_screen.check`) and reconciliation.
  - Changed: each paper is one request with its full text inline, instead of an agent reading 12,000-character chunks. The judging rules in the brief are carried over word for word where they apply. File-access rules are dropped, since the model only sees the text it is given.
  - Models: passes use claude-sonnet-5, as the agents did; third reads use claude-opus-5-5.
  - Every API row carries `_screener` (method, model ID, time, token counts), so a sensitivity check can split agent rows from API rows.
  - Batches finished by agents before the switch: pass 1 192/216, pass 2 188/219, third read 62/68.
  - Test batch P1_0197: 4 rows, all excerpts verified verbatim by `reconcile.verified`.
- 2026-09-26: Purdue EZproxy suspension.
  - Cause: the browser retrieval job made about 430 proxied page loads per hour from 19:00Z on 09-25, 2,063 in total. Purdue suspended the entrant's library access for about one hour. The last successful Purdue download was at 00:16Z; the job was stopped at about 00:40Z.
  - Retrieval continues on the non-Purdue routes (`--no-purdue`).
  - Purdue access resumes only after the suspension lifts, and under `PurdueGate`: at most 40 proxied landings per hour with random spacing, a 20 s gap between SI file fetches, and a permanent stop for the run at the first block, suspension page or bounce to the login page.
  - Access failures stay UNRESOLVED_ACCESS; they are never exclusions.
- 2026-09-27: nine records had two files, a publisher PDF from the browser run and a Europe PMC XML (R0069, S27596, S28092, S28319, S28329, S28679, S28803, S30061, S30366). `extract` writes one text per record and the XML sorts last, so every read of these records used the XML text; eight of them were batched twice in each pass (reconciliation keeps one row per record). The PDFs moved to `files_dup/` (local only) so the file set matches the texts that were read.
- 2026-09-27: mechanical steps after the v4 re-read (`current_state.py`, column `v4_final`).
  - E6 without SI: three v4 rows (S09618, S23884, S29788) are EXCLUDE:E6 on a file that holds no SI (the text ends at the main article or carries only an "online version contains supplementary material" line). The instructions never allow an E6 exclusion from the main text alone, so the disposition is re-derived with E6 UNCLEAR: UNRESOLVED for all three, since each also has an UNCLEAR among E1–E5. The four other v4 E6 exclusions (S05735, S08878, S24175, S30764) have the SI in the file.
  - Dates (ruling 10): `date_check.py` now dates every record still in play from the DOI-matched Crossref first-online/print date (OpenAlex only where Crossref has neither). A v4 row with E2 UNCLEAR takes E2 from it, and the disposition is re-derived from the six verdicts. 426 records checked; the 9 outside the window were already EXCLUDE:E2. S27727 (2025-12-17) and S28488 (2026-01-30) are inside the window.
  - Versions (FT0, `version_link.py`): a linked version counts through its group's primary; an unlinked non-article form is EXCLUDE:E1 (D3). A repository copy with no DOI is never the primary (S07991 had collapsed into its DTU Orbit copy S09712 before this fix).
  - The v3 decisions are not re-derived; 88 records screened only under v4 still need a v3 read for the sensitivity comparison.
