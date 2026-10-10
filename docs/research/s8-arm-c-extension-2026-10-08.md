# S8 arm C extension — seeded SCFs for Cu8 and Fe25, 2026-10-08

Status: **round 4 read out, 2026-10-10: the Fe25 s25/2 O converged in 20 iterations, so Fe25 has an exploratory single-site value, 0.893 V. Cu8 still has none, so K1, K2 and the Ni34 nomination stay not evaluable ([Round 4 readout](#round-4-readout-2026-10-10-the-fe25-o-converged-fe25-has-a-single-site-value)).** Round 4 (Frank: "Do the Fe25 O run") started Fe 22 in the configuration the site's OH and OOH share. Before it:
- round 3 converged neither of its two states ([Round 3 readout](#round-3-readout-2026-10-10-neither-state-converged-no-value));
- round 2 converged 3 of 11 ([Round 2 main readout](#round-2-main-readout-2026-10-09-3-of-11-converged-no-value)). Round 2 (Frank: "repair") moves each seed density onto the target's atoms;
- round 1's canary failed, and its main array was cancelled before it ran.

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

## Round 2 canary readout, 2026-10-08: passed; main released

**Staging.** The first stage run was killed when the local machine ran critically low on memory. By then it had put 43 files and 3 of the 11 densities on Anvil, plus one partial density, and it wrote no receipt (`stage_probe_20261008T212434Z.json`). After Frank said "Resume", three passes of `launch_ops.py resume` replaced the partial file and sent the rest, verifying every file against its pin; `stage_receipt.json` records the result. Preflight passed. The balance was 20,193.2 SU, because Anvil raised the allocation limit from 100,000 to 102,490 SU while usage stayed at 82,296.8.

**Runs.** Canary array 21195260 ran on a303 and a310; the two tasks finished after about 9.5 and 11.5 min. `canary_check.json` records `passed: true`, and main array 21195261 was released.

| | Cu8 s16/2 slab | Fe25 s13/0 OOH |
|---|---|---|
| Read as built: "negative rho (up, down)", printed vs predicted | 7.515E-02 3.168E-01 vs 0.075152 0.316813 | 4.059E-03 2.258E-02 vs 0.004059 0.022581 |
| Rescaled ("renormalised") | no | no |
| QE errors; IEEE notes; graceful stop | none; none; yes | none; none; yes |
| Accuracy at iteration 1: moved vs production (round 1 copied) | 3.44 vs 460 Ry (4,110) | 1.13 vs 299 Ry (55,573) |
| Accuracy at iteration 8: moved vs production (round 1 copied) | 0.0114 vs 4.60 Ry (247) | 0.0069 vs 11.41 Ry (round 1 stopped at 3) |
| Total magnetization at iteration 8 (seed converged) | 51.09 μB (49.63) | 50.31 μB (51.34) |
| Gate | passed | passed |

**What this shows.**
- QE read the spliced files exactly as built.
- The moved start keeps the seed's magnetic state; round 1's collapsed to 2 and 15 μB.
- After eight iterations each run is ahead of production by more than two orders of magnitude.

**What it does not show.**
- The production runs of these states stalled with the accuracy hovering around 10⁻³–10⁻² Ry (Cu8 slab: median of the last 40 iterations 1.4×10⁻²; its ndim16 re-run 1.8×10⁻³) and 10⁻⁴–10⁻³ Ry (Fe25 OOH: 9.9×10⁻⁴; re-run 7.8×10⁻⁴), never reaching conv_thr 10⁻⁶ in 126 iterations.
- The canaries reached 0.011 and 0.007 Ry in eight iterations; production and its ndim16 re-runs first reached those levels at iterations 20–29, then stalled. Whether the seeded runs get past the level where production stalled is what the main array shows.

## Round 2 main readout, 2026-10-09: 3 of 11 converged; no value

**Runs.** Main array 21195261 ran its 11 tasks on 11 nodes between a604 and a616. Slurm lists the runner's rejections as `FAILED` (exit 10).
- Converged:
  - Cu8 s16/2 OH and OOH: 33 and 31 iterations, about 32 min each;
  - Fe25 s25/2 OH: 61 iterations, 60 min.
  - All three converged inside arm C's registered 126-iteration cap and wrote their own saves.
- The other eight stopped at the 200-iteration ceiling after 2.6–3.5 h.
- There were no QE errors. The only IEEE notes are underflow and denormal; none is invalid, divide-by-zero or overflow.

**Cost.**
- Round 2 used 3,416.7 SU (sacct CPU time), inside its 5,472 SU ceiling: canary 43.59, main 3,373.16.
- The campaign has used 20,888.5 SU of the approved 23,680.
- Balance: 16,776.5 SU (`mybalance`, 2026-10-09 04:32Z).

**Readout.** `readout.json` comes from the command under Readout, with this round's plan and mirror.
- 43 of 64 SCFs are accepted, up from 40.
- 6 of 16 sites are complete, unchanged.
- Every extension job read its moved file.

| Support site | Accepted before round 2 | Round 2 | Still missing |
|---|---|---|---|
| Cu8 s16/2 | O (ndim16 re-run) | OH and OOH converged; slab stopped | slab |
| Cu8 s26/1 | OH (production) | slab, O and OOH stopped | slab, O, OOH |
| Fe25 s13/0 | slab (ndim16 re-run) | O, OH and OOH stopped | O, OH, OOH |
| Fe25 s25/2 | slab, OOH (production) | OH converged; O stopped | O |

**Consequence.**
- Every support site of Cu8 and Fe25 still lacks at least one state, so both alloys stay `NO_VALUE`.
- K1, K2 and the Ni34 nomination stay `NOT_EVALUABLE_UNDER_ARM_C`, and arm C's registered readings are unchanged.
- The three converged states stay in the record. They count only if the last state at their site converges.

**Trajectories.** `trajectories.py` reads the committed mirrors and writes `trajectories.json`. Accuracy is QE's "estimated scf accuracy" in Ry; conv_thr is 10⁻⁶. Production and the ndim16 re-run each ran 126 iterations.

| Converged state | Iterations | Production / re-run, best in 126 | Total magnetization, μB (seed) |
|---|---|---|---|
| Cu8 s16/2 OH | 33 | 6.3×10⁻⁴ / 1.1×10⁻³ | 50.13 (O, 49.63) |
| Cu8 s16/2 OOH | 31 | 1.0×10⁻⁵ / 9.3×10⁻⁶ | 50.00 (O, 49.63) |
| Fe25 s25/2 OH | 61 | 2.4×10⁻⁶ / 3.9×10⁻⁶ | 44.44 (OOH, 43.40) |

| Stopped state | Moved: best in 126 | Production / re-run: best in 126 | Moved: best in 200 (iteration) | Moved: median, iterations 151–200 |
|---|---|---|---|---|
| Cu8 s16/2 slab | 1.2×10⁻⁵ | 1.8×10⁻³ / 2.9×10⁻⁴ | 1.2×10⁻⁵ (56) | 2.5×10⁻⁴ |
| Cu8 s26/1 slab | 4.9×10⁻⁶ | 1.7×10⁻⁴ / 1.5×10⁻⁴ | 1.3×10⁻⁶ (200) | 2.8×10⁻⁶ |
| Cu8 s26/1 O | 2.0×10⁻⁴ | 1.8×10⁻⁴ / 1.3×10⁻⁴ | 2.0×10⁻⁴ (28) | 6.8×10⁻³ |
| Cu8 s26/1 OOH | 8.1×10⁻⁵ | 1.6×10⁻⁴ / 4.5×10⁻⁴ | 8.1×10⁻⁵ (65) | 5.8×10⁻⁴ |
| Fe25 s13/0 OH | 4.7×10⁻⁶ | 2.4×10⁻⁵ / 3.5×10⁻⁵ | 4.0×10⁻⁶ (200) | 4.2×10⁻⁶ |
| Fe25 s13/0 O | 2.6×10⁻⁴ | 1.2×10⁻⁶ / 9.1×10⁻⁴ | 2.6×10⁻⁴ (77) | 4.8×10⁻³ |
| Fe25 s13/0 OOH | 4.7×10⁻⁵ | 4.1×10⁻⁴ / 1.2×10⁻⁴ | 4.7×10⁻⁵ (85) | 3.5×10⁻⁴ |
| Fe25 s25/2 O | 1.2×10⁻⁵ | 1.3×10⁻⁵ / 1.3×10⁻⁵ | 4.7×10⁻⁶ (195) | 6.5×10⁻⁶ |

**What this shows.**
- The moved start converged three states that no earlier start had converged in 126 iterations. Each ended within about 1 μB of its seed's total magnetization (0.4–1.0).
- Within 126 iterations, the moved start beat production and the re-run by 2–31× on five of the eight others. It matched them on two (Cu8 s26/1 O, Fe25 s25/2 O).
- On one it fell far short: production's Fe25 s13/0 O reached 1.2×10⁻⁶ at its 126-iteration cap, just above conv_thr, while the moved start stalled near 10⁻³.
- Over 200 iterations the eight split three ways:
  - still improving at the ceiling: Cu8 s26/1 slab (1.3×10⁻⁶ at iteration 200) and Fe25 s25/2 O (4.7×10⁻⁶ at 195);
  - flat: Fe25 s13/0 OH, at 4–5×10⁻⁶ from about iteration 50;
  - stalled or drifting back up to 10⁻⁴–10⁻²: the Cu8 s16/2 slab (after 1.2×10⁻⁵ at iteration 56), Cu8 s26/1 O and OOH, and Fe25 s13/0 O and OOH.
- The start sets how fast a run reaches 10⁻⁴–10⁻⁵ Ry. For five of these eight states, something else stops it there.

**Competing explanations for the late stalls.**
- *The SCF hops between nearby magnetic configurations.* In iterations 101–200, the cell's total moment wandered by 0.6–0.8 μB in three of the runs that drifted back up: Cu8 s26/1 O and OOH, and Fe25 s13/0 O. In the three that crept down or held flat (Cu8 s26/1 slab, Fe25 s25/2 O, Fe25 s13/0 OH), it held within 0.1 μB.
- *Charge sloshing or an orbital-occupation change that the total moment does not show.* The Cu8 s16/2 slab drifted back up while its total moment stayed within 0.2 μB, so the total alone cannot separate the two explanations for it. Per-atom moments would, but these runs print none at this verbosity.

**What a value still needs.**
- One state per alloy would complete a support site and give that alloy a single-site value (`SINGLE_SITE`): the Cu8 s16/2 slab and Fe25 s25/2 O. K1 needs both.
- Each of the two has now stopped short from three starts: production's atomic start, the ndim16 re-run and the moved seed.
- A further round would have to change the SCF path, not only the start; for example, a smaller mixing_beta with a higher iteration cap. Mixing changes the path, not the equations solved, though it can change which magnetic state a run lands in.
- At 57–63 s per iteration on 128 cores, 400 iterations cost about 850 SU per state, about 1,700 SU for the two. That fits inside the 2,791.5 SU left under the approved 23,680.
- No such round is planned.

**Open for Frank.** Stop here and deposit the freeze, arm C and the extension readouts as planned (before any OER measurement; Oct 21 fallback), or approve a narrow third round on those two states. Frank chose the third round on 2026-10-09 ([Round 3](#round-3-2026-10-09)).

| Part | Location |
|---|---|
| Readout | `results/arm_c_ext_r2_2026-10-08/readout.json` (`readout.job.json`); `terminal_collection.json`; `status_snapshot_20261009T043156Z.json` |
| Mirror | `results/arm_c_ext_r2_2026-10-08/raw_mirror/`: outputs, inputs, receipts and Slurm logs, sha256-matched to Anvil; projection outputs kept local |
| Trajectories | `results/arm_c_ext_r2_2026-10-08/trajectories.py` and `trajectories.json` |
| Tests | `tests/test_arm_c_ext_r2.py`, 23 tests (the readout reproduction skips without the local projection outputs); 191 pass with the arm C and HEA QC suites |

## Round 3, 2026-10-09

Decisions of record: Frank, 2026-10-09: "Lets do a round 3" (the alternative was to stop and deposit), then "0.3 + longer memory" after the pre-launch review below.

**Targets.** The Cu8 and Fe25 support sites still missing exactly one state after round 2: the Cu8 s16/2 slab and Fe25 s25/2 O.
- Either one converging completes its site and gives its alloy a single-site value.
- K1 needs both.

**What changes.** Each job is round 2's job with the same start, byte for byte: the moved density, the XML, occup.txt and paw.txt. Three deck lines differ from round 2's:
- its own prefix (`<state>__atomic_moved_ndim16`);
- an added `mixing_ndim = 16`, instead of QE's default 8: the mixer keeps 16 past steps (arm C's ndim16 re-run setting). `mixing_beta` stays at production's 0.3;
- `max_seconds = 18400` instead of 165000 (below).

The runner's ceiling rises from round 2's 200 iterations to 300.

**Mixing, after the pre-launch review.** As first built, round 3 lowered `mixing_beta` to 0.1. The review found that this project had already measured that setting on these two alloys (`lowtail-clean-slab-scf-stall-2026-09-19.md`, diagnostic of 2026-09-22):
- At fixed geometry, with this protocol, 0.1 was worse everywhere it was tried:
  - Cu8Cr23Mn35Co34 s20/2 slab: stalled at 2.7×10⁻⁴ Ry, where 0.3 converged in 68 iterations;
  - Fe25Co25Ni25Cr25 s2/0 slab: stalled at 1.2×10⁻⁵ Ry; 0.3 had stalled near 6×10⁻⁶.
- The stalls diagnosed there are second self-consistent states, not transients of the mixing history. On the Cu8 s20/2 slab, the stall state sits 95 meV above the converged one through an orbital reorientation on one surface Co. From their own densities, changing the mixing did not move them.

Frank then chose production mixing with the longer history.
- In the ndim16 re-run, this setting took the Cu8 s16/2 slab to 2.9×10⁻⁴ Ry at the 126-iteration cap, still falling; production reached 1.8×10⁻³.
- Round 2's Fe25 s25/2 O was still improving at its 200-iteration cutoff (4.7×10⁻⁶ Ry at iteration 195).
- If either state is stuck in a second self-consistent state, no mixing setting is expected to free it.

**Why max_seconds.** The runner stops a job at its ceiling by touching QE's EXIT file, and kills it if QE has not exited 30 s later.
- An iteration of these slabs takes about 60 s. Six of round 2's eight stopped runs exited in time and wrote their last density, but the two runs of these states were killed mid-iteration and wrote nothing to continue from.
- With `max_seconds` below the runner's 19,000 s wall, and `electron_maxstep` (300) equal to the runner's iteration ceiling, QE stops itself either way and writes its last density.
- In this repository, QE needed 3–6 s from such a stop to its final clock, well inside the runner's 30 s.
- Round 2's Fe25 O ran at about 62.4 s per iteration, so `max_seconds` will stop it near iteration 293 rather than 300.

**Limits and cost.**
- Runner: 300 iterations, a 19,000 s SCF wall (the runner's maximum for an SCF) and a 600 s projection. Slurm: 345 min.
- Ceiling: 2 × 345 min × 128 cores = 1,472 SU.
- Spent before launch: 20,888.5 SU (17,471.8 before round 2, plus round 2's 3,416.7). Campaign bound: 22,360.5 SU, inside the approved 23,680.
- When round 3 was proposed, the plan was 400 iterations for about 1,700 SU. That does not fit the runner's 19,000 s SCF maximum at about 60 s per iteration; 300 iterations do, at a lower ceiling.

**No canary; a start check instead.**
- QE already read these exact files as built in round 2: the Cu8 slab file in the canary, and both files in the main array.
- QE computes the first iteration's accuracy before any mixing. Round 2's canary and main array printed it to the same 8 digits on different nodes.
- A few minutes after release, `start_check.py` reads each job's first "negative rho (up, down)" and "estimated scf accuracy" lines on Anvil (read-only). They must equal round 2's:
  - Cu8 s16/2 slab: 7.515E-02 3.168E-01 and 3.43867242 Ry;
  - Fe25 s25/2 O: 4.686E-03 4.562E-01 and 38.00323795 Ry.
- On a mismatch, the array is cancelled and the mismatch investigated.

**Staging.** No density is uploaded. The two densities and XMLs are copied on Anvil from round 2's root, each checked against round 2's pin before and after the copy. The decks, spec, Slurm script, seed text files and runner go by sftp, as in earlier rounds.

**Checks written down before any result.**
- **Magnetic state.** A converged state counts toward a value only if it lies in the magnetic state of the site's other states. The site's converged states:
  - Cu8 s16/2: O, OH and OOH at 49.6–50.1 μB total (absolute 68.0–69.2). Round 2's slab sat at 51.25 / 69.17 μB, and production's slab trajectory near 45 μB.
  - Fe25 s25/2: slab 41.98, OH 44.44, OOH 43.40 μB. Round 2's O sat at 42.63 μB, production's near 40.5.
  - The readout sets each converged round-3 state's total magnetization against the nearest converged state at its site (`magnetization_vs_site`) and flags a difference above 1.5 μB. An alloy value resting on a flagged state lists it in `magnetization_flags`, and that value is reported as resting on a state in a different magnetic state.
- **A stalled run.** `collect_terminal.py` also mirrors each run's saved Hubbard occupations (`occup.txt`, about 35 KB), as QE wrote them when it stopped. They can be compared with the site's converged states for a single-site orbital difference like the one diagnosed on 2026-09-22, at no compute cost.

**Readout.**
- `arm_c_readout.py` now takes repeated `--ext-plan`/`--ext-mirror` pairs. It applies them in order of the plans' `round`, which must increase strictly, each to the states still failed after the rounds before it.
- An attempt from a plan row that records its round also records:
  - the round and the mixing;
  - `qe_stop` ("time" or "iterations"), when QE stopped itself;
  - `config_written`: QE wrote its last density to its own save;
  - for a converged state, `magnetization_vs_site` (above).
- Such a stop counts as CEILING. The runner itself labels it "numerical failure marker".
- With one pair, the earlier readouts reproduce byte for byte (tested).

Round 3's readout stacks rounds 2 and 3:

```
python src/dft/arm_c_readout.py --plan results/arm_c_2026-10-07/site_plan.json \
  --mirror results/arm_c_2026-10-07/raw_mirror \
  --rerun-plan results/arm_c_2026-10-07_rerun/rerun_plan.json \
  --rerun-mirror results/arm_c_2026-10-07_rerun/raw_mirror \
  --ext-plan results/arm_c_ext_r2_2026-10-08/ext_plan.json --ext-mirror results/arm_c_ext_r2_2026-10-08/raw_mirror \
  --ext-plan results/arm_c_ext_r3_2026-10-09/ext_plan.json --ext-mirror results/arm_c_ext_r3_2026-10-09/raw_mirror \
  --out results/arm_c_ext_r3_2026-10-09/readout.json
```

| Part | Location |
|---|---|
| Builder | `src/dft/arm_c_ext_r3_build.py`, with `--check` (9 files) |
| Decks, manifest | `runs/hea/arm_c_ext_r3_2026-10-09/` (2) and `runs/m_arm_c_ext_r3_2026-10-09_main.txt` |
| Spec, plan, seed text files | `results/arm_c_ext_r3_2026-10-09/` (`launch_spec.json`, `ext_plan.json`, `seeds/`) |
| Slurm | `anvil/98_arm_c_ext_r3.slurm`, with round 2's resources |
| Operations | `results/arm_c_ext_r3_2026-10-09/launch_ops.py` (stage with copies on Anvil, preflight, held submit, validate, release), `start_check.py`, `status_once.py`, `collect_terminal.py` |
| Tests | `tests/test_arm_c_ext_r3.py`, 15 tests; 206 pass with the arm C and HEA QC suites |

## Round 3 readout, 2026-10-10: neither state converged; no value

**Runs.** Array 21199937 waited 19.6 h after its release: priority on the busy `wholenode` partition comes mostly from age, and round 2 had started within minutes. Its two tasks then ran on a477 and a268 from 01:44Z and 01:48Z on 2026-10-10.
- The start check passed at 03:07Z: both jobs printed round 2's first "negative rho" and accuracy lines exactly (`start_check_20261010T030728Z.json`).
- Neither state reached conv_thr 10⁻⁶ Ry. Each ran all 300 iterations, and QE then stopped itself ("convergence NOT achieved after 300 iterations: stopping").
  - Each wrote its last density and occupations ("Writing config") and ended normally: the Cu8 slab after 4 h 37 min, the Fe25 O after 5 h 4 min.
  - The Fe25 O ran at about 61 s per iteration, so it reached the iteration cap before `max_seconds`. The design had expected a time stop near iteration 293.
- The runner labels QE's own stop "numerical failure marker", and Slurm lists the rejections as `FAILED` (exit 10). There were no QE errors; the only IEEE notes are underflow and denormal.

**Cost.**
- Round 3 used 1,241.2 SU (sacct CPU time: 591.6 and 649.7), inside its 1,472 SU ceiling.
- The campaign has used 22,129.7 SU of the approved 23,680, leaving 1,550.3.
- Balance: 15,535.2 SU (`mybalance`, 2026-10-10 13:42Z). Its drop since round 2's readout, 1,241.3 SU, matches round 3's use.

**Readout.** `readout.json` comes from the stacked command under Round 3.
- It is round 2's readout plus the two new attempts. Only the extension counts change: 13 attempted, 3 accepted. A test checks this.
- 43 of 64 SCFs are accepted and 6 of 16 sites are complete, unchanged.
- Each new attempt records round 3, beta 0.3 with ndim 16, `qe_stop` "iterations", `config_written`, and failure CEILING.

**Consequence.**
- The Cu8 s16/2 slab and Fe25 s25/2 O are still missing, so Cu8 and Fe25 stay `NO_VALUE`.
- K1, K2 and the Ni34 nomination stay `NOT_EVALUABLE_UNDER_ARM_C`, and arm C's registered readings are unchanged.
- The magnetic-state check covers converged states only, so it did not apply. Both runs stopped in round 2's magnetic state: 51.18 μB total (round 2: 51.25) and 42.63 μB (42.63).

**Trajectories.** `trajectories.py` reads the committed mirrors and seed files and writes `trajectories.json`. Accuracy is QE's "estimated scf accuracy" in Ry.

| Stopped state | Round 2 (ndim 8): best in 200 (iteration) | Round 3 (ndim 16): best in 300 (iteration) | Round 3: iterations below 10⁻⁵ | Round 3 median, iterations 51–100 / 151–200 / 251–300 | Total magnetization from iteration 101, μB: round 3 (round 2) |
|---|---|---|---|---|---|
| Cu8 s16/2 slab | 1.2×10⁻⁵ (56) | 5.3×10⁻⁶ (68) | 32, iterations 48–79 | 8.5×10⁻⁶ / 8.8×10⁻⁵ / 1.2×10⁻⁴ | 51.08–51.25 (51.06–51.25) |
| Fe25 s25/2 O | 4.7×10⁻⁶ (195) | 7.6×10⁻⁶ (293) | 11, iterations 172–293 | 2.1×10⁻⁵ / 2.8×10⁻⁵ / 1.9×10⁻⁵ | 42.52–42.66 (42.55–42.65) |

Round 2's medians for iterations 151–200 were 2.5×10⁻⁴ and 6.5×10⁻⁶ (Round 2 main readout). Its Fe25 O spent 48 iterations below 10⁻⁵, from iteration 129 to its cutoff.

**What this shows.**
- The Cu8 slab followed round 2's path at two to three times lower accuracy values. Between iterations 48 and 79 it was below 10⁻⁵ Ry, closer to conv_thr than any earlier run of this state. It then drifted back up and held near 10⁻⁴ Ry for its last 200 iterations.
- The Fe25 O did worse than round 2. It dipped below 10⁻⁵ in only 11 of 300 iterations and held at 2–3×10⁻⁵ to the end. Round 2 had been creeping down through 10⁻⁵ at its 200-iteration cutoff.
- Neither run hopped between magnetic states: from iteration 101, each cell's total moment held within 0.17 μB.
- The two mixing histories cannot be ranked from these runs.
  - Through iteration 9 the mixer holds at most 8 past steps, so ndim 8 and ndim 16 do the same arithmetic.
  - Even so, round 3's accuracies differ from round 2's by 1–5×10⁻⁸ (relative) at iteration 2 and by 0.1–6% at iterations 3–8.
  - Round 2's canary and main array, run from identical inputs, differ the same way: 2×10⁻⁸ at iteration 2 and up to 4% at iterations 4–8.
  - Runs of these states amplify rounding differences within a few iterations, so one run per setting cannot attribute a difference to the mixing.

**Occupations at the stop.** This is the stalled-run check written down before launch: each run's last Hubbard occupations, against the site's converged states, for a single-site orbital difference like the one diagnosed on 2026-09-22. There, a minority-spin reorientation on one surface Co held the Cu8 s20/2 slab in a second self-consistent state.
- `site_occupations.py` mirrors the occupations of every converged state at the two sites: six files, sha256-matched to Anvil. `trajectories.json` sets each run's `occup.txt` (from its own save) against them.
- The distance between two occupation sets at one atom is the Frobenius norm of their difference over both spins. Each run's start is one of these converged states: the O state's occupations for the Cu8 slab, the slab's for the Fe25 O.

| Run | Atom | Stalled run to each converged state | Converged states to each other |
|---|---|---|---|
| Cu8 slab | Co 13, 15, 21, 23 | O: 0.28–0.48; OH and OOH: 0.03–0.14 | O to OH and OOH: 0.27–0.49; OH to OOH: 0.03–0.10 |
| Fe25 O | Fe 22 | slab: 0.77; OH and OOH: 0.90 | slab to OH and OOH: 0.94; OH to OOH: 0.02 |
| Fe25 O | Co 20; Ni 18 | 0.15–0.17; 0.10–0.11 | at most 0.03; at most 0.02 |

- **Cu8 slab: no single-site difference.**
  - Starting from the O state's occupations, the slab turned the minority-spin orbitals of Co 13, 15, 21 and 23 into the configuration that the converged OH and OOH states share. The O state differs from both of them at those atoms.
  - At every atom, the stalled slab lies within the spread of the site's converged states. Its median distance to the nearest is 0.025, against a median spread of 0.097.
- **Fe25 O: a difference at Fe 22, of uncertain origin.**
  - At Fe 22 (top layer, 4.2 Å from the O), the stalled run is in a third configuration: 0.77 from the slab's and 0.90 from the one OH and OOH share. Halfway between those two would be about 0.47 from each.
  - It also lies outside the converged states' spread at Co 20 and Ni 18.
  - No O state at this site has converged, and the Cu8 site shows a bound O turning neighbouring orbitals away from the OH and OOH configuration. So this cannot separate a stalled configuration from the O's own effect.

**Competing explanations for the stalls.**
- *A second self-consistent state, held by an orbital configuration.*
  - For the Cu8 slab, the occupations show none. The run reached the configuration the site's converged states share and still held near 10⁻⁴ Ry.
  - For the Fe25 O, Fe 22 is a candidate. The steady moments while the accuracy plateaus also fit, and no mixing setting is expected to free such a state.
- *Slow charge sloshing, or a near-degeneracy the occupations do not show.* For the Cu8 slab this now fits better. But beta 0.1 measured worse on these alloys (2026-09-22), and the longer history did not help here.

**What a value still needs.**
- Each of the two states has now stopped short in four attempts: production's atomic start, the ndim16 re-run, round 2's moved seed, and round 3's moved seed with ndim 16 (126, 126, 200 and 300 iterations).
- For the Fe25 O, the occupations suggest a targeted test.
  - Start Fe 22 in the configuration that OH and OOH share, for example from the OH state's occupations, and hold the occupations for the first iterations (`mixing_fixed_ns`, protocol P-B of `lowtail-stall-robust-protocol-plan-2026-09-22.md`).
  - The deck template would have to admit that setting. If the run converges, Fe 22's configuration was the obstacle.
- For the Cu8 slab, the occupations point at nothing to change.
- 1,550.3 SU is left under the approved 23,680. One state at this length costs about 650 SU.
- No such round is planned.

**Open for Frank.** Stop here and deposit the freeze, arm C and the extension readouts as planned (before any OER measurement; Oct 21 fallback), or approve a further round on these two states.

| Part | Location |
|---|---|
| Readout | `results/arm_c_ext_r3_2026-10-09/readout.json` (`readout.job.json`); `terminal_collection.json`; `status_snapshot_20261010T134221Z.json` |
| Mirror | `results/arm_c_ext_r3_2026-10-09/raw_mirror/`: outputs, inputs, receipts, stop markers, Slurm logs and each run's `occup.txt`, sha256-matched to Anvil |
| Site occupations | `results/arm_c_ext_r3_2026-10-09/site_occupations.py` (`site_occupations.job.json`), `site_occupations.json` and `site_occupations/` |
| Trajectories and occupations | `results/arm_c_ext_r3_2026-10-09/trajectories.py` and `trajectories.json` |
| Tests | `tests/test_arm_c_ext_r3.py`, 19 tests (the readout reproduction skips without the local projection outputs); 210 pass with the arm C and HEA QC suites |

## Round 4, 2026-10-10

Decision of record: Frank, 2026-10-10: "Do the Fe25 O run", after the Round 3 readout. The alternative was to stop and deposit.

**Target.** The Fe25 s25/2 O, its site's last missing state.
- If it converges, the site is complete and Fe25 gets a single-site value (`SINGLE_SITE`).
- K1 still needs the Cu8 s16/2 slab.

**The test.** At its stop, round 3's Fe25 O had Fe 22 in an occupation configuration that none of the site's converged states has (Round 3 readout). Round 4 starts Fe 22's Hubbard occupations, and so its +U potential, in the configuration the converged OH and OOH share. It holds the occupations while the density settles around them.

**What changes.**
- *Start.* Round 3's save, as QE wrote it when it stopped at iteration 300. Its density and XML are copied on Anvil; `start_sources.json` pins them and mirrors round 3's and the OH state's `paw.txt`.
- *Fe 22.* Its blocks in `occup.txt` (the Hubbard occupations) and in `paw.txt` (the PAW on-site block; Fe uses a PAW potential) are both taken from the converged OH state, for both spins. Round 1 rebuilt these two files together for every seeded state in the same way.
  - Fe 22 then starts at Tr[ns] 4.908 (up) and 1.292 (down); round 3 stopped at 4.800 and 1.624.
  - So OH's block has 0.22 fewer d electrons and a 0.44 μB larger d moment: it differs in more than orientation. With these non-orthogonalized atomic projectors, the d count alone does not establish a change of oxidation state.
  - OH's Fe 22 sits 0.14 Å from its place in the O structure, so the transferred blocks belong to a slightly different geometry. Round 1's seeding made the same approximation.
- *Everything else.* Every other atom keeps round 3's last occupations and PAW blocks. That includes Co 20 and Ni 18, which also lay outside the converged states' spread, so they are held at their stalled values. The plane-wave density everywhere, Fe 22's surroundings included, starts as the stalled run left it and relaxes from iteration 1.
- *Deck.* Round 3's, with its own prefix and one added line, `mixing_fixed_ns = 5`. QE keeps the occupations at their starting values for the first 5 iterations, so the density settles around them before they may move.
  - mixing_beta 0.3, mixing_ndim 16, electron_maxstep 300 and max_seconds 18,400 stay as in round 3.
  - The Round 3 readout said the deck template would have to admit this setting. It does not: the extension builders patch each round's deck, and the production template is not involved.
- *After the hold.* At iteration 6 the mixer's history holds no occupation steps, so the occupations first move by plain mixing at beta 0.3. The held steps leave the 16-step history by about iteration 21, so a transient after the release is expected.

**Held occupations: a rule set before launch.**
- While QE holds the occupations, it resets them to their input values before mixing (QE 7.5, `electrons_scf`). Its convergence test then ignores them, so a run could stop as converged inside those iterations with occupations that are not self-consistent.
- `arm_c_readout.py` therefore does not accept a convergence within the held iterations: the attempt records `held_occupations` and fails as HELD. Earlier readouts reproduce byte for byte (tested).
- With the occupations held, what remains is a density-only problem that starts near convergence and is disturbed at one atom, so it may converge fast.
  - The hold is 5 iterations rather than the 10 first built, to make such a stop less likely. From an error of 10⁻² Ry at the first iteration, converging within 5 would need the error to fall about 10× per iteration.
  - A shorter hold leaves the density less settled when the occupations are released. That is the price of the change.
- *If it stops as HELD anyway,* the run ends within about 20 minutes, projection included (under 50 SU). Its save, a density converged around the held occupations, is then the start of a continuation without the hold, under the same limits. That needs a separate approval; about 1,500 SU would remain under the approved 23,680.

**Limits and cost.**
- Runner: 300 iterations, a 19,000 s SCF wall and a 600 s projection. Slurm: 345 min, one task.
- Ceiling: 345 min × 128 cores = 736 SU.
- Spent before launch: 22,129.7 SU (20,888.5 before round 3, plus round 3's 1,241.2). Campaign bound: 22,865.7 SU, inside the approved 23,680.

**Start check.** A few minutes after the job starts, `start_check.py` reads the head of its output on Anvil (read-only).
- QE's "STARTING HUBBARD OCCUPATIONS" must equal the built `occup.txt`:
  - every Hubbard atom's Tr[ns] (up, down and total) within 10⁻⁵;
  - Fe 22's two 5×5 matrices within 1.5×10⁻³.
  - Round 3 printed its own start to within 5×10⁻⁶ and 5×10⁻⁴ (tested).
- Once the first iteration has finished, "The initial density is read from file" and "RESET ns to initial values (iter <= mixing_fixed_ns)" must both appear. Until then the check reports no verdict, unless the starting block already disagrees.
- It also records Fe 22's occupations as QE printed them after the first iteration.
- On a mismatch, the job is cancelled and the mismatch investigated.

**What a result means.**
- *Converged after the hold:* a self-consistent O state, with Fe 22 started in OH's configuration. The readout gives Fe25 a single-site value, exploratory like the rest of the extension.
  - If the cell's total moment lies more than 1.5 μB from the nearest converged state at the site, the value is flagged as resting on a state in a different magnetic state. The flag reports; it does not withhold the value.
- *That value would rest on a state chosen by its start.* Nothing shows that it is the O state's lowest-energy solution. Round 3 started Fe 22 in the slab's configuration, 0.94 from OH's, and stopped 0.90 from OH's in a configuration of its own, while its energy fell by about 0.8 mRy between iterations 109 and 300. Three checks are therefore reported with any value, set before the run:
  - *Energy against round 3.* The reference is the median of round 3's last 50 total energies, −8913.94359 Ry. A converged energy more than 1 mRy (13.6 meV) above it marks the state as metastable relative to round 3's trajectory. An error in E(O) shifts ΔG2 and ΔG3 one for one.
  - *Occupations at the stop.* Fe 22, Co 20 and Ni 18 are set against the site's converged states, as in the Round 3 readout: does Fe 22 stay in OH's configuration, and do Co 20 and Ni 18 return within the converged states' spread?
  - *A spectator term.* The site's slab has Fe 22 0.94 from the configuration its OH and OOH share. So ΔG1 and ΔG4 already include a change at Fe 22, 4.2 Å from the adsorbate, in any value at this site.
- *What a convergence would not show:* that Fe 22 was the obstacle. The run also restarts the mixing from a nearly converged density and holds every atom's occupations, not only Fe 22's. A control from the same start with Fe 22 unchanged (about 650 SU) would separate these; it is not planned.
- *Stopped again:* holding Fe 22 in the OH and OOH configuration for 5 iterations did not free the state. The occupations at the stop show whether Fe 22 stayed there or went back.

**Readout.** The command stacks rounds 2, 3 and 4:

```
python src/dft/arm_c_readout.py --plan results/arm_c_2026-10-07/site_plan.json \
  --mirror results/arm_c_2026-10-07/raw_mirror \
  --rerun-plan results/arm_c_2026-10-07_rerun/rerun_plan.json \
  --rerun-mirror results/arm_c_2026-10-07_rerun/raw_mirror \
  --ext-plan results/arm_c_ext_r2_2026-10-08/ext_plan.json --ext-mirror results/arm_c_ext_r2_2026-10-08/raw_mirror \
  --ext-plan results/arm_c_ext_r3_2026-10-09/ext_plan.json --ext-mirror results/arm_c_ext_r3_2026-10-09/raw_mirror \
  --ext-plan results/arm_c_ext_r4_2026-10-10/ext_plan.json --ext-mirror results/arm_c_ext_r4_2026-10-10/raw_mirror \
  --out results/arm_c_ext_r4_2026-10-10/readout.json
```

**Pre-launch review.** An independent review found no blocker. It confirmed from the QE 7.5 source that `read_scf` loads `occup.txt` into the occupations QE starts from and holds, that iteration 5 itself is held, and that the start check's text and tolerances fit. Its three record changes are folded in above:
- what a convergence would and would not show, with the three checks;
- the case of a stop within the hold;
- the wording on Fe 22.

It also led to the shorter hold and to the start check's matrix comparison and pending state. Its note that Fe 22's PAW block would start in the stalled configuration led to taking that block from OH as well.

| Part | Location |
|---|---|
| Builder | `src/dft/arm_c_ext_r4_build.py`, with `--check` (6 files) |
| Start sources | `results/arm_c_ext_r4_2026-10-10/start_sources.py`, `start_sources.json` and `sources/` |
| Deck, manifest | `runs/hea/arm_c_ext_r4_2026-10-10/` and `runs/m_arm_c_ext_r4_2026-10-10_main.txt` |
| Spec, plan, rebuilt files | `results/arm_c_ext_r4_2026-10-10/` (`launch_spec.json`, `ext_plan.json`, `seeds/`: `occup.txt` and `paw.txt`) |
| Slurm | `anvil/99_arm_c_ext_r4.slurm`, with round 3's resources |
| Operations | `results/arm_c_ext_r4_2026-10-10/launch_ops.py` (stage with copies on Anvil, preflight, held submit, validate, release), `start_check.py`, `status_once.py`, `collect_terminal.py` |
| Tests | `tests/test_arm_c_ext_r4.py`, 13 tests; 223 pass with the arm C and HEA QC suites |

## Round 4 readout, 2026-10-10: the Fe25 O converged; Fe25 has a single-site value

**Run.** Job 21224301 waited 3 h 43 min after its release, then ran on a317 from 18:47Z to 19:10Z.
- It converged in 20 iterations, after the 5 held ones, so the HELD rule did not apply. The runner's receipt is COMPLETE, and the projection ran.
- There were no QE errors; the only IEEE notes are underflow and denormal.
- The job started and ended between two status checks, so the start check ran after it had ended (`start_check_20261010T211017Z.json`). It passed:
  - QE printed the built occupations: traces within 4.9×10⁻⁶, Fe 22's matrices within 5.0×10⁻⁴.
  - It read the density from file and printed the RESET line in each of iterations 1–5 (counted in `checks.json`).

**Cost.**
- Round 4 used 49.96 SU (sacct CPU time: 179,840 core-seconds), inside its 736 SU ceiling.
- The campaign has used 22,179.7 SU of the approved 23,680, leaving 1,500.3.
- Balance: 15,485.2 SU (`mybalance`, 2026-10-10 21:10Z). Its drop since the Round 3 readout, 50.0 SU, matches round 4's use.

**Readout.** `readout.json` comes from the stacked command under Round 4.
- It is round 3's readout with the new attempt accepted, which completes the Fe25 s25/2 site. A test checks that nothing else changed.
- 44 of 64 SCFs are accepted and 7 of 16 sites complete. Extension: 14 attempted, 4 accepted.
- Fe25 s25/2: ΔG1–ΔG4 = 2.123, 1.027, 1.773 and −0.003 eV. Step 1 (OH formation) limits, so η = 0.893 V.
- The O state's total moment, 44.60 μB, lies 0.16 μB from the OH state's 44.44: no magnetic-state flag.
- The site mixes recipes: the slab and OOH come from production, the OH (round 2) and O (round 4) from seeded starts.
  - The ndim16 control of this production slab reproduced it within 0.10 meV (design doc §7).
  - With the control slab, η is 0.8933 V.

| Alloy | Value (V) | Basis |
|---|---|---|
| Cu26Ni9Cr31Co33 | 0.613 | one site (s1/0) |
| **Fe25Co25Ni25Cr25** | **0.893** | **one site: s25/2, weight 0.8 (s13/0 incomplete); new** |
| Ni31Cr29Cu5Mn35 | 0.934 | two sites |
| Cu22Fe30Co32Mn15 | 0.942 | one site (s24/3) |
| Ni34Fe6Cu29Co31 | 1.281 | one site (s29/1) |
| Cu8Cr23Mn35Co34 | — | no value: s16/2 and s26/1 both incomplete |

**Consequence.**
- Fe25 has an exploratory single-site value, 0.893 V. Arm C's registered readings are unchanged.
- K1, K2 and the Ni34 nomination stay `NOT_EVALUABLE_UNDER_ARM_C`. Each needs Cu8:
  - K1 compares Cu8 with Ni31 and Fe25;
  - K2 orders the five batch-1 alloys;
  - the nomination needs all six alloys.
- Fe25 and Ni31 now bracket K1. It would read Cu8 more active below 0.893 V, less active above 0.934 V, and mixed between. The 41 mV between them is inside DFT+U error.
- The order of the five values is descriptive only, as in §7.
- DFT − MLIP at this site is +0.34 V (MLIP 0.557 V), inside the +0.10 to +0.52 V of the six complete sites in §7 (informative).

**The checks set before launch.** `checks.py` reads the committed mirrors, round 3's site occupations and the readout, and writes `checks.json`.

| Check | Result |
|---|---|
| Energy against round 3 | −8913.96642 Ry. That is 22.8 mRy (0.31 eV) below the reference, −8913.94359 Ry, and at least 22.5 mRy below each of round 3's last 50 energies. Not flagged. |
| Fe 22 | 0.11 from OH, 0.13 from OOH and 0.92 from the slab; 0.89 from round 3's stop |
| Co 20 and Ni 18 | still outside the converged states' spread: 0.14 and 0.09 from the nearest (OH), against spreads of 0.03 and 0.02; within 0.03 of round 3's stop |
| Spectator term | OH, OOH and now O share Fe 22's configuration, and the slab does not. The change enters ΔG1 and ΔG4, and ΔG1 limits. |

- *Energy.*
  - Round 3 was not converging slowly toward this state. Its last 50 accuracies had a median of 1.9×10⁻⁵ Ry, about a thousandth of the gap.
  - It sat in a different state, 0.31 eV higher, with a total moment 2.0 μB lower (42.63 against 44.60 μB).
  - Round 4's energy fell below the reference at iteration 2, during the hold.
- *SCF path.*
  - The first accuracy was 0.53 Ry, not the 10⁻² Ry the design assumed: OH's occupations on Fe 22 disturbed the potential more than expected.
  - At iteration 5, the last held one, the accuracy was 8.7×10⁻³ Ry, so the hold could not end the run.
  - After the release it fell at every iteration, from 3.1×10⁻³ Ry at iteration 6 to 8.3×10⁻⁷ at iteration 20. The expected transient did not appear.
  - The total moment stayed between 44.27 and 44.60 μB throughout.
- *Occupations.*
  - Away from Fe 22, the converged O is round 3's stop. No other atom moved by more than 0.09: Co 12 by 0.09, Cr 24 by 0.05, the rest by at most 0.02.
  - Co 15 and 20, and Ni 10, 14, 16 and 18, lie outside the converged states' spread. So did they at round 3's stop, with Co 4 just outside as well (0.008 against 0.007).
  - Fe 22 stayed near the configuration OH and OOH share: 0.11 from OH's, where OH and OOH lie 0.02 apart.
  - Fe 22's d moment (Tr up − Tr down) is 3.79, against 3.62 in OH, 3.58 in OOH, 2.88 in the slab and 3.18 at round 3's stop.
  - Co 20 and Ni 18 never left round 3's values. Now that an O state has converged with them there, their offset may be the O's own effect.
- *Spectator term.*
  - Fe 22's change between the slab and the adsorbed states cancels in ΔG2 and ΔG3 and enters ΔG1 and ΔG4. ΔG1 limits, so the 0.893 V includes its energy directly.
  - Part of that energy may come from which self-consistent state each run reached, rather than from the OH. That would be a lower slab state with Fe 22 in the adsorbed configuration, or lower adsorbed states with Fe 22 in the slab's. η would then move one for one with it:
    - up, without a bound from these data;
    - or down, to 0.543 V, where ΔG3 takes over after 0.35 eV.
  - Differences in orbital configuration measured in this project have cost:
    - 95 meV for one reoriented surface Co on the Cu8 s20/2 slab (2026-09-22);
    - 0.31 eV between round 3's stop and this state, whose occupations differ mainly at Fe 22.
  - A term of that size could reorder Fe25 and Ni31.
- *E(O).*
  - Step 1 stays limiting for any error in E(O) from −0.35 to +1.10 eV, because ΔG2 and ΔG3 shift by it in opposite directions.
  - Round 3's energy, 0.31 eV higher, lies inside that range: it would give the same η.
  - So the value rests on the slab and OH energies and on Fe 22's change between them, not on which O state was found.

**What this does not show.** It does not show that Fe 22 was what held round 3. Round 4 also restarted the mixing from a nearly converged density and held every atom's occupations. A control from round 3's save with Fe 22 unchanged would separate these, at about 650 SU if it stalls as round 3 did. It is not planned.

**What a firmer value would need.** A test of the spectator term at this site:
- Rerun the slab from its own converged density, with Fe 22's occupations and PAW block from OH and the occupations held for 5 iterations, as in round 4.
  - If it converges below the current slab, ΔG1 and η rise by the difference.
  - If it converges above it, or returns Fe 22 to the slab's configuration, the slab stands.
- A run of OH with Fe 22 from the slab would test the other direction.
- Each would cost about 50 SU if it converges as round 4 did, with a 736 SU ceiling. 1,500.3 SU is left under the approved 23,680.
- For Cu8, round 3's occupations point at nothing to change.
- No such run is planned.

**Open for Frank.** Deposit the freeze, arm C and the extension readouts as planned (before any OER measurement; Oct 21 fallback), or approve the spectator test at Fe25 s25/2 first.

| Part | Location |
|---|---|
| Readout | `results/arm_c_ext_r4_2026-10-10/readout.json` (`readout.job.json`); `terminal_collection.json`; `status_snapshot_20261010T164754Z.json` and `status_snapshot_20261010T210932Z.json` |
| Mirror | `results/arm_c_ext_r4_2026-10-10/raw_mirror/`: output, inputs, receipt, Slurm log and the run's `occup.txt`, sha256-matched to Anvil; the projection output kept local |
| Start check | `results/arm_c_ext_r4_2026-10-10/start_check_20261010T211017Z.json`, run after the job had ended |
| Checks | `results/arm_c_ext_r4_2026-10-10/checks.py` (`checks.job.json`) and `checks.json` |
| Tests | `tests/test_arm_c_ext_r4.py`, 17 tests (the readout reproduction skips without the local projection outputs); 227 pass with the arm C and HEA QC suites |
