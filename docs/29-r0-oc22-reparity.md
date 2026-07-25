# 29 — R0: Killing the Task-Head Artifact (uma-s-1p2p1 / oc22 re-parity)

**Date:** 2026-07-24
**Status:** IN PROGRESS — protocol frozen below *before* results landed (pre-registration)
**Plan:** [docs/28 §2, §7 R0](28-electrocatalyst-revival-plan.md) · **Supersedes the verdict in**
[docs/26](26-endmember-parity-checkpoint.md) *if and only if* the gate below says so.
**Branch:** `r0-catalysis-revival` · **Runner:** `src/dft/uma_oc22_parity.py` ·
**Analysis:** `src/dft/parity_r0.py`

---

## 1. The question

docs/26 concluded "UMA cannot rank rutile-oxide OER" from Spearman ρ = 0.40 (p = 0.60),
Pearson r = −0.216, MAE 0.706 eV over 4 endmembers. That campaign ran **`uma-s-1p1`
with `task_name="oc20"`** — the head trained to emulate **RPBE adsorption energies on
metals**. Our chemistry is correlated rutile oxides computed with **PBE+U**, which is
what the **`oc22`** head emulates; OC22's training set contains 4,318 rutile systems
with O\*/OH\*/OOH\* intermediates (arXiv:2206.08917). `oc22` exists only in the
`uma-s-1p2`/`uma-s-1p2p1` checkpoints, so it was never reachable from `uma-s-1p1`.

A **negative** Pearson r is the signature of a reference/settings mismatch, not of a
capability ceiling — a merely under-powered model gives noisy-positive correlation, not
anti-correlation. So the docs/26 verdict is **confounded** until the correct head is tested.

## 2. Pre-registered protocol (frozen before results)

Everything except the model/head is byte-identical to docs/26:

- **Geometries:** the archived QE `*.in` initial structures (`runs/<M>_slab/`), parsed
  with the same `ase.io.read(..., format="espresso-in")` path, same `FixAtoms` bottom-half
  constraint, 18-atom MO₂(110), 1 cus site.
- **Relaxer:** ASE BFGS, `fmax = 0.05 eV/Å`, `steps = 300` (docs/26 values).
- **Referencing:** `hea_oer.referencing.delta_G` + `descriptors.oer_overpotential`, unchanged.
- **Reference chain:** gas-phase H₂O/H₂ relaxed with the **same model and same head** as
  the slabs. Heads emulate different DFT references, so cross-head mixing would break the
  CHE chain; each head is internally self-consistent, mirroring the QE side.
- **Variants:** `uma-s-1p2p1` × {`oc22` (the hypothesis), `oc20` (ablation — isolates
  head-change from checkpoint-change)}. The archived `uma-s-1p1`/`oc20` numbers are the
  third leg, read from `runs/<M>_slab/uma_eta.json` (never overwritten).
- **Energy convention (checked before running):** in UMA *all* task heads emit **total**
  energies — OC20 was recomputed from its original adsorption-energy labels for the UMA
  release — so a per-head CHE chain is well-posed and cross-head mixing is not. This is
  why gas references are recomputed per head rather than shared.
- **Exploratory 4th leg, outside the gate:** `oc25`, the *electrocatalysis* head (also
  1p2-only), which docs/28 did not consider. Caveat stated up front: OC25's level of
  theory is built on **explicit solvent and ions** (arXiv:2509.17862) while these slabs are
  dry vacuum, so it is out-of-distribution in a different way than oc20 is. Included
  because it costs ~$0.10 and pre-empts the obvious "did you try the electrocatalysis
  head?" question; it cannot move the gate in §3, which is defined on `oc22`.
- **QC recorded per relaxation:** BFGS step count, final `fmax`, convergence flag —
  the docs/26 §4 lesson (a "finished" job that never converged) applies to MLIP relaxations too.

### In-distribution anchors (new)

