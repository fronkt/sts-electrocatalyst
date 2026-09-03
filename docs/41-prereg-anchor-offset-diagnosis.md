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

### 2e. Every adsorbate in this campaign relaxed inside a mirror plane

`hea_oer.surfaces._adsorbate` defines all three OER adsorbates with **y ≡ 0**:

```python
"O"   -> Atoms("O",   [[0,0,0]])
"OH"  -> Atoms("OH",  [[0,0,0], [0.7,0,0.7]])
"OOH" -> Atoms("OOH", [[0,0,0], [1.1,0,0.9], [1.4,0,1.85]])
```

and `surfaces_rutile.add_oer_adsorbate_at` places that template at (x_cus, y_cus).
Every adsorbate therefore starts **exactly on the rutile(110) mirror plane**
y = y_cus, which is an exact symmetry of the slab. `pw.x` uses that mirror to reduce
32 k-points to 15 irreducible — and then symmetrises the forces onto it.

Measured directly from the outputs, not inferred. Maximum |F_y| on **any adsorbate
atom**, over **every** ionic step:

| run | ionic steps | max abs F_y, adsorbate | max abs F_y, any atom |
|---|---|---|---|
| `Ru_anchor/s0_OOH.out` | 68 | **0.0000000000** | 0.026079 |
| `Ir_anchor/s0_OOH.out` | 60 | **0.0000000000** | 0.049007 |
| `Ru_anchor/s0_OH.out` | 33 | **0.0000000000** | 0.047480 |
| `Cr_slab/s0_OOH.out` | 82 | **0.0000000000** | 0.021930 |

Exactly zero, to ten decimals, while other atoms in the same runs carry |F_y| up to
0.049 Ry/au. This is a symmetry constraint, not a coincidence.

**So every adsorbate relaxation in this campaign was a constrained optimisation in a
2-D (x, z) subspace.** The "textbook" convergence the anchors are credited with in
docs/32 — fmax 0.0014–0.0019 Ry/au — is convergence *inside* that constraint. The
multi-start machinery in `surfaces_rutile.adsorbate_starts` varies only the radial
M–O distance (`PULL_TO`), so it never leaves the plane either, which is exactly why
docs/38 could measure multi-start as worth ≤3 mV and conclude the starts were
adequate.

This is the same failure class that already produced the trapped Cr *O (1.396 eV
above the true minimum) and the desorbed *OOH on Mn/Fe/Ni — but worse, because a
numerical QC gate **cannot** detect it: the constrained optimum is a genuine
stationary point of the constrained problem, with genuinely vanishing forces.

MACE-MPA-0 with 16 orientational starts, at unchanged 1×1 cell and unchanged 1 ML
coverage, puts the on-record *OOH basin **0.273 eV (Ru) and 0.731 eV (Ir)** above the
global minimum. Repeating the 1×1-vs-2×1 coverage experiment with orientational
starts on both sides collapses the Ir *OOH lateral term from +0.382 to **+0.007 eV** —
i.e. what §6a attributes to coverage may be largely this trap instead. The two
candidate causes are the same size, same sign, same channel (*OOH only) and same
metal-dependence, so they are collinear in every observable currently in hand and
**only DFT can separate them.**

### 2f. η(RuO₂) ≈ 0.79 V is not anomalous — it is a named, published systematic

The framing in §1 — "the DFT failed its gate" — assumed 0.787 V was an outlier. A
literature check says it is a **known, reproducible, named** outcome of this exact
protocol. Four independent confirmations, three read in full text:

| source | protocol | η(RuO₂) |
|---|---|---|
| **Zhu et al., Nat. Commun. 14, 5365 (2023)** | VASP, PBE, PAW, 500 eV, **with** VASPsol implicit solvation | **0.81 V** (IrO₂ 1.00) |
| **Liang, Bieberle-Hütter & Brocks, JPCC 126, 1337 (2022)** | VASP PBE+U, 7-layer, 3×2 cell, **nspin = 1** | **0.63–0.73 V, pls = 3** |
| **Dickens & Nørskov, JPCC 121, 18516 (2017)** | BEEF-vdW, converged SUNCAT setup | descriptor 0.88 eV ⇒ **η ≈ 1.0 V** |
| **Briquet et al., ChemCatChem 9, 1261 (2017)** | RPBE **and** PBE across **six codes** | "RuO₂ is consistently predicted to have large overpotentials" |

Zhu et al. state it outright: *"Most of the existing DFT calculations exhibit a
systematic overestimation of the OER overpotentials for IrO₂ and RuO₂."* This
project's 0.787 V is **within 0.03 V** of a *Nature Communications* reference value
obtained with a strictly more complete protocol. And Dickens & Nørskov's own
BEEF-vdW descriptor (0.88 eV) is **further from the apex than this project's 1.163**.

The gate's reference band was also too narrow. The published DFT descriptor for
RuO₂(110) spans ~0.7 eV (0.88 → ~1.6 eV), i.e. η from ~1.0 V down to ~0.4 V for the
same material and facet. "Literature 0.37–0.42 V" is **one corner of a 0.6 V-wide
published range**, not a consensus. docs/32's clause 1 was scored against the
optimistic edge of that range.

**And the literature names the fix, in Ru's exact coordinate.** RuO₂ is
**antiferromagnetic** — Berlijn et al., PRL 118, 077201 (2017), itinerant AFM from
neutron diffraction. Liang 2022 shows spin polarisation puts a moment on the bare,
*OH- and *OOH-covered cus Ru but **not** on the already-low-spin *O one, so ΔG(*O)
rises by up to **~0.3 eV**, the descriptor moves toward the apex, and the step-3
limitation eases: AFM gives **0.41–0.49 V** against NM's 0.63–0.73 V.

`qe_slab.py:44-48` sets Ru and Ir to `U = 0, mag = 0` with the comment *"RuO2/IrO2 are
4d/5d rutile metals, itinerant and non-magnetic."* **For RuO₂ that is factually
wrong**, and it is the single best-supported candidate for the descriptor deficit
§2 localised. This campaign's signature — 0.787 V, pls = 3, nspin = 1 — matches
Liang's non-magnetic row on all three counts.

Note this also **downgrades P9**: Briquet et al. ran both RPBE and PBE across six
codes and got the RuO₂ anomaly either way, so RPBE alone is not expected to fix it.
P9 still runs (it is cheap and pre-registered) but it is no longer the leading
hypothesis. **P11 is.**

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

