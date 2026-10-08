# S8 arm C — DFT design and pricing, 2026-10-07

Status: **APPROVED and LAUNCHED.** Frank, 2026-10-07: "Go ahead. Yes to each add on." Anvil arrays 21165189 (main, 64 SCFs) and 21165190 (probe, 2 SCFs) were staged, preflighted, held, validated and released once on 2026-10-07 (receipts in `results/arm_c_2026-10-07/`). After the terminal readout, the full re-run round (§6; Frank: "Go with the full rerun.") went out the same way as array **21176478** (33 SCFs, 10,560 SU ceiling; receipts in `results/arm_c_2026-10-07_rerun/`). **Arm C is terminal (§7, read out 2026-10-08):** 40/64 SCFs and 6/16 sites; Cu8 and Fe25 have no value, so K1, K2 and the Ni34 nomination are not evaluable.

| Approved item | Value |
|---|---|
| Option | C-FG |
| Ni34 add-on | yes (sites s22/0 and s29/1) |
| Best-site add-on | yes: Cu8 s20/2, Fe25 s2/0, Cu26 s5/2, Cu22 s27/3. Ni31's best site s1/0 is already a support site. Ni34's best site was not priced and is not included |
| Scope | 16 sites, 64 SCFs, plus the Fe25 probe and one re-run round |
| Hard ceiling | **23,680 SU** = 16,000 + 2,560 + 5,120 |
| Expected | 9,300–16,400 SU |

The text below is the approved design. §3 gives the implementation as built.

Decision of record: Frank, 2026-10-07, "Continue it. OK With me." That started this design after O1's CONTINUITY_PASS ([readout](pa-o1-and-repro-probe-readout-2026-10-07.md)). It also kept the IEEE_INVALID rule unchanged, with about 11% re-runs budgeted.

Arm C is the third frozen prediction in the [stage-1 freeze proposal](s8-stage1-freeze-proposal-2026-10-07.md) §4. It is deposited before any OER measurement of the five alloys, with Oct 21 as the fallback date.

## 1. What constrains the design

**No alloy has a DFT chain.** None of the five alloys has a complete clean slab + OH + O + OOH chain. What exists:

| Type | Alloy and site | States |
|---|---|---|
| Relaxed | Ni31 s1/0 | clean slab, \*O |
| Relaxed | Cu8 s20/2 | \*O |
| Fixed-geometry chain | Ni31 s0/0 and s1/0 | all four |

Cu26, Cu22 and Ni34 have no DFT output at all (`results/lowtail_dft_2026-09-18/followthrough/primary_readout.json`; [panel readout](hea-panel-readout-2026-09-17.md)).

**SCF multistability is unsolved.** In September, 5 of 9 relaxation legs stopped at the SCF iteration ceiling, unevenly by alloy:

| Alloy | Legs stopped |
|---|---|
| Ni31 | 0 of 3 |
| Cu8 | 2 of 3 |
| Fe25 | 3 of 3 |

([stall readout](lowtail-clean-slab-scf-stall-2026-09-19.md)).
- **Mechanism at Cu8.** A density carried from step to step settles into a higher orbital configuration on one Co site, 95 meV above the state a fresh start finds. The tightened relaxation threshold cannot be met there.
- **Re-seeding helps only briefly.** Re-seeding from the low state carried the relaxation six steps before it stalled again.
- **Fe25 seed 2 has never converged an SCF.** Two fresh starts plateaued at 6e−6 and 1.2e−5 Ry.
- **Fixed geometry, same pattern.** In the September panel, Fe25 fixed-geometry SCFs failed in 6 of 10 legs (atomic projector: 4 of 5). Ni31 failed in 1 of 12, an ortho-projector branch geometry.

**Measured cost (128 cores, 0.0356 SU/s):**

| Item | Measured |
|---|---|
| Warm relaxation step | 1,000–1,400 s, 36–50 SU |
| Relaxed legs that converged | 13–23 BFGS steps, 547–1,109 SU |
| Step with a fresh check every step (P-A as designed) | 176 SU |
| Fresh-start SCF at 1e−6 | 3,348–3,399 s, about 120 SU |
| Fixed-geometry SCF (Sept panel) | 1,871–3,800 s, 66–135 SU |

