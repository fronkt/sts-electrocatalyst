# Lim (2021) and Lee (2022) supplement access check, 2026-09-23

TODO item: *Check remaining Lim/Lee supplement access through actual publisher or repository links; retain failures.*

Only legal public routes were used: publisher pages, Crossref, DataCite, the DOI handle API, Unpaywall, Europe PMC, NCBI PMC, OpenAlex, figshare, Zenodo and the MPG PuRe repository. There was no login, no library proxy and no shadow library. All 70 requests, successes and failures, are in `receipts.json` (also `receipts.jsonl`). Each receipt holds the URL, HTTP status, content type, bytes, SHA-256 and UTC time, and every response body is kept under `bodies/`. `verification.json` holds the identity and hash checks. Nothing here changes an eligibility decision, and methods stay NOT_CODED.

## Sources

| Paper | DOI | Publisher | Declared supplement |
|---|---|---|---|
| Lim et al. 2021, *First-Principles Design of Rutile Oxide Heterostructures for Oxygen Evolution Reactions* | 10.3389/fenrg.2021.606313 | Frontiers Media SA (Front. Energy Res.) | 5 files in the JATS XML: SM1 `table1.docx`, SM2 `table2.docx`, SM3 `image1.tif`, SM4 `image2.tif`, SM5 `image3.tif`. The article text cites Supplementary Tables S1–S2 and Figures S1–S3. |
| Lee, Scheurer, Reuter 2022, *Epitaxial Core-Shell Oxide Nanoparticles…* | 10.1002/cssc.202200015 | Wiley-VCH (ChemSusChem 15(10) e202200015), CC BY 4.0, PMC9321688 | One file, "Supporting Information". The publisher file name is `cssc202200015-sup-0001-misc_information.pdf`; in PMC it is `CSSC-15-0-s001.pdf`. |

## Outcome per declared file

| File | Status | Evidence |
|---|---|---|
| Lim SM1 `table1.docx` = Table S1 | **CLOSED** | Component DOI `.s004` from Frontiers' figshare portal, article 13902623, file 26435288. MD5 matches figshare `computed_md5`. The Crossref component title is `table1.docx` and its `is-component-of` is the article DOI. The caption opens "Table S1. Binding energies and free energies of OH*, O*, OOH*…". |
| Lim SM2 `table2.docx` = Table S2 | **CLOSED** | `.s005`, figshare 13902626 / 26435291, MD5 match, caption "Table S2. Free energy differences for each step of OER…" |
| Lim SM3 `image1.tif` = Figure S1 | **CLOSED** | `.s001`, figshare 13902611 / 26435279, MD5 match. The printed caption, read visually, is "Figure S1. Equation of state for bulk (A) VO2, (B) SnO2, (C) TaO2 and (D) OsO2". |
| Lim SM4 `image2.tif` = Figure S2 | **CLOSED** | `.s002`, figshare 13902614 / 26435282, MD5 match, caption "Figure S2. Linear relation between the ESSI and the overpotential of the OER…" |
| Lim SM5 `image3.tif` = Figure S3 | **CLOSED** | `.s003`, figshare 13902620 / 26435285, MD5 match, caption "Figure S3. Linear scaling relationship of ΔG3 as a function of ΔG2…" |
| Lee Supporting Information (14 pp.) | **CLOSED** | There are two independent copies: the Europe PMC `supplementaryFiles` zip member and the PMC Open Access AWS open-data object. Their SHA-256 values are identical, and the MD5 equals the PMC record's `md5` for `CSSC-15-0-s001.pdf`. The PMC record DOI is 10.1002/cssc.202200015. The title page gives "Supporting Information", the article title and all three authors. |
| Lee article, real PDF (was web-only) | **OBTAINED, verified** | MPG PuRe REST content endpoint for `file_3400083`, marked publisher-version under CC BY 4.0. The MD5 `94617fc3…` equals the PuRe checksum. PDF page 1 is an image-only cover, and the article pages 1–10 are PDF pages 2–11. |

These Lim component DOIs are only mapped to article files. The XML order (SM1–SM5) and the DOI order (`.s001` = image1 … `.s005` = table2) differ. The mapping is made by file name and the Crossref component title, not by order.

## Reference lists

- **Lim supplements**: no reference list. The two DOCX tables contain no citation-like strings. The three TIFFs are figures with printed captions only. The 4th TIFF sample is an unassociated alpha channel, so a naive viewer shows black text on black.
- **Lee SI**: 9 numbered references on p. S14, in `lee2022_si_reference_block.txt` (locators `L<n>@P<1-based page>`). They are not merged into any index.
- **Lee article PDF**: `lee2022_article_pdf_reference_block.txt` contains refs [1]–[67], read left column then right column with running header and footer clipped (`L<n>@P<page><L|R>`).
- **Comparison with the 2026-09-21 web transcription** (`results/s2_2026-09-21/backward_reference_extension/lee2022_article_reference_block.txt`): both have 67 references. After removing the listed running header and footer strings and the web locators, all 67 are text-identical. Without that removal, the web block differs only at [57] (header/footer text inside the entry) and [58] (its label sits mid-line after a footer at L896). The earlier review already recorded this. The web block's zero-indexed P9/P10 match the 1-based PDF pages 10/11 of this file.

## Routes that failed (retained as evidence)

- Wiley `pdfdirect`, `doi/pdf`, `doi/full`, `doi/full-xml` (the Crossref text-mining links, tried without a TDM token) and `action/downloadSupplement` all returned HTTP 403 with an HTML body. Because of this, the Lee SI could not be compared byte-for-byte with Wiley's own copy.
- Europe PMC PDF render (`ptpmcrender.fcgi`): 403. PMC OA web service (`oa.fcgi` at both hosts): 404.
- PuRe `pubman/.../component/...pdf` public URL: 403 again, the same as 2026-09-21. The REST `content` endpoint for the same file worked.
- Frontiers component landing URLs registered in Crossref (`/supplementary-material/<s00N DOI>`): each returned HTTP 200 with the article full-text HTML, byte-identical across all five, and no file.
- No hits from DataCite related-identifier search (either paper), Zenodo (either paper), figshare for Lee, or Europe PMC for Lim. DataCite has no record of the `.s00N` DOIs, which are Crossref components.

## Routes needing the user (optional, not required to close any gap)

- Downloading the Lee SI or article from Wiley in an interactive browser would give a publisher-byte comparison against the PMC and PuRe copies. The Purdue library proxy was not tried. Both works are CC BY, so a proxy is not needed for access.

## Scripts

`access_log.py` is the shared fetch and receipt helper (1.5 s spacing, backoff on 429/5xx). The routes are in `stage1_metadata.py`, `stage2_files.py`, `stage3_lee_article.py` and `stage4_lee_si_crosscopy.py`. `verify.py` writes `receipts.json`, `verification.json`, `files/` and the reference blocks. Verified copies are in `files/`, and raw bodies are in `bodies/`.

## Note — 2026-09-24

- The two Lee reference blocks were rewritten with LF line endings so their bytes match the `reference_block.sha256` values in `verification.json` (the content was hashed as LF; the first write used CRLF). Content is unchanged.
- Lim 2021 and its five supplementary files are CC BY 4.0 (Crossref licence field, figshare and publisher pages in `bodies/`); `verification.json` omits the Lim licence field.
- Independent review: `../independent_review_2026-09-24.json` (PASS_WITH_FINDINGS; no data defects).
