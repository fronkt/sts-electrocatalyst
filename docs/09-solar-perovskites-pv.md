# 09 — Solar / Perovskites / Photovoltaics

**Bottom line up front:** This is the single richest hybrid lane for an STS ceiling-break — ML-screen a lead-free (Sn-based) or additive/passivation composition, spin-coat it in the Purdue glovebox, and beat a baseline on the *real* bottleneck (stability), not just peak PCE — but air-sensitivity and 3.5-month reproducibility risk are real, so scope tightly and pick a narrow, defensible target.

## Cheat-sheet: PV technologies

| Technology | Record / typical PCE | Key tradeoff |
|---|---|---|
| Crystalline Si (single-junction, the baseline) | **27.3%** certified HBC cell (LONGi, 2024); ~29.4% Auger/SQ practical ceiling; commercial modules ~22–24% | Mature, cheap, durable (25–30 yr). Near its physical limit — little room to "beat" without tandems. |
| Halide perovskite, single-junction (MAPbI₃ / FAPbI₃ / mixed-cation-anion) | **26.7–27.3%** certified (USTC; UNSW–Soochow ~27%) | Stunning PCE rise in ~15 yr, cheap solution processing — but **stability** (moisture/thermal/light/ion-migration) + **lead toxicity** + hysteresis are the open problems. |
| Lead-free Sn perovskite (FASnI₃ / CsSnI₃ / (PEA,FA,Cs)Sn(I,Br)₃) | **16.65%** certified (triple-cation 2D/3D, U. Queensland 2025); 14.5% certified centimetre-scale | Non-toxic-ish, but Sn²⁺→Sn⁴⁺ oxidation makes them *even more* air-sensitive than Pb. Novelty-rich, lower ceiling. |
| Lead-free Bi/Sb / double perovskite (Cs₂AgBiBr₆, Cs₃Sb₂I₉) | ~**6.4%** experimental record (Cs₂AgBiBr₆); much higher in indoor/LED light | Wide bandgap (~1.8–2.0 eV) kills outdoor PCE; genuinely good fit for **indoor PV** (IoT), which is where recent ISEF/STS lead-free work has landed. |
| Perovskite–Si tandem (2-terminal) | **34.85%** certified (LONGi, 2025) — first flat-plate device above the single-junction SQ limit | Highest PCE of any lane, but needs *both* sub-cells + current-matching; fab is far beyond a HS glovebox. |
| All-perovskite tandem | **29.1%** certified (Nat. Mater. 2025); 31.4% claimed (SolaEon) | Uses a fragile narrow-bandgap Sn-Pb bottom cell — stability is the bottleneck. Fab is hard. |
| Organic PV (OPV, non-fullerene acceptors) | **~20%** certified single-junction (2024); 14.5% certified module | Flexible, lightweight, tunable. Lower PCE + outdoor photostability limits; strong indoor/flexible niche. |
| Quantum-dot PV (CsPbI₃ / perovskite QD) | **18.1%** certified (UNIST); 18.3% claimed (2025) | Solution-processable, tunable bandgap via size; ligand chemistry and stability are limiting. This is the exact Jolene Cao (STS '25 Finalist) family. |
| Thermoelectric bridge (CsSnI₃ Seebeck/ZT) | ZT ≈ 0.11–0.14 measured at RT; ~0.63 predicted at 1000 K | Not PV, but the *same* spin-coated Sn-perovskite film harvests waste heat — a clean "dual-function" story (the Tahani Ahmed ISEF '22 framing). Low ZT vs. real TE materials. |

*All numbers sourced below. Records move fast — the canonical reference is the peer-reviewed **Solar Cell Efficiency Tables (Version 66, 2025)** and the NREL Best Research-Cell Efficiency Chart.*

## Where the real bottleneck is

The field is **not** efficiency-limited any more — single-junction perovskites are within ~1 percentage point of single-crystal silicon, and tandems have broken the single-junction Shockley-Queisser limit. The unsolved problems, in priority order:

1. **Operational stability / degradation.** Perovskites decompose under the four field stresses — **moisture, heat, light (UV), and electrical bias** — and uniquely suffer **mobile-ion migration** that drives reversible "burn-in," phase segregation, and hysteresis. MAPbI₃ in humid air decomposes to PbI₂ + CH₃NH₃I → HI + methylamine. Lifetimes are benchmarked by the **ISOS protocols** (ISOS-D dark, ISOS-L light-soak, ISOS-T thermal cycling, ISOS-LT damp-heat, ISOS-V bias) and the **T₈₀** metric (time to 80% of initial PCE). Interface engineering has pushed reported T₈₀ from ~80 h to ~530 h in lab studies — i.e., still orders of magnitude short of silicon's 25-year warranty. **This is the bottleneck a student can actually move and measure.**

2. **Lead toxicity.** PbI₂ is water-soluble (~340 mg/L — ~11 orders of magnitude more soluble than PbS/PbSe), so leakage from a cracked module is bioavailable. This drives two research thrusts: **lead-free chemistries** (Sn, Bi, Sb, double perovskites) and **lead-sequestration encapsulation** (e.g., cyclodextrin/polyacid complexes retaining 97% PCE and <14 ppb Pb leakage after water scouring). Lead-free is the more novel, more "high-school-appropriate-safety" angle.

3. **Hysteresis & reproducibility.** Solution-processed films vary batch-to-batch; J-V scan-direction hysteresis (an ion-migration fingerprint) inflates reported PCE. **Reproducibility is itself now a publishable problem** — the Jan-2026 *Nature* autonomous closed-loop paper exists precisely because manual perovskite fab is irreproducible.

4. **Scaling.** Lab champion cells are ~0.05–0.1 cm²; modules drop several points. Out of scope for a HS project, but worth one honest sentence.

## Feasibility verdict (3.5-month runway)

**Doable, with disciplined scope.** A Purdue lab with a glovebox, spin-coater, solar simulator (AM1.5G), and XRD/PL/UV-Vis is exactly the standard perovskite toolchain. What's realistic vs. not in Jul–early Oct 2026:

- **Realistic:** spin-coat perovskite *films* (not necessarily full devices) of one composition family; characterize structure (XRD), bandgap (UV-Vis Tauc + PL), and **track degradation** of films vs. a baseline under controlled moisture/light/heat (a homemade ISOS-D/L-style aging test with periodic PL/XRD/UV-Vis). A **film-level stability study beating a baseline additive** is the safest high-yield deliverable.
- **Stretch but achievable:** full single-junction devices with a solar simulator PCE + EQE, *if* the lab's device stack is already dialed in and a grad-student mentor hands over a working recipe. Getting a *new* recipe to reproducible >15% from scratch in 3.5 months is the classic trap.
- **Risky / avoid:** tandems (need two sub-cells + current matching), large-area modules, anything requiring a brand-new fab line.

**Highest-EV path = HYBRID + lead-free + stability.** ML narrows a composition/additive space → you fabricate the top 1–3 candidates + a literature baseline → you measure that your ML-picked variant degrades slower (and/or has a better/targeted bandgap). Lead-free (Sn or Bi/Sb double) doubles as a **safety story** for judges and sidesteps Pb-handling concerns — though note Sn²⁺ oxidation makes Sn films *harder* to keep alive, so an inert-atmosphere glovebox is non-negotiable for that route. **Fort Wayne Metals is a weak fit for the absorber itself** but is a legitimate supplier of **metal back-contacts/electrodes, fine-wire interconnects, or encapsulation foils** — mention it for completeness, don't build the project around it.

## Where ML adds value

| Angle | Toolchain / data | Difficulty |
|---|---|---|
| **Bandgap / formation-energy screening** (find a stable, defect-tolerant lead-free composition with target gap) | XGBoost / GNN on curated ABX₃ / double-perovskite sets (e.g., 1,185-cubic-ABX₃ and ~3,864-ABX₃ datasets); reported XGBoost R²≈0.82–0.96. Your reusable ML-property stack applies directly. | Low–Med |
| **Stability / defect-tolerance prediction** (rank candidates by predicted degradation, tolerance factor, decomposition enthalpy) | ML on Goldschmidt/octahedral factors + DFT decomposition energies; smaller, noisier labels — this is where novelty lives. | Med–High |
| **Generative composition / structure proposal** (your generative crystal-structure stack proposes new mixed-cation/anion or double-perovskite candidates, then filter) | Generative CSP → DFT/ML relaxation → property filter. Strong "ML designs it" narrative; validate the *winner* in the wet lab. | Med–High |
| **Additive / passivation-molecule discovery** | Active-learning + quantum modeling over molecular libraries (cf. the 5ANI passivator found by closed-loop ML in *Nature* 2026). | High |
| **Bayesian optimization of fabrication** (spin speed, anneal T/time, antisolvent, additive ratio → maximize PCE or T₈₀) | Your BO stack on a small DOE of real lab runs — closes the loop, directly attacks reproducibility. **This is the most STS-distinctive ML angle because the data is *yours*.** | Med (data-limited) |
| **ML for tandem current-matching** (optical/electrical sub-cell modeling) | Transfer-matrix + surrogate model; computational-only, no fab. | Med |

## Ranked project framings

### 1. Lead-free Sn-perovskite stability via ML-guided additive — *HYBRID* (recommended)
- **Hypothesis:** An ML-ranked additive/passivator (or cation-mix ratio) suppresses Sn²⁺→Sn⁴⁺ oxidation and ion migration, so the film's T-tracked degradation is measurably slower than a FASnI₃ baseline at matched bandgap.
- **Toolchain & data:** XGBoost/GNN property model + Bayesian optimization over additive ratio & anneal conditions on your own DOE; literature labels for pre-screen. Generative stack optional for cation-mix proposals.
- **Novelty hook:** Most Sn-perovskite work chases peak PCE; you optimize *for stability* with a closed ML→fab→measure loop on a lead-free system — combines the Tahani Ahmed (CsSnI₃) and Belal (lead-free indoor doping) lineages with a modern BO twist.
- **Fabricate + measure:** Glovebox spin-coat films; XRD (phase purity), UV-Vis Tauc + PL (bandgap, trap states), then ISOS-D/L-style aging with periodic re-measurement; report T₈₀ (or PL-intensity half-life) vs. baseline. Devices if recipe permits → PCE + EQE.
- **STS-ceiling read:** **Top 300 very plausible; Top 40 if the device works and the ML genuinely picked the winner** out of a defensible search space. Stability beat + lead-free safety story is exactly the Finalist profile.

### 2. ML-designed lead-free double perovskite for **indoor** PV — *HYBRID*
- **Hypothesis:** A doped/alloyed Cs₂AgBiBr₆ or Cs₃Sb₂I₉ variant (ML-selected B-site dopant) shifts bandgap toward the indoor-light optimum and out-performs the undoped baseline under LED illumination.
- **Toolchain & data:** Bandgap/formation-energy ML screen over double-perovskite space → DFT confirm top dopants → fabricate.
- **Novelty hook:** Wide bandgap is a *liability* outdoors but an *asset* indoors; reframing the lane's weakness as the application is the clever move (directly mirrors Belal's ISEF '25 EGSD 3rd-place dual-doping indoor PV, but with your generative/BO stack and a different dopant).
- **Fabricate + measure:** Spin-coat, XRD/UV-Vis/PL; measure under calibrated white-LED (lux-defined) rather than only AM1.5G — easier, safer, less air-sensitive than Sn.
- **STS-ceiling read:** **Top 300 realistic.** Lower outdoor PCE caps the "wow," but the *defensible niche + lead-free + ML design* is a clean, complete story; Top 40 needs a strong device + a surprising dopant finding.

### 3. Bayesian-optimization "mini self-driving lab" for reproducible perovskite films — *HYBRID*
- **Hypothesis:** BO over fabrication parameters reaches a target (PCE or T₈₀) in far fewer runs than a grid/OFAT baseline, *and* tightens run-to-run variance.
- **Toolchain & data:** Your BO stack driving a small physical DOE; the response variable is measured in-lab. Reproducibility (variance reduction) is a co-primary metric.
- **Novelty hook:** Rides the hottest 2025–26 theme (autonomous/closed-loop perovskites, *Nature* 2026) but at HS scale — and reproducibility is a recognized open problem, so even a modest result is meaningful.
- **Fabricate + measure:** Iterative spin-coat batches; PCE/EQE or film-quality proxies (PL FWHM, XRD coherence) each round; report optimization curve + variance vs. baseline.
- **STS-ceiling read:** **Top 300 plausible; Top 40 risky** — judges may see "optimization, not discovery." Strongest as a *component* of framing 1 rather than standalone.

### 4. Generative crystal-structure search for new lead-free absorbers — *COMPUTATIONAL-ONLY (with optional wet-lab cherry on top)*
- **Hypothesis:** A generative CSP + multi-property filter surfaces previously unreported stable, defect-tolerant, ~1.3–1.6 eV lead-free candidates.
- **Toolchain & data:** Your generative stack → ML/DFT relaxation → bandgap/stability/tolerance-factor filter → shortlist; validate *one* by spin-coating if time permits.
- **Novelty hook:** "We computationally discovered a candidate the field hasn't tried" — your strongest *pure-ML* differentiator; leans on your unique generative asset.
- **Fabricate + measure:** Optional single-candidate film confirmation (XRD phase + bandgap match).
- **STS-ceiling read:** **Top 300 solid; Top 40 only if a candidate is experimentally confirmed** — pure computation rarely cracks Finalist in materials without a wet-lab tie-in.

### 5. Dual-function Sn-perovskite: PV + thermoelectric harvesting — *HYBRID (ambitious)*
- **Hypothesis:** One ML-tuned CsSnI₃-family film usefully does both — absorbs light *and* shows a measurable Seebeck/power factor — beating a baseline on a combined figure.
- **Toolchain & data:** ML to co-optimize bandgap (PV) and carrier concentration (Seebeck); same film, two measurements.
- **Novelty hook:** Explicit "two energy-harvesting modes from one cheap film" story (the Tahani Ahmed ISEF '22 framing, modernized with ML co-optimization).
- **Fabricate + measure:** PV side as above; TE side needs a Seebeck rig (ΔT + thermovoltage) and conductivity — added equipment risk. CsSnI₃ RT ZT is only ~0.11–0.14, so frame as proof-of-concept, not a TE record.
- **STS-ceiling read:** **High-variance.** Novel framing helps Top 40 *if* both measurements land; the doubled experimental burden in 3.5 months is the danger — only pursue if the TE rig already exists.

## How to stand out

- **Pick stability, not peak PCE, as the headline metric.** Everyone chases efficiency; a clean, honest **T₈₀ / ISOS-style degradation beat over a named baseline** is more defensible, more novel, and more measurable in a HS timeframe.
- **Make the ML *load-bearing*, not decorative.** Judges punish "I ran XGBoost then did unrelated chemistry." Show the ML *chose* the exact composition/additive/parameters you fabricated, with an ablation/baseline proving the choice mattered.
- **Quantify uncertainty and reproducibility.** Replicate films, report error bars, show J-V hysteresis index, and disclose batch variance. This alone separates Top-40 rigor from Top-300.
- **Own the safety/sustainability narrative.** Lead-free + a sentence on encapsulation/leakage framing reads as mature and societally aware — strong with STS judges.
- **Cite the canonical references precisely** (Efficiency Tables v66, NREL chart, ISOS consensus protocol). Getting the records exactly right signals you actually know the field.
- **Honest limitations section.** Acknowledge air-sensitivity, small-area cells, and the gap to commercial lifetimes. Finalists are graded on scientific maturity, not hype.

### Key sources

- Green et al., **Solar Cell Efficiency Tables (Version 66)**, *Prog. Photovolt.* 33(7):795–810 (2025) — canonical record list. https://doi.org/10.1002/pip.3919 (newer: Version 67, https://doi.org/10.1002/pip.70068)
- **NREL Best Research-Cell Efficiency Chart** (master record chart). https://www.nrel.gov/pv/cell-efficiency
- c-Si HBC 27.3% record (LONGi/ISFH): https://www.longi.com/eu/news/2730-hbc-world-record/
- Single-junction perovskite ~27%, NREL listing: https://www.acap.org.au/post/world-leading-27-perovskite-efficiency-record-achieved-by-unsw-and-soochow-university-with-acap-su ; overview https://www.ossila.com/pages/highest-efficiency-perovskite-solar-cells
- Perovskite–Si tandem **34.85%** (LONGi, NREL-certified): https://www.longi.com/en/news/silicon-perovskite-tandem-solar-cells-new-world-efficiency/
- All-perovskite tandem **29.1%** certified: https://www.nature.com/articles/s41563-024-02073-x
- Lead-free **Sn perovskite 16.65% certified** (2D/3D, U. Queensland): https://www.nature.com/articles/s41565-025-01905-4 ; 14.51% certified cm-scale: https://www.nature.com/articles/s41560-025-01919-1
- Lead-free double perovskite **Cs₂AgBiBr₆** (record ~6.4%, indoor potential): https://iopscience.iop.org/article/10.1088/1402-4896/ad9b59
- OPV **~20%** certified single-junction (2024): https://www.pv-magazine.com/2024/08/21/chinese-scientists-achieve-record-breaking-20-efficiency-in-single-junction-organic-solar-cell/ ; module 14.5% https://www.sciencedirect.com/science/article/pii/S2542435124000990
- Perovskite **QD 18.1–18.3%**: https://www.pv-magazine.com/2025/10/08/perovskite-quantum-dot-solar-cell-achieves-record-breaking-efficiency-of-18-3/
- **Stability / ISOS protocols & T₈₀**: https://www.fluxim.com/research-blogs/isos-protocols-stability-perovskite-solar-cells ; degradation mechanisms review https://www.mdpi.com/2079-9292/14/22/4428 ; long-term operational stability (UToronto) https://light.utoronto.ca/wp-content/uploads/2023/08/s41578-023-00582-w.pdf
- **Lead toxicity / leakage / encapsulation**: https://www.sciencedirect.com/science/article/abs/pii/S030438942102817X ; review https://onlinelibrary.wiley.com/doi/10.1002/eom2.12511
- **ML for perovskite design** (bandgap/formation-energy XGBoost/GNN): https://www.nature.com/articles/s41524-021-00495-8 ; lead-free double-perovskite ML screen https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12155886/
- **Bayesian-optimization / self-driving labs**: autonomous closed-loop reproducible perovskites, *Nature* (2026) https://www.nature.com/articles/s41586-026-10482-y ; AI for perovskite additive engineering review https://pmc.ncbi.nlm.nih.gov/articles/PMC12899829/ ; AMADAP self-driving lab https://link.springer.com/article/10.1557/s43577-024-00816-4
- **Thermoelectric CsSnI₃** (ZT ~0.11–0.14 RT): https://pubs.acs.org/doi/10.1021/acsaem.2c01936 ; theory ZT~0.63@1000K https://pubs.rsc.org/en/Content/ArticleHtml/2016/RA/c6ra14144g
- **STS/ISEF precedent:** Jolene Cao (STS '25 Finalist, magnetite/CsPbX₃ QDs, 53× stability gain) https://www.societyforscience.org/regeneron-sts/2025-student-finalists/jolene-cao/ ; Tahani Ahmed (ISEF '22, CsSnI₃ solar + thermoelectric, materials 3rd) https://www.mawhiba.sa/en/media-center/news/with-an-unprecedented-historical-achievement-ksa-wins-16-grand-awards-and-7-special-awards-among-students-from-80-countries-at-isef-2022/ ; Jomanah Belal (ISEF '25 EGSD 3rd, dual-doping lead-free indoor PV) https://isef.net/project/egsd037-dual-doping-strategies-of-lead-free-indoor-pvs