**Scheduler and budget:**
- Anvil `wholenode` allows 4 days per job and 64 running jobs per user (live query, `results/arm_c_design_2026-10-07/anvil_limits_summary.json`).
- Recent queue waits were 4–16 h.
- Balance: 35,185.7 SU.

## 2. Options

| | What | Expected SU | Hard ceiling | Ready for the deposit | Main risk |
|---|---|---:|---:|---|---|
| **C-FG** (recommended) | DFT+U single points (clean slab, OH, O, OOH) at the MLIP's own census structures for each alloy's two arm-B p10 support sites. Plus a small Fe25 convergence probe | 6,000–11,000 | 16,000 | about Oct 12–13 | Fe25 SCFs may not converge. Structures are not DFT-relaxed |
| C-REL | Relaxed chains at each alloy's best site, re-seeded on every stall, plus a terminal fresh check. Needs a new driver | 17,000–35,000+ | not boundable below the balance | Oct 17–20 at best | The stall problem is unsolved: Fe25 has no converged SCF and Cu8 stalls every few steps. P-A checking every step would be 60,000–75,000 SU |
| C-SKIP | Arm C reported "not tested" | 0 | 0 | — | S8 compares arms A and B only |

**Why C-REL is not recommended.** A relaxed chain is the better physics, but the stall problem has no validated exit. At about one stall per six steps, each stall costs about 370 SU: the wasted SCF plus a fresh SCF. Re-seeds also reset BFGS, so more steps are needed. A Cu8-like leg then costs about 2,700 SU, and twenty legs consume most or all of the allocation, with a real chance that Fe25 never completes.

**What C-FG answers.** Holding the structures fixed and swapping MACE-MPA-0 energies for DFT+U energies asks one clean question: does the energy model change the ranking at the sites that define arm B? It reuses the September fixed-geometry pipeline: `hea_validation_plan.py` / `build_hea_validation_decks.py` for decks from the census JSON, `research_batch.py` for SCF supervision, and `hea_panel_readout.py` plus `src/hea_oer/referencing.py` for scoring. Very little new code is needed.

## 3. C-FG, as it would be registered

### Sites (verified against `results/site_census_2026-09-06/readout_full/per_site.csv`; MACE-MPA-0, adsorbate-intact policy, linear p10)

| Alloy | n | p10 (V) | Support site 1: η (V), weight | Support site 2: η (V), weight |
|---|---:|---:|---|---|
| Cu8Cr23Mn35Co34 | 16 | 0.3835 | s16/2 Cr, 0.38080, 0.5 | s26/1 Cr, 0.38629, 0.5 |
| Ni31Cr29Cu5Mn35 | 8 | 0.4730 | s1/0 Cr, 0.44000, 0.3 | s10/2 Cr, 0.48713, 0.7 |
| Fe25Co25Ni25Cr25 | 19 | 0.5544 | s13/0 Cr, 0.54309, 0.2 | s25/2 Cr, 0.55719, 0.8 |
| Cu26Ni9Cr31Co33 | 13 | 0.5021 | s1/0 Cr, 0.47919, 0.8 | s17/1 Cr, 0.59370, 0.2 |
| Cu22Fe30Co32Mn15 | 38 | 0.8310 | s6/1 Co, 0.80515, 0.3 | s24/3 Co, 0.84204, 0.7 |
| *Ni34Fe6Cu29Co31 (add-on)* | 15 | 0.7387 | s22/0 Ni, 0.70722, 0.6 | s29/1 Ni, 0.78595, 0.4 |

Every Cr support site except Cu26 s17/1 has a reconstructed \*O in the census.

**Structures.** From `results/site_census_2026-09-06/results/<manifest>_result.json`:
- the decoration's `relaxed_slab` (72 atoms);
- the site's `relaxed_states` for OH, O and OOH (74, 73 and 75 atoms).

Each site sits on its own decoration, so the base set is 10 clean slabs + 30 adsorbate states = **40 SCFs**.

