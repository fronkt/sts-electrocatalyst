# STS operational timeline and phase scope — 2026-10-05

Status basis: 2026-10-05 10:52:43 EDT (14:52:43 UTC). This is a scheduling and scope reference for existing project work. Future windows below are proposed working targets, conditional on scientific gates, exact compute budgets, queue waits and laboratory throughput. They are not booked appointments, new compute approval, a new scientific protocol, or student research-report prose.

## 1. Where we are now

Job **21075231** is RUNNING on Anvil. The continuous control and stopped candidate both have NUMERICAL_RECEIPT_VALIDATED receipts; the isolated fresh electronic calculation is STARTED. Scheduler elapsed time is 72m12s, with approximately **154.03 allocation CPU SU accrued** at the snapshot. These are interim accounting observations, not the final bill or a completed scientific verdict.

The current material is the existing **Cu8Cr23Mn35Co34, seed20/site2, 72-atom clean slab**, at the retained cycle-5 geometry. Quantum ESPRESSO 7.5 uses the pinned spin-polarized DFT+U deck, atomic Hubbard projector, 80/640 Ry cutoffs and unchanged solver/parallel settings. Its role is a numerical restart-boundary validation.

The approved job has one 128-core whole node, 200 GiB, a 16-hour / **2,048-SU** hard ceiling, up to six sequential bounded solver calls, and no automatic retries or requeue. Estimate: **275–543 SU**. It started at 09:40:32 EDT on October 5; the scheduler hard end is **01:40:32 EDT on October 6**. Afternoon completion on October 5 is a planning expectation, subject to the fresh/resume branch; the hard end is the enforceable limit.

Its possible final labels are PASS_ONE_BOUNDARY, RESEED_BRANCH_ONLY, HOLD or INCONCLUSIVE. A pass establishes observed checkpoint consumption and three-step energy/force/geometry continuity at one checked boundary. Full ionic relaxation, every-step checking, a ground-state guarantee, adsorption references and melt ranking remain later gates.

The record of job 21034683 remains FAILED3:0 / scientific INCONCLUSIVE, charged 102.8622 SU. It is preserved independently of the corrected trial.

## 2. End point and parallel work

The current STS claim spine is the completed detector/corpus investigation (S1/S2/S6), with its registered negative findings and limitations. The compute-to-melt lane supplies additional numerical and prospective materials evidence. The program keeps its existing stage scopes and physics exclusions; this calendar does not silently remove stages or revive dead arms.

Writing, figure organization, literature closeout and application administration proceed alongside compute and laboratory work. S8 can contribute one prospective experimental figure if complete by REPORT LOCK. Positive, negative and inconclusive material outcomes all retain their actual scientific labels.

The official submission deadline is **Thursday, November 5, 2026, 8:00 p.m. Eastern Standard Time**. Recommended internal submission target: **November 4**. The project binding REPORT LOCK remains the entrant's dated election, with the November 5 backstop. **October 25 is a proposed working data-lock target**, not an amendment. P-LIT's separately retained October 15 disposition date is unchanged.

## 3. Proposed target calendar

All October windows after the active trial are conditional planning estimates. The DFT window has the largest uncertainty because the remaining job inventory and budget are not yet approved.

