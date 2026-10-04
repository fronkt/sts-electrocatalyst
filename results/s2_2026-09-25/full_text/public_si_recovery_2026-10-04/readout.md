# Public SI recovery round, 2026-10-04 (retrieval only)

No screening or eligibility decision is made here. Packages listed below are ready for two independent blind reads; whether to run them is the coordinator's call.

## 1. Target list and how it was derived

- `si_checklist.csv` (144 rows, unchanged since 2026-10-03: tiers 60/31/47/6) cross-checked against `reconcile/current_state.csv`: all 60 tier-1 rows are still NEEDS_SI (56) or ELIGIBLE with an open SI question (4: S29721, S10090, S22807, S26024).
- Priority inside tier 1 (checklist order breaks ties): (0) the 4 ELIGIBLE records, (1) records whose deciding rows name specific SI items, (2) D10 checks, (3) the rest. See `build_targets.py`, `targets.json`.
- Six handoff dead ends were not re-searched (S11392 journal lead, S13316, S14704 and S11549 repository copies, S23244, S22690). Two of them were then touched by routes the handoff had not covered, as noted below (S14704 via the Elsevier asset CDN; S11392 via its own preprint page).
- Processed in priority order: **40 records** (cap reached). Not reached (14, all Wiley except S26744 RSC): S26744, S08129, S19847, S20851, S21358, S22122, S22135, S23889, S24603, S24787, S24921, S25750, S25769, S29894.
- Prior routes were skipped, not repeated: Unpaywall DOI lookups, figshare exact-DOI, Europe PMC OA checks, earlier publisher-page blocks (si_public_log.jsonl and the 2026-10-01/02/03 route files).

## 2. Outcomes

Final outcome per processed record (best outcome over all routes): **recovered 12, main-only 5, no-SI-evidence 1, gated 22, wrong-version 0, not-found 0** (total 40).

Dead ends: S14704 recovered (new route), S11392 recovered (preprint-version SI, new route), S13316 and S11549 main-only as already known, S23244 and S22690 not re-searched.

Route-level rows in `search_log.jsonl`: 722 total (recovered 17, main-only 12, no-SI-evidence 1, gated 37, not-found 655).
Most `not-found` rows are API checks per record (Crossref, OpenAlex locations, Europe PMC DOI and title, DataCite related-identifier and title, Zenodo DOI and title, OpenAIRE, arXiv, Crossref preprints, OpenAlex title, figshare title, NOMAD). A not-found is never evidence that no SI exists.

| rank | id | publisher | final | note |
|---|---|---|---|---|
| 1 | S29721 | ACS | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 2 | S10090 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 3 | S22807 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 4 | S26024 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 5 | S23135 | Elsevier | recovered | elsevier, 24 pages |
| 6 | S31137 | Elsevier | recovered | elsevier, 34 pages |
| 7 | S05155 | RSC | main-only | OSTI, DTU Orbit and Imperial Spiral copies are accepted manuscripts (OSTI copy is byte-identical to the local main file); MIT DSpace refused (HTTP 405); RSC pages 403 |
| 8 | S21177 | Research Square | recovered | researchsquare, 60 pages |
| 9 | S30575 | Research Square | recovered | researchsquare, 41 pages |
| 10 | S18606 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 11 | S18904 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 12 | S19097 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 13 | S21048 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 14 | S21131 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 15 | S21441 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 16 | S23402 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 17 | S23565 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 18 | S24489 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 19 | S26703 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 20 | S26740 | Wiley | main-only | PSI DORA manuscript (23 pp) cites Figure S1-S23 but has no SI pages; Wiley gated |
| 21 | S27901 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 22 | S29976 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 23 | S30943 | Wiley | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 24 | S04318 | ACS | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 25 | S03607 | Pleiades | no-SI-evidence | Springer Nature Link page loaded, shows no supplementary section (D10 evidence, not a decision) |
| 26 | S00759 | ACS | main-only | Radboud and Groningen copies are the 6-page article only; ACS gated |
| 27 | S01354 | ACS | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 28 | S08806 | ACS | main-only | EPFL author manuscript (27 pp) is main only; Materials Cloud holds a data deposit (IsSupplementTo the article), no SI PDF; ACS gated |
| 29 | S08766 | ECS | main-only | NLR/OSTI copies are the 10-page JES article only; IOP bot-captcha |
| 30 | S00358 | Elsevier | recovered | elsevier, 13 pages |
| 31 | S00887 | Elsevier | recovered | elsevier, 2 pages |
| 32 | S05043 | Elsevier | recovered | elsevier, 3 pages |
| 33 | S11279 | Elsevier | recovered | elsevier, 12 pages |
| 34 | S20599 | Elsevier | recovered | elsevier, 11 pages |
| 35 | S23308 | Elsevier | recovered | elsevier, 1 pages |
| 36 | S27476 | Elsevier | recovered | elsevier, 40 pages |
| 37 | S31037 | Elsevier | recovered | elsevier, 31 pages |
| 38 | S01251 | RSC | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 39 | S01836 | RSC | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |
| 40 | S23927 | RSC | gated | publisher host blocked this phase; no repository, preprint or dataset copy found |

