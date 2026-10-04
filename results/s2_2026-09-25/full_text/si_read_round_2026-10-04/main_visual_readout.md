# Main-text visual evidence, SI-read round 2026-10-04

Gap filled: the blind reads of `si_read_round_2026-10-04/` see only `files/<SID>/` (SI media and previews). This folder holds the MAIN-TEXT page images and 6-up contact sheets for the same 22 records, in the form the 2026-10-03 round gave its readers. No screening decision is made here and no paper was read for content; page images were looked at only to confirm that the right file was rendered (S31037, S31125 and S31137 sheets: journal header, title and figure pages match the record).

Nothing under `si_read_round_2026-10-04/files/` was added or changed (no file there is newer than the first rendering run). Rendered images stay local (`results/` is gitignored); nothing was staged, committed or pushed.

## Layout

```
si_read_round_2026-10-04/main_visual/
  render_main_visual.py            # the script that was run (re-runnable, write-once, refuses a differing existing file)
  main_visual_summary.json         # status of all 22 records
  <SID>/
    pages/<SID>_main_pNNN.png      # one PNG per main-text page, 1.5x
    contacts/main_01.png ...       # 6-up contact sheets, 6 pages each, in page order
    main_visual_index.json         # source path, sha256, page count, render settings, identity checks, per-file sha256
```

## Method (same as download_si_review_2026-10-03/prepare_sources.py, pdf_read + contacts)

- PyMuPDF 1.28.0, `page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))`, PNG, RGB, no alpha; names `<SID>_main_p001.png`, 3-digit page number.
- Contact sheets: 1600 x 2100 white canvas, 2 columns x 3 rows, 800 x 700 pitch, each page thumbnail fitted into 785 x 650 (`ImageOps.contain`), page file name printed at the cell's top-left; names `main_01.png`, `main_02.png`, ... (6 pages per sheet).
- Reading note: a page is shrunk to roughly 500 x 650 px in a contact sheet, as in 10-03; for panel-level reading of a figure use the full `pages/` PNG (about 920 x 1190 px).

## Source identity gate (all 22 passed before any rendering)

The main text each reader gets is `text/<SID>.txt`. It was made by `ft_screen.py extract` from `files/<SID>.pdf`. For every record:

1. sha256 of `files/<SID>.pdf` equals `file_sha256` in `texts.csv`, and the page count equals `texts.csv` `pages`.
2. Re-running the `ft_screen.py` extraction on that PDF (PyMuPDF page text joined by newline, then the reference-list cut) reproduces `text/<SID>.txt` character for character (and the character count equals the pass input `chars`).
3. sha256 of `text/<SID>.txt` equals `main_text.sha256` in `intake_manifest.json`; page count equals the pass-input `main_pages` and the manifest `main_text.pages`.
4. Every other corpus copy of the record (`files_manual/`, `files_dup/`) is byte-identical to `files/<SID>.pdf` (the 13 `files_manual/` copies are; `files_dup/` holds no copy of any of the 22).
5. Supporting only: DOI printed in the PDF (21 of 22; S05043 is the author manuscript, see below), title in the first two pages (22 of 22 after ligature normalisation), and for the files_manual copies the `manual_ingest_log.jsonl` entry (`matched_by: DOI in page 1`, same sha256).

No record is missing a PDF; no record's main text is HTML or extracted-text only; no other version was substituted.

## Per record

