# 43 — Pre-registration: the Week-1 factorial, the Hessian test, and the *U* gate

**Written 2026-08-09, before any Week-1 job was launched.** Deposited to Zenodo for a DOI
before the first job of block 1A runs. Nothing in this document may be edited after that
deposit; corrections go in a dated addendum at the bottom with the reason.

**Relationship to docs/41.** docs/41 §5 pre-registered P1–P11 for the anchor-offset
diagnosis. That campaign is complete: P2, P3, P9, P11 are closed negatives, P7 triggered
and withdrew the headline, and P10 **fell in a gap its own criteria left open**. This
document does three things and only three:

1. closes the P10 gap, in advance, with a criterion that has no hole in it;
2. pre-registers the four Week-1 experiments (1A cell×symmetry, 1B hp.x, 1C Hessian) and
   the rules that will be used to read them;
3. pre-registers, with numbers, the predictions that the rest of the campaign would
   otherwise be able to make after seeing the answer — chiefly the MLIP degradation.

---

## 0. The frozen record

Two tiers are pinned as immutable JSON before any Week-1 job returns. Every figure and
every statistic must name the tier version it was computed against; `reference_tier()`
takes a required version argument and has no default.

| | provenance |
|---|---|
| **`tier_v1`** | the tier as published internally through 2026-08-08. Cr 0.491, Co 0.544, Ir 0.781, Ru 0.787, Mn 0.892, Ni 1.084, Fe 1.263. Ordering Cr<Co<Ir<Ru<Mn<Ni<Fe. **Retained only so the corrections can be shown against it.** |
| **`tier_v2`** | after the three basin restarts of docs/41 §6f (commit a44417d). Cr 0.330, Ir 0.781, Co 0.784, Ru 0.787, Mn 0.892, Ni 1.189, Fe 1.263. Ordering Cr<Ir<Co<Ru<Mn<Ni<Fe. **This is the baseline every Week-1 result is measured against.** |

`tier_v3` is the tier after the Week 1–6 corrections. It does not exist yet, and every
prediction in §7 below is registered before it does.

**One honesty note carried forward.** The `tier_v2` MLIP rescore in docs/41 §6f was run
*after* the corrections were known. It discharges the docs/39 §4 commitment but it is
**not a blind test**. §7 of this document exists so that the `tier_v3` comparison is one.

---

## 0a. What the archive audit found, before any pilot ran

Block 1D was run first, on 2026-08-09, because it costs nothing. Its result (docs/41 §6g)
changes what block 1A can claim, so it is recorded here as part of the pre-pilot record
rather than being discovered later and folded in.

**The tier was never computed under one protocol.** Of the 20 production adsorbate
relaxations, 9 are LOCKED (pw.x kept a mirror and symmetrised F_y to exactly zero), 6 are
ON_PLANE (`nosym` was set but the out-of-plane force never rose above 1e-4 Ry/au, so nothing
ever left the plane), and 5 EXPLORED. **75% were confined either way.** The class is
predicted 20-for-20 by whether one line — `nosym = .true.` — was present in the deck; it is
absent for Cr, Ir and Ru and present for Mn, Fe, Co, Ni and Cu.

*Corrected 2026-08-09 under amendment 1: an earlier draft of this paragraph attributed
the split to the endmember rescue ladder. The real cause is `qe_slab.py`, which passed
`nosym = False` for adsorbate decks under the justification "an adsorbate lowers the
symmetry by itself ... same physics, 2.4x the bill" — both premises false, adopted
deliberately on 2026-07-31 in commit `1a3a77b` as a cost optimisation. See docs/41 §6g.*

Three consequences are registered here, in advance:

1. **The "mirror" arm of block 1A reproduces the production protocol only for Cr, Ir and
   Ru.** For the other four metals there is no production mirror arm to compare against,
   because they already ran with `nosym`. The tier-wide correction is therefore **not**
   "apply a symmetry fix to seven metals" — it is "bring seven metals onto one protocol,
   from three different starting positions." The report must say this rather than
   presenting a uniform correction.
2. **`nosym` is not a treatment.** Six of the eleven states that had it never left the
   plane. Any claim that a state was searched off-plane must cite its measured max\|F_y\|,
   never the presence of the flag.
3. **A new internal control, pre-registered.** If the confinement classes are causal rather
   than coincidental, then in the core sweep the metals whose production runs are LOCKED
   (Cr, Ir, Ru) must show **larger** symmetry corrections than the ones that EXPLORED (Mn,
   Co). Concretely: **median \|ΔE_sym\| over LOCKED states ≥ 2× the median over EXPLORED
   states.** If instead EXPLORED metals show corrections as large, then the confinement
   class is not what governs the error, the correlation with the campaign's three
   unexplained problems is a coincidence of n = 8, and that must be reported as a
   refutation of our own mechanism.

**The correlation that motivates all of this, stated with its weakness.** The three LOCKED
metals are exactly Cr (withdrawn headline), Ir (scaling anomaly, fixed by an off-plane
restart) and Ru (descriptor deficit surviving six closed negatives); and Mn — the only
endmember clean across all four states — is one of only two that EXPLORED. That is a
striking pattern on **n = 8 metals**, and confinement is confounded with which era built the
deck. It is hypothesis-generating. Point 3 above is how it gets tested.

---

## 1. Closing the P10 gap

docs/41 §5 declared a verdict for a symmetry-escape energy of **≥ 0.30 eV** (trapped;
tier-wide retraction) and for **< 0.10 eV** (exonerated). Ir's `yaw90` came in at
**−0.2913 eV** — 9 meV below the trigger and three times above the exoneration bin. There
was no rule for that value, and assigning it to a bin after the fact is exactly the
circularity docs/41 §6a warns about. The result was therefore recorded as unbinnable, and
it still is.

Two things were wrong with the old criterion, not one.

**It had a hole.** Two bins over a continuous quantity, with a gap between them.

**It was stated in the wrong variable.** A raw ΔE on one state is not what the campaign
cares about. What matters is whether the correction changes the *overpotential* and the
*scaling constant* — and those depend on which rung is potential-limiting, so the same
ΔE means different things on different metals. Cr is `pls = 2`: lowering its `*OOH` by
0.2 eV moves η by exactly **zero**. Ru is `pls = 3`: the same 0.2 eV moves η by 0.2 V.

### P12 — the symmetry-escape criterion, restated

For each (metal, state), let ΔE_sym = E(off-plane, GATE-1-passed) − E(mirror,
GATE-1-passed) ≤ 0. Propagate it through the full CHE chain and compare the corrected
quantities against `tier_v2`:

| bin | condition | declared action |
|---|---|---|
| **TRAPPED** | \|Δη\| ≥ 0.10 V **or** \|Δc_M\| ≥ 0.20 eV | the on-record value for that metal is withdrawn; the tier is recomputed |
| **MATERIAL-BUT-SUBCRITICAL** | anything in between | **reported with its number as a non-zero row in the error budget.** Does *not* trigger a retraction. This bin is the fix: it exists, it is named, and it has an action. |
| **NEGLIGIBLE** | \|Δη\| < 0.03 V **and** \|Δc_M\| < 0.05 eV | recorded as a closed negative for that metal |

Three bins, no gap, and the middle one is a reporting obligation rather than a judgement
call. Ir's −0.291 eV re-scored under this rule is unambiguously TRAPPED (Δη = 0.291 V,
Δc_M = 0.291 eV), which is the right answer and the reason the old criterion felt wrong.

**A sign constraint that can fail.** ΔE_sym ≤ 0 by construction — an additional search
direction cannot raise the minimum. **Any ΔE_sym > +0.02 eV is a failure of the search or
of the comparison, not a physical result**, and voids that arm rather than being reported
as "symmetry doesn't matter here."

---

## 2. P13 — block 1A, the cell × symmetry factorial

### Why it is a factorial and not a sequence

docs/41 §2e records that repeating the 1×1-vs-2×1 comparison *with* orientational starts
collapsed Ir's lateral interaction term from **+0.382 eV to +0.007 eV**. The symmetry
trap and the periodic image are therefore not two independent corrections that can be
measured separately and added; on the evidence in hand they are the same 0.3 eV seen
twice. A staged design cannot tell them apart, and a campaign that stages them will
double-count. This block crosses them.

### Design

Metals Cr, Ir, Ru × cells {1×1, 2×1 neighbour-vacant, 2×1 neighbour-`*O`} × symmetry
{mirror, off-plane}, with each arm's own reference computed in the same cell at the same
settings. Off-plane means the adsorbate yawed off the mirror plane **and** `nosym=.true.
noinv=.true.` **and** a physical displacement — `nosym` alone does nothing when the input
is exactly symmetric, because F_y stays at ~1e-8 against a 1e-3 threshold.

**States: `*O`, `*OH`, `*OOH` — not `*OH` and `*OOH` alone.** The plan as drafted omitted
`*O`, and that omission would have made the block unable to answer its own question. Ru's
entire anchor failure is ΔG_O − ΔG_OH = 1.163 eV against an apex of 1.60 (docs/41 P4), and
Cr, Mn and Fe are all `pls = 2`, which is also a ΔG_O − ΔG_OH quantity. Testing symmetry on
`*OOH` only can move Ir and Ru's ΔG_OOH and can move nothing at all for a `pls = 2` metal.
`*O` is added on that reasoning, recorded here before the results exist.

### Pre-registered predictions

**Replication (gating).** Ir `*OOH`, 1×1, off-plane must reproduce ΔE_sym = **−0.291 ±
0.05 eV**. This is a pipeline control, not a measurement: it is a job we have already run.
A miss voids the block and the pipeline is debugged before anything else is read.

**Cr `*OOH` will not move η(Cr), and this is a prediction, not a hedge.** Cr is `pls = 2`
with ΔG₂ = 1.560 and ΔG₄ = 0.300 eV. For ΔG₄ to become the maximum, ΔG_OOH would have to
fall by **1.26 eV**. No symmetry escape on record is within a factor of four of that.
Therefore: Cr's `*OOH` symmetry correction is predicted to change η(Cr) by **exactly zero**
while changing Cr's scaling constant c_Cr by the full ΔE_sym. If η(Cr) moves at all, the
CHE bookkeeping is wrong and must be audited before the number is used.

**Interaction.** Define I = ΔE_sym(2×1 vacant) − ΔE_sym(1×1) per (metal, state).

| \|I\| | declared reading |
|---|---|
| < 0.05 eV | the two effects are additive. The campaign may report them as separate corrections and may decompose the waterfall in Figure 1 Panel A. |
| ≥ 0.30 eV | **not separable.** Only the fully-corrected cell is reportable. Figure 1 Panel A collapses those two steps into one labelled "cell + symmetry (not decomposable)", and the report says so in words. This is the R5 fallback and it is a legitimate result. |
| 0.05–0.30 eV | inconclusive. Reported as inconclusive. Not rounded toward either. |

*Prior, stated so it can be wrong:* on the §2e evidence I expect \|I\| ≥ 0.30 eV for Ir
`*OOH`, i.e. **not separable**. If the interaction turns out small, the collinearity worry
that reshaped this whole program was overstated and that must be said plainly.

**Ru.** Ru's measured `*OOH` trap is 82 meV and left its descriptor untouched. Predicted
\|ΔE_sym(Ru, `*OOH`)\| ≤ 0.15 eV. **Ru `*O` is the open question** — it has never been
tested, and it is the only state that can move Ru's descriptor. No prediction is offered
for its magnitude; the direction is constrained by the sign rule in §1.

**Ru gets worse under the coverage arm.** Diluting to ½ ML independently takes Ir's c from
3.652 to ~3.11, and Ru's descriptor from 1.163 toward ~1.01 — i.e. **further from the
apex.** This is registered now so that it is not presented later as a surprise or quietly
dropped.

### The production-cell decision, declared in advance

Adopt 2×1-vacant as the production cell if the per-adsorbate adsorption energy differs
from 1×1 by **≥ 0.10 eV** on any of the three metals in the **off-plane** arm (the mirror
arm cannot be used for this decision, because §2e shows the mirror arm's cell effect is
largely an artifact of the constraint). Otherwise keep 1×1 and publish the measured bound.

If the 2×1 + `*O`-neighbour arm differs from 2×1-vacant by ≥ 0.10 eV, the resting-state
coverage is itself a live variable; it is then added as its own error-budget row and is
**not** resolved by picking one of the two.

---

## 3. P14 — block 1C, the Hessian test

### What is actually being claimed

That a lower-energy off-plane minimum exists does **not** establish that the mirror
geometry is a saddle point. A barrier could separate them, in which case the published
mirror-plane geometries are genuine local minima and the field's practice is defensible.
The distinction matters, and the Hessian is the only thing that settles it. This is the
load-bearing novel object of the lead contribution — the *existence* of the precaution has
been known on rutile(110) since at least 1995 (Goniakowski & Gillan, **citation
unverified**, see §9).

### Method, fixed in advance

Partial Hessian on the adsorbate atoms only, central finite differences of forces,
δ = 0.01 Å, `nfree = 2` → 18 displaced SCFs plus one reference per state. `conv_thr = 1e-10`.
`nosym = .true.` and `noinv = .true.` on **every** displacement *including the reference* —
a +y displacement breaks a mirror the reference still has, and with symmetry on the two are
computed in different point groups and the differences are meaningless. Identical k-point
set throughout. States: Ir `*OOH` at `runs/Ir_anchor/s0_OOH.out`, and Cr `*OOH` at the
**basin-corrected** geometry `runs/probe/Cr_basin/s0_OOH.out` — not the production one,
which is a known-wrong magnetic solution 178.58 meV high.

### Validity gates (a failed gate voids the state; it is not reported with a caveat)

- **Hessian symmetry:** max\|H_ij − H_ji\| / max\|H_ij\| ≤ **0.05**.
- **Magnetic guard:** any displacement whose total magnetisation differs from the reference
  by > **0.1 μ_B** changed basin; its force row is contaminated. Such rows are excluded and
  listed. **More than 2 exclusions of 18 voids the state.**

### Verdict criteria

| verdict | condition |
|---|---|
| **CONFIRMED** | ≥ 1 imaginary mode with \|ω\| ≥ **50 cm⁻¹** whose eigenvector carries ≥ **50%** of its weight on the mirror-normal (y) component |
| **AMBIGUOUS** | an imaginary mode with 20 ≤ \|ω\| < 50 cm⁻¹, or \|ω\| ≥ 50 cm⁻¹ with < 50% y-character |
| **REFUTED** | no imaginary mode above 20 cm⁻¹ |

Anything softer than ~i·50 cm⁻¹ is numerical noise rather than a saddle. We say so here
rather than waiting for a referee to say it.

### Declared consequence of REFUTED

If **both** pilot states come back REFUTED, the saddle-point claim is wrong: the mirror
geometries are genuine local minima behind a barrier. The lead contribution then loses its
proof and the report reweights to **S1 (the scaling-floor decomposition) + S4 (the error
budget and the resolution number)** as the lead, with the symmetry effect reported as an
energy measurement carrying a number and no saddle-point language. That is risk R3, it is
a weaker paper, and it is still a paper. This branch is written down now so that a null
result cannot be quietly reframed in October.

---

## 4. P15 — block 1B, the *U* gate

### Why the external number cannot be the gate

The program's draft criterion was "hp.x on bulk rutile TiO₂ should return ≈ 4.9 eV." That
value comes from a citation we **could not verify** — the search budget was exhausted and
both OpenAlex and Semantic Scholar returned HTTP 429. Building a go/no-go on an unchecked
number would make the gate itself unfalsifiable. So the gate is split.

**External part (wide, deliberately).** GO requires U(Ti-3d, rutile TiO₂, atomic
projectors) ∈ **[3.0, 7.0] eV**. The question this answers is "does hp.x produce a
physically sane number on a closed-shell system we understand," not "does it reproduce a
specific literature value." If the literature value is later verified, the narrower
comparison is reported as an additional check, not as the gate.

**Internal part (the real gate; no citation required).** All four must pass:

| check | threshold | what it catches |
|---|---|---|
| q-mesh convergence | ΔU < 0.2 eV vs the next finer mesh | an under-converged response |
| response-matrix symmetry | max\|χ_ij − χ_ji\| / max\|χ_ij\| ≤ 0.05 | a broken linear-response setup |
| perturbation-amplitude independence | ΔU < 0.1 eV when the amplitude is halved | leaving the linear regime |
| symmetry-equivalent perturbed atoms | agree within 0.05 eV | an inconsistent projector or k-set |

### Declared consequence of NO-GO

**A0 ships regardless.** The η(U) grid over 0–9 eV from pw.x alone (140 fixed-geometry
SCFs, block 6A) does not depend on hp.x at all, and it answers P7. On a NO-GO, S2
downgrades from *"we computed U from first principles"* to *"we bracketed U with three
independent determinations (MP-fitted, Xu supercell linear response, literature DFPT)"*,
and the report states that hp.x was attempted and did not validate, with the failing check
named.

### A separate gate for the slab

**A successful bulk validation does not license a slab U.** hp.x on a magnetic 3d oxide
slab is a materially harder problem than on a closed-shell bulk insulator, no published
protocol exists for it, and docs/42's own caveat is that availability is not competence.
The slab is its own GO/NO-GO against the same four internal checks, run in Week 2–3. U is
held **fixed per metal across that metal's four rungs** — recomputing U per adsorbate would
make the four CHE rungs non-comparable, and that approximation is stated in the report
rather than hidden.

---

## 5. P16 — separating a geometry effect from a basin change

This applies to every block, and it is the generalisation of what P10 could not do.

- Any state whose **total magnetisation differs by > 0.1 μ_B** between the constrained and
  the free solution is **CONFOUNDED**: its energy difference mixes a geometry effect with a
  magnetic basin change and cannot be attributed to either. Confounded states go in their
  own table, are excluded from every symmetry-effect statistic, and are counted in the
  report.
- **Every** relaxation in this campaign, in every block, gets a GATE-1 fresh-density
  fixed-geometry SCF at its own final coordinates. If that SCF lands ≥ 5 meV lower, the
  state is re-relaxed from it and the loop repeats until GATE-1 passes. The number of
  iterations per state is published.
- docs/41 §6f established that the GATE-1 SCF **is** the correction to within 2–3.5 meV —
  relaxing on the corrected surface bought only 3.46 / 1.99 / 2.81 meV on Cr / Co / Ni.
  Where a full re-relaxation is not affordable, the GATE-1 energy may be quoted as the
  correction **with a stated 4 meV residual**, and that substitution must be marked in the
  per-state depth table.

---

## 6. P17 — the scaling-floor acceptance gate

Since ΔG₂ + ΔG₃ ≡ c_M = ΔG_OOH − ΔG_OH once the 4.92 eV total is imposed,

> **η ≥ c_M/2 − 1.23, exactly.**

Verified numerically: the identity holds to 1e-9 on every full chain in the archive.

Every corrected tier must publish, per metal, c_M, the floor, the excess η − floor, and
z = (c_M − 3.18)/0.12 against the pooled universal value (Divanis 2020 — **citation
unverified**, §9; the gate is stated now and the reference value is re-confirmed before
publication).

**The gate:** a correction that moves η by ≥ 0.10 V while leaving \|z\| ≥ 3 **has not fixed
the scaling anomaly** and must be reported as such rather than as a resolution.

Baseline at `tier_v2`, for the record: Cr c = 3.102 floor 0.321 excess **0.009**; Ir 3.652 /
0.596 / 0.185; Ru 3.180 / 0.360 / 0.427; Mn 3.034 / 0.287 / 0.604; Fe 2.711 / 0.125 / 1.138.
Cr sits essentially **on** its floor, which means Cr's low η is scaling-limited, not
descriptor-limited, and no correction that leaves c_Cr near 3.10 can improve it.

---

## 7. P18 — the MLIP degradation against `tier_v3`, registered before it exists

Measured so far, same matched-protocol pipeline, n = 7, exact permutation p:

| head | vs `tier_v1` | vs `tier_v2` |
|---|---|---|
| UMA `uma-s-1p2`, `omat` | ρ = +0.9643, p = 0.0028, MAE 0.125 V | ρ = +0.8929, p = 0.0123, MAE 0.134 V |
| MACE `medium-mpa-0` | ρ = +0.8571, p = 0.0238, MAE 0.173 V | ρ = +0.8214, p = 0.0341, MAE 0.146 V |

**Predictions for `tier_v3`, written before the corrections are computed:**

1. Both ρ fall further. Point predictions **ρ(omat) = 0.79** and **ρ(MACE) = 0.71**;
   intervals [0.60, 0.90] and [0.50, 0.85].
2. MAE rises: omat to **0.15–0.25 V**, MACE to **0.15–0.28 V**.
3. **The sharp one.** MACE-MPA-0 trains on MPtrj at exactly the Materials Project U set,
   with U = 0 on Ru and Ir — *the identical partition this campaign uses*. Its current
   agreement is therefore partly a shared Hubbard convention rather than shared physics.
   `omat` is trained on OMat24, which does not share that convention. So if `tier_v3`
   adopts a DFPT U, **Δρ(MACE) must be more negative than Δρ(omat)**. If instead MACE
   degrades *less* than `omat`, the shared-convention explanation is wrong and that is
   reported as a refutation of our own mechanism.
4. **The falsifier that would be good news.** If either ρ *increases* against `tier_v3`,
   the corrections moved the DFT tier *toward* the MLIP prediction — i.e. the models were
   closer to the truth than the uncorrected DFT was. That outcome is reported as
   prominently as a degradation would be, per the standing docs/39 §4 commitment.

Nothing in this section may be revised after the deposit. The comparison in Week 8 is
blind because this section exists.

---

## 8. P19 — the uniformity rule

η is a difference against the clean slab. Auditing `*OOH` deeply and the clean slab
shallowly injects a new systematic of unknown sign into every rung at once. Co's **+59 meV
clean-slab drift** is the proof that the reference is not safe.

- **Audit depth is declared per metal and applied identically to all four states**,
  including states expected to be clean. The per-state depth table is published.
- Within a metal, the orientational grid size may vary by state **only** according to a
  fixed declared function of that state's actual orientational freedom — clean ×1, `*O` ×2,
  `*OH` ×3, `*OOH` ×4 — never by per-state judgement.
- The clean slab is audited at the **same magnetic depth as the deepest adsorbate state**
  of that metal.
- Holes are reported as holes, with the state named and the reason given. A missing state
  is never silently replaced by a bound without the bound being labelled as one.

---

## 9. What would falsify the lead contribution

Registered in advance so that none of these can be reframed later:

- **Both Hessian pilots REFUTED** → the saddle-point claim is wrong; reweight to S1 + S4
  per §3.
- **Symmetry moves η by < 0.03 V on every 3d metal, and \|I\| < 0.05 eV** → the symmetry
  error class is real but not tier-relevant; it drops from a headline error class to a
  footnote, and the lead becomes a two-class paper.
- **GATE-1 finds no further multistable states in the remaining 10 of 28** → the rate is
  5/28 ≈ 18%, Wilson 95% CI roughly 8–35%, which overlaps AdsorbML's published 9–19% ML+RX
  band. The multiplicity result is then stated as *consistent with published rates in a new
  setting*, not as a new phenomenon. A count with a Wilson interval is reported in every
  case; **a bare percentage is never reported**, because at n = 28 the interval is ±18
  points.
- **hp.x U lands within 0.5 eV of the MP U for all seven metals** → P7's 1.122 V range is a
  sensitivity result, not an error; S2 collapses from a correction to a confirmation, and
  the report says the imported U was, in the event, adequate.

---

## 10. Standing caveats

- **Every external citation used in this document is unverified.** The web-search budget
  was exhausted and both OpenAlex and Semantic Scholar returned HTTP 429 on 2026-08-09.
  This specifically includes the two that are load-bearing for novelty — Goniakowski &
  Gillan, *Surf. Sci.* (1995), and Deshpande, Kitchin & Viswanathan, *ACS Catal.* **6**,
  5251 (2016) — and the Divanis (2020) pooled c = 3.18 ± 0.12 eV used in §6. Each must be
  confirmed from the actual paper before it is cited in the report or used to concede a
  novelty claim. Thresholds in this document that reference them are stated as thresholds,
  not as agreements with the literature, precisely so that a citation failure does not
  invalidate the pre-registration.
- Blocks 1A and 1C start from production final geometries. Second-order effects of
  re-relaxing the slab under a changed cell are inside block 1A (which relaxes) and outside
  block 1C (which does not, by construction — it is a Hessian at a fixed point).
- The apex value 1.60 eV and band centre 3.2 eV are Man (2011) conventions, inherited from
  docs/32 and docs/41. Every threshold here is stated as a *movement*, so none depends on
  the exact centre of either band.
- `tier_v2`'s Co and Ni entries are **bounds, not measurements** — neither metal has a
  converged `*OOH`. Their windows are [2.91, 5.40] and [2.50, 6.97] eV and both comfortably
  contain every ΔG_OOH on record, but a bound is labelled as a bound everywhere it appears.
- Nothing here touches the melt list or the experimental protocol, which are pre-registered
  separately before the Week-3 pilot.

---

# AMENDMENT 1 — 2026-08-09, before any block-1A/1B/1C job was launched

**Status when written.** No job of blocks 1A, 1B or 1C had run. One exception, declared
here so it cannot look like an omission later: a single SCF,
`runs/probe/Ir_hess/s0_OOH__hess_ref`, was launched at 18:55 UTC as a **throwaway
feasibility probe** to measure whether `conv_thr = 1e-10` is reachable at all on this
system and in how many iterations. **Its output will not be used as the Hessian reference
for any verdict.** The reference will be recomputed under the final protocol. It exists
only to answer a cost question the whole 1C block was about to be built on.

**Why this amendment exists.** The Week-1 decks were built and then adversarially verified
by six independent reviewers, who returned **31 blocking findings and six FIX_FIRST
verdicts — none of the three blocks was safe to launch.** Several findings are genuine
improvements to the pre-registration itself rather than to the code. Those are recorded
here, in advance, with the previous wording quoted beside the new one. The pre-amendment
document is archived verbatim at
`docs/43-prereg-week1-factorial-archive-2026-08-09-pre-amendment-1.md`.

**A correction folded in.** §0a's account of *why* the tier carries two protocols was
wrong in its first draft (it blamed the rescue ladder). The real cause — a deliberate
cost optimisation whose stated justification was false — is now in §0a and docs/41 §6g.
The audit numbers themselves never changed.

**A rule this amendment establishes.** Three builders each wrote their own `PREREG` block
into source files, and all three contradicted §2/§3/§4 of this document. **docs/43 is the
only pre-registration.** In-code rules must be a pointer to it, never a copy. A rule that
exists in two places is a rule that will be read in whichever version suits the result.

---

## §2-A — block 1A (cell × symmetry). Amendment 1.

**1. `*O` is confirmed IN, against the builder's omission.** §2 already required `*O` and
gave the reason. The builder excluded it on the argument that "`*O` has no orientational
degree of freedom, so it cannot populate the symmetry arm." That argument is false by the
builder's own construction: a single O cannot be *yawed*, but it can be *translated* off
the mirror plane, and the builder already implements exactly that operation (`kick_y`,
0.35 Å) for the 2×1o spectator. Without ΔG_O in the 2×1 cells, ΔG₂ and ΔG₃ are both
uncomputable, so P12's primary bin boundary |Δη| ≥ 0.10 V could not be evaluated for any
metal and `tier_v3` could not be built from this block. Off-plane treatment for `*O` is a
y-translation of ≥ 0.30 Å plus `nosym`/`noinv`.

**2. The 2×1o spectator must not differ between the symmetry arms.** §2 asserted that the
spectator leaves the interaction term "unaffected either way". **That was wrong as built**
and is withdrawn. The reference does cancel from the symmetry effect S(c) = E(c,off) −
E(c,mir); it does *not* cancel from the interaction S(2×1o) − S(2×1v) if the spectator is
kicked in the `off` deck and pinned in the `mir` deck, because then S(2×1o) contains the
spectator's own off-plane relaxation energy and S(2×1v) does not. The interaction term is
the entire reason this is a crossed design rather than two experiments.

*Registered fix:* the kick is applied to `ref__2x1o` only, never to the 2×1o adslab `off`
decks — with the working adsorbate yawed and `nosym` set, the cell has no mirror and the
spectator is already free without being *pushed differently* between arms.

*Registered contingency, before the fact:* if `ref__2x1o`'s spectator relaxes to
\|Δy\| > 0.02 Å, a `ref__2x1o_mir` job is added **before** the interaction is scored.

**3. Cr gets a magnetic-basin control, and it is a precondition of the readout.** §5
already requires GATE-1-passed energies; block 1A as built had no GATE-1 for its ten new
Cr relaxations. The drifts this catches are the same size as the effect being measured
(Cr `*OOH` −178.58 meV, Co `*OH` −406.51 meV, against an Ir symmetry escape of −291 meV),
and a basin flip between the Cr mirror and Cr off-plane runs is indistinguishable from
ΔE_sym in the output — no `SCF_FAIL`, no force anomaly, no QC refusal. Doubling the cell
makes it worse, not better: the 2×1 admits orderings along [001] the 1×1 cannot represent.
Registered, both parts:

- **(a)** total and absolute magnetisation are recorded for every Cr job, and the `mir`
  and `off` members of each Cr pair must agree to within **0.1 μ_B**. A pair that fails is
  **CONFOUNDED** under §5, excluded from the symmetry statistics, and reported separately.
  This is free — pw.x prints it every iteration.
- **(b)** one fixed-geometry fresh-density SCF per Cr 2×1 relaxation at its own final
  coordinates, required to agree to **≤ 5 meV**. ~25 h against a Cr arm of several hundred.

**4. GATE C is an energy *and* magnetisation test.** The registered check
\|E(2×1 clean) − 2·E(1×1 clean at the folded mesh)\| ≤ 5 meV can be passed by a different
magnetic state at near-degeneracy. Magnetisation must match to 0.1 μ_B as well.

**5. Cr's k-mesh bridge is measured, not assumed.** Cr's production 1×1 mesh is 9 4 1 and
9 is odd, so no integer 2×1 mesh folds onto it (Ru and Ir run 8 4 1, which folds exactly).
Cr therefore runs the same 4 4 1 as the others, and the 9 → 8 shift is measured explicitly
by three fixed-geometry SCFs of the Cr 1×1 mirror states at 8 4 1. The k-sensitivity
becomes a published number instead of a term hiding inside the cell effect.

---

## §3-A — block 1C (Hessian). Amendment 1.

**The verdict logic as coded could not return its own falsifying answer.** This is the most
serious class of finding in the review, and it is registered here rather than fixed quietly.

**1. Two new per-state verdicts. CONFIRMED and REFUTED now require the gates to have
passed.** As coded, every quality-gate failure routed to AMBIGUOUS, and the campaign rule
then printed *"NEITHER CONFIRMED → R3 TRIGGERED. Do not spend the 378 SCFs."* A reviewer
demonstrated it: 19 synthetic outputs whose only defect was a missed `conv_thr` produced
exactly that sentence. **A compute failure was indistinguishable from a scientific null at
the decision layer** — and since `conv_thr = 1e-10` had never been reached anywhere in this
project, that was the *likely* outcome, not a corner case.

| verdict | condition |
|---|---|
| **CONFIRMED** | gates passed; ≥ 1 imaginary mode at or above its effective floor with ≥ 50% y-character |
| **REFUTED** | gates passed; no imaginary mode reaches its effective floor |
| **AMBIGUOUS** | gates passed; an imaginary mode above floor but < 50% y-character |
| **UNDERPOWERED** | gates passed, but the effective floor on the highest-y-character mode exceeds **i80 cm⁻¹** |
| **VOID** | any gate failed. **Not a scientific result.** |

The campaign-level rule returns **"PILOT INVALID — no campaign decision"** if any state is
VOID, and **"rerun at tighter conv_thr"** if any state is UNDERPOWERED. **Only gate-clean
CONFIRMED/REFUTED states may trigger the R3 branch of §3.**

**2. REFUTED is made reachable.** §3 defined REFUTED as "no imaginary mode above 20 cm⁻¹"
while the code routed *any* sub-floor imaginary eigenvalue to AMBIGUOUS — so a spectrum
carrying one mode at i5 cm⁻¹ returned AMBIGUOUS, and the §3 consequence keyed on the words
"both pilot states come back REFUTED" could never fire. That is precisely the quiet
reframing §3 exists to prevent. Sub-floor imaginary modes now route to **REFUTED**, named
in the reason string, with the largest reported as a number.

**3. The floor is per-mode, and blindness is not a null.** Effective floor =
max(50 cm⁻¹, 3σ), with σ propagated from the measured force noise. The out-of-plane modes
of `*OOH` are H-dominated, and at the design σ_F the effective floor on an H-carried mode
is **≈ i111 cm⁻¹**, not the i50 registered — so the pilot can be structurally incapable of
seeing the mode it exists to detect. §3's "~70 cm⁻¹" was a 1σ figure quoted against a 3σ
rule and is corrected. Hence the UNDERPOWERED verdict above.

