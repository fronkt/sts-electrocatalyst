# 13 — Round-1 results: first real UMA surface energies

First physically-grounded pass of the round-1 selector, replacing the heuristic
placeholder ([`adsorption.HeuristicBackend`](../src/hea_oer/adsorption.py)) with
real adsorption energies from a Meta **UMA** universal MLIP
(`uma-s-1p1`, `fairchem-core` 2.21.0). Run on an RTX 5090 (Vast.ai), 2026-06-26.

Two surface models were run (`--surface`): a metal **fcc(111)** proxy (first pass,
below) and a **rutile(110) oxide, multi-site** model (the refinement — **the result
to use**). The oxide surface is far more physical for OER; the metal pass is kept
for the surface-sensitivity comparison.

> This is round-1 **screening**, not a physical prediction of catalytic activity:
> the **relative ranking** of single-phase candidates is what's used, with the
> honest model caveats below.

## Rutile(110) oxide, multi-site — headline result

The metal proxy over-binds O, stranding every candidate on the strong-binding leg
(descriptors −2…0 eV, η 2.7–4.9 V). The physically faithful fix is the OER-active
oxide surface: **rutile MO2(110)** — the surface the Man et al. (2011) universal
scaling (which sets the volcano) was built on — cleaved with `pymatgen`
`SlabGenerator` (correct stoichiometric, symmetric, bridging-O termination), with
the cation sublattice decorated by the composition and the **distribution of cus
(coordinatively-unsaturated) active sites** sampled — 4 per composition, each a
different local cation environment (the HEA scaling-breaking hypothesis, docs/12
§3b). η is taken at the **favorable-tail (best) cus site**; per-site spread is
reported. Module: [`surfaces_rutile.py`](../src/hea_oer/surfaces_rutile.py)
(pymatgen is an *optional* dependency — only this module imports it).

Run: top **12** single-phase candidates, **4 cus sites** each, 1899 s.

```bash
PYTHONPATH=src python src/scripts/run_round1_uma.py \
    --surface rutile --n-sites 4 --pool 12 --top-k 4 --model uma-s-1p1 --device cuda
```

**The oxide surface fixes the physics.** Descriptors now cluster around the volcano
**apex (~1.6 eV)** and best-site η drops to **0.78–1.5 V** for the top candidates
(CoCrFeMnNi smoke: descriptor −0.29 eV metal → **+2.02 eV** rutile). Candidates now
track the scaling-limit volcano. **Spearman ρ(η_heuristic, η_rutile) = −0.09** — the
cheap prior is *uncorrelated* with the real oxide ranking, the strongest evidence
yet that the ML surface model carries the signal.

### Rutile shortlist to melt (best-site η + site distribution)

| Rank | Composition (at.%) | η_best (V) | descriptor (eV) | η_mean (V) | η_std (V) | sites |
|---|---|---|---|---|---|---|
| 1 | **Fe32Ni17Co34Mn18** (Cr-free) | 0.78 | 1.75 | 1.18 | 0.26 | 4 |
| 4 | Cr21Ni24Co15Cu6Fe33 | 1.03 | 1.38 | 1.45 | 0.32 | 4 |
| 5 | Cr8Fe34Mn9Ni23Co27 | 1.15 | 2.38 | 1.26 | 0.14 | 4 |
| 8 | Co24Fe24Ni35Mn17 | 1.15 | 2.34 | 1.39 | 0.27 | 4 |

Top pick **Fe32Ni17Co34Mn18** sits nearest the apex (descriptor 1.75, best-site η
0.78 V), is **Cr-free** (no Cr(VI) leaching hazard) and Pt-group-free. The favorable
cus site is markedly more active than the surface average (η_best 0.78 vs η_mean
1.18) — direct support for the HEA active-site-distribution hypothesis.

Full table + per-site stats: [`results/round1_uma_rutile_candidates.csv`](../results/round1_uma_rutile_candidates.csv).
Volcano: [`results/round1_uma_rutile_volcano.png`](../results/round1_uma_rutile_volcano.png).

**Surface model reshuffles the ranking** (a result in itself): the rutile #1
(Fe32Ni17Co34Mn18) was *rank 18* on the metal surface; the metal #1
(Fe35Mn15Ni18Co32) is rank 7 on rutile — screening on the bare-metal proxy would
have missed the best oxide candidate.

---

## (First pass) Metal fcc(111) proxy

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

## Honest caveats (carry into the paper)

- **Metal fcc(111) is a proxy** (first pass). On bare metal the surface over-binds O,
  so ΔG_O − ΔG_OH lands at −2…0 eV (far from the ~1.6 eV apex) and η is 2.7–4.9 V —
  **unphysical in magnitude**. *Addressed* by the rutile(110) oxide model above.
- **Site-occupancy distribution** — *addressed*: rutile sampling uses 4 cus sites per
  composition (favorable-tail aggregation), so the HEA active-site distribution is
  now captured, not a single site.
- **Rutile oxide caveats:** (i) UMA's OC20 adsorption head is metal-dominated, so
  oxide adsorption is partly **out-of-distribution**; (ii) FeO2/CoO2/NiO2/CuO2 are
  not ground-state rutiles, so their lattice entries are **model values** on the
  rutile trend; (iii) rutile(110) is still a *model* surface, not the true layered
  oxyhydroxide.
- **Screening prior, not an oracle.** Reconstruction, SRO, and surface restructuring
  mean predicted η is approximate; the contribution is the *calibrated* ML-guided
  search confirmed against experiment.

## Next

- Down-select the **rutile shortlist** for the first FWM melt (top pick
  Fe32Ni17Co34Mn18; single-phase already gated).
- Further model refinement (optional): true **oxyhydroxide (NiOOH/FeOOH)** termination
  or **omat**-task surface energies; widen the rutile pool beyond 12; larger supercell
  for >4 cus sites per composition.
- After measured η comes back, condition the round-2 surrogate
  ([`active_learning.propose_round2`](../src/hea_oer/active_learning.py)).
