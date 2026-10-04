# T3_word_02: third read (visual completion), coverage note

Instructions: `eligibility_instructions.md` v5, sha256 `e910951616a433cecff859996be6c922d4e9f22808c1d19aa568198014913fb9` (confirmed before reading).
Output: `T3_word_02.out.jsonl` (4 lines, input order). Format check (brief step 11): `ok`.

Summary: ELIGIBLE 3 (S21177, S21253, S22127), EXCLUDE 1 (S23135, E6), NEEDS_SI 0, UNRESOLVED 0. Entrant questions: 1 (S23135).

How I read each paper: the main text in full (12,000-character chunks) and the SI text in full. Word SI tables and references were read in compact print form, and the Pandoc reading aid was compared against the SI paragraph text. I checked every excerpt segment against the source text with a print-only substring check. Segments taken from figure images are cited by page and panel because they are not in the text files. Full-resolution page PNGs were enlarged by cropping only (PIL, print/image only). A plotted level was never used as a reported value.

---

## S21177 (10.21203/rs.3.rs-3710432/v1): ELIGIBLE (same disposition as both passes; one field changed)

**Inspected:** all 20 main pages on contact sheets `main_01`–`main_04`. Pages 1–13 are text and references. The figures are on pp. 14–20. Full-resolution pages: p. 15 (Fig. 2, XRD card label in Fig. 2e: "RuO2 PDF#71-2273"), p. 18 (Fig. 5a–g with caption) and p. 20 (Fig. 7a,b with caption). I did not open the SI media because the SI text settles E3–E6.

**Disposition:** The figures were not available to the passes. The text file ends at the reference list, so the figure captions were also missing from the text. Now that I have the figures:
- Fig. 5a (p. 18) is the four-step CHE diagram at "U = 0" for RuO2, Zn@RuO2 and CoZn@RuO2.
- Fig. 5e plots "Theoretical η (V)" for each model: CoZn@RuO2 ≈0.43 V, Zn@RuO2 ≈0.52 V, RuO2 ≈0.65 V. The caption reads "(e) theoretical overpotential". The text on p. 9 points to it ("a decrease in the theoretical overpotential of the OER (Fig. 5e)").

These values match the limiting potentials in the text minus 1.23 V (1.66/1.75/1.88). E6 YES stands. RHE scale: SI paragraphs 47–48 ("ΔG = ΔG0 − eURHE"). E4: "tetragonal RuO2 … group P4_2/mnm" (space group = rutile) on the characterized sample, connected to the model by "constructed with reference to XRD and HRTEM".

**Departure:** Both passes had `eta_derivation` = equivalent. Fig. 5e shows the authors label the CoZn@RuO2 quantity a theoretical overpotential, so under D14 the derivation is `direct`. `eta_form` stays `numeric` because of the 1.66 eV limiting potential in the text.

**Observation (no effect on the verdict):** Fig. 7a,b (p. 20) plots η_OER ≈0.10 V (CoZn@RuO2), ≈0.13 V and ≈0.19 V (RuO2), which do not match Fig. 5e. This is recorded in the note.

## S21253 (10.1016/j.gee.2023.12.003): ELIGIBLE (pass1 ELIGIBLE, pass2 UNRESOLVED; the main-text figure settles the disagreement)

**Inspected:** all 12 main pages on contact sheets `main_01`, `main_02` (Fig. 1 on p. 941: card/HRTEM labels and the Fig. 1g caption "rutile Pd0.08Ru0.92O2"; Fig. 2a XRD "RuO2 40-1290"; Fig. 3; Fig. 5). Full-resolution p. 9 (journal p. 945, Fig. 4a–e), with Fig. 4e enlarged 4× and 6×. Pixel profiles of the Fig. 4e lines and y-axis ticks (scale 21.1 px/eV) were used only to check which curve each label sits on. SI images `image24`–`image26` (Figs. S24–S26: models, no numbers).

**What Fig. 4e shows:** two sets of curves.
- Red curves are marked "U=0 V". The 1.82 eV (RuO2, dashed) and 1.74 eV (Pd0.08Ru0.92O2, solid) arrows are on the *O→*OOH step.
- Black curves are marked "U=1.23 V". The *O→*OOH step carries 0.59 eV (arrow to the dashed RuO2 *OOH level) and 0.51 eV (arrow to the solid Pd0.08Ru0.92O2 *OOH level).

This answers pass2's objection that "the common potential of the Fig. 4e diagram is not stated in text": the 1.74/1.82 eV comparison is explicitly at U = 0 V. More directly, the diagram reports each surface's potential-determining step at U = 1.23 V. The authors identify *O→*OOH as the PDS "for these samples", and the CHE/RHE statement is in Sec. 2.6. E6 is therefore YES as a D5 equivalent (numeric, 0.51 eV for Pd0.08Ru0.92O2(110)), and the D4 relative comparison at U = 0 also holds.

**Note for adjudication:** I am not using this for the verdict, because a plotted level is not a listed step value and I am not allowed to compute differences from it. Read off the plot, the Pd0.08Ru0.92O2 *OOH→O2 step is ≈1.78–1.81 eV at U = 0 (≈0.55–0.57 eV at U = 1.23 V). That is comparable to, or about 1 px above, the labelled 0.51 eV PDS. RuO2(110) shows no such tension: the plotted last step is ≈1.72 eV against a PDS of 1.82 eV. RuO2(110) also meets E3–E6 (0.59 eV at U = 1.23 V; models "of the electrocatalysts based on the RuO2 structure"; RuO2 NSs indexed to rutile-phase RuO2). So the disposition does not depend on this point, and I set no entrant question. The reported model is Pd0.08Ru0.92O2(110), with the alternative named in the note.

