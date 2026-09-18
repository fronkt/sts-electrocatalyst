# S2 scientific readout — 2026-09-18

The completed numerical audits support a bounded detector-and-census result. **P-XU and P-DIVANIS are FALSIFIED; the four P-BUILDER families are HELD; P-XU-SPAN has INCOMPLETE EVIDENCE.** These outcomes answer different questions and are not pooled into an overall success rate. The Xu molecular-reference branch is DEFERRED and P-LIT discovery/coding is incomplete. This is a dated scientific readout and early claim-scope re-test, not a claim that the entire S2 program or September 20 disposition is finished.

The governing population, thresholds and failure rules are in [docs/43 A9](../43-prereg-week1-factorial.md) and the [September 18 operating decisions](s2-operating-decisions-2026-09-18.md). Historical sampling remains disclosed; passing tests or independent arithmetic does not make previously seen data blind.

## Xu: the high-exposure prediction fails, with a clear job-class boundary

The [primary census](../../results/s2_2026-09-18/xu_census.json) verifies the registered archive MD5 and all selected input/output bytes against the mirror manifest. The [independent verifier](../../results/s2_2026-09-18/xu_independent_verification.json) reparsed 810 outputs and 810 inputs with a separate parser, returned PASS, and found no differences in the checked numerators, forces, energy usability or spans.

| Registered clause | Observed result | Outcome |
| --- | --- | --- |
| Headers reporting more than one symmetry operation | 70/810 = 8.64%; no unknown headers | FALSIFIED |
| Final-force ALL-adsorbate-atom lateral-zero rule | 50 successes, 496 known failures, 80 unknown among 626 retained outputs; original denominator 630, four NO_FORCE_BLOCK exclusions, zero UNIDENTIFIED exclusions | FALSIFIED |
| Different singleton all-step lateral sets on the named four-layer OH-relax/OOH-relax pairs | 10/10 metals; 4/4 seen, 6/6 blind by record, 5/5 blind by availability | HELD |

For the force clause, the success fraction is bounded by 50/626 to 130/626 (7.99%–20.77%), even allowing every unknown to be positive. The 80 retained unknowns have no eligible unconstrained adsorbate atoms under the adopted `if_pos` exclusion rule. They remain in the denominator; they are not zero-force successes or measured failures. The four absent-force outputs are Cr OOH U=2.5, Mn OOH U=2.5 and 6.0, and Mo OOH U=7.5, all in the two-layer ladder.

The important descriptive stratification is exact:

| Output class | Headers >1 operation | Final-force successes / original adsorbate population | Other force accounting |
| --- | ---: | ---: | --- |
| Two-layer U ladder | 0/680 | 0/510 | 456 known failures; 50 retained unknowns; four excluded absent-force outputs |
| Other two-layer jobs | 0/60 | 0/60 | 40 known failures; 20 retained unknowns |
| Four-layer jobs | 70/70 | 50/60 | 10 retained unknowns |

Every detected two-witness LOCKED adsorbate output is in the four-layer class. The earlier four-layer sample therefore cannot estimate corpus-wide prevalence. All ten descriptive 42-output OH/OOH direction maps are MIXED: the named-pair result does not extend uniformly across the jobs for a metal. The descriptive P-A2 row is 20/210 O relaxations with both lateral components zero, with no unknowns.

Four named OOH-relax pair members (Cr, Mn, Pt and Rh) fail the separate energy-usability gate. Their printed force histories still score the registered constraint question; the 10/10 pair result is not evidence for ten converged minima. More generally, absence of a LOCKED classification never establishes that a coordinate was freely explored, and the census measures neither saddle points nor errors in the original paper's conclusions. The registered falsification branch rules out a field-wide high-exposure claim. The measured external instances remain reportable at their actual rates and job-class scope.

## Xu U spans: incomplete primary ladders, substantial descriptive lower bounds

Energy usability requires finite matched energy/convergence witnesses, exactly one normal completion marker, no recorded severe failure, and the appropriate BFGS convergence witness for a relaxation. A normal completion marker alone does not pass. Of 680 ladder outputs, 665 pass; 15 remain unusable with reasons preserved. This is numerical usability, not an independent test of vibrational stability or retained adsorption chemistry.

The paired differences cancel the common gas and correction constants. A primary span requires all 17 relevant state pairs; an unusable bare or O state does not invalidate an otherwise usable OH/OOH pair. The fixed denominator is ten metals.

