# Sizing the DFT generalization beyond the three Cr sites — 2026-09-22

Scope: what a first generalization row would consist of, what it would cost against the allocation, which registered rules govern adding legs, and what the same morning's diagnostic readout implies for the order of operations. Nothing here licenses a deck; every count is exact and every cost is from observed runs.

## 1. Where the current program stands

Array 20813525 (nine legs, three sites, `lowtail-relaxation-launch-v1`, concurrency one) at 05:05 UTC: task 1 Cu8Cr23Mn35Co34 seed20 site2 clean slab FAILED at the SCF ceiling (15,134 s); task 2 Cu8 O_recon COMPLETED (31,203 s); task 3 Cu8 O_unrecon KILLED at the SCF ceiling (33,571 s); task 4 Ni31 clean slab RUNNING; tasks 5 to 9 PENDING. Two of the three Cu8 legs stopped without an energy. Balance 46,313.9 SU; tasks 4 to 9 still carry 3,674 planning / 12,101 ceiling core-hours of the spec's commitment.

The SCF diagnostic (array 20840139) is read in `lowtail-clean-slab-scf-stall-2026-09-19.md`, "Diagnostic readout — 2026-09-22": the production mixing (0.3, local-TF) is what the 0.30 legs ran; a fresh-start SCF at the Cu8 cycle-5 geometry converged 94.7 meV below the relaxation's stagnating value at the same geometry and Hamiltonian, with matching occupations and moments; Ni31 converges to one solution; Fe25 has two failed SCFs and none converged; 0.10 is worse everywhere.

## 2. The first generalization row as defined

Row definition from the S8 proposal and its independent review: the sites that support the p10 statistic under the `adsorbate_intact` policy for the two compositions that lead the tail and central statistics. Data: `results/s8_ranking_statistic_2026-09-19/independent_review/diagnostics.json`; review line `s8-ranking-independent-review-2026-09-19.md:97`.

| Composition | n (intact) | min (V) | p10 (V) | Bracketing sites (interpolation weight) | η (V) | Census endpoint |
|---|---:|---:|---:|---|---:|---|
| Cu8Cr23Mn35Co34 | 16 | 0.362220 | 0.383548 | seed16 site2 (0.5) | 0.380804 | Cr reconstruction (O) |
| | | | | seed26 site1 (0.5) | 0.386293 | Cr reconstruction (O) |
| Cu26Ni9Cr31Co33 | 13 | 0.449168 | 0.502093 | seed1 site0 (0.8) | 0.479192 | Cr reconstruction (O) |
| | | | | seed17 site1 (0.2) | 0.593696 | intact |

Under the "at or below p10" reading the sets are instead {seed20 site2, seed16 site2} for Cu8 and {seed5 site2, seed1 site0} for Cu26, all four Cr-reconstruction endpoints. Either reading gives four sites; at three legs per site (clean slab, O_recon, O_unrecon, atomic projector) that is twelve legs. Only Cu8 seed20 site2 has decks and runs today (array tasks 1 to 3), so the bracket reading needs twelve new legs and the at-or-below reading nine; a leg byte-equivalent to one already run is resolved to the existing record and omitted (`build_hea_controls.py:311`, the RUN ONCE header rule). No Cu26 deck exists anywhere under `runs/`.

## 3. Cost against the allocation

Observed at 128 ranks on this site family (1 SU ≈ 1 core-hour, checked against the balance drawn since 2026-09-18): clean-slab relaxation leg 538 core-h to its failure; adsorbate relaxation legs 1,109 (completed) and 1,194 (killed) core-h; fixed-geometry clean-slab SCF at production mixing 128 (Cu8) and 80 (Ni31) core-h, per-job ceiling 288.

| Scenario | Legs | Expected core-h (spec planning / observed Cu8 basis) | Ceiling core-h | Share of 46,314 SU at ceiling |
|---|---:|---|---:|---:|
| Two discriminating SCFs on the Cu8 stall (from retained scratch; production mixing and plain mixing) | 2 | ≈260 | 576 | 1.2 % |
| Twelve-leg row, bracket reading | 12 | 7,075 / 11,365 | 23,298 | 50.3 % |
| Nine-leg row, at-or-below reading, Cu8 seed20 reused | 9 | 5,306 / 8,524 | 17,473 | 37.7 % |
| One site per composition, all six | 18 | 10,886 / 17,047 | 35,850 | 77.4 % |

The three relaxation rows sit on top of the 12,101 core-hours of ceiling already committed to array tasks 4 to 9; the eighteen-leg row plus that commitment exceeds the balance at ceiling.

## 4. Rules that govern adding legs

- A11.R3 (`docs/43:2113`, restated `:2962`): each licensed compute addition carries its own dated line with every count exact; a submission to a shared allocation is not a scribe's act.
- HEA-1 to HEA-9 (`research-decisions-2026-09-16.md:78-86`): HEA-2 both projectors on each specified geometry; HEA-4 `electron_maxstep = 300`, supervisor stop at iteration 127 or the per-deck ceiling, KILLED recorded, scratch preserved, no automatic restart ladder; HEA-7 planning and ceiling core-hours and the scheduler cap stated in advance; `:88` stopped calculations remain unusable.
- A6.6 scope guard (`docs/43:1283-1288`) licenses fixed-geometry SCFs and no relaxation; the relaxation array rests on `research-decisions-2026-09-16.md:55` and `operating_decisions.json.registration_context` ("no registered threshold for this question").
- Builder licence line (`lt_decks.py:216`): a manifest carries NOT LICENSED until a dated approval line exists; `research_batch.py:64` and `lowtail_batch.py:34` refuse such manifests.
- Restart rule (`operating_decisions.json.kill_rule.on_stop`): a stopped leg yields no energy, geometry or basin; restarting from the last ionic geometry needs its own dated decision.

Machinery: a new fixed-geometry SCF batch reuses `research_batch.py` unchanged with a new spec, manifest, slurm and submit pair and a launcher whose five module constants are parameterized; a new relaxation batch additionally needs `lowtail_batch.py` freed from its nine-job, single-authorization validation and a submit path without the hard-wired `--array=1-9%1`, which changes pinned hashes.

## 5. Order of operations this note recommends

1. Run the two discriminating SCFs first (≈260 core-hours). Until they say whether the Cu8 stall is a second solution or a stagnating density with a misleading accuracy estimate, every clean-slab and unreconstructed-O relaxation in the new row is at risk of repeating a failure that costs 500 to 1,200 core-hours a leg, and the completed legs' forces are of uncertain provenance.
2. Fe25 seed2 site0 has no converged SCF at any tried mixing; a Fe25 relaxation leg (array task 7 is such a leg) should not be replicated in the row until one exists.
3. Then license the row by the bracket or the at-or-below reading, nine or twelve legs, with the cost lines above, one dated line under A11.R3.

The melt candidates list does not wait on this row: the S8 disposition holds selection until the nine-leg readout and the entrant's dated ranking-rule line, and the row is post-freeze evidence either way.
