# 29 — R0: Killing the Task-Head Artifact (uma-s-1p2p1 / oc22 re-parity)

**Date:** 2026-07-24 (protocol) / 2026-07-25 (results) · **amended 2026-08-03**
**Status:** COMPLETE — **R0 gate NOT met.** The docs/26 negative result is confirmed and
un-confounded. Decision point for Frank in §7.
> ⚠ **READ §8 BEFORE QUOTING ANY ρ IN THIS DOCUMENT.** The headline "oc22 ρ = −0.80,
> strongly *anti*-correlated" was measured against a DFT reference later found to contain
> a trapped `Cr_slab/s0_O` relaxation. Against the repaired reference oc22 is
> **ρ = 0.000** (n = 5) / **+0.500** (n = 3): no rank signal, not an inverted one. The
> gate verdict is unchanged; the *shape* of the negative is not. Every UMA number below
> is as-measured and correct — only the DFT column moved.
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

> **⚠ CORRECTION 2026-08-06 (docs/38 §3).** The sentence above is true as written and
> misleading as used. Audited against the real OC22 metadata (62,331 systems, 4,286
> bulks — `oc22_metadata.pkl`, CC-BY 4.0): the 4,318 rutile count is right, but **only
> 83 of them are at (110)**, and across all of those exactly **one** carries `*OOH`.
> Restricted to this project's eight metals, rutile(110) gives 19 systems, 5 with an
> OER intermediate and **0 with `*OOH`**. Neither canonical rutile bulk — mp-825
> (RuO₂) nor mp-2723 (IrO₂) — is sampled at (110) at all.
>
> So the premise "our chemistry is *literally* the OC22 dataset" was too strong: the
> facet we model is a thin slice of OC22, and the `*OOH` leg of the CHE chain is
> essentially absent from it. This **weakens the confound hypothesis** that motivated
> R0 and correspondingly **strengthens** the R0 negative — oc22's failure is less
> surprising once the (110) coverage is known. Reproduce with
> `src/dft/oc22_coverage.py`.
>
> One live lead survives the audit: `mp-1095353` (Ir₄O₈) has 15 systems at (110)
> including **3 `*OOH`, 3 `*O`, 1 `*OH`** — a complete OER triad on one of our two
> anchors. It is a different MP entry from canonical rutile IrO₂, so its structure
> type is unconfirmed; docs/38 §5 keeps it open as the one external-validation lead
> worth the half hour it costs to settle.

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

## 4. Results — GATE NOT MET (the confound is killed; the negative result survives)

Run 2026-07-25, `uma-s-1p2`, 1705 s on the RTX 4090 (instance 45770673), all 24 relaxations
(8 systems × 3 heads) completed. QC: every relaxation converged to fmax ≤ 0.05 eV/Å **except**
two in the exploratory `oc25` leg (Fe, Mn `s0_O`), which are flagged below — those two
`oc25` endmember points are therefore not trustworthy, but `oc25` is outside the gate anyway.
Machine-readable: `runs/uma_1p2_summary.json`, per-dir `runs/<M>_slab/uma_eta_1p2_<task>.json`,
figure `docs/figs/uma_oc22_parity.{png,json}`.

**η (V) by task head:**

| Endmember | η_DFT (V) | η 1p1/oc20 (docs/26) | η 1p2/oc20 | **η 1p2/oc22** | η 1p2/oc25 |
|---|---|---|---|---|---|
| MnO₂ | 0.892 | 2.347 | 2.110 | **1.675** | 1.047 † |
| FeO₂ | 1.263 | 1.105 | 0.969 | **1.537** | 1.890 † |
| CrO₂ | 1.726 | 1.147 | 2.175 | **0.690** | 1.676 |
| NiO₂ | 1.751 | 2.382 | 1.558 | **1.114** | 1.449 |
| CoO₂ | — (excl.) | 2.389 | 0.922 | 1.042 | 0.927 |
| CuO₂ | — (excl.) | 2.418 | 3.549 | 1.959 | 1.637 |
| **RuO₂ anchor** | lit. 0.37–0.42 | — | 1.037 | **1.954** | 0.924 |
| **IrO₂ anchor** | lit. ≈ 0.49–0.62 | — | **0.520 ✓** | **2.238** | **0.567 ✓** |

† `oc25` Fe/Mn `s0_O` did not converge (fmax > 0.05) — point unreliable.

**Correlation vs DFT+U (n = 4 endmembers: Cr, Mn, Fe, Ni):**

