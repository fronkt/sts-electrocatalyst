# STS electrocatalyst: current project review

Review date: October 7, 2026. Live scheduler snapshot: **19:05:40 EDT / 23:05:40 UTC**. The timestamp applies to operations; scientific results below retain their own dates. See the [paper-report foundation](report-foundation-2026-10-07.md) for the writing workspace.

## Short overview

The project investigates reliable computational screening of multicomponent alloys for the oxygen evolution reaction (OER), with a planned alloy fabrication and electrochemical validation loop. Machine-learned interatomic potentials (MLIPs) screen adsorption sites; Quantum ESPRESSO density functional theory (DFT) tests energies and numerical behavior; Fort Wayne Metals and Purdue provide the proposed fabrication and measurement route.

The strongest completed contribution is presently methodological. The investigation exposed structural traps, symmetry restrictions, chemical changes in nominal adsorption intermediates, and sensitivity to Hubbard U and projector conventions. The silentgate output auditor and a complete external adsorption-output census provide a bounded, testable central result. Candidate performance is still a prediction: the reviewed records do not contain completed alloy OER measurements or a validated superior alloy. Sources: [current claim ledger](../45-error-ledger.md), [S2 scientific readout](../research/s2-scientific-readout-2026-09-18.md), [S8 proposal](../research/s8-stage1-freeze-proposal-2026-10-07.md).

## What is running

| Work | Verified state | Meaning |
|---|---|---|
| Anvil array 21176478, arm-C full rerun | **16 RUNNING, 17 PENDING (Priority), 0 terminal** at 19:05 EDT | 31 failed SCFs receive their one allowed rerun; two slab controls test the changed mixing-history recipe. Each task has 128 cores and a 2.5 h limit; total ceiling 10,560 CPU SU. |
| Original arm-C arrays 21165189 / 21165190 | Terminal | Main: 33/64 SCFs accepted; probe: one accepted and one failed. Combined cost 10,876.7 CPU SU. |
| P-A O1 21159532 | Terminal, COMPLETED; CONTINUITY_PASS | One stop/resume boundary passed its prospective, precision-referenced tolerances. |
| Same-state probe 21157910 | Terminal, FAILED 3:0; PR1/PR2 INCOMPLETE | One repeat was excluded by the unchanged IEEE_INVALID failure rule. |
| Relevant local scientific processes | No project watcher or calculation detected by the process query | Only this review's two pythonw snapshot helpers matched. This is a command-line-based process inventory, not proof that every possible alias or external machine is idle. |
| Other Anvil jobs for x-fcai3 | None in the account-wide squeue snapshot | No other queued or running scheduler job appeared at the snapshot time. |

The live allocation query reported **24,298.3 CPU SU** and **150 GPU SU** remaining. The CPU figure is the allocation tool's reported balance; running-job charges can lag. Scheduler observations are not convergence/QC verdicts, and an empty receipt set at this early snapshot does not diagnose a calculation failure.

Evidence: [live scheduler/accounting/QC snapshot](../../results/project_review_2026-10-07/status_snapshot_20261007T230537Z.json), [local process snapshot](../../results/project_review_2026-10-07/local_processes_20261007T230537Z.json), [original arm-C readout](../../results/arm_c_2026-10-07/readout.json), [O1/probe readout](../research/pa-o1-and-repro-probe-readout-2026-10-07.md). No new scientific calculation or scheduler mutation was part of this review.

## Completed scientific evidence