**Numerical recipe.** The production atomic-projector DFT+U deck (`src/dft/hea_deck.py`):
- PBE with SSSP pseudopotentials, 80/640 Ry, MV smearing 0.01 Ry;
- nspin 2 with ferromagnetic starts, MP U values;
- k-points 4×2×1, conv_thr 1e−6, local-TF mixing with β 0.3;
- `calculation = 'scf'` with a fresh atomic + random start;
- 128 ranks with `-nk 8`, a 126-iteration ceiling and 2.5 h per SCF.

The atomic projector is the primary one; the ortho control is not run.

**Acceptance per SCF:**
- converged inside the ceiling;
- no `IEEE_(INVALID|OVERFLOW|DIVIDE_BY_ZERO)_FLAG` note (unchanged rule);
- energy parsed;
- per-site moments recorded.

**Re-runs:**
- A call failed only by the IEEE rule gets one identical re-run (Frank, 2026-10-07).
- A ceiling stop gets one re-run with the probe-selected recipe below. If the probe selects none, it gets no re-run.

**Fe25 convergence probe (runs alongside the production jobs).** Three convergence-path variants are tried on the Fe25 seed-2 clean slab, the one structure known to fail under the production recipe:

| Priority | Variant |
|---|---|
| (a) | `mixing_ndim = 16` |
| (b) | `diagonalization = 'cg'` |
| (c) | U-ramp start: U = 0 SCF, then full U from its density and wavefunctions |

None of the variants changes the Hamiltonian. The first variant, in this priority order, that converges becomes the re-run recipe for ceiling stops. If a variant reaches a different state than a converged production start, that is recorded.

**η.** The project's computational hydrogen electrode with the banked PBE H2O/H2 references (`runs/Cr_slab/H2O.out`, `H2.out`):
- ΔG_OH = ΔE − (E_H2O − ½E_H2) + 0.35
- ΔG_O = ΔE − (E_H2O − E_H2) + 0.05
- ΔG_OOH = ΔE − (2E_H2O − 1.5E_H2) + 0.40
- η = max(ΔG1…ΔG4) − 1.23 V

At fixed census geometry, every adsorbate is intact by construction, because the census admitted only adsorbate-intact sites.

**Alloy value.** C = w₁η₁ + w₂η₂ with arm B's weights:
- if one chain is incomplete, the other site's η is used, flagged single-site;
- if both are incomplete, the alloy has no arm-C value.

The predicted order, and K1 and K2, follow the rules for arms A and B. A hypothesis involving an alloy without a value is reported as *not evaluable under arm C*.

**What it does not claim:**
- *Structures not relaxed.* They are not DFT minima: at MACE geometries, DFT forces are 1.26–1.66 eV/Å.
- *One start per structure.* States about 0.1 eV apart exist at these surfaces, and only one electronic start is run per structure.
- *Projector.* The atomic projector only.
- *Inherited Cr bias.* The DFT+U setup is the one that ranks CrO2 ahead of IrO2 and RuO2, so arm C may inherit a Cr preference. K1 still tests whether that preference survives in real alloys.

### Price

| Block | Calls | Expected SU | Hard ceiling (SU) |
|---|---|---:|---:|
| Fe25 probe | 3 variant SCFs + 1 U = 0 pre-SCF, 1 job | 300–800 | 1,280 (10 h) |
| Production | 40 SCFs, one job per site chain (10 jobs × 10 h) | 4,300 base; 5,500–9,000 with stalls and IEEE re-runs | 12,800 |
| Re-run round | only failed SCFs, probe recipe; 1 job × 15 h, at most 6 SCFs | 0–2,000 | 1,920 |
| **Campaign** | | **6,000–11,000** | **16,000** |

**Basis:**
- 107 SU per SCF (3,000 s);
- 15–30% ceiling stops at about 250 SU wasted each, plus about 10% IEEE re-runs;
- every Slurm limit × 128 cores sums to the ceiling.

**Add-ons:**

| Add-on | Calls | Expected SU | Ceiling |
|---|---|---:|---:|
| Ni34 (keeps the batch-2 route) | 8 SCFs | +1,100–1,800 | +2,560 |
| Each alloy's best site (the registered S8 re-rank gate) | 16 SCFs; Fe25 s2/0 is a known stall | +2,200–3,600 | +5,120 |

