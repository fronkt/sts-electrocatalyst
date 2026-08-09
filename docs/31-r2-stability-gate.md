# 31 — R2: the aqueous-stability gate

**Date:** 2026-07-31
**Status:** COMPLETE. **$0 spent, no box, no GPU.** The rented R1 instance was not touched.
**Follows:** [docs/30 §6](30-qc-audit-and-r1-campaign.md) (which costed R2 at $0 and predicted
the shape of the answer) · [docs/28 §3](28-electrocatalyst-revival-plan.md) (the claims graded here)
**Code:** `src/dft/pourbaix_r2.py` (new) · `tests/test_pourbaix_r2.py` (new, 8 tests)
**Artifacts:** `results/r2_stability.json` (gitignored; regenerate with one command) ·
`docs/figs/pourbaix_mno2.png` · `docs/figs/pourbaix_mno2.json` (committed sidecar)
**Not committed** — left in the working tree for Frank.

```
PYTHONPATH=src python src/dft/pourbaix_r2.py run       # gate + windows + dG_pbx + figure
PYTHONPATH=src python src/dft/pourbaix_r2.py selftest  # offline, no key, no network
```

---

## 1. Verdict

**Of the six rutile MO₂ endmembers the DFT campaign was built around, at most two are
physically realizable rutile electrodes, and exactly one of those has any aqueous stability
window at all.** Four fail before a single energy is computed — the rutile polymorph either
has no experimental structure (FeO₂) or does not exist in the Materials Project at all
(CoO₂, NiO₂, CuO₂, across 37/15/8 catalogued polymorphs respectively). The fifth (CrO₂) is a
real bulk material but has **no stability window at any pH**: it goes to soluble chromate.
The sixth, β-MnO₂ (pyrolusite), is real and does have a window — a window whose upper edge
sits **0.04–0.35 V above the OER equilibrium**, i.e. it is consumed anodically as
permanganate at any overpotential the campaign's own DFT says this material would need.