| Result | Evidence and interpretation | Main limitation |
|---|---|---|
| Tested output detector | 9/9 positive controls under the ALL rule; 0/11 QE and 0/500 OC20 persistent-atom-lock detections under the separate ANY negative rule; 138 integrated tests and four hosted CI jobs passed in the recorded implementation verification. | These different quantifiers and control populations cannot be pooled into a single accuracy estimate. Exact printed zero is the instrument's evidence, not a universal test for unconstrained dynamics. |
| External Xu corpus | Complete 810-output corpus: 70/810 have nontrivial symmetry headers. The final-force clause retains 626 outputs: 50 successes, 496 known failures, 80 unknown; four of the original 630 have no force block. The detector identifies 50 LOCKED outputs, all four-layer. The combined registered high-exposure prediction is FALSIFIED; the named directional-pair clause holds for 10/10 metals. | Header exposure, final-force-clause success, and all-step LOCKED classification are separate quantities. Detected locks are a lower bound; the force-clause bounds are 7.99–20.77%. Four-layer concentration is a job-class association, not a controlled thickness effect; LOCKED does not by itself prove an unstable minimum or a wrong catalyst conclusion. |
| U/projector sensitivity | P-PLS is CONFIRMED, with limiting-step flips in 5/6 metals; Cr/Ir/Mn carry the robust three-member subset. P-PROJ FIRES at a 0.487 V atomic-versus-ortho difference in its named Cr case. The fixed-endpoint P-FLOOR-U metric exceeds 0.10 V in 3/6, scored MIDDLE BAND / NOT MET. | Protocol-, geometry-, spin-, phase- and coverage-conditional method results; not a universal physical catalyst ranking or proof that a scaling floor was broken. |
| BEEF uncertainty | P-BEEF CONFIRMED 3/3 under Ladder B; matched 2,000-member ensembles. | XC-only uncertainty on fixed PBE geometries for the three nonmagnetic test systems; not total prediction error. Execution preceded amendment adoption, as the dated ledger records. |
| Alloy site census | Six retained alloys each have 120 MPA-0 sites: 720 total. OOH desorption occurs at 551/720; 109/720 sites pass the adsorbate-intact policy, versus 72/720 strict-intact sites. Broader sampling and admission/statistic choices change the proposed ranking. | Descriptive calibration, not a registered prediction test or electrode validation. Multiple sites within a decoration are not independent material batches. |
| Restart continuity | O1's maxima are 1.69e-7 Ry in energy, 6.40e-5 bohr in position, and 8.74e-5 Ry/bohr in force. Its lost-history negative control exceeds each tolerance after a step. | Validates one boundary only. The older 21075231 remains INCONCLUSIVE; O1's passing verdict uses different, prospectively measured tolerances. |

Primary sources: [detector verification](../../results/silentgate_core_2026-09-13/verification.json), [Xu census](../../results/s2_2026-09-18/xu_census.json), [A0 sensitivity readout](../figs/a0main_readout.json), [projector readout](../figs/pproj_readout.json), [S2 interpretation](../research/s2-scientific-readout-2026-09-18.md), [BEEF readout](../../results/s5_beef_2026-09-17/readout.json), [full site census](../95-census-2-3-readout-2026-09-13.md), [site-level data](../../results/site_census_2026-09-06/readout_full/per_site.csv).

The historical Cr correction matters. Repairing Cr’s trapped *O geometry moved the endmember descriptor from 1.726 V to 0.491 V; a subsequent *OOH electronic-basin repair moved it to 0.330 V, reversing its position relative to Mn and Fe. These distinct repairs changed the reference values and ranking; today’s small restart differences do not make the earlier structural and electronic-basin errors harmless. The repaired panel’s preference for Cr over Ir/Ru also limits its interpretation as experimental activity. See [Cr repair verdict](../32-anchor-gate-verdict.md), [anchor diagnosis](../41-prereg-anchor-offset-diagnosis.md), and [ranking adequacy](../candidate-ranking-adequacy-2026-09-06.md).

## Arm C: present scope and missing results

The approved and launched arm is **C-FG: DFT+U single points at fixed MLIP census coordinates**. Earlier roadmap/melt-plan language about production relaxations describes a different prospective scope. C-FG descriptors do not establish DFT-relaxed minima.

| Alloy | Original C-FG value (V) | Disposition before rerun |
|---|---:|---|
| Cu8Cr23Mn35Co34 | — | NO_VALUE on its p10 support sites; its separate best-site audit is complete |
| Ni31Cr29Cu5Mn35 | 0.768 | SINGLE_SITE fallback |
| Fe25Co25Ni25Cr25 | — | NO_VALUE |
| Cu26Ni9Cr31Co33 | — | NO_VALUE |
| Cu22Fe30Co32Mn15 | 0.942 | SINGLE_SITE fallback |
| Ni34Fe6Cu29Co31 | 1.281 | SINGLE_SITE fallback |

