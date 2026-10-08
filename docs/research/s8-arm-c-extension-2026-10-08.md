# S8 arm C extension — seeded SCFs for Cu8 and Fe25, 2026-10-08

Status: **built, tested and independently reviewed (no blockers; its eight should-fix items are folded in); launch in progress.**

Decision of record: Frank, 2026-10-08: "Let's rerun DFT for those and get values for them." It came after arm C's final readout (`results/arm_c_2026-10-07_rerun/readout.json`, commit 2229549; [design doc](s8-arm-c-dft-design-2026-10-07.md) §7) left Cu8Cr23Mn35Co34 and Fe25Co25Ni25Cr25 without a value.

The extension is **exploratory** ([freeze proposal](s8-stage1-freeze-proposal-2026-10-07.md) §4b):
- Arm C's registered readings stay final: K1, K2 and the Ni34 nomination are not evaluable.
- Any values it adds, and the DFT readings of K1 and K2 they allow, are frozen as exploratory predictions when this readout is deposited, before any OER measurement. The Oct 21 fallback applies.

## Scope

The 11 SCFs still failed at the four support sites (all CEILING stops in both rounds):

| Site | Weight | Missing states | Seed (accepted state at the same site) |
|---|---|---|---|
| Cu8 s16/2 | ½ | slab, OH, OOH | O (re-run, ndim16) |
| Cu8 s26/1 | ½ | slab, O, OOH | OH (production) |
| Fe25 s13/0 | ⅕ | OH, O, OOH | slab (re-run, ndim16) |
| Fe25 s25/2 | ⅘ | OH | OOH (identical re-run) |
| Fe25 s25/2 | ⅘ | O | slab (production) |

**Seed rule:** the accepted state at the same site with the fewest differing atoms. A tie would stop the build; none occurs.

## Why this recipe

The project's own record of SCF rescues, compiled for this decision:

| Start or setting | Converged | Note | Source |
|---|---|---|---|
| Density of a neighbouring Hubbard-U run (same structure), A0 rung (i) | 2 of 4 | the closest precedent: a seed from a different calculation; u300_r1 and u450_r2b converged, u450_r1 and r2 stopped at 200 iterations | `docs/45-error-ledger.md`:2244–2256, 2286–2296; `docs/59-a0-roster-correction-2026-08-28.md`:231–243 |
| Converged density of the same structure (replays, checkpoint restarts) | 17 of 17 | starts at an already converged solution, so it says little about a different structure; 2 then rejected for IEEE notes | `docs/45-error-ledger.md`:206–220, 567–617; [hea-numerical-2026-09-08.md](hea-numerical-2026-09-08.md):85–100 |
| The run's own stalled density | 0 of 13 | the stall returns within 1–3 iterations | [lowtail-clean-slab-scf-stall-2026-09-19.md](lowtail-clean-slab-scf-stall-2026-09-19.md):85–113 |
| mixing_ndim 16 | 5 of 28 here | the identical deck converged once and stalled once | arm C design doc §7 |
| mixing_beta 0.15 to 0.05 | 3 of 21 (and 0 of 32 Ru rows) | left worse residual floors on Cu8 and Fe25 | `docs/45-error-ledger.md`:145–201, 2619–2637 |
| electron_maxstep 500 | 3 of 11 | | `docs/45-error-ledger.md`:307–333 |

**Expectation.** A seed is the best-supported start the project has, but this one comes from a different adsorbate state. Read the closest precedent (2 of 4) as the realistic rate, not the 17 of 17.

**The recipe** is the production deck, unchanged, except:
- its own prefix;
- one added line, `startingpot = 'file'`, so QE starts from the seed's converged density;
- a runner iteration cap of 200, instead of 126, with an SCF wall of 12,600 s.

Everything else is kept: geometry, PBE+U values, cutoffs, k-points, smearing, local-TF mixing at β 0.3, conv_thr 1e-6 and atomic+random wavefunctions.

**What is new.** Seeding across structures (a seed with a different adsorbate) has not been done in this project before. A canary checks it first (below).

