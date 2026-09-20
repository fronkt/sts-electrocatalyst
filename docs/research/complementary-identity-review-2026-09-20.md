# Complementary literature identity review — 2026-09-20

The registered complementary inventory now has an additive identity review for all **120 keys and 271 citation occurrences**. **103 keys, covering 237 occurrences, resolve to 81 distinct canonical identities.** The other **17 keys and 34 occurrences** remain explicit. These counts do not establish how many papers meet P-LIT inclusion criteria.

The review follows the identity and version rules in [the S2 operating specification](s2-operating-decisions-2026-09-18.md) and [the retrieval amendment](s2-literature-retrieval-amendment-2026-09-18.md). Its scope is the existing Divanis ESI reference list, both August 15 syntheses and the already registered Xu/Man identities. Primary publisher, arXiv and repository pages supply exact identity evidence; DOI-specific Crossref requests validate the bibliography. No OpenAlex calls, broad bibliographic query arm, recursive reference traversal, eligibility decisions or method coding occurred.

All original discovery records remain unchanged. The additive records are in [the identity-review directory](../../results/s2_2026-09-20/complementary_identity_review/README.md). Each original occurrence retains its source path, source hash, line/reference location and original occurrence-file hash. The complete canonical title and ordered author metadata live in `bibliographic_records.jsonl`; aliases and ambiguities live in `identity_links.jsonl`.

| Identity disposition | Keys | Meaning |
| --- | ---: | --- |
| Literal DOI or arXiv identifier resolved | 56 | All 46 DOI keys and 10 arXiv keys have primary identity metadata. |
| Divanis bibliography resolved | 25 | All references 1–25 match author/journal/year/volume/pages or distinctive article identifier. |
| Named study lead resolved | 16 | Named context is linked to the checked study identity; scientific assertions remain unverified. |
| Exact repository/documentation resource resolved | 6 | Six source keys reach five separate resource identities. |
| Partly resolved | 1 | Dickens has a verified defect-site candidate but a conflated attribution remains unjoined. |
| Unresolved | 16 | Insufficient exact work or version identity. |

