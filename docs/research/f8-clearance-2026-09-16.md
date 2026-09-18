# F8 clearance — 2026-09-16

F8 (docs/43 A9.5 item 8, :1945) requires five items to be cleared or excluded, with the bibliography regenerated from Crossref; the Sun, Reuter & Scheffler citation is A9.5 item 7 (:1944). Each item was checked here against registrar records, open full text, crystallographic databases and the repository's own files. The deadline in :1945 was Sep 15; this record is dated Sep 16. No registered text was edited.

Source review updated 2026-09-18: the Sun journal wording is checked against the previously archived MPG copy, and the OsO₂ structural statement names the COD population it describes. The prior report and summary are preserved in `results/s2_2026-09-16/f8_before_vor_correction/`.

Code: `src/s2/f8/`; `PYTHONPATH=src python -m s2.f8.run --offline` rebuilds every table below from the cached responses. Outputs: `results/s2_2026-09-16/f8/` (`summary.json`, one JSON per item, `references.crossref.bib`, `bib_crossref_diff.json`). `manifest.json` holds the sha256 of 504 repository inputs and the 330 cached registrar, database and full-text responses this run read; it lists separately, with hashes, 1 cached response that no current request reads (`https://export.arxiv.org/api/query?search_query=ti%3ARuO2+AND+au%3AReuter&max_results=20` HTTP 406).

## Verdicts

Each claim is split into the sub-claims its sentence makes. A sub-claim is CLEARED only when every evidence test passes; any failed test or any statement with no accessible evidence makes it EXCLUDED (docs/43 :1945, 'each cleared or excluded'). A 'narrowed' form records a weaker sentence the evidence does support, with its own binary verdict; it never changes the verdict of the sub-claim as written.

| Item | Claim | Result |
|---|---|---|
| Sun, Reuter & Scheffler 2004 (:1944) | Sun, Reuter & Scheffler state that a structural relaxation allowing any symmetry breaking at the RuO2(110) surface was crucial to obtain the correct energetics and structures. | **CLEARED**: PRB 70, 235402 (2004), p. 235402-2: published article archived by the MPG repository; PDF identity and wording checked |
| Sun, Reuter & Scheffler 2004 (:1944) | The same sentence appears in the version of record, Phys. Rev. B 70, 235402 (2004). | **CLEARED**: PRB 70, 235402 (2004), p. 235402-2: the same wording is present in the MPG-hosted published PDF |
| 2026-08-15-lit-sweep-round2-synthesis.md:113 | β-PbO₂ (plattnerite) is a rutile-type PbO₂ polymorph recorded at ambient pressure. | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:113 | β-PbO₂ is markedly non-stoichiometric. | **EXCLUDED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:114 | MP mp-996 (OsO₂) is P4₂/mnm (sg 136) with corner- and edge-sharing OsO₆ octahedra, i.e. rutile-type; the two OsO₂ entries in this COD census are also rutile-type. | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:114 | The MP label "Hydrophilite" on mp-996 is a classification artefact: hydrophilite is the CaCl₂-type (Pnnm) mineral, which cannot coexist with sg 136. | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:105 | SnO₂ (cassiterite) is ambient P4₂/mnm rutile. | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:105 | Sn in SnO₂ (formally Sn⁴⁺) is d¹⁰. | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:115 | Rutile-type GeO₂ (argutite) is a GeO₂ polymorph recorded at ambient pressure. | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:115 | Rutile-type is the thermodynamically stable GeO₂ polymorph at ambient conditions. | **EXCLUDED**; narrowed form "Rutile-type is the lowest-energy GeO₂ entry in the Materials Project (DFT, 0 K)." **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:115 | GeO₂ converts from rutile-type to quartz-type above ~1035 °C. | **EXCLUDED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:115 | Stishovite (rutile-type SiO₂) is the high-pressure case. | **EXCLUDED** |
| 43-prereg-week1-factorial.md:1429 | Rutile-type GeO₂ is an ambient GeO₂ polymorph (a real phase, not a model phase). | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:118 | The PtO₂ ground state is not rutile-type. | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:118 | A CdI₂-type hexagonal PtO₂ phase is recorded. | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:118 | The CdI₂-type hexagonal phase is α-PtO₂. | **EXCLUDED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:118 | β-PtO₂ is CaCl₂-type orthorhombic. | **CLEARED** |
| 2026-08-15-lit-sweep-lens-digest.md:280 | PtO₂ is a real rutile-like dioxide (through its CaCl₂-type phase, an orthorhombic rutile derivative). | **CLEARED** |
| 2026-08-15-lit-sweep-lens-digest.md:280 | SnO₂ is a real rutile-type dioxide. | **CLEARED** |
| 2026-08-15-lit-sweep-lens-digest.md:280 | OsO₂ is a real rutile-type dioxide. | **CLEARED** |
| +0.40 eV *OOH ZPE − TS | the constant has a readable primary source | **EXCLUDED**: absent from every source readable here; the implied convention is δ = +0.05 eV |
| 3.18 ± 0.12 eV intercept | qualitative only (disposition) | disposition holds in the registered text; 18 lines in the tree still use it or the 0.12 V floor quantitatively (table in §4) |
| ~0.12 V code floor | dead (disposition) | dead in the registered text; A9.5 item 1 option (b) still carries a ±0.12 V η gate |
| docs/references.bib vs Crossref | metadata agrees with the registrar | 217 entries, 217 title / 217 first-author / 217 year / 217 journal / 217 volume / 217 pages match; 2 DOI fields are not registered DOIs |
| docs/28 DOI defects | every DOI names the work its label names | CatBench → `10.1016/j.xcrp.2025.102968` (lines 87, 114); J. Catal. → `10.1016/j.jcat.2025.115968` (line 90) |