### Calendar

| Date | Step |
|---|---|
| Oct 8 | Build the plan snapshot, decks, spec and tests; independent review |
| Oct 8–9 | Stage, preflight, held submit, validation, one release |
| Oct 9–10 | Runs (queue 4–16 h, then ≤ 10 h) |
| Oct 10–11 | Readout and any re-run round |
| Oct 12–13 | Arm-C values and the dated freeze version deposited |

This leaves a week of margin before the Oct 21 fallback. The batch-1 melt does not depend on any of it.

## 4. Decisions for Frank

1. Option: **C-FG** (recommended), C-REL or C-SKIP.
2. Add-ons: Ni34 (yes/no); best sites (yes/no).
3. The SU ceiling for the chosen scope: base C-FG is 16,000 hard, 6,000–11,000 expected.

Nothing is submitted before the usual build, independent review, staging, preflight, held submit, validation and single release.

**Decided** (decision of record at the top): C-FG plus both add-ons, with a 23,680 SU ceiling.

## 5. As built, 2026-10-07

### Package

**Builder:** `src/dft/arm_c_build.py`. It:
- recomputes every site, weight and best site from `per_site.csv`, and refuses if they differ from the approved scope;
- reads the structures from the hash-checked census result files;
- renders the decks through `hea_deck.render_deck`.

Its `--check` mode rebuilds the package in memory and compares it byte for byte with the 70 files below.

| Output | Contents |
|---|---|
| `runs/hea/arm_c_2026-10-07/<alloy>__s<seed>_site<i>/{slab,OH,O,OOH}__atomic.in` | 64 production decks (16 sites × 4 states) |
| `runs/hea/arm_c_2026-10-07/probe__Fe25Co25Ni25Cr25__s2_site0/slab__atomic_{ndim16,hs}.in` | 2 probe decks |
| `runs/m_arm_c_2026-10-07_{main,probe}.txt` | manifests |
| `results/arm_c_2026-10-07/site_plan.json` | site plan: sites, roles, weights, MLIP values, census hashes |
| `results/arm_c_2026-10-07/launch_spec.json` | launch spec |

**Runner:** the unchanged September runner `src/dft/research_batch.py`, schema `research-batch-2026-09-16`, with its pinned helpers. It already applies:
- the 126-iteration ceiling;
- the `IEEE_(INVALID|OVERFLOW|DIVIDE_BY_ZERO)` rejection;
- the one-SCF / one-energy / JOB DONE checks;
- force and moment recording;
- the projection;
- the full HEA QC.

**Slurm:** `anvil/94_arm_c_batch.slurm` pins the spec and runner sha256. It runs one SCF per array task on `wholenode` with 128 ranks and `-nk 8`.

**Operations:**
- `results/arm_c_2026-10-07/launch_ops.py`: stage, preflight, held submit, validate, release. Preflight also requires:
  - the stage receipt and the logs directory;
  - at least 1.5 TB free in the project space (`myquota`), because the runner keeps about 18 GB of wavefunctions per SCF (2.5 TB free on Oct 7);
  - the QE binary sha256 of pw.x, projwfc.x and mpirun as pinned in the spec (pw.x and mpirun equal the O1 pins);
- `status_once.py`, `collect_terminal.py`.

### Changes from §3, made before launch

| Item | Design text | As built | Why |
|---|---|---|---|
| Job layout | one 10 h job per site chain | one 2.5 h array task per SCF (64 tasks, throttle 60) | Same 20,480 SU ceiling; faster wall clock; a stall costs only its own task |
| Per-task limits | 2.5 h per SCF | scf_seconds 8,100, projection_seconds 600, Slurm 2:30:00 | The 126-iteration ceiling binds first: September ceiling stops took 5,782–7,116 s (worst 60.7 s per iteration including setup) and projections 44–56 s |
| Probe variant (c) | U-ramp start | high-spin start (`starting_magnetization = 1.0` on every metal) | The unchanged runner cannot seed a second SCF. Both change only the starting state, not the Hamiltonian |
| Probe variant (b) | `diagonalization = 'cg'` | dropped before launch | Independent review: CG runs about 3× slower per iteration than Davidson (`runs/Co_slab/s0_O.out.attempt3` vs `attempt1`), so it could not finish inside the 2.5 h that any re-run task also has |
| Probe launch | one job | 2 array tasks × 2.5 h = 640 SU | |

