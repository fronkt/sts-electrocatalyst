# 20 — Deep-research brief: the best-bet computational fallback

Phase-1/2 deep-research output (2026-06-26) converging the [docs/19](19-computational-fallback.md)
fallback to a **single best bet**, scoped to the entrant's answers: *compute-only fallback, solo,
finishable by Oct 2026, optimize for STS placement, big-compute/train-from-scratch acceptable,
domain = whatever places best, validation either route, "I can validate quickly."*

## The best bet (one sentence)
**A conditional generative model that proposes *new* earth-abundant, platinum-group-free catalysts
for the hydrogen evolution reaction (HER), screened by a universal MLIP and validated by the
entrant's own DFT — benchmarked against an experimental dataset (OCx24) and against known top
catalysts as a positive control.**

### Research question (precise)
> Can a structure+composition generative model, conditioned on near-optimal hydrogen adsorption
> (ΔG_H\* ≈ 0), single-phase stability, and earth-abundance, **discover novel Pt-free HER catalysts**
> that (a) DFT confirms at the volcano apex, (b) rank-correlate with the experimental **OCx24** HER
> measurements, and (c) reproduce known top HER catalysts as a positive control?

### Why HER (not OER / CO₂RR / ORR) — this is the key scoping decision
- **Single descriptor ΔG_H\*** (Nørskov volcano, apex at ΔG_H\* ≈ 0). One adsorption energy per
  candidate → **the fastest, cleanest DFT validation of any catalytic reaction** — directly serves
  the entrant's "I can validate it quickly after." OER needs three intermediates + the 4-step diagram;
  CO₂RR/N²RR add product-selectivity overhead.
- **An experimental benchmark already exists** — OCx24 measured HER voltages across many compositions
  → the project can claim *"predictions validated against experiment"* **without a wet lab**.
- **Maximal reuse:** the existing UMA/fairchem adsorption pipeline transfers with a *one-adsorbate
  swap* (\*OH/\*O/\*OOH → \*H); the phase-stability gate and CHE referencing are unchanged.
- **Strong, generalist-legible "so what":** green hydrogen, Pt-group-free, supply chain.

