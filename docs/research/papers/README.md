# Local reading copies — paywalled pulls

Seventeen publisher PDFs, pulled 2026-08-11, clearing the "paywalled-no-OA items
flagged for Purdue library pull" list in `docs/28` §9 and the `[PAYWALLED]` flags in
`docs/research/2026-07-24-methodology-survey.md`. The full set was read and integrated
against the pre-registered plan the same day — see
`docs/research/2026-08-11-paywalled-sweep-plan-implications.md`.

**The PDFs are gitignored and stay on this machine.** This repository is public;
redistributing a publisher PDF is a copyright problem however the copy was obtained. This
index is the part that gets committed, so the bibliography survives even though the files
do not. Anyone rebuilding the set pulls it from the DOIs below.

Citations are transcribed from each PDF's own front matter, not from memory. Where a PDF is
an advance-online or ASAP proof and carries no volume/pages, that is said rather than filled
in.

## Descriptors and methodology

| Local file | Citation | Why it is here |
|---|---|---|
| `Exner-2020_ACSCatal_universal-descriptor-beyond-eta.pdf` | Exner, "A Universal Descriptor for the Screening of Electrode Materials for Multiple-Electron Processes: Beyond the Thermodynamic Overpotential," *ACS Catal.* **2020**, 10, 12607–12617. [10.1021/acscatal.0c03865](https://doi.org/10.1021/acscatal.0c03865) | Primary source for G_max(η). The repo already reports a G_max(η = 0.3 V) column in `docs/29` §4b against the four `dft_eta.json` endmembers, so this is the definition that column has to match. |
| `Razzaq-Exner-2023_ACSCatal_Gmax-free-energy-span.pdf` | Razzaq & Exner, "Materials Screening by the Descriptor G_max(η): The Free-Energy Span Model in Electrocatalysis," *ACS Catal.* **2023**, 13, 1740–1758. [10.1021/acscatal.2c03997](https://doi.org/10.1021/acscatal.2c03997) | The worked screening protocol — how to read the span off a free-energy diagram, and the failure cases where G_max and η_thermo rank differently. |
| `Comer-2024_ACSCatal_O-OH-adsorption-from-bulk-descriptors.pdf` | Comer, Bothra, Lunger, Abild-Pedersen, Bajdich & Winther, "Prediction of O and OH Adsorption on Transition Metal Oxide Surfaces from Bulk Descriptors," *ACS Catal.* **2024**, 14, 5286–5296. [10.1021/acscatal.4c00111](https://doi.org/10.1021/acscatal.4c00111) | Bulk-descriptor route to ΔG_O / ΔG_OH without a surface calculation — a cheap independent check on the screen, and a cross-check on anchor offsets. |
| `Tripkovic-2018_JPCC_DFTU-vs-HSE-perovskite-OER.pdf` | Tripkovic, Hansen, Garcia-Lastra & Vegge, "Comparative DFT+U and HSE Study of the Oxygen Evolution Electrocatalysis on Perovskite Oxides," *J. Phys. Chem. C* **2018**, 122, 1135–1147. [10.1021/acs.jpcc.7b07660](https://doi.org/10.1021/acs.jpcc.7b07660) | Functional-choice benchmark (survey recommendation 9): how far +U and HSE move OER energetics on oxides, which bounds how much of our spread is functional artefact. |
| `Grimaud-2017_NatChem_lattice-oxygen-redox.pdf` | Grimaud, Diaz-Morales, Han, Hong, Lee, Giordano, Stoerzinger, Koper & Shao-Horn, "Activating lattice oxygen redox reactions in metal oxides to catalyse oxygen evolution," *Nat. Chem.* **2017**. [10.1038/NCHEM.2695](https://doi.org/10.1038/NCHEM.2695) — *this copy is the advance-online PDF and carries no volume/pages; the survey records them as 9(5), 457–465* | The lattice-oxygen mechanism (survey recommendation 8). Relevant wherever AEM may not be the operative path. |
| `Fabbri-2018_ACSCatal_OER-enigma-viewpoint.pdf` | Fabbri & Schmidt, "Oxygen Evolution Reaction — The Enigma in Water Electrolysis," *ACS Catal.* **2018**, 8, 9765–9774. [10.1021/acscatal.8b02712](https://doi.org/10.1021/acscatal.8b02712) | Short viewpoint; useful framing and citation anchor for the report's mechanism paragraph. |
| `man2011.pdf` | Man, Su, Calle-Vallejo, Hansen, Martínez, Inoglu, Kitchin, Jaramillo, Nørskov & Rossmeisl, "Universality in Oxygen Evolution Electrocatalysis on Oxide Surfaces," *ChemCatChem* **2011**, 3, 1159–1165. [10.1002/cctc.201000397](https://doi.org/10.1002/cctc.201000397) | The universal-scaling paper (3.20 eV intercept, MAE 0.17 eV, ~0.37 V planar-oxide floor). Pulled for the tabulated ΔG values, not the argument; corroborates the Divanis 3.18 ± 0.12 eV constant that P17 already uses. |
| `jp5b05338.pdf` | Curnan & Kitchin, "Investigating the Energetic Ordering of Stable and Metastable TiO2 Polymorphs Using DFT+U and Hybrid Functionals," *J. Phys. Chem. C* **2015**, 119, 21060–21071. [10.1021/acs.jpcc.5b05338](https://doi.org/10.1021/acs.jpcc.5b05338) | Pulled 2026-08-12 **by mistake for Xu 2015** (same group/journal/year — see below) and kept on merit: polymorph ordering is consistent over U *intervals* under GGA+U, while no first-principles method predicts the exact-exchange fraction — independent support for the no-hybrid-arbitration position (Tripkovic conclusion 3). |

## Solvation and the interface

These three bear on the `docs/41` *OOH problem — the pre-registered P7 trigger and the
metastable-magnetic-state relaxation — where the question is whether an implicit or bare
treatment of the intermediate is what moved the number.

| Local file | Citation | Why it is here |
|---|---|---|
| `Gauthier-2017_JPCC_solvation-IrO2-110.pdf` | Gauthier, Dickens, Chen, Doyle & Nørskov, "Solvation Effects for Oxygen Evolution Reaction Catalysis on IrO2(110)," *J. Phys. Chem. C* **2017**. [10.1021/acs.jpcc.7b02383](https://doi.org/10.1021/acs.jpcc.7b02383) — *ASAP proof; volume/pages print as XXXX on this copy* | Per-intermediate solvation corrections on the rutile (110) cus site, from the group whose CHE convention we follow. |
| `Inico-2024_ChemCatChem_stability-solvation-TiO2-RuO2-IrO2-110.pdf` | Inico, Di Liberto & Giordano, "Stability and Solvation of Key Intermediates of Oxygen Evolution on TiO2, RuO2, IrO2 (110) Surfaces: A Comparative DFT Study," *ChemCatChem* **2024**, 16, e202400813. [10.1002/cctc.202400813](https://doi.org/10.1002/cctc.202400813) | Same three (110) surfaces we anchor on, solvation and stability side by side — the closest published comparator to our anchor set. |
| `Qiu-2026_AngewChem_potential-dependent-phases-RuO2.pdf` | Qiu, Jiao, Hu, Chen & Li, "Potential-Dependent Oxygenated Surface Phases and Interfacial Water Layers Underlie the High Overpotential and Mechanistic Switching of Oxygen Evolution on RuO2," *Angew. Chem. Int. Ed.* **2026**, 65, e21856. [10.1002/anie.202521856](https://doi.org/10.1002/anie.202521856) | AIMD on the RuO2 interface; the resting termination at OER potential is not the clean surface, which is survey recommendation 4. |

## Doped-rutile screens and experimental comparators

| Local file | Citation | Why it is here |
|---|---|---|
| `Garcia-Mota-2011_ChemCatChem_TiO2-110-TM-substitution.pdf` | García-Mota, Vojvodic, Metiu, Man, Su, Rossmeisl & Nørskov, "Tailoring the Activity for Oxygen Evolution Electrocatalysis on Rutile TiO2(110) by Transition-Metal Substitution," *ChemCatChem* **2011**, 3, 1607–1611. [10.1002/cctc.201100160](https://doi.org/10.1002/cctc.201100160) | Item **B5** of the methodology survey. The original TM-substituted rutile (110) study — the direct precedent for what this project does. |
| `Sun-2024_JACS_3d-cation-doped-MRuOx-acidic-OER.pdf` | Sun *et al.*, "Designing 3d Transition Metal Cation-Doped MRuOx As Durable Acidic Oxygen Evolution Electrocatalysts for PEM Water Electrolyzers," *J. Am. Chem. Soc.* **2024**, 146, 15515–15524. [10.1021/jacs.4c04096](https://doi.org/10.1021/jacs.4c04096) | One of the "JACS 2024/2025 doped-RuO2 screens" flagged in `docs/28`. 3d-cation doping is our composition space. |
| `Cao-2026_JACS_dual-descriptor-metal-doped-RuO2.pdf` | Cao *et al.*, "Dual-Descriptor-Guided Screening of Stable Metal-Doped RuO2 Catalysts for Acidic Oxygen Evolution," *J. Am. Chem. Soc.* **2026**, 148, 4250–4261. [10.1021/jacs.5c17145](https://doi.org/10.1021/jacs.5c17145) | Closest published competitor to this project's method: activity **and** stability descriptors screened jointly over doped RuO2. Read against `docs/18` before the report claims novelty. |
| `Jia-2025_JACS_closed-loop-bifunctional-oxide-discovery.pdf` | Jia, Zhou *et al.*, "Closed-Loop Framework for Discovering Stable and Low-Cost Bifunctional Metal Oxide Catalysts for Efficient Electrocatalytic Water Splitting in Acid," *J. Am. Chem. Soc.* **2025**, 147, 22642–22654. [10.1021/jacs.5c04079](https://doi.org/10.1021/jacs.5c04079) | Active-learning loop over the same objective (activity + stability + cost). Same competitive-benchmark caution as above. |
| `Deng-2025_ACSCatal_betaMnO2-IrRu-cosubstitution.pdf` | Deng, Liu *et al.*, "Rational Design of β-MnO2 via Ir/Ru Co-substitution for Enhanced Oxygen Evolution Reaction in Acidic Media," *ACS Catal.* **2025**, 15, 1782–1794. [10.1021/acscatal.4c05989](https://doi.org/10.1021/acscatal.4c05989) | Mn-rutile host with noble co-substitution — directly relevant given Mn ranked best on both η and G_max in `docs/29`. |
| `Burnett-2020_ChemMater_M-RuO2-rutiles-MEA.pdf` | Burnett, Petrucco, Rigg, Zalitis, Lok, Kashtiban, Lees, Sharman & Walton, "(M,Ru)O2 (M = Mg, Zn, Cu, Ni, Co) Rutiles and Their Use as Oxygen Evolution Electrocatalysts in Membrane Electrode Assemblies under Acidic Conditions," *Chem. Mater.* **2020**, 32, 6150–6160. [10.1021/acs.chemmater.0c01884](https://doi.org/10.1021/acs.chemmater.0c01884) | Synthesised (M,Ru)O2 rutiles measured in a real MEA — the experimental reality check on a computed ranking, and it includes Cu and Co. |
| `1-s2.0-S0021951725000338-main.pdf` | Feng, Li, Zheng, Zhong, Wang & Wang, "GC-DFT simulation of coverage and potential effect for oxygen evolution reaction on RuO2-based electrocatalyst," *J. Catal.* **2025**, 443, 115968. [10.1016/j.jcat.2025.115968](https://doi.org/10.1016/j.jcat.2025.115968) | Item **B2** of the rutile-landscape survey and the most direct overlap with this project: our exact 3d dopant set on RuO2(110) with surface Pourbaix, GC-DFT and their own synthesis (Cr-RuO2 201 mV, best in set) — at zero Hubbard U and no spin. |

## Next pulls flagged by the 2026-08-11 sweep

The original `docs/28` §9 flagged list is now fully cleared (Man 2011 and Feng 2025 both
arrived in this pull). The sweep memo's citation ledger (§7) flags the next round, in
priority order:

- **Xu, Rossmeisl & Kitchin,** "A Linear Response DFT+U Study of Trends in the Oxygen
  Evolution Activity of Transition Metal Rutile Dioxides," *J. Phys. Chem. C* **2015**, 119,
  4827–4833, [10.1021/jp511426q](https://doi.org/10.1021/jp511426q). **Gates the hp.x
  novelty wording** — likely bulk-only linear response, which would preserve our slab claim,
  but that must be read, not assumed. **STILL NEEDED**: the 2026-08-12 pull fetched
  `jp5b05338.pdf`, which is the *other* Kitchin JPCC 2015 paper (Curnan & Kitchin, indexed
  above). No OA copy exists (Unpaywall: closed) — pull `10.1021/jp511426q` via Purdue.
- **Lin 2019**, *Nat. Commun.* 10:162 — Cr₀.₆Ru₀.₄O₂ experimental prior art.
- **Comer 2022**, *J. Phys. Chem. C* 126, 7903 — pure-rutile slab series.
- **Dickens, Kirk & Nørskov 2019**, *J. Phys. Chem. C* — kinetic volcano.
- **McCrory 2013**, *JACS* 135, 16977 + **Palkovits 2019**, *ACS Catal.* 9, 8383 — the
  η = 0.3 V benchmarking convention.
- **Sun 2024 and Cao 2026 SIs** (free ACS downloads) — per-dopant experimental η₁₀ and
  Cao's dopant-U table (direct comparator for our hp.x numbers).

## One correction this pull turned up

`docs/research/2026-07-24-methodology-survey.md` cites the universal-descriptor paper as
*ACS Catal.* **2021**, 11(6), 3234–3241. The PDF's own front matter reads *ACS Catal.*
**2020**, 10, 12607–12617 for that DOI. The survey entry has been corrected. `docs/28`
§9 labels the same paper "Exner ACS Catal. 2021" in two places; the DOI there is right and
the year label is wrong, left alone because that document is a dated plan of record.
