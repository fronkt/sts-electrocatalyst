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
| **Status (2026-06-26)** | ML round-1 screening **complete**; fabrication & electrochemistry **pending** (gated on lab logistics — §10). |
| **Mentorship / access** | Fort Wayne Metals (alloy fabrication + structural characterization); Purdue (electrochemistry). *Sponsor/mentor of record: TBD — see §10.* |

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
4. **ML-vs-experiment calibration as a first-class deliverable.** The Spearman ρ between
   predicted and measured rankings (with error bars), including its *failure modes*, is reported
   as a result — turning "the model was wrong" from an embarrassment into a publishable
   calibration finding.
5. **A methodological self-correction on record.** When the cheap heuristic prior was found
   *uncorrelated* with the real oxide ranking (ρ = −0.09), the candidate-selection step was
   redesigned from "rank by heuristic" to "**diversity-cover the single-phase composition
   space**," removing a hidden bias — documented as it happened (§5, [docs/14](14-compute-log.md)).
6. **(Optional Finalist axis)** composition-*and*-processing co-design — varying grain size at
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

## 6. Results to date (computational)

All three runs on 2026-06-26, RTX 5090, `uma-s-1p1`. Full tables/figures in
[docs/13](13-round1-uma-results.md), reproducible record in [docs/14](14-compute-log.md).

| Run | Surface | Pool | ρ(heuristic, UMA) | Headline |
|---|---|---|---|---|
| A | metal fcc(111) | top-24 by heuristic | **0.236** | over-binds; ranking only |
| B | rutile(110) multi-site | top-12 by heuristic | **−0.09** | descriptors at apex; η 0.78–1.5 V |
| C | rutile(110) multi-site | **diverse 30** (unbiased) | **0.155** | **confirms the headline on an unbiased pool** |

**Headline result:** **Fe₃₂Ni₁₇Co₃₄Mn₁₈** is the **#1 candidate**, robust across both the
heuristic-selected pool (run B) and the diversity-selected pool (run C) at the **identical**
best-site **η = 0.78 V**, with the **lowest site-spread in the top tier (η_std = 0.26)** — a
reliable prediction, not a lucky tail. It is **Cr-free** (no Cr(VI) hazard) and platinum-group-free.
The broader sweep also surfaced **Cr₆Fe₃₃Ni₂₇Mn₃₄** — single-phase, near-apex, and the **cheapest
($6.25/kg) and most abundant** composition in either pool — added as the low-cost/scalability pick.

The low ρ values are themselves a result: the cheap composition-weighted prior carries almost no
information about the real oxide ranking, so the UMA surface model is doing the actual work.

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
  *screening* estimate. *Mitigation:* relative ranking only; experimental calibration is the point.
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

**Independence (STS judges probe this hard).** Yours to defend: the hypothesis, the ML pipeline
design, the composition logic, the active-learning loop, the **hands-on melting/processing at FWM**,
the electrochemistry, the analysis and interpretation. Acknowledged access/supervision: FWM mentor +
facilities, Purdue lab/instruments. The dated git history of the code and these docs **is** the
independence evidence. *(Sponsor of record, mentor names, and the "whose idea" attribution: TBD — §10.)*

---

## 10. Provenance, reproducibility & open logistics

- **Code & data:** `src/hea_oer` (22 passing tests) + `src/scripts/run_round1_uma.py`; results under
  `results/`. All merged to `main` via PR #1 (metal pass) and PR #2 (oxide refinement + diverse sweep).
- **Reproduce:** environment and exact commands in [docs/14](14-compute-log.md) §1, §5.
- **Frozen predictions:** the round-1 ranking is committed/timestamped so the ML-vs-experiment
  correlation cannot be retrofitted ([docs/15](15-round1-melt-test-plan.md) §2).
- **Open gates before the wet-lab loop can start** ([tasks/todo.md](../tasks/todo.md)):
  Purdue potentiostat/EIS booking (the one must-book instrument); STS sponsor + independence
  attribution; DFT/first-principles experience level; 12th-grade eligibility confirmation.

> **Items marked TBD in this document** (entrant name confirmation, mentor/sponsor of record, DFT
> experience, instrument booking status, current fabrication stage) are the subject of the open
> questions accompanying this draft — they will be filled once answered.

---

### Change log
- **2026-06-26** — initial dossier created; reflects ML round-1 complete (metal proxy → rutile
  multi-site → broader diverse sweep), headline Fe₃₂Ni₁₇Co₃₄Mn₁₈, experiment pending.
