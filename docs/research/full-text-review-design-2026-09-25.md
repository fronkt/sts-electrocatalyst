# Full-text review design — 2026-09-25

**Status:** design, not run. It covers the 5,586 records that the title/abstract pre-screen routed to full text (`results/s2_2026-09-24/title_abstract_screen/passes/merge/`). Frank approved the pre-screen safety net on 2026-09-25. Nothing in this stage codes a method field, computes a P-LIT proportion, or gives a verdict.

## 1. Fixed rules this stage must follow

Sources: `s2-operating-decisions-2026-09-18.md` (OPS), the retrieval amendment (AMD), and the 2026-09-20 gap audit, access review and second-review records.

- **Population (OPS:68).** Primary research articles, first published 2011-01-01 through 2026-09-18, that calculate OER on a rutile-oxide (110) surface and report a CHE overpotential in the article or SI.
  - Comparative studies are included whatever the authors call them.
  - A preprint and its journal article count once. Both dates are preserved.
- **What counts as reported.**
  - A numeric or explicitly graphical η counts.
  - η derived by us from ΔG values does not count, and neither do instructions for calculating η.
  - An applied operating overpotential or Gmax is not a substitute.
  - The rutile polymorph must be established. A (110) facet alone is not enough.
- **Metadata cannot decide.** Article type, date or a title match alone does not establish eligibility (gap audit:11). A missing "(110)" or "CHE" in the abstract is not grounds to exclude (gap audit:38).
- **Second review (OPS:91; gap audit:38).** A second independent pass reviews every included row and every exclusion. Discrepancies are resolved against the primary source.
- **No early coding (gap audit:36).** Reading methods or SI to decide eligibility does not permit recording the four method fields. None are recorded in this stage.
- **Inaccessible papers.** Missing access never becomes an exclusion or a smaller denominator. It stays UNRESOLVED_ACCESS (access review:46; AMD:22).
- **Freeze before coding (OPS:81).** The deduplicated candidate and inclusion/exclusion list is frozen before coding, with reasons and unresolved-access entries.
- **Coding is Frank's (43:1906).** The entrant codes every included paper from the paper itself. A suggested code is never the recorded value.
- **Deadline.** P-LIT that has not landed by **2026-10-15** becomes WITHDRAWN-UNSCORED (43:1437; 45:84).

## 2. What the routed set looks like

| | Count |
|---|---:|
| Routed records | 5,586 (4,604 by rule, 982 by the safety net) |
| Signal: at least one LIKELY_RELEVANT | 604 |
| Signal: POSSIBLY_RELEVANT in both passes | 2,668 |
| Signal: pass disagreement | 1,332 |
| Signal: safety net only | 982 |
| OpenAlex type: article | 3,986 |
| OpenAlex type: conference abstract | 532 |
| OpenAlex type: preprint | 412 |
| OpenAlex type: dissertation | 329 |
| OpenAlex type: other | 327 |
| Open-access status: not closed | 3,444 |
| Open-access status: closed | 2,031 |
| Open-access status: reference-pass records with OA status not looked up | 111 |
| With an OpenAlex OA PDF link | 2,725 |
| Dated before 2011 by OpenAlex | 24 |

## 3. Stages

**FT0 — version linking (deterministic, no exclusion).**
- Link preprint to article, and conference abstract or dissertation chapter to article, using DOI relations, OpenAlex relations and a normalized title plus first-author match.
- A linked group is read once, through its most complete version. All member IDs and both dates are kept.
- Records dated before the window are carried as `DATE_CHECK`. They are not dropped, because the rule counts from first publication and provider dates can be wrong.

**FT1 — retrieval with a per-record access log.** Routes are tried in this order, and every attempt is logged (URL, status, bytes, SHA-256, content type):

1. OpenAlex OA locations. These are already in the hashed raw pages.
2. Preprint servers: arXiv and ChemRxiv.
3. Free publisher HTML full text.
4. Institutional subscription access through Frank's browser session. This is the legitimate route for closed papers, but it is slow and interactive.
5. Nothing else unless Frank decides otherwise (**D1**).

Retrieved files stay local and are never committed; the repository is public. The log and hashes are committed. SI is fetched **only on demand**, when the main text cannot settle whether a CHE overpotential is reported. Anything not retrieved stays UNRESOLVED_ACCESS.

**FT2 — eligibility pass 1.**
- **Screener:** reads the extracted full text: all of the main text, with references removed and figure captions kept.
- **Output:** one row per record with six criteria, each with a verdict and a page/section plus short verbatim excerpt:
  - E1 primary research;
  - E2 first publication in the window;
  - E3 OER computed by the authors;
  - E4 rutile polymorph established;
  - E5 a (110) surface calculated;
  - E6 CHE overpotential reported (numeric or explicit graphical).
- **Disposition:** `ELIGIBLE`, `EXCLUDE:<first failing criterion>`, `NEEDS_SI`, or `UNRESOLVED`.
- **Excluded from this pass:** screeners are told not to record symmetry, imaginary-mode, magnetism or deposition content. The output schema has no fields for them.

**FT3 — eligibility pass 2 (independent).**
- A different screener reads every record, not only the exclusions, because OPS:91 requires review of every included row and every exclusion.
- Pass 2 uses a different batching, does not see pass 1, and has the same schema.

