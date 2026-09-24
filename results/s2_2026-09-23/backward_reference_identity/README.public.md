# Backward-reference identity links — 2026-09-23

This directory links all **529 preserved one-generation reference occurrences** to DOI/provider evidence: the 217 occurrences from the four September 20 base papers (Man, Feng, Xu, Garcia-Mota, plus the Xu SI) and the 312 citation groups from the September 21 extension (Lim, Neto, Dickens, Lee, plus the Neto and Dickens SIs). Every occurrence has exactly one link record. The inputs, the provider union and every earlier artifact are unchanged. These are identity records, not screening: every record stays NOT_SCREENED, and every method-reporting field stays NOT_CODED. No record seeds further reference expansion. Nothing here supports a P-LIT proportion or verdict.

## Outcome

| Status | Occurrences | Meaning |
|---|---:|---|
| RESOLVED_PRINTED_DOI | 104 | The printed DOI resolves at Crossref `/works/{doi}` and agrees with the printed citation on first author, year and journal (and on title where the style prints titles). |
| RESOLVED_BIBLIOGRAPHIC | 242 | No printed DOI. A Crossref `query.bibliographic` item agrees on **title, first author, year and journal**, and its `/works/{doi}` record confirms that agreement. |
| CONFLICT | 6 | The printed DOI resolves, but its record disagrees with the printed citation. Both sides are kept. |
| CANDIDATE | 168 | A bibliographic candidate agrees on at least two of the four fields, but not on all four. **No identity is established.** |
| UNRESOLVED | 9 | Crossref returned 404, or no candidate qualified. This is not an exclusion. |

Resolved occurrences: 346, covering 299 distinct DOIs. By exact DOI against all metadata variants of the [September 22 provider union](../../s2_2026-09-22/identity_handoff/README.md) (31,471 identities, 28,440 distinct DOIs):
- 64 occurrences (61 DOIs) match an OpenAlex identity.
- 238 resolved DOIs are **new to the union** (282 occurrences).

That the union misses most cited works is expected: the union comes from four literal topic queries, and bibliographies cite methods, software and reviews. Being new to the union does not make a work eligible. Separately, 20 CANDIDATE DOIs appear in the union. They are recorded as evidence only.

The candidate classes are:
- **133 `CANDIDATE_TITLE_NOT_PRINTED_OTHER_FIELDS_AGREE`**, almost all from the Man, Garcia-Mota and Lee bibliographies. Their abbreviated style prints no article title, so under the four-field rule they cannot rise above CANDIDATE, even when author, year, journal and volume/page all agree.
- **33 `CANDIDATE_PARTIAL_AGREEMENT`.**
- **2 `CANDIDATE_MATCHED_CORRECTION_OR_ERRATUM_NOTICE`** (Dickens article ref 35 and SI ref 1). Both cite Campbell and Sellers, *Chem. Rev.* 2013, 113, 6902. That page is the Crossref "Correction to …" notice 10.1021/cr4003853, not the review itself. A correction notice is not accepted as a confirmation unless the printed citation names one.

Sixteen resolved records carry non-blocking `review_flags`:
- 7 where the title agrees by word coverage rather than an exact match;
- 5 where the journal agrees only through the letters-only fallback (letter-spaced or broken Lim/Neto text);
- 2 with a partial first-author name match;
- 2 where neither volume nor page agrees.

## Conflicts (kept, not repaired)

- **Man [4b]:** the printed DOI 10.1016/j.physletb.2003.10.071 resolves to a *Physics Letters B* particle-physics paper (Frabetti, 2004) beside a Koper *J. Electroanal. Chem.* 2010 "in press" citation. This is the mismatch the September 20 pass flagged.
- **Garcia-Mota [21]:** 10.1016/j.jelechem.2010.10.004 is Koper's *J. Electroanal. Chem.* paper. The printed year is 2010 ("in press"); the Crossref issue date is 2011-09. This is a year disagreement only.
- **Lim u27:** the printed PBE year is 1997; the Crossref record for 10.1103/PhysRevLett.77.3865 is 1996. The supplementary bibliographic lookup's four-field match is the PRL erratum 10.1103/physrevlett.78.1396, whose title embeds the original citation, not the original article. It is recorded as supplementary evidence only.
- **Lim u28:** the printed first author "Qingxiang, W." is Crossref's "Wang" (given and family names reversed).
- **Lim u38:** the printed DOI 10.1021/jacs.5b07788 resolves to Reier et al., an Ir–Ni oxide paper, while the printed citation is Wang et al., Co-doped FeS2 (J. Am. Chem. Soc. 2015, 137, 1587). The supplementary query confirms 10.1021/ja511572q on all four fields for the printed citation.
- **Neto SI 46:** the printed journal is "J. Condens. Matter Phys."; the Crossref record for 10.1088/1361-648x/aa680e is *J. Phys.: Condens. Matter*.

