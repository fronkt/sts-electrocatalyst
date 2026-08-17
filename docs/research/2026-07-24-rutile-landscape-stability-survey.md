# Deep-Research Report 4/4 — Rutile MO₂ OER: Sanity Check, Prior Art, Stability, Mechanism, Novelty

> **Provenance:** produced 2026-07-23/24 by a literature-survey agent (WebSearch/WebFetch over
> publisher pages, PMC, arXiv, OA repositories — legal-first sourcing, no Sci-Hub). One of four
> parallel surveys distilled into [docs/28](../28-electrocatalyst-revival-plan.md). Verbatim archive.
> Verification levels flagged per item: [FETCHED] = page retrieved and read; [SEARCH] = metadata
> from search index only; [PAYWALLED] = no OA, abstract only.

**Scope note:** project values under review — η(Mn)=0.89, η(Fe)=1.26, η(Cr)=1.73, η(Ni)=1.75 V (CHE 4-step, rutile-(110)-type slabs); Co, Cu failed SCF.

---

## A. SANITY CHECK — Published rutile-(110) OER overpotentials on comparable footing

**A1. The canonical benchmark — Man et al. 2011 (the paper the CHE 4-step method descends from).**
Man, Su, Calle-Vallejo, Hansen, Martínez, Inoglu, Kitchin, Jaramillo, Nørskov, Rossmeisl (2011), *ChemCatChem* 3(7):1159–1165. **DOI 10.1002/cctc.201000397.** OA metadata verified at DTU Orbit: https://orbit.dtu.dk/en/publications/universality-in-oxygen-evolution-electrocatalysis-on-oxide-surfac/ [FETCHED — metadata/authors/venue confirmed; the numeric table is behind Wiley].
- Method: RPBE, computational SHE, descriptor **η set by ΔG_O − ΔG_OH**; the universal relation **ΔG_OOH − ΔG_OH ≈ 3.2 eV** (vs ideal 2.46) is what caps planar oxides at η ≳ 0.3–0.4 V.
- **Canonical rutile-(110) values (widely reproduced; one independent search hit independently returned "0.42 V" for RuO₂(110)):** RuO₂(110) η ≈ **0.42 V**, IrO₂(110) η ≈ **0.56 V**. TiO₂ and PtO₂ sit far down the volcano (η > 1 V). Man's rutile set is small (RuO₂, IrO₂, TiO₂, PtO₂-type) — **it does NOT contain CrO₂/FeO₂/CoO₂/NiO₂/CuO₂**, so the project's 3d numbers have no direct Man counterpart.

**A2. The closest published equal-footing 3d-rutile-(110) set — Lim, Park, Kim, Jung, Kwak (2021),** "First-Principles Design of Rutile Oxide Heterostructures for Oxygen Evolution Reactions," *Frontiers in Energy Research* 9:606313. **DOI 10.3389/fenrg.2021.606313.** OA (CC BY): https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2021.606313/full [FETCHED — oxide list, functional, U values confirmed; per-oxide η are in Supplementary tables the fetch model could not render].
- Screened **11 rutile MO₂ on rutile (110): VO₂, CrO₂, MnO₂, NbO₂, RuO₂, RhO₂, SnO₂, TaO₂, OsO₂, IrO₂, PtO₂**, both as bulk (110) and as monolayers on a TiO₂(110) substrate.
- **Functional GGA-PBE+U**, with sizeable U: **Cr 7.15, Mn 6.63, Ru 6.73, Ir 5.91, Pt 6.25 eV** (also Ti 4.95). Descriptor ΔG_OOH−ΔG_O.
- Result: **RuO₂ and IrO₂ near the volcano top; CrO₂ and MnO₂ sit well down-slope (higher η)** — qualitatively consistent with the project's η(Cr) and η(Mn) being far above the RuO₂ benchmark. **Crucially, FeO₂, CoO₂, NiO₂, CuO₂ were excluded** (they are not viable rutile endmembers — see §C).

**A3. β-MnO₂ specifically.** Multiple DFT studies use the ΔG_O−ΔG_HO volcano for α-/β-MnO₂ (e.g., the β-MnO₂ Ir/Ru co-substitution study, §B4); pristine β-MnO₂(110) CHE overpotentials in the literature cluster **~0.7–1.0+ V** depending on facet/coverage/U — so the project's **η(Mn)=0.89 V is squarely in the physically expected range** for a pristine β-MnO₂ slab.

