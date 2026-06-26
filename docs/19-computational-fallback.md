# 19 — Fully-computational fallback ideas (the hedge)

Insurance in case the wet-lab loop slips (potentiostat never booked, melts come out
multi-phase, or the ~3.5-month clock runs out). [docs/18](18-competitive-benchmark.md)
is blunt about the risk: an ML screening study *without* validation places at **Scholar**
(Hirshorn '26). So a compute-only pivot must clear the bar the computational Finalists
cleared — **a new method that proposes a discovery and validates it** (ScGAN '23 is the
template), benchmarked against published baselines.

## Design rules for any fallback here
1. **Reuse the existing stack** to fit a solo runway — your flow-matching generative CSP
   ([[project_symmc_flow]]), MLIP dynamic-stability work ([[project_mlip_dynstab]]), the
   UMA HEA-OER pipeline already built, and PXRD-diffusion ([[project_pxrd_diff]]).
2. **But ship a *distinct new* project**, not a re-submission of symmc-flow / mlip-dynstab /
   pxrd-diff / OptiGrain — those are being published/commercialized elsewhere, which muddies
   STS independence and triggers prior-work disclosure. **Reuse the *skills & tooling*, not the
   papers.** (Confirm STS prior-publication rules before adapting any solo-authored existing line.)
3. **No lab.** **DFT-validatable in-house** — you run VASP/QE, so a DFT campaign substitutes for
   the missing experiment (this is exactly how a pure-compute project earns Finalist credibility).
4. **Graceful degradation preferred:** the computation *already done* for the HEA project should
   feed the fallback, so hedging costs ≈ 0 and even *strengthens* the main project if the melt happens.

## Ranked ideas

### 1 — (Primary) Generative inverse design of HEA OER catalysts, physics-validated
The ScGAN template, in your domain. Build a **conditional generative model** (flow-matching /
diffusion — your symmc-flow skillset) over the composition simplex, conditioned to target the OER
**volcano apex + single-phase + earth-abundance**. Generate candidates → **validate in-silico with
UMA** (your existing evaluator plays the "classifier" role ScGAN used) → **DFT spot-check** the top
hits. Report hit-rate vs. random/heuristic baselines, novelty fraction, and a held-out check.
- **Novelty:** multi-objective conditional generative inverse design for HEA *oxide* electrocatalysis,
  validated by a foundation MLIP + DFT (a closed *computational* design→validate loop).
- **Reuse:** ~everything already built (UMA pipeline, phase-stability gate, the ranked sweep data as
  training/eval) + your generative stack. **Net-new:** the conditional generator + the benchmark.
- **Validation:** UMA + in-house DFT — no lab.
- **Ceiling:** **Finalist-credible** (matches the placed template); needs zero fabrication.
- **Hedge cost:** near-zero — it consumes the HEA computation you already have, and doubles as the
  round-2 *proposer* if the experiment proceeds.

### 2 — (Primary alt / safest) Foundation-MLIP calibration & uncertainty for OOD oxide catalysis
Turn the honest caveat (UMA's OC20 head is metal-dominated → oxide adsorption is out-of-distribution)
into the contribution. Systematically benchmark **UMA vs. your DFT** on \*OH/\*O/\*OOH across the
rutile HEA surfaces; quantify error vs. composition/coordination; build a **calibration + uncertainty
correction**; show it *measurably improves the screening ranking*.
- **Novelty:** a calibration/UQ framework for foundation-MLIP catalysis screening — very current
  (foundation models are everywhere) and methodologically rigorous.
- **Reuse:** the whole pipeline. **Net-new:** a DFT validation campaign (you run it) + the calibration model.
- **Ceiling:** strong **Scholar**, **Finalist** if breadth/framing is sharp. Pure benchmarks can read
  incremental → strongest when **fused with #1** ("generate → validate → calibrate" = one complete story).
- **Hedge cost:** lowest — it salvages the *exact* work already done.

### 3 — (Higher "so what", higher risk) RE-free permanent-magnet inverse design, DFT-validated
Highest national-importance hook (critical materials / supply chain / defense — [docs/02](02-sts-materials-landscape.md)
takeaway #5; ties to [[project_fe_sma_paper]] Fe-alloy work). Inverse-design earth-abundant magnet
compositions (Fe-Ni-X, tetrataenite-adjacent); screen with MLIPs; validate with **spin-orbit DFT for
magnetocrystalline anisotropy** (you run it); stability via your MLIP dynamic-stability skills.
- **Novelty:** generative RE-free magnet design + first-principles MAE validation.
- **Reuse:** generative + MLIP-stability skills. **Net-new physics:** SOC-DFT for MAE is genuinely
  hard and **slow** — real time-risk in 3.5 months.
- **Ceiling:** **Finalist** if it lands; **highest risk** of the four. Different domain = diversifies
  away from catalysis but abandons the graceful-degradation advantage.

### 4 — (Method companion) A transferable descriptor/surrogate for HEA active-site distributions
Generalize the "active-site *distribution*" idea into a reusable tool: a GNN that predicts the
**distribution** of cus-site adsorption energies from local chemistry, trained on UMA labels,
DFT-anchored — so future HEAs are screened without a full UMA campaign.
- **Ceiling:** Scholar–Finalist (a methods contribution); best as a **companion to #1/#2**, not solo.

## Recommendation
Run **#1, fused with #2** as the primary hedge: *generate → validate (UMA) → DFT-calibrate*. It is
the placed STS computational template, reuses ~all of the HEA work, needs no lab, and you can
DFT-validate it yourself. It also **strengthens the main project** if the experiment happens (a
generative round-2 proposer + a DFT-calibrated screen are upgrades to [docs/16](16-project-overview.md),
not throwaway work). Hold **#3 (magnet)** as the "different domain, higher ceiling, higher risk"
option only if you want to diversify out of catalysis.

## How the hedge integrates (don't fork your effort)
The same computation feeds both outcomes. **Decision point = the [docs/12](12-catalysis-hea-execution-plan.md)
§10 Week-9 go/no-go:** if there is no clean experimental η by then, pivot the write-up to #1+#2 —
the UMA screen you already ran becomes the evaluator/training set for a generative+calibrated
*computational* discovery paper, with your DFT as the gold-standard validation in place of the lab.

> Bottom line: you do **not** have to choose now. Keep doing the shared computation; the fork only
> happens at Week-9, and either branch reuses everything built to date.
