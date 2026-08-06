# 41 — Pre-registration: diagnosing the anchor-gate failure

**Status:** frozen before any probe number exists. Written 2026-08-06.
**Depends on:** docs/32 (the failed gate), docs/22 (the protocol spec it departs from),
docs/35 (the n=7 tier), docs/40 (predictor/reference coupling).
**Code:** `src/dft/probe_decks.py` (build), `src/dft/probe_eta.py` (score).

This document states the acceptance criteria **before** the calculations are run, so
that the outcome cannot be re-interpreted after the fact. docs/39 did this for the
`omat` head and the result was that R0's headline claim was falsified by its own
test; the same discipline applies here.

---

## 1. What actually failed

docs/32 records the failed external gate:

| anchor | η computed | literature | error |
|---|---|---|---|
| RuO₂(110) | 0.787 V | 0.37–0.42 V | **+0.39 V** |
| IrO₂(110) | 0.781 V | 0.54–0.58 V | **+0.22 V** |

Both errors are positive, and the earlier working hypothesis — carried in the tracker
and in conversation — was that this is one **tier-wide systematic offset**: some shared
reference, coverage or electrostatic error pushing every η up together.

**That hypothesis is wrong, and the tier's own numbers refute it.**

## 2. The decomposition that refutes it

A CHE overpotential is built entirely out of *differences*. Decomposing both anchors
against the two literature invariants — the Man (2011) universal scaling band
ΔG(*OOH) − ΔG(*OH) = 3.2 ± 0.2 eV, and the volcano apex ΔG(*O) − ΔG(*OH) ≈ 1.60 eV:

| metal | ΔG_O − ΔG_OH | vs apex 1.60 | ΔG_OOH − ΔG_OH | vs band 3.2 | η | pls |
|---|---|---|---|---|---|---|
| Ru | 1.163 | **−0.437** | 3.180 | −0.020 ✅ | 0.787 | 3 |
| Ir | 1.642 | +0.042 ✅ | 3.652 | **+0.452** | 0.781 | 3 |
| Cr | 1.560 | +0.040 ✅ | 3.281 | +0.081 ✅ | 0.491 | 3 |
| Mn | 2.122 | +0.522 | 3.034 | −0.166 ✅ | 0.892 | 2 |
| Fe | 2.493 | +0.893 | 2.711 | −0.489 | 1.263 | 2 |

The two anchors fail in **completely different coordinates**:

- **Ru is broken only in the descriptor.** Its *OOH scaling is essentially perfect
  (3.180 against a band centred on 3.2). Its ΔG(*O) sits 0.437 eV too low relative to
  ΔG(*OH) — *O is bound too strongly. If the descriptor alone sat at the apex, ideal
  scaling gives η = 1.60 − 1.23 = **0.37 V**, which is the literature value exactly.
  The entire RuO₂ error is one number.
- **Ir is broken only in the *OOH scaling.** Its descriptor is essentially at the apex
  (1.642 against 1.60). Its ΔG(*OOH) sits 0.452 eV too high. η is set by
  ΔG₃ = ΔG_OOH − ΔG_O = 2.011 eV.

Both then land at η ≈ 0.78 V by coincidence, through different steps of the same
mechanism. **The shared sign of the error is not evidence of a shared cause.**

### 2a. This rules out the gas references analytically

From `hea_oer.referencing._REF_COEFFS`, a shift in either gas reference propagates in a
fixed pattern:

| perturbation | ΔG_OH | ΔG_O | ΔG_OOH | ⇒ (O−OH) | ⇒ (OOH−OH) |
|---|---|---|---|---|---|
| E(H₂O) → +d | −d | −d | −2d | **0** | −d |
| E(H₂) → +e | +½e | +e | +3⁄2e | +½e | +e |

An H₂O error **cannot move the descriptor at all**, so it cannot be Ru's problem. And
no single scalar fixes both anchors:

- the H₂O shift that pulls Ir onto the scaling band (d = +0.452 eV) drives Ru's
  ΔG_OOH − ΔG_OH from 3.180 to **2.728**, breaking a metal that was correct;
- the H₂ shift that moves Ru's descriptor to the apex (e = +0.873 eV) drives Ru's
  ΔG_OOH − ΔG_OH to **4.053** and Ir's descriptor to **2.078**, breaking both.

