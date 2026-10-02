# Seven entrant choices after focused source review

Status: proposals only. None is adopted, and none changes canonical state in this
batch. The original questions, assessments and recommendations remain intact in
`reconcile/si_policy_choices_2026-10-01.md` and `reconcile/si_questions_triage.md`.
Source passages below were checked directly against the existing reading copies.
The choices are limited to these records; they do not authorize a general scope
extension, missing-reference inference, reconstructed overpotential, or compute.

## Proposed choices and consequences

| Record | Proposed choice | Why | Effect if approved and verified |
| --- | --- | --- | --- |
| S25856 / Q2 | **(c): follow the referent of contradictory phase labels.** | Both FCC and rutile labels refer to the characterized catalyst used to support the model. v5 D1 does not permit silently treating the FCC label as a typo. | Keep E4 UNCLEAR and UNRESOLVED. |
| S26411 / Q3 | **(c): authorize a documented coordinate identity check at reconciliation, not screening.** | The optimized CONTCAR files exist; text alone does not resolve the assigned polymorph. Coordinate reconstruction is not an explicitly adopted identification route. | Remain UNRESOLVED until an authorized check establishes or fails to establish the model identity. Approval authorizes a check, not an E4 YES in advance. |
| S02708 / Q8 | **(b): require the computed species/step to be presented as part of oxidation to O2.** | OER-region/pH framing alone does not identify the calculated Pourbaix species as a step or intermediate of the O2 pathway. | Overall exclusion unchanged; first failure would move from E6 to E3 after reconciled evidence review. |
| S05004 / Q11 | **Clarify whether FEFF spectral-property calculations on borrowed geometries count under D2; proposed (a), conditional on accepting that boundary.** | The authors explicitly study spectra of OER intermediates, but no new intermediate energies or relaxed geometries are reported. The adopted spectra clause and the general “DFT or similar electronic-structure method” definition meet at this unresolved boundary. | Proposed (a) preserves EXCLUDE:E6. If (c) is preferred, first failure moves to E3. No option here justifies treating the new FEFF property simulation as re-analysis of existing electronic-structure results. |
| S16323 / SI-Q1 | **Paragraph scope for the RHE-conversion sentence.** | “All potentials” is immediately defined by conversion from experimental SCE measurements; no computational reference follows merely from its broad wording. | Keep E6 UNCLEAR and UNRESOLVED. Broad-scope approval could change the E6 assessment only after checking the model-specific UL evidence. |
| S26256 / SI-Q2 | **Hold E6 UNCLEAR until the surface assignment/ranking conflict is resolved.** | The authors' stated comparison and their source-data assignments disagree. Do not replace the comparison with a reader-ranked reversal or decide that one source is a typo. | Keep UNRESOLVED; no pending YES-to-UNCLEAR correction. |
| S27700 / SI-Q3 | **Require an explicit author assignment as eta or minimum UL.** | A potential line “based on” theoretical eta does not itself identify that plotted quantity as eta or minimum UL. | Keep E6 UNCLEAR. E4/E5 also remain unresolved, so accepting the line alone would not establish eligibility. |

## Decisive checked passages

**S25856.** Main HRTEM, `text/S25856.txt` lines 153-158: the fringes are assigned
to “face-centred cubic (FCC) RuO2”; main operando Raman, lines 286-288, reports
“Raman features of rutile RuO2”. The FCC statement concerns Se-RuOx, not an
unrelated reference. The contradiction therefore remains a scientific identity
issue under the proposed referent rule.

**S26411.** `text_si/S26411.txt`, SI2 p. 1, describes “The optimized-geometry
CONTCAR of RuO2, B-RuO2, and Ta/B-RuO2.” SI3 contains a `RuO2\(1\1\0)` header,
cell vectors and atom coordinates. Those are available evidence for a potential
check, not a completed polymorph determination. No reconstruction was performed.

**S02708.** Main Sec. 3.3, `text/S02708.txt` lines 701-712, describes structural
differences in the OER region that “may result in the observed pH-dependent
behavior of the OER”. The conclusion, lines 769-786, describes the assessment of
interfacial Gibbs energy and a surface Pourbaix diagram. These passages provide
context, not an explicitly calculated O2-evolution pathway step. The current
EXCLUDE:E6 record remains untouched while this criterion clarification is pending.

**S05004.** Main `text/S05004.txt` lines 160-176 chooses “the four intermediates
mentioned in the proposed reaction mechanism” for simulated spectra. Methods,
lines 364-389, identifies FEFF and an Ir-substituted rutile RuO2(110) spectral
model. Main Fig. 1 caption, lines 215-222, attributes the OER free-energy diagram
to “free energy DFT calculations in ref 30”; the IrO2 result is attributed to
another reference. Existing SI documents structures and spectra, not a new OER
energy cycle. The earlier policy sheet recommends (c); the fresh independent
review instead favors a literal spectra-clause reading, (a). Both readings and
their boundary are retained here. This is not a silent revision of the old
recommendation and not evidence that an E3 YES is already authorized.

**S16323.** Main Electrochemical Measurements, `text/S16323.txt` lines 184-191:
the RHE statement immediately specifies `E (vs RHE) = E (vs SCE) + 0.244 V +
0.0591 × pH`. Fig. 3c is the computed limiting-potential evidence, not the
separate 0.17 eV result at 1.5 V. The conversion paragraph's referent, rather than
its physical location alone, is the reason for the proposed narrow reading.

**S26256.** Main `text/S26256.txt` lines 1008-1015 states a lower barrier at Ru1
than at Ru2 and the RuO2 comparison site. SI source-data sheet `figure 5g`,
`text_si/S26256.txt` lines 5553-5564, assigns the cumulative *O/*OOH levels
1.98/3.97 to RuO2 and 1.89/3.96 to Pt-RuO2-Ov at U=0. Checking adjacent steps
reveals the incompatible comparison, but no substitute eta, ranking or corrected
table is adopted. The 1.23 V cumulative levels are not directly a reported
maximum step.

**S27700.** Main Fig. 6 caption describes a plot based on theoretical
overpotential. SI4 peer-review response 7, `text_si/S27700.txt` lines 2921-2931,
explains the plotted axis as `V vs. CHE`, including “The units of theoretical
overpotential in our work can be converted to V vs. CHE based on CHE.” Preserve
that wording without treating it as a valid scale conversion or identifying an
unlabelled potential line as minimum UL. Existing unresolved model identity/facet
issues remain separate.

## Approval boundary

Approval of these proposals would authorize the stated interpretations/check,
not automatic eligibility for an unresolved paper. Any resulting field change
requires a recorded, evidence-checked reconciliation, preservation of previous
rows, and an explicit review of whether the clarification affects other cases.
No coordinate check, global rule revision or policy-dependent canonical change
has occurred in this batch.
