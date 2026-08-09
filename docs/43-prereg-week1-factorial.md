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
