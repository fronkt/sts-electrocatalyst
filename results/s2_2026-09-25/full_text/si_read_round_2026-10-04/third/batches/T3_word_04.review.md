# T3_word_04 — third read (visual completion), coverage note

Instructions hash checked before reading: `sha256(eligibility_instructions.md) = e910951616a433cecff859996be6c922d4e9f22808c1d19aa568198014913fb9` (matches).
For every paper: main text read in full (12,000-character chunks), SI reading text read in full, main-text contact sheets (`contacts/main_01.png`, `main_02.png`) viewed for every page, decisive figure pages opened at full resolution and the relevant panel cropped and upscaled 3× (crops are in the session scratchpad only, not in the corpus). Page PNGs are 893 × 1191 px, so panel numbers were read from the upscaled crops.

## S31037 — 10.1016/j.cej.2026.181481 — ELIGIBLE (departs from both passes)

**Inspected:** main pages 1–12 (both contact sheets); p. 6 at full resolution, with Fig. 4 free-energy panel cropped; p. 7 Fig. 5 (H3O+ desorption on "The (110) surface of Mg-RuO2", not OER); p. 2 Fig. 1 (XRD/Raman). SI: contact sheets word_01–word_04, including Fig. S23/S24 (AEM intermediates *OH, *O, *OOH on RuO2(110) and Mg-RuO2(110) slabs) and Fig. S25.

**Figure finding:** the panels of Fig. 4 are printed a, b, c, e, f, but the caption runs (a)–(e). The free-energy diagram the caption and text call "Fig. 4e" is printed as panel "f". It has two potential sets: the upper curves on the left axis "Free energy U=0 V (eV)", marked "U = 0 V", and the lower curves on the right axis "Free energy U=1.23 V (eV)", marked "U = 1.23 V". The labels are colour-coded by surface: Mg-RuO2 (blue) 1.64 eV at U = 0 and 0.41 eV at U = 1.23 V; RuO2 (magenta) 2.00 eV at U = 0 and 0.64 eV at U = 1.23 V. All four labels sit on the shaded O*→OOH* step. Every intermediate (H2O, OH*, O*, OOH*, O2) is plotted on a numbered axis. The step heights I read are below; the paper prints none of them except the labelled ones:
- RuO2 at U = 0: about 0.63, 0.94, 1.98 and 1.37 eV.
- Mg-RuO2 at U = 0: about 1.1, 1.3, 1.63 and 0.9 eV.

So O*→OOH* is visibly the largest step for both surfaces at both potentials. This is what the text calls the RDS ("For both RuO2 and Mg-RuO2, the rate determining step (RDS) is the transition from *O to *OOH").

**Disposition reasoning:** E1–E5 are YES, as in both passes. E4 rests on the authors' own statement that the computed models "were built with a rutile lattice structure". E5 rests on the (110) slab statement and Fig. S24. The passes left E6 UNCLEAR because the step values and the potential could not be seen. I now take E6 YES under D4 (relative equivalent):
- The authors themselves state the comparison: 1.64 eV on Mg-RuO2, "0.36 eV lower than that on RuO2 surface (2.00 eV), thus elucidating the higher OER activity".
- The two values sit at one common potential that the diagram documents: U = 0 V.
- The steps are one-electron AEM steps, with ΔGU = −eU.
- The reference and conditions are the same for both surfaces.
- The diagram plots every step, so I could check that the compared step is each surface's largest.

I did not use the U = 1.23 V labels (0.41/0.64 eV) as a numeric equivalent. The paper's only computational reference statement is Eq. (3), ΔG = ΔE + ΔZPE − TΔS + ΔGU + ΔGpH with ΔGU = −eU. It gives neither a reference electrode nor a value for ΔGpH, so the D5 RHE-scale check is not met. That leaves eta_form `relative` + `equivalent` rather than `numeric`.

Inconsistency noted, not corrected: the RuO2 U = 1.23 V curve does not match its U = 0 curve (2.00 − 1.23 = 0.77, but 0.64 is printed). The Mg-RuO2 pair is consistent (1.64 − 1.23 = 0.41). Neither curve contradicts O*→OOH* being the largest step.

**Entrant question:** two judgements are not settled by the instructions:
- Do plotted but unlabelled step heights satisfy D4/D13's "every step given" for an "RDS" label?
- Does Eq. (3) satisfy D5, so that the U = 1.23 V labels would count as numeric?

If plotted heights do not count, E6 falls back to UNCLEAR and the disposition to UNRESOLVED.

## S31125 — 10.1016/j.jpowsour.2026.241435 — UNRESOLVED (agrees with both passes)