| Phase | Target window | Scope and resource | Required output / exit gate |
|---|---|---|---|
| 0. Current boundary trial | Oct 5; hard end early Oct 6 | Current approved Anvil job: control → stopped candidate → isolated fresh SCF → permitted resume or reseed branch; history-reset control on the resume path | Terminal scientific/scheduler record, all arm receipts and actual SU; preserve any failure |
| 1. Exact-snapshot readout | Oct 5–6 after termination | Local/offline parsing, immutable evidence mirror, raw energy/force/geometry and optimizer audit, independent review | Scoped verdict tied to the exact launch commit/spec; explicit-path publication; no extra QE needed |
| 2. Longer checked-relaxation pilot | Oct 6–9 target | Additive every-step P-A driver, isolated fresh checks, observed restart/history semantics, bounded end-to-end catalyst pilot on Anvil after dated scope/cost approval | Every-step and terminal acceptance validated, or a retained HOLD/INCONCLUSIVE outcome. Reprice from this trial before launch |
| 3. Finite selection-relevant DFT batch | Oct 8–15 target, after appropriate protocol clearance | Inventory and execute exact missing clean-slab/adsorbate/structural/reference legs; audit reusable results; preserve fixed discovery/held-out assignments | Matched, chemically applicable reference/chain evidence and an uncertainty-aware comparison. Exact new job count, SU and deadlines must precede launch |
| 4. S8 decision and melt-list freeze | Oct 13–15 target | Offline ranking/uncertainty review plus entrant and laboratory decisions | Explicit selection purpose and rule, composition percentages, controls, prediction table, independent batch/replicate design and deposit before validation sample preparation / first ingot |
| 5. Make and characterize samples | Oct 15–21 target | Laboratory: approved stock and sample form, supervised preparation/processing, composition and phase/homogeneity checks, electrode preparation | Traceable samples with actual composition/phase and matched processing; throughput and dated instrument slots confirmed by lab |
| 6. OER measurements and durability | Oct 19–25 target; rolling only after valid samples exist | Matched electrochemical comparisons, activation, resistance/reference treatment, primary sustained endpoint, durability and oxygen-product checks | Independent-batch results, uncertainty, controls and failure records; claim-dependent additional chemistry/phase measurements |
| 7. Final analysis and working data lock | Oct 25–27 target | Local statistics and mechanism-limited interpretation; frozen predictions versus measured outcomes; figure/source audit | Complete scored/failed/unknown disposition table and entrant's REPORT LOCK election; proposed working cutoff Oct 25 |
| 8. Report and application completion | Start Oct 5; final integration Oct 26–Nov 2 | Entrant's own report/abstract/essays; figure assembly and feedback; educator/project recommendations and transcript administration | Completed investigation presented within actual evidence bounds; final report and application components ready |
| 9. Final review and submission | Nov 2–4 internal target; Nov 5 official deadline | Scientific/numerical/reference consistency, package review and entrant submission | Complete application and required recommendations submitted by Nov 5, 8 p.m. EST |
| 10. Competition continuation | Jan–Mar 2027, conditional on selection | Prepare to discuss submitted methods/results; update separately dated research only as permitted; presentation/interview preparation if selected | Top 300 announcement Jan 7; Top 40 Jan 21; finals Mar 11–17 |

### Parallel evidence and administration

- **Oct 5–15:** targeted source closeout, source-verified extraction/coding and uncertainty dispositions; preserve unresolved literature records. Apply the registered P-LIT October 15 disposition if still unlanded. Repeated discovery or completed screening is not the default work item.
- **Oct 5–12:** candidate/sample-form feasibility, instrument scheduling, comparator procurement, primary endpoint and replicate design can advance while gated DFT runs. Laboratory access is already confirmed; exact dated slots, throughput, stock and sample-form constraints remain to be pinned.
- **Oct 5–Nov 2:** entrant report development and application administration run continuously. Completed detector/census figures can advance now; later material outcomes enter only with verified evidence.

### Timeline overview

~~~mermaid
gantt
    title Proposed STS working calendar — later phases gated
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    section Anvil and DFT
    Current trial and offline readout :active, 2026-10-05, 2d
    Checked-relaxation pilot target :2026-10-06, 4d
    Finite candidate DFT target :2026-10-08, 8d
    section Selection and laboratory
    S8 selection and freeze target :2026-10-13, 3d
    Fabrication and characterization target :2026-10-15, 7d
    OER and durability target :2026-10-19, 7d
    section Evidence and report
    Literature closeout :2026-10-05, 11d
    Entrant report and application work :2026-10-05, 29d
    Working data-lock target :milestone, 2026-10-25, 0d
    Final analysis and review :2026-10-25, 10d
    Internal submission target :milestone, 2026-11-04, 0d
    Official deadline Nov 5 at 8pm EST :milestone, 2026-11-05, 0d
~~~

## 4. What the compute phases actually contain

### Phase 1 — Finish this trial's readout

Collect final scheduler accounting and immutable arm logs, inputs, XML, saved optimizer and checkpoint manifests. Build a retest-aware additive readout, leaving the first-trial frozen readout intact. Check geometry/evaluation pairing, force units/constraints, settings identity, actual checkpoint consumption and complete ordered trajectories. Read reseed evidence separately from continuity. Independently audit and bank the outcome. This phase needs no new solver allocation.

### Phase 2 — Validate longer P-A operation

P-A means a warm relaxation segment followed by an independent fresh electronic check at the evaluated geometry. The longer implementation must validate this transition repeatedly and at terminal convergence:

- A failed fresh reference yields HOLD.
- A fresh state strictly more than 10 meV/cell lower triggers the registered intentional electronic reseed and optimizer-history reset.
- A permitted continuation must demonstrably consume its full checkpoint; a copied BFGS file alone is insufficient.
- Terminal force/geometry evidence needs a valid fresh comparison.
- Fix exact maximum accepted steps, reseeds, numerical targets, scheduler resources, total SU and wall limits before approval.