**Launch ceiling:** 64 × 2.5 h × 128 + 2 × 2.5 h × 128 = **21,120 SU**. The re-run round is reserved at 1,920 SU (at most 6 SCFs × 2.5 h), for a campaign total of 23,040 SU, within the approved 23,680.

### Registered readout (`src/dft/arm_c_readout.py`)

**Acceptance per SCF.** An SCF counts only if:
- the runner's receipt is COMPLETE;
- the unchanged parser (`hea_panel_readout.parse_out`) reads it as CONVERGED;
- both report the same energy.

**η.** `hea_panel_readout.che_from_energies` with the banked `runs/Cr_slab` H2O/H2.

**Alloy value C, re-run selection and Ni34 nomination:**
- C follows §3.
- **Failure classes,** checked in this order:
  1. CEILING: an iteration or wall-time stop. It is checked first because a stopped run still prints gfortran flag notes.
  2. IEEE: an `IEEE_(INVALID|OVERFLOW|DIVIDE_BY_ZERO)` marker in the receipt, the SCF output or the projection output.
  3. OTHER.
- **Re-run recipe:**

  | Failure | Re-run |
  |---|---|
  | IEEE | identical deck, same job name |
  | CEILING | the first probe variant, in priority order ndim16 → hs, whose SCF is accepted (converged, no IEEE marker); its energy and moments are reported against the production control on the same slab. No re-run if no variant is accepted |
  | OTHER | none |

- **Re-run selection** (`rerun_selection`, ≤ 6 SCFs, deterministic):
  - Only sites whose every failed state is repairable are eligible.
  - Order:
    1. tier: (1) Cu8, Ni31, Fe25 supports; (2) Cu26, Cu22 supports; (3) Ni34 supports; (4) best-only sites;
    2. then fewer failed states;
    3. then site-plan order.
  - Each chosen site re-runs all of its failed states or none. A site that does not fit the remaining slots is skipped, and the next one is considered.
  - **Where re-runs live:** decks go in `runs/hea/arm_c_2026-10-07_rerun/<site>/`. Ceiling re-runs carry the job suffix `_<recipe>` and are built by `arm_c_build.variant_deck`.
  - **Substitution:** a re-run replaces a failed state only if it is accepted. The state then records its recipe, and a chain that mixes recipes is flagged. The high-spin start in particular may reach a different electronic state, so its moments are reported.

- **Ni34 batch-2 nomination,** registered before any result: Ni34Fe6Cu29Co31 is nominated if arm C ranks it first or second of the six alloys. That requires all six values.

### Tests

`tests/test_arm_c.py` checks:
- the build reproduces the committed files byte for byte;
- the sites and weights match the arm-B p10;
- the builder refuses a drifted census;
- every deck is the census structure under the production recipe;
- each probe deck differs only by its registered change;
- the spec pins and shape are as registered;
- the unchanged runner accepts both stages;
- the Slurm pins are current;
- the readout rules: weighted value, single-site fallback, K1/K2/Ni34, acceptance, and failure classes.

### Independent review before launch

The review found no blockers. Its should-fix items are folded in:
- the quota check;
- dropping `cg`;
- the failure-class order and the projection-output IEEE scan;
- the registered re-run selection and substitution;
- binary sha256 pins and the logs-directory and stage-receipt checks;
- try/finally stage receipts;
- LF attributes for the runner helpers.

**Expectations recorded, not acted on:**
- **Cost may run above the expected range.** In September, 2 of 11 atomic HEA SCFs failed on IEEE, both Fe25, which is above the 11% budgeted. Fe appears in 32 of the 64 production SCFs, so failures may outrun the six re-run slots. The SU bound is unaffected.
- **A free reproducibility check.** The Fe25 s2/0 slab, OH and O decks are byte-identical to the September pilot decks. That run gave: slab KILLED at the ceiling, OH converged then rejected for IEEE, O complete at −121279.02432910522 eV.
- **The node exclusions do nothing.** The manifest's exclusion list covers only `shared` nodes (a000–a249); `wholenode` is a250–a999.