**Departure:** I agree with pass1 on the disposition. Pass1 used E6 relative + equivalent. I use the numeric U = 1.23 V value labelled on the figure, which pass1 could not see.

## S22127 (10.1016/j.ensm.2024.103341): ELIGIBLE (same disposition as both passes; the figure confirms it)

**Inspected:** all 9 main pages on contact sheets `main_01`, `main_02` (Fig. 1; Fig. 2a XRD label "RuO2 JCPDS: 01-088-0322" with (110)/(101)/(200)/(211); Fig. 3; Fig. 5; reference pages). Full-resolution p. 6 (Fig. 4a–h), with Fig. 4g and 4d enlarged 4×. I did not open the SI media.

**What Fig. 4g shows:** the Gibbs diagram for "Ru site on Mn-RuO2" and "Ru site on RuO2" at both "U = 0 V" and "U = 1.23 V".
- "0.50 V RDS" is drawn on the *OH→*O step of Mn-RuO2. In the U = 1.23 V curves that step is the largest uphill step (≈+0.5 eV; the later steps are ≈+0.2 and ≈+0.15 eV).
- "RDS 0.72 V" is drawn on the *OOH→*+O2 step of RuO2.

The text labels 0.50 V an overpotential, so E6 is YES, numeric and direct, and the figure removes pass1's caveat that Fig. 4g was not viewable. E4: space group P42/mnm (rutile type) on both samples; the doped model is a "5×2 supercell of RuO2" with Mn on (110). E5: OER "on the (110) plane of Mn-RuO2 and RuO2" (SI paragraph 27).

**Departure:** Pass2 put an `eta_note` on the RuO2 value: the 0.72 V is called "desorption of O2*", while the SI scheme splits *OOH→*O2 + H⁺ + e⁻ from *O2→* + O2, and Fig. 4g draws them as one step. That value belongs to the RuO2 comparison model, not to the reported Mn-RuO2 Ru-site model. For the reported model the 0.50 V is consistent with the U = 1.23 V curve, so `eta_note` is null. The Fig. S32 caption says "Mn sites", but the main Fig. 4g legend and the text put the OER on Ru sites. This is recorded in the note.

## S23135 (10.1016/j.apcatb.2024.124382): EXCLUDE on E6 (both passes UNRESOLVED/E6 UNCLEAR; this is a departure; entrant question set)

**Inspected:** all 11 main pages on contact sheets `main_01`, `main_02` (Fig. 1 STEM/HRTEM with RuO2(110)/(101) and TiO2 labels; Fig. 2; Fig. 3; Fig. 5; references). Full-resolution p. 7 (Fig. 4a–h), with Fig. 4d and Fig. 4e enlarged 3×. All SI media on contact sheets `word_01`–`word_03` (Figs. S1–S17: XRD, zeta potential, TGA, TEM/STEM, XPS, Raman, CV/ECSA, EIS, pH dependence, in-situ Raman). The Fig. S13 preview (`image13.tiff.png`, AEM/LOM adsorption models without numbers) was also enlarged. The main text and the whole SI were read before calling E6 NO. The SI has no step values, step equations, overpotential or limiting potential, and the reading aid adds only the same tables.

**Models:** NL-RuO2-250 = RuO2(101)/TiO2(101), so E5 is NO for it. NS-RuO2-250 = RuO2(110)/TiO2(101) is the only (110) model. It meets E3–E5 ("rutile RuO2" lattice in Sec. 2.7; Ru sites "exposed in the RuO2 (110)-oriented direction").

**What Fig. 4e shows (NS, "@U = 0 V"):**
- An AEM (green) four-step path. Its *-O→*-OOH step is labelled 2.57 eV and is the visibly largest AEM step. It is a lone U = 0 step, not labelled RDS, PDS, η or U_L, never discussed in the text, and never compared by the authors with another surface. It does not count.
- A LOM (blue) path *+H2O → *-OH → *-O → VO-*-OO → VO-* + O2 → OH-* → *. Its 1.91 eV arrow spans *-O → VO-*-OO, the lattice-oxygen coupling step.

**The authors' comparison:** "LOM … high energy barrier (1.91 eV), 0.32 eV larger than that of NL-RuO2-250". This sets the NS LOM coupling step against the NL AEM RDS (1.59 eV). The paper itself contrasts LOM with CPET: "In the AEM pathway, oxygen evolves through a series of four coupled proton-electron transfer (CPET) reactions, whereas, in the LOM pathway, lattice oxygen is directly coupled with an oxygen intermediate to produce oxygen gas". The figure shows the 1.91 eV value is exactly that direct-coupling step. This fails D4's requirement that all steps be conventional one-electron CHE steps (the "different electron counts" exclusion). The other D4 condition also cannot be met: NL's 1.59 eV is labelled only "RDS", and NS's 1.91 eV is only an "energy barrier". The 1.91 eV is therefore a generic "energy barrier" outside any qualifying comparison. No other η exists for the (110) model in the main text or the SI, so E6 is NO.

**Departure:** Both passes said UNCLEAR without the figure. They did not know which step the 1.91 eV belongs to, or that the NS AEM value appears only as a U = 0 ΔG. Because D4 also says "if these conditions cannot be established, E6 is UNCLEAR", I set an entrant question on whether this counts as a clear D4 failure (EXCLUDE) or as unestablished (UNRESOLVED). EXCLUDE is my best reading.
