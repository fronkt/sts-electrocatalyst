# One-generation backward-reference pass, 2026-09-20

Status: provisional discovery from the four base papers supported by the current first and second eligibility reviews: Man 2011, Feng 2025, Xu 2015 and Garcia-Mota 2011. The global candidate/inclusion freeze remains open. These reference occurrences are neither screened inclusions nor method codes.

The [registered P-LIT rule](s2-operating-decisions-2026-09-18.md#p-lit-prospective-search-and-coding-choices) permits one backward-reference inspection from eligible base papers, without recursive or forward-citation expansion. This pass retains complete bibliography lists from every currently available component of those four papers. It does not select only apparently relevant citations.

| Source bibliography | PDF page(s) | Printed labels | Numbered groups | Occurrences after splitting lettered items |
|---|---:|---|---:|---:|
| Man article | 7 | [1]-[26] | 26 | 47 |
| Feng article | 9-10 | [1]-[71] | 71 | 71 |
| Xu article | 6-7 | (1)-(52) | 52 | 52 |
| Garcia-Mota article | 5 | [1]-[28] | 28 | 44 |
| Xu SI | 68/S68 | (S1)-(S3) | 3 | 3 |
| Total | | | 180 | 217 |

[Reference occurrences](../../results/s2_2026-09-20/backward_reference_discovery/reference_occurrences.json) retain each parent DOI, source PDF and text hashes, document role, reference number/subletter, PDF page(s), original full-text line range and complete printed bibliographic text. Each lettered item links to an intact numbered group. Parallel-language journal citations within a single unlettered item remain together. These are 217 source occurrences, not 217 deduplicated papers.

Five exact reference-block transcripts in the same directory permit independent comparison with the original extracted text. Repeated page headers/footers are omitted from cleaned citation fields but tracked by line number. Accent, ligature and spacing artifacts remain visible. Missing titles in abbreviated Wiley references are not invented. Every record has source kind PRIMARY_INSPECTED_BIBLIOGRAPHY; there are zero metadata-only or Crossref-derived occurrences in this pass. Later DOI/title enrichment must remain a separate evidence layer.

Only three bibliography occurrences print a DOI:

- Man [4b] prints `10.1016/j.physletb.2003.10.071` beside a Koper/J. Electroanal. Chem. citation. That apparent mismatch is retained and flagged for later identity resolution.
- Xu (34) explicitly identifies the supporting-data DOI `10.5281/zenodo.12635`.
- Garcia-Mota [21] prints the line-wrapped `10.1016/j.jelechem.2010.10.004`; the original `j.jele-/chem` typography remains in the citation, while the DOI field joins the line-break hyphen.

No missing DOI is inferred. Feng [9]'s pancreatic-fibroblast citation is retained despite its apparent irrelevance; Feng [53]'s missing year is not filled by guesswork. Prior-to-window studies, books, software and methodological references also remain in the discovery record. Relevance and date decisions belong to later screening, not extraction.

## Source coverage and verification

[Xu's access addendum](../../results/s2_2026-09-20/primary_access_review/xu_si_access_addendum.json) closes its former SI acquisition gap: official Figshare item 2190043/file 3824209, 68 pages, matching title, all three authors, resource DOI and publisher checksum. Its three SI references therefore join the article's 52 entries.

The declared Man, Feng and Garcia-Mota supplements remain unavailable. Whether they contain additional references is unknown. Thus all five available bibliography blocks are enumerated, while completeness across the four full article/SI bundles remains unresolved. The broader database search and candidate freeze are also outside this pass.

[Structural verification](../../results/s2_2026-09-20/backward_reference_discovery/structural_verification.json) confirms 180 groups, 217 unique occurrence IDs, intact expected label sequences and matching PDF/text/block hashes. Rejoining each group's split items reconstructs its cleaned citation text after whitespace normalization with zero disagreements. This checks preservation and indexing; it is not an independent all-page visual inspection or scientific screening.

The source text paths and line numbers refer to the parent's full-text extraction directory. The retained PDF hashes, local reference-block copies and block hashes preserve review anchors if the temporary extraction directory is later archived. No primary PDF, frozen eligibility proposal or original search artifact was changed.

## Next application

Validate identities and screen these occurrences under the unchanged rutile-(110)/OER/reported-CHE-overpotential/date rule, preserving every discovery edge when identities merge. Resolve suspicious bibliography text against primary publisher metadata instead of silently repairing it. Add references from the three missing supplements if legitimate access becomes available. A cited study does not become a new expansion source in this pass. Complete the global candidate procedures and independent eligibility review before coding reporting fields.
