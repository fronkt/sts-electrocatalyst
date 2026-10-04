# Elsevier asset-CDN extension, 2026-10-04 (retrieval only)

No screening or eligibility decision is made here. Packages listed below are ready for two independent blind reads; whether to run them is the coordinator's call.

## 1. Scope

- Frank, in session, 2026-10-04: keep the 11 Elsevier-CDN packages of `public_si_recovery_2026-10-04/` and extend the same route to the 10 non-tier-1 Elsevier checklist records: S22127, S23544, S31125, S00882, S14386, S21070, S30334, S21253, S22941, S29795.
- Targets come from `si_checklist.csv` (tiers 2: S22127, S23544, S31125; 3: S00882, S14386, S21070, S30334; 4: S21253, S22941, S29795) and `reconcile/current_state.csv`; see `targets.json`.
- Method, unchanged from `els_cdn.py` of the earlier round: identity first (Crossref and OpenAlex by exact DOI; PII from the Crossref `alternative-id`, equal to the PII in the checklist's ScienceDirect link for all 10), then plain HTTP GET of `https://ars.els-cdn.com/content/image/1-s2.0-<PII>-mmc<N>.<ext>` with an honest User-Agent, 5 s spacing, no key, no login, no api.elsevier.com, no proxy, no browser. mmc1 was tried with pdf, docx, zip, xlsx, doc; each mmc<N> that existed was followed by mmc<N+1>. For the one record with no hit, seven more extensions (xls, pptx, txt, csv, mp4, docm, rtf) were tried for the exact mmc1 name.
- The OpenAlex key was read from `~/.config/openalex/api_key` at request time; it is in no file of this directory (scanned).

## 2. Outcomes

Final outcome per record: **recovered 9, not-found 1** (total 10). Requests to ars.els-cdn.com: 78 (HTTP 200: 10, HTTP 404: 68); none was refused or challenged, so no host was gated in this phase (`host_gates.json` was not created; hosts gated in the earlier phase stay gated, read only). Route rows in `search_log.jsonl`: 108 (recovered 19, not-found 89; the 19 `recovered` rows are the 10 CDN files plus 9 record-final rows).
A 404 is logged per exact URL; it is never evidence that no supplement exists.

| id | tier | journal | final | files | pages | note |
|---|---|---|---|---|---|---|
| S22127 | 2 | Energy Storage Materials | recovered | S22127_mmc1.docx, S22127_mmc2.docx | 36 | Word-stored page count (docProps/app.xml); no layout render available |
| S23544 | 2 | eScience | recovered | S23544_mmc1.docx | 31 | Word-stored page count (docProps/app.xml); no layout render available |
| S31125 | 2 | Journal of Power Sources | recovered | S31125_mmc1.docx | 8 | Word-stored page count (docProps/app.xml); no layout render available |
| S00882 | 3 | Electrochimica Acta | recovered | S00882_mmc1.doc | not claimed | not claimed (binary .doc, text read with antiword) |
| S14386 | 3 | Electrochimica Acta | recovered | S14386_mmc1.pdf | 11 | PDF page count |
| S21070 | 3 | Applied Catalysis B: Environmental | recovered | S21070_mmc1.docx | 32 | Word-stored page count (docProps/app.xml); no layout render available |
| S30334 | 3 | Journal of Catalysis | recovered | S30334_mmc1.pdf | 7 | PDF page count |
| S21253 | 4 | Green Energy and Environment | recovered | S21253_mmc1.docx | 1 | Word-stored page count (docProps/app.xml); no layout render available |
| S22941 | 4 | Electrochimica Acta | not-found | none | | mmc1 absent for 12 extensions on the CDN; lead noted in section 5 |
| S29795 | 4 | Chinese Journal of Chemical Engineering | recovered | S29795_mmc1.docx | 16 | Word-stored page count (docProps/app.xml); no layout render available |

## 3. Recovered packages (details in `recovered_manifest.json`)

| id | pages | route | identity | completeness | caveat |
|---|---|---|---|---|---|
| S22127 | 36 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 5 of 5 Crossref author surnames, first 12 at most (Bu, Lu, Shao, Wang, Zou) | 34 main-referenced SI items, 0 missing; 38 caption labels | Two files: mmc1 and mmc2 have identical paragraph text and identical media members (comparison recorded below); they differ only in Word markup (document.xml, footer, settings, docProps). Treated as one SI whose text is read once. |
| S23544 | 31 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 9 of 9 Crossref author surnames, first 12 at most (Chen, Huang, Li, Wu, Xin, Ye, Yuan, Zhang, Zhao) | 22 main-referenced SI items, 0 missing; 22 caption labels |  |
| S31125 | 8 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=False; 4 of 4 Crossref author surnames, first 12 at most (Qu, Wang, Yang, Yu) | 10 main-referenced SI items, 0 missing; 11 caption labels | The SI's own title ('Molybdenum-mediated electronic modulation of RuO2 for balancing oxygen intermediate adsorption and lattice oxygen participation in acidic oxygen evolution reaction') differs from the published title; identity rests on the exact PII-addressed file, the same four authors (Yuhan Wang, Yihao Qu, Min Yu and Ji Yang, whom the SI prints as 'Yang Ji'), the same sample names (Mo-17-RuO2, Mo-25-RuO2) and the main text's Fig. S1 / Tables S3-S4 matching the SI's own captions. |
| S00882 | n/a | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 4 of 4 Crossref author surnames, first 12 at most (Anton, Exner, Jacob, Over) | 0 main-referenced SI items, 0 missing; 0 caption labels | Binary Word 97-2003 .doc: text and tables read with antiword; the file's one embedded image (the 'Fig. SI' Pourbaix diagram, PNG) is not in the text and needs visual reading. Main text names no numbered SI item; completeness rests on the exact PII-addressed file, its title/authors page, sections a)-f) and the 'Fig. SI' caption. |
| S14386 | 11 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 9 of 9 Crossref author surnames, first 12 at most (Alia, Bell, Danilovic, Fornaciari, Ogitsu, Pham, Weber, Weng, Zhan) | 16 main-referenced SI items, 0 missing; 16 caption labels |  |
| S21070 | 32 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 12 of 12 Crossref author surnames, first 12 at most (Feng, Fu, Long, Luo, Shakouri, Wu, Xiao, Zhang, Zhao, Zhu) | 36 main-referenced SI items, 0 missing; 48 caption labels | Caption-label census contains table-of-contents artefacts (the contents lines run the page number into the label, e.g. 'Figure S38' is Figure S3 on page 8); Figures S1-S34 and Tables S1-S7 are present and no main-referenced item is missing. |
| S30334 | 7 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 4 of 4 Crossref author surnames, first 12 at most (Gupta, Janardhanan, Mekkad, Thalya) | 7 main-referenced SI items, 1 missing; 8 caption labels | The verify script listed 'Section S6' as missing; that is a false hit on the main text's 'Sections 6.6.1 and 6.6.2' (case-insensitive regex), not an SI item. No SI item named by the main text is missing. |
| S21253 | 1 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 7 of 7 Crossref author surnames, first 12 at most (Hu, Jiang, Liu, Zheng, Zhu) | 29 main-referenced SI items, 0 missing; 31 caption labels | Word-stored page count is 1 (docProps), which does not match 29 figure captions and 2 tables; page count not relied on. |
| S29795 | 16 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 6 of 6 Crossref author surnames, first 12 at most (Chen, Wang, Yang, Zhong) | 9 main-referenced SI items, 0 missing; 14 caption labels | Crossref lists 6 authors, OpenAlex 8; all 6 Crossref surnames are in the SI text. |

Identity confirmation by Crossref and OpenAlex (exact DOI): the Crossref title equals the checklist title for 9 records; for S22941 the Crossref title carries MathML markup and the OpenAlex title ('Lattice oxygen evolution in rutile Ru 1-x Ni x O 2 electrocatalysts') equals the checklist title. The Crossref PII equals the checklist PII for all 10; the first Crossref author's surname is in the head of the corpus main text for all 10 (`metadata/<SID>_identity.json`).
Page counts: PDF pages for S14386 and S30334; Word-stored page counts (docProps/app.xml) for the Word files, since no layout render is available; S00882 is a binary Word 97-2003 file whose text and tables were read with antiword, so no page count is claimed. Images inside Word files were counted, not read.

### Ready for two independent blind reads

All 9 recovered packages: S22127, S23544, S31125, S00882, S14386, S21070, S30334, S21253, S29795.
Needs visual reading: S00882 (one embedded image, the Pourbaix diagram 'Fig. SI', outside the text). Figure-heavy Word and PDF files (most of them) have figures as images whose plotted values are not in the text. S22941 is not recovered.

## 4. Gates hit

None in this phase. All 78 CDN requests were answered 200 or 404 with no challenge page. Hosts gated earlier (www.sciencedirect.com, onlinelibrary.wiley.com and the others in `public_si_recovery_2026-10-04/host_gates.json`) were not requested.

## 5. Findings reported, not decided

- **S22941, not recovered.** The main text states: 'Structures and scripts are available in the electronic supplementary material at link: https://nano.ku.dk/english/research/theoretical-electrocatalysis/katladb/loer-runio2/'. That is a public University of Copenhagen page outside the approved Elsevier-CDN route; it was not requested. Whether the article also has an Elsevier-hosted mmc file under another name is not known.
- **S31125.** The SI's title differs from the published title (SI: 'Molybdenum-mediated electronic modulation of RuO2 for balancing oxygen intermediate adsorption and lattice oxygen participation in acidic oxygen evolution reaction'; article: 'Mo-mediated electronic modulation of RuO2 for improved acidic oxygen evolution activity and Ru retention'). Same four authors (the SI prints the last as 'Yang Ji', Crossref has 'Ji Yang'), same sample names, and the main text's Fig. S1 and Tables S3-S4 match the SI's own captions. Identity rests on the exact PII file plus those matches.
- **S22127.** mmc1.docx and mmc2.docx are two different files (different sha256) with identical paragraph text (640 of 640) and byte-identical media members; they differ in Word markup only. One SI, text read once.
- **S00882.** 2013 article; the SI is a binary .doc (sections a-f, with tables of free enthalpies and one figure). Main text names no numbered SI item.
- **S30334.** The completeness script reported 'Section S6' as missing; that is a false hit on 'Sections 6.6.1 and 6.6.2' of the main text. Nothing the main text names is missing.
- **Dates (facts only).** Crossref issue date versus OpenAlex publication date: S22127 2024-04 vs 2024-03-11; S23544 2025-01 vs 2024-08-27; S31125 2026-12 vs 2026-09-04; S00882 2014-02 vs 2013-11-21; S14386 2022-02 vs 2021-12-31; S21070 2024-04 vs 2023-11-27; S30334 2026-09 vs 2026-07-09; S21253 2024-06 vs 2023-12-13; S29795 2026-05 vs 2026-05-01. Existing date reconciliation (`reconcile/date_check.csv`) is not touched here.

## 6. Files

In `results/s2_2026-09-25/full_text/public_si_recovery_2026-10-04_ext/`: `search_log.jsonl`, `recovered_manifest.json`, `readout.md`, `targets.json`, `downloads.jsonl`, `outcomes_logged.json`, `els_run.out`, `metadata/` (Crossref/OpenAlex identity files, verify evidence and extracted SI text; local only), `files/` (downloaded binaries; local only, ignored by git through the `results/` rule), and the scripts used (`si_recovery_lib.py`, `build_targets.py`, `meta_check.py`, `els_cdn.py`, `verify_si.py`, `build_manifest.py`, `relog_final_rows.py`, `write_readout.py`). No existing file was changed.