### Verdict on the project's numbers
- **Ordering is physically sane.** Mn best (0.89) < Fe (1.26) < Cr (1.73) ≈ Ni (1.75). β-MnO₂ being the strongest 3d rutile is exactly what the literature implies (it is the *only* genuinely rutile, ambient-stable 3d oxide and a known modest OER catalyst). All four exceed the RuO₂/IrO₂ 0.42/0.56 V benchmark — correct: pristine 3d rutiles are poor planar OER catalysts.
- **No clean published pristine-slab counterpart exists for CrO₂/FeO₂/NiO₂(110) on identical footing**, so a strict ">0.3 V discrepancy" check is not possible — *this absence is itself the novelty hook (§E).*
- **Discrepancy risk flags (any of these can move η by >0.3 V):**
  1. **Magnetic state.** CrO₂ is a ferromagnetic half-metal; β-MnO₂ is antiferromagnetic; FeO₂/CoO₂/NiO₂ have competing spin states. If the slab converged to the wrong spin, ΔG_O shifts by several tenths of a volt. The AFM-RuO₂ study (Klyukin/Rossmeisl group, *J. Phys. Chem. C* 2021/2022, **DOI 10.1021/acs.jpcc.1c08700** [SEARCH]) shows spin/termination alone swings RuO₂(110) across η ≈ 0.4–0.5 V.
  2. **U value.** Lim used U up to ~7 eV on Cr/Mn/Ru. O-2p position (hence ΔG_O) is very U-sensitive; if a run used U=0 or a different U, η(Cr)/η(Ni) could be off by >0.3 V vs a +U reference. Report the U used.
  3. **Termination/coverage.** Bare cus-metal vs O-precovered (2O_b, 2O_b2O_c) terminations move η by 0.3–0.5 V (explicit in Lim 2021 and the RuO₂ coverage/GC-DFT work). CHE on a single fixed termination is a lower bound.
  4. **Co, Cu SCF failure is a physical signal, not a nuisance** — rutile CoO₂/CuO₂ are not real ambient polymorphs and Cu(IV) is electronically unfavorable (§C), so non-convergence is expected.

---

## B. DOPED/MIXED RUTILE OER LANDSCAPE — what's mined vs open

**Heavily mined: 3d-cation doping INTO RuO₂/IrO₂ (acidic PEM focus).** This space is saturated 2019–2026:
- **B1. Lin, Tian, Zhang, Ma, Jiang, Deibert, Ge, Chen (2019),** "Chromium-ruthenium oxide solid solution…acidic OER," *Nature Communications* 10:162. **DOI 10.1038/s41467-018-08144-3.** OA: https://pmc.ncbi.nlm.nih.gov/articles/PMC6329788/ [FETCHED]. **Cr₀.₆Ru₀.₄O₂ rutile solid solution; η = 178 mV @10 mA cm⁻²** in 0.5 M H₂SO₄, stable 10 h / 10,000 cycles (11 mV loss). DFT: Cr raises O p-band center (−2.91→−2.48 eV), oxidizes Ru (+1.73→+1.92 |e|), lowers RDS barrier **2.02→1.87 eV**, and suppresses acidic dissolution. This is the flagship earth-abundant-doped-rutile result.
- **B2. Feng et al. (2025),** "GC-DFT simulation of coverage and potential effect for OER on RuO₂-based electrocatalyst," *Journal of Catalysis*. ScienceDirect S0021951725000338 [PAYWALLED/SEARCH]. **Grand-canonical DFT over M-RuO₂, M = Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn** — i.e., the project's exact 3d set, but as *dopants in RuO₂*, not endmembers. Finds **Co-RuO₂ and Cr-RuO₂** best. Directly overlaps and partly preempts a naive "dope 3d into rutile" plan.
- **B3. JACS 2024,** "Designing 3d Transition Metal Cation-Doped MRuOₓ as Durable Acidic OER Electrocatalysts for PEM," **DOI 10.1021/jacs.4c04096** **[HELD LOCALLY: `papers/Sun-2024_JACS_3d-cation-doped-MRuOx-acidic-OER.pdf`]**; and **B3b. JACS 2025,** "Dual-Descriptor-Guided Screening of Stable Metal-Doped RuO₂ Catalysts for Acidic OER," **DOI 10.1021/jacs.5c17145** [PAYWALLED/SEARCH]. Together these show **stability-and-activity dual-descriptor screening of metal-doped RuO₂ is already state-of-the-art as of 2025.**
- **B4. Rational design of β-MnO₂ via Ir/Ru co-substitution (2024),** *ACS Catalysis*, **DOI 10.1021/acscatal.4c05989** **[HELD LOCALLY: `papers/Deng-2025_ACSCatal_betaMnO2-IrRu-cosubstitution.pdf`]**. DFT+exp; substitution drives AEM→OPM (oxide-path). Shows the *reverse* direction (noble metal into 3d rutile) is also being worked.
- **B5. (M,Ru)O₂ (M = Mg, Zn, Cu, Ni, Co) rutiles as acidic OER catalysts in MEAs,** *Chemistry of Materials* 2020, **DOI 10.1021/acs.chemmater.0c01884** **[HELD LOCALLY: `papers/Burnett-2020_ChemMater_M-RuO2-rutiles-MEA.pdf`]**. Earth-abundant divalent metals into rutile RuO₂ to cut Ru loading — the mixed-rutile compositional space is being explored experimentally.

