# 06 — Project Shortlist (ranked candidate framings)

All framings share the winning shape: **ML/simulation proposes or screens a
candidate → fabricate it → measure it and beat a baseline.** Each is gated on the
logistics in [`../tasks/todo.md`](../tasks/todo.md).

## Rare-earth track (strongest "so what")

### R1 ⭐ — RE-lean / RE-free magnet inverse design *(top recommendation)*
- **Pitch:** AI-designed magnets that cut critical-rare-earth (Dy/Tb/Nd) dependence.
- **Hypothesis:** ML finds a composition preserving an intrinsic hard-magnetic
  figure of merit with less critical RE — Ce/La substitution, Sm-Fe-N, or RE-free
  **tetrataenite (L1₀ FeNi)** / MnBi / Fe₃Sn.
- **Toolchain:** generative/inverse-design stack + Materials Project/AFLOW magnetic
  data → FWM melt (Fe-Ni) → Purdue VSM (M–H), XRD (order parameter), SEM.
- **Measure (not BHmax):** magnetization, Curie-T, anisotropy, or L1₀ order parameter.
- **Ceiling:** Top-40 stretch. **Fit:** ★★★. **Bridge to thermal:** none.

### R2 — Magnetocaloric RE materials for solid-state cooling *(keeps the thermal theme)*
- **Pitch:** rare-earth magnetic refrigeration = compressor-free green cooling.
- **Hypothesis:** ML optimizes ΔS_M near room-T (Gd, La(Fe,Si)₁₃, Gd₅Si₂Ge₂);
  fabricate one, confirm via M(H,T).
- **Why:** cleanest single-measurement experiment; directly bridges cooling + RE.
- **Ceiling:** Top-40 stretch. **Fit:** ★★★. **Bridge to thermal:** direct.

### R3 — ML-guided selective REE separation / recovery
- **Pitch:** urban-mining of rare earths from e-waste / spent magnets.
- **Hypothesis:** ML designs a selective ligand/sorbent; validate by leaching scrap
  + ICP-MS selectivity.
- **Ceiling:** Scholar→Finalist. **Fit:** ★★ (wet-chem heavy). **Risk:** lowest fab risk.

## Thermal track (white space, Scholar-safe)

### T1 — Heat-spreader alloy/composite inverse design
- **Hypothesis:** ML inverse-designs a Cu-based / metal-matrix composite hitting
  the real sweet spot — **high κ *and* CTE matched to GaN/SiC** (CTE mismatch, not
  low κ, is the failure mode) — beating a Cu / Cu-Mo baseline on a κ/CTE figure of merit.
- **Toolchain:** inverse-design stack → FWM fabricates → Purdue laser-flash (κ),
  dilatometry (CTE), SEM/XRD.
- **Gate:** can FWM make a custom Cu-based / metal-matrix sample in weeks?
- **Ceiling:** Top-40 stretch. **Fit:** ★★★ (reuses alloy-AI + FWM core).

### T2 — Surrogate-accelerated cold-plate inverse design *(fabrication-agnostic)*
- **Hypothesis:** a CNN surrogate on a few hundred OpenFOAM runs drives an optimizer
  to a microchannel geometry >10% cooler at equal pumping power vs. a straight-
  channel baseline — confirmed by full CFD **and** a 3D-printed bench test.
- **Toolchain:** OpenFOAM → PyTorch surrogate → GA/Bayesian opt → 3D print + cartridge
  heater/thermocouples.
- **Why:** self-contained; doesn't depend on FWM. **Trade-off:** reads more
  thermal-fluids than materials.
- **Ceiling:** Top-40 stretch. **Fit:** ★★.

### T3 — MLIP lattice-κ + defect engineering *(computational fallback)*
- **Hypothesis:** quantify how antisite defects degrade κ in c-BAs (or a fabricable
  system) via foundation-MLIP + phono3py/ShengBTE; reproduce the pristine benchmark.
- **Why lower:** BAs can't be fabricated → loop stays in-silico → Scholar-safe,
  Finalist-unlikely alone. Most reuses the `mlip-dynamic-stability` stack.

## Decision matrix

| | Ceiling | ML fit | Fab risk (3.5 mo) | "So what" | Reuses existing stack |
|---|---|---|---|---|---|
| **R1 magnets** | Top-40 stretch | ★★★ | medium | **highest** | ★★★ |
| **R2 magnetocaloric** | Top-40 stretch | ★★★ | low–medium | high | ★★★ |
| R3 REE separation | Scholar→Finalist | ★★ | low | high | ★ |
| T1 heat-spreader alloy | Top-40 stretch | ★★★ | medium | high | ★★★ |
| T2 cold-plate surrogate | Top-40 stretch | ★★ | medium | high | ★★ |
| T3 MLIP κ + defects | Scholar | ★★★ | n/a (in-silico) | medium | ★★★ |

## Current recommendation

**R1 (RE-lean / tetrataenite magnets)** for maximum ceiling + "so what" + stack
reuse; **R2 (magnetocaloric)** if keeping the cooling theme and the cleanest
experiment matters more. **T1** is the best purely-thermal option if rare earths
are dropped. Final pick is gated on the four logistics answers in `tasks/todo.md`.
