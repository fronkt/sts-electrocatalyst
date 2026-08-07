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

## 7. Standing caveats

- Fixed geometry. Second-order relaxation effects are excluded by construction.
- The literature anchors in §1 are themselves a range across protocols, not a
  measurement; docs/32 already treats them as a band and this document inherits that.
- The apex value 1.60 eV and band centre 3.2 eV are Man (2011) conventions. P4 and P5
  are stated as *movements* of ≥ 0.30 eV precisely so they do not depend on the exact
  centre of either literature band.
- Nothing here touches the melt list, which remains unfrozen and Frank's decision.