The current one-boundary approval does not supply that longer pilot's resource budget. The older 40-step/10-reseed proposal and its stricter fresh target remain unadopted; choose and review the concrete next pilot after this readout.

### Phase 3 — Inventory, then fill exact DFT gaps

DFT is already present in the project. The necessary action is source-specific reuse and gap closure:

- The original nine-leg three-site structural study is terminal: **3 accepted / 6 terminal QC failures**. Accepted evidence includes Cu8 reconstructed O, Ni31 clean slab, and Ni31's unreconstructed-start O leg (its final endpoint is classified reconstructed). All three paired-start basin conclusions remain UNDECIDED; conditional ortho controls remain unrun. Preserve these outcomes instead of assuming nine fresh reruns.
- Selection-relevant chains require consistent **clean slab + OH + O + OOH** evidence, intact or explicitly classified chemical identity, acceptable numerical/force evidence and consistent magnetic, projector and gas/free-energy conventions.
- H2/H2O reference DFT is already banked. Check compatibility and reuse valid references; additional gas calculations require a real mismatch or protocol change.
- The historical chain panel currently supplies **zero ordinary AEM overpotential scores**: some chains are incomplete; the leader's third state is O2 plus slab H rather than adsorbed OOH. Chemical outcomes cannot be relabeled to fill a conventional chain.
- The retained blind DFT-label design is **15 chain / 60 state slots**: 8 discovery groups, 4 held-out groups and 3 targeted audit slots. This is scientific scope before reuse/branches, not a new-job count or licensed allocation. Retain composition splits and failed/missing denominators. Decide which unfinished obligations the next dated batch covers; unresolved planned work keeps its registered disposition.
- The active Cu8 seed20/site2 is a selected minimum. Its result does not by itself validate the p10 support sites. Broader tail-support generalization has its own scope and cost; the existing sizing note places that row after the melt freeze, rather than making it a universal freeze prerequisite.

Each new batch needs an exact leg inventory, source/settings pins, acceptance rules, usable-result reuse list, estimate and hard ceiling, independent review and approval. A finite missing-work manifest is the output of scoping; no all-site sweep, active-phase expansion or replacement realization is automatic.

## 5. Melt freeze and laboratory scope

The purpose of the S8 experiment must be explicit. Selection of a **claimed superior** melt remains on hold until relevant structural/reference evidence and the entrant's ranking-rule decision support it. A declared exploratory or informative validation set can retain unresolved rankings, with a dated scope decision, frozen predictions and matched controls. Its scientific claims follow its actual endpoint and uncertainty.

Current sample roles are **2–4 candidate alloys + a predicted-poor anchor**, with **same-bench IrO2** as the required reference. The candidate names are not elected by this timeline. NiFe-LDH can be an added alkaline comparator; it is not an automatic substitution for IrO2.

Before validation samples: lock exact compositions, selection/statistic/admission/tie/missing-case rules, measured endpoint, expected ordinal outcomes and uncertainty, batch and replicate counts, preparation/activation, stock/sample form and role-overlap rules. Retain the S8 freeze/deposit before first ingot. Historical melt lists and weigh sheets must not silently become today's composition or feedstock instructions.

Sample work consists of supervised melt/processing, actual composition and phase/homogeneity checks (such as XRD and SEM-EDS), matched electrode preparation and traceable batches. Electrochemistry then fixes electrolyte, reference calibration, current normalization and resistance treatment; measures activity and durability; and verifies oxygen production for an OER activity claim. Additional dissolved-metal or surface/phase measurements depend on the intended mechanism/stability claim and laboratory capability. Bulk phase characterization alone does not establish the operating active surface.

Independent material batches and repeated electrodes are distinct replication levels. The final SOP, exact replicate counts, duration and primary sustained-current interval remain prospective choices. Historical numerical SOP values are starting context rather than an adopted current protocol.

## 6. Resource and schedule checkpoints