**4. The Hessian symmetry gate becomes absolute.** §3 set a relative gate,
max\|H_ij − H_ji\| / max\|H_ij\| ≤ 0.05. max\|H_ij\| is dominated by the O–H stretch
(~48 eV/Å²/amu), so 5% of it is ~2.4 against an expected asymmetry of ~0.05 — **the
registered gate was toothless.** Replaced by an absolute threshold on
max\|H_ij − H_ji\|. Withdrawn with the reason stated, not silently retuned.

**5. New gate Q0 — the reference must be the state it claims to be.** All 19 jobs start
from a fresh atomic superposition, so they can agree with each other while collectively
sitting in the wrong basin — the exact defect docs/41 §6f was written about. Required:
\|E_ref − E_source_relax\| ≤ 10 meV, and for nspin = 2, \|M_ref − M_source\| ≤ 0.1 μ_B.

**6. Unchanged, against the builder.** Magnetic exclusions still void a state only at
**more than 2 of 18**, not at the first one; and CONFIRMED still requires ≥ **50%**
y-character, not 90%. Neither change came with a stated reason, and a registered threshold
is not moved without one.

**7. Scope. Every 1C verdict is scoped to "at q = 0, in the 1×1 cell, at 1 ML."** The Cr
`*OOH` geometry carries a low-barrier hydrogen bond to its own periodic image along the cus
row — H···O = **1.338 Å**, O···O = 2.399 Å (Ir is the same class but milder, 2.516 Å). The
two modes most likely to come back imaginary — the OOH yaw and the H torsion — are on Cr
governed by that image contact rather than by the mirror constraint the paper is about, so
a CONFIRMED on Cr at 1×1 would be attributed to the symmetry trap when its cause is the
coverage. A proton in a 2.40 Å O···O bond is also the worst possible case for a harmonic
central difference. Registered additions:

- **Cr is held** until block 1A returns its cell verdict, then run in the chosen production
  cell. **Ir runs now** — milder, and it is the state with the known −291 meV escape, so it
  is the one the saddle-point claim most needs.
- REFUTED gains, alongside the existing "confined to the adsorbate" caveat: *an all-real
  Γ-point spectrum in a 1×1 cell does not exclude an instability at another wavevector.*

**8. The verdict is taken from the y-axis block.** Every ±x and ±z deck is exactly
mirror-symmetric, so F_y ≡ 0 by symmetry in all of them and all 18 y/xz cross-elements of
H are structurally zero. Those decks measure noise, not physics, for 1C's purposes. They
are bought for block 2B's in-house ZPE/−TS table and that is now their stated reason;
**1C's verdict rests on the ±y block.** The ±y central difference is kept for its √2 noise
gain.

---

## §4-A — block 1B (hp.x). Amendment 1.

**1. The external window stays [3.0, 7.0] eV.** The builder widened it to [2.0, 8.0] with
no physics reason given. "Catch a broken calculation" is satisfied by the narrower window.

**2. The amplitude-independence criterion is WITHDRAWN, with its reason.** §4 listed it as
one of four internal checks. **hp.x is DFPT — there is no perturbation-amplitude keyword in
the binary's input-variable list**, so the check was not merely unmet, it was
unperformable. Registering an impossible criterion is worse than registering none. Replaced
by check 4′ below.

**3. Check 4′, and it is the one that matters: a magnetic, metallic arm.** The TiO₂ target
is nspin = 1, `occupations = 'fixed'`, a d⁰ closed-shell insulator with an empty Hubbard
manifold. Production (blocks 2C and 3Y) is nspin = 2, smearing, metallic, partially-filled
3d — six co-varying differences, and hp.x is known to take a *different branch* on gapped
versus smeared systems. **A GO on TiO₂ alone licenses only the sentence "hp.x validates on
a closed-shell bulk insulator", which is not what the campaign needs.** Registered: one
bulk rutile CrO₂ arm (nspin = 2, smearing mv/0.01, U(Cr-3d) seed 1e-8, `find_atpert = 1`,
nq 2×2×2 — roughly ten minutes of the box) must print a finite U with **zero** "Convergence
has not been reached" lines. If it does not, the GO is scoped to the closed-shell statement
and the slab U is not attempted in Week 2.

**4. The χ-symmetry check is demoted to a reported diagnostic, pending one measurement.**
hp.x appears to *symmetrise* the response matrices and reconstruct unperturbed rows
(`hp_symdnsq.f90`, `hp_rotate_dnsq.f90`, and the runtime string "RESPONSE OCCUPATION
MATRICES (SYMMETRIZED):"), in which case a symmetry test on its printed χ is an identity
and passes vacuously — **a hard gate that cannot fail is not a gate.** Whether the printed
χ is pre- or post-symmetrisation is settled by reading one completed `iverbosity = 2` run.
Until then it is reported, not gated, and **the real reproducibility test is
`find_atpert = 4` with two independently perturbed Ti agreeing within 0.05 eV** — unchanged
from §4's fourth check, and now load-bearing.

**5. The cost model must be per-(atom, q), scaled by the measured NSCF k-count.** As built
it applied a flat cost to all 102 (atom, q) pairs, anchored on nq = 2×2×2 — the one mesh in
which **every** q is a time-reversal-invariant momentum, so hp.x gets maximum symmetry
reduction at every measured point — and the slab timing deck measured **q = Γ**, the
cheapest point that exists. Measured k-counts on the shipped ground state: 65 at Γ, 130 at
the zone boundary, 208 at nq 3×3×3 q#2, **576** at nq 4×4×4 q#14. A cost model built on Γ
and TRIM points understates a general q by up to ~9×, and block 3Y is the thing this model
exists to protect. Registered: cost scales with n_k(q), which hp.x prints for every q, and
the slab timing is taken at a **general, non-Γ** q.

---

# AMENDMENT 2 — 2026-08-09, after the feasibility probe, before any 1C production job

## The probe returned, and it closes one question and opens another

`runs/probe/Ir_hess/s0_OOH__hess_ref` — the throwaway feasibility probe registered in
amendment 1 — completed. Its files are renamed
`*.THROWAWAY-convthr-feasibility-probe-2026-08-09.*` so they cannot be mistaken for a
Hessian reference.

| | |
|---|---|
| `conv_thr = 1e-10` reached? | **yes** — "convergence has been achieved in **30 iterations**" |
| final accuracy | 6.9e-11 Ry, descending cleanly at ~0.36 decades/iteration, **no plateau** |
| cost | **639 s** at NP = 20 |
| final `ethr` | **1.79e-13** |

**Closed:** `conv_thr = 1e-10` is reachable and cheap on this system. It had never been
reached anywhere in this project — the deepest on record was 5.7e-9 — and the entire 1C
block was about to be built on the assumption. 30 iterations sits comfortably inside
`electron_maxstep`, so the 18.4 h stall the review projected does not happen.

## Opened, and it invalidates a registered response

**The escalation path this document registered does not exist.** §3-A.1 declares the
response to an UNDERPOWERED verdict as *"rerun at tighter `conv_thr`"*. The probe shows why
that cannot work: QE clamps the Davidson threshold at `ethr = MAX(ethr, 1e-13)`, and at
`conv_thr = 1e-10` this system already sits at **ethr = 1.79e-13** — a factor of 1.8 above
the clamp. A further two decades of `conv_thr` would demand ethr ≈ 1.8e-15, which the clamp
forbids, so the SCF could not reach the requested threshold and would return
"convergence NOT achieved" — a VOID, not a tighter measurement.

**Registered replacement.** The response to UNDERPOWERED is **a larger displacement, not a
tighter `conv_thr`.** The Hessian's noise scales as σ_F/δ while its anharmonic error scales
as δ, so with σ_F pinned at the floor the only remaining lever is δ. On an UNDERPOWERED
verdict the state is re-run at **δ = 0.02 Å**, and the two δ values are reported together —
agreement between them is itself evidence that the harmonic regime holds, and disagreement
is reported rather than averaged.

This is registered now, before any 1C production job, because it was found by a
639-second probe rather than after a 38-job block returned VOID.

## Also registered: the 1×1 mirror arm must be re-emitted, not reused

The review found (N11) that the 1×1 comparison is not controlled. `write_probe` hardcodes
`mixing_mode = 'local-TF'`, and Cr's production **adslab** decks carry no `mixing_mode` at
all. §2 as written reuses the production run as the 1×1/mirror row and emits a new deck for
the 1×1/off row — so the pair differs in the mixing scheme as well as in the symmetry.

Mixing does not change a converged solution *in general*, but this campaign's entire subject
is that it can change **which** solution is converged to: the same Cr `*OOH` geometry gives
−1636.47080 Ry from the production relax and −1636.48367 Ry from a fresh local-TF SCF, a
178.58 meV basin difference (docs/41 §6f). Mixing and starting density are confounded there,
and the pilot must not inherit that confound.

**Registered fix:** the 1×1/mirror rows are **re-emitted as cellsym decks** under identical
settings to their off-plane partners, rather than reused from production. They restart from
a converged geometry, so they are cheap — the three basin restarts of docs/41 §6f converged
in 3, 4 and 5 ionic steps. The production values remain the tier-of-record; these exist only
so that ΔE_sym is a difference between two decks that differ in exactly one thing.

---

# AMENDMENT 3 — 2026-08-09. Correcting a claim I made in amendment 1.

**§3-A.8 said the ±y central difference is "kept for its √2 noise gain". That is wrong,
and it is my error, not the builder's.**

At a mirror-symmetric reference geometry the +δy and −δy structures are related by the
mirror. pw.x is deterministic, so their forces are exactly mirror-related:
F(−δy) = σ·F(+δy), with no independent noise realisation. The central difference therefore
reduces algebraically to the forward difference — same number, same noise — and the cubic
anharmonic term it would normally cancel is already absent by the same symmetry. A
byte-level check confirms the premise: each `..ym.in` deck is the **exact** mirror image of
its `..yp.in` partner, slab included, to all eight written decimals.

So the six `ym` decks carry **exactly zero information** and are withdrawn from the pilot.
The verdict rests on the +δy displacements alone.

Two things follow that are worth stating rather than absorbing:

- The saving is real but it is not the point. The point is that a "central difference for
  noise averaging" that is a mirror image of its partner is a redundancy dressed as a
  control, and the same reasoning applies to **Q5**, the Hessian-symmetry check on the
  y/xz cross-block: those elements are structurally zero by the same symmetry, so Q5 as
  registered is a noise measurement, not a physics gate. It is reported, not gated.
- The ±x and ±z decks remain, with the purpose amendment 1 already assigned them —
  block 2B's in-house ZPE/−TS table, replacing digits taken from paywalled sources this
  project cannot legally verify. They are not evidence for the 1C verdict and are no longer
  described as such.

**Registered consequence for UNDERPOWERED.** With the √2 gain gone, the noise floor on the
y-block is whatever a single displacement gives. That makes amendment 2's replacement
remedy — a **larger δ**, not a tighter `conv_thr` — the only lever left, and raises the
prior probability that the Ir pilot returns UNDERPOWERED rather than a verdict. If it does,
that is a measurement of this design's resolution and is reported as such, not as evidence
about the physics.

---

# AMENDMENT 4 — 2026-08-09, after the round-2 review, before any 1A gate job runs

Four registrations, all arising from round-2 findings on the block-1A implementation
(tasks/review/round2-findings.md). Every one is registered here **before** the affected
job has produced a number.

## 1. GATE C / C-2's Cr baseline is a relaxation at the folded mesh (finding N10)

As built, GATE C compared a **relaxed** 2×1 energy against a **fixed-geometry** 1×1
baseline evaluated at a geometry relaxed at 9 4 1. Any relaxation energy released by the
9 → 8 mesh change would appear as a systematic negative ΔE and read as a gate failure,
with nothing to distinguish "the cell construction is wrong" from "the 1×1 geometry was
not stationary at the folded mesh". §2-A.4's registered test says only "1×1 clean at the
folded mesh" — it is silent on the baseline's relaxation state, and the confound forces
the choice:

- **Registered:** for Cr, the GATE C baseline is `slab__1x1_k8_relax` and the GATE C-2
  baseline is `s0_O__1x1_k8_relax` — the production 1×1 geometries **re-relaxed at
  8 4 1**, so both sides of each gate are the same protocol. Ir/Ru are unchanged (their
  production mesh folds exactly; both sides were always relaxations).
- The fixed-geometry SCFs at 8 4 1 remain exactly what §2-A.5 registered them as: the
  k-mesh bridge. They are not gate baselines.
- The difference E(relax@841) − E(scf@841) is reported per state as
  `mesh_relaxation_meV`. On a gate FAIL, a |ΔE| comparable to `mesh_relaxation_meV` is
  read as MESH_RELAXATION, not CELL_MISMATCH — and the readout says which.
- Step cost of the two new relaxations is quoted from the measured
  restart-from-own-minimum class (docs/41 §6f basin restarts: 3/4/5 ionic steps), not
  from the 1×1 from-scratch counts.

## 2. GATE-1 extends to every Cr relaxation in the block (findings U2/U5, N3)

§2-A.3(b) registered one fresh-density SCF per Cr **2×1** relaxation. The failure it
guards against was first measured on a **1×1** (Cr `*OOH`, −178.58 meV, docs/41 §6f), so
the 1×1 rows are equally exposed and the marginal cost is five cheap SCFs.

- **Registered:** every Cr relaxation this block emits gets a `__g1` fresh-density
  fixed-geometry SCF at its own final coordinates, **at the parent's own symmetry
  treatment, k-mesh and cell** (a GATE-1 child that changes `nosym` or the k-set at the
  same time attributes nothing — finding N3).
- The evaluator is `--score`, which now actually computes the ≤ 5 meV comparison (U5):
  verdict AGREE within tolerance, else **BASIN_DRIFT**, in which case the GATE-1 SCF
  energy is the corrected value (docs/41 §6f: the fresh-density SCF reproduced the true
  basin to 2–3.5 meV on all three restarts) and the pair is scored from it.
- Cr pair members without a scoreable GATE-1 SCF are **PENDING_GATE1** — §2-A.3 calls
  the control "a precondition of the readout", and now the code enforces that. The Cr
  `*OOH` 1×1 mirror member is prevalidated (the docs/41 §6f basin restart) and enters
  as-is; its provenance is recorded in the readout row.

## 3. Both magnetisation channels are thresholded (finding U4)

§2-A.3(a) records "total and absolute magnetisation" and requires pair members to
"agree to within 0.1 μ_B"; §2-A.3's own stated failure mode is an antiferromagnetic
rearrangement — which has ΔM_total = 0 and a large ΔM_absolute. As coded, only the total
was thresholded, so the registered test was blind to the registered failure mode.

- **Registered:** the 0.1 μ_B tolerance applies to **total AND absolute** magnetisation,
  for the Cr pair test and for GATE C / C-2 (where the comparison is against 2× the
  baseline value). Either channel exceeding tolerance is CONFOUNDED (pairs) or a FAIL
  channel (gates).

## 4. The replication gate scores a fresh run (finding N2)

§2's "Replication (gating)" requires Ir `*OOH` 1×1 off-plane to **reproduce**
ΔE_sym = −0.291 ± 0.05 eV as a pipeline control. As built, the scorer redirected that
row to the archived P10 output — the gate re-read the very run it exists to replicate
and returned −0.291323 by construction. A control that cannot fail controls nothing.

- **Registered:** the Ir `s0_OOH__1x1_off` deck is emitted and **run fresh** through the
  current pipeline; GATE R scores the fresh run against −0.291 ± 0.05 eV. The archived
  P10 output is no longer an admissible source for this row. (Ru's P10 reuse stands —
  Ru is not the gating row — and is declared per-row in the manifest and readout.)
- The manifest field that recorded the re-read as "validated" is renamed
  `scorer_selftest` and states what it actually was: an arithmetic check of the scorer,
  not the gate.


## 5. Citation verification — the three load-bearing references (2026-08-09)

Section 10 registered every external citation as unverified and required confirmation from
the actual papers before any is cited in the report or used to concede a novelty claim.
Done, from primary records (Crossref, OpenAlex, PMC, arXiv — no grey-area sources):

1. **Deshpande, Kitchin & Viswanathan — CONFIRMED, exact.** "Quantifying Uncertainty in
   Activity Volcano Relationships for Oxygen Reduction Reaction", *ACS Catal.* **6**,
   5251–5259 (2016), DOI 10.1021/acscatal.6b00509. Volume and first page as cited. Note
   for the report: it is an **ORR** volcano-uncertainty paper — cite it for the
   uncertainty-quantification methodology, not as OER precedent.

2. **Divanis et al. — CONFIRMED, verbatim.** *Chem. Sci.* **11**, 2943–2950 (2020),
   DOI 10.1039/c9sc05897d (open access, PMC8157516). The paper's own pooled value:
   "In this study the intercept is equal to **3.18 ± 0.12 eV** and ±0.24 eV for a
   confidence level of 1σ and 2σ respectively." §6's z = (c_M − 3.18)/0.12 uses the
   paper's 1σ exactly as printed. (The 3.2 ± 0.2 eV it also quotes is the prior
   literature value, not the pooled fit.)

3. **Goniakowski & Gillan — CONFIRMED in substance; the citation year needed one
   correction.** The journal article is *Surf. Sci.* **350**, 145–158 (**1996**), DOI
   10.1016/0039-6028(95)01252-4 — not 1995 as this document wrote. "Known since 1995"
   survives via the preprint: arXiv:mtrl-th/9508009, submitted **24 Aug 1995**. The
   content claim is stronger than assumed — the abstract states, of H₂O on rutile
   TiO₂/SnO₂(110): "allowance is made for relaxation of the adsorbed species to
   unsymmetrical configurations" and "the **symmetrical molecularly adsorbed
   configuration is unstable with respect to lowering of symmetry**." That is the
   precaution, on this surface, verbatim, thirty-one years before this campaign. Cite as
   Surf. Sci. 350, 145 (1996); arXiv:mtrl-th/9508009 (1995). The report's novelty framing
   must credit it accordingly: the lead contribution is the *Hessian classification and
   the magnitude on MO₂ OER intermediates*, not the observation that symmetric adsorbates
   can be unstable.

The §10 caveat "every external citation is unverified" is superseded for these three; it
stands for all others.


## 6. Corrections and completions from the adversarial verify round (2026-08-09, same day)

Three verifier agents re-ran every round-2 demonstration against the fixed code: all 21
fixes CONFIRMED, 13 new defects found. The defects are closed in code; four touch this
document and are registered here:

1. **§2's cost prose said "five cheap SCFs"; the registered rule covers seven.** "Every
   Cr relaxation this block emits" sweeps in the two `__1x1_k8_relax` gate baselines
   created by §1 of this same amendment — 21 GATE-1 parents in all, not 19. The rule is
   unchanged; the count was wrong.
2. **GATE-1-passed energies apply to the GATES as well as the pairs.** As coded after §2,
   the four Cr relaxations that feed gates but no pair (`ref__2x1v`, `ref__2x1o`, the two
   `_k8_relax` baselines) had an evaluated-then-ignored control: GATE C could PASS from a
   raw parent energy while that parent's own GATE-1 verdict was BASIN_DRIFT. Registered:
   every Cr energy entering any gate or pair is the GATE-1-passed value; a Cr gate whose
   side lacks a scoreable `__g1` child is **PENDING_GATE1**.
3. **"Comparable" in §1 is made numeric.** A GATE C/C-2 FAIL with
   \|ΔE\| ≤ 2×\|mesh_relaxation_meV\| is read (and recorded by the readout, in a
   `fail_reading` field) as MESH_RELAXATION; otherwise CELL_MISMATCH_OR_UNATTRIBUTED.
4. **A missing magnetisation record is NOT_SCOREABLE, never agreement.** The verify round
   demonstrated a CONFOUNDED pair flipping to OK and a GATE C-2 FAIL flipping to PASS
   when the magnetisation lines were stripped from the output — every threshold was
   guarded by "if present". For a magnetic metal, §2-A.3(a)/§2-A.4 tests refuse to score
   without the record.

Also noted for the record: the queue launcher's controls (the `# NP=<n> NCONC=<n>`
directive, `# EXPECT_CAP`, the calculation-aware stale rules, the cgroup refusal) are
engineering controls documented in the script and manifest headers, deliberately not
registered here — they protect the schedule, not the inference.


## 7. The ym decks' role, resolved (2026-08-09, after the 1C verify round)

Amendment 3 withdrew the √2 claim and registered that "the verdict rests on the +dy
displacements alone" — but the verify round then found (its N34) that the ym decks have a
value amendment 3 did not consider: because each ym deck is the *exact mirror* of its yp
partner (verified to 8.9e-16 Å), symmetry fixes F_y(ym) = −F_y(yp) and F_x/F_z(ym) =
+F_x/F_z(yp) atom by atom, which is the **only available test of the Hessian diagonal** —
the axis every other gate is provably blind to (a diagonal force error contributes zero to
H − H^T and zero to σ_F; a demonstrated 1e-2 Ry/bohr corruption flipped the verdict to
CONFIRMED with zero gate failures). Registered resolution, superseding amendment 3's
"withdrawn from the pilot" clause and only that clause:

1. **The ym decks are RETAINED and RUN, solely as the Q6 mirror-identity control.** They
   never enter H.
2. **The y-block of H is built from the +dy forward difference exclusively** (algebraically
   identical to the central difference whenever Q6 passes, which is why amendment 3 found
   the central difference carried no extra information). x and z blocks remain central.
3. **A missing or unusable force block on any +displacement deck is a hard gate failure
   (VOID) for that state** — never a silent coordinate drop. The verify round demonstrated
   the y coordinate being dropped wholesale, after which the state returned REFUTED — the
   R3-feeding verdict — without the H-atom y mode ever having been measured. Missing
   evidence must not score as a pass (the N38 rule, third appearance). An unusable ym deck
   voids only the Q6 control for that atom, and is reported.
4. **Q5 is reported, not gated** — this was already registered in amendment 3 and the code
   must comply; the verify round found it still appending to the gate list.


---

# AMENDMENT 5 — 2026-08-11, after the literature sweep, before any LIT job runs

Seventeen paywalled PDFs were pulled on 2026-08-11 and integrated the same day
(docs/research/2026-08-11-paywalled-sweep-plan-implications.md, commit 0126b96 — twelve
reader agents, one synthesis, six adversarial verifiers, one global skeptic). The sweep's
verdict was **no pivot**: nothing in the seventeen papers invalidates blocks 1A/1B/1C or
the surviving symmetry-trap finding. Frank adopted the memo's recommended subset on
2026-08-11 (decision sheet, memo §9.7): **D1, D2, D4, D6, D8, D11** — registered below.
**Deferred and NOT registered:** D3 (full per-metal termination campaign + U-flip
extension), D5 (thermochemical U re-fit), D7 (single-water probe arm), D9 (LIT-7: Co *OOH
attempt, scaling column, Comer parity), D10 (LIT-8: mechanism-scope flags). Any of these
may still happen, but only through its own dated amendment; D9/D10 additionally were never
adversarially verified.

**Stated weakness, up front.** This sweep was conducted *after* 1C returned CONFIRMED,
after tier_v2 was known, and after the 1.122 V Cr swing was measured. Every "test" below
is therefore motivated by literature read after the data existed. Following the precedent
of §0a (a control registered from an observed correlation, stated with its weakness),
nothing here is dressed as a prediction: these are **mechanism tests and scope columns
registered before their own jobs run**, which is the only blindness still available to
them. One exception is genuinely blind and is the reason this amendment exists today
rather than in October: §A5.1(b), which must be registered before tier_v3 exists.

## A5.1 — LIT-1: the U-robustness analysis package (D1)

