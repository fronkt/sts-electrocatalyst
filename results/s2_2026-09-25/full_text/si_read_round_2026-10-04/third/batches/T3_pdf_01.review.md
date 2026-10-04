# T3_pdf_01 — third read (visual completion), coverage note

Instructions: `eligibility_instructions.md` sha256 e910951616a433cecff859996be6c922d4e9f22808c1d19aa568198014913fb9 (confirmed before reading).
Page references to the page images use the PNG/PDF page number (`pNNN`). Where a journal prints different page numbers, the `where` field gives both or says "PDF p.".
Every paper: main text read in full, then the complete SI text read in full (all four have `si_complete: true`). After that I went through every main-text page on the 6-up contact sheets and opened full-resolution pages for each figure or table that bears on a criterion.

Dispositions: ELIGIBLE 0, EXCLUDE 1, NEEDS_SI 0, UNRESOLVED 3; entrant questions 3.

---

## S00358 — Karlsson, Cornell, Pettersson, Electrochim. Acta 180 (2015) 514–527 — EXCLUDE (E6)

**Inspected.**
- Main: contact sheets main_01–03, covering all 14 pages.
- Main, full resolution:
  - p002, Fig. 1 (slab and dopant positions);
  - p004, Figs. 2–3 (Hubbard-U effect on ΔE(Oc) and on d1cus−2a);
  - p005, Fig. 4 (distance parameter);
  - p006, Fig. 5 (descriptor bars, 1cus and 1br panels);
  - p007, Figs. 6–7 (ternary descriptor bars);
  - p009, Figs. 9–10 (1cus−1br energy differences; Bader charges);
  - p010, Figs. 11–13 (Bader charges; H final states);
  - p011, Fig. 14 (NEB path).
- Main, contact sheet only: p008, Fig. 8 (metal prices).
- SI: contact sheets si_01–02, covering SI pp. 1–12 (Tables 1–3, Figs. 1–8). I did not open si_03 (SI p. 13), which is references only; its text was read.

**Disposition.**
- E1–E5 are YES:
  - The study is a primary DFT screening, available online 21 August 2015.
  - E3 rests on the newly computed O adsorption energy E(Oc), used explicitly as an OER/ClER descriptor (v5 D3).
  - The models are "doped rutile TiO2" slabs ("perfect 4-layer rutile metal oxide slabs"). Rutile TiO2 is a D9 rutile-type name.
  - E5 comes from the descriptor being defined "on the (110) surface of a rutile oxide", computed on a 1x1 cell with bridge and cus sites.
- E6 is NO. Before calling it I had read the whole main text and the whole SI and looked at every main-text figure:
  - Every quantitative OER result is an E(Oc) bar compared with vertical or horizontal lines for Hansen's volcano optimum (2.4 eV) and the ClER optimum (3.2 eV): Fig. 5, Figs. 6–7, and SI Figs. 7–8.
  - The volcano apex is a universal optimum, not an η.
  - No free-energy steps, U_L or labelled η appear for any model: doped, pure TiO2 or pure RuO2.
  - Fig. 14 is an NEB barrier for H transfer, which is kinetic.
  - The full-resolution figures show axis labels ΔE(Oc)/eV, Å, eV and charge only.

**Versus passes.** Same disposition and criterion as both passes. The main-text figures changed nothing; they confirm that no plotted or labelled η exists.

---

## S11279 — Qiu et al., Chem. Eng. J. (journal pre-proof, 2020) — UNRESOLVED (E2, E6 UNCLEAR)

**Inspected.**
- Main: contact sheets main_01–04, covering all 20 pages.
- Main, full resolution:
  - p010, Fig. 2 (XRD with "PDF card No. 40-1290", indexed (110)/(101)/(211); XPS);
  - p014, Fig. 4 (Sn3Ru33O72 top and side views; free-energy diagrams for Ru0 and Ru1; intermediates).
- Main, contact sheets: p009 Fig. 1 (SEM/TEM/HRTEM); p012 Fig. 3 (LSV/Tafel/EIS/stability); p015 Fig. 5 (COHP).
- Cover page p001: received, revised and accepted dates only.
- SI, full resolution: p009 Fig. S11 (11 Sn3Ru33O72 configurations); p011 Fig. S12a–d (free-energy diagrams for Ru0, Ru1, Ru2 and Sn).

**Disposition.**
- E2 is UNCLEAR: the pre-proof prints no first-publication date.
- E4 is YES:
  - XRD peaks are "assigned to crystalline planes of rutile ruthenium oxide in Sn0.1-RuO2@NCP".
  - The DFT paragraph presents the model as a model of that sample: "To get insight on the excellent OER performance of Sn-RuO2@NCP, the DFT were performed", and the composition is "similar to the sample with the best performance". Under D1 that is a documented connection.