## Rebuilt occupations

**QE 7.5's `read_scf` needs three files.** With `startingpot = 'file'` it reads:
- the density;
- `occup.txt`, the DFT+U occupations, ns(5, 5, 2, nat);
- `paw.txt`, the PAW becsum(171, nat, 2).

It stops if either of the last two is missing or short. They have to be rebuilt for the target's atom list.

**Layout, verified on the five seeds and ten failed-target saves:**
- Every `occup.txt` holds exactly 50·nat values, and its blocks are zero for exactly the atoms without U (Cu, O, H).
- Every `paw.txt` holds 171·nat·2 values. The nonzero extent of each 171-value block depends only on species (metals 171, O 36, H 3) and agrees in both spin halves.
- In all four states, the first 72 atoms are the slab in a common species order, and the adsorbate atoms follow. The geometries differ: each state was relaxed on its own, and slab atoms, including the adsorption-site metal, move by up to 0.89 Å between seed and target.

**Mapping, target atom ← seed:**
- The 72 slab atoms keep the seed's blocks.
- An adsorbate atom keeps the seed's block for the same role (O1, O2, H).
- A second O takes the seed's first adsorbate O.
- A new adsorbate O takes the nearest slab O (minimum image in the surface plane).
- A new H starts at zero. H has an ultrasoft pseudopotential, not PAW, so its becsum block is a starting value only.

Adsorbate occupations are zero in every case, because O and H carry no U. The density file is copied unchanged; QE renormalises its charge to the target's electron count.

**Checks against the ten target layout references:**
- the rebuilt files match them in size;
- they match them in each element's block pattern, except a new H, which is zero by design (the reference has 3 nonzero values);
- the slab blocks equal the seed's.

## Launch design

**Runner.** `src/dft/research_batch_seeded.py`, the pinned sibling of the arm C runner.
- It content-pins the seed files, copies them into the job's fresh scratch, and refuses any drift.
- For stage kind "hea" its acceptance is the same code as arm C's: one converged SCF, no failure or IEEE marker, the force audit, the projection, the complete HEA QC, and density retention.

**Bundles.** Each target's seed bundle is `results/arm_c_ext_2026-10-08/seeds/<site>/<state>/`:
- the rebuilt `occup.txt` and `paw.txt` come from git;
- the seed's `charge-density.hdf5` and `data-file-schema.xml` are copied on Anvil from the arm C roots at staging, then verified against the sha256 values fetched on 2026-10-08 (`seed_fetch.json`).

**Two held arrays:**

| Array | Tasks | Limits | Ceiling |
|---|---|---|---|
| `ext_canary` | 2 | eight iterations, 25 min | 106 SU |
| `ext_main` | 11 | 200 iterations, 225 min | 5,280 SU |

The two canaries cover both rebuild directions:
- Cu8 s16/2 slab, from a seed with one more atom;
- Fe25 s13/0 OOH, from a seed with three fewer atoms, two of them new PAW O.

**Canary gate (`canary_check.py`).** Both canaries must:
- report "The initial density is read from file";
- print no QE error;
- raise no IEEE_INVALID, OVERFLOW or DIVIDE_BY_ZERO note, since such a note would reject every main run;
- run at least three iterations;
- stop at the eight-iteration ceiling, or complete;
- be ahead of the production run at the same iteration. Production started from atomic densities, and its accuracy at iteration 8 was 4.60 Ry (Cu8 s16/2 slab) and 11.41 Ry (Fe25 s13/0 OOH). A first-iteration comparison would pass for any seed QE reads.

The check writes nothing until both canaries have runner receipts, so an early run cannot block the gate. It records each canary's moments next to its seed's. `release main` refuses to run until the check has passed.

**Iteration cap in practice.** The SCF wall of 12,600 s binds before iteration 200 for the slowest states: Fe25 s25/2 OH and O ran at 68–69 s per iteration in production, which reaches the wall near iteration 185–190.

**Bad nodes.** Both arrays are submitted with `--exclude` set to the spec's list of known bad nodes, and validation checks it. The arm C rounds named this list in their manifests but did not pass it.