(a) **Valence tracking.** Every existing (metal × adsorbate × U) output is post-processed
for the active-site **local magnetic moment vs the bare slab** — already printed in every
spin-polarized pw.x output, zero new DFT — as the primary valence tracker, supplemented by
Löwdin populations from projwfc.x where charge densities are regenerated (no `.save`
directories survive; each Löwdin point costs one fixed-geometry SCF + projwfc, budget
≤ ~150 cheap SCFs if the full A0 grid is covered). Each ΔG is classified
**valence-conserving** (expected U-robust) or **valence-changing** (expected U-fragile) —
an adaptation of Tripkovic 2018's V(B) analysis (moments, charges *and* O–O bond
structure; peroxo/superoxo O–O distances checked as in their protocol). The mechanism
test, stated with its post-hoc weakness: the 1.122 V η(Cr) swing should correlate with a
Cr oxidation-state change under *O/*OOH, and U-flat quantities should show none. Either
outcome is reported.

(b) **The ranking-claim rule — registered now, before tier_v3 exists.** A pairwise
ordering of metals may be claimed in the report only if **all three** hold:
  1. the ordering is the same under η_TD and under G_max(η = 0.3 V);
  2. the G_max gap between the pair is ≥ 0.20 eV (Exner 2020's stated sensitivity floor,
     p. 12611);
  3. the ordering is stable across the U band **{U = 0, MP U, hp.x U if block 1B returns
     GO}** at fixed geometry (the A0 grid's approximation, stated wherever used).
Pairs failing any leg are reported as **not distinguishable at this protocol's
resolution**. The band contains no thermochemical leg because D5 was not adopted; if a
later amendment adopts it, the band extends by that amendment. This rule is registered
while tier_v3 does not exist (§7's blind-prediction reasoning): registering it after
tier_v3 would let the rule be fitted to the outcome.

(c) **G_max across the A0 grid.** G_max at η = 0.1/0.2/0.3 V with the limiting-span
identity, computed for every U in the A0 grid — a pure function of the same four ΔG
values, zero new DFT. The `g_max()` implementation was session-verified algebraically
identical to Razzaq–Exner 2023 eqs 10–25 and reproduces the docs/29 §4b Fe/Mn values
exactly; no renumbering.

(d) **Intercept-vs-descriptor U-test** ("U moves you along the volcano, not off it"):
does the 3.2 eV scaling intercept stay U-robust while the descriptor axis is U-fragile?
Motivating prior, from Tripkovic Table 3 itself: LaCrO₃ ΔE(*OOH)−ΔE(*OH) moves 2.94→2.93
eV over U = 0–5 eV while ΔE(*O)−ΔE(*OH) moves +1.06 eV.

(e) **Hygiene.** docs/29 §4b currently carries the trapped Cr rows (1.726/1.426) and a Ni
row resting on `runs/Ni_slab/dft_eta.json.RETRACTED` (both verified on disk 2026-08-11).
docs/29 is a dated plan-of-record and is not rewritten; the stale rows receive an inline
erratum marker pointing to a regenerated table, which is published in the LIT-1 results
document with tier version named per §0 and GATE-1 provenance per Amendment 4 §2. Every
Cr energy in the regenerated table is the GATE-1-passed value. `volcano_r1.py`'s
docstring is corrected to cite Exner 2020 and Razzaq–Exner 2023 (it currently cites only
Acc. Chem. Res. 2024); `descriptors.py` lines 16–17 ("the scaling-relation floor this
project aims to circumvent") are reworded — Razzaq–Exner 2023 §3.1 shows breaking the
3.2 eV relation can *reduce* activity, and the retracted-Ni "broken scaling" talking
point stays dead.

## A5.2 — LIT-2 trimmed core: the termination check (D2; full campaign deferred = D3)

Static CHE surface Pourbaix in the existing 2×1 cells, **registered scope: the RuO₂
benchmark plus the Cr O-covered-preference check only** (~12 relaxations; the full
Ru/Ir/Cr termination campaign and the U-flip extension are D3, deferred).

- Terminations representable at 2×1: clean / 1 ML *O_cus / mixed 1:1 *OH–*O / 1 ML *OH
  (plus an O-depleted variant for Cr). Block-1A outputs are **reused, not re-run**, where
  they already are these states (the 2×1 neighbour-*O arm with working *O is 1 ML *O_cus;
  working *OH with *O spectator is the mixed rung). Genuinely new relaxations run under
  the standing protocol: off-plane starts, nosym/noinv, a `__g1` GATE-1 child at the
  parent's own symmetry/k-mesh/cell (Amendment 4 §2), total AND absolute magnetisation
  recorded with the 0.1 μ_B channels for Cr (Amendment 4 §3).
- **RuO₂ validation, two-sided, registered before any job runs.** A 2×1 cell cannot
  represent Qiu 2026's 1/3, 2/3, 5/6 ML rungs, so the scoreable benchmark is the
  coarsened ladder. PASS iff (i) the ordering with falling potential is
  full-O → mixed → full-*OH and (ii) the full-O/mixed and mixed/full-*OH transition
  potentials fall within **±0.25 V** of Qiu's AIMD brackets (~1.50 V and ~1.24 V; the
  tolerance absorbs the known vacuum-vs-solvated offset). On PASS, the Cr column is
  reported as validated-by-proxy. On FAIL, the Cr column is still reported, labelled
  vacuum-CHE-only, with the measured RuO₂ discrepancy attached as its systematic error.
  Both outcomes are publishable; neither is a gate on any 1A/1B/1C result.
- **Decision rule (Cao's oxygen-environment finding, restated in CHE-at-U form):** if Cr
  prefers an O-covered termination by > 0.1 eV per site at U = 1.23 V + η(Cr), every
  clean-termination Cr energetics row in the report carries a **conditional-on-termination
  flag**. The flag qualifies; it does not retract — P7's withdrawal already stands on
  U-sensitivity alone.
- **Descriptor rewording, registered:** all reported η_TD values are named
  **bare-surface-limit η_TD** wherever the resting-termination question is live (Qiu
  2026: no bare cus-exposed RuO₂ surface exists at any potential in 1.23–1.80 V; Feng
  2025 p.4: almost all M-RuO₂ are fully O-terminated at 1.43 V).

## A5.3 — LIT-3: the *OOH anatomy (D4)

(a) **Fingerprint classification, zero DFT first.** Every archived *OOH geometry is
classified by **O–O distance as the primary fingerprint** (hydroperoxo *O–OH ~1.37–1.45 Å
vs superoxo *OO-H ~1.30–1.32 Å, Inico 2024), with Bader (QTAIM) charge via pp.x as the
secondary check — Inico's charge thresholds (~−0.4 |e| hydroperoxo, < 0.1 |e| superoxo)
are Bader-defined and may not be compared against Löwdin values without recalibration on
our own unambiguous anchor states. Where charge densities were not retained, one
fixed-geometry SCF per state regenerates them. A scaling-residual audit accompanies the
classification (Man 3.2 ± 0.2/0.4 as an RPBE-population outlier flag only, never a
per-state pass/fail — docs/41 P9's functional-mismatch caveat applies).

(b) ***OO-H spot check, uniform across Cr, Ir, Ru** (P6/P19: never Cr alone): one *OO-H
initialization (superoxo O–O + H on bridging O) per metal, ± spin starts, standing
protocol with GATE-1 children for Cr. Inico's measured stabilizations, per oxide: 0.46 eV
(TiO₂, vacuum), 0.19 eV (RuO₂, vacuum), ~0.13–0.15 eV (IrO₂, one-water/bilayer models).

(c) **Cr conformer × spin factorial** including one nspin=1 control — the Gauthier
diagnostic for the 175 meV metastable-magnetic *OOH state (Gauthier 2017 p.4: the *OOH
moment differs between conformers and "significantly affects the energy"; without spin
polarization the conformer gap collapses to ~0.05 eV).

**Registered constraint:** outputs of (b) and (c) are mechanism-caveat columns or
uniformly-applied tier_v3 inputs — never a Cr-specific rescue (P6). §2's registered Cr
prediction (the *OOH symmetry correction changes η(Cr) by exactly zero) is untouched.
The (c) result feeds the held Cr Hessian decision (§3-A.7) as context, not as a gate.

## A5.4 — LIT-5r: the solvation sensitivity band (D6; single-water arm deferred = D7)

- All as-computed vacuum η_TD and G_max columns remain the **primary** results.
- Sensitivity overlay, zero DFT: ΔG_OOH swept over **[−0.4, +0.2] eV** — the rutile-(110)
  literature band (Gauthier 2017: −0.3/−0.4 eV at *O neighbour-coverage, +0.2 eV at *OH
  neighbour-coverage, all stated by Gauthier as upper bounds from a 0 K ice-network
  global-minimum search). **No central value is designated**: the correction is
  coverage-dependent and sign-flipping, and both of Gauthier's coverage cases have an
  occupied neighbouring cus site, which our low-coverage slabs do not — no literature
  value exists for our geometry. ΔG_OH and ΔG_O are swept over 0 ± 0.1 eV. The report
  states which rankings, apex assignments, and limiting-step labels survive the whole
  band including zero.
- **Guard, registered:** shifted columns may only **demote or qualify** vacuum-based
  conclusions. No candidate that fails at unshifted values may be promoted to any
  headline via a shifted column.
- **Registered: no static water bilayer will be run.** Inico 2024: AIMD shows 45%/63%
  water dissociation on RuO₂/IrO₂(110); the rigid intact bilayer inflates the RuO₂
  *OOH/*OO-H splitting from 0.19 to 0.88 eV — a ~0.69 eV artifact — and destabilizes
  *O-H on IrO₂. Running one anyway and reporting it would manufacture a number this
  document has pre-committed to distrust.
- Gauthier 2017 p.4 is cited as independent literature support for the Cr *OOH
  metastable-magnetic-state finding (docs/41).

## A5.5 — LIT-6: stability and dissolution scope columns (D8)

Registered **outcome-neutrally, before any value is computed** (this amendment is that
registration; the pre-amendment document is archived as
docs/43-prereg-week1-factorial-archive-2026-08-11-pre-amendment-5.md).

(a) **Bulk Pourbaix flags**, pymatgen/Materials Project, pH 0, 1.23–2.0 V vs SHE, applied
uniformly to every host and dopant composition including the Ru/Ir survivors. Gate =
Jia 2025's full published criterion: ΔG_pbx < 0.5 eV/atom **and** a solid phase present
in the window. The flag is reported whatever it says. Anticipated but not asserted:
Cr/Co/Cu likely flag; RuO₂ itself crosses its RuO₄ line at ~1.82 V (Cao Fig 2b), so a
host flag near the window top is expected behaviour of the gate, not a defect. Wording:
"thermodynamically flagged for bulk dissolution/transformation" — bulk Pourbaix carries
no surface-state or kinetic information (Jia's own caveat).

(b) **Substitutional formation energies** per Garcia-Mota 2011 Eq. 5, reusing existing
doped-slab totals plus ~10 bulk reference relaxations (elemental metals in correct
magnetic states, host bulks, O₂). Because slab totals carry U and elemental references do
not, ΔE_form is U-dependent: reported at production U **and** at the P7 U-range
endpoints, flagging any dopant whose stability verdict flips across the range.

(c) **Published-SI anchors:** the free ACS SIs of Sun 2024 (Fig S6b per-dopant η₁₀ — the
only published experimental activity set spanning the full Sc–Zn row in a rutile RuOx
host) and Cao 2026 (Tables S1/S8 — their dopant U values, the direct comparator for our
hp.x numbers). These are **anchor/context columns, never validation targets** (Sun's
full-row η₁₀ spread is ~66 mV in nanoparticulate form; Burnett 2020 shows wet-cell and
MEA rankings disagree on identical powders).

(d) **Leaching caveat text**, stated with both edges: Burnett — Co loses 91.4% of its
dopant in 1000 cycles while Ru loses < 0.4%, and Co's activity *rose* post-leach; Deng —
Mn leaches ~300× Ir/Ru and it is sacrificial-protective. The caveat scopes what the
ranking predicts (the modelled doped surface is transient under operation); it does not
say the catalyst is dead.

**Firewall, registered:** these stability columns are orthogonal scope documentation.
They may note that Co/Cu would have been triaged on independent grounds; they may NOT be
used to argue the withdrawn Cr headline or the P7 U-sensitivity finding is moot, and the
Co *OOH and Cu holes remain holes in the activity dataset.

## A5.6 — Wording and attribution obligations (D11; binding on report drafting, no compute)

The memo §4 obligations are adopted as standing constraints on how results are worded
(the report prose itself remains Frank's, per standing rule): (1) the withdrawal framed as
field-consistent (Exner: η_TD least reliable near the apex); (2) P7 attributed — same
phenomenon and mechanism as Tripkovic 2018, ours the pre-registered quantification on
doped rutile (110); (3) no hybrid-functional arbitration — cite Tripkovic conclusion 3,
do not compute; (4) "fixed-protocol DFT cannot reliably place Cr," never "Cr is bad"
(Feng 2025: Cr-RuO₂ 201 mV experimental, best in set; Cao 2026: CrRuO₂ 360 h at
100 mA/cm²); (5) the AEM-scope caveat package (Grimaud/Fabbri/Qiu/Deng) with the
crystalline-RuO₂ null result defending the host baseline; (6) experimental validation
limited to Mn-consistency plus leaching caveats, with Burnett's wet-cell/MEA
non-correlation as the standard rebuttal to "validate against experiment"; (7) G_max
presented as Exner's descriptor, adopted with citation; (8) every absolute η scoped:
bare-surface-limit, AEM-channel, unsolvated, at stated tier and U.

## A5.7 — Scope guard

Nothing in this amendment alters the 1A replication gate, the P12 bins, the 1C verdict
ladder, the 1B GO window, the frozen tiers, or any registered threshold. No LIT job
launches on a box that is still running block-1A work; LIT decks queue only after the 1A
manifest on a box is drained, or on a separately provisioned box. Total newly registered
compute: ~12 relaxations (A5.2) + ~10–15 relaxations (A5.3b/c) + ~10 bulk relaxations
(A5.5b) + regeneration SCFs (A5.1a/A5.3a, bounded above at ~150 cheap fixed-geometry
SCFs). Every new Cr relaxation gets its GATE-1 child; every new relaxation of any metal
follows the off-plane/nosym standing protocol with measured max|F_y| recorded (§0a.2).

## A5.8 — The Xu 2015 gate: still open, and a wrong-paper note for the record

The sweep memo gated all novelty wording about linear-response U on rutile OER systems on
reading **Xu, Rossmeisl & Kitchin, "A Linear Response DFT+U Study of Trends in the Oxygen
Evolution Activity of Transition Metal Rutile Dioxides," J. Phys. Chem. C 2015, 119,
4827–4833, DOI 10.1021/jp511426q**. The PDF pulled on 2026-08-11 under the name
`jp5b05338.pdf` is a **different paper from the same group, journal and year** — Curnan &
Kitchin, "Investigating the Energetic Ordering of Stable and Metastable TiO₂ Polymorphs
Using DFT+U and Hybrid Functionals," JPCC 2015, 119, 21060–21071, DOI
10.1021/acs.jpcc.5b05338. That paper is kept (it independently supports the no-hybrid-
arbitration position: experimentally consistent polymorph ordering holds over U
*intervals*, while "a first-principles methodology capable of calculating exact exchange
fractions ... is not available"), but it does not resolve the gate. No open-access copy
of the correct paper exists (Unpaywall: closed; publisher and Scopus links only on the
group's site). **Until 10.1021/jp511426q is pulled and read, the report may not claim
novelty or priority for any linear-response-U result beyond the plain statement of what
was computed here.** The slab non-convergence observation remains reportable as an
observation.

---

# AMENDMENT 6 — 2026-08-15, before any block-6A (A0) deck is built or launched

## A6.0 — What changed, and why this is registered now

Block 6A — the A0 grid — was registered in §4 as *"the η(U) grid over 0–9 eV from pw.x
alone (140 fixed-geometry SCFs)"*, declared independent of the 1B hp.x gate and declared
to ship regardless of a NO-GO. It has never been built or run; only the inherited
four-point ladders exist.

Since it was registered, **block 1A closed with the verdict ADOPT_2X1V** (commit 58f5867):
on 7 of 9 off-arm rows the 1×1 cell was systematically weakening binding through the
periodic image, by 0.11–0.36 eV. A0's fixed geometries are 1×1. As registered, therefore,
A0 would densify η(U) in a cell this campaign has since retired — a scope question the
original registration never had to face.

This amendment answers it **before a single A0 deck exists**, which is the only point at
which the answer is worth anything.

## A6.1 — The decision: the main grid stays 1×1, and a second arm crosses the cell

**(a) A0-main, unchanged.** Dense η(U) grid, U = 0–9 eV, fixed geometry, 1×1 cell, pw.x
only, ~140 SCFs — exactly as block 6A registered it.

*Rationale, stated so it can be attacked:* P7 — the withdrawn η(Cr) headline, the 1.122 V
swing — was measured in the 1×1 cell. A0's registered job is to bound **that** claim.
Moving the grid wholesale into 2×1v would not bound P7; it would compute a different
quantity and leave P7 a four-point result permanently, which is strictly worse for the
finding the report is built on. The retired-cell objection is answered by (b), not by
abandoning (a).

**(b) A0-cell, newly registered.** A Cr-only 2×1v arm: four states (`ref`, `*O`, `*OH`,
`*OOH`) × five U points = **20 fixed-geometry SCFs**, run on block 1A's already-relaxed
2×1v Cr geometries. The builder must take those geometries from the production set that
defines `tier_v3`, not re-pick them — a different 2×1v geometry would confound the cell
comparison with a geometry comparison.

U points: the four already on the ladder — `u0.0` = 0, `u0.5` = 1.85, `base` = 3.70,
`u1.35` = 5.00 eV — plus **7.15 eV**, which is Xu, Rossmeisl & Kitchin 2015 Table 1's
linear-response U for CrO₂ (10.1021/jp511426q). The fifth point is an external anchor,
not a free choice made after seeing the first four.

## A6.2 — The registered test: is the U error separable from the cell error?

Over the five shared U points, with D(cell) = ΔG_O − ΔG_OH — the descriptor P7 measured —
and span(cell) = max_U D − min_U D, define

> **I_U ≡ span(2×1v) − span(1×1)**

Thresholds are **inherited verbatim from §2's interaction bins** (P13, block 1A). They are
not re-derived, and deliberately so: a threshold invented after the quantity is known is
worth nothing.

| \|I_U\| | declared reading |
|---|---|
| < 0.05 eV | **additive.** The U error and the cell error are separate corrections; the error budget may report and decompose them separately. |
| ≥ 0.30 eV | **not separable.** Only the fully-corrected 2×1v U-sensitivity is reportable; the error budget carries one combined "cell + U" row and the report says so in words. |
| 0.05–0.30 eV | **inconclusive.** Reported as inconclusive. Not rounded toward either. |

*Prior, stated so it can be wrong:* I expect **|I_U| < 0.05 eV, additive.** Block 1A
already measured the cell × symmetry interaction as additive on five of six scoreable rows
(~0.00–0.04 eV) with one inconclusive (Ir `*OOH`, 0.266 eV), and the A5.1a mechanism test
attributes the U-swing to a valence change on `*O` whose Δm is itself U-flat for every Cr
state (range ≤ 0.12 μ_B). **If instead |I_U| ≥ 0.30 eV, the "separable error classes"
framing that organises the entire report is wrong** and must be replaced by a
non-decomposable combined budget. That is a legitimate result and it gets stated plainly,
in the same paragraph as the finding it damages, not buried in supplementary material.

**Second readout from the same arm, no extra compute:** whether the *location* of the
volcano-apex crossing moves between cells. If the two cells place the crossing at U values
differing by more than 1.0 eV, then A0's central claim — that the crossing is *located*
rather than bracketed — is cell-conditional, and must be reported as such.

## A6.3 — The reference anchors are in scope

Production assigns **U = 0 to Ru and Ir** by the MP convention. That is a free choice this
campaign has never examined, sitting underneath every number in the reference tier. Xu 2015
computed 6.73 eV (Ru) and 5.91 eV (Ir) by linear response and reported that using them
*improves* agreement with the experimental ordering — a 0.2–0.4 eV effect already flagged
in the sweep memo §10.

Registered: **A0-main spans U for Ru and Ir as well as the 3d metals**, over the same
0–9 eV range, with Xu's computed values marked as declared anchor points.

*Pre-registered prediction, falsifiable:* **the reference ordering Ir < Ru is stable across
U ∈ [0, 9] eV.** If it inverts anywhere in the band, then the anchors against which every
3d result in this campaign is reported are themselves U-conditional, and every ranking
claim in the report — including the ones that survived P7 — inherits that caveat.

This does **not** license re-deriving the production tier at nonzero Ru/Ir U. The
production convention stays U = 0; any finding here is reported as a sensitivity, not
applied as a correction.

## A6.4 — What A0 may and may not claim

- The **fixed-geometry approximation is unchanged** and must be restated wherever the grid
  is used. A0 measures the U-response of energies at frozen geometry; it cannot see a
  U-driven geometry change. Where A0 and a relaxed point disagree, **the relaxed point
  wins** and the discrepancy is reported, not averaged.
- **A0 does not supersede P7.** P7 stands as the registered prediction that triggered and
  forced a withdrawal. A0 resolves it; it does not retroactively soften it.
- **A5.1(b)'s ranking-claim rule continues to bind unchanged.** A0 supplies the U-band leg
  from measured curves instead of interpolation. It relaxes none of the three legs.

## A6.5 — Operational requirements, registered because they have already cost this campaign once

1. **Charge densities must survive, or `projwfc.x` runs inline.** LIT-1 tranche 1 has no
   Löwdin populations for exactly one reason: no `.save` directories survived (A5.1a).
   Every A0 point either retains its `.save` or runs `projwfc.x` in the same job. Where
   this holds, the moment-based valence tracker is upgraded to a charge-based one.
2. **A declared escalation ladder for non-convergent points.** SCF convergence is expected
   to be *worst* near the valence transition — precisely where the physics is. The
   registered "re-run at tighter `conv_thr`" remedy is dead (amendment 2: QE's 1e-13 `ethr`
   clamp). Replacement, in order: (i) restart from the converged neighbouring-U density as
   `startingpot`; (ii) halve the mixing β; (iii) failing both, the point is recorded
   **NOT_CONVERGED and plotted as a gap** — never interpolated across, never silently
   dropped. A grid with holes is reportable. A grid with invented points is not.
3. **The 2×1v arm scores only against GATE-1-passed parent geometries**, consistent with
   §5 and amendment 4 §2.

## A6.6 — Scope guard

This amendment registers **~160 fixed-geometry SCFs and zero relaxations** (~140 A0-main +
20 A0-cell). It alters no existing threshold: §2's interaction bins are reused unchanged,
and the P12 bins, the 1C verdict ladder, the 1B GO window, the frozen tiers and A5.1(b) are
untouched. It does **not** license an oxyhydroxide tier, an SQS/HEA tier, re-derivation of
the production tier at nonzero Ru/Ir U, or any relaxation in any cell. Block 6A remains
independent of the 1B hp.x gate and still ships regardless of its outcome.

## A6.7 — A5.8's gate is discharged; recording it here so the live document is not stale

A5.8 above states that the Xu 2015 gate is open. **It is not — it was discharged on
2026-08-12** (commit 147f61e, sweep memo §10): `jp511426q.pdf` was pulled and read in full.
Their linear-response U is **bulk-only** (Cococcioni 2×2×2 supercell, predating `hp.x`), so
this campaign's slab-DFPT non-convergence observation survives as first-of-kind, and the
wording ban A5.8 imposed is lifted to the extent that memo §10 records. The attribution
debts that read created — on-rutile U-dependence to Xu 2015, and their p. 4831 caveat
*"except perhaps near the top of the volcano"* being exactly P7's regime — are binding on
report drafting under A5.6. A5.8's text is left standing rather than edited, per the
no-edit-after-deposit rule; this section is the correction of record.

---

**Deposit obligation.** Like amendments 1–5, this amendment must be Zenodo-deposited
**before the first block-6A job runs**. That is Frank's action, and it is a launch gate,
not a formality: an interaction test registered after the grid is read is not a test.


---

# AMENDMENT 7 — 2026-08-16, before any post-1A job launches (S0 gates, the projector, the pls closed form, the floor-U replacement)

## A7.0 — What changed, and why this is registered now

The two-round adversarial literature sweep (docs/research/2026-08-15-lit-sweep-*,
committed 1b9b326) closed with a program whose first stage is nine cheap capability
gates and three new predictions. None of them may run after the answers are visible;
all of them are therefore registered here, before any new job launches. Drafting
provenance: this amendment was AI-drafted at the entrant's direction (2026-08-16)
and is recorded as such in the AI-use log; the report will paraphrase, never
reproduce, any sentence of it (see A7.7).

## A7.1 — P-PROJ: the Hubbard projector as a paired variable

The fifth A0 grid point (U = 7.15 eV, Xu 2015 Table 1) was produced under a
different Hubbard projector than the production tier's `HUBBARD (atomic)`. The
campaign has measured a +1.45 eV shift in the U *value* from projector choice, but
has never measured the η consequence at fixed U. Before any A0 deck is built on the
fifth grid point:

- **Test:** two Cr fixed-geometry SCF sets at U = 7.15 eV, 1×1 (matching A0),
  `HUBBARD (atomic)` vs `(ortho-atomic)`, all four states.
- **PREDICTION (blind): |Δη(Cr)| > 0.10 V.** FALSIFIED below 0.03 V, in which case
  the projector is not a live variable at this U and Xu's supercell linear-response
  value may be imported as a literature anchor.
- If it fires: the fifth grid point is labelled PROJECTOR-MISMATCHED before any
  result exists; the whole η(U) grid runs in ONE projector; the projector delta
  becomes its own labelled sub-row.
- Gated on the S0 ortho-atomic acceptance test; if this QE build rejects the card,
  that is recorded as a capability result and the point is labelled
  projector-unverifiable rather than silently imported.
- Citation rule: 10.1016/j.cpc.2022.108455 (the HP code paper) is NOT evidence for
  projector dependence of η and must not be cited for it; the campaign's own
  measured +1.45 eV is the evidence.

## A7.2 — P-PLS: the closed form and the crossing as a deliverable

Registered: for pls in {2,3}, **η = (c_M/2 − 1.23 V) + |ΔG₂ − ΔG₃|/2** exactly, where
c_M = ΔG_OOH − ΔG_OH; the identity breaks when pls flips to 1 or 4; any row spanning
a flip is reported in two pieces, never averaged across it. The U at which each
metal's pls flips is a first-class deliverable.

- **PREDICTION: ≥3 of 6 metals show a pls flip inside the registered A0 grid.**
- **DISCLOSED NON-BLIND:** Cr flips 3→2 between U = 1.85 and 3.70 (its production U
  landed 7 meV from the crossing — the physical content of "Cr sat 9 meV above its
  floor"); Co and Ni both flipped 1→2 under correction; the LIT-1 Co ladder returns
  pls = 1 at U = 4.48. **Blind: Mn, Fe, Ru, Ir, Ti.**

## A7.3 — P-FLOOR-U (replaces the withdrawn P-U-SPLIT)

The round-1 ratio ("excess exceeds floor by >3×") is WITHDRAWN before any grid is
read: the excess |ΔG₂ − ΔG₃|/2 vanishes identically at a pls crossing, so the ratio
is a grid artifact (Cr's excess runs 0.961 → 0.007 → 0.375 V across U = 0/3.70/5.00).
Registered replacement, smooth and physical:

- **Quantity: span(c_M)/2 in volts, at FIXED endpoints U = 0 and U = U_max** —
  never max-minus-min over a grid.
- **PREDICTION: span(c_M)/2 exceeds 0.10 V on ≥4 of the 6 metals with a converged
  *OOH geometry.** FALSIFIED if ≤1 of 6 exceeds 0.10 V, in which case U does not
  move the physical limit and the floor may serve as a U-invariant denominator —
  a change of framing registered here, before the fact.
- **DISCLOSED NON-BLIND:** Cr measures 0.223 V (floor 0.492 → 0.269 V across
  U = 0 → 5.00), conditional on the S0(f) GATE-1 pass: if any of the four ladder
  points moves > 50 meV on a fresh-density restart, the number is re-derived and
  the correction recorded before this prediction is dated. **Blind: Mn, Fe, Ru,
  Ir, Ti.**

## A7.4 — The nine capability gates, each recorded whichever way it goes

| Gate | Decides | Kill it prevents |
|---|---|---|
| (a) BEEF emission, FOUR decks (`ensemble_energies` / `calculation='ensemble'` / control / winner + HUBBARD card) | which switch this build honours | striking the XC row on a null a grep cannot interpret |
| (b) `noinv` exactness (2 fixed-geometry SCFs, one 2×1v off-plane geometry, must agree < 1 meV) | drop `noinv` from every off-plane job (~38% off the battery; worst job ~62 h → ~39 h) | a week of avoidable critical-path calendar |
| (c) Mirror-arm `nosym` invariance (< 1 meV) | mirror arm stays symmetry ON / 9 k; comparability control | conflating k-folding with a sampling change |
| (d) Hessian timing AND σ_F in 2×1v (`conv_thr 1e-10`) | wall clock; whether 1e-10 is REACHED at 42 atoms/16 k; σ_F delivered | launching 19 decks whose minimum claim is unscorable |
| (e) Ortho-atomic acceptance (build capability) | whether P-PROJ can run at all | silent import of a mismatched grid point |
| (f) GATE-1 on the four Cr LIT-1 U-ladder points (6 fresh-density SCFs) | whether the 0.223 V floor number survives a basin audit | registering the program's most legible number on ungated points |
| (g) TiO₂ 2×1v nspin=1 timing (1 relaxation) | replaces an extrapolated cost class with a measurement | mis-costing S3 |
| (h) AFM anchor probe (4 nspin=2 AFM SCFs on existing RuO₂ 2×1v geometries) | a measured magnetic row on the anchor; closes P11 | the refuted "structurally incapable" wording resurfacing |
| (i) Ti/Sn bulk cutoff ladders (8 SCFs; admission delta-E under 5 meV/atom, 80 to 100 Ry) | endmember admission inside the frozen 80/640 protocol | an unqualified pseudopotential entering the tier |

## A7.5 — The phase-reality ledger and the MODEL-PHASE scoping rule

Registered before any gate: the measured quantity of every arm is a **difference
between two treatments of the SAME slab**; a difference is a valid method
measurement whether or not the slab is a synthesisable electrode. The report may
therefore never quote an absolute η for Cr, Fe, Co or Ni as a materials claim; they
appear only inside paired within-metal differences. Enforced by the pre-submission
script (S7).

Tier strata: TiO₂, β-MnO₂, RuO₂, IrO₂ = REAL-AMBIENT-UNDISTORTED; CrO₂ =
REAL-UNDISTORTED-METASTABLE (Man 2011, read verbatim: "some oxides such as NbO₂,
ReO₂, VO₂, MoO₂, and CrO₂ are not stable"); FeO₂, CoO₂, NiO₂ = MODEL PHASE, method
test systems only. β-MnO₂ is antiferromagnetic and `gen_rutile.py` initialises it
FM — either the AFM arm runs or every materials-facing Mn sentence is struck.
Exclusions (VO₂, NbO₂, MoO₂, WO₂, ReO₂, TcO₂, RhO₂, PtO₂, TaO₂, GeO₂, PbO₂, OsO₂,
SiO₂-stishovite, CuO₂): each row of the exclusion table must carry one resolvable
identifier (MP entry or primary crystallography) plus one reason, or the row is
marked UNVERIFIED — the phase claims for candidate additions are currently unsourced
(the 2026-07-24 survey covers only Cr/Mn/Fe/Co/Ni/Cu) and may not be presented
otherwise. SnO₂ may be admitted as a declared control-stratum member only if Mom
2014's stoichiometric rows are confirmed cus-site by Sep 1 (Man 2011's reduced-
surface SnO₂ row is bridge-site, with the cus site reported not to bind).

## A7.6 — Corrections of record entering with this amendment

1. The multistability priors misattributed to "Dorado et al. 2013" are **Rabone &
   Krack**, Comput. Mater. Sci. 2013 (10.1016/j.commatsci.2013.01.023).
2. `starting_ns_eigenvalue` is an initial guess on the first DFT+U iteration, NOT a
   held constraint; it must not be called occupation-matrix control.
3. arXiv:2605.20985 contains no statement about DFPT+U non-convergence above U ~2 eV;
   that claim is struck. The ph.x rejection rests on this system's measured hp.x
   behaviour plus the already-priced finite-difference Hessian.
4. Moore et al. 2024 (10.1103/PhysRevMaterials.8.014409): verified author order
   Moore, Horton, Ganose, Siron, Linscott, O'Regan, Persson; the "VASP + atomate
   supercell" characterisation is an inference from the abstract, labelled as such.
5. GeO₂'s exclusion reason is corrected: rutile-type IS its ambient polymorph; it is
   excluded as a wide-gap (~4.7 eV) insulator that would be a third occupancy
   convention in one table, not on phase grounds.
6. The token "STRUCTURALLY ZERO" is struck from the status vocabulary; permitted
   statuses are MEASURED / BOUNDED / TRANSFERRED / NOT MEASURED.

## A7.7 — Governance: P-DISPOSITION and authorship, as amended by the entrant

- **P-DISPOSITION.** Any prediction not scored by Oct 15 is marked WITHDRAWN-UNSCORED
  with its date; withdrawal is a legitimate ledger outcome shown alongside HELD and
  TRIGGERED. The body-figure ledger is capped at six rows (five new + the historical
  P7).
- **Authorship (amends the round-2 P-AUTHORSHIP proposal; entrant's decision,
  2026-08-16).** Amendments are AI-drafted research infrastructure, disclosed in the
  AI-use log. The protection sits at report time: no sentence of any amendment is
  reproduced verbatim in the report, essays, or application answers — the entrant
  paraphrases. The AI-use log records what AI produced (sweeps, amendment drafts,
  critique, scaffolding, CI) and what it did not (the report, essays, boxes,
  disclosures, and the silentgate core, which the entrant writes himself per S1).

## A7.8 — Deposit obligation, and a correction about the record

No Zenodo DOI is recorded anywhere in this repository for amendments 1–6; as far as
the record shows, no deposit has actually been performed and the chain to date is
git-only. This amendment therefore carries the obligation for the whole document:
docs/43 complete (A1–A7) is deposited to Zenodo as ONE restricted-access record
(files closed, DOI + timestamp public, flipped to open at report submission) BEFORE
any job governed by this amendment runs. The DOI is recorded here in a dated line
when it exists.

**DOI line (2026-08-16):** the A1–A7 chain was deposited and published as Zenodo
record **10.5281/zenodo.21963144** (restricted access: DOI + timestamp public, files
closed until report submission; file `43-prereg-week1-factorial-A1-A7.md`, 92,505
bytes, exactly the state committed at d1032e5). The deposit obligation of A7.8 is
discharged; every job governed by A7 may now launch. Text added after publication;
the deposited file is the frozen artifact.


# AMENDMENT 8 — 2026-08-23, adopted by the entrant, before any S3 deck is built or launched

**Adoption record.** This amendment was AI-drafted as disclosed research infrastructure
under A7.7 (docs/47, drafted 2026-08-16–23). The draft required every THRESHOLD to be
re-authored by the entrant before deposit. What happened instead, recorded as the
authorship event: the entrant reviewed every open decision through the indexed decision
sheet docs/52 (66 rows, each quoting the drafted options verbatim with file:line) and
adopted the drafted proposals as his decisions — his words, from the session log of
2026-08-23: "I went through them and they pass with me. Go ahead." Under that decision
every marker below reads "THRESHOLD (adopted as proposed, 2026-08-23)"; items that had
no drafted default remain OPEN and are annotated in place as [ADOPTION NOTE 2026-08-23:
still open …]. Adoption-time annotations are bracketed and change no drafted content.
A7.7's model is unchanged: AI drafted, the entrant decided, the report paraphrases and
never copies. The Governs block below restates the draft preamble's Governs and
Also-carries lines (docs/47:13-17) with no content change.

**Governs:** S3 — `tier_v3` crossed coverage × symmetry × basin over 8 metals; the dy
ladder; GATE-1 depth; the CONFOUND rule; P-SYMCOV; the convergence-failure budget; block
1C's σ_F instrument question (A8.7); and the migration of all remaining compute from
Vast box 47662258 to Purdue Anvil (A8.5).

## A8.0 — Why this amendment is being written now, and what changed under it

A8 was scheduled on 2026-08-16 to register the S3 protocol. Between then and now three
things happened that A8 must absorb — two of them change what S3 costs, one changes what
S3 must measure.

1. **S0 closed** (2026-08-22, 25/25 jobs, 0 SCF failures). Its nine gates settled the
   open protocol questions S3 inherits: the production cell is 2×1v, `noinv` is
   droppable, the mirror arm keeps symmetry on, ortho-atomic projectors are accepted,
   1e-10 is affordable at 1.71× cost, and BEEF is reachable only through
   `calculation='ensemble'`.
2. **Vast box 47662258 was destroyed** (2026-08-22, zero instances). All remaining
   compute moves to Anvil under ACCESS allocation CHE260157. That move is an S3+
   decision and anvil/README.md already routes its registration here.
3. **Gate (g) falsified the S3 cost model** — and it did so on hardware that no longer
   exists, so the falsification itself had to be re-measured on Anvil (A8.6).

---

## A8.1 — The S3 design, restated so it can be attacked

S3 computes `tier_v3`: the corrected tier over 8 metals, crossing the three factors that
S0 and block 1A each measured in isolation.

| factor | levels | why it is crossed rather than fixed |
|---|---|---|
| coverage / cell | 1×1, 2×1v | block 1A: 7 of 9 off-arm rows moved > 0.10 eV; the 1×1 cell weakens binding through the periodic image by 0.11–0.36 eV. The 1×1 rows are not discarded — P7 was measured in 1×1, and the contrast leg is what prices error class 7. |
| symmetry | off-plane (`nosym` + displacement), mirror (symmetry ON) | S0(c) settled that the mirror arm runs sym-ON. The symmetry trap is **coverage-conditional**: 0.291 V on Ir at 1×1, −0.018 eV at 2×1v half coverage. A single-coverage symmetry measurement would have reported either number as *the* effect. |
| magnetic basin | production seed + second seed | error class 2. Restored beyond *OOH-only wherever triage allows. |

**The crossing is the point.** Each factor has already been shown to change the answer by
more than the 0.03–0.08 V separations the screen ranks. What has never been measured is
whether they are additive. S0's interaction probe found ADDITIVE ×5 with one INCONCLUSIVE
row (Ir *OOH, 0.266 eV).

**THRESHOLD (adopted as proposed, 2026-08-23):** a cell × symmetry interaction term is reported NON-ADDITIVE
where |E(both) − E(cell) − E(sym) + E(neither)| exceeds **0.10 eV** — the same bin block
1A used, so the two are comparable without a conversion.

## A8.2 — P-SYMCOV: the symmetry claim is coverage-indexed or it is not made

Registered as a wording obligation with teeth, because this campaign has already made the
mirror-image mistake once.

No statement of the form "the symmetry trap is worth X V" may appear in any output of
this project without the coverage at which X was measured attached in the same sentence.
The measured pair — 0.291 V (Ir, 1×1) and −0.018 eV (Ir, 2×1v half) — is a **range across
coverage**, not a value with noise. A reader given only the first number is told the trap
is a third of a volt; a reader given only the second is told it is nothing. Both readings
are wrong, and the campaign's own withdrawn headline is what a wrong reading costs.

**THRESHOLD (adopted as proposed, 2026-08-23):** P-SYMCOV is satisfied when, for every metal in S3, the symmetry
effect is reported at **both** coverages, or the missing cell is reported as a gap. A
metal with only one coverage is **not** averaged into any symmetry statistic.

**Both outcomes, stated now (added 2026-08-23 — A9.4 found that round-2 F9's "both
outcomes … pre-written in Amendment 8" was not in fact here).** P-SYMCOV is a wording
rule, but it rides on a measurement — the coverage-dependence of the symmetry effect —
and that measurement has two outcomes. **Claim scope if the effect is coverage-dependent
on most metals** (the Ir pattern, |ΔΔE(1×1) − ΔΔE(2×1v)| large): the symmetry trap is
reported as a coverage-conditional effect, the range stated per metal, and the 1×1
numbers of the literature census (A9) are read as the high-coverage end of that range.
**Claim scope if the effect is coverage-independent** (the two cells agree within the
basin CONFOUND tolerance on most metals): the trap is reported as a property of the
placement, not the cell; the 1×1 legacy numbers stand as-is; and P-SYMCOV reduces to the
reporting rule with no "range" to state. **THRESHOLD (adopted as proposed, 2026-08-23) for "most":** ≥ 5 of the
8 metals with both cells measured; a metal with one cell is a gap, as above. Neither
outcome changes what S3 computes; they change one sentence, and the sentence is the
entrant's. The solvation × coverage non-additivity row (docs/45 §B row 9) is **carried
here** as an appendix prediction with its TRANSFERRED status and the swept ΔG_OOH band
(A9.5 flagged the ownership; A8 takes it — it is a coverage statement, not a census one).

## A8.3 — The CONFOUND rule, extended to the magnetic basin

§5 and amendment 4 already refuse a symmetry comparison whose two members relaxed into
different geometries. S3 needs the magnetic analogue, because the campaign has now
measured it twice.

**THRESHOLD (adopted as proposed, 2026-08-23):** a pair whose members differ in converged total magnetisation by
more than **0.05 µB** is **CONFOUNDED** — its energy difference mixes the intended
contrast with a basin change — and is excluded from the contrast statistics and reported
separately, exactly as a geometry confound is. The 0.05 µB figure sits far below the
drifts actually observed (11.00 → 14.90 and 11.00 → 14.71 µB) and far above SCF noise in
a converged moment.

**Evidence this is not hypothetical.** Re-scoring the LIT-3 GATE-1 family on 2026-08-22
against its own parents:

| deck | parent E (Ry) | parent µ | child E (Ry) | child µ | Δ child−parent |
|---|---|---|---|---|---|
| `oosh__1x1_off_magm` | −1636.57116531 | 11.00 | −1636.57116516 | 11.00 | +0.002 meV |
| `s0_OOH__1x1_yaw270_magm` | −1636.56955293 | 11.00 | −1636.56955277 | 11.00 | +0.002 meV |
| `s0_OOH__1x1_yaw270_magp` | −1636.56975169 | 11.00 | −1636.56975161 | 11.00 | +0.001 meV |
| `oosh__1x1_off_magp` | −1636.57118655 | 11.00 | −1636.57057718 | **14.90** | **+8.29 meV** |
| `s0_OOH__1x1_yaw90_magm` | −1636.56961270 | 11.00 | −1636.56610153 | **14.71** | **+47.77 meV** |

The three rows that held their moment reproduce to 0.002 meV. The two that changed moment
are the two that move — and both move the **wrong way**: the fixed-geometry child sits
*above* its own relaxed parent. For a re-run at the parent's own relaxed geometry that is
backwards, so it is a diagnostic, not a result.

**THRESHOLD (adopted as proposed, 2026-08-23):** a `__g1` child that lands above its parent by more than **1 meV**
is refused and re-run from the parent's converged density. If the second attempt also
lands above, the pair is recorded MULTISTABLE with both numbers, and neither is banked as
the state's energy.

## A8.4 — Convergence-failure budget (error class 5)

Co *OOH failed 4 times and Ni *OOH 5 times in earlier waves, and those failures were
dropped silently. A dropped non-convergence is a selection effect: the states that fail
are the magnetically frustrated ones — exactly the ones carrying the effect.

**THRESHOLD (adopted as proposed, 2026-08-23):** S3 records a **per-metal, per-state convergence-failure rate**
as a reported quantity, not a log artifact. The escalation ladder is A6.5's, unchanged:
restart from a converged neighbour's density → halve mixing β → record NOT_CONVERGED and
plot as a gap. A metal whose failure rate exceeds **20%** on any state has that state's
contribution to the ranking marked low-confidence in the report rather than dropped.

## A8.5 — The move to Anvil, registered as a change of machine, not of method

The QE build is pinned by an explicit conda lock to the same version and the same
libraries; the decks, the driver, and the pseudopotentials are byte-identical (md5
verified on both ends). What is not identical is the microarchitecture — Vast EPYC 7B12
(Zen 2) against Anvil EPYC 7763 (Zen 3), which dispatch different OpenBLAS kernels.

**THRESHOLD (adopted as proposed 2026-08-23, and already applied):** an Anvil re-run of a banked deck agrees
when |ΔE| ≤ **1e-5 Ry**. The first attempt failed at −8.28 meV; the diagnosis is A8.3's —
the reference chosen was one of the two BASIN_DRIFT rows. Against its own parent, the same
Anvil number agrees to **6.7e-7 Ry (0.009 meV)**. The panel of clean spin-polarised rows
is in docs/46.

**THRESHOLD, entrant's call:** whether the migration is certified is Frank's decision,
made against the panel in docs/46, and it is enforced mechanically — no wave launches
until `$PROJECT/parity/PARITY_PASS` exists. [ADOPTION NOTE 2026-08-23: decided 2026-08-22 — certified; `PARITY_PASS` was created on the entrant's instruction against the docs/46 panel, and every Anvil wave since has run under it.]

**What ran on Anvil before this amendment's deposit (added 2026-08-23, so the record is
in one place; every item is a run of already-DEPOSITED-amendment work under the
PARITY_PASS gate, none of it S3):** the block 1C Cr Hessian waves (jobs 20085020,
20089685 + retry 20090507 — docs/49); the parity control and 5-deck panel (20082656,
20082912 — docs/46); the S3 sizing arms (20083509–14 — docs/48); the S0 gate (i) SnO₂
arm (20094699 — **PASS**, 1.188 meV/atom, docs/51), which anvil/README.md's earlier "S0
stays on Vast" line predates — the box was destroyed with the arm still
precondition-deferred, so completing gate (i) on Anvil is the only way it completes; the
LIT-2 GATE-1 children for the two Cr termination relaxations (20094768 — both AGREE,
+0.004 meV); and the LIT-2 Ru `cov_2OH__2x1_off` **re-run of an unbanked row**
(20094762) — its Vast output reached `JOB_DONE` 2026-08-14 but was never retrieved
before the box's destruction; no number was ever banked, so A8.8's no-replacement clause
does not bite, and the manifest header (`runs/probe/m_lit2_ru_rerun.txt`) records the
loss. This paragraph is the correction-of-record for that loss.

**A consequence worth registering explicitly.** Gate (h) returned 4/4 ADOPT_AFM on the
RuO2 anchors (−144, −80, −85, −111 meV against NM, against a −20 meV rule), and the
adsorption energies move 33–64 meV once the anchor is AFM. Those four AFM points are
single points on NM-relaxed geometries — P11 limit (ii), a lower bound. Adopting AFM as
the anchor's magnetic row therefore owes **four 2×1v AFM relaxations**, which are S3-class
jobs and are priced in A8.6, not in S0's closed budget.

[ADOPTION NOTE 2026-08-23: still open — this paragraph and the A8.1 magnetic-basin row collide (docs/52 row 26; docs/51 skeptic addition iii): whether these four are the Ru second seed inside tier_v3's crossed magnetic-basin factor (then crossed with cell and symmetry, up to 16 relaxations) or four standalone S3-class jobs, and what the A8.1 row's "wherever triage allows" resolves to. No default was drafted, so the blanket adoption decides nothing here; the resolution is the entrant's to write in a dated line. Until he does, the gate-(h) AFM relaxations remain HOLD (0 built — docs/51) and the S3 deck count this amendment fixes is fixed only up to this family.]

## A8.6 — Measured Anvil cost

Measured 2026-08-22 on the gate (g) deck itself, five arms, docs/48. The arms are on the
same BFGS path as the banked Vast run (forces agree step for step to 4 significant
figures), so the timings compare like with like.

| shape | wall per 2×1v relax | SU per relax |
|---|---|---|
| 20 ranks, −nk 4, unbound — today's production shape | ~12 h | ~237 |
| 128 ranks, −nk 16, bound — one whole node | **~1.5–2.1 h** | ~194–269 |

Three facts the schedule now rests on, none of them estimates:

1. Zen 3 is **1.52×** Zen 2 at identical shape (Vast 2745.5 s per first ionic step,
   Anvil 1801.1 s).
2. **SU per ionic step is flat** from 40 to 128 ranks (6.6–7.5 SU) while wall-clock per
   step falls 3×. On `shared`, which bills cores × hours and nothing else, wall-clock is
   therefore nearly free to buy.
3. `--bind-to core` is worth **18%** against the driver's inherited `--bind-to none`, and
   cannot move a number — it changes rank placement, not rank count or reduction order.

**THRESHOLD (adopted as proposed, 2026-08-23):** S3 relaxations run at **128 ranks, −nk 16, `-N 1`**, with the
walltime cap raised from 48 h to a value the entrant sets — `shared` reports
`MaxTime=UNLIMITED`, so 48 h was never a limit, and at the measured rate a 60-step relax
lands inside 4 h anyway. [ADOPTION NOTE 2026-08-23: no walltime value was set at adoption; the 48 h cap stands unchanged until the entrant writes another — at the measured rate it binds nothing.]

**Not proposed, flagged instead:** whether `--bind-to core` becomes the driver's default.
It is free and provably number-neutral, but `queue_r1.sh` is shared with every banked run
and changing it is a decision rather than a measurement. [ADOPTION NOTE 2026-08-23: still flagged, not decided; the driver default is unchanged everywhere, and no new submission script sets it either until the entrant writes the decision.]

**Consequence for the budget.** At ~270 SU per relax the remaining 99,707 SU buys about
370 of them, eight at a time on eight of `shared`'s 250 nodes. Compute is no longer the
constraint on S3; the deck count this amendment fixes is.

## A8.7 — Block 1C's instrument question: what "measured force noise" is, and where amendment 2's escalation leads

**Written 2026-08-23 from docs/49. This section decides nothing. It puts three questions the
Cr 2×1v Hessian surfaced in front of the entrant with the measured consequences of each
answer stated — because the verdict label of block 1C turns on them, and a verdict-bearing
instrument choice is his under P-AUTHORSHIP and A7.7. It is also written with the outcome
known, and says so: docs/49 shows the spectrum under every option, so whatever is chosen
here must be chosen for a stated reason that does not reference which verdict it yields,
and the report must carry both labels if the reason is contestable.** 

[ADOPTION NOTE 2026-08-23: the three questions were put to the entrant with the drafted proposals and the measured consequences of each answer (docs/52 rows); his adoption decides Question 1 = reading (b) for the stated δ-invariance reason, Question 3 = Q4b demoted to reported, and Question 2 resolves to (i) as noted below. Because the choice was made with the outcome known — as this section discloses — the report carries the reading-(a) label alongside wherever the (b) verdict is contestable, as the paragraph above requires.]

**What is not in question.** Block 1C ran 38 clean SCFs on Cr *OOH in the 2×1v production
cell at two displacements; one magnetic basin (M = 23.00 throughout); `conv_thr 1e-10`
reached on every deck; one out-of-plane, hydrogen-carried imaginary mode at i244.7
(δ = 0.01 Å) and i242.8 cm⁻¹ (δ = 0.02 Å), 0.8 % apart, f_y = 1.00; eight real modes
agreeing to ≤ 0.6 %; the hydrogen's out-of-plane energy curvature negative and quadratic
in δ; the mirror-identity force noise at 1.75e-7 / 2.08e-7 Ry/bohr (docs/49 §3, §4a).

**Question 1 — the σ_F instrument.** docs/43 §3-A.3 registers the floor as max(50 cm⁻¹,
3σ) "with σ propagated from the measured force noise". `hessian_analyze.py` measures σ_F
from the Hessian's own asymmetry |H − Hᵀ| (§3-A.4's observable). docs/49 §4–4b measured
that on this system that asymmetry is truncation error at every block — the (y, xz) cross
block scales exactly as a forward difference (σ_F ×4.00 when δ doubles), every other block
exactly as a central difference (×7.85 against an expected ×8) — and nowhere as noise
(×1). docs/43 §3-A.8 and am.4 §7 item 4 already classify the cross block as "structurally
zero … measure noise, not physics" and demoted Q5 on that ground; the measurement says it
is not even noise. The two readings of "measured force noise":

| reading | σ_F (δ 0.01 / 0.02) | 3σ floor on mode #0 | effective floor | block 1C label |
|---|---|---|---|---|
| (a) asymmetry-based, as coded | 2.99e-5 / 1.20e-4 | i265 / i374 | i265 / i374 | UNDERPOWERED / VOID; REFUTED and CONFIRMED unreachable at any δ |
| (b) force noise from identities the SCF does not enforce (the Q6 mirror identities; `hessian_mirror_noise.py`) | 1.75e-7 / 2.08e-7 | ≈ i21 / i15 | **i50** (the declared minimum) | scored against i50, with the mode at i243–i245 and f_y = 1.00 |
| (c) asymmetry-based on the non-cross pairs only | 1.74e-6 / 1.37e-5 | i64 / i126 | i64 / i126 | passes at δ 0.01, UNDERPOWERED (> i80) at δ 0.02 — still an anharmonicity meter |

**THRESHOLD (adopted as proposed, 2026-08-23):** reading (b) is what "measured force noise" means — σ_F is the rms
residual of force identities the SCF does not enforce (mirror identities on a
mirror-symmetric reference), measured on the same decks, reported alongside the
asymmetry diagnostic; the asymmetry is retained and reported as the truncation-error
diagnostic it is. Reason offered, independent of outcome: a noise estimator must be
δ-invariant when the noise is, and (b) is the only one of the three that is (×1.19 vs ×4
and ×7.85). The entrant may instead keep (a) — in which case block 1C is recorded as
UNDERPOWERED/VOID by instrument, not by physics, with the mode reported as a measurement
without a verdict label — or choose (c), or something else. Whatever is chosen, the
choice and its reason are written in his words.

**Question 2 — amendment 2's escalation collides with Q4.** am.2 routes UNDERPOWERED to a
rerun at δ = 0.02 Å. But the Q4b absolute floor is 3√2·σ_design/δ — it falls as 1/δ —
while the forward-difference asymmetry it is tested against grows as δ; and Q4a's σ_F
grows as δ (cross) or δ² (central). So the registered escalation fires Q4a and Q4b by
construction once they were anywhere near threshold at δ = 0.01, which is exactly what
happened (docs/49 §2). Two coherent resolutions, **both proposed, neither chosen here:**
(i) under reading (b) the floor is δ-independent and am.2's rerun keeps its registered
meaning — a harmonic-regime test (passed: 0.8 %) that does not touch the noise floor; Q4
stays a gate on a noise measurement, not on anharmonicity; (ii) alternatively the y rows
return to central differences (the ym decks enter H after Q6 passes), which zeroes the
cross-block asymmetry by construction — at the cost of the ym decks' status as an
independent control, which am.4 §7 fixed for a stated reason. (i) is the smaller change. [ADOPTION NOTE 2026-08-23: with Question 1's reading (b) adopted, resolution (i) is operative by this paragraph's own first clause — under (b) the floor is δ-independent and am.2's rerun keeps its registered meaning; (ii) is not taken, and the ym decks keep their am.4 §7 status as an independent control.]

**Question 3 — Q4b's standing.** The analyzer labels Q4b "CODE-LEVEL, in no docs/43
clause (N32/N33) — reported, not registered" and nonetheless counts it toward VOID. Either
register it here (with its formula and the reading of σ_design it uses) or demote it to
reported, as Q5 was. **THRESHOLD (adopted as proposed, 2026-08-23):** demote to reported; the gate it duplicates
(Q4a) carries the registered meaning, and a gate that is not registered must not void a
state.

**Consequence for S3 (A8.1 "Cr 1C + re-Hessian at escape").** Every re-Hessian in S3 is on
a mirror-symmetric or near-symmetric reference and will present the same estimator
behaviour; the answer to Question 1 is therefore an S3 protocol parameter, not a Cr
footnote, and must be settled in this amendment before the first S3 Hessian is built.
`hessian_analyze.py` is NOT changed until it is; docs/49 and the banked outputs
(`runs/probe/Cr_hess`, `runs/probe_d02/Cr_hess`) carry the numbers under every reading.

## A8.8 — What this amendment does NOT license

- It does not reopen any closed S0 gate.
- It does not license a new tier, a new adsorbate, or an oxyhydroxide phase.
- It does not change the production convention U = 0 on Ru and Ir.
- It does not permit re-running a banked Vast number on Anvil and **replacing** it. A
  re-run is a new measurement reported alongside, or a correction with a stated reason —
  never a silent overwrite. The banked tree is read-only by construction: every parity and
  sizing job writes into its own isolated directory.
- It does not license loosening the parity threshold to accommodate a measurement. A gate
  widened until the data fits is the failure mode this project exists to indict.

## A8.9 — Deposit obligation

Per A7.8, docs/43 complete (A1–A8) is re-deposited to Zenodo as a new version of record
10.5281/zenodo.21963144 — restricted access, DOI and timestamp public, files closed until
report submission — **before the first S3 deck launches**. The new version DOI is recorded
here in a dated line when it exists.

**DOI line (2026-08-23):** docs/43 complete (A1-A9) was deposited and published as Zenodo record **10.5281/zenodo.22072991** (new version of concept 10.5281/zenodo.21963143; restricted access: DOI + timestamp public, file closed until report submission; file `43-prereg-week1-factorial-A1-A9.md`, 187,187 bytes, md5 `7e10c62063fb624c4a70f63ff201cce1`, sha256 `cac535df9b26fa81220a64b5f52ed7b4bf68b5e7033552086dd8dac7e2b9ba5e` — exactly the state committed at 1c09c38). The deposit obligation of A8.9 and A9.7 is discharged in one version, per the ordering rule's second branch. Text added after publication; the deposited file is the frozen artifact.


# AMENDMENT 9 — 2026-08-23, adopted by the entrant, before any external corpus is parsed

**Adoption record.** This amendment was AI-drafted as disclosed research infrastructure
under A7.7 (docs/50, drafted 2026-08-22–23, three-lens critique applied). The draft
required every THRESHOLD to be re-authored by the entrant before deposit. What happened
instead, recorded as the authorship event: the entrant reviewed every open decision
through the indexed decision sheet docs/52 (66 rows, each quoting the drafted options
verbatim with file:line) and adopted the drafted proposals as his decisions — his words,
from the session log of 2026-08-23: "I went through them and they pass with me. Go
ahead." Every marker below reads "THRESHOLD (adopted as proposed, 2026-08-23)"; items
that had no drafted default remain OPEN, are annotated in place, and are re-listed in
the ADOPTION STATUS block at the end of A9.5. Adoption-time annotations are bracketed
and change no drafted content. A7.7's model is unchanged: AI drafted, the entrant
decided, the report paraphrases and never copies.

**Correction of record, entering with this amendment (the entrant's decision 2026-08-23,
drafted by AI and adopted; amends a DEPOSITED clause without editing it):** the docs/43
§6 gate "a correction that moves η by ≥ 0.10 V while leaving |z| ≥ 3 has not fixed the
scaling anomaly" (:331-337, deposited with A1–A7) is **withdrawn**. Reason: the pooled
±0.12 eV 1σ behind z is pseudo-replicated — 515 rows from 24 articles with one article
supplying 24 % of rows — so |z| ≥ 3 is not the test it was registered as. The z column
is retained as reported; if a gate is wanted, the Divanis rutile-only n = 38 sub-fit
replaces the pooled intercept (A9.3.4). The deposited A1–A7 text is not edited.

**Governs:** S1 — `silentgate` v0.1 (entrant-written core, readers, two CI controls);
S2 — the external census (Xu 810-output lock/direction census, span_U halves, Divanis
δ-curve, pymatgen census paired with the atomate input-set audit, restored
literature-coding audit); the disclosure of the 2026-08-15 pre-registration sampling.

## A9.0 — Why this amendment is being written now, and what changed under it

A9 was scheduled on 2026-08-16 (docs/45 §D) to be deposited by Aug 22, before the first external corpus is parsed, because S1 (Aug 21–27) and S2 (Aug 27 – Sep 5) are the critical path of the closure (round-2 synthesis :206, :225) and every amendment goes to Zenodo before the first act it governs (docs/45 :58-61; docs/43 A7.8 :1449-1464). Four things the amendment must absorb:

1. **The deadline passed with nothing parsed by the entrant.** Verified by `ls` on 2026-08-23: there is no local copy of the Xu deposit in the repo (zero `pwscf.out` files tracked; no `rutile-OER/` directory), no OC20 data on disk (no LMDB / `.traj` / OC20 extxyz / OUTCAR anywhere in the repo — the only `.extxyz` files are this campaign's own `data/qe_frames*.extxyz`; `.venv-fairchem/` holds the libraries only), no `silentgate/` package, no CI (`.github/` does not exist), and `src/dft/symops_audit.py` has never been pointed at anything but `runs/` (its only CSV, `docs/figs/symops_audit.csv`, is 156 `runs/`-relative rows, committed 137010b on 2026-08-09). S1 and S2 remain blocked on this document. The slip is one day and costs no blindness that was not already spent (item 3).
2. **S0 closed and A8 is in draft** (docs/47, 2026-08-23). A8 governs S3 compute; A9 governs zero-compute work plus, at most, the two gas-reference SCFs of A9.3.3. The two are independent in content and are sequenced in A9.7.
3. **Pre-registration sampling already happened, on 2026-08-15, by an AI agent — not by the entrant.** It is disclosed in full here and again at the point it touches a prediction (A9.3). The numbers it returned are pre-registration observations; they are not results and will be re-derived, from scratch, by the registered detector over the full population. The only narrative record is docs/research/2026-08-15-lit-sweep-lens-digest.md (:253-261, :297-303, :314). **What was retained and what was not:** the header/force sampling script was NOT retained and no results file exists; the pymatgen census script, the mirror tree listing, and one Xu deck/output pair WERE retained, in an ephemeral session scratchpad, and are hashed here so that the disclosure does not depend on that directory surviving. **Registered obligation before deposit — DISCHARGED 2026-08-23:** these files (plus `t.py`, the Divanis ESI PDF and its text extraction) are filed in `docs/research/2026-08-15-sampling/` with `SHA256SUMS` and a README stating provenance and licence (the deck/output pair committed as the single format-validation fixture with attribution — CC0 on Zenodo, CC-BY-4.0 on the mirror); the entrant may still elect to drop the output from git and keep the hash. [ADOPTION NOTE 2026-08-23: the output is retained in git; the drop-election is not exercised.] The sampled items:
   - the complete file tree of the GitHub mirror `zhongnanxu/rutile-OER` at commit `c4cb89260586229f6a007072ca9e4eeed545d622`, fetched via the GitHub API — a listing, not contents — retained as `xu_tree.json` (2,663,448 bytes, sha256 `d20af9dbfbbbdc05714b352ac15b176e75b4096f5bff475159395187c957e8b9`; 8,247 entries, 6,989 blobs, 815 `pwscf.in` + 815 `pwscf.out`);
   - **40 of 810 Eads output headers** (10 metals × {bare, O-relax, OH-relax, OOH-relax}): 40/40 non-trivial — 4 Sym. Ops. for bare and *O, 2 for *OH and *OOH. Those job names exist only under `Eads-4-layers/`, so the sample is inferred (not recorded) to be the 4-layer U = 0, `nspin = 1` relaxations; **0 of the 680 two-layer U-ladder headers were read**;
   - **12 of 810 final-ionic-step force blocks** (CrO₂, MnO₂, IrO₂, TiO₂ × {*O, *OH, *OOH}): *O has F_x and F_y exactly 0.00000000; *OH has F_y exactly 0 on both atoms; *OOH has F_x exactly 0 on all three atoms — i.e. *OH and *OOH locked on orthogonal lateral axes on those four metals. Forces are blind by record on MoO₂, NbO₂, PtO₂, ReO₂, RhO₂, RuO₂ (6 of 10);
   - three decks read: RuO₂ 4-layer *OOH (`nat = 51`, `nspin = 1`, U = 0, adsorbate x = 0.50000 exactly; retained as `ruo2_ooh.in`, sha256 `447b73e34bca7eabdfea9627c1243dcbbdc54e7f045a86c11dd0dbbf8a1dc0e8` — its `&IONS` block is empty, so it sets **no** `forc_conv_thr`; species are suffixed `O0 / Ru1 / H2`; the adsorbate atoms are the last three `ATOMIC_POSITIONS` lines, `O0, O0, H2`), CrO₂ `Eads-2-layers/OOH-U-4.0` (`calculation = 'relax'`, 33 atoms, `nspin = 2`, `tot_magnetization = 15`), and the CrO₂ linear-response `alpha_0` deck (48-atom bulk, 4×4×4 k);
   - **one full output cached locally** — RuO₂ 4-layer `OOH-relax` (`ruo2_ooh.out`, 1,328,638 bytes, sha256 `2b9bc0dd56c79b93dfa3b7539f8b128dac8dd6ac61f36c0a22b4814ad3e6c620`; 17 force blocks; header `2 Sym. Ops. (no inversion) found`) — the only Xu output content physically on this machine. Whether its force blocks were looked at on 2026-08-15 is **not recorded**; RuO₂ *OOH is therefore **blind by record, not by availability**, and the blind-metal count is stated both ways below (6 by record, 5 by availability);
   - fairchem's OC20 `VASP_FLAGS` source read (`src/fairchem/data/oc/utils/vasp_flags.py`: `isym = 0`, `symprec = 1e-10`, `ispin = 1`) — no OC20 data touched;
   - a pymatgen `AdsorbateSiteFinder` census run **outside the repo** on a pymatgen-built RuO₂(110) slab (A9.3.5); the script is retained as `t2.py` (sha256 `f4d9777f4830d5cd83b99bd93f1799c29f40b611daff07daa8909879ef1bb3e9`) and its exact arguments are written into A9.3.5.
   The agent's own statements stand on the record: "I did NOT check all 810; the sample is 4 of 10 metals for forces and 10 of 10 for headers" and "I verified contents via the GitHub mirror instead and am ASSUMING the zip mirrors it" (lens-digest :301, :314).
4. **The 2026-08-16 addendum restored the literature-coding audit** (round-2 :579-582; docs/45 §E row S2) after round-2 had cut it on budget grounds. Its registration therefore belongs here and was missing from round-2's A9 list (:479-485), which was written before the restoration. The Xu *repair* is a different case: round-2 :570 cuts it, the addendum names it in neither its physics-kill list nor its reverted-budget list, and round-1 :225 gives mixed reasons and a minimum-viable fallback — so its disposition is the **entrant's call**, presented as such in A9.5 item 1, not decided here.

---

## A9.1 — The instrument: what `silentgate` v0.1 measures, and who writes it

**What it measures.** `silentgate` reads a relaxation output and returns, per atom, per Cartesian axis, per ionic step, whether the printed force component is exactly zero; from that it reports the **lock direction** of each adsorbate atom (the set of lateral axes on which the component is exactly zero in every step), and it reads, where the format carries one, the **size of the symmetry group the code kept** (pw.x: the count-first header `N Sym. Ops. ... found`, or `No symmetry found` = identity = 1 operation). Header and force block are two separate witnesses to the same thing; on the 96 classifiable adsorbate rows of `docs/figs/symops_audit.csv` at commit 137010b they agreed 96/96 (docs/41 :930-932; the CSV carries 98 rows with an adsorbate, two of which — `Cu_slab/s0_OH.out`, `probe/Ru_spin/s0_OH__spin0.5.out` — have no force block to classify). Where they disagree, the force evidence wins and the disagreement is itself reported.

**Scope of v0.1, stated as a narrowing.** Round-2 :209 and round-1 :50 describe S1 as lifting "the five existing detectors" into one pip-installable package. v0.1 as registered here is **the symmetry-lock detector** — header read, per-atom/per-axis/per-step exact-zero census, the three classes, the direction map — **plus the two QE readers S2 needs and that nothing else supplies:** a per-step total-energy reader over the 680-file ladder (for span_U, A9.3.3) and a per-deck reader for `tot_magnetization`, `nspin`, U and `forc_conv_thr` (A9.3.2). Those readers are core under the authorship rule below. The "five existing detectors" are not enumerated anywhere in the repo; the candidates in `src/dft/` are `symops_audit.py`, `orient_starts.py`, `qe_qc.py`, `adsorbate_qc.py`, and `hessian_mirror_noise.py` / `hessian_analyze.py` — **the entrant confirms the list.** [ADOPTION NOTE 2026-08-23: list confirmed as the six candidates named; none is lifted into the core; no `legacy/` sub-module exists unless the entrant later adds one with a dated line.] None of them is lifted into the core: the core is written from scratch by the entrant; any legacy detector he wants in the package goes into a clearly separated `silentgate/legacy/` sub-module, lifted as-is with its existing authorship recorded in the AI-use log, and is not exercised by the controls. Everything else round-2 :209 alludes to is out of v0.1 scope.

**The three classes, per axis.** The registered vocabulary of docs/41 §6g (:937-945) and docs/43 §0a (:46-51, :62-65) is carried over unchanged and generalised from "F_y" to "the named axis": LOCKED — ≥2 operations kept and the component symmetrised to exactly 0.0 in every step; ON_PLANE — no symmetry enforced and max|F_axis| below the per-corpus noise floor; EXPLORED — max|F_axis| at or above it. **Run-level rule, registered:** a run is LOCKED when it has ≥2 operations and at least one lateral axis is exactly zero on every step for every adsorbate atom; on the 20 in-house production runs this coincides with docs/43 §0a's F_y class, because F_y was the only axis censused there (stated so the old table and the new one are the same object). The docs/43 consequence stands for every corpus: `nosym` is not a treatment; a claim that a state was searched off a plane must cite its measured max|F_axis|, never the presence of a flag.

**THRESHOLD (adopted as proposed, 2026-08-23) — the per-corpus noise floor, registered as a RULE so that nothing need be read before deposit.** The ON_PLANE/EXPLORED boundary is, per corpus, **floor = `forc_conv_thr` / 20 in that corpus's force units, read per deck at parse time; where a deck sets none, the pw.x default 1e-3 Ry/bohr applies.** In-house this reproduces the registered **1e-4 Ry/au** (docs/41 §6g, docs/43 §0a :48, `FY_NOISE` in `symops_audit.py` :95): every production deck sets `forc_conv_thr = 2.0d-3` (450 of 450 `forc_conv_thr` lines under `runs/`, verified 2026-08-23 — the code comment at `symops_audit.py` :93-94 that says "1e-3" is wrong and is corrected in the S1 commit), so 1e-4 is a factor 20 below the threshold, not a decade; the in-house floor is retained at 1e-4 because it is the floor already published with those classes and moving it now would be post hoc. For the Xu corpus the same rule gives the **expected** floor 5e-5 Ry/bohr for a deck that sets none (the one cached deck sets none); the value actually found is reported per deck and **never moved after the parse**. (If the entrant prefers the round-number rule floor = `forc_conv_thr`/10, the in-house floor becomes 2e-4 Ry/au; no production row lies in (1e-4, 2e-4] — CSV values below: 3.998e-05, 1.573e-05, 2.59e-06, 7.8e-07, 4e-08, 8e-08; above: 0.00049, 0.00078, 0.00103, 0.00234, 0.0168, 0.0394 — so no class changes; that is his call, written once.) **OC20: no ON_PLANE class is used** — the negative control scores LOCKED only (A9.2), so no floor is needed there and none is declared. Because symmetry-ON corpora yield LOCKED lower bounds only (A9.2.3), the Xu ON_PLANE/EXPLORED rows are descriptive and no pre-deposit number is needed for any scored clause.

**Readers and the registered adsorbate-identification rule.** Every force clause in this amendment is defined over adsorbate atoms; the rule that names them is fixed here, per reader, before any parse, and a deck on which it is ambiguous is **reported, not silently dropped**. pw.x `pwscf.out` (the native format of this campaign and of the Xu deposit — round-2 :209): adsorbate atoms are the atoms whose index exceeds `nat` of the same-metal, same-layer-count bare deck (Xu appends them last — the cached deck ends `O0, O0, H2`; 2-layer: any `bare-U-x` of that metal, since a bare slab's `nat` does not depend on U; 4-layer: `bare`; if the bare `nat` differs across U for any metal, that metal's outputs are UNIDENTIFIED until the entrant resolves it in a dated line), cross-checked by species symbol with its numeric suffix stripped ∈ {O, H} and by z above the topmost metal atom; disagreement between the two rules → the output is **UNIDENTIFIED**, excluded from the adsorbate denominators with the count printed on the figure face; atoms with any `if_pos = 0` are excluded from every exact-zero count and their number reported (pw.x prints the if_pos-masked force, so a fixed coordinate reads exactly zero for a reason that is not symmetry). In-house outputs: the same tag-free rule, with the legacy `s0_O/s0_OH/s0_OOH` filename tag used only as a consistency check — the rule must reproduce the tag counts 20/20 on the production runs, and that agreement is printed by CI. OC20: adsorbate = ASE `tags == 2`; forces read raw (`apply_constraint=False`), and `FixAtoms`-constrained atoms excluded from all counts (ASE's default `get_forces()` applies the constraint and returns exact zeros on every fixed slab atom, which would flood the all-atom count or void the control for a reader reason). A corpus without a symmetry header (OC20's trajectories carry forces but no space-group line) is read in **force-only mode**, and the output says so: LOCKED in force-only mode means "exact-zero component on every step," with no header witness. VASP OUTCAR: a reader slot exists in the interface for completeness; no corpus in this program uses it (the OC22 arm is cut), and if one is ever written its adsorbate rule is registered then, not now. The OC20 artefact class is general knowledge flagged as such (no OC20 file has been opened locally); the precision of the stored forces is recorded at download as a dated fact (A9.2.1).

**Header-format validation, registered as the first act AFTER the DOI line.** `symops_audit.py` matches only the count-first header of pw.x 7.5 (:43-48) while its own docstring shows the older `Sym. Ops., with inversion, found N` form (:12-13). Xu's 2014-era outputs may use either. The reader accepts **both** forms by regex and logs the form encountered per file. The validation itself — reading one header of each of the four states from one metal's `Eads-4-layers/{bare,O-relax,OH-relax,OOH-relax}/pwscf.out` — is **not** done before deposit; it is the first parse after the DOI line exists (after the zip is fetched and its listing compared, A9.7), the four file paths are named in a dated line under A9.7 at that time, the outcome is logged, and a reader failure is a reader fix and never a threshold change. The one cached Xu output already shows count-first for one 2014 job, which is evidence for one file and not for the corpus.

**The three confirmed defects of the current code, which v0.1 must not inherit** (round-2 :210-212; code lines verified 2026-08-23): (a) `adsorbate_max_fy` reads only `group(3)` = F_y (:76-90), so it cannot see an x-lock or a double lock and returns a boolean, not a direction; (b) `slab_atom_count` infers adsorbate indices from this repo's `s0_O`/`s0_OH`/`s0_OOH` filename tags (:120-135), so any other naming — Xu's `OOH-relax/pwscf.out` included — is silently treated as adsorbate-free — the replacement rule is the one registered above; (c) `FY_NOISE` is hard-coded and not derived per corpus (:95) — replaced by the rule above. Two further limits of record: it requires `Program PWSCF` (:154) and cannot call LOCKED without a header (:113-114), so it has never been exercised on a header-less corpus.

**Who writes it — the boundary made checkable.** Verbatim from the program (round-2 :218; round-1 :52): "THE ENTRANT WRITES THE CORE HIMSELF — a few hundred lines of output parsing plus a symmetry-op header read and an exact-zero force census — with AI limited to test scaffolding, CI and review. Rule: AI may not author the object the project is named after." A7.7 already records the silentgate core as something AI did not produce (docs/43 :1447). Under this amendment the **core is the named module set** `silentgate/readers/*` (pw.x force/header/energy/deck readers, the OC20 trajectory reader), `silentgate/census.py`, `silentgate/classify.py`, `silentgate/direction.py` and `silentgate/cli.py` — written and committed only by the entrant. AI may write tests and fixtures, the CI workflow, and review comments, each logged in the AI-use log as produced; "packaging" means `pyproject` metadata, the version string and the console-script entry-point declaration only — **flagged:** this is one word wider than round-2 :218's "test scaffolding, CI and review," and the entrant decides whether even that is allowed. [ADOPTION NOTE 2026-08-23: allowed as defined here — pyproject metadata, the version string and the entry-point declaration, nothing wider.] CI asserts that the AI-use log's file list and the core path list are **disjoint**, and prints the assertion's status next to the controls, so that "AI never touched the core" is a checked fact and not a sentence. **Second flag for the entrant:** round-2 :218 says the rule-sentence "goes verbatim in the 100-word disclosure," while A7.7 forbids reproducing any amendment sentence verbatim in an application answer (docs/43 :1443-1445). The proposed resolution is that the entrant writes the rule in his own words in the Task 4 disclosure (docs/25 :110-120; docs/44 :125-126) and cites the AI-use log; this draft does not supply disclosure wording.

**Packaging and release.** One pip-installable package with a CLI and pluggable readers (round-2 :209), the core and any `legacy/` sub-module separated as above. v0.1 at S1 is the instrument; "v1.0 with a Zenodo DOI" at S7 appears in the report only as a bibliography entry — the word "released" does not appear in the headline sentence (round-2 :220-221, :311). The corpora it reads stay out of git; this repo is public.

---

## A9.2 — P-CTRL: the two controls, registered as a GATE

**Why a gate.** F4 (round-2 :510-511): the detector is wrong in the same direction as the finding; every number flows through code written by the person who believes the trap is real. P-CTRL therefore voids rather than caveats. **Any drift voids the corresponding numbers rather than caveating them.**

### A9.2.1 — NEGATIVE control (false-positive rate)

**Corpus.** OC20 (10.1021/acscatal.0c04525): slab/adslab relaxations run with `isym = 0`, `symprec = 1e-10`, `ispin = 1`, verified by the 2026-08-15 sweep from fairchem's `src/fairchem/data/oc/utils/vasp_flags.py` (lens-digest :254, :302; round-2 :141); symmetry disabled by construction, so "the answer is zero by construction — a gate, not a finding" (round-2 :141, :430). **Not on disk** (A9.0 item 1). **THRESHOLD (adopted as proposed, 2026-08-23) — artefact class and split, fixed now from public documentation, no file fetched:** the negative corpus is **whole-relaxation, per-system trajectories from OC20's relaxation-trajectory release** (the fairchem `DATASET.md` section on relaxation trajectories — general knowledge, flagged); S2EF frame subsets are ineligible because the LOCKED criterion needs every ionic step of a system. The proposed draw is the smallest in-domain validation split that release offers (`val_id`, if the documentation confirms that name); the artefact name, URL, md5 and licence line (CC-BY-4.0 is the expected licence — confirmed from the documentation, not assumed) are copied from `DATASET.md` into this section **before deposit** — reading documentation is not parsing a corpus (A9.6). [ADOPTION NOTE 2026-08-23: the artefact line, copied from the documentation on 2026-08-23. fairchem's DATASET.md content now lives at `docs/catalysts/datasets/oc20.md` in `FAIR-Chem/fairchem@main` (fetched 2026-08-23, sha256 `8acc6821e19f6753ef9bd5b06bbbb74c1bd3ceae62656cbeaf23042db06e434f`). The relaxation-trajectory release confirms the split name: artefact **"val_id (~25K trajectories)"**, 5.9G compressed / 46G uncompressed, md5 `fcb71363018fb1e7127db2500e39e11a`, URL https://dl.fbaipublicfiles.com/opencatalystproject/data/is2res_val_id_trajectories.tar; licence **CC-BY-4.0**, stated twice in the document (once as CC-BY-4.0 in the metadata table, once spelled out as "Creative Commons Attribution 4.0 License" in the citation section, both linking the same legalcode URL); the document's own update note revises val_id IS2RE/IS2RS system counts 24,946 → 24,943. The negative corpus is therefore fully fixed: the first 500 trajectory filenames in ascending lexical order inside that tar.] The download itself happens **after** the DOI line; the files are stored outside git on the STS machine or Anvil scratch (STS-scope use of the ACCESS allocation), with a sha256 manifest of the files used committed to the repo.

**THRESHOLD (adopted as proposed, 2026-08-23) — size and selection rule.** **N = 500 relaxations**, taken as the first 500 trajectory filenames in ascending lexical order inside the named artefact, fixed in this text before download; no re-draw, no substitution, no second sample. Any enlargement is additive and disclosed. The rule exists so that the control cannot be re-drawn until it passes.

**THRESHOLD (adopted as proposed, 2026-08-23) — pass condition.** In force-only mode, **exactly 0.00 % of the 500 relaxations** contain any adsorbate atom (`tags == 2`) with a lateral force component that is exactly zero in every ionic step (the LOCKED criterion), with constrained atoms excluded per A9.1, and the per-step exact-zero count over all unconstrained atoms and axes is reported alongside. **Any nonzero rate voids every downstream symmetry number until the detector is repaired** (round-2 :481 — its wording is kept). A nonzero rate may not be explained away as print quantisation by argument; if it occurs, the offending frames are exhibited and the number stays void until the detector is repaired. The exact-zero test is defined **at the stored precision of the distributed artefact**, which is recorded at download as a dated fact and bounds what the control certifies.

**What this control certifies, stated so it is not over-read.** OC20 forces are VASP floats in eV/Å at whatever precision the artefact stores (UNKNOWN until download; the 6-decimal OUTCAR convention is general knowledge) and arrive through the trajectory reader, not through the QE reader the Xu census uses; the same print-quantisation caveat that kills any OC22 symmetry arm (round-2 :216, :435) applies to what 0.00 % here means. OC20 therefore certifies the **trajectory reader and the exact-zero census on float forces**. It does not certify the QE reader. For the QE reader the same-code negative control is in-house and already on disk: **the 11 `nosym`-present production relaxations** (Mn, Fe, Co, Ni, Cu; docs/41 :966-970; 0 LOCKED, 6 ON_PLANE + 5 EXPLORED), which A9 registers as the QE-reader negative control and which also serve as the `nosym`-present half of the positive partition in A9.2.2 (the same 11 runs, two roles, stated once). **THRESHOLD (adopted as proposed, 2026-08-23), scored in FORCE-ONLY mode with the header witness ignored:** 0 of the 11 has any adsorbate atom with a lateral force component exactly 0.0 in every printed step; the two-witness class is reported alongside. Stated because the two-witness form cannot fail by construction — every `nosym` run prints `No symmetry found` (n_symops = 1 in the CSV), so the header alone excludes LOCKED whatever the forces say. Force-only, the gate is non-trivial: it passes today on y (CSV `max_fy_adsorbate` for the 11 ranges 4e-08 to 0.039, none exactly 0.0) and is **unmeasured on x** until v0.1 reports it. Re-run on every commit.

### A9.2.2 — POSITIVE control (the partition this campaign already reported)

**Correction of record.** Round-2 :214/:481 and round-1 :183 word the positive control as "≥95 % LOCKED over this campaign's own 20 `nosym`-absent production relaxations" (round-1 :51 says "this campaign's own 20 production relaxations must return ≥95% LOCKED, reproducing the 20-for-20 `nosym` partition"). The 20-`nosym`-absent population does not exist. docs/41 §6g (:949-970) and docs/43 §0a (:46-51) record **20 production adsorbate relaxations in total**, of which **9 are `nosym`-absent (Cr, Ir, Ru × *O/*OH/*OOH; all 9 LOCKED)** and **11 are `nosym`-present (0 LOCKED)**; "20-for-20" is the flag→class partition, not a LOCKED rate. A literal ≥95 %-of-20 gate would void the campaign's own finding on day one. The control is re-stated against the record:

**THRESHOLD (adopted as proposed, 2026-08-23).** Over the 20 production relaxations enumerated by file in `docs/figs/symops_audit.csv` at commit 137010b (docs/41 :1050) — `runs/{Cr_slab,Ir_anchor,Ru_anchor}/s0_{O,OH,OOH}.out` (9) and `runs/Co_slab/s0_O.out, runs/Co_slab/s0_OH.out, runs/Cu_slab/s0_OOH.out, runs/Fe_slab/s0_{O,OH,OOH}.out, runs/Mn_slab/s0_{O,OH,OOH}.out, runs/Ni_slab/s0_O.out, runs/Ni_slab/s0_OH.out` (11); the four missing cells of the 24-cell table are **Co *OOH and Ni *OOH (absent by record), Cu *O (absent by record), and Cu *OH (present as `runs/Cu_slab/s0_OH.out` but an `scf` with 0 force blocks — unscorable, docs/41 :955-962)** — `silentgate` returns **9/9 LOCKED on the `nosym`-absent set (scored two-witness AND force-only with the header ignored), 0/11 LOCKED on the `nosym`-present set (A9.2.1), and the 20-for-20 partition by the deck's `nosym` line**, with header-vs-force two-witness agreement **on every classifiable adsorbate row of `docs/figs/symops_audit.csv` at the commit CI runs against, n/n printed (96 of 98 rows at 137010b; 2 unclassifiable single-points named above)**. Any miss voids the 20-for-20 partition claim (round-2 :481) and halts the census until repaired — **repaired toward the raw force evidence, which wins:** if the raw outputs show an archived CSV row wrong, the CSV is corrected as a correction of record and the detector is not changed to match it. Supplementary, MEASURED but not gating unless the entrant adds them: the symmetry-ON adsorbate relaxations and fixed-geometry SCFs added to `runs/probe/` after Aug 9 (`Cr_hess, Cr_lit2, Cr_lit3, Ir_lit3, Ru_lit2, Ru_lit3, Ni_basin, Cr_cellsym, Ir_cellsym, Ru_cellsym, Cr_basin, …` are present on disk and not in the Aug 9 CSV) — their count was tallied off-repo as 22 relaxations + 48 SCFs and is **UNKNOWN in the repo until `symops_audit.csv` is regenerated at HEAD, which fixes the number**; for all of them v0.1 reports the class and direction per axis. Known in advance and to be reported, not hidden: in-house *OH and *OOH both lock **y** — the same axis — (CSV rows `Cr_slab/s0_OH.out`, `Cr_slab/s0_OOH.out` and the Ir/Ru counterparts: n_symops = 2, max|F_y| = 0.0), and in-house 1×1 *O locks y MEASURED and x INFERRED (n_symops = 4 with F_y = 0.0 — the 4-operation group of a 1×1 rutile(110) cell with the adsorbate on y = 0 contains both lateral mirrors — F_x was never censused by the current code and is reported by v0.1), whereas the Xu sample shows *OH on y and *OOH on x (lens-digest :256). The positive control checks the detector, not the direction map.

### A9.2.3 — CI semantics and the registered scope limit

**Both controls live in CI and re-run on every commit; the amendment records their status at the moment each audit number is generated** (round-2 :214, :511). Mechanically (proposed; no CI exists today — `.github/` absent by `ls` 2026-08-23): the in-house positive and QE-negative controls run natively on every commit because `runs/` is tracked (all 384 `.out` files and the 23 production decks; seconds to run). The OC20 control cannot see a sample that lives only on the STS machine — so, **THRESHOLD (open at adoption 2026-08-23 — entrant's call between two mechanisms, written once in a dated line before the OC20 control first runs in CI):** (a) the 500-file sample is published as a sha256-pinned release asset of the public repo (CC-BY-4.0 permits redistribution with attribution; ~0.5–2 GB, UNKNOWN until drawn) and the workflow downloads and hash-checks it; or (b) a self-hosted runner on the STS machine holds the sample. Under either, **a commit on which the OC20 job did not execute is not green.** Every census table, figure and CSV written by `silentgate` carries the commit hash and the control status at that commit on its face; a control regression fails the build and marks every number produced after the last green commit VOID. Control results are recorded with the status vocabulary MEASURED / BOUNDED / TRANSFERRED / NOT MEASURED (docs/43 :1433 — "STRUCTURALLY ZERO" is struck; docs/45 :6-8).

**Registered scope limit, worded to be consistent.** P-CTRL measures the **false-positive** rate only. No false-negative rate on a symmetry-ON corpus exists and no claim may depend on one (round-2 :216). Consequently, on any symmetry-ON corpus only **LOCKED counts — lower bounds on exposure** — may be claimed; "not LOCKED" is never read as "free," "searched," or "unconstrained," anywhere in this program. Round-2 :481's broader sentence ("no symmetry claim about any symmetry-ON corpus may be made") is read in this sense; read literally it would forbid P-XU, and that is not its intent.

---

## A9.3 — The external census (S2): deliverables and acceptance, registered before the parse

### A9.3.1 — The Xu deposit: attribution facts and the verification gate

Paper: Xu, Rossmeisl & Kitchin, J. Phys. Chem. C 2015, 119, 4827–4833 (10.1021/jp511426q); data: 10.5281/zenodo.12635, CC0, one file `rutile-OER-v1.0.zip`, 572.4 MB; mirror: `github.com/zhongnanxu/rutile-OER`, CC-BY-4.0, created 2014-11-07 (round-2 :429; lens-digest :256). **Attribute regardless of mirror.** Contents per the hashed mirror listing (A9.0 item 3; counts re-derived from `xu_tree.json` on 2026-08-23): 815 `pwscf.in` + 815 `pwscf.out`, Quantum ESPRESSO; **810 Eads outputs = 81 per metal × 10 metals** (CrO₂, IrO₂, MnO₂, MoO₂, NbO₂, PtO₂, ReO₂, RhO₂, RuO₂, TiO₂) — per metal `Eads-2-layers/` holds 74 jobs ({bare,O,OH,OOH}-U-{0.0..8.0} = 68, the **680-file U ladder**, plus O/OH/OOH and O/OH/OOH-relax-surf; there is no unsuffixed 2-layer `bare`) and `Eads-4-layers/` holds 7 (bare, O, OH, OOH, O-relax, OH-relax, OOH-relax); so each metal has **21 *OH and 21 *OOH outputs** (17 ladder rungs + 2-layer single + relax-surf + 4-layer single + relax, each) and **18 bare outputs** (17 `bare-U-x` + 1 four-layer `bare`); bulk linear-response inputs (48-atom Cococcioni supercell, `Hubbard_alpha` ∈ {0, ±0.07, ±0.15}, 4×4×4 k) under `supporting-data/linear-response/`; SnO₂ is bulk-EOS only (no slabs, no Eads); 671.65 MB of `.out` in total (lens-digest). Deck facts read so far (one deck each, A9.0): 2-layer ladder `calculation = 'relax'`, 33 atoms, `nspin = 2`, U on the metal species only, `U_projection_type = 'atomic'`, ecutwfc 40 / ecutrho 500 Ry, GBRV ultrasofts, 4×4×1 k, MP smearing 0.01 Ry, `tot_magnetization = 15`; 4-layer RuO₂ *OOH `nspin = 1`, U = 0, no `forc_conv_thr` set. Xu's Table 1 linear-response U values are already load-bearing in docs/43 (U_Cr = 7.15 eV, :1201, :1327; U_Ru = 6.73 eV and U_Ir = 5.91 eV, :1240); A6.7 records that Xu's linear-response U is bulk-only, so this campaign's slab-DFPT non-convergence observation **survives as first-of-kind** (docs/43 :1294-1298), and A6.7's attribution debts — the on-rutile U-dependence and the p. 4831 "except perhaps near the top of the volcano" caveat — remain binding on report drafting (docs/43 :1294-1302).

**Verification gate before any file is cited to the DOI** (lens-digest :314): the census parses the **Zenodo zip**, after its file listing has been compared with the hashed mirror listing — **comparison unit: the 6,989 blob paths and sizes from `xu_tree.json`; for each of the 815 `pwscf.out` the git blob SHA-1 in the listing is recomputed from the zip file's bytes** (git's blob hash, not a plain SHA-1 of the file). If they differ, both listings are reported and the zip is the population. Until that comparison is done, every count above is "per the GitHub mirror at `c4cb892`." The comparison is a listing operation and is not parsing (A9.6), but it is done after the DOI line all the same, because the zip is not fetched before it.

### A9.3.2 — Census product 1: the lock census and the direction map (P-XU)

**Deliverable.** Over all 810 Eads outputs: symmetry-op header count; per-atom, per-axis exact-zero force census in the final ionic step and across every step; the lock-direction map per metal per rung; `tot_magnetization`, `nspin`, U, `calculation` and `forc_conv_thr` read **per deck** (the frozen-15 statement was read from one deck and cannot yet be asserted for all 680). Reported as one table per product, raw, with the denominator on the figure face.

**Denominators fixed before the parse.** The header clause runs over all **810**. The adsorbate-force clause runs over the **630 adsorbate-bearing outputs** (810 minus 18 bare per metal, per the hashed listing) — "an exactly-zero adsorbate force component" is undefined for a bare slab; UNIDENTIFIED outputs (A9.1) are removed from the 630 with the count on the face. **An output with zero force blocks is NO_FORCE_BLOCK, excluded from the 630 with the count on the face; a single-block output is scored on that block and flagged single-point; `calculation` is read per deck and tabulated** (the unsuffixed 2-/4-layer O/OH/OOH jobs may be single points — UNKNOWN until read). The direction clause runs per metal as defined next.

**Definitions.** An adsorbate atom's **locked lateral set** is the set of lateral axes (the cell's two in-plane Cartesian axes) on which its force component is exactly 0.0 in every printed step. An output's lock direction is the intersection over its adsorbate atoms. **Per-metal rule for clause (iii), registered before the parse:** clause (iii) is **scored on the named pair `Eads-4-layers/OH-relax` vs `Eads-4-layers/OOH-relax` per metal** — the job class the 2026-08-15 sample read, so that "≥4 of the 6 blind metals" keeps its meaning; *OH and *OOH are **orthogonal** on a metal when, on that pair, each has a single-axis locked set and the two axes differ (the sampled pattern on Cr/Mn/Ir/Ti: *OH {y}, *OOH {x}); double-locked, unlocked, or same-axis pairs are all "not orthogonal" and each is counted and named. The **full per-output direction map over all 42 *OH/*OOH outputs per metal** (ladder + relax variants) is reported as a descriptive table and is not scored; a metal on which any of its 42 outputs deviates from its scored pair's directions is flagged **MIXED** in that table, with the deviating outputs listed by job. (If the entrant prefers the stricter rule — a metal is orthogonal only if every one of its *OH outputs has the same single-axis locked set {a} and every *OOH output {b} ≠ {a}, otherwise MIXED and not orthogonal — he writes it; one rule is fixed in the text either way.) [ADOPTION NOTE 2026-08-23: the named-pair rule as drafted is the fixed rule; the stricter all-outputs variant was not taken.]

**THRESHOLD (adopted as proposed, 2026-08-23) — P-XU** (round-2 :482, with the denominators above): (i) **≥90 % of the 810** report more than one symmetry operation; (ii) **≥90 % of the 630** carry at least one exactly-zero **lateral** adsorbate force component in the final ionic step; (iii) *OH and *OOH are orthogonal on **≥8 of the 10 metals** under the per-metal rule above. **FALSIFIED** if (i) or (ii) is below 75 %, or if (iii) holds on ≤4 of 10 — in which case the lock as found here is reported as this campaign's own builder behaviour and no field-wide claim is made. **Disclosed at registration:** clauses (i) and (ii) are completions of an already-seen sample (40/40 headers; 12/12 force blocks on 4 metals — A9.0), not predictions; the blind quantities are all 680 ladder outputs and the 90 unsampled 2/4-layer jobs for (i)–(ii), and the direction map on MoO₂, NbO₂, PtO₂, ReO₂, RhO₂ and RuO₂ for (iii) — RuO₂ blind by record, not by availability (A9.0) — so "≥8 of 10" means **≥4 of the 6 blind metals (≥3 of 5 if RuO₂ is counted as seen)**. Lens-4's alternative clause (P-A2: ≥90 % of *O relaxations with both lateral components exactly zero) is **reported as a descriptive row, not scored**. The in-house same-axis *OH/*OOH pattern is reported next to Xu's orthogonal one as a tool-dependence observation (lens-digest :265), not folded into any rate.

### A9.3.3 — Census product 2: span_U(c_M) and span_U(ΔG₂) (P-XU-SPAN)

From the 680-file ladder, at fixed metal, span_U(c_M) = max_U − min_U of c_M = ΔG_OOH − ΔG_OH and span_U(ΔG₂) are **gas-reference-independent** (round-2 :150) — the deposit holds `supporting-data/O2` and zero files matching h2o/h2/gas/molecule/reference over 8,247 paths, and CHE needs G(H₂O) and ½G(H₂) separately, so no η and no floor margin can be reconstructed from it without new jobs. **THRESHOLD (adopted as proposed, 2026-08-23):** **span_U(c_M) > 0.20 eV on ≥5 of the 10 rutiles; FALSIFIED below 3 of 10**; span_U(ΔG₂) reported alongside without a threshold. This **supersedes round-1's P-XU-U** ("η span > 0.15 V on ≥5 of 10; ≥1 metal changes volcano rank by ≥3" — round-1 :185) because η needs the gas references the deposit lacks. **Registered in the same clause:** the frozen `tot_magnetization` (value read per deck) is a **DECLARED modelling choice visible in the deck, not a fourth silent error class**. **Registered separately — THRESHOLD (open at adoption 2026-08-23 — entrant's call; if the jobs never run, that half is DEFERRED as written):** the absolute floor-margin half needs two GBRV molecule jobs (H₂ and H₂O; proposed protocol 12 Å Martyna–Tuckerman box, ecutwfc 40 / ecutrho 500 Ry to match Xu's decks; ~0.2 box-h on the old Vast shape, i.e. of order a few SU on Anvil under A8.6's rates — UNKNOWN exactly until timed; GBRV pseudopotentials are not the SSSP set pinned on Anvil and must be staged and md5-logged as a precondition under A8.5's machine rules); whether they run is the entrant's call — if not, that half is reported **DEFERRED, not fudged**; **if they do run, only the floor-margin column (η − floor, a difference) is reported, and no η for any Xu metal appears anywhere** (A9.5 item 2). Xu's ladder is corroboration only: full relaxations, 33-atom 2-layer slab, 40/500 Ry GBRV vs this campaign's 80/640 SSSP, frozen moment — it supersedes neither A0 nor anything in-house (round-2 :142, :273; round-1 :79).

### A9.3.4 — Census product 3: the Divanis floor population as a δ-curve (P-DIVANIS)

Data facts (round-2 :431, :232, :522): Divanis et al. 10.1039/C9SC05897D; 515 rows / 24 articles; only 38 bare rutile MO₂ from 3 articles (Man 26, Mom 11, Frydendal 1); article 22 = 122 rows (24 %), article 18 = 75; Table SI-1 has exactly four correction rows (H₂O 0; *OH + ½H₂ = 0.35; *O + H₂ = 0.05; ½O₂ + H₂ = −0.29), **no *OOH row**, attributed to ref [25] = Nørskov 2004 (10.1021/jp047349j), not Man 2011; the "+0.40 eV *OOH correction" is ABSENT; ref [19] Tripkovic rows are hollandite α-MnO₂, not rutile. **The ESI (`SC-011-C9SC05897D-s001.pdf`, 3,557,937 bytes, and its text extraction `divanis_esi.txt`, 34,094 bytes) is NOT in the repo** — it sits in the same 2026-08-15 session scratchpad as the Xu artefacts; docs/research/papers/ holds PDFs only. **Registered obligation before deposit — DISCHARGED 2026-08-23:** the ESI PDF (sha256 `348462f7…08d5adc02a`) and its text extraction (`88bfcda9…42c0bd8bda`) are filed under `docs/research/2026-08-15-sampling/`, so "on disk" means a repo path. **THRESHOLD (adopted as proposed, 2026-08-23):** the floor margin is reported as an explicit curve over δ = corr_OOH − 0.35 eV, δ ∈ [0.00, 0.10] eV, with the shift registered now as **Δ(floor margin) = +δ/2 (pls = 3), −3δ/2 (pls = 4), −δ/2 (pls ∈ {1, 2})** — equivalently ∂(floor margin)/∂δ = +1/2, −3/2, −1/2 (round-2 :232 writes the shifts as derivatives; the dimension is fixed here); **prediction: ≥25 % of the rutile-only entries with η < 0.60 V sit within 50 meV of their own exact scaling floor, per-paper rate (n = 24) alongside; FALSIFIED below 10 %**; no exact binomial CI at n = 515; denominator composition on the figure face. **Denominator, fixed before the parse:** the number of rutile-only rows with η < 0.60 V is **UNKNOWN today**; the entrant counts it from `divanis_esi.txt` (a count of a published table already read on 2026-08-15 — not a raw-output corpus under A9.6's no-parse rule; no floor is computed) and writes it into this clause before deposit; if it is not counted before deposit, the denominator defaults to **all 38 rutile-only rows** and the prediction is read as "≥25 % of the 38 have η < 0.60 V and sit within 50 meV." [ADOPTION NOTE 2026-08-23: not counted before deposit; the written default applies — the denominator is all 38 rutile-only rows.] If δ is not resolved from Nørskov 2004 by **Sep 15**, only the δ-curve is reported and no single-δ number is quoted. **Guard:** Man 2011's high-coverage CrO₂ row reconstructs to η = 1.96 V with ΔG₄ = −0.46 eV (ΔG_OOH = 5.38 > 4.92) — unphysical under imposed 4.92; never quoted without that note (round-2 :413). **The Divanis z-score — an amendment to a DEPOSITED clause, entrant's call:** docs/43 §6 :331-337 registers z = (c_M − 3.18)/0.12 **and a gate** ("a correction that moves η by ≥ 0.10 V while leaving |z| ≥ 3 has not fixed the scaling anomaly"), and docs/43 §9 item 2 (:836-841) CONFIRMED 3.18 ± 0.12 eV verbatim from the paper; both are in the deposited A1–A7 record (10.5281/zenodo.21963144); tasks/plan-maximal-rigor.md :87 repeats the gate. Round-2 F8 (:522) and §6 item 7 (:411) demote the pooled ±0.12 eV to qualitative on clustering grounds — 515 rows / 24 articles, article 22 = 24 % of rows, so the 1σ is pseudo-replicated. **ADOPTED as proposed, 2026-08-23 (correction of record — the entrant's decision):** the §6 |z| ≥ 3 gate is **withdrawn as a correction of record**, with that reason, in the entrant's words appended to docs/43 (no edit of the deposited text); the z column is retained as reported; if a gate is wanted, the Divanis rutile-only n = 38 sub-fit replaces the pooled intercept. This is flagged as a change to a deposited registration, not a clarification.

### A9.3.5 — Census product 4: the pymatgen census PAIRED with the atomate input-set audit (P-BUILDER)

**Two numbers, never one product** (round-2 :233, :485). (1) pymatgen `AdsorbateSiteFinder` (10.1038/s41524-017-0017-z), run **unmodified, inside the repo**, over rutile(110) / perovskite(001) / spinel(001) / fcc(111) × {*O, *OH, *OOH}: the fraction of enumerated configurations retaining at least one adsorbate-invariant symmetry operation — **the site-selection mechanism only**. (2) The input-set audit: whether the relaxation stack the field runs those sites through keeps symmetry on. **"The project's own slabs" is true only for rutile(110):** the repo has rutile(110) builders, a rocksalt MO(100) builder (`src/hea_oer/surfaces_oxide.py`) and a randomly decorated HEA fcc(111) slab (`src/hea_oer/surfaces.py`) whose random decoration is P1 by construction and would return "no symmetry" trivially; it has **no perovskite(001) or spinel(001) builder** (grep of `src/` 2026-08-23). **Registered before the blind arms run — THRESHOLD (open at adoption 2026-08-23 — every value the entrant's call, owed in a dated line here before any blind arm runs):** per family, the source structure (MP id or CIF, written here), termination, slab thickness, vacuum, a **pure-metal** fcc(111) element; the enumerator call `AdsorbateSiteFinder(slab).generate_adsorption_structures(mol, repeat=[1,1,1], find_args={"distance": 2.0})`; the adsorbate molecules O; OH (d_OH = 0.98 Å, upright); OOH bent with coordinates as in the retained `t2.py` (`[[0,0,0],[1.29,0,0.7],[1.29,0.9,1.0]]`) or the entrant's choice, written here; the site-symmetry call `SpacegroupAnalyzer(structure, symprec=1e-3)`; and the operational definition — an operation is adsorbate-invariant when it maps every adsorbate atom onto itself mod lattice (distance < 1e-3) and has a −1 eigenvalue, i.e. a force component it forces to zero. Those are exactly the arguments the 2026-08-15 run used (`SlabGenerator(min_slab_size=9., min_vacuum_size=15., center_slab=True, primitive=True)` on a hand-built RuO₂ rutile cell a = 4.4919, c = 3.1066, u = 0.3058), so the rutile arm is reproducible in-repo from them; the four slab files are named by path and sha256 in this section once built. **Denominators:** UNKNOWN today; the entrant runs the enumerator (no symmetry computed) on the four families under exactly these arguments and writes the four configuration counts into this section before deposit. [ADOPTION NOTE 2026-08-23: not supplied at deposit; per this section's own rule the blind arms do not run until the entrant writes them in a dated line here — supplying them before any arm runs completes the registration and is not a post-hoc move.] **THRESHOLD (open at adoption 2026-08-23): rate X per family — X is UNKNOWN and is the entrant's number**; this draft proposes none. **Disclosure:** the rutile(110) arm is **non-blind** — the 2026-08-15 agent ran it outside the repo (clean slab Pmm2, 4 ops; *O and *OH: 9 of 10 configurations retain a mirror, 1 of 10 P1; bent *OOH: 10 of 10 P1; lens-digest :265) and said "that result is MY computation … needs re-running inside the repo"; perovskite(001), spinel(001) and fcc(111) are blind. **The atomate facts are a verification gate, not a fact:** "atomate `MPSurfaceSet` sets `ISYM: 0` under the comment 'Should give better forces for optimization', introduced 25 May 2018, commit a7d5f316; the 2017-era workflow (commit d2742a3b) used pymatgen's `MVLSlabSet`, which does not set ISYM (VASP default ISYM = 2)" exists only in the round-2 synthesis (:233, :409, :432) and is **NOT MEASURED** in this repo. It is cited only after the entrant verifies both commits and the comment in the atomate git history; failing that, the statement narrows to the version inspected on a stated date. The two rates are never multiplied; the exposed population is stated as the papers that do not use those stacks. Montoya & Persson's Methods are still unread — pull through Purdue ILL by Aug 29 (A9.5).

### A9.3.6 — Census product 5: the literature-coding audit, restored (P-LIT)

Restored by the 2026-08-16 addendum (round-2 :579-582; docs/45 :76); only spec is round-1 :138/:187. **THRESHOLD (structure adopted as proposed 2026-08-23; the entrant's values — search string, databases, date window, predicted proportion — owed before the first paper is coded) — inclusion rule:** every rutile-oxide (110) OER screen published 2011–2026 that reports a CHE overpotential, found by a search string, databases and date that are **UNKNOWN today and the entrant's — written into this section before the first paper is coded**; listed before the first paper is coded; **three binary fields:** symmetry setting reported? imaginary-mode check reported? magnetic-state check reported? **Predicted proportion: UNKNOWN — the entrant writes the number**; round-1's example (">80 % report none of the three") is an example, not a proposal. **Disclosure, mirroring A9.3.2's:** in-scope papers whose methods the campaign has already read before any coding — Xu 2015 in full (docs/43 :1294-1298, 2026-08-12), Man 2011 (`docs/research/papers/man2011.pdf`, text extracted 2026-08-15), the Divanis 2020 ESI (A9.3.4), and whatever the 2026-08-15 lit sweeps read (recorded in the two synthesis files) — so the predicted proportion is partly informed and is disclosed as such. **Who codes:** the entrant codes every included paper's fields from the paper itself and owns the inclusion list; AI may execute the registered search string and pre-screen titles/abstracts for inclusion, logged as such; an AI-suggested code is never the recorded value; the coded table carries the coder and date per row. **Deposit-availability count:** proposed as a fourth coded field (raw outputs deposited? yes/no) at zero marginal cost, no threshold — entrant's call whether to carry it; its status after the addendum is otherwise undecided (round-2 :235, :570). [ADOPTION NOTE 2026-08-23: the fourth field is carried as proposed.]

### A9.3.7 — What S2 delivers and unlocks

Deliverable: the census tables plus the paired site-symmetry/input-set result and the coded literature table, **all census numbers computed from raw outputs the entrant parsed himself, and all literature codes entered by him** (round-2 :237). Claim scope unlocked, and no wider: that the symmetry lock is present, rung-dependently, at measured rate r with direction map D in the deposited output of the paper this project cites for its own Hubbard U — i.e. the lock is not peculiar to this campaign's builder — and a dated statement about when the field's canonical framework began disabling symmetry, **if and only if** A9.3.5's verification gate is passed (round-2 :238). S2 is 0–2 DFT jobs, of order a few Anvil SU at most (A9.3.3), none able to fail for compute reasons (:225-228). Total external n ≈ 5,800 for zero box-hours (round-2 :148).

---

## A9.4 — Both outcomes stated before the parse

Round-2 F9 (:526) says the both-outcomes mitigation is "pre-written in Amendment 8." **It is not:** docs/47 A8.2 is a wording obligation with no FALSIFIED branch for P-SYMCOV and no fallback-lead statement (docs/47 :59-73). It is written here, for every S2 prediction, and **the A8 draft is flagged to carry its own P-SYMCOV falsification branch**.

| prediction | claim scope if HELD | claim scope if FALSIFIED |
|---|---|---|
| P-XU | the lock is present in the deposited output of the field's canonical rutile-OER DFT+U study, at rate r on n = 810/630, with direction map D — an external instance, not a self-audit | the lock rate in Xu's outputs is r < 0.75 (or orthogonality ≤4/10): the lock as found here is this campaign's own builder behaviour; reported as such, no field-wide claim; the detector and the completed census still stand as a complete study of a complete corpus |
| P-XU-SPAN | c_M moves by > 0.20 eV across U on k ≥ 5 of 10 deposited rutiles, gas-reference-free, corroborating (not superseding) the in-house U-fragility | fewer than 3 of 10: U-fragility is reported as in-house-only (n = 8, CONTROL not PRECISION); Xu's ladder is reported as not corroborating it |
| P-DIVANIS | a stated fraction of published rutile η < 0.60 V entries sit within 50 meV of their exact floor, as a δ-curve with denominators on the face | below 10 %: the scaling floor is an identity that binds few published entries; reported as the δ-curve only; the floor lemma's in-house use is unaffected |
| P-BUILDER | X per family, mechanism only, next to the verified input-set date; two numbers | low X or failed verification: site selection is not a propagation mechanism, or the date cannot be verified; the rate is reported without the pairing sentence |
| P-LIT | the coded proportion, with inclusion rule and n | the predicted proportion fails: the "invisible to standard checks" sentence is dropped from the report, not defended |

These are scope statements, not wording; the report's sentences are the entrant's and are not these.

**Standing regardless of every row:** the detector, its controls, and the 810-output census — a complete study of a complete corpus (round-2 :508) — and the already-banked zero-compute fallback lead, the floor/excess decomposition (0.223 V of movement in the physical limit under a parameter no convergence gate constrains, ~25× Cr's own 9 meV margin; round-2 :526). **The report must not discover any of this in October.**

**P-DISPOSITION and the six-row cap** (docs/43 A7.7 :1436-1440): any A9 prediction not scored by Oct 15 is WITHDRAWN-UNSCORED with its date. The body-figure ledger holds six rows (five new + P7). **The arithmetic, written so the displacement decision is visible:** rows already claimed or in line — P7 (historical), P-PROJ, P-PLS, P-FLOOR-U (A7, deposited; docs/43 :1325, :1348, :1361), P-SYMCOV (A8 draft, docs/47 A8.2 — docs/47 does not itself say "body row," so its placement is also open), and A10's P-BEEF (round-2 :487-489, pending) — **six: the cap is reached before A9 adds anything.** Round-2 Q6 (:553-554) says the detector plus the exposure census LEADS the abstract, which means P-XU in the body. **THRESHOLD (open at adoption 2026-08-23 — entrant's call, decided once in writing before Sep 20):** P-CTRL is a gate and takes no ledger row; of A9's five predictions, P-XU is proposed for the body ledger and P-XU-SPAN, P-DIVANIS, P-BUILDER, P-LIT for the appendix ledger with the same HELD/TRIGGERED/WITHDRAWN vocabulary; **and the entrant names which already-registered prediction moves to the appendix ledger to make the room, or decides instead that P-XU stays in the appendix and re-tests the headline sentence against that.** [ADOPTION NOTE 2026-08-23: the proposed allocation is adopted — P-CTRL takes no row, P-XU proposed for the body, P-XU-SPAN/P-DIVANIS/P-BUILDER/P-LIT for the appendix; the displacement itself (which registered prediction moves, or P-XU stays in the appendix) remains the entrant's, in writing before Sep 20.]

**The Sep 20 re-test and the one sentence** (round-2 :507-508, :553-554): the central claim must be scorable from S1 + S2 + S6 alone. **AI-drafted candidates exist in the repo** — round-1 :227 gives sentences (a) and (b) with a recommendation, round-2 Q6 (:553-554) registers the ordering **detector + exposure census leads; floor movement second; coverage-conditionality third**, and docs/44 :176-183 carries "The one-sentence story (report framing + interview)" written 2026-08-16 — **what does not exist is the entrant's own claim sentence.** The entrant says whether the docs/44 sentence is the abstract's claim sentence or only the narrative; if the latter, he writes the claim sentence into docs/45 §D as a dated line, and on **Sep 20** redrafts it against only what has landed; if it does not stand, a stage is cut rather than hoped for. "Results to date of an unfinished study" is ineligible (round-2 :507). [ADOPTION NOTE 2026-08-23: open; the entrant's statement on whether the docs/44 sentence is the claim sentence is owed as a dated line in docs/45 §D, and the Sep 20 re-test stands.]

---

## A9.5 — Scope limits on what the census may claim, registered rather than discovered

1. **The Xu repair — entrant's call, both options on the table.** Round-2 :570 cuts it ("never re-runs anyone's decks"); the 2026-08-16 addendum names it in neither list; round-1 :225's three reasons are mixed — one is effort ("unbudgeted" QE 5.x → 7.5 Hubbard translation, `Hubbard_U(i)` → the `HUBBARD` card across an augmentation-charge change for ultrasoft pseudos), one is physics (CrO₂/MnO₂ running at frozen `tot_magnetization`), and one — the ~0.12 V code-to-code floor — round-2 F8 (:522) has since declared dead and it is dropped from any justification here. **(a) Cut on evidence:** frozen moment on the only 3d metals in the set, plus the translation risk; then "never re-run anyone's decks" stands and A9.6 keeps its first bullet. **(b) Round-1 :225's minimum-viable version:** 3 metals, a gate on the three ΔG rungs (|ΔΔG_i| < 0.10 eV) rather than on η, a widened ±0.12 V η gate, 2–3 human-days budgeted for the deck translation, charged to S2 or S6, not S3. The entrant writes which; A9.6's first bullet is kept only under (a). Either way the census's sentence is "the lock is present in their outputs too" and S3's is "here is the corrected number on systems I control" (round-2 :570). [ADOPTION NOTE 2026-08-23: still open — the entrant has not written (a) or (b); until he does, A9.6's first bullet stands in its conditional form and no repair act may begin.]
2. **Rates, differences and an instrument — never absolute overpotentials** for any single material, and never anything about whether Xu's, Divanis's or anyone's conclusions are wrong. **In every sentence about an external corpus the noun is "lock" or "constraint" — never "trap," "bug," "error" or "pathology."** LOCKED means pw.x kept ≥2 operations and symmetrised a component to exactly zero; it counts what the code removed, not what the physics wanted; a locked geometry whose true minimum is symmetric lost nothing (`symops_audit.py` :27-30 already says so). Whether any Xu geometry is a minimum or a saddle is **NOT MEASURED** by this census and no such statement is made. The only sentence about the Xu corpus is: the lock is present in their outputs at rate r with direction map D, under the definitions of A9.3.2. MODEL-PHASE scoping stands: the tier's Cr/Fe/Co/Ni are phases that do not exist as electrodes (round-2 :81, :107) and Mn, the one real ambient magnetic 3d rutile in the tier, is run in an approximate magnetic order (round-2 :550) — so no absolute η for Cr/Fe/Co/Ni as a materials claim, paired within-metal differences only, enforced by the pre-submission PDF parser, and **this goes in the report's scope section, not a limitations footnote** (round-2 :107, :315, :570).
3. **Symmetry-ON corpora yield LOCKED lower bounds only** (A9.2.3). No false-negative rate exists anywhere in this program.
4. **No OC22 symmetry arm.** VASP 6-decimal eV/Å printing makes "exactly zero" a quantisation question; OC20's `isym = 0` does not transfer (round-2 :216, :435; docs/45 :68-70). OC22 symmetry exposure is recorded **NOT MEASURED**.
5. **In-house n buys CONTROL; external n buys PRECISION.** Never in one sentence; never multiply a per-relaxation exposure rate by a per-metal consequence rate; units registered separately — PER-STATE n = 24 with DEFF = 1 + 2·ICC on the figure face, PER-METAL n = 8 with the Clopper–Pearson width (~0.68 near p̂ = 0.5) registered in advance, PER-PAIR n = 7; a per-state rate is never multiplied up into a per-metal rate (round-2 :148, :154-162). External n as registered: Xu 810 (a 95 % interval ~0.07 wide), OC20 ≥500, Xu ladder 170 (metal, U) points, Divanis 515/24/38, pymatgen unlimited enumeration paired, Fahmy arXiv:2509.05909 >7,843 entries **TRANSFERRED, cited not re-analysed**; **Wander & Kitchin 3,963 + 636 CUT on physics, a kill that stands under the addendum** (round-2 :235, :435; docs/45 :68-70): its registered noise floor — "3× the median |ω_imag| of the translational/rotational modes" — does not exist for a fixed-bottom-layer adslab or a partial Hessian, and at OC20's `ediffg = −0.03 eV/Å` the incidence is dominated by residual-force curvature error. Total external n ≈ 5,800 for zero box-hours (round-2 :138-148, :433).
6. **Do not scan / do not fine-tune:** ODAC23/OMol25/OMC25, AFLOW/OQMD/Alexandria/MP Crystalium, Tran's 4,119-oxide screen beyond the floor lemma; no MLIP fine-tuned on Xu or OC20 frames (all candidate frames are locked on the coordinate the trap lives in; Warford, Thiemann & Csányi arXiv:2601.21056 supplies an independent reason); CatHub needs an API key before any arm is planned (round-2 :435-439).
7. **Prior-art framing:** the trap is DEAD as discovery and SURVIVES as a quantified audit — Goniakowski & Gillan, *Surf. Sci.* **350**, 145–158 (**1996**), DOI 10.1016/0039-6028(95)01252-4 (preprint arXiv:mtrl-th/9508009, Aug 1995 — the year correction is docs/43 §9 item 3, :843-850, and is not re-broken here) on TiO₂(110)/SnO₂(110); Sun, Reuter & Scheffler, PRB 70, 235402 (2004), "crucial" on RuO₂(110) — **UNVERIFIED in this repo** (it appears only in tasks/plan-maximal-rigor.md :290 and here) and is cleared or excluded in the F8 Crossref regeneration by Sep 15; the VASP ISYM wiki; OC20/AdsorbML randomise orientation by construction (tasks/plan-maximal-rigor.md :290). The permitted sentence is the narrowed one there; lens 7's framing — known and named for point defects (ShakeNBreak), no equivalent for adsorbate placement in high-throughput catalysis, "absence of evidence, not evidence of absence" — is the novelty statement (round-2 :346). Never "published computational work is unchecked"; never first discovery of DFT screening error; never the aggregate noise scale (round-2 :519-520). The distinction from arXiv:2604.12198 (an AI agent reproducing 111 QE papers) — human-designed instrument, human-set thresholds registered with dates before results existed, human-written detector core, human-written report, and a withdrawal a machine would not have chosen — is made affirmatively in the report body.
8. **Kill criteria that touch S1/S2, with dates:** F1 — S1, S2's Xu census, S6 and S7 are NOT cuttable (round-2 :502); F3 — Sep 20 (A9.4); F4 — P-CTRL voids (A9.2); F7 — Briquet 2017 (10.1002/cctc.201601662), Chatterjee arXiv:2512.05938, Montoya & Persson Methods, Huang arXiv:2604.12198 all in hand by **Aug 29** via Purdue ILL, and anything not in hand has its dependent claim narrowed pre-emptively (round-2 :519-520); F8 — the Divanis +0.40 eV correction (ABSENT), the 3.18 ± 0.12 eV intercept (qualitative), the ~0.12 V code floor (dead), the Sun/Reuter/Scheffler citation (item 7), and the PbO₂/OsO₂/SnO₂/GeO₂/PtO₂ structure-type assignments each cleared or excluded by **Sep 15**, with the bibliography regenerated from Crossref (round-2 :522-523).
9. **Report mechanics A9 must not contradict:** every figure and table carries a citation (a missing figure citation can disqualify); no hyperlinks outside the bibliography; the Zenodo deposit appears only as a bibliography entry; every census figure names its CELL and prints its denominator composition on its face (round-2 :311, :315, :232).

**Open decisions this draft leaves to the entrant, listed once:** the OC20 split name and artefact line, copied from the documentation (A9.2.1); the OC20 CI mechanism, release asset or self-hosted runner (A9.2.3); the noise-floor divisor, /20 as proposed or /10 (A9.1); whether "packaging" is inside AI's permitted list (A9.1); the list of "five existing detectors" and whether any goes into `legacy/` (A9.1); where the four 2026-08-15 artefacts and the Divanis ESI are filed, in git or hashed-out (A9.0, A9.3.4); the Xu-repair disposition, (a) or (b) (A9.5 item 1); the P-XU per-metal rule, named-pair as proposed or all-outputs-agree (A9.3.2); the P-DIVANIS denominator count (A9.3.4); the Divanis z-gate withdrawal as a correction of a deposited clause (A9.3.4); the P-BUILDER structure sources, parameters, denominators and X (A9.3.5); the P-LIT search string, databases, date, predicted proportion and the fourth field (A9.3.6); the six-row allocation and which registered prediction is displaced (A9.4); whether the docs/44 sentence is the claim sentence (A9.4); whether the two molecule jobs run (A9.3.3); and **ownership of the solvation × coverage non-additivity registration** — docs/45 §B row 9 assigns |Δc_M(O cov) − Δc_M(OH cov)| > 0.10 eV (TRANSFERRED; ΔG_OOH swept [−0.4, +0.2] eV, no central value; round-2 :377, :407) to "A8/A9 (owed)"; docs/47 does not carry it and it is not a census item, so it is **not registered here as a census prediction and the A8 author is flagged — with a fallback: if A8 does not carry the §B row 9 registration at its deposit, A9 carries it as an appendix prediction with the TRANSFERRED status and the swept ΔG_OOH band, so that the row is owned by someone.** 

**[ADOPTION STATUS 2026-08-23 — the list above, resolved.** Adopted as proposed: the OC20 split name and artefact line, fixed in place from the documentation by the A9.2.1 note (val_id); the noise-floor /20 rule; "packaging" as defined; the detector-candidate list; the 2026-08-15 artefacts filed in git with the output retained; the P-XU named-pair rule; the P-DIVANIS default denominator (all 38); the Divanis z-gate withdrawal as a correction of record; the six-row allocation as proposed; the fourth P-LIT field; and the solvation × coverage row-9 ownership — A8.2 carries it at A8's deposit, so A9's fallback lapses. Still OPEN, each annotated in place with its owner and deadline: the OC20 CI mechanism (a)/(b); the Xu-repair disposition (a)/(b); the P-BUILDER structures, parameters, counts and X; the P-LIT search string, databases, date and predicted proportion; the six-row displacement and the claim sentence (both Sep 20); and the two molecule jobs.]

---

## A9.6 — What this amendment does NOT license

- It does not license re-running, re-relaxing, or "repairing" any deck from the Xu deposit or any other external corpus — **standing only if the entrant chooses (a) in A9.5 item 1;** under (b) the minimum-viable version is registered there and this bullet narrows to "nothing beyond it."
- It does not license an OC22 symmetry arm, a CatHub arm, or any scan of the corpora listed in A9.5 item 6, nor fine-tuning any MLIP on Xu or OC20 frames.
- It does not license any false-negative statement, any "free"/"searched"/"unconstrained" reading of a not-LOCKED output on a symmetry-ON corpus, or any symmetry claim about a corpus the controls have not certified the reader for.
- It does not license an absolute overpotential for any single material, in-house or external, or any statement that a cited paper's conclusion is wrong, or the nouns "trap," "bug," "error" or "pathology" applied to an external corpus (A9.5 item 2).
- It does not license re-drawing, enlarging selectively, or substituting the OC20 sample after it has been drawn, or moving a per-corpus noise floor after that corpus is parsed. A gate widened until the data fits is the failure mode this project exists to indict.
- It does not license AI authorship of any part of the `silentgate` core as named in A9.1, or any verbatim reuse of this text in the report, essays, or application answers.
- It does not change A8's S3 protocol, reopen any S0 gate, or add in-house n beyond the cap of 8 (+ conditional SnO₂); n = 25 is a physics kill that stays dead (round-2 :570, addendum; docs/45 :68-70).
- It does not license parsing any external corpus — beyond the disclosed 2026-08-15 sampling, which is closed — before the dated DOI line in A9.7 exists. **What is and is not parsing:** reading a dataset index or its documentation, downloading an artefact, listing its contents, or comparing file listings is **not** parsing; reading any force block, header, or deck of an external corpus **is**. Under this amendment nothing external is fetched before the DOI line either, because nothing needs to be; the one cached Xu pair is hashed (A9.0) and is not opened again until then.
- **What S1 may and may not do before the DOI line, stated once:** the entrant may write the core and its tests may run; the in-house positive control and the in-house QE-negative control may run, because `runs/` is on disk and their thresholds (9/9, 0/11, 20-for-20, n/n two-witness) are already the published record; CI may be built against `runs/`. No Xu header, force block or deck, and no OC20 file, is read by `silentgate` or by anyone before the DOI line.

## A9.7 — Deposit obligation

Per A7.8, docs/43 complete through this amendment is re-deposited to Zenodo as a new version of record 10.5281/zenodo.21963144 — restricted access, DOI and timestamp public, files closed until report submission — **before `silentgate` is pointed at any external corpus and before the first S2 table is computed**. The 2026-08-15 sampling is disclosed above and is not repeated before deposit. **The first registered acts after the DOI line, in order:** (1) the Zenodo zip fetched and its listing compared with the hashed mirror listing (A9.3.1) — a listing operation, no content read; (2) the header-format validation on the four named 4-layer files of one metal, taken from the zip (A9.1), outcome logged in a dated line here — the first parse; (3) the OC20 artefact downloaded, its stored force precision recorded in a dated line here, the 500 drawn by the registered rule and their sha256 manifest committed (A9.2.1); (4) the census. **Ordering relative to A8, proposed:** A9 is deposited first and alone if A8 is not ready on the same day, because A9's governed act (the parse) precedes A8's (the first S3 deck, Aug 26) and is already overdue; if both are ready together they go as one version with A8 and A9 in numerical order. [ADOPTION NOTE 2026-08-23: both amendments were ready together and were appended as one version in numerical order (commit 2e61bf0); the second branch of this rule is the one that executed.] The entrant's re-authoring of every THRESHOLD line above is recorded in the commit that appends this text to docs/43. The new version DOI is recorded here in a dated line when it exists.

**DOI line (2026-08-23):** **10.5281/zenodo.22072991** — see the identical dated line at the end of A8.9; one version carries both amendments. Every post-DOI act of A9.7 is now unblocked in its registered order.
**Zip-listing comparison line (2026-08-23, act 1):** `rutile-OER-v1.0.zip` fetched from 10.5281/zenodo.12635 (572,402,421 bytes, md5 `e193c56cf17c6d98827bbb19752d04b3`, matching the Zenodo record's checksum). The zip's single top-level directory is `zhongnanxu-rutile-OER-c4cb892/` — the deposit is the mirror snapshot at the very commit `xu_tree.json` hashed. Comparison per A9.3.1's registered unit: 6,989/6,989 blob paths and sizes identical (0 only-in-zip, 0 only-in-tree, 0 size mismatches); 815/815 `pwscf.out` git-blob SHA-1s recomputed from the zip bytes match the mirror listing. The listings do not differ, so the zip is the population AND every count formerly “per the GitHub mirror at `c4cb892`” is a count of the zip. Report + script: `docs/research/xu-verification-2026-08-23/`. A listing operation; no content parsed (A9.6).
**Header-format validation line (2026-08-23, act 2 — the first parse):** metal chosen RuO₂, the metal already seen by record (A9.0), so P-XU's six blind metals stay unread. The four paths (under `zhongnanxu-rutile-OER-c4cb892/supporting-data/RuO2/Eads-4-layers/` in the zip): `bare/pwscf.out` → `4 Sym. Ops. (no inversion) found` (l.101); `O-relax/pwscf.out` → `4 Sym. Ops. (no inversion) found` (l.99); `OH-relax/pwscf.out` → `2 Sym. Ops. (no inversion) found` (l.110); `OOH-relax/pwscf.out` → `2 Sym. Ops. (no inversion) found` (l.111). Outcome: all four are the count-first form; the older docstring form was not encountered; no reader fix is needed and the both-forms-by-regex rule stands, the form logged per file. Record: `docs/research/xu-verification-2026-08-23/README.md`.
**OC20 artefact / precision / manifest line (2026-08-23, act 3):** `is2res_val_id_trajectories.tar` downloaded (6,296,166,400 bytes; **md5 `fcb71363018fb1e7127db2500e39e11a` — matches the registered value**; CC-BY-4.0). Member count as found: **24,945** `random*.extxyz.xz` xz-compressed extended-XYZ trajectories (the documentation's own note says ~25K / 24,943 systems; the artefact fact is recorded as found). The 500 drawn by the registered rule (first 500 member names, ascending lexical): `docs/research/oc20-val_id/first500.txt`; their sha256 manifest is committed at `docs/research/oc20-val_id/first500.SHA256SUMS`. **Stored force precision, the dated fact: fixed-point decimal text, exactly 8 digits after the point, eV/Å** (extxyz `forces:R:3`; verified on all 141,435 force components of 5 of the 500, draw indices 1/100/250/400/500) — “exactly zero at the stored precision” means the literal token `0.00000000` / `-0.00000000`. Forces are stored raw (nonzero on `move_mask F` atoms), constraint mask and `tags` are in-file columns. Files outside git on Anvil scratch with a durability copy at `$PROJECT/corpora/oc20/` (A9.2.1); no census was run — act 4 waits on the entrant's `silentgate`. Record: `docs/research/oc20-val_id/README.md`.

---

## Dated addendum — 2026-08-30: the gate-(h) AFM scope, resolved

**[AFM-SCOPE RESOLVED 2026-08-30: STANDALONE_FOUR]** — decided by the entrant
2026-08-30 (recorded from his explicit selection in-session; AI-drafted disclosed
infrastructure per A7.7, the decision his, this text the scribe's). This is the dated
line the ADOPTION NOTE at docs/43:1645 says the resolution requires, placed here
because nothing above the deposit line may be edited in place.

**Resolution.** The four 2x1v AFM relaxations owed by A8.5 stand alone as S3-class
jobs: `ref__2x1v__afm__relax`, `s0_O__2x1v_off__afm__relax`, `s0_OH__2x1v_off__afm__relax`,
`s0_OOH__2x1v_off__afm__relax` (decks committed under `runs/s0/h_afm_relax/`, built by
`src/dft/build_h_afm_relax.py` from the banked gate-(h) SCF parents with exactly two
lines changed each). The family is >= 8 decks under the deposited GATE-1 rule
(:311-314): each relaxation gets a fresh-density fixed-geometry `__g1` child, with the
>= 5 meV BASIN_DRIFT re-relax loop and A8.3's 1 meV above-parent refusal.

**A8.1's crossed reading is DEFERRED, not silently dropped.** The magnetic-basin row's
"second seed ... wherever triage allows" is resolved for the AFM Ru family as: the
2x1v/off arm runs now (the four above); the crossing with cell (1x1) and symmetry
(mirror) — up to 12 further relaxations — is deferred with its reason stated: (i) the
crossed family costs ~16,000–30,000 SU against ~4,000–7,600 for the standalone four
(balance 70,851.6 SU, measured 2026-08-30), and competes directly with A0-SPIN Stage 1
and the docs/61-item-10 Ru AFM probe inside the Oct 15 freeze; (ii) no registered
prediction scores an AFM cell- or symmetry-crossing, so the crossed arms would buy
coverage no scorer consumes; (iii) docs/63 §4.3 records that NO version of this family
— crossed included — can bound A7.3's error (it is U = 0 in 2x1v; A7.3 scores the 1x1
grid across U ∈ [0, 9]), so the larger family does not buy the one thing that would
justify its cost. If the crossed arms are wanted later they are a new dated line, not a
reinterpretation of this one.

**What this line licenses:** the four relaxations above and their four GATE-1 children,
S3-class, priced under A8.6. **What it does not license:** any other AFM relaxation, any
AFM deck in 1x1 or mirror, any change to the banked gate-(h) SCFs or their 4/4
ADOPT_AFM verdict, or any A7.3 claim from this family (docs/63 §6).

---

# AMENDMENT 11 — 2026-08-31, adopted by the entrant (directive of record: docs/66), before any A0-SPIN Stage-1 deck is submitted

**Adoption instrument.** This amendment ADOPTS docs/61 (`61-amendment-11-DRAFT.md`,
§A11.0–§A11.11, at the commit that appends this text) as registered text, with the
re-authorings and additions enumerated below. Where this section and docs/61
disagree, this section wins; everywhere else docs/61's drafted sentence is the
registered sentence. The entrant's re-authoring of every THRESHOLD line is recorded
in the commit that appends this text to docs/43 (the A9.7 pattern). Numbering note:
A10 (P-BEEF) remains gated on S0(a) and undrafted; amendment numbering is by
identity, not append order. The election authority for every dated line below is the
entrant's 2026-08-31 directive, quoted verbatim and scoped in docs/66 §1; the entrant
may override any line by a later dated line.

## A11.R1 — The elections (re-authorings of docs/61's PROPOSED values)

**[A11.5 HEADLINE CENSUS 2026-08-31: AS-BUILT 3-of-6]** — the as-built 3 of 6 remains
the registered score of A7.3 and remains the headline; the spin-equalised census is a
registered sensitivity whose only power is to select which caveat sentence is true;
it cannot promote A7.3 to CONFIRMED (docs/61:120-122, adopted as drafted and
recommended).

**[A11.6 SEEDS+SELECTION 2026-08-31: AS PROPOSED, with two dated riders]** — seed set
S = {0.10, 0.30, 0.50}; selection = lowest converged total energy per (metal, state,
U) across the three seeds AND the banked nspin = 1 energy, hard variational floor
("must be ≤ 0" — equality passes; no additional tolerance is introduced), ties within
1 meV to the smallest |seed|; both magnetizations reported. Rider 1: **extension seed
0.05 is pre-named NOW, for the Ir-slab contingency only** (see A11.R3); it is not a
member of S for any other cell. Rider 2: at the (Ti, s0_OOH, u900) cell the banked
null-seed row **−1298.17043625 Ry (totmag 1.04)** is NAMED into the candidate pool as
the free fifth candidate (docs/62:220-222), under the same selection rule. This is
not selection after the fact: the rule is lowest-converged-energy regardless of pool,
so adding a candidate whose value is already banked can only lower, never raise, the
selected minimum; the value entered the record as the A11.7 CONTROL, its three
competitors are unrun, and excluding a known lower converged solution — not
including it — would be the choice this rule exists to forbid. The same sentence
governs the A11.6-ANALOGUE incumbent rows of the Cr/Mn/Fe search.

**[A11.3 THRESHOLD 2026-08-31: 0.026 eV; FALSIFICATION 0.005 eV]** — P-SPIN-DELTA's
movement threshold is |D_M| ≥ 0.026 eV on ≥2 of the licensed metals: the gate-(h)
class re-anchored through c_M (docs/63 §4.2), stated as a LEVEL standing proxy for a
SWING (docs/64 §3's requirement); the relaxed level 0.0325 eV is disclosed alongside
and the original 0.033-with-adsorption-class citation is ineligible (docs/63:176-177).
Falsification band: all licensed metals show |D_M| < 0.005 eV (≈100× the measured
0.052 meV cross-decomposition floor). **Middle band, mapped before the fact:** any
outcome not meeting the ≥2-crossing threshold and not in the falsification band —
i.e., exactly one metal crossing, or zero metals crossing with at least one
|D_M| ≥ 0.005 eV — maps to SCORED — MIDDLE BAND / NOT MET (the A11.R2 vocabulary),
never to either registered column. **Denominator rule:** "of the licensed metals" means metals whose equalised
rows are licensed and not withdrawn (3 with Ti licensed; if Ti's rows had been
withdrawn: ≥2 of 2 for the threshold, both-of-2 for falsification — the confirmation
bar never falls under a withdrawal).

**[A11.4 RE-WORDED 2026-08-31]** — the P-SPIN-DELTA row of the both-outcomes table now
reads: HELD → "the spin convention is worth ≥26 meV of U-dependent movement in c_M
(|D_M| ≥ 0.026 eV) on ≥2 licensed metals; every A0 span on an nspin = 1 metal is
spin-treatment-conditional at that size, and the caveat quotes it." FALSIFIED → "the
spin convention's U-dependent movement is |D_M| < 5 meV on every licensed metal — the
SWING is bounded, not any endpoint level — so the 3/3 split is not a spin artifact
at the swing scale, and the confound, while real as a correlation, carries no
measured U-dependent consequence for A7.3." (The drafted FALSIFIED cell's "worth
<5 meV on c_M at both endpoints" was licensable-false — a swing criterion cannot
license an endpoint-level sentence.)

**[A11.7 NULL-SEED RE-REGISTRATION 2026-08-31: AUTHORISED]** — docs/62 §5.2's
replacement is authorised as drafted: (a) the index-rule leg PASSES as run; (b) the
stability leg is reported, not scored — Ti s0_OOH at U = 9.0: BREAKS, ≥153.07 meV,
SPIN-UNSTABLE. Numeric tolerance for the leg-(a) reproduction: within ≤25× conv_thr
with absmag ≈ 0, as measured on the even-electron control. The criterion as
originally drafted is UNSATISFIABLE on an odd-electron state whose unpolarised
solution is unstable (docs/62:139-141) — declining would have deadlocked scoring, not
preserved it.

## A11.R2 — The middle band and the denominator (A7.3 scoring instruments)

**[A7.7 MIDDLE-BAND DISPOSITION 2026-08-31]** — a count strictly between the
FALSIFIED bound and the CONFIRMED threshold of the operative denominator row (table
below) is **SCORED — MIDDLE BAND / NOT MET**: a registered prediction that failed to
reach its registered threshold. It is reported with its count and the banked
a7_3.conditionality attached and is never quoted bare; it licenses no registered
consequence; it is neither HELD, nor TRIGGERED, nor WITHDRAWN-UNSCORED. This line
SUPPLEMENTS A7.7's ledger vocabulary for the middle band only, in the old census and
the new one alike.

**[A7.3 DENOMINATOR RULE 2026-08-31: TABLE]**

| denominator (metals with a converged *OOH geometry, licensed and not withdrawn) | CONFIRMED | MIDDLE BAND (disposition above) | FALSIFIED (licenses the registered U-invariant-denominator reframe) |
|---|---|---|---|
| 6 (Ti rows licensed under docs/59 §3c) | ≥4 of 6 exceed 0.10 V | 2–3 of 6 | ≤1 of 6 |
| 5 (Ti rows WITHDRAWN-UNSCORED) | ≥4 of 5 exceed 0.10 V | 2–3 of 5 | ≤1 of 5 |

Rules fixed with the table: (i) the CONFIRMED threshold never falls under a
withdrawal (4/5 = 0.80 ≥ 4/6 ≈ 0.667); (ii) the FALSIFIED bound stays the registered
absolute ≤1; (iii) the denominator is set solely by the docs/59 §3c
countersignature, never by this table; (iv) any denominator not enumerated here
requires a new dated line BEFORE scoring; (v) disclosure written with the table: at
either denominator the census when this line was written (3 over: Cr, Mn, Fe) lies
in the MIDDLE BAND, so no choice available in this table can flip a verdict between
CONFIRMED and FALSIFIED — checkable from the banked artifact.

## A11.R3 — Licensed compute additions (each its own dated line; every count exact)

**[IR-SLAB CONTINGENCY 2026-08-31: EXTENDED-SEEDS(0.05) THEN
EQUALISED-BY-SELECTION(nspin=1)]** — if none of {0.10, 0.30, 0.50} lands at or below
the banked nspin = 1 Ir slab energy, stage A runs the pre-named extension seed 0.05
(the Ir slab cells only, u000 + u900 = 2 SCFs); if that also lands above, the (Ir,
slab, U) cell resolves BY THE SELECTION RULE — the banked nspin = 1 energy is in the
candidate set (A11.6) and the floor passes equality — so the equalised row EXISTS,
equals the banked nspin = 1 row, and is reported as EQUALISED-BY-SELECTION(nspin=1)
with the full rejection record. §A11.6's candidate-set reading is adopted over
docs/62:109-110's "no row" sentence; STATED-OMISSION survives only as fallback
wording if a later dated line adopts the stricter reading. State at writing,
disclosed: the u000 seed-0.50 attempt is already banked REJECT (+0.583 meV,
docs/62 §4, called in advance from P11); the other five attempts are unrun. The
resolution is fixed now, before any of them exists, and
EQUALISED-BY-SELECTION(nspin=1) is the conservative branch — it reports zero
spin-polarisation effect on the Ir slab and can manufacture none.

**[CR/MN/FE SEED SEARCH 2026-08-31: RUNS]** — exactly 28 SCFs (Cr 12: banked seed 0.6
is off-grid in every cell; Mn 8: banked 0.5 = m050 covers all four cells; Fe 8:
banked s0_OH 0.5 and s0_OOH 0.1 cover four cells). Coverage convention, registered:
a banked seed equal to a grid member covers that cell AT BOTH ENDPOINTS (banked u900
seeds verified identical to u000). FM-uniform-seed only — this family never touches
the A7.5 Mn AFM condition (the registered either/or at :1406-1407 is untouched by
it). Selection: the A11.6-ANALOGUE rule — lowest converged total energy per (metal,
state, U) across the grid seeds AND the banked FM row as incumbent (these metals
have no nspin = 1 floor; the banked FM energy is the incumbent candidate), ties
within 1 meV to the smallest |seed|. Winners enter the a7_3_spin sensitivity census
ONLY; no banked A0 row is replaced (§A11.9).

**[A7.2 EQUALISED RE-READ 2026-08-31: RE-READ]** — per §A11.9, the equalised rows
read for A7.3 have A7.2 re-read on the same rows. Scope: Ru/Ir now — which requires
**Family C, 20 SCFs**: {slab, s0_O} × {u000, u900} × {0.10, 0.30, 0.50} × {Ru, Ir}
minus the 4 already-run Stage-0 u000-seed-0.50 rungs (three banked; the Ir slab rung
is the registered REJECT, its energy recorded in the rejection record — a family
docs/65's 76-SCF tally omitted; priced here); Ti under the §3c grant (+12: {slab, s0_O} × {u000, u900} ×
3 seeds, docs/62:217-218). Limitation stated before the fact: an endpoint-only
re-read detects pls(0) ≠ pls(9) but CANNOT locate the crossing U — the registered
flip-U crossing deliverable (docs/43:1352-1353) needs the interior ladder, which is a
registered phase-2 decision point (docs/66 §6), not licensed here.

**[RU AFM PROBE 2026-08-31: RUNS, both U endpoints]** — item 10's probe runs as
drafted: the 4 pre-staged NM-relaxed-geometry decks (`runs/s0/h_afm_probe/`), whose
DERIVED enumeration and NM-relaxed geometry choice the entrant countersigns with
this line; recorded either way, not entering the A7.3 score. **Robustness arm, its
own line:** +6 SCFs on the AFM-relaxed geometries (`runs/s0/h_afm_relax` finals): NM
u000 (2), AFM u900 (2), NM u900 (2); the AFM u000 legs are the banked `__g1`
fresh-density children (relaxed-AFM-vs-NM-relaxed Δc_M(0) = −32.12 meV via the g1
children, −32.51 via the relax finals; the fixed-AFM-geometry Δc_M(0) is what the
arm's NM u000 legs will complete; the g1 children are the elected legs, pre-stated
here before any U = 9 result exists). The robustness arm inherits item 10's
no-A7.3-score limit verbatim. nk pre-stated: 4 (the h_afm_anchor runner note), for
both arms. Citation correction of record: the manifest's "−41.4 meV
(docs/figs/a0main_readout.json)" is a DERIVED sum (−25.9 banked dc_M(0) − 15.5 floor
distance); of these quantities the JSON stores only delta_to_floor_eV =
0.015503671954502363 (0.0155 rounded); neither −41.4 nor −25.9 appears in it.

**[MN AFM ARM 2026-08-31: IN SCOPE]** — design of record docs/67 (adopted with this
line); this line IS the arm's licence (docs/43:2008 excludes any AFM deck in 1×1
from the gate-(h) licence, so nothing prior covers it). Staged program and triggers
per docs/67 §5: MN-AFM-ORDER 4 (licensed now) → MN-AFM-CORE 12 (on the measured
ordering winner) → MN-AFM-RELAX 4+4 (GATE-1) → contingent MN-KBRIDGE 4 /
MN-AFM-PROD-2X1 4 (+8 in-frame E4 FM twins if P-B wins). Protocol thresholds reused from gate-(h) verbatim (±20 meV,
frozen u390 FM comparator, M_abs witness), fixed before any AFM energy exists.
Firewalled from A7.2/A7.3. The strike on materials-facing Mn sentences lifts only by
this arm RUNNING, on any outcome.

**[LEDGER PLACEMENT 2026-08-31]** — this amendment is numbered A11; P-FLOOR-U-SPIN
and P-SPIN-DELTA take APPENDIX ledger rows with the same HELD/TRIGGERED/WITHDRAWN
vocabulary and the P-DISPOSITION sweep; the body-figure ledger stays at the
registered six (P7, P-PROJ, P-PLS, P-FLOOR-U, P-SYMCOV, P-BEEF). The docs/52 row 63
displacement decision remains open and owed in writing before Sep 20.

**[DOCS/60 §6 FACT 2 RESTATED 2026-08-31]** — the sentence of record is now: "Ru's
A7.3 shortfall is 15.5 meV of required additional swing in |Δc_M| across U = 0 → 9 —
a change in D_M = Δc_M(U_max) − Δc_M(0). The AFM re-anchor numbers (−25.9 meV
fixed-geometry, −32.5 meV relaxed) are levels of Δc_M at U = 0 only; by the A11.1
arithmetic (Δ[span/2] = −D_M/2) a U-independent level cancels exactly at any size,
so neither level bounds, closes, or widens the 15.5 meV. What the levels establish
is that the NM-vs-AFM class is real on exactly the nearest metal at a magnitude
comparable to the shortfall, while its U-dependence is unmeasured. 'NOT MET is not
settled' therefore stands — on the unmeasured U-dependence, not on 25.9 > 15.5 —
pending the item-10 probe, the only measurement that acts on A7.3." The original
sentence's 2–4× comparison and the 33–64 meV class do not travel; conclusion
unchanged (docs/63:230); this supersedes docs/63 §6's "exceeds … so not settled"
phrasing on the same point (dated row in the error ledger).

## A11.R4 — Scale disclosure (A6.6, running total)

A6.6 registered "~160 fixed-geometry SCFs and zero relaxations"; docs/59 disclosed
the running total at ~250 (and the seven 1×1 Ti relaxations, licensed by the §3c
line of 2026-08-31). This amendment adds, all fixed-geometry SCFs: Ru/Ir Stage-1 20
+ Ti Stage-1 12 + Family C 20 + Ti re-read 12 + Cr/Mn/Fe 28 + probe 4 + robustness 6
= 102, plus Mn stage-1 4 (docs/67; its later families on their own triggers), plus
contingents (Ir-slab 0.05: 2; Mn core 12, k-bridge 4, prod-2×1 4 — up to 12 with the
E4 FM twins if P-B wins — and the relax family's 4 `__g1` SCF children, per docs/67
§5). Running fixed-geometry total: **~250 → ~356 licensed now, up to ~395 at full
contingent trigger** — stated, not absorbed; the same disclosure stance as docs/59
§3c. Relaxations beyond the seven and the gate-(h) STANDALONE_FOUR family (licensed
2026-08-30, run and banked) remain unlicensed except the MN-AFM-RELAX family under
its docs/67 trigger.

## A11.R5 — Deposit obligation

Per A7.8, docs/43 complete through this amendment (A1–A9 + A11 + both dated addenda;
A10 pending, gated on S0(a)) is re-deposited to Zenodo as a new version of record
10.5281/zenodo.21963144 — restricted access, DOI and timestamp public, files closed
until report submission — **before any deck this amendment licenses is submitted**
(vehicle: OWN VERSION NOW, elected in docs/66 §2 row 18; the new version drafts off
the latest published version id 22072991). The deposit fileset: docs/43 (this
state), docs/59 (countersigned), docs/61 (the adopted draft, historical), docs/62–67.
Contingent lines above (Ir-slab 0.05; the docs/67 §5 contingent families — core,
relax, k-bridge, prod-2×1; the phase-2 decision
points of docs/66 §6) ride THIS deposit, so their later triggering needs no new
version. The new-version DOI is recorded here in a dated line when it exists, with
the per-file manifest (name, bytes, md5, sha256, commit).

**DOI line (2026-08-31):** **10.5281/zenodo.22213117** — docs/43 complete through
this amendment (A1–A9 + A11 + both dated addenda; A10 pending, gated on S0(a))
published 2026-08-31 as a new version of concept record 10.5281/zenodo.21963143,
restricted access (DOI + timestamp public, files closed until report submission).
Fileset: 9 files — this document as `43-prereg-week1-factorial-A1-A11.md`
(212,852 bytes, md5 `b16aa3b9639bbae505ab524feb42b1d4`) plus docs/59
(countersigned), docs/61 (adopted draft, historical), and docs/62–67 — each the
working-tree serialization of commit `6fe167b`, per-file bytes/md5/sha256 in the
committed manifest `docs/deposits/2026-08-31-A11.manifest.txt`, and every
uploaded md5 verified against the published record. The deposit obligation of
A11.R5 is discharged; every deck this amendment licenses may now be submitted in
the A11.R5 ordering (the Ti manifests additionally carried the docs/59 §5
confirmation gate, discharged by the entrant's dated line there the same day).
Text added after publication; the deposited files are the frozen artifacts.

---

## Dated addendum — 2026-08-31: P-DISPOSITION date, amended

**[P-DISPOSITION DATE AMENDED 2026-08-31: OCT 15 → REPORT LOCK, BACKSTOP NOV 5 2026
8:00 PM ET]** — decided by the entrant 2026-08-31, recorded from his directive
verbatim: "Freeze is not Oct 15. We go until we cant anymore. Verify the oens that
are the most rigorous and most compute / better for STS 2027 application. If it is
not the most rigorous, amend so it is. remember, we are trying to be impactful and
most rigor". (AI-drafted disclosed infrastructure per A7.7, the decision his, this
text the scribe's; placed here because corrections go in a dated addendum at the
bottom — :4-5 — and nothing above the deposit line may be edited in place.)

**Resolution.** A7.7 P-DISPOSITION (:1437-1440) is amended in its date only: "Oct 15"
now reads "**the entrant's dated REPORT LOCK line — the dated line, written in this
addendum's style, that declares the report's data complete — and in no case later
than Nov 5 2026 8:00 pm ET (the STS 2027 submission deadline)**". The FIRST REPORT
LOCK line governs; it is irrevocable — the docs/66 override right does not reach
it — a second such line is void, and the line takes effect only when committed, its
commit hash recorded beside it. The rule stays
self-executing: if no REPORT LOCK line exists when the backstop instant arrives, the
sweep executes AT the backstop, automatically, exactly as the original rule executed
by date. The disposition sweep executes exactly once, at whichever instant governs:
any prediction not scored when it executes is marked WITHDRAWN-UNSCORED with its
date, exactly as registered. The same date substitution reads through every
registered restatement of the P-DISPOSITION date — :1930's A9 sweep clause ("any A9
prediction not scored by Oct 15") and :1999's scheduling reference — which restate
A7.7's rule and carry no independent date; the Sep 20 displacement decision at
:1930 and A10's Sep 18 are dates of other rules and stay unchanged. Nothing else
moves — no threshold, scoring rule,
sample, consequence, or other registered date (A10's Sep 18; the Sep 20 displacement
decision at :1930 — both independent and unchanged); the S7 window (docs/45:81)
re-keys to end at the amended date by a dated row in docs/45.

**Prospectivity and state at amendment.** No banked verdict depends on the old date:
the banked A0 artifact reads "whatever stays unscored at freeze" with no literal
date (docs/figs/a0main_readout.json; src/dft/a0main_readout.py), and no prediction
has been marked WITHDRAWN-UNSCORED under the Oct 15 rule — every use in the record
is conditional/prospective. Ledger state when this line was written: A7.2 CONFIRMED
5/6; A7.3 at 3-of-6 middle band with Ru +15.5 meV from the floor and the item-10
probe undecided — the 3-over/3-under split coincides exactly with the
nspin=2/nspin=1 partition (the confound the equalised census instruments). The
extension is uniform over every unscored prediction and both outcome directions —
more time to fail as well as to pass — and the pre-extension census stands banked.
No compute this session licenses can move any banked verdict: the equalised census
cannot promote A7.3 (A11.5), no banked A0 row is replaced (§A11.9), and the item-10
probe is firewalled from the score — so the extension cannot act on the 15.5 meV
margin it discloses. This is a date amendment, not a gate widening (A9.6's :1960
indicts thresholds moved to fit data; this moves a calendar, before it arrives,
uniformly, with every threshold untouched).

**What the original date bought, disclosed.** The Oct 15 date served a writing
window — "results must be complete, not proposed; hold the mid-October freeze so
there's ~3 weeks left for Frank to write" (docs/44:129-130). The amendment
transfers that scheduling risk to the entrant knowingly: compute may now run into
the writing window, and the REPORT LOCK line is his instrument for closing it.

**Deposit.** Per A7.8 this addendum deposits with the next Zenodo version (the A11.R5
deposit) and in any case before any job or scoring act dated after Oct 15 relies on
it. **Report discloses:** the original date, this amendment's date + DOI, the ledger
state above, the uniform-extension fact, the writing-window rationale, and the
AI-use log entry (paraphrased per A7.7).

## A11.R6 — Rung ladder for the sixteen unconverged Ru U = 9 spin rows (2026-09-02)

**[RU U9 SPIN RUNG LADDER 2026-09-02: LICENSED]** — on the entrant's directive of
2026-09-02, verbatim: *"Lets go ahead with B. Does it also widen the candidate pool? Wait
for D2 until after D1."* Context: docs/68 §2 and §8 (0 of 16 spin-polarised Ru SCFs converge
at U = 9 under the registered numerics) and the D1 elaboration put to the entrant the same
day (docs/68 §10). This line is written before any rung deck exists.

*Trigger and scope.* Exactly the sixteen rows that hit `electron_maxstep = 200` at U = 9.0:
the twelve nspin = 2 rows `runs/a0/spin/Ru/{slab,s0_O,s0_OH,s0_OOH}__u900__sp2m{010,030,050}`
and the four AFM 2×1v rows `runs/s0/h_afm_probe/{s0_OH,s0_OOH}__2x1v_off__afm__u900` and
`runs/s0/h_afm_robust/{s0_OH,s0_OOH}__2x1v_off__afm__afmgeo__u900`. No converged row is
re-run. No other metal, state, U, seed or cell gains a row.

*The ladder — both rungs pre-named now; nothing may follow it.*
- **Rung 1 = A6.5(2)(ii) literally:** `mixing_beta` 0.3 → 0.15 and `electron_maxstep`
  200 → 400; every other byte of the deck identical to its rung-0 parent (which already
  carries `mixing_mode = 'local-TF'`, `mixing_ndim` at the default 8, `conv_thr = 1.0d-6`).
  Stem and prefix gain the suffix `__rung1`.
- **Rung 2, only on rows rung 1 leaves unconverged:** `mixing_beta` 0.075, `mixing_ndim` 16,
  `electron_maxstep` 600, suffix `__rung2`, otherwise identical to the rung-0 parent.
- A row unconverged after rung 2 is NOT_CONVERGED under A6.5(2)(iii): recorded, never
  interpolated, and its cell stays EQUALISED-BY-SELECTION(nspin=1). `startingpot` and
  `startingwfc` remain forbidden on every spin deck (build_a0spin A10), so rung (i) has no
  spin-arm form.

*Interpretation, fixed before any rung runs.*
(a) Still unconverged after the ladder → docs/68 §2's sentence hardens to "at β = 0.3, 0.15
and 0.075 with local-TF mixing"; nothing else changes.
(b) Converged but above the banked nspin = 1 energy → REJECT-FLOOR under guard 2; the cell is
unchanged; the rejection is recorded with the candidate's moment.
(c) Converged at or below the floor → enters that (Ru, state, u900) cell's pool as a **rung
candidate** under A11.6 unchanged: lowest converged energy across the pool AND the incumbent;
ties within 1 meV to the smallest |seed|, residual ties to the lowest rung; guards 1 (k-set /
symmetry) and 3 (branch) apply as written. A rung-converged magnetic U = 9 winner may make the
Ru endpoint pair same-branch; that is REPORTED by the census and adjudicated only by the
entrant's D2 line, which the entrant has HELD until this ladder returns.

*Pool widening — the entrant's question, answered.* The candidate pool widens ONLY inside the
twelve (Ru, state, u900) cells, by at most one rung candidate per row per rung, and only for
candidates that converge. The seed set S, the incumbents, every other cell, the as-built
census and the headline are untouched (A11.5, A11.9). The four AFM 2×1v rows never enter the
a7_3_spin census: they feed the S0(h) family's readout (docs/63) with the U = 9 level that
docs/63 §6 calls unmeasured.

*Census.* The a7_3_spin readout is extended to parse `__rung[12]` stems, to verify each rung
deck against this table (β, ndim, maxstep, byte-identity elsewhere, same seed and species
index as its parent) and to refuse a rung stem in any cell outside the twelve — committed
BEFORE any rung deck runs (commit hash recorded in docs/68 §10).

*Cost and disclosure.* ≤ 16 + 16 fixed-geometry SCFs; measured band ≈ 1,100–4,400 SU.
A11.R4 running total: ~356 → ~372 licensed now, ~388 at full rung-2 trigger.

**[MN AFM ARM STAGE 1 COUNTERSIGNED 2026-09-02]** → docs/67 §7's dated line. Measured null,
FM stands; MN-AFM-CORE does not trigger; no further Mn family in A11.R4's contingents will run.

**[D2 GUARD-3 ADJUDICATION 2026-09-02: HELD]** — by the entrant's directive ("Wait for D2
until after D1"); the four flags of docs/68 §8 stand un-adjudicated until A11.R6 returns.

## A11.R7 — A5.1(a)'s valence tracker on the A0 grid, via the already-banked Löwdin populations (2026-09-03)

**[A0 LÖWDIN VALENCE TRACKER 2026-09-03: REGISTERED — COUNTERSIGNED 2026-09-03, see Item 2 of the dated addenda at the end of this file]** — written
before a single Löwdin number has been read out of the A0 bank. Nothing below was chosen after
seeing a value of the predictor it registers. The commit that carries this section contains **no
readout script and no result**; the script and its output land in a later commit, and the two
hashes are the proof of order.

### Why this exists, and why it is not a new claim

A5.1(a) already registers exactly this analysis: *"Every existing (metal × adsorbate × U) output is
post-processed for the active-site **local magnetic moment vs the bare slab** … as the primary
valence tracker, supplemented by **Löwdin populations from projwfc.x** where charge densities are
regenerated … budget ≤ ~150 cheap SCFs if the full A0 grid is covered"* (docs/43:946-952).

Two things have changed since that was written, both matters of fact:

1. **The regeneration SCFs were already spent.** The A0 main grid carries **235 banked
   `<job>.lowdin.txt` artifacts** alongside their decks — Cr 76, Mn 32, Fe 35, Ti 28, Ru 32, Ir 32 —
   produced by the projwfc.x runs that the A0 campaign paid for. The supplement A5.1(a) priced at
   ≤ 150 SCFs is **already on disk at zero marginal cost**.
2. **The primary tracker does not exist for half the grid.** The A0 main decks for **Ti, Ru and Ir
   carry no `nspin` card at all** (0 of 28, 0 of 32, 0 of 32 — verified by grep across the decks),
   so pw.x prints no moment for them. The sphere-integrated moment A5.1(a) makes primary is
   **identically unavailable** on those three metals.

And those three metals are exactly the A7.3 under-the-floor set. **The banked Löwdin grid is the
only measured valence quantity in this campaign that exists on both sides of the nspin = 2 /
nspin = 1 partition** — the partition with which A7.3's 3-over / 3-under split is perfectly
confounded (docs/60, docs/63). It cannot un-confound that split. It can test whether the mechanism
A5.1(a) posits survives contact with the metals the moment tracker cannot see.

This section registers the numeric criterion A5.1(a) left unstated for the Löwdin leg. The 0.5 μ_B
threshold A5.1(a) fixes is a **moment** criterion (`lit1_urobustness.py:95-111`) and does not
transfer to a Löwdin charge; nothing below reuses it.

**Already delivered, and not re-opened:** A5.1 items (a), (c) and (d) are implemented in
`src/dft/lit1_urobustness.py` and scored for **tranche 1** — the P7 fixed-geometry U-ladders for
**Cr and Co**, 4 U points each — and banked at `docs/research/lit1_tranche1_uladder.json` and
`docs/research/2026-08-12-lit1-tranche1-uladder.md`, which states in its own scope section that
"Löwdin populations (projwfc.x) are **not in this tranche**". A11.R7 extends the same registered
item to the A0 grid with the tracker tranche 1 could not use. Tranche 1's numbers are untouched.

### Scope — fixed here, drift-proof by construction

Exactly the banked `runs/a0/main/<M>/<state>__<utok>.lowdin.txt` artifacts for
M ∈ {Cr, Mn, Fe, Ti, Ru, Ir}, state ∈ {slab, s0_OH, s0_O, s0_OOH}, and **U tokens matching
`^u\d{3}$`** — the production ladder. Every file the rule excludes (Fe's `pilot530_m*`, `r1`, `r2b`
seed-study rows are the known cases) is **named individually in the readout's census with its
reason**; a file excluded silently is a failure of the readout, not a scope decision. Zero new DFT.
No deck is re-run. No banked energy is recomputed.

### The tracked quantity

For metal M, state s, U point u:

- **Active site A(M).** The metal atom index nearest the adsorbate's binding oxygen, determined
  **once** from the `s0_OH__u000` deck's `ATOMIC_POSITIONS` (minimum-image distance), and used
  unchanged for every state and every U of that metal. The A0 decks list the six metal atoms first
  and append adsorbate atoms last, so the index is stable across states; the readout **asserts**
  this rather than assuming it.
- **q_d(M, s, u)** = the Löwdin **d-channel** charge on atom A(M): the single `d =` value for an
  nspin = 1 file, and **spin-up d + spin-down d** for an nspin = 2 file.
- **Δq_d(M, s, u) = q_d(M, s, u) − q_d(M, slab, u)** — the adsorbate-induced d-occupancy change at
  the active site, referenced to the bare slab **at the same U**. This is A5.1(a)'s construction
  with Löwdin d in place of the sphere moment.

### The predictor — evaluated at U = 0 only, and why

All predictors are read at **u000**: the one point common to all six metals, free of the Hubbard
parameter, and **outside the U-span it is used to predict** (evaluating the predictor inside its own
response would be circular). Per metal:

- step-level: δq₁ = Δq_d(\*OH), δq₂ = Δq_d(\*O) − Δq_d(\*OH), δq₃ = Δq_d(\*OOH) − Δq_d(\*O);
- on the A7.3 quantity: **δq_c(M) = Δq_d(\*OOH, u000) − Δq_d(\*OH, u000)**, the Löwdin analogue of
  c_M = ΔG_OOH − ΔG_OH.

### The response — banked, not recomputed

span_U(ΔG_i) per (metal, step) and span_U(c_M) per metal, over that metal's production ladder,
computed by **importing** `src/dft/a0main_readout.py`'s existing per-U ΔG rows. `g_max`,
`delta_G`, `oer_overpotential` and the QC gate are imported, never reimplemented — the tranche-1
rule. span_U is invariant to any U-independent offset, so the gas references cannot enter it.

### Registered predictions

- **R7-P1 (primary; n = 18 (metal, step) pairs).** Spearman ρ between |δq_i| and span_U(ΔG_i).
  **CORROBORATED** iff ρ ≥ +0.50 **and** two-sided permutation p < 0.05; **REFUTED** iff ρ ≤ 0;
  **INCONCLUSIVE** in between. The three steps of one metal share that metal's slab reference and
  are not independent; the p-value is therefore reported as **nominal**, with the by-metal
  leave-one-metal-out range of ρ printed beside it. Registered now, so that range cannot be
  presented as a robustness check chosen after the fact.
- **R7-P2 (the A7.3 quantity; n = 6).** Spearman ρ between |δq_c(M)| and span_U(c_M), reported with
  its exact permutation p. **No threshold, and not scoreable as pass/fail** — at n = 6 the smallest
  attainable two-sided p is 1/360 ≈ 0.0028 and a single metal moves ρ by ~0.3. Registered as
  *reported, never scored*, so it cannot be promoted to a result later.
- **R7-P3 (the falsification that earns this its place).** A7.3's 3-over / 3-under split is
  perfectly confounded with nspin = 2 / nspin = 1. Registered question: do the six |δq_c(M)| values
  place the three A7.3-over metals on one side of the three under? **A separation proves nothing** —
  no 3-vs-3 comparison can break a perfect confound, and this line says so in advance. **A failure
  to separate falsifies** the claim that the A7.3 split is a valence-change effect, and that
  falsification is the deliverable. Reported as six numbers and two group ranges; no p-value, no
  threshold, no rescue.

### Stability witness, and the flag it can raise

Mirroring A5.1(a)'s supplementary check: for each metal, **range_U(Δq_d)** across the production
ladder, per state. If a metal's range_U(Δq_d) for either \*OH or \*OOH **exceeds |δq_c(M)| itself**,
the tracker is **UNSTABLE across U** for that metal — an SCF-solution change somewhere on the
ladder — and that metal's row is **flagged and excluded from R7-P1 and R7-P2**, with the exclusion
named and the metal reported separately. Fixed now, before any range is known.

### Self-checks the readout must pass, or it reports nothing

1. Every artifact passes `python src/dft/extract_lowdin.py --check`.
2. For every parsed atom, the printed `total charge` equals s + p + d to within **1e-3 e**.
3. For every nspin = 2 atom, spin-up d + spin-down d equals the total d to within **1e-3 e**.
4. A(M) resolves to the same integer for all four states of a metal, and to a **metal** species.
5. The census prints realized counts per metal and names every excluded file with its reason.

A failure of any check is fatal: the readout exits non-zero and publishes nothing. The parser is
written fresh rather than reaching into `extract_lowdin.py`'s private validators, and check 2 is
what makes that safe — the file's own printed total is an independent witness of the parse.

### What this may not do

It moves **no banked verdict**. The A7.2 and A7.3 census, the as-built headline (A11.5), the
selection rule (A11.6), tier_v2 and every ΔG stand exactly as they are. R7 is a **mechanism
readout reported alongside them**, and an outcome favourable to the campaign cannot convert a
failed registered prediction into a passed one. In particular: **A7.3 remains NOT MET at 3 of 6
whatever R7 returns.**

### Cost

**0 SU. Zero new DFT.** The compute this analysis needs was spent by the A0 campaign and is sitting
on disk.

### Countersignature

Owed from the entrant, as with every dated line. If he declines it, the readout and its output are
withdrawn from the report and this section stands as the record of what was registered and not
used.

## Dated disclosure — 2026-09-03: §7's prediction 3 rested on a premise this project had already refuted three days before the deposit

**This is a disclosure, not a revision.** §7 closes with "Nothing in this section may be revised
after the deposit", and nothing in it is revised here. Prediction 3 stands exactly as written and
as deposited. What follows records what was already known at deposit time and what the prediction
can therefore still score.

### The premise, and the refutation that preceded it

§7 prediction 3 registers, verbatim: *"MACE-MPA-0 trains on MPtrj at exactly the Materials Project
U set, with U = 0 on Ru and Ir — the identical partition this campaign uses. Its current agreement
is therefore partly a shared Hubbard convention rather than shared physics. **`omat` is trained on
OMat24, which does not share that convention.** So if `tier_v3` adopts a DFPT U, **Δρ(MACE) must be
more negative than Δρ(omat)**."

`docs/40-predictor-reference-independence.md` §1.4 is dated **2026-08-06**. §7 was in place by
**2026-08-09** (`docs/43-…-archive-2026-08-09-pre-amendment-1.md:348`). docs/40 §1.4 reads OMat24's
own paper (arXiv:2410.12771 §4.2) and quotes it: *"…PBE with Hubbard U corrections for oxide and
fluoride materials containing Co, Cr, Fe, Mn, Mo, Ni, V, or W, **following Materials Project
defaults**,"* with *"VASP input sets … generated using the **MPRelaxSet** class."* It checks the
values against `pymatgen/io/vasp/MPRelaxSet.yaml` locally — every one matches, and the three zeros
(Cu, Ru, Ir) match three absences. Its conclusion, in bold in the source: **"Independence gained on
the U axis by switching MACE → omat is zero."**

So the clause "which does not share that convention" was false when it was written, and this
project had established that it was false, in its own numbered document, three days earlier.

### External corroboration, and it points the other way

Warford, Thiemann & Csányi, *"Better without U: Impact of Selective Hubbard U Correction on
Foundational MLIPs"*, **arXiv:2601.21056** (preprint, 28 January 2026; **no journal reference** —
opened and read 2026-09-03): *"fMLIPs trained on large datasets such as MPtrj, Alexandria, and
**OMat24** encode inconsistencies from the Materials Project's selective use of the Hubbard U
correction."* It goes further than docs/40 needs: it links the severity to oxygen number density in
the U-corrected training configurations and concludes that **"OMAT-trained models are most
affected."**

Prediction 3 asserts MACE should degrade *more* than `omat`. The only external source on the
question says `omat` is the more affected of the two, by a mechanism prediction 3 does not
consider.

### What prediction 3 can and cannot now score

- **It cannot score the shared-convention mechanism, in either direction.** The differential test
  Δρ(MACE) vs Δρ(omat) was built as a contrast between a model that shares the U partition and one
  that does not. Both share it. A contrast between two things that do not differ on the axis under
  test measures nothing about that axis — so **neither** ordering of Δρ bears on the mechanism, and
  in particular §7's own clause *"If instead MACE degrades less than `omat`, the shared-convention
  explanation is wrong and that is reported as a refutation of our own mechanism"* is **unsound and
  is not available as a refutation route.**
- **It can still be reported as a measurement.** Δρ(MACE) and Δρ(omat) against `tier_v3` remain
  well-defined numbers and will be reported as deposited, with this disclosure attached. They are
  descriptive, not discriminating.
- **What is NOT registered here.** Under the corrected premise the shared-convention hypothesis
  implies both models degrade together, which is a *joint* prediction rather than a differential
  one. Registering that now — after the premise is known false and with docs/40 and Warford both
  in hand — would be fitting a prediction to what is already known, and this section deliberately
  does **not** do it. If the entrant wants a joint test, it needs a new dated line that discloses
  it was written after this paragraph.
- **§7 predictions 1, 2 and 4 are untouched.** Nothing above bears on the point predictions, the
  MAE band, or the "falsifier that would be good news".

### Why this was not caught

docs/40 and §7 were written three days apart, by the same person, about the same two models, and
§7's premise contradicts docs/40's headline sentence. The failure was not of evidence — the
evidence was in the repo, recomputed and bolded — but of **cross-reading between a finished
analysis document and a pre-registration being drafted beside it**. A pre-registration is exactly
where a stale premise does the most damage, because the deposit freezes it. Recorded as a rule in
docs/45.

*Surfaced by the docs/70 ideation round as hole H-2 (`docs/70:117-131`); dates, quotes and the
absence of any prior withdrawal re-verified against the tree on 2026-09-03, and the Warford
abstract opened directly rather than carried from the workflow.*

---

# Dated addenda — 2026-09-03: the entrant's directive of this date, and the lines executed under it

**The directive (verbatim, in session, 2026-09-03):**

> make the decisions in that it ends in best rigor and STS placements. I agree with the fixes
> fir A11.R7 but should we do a higher n=?. I confirm A7.7. Continue items 6, 7, 8 (send) and
> relable 9. Write 1. Your call on 3. Continue with 4. Again, decisions that maximize placement
> at STS

This is the entrant speaking, the same instrument as docs/66 §1 — his standing criterion
(maximum rigor, maximum measurement) applied to the nine-item review he was given the same day.
The items are numbered as they were put to him. Each line below records **what he decided** and,
where he delegated ("your call", "write 1"), **what was decided under the criterion he set**,
in the scribe form docs/66 §1 establishes. AI-drafted disclosed infrastructure per A7.7; the
decisions are his; his override right by a later dated line is unaffected, save where a line is
marked irrevocable by its own registered terms.

## Item 1 — D2, the guard-3 adjudication

**[D2 GUARD-3 ADJUDICATED 2026-09-03: Ru BRANCH-CONDITIONAL, Ir BRANCH-CONDITIONAL, Cr
SAME-BRANCH, Ti SAME-BRANCH]** — written under the entrant's directive "Write 1", superseding
**[D2 GUARD-3 ADJUDICATION 2026-09-02: HELD]** (:2364) now that A11.R6 has returned
(docs/68 §11, ladder EXHAUSTED).

Scored on the census of record `tasks/review/a7_3_spin_census_2026-09-02_LADDER-EXHAUSTED.json`.
Per metal, with the evidence each rests on:

- **Ru — BRANCH-CONDITIONAL.** Magnetic at U = 0, and at U = 9 no spin-polarised solution exists
  to compare against: 0 of 16 SCFs converge across three pre-registered mixing settings, 19,200
  iterations, closest approach 595x the threshold, while the nspin = 1 twins in the same cell and
  geometry converge in 25 iterations (docs/68 §2, §11). The endpoints are not in the same branch;
  they are not even in the same spin treatment. Its equalised span is **not scored into a span**
  per docs/61 §A11.7 guard 3.
- **Ir — BRANCH-CONDITIONAL.** Endpoint winners differ in seed (lo s0_OH 0.0 / s0_OOH 0.5; hi
  0.1 / 0.1) and the moments move across the pair (0 -> 1.62 μB on s0_OH; −1.07 -> +0.42 on
  s0_OOH, docs/68:108-114). Not scored into a span.
- **Cr — SAME-BRANCH.** Seeds differ (lo 0.1/0.3, hi 0.6/0.1) but every winner is FM with
  m = 11.0 μB (docs/68:204); a seed label is not a branch. Scoreable.
- **Ti — SAME-BRANCH.** Its guard flag is a **tie-break artifact**, not a branch change: the
  s0_OOH hi winner is the Rider-2 null row selected by tie-break (docs/68:209). Ti's equalised
  span is scoreable.

**Consequence, stated so it cannot be over-read.** This adjudication acts **only** on the
spin-equalised sensitivity census. It does **not** touch the as-built headline: A7.3 remains
**NOT MET at 3 of 6** and A7.2 remains **CONFIRMED at 5 of 6**, per A11.5 (:2029-2033), which
this line does not and cannot amend. With Ru and Ir unscoreable, the equalised sensitivity rests
on Cr, Mn, Fe and Ti; its over-floor set is unchanged at **{Cr, Mn, Fe}**.

**One internal conflict resolved by this line.** docs/68:235 calls Cr and Ir "almost certainly
same-branch"; docs/68:326 calls Cr and Ti same-branch with Ir branch-conditional. **:326 is
adopted and :235's phrasing is superseded** — Ir's endpoint moments move by 1.62 and 1.49 μB,
which is a branch change under any reading of guard 3, and :235 was written before the moment
table at :108-114 was cross-read against it. The report quotes :326.

## Item 4 — A7.7's middle-band disposition, confirmed

**[A7.7 MIDDLE-BAND DISPOSITION CONFIRMED 2026-09-03]** — the entrant, in session: "I confirm
A7.7". This completes the countersignature on the text already written at :2086-2095 and elected
under directive at docs/66 §2; that text is unchanged by this line and nothing in it is
re-authored here. A middle count stands as **SCORED — MIDDLE BAND / NOT MET**, never quoted
bare, licensing no registered consequence, and is neither HELD, nor TRIGGERED, nor
WITHDRAWN-UNSCORED.

The disclosure that text carries on its face (:2108-2111) — that it was written when the 3-of-6
census was already known, and that no choice in its table can flip a verdict between CONFIRMED
and FALSIFIED — **stands with it and travels with every report sentence that scores A7.3.**

## Item 3 — the Ti spin convention (delegated: "Your call on 3")

**[TI CONVENTION 2026-09-03: NSPIN=1 STANDS, FINAL]** — decided under the entrant's delegation
and his maximum-rigor criterion.

The docs/66 §2 row 9 revisit trigger has **fired**: row 9 elected NSPIN=1 "pending the equalised
census … Revisit ONLY after D_Ti is measured", and D_Ti is now measured at **−0.0169 eV**
(docs/68:209; as-built span/2 0.0438 -> equalised 0.0522). The revisit is therefore live, and it
resolves **against** a THROUGHOUT re-run, on four grounds:

1. **It cannot change any verdict.** Equalising moves Ti from 0.0438 to 0.0522 span/2 — further
   from zero, still far under the 0.10 V floor (95.6 meV of distance remaining). A7.3 stays NOT
   MET at 3 of 6; A7.2 stays CONFIRMED at 5 of 6, with Ti FLAT either way.
2. **The instrument for this question already exists and is symmetric.** A0-SPIN is nspin = 2 by
   construction and was pre-registered as exactly the arm that prices the spin convention. Its
   answer is banked. Re-running the base ladder would answer a question that has an answer.
3. **It would buy a partial fix and a new debt.** Ti is 1 of 3 metals carrying no `nspin` card;
   Ru (0/32) and Ir (0/32) would remain, so the deck-census asymmetry survives the re-run. The
   cost is 28 SCFs plus a fresh A6.6 scale disclosure plus a **new relaxation licence** for the
   PULL_TO-remedied geometries — a new registered claimant against a ledger already at its cap.
4. **Rigor here is the disclosure, not the re-run.** The honest sentence is that Ti's absolute
   rows sit ~0.12 eV high while its span is nearly right, and that the equalised arm prices the
   convention at −0.0169 eV. That sentence is already available and is stronger than a re-run
   that changes nothing, because it reports the size of the effect rather than hiding it.

The 28 banked base SCFs stand as scored. **This line does not close the underlying gap**: Ti, Ru
and Ir still carry no `nspin` card in the A0 main decks (0/28, 0/32, 0/32), that fact is reported,
and A11.R8 below is the registered instrument that acts on it at zero SU.

## Item 9 — the gate-(h) AFM family, re-labelled

**[GATE-(H) AFM FAMILY RELABELLED 2026-09-03: SENSITIVITY ARM]** — entrant's directive
("relable 9").

`[AFM-SCOPE RESOLVED 2026-08-30: STANDALONE_FOUR]` (:1979) stands and is not reopened; the family
has already run (docs/64: three BANKED, all GATE-1 PASS at +0.028 / −0.090 / +0.302 meV;
`s0_O__2x1v_off__afm__relax` NOT_CONVERGED as a recorded gap; measured 1,067.9 SU). What changes
is the **label on a completed family**, not a launch decision.

On the 2026-09-03 literature correction (docs/41 "Correction of record", docs/45 §A row 6) the
RuO2 bulk ordered moment is bounded **67-357x below** the diffraction value that justified these
relaxations. They therefore relax into a state the bulk evidence excludes. They are re-labelled a
**sensitivity arm**: they measure how far this Hamiltonian's preferred magnetic state moves the
answer (80-144 meV in state energy, 33-64 meV in adsorption energy), and they are **not** a
ground-state adoption and may not be quoted as one. The `s0_O` gap stays a recorded gap.

**This strengthens rather than weakens the arm's use in the report**, and the reason is worth
stating: a method that prefers, by 80-144 meV, a magnetic state experiment excludes at the
10^-4 μB level is the campaign's own thesis instantiated on its benchmark anchor, with an
independent experimental check. The relabelling is what makes that sentence available.

## Item 2 — A11.R7 countersigned, and the "higher n" question answered

**[A0 LÖWDIN VALENCE TRACKER COUNTERSIGNED 2026-09-03]** — the entrant, in session: "I agree
with the fixes fir A11.R7". The readout at `docs/research/2026-09-03-a11r7-lowdin-valence.md`
and `docs/figs/a0lowdin_valence.json` **enters the report**, under three conditions that are
part of this signature:

1. **R7-P3's falsification is the deliverable** and is quotable as registered: |δq_c| does not
   separate the over-floor from the under-floor group — Mn 0.0069 OVER, Ti 0.0096 under, Ir
   0.0165 under, Cr 0.0399 OVER, Ru 0.0695 under, Fe 0.0735 OVER, completely interleaved, while
   the spans they are meant to predict do not overlap at all.
2. **R7-P1 (REFUTED, ρ = −0.2571) is never quoted without the defect disclosure.** Its registered
   stability rule compares a swing across U against a difference between two states at fixed U;
   it fired on four of six metals and collapsed the primary test to **n = 6**, two metals by three
   steps. It is not a physics statement and the report does not make it one.
3. **R7-P2 is reported, never scored**, exactly as registered.

### The "higher n" question, answered

**The answer is no, and the reason is the interesting part.**

- **n = 18 is the ceiling of the design, not a budget choice.** The pairs are (metal, step): six
  metals by three adsorbate steps. There is no seventh metal and no fourth step. The registered
  test ran at n = 6 only because the malformed rule excluded four metals — the shortfall is a
  defect, not a sample-size decision.
- **Recovering n = 18 on this data is post-hoc and is already reported as such.** With the rule
  corrected the figure is ρ = −0.3808, p = 0.1209 — same sign, still not significant. It is in
  the readout labelled POST-HOC and it stays labelled that way. Re-registering a corrected rule
  now, with that number in hand, would be fitting the instrument to a known result.
- **Inflating n by reading every U rung is REFUSED, and this line refuses it in advance.** Pairing
  Δq_d at each of seven U rungs against span_U(ΔG_i) would give n = 126, and it would be
  **pseudo-replication**: span_U is one number per (metal, step), so the same y would be repeated
  seven times against seven correlated x's. The p-value would fall for an arithmetic reason and
  not a physical one. A larger n bought that way is a rigor loss wearing the costume of a rigor
  gain, and any competent reviewer reads it as one.
- **What actually buys rigor here is not more n — it is a sample that does not have the confound
  in it.** R7 measured one tracker on a set where over/under is perfectly confounded with
  nspin = 2 / nspin = 1. The upgrade is to measure **the same tracker on both sides of that
  confound**. The material for it is already banked and costs nothing: **90 Löwdin artifacts in
  the A0-SPIN arm**, covering Ti, Ru and Ir — precisely the three metals whose A0 main decks carry
  no `nspin` card — with slab plus all three adsorbate states at u000, which is the exact point
  A11.R7 registered its predictor at. Cr, Mn and Fe are already nspin = 2 in the main arm, and
  the census records their equalised span as identical to as-built (D_M = 0.0000), so they need
  no new measurement.

**That instrument is registered as A11.R8, in its own commit, before any spin-arm Löwdin value
has been read.** It is the one test in the campaign that can say whether A7.3's split is a
statement about U or a statement about spin convention — which is the single largest open
question behind the headline. Zero SU.

---

## A11.R8 — the same valence tracker on both sides of the nspin confound, via the already-banked A0-SPIN Löwdin populations (2026-09-03)

**[A0-SPIN LÖWDIN VALENCE TRACKER 2026-09-03: REGISTERED — COUNTERSIGNED 2026-09-03, see the countersignature at the end of this file]** — written
before a single Löwdin number has been read out of the A0-SPIN arm. The commit carrying this
section contains **no readout script and no result**; the script and its output land in a later
commit, and the two hashes are the proof of order. Registered under the entrant's directive of
2026-09-03 ("decisions that maximize placement at STS") as the answer to his "higher n" question:
**not more n — a sample without the confound in it.** Zero new DFT; zero SU.

### What has been read before writing this, and what has not

**Read:** file *names* under `runs/a0/spin/` (a coverage listing, 90 `.lowdin.txt` artifacts:
Cr 12, Mn 8, Fe 8, Ti 26, Ru 12, Ir 24); the `nspin`-card census of the scoped decks (Cr 76/76,
Mn 32/32, Fe 32/32 carry one; Ti 0/28, Ru 0/32, Ir 0/32 do not); and the census of record's
per-metal spans and winner-seed labels. **Not read:** any Löwdin population, charge, or
occupancy from the A0-SPIN arm — the predictor this section registers. That asymmetry is the
point of writing this now.

### The question, and why it is the one worth asking

A7.3's 3-over/3-under split is **perfectly confounded** with nspin = 2 (Cr, Mn, Fe) / nspin = 1
(Ti, Ru, Ir); the deck census above is what makes "perfectly" literal rather than approximate.
A11.R7 measured a valence tracker on that confounded set and R7-P3 fired: |δq_c| interleaved the
two groups completely. **One rescue survives that result** — that R7-P3 failed only because
Ti, Ru and Ir's valence was read from calculations that were never allowed to polarise. A11.R8
tests exactly that rescue, and nothing else.

### Scope, fixed here

Exactly the banked artifacts below; **zero new DFT**, and no artifact outside this list enters.

- **Cr, Mn, Fe — unchanged from A11.R7:** `runs/a0/main/<M>/<state>__u000.lowdin.txt`. These
  decks already carry `nspin = 2` (76/76, 32/32, 32/32 on the scoped `^u\d{3}$` set), and the
  census of record puts their equalised span identical to as-built (D_M = 0.0000 on all three).
  **They need no new measurement and get none.**
- **Ti, Ru, Ir — the new material:**
  `runs/a0/spin/<M>/<state>__u000__sp2m<seed>.lowdin.txt`, state in {slab, s0_O, s0_OH, s0_OOH}.
- **State set:** slab, s0_O, s0_OH, s0_OOH. **U point:** `u000` only — the same single point
  A11.R7 registered its predictor at, so the two are directly comparable.

**Seed-selection rule, fixed before any energy or population is read.** For each (metal, state)
at u000, take the **lowest-total-energy converged `nspin = 2` seed** among those banked; ties
below 1e-6 Ry break to the lowest seed label. This is deliberately **not** the census's winner
seed: the census selects across a pool that includes the `nspin = 1` row (its winner label 0.0
means the unpolarised row won, which happens at least once), and a predictor defined as "the
metal's best spin-polarised solution" must not silently fall back to an unpolarised one. Any
(metal, state) with **zero** converged `nspin = 2` seeds is EXCLUDED, named in the readout with
its reason, and its metal reported at reduced state coverage rather than imputed.

### The tracked quantity, unchanged from A11.R7 so the comparison is single-variable

A(M) = the metal atom nearest the adsorbate binding O in that metal's `s0_OH` cell;
q_d = Löwdin d-channel charge on A(M), summed over spin-up and spin-down;
Δq_d(state) = q_d(state) − q_d(slab), same metal, same U, same arm;
**δq_c = Δq_d(s0_OOH) − Δq_d(s0_OH)**, the valence-change analogue of c_M = ΔG_OOH − ΔG_OH.

### The response, and why it is the as-built span and not the equalised one

**Response = span_U(c_M)/2 as banked in the A0 main readout** — the identical response A11.R7
used. **The equalised span is deliberately NOT used**, and the reason is a line written earlier
today: `[D2 GUARD-3 ADJUDICATED 2026-09-03]` makes Ru's and Ir's equalised spans
BRANCH-CONDITIONAL and therefore **not scoreable into a span**. Using them here would violate a
dated line hours old. Holding the response fixed also makes A11.R8 a **single-variable change**
from A11.R7 — only the predictor's spin treatment moves — which is the whole evidential value.

### Registered predictions

**R8-P1 (primary; the falsification test; n = 6).** With every metal's predictor now read from a
spin-polarised calculation, does |δq_c| separate the over-floor set {Cr, Mn, Fe} from the
under-floor set {Ti, Ru, Ir}? **SEPARATES** iff max|δq_c| over the under-floor set is strictly
less than min|δq_c| over the over-floor set — i.e. a single threshold exists that sorts them.
Otherwise **DOES NOT SEPARATE**.

The registered asymmetry, stated in advance and identical in form to R7-P3:

- **A separation proves nothing.** Six points split 3-and-3 along a line that is still perfectly
  aligned with the metals' 3d/4d/5d identity cannot establish a mechanism, and this line says so
  before the number exists.
- **A failure to separate falsifies the rescue.** If |δq_c| still interleaves when all six
  predictors are spin-polarised, then R7-P3's result was **not** an artifact of the unpolarised
  decks, and the valence-change explanation of the A7.3 split is refuted on this tracker under
  both spin conventions. **That falsification is the deliverable.**

**R8-P2 (n = 18, per-step; REPORTED, NEVER SCORED).** Spearman ρ between |Δq_d| and
span_U(ΔG_i), reported with its exact permutation p. **Registered as unscoreable and it cannot be
promoted later**, for a disclosed reason: nine of the eighteen pairs (Cr, Mn, Fe) are carried over
unchanged from A11.R7, whose post-hoc all-six value is already known (ρ = −0.3808, p = 0.1209).
Half the sample is contaminated by prior sight, so no threshold on it would be honest.

**R8-P3 (n = 3; REPORTED, NEVER SCORED).** For Ti, Ru and Ir alone — the metals whose predictor
actually changes — the shift |δq_c|(nspin = 2) − |δq_c|(nspin = 1), reported per metal with its
sign. This is the direct measurement of **how far the spin convention moves the valence tracker**,
it is genuinely unseen, and it is descriptive by construction: three points admit no test.

### The stability witness, in its corrected form

A11.R7's witness compared `range_U(Δq_d)` — a swing across U — against `|δq_c|`, a difference
between two states at fixed U. Those are different kinds of quantity with no reason to share a
scale; the rule fired on four of six metals and is disclosed as malformed in docs/45. **The
corrected witness registered here is like-for-like:** for each (metal) with two or more converged
`nspin = 2` seeds, compute the spread of δq_c **across seeds at the same U** — a difference of the
same quantity, at the same U, differing only by starting moment. If that seed spread exceeds
|δq_c| itself, the metal's value is **SEED-UNSTABLE**, flagged, and excluded from R8-P1.

Cr, Mn and Fe are single-row in the main arm and carry **no** seed spread; they are marked
**WITNESS-UNAVAILABLE**, which is *not* a flag and does *not* exclude them. Stating that here
prevents the R7 failure mode, where an ill-posed witness silently ate the sample.

### Fatal self-checks — any one failing voids the readout

1. **Parser identity.** The A0-SPIN files are parsed by the same reader as A11.R7 and, on every
   file both sections touch, must return bit-identical values.
2. **Per-atom sum.** total = s + p + d on every parsed atom row.
3. **Spin sum.** up_d + dn_d = total d on every `nspin = 2` row.
4. **Carry-over identity.** Cr, Mn and Fe's |δq_c| here must reproduce their A11.R7 values
   **exactly** — they are the same files under the same rule. Any drift means the reader changed
   and the comparison is void.
5. **Named exclusions.** Every (metal, state) dropped is listed with its reason; a silent drop
   voids the readout.

### What A11.R8 cannot do

It **cannot move A7.2 or A7.3**. A7.2 stays CONFIRMED at 5 of 6; **A7.3 stays NOT MET at 3 of 6
whatever R8 returns**, at denominator 6 per the docs/59 §3c grant. R8 acts on the *explanation*
of the split, never on the count. It also cannot break the confound by separating — only by
failing to.

### Countersignature

Owed from the entrant, as with every dated line. If he declines it, the readout and its output are
withdrawn from the report and this section stands as the record of what was registered and not
used.

## Item 6 — the Cr `oosh` state: neither "finding" nor "artifact" is claimed

**[CR OOSH DISPOSITION 2026-09-03: 1x1-CONDITIONAL OBSERVATION, NOT A FINDING]** — decided
under the entrant's directive ("Continue items 6, 7, 8") and his maximum-rigor criterion.

The measurement is settled and is not reopened here (docs/54 dated correction, docs/45 H-10):
the Cr `oosh` row relaxes to **O-O 1.227 A with both oxygens 3.09 and 3.78 A from the nearest
Cr** — against this campaign's own measured Cr-O bond of 1.856 A — and **the H on a different
O**, both spin seeds agreeing to 0.0004 A over 41 and 42 ionic steps. It is a desorbed O2 plus a
surface hydroxyl and **is not scored as an `*OOH` member**. Ir and Ru, from the identical
starting construction, relax to bound superoxo and are unaffected.

**What is decided:** the state is recorded as a **1x1-conditional observation**. The report says
what was measured, in which cell, and stops there.

**What is deliberately NOT claimed, and why.** The tempting sentence — "rutile CrO2(110) does not
support a bridge-protonated `*OOH`" — is a claim about a *surface*, and it cannot be carried by
**one cell**. At 1x1 the adsorbate sees its own periodic images at the lattice spacing; a
desorption under that lateral pressure is consistent both with a real surface property and with a
coverage artifact, and nothing in the banked set distinguishes them. Asserting the surface
property from a single 1x1 cell is exactly the kind of over-read this campaign exists to indict,
and it would be the weakest sentence in the report for a reviewer to pull.

**The test that would decide it is named and not proposed.** An oosh-seeded Cr deck in the 2x1v
cell would separate the two readings; docs/54 §6 item 10 records that **no such deck exists
anywhere**. Building one is new compute against a registered ledger already at its claimant cap,
it is not proposed here, and this line does not license it. If it is ever wanted it takes its own
dated line under A11.R3.

**Nothing banked moves:** no dG, no eta, no census, no verdict.

## Item 7 — the Co BASIN_DRIFT row: the earlier diagnosis is WITHDRAWN and the finding is worse

**[CO BASIN_DRIFT PROVENANCE 2026-09-03: NO CONVERGED ARTIFACT EXISTS, ANYWHERE]** —
established by exhaustive search under the entrant's directive to continue item 7.

**Correction of my own record, made the same day it was written.** The 2026-09-03 census note
(docs/45, `tasks/todo.md`) said of the Co −77.009 meV BASIN_DRIFT row that *"the fromparent run
happened on Anvil and its output was never pulled … the fix is a file transfer, not compute."*
**That is wrong.** Searched this date:

- **Locally:** `runs/s3/Co/s0_O__1x1_off__g1.out` and both `.attempt` files report
  "convergence NOT achieved" and print no `!` total energy;
  `runs/s3/Co/s0_O__1x1_off__g1.fromparent.in` exists with **no `.out`**.
- **On Anvil (`x-fcai3@anvil.rcac.purdue.edu`):** the run tree is not on scratch; the banks live
  as tarballs in `$HOME`. **Every** tarball was listed. `s0_O__1x1_off__g1.fromparent.out` exists
  for **Ni** (`s3_bank2.tgz`) and for two `Cr_lit3` rows — and **not for Co**, in any archive.
  The only Co copies of the parent are `s3_bank2.tgz` and `s3_round3_outs.tgz`, and the round-3
  copy was extracted and read: **0 occurrences of "convergence has been achieved", 1 of
  "convergence NOT achieved", no `!` energy** (md5 cffbcfd2a2e9df3dfb4afd73b8aed646).

**The corrected finding.** The Co row's GATE-1 remedy was **never executed**, not merely never
retrieved. The registered remedy at :311-314 (re-relax from the GATE-1 geometry until it passes)
has not run, and the affordability escape at :317-320 (quote the GATE-1 energy with a stated
4 meV residual) is **also unavailable**, because Co's GATE-1 SCF never converged and so has no
energy to quote. **There is no artifact from which the −77.009 meV can be re-derived.**

**A second reason the escape does not reach this family, stated for the record.** The 4 meV
residual at :317-320 is calibrated on docs/41 §6f, where relaxing on the corrected surface bought
3.46 / 1.99 / 2.81 meV. The Fe row of this same family sits **384.3 meV** below its parent. A
drop two orders of magnitude outside the calibration set is a **basin change, not a density
correction**, and the residual bound does not transfer to it. That is true whatever is decided
about Co.

**Disposition, and what this line does NOT do.** The row is recorded as a **recorded gap** with
the provenance above — the same class as `s0_O__2x1v_off__afm__relax` in the gate-(h) family. It
is **not withdrawn** and its number is **not quoted as re-derived**.

**Recommended, and requiring the entrant's own dated line before it runs:** one
fixed-geometry SCF from the parent density on `s0_O__1x1_off__g1.fromparent.in`, at the repo's
measured band of **5-19 SU** — roughly 0.02 % of the 59,761.1 SU balance. It would close a
registered remedy that is currently unexecuted on a row every dG built on it inherits. **It is
not launched here.** A11.R3 requires each licensed compute addition to carry its own dated line,
and a submission to a shared allocation is not a scribe's act; the deck is staged and one command
away.

---

## A11.R8 — countersigned

**[A0-SPIN LÖWDIN VALENCE TRACKER COUNTERSIGNED 2026-09-03]** — the entrant, in session:
*"I counter sign the A11.R8"*. The readout at `docs/research/2026-09-03-a11r8-spin-valence.md`
and `docs/figs/a0spin_valence.json` **enters the report.**

**What is countersigned, stated so it cannot be over-read:**

- **R8-P1 = DOES NOT SEPARATE**, and it is the deliverable. With every metal's predictor read
  from a spin-polarised calculation, |δq_c| still interleaves the two A7.3 groups completely —
  Mn 0.0069 OVER, Ti 0.0094 under, Ir 0.0209 under, Cr 0.0399 OVER, Ru 0.0714 under, Fe 0.0735
  OVER; largest under-floor 0.0714 against smallest over-floor 0.0069, a gap of **−0.0645**.
  **The last surviving rescue of R7-P3 is falsified:** R7-P3's failure was not an artifact of
  Ti/Ru/Ir having been read from decks that carry no `nspin` card.
- **The registered asymmetry holds and is quoted with the result.** A separation would have
  proved nothing; only a failure to separate carries information, and that is what was observed.
- **R8-P3, reported never scored:** the spin convention moves the tracker by **at most 0.0044
  electrons** (Ir +0.0044, Ru +0.0019, Ti −0.0002), and **the ordering of all six metals is
  unchanged** from A11.R7.
- **R8-P2 stays REPORTED, NEVER SCORED**, exactly as registered, and its n = 18 figure
  (ρ = −0.3148, nominal p = 0.2046) may not be promoted to a scored test by this or any later
  line — nine of its eighteen pairs were seen before it was written. See A11.R9 below for the
  only form in which an n = 18 statement may be made.
- **Self-checks passed:** carry-over identity exact at **0.0** for Cr, Mn and Fe; **zero**
  exclusions; every seed witness STABLE at spreads of 0.0002–0.0004; parser identity with A11.R7
  enforced by import. 11 tests.

**Binding, restated with the signature:** A11.R8 moves no banked verdict. **A7.2 stays CONFIRMED
at 5 of 6; A7.3 stays NOT MET at 3 of 6 at denominator 6.** It acts on the *explanation* of the
split and never on the count.

---

## A11.R9 — the n = 18 statement, in the only form it can honestly be made (2026-09-03)

**[N18 ROBUSTNESS SURFACE 2026-09-03: REGISTERED — POST-HOC AT ONE RUNG, OUT-OF-SAMPLE AT SIX]**
— written under the entrant's directive of this date: *"Continue and do n=18"*. The commit
carrying this section contains **no script and no result.**

### Why this is not simply "R8-P2, promoted"

The entrant asked for the n = 18 test. **R8-P2 already carries an n = 18 number and it may not be
used as one**, by its own registration: *"Registered as unscoreable and it cannot be promoted
later"*, because nine of its eighteen pairs are carried over from A11.R7 whose post-hoc all-six
value was already known. Promoting it would be laundering a seen number into a scored test. This
section therefore does **not** promote it. It builds the n = 18 statement out of material that is
mostly **unseen**, and labels precisely which part is not.

### What is seen and what is not, stated before the run

- **Seen:** the n = 18 correlation at **u000**, in both arms — A11.R7's post-hoc all-six figure
  (ρ = −0.3808, p = 0.1209) and A11.R8's nspin = 2 figure (ρ = −0.3148, nominal p = 0.2046).
- **Not seen, and never computed by anything:** the n = 18 correlation at **u150, u300, u450,
  u600, u750, u900**. Six of the seven rungs are out-of-sample.

So A11.R9 is **post-hoc at one rung and a genuine out-of-sample replication at six.** That
asymmetry is the whole evidential content and it is written here before the numbers exist.

### The grid, fixed here so no rung can be selected afterwards

The **common grid** is every U token banked for **all six** metals. Measured from the A11.R7
readout's own `dq_d` keys: **u000, u150, u300, u450, u600, u750, u900 — exactly seven rungs.**
Cr's finer ladder (19 tokens) and the four odd tokens that exist for one metal only (Mn u390,
Fe u530, Ir u591, Ru u673) are **excluded**, because a rung missing a metal is not an n = 18 test.

### The quantity, unchanged from A11.R7 so this is a replication and not a new instrument

At each rung u, for each metal, the three CHE **step increments**
`dq1 = Δq_d(*OH)`, `dq2 = Δq_d(*O) − Δq_d(*OH)`, `dq3 = Δq_d(*OOH) − Δq_d(*O)`
are paired against the banked `span_dG1/2/3`. n = 6 metals × 3 steps = **18** at every rung.
The response is the same at every rung by construction — `span_U(ΔG_i)` is a U-spanning quantity
— and **only the predictor moves.** That is the point: it asks whether u000 was special.

### What is refused in advance, again

**The 7 × 18 = 126 pairs are never pooled.** Pooling them is the pseudo-replication this campaign
already refused once: the response would be repeated seven times against seven correlated
predictors, and the p-value would fall for an arithmetic reason. **Seven separate n = 18 tests are
reported; one pooled n = 126 test is not computed and may not be quoted.**

### Registered reporting rule — the anti-selection clause

**All seven rungs are reported, always, as a distribution.** The readout prints ρ and its nominal
p at every rung, plus min / median / max and the count of rungs reaching nominal p < 0.05. **No
rung may be quoted alone**, and the report may not lead with the strongest. Multiplicity is
stated with the result: seven tests at α = 0.05 give a ≈30 % chance of at least one nominal hit
under the null if they were independent — and they are **not** independent, since the predictor
varies smoothly in U, so that figure is an upper bound and the effective number of tests is
smaller than seven.

**Non-independence within a rung, carried from A11.R7 unchanged:** the three steps of one metal
share that metal's slab reference, so every p here is **NOMINAL**.

### R9-P1 (the only statement, and it is descriptive)

**Reported as an effect-size surface. Scores nothing.** There is no threshold, no CORROBORATED
and no REFUTED. The honest questions it answers are:

1. Does the sign of ρ hold across U, or is the negative sign a feature of u000 alone?
2. Is the magnitude stable, or does it wander?

**Registered reading, fixed now:** a sign that **flips across the grid** would mean the u000
result carries no information about U-robustness and the report must say so. A sign that
**holds at every rung with comparable magnitude** is consistent with A11.R7's conclusion and adds
nothing to it — the tracker still fails to explain the A7.3 split, at every U. **Neither outcome
can rescue the valence explanation**, because R7-P3 and R8-P1 are separation tests and this is a
correlation surface; a correlation among 18 heterogeneous (metal, step) pairs is not a mechanism.

### Binding

**CONFIRMATORY-INELIGIBLE.** A11.R9 cannot score any prediction, cannot be cited as a registered
test, and **cannot move A7.2 or A7.3**. A7.2 stays CONFIRMED at 5 of 6; **A7.3 stays NOT MET at
3 of 6** at denominator 6. It may appear in the report only as a labelled robustness surface with
its post-hoc rung named.

### Countersignature

Owed from the entrant. If declined, the readout is withdrawn and this section stands as the
record of what was registered and not used.

### Correction to this section, same day, before the result was quoted anywhere

**[A11.R9 GRID CORRECTED 2026-09-03: FIVE RUNGS, NOT SEVEN]** — the registration above states
*"exactly seven rungs"* and names u000, u150, u300, u450, u600, u750, u900. **That was wrong when
written.** It was derived from the *union* of the three step states per metal rather than their
*intersection*, and the rule as registered requires all three — a rung missing a state is not an
n = 18 test.

**Measured:** **Fe has no `s0_O` at u300 or u450** (`docs/figs/a0lowdin_valence.json`,
`per_metal.Fe.dq_d`), while Ti, Ru, Ir and Mn all do. Both rungs therefore leave the common grid.
The correct grid is **five rungs: u000, u150, u600, u750, u900** — one post-hoc and **four
out-of-sample**, not six.

**Nothing else moves.** The rule itself is unchanged and was applied as written; the script's own
guard raised on the discrepancy rather than reporting a short rung, which is why this was caught
before a number was quoted. The registered reading, the anti-selection clause, the pooling
refusal and the binding are all unaffected. The out-of-sample claim weakens from six rungs to
four and is restated at four here.