### Why discovery-first, NOT method-first (the placement-critical call)
The generative-catalyst-design *method* lane is **already crowded by professionals** — MatterGen
(diffusion), CrystalFlow (flow-matching), Catalyst GFlowNet (HER), and a 2025 *Nature Synthesis*
HEA-generative paper. A solo entrant **will not beat SOTA method** in 3.5 months, so a "new
architecture" framing is a **placement trap** (it invites "why is this better than MatterGen?").
The placed STS computational pattern (ScGAN '23) is **method-applied → discovery → validation**.
So the contribution is the **validated discovery + the experimental benchmark**, with the generator
as the *vehicle*, not the headline.

## Prior art & exactly how this differs (novelty positioning)
| Prior work | What it did | The gap this project fills |
|---|---|---|
| **Catalyst GFlowNet** (arXiv 2510.02142) | GFlowNet over OC20/22 + FAENet descriptors for HER; DFT-checked | Authors report **no breakthrough novel catalysts**, flag **structural-stability uncertainty** & **no experimental validation** → this project delivers **concrete DFT-validated novel candidates**, uses **UMA full relaxations + a phase-stability gate** (addresses their stability gap), and **benchmarks against OCx24 experiment** |
| **MatterGen** (diffusion, general) | Stable inorganic generation, fine-tunable | Not catalysis-specific; here it's a **de-risk fallback backbone** to fine-tune if from-scratch underperforms |
| **CrystalFlow** (arXiv 2412.11693) | Flow-matching crystal generation | Matches the entrant's flow-matching skillset; reused as the **generator architecture**, conditioned on catalytic + abundance targets |
| **Nature Synthesis 2025** — generative HEA catalysts | Spectroscopic-descriptor generative design, −32 mV | Professional, experiment-heavy; this project's edge is the **MLIP+DFT validation loop + the abundance/Pt-free framing at the HER single-descriptor**, executable solo |

**Novelty at the STS level is high:** no STS/ISEF generative-catalyst-*discovery* project surfaced;
the contribution is a **calibrated, DFT-and-experiment-validated generative discovery of Pt-free HER
catalysts** — distinct from the professional method papers by being *discovery- and validation-led*.

## Methodology blueprint
- **Data:** OC20/OC22 (\*H adsorption energies) · Materials Project / OQMD / Alexandria (structures +
  formation energy/stability) · **OCx24** (experimental HER, the benchmark).
- **Generator (the compute flex):** conditional **flow-matching** over composition+structure
  (entrant's [[project_symmc_flow]] skillset), conditioned on ΔG_H\* ≈ 0 + stability + abundance/cost.
  *De-risk:* if from-scratch training underperforms by a hard cutoff, **fine-tune MatterGen** instead.
- **Screen / evaluator:** **UMA** (`uma-s-1p1`) relaxation + \*H → ΔG_H\* (reuse the HEA pipeline,
  swap adsorbate) + the single-phase/synthesizability gate.
- **Validation (multi-pronged → this is the placement engine):**
  1. **Positive control** — pipeline must rank known top HER catalysts (Pt, MoS₂-edge, Ni₂P) correctly.
  2. **DFT (entrant-run VASP/QE)** on the top novel candidates → confirm ΔG_H\* at the apex.
  3. **Experimental benchmark** — predicted activity vs **OCx24** measured HER, Spearman ρ (no lab).
  4. *(Optional, Scholar→Finalist)* one collaborator-measured sample if any EC access materializes.
- **Baselines to beat:** random search, the composition-heuristic prior, and a published ΔG_H\*
  descriptor/volcano baseline.
- **Metrics:** DFT-confirmed hit-rate (|ΔG_H\*| < 0.1 eV), novelty fraction vs known catalysts,
  generated-structure validity/stability rate, ρ vs OCx24, and cost/abundance of the hits.

## Predicted STS placement & risks (devil's-advocate checkpoint)
- **Predicted placement: Finalist-credible** *iff* it ships ≥1–2 **DFT-validated novel** candidates
  **and** the **OCx24 experimental benchmark** lands (that benchmark is what separates this from the
  Hirshorn/Scholar tier — it is "validated against experiment" without a lab).
- **Risks & mitigations:**
  - *Crowded method lane* → **frame as discovery, never as "a new model."**
  - *From-scratch generator may not converge in time* → **MatterGen fine-tune fallback + hard cutoff.**
  - *UMA out-of-distribution on novel chemistries* → **DFT bounds it; report the error.**
  - *"Is it novel vs Catalyst GFlowNet?"* → **validated novel discoveries + UMA relaxation + OCx24
    benchmark** are exactly its stated gaps.
  - *Pure-compute Scholar ceiling* → keep the **optional experimental anchor** open.
- **Timeline:** fits Jul→early-Oct — reuses the HEA infrastructure; the only net-new heavy item is the
  generator (boxed to a few GPU-weeks with the fine-tune fallback).

## Why this is the best bet specifically
It is the **only** option that simultaneously: optimizes placement (discovery + experiment-validated,
the placed pattern), honors the big-compute appetite (a trained generator), **validates fast**
(single HER descriptor), **reuses ~all** the HEA work (one-adsorbate swap), and **degrades
gracefully** (underperforming generator still yields a validated screening result; and if the main
HEA experiment proceeds, this generator becomes its round-2 proposer). Net wasted work ≈ 0.

## Limitations of this brief
Scoped by a rapid literature pass (sources below), not a systematic review; dataset access (OCx24
licensing, Alexandria size) to be confirmed; the from-scratch-vs-fine-tune decision should be settled
by a one-week training pilot before committing. *AI-assisted research tools were used to compile this
brief; all cited works are real and listed below for independent verification.*

### Sources
- Catalyst GFlowNet (HER): <https://arxiv.org/pdf/2510.02142>
- Open Catalyst Experiments 2024 (OCx24): <https://arxiv.org/pdf/2411.11783>
- CrystalFlow (flow-matching crystals): <https://arxiv.org/pdf/2412.11693>
- MatterGen / generative crystal review: <https://www.nature.com/articles/s41524-025-01881-2>
- Generative AI for high-entropy catalysts (Nature Synthesis 2025): <https://www.nature.com/articles/s44160-025-00983-5>
- HER descriptor / alkaline HER review: <https://www.mdpi.com/2073-4344/14/9/608> · <https://www.sciencedirect.com/science/article/pii/S0378775324008085>
- Symmetry-assured generation for water-splitting photocatalysts: <https://arxiv.org/pdf/2507.19307>
