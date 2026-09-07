# Prospective screening-failure benchmark — 2026-09-07

Status: evaluation machinery available; scientific performance remains PENDING
until independently adjudicated HEA DFT truth and the required pre-DFT features
are available. This is an additive proposal and does not revise docs/91, the
running census, eligibility, or any historical candidate ranking.

## Question and separation of evidence

Can inexpensive pre-DFT features identify consequential screening errors on
previously unevaluated HEA compositions? Compare convergence-only,
geometry-only, model-disagreement, and combined scores on exactly the same
complete-feature, DFT-adjudicated cohort. Keep discovery, targeted audit, and
heldout readouts separate. Targeted abnormal cases measure diagnostic behavior;
they do not estimate prevalence in the candidate population.

A geometry change is a feature, not a failure label. Transferred protons and
weakly bound fragments can be physically valid. Ground truth must identify an
independently established DFT mismatch or consequential decision error, under a
named criterion fixed before opening heldout DFT labels. DFT force residuals,
DFT/ML energy errors, magnetic-basin evidence, and DFT-relaxed endpoint identity
belong to reference validation or adjudication; none enter the pre-DFT scores.
A detector requiring DFT forces would be a separate post-DFT diagnostic with a
different cost baseline.

A completed truth row requires a DFT reference method ID, passed reference QC,
independent-adjudication attestation, an adjudication record ID, retained DFT
evidence IDs, and rationale. These are traceability requirements. The evaluator
cannot establish the scientific adequacy of those claims by reading a boolean.
Failed or unresolved DFT QC must leave truth null. The adjudicator should not see
the proposed scores; record the evidence and criterion decision before unblinding.

## Fixed diagnostic scores

The score rule is screen-failure-flags-v1. These numbers are prespecified,
uncalibrated heuristics; they are neither learned probabilities nor physically
validated error thresholds.

| Method | Score (larger means more concerning) |
|---|---|
| convergence_only | 0 if the required screen relaxation converged, otherwise 1 |
| geometry_only | intact = 0; ambiguous = 0.5; changed = 1 |
| model_disagreement | min(1, ensemble_spread_ev / 0.10 eV) |
| combined | maximum of the three component scores |

The fixed flag threshold is score >= 0.5. Consequently the spread flag begins at
0.05 eV; this is an experimental diagnostic cutoff, not a claim about MACE error.
The target consequential-error criterion is separate and must be defined in the
named protocol. Do not tune these cutoffs against heldout labels. Any revised
rule needs a new version and a new untouched evaluation cohort.

The protocol must define the case unit, relaxation convergence criterion,
geometry-to-category mapping, ensemble members, and the scalar quantity whose
maximum-minus-minimum spread is measured. Compare like-for-like reaction or
branch quantities with common referencing. Different functional families can
disagree systematically; spread is a feature, not an uncertainty interval.
Missing models do not imply agreement. Unknown convergence, geometry, or
ensemble spread is null. The combined score remains null if any component is
unknown. This module accepts geometry categories from a declared upstream
classifier; it does not reinterpret or change frozen geometry criteria.

## Manifest contract

The JSON root contains exactly schema, protocol_id, truth_criterion_id,
ranking_tolerance_ev, and cases. Schema is screen-failure-benchmark-v1. Identifiers
are nonempty trimmed strings. Every scalar must be finite and numeric booleans
are refused. Duplicate JSON keys, duplicate case IDs, and unknown fields fail
validation.

Each case contains exactly:

- case_id: stable physical case/chain ID, retained when new observations arrive.
- group_id: canonical sampling-group ID.
- composition_id: canonical composition ID; aliases must resolve before input.
- split: discovery, audit, or heldout.
- features: exactly converged (boolean/null), geometry_status
  (intact/ambiguous/changed/null), ensemble_spread_ev (nonnegative number/null).
- truth: null until admissible independent DFT evidence is available.
- ranking: null unless a matched scalar comparison is defined.

No composition_id or group_id may occur in heldout and either development split.
Discovery and audit may share a composition/group but remain separately reported.
All descendants of a composition, including its sites, decorations, intermediates,
and adjacent trajectory frames, inherit its allocation. Enforcement uses the
supplied canonical IDs; silently relabeling the same composition is not a valid
way to bypass it.

A non-null truth contains exactly failure (boolean), criterion_id (equal to the
root truth_criterion_id), reference_method_id, reference_qc_passed (true),
independently_adjudicated (true), adjudication_id, dft_evidence_ids (nonempty
unique string list), and rationale. Both positive and negative labels need evidence.

A non-null ranking contains exactly comparison_set_id, screen_value_ev, and
dft_value_ev (number/null). Lower values rank ahead of higher values. The
comparison set must identify a common observable, stoichiometry/reference cycle,
and DFT specification; quantities from unrelated branches are not comparable.
A non-null DFT value requires admissible truth. A comparison set cannot mix DFT
reference methods within a split. The common root ranking_tolerance_ev is the
predeclared resolution tolerance, applied to pair differences on both axes.
Do not choose it after seeing which candidate would win. It should follow the
numerical error budget; the code does not infer one from conv_thr.

