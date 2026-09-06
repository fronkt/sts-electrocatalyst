# 37 — The screen ran, and activity and stability came out anti-correlated

**Date:** 2026-08-05 · **Spend: ~$0.25** (Vast Tesla V100, 46909320, ~1 h 40 m incl. setup;
**instance destroyed, 0 active**) · **Follows:** [docs/36](36-screen-validation-and-stability-gate.md)
**Artifacts:** `results/r4_screen_box.json` (12 candidates) · `results/r4_gated.json` ·
`results/r4_melt_list.json` · `results/box/shard_*.{json,log}`
**Code:** `screen_mace.py --shard/--device` · `pourbaix_multi.py gate` · `melt_list.py build`

---

## 1. The screen

12 diverse single-phase candidates (3339/4000 sampled compositions cleared the
Hume-Rothery/Ω–δ filter), each scored at its best of **12 cus sites — 4 sites × 3
independent decorations**, every adsorbate state relaxed from 3 starts.

| composition | η_best | site spread | site mean | descriptor | pls | flags |
|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | **0.440** | 0.324 | 0.910 | 1.499 | 1 | |
| Fe25Co25Ni25Cr25 | **0.453** | 0.329 | 1.047 | 1.683 | 2 | |
| Cu26Ni9Cr31Co33 | **0.479** | 0.273 | 0.916 | 1.615 | 1 | |
| Cr33Co5Ni29Cu33 | 0.515 | 0.194 | 0.895 | −0.270 | 3 | **desorbed** `*O`,`*OOH` |
| Mn31Ni31Co33Cu6 | 0.668 | 0.214 | 1.016 | 0.673 | 1 | **desorbed** `*OOH` |
| Fe31Cu25Cr13Ni31 | 0.677 | 0.354 | 1.077 | −0.019 | 1 | **desorbed** `*O`,`*OOH` |
| Ni34Fe6Cu29Co31 | 0.726 | 0.194 | 1.001 | 0.187 | 4 | |
| Mn34Cu7Fe33Cr27 | 0.736 | 0.209 | 1.106 | −0.213 | 1 | **desorbed** `*O`,`*OOH` |
| Co5Cu33Ni28Mn34 | 0.745 | 0.347 | 1.088 | 0.738 | 1 | **desorbed** `*OOH` |
| Cu8Cr23Mn35Co34 | 0.756 | 0.135 | 1.058 | 1.986 | 2 | |
| Cu22Fe30Co32Mn15 | 0.796 | 0.184 | 1.088 | 2.026 | 2 | |
| Ni34Fe29Mn30Co7 | 0.872 | 0.320 | 1.334 | −0.691 | 1 | **desorbed** `*O` |

**Half the pool — 6 of 12 — is chemically invalid**, and the QC that caught them is the
machinery docs/36 §2 was written to add. Note what would have happened without it: four
of the six carry a *negative* descriptor (ΔG_O < ΔG_OH), which is not a volcano position
at all, and one of them (Cr33Co5Ni29Cu33 at 0.515 V) would have ranked **fourth-best in
the whole screen** on an η computed from a state that never adsorbed. The desorption
flag is doing exactly the job the campaign paid $2.64 to learn it needed.

**The site spread is the headline physics.** Across the clean candidates the best site
runs **0.44–0.60 V below the site mean**. Screened by average site, every one of these
compositions is unremarkable; screened by favourable tail, three of them sit below every
rutile endmember in the DFT tier. That gap *is* the high-entropy hypothesis, and it is
only visible because sites are pooled over 3 decorations — for Fe25Co25Ni25Cr25 the
winning site came from seed 2, which a single-decoration screen would never have built.

## 2. Activity and stability are anti-correlated

Joining the multi-element Pourbaix gate (docs/36 §4) onto the ranking, over the 6
chemically clean candidates:

| composition | η_best | soluble cations @ pH 14, 1.53 V |
|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.440 | **94.8 %** |
| Fe25Co25Ni25Cr25 | 0.453 | 50.0 % |
| Cu26Ni9Cr31Co33 | 0.479 | 40.9 % |
| Ni34Fe6Cu29Co31 | 0.726 | 33.9 % |
| Cu8Cr23Mn35Co34 | 0.756 | 57.6 % |
| Cu22Fe30Co32Mn15 | 0.796 | **15.5 %** |

**Spearman ρ(η, soluble) = −0.657, exact two-sided p = 0.175, n = 6.**

The most active candidate dissolves almost completely; the least active is six times more
durable. That is the activity/stability scaling relation this project exists to try to
break, reproduced inside the HEA design space rather than assumed from the literature.

**It is not significant, and must not be written up as if it were.** At n = 6, ρ = −0.657
gives p = 0.175 — the honest statement is "suggestive, consistent with the known
trade-off, underpowered". Establishing it needs more clean candidates, and half the pool
being rejected is why there are only six.

**A p-value bug was found in the course of measuring it.** `exact_two_sided_p` counted
only the upper tail (`ρ ≥ ρ_obs`) and doubled, which is the correct two-sided p **only**
for positive ρ; on a negative correlation it returned ~1.0. It now measures the tail from
|ρ|. **No published number changes** — verified exhaustively against the pre-fix
implementation over every attainable ρ at n = 5, 6, 7, and docs/33/34/35's four quoted
p-values (0.0833, 0.0333, 0.0167, 0.0238) all reproduce exactly. Every prior use was on
the positive R0/R3 gate, where `abs()` is the identity.

## 3. Cross-platform parity, which replaces a planned re-validation

The plan was to re-run the endmember validation on the box before screening there. Two
candidates ended up running on **both** platforms instead, which tests the same thing on
the real workload rather than a proxy:

| | η (laptop) | η (V100) | Δη | spread (laptop) | spread (V100) | Δ |
|---|---|---|---|---|---|---|
| Fe25Co25Ni25Cr25 | 0.4531 | 0.4531 | −0.0000 | 0.3286 | 0.3286 | −0.0001 |
| Co5Cu33Ni28Mn34 | 0.7448 | 0.7448 | +0.0000 | 0.3460 | 0.3466 | +0.0005 |

**η identical to 4 decimal places** across 8-core CPU ↔ Tesla V100, mace 0.3.15 ↔ 0.3.16,
both float64; desorption verdicts identical. Choosing a Volta card specifically for 1:2
FP64 — so the screen kept exact numerics parity with the float64 gate — is what makes
this clean.

## 4. The melt list

Pareto front over (activity, stability), plus the anchors a correlation study needs:

| role | composition | η_pred | soluble | $/kg |
|---|---|---|---|---|
| activity end | **Ni31Cr29Cu5Mn35** | 0.440 | 94.8 % | 9.47 |
| interior front | **Fe25Co25Ni25Cr25** | 0.453 | 50.0 % | 15.20 |
| interior front | **Cu26Ni9Cr31Co33** | 0.479 | 40.9 % | 17.98 |
| stability end **+ poor anchor** | **Cu22Fe30Co32Mn15** | 0.796 | 15.5 % | 13.10 |
| ablation (carried from docs/15) | **FeCoNi** | — | 33.3 % | — |

**Two limitations, both structural, both stated rather than designed around:**

1. **Role collapse.** The least-active clean candidate is also the most stable, so the
   list has no *independent* low-activity point. Its dynamic range is whatever the Pareto
   front happens to span.
2. **That span is 0.356 V, against a validated screener MAE of 0.130 V** — under 3 MAE of
   range across the whole list. docs/15 §6 is right that a correlation over ~6 points is
   meaningless without dynamic range, and this is thin. The cheap remedy is a wider
   screened pool: the box workflow is now proven end-to-end at **~$0.25 and ~1.5 h for 12
   candidates**, so 24–36 more is a sub-$1 decision, not a research programme.

**Why not a weighted score.** Every candidate measured across docs/36 and this document
is ≥15 % soluble, and activity anti-correlates with stability. There is no
stable-and-active corner for a scalarization to find; a weight vector would just bury an
arbitrary exchange rate and report a winner as though the trade-off were resolved. The
list spans the front so the experiment can measure where the real materials land.

## 5. What this does and does not establish

**Does establish**

- A ranked, chemically-gated, stability-annotated HEA candidate set from a pipeline whose
  ranking was validated against the DFT tier at ρ = +0.857, p = 0.0238, MAE 0.130 V.
- That half of a naively-screened HEA pool is chemically invalid, and that the invalid
  half includes candidates that would otherwise have ranked near the top.
- That the favourable-tail site is 0.44–0.60 V below the site mean — the quantitative
  form of the high-entropy hypothesis — and that pooling decorations is required to see it.
- Bit-level reproducibility of the screen across CPU/GPU and two MACE versions.

**Does not establish**

- **Any measured overpotential.** η here is an ORDERING. docs/34's pre-registered
  out-of-sample test missed η(Co) by +0.339 V, 2.3× the validated bar.
- **That the anti-correlation is real** (p = 0.175, n = 6).
- **That these numbers describe the real electrode.** The screen ranks rutile-structured
  mixed oxides; what gets melted is an fcc metal that reconstructs to an (oxy)hydroxide
  under OER. The oxyhydroxide-termination spot-check (docs/28 §4 M4) is still not done,
  and the rutile tier remains a calibration tier (docs/31 §8.1).
- **Cross-comparison to the endmember tier.** These η are the minimum over 12 sites; an
  endmember has one distinct site. A tail statistic beats a single draw for free.
  "This HEA beats β-MnO₂" does not follow and needs matched sampling.
- **Anything the U-sensitivity ladder might move.** docs/35 §5 stands: the reference puts
  Cr and Co below both noble anchors, Cr/Co carry Hubbard U and Ru/Ir do not, and the
  screen is validated *against that reference*, so it inherits any systematic in it.

## 6. Next

- **Frank's call before freezing:** accept the 0.356 V span, or spend ~$0.50 and ~3 h to
  screen 24–36 more candidates for a genuine predicted-poor anchor. The frozen prediction
  is a scientific commitment; widening it is cheap now and expensive after the melt.
- **Then:** weigh sheet (`src/scripts/weigh_sheet.py`, docs/17) for the chosen set,
  Cr(VI) risk assessment dated **before** the first melt (docs/25) — the gate confirms Cr
  goes to chromate in every Cr-bearing candidate — and the XRD single-phase check at FWM.
- **Still open and unchanged:** STS sponsor of record, and the U-sensitivity ladder.

---

## Dated correction — 2026-09-06: equilibrium annotations and preserved selection

The soluble-cation fractions in section 2 describe an equilibrium assemblage at specified potential, pH and concentration. They do not establish that the highest fraction actually dissolves almost completely, or that the lowest fraction is six times more durable. Those are kinetic/experimental claims that the calculation does not measure. The sampled minimum-to-mean difference does not establish the abundance or turnover of those motifs on an operating electrode.

The banked melt list preserves the earlier selector. The current spacing rule would replace Cu26Ni9Cr31Co33 with Ni34Fe6Cu29Co31; neither set is newly adopted here. The supporting [ranking adequacy review](candidate-ranking-adequacy-2026-09-06.md) compares both versions, preserves the old data, and identifies the validation needed before a prospective melt choice.