140 tests pass with the related QC suites.

## 6. Terminal readout and the full re-run round, 2026-10-07

### Terminal readout (`results/arm_c_2026-10-07/readout.json`, commit 066da3b)

- Both arrays finished, using 10,876.7 SU by sacct.
- 33 of 64 production SCFs were accepted: 28 stopped at the 126-iteration ceiling, 3 were rejected for an IEEE exit note, and none failed otherwise. 4 of 16 sites are complete.
- K1, K2 and the Ni34 nomination all read NOT_EVALUABLE_UNDER_ARM_C. Cu8, Fe25 and Cu26 have no value.
- **Probe:** ndim16 was accepted in 51 iterations on the Fe25 s2/0 slab, whose production control stopped at the ceiling. hs stopped at the ceiling. ndim16 is therefore the ceiling re-run recipe.
- **The registered 6-slot round would not be enough.** It selects the Ni31 s10/2 slab, the Cu8 s26/1 slab, O and OOH, the Cu26 s1/0 O state and the Ni34 s22/0 slab. Even if all six were accepted, Fe25 would have no value, so K1 and K2 would stay not evaluable.
- **Informative traces:** 9 of the 28 ceiling stops were still converging steadily (3 within about two iterations of the threshold). The other 19 were stalled or oscillating.
- The Fe25 s2/0 pattern repeats the September pilot (§5): slab at the ceiling, OH rejected for IEEE, O complete.

### Decision of record

Frank, 2026-10-07: "Go with the full rerun."

**The one change to §5:** the round re-runs every failed state of the terminal readout (31 SCFs) instead of at most 6. Re-running all of them, rather than choosing, keeps the round independent of the values already seen.

**Unchanged:**
- the recipes (CEILING → ndim16, IEEE → identical deck);
- geometries, the 126-iteration ceiling, runtime bounds and the runner;
- the substitution rule and the mixed-recipe flag;
- the alloy value and the K1, K2 and Ni34 rules.

This remains the one re-run round: a state that fails again stays failed.

**Recipe controls (2 SCFs, informative).**
- **What:** the accepted production slab of each site that has both a production slab and a ceiling stop, re-run with ndim16. Those are Fe25 s25/2 and Cu26 s1/0.
- **Why:** they measure whether ndim16 reaches the same SCF solution as production on structures where both converge. The probe's ndim16 slab ended at a total magnetization of 35.95 μB, against about 37.8 μB where production stalled.
- **Reported:** the energy and moment differences, and the site's η with the control slab.

The Fe25 s2/0 slab re-run deck is byte-identical to the converged probe deck, so it also repeats that SCF.

**The three IEEE re-runs may fail again.** All three production SCFs converged (in 61, 65 and 90 iterations) and were rejected only for an IEEE_INVALID_FLAG exit note. Fe25 s2/0 OH ended the same way in the September pilot (`runs/hea/pilot_retained/Fe25Co25Ni25Cr25__s2_site0/OH__atomic.qc.json`). The rule is unchanged: one identical re-run each, at most 960 SU together. One of the three is the Fe25 s25/2 OOH state, at the support site that carries 0.8 of Fe25's weight, so a repeat failure there leaves Fe25 depending on s13/0.

**Pre-launch review** (independent, read-only): no blockers. Folded in before launch:
- the readout records every attempted re-run, accepted or not;
- a re-run readout refuses a missing re-run mirror;
- the controls key is written only for a re-run readout, so the amended module reproduces the committed terminal readout byte for byte (tested);
- this note on the IEEE re-runs.

### Package

| Part | Location |
|---|---|
| Builder | `src/dft/arm_c_rerun_build.py`: built from the committed readout (sha256-pinned), with `--check` |
| Decks | 33 in `runs/hea/arm_c_2026-10-07_rerun/`: 28 ceiling re-runs, 3 IEEE re-runs, 2 controls |
| Manifest | `runs/m_arm_c_2026-10-07_rerun.txt` |
| Spec and plan | `results/arm_c_2026-10-07_rerun/launch_spec.json` and `rerun_plan.json` |
| Slurm | `anvil/95_arm_c_rerun.slurm`, with the production resources |
| Operations | `launch_ops.py`, `status_once.py` and `collect_terminal.py` for the Anvil root `sts_arm_c_2026-10-07_rerun`; array 1-33%33, 2.5 h per task |

