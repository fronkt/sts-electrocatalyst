# S2 operating decisions and execution specification — 2026-09-18

This record completes the remaining S2 operating choices under the instruction to continue. It carries forward `research-decisions-2026-09-16.md`, docs/43 A9.3–A9.5, the September 4 silentgate rulings, and `s2-operating-decisions-2026-09-16/p-builder.md`. Historical records stay intact. No result, personal signature, or completed execution is asserted here.

Commit and push this record before the new literature search or coding begins. P-BUILDER has its separate complete input/code boundary described below. Source records, exclusions, unknowns and failed calculations remain visible in every readout.

## Xu repair and source identity

**Choose A9.5 item 1 option (a): no Xu deck re-runs or structural repairs in this S2 program.** The census measures the constraints present in the deposited outputs. The frozen magnetic moment and the QE-version/ultrasoft translation would introduce a different scientific comparison requiring its own validation. Neither changes the value of the complete output census or its gas-independent U spans. The in-house relaxation program supplies direct structural validation on systems whose settings are controlled here.

The separate H2/H2O reference calculations below are newly built isolated-molecule calculations; they do not alter or replace any Xu slab result. They support only the registered floor-margin difference.

Use the local Zenodo corpus whose zip MD5 is `e193c56cf17c6d98827bbb19752d04b3`, with the existing verification against 6,989 mirror paths/sizes and 815 output git-blob hashes. Recheck the selected output bytes against that manifest before analysis. Record the extraction root and software commit, retain the raw archive, and write results outside the corpus tree. Population changes or mismatched bytes are failures to resolve before scoring, not reasons to silently choose a different corpus.

## P-XU: preserve the registered population and clauses

The population is all 810 Eads outputs from the ten named metals in docs/43 A9.3.1. Report all headers, calculation types, U values, spin settings, total-magnetization settings, force thresholds, ionic-step counts and missing values per deck. Do not generalize the settings of a sampled deck to the population.

Keep the distinct computations separate:

1. Header clause: more than one reported symmetry operation in at least 90% of 810 outputs; falsified below 75%.
2. Final-force clause: at least one exactly zero lateral component under the settled ALL-adsorbate-atoms rule in at least 90% of the eligible adsorbate population. Start from 630; remove only registered UNIDENTIFIED and NO_FORCE_BLOCK cases, naming their counts on the face. Preserve numerator and original/eligible denominators together. Falsified below 75%. Single-block outputs use that block and carry their calculation type and single-block flag.
3. Direction clause: the named four-layer `OH-relax`/`OOH-relax` pair has different singleton locked lateral sets on at least 8 of 10 metals; falsified at at most 4 of 10. The locked set uses every printed step and the intersection over identified adsorbate atoms. Missing or unscorable pair members remain named in the ten-metal accounting and supply no positive success. Report seen and blind metal subsets explicitly.

The descriptive 42-output OH/OOH direction map per metal marks MIXED behavior and names the deviating jobs. P-A2, the both-lateral-components O-relaxation row, stays descriptive. Do not replace either scored clause by silentgate's broader LOCKED label: header, final-step force and all-step direction questions have different numerators.

For the combined statement, all three confirmation clauses must hold. Any registered falsification clause triggers the falsification branch; otherwise report `SCORED — MIDDLE BAND / NOT MET` with the three separate outcomes. Distinguish incomplete evidence from measured failure; no missing output becomes an exact-zero observation. The numerator implementation and aggregate verdict receive an independent raw-output check.

## P-XU-SPAN and isolated-molecule decision

Score all 680 ladder outputs: ten metals, 17 U values from 0 to 8 eV in 0.5 eV steps, and four states at each rung. For each complete usable rung compute `E_OOH - E_OH` and `E_O - E_OH`; their across-U ranges equal the registered spans of `c_M` and `deltaG2` because the same gas and correction constants cancel. Parse the total energies and termination/convergence evidence, retaining all failed or incomplete states.

A metal's primary full-ladder span requires all 17 relevant state pairs to be usable. An observed range from fewer rungs is a labeled lower bound, never substituted for the primary span. Report missing-rung metals in the fixed ten-metal denominator. `span_U(c_M) > 0.20 eV` on at least five metals meets the registered criterion; fewer than three meets falsification only when missing evidence cannot lift the count to three. Otherwise use middle-band or incomplete-evidence wording. `span_U(deltaG2)` remains descriptive. Publish the paired complete-rung count and any lower bound next to the full-ladder status.