- E5 is YES: a RuO2(110) 3×2×1 supercell.
- E6 is UNCLEAR. The main-text figure adds one thing the passes lacked:
  - Fig. 4c (p014) prints every step for Ru0: 0.41, 0.99, **2.01**, 1.45 eV.
  - Fig. 4d prints every step for Ru1: 0.72, 1.00, **1.92**, 1.28 eV.
  - Fig. S12 repeats the largest steps for Ru0, Ru1, Ru2 and Sn: 2.01, 1.92, 2.01, 2.47 eV.
  - So the D13 and D4 condition that each compared ∆Gmax is that surface's largest one-electron step is now shown from the paper's own step values. The authors state the comparison: "The ∆Gmax value was reduced from 2.01 eV (for Ru0) to 1.92eV (for Ru1)".
  - What remains unmet is the D4 requirement of "one common documented potential". No diagram, caption or methods sentence states U; the methods only say the CHE model was used to compute ∆G.
  - The step sums (≈4.9 eV) would suggest U = 0, but D5 says the size of a value never shows its reference potential.
- A lone ∆G_RDS at U = 0, if it were documented, would not count as numeric in any case. The 178 mV overpotential is experimental.

**Versus passes.** Same disposition as both passes. The figures resolve the "largest step" condition but not the potential. I added an entrant question on whether a fully printed, author-compared ∆Gmax pair with no stated potential meets D4.

---

## S14386 — Fornaciari et al., Electrochim. Acta 405 (2022) 139810 — UNRESOLVED (E4 UNCLEAR)

**Inspected.**
- Main: contact sheets main_01–02, covering all 8 pages.
- Main, full resolution:
  - p003, Fig. 1 (schematic with "from DFT" slab inset showing *OOH);
  - p007, Fig. 5 (perturbation/DRC maps; coverage) and Fig. 6 (OER free-energy diagrams with TS, "ηOER = 0.0 V", pH 1 and 12.9).
- Main, contact sheets: p005 Figs. 2–3 (LSVs; experimental and simulated potential vs pH); p006 Fig. 4 (local pH); p008 reference list.
- SI, full resolution: p003 Fig. S3 (IrO2(110) model images); p004 Table S2 and Fig. S4a/b.

**Disposition.**
- E1–E3 and E5 are YES:
  - Four PCET steps on an IrO2(110) 2×1 slab; Table S2 gives steps of 1.40, 1.72, 1.48 and 0.32 eV at U = 0.
- E6 is YES:
  - SI Fig. S4a is a DFT surface phase diagram with an "Overpotential η (V)" axis. It labels "E = 1.72 V" and "η = 0.49 V" at the *O→*OOH boundary, which is the largest step (1.72 eV) in Table S2.
  - The RHE scale is defined in Sec. 3.2.
  - Main Fig. 6 (full resolution) shows cumulative levels (0.17, 0.66, 0.91 eV) and TS energies at ηOER = 0.0 V with no labelled η, so it is not used.
- E4 is UNCLEAR:
  - The full-resolution Fig. 1 inset and SI Fig. S3 show the slab, but nothing names the polymorph. Neither does the text, for the model or for the commercial "iridium oxide catalyst (Alfa Aesar)".
  - Only the formula, (110) and the slab cell (a = 6.34, b = 6.38, c = 40 Å) are given.
  - The single "rutile IrO2" occurrence is a reference title, ref. [36], cited for experimental pH trends. Under D6 that does not count.
  - Recognising the cell as rutile would need outside lattice constants.

**Versus passes.** Same disposition and E-verdicts as both passes. The main-text figures changed nothing: there is no rutile label, and Fig. 6 is not an η. I added an entrant question on whether the stated slab cell plus model images count as a "stated unit cell and atomic arrangement that is rutile".

---

## S30334 — Mekkad et al., J. Catal. 461 (2026) 117051 — UNRESOLVED (E4 UNCLEAR)

**Inspected.**
- Main: contact sheets main_01–03, covering all 14 pages.
- Main, full resolution: p005, Fig. 1 (free-energy profile at E = 0 and 1.23 V vs RHE, labels 0.12/1.54/1.86/1.40 eV and 0.63 eV), Table 1 and Fig. 2.
- Main, contact sheets: Figs. 3–9 (box plots, coverages, PE, DRC, eFAST, literature validation), all kinetic, and pp. 13–14 references.
- SI, full resolution: p001, Fig. S1 (HO*/O*/HOO* on IrO2(110)). The other SI pages (S2–S8: sensitivity, Tafel, box plots) were read as text and captions.

**Disposition.**
- E1–E3 and E5 are YES. The paper is available online 9 July 2026, which is inside the window.
- E6 is YES (numeric, equivalent):
  - Table 1 at E = 1.23 V vs RHE lists every step: −1.11, 0.31, 0.63 and 0.17 eV.
  - The text identifies step 3 as having "the highest positive ΔG among all elementary steps" at 1.23 V.
  - Fig. 1 labels the 0.63 eV step on the 1.23 V curve.
- E4 is UNCLEAR:
  - The only structural data are the bulk cell, a = b = 4.505, c = 3.176 Å, matched to experiment [29].
  - The only "rutile" is "in agreement with the previous theoretical studies on rutile oxides [25,36]". Arguably this places the IrO2(110) result among rutile oxides, but it reads as a remark about prior studies (D6 "generic remarks").
  - Fig. 1 and Fig. S1 carry no phase label.

**Versus passes.** Same disposition and E-verdicts as both passes. The main-text figures changed nothing for E4. Fig. 1 confirms the 0.63 eV value at 1.23 V. I added an entrant question on whether that remark plus the stated bulk cell identifies the model as rutile under D6.
