# 39 — PRE-REGISTRATION: the UMA `omat` head, the one head R0 never tested

**Date frozen: 2026-08-06, before any `omat` number exists.** Committed and pushed prior
to the run; the commit timestamp is the evidence.
**Follows:** [docs/38](38-matched-protocol-parity.md) §5 K · **Amends the R0 protocol of**
[docs/29](29-r0-oc22-reparity.md) §2
**Runner:** `src/dft/mace_uma_protocol.py --backend uma --uma-task omat`
**Scorer:** `src/dft/parity_matched.py`

---

## 1. Why this is being run, and why that is awkward

R0 tested `oc22` (the pre-registered hypothesis), `oc20` (ablation) and `oc25`
(exploratory). It never tested **`omat`**, and `uma_oc22_parity.py --tasks` reaches it
with one CLI argument. docs/38 concluded that leaving it untested was the largest
unpatched hole in the R0 negative, because the claim on the record is the universal
*"no out-of-the-box UMA head ranks rutile OER"* — a claim over all heads, defended by
testing three of them.

**This is a post-hoc addition to a pre-registered protocol, and it is the only one in
the project.** docs/29 §2 and docs/34 were frozen before their results; this was not
planned in either. That is exactly why the criterion below is being frozen and pushed
before the run rather than written afterwards — a post-hoc test with a post-hoc
threshold is not evidence of anything.

The external motivation is Karimitari et al. (arXiv:2605.09394) Table 4, which puts
UMA/OMAT at **0.243 eV** on metal-oxide reaction energies — the best out-of-box number
in that table, and ahead of MACE-MP-0 (0.466) and MACE-MH-1/OMAT (0.322). A judge who
reads that paper asks this exact question. Note the caveat that paper carries and docs/38
records: its metal-oxide set is **iridium** oxide, and it explicitly *excludes*
partially-filled-3d elements because they need Hubbard U — which is five of our seven
tier metals. So the transfer to our chemistry is an assumption, not a finding.

## 2. Protocol — identical by construction, not by discipline

The run uses **the same runner** as the matched MACE run (`mace_uma_protocol.py`), with
only the calculator swapped via `--backend uma --uma-task omat`. This matters: the three
`.in` files that were replaced after the July UMA campaign (`Cr_slab/s0_O`,
`{Mn,Fe}_slab/s0_OOH`) are restored from their dated archive suffixes by the runner's
`ORIG` table, so `omat` sees exactly what `oc22` saw in July and exactly what MACE saw in
docs/38. Matching is a property of the code path, not of my remembering to match.

Frozen settings: original builder `.in`, **single start**, as-shipped `FixAtoms` masks,
ASE BFGS `fmax = 0.05` / 300 steps, gas references from `ase.build.molecule` in a 12 Å
cubic cell relaxed **by the same model and same head**, `uma-s-1p2`, CPU, and scoring
against `eta_bounded.reference_tier()` — the repaired n = 7 tier.

## 3. THE ACCEPTANCE CRITERION (frozen)

> **`omat` meets the gate iff Spearman ρ ≥ 0.80 AND exact two-sided permutation
> p < 0.05, at n = 7, against the repaired tier.**

That is the identical bar MACE-MPA-0 cleared (+0.857, p = 0.0238) and the identical bar
docs/28 §7 set for R0. No other statistic decides it. In particular I am **not** free to
fall back on MAE, on the descriptor correlation, on a subset of metals, or on the n = 5
cut if ρ lands awkwardly — those are all reported, none of them is the gate.

**Secondary quantities reported regardless, deciding nothing:** η MAE, the n = 5
chain-complete cut, per-state M–O final distances and desorption flags, BFGS step counts
and final `fmax`, and the raw gas-phase `E_H2O` / `E_H2`.

## 4. What each outcome means — decided now, not later