**Run the two GBRV molecule jobs.** Build H2 and H2O with the H/O pseudopotential bytes used by Xu's selected slab decks, verified from deck names and available deposit/pseudopotential metadata; write the exact filenames, source URLs, checksums and valence/XC identities into the prospective launch manifest. Do not substitute the SSSP or S5 gas references. If exact identity cannot be established, report this half as DEFERRED with the unresolved identity; the gas-independent span readout proceeds.

Use a 12 Å cubic cell, Gamma point, PBE, `assume_isolated='martyna-tuckerman'`, `ecutwfc=40 Ry`, `ecutrho=500 Ry`, `nspin=1`, fixed occupations, no symmetry enforcement, and full molecular ionic relaxation. Starts: H2 bond length 0.74 Å; H2O O–H length 0.9572 Å and angle 104.52 degrees, centered in the box. Require `conv_thr=1e-10 Ry`, force threshold `1e-4 Ry/bohr`, at most 100 ionic steps and 300 electronic iterations per step. Preserve input, executable and pseudopotential identities and all termination evidence. Both jobs must pass finite-energy, electronic-convergence and ionic-convergence checks; `JOB DONE` alone does not pass.

The launch budget ceiling is 64 allocated core-hours total, using at most 16 ranks and a two-hour limit for each of the two molecules. Treat this as a resource ceiling, not a runtime estimate. A failed job is diagnosed before any new attempt; no automatic parameter sweep is authorized by this record. Record realized cost. These are matched-reference calculations at the deposited cutoff/box convention, not a new convergence study.

With both references valid, report only each applicable external chain's **floor margin**, with the correction dependence over the same declared delta interval where the OOH correction enters. Do not publish an absolute Xu-metal overpotential. Keep failed-chain and missing-reference accounting explicit. No new confirmation threshold is introduced for this descriptive column.

## P-DIVANIS: exact curve, population and failure accounting

Use `results/research_decisions_2026-09-16/divanis_selection.json` and its pinned text SHA-256 `88bfcda9a5e70da10d3b2565af7cc09b7377578e4aac4dd5d9a74b42c0bd8bda`. Preserve the 38 row identities, source order, repeated material rows, unlegended b suffix and full source values: Man 26, Mom 11, Frydendal 1. This is the historically selected lexical population; its label does not certify all entries as stable rutile electrodes.

Apply the settled September 16 R2–R7 choices. Denominator is always 38; numerator requires both `eta < 0.60 V` and floor margin at most 0.050 eV, using exact source-decimal arithmetic where possible. Counts at least 10 meet the registered confirmation threshold; counts at most 3 meet falsification; counts 4–9 are `SCORED — MIDDLE BAND / NOT MET`. Show all three article-specific rates beside the whole selected population. The whole ESI has 24 articles; that is not the selected-population article denominator.

Use the full closed interval `delta = corr_OOH - 0.35 eV` from 0 to 0.10 eV. Enumerate every CHE active-step crossing and every root of the eta and margin predicates, then evaluate all endpoints, exact roots and intervening open intervals. Equality is excluded at the strict eta threshold and included at the margin threshold. Use exact decimal/rational breakpoints or disclose a deterministic tolerance with independently verified boundary decisions. The curve is the primary result; no privileged single-delta headline is introduced. Display step ties without arbitrary reassignment.

Enumerate negative fourth-step free energies throughout the interval and retain those rows. They are consequences of the imposed CHE cycle, not proof that the material or an entire study is physically impossible. The historical high-coverage Cr arithmetic is a labeled external-table reconstruction. Keep model-phase and electrode-performance claims separate. Independent recomputation must use the raw table values and a distinct calculation path, not simply reload the primary result JSON.

## P-BUILDER: execute the complete prepared specification

Adopt the unchanged prepared `s2-operating-decisions-2026-09-16/p-builder.md` and its matching manifest. All ten code files, source structures, slab/configuration files, denominators, decision JSON and decision document must be in the pushed boundary commit before blind symmetry is computed. Keep the disclosed rutile arm labeled non-blind.

| Family | Configurations per adsorbate | HELD minimum for O and OH separately | FALSIFIED maximum | Middle counts |
|---|---:|---:|---:|---|
| rutile(110) | 10 | 9 | 5 | 6–8 |
| perovskite(001) | 5 | 5 | 2 | 3–4 |
| spinel(001) | 13 | 8 | 6 | 7 |
| fcc(111) | 4 | 4 | 2 | 3 |

OOH retained count zero and O/OH configuration-wise agreement are construction checks; a violation voids the family until explained. Pooled counts remain descriptive. The atomate historical/default-input audit is a separate result, never multiplied into a population rate. Its prepared gate and both scope checks passed on the inspected source records. The blind execution command from `src/` is `python -m s2.p_builder.run_census --allow-blind --out ../results/s2_2026-09-18/p_builder_census.json`.

