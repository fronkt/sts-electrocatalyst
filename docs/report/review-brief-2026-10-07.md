# Project review and report starting brief — 2026-10-07

This file is a research inventory and writing worksheet for Frank's own report. It changes no protocol, prediction, threshold, sample list or experimental decision. Laboratory statements are recorded in the October 7 melt plan; the underlying correspondence was not independently checked here. Queue status below comes from a dated local receipt, not a live query.

## Evidence ready for the report

The October 5 roadmap puts the completed detector/corpus investigation (S1/S2/S6) at the center. The materials lane connects composition screening, MLIP adsorption predictions, structural/site-integrity audits, DFT checks and a prospective five-alloy electrochemical comparison. S8 can supply later evidence; completed computational results already support report development.

The scientific claim of record is in docs/45-error-ledger.md, section D, September 21 claim re-test. Its supporting counts remain distinct:

| Evidence | Number and status | Boundary | Source |
|---|---|---|---|
| Complete Xu corpus | 810 outputs; 70/810 nontrivial symmetry headers | Header exposure differs from a detected force lock | docs/research/s2-scientific-readout-2026-09-18.md |
| LOCKED outputs | 50, all four-layer: 20 O, 20 OH, 10 OOH | Lower bound; job-class association does not isolate a thickness effect | docs/research/claim-evidence-audit-2026-09-19.md |
| Final-force population | 626 = 50 successes + 496 known failures + 80 unknown; four original members lack force blocks | 50/626–130/626 = 7.99%–20.77%; unknowns are not negatives | S2 scientific readout |
| Detector controls | Positives 9/9; QE negatives 0/11; selected OC20 negatives 0/500 | Fixed samples do not establish a universal zero false-positive rate | Claim-evidence audit |
| External hypotheses | P-XU and P-DIVANIS FALSIFIED; named-pair subclause HELD 10/10 | Four named OOH-relax members (Cr, Mn, Pt, Rh) fail energy-usability QC; exposure is not an overpotential consequence | S2 scientific readout |
| U and uncertainty | P-PLS 5/6 CONFIRMED; P-FLOOR-U 3/6 MIDDLE BAND / NOT MET; P-BEEF 3/3 CONFIRMED | Preserve endpoint, functional, projector and ordering qualifications | Claim audit; docs/research/s5-beef-readout-2026-09-17.md |
| Site census | Six compositions × 120 MPA-0 sites =720; 551 OOH DESORPTION endpoints; 109 adsorbate-intact sites, 72 strict-intact | Descriptive calibration; no experimentally validated alloy order | docs/95-census-2-3-readout-2026-09-13.md and linked review |

Elected body rows: P7, P-PROJ, P-PLS, P-FLOOR-U, P-XU and P-BEEF. P-SYMCOV belongs in the appendix. P-CTRL supports method validation without its own body row. P-XU-SPAN, P-DIVANIS, P-BUILDER and P-LIT keep appendix roles. The 0.223 V / 25-times / 9 meV headline remains withdrawn. An unscored literature branch does not strengthen the claim.

## S8: present design

The five-alloy stage-1 document remains **proposed, not frozen, not deposited**. Fe25's addition and disk dimensions are recorded decisions; the entire freeze has not thereby been adopted. The melt plan and weigh sheet retain pending preparation/measurement values.

| Batch-1 alloy | Exact nominal at.% | A: best-of-12 η, V | B: adsorbate-intact linear p10 η, V [90% interval]; retained sites |
|---|---|---:|---|
| Cu8Cr23Mn35Co34 | Cu7.887 Cr22.634 Mn34.993 Co34.485 | 0.756 | 0.384 [0.362,0.404]; 16/120 |
| Ni31Cr29Cu5Mn35 | Ni31.115 Cr29.187 Cu5.169 Mn34.529 | 0.440 | 0.473 [0.440,0.835]; 8/120 |
| Fe25Co25Ni25Cr25 | Fe25 Co25 Ni25 Cr25 | 0.453 | 0.554 [0.468,0.834]; 19/120 |
| Cu26Ni9Cr31Co33 | Cu25.780 Ni9.393 Cr31.466 Co33.362 | 0.479 | 0.502 [0.449,0.703]; 13/120 |
| Cu22Fe30Co32Mn15 | Cu22.116 Fe29.974 Co32.425 Mn15.484 | 0.796 | 0.831 [0.797,0.887]; 38/120 |

Source: docs/research/s8-stage1-freeze-proposal-2026-10-07.md. A is the historical August 5 prediction, commit 96b1cb1. B is a proposed prospective comparison based on an already inspected census. These are CHE descriptors. The intervals cover conditional sampling uncertainty, not MLIP error or a physical fixed-current mapping.

Proposed K1 asks whether Cu8 is more active than Ni31 and Fe25 (B) or less active than both (A); mixed/unresolved remains a valid outcome. K2 asks whether Cu22 is least active. Full orders and Spearman correlations are exploratory, n=5. Strict-intact p10 is secondary and not tested; Cu26 leads it. Strict retention ranges from 3 to 33 across the census.