**Cost:** the ceiling is 33 × 2.5 h × 128 = **10,560 SU**. With the 10,876.7 SU already spent, the campaign bound is 21,436.7 SU, inside the approved 23,680.

**Readout:**

```
python src/dft/arm_c_readout.py --plan results/arm_c_2026-10-07/site_plan.json \
  --mirror results/arm_c_2026-10-07/raw_mirror \
  --rerun-plan results/arm_c_2026-10-07_rerun/rerun_plan.json \
  --rerun-mirror results/arm_c_2026-10-07_rerun/raw_mirror --out <readout.json>
```

**Tests:** `tests/test_arm_c_rerun.py` (10 tests) checks:
- build reproducibility;
- full coverage with the registered recipes and order;
- the control rule;
- that each deck is the production bytes or the one-line variant;
- the repeat of the probe deck;
- the spec shape, ceiling and campaign bound;
- runner acceptance;
- the Slurm pins and resources;
- the operations targets;
- substitution and the control readout on fake mirrors.

150 tests pass with the related suites.

## 7. Re-run readout: arm C is terminal, 2026-10-08

Array 21176478 ran on 2026-10-07 from 19:04 to 21:53 Anvil time. All 33 tasks ended: 9 converged and 24 stopped. It used **6,523.1 SU** of its 10,560 ceiling (sacct CPUTimeRAW, equal to the `mybalance` drop). Arm C used **17,399.8 SU** in total, inside the approved 23,680. The balance afterwards is 17,775.2 SU (`mybalance`, 2026-10-08 05:08Z).

The collection (`terminal_collection.json`) holds 174 files, and every remote and local sha256 matches. As in §6, the 9 projection outputs (88 MB) stay local.

### Registered readout (`results/arm_c_2026-10-07_rerun/readout.json`)

| | Round 1 | After the re-run |
|---|---|---|
| SCFs accepted | 33 / 64 | **40 / 64** |
| Sites complete | 4 / 16 | **6 / 16** |
| Re-runs accepted | — | 7 / 31: 5 of 28 ndim16 ceiling re-runs, 2 of 3 identical IEEE re-runs |
| Final failures | 31 | 24: 22 iteration-ceiling stops, 2 IEEE notes |

| Alloy | C value (V) | Basis | Mixed recipe |
|---|---|---|---|
| Cu26Ni9Cr31Co33 | 0.613 | one site: s1/0, weight 0.8 (s17/1 incomplete) | yes (O by ndim16) |
| Ni31Cr29Cu5Mn35 | 0.934 | two sites: s1/0 0.768 × 0.3, s10/2 1.006 × 0.7 | yes (s10/2 slab by ndim16) |
| Cu22Fe30Co32Mn15 | 0.942 | one site: s24/3, weight 0.7 (s6/1 incomplete) | no |
| Ni34Fe6Cu29Co31 | 1.281 | one site: s29/1, weight 0.4 (s22/0 incomplete) | no |
| Cu8Cr23Mn35Co34 | — | no value: s16/2 and s26/1 both incomplete | — |
| Fe25Co25Ni25Cr25 | — | no value: s13/0 and s25/2 both incomplete | — |

**K1, K2 and the Ni34 nomination: NOT_EVALUABLE_UNDER_ARM_C.** This was the one re-run round, so the reading is final. The order Cu26 < Ni31 < Cu22 < Ni34 is descriptive only: three of the four values rest on one site, and Ni31 and Cu22 differ by 8 mV, far inside DFT+U error.

**Best-site checks:**
- Complete: Cu8 s20/2 (0.621 V) and Ni31 s1/0 (0.768 V).
- Not complete:
  - Fe25 s2/0: slab ceiling, OH IEEE.
  - Cu26 s5/2: slab ceiling.
  - Cu22 s27/3: all four states hit the ceiling.

