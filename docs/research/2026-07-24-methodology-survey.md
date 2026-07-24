# Deep-Research Report 2/4 — Oxide-OER Computational Methodology Upgrade

> **Provenance:** produced 2026-07-23/24 by a literature-survey agent (WebSearch/WebFetch over
> publisher pages, arXiv/ChemRxiv, OA repositories — legal-first sourcing, no Sci-Hub; citations
> verified against landing pages). One of four parallel surveys distilled into
> [docs/28](../28-electrocatalyst-revival-plan.md). Verbatim archive.
> Items with no free full text are marked **[PAYWALLED — flag for library access]**.

**Scope:** rutile-structure MO₂ (M = Cr, Mn, Fe, Co, Ni, Cu) OER via the 4-step CHE/AEM thermodynamic descriptor.

---

## A. CANONICAL FOUNDATION

**A1. Nørskov, Rossmeisl, Logadóttir, Lindqvist, Kitchin, Bligaard, Jónsson (2004). "Origin of the Overpotential for Oxygen Reduction at a Fuel-Cell Cathode."** *J. Phys. Chem. B* 108(46), 17886–17892. DOI: **10.1021/jp047349j**. OA: [ScienceOpen record](https://www.scienceopen.com/document?vid=539b625e-708b-4701-b03d-bb24f5b6a969), [DTU Orbit](https://orbit.dtu.dk/en/publications/origin-of-the-overpotential-for-oxygen-reduction-at-a-fuel-cell-c/).
- **This is the CHE-defining paper.** Conventions your project already relies on originate here: (i) the electrochemical step G is referenced to the *reversible hydrogen electrode*, so at potential U each proton–electron transfer shifts ΔG by −eU (ΔG = ΔG⁰ − eU); (ii) **O₂ is never computed directly** — the O₂ reference is fixed via the liquid-water equilibrium 2H₂O ⇌ O₂ + 4H⁺ + 4e⁻ set to 1.23 V, i.e. G(O₂) = 2G(H₂O) − 2G(H₂) + 4×1.23 eV, which sidesteps the notorious GGA O₂ triplet error; (iii) each intermediate energy gets **ΔZPE − TΔS** corrections (gas-phase H₂O at 0.035 bar taken as liquid; adsorbate entropies ≈ 0, gas entropies from tables at 298 K). These are the exact corrections you must apply to O*, OH*, OOH*.

**A2. Rossmeisl, Qu, Zhu, Kroes, Nørskov (2007). "Electrolysis of water on oxide surfaces."** *J. Electroanal. Chem.* 607(1–2), 83–89. DOI: **10.1016/j.jelechem.2006.11.008**. OA: [Academia.edu](https://www.academia.edu/27268674/Electrolysis_of_water_on_oxide_surfaces), [DTU Orbit](https://orbit.dtu.dk/en/publications/electrolysis-of-water-on-oxide-surfaces).
- **First application of CHE to rutile-oxide (110) OER** — the direct template for your project. Established the 4-step AEM path OH* → O* → OOH* → O₂ on the coordinatively-unsaturated site (cus) of rutile (110), and the linear O*/OH*/OOH* binding-energy relations on oxides. **Reference overpotentials (RPBE, (110) cus): RuO₂ = 0.37 V, IrO₂ = 0.56 V, TiO₂ = 1.19 V.** Use these to sanity-check: your 3d-rutile η values (0.89–1.75 V) sit *above* the noble rutiles, which is qualitatively expected, but the ~1.7 V for Cr and Ni is a red flag for wrong magnetic state / missing +U (see B).

**A3. Man, Su, Calle-Vallejo, Hansen, Martínez, Inoglu, Kitchin, Jaramillo, Nørskov, Rossmeisl (2011). "Universality in Oxygen Evolution Electrocatalysis on Oxide Surfaces."** *ChemCatChem* 3(7), 1159–1165. DOI: **10.1002/cctc.201000397**. **[PAYWALLED — flag for library access]**; OA copy: [Academia.edu](https://www.academia.edu/55798834/Universality_in_Oxygen_Evolution_Electrocatalysis_on_Oxide_Surfaces); [DTU Orbit](https://orbit.dtu.dk/en/publications/universality-in-oxygen-evolution-electrocatalysis-on-oxide-surfac/).
- **The volcano paper.** Defines the single activity descriptor **ΔG_O − ΔG_OH** and the near-universal scaling relation **ΔG_OOH = ΔG_OH + 3.2 eV (± ~0.2 eV)** across oxide surfaces. Because OOH* and OH* are locked 3.2 eV apart while the ideal spacing is 2×1.23 = 2.46 eV, scaling imposes a **theoretical minimum overpotential of ≈ (3.2 − 2.46)/2 ≈ 0.37 V** — no AEM oxide can beat it. Volcano apex at **ΔG_O − ΔG_OH ≈ 1.5–1.6 eV**. Reported theoretical overpotentials: **RuO₂(110) ≈ 0.42 V, IrO₂(110) ≈ 0.56 V.** Method: DFT (RPBE), (110) rutile / (001) perovskite terminations, standard ZPE−TΔS and H₂O/H₂ referencing as in A1. **Your η values should be reported as distance from this volcano line**, not just absolute numbers.

> Sanity-check summary for your data: the correct 3d-rutile expectation is that β-MnO₂ is the most active 3d rutile (your Mn = 0.89 V is in the plausible band but high), while CrO₂/NiO₂/CoO₂ are strongly magnetic/metastable and are exactly the cases where plain PBE mis-ranks them — consistent with your suspiciously high Cr (1.73) and Ni (1.75) and the Co/Cu convergence failures.

---

## B. DFT SETTINGS BEST PRACTICE FOR RUTILE TM OXIDES (2015–2026)

**B1. Xu, Rossmeisl, Kitchin (2015). "A Linear Response, DFT+U Study of Trends in the Oxygen Evolution Activity of Transition Metal Rutile Dioxides."** *J. Phys. Chem. C* 119(9), 4827–4833. DOI: **10.1021/jp511426q**. OA data + SI: [Zenodo 12635](https://zenodo.org/records/12635); [Figshare collection](https://figshare.com/collections/A_Linear_Response_DFT_i_U_i_Study_of_Trends_in_the_Oxygen_Evolution_Activity_of_Transition_Metal_Rutile_Dioxides/2266405).
- **The single most relevant paper to your project** — same material class (transition-metal rutile dioxides), same descriptor. Key finding: applying a **self-consistent linear-response (Cococcioni-style) U always makes adsorption energies more endothermic** (weaker binding), shifting metals rightward on the volcano and changing the activity ranking. Message: the choice U = 0 vs linear-response U is *not* cosmetic for 3d rutiles — it can flip which of your metals looks best. Linear-response U values are large for 3d rutiles.

**B2. Lim, Park, Kim, Jung, Kwak (2021). "First-Principles Design of Rutile Oxide Heterostructures for Oxygen Evolution Reactions."** *Front. Energy Res.* 9, 606313. DOI: **10.3389/fenrg.2021.606313**. **Fully OA:** [Frontiers](https://www.frontiersin.org/articles/10.3389/fenrg.2021.606313/full).
- Directly usable recipe. **PBE+U with U (from Xu 2015): Ti 4.95, V 2.0, Cr 7.15, Mn 6.63, Nb 3.32, Ru 6.73, Rh 5.97, Ir 5.91, Pt 6.25 eV.** Facet: **rutile (110), the most stable termination.** Magnetic conventions: **nonmagnetic for TiO₂, NbO₂, RuO₂, RhO₂, IrO₂, PtO₂; ferromagnetic for CrO₂ and MnO₂.** (Note: real β-MnO₂ is antiferromagnetic — FM is a common but imperfect approximation; test both.) This gives you concrete U for Cr and Mn today; for Fe/Co/Ni/Cu rutile you must derive linear-response U (B1) or borrow from oxide-consistent sets.

**B3. Swathilakshmi, Devi, Sai Gautam (2023). "Performance of the r2SCAN Functional in Transition Metal Oxides."** *J. Chem. Theory Comput.* 19(13), 4202–4215. DOI: **10.1021/acs.jctc.3c00030**. **OA (author copy):** [sai-mat-group.github.io](https://sai-mat-group.github.io/papers/swathilakshmi-jctc/).
- Benchmarks r2SCAN and r2SCAN+U across binary 3d TMOs (oxidation enthalpies, lattice parameters, on-site magnetic moments, band gaps) and gives per-metal optimal U for r2SCAN. r2SCAN(+U) reproduces SCAN-quality ground states at **lower cost than SCAN** — the current best-practice functional choice for 3d oxides. Adding U still needed for correct gaps/moments/localization even with meta-GGA.

**B4. García-Mota, Bajdich, Viswanathan, Vojvodic, Bell, Nørskov (2012). "Importance of Correlation in Determining Electrocatalytic Oxygen Evolution Activity on Cobalt Oxides."** *J. Phys. Chem. C* 116(39), 21077–21082. DOI: **10.1021/jp306303y**. **OA:** [OSTI 1382933](https://www.osti.gov/biblio/1382933).
- Demonstrates that **DFT+U is *required* to recover experimental OER trends on strongly-correlated cobalt oxides** — directly relevant to your failed Co endmember. U lowers predicted activity vs plain PBE. Also builds a surface Pourbaix diagram (bridge to Section C).

**B5. García-Mota, Vojvodic, Metiu, Man, Su, Rossmeisl, Nørskov (2011). "Tailoring the Activity for Oxygen Evolution Electrocatalysis on Rutile TiO₂(110) by Transition-Metal Substitution."** *ChemCatChem* 3(10), 1607–1611. DOI: **10.1002/cctc.201100160**. **[PAYWALLED — flag for library access]**; [SUNCAT record](https://suncat.stanford.edu/publications/tailoring-activity-oxygen-evolution-electrocatalysis-rutile-tio2110-transition-metal).
- Template for M-substituted rutile (110) OER; establishes coverage/cus-site conventions and how transition-metal dopants move O*/OH* binding.

**B6. Tripković, Hansen, García-Lastra, et al. (2018). "Comparative DFT+U and HSE Study of the Oxygen Evolution Electrocatalysis on Perovskite Oxides."** *J. Phys. Chem. C* 122(2), 1135–1147. DOI: **10.1021/acs.jpcc.7b07660**. **[PAYWALLED]**; [DTU Orbit](https://orbit.dtu.dk/en/publications/comparative-dftu-and-hse-study-of-the-oxygen-evolution-electrocat/).
- Quantifies **how sensitive heats of formation and OER overpotentials are to U (0/3/5 eV) and to HSE exact-exchange α (0/0.15/0.25/0.35)** for B = Cr, Mn, Fe, Co, Ni, Cu oxides. Use it to set honest error bars on functional choice (Section D) even though it is perovskite, not rutile — the B-cation sensitivity carries over.

**Magnetic-state / metastability protocols (the fix for the Co, Cu, Cr failures):**

**B7. Allen, Watson (2014). "Occupation matrix control of d- and f-electron localisations using DFT+U."** *Phys. Chem. Chem. Phys.* 16(39), 21016–21031. DOI: **10.1039/C4CP01083C**. OA PDF: [SciSpace](https://scispace.com/pdf/occupation-matrix-control-of-d-and-f-electron-localisations-37xxf0ys6b.pdf); VASP tool: [WatsonGroupTCD/Occupation-matrix-control-in-VASP](https://github.com/WatsonGroupTCD/Occupation-matrix-control-in-VASP).
- The canonical reference for **why DFT+U converges to metastable electronic minima** (different d-orbital occupations → large total-energy differences and irreproducible results — exactly the "spin/magnetic multistability" failure). Three documented cures: **occupation-matrix control (OMC), U-ramping, and quasi-annealing.** Directly actionable to rescue Co/Cu/Cr endmembers.

**B8. Liang, et al. (2022). "Anti-Ferromagnetic RuO₂: A Stable and Robust OER Catalyst over a Large Range of Surface Terminations."** *J. Phys. Chem. C* 126(3). DOI: **10.1021/acs.jpcc.1c08700**. OA PDF: [U. Twente repository](https://ris.utwente.nl/ws/files/276607080/Liang_2022_Anti_ferromagnetic_ruo_a_stable_and_1_.pdf).
- Shows the surface magnetic moment of Ru changes with O/OH coverage and that **magnetic ordering (here AFM RuO₂) materially affects computed OER energetics and the stable termination** — a concrete demonstration that you must initialize slabs from the correct bulk magnetic ground state (FM for CrO₂, AFM for β-MnO₂, etc.), not a default guess.

**B9. (bulk→surface shortcut) "Prediction of O and OH Adsorption on Transition Metal Oxide Surfaces from Bulk Descriptors."** *ACS Catal.* 2024, 14. DOI: **10.1021/acscatal.4c00111**. **[PAYWALLED]**; [ACS landing](https://pubs.acs.org/doi/10.1021/acscatal.4c00111).
- Modern data-driven mapping from cheap bulk descriptors to O*/OH* adsorption — useful for screening before running full magnetic slab convergence.

**Slab conventions (rutile 110):** stable facet is (110); model the coordinatively-unsaturated (cus) metal row as the active site with bridging O rows saturated; ≥ 4 O–M–O tri-layers with the bottom 2 fixed at bulk positions; ≥ 15 Å vacuum + dipole correction; check O*/OH*/OOH* at the relevant coverage rather than the clean surface (coverage self-consistency, Section C).

---

## C. BEYOND-THERMODYNAMIC-DESCRIPTOR CRITIQUES & UPGRADES

**C1. Surface Pourbaix / resting-state termination (the highest-value critique).**
**Hansen, Rossmeisl, Nørskov (2008). "Surface Pourbaix diagrams and oxygen reduction activity of Pt, Ag and Ni(111) surfaces studied by DFT."** *Phys. Chem. Chem. Phys.* 10(25), 3722–3730. DOI: **10.1039/b803956a**. OA: [CORE](https://core.ac.uk/outputs/13720450/), [Academia.edu](https://www.academia.edu/27268757/).
- Foundational method for building **surface Pourbaix diagrams** — the O/OH coverage that is thermodynamically stable as a function of U and pH. **Critique for your project: under OER potentials (>1.5 V RHE) the rutile cus site is usually O-covered or forms higher oxides, so the clean/low-coverage surface you compute η on may not be the real resting surface.** This changes which surface enters the free-energy diagram and can shift η by several tenths of a volt.
- Applied to rutile OER specifically: **"Electrochemical Surface Composition of Iridium Oxide IrO₂(110): Implications for the OER Mechanism," *ACS Omega* 2025**, DOI **10.1021/acsomega.5c10410** ([PMC12854491](https://pmc.ncbi.nlm.nih.gov/articles/PMC12854491/)) — first-principles Pourbaix shows OER on IrO₂(110) proceeds from a **hydrotrioxide (–OOOH) termination**, not the textbook cus-O surface. Complemented by **"OER on IrO₂(110) is governed by Walden-type mechanisms," *Nat. Commun.* 2025**, DOI **10.1038/s41467-025-61367-z** (OA).

**C2. Lattice-oxygen mechanism (LOM) vs adsorbate-evolution mechanism (AEM) — the mechanism your 4-step descriptor cannot see.**
**Grimaud, Diaz-Morales, Han, et al. (2017). "Activating lattice oxygen redox reactions in metal oxides to catalyse oxygen evolution."** *Nat. Chem.* 9(5), 457–465. DOI: **10.1038/nchem.2695**. **[PAYWALLED — flag for library access]**; abstract + summary via [Experts@Minnesota](https://experts.umn.edu/en/publications/activating-lattice-oxygen-redox-reactions-in-metal-oxides-to-cata/).
- ¹⁸O isotope-labelling proof that O₂ can originate from **lattice oxygen**, increasingly so with higher metal–oxygen covalency. AEM-only descriptors miss this pathway entirely, and LOM can undercut the 0.37 V AEM scaling floor.
- Computational-pitfalls companion: **Exner (2021). "On the Lattice Oxygen Evolution Mechanism: Avoiding Pitfalls."** *ChemCatChem* 13. DOI: **10.1002/cctc.202101049** ([Wiley](https://chemistry-europe.onlinelibrary.wiley.com/doi/abs/10.1002/cctc.202101049)) — how to set up (and mis-set-up) LOM free-energy diagrams with vacancy refilling.

**C3. Free-energy-span / kinetic-aware descriptor (cheap upgrade over pure thermodynamic η).**
- **Exner (2021). "A Universal Descriptor for the Screening of Electrode Materials for Multiple-Electron Processes: Beyond the Thermodynamic Overpotential."** *ACS Catal.* 11(6), 3234–3241. DOI: **10.1021/acscatal.0c03865**. **[PAYWALLED]**.
- **Exner (2023). "Materials Screening by the Descriptor Gmax(η): The Free-Energy Span Model in Electrocatalysis."** *ACS Catal.* 13(7). DOI: **10.1021/acscatal.2c03997**. **[PAYWALLED]**; [PubMed 36776387](https://pubmed.ncbi.nlm.nih.gov/36776387/).
- **Exner (2024). "Four Generations of Volcano Plots for the OER: Beyond Proton-Coupled Electron Transfer Steps?"** *Acc. Chem. Res.* 57. DOI: **10.1021/acs.accounts.4c00048**. **OA:** [PMC11080045](https://pmc.ncbi.nlm.nih.gov/articles/PMC11080045/).
- The **G_max(η)** descriptor is computed from the *same* free-energy diagram you already have (same cost as η_thermo) but reads the largest free-energy span at a working overpotential — much closer to kinetics than the potential-determining-step overpotential. Nearly free accuracy upgrade.
- Mechanism switching at the apex: **Exner (2023). "On the mechanistic complexity of oxygen evolution: potential-dependent switching of the mechanism at the volcano apex."** *Mater. Horiz.* 10. DOI: **10.1039/D3MH00047H** ([OA HTML](https://pubs.rsc.org/en/content/articlehtml/2023/mh/d3mh00047h)).

**C4. Constant-potential / grand-canonical DFT (fixes the constant-charge flaw of CHE).**
**Melander, Kuisma, Christensen, Honkala (2019). "Grand-canonical approach to density functional theory of electrocatalytic systems."** *J. Chem. Phys.* 150(4), 041706. DOI: **10.1063/1.5047829**. **OA:** [ChemRxiv](https://chemrxiv.org/engage/chemrxiv/article-details/60c73e98337d6cdd8be26388), [JYX PDF](https://jyx.jyu.fi/bitstream/handle/123456789/60925/1/melanderym1.pdf).
- CHE fixes charge and infers potential; real electrochemistry fixes potential. GC-DFT floats electron number to pin the Fermi level to the electrode potential, giving explicit ΔG(U). Expensive but the rigorous version of what you approximate.

**C5. Explicit solvation / interfacial water (H-bond stabilization of OH* and OOH*).**
- **"Solvation Effects for Oxygen Evolution Reaction Catalysis on IrO₂(110)."** *J. Phys. Chem. C* 2017, 121. DOI: **10.1021/acs.jpcc.7b02383**. **[PAYWALLED]**.
- **Inico, et al. (2024). "Stability and Solvation of Key Intermediates of Oxygen Evolution on TiO₂, RuO₂, IrO₂ (110) Surfaces: A Comparative DFT Study."** *ChemCatChem* 16. DOI: **10.1002/cctc.202400813**. **[PAYWALLED]**; [ResearchGate](https://www.researchgate.net/publication/382409953). Compares single-water, bilayer, and AIMD interface solvation — quantifies how explicit water stabilizes H-bond-donating OH*/OOH* and even a non-standard –OO(H) intermediate.
- Most recent (2026): **Qiu, et al. (2026). "Potential-Dependent Oxygenated Surface Phases and Interfacial Water Layers Underlie the High Overpotential and Mechanistic Switching of Oxygen Evolution on RuO₂."** *Angew. Chem. Int. Ed.* DOI: **10.1002/anie.202521856**. **[PAYWALLED]** — combines potential-dependent terminations (C1) + interfacial water (C5) for rutile RuO₂; the current state of the art for this exact system.

---

## D. ACCURACY REALITY CHECK

**D1. Fabbri, Schmidt (2018). "Oxygen Evolution Reaction—The Enigma in Water Electrolysis."** *ACS Catal.* 8(10), 9765–9774. DOI: **10.1021/acscatal.8b02712**. [ACS landing](https://pubs.acs.org/doi/10.1021/acscatal.8b02712) (**[PAYWALLED]** full text).
- Community-standard honest appraisal: the CHE/volcano descriptor captures *trends* across broad oxide families but routinely mis-ranks within a family and cannot reconcile activity with the stability/reconstruction that dominates real electrodes.

**D2. Jones, Teschner, Piccinin (2024). "Toward Realistic Models of the Electrocatalytic Oxygen Evolution Reaction."** *Chem. Rev.* 124(15), 9136–9223. DOI: **10.1021/acs.chemrev.4c00171**. **OA:** [OSTI 2406541](https://www.osti.gov/pages/biblio/2406541).
- The comprehensive 2024 synthesis of everything in Section C: why static, constant-charge, gas-phase-referenced CHE diagrams are a *starting point*, and what a "realistic" model adds (constant potential, explicit interface, coverage, LOM, kinetics). The one review to cite when stating your method's limitations.

**D3. Exner (2024, Acc. Chem. Res., cited above C3)** and **"Toward data- and mechanistic-driven volcano plots," *Electrochem. Sci. Adv.* 2024, DOI 10.1002/elsa.202200014** — quantify that ranking by thermodynamic η "cannot reproduce experimental trends reasonably well," motivating G_max(η).

**D4. Reaction-descriptors mini-review — Curr. Opin. Electrochem. 2022.** ScienceDirect PII **S2451910322001090** ([landing](https://www.sciencedirect.com/science/article/pii/S2451910322001090)). **[PAYWALLED — flag for library access]** (authors/DOI not fully resolvable from OA metadata). Surveys thermodynamic vs electronic descriptors and where each fails.

**Practical error bars to state honestly in the write-up:**
- Individual adsorption-energy error with GGA(-RPBE/BEEF-vdW): **~0.2 eV**, propagating to **~0.2–0.4 V** uncertainty in η. Report η to no better than ±0.2 V.
- The 3.2 eV OOH–OH scaling has **±~0.2 eV** intrinsic scatter → the volcano itself carries ~0.1–0.2 V of built-in noise; differences between two metals smaller than this are not meaningful.
- Functional/U/α choice moves oxide overpotentials by **several tenths of a volt** (B6), and choice of resting-surface termination (C1) by a comparable amount — these are systematic, not random, so always report which functional/U/termination was used.
- The framework predicts *trends across families* better than *absolute η* or *within-family ranking*; state ranking claims, not absolute-activity claims.

---

## TOP 10 ACTIONABLE UPGRADES (ranked)

1. **Switch 3d-rutile calculations to PBE+U (or r2SCAN+U) with documented per-metal U; report U-sensitivity.** Backing: Xu 2015 (10.1021/jp511426q), Lim 2021 (10.3389/fenrg.2021.606313, gives Cr 7.15 / Mn 6.63 eV etc.), Swathilakshmi 2023 (10.1021/acs.jctc.3c00030), García-Mota 2012 (10.1021/jp306303y). *Cost: moderate (re-run existing slabs with adjusted +U; derive linear-response U for Fe/Co/Ni/Cu).* **Highest priority — likely explains the anomalous Cr/Ni η and Co/Cu failures.**
2. **Fix magnetic multistability with occupation-matrix control / U-ramping / quasi-annealing, and initialize each slab from its correct bulk magnetic ground state** (CrO₂ FM half-metal, β-MnO₂ AFM, test FM/AFM for Co/Ni/Cu). Backing: Allen & Watson 2014 (10.1039/C4CP01083C + VASP OMC tool), Liang 2022 (10.1021/acs.jpcc.1c08700), Lim 2021 magnetic conventions. *Cost: moderate — this is what rescues the Co and Cu endmembers.*
3. **Report η as position on the Man 2011 volcano (descriptor ΔG_O − ΔG_OH) and against the 0.37 V AEM scaling floor, not as bare numbers.** Backing: Man 2011 (10.1002/cctc.201000397), Rossmeisl 2007 (10.1016/j.jelechem.2006.11.008). *Cost: cheap — reanalysis of existing data.*
4. **Build surface Pourbaix diagrams and compute η on the actual OER-potential resting termination** (rutile cus is typically O-/OOH-covered, not clean). Backing: Hansen 2008 (10.1039/b803956a), IrO₂(110) hydrotrioxide *ACS Omega* 2025 (10.1021/acsomega.5c10410), García-Mota 2012. *Cost: moderate — a handful of extra coverage/termination calculations per metal.*
5. **Add the G_max(η) free-energy-span descriptor alongside η_thermo.** Backing: Exner 2021 (10.1021/acscatal.0c03865), 2023 (10.1021/acscatal.2c03997), 2024 (10.1021/acs.accounts.4c00048, OA). *Cost: cheap — computed from the free-energy diagrams you already have.*
6. **State explicit error bars (±0.2–0.4 V) and frame results as trend/ranking, not absolute activity.** Backing: Fabbri & Schmidt 2018 (10.1021/acscatal.8b02712), Jones/Teschner/Piccinin 2024 (10.1021/acs.chemrev.4c00171, OA). *Cost: cheap — a paragraph in the discussion.*
7. **Add implicit solvation, then spot-check with explicit water (bilayer/AIMD) on 1–2 metals to correct OH*/OOH* H-bond stabilization.** Backing: IrO₂(110) solvation *JPCC* 2017 (10.1021/acs.jpcc.7b02383), Inico 2024 (10.1002/cctc.202400813), Qiu 2026 (10.1002/anie.202521856). *Cost: moderate (implicit) → expensive (AIMD).*
8. **Test the lattice-oxygen mechanism (LOM) for the most covalent/most-active metals (Ni, Co, Cu oxides) where AEM may not be the operative path.** Backing: Grimaud 2017 (10.1038/nchem.2695), Exner LOM-pitfalls 2021 (10.1002/cctc.202101049). *Cost: moderate — vacancy-refilling free-energy diagrams.*
9. **Benchmark functional choice (PBE vs PBE+U vs r2SCAN+U vs HSE) on RuO₂/IrO₂ where experimental η is known, to calibrate before trusting 3d numbers.** Backing: Tripković 2018 (10.1021/acs.jpcc.7b07660), Swathilakshmi 2023, García-Mota 2012. *Cost: moderate.*
10. **(Stretch) Move potential-determining steps to constant-potential / grand-canonical DFT.** Backing: Melander 2019 (10.1063/1.5047829, OA); framing in Jones 2024 Chem. Rev. *Cost: expensive — do only for final validation of best candidates.*

**Fastest wins for the current failures:** #1 + #2 together (correct functional + correct magnetic state) are the direct fix for the Co/Cu non-convergence and the physically-implausible Cr (1.73 V) and Ni (1.75 V) overpotentials; #3 + #5 + #6 are near-zero-cost reanalysis upgrades that immediately raise methodological rigor.
