# LIT-3(a) — *OOH O–O fingerprint classification (zero DFT)

*Generated 2026-08-12 by `src/dft/lit3_ooh_fingerprints.py`. Registered under docs/43-prereg-week1-factorial.md AMENDMENT 5, A5.3(a) -- zero-DFT tranche. Do not hand-edit — rerun the script.*

## Scope

- **Primary fingerprint (registered):** O–O distance — hydroperoxo *O–OH ~1.37–1.45 Å vs superoxo *OO-H ~1.30–1.32 Å (Inico 2024). The registration writes the bands with `~`; they are applied here as the stated intervals and out-of-band values are reported as such, never coerced.
- **Secondary (registered, NOT computed here):** Bader (QTAIM) charge via pp.x. Inico's thresholds are Bader-defined and may not be compared against Löwdin values without recalibration on our own anchor states. No `.save` directory survives on disk, so **every run below needs one fixed-geometry SCF + pp.x before any charge fingerprint exists** (bounded within the ~150-SCF A5.1a/A5.3a regeneration budget) — see the Bader section.
- Zero new DFT: geometric observables from archived outputs. tier_v2 is frozen and unchanged; tier_v3 does not exist.

## Classification — every archived *OOH relaxation

| run | cell | conv. | O–O (Å) | registered-band class | H sits on | H–O (Å) | tot/abs mag (μ_B) | QC |
|---|---|---|---|---|---|---|---|---|
| `runs/probe/Cr_basin/s0_OOH.out` | 1x1 | yes | 1.354 | UNCLASSIFIED (between the registered bands; nearest = hydroperoxo, 0.016 A away) | adsorbate outer O (*O-OH connectivity) | 1.062 | 11 / 20.09 | TRUSTWORTHY |
| `runs/probe/Cr_cellsym/s0_OOH__2x1o_mir.out` | 2x1 | yes | 1.316 | superoxo (*OO-H band) | adsorbate outer O (*O-OH connectivity) | 1.072 | 21 / 38.41 | TRUSTWORTHY |
| `runs/probe/Cr_cellsym/s0_OOH__2x1o_off.out` | 2x1 | yes | 1.221 | UNCLASSIFIED (outside both registered bands; nearest = superoxo, 0.079 A away) | slab bridging O (*OO-H connectivity) | 0.971 | 21 / 39.89 | TRUSTWORTHY |
| `runs/probe/Cr_cellsym/s0_OOH__2x1v_mir.out` | 2x1 | yes | 1.354 | UNCLASSIFIED (between the registered bands; nearest = hydroperoxo, 0.016 A away) | adsorbate outer O (*O-OH connectivity) | 0.990 | 23 / 38.66 | TRUSTWORTHY |
| `runs/probe/Cr_cellsym/s0_OOH__2x1v_off.out` | 2x1 | yes | 1.232 | UNCLASSIFIED (outside both registered bands; nearest = superoxo, 0.068 A away) | slab bridging O (*OO-H connectivity) | 0.972 | 23 / 40.52 | TRUSTWORTHY |
| `runs/Cr_slab/s0_OOH.out` | 1x1 | yes | 1.360 | UNCLASSIFIED (between the registered bands; nearest = hydroperoxo, 0.010 A away) | adsorbate outer O (*O-OH connectivity) | 1.058 | 11.8 / 19.41 | TRUSTWORTHY |
| `runs/Cu_slab/s0_OOH.out` | 1x1 | **NO** | 1.323 | UNCLASSIFIED (between the registered bands; nearest = superoxo, 0.003 A away) | adsorbate outer O (*O-OH connectivity) | 0.967 | 2.51 / 3.18 | POISONED |
| `runs/Fe_slab/s0_OOH.out` | 1x1 | yes | 1.330 | UNCLASSIFIED (between the registered bands; nearest = superoxo, 0.010 A away) | adsorbate outer O (*O-OH connectivity) | 1.082 | 22.98 / 25.89 | TRUSTWORTHY |
| `runs/Ir_anchor/s0_OOH.out` | 1x1 | yes | 1.427 | hydroperoxo (*O-OH band) | adsorbate outer O (*O-OH connectivity) | 0.982 | — | TRUSTWORTHY |
| `runs/probe/Ir_cellsym/s0_OOH__1x1_off.out` | 1x1 | yes | 1.436 | hydroperoxo (*O-OH band) | adsorbate outer O (*O-OH connectivity) | 0.983 | — | TRUSTWORTHY |
| `runs/probe/Ir_cellsym/s0_OOH__2x1o_mir.out` | 2x1 | yes | 1.421 | hydroperoxo (*O-OH band) | adsorbate outer O (*O-OH connectivity) | 0.982 | — | TRUSTWORTHY |
| `runs/probe/Ir_orient/s0_OOH__yaw270.out` | 1x1 | **NO** | 1.470 | UNCLASSIFIED (outside both registered bands; nearest = hydroperoxo, 0.021 A away) | adsorbate outer O (*O-OH connectivity) | 0.989 | — | POISONED |
| `runs/probe/Ir_orient/s0_OOH__yaw90.out` | 1x1 | yes | 1.434 | hydroperoxo (*O-OH band) | adsorbate outer O (*O-OH connectivity) | 0.984 | — | TRUSTWORTHY |
| `runs/Mn_slab/s0_OOH.out` | 1x1 | yes | 1.335 | UNCLASSIFIED (between the registered bands; nearest = superoxo, 0.015 A away) | adsorbate outer O (*O-OH connectivity) | 1.089 | 17 / 23.76 | TRUSTWORTHY |
| `runs/Ru_anchor/s0_OOH.out` | 1x1 | yes | 1.387 | hydroperoxo (*O-OH band) | adsorbate outer O (*O-OH connectivity) | 1.026 | — | TRUSTWORTHY |
| `runs/probe/Ru_cellsym/s0_OOH__2x1o_mir.out` | 2x1 | yes | 1.348 | UNCLASSIFIED (between the registered bands; nearest = hydroperoxo, 0.022 A away) | adsorbate outer O (*O-OH connectivity) | 1.079 | — | TRUSTWORTHY |
| `runs/probe/Ru_cellsym/s0_OOH__2x1o_off.out` | 2x1 | yes | 1.357 | UNCLASSIFIED (between the registered bands; nearest = hydroperoxo, 0.013 A away) | adsorbate outer O (*O-OH connectivity) | 1.085 | — | TRUSTWORTHY |
| `runs/probe/Ru_cellsym/s0_OOH__2x1v_mir.out` | 2x1 | yes | 1.404 | hydroperoxo (*O-OH band) | adsorbate outer O (*O-OH connectivity) | 0.984 | — | TRUSTWORTHY |
| `runs/probe/Ru_cellsym/s0_OOH__2x1v_off.out` | 2x1 | yes | 1.376 | hydroperoxo (*O-OH band) | adsorbate outer O (*O-OH connectivity) | 1.060 | — | TRUSTWORTHY |
| `runs/probe/Ru_orient/s0_OOH__yaw270.out` | 1x1 | **NO** | 1.389 | hydroperoxo (*O-OH band) | adsorbate outer O (*O-OH connectivity) | 1.018 | — | POISONED |
| `runs/probe/Ru_orient/s0_OOH__yaw90.out` | 1x1 | yes | 1.361 | UNCLASSIFIED (between the registered bands; nearest = hydroperoxo, 0.009 A away) | adsorbate outer O (*O-OH connectivity) | 1.071 | — | TRUSTWORTHY |