Proposed preparation: one 10 g ingot per alloy, +4% Mn, four Ar arc-melt flip/remelt passes, 1,050 °C/24 h Ar homogenization and quench. Total nominal feedstock is 50.331 g including over-charge. SEM-EDS tolerance is ±2 at.% per element, one remelt allowed, then retain/flag the measured composition. These processing values still require confirmation.

Recorded disk decision: 5.00 mm diameter ±0.02 mm; 1.5 mm thick ±0.1 mm as cut; face 0.196 cm² (approximately 1.96 mA at 10 mA cm⁻²). Per alloy: ≥3 mounted disks, one bare disk, slice remainder for SEM-EDS/XRD. Three disks from one ingot measure coupon variation; they do not independently estimate ingot/batch variation.

Recorded Tackett-lab requirements:

- Stationary coupons accepted through a 24 mm port, span ≤20 mm.
- Epoxy covers back/edges, leaving one immersed face; silver-paint/wire back contact, continuity checked before potting, wire emerges above electrolyte.
- Coupons arrive mounted. The earlier Pine-cylinder proposal is superseded and archived.
- IrO₂ available and will run as prescribed. The proposed campaign also includes a blank each bench day. PhD students conduct electrochemistry.

Pending lab details:

- Signed risk assessment and supervisor names/dates: an unsigned assessment file exists. Four alloys contain Cr.
- Actual melt/instrument slots, mounting responsibility, shipping/completion date and available potentiostat channels.
- Final explicit activation/polish, 1 M KOH, Hg/HgO treatment, counter electrode, EIS resistance, 90% iR compensation, 5 mV s⁻¹ LSV and analysis criterion.
- Freeze primary is η at 10 mA cm⁻²; Tackett mentioned 1 mA cm⁻². The plan proposes retaining 1 mA cm⁻² as secondary, not exchanging the primary.
- ≥3 randomized coupons/alloy across ≥2 days proposed. Twice pooled coupon SD is the pending pairwise rule, not a p-value/confidence interval.
- Fifteen 12 h holds total 180 channel-hours. The one-coupon/alloy durability alternative is not elected.
- O₂/FE method unresolved. EC-MS might accept a bare 5 mm disk; holder thickness/availability pending. Cu8 is proposed. Tafel slope does not itself quantify O₂ or separate Cr-oxidation charge from oxygen-product charge.

Batch 2 is conditional on arm-C nomination of Ni34Fe6Cu29Co31, with Cu22 and optionally another batch 1 alloy remelted as bridges. Optional sixth batch 1 melt remains unconfirmed. No third batch planned. October 21 fallback and October 25 working cutoff remain proposals/calendar targets, distinct from an elected report lock.

## Arm C: approved fixed-geometry DFT

C-FG plus Ni34 and best-site add-ons is approved. It holds census structures fixed, replacing MLIP energies with spin-polarized PBE+U energies. It establishes neither DFT-relaxed minima nor ground-state electronic solutions. The two MLIP p10 support-site η values are combined using their MLIP weights; a single usable chain is flagged SINGLE_SITE. Best-site add-ons do not replace the primary supports.

Recipe: atomic Hubbard projector, PBE/SSSP, 80/640 Ry, MV 0.01 Ry, MP U values, 4×2×1 mesh, conv_thr 1e−6, local-TF β 0.3, fresh atomic+random starts, 128 ranks / -nk 8, 126-iteration and 2.5 h limits. Acceptance retains COMPLETE/converged/agreed-energy and IEEE rejection rules.

Local terminal evidence, results/arm_c_2026-10-07/readout.json:

- Arrays 21165189/21165190 finished; 10,876.7 SU recorded.
- 33/64 main SCFs accepted; 28 ceiling stops; 3 IEEE exits rejected; 4/16 complete site chains.
- Ni31 C=0.7677656 V, Cu22 C=0.9419554 V, Ni34 C=1.2805586 V, all SINGLE_SITE. Cu8/Fe25/Cu26 have NO_VALUE at primary supports.
- Cu8 additional best site s20/2 is complete, η=0.6209516 V. It does not replace its p10 supports.
- K1/K2/Ni34 nomination NOT_EVALUABLE_UNDER_ARM_C.
- Fe25 ndim16 probe accepted in 51 iterations; high-spin stopped. ndim16 selected for ceiling retries.

The single full rerun covers all 31 failed states plus 2 converged-slab recipe controls. Array 21176478 was released at 22:43:46 UTC on October 7; the release receipt saw PENDING, a dated observation. Rerun ceiling 10,560 SU; first-round actual plus rerun ceiling 21,436.7 SU, within 23,680 SU approved. Controls check whether mixing history reaches a different electronic state. Second-attempt failures remain failures.

