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
