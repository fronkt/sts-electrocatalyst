# Paywalled-literature sweep: plan implications

**Date:** 2026-08-11
**Scope:** 17 newly pulled PDFs (12 reader agents), integrated against docs/43 (+ Amendments 1-4), docs/41, docs/44, docs/28, docs/29.
**Status:** Internal analysis memo. This is **not** the STS report and none of this text may be pasted into report or essay prose (docs/44 §6 — AI may not write report/essay prose). Every amendment below is a **proposal**; docs/43 changes only by dated amendment, and the decision on each rests with **Frank**.

---

## 1. Verdict

**No pivot.** Nothing in the sweep invalidates the Week-1 campaign (1A factorial, 1B hp.x, 1C Hessian) or the surviving symmetry-trap headline:

- **None of the 17 papers performs curvature (Hessian) verification of adsorbate geometries.** The founding screens (Garcia-Mota 2011; Man 2011) relax with force-only criteria (Man: max force < 0.05 eV/Å) in (1×2) mirror-plane cells — force convergence is *structurally* blind to a mirror-plane saddle because the symmetry-odd force component vanishes identically. Our Hessian classification (Ir *OOH i167 cm⁻¹, η 0.781→0.490 V) stands, with Goniakowski & Gillan 1995/96 credited for the underlying observation exactly as Amend 4.5 requires.
- **None attempts linear-response U on slabs.** The hp.x slab non-convergence finding stands (one bulk-rutile check still owed — see §6, Xu 2015).
- **None treats magnetic/SCF multistability as an auditable protocol failure.** Several *exhibit* it without analyzing it (Tripkovic's own Table 3; Gauthier's conformer-spin coupling; Inico's 0.3 eV spin softness) — which strengthens, not weakens, that error class.
- **The one real narrative threat** is Feng 2025: an independent group predicted Cr-near-apex at **zero U** (η_TD = 0.41 V) and confirmed it experimentally (201 mV @ 10 mA/cm², best in set). This does not touch P7's logic — η(Cr) still moves 1.12 V across plausible U at fixed geometry — but it locks the wording: **"the prediction is not U-robust," never "Cr is bad."** The prereg's ban on re-framing Cr as a discovery is unchanged.

What the sweep *does* force: (i) attribution of the U-sensitivity phenomenon to Tripkovic 2018 (and a mandatory fetch of Xu/Rossmeisl/Kitchin 2015); (ii) final burial of every compositional-novelty residue (Feng 2025, Cao 2026, Sun 2024, Jia 2025, Garcia-Mota 2011); (iii) a set of cheap scoping analyses (proposals LIT-1…LIT-8, §5) that convert our known holes (coverage, solvation, stability, Co/Cu) from confessions into tested or bounded statements.

---

## 2. Papers covered (all now primary-verified per docs/43 §10)

| # | Paper | DOI | One-line relevance |
|---|-------|-----|--------------------|
| 1 | Exner 2020, ACS Catal. 10, 12607 | 10.1021/acscatal.0c03865 | Gmax(η) definition; 0.20 eV ranking floor; η_TD unreliable near apex |
| 2 | Razzaq & Exner 2023, ACS Catal. 13, 1740 | 10.1021/acscatal.2c03997 | 10-span formalism; coverage prerequisite; anti-scaling-breaking result |
| 3 | Comer 2024, ACS Catal. 14, 5286 | 10.1021/acscatal.4c00111 | Bulk-descriptor surrogates on fixed-U foundations; open dataset; OOH scaling |
| 4 | Tripkovic 2018, JPCC 122, 1135 | 10.1021/acs.jpcc.7b07660 | **The mechanism for P7**; ~1.1 V Cr swings; HSE not the fix |
| 5 | Grimaud 2017, Nat. Chem. 9, 457 | 10.1038/NCHEM.2695 | LOM isotope evidence; O 2p centre descriptor; O-O coupling switch |
| 6 | Fabbri 2018, ACS Catal. 8, 9765 | 10.1021/acscatal.8b02712 | LOM/LOER/dissolution linkage; acidic-rutile lattice-O map |
| 7 | Gauthier 2017, JPCC 121, 11455 | 10.1021/acs.jpcc.7b02383 | Explicit-water solvation on IrO2(110); *OOH conformer-spin coupling |
| 8 | Inico 2024, ChemCatChem 16, e202400813 | 10.1002/cctc.202400813 | *OO-H unconventional intermediate; static bilayer discredited |
| 9 | Qiu 2026, Angew. Chem. Int. Ed. 65, e21856 | 10.1002/anie.202521856 | AIMD resting-termination ladder; PZC/charging; mechanism crossover |
| 10 | Garcia-Mota 2011, ChemCatChem 3, 1607 | 10.1002/cctc.201100160 | The founding doped-TiO2(110) screen; Cr 0.61 V at U=0; explicit U punt |
| 11 | Man 2011, ChemCatChem 3, 1159 | 10.1002/cctc.201000397 | Universal 3.2 eV scaling; 0.37 V floor; explicit U rejection |
| 12 | Sun 2024, JACS 146, 15515 | 10.1021/jacs.4c04096 | 3d-doped MRuOx dissolution screen + full experimental series |
| 13 | Cao 2026, JACS 148, 4250 | 10.1021/jacs.5c17145 | Pourbaix-SR + bond-length dual descriptor; termination preferences; mis-cited U |
| 14 | Jia 2025, JACS 147, 22642 | 10.1021/jacs.5c04079 | Closed-loop discovery paradigm; surface-state-first protocol |
| 15 | Burnett 2020, Chem. Mater. 32, 6150 | 10.1021/acs.chemmater.0c01884 | (M,Ru)O2 experiments; wet-cell vs MEA non-correlation; leaching |
| 16 | Deng 2025, ACS Catal. 15, 1782 | 10.1021/acscatal.4c05989 | Ordinal U-scan precedent; AEM→OPM mechanism switch; Mn anchor |
| 17 | Feng 2025, J. Catal. 443, 115968 | 10.1016/j.jcat.2025.115968 | **Our exact 3d set on RuO2(110)**, more physics, zero U, experiment |

---

## 3. Findings by theme

### 3.1 U-sensitivity: we have the quantification; Tripkovic has the mechanism; attribution is mandatory

- **Tripkovic 2018** (perovskites, VASP, U = 0/3/5 eV): η(LaCrO3) ≈ 1.41 → 0.65 → 0.30 V (span ~1.1 V) — quantitatively the same phenomenon as our P7 (1.122 V). Mechanism: U-sensitivity is controlled by whether the active cation's **oxidation state changes** between the states compared. Cr is pathological because *O oxidizes Cr(+3) to ~+5 (stable Cr2O5): dE(*O) 0.80 → 2.82 eV across U. Step *differences* do **not** cancel: LaCrO3 step-2 proxy +1.06 eV, step-3 proxy −1.07 eV across U = 0–5. So descriptor swaps do not launder U-sensitivity.
- **HSE is not the fix**: η depends on exact-exchange fraction α as strongly as on U (LaCrO3: 1.40/1.04/0.73/0.56 V at α = 0/0.15/0.25/0.35); their conclusion 3: HSE "cannot be used as benchmarks." → do not spend compute on hybrids; cite instead.
- **U spread is normal**: literature U for LaMnO3 alone spans 1.0–6.7 eV. Our CrO2 spread (MP 3.7 / hp.x 6.16 / lit 7.15 eV) is normal behavior, not an error. The **slab** linear-response non-convergence remains ours.
- **The field's practice, in numbers**: Feng 2025 screens our exact 3d set with **no U at all** and no spin; its largest correction from *any* added physics (constant-potential GC-DFT) is **0.30 V**, and for Cr specifically **0.002 eV** — our 1.12 V U swing is ~4× their worst case and ~500× their Cr correction. Comer 2024 builds 0.17–0.22 eV-MAE surrogates on a single fixed U per metal with no sensitivity scan. Cao 2026 uses U(Ru) = 2.4 eV justified by a **mis-citation** (their ref 54 is a 1994 two-photon quantum-optics paper). Grimaud 2017 — the field's flagship mechanism paper — uses a single Ueff = 3.3 eV. Garcia-Mota 2011 (p.1609) and Man 2011 (p.1165) explicitly punt on +U.
- **Deng 2025** is the reporting template: they scanned Ueff(Mn) 1–5 eV and reported that mechanistic ordering is invariant (SI Table S10, discussed p.1791). Our case is the documented **failure** of that invariance — present it as the converse, with their scan cited as accepted practice.
- **Prior-art gate**: Tripkovic's ref 102 = **Xu, Rossmeisl, Kitchin, JPCC 2015, 119, 4827** — "A Linear Response DFT+U Study of Trends in the Oxygen Evolution Activity of Transition Metal Rutile Dioxides." Our exact material class. Must be fetched and read before any novelty wording on linear-response U (the slab-vs-bulk distinction likely preserves our slab claim, but that must be verified, not assumed).

### 3.2 Descriptor layer: the Gmax column is correct, Exner's, and our table is stale

- Our `g_max()` in `src/dft/volcano_r1.py` is **algebraically identical** to the official 10-span formalism (Razzaq-Exner 2023, eqs 10–25); session recompute reproduced docs/29 §4b Fe (1.567 eV) and Mn (0.969 eV) exactly. Renumbering is provably unnecessary.
- **docs/29 §4b is doubly stale** (verified on disk): the Cr row (1.726/1.426) is the *trapped* geometry — the repaired `runs/Cr_slab/dft_eta.json` gives η_TD = 0.491 V, Gmax(0.3V) = 0.221 eV with limiting span *OH→*OOH (our first genuine multi-step span, which η_TD structurally cannot represent); and the Ni row rests on `runs/Ni_slab/dft_eta.json.RETRACTED`. Any regeneration must name tier version (frozen tier_v2 Cr = 0.330 V; the repaired value is **not** a tier entry until tier_v3 exists) and use only GATE-1-passed Cr energies (P16).
- **Ranking teeth**: Exner's floor — differences in Gmax(η) below **0.20 eV are not meaningful** (from δG‡rds-max ≈ 0.40–0.60 eV). η_TD vs Gmax(0.3V): R² = 0.82 with deviations up to 0.8 V; rank reversals concentrate in the active region Gmax(0.3V) < 1 eV — exactly where near-apex claims live. η = 0.3 V is the community operating point (≥350 mV for 10 mA/cm² even for highly active catalysts).
- **Anti-scaling-breaking result** (Razzaq-Exner 2023 §3.1): breaking SRI 3.2 → 2.46 eV can *reduce* activity (worked example Gmax 0.17 → 0.38 eV); the statistical optimum is the asymmetric SRI = 2.76 eV. → reword `src/hea_oer/descriptors.py` lines 16–17 ("the scaling-relation floor this project aims to circumvent") and drop the retracted-Ni "broken scaling" talking point permanently.
- Man 2011's universal constant (3.20 eV, MAE 0.17 eV, 95% within ±0.4 eV) corroborates the Divanis 3.18 ± 0.12 eV already load-bearing in P17. Man's floor — minimum planar-oxide η_TD ≈ 0.37 V, "activity could not be significantly improved beyond RuO2" — caps any residual compositional statement.
- **Cr's magnetic error is descriptor-material**: the 175 meV metastable *OOH state feeds dG3 and hence Cr's limiting span — by itself ~80% of the 0.20 eV distinguishability budget.

### 3.3 The clean slab is not the operando surface

- **Qiu 2026** (potential-controlled AIMD, explicit water): RuO2(110) is **fully O-covered at ≥ 1.60 V**; *OH_cus onset ~1.50 V (1/3 ML), full *OH_cus at 1.24 V — the clean cus-exposed surface exists at **no** potential in 1.23–1.80 V. The O-terminated phase's PZC ≈ 2.50 V vs SHE ⇒ the electrode is **negatively charged** throughout the OER window; *OH spontaneously deprotonates on an uncharged interface. Mechanism switches (OPM ↔ AEM) at ~1.54 V. *OOH is **transient** under explicit water (spontaneous deprotonation during O–O coupling).
- **Feng 2025** (static surface Pourbaix, 16 terminations): fully O-terminated is the resting state for almost all M-RuO2 at 1.43 V; termination alone moves η_TD by up to ~0.6 V (Ni case).
- **Cao 2026**: dopant-dependent termination preference — **V, Cr, Nb, Mo, W, Ti, Ir prefer O-covered** terminations; Sc/Mn/Fe stoichiometric; Co/Ni/Zn O-depleted. Explicit warning that models ignoring this "may yield incomplete or misleading interpretations." Directly relevant to our clean-termination Cr model and the Cr *OOH anomalies.
- **Razzaq-Exner 2023 §2.5**: on solids one should determine resting-intermediate coverage first (surface Pourbaix), "otherwise, activity trends determined by the free-energy span model are prone to be erroneous." **Jia 2025** operationalizes surface-state-first as current JACS practice.
- Mitigations available: Man 2011 explicitly justifies bare-slab/no-water as the founding-paper standard; Comer 2024 shows dG_O − dG_OH is far less facet/coverage-dependent than individual adsorption energies (3-descriptor bulk-only model, MAE 0.181 eV) — a citable defense of the **ranking coordinate**, if not of absolute η. Qiu notes the O-covered oxide-water interaction is weak (first water layer ~3.78 Å out) — omitting solvation on O-covered rutile is less damaging than on metals.

### 3.4 Solvation and the *OOH problem

- **Gauthier 2017** (explicit bilayers, IrO2(110)): solvation is per-intermediate and H-bond-donor selective. *O/*OH nearly unshifted; ***OOH stabilized 0.3–0.5 eV more than *OH** — and the correction is **coverage-sign-flipping**: −0.3 eV at O coverage, **+0.2 eV** at OH coverage. A single universal number does not exist; only a band [−0.4, +0.2] eV is defensible. Absolute η values — including "Ir 0.781→0.490 V" — must be scoped as *within a fixed unsolvated model*.
- **Gauthier's conformer-spin result is our Cr anomaly's likely mechanism**: the *OOH magnetic moment "changes significantly" between the bridge-H-bonded and up/solvated conformers and "significantly affects the energy"; without spin polarization the conformer gap collapses to ~0.05 eV. A cheap Cr factorial (LIT-3c) tests whether our 175 meV gap is magnetic-state selection.
- **Inico 2024**: conventional *OOH is dynamically unstable on TiO2/RuO2/IrO2(110) in AIMD, converting to ***OO-H** (superoxo + proton on bridging O; O-O 1.30–1.32 Å; already 0.19–0.46 eV lower in vacuum). The static bilayer is **discredited** on these surfaces (0.69 eV artifact vs their own AIMD); one co-adsorbed water captures 0.1–0.4 eV. Spin polarization moves *OOH-type species by 0.3 eV on a semiconducting rutile host — our 175 meV sits inside documented softness.

### 3.5 Mechanism scope (AEM vs LOM/OPM)

- Isotope evidence (Grimaud 2017): LOM is real on covalent, O-vacancy-rich oxides (SrCoO3−δ: 37 monolayers of lattice O; 36O2 onset 1.5 V). Acidic rutiles (Fabbri 2018): RuO2 lattice O evolves in H2SO4; IrO2 ~1% (surface layer only); **crystalline RuO2 films show no lattice exchange** (Stoerzinger) — AEM defensible for pristine hosts; **Ni-doped RuO2 shows enhanced lattice-O activity** (Macounova) — the AEM assumption is weakest for exactly our doped compositions (risk order roughly Cu > Co ≈ Mn > Cr > hosts; Cr's acid escape channel is chromate dissolution).
- Binninger linkage (via Fabbri): OER, lattice-O evolution, and dissolution are thermodynamically inseparable above the equilibrium potential — stability and mechanism caveats must be connected, not listed independently.
- **Deng 2025**: the best catalyst in our own materials family (IrRu-β-MnO2) wins by **leaving AEM** (OPM barrier 0.66 eV vs AEM 0.83 eV, enabled by 2.91 Å cus-cus distance). An AEM-only η_TD screen structurally cannot identify such winners → scope every ranking claim to the AEM channel. Feng's published OPM-rejection criterion (O2 desorption > 0.48 eV) is the citable justification for our AEM-only scope on the systems where it holds.
- Consequence for holes: a missing Co *OOH or a pathological Cr *OOH bounds **only the AEM channel**; where LOM/OPM opens, it can only lower the true overpotential below our η_TD (which bypasses the ~0.37 V AEM floor). Keep this scoping statement separate from the SCF/magnetism explanation of the Cr artifact.

### 3.6 Stability/dissolution

- **Sun 2024** (explicit-H2SO4 dissolution barriers, full 3d series + experiment): stability order Zn > Fe > Ni > Co > Mn > V > **Cr** > Cu > pristine > Ti > Sc; dissolution energy vs measured durability is linear (Fig 2g). ZnRuOx: 320 h vs 20 h for commercial RuO2.
- **Cao 2026** (Pourbaix SR + bond-length dual descriptor, whole d/ds/p block): decay-rate vs SR R² = 0.78; Cr passes the SR screen but fails the bond-length criterion — yet **experimentally CrRuO2 is among their best** (360 h @ 100 mA/cm², suppressed Ru dissolution). Fixed-U DFT cannot reliably *place* Cr; experiment says Cr-doped rutile is genuinely good.
- **Burnett 2020**: dopant leaching is massive (Co **91.4%** of M lost in 1000 cycles; Mg 35.4%) while Ru loss < 0.4%; leaching *correlates with activity*; wet-cell and MEA rankings **disagree** on identical powders ("cannot be used as a … screening protocol"); best wet-cell dopant is d0 **Mg**, which has no AEM site chemistry. → doped-Ru-rutile experiments cannot validate a 3d-site η ranking; the modelled dopant may not persist at the surface.
- → stability belongs in the report as a **scope column** (LIT-6), not a claim: activity (ours) and stability (theirs) are orthogonal axes, and Man 2011 already flagged CrO2 as Pourbaix-unstable under OER.

### 3.7 Prior-art landscape — the four screens

- **Garcia-Mota 2011** is the verbatim shell of our original project (doped TiO2(110), (1×2) cell, half-cus coverage, RPBE, U=0): Cr 0.61 V, Mo 0.53, Ir 0.63, Mn 0.69 V, all "close to RuO2." The withdrawn headline was, additionally, a 15-year-old rediscovery.
- **Feng 2025** is the modern pre-emption: our exact Ti–Zn dopant set on RuO2(110), plus implicit solvation, surface Pourbaix, GC-DFT, microkinetics, and their own synthesis (Cr-RuO2 201 mV, TOF 0.40 s⁻¹, best in set; kinetic winner switches from Co to Cr with potential). Zero Hubbard U, zero spin, zero vibrational checks.
- **Sun 2024 / Cao 2026** close the stability-screening space on RuO2 hosts with experimental validation. **Jia 2025** closes the closed-loop/multi-objective framing (and avoids the 3d problem entirely via d0/d10 chemistry).
- Three Cr-number spread worth quoting side by side: 0.61 V (doped TiO2, U=0) vs ~2.0 V (pure CrO2, U=0, Man Fig 4a) vs 0.41 V + 201 mV experimental (Cr-RuO2, RPBE) vs our 1.12 V U-swing on one fixed system — **Cr OER energetics are protocol-dominated**, which *is* our surviving central story.

### 3.8 What no paper touches (the surviving core)

1. Mirror-plane symmetry trap with **Hessian classification** and measured η impact (plus the audit-lens: the founding screens are structurally blind to it).
2. **Pre-registered falsification** with a triggered withdrawal (P7) — no paper in this sweep pre-registers anything; Cao prints negative results, which is precedent, not pre-emption.
3. **hp.x linear-response U on slabs**, including the non-convergence negative result (gated on the Xu 2015 read).
4. **Magnetic/SCF multistability** as an auditable protocol failure (GATE-1, drifts 175–407 meV, Wilson-CI reporting).
5. The **error-taxonomy-with-fix** synthesis, seven-metals-onto-one-protocol unification, and the closed **design→melt→measure** loop (docs/18 differentiator — untouched).

---

## 4. Wording obligations adopted (no plan change)

1. Withdrawal framed as field-consistent (Exner: η_TD documented least reliable near the apex; reversals up to 0.8 V).
2. P7 attributed: same phenomenon/mechanism as Tripkovic 2018; ours is the pre-registered quantification on doped rutile (110).
3. No hybrid-functional arbitration (Tripkovic conclusion 3) — cite, don't compute.
4. "Fixed-protocol DFT cannot reliably place Cr" — never "Cr is bad"; Cr-doped rutile is experimentally good (Feng, Cao, Lin 2019 via Burnett).
5. AEM-scope caveat package (Grimaud/Fabbri/Qiu/Deng) with the crystalline-RuO2 null result defending the host baseline.
6. Validation paragraph limited to Mn-consistency (Deng: β-MnO2 η10 = 418 mV — qualitative support for Mn-best-endmember at tier_v2) plus leaching caveats; Burnett's wet-cell/MEA non-correlation is the standard rebuttal to "validate against experiment."
7. Gmax presented as adoption of Exner's descriptor (fix `volcano_r1.py` citation); reword the descriptors.py scaling-circumvention docstring; retracted-Ni broken-scaling point stays dead.
8. Every absolute η scoped: bare-surface-limit, AEM-channel, unsolvated, at stated tier and U.

---

## 5. Proposed amendments (ranked; decisions = Frank; each needs a dated docs/43 amendment)

All are CPU-fleet-feasible before the mid-October data freeze. P6 (no per-metal cherry-picking), P19 (uniformity), and frozen-tier discipline apply to every item: new configuration searches run uniformly across Cr/Ir/Ru and produce caveat columns or dated tier_v3 inputs — never post-hoc per-metal fixes.

| Rank | ID | Proposal | Cost | Urgency |
|---|---|---|---|---|
| 1 | LIT-1 | U-robustness package: valence-tracking diagnostic; U-band claim rule (both descriptors + ≥0.20 eV Gmax gap + U-stability) registered **before tier_v3 exists**; Gmax(0.1/0.2/0.3 V) with limiting-span identity across the A0 U grid; intercept-vs-descriptor U-test; regenerate stale docs/29 §4b (trapped Cr row, retracted Ni row) with tier/GATE-1 provenance; fix code citations | ~zero DFT; days of scripting | now |
| 2 | LIT-2 | Termination/coverage resting-state mini-campaign (clean / 1 ML *O / mixed / 1 ML *OH; + O-depleted for Cr) for Ru/Ir/Cr, benchmarked against Qiu's AIMD ladder; Cao-style decision rule (Cr O-covered by >0.1 eV/site ⇒ clean-termination Cr flagged conditional); U-flip check on termination ordering (new to the literature) | ~4–6 relax/metal + SCF U re-evals; days–2 wks | now |
| 3 | LIT-3 | *OOH anatomy: O-O/charge fingerprint classification + scaling-residual audit (zero DFT); *OO-H spot check for Cr/Ir/Ru uniformly (±spin inits); Cr conformer×spin factorial incl. one nspin=1 control (Gauthier diagnostic for the 175 meV anomaly); feeds the held Cr Hessian decision | ~10–15 relaxations | now |
| 4 | LIT-4 | Thermochemical U anchor per problem metal (fit to experimental bulk redox enthalpy spanning the adsorbate-induced valence change, guided by LIT-1); report η at (MP, hp.x, thermochemical) U as a band — grounds the S2 'three determinations' fallback | few bulk SCFs/metal; days | before-report |
| 5 | LIT-5 | Solvation sensitivity band: dG_OOH −0.3 eV central, swept [−0.4, +0.2]; dG_OH/dG_O ±0.1; report band-surviving conclusions; optional (H2O)1 arm with eq-6 decomposition; register **no static bilayer** (Inico) | band: zero DFT; arm: 9–16 relax | before-report |
| 6 | LIT-6 | Stability scope columns: MP/pymatgen bulk Pourbaix flags at pH 0, 1.23–2.0 V; Garcia-Mota Eq. 5 substitutional formation energies; fetch Sun/Cao SIs (per-dopant η10; their dopant U values vs our hp.x) | hours + ~10 bulk SCFs | before-report |
| 7 | LIT-7 | Co *OOH attempt (off-plane, multi-magnetic, GATE-1; declared possible-fail — failure is itself multistability data); scaling-OOH estimate column (0.84·dG_OH + 3.14, labelled) for all metals; Comer open-dataset parity check on dG_O − dG_OH incl. the only external Co/Cu reference | few relax + downloads | before-report |
| 8 | LIT-8 | Mechanism-scope flags: cus-cus M-M distance (zero cost); O 2p band centre vs E_F incl. U-dependence (nscf+projwfc); dopant-adjacent bridging-O vacancy formation energy at 2 U values | hours–days | optional |

Interactions with the running campaign: LIT-2 and LIT-3 slot into/extend Block 1A (extra terminations and initializations); LIT-1 and LIT-5 are pure analysis over the A0 grid and existing ledgers; nothing here alters the 1A replication gate, P12 bins, 1C verdict ladder, or 1B GO window. P13's registered Cr prediction (symmetry correction changes η(Cr) by exactly zero) is untouched — LIT-3's *OO-H search is a *configuration-space* extension, to be reported as a mechanism caveat or a uniformly-applied tier_v3 input, never as a Cr-specific rescue (P6).

---

## 6. Novelty after the sweep

**Dropped outright:** "computational screen of 3d-doped rutiles for acidic OER" as a contribution (Garcia-Mota 2011 shell; Feng 2025 exact-set superset with experiment; Sun/Cao stability screens; Jia closed loop); Cr-near-apex in any form (published 2011 at U=0, re-predicted and experimentally confirmed 2025, and P7-withdrawn); "first to quantify solvation/coverage on rutile (110)" (Gauthier/Inico/Qiu); Gmax as our methodology (Exner's — adopted with citation).

**Attributed, claimable only as extension:** U-sensitivity of 3d-oxide OER energetics as a phenomenon → Tripkovic 2018 (perovskites, same mechanism, same magnitude); linear-response U on rutile OER → Xu/Rossmeisl/Kitchin 2015 (**must read before wording**; likely bulk-only, which would preserve our slab claim); ordinal U-scanning as practice → Deng 2025; symmetric-adsorbate instability on rutile (110) → Goniakowski & Gillan 1995/96 (already credited).

**Surviving and defensible (untouched by all 17):** (a) Hessian *classification* of mirror-locked geometries as genuine saddles with measured η magnitude on MO2(110) OER intermediates, plus the demonstration that the founding screens' force-only convergence is structurally blind to them; (b) the pre-registered falsification framework with a production headline killed by its own pre-committed trigger, and the quantitative foil that the swing (1.12 V) is 4–7× the largest correction the state-of-the-art screens compute at all; (c) hp.x linear-response U **on slabs**, including the non-convergence negative result; (d) magnetic/SCF multistability as an audited protocol failure class (measured drifts 175–407 meV; Wilson-CI reporting); (e) the closed 5–6-class error taxonomy, the seven-metals-onto-one-protocol unification, and — if LIT-2/LIT-8 land — the first per-dopant U-dependence flags for termination and mechanism selection on the 3d-doped rutile series; (f) the self-fabricated design→melt→measure loop as the STS differentiator (docs/18), unaffected.

**Positioning sentence for internal use (not report prose):** the report is a *reliability audit of the screen class these papers exemplify* — citing Feng 2025, Cao 2026, Sun 2024, and Jia 2025 as the state of the art whose conclusions our error classes stress-test — not a competing screen.

---

## 7. Citation ledger

- **Now primary-verified (citable):** the 17 papers in §2.
- **Must fetch before report:** Xu/Rossmeisl/Kitchin JPCC 2015 (119, 4827) — gates hp.x novelty wording; Lin 2019 Nat. Commun. 10:162 (Cr0.6Ru0.4O2 experimental prior art); Comer 2022 JPCC 126, 7903 (pure-rutile slab series); Dickens/Kirk/Nørskov JPCC 2019 (kinetic volcano); McCrory 2013 JACS 135, 16977 + Palkovits 2019 ACS Catal. 9, 8383 (η = 0.3 V justification); Sun 2024 and Cao 2026 SIs (per-dopant η10; dopant U tables).
- **Standing rules unchanged:** Deshpande 2016 = ORR-UQ methodology only; Divanis 3.18 ± 0.12 verbatim; Goniakowski & Gillan credited in all symmetry-trap framing; second-hand citations inside the swept papers remain unverified until pulled.
- **Field-QC exhibits (use politely):** Cao 2026 ref 54 (U provenance cites a 1994 quantum-optics paper); Feng 2025 ref 9 (pancreatic-fibroblast paper cited for RuO2 degradation).

---

## 8. Compliance notes

- Frozen tiers respected: all numbers above quote tier_v2 or explicitly-labelled on-disk repaired values; nothing here constructs tier_v3.
- P6/P19: every proposed configuration search (LIT-3, LIT-7) is specified uniformly across metals; outputs are caveat columns or dated amendments, not per-metal fixes.
- P18 blind hygiene: LIT-1(b) registers the ranking-claim rule before tier_v3 exists precisely so the rule cannot be accused of being fitted to the outcome.
- No re-framing of Cr as a discovery anywhere in this memo; the withdrawal stands.
- Amendment decisions rest with Frank; this memo is analysis, not the STS report, and none of its prose may enter the report or essays.

---

## 9. Adversarial verification appendix

§§1–8 are the synthesis stage's output. Each of LIT-1…LIT-6 was then independently attacked by a verifier agent instructed to refute it — re-reading the cited PDF pages, checking pre-registration compatibility, and auditing cost — plus one global skeptic arguing the full "change nothing" case. **LIT-7 and LIT-8 were not adversarially verified** (verification capped at six proposals); treat their §5 entries as unverified synthesis output.

| ID | Verdict as written | Outcome |
|----|--------------------|---------|
| LIT-1 | **Upheld** | Adopt with the corrected text in §9.2 (key fix: no `.save` dirs survive on disk, so Löwdin charge analysis costs one fixed-geometry SCF + projwfc.x per point; the active-site **local magnetic moment** — already printed in every spin-polarized output — is the zero-DFT primary valence tracker) |
| LIT-2 | **Refuted as written** | Corrected LIT-2-rev in §9.3. Three failures: a 2×1 cell cannot represent Qiu's 1/3, 2/3, 5/6 ML rungs (benchmark must be a coarsened ladder with ±0.25 V tolerance and a pre-registered FAIL path); Block-1A outputs must be *reused*, not re-run; and the "~0.6 V Ni termination shift" figure attributed to Feng is **withdrawn** — not on the cited pages |
| LIT-3 | **Upheld** | Two wording fixes before deposit: Inico's fingerprint charge thresholds are **Bader (QTAIM)**-defined, not Löwdin — use O–O distance as primary fingerprint, Bader via pp.x as secondary; and the *OO-H stabilization is per-oxide (0.46 eV TiO₂, 0.19 eV RuO₂, ~0.13–0.15 eV IrO₂), not a blanket 0.19–0.46 eV |
| LIT-4 | **Upheld only as corrected** | §9.4. Reframed: the MP U = 3.7 eV is *itself* thermochemically fitted (Wang–Ceder lineage), so the leg is not "independent" — the honest argument is **same-code re-fit** (U does not transfer across projector schemes). The dated amendment must be registered **before any fit computation runs**, because η(U) is already known and post-hoc freedom in couple/data choice would let the fit select its own η |
| LIT-5 | **Refuted as written** | Corrected LIT-5r in §9.5. The "−0.3 eV central value" is indefensible: Gauthier's stabilizations are stated **upper bounds**, and both his coverage cases have an *occupied* neighboring cus site — no literature value exists for our low-coverage bare-slab geometry. Only the band [−0.4, +0.2] eV survives, with a no-promotion guard |
| LIT-6 | **Upheld** | Adopt with corrections folded into §9.6: register outcome-neutrally *before* computation; Garcia-Mota Eq. 5 formation energies are U-dependent (slab totals carry U, elemental references do not) and must be reported at production U **and** the P7 U-range endpoints; Jia's gate also requires a solid phase present in the window |

### 9.1 Global skeptic: the "change nothing" case, and where it wins

The skeptic's verdict: **the do-nothing case loses overall (upheld = false), but wins against roughly half the proposed compute.** Its strongest points, accepted into the recommendation:

- **Prereg integrity is the product.** Eight new packages sourced from a literature sweep conducted *after* 1C returned CONFIRMED and after the 1.12 V Cr swing was measured hands a hostile reviewer the forking-paths narrative. Mitigation: LIT-1a's "registered prediction" must be framed the way docs/43 §0a framed its own control — a mechanism test *motivated by Tripkovic, read after the swing was measured*, stated with that weakness — never dressed as a prediction.
- **Deadline arithmetic.** ~9 weeks to the mid-October data freeze, already committed to Week-1 blocks, the docs/44 §3 lanes, ZPE, and the melt+measure campaign — the actual STS differentiator. Every fleet-hour given to LIT-* is taken from those.
- **Redundancy.** The A0 140-SCF η(U) grid already *is* the U-band; 1A's 2×1-*O arm already probes coverage with a registered promotion rule; GATE-1/P16 already audits magnetic multistability.

Why it nonetheless fails: (a) most of the decisive content is **zero-DFT post-processing** of already-converged outputs — compatible with running the campaign unchanged; (b) the killer: **LIT-1b's ranking-claim rule must be registered before tier_v3 exists or blindness is unrecoverable** — deferring it to October, after tier_v3 exists, is the actual data-peeking; (c) hygiene is an obligation, verified on disk (docs/29 §4b still carries the trapped Cr rows 1.726/1.426 and a Ni row resting on `dft_eta.json.RETRACTED`); (d) attribution is load-bearing — the surviving novelty wording cannot be written until Xu/Rossmeisl/Kitchin 2015 is read; (e) one compute item is decision-relevant: Qiu/Cao/Feng jointly indicate the clean cus surface may exist at *no* operating potential, calibratable only by the trimmed LIT-2 check.

**Skeptic's trimmed adoption set** (endorsed as the recommendation of this memo):

- **Adopt now, zero/near-zero DFT:** LIT-1 (full, as corrected — 1b is time-critical before tier_v3), LIT-3's zero-DFT fingerprint classification, LIT-5r's band overlay (a, c, d), LIT-6's scripting parts (Pourbaix flags, SI fetches, leaching caveat text), and all §4 wording/attribution obligations including the Xu 2015 fetch.
- **Adopt trimmed, bounded compute:** LIT-2-rev's validation core (coarsened Qiu-ladder benchmark on Ru + Cr O-covered preference check), ~a dozen relaxations on one box; LIT-3's *OO-H spot check and Cr conformer×spin factorial (~10–15 relaxations, slots into 1A machinery, feeds the held Cr Hessian decision).
- **Defer or cut:** LIT-4 (thermochemical U re-fit), LIT-5's single-water arm, LIT-7a (Co *OOH attempt), LIT-8b/c (projwfc + vacancy energies), and LIT-2's full per-metal termination campaign. These can still become labelled exploratory analyses in October if time allows.

### 9.2 LIT-1 (corrected): U-robustness analysis package

**What changes.** (a) Post-process every existing (metal × adsorbate × U) run: active-site local magnetic moment vs bare slab as the primary valence tracker (zero DFT — already printed in every spin-polarized pw.x output), supplemented by Löwdin charges from projwfc.x where wavefunctions can be cheaply regenerated (no `.save` dirs survive; each Löwdin point costs one fixed-geometry SCF + projwfc). Classify each ΔG as valence-conserving (predicted U-robust) or valence-changing (predicted U-fragile) — an adaptation of Tripkovic's V(B) analysis (which assigns valence via moments, charges *and* O–O bond structure, not Löwdin alone; peroxo/superoxo O–O distances checked as in their protocol). Registered mechanism test (motivated post-hoc by Tripkovic, stated as such): the 1.12 V η(Cr) swing correlates with a Cr oxidation-state change under *O/*OOH; U-flat quantities show none. (b) Register the ranking-claim rule **before tier_v3 exists** (preserves P18 blind hygiene): a pairwise ordering is claimed only if it holds under both η_TD and G_max, the G_max gap is ≥ 0.20 eV (Exner floor), and it is stable across the U band {U=0, MP U, hp.x U if GO, thermochemical U if LIT-4 adopted}. (c) Recompute G_max at η = 0.1/0.2/0.3 V with the limiting-span identity for every U in the A0 grid (pure function of the same four ΔG values — zero DFT; A0 ΔG(U) are fixed-geometry and that approximation is stated). (d) Test whether the 3.2 eV scaling intercept is U-robust while the descriptor axis is U-fragile ("U moves you along the volcano, not off it") — motivating prior from Tripkovic Table 3 itself: LaCrO₃ ΔE(*OOH)−ΔE(*OH) moves only 2.94→2.93 eV over U = 0–5 while ΔE(*O)−ΔE(*OH) moves +1.06 eV. (e) Hygiene: regenerate docs/29 §4b (stale trapped-Cr row 1.726/1.426; Ni row on `dft_eta.json.RETRACTED` — both verified on disk) with tier version named per docs/43 §0 and GATE-1 status per P16; fix `volcano_r1.py` docstring to cite Exner 2020 + Razzaq-Exner 2023 (currently cites only Acc. Chem. Res. 2024 — verified, lines 8–11).

**Paper basis.** Tripkovic p.1139 (valence rule), pp.1141–1142 + Table 3 p.1142 (LaCrO₃ ΔE(*O) 0.80→2.82 eV; step differences +1.06/−1.07 eV — single-step differences do **not** launder U; the OOH−OH difference is U-flat, the prior for (d)). Exner 2020 pp.12611, 12615 (0.20 eV floor), Fig 7 p.12613 + p.12614 (active-region rank reversals). Razzaq-Exner eqs 10–25 p.1742, span switching p.1745. Deng p.1791 (ordinal U-scan as field practice). Man p.1161 Fig 2 (3.20 eV intercept, MAE 0.17 eV).

**Cost.** Zero new DFT for the moment tracker, G_max(U) grid, and table regeneration; tens of cheap SCFs (≤ ~150 if the full A0 grid gets Löwdin) on one fleet box; days of scripting. **Urgency: now** — (b) is time-critical.

### 9.3 LIT-2-rev (corrected): termination/coverage resting-state check

**What changes.** Static CHE surface Pourbaix for Ru, Ir, Cr in the existing 2×1 cells over the terminations representable at that size: clean / 1 ML *O_cus / mixed 1:1 *OH–*O / 1 ML *OH (+ O-depleted variant for Cr). **Reuse, do not re-run,** Block-1A 2×1 outputs where they already are these states (2×1 neighbour-*O with working *O = 1 ML *O_cus; working *OH + *O spectator = mixed); genuinely new relaxations (~2–4 per metal) run under the standing protocol (off-plane starts, nosym/noinv, GATE-1 child, total and absolute magnetisation with the 0.1 μ_B channels for Cr). **RuO₂ validation, two-sided and pre-registered:** a 2×1 cell cannot represent Qiu's 1/3, 2/3, 5/6 ML rungs, so the scoreable benchmark is the coarsened ladder — PASS iff (a) ordering with falling potential is full-O → mixed → full-*OH and (b) the two transition potentials fall within ±0.25 V of Qiu's AIMD brackets (~1.50 V and ~1.24 V; tolerance absorbs the vacuum-vs-solvated offset). On PASS, Ir/Cr columns report as validated-by-proxy; on FAIL, they still report, labelled vacuum-CHE-only with the measured RuO₂ discrepancy attached as systematic error. Either way: report the resting termination at U = 1.23 V + η per metal and re-word the descriptor as **bare-surface-limit η_TD**. Decision rule (adapted from Cao's oxygen-environment finding, restated in CHE-at-U form): if Cr prefers an O-covered termination by > 0.1 eV/site at operating potential, all clean-termination Cr energetics are flagged conditional. **U-flip extension:** re-evaluate the termination ordering at 2–3 U values (fixed-geometry SCF level). Novelty framed honestly: Tripkovic determined termination at U = 5 eV and assumed U-independence (their LaCoO₃ case already shows terminations differ between Hamiltonians); no systematic U-resolved resting-termination scan exists for rutile MO₂ — a Cr resting-surface flip with U would be a qualitative amplification of P7 closing a gap Tripkovic flagged, not "no paper has shown." Deposit as a dated amendment before any LIT-2 job launches.

**Paper basis (all page-verified).** Qiu pp.3–5 + Fig 2 (fully O-covered ≥ 1.60 V; 1/3 ML *OH_cus at 1.50 V; full *OH_cus at 1.24 V; no bare cus surface anywhere in 1.23–1.80 V; PZC ≈ 2.50 V vs SHE). Cao p.4251 Fig 1e + p.4253 (V/Cr/Nb/Mo/W prefer O-terminated; "incomplete or misleading interpretations" verbatim). Feng p.4 (almost all M-RuO₂ fully O-terminated at 1.43 V) and p.5 — **the earlier "~0.6 V Ni shift" figure is withdrawn** (not on the cited pages; contradicted by main-text numbers; Ni is the 1.00 V outlier among O/OH-terminated M-RuO₂). Razzaq-Exner pp.1745–46 (resting-coverage-first, verbatim). Jia pp.4–6 (surface-state-first protocol). Tripkovic pp.1140–41 (the precedent the novelty claim must credit).

**Cost.** ~2–4 new relaxations per metal after Block-1A reuse, each with its GATE-1 child, + 2–3 fixed-geometry SCFs per termination for the U-flip; days to ~2 weeks. **Urgency: now** (compute lead time) — but per §9.1, the *trimmed* core (RuO₂ benchmark + Cr O-covered check) is the recommended scope.

### 9.4 LIT-4-rev (corrected): same-code thermochemical U re-fit

**What changes.** Fit U(Cr) in our QE 7.5 + our pseudopotentials/projectors to the experimental enthalpy of a bulk Cr-oxide redox reaction spanning the oxidation-state change the adsorbates induce. Justification is **code-consistency plus couple-specificity, not independence**: MP's U = 3.7 eV is itself thermochemically fitted, but in VASP PAW to generic couples, and U does not transfer across projector schemes. Report η(Cr) at (MP U, hp.x U, thermochemical U) as a band; no single-U headline; the P7 withdrawal stands regardless of where the fitted U lands. Pre-commitments registered in the dated amendment **before any fit computation**: (1) auxiliary reactions recast on H₂/H₂O references (oxide + H₂ → lower oxide + H₂O) so molecular-reference error cancellation matches the CHE scheme — removing the PBE O₂ error that would otherwise be absorbed into U; (2) exact tabulated enthalpies with source (Barin/NBS/JANAF) and uncertainties written into the amendment — CrO₂ is metastable with scattered ΔH_f data and is the weak datum in both Cr couples; (3) both couples fitted as consistency check — Cr₂O₃/CrO₂ (III→IV) and CrO₂/CrO₃ (IV→VI), primary couple selected by the valence-tracking output (LIT-1), with the caveat that CrO₃ is a d⁰ molecular-chain solid so U acts only through CrO₂ in that couple; (4) ill-conditioning gate: publish d(ΔH)/dU per reaction, propagate tabulated-enthalpy uncertainty into fitted-U uncertainty; beyond a pre-set bound (e.g. ±1.5 eV) the leg reports as unusable, not forced; (5) magnetic-configuration scan per oxide per U point (Cr₂O₃ AFM, CrO₂ FM half-metal, CrO₃ NM); (6) inherited limits stated from Tripkovic p.1142 (one bulk reaction cannot guarantee all four electrochemical steps; if valence tracking shows O 2p hole localization or non-integer mixed valence, no tabulated couple applies and the leg reports N/A). Scope: Cr now; Mn/Fe/Ni only if they enter conclusions; Co/Cu excluded until they have usable adsorbate data; Ru/Ir (U=0) out of scope. Cite Wang–Maxisch–Ceder PRB 2006 + Jain 2011 as the executed precedent; drop the Tripkovic p.1143 cite for the fit protocol (it announces a different remedy).

**Cost.** ~20 bulk relax/SCF runs per metal (3 oxides × ~6-point U grid) + magnetic scans; CPU-days, trivially parallel. **Urgency: before-report; amendment must precede the first fit run.** Per §9.1: recommended **defer/cut** unless time allows.

### 9.5 LIT-5r (corrected): solvation sensitivity band

**What changes.** (a) All as-computed vacuum η_TD and G_max columns stay primary. Sensitivity overlay: sweep ΔG_OOH over [−0.4, +0.2] eV (the rutile-(110) literature band, IrO₂-derived; **no central value designated** — the correction is coverage-dependent and sign-flipping, both Gauthier coverage cases have an occupied neighboring cus unlike our slabs, and Gauthier states his values are upper bounds) and ΔG_OH/ΔG_O over 0 ± 0.1 eV. Report which rankings, apex assignments, and limiting-step labels survive the whole band including zero. **Guard (pre-registered): shifted columns may only demote or qualify vacuum-based conclusions — no candidate failing at unshifted values may be promoted via a shifted column.** (b) Optional compute arm, framed as a *material-dependence probe*, not an in-house solvation measurement (Inico: one water is insufficient): single co-adsorbed (H₂O)₁ for Cr/Ir/Ru × {*OH, *O, *OOH}, ≥2 water placements per system, multi-magnetic-start protocol, analyzed with Gauthier's eq-6 decomposition; realistic scope 20–50 relaxations. (c) **Pre-register that no static water bilayer will be run**: Inico shows the bilayer is unphysical on these surfaces (AIMD: 45%/63% water dissociation on RuO₂/IrO₂; the bilayer inflates the RuO₂ *OOH/*OO-H splitting 0.19 → 0.88 eV, a ~0.69 eV artifact). (d) Cite Gauthier p.4 (solvent-dependent *OOH magnetic-moment changes significantly affecting energy) as independent support for the Cr *OOH metastable-magnetic-state finding.

**Cost.** Band: hours of scripting, zero DFT. Optional arm: 20–50 relaxations. **Urgency: before-report.** Per §9.1: adopt (a)/(c)/(d) now; defer the (b) arm.

### 9.6 LIT-6 corrections (folded)

Register outcome-neutrally **before** computation, with the pre-amendment text archived. Jia's gate is ΔG_pbx < 0.5 eV/atom **and** a solid phase present in 1.23–2.0 V vs SHE; note RuO₂ itself crosses its RuO₄ line at ~1.82 V (Cao Fig 2b), so a host flag near the window top is expected gate behavior, not a defect. Garcia-Mota Eq. 5 formation energies are U-dependent (slab totals carry U, elemental references do not): report at production U and the P7 U-range endpoints, flagging any dopant whose stability flips across the range. Leaching caveats stated with both edges (Burnett's Co activity *rose* post-leach; Deng's Mn leaching is sacrificial-protective) — a scope limit on what the ranking predicts, not "the catalyst is dead." **Firewall:** stability columns are orthogonal scope documentation; they may note Co/Cu would have been triaged on independent grounds, but must not be used to claim the withdrawn Cr headline or the P7 finding is moot.

### 9.7 Decision sheet for Frank

Each row needs a yes/no; every "yes" becomes a dated docs/43 amendment (pre-amendment text archived) before its first job runs. Recommended set = §9.1 trimmed adoption.

| Decision | Item | Recommended |
|---|---|---|
| D1 | LIT-1 as corrected (§9.2), incl. the time-critical 1b claim rule | **Yes, now** |
| D2 | LIT-2-rev trimmed core: RuO₂ coarsened-ladder benchmark + Cr O-covered check (~12 relaxations) | **Yes, now** |
| D3 | LIT-2-rev full per-metal termination campaign + U-flip | Defer |
| D4 | LIT-3 with wording fixes (zero-DFT fingerprints now; *OO-H spot check + Cr conformer×spin factorial ~10–15 relaxations) | **Yes, now** |
| D5 | LIT-4-rev thermochemical U re-fit | Defer/cut |
| D6 | LIT-5r band + no-bilayer registration + Gauthier citation (zero DFT) | **Yes, now** |
| D7 | LIT-5r single-water probe arm | Defer |
| D8 | LIT-6 as corrected (scripting parts now; ~10 bulk SCFs when convenient) | **Yes** |
| D9 | LIT-7 (unverified) — Co *OOH attempt / scaling column / Comer parity | Verify first if wanted |
| D10 | LIT-8 (unverified) — mechanism-scope flags | Verify first if wanted |
| D11 | §4 wording/attribution obligations + Xu 2015 fetch (no prereg change) | **Yes, automatic** |


---

## 10. Addendum (2026-08-12): the Xu 2015 gate, resolved

Xu, Rossmeisl & Kitchin, "A Linear Response DFT+U Study of Trends in the Oxygen Evolution
Activity of Transition Metal Rutile Dioxides," *J. Phys. Chem. C* **2015**, 119, 4827–4833
(10.1021/jp511426q) was pulled via Purdue on 2026-08-12 and read in full. (The 2026-08-12
pull first fetched the wrong Kitchin JPCC 2015 paper — Curnan & Kitchin, 10.1021/acs.jpcc.5b05338,
kept and indexed on its own merits; see docs/43 A5.8.) Gate outcomes:

**The slab hp.x claim survives.** Their linear-response U is **bulk-only**: Cococcioni–de
Gironcoli supercell method, perturbations up to ±0.15 eV on both metal and oxygen in
2×2×2 48-atom rutile supercells (p. 4828). Adsorption energetics ran on two-layer
H-terminated (110) slabs with the bulk U applied. No slab linear-response calculation
appears anywhere in the paper (which predates hp.x). The §3.8/§6 wording stands, now
verified rather than assumed: our slab-DFPT attempt and its non-convergence result are,
to our knowledge, without precedent — and the bulk-U-applied-to-slabs practice our
attempt was probing is exactly what Xu 2015 canonized.

**New attribution debts (§6 updated by this addendum):**

1. **U-dependence of rutile (110) OER energetics as a phenomenon → Xu 2015, not
   Tripkovic.** They scanned U = 0–8 eV in 0.5 eV steps on our exact surface class,
   including CrO₂ and MnO₂: adsorption weakens systematically with U, scaling relations
   established at U = 0 are preserved for 4d/5d, and applying the computed U moves
   compounds **along** the volcano (pp. 4829–4831). Tripkovic 2018 remains the
   attribution for the valence-change **mechanism** and the perovskite η swings; Deng
   2025 for ordinal U-scans as reporting practice. Our surviving contribution is
   unchanged in kind but must be worded against Xu: the pre-registered,
   falsification-grade quantification of the **near-apex failure mode** at fixed
   geometry (η(Cr) swing 1.122 V), plus the magnetic-multistability audit. Xu's own
   screening conclusion contains the caveat our case demonstrates: U = 0 trend studies
   "should produce similar conclusions, **except perhaps near the top of the volcano**"
   (p. 4831) — quote it; it is the paper conceding the exact regime P7 fired in.
2. **A5.1(d)'s intercept test ("U moves you along the volcano, not off it") is a
   replication-and-extension of Xu's central result**, not a novel hypothesis. The
   registered test is unchanged; its motivating prior is now Xu 2015 (rutile, same
   surfaces) with Tripkovic Table 3 as the differences-don't-cancel counterpoint. Any
   report wording presents it as testing whether Xu's scaling-preservation result
   survives on *doped* rutiles under our protocol.
3. **The Cr *OOH pathology has a 2015 sighting.** On CrO₂ and MnO₂ they found *OOH
   adsorption becomes unstable above U ≈ 4 eV, breaking the OH/OOH scaling relation —
   "We are unsure how to interpret the breaking of the surface−adsorbate bonds"
   (p. 4830). Our metastable-magnetic-state finding and the LIT-3 anatomy are the
   follow-up that question has been waiting for; cite accordingly.
4. **CrO₂ U = 7.15 eV (their Table 1) is the "lit 7.15" leg of our U spread — now
   primary-verified.** The three-determination bracket becomes precisely citable:
   MP 3.7 (VASP PAW thermochemical fit) / our hp.x DFPT bulk 6.16 / Xu supercell linear
   response 7.15 eV — with the DFPT-vs-supercell methods difference stated rather than
   implied. Their Table 1 also gives MnO₂ 6.63, TiO₂ 4.95 (inside the 1B GO window
   [3.0, 7.0] eV), RuO₂ 6.73, IrO₂ 5.91.
5. **A caveat lands on the U = 0 Ru/Ir anchor convention.** Xu computed linear-response
   U for the 4d/5d hosts and found that applying it *improves* agreement with the
   experimental activity ordering (IrO₂ > RhO₂ > RuO₂ > PtO₂ vs measured
   RuO₂ ≈ IrO₂ > RhO₂ > PtO₂), with reaction-energy shifts of 0.2–0.4 eV that never
   flip a compound between volcano legs (p. 4831). Our production protocol's U = 0 on
   Ru/Ir (MP convention) is defensible but must carry this citation as the measured
   size of what the convention neglects.
6. **One more Cr-instability prior for LIT-6:** they excluded CrO₂ from the activity
   comparison outright on Pourbaix grounds (p. 4831, citing the Pourbaix Atlas) —
   alongside Man 2011's identical flag, the anticipated Cr bulk-Pourbaix flag in
   A5.5(a) now has two independent priors and must be presented as confirmation of
   known thermodynamics, never as a finding.

**Also of practical use:** their complete inputs/outputs are open data
(10.5281/zenodo.12635) — an external parity anchor for our QE rutile setups if one is
ever needed; and their two-layer-slab validation (parity and shared scaling vs a
four-layer slab at U = 0, Fig 1) is the citable precedent for economical rutile (110)
slab models.

The A5.8 bar on linear-response-U novelty wording is lifted by its own terms; the
obligations above replace it. This addendum records a read, not a plan change — no
docs/43 amendment is required, and the report prose remains Frank's.