**P9 — RPBE vs PBE (added 2026-08-06, before any probe result existed).** The
literature overpotentials in §1 that this gate is scored against are **RPBE**
(Rossmeisl 2007, Man 2011; `docs/research/2026-07-24-methodology-survey.md` says so
explicitly for both). This campaign is **PBE**. That was never a like-for-like
comparison, and it has gone unremarked through docs/29–40. RPBE weakens chemisorption
relative to PBE by ~0.3–0.5 eV for atomic *O and only ~0.15–0.25 eV for *OH/*OOH, so
it raises ΔG_O − ΔG_OH — the exact coordinate, sign, and order of magnitude of Ru's
descriptor deficit.

*Predicted before running:* the `rpbe` variant raises Ru's descriptor by **0.2–0.5 eV**.
- Raises it by **≥ 0.30 eV** ⇒ P4 satisfied; the dominant Ru error is a
  functional mismatch between this campaign and its own reference values, not a bug.
- **< 0.15 eV** ⇒ the functional-mismatch explanation is dead and must be recorded as
  a closed negative alongside dipole, vacuum, thickness and referencing.

Two conditions on this test, both enforced in code:
1. The variant carries **its own RPBE gas references**. ΔG subtracts a·E_H₂O + b·E_H₂,
   so scoring an RPBE slab against a PBE water is a category error worth hundreds of
   meV. `probe_eta.py` refuses to score an XC variant whose own H₂O/H₂ are missing.
2. The pseudopotentials were **generated for PBE**. An RPBE single point on them is the
   standard non-self-consistent-pseudo approximation, not a clean RPBE calculation.
   It is the right first cut — PBE and RPBE differ only in the exchange enhancement
   factor — but the result must be reported with that caveat and must not be presented
   as a converged RPBE overpotential.

**P10 — the symmetry trap (added 2026-08-06, before any result existed).** Restart
*OOH on both anchors from orientations yawed 90° and 270° about the vertical axis
through the binding atom, with `nosym`/`noinv` so `pw.x` cannot symmetrise the forces
back onto the mirror plane. The binding atom is held at its production position, so
the M–O distance — the one coordinate the existing multi-start already explored — is
unchanged and only the frozen degree of freedom moves. Readout:
ΔG_OOH(off-plane) − ΔG_OOH(on record).

- **Drop ≥ 0.30 eV** ⇒ the on-record *OOH is a symmetry-trapped basin. Then the Ir
  scaling anomaly is a **basin failure**, not coverage, and — because the trap is in
  the builder, not in the anchors — **every `*OH` and `*OOH` number in the entire
  seven-metal tier is suspect**, including the Cr and Co values behind the headline
  claim. That is the single largest retraction risk currently live in the project,
  which is why this test outranks everything else in §6.
- **Drop < 0.10 eV** ⇒ the trap is exonerated at DFT level and the coverage
  attribution in §6a stands.
- MACE predicts −0.27 eV (Ru) and −0.73 eV (Ir). That prediction is on the record here
  before the DFT is run.

**P11 — spin polarisation on the anchors (added 2026-08-06, before any result).**
Re-run all four states of Ru and Ir at fixed geometry with `nspin = 2` and
`starting_magnetization = 0.5` on the metal only. *Predicted before running,* from
Liang 2022's mechanism: ΔG(*O) rises by **0.15–0.35 eV** while ΔG(*OH) and ΔG(*OOH)
move by **< 0.10 eV**, so the descriptor rises by 0.15–0.35 eV and η(Ru) falls.

- **Descriptor rises ≥ 0.30 eV** ⇒ P4 satisfied; the `nspin = 1` choice in
  `qe_slab.py:44-48` is the dominant Ru error and its stated justification must be
  retracted.
- **Descriptor rises 0.10–0.30 eV** ⇒ a major contributor but not the whole gap;
  report as partial and combine with §2f's other named ingredients.
- **< 0.10 eV, or the moment collapses to zero** ⇒ magnetism is not available at this
  geometry and the hypothesis is closed. Report the converged total magnetisation
  either way — a collapsed moment is a result, not a failed run.

Two limits on this test, both stated in advance: (i) it is **FM**, not the AFM ground
state, because AFM needs the Ru sublattice split into two species — FM captures the
*local* moment that drives Liang's mechanism, and AFM is the follow-up if FM moves the
descriptor; (ii) it is a **single point at an NM-relaxed geometry**, so it is a lower
bound on the effect — relaxation under a moment can only lower the magnetic state
further.

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

## 6a. Corrections to the record (2026-08-06)

- **The non-uniform constraint mask does not touch the anchor gate.** The claim that
  the compared metals ran different masks (11 free for Cr/Mn/Fe/Cu/Ru, 10 for Ir, 8 Co,
  7 Ni) traces to the **superseded `*.in.uma` files**, not to what `pw.x` executed.
  Read back from the ionic trajectories in `runs/Ru_anchor/slab.out` and
  `runs/Ir_anchor/slab.out`, the atoms with exactly zero displacement from first to
  last step are `[0,1,6,7,8,9,11]` in **both** anchors — byte-identical 11-free/7-fixed
  masks. Cr/Mn/Fe/Cu/Ru/Ir all ran 11 free. Only **Co (8)** and **Ni (7)** genuinely
  differ, so the mask is a live concern for those two metals and for nothing else.
- **Slab thickness and constraint are a closed negative.** Releasing all 18 atoms
  moves η(Ru) by **+0.05 V** and η(Ir) by **+0.00 V** — the wrong sign for Ru, and an
  order of magnitude short. Going 3 → 5 trilayers moves ΔG₃ by +0.006 (Ru) and −0.011
  (Ir). Scored in the P4/P5 currency the shifts are ~0.03 eV and ~0.001 eV against a
  required 0.30 eV: a null by two orders of magnitude. Do not spend on `Ru_freeall`.
- **Coverage is real, large, and metal-dependent — but it is not the shared cause.**
  In the 1×1 cell the *OOH proton reaches its own periodic image: on Ru it forms a
  near-shared-proton bond at H···O = **1.473 Å** that *over*-stabilises *OOH, while on
  Ir it points away and leaves a repulsive O···O = 2.516 Å contact. This is the
  accidental version of the Halck/Rossmeisl proton-accepting-neighbour mechanism.
  Diluting to ½ ML takes **Ir's ΔG_OOH−ΔG_OH from 3.652 to ~3.11, back inside the
  universal band** — i.e. it explains §2's Ir anomaly outright — while moving Ru's
  descriptor *further* from the apex (1.163 → ~1.01). So the coverage artifact is
  currently **masking** part of Ru's descriptor deficit rather than causing it, and
  removing it widens the failed ordering clause instead of repairing it.

Net: of the six candidate causes, four are closed negatives (dipole, vacuum,
thickness/constraint, referencing), coverage is confirmed but explains **Ir only**, and
Ru's descriptor deficit is still open — which is what P9 now tests.

## 6b. RESULTS — first returns, scored against §5 as written (2026-08-07)

Criteria below are quoted from §5 unchanged. Nothing here was revised after seeing a
number.

### GATE 1 — extraction control: **PASS**, by three orders of magnitude

| | base SCF vs relaxation final | tolerance |
|---|---|---|
| Ru `s0_OOH` | **+0.0024 meV** | 5 meV |
| Ir `s0_OOH` | **+0.0031 meV** | 5 meV |

The fixed-geometry probe reproduces the production relaxation to ~2.5 µeV. The whole
approach is validated: any shift a variant shows is the variant, not the round trip.

### P11 — spin polarisation: **REFUTED. It moves η the WRONG WAY.**

All 16 jobs converged, zero SCF failures.

| | ΔG_OH | ΔG_O | ΔG_OOH | descriptor | η |
|---|---|---|---|---|---|
| **Ru** base | 0.529 | 1.692 | 3.709 | 1.163 | 0.787 |
| **Ru** spin | 0.527 | 1.676 | 3.715 | **1.149** | **0.808** |
| **Ir** base | −0.000 | 1.641 | 3.652 | 1.642 | 0.781 |
| **Ir** spin | −0.002 | **1.467** | 3.642 | **1.468** | **0.945** |

Descriptor change: **−0.014 eV (Ru), −0.173 eV (Ir)**, against a requirement of
**≥ +0.30**. η *rises* by +0.022 V and +0.165 V. §5's third bin — "< 0.10 eV … the
hypothesis is closed" — is met, so **P11 is closed as written.**

This is not a collapsed-moment null; §5 required the magnetisation be reported either
way and moments genuinely appeared: Ru clean slab total 1.03 / absolute 3.20 µB, Ru *O
2.23 / 2.97; Ir clean slab −0.15 / 0.17 (correctly near-nonmagnetic), Ir *O 0.65 /
**2.46**. Magnetism is available — it just stabilises *O *relative to the bare slab*,
which **lowers** ΔG_O and shrinks the descriptor. That is the opposite of the mechanism
Liang reports.

**What this does and does not close.** Both limits were registered in §5 before the run:
this is **FM, not the AFM ground state**, and a **single point at an NM-relaxed
geometry**. Liang's 0.41–0.49 V comes from AFM ordering with full relaxation in a 3×2
cell at a surface-Pourbaix-selected termination. So this result closes **the cheap
version of the magnetism test**; it does not refute Liang, and it does not make
`qe_slab.py:44-48`'s "itinerant and non-magnetic" comment correct — RuO₂ is still
experimentally AFM. What it does establish is that **magnetism is not a cheap fix**, and
that the ~0.3 eV Liang attributes to it does not survive being stripped of the ordering,
the relaxation, and the coverage.

### P10 — the symmetry trap: Ru **CONVERGED at −0.082 eV → exonerated as written**

| | E | vs on-record |
|---|---|---|
| Ru `s0_OOH` on-record (in-plane) | −23333.8595 eV | — |
| Ru `s0_OOH` off-plane, yaw 90°, `nosym` | −23333.9412 eV | **−0.0817 eV** |

The trap is **real but small**. §5: "drop < 0.10 eV ⇒ the trap is exonerated at DFT
level" — met, at 82 meV. **MACE predicted −0.273 eV and overestimated the trap depth by
3.3×**, which is worth recording: the MLIP was right that a lower basin exists and wrong
about how much lower.

Consequence for Ru: only ΔG_OOH moves, so the descriptor is untouched at 1.163 and the
scaling goes 3.180 → 3.098 (still inside the band). **η(Ru) 0.787 → 0.705 V.** Closer to
literature, nowhere near it.

**The tier-wide retraction risk in §2e is therefore much reduced — for Ru.** Ir is still
relaxing (22 ionic steps, −0.180 eV and descending, fmax 0.033), already past the 0.10 eV
bin and not yet at 0.30. Ir is where the trap could still bite, and its result is
pending.

### Where that leaves the Ru descriptor deficit

Closed negatives now: dipole, vacuum, thickness/constraint, referencing, **and cheap
magnetism**. Coverage explains Ir, not Ru, and pushes Ru's descriptor the wrong way. The
symmetry trap is worth 82 meV on Ru and touches only ΔG_OOH, not the descriptor.

**Ru's −0.437 eV descriptor deficit remains unexplained by every mechanism tested.** The
untested candidates are now the expensive, structural ones §2f names: implicit or
explicit solvation, a surface-Pourbaix-correct resting state at proper coverage, AFM with
relaxation, and the functional itself. That list, and the fact that three independent
methods agree to 11 meV (§2c), is increasingly consistent with §2f's reading: this is the
field's known RuO₂ systematic, not a defect in this campaign.

## 6c. RESULTS — the queue drained (2026-08-08)

Both queues reached `QUEUE_ALL_DONE`. What follows is scored against §5 as written. Two
tests did not run at all because of harness bugs, and they are reported as *not run*, not
as nulls — a deck that aborts in 2 s is not evidence of a small effect.

### A QC bug was silently discarding every probe — found, fixed, and the fix verified

`qe_qc.scan` inferred "single point" from `n_ionic == 0`. But `pw.x` prints a forces block
whenever `tprnfor` is on, so **every** probe SCF scored `n_ionic == 1`, failed to find a
`bfgs converged` line, and was demoted to `SUSPECT` — which `trusted_energy_ev(strict=True)`
drops. The verdict now reads `calculation` from the deck instead of guessing from the
output's shape, and the free-atom force audit no longer poisons a single point (a variant
probe at coordinates relaxed under a *different* Hamiltonian is expected to carry force).

This gate was changed **after** seeing that it blocked results, so it is held to the
matching standard:

- It moves **no** pre-registered threshold — GATE 1's 5 meV, P7's 0.15 V, P10's 0.10/0.30 eV
  and P11's 0.30 eV are all untouched.
- All 18 production relaxations keep their `TRUSTWORTHY` verdict; the killed `yaw270`
  restarts stay `POISONED`. The fix admits single points and nothing else.
- **§6b's P11 numbers reproduce digit for digit** under the fixed gate, and GATE 1 now
  passes on all four adsorbate states per anchor instead of only `s0_OOH`. §6b stands as
  written; the bug was dropping jobs, not corrupting them.

### P3 — vacuum: **REFUTED at the DFT level.** Closed negative.

At 32 Å (from 20 Å), fixed geometry, both anchors:

| | Δη | max |ΔΔG| |
|---|---|---|
| Ru | **−0.0005 V** | 0.001 eV |
| Ir | **+0.0002 V** | 0.003 eV |

§5 sets < 50 mV ⇒ not the explanation. This is two orders of magnitude inside that. The
a-priori MLIP argument in §2c is now confirmed by direct DFT rather than merely inherited.

### P2 — dipole: **NOT RUN.** Deck bug.

All 16 dipole decks aborted in 2 s: `bad line in namelist &system: "tefield = .true."`.
`tefield` and `dipfield` are **`&CONTROL`** variables; only `edir`/`emaxpos`/`eopreg`/`eamp`
belong to `&SYSTEM`. `probe_decks.py` emitted all six into `&SYSTEM`. Fixed. P2 remains
closed only by the §2c a-priori argument and by P3's result, **not** by its own test.

### P9 — RPBE: **NOT SCORED.** Gas references died.

The eight RPBE slab single points ran clean. Both gas decks aborted: *"Gamma-only
calculations not allowed with pools"* — the gas decks are Γ-only but the queue launched
everything at `-nk 4`. `probe_eta.py` then did exactly what §5 condition 1 requires and
**refused to score RPBE slabs against cached PBE water**. The gate worked; the test is
still owed.

### P10 — the symmetry trap: Ir lands at **−0.291 eV, in a band §5 left undeclared**

Ir's `yaw90` converged after 54 ionic steps and 22.6 h at **−0.2913 eV**. §5 declares a
verdict for ≥ 0.30 eV (trapped, tier-wide retraction) and for < 0.10 eV (exonerated). This
is **9 meV below the trigger and three times above the exoneration bin** — the criterion
has a gap and this result sits in it. It is recorded as such. It is *not* rounded up to
"trapped" and *not* waved through as "exonerated"; assigning it to either bin after the
fact is the circularity §6a warns about.

What can be said without choosing a bin — the consequences for Ir, which are large:

| Ir | ΔG_OOH − ΔG_OH | vs band 3.2 ± 0.2 | η | pls |
|---|---|---|---|---|
| on record (in-plane) | 3.652 | **outside** | 0.781 V | 3 |
| off-plane `yaw90` | **3.361** | **inside** | **0.490 V** | 3 |

So the off-plane restart pulls Ir's scaling anomaly — the second of the two independent
anchor failures in §2 — from outside the universal band to inside it, and drops η(Ir) into
the published IrO₂ range. Ru's trap is worth only 82 meV and leaves its descriptor
untouched. **The two anchors' failures remain distinct: Ir's was substantially a basin
failure, Ru's is not.**

MACE predicted −0.73 eV for Ir and −0.27 eV for Ru. Measured: −0.291 and −0.082. It called
the *existence* and the *ordering* of the lower basin correctly on both, and overestimated
the depth by 2.5× and 3.3×. That prediction was on the record before the DFT ran.

### P7 — U-sensitivity: **TRIGGERED. The headline claim must be withdrawn.**

Cr, four U values at fixed geometry:

| variant | ΔG_O − ΔG_OH | η | pls |
|---|---|---|---|
| ×0.0 | 0.761 | 1.452 V | 3 |
| ×0.5 | 1.133 | 0.904 V | 3 |
| **×1.0 (production)** | **1.560** | **0.330 V** | **2** |
| ×1.35 | 1.873 | 0.643 V | 2 |

§5: *"If η(Cr) or η(Co) moves by more than 0.15 V across U ∈ {0, 0.5×, 1×, 1.35×} at fixed
geometry, then 'earth-abundant rutiles outperform RuO₂/IrO₂ in this tier' is not supported
by this data and must be withdrawn, not softened."*

η(Cr) moves **1.122 V**. That is 7.5× the criterion.

**This survives the GATE 1 failure below.** The descriptor uses only `s0_O` and `s0_OH`,
both of which round-trip at 0.00 meV, and it spans **1.112 eV** across the ladder. The two
`pls = 2` rows — production and ×1.35 — take η directly from that clean descriptor and
alone give a **0.313 V** swing, still 2× the criterion. No part of the trigger depends on a
drifted number.

The mechanism is the damaging part: the descriptor is monotonic in U and production U
happens to place Cr at **1.560 eV, essentially on Man's 1.60 eV apex**. η(Cr) = 0.330 V is
therefore not a prediction the method made — it is where the volcano peak sits, selected by
a U value the campaign did not derive from anything. **"Earth-abundant rutiles beat the
noble anchors" is withdrawn.**

Co's ladder never ran: its probe batch was built without a `base` control, so `probe_eta.py`
refused it. P7 is triggered by Cr alone, but Co is still owed.

### NEW — the Cr `*OOH` relaxation is in a metastable magnetic state, 175 meV high

GATE 1 failed for Cr on `s0_OOH` alone: base SCF −22265.4947 eV vs the relaxation's own
final −22265.3196 eV, a drift of **−175.11 meV**, with the SCF *below* the relaxation. A
converged geometry cannot do that unless the electronic state differs — and it does:

| Cr `s0_OOH` | total mag | abs mag | E (eV) |
|---|---|---|---|
| relaxation, final step | **11.80** | 19.41 | −22265.3196 |
| fresh SCF, identical coordinates | **11.00** | 20.09 | **−22265.4947** |

`s0_OH` gives 11.00 / 19.45 both ways and round-trips at 0.00 meV. The relaxation converged
cleanly — `bfgs converged`, 82 steps, fmax 0.0021 — and carried a metastable magnetic
solution through all 82 of them. The SCF at step 1 chose a basin and the relaxation never
left it.

Consequences:

1. **η(Cr) = 0.330 V is unaffected**, because Cr's limiting step is `pls = 2` — the
   ΔG_O − ΔG_OH step, which involves neither `*OOH` nor any drifted number. Lowering
   ΔG_OOH by 0.175 eV moves ΔG₃ to 1.371 and ΔG₄ to 0.471, both still below 1.560.
2. **The tier-wide exposure is not bounded by this.** Six magnetic 3d metals × 4 states =
   24 production states have never been checked for this, and it took one probe to find one
   case at 175 meV. Where a metal's `pls` *is* 3 or 4, an error of this size lands directly
   on η.
3. The audit is cheap — one fresh SCF per state, ~28 jobs, the same machinery as this
   campaign. It is now the highest-value outstanding DFT task.

**GATE 1 earned its place here.** It was written to catch a coordinate round-trip failure
and it caught a physics failure instead, in the one state out of four where it mattered.

## 6d. RESULTS — the magnetic audit (2026-08-08)

§6c item 3 called the audit "the highest-value outstanding DFT task." It ran: 11 fresh
fixed-geometry SCFs over Fe (4 states), Mn (4) and Ni (3), each compared against its own
relaxation's final energy. **Two of the three elements carry a multistable state.**

| element | state | fresh SCF (eV) | relaxation final (eV) | drift | total mag, SCF → relax |
|---|---|---|---|---|---|
| **Mn** | all four | — | — | **≤ 0.005 meV** | 17.00 → 17.00 |
| **Fe** | `s0_OOH` | −34803.8875 | −34804.1641 | **+276.60 meV** | 23.86 → 22.98 |
| **Ni** | `s0_OH` | −35374.7913 | −35374.6182 | **−173.04 meV** | 4.16 → 7.18 |

Fe's other three states round-trip at ≤0.52 meV and Ni's other two at ≤0.03 meV, so in both
cases the failure is one state, not a systematic extraction fault. Mn reproduces
digit-for-digit including absolute magnetization (23.76 both ways).

**The sign matters, and it differs between the two.** For Ni — as for Cr in §6c — the fresh
SCF lands *below* the relaxation, meaning the production relaxation carried an **excited**
state and its ΔG is too high. For Fe the fresh SCF lands *above*: the production relaxation
found the lower solution and it was the audit SCF that got trapped. **Fe's on-record number
is the good one; Ni's is not.**

Consequences:

1. **η(Fe) = 1.263 V survives, and is more robust than it looked.** Re-scoring Fe with the
   drifted `*OOH` in place returns **1.2636 V**, unchanged from the record. Fe's limiting
   step is `pls = 2` with a rung-2 margin of ~2.0 eV over rungs 3 and 4, so a 277 meV
   wobble in `*OOH` cannot reach η by an order of magnitude in margin.
2. **η(Ni) = 1.084 V is now compromised twice over** — it was already a bounded inference
   rather than a measurement (§1), and its `*OH` sits 173 meV above the state a fresh SCF
   finds at identical coordinates. The audit deck carried no `s0_OOH` for Ni, so it cannot
   be re-closed from what is in hand.
3. **Mn is the only endmember verified clean across all four states.** η(Mn) = 0.8917 V
   re-scores through GATE 1 without a refusal — the one tier number that has now passed
   both the convergence and the multistability check.
4. **The rate is not a tail.** Three of the seven production states audited so far are
   multistable (Cr `*OOH`, Fe `*OOH`, Ni `*OH`). The §6c estimate of the exposure was
   correct to treat 24 unchecked states as an open liability rather than a formality.
5. The two anchors are **not** exposed to this failure mode: Ru and Ir run `nspin = 1`
   (§2f, P11), so they have no magnetic basin to be trapped in.

Still unaudited: Co (its `s0_OOH` was never computed at all, and the U-ladder is what is
running now), and Cu (no usable production data to audit against).

## 6e. RESULTS — the follow-up queue drained (2026-08-09)

All 36 jobs returned. Every remote output was verified byte-identical against the local
copy (112 files, md5) before teardown. This closes the two probes §6c had to report as
unrun, and it resolves Co.

### P2 — dipole: **REFUTED by direct DFT.** Closed negative.

§6c could only report the deck bug. The rebuilt decks ran clean (`SCF_FAIL=0`, fmax
0.0035–0.0051) and the correction is nil:

| anchor | Δη (dipole) | ΔG shifts (OH / O / OOH) | deficit it must explain |
|---|---|---|---|
| Ru | **−0.0018 V** | +0.000 / +0.004 / +0.002 | +0.39 V |
| Ir | **+0.0002 V** | +0.001 / +0.009 / +0.010 | +0.22 V |

Two orders of magnitude short on Ru, three on Ir. The earlier ≤20 meV bound from §6c was
an estimate; this is a measurement, and it is tighter. (The combined `dipole+vac32`
variant still carries the original `&SYSTEM`/`&CONTROL` deck bug and died in 2 s — moot,
since dipole alone and vac32 alone are each independently null.)

### P9 — RPBE: **REFUTED, and it moves η the wrong way.**

RPBE was the plausible XC rescue — it is OC20's functional, and a GGA that weakens
adsorbate binding. It does weaken binding, and that makes both anchors *worse*:

| anchor | η base | η RPBE | Δη | descriptor ΔG_O−ΔG_OH |
|---|---|---|---|---|
| Ru | 0.7868 | **1.0027** | **+0.2160 V** | 1.163 → **1.018** |
| Ir | 0.7806 | **0.9426** | **+0.1620 V** | 1.642 → **1.495** |

RPBE gas references: H₂O −601.3804 eV, H₂ −32.0726 eV.

The mechanism is worth keeping, because it is almost perfectly transferable between two
different metals: **ΔG_OH +0.198 / +0.199 eV and ΔG_O +0.053 / +0.053 eV** on Ru and Ir
respectively. A near-identical rigid shift on both — so the descriptor drops by 0.145 (Ru)
and 0.147 (Ir). Ru's descriptor was already 0.44 eV *below* Man's 1.60 apex, so RPBE drives
it further off; Ir's was sitting *on* the apex, and RPBE knocks it off. Neither anchor is
rescued by changing the functional, and the direction is unambiguous.

### P7 on Co — **unscoreable, and the reason is the result.**

The hard restart worked as a convergence fix: `slab__base` converged in 4.4 h
(`rc=0`, `SCF_FAIL=0`) where the original stalled for 7.9 h at iteration 115/200. But
GATE 1 then refused the ladder:

| Co state | fresh SCF (eV) | relaxation final (eV) | drift |
|---|---|---|---|
| `s0_O` | −31710.3473 | −31710.3473 | +0.01 meV OK |
| `s0_OH` | −31728.5322 | −31728.1277 | **−404.52 meV** |
| `slab` | −31146.1540 | −31146.2133 | **+59.39 meV** |

**−405 meV is the largest drift in the campaign**, and the escalated mixing did not fail
so much as find a *different, higher* basin for the slab. So Co is not merely hard to
converge — its SCF has multiple solutions and the recipe selects among them. That
retroactively explains Co going 0-for-4 in the endmember campaign (docs/26 §6): it was
read as convergence difficulty, and it is really solution multiplicity.

**The `slab` drift is the serious one.** A clean slab is the common reference in every
ΔG on that element, so a 59 meV ambiguity there propagates into all four rungs at once.

### Where the tier stands on multistability

| | states audited | multistable | worst drift |
|---|---|---|---|
| **Mn** | 4 | **0** | ≤0.005 meV |
| Cr | 4 | 1 (`*OOH`) | −175 meV |
| Fe | 4 | 1 (`*OOH`) | +277 meV (audit trapped; record OK) |
| Ni | 3 | 1 (`*OH`) | −173 meV |
| Co | 3 | 2 (`*OH`, **slab**) | −405 meV |
| **Ru / Ir** | 4 + 4 | **0** | ≤0.01 meV |

**Every magnetic 3d endmember except Mn carries at least one multistable state, and the
two `nspin = 1` anchors carry none** — they round-trip to 0.01 meV across all eight states.
That is a clean structural statement: the failure mode is magnetic, it is confined to the
open-shell 3d oxides, and it does not touch the anchors.

### What is left of the anchor deficit

With P2 and P9 closed, the candidate list is nearly exhausted. Gas references (ruled out
algebraically, §2a), vacuum (−0.0005 V, §6c), dipole (≤2 meV, above), thickness and
constraint (+0.05 V, wrong sign, §6c), spin (P11, wrong way, §6c), XC (P9, wrong way,
above), and magnetic multistability (not applicable at `nspin = 1`) are all closed
negatives. Only P10 survives, and it is asymmetric: **it largely fixes Ir** (scaling
3.652 → 3.361, η 0.781 → 0.490 V, inside the published range) and **leaves Ru essentially
untouched** at 82 meV.

So the honest position going into the writeup is that **Ir is explained and Ru is not** —
not by any artifact this campaign can find. The remaining account for Ru is the one in
§2f and §2d, which does not depend on finding a bug: η ≈ 0.79 V for `nspin = 1` RuO₂(110)
is a *published* result (Liang 2022, 0.63–0.73 V, same `pls = 3` signature), and η is a
positively biased estimator (§2d). That is a defensible story, and it is stronger for
having eliminated the alternatives by direct calculation rather than by argument.

## 6f. RESULTS — the basin restarts landed (2026-08-09). `tier_v2`.

The three states GATE 1 caught in the wrong SCF solution (§6d) were re-relaxed from
their own final geometry with a fresh atomic-superposition density
(`src/dft/build_basin_restarts.py`). All three converged. **All three reproduced the
audit SCF at ionic step 1 to better than 0.02 meV**, which is the validation the repair
needed: it confirms the mechanism was path dependence in the extrapolated charge
density, not a mixing or convergence failure.

| state | production relax | audit fixed SCF | basin re-relax step 1 | basin final | drift prod → final |
|---|---|---|---|---|---|
| Cr `*OOH` | −1636.47080322 | −1636.48367381 | −1636.48367381 | −1636.48392834 | **−178.58 meV** |
| Co `*OH`  | −2331.97437355 | −2332.00410501 | −2332.00410589 | −2332.00425138 | **−406.51 meV** |
| Ni `*OH`  | −2599.98648382 | −2599.99920170 | −2599.99920186 | −2599.99940826 | **−175.85 meV** |

(Ry. `bfgs converged` and `JOB DONE` on all three; 4, 3 and 5 ionic steps respectively.)

Relaxing on the correct surface bought only **2–3.5 meV** beyond the fixed-geometry
estimate. That is worth stating plainly: **the §6d fixed-geometry numbers were not merely
lower bounds, they were essentially the answer.** The geometry these states want is the
geometry they already had — what was wrong was the electronic solution sitting on top
of it. A future audit can therefore quote the GATE-1 SCF as the correction with a stated
2–4 meV residual, rather than paying for a full re-relaxation per state.

### The corrected tier

| M | η(v1) | η(v2) | Δ | pls v1 → v2 | c_M | floor c_M/2 − 1.23 | excess |
|---|---|---|---|---|---|---|---|
| Cr | 0.491 | **0.330** | **−0.160** | 3 → 2 | 3.102 | 0.321 | **0.009** |
| Ir | 0.781 | 0.781 | — | 3 | 3.652 | 0.596 | 0.185 |
| Co | 0.544 | **0.784** | **+0.240** | 1 → 2 | — (bounded) | — | — |
| Ru | 0.787 | 0.787 | — | 3 | 3.180 | 0.360 | 0.427 |
| Mn | 0.892 | 0.892 | — | 2 | 3.034 | 0.287 | 0.604 |
| Ni | 1.084 | **1.189** | **+0.105** | 1 → 2 | — (bounded) | — | — |
| Fe | 1.263 | 1.263 | — | 2 | 2.711 | 0.125 | 1.138 |

    tier_v1 : Cr < Co < Ir < Ru < Mn < Ni < Fe
    tier_v2 : Cr < Ir < Co < Ru < Mn < Ni < Fe

Three things follow.

**Co 0.544 V is withdrawn.** It was the tier's second-best number and it does not exist.
Co's `*OH` was the largest drift in the campaign, and correcting it moves Co by +240 mV
and changes its potential-limiting step from 1 to 2. Co is now an ordinary mid-tier
metal, 3 mV from Ir and 3 mV from Ru. It never had a `*OOH` and still does not; the value
above is a bound, and the bound is now *safer* than before — the window widens from
[3.15, 5.16] to **[2.91, 5.40] eV**, comfortably containing Co's own partial-relaxation
upper bound of 4.571.

**Cr is now sitting on its scaling floor.** The correction pulls c_Cr from 3.281 to
**3.102 eV**, and η(Cr) = 0.330 V against a floor of 0.321 V — an excess of **9 meV**.
Cr is not a descriptor success; it is a metal whose `*OOH`/`*OH` scaling constant happens
to be favourable, and it is exploiting essentially all of it. c_M = 3.102 is only 0.65σ
below Divanis (2020)'s pooled 3.18 ± 0.12 eV, i.e. **not a scaling-relation breaker.**
This does not reinstate the headline: **P7 still stands**, η(Cr) moves 1.122 V across U,
and 0.330 V is a value at one chosen U, not a measurement.

**Ni's `pls` flips 1 → 2 and its bound gets much safer** — window [2.50, 6.97] eV, width
4.47 eV. Ni is unchanged in rank.

### The docs/39 pre-registration, discharged

docs/39 §4 committed to reporting the `omat` result "as prominently as the negative."
Both pre-registered heads were rescored against `tier_v2` with the identical
matched-protocol pipeline:

| head | vs `tier_v1` | vs `tier_v2` |
|---|---|---|
| UMA `uma-s-1p2`, `omat` task | ρ = +0.9643, exact p = 0.0028, MAE 0.125 V | **ρ = +0.8929, exact p = 0.0123, MAE 0.134 V** |
| MACE `medium-mpa-0` | ρ = +0.8571, exact p = 0.0238, MAE 0.173 V | **ρ = +0.8214, exact p = 0.0341, MAE 0.146 V** |

Both degrade and **both remain significant at α = 0.05.** The degradation is one adjacent
transposition in each case, and it is the *same* transposition: neither model predicted
Co's basin failure, because neither model was ever told which SCF solution the DFT
reference had landed in. MACE's MAE *improves* while its ρ falls, which is the expected
signature of a rank error on a pair that moved apart in value.

Recorded honestly: this rescore was run **after** the corrections were known, so it
discharges the docs/39 commitment but it is **not** a blind test. The remaining
corrections — symmetry, cell, U — have not run, and the degradation against `tier_v3`
must be written down with a number *before* they are scored.

### What this does not fix

The three repaired states were all built at y ≡ 0 and are all still on the slab mirror
plane. **The symmetry trap is untouched by this correction**, and Cr's `*OOH` — the state
that now sets Cr's scaling constant — is exactly the class of state P10 found a −0.291 eV
escape for on Ir. Cr's 0.330 V should be read as "the magnetically-correct value at the
production U, in the production cell, on the mirror plane," and every one of those four
qualifiers is still live.

## 6g. RESULTS — the archive symmetry audit (2026-08-09). The tier is not one protocol.

Block 1D of the program asked a bookkeeping question: how many of the 153 archived `.out`
files were relaxed inside a symmetry constraint? The answer is not a percentage. It is that
**the seven-metal tier was never computed under a single protocol**, and which protocol a
metal got was decided by an input flag that nobody chose deliberately.

`src/dft/symops_audit.py` reads every pw.x output, records the size of the symmetry group
pw.x kept, and independently measures max|F_y| on the adsorbate atoms across every printed
force block. Those are two separate witnesses to the same thing, and **they agree on every
one of the 96 adsorbate runs.**

### Three regimes, not two

| class | definition | meaning |
|---|---|---|
| **LOCKED** | pw.x kept ≥ 2 operations and symmetrised F_y to **exactly** 0.0000000000 Ry/au | the relaxation was a constrained optimisation in a 2-D (x, z) subspace and could not leave the plane |
| **ON_PLANE** | no symmetry enforced, but max\|F_y\| < 1e-4 Ry/au | numerically free; the optimiser was never pushed off the plane and did not leave it. **Physically identical to LOCKED.** |
| **EXPLORED** | max\|F_y\| ≥ 1e-4 Ry/au | a real out-of-plane force existed and the optimiser acted on it |

The middle class is the one a two-way audit would have missed. `nosym` on an exactly
symmetric input does nothing — it removes the constraint without supplying a reason to
move — so "we set `nosym`" is not evidence that a search explored anything.

### The 20 production adsorbate relaxations

| | LOCKED | ON_PLANE | EXPLORED |
|---|---|---|---|
| count | 9 (45%) | 6 (30%) | 5 (25%) |

**15 of 20 (75%) were confined to the mirror plane by one route or the other.**

| metal | `*O` | `*OH` | `*OOH` |
|---|---|---|---|
| **Cr** | LOCKED | LOCKED | LOCKED |
| **Ir** | LOCKED | LOCKED | LOCKED |
| **Ru** | LOCKED | LOCKED | LOCKED |
| Mn | ON_PLANE | **EXPLORED** | **EXPLORED** |
| Fe | ON_PLANE | **EXPLORED** | ON_PLANE |
| Co | **EXPLORED** | **EXPLORED** | — |
| Ni | ON_PLANE | ON_PLANE | — |
| Cu | — | — | ON_PLANE |

### The cause is a single flag, and it partitions the tier perfectly

| `nosym = .true.` in the deck | LOCKED | ON_PLANE | EXPLORED |
|---|---|---|---|
| **absent** (Cr, Ir, Ru) | **9** | 0 | 0 |
| **present** (Mn, Fe, Co, Ni, Cu) | 0 | 6 | 5 |

Twenty for twenty, no exceptions. The confinement class of every production relaxation in
this campaign is predicted exactly by whether one line was present in its input.

### The cause, exactly: it was deliberate, and the reasoning is written down

*(An earlier draft of this section attributed the split to the endmember rescue ladder.
That was wrong. The real cause is in the builder, with a comment.)*

`src/dft/qe_slab.py` emitted `nosym = .true.` for the clean slab and `nosym = False` for
every adsorbate slab. The docstring that justified it, in the repository until today:

> `nosym` belongs on the CLEAN slab only. […] it also discards the in-plane symmetry,
> taking that slab from 15 to 36 irreducible k-points. **An adsorbate lowers the symmetry
> by itself**, and `runs/Cr_slab/s0_OH.in` (no nosym) ran to JOB DONE at 15 k-points while
> `runs/Mn_slab/s0_O.in` (nosym) paid for 36 — **same physics, 2.4× the bill.**

Both claims are false, and the second one is this campaign's central finding.

**"An adsorbate lowers the symmetry by itself."** It does not.
`hea_oer.surfaces._adsorbate` defines every OER adsorbate with y ≡ 0 and places it at
(x_cus, y_cus) — *exactly on* the rutile(110) mirror plane. The adsorbate sits **in** the
mirror rather than breaking it. That is the entire mechanism, and it is the one thing the
justification assumed away.

**"Same physics, 2.4× the bill."** Not the same physics. With the mirror alive, pw.x
symmetrises F_y onto it and the relaxation becomes a constrained optimisation over a 2-D
(x, z) subspace. The saving bought a *different calculation*, and on Ir's `*OOH` the
difference is **−291 meV**, which moves η(Ir) from 0.781 to 0.490 V.

### The chronology

| date | event |
|---|---|
| **2026-06-29** | endmember decks committed (`3f3dd19`) carrying `nosym` — Mn, Fe, Co, Ni, Cu. The Cr anchor lands the same day by a separate path (`7e06fdb`) **without** it. The discrepancy exists, unnoticed. |
| **2026-07-31** | `1a3a77b` — *"make the Ru/Ir anchors runnable and 4× cheaper"*. The Cr-vs-Mn discrepancy is **observed, measured at 15 vs 36 k-points, explained as "same physics", and made the rule.** `nosym = False` becomes the default for every adsorbate deck. |
| **2026-07-31 →** | Ir and Ru are built under the new rule. Both LOCKED on all three states. |
| **2026-08-09** | this audit. The rule is reversed and the call site now states its choice explicitly; `nosym` is a required argument with no default. |

So the honest account is not that a constraint crept in unnoticed. **It was noticed, checked
against two runs, rationalised with a physical argument, and adopted as a documented cost
optimisation** — in a commit that advertises the saving in its subject line. The argument
was wrong in the one way no convergence test can reveal, and the two runs it was checked
against were the two whose difference it was explaining.

That is a better story than an accident, and a more useful one: it is what a careful
practitioner does, and it still produced two protocols in one benchmark tier.

### Why this matters more than the count does

**1. The tier's η values are not mutually comparable.** Cr, Ir and Ru were optimised over a
2-D subspace; Mn, Fe, Co, Ni and Cu over the full 3-D one. Comparing those seven numbers —
which is exactly what a benchmark tier is for — compares two different calculations. This is
not a correction to apply; it is a statement that the comparison was ill-posed.

**2. The partition lands on precisely the campaign's three unexplained problems.** Cr, whose
headline was withdrawn. Ir, whose scaling anomaly is fixed by an off-plane restart
(3.652 → 3.361, η 0.781 → 0.490). Ru, whose descriptor deficit has survived six closed
negatives. All three LOCKED, on all three states, with no exceptions.

**3. And it lands on the clean metal from the other side.** Mn is the only endmember verified
clean across all four states (≤ 0.005 meV, §6d) and the only real ambient rutile in the tier
— and Mn is one of only two metals that genuinely explored off-plane.

That correlation is on n = 8 metals and confinement is confounded with which era built the
deck, so it is **hypothesis-generating, not causal**. It is exactly what block 1A of the
program is designed to test, and it is registered as such in docs/43 §2 before that block
runs.

**4. It sharpens what the symmetry claim can honestly say.** Not "this campaign relaxed
every adsorbate inside a mirror plane" — that overstates it, and `orient_starts.py`'s
docstring, written before this audit, says exactly that. The accurate claim is stronger and
more specific: *a single undeclared input flag, varying silently across a benchmark tier,
determined whether each metal's geometry optimisation was three-dimensional; 75% of the
production relaxations were confined either way; and no force, energy or convergence
criterion distinguishes the two populations.* Every affected run passed every QC gate this
project has.

Machine-readable output: `docs/figs/symops_audit.csv`, one row per `.out`, with the symmetry
count, the deck's `nosym` state, max|F_y|, and the class.

## 7. Standing caveats

- Fixed geometry. Second-order relaxation effects are excluded by construction.
- The literature anchors in §1 are themselves a range across protocols, not a
  measurement; docs/32 already treats them as a band and this document inherits that.
- The apex value 1.60 eV and band centre 3.2 eV are Man (2011) conventions. P4 and P5
  are stated as *movements* of ≥ 0.30 eV precisely so they do not depend on the exact
  centre of either literature band.
- Nothing here touches the melt list, which remains unfrozen and Frank's decision.

## Correction of record — 2026-09-03: the RuO₂ antiferromagnetism premise is refuted, and this document asserted it as fact

**This document is a pre-registration and is not rewritten.** The paragraphs corrected below stand
as written; this section is the correction of record, in the same discipline as every other dated
correction in this campaign. Nothing in §§1–7 above has been edited.

### What this document asserted

Three places, all resting on one 2017 citation:

- **`:268-271`** — "**And the literature names the fix, in Ru's exact coordinate.** RuO₂ is
  **antiferromagnetic** — Berlijn et al., PRL 118, 077201 (2017), itinerant AFM from neutron
  diffraction."
- **`:275-277`** — of `qe_slab.py:44-48`'s comment *"RuO2/IrO2 are 4d/5d rutile metals, itinerant
  and non-magnetic"*: "**For RuO₂ that is factually wrong**, and it is the single best-supported
  candidate for the descriptor deficit §2 localised."
- **`:512-515`** — "it does not make `qe_slab.py:44-48`'s 'itinerant and non-magnetic' comment
  correct — RuO₂ is still experimentally AFM."

The same premise is asserted in deck-generating code at `src/dft/probe_decks.py:250-253`.

### What the literature says now — three sources, each opened and read this session

| source | what it measures | result |
|---|---|---|
| Hiraishi, Okabe, Koda, Kadono, Muroi, Hirai & Hiroi, **PRL 132, 166702 (2024)**, arXiv:2403.10028 | μSR on **single-crystal** RuO₂, 5–400 K; muon sites computed from first principles (dilute H as pseudo-hydrogen) to rule out accidental cancellation of B_loc | no spontaneous internal field; upper limit **\|m_Ru\| ≤ 4.8(2)×10⁻⁴ μ_B**. Verbatim: "*These results indicate that the AFM order, as reported, is unlikely to exist in the bulk crystal.*" |
| Keßler, Garcia-Gassull, Suter, Prokscha, Salman, Khalyavin, Manuel, Orlandi, Mazin, Valentí & Moser, **arXiv:2405.10820** | μSR **and** neutron diffraction, bulk crystals and epitaxial films | **bulk ≤ 1.4×10⁻⁴ μ_B/Ru**, films ≤ 7.5×10⁻⁴ μ_B/Ru; the earlier neutron peak attributed to **multiple scattering** |
| Smolyanyuk, Mazin, Garcia-Gassull & Valentí, **PRB 109, 134424 (2024)**, arXiv:2310.06909 | DFT+U survey of where RuO₂'s magnetism comes from | stoichiometric RuO₂'s electronic properties are described by a **smaller U than the U required to have magnetism**; Ru vacancies can aid a magnetic state |

Against the ≈ 0.05 μ_B that diffraction suggested and that Hiraishi's abstract names explicitly,
those bounds are **104× (Hiraishi), 357× (Keßler bulk) and 67× (Keßler films)** below it.

### The correction

1. **The sentence "RuO₂ is antiferromagnetic … for RuO₂ that is factually wrong" is WITHDRAWN.**
   For the **bulk**, `qe_slab.py`'s "itinerant and non-magnetic" — the comment this document
   rebuked — is the reading the 2024 measurements support. The rebuke was wrong, not the comment.
2. **Scope, stated so the correction does not over-claim in the other direction.** What is refuted
   is **bulk long-range order**. Surface moments on a (110) slab are a separate question and are
   *not* excluded by a bulk μSR bound. Any sentence in the report saying "RuO₂ is non-magnetic"
   must carry "in the bulk"; the campaign's production convention for Ru (nspin = 1, U = 0) is a
   **modelling choice that the bulk evidence supports**, not a measured surface fact.
3. **Liang, Bieberle-Hütter & Brocks, JPCC 126, 1337 (2022) is downgraded, not withdrawn.** Its
   0.41–0.49 V is a calculation on an AFM ordering that the bulk evidence now excludes. This
   document used it as "the literature names the fix"; it is demoted to *a hypothesis about
   surface magnetism*, and the ~0.3 eV it attributes to the moment on the bare/\*OH/\*OOH cus Ru
   can no longer be cited as a known mechanism for the descriptor deficit.
4. **No measurement in this campaign changes.** Every P7 and S0(h) number stands: they are
   measurements of what a magnetic SCF solution does to adsorption energies at this protocol, and
   that is true regardless of which solution nature picks. What changes is their **label**.

### What this does to gate (h) — and it strengthens the campaign

Gate (h) returned **4/4 ADOPT_AFM** on the RuO₂ anchors: the AFM solution sits **80–144 meV below**
the NM one under this campaign's Hamiltonian, and adsorption energies move **33–64 meV** when the
anchor is AFM (docs/43:1638-1644). Read with the 2024 measurements, that is no longer an
adoption of the experimental ground state. It is **an in-house instance of this campaign's own
thesis, with a literature-verified ground truth**: the electronic-structure method prefers, by
80–144 meV, a magnetic state that experiment excludes at 10⁻⁴ μ_B — two to three orders of
magnitude below the moment that solution carries — and the answer moves 33–64 meV because of it.
Smolyanyuk 2024 supplies the mechanism: the U that makes RuO₂ magnetic in DFT+U is larger than
the U its electronic properties want.

This is the strongest single example the campaign has of a **silent premise error with an
independent experimental check**, and it is on the benchmark anchor rather than on a proxy.

### Two things this correction does NOT decide

- **The four gate-(h) 2×1v AFM relaxations remain on HOLD** (0 built; docs/43:1645 ADOPTION NOTE,
  scope resolved 2026-08-30 as STANDALONE_FOUR). Their *justification* has changed — they would
  relax into a state the bulk evidence excludes — so they are now a **sensitivity arm**, not a
  ground-state adoption. Whether that changes the entrant's launch decision is a dated line he
  owes; this correction supplies the new information and decides nothing.
- **A post-hoc observation, flagged as post-hoc and registered against nothing.** A11.R6's result
  — 0 of 16 spin-polarised Ru SCFs converging at U = 9 across three mixing settings, while the
  nspin = 1 twins converge in 25 iterations at 5.9e-7 Ry (docs/68 §2, §11) — is *consistent* with
  Smolyanyuk's picture of RuO₂ magnetism as a high-U artifact. It was observed after the fact, no
  prediction scores it, and it is recorded here as an observation only.

### Provenance

Surfaced by the docs/70 ideation round as hole H-1 (`docs/70:96-114`). The three sources above were
opened and their abstracts read in this session before this section was written; the 104× / 357× /
67× ratios were computed here from the bounds each abstract states against the 0.05 μ_B that
Hiraishi's abstract names. Ledger row: docs/45 §A row 6 and the dated section beneath it.

### Sub-correction — 2026-09-03 (same day, appended not edited): "remain on HOLD (0 built)" is FALSE

The first bullet above says the four gate-(h) 2×1v AFM relaxations "remain on HOLD (0 built)".
**That is wrong, and it was already wrong when written earlier today.** It repeats the "still open"
voice of the 2026-08-23 ADOPTION NOTE at docs/43:1645 without checking whether a later dated line
had closed it. One had: `**[AFM-SCOPE RESOLVED 2026-08-30: STANDALONE_FOUR]**` (docs/43:1979). The
builder then emitted its manifest (`runs/s0/m_h_afm_relax.txt`) and the family ran to terminal
state the same week (docs/64 §1):

| registered job | terminal state | GATE-1 |
|---|---|---|
| `ref__2x1v__afm__relax` | **BANKED** (2 BFGS steps) | **PASS** (+0.028 meV, Δm 0.00) |
| `s0_OH__2x1v_off__afm__relax` | **BANKED** (2 BFGS steps) | **PASS** (−0.090 meV, Δm +0.02) |
| `s0_OOH__2x1v_off__afm__relax` | **BANKED** (3 BFGS steps) | **PASS** (+0.302 meV, Δm −0.03) |
| `s0_O__2x1v_off__afm__relax` | **NOT_CONVERGED** (recorded gap) | never owed — no final geometry |

Measured family cost **1,067.9 SU** (70,851.6 → 69,783.7), against the 4,000–7,600 SU
STANDALONE_FOUR estimate; arrays 20238023 / 20241317 / 20243152 / 20243153.

**What this changes about the line the entrant owes.** It is not a *launch* decision — the launch
already happened, under a resolution he wrote. What the μSR correction actually leaves open is a
**re-label**: three banked relaxations and one recorded gap were justified as a ground-state
adoption and are now, on the bulk evidence, a **sensitivity arm**. That is a smaller line, and it
acts on a completed family rather than on a hold. The correction of record above is otherwise
unaffected — no literature claim, bound, or withdrawal in it depends on this bullet.

**Rule.** *A "still open" clause quoted from a registration is evidence about the day it was
written, not about today.* Registrations say "still open" in their own frozen voice, and the line
that closes them lives in a different place — here, 334 lines further down the same file. Before
repeating any "open / HOLD / not built" clause, grep for its own resolution token (`AFM-SCOPE
RESOLVED`) and check the artifacts on disk. A count of built decks is a `ls`, not a recollection.
