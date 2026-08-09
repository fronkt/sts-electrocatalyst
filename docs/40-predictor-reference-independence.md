# 40 — Independence of the predictor and the reference

**Date:** 2026-08-06 · **Spend: $0** · **Closes:** todo item L (docs/38 §5)
**Amends:** docs/38 §2 ("three independent routes") and §5(iii) (names the wrong metals)
**Verification:** every number below was recomputed locally on 2026-08-06 unless marked
*(external)* or *(unverified)*. Spearman *p* are exact two-sided permutation values.

---

## 1. The disclosure

The MLIP that ranks candidates and the DFT tier that scores it are **not independent**.
This is not "data leakage" in the strict sense — no test data entered any training set —
and there is no single term for it in the ML-for-materials literature. Three distinct
mechanisms are at work, each with an established name *(external)*: **selection bias in
performance evaluation** (Cawley & Talbot, *JMLR* 11:2079, 2010) for choosing the model
on the points it is reported against; **circular analysis / double dipping**
(Kriegeskorte et al., *Nat. Neurosci.* 12:535, 2009) for reference geometries proposed by
the model under test; and the **reference-level ceiling** (Morrow, Gardner & Deringer,
*J. Chem. Phys.* 158:121501, 2023) for the shared DFT convention.

Ordered by exposure to the headline claim.

### 1.1 Selection on the target — the tier that validates the model is the tier that chose it

`screen_mace.dft_tier()` calls `eta_bounded.reference_tier()`, the identical call
`parity_matched.py` makes. Verified: `results/r4_validate.json`'s `dft` block is
**element-for-element identical** to `reference_tier()` — Cr 0.4907, Co 0.5440,
Ir 0.7806, Ru 0.7868, Mn 0.8917, Ni 1.0836, Fe 1.2631 V. MACE-MPA-0 was itself selected
on this tier (docs/33 §2), and docs/34–35 bought Ni and Co to raise its *n*.

So docs/35 (MAE 0.172 V), docs/36 (0.130 V) and docs/38–39 (MACE 0.173 V, omat 0.125 V)
are **three predictor-side protocols against one target — seven distinct DFT η values,
not twenty-one.** Held-out DFT points in the entire project: **zero.**

> **docs/38 §2's "MACE now meets the gate by three independent routes" is overstated and
> is corrected there.** The three routes vary only the predictor.

One real defence, verified rather than assumed: the screen's cell genuinely differs — the
DFT slabs are `supercell=(1,1)`, 18 atoms; the screen validation runs `supercell=(2,2)`,
72 atoms (`r4_validate.json`). It is not a pure re-score, and it does exercise the builder
and the multi-start.

**To break it:** one new metal computed at DFT and pre-registered before any model is
scored on it. Cu already sits in `RUTILE_AC` and carries no Hubbard U. That converts
"zero held-out points" into "one" — a categorical change in what the report may claim.

### 1.2 The Cr `*O` basin came from MACE, and both models' significance rests on it

`runs/Cr_slab/s0_O.in` is position-for-position identical (**rms 0.000000 Å**) to
`data/fix_geoms/Cr_slab_s0_O.mace.xyz`, a MACE-MPA-0 relaxed geometry. Cr is `pls = 3`,
so η = ΔG_OOH − ΔG_O − 1.23 depends on that state directly.

| Cr η set to | MACE n=7 | omat n=7 | MACE n=5 | omat n=5 |
|---|---|---|---|---|
| 0.491 (repaired, current) | +0.857, p 0.0238 **MET** | +0.964, p 0.0028 **MET** | +0.900, p 0.0833 | +1.000, p 0.0167 **MET** |
| 1.726 (pre-repair) | +0.107, p 0.8397 | +0.464, p 0.3024 | −0.100, p 0.9500 | 0.000, p 1.0000 |

**Both models, both cuts, fail without this one MACE-supplied basin.** docs/38 §5(iii)
names Ni and Co and **does not name Cr. Cr is the load-bearing case.**

**Two things cut the other way and must be said in the same breath.** First, the
reversion is **not a legitimate alternative hypothesis**: 1.726 V came from a *trapped*
stationary point at Cr–O 2.016 Å, and the restart converged **1.396 eV lower** at
1.572 Å. A lower minimum is more correct whoever proposed it, and DFT computed its own
energy from a 1.609 Å start. The table above measures **how load-bearing** the point is,
not that the current value is doubtful. Second, seeding a DFT restart from an MLIP
minimum is a named, peer-reviewed protocol — AdsorbML's ML+RX (Lan et al.,
arXiv:2211.16486; *npj Comput. Mater.* 9:172, 2023) *(external)*. The asymmetry we own is
that AdsorbML scores against a densely multi-start-searched DFT reference and **we have
none: nothing except MACE ever proposed the 1.572 Å basin.**