## 1. Sun, Reuter & Scheffler (2004)

**Record.** Crossref `10.1103/physrevb.70.235402` (HTTP 200): *Hydrogen adsorption on RuO2(110): Density-functional calculations*, Qiang Sun, Karsten Reuter, Matthias Scheffler, Physical Review B **70**, 235402 (2004). Authors, journal, volume, article number and year agree with the repository citation in 5 of 5 checks.

**Accessible text.** The MPG repository supplies the [published PDF](https://pure.mpg.de/rest/items/item_739138_2/component/file_2052691/content) (sha256 `b308323685216613d03f4f1e246928f0348243479f7d340631df7c4cce6579d0`, 12 pages). Its first-page journal, volume, article number, year, DOI and author checks pass: True. The cached access indexes say OpenAlex `closed`, no repository full text; Semantic Scholar `CLOSED`. Those labels missed this copy. The previous F8 draft excluded the journal wording because the copy had not been incorporated; this readout corrects that exclusion using the already archived primary evidence. The APS abstract page gives received 2003-09-17 and published 2004-12-02. arXiv:cond-mat/0309714v1, *Hydrogen adsorption at RuO2(110)*, was posted on 2003-09-30 with the same author list in the same order, 13 days after APS receipt, abstract token overlap (Jaccard) with the published abstract 0.579. The published title and abstract were revised, so the preprint is the submitted manuscript, not the version of record.

**The sentence.** The published article describes allowing symmetry breaking during structural relaxation on p. 235402-2, followed by:

> This was found to be crucial to obtain the correct energetics and structures.

The tilt example on p. 235402-6 gives a 0.1 eV/H energy gain for the tilted surface hydroxyl relative to the upright configuration. The preprint carries the corresponding passages on pp. 2 and 7.

**Where the repository cites it.**

| Line | Role | Claim as written | Verdicts |
|---|---|---|---|
| docs/43-prereg-week1-factorial.md:1944 | claim | Sun, Reuter & Scheffler, PRB 70, 235402 (2004), "crucial" on RuO₂(110) | SUN-crucial-statement-by-these-authors CLEARED; SUN-same-wording-in-PRB-70-235402 CLEARED |
| docs/50-amendment-9-DRAFT.md:152 | claim | Sun, Reuter & Scheffler, PRB 70, 235402 (2004), "crucial" on RuO₂(110) | SUN-crucial-statement-by-these-authors CLEARED; SUN-same-wording-in-PRB-70-235402 CLEARED |
| tasks/plan-maximal-rigor.md:290 | claim | Sun/Reuter/Scheffler PRB **70**, 235402 (2004) call it "crucial" on RuO₂(110) | SUN-crucial-statement-by-these-authors CLEARED; SUN-same-wording-in-PRB-70-235402 CLEARED |
| docs/43-prereg-week1-factorial.md:1945 | f8 registration | — | — |
| docs/50-amendment-9-DRAFT.md:153 | f8 registration | — | — |
| docs/52-decision-sheet-2026-08-23.md:426 | f8 registration | — | — |
| tasks/todo.md:1993 | task item | — | — |
| tasks/todo.md:2612 | task item | — | — |

**Verdicts.**

| Sub-claim | Statement | Verdict | Basis |
|---|---|---|---|
| SUN-crucial-statement-by-these-authors | Sun, Reuter & Scheffler state that a structural relaxation allowing any symmetry breaking at the RuO2(110) surface was crucial to obtain the correct energetics and structures. | **CLEARED** | PRB 70, 235402 (2004), p. 235402-2: published article archived by the MPG repository; PDF identity and wording checked |
| SUN-same-wording-in-PRB-70-235402 | The same sentence appears in the version of record, Phys. Rev. B 70, 235402 (2004). | **CLEARED** | PRB 70, 235402 (2004), p. 235402-2: the same wording is present in the MPG-hosted published PDF |

Scope of the cleared sub-claim: the paper studies hydrogen at the stoichiometric RuO₂(110) surface; the "crucial" sentence is about relaxations that allow symmetry breaking of surface species, and the tilt example gives the size of one such case (tilted versus upright surface hydroxyl). It supports "called crucial on RuO₂(110) by these authors"; it says nothing about *OH/*OOH at cus sites or about any code's symmetrisation. The journal locator is PRB 70, 235402 (2004), p. 235402-2.

## 2. Structure types: PbO₂, OsO₂, SnO₂, GeO₂, PtO₂

**Method.** Every COD entry for the five formulas (65 returned, 65 parsed, 0 unparsed) was downloaded; space group and Wyckoff sites were recomputed from the CIF coordinates with spglib (symprec 0.01 Å). Declared and recomputed space groups disagree in 0 entries. A prototype is assigned only by explicit rules: rutile = P4₂/mnm with M 2a, O 4f; CaCl₂ = Pnnm, M 2a, O 4g; α-PbO₂ = Pbcn, M 4c, O 8d; CdI₂ = P-3m1, M 1a, O 2d; α-quartz = P3₁21/P3₂21, M 3a/3b, O 6c; fluorite; pyrite; anything else is listed by space group. "Ambient" means a recorded pressure of at most 1 MPa or, where COD records none, a source title that does not name high pressure or an ab initio calculation. Materials Project summary documents give the DFT energy above hull and ICSD cross-references; they are 0 K orderings, not phase equilibria.

| Oxide | COD parsed | COD prototypes | …ambient by COD record and title | MP lowest E_hull | MP rutile-type E_hull (meV/atom) | MP next (meV/atom) |
|---|---|---|---|---|---|---|
| PbO₂ | 17/17 | alpha-PbO2 2, fluorite 3, rutile 3, sg62 9 | alpha-PbO2 2, rutile 3 | P4_2/mnm (mp-aaaaberd) | 0.0 | Pbcn 1.5; Pnma 57; Fm-3m 107 |
| OsO₂ | 2/2 | rutile 2 | rutile 2 | P4_2/mnm (mp-aaaaabmi) | 0.0 | Pa-3 73 |
| SnO₂ | 9/9 | rutile 9 | rutile 9 | P4_2/mnm (mp-aaaaabgy) | 0.0 | Imma 0.4; Pnnm 2.3; Pbcn 11 |
| GeO₂ | 33/33 | CaCl2 6, alpha-PbO2 2, alpha-quartz 7, pyrite 2, rutile 15, sg14 1 | alpha-quartz 2, rutile 6 | P4_2/mnm (mp-aaaaaasc) | 0.0 | Pbcn 36; P3_121 80; P3_221 80 |
| PtO₂ | 4/4 | CaCl2 2, CdI2 1, sg186 1 | CdI2 1, sg186 1 | Pnnm (mp-aaaaabxl) | 40 | P4_2/mnm 40; P-3m1 56; P6_3mc 56 |

**Assignments found in the repository and their verdicts.**

| Line | Sub-claim | Statement | Evidence tests | Verdict |
|---|---|---|---|---|
| 2026-08-15-lit-sweep-round2-synthesis.md:113 | PbO2-beta-plattnerite-is-rutile-type | β-PbO₂ (plattnerite) is a rutile-type PbO₂ polymorph recorded at ambient pressure. | COD PbO2 rutile ambient mineral Plattnerite present → PASS (3 records: 9007543, 9011216, 9014175) | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:113 | PbO2-beta-markedly-nonstoichiometric | β-PbO₂ is markedly non-stoichiometric. | no accessible evidence: An oxygen-deficiency statement, not a structure type; the COD records parsed here carry full O occupancy and no accessible primary text on PbO2-x stoichiometry was read. | **EXCLUDED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:114 | OsO2-mp996-is-rutile-type | MP mp-996 (OsO₂) is P4₂/mnm (sg 136) with corner- and edge-sharing OsO₆ octahedra, i.e. rutile-type; the two OsO₂ entries in this COD census are also rutile-type. | MP mp-996 sg 136, octahedra text → PASS; COD OsO2 rutile ambient present → PASS (2 records: 1538149, 9007542); COD OsO2 CaCl2 absent → PASS (0 records) | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:114 | OsO2-hydrophilite-label-is-an-artefact | The MP label "Hydrophilite" on mp-996 is a classification artefact: hydrophilite is the CaCl₂-type (Pnnm) mineral, which cannot coexist with sg 136. | MP mp-996 sg 136, label Hydrophilite → PASS; COD CaCl2 CaCl2 mineral Hydrophilite present → PASS (2 records: 1011280, 9009084); COD CaCl2 rutile mineral Hydrophilite absent → PASS (0 records) | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:105 | SnO2-cassiterite-is-ambient-rutile | SnO₂ (cassiterite) is ambient P4₂/mnm rutile. | COD SnO2 rutile ambient mineral Cassiterite present → PASS (6 records: 1000062, 2104743, 2104754, 5000224, 9007533, 9009082) | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:105 | SnO2-Sn4-is-d10 | Sn in SnO₂ (formally Sn⁴⁺) is d¹⁰. | formal d count Sn(+4) = 10 → PASS | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:115 | GeO2-rutile-type-is-an-ambient-polymorph | Rutile-type GeO₂ (argutite) is a GeO₂ polymorph recorded at ambient pressure. | COD GeO2 rutile ambient mineral Argutite present → PASS (5 records: 9006849, 9007435, 9007532, 9009080, 9016492) | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:115 | GeO2-rutile-type-is-ambient-stable | Rutile-type is the thermodynamically stable GeO₂ polymorph at ambient conditions. | no accessible evidence: A phase-equilibrium statement; no measured GeO2 phase-equilibrium text was read, and quartz-type GeO2 is also recorded at ambient pressure, so the existence of records does not decide stability. Narrowed form "Rutile-type is the lowest-energy GeO₂ entry in the Materials Project (DFT, 0 K).": MP lowest-E_hull GeO2 is sg 136 → PASS → **CLEARED** | **EXCLUDED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:115 | GeO2-converts-to-quartz-type-above-1035C | GeO₂ converts from rutile-type to quartz-type above ~1035 °C. | no accessible evidence: A transition temperature; no accessible primary text giving it was read, and crystal-structure records do not carry it. | **EXCLUDED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:115 | GeO2-sentence-stishovite-is-high-pressure | Stishovite (rutile-type SiO₂) is the high-pressure case. | no accessible evidence: A statement about SiO2, outside the five F8 formulas; no SiO2 record or text was read. | **EXCLUDED** |
| 43-prereg-week1-factorial.md:1429 | GeO2-docs43-rutile-type-is-an-ambient-polymorph | Rutile-type GeO₂ is an ambient GeO₂ polymorph (a real phase, not a model phase). | COD GeO2 rutile ambient mineral Argutite present → PASS (5 records: 9006849, 9007435, 9007532, 9009080, 9016492) | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:118 | PtO2-ground-state-is-not-rutile | The PtO₂ ground state is not rutile-type. | COD PtO2 rutile absent → PASS (0 records); MP lowest-E_hull PtO2 is not sg 136 → PASS | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:118 | PtO2-a-CdI2-type-hexagonal-phase-exists | A CdI₂-type hexagonal PtO₂ phase is recorded. | COD PtO2 CdI2 ambient present → PASS (1 record: 1537410) | **CLEARED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:118 | PtO2-alpha-is-the-CdI2-type | The CdI₂-type hexagonal phase is α-PtO₂. | COD PtO2 CdI2 named /α\|\balpha\b/ present → FAIL (0 records) | **EXCLUDED** |
| 2026-08-15-lit-sweep-round2-synthesis.md:118 | PtO2-beta-is-CaCl2-type-orthorhombic | β-PtO₂ is CaCl₂-type orthorhombic. | COD PtO2 CaCl2 named /β\|\bbeta\b/ present → PASS (2 records: 1008935, 1530633) | **CLEARED** |
| 2026-08-15-lit-sweep-lens-digest.md:280 | PtO2-is-real-rutile-like | PtO₂ is a real rutile-like dioxide (through its CaCl₂-type phase, an orthorhombic rutile derivative). | COD PtO2 CaCl2 present → PASS (2 records: 1008935, 1530633) | **CLEARED** |
| 2026-08-15-lit-sweep-lens-digest.md:280 | SnO2-is-real-rutile | SnO₂ is a real rutile-type dioxide. | COD SnO2 rutile ambient present → PASS (9 records: 1000062, 1526637, 1534785, 2101853, 2104743, 2104754, 5000224, 9007533, 9009082) | **CLEARED** |
| 2026-08-15-lit-sweep-lens-digest.md:280 | OsO2-is-real-rutile | OsO₂ is a real rutile-type dioxide. | COD OsO2 rutile ambient present → PASS (2 records: 1538149, 9007542) | **CLEARED** |

Sub-claims: 18; CLEARED 13, EXCLUDED 5.

OsO₂: MP `mp-996` now resolves to `mp-aaaaabmi`, P4_2/mnm (no. 136), E_hull 0.0 meV/atom; its robocrystallographer label is "Hydrophilite" while the same text states the tetragonal P4₂/mnm group and corner- and edge-sharing OsO₆ octahedra. COD's CaCl₂ records (2/2 parsed; CaCl2 2) carry the mineral name hydrophilite, so the label names the orthorhombic type and does not change the rutile assignment.

PtO₂: COD holds no rutile-type PtO₂; MP's lowest entry is Pnnm; the MP rutile-type PtO₂ lies 40 meV/atom above the hull and carries icsd-647316. Rutile PtO₂(110) slabs in Xu 2015, Man 2011, Mom 2014 and Lim 2021 are therefore a model phase; "rutile-like" (lens-digest :280) holds only through the CaCl₂-type distortion. 2 CaCl₂-type records name the phase β and 0 CdI₂-type records name it α, so "α = CdI₂-type" is EXCLUDED while the hexagonal CdI₂-type phase itself is CLEARED.

GeO₂: argutite (rutile-type) and quartz-type records are both ambient by that rule, and MP places rutile-type lowest with quartz-type at 80 meV/atom. "Ambient-stable" is a phase-equilibrium statement that no text read here makes, so it is EXCLUDED as written; the narrowed sentence "Rutile-type is the lowest-energy GeO₂ entry in the Materials Project (DFT, 0 K)." is CLEARED. The transition temperature is EXCLUDED and the SiO₂ stishovite remark EXCLUDED. docs/43 :1429 ("rutile-type IS its ambient polymorph") is CLEARED as "an ambient polymorph", which is what its exclusion argument needs; read as "the stable one" it carries the excluded sub-claim.

**Primary crystallographic sources used as evidence** (COD id, recomputed space group, prototype):

| COD | Compound | Space group | Prototype | Mineral | Source |
|---|---|---|---|---|---|
| 1000062 | SnO₂ | P4_2/mnm | rutile | Cassiterite | Baur 1971, Acta Crystallographica B (24,1968-38,1982) 27, 2133, 10.1107/S0567740871005466 |
| 1008935 | PtO₂ | Pnnm | CaCl2 | — | Muller 1968, Journal of the Less-Common Metals 16, 129, 10.1016/0022-5088(68)90070-2 |
| 1011280 | CaCl₂ | Pnnm | CaCl2 | Hydrophilite | van Bever 1935, Zeitschrift fuer Kristallographie, Kristallgeometrie, Kristallphysik, Kristallchemie (-144,1977) 90, 374 |
| 1526637 | SnO₂ | P4_2/mnm | rutile | — | Kim 2000, The Korean Journal of Ceramics 6, 354 |
| 1530633 | PtO₂ | Pnnm | CaCl2 | — | Range 1987, Materials Research Bulletin 22, 1541 |
| 1534785 | SnO₂ | P4_2/mnm | rutile | — | Seki 1984, Journal of the Ceramic Association, Japan 92, 219, 10.2109/jcersj1950.92.1064_219 |
| 1537410 | PtO₂ | P-3m1 | CdI2 | — | Hoekstra 1971, Advances in Chemistry Series 98, 39 |
| 1538149 | OsO₂ | P4_2/mnm | rutile | — | Goldschmidt 1926, Skrifter utgitt av det Norske Videnskaps-Akademi i Oslo 1: Matematisk-Naturvidenskapelig Klasse 1926, 1 |
| 2101853 | SnO₂ | P4_2/mnm | rutile | — | Bolzan 1997, Acta Crystallographica Section B 53, 373, 10.1107/S0108768197001468 |
| 2104743 | SnO₂ | P4_2/mnm | rutile | Cassiterite | Elliot 2010, Acta Crystallographica Section B 66, 271, 10.1107/S0108768110011845 |
| 2104754 | SnO₂ | P4_2/mnm | rutile | Cassiterite | Elliot 2010, Acta Crystallographica Section B 66, 271, 10.1107/S0108768110011845 |
| 2300365 | GeO₂ | P3_121 | alpha-quartz | — | Lignie 2012, Journal of Applied Crystallography 45, 272, 10.1107/S0021889812003081 |
| 5000224 | SnO₂ | P4_2/mnm | rutile | Cassiterite | Baur 1956, Acta Crystallographica 9, 515, 10.1107/S0365110X56001388 |
| 9006849 | GeO₂ | P4_2/mnm | rutile | Argutite | Haines 2000, Physics and Chemistry of Minerals 27, 575, 10.1007/s002690000092 |
| 9007435 | GeO₂ | P4_2/mnm | rutile | Argutite | Baur 1956, Acta Crystallographica 9, 515, 10.1107/S0365110X56001388 |
| 9007477 | GeO₂ | P3_221 | alpha-quartz | — | Smith 1964, Acta Crystallographica 17, 842, 10.1107/S0365110X64002262 |
| 9007532 | GeO₂ | P4_2/mnm | rutile | Argutite | Baur 1971, Acta Crystallographica, Section B 27, 2133, 10.1107/S0567740871005466 |
| 9007533 | SnO₂ | P4_2/mnm | rutile | Cassiterite | Baur 1971, Acta Crystallographica, Section B 27, 2133, 10.1107/S0567740871005466 |
| 9007542 | OsO₂ | P4_2/mnm | rutile | — | Baur 1971, Acta Crystallographica, Section B 27, 2133, 10.1107/S0567740871005466 |
| 9007543 | PbO₂ | P4_2/mnm | rutile | Plattnerite | Baur 1971, Acta Crystallographica, Section B 27, 2133, 10.1107/S0567740871005466 |
| 9009080 | GeO₂ | P4_2/mnm | rutile | Argutite | Wyckoff 1963, Crystal Structures 1, 239 |
| 9009082 | SnO₂ | P4_2/mnm | rutile | Cassiterite | Wyckoff 1963, Crystal Structures 1, 239 |
| 9009084 | CaCl₂ | Pnnm | CaCl2 | Hydrophilite | Wyckoff 1963, Crystal Structures 1, 239 |
| 9011216 | PbO₂ | P4_2/mnm | rutile | Plattnerite | D'Antonio P 1980, Acta Crystallographica, Section B 36, 2394, 10.1107/S0567740880008813 |
| 9014175 | PbO₂ | P4_2/mnm | rutile | Plattnerite | Bolzan 1997, Acta Crystallographica, Section B 53, 373, 10.1107/S0108768197001468 |
| 9016492 | GeO₂ | P4_2/mnm | rutile | Argutite | Bolzan 1997, Acta Crystallographica, Section B 53, 373, 10.1107/S0108768197001468 |

**Scope of the search.** 30 lines in docs/, tasks/, src/ and README.md name one of the five with structure vocabulary: ASSIGNMENT 7, EXCLUSION_LIST 1, F8_REGISTRATION 4, MODEL_DESCRIPTION 14, NOT_A_STRUCTURE_STATEMENT 4. MODEL_DESCRIPTION lines say which structure a cited calculation used (for example rutile PtO₂ slabs) and are consistent with the table above once "model phase" is attached to PtO₂. src/ assigns no structure type to any of the five. The docs/43 A7.5 exclusion list (:1408) can now carry a COD or MP identifier for PtO₂, GeO₂, PbO₂ and OsO₂ from the tables above.

## 3. The +0.40 eV *OOH ZPE − TS constant

**Man 2011** (`docs/research/papers/man2011.pdf`, 7 pages, sha256 `9c61b31e2d4e…`): text search counts "0.40" 0, "0.35" 0, "ZPE" 0, "Table" 0, "zero point" 1, "0.05" 1, "Supporting Information" 4. The "zero point" hit is the Fig. 2 caption (the plotted adsorption energies "do not include zero point energy and entropy corrections"); the "0.05" hit is the force threshold. The main text holds no ZPE/TS table and defers the derivation to the Supporting Information, whose publisher download returned HTTP 403 with a bot-challenge page; it was not read.

**Divanis 2020 ESI Table SI-1** (`docs/research/2026-08-15-sampling/divanis_esi.txt` line 70; sha256 matches the committed SHA256SUMS), attributed there to ref. [25] = Nørskov et al. 2004. Header `TS T∆S ZPE ∆ZPE ∆ZPE – T∆S`; the table has no *OOH row.

| Row | Values as printed |
|---|---|
| H2O | 0.67, 0.00, 0.56, 0.00, 0.00 |
| *OH + ½ H2 | 0.20, -0.47, 0.44, -0.12, 0.35 |
| *O + H2 | 0.41, -0.27, 0.34, -0.22, 0.05 |
| ½ O2 + H2 | 0.73, 0.05, 0.32, -0.24, -0.29 |
| H2 | 0.41, 0.27 |
| ½ O2 | 0.32, 0.05 |
| O* | 0.00, 0.07 |
| HO* | 0.00, 0.30 |
| H* | 0.00, 0.17 |

From the single-species rows (H₂O TS 0.67, ZPE 0.56; H₂ TS 0.41, ZPE 0.27; HO* ZPE 0.30; O* ZPE 0.07) the *OH and *O corrections recompute to 0.34 and 0.04 eV against the printed 0.35 and 0.05 (rounding in the table). The convention is ΔG = ΔE + (ΔZPE − TΔS) with each adsorbate formed from H₂O and released H₂ (the references of `src/hea_oer/referencing.py`). On those molecule columns the repository's 0.40 eV requires ZPE − TS(HOO*) = 0.39 eV, and the *OH value applied to *OOH requires 0.34 eV. On the registered axis "δ = corr_OOH − 0.35 eV, δ ∈ [0.00, 0.10] eV" (docs/43 :1898) the constant is δ = +0.05 eV (inside the registered range).

| Candidate source | DOI | Crossref | OpenAlex OA | Repository full text | Read |
|---|---|---|---|---|---|
| Norskov et al. 2004 | 10.1021/jp047349j | The Journal of Physical Chemistry B 108, 17886-17892 (2004) | closed | False | not read |
| Man et al. 2011 | 10.1002/cctc.201000397 | ChemCatChem 3, 1159-1165 (2011) | closed | False | main text on disk |
| Valdes et al. 2008 | 10.1021/jp711929d | The Journal of Physical Chemistry C 112, 9872-9879 (2008) | closed | False | not read |
| Rossmeisl, Logadottir & Norskov 2005 | 10.1016/j.chemphys.2005.05.038 | Chemical Physics 319, 178-184 (2005) | closed | False | not read |
| Rossmeisl et al. 2007 | 10.1016/j.jelechem.2006.11.008 | Journal of Electroanalytical Chemistry 607, 83-89 (2007) | closed | False | not read |

**Verdict: EXCLUDED as a sourced constant.** 0.40 eV appears in no text readable here: not in the Man 2011 main text, not in Table SI-1 (no *OOH row), and the Nørskov 2004 tables, the Man 2011 SI and Valdés 2008 are closed or blocked. The attribution at `src/hea_oer/referencing.py` lines 11, 12, 17 (Man 2011 / Valdés 2008) stays unverified, and the constant remains a declared convention of this repository; where it does and does not enter reported values is recorded in the 2026-09-04 addendum (docs/43 :3980). Because δ was not resolved from Nørskov 2004 by Sep 15, A9.3.4's registered fallback applies: P-DIVANIS reports only the δ-curve and no single-δ number.

## 4. The 3.18 ± 0.12 eV intercept and the ~0.12 V code floor

Every line in docs/, tasks/, src/, tests/, README.md and CLAUDE.md (490 files) matching `3.18`, a 0.12 V/eV value (alone or as the lower end of a range such as "0.12-0.30 V"), 120 mV, "code(-level) floor" or "irreducible floor/band" was listed: 99 lines in 30 files, 0 unclassified. Each class is keyed to a verbatim fragment in `src/s2/f8/data/intercept_floor_classes.json`. As a reach check, 36 further lines hold a bare `0.12` that none of these patterns matches; they are listed in `intercept_floor.json` (units such as mV at a stated pH, μ_B, %, table cells and file names), not classified.

| Class | Lines |
|---|---|
| ARCHIVE_COPY | 10 |
| CAVEAT | 3 |
| CITATION_RULE | 1 |
| DATA_TABLE_VALUE | 3 |
| DATED_RECORD_QUANTITATIVE | 11 |
| DISPOSITION | 10 |
| DRAFT_COPY | 4 |
| FROZEN_DEPOSITED_QUANTITATIVE | 3 |
| GENERATED_COPY | 22 |
| LIVE_QUANTITATIVE | 3 |
| PAPER_VALUE_REPORTED | 1 |
| REGISTERED_OPTION_QUANTITATIVE | 1 |
| UNRELATED_NUMBER | 20 |
| UNRELATED_QUANTITY | 6 |
| VERBATIM_CITATION | 1 |

The registered text matches the dispositions: :1945 lists the intercept as qualitative and the floor as dead; :1791-1797 and :1898 withdraw the |z| ≥ 3 gate and keep the z column as reported; :1938 drops the floor from the Xu-repair justification. Matching lines in src/ and tests/: 0. Lines that still use a value quantitatively:

| Line | Class | Text | Note |
|---|---|---|---|
| docs/41-prereg-anchor-offset-diagnosis.md:885 | DATED_RECORD_QUANTITATIVE | "pooled 3.18 ± 0.12 eV, i.e. **not a scaling-relation breaker.**" | sigma-distance verdict against the pooled 1-sigma (the 0.65 sigma figure is on the preceding line) |
| docs/43-prereg-week1-factorial.md:332 | FROZEN_DEPOSITED_QUANTITATIVE | "z = (c_M − 3.18)/0.12 against the pooled universal value" | section 6 z definition; its gate is withdrawn by the correction of record at docs/43:1791-1797 |
| docs/43-prereg-week1-factorial.md:422 | FROZEN_DEPOSITED_QUANTITATIVE | "the Divanis (2020) pooled c = 3.18 ± 0.12 eV used in §6" | deposited unverified-citation note |
| docs/43-prereg-week1-factorial.md:839 | FROZEN_DEPOSITED_QUANTITATIVE | "§6's z = (c_M − 3.18)/0.12 uses the" | section 9 item 2, z uses the 1-sigma |
| docs/43-prereg-week1-factorial.md:1938 | REGISTERED_OPTION_QUANTITATIVE | "a widened ±0.12 V η gate" | the same line declares the code floor dead, yet Xu-repair option (b) still carries a ±0.12 V eta gate whose only stated origin is round-1 :225's code-to-code floor |
| docs/research/2026-08-11-paywalled-sweep-plan-implications.md:63 | DATED_RECORD_QUANTITATIVE | "corroborates the Divanis 3.18 ± 0.12 eV already load-bearing in P17" | 'load-bearing' use of the pooled value |
| docs/research/2026-08-15-lit-sweep-lens-digest.md:230 | DATED_RECORD_QUANTITATIVE | "0.12 eV in c_M implies only ~0.06 V of floor spread" | pooled 1-sigma converted to a floor spread |
| docs/research/2026-08-15-lit-sweep-lens-digest.md:319 | DATED_RECORD_QUANTITATIVE | "is never tighter than ±0.12 V" | code-floor gate half-width |
| docs/research/2026-08-15-lit-sweep-lens-digest.md:323 | DATED_RECORD_QUANTITATIVE | "intercept 3.18 ± 0.12 eV (1σ) / ±0.24 eV (2σ), is already used by P17" |  |
| docs/research/2026-08-15-lit-sweep-lens-digest.md:333 | DATED_RECORD_QUANTITATIVE | "An externally-sourced floor of ≈0.12 V" | code-floor derivation |
| docs/research/2026-08-15-lit-sweep-lens-digest.md:334 | DATED_RECORD_QUANTITATIVE | "a 0.12 V code-level gap" | code-floor derivation (both legs) |
| docs/research/2026-08-15-lit-sweep-lens-digest.md:335 | DATED_RECORD_QUANTITATIVE | "no external gate on η may be tighter than ±0.12 V" | code-floor gate half-width |
| docs/research/2026-08-15-lit-sweep-lens-digest.md:356 | DATED_RECORD_QUANTITATIVE | "a third data point for the ≈0.12-0.30 V irreducible band" | the ~0.12 V code floor as the lower edge of an 'irreducible band' (round-2 :60 withdraws the '~0.12 V irreducible code-level floor') |
| docs/research/2026-08-15-lit-sweep-round1-synthesis.md:34 | DATED_RECORD_QUANTITATIVE | "~3.7× the entire published inter-study intercept spread" | superseded synthesis; ratio to the pooled spread |
| docs/research/2026-08-15-lit-sweep-round1-synthesis.md:225 | DATED_RECORD_QUANTITATIVE | "a code-to-code floor the project's own evidence puts at ≈0.12 V" | origin of the option (b) gate width |
| docs/research/papers/README.md:28 | LIVE_QUANTITATIVE | "corroborates the Divanis 3.18 ± 0.12 eV constant that P17 already uses" | live paper index |
| tasks/plan-maximal-rigor.md:87 | LIVE_QUANTITATIVE | "z-score against Divanis 2020's pooled 3.18 ± 0.12 eV. Add the z-score column to every corrected tier as a pre-registered acceptance gate" | repeats the withdrawn z-gate (docs/43:1898 names this line) |
| tasks/plan-maximal-rigor.md:295 | LIVE_QUANTITATIVE | "supplies the pooled 3.18 ± 0.12 eV calibration" |  |

Two kinds need attention before report drafting. The three LIVE_QUANTITATIVE lines are a plan and an index that still treat the pooled ±0.12 eV as a calibration or gate. The REGISTERED_OPTION_QUANTITATIVE line is open option (b) of the Xu-repair decision: its ±0.12 V η gate has no stated origin other than round-1 :225's code-to-code floor, so choosing (b) as written would bring the dead floor back as a gate width. The deposited and dated-record lines are frozen history and stay as they are.

## 5. Crossref check of docs/references.bib, and the docs/28 DOIs

**docs/references.bib.** 217 entries; 217 with a DOI, 0 without. Registrar that answered: crossref 210, datacite 7. Crossref was queried for every DOI, DataCite only after a Crossref 404.

| Field | Status | Entries |
|---|---|---|
| first_author | MATCH | 217 |
| journal | MATCH | 217 |
| pages | MATCH | 217 |
| title | MATCH | 217 |
| volume | MATCH | 217 |
| year | MATCH | 217 |

No title, first author, year, journal, volume or page field disagrees with its registrar record; the file was built from the same registrars on 2026-09-04. The defects are of other kinds:

| Defect | Entries | Detail |
|---|---|---|
| DOI field is not a registered DOI (website suffix) | 2 | `lim2021full`: `10.3389/fenrg.2021.606313/full` → `10.3389/fenrg.2021.606313`; `ooka2021full`: `10.3389/fenrg.2021.654460/full` → `10.3389/fenrg.2021.654460` |
| author field holds only the first author's family name | 197 |  |
| issue number missing | 191 |  |
| title carries registrar markup or line breaks | 48 |  |
| journal carries HTML entity markup (`&amp;`) | 5 | `sajjad20251468`; `ospinaacevedo20241408`; `christensen2015332a`; `rao2017307c`; `anantharaj2018457a` |
| print and online years differ (bib uses print) | 14 | `lee20264939` 2026/2025; `frydendal20152756` 2015/2014; `exner20240014` 2024/2023; `stevens20172796` 2017/2016; `iyer20210156` 2021/2020; `kerr20231691` 2023/2022; `moon2024707w` 2024/2023; `melander20197829` 2019/2018; `lejaeghere20142503` 2014/2013; `chamberland19773431` 1977/2006; `li20254933` 2025/2024; `jakirhossen20259b59` 2025/2024; `amatucci19966594` 1996/2019; `klemens19861197` 1986/2013 |

`results/s2_2026-09-16/f8/references.crossref.bib` holds 218 entries rebuilt from the cached registrar records under the original keys: full author lists, plain-text titles, issue numbers and the two registered DOI stems. One entry is replaced because its DOI names a different work than the lines citing it: `yin20252847` (`10.1016/j.xcrp.2025.102847`) → `moon20252968` (`10.1016/j.xcrp.2025.102968`). One entry is added for a cleared citation that had no DOI in the tree: `sun20045402` (`10.1103/physrevb.70.235402`). `bib_crossref_diff.json` lists every changed field per entry. The comparison is of metadata; whether each citation supports its sentence is outside it.

**docs/28.** 48 DOI mentions (30 unique), each resolved and compared with its label. Two DOIs are wrong:

| docs/28 line | Cited | Resolves to | Correction | Evidence |
|---|---|---|---|---|
| 87, 114 | `10.1016/j.xcrp.2025.102847` | "Multifunctional robotic fish with post-buckling notched plates" (Yin et al.; PII S2666386425004461) | `10.1016/j.xcrp.2025.102968` | Crossref: "CatBench framework for benchmarking machine learning interatomic potentials in adsorption energy predictions for heterogeneous catalysis", Moon, Jeon, Choung, Han, Cell Reports Physical Science 6, 102968 (2025); PII S2666386425005673 equals S2666-3864(25)00567-3 at docs/research/2026-07-24-mlip-finetuning-survey.md (match: True) |
| 90 | `10.1016/j.jcat.2025.115963-range` | not registered; the stem resolves to "Contents continued" (Journal of Catalysis 442, 115963; 0 authors) | `10.1016/j.jcat.2025.115968` | DOI printed on p. 1 of `docs/research/papers/1-s2.0-S0021951725000338-main.pdf`; Crossref: "GC-DFT simulation of coverage and potential effect for oxygen evolution reaction on RuO2-based electrocatalyst", Feng, Li, Zheng, Zhong, Wang, Wang, Journal of Catalysis 443, 115968 (2025) |

The wrong CatBench DOI string also appears outside docs/28 at: docs/research/2026-07-24-mlip-finetuning-survey.md:64, docs/research/2026-09-04-f8-doi-resolution.md:33, docs/research/2026-09-04-f8-doi-resolution.md:36.

Label defects where the DOI itself is right:

| Line | DOI | Label | Correction |
|---|---|---|---|
| 67 | `10.1021/acsomega.5c10410` | IrO₂(110) resting-state work, ACS Omega 2025, | 2025 → 2026 |
| 112 | `10.1021/acscatal.0c03865` | Exner G_max 2021/2023/2024 | 2021 → 2020 |
| 115 | `10.1126/science.aaf1525` | Zhou/Sargent 2016 | "Zhou" is not an author; first author is Zhang |

The same defects repeated in docs/28 clauses that carry no DOI: 3 clauses, 2 naming the same author, journal and wrong year (or the same name pair), 1 naming author and year only.

| Line | Clause | Match | Resolution | Source row | Correction | Other works, same author, journal and year |
|---|---|---|---|---|---|---|
| 60 | Exner, ACS Catal. 2021/2023 | SAME_LABEL | TOPIC_MATCH (DOI-row work shares 1 title word with the line) | :112 `10.1021/acscatal.0c03865` | 2021 → 2020 | `10.1021/acscatal.1c03893` "General Efficacy of Atomically Dispersed Pt Catalysts for th…" (2021; author 8 of 9; title words shared with the line: 0) |
| 69 | Exner pitfalls 2021 | AUTHOR_AND_YEAR_ONLY | — | :112 `10.1021/acscatal.0c03865` | no correction (not linked to one work) | — |
| 116 | Exner ACS Catal. 2021/2023 | SAME_LABEL | SAME_LABEL_STRING_AS_LINE_60 (DOI-row work shares 0 title words with the line) | :112 `10.1021/acscatal.0c03865` | 2021 → 2020 | `10.1021/acscatal.1c03893` "General Efficacy of Atomically Dispersed Pt Catalysts for th…" (2021; author 8 of 9; title words shared with the line: 0) |

"Other works" are registrar records in the same journal and year that list the same author, so the label year could name them instead. A correction is listed only when the DOI row's work is the one the line is about (more shared title words than every other work) or the clause repeats a resolved label string verbatim.

Rows flagged only because the label names no author and shares no title word, with journal and year consistent, and no defect: :60 `10.1021/acs.accounts.4c00048` (Four Generations of Volcano Plots for the Oxygen…, consistent True); :90 `10.1126/science.aaf1525` (Homogeneously dispersed multimetal oxygen-evolvi…, consistent True); :115 `10.1126/sciadv.adw0894` (Bayesian learning-assisted catalyst discovery fo…, consistent True); :115 `10.1038/s41563-023-01707-w` (Active learning guides discovery of a champion f…, consistent True). The docs/28 sentence "our exact 9-dopant set" is a content claim this DOI check does not test.

## Limits

- The Nørskov 2004 tables, the Man 2011 SI and Valdés 2008 were not read: they are closed, and the one publisher SI download was blocked. Reading these sources could settle the source of +0.40 eV. Sun et al. 2004's journal wording is checked against the MPG-hosted published PDF.
- COD pressure fields are often empty; where they are, "ambient" is inferred from the source title, which is weaker than a recorded pressure. The rutile-type ambient checks rest on named-mineral entries (plattnerite, cassiterite, argutite); the quartz-type GeO₂ check rests on the COD ids in its evidence row. Some COD GeO₂ entries are computed structures and are not ambient by the rule.
- Materials Project energies are DFT orderings at 0 K and move between database versions; they support "lowest in MP" and nothing about equilibrium at a temperature.
- Line classes in §4 and mention categories in §2 are judgments recorded with verbatim fragments; the counts depend on the patterns listed in `intercept_floor.json` and `structures.json`.
- Sub-claim boundaries in §2 are judgments recorded in `src/s2/f8/data/structure_claims.json`; each sub-claim is tested on its own evidence and none inherits another's verdict.
- A docs/28 clause without a DOI is tied to a DOI row only by the same author, journal and wrong year (or the same name pair); clauses naming author and year alone are listed, not corrected.
- The bibliography check tests registrar metadata, not whether a cited work supports its sentence.