## 3. Recovered packages (details in `recovered_manifest.json`)

| id | pages | route | identity | completeness | caveat |
|---|---|---|---|---|---|
| S21177 | 60 | researchsquare_public_preprint_page_file_list | title in SI text=True; 7 of 7 Crossref author surnames, first 12 at most | 38 main-referenced SI items, 0 missing; 43 caption labels |  |
| S30575 | 41 | researchsquare_public_preprint_page_file_list | title in SI text=True; 9 of 9 Crossref author surnames, first 12 at most | 55 main-referenced SI items, 0 missing; 64 caption labels | Movies S1-S3 are non-text media of the same package. The source's Supplementary Fig. S3 caption lacks its 'S3' label (text '3D AFM...' neighbours S2/S4); content is present. |
| S11392 | 25 | researchsquare_public_preprint_page_file_list | title in SI text=True; 12 of 12 Crossref author surnames, first 12 at most | 9 main-referenced SI items, 0 missing; 9 caption labels | PREPRINT-version SI (Fig. S1-S7, Table S1-S2, 25 pages). The journal version S13010 (JACS 10.1021/jacs.1c01655) has a different, already-read SI (17 pages, Fig. S1-S10). Handoff dead end concerned the journal lead; whether this preprint SI needs reads is for the coordinator. |
| S23135 | 24 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 7 of 7 Crossref author surnames, first 12 at most | 15 main-referenced SI items, 0 missing; 22 caption labels |  |
| S31137 | 34 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 2 of 2 Crossref author surnames, first 12 at most | 29 main-referenced SI items, 0 missing; 30 caption labels |  |
| S00358 | 13 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 3 of 3 Crossref author surnames, first 12 at most | 0 main-referenced SI items, 0 missing; 0 caption labels | Main text names no specific SI item; completeness is by the exact PII-addressed file plus the SI's own title page and 'Tables 1-3' content. |
| S00887 | 2 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 3 of 3 Crossref author surnames, first 12 at most | 2 main-referenced SI items, 0 missing; 2 caption labels |  |
| S05043 | 3 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 12 of 12 Crossref author surnames, first 12 at most | 5 main-referenced SI items, 0 missing; 5 caption labels |  |
| S11279 | 12 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 5 of 5 Crossref author surnames, first 12 at most | 12 main-referenced SI items, 0 missing; 14 caption labels |  |
| S20599 | 11 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 9 of 9 Crossref author surnames, first 12 at most | 5 main-referenced SI items, 0 missing; 8 caption labels |  |
| S23308 | 1 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=False; 0 of 2 Crossref author surnames, first 12 at most | 0 main-referenced SI items, 0 missing; 0 caption labels | One-page SI whose only content is 'Table 1 - ZPE and TS corrections' as an EMF image; no title/authors inside, so identity rests on the PII-addressed file name; table values are only in the image (needs visual reading). |
| S27476 | 40 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 7 of 7 Crossref author surnames, first 12 at most | 15 main-referenced SI items, 0 missing; 28 caption labels |  |
| S31037 | 31 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 7 of 7 Crossref author surnames, first 12 at most | 25 main-referenced SI items, 0 missing; 27 caption labels |  |
| S14704 | 6 | elsevier_article_asset_cdn_PII_addressed_mmc | title in SI text=True; 5 of 5 Crossref author surnames, first 12 at most | 9 main-referenced SI items, 0 missing; 9 caption labels | Handoff dead end (repository copies were main-only); recovered by a different route. |

Page counts: PDF pages for S00358 and S11279; Word-stored page counts (docProps/app.xml) for the Word files, since no layout render is available. Images inside Word files were counted, not read.