**To break it:** an independent DFT multi-start on Cr `*O` reaching ≤1.572 Å from a
non-MLIP start.

### 1.3 Ni's η rests on a seeded state; Co's does not — docs/38 §5(iii) overstates Co

Measured against the archived MACE geometries, atom by atom:

| input | rms Δ vs MACE | seeded? |
|---|---|---|
| `Cr_slab/s0_O.in` | 0.000000 Å | **yes** |
| `Ni_slab/s0_O.in`, `s0_OH.in` | 0.000000 Å | **yes** |
| `Co_slab/s0_O.in` | 0.000000 Å | **yes** |
| **`Co_slab/s0_OH.in`** | **0.502 Å** (max 1.739) | **no** |
| `Fe_slab/s0_OOH.in`, `Mn_slab/s0_OOH.in` | 0.690 / 1.071 Å | no |

Ni is `pls = 1`, so η = ΔG_OH − 1.23 rests on the MACE-seeded `s0_OH`. **Co is `pls = 1`
and its `s0_OH` is not seeded, so Co's η value does not depend on a MACE-supplied basin**
— what does depend on it is Co's presence in the tier at all, since the bounded identity
needs ΔG_O.

The leave-one-out spectrum sharpens this and is published rather than the best cut:

| dropped | MACE ρ (p) | omat ρ (p) |
|---|---|---|
| Cr | +0.771 (0.1028) ✗ | +1.000 (0.0028) ✓ |
| Fe | +0.771 (0.1028) ✗ | +0.943 (0.0167) ✓ |
| Mn | +0.829 (0.0583) ✗ | +0.943 (0.0167) ✓ |
| Ni | +0.829 (0.0583) ✗ | +0.943 (0.0167) ✓ |
| Co | +0.886 (0.0333) ✓ | +1.000 (0.0028) ✓ |
| Ir | +0.886 (0.0333) ✓ | +0.943 (0.0167) ✓ |
| Ru | +0.943 (0.0167) ✓ | +0.943 (0.0167) ✓ |
| | **MET on 3 of 7** | **MET on 7 of 7** |

**MACE's significance rests on Ni, not on "Ni and Co"** — dropping Co *improves* it.

### 1.4 The shared PBE+U convention, which `omat` does **not** break

`qe_slab.ELEMENTS` applies Cr 3.7, Mn 3.9, Fe 5.3, Co 3.32, Ni 6.2 eV and zero for
Cu/Ru/Ir. Read locally from `pymatgen/io/vasp/MPRelaxSet.yaml`, `INCAR.LDAUU['O']` =
{Co 3.32, Cr 3.7, Fe 5.3, Mn 3.9, Mo 4.38, Ni 6.2, V 3.25, W 6.2}, with Cu, Ru and Ir
**absent**. Every value matches and our three zeros match three absences.

OMat24 (arXiv:2410.12771 §4.2) *(external)*: "…PBE with Hubbard U corrections for oxide
and fluoride materials containing Co, Cr, Fe, Mn, Mo, Ni, V, or W, **following Materials
Project defaults**," with "VASP input sets … generated using the **MPRelaxSet** class."
MACE-MPA-0 trains on MPtrj + sAlex; UMA's `omat` head on OMat24. **Independence gained on
the U axis by switching MACE → omat is zero.**

**Five of seven tier metals carry U and two carry none, and that partition is identical
on both sides.** It is the same partition docs/35 §5 flags as the suspect for Cr and Co
sitting below both noble anchors.

Two limits on how far this may be pushed. What is shared is the **convention, not the
implementation** — our reference is Quantum ESPRESSO with SSSP USPP/PAW pseudopotentials
against VASP PAW corpora, and identical U_eff under different codes and different Hubbard
projectors is not identical energetics. And the best-quantified form of this error, a
per-element energy offset, is **projected out of our observable exactly**
(`e0_stage0.py`, max |Δη| = 3.6 × 10⁻¹⁵ eV). That bounds only the composition-linear
subspace; the residual is a U-distorted PES shape near the M–O bond and is
**unquantified**.

