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
absent for Cr, Ir and Ru and present for Mn, Fe, Co, Ni and Cu, having arrived through the
endmember rescue ladder that the three trouble-free metals never went through.

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
