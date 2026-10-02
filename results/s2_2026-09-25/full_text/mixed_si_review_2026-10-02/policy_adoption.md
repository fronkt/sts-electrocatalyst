# Seven case-specific choices adopted — 2026-10-02

Frank explicitly approved the proposed seven choices. The preceding proposal
sheet and source pins remain intact as history; the adopted record is
`approved_policy_adjudications.json`. This answers the seven interpretation
questions, not the remaining scientific evidence gaps. Eligibility instructions
v5 and the completed September SI reads are unchanged.

| Case | Adopted interpretation | Reconciled effect |
| --- | --- | --- |
| S25856 / Q2(c) | Follow the referent of conflicting FCC/rutile labels; do not assume a typo. | E4 UNCLEAR; UNRESOLVED. |
| S26411 / Q3(c) | Permit a documented coordinate identity check at reconciliation. | Check cannot establish identity: each supplied block declares108 atoms but has53 coordinate rows. Fresh public artifact is byte-identical. E4 UNCLEAR; UNRESOLVED. |
| S02708 / Q8(b) | A computed species/step must be explicitly studied as part of oxidation to O2. | E3 UNCLEAR→NO; first failure E6→E3. Overall exclusion remains. |
| S05004 / Q11(a) | Count new FEFF spectral-property simulations of explicitly selected OER intermediates; not D11 reanalysis. | E3 YES, secondary/provenance null; EXCLUDE:E6 unchanged. Earlier proposed(c) remains in the prior sheet, superseded by this case decision. |
| S16323 / SI-Q1 | The SCE-to-RHE conversion refers to the experimental paragraph, not automatically to DFT. | E6 UNCLEAR; UNRESOLVED. |
| S26256 / SI-Q2 | Hold the conflicting author ranking/source-data assignment. | E6 UNCLEAR and the existing verification hold retained; no substituted ranking or eta. |
| S27700 / SI-Q3 | Require an explicit eta or minimum-UL assignment; “based on” eta alone is insufficient. | E6 UNCLEAR; E4/E5 also unresolved. |

All seven current entrant-question flags are closed by the approved additive
layer. Five evidence holds remain. The historical21-question triage (14 answered
rules, seven then-open policies) remains byte-preserved; it is not a current
claim that these seven decisions are still unapproved.

## Coordinate check

The materials-structure validation gate checks declared species/counts, finite
Cartesian coordinates and nonsingular cells before any identity reconstruction.
All three S26411 blocks fail atom-count completeness:108 declared,53 supplied,
55 missing per block. The public Springer supplementary TXT returned HTTP200,
6649 bytes and the same SHA256 as the September27 file. No atoms were imputed,
bulk symmetry inferred from slab symmetry, phase assigned, or new DFT performed.
The next evidence need is a complete author-supplied coordinate file or an
explicit model-polymorph identification, not more calculation on these partial
blocks. Receipts: `coordinate_validation.json` and
`coordinate_primary_recheck.json`.

## Review boundary

Independent focused checks and root source reconciliation support the narrow
interpretations. S02708's complete main/SI review also considers its sampled
molecular-O2 configuration: it is an interfacial state, not presented as a step
in an oxidation-to-O2 pathway. Missing transition states or a complete cycle is
not itself the exclusion rule. S05004's new spectra are distinct from borrowed
free-energy results. No general population extension or automatic inclusion
follows from these decisions.