| Metal | Usable OH/OOH pairs | Full-ladder c_M span (eV) | Incomplete-ladder observed lower bound (eV) |
| --- | ---: | ---: | ---: |
| CrO2 | 16/17 | — | 0.563070 |
| IrO2 | 17/17 | 0.112461 | — |
| MnO2 | 11/17 | — | 1.016347 |
| MoO2 | 15/17 | — | 0.038465 |
| NbO2 | 17/17 | 0.093621 | — |
| PtO2 | 17/17 | 0.104110 | — |
| ReO2 | 16/17 | — | 3.742887 |
| RhO2 | 17/17 | 0.138479 | — |
| RuO2 | 17/17 | 0.074604 | — |
| TiO2 | 17/17 | 0.224703 | — |

Only TiO2 exceeds 0.20 eV with a complete primary ladder: one confirmed metal, four incomplete, and a possible maximum of five. The registered result is **INCOMPLETE EVIDENCE**, neither HELD nor FALSIFIED. Cr, Mn and Re already show observed ranges above 0.20 eV, so the result must not be summarized as evidence that only one metal is U-sensitive. Those ranges remain labeled lower bounds and do not replace the required full-ladder spans. The independent readout reproduces every pair count and range. The descriptive deltaG2 span is complete for nine metals; Mo has 15/17 pairs and a 0.285881 eV lower bound.

No Xu slab repair or rerun is part of this program. The frozen magnetic settings are declared modeling choices. [Exact original H/O pseudopotential bytes were not recovered](../../results/s2_2026-09-18/xu_molecules/README.md), so neither reference molecule was submitted and no Xu floor-margin column is reference-complete. No absolute Xu-metal overpotential is reported.

## Divanis: the registered near-floor population is small throughout the correction interval

The [verified exact readout](../../results/s2_2026-09-18/divanis_verified/readout.md) finds **1/38 (2.63%)** qualifying rows at every point of the full closed delta interval [0, 0.10] eV. Membership and the FALSIFIED verdict are invariant. The article-specific rates are Man 1/26, Mom 0/11 and Frydendal 0/1; these are three selected articles, not 24 independent articles. The same Man RuO2 row, `divanis-si2-L108`, qualifies throughout.

The numerator requires both eta <0.60 V and excess above each row's exact scaling floor <=0.050 eV. Exact roots, endpoints, ties and intervening intervals were checked with rational arithmetic. Independent raw-table recomputation passed 570 exact row/sample comparisons and 23 independently constructed probes. Repeated rows and the unlegended suffix remain in the fixed denominator; the lexical selection is not a certification of stable rutile electrodes.

Seven rows have a negative fourth CHE step through delta=0.01 inclusive, and eight above it. They remain included. A negative step under the imposed cycle is not evidence that a material or paper is physically impossible. The floor identity and its in-house uses survive; widespread near-floor occupancy in this selected published population does not. No preferred OOH correction is inferred.

## Builder: geometric retention is reproducible, with software scope attached

The [primary census](../../results/s2_2026-09-18/p_builder_census.json) passes the pushed-boundary and input-manifest checks. The [independent lattice-operation enumeration](../../results/s2_2026-09-18/p_builder_independent.json) verifies all 96 configurations without pymatgen, spglib or the production census functions, with no operation-count or retention mismatches.

| Family | O retained | OH retained | Bent OOH retained | Registered O/OH outcome | Disclosure |
| --- | ---: | ---: | ---: | --- | --- |
| rutile(110) | 9/10 | 9/10 | 0/10 | HELD / HELD | Non-blind reproduction |
| perovskite(001) | 5/5 | 5/5 | 0/5 | HELD / HELD | Blind arm |
| spinel(001) | 10/13 | 10/13 | 0/13 | HELD / HELD | Blind arm |
| fcc(111) | 4/4 | 4/4 | 0/4 | HELD / HELD | Blind arm |

All construction checks pass. These rates describe the specified slab/site/adsorbate geometries, not the prevalence or energetic cost of constraints in deployed workflows. Bent OOH's zero count is a construction check. Pooled O/OH/OOH rates are descriptive only.

The separate [atomate gate](../../results/s2_2026-09-16/p_builder_prestate/atomate_gate.json) passes: the inspected default adsorption input set introduced `ISYM=0` on 2018-05-25 and retained it across the 11 inspected default-branch file versions through the pinned head, unless overridden. The earlier workflow's admitted pymatgen chain was checked across 43 releases. This supports the dated, source-bounded software statement; it does not turn the geometric census into a field-wide exposure estimate or establish what every user ran.

## F8 and remaining evidence

The [updated F8 clearance](f8-clearance-2026-09-16.md) verifies Sun, Reuter and Scheffler's published RuO2(110) symmetry-breaking statement. Its physical example concerns hydrogen/surface hydroxyl on the stoichiometric surface; it does not establish an OOH-specific effect or a software symmetrization mechanism. Structural claims carry the individual cleared/excluded dispositions in that record, including the model-phase limit for rutile PtO2.

