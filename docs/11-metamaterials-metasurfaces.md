# 11 — Metamaterials / Metasurfaces

**Bottom line:** A 3D-printed acoustic or mechanical/architected metamaterial that your ML stack inverse-designs, you fabricate, and you measure against a baseline (impedance tube or Instron) is a fully feasible, defensible hybrid project for a 3.5-month solo runway — but this lane has historically capped at **STS Scholar**, and breaking into Finalist requires a genuine methodological or physical novelty (a new objective, a new design space, or a measured result that beats a published number), not just "GAN + fabricate."

## Cheat-sheet: classes, functions, metrics

| Class | What it does (function) | Key metric(s) | Feasible fab for a high-schooler? |
|---|---|---|---|
| **Photonic metasurfaces** (metalenses, flat optics, structural color) | Bends/focuses/colors light with sub-wavelength nanostructures | Focusing efficiency (%), numerical aperture, bandwidth (nm) | **No** — needs nanofab (e-beam/nanoimprint). MIT-gated only. |
| **Acoustic metamaterials** (absorbers, ventilated barriers, cloaks) | Sub-wavelength sound absorption/insulation, often with airflow | Absorption coefficient α (0–1), transmission loss (dB), thickness vs λ | **Yes** — FDM/SLA print + impedance tube. Strongest hybrid. |
| **Mechanical / architected** (lattices, auxetics, energy absorbers) | Tailored stiffness, negative Poisson's ratio, crush energy absorption | Specific energy absorption SEA (kJ/kg or J/g), Poisson's ratio ν, modulus | **Yes** — print + Instron compression. Second strongest hybrid. |
| **Phononic crystals** (elastic/vibration band gaps) | Block elastic/vibration waves in a frequency band | Band-gap width/center (Hz), transmission loss (dB) | **Partly** — print + shaker/accelerometer; harder to measure cleanly. |
| **Thermal metamaterials** (cloaking, concentration) | Steer/hide heat flux via engineered conductivity | Temperature-field fidelity, isotherm distortion | **Partly** — thermal camera + heater rig; novelty bar is high. |

## Where the real bottleneck is

The hard part is **inverse design under an expensive forward solver**. For any of these classes the forward map (geometry → physical response) is a full-wave EM, FEM-acoustic, or nonlinear-mechanical simulation that can take minutes to hours per candidate, and the design space is combinatorially huge (free-form geometry, many unit-cell parameters). Brute-force or naive optimization is intractable. The 2024 Acoustic Metamaterials Roadmap and recent ML-metamaterials reviews frame the core tension explicitly: you want **broadband performance, low loss, sub-wavelength thickness, AND manufacturability simultaneously**, and these trade off against each other (a deep-subwavelength resonant absorber is narrowband; broadening it costs thickness or peak α).

This is precisely the gap ML fills, and why this lane is ML-native:
- **Surrogate/forward models** replace the expensive solver. Donda et al.'s CNN cut acoustic-absorber model computation by **~4 orders of magnitude** while still designing perfect absorption at 38.6 Hz in a 1.3 cm cell (reported in the Nat. Comms. Eng. review, DOI 10.1038/s44172-025-00470-x). A two-step DeepONet neural operator for mechanical metamaterials hit **R² > 0.98 / MSE 4.69×10⁻³** on stress–strain prediction and runs inverse design "within seconds" (Jin et al., *Adv. Mater.* 2025, DOI 10.1002/adma.202420063).
- **Generative inverse design** (GAN/VAE/diffusion) proposes geometries directly from a target spec — exactly the Claire Gu (cWGAN) and Ryan Rezaei (VAE + latent diffusion) playbook.
- **ML + topology optimization / physics-informed nets** for free-form designs and band-gap targeting.

Second bottleneck: **fabrication at the right length scale.** Acoustic/mechanical cells are millimeter-to-centimeter → desktop 3D printers work. Photonic meta-atoms are 100–500 nm → you need a cleanroom. This single fact decides your lane.

## Feasibility verdict (3.5-month runway)

