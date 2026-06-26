# `hea_oer` — ML round-1 selector for HEA OER electrocatalysts

Implements the pipeline in [`../docs/12-catalysis-hea-execution-plan.md`](../docs/12-catalysis-hea-execution-plan.md) §3:
**enumerate compositions → empirical phase-stability filter → adsorption-energy
descriptor → OER theoretical overpotential → multi-objective ranking → shortlist
to melt**, plus a round-2 active-learning scaffold.

## Quick start (CPU, no install)

```bash
cd STS2027
python -m pytest -q                                   # run the test suite
PYTHONPATH=src python src/scripts/run_round1.py --top-k 4 --seed 0
```

Outputs: a ranked table + diverse shortlist printed to stdout,
`results/round1_candidates.csv`, and `results/round1_volcano.png`
(η vs. the ΔG_O−ΔG_OH descriptor, with the scaling-limit volcano).

## Modules

| File | Role |
|---|---|
| `hea_oer/data.py` | Curated, cited element tables (radii, VEC, Miedema ΔH, abundance, oxophilicity) |
| `hea_oer/composition.py` | `Composition` + HEA simplex sampling (4–5 elements, 5–35 at.%) |
| `hea_oer/phase_stability.py` | VEC, δ, ΔS_mix, Miedema ΔH_mix, Ω → single-solid-solution score |
| `hea_oer/descriptors.py` | OER 4-step thermodynamics → theoretical overpotential η |
| `hea_oer/adsorption.py` | `HeuristicBackend` (CPU placeholder) · `FairchemSurfaceBackend` (real, GPU) |
| `hea_oer/surfaces.py` | fcc(111) HEA slab build + *OH/*O/*OOH adsorbate placement (ASE) |
| `hea_oer/referencing.py` | CHE ΔG referencing (H2O/H2 + ZPE−TΔS corrections) |
| `hea_oer/relax.py` | ASE BFGS relaxation + fairchem UMA calculator factory |
| `hea_oer/objective.py` | Multi-objective table, Pareto front, diverse top-k selection |
| `hea_oer/pipeline.py` | `run_round1(...)` orchestrator |
| `hea_oer/active_learning.py` | Round-2 GP + expected-improvement scaffold |

## ⚠️ Honesty: the default backend is a placeholder

`HeuristicBackend` is **not DFT**. It maps a composition-weighted oxophilicity
proxy to ΔG(\*OH), applies the universal \*OOH/\*OH scaling, and lets
compositional disorder nudge the activity descriptor toward the volcano apex — a
transparent prior for *ranking only*. Every output row carries `backend="heuristic"`.
Do not report these as physical adsorption energies.

## Real backend: fairchem UMA on a GPU (Vast.ai)

`FairchemSurfaceBackend` (`--backend uma`) computes CHE-referenced *OH/*O/*OOH
adsorption ΔG on an fcc(111) HEA slab using a fairchem universal model (UMA, OC20
task). Surface + referencing live in `surfaces.py` / `referencing.py`; energies
come from `relax.py`.

On the GPU box:
1. `uv pip install fairchem-core` (torch ships with the PyTorch image).
2. Accept the UMA license at hf.co/facebook/UMA, then `huggingface-cli login`
   (UMA is **gated** — access is granted by review, not instantly).
3. Validate plumbing without the model (CPU): `python src/scripts/smoke_uma.py --calc emt`
   — EMT stand-in on Ni50Cu50; exercises slab → relax → reference → ΔG → η end to end.
4. Real single composition: `python src/scripts/smoke_uma.py --model uma-s-1p1`.
5. Re-rank with real energies on the **shortlist** (not 4000 — each composition is
   ~6 relaxations): `run_round1.py --backend uma --n-samples 200 --top-k 4`.

**Caveat:** the surface is a *metal* fcc(111) proxy; the true OER-active phase is
the reconstructed (oxy)hydroxide. A rutile-oxide (110) surface is the future refinement.

## Round-2 (after measuring round-1 alloys)

Feed measured overpotentials into `active_learning.propose_round2(...)` to pick the
next compositions to melt. Swap the scikit-learn GP for BoTorch `qNEHVI` for true
multi-objective acquisition (`pip install botorch ax-platform`).
