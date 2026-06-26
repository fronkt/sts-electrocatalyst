# 10 — Computational / ML Materials

**Bottom line:** This is the cross-cutting *methods* lane — the engine, not the destination — and it places at STS but caps lower as a standalone; the Top-40 path is a method-novel generative/inverse-design framework that **proposes AND validates** candidates, ideally closing the loop with one real experiment through the student's Fort Wayne Metals / Purdue / MIT access, which converts a "ran a model" project into a discovery story.

---

## Cheat-sheet: the method toolkit

| Method | What it does | Maturity & key tooling / datasets |
|---|---|---|
| **Generative inverse design (VAE / GAN / diffusion / flow)** | Samples *new* crystal structures or compositions conditioned on a target property | Mature & reproducible. CDVAE ([Xie 2022, ICLR](https://arxiv.org/abs/2110.06197)), DiffCSP ([Jiao, NeurIPS 2023](https://arxiv.org/abs/2309.04475)), MatterGen ([Zhao/Microsoft, *Nature* 2025, DOI 10.1038/s41586-025-08628-5](https://www.nature.com/articles/s41586-025-08628-5)) all open-source |
| **GNN property prediction** | Fast surrogate for DFT properties (formation energy, band gap, elastic moduli) | Mature. MEGNet/M3GNet ([Chen & Ong, *Nat. Comput. Sci.* 2022](https://www.nature.com/articles/s43588-022-00360-8)), ALIGNN ([Choudhary & DeCost, *npj Comput. Mater.* 2021](https://www.nature.com/articles/s41524-021-00650-1)) — bond-angle aware |
| **Foundation MLIPs (universal potentials)** | Near-DFT energies/forces across the periodic table; enables MD, relaxation, phonons | Maturing fast. MACE-MP-0 ([Batatia 2023](https://arxiv.org/abs/2401.00096)), CHGNet ([Deng, *Nat. Mach. Intell.* 2023](https://www.nature.com/articles/s42256-023-00716-3)), M3GNet, SevenNet, Orb ([Neumann 2024](https://arxiv.org/abs/2410.22570)); ranked on [Matbench Discovery](https://matbench-discovery.materialsproject.org/) |
| **Active learning / Bayesian optimization** | Picks the next-most-informative candidate to compute or synthesize | Mature pattern; the natural backbone for a propose→validate loop |
| **High-throughput DFT screening** | Computes ground-truth labels / filters candidates | Mature. [Materials Project](https://next-gen.materialsproject.org/) (~150k+ bulk), [OQMD](https://oqmd.org/) (~1.4M), [AFLOW](http://aflowlib.org/) (~3.5M), [JARVIS-DFT](https://jarvis.nist.gov/) (~76k) |
| **LLM-for-materials** | CIF-token generation, synthesizability/precursor prediction, literature mining | Emerging / hot but unproven for novelty. CrystalLLM, deCIFer; review [arXiv:2508.06691](https://arxiv.org/pdf/2508.06691); synthesizability LLM [*Nat. Commun.* 2025](https://www.nature.com/articles/s41467-025-61778-y) |

---

## Where the real bottleneck is

The field's hard problems are exactly the openings a strong STS project should target — they're also where a "standard model on a standard dataset" project loses to the judges.

1. **The validation gap (synthesizability).** Generative models emit structures that are thermodynamically plausible but rarely *made*. Energy-above-hull is a weak proxy for synthesizability; metastable-but-real and stable-but-never-synthesized materials both break the assumption ([*Nat. Commun.* 2025](https://www.nature.com/articles/s41467-025-61778-y); synthesizability-guided pipeline [arXiv:2511.01790](https://arxiv.org/html/2511.01790v1)). The cautionary tale: GNoME predicted ~380k "stable" candidates ([*Nature* 2023, DOI 10.1038/s41586-023-06735-9](https://www.nature.com/articles/s41586-023-06735-9)) and the paired A-Lab claimed 41 autonomous syntheses ([*Nature* 2023, DOI 10.1038/s41586-023-06734-w](https://www.nature.com/articles/s41586-023-06734-w)) — then outside chemists (Palgrave et al.) argued few if any were genuinely new phases ([Chemistry World](https://www.chemistryworld.com/news/new-analysis-raises-doubts-over-autonomous-labs-materials-discoveries/4018791.article)). **A single real experimental confirmation is worth more than 10,000 generated candidates** — and that is precisely the student's structural advantage.
2. **MLIP generalization & anharmonicity.** Foundation potentials are excellent near their training distribution and degrade out-of-domain (high pressure, defects, surfaces, strong anharmonicity). The MACE-MP-0 line needed successive patches (-0b2 high-pressure, -0b3 phonons) to fix systematic phonon errors, and benchmarks show fine-tuning improves force errors 5–15× ([fine-tuning tutorial, arXiv:2506.21935](https://arxiv.org/pdf/2506.21935)). Anharmonic free energies and lattice thermal conductivity remain a known weak spot.
3. **Data scarcity & label quality.** Cross-database DFT disagreement is real (AFLOW vs MP vs OQMD use different settings; [Phys. Rev. Mater. 2023](https://link.aps.org/doi/10.1103/PhysRevMaterials.7.053805)), experimental labels are sparse, and crystallographic databases carry duplicates that inflate "novelty" counts ([C&EN 2025](https://cen.acs.org/research-integrity/Duplicate-structures-haunt-crystallography-databases/103/web/2025/12)).
4. **Uncertainty quantification.** Most property predictors and generators ship point estimates; calibrated uncertainty is what makes an active-learning loop trustworthy and is still under-served.
5. **Conditioning that respects physics.** Generators routinely violate charge balance, valence, or space-group symmetry. Embedding hard physical constraints (e.g., valence-constrained generation, symmetry preservation) is an active, publishable frontier.

---

## Feasibility verdict (3.5-month runway)

**Compute & software: fully feasible, and it reuses the student's existing stack.** Every tool above is open-source and the student already operates a mature generative-CSP + inverse-design + MLIP/phonon/Boltzmann-transport pipeline plus GPU/Vast.ai. Training or fine-tuning a CDVAE/DiffCSP-class model, running a MACE/CHGNet relaxation+phonon screen, or standing up an active-learning loop are all days-to-weeks of compute, not the bottleneck. Materials Project / JARVIS / OQMD are freely downloadable for labels and held-out tests.

**The real risk is the CEILING, not feasibility.** Pure computational/ML materials entries *place* — Claire Gu (metasurface cWGAN) and Brendan Hirshorn (alloy generative inverse design) were **Scholars (Top 300)**; Amy Guan and Vedanth Iyer (DFT) reached **Finalist (Top 40)** but with deep physics framing, not "I ran a model." And the routing penalty is stark: Ryan Rezaei's symmetry-preserving VAE + rectified-flow diffusion materials project was sophisticated but **entered ISEF in Robotics & Intelligent Machines and won only a Midjourney Special Award, not a Grand Award** ([GSDSEF](https://www.gsdsef.org/news/the-75th-international-science-and-engineering-fair); [ISEF 2025 Special Awards](https://www.societyforscience.org/press-release/regeneron-isef-2025-special-awards-winners/)) — a method-first ML project can get mis-routed away from the high-value categories.

**The unlock with a 3.5-month runway is closing the loop.** The student can take ONE computational prediction and have it characterized/made via Fort Wayne Metals (alloys) or Purdue/MIT characterization. That single experiment is the difference between a Scholar-tier method demo and a Finalist-tier discovery. Budget ~6 weeks for compute+novelty, run the wet-lab/characterization request *early and in parallel* (it's the long-lead item), and reserve the back third for the ~20-page writeup. Do **not** save the experiment for last.

---

## Where ML adds value — what counts as a NOVEL methodological contribution

Judges reward a genuine methods contribution, not a benchmark re-run. Ranked by how much "novelty credit" each earns relative to effort.

| Contribution type | Toolchain / data | Difficulty |
|---|---|---|
| **A physics-informed constraint baked into the generator** (charge balance, valence, space-group symmetry) | Modify CDVAE/DiffCSP loss or sampling; validate on MP/JARVIS held-out | Medium — high payoff, clearly "new method" |
| **A synthesizability / stability filter that the model proposes against** (not just e-above-hull) | Train a synthesizability classifier ([*Nat. Commun.* 2025](https://www.nature.com/articles/s41467-025-61778-y), [ACS Omega 2022](https://pubs.acs.org/doi/10.1021/acsomega.2c04856)) → couple to generator | Medium — directly attacks the field's #1 gap |
| **A closed active-learning loop that proposes AND validates** (DFT, MLIP, or one real experiment) | Generator → MLIP/DFT screen → BO/uncertainty → next candidate → confirm | Medium-High — the Top-40 template |
| **A new representation or conditioning channel** (e.g., condition generation on PXRD, on processing route, on an experimental descriptor) | Decoder conditioned on measured signal; tie to the student's characterization access | High — strongest novelty, riskiest |
| **Calibrated UQ that changes a decision** (UQ-gated screening that beats naive ranking) | Ensemble / evidential MLIP or predictor; show it improves hit rate | Medium — under-served, demonstrable |
| **Transfer / fine-tuning a foundation MLIP to a regime it fails in** (anharmonic phonons, specific alloy family) and proving the fix | MACE/CHGNet/SevenNet fine-tune + phonon/transport check vs DFT or experiment | Medium — leverages the student's phonon/Boltzmann tooling |
| *Anti-pattern: "ran M3GNet/CDVAE on the Materials Project and reported metrics"* | — | Low novelty — will cap at Scholar at best |

---

## Ranked project framings

Each notes whether it is **standalone-computational** (lower ceiling) or **engine-for-a-hybrid** (the student's stack powering a discovery in another lane — higher ceiling).

### 1. Closed-loop generative alloy design, validated at Fort Wayne Metals *(engine-for-a-hybrid; HIGHEST ceiling)*
- **Hypothesis:** A property-conditioned generative model + synthesizability filter can propose a *makeable* alloy composition with a target mechanical/functional property that, when actually cast and tested, matches the prediction within error.
- **Toolchain & data:** Student's inverse-design stack (conditioned VAE/diffusion or latent BO) trained on alloy datasets; MLIP/DFT for screening; **Fort Wayne Metals** to produce the alloy and Purdue for mechanical/microstructural characterization.
- **Novelty hook:** A synthesizability/manufacturability constraint inside the generator (not post-hoc), so it proposes *castable* candidates — directly answering the validation gap.
- **How to validate:** The real experiment IS the validation; back it with held-out DFT and an ablation showing the constraint improves hit rate.
- **STS-ceiling read:** This is the **Top-40 template** — a method-novel generator that proposes and a real lab confirms. Maps onto the metallurgy/applied lane, not "Robotics/ML," avoiding the Rezaei routing penalty. Closest precedent is Hirshorn (alloy generative inverse design, Scholar) — the *experimental loop* is what pushes past Scholar.

### 2. Synthesizability-guided crystal generation with one experimental hit *(engine-for-a-hybrid; high ceiling)*
- **Hypothesis:** Coupling a synthesizability classifier to a diffusion/flow CSP generator yields candidates with a measurably higher experimental-realization rate than energy-above-hull screening alone.
- **Toolchain & data:** DiffCSP/CDVAE/MatterGen-class generator + synthesizability model ([*Nat. Commun.* 2025](https://www.nature.com/articles/s41467-025-61778-y)); MP/OQMD/JARVIS; MLIP relaxation; pick ONE candidate for synthesis/characterization at Purdue or MIT.
- **Novelty hook:** Reframes the objective from *stable* to *synthesizable* and proves the shift with a confirmed sample — a direct rebuttal to the GNoME/A-Lab credibility debate.
- **How to validate:** Held-out recovery of known-synthesized vs never-synthesized compounds; one experimental confirmation (XRD match).
- **STS-ceiling read:** Finalist-plausible if the experiment lands; Scholar-solid even on DFT-only validation.

### 3. Fine-tuned foundation MLIP for anharmonic thermal transport, checked against experiment *(engine-for-a-hybrid; medium-high ceiling)*
- **Hypothesis:** A foundation MLIP fine-tuned on a target material family predicts lattice thermal conductivity (via anharmonic phonons + Boltzmann transport) more accurately than the off-the-shelf model, closing a known generalization gap.
- **Toolchain & data:** MACE-MP/CHGNet/SevenNet fine-tuned; student's **phonon + Boltzmann-transport tooling**; DFT/experimental κ as ground truth.
- **Novelty hook:** Quantifies and *fixes* the documented anharmonicity/phonon failure of foundation MLIPs (the -0b3 phonon patch shows this is real and open) for a chosen system.
- **How to validate:** Against DFT-computed κ and/or a measured thermal-transport value.
- **STS-ceiling read:** Strong methods story; pairs naturally with a thermoelectrics/thermal-management lane. Scholar-likely standalone, Finalist-plausible with an experimental κ.

### 4. Physics-constrained generator: symmetry + valence as hard constraints *(standalone-computational; medium ceiling)*
- **Hypothesis:** Enforcing space-group symmetry and charge/valence balance during generation increases the fraction of valid, stable, *novel* structures vs an unconstrained baseline.
- **Toolchain & data:** Modify CDVAE/DiffCSP; evaluate on MP/JARVIS with DFT spot-checks; report validity/novelty/stability like MatterGen does.
- **Novelty hook:** A clean architectural/loss contribution targeting the physics-violation failure mode.
- **How to validate:** Held-out + DFT relaxation of top samples; ablation vs unconstrained model.
- **STS-ceiling read:** Honestly **Scholar-tier** without an experiment — this is the Gu/Hirshorn pattern (Scholars). Good as a *fallback* if the wet-lab loop slips, or as the methods core of framings 1–2.

### 5. Uncertainty-gated active-learning screen that beats naive ranking *(standalone-computational, optionally hybrid; medium ceiling)*
- **Hypothesis:** A calibrated-UQ active-learning loop discovers stable/target candidates with fewer DFT calls than greedy property ranking.
- **Toolchain & data:** Ensemble/evidential MLIP or property predictor + BO over MP/OQMD; ground-truth via on-demand DFT.
- **Novelty hook:** Demonstrated calibration that *changes the decision* and improves discovery efficiency — addresses the under-served UQ gap.
- **How to validate:** Discovery acceleration factor vs baseline on held-out DFT (Matbench-Discovery-style).
- **STS-ceiling read:** Scholar-tier standalone; becomes a Finalist component if it feeds framing 1 or 2 and a candidate gets made.

---

## How to stand out

- **Close the loop with ONE experiment.** Everything above hinges on this. A confirmed prediction (an alloy cast at Fort Wayne Metals, a phase verified by XRD at Purdue/MIT) is the single highest-leverage move and the student is rarely-positioned to do it. Start the lab request in week 1.
- **Route into a *materials/physics/applied* lane, not "Robotics/ML."** Rezaei's penalty is the lesson — frame the contribution as a battery/alloy/thermal/magnet discovery powered by ML, not as an ML method looking for an application.
- **Attack a named bottleneck, out loud.** Position explicitly against the synthesizability/validation gap and cite the GNoME/A-Lab credibility debate; showing you understand *why* generated materials usually aren't real is itself a maturity signal judges reward.
- **Ablate honestly.** Report validity/novelty/stability the way MatterGen and Matbench Discovery do; show the new constraint/loop *beats* the baseline. A clean ablation reads as rigor.
- **Use the foundation models as infrastructure, claim novelty above them.** MACE/CHGNet/M3GNet/CDVAE are the engine, not the contribution — make the new representation, constraint, filter, or loop the thing you defend.
- **Keep the compute story crisp.** One trained/fine-tuned model + one screen + one validated candidate, fully reproducible, beats a sprawling benchmark sweep on a 20-page paper.

---

### Key sources

- Xie et al., *Crystal Diffusion Variational Autoencoder (CDVAE)*, ICLR 2022 — https://arxiv.org/abs/2110.06197
- Jiao et al., *DiffCSP: Crystal Structure Prediction by Joint Equivariant Diffusion*, NeurIPS 2023 — https://arxiv.org/abs/2309.04475
- Zhao et al. (Microsoft), *MatterGen: a generative model for inorganic materials design*, *Nature* 2025, DOI 10.1038/s41586-025-08628-5 — https://www.nature.com/articles/s41586-025-08628-5
- Chen & Ong, *M3GNet — universal many-body GNN potential*, *Nat. Comput. Sci.* 2022 — https://www.nature.com/articles/s43588-022-00360-8
- Choudhary & DeCost, *ALIGNN*, *npj Comput. Mater.* 2021 — https://www.nature.com/articles/s41524-021-00650-1
- Deng et al., *CHGNet*, *Nat. Mach. Intell.* 2023 — https://www.nature.com/articles/s42256-023-00716-3
- Batatia et al., *MACE-MP-0 — foundation model for materials chemistry*, 2023 — https://arxiv.org/abs/2401.00096
- Neumann et al., *Orb: A Fast, Scalable Neural Network Potential*, 2024 — https://arxiv.org/abs/2410.22570
- Riebesell et al., *Matbench Discovery*, *Nat. Mach. Intell.* 2025 — https://www.nature.com/articles/s42256-025-01055-1 ; leaderboard — https://matbench-discovery.materialsproject.org/
- Merchant et al., *GNoME — Scaling deep learning for materials discovery*, *Nature* 2023, DOI 10.1038/s41586-023-06735-9 — https://www.nature.com/articles/s41586-023-06735-9
- Szymanski et al., *A-Lab autonomous synthesis*, *Nature* 2023, DOI 10.1038/s41586-023-06734-w — https://www.nature.com/articles/s41586-023-06734-w ; credibility critique — https://www.chemistryworld.com/news/new-analysis-raises-doubts-over-autonomous-labs-materials-discoveries/4018791.article
- Synthesizability + precursor prediction via LLMs, *Nat. Commun.* 2025 — https://www.nature.com/articles/s41467-025-61778-y
- LLMs/RAG for crystalline materials (systematic review), arXiv:2508.06691 — https://arxiv.org/pdf/2508.06691
- Open DFT databases: Materials Project — https://next-gen.materialsproject.org/ ; OQMD — https://oqmd.org/ ; AFLOW — http://aflowlib.org/ ; JARVIS-DFT — https://jarvis.nist.gov/
- **STS/ISEF precedent:** Evan Kim (STS '23 Finalist, *ScGAN*) — https://www.societyforscience.org/regeneron-sts/2023-student-finalists/evan-kim/ ; ScGAN paper — https://arxiv.org/abs/2209.03444 · Brendan Hirshorn (STS '26 Scholar, alloy generative inverse design) — https://www.societyforscience.org/regeneron-sts/2026-scholars/ · Claire Gu (STS '23 Scholar, cWGAN metasurfaces) — https://www.societyforscience.org/regeneron-sts/2023-scholars/ · Claire Andreasen (STS '22 Finalist, computational solid-state) — https://www.societyforscience.org/regeneron-sts/2022-finalists/ · Amy Guan & Vedanth Iyer (STS '21 Finalists, DFT) — https://www.societyforscience.org/regeneron-sts/2021-finalists/ · Ryan Rezaei (ISEF '25, symmetry-VAE + rectified-flow, Robotics category, Special Award only) — https://www.gsdsef.org/news/the-75th-international-science-and-engineering-fair
