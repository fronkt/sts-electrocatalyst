# S8 arm C extension — seeded SCFs for Cu8 and Fe25, 2026-10-08

Status: **round 2 built and independently reviewed (no blockers; findings folded in), 2026-10-08 (Frank: "repair"): the seed densities are moved onto the target's atoms; offline, on 7 converged pairs (14 directions) at two sites, the moved start lies 31–77× closer to the converged density than production's atomic start ([Round 2](#round-2-repair-2026-10-08)). Round 1's canary failed and its main array was cancelled before it ran.**

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

## Canary readout, 2026-10-08: failed; main held

**Runs.**
- Canary array 21181502 ran 13 min 05 s (a753) and 20 min 41 s (a755): 72.0 SU. The balance went from 17,775.2 to 17,703.2 SU.
- `canary_check.json` records `passed: false`, so `release main` refuses. Main array 21181503 is still held.
- The first gate run stopped on a wrong production-output path before writing anything. The path now comes from `production_output()` (tested), and the gate was re-run.

| | Cu8 s16/2 slab | Fe25 s13/0 OOH |
|---|---|---|
| Seed | O (73 atoms) | slab (72 atoms) |
| Seed read; QE errors; IEEE notes | yes; none; none | yes; none; none |
| Starting charge, renormalised to | 656.0 → 650.0 | 678.0 → 691.0 |
| Iterations completed, stop | 8, iteration ceiling | 3, SCF wall (1,231 s) |
| Accuracy at iteration 1, seeded vs production | 4,110 vs 460 Ry | 55,573 vs 299 Ry |
| Accuracy at the last iteration, seeded vs production | 247 vs 4.60 Ry (iteration 8) | 6,467 vs 145 Ry (iteration 3) |
| Total magnetization after iteration 1 (seed converged) | 2.0 μB (49.6) | 14.8 μB (51.3) |
| Hubbard d occupation, start → after iteration 1 | 133.7 → 154.7 | 161.3 → 39.8 |
| Hubbard moments, start → after iteration 1 | 51.5 → 0.6 μB | 51.9 → 5.4 μB |
| Negative charge after iteration 1 (up, down) | 0.02, 0.04 e | 10.6, 10.7 e |
| Gate | fails: behind production | fails: behind production, and stopped at the wall |

Fe25's first iteration took 738 s. From a file density QE starts the diagonalisation at ethr 1e-5, and the atomic+random wavefunctions needed 59 Davidson steps on average. Production's first iteration took 33 s.

**What went wrong.** QE read the seed's plane-wave density as it was and only rescaled it to the target's electron count. The rebuild had carried over the atom-centred parts (Hubbard occupations, PAW becsum). The density itself still described the seed's adsorbate:
- Cu8 s16/2 slab: the removed O's six electrons stayed above the site with no nucleus under them.
- Fe25 s13/0 OOH: the OOH's 13 valence charges had no electrons on them. The rescaling spread the missing 13 over the slab.

The first diagonalisation then overfilled (Cu8) or emptied (Fe25) the metal d shells and quenched the moments. The error grows with the misplaced charge: 6 electrons gave 4,110 Ry, 13 gave 55,573 Ry. The design's assumption under "Rebuilt occupations", that the density file can be copied unchanged, is what failed.

**Displacement is secondary.** Slab atoms moved little between seed and target:
- Cu8: RMS 0.12 Å. One metal (Cr, atom 19) moved 0.85 Å; no other atom moved more than 0.29 Å.
- Fe25: RMS 0.06 Å, with no atom past 0.26 Å.

Fe25 still had the much larger error.

**Consequence.** The 11 states stay failed, and Cu8 and Fe25 still have no value. Arm C's registered readings are unchanged.

**Repair candidate (adopted as round 2, below).** Move the density with the atoms, as QE does between ionic steps (`pot_extrapolation = 'atomic'`): subtract the superposed atomic densities at the seed's atoms and add them at the target's, using each species' UPF atomic density.
- The result integrates to the target's electron count, so no rescaling is needed, and the adsorbate's charge sits on its atoms.
- The rebuilt occupations and becsum stay as they are.
- It needs the five seed densities and the UPFs from Anvil.
- It needs a new canary, with a wall that allows the slower first iteration from a file density, and the gate unchanged.

Ceilings: about 190 SU for the canary and 5,280 SU for the main array. With the 17,471.8 SU spent so far, the campaign bound is about 22,940 SU, inside the approved 23,680.

## Round 2 (repair), 2026-10-08

Decision of record: Frank, 2026-10-08: "repair".
- Round 1's main array 21181503 was cancelled before it ran: 0 SU (`results/arm_c_ext_2026-10-08/cancel_receipt.json`, status snapshot 19:58Z).
- Round 2 runs the same 11 SCFs from the same seeds, changing only the density each job reads.

**The move.** `src/dft/qe_density_move.py` puts each seed's converged density on the target's atoms:

ρ(G) = ρ_seed(G) − Σ_seed atoms f_s(|G|) e^(−iG·τ)/Ω + Σ_target atoms f_s(|G|) e^(−iG·τ)/Ω

- This is QE's own charge extrapolation between ionic steps (`update_pot.f90`, `pot_extrapolation = 'atomic'`), extended to atoms that appear or vanish.
- f_s is QE's atomic charge form factor: the UPF `PP_RHOATOM` integrated with QE's Simpson rule over QE's msh points (the first mesh point beyond 10 bohr, rounded down to an odd count).
- The moved density integrates to the target's electron count, within 1.2×10⁻⁵, so QE no longer rescales it.
- The magnetization density is carried over unchanged. QE's own extrapolation instead keeps ζ = m/(ρ + ρ_core) fixed (`update_pot.f90`). Here atoms are added in vacuum, where ζ is a ratio of two vanishing densities, so the added charge would take an arbitrary polarisation; carried over, it starts unpolarised.
- The occupations and becsum are round 1's, byte for byte. Both are atom-centred, so they already moved with their atoms.
- The file is the seed file with only the stored `rhotot_g` values replaced.

**Offline validation, before any SU** (`results/arm_c_ext_r2_2026-10-08/density_validation.json`):
- The atomic charges reproduce the starting charge QE printed for all eight production atomic starts used here, to 10⁻⁴ (for example 631.9986 for the Cu8 s20/2 slab).
  - The GBRV metal pseudopotentials' atomic densities hold 0.5–2 electrons fewer than their valence charge, which is why every production start is rescaled by 3–4%.
- Each fetched density integrates to its state's electron count, and its magnetization to the run's final moment.
- Moving a density onto its own atoms returns it exactly.
- The distance from each start to the converged density was measured for 7 pairs of converged states, in both directions (14):
  - Cu8Cr23Mn35Co34 s20/2: all 12 directions between its four states;
  - Fe25Co25Ni25Cr25 s25/2: slab ↔ OOH.
  - The distance is the plane-wave part of QE's measure behind "estimated scf accuracy" (`rho_ddot`, over the G vectors QE mixes). QE also adds Hubbard and PAW terms, left out here.
  - The moved residual only changes sign with the direction, so the 14 directions hold 7 independent moved distances.

| Start | Distance to the converged density | Charge part only |
|---|---|---|
| Round 1: seed density copied and rescaled | 41–144 Ry | 41–143 Ry |
| Production: superposed atomic densities, deck moments, rescaled | 21.5–29.0 Ry | 4.4–8.3 Ry |
| Round 2: seed density moved | 0.29–0.70 Ry | 0.11–0.31 Ry |

The two pairs in the canaries' directions:
- Cu8 s20/2 O → slab (one O removed): copied 141.1, atomic 21.5, moved 0.70 Ry.
- Fe25 s25/2 slab → OOH (three atoms added): copied 127.4, atomic 29.0, moved 0.45 Ry.

**What this shows and what it does not.**
- It does show:
  - Round 1's copied start was far worse than the atomic start, matching the canary.
  - The moved start begins 31–77× closer to a converged density than production's start, on the 7 pairs tested.
- It does not show that the 11 stalled states will converge, nor test the launch densities themselves (no converged reference exists for them):
  - Their stalls arose from atomic starts. Converged-density restarts of the same structure converged 17 of 17; the closest precedent with a different seed converged 2 of 4.
  - The canary tests the start inside QE first.

**Negative spin density in the moved starts.** Where an atom is removed, or a site metal moved, the magnetization stays where the charge was taken out, leaving negative spin density (`canary_expectations.json`):
- Fe25 s25/2 O 0.46 e, Fe25 s13/0 O 0.34 e, Cu8 s16/2 slab (a canary) 0.32 e, Cu8 s26/1 O 0.27 e; the other seven 0.02–0.17 e.
- The seeds hold 0.005–0.025 e.
- QE prints this and continues (`v_of_rho.f90`); round 1's Fe25 canary ran on through 10.6 e. The Cu8 canary tests this case.

**Launch design (round 2).**
- **Names.** Root `sts_arm_c_ext_r2_2026-10-08`, jobs `<state>__atomic_moved` and Slurm `anvil/97_arm_c_ext_r2.slurm`, which pins the round-2 spec and the unchanged seeded runner. The resources and the exclusion list are round 1's.
- **Staging.** The 11 moved densities (about 153 MB each, outside git) are uploaded and checked against the spec's sha256 pins before and after transfer. The seeds' XML files are copied on Anvil, as in round 1.
- **Canary.** Eight iterations with a 2,400 s SCF wall and a 45 min Slurm wall. Round 1's first iteration from a file density took up to 738 s, because QE starts the diagonalisation at ethr 1e-5.
  - The gate is round 1's (the seed is read, no QE error, no severe IEEE note, at least three iterations, a stop at the iteration ceiling or completion, and a lead over production at the same iteration) plus one line: QE read the moved file as built. Before its first iteration it must print no "renormalised" line, and its "negative rho (up, down)" must match `canary_expectations.json` within 1%: 7.515E-02 3.168E-01 (Cu8 slab) and 4.059E-03 2.258E-02 (Fe25 OOH). The same FFT, rescaled as QE did, reproduces round 1's printed values (6.936E-03 2.243E-02; 4.593E-03 2.202E-02).
  - The check also records whether each canary stopped gracefully ("JOB DONE."). gfortran prints its IEEE notes only then, so for a killed run the IEEE line shows nothing.
- **Main array.** Round 1's limits: 200 iterations, a 12,600 s SCF wall and 225 min.
- **Cost.**
  - Ceilings: 192 SU (canary) + 5,280 SU (main) = 5,472 SU.
  - Spent before launch: 17,471.8 SU (arm C 17,399.8 + round-1 canary 72.0).
  - Campaign bound: 22,943.8 SU, inside the approved 23,680. Balance: 17,703.2 SU.
- **Readout.** The plan rows carry `seed_density: "moved"`, and the readout records it on each extension attempt (`"copied"` for round-1 plans). The readout command is the one under Readout, with `results/arm_c_ext_r2_2026-10-08/` in place of `results/arm_c_ext_2026-10-08/`.

| Part | Location |
|---|---|
| Density move | `src/dft/qe_density_move.py` |
| Builder | `src/dft/arm_c_ext_r2_build.py`, with `--check` (39 files; also the 11 densities when the seed densities are present) |
| Inputs | `results/arm_c_ext_r2_2026-10-08/density_fetch.py` and `density_fetch.json` (9 densities, 8 UPFs, sha256-checked; files kept locally) |
| Validation | `results/arm_c_ext_r2_2026-10-08/density_validation.py` and `density_validation.json`; `canary_expectations.py` and `canary_expectations.json` (the start QE should print for each moved density) |
| Decks, manifests | `runs/hea/arm_c_ext_r2_2026-10-08/` (11, plus `canary/` 2) and `runs/m_arm_c_ext_r2_2026-10-08_{canary,main}.txt` |
| Spec, plan, operations | `results/arm_c_ext_r2_2026-10-08/` (`launch_spec.json`, `ext_plan.json`, `launch_ops.py`, `canary_check.py`, `status_once.py`, `collect_terminal.py`) |
| Tests | `tests/test_arm_c_ext_r2.py`, 20 tests; 188 pass with the arm C and HEA QC suites |
