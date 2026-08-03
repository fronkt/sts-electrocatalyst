# 34 — Pre-registration: which sixth metal to buy, and what the DFT must show

**Date:** 2026-08-03 · **Spend so far: $0** · **Status:** predictions frozen, DFT not yet
commissioned.
**Code:** `src/dft/mlip_predict.py` · **Artifacts:** `results/r3_predict_validation.json`,
`results/r3_predict_nicocu.json`, `results/r3_maskbias.json`
**Follows:** [`32 §5`](32-anchor-gate-verdict.md) · [`33 §6`](33-r3-mlip-evaluation.md)

This document exists so that the DFT we buy next is a **test of a stated prediction**
rather than a fit to whatever comes back. Everything below is on record before any
instance is rented.

## 1. Why a sixth point at all

The R3 gate is a Spearman rank correlation between a screener's η and the DFT tier's η.
Exact two-sided permutation p:

| n | ρ needed for p < 0.05 | adjacent swaps tolerated |
|---|---|---|
| **5 (now)** | 1.000 only | **zero** |
| 6 | 0.886 | two |
| 7 | 0.821 | five |

MACE-MPA-0, free and un-fine-tuned, currently makes exactly one ranking error: **Ru vs
Ir**, the pair our own DFT separates by **6 mV** against a measured tier resolution of
~0.17 V (docs/32 §2). At n = 5 the gate therefore demands a model reproduce an ordering
the reference cannot resolve, and a perfect score would be indistinguishable from luck.
**n, not model quality, is the binding constraint.** A $1.9 fine-tune cannot fix it; a
~$3 DFT job can.

## 2. The protocol, and its measured error bar

`mlip_predict.py` relaxes each state with MACE-MPA-0 from **builder geometries only** —
no DFT input of any kind — starting from the builder placement *and* from rigidly
pulled-in copies at M–O = 1.70 and 2.10 Å, keeping the lowest relaxed energy. Multi-start
is not decoration: Cr's `*OOH` relaxes to a **desorbed 3.013 Å** from the builder start
but to 1.951 Å and 0.088 eV lower when pulled in — i.e. a single-start protocol would
reproduce exactly the defect the 2026-08-02 repair paid $2.64 to fix.

Run first on the five metals whose answer we already have:

| | ΔG_OH | ΔG_O | ΔG_OOH | descr | η_MACE | η_DFT | err |
|---|---|---|---|---|---|---|---|
| Cr | 1.431 | 3.162 | 4.681 | 1.731 | 0.501 | 0.491 | **+0.010** |
| Ru | 0.218 | 1.424 | 3.300 | 1.206 | 0.646 | 0.787 | −0.141 |
| Ir | −0.054 | 1.443 | 3.585 | 1.497 | 0.912 | 0.781 | +0.131 |
| Mn | 1.539 | 4.010 | 4.458 | 2.471 | 1.241 | 0.892 | +0.349 |
| Fe | 1.874 | 4.485 | 4.489 | 2.611 | 1.381 | 1.263 | +0.118 |

**ρ(η) = +0.900 · ρ(descriptor) = +0.900 · η MAE = 0.150 V.** Statistically identical to
the DFT-geometry-start result (0.900 / 0.149 V), so the model does not need our geometries
at all. Its single error is again Ru/Ir. **0.150 V is the error bar on every prediction
in §3.**

## 3. The predictions (frozen)

| metal | η_MACE | ±1 MAE | vs the unresolved cluster (0.781–0.892 V) | jobs needed |
|---|---|---|---|---|
| **Ni** | **1.200 V** | 1.05–1.35 | **outside** at every point of the interval | 2 (`s0_O`, `s0_OH`) |
| Co | 0.883 V | 0.73–1.03 | **inside** — 9 mV from Mn | 2 (`s0_O`, `s0_OOH`) |
| Cu | 1.373 V | 1.22–1.52 | outside | 4 (`slab`, `s0_O`, `s0_OH`, `s0_OOH`) |

Secondary predictions, also on record: all three are **pls = 2** (`*OH → *O` limited) with
descriptors 2.11–2.60, i.e. out on the weak-O-binding leg beside Mn and Fe — none of them
is a second Cr.

## 4. What to buy, and why it is Ni + Co

**Ni + Co, four concurrent jobs, ~$4.** Not Cu: it needs four slab jobs instead of two,
has no successful `slab.out` at all, and its predicted η sits 0.11 V from Fe's — more
cost, more risk, no more resolving power.

The honest complication is that **no candidate lands in clear space.** Predicted η(Ni) is
0.063 V from Fe's 1.263 and predicted η(Co) is 0.009 V from Mn's 0.892 — both inside the
0.17 V resolution floor. So each new point most likely brings its own unresolvable pair.
That is survivable, and the arithmetic is the reason to prefer n = 7 over n = 6:

| outcome | n | unresolvable pairs | if **all** of them swap | verdict |
|---|---|---|---|---|
| both jobs land | 7 | 3 (Ru/Ir, Ni/Fe, Co/Mn) | ρ = 0.893, p = **0.0123** | **clears comfortably** |
| one metal fails | 6 | 2 | ρ = 0.886, p = **0.0333** | clears, zero margin |
| neither lands | 5 | 1 | ρ = 0.900, p = 0.0833 | fails, as today |

Running both is therefore the hedge, not the indulgence — **and both need it**: Ni and Co
died on the *same* SCF-plateau pathology (Ni `s0_O` stalled flat at 2.1e-4 Ry against
`conv_thr = 1e-6`; Co `s0_O`/`s0_OOH` never converged across three attempts), so neither
is a safe bet alone. Both require the two-stage `degauss` protocol: pre-converge smooth,
then production `degauss` for the energies.

Cost basis is measured, not guessed: the repair campaign ran three concurrent magnetic 3d
jobs for 12.1 h wall at $0.21/hr = **$2.64** (docs/33 §5b). Four jobs ≈ $4 against the
current $8.46 credit.

### 4b. Correction before spending: it is five jobs, not four

Running `adsorbate_qc` over the states we planned to *reuse* found a fourth instance of
the desorption defect, in Ni:

| state | qe_qc | ionic steps | M–O | verdict |
|---|---|---|---|---|
| `Ni_slab/s0_OOH` | TRUSTWORTHY | 39 | **3.080 Å** | **desorbed — must be re-run** |
| `Co_slab/s0_OH` | TRUSTWORTHY | 16 | 1.796 Å | bound; reusable (MACE finds 1.811 Å) |

Ni's `*OOH` ran 39 ionic steps — it is not the barely-moved case Mn and Fe were — and
still ended unbound, while MACE finds a bound minimum at 2.221 Å from all three starts.
So **Ni needs three jobs (`s0_O`, `s0_OH`, `s0_OOH`), Co needs two (`s0_O`, `s0_OOH`)**:
five in total, ~$5.

**The builder's `*OOH` placement is systematically wrong for 3d metals.** It puts the
adsorbate 3.07–3.13 Å out, and from there DFT has now failed on Mn, Fe *and* Ni — and
MACE says Co would fail the same way (builder start → 2.983 Å; pulled-in start → 2.105 Å
at **0.427 eV lower**). Every job commissioned here therefore starts from the MLIP
minimum rather than the builder placement, which is also what rescued Cr's `*O`.

**η itself is unaffected by any of this**, which is worth stating because it bounds the
damage: both Ni and Co are predicted `pls = 2`, so their overpotential is set by
ΔG_O − ΔG_OH and never touches ΔG_OOH. Step 2 leads the next-largest step by 1.47 eV (Ni)
and 1.38 eV (Co), far outside the 0.150 V error bar, so `pls = 2` is not a close call.
The three η-critical jobs are **Ni `s0_O`, Ni `s0_OH`, Co `s0_O`**; the two `*OOH` jobs
buy the complete CHE chain, the ΔG₄ check and the 15-point ΔG MAE, and are the ones to
drop if the box misbehaves.

## 5. The constraint float-tie: measured, and it does not matter

docs/30 §3 found the mid-plane layer was assigned by floating-point rounding, and flagged
that it "does bias the cross-metal η ranking". The distribution is uneven in exactly the
worst way — Cr/Mn/Fe/Cu/Ru/Ir all have 11 free atoms, **Co has 8 and Ni has 7**, so the
two exceptions are precisely the two candidates.

Same metal, same geometries, only the mask changed:

| metal | η (as-shipped mask) | η (canonical 11-free) | Δ |
|---|---|---|---|
| Ni | 1.200 (7 free) | 1.196 | **−0.004 V** |
| Co | 0.883 (8 free) | 0.882 | **−0.001 V** |

**1–4 mV, against a tier resolution of ~0.17 V.** The extra mid-plane atoms are deep in
the slab and their freedom barely reaches the surface chemistry. Two consequences:

1. Ni and Co can **reuse their existing TRUSTWORTHY states** — two jobs per metal, not
   four. This is what keeps the spend near $4.
2. docs/30 §3's concern is largely retired for the η ranking. It remains a real defect
   worth fixing for cleanliness, but it is not contaminating any published number.

Stated caveat: this is MACE's estimate of the mask sensitivity, not DFT's. At 1–4 mV
against a 170 mV floor it would have to be wrong by more than an order of magnitude to
change the conclusion.

## 6. What would falsify what

- **η(Ni) comes back inside 0.78–0.89 V** → the prediction was wrong by ≥ 2 MAE, the
  screener's error bar is worse than 0.150 V, and the sixth point buys less than claimed.
- **η(Ni) ≈ 1.20 ± 0.15 V** → the protocol predicted an unseen material to within its
  stated error, which is a far stronger claim for the screener than any retrospective
  parity, because it is on record here first.
- **MACE's ordering error count exceeds the tolerance in §4** → the R3 gate fails at n = 7
  and the fine-tune becomes the live option again rather than a deferred nice-to-have.
