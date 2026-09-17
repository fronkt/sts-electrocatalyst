# Research operating decisions — 2026-09-16

These prospective operating decisions apply under the current instruction to approve the remaining work and start it. They adopt the scientifically defensible recommendations in `remaining-research-decisions-2026-09-13.md` with the corrections below. Historical records remain available; this document records the current scope and choices, without asserting a personal signature or changing any completed result. Execution status and actual job identifiers belong in the task ledger.

## Decisions that remain unchanged

The seven September 4 silentgate rulings remain in force: ALL adsorbate atoms; a truncated force block is scorable only when all identified adsorbate atoms are present; release-asset OC20 CI; the explicit provenance-record path; the if_pos mechanism correction with the conservative exclusion retained; the recorded packaging scope; and the dated x-census disposition. Their actual dated lines are `docs/43-prereg-week1-factorial.md:4175` onward and their machine-readable choices are in `tests/silentgate/spec_rulings.toml`. The September 13 silentgate core supersession also remains in force.

## Divanis rulings 2–7

**R2 — exact population.** Adopt the source row identities in `results/research_decisions_2026-09-16/divanis_selection.json`. Within Table SI-2, select complete rows whose structure token matches `^[A-Z][a-z]?O2b?$`, followed by the four numeric energy columns; retain source order and repeated material rows, with no energy filter or deduplication. This gives 38 rows: Man/article 1 = 26; Mom/article 7 = 11; Frydendal/article 9 = 1. The predicate does not use an article whitelist to force those counts. The source text SHA-256 is `88bfcda9a5e70da10d3b2565af7cc09b7377578e4aac4dd5d9a74b42c0bd8bda`. The lexical population reproduces the historical subset; it is not independent structural evidence that every entry is a real rutile phase. Preserve the unlegended b suffix and identify Man coverage attribution as external to this ESI text.

**R3 — middle band.** With denominator 38, a scored count of 4–9 is `SCORED — MIDDLE BAND / NOT MET`. Counts at least 10 meet the historical confirmation criterion; counts at most 3 meet its falsification criterion. Report the per-article breakdown, denominator composition and exact count with the outcome; a middle-band result supports no binary class claim. No scored count is calculated in this decision record.

**R4 — correction sensitivity.** Report the full interval delta = corr_OOH − 0.35 eV in [0.00, 0.10] eV. The historical CrO2 guard reconstructs at delta = 0.05; that arithmetic does not establish a primary source for the correction and does not license a privileged single-delta headline. Since the repository deadline has passed without a documented resolution here, retain the curve-only fallback. Any claim of invariance requires enumeration of CHE branch crossings and all threshold roots, evaluation within each resulting interval, and exact-boundary and one-sided cases. Equality at three sample points alone is only three-point sensitivity. The curve and invariance result remain pending.

**R5 — article denominator.** Use three articles for the selected population and correct the historical n = 24 label explicitly: 24 is the whole-corpus article count. Display Man 26 / Mom 11 / Frydendal 1 on the figure face.

**R6 — negative fourth steps.** Enumerate and retain every selected row with deltaG4 < 0 under each applicable correction convention. Report these as negative fourth-step free energies under the imposed CHE cycle. A negative individual reaction step does not by itself prove a material impossible, an adsorption structure unstable, or an entire paper wrong. The historical CrO2 wording is retained only as a historical description; use this thermodynamic interpretation for new analysis. The enumeration remains pending.

**R7 — reporting scope.** A clearly labeled reconstruction of an external table, including the historical CrO2 arithmetic guard, is permitted as an arithmetic check. It is not an in-house prediction of electrode performance. Any eventual S7 exception must be named `external-corpus-arithmetic-reconstruction-2026-09-16`, limited to explicitly labeled external reconstruction text, and must not exempt materials-performance claims. No S7 implementation or passing check is implied here.

The separate September 5 BROAD election for the scored Divanis rate is not silently changed. This record freezes source identities and interpretive choices; it computes no floor-margin rate.

## A10 / S5: all fifteen decisions

The 18 placeholder occurrences in docs/88 correspond to fifteen distinct IDs. Nine are labeled THRESHOLD blocks in docs/74; they are not nine independent numerical thresholds. Several select an estimator, population, vocabulary or process. The existing sigma bands are retained; no value is fitted to the observed HEA census.