**To break it:** a predictor whose training corpus applies no U. `MACE-MATPES-PBE-0` is
released at level of theory "DFT (PBE)". Caveat: MatPES structures are seeded from
Materials Project entries, so it would break the convention coupling and not the
structural one. *(Proposal only, not run.)*

### 1.5 One shared geometry builder, whose known defect is common-mode

`qe_slab.py`'s own docstring says it: adsorbate placement is `hea_oer.surfaces_rutile`,
"same as UMA". Verified: every DFT `slab.in` reproduces
`build_rutile110_hea(comp, supercell=(1,1), seed=0)` to **max |Δr| = 0.000000 Å on all
seven metals**. The builder measures adsorbate height from the slab's topmost atoms —
the bridging-O rows on rutile(110) — so all 21 adsorbate starts begin **3.064–3.141 Å**
from the cus metal, past our own 3.00 Å desorption cut.

That one defect produced four wrong DFT structures **and** the desorbed `*OOH` in every
matched MLIP run. Predictor and target begin from the same defective geometry, so their
errors are positively correlated by construction, and **correlated failure inflates
apparent agreement rather than testing it.**

### 1.6 Smaller contacts, stated for completeness

- **Shared CHE constants and gas references.** Both sides use the same ZPE−TΔS constants
  (OH 0.35, O 0.05, OOH 0.40 eV), G_TOTAL 4.92, U_EQ 1.23, and a 12 Å gas box; on the DFT
  side **one H₂O and one H₂ calculation underlie all seven target points**. Any error
  there is common-mode. This limits what the agreement *means* — the parity is
  structurally blind to the thermochemistry both sides assume — rather than biasing
  either number. It cannot be broken by agreement, only bounded by a ZPE sensitivity
  sweep, which does not exist in the repo.
- **Shared lattice table, three entries invented.** `RUTILE_AC` concedes Fe, Co, Ni and
  Cu are "model values on the rutile trend". QE runs `relax` (ions only, never
  `vc-relax`) and the MLIP path relaxes positions only, so **neither side can correct the
  cell**. **UNQUANTIFIED.** The exposures compound: Fe, Co and Ni sit at invented cells,
  all three carry U, and Ni and Co additionally carry seeded restarts and bounded η.
- **The bounded-η window is calibrated on the tier it extends.**
  `OBSERVED_DG_OOH = (3.652, 4.942)` comes from the same five chain metals, and its upper
  edge is a repaired structure. Co's window closes with only **+0.214 eV** of margin.
  What closes Co rigorously is a partial relaxation bounding ΔG_OOH ≤ 4.571 eV, and that
  partial ran from a MACE-seeded start. The upper-bound *logic* survives any starting
  point — a run stopped above its own minimum still bounds the minimum from above — so
  the rigour is genuine; the **tightness** came from MACE's basin. Ni is genuinely safe
  (window width 4.263 eV).
- **Adsorbate-QC thresholds were revised in a campaign the MLIP corroborated.** Weaker
  than "set from MLIP results" and stated that way: in each case the falsifying evidence
  was a DFT run, with MACE cited as corroboration — but that DFT run was itself part of
  the MACE-seeded repair campaign. Measured exposure: MACE's Cr/Mn/Fe `*OOH` sit
  13–74 mÅ past the 3.00 Å cut, so a 3.10 Å cut would give MACE zero desorptions — with
  **zero η impact**, since all three are `pls = 2`.
- **Target-internal, not a predictor contact:** `make_fix_inputs.py` rebuilt Mn's and
  Fe's `*OOH` by transplanting Cr's DFT-relaxed adsorbate, so three of five chain
  ΔG_OOH values share one geometric ancestor while the Spearman treats them as
  independent. η impact zero (both `pls = 2`).

### 1.7 Closed

The predictor was once scored on the target's own relaxed geometries —
`evaluate_relaxed` reads DFT final frames, billed "like-for-like" in docs/33 §3.
**Closed** by `mace_uma_protocol.py`: `m_o_start` across all 21 states in both matched
runs is 3.064–3.141 Å, the builder placement. Measured cost of the old coupling: **≤5 mV
on every tier metal.**

## 2. What the `omat` result changes

**It repairs checkpoint non-independence and bears directly on the seeding coupling. It
does not touch the DFT convention.**

