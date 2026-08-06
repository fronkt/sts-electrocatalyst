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

## 6. Result

*(To be filled after the run. If this section is still empty in a later commit, the run
did not happen and nothing may be claimed about `omat`.)*