Each CONFLICT and each failed printed DOI also carries `supplementary_bibliographic_evidence`. That evidence never changes the status.

## Unresolved

- Xu (34), `10.5281/zenodo.12635`, is a DataCite (Zenodo) DOI. Crossref returns 404, as it did in the September 20 complementary review. DataCite was out of scope for this pass.
- Eight citations without a DOI had no qualifying candidate:
  - two web pages (Dacapo; the Umicore product page);
  - the Org-Mode manual;
  - Kittel's textbook;
  - two CRC Handbook sections;
  - a patent;
  - the NIST-JANAF tables.

## Method

[`fetch_link_identities.py`](fetch_link_identities.py) runs the whole pass. It follows the request and receipt style of the complementary identity review.

Network access was limited to Crossref `/works/{doi}` and `/works?query.bibliographic=…&rows=5`:
- User-Agent `…(mailto:<contact-email-redacted>)`, at least 0.35 s between requests (below 5 req/s).
- Up to five attempts, with Retry-After or exponential backoff on 429/5xx/network errors.
- Every error body is saved in `crossref_failures/`.

No OpenAlex endpoint, broad query, reconciliation collector or v2 cursor was called.

Before any request, existing cached `/works` responses were indexed (hash-checked against their receipts). The sources were:
- the September 19 primary review;
- the September 20 complementary review and its supplement;
- the September 20 priority receipts;
- the September 16 f8 cache.

Forty-one DOIs were reused. Their bytes were copied to `crossref_works/`, and each receipt records `cache_source_path`, `cache_receipt_path` and the original retrieval time.

Field agreement is a text comparison against the printed citation:
- **Title:** an exact letters-only substring, or at least 90% word coverage with four or more words.
- **First author:** the Crossref first-author family name appears within the leading 40 letters.
- **Year:** any printed year equals an issued, print, online or published year.
- **Journal:** an in-order abbreviation of the container or short title, with a letters-only fallback for letter-spaced text.
- **Volume and first page/article number:** recorded as supporting evidence only.

A CONFLICT is a recorded disagreement for review. It is not a finding that a DOI is wrong.

## Files

- `reference_identity_links.jsonl` — one record per occurrence. Each record keeps the parent DOI, document, reference number/letter/ordinal, locators, `discovery_generation` = 1, `seeds_further_expansion` = false, the verbatim and normalized printed citation, and the printed DOI. Its `resolution` holds the Crossref metadata (title, authors, journal, type, identifiers, online/print/issued dates, relations, update notices), per-field agreement, receipts (path, sha256, HTTP status, timestamp), evaluated bibliographic items with scores, and the OpenAlex union match.
- `summary.json` — all counts, status definitions, the conflict list, the new-to-union DOIs and limits.
- `request_receipts.jsonl` — an append-only request log: 731 request keys, 692 HTTP attempts, 41 cache reuses. The final statuses are 689 HTTP 200, 41 CACHE_REUSED and 1 HTTP 404 (the Zenodo DOI, attempted once in each of three runs; every 404 body is kept).
- `crossref_works/` (305), `crossref_bibliographic/` (425), `crossref_failures/` (3) — the raw responses.
- `input_hashes_before.json`, `self_check.py`, `self_check.json` — the self-check has no network access. It recounts every summary number from the link records and receipts, re-hashes every saved response and failure body, confirms that cached bytes equal their sources and that every input occurrence is linked once with unchanged printed fields, re-derives the union matches, and confirms the input hashes. Result: **44/44 checks pass**.
- `run_log_run1.txt`, `run_log_run3.txt`, `summary_run1_superseded.json` — console logs and the superseded first summary. Run 1 made all the network requests. Before run 2, an erratum/correction guard and review flags were added. Runs 2 and 3 reused every saved response; the only new requests were the Zenodo 404 retries. Run 3 renamed one summary key. Run 2's console log was discarded, but its request is in the receipts.

The input sha256 values are unchanged before and after the pass:
- September 20 occurrences: `be7fde04…993867`.
- September 21 occurrences: `8a16a621…8388e5`.

The provider union's hash is recorded in `input_hashes_before.json`.

## Limits

- Only Crossref was consulted.
- Title-less citation styles cap bibliographic resolution at CANDIDATE.
- The automated agreement tests can miss abbreviations and garbled text. The flags and per-field evidence are there for review.
- Lim's five and Lee's supplementary files are still inaccessible, so their references are absent.
- Deduplication into studies, primary eligibility review and the candidate/inclusion freeze remain open.

## Note — 2026-09-24

The limits above that call Lim's five supplemental files and the Lee supplement inaccessible are superseded by `../supplement_access/`, which closes both with verified copies (neither supplement adds references to this index: Lim's contain none; Lee's SI prints nine, kept as a separate block). `summary.json` is left as recorded. Independent review: `../independent_review_2026-09-24.json` (PASS_WITH_FINDINGS; no data defects).