**Repaired.** `uma-s-1p2/omat` is a different vendor, architecture and corpus, and
decisively — **it seeded none of the DFT restarts.** From unseeded builder starts
(3.06–3.14 Å) it independently reaches every basin the DFT had to be seeded into:
Cr `*O` 1.583 vs DFT 1.572 Å, Ni `*O` 1.795 vs 1.775, Ni `*OH` 1.856 vs 1.838,
Co `*O` 1.627 vs 1.650, Co `*OH` 1.788 vs 1.796 — **max |Δ| = 0.023 Å across all five**
*(from the workflow's measurement; the η-level numbers are verified)*. Its gate does not
rest on the seeded metals: n = 5 ρ +1.000 (p 0.0167) and **7 of 7 leave-one-out cuts
MET**. A model that touched none of the seeding confirms the basin choice. Coupling
1.2/1.3 is a real provenance defect, but **it did not manufacture the answer.**

**Not repaired.** OMat24 applies the MP U table to the MP element list via MP's own
pymatgen input-set class. Worse for independence, OMat24 §4.1 states its initial
structures were "obtained by randomly sampling the relaxed structures in the **Alexandria**
PBE bulk materials dataset" — and sAlex, the second half of MACE-MPA-0's training set, is
a filtered subsample of that same Alexandria corpus. One OMat24 subset was additionally
filtered by "an EquiformerV2 model trained on the **MPtrj** dataset" *(external, quoted
from arXiv:2410.12771 §4.1)*. So there is a live MPtrj → OMat24 channel.

**Unsettled.** Whether the shipped `uma-s-1p2` `omat` head carries MPtrj + sAlex
fine-tuning is **not established** *(unverified)*. UMA Table 10 lists eight training
datasets for UMA-S-1.2 with neither among them, which is good evidence against, but the
same appendix defers full 1.2 details. **If the shipped head is MPtrj-fine-tuned,
omat's corpus independence collapses and §2 must be rewritten. Re-check before the
mid-October freeze.**

**A claim we deliberately do not make.** `omat` desorbs `*OOH` on exactly the five
U-corrected metals (3.778–4.012 Å) and holds on exactly the two zero-U metals (1.953,
1.928 Å); MACE desorbs on {Cr, Mn, Fe}, a strict subset. The chance of that partition
falling entirely inside the U-set is 1/C(7,5) = **0.048**. This is a striking coincidence
**in our own artifacts and is reported as exactly that.** It is **not** evidence we have
reproduced the selective-U pathology of Warford, Thiemann & Csányi (*Mach. Learn.: Sci.
Technol.* 7:035033, 2026) *(external)*: that paper tests elemental-metal slabs and
metal|oxide interfaces, contains no rutile and no OER chemistry, never evaluates UMA, and
its own mechanism predicts the fully-oxidised limit is **exempt**. The direction is also
partly real chemistry — DFT itself gives weakly bound 3d `*OOH` (Cr 2.076, Mn 2.480,
Fe 2.552 Å) against Ru 1.947 and Ir 1.912 Å. Both models exaggerate a real trend past the
cut, and **our reference cannot separate artifact from chemistry because it shares the
convention.**

## 3. What we already do about it

- **Pre-registration** — the `omat` criterion was frozen in commit `e084af8` before the
  run. Closes researcher degrees of freedom on that test; does **not** close the
  shared-target problem, since it was pre-registered against the same seven points.
- **Both cuts and the full deletion spectrum**, published rather than the best cut. This
  is jackknife influence diagnostics — the honest small-*n* substitute for a held-out
  set, not a replacement for one.
- **A matched protocol** — one runner, calculator swapped, so comparisons are matched by
  construction rather than by discipline.
- **Adsorbate QC that is allowed to condemn our own result** — `parity_matched.json`
  publishes `eta_contaminated: ["Cr"]` against the model that wins.
- **Provenance in artifacts, not memory** — `_PROVENANCE` blocks and `SUPERSEDED_BY`
  stamps rather than deletions.
- **A proved closure of the per-element error channel** — claimed exactly that far and
  no further.
- **A second predictor family** — seeding nothing, with the limits in §2.

## 4. The one sentence, if the report carries only one

> The seven DFT overpotentials both foundation models are ranked against are the same
> seven that selected them; four of the underlying relaxations were restarted from
> MACE-MPA-0's own minima — including the Cr `*O` state whose reversion drops both models
> below significance — and every training corpus behind both models applies the identical
> Materials Project selective Hubbard U table our own reference uses, so **this parity is
> a reproducibility check within one level of theory, not independent validation of it.**