| Variant | Spearman ρ | Pearson r | MAE (eV) | IrO₂ anchor | RuO₂ anchor |
|---|---|---|---|---|---|
| 1p1 / oc20 (docs/26 baseline) | +0.400 | −0.216 | 0.706 | — | — |
| 1p2 / oc20 | **0.000** | −0.005 | 0.538 | 0.52 ✓ | 1.04 ✗ |
| **1p2 / oc22 (pre-registered hypothesis)** | **−0.800** | −0.885 | 0.682 | 2.24 ✗ | 1.95 ✗ |
| 1p2 / oc25 (exploratory) | +0.200 | +0.486 | 0.283 | 0.57 ✓ | 0.92 ✗ |

### Verdict against the §3 gate

**oc22 gives ρ = −0.80** — not merely ~0 but strongly *anti*-correlated, worse than the docs/26
baseline it was supposed to rescue. This lands squarely on the gate's "≈0 → the negative result
is real" branch. **The docs/28 §2 hypothesis is refuted:** switching to the correct PBE+U-oxide
task head does not recover the ranking. Across the metal head (oc20, ρ=0.0), the correct oxide
head (oc22, ρ=−0.8), and the electrocatalysis head (oc25, ρ=+0.2, and QC-tainted), **no
out-of-the-box UMA head ranks rutile-MO₂(110) OER activity** against DFT+U. The docs/26
conclusion stands, now un-confounded.

### Why this is a real finding and not a pipeline bug — the anchors decide it

The RuO₂/IrO₂ anchors are the control, and they exonerate the pipeline while localizing the
failure to the oc22 *energetics*:

- The **same slab + CHE + referencing code** places the benchmark IrO₂(110) electrode at
  **0.52 V (oc20) / 0.57 V (oc25)** — both inside the literature band (~0.56 V). So the geometry,
  the CHE chain, and the per-head gas references are correct; a bug would not spare two heads
  and hit one.
- Under **oc22**, *both* anchors blow up to ~2 V and become step-4 limited, with an unphysical
  free-energy landscape (dG_OH < 0, i.e. *OH over-bound; dG_OOH ~1.5 eV, far below the ~3.5 eV
  such surfaces show). This is the oc22 head's PES on pristine dry (110) cus sites, not a
  referencing artifact (CHE differences cancel the per-head reference exactly).
- **The irony worth stating in the writeup:** the *metal*-oriented oc20 head places the
  canonical metal-oxide OER electrode (IrO₂) correctly, while the head *built for oxides*
  (oc22) does not — consistent with the Loveday/López 2026 finding that out-of-box universal
  MLIPs carry ~0.5 eV oxide-adsorption errors and that "fine-tuning is expected to be mandatory."

**Caveats kept honest:** n = 4; OC22 was trained with all atoms free while our slabs fix the
bottom half (mild OOD for oc22 specifically); oc25 assumes solvent/ions its inputs don't have
and has 2 unconverged points. None of these rescue oc22 to the gate — a +2 V anchor error and
ρ = −0.8 are not 0.2 V effects.

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

## 7. What R0 decides, and the fork for Frank

R0 was the cheap gate that determined which of two campaigns the project runs. The gate
says the un-fine-tuned model is not a usable screener for this chemistry — so the "screen
3000 compositions with UMA, DFT-calibrate the offset" funnel (docs/22) is off the table
without training. Two legitimate paths remain; this is a genuine owner decision, not a
default:

- **Path A — embrace the benchmark negative (lowest risk, STS-ready now).** The deliverable
  is docs/28 §6 finding #3/#4: *"out-of-box UMA — across oc20, oc22, AND oc25 heads — cannot
  rank rutile-MO₂ OER; the oxide-specialized head is the worst and gives unphysical anchor
  overpotentials, while the metal head places IrO₂ correctly."* This is a recognized
  contribution class (CatBench 2025; Loveday 2026), it is pre-registered and QC-audited, and
  it reads as integrity for an STS judge. Combined with the R1 volcano analysis (§4b) it is a
  complete, honest story with zero further compute. **Recommended as the floor.**
- **Path B — fine-tune, then screen (docs/28 §5/R3; single GPU-days).** The archived QE
  trajectories (commit 78396b5) are an in-domain training set already on disk. The field's
  small-data evidence (CLAM, MACE-catalysis, ~200–500 points → ρ 0.85–0.95) says a naive
  fine-tune could turn ρ = −0.8 into a usable screener. Higher upside, higher risk, and R3/R4
  spend is explicitly gated on Frank in docs/28 §7. Path A is not wasted if we do B — it
  becomes the "before" half of a before/after fine-tuning figure, which is a *stronger* paper
  than either alone.

I did not launch R3: it is a substantial new direction the plan marks owner-gated, and the
R0 outcome (embrace-negative vs invest-in-training) is a framing decision that is Frank's per
docs/25. R1's *free* reanalysis (§4b) is already done; R1's *moderate* DFT hygiene (U-sensitivity,
magnetic protocol — CPU-box-weeks) should wait until A-vs-B is chosen, since B reframes what
those re-runs are for.

