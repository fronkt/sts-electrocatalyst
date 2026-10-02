# Public-source screening continuation

Batch started 2026-10-01 local time and verified 2026-10-02. No Purdue/Elsevier
API, institutional login, publisher challenge bypass, paid OpenAI request or DFT
submission. The tracked API estimate remains $1.1105254 of the $50 lifetime cap;
this is not an invoice or account-wide spending limit. Routine work used GPT-6 Luna.

## Retrieval and reviewed decisions

64 distinct exact-DOI Europe PMC queries exclude historical metadata attempts,
the earlier 30-query batch, duplicate DOIs and the known S13316 package-only route.
32 exact matches yield eight PMC leads. Exact XML/cloud DOI identity and declared
file manifests were checked; all eight inventories downloaded with matching cloud
MD5 checksums. Cached replay verifies all retained hashes without network access.
184 declared attachments remain local, alongside eight main PDFs and extracted text.

| Record | Before | Reviewed result | Decisive evidence |
| --- | --- | --- | --- |
| S00475 | NEEDS_SI | ELIGIBLE | Complete 13-page SI states the authors' (001)-to-rutile-(110) mapping; main reports numerical theoretical eta. Author units/definition caveat retained, not corrected. |
| S09964 | NEEDS_SI | EXCLUDE:E6 | Complete 11-page SI and main report a water-dissociation activation barrier, not CHE eta. |
| S03669 | UNRESOLVED | EXCLUDE:E6 | Complete 27-page SI and main report OH/O species-formation redox potentials, not an OER CHE overpotential. |
| S03699 | UNRESOLVED | EXCLUDE:E5 | Complete 11-page SI describes finite global-minimum nanoparticles with no rutile-(110) mapping. Phase remains UNCLEAR, not inferred non-rutile from size/formula. |

Nine independent full-source assessments cover these four papers. A focused third
read resolves S03699's first-failure disagreement; the original dissent is retained
and not adopted. S00475's eta-note disagreement has an explicit field decision.
Root checked actual decisive PDF pages/figures and repaired source quotations and
page labels without changing scientific verdicts. Initial failed quote checks and
two initial output versions are retained; `scientific_final/` is authoritative.

Four recovered mixed-format inventories remain unassessed, unchanged in canonical
state and still on the checklist: S12208 (60-page PDF plus 173 trajectory files),
R0003 (27-page PDF plus video), S24821 (56-page PDF plus two videos), S25024 (Word SI).
See `mixed_format_queue.json`. Retrieval completeness is not a completed full-format
read, and no absence-based E6 decision follows from unchecked files. Separate
targeted repository searches retain duplicate/no-new-SI outcomes explicitly.

## Verification and next work

37 offline regression tests pass. All nine current assessment rows pass format,
all-excerpt and strict deciding-excerpt checks. Both dated/completed-round
scientific verifiers have zero errors. Against `0983987`, only four reviewed rows
change; all 2,496 v3/v4 rows and 119 historical evidence pins are preserved.
Checklist 161 to 157; every retained row is exact, including S29721/S10090/S22807/
S26024. Tiers 68/36/47/6; 17 D10 checks. Current 173 ELIGIBLE, 102 NEEDS_SI,
115 UNRESOLVED and 28 no-readable-text records. The original 104 third reads,
130 verification targets and 21-question triage are preserved.

Next: full-format assessment of the four recovered packages, remaining distinct
public evidence routes and the seven unadopted entrant policy choices. No inclusion
freeze, method coding, compute spending or melt selection is authorized here. The
paid-runner manifest still intentionally refuses calls after scientific-state
changes; any future paid tranche requires reviewed-state pins and the same lifetime
ledger, not a budget reset. Public-source work does not depend on that gate.
