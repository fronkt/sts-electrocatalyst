# 36 — The screen is validated, and the melt list it replaces was built on a desorbed surface

**Date:** 2026-08-05 · **$0 spent, no box, no GPU** — everything here ran on the laptop CPU.
**Trigger:** the Purdue potentiostat is BOOKED, so the experimental half is live and the
melt list is now on the critical path.
**Code:** `src/scripts/{screen_mace,melt_list}.py` · `src/dft/pourbaix_multi.py` ·
`src/hea_oer/surfaces_rutile.adsorbate_starts` · 94 tests
**Supersedes:** [docs/15](15-round1-melt-test-plan.md) §1 (melt set) · closes the open half of
[docs/31](31-r2-stability-gate.md) §7

---

## 1. Verdict

**The screening pipeline reproduces the DFT tier's ranking at n = 7 and the gate is met:
Spearman ρ = +0.8571, exact two-sided p = 0.0238, η MAE = 0.130 V.**

This is a different and stricter question than [docs/35](35-n7-campaign-result.md) answered.
docs/35 scored MACE-MPA-0 on **the DFT tier's own 18-atom cells** — it measured the *model*.
This scores the **whole pipeline on its own slabs**: pymatgen-cleaved 2×2 rutile(110), Vegard
lattice constants, its own cus-site finder, its own adsorbate placement, its own relaxation,
the same CHE referencing — exactly as the HEA screen will run it. A model that ranks well on
someone else's geometry can still be wrecked by a builder defect, which is not hypothetical
here (§2).

| | ρ(η) | exact p | η MAE |
|---|---|---|---|
| docs/35 — model, on DFT geometries | +0.857 | 0.0238 | 0.172 V |
| **docs/36 — pipeline, on its own slabs** | **+0.857** | **0.0238** | **0.130 V** |

The pipeline is not merely as good as the single-point evaluation; its **MAE is 42 mV lower**.
Letting the MLIP find its own minimum beats scoring it on a geometry someone else relaxed —
consistent with the repair campaign, where MACE's own minima were right and our DFT's were
wrong four times running (docs/33 §5b, docs/35 §4).

| | MACE (pipeline) | DFT | err | winning starts (`*O`/`*OH`/`*OOH`) |
|---|---|---|---|---|
| Cr | 0.353 | 0.491 | −0.138 | builder, pull2.10, pull2.10 |
| Co | 0.764 | 0.544 | +0.220 | pull1.70, pull2.10, pull2.10 |
| **Ir** | **0.526** | **0.781** | **−0.254** | pull2.10, pull1.70, builder |
| Ru | 0.731 | 0.787 | −0.056 | pull2.10, pull2.10, pull2.10 |
| Mn | 1.069 | 0.892 | +0.178 | pull2.10, pull1.70, pull2.10 |
| Ni | 1.056 | 1.084 | −0.027 | pull1.70, pull1.70, pull2.10 |
| Fe | 1.229 | 1.263 | −0.034 | builder, pull2.10, pull2.10 |

Two ranking errors, both on pairs the reference cannot resolve: Co/Ir and Mn/Ni. The tier's own
differential resolution is ~0.17 V (docs/32 §2).

**Where it is worst: IrO₂, and it moved.** docs/35 had MACE at +0.131 V on Ir; relaxing on our
own slab sends it to **−0.254 V**, the largest error in the set. Ir is the one material here with
a real OER pedigree (lit. 0.54–0.58 V), and the pipeline now *under*-predicts it. That is a
caveat on any claim that a candidate "beats IrO₂", and it is recorded here rather than buried.

## 2. The melt list was built on a surface where nothing was bound

`surfaces._adsorbate` sets the initial adsorbate height above the slab's **topmost** atoms. On
rutile(110) those are the bridging-O rows, which stand above the cus metal row the adsorbate is
supposed to bind. Measured on the HEA path (Fe32Ni17Co34Mn18, 2×2, seed 0):

| | `*O` | `*OH` | `*OOH` |
|---|---|---|---|
| M–O at the builder placement | **3.080 Å** | **3.130 Å** | **3.130 Å** |

`adsorbate_qc.M_O_DESORBED_MIN` is **3.00 Å**. Every adsorbate in the HEA screen therefore
started **already desorbed** — past the cut the campaign uses to condemn a structure as
chemically meaningless.

