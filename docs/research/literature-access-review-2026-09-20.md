# Bounded literature access and eligibility evidence, 2026-09-20

Status: proposals only. This review covers the ten DOI identities already reconciled in [the identity record](../../results/s2_2026-09-19/primary_identity_review/identity_review.json). It does not establish search completeness, freeze the candidate population, adopt inclusion/exclusion decisions, expand references, or code the three reporting questions.

The controlling rule is [P-LIT in the frozen operating decisions](s2-operating-decisions-2026-09-18.md#p-lit-prospective-search-and-coding-choices): primary research first published from 2011-01-01 through 2026-09-18, calculating OER on a rutile-oxide (110) surface and reporting CHE overpotential in the article or SI. Comparative calculations count. Readable article and relevant available methods/SI must be inspected before a negative reporting code; inaccessible components remain unresolved. Every eligibility decision needs a second independent pass before the global freeze.

## Article and supplement bundles

[Access records](../../results/s2_2026-09-20/primary_access_review/access_review.json) preserve titles, authors, original PDF hashes, extracted-text hashes, separate access states, official URLs, version gaps and next actions. [Eligibility proposals](../../results/s2_2026-09-20/primary_access_review/eligibility_proposals.json) preserve page/section evidence separately from method fields, which remain NOT_CODED.

| Study | Verified access in this review | Remaining bundle or version gap |
|---|---|---|
| Man 2011, 10.1002/cctc.201000397 | Local 7-page published article text; publisher SI listing | Wiley SI `cctc_201000397_sm_miscellaneous_information.pdf`, listed as 1.2 MB, not retrieved |
| Inico 2024, 10.1002/cctc.202400813 | Local 11-page published article text; publisher SI listing | Wiley SI `cctc202400813-sup-0001-misc_information.pdf`, 736.1 KB, not retrieved |
| Feng 2025, 10.1016/j.jcat.2025.115968 | Local 10-page published article text; Appendix A declares supplementary material | Supplement file URL and contents unverified |
| Gauthier 2017, 10.1021/acs.jpcc.7b02383 | Local 9-page proof text; institutional publication identity | Final-version equivalence unresolved. No separate SI identified; absence is not established |
| Tripkovic 2018, 10.1021/acs.jpcc.7b07660 | Local 13-page article plus newly retrieved 9-page official SI; title and four authors match | No article/SI access gap identified in this bounded check; no methods audit performed |
| Exner 2020, 10.1021/acscatal.0c03865 | Local 11-page article plus newly retrieved 24-page official SI; title/sole author/resource DOI match | No article/SI access gap identified in this bounded check; primary-study eligibility unresolved |
| Xu 2015, 10.1021/jp511426q | Local 7-page article; publisher SI declaration; author repository metadata | Journal SI not retrieved. Zenodo v1 explicitly predates submission; its equivalence is unproven |
| Divanis 2020, 10.1039/c9sc05897d | Publisher article HTML sections 2.1 and 3 inspected; local 29-page SI; parent visually checked SI p.27 | Article PDF GET failed; article HTML inspection is not a retained PDF or all-page visual check |
| Garcia-Mota 2011, 10.1002/cctc.201100160 | Local 5-page article; publisher SI listing | Wiley SI `cctc_201100160_sm_miscellaneous_information.pdf`, 218.6 KB, not retrieved |
| Mom 2014, 10.1021/jp409373c | Local 3-page SI; its MD5 matches official Figshare metadata | Main article unavailable in this bounded review; institutional records supply metadata only |

The three Wiley landing requests returned HTTP 403 in [initial access receipts](../../results/s2_2026-09-20/primary_download_receipts/initial_access.json), despite publisher metadata/SI listings being visible through web search. No authenticated access, paid purchase or bypass was attempted. The [Tripkovic SI](https://pstorage-acs-6854636.s3.amazonaws.com/10161405/jp7b07660_si_001.pdf) returned HTTP 200 and matches the article. [Official Exner SI item 13100308](https://acs.figshare.com/articles/journal_contribution/13100308) supplies file 25108630, DOI relation and version 1; acquisition is in [secondary receipts](../../results/s2_2026-09-20/primary_download_receipts/secondary_access.json). [Mom SI item 2319313](https://acs.figshare.com/articles/journal_contribution/2319313) supplies file 3956950; parent verified local MD5 `8b1c0a6ee0380410d018e76aefaf7ae3`.

## Eligibility findings awaiting independent review

Four proposals are INCLUDE: Man, Feng, Xu and Garcia-Mota. Tripkovic is proposed EXCLUDE because its own OER calculation family is perovskites, not rutile (110); citing Xu does not satisfy the surface criterion. Five cases remain unresolved:

- Inico uses CHE for stability analysis, but a reported CHE overpotential was not located in the article text/results inspected. Its missing SI could supply it.
- Gauthier contains CHE and an OER free-energy sequence, but a study overpotential was not located in the proof. Computing one from a step energy would not satisfy “reported.” Its final version also remains unverified.
- Exner's label Viewpoint alone is insufficient to exclude it. SI S10 uses MO2(110) and attributes its energies and thermodynamic overpotentials to prior literature; the new descriptor reanalysis needs a consistent primary-research eligibility decision. Applied operating overpotential and Gmax are not substitutes for the registered CHE overpotential.
- Mom's SI and abstract do not replace its unavailable article. Historical project notes about reading the article do not close the current access gap.
- Divanis establishes new TiO2(110) calculations and graphical eta, but the rutile polymorph of this arm is not yet established from inspected primary text. The (110) facet alone is insufficient.

Divanis needs special care: the perspective title and literature compilation coexist with its own one/two-dopant TiO2(110) calculations in [publisher HTML section 2.1](https://pubs.rsc.org/en/content/articlehtml/2020/sc/c9sc05897d). Parent rendered retained SI p.27/S27 and observed Fig. SI-18b's explicit eta_OER arrow above a 1.23 V baseline for a modeled point. This supports a reported graphical overpotential for the new calculation arm. No numeric eta was inferred from the image. Its title therefore does not justify automatic review exclusion. During independent review the initial inclusion proposal was withdrawn: an explicit rutile-polymorph statement for this new arm was not located. Primary structural or textual evidence is still required before inclusion.

Feng's GC-DFT title likewise does not erase its electroneutral CHE comparison: article p.5 section 3.2 presents that arm and the abstract reports thermodynamic overpotentials. These distinctions affect eligibility only, not reporting codes.

## Dates, limits and next actions

Feng article p.1 states online availability on 2025-01-23, supplementing the earlier month-only Crossref print date. [Divanis's publisher record](https://pubs.rsc.org/en/content/articlelanding/2020/sc/c9sc05897d) gives first publication 2020-02-11. Preserve both the detailed 2014-02-11 publisher/Crossref date and the 2014-02-03 header/institution date for Mom. Xu similarly has detailed online 2015-02-20 versus header/author-news 2015-02-09. These discrepancies do not cross the registered date-window boundary. Tripkovic's copyright 2017 is not its online publication date, 2018-01-08.

Complete text extractions were available for all ten original files; eligibility-relevant sections and supporting-material declarations were inspected. This is not a statement that every PDF page was visually checked or that methods were coded. Extraction repaired xref problems in a source file; extracted text alone cannot verify figure content. Parent supplied only the isolated Divanis p.27 visual observation.

Next, retrieve the declared Wiley/Feng/Xu supplements through ordinary publisher or verified author/institution access; obtain Mom's article and Gauthier's final article or establish equivalence; retain Divanis's article HTML/PDF where ordinary access succeeds. A bounded exact-title Figshare query for Xu must be checked against resource DOI and cover identity; unrelated DOI-token search hits must not be accepted. A zero-result Gauthier query does not establish no SI. Then independently resolve eligibility, complete the global discovery/freeze procedure, and only afterward begin method coding. Missing access does not justify a No code, a smaller denominator, or a completeness claim.

## Addendum: Xu supplement access

The earlier Xu SI access gap is superseded by [the additive cover/identity check](../../results/s2_2026-09-20/primary_access_review/xu_si_access_addendum.json). [Official Figshare item 2190043](https://acs.figshare.com/articles/journal_contribution/2190043) identifies DOI 10.1021/jp511426q and file 3824209. The retained 68-page supplement matches its publisher checksum; its cover matches the article title and all three authors. Article and official SI are now available. This closes the SI acquisition gap without assigning a method code or claiming a complete methods inspection. The earlier pre-submission Zenodo resource remains separately versioned.
## Addendum: Wiley dates and direct supplement links

[The additive Wiley observation](../../results/s2_2026-09-20/primary_access_review/wiley_access_date_addendum.json) preserves Inico's publisher **First published: 19 July 2024** alongside Crossref's **online: 12 September 2024** and **print: 11 November 2024**. The publisher date was directly inspected by the parent reviewer; this file-only follow-up did not re-fetch it. Both dates are in-window, so no eligibility outcome changes. Resolve the version/history distinction before selecting a final first-publication date.

One ordinary request to each actually observed Man, Inico and Garcia-Mota publisher supplement link returned HTTP 403, as preserved in the direct-download receipts. These three SI access gaps remain open. No paid access or bypass followed.