The +0.40 eV OOH correction remains a repository convention without a verified readable primary-source attribution in this audit. The pooled 3.18 +/-0.12 eV intercept is qualitative only; the asserted ~0.12 V code floor remains withdrawn. Bibliographic regeneration and remaining live citation defects are enumerated by F8 rather than silently treated as corrected everywhere.

P-LIT discovery is incomplete. The [dated retrieval amendment](s2-literature-retrieval-amendment-2026-09-18.md) preserves the original incomplete streams, uses exhaustive OpenAlex discovery plus the registered known/reference sources, and reserves Crossref for DOI validation. No coded proportion or HELD/FALSIFIED literature verdict exists. Unavailable methods remain unknown; no broad sentence about checks being absent or calculations being unchecked follows. The Cr DFT validation program is separate and supplies no completed physical-validation result to this readout.

## What can be re-tested now for September 20

[docs/43 A9.4](../43-prereg-week1-factorial.md) and [docs/87](../87-claim-sentence-constraints-2026-09-05.md) require a claim supported by landed S1, S2 and S6 work, with detector/census first, floor movement second and coverage conditionality third. The complete Xu numerical census now permits the detector-led scope to be tested against measured outcomes, including a failed prevalence prediction. It does not license postponing the falsification branch until other compute arrives.

Candidate scope wording for the dated re-test, with the numerical tables above attached:

> The tested Quantum ESPRESSO output detector identifies symmetry constraints concentrated in the four-layer jobs of the complete 810-output adsorption population; the registered high-exposure prediction fails when the full header and adsorbate-force populations are counted separately.

This candidate is scoped by the evidence and adopted body allocation below and remains subject to the September 20 re-check. A claim about the constraint's energetic consequences belongs to separately scoped in-house evidence. The old 0.223 V / 25-times / 9 meV headline in docs/87 remains refuted; S4 projector results do not substitute for S6. The Divanis result supports an exact-floor analysis with sparse near-floor occupancy, not a widespread-floor claim. Builder retention supports a construction mechanism, with the atomate symmetry-disabling history beside it.

The early re-test retains the bounded detector/census claim above. Claims requiring P-LIT, matched Xu gas references or completed Cr basin validation remain outside it. The September 20 re-check remains scheduled; a positive external prevalence claim, a repaired Xu energy claim, a selected superior HEA composition and a field-wide reporting claim are unsupported.

## Current S6 reconciliation and six-row allocation

The [banked A0 readout](../figs/a0main_readout.json) and [crossing brackets](../figs/a7_2_crossings.json), read with the September 3 dispositions in docs/43, preserve **P-PLS CONFIRMED at 5/6** on the fixed-geometry U grids. Cr, Ir and Mn are the three robust carriers; Fe and Ru membership each depends on one terminal row. This is an in-house parameter-sensitivity result with its own six-metal denominator, not an estimate of an external corpus error rate.

**P-FLOOR-U remains SCORED — MIDDLE BAND / NOT MET at 3/6.** Its registered endpoint metric is |delta c|/2. It is not an unrestricted change in the exact floor: the two-step overpotential decomposition requires limiting step 2 or 3, and Mn/Fe high-U endpoints cross that scope. The general exact floor remains max(c, 4.92-c)/2 - 1.23 V. Later reviewed Ru pseudopotential controls are also MIDDLE ([September 17 readout](ru-pp-readout-2026-09-17.md)); they do not rescue the primary threshold. Historical Ti-spin and Ru-AFM pending notes are superseded by the later September 3 ruling and docs/60, rather than repeated as current blockers.

The [P-SYMCOV readout](../../runs/s3/readout/p_symcov_2026-08-24.md) contains no registered aggregate branch verdict: aggregation and the meaning of “large” remain unsettled. Its historical pending-job table is not a current queue report. No general coverage-consequence claim enters this re-test.

Under the authorized continuation, the A9.4 displacement is now **P-SYMCOV to the appendix, P-XU to the body**. The resulting six body rows are P7, P-PROJ, P-PLS, P-FLOOR-U, P-XU and P-BEEF. P-CTRL remains a gate with no row. P-XU retains its FALSIFIED combined result and the held 10/10 directional subclause together; the positive subclause does not replace the failed prediction. P-XU-SPAN, P-DIVANIS, P-BUILDER and P-LIT retain their existing appendix allocation regardless of outcome. This records placement after the numerical outcomes were known and changes no scientific threshold or verdict. The owning dated entries are in docs/43 and docs/45 section D.