The same argument disposes of any other single uniform correction, including a uniform
solvation stabilisation of the H-bearing adsorbates: stabilising *OH by ~0.44 eV fixes
Ru's descriptor and simultaneously pushes Ir's to 2.08, past the apex and further from
experiment. **There is no one-parameter repair.**

### 2b. A separate signature on Ir

ΔG(*OH) on Ir is **−0.0005 eV** (full precision; the leading zeros are real, not a
placeholder). In the CHE construction that means the bare cus site is in equilibrium
with H₂O/H₂ at U = 0 V — the surface is unstable to hydroxylation at *any* potential,
so the bare cus site is not the resting state and referencing every ΔG to it is
referencing to a state that does not exist under operating conditions. This is
independent evidence for the coverage / surface-Pourbaix hypothesis, and it is specific
to Ir rather than tier-wide.

### 2c. Two independent MLIPs reproduce both anomalies — so the numerics are exonerated

This is the strongest constraint available, it costs nothing, and the data was already
in `results/r5_matched_protocol.json` and `results/r5_matched_omat.json` (docs/38's
matched-protocol run, all states converged, sensible M–O distances, independent gas
references):

| | ΔG_O − ΔG_OH (apex 1.60) | | ΔG_OOH − ΔG_OH (band 3.2) | |
|---|---|---|---|---|
| | **Ru** | **Ir** | **Ru** | **Ir** |
| QE PBE(+U), this project | 1.163 | 1.642 | 3.180 | **3.652** |
| MACE-MPA-0 | 1.206 | 1.495 | 3.082 | **3.641** |
| UMA `omat` | 1.248 | 1.589 | 3.357 | **3.651** |
| miss vs literature | **−0.35 to −0.44** | ok | ok | **+0.44 to +0.45** |

All three methods reproduce Ru's descriptor deficit and Ir's scaling violation. The
three Ir values agree to **11 meV**.

What the three share: the 1×1 rutile(110) builder geometry, the bare-cus-site
reference, no solvation, no coverage treatment, the CHE construction, and PBE-level
physics. What they do **not** share: the DFT engine (QE here, VASP-derived training
data there), pseudopotentials, Hubbard U, k-points, cutoffs, smearing, convergence
thresholds, gas references — and, decisively, **long-range electrostatics, which the
MLIPs do not have at all.** MACE and UMA are short-range models with a ~6 Å cutoff:
they carry no dipole term and cannot see the cell height.

Therefore:

1. **The whole "QE numerical setup" family is ruled out** — pseudopotentials, k-points,
   cutoffs, smearing, Hubbard implementation, convergence thresholds. Two models with
   none of those reach the same numbers.
2. **The missing dipole correction cannot be responsible for a 0.4 eV error.** If it
   were, models with *no electrostatics whatsoever* could not agree with this DFT to
   11 meV on the very quantity that fails.
3. **Vacuum size cannot be responsible** for the same reason: it is invisible to a
   6 Å-cutoff model.
4. The anomaly lives in what the three **do** share: the structural and physical model
   — bare-cus reference, 1 ML coverage, no solvation, PBE. This is the same place
   §2b's ΔG_OH(Ir) = −0.0005 eV points.

**This converts P2 and P3 from open questions into pre-registered predictions.**
Both are predicted **NULL** (|Δη| < 50 mV) before running, on the argument above. If
either comes back ≥ 100 mV, the argument in this section is wrong and must be
retracted — which is exactly why the probes are still worth their ~$3.

The honest reading of the anchor-gate failure is therefore *not* "the DFT has a bug."
It is: **a bare, unsolvated, full-coverage rutile(110) cus site at PBE level puts
RuO₂ 0.4 V from experiment, and three independent methods agree on that number.**

### 2d. η is a positively biased statistic, and that alone predicts a positive miss

The construction in `hea_oer/descriptors.py` imposes `G_TOTAL = 4.92` by defining
ΔG₄ ≔ 4.92 − ΔG_OOH. The four rungs then telescope:

```
ΔG₁ + ΔG₂ + ΔG₃ + ΔG₄ = ΔG_OH + (ΔG_O−ΔG_OH) + (ΔG_OOH−ΔG_O) + (4.92−ΔG_OOH) ≡ 4.92
```

