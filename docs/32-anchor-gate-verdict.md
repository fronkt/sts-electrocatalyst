# 32 — RuO₂/IrO₂ anchor verdict: the DFT tier's resolution, measured

Campaign run 2026-07-31 → 2026-08-01 on Vast instance 46420594 (dual EPYC 7742).
Cost $4.42. Instance destroyed on completion. Companion to [`30`](30-qc-audit-and-r1-campaign.md)
(which froze the gate) and [`31`](31-r2-stability-gate.md) (stability).

## 1. Verdict: GATE NOT MET

The gate, frozen in docs/30 §7 before any anchor number existed:

> DFT tier validated if η(RuO₂) and η(IrO₂) both land in **0.30–0.90 V** *and* **η(Ru) < η(Ir)**.

| metal | ΔG_OH | ΔG_O | ΔG_OOH | descriptor | pls | **η_DFT** | literature | error |
|-------|-------|------|--------|-----------|-----|-----------|------------|-------|
| Ru    | 0.529 | 1.692 | 3.709 | 1.163 | 3 | **0.787 V** | 0.37–0.42 V | **+0.39** |
| Ir    | −0.000 | 1.641 | 3.652 | 1.641 | 3 | **0.781 V** | 0.54–0.58 V | **+0.22** |

- clause 1 — η(Ru) ∈ [0.30, 0.90]: **PASS**
- clause 2 — η(Ir) ∈ [0.30, 0.90]: **PASS**
- clause 3 — η(Ru) < η(Ir): **FAIL** (0.787 vs 0.781; gap **+0.006 V**)

All eight anchor jobs passed the strict gate independently: `JOB_DONE=1`, zero SCF
failures, free-atom fmax 0.0014–0.0019 Ry/au (threshold 2e-3), and relaxed adsorbate
geometries verified textbook — intact peroxo `*OOH` (Ru–O 1.947 / O–O 1.387 / O–H
1.026 Å; Ir–O 1.912 / O–O 1.427 / O–H 0.982 Å), `*OH` at M–O ≈ 1.93 Å, short M=O
`*O` at 1.77–1.95 Å. **Nothing here is a convergence artefact.**

## 2. The real finding: a 6 mV gap is not a ranking

Clause 3 fails, but reporting it as "the tier got the order backwards" would overstate
what happened. The gap is **0.006 V** — 158× smaller than the 0.945 V spread across the
five materials now on record, and ~30× smaller than this method's own accuracy. Ru and
Ir are **tied**, not mis-ordered.

That is the useful number the anchors were bought to produce. Quantitatively:

- Absolute error is large and positive for both: **+0.39 V** (Ru), **+0.22 V** (Ir).
- The *differential* error between two chemically similar rutiles is **0.17 V** —
  and the true Ru–Ir separation is only ~0.15 V. The tier cannot see a difference
  smaller than its own differential error.

So the anchors did their job: **they measured the tier's resolution rather than
confirming it.** A failed pre-registered gate that yields a calibrated error bar is
worth more than a passed one that yields none.

## 3. What this costs the ranking claims

Full DFT record, n = 5, QC-gated:

| metal | descriptor | pls | η_DFT |
|-------|-----------|-----|-------|
| Cr | 2.956 | 2 | 1.726 |
| Fe | 2.493 | 2 | 1.263 |
| Mn | 2.122 | 2 | 0.892 |
| Ru | 1.163 | 3 | 0.787 |
| Ir | 1.641 | 3 | 0.781 |

Applying the 0.17 V differential error as a resolution floor, the separations are
Cr→Fe 0.463 V (resolved), Fe→Mn 0.371 V (resolved), Mn→Ru 0.105 V (**not** resolved),
Ru→Ir 0.006 V (**not** resolved). The tier therefore supports roughly

> **Cr > Fe > {Mn ≈ Ru ≈ Ir}** — three distinguishable levels across five materials.

Caveat, stated plainly: 0.17 V is a *two-point* estimate, and literature η themselves
carry setup dependence. It is an order-of-magnitude resolution estimate, not a
rigorous error bar. But it is the only empirical one this project has.

Consequence for R0: the Spearman test of UMA against DFT is weaker than n = 5 implies,
because the bottom three targets are not reliably ordered among themselves. Combined
with the exact permutation arithmetic (see `tasks/todo.md` R3), a significant rank
claim from this data is not currently reachable. **This does not touch the R0 negative
result** — "no out-of-box UMA head ranks rutile OER" survives, because oc22 was
*anti*-correlated at ρ = −1.00, a failure far larger than any resolution question.