Two literature-anchored slabs, built by the **same** code path
(`surfaces_rutile.build_rutile110_hea` + `qe_slab.write_slab_input`) with experimental
rutile constants (Bolzan 1997): **RuO₂(110)** a = 4.492, c = 3.107 Å; **IrO₂(110)**
a = 4.498, c = 3.154 Å → `runs/{Ru,Ir}_anchor/`.

Builder provenance check: rebuilding the Cr slab with the current pymatgen reproduces
the archived `runs/Cr_slab/slab.in` geometry to **max |Δpos| = 2.9 × 10⁻⁹ Å**,
**max |Δcell| = 3.0 × 10⁻⁹ Å** at `supercell=(1,1)` — so the anchors are on exactly the
footing of the 2026-07 endmembers, and no silent pymatgen drift has occurred.

Purpose: these are *pipeline* controls, not extra data points. Literature η(RuO₂(110)) ≈
0.37–0.42 V and η(IrO₂(110)) ≈ 0.56 V (Rossmeisl 2007, 10.1016/j.jelechem.2006.11.008;
Man 2011, 10.1002/cctc.201000397). If the oc22 head cannot place RuO₂/IrO₂ near their
known values on our own slab+referencing stack, then a poor endmember correlation
indicts *our pipeline*; if it can, a poor correlation is genuinely about the 3d oxides.

## 3. Gate (docs/28 §7, unchanged)

| Spearman ρ (oc22, n = 4) | Verdict | Next |
|---|---|---|
| **≥ 0.8** | UMA usable out of the box | skip to R2/R3 screening |
| **0.5 – 0.8** | partial signal | R3 fine-tune (archived QE trajectories) |
| **≈ 0** | docs/26 conclusion survives, now un-confounded | the negative result becomes a headline finding |

n = 4 is small: ρ is reported with its p-value and never quoted as precision. The
ablation leg (`1p2p1`/`oc20`) is what separates "the head was wrong" from "the checkpoint
was old" — both change at once otherwise.

## 4. Results

*(pending — box run in flight; filled from `docs/figs/uma_oc22_parity.json`)*

| Endmember | η_DFT (V) | η 1p1/oc20 (docs/26) | η 1p2p1/oc20 | η 1p2p1/oc22 |
|---|---|---|---|---|
| MnO₂ | 0.892 | 2.347 | | |
| FeO₂ | 1.263 | 1.105 | | |
| CrO₂ | 1.726 | 1.147 | | |
| NiO₂ | 1.751 | 2.382 | | |
| CoO₂ | — (excluded) | 2.389 | | |
| CuO₂ | — (excluded) | 2.418 | | |
| **RuO₂ anchor** | lit. 0.37–0.42 | — | | |
| **IrO₂ anchor** | lit. ≈ 0.56 | — | | |

## 4b. R1 free reanalysis (docs/28 §4 F1–F3) — DONE, zero new compute

`src/dft/volcano_r1.py` → `docs/figs/volcano_endmembers.{json,png}`. No new DFT: this is
the existing four `dft_eta.json` re-read through the volcano/G_max lens.

| M | x = ΔG_O − ΔG_OH (eV) | ΔG_OOH − ΔG_OH (eV) | η (V) | limiting step | G_max(η=0.3 V) (eV) |
|---|---|---|---|---|---|
| Mn | 2.122 | 3.082 | 0.892 | 2 | 0.969 |
| Fe | 2.493 | 3.087 | 1.263 | 2 | 1.567 |
| Cr | 2.956 | 3.281 | 1.726 | 2 | 1.426 |
| Ni | 2.981 | 2.686 | 1.751 | 2 | 2.437 |

Three findings, all free:

1. **All four sit on the scaling line, far out on the weak-O-binding leg.** Every
   descriptor is x = 2.1–3.0 eV against an apex of ≈1.6, and every point is *OH→*O
   (step-2) limited. The reason none of these endmembers is a good catalyst is therefore
   not incidental — they are descriptor-limited in the way the universal scaling relation
   predicts. This is the quantitative motivation for the whole HEA
   scaling-breaking thesis (docs/12 §3b), stated in the field's own coordinates.
