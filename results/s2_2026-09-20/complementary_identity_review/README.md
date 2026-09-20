# Complementary citation identity reconciliation — 2026-09-20

This additive review reconciles the registered September 19 inventory without editing its 120 identity keys or 271 citation occurrences. It applies the P-LIT identity rules in `docs/research/s2-operating-decisions-2026-09-18.md` and the retrieval amendment. It makes no inclusion/exclusion decisions or method-reporting codes.

The review resolves **103 keys / 237 occurrences**, reaching **81 distinct canonical identities**. **17 keys / 34 occurrences** remain unresolved or partly resolved. These are identity counts, not eligible-paper counts. All 25 Divanis references and all 10 arXiv identifiers have verified metadata; six arXiv/journal relations remain explicit. No preferred screening version is selected.

| File | Purpose |
| --- | --- |
| `identity_links.jsonl` | One row for every original identity key, with exact occurrence IDs, canonical join or explicit unresolved state, basis and evidence. |
| `citation_identity_links.jsonl` | All 271 discovery edges, retaining original source hashes, paths, line/reference locations and occurrence-file hash. |
| `bibliographic_records.jsonl` | 88 primary metadata records: 72 Crossref records, the separate DataCite/Zenodo dataset, 10 arXiv versions and five repository/documentation resources. Six preprint records and the unmerged Dickens candidate are retained even where they are not canonical join targets. |
| `bibliographic_relations.jsonl` | Six preprint/journal identities and two separate Xu supporting-resource relationships. |
| `divanis_identity_review.jsonl` | All references 1–25 with exact bibliographic comparison and source defects. |
| `unresolved_identities.jsonl` | All 17 unresolved or partial keys and precise reasons against forced merges. |
| `primary_page_observations.json` | Metadata observations with primary URLs; a transcription, not a raw HTTP archive. |
| `crossref*/`, `*receipts*.json` | Raw DOI replies and request/cache provenance. |
| `metadata_requests*.json`, `fetch_metadata*.py` | Frozen bounded DOI batches; no broad discovery search or OpenAlex requests. |
| `reconcile.ps1` | File-only reconciliation using the retained metadata and explicit reviewed aliases. |
| `verification.json`, `validation_checks.json`, `validate.ps1` | Accounting, source/PDF hashes and 12 independent structural checks. |

Crossref supplied 72 successful or reused records from 73 DOI requests. Its sole 404 is DOI `10.5281/zenodo.12635`, whose official DataCite lookup succeeds; this is a different registry, not an invalid DOI. The DataCite raw record and HTTP receipt are under `results/s2_2026-09-20/primary_download_receipts/`.

The 17 outstanding keys are nine generic dataset/database families; an hp.x manual/mailing-list conflation; and Paz, Holm, Nabat, Dickens, program books, Reuter/Scheffler and Otani. The Dickens metadata candidate is verified, but the original key also holds a separate Briquet-critique attribution that has not been matched from primary full text. Do not merge the whole key on surname alone.

Metadata identity does not establish complete article/SI access. Ten prior PDF identities are reused only after their hashes match the earlier primary review. Named Xu/Wander study leads do not equate their article, dataset and repository versions. Article first-publication dates and the September 18 cutoff still need review where metadata precision is insufficient, especially the Chen September 2026 journal version.

All records remain `NOT_SCREENED` and `NOT_CODED`; `methods_bundle_complete` and preferred screening version remain null. The original discovery records and pinned search engine are untouched. No scientific processes or OpenAlex calls occurred in this review.

For an independent file-only check from PowerShell at the repository root:

```powershell
. ./results/s2_2026-09-20/complementary_identity_review/validate.ps1
```

The scientific readout and next actions are in `docs/research/complementary-identity-review-2026-09-20.md`.
