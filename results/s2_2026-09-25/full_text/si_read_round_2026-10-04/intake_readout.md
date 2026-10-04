# SI-read intake, 2026-10-04

Inputs for two independent blind reads (pass 1 and pass 2) of the recovered SI packages. No read was run, no verdict or eligibility decision is made here.

## 1. Packages included

**22 packages**: the 13 packages of `public_si_recovery_2026-10-04/` other than S11392, plus the 9 recovered in `public_si_recovery_2026-10-04_ext/`. Main text: the corpus file `text/<SID>.txt` of each record. SI text: `si_read_round_2026-10-04/files/<SID>/<SID>_si_reading.txt` (1,034,132 main characters, 854,163 SI-reading characters in all).
Not included: **S11392** (Frank, 2026-10-04: linkage only, not sent to the reads; `decisions_2026-10-04.md`) and **S22941** (no SI recovered).
Instructions: `eligibility_instructions.md` (v5, sha256 `e910951616a433cecff859996be6c922d4e9f22808c1d19aa568198014913fb9`, unchanged since the 2026-09-28 SI round); brief: `SI_READ_BRIEF.md`.

| id | SI format | main chars | SI chars | si_complete | batch | visual-review flags | state before (v5_final / lane) |
|---|---|---|---|---|---|---|---|
| S00358 | PDF | 78,398 | 19,000 | true | pdf_01 | 9 of 13 pages with images/drawings | NEEDS_SI / NEEDS_SI |
| S00882 | binary .doc | 42,107 | 16,443 | true | word_01 | 1 carved image | UNRESOLVED / AGREED_EXCLUDE |
| S00887 | Word | 32,765 | 2,527 | true | word_01 | 3 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S05043 | Word | 48,033 | 15,096 | true | word_01 | 1 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S11279 | PDF | 27,289 | 4,746 | true | pdf_01 | 10 of 12 pages with images/drawings | NEEDS_SI / NEEDS_SI |
| S14386 | PDF | 35,285 | 8,029 | true | pdf_01 | 11 of 11 pages with images/drawings | UNRESOLVED / NEEDS_SI |
| S14704 | Word | 84,987 | 30,188 | true | word_01 | 3 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S20599 | Word | 22,419 | 6,316 | true | word_01 | 9 embedded image(s) | NEEDS_SI / THIRD_READ |
| S21070 | Word | 57,691 | 78,665 | true | word_01 | 35 embedded image(s) | UNRESOLVED / NEEDS_SI |
| S21177 | Word | 34,212 | 113,074 | true | word_02 | 37 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S21253 | Word | 46,585 | 29,556 | true | word_02 | 29 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S22127 | Word (2 files) | 40,159 | 87,253 | true | word_02 | 36 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S23135 | Word | 43,645 | 72,610 | true | word_02 | 17 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S23308 | Word | 54,199 | 312 | true | word_03 | 1 embedded image(s); TABLE ONLY AS IMAGE | NEEDS_SI / NEEDS_SI |
| S23544 | Word | 32,562 | 37,644 | true | word_03 | 29 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S27476 | Word | 37,419 | 71,650 | true | word_03 | 22 embedded image(s); 2 SVG without preview (PNG fallbacks previewed) | NEEDS_SI / THIRD_READ |
| S29795 | Word | 60,546 | 41,281 | true | word_03 | 8 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S30334 | PDF | 63,352 | 2,999 | true | pdf_01 | 7 of 7 pages with images/drawings | UNRESOLVED / THIRD_READ |
| S30575 | Word + 3 videos | 47,327 | 79,418 | true | word_03 | 56 embedded image(s); 3 videos not viewed | NEEDS_SI / AGREED_ELIGIBLE |
| S31037 | Word | 51,464 | 47,877 | true | word_04 | 24 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S31125 | Word | 37,879 | 16,552 | true | word_04 | 12 embedded image(s) | NEEDS_SI / NEEDS_SI |
| S31137 | Word | 55,809 | 72,927 | true | word_04 | 78 embedded image(s); 53 equation objects (formulas only as images) | NEEDS_SI / NEEDS_SI |

