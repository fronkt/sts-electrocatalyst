# Unresolved eligibility cases and complementary identities — 2026-09-23

This review covers every unresolved eligibility case in the two reviewed subsets (18 study-level cases) and the 17 unresolved complementary identity keys. It adds records only; every earlier record is unchanged. Where a new disposition differs from an earlier one, it is marked `PROPOSED_CHANGE`. No method-reporting fields were coded. No P-LIT proportion or verdict was computed, and nothing is frozen.

## Case list

`case_list.json` lists the cases:

- 5 UNRESOLVED rows from `reviewed_eligibility_subset.json` (T01–T05).
- 12 UNRESOLVED rows from `priority_primary_triage/reconciled_subset.json` (P01–P12).
- 1 journal representative with no row of its own (V01, 10.1021/acs.jpcc.3c08103). It stands for the IrO2-anion preprint row.

The four Divanis-2021 ChemRxiv alias/preprint rows are grouped under P08. They are not counted as separate studies. `tasks/todo.md` mentions "six unresolved journal eligibility cases", but no file in the repo lists those six, so this review covers all 18.

## Results (`eligibility_records.json`, `summary.json`)

| Final | Cases |
|---|---|
| ELIGIBLE_PENDING_DISCOVERY_FREEZE | T04 Divanis 2020, T05 Mom 2014, P01 Zheng 2025, P07 Godinez-Salomon 2022 |
| EXCLUDE | T01 Inico (no CHE η), T02 Gauthier (no CHE η), T03 Exner (no OER calculation of its own), P03 Kuo (no CHE η; DFT for OH/O only), P05 SnSe2/TiO2 (anatase, not rutile), P09 Creazzo (barriers only, no CHE η), P10 SciMeetings poster (record type), P11 strain RuO2(101) (purely experimental), V01 Navodye JPCC (1.6 V limiting potential cited from Man 2011; no η of its own) |
| UNRESOLVED | P02 (article/SI inaccessible), P04 (SSRN preprint SI not posted), P06 (article inaccessible; SI has no η), P08 (no explicit CHE reference statement), P12 (article inaccessible; SI experimental only) |

Each record holds, for each of the two passes, evidence per criterion with page/section/figure locators. The criteria are: primary research, first-publication date, OER calculated, rutile, (110), and CHE η in the article or SI. Each record also gives the final disposition, the failed criterion or the missing evidence, and whether the two passes agreed. They agreed on all 18 cases.

**Limits on independence.** One reviewer did both passes in the same session. The second pass re-read the primary sources and recorded its evidence before the comparison, but it is not an independent second reviewer in the registered sense.

**Access routes.**
- Open-access HTTP requests are recorded in `receipts.jsonl` and `download_attempts.json`.
- Some open-access pages were read in the browser after scripted requests returned HTTP 403 from bot protection. For these, the SHA-256 was computed in the browser, and the bytes were not kept.
- **T02, T05, P03 and V01 depend on an institutional subscription session.** They were read under institutional subscription access; subscriber-watermarked files stay out of the public record. If this batch should count only open-access routes, those four cases go back to UNRESOLVED.
- Elsevier ScienceDirect pages showed a CAPTCHA. It was not attempted, which leaves P02, P06 and P12 open.

**Rule-application flags for adjudication:**
- T03: "calculating OER" is read as meaning the study's own calculation.
- T04: the rutile polymorph is taken from the authors' deposited katlaDB structure. The in-plane cell is 6.557 × 8.947 Å, which is √2a × 3c for rutile, and the slab has 5c/6c Ti. Only range requests were used; the 3.5 GB archive was not downloaded.
- T05: η is shown graphically for the whole calculated set, and the points are not labelled.
- P07: the explicit ½E_H2 CHE term is on p16.
- P08: the same explicit-reference standard gives UNRESOLVED.

## Identities (`identity_records.json`, `identity_crossref_attempts.json`)

- 17 keys, 34 occurrences. Every occurrence is kept.
- **1 key resolved: Dickens → 10.1021/acs.jpcc.7b03481 (3 occurrences).** Evidence: Crossref `/works`, plus the full text, which contains both cited items (the 0.7 eV defect range on p2 and the Briquet critique on pp8–9). This is a PROPOSED_CHANGE from PARTIALLY_RESOLVED.
- 16 remain UNRESOLVED. Their occurrences give no title, year or venue, so the required agreement is not possible.
- Crossref `query.bibliographic` candidates are recorded but not selected. This includes several OQMD papers. The Nabat DOI was confirmed as a Phys. Rev. D paper, but the occurrence names no work.

## Files

- `scripts/`: `httpfetch.py` (rate-limited GET with receipts), `s01`–`s07` (pipeline), `loc.py` (page locator). Every script passes `ast.parse`.
- `raw/`: Unpaywall, Crossref, OSTI and Europe PMC JSON responses, named by hash prefix.
- `files/`: retrieved articles, SI, bot/403 pages, katlaDB data, and Divanis ERDA range pieces and extracted members.
- `text/`: text extracted from local PDFs, used for inspection only.
- `access_discovery.json`, `repository_lookup.json`, `download_attempts.json`, `receipts.jsonl`, `divanis2020_erda_traj_listing.json`, `manifest.json` (SHA-256 of every file here).