### Ready for two independent blind reads

All 14 packages in the manifest: S21177, S30575, S11392, S23135, S31137, S00358, S00887, S05043, S11279, S20599, S23308, S27476, S31037, S14704.
Needs a coordinator note first: **S11392** (preprint-version SI; the journal version S13010 already has complete SI reads and a different SI document). Needs visual reading: **S23308** (one table, supplied as an image). The four ELIGIBLE-question records (S29721, S10090, S22807, S26024) are not recovered: all are Wiley or ACS, both gated.

## 4. Gates hit

| host (family) | first block | evidence |
|---|---|---|
| pubs.acs.org | 2026-10-04T09:31:25Z | HTTP 403 to WebFetch on the ACS article page (S29721) |
| pmc.ncbi.nlm.nih.gov | 2026-10-04T09:39:36Z | HTTP 200 body was a Google reCAPTCHA challenge page (S29976); not read |
| dspace.mit.edu | 2026-10-04T09:40:42Z | HTTP 405 on the bitstream URL (S05155) |
| commons.case.edu | 2026-10-04T09:43:53Z | HTTP 403 on the repository file URL (S05043) |
| scholars.cityu.edu.hk | 2026-10-04T09:43:53Z | HTTP 403 on the repository file URL (S27476) |
| onlinelibrary.wiley.com | 2026-10-04T09:45:30Z | HTTP 403 to WebFetch on the Wiley article page (S10090); all *.wiley.com treated as blocked |
| www.sciencedirect.com | 2026-10-04T09:45:30Z | HTTP 403 to WebFetch on the ScienceDirect article page (S23308) |
| biblio.vub.ac.be | 2026-10-04T09:45:30Z | HTTP 200 body was a 246-byte 'Request Rejected' WAF page instead of the PDF (S23308) |
| espace.library.uq.edu.au | 2026-10-04T09:46:31Z | HTTP 403 on the UQ eSpace record (S21441) |
| papers.ssrn.com | 2026-10-04T09:47:22Z | HTTP 403 Cloudflare 'Just a moment' challenge (S27476) |
| iopscience.iop.org | 2026-10-04T09:47:46Z | HTTP 200 body was a Radware Bot Manager captcha page, redirect to validate.perfdrive.com (S08766) |
| pubs.rsc.org | 2026-10-04T09:45:30Z | HTTP 403 to WebFetch on the RSC article landing page (S05155) |

After each first block the host was not requested again. No challenge was solved or bypassed, no browser, proxy, Purdue/EZproxy, keyed API or shadow library was used, and no paid API was called. The OpenAlex key was read at request time, never printed; a scan of every file in this phase finds no copy of it.

**Sci-Hub:** the 2026-10-04 coordinator message allowed Sci-Hub as a last resort. One request was attempted (S10090, three mirrors in one call) and the Claude Code permission classifier DENIED the tool call before anything was sent; a following benign local read was also denied. I did not retry through another tool, host or interpreter. Sci-Hub is therefore untried for all records (one `scihub` row is logged). A user-side Bash permission rule would be needed. Note it would mostly return main articles, which do not count as SI.

## 5. Judgement calls worth a look

1. **Elsevier asset CDN (ars.els-cdn.com).** After www.sciencedirect.com answered 403 to WebFetch, I fetched the exact file URL behind each article's 'Appendix A. Supplementary data' link (`1-s2.0-<PII>-mmc1.<ext>`, PII from Crossref) by plain GET with an honest User-Agent: no key, no login, no API, no challenge page seen. It returned the SI for 11 of 11 tier-1 Elsevier records. This is a different host from the page that blocked me, but the same publisher; if you read the 'record the block and move on' rule at publisher level, drop the 11 Elsevier packages. The Crossref `link` fields of these records point at api.elsevier.com text-mining URLs; those were NOT used.
2. **Research Square.** Plain HTTP GET of the public preprint pages; the page's embedded file list names the supplement. The earlier NO_SI_LINK_ON_PAGE logs for S21177 and S11392 were false negatives (the link is in the page data, not in visible link text).
3. **RSC direct SI URL** (`www.rsc.org/suppdata/...`) answered 404 for three records (path no longer valid); not a gate.
4. WebSearch is unreliable for this: one query returned another paper's SI (acscatal.2c01944) as if it belonged to S29721; it was rejected.