**FT4 — reconciliation.**
- Every disagreement, every `NEEDS_SI` and every `UNRESOLVED` is resolved against the source by a third read. The third read records which excerpts decided the case.
- Interpretive cases go to Frank as a short list. These are the Exner-type "reused published data" cases and graphical-η borderline cases.

**FT5 — freeze and deposit.**
- The frozen list covers every record: disposition, deciding criterion and excerpt, version links, access routes, and the UNRESOLVED_ACCESS entries.
- It is committed and deposited with restricted access before any coding, as the P-LIT preregistration was.

**FT6 — coding (Frank).** A coding sheet shows each included paper's link and files. Frank records the four fields with page/excerpt, coder and date. Tooling for this is built after the freeze, when the inclusion count is known.

## 4. Capacity and timeline

- **Measured so far:** pre-screen screeners read about 200 short records in 6–10 minutes (about 220k tokens each), 20 at a time.
- **Full-text estimate:** a paper's main text is roughly 8–15k tokens, so about 8 papers fit per screener run.
- **Runs:** two passes over about 5,500 records come to about 1,400 runs. At 20 concurrent, that is about 10 hours of screening per pass, plus usage-limit pauses. The pre-screen hit one limit after about 250 runs.
- **Retrieval:** the open-access routes are fast. Institutional retrieval of about 2,000 closed papers through a browser is the slow step, roughly 1–2 minutes per paper.
- **Coding:** Frank's coding time scales with the inclusion count, which is not known yet. The pilot below estimates it.
- **Order:** the plan runs the 604 records with a LIKELY_RELEVANT label first, so eligibility for the likeliest papers is settled early, and ends with a hard stop for the freeze well before 10-15.

## 5. Decisions for Frank

- **D1 — access beyond institutional.**
  - The registered access record says no bypass was attempted, and it lists only ordinary, author/institution and institutional-subscription routes. Frank separately permitted Sci-Hub for STS literature on 2026-09-21.
  - Using it here would contradict the method statement already on record, so it would need a dated amendment.
  - **Recommendation:** do not use it. Leave what open-access and institutional routes cannot reach as UNRESOLVED_ACCESS, which the bounds already absorb.
- **D2 — who does the eligibility reading.**
  - Registered text reserves only the method-field coding for Frank. Earlier eligibility reviews were made by assisted sessions and labelled as single or independent reviews.
  - **Proposal:** FT2 and FT3 use independent in-session screeners reading the full text, as the pre-screen did. Frank decides the FT4 interpretive cases.
- **D3 — non-article forms.**
  - OPS limits the population to primary research *articles*. The routed set has 532 conference abstracts, 329 dissertations and 74 conference papers.
  - **Proposal:** these stay candidates only through FT0 version links. A form with no linked article is excluded under E1, and that exclusion gets the same second review.
- **D4 — institutional retrieval time.** How much browser time Frank can give to closed papers before 10-15, or whether the Purdue route can run in his logged-in Chrome session.

## 6. Retrieval pilot result, 2026-09-25 (`results/s2_2026-09-25/full_text_pilot/`)

**Sample.** 100 routed records, 25 per signal stratum (seed 20260925), plus the 7 sentinels. Only open-access routes were tried: direct HTTP GET of every OpenAlex OA PDF location.

**Retrieved: 24 / 107 (22%).**

| Stratum | Retrieved |
|---|---:|
| any_LIKELY | 2 / 25 |
| both_POSSIBLY | 6 / 25 |
| split | 12 / 25 |
| rescue | 3 / 25 |
| sentinels | 1 / 7 |

**Why the rest failed.**
- 47 records have no OA PDF location in OpenAlex.
- Publisher hosts answered 403 bot blocks: Wiley 10, MDPI 5, ACS 4, ScienceDirect 3, RSC 2, AIP 1, Science 1, ChemRxiv 1. MDPI and ChemRxiv refused even their open-access copies.
- PMC and IOP returned HTML challenge pages instead of PDFs.

**Text size.** The median extracted text is about 50k characters (about 12k tokens); the 90th percentile is about 126k (about 30k tokens).

**Consequence.** Plain HTTP retrieval cannot supply the full text, least of all for the likeliest records. Those sit mostly in ACS, Elsevier, Wiley and RSC journals. A workable pipeline needs:

- **(a) Browser retrieval.** Frank's logged-in Chrome with institutional access handles both the bot-blocked open-access copies and the closed papers. It is the legitimate route and the slow one.
- **(b) Other legitimate APIs.**
  - Europe PMC full-text XML for PMC items.
  - Unpaywall repository copies. The Unpaywall API needs a contact email, which is Frank's call to provide.
  - arXiv and ChemRxiv by title.
  - Elsevier and Wiley text-mining APIs. These need institutional tokens.
- **(c) D1.**

Retrieval, not screening, sets the pace of this stage.

## 7. Pilot before scaling

This is a random sample of 100 routed records, seeded and stratified by pre-screen signal. It measures:

- the open-access retrieval rate by route;
- extracted text size;
- the FT2 rate of eligible, needs-SI and unresolved outcomes;
- FT2/FT3 agreement on the sample.

It also includes the known-eligible sentinels to check recall at full text. The pilot uses only open-access routes until D1 and D4 are answered.