`si_complete` is true for all 22: each package is the exact article-addressed file set (hash-pinned to the recovery manifests), every SI item the main text names is present in the SI text (the one script hit, S30334 'Section S6', is a regex false hit on 'Sections 6.6.1 and 6.6.2'), and the SI text was extracted without error. It does not mean the images are in the text: figures, and for S23308 the only table, are images (section 3). The basis per package is in `intake_manifest.json` (`si_complete_basis`).

## 2. Pass inputs and batches

Layout mirrors `si_read/pass_<N>/batches/<batch>.in.jsonl` under this directory: `si_read_round_2026-10-04/pass_<N>/batches/<batch>.in.jsonl` and `pass_<N>/plan.json`. Batching follows `ft_screen.py` (480,000 characters of main plus SI text, at most 10 papers per batch) after grouping by SI format as in 2026-10-03 (`pdf_*`, `word_*`); records in screen_id order. **Pass 1 and pass 2 files are byte-identical in content** (verified by `verify_intake.py`), in separate files: only the batch name differs (`SI1_...` versus `SI2_...`).

| batch (pass 1 / pass 2) | records | characters |
|---|---|---|
| `SI1_pdf_01` / `SI2_pdf_01` | S00358, S11279, S14386, S30334 | 239,098 |
| `SI1_word_01` / `SI2_word_01` | S00882, S00887, S05043, S14704, S20599, S21070 | 437,237 |
| `SI1_word_02` / `SI2_word_02` | S21177, S21253, S22127, S23135 | 467,094 |
| `SI1_word_03` / `SI2_word_03` | S23308, S23544, S27476, S29795, S30575 | 462,358 |
| `SI1_word_04` / `SI2_word_04` | S31037, S31125, S31137 | 282,508 |

Line schema (SI_READ_BRIEF.md step 2 fields first): `screen_id`, `doi`, `text`, `si_text`, `chars`, `si_chars`, `si_complete`, `si_files`, `facts`; then, as in the 2026-10-03 inputs, `visual_root`, `main_pages`, `si_pages` (PDF only), `word_media`, `doc_media`, `word_extras`, plus `visual_review` (list of flags with the contact-sheet paths) and `limitations`. `facts` are the identity facts of `reconcile/identity_check.csv` marked supplied_to_reads = yes (same rule as `si_read.py`): S21070, S27476 and S30575 carry one each; S30334's identity check is not marked for the reads and is not supplied.

## 3. Visual-review flags

Markers in the SI text: `[SI file <tag>: <local name> (published as <name>)]` per file; PDFs `[<tag> p. N]`; Word and binary Word have no pages, so locations use `[<tag> paragraph N]` (N counts every paragraph of the part, as in 2026-10-02/03) or, for the binary .doc, `[<tag> block N]`. Word page layout is not rendered (as before). Per package, `files/<SID>/` holds the page images or media previews and 6-up contact sheets (`contacts/`), `visual_index.json` (every image with the paragraph it sits at and a nearest-caption candidate; a mechanical reading aid) and, for Word, `word_extras.json`.

