# Entrant choices: seven open SI policy questions

These are choices about how to apply the entrant rules, not findings that missing scientific evidence exists or does not exist. The recommendations below are already recorded in the triage files but remain unadopted. Effects are limited to the cited record and evidence. No missing reference is inferred, and no new numerical overpotential is calculated.

## S25856 — Q2: contradictory phase labels

**Question.** The characterized sample has Raman evidence labelled rutile RuO2 and HRTEM fringes labelled face-centred cubic RuO2; the paper connects its catalyst models to this sample. Should the conflicting label prevent E4 from being YES?

- **(a) Give priority to the explicit rutile evidence.** Treat the FCC label as a probable slip and set E4 YES. With the completed SI's E6 evidence, this could make S25856 ELIGIBLE if the other criteria remain YES.
- **(b) Treat any potentially applicable conflicting phase label as a contradiction.** Keep E4 UNCLEAR and the record UNRESOLVED until resolved.
- **(c) Decide by referent.** A label on the computed model or the characterized material whose phase evidence is used is a contradiction; a separate reference label is not. Here the FCC label is on that same characterized sample, so E4 remains UNCLEAR and the record UNRESOLVED.

**Existing recommendation (unadopted):** (c), because phase evidence and contradictions should follow what each label refers to. The SI supplies E6 evidence but does not settle the sample's conflicting phase labels; that scientific identity conflict remains distinct from the entrant's choice of rule.

## S26411 — Q3: identifying rutile from coordinates

**Question.** The SI supplies optimized CONTCAR files for RuO2, B-RuO2 and Ta/B-RuO2, along with a published cell and atomic coordinates. May structural identity be established by reconstructing the relaxed slab from these files, although v5 does not say whether coordinate reconstruction is an allowed route?

- **(a) Require the paper's text to establish rutile.** Without a stated rutile identity or sufficient stated cell and arrangement, E4 remains UNCLEAR; S26411 remains UNRESOLVED.
- **(b) Allow screeners to identify the polymorph from relaxed coordinate files.** E4 may become YES if a documented coordinate check establishes rutile for the qualifying computed model; otherwise it remains UNCLEAR.
- **(c) Keep the initial E4 UNCLEAR and refer a documented coordinate identity check to reconciliation.** E4 becomes YES only if that check establishes rutile for the model; if not, the record remains UNRESOLVED.

**Existing recommendation (unadopted):** Extend Q3(c) to coordinate-file evidence: retain E4 UNCLEAR at screening and send a precisely documented identity check to reconciliation if authorized. The CONTCAR files are scientific evidence available for checking; whether screeners or reconciliation may use reconstructed coordinates is the policy choice.

## S02708 — Q8: OER context without an O2-pathway step