**Broad oxide OER screening / ML (context for "is earth-abundant mixed 3d rutile done?"):**
- **B6. Tran et al. (2024),** "Rational design of (acid-stable / nanoscale-stabilized) oxide catalysts for OER with OC22," **arXiv:2311.00784.** OA: https://arxiv.org/html/2311.00784v2 [FETCHED]. GNN + **Pourbaix decomposition energy** over **4,119 oxides** (pH 1, U=1.8 V, 80 °C); criteria include η<0.75 V on ≥2 facets, E_hull≤0.1, cost<RuO₂ → **48 bulk + 69 nanoscale acid-stable candidates.** This is the modern "screen everything with stability built in" template.
- **B7. DigCat closed loop (2025),** "Closed-Loop Framework for Discovering Stable and Low-Cost Bifunctional Metal Oxide Catalysts…in Acid," *JACS*, **DOI 10.1021/jacs.5c04079** **[HELD LOCALLY: `papers/Jia-2025_JACS_closed-loop-bifunctional-oxide-discovery.pdf`]**. Data-mining + microkinetics + experiment.
- **B8. Zhou/Sargent (2016),** "Homogeneously dispersed multimetal oxygen-evolving catalysts," *Science* 352:333. **DOI 10.1126/science.aaf1525** [SEARCH]. **~3,500 earth-abundant mixed oxides screened (alkaline)** → Ni-Fe + third metal (Al/Ga/Cr). The alkaline earth-abundant mixed-oxide space is heavily mined.

**Bottom line for B:** The **"dope/mix 3d cations into RuO₂/IrO₂ for acidic OER"** niche is crowded (2019–2026, incl. the exact 9-element dopant set via GC-DFT in B2). **"Earth-abundant *noble-metal-free* mixed 3d rutile OER"** as pristine endmembers is *not* systematically screened — because those endmembers are mostly unstable/nonexistent (§C), which is precisely why the field jumped to RuO₂-hosted doping. Open space is at the intersection of **endmember stability filtering + spin resolution**, not raw activity.

---

## C. STABILITY — the make-or-break critique, per endmember

**Framework citations (cite these for any Pourbaix claim):**
- **C0a. Persson, Waldwick, Lazič, Ceder (2012),** "Prediction of solid-aqueous equilibria: scheme to combine first-principles calculations of solids with experimental aqueous states," *Phys. Rev. B* 85:235438. **DOI 10.1103/PhysRevB.85.235438** [SEARCH]. The original computed-Pourbaix framework (now the Materials Project Pourbaix app).
- **C0b. Wang, Guo, Montoya, Persson (2020),** "Predicting aqueous stability of solid with computed Pourbaix diagram using SCAN functional," *npj Computational Materials* 6:160. **DOI 10.1038/s41524-020-00430-3.** OA preprint (ChemRxiv): https://chemrxiv.org/engage/chemrxiv/article-details/60c74f124c8919eafdad3b3a [SEARCH]. Defines the **Pourbaix decomposition energy (ΔG_pbx)** metric and adds **SCAN+U** corrections for TM oxides — the recommended stability filter for a screening project.

**Per-endmember verdict (rutile synthesizability + Pourbaix @ OER potentials ~1.6–2.0 V vs SHE):**

