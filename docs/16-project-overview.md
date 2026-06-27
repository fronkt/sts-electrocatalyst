# 16 — Project Overview & Scientific Dossier

> **Master narrative** for the STS 2027 entry. Reads top-to-bottom for a non-specialist
> (judge, sponsor, reviewer): what problem it solves, the vocabulary, the novelty, and
> every step taken so far *with the reasoning behind it*. The lane analysis lives in
> [`docs/01`–`docs/11`](01-strategy-and-timeline.md); the execution spec in
> [`docs/12`](12-catalysis-hea-execution-plan.md); the compute record in
> [`docs/13`](13-round1-uma-results.md)/[`docs/14`](14-compute-log.md); the wet-lab
> protocol in [`docs/15`](15-round1-melt-test-plan.md). This document ties them together.

| | |
|---|---|
| **Working title** | *Machine-Learning-Guided Discovery of an Earth-Abundant High-Entropy-Alloy Oxygen-Evolution Electrocatalyst, Validated by Self-Fabrication and Calibrated Against Experiment* |
| **Entrant** | Frank Cai *(sole author; STS is an individual competition)* |
| **Competition** | Regeneron Science Talent Search 2027 — entry due ~Nov 5 2026 |
| **Status (2026-06-26)** | ML round-1 screening **complete**; **no alloy melted yet** — first melt expected **~early July 2026 (~1 week out)**; electrochemistry follows (gated on potentiostat booking — §10). |
| **Independence** | Project **conceived independently by the entrant** (hypothesis, ML pipeline, composition logic, AL loop); mentors/facilities provide access & supervision only. |
| **Mentorship / access** | Fort Wayne Metals (alloy fabrication + structural characterization); Purdue (electrochemistry). *Mentor/sponsor of record: TBD — see §10.* |

---

## 1. The problem, in plain language then precisely

**Plain language.** "Green" hydrogen is made by splitting water with electricity. The
hard half of that reaction — the one that wastes most of the energy — is the part that
pulls oxygen out of water (the **anode** reaction). Today's best fast catalysts for the
acidic version of it rely on **iridium**, one of the rarest metals on Earth (~$5,000/oz).
If clean hydrogen is going to scale to the terawatt level, we need an anode catalyst
made of *cheap, abundant* metals (iron, cobalt, nickel, manganese, …) that works *as
well as* the scarce-metal benchmark. That is an open, economically important problem.

**Precisely.** Water electrolysis is bottlenecked at the anode by the **oxygen evolution
reaction (OER)**:

> 2 H₂O → O₂ + 4 H⁺ + 4 e⁻   (acidic) ·  4 OH⁻ → O₂ + 2 H₂O + 4 e⁻ (alkaline)

It is a **4-electron** reaction proceeding through three bound intermediates — **\*OH,
\*O, \*OOH** (the `*` denotes a species adsorbed on the catalyst surface). The extra
voltage you must apply above the thermodynamic minimum (1.23 V) to drive it at a useful
rate is the **overpotential η** — the single number that defines a catalyst's quality.
Lower η = less wasted energy. State-of-the-art earth-abundant alkaline catalysts (e.g.
NiFe-LDH) sit around **η ≈ 250–300 mV at 10 mA cm⁻²**.

**Why it's hard — the scaling-relation floor.** On any ordered surface, the binding
strengths of \*OH and \*OOH are *not independent*: across essentially all materials they
obey a near-universal linear relation, **ΔG(\*OOH) ≈ ΔG(\*OH) + 3.2 eV** (±~0.2 eV). Because
you cannot tune the two intermediates separately, the best achievable overpotential is
pinned to a **volcano plot** with a hard thermodynamic floor of **η ≈ 0.37 V** at the
optimal binding (activity descriptor **ΔG(\*O) − ΔG(\*OH) ≈ 1.6 eV**). Breaking that floor —
"**scaling-relation circumvention**" — is the field's grand challenge.

---

## 2. Terminology (glossary)