Also worth noting: there is a clean structural split. The three 3d rutiles sit at
descriptors 2.12–2.96, far onto the weak-O-binding leg (apex 1.60) and step-2 limited;
both noble rutiles sit at 1.16–1.64, near the apex and step-3 limited. The tier gets
that coarse chemistry right, which is consistent with it resolving ~0.4 V differences
and not ~0.1 V ones.

## 4. The IrO₂ scaling deviation — unresolved, recorded both ways

The `*OOH`/`*OH` scaling constant ΔG_OOH − ΔG_OH:

- **Ru: 3.180 eV** — textbook, 0.02 eV from the universal 3.2 ± 0.2.
- **Ir: 3.652 eV** — **+0.45 eV, outside the band.**

Because Ru obeys the relation to 0.02 eV under the *identical* builder, cutoffs, slab,
gas references and QC gate, this is **not** a pipeline-wide `*OOH` systematic. It is
specific to Ir. Two readings remain consistent with the data:

1. Scaling genuinely breaks for IrO₂(110) at this setup; or
2. Ir's ΔG_OH (= −0.000 eV) is ~0.45 eV over-bound, which would restore the scaling
   *exactly* and simultaneously move Ir's descriptor from 1.641 (on the apex, matching
   literature) to ≈ 1.19 (beside Ru's 1.163).

**Hypothesis tested and refuted.** The obvious mechanism for (2) — extra stabilisation
of Ir's `*OH` by an H-bond to a lattice bridge O — does not hold. The two `*OH`
geometries are near-identical and neither is H-bonded:

| | M–O(ads) | O–H | tilt from normal | H⋯nearest lattice O |
|---|---|---|---|---|
| Ru | 1.929 Å | 0.981 Å | 67.2° | 2.701 Å |
| Ir | 1.937 Å | 0.981 Å | 66.5° | 2.756 Å |

So the 0.53 eV difference in ΔG_OH between the two is **electronic, not structural**,
and the deviation stays unexplained. Recorded rather than resolved — this is the same
shape of claim as the withdrawn docs/29 §4b NiO₂ anomaly, and it gets the same
treatment until something independent settles it.

η is unaffected either way: both anchors are `pls = 3`, which uses ΔG_OOH − ΔG_O and
never touches ΔG_OH.

## 5. Ni: still retracted, and n stays at 5

`Ni_slab/s0_O` was stopped deliberately at 22:44 UTC after stalling — SCF flat at
2.1e-4 Ry against `conv_thr = 1e-6` for 4 iterations, still on ionic step 1 of ~20 at
~150 s/iteration (~17 h and ~$10 to reach a `convergence NOT achieved` ending). Its
partner `s0_OH` was then worthless on its own and died with the instance; its partial
output is kept for MLIP frames only.

Per docs/30 §7, Ni is **not** reinstated and the parity stays at **n = 5**.

The cost/benefit has changed since docs/30, and against the earlier note in
`todo.md` the case for the rescue is now *stronger*, for a different reason: at n = 5
only a perfect ordering reaches p < 0.05 (ρ = 1 → p = 0.017; one adjacent swap →
ρ = 0.9 → p = 0.083), whereas at n = 6 two ranking errors still clear it
(ρ = 0.886 → p = 0.033). Ni buys **error tolerance**, not a marginally better p.

But §3 above complicates that: if Ni's η lands near 0.8 V it becomes a fourth member
of the unresolved cluster and buys nothing. A rescue would need the two-stage SCF
protocol (smooth-`degauss` pre-converge, then production `degauss` for the energies)
at ~$5–9. **Owner's call; not spent.**

## 6. Ledger

| | |
|---|---|
| Jobs accepted | 8/8 anchor jobs TRUSTWORTHY |
| Jobs killed | 2 (Ni `s0_O` stalled, Ni `s0_OH` orphaned) |
| Spend | $4.42; instance destroyed |
| New η on record | η(RuO₂) = 0.787 V, η(IrO₂) = 0.781 V |
| Gate | **NOT MET** (clause 3, by 6 mV) |
| Tier resolution | ~0.17 V differential; ~3 distinguishable levels over 5 materials |