| Endmember | Rutile ambient-stable? | Pourbaix under OER | Verdict |
|---|---|---|---|
| **β-MnO₂ (Mn)** | **YES** — pyrolusite is genuinely rutile & ambient-stable | Acidic: dissolves/disproportionates to Mn²⁺/MnO₄⁻ at OER potentials (classic Mn Pourbaix); more robust in neutral/alkaline | **Only physically meaningful endmember; acid-unstable** |
| **CrO₂ (Cr)** | Metastable — rutile forms but **decomposes to Cr₂O₃**; made only by CVD from CrO₃ (ferromagnetic half-metal) [SEARCH: ScienceDirect "Chromium Dioxide" overview; arXiv cond-mat/0605600] | Above ~0.9–1.2 V Cr oxidizes to **soluble chromate CrO₄²⁻/Cr₂O₇²⁻** at essentially all pH → total dissolution at OER | **Dissolves as chromate — non-viable OER material** |
| **FeO₂ (Fe)** | **NO rutile at ambient** — pyrite-type FeO₂ only stable **>74 GPa** (Earth's lower mantle) [SEARCH: OSTI 1540924; ScienceDirect S0925838818323582] | N/A (phase doesn't exist as a solid electrode ambient) | **Fictitious ambient phase; slab is a model artifact** |
| **CoO₂ (Co)** | Not rutile — real "CoO₂" is the **layered O3/CdI₂-type delithiated LiCoO₂** [SEARCH: ScienceDirect S037877539900110X] | Layered CoO₂ is metastable; under OER Co oxides reconstruct to CoOOH (§D) | **Wrong polymorph; SCF failure expected** |
| **NiO₂ (Ni)** | Not rutile — real "NiO₂" is **layered delithiated LiNiO₂**; rutile NiO₂ not a thermodynamic polymorph | Ni oxides → NiOOH oxyhydroxide under OER (§D) | **Wrong polymorph; η=1.75 physically meaningless** |
| **CuO₂ (Cu)** | **NO** — Cu(IV) unfavorable; only superoxo/peroxo clusters, no bulk rutile CuO₂ [SEARCH: *J. Phys. Chem. A* "Systematic Study of Oxo/Peroxo/Superoxo Isomers of 3d-Metal Dioxides," DOI 10.1021/jp002252s] | N/A | **Does not exist; SCF failure expected** |

**Consequence:** Of the six, **only β-MnO₂ is a real rutile endmember**, and even it is acid-unstable. CrO₂ dissolves as chromate; FeO₂/CuO₂ don't exist at ambient; CoO₂/NiO₂ are layered, not rutile. **A pristine-rutile OER η for FeO₂/CoO₂/NiO₂/CuO₂ is a number for a phase that isn't a real electrode.** Any screening result must be gated by ΔG_pbx (C0b) or it is physically meaningless — this is the single most important critique of the current project.

---

## D. MECHANISM CAVEATS — LOM, reconstruction, oxyhydroxide active phase

The pristine-rutile-slab assumption fails hardest exactly for Mn/Co/Ni/Fe:
- **D1. In-situ/operando reviews.** "In situ/operando analysis of surface reconstruction of transition-metal-based OER electrocatalysts," *Cell Reports Physical Science* 2021 [SEARCH]; and **"Toward data-driven predictive modeling of electrocatalyst stability and surface reconstruction," *J. Chem. Phys.* 163:040902 (2025)** [SEARCH] — both document that 3d oxides **restructure into (oxy)hydroxides under anodic bias**; the pristine facet is not the working surface.
- **D2. Dionigi/Strasser et al. (2020),** "In-situ structure and catalytic mechanism of NiFe and CoFe layered double hydroxides during OER," *Nature Communications* 11:2522. **DOI 10.1038/s41467-020-16237-1.** OA: https://www.nature.com/articles/s41467-020-16237-1 [SEARCH]. γ-(oxy)hydroxide with ~8% lattice contraction is the active phase.
- **D3. PNAS 2023,** "Triggered lattice-oxygen oxidation with active-site generation and self-termination of surface reconstruction during water oxidation," **DOI 10.1073/pnas.2312224120** [SEARCH]. Direct LOM evidence + self-limiting reconstruction depth.
- **D4.** Mn oxides: LOM/Mars–van Krevelen and dissolution–redeposition are well established; the β-MnO₂ Ir/Ru work (B4) explicitly frames the AEM↔LOM↔OPM competition.

