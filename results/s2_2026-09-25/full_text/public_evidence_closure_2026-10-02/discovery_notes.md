# Public missing-SI discovery — 2026-10-02

## Scope and result

This bounded round selected ten checklist records for distinct scoped Zenodo/OSF searches, with no overlap with the S21177/S30575/S16392 assignments handled by the parent. Earlier Figshare attempts exist for several selected IDs and are not characterized here as first-ever SI searches: S11310, S18904, S20440, S21048, and S21131 had three each; S21356 and S23207 had two each, as recorded in `openai_public_si_continuation_2026-10-01/epmc_metadata_routes.json`. The supplied 2026-10-01 route receipts were checked first. Europe PMC DOI or supplementary-file queries were not repeated. The S11549/NLR and S14704/NSF PAR repeats were excluded.

Distinct public Zenodo and OSF searches did not surface matching deposits. Eight exact-DOI queries to Zenodo's public records API returned HTTP 500, so those results are unresolved service failures rather than evidence that a deposit does not exist. The API pattern used was `https://zenodo.org/api/records/?q=<URL-encoded DOI>&size=5`; DOI strings and individual route outcomes are in `discovery_routes.json`.

The search-indexed official Wiley pages exposed named SI files for S11310, S21356, and S23207. The official article page for S20440 exposed a named SI file and size, but clicking that listed attachment returned HTTP 403. The publisher stop was observed immediately; there were no retries or alternate publisher access attempts. None of these four manifests verifies local bytes, package completeness, or recovery. No SI was recovered.

## Selected records and rationale

| ID | Why this record was selected | Discovery outcome |
| --- | --- | --- |
| S03607 | Pleiades record selected for an exact DOI search in Zenodo and OSF. | Third-party bibliographic result was only a discovery hint; no SI deposit or SI manifest surfaced. |
| S08766 | ECS paper selected for an exact DOI search in Zenodo and OSF. | ResearchGate/SciSpace results were third-party discovery hints and surfaced main-article copies, not SI. |
| S11310 | Wiley record with an official indexed SI filename; checked distinct Zenodo/OSF deposit routes. | `adfm202009610-sup-0001-SuppMat.pdf` (1.7 MB) is manifest-only. |
| S18904 | Selected for scoped Zenodo/OSF searches; prior Figshare attempts are documented above. | CiNii was a bibliographic discovery hint only; no public deposit or authoritative SI manifest established. |
| S20440 | Open-access Wiley page offered a concrete attachment manifest and full author/affiliation identity, making it the strongest inventory lead. | Listed `sstr202300276-sup-0001-SuppData-S1.pdf` (846.2 KB); attachment click returned 403; no retrieval. |
| S21048 | Selected for scoped Zenodo/OSF searches; prior Figshare attempts are documented above. | EBSCO was a bibliographic discovery hint only; no SI deposit or manifest found. |
| S21131 | Selected for scoped Zenodo/OSF searches; prior Figshare attempts are documented above. | PubMed/OpenAlex were bibliographic discovery hints only; surfaced article copies are not SI. |
| S21356 | Official indexed page exposes a named SI PDF; data statement directs underlying data to the corresponding author, so author contact was not attempted. | `adma202306934-sup-0001-SuppMat.pdf` (1.2 MB) is manifest-only. |
| S23207 | Official indexed page exposes a named SI DOCX, with identifiable Anhui University and Ningbo Institute authorship. | `adfm202409714-sup-0001-SuppMat.docx` (10.1 MB) is manifest-only. |
| S23881 | Selected for scoped Zenodo/OSF searches. | OpenAlex was a bibliographic discovery hint only; available article PDF is not SI, and no deposit or SI manifest was verified. |

The exact quoted search strings, primary URLs, identity notes, repository response codes, and attachment distinctions are recorded per record in `discovery_routes.json`.

The initial receipt's blanket claim of no prior exact-ID SI-log hits was incorrect and is withdrawn. Current newness is limited to the scoped Zenodo/OSF searches. Third-party bibliographic and article-copy pages were used only as discovery hints, not as technical evidence.

## Search and access boundaries

- Public Zenodo records API: eight exact DOI queries; every request returned HTTP 500.
- Scoped public-index searches: `site:zenodo.org/records "<DOI>"`, `site:osf.io "<DOI>"`, and `"<DOI>" "Zenodo" OR "OSF"`; no matching repository results for the selected IDs.
- The route receipts and SI retrieval log were inspected for duplication before selection. No S21177, S30575, or S16392 searches were run.
- A manuscript, thesis, citation record, request-only page, or article PDF was never classified as SI.
- No author was contacted. No institutional repository, Purdue, Elsevier, proxy, credential, paid API, or Europe PMC route was used.
- The first Wiley SI attachment click returned 403. All publisher attachment requests stopped at that point; no bypass was attempted.

## Disposition

Ten records were checked. Four public publisher manifests identify expected attachments, but none was retrieved or completeness-verified. No verified SI attachment was found. These results add route evidence only; all selected missing-SI distinctions remain open.
