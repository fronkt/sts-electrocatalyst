# 14 — Compute log (reproducible record / lab notebook)

Dated record of every compute step behind the round-1 ML screening, for
reproducibility and as STS independence evidence (docs/12 §8). All work on
2026-06-26 on a Vast.ai **RTX 5090** (32 GB, driver 580, CUDA 13.0), venv
`/venv/main` (Python 3.12.13). Code + results on branch `uma-round1-results`.

## 1. Environment

| Component | Version / note |
|---|---|
| GPU | RTX 5090 (Blackwell, sm_120), 32 GB |
| torch | **2.8.0+cu128** (fairchem-core 2.21 pins torch==2.8.0; the default PyPI/cu128 wheel supports sm_120) |
| fairchem-core | 2.21.0 (UMA) |
| ase | 3.x · pandas 3.0.3 · pymatgen (optional, rutile only) |
| model | `uma-s-1p1` (1.2 GB checkpoint), task `oc20`, gated `facebook/UMA` (acct frankcai222) |

**Install order that worked on this bandwidth-capped box** (PyPI ~1 MB/s; PyTorch
CDN ~5 MB/s; HF Xet ~7 MB/s):
```bash
source /venv/main/bin/activate
uv pip install torch==2.8.0 torchvision --index-url https://download.pytorch.org/whl/cu128
uv pip install fairchem-core pandas pymatgen
hf auth login    # token with facebook/UMA access; HF_HOME=/workspace/.hf_home
```
Run long installs in **tmux** (survives SSH drops); `pkill -x uv` (not `-f "uv pip"`,
which matches the launching shell). See [[feedback_vast_workflow]].

## 2. Validation steps (all passed)

| Step | Command / check | Result |
|---|---|---|
| Plumbing (CPU) | `smoke_uma.py --calc emt` (Ni50Cu50) | slab→relax→reference→ΔG→η OK, 0.6 s |
| First real UMA | `smoke_uma.py --model uma-s-1p1` (CoCrFeMnNi, metal) | ΔG −0.52/−0.82/−0.95, desc −0.29, η 4.64 V, 188 s (incl. 1.2 GB download) |
| Rocksalt(100) geometry | local ASE check | 128 atoms, cus metal 5-coord ✓ |
| Rutile(110) geometry | local pymatgen check | 72 atoms, **O:M = 2.00**, cus 5-coord, 4 cus sites ✓ |
| Rutile multisite smoke | CoCrFeMnNi, 4 sites | desc **−0.29→+2.02**, best-site η 1.95 V, 116 s |

## 3. Production runs

**A. Metal fcc(111) round-1** — `run_round1_uma.py --backend uma --pool 24 --top-k 4`
- Stage 1: 3000 sampled → **2470 single-phase** → top 24 by heuristic score.
- Stage 2: UMA fcc(111), 24 candidates, **833 s**.
- ρ(heuristic, UMA) = **0.236**; shortlist Fe35Mn15Ni18Co32 / Mn24Fe24Ni25Co17Cu9 / Mn16Co22Ni33Fe28 / Cr19Co21Fe27Ni33.
- Out: `results/round1_uma_candidates.csv`, `…_volcano.png`. (Caveat: metal proxy over-binds → η 2.7–4.9 V unphysical, ranking only.)

**B. Rutile(110) multi-site round-1** — `run_round1_uma.py --surface rutile --n-sites 4 --pool 12 --top-k 4`
- Stage 1: same prior → top **12** single-phase.
- Stage 2: rutile(110), 4 cus sites/comp, favorable-tail aggregation, **1899 s** (GPU shared with a batterycv job).
- ρ(heuristic, rutile) = **−0.09**; descriptors at the volcano apex; best-site η 0.78–1.5 V.
- Shortlist: **Fe32Ni17Co34Mn18** (Cr-free, top) / Cr21Ni24Co15Cu6Fe33 / Cr8Fe34Mn9Ni23Co27 / Co24Fe24Ni35Mn17.
- Out: `results/round1_uma_rutile_candidates.csv`, `…_rutile_volcano.png`. Detail in [docs/13](13-round1-uma-results.md).

## 4. Status — is the compute done?

- **Round-1 screening: DONE** (a physically-grounded ranking + shortlist exist).
- **⚠ Known limitation (act before melting):** the two-stage prior pre-filtered to
  12 candidates by **heuristic** score, but ρ(heuristic, rutile) = −0.09 means the
  heuristic does **not** predict rutile activity — so a rutile-excellent composition
  could sit in heuristic-rank 13+ and was never evaluated. **Recommended remaining
  run:** a broader rutile-UMA sweep over more single-phase candidates (e.g. 30–40,
  selected by phase-stability/diversity, *not* heuristic activity), ~1.5–2 GPU-hr.
  The phase-stability gate itself is sound (physics-based); only the heuristic
  *activity* pre-ranking is the weak link.
- **Round-2 active learning: BLOCKED** on experimental η (cannot start until melts
  are measured) — `active_learning.propose_round2`.
- **Optional further refinement:** true oxyhydroxide (NiOOH/FeOOH) termination;
  larger supercell (>4 cus sites); `omat`-task surface energies for cross-check.

## 5. Reproduce

```bash
# round-1 rutile (headline), on a CUDA box with the env in §1:
PYTHONPATH=src python src/scripts/run_round1_uma.py \
    --surface rutile --n-sites 4 --pool 12 --top-k 4 --model uma-s-1p1 --device cuda
# broader sweep (recommended) — raise --pool, optionally widen --n-samples:
#   --surface rutile --n-sites 4 --pool 36 --top-k 6
```

> Infrastructure note: the 5090 box (`137.175.76.24`) was **shared** with a
> batterycv GPU job (separate project) — both coexisted in 32 GB. Do not
> `tmux kill-server` on a shared box.
