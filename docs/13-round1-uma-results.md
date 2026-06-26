# 13 — Round-1 results: first real UMA surface energies

First physically-grounded pass of the round-1 selector, replacing the heuristic
placeholder ([`adsorption.HeuristicBackend`](../src/hea_oer/adsorption.py)) with
real adsorption energies from a Meta **UMA** universal MLIP
(`uma-s-1p1`, `fairchem-core` 2.21.0). Run on an RTX 5090 (Vast.ai), 2026-06-26.

> This is round-1 **screening**, not a physical prediction of catalytic activity.
> See the surface caveat in §3 — the absolute overpotentials are not meaningful;
> the **relative ranking** of single-phase candidates is.

## Method (two-stage, to spend GPU only where it counts)

The UMA backend is ~6 relaxations per composition, so we do **not** run it on every
sampled alloy. Driver: [`src/scripts/run_round1_uma.py`](../src/scripts/run_round1_uma.py).

1. **Stage 1 (CPU, cheap) — heuristic prior + phase-stability gate.** Sample 3000
   HEA compositions over Fe–Co–Ni–Cr–Mn–Cu; score with the oxophilicity heuristic
   and the empirical single-phase rules (VEC, δ, ΔH_mix, ΔS_mix, Ω). 2470/3000 were
   single-phase; the top **24** by heuristic score were promoted.
2. **Stage 2 (GPU) — UMA on the pool only.** For each of the 24: build an fcc(111)
   slab, relax the clean slab + `*OH/*O/*OOH` adsorbates with `uma-s-1p1` (OC20
   task), and CHE-reference to gas-phase H₂O/H₂ → ΔG → theoretical η. 24 candidates
   in **833 s** (~35 s each) after a one-time 1.2 GB checkpoint download.

Reproduce:

```bash
# GPU box: fairchem-core 2.21 (pins torch==2.8.0; install torch from the cu128
# PyTorch CDN first), HF login with facebook/UMA access.
PYTHONPATH=src python src/scripts/run_round1_uma.py \
    --n-samples 3000 --pool 24 --top-k 4 --model uma-s-1p1 --device cuda
```

## Key result — UMA re-orders the cheap prior

**Spearman ρ(η_heuristic, η_UMA) = 0.236** over the shared 24-candidate pool. The
oxophilicity prior and the real model **disagree substantially**: UMA adds real
information beyond a composition-weighted descriptor, and shifts the picks toward
**higher-Mn, lower-Cr** compositions. This is the first ML-vs-ML calibration point
and the template for the eventual ML-vs-experiment correlation (the project's
contribution).

### Shortlist to melt (diverse top-4 by activity × formability × abundance)

| Rank | Composition (at.%) | η_UMA (V) | descriptor (eV) | formability | abundance | cost $/kg |
|---|---|---|---|---|---|---|
| 1 | Fe35Mn15Ni18Co32 | 2.78 | −0.26 | 0.91 | 0.45 | 14.2 |
| 2 | Mn24Fe24Ni25Co17Cu9 | 2.70 | −0.66 | 0.85 | 0.40 | 11.8 |
| 3 | Mn16Co22Ni33Fe28 | 3.17 | −1.17 | 0.92 | 0.41 | 13.7 |
| 4 | Cr19Co21Fe27Ni33 | 3.32 | −0.53 | 0.94 | 0.36 | 14.8 |

Full ranked table + ΔG(*OH/*O/*OOH): [`results/round1_uma_candidates.csv`](../results/round1_uma_candidates.csv).
Volcano / Pareto plot: [`results/round1_uma_volcano.png`](../results/round1_uma_volcano.png).

## 3. Honest caveats (carry into the paper)

- **Surface is a metal fcc(111) proxy.** The true OER-active phase is the in-situ
  reconstructed (oxy)hydroxide skin. On bare metal the surface over-binds O, so the
  descriptor ΔG_O − ΔG_OH lands at −2…0 eV (far from the ~1.6 eV scaling-limit
  apex) and absolute η is 2.7–4.9 V — **unphysical in magnitude**. Only the ranking
  is used. **Next refinement:** rutile-oxide (110) / oxyhydroxide terminations.
- **Single adsorption site per slab.** A site-occupancy distribution (the favorable
  tail) per composition is the planned upgrade — HEAs present a *distribution* of
  active sites, which is the scaling-relation-breaking hypothesis.
- **Screening prior, not an oracle.** Reconstruction, SRO, and surface
  restructuring mean predicted η is approximate; the contribution is the
  *calibrated* ML-guided search confirmed against experiment.

## Next

- Down-select the shortlist for the first FWM melt (single-phase already gated).
- Optional model refinement: oxide(110) surface termination + per-composition site
  distribution; re-rank and compare the shortlist stability.
- After measured η comes back, condition the round-2 surrogate
  ([`active_learning.propose_round2`](../src/hea_oer/active_learning.py)).