This is not a new defect. It is the same placement that trapped Cr's `*O` 1.396 eV above its
true minimum and left `*OOH` desorbed on Mn, Fe and Ni: four structures that passed every
numerical QC check, entered the published tier, and cost $2.64 to repair (docs/33 §5b,
docs/34 §4b, docs/35 §4). What is new is the realisation that **the HEA screening path inherited
it verbatim**, and that screening thousands of compositions through it would have reproduced the
defect on every one of them — with no DFT tier downstream to catch it, because the whole point of
the screen is that there is no DFT for those compositions.

The remedy is the one already proven on the endmembers: relax each state from the builder
placement **and** from rigid pull-ins at M–O = 1.70 / 2.10 Å, keep the lowest energy, and record
the winning bond length so a desorbed "minimum" cannot enter a melt list silently.

**It is load-bearing, not belt-and-braces: 19 of the 21 winning starts in §1 were pull-ins.**
Without the fix, 19 of 21 states would have been relaxed from an already-desorbed geometry. The
other 2 were the builder start, which is why all three are kept rather than replacing one bad
default with another.

## 3. One decoration is the wrong instrument for a distribution

A 2×2 rutile(110) slab exposes exactly **4** cus sites, and which elements occupy them is an
accident of one seeded shuffle. For the headline candidate Fe32Ni17Co34Mn18:

| seed | elements on the 4 cus sites |
|---|---|
| 0 | Co ×2, Fe ×2 — **Ni and Mn absent entirely** |
| 1 | Ni ×2, Fe ×1, Co ×1 |
| 2 | Mn ×1, Co ×1, Ni ×1, Fe ×1 |

Under seed 0 the two elements making up 34 at.% of the alloy never appear at an active site, so
the composition's reported η is the best of a Co/Fe-only sample. The project's thesis is that
high-entropy disorder produces a **distribution** of active sites whose favourable tail does the
catalysis (docs/12 §3b); estimating that tail from four sites of one decoration is the wrong
instrument for the hypothesis under test. The 2026-06 UMA sweep (docs/13) had the same weakness.

The screen now pools cus sites over **3 independent decorations** and records which metal each
winning site sits on, so site-metal coverage is visible in the output rather than assumed.

**Sampling-depth caveat, stated once and loudly.** The screen reports the lowest-η site out of
12 (4 sites × 3 decorations). Every candidate is sampled to the same depth, so ranking candidates
*against each other* is sound. Ranking them against the **endmember tier is not**: a pure MO₂ slab
has one distinct cus site, so its η is a single draw while an HEA's is a minimum over many, and a
tail statistic beats a single draw for free. "This HEA beats β-MnO₂" does not follow from these
numbers and needs matched sampling before anyone writes it down.

## 4. Stability: the open half of R2, and it reorders the melt set

docs/31 §7 closed with the admission that the multi-element diagram an actual HEA needs was not
built, and §8.3 with the requirement that any screening objective be activity × ΔG_pbx. That half
is now done, at **$0 and with no new network access** — the R2 cache already holds the Pourbaix
entry set for all eight metals, and a multi-element hull is built by pooling them at a
candidate's own cation ratios.

**The metric, and why not ΔG_pbx of "the HEA oxide".** That number would require an entry for a
phase nobody has made and MP does not hold — exactly what docs/31 §5 refused to emit for rutile
CoO₂/NiO₂/CuO₂. So the question is turned around into one the data can answer: **at operating
conditions, what fraction of this composition's cations is thermodynamically soluble?** Build the
hull at the candidate's ratios, read the stable assemblage at (pH, V), add up the cation moles
sitting in aqueous ions rather than solids.

**Validation:** the quaternary hull reproduces docs/31 §4's per-element assignments exactly —
Fe→Fe₂O₃(s), Co→CoOOH(s), Mn→MnO₄⁻, Ni→Ni(OH)₃⁻ at pH 14 / 1.53 V vs RHE.

**The docs/15 melt set, at pH 14 / 1.53 V vs RHE, 10⁻⁶ M:**

| composition | soluble cations | its role in docs/15 §1 |
|---|---|---|
| FeCoNi | **33.3 %** | the *ablation* — meant to be the foil |
| Fe32Ni17Co34Mn18 | **34.0 %** | headline pick |
| Cr19Co28Fe25Ni28 | 47.0 % | the deliberately *predicted-poor* anchor |
| Co20Ni20Cr20Mn20Cu20 | 60.0 % | equiatomic reference |
| Cr6Fe33Ni27Mn34 | 67.0 % | "low-cost / scalability" pick |
| Mn19Fe12Ni35Co16Cr18 | 72.0 % | "most-confident prediction" |

Three things follow, and none of them is comfortable:

