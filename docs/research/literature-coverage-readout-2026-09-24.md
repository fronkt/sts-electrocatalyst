# Literature coverage progress — 2026-09-24

**Four additive batches this pass: reference identities, supplement access, open eligibility cases and the title/abstract pre-screen design. Full literature coverage remains open.** Nothing here freezes the candidate or inclusion list. All method-reporting fields remain NOT_CODED, and no P-LIT proportion or verdict is available.

## Backward-reference identities

[`backward_reference_identity/`](../../results/s2_2026-09-23/backward_reference_identity/README.md) links all **529** preserved reference occurrences (217 from the 2026-09-20 pass, 312 from the 2026-09-21 extension) to DOI evidence. No record seeds further expansion.

| Status | Occurrences |
|---|---:|
| Resolved from a printed DOI | 104 |
| Resolved bibliographically (title, first author, year and venue all agree) | 242 |
| Conflict (both sides kept) | 6 |
| Candidate (partial agreement; not resolved) | 168 |
| Unresolved | 9 |

- **Resolved DOIs:** 346 occurrences resolve to 299 distinct DOIs.
- **Already in the provider union:** 61 of those DOIs.
- **New to the union:** 238. These enter screening the same way as the union, as one-generation references that do not seed recursion.
- **Candidates:** mostly citation styles that print no title (Man, Garcia-Mota, Lee). The four-field rule caps these at candidate.
- **Conflicts:**
  - Man [4b]: the printed DOI resolves to a particle-physics paper.
  - Lim u38: the printed DOI resolves to a different JACS article.
  - The other four are year, name-order or journal-name discrepancies.

## Supplement access

[`supplement_access/`](../../results/s2_2026-09-23/supplement_access/README.md) closes the open gaps with verified legitimate copies:

- **Lim 2021:** all five declared supplementary files, from the publisher's figshare. Each is MD5-matched and linked to the article DOI.
- **Lee 2022 SI:** 14 pages. Europe PMC and the PMC open-access store give identical SHA-256.
- **Lee 2022 article:** a publisher-version PDF, CC BY, from the institutional repository. Its 67 references agree word for word with the earlier web transcription once page furniture is removed.
- **Lim supplement references:** none.
- **Lee SI references:** nine, kept as a separate block, not merged into any index.

Wiley's own routes answered 403, so the publisher copy is not byte-compared. All failed attempts are retained.

## Open eligibility cases and complementary identities

[`eligibility_identity_review/`](../../results/s2_2026-09-23/eligibility_identity_review/README.md) covers all **18** study-level cases left unresolved by the earlier reviewed subsets:

- the five from the ten-study subset;
- the twelve from the 29-record joint review;
- one version-linked journal article that had no row of its own.

| Proposed disposition | Cases |
|---|---|
| Eligible pending the discovery freeze | 4: Divanis 2020, Mom 2014, Zheng 2025, Godinez-Salomon 2022 |
| Exclude | 9: five for no CHE overpotential of their own, one anatase not rutile, one purely experimental, one poster record, one with no own OER calculation |
| Unresolved | 5: three articles behind publisher bot checks, one preprint whose SI is unposted, one where the CHE reference is not explicit |

These are **proposed changes from a single review**. Prior records are untouched. The two passes in this batch were made in one sitting and are not independent, so every disposition still needs the registered independent second review before it counts.

- **Institutional access:** four cases (Gauthier 2017, Mom 2014, Kuo 2017, JPCC 3c08103) were read through institutional subscription access. Their retrieved files carry a subscriber watermark and are kept out of the public record.
- **Interpretive flags for the second review:**
  - Exner 2020: whether reusing published RuO2(110) data counts as "calculating OER".
  - Divanis 2020: rutile identity established from the deposited structures, not the text.
  - Mom 2014: plotted points carry no material labels.
- **Complementary identities:** one more key resolves (Dickens → 10.1021/acs.jpcc.7b03481, three occurrences). The other 16 keys stay unresolved, because their source lines give no title, year or venue to match.

## Title/abstract pre-screen of the provider union

[`title_abstract_screen/`](../../results/s2_2026-09-24/title_abstract_screen/README.md) prepares two independent title/abstract passes over all **31,471** provider identities:

- **Inputs:** built offline from the hash-verified raw pages. 28,478 identities have a DOI and 27,280 have an abstract.
- **Record:** a DOI-level record of every screened identity.
- **Merge rule, fixed in advance:** a record is pre-screen excluded only when both passes independently label it clearly irrelevant. Everything else goes to full-text review.

The 200-record pilot, with 7 known-eligible papers hidden in it:

- **Recall:** 7 of 7 routed to full text.
- **Agreement:** 0.955 on exclusion.
- **Routing:** 19% of random records sent to full text, which extrapolates to about 6,000 identities. That full-text stage has not been designed or run.

## What remains

1. The full two-pass pre-screen of the union, plus the 238 new reference-pass DOIs.
2. The full-text stage for the routed records, with a second independent review of every exclusion.
3. The independent second review of the 18 proposed dispositions.
4. The three blocked articles and one missing SI.
5. One-generation references for any newly eligible base paper: Divanis 2020, Mom 2014, Zheng 2025 and Godinez-Salomon 2022, once confirmed.
6. Independent reconciliation before the registered candidate and inclusion freeze.