**If `omat` MEETS the gate (ρ ≥ 0.80, p < 0.05):**
R0's headline claim is **falsified** and must be rewritten, not softened. The correct
statement becomes "the oc20/oc22/oc25 heads do not rank this chemistry; the `omat` head
does, and R0 tested the wrong three heads." docs/26, docs/29 and docs/38 §4 all get
amended. This does **not** invalidate the screen — the screen is built on MACE, whose
validation stands independently — but it does mean the *model-selection narrative* is
wrong, and the honest framing becomes "two foundation models rank this chemistry" rather
than "MACE does and UMA cannot." I commit to publishing this outcome as prominently as
the negative, because a pre-registration that only reports one direction is worthless.

**If `omat` FAILS the gate:**
R0 stands and is strengthened — four heads tested, none reaching the bar, including the
one with the best published oxide number in the literature. docs/38 §4's "may claim"
list gains its strongest member.

**If the run does not complete** (gated weights, dependency conflict, non-convergence,
cost): that is reported as an attempted-and-blocked result with the blocker named. It is
**not** quietly dropped, and it does not become "we chose not to test omat."

## 5. Known risks, named before the run

1. **OMat24 contains no gas-phase molecules.** The `omat` head is being asked for H₂ and
   H₂O in a 12 Å box, which is severely out of distribution. A wild gas energy is a
   *predicted* failure mode, not a surprise, and the raw values are reported. Note the
   partial protection: `e0_stage0.py` proves the CHE chain is closed against any
   *per-element* shift (max |Δη| = 3.6e-15 eV), so a systematic per-element error in the
   gas references cancels exactly — but a molecule-specific error does not.
2. **`omat` emulates PBE/PBE+U VASP total energies on bulk inorganic materials** — the
   right functional family for us, but with zero adsorbate and zero surface training.
   That cuts both ways and is the reason this is worth testing at all.
3. **Environment.** `fairchem-core` pins `torch~=2.8`; this machine runs torch 2.11 with
   mace 0.3.15, the environment that produced docs/37 §3's bit-exact CPU↔GPU parity.
   fairchem goes in an **isolated venv**; the main environment is not touched.
4. **Licence.** UMA weights are gated. FAIR Chemistry License v1 §1(b)(ii) requires
   acknowledging Meta's UMA materials in any publication of results obtained with them —
   an obligation the project is already under from R0, and which the STS report must
   carry.

## 6. Result — `omat` MEETS the gate, and R0's headline claim is FALSIFIED

**Run 2026-08-06, ~9 min laptop CPU, $0.** Criterion frozen in commit `e084af8` at
07:46:27−04:00; the run started after it. Artifacts: `results/r5_matched_omat.json`,
`docs/figs/parity_matched.{json,png}`.

| model / head | n=7 ρ | exact p | η MAE | **gate** | n=5 ρ | p | gate |
|---|---|---|---|---|---|---|---|
| **uma-s-1p2 / `omat`** | **+0.964** | **0.0028** | **0.125 V** | **MET** | **+1.000** | 0.0167 | **MET** |
| mace:medium-mpa-0 | +0.857 | 0.0238 | 0.173 V | MET | +0.900 | 0.0833 | NOT MET |
| uma-s-1p2 / `oc25` | +0.357 | 0.4444 | 0.438 V | — | +0.400 | 0.5167 | — |
| uma-s-1p2 / `oc22` | +0.321 | 0.4976 | 0.630 V | — | 0.000 | 1.0000 | — |
| uma-s-1p2 / `oc20` | −0.036 | 0.9635 | 0.651 V | — | −0.300 | 0.6833 | — |

`omat` clears the frozen criterion on both the headline and every secondary quantity,
and it holds at n = 5 where MACE does not. The orderings:

```
DFT :  Cr < Co < Ir < Ru < Mn < Ni < Fe
omat:  Co < Cr < Ir < Ru < Mn < Ni < Fe     <- ONE adjacent swap, on a 53 mV DFT gap
mace:  Cr < Ru < Co < Ir < Ni < Mn < Fe     <- four
```