1. **Nothing in the set is stable.** The best still dissolves a third of itself. There is no
   stable-and-active corner to optimise into — which is why the replacement melt list spans the
   activity/stability front rather than scalarizing it (`melt_list.py`).
2. **The two picks docs/15 sold hardest are the two worst.** "Most-confident" and "low-cost" rank
   6th and 5th on stability.
3. **The ablation is the most stable composition in the set.** FeCoNi was included to be beaten;
   on this axis it wins. It is a contender, not a foil.

**Concentration sensitivity** (docs/31 §6.5 flagged the Ni assignment as concentration-sensitive
and every candidate here is Ni-bearing, so this had to be checked):

| conc. | Fe32Ni17Co34Mn18 | FeCoNi | Ni phase |
|---|---|---|---|
| 10⁻⁸ M | 66.0 % | 66.7 % | Ni(OH)₃⁻ (ion) |
| 10⁻⁶ M | 34.0 % | 33.3 % | Ni(OH)₃⁻ (ion) |
| 10⁻⁴ M | 34.0 % | 33.3 % | Ni(OH)₃⁻ (ion) |
| 10⁻² M | 17.0 % | 0.0 % | **NiO (solid)** |

The **ordering is robust** across the dilute range, but the absolute percentage is not a physical
constant — it moves by a factor of two across four decades, and at 10⁻² M Ni passivates as NiO and
FeCoNi becomes fully insoluble. Quote the ranking; never quote the percentage without its
concentration.

## 5. What this does and does not establish

**Does establish**

- The screening pipeline, end to end on its own slabs, reproduces the QC-gated DFT ranking at
  n = 7 with p = 0.0238 and MAE 0.130 V.
- The builder placement starts every rutile adsorbate past the desorption cut, and the multi-start
  remedy is load-bearing (19/21 winning starts).
- A single decoration samples the HEA active-site distribution too thinly to estimate its tail.
- Soluble cation fraction at operating conditions for the docs/15 melt set, cross-validated
  against docs/31's independent single-element result.

**Does not establish**

- **Anything about an HEA's activity yet.** The screen is running; this document validates the
  instrument, not a result.
- **That any of this describes the real electrode.** The screen ranks rutile-structured mixed
  oxides. What gets melted is an fcc metal that reconstructs to an (oxy)hydroxide under OER —
  docs/31 quantified that reconstruction and the oxyhydroxide-termination spot-check (docs/28 §4
  M4) is still not done. The rutile tier remains a **calibration** tier (docs/31 §8.1).
- **Point-wise η.** docs/34's pre-registered out-of-sample test came back 1 hit / 1 miss, missing
  η(Co) by +0.339 V — 2.3× the validated bar. The screen orders; it does not predict.
- **Bulk ≠ surface, thermodynamics ≠ rates, 0 K, 10⁻⁶ M.** All of docs/31 §7's standing caveats
  carry over unchanged.
- **The U-sensitivity question, which is still open and still required.** docs/35 §5: our DFT puts
  Cr (0.491) and Co (0.544) below both noble anchors, inverting the experimental ordering, and
  Cr/Co carry Hubbard U while Ru/Ir do not. The screen is validated *against that reference*, so
  if the reference has a cross-family systematic, the screen inherits it.

## 6. Running now, and what needs a decision

**Running:** `screen_mace.py screen`, 12 diverse single-phase candidates (3339/4000 sampled
compositions passed the Hume-Rothery/Ω–δ filter), 4 cus sites × 3 decorations, checkpointed after
every candidate to `results/r4_screen.json`. On this CPU-only box that is a **~15–20 h job**;
partial results are ranked and usable at any point. A GPU box would do it in well under an hour
for roughly $1 — **Vast credit is $0.295**, so that is a top-up decision, not a technical one.

**Then, both cheap:** `pourbaix_multi.py gate` joins stability onto the ranking, and
`melt_list.py build` emits the frozen list — Pareto front over (activity, stability) plus the
predicted-poor anchor and the FeCoNi ablation.

**Still Frank's call, and unchanged by any of this:**

- **STS sponsor of record** — open since June, hard-required by Nov 5, and the only item here
  whose lead time is outside our control.
- **Hazardous-activities risk assessment, dated, BEFORE the first melt** (docs/25). The Cr-bearing
  candidates leach Cr(VI) under anodic potential; the stability gate now quantifies that the
  Cr in every Cr-bearing candidate goes to chromate.
- **The U-sensitivity ladder** — needs credit, and docs/35 §5 already promoted it from optional
  to required.
