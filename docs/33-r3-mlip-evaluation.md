# 33 — R3: the screener already exists, and it found bugs in our reference

Status 2026-08-01: baselines complete; three DFT repair jobs running (§5). The
fine-tune itself is **not** started, deliberately — §4 explains why it would have
baked in a known-bad reference point.

Companions: [`30`](30-qc-audit-and-r1-campaign.md) (QC gate), [`32`](32-anchor-gate-verdict.md)
(anchor verdict and the tier's resolution), `src/dft/{e0_stage0,mlip_eval,adsorbate_qc}.py`.

## 1. Stage 0 closed analytically: E0 refitting is a no-op

The plan budgeted a free control before paying for a fine-tune — refit the per-element
reference energies and see how much disagreement that removes. It removes none, and
the reason is structural rather than empirical.

The CHE reference is **stoichiometrically closed**. For `*OH` the adslab-minus-slab
composition difference carries exactly +1 O +1 H, and the `E_H2O − ½E_H2` reference
term carries the same, so they cancel identically; likewise `*O` and `*OOH`. The metal
coefficient cancels too, since adslab and slab hold the same metal count:

```
δΔG(*OH)  = (a_O + a_H)  − [(a_O + 2a_H) − a_H]   = 0
δΔG(*O)   = (a_O)        − [(a_O + 2a_H) − 2a_H]  = 0
δΔG(*OOH) = (2a_O + a_H) − [2(a_O + 2a_H) − 3a_H] = 0
```

Verified through the real `hea_oer.referencing` path on all 8 stored oc22 records
under a large asymmetric shift (a_M = −3.76, a_O = +2.41, a_H = −1.08 eV/atom):
**max |Δη| = 3.6e-15 eV**. Note this is stronger than a ranking invariance — Ru/Ir are
`pls = 4` while the 3d metals are `pls = 2`, so the systems *are* limited by different
steps, and each ΔG is invariant *separately*.

Three consequences:

1. Stage 0 has no informative outcome. Don't run it.
2. The oc22 ρ = −1.00 is **not** a reference-energy artefact. The entire
   composition-linear subspace of model error is projected out of the descriptor, and
   being force-free it does not move geometries either.
3. **The R3 gate must be the CHE observable, not energy MAE** — E0 alone can cut
   total-energy MAE a long way while leaving every η identical.

Point 2 has a second, larger use: it makes a foundation model on a *different
functional with a different energy zero* directly comparable to our PBE+U numbers with
**no alignment applied**. Fitting a shift first would be fitting noise.

## 2. Two foundation models rank rutile OER out of the box

Single-point on the DFT-relaxed geometries of the five QC-passing metals, zero
fine-tuning, zero alignment:

| model | ρ(descriptor) | ρ(η) | 15-point ΔG MAE | signed bias |
|---|---|---|---|---|
| MACE-MPA-0 (2024) | **+1.000** (exact p = 0.017) | +0.900 (p = 0.083) | 0.264 eV | −0.258 |
| MACE-MP-0 (2023) | +0.900 | +0.900 | 0.336 eV | **+0.316** |
| UMA-oc22 | — | **−1.00** | — | — |

Different vintages, different training sets, **opposite sign of systematic bias**, both
strongly positive. Not a lucky checkpoint.

So docs/29's "no out-of-box head ranks rutile OER" was really **"no UMA head does"** —
only oc20/oc22/oc25 were ever tested. That is a meaningful narrowing of the R0 claim
and it should be stated that way from here on.

MPA-0's single η ranking error is Ru vs Ir — the pair docs/32 measured as a **6 mV tie**
in our own DFT, i.e. the one pair the reference cannot resolve. Its Ru < Ir also matches
literature (0.37–0.42 vs 0.54–0.58), where our DFT marginally inverts them.

## 3. The like-for-like test broke, and that is the real finding

The stored UMA records come from UMA **relaxing** each structure itself (16–52 optimiser
steps in their `qc` blocks). A single-point on DFT-relaxed geometry is the easier task —
it hands the model the answer to the geometry half. Running MACE the way UMA was run
(same `FixAtoms`, fmax = 0.05 eV/Å ≈ the DFT `forc_conv_thr` of 2e-3 Ry/au):

| | single-point | model-relaxed |
|---|---|---|
| ρ(η) | +0.900 | **−0.100** |
| ρ(descriptor) | +1.000 | +0.700 |
| 15-point ΔG MAE | 0.264 eV | 0.339 eV |

The entire degradation is **one structure**. Per-metal ΔG_O shift on relaxation:

```
Cr  -1.013   <<<
Mn  -0.069
Fe  -0.011
Ru  +0.079
Ir  +0.019
```

`report()` now requires an explicit `mode` string so a single-point run can never be
recorded as a relaxed one.

## 4. Chasing that outlier found two defects in our own DFT reference

**Cr_slab/s0_O — a trapped relaxation.** Not a rearrangement: the adsorbate moves
0.139 Å and the slab a maximum of 0.269 Å. The bond goes **2.016 Å → 1.609 Å**, worth
1.06 eV. The DFT trajectory shows why:

| system | steps | M–O start | min reached | final |
|---|---|---|---|---|
| Fe | 38 | 3.091 | 1.769 | 1.774 |
| Ir | 34 | 3.090 | 1.619 | 1.767 |
| Mn | 34 | 3.064 | 1.638 | 1.671 |
| Ru | 27 | 3.089 | 1.618 | 1.698 |
| **Cr** | **28** | **3.069** | **2.016** | **2.016** |

Every other metal explores 1.62–1.83 Å on the way down. Cr stalls at ~2.03 Å and never
goes below. Its run is force-converged with a final energy change of 5e-4 eV — a genuine
stationary point, almost certainly not the right one. 2.016 Å is also long for a
terminal chromyl Cr=O and 0.25 Å *longer* than IrO₂'s, which is backwards for 3d vs 5d.

**Mn_slab/s0_OOH and Fe_slab/s0_OOH — never adsorbed.** "Converged" in 2 and 13 ionic
steps with the `*OOH` 3.83/3.95 Å from the metal and 2.15/2.20 Å above the slab; nearest
*anything* is 3.4–4.5 Å, so it is not bound to an alternative site either. A desorbed
molecule has no forces on it, so BFGS stops immediately. The O–H is stretched to
1.164/1.180 Å against 1.026 for Ru — the signature of a barely-moved builder geometry.

Their ΔG_OOH exceed the 4.92 eV total, giving a **negative fourth CHE step** —
thermodynamically impossible for a real OER intermediate. They appear to obey the
universal scaling relation, but that is coincidence: `E_adslab` contains a slab that
never relaxed, which inflates ΔG_OOH by a metal-dependent amount (and explains why Mn
and Fe differ by 0.23 eV when a genuinely desorbed molecule would give near-identical
values).

**`qe_qc` is blind to all of this by construction** — every check in it is numerical
(SCF converged, forces small, an energy exists). New `src/dft/adsorbate_qc.py` checks
chemistry instead: bound-adsorbate distance, cross-metal bond outliers, and the
ΔG₄ > 0 thermodynamic floor. It flags all three, and independently reproduces the three
already-POISONED structures (Cu/s0_OOH, Ni/s0_O, Ni/s0_OOH) from geometry alone.

This is why the fine-tune has not started: training against a reference with a known-bad
point would bake the error in, and the gate is a rank correlation *against that
reference*.

## 5. Repair jobs (running)

Instance 46548182, $0.21/hr, 20 ranks each. All five pseudopotential MD5s verified
identical to the 2026-06/07 archive, and only `ATOMIC_POSITIONS` differs from the
original inputs, so the new energies are directly comparable to each metal's existing
CHE chain.

| job | change | decides |
|---|---|---|
| `Cr_slab/s0_O` | restart at Cr–O 1.609 Å (was 2.016) | If DFT climbs back, the original stands and MACE is wrong. If it stays short and lower, **η(Cr) = 1.726 V is superseded**. |
| `Mn_slab/s0_OOH` | `*OOH` bound at 2.076 Å (was 3.83) | Whether a cus-site minimum exists at all. |
| `Fe_slab/s0_OOH` | same (was 3.95) | same. |

**Honest caveat.** MACE does not keep the Mn/Fe `*OOH` bound either: from 3.83 Å it
relaxes to 3.42, and from the transplanted 2.076 Å back out to 2.54, gaining ~0.25 eV
both times. Two very different starting points reach the same weakly-bound region, so
`*OOH` may genuinely bind weakly on MnO₂/FeO₂(110). That is **not** the claim being
tested. The claim is narrower: a run that stopped after 2 and 13 ionic steps at a
barely-moved builder placement never located any minimum. DFT gets to find its own.

## 6. What this does to the plan

- The screening tier may be **free**. If MACE-MPA-0 survives on a repaired reference,
  R3's question changes from "fine-tune until something works" to "does fine-tuning on
  864 frames beat a foundation model that already works, and is that worth $1.9?"
- If Cr's `*O` is confirmed wrong, **η(Cr) = 1.726 V is superseded** and the DFT ranking
  changes at the top. Since UMA-oc22 put Cr at 0.690 V, part of R0's ρ = −1.00 may be
  our reference rather than UMA. Hypothesis, pending §5 — but it must be checked before
  the R0 negative is written up as settled.
- The bottleneck has moved from model quality to **reference quality**, which argues for
  spending remaining compute on DFT hygiene (docs/30 M1a/M2a, the U ladder) rather than
  on GPU fine-tuning.