| Term | Meaning in this project |
|---|---|
| **OER** | Oxygen Evolution Reaction; the rate-limiting anode half-reaction of water splitting. |
| **Overpotential η** | Extra voltage above 1.23 V needed to drive OER; primary metric, reported **at 10 mA cm⁻²**. Lower is better. |
| **\*OH / \*O / \*OOH** | The three adsorbed OER intermediates; their binding free energies set η. |
| **ΔG (adsorption free energy)** | Gibbs free energy to bind an intermediate, referenced to gas-phase H₂O/H₂. |
| **CHE (computational hydrogen electrode)** | Standard trick to reference proton-electron transfers to ½H₂ at a given potential, so each OER step's ΔG is computable from total energies. |
| **Theoretical overpotential** | η = max(ΔG₁…ΔG₄)/e − 1.23 V — the largest uphill step sets it. |
| **Activity descriptor** | ΔG(\*O) − ΔG(\*OH); the x-axis of the OER volcano; apex ≈ 1.6 eV. |
| **Scaling relation** | ΔG(\*OOH) ≈ ΔG(\*OH) + 3.2 eV; the constraint that creates the η ≈ 0.37 V floor. |
| **Volcano plot** | η vs descriptor; activity peaks ("apex") at intermediate binding, falls off on both legs. |
| **HEA (high-entropy alloy)** | A near-equimolar mix of ≥4–5 metals forming one solid-solution phase; here Fe–Co–Ni–Cr–Mn–Cu. |
| **Self-reconstruction** | Under anodic OER potential a 3d-metal alloy grows a catalytically active (oxy)hydroxide skin; the melted alloy is a **precursor**, the active phase is the in-situ oxide. |
| **Single-phase / formability** | Whether a composition solidifies as one solid-solution crystal (meltable, not brittle/segregated). |
| **VEC, δ, ΔH_mix, ΔS_mix, Ω** | Empirical HEA descriptors (valence-electron concentration, atomic-size mismatch, mixing enthalpy/entropy, the Ω = TΔS/\|ΔH\| stability ratio) used to predict single-phase formability. |
| **MLIP** | Machine-Learning Interatomic Potential — a neural network that predicts energies/forces ~10³–10⁶× faster than DFT. |
| **UMA** | Meta's *Universal Model for Atoms* (`uma-s-1p1`, via `fairchem`); the pretrained MLIP used here for adsorption energies. |
| **DFT** | Density Functional Theory — the first-principles quantum method MLIPs are trained to emulate. |
| **rutile(110)** | A specific oxide crystal facet (MO₂, the (110) surface) used as the model OER surface — the surface the universal scaling relation was originally established on. |
| **cus site** | "Coordinatively-unsaturated site" — the under-coordinated surface metal atom that actually binds the OER intermediates. |
| **Spearman ρ** | Rank-correlation coefficient; here it measures how well one ranking predicts another (ML-vs-ML now, ML-vs-experiment later). |
| **Active learning (AL)** | Iterative loop: model proposes candidates → measure them → retrain on the new data → propose better candidates. |
| **NiFe-LDH** | Nickel-iron layered double hydroxide; the accepted earth-abundant alkaline-OER benchmark to beat. |

---

## 3. The idea and the hypothesis

**The idea.** Where an *ordered* surface offers one kind of active site (and is therefore
locked onto the scaling relation), a **high-entropy alloy presents a near-continuous
distribution of multi-element active sites**. Different local arrangements of Fe/Co/Ni/Cr/Mn/Cu
around a surface metal atom bind \*OH and \*OOH by *different* amounts — so the *distribution*
of binding energies can partially **decouple** the \*OH/\*OOH scaling relation that caps ordered
surfaces. The favorable tail of that distribution can, in principle, sit closer to the volcano
apex than any single ordered material. Under OER conditions the alloy self-reconstructs into the
active oxide skin, so we screen the **oxide** surface, not the bare metal.

**Hypothesis (sharp, falsifiable — from [docs/12](12-catalysis-hea-execution-plan.md) §1):**

> An ML-selected, earth-abundant high-entropy composition in the **Fe–Co–Ni–(Cr/Mn/Cu)**
> space will, after electrochemical activation, exhibit an OER overpotential at 10 mA cm⁻²
> **within ±20 mV of, or below, a NiFe-LDH benchmark** measured under identical conditions,
> with **zero platinum-group metals**; *and* the ML-predicted activity ranking of the
> synthesized compositions will correlate with the measured ranking (**Spearman ρ reported
> with error bars**).

The second clause is the scientific heart: it makes the *model itself* a falsifiable object,
not just a candidate generator.

---

## 4. What is novel here (and, honestly, what is not)

**Novel / distinctive:**
1. **A fully closed design → fabricate → measure → calibrate loop that the entrant executes
   end-to-end** — including melting the alloys by hand at Fort Wayne Metals. Almost no STS
   computational-materials entry physically makes *and* measures its own ML-designed material;
   most stop at prediction.
2. **Active-site *distribution* modeling.** Instead of one adsorption energy per composition,
   the pipeline samples **multiple coordinatively-unsaturated (cus) sites** on the disordered
   oxide slab and aggregates the favorable tail — a direct computational encoding of the
   scaling-breaking hypothesis, not a single-site approximation.