- **3D-printed acoustic = the feasible hybrid.** Print a labyrinthine/Helmholtz/micro-perforated absorber in PLA or TPU on an FDM/SLA printer, test normal-incidence α in an impedance tube per **ASTM E1050 / ISO 10534-2**. Published desktop-scale results to benchmark against: broadband α ≥ 0.9 over 400–2500 Hz (Liu et al.); ventilated space-coiling barriers giving ~30 dB transmission loss over 660–1200 Hz while passing airflow; sub-λ/30 ventilated units at 860 Hz. If the Purdue lab has (or can borrow) a two-mic impedance tube, this is the cleanest "design→print→measure→beat baseline" loop available to you.
- **3D-printed mechanical/architected = the second feasible hybrid.** Print lattices/auxetics, run quasi-static compression on the Purdue **Instron**, report **SEA** and Poisson's ratio. Auxetic and re-entrant designs show ~25% higher SEA than plain hexagonal lattices; ML inverse design of auxetics with user-specified ν is well-established (cGAN, DNN). This needs only a printer + load frame you already have.
- **Photonic metasurfaces = nanofab-gated.** State-of-the-art is gorgeous (visible metalenses at 81–89% focusing efficiency; broadband achromatic metalens at ~60% average, 470–670 nm) but every one requires e-beam or nanoimprint lithography. **Only pursue if the MIT connection is a confirmed, scheduled nanofab slot with a mentor** — otherwise you have a computational-only project, and "another metasurface GAN" is the exact framing that capped Claire Gu at Scholar.
- **Phononic/thermal = possible but riskier.** Measurement rigs (shaker + accelerometers for band gaps; heater + thermal camera for cloaks) are fussier and the novelty bar is higher; treat as stretch.
- **What Fort Wayne Metals enables:** architected **metal** lattices / fine-wire structures. Metal AM lattices (Ti-6Al-4V, 316L) reach high SEA, but you likely can't print metal lattices yourself. The realistic FWM angle is **wire-woven / wire-assembled lattices or fine-wire-reinforced architected cells** — a distinctive, less-crowded design space (most STS metamaterial work is polymer FDM). If FWM can supply characterized fine wire and you build/test wire lattices on the Instron, that material novelty is a genuine differentiator.

## Where ML adds value

| Angle | Toolchain & data | Difficulty |
|---|---|---|
| **Generative inverse design** (geometry from target spec) | cWGAN / VAE / diffusion (your stack); data = simulated unit-cell library | Medium — the proven STS path (Gu, Rezaei); novelty must be in *what* you generate |
| **Deep-net surrogate for fast forward sim** | CNN / DeepONet / Fourier-neural-operator; data = a few thousand FEM/EM/acoustic runs | Medium — surrogate accuracy + needing a working solver to generate data |
| **ML + topology optimization** (free-form, not parametric) | Adjoint/TO with a learned surrogate or learned prior | Hard — but free-form designs are where the publishable performance lives |
| **Physics-informed neural nets (PINNs)** | Embed the wave/Helmholtz/elasticity PDE in the loss; less labeled data needed | Hard — finicky training; strong novelty hook if it works |
| **Bayesian optimization over the design space** | BO / multi-objective (your stack) directly on the surrogate | Low–Medium — pragmatic, great for the manufacturability/bandwidth trade-off front |

Your existing stack (generative inverse design + surrogate + Bayesian/topology optimization) maps onto all five rows — you are not building tooling from scratch, which is the single biggest 3.5-month advantage you have.

## Ranked project framings

**1. ML-inverse-designed broadband acoustic absorber, printed and impedance-tube-validated — [HYBRID]**
- **Hypothesis:** A generative + surrogate pipeline can design a sub-wavelength (≤ λ/10) labyrinthine/MPP absorber that achieves α ≥ 0.9 over a *wider* band or *thinner* profile than a named published baseline, and the printed part matches simulation within a few percent.
- **Toolchain & data:** Acoustic FEM/transfer-matrix solver to generate a unit-cell dataset → CNN/DeepONet surrogate → generative or BO inverse design → FDM/SLA print (PLA/TPU) → impedance tube (ASTM E1050).
- **Novelty hook:** A *new objective* (e.g., maximize bandwidth-thickness product, or co-optimize absorption AND airflow for a ventilated barrier) rather than re-deriving a known absorber. Ventilated + broadband is hot and under-explored at the high-school level.
- **Fabricate + measure:** Print 2–3 designs + a baseline; report measured α(f), compare sim vs. experiment, beat the baseline on one axis.
- **STS-ceiling read:** This is the Will Bao lane → reliably **Scholar**. To push toward **Finalist**, the win must be a *measured* result beating a published number (not just "our GAN works"), framed around a real-world problem (low-frequency / ventilated noise) with honest sim-vs-experiment error analysis.

