# 07 — Batteries / Energy Storage / Redox-Flow

**Bottom line up front:** This lane has the strongest STS/ISEF precedent of any materials topic and a clean hybrid path for this student — ML screens a candidate (electrolyte additive, cathode dopant, or solid-electrolyte composition), then it gets fabricated and cycled in a coin cell or a benchtop aqueous flow cell against a baseline; the highest-ceiling, most-feasible-in-3.5-months framing is an **ML-guided electrolyte-additive or aqueous-flow chemistry**, because the wet-lab loop is fast, cheap, air-tolerant, and directly extends the Sanxhaku '25 finalist template.

## Cheat-sheet: chemistries at a glance

| Chemistry | Key metric | Key tradeoff |
|---|---|---|
| **Li-ion, NMC811 (Ni-rich)** | ~260 Wh/kg cell, ~320 Wh/kg high-end pouch | High energy + power, but cobalt/nickel cost, thermal runaway risk, ~1,000–2,000 cycles ([Grepow](https://www.grepow.com/blog/what-is-the-nmc-811-battery-what-are-its-features-battery-monday.html), [NX-Tech](https://nx-tech.com/insight-hub/lfp-vs-nmc-batteries/)) |
| **Li-ion, LFP** | ~170 Wh/kg cell, ~$80–100/kWh | Cheap, safe, 2,000–5,000 cycles, but lower energy density ([NX-Tech](https://nx-tech.com/insight-hub/lfp-vs-nmc-batteries/)) |
| **Graphite anode** | 372 mAh/g (theoretical) | Mature, but caps cell energy; Li-plating risk on fast charge |
| **Si anode** | ~3,600–4,200 mAh/g (theoretical) | ~10× capacity, but ~300% volume swell cracks SEI → fade |
| **Li-metal anode** | 3,860 mAh/g | Highest capacity; dendrites + dead-Li from unstable SEI kill cycle life ([Cell Reports Phys. Sci.](https://www.sciencedirect.com/science/article/pii/S2542435123003549)) |
| **Solid electrolyte, sulfide (LGPS/argyrodite)** | >10 mS/cm (room-T Li⁺) | Liquid-like conductivity, but air/moisture-sensitive (H₂S), soft interfaces ([Adv. Mater. 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC12783987/)) |
| **Solid electrolyte, oxide (LLZO garnet)** | ~0.1–1 mS/cm | Air-stable, dendrite-resistant, but brittle + high interfacial resistance ([PMC review](https://pmc.ncbi.nlm.nih.gov/articles/PMC11597872/)) |
| **Solid electrolyte, halide (Li₃YCl₆ etc.)** | ~0.1–1+ mS/cm | Good cathode compatibility + processability, costlier, less Li-stable ([Nano-Micro Lett. 2026](https://link.springer.com/article/10.1007/s40820-026-02251-3)) |
| **Na-ion (hard carbon ‖ layered oxide / Prussian white)** | ~140–175 Wh/kg cell, >10,000 cycles | Cheap, no Li/Co, sodium-abundant, but lower energy density ([ESS-News on CATL](https://www.ess-news.com/2026/04/20/a-closer-look-at-catls-new-sodium-ion-battery/)) |
| **Vanadium redox flow** | ~20–50 Wh/L; <$350/kWh (4 h, optimized) | Decoupled power/energy, ~25 yr life, but vanadium cost + low energy density ([OSTI](https://www.osti.gov/servlets/purl/1981578)) |
| **Aqueous-organic flow (anthraquinone)** | fade <0.01–0.02%/day (best couples) | Tunable, abundant organics, but molecular degradation + crossover ([ACS Energy Lett.](https://pubs.acs.org/doi/abs/10.1021/acsenergylett.2c01691)) |
| **All-iron flow** | ~$2/kg Fe; ~98% CE, ~87% EE (DES) | Dirt-cheap, abundant; Fe³⁺ crossover + plating morphology limit it ([Chem. Eng. J. 2024](https://www.sciencedirect.com/science/article/abs/pii/S1385894724034235), [Nat. Commun. 2024](https://www.nature.com/articles/s41467-024-45862-3)) |
| **Aqueous Zn-ion** | high theoretical (Zn-air ~1,218 Wh/kg); modest practical | Safe, aqueous, cheap; Zn dendrites + H₂ evolution + corrosion ([Adv. Mater. 2025](https://advanced.onlinelibrary.wiley.com/doi/full/10.1002/adma.202501361)) |
| **Li-S** | 1,675 mAh/g, ~2,600 Wh/kg (theoretical) | Huge energy; polysulfide shuttle + poor kinetics gut real cycle life ([MDPI Batteries](https://www.mdpi.com/2313-0105/12/3/104)) |
| **Supercapacitor** | ~5–15 Wh/kg, but ~10× battery power density | Near-instant charge, ~10⁶ cycles, but tiny energy density ([Wikipedia/Supercapacitor](https://en.wikipedia.org/wiki/Supercapacitor)) |

## Where the real bottleneck is

The bottleneck is almost never the bulk electrode — it is the **interfaces and the transport across them**. Concretely:

- **SEI / dendrites (the dominant killer).** On Li-metal and Si anodes, the solid-electrolyte interphase repeatedly cracks during plating/stripping, exposing fresh metal, consuming electrolyte, and growing dendrites and electrically-isolated "dead lithium." Cycle life is set by how stable and LiF-rich (mechanically robust, ionically conductive, electronically insulating) that nanometer-thick film is — not by the cathode's theoretical capacity ([Cell Reports Phys. Sci. 2023](https://www.sciencedirect.com/science/article/pii/S2542435123003549)).
- **Ionic conductivity + interfacial resistance (solid-state).** Sulfides already match liquids (>10 mS/cm) but degrade in air; oxides are stable but brittle with high cathode/electrolyte contact resistance. The unsolved problem is a single material that is conductive, air-stable, Li-stable, AND forms a low-resistance interface ([Adv. Mater. 2026 sulfide/halide review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12783987/)).
- **Fast-charge limits.** Pushing current causes Li to plate on graphite instead of intercalating, nucleating dendrites — again an interface/kinetics problem, not a capacity one.
- **Flow-battery degradation = molecular + crossover.** Aqueous-organic flow life is governed by active-molecule decomposition rate (best anthraquinones now <0.01–0.02%/day) and active-species crossover through the membrane; all-iron is limited by Fe³⁺ crossover and uneven Fe plating, not by iron cost ([ACS Energy Lett.](https://pubs.acs.org/doi/abs/10.1021/acsenergylett.2c01691), [Chem. Eng. J. 2024](https://www.sciencedirect.com/science/article/abs/pii/S1385894724034235)).
- **Zn-ion.** Same story as Li-metal but aqueous: Zn dendrites, hydrogen evolution, and corrosion at the anode/electrolyte interface, almost always tackled via **electrolyte additives** ([Adv. Mater. 2025](https://advanced.onlinelibrary.wiley.com/doi/full/10.1002/adma.202501361)).

**Strategic read:** every one of these is an *interface chemistry / additive / composition* problem — which is exactly what cheap, fast wet-lab loops (coin cells, symmetric cells, aqueous flow cells) and ML screening can attack in a high-school timeframe. Bulk energy-density records are off the table; interface-tuning is where a student can beat a baseline.

## Feasibility verdict (3.5-month runway)

**What the access enables:**

- **Fort Wayne Metals (industrial alloy / fine-wire / Fe-Ni melt-and-draw).** This is a real, differentiating asset. FWM can supply or fabricate **metal foils, fine wires, and custom alloy compositions** usable as: anodes (Zn, Fe, alloy anodes, Li-alloy hosts), **current collectors**, and — most directly — **iron feedstock/electrodes for an all-iron or iron-hybrid flow cell**. The Fe-Ni melt-and-draw capability uniquely lets the student vary an *alloy composition* that ML designed and then physically test it. This is the rare lever that turns a computational-only project into a hybrid.
- **Purdue lab (assistant researcher; characterization + likely coin-cell/electrochemistry).** This is the workhorse. Realistic in-scope: **coin-cell (CR2032) assembly in a glovebox/dry room, galvanostatic charge/discharge cycling, cyclic voltammetry, EIS (impedance), and basic characterization (XRD, SEM, maybe EDS).** A potentiostat/battery cycler (Biologic/Arbin/Neware) is the single most important instrument and is standard in such labs.
- **MIT industrial wet-lab connections.** Best used for a specialized step the other two can't do — e.g., advanced characterization (XPS for SEI, NMR for organic flow molecule stability), membrane access, or sourcing a specific synthesized organic redox couple.

**Realistically in-scope in 3.5 months (Jul–early Oct):**
- ✅ **Aqueous redox-flow chemistry on the bench** (iron, or aqueous-organic): air-tolerant, glassware + pumps + carbon felt + membrane + potentiostat. Sanxhaku '25 did exactly this. Fastest, safest wet loop.
- ✅ **Electrolyte-additive screening** in coin cells or symmetric Zn/Zn (or Fe) cells — small parameter space, fast cycling, clear baseline-vs-additive comparison.
- ✅ **Alloy / metal-anode or current-collector fabrication via FWM** + electrochemical testing at Purdue.
- ✅ **All the ML** (reuse the existing stack — see next section). Compute is not the constraint.

**Off the table (don't attempt):**
- ❌ Building a competitive **all-solid-state** Li cell from scratch (sulfide handling needs an Ar glovebox + dry room + cold-press tooling; interface engineering is a multi-year problem). ML on solid electrolytes is fine; *fabricating* a record cell is not.
- ❌ Si or Li-metal anode **cycle-life records** — needs hundreds of hours of cycling and pristine dry-room conditions to be credible.
- ❌ Anything requiring >~2 months of continuous cycling to show a result.

**Instruments needed (gate the project on these):** potentiostat/galvanostat with EIS (Biologic VSP / Gamry / Arbin / Neware) — non-negotiable; Ar glovebox (for any Li chemistry); coin-cell crimper; for flow: peristaltic pumps, carbon felt/paper electrodes, ion-exchange membrane (Nafion or anion-exchange), flow-cell hardware; characterization: XRD + SEM/EDS (Purdue), optionally XPS/NMR (MIT) for interface/molecule evidence.

## Where ML adds value

| Angle | Toolchain / data | Difficulty |
|---|---|---|
| **GNN cathode voltage / stability screening** | CGCNN / M3GNet on **Materials Project Battery Explorer** (~3,600 Li intercalation compounds, ~5,574 electrode entries total; reported CGCNN voltage MAE ~0.32 V for Li) — reuse the generative crystal-structure stack to *propose* dopants | Low–Med ([MP Batteries](https://next-gen.materialsproject.org/batteries), [arXiv 2412.11032](https://arxiv.org/pdf/2412.11032)) |
| **MLIP for Li/Na ionic conductivity** | MACE / CHGNet / M3GNet foundation potentials + MD for Li⁺ diffusivity; MACE ~comparable to DFT but **>350× faster** across 21 Li solid electrolytes — directly reuses the MLIP + phonon/transport tooling | Med ([arXiv 2603.28012](https://arxiv.org/pdf/2603.28012), [arXiv 2502.09970](https://arxiv.org/pdf/2502.09970)) |
| **Electrolyte / additive discovery** | Cheminformatics + DFT (HOMO/LUMO, redox potential, solubility) to rank additives/redox molecules; pair with Bayesian optimization over formulation space | Med — best **hybrid** glue: ML ranks → student tests ([Nat. Commun. autonomous electrolyte](https://www.nature.com/articles/s41467-022-32938-1)) |
| **Generative solid-electrolyte / composition design** | Reuse generative crystal-structure prediction to propose new conductor compositions; validate conductivity with MLIP-MD before any synthesis | Med–High ([arXiv 2510.09861 fine-tuned MLIP halides](https://arxiv.org/html/2510.09861v1)) |
| **Bayesian-opt formulation / fast-charge** | Closed-loop BO over additive ratios or charge protocols, minimizing experiments — proven to cut experimental count dramatically | Med ([Closed-loop fast-charge, Nature 2020](https://pubmed.ncbi.nlm.nih.gov/32076218/), [BO fast-charge design](https://www.sciencedirect.com/science/article/abs/pii/S0306261921015075)) |
| **SOH/SOC estimation** | Equivalent-circuit + ML on cycling/EIS data (the Colin Chu '26 template; he hit 2.36% SOH error) — purely data-driven, no synthesis | Low–Med ([Soc. for Science / Chu](https://www.societyforscience.org/regeneron-sts/2026-student-finalists/colin-jie-chu/)) |

## Ranked project framings

### 1. ML-screened metal-additive for an aqueous iron / iron-hybrid flow battery — **[HYBRID, top pick]**
- **Hypothesis:** A computationally-ranked low-level metal-salt (or organic ligand) additive lowers charge-transfer resistance and/or improves Fe-plating morphology in an aqueous iron flow cell, raising power density and Coulombic efficiency versus the additive-free baseline.
- **Toolchain & data:** DFT/cheminformatics to rank candidate cations/ligands by redox potential and binding (reuse the alloy-design + electronic-structure tooling); optional MLIP for speciation. Wet side: benchtop aqueous Fe flow cell, FeCl₂/FeCl₃ electrolyte, carbon-felt electrodes, membrane, potentiostat with EIS.
- **Novelty hook:** *Predict-then-test* an additive on the cheapest, most grid-relevant flow chemistry. Directly extends Sanxhaku '25 ("cation effect... electrolyte additives") but adds the ML screening layer he didn't have, and moves from iron-RFB cation effects to an explicitly ML-ranked additive set.
- **Fabricate + measure:** Assemble flow cell; cycle galvanostatically; report power density, CE/EE, EIS (R_ct), capacity-fade rate — baseline vs. best ML-ranked additive. FWM supplies iron electrode stock.
- **STS-ceiling read:** **Finalist-plausible.** Same chemistry family as a *recent* finalist + ML layer + clean baseline-beating result. Highest reward-to-risk here.

### 2. ML-ranked electrolyte additive to suppress Zn (or Fe) dendrites in an aqueous metal-anode cell — **[HYBRID]**
- **Hypothesis:** An additive selected by ML (adsorption energy / desolvation descriptors) homogenizes metal deposition, extending the cycle life / Coulombic efficiency of a symmetric Zn‖Zn (or Fe) cell vs. baseline electrolyte.
- **Toolchain & data:** DFT adsorption-energy screening of additive candidates on the Zn(002)/Fe surface (reuse MLIP/electronic-structure stack); wet side: symmetric coin/pouch cells, galvanostatic plating/stripping, EIS, SEM of the cycled anode.
- **Novelty hook:** Targets *the* canonical Zn-ion bottleneck (dendrites/HER/corrosion) with a predictive additive-design loop; SEM dendrite-morphology evidence is visually compelling for judges. Conceptual cousin of Jonathan Hu's ISEF '24 flexible Zn-ion work but mechanistic rather than device-demo.
- **Fabricate + measure:** Symmetric-cell cycle life (hours to short-circuit), CE in asymmetric cells, EIS, SEM before/after — additive vs. control.
- **STS-ceiling read:** **Scholar-solid, Finalist-stretch.** Aqueous = fast/safe; risk is that "additive improves Zn cycling" is crowded, so the ML-design rationale must be the differentiator.

### 3. ML-guided dopant for a Li-ion (or Na-ion) cathode, then fabricate + half-cell test — **[HYBRID]**
- **Hypothesis:** A GNN/DFT-predicted dopant on a chosen cathode (e.g., a polyanionic Na cathode or a Mn-based oxide) raises average voltage or structural stability without capacity loss, verified in a coin half-cell.
- **Toolchain & data:** CGCNN/M3GNet on Materials Project Battery Explorer to screen dopants for voltage/stability (reuse generative + GNN stack); DFT to confirm the top pick. Wet side: solid-state synthesis of doped vs. undoped cathode (Purdue), coin half-cell vs. Li/Na, galvanostatic cycling + dQ/dV.
- **Novelty hook:** This is the **Vedanth Iyer '21 template made hybrid** — Iyer was finalist on DFT *alone* (Cr-doped vanadyl oxide); doing the prediction *and* the synthesis + electrochemistry clears a higher bar.
- **Fabricate + measure:** Synthesize both compositions, build half-cells, compare first-cycle capacity, voltage, rate capability, capacity retention; XRD to confirm phase.
- **STS-ceiling read:** **Finalist-plausible if synthesis succeeds.** Higher fabrication risk (furnace synthesis, phase purity, glovebox for Li); Na-ion is the safer, cheaper, more topical variant.

### 4. MLIP-accelerated conductivity screening of a solid-electrolyte composition family — **[COMPUTATIONAL-ONLY, with a verification hook]**
- **Hypothesis:** Within a halide/oxide composition family, a fine-tuned MLIP predicts a composition with higher room-T Li⁺/Na⁺ conductivity than the parent, identified ~100× faster than DFT-MD.
- **Toolchain & data:** Fine-tune MACE/CHGNet on the target family; MLIP-MD for diffusivity → Arrhenius conductivity; benchmark against literature DFT/experiment. Pure reuse of the MLIP + transport stack.
- **Novelty hook:** Method + discovery: a data-efficient MLIP workflow that ranks a composition family and flags a candidate, leveraging the >350× MACE-vs-DFT speedup as the engine.
- **Fabricate + measure:** Optional/stretch — if a top candidate is air-stable and oxide/halide-based, attempt a pressed-pellet + EIS conductivity check (no full cell). Otherwise computational with rigorous literature validation.
- **STS-ceiling read:** **Scholar-realistic; Finalist only with experimental verification.** Pure-ML caps lower (this is the lesson of the precedent set); add even a single measured pellet conductivity to break the ceiling.

### 5. Frequency/EIS-based SOH estimation on cells the student cycles — **[DATA-DRIVEN / light wet-lab]**
- **Hypothesis:** Features extracted from EIS/frequency response predict state-of-health of cells aged in-house with lower error than a baseline equivalent-circuit model.
- **Toolchain & data:** Cycle a small set of cells to varying SOH at Purdue; ML (equivalent-circuit + regression) on EIS features. Reuses ML expertise, minimal synthesis.
- **Novelty hook:** Colin Chu '26 finalist template (he reached 2.36% SOH error) — but Chu used a public dataset; **generating your own aged-cell EIS data** is the differentiator.
- **Fabricate + measure:** Age cells, collect EIS spectra, train/validate model, report error vs. baseline.
- **STS-ceiling read:** **Scholar-realistic.** Lower fabrication risk; ceiling is the same as Chu's *if* the dataset is self-collected and the method is genuinely new — otherwise it reads as a re-run.

## How to stand out

1. **Be a hybrid, not a half.** Every recent battery finalist who used computation either *also* fabricated (the ceiling-breakers) or did exceptionally rigorous DFT (Iyer). Predict → fabricate → beat a baseline is the proven STS pattern; ML-only caps at Scholar.
2. **Pick the fast wet loop.** Aqueous flow and aqueous additive screening cycle in hours-to-days and are air-tolerant — they fit 3.5 months. Solid-state and Li-metal cycle-life work does not.
3. **Exploit FWM as the unfair advantage.** Almost no high-schooler can vary an *alloy/metal-electrode composition* that ML designed and then physically melt-and-draw it. Foreground this — it's a stronger differentiator than another DFT screen.
4. **Quantify a clean baseline delta.** Judges reward "X% lower R_ct," "Y% higher CE," "Z% slower fade vs. control" with error bars — not "promising." Sanxhaku's "reduced resistance" framing landed; copy the structure, improve the rigor.
5. **Make the ML→experiment link causal.** Show the additive/dopant/composition you tested was *chosen by the model*, and that the model's predicted descriptor (R_ct, adsorption energy, voltage) tracks the measured outcome. That closed loop is the whole story.
6. **Use open data honestly.** Materials Project Battery Explorer + MACE/CHGNet are free and citable; ground every screening claim in them and report MAE/limits so it reads as a grad-student would write it.

### Key sources

**STS / ISEF precedent**
- Aiden Sanxhaku, STS '25 Finalist (iron RFB, electrolyte additives): https://www.societyforscience.org/regeneron-sts/2025-student-finalists/aiden-sanxhaku/
- Colin Jie Chu, STS '26 Finalist (frequency-based SOH, 2.36% error): https://www.societyforscience.org/regeneron-sts/2026-student-finalists/colin-jie-chu/
- Vedanth Iyer, STS '21 Finalist (DFT Cr-doped vanadyl-oxide cathode): https://www.societyforscience.org/regeneron-sts/2021-scholars/ and project listing in [2021 finalist coverage](https://americanbazaaronline.com/2021/02/04/2021-regeneron-science-talent-search-indian-american-finalists-444111/)
- Jonathan Hu, ISEF '24 (self-healing flexible Zn-ion battery): [Regeneron ISEF 2024 full awards](https://www.societyforscience.org/press-release/regeneron-isef-2024-full-awards/); related peer-reviewed Zn-ion hydrogel chemistry: [Chem. Sci. 2024, DOI 10.1039/D4SC02348J](https://pubs.rsc.org/en/content/articlehtml/2024/sc/d4sc02348j)

**Chemistry metrics**
- NMC vs LFP energy density / cycle life / cost: https://nx-tech.com/insight-hub/lfp-vs-nmc-batteries/ ; NMC811 specifics: https://www.grepow.com/blog/what-is-the-nmc-811-battery-what-are-its-features-battery-monday.html
- Solid electrolytes (sulfide >10 mS/cm; oxide/halide tradeoffs): [Adv. Mater. 2026, PMC12783987](https://pmc.ncbi.nlm.nih.gov/articles/PMC12783987/) ; classification/mechanism review: [PMC11597872](https://pmc.ncbi.nlm.nih.gov/articles/PMC11597872/) ; halides: [Nano-Micro Lett. 2026, DOI 10.1007/s40820-026-02251-3](https://link.springer.com/article/10.1007/s40820-026-02251-3)
- Na-ion (CATL 160–175 Wh/kg, >10,000 cycles): https://www.ess-news.com/2026/04/20/a-closer-look-at-catls-new-sodium-ion-battery/
- Vanadium / flow cost + energy density: [OSTI techno-economic](https://www.osti.gov/servlets/purl/1981578) ; [DOE Flow Battery Strategy Assessment](https://www.energy.gov/sites/default/files/2023-07/Technology%20Strategy%20Assessment%20-%20Flow%20Batteries.pdf)
- Aqueous-organic flow fade rates (anthraquinones <0.01–0.02%/day): [ACS Energy Lett., DOI 10.1021/acsenergylett.2c01691](https://pubs.acs.org/doi/abs/10.1021/acsenergylett.2c01691) ; quinone degradation review: [J. Mater. Chem. A, DOI 10.1039/D5TA03034J](https://pubs.rsc.org/en/content/articlehtml/2025/ta/d5ta03034j)
- All-iron flow (~$2/kg Fe, ~98% CE / ~87% EE): [Chem. Eng. J. 2024 DES all-iron](https://www.sciencedirect.com/science/article/abs/pii/S1385894724034235) ; [Nat. Commun. 2024 phosphonate Fe complex, DOI 10.1038/s41467-024-45862-3](https://www.nature.com/articles/s41467-024-45862-3)
- Zn-ion anode challenges/additives: [Adv. Mater. 2025, DOI 10.1002/adma.202501361](https://advanced.onlinelibrary.wiley.com/doi/full/10.1002/adma.202501361)
- Li-S (1,675 mAh/g, 2,600 Wh/kg, shuttle): [MDPI Batteries review](https://www.mdpi.com/2313-0105/12/3/104)
- Supercapacitor energy/power: https://en.wikipedia.org/wiki/Supercapacitor
- SEI / dendrite mechanism: [Cell Reports Phys. Sci. 2023, S2542435123003549](https://www.sciencedirect.com/science/article/pii/S2542435123003549)

**ML toolchain & data**
- Materials Project Battery Explorer (~3,600 Li intercalation cmpds; ~5,574 electrode entries): https://next-gen.materialsproject.org/batteries ; docs: https://doc.docs.materialsproject.org/user-guide/batteries-explorer/
- CGCNN voltage MAE ~0.32 V (Li): [arXiv 2412.11032](https://arxiv.org/pdf/2412.11032) ; earlier voltage-ML: [arXiv 1903.06813](https://arxiv.org/pdf/1903.06813)
- MLIP for Li conductivity (MACE >350× faster than DFT; uMLIP benchmarks): [arXiv 2603.28012](https://arxiv.org/pdf/2603.28012) ; [arXiv 2502.09970](https://arxiv.org/pdf/2502.09970) ; fine-tuned halide MLIP: [arXiv 2510.09861](https://arxiv.org/html/2510.09861v1)
- Bayesian-opt / closed-loop: [closed-loop fast-charge, Nature 2020](https://pubmed.ncbi.nlm.nih.gov/32076218/) ; [BO fast-charge design](https://www.sciencedirect.com/science/article/abs/pii/S0306261921015075) ; [autonomous electrolyte discovery, Nat. Commun. 2022](https://www.nature.com/articles/s41467-022-32938-1)