- 21 geometries classified (18 from converged relaxations); 12 sit outside the two registered bands (between or beyond them) and are reported with their distance to the nearest band, never coerced into one.
- Unconverged rows (if any) are classified from their last-step geometry and marked; they are not relaxed minima and must not be quoted as such.

## Excluded fixed-geometry outputs (geometry duplicates)

The P7 U-ladders, the docs/41 probe variants (dipole/vac/RPBE/spin), the Cr k-mesh bridges and the block-1C Hessian stencil are fixed-geometry SCFs at a parent relaxation's coordinates: same geometry, so classifying them again would double-count. 25 entries listed in the JSON.

## Scaling-residual audit (Man 3.2 ± 0.2/0.4 — flag only)

| metal | *OOH energy used | ΔG_OH | ΔG_OOH | x = ΔG_OOH−ΔG_OH (eV) | flag |
|---|---|---|---|---|---|
| Ru | production | 0.529 | 3.709 | **3.180** | within Man 3.2 +/- 0.2 |
| Ir | production | -0.001 | 3.652 | **3.652** | RPBE-population OUTLIER FLAG (|x - 3.2| = 0.452 eV > 0.4) -- flag only, never a per-state pass/fail; docs/41 P9 functional-mismatch caveat applies |
| Cr | gate1_passed_basin (value of record) | 1.518 | 4.620 | **3.102** | within Man 3.2 +/- 0.2 |
| Cr | production_mirror (METASTABLE, docs/41 s6f -- audited, not of record) | 1.518 | 4.799 | **3.281** | within Man 3.2 +/- 0.2 |
| Mn | production | 1.907 | 4.942 | **3.034** | within Man 3.2 +/- 0.2 |
| Fe | production | 2.134 | 4.845 | **2.711** | RPBE-population OUTLIER FLAG (|x - 3.2| = 0.489 eV > 0.4) -- flag only, never a per-state pass/fail; docs/41 P9 functional-mismatch caveat applies |
| Cu | production | — | — | — | NOT COMPUTABLE: slab (missing), s0_OH (failed strict QC), s0_OOH (failed strict QC), H2O (missing), H2 (missing) |

Registered holes (reported, not repaired): (1) Co: no *OOH run exists at any U (docs/41 s6d/s6e; docs/43 A5.5 firewall) -- the hole is registered, not papered over (2) Ni: runs/Ni_slab *OOH chain rests on dft_eta.json.RETRACTED; no trusted Ni row exists

## Bader (registered secondary) — what it would take

- Status: **NOT ATTEMPTED (registered secondary; requires charge densities that do not survive on disk)**.
- Runs needing charge-density regeneration: **21** (every classified row; no `.save` survives).
- Per run: one fixed-geometry SCF at the archived final geometry to regenerate the density (A5.3a; part of the ~150-SCF A5.1a/A5.3a regeneration budget) + pp.x + a Bader partitioning, recalibrated on our own unambiguous anchor states before Inico's thresholds are applied.

## Companion compute decks (prepared, NOT deployed)

The A5.3(b) *OO-H spot check and A5.3(c) Cr conformer×spin factorial decks are built by `src/dft/build_lit3_ooh_anatomy.py` into `runs/probe/{Cr,Ir,Ru}_lit3/` with NOT-DEPLOYED manifests (`runs/probe/m_lit3_np20.txt`, `runs/probe/lit3_manifest.json`). docs/43 A5.7 gates any launch on the 1A manifest being drained, and the ±-spin-start reading needs sign-off first.