**Recipe controls (informative).** Both ndim16 repeats of accepted production slabs reproduced them:
- Fe25 s25/2: −0.10 meV and +0.01 μB.
- Cu26 s1/0: +0.08 meV and 0.00 μB; its η moves by 0.08 mV.

The two mixed-recipe chains (Cu26 s1/0, Ni31 s10/2) therefore carry no recipe offset at the meV level.

**Descriptive, not a registered test: DFT against MLIP at the six complete sites.**

| Site | MLIP η (V) | DFT η (V) | DFT − MLIP (V) |
|---|---|---|---|
| Cu26 s1/0 | 0.479 | 0.613 | +0.13 |
| Cu8 s20/2 | 0.362 | 0.621 | +0.26 |
| Ni31 s1/0 | 0.440 | 0.768 | +0.33 |
| Cu22 s24/3 | 0.842 | 0.942 | +0.10 |
| Ni31 s10/2 | 0.487 | 1.006 | +0.52 |
| Ni34 s29/1 | 0.786 | 1.281 | +0.49 |

The MLIP sits below DFT at every site, by 0.10 to 0.52 V. The offset changes from site to site, so it is not a constant shift.

### Why the SCFs stop

- **Same deck, different answer.** The Fe25 s2/0 slab re-run deck is byte-identical to the probe deck that converged in 51 iterations (same sha256 `c02740c0…`).
  - The setup matched: the same 128-rank, 8-pool layout and 486 randomized atomic starting wavefunctions. Only `outdir` differs.
  - The two runs already differ in the first iteration, by 3e-5 Ry. They separate into different magnetic states between iterations 12 and 16.
  - The probe converged at 35.95 μB. The re-run stalled at 37.78 μB, with its residual held near 1e-5 Ry from about iteration 50 to the ceiling. That is the state the production slab stopped in: the same moment, and an energy within 1e-6 Ry.
  - The stalled state lies 33.8 meV above the converged one.
  - So the probe converged because of the magnetic state it fell into, not only because of the mixing setting. This is the same branch instability as R3 (`tasks/todo.md`, 2026-08-26 entries: the same deck on the same machine gave a different answer).
- **Two kinds of stop.**
  - 9 of the 22 ceiling stops sat in one magnetic state. Over the last 20 iterations, their residual stayed between 5e-6 and 1.2e-4 Ry and the energy stayed within 10 meV.
  - The other 13 never settled: residuals reached 2e-4 to 6e-2 Ry, and the energy swung 19–461 meV over the same window.
- **No post hoc rescue.** Accepting every near-threshold stall would still leave Cu8 and Fe25 without a value. Each of their four support sites has at least one state that never settled. So no relaxation of the acceptance rule changes K1, K2 or the Ni34 call.
- **IEEE notes.**
  - Fe25 s2/0 OH ended with IEEE_INVALID_FLAG for the third time (September pilot, round 1, this repeat), each time after converging.
  - Fe25 s25/2 OOH and Cu26 s5/2 O passed on their repeat.
  - One ndim16 run, Cu22 s6/1 O, converged in 92 iterations and then ended with the same note.

### Package additions

| Part | Location |
|---|---|
| Status snapshot | `status_snapshot_20261008T050812Z.json` |
| Collection | `terminal_collection.json`, `raw_mirror/` (projection outputs local) |
| Readout | `readout.json` (LF-pinned), `readout.job.json`, `readout.log` |
| Test | `tests/test_arm_c_rerun.py::test_the_rerun_readout_reproduces_the_committed_rerun_readout` rebuilds the readout byte for byte from both mirrors; it is skipped when the projection outputs are absent |

`tests/test_arm_c_rerun.py` holds 14 tests. 154 pass with `test_arm_c`, `test_hea_force_audit`, `test_hea_followup_qc` and `test_hea_panel`.

**After this readout (2026-10-08):**
- **Six alloys.** The freeze proposal now covers six alloys (Ni34 added), so the "five alloys" in the introduction and §3 describe the design at the time.
- **Deposit.** Arm C's readout is deposited with the freeze itself.
- **Oct 21 fallback.** It now applies to the targeted extension round for Cu8 and Fe25 (Frank: "Let's rerun DFT for those and get values for them."; freeze proposal §4b).