**2. ML inverse-designed architected lattice / auxetic energy absorber, printed and crush-tested — [HYBRID]**
- **Hypothesis:** An inverse-design model can produce a lattice with target Poisson's ratio and **measurably higher SEA** than a standard (honeycomb/octet/re-entrant) reference at equal mass.
- **Toolchain & data:** Nonlinear FEM (compression) → surrogate (DeepONet/FNO) → cGAN/diffusion or multi-objective BO for the SEA-vs-stiffness front → print → Instron quasi-static compression.
- **Novelty hook:** Target the *full nonlinear stress–strain curve* (programmable crush behavior), not just one scalar — this is where neural operators are state-of-the-art and where a high-schooler matching published surrogate quality is striking.
- **Fabricate + measure:** Print several lattices + baseline, crush them, report SEA (kJ/kg) and ν, validate the surrogate against measured curves.
- **STS-ceiling read:** Strong **Scholar**, with a real **Finalist** shot if the inverse-designed curve is *experimentally* hit and the analysis is rigorous. Cleaner physics and easier measurement than acoustics.

**3. Wire-architected metal lattice (Fort Wayne Metals fine wire) with ML-tuned geometry — [HYBRID, differentiated material]**
- **Hypothesis:** Fine-wire-woven/assembled architected cells, with geometry optimized by your stack, give a distinct SEA-vs-density or stiffness-vs-density trade-off versus polymer-printed lattices.
- **Toolchain & data:** FEM with measured wire properties (FWM can characterize) → surrogate → BO/topology optimization over weave/cell parameters → build wire lattices → Instron.
- **Novelty hook:** **Material + fabrication route nobody else at STS is using.** Almost all student metamaterial work is polymer FDM; metal fine-wire architected structures are a genuinely fresh, FWM-enabled niche.
- **Fabricate + measure:** Assemble wire lattices, compress, compare to a printed-polymer control and a metal-lattice literature value.
- **STS-ceiling read:** The material novelty is the ceiling-breaker argument — **if** the fabrication is reproducible and the testing is clean. Higher fabrication risk; pilot a single cell early before committing.