- **S23308, table only as an image.** The SI's only content ('Table 1 - ZPE and TS corrections') is one EMF image; the text has just the caption. No title or authors inside, so **identity rests on the PII-addressed file name** (exact article PII in the download URL). Rendered preview: `files/S23308/docx_media/image1.emf.png`. A reader without image access cannot read the table.
- **S31137, formulas only as images.** 53 MathType equation objects (the OER-step and free-energy equations) appear in the text as empty paragraphs with an image marker; their content is in the WMF previews (rendered with GDI+ because Pillow garbles these metafiles). All 78 media items (53 equation previews, 25 PNG figures) are in document order on `files/S31137/contacts/word_01.png` to `word_11.png` (6 per sheet), except 12 wide equation strips that are on `word_wide_01.png` and `word_wide_02.png`; `visual_index.json` gives each item's paragraph.
- **S00882, one figure outside the text.** Binary .doc read with antiword (text and tables complete, block markers numbered for location only); its single embedded image (the 'Fig. SI' Pourbaix diagram) was carved by PNG signature: `files/S00882/contacts/doc_01.png`.
- **S30575, videos.** Movies S1-S3 (5 s each) are part of the package; inventory only (`files/S30575/video_inventory/`), not viewed.
- **S27476, two SVG members** have no raster preview; the same two pictures carry PNG fallbacks that are previewed.
- **S22127, duplicate file.** mmc2.docx has the same paragraph text and media as mmc1.docx (differs in Word markup only; verified by `prepare_si_round.py`); its text is not repeated in the reading copy.
- **S31125, identity.** The SI's own title differs from the published title; identity rests on the exact PII file, the same four authors and the same sample names (`intake_manifest.json`).
- **All other Word packages and all PDFs:** figures (plots, spectra, micrographs, structure images) are images; the text holds captions and printed labels, not plotted values (brief step 3). PDF pages with images, vector drawings or little text are listed per package in `visual_review`.
- Word-stored page counts are not reliable (S21253 reports 1 page for 29 figures); they are given only as recovery metadata.

## 4. Method (reused from 2026-10-03 and 2026-09-28; refinements listed)

PDFs: PyMuPDF page text in native order, 1.5x page images, 6-up contact sheets (`prepare_sources.pdf_read` / `contacts`). Word: paragraph-by-paragraph accepted-revision text with embedded-image markers, original media plus previews, OMML / revision / embedded-object inventory (`word_extras.json`), and the Pandoc accepted-revision view appended as a 'structured equation/table reading aid' where a file has tables, equations or objects (`inspect_word_extras.py`). Refinements: text-box paragraphs read once (S23135 has 17 text-box pairs), `w:sym` symbols (Greek letters, arrows) and no-break hyphens kept, tabs and manual line breaks kept, transparent images flattened on white (2026-10-03 noted black backgrounds), WMF/EMF rendered with GDI+ via `render_metafile.ps1` (the same local-PowerShell approach as `decode_wdp.ps1`). Binary .doc: antiword text, which `si_read.py` had marked 'not extracted'. Scripts: `prepare_si_round.py`, `build_inputs.py`, `verify_intake.py`, `render_metafile.ps1`, `write_intake_readout.py`.

## 5. What affects running the reads

No blocker. Points for the reader prompts:
1. **Visual folders.** SI_READ_BRIEF.md step 10 forbids opening `files/` and `files_si/` (the corpus-root folders). The visual material for this round is under `si_read_round_2026-10-04/files/<SID>/` (`visual_root`); readers need an explicit instruction to open it (the 2026-10-03 inputs carry the same `visual_root` field for this purpose). Without image access the flagged items (S23308 table, S31137 equations, S00882 figure, all figure-borne values) are unreadable and `si_complete` does not cover them.
2. **Reading load.** Word reading copies contain the Pandoc aid as a second copy of the text for files with tables or equations (S21177: 113,074 characters of SI reading text; the biggest batch is `word_02` at 467,094 of 480,000 characters).
3. **Earlier reads without SI.** S21070, S27476 and S30575 were read in the 2026-09-28 SI round on their main text alone (they carry reconciliation facts; `si_read/queue.csv`); S30575 stands at AGREED_ELIGIBLE with v5_final NEEDS_SI. These reads add the SI.
4. **Dates and identities** are not part of this intake (existing reconciliation: `reconcile/date_check.csv`, `identity_check.csv`).

## 6. Files

In `results/s2_2026-09-25/full_text/si_read_round_2026-10-04/`: `decisions_2026-10-04.md`, `intake_readout.md`, `intake_manifest.json` (per package: source pins, reading-copy pin, si_complete basis, identity basis, visual flags, batch names), `reading_copies_summary.json`, `pass_1/` and `pass_2/` (`batches/*.in.jsonl`, `plan.json`), `files/<SID>/` (reading copies, previews, contact sheets, indexes; local only, ignored by git through the `results/` rule), and the scripts. Source binaries stay in the two recovery directories; nothing was copied out of them. No existing file was changed.