## 6. Findings reported, not decided

- **D10.** S21177 and S11392 (both D10-flagged): the preprint pages list supplement files (S21177 SupportingInformation.docx, 49,126,359 bytes; S11392 VelascoVelezetal.NatureEnergySI2020.docx, 2,605,142 bytes), so SI exists and is now in hand. S03607 (D10-flagged): the official Springer Nature Link page loads and has no supplementary section (sections: Abstract, References, Author information, Additional information, Rights and permissions, About this article; saved as `metadata/S03607_page_springer.html`). S04318 and S11549 (D10-flagged): not re-checked, ACS and IOP gated. Because the old page-text check missed supplements stored in page data, other NO_SI_LINK_ON_PAGE results for JavaScript-built pages deserve a recheck.
- **Version linkage S11392 / S13010** (`metadata/S11392_S13010_linkage.json`): Crossref `relation` is empty for both; OpenAlex lists no link; Europe PMC has the preprint as PPR253311 and the journal article as PMC8397309 (hasSuppl=Y); Research Square page has no version-of-record link. Both author lists share the same surnames (17 vs 18 authors) and titles differ ('...Water Splitting' vs '...Water Oxidation'). The two SI documents differ (preprint: 25 pp, Fig. S1-S7, Table S1-S2; journal: 17 pp, Fig. S1-S10, Table S1-S2). No authoritative link was found.
- **Dates.** S31137 and S31037 keep the existing SOURCES_STRADDLE_BOUNDARY flag. New Crossref facts: DOIs created 2026-09-04 and 2026-09-02, deposited 2026-10-03 and 2026-10-01, issue date 2026-11, license start 2026-11-01; OpenAlex publication dates 2026-09-04 and 2026-09-02.
- **Identity (editions).** Six Angewandte targets (S26024, S21048, S21441, S23402, S26703, S29976) have both an `anie` and an `ange` DOI in Crossref with identical author lists and dates. The corpus already collapses three counterparts (S21049, S21444, S23404); counterparts of S26024, S26703 and S29976 are not in the corpus. Both editions share one SI.

## 7. Leads that need a human or a new permission

- **S29976:** Europe PMC lists PMC13427193 (author manuscript, hasSuppl=Y, not OA). PMC served a reCAPTCHA page. A manual look at the PMC record's supplementary-material list is the cheapest next step.
- **S08806:** Materials Cloud datasets (10.24435/materialscloud:sr-bh, :2019.0038 v1/v2) are IsSupplementTo the article: computation inputs and outputs, no SI PDF.
- **S27476:** an SSRN preprint with the same title exists (10.2139/ssrn.5462162, Cloudflare challenge); moot now that its SI is recovered.
- **S21441:** UQ eSpace (403) and Griffith (script-built page) hold the International-Edition record; not readable without a browser.
- **Wiley and ACS/RSC/IOP records** need manual downloads of the checklist file names (`si_checklist.csv`, column `file`) or a decision on Sci-Hub: 27 processed records without SI (22 gated, 5 with only main-article copies) plus 14 not reached.
- **Same Elsevier route, outside tier 1:** 10 more Elsevier checklist records (S22127, S23544, S31125, S00882, S14386, S21070, S30334, S21253, S22941, S29795). I stopped at the tier-1 cap; say go if you accept judgement call 1.

## 8. Files

In `results/s2_2026-09-25/full_text/public_si_recovery_2026-10-04/`: `search_log.jsonl`, `recovered_manifest.json`, `readout.md`, `targets.json`, `downloads.jsonl`, `host_gates.json`, `metadata/` (API responses, page captures, verify evidence and extracted SI text; local only), `files/` (downloaded binaries; local only, ignored by git through the `results/` rule), and the scripts used (`si_recovery_lib.py`, `build_targets.py`, `metadata_sweep.py`, `rs_files.py`, `els_cdn.py`, `probe_urls.py`, `verify_si.py`, `verify_summary.py`, `preprint_search.py`, `extra_repos.py`, `date_identity_probe.py`, `linkage_s11392.py`, `epmc_supp.py`, `dl.py`, `logrow.py`, `log_outcomes.py`, `log_skipped_gates.py`, `build_manifest.py`, `summarize_log.py`, `write_readout.py`, `analyze_sweep.py`, `inspect_pdf.py`). Nothing was staged or committed; no existing file was changed.