3. **A universal MLIP (UMA) repurposed for high-throughput oxide-adsorption screening**, making
   it feasible to evaluate physically-grounded ΔG(\*OH/\*O/\*OOH) for thousands of disordered
   compositions on one GPU — a regime that is impractical with DFT.
4. **A multi-fidelity funnel (UMA → DFT → experiment), each tier calibrating the next.** The cheap
   universal screen is checked against **entrant-run Quantum ESPRESSO DFT** (UMA↔DFT parity, ρ + CI;
   [docs/22](22-multifidelity-dft-calibration.md)) *before* any metal is cut, and against measured η
   *after* — so the project reports **two** calibrations (computational and experimental), not a bare
   prediction. Most STS computational entries report one model and no first-principles cross-check.
5. **ML-vs-experiment calibration as a first-class deliverable.** The Spearman ρ between
   predicted and measured rankings (with error bars), including its *failure modes*, is reported
   as a result — turning "the model was wrong" from an embarrassment into a publishable
   calibration finding.
6. **A methodological self-correction on record.** When the cheap heuristic prior was found
   *uncorrelated* with the real oxide ranking (ρ = −0.09), the candidate-selection step was
   redesigned from "rank by heuristic" to "**diversity-cover the single-phase composition
   space**," removing a hidden bias — documented as it happened (§5, [docs/14](14-compute-log.md)).
7. **(Optional Finalist axis)** composition-*and*-processing co-design — varying grain size at
   fixed composition via cold-work/anneal — a lever ML-catalysis projects almost never have.

**Not novel (stated plainly, so the contribution is honest):** HEA electrocatalysis is an
active field; `fairchem`/UMA, `pymatgen`, and the CHE-OER formalism are established tools;
rutile(110) is a *model* surface, not the true layered oxyhydroxide. The contribution is the
**integrated, self-fabricated, experimentally-calibrated loop and its rigor**, not a new model
architecture or a new mechanism.

---

## 5. Every step taken so far — and why

### Step 0 — Lane selection (why HEA OER at all)
Across seven materials lanes ([docs/02](02-sts-materials-landscape.md), [docs/04`–`11]), the
recurring insight was that the entrant's *real* edge is **melting custom Fe-based alloys at
FWM**. The highest Finalist-reward/risk lane is the one that consumes that capability with a
**fast, quantitative** measurement inside a ~3.5-month window. OER overpotential vs NiFe-LDH is
exactly that: a single, well-defined number, measured on a benchtop potentiostat in hours.
HEA OER beat all-iron redox-flow batteries, rare-earth magnets, and thermal heat-spreaders on
that axis ([docs/06](06-project-shortlist.md), [docs/08](08-catalysis.md)).

### Step 1 — Composition enumeration + phase-stability gate *(cheap, CPU)*
**What:** sample thousands of compositions over Fe–Co–Ni–Cr–Mn–Cu; score each with the empirical
HEA formability rules (VEC, δ, ΔH_mix, ΔS_mix, Ω) and keep only those predicted **single-phase**.
Code: `hea_oer/phase_stability.py`, `composition.py`.
**Why:** a metallic precursor FWM can melt cleanly must be (near) single-phase; spending expensive
surface calculations on compositions that would solidify multi-phase or brittle is wasted compute.
This gate is **physics-based and kept throughout** — it was never the weak link.

### Step 2 — Surface model & the OER descriptor *(the core physics)*
**What:** build a surface slab, place \*OH/\*O/\*OOH, relax with an MLIP, and convert the energies
to the 4-step OER free-energy diagram via CHE referencing → theoretical η and the descriptor
ΔG(\*O) − ΔG(\*OH). Code: `descriptors.py` (η math), `referencing.py` (CHE), `relax.py`,
`adsorption.py` (backend).
**Why this evolved through three surface models** — each fixed a flaw in the last:

| Pass | Surface | Why tried | What it showed | Verdict |
|---|---|---|---|---|
| A | **metal fcc(111)** proxy | simplest; tests the whole pipeline end-to-end | over-binds O badly → descriptors −2…0 eV, η 2.7–4.9 V (**unphysical magnitude**) | ranking-only; not the real surface |
| — | rocksalt MO(100) | quick oxide sanity model (ASE) | geometry check only | superseded by rutile |
| B/C | **rutile MO₂(110), multi-site** | the surface the universal OER scaling was built on; supports cus-site **distribution** sampling | descriptors move onto the **volcano apex (~1.6 eV)**, η drops to **0.78–1.5 V** (physical) | **the model used** |