The raw metadata accounting comprises 72 successful or reused Crossref records from 73 DOI requests, plus the official DataCite record for the Zenodo dataset. Ten Crossref replies reuse the prior hash-verified primary review. The single Crossref 404 for [Zenodo DOI 10.5281/zenodo.12635](https://zenodo.org/records/12635) is retained: the [official DataCite record](https://api.datacite.org/dois/10.5281/zenodo.12635) identifies the DOI as a dataset. The dataset, its GitHub repository and the Xu journal article remain distinct resources connected by supporting-data relationships.

All 25 Divanis references resolve, but several source defects matter for subsequent citation work:

| Reference | Correction or retained distinction |
| --- | --- |
| 5 | The raw author string ends at “M. T. M.”; the complete primary list identifies Marc T. M. Koper. Crossref supplies start page 1245, while the RSC page gives 1245–1249. [RSC record](https://pubs.rsc.org/en/content/articlelanding/2013/sc/c2sc21601a). |
| 7 | The published title and deposited metadata spell “Infuence.” Preserve the published identity; do not silently correct the record. The prior primary review retains the ACS date discrepancy. |
| 9 | The cited 2015 year is the issue year; Crossref records online publication on November 6, 2014. Both fields remain. |
| 11 | `ncomms9253` is the DOI suffix, while the article number is 8253. The full eight-author list matches. [Nature record](https://www.nature.com/articles/ncomms9253). |
| 12 | `6283` is the Science issue, not a page number. The complete 25-author tuple identifies volume 352, issue 6283, pages 333–337. |
| 17 | The primary author's publication list points to a later correction, DOI 10.1021/acscatal.8b01775. This remains a bibliographic warning for article review, not another discovery candidate in this pass. [Carter publication list](https://carter.princeton.edu/wp-content/uploads/2025/07/2025-06-30-EAC_CV-Website.pdf). |
| 23 | Two Qian Zhang authors remain separate, with the deposited (m)/(f) disambiguators retained. |
| 24 | The citation uses the 2019 issue year; the article reports online availability on February 19, 2018, while Crossref has only the February 2019 print date. [Primary article](https://pure.tue.nl/ws/portalfiles/portal/116894860/1_s2.0_S0920586118300920_main.pdf). |
| 25 | The 2004 methodological citation remains in the identity inventory. Date eligibility is a later, separate decision. |

Six preprint/journal identities are recorded: OC20, OC22, AdsorbML, Wander's Hessian study, Fahmy's magnetic-order study and Chen's Hubbard-U electron–phonon study. Five have explicit journal DOI relations on their primary arXiv pages. Wander's arXiv and journal metadata have the exact same title and all four ordered author names; its preprint and journal dates remain separate. These relations do not silently select a version for screening. [Wander preprint](https://arxiv.org/abs/2410.01650), [journal DOI](https://doi.org/10.1021/acs.jpcc.4c07477).

Chen's journal metadata has September 2026 month precision. Whether that journal version first appeared by the registered September 18 cutoff remains unresolved, even though the arXiv identity and earlier submission are clear. Later screening must resolve the exact journal date before selecting the preferred version. [Chen arXiv record](https://arxiv.org/abs/2605.20985), [journal DOI](https://doi.org/10.1016/j.mtphys.2026.102192).

The ESSI-origin lead now has a primary identity: Govindarajan, García-Lastra, Meijer and Calle-Vallejo, DOI 10.1016/j.coelec.2018.03.025. Page 2 of the author-hosted final article introduces ESSI and carries the title, ordered authors and DOI. This resolves the lead's identity without deciding whether a review article belongs in the eventual sample. [Primary article](https://pure.uva.nl/ws/files/35119379/main.pdf).

The outstanding identities have bounded next actions:

| Unresolved group | Keys / occurrences | What would resolve it |
| --- | ---: | --- |
| AFLOW, Alexandria, MP Crystalium, MPtrj, ODAC23, OMat24, OMC25, OMol25, OQMD | 9 / 18 | An exact cited paper, release or primary URL tied to the original mention. Familiar dataset names do not select one publication or version. |
| hp.x manual / troubleshooting / mailing-list replies | 1 / 4 | Exact manual version and message URL/date, with each source occurrence assigned separately. The HP journal article is not a substitute. |
| Dickens | 1 / 3 | Primary full text establishing the defect-site and Briquet-critique attributions separately; split occurrence joins if they refer to different works. The defect-site metadata candidate is DOI 10.1021/acs.jpcc.7b03481. [Publisher record](https://pubs.acs.org/doi/abs/10.1021/acs.jpcc.7b03481). |
| Paz and Nabat | 2 / 2 | Specific publication titles or identifiers. The sole shared context says only that they had publications; a known Nabat DOI does not prove which work that sentence means. |
| Holm | 1 / 3 | A specific intended publication if one was meant. Naming a correction procedure alone does not authorize insertion of an assumed original paper. |
| Reuter / Scheffler | 1 / 1 | Exact title/year/identifier for the named thermodynamics framework. |
| Otani | 1 / 1 | Exact Tsukuba tutorial title/date/URL. The verified MOLs repository is a different resource. |
| Program books | 1 / 2 | Exact editions/files/URLs. Multiple unspecified editions cannot be collapsed to a single work. |

Twelve independent file checks pass: exact key and occurrence coverage, source-field preservation, per-key edge membership, canonical referential integrity, unresolved-list accounting, Divanis references 1–25, six retained version relations, unchanged screening/coding statuses, DOI receipt hashes and identifiers, the correct DataCite registry, and original source/PDF hashes. The five registered source entries, ten prior PDF identities and four original inventory files retain their hashes. The validator and results are [retained alongside the review](../../results/s2_2026-09-20/complementary_identity_review/validation_checks.json).

The next literature step is to merge these exact identities into the candidate accounting while preserving the unresolved rows, then complete article/SI access and inclusion review under the registered criteria. Only the subsequently included papers receive one backward-reference pass. This review does not establish complete article/SI access, exhaustive database discovery, or a frozen eligible sample; every record remains NOT_SCREENED and NOT_CODED.