## P-LIT: prospective search and coding choices

**Population and window.** Include primary research articles first published from 2011-01-01 through 2026-09-18 inclusive that calculate OER on a rutile-oxide (110) surface and report a computational-hydrogen-electrode overpotential in the article or supporting information. Include comparative computational studies irrespective of whether the authors call them high-throughput screens. Exclude reviews, purely experimental work, studies without a (110) rutile calculation, and studies that do not report a CHE overpotential. A precursor preprint and its journal article count once, using the journal version when within the window. Resolve online/print dates by first publication date and preserve both in the evidence record.

**Databases and exact query strings.** Execute all four literal queries separately in both OpenAlex works search and Crossref works `query.bibliographic`, with the date window above:

```
rutile oxygen evolution
RuO2 oxygen evolution
IrO2 oxygen evolution
rutile oxide computational hydrogen electrode
```

Fetch every available result page, preserving request parameters, retrieval time, pagination, raw responses and failures. No top-N cutoff. Use DOI for primary deduplication, then normalized title/year/first-author for records without DOI; preserve all source identifiers and any conflicting records. If a database limits enumeration, record the limit and leave search completeness unresolved instead of relabeling the returned subset as exhaustive. API-specific syntax, escaping and page cursors may be adapted to documented interfaces without changing these literal queries or the date window.

**Complementary retrieval fixed now.** Add the already-known eligible candidates from Xu 2015, Man 2011, the Divanis 2020 ESI's source list and the two 2026-08-15 literature syntheses. From each included paper inspect its references once for additional primary studies meeting the same rule; no forward-citation or recursive reference expansion in this primary sample. Candidate discovery is recorded before method fields are coded. Freeze the deduplicated candidate and inclusion/exclusion list, with reasons and unresolved-access entries, before primary coding. Any later extension is labeled a separate search update.

**Fields.** Preserve the three registered binary reporting questions: explicit symmetry setting reported; an imaginary-mode/vibrational stability check reported; a magnetic-state check reported. Carry the already-adopted fourth descriptive field, raw computational outputs deposited. Yes requires a primary-text/SI statement or an identifiable deposited artifact; record its page/section/URL and a short supporting excerpt. For symmetry, a named code or default alone is insufficient. For imaginary modes, routine force convergence alone is insufficient. For magnetism, a statement that calculations are spin-polarized alone is insufficient; require a comparison of initial/order/moment states or an explicit check of the adopted magnetic state. This field measures reporting, not whether the calculation is physically correct or whether the test was necessary for a particular material.

No means that readable article and available methods/SI were searched and no qualifying statement was found, with the inspected files and sections recorded. Unavailable full text or a missing methods/SI component needed to decide is UNKNOWN, never No. The recorded binary field is left empty with a reason for UNKNOWN cases. Raw-output deposition requires an accessible deposit of actual calculation input/output or equivalent machine-readable result artifacts; a data-availability sentence without accessible artifacts is recorded separately and does not establish Yes.

**Prospective proportion.** Predict **more than 80%** of included papers report none of the three method checks. This adopts a transparent, stringent hypothesis for the newly frozen search; it is not a value estimated from the as-yet uncoded sample. It is partly informed by the already-read methods disclosed in docs/43 A9.3.6, so the entire audit is not described as blind. The fourth field has no threshold.

With all papers coded, a proportion strictly greater than 0.80 is HELD; a proportion at most 0.80 is FALSIFIED and the broad “invisible to standard checks” sentence is dropped. The denominator is all included papers. If some papers are UNKNOWN, report exact lower and upper proportions for “none of three”: known-none/N and (known-none + potentially-none-unknown)/N. HELD requires the lower bound to exceed 0.80; FALSIFIED requires the upper bound to be at most 0.80; otherwise the outcome is INCOMPLETE EVIDENCE. A known Yes in any of the three fields rules out “none” even if another field is unknown. Do not infer missing papers' codes or change the denominator to make a threshold pass.

Keep coding time, source locators and evidence beside each row. A second independent pass reviews every included row and exclusion, resolving discrepancies against the primary sources. Automated pre-screening never substitutes for reading the methods. Historical authorship instructions are not evidence that the current scientific analysis was personally performed or signed by the user.

## Execution and completion evidence

The frozen analysis order is corpus identity and source checks; P-XU and spans; full Divanis curve; P-BUILDER after its pushed boundary; P-LIT after this pushed search boundary; molecular preparation and bounded execution after exact pseudopotential matching. Independent raw-data recomputation accompanies each numerical readout. A single scientific summary then re-tests the detector/census-led claim against the results that actually passed, preserving middle bands and unresolved evidence. The expensive Cr relaxation program runs separately under its own launch record.