**Cost.**
- The ceiling is 106 + 5,280 = **5,386 SU**.
- With the 17,399.8 SU already spent on arm C, the campaign bound is 22,785.8, inside the approved 23,680.
- Balance before launch: 17,775.2 SU.

## Readout

`src/dft/arm_c_readout.py` gains `--ext-plan` and `--ext-mirror`. They apply this round after the re-run round, to states that are still failed, under the same acceptance and substitution rules.
- A replaced state carries the recipe "seeded", or "unseeded_fallback" if QE did not report reading the seed.
- Each extension attempt records:
  - `save_written`: QE wrote its own save, as shown by "Writing all to output data dir" with the job's own save path. The runner's retention check cannot show this for a seeded job, because the seed's files sit in the save from the start.
  - `beyond_registered_cap`: the SCF converged after arm C's 126-iteration cap.
- Each alloy records `uses_extension`.
- The readout is written with the schema `s8-arm-c-ext-readout-v1`. It reports its K1, K2 and Ni34 readings as `exploratory_predictions`.
- Without these flags, both existing readouts are reproduced byte for byte (tested).

```
python src/dft/arm_c_readout.py --plan results/arm_c_2026-10-07/site_plan.json \
  --mirror results/arm_c_2026-10-07/raw_mirror \
  --rerun-plan results/arm_c_2026-10-07_rerun/rerun_plan.json \
  --rerun-mirror results/arm_c_2026-10-07_rerun/raw_mirror \
  --ext-plan results/arm_c_ext_2026-10-08/ext_plan.json \
  --ext-mirror results/arm_c_ext_2026-10-08/raw_mirror --out results/arm_c_ext_2026-10-08/readout.json
```

## Risks

- **Branch inheritance.** A seeded state usually keeps the seed's magnetic branch, and seeding does not break a tie between branches.
  - Seeded or restarted runs in this project have landed −77 and +173 meV from independent runs.
  - Same-geometry branch gaps reached −384.3 meV (Fe s0_OOH, tasks/todo.md, 2026-08-26) and +747.4 meV (Co s0_OOH, `docs/45-error-ledger.md`:847, 923).
  - Fe25 s2/0's two branches differ by 33.8 meV (arm C design doc §7).
- **The active site starts misplaced.** The adsorption-site metal moves 0.57–0.89 Å between seed and target in 6 of the 11 pairs, so the copied density and that metal's occupations start in the wrong place exactly where the chemistry is:
  - Cu8 s16/2: slab, OH, OOH;
  - Cu8 s26/1: O;
  - Fe25 s13/0: O;
  - Fe25 s25/2: O.
- **One attempt per state.** There are no retries. A state that fails again stays failed, and the alloy keeps no value or a one-site value.
- **IEEE notes.** About 1 in 9 calls ends with an IEEE note (O1 readout). Those are rejected under the unchanged rule.
- **The adsorbate region starts wrong.** The seed has a different adsorbate. The canary tests only whether the seed keeps a run ahead of the production start for eight iterations; it cannot show convergence.

## Package

| Part | Location |
|---|---|
| Builder | `src/dft/arm_c_ext_build.py`, with `--check` (39 files) |
| Decks | `runs/hea/arm_c_ext_2026-10-08/` (11), plus `canary/` (2) |
| Manifests | `runs/m_arm_c_ext_2026-10-08_{canary,main}.txt` |
| Seeds | `results/arm_c_ext_2026-10-08/seed_files/` (fetched), `seeds/` (rebuilt), `seed_fetch.json` |
| Spec, plan | `launch_spec.json`, `ext_plan.json` |
| Slurm | `anvil/96_arm_c_ext.slurm`, with the production resources |
| Operations | `launch_ops.py` (stage with seed copies, preflight, held submit, validate, release canary/main), `canary_check.py`, `status_once.py`, `collect_terminal.py` |
| Tests | `tests/test_arm_c_ext.py`, 14 tests; 168 pass with the arm C and HEA QC suites |
