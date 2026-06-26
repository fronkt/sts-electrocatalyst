# 08 — Catalysis / Electrocatalysis / Photocatalysis

**Bottom line:** This lane is the single best fit for a hybrid ML-designs → student-fabricates → student-measures STS project because electrochemistry benchmarks (overpotential, Tafel slope, Faradaic efficiency) are cheap, fast, and quantitative — and a **high-entropy-alloy (HEA) electrocatalyst that Fort Wayne Metals can physically melt** lets the student close the loop in a way pure-computational entries cannot, directly mirroring the two catalysis-ML finalist projects (Guan '21, D'Halleweyn '24).

| Reaction / system | Benchmark metric | Key tradeoff |
|---|---|---|
| HER (H₂ evolution, acid/alkaline) | Overpotential @ 10 mA cm⁻²; exchange current density; Tafel slope | Pt is near-perfect (~28 mV @ 10 mA cm⁻² for Pt composites) but expensive — the game is matching Pt with earth-abundant metals ([JACS 2015](https://pubs.acs.org/doi/10.1021/ja510442p)) |
| OER (O₂ evolution, water-splitting anode) | Overpotential @ 10 mA cm⁻²; stability @ 100+ h | Scaling relations cap thermodynamic overpotential at ~0.37 V; acid OER still needs Ir; alkaline NiFe-LDH ~250–350 mV ([Sabatier review](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2021.654460/full); [Nat. Commun. 2025](https://www.nature.com/articles/s41467-025-61356-2)) |
| ORR (fuel-cell cathode) | Half-wave potential E₁/₂; mass activity | Pt-group dominance vs. cost; HEA/single-atom sites break scaling ([JACS 2024](https://pubs.acs.org/doi/10.1021/jacs.3c14486)) |
| CO₂RR (CO₂ → CO/formate/C₂₊) | Faradaic efficiency (FE) per product; partial current density | Selectivity: Cu makes everything; commercial Cu peaks ~43% FE-CO at 100 mA cm⁻² ([arXiv 2504.13634](https://arxiv.org/pdf/2504.13634)) |
| NRR / NO₃⁻RR (→ ammonia) | NH₃ yield rate; FE | N₂RR plagued by H₂ competition + contamination artifacts; nitrate-RR is the honest route (Cu-Co₂P hit 93.4% FE) ([PMC12114531](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12114531/)) |
| Methane activation (C–H scission) | Activation barrier (DFT, eV); TOF | Strong C–H bond; selectivity to CH₃OH vs. over-oxidation — Guan's '21 finalist topic ([UNT](https://research.unt.edu/magazine/regeneron-science-talent.html)) |
| Photocatalytic water splitting / CO₂ | Solar-to-hydrogen %; apparent quantum efficiency | Bandgap vs. band-edge alignment vs. charge recombination — hard to benchmark cleanly in 3.5 mo |

## Where the real bottleneck is

The field is governed by **linear scaling relations**: on a given surface the binding energies of reaction intermediates (e.g., *OH, *O, *OOH in OER) are mechanistically correlated, so you cannot independently tune them. This forces every conventional catalyst onto a **volcano plot** and imposes a hard floor — the best-case OER thermodynamic overpotential is **~0.37 V**, versus the ~0.0 V you'd get if each step were individually ideal ([Frontiers, Sabatier review](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2021.654460/full); [Chem. Soc. Rev. 2025](https://pubs.rsc.org/en/content/articlehtml/2025/cs/d5cs00597c)). Real progress means **circumventing scaling relations**, which is exactly why HEAs and single-atom catalysts are hot: their disordered, multi-element active-site distributions can break the correlations that cap conventional alloys ([JACS 2024 HEA-ORR](https://pubs.acs.org/doi/10.1021/jacs.3c14486); [Nat. Commun. 2023, "unusual Sabatier on HEA"](https://www.nature.com/articles/s41467-023-44261-4)).

Wrapped around that physics floor is the **activity–stability–selectivity triangle**: acid OER is fast on Ir but Ir is scarce; earth-abundant oxides are cheap but dissolve under acid OER; CO₂RR/NRR catalysts that are active are rarely selective. The grand challenge across the lane is **replacing Pt/Ir with earth-abundant metals** without sacrificing activity or lifetime — a framing every judge will recognize and a natural slot for a custom multi-metal alloy.

## Feasibility verdict (3.5-month runway)

**Strongly feasible — this is the lane to pick.** Electrochemical screening is the fastest quantitative wet-lab in materials science: a three-electrode cell + potentiostat gives you LSV/CV (overpotential), Tafel slopes (mechanism), and Faradaic efficiency (selectivity) in **hours per sample**, not weeks. Purdue's potentiostat + characterization access covers this directly.

- **HER/OER in alkaline KOH** — the safest, fastest measurements; NiFe-LDH and HEA anodes are robust and reproducible. Do this first.
- **HEA electrocatalysts via Fort Wayne Metals** — FWM's Fe-Ni melt-and-draw line can physically produce a custom 4–5 element alloy ingot/wire that the student then characterizes and tests. This is the rare asset most STS catalysis entrants lack; it converts a computational screen into a **real fabricated material with a measured polarization curve**.
- **Realistic risks:** acidic OER stability testing is harsh (skip it or keep short); CO₂RR product quantification needs GC/NMR (doable at Purdue but adds a day per run); **avoid N₂-reduction (NRR)** as the headline — the literature is littered with false positives from N-containing contamination, and a contested result will sink the project. Use **nitrate reduction (NO₃⁻RR)** instead if ammonia is the theme — it has real FE and clean controls.

Verdict: a **HER or OER HEA hybrid** is comfortably executable in Jul–early Oct; a CO₂RR-to-CO hybrid is feasible but tighter; pure photocatalysis is the riskiest (recombination/quantum-efficiency benchmarking is finicky) — keep it computational-only if at all.

## Where ML adds value

| Angle | Toolchain / data | Difficulty |
|---|---|---|
| Adsorption-energy / descriptor prediction | Pretrained GNNs (EquiformerV2, GemNet-OC) on **OC20** (1.28M relaxations, ~82 adsorbates × 11,451 slabs) + **OC22** (62k oxide relaxations) — predict *OH/*O/*OOH binding without running DFT ([arXiv:2206.08917](https://arxiv.org/abs/2206.08917); [OC Project](https://opencatalystproject.org/)) | Low–Med (models + data are open; inference on a laptop/single GPU) |
| HEA composition active learning | Multi-objective Bayesian optimization over composition space (activity + cost + entropic stability); diversity-batched — proven on 4.3×10¹² HEA candidates ([JACS 2024](https://pubs.acs.org/doi/10.1021/jacs.3c14486)) | Med (your existing alloy-design + active-learning stack maps directly) |
| MLIP for surface relaxations/segregation | Machine-learned interatomic potentials to relax slabs and predict surface segregation in the HEA — your MLIP + surface/adsorption tooling | Med–High (training/validation cost) |
| GNN screening → ranked shortlist | Filter thousands of compositions to a handful to actually melt/test — the core of the hybrid narrative | Low–Med |
| Generative / inverse design | Diffusion / generative crystal models for inverse catalyst design (CO₂RR electrocatalysts, bimetallic NH₃-decomposition, water-splitting photocatalysts) ([J. Mater. Inf. 2025](https://www.oaepublish.com/articles/jmi.2025.38); [arXiv:2507.19307](https://arxiv.org/pdf/2507.19307)) | High (novelty-rich but harder to validate experimentally in 3.5 mo) |

The honest framing for judges: ML here is a **screening accelerator that replaces brute-force DFT/experiment**, not an oracle — descriptor models tell you *which* of millions of compositions to fabricate, and the wet-lab confirms it.

## Ranked project framings

**1. HEA electrocatalyst, ML-screened → FWM-melted → measured (HYBRID — flagship; uses FWM)**
- **Hypothesis:** An ML-optimized earth-abundant high-entropy alloy (e.g., a Fe-Co-Ni-Cr-(Mn/Cu) family) achieves OER/HER overpotential within striking distance of NiFe-LDH/Pt while avoiding scaling-relation limits via disordered active sites.
- **Toolchain & data:** Pretrained OC20/OC22 GNN for *OH/*O/*OOH binding → multi-objective Bayesian active learning over composition (activity/cost/stability) → shortlist 2–4 compositions ([JACS 2024](https://pubs.acs.org/doi/10.1021/jacs.3c14486); [OC22](https://arxiv.org/abs/2206.08917)).
- **Novelty hook:** Closing the *physical* loop — a high-schooler who can actually **melt the predicted alloy at Fort Wayne Metals**, then put a polarization curve on it. Almost no STS catalysis entrant has melt-and-draw access.
- **Fabricate + measure:** FWM melts ingot/wire; Purdue does LSV (overpotential @ 10 mA cm⁻²), Tafel slope, chronopotentiometric stability, XRD/SEM-EDS; **beat or match a NiFe-LDH baseline** (~250–350 mV in alkaline, [Nat. Commun. 2025](https://www.nature.com/articles/s41467-025-61356-2)).
- **STS-ceiling read:** Highest ceiling — Finalist-plausible (Top 40 stretch) because it is the full design→make→measure→beat-baseline arc that has historically broken the ceiling. Top 300 floor is very safe if even one composition matches baseline.

**2. ML descriptor model for earth-abundant OER, validated on a synthesized oxide (HYBRID — Purdue-only fabrication)**
- **Hypothesis:** A GNN trained on OC22 can rank-predict OER overpotential of mixed transition-metal (oxy)hydroxides well enough that the top pick, synthesized wet-chemically, beats a control.
- **Toolchain & data:** OC22 oxide relaxations + EquiformerV2/GemNet-OC fine-tuning; predict adsorption descriptors → activity ranking ([OC22](https://pubs.acs.org/doi/10.1021/acscatal.2c05426)).
- **Novelty hook:** Honest quantification of *how well* cheap ML descriptors actually predict measured overpotential — a calibration study with real error bars, not a press-release claim.
- **Fabricate + measure:** Electrodeposit/hydrothermal NiFe(±Co/Mn)-LDH at Purdue; three-electrode OER; correlate predicted vs. measured.
- **STS-ceiling read:** Solid Scholar (Top 300); Finalist if the ML-experiment correlation is rigorous and the synthesis is non-trivial. Lower fabrication novelty than #1.

**3. CO₂RR-to-CO selectivity: ML-guided single-atom / dilute-alloy catalyst (HYBRID — tighter)**
- **Hypothesis:** An ML-selected M–N–C or Cu-based dilute-alloy site maximizes Faradaic efficiency to CO while suppressing HER, beating polycrystalline Cu (~43% FE-CO baseline, [arXiv 2504.13634](https://arxiv.org/pdf/2504.13634)).
- **Toolchain & data:** Multi-task GNN for CO₂RR intermediate binding / single-atom-alloy screening ([arXiv:2209.07300](https://arxiv.org/pdf/2209.07300)); Fe–N–C reaches ~100% FE-CO as the aspirational target ([PMC9661489](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9661489/)).
- **Novelty hook:** Selectivity, not just activity — judges reward the harder CO₂RR selectivity problem.
- **Fabricate + measure:** Synthesize SAC/dilute alloy; H-cell or flow cell at Purdue; FE by GC. Adds product-quantification overhead.
- **STS-ceiling read:** High ceiling but tighter runway (product analysis + reproducibility). Scholar likely; Finalist if FE is clean and beats Cu.

**4. Generative inverse design of a water-splitting photocatalyst (COMPUTATIONAL-ONLY)**
- **Hypothesis:** A symmetry-constrained generative model proposes stable, band-aligned candidate photocatalysts for water splitting.
- **Toolchain & data:** Your generative crystal-structure stack + stability/symmetry constraints ([arXiv:2507.19307](https://arxiv.org/pdf/2507.19307)); MLIP for relaxation/stability screening.
- **Novelty hook:** Generative + descriptor pipeline; strong methods story.
- **Fabricate + measure:** None (or a token synthesis if time allows).
- **STS-ceiling read:** Caps lower (pure-ML). Use only as fallback or as the computational engine feeding #1/#2. D'Halleweyn ('24) shows ML-only catalysis can reach Finalist, but it required deep experimental-data novelty (XAFS) — hard to replicate without that hook.

**5. Methane / small-molecule activation DFT optimization (COMPUTATIONAL-ONLY — Guan-style fallback)**
- **Hypothesis:** Metal/ligand tuning lowers the C–H activation barrier for selective methane functionalization.
- **Toolchain & data:** DFT (your MLIP-screened candidates → DFT refinement); descriptor optimization — directly the Guan '21 Finalist template ([UNT](https://research.unt.edu/magazine/regeneron-science-talent.html)).
- **Novelty hook:** Mechanistic descriptor for selective oxidation vs. over-oxidation.
- **Fabricate + measure:** None.
- **STS-ceiling read:** Proven Finalist-capable as pure-computational (Guan did it), but you'd be giving up your wet-lab edge. Only choose if lab access falls through.

## How to stand out

- **Close the loop physically.** The differentiator no other STS catalysis entrant likely has is an industrial melt line. Lead with: "I designed it, FWM melted it, I measured it, it beat the baseline." That single sentence outranks any pure-ML abstract.
- **Pick one reaction, beat one baseline, with error bars.** Alkaline OER overpotential @ 10 mA cm⁻² vs. NiFe-LDH is the cleanest, judge-legible win. Don't sprawl across HER+OER+CO₂RR.
- **Quantify your ML honestly.** Report predicted-vs-measured correlation with MAE in mV or FE%, and discuss where the model failed. Calibration honesty reads as maturity; over-claiming reads as a science-fair poster.
- **Frame against scaling relations.** Stating *why* HEAs/SACs can beat the ~0.37 V floor signals you understand the field's actual bottleneck, not just the buzzwords.
- **Operando, even lightweight.** A simple post-mortem XRD/SEM-EDS showing the alloy survived (or restructured during) operation adds a stability dimension judges love and most students skip.
- **Pre-empt the artifact critique.** If ammonia is involved, use nitrate reduction with isotope/blank controls — explicitly addressing the NRR contamination problem shows you know the literature's failure modes.

### Key sources

- Open Catalyst 2022 (OC22) dataset & oxide benchmarks — [arXiv:2206.08917](https://arxiv.org/abs/2206.08917) and [ACS Catal.](https://pubs.acs.org/doi/10.1021/acscatal.2c05426)
- Open Catalyst Project (OC20 scale, models, leaderboard): <https://opencatalystproject.org/>
- HEA electrocatalyst discovery via multi-objective Bayesian optimization (4.3×10¹² space) — [JACS 2024](https://pubs.acs.org/doi/10.1021/jacs.3c14486)
- "Unusual Sabatier principle on high-entropy-alloy catalysts for HER" — [Nat. Commun. 2023](https://www.nature.com/articles/s41467-023-44261-4)
- Sabatier principle, scaling relations & the ~0.37 V OER floor — [Frontiers Energy Res. 2021](https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2021.654460/full)
- "Twenty years after: scaling relations in oxygen electrocatalysis" — [Chem. Soc. Rev. 2025](https://pubs.rsc.org/en/content/articlehtml/2025/cs/d5cs00597c)
- HER/OER benchmarking standard (10 mA cm⁻², Pt/IrO₂ context) — [JACS 2015](https://pubs.acs.org/doi/10.1021/ja510442p)
- NiFe-LDH OER (earth-abundant alkaline benchmark, ~250–350 mV) — [Nat. Commun. 2025](https://www.nature.com/articles/s41467-025-61356-2)
- Commercial Cu CO₂RR FE-CO (~43% @ 100 mA cm⁻²) — [arXiv:2504.13634](https://arxiv.org/pdf/2504.13634)
- Fe–N–C single-atom catalysts (~100% FE-CO) — [PMC9661489](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9661489/)
- Nitrate-RR to ammonia, Cu-Co₂P 93.4% FE (NRR-artifact-safe route) — [PMC12114531](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12114531/)
- Generative/inverse catalyst design — [J. Mater. Inf. 2025](https://www.oaepublish.com/articles/jmi.2025.38) and [arXiv:2507.19307](https://arxiv.org/pdf/2507.19307)
- Multi-task GNN for Cu single-atom-alloy CO₂RR screening — [arXiv:2209.07300](https://arxiv.org/pdf/2209.07300)
- **STS precedent — Amy Guan '21 Finalist** (methane activation, DFT): <https://research.unt.edu/magazine/regeneron-science-talent.html> · [2021 finalists](https://www.societyforscience.org/regeneron-sts/2021-finalists/)
- **STS precedent — Sophie D'Halleweyn '24 Finalist** (multi-task ML nanocatalysts, XAFS): <https://www.societyforscience.org/regeneron-sts/2024-student-finalists/sophie-dhalleweyn/>
- **STS precedent — Vincent Chen '26 Scholar** (ferroelectric HfO₂ CNT membranes for ammonia synthesis): <https://www.societyforscience.org/regeneron-sts/2026-scholars/>
- **ISEF precedent — Tai & Ge '25, EGSD Second Award**, "Dual Functional Catalyst for Green Hydrogen Production": <https://www.societyforscience.org/press-release/regeneron-isef-2025-full-awards/>