**4. Generative inverse design of dielectric metasurface meta-atoms — [NANOFAB-GATED]**
- **Hypothesis:** A diffusion/GAN model designs meta-atoms hitting a target phase/efficiency spectrum better than a parametric library.
- **Toolchain & data:** RCWA/FDTD solver → surrogate → generative inverse design → (MIT) e-beam fab → optical efficiency measurement.
- **Novelty hook:** Free-form meta-atoms via diffusion (newer than the cWGAN era) and *fabricated + measured*, not simulation-only.
- **STS-ceiling read:** Simulation-only = **Scholar at best** (this is literally the Gu '23 ceiling). The *only* thing that lifts it is a **fabricated, optically measured** device — which means a confirmed MIT nanofab slot and mentor. Without that, deprioritize.

**5. Computational-only ML surrogate + inverse design across a class — [COMPUTATIONAL-ONLY]**
- **Hypothesis:** A single surrogate (neural operator / PINN) generalizes inverse design across a metamaterial family faster/more accurately than prior work.
- **STS-ceiling read:** Honestly, **Scholar floor and Scholar ceiling** unless the method is genuinely new. STS rewards the physical loop closing. Use this only as a fallback if no fab access materializes — and even then, fold in *some* fabricated validation.

## How to stand out

- **Close the loop and beat a real number.** The historical Scholar ceiling for this lane comes from projects that stop at "ML produces a design." Finalist-tier means: inverse-design → fabricate → measure → **demonstrate you beat a specifically named published baseline** on one metric, with honest sim-vs-experiment error bars. Pick your baseline *now* and design to beat it.
- **Pick an objective nobody else optimized.** Bandwidth-thickness product, ventilated-and-broadband, full nonlinear crush curve, or a new material route (FWM wire) — novelty in the *problem statement* travels further than novelty in the *network architecture*.
- **Quantify the ML win.** State the surrogate's speedup over the solver (orders of magnitude, as in the cited reviews) and its accuracy (R², MSE). That makes the ML contribution concrete and reviewable, not decorative.
- **Be honest about loss, manufacturability, and the sim-to-real gap** — printed parts deviate from CAD; report it. Reviewers reward rigor over polish.
- **Lock fabrication access in week one.** Confirm the impedance tube / Instron / (FWM wire) / (MIT nanofab) *before* committing to a framing. Your lane is decided by which rig is actually in your hands. If MIT nanofab isn't a scheduled, mentored slot, do not bet the project on photonics.
- **Start small and parallel:** build the surrogate while you print and test a *known* design to validate your measurement rig early; only then chase the novel optimized design.

### Key sources

**Precedent (verified):**
- Will Bao — 2025 STS Scholar: [2025 Regeneron STS Scholars](https://www.societyforscience.org/regeneron-sts/2025-scholars/); ISEF '24 project MATS050 "ML-Discovered Metamaterials for Noise Mitigation" [isef.net/project/mats050](https://isef.net/project/mats050-ml-discovered-metamaterials-for-noise-mitigation)
- Claire Gu — 2023 STS Scholar, "Conditional Wasserstein GAN…All-Dielectric Metasurfaces": [2023 Regeneron STS Scholars](https://www.societyforscience.org/regeneron-sts/2023-scholars/)
- Ryan Rezaei — ISEF '25 ROBO033, VAE + latent diffusion for materials: [isef.net/project/robo033](https://isef.net/project/robo033-latent-space-diffusion-for-accelerated-materials); [ISEF 2025 Special Awards](https://www.societyforscience.org/press-release/regeneron-isef-2025-special-awards-winners/)

**Acoustic:**
- ML for bio-inspired acoustic metamaterials (review incl. Donda CNN ~4-orders speedup; broadband α data) — *Comms. Eng.* 2025, DOI 10.1038/s44172-025-00470-x: [nature.com/articles/s44172-025-00470-x](https://www.nature.com/articles/s44172-025-00470-x) · open: [PMC12307771](https://pmc.ncbi.nlm.nih.gov/articles/PMC12307771/)
- 2024 Acoustic Metamaterials Roadmap (bottleneck/trade-off framing), DOI 10.1088/1361-6463/add306: [iopscience.iop.org/article/10.1088/1361-6463/add306](https://iopscience.iop.org/article/10.1088/1361-6463/add306)
- Additively manufactured metamaterials for acoustic absorption (review; FDM/SLA/SLS), DOI 10.1080/17452759.2024.2435562: [tandfonline.com](https://www.tandfonline.com/doi/full/10.1080/17452759.2024.2435562)
- Ventilated broadband barrier (~30 dB, 660–1200 Hz, 3D printed): [ScienceDirect S235243162100105X](https://www.sciencedirect.com/science/article/abs/pii/S235243162100105X); deep-subwavelength ventilated unit (sub-λ/30): [PMC12072964](https://pmc.ncbi.nlm.nih.gov/articles/PMC12072964/)

**Mechanical / architected:**
- Stochastic mechanical metamaterials via neural operators (DeepONet, R²>0.98), *Adv. Mater.* 2025, DOI 10.1002/adma.202420063: [PMC12288774](https://pmc.ncbi.nlm.nih.gov/articles/PMC12288774/)
- ML inverse design of auxetics (deep learning / cGAN), DOI 10.1016/j.mtcomm.2022.103186: [ScienceDirect S2352492822000630](https://www.sciencedirect.com/science/article/abs/pii/S2352492822000630)
- Metallic micro-lattices for high SEA (static + dynamic), *Acta Materialia* 2016, DOI 10.1016/j.actamat.2016.05.054: [ScienceDirect S1359645416304153](https://www.sciencedirect.com/science/article/abs/pii/S1359645416304153); Ti lattice SEA enhancement, DOI 10.1016/j.addma.2022.102943: [ScienceDirect S221486042200286X](https://www.sciencedirect.com/science/article/abs/pii/S221486042200286X)

**Photonic (nanofab-gated):**
- Visible metalenses, 81%/89% focusing efficiency (nanoimprint vs e-beam): [arXiv 2312.13851](https://arxiv.org/pdf/2312.13851)
- Broadband achromatic visible metalens (~60% avg, 470–670 nm), *Nat. Nanotech.* 2018, DOI 10.1038/s41565-017-0034-6: [nature.com/articles/s41565-017-0034-6](https://www.nature.com/articles/s41565-017-0034-6)
- AI for optical metasurfaces (review), DOI 10.1038/s44310-024-00037-2: [npj Nanophotonics](https://www.nature.com/articles/s44310-024-00037-2)

**Phononic / thermal:**
- On-demand inverse design of arbitrary-band-gap metamaterials (cVAE+MLP), *npj AI* 2025, DOI 10.1038/s44387-025-00001-1: [nature.com/articles/s44387-025-00001-1](https://www.nature.com/articles/s44387-025-00001-1)
- Soft phononic crystal band-gap design via deep learning, DOI 10.3390/ma18020377: [PMC11767058](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11767058/)
- Thermal cloak via topology optimization (experimental), DOI 10.1016/j.ijheatmasstransfer.2022.123093: [ScienceDirect S0017931022005658](https://www.sciencedirect.com/science/article/abs/pii/S0017931022005658)
