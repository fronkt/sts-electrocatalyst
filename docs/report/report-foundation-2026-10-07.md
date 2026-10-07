# Paper-report foundation — October 7, 2026

Working evidence and writing prompts for Frank. This is a report workspace, with section questions and source pointers. The [current project review](project-review-2026-10-07.md) supplies the scientific and live operational context. Sources in this workspace are research navigation, not a submission bibliography.

The [official STS 2027 Research Report Guidelines](https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Research-Report-Guidelines.pdf), checked October 7, require the student to write the report without generative AI and to assemble their own references. This foundation supports evidence review and idea development; the manuscript text and scientific conclusions are Frank's writing. The report permits up to 20 content pages, with title, abstract and bibliography outside that count; appendices count. Basic format: one column, 1.5 spacing, 1-inch margins, legible type at least the apparent size of Times New Roman 11 pt, a PDF no larger than 4 MB, and bottom-right page numbering after the abstract. Each figure/table needs its own source attribution.

## 1. Decide the scientific emphasis from completed evidence

**Supported report center:** output-level detection of symmetry restrictions, the external corpus census, and conditional sensitivity of OER descriptors to computational choices.

**Application extension:** MLIP site-integrity screening and the exploratory S8 prediction comparison. At this review, C-FG has incomplete values and S8 has no retained experimental results. Neither supplies a proven new catalyst.

Writing questions:

- What specific reliability problem did the project uncover while screening catalysts?
- What does silentgate measure directly, and what remains inferred or undetectable?
- Which original predictions were supported, falsified or left incomplete?
- How do these findings affect confidence in the proposed alloy rankings?

Consult the elected [claim of record and six-row body allocation](../45-error-ledger.md) before deciding your wording. Keep detector observations, interpretation, and material performance distinct. A change in the paper's emphasis does not cut the ongoing scientific program.

## 2. Working content budget

This is an initial organization to adjust after your own first draft; figure space is included.

| Section | Approximate content pages | Evidence task |
|---|---:|---|
| Introduction and research question | 1.5 | Explain the problem and hypothesis briefly from papers you have read. |
| Methods | 4.5 | Describe the instrument, control populations, corpus, DFT conventions and analysis choices reproducibly. |
| Detector validation and external census results | 4 | Show controls, full denominators, stratification, unknowns and failed predictions. |
| U/projector/uncertainty results | 3 | Present the six registered body rows and their protocol limits. |
| Alloy application | 2 | Use the completed site census; include terminal C-FG or experimental evidence only at its actual scope. |
| Discussion and limitations | 3 | Interpret your findings, competing explanations and external validity. |
| Compact supplementary detail within the report | 1 | Prioritize reproducibility detail not already in Methods. |
| Reserve | 1 | Accommodate the final figure layout or an actual new result. |
| **Total** | **20** | Title, abstract and bibliography are separate. |

## 3. Methods: begin writing here

### 3.1 Research design and endpoints

Prompts: What was the primary question? Which quantities, populations, thresholds and outcomes were fixed before observation? How did the preregistered investigation differ from later descriptive calibration? Where did the scope change? Explain why rejected or unknown outputs remain visible. Use [the registration](../43-prereg-week1-factorial.md), [dated ledger](../45-error-ledger.md), and [S2 scientific readout](../research/s2-scientific-readout-2026-09-18.md). Select the relevant protocol details; do not copy the amendment history into the report.

### 3.2 Output auditor and controls

Prompts: How are eligible adsorbate atoms identified? What evidence produces LOCKED, ON_PLANE, UNRESOLVED or unscorable classifications? What does exact zero mean at output precision? Why do run-level ALL and negative-control ANY use different quantifiers? How do missing atoms, truncation and invalid force blocks affect scoring? What can the auditor miss?

Sources: [core behavior](../research/silentgate-core-2026-09-13.md), [verification](../../results/silentgate_core_2026-09-13/verification.json), the reader/classifier implementation under silentgate, and the actual positive/negative-control fixtures. Recorded results: 9/9 positives; QE 0/11 ANY locks; OC20 0/500 ANY locks; 96/96 two-witness agreement. Avoid calling this a universally measured sensitivity/specificity or combining the different denominators into one accuracy.

