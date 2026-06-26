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
| `hea_oer/adsorption.py` | `HeuristicBackend` (CPU placeholder) · `OC22FairchemBackend` (GPU stub) |
| `hea_oer/objective.py` | Multi-objective table, Pareto front, diverse top-k selection |
| `hea_oer/pipeline.py` | `run_round1(...)` orchestrator |
| `hea_oer/active_learning.py` | Round-2 GP + expected-improvement scaffold |

## ⚠️ Honesty: the default backend is a placeholder

`HeuristicBackend` is **not DFT**. It maps a composition-weighted oxophilicity
proxy to ΔG(\*OH), applies the universal \*OOH/\*OH scaling, and lets
compositional disorder nudge the activity descriptor toward the volcano apex — a
transparent prior for *ranking only*. Every output row carries `backend="heuristic"`.
Do not report these as physical adsorption energies.

## Plugging in the real OC22 backend (GPU / Vast.ai)

1. `pip install fairchem-core` and download an OC22 checkpoint (EquiformerV2 / GemNet-OC).
2. In `hea_oer/adsorption.py`, implement `OC22FairchemBackend.predict`:
   build (oxy)hydroxide/oxide surface slabs for the composition (pymatgen/ASE),
   place \*OH/\*O/\*OOH adsorbates, relax with the GNN, convert binding energies
   to ΔG with the standard gas-phase references.
3. Run with `--backend oc22`. Everything downstream (ranking, plot, shortlist) is unchanged.

## Round-2 (after measuring round-1 alloys)

Feed measured overpotentials into `active_learning.propose_round2(...)` to pick the
next compositions to melt. Swap the scikit-learn GP for BoTorch `qNEHVI` for true
multi-objective acquisition (`pip install botorch ax-platform`).