The jump from a single-site metal proxy to a **multi-cus-site oxide** is what makes the numbers
physical *and* encodes the HEA active-site-distribution hypothesis. Module:
`hea_oer/surfaces_rutile.py` (pymatgen is an *optional* dependency — only this module needs it).

### Step 3 — Adsorption energies from UMA *(expensive, GPU)*
**What:** for each pooled composition, build a rutile(110) HEA slab, find the cus sites, and relax
the clean slab + each adsorbate with Meta's **UMA** MLIP (`uma-s-1p1`, OC20 task, `fairchem-core`
2.21) on a Vast.ai **RTX 5090**; CHE-reference to gas-phase H₂O/H₂ → ΔG → η. ~4 relaxations × N sites
per composition. Full record: [docs/14](14-compute-log.md).
**Why UMA, not DFT:** DFT would cost ~GPU-days per composition; UMA gives a physically-grounded
energy in seconds, making a *distribution over sites over many compositions* tractable. Honest
caveat carried into the paper: UMA's OC20 head is metal-dominated, so oxide adsorption is partly
**out-of-distribution** — hence the model is a **screening prior, not an oracle** (§8).
**DFT calibration tier — the keystone of the multi-fidelity funnel (entrant-run):** the project
is not a single-model screen but a **funnel** — *UMA (screens thousands) → Quantum ESPRESSO DFT
(validates the top ~3–5 + reference oxides) → melt + measure (confirms the consensus)* — where
each tier cross-validates the one above. The entrant runs **Quantum ESPRESSO** (open; no VASP
license) personally on rented Vast.ai compute to recompute the top picks' best-site ΔG from first
principles, producing a **UMA↔DFT parity (Spearman ρ + CI) and a re-ranking** that (a) calibrates
the cheap screen with *the same method the OER scaling relations were built on*, and (b)
**DFT-blesses the melt list** so FWM receives the UMA↔DFT *consensus*, not UMA alone. Honest scope:
DFT re-ranks *within* the UMA-surfaced top tier — it validates/corrects the screen, it does not
independently search the space. Full protocol (PBE+U, U values, SSSP pseudos, cutoffs, k-points,
SQS construction, parity methodology, go/no-go) in **[docs/22](22-multifidelity-dft-calibration.md)**.
*(Full model spec, compute environment, relaxation/CHE protocol, validation, and every run's exact
parameters are in §6.)*

### Step 4 — Multi-objective ranking *(CPU)*
**What:** combine predicted activity (proximity to the volcano apex), single-phase formability, and
earth-abundance/cost into one ranked shortlist. Code: `objective.py`, `pipeline.py`.
**Why:** the deliverable is not "lowest η on paper" but "**meltable, cheap, and active**" — a
candidate the project can actually fabricate and defend as earth-abundant.

### Step 5 — The two-stage design and the bias it exposed *(the key methodological moment)*
**What:** because UMA is expensive, the pipeline runs in two stages — a cheap heuristic prior
pre-selects a small pool, then UMA evaluates only that pool. The first runs pre-filtered by the
heuristic **activity** score.
**The problem we caught:** the Spearman correlation between the heuristic ranking and the UMA-rutile
ranking was **ρ = −0.09** — i.e. **the cheap prior does not predict oxide activity at all**. So
pre-filtering the pool by that prior could easily *exclude* the best candidate (it would sit at
heuristic-rank 13+ and never be evaluated). This is a real threat to the result's validity.
**The fix (run C):** replace "rank by heuristic" with `--select diverse` — pick the pool by
**max-min diversity coverage** of the single-phase composition space (greedy farthest-point,
seeded by formability), *independent of* the heuristic activity score. Then re-run UMA on that
unbiased pool. Code: `_diverse_pick` in `src/scripts/run_round1_uma.py`.
**Why this matters for STS:** catching and correcting your own hidden bias — on the record, with the
correlation number that exposed it — is exactly the kind of rigor that distinguishes a Finalist
from a candidate-generator.

### Step 6 — Active-learning loop *(planned, after experiment)*
**What:** once measured η values return, condition a multi-objective surrogate on the real data and
propose round-2 compositions. Code stub: `hea_oer/active_learning.py` (`propose_round2`).
**Why:** the closed loop *with experimental feedback* — not a one-shot prediction — is the
methodological contribution. It is currently **blocked** until the first melts are measured.

---

## 6. Computational results — UMA & the three sweeps, in full

Self-contained: the model, the compute environment, the per-step protocol, the validation, and
every production run with its parameters and outputs. All work 2026-06-26. Underlying CSVs/figures:
[docs/13](13-round1-uma-results.md); dated lab-notebook record: [docs/14](14-compute-log.md).