verified to 8.9e-16 over 20,000 random inputs through the real code path. So the sum is
an **identity**, the mean rung is pinned at exactly 1.23 eV, and

> **η = max(ΔG_i) − mean(ΔG_i)**

η is therefore a *max-minus-mean* statistic over four numbers of fixed sum. It is ≥ 0
by construction, equal to zero only when all four rungs are degenerate — which is the
definition of an ideal catalyst — and **any error, of any origin, in any direction,
inflates it.** "Both anchors miss positive" is not evidence of a shared physical
mechanism. It is the expected behaviour of this estimator.

Monte Carlo, adding Gaussian error of s.d. σ to the three adsorbate free energies of a
ladder with **true η = 0.370 V** (a literature-consistent RuO₂: descriptor 1.60,
ΔG_OOH−ΔG_OH 3.20) and reading off the computed η:

| σ (eV) | 0.10 | 0.20 | 0.30 | 0.35 | 0.40 |
|---|---|---|---|---|---|
| E[η] iid errors | 0.468 | 0.566 | 0.671 | 0.725 | **0.783** |
| bias | +0.098 | +0.196 | +0.301 | +0.355 | **+0.413** |
| with ρ(OH,OOH)=0.8, ρ_O=0.5 | +0.076 | +0.152 | +0.227 | +0.267 | +0.306 |
| with ρ(OH,OOH)=0.95, ρ_O=0.8 | +0.049 | +0.098 | +0.148 | +0.173 | +0.200 |

At σ ≈ 0.35–0.40 eV — an ordinary GGA error bar for oxide adsorption energies — the
**expected** computed η for a true-0.37 V catalyst is 0.73–0.78 V. The measured value
is **0.787 V**. The sampling s.d. of η at that σ is ~0.34–0.38 V, which is also why the
6 mV Ru/Ir "inversion" is meaningless, as docs/32 already concluded on other grounds.

The correlation rows are the honest caveat and they matter: scaling relations correlate
the errors on *OH and *OOH, and under strong correlation the bias explains only
~0.10–0.20 V of the gap rather than all of it. **This is a range, not a closed case.**
What it does establish is that a substantial, previously unaccounted-for part of both
anchor misses is a property of the estimator rather than of the chemistry, and that no
physical mechanism needs to be found for the *shared sign*.

Two things this does **not** license:

- It does not say the physical model is fine. §2c still points at coverage / resting
  state / solvation, and the residual after the bias is exactly what those must explain.
- It does not say η is the wrong statistic for *model-vs-model* benchmarking. That was
  tested on the n=5 matched set and came out **neutral**: MAE(model−DFT) scored on η,
  on the descriptor, and on ΔG_OOH−ΔG_OH is 0.150/0.165/0.148 (MACE) and
  0.131/0.109/0.177 (UMA `omat`), with ρ differing by a single swap. The bias largely
  cancels when both sides carry it. Do not claim otherwise from this data.

## 3. Why this is good news

A diffuse tier-wide offset would be nearly undiagnosable on this budget. Two localised,
single-state errors are each testable, and §2 has already eliminated the cheapest
family of explanations analytically at zero compute cost. The remaining candidates are
all geometry/electrostatics/coverage effects, and every one of them can be probed at
**fixed geometry**, because all four states of both anchors are already relaxed.

## 4. The probe protocol

`probe_decks.py` extracts the relaxed coordinates from each production `.out`, re-emits
the deck with exactly one variable changed, and runs a single SCF step. Cost is cents
rather than dollars. This is a **leading-order sensitivity analysis**: relaxation under
the perturbation is a second-order correction and is not included. Every artifact the
tool writes carries that statement, and no output of this campaign may be described as
a relaxed result.

Variants, per anchor: `base`, `dipole`, `vac32`, `dipole+vac32`
(4 states × 4 variants × 2 anchors = **32 single points**).
U-ladder, per 3d metal (Cr, Co): `base`, `u0.0`, `u0.5`, `u1.35`
(4 states × 4 variants × 2 metals = **32 single points**).

`u0.0` emits no `HUBBARD` card at all, so that rung is genuinely plain PBE — the exact
protocol Ru and Ir ran under, which is the comparison the rung exists to make.

## 5. Pre-registered acceptance criteria