| Item | Current standing |
|---|---|
| Active diagnostic trial | Approved estimate 275–543 SU; hard cap 2,048 SU / 16 h; one job, no automatic retries |
| Offline readout, coding, rankings and statistics | No new Anvil solver SU allocation |
| Longer every-step pilot | **TBD estimate and cap.** Historical unadopted sizing: about 3,526 SU / 27.5 h for 20 steps; about 11,003 SU / 86 h at the larger proposed ceiling. Reprice from current timings and scheduler feasibility before approval |
| Candidate production/chain DFT | **TBD leg count, estimate and cap.** Reuse compatible existing results; prices depend on accepted-step/fresh-check counts and branch behavior |
| Broad tail/generalization rows | Separately scoped. Historical bracket row: 12 structural legs, roughly 7,075–11,365 SU expected and 23,298-SU ceiling under old sizing, not today's commitment |
| Laboratory campaign | Exact stock, independent batches, processing and instrument calendar remain to be fixed; no invented booking or cost |

**Proposed decision checkpoints:**

- **Oct 6:** close current readout or retain exact terminal uncertainty; put a concrete longer-pilot estimate/ceiling on the table.
- **Oct 9:** decide whether protocol evidence and remaining allocation support the proposed candidate batch; clarify superior-selection versus exploratory-validation scope.
- **Oct 15:** target S8 freeze/deposit only if its scientific and experimental specification is complete. Apply the separate registered P-LIT disposition. Calendar pressure does not change QC or statistical thresholds.
- **Oct 21:** assess actual sample readiness and realistic measurement throughput.
- **Oct 25:** proposed working data-lock checkpoint. Preserve late/failed/unresolved material outcomes with their labels and decide REPORT LOCK. Research can continue as a separately dated extension; the submitted report must describe the completed investigation actually in the package.
- **Nov 4:** internal application submission target. The official application/recommendation deadline remains Nov 5, 8 p.m. EST.

If the pilot or selection-critical DFT slips, the dependent freeze/fabrication windows move. The detector/census, source closeout, figures and entrant report continue in parallel. Optional broader ranking/active-phase studies retain their scope and disposition rather than being silently required before submission. No automatic additional melt or computation is implied.

## 7. Finish criteria

The submission endpoint comprises a reconciled scientific disposition/claim table, verified figure/source pack, reproducible analysis and versioned raw evidence, the entrant's own report/abstract/essays, and completed recommendation/transcript/application components. The official report is limited to 20 content pages, with title/abstract/bibliography outside that limit, and must report a completed investigation. Entrant writing proceeds under the official report guidelines; this operational timeline is not application text.

After submission, preserve the submitted snapshot and prepare to explain its actual findings. If selected, the official dates are **Jan 7, 2027** (Top 300), **Jan 21** (Top 40), **Mar 11–17** (finals), **Mar 14** (public exhibition), and **Mar 16** (awards). Post-deadline research does not retrospectively enter the submitted investigation.

## 8. Source map

- Current raw status and identities: [status snapshot](../../results/sts_roadmap_2026-10-05/status_snapshot.json), [source pins](../../results/sts_roadmap_2026-10-05/roadmap_basis.json).
- Current claim, stages and report-lock amendment: [program board](../45-error-ledger.md), lines 76–122 and 2540–2551.
- Boundary-to-production and melt dependencies: [current readiness](eligible-comparison-pa-readiness-2026-10-03.md), lines 134–178.
- Laboratory access and unresolved forms: [readiness lanes](sequential-evidence-compute-readiness-2026-10-03.md), lines 113–134.
- S8 selection disposition: [operating decisions](research-decisions-2026-09-16.md), lines 51–64; [independent ranking review](s8-ranking-independent-review-2026-09-19.md), lines 68–76.
- Numerical sizing, unadopted longer-pilot proposal: [readout preparation](pa-catalyst-trial-readout-prep-2026-10-04.md), lines 118–166.
- Terminal nine-leg outcomes: [primary readout](../../results/lowtail_dft_2026-09-18/followthrough/primary_readout.json).
- Existing chain and gas references: [HEA panel readout](hea-panel-readout-2026-09-17.md), lines 60–74.
- Fixed pilot membership: [HEA DFT-label design](hea-validation-design-2026-09-07.md), lines 9–23.
- Tail-support extension and cost: [generalization sizing](lowtail-generalization-sizing-2026-09-22.md), lines 20–53.
- Comparative claim bounds and informative sample purpose: [ranking adequacy](../candidate-ranking-adequacy-2026-09-06.md), lines 43–61.
- Verified official deadline/application components: [Society for Science](https://www.societyforscience.org/regeneron-sts/application-requirements/).
- Verified official competition dates: [STS calendar](https://www.societyforscience.org/regeneron-sts/).
- Report format and completed-investigation requirements: [2027 Research Report Guidelines](https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2027/Application/Research-Report-Guidelines.pdf).