| ID | Operating decision |
|---|---|
| A10-E | Round-2 Amendment 10 together with its S5 stage specification governs. The earlier round-1 seven-metal rule is superseded. |
| A10-M | Outcomes meeting neither numerical band are `SCORED — MIDDLE BAND / NOT MET`, with counts and per-metal sigma shown; no binary class claim. |
| A10-D | Use Ladder B, fixed before the new S5 executions: for three scoreable metals, at least two below 0.25 V confirms and at least two at/above 0.30 V falsifies; for two scoreable metals, both below 0.25 V confirms and both at/above 0.30 V falsifies. Otherwise middle band. One metal is reported without a verdict; zero is unscored with reasons. |
| A10-G | The historical S0(a) switch result is passed for its tested binary: calculation=ensemble. Actual production-binary emission remains an execution check. Run bounded slab and isolated-gas checks before scaling; strings/library linkage is insufficient. |
| A10-σ | For each common ensemble member, form the four CHE steps from the four slab-state total energies and both gas-reference total energies, with fixed ZPE/TS corrections. Compute that member's maximum step, subtract 1.23 V, then take sample standard deviation (ddof=1) across the 2000 member overpotentials. Report the member-wise limiting-step histogram. |
| A10-C | Retain absolute sigma bands <0.25 V and >=0.30 V. Compare descriptively to the same-metal eta change between U=0 and U=9, with grid max-minus-min beside it: Ru 0.4968 V, Ti 0.2459 V, Ir 0.0266 V; Ir grid span 0.1979 V. These are different uncertainty/sensitivity summaries, so a larger sigma alone does not establish the dominant physical error source. Cr's 1.122 V context must identify Cr and its distinct scope. Any symmetry comparison retains both coverages. |
| A10-S | Label the primary S5 result XC ensemble at fixed geometry, non-magnetic Ru/Ir/Ti. It is not a calibrated predictive error or an uncertainty bound for HEA screening. |
| A10-X | No Cr extension in this primary S5 population: base {Ru, Ir, Ti}, fourteen existing decks including two gas references. Cr BEEF+U remains separate research with an explicit future population, geometry and estimator before its results can enter a new claim; do not add it opportunistically to Ladder B. |
| A10-K | Start with bounded capability/gas checks and proceed to the approved base program when they pass. Preserve the historical submit-by dates as planning history; do not cut otherwise useful science merely because a date passes. At a report snapshot, an unfinished result remains unscored rather than being anticipated. |
| A10-ARM | Use the existing mir fixed geometries for Ru/Ir/Ti adsorbate states and the existing bare ref geometries, as the fourteen current decks specify. These are fixed PBE geometries, not BEEF-relaxed geometries. Report known symmetry-arm dependence as an unmeasured contribution to this S5 uncertainty estimate. |
| A10-ENS | Regenerate the primary ensemble using ASE BEEFEnsemble.get_ensemble_energies(size=2000, seed=0) from the converged BEEF-vdW SCF energy and its 32 XC contributions. Use one identical coefficient matrix across all slab states and both gas references, and record its checksum and ASE/NumPy versions. QE's 2000-member emission is a capability/completeness check, not the primary member draw. |
| A10-DISP | Place P-XU in the six-row body ledger and move historical P7 to the appendix with its result unchanged. Retain P-PROJ, P-PLS, P-FLOOR-U, P-SYMCOV and P-BEEF in the body. This supports the elected detector/census-first ordering without discarding historical results. |
| A10-A74 | Add an explicit result/status column to the current supporting gate table: historical S0(a) tested-binary result and production-binary check are separate entries. Do not rewrite deposited history or mark the latter passed before execution. |
| A10-CHR | Do not claim Christensen-style functional independence or across-material universality from three endmembers. |
| A10-DEP | No additional disclosure or deposit task is an execution gate in this scientific continuation. Historical deposit obligations remain identifiable as historical records; no new deposit or signature is asserted. |

**Estimator implementation conditions.** ASE's installed `ase/dft/bee.py` returns the SCF baseline plus the coefficient/contribution perturbation. Pass baseline and contributions in consistent eV units, after verifying QE's contribution order and Ry-to-eV conversion; never treat the printed perturbation block alone as a total energy. An identical seed is not enough across differing software implementations: construct or verify the actual common coefficient matrix, including its checksum. Require clean convergence, JOB DONE, no QE routine error, the complete finite 32-contribution vector, and complete finite 2000-member QE emission on every contributing state. If any slab state or either required gas reference fails, do not manufacture matching by truncating, independently resampling or substituting PBE gas energies. A failed shared gas reference prevents a score for all metals. Retain failed outcomes and their reasons.