| id | pages rendered | contact sheets | source file (under `results/s2_2026-09-25/full_text/`) | sha256 | other corpus copy (identical) | note |
|---|---|---|---|---|---|---|
| S00358 | 14 of 14 | 3 | `files/S00358.pdf` | `fbb57b0bb9bd4b722ff7a600739456726cd1fdaa31640149729398e2c1a77900` | none |  |
| S00882 | 7 of 7 | 2 | `files/S00882.pdf` | `41b2c59838558a1d8c817c7e8c56f0a6372d073f54bdfc13c3411a6744ce07f7` | none |  |
| S00887 | 8 of 8 | 2 | `files/S00887.pdf` | `6771e120a9d7f82581db5846beb6986786364ec1d11b5d5366296c707902fa75` | none |  |
| S05043 | 31 of 31 | 6 | `files/S05043.pdf` | `890b98c9796ecafc8e17f9725966d483ed2a7851adebf4de9fe9418067863d89` | none | Corpus PDF is the Brookhaven author manuscript (BNL-114508-2017-JAAM, 'To be published in J. Electroanal. Chem.'): no DOI printed in the file; identity rests on title (exact match to the manifest title), exact text reproduction and sha256. The corpus holds no other main-text file for this record. |
| S11279 | 20 of 20 | 4 | `files/S11279.pdf` | `94c09defc5ff9db1a9cf3b97bb2867e9778ab578a6670446fe647d369bdbf0ff` | none |  |
| S14386 | 8 of 8 | 2 | `files/S14386.pdf` | `64c9b9863681ffb6794abc170f0d972416a10965a7129d6781c9b1cb735cb7a3` | none |  |
| S14704 | 17 of 17 | 3 | `files/S14704.pdf` | `2422c7e73ad611ff9758bf21fe00224bdf8a0cfab0a925ac3b4dd904d07ba8d9` | `files_manual/S14704.pdf` |  |
| S20599 | 7 of 7 | 2 | `files/S20599.pdf` | `86f9d5bc47559bd67122a12dfbec9fe4c17aef0ec0f5d5b24514f70d8d042ab4` | `files_manual/S20599.pdf` |  |
| S21070 | 38 of 38 | 7 | `files/S21070.pdf` | `56d98718b5d6038aaffdfb7f072411a1eb89c4b0dc6fdcfa67340454a3d34e9f` | none |  |
| S21177 | 20 of 20 | 4 | `files/S21177.pdf` | `44de44f33025ca9e3bae60f0b5630e5b734050ae33bcc9a5af69f7656e15c762` | none | Research Square preprint (DOI 10.21203/rs.3.rs-3710432/v1); the PDF is the preprint. |
| S21253 | 12 of 12 | 2 | `files/S21253.pdf` | `13d8d601f3555c62cefd3baf54b34dbfa4dc94f06cec58b48cc1bd3742adf7cf` | `files_manual/S21253.pdf` | Title string split across a line with a ligature; matched after ligature normalisation (also in PDF metadata with the DOI). |
| S22127 | 9 of 9 | 2 | `files/S22127.pdf` | `fdcadb045fa6ba0f70847f72b76e482bc2280744a5621aaf55039f8f72e59f99` | `files_manual/S22127.pdf` |  |
| S23135 | 11 of 11 | 2 | `files/S23135.pdf` | `52086630942457392432910a973f74bea5099f23631cd057257d341a0a160f38` | `files_manual/S23135.pdf` |  |
| S23308 | 12 of 12 | 2 | `files/S23308.pdf` | `504f439fb5200e244437dbb15af9ad50c2a38fcd113985273e037abeea312015` | `files_manual/S23308.pdf` |  |
| S23544 | 9 of 9 | 2 | `files/S23544.pdf` | `dbc3f218a1bc0b6e2c9792658d307f4bf28fedae996e9406fa9832ad6a68c374` | `files_manual/S23544.pdf` |  |
| S27476 | 10 of 10 | 2 | `files/S27476.pdf` | `316cb9722d2ca86128ff273ae64ce1ba89a9babbc948c7143521035907c743ec` | `files_manual/S27476.pdf` |  |
| S29795 | 32 of 32 | 6 | `files/S29795.pdf` | `e0e5df22c3d5b4945cb49dd205dbabe36603193717f22ce058672451cd54325c` | `files_manual/S29795.pdf` |  |
| S30334 | 14 of 14 | 3 | `files/S30334.pdf` | `ffad0f05b1c1cf136a89c3fdf6486969c12302f0ed15f06ae91f3d1d7ec5a331` | `files_manual/S30334.pdf` |  |
| S30575 | 24 of 24 | 4 | `files/S30575.pdf` | `be6725c6e10c79db39cec17a7ac222150888f1f0976cb65372f9fdb36b1568b5` | none | Research Square preprint (DOI 10.21203/rs.3.rs-10033317/v1); the PDF is the preprint. |
| S31037 | 12 of 12 | 2 | `files/S31037.pdf` | `35bf472b34b87e51986b0864b0efc6bc6f8b032eaf2b42dab533899f5ee9bece` | `files_manual/S31037.pdf` |  |
| S31125 | 8 of 8 | 2 | `files/S31125.pdf` | `021f9dd33b6d90dab413aca79ca1fda08225a426c58f45679bd43185198adf81` | `files_manual/S31125.pdf` |  |
| S31137 | 11 of 11 | 2 | `files/S31137.pdf` | `c50d54fabffaac0a0358c1cde01bc2c69c7dc392d814ba10963f3427c90e69a4` | `files_manual/S31137.pdf` |  |

Totals: 22 records, 334 page PNGs, 66 contact sheets.

## The three records named in the gap

- S31037: 12 pages, sheets `main_01.png`, `main_02.png`. Page locations noted from the sheets only to confirm the right file: Fig. 1 on page 2, Fig. 2 on page 3, Fig. 3 on page 5, Fig. 4 (panels a-f, incl. e) on page 6; all on `main_01.png`.
- S31125: 8 pages, sheets `main_01.png`, `main_02.png`. Page locations noted from the sheets only to confirm the right file: Figs. 1-2 on page 4, Fig. 3 on page 6 (`main_01.png`), Figs. 4-5 on page 7 (`main_02.png`).
- S31137: 11 pages, sheets `main_01.png`, `main_02.png`. Page locations noted from the sheets only to confirm the right file: Fig. 1 (panels a-d) on page 3, Fig. 2 on page 4, Fig. 3 on page 5, all on `main_01.png`.

## Not in scope

S11392 (linkage only, not sent to the reads) and S22941 (no SI recovered) are not among the 22 pass-input records and were not rendered.