**P1 — extraction control (gating).** For every state of every anchor,
|E(`base`) − E(relaxation final)| ≤ **5 meV**. `probe_eta.py` refuses to score a batch
that fails this, and a failure voids the batch rather than being reported with a
caveat. *Rationale:* if the coordinate/cell/species/magnetisation/Hubbard round trip is
not faithful, every other variant is measuring the round trip rather than the physics.

**P2 — dipole correction.** *Predicted before running:* |Δη| < 50 mV on both anchors —
and now predicted **NULL on the independent argument of §2c**, not merely on a guess
about magnitude. A result of ≥ 100 mV falsifies §2c and that retraction must be
recorded alongside the number.
- **< 50 mV on both** ⇒ the missing dipole correction is **not** the explanation. Record
  it as a closed negative and stop citing it as a suspect.
- **≥ 100 mV on either** ⇒ it is a live contributor; docs/22's spec was right and the
  UMA-matching justification in `qe_slab.py:21-22` must be withdrawn.
- 50–100 mV ⇒ inconclusive; report as such, do not round toward either verdict.

**P3 — vacuum.** Identical thresholds to P2. Note the true image gaps on the *relaxed*
geometries are 16.57 / 15.49 / 15.94 / 14.79 Å for bare / *OH / *O / *OOH — differential
by 1.78 Å, which is the only reason this can move η at all.

**P4 — the Ru test.** Ru's failure is entirely `ΔG_O − ΔG_OH = 1.163` against an apex of
1.60. A variant counts as **an explanation of RuO₂** only if it raises that descriptor
by **≥ 0.30 eV**. A variant that changes absolute energies substantially but moves the
descriptor by less than 0.30 eV is *not* the cause, however large its effect looks.

**P5 — the Ir test.** Ir's failure is entirely `ΔG_OOH − ΔG_OH = 3.652` against a band
centred on 3.2. A variant counts as **an explanation of IrO₂** only if it lowers that by
**≥ 0.30 eV**.

**P6 — the joint criterion, declared in advance.** P4 and P5 are different quantities.
If no single variant satisfies both, the registered conclusion is that **the two anchors
are broken by two independent mechanisms**, and the project reports that finding rather
than assembling a "corrected" tier out of per-metal fixes. Choosing a different
correction for each metal after seeing the numbers is exactly the circularity docs/40
was written to catch.

**P7 — U-sensitivity (project-falsifying).** The headline result is that Cr (0.491 V)
and Co (0.544 V) beat both noble anchors, and that comparison crosses the PBE+U /
plain-PBE boundary. If η(Cr) or η(Co) moves by more than **0.15 V** across
U ∈ {0, 0.5×, 1×, 1.35×} at fixed geometry, then "earth-abundant rutiles outperform
RuO₂/IrO₂ in this tier" is **not supported by this data** and must be withdrawn, not
softened. 0.15 V is chosen as slightly under the 0.17 V differential resolution docs/32
already concedes, so the criterion cannot be met by a change the tier could not resolve
anyway.

**P8 — what will not count as evidence.** Agreement of any variant's *absolute* η with
literature, absent the corresponding descriptor or scaling movement in P4/P5. Two
errors cancelling is not a diagnosis, and the tier has enough free parameters to hit
0.40 V by accident.

## 6. Cost and order

| step | jobs | est. cost | falsifies? |
|---|---|---|---|
| P1–P3, P4/P5 probe on Ru + Ir | 32 SCF | ~$3 | no — diagnoses |
| P7 U-ladder on Cr + Co | 32 SCF | ~$4 | **yes — the headline claim** |

P7 runs **first** on the honest ordering (a step that can falsify the central claim
precedes one that only refines it), but both fit inside a single ~$25 top-up. Remaining
credit at time of writing is **$0.295**, which is less than either step; the top-up is
the blocking action.

## 7. Standing caveats

- Fixed geometry. Second-order relaxation effects are excluded by construction.
- The literature anchors in §1 are themselves a range across protocols, not a
  measurement; docs/32 already treats them as a band and this document inherits that.
- The apex value 1.60 eV and band centre 3.2 eV are Man (2011) conventions. P4 and P5
  are stated as *movements* of ≥ 0.30 eV precisely so they do not depend on the exact
  centre of either literature band.
- Nothing here touches the melt list, which remains unfrozen and Frank's decision.
