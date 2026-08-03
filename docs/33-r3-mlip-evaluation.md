# 33 — R3: the screener already exists, and it found bugs in our reference

Status 2026-08-03: baselines complete; the three DFT repair jobs of §5 have **run and
landed** (§5b), and every one of them confirmed the MLIP against our own reference. The
fine-tune is still not started — §6 now argues it is the *wrong* thing to buy, for a
reason that did not exist when this document was opened.

The pre-outcome version, written while §5 was still running, is preserved at
[`33-archive-2026-08-03-pre-repair-outcome.md`](33-archive-2026-08-03-pre-repair-outcome.md).

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
2. Whatever oc22's disagreement with us is, it is **not** a reference-energy artefact.
   The entire composition-linear subspace of model error is projected out of the
   descriptor, and being force-free it does not move geometries either. *(This was
   written when oc22 stood at ρ = −1.00. It has since gone to ρ = 0.000 — but for an
   unrelated reason, a defect in our DFT, not in the referencing; docs/29 §8. The proof
   here is unaffected: it holds for any E0 shift regardless of what ρ happens to be.)*
3. **The R3 gate must be the CHE observable, not energy MAE** — E0 alone can cut
   total-energy MAE a long way while leaving every η identical.

Point 2 has a second, larger use: it makes a foundation model on a *different
functional with a different energy zero* directly comparable to our PBE+U numbers with
**no alignment applied**. Fitting a shift first would be fitting noise.

## 2. Two foundation models rank rutile OER out of the box

Single-point on the DFT-relaxed geometries of the five QC-passing metals, zero
fine-tuning, zero alignment:

**Re-measured 2026-08-03 on repaired frames and the repaired reference.** The original
row set was computed against the defective reference *and* on the defective geometries;
re-running both models on the re-extracted frames makes the comparison matched again
(§3a explains why an unmatched re-score is meaningless rather than merely shifted).

| model | ρ(descriptor) | ρ(η) | 15-point ΔG MAE | η MAE | signed bias |
|---|---|---|---|---|---|
| MACE-MPA-0 (2024) | +0.900 | **+0.900** (p = 0.083) | **0.250 eV** | **0.164 V** | −0.227 |
| MACE-MP-0 (2023) | +0.900 | +0.800 (p = 0.133) | 0.375 eV | 0.173 V | **+0.365** |
| UMA-oc22 | — | **0.000** | — | 0.776 V | — |

*(as first published, against the defective reference: MPA-0 ρ(descr) +1.000 / ρ(η) +0.900
/ MAE 0.264; MP-0 +0.900 / +0.900 / 0.336; oc22 ρ(η) −1.00.)*

Different vintages, different training sets, **opposite sign of systematic bias**
(−0.227 vs +0.365 eV), both strongly positive in rank. Not a lucky checkpoint. MACE-MPA-0
is the better model on every metric, which is the expected ordering for the newer
checkpoint and a mild sanity check on the pipeline.

Worth stating on its own: single-point MACE-MPA-0 puts **η(CrO₂) at 0.501 V against the
repaired DFT's 0.491** — a 10 mV error on the structure our own reference had wrong by
1.235 V.

So docs/29's "no out-of-box head ranks rutile OER" was really **"no UMA head does"** —
only oc20/oc22/oc25 were ever tested. That is a meaningful narrowing of the R0 claim
and it should be stated that way from here on.

MPA-0's single η ranking error is Ru vs Ir — the pair docs/32 measured as a **6 mV tie**
in our own DFT, i.e. the one pair the reference cannot resolve. Its Ru < Ir also matches
literature (0.37–0.42 vs 0.54–0.58), where our DFT marginally inverts them.

## 3. The like-for-like test "broke" — and the break was ours, not the model's

The stored UMA records come from UMA **relaxing** each structure itself (16–52 optimiser
steps in their `qc` blocks). A single-point on DFT-relaxed geometry is the easier task —
it hands the model the answer to the geometry half. Running MACE the way UMA was run
(same `FixAtoms`, fmax = 0.05 eV/Å ≈ the DFT `forc_conv_thr` of 2e-3 Ry/au) appeared to
destroy the ranking:

| | single-point | model-relaxed | model-relaxed, **repaired ref** |
|---|---|---|---|
| ρ(η) | +0.900 | **−0.100** | **+0.900** |
| ρ(descriptor) | +1.000 | +0.700 | +0.900 |
| 15-point ΔG MAE | 0.264 eV | 0.339 eV | — |
| η MAE | — | — | **0.149 V** |

The entire degradation was **one structure**. Per-metal ΔG_O shift on relaxation:

```
Cr  -1.013   <<<
Mn  -0.069
Fe  -0.011
Ru  +0.079
Ir  +0.019
```

Chasing that single outlier is what produced §4, and §5b then settled it with DFT: **the
model was right and our reference was wrong.** The third column above is the same MACE
run, unchanged, re-scored against the repaired reference. So the honest reading of this
section is the opposite of the one it was opened with — the like-for-like test did not
break, it *detected a defect in the target*.

**And once the frames were re-extracted too, the gap closed entirely** (§3a): single-point
on matched geometries also gives ρ(η) = +0.900, η MAE 0.164 V. There was never a
single-point-vs-relaxed difference to explain. What looked like one was the trapped Cr
`*O` appearing in the frames file, so the two modes disagreed only about a structure that
was wrong in the first place.

The residual reason to prefer model-relaxed is narrower than "it scores better", and
survives the correction: it is free to disagree about geometry, and that disagreement is
the diagnostic that found four defects in our own reference. A single-point cannot
produce that signal because it never proposes a geometry of its own.

`report()` now requires an explicit `mode` string so a single-point run can never be
recorded as a relaxed one. `dft_reference()` reads `<state>.out`, and on 2026-08-02 the
repaired outputs were written *alongside* the defective ones under `.out.shortbond` /
`.out.bound` — so the canonical path kept returning the trapped Cr for another day. The
files were swapped on 2026-08-03 and `tests/test_dft_reference.py` now pins the repaired
η so that shape of mistake fails loudly.

## 3a. The two modes swapped places, and that is the cleanest evidence in the campaign

Re-scoring the *stored, unchanged* MACE predictions against the repaired reference made
the two modes appear to exchange scores exactly:

| | vs defective ref | vs repaired ref, **old frames** | vs repaired ref, **repaired frames** |
|---|---|---|---|
| MACE-MPA-0, **single-point** | ρ(η) **+0.900** | ρ(η) **−0.100** | ρ(η) **+0.900** |
| MACE-MP-0, **single-point** | ρ(η) **+0.900** | ρ(η) **−0.100** | ρ(η) **+0.800** |
| MACE-MPA-0, **model-relaxed** | ρ(η) **−0.100** | ρ(η) **+0.900** | — |

The middle column is **an artefact of a mismatch, not a result**, and the mechanism is
not subtle. A single-point is computed *on the DFT-relaxed geometry* — which for Cr was
the trapped 2.016 Å structure sitting in `data/qe_frames.extxyz`. The repaired reference
energy belongs to a different structure (1.572 Å) that the single-point never saw.
Pairing a defective geometry with a repaired energy measures nothing about the model.

Re-extracting the frames from the repaired trajectories and re-running (right column)
settles it: **single-point recovers ρ = +0.900 with η MAE 0.164 V**, statistically
indistinguishable from model-relaxed's +0.900 / 0.149 V.

So the "like-for-like test breaks" framing this document opened with was wrong in both
directions, and the truth is simpler than either version: **the two modes agree, and the
apparent collapse was one defective structure viewed two different ways.** The honest
summary is that MACE-MPA-0 ranks this tier at ρ = +0.900 with η MAE ≈ 0.15 V whether or
not it is handed our geometries.

Model-relaxed remains the mode to prefer, but for a narrower reason than "it scores
better": it is the only one whose result cannot be corrupted by a defect in *our*
relaxation, which is a property worth having given that four such defects have now been
found. `report()` requires an explicit `mode` string so the two can never be conflated.

`dft_reference()` reads `<state>.out`, and on 2026-08-02 the repaired outputs were written
*alongside* the defective ones under `.out.shortbond` / `.out.bound` — so the canonical
path kept returning the trapped Cr for another day. The files were swapped on 2026-08-03
and `tests/test_dft_reference.py` now pins the repaired η so that shape of mistake fails
loudly.

### The training set was unrepresentative, not poisoned — a distinction worth keeping

`data/qe_frames.extxyz` was extracted from the pre-repair trajectories. The first version
of this section said fine-tuning on it "would teach a model our own error". **That is
wrong and worth correcting explicitly**, because it is the same kind of overclaim this
document exists to catch.

Every frame in it is a legitimate sample of E(R): converged SCF, a real geometry, real
forces. `qe_frames.py` only ever emits frames whose SCF converged, and the trapped Cr
`*O` run is a genuine stationary point on the PBE+U surface — just a *higher* one than
the minimum the restart found. Two local minima are not a contradiction, and a trajectory
that walks into the wrong one is still true information about the potential.

What the pre-repair extraction actually lacked was **coverage of the region that
matters**:

| | pre-repair | repaired |
|---|---|---|
| `Cr_slab/s0_O` | 28 frames, none below 2.016 Å | 12 frames, all in the 1.57 Å basin |
| `Mn_slab/s0_OOH` | **2** frames, desorbed | **34** frames, bound |
| `Fe_slab/s0_OOH` | **13** frames, desorbed | **29** frames, bound |
| total | 864 | **896** |

Two of the three `*OOH` states contributed 2 and 13 frames of a molecule floating in
vacuum, and nothing at all near a bound `*OOH` on those metals. That is a sampling hole,
not contamination — and it sits exactly where the model would need data to get ΔG_OOH
right. Re-extracted 2026-08-03; the pre-repair set is kept at
`data/qe_frames-archive-2026-08-03-pre-repair.extxyz`.

Since both sets are valid, their **union** is strictly better training data than either
(896 bound-region frames plus 43 frames of the higher basin and the desorbed
approach). Worth doing if the fine-tune is ever commissioned; not done here.

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

## 5. Repair jobs — as commissioned

Instance 46548182, $0.21/hr, 20 ranks each. All five pseudopotential MD5s verified
identical to the 2026-06/07 archive, and only `ATOMIC_POSITIONS` differs from the
original inputs, so the new energies are directly comparable to each metal's existing
CHE chain.

| job | change | decides |
|---|---|---|
| `Cr_slab/s0_O` | restart at Cr–O 1.609 Å (was 2.016) | If DFT climbs back, the original stands and MACE is wrong. If it stays short and lower, **η(Cr) = 1.726 V is superseded**. |
| `Mn_slab/s0_OOH` | `*OOH` bound at 2.076 Å (was 3.83) | Whether a cus-site minimum exists at all. |
| `Fe_slab/s0_OOH` | same (was 3.95) | same. |

**Honest caveat, recorded before the results.** MACE does not keep the Mn/Fe `*OOH` bound
either: from 3.83 Å it relaxes to 3.42, and from the transplanted 2.076 Å back out to
2.54, gaining ~0.25 eV both times. Two very different starting points reach the same
weakly-bound region, so `*OOH` may genuinely bind weakly on MnO₂/FeO₂(110). That is
**not** the claim being tested. The claim is narrower: a run that stopped after 2 and 13
ionic steps at a barely-moved builder placement never located any minimum. DFT gets to
find its own.

## 5b. Outcome — three for three, and the MLIP was right every time

| job | result | Δ energy | M–O before → after | MACE predicted |
|---|---|---|---|---|
| `Cr_slab/s0_O` | **superseded** | **−1.396 eV** | 2.016 → **1.572 Å** | 1.609 Å; η = 0.500 V |
| `Fe_slab/s0_OOH` | **superseded** | −0.376 eV | 3.949 → **2.552 Å** | 2.565 Å |
| `Mn_slab/s0_OOH` | **superseded** | −0.047 eV | 3.825 → **2.480 Å** | 2.541 Å |

Every restart found a lower minimum, so none of the three originals was the right
structure. Two numbers deserve to be stated on their own:

- **η(CrO₂) = 1.726 → 0.491 V.** MACE predicted 0.500 V from its own relaxation — a
  **9 mV** error on the one structure our reference got wrong.
- Fe's `*OOH` settled at 2.552 Å against MACE's independent 2.565 Å — **0.013 Å**.

η(Fe) and η(Mn) are unchanged, exactly as predicted: both are `pls = 2`, so their
overpotential is set by the `*OH → *O` step and never touches ΔG_OOH. The repair fixes
their thermodynamics without moving their activity.

**Cost: $2.64 against an estimate of $0.6–1.1.** The projection was built on the
non-magnetic anchors; the magnetic 3d systems with 32–36 k-points ran 4.3 h (Cr), 10.7 h
(Fe) and 12.1 h (Mn) rather than the 3–5 h assumed. That timing is now the basis for
costing any further 3d job.

### Two of the checks in `adsorbate_qc.py` were falsified by their own results

Both are documented in `tests/test_adsorbate_qc.py` as named regression tests.

1. **The 2.40 Å bond cut.** Written with the explicit claim that "real M–O bonds are
   1.6–2.1 Å, the failures sit at 3.8–4.0 Å, nothing legitimate lands in between."
   Fe's repaired `*OOH` is a genuine, fully-relaxed minimum at **2.552 Å** — squarely in
   the supposedly impossible gap. Replaced by three tiers (bound < 2.20, weak, desorbed
   > 3.00 Å) where only `desorbed` fails, plus a minimum-ionic-step check that turned out
   to separate the real defects far more reliably than any distance ever did.