**Per §4, the outcome is therefore: R0's headline claim is falsified and must be
rewritten, not softened.** "No out-of-the-box UMA head ranks rutile OER" was always a
claim over *all* heads defended by testing three of them, and the untested one is the
best model on this tier the project has measured. In hindsight `omat` is the obvious
head to have tried: OMat24 is PBE/PBE+U VASP energetics on bulk inorganic materials —
the same functional family as our QE PBE+U reference — whereas R0 reasoned entirely
about *adsorption* datasets and never considered that a bulk-energetics head might
transfer better.

### 6a. The `*OOH` problem, which does not rescue R0

`omat` **desorbs `*OOH` on 5 of 7 metals**: Cr 3.778, Mn 3.835, Fe 4.012, Co 3.906,
Ni 3.857 Å, against our 3.00 Å cut. That is far worse than MACE under the same protocol
(Cr 3.013, Mn 3.028, Fe 3.074 — marginal). Only Ru (1.953) and Ir (1.928) held.

But a desorbed `*OOH` corrupts η **only when the potential-limiting step touches
ΔG_OOH**, i.e. `pls ∈ {3, 4}`. Of the five, four are `pls` 1 or 2:

| | Cr | Mn | Fe | Co | Ni | Ru | Ir |
|---|---|---|---|---|---|---|---|
| `pls` | **3** | 2 | 2 | 2 | 1 | 3 | 3 |
| `*OOH` desorbed | ✗ | ✗ | ✗ | ✗ | ✗ | — | — |
| η contaminated | **YES** | no | no | no | no | no | no |

**Exactly one η is contaminated — Cr.** Six of seven are well-founded, so the desorption
finding cannot be used to wave the gate result away. `parity_matched.py` now records
`desorbed_OOH` and `eta_contaminated` separately, because "QC flag" and "this number is
wrong" are different claims.

The uncomfortable direction deserves the same honesty: **Cr is the one metal `omat`
mis-ranks, and it is the one contaminated point.** Reading Cr's η off its `pls = 2` step
instead (ΔG_O − ΔG_OH − 1.23 = 3.144 − 1.445 − 1.23) gives **0.469 V against a DFT
0.491 V**, a 22 mV error, and would make the ranking *perfect*. **This is post-hoc
arithmetic and it is not the gate** — §3 forbids exactly this kind of substitution, and
the gate is already met without it. It is recorded as an observation, and as the reason
a properly-constrained `*OOH` re-run would be interesting rather than decisive.

### 6b. Risk 1 materialised and did not matter

As predicted in §5, the gas references are shifted: `E_H2O` = −14.1961, `E_H2` = −6.6497
eV, against MACE's −13.7861 / −6.5185. The ranking is unaffected, consistent with
`e0_stage0.py`'s closure proof absorbing the per-element component exactly.

### 6c. What this changes, and what it does not

**Does not change:** the screen, the ranking, or the melt list. All rest on MACE, whose
validation stands independently and by three separate routes (docs/38 §2). No candidate
moves.

**Does change:** the model-selection narrative, and docs/26 / docs/29 / docs/38 §4.

**The tension worth writing up rather than resolving:** `omat` ranks this tier better
while being *worse* at keeping adsorbates bound. The tier is forgiving because 5 of 7
metals are `pls ≤ 2`, so most η never touch the leg `omat` fails. **The HEA screen is
not forgiving** — docs/37 found 6 of 12 candidates chemically invalid from precisely
this failure mode, and screened candidates span `pls` 1–4. "Ranks the endmembers better"
and "is the better screener" are different claims, and only the first is established.

**Recommendation: do not re-screen on `omat`.** It re-opens a gate already met, ten
weeks from freeze, on a model that desorbs the `*OOH` leg on 5 of 7 known systems. The
right use of this result is in the write-up, as a corrected negative and an honest
account of how a pre-registered test overturned the project's own prior conclusion.
