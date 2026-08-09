# 35 — n = 7: the gate is met, one prediction held, one missed

**Date:** 2026-08-03 → 2026-08-04 · **Instance 46726365 destroyed; credit exhausted.**
**Spend: $8.17** against a $3.20 projection — see §6.
**Pre-registration:** [`34`](34-prereg-sixth-point.md) (frozen before the box was rented)
**Code:** `src/dft/{make_rescue_inputs,run_rescue.sh,eta_bounded,score_n7}.py`

## 1. The result

**The R3 gate is met.** MACE-MPA-0, un-fine-tuned and free, against the DFT tier:

| | ρ(η) | exact two-sided p | η MAE | |
|---|---|---|---|---|
| n = 5 (before this campaign) | +0.900 | 0.0833 | 0.150 V | not met |
| **n = 6 (+Ni)** | **+0.886** | **0.0333** | 0.144 V | **MET** |
| **n = 7 (+Ni, Co)** | **+0.857** | **0.0238** | 0.172 V | **MET** |

This is the shape docs/34 §1 predicted: **the binding constraint was n, not the model.**
The screener carries exactly the errors it always had; adding data points made the same
performance statistically legible. The $1.9 fine-tune was never the missing piece.

Full tier, ordered by DFT η:

| | ΔG_OH | ΔG_O | descriptor | η_DFT | η_MACE | err |
|---|---|---|---|---|---|---|
| Cr | 1.518 | 3.078 | 1.560 | **0.491** | 0.501 | +0.010 |
| **Co** | 1.774 | 3.382 | **1.608** | **0.544** | 0.883 | **+0.339** |
| Ir | −0.000 | 1.641 | 1.642 | 0.781 | 0.912 | +0.131 |
| Ru | 0.529 | 1.692 | 1.163 | 0.787 | 0.646 | −0.141 |
| Mn | 1.907 | 4.029 | 2.122 | 0.892 | 1.241 | +0.349 |
| **Ni** | 2.314 | 4.556 | 2.243 | **1.084** | 1.200 | +0.116 |
| Fe | 2.134 | 4.627 | 2.493 | 1.263 | 1.381 | +0.118 |

## 2. The pre-registered test: 1 hit, 1 miss

Frozen in docs/34 §3 before any compute was bought, with a validated ±0.150 V bar:

| | predicted | DFT | error | verdict |
|---|---|---|---|---|
| Ni | 1.200 V | **1.084 V** | +0.116 | **HIT** — and the "outside the cluster" call was right |
| Co | 0.883 V | **0.544 V** | **+0.339** | **MISS** — 2.3× the bar, and the cluster call was wrong too |

Co is the worst point in the campaign: descriptor error +0.505 eV against a 0.250 eV MAE.
MACE placed it inside the unresolved 0.78–0.89 V cluster; DFT puts it second-best in the
tier. **An out-of-sample test that only ever confirms is not a test**, and this one did
not — the screener is good enough to rank (ρ = 0.857) and not good enough to trust
point-wise on an unseen metal.

## 3. Both `*OOH` jobs failed, and η did not need them

Ni's `*OOH` diverged three times (SCF accuracy *rising*: 0.0059 → 0.0108 → 0.0161 over
300 iterations, then again on a damped 0.02 Ry rung). Co's ran out of credit at 16 ionic
steps. `dft_reference()` therefore excludes both — correctly, since neither has a
complete, chemically valid chain.

η survives anyway, from an identity rather than an assumption
(`src/dft/eta_bounded.py`):

```
ΔG₃ + ΔG₄ = G_TOTAL − ΔG_O          ← contains no ΔG_OOH
```

So once ΔG_OH and ΔG_O are measured, step 3 or 4 can only be limiting if ΔG_OOH leaves a
computable window:

| | window for ΔG_OOH | width | margin vs the observed 3.65–4.94 eV |
|---|---|---|---|
| Ni | (2.61, 6.87) | 4.26 eV | +1.05 / +1.93 eV — **safe** |
| Co | (3.15, 5.16) | 2.01 eV | +0.51 / **+0.21** eV — tight |