2. **The ΔG₄ > 0 floor.** Repaired Mn gives ΔG₄ = **−0.022 eV** after a full 34-step
   relaxation. G_TOTAL = 4.92 eV is the *experimental* 4 × 1.23 V while ΔG_OOH carries
   0.1–0.2 eV of GGA error, so a marginally negative ΔG₄ is consistent with zero, not
   impossible. Given a 0.15 eV tolerance; Fe's pre-repair −0.301 eV still fails, which is
   the scale of a real violation.

## 6. What this does to the plan — the fine-tune is now the wrong thing to buy

Both hypotheses from the pre-outcome version resolved, and in the same direction: the
screening tier **is** free, and part of R0's ρ = −1.00 **was** our reference (docs/29 §8:
oc22 goes −1.000 → 0.000 at n = 5). What that leaves is an arithmetic problem, not a
model problem.

**The gate cannot be passed at n = 5, by anything.** Exact two-sided permutation p:

| n | ρ needed for p < 0.05 | adjacent swaps tolerated | MACE-MPA-0 at its current Σd² = 2 |
|---|---|---|---|
| **5 (now)** | 1.000 only (p = 0.0167) | **zero** | ρ = 0.900, **p = 0.083** ✗ |
| 6 | 0.886 (p = 0.033) | two | ρ = 0.943, **p = 0.0167** ✓ |
| 7 | 0.821 (p = 0.034) | five | ρ = 0.964, **p = 0.0028** ✓ |

MACE-MPA-0's single ranking error is **Ru vs Ir** — the pair docs/32 §2 measured as a
**6 mV tie** against a differential resolution of ~0.17 V. So at n = 5 the gate demands
that a model reproduce an ordering our own reference cannot resolve, and a fine-tune that
achieved ρ = 1.000 would be fitting 6 mV of our own noise. **A perfect score would be
indistinguishable from luck, and would not mean the screener works.**

Consequences, in order:

1. **Buy the sixth data point, not the fine-tune.** At n = 6 the *existing free model*,
   keeping exactly the error it already has, clears p < 0.05 — and n = 6 tolerates one
   *new* error on top. This is the only available spend that changes what can be
   concluded. Costed in `tasks/todo.md` R1 at ~$4 for four concurrent jobs, using the
   §5b timings rather than the old guess.
2. **Ni and Co are the only candidates, and both need care.** Cu has 2 of 6 states and
   both are POISONED. Ni and Co each have two states missing or POISONED — *and both died
   on the same SCF-plateau pathology*, so neither is a safe bet and both need the
   two-stage `degauss` protocol. Running both is the hedge: if the pathology takes one,
   n = 6 still lands.
3. **A sixth point inside the 0.78–0.89 V cluster buys nothing.** {Ir, Ru, Mn} are already
   unresolved among themselves. `src/dft/mlip_predict.py` therefore predicts η for Ni, Co
   and Cu from builder geometries *before* anything is rented, validated first against the
   five metals whose answer we know. Whichever is predicted farthest from the cluster is
   the one worth buying — and the prediction is on record beforehand, so the DFT becomes a
   test of it rather than a fit to it.
4. **The constraint float-tie is now load-bearing.** docs/30 §3 found the mid-plane layer
   was assigned by rounding. It is not spread evenly: Cr/Mn/Fe/Cu/Ru/Ir all have the same
   11 free atoms, while **Co has 8 and Ni has 7** — i.e. the two exceptions are exactly
   the two candidates. Adding either as shipped would introduce a point relaxed under
   different freedom than the five it is ranked against. `mlip_predict.py maskbias`
   measures what that costs; if it exceeds ~0.05 V, Ni/Co cannot reuse their existing
   TRUSTWORTHY states and n = 6 costs four jobs per metal instead of two.
5. **DFT hygiene is promoted from optional to required, and narrowed to Cr.** Not for the
   general reason given before, but a specific one: η(Cr) moved 1.24 V on a single
   geometry fix and now sits at descriptor 1.560 against the Man 2011 apex of 1.60,
   beating both noble anchors. That is a strong claim about a material with no OER
   pedigree — and one that docs/31 says has **no aqueous stability window at any pH**.
   Its U- and magnetic-state sensitivity must be measured before it is written up.

**What the fine-tune would still be worth, honestly.** Not nothing — LOMO CV on 864
in-domain frames is a legitimate experiment and would make a clean before/after figure.
But it answers "can we beat 0.149 V MAE", which is not the question the campaign is
gated on, and it cannot make an unattainable rank gate attainable. It is a $1.9 nice-to-have
behind a ~$4 must-have. Deferred, not cancelled.