2. **Mn is the only endmember within error of a real electrode band.** η = 0.892 ± 0.3 V;
   the IrO₂ literature band (≈0.56 V) is ~1σ away, RuO₂ (0.37–0.42 V) is not. Mn being
   both the best DFT point *and* the only ambient-stable rutile (docs/28 §3, β-MnO₂
   pyrolusite) is a consistency worth stating: the physics and the stability gate agree.
3. **NiO₂ breaks *OOH/*OH scaling by −0.51 eV** (2.686 vs the universal 3.2 ± 0.2) — the
   only endmember outside the scatter band. That cuts both ways and must not be
   over-claimed: it is the signature the project *wants* (scaling-relation breaking), but
   it appears on a fictitious ambient phase (NiO₂ is layered, not rutile — docs/28 §3),
   at one cus site, with ±0.2–0.4 V method error. Filed as a hypothesis for R1's
   magnetic/termination protocol to confirm or kill, not as a result.

G_max ranks the same as η here (Mn best), so the kinetics-aware descriptor does not
overturn the thermodynamic ordering at this level — one fewer confound to worry about.

## 4c. Checkpoint substitution: uma-s-1p2 (not 1p2p1)

The plan (docs/28 §7 R0) names `uma-s-1p2p1`. On the box, **`fairchem-core 2.21.0`'s
`pretrained_mlip` registry does not resolve the name `uma-s-1p2p1`** — its UMA entries are
`('uma-s-1p2', 'uma-s-1p1', 'uma-m-1p1')` (plus eSEN models). The `.pt` for 1.2.1 exists on
the HF repo but this fairchem release does not register it by that name.

Resolution: run with **`uma-s-1p2`**, the v1.2 checkpoint that docs/28 §2 explicitly names
as an `oc22` carrier ("only exists in the `uma-s-1p2` / `uma-s-1p2p1` checkpoints"). 1.2 → 1.2.1
is a patch (the HF README flags only the original `uma-s-1` for an extensivity bug); for R0's
binary question — *does the oc22 head rank rutile OER at all* — 1p2 is decisive. If the gate
lands in the 0.5–0.8 fine-tune band and the patch matters, the exact 1p2p1 re-run is a
one-line change once fairchem is upgraded to a release that registers it. All output files
and figures are tagged `1p2` (not `1p2p1`) so the record states what actually ran.

This substitution was forced by tooling, discovered *after* the §2/§3 protocol was frozen,
and does not change the gate thresholds.

## 5. Compute ledger

- Box: Vast.ai RTX 4090 (instance 45770673, California, $0.29/hr),
  `pytorch/pytorch:2.7.1-cuda12.8` + `fairchem-core 2.21.0` (torch 2.8.0+cu128).
  Two earlier boxes were destroyed: 45733809 (stuck ~20 min pulling the image) and
  45736612 (crashed in 6 s on a missing `pandas` — the runner's `hea_oer` import pulls
  `pipeline.py`→pandas; fixed in `src/dft/setup_r0_box.sh` + a post-extract import-chain check).
- Two false starts cost ~zero compute — both died at import/name-resolution before the
  model downloaded. Real run: 8 systems × 4 jobs × up to 3 heads of 18-atom MLIP
  relaxations; well under $1.
- HF access: fresh READ token `sts-r0-uma-box` minted 2026-07-24 (gated
  `facebook/UMA` checkpoint access verified, HTTP 200). Old flagged token
  (`hf_…qBUA`, docs/23 §9) still pending deletion — one manual click, owner action.

## 6. Note for the record

A concurrent session holds a second Vast.ai box (45678136, RTX 3090) running a live
`pxrd-flow` conditioned-training job. It was inspected read-only and left untouched;
combined burn of the two boxes against the remaining credit is the reason this campaign
destroys its box immediately on completion.
