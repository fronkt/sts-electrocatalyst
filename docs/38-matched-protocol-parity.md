# 38 — MACE beat UMA. We had not earned the right to say so.

**Date:** 2026-08-06 · **Spend: $0** (16 min laptop CPU, no GPU, no credit) ·
**Follows:** [docs/37](37-hea-screen-result-and-melt-list.md)
**Artifacts:** `results/r5_matched_protocol.json` · `docs/figs/parity_matched.{json,png}`
**Code:** `src/dft/mace_uma_protocol.py` · `src/dft/parity_matched.py` · `src/dft/oc22_coverage.py`
**Amends:** docs/26 (headline), docs/29 §2, docs/33 §3, docs/34 §2, `mlip_eval.evaluate_relaxed`

---

## 1. The comparison was never matched, and every unmatched axis flattered MACE

R0 rejected UMA; R3 accepted MACE; the screen was built on MACE. That chain is only as
good as the comparison at its head — and until today the two models had **never been
scored the same way in any committed artifact**. Six axes differed, all in one direction:

| Axis | UMA got (docs/26, docs/29) | MACE got (docs/33, /35, /36) |
|---|---|---|
| **DFT reference** | **Defective.** Cr 1.726 V (trapped `s0_O` at 2.016 Å; restart 1.396 eV lower → 0.491 V) and Ni 1.751 V (unconverged, retracted docs/30 §2 → 1.084 V). **Two of four points wrong.** | Repaired reference, repaired frames |
| **n** | 4 → 3 after the docs/30 QC cut → 5 in the docs/29 §8 prose. **Never 7.** | 5 (docs/33), 7 (docs/35, docs/36) |
| **Start geometry** | Builder `.in`, adsorbate 3.06–3.14 Å off the cus metal — past our own 3.00 Å desorption cut. 10–221 BFGS steps. | docs/33: single-points, *and* "relaxations" that start from **DFT-relaxed** frames (`final_frames()`), 5–62 steps. docs/35: `.in` files, **3 of 21 replaced after the UMA run** by MACE-derived and DFT-derived geometries. |
| **Starts per state** | 1 | 3 (builder + rigid pull-in at 1.70 and 2.10 Å); 14 of 21 winners were pull-ins |
| **Precision** | Unrecorded — `uma_oc22_parity.py` never sets a dtype | Explicit `float64` (`relax.py:19`: "float64 matters") |
| **Checkpoint / mask** | `uma-s-1p2` substituted for the pre-registered `1p2p1` (disclosed, docs/29 §4c); Ir anchor 10 free atoms | 11 free (canonical) |

The one axis that *is* matched is the gas-phase CHE chain: 12 Å box, same-model H₂/H₂O
on both sides, and `e0_stage0.py` proves the referencing is stoichiometrically closed to
3.6e-15 eV. That is why no alignment is applied anywhere.

**"UMA scored 0.0 and MACE scored 0.857" was the most attackable sentence the report
could have contained.** It compares two different experiments.

## 2. The matched experiment

`mace_uma_protocol.py` restores the original builder inputs from their dated archive
suffixes and re-runs MACE-MPA-0 under UMA's exact protocol — single start, no pull-ins,
as-shipped `FixAtoms`, BFGS `fmax=0.05`/300 steps, `ase.build.molecule` in a 12 Å box.
`parity_matched.py` then scores **every stored UMA head and this MACE run** against
`eta_bounded.reference_tier()`, the n = 7 tier of record:

| model / head | n | ρ | exact p | η MAE | gate |
|---|---|---|---|---|---|
| **MACE-MPA-0 (UMA's protocol)** | 7 | **+0.857** | **0.0238** | **0.173 V** | **MET** |
| uma-s-1p2 / `oc25` | 7 | +0.357 | 0.4444 | 0.438 V | — |
| uma-s-1p2 / `oc22` *(the pre-registered hypothesis)* | 7 | +0.321 | 0.4976 | 0.630 V | — |
| uma-s-1p2 / `oc20` | 7 | −0.036 | 0.9635 | 0.651 V | — |
| uma-s-1p1 / `oc20` *(docs/26)* | 5 | −0.300 | 0.6833 | 1.083 V | — |

**The conclusion survives matching.** MACE reproduces its published η to **within 5 mV
on all seven metals** from raw builder geometry with a single start, so none of the
protocol advantages was load-bearing — the multi-start is worth ≤3 mV on every tier
metal. MACE now meets the gate by **three independent routes**: the DFT tier's 18-atom
cells (MAE 0.172 V), the screen's own 2×2 Vegard slabs (0.130 V, `r4_validate.json`),
and UMA's protocol (0.173 V).

**Two things the matched run exposes that were not previously stated:**

1. **Under the matched protocol MACE also leaves `*OOH` desorbed** on Cr (3.013 Å),
   Mn (3.028), Fe (3.074) and Co (2.983). η survived only because all four are step-2
   limited. That is luck of the potential-limiting step, not robustness.
2. **The gate is not met at n = 5.** Dropping Ni and Co — whose η come from the bounded
   `*OH`/`*O` identity and whose DFT restarts were commissioned from MACE's own minima
   (docs/34 §4b) — gives ρ = +0.900 at **p = 0.0833**. The two MACE-entangled points are
   what carry significance. `parity_matched.py` reports both cuts by default so this can
   never be quietly dropped again.

## 3. OC22 does not contain our surface

docs/29 §2 justified the whole R0 campaign with "OC22's training set contains 4,318
rutile systems with O\*/OH\*/OOH\* intermediates — our chemistry is *literally* the OC22
dataset." Audited against the real metadata (62,331 systems, `oc22_coverage.py`):

| | count |
|---|---|
| rutile systems | 4,318 ✓ (matches the paper) |
| …at **(110)** | **83** |
| …with `*OOH`, any metal | **1** |
| rutile(110) touching our 8 metals | 19 — 5 with an OER intermediate, **0 with `*OOH`** |
| canonical rutile bulks at (110) — mp-825 RuO₂, mp-2723 IrO₂ | **0** |

The facet we model is a thin slice of OC22 and the `*OOH` leg is essentially absent from
it. This **weakens the confound hypothesis that motivated R0** and correspondingly
**strengthens the R0 negative**: oc22's failure is less surprising once its (110)
coverage is known.

### 3b. The one surviving lead was not rutile either

The audit left exactly one candidate external validation point: **`mp-1095353` (Ir₄O₈)**,
15 OC22 systems at (110) carrying **3 `*OOH`, 3 `*O`, 1 `*OH`** — a complete OER triad on
one of our two anchors. Settled against the MP OPTIMADE record (no API key needed:
`optimade.materialsproject.org/v1/structures/mp-1095353`), symmetry via `spglib`:

| | mp-1095353 | mp-2723 (canonical rutile IrO₂) |
|---|---|---|
| space group | **Pa-3 (205)** — cubic | **P4₂/mnm (136)** — tetragonal |
| a, b, c (Å) | 4.904, 4.902, 4.905 | 3.177, 4.505, 4.505 |
| cell | Ir₄O₈, 12 atoms | Ir₂O₄, 6 atoms |
| O sites | Wyckoff 8c, u ≈ 0.35 (pyrite-type framework) | 4f, the rutile motif |
| Ir–O, Ir coordination | 2.006 Å, 6 | 1.967 Å, 6 |

**It is a pyrite-type cubic polymorph, not rutile** (identical at `symprec` 0.01 and 0.1,
so this is not a tolerance artifact). Its O–O of 2.550 Å is too long for a peroxide
dimer, so it is a pyrite *framework* rather than textbook pyrite — but either way its
(110) facet is not our surface. Rutile(110) exposes the alternating bridging-O rows and
5-fold coordinatively-unsaturated metal sites that this entire project's OER model rests
on; a Pa-3 (110) cut has no such motif. The adsorption energies are not comparable, and
scoring MACE against them would be a **false validation** — the failure mode docs/37 §5
already warns about, arriving through the back door.

**So the audit closes cleanly: OC22 contains no usable external validation for rutile
MO₂(110) OER on any of our metals.** That is a more useful result than a half-comparable
dataset would have been, and it retires "just validate against public data" as an option
rather than leaving it open as a vague possibility.

**Do not publish the symmetric corollary.** "OC22 has no rutile(110), so UMA was judged
out-of-domain" invites the obvious return question, and MACE-MPA-0 trains on MPtrj +
sAlex — bulk crystals with **zero** adsorbates and zero catalytic surfaces. By that
standard our own screener is further out of distribution than the model we rejected. The
defensible claim is the empirical one: on this tier, MACE ranks and UMA does not.

## 4. What may and may not be claimed

> **⚠ SUPERSEDED 2026-08-06 by [docs/39](39-prereg-omat-head.md) §6 — the same day.**
> §5 K listed the `omat` head as the one untested attack on R0. It was tested under a
> pre-registered criterion and **it meets the gate: ρ = +0.964, p = 0.0028, MAE 0.125 V
> at n = 7**, beating MACE (+0.857 / 0.0238 / 0.173 V) and holding at n = 5 where MACE
> fails. **The claim below is false as written and is retained only to show what it
> said.** Correct statement: *the `oc20`/`oc22`/`oc25` heads do not rank this chemistry;
> the `omat` head does. R0 tested three adsorption heads and never tried the bulk-
> energetics head that works.* The screen is unaffected — it rests on MACE, validated
> independently — but the model-selection narrative is not.

**May:** ~~no UMA head tested (`oc20`/`oc22`/`oc25`, on 1p1 or 1p2) reaches the
pre-registered ρ ≥ 0.8 gate on this tier — true against every reference, every n, and
the matched re-run.~~ MACE meets it at n = 7 by three independent routes. And **the MLIP
corrected the DFT on four structures** — Cr `*O` (MACE 1.609 Å vs the DFT restart's
1.572 Å; η predicted 0.500 against a measured 0.491, a 9 mV error on a number the old
reference had wrong by 1.235 V), plus Fe/Mn `*OOH` and the desorbed Ni `*OOH`. That last
claim is the strongest the project owns and it does not depend on any model scoreboard.

**May not:** docs/26's ρ = 0.400 / MAE 0.706 eV, or docs/29's ρ = −0.800, as "UMA's
performance". "Like-for-like" for `evaluate_relaxed`. "No DFT input of any kind" for the
docs/34 run as it was executed. p < 0.05 without the n = 5 disclosure.

## 5. Open, and deliberately not closed here

- ~~**`mp-1095353` (Ir₄O₈)**~~ — **CLOSED NEGATIVE 2026-08-06, see §3b.** It is not
  rutile. There is no free external validation point in OC22.
- **UMA `omat` head, never tested.** `uma_oc22_parity.py --tasks` defaults to
  `oc20,oc22,oc25`; `omat` is one CLI argument away, and Karimitari et al.
  (arXiv:2605.09394) Table 4 puts UMA/OMAT best-in-table on metal-oxide reaction
  energies. It is the only untested attack on R0. **Pre-register the acceptance
  criterion first** — this would be the sole post-hoc addition to a pre-registered
  protocol — or state in one sentence that it was not run and why. Silence is the only
  unacceptable option.
- **The predictor and the target are coupled three ways**, and this is the largest
  untracked risk in the project: (i) MACE-MPA-0 trains on MPtrj, which carries the
  Materials Project selective-U convention, and our QE reference uses MP's U values
  verbatim (`qe_slab.py:34–46`); (ii) both "independent checkpoints" are MPtrj-family,
  so docs/33's "not a lucky checkpoint" is weaker than written; (iii) Ni and Co carry
  significance and are seeded from MACE's own minima. One paragraph naming all three,
  plus the n = 5 row, is the honest fix. The thing that actually breaks the circle is
  the potentiostat.

## 6. What changed in the repo

- **New:** `mace_uma_protocol.py`, `parity_matched.py`, `oc22_coverage.py`,
  `results/r5_matched_protocol.json`, `docs/figs/parity_matched.{json,png}`.
- **Amended:** docs/26 (headline banner — it had never been amended for the repair),
  docs/29 §2 (OC22 coverage), docs/33 §3 (not like-for-like), docs/34 §2 (three starts
  were not builder geometries), `mlip_eval.evaluate_relaxed` docstring.
- **Stamped `SUPERSEDED_BY`:** `uma_dft_parity.json`, `uma_oc22_parity.json`,
  `uma_oc22_parity_qc.json` — all three still publish the retracted `dft_eta`
  Cr = 1.7262460450084243. Their UMA columns are as-measured and correct, so they are
  kept rather than deleted; only the banner is added.