Chronology correction: earlier melt/design paragraphs say no alloy DFT chain/overpotential exists. They describe the pre-arm-C baseline. The October 7 readout now contains complete chains and partial values; it still has no final five-alloy DFT order.

## Writing worksheet for Frank

Suggested 18-page body budget leaves 2 pages for necessary appendix detail. Title/abstract/bibliography separate. This is a planning suggestion, not manuscript text.

| Part | Pages | Questions to answer independently | Evidence to open |
|---|---:|---|---|
| Introduction |1.5| What scientific problem connects adsorption screening to hidden structural/electronic constraints? What was the testable question? | Original experiment record; personally read primary papers |
| Definitions/design |2| What is a lock/header/force block/usable energy? Which hypotheses preceded outputs? Which branches are calibration/exploratory? | docs/43, docs/45, S1/S2 protocols |
| Methods |3| How are controls, coverage, calculations, CHE, U/projector comparisons and failures reproduced? What is each observation unit? | S1/S2/S5 methods and recipes |
| Detector/corpus results |4| What happened against each primary prediction and denominator? Which expectation failed? Which outputs remain unknown? | Claim audit; S2 readout; current body rows |
| Numerical/site results |3| Which error classes changed geometry/energy/descriptors/orders? How do model/admission change the ranked population? | Repairs; S6; docs/95/review; S8 ranking review |
| Materials comparison |1.5| What was predicted before measurement? If data land, what were actual composition, processing, independent units and outcomes? | S8 freeze, accepted C readout, later lab records |
| Discussion |2| What do corpus/controls establish? Which alternatives remain? How does model surface differ from electrode? | Recorded limits; Frank's interpretation |
| Conclusion |0.5| Which completed finding is supported without pending work? | Frank's synthesis |

Keep principal counts and negative findings assessable early. If S8 stays incomplete, bound/omit its prospective details; the completed computational investigation carries the report. First writing exercise: independently explain why 70/810 and 50/626 are different measurements, then describe one positive control, one negative control and one retained unknown.

## Display plan

The September 21 source pack is an inventory, not a publication-ready reference list. Older figure status travels with each artifact.

| Display | Source | Purpose/status |
|---|---|---|
| Detector/corpus figure | S1 controls; S2 readout/claim audit | Separate exposure, force denominator, unknowns and job classes; plot pending |
| Primary hypothesis table | Six elected body rows/docs45 + readouts | Prediction/observation/denominator/verdict/limit together; current evidence assembly |
| Integrity/admission display | docs95 B1/B2; readout_full/per_site.csv | OOH outcomes, retention and conditional descriptors; label calibration; raw tables exist |
| S8 A/B table | Five-alloy freeze/support sites | Makes K1 reversal and shared anchor visible; status proposed |
| S8 measured comparison | Later accepted C readout + coupons | Actual data/uncertainty/controls/failures; pending |
| CHE robustness example | results/che_box_case_study_2026-09-05/continuous_che_counterexample.svg and audit; docs84 correction | Existing PNG/SVG; limited supporting/appendix role |
| Matched parity | docs/figs/parity_matched.png + sidecar/docs38 | Historical endmember comparison; recheck reference tier/status |

uma_dft_parity.png and uma_oc22_parity.png are superseded. volcano_endmembers.json carries retracted DFT columns per docs73. Round 1 UMA volcano plots are historical screening displays. pourbaix_mno2.png uses experimental formation free energies, not DFT. Article-page images under SI review are reading aids, not project scientific figures.

## Official report requirements checked October 7

The public 2027 [Research Report Guidelines](https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Research-Report-Guidelines.pdf), first page, state: “The Student Researcher is required to write the paper without the use of generative AI (ChatGPT or other programs).”

Format facts: ≤20 body pages including appendices; title first/abstract second/bibliography last excluded from limit; single column; 1.5 spacing; 1-inch margins; text at least visually equivalent to Times New Roman 11 pt; bottom-right numbering after abstract; PDF ≤4 MB. Every display/table needs its own citation. Content/presentation review is allowed; the entrant retains their own writing. These are format facts, not an additional research gate.

The [2027 AI Usage Chart](https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/AI-Usage-Chart.pdf) classifies initial plan/abstract/paper writing as unacceptable: “Never acceptable. This must be the independent work of the student.” It allows idea development and limited grammar/syntax feedback on an existing student abstract under stated conditions; it disallows an AI starter bibliography. This worksheet supplies evidence locations/questions/display organization, with no initial manuscript sections, conclusions or reference-list entries.

## Review completion

- Current five-alloy freeze, melt plan, weigh sheet and full arm-C design read.
- Initial C readout checked directly; complete best-site chains distinguished from primary supports.
- Rerun release receipt checked; no live queue claim inferred.
- Current claim ledger/census reviews checked; denominators and withdrawn claims retained.
- Public official PDFs checked through web tools, without browser sessions, proxies or keyed APIs.
- No scientific protocol, solver job or external message changed.