## 6. Note for the record

A concurrent session holds a second Vast.ai box (45678136, RTX 3090) running a live
`pxrd-flow` conditioned-training job. It was inspected read-only and left untouched;
combined burn of the two boxes against the remaining credit is the reason this campaign
destroys its box immediately on completion.

---

## 8. Amendment, 2026-08-03 — the reference moved, so every ρ here moved with it

**Nothing measured in this document about UMA has changed.** All 24 relaxations, all
per-head η, and the anchor analysis of §4 stand exactly as written. What changed is the
DFT column they were correlated *against*.

On 2026-08-02 three structures in our own reference were found defective and re-run
(diagnosis: docs/33 §4; outcome: docs/32 §3). The consequential one is `Cr_slab/s0_O`,
force-converged at a Cr–O bond of 2.016 Å where every other metal reaches 1.67–1.77 Å.
Restarted short it converged **1.396 eV lower**, moving η(CrO₂) from **1.726 → 0.491 V**
— from the worst material in the set to the best.

Cr is one of only three 3d endmembers surviving QC, so a 1.235 V move in one of three
points does not perturb a rank correlation, it re-draws it:

| head | n = 3 (Cr, Mn, Fe) | n = 5 (+ Ru, Ir anchors) | η MAE, n=5 |
|---|---|---|---|
| oc20 | +0.500 → **−1.000** | +0.700 → **−0.300** | 0.742 V |
| **oc22** | **−1.000 → +0.500** | **−1.000 → 0.000** | 0.776 V |
| oc25 | +0.500 → +0.500 | +0.900 → **+0.400** | 0.464 V |

*(left of each arrow: as published, against the defective reference; right: against the
repaired one. No p-value here reaches significance at any n — see §8.3.)*

### 8.1 What survives, stated exactly

**Survives:** *no out-of-box UMA head ranks rutile-MO₂(110) OER activity.* The best head
against the repaired reference is oc25 at ρ = +0.400 (exact two-sided p = 0.52), and oc25
is the QC-tainted exploratory leg. The pre-registered §3 gate asked for ρ ≥ 0.8; nothing
comes near it. **The R0 verdict is unchanged.**

**Withdrawn:** the stronger claim that oc22 is *anti*-correlated — "not merely ~0 but
strongly anti-correlated, worse than the docs/26 baseline it was supposed to rescue"
(§4 verdict), and its restatement in docs/30 §7 as ρ = −1.00 that "SURVIVES and sharpens".
oc22 against the repaired reference is ρ = 0.000 at n = 5. It lands on the gate's "≈ 0"
branch, which is where the gate table already said the negative result becomes the
finding — so the conclusion arrives by the route the protocol pre-registered, rather than
by the more dramatic one we reported.

**Also withdrawn:** the §4b claim that "all four sit far out on the weak-O-binding leg"
and that this is *why* none is a good catalyst. Cr's repaired descriptor is 1.560 eV
against the Man 2011 apex of 1.60 — it is **on** the apex, step-3 limited, not out on the
weak-binding leg at 2.956. The scaling-relation motivation for the HEA thesis is intact
for Mn and Fe; it no longer describes Cr, and Cr is now the most active point we have.

### 8.2 An honest accounting of who was wrong

The oc22 head placed CrO₂ at η = 0.690 V while our DFT said 1.726 V, and that single
disagreement carried most of the anti-correlation. **The model was closer to the repaired
answer (0.491 V) than our own DFT was.** MACE-MPA-0 independently found the same short
bond and predicted η(Cr) = 0.500 V — a 9 mV error against the DFT that eventually
confirmed it. Two independent MLIPs disagreed with our reference in the same direction,
and both were right. That is the strongest evidence in this campaign that MLIP screening
has value, and it arrived as a byproduct of a negative result.

It should also be said plainly that this was found only because the R3 evaluation chased
a single outlier rather than reporting the aggregate. The QC tooling of docs/30 could not
have caught it: `qe_qc` is entirely numerical and the trapped run is a genuine, honestly
converged stationary point. `src/dft/adsorbate_qc.py` exists now to close that gap.

### 8.3 The real limit is n, and it always was

At n = 3 the only attainable |ρ| are 1.0 and 0.5, and *every* exact two-sided p is 1.000 —
no result at n = 3 can be significant in either direction. At n = 5 only a perfect
ordering reaches p < 0.05 (ρ = 1 → p = 0.017). So neither the published ρ = −1.00 nor the
corrected ρ = 0.000 was ever a *statistically* supported statement; both are descriptive.
This does not weaken the R0 negative — a screener that needs to be usable must clear
ρ ≥ 0.8, and the burden of proof there is on the positive claim — but it does mean the
campaign's binding constraint is the number of metals, not the choice of task head. That
is what `tasks/todo.md` R3 now spends on.