### 3.3 External corpus and prevalence bounds

Prompts: Why this fixed corpus? What is a row, and which rows have adsorption-force evidence? How do 810 headers, the original 630 final-force cases and retained 626 relate? Explain the four exclusions and 80 unknowns. Define the combined prediction and named-pair subclause separately. Explain the detected-lock lower-bound claim in your own words.

Sources: [Xu census](../../results/s2_2026-09-18/xu_census.json), [independent verification](../../results/s2_2026-09-18/xu_independent_verification.json), [scientific readout](../research/s2-scientific-readout-2026-09-18.md). Key arithmetic: 50 + 496 + 80 = 626; final-force-clause bounds 50/626 and 130/626; nontrivial headers 70/810. The 50 detector LOCKED rows all belong to the four-layer subset. These quantities need separately labeled panels or columns.

### 3.4 DFT/CHE conventions and sensitivity

Prompts: Which cell, termination, adsorbate identity, magnetic initialization, pseudopotential, gas reference, U convention and projector apply to each reported comparison? How is the potential-limiting step obtained from the reaction-step free energies? What remains a model phase or a protocol-conditional result? Which references are shared rather than independent calculations? How are geometry, XC and numerical uncertainty distinguished?

Sources: [A0 readout](../figs/a0main_readout.json), [projector readout](../figs/pproj_readout.json), [BEEF readout](../../results/s5_beef_2026-09-17/readout.json), their pinned input/output paths and [S2 interpretation](../research/s2-scientific-readout-2026-09-18.md). The fixed-endpoint |delta c|/2 test is not automatically the movement of the general CHE floor. Preserve Mn magnetic, Fe model-phase, Ti spin and cell/coverage conditions.

### 3.5 Alloy site sampling and application

Prompts: Why did the sampling expand from 12 to 120 sites per retained alloy? What distinguishes strict intact and adsorbate-intact? How do admission policy, sampling and choice of statistic affect the proposed leader? What is the bootstrap resampling unit? How small is the admitted low tail? Why is a CHE descriptor not measured activity?

Sources: [census and errata](../95-census-2-3-readout-2026-09-13.md), [scientific census review](../research/census-review-2026-09-13.md), [site data](../../results/site_census_2026-09-06/readout_full/per_site.csv), [ranking-statistic record](../research/s8-ranking-statistic-proposal-2026-09-19.md). The complete MPA-0 set has 720 sites; only 109 pass the adsorbate-intact policy. C-FG, if included, uses fixed MLIP coordinates and two weighted p10-support sites; it is not a DFT relaxation experiment. Sources: [current arm-C design](../research/s8-arm-c-dft-design-2026-10-07.md) and its eventual terminal rerun readout.

## 4. Results evidence matrix

Use this as a factual checkpoint while writing your own Results. Outcome labels belong with their caveats; they are not conclusions to copy.

| Registered body row | Current outcome | Evidence to consult | Essential qualification |
|---|---|---|---|
| P7 | TRIGGERED; Cr eta span 1.122 V exceeds the 0.15 V trigger | [anchor-offset diagnosis](../41-prereg-anchor-offset-diagnosis.md) | Withdraws the original noble-anchor superiority framing; keep protocol/reference conditions. |
| P-PROJ | FIRES; absolute eta difference 0.486856 V | [projector result](../figs/pproj_readout.json) | Named Cr projector comparison, not a universal projector correction. |
| P-PLS | CONFIRMED 5/6 | [A0 result](../figs/a0main_readout.json) | Cr/Ir/Mn robust; Fe/Ru memberships rest on one terminal grid row. |
| P-FLOOR-U | SCORED MIDDLE BAND / NOT MET, 3/6 | [current interpretation](../research/s2-scientific-readout-2026-09-18.md) and [A0 data](../figs/a0main_readout.json) | Fixed endpoints, not a general physical floor; later dated interpretation supersedes stale sidecar disposition caveats. |
| P-XU | FALSIFIED overall; named-pair clause HELD 10/10 | [Xu result](../../results/s2_2026-09-18/xu_census.json) | Include the failed prevalence prediction and the positive subclause with separate denominators. |
| P-BEEF | CONFIRMED 3/3, Ladder B | [BEEF result](../../results/s5_beef_2026-09-17/readout.json) | XC-only on fixed geometries; preserve the recorded execution-before-adoption correction. |