**Implication:** For Co/Ni/Fe especially, the CHE 4-step AEM on a pristine rutile (110) models a surface that **does not survive OER** — the active site is a reconstructed CoOOH/NiOOH/FeOOH, often operating by lattice-oxygen mechanism (outside the ΔG_OOH−ΔG_OH=3.2 eV scaling). **How screening papers hedge:** they (i) restrict claims to *acidic, dissolution-resistant rutiles* (RuO₂/IrO₂-hosted, e.g. B1–B3, B6), (ii) add a Pourbaix/ΔG_pbx stability gate (C0b, B6), and/or (iii) explicitly state pristine-slab η is an activity *descriptor*, not a prediction of the operating surface. This project must adopt at least (ii)+(iii) to be defensible.

---

## E. WHERE THE NOVELTY IS — defensible, HS-executable angles

Given A–D, raw "compute η for more rutiles" is preempted (Lim 2021, Feng 2025) and largely physically void (§C). The genuinely open, defensible angles:

**E1. Spin-multistability-resolved rutile OER screening (methodology study).** The literature confirms **no systematic paper resolves magnetic-state ambiguity** across the 3d rutile (110) OER series (search for a spin-resolved CrO₂/MnO₂/FeO₂/CoO₂/NiO₂ set returned none). CrO₂ (FM half-metal), β-MnO₂ (AFM), and the competing spin states of Fe/Co/Ni make η spin-sensitive at the >0.3 V level. **Deliverable:** for each rutile endmember, converge *all* accessible spin orderings, report η(spin) spread, and show which prior single-spin values are unreliable. This directly explains the Co/Cu SCF failures and is a clean, bounded, reproducible HS project.

**E2. Stability-FILTERED doped-rutile map (the honest version of the screen).** Couple activity (CHE η) with **ΔG_pbx from the Persson/Montoya SCAN-Pourbaix framework (C0b)** *before* reporting any candidate. Because §C kills 5 of 6 endmembers, the real map is over **RuO₂/(β-MnO₂/TiO₂/SnO₂)-host solid solutions with 3d dopants**, colored by acid- and alkaline-stability window — a 2D activity×stability Pareto plot the flagship papers (B1, B6) gesture at but rarely publish as a clean endmember-resolved figure for the earth-abundant set.

**E3. MLIP-benchmark-plus-fine-tune methodology study (leverages the existing NEP/MLIP stack).** Nobody has cleanly benchmarked a machine-learned interatomic potential (or OC22-class GNN) against DFT CHE η for the *pristine 3d rutile (110)* set, then fine-tuned on the SCF-hard cases (CrO₂ spin, Co/Ni). This reframes "some slabs failed to converge" from a bug into a **DFT-vs-MLIP transferability finding** — a very publishable HS angle.

**E4. "Why the pristine-slab descriptor breaks for 3d rutiles" — a critical case study.** Combine A (the project's η values) + C (Pourbaix nonexistence) + D (reconstruction/LOM) into a short, rigorous negative/critical result: quantify, per endmember, the gap between the pristine-slab η and the physical reality (phase doesn't exist / dissolves / reconstructs). This is defensible, honest, and needs only modest compute — and it inoculates the project against the exact critique a Regeneron STS judge would raise.

**Recommended framing:** E1+E2 combined (spin-resolved, stability-gated map) is the strongest single project; E3 is the best fit for the existing MLIP tooling; E4 is the safest "the result is the critique" fallback. Avoid a pure activity-only endmember screen — it is both preempted and physically meaningless for 5 of the 6 targets.

---

### Verification ledger
Individually fetched & read: Man 2011 (DTU Orbit metadata), Lim 2021 (Frontiers full text), Tran/OC22 2024 (arXiv HTML), Lin/Cr-Ru 2019 (PMC full text). Metadata from search index (real papers, page not individually fetched): SCAN-Pourbaix 2020, Persson 2012, Feng/GC-DFT 2025, JACS 2024/2025 doped-RuO₂, Chem. Mater. 2020, ACS Catal. 2024, JACS 2025 closed-loop, Science 2016, the reconstruction/LOM set (Cell Rep. Phys. Sci. 2021, Nat. Commun. 2020, PNAS 2023, J. Chem. Phys. 2025), and the CrO₂/FeO₂/CoO₂/NiO₂/CuO₂ existence sources. Paywalled-no-OA items are marked [PAYWALLED] and reported at abstract level only.