**Question.** A *O/*OH/H2O Pourbaix analysis is placed in an OER potential region and linked to pH-dependent OER activity, but the paper does not present those species or a calculated step as part of its O2-evolution pathway. Does this satisfy E3?

- **(a) Count any explicit OER connection.** E3 is YES. The completed SI has no model-specific CHE η/UL, so E6 is NO and the record is excluded at E6.
- **(b) Require the species or step to be presented as part of O2 evolution.** E3 is NO and the record is excluded at E3.
- **(c) As in (b), while counting a water step placed inside a named OER mechanism.** No such pathway step is presented here, so E3 is NO and the record is excluded at E3.
- **(d) Treat the middle case as uncertain.** E3 remains UNCLEAR; the completed SI's lack of a qualifying model-specific CHE η/UL still makes the record excluded at E6.

**Existing recommendation (unadopted):** (b), which follows the adopted test that species or steps must be studied as part of oxidation to O2. The alternatives change the first failing criterion, not the overall exclusion. The absent pathway step is the scientific-evidence issue; how much OER framing suffices for E3 is the entrant's rule choice.

## S05004 — Q11: FEFF spectra on borrowed geometries

**Question.** The paper runs FEFF spectral simulations for OER-related species using literature bond lengths, while its cited free-energy diagram comes from another study. Does the new spectral calculation count as computing OER intermediates for E3? If not, is it a re-analysis under D11?

- **(a) Count the spectral simulation as a new OER calculation.** E3 is YES, but the completed SI still supplies no qualifying CHE η for this model, so the record is excluded at E6.
- **(b) Do not count it as new OER calculation; call reuse of electronic-structure geometries “reanalysis.”** E3 is NO and the record is excluded at E3; secondary is `reanalysis`, with provenance based on whose geometries are reused (external where the paper identifies another study).
- **(c) Do not count it as new OER calculation or as re-analysis.** E3 is NO and the record is excluded at E3; secondary and provenance remain null because a property simulation on borrowed structures is not re-analysis of reported electronic-structure results.

**Existing recommendation (unadopted):** (c). D11's re-analysis category concerns analysis of existing electronic-structure results; the new FEFF run computes a spectral property on borrowed structures. All options exclude this paper overall; the choice changes the criterion and, under (b), the secondary/provenance fields.

## S16323 — SI-Q1: scope of “all potentials in this work”

**Question.** Does the sentence “All potentials in this work were converted to reversible hydrogen electrode (RHE) scale,” located in an experimental SCE-conversion paragraph, also establish the reference for the computed limiting potential in Fig. 3c?

- **Broad scope:** Read “all potentials” literally across experimental and computational results. The reported UL may satisfy E6 if the figure's result is otherwise assigned to the qualifying model.
- **Paragraph scope:** Read the sentence as describing the measured potentials converted from SCE; it does not establish the DFT reference. E6 remains UNCLEAR and S16323 remains UNRESOLVED.

**Existing recommendation (unadopted):** Paragraph scope, with the reference determined by what the sentence describes. The deciding evidence is the sentence's scientific context and referent; the entrant must choose whether its scope extends to DFT. The separate 0.17 eV value at 1.5 V is not itself an E6 equivalent.

## S26256 — SI-Q2: author ranking conflicts with source-data assignment

**Question.** The authors state that the barrier at Ru1 is lower than at Ru2, but the source-data surface assignment appears to reverse that ranking. Should the author-stated comparison still qualify under D4?

- **Accept the author-stated comparison.** Count the comparison for E6 if the remaining D4 conditions are met.
- **Require the source assignment and author comparison to agree.** Keep E6 UNCLEAR and the record on hold until the conflict is resolved.
- **Treat the source table as controlling and reject the comparison.** Do not count the stated ranking for E6; this would require a rule for resolving the incompatible assignment rather than silently correcting the paper.

**Existing recommendation (unadopted):** Keep E6 UNCLEAR until the assignment is resolved; do not correct the paper's values or substitute a reader-created reversal. This is also the current SI-adjudication hold, so no YES→UNCLEAR correction is pending. The conflict is in the paper's scientific reporting; which source controls eligibility is the policy choice. The 1.23 V cumulative levels do not themselves report a maximum step.

## S27700 — SI-Q3: pH-dependent onset line related to η

**Question.** A pH-dependent OER onset line is captioned as based on theoretical η, but the plot shows potential rather than a labelled η and does not identify the line as a minimum UL. Does that graphical result itself report a qualifying η/UL?

- **Count the transformed plot as a graphical η/UL.** E6 may be YES if the plotted line is assigned to the qualifying model and accepted as the authors' η result.
- **Require an explicit author assignment as η or UL.** Because the plot's potential is not explicitly identified as either, E6 remains UNCLEAR.

**Existing recommendation (unadopted):** Require the explicit η/UL assignment. A statement that a plot is based on theoretical η does not by itself establish that the plotted potential is η or minimum UL. E4 and E5 are separately unresolved, so accepting this graphical result alone would not make S27700 eligible. The 1.80 eV value at 0 V is a maximum-step quantity, not an absolute η to convert.