The readout must use the decision values above consistently; no S5 sigma or verdict exists in this decision record. Keep the fixed-geometry limitation and the PBE-generated pseudopotential/input_dft override explicit. Fresh self-consistent BEEF-vdW density precedes ensemble evaluation. The gas compatibility test concerns the actual isolated H2/H2O decks under the production executable.

## S8 scientific go/no-go

Continue computational validation and experimental feasibility. Hold selection of a claimed superior melt: the present census gives different leaders for minimum, mean and median, and the low-overpotential tail includes reconstruction and adsorbate loss. A short Cr–O bond plus lifted Cr is a model-predicted structural response; cross-model agreement would support robustness within those models, while disagreement identifies validation priority. Neither result establishes experimental surface chemistry.

Use the completed cross-model results to examine geometry, adsorbate integrity, relaxation convergence and per-state energy changes. Test retained low-tail and comparison structures with DFT, including the paired projector control. Keep the historical branch panel and energy-blind mixed-composition pilot identifiable; they are not replacements for validation of the new low-tail sites. Single-point agreement assesses energies/forces on specified configurations; persistence of a reconstruction requires a suitable relaxation and a basin/chemical-integrity check.

Before a prospective materials-performance comparison, define composition selection and its ranking statistic, preparation and activation, independent material batches, uncertainty and replication, and matched poor-anchor/IrO2 benchmarks. Freeze actual predictions before preparing their validation samples. No melt composition, superiority claim or physical experiment is approved by a missing numerical result in this record.

## Dates checked against the repository

- September 15: `docs/43-prereg-week1-factorial.md:1898` sets the delta provenance deadline and curve-only fallback; `:1945` sets the F8 literature/structure-assignment cleanup deadline. It is not a blanket due date for all docs/86 rulings 2–7. Those rulings must precede the scored count (`:4355`).
- September 18: A10 in `docs/45-error-ledger.md:55` and docs/88. The ledger's NOT DRAFTED/gated-on-S0(a) text is historical and contradicted by the existing draft and gate evidence.
- September 20: claim-sentence re-test in `docs/45-error-ledger.md:65–72`, `docs/87-claim-sentence-constraints-2026-09-05.md:6–8`, and the body-ledger displacement at `docs/43-prereg-week1-factorial.md:1930`.
- S8: prediction freeze precedes first validation melt; it is not a September 15 deadline (`docs/45-error-ledger.md:56`). Dates do not substitute for scientific evidence.

## Verification and pending measurements

The local source SHA-256, 38 unique source-line identities, raw row text, numeric column shape and 26/11/1 composition are checked by direct file inspection. The installed ASE API confirms the selected class method accepts size and seed and adds the SCF baseline to its perturbations. No shell command, DFT job or scored chemistry calculation is part of those file checks.

Pending: full-interval Divanis reconstruction and negative-step enumeration; primary-source/convention verification of QE-to-ASE contribution mapping; actual Anvil slab/gas capability checks; S5 sigma, per-member limiting steps and verdict; DFT scientific readouts; held-out mixed-composition validation; prospective physical performance validation. The scientific go-ahead is not evidence that any of these checks has passed.

## HEA-DFT: HEA-1 through HEA-9

Approve the 22 exact existing fixed-geometry inputs in docs/92 through the separate approved manifests `runs/m_research_2026-09-16_hea_panel.txt` (10) and `runs/m_research_2026-09-16_hea_pilot.txt` (12). Historical draft manifests remain unchanged and cannot accidentally submit through their old route. These are the two retained historical chains and branch endpoints, not the newly identified census winners. Earlier pilot/control realizations and rejected numerical attempts remain unchanged; these new executions do not add independent material samples.

