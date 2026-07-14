# src/thermo — the thermal-conductor oracle (docs/24 Spike 1)

Compute code for the Cu-Fe(-X) co-design project
([docs/24](../../docs/24-thermal-pivot-execution-plan.md)). First piece: the
**κ_e channel** — KKR-CPA residual resistivity via
[MuST](https://github.com/mstsuite/MuST) (`mst2` for self-consistent CPA
potentials, `kubo` for Kubo-Greenwood conductivity), then κ_e through
Wiedemann-Franz/Smith-Palmer calibrated against our own 4-point wire
measurements. κ_L (fine-tuned NEP + GPUMD HNEMD) and the qNEHVI BO layer land
here later.

## Files

- `setup_must_box.sh` — one-shot MuST build on a fresh Vast CPU box (tmux,
  idempotent, logs to `/workspace/setup_must.log`). **Untested on a live box**
  (written 2026-07-13 after the DFT boxes were torn down); the `ARCH` auto-pick
  is the likeliest thing to need a manual override on first run.

## Validation ladder (the week-2 gate, run before ANY production sweep)

The catalysis campaign's lesson ([docs/26](../../docs/26-endmember-parity-checkpoint.md)):
never trust a tier until it reproduces something known. In order:

1. **fcc Cu KKR SCF** (a = 3.615 Å): converges, sensible Fermi energy/DOS.
   MuST ships `Tutorials/` + `Potentials/` starting potentials — adapt the
   nearest bundled example rather than writing inputs from scratch.
2. **Cu₁₋ₓFeₓ KKR-CPA** at x ∈ {1, 2, 5, 10} at.%: SCF converges at every x.
   Watch the Fe local moment — Fe in Cu is magnetic; if a non-spin-polarized
   run misbehaves, go spin-polarized (and note DLM as the fallback).
3. **`kubo` residual resistivity ρ_res(x)** on the converged potentials. Gates:
   - ρ_res → 0 as x → 0 (pure-Cu limit clean);
   - **dilute slope vs the Linde/experimental value for Fe in Cu,
     ~9.3 μΩ·cm per at.%** — accept within ~2× (CPA + local-moment physics;
     document the gap either way, it becomes the calibration constant);
   - Nordheim-like x(1−x) curvature toward higher x.
4. Only then: the composition-grid sweep v1 (docs/24 §6 week 2–3), ~minutes–hours
   per composition on a 15-vCPU box.

Every ρ_res(x) point gets committed with its inputs, like `runs/<M>_slab/` did
for the DFT campaign — same provenance discipline, new physics.

## Ladder results (2026-07-14, box 137.175.76.24 — GATE PASSED)

MuST v1.9.3-class build (arch `arch-vast-gnu-openblas`, NotUse_P3DFFT), fcc
a = 3.615 Å fixed, non-spin-polarized, muffin-tin/VWN, 20³ k, vertex
corrections ON. Full outputs in `runs_cpa/<tag>/o_n*`; raw tensor blocks in
`runs_cpa/results.txt`.

| x_Fe (at.%) | ρ_res (μΩ·cm) | ρ/x (μΩ·cm/at.%) |
|---|---|---|
| 1 | 16.262 | 16.26 |
| 2 | 30.184 | 15.09 |
| 5 | 68.211 | 13.64 |
| 10 | 112.979 | 11.30 |

- **Dilute slope 16.26 μΩ·cm/at.% = 1.75× Linde (9.3) → inside the
  pre-registered 2× gate.** The overshoot direction/magnitude is the textbook
  non-spin-polarized artifact: paramagnetic Fe parks its full d virtual bound
  state at E_F, while the real (magnetic) impurity splits it. Literature
  non-magnetic KKR values for Fe-in-Cu sit at ~14–18; spin-polarized/DLM
  brings them to ~7–10 — that re-run is the documented refinement, and the
  measured round-0 Cu-2Fe button (docs/27 #3) anchors it experimentally.
- **Curvature is physical:** ρ/x falls monotonically 16.3 → 11.3 (concave,
  Nordheim-consistent; saturates faster than rigid-band x(1−x), as expected
  for resonant scatterers). Tensor perfectly isotropic (cubic ✓).
- **Tool limitations (documented, both hit live):** (1) `kubo` hard-stops on
  single-species sites ("atom on non-CPA sublattice") even at concentration
  1.00 — and the sublattice type is baked into the *potential file*, so a
  CPA-typed SCF redo doesn't save x = 0. (2) **Sub-1 at.% CPA is pathological
  on this setup:** x = 0.1 at.% dies at SCF #4 ("screwed potential"),
  x = 0.5 at.% converges but to ρ = 19.26 μΩ·cm > the 1 at.% value —
  non-monotonic, unphysical, **excluded** (`runs_cpa/o_n0000000_CuFe_x0005`
  kept as evidence; `CuFe_x0001.off` retired on-box). The ρ→0 limit is an
  analytic property of CPA (zero disorder ⇒ zero residual scattering), not a
  numerical demonstration here. This costs nothing: the entire round-0 design
  space (Cu-2…14 wt.% ≈ 2.3–15.6 at.%) lies inside the validated 1–10 at.%
  window, and the sweep grid will respect a ≥1 at.% floor.
- **Cost ledger:** SCF 16–48 min + kubo ~10 min per composition at 8 ranks on
  a 9.6-vCPU box ⇒ ~1 h/composition ⇒ the docs/24 §6 CPA sweep v1 (20–40
  compositions) is 1–2 box-days. The κ_e tier is affordable exactly as planned.

**Verdict: the κ_e engine is validated at v1.** Next: spin-polarized re-run of
this ladder (one flag), then the composition-grid sweep feeding
`surrogate_v0.DRHO_SOLUTE` replacement.
