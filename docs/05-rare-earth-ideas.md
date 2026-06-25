# 05 — Rare-Earth Project Ideation

## Why rare earths may beat the generic thermal idea

STS Top-40 materials projects almost always carry a **national-importance "so
what."** Rare earths are the strongest critical-materials story in 2026: China
controls ~90% of REE refining and magnet production, and 2023–2025 export
controls on rare-earth magnet technology made it a supply-chain/defense
flashpoint. That hook is the ceiling-breaker the pure-thermal lane lacked — and
it still bridges to the cooling theme via magnetocaloric refrigeration.

## Why it fits this student

The dominant REE application — **permanent magnets** (NdFeB; Dy/Tb for
high-temperature coercivity) — is an **alloy inverse-design problem**, which is:

- the proven STS-winning computational template (Hirshorn '26 alloy inverse
  design; Evan Kim '23 superconductor GAN);
- exactly what the student already builds (generative CSP, alloy AI design, MLIPs);
- fabricable through **Fort Wayne Metals'** Fe-Ni / specialty-alloy melt-and-draw
  capability.

## Ranked ideas

| # | Idea | STS ceiling | ML fit | Fabricate via | Thermal bridge |
|---|---|---|---|---|---|
| 1 | ML inverse design of **critical-REE-lean / RE-free magnets** | **Top-40 stretch** | ★★★ | FWM (Fe-Ni, Ce/La-substituted) + Purdue VSM/XRD | — |
| 2 | **Magnetocaloric** RE materials for solid-state cooling | Top-40 stretch | ★★★ | FWM/Purdue + PPMS/VSM | **direct** |
| 3 | ML-guided **selective REE separation / recovery** | Scholar→Finalist | ★★ | wet chem + ICP-MS/OES | — |

### #1 (recommended) — "AI-designed magnets to cut critical rare-earth dependence"
- **Hypothesis:** an ML model finds a composition that reduces Dy/Tb (or Nd)
  while preserving the intrinsic hard-magnetic figure of merit — via heavy-RE-free
  coercivity routes (Ce/La substitution in NdFeB, Sm-Fe-N) **or** a genuinely
  RE-free phase (**tetrataenite** = L1₀-ordered FeNi, the "meteorite magnet";
  MnBi; Fe₃Sn).
- **Toolchain:** generative/inverse-design stack + magnetic datasets (Materials
  Project / AFLOW moments, Curie-T) → propose candidates → **FWM makes Fe-Ni /
  specialty alloy → Purdue VSM (M–H), XRD (order parameter), SEM**.
- **Novelty hook:** tetrataenite is especially hot — terrestrial L1₀ ordering is
  kinetically "forbidden"; a 2022 Cambridge result showed P-doping accelerates it.
  **ML to find the dopant/processing that unlocks ordering**, fabricated in FWM's
  Fe-Ni wheelhouse, is novel, RE-free, and supply-chain-relevant.
- ⚠️ **Rigor trap:** do NOT promise *BH*max / coercivity (dominated by
  microstructure/processing; won't converge in 3.5 months). Target an
  **intrinsic, ML-predictable, fast-to-measure** property: magnetization, Curie
  temperature, magnetocrystalline anisotropy, or L1₀ order parameter.

### #2 (keeps the thermal interest) — "RE magnetocaloric materials for compressor-free cooling"
- **Hypothesis:** ML screens/optimizes a magnetocaloric composition (Gd,
  La(Fe,Si)₁₃, Gd₅Si₂Ge₂ family) for large near-room-T entropy change ΔS_M;
  fabricate one and confirm via M(H,T) curves.
- **Why elegant:** magnetic refrigeration = green solid-state cooling — the bridge
  between rare earths and the original cooling theme. ΔS_M is **measurable from a
  single PPMS/VSM campaign** (cleaner than magnet coercivity).
- **So what:** energy-efficient cooling for electronics/datacenters + a
  critical-materials angle.

### #3 (sustainability/chemistry lane) — "ML-designed selective REE recovery from e-waste / spent magnets"
- **Hypothesis:** an ML model designs a ligand/sorbent (or optimizes conditions)
  that selectively captures a target lanthanide despite near-identical adjacent
  REE chemistry; validated by leaching scrap magnets and measuring selectivity by
  ICP-MS.
- **So what:** urban-mining / circular-economy framing — very STS-friendly.
  Weaker fit to the student's compute strengths; lowest fabrication risk.

## Quick-hit alternatives (honest feasibility)

- **REBCO / YBCO superconductors** — fusion-magnet relevance is white-hot in 2026,
  and ScGAN-for-superconductors already placed at STS; but synthesis/
  characterization is hard in 3.5 months → lean computational.
- **Upconversion nanoparticles** (NaYF₄:Yb,Er) — clean nanoparticle synthesis + PL
  spectroscopy for bioimaging/solar; more photonics-chemistry than the core stack.
- **Rare-earth quantum-memory crystals** (Er/Eu) — too cryogenics-heavy for a
  high-school timeline.

## Recommendation

Lead with **#1 (RE-lean / tetrataenite magnets)** for maximum ceiling and the
cleanest match to the inverse-design stack; switch to **#2 (magnetocaloric)** to
keep the cooling theme and a cleaner single-measurement experiment. Both convert
the existing ML-materials tooling into the Top-40 template, anchored to the
strongest "so what" in materials right now.

**Magnet-specific gates:** VSM/PPMS access + booking lead time (the make-or-break
instrument here); whether FWM can melt a custom Fe-Ni / RE-substituted
composition and how fast; DFT-for-magnetism experience (magnetocrystalline
anisotropy needs spin-orbit DFT — harder than κ).