| Slot | Decision |
|---|---|
| HEA-1 | MP set of record: Cr 3.7, Mn 3.9, Fe 5.3, Co 3.32, Ni 6.2 eV; Cu without U. No Wang–Ceder arm. |
| HEA-2 | Both atomic and ortho-atomic projectors on each specified geometry. |
| HEA-3 | Existing ferromagnetic per-species starts; magnetic ground state is not established. Retain open-shell fragment flags. |
| HEA-4 | Keep input electron_maxstep=300; the execution supervisor stops once iteration 127 begins or the individual SCF exceeds its unrounded per-deck ceiling reconstructed from the published cost table (rounded upward to the next second). Record KILLED, preserve scratch and never turn a stopped endpoint into an energy. No automatic restart ladder. |
| HEA-5 | Both listed pairs, both projectors: eight SCFs. |
| HEA-6 | Include leader_pull1.70 proton-acceptor control, both projectors: two SCFs. |
| HEA-7 | Historical planning 4,164.7 core-hours; rounded per-deck SCF ceilings sum approximately 12,494.2 core-hours. Add up to 30 minutes per task for projection and bounded shutdown grace. Scheduler cap is six hours per task, 16,896 core-hours for 22; this cap is not the expected cost. |
| HEA-8 | Run the two retained chains only, with OOH reused from the panel. The separate three-composition mixed pilot keeps its already frozen outcome-blind membership; no favorable census site substitutes for it. No new comparison-site rule is invented for missing historical coordinates. |
| HEA-9 | Fixed-geometry eta MAE comparison 0.164 V, with 0.12955764753597102 V relaxed-pipeline number explicitly secondary and labeled. Adsorbate loss still makes the ordinary AEM eta undefined. |

All runs use 128 MPI ranks and the existing per-row pool count. Severe numerical exceptions, incomplete energy/force blocks, missing projection records or stopped calculations remain unusable. The old HEA scorer is tightened before submission to enforce this existing scientific requirement. A converged single point with large residual forces is an energy/force measurement at the fixed geometry, not evidence of a DFT minimum.

## Ru pseudopotential control: RU-PP-1 through RU-PP-7

Approve the twelve existing GBRV Ru decks at U=0, 6.73 and 9 eV, four states each, against the corresponding ONCV bank. Use `runs/m_research_2026-09-16_ru_pp.txt` and the precommitted sibling readout. Adopt the docs/89 choices:

- RU-PP-1: those three rungs, atomic projector, unchanged geometry and spin convention.
- RU-PP-2: retain 80/640 Ry and the existing k-mesh; this is a controlled pseudopotential substitution, with no new Ru cutoff-convergence claim.
- RU-PP-3: Q is half the absolute endpoint change in E(OOH)-E(OH). Q>=0.100 V is PP-SENSITIVE; below that, absolute shift from the frozen 0.09225 V reference <=0.0078 V confirms the stated comparability margin; otherwise MIDDLE. Preserve the exact ONCV recomputation beside that historical rounded reference.
- RU-PP-4: at U=9 use Ir-minus-Ru margin >0.36 V / [0.20,0.36] V / <0.20 V; retain original verdicts and report conditionality.
- RU-PP-5: at U=0 use absolute eta shift <=0.20 V versus >0.20 V.
- RU-PP-6: at U=6.73 compare sign of 0.637-eta; an exact tie provides no corroboration. Keep PROJECTOR-MISMATCHED wording.
- RU-PP-7: historical planning about 50 core-hours, 33–90 core-hours estimated range. Each SCF has a 20-minute execution bound, projection ten minutes, and scheduler 35 minutes including shutdown grace. Total scheduler cap 896 core-hours, not a 90-core-hour hard budget.

The live Ru GBRV UPF matches md5 `7158a806dd851261a58e6920c40ebe78`. Projected populations use different bases across UPFs and are retained as diagnostics, not compared as equivalent charges.

## Bounded launch and release policy

The exact inputs, helpers and approved manifests are hashed in `results/research_launch_2026-09-16/launch_spec.json`. Commit and push precede verified staging. Submit held, inspect actual scheduler resources and then release. Preserve the parity marker, pseudopotential byte checks, sick-node exclusions and no-overwrite guards.

S5 starts with H2, H2O and the Ru bare slab. Each has a 50-minute execution bound and a one-hour scheduler limit. The remaining eleven S5 tasks may release only after all three prerequisites have COMPLETE QC, unchanged output/runtime hashes, valid 2000-member emission and valid 32-term contribution blocks. Failed capability/gas checks stop expansion; they do not change the scientific denominator by selecting replacements.

HEA arrays each have concurrency one; the small control arrays each have concurrency two. The maximum sum of scheduler allocations for the entire 48-job program is 19,584 CPU SU, against the freshly checked balance of 53,217.8 SU. Expected usage is substantially lower; elapsed usage and failures will be reported from scheduler accounting. No GPU allocation or paid external instance is requested. Scratch and raw outputs remain available on Anvil; 4.3 TB was available at preflight.

This operating record and its committed hashes are the prospective execution authority for these exact jobs. It does not assert a personal signature, retroactive registration, deposit, successful calculation, new materials ranking or physical validation.