Co's high edge sits only 0.21 eV above the largest ΔG_OOH on record, so the observed-range
argument alone is not enough. Its partial relaxation supplies the missing rigour: **a run
stopped early sits above its own minimum**, so the ΔG_OOH it implies (4.571 eV) is an
*upper bound* on the converged value, and 4.571 < 5.16 closes the edge.

This deliberately avoids the universal scaling relation (ΔG_OOH ≈ ΔG_OH + 3.2 ± 0.2),
which would have been the tempting shortcut. docs/32 §4 measured a **+0.45 eV violation
of that relation for IrO₂ in this very pipeline**; leaning on it here would repeat the
campaign's characteristic mistake. `tests/test_eta_bounded.py` pins the negative control:
Ru is genuinely `pls = 3`, and its true ΔG_OOH falls *outside* the window, so the bound
declines to apply rather than inventing an answer.

## 4. A fourth desorbed `*OOH`, and a trap avoided by one day

`Ni_slab/s0_OOH.out` from the 2026-06 campaign is `TRUSTWORTHY` by `qe_qc` — 39 ionic
steps, converged — and has the adsorbate **3.080 Å off the surface**. It was found by
running `adsorbate_qc` over the states this campaign planned to *reuse*, which is why the
buy became five jobs instead of four.

It is now archived as `.out.desorbed-2026-08-04`. Left in place it would have given
ΔG_OOH = 5.202 eV and **ΔG₄ = −0.282 eV** — thermodynamically impossible, and exactly what
`check_thermo` flags. η(Ni) happens to be unaffected (1.084 V either way, since `pls = 1`),
but that is luck, not design.

Four structures have now passed a purely numerical QC gate while being chemically wrong:
Cr `*O`, and `*OOH` on Mn, Fe and Ni. **In every case the MLIP was closer to the truth
than our own DFT.**

## 5. Two claims that must not be written up yet

**Our DFT puts two 3d rutiles below both noble metals.** Cr 0.491 and Co 0.544 against
Ru 0.787 and Ir 0.781 — inverting the experimental ordering in which RuO₂/IrO₂ are the
benchmark OER catalysts (lit. 0.37–0.42 and 0.54–0.58 V). Cr and Co carry Hubbard U
(3.7, 3.32 eV); Ru and Ir carry none. A cross-family systematic of exactly that shape is
the obvious suspect. **The U-sensitivity ladder is now required, not optional.**

**Neither material is a realizable electrode anyway.** docs/31: CrO₂ has no aqueous
stability window at any pH (it dissolves as chromate), and rutile CoO₂ does not exist in
the Materials Project across 15 catalogued polymorphs. The two most active points in our
tier are the two that cannot be built — which is the activity/stability tension the HEA
thesis exists to attack, and the honest way to frame the tier.

## 6. Ledger, and a 2.5× cost overrun

| | |
|---|---|
| Jobs commissioned | 5 |
| Converged | 3 (Ni `s0_O`, Ni `s0_OH`, Co `s0_O`) — all TRUSTWORTHY |
| Failed | 2, both `*OOH` |
| Broken box (destroyed, machine 129402) | $0.044 |
| **Total spend** | **$8.17** (projected $3.20) |
| Credit remaining | $0.295 |
| Delivered | n = 5 → 7; gate MET at p = 0.0238 |

**Where the estimate went wrong.** I costed the run from the repair campaign's 12.1 h
wall for three concurrent magnetic-3d jobs. Five jobs on a 92-core quota at 18 ranks each
ran ~30 h, not ~12 — stage A alone took 1.7–2.5 h per job before any relaxation started,
and the two-stage protocol doubles the SCF work by construction. I also assumed all five
would converge; two did not, and the failures burned the most time (Ni `*OOH` consumed
17.7 h before failing, then 11 h more on the retry).

The honest read is that **the campaign delivered its objective and I mispriced it by
2.5×.** The three jobs that mattered cost roughly $4 of the $8.17; the rest went to two
`*OOH` jobs whose scientific value turned out to be zero, because the bound in §3 made
them unnecessary. Had I derived that bound *before* renting instead of after, the buy
would have been three jobs and ~$4.