The gate reproduces, without being told, the one fact about this chemistry everyone agrees
on: **IrO₂ is the only phase in the whole set whose window spans the acid OER band**
(0.442 → 1.869 V vs RHE at pH 0), and **RuO₂'s window closes at 1.003 V vs RHE**, below the
OER equilibrium, matching the measured dissolution of Ru under acidic OER
(Cherevko et al., ChemCatChem 2014, [10.1002/cctc.201402194](https://doi.org/10.1002/cctc.201402194);
Catal. Today 2016, [10.1016/j.cattod.2015.08.014](https://doi.org/10.1016/j.cattod.2015.08.014)).
That is an external validation the DFT tier still does not have.

**Consequence, stated plainly: the rutile tier is a CALIBRATION tier, not a screening
result, and the project must say so in every artifact that quotes η.** η(CrO₂), η(FeO₂),
η(CoO₂), η(NiO₂), η(CuO₂) are properties of model solids, not of candidate electrodes.

## 2. Stage 1 — the phase-existence gate

Purely structural, no energetics. For each MO₂, does Materials Project hold a
**P4₂/mnm (#136, rutile)** entry; does it carry ICSD ids (`theoretical = False`, i.e. someone
made it and diffracted it); and how far above the convex hull does it sit. MP runs structure
substitution across every prototype it holds, so the *absence* of a rutile entry after that
sweep is meaningful negative evidence, not just a gap.

| Endmember | rutile entry | ICSD-backed | E_hull(rutile) eV/atom | min E_hull over **all** polymorphs, eV/atom | verdict |
|---|---|---|---|---|---|
| **MnO₂** | `mp-510408` | **yes** (icsd-20229, -393, -246888, -643186) | 0.046 | 0.000 | **ambient phase** (pyrolusite) |
| **CrO₂** | `mp-19177` | **yes** (icsd-9423, -35327, -202836, -246901) | 0.000 | 0.000 | real bulk phase, thermally metastable |
| FeO₂ | `mp-850222` | no | 0.145 | 0.145 | hypothetical structure |
| CoO₂ | **none of 37** | — | — | 0.000 | **absent** |
| NiO₂ | **none of 15** | — | — | 0.127 | **absent** |
| CuO₂ | **none of 8** | — | — | 0.180 | **absent** |
| RuO₂ *(anchor)* | `mp-825` | yes (icsd-84618, -84619, -23961, -15071) | 0.000 | 0.000 | ambient phase |
| IrO₂ *(anchor)* | `mp-2723` | yes (icsd-56009, -84577, -640885, -640887) | 0.000 | 0.000 | ambient phase |

The last-but-one column is the sharper one. `min E_hull > 0` means the **MO₂ stoichiometry
itself** is unstable in *any* structure at 0 K in MP's GGA+U: NiO₂ by 0.127 eV/atom, CuO₂ by
0.180, FeO₂ by 0.145. Those three compositions decompose to a lower oxide plus O₂ before the
question of which polymorph even arises.

What the real phases are, where a real phase exists:

- **CoO₂** — the experimentally real CoO₂ is the layered CdI₂-type R-3̄m phase from fully
  delithiated LiCoO₂ (`mp-550206`, ICSD-backed, 7 meV/atom above the hull; Amatucci, Tarascon
  & Klein, *J. Electrochem. Soc.* **143**, 1114, 1996,
  [10.1149/1.1836594](https://doi.org/10.1149/1.1836594)). Not rutile.
- **NiO₂** — likewise layered R-3̄m from delithiated LiNiO₂ (`mp-35925`, `mp-25210`), and
  ≥ 0.127 eV/atom above the Ni–O hull. Not rutile.
- **CuO₂** — no rutile, and nothing closer than 0.18 eV/atom to the Cu–O hull. Consistent
  with docs/28: there is no bulk Cu(IV) dioxide.

**This decides the Co/Cu SCF failures.** docs/28 §2 argued they were "physics, not tuning".
Stage 1 makes that concrete and stronger: there is no rutile CoO₂ or CuO₂ anywhere in a
database that has tried the substitution. Two solvers disagreeing about the self-consistent
spin state at fixed coordinates is what a calculation looks like when it is being asked
about a structure that has no ground state to find.

## 3. Stage 2a — β-MnO₂, the one endmember with a window

Built **offline** from hand-entered experimental ΔG_f° (298 K, 1 bar; NBS tables, Wagman et
al., *J. Phys. Chem. Ref. Data* **11** Suppl. 2, 1982, cross-checked against Pourbaix's
*Atlas*), because `pymatgen.analysis.pourbaix_diagram` ships no bundled thermodynamic data.
**Axis: experimental ΔG_f. Not DFT.** Figure: `docs/figs/pourbaix_mno2.png`.

> **Dissolved-Mn concentration = 1 × 10⁻⁶ M throughout** (the Materials Project convention).
> A window quoted without its concentration is meaningless: the reductive edge moves by
> −0.0591/2 V and the oxidative edge by +0.0591/3 V per decade of dissolved ion, so raising
> the electrolyte to 10⁻³ M *widens* the pH-0 window by ≈ 0.15 V. Every number below is at
> 10⁻⁶ M.

| pH | lower edge (V vs RHE) | upper edge (V vs RHE) | width (V) | reduces to | oxidises to | η headroom to upper edge (V) |
|---|---|---|---|---|---|---|
| 0 | **1.407** | **1.583** | 0.176 | Mn²⁺(aq) | MnO₄⁻(aq) | **+0.354** |
| 7 | 0.993 | 1.445 | 0.452 | Mn²⁺(aq) | MnO₄⁻(aq) | +0.216 |
| 13 | 0.974 | 1.327 | 0.353 | Mn₂O₃(s) | MnO₄⁻(aq) | +0.098 |
| 14 | 0.974 | **1.270** | 0.295 | Mn₂O₃(s) | MnO₄²⁻(aq) | **+0.041** |

*(η headroom = upper edge − 1.229 V, the OER equilibrium, which is pH-independent on the RHE
scale. "reduces to"/"oxidises to" are the phases bounding the window below and above.)*

**Answer to the question the gate was built to ask.** β-MnO₂'s upper edge is **above** the
OER equilibrium potential at every pH — but only just, and it is **below** a realistic
operating potential of 1.53 V (η = 0.30 V) at pH 7, 13 and 14. Only at pH 0 does the window
contain 1.53 V. Two further consequences:

1. **At pH 0 the window has a floor as well as a ceiling.** At η < 0.178 V, β-MnO₂ is
   reduced and dissolves as Mn²⁺; above η = 0.354 V it is oxidised to permanganate. The
   usable acid band is the 0.176 V slot **η ∈ [0.178, 0.354] V**.
2. **Our own DFT puts the electrode far outside every window.** The campaign's converged
   value is η(β-MnO₂(110)) = 0.892 V (docs/26), i.e. a limiting potential of
   **U_L = 2.121 V vs RHE** — 0.54 V above the upper edge at pH 0 and 0.85 V above it at
   pH 14. Even with the honest ±0.3 V method error bar (docs/28 §4 F3;
   Jones et al., *Chem. Rev.* 2024, [10.1021/acs.chemrev.4c00171](https://doi.org/10.1021/acs.chemrev.4c00171)),
   the sign of that gap does not change.

**Validation of the hand-entered table** (`selftest`): two boundaries derived by hand from
the same ΔG_f numbers —
MnO₂ + 4H⁺ + 2e⁻ → Mn²⁺ + 2H₂O and MnO₄⁻ + 4H⁺ + 3e⁻ → MnO₂ + 2H₂O —
are reproduced by pymatgen's halfspace construction to **−0.03 mV and +0.12 mV** at pH 0 and
pH 7. That is the cheapest available proof that the sign, units, H₂O reference and
concentration term are wired in correctly.

## 4. Stage 2b — MP PBE+U ΔG_pbx, only for what cleared stage 1

**Axis: Materials Project GGA/GGA+U solids (MP2020 corrections) + experimental aqueous ions,
Persson et al. scheme (*PRB* **85**, 235438, 2012,
[10.1103/PhysRevB.85.235438](https://doi.org/10.1103/PhysRevB.85.235438); SCAN successor,
Wang et al., *npj Comput. Mater.* 2020, [10.1038/s41524-020-00430-3](https://doi.org/10.1038/s41524-020-00430-3)).**
ΔG_pbx in eV/atom, dissolved ions at 10⁻⁶ M. **This is a different axis from §3 and the two
are never mixed.**

| Rutile phase | mp-id | ΔG_pbx pH 0, 1.23 V | pH 0, 1.53 V | pH 14, 1.23 V | pH 14, 1.53 V | window at pH 0 (V vs RHE) |
|---|---|---|---|---|---|---|
| β-MnO₂ | `mp-510408` | +0.145 | +0.030 | +0.030 | +0.248 | none (floor +0.030, see note) |
| CrO₂ | `mp-19177` | +0.251 | +0.300 | +0.524 | +0.724 | **none at any pH** (floor +0.068 at pH 7) |
| RuO₂ | `mp-825` | +0.301 | +0.701 | +0.301 | +0.701 | 0.294 → **1.003** |
| IrO₂ | `mp-2723` | **0.000** | **0.000** | +0.125 | +0.325 | 0.442 → **1.869** |

*Note on the β-MnO₂ floor — it is a polymorph artifact, not instability.* On this axis
pyrolusite never reaches the Pourbaix hull because MP's PBE+U places other MnO₂ polymorphs
below it: `mp-644514` (C2/m) by 46 meV/atom on MP's standard thermo hull, and `mp-19395`
(I4/m) by **exactly the 29.75 meV/atom** measured as the ΔG_pbx floor on the aqueous-referenced
Pourbaix scale. The floor is therefore *entirely* polymorph-energy offset — β-MnO₂ minus
whichever MnO₂ solid MP thinks is lowest — and carries no information about aqueous
stability. That inversion is a **documented PBE+U failure for MnO₂ polymorph energetics that
SCAN repairs** (Kitchaev, Peng, Liu, Sun et al., *PRB* **93**, 045132, 2016,
[10.1103/PhysRevB.93.045132](https://doi.org/10.1103/PhysRevB.93.045132)); experimentally
pyrolusite is the stable ambient MnO₂ polymorph and a common ore mineral (Post, *PNAS* **96**,
3447, 1999, [10.1073/pnas.96.7.3447](https://doi.org/10.1073/pnas.96.7.3447)). **The
physically meaningful MnO₂ window is the experimental one in §3**, and the MP row above is
kept only for the cross-check below.

**Cross-check of the two axes on the same physical window** — the MnO₂(s) domain:

| pH | experimental ΔG_f (§3) | MP PBE+U | Δ lower | Δ upper |
|---|---|---|---|---|
| 0 | 1.407 → 1.583 | 1.401 → 1.586 | 6 mV | 4 mV |
| 7 | 0.993 → 1.445 | 1.004 → 1.448 | 11 mV | 4 mV |
| 13 | 0.974 → 1.327 | 1.004 → 1.330 | 31 mV | 4 mV |
| 14 | 0.974 → 1.270 | 1.004 → 1.274 | 31 mV | 5 mV |

Upper edges agree to ≤ 5 mV, lower edges to ≤ 31 mV. **This is not a fully independent
check** — MP's aqueous compatibility scheme is itself fitted to experimental formation
energies, and both axes use the same MnO₄⁻/MnO₄²⁻ ion data. What it does test is the solid
energetics and the wiring, and both pass.

**What each metal actually becomes at OER conditions** (MP Pourbaix-stable phase, 10⁻⁶ M).
This is legitimate for every element regardless of stage 1, and it is the quantitative form
of the docs/12 thesis that the active surface is a reconstructed (oxy)hydroxide:

| metal | pH 0, 1.23 V | pH 0, 1.53 V | pH 14, 1.23 V | pH 14, 1.53 V |
|---|---|---|---|---|
| Mn | Mn²⁺ | MnO₂(s) | MnO₂(s) | MnO₄⁻ |
| Cr | Cr³⁺ | HCrO₄⁻ | CrO₄²⁻ | CrO₄²⁻ |
| Fe | Fe³⁺ | Fe³⁺ | Fe₂O₃(s) | Fe₂O₃(s) |
| Co | Co²⁺ | Co²⁺ | CoO₂H⁻ | **CoOOH(s)** |
| Ni | Ni²⁺ | Ni²⁺ | Ni(OH)₃⁻ | Ni(OH)₃⁻ |
| Cu | Cu²⁺ | Cu²⁺ | CuO₂²⁻ *(aqueous ion)* | Cu₂O₃(s) |
| Ru | RuO₄(s) | RuO₄(s) | RuO₄(s) | RuO₄(s) |
| Ir | IrO₂(s) | IrO₂(s) | IrO₄²⁻ | IrO₄²⁻ |

Read carefully: `CuO₂²⁻` in that table is an **aqueous cuprate ion**, not the solid CuO₂ —
it is not evidence for a CuO₂ phase. Co does reconstruct to CoOOH(s) in alkali at operating
potential, exactly as docs/28 §3 asserted. Ni's stable alkaline species at 10⁻⁶ M is the
*soluble* Ni(OH)₃⁻ rather than a solid NiOOH; that assignment is concentration-sensitive and
is flagged rather than leaned on.

## 5. What was deliberately NOT computed, and why

The integrity rule is enforced in code, not just in prose
(`tests/test_pourbaix_r2.py::test_no_dg_pbx_is_produced_for_a_nonexistent_phase`):

| Phase | Produced? | Reason |
|---|---|---|
| rutile CoO₂ | **refused** | stage-1 verdict ABSENT. A ΔG_pbx here would be a number about a phase that does not exist. |
| rutile NiO₂ | **refused** | same |
| rutile CuO₂ | **refused** | same |
| rutile FeO₂ | reported **only** in a separately labelled block | MP has a PBE+U entry (`mp-850222`) for a hypothetical structure. Values (eV/atom, 10⁻⁶ M): +0.280 / +0.180 at pH 0 and +0.198 / +0.098 at pH 14, for 1.23 / 1.53 V vs RHE — **MP PBE+U, hypothetical structure, not an ambient phase.** Reported to show a magnitude, not as a property of a material. |

## 6. Corrections to docs/28 §3

1. **"CrO₂ — metastable (CVD-only; decomposes to Cr₂O₃)" — partly wrong, and wrong in a way
   that matters for how the SCF results are read.** Rutile CrO₂ is a real, ICSD-backed bulk
   material that was mass-produced as magnetic recording media (Chamberland, *Crit. Rev. Solid
   State Mater. Sci.* 1977, [10.1080/10408437708243431](https://doi.org/10.1080/10408437708243431);
   Coey & Venkatesan, *J. Appl. Phys.* **91**, 8345, 2002,
   [10.1063/1.1447879](https://doi.org/10.1063/1.1447879)), and MP's 0 K GGA+U hull calls it
   the **stable** ground-state CrO₂ polymorph (`mp-19177`, E_hull = 0, moment 2 μ_B/Cr — the
   FM half-metal). Its metastability is *thermal* (decomposition to Cr₂O₃ + O₂), which a 0 K
   hull cannot see; "CVD-only" is also too narrow. **The OER-relevant half of the claim
   survives and is now quantified**: soluble chromate at every pH, no aqueous window at
   10⁻⁶ M anywhere in 0 ≤ pH ≤ 14.
2. **"FeO₂ — pyrite-type, stable only >74 GPa": the 74 GPa figure is unsourced in docs/28 and
   is NOT verified here.** The right paper is Hu, Kim, Yang, Yang et al., *Nature* **534**,
   241, 2016 ([10.1038/nature18018](https://doi.org/10.1038/nature18018)), "FeO₂ and FeOOH
   under deep lower-mantle conditions" — a deep-lower-mantle, megabar-regime phase. Treat the
   specific threshold as unsourced until someone reads the paper. What *is* verified: MP holds
   **no Pa-3̄ (pyrite) FeO₂ entry at all**, its only rutile FeO₂ is theory-only at
   +0.145 eV/atom, and no FeO₂ polymorph is within 0.145 eV/atom of the Fe–O hull.
3. **"β-MnO₂ — dissolves in acid; workable neutral/alkaline" — inverted.** At 10⁻⁶ M the
   *acid* window is the one that contains the η = 0.30 V operating point (1.53 V ∈ [1.407,
   1.583]); the alkaline window closes 41 mV above the OER equilibrium and does not. The
   dominant β-MnO₂ loss channel under OER is **anodic** (→ MnO₄⁻/MnO₄²⁻) and it gets *worse*
   with pH; the acid problem is *cathodic* (→ Mn²⁺) and only bites below η = 0.18 V. Whether
   a real acid MnOₓ anode survives that slot is a kinetics question this calculation cannot
   answer — functionally stable acid MnOₓ anodes are reported (Huynh, Bediako & Nocera, *JACS*
   **136**, 6002, 2014, [10.1021/ja413147e](https://doi.org/10.1021/ja413147e); Huynh, Shi,
   Billinge & Nocera, *JACS* **137**, 14887, 2015,
   [10.1021/jacs.5b06382](https://doi.org/10.1021/jacs.5b06382)).
4. **"Five of six endmembers are not real electrodes": the count survives, the mechanism
   splits 4 : 1.** Four fail *phase existence* (FeO₂ hypothetical; CoO₂/NiO₂/CuO₂ absent);
   one (CrO₂) exists as a phase and fails *aqueous stability*. That distinction matters,
   because the two failures have different cures — nothing rescues a nonexistent polymorph,
   whereas a dissolving one can in principle be alloyed or protected.
5. **"CoO₂ reconstructs to CoOOH" — confirmed quantitatively.** MP's Pourbaix-stable Co
   phase at pH 14 / 1.53 V vs RHE is CoOOH(s). The analogous NiO₂ → NiOOH claim does **not**
   reproduce at 10⁻⁶ M: the stable Ni species there is soluble Ni(OH)₃⁻. Flagged, not fixed.

## 7. What this does and does not establish

**Does establish**

- Four of the six rutile MO₂ endmembers have no ambient bulk rutile polymorph, on MP evidence
  with material ids and ICSD provenance for every call.
- β-MnO₂'s aqueous window, in V vs RHE, at pH 0/7/13/14 at a stated ion concentration,
  validated to <0.2 mV against hand algebra on the same ΔG_f table and agreeing with the
  independent MP solid energetics to ≤ 31 mV.
- CrO₂ has no aqueous window at any pH at 10⁻⁶ M.
- The pipeline reproduces the IrO₂-vs-RuO₂ acid-stability contrast that the experimental
  literature reports — the first external validation of *any* tier of this project.

**Does not establish**

- **Bulk ≠ surface.** These are bulk-phase equilibria. At OER potentials the real cus row is
  O-covered and the surface has its own Pourbaix diagram (Hansen et al., *PCCP* 2008,
  [10.1039/b803956a](https://doi.org/10.1039/b803956a)). A bulk-unstable oxide can persist
  behind a passivating or self-healing surface; that is docs/28 §4 M4 and it is not done.
- **Thermodynamics, not rates.** ΔG_pbx > 0 says "will decompose if it can", never "will
  decompose fast". IrO₂ and RuO₂ both dissolve measurably during OER despite ΔG_pbx = 0 for
  IrO₂ in acid.
- **Concentration convention.** Everything is at 10⁻⁶ M. Windows widen with dissolved-ion
  concentration (~59 mV/decade per edge, opposite signs); a real electrolyte at 10⁻³ M gives
  β-MnO₂ ≈ 0.15 V more room at pH 0. Nothing here is a claim about a specific cell.
- **0 K, PBE+U, no entropy.** MP's hull has no T·ΔS, no configurational entropy and no
  pressure axis. CrO₂'s thermal metastability is invisible to it, and MnO₂'s polymorph
  ordering is demonstrably wrong in it.
- **No multi-element diagram.** Only single-element Pourbaix diagrams were built. The
  Fe–Ni–Co–Mn quaternary that an actual HEA needs (MultiEntry combinatorics, the expensive
  part) is **not** done; the per-element "what does this metal become" table above is a
  partial stand-in. That half of the R2 to-do stays open.
- **`theoretical`/ICSD flags are evidence, not proof.** They record whether MP matched a
  structure to ICSD. The four ICSD-tagged CuO₂ entries (`mp-1181499` Cmcm/icsd-15455,
  `mp-601195`, `mp-600604` Fmmm, `mp-705439` Pmmm) were **not** traced back to their ICSD
  records — they are most likely cuprate sub-lattices or peroxide/high-pressure assignments
  rather than bulk CuO₂, but that was not confirmed and no claim here rests on it.
- **One omission in the hand-entered table:** no Mn(III) oxyhydroxide (γ-MnOOH). Its tabulated
  ΔG_f varies by tens of kJ/mol across compilations, so it was left out rather than guessed.
  It would move the *lower* MnO₂ edge; the OER-relevant upper edge is set by the
  MnO₄⁻/MnO₄²⁻ couples and is untouched.

## 8. Consequence for the campaign

1. **The rutile tier is a calibration tier.** Every artifact that quotes η for Cr/Fe/Co/Ni/Cu
   must say so on the same page as the number. The defensible framing is docs/28 §6 item 4 —
   "why the pristine-slab descriptor breaks for the 3d rutiles" — with this gate as its
   evidentiary spine, not a screening result with a stability footnote.
2. **The R1 anchor spend gets *more* valuable, not less.** RuO₂ and IrO₂ are now the only two
   endmembers in the set that are simultaneously real, rutile and stable somewhere in the OER
   band. They are the only members for which η is a property of an electrode, and docs/30 §7
   already pre-registered the gate for them.
3. **Any future screening objective must be activity × ΔG_pbx**, per Tran et al., *Nanoscale*
   2024 ([10.1039/d4nr01390e](https://doi.org/10.1039/d4nr01390e)). `results/r2_stability.json`
   is the machine-readable input for that; it carries a `realisable_electrode` boolean per
   phase and refusal records for the phases that must never enter an objective function.
4. **Open, and cheap:** the Fe–Ni–Co–Mn multi-element Pourbaix diagram for candidate HEA
   oxide products. Still $0, still no box; just slower (MultiEntry generation).

## 9. Reproducing this

`results/` is gitignored, so the JSON is not in the repo; `docs/figs/pourbaix_mno2.{png,json}`
are. Everything regenerates from committed code:

| Command | Needs a key? | Produces |
|---|---|---|
| `pourbaix_r2.py selftest` | no | analytic Nernst validation of the hand-entered ΔG_f table |
| `pourbaix_r2.py window` | no | the §3 table |
| `pourbaix_r2.py figure` | no | `docs/figs/pourbaix_mno2.png` |
| `pourbaix_r2.py gate` | MP key (free) | the §2 table |
| `pourbaix_r2.py anchors` | MP key (free) | the §4 tables |
| `pourbaix_r2.py run` | MP key (free) | all of the above + `results/r2_stability.json` |

Every MP response is cached to `results/r2_mp_cache.json` after each element, so a dropped
connection costs one query and a second run needs no network at all. Two environment notes
worth recording: `pymatgen.analysis.pourbaix_diagram` ships **no** bundled thermodynamic data
(hence the offline hand-entered path), and mp-api 0.46 returns `potcar_spec` as pydantic
models while pymatgen 2026.4's `PotcarCorrection` still calls `.get()` on them — the MP
Pourbaix path is dead without the type shim in `_normalise_potcar_spec`.

## 10. Citation ledger (all DOIs resolved against Crossref, titles and authors verified)

Framework: Persson 2012 ([10.1103/PhysRevB.85.235438](https://doi.org/10.1103/PhysRevB.85.235438)) ·
Wang 2020 ([10.1038/s41524-020-00430-3](https://doi.org/10.1038/s41524-020-00430-3)) ·
Tran 2024 ([10.1039/d4nr01390e](https://doi.org/10.1039/d4nr01390e)).
Phases: Post 1999 MnO₂ minerals ([10.1073/pnas.96.7.3447](https://doi.org/10.1073/pnas.96.7.3447)) ·
Kitchaev 2016 MnO₂ polymorphs in DFT ([10.1103/PhysRevB.93.045132](https://doi.org/10.1103/PhysRevB.93.045132)) ·
Chamberland 1977 CrO₂ ([10.1080/10408437708243431](https://doi.org/10.1080/10408437708243431)) ·
Coey & Venkatesan 2002 CrO₂ half-metal ([10.1063/1.1447879](https://doi.org/10.1063/1.1447879)) ·
Amatucci 1996 CoO₂ ([10.1149/1.1836594](https://doi.org/10.1149/1.1836594)) ·
Hu 2016 FeO₂ ([10.1038/nature18018](https://doi.org/10.1038/nature18018)).
Electrochemistry: Cherevko 2014 ([10.1002/cctc.201402194](https://doi.org/10.1002/cctc.201402194)) ·
Cherevko 2016 ([10.1016/j.cattod.2015.08.014](https://doi.org/10.1016/j.cattod.2015.08.014)) ·
Huynh 2014 acid MnOₓ ([10.1021/ja413147e](https://doi.org/10.1021/ja413147e)) ·
Huynh 2015 ([10.1021/jacs.5b06382](https://doi.org/10.1021/jacs.5b06382)) ·
Hansen 2008 surface Pourbaix ([10.1039/b803956a](https://doi.org/10.1039/b803956a)) ·
Man 2011 volcano ([10.1002/cctc.201000397](https://doi.org/10.1002/cctc.201000397)) ·
Jones 2024 error bars ([10.1021/acs.chemrev.4c00171](https://doi.org/10.1021/acs.chemrev.4c00171)).
Thermochemistry: Wagman et al., NBS tables, *J. Phys. Chem. Ref. Data* **11** Suppl. 2 (1982)
— no DOI; cross-checked against Pourbaix, *Atlas of Electrochemical Equilibria in Aqueous
Solutions* (NACE, 1974).
Structures: MP material ids as cited inline (`mp-510408`, `mp-19177`, `mp-850222`, `mp-825`,
`mp-2723`, `mp-550206`, `mp-35925`, `mp-644514`), Materials Project, retrieved 2026-07-31.
