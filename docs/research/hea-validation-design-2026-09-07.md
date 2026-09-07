# Prospective HEA DFT-label validation pilot — 2026-09-07

The twelve-composition historical R4 screen is a selected pool with known MACE outcomes. This pilot withholds four composition groups from **future DFT-label fitting**. It cannot retroactively make the historical screen blind, validate composition discovery, or establish a calibrated interval.

The plan freezes before this workflow reads completed CENSUS-1 scientific outputs. The earlier equiatomic seed-2/site-0 and leader seed-0/site-0 investigations are already known; both compositions remain discovery-only. The historical leader's winning site remains a separate targeted audit, never a held-out example.

## Fixed selection

One chain per composition is reserved without consulting new energies or geometries. All four-composition subsets eligible for holding out are enumerated. The objective first maximizes the smaller element coverage of the two splits, then their summed coverage; SHA256 of the canonical exact element/fraction identities and the fixed salt breaks ties. This includes every pool element in both splits whenever feasible. Separate composition hashes determine seed (modulo 3) and site (modulo 4). The other eight groups are discovery. No salt search or outcome-based stratification applies. The plan records element-composition counts in both splits; element presence does not guarantee coverage of active metals, oxidation states, or local environments.

Every decoration, site, intermediate, projector and spin branch of a composition inherits its composition's split. The held-out labels must remain outside model fitting, threshold selection, and method choice until those decisions are frozen on discovery labels. Retained coordinate readiness does not expose a DFT label.

The base pilot has 12 energy-blind chain slots: eight discovery and four held out. Three additional targeted audit slots cover the two known chains and historical leader winner. Each slot includes clean slab, OH, O and OOH: 15 chains / 60 state slots before duplicate geometries, projector branches or spin starts. This is a scope count, not a count of newly required SCFs or a compute allocation.

The historical winner has no retained site index in the old box. Its slot resolves only when exactly one census site matches the banked seed, metal, eta (within 1e-6 V), and all three bond lengths (within 1e-3 Å), using the reproduction tolerances already stated in docs/91. Zero matches or multiple matches remain pending. The current census minimum is never substituted for an unmatched historical winner.

## Validation sequence and escalation

First compare MACE and DFT at identical coordinates, with forces requested and magnetic/numerical controls applied. Report per-state/reaction errors and force residuals separately from changes after DFT relaxation. Ordinary, transferred, detached and unconverged states all remain in the denominator; state identity governs whether an AEM eta is defined. A low force residual is not evidence that the chemical intermediate is intact.

One site per composition and only four held-out composition groups constitute a pilot. They cannot establish the complete 12-site-per-composition ranking, tail error rates, or reliable chemical-subgroup performance. If the pilot cannot resolve errors relative to a candidate separation, the staged extension is **all seeds 0, 1, 2 and all sites 0, 1, 2, 3 for each relevant composition group**, retaining the same group split and all failed/missing members. Expansion is a separate phase with explicit compute scope; it does not replace unfavorable pilot cases or alter the reserved held-out set. If held-out labels inform redesign, the revised method requires a new genuinely untouched evaluation set; reuse of these four groups is descriptive.

Report candidate ties where accuracy does not resolve the gap. Discovery, held-out and targeted audit statistics remain separate. The targeted cases probe known mechanisms and decisions; they do not estimate population accuracy.

## Identities and pending results

The plan pins the tracked R4 source's normalized-LF SHA256, exact census manifests/candidate IDs, the already-known retained result hashes, and the planning implementation hash. The separate materialization snapshot checks manifest equality, result-content hashes, candidate identity, finite periodic geometries, atom constraints, and unique site identity. Only terminal census results are consumed. Running, absent, failed, ambiguous and incomplete slots persist with their reasons and original denominators. Unsupported constraints remain pending rather than being silently dropped.

Force convergence is retained as an observation, not a readiness filter. Ready means usable coordinates are present; it does not mean DFT was run, a result passed chemical QC, or a ranking was validated. Duplicate ready geometry hashes are counted separately from state slots for later job reuse.

## Commands

Run the lightweight plan preparation first and retain its identity in the boundary commit:

~~~text
python src/dft/hea_validation_plan.py prepare --out results/hea_validation_2026-09-07/plan.json
~~~

After the boundary is fixed, materialize a separate readiness snapshot:

~~~text
python src/dft/hea_validation_plan.py materialize --plan results/hea_validation_2026-09-07/plan.json --out results/hea_validation_2026-09-07/geometry_snapshot.json
~~~

Both commands use exclusive output creation. Later snapshots need new paths; they never rewrite the plan. Neither command runs a calculator or submits a DFT job.