### 6.1 Model & compute environment
| Component | Detail |
|---|---|
| Model | Meta **UMA** `uma-s-1p1` (Universal Model for Atoms), 1.2 GB checkpoint, task **OC20**; HF-gated `facebook/UMA` |
| Library | `fairchem-core` 2.21.0 (pure-PyTorch v2; the older OC22 PyG/torch-scatter stack won't build on Blackwell) |
| GPU / driver | Vast.ai **RTX 5090** (Blackwell, sm_120, 32 GB), driver 580, CUDA 13.0 |
| Torch | **2.8.0+cu128** (fairchem pins torch==2.8.0; install from the PyTorch CDN first, then fairchem) |
| Aux | `ase` 3.x · `pandas` 3.0.3 · `pymatgen` (rutile slabs only, optional dep) · Python 3.12.13 |

### 6.2 Adsorption → overpotential protocol
For each composition (and, for rutile, each cus site):
1. **Slab** — build the surface supercell, decorate the metal sublattice with the composition
   (seeded RNG for reproducibility). Sizes: metal fcc(111) `(3,3,4)`; rocksalt(100) `(2,2,4)`;
   **rutile(110) `(2,2,1)` → 72 atoms, O:M = 2.00 verified**.
2. **Relax** the clean slab and each of `*OH / *O / *OOH` with UMA via ASE, **fmax = 0.05 eV/Å,
   ≤ 300 steps**.
3. **CHE-reference** the energies to gas-phase H₂O/H₂ (computational hydrogen electrode) → the three
   ΔG → the 4-step OER diagram → **η = max(ΔG₁…₄) − 1.23 V** and descriptor ΔG(\*O) − ΔG(\*OH).
   Code: `referencing.py`, `descriptors.py`.
4. **Rutile multi-site** — cus sites are located on the **pristine** slab (ideal 5-coordination;
   finding them on the *relaxed* slab miscounts), **4 sites/composition**, each a distinct local
   cation environment. η is taken at the **favorable-tail (best) cus site**; the full per-site
   distribution (η_min/mean/std/max) is recorded. Code: `surfaces_rutile.py`,
   `_predict_rutile_multisite` in `adsorption.py`.

### 6.3 Validation (all passed, before the production runs)
| Check | What | Result |
|---|---|---|
| Plumbing (CPU, EMT) | Ni₅₀Cu₅₀ slab→relax→ref→ΔG→η | OK, 0.6 s |
| First real UMA (metal) | CoCrFeMnNi fcc(111) | ΔG −0.52/−0.82/−0.95, desc −0.29, η 4.64 V, 188 s (incl. 1.2 GB download) |
| Rocksalt(100) geometry | ASE bulk MgO-type | 128 atoms, cus metal 5-coord ✓ |
| Rutile(110) geometry | pymatgen SlabGenerator | 72 atoms, **O:M = 2.00**, cus 5-coord, 4 sites ✓ |
| Rutile multisite smoke | CoCrFeMnNi, 4 sites | descriptor **−0.29 (metal) → +2.02 (rutile)**, best-site η 1.95 V, 116 s |

The descriptor jump **−0.29 → +2.02 eV** on the *same composition* when moving from the metal proxy
to the rutile oxide is the clearest single demonstration that the **surface model**, not composition
alone, controls the predicted activity.

### 6.4 The three production runs

**Run A — metal fcc(111) proxy.** `--backend uma --pool 24 --top-k 4`
- Stage 1: 3000 sampled → **2470 single-phase** → top 24 by heuristic score.
- Stage 2: UMA fcc(111), 24 candidates, **833 s** (~35 s each).
- **ρ(heuristic, UMA) = 0.236.** Shortlist Fe₃₅Mn₁₅Ni₁₈Co₃₂ (η 2.78) / Mn₂₄Fe₂₄Ni₂₅Co₁₇Cu₉ (2.70) /
  Mn₁₆Co₂₂Ni₃₃Fe₂₈ (3.17) / Cr₁₉Co₂₁Fe₂₇Ni₃₃ (3.32).
- **Verdict:** the bare metal over-binds O → descriptors −2…0 eV, **η 2.7–4.9 V (unphysical magnitude)**;
  ranking-information only. This motivated the oxide model.

**Run B — rutile(110) multi-site, heuristic pool.** `--surface rutile --n-sites 4 --pool 12 --top-k 4`
- Stage 1: same prior → top **12** single-phase. Stage 2: rutile(110), 4 cus sites/comp, **1899 s**
  (GPU shared with a batterycv job).
- **ρ(heuristic, rutile) = −0.09** — the prior is *uncorrelated* with the oxide ranking. Descriptors
  cluster at the volcano apex; best-site **η 0.78–1.5 V (physical)**.
- Shortlist: **Fe₃₂Ni₁₇Co₃₄Mn₁₈** (η 0.78, desc 1.75) / Cr₂₁Ni₂₄Co₁₅Cu₆Fe₃₃ (1.03) /
  Cr₈Fe₃₄Mn₉Ni₂₃Co₂₇ (1.15) / Co₂₄Fe₂₄Ni₃₅Mn₁₇ (1.15).
- **The ρ = −0.09 is the problem that triggered run C** (§5 Step 5): if the prior can't predict oxide
  activity, pre-filtering the pool by it can silently hide the best candidate.

**Run C — broader *diverse* sweep (the unbiased pool).**
`--surface rutile --n-sites 4 --pool 30 --select diverse --top-k 6 --n-samples 4000`
- **Pool selection (the fix):** `_diverse_pick` — sort single-phase candidates by formability, seed
  with the most formable, then **greedily add the composition farthest (max-min Euclidean distance in
  composition-vector space) from those already chosen**. Covers Cu-/Mn-rich regions the heuristic
  top-12 never reached, *independent of* the activity prior.
- Stage 1: 4000 sampled → **3304 single-phase** → diverse 30. Stage 2: **5795 s**.
- **ρ(heuristic, rutile) = 0.155** (still low — re-confirmed on a 2.5× larger pool).
- **Fe₃₂Ni₁₇Co₃₄Mn₁₈ remains #1** at the *identical* η_best **0.782 V** with the **lowest top-tier
  site spread (η_std 0.26)**.

### 6.5 Full ranked single-phase results (run C)
Top single-phase **FCC** candidates (the meltable set). Two compositions had a lower η_best but are
predicted **FCC+BCC dual-phase** (won't melt single-phase) with unreliable site variance → excluded:

| Rank | Composition (at.%) | η_best (V) | descriptor (eV) | η_std (V) | phase | $/kg |
|---|---|---|---|---|---|---|
| 1 | **Fe₃₂Ni₁₇Co₃₄Mn₁₈** | 0.782 | 1.753 | 0.263 | FCC | 14.5 |
| 3 | **Cr₆Fe₃₃Ni₂₇Mn₃₄** | 1.065 | 2.295 | 0.922 | FCC | **6.25** |
| 4 | Mn₁₉Fe₁₂Ni₃₅Co₁₆Cr₁₈ | 0.930 | 1.847 | **0.151** | FCC | 13.8 |
| 7 | Cu₁₂Mn₃₃Co₃₅Fe₂₁ | 0.921 | 1.925 | 0.489 | FCC | 13.2 |
| 8 | Co₂₀Ni₂₀Cr₂₀Mn₂₀Cu₂₀ | 0.882 | 1.636 | 0.739 | FCC | 14.3 |
| 9 | Cu₁₁Ni₃₄Cr₆Fe₂₀Co₂₉ | 1.094 | 1.833 | 0.203 | FCC | 17.4 |
| *excl.* | *Ni₁₁Cr₂₄Mn₁₈Co₂₉Fe₁₈* | *0.772* | 1.815 | 0.601 | **FCC+BCC** | — |
| *excl.* | *Cu₈Cr₂₃Mn₃₅Co₃₄* | *0.768* | 1.947 | **3.242** | **FCC+BCC** | — |
| 30 | Co₂₀Mn₈Ni₁₈Fe₂₆Cu₂₈ | 3.590 | 1.690 | 0.982 | FCC | (worst — natural poor anchor) |

Full 30-row table incl. ΔG(\*OH/\*O/\*OOH): [`results/round1_uma_rutile_sweep_candidates.csv`](../results/round1_uma_rutile_sweep_candidates.csv);
volcano [`…_sweep_volcano.png`](../results/round1_uma_rutile_sweep_volcano.png). Runs A/B outputs:
`results/round1_uma_candidates.csv`, `…_rutile_candidates.csv`.

### 6.6 What the numbers mean
- **The headline is robust.** Fe₃₂Ni₁₇Co₃₄Mn₁₈ wins on *both* a heuristic-selected (B) and an
  unbiased diverse (C) pool, at the same η and with the tightest site distribution — Cr-free and
  Pt-group-free.
- **The favorable cus site beats the surface average** (η_best 0.78 vs η_mean 1.18 on the headline) —
  direct support for the HEA active-site-*distribution* hypothesis (§3).
- **The low ρ is itself a result:** the cheap composition-weighted prior carries almost no information
  about the real oxide ranking, so the UMA surface model is doing the actual work — and the surface
  choice reshuffles the ranking (the rutile #1 was metal-surface *rank 18*).
- **A built-in poor anchor exists** (Co₂₀Mn₈Ni₁₈Fe₂₆Cu₂₈, η 3.59) giving the eventual
  ML-vs-experiment correlation real dynamic range without melting anything exotic.

---

## 7. The experimental plan (make → measure → correlate)

Detailed protocol in [docs/15](15-round1-melt-test-plan.md). In brief:

1. **Melt** the locked round-1 set at FWM — 4 predicted-good single-phase HEAs (Fe₃₂Ni₁₇Co₃₄Mn₁₈,
   Cr₆Fe₃₃Ni₂₇Mn₃₄, Mn₁₉Fe₁₂Ni₃₅Co₁₆Cr₁₈, Co₂₀Ni₂₀Cr₂₀Mn₂₀Cu₂₀) + a **predicted-poor anchor**
   (Cr₁₉Co₂₈Fe₂₅Ni₂₈) and a **ternary ablation** (FeCoNi). Arc-melt, anneal, verify single-phase by
   on-site XRD/SEM-EDS *before* traveling.
2. **Measure** OER at Purdue: 3-electrode, 1 M KOH, η@10 mA cm⁻² (iR-corrected), Tafel slope, ECSA,
   EIS, ≥12 h stability, post-mortem reconstruction evidence — in triplicate, vs NiFe-LDH + bare GC.
3. **Correlate** the *frozen* predicted ranking against measured η: report **Spearman ρ and Pearson r
   with error bars**. The predicted-poor anchor gives the correlation statistical range. Three honest
   outcomes (high ρ = model guided discovery; low ρ but a candidate beats baseline = useful catalyst +
   calibration lesson; low ρ and none beat baseline = rigorous negative result) are **all publishable**.

---

## 8. Limitations & threats to validity (carried into the paper)

- **OC20 is metal-dominated** → oxide adsorption is partly out-of-distribution for UMA; η is a
  *screening* estimate. *Mitigation:* relative ranking only; the **entrant-run Quantum ESPRESSO DFT
  calibration tier** ([docs/22](22-multifidelity-dft-calibration.md)) bounds the MLIP error on these
  exact surfaces (UMA↔DFT parity, ρ + CI) *before* the melt; experimental calibration follows.
- **Non-ground-state rutiles.** FeO₂/CoO₂/NiO₂/CuO₂ lattice entries are model values on the rutile
  trend, not experimental ground states.
- **Model surface ≠ real active phase.** rutile(110) approximates, but is not, the true in-situ
  layered oxyhydroxide. *Optional refinement:* explicit NiOOH/FeOOH terminations.
- **Reconstruction, short-range order, and segregation** mean the as-melted composition ≠ the active
  surface composition; SEM-EDS + post-mortem analysis bound this experimentally.
- **Finite site sampling** (4 cus sites) under-samples the true HEA site distribution; larger
  supercells are a future refinement.
- **The heuristic-prefilter bias** (now mitigated by diverse selection) — disclosed, not hidden.

---

## 9. STS positioning

| Tier | What it takes | Where we are |
|---|---|---|
| **Scholar floor** | a working ML→fabricate→measure pipeline; ≥3 HEAs made & benchmarked vs NiFe-LDH with clean triplicate data + honest ML-vs-experiment ρ — *even if none beat the baseline* | ML pipeline + shortlist **done**; fabrication/measurement pending |
| **Finalist stretch** | ≥1 ML-designed composition **matches/beats** NiFe-LDH on η@10, survives ≥12 h, with post-mortem reconstruction evidence, AND the ML ranking demonstrably guided the discovery | contingent on the wet-lab loop |

**Independence (STS judges probe this hard).** The project was **conceived independently by the
entrant** — the OER/HEA hypothesis, the ML pipeline design, the composition logic, and the
active-learning loop are the entrant's own, not a slice of a mentor's grant. Yours to defend: all of
the above plus the **hands-on melting/processing at FWM**, the **entrant-run DFT validation**, the
electrochemistry, and the analysis/interpretation. Acknowledged access/supervision only: FWM mentor +
facilities, Purdue lab/instruments. The dated git history of the code and these docs **is** the
independence evidence. **Nuance to address head-on in the application:** the entrant is also a *paid
assistant researcher*, so the write-up should make explicit that this STS project — its hypothesis,
pipeline, and analysis — is the entrant's **own initiative, distinct from any assigned employer
work**, and that the consumables/compute were self-funded. *(Mentor/sponsor names of record: TBD — §10.)*

---

## 10. Provenance, reproducibility & open logistics

- **Code & data:** `src/hea_oer` (22 passing tests) + `src/scripts/run_round1_uma.py`; results under
  `results/`. All merged to `main` via PR #1 (metal pass) and PR #2 (oxide refinement + diverse sweep).
- **Reproduce:** environment and exact commands in [docs/14](14-compute-log.md) §1, §5.
- **Frozen predictions:** the round-1 ranking is committed/timestamped so the ML-vs-experiment
  correlation cannot be retrofitted ([docs/15](15-round1-melt-test-plan.md) §2).
- **Resolved (2026-06-26 grilling):** first-principles capability — *entrant runs DFT (Quantum
  ESPRESSO, no VASP license) personally* → promoted to the **multi-fidelity DFT calibration tier**
  ([docs/22](22-multifidelity-dft-calibration.md)); idea origin — *entirely the entrant's own*;
  fabrication stage — *pre-melt, nothing cast yet*.
- **Live critical-path gate:** Purdue potentiostat/EIS access is **expected but not yet booked** —
  this is now the single most schedule-sensitive action; book recurring slots before the first melt
  so the make→measure loop never stalls on instrument time.
- **Self-funded** (2026-06-26): consumables, compute, and Purdue travel are paid by the entrant —
  clean for the independence story (no grant strings).
- **First melt imminent (~early July 2026, ~1 week out)** → the round-1 melt set ([docs/15](15-round1-melt-test-plan.md))
  should be weigh-sheet-ready (target at.% → feedstock masses, Mn over-charge) before the melt.
- **Eligibility — CONFIRMED (2026-06-26):** entrant is a **high-school senior graduating spring
  2027** → STS-eligible. Application note: the entrant is *also* a **paid, employed assistant
  researcher**, so the independence / "work-for-hire" question (the entrant's own project vs. assigned
  employer work?) must be **addressed explicitly** — mitigated by the hypothesis, ML pipeline, and
  analysis being the entrant's own (§9) and by self-funding the consumables/compute.
- **STS sponsor of record: not yet identified** — STS requires an adult sponsor who signs; this is an
  open action item. Mentor names (FWM, Purdue) for acknowledgments also TBD.

> The TBD items above will be filled as answered; the change log records each update.

---

### Change log
- **2026-06-26** — initial dossier created; reflects ML round-1 complete (metal proxy → rutile
  multi-site → broader diverse sweep), headline Fe₃₂Ni₁₇Co₃₄Mn₁₈, experiment pending.
- **2026-06-26 (rev.)** — folded in entrant answers: entrant runs DFT (added DFT cross-check to
  methods/limitations); project conceived independently (strengthened §9); potentiostat expected
  but unbooked (flagged as live critical-path gate); pre-melt status made explicit. Remaining TBDs
  narrowed to eligibility, mentor/sponsor names, and funding.
- **2026-06-26 (rev. 2)** — self-funded; first melt ~early July 2026 (~1 week out); STS sponsor of
  record not yet identified. Added an **eligibility flag**: entrant is a paid employed assistant
  researcher — must confirm HS-senior (spring-2027 graduation) standing before committing to STS, and
  handle the paid-employment independence question explicitly.
- **2026-06-26 (rev. 3)** — **eligibility confirmed**: entrant is a HS senior graduating spring 2027
  (STS-eligible). Paid-employment independence nuance retained as an explicit application to-do (§9).
- **2026-06-26 (rev. 4)** — **§6 expanded to be self-contained**: UMA model + compute environment,
  the adsorption→η protocol, the validation suite, all three production runs (A/B/C) with full
  parameters, the diverse-selection algorithm, and the full ranked single-phase results table —
  folded in from docs/13–14 so the dossier stands alone.
- **2026-06-27 (rev. 5)** — **DFT promoted from spot-check to the keystone of a multi-fidelity
  funnel** (UMA → Quantum ESPRESSO → experiment). Engine locked to **Quantum ESPRESSO** (no VASP
  license); added a new novelty point (two calibrations, computational + experimental); new protocol
  doc **[docs/22](22-multifidelity-dft-calibration.md)** + a Phase-1.5 DFT-calibration phase in the
  tracker; melt list redefined as the **UMA↔DFT consensus**. Decided with the entrant to *combine*
  the screen and the (formerly fallback) DFT-validation engine into one project rather than two.
