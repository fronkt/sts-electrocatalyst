# F8 — DOI resolution report

Every DOI in the scanned tree, resolved against Crossref and then DataCite.
`NOT_FOUND` means the registrar has no such identifier.

| state | n |
|---|---|
| NOT_FOUND | 1 |
| RESOLVED | 217 |

## NOT FOUND — these do not exist at any registrar

- `10.1016/j.jcat.2025.115963-range` — 404 from datacite
    - docs/28-electrocatalyst-revival-plan.md:90

## RESOLVED but no vocabulary overlap with any citing line

Not a verdict — many citations name only an author and a year.
These are the ones worth a human eye.

- `10.1002/eom2.12486` -> Recommended practice for measurement and evaluation of oxygen evolution reaction electrocatalysis (An 2024)
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:340 — WHAT: McCrory 2013 (JACS 135, 16977) fixes the figure of merit as η at 10 mA cm⁻² geometric, with ECSA, Faradaic efficie
- `10.1002/sus2.239` -> Thermal interface materials: From fundamental research to applications (Wei 2024)
    - docs/04-thermal-materials.md:81 — [SusMat 2024 TIM review](https://onlinelibrary.wiley.com/doi/full/10.1002/sus2.239);
- `10.1007/s11837-025-07815-z` -> Cu–Fe Composites Processed by Deformation-Driven Metallurgy: Correlating Structural, Mechanical, Electrical, and Tribological Properties (Sakhaei 2025)
    - docs/24-thermal-pivot-execution-plan.md:284 — **Materials/experimental:** Cu-Fe DPMMC reviews ([Sage 2022](https://journals.sagepub.com/doi/10.1177/14644207221090534)
- `10.1007/s42243-025-01507-3` -> Simultaneous enhancement of tensile strength and electrical conductivity of drawn Cu–20 wt.% Fe wire through intermediate annealing (Yang 2025)
    - docs/24-thermal-pivot-execution-plan.md:284 — **Materials/experimental:** Cu-Fe DPMMC reviews ([Sage 2022](https://journals.sagepub.com/doi/10.1177/14644207221090534)
- `10.1016/0254-0584(86)90045-3` -> Electrocatalytic properties of transition metal oxides for oxygen evolution reaction (Matsumoto 1986)
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:342 — - [zero-compute] The provenance of the 'experimental' points in every OER volcano figure is one 1986 compilation (10.101
- `10.1016/j.addma.2022.102943` -> Optimization of stochastic feature properties in laser powder bed fusion (Jensen 2022)
    - docs/11-metamaterials-metasurfaces.md:104 — - Metallic micro-lattices for high SEA (static + dynamic), *Acta Materialia* 2016, DOI 10.1016/j.actamat.2016.05.054: [S
- `10.1016/j.xcrp.2025.102847` -> Multifunctional robotic fish with post-buckling notched plates (Yin 2025)
    - docs/28-electrocatalyst-revival-plan.md:87 — 3. **MLIP benchmark-plus-fine-tune** — "out-of-box UMA (oc20 AND oc22 heads) cannot rank rutile-MO₂ OER; task-correction
    - docs/28-electrocatalyst-revival-plan.md:114 — MLIP: UMA (arXiv:2506.23971; HF `facebook/UMA`) · OC22 (arXiv:2206.08917) · Loveday/López failure modes 2026 (10.1021/ac
    - docs/research/2026-07-24-mlip-finetuning-survey.md:64 — **CatBench** (Moon et al.), **Cell Reports Physical Science 2025**, DOI 10.1016/j.xcrp.2025.102847 (article S2666-3864(2
- `10.1021/acs.jcim.3c00142` -> <i>WhereWulff</i>: A Semiautonomous Workflow for Systematic Catalyst Surface Reactivity under Reaction Conditions (Sanspeur 2023)
    - docs/75-novelty-and-placement-2026-09-03.md:149 — Kitchin & Ulissi, *JCIM* **63**(8), 2427-2437 (2023), DOI 10.1021/acs.jcim.3c00142
- `10.1021/acsami.4c01408` -> Catalytic Activity and Electrochemical Stability of Ru<sub>1–<i>x</i></sub>M<sub><i>x</i></sub>O<sub>2</sub> (M = Zr, Nb, Ta): Computational and Experimental Study of the Oxygen Evolution Reaction (Ospina-Acevedo 2024)
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:279 — - [heavy] The defensible reference-tier expansion is toward REAL rutiles (n=7 -> n≈11–14), and two independent published
- `10.1021/ja407115p` -> Benchmarking Heterogeneous Electrocatalysts for the Oxygen Evolution Reaction (McCrory 2013)
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:339 — - [zero-compute] The rigorous experimental-protocol corpus, and its headline: experiment does not resolve what the compu
- `10.1021/jz500610u` -> Orientation-Dependent Oxygen Evolution Activities of Rutile IrO
                    <sub>2</sub>
                    and RuO
                    <sub>2</sub> (Stoerzinger 2014)
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:345 — - [zero-compute] Experimentally, (110) is NOT the most active facet of RuO2 or IrO2 — so a perfect (110) calculation sho
- `10.1038/nature18018` -> FeO2 and FeOOH under deep lower-mantle conditions and Earth’s oxygen–hydrogen cycles (Hu 2016)
    - docs/31-r2-stability-gate.md:221 — 241, 2016 ([10.1038/nature18018](https://doi.org/10.1038/nature18018)), "FeO₂ and FeOOH
    - docs/31-r2-stability-gate.md:221 — 241, 2016 ([10.1038/nature18018](https://doi.org/10.1038/nature18018)), "FeO₂ and FeOOH
    - docs/31-r2-stability-gate.md:335 — Hu 2016 FeO₂ ([10.1038/nature18018](https://doi.org/10.1038/nature18018)).
- `10.1038/s41467-017-01983-6` -> Scaling relationships and theory for vibrational frequencies of adsorbates on transition metal surfaces (Lansford 2017)
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:51 — - [moderate] ZPE and −TΔS are usually BORROWED from a table, and the transferability assumption fails across this tier's
- `10.1038/s41524-023-00973-1` -> Identifying the ground state structures of point defects in solids (Mosquera-Lois 2023)
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:383 — - [heavy] The symmetry trap has a fully worked precedent in the DEFECT literature — ShakeNBreak — which supplies the sam
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:412 — ShakeNBreak numeric defaults (distortion factor range, step, rattle sigma, number of neighbours distorted) could NOT be 
    - docs/research/2026-08-15-lit-sweep-round2-synthesis.md:258 — - Displacement ladder dy ∈ {0.10, 0.25, 0.50} Å on **one pilot metal (Cr, *OOH only)**, then the single best dy applied 
- `10.1038/s41524-023-01121-5` -> AdsorbML: a leap in efficiency for adsorption energy calculations using generalizable machine learning potentials (Lan 2023)
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:95 — - [zero-compute] AdsorbML is the adjacent error class you must distinguish yourself from, explicitly and in one sentence
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:273 — - [moderate] AdsorbML + OC20-Dense define the field's accepted adequacy standard for adsorbate configuration sampling: ~
- `10.1038/s44306-024-00055-y` -> Absence of magnetic order in RuO2: insights from μSR spectroscopy and neutron diffraction (Keßler 2024)
    - docs/70-ideation-holes-spikes-2026-09-02.md:382 — DOI 10.1038/s44306-024-00055-y: ≤1.14×10⁻⁴ μ_B/Ru bulk, ≤7.5×10⁻⁴ μ_B/Ru films, with **multiple
- `10.1080/21663831.2024.2424933` -> Accelerated composition-process-properties design of precipitation-strengthened copper alloys using machine learning based on Bayesian optimization (Li 2025)
    - docs/24-thermal-pivot-execution-plan.md:284 — **Materials/experimental:** Cu-Fe DPMMC reviews ([Sage 2022](https://journals.sagepub.com/doi/10.1177/14644207221090534)
- `10.1088/0953-8984/23/5/053201` -> <i>Ab initio</i>
                    random structure searching (Pickard 2011)
    - docs/research/2026-08-15-lit-sweep-lens-digest.md:277 — WHAT: GOFEE actively learns a Gaussian-process surrogate on the fly and reports outperforming an established first-princ
- `10.1103/revmodphys.94.025002` -> Interfacial thermal resistance: Past, present, and future (Chen 2022)
    - docs/04-thermal-materials.md:34 — ([Rev. Mod. Phys. 94, 025002](https://link.aps.org/doi/10.1103/RevModPhys.94.025002))
    - docs/04-thermal-materials.md:80 — interfaces: [Rev. Mod. Phys. 94,025002](https://link.aps.org/doi/10.1103/RevModPhys.94.025002),
- `10.1126/sciadv.adq6758` -> MoZn-based high entropy alloy catalysts enabled dual activation and stabilization in alkaline oxygen evolution (Mei 2024)
    - docs/18-competitive-benchmark.md:104 — - HEA-OER professional context: <https://www.science.org/doi/10.1126/sciadv.adq6758> · <https://www.ncbi.nlm.nih.gov/pmc
- `10.1126/science.aat5522` -> Experimental observation of high thermal conductivity in boron arsenide (Kang 2018)
    - docs/04-thermal-materials.md:78 — BAs: [Science aat5522](https://www.science.org/doi/10.1126/science.aat5522),
- `10.1126/science.aat8982` -> High thermal conductivity in cubic boron arsenide crystals (Li 2018)
    - docs/04-thermal-materials.md:79 — [Science aat8982](https://www.science.org/doi/10.1126/science.aat8982);
- `10.5281/zenodo.22213117` -> Pre-registration record, DFT error-budget campaign (sts-electrocatalyst): Week-1 factorial, Hessian test, U gate — Amendments 1-11 + the 2026-08-31 entrant directive, frozen 2026-08-31 (Cai 2026)
    - docs/43-prereg-week1-factorial.md:2230 — **DOI line (2026-08-31):** **10.5281/zenodo.22213117** — docs/43 complete through
    - docs/43-prereg-week1-factorial.md:3323 — deposit at **10.5281/zenodo.22213117** carries the pre-change wording. Until the next deposit, the
    - docs/59-a0-roster-correction-2026-08-28.md:317 — **DOI line (2026-08-31):** **10.5281/zenodo.22213117** — docs/59 in its
- `10.5281/zenodo.22304889` -> Pre-registration record, DFT error-budget campaign (sts-electrocatalyst): Week-1 factorial, Hessian test, U gate — Amendments 1-13 (A10 pending) + the Hubbard-projector arms, frozen 2026-09-04 (Cai 2026)
    - docs/43-prereg-week1-factorial.md:3877 — **DOI line (2026-09-04):** **10.5281/zenodo.22304889** — docs/43 complete through
    - docs/43-prereg-week1-factorial.md:4004 — 12:35:26Z deposit of 10.5281/zenodo.22304889. A12b's readout row (A12b.R4) sits inline
    - docs/81-zpe-decomposition-of-a71-2026-09-04.md:149 — **The version of this file deposited in Zenodo 10.5281/zenodo.22304889 contains a false