## Output and interpretation

Within each split, all methods use the same rows having all three features and
admissible truth. The report lists every excluded case and its missing inputs;
report its denominator alongside performance. Total and evaluated composition/group
counts accompany case counts so repeated sites cannot masquerade as independent
samples. If missingness is selective, this
complete-case result does not establish whole-panel performance.

Confusion matrices report TP/FP/TN/FN, precision, recall, and specificity.
Undefined denominators are JSON null, never perfect performance or NaN.
Selective risk is the observed failure fraction among accepted low-score cases.
Coverage is relative to the evaluated cohort. The curve includes the empty
cohort and only complete tied-score groups: it never picks the favorable order
within a tie. Correlated cases are not treated as independent uncertainty samples;
this version reports descriptive point estimates, without confidence intervals.

Ranking readouts separate concordant pairs, reversed pairs, screen-unresolved
pairs, DFT-unresolved pairs, and incomparable pairs. Resolved-pair error rate
excludes ties, while screen-unresolved fraction makes unresolved predictions
visible. Curves recalculate those counts on each retained score group. Pair
metrics do not pool discovery/audit/heldout or unmatched comparison sets.

Accepted-case counts are not measured DFT cost savings. A claim of savings needs
a prospective selection policy, cost accounting including ensemble inference,
and independent evidence that skipped cases satisfy the required decision risk.

The top-level report remains PENDING without an evaluable heldout case, including
when all known audit cases are labeled. PARTIAL means heldout evaluation exists
but some manifest inputs remain pending. EVALUATED means all included cases are
evaluable and heldout cases exist; it makes no claim about statistical power,
DFT accuracy, calibration, or surface relevance.

## API and operation

src/hea_oer/failure_benchmark.py exposes validate(payload), score_features(features),
evaluate(payload), load_manifest(path), and main(argv=None). It uses only the
Python standard library, performs no fitting, invokes no subprocess, and launches
no compute. Run through the project's verified background execution route:

~~~text
python src/hea_oer/failure_benchmark.py INPUT.json --output NEW_REPORT.json
python -m pytest tests/test_failure_benchmark.py -q
~~~

CLI exit codes: 0 EVALUATED; 3 PENDING or PARTIAL (the report still exists); 2 invalid
input or I/O error. Existing output paths are refused to preserve banked readouts.
Tests call the API and CLI entry function in process and use only synthetic
fixtures, with coverage for split leakage, truth leakage, invalid references,
missing model results, duplicate/nonfinite JSON, tied-score selection, ranking
reversals, unresolved pairs, and preservation of existing outputs.

The HEA panel planner maps heldout_dft_labels to heldout, targeted_audit to audit,
and discovery to discovery. Use its stable slot_id for case_id and canonical
candidate_id for composition_id/group_id. Unresolved slots remain in the input
with null features and truth. Materialized MACE geometry is not DFT ground truth.

## Concrete pilot input and truth criterion

The frozen plan at results/hea_validation_2026-09-07/plan.json maps through src/scripts/prepare_failure_benchmark.py to 45 adsorbate-state cases (15 chain slots times OH/O/OOH). Slab references remain in the geometry snapshot. Selected states have only pre-DFT geometric and convergence features; every DFT truth and every unavailable ensemble spread remains null. The adapter retains raw classification evidence and the exact geometry hash separately.

The proposed criterion id paired-state-reference-error-0p10eV-v1 denotes an absolute error exceeding 0.10 eV in a paired, same-geometry, reservoir-referenced state energy. This 0.10 eV is a prospective scientific decision threshold, not an empirically calibrated accuracy bound. Specify one coherent DFT Hamiltonian/reference family per benchmark and keep projector alternatives separate. A DFT label requires clean SCF, verified source geometry and spin adjudication, plus numerical controls supporting the needed resolution. If reference uncertainty straddles the threshold, keep truth null. The label evaluates agreement with that DFT reference, not physical electrode accuracy. Chemical-state retention after DFT relaxation is a separate endpoint and must not be merged into this label after inspecting held-out results.

For each state, use E(state)-E(clean)-nO*E(H2O)+(nO-nH/2)*E(H2), consistently within each calculator, with (nO,nH)=(1,1),(1,0),(2,1) for the three inventories. These are formal electronic state energies; a rearranged inventory is not automatically an intact adsorbate or a physical CHE pathway. The benchmark does not add an OOH vibrational correction to a changed geometry. Before classifying near-threshold errors, converge the paired differences and record their remaining numerical sensitivity; 0.10 eV has no relation to calibrated ensemble uncertainty.

The 0.05 eV ranking tolerance is reserved for future comparable reaction-energy pairs; the current input contains no ranking values. Cases sharing a composition remain in the same development/held-out partition. Targeted audits and discovery cases may share a composition but are reported separately.