Only 4/16 sites have all four accepted states. **K1, K2 and the Ni34 nomination are NOT_EVALUABLE_UNDER_ARM_C.** Of 31 failed states, 28 hit the 126-iteration ceiling and three were rejected for IEEE notes. The rerun changes mixing_ndim to 16 for ceiling cases and repeats IEEE cases identically; failures remain failures if that one rerun fails. Recipe controls measure energy/moment changes where both recipes converge. A second solution or a mixed recipe can affect comparisons, so convergence alone does not settle the ranking. Sources: [approved arm-C design and terminal/rerun amendment](../research/s8-arm-c-dft-design-2026-10-07.md), [original readout](../../results/arm_c_2026-10-07/readout.json), [rerun plan](../../results/arm_c_2026-10-07_rerun/rerun_plan.json).

## Experimental status

The five-alloy S8 set is **proposed, not frozen or deposited**: Cu8Cr23Mn35Co34, Ni31Cr29Cu5Mn35, Fe25Co25Ni25Cr25, Cu26Ni9Cr31Co33, and the predicted-poor Cu22Fe30Co32Mn15 anchor. Same-bench IrO2 is the planned reference. Arm A uses historical best-of-12-site predictions; arm B proposes the adsorbate-intact p10 from 120 sites; arm C supplies fixed-geometry DFT-informed predictions if it becomes evaluable and is deposited before measurement.

The main test is informative: arm A puts Ni31 and Fe25 ahead of Cu8; arm B puts Cu8 ahead of both. Both place Cu22 last. The set tests disagreement between predictions; it does not presently establish alloy superiority.

The latest confirmed electrode geometry is a **5.00 mm diameter, 1.5 mm thick disk**, mounted and polished flush with epoxy covering the sides/back; exposed area approximately 0.196 cm². The proposed design has at least three mounted coupons plus a bare EC-MS candidate per alloy. Coupons from one ingot measure electrode variability; they do not replicate independent ingot fabrication. The lab accepts stationary mounted coupons and has IrO2. Measurement dates, throughput, scan rate, the final endpoint/SOP, oxygen measurement, and mentor signatures remain open in the reviewed records. EC-MS is a possible oxygen measurement route, not a confirmed completed measurement. Sources: [freeze proposal](../research/s8-stage1-freeze-proposal-2026-10-07.md), [latest melt/electrode plan](../research/s8-melt-plan-2026-10-07.md), [weigh sheet](../research/s8-weigh-sheet-2026-10-07.md), [risk-assessment status](../research/s8-cr6-risk-assessment-2026-10-07.md).

## Remaining scientific work

1. Collect the terminal rerun evidence, retain each failed attempt, apply the existing substitution/readout rules, and examine both recipe controls before any arm-C ranking/deposit.
2. Settle and deposit S8's outstanding experimental values and predictions before the corresponding measurement boundary; reconcile older C-REL wording with the actually elected C-FG scope. Complete the existing laboratory risk-assessment and logistics requirements.
3. Complete fabricated-composition/phase checks and the adopted electrochemistry/oxygen endpoint before making a measured OER claim. Resolve coupon-versus-independent-ingot replication at the scope appropriate to the intended claim.
4. Keep unfinished external-literature and blind DFT-label branches explicit. The current literature reconciliation has 178 eligible, 89 NEEDS_SI and 121 UNRESOLVED records among 2,496 reconciled records; these are workflow dispositions, not a coded literature-exposure prevalence. The separate 45-case failure benchmark remains PENDING with zero adjudicated truth/evaluable cases in its three splits; C-FG SCF counts do not fill those truth labels.
5. Begin the report from the completed detector/census result and its registered sensitivity tests. Add alloy results at their actual completion/uncertainty level. The withdrawn 0.223 V / 25-times / 9 meV headline and superseded pre-repair plots are unsuitable as current findings.

Sources for unfinished branches: [current literature dispositions](../../results/s2_2026-09-25/full_text/reconcile/current_state.json), [failure-benchmark standing](../../results/hea_validation_2026-09-07/benchmark_pending_report.json), [claim/evidence ledger](../45-error-ledger.md). This review scopes existing obligations and does not authorize new compute, samples or external messages.