P-SYMCOV has appendix allocation; P-CTRL validates the instrument and has no prediction body row. P-XU-SPAN, P-DIVANIS, P-BUILDER and P-LIT retain their designated appendix scope. Select compact detail to fit the report rather than treating pending branches as positive results. The [latest literature dispositions](../../results/s2_2026-09-25/full_text/reconcile/current_state.json) are an unfinished evidence workflow, not a prevalence estimate.

## 5. Figure and table workspace

| Item | Purpose | Evidence and design notes |
|---|---|---|
| Figure 1: detection mechanism and control logic | Explain a retained mirror direction, printed force history and the decision categories | Draw from actual structures/force traces and the classifier; distinguish ALL/ANY. Label inferred mechanism versus direct output evidence. |
| Figure 2: external census | Show job-class concentration and test the exposure prediction | Use xu_census.json; separate 810-header and 626-force-clause panels; retain unknowns, four exclusions and detected-lock lower bound. |
| Figure 3: U and projector response | Show descriptor/limiting-step changes within their protocols | Use A0/projector raw sidecars, with cell/spin/phase conditions and grid endpoints. Do not combine incomparable uncertainty types into one error bar. |
| Table 1: registered outcomes | Make the six body rows and negative outcomes scannable | Use the results matrix above and current ledger; retain denominators and caveats. |
| Figure 4: alloy chemical integrity and sampling | Show why admitted-site tails change proposed rankings | Use 720-site CSV and policy-specific rankings; display 109 adsorbate-intact versus 72 strict-intact sites, admitted n and uncertainty. Label descriptive calibration. |
| Figure 5: application evidence, conditional | Compare A/B against C-FG and eventually measurements | Populate after terminal readout; retain missing/fallback/mixed-recipe labels. Experimental coupon data enter only when measured under the adopted SOP. |

The [September 21 figure inventory](source-pack-2026-09-21.md) is useful navigation but is not current clearance for every plot. The early UMA parity figures are superseded; volcano_endmembers.json includes retracted DFT columns; early volcano figures do not provide current validated candidate rankings. The matched-protocol parity figure uses an older reference tier and needs explicit labeling. Prefer fresh figures from current primary data after checking their rows, rather than copying old headline panels.

## 6. Discussion prompts

- What does the complete corpus falsify, and what positive result survives that falsification?
- What alternative explanations produce small/zero lateral forces, and which does the paired header/force evidence distinguish?
- When can a converged geometry still be a saddle, a trapped electronic state, or a chemically different intermediate?
- Which sensitivity results survive the known structural/spin/cell caveats, and which are conditional?
- What does the detector miss, and how would that affect prevalence estimates?
- How does the Cr reference reversal change confidence in a Cr-rich proposed leader?
- What would the S8 test distinguish about sampling and DFT energy refinement? What can stationary-electrode current, coupon replication and an optional oxygen measurement actually establish?

Your scientific interpretation should follow the completed evidence. The broad failure benchmark has no scored truth cohort yet, so it supports no cost-saving or held-out accuracy claim. O1 certifies one boundary, not every-step production acceptance. A nominal OOH file ending in O2 plus transferred H must keep its actual chemical identity.

## 7. First writing session

1. Open the detector and Xu source files, inspect a representative locked case and an unscorable case, and make your own notes on what each demonstrates.
2. Write Methods 3.2 and 3.3 in your own words, with the atom-identification rules, quantifiers, denominators and exclusion handling.
3. Check every number in those paragraphs against the source keys and choose the actual data for Figure 2.
4. Write the corresponding Results with both the failed combined prediction and held subclause visible.
5. Add the U/projector methods and results next. Write the introduction and abstract after the evidence sequence is clear.

Keep application measurements and terminal rerun outcomes in a separate dated note until their evidence is available. The next research update can change that part of the report; it should not rewrite the historical predictions or failures.