**Inspected:** main pages 1–8 (both contact sheets); p. 7 at full resolution, with Fig. 5 cropped; p. 4 Fig. 1–2 (XRD with (110) reflection label, XPS, SEM/EDS, HRTEM); p. 6 Fig. 3 (electrochemistry); p. 7 Fig. 4 (PDOS). SI: contact sheets word_01, word_02, and the full-size previews of image8.emf and image9.emf (Table S8).

**Figure finding:** main Fig. 5 shows only the energy levels:
- RuO2: 0.000 / 1.232 / 2.933 / 3.521 / 4.920 eV.
- Mo-17-RuO2: 1.192 / 1.974 / 3.479 eV, and 2.431 / 3.923 eV on the LOM branch.

The figure also prints "η = ΔGmax/e −1.23", "ηRuMoLOM = 262 mV" and "ηRuMoAEM = 275 mV". It has no structure image and no facet or Miller index. Table S8 (image9) gives the Mo-17-RuO2 AEM steps 1.192, 0.782, 1.505 and 1.441 eV, so the largest is *O→*OOH at 1.505 eV. The image8 table labels the structures only as "RuMo slab vacancy" and similar. The only "(110)" anywhere is the XRD reflection of the synthesized powder (main Sec. 3.1, Fig. 1a).

**Disposition reasoning:** E4 is YES: the model is "A rutile RuO2 cell (P42/mnm)". E6 is YES: η_AEM = 0.275 V is labelled as a theoretical overpotential (direct) for that model. E5 stays UNCLEAR. Neither the main text (figures included) nor the SI states which facet carries the OER intermediates. Fig. 5, the figure the passes hoped might name the facet, does not. With the SI complete, the disposition is UNRESOLVED. The figure confirms the passes; nothing changes. No entrant question, because the instructions settle this case (E5 UNCLEAR when no facet is stated).

## S31137 — 10.1016/j.jcat.2026.117169 — UNRESOLVED (agrees with both passes)

**Inspected:** main pages 1–11 (both contact sheets); p. 3 at full resolution, with Fig. 1c,d cropped; p. 4 Fig. 2; p. 5 Fig. 3; p. 7 Fig. 4; p. 8 Fig. 5. SI: all 13 contact sheets (word_01–word_11, word_wide_01, word_wide_02). These include the WMF equation previews:
- the AEM steps *+H2O→*OH+H++e− (ΔG1) through *OOH→O2+H++e− (ΔG4);
- the LOM steps;
- ΔG = ΔEDFT + ΔZPE − TΔS + Δ∫CpdT;
- TOF = TOF0 exp(−ΔGPDS/kBT).

They also include Fig. S1–S25 (Fig. S2's representative slabs are unlabelled).

**Figure finding:** Fig. 1c plots −ΔGPDS (eV) against ΔE(*Ocus). Its legend lists the PDS steps (*Ocus+H2O→*OOH+H++e−; *OH→*Ocus+H++e−) and the point categories Ru, Co and Ni CUS site. The labelled "RuO2" point sits near −1.88 eV, consistent with Table S2's ΔG(AEM)PDS = 1.884 eV. The Co CUS points lie near the apex (about −1.48 to −1.53 eV; apex −1.43 eV). Fig. 1d is the LOM analogue, with RuO2 near −2.65 eV (Table S2: 2.666 eV). No panel carries an η axis, an η label, an η arrow or a U_L. No other main or SI figure shows η: Figs. 2–5 and S4–S25 are composition, TOF-metric, ΔΔG, distribution and parity plots.

**Disposition reasoning:** E1–E5 are YES. All slab models are "five-layer rutile (110) slabs". RuO2(110) and the doped (110) surfaces carry DFT-computed AEM intermediates (Fig. S3 scaling data; Table S2). For E6, the paper gives:
- ΔGPDS values: RuO2(110) 1.884 eV, and the volcano apex 1.43 eV, which is excluded as a universal optimum;
- a caption formula η = ΔGPDS/e − 1.23 V, with the statement that −ΔGPDS "gives the same activity ranking".

Under v4 and D12 a lone U = 0 ΔG at the largest step that I would have to convert does not count, and a formula is "instructions on how to compute η". Under D4 the authors never state a comparison of the PDS values of identified surfaces; they say only that Co-containing CUS sites lie "near the AEM volcano peak" with "favorable AEM energetics". The figures confirm what the passes inferred and add no labelled η.

I keep E6 UNCLEAR rather than NO. Whether an author-presented −ΔGPDS volcano, explicitly tied to η as the same ranking, is a graphical/relative η is a judgement the instructions do not settle. That judgement is the entrant question. No change from the passes.
