# Corpus escape: does breaking a kept mirror lower a locked Xu adsorbate? (2026-11-01)

Status: **not staged, not submitted.** Exploratory and post-census: the cases below were chosen on
2026-11-01, after the Xu census (results/s2_2026-09-18/xu_census.json) had been read and reported.
Nothing here was registered before the census. Whatever the runs show is reported, including
null, unresolved and failed cases.

## Purpose

The report's auditor labels 50 Xu four-layer adsorbate outputs locked: a kept mirror held one
lateral force component of every adsorbate atom at exactly zero through the relaxation. The blind
panel's first criticism (10 of 10 readers) is that the label is not shown to cost anything, because no
corpus lock was ever relaxed without symmetry. The only measured costs are on my own cells: CrO2 *OOH
in the 2 x 1 cell (symmetry-held geometry 150.8 meV above the symmetry-free one) and the IrO2 *OOH of the
U ladder (0.291 eV). This batch measures, for a fixed set of corpus locks, whether the held adsorbate
falls to a lower energy once the symmetry is broken.

## Selection rule (fixed before any run)

Population: census rows with `layers == 4` and `force.silentgate_verdict == "LOCKED"` (50 rows; all
U = 0). Locked axis of a row = `force.every_step_all_atom_zero_lateral_axes` (it equals the final-step
axis on every selected row; the builder asserts this).

- **Tier 1:** the 10 locked *OOH outputs, one per metal. They are the 10 `OOH-relax` jobs, locked
  axis x. Four of them (CrO2, MnO2, PtO2, RhO2) ended before converging in the deposit; they stay in,
  started from their last printed geometry.
- **Tier 2:** the 20 locked *OH outputs, two per metal (`OH` and `OH-relax`), locked axis y.
- Not selected: the 20 locked *O outputs (both lateral axes locked; a single-axis escape is not
  defined for them).

Order of launch, fixed now: **tier 1a** (the six *OOH whose deposited relaxation converged: IrO2, MoO2,
NbO2, ReO2, RuO2, TiO2), then **tier 1b** (the four that stopped unconverged: CrO2, MnO2, PtO2, RhO2;
their held arm has to finish the deposited relaxation and costs about 2.5 times more), then **tier 2**.
Each later group is submitted only if the allocation still covers its reservation after the earlier
groups have finished (see Cost). The split is a launch order inside the selection, not a new
selection: whatever runs is reported against the full rule (k of 10, k of 20).

## Two runs per case, same code and settings

Both arms of a case use the same pw.x binary (QE 7.5 on Anvil), the same pseudopotential bytes, and
the same deck except for the lines named here.

- **held (control):** relaxation from the deposited final geometry (last printed geometry where the
  deposited run did not converge) with symmetry on, as deposited. It gives E_held in this
  environment and must reproduce the lock (see validity checks).
- **escape:** the same deck with every adsorbate atom displaced along the locked axis, and
  `nosym = .true.`. `noinv` is not set: dropping it from every off-plane job is the registered
  protocol change S0(b) (runs/s0/b_noinv/README.md; measured |dE| = 3.2e-7 Ry), and it was
  dropped from the CrO2 *OOH escape (src/dft/build_s3.py, build_cr_escape).

### Displacement recipe

The CrO2 *OOH escape displaced the adsorbate along the imaginary mode from a Hessian (78 % H, out
of the plane) and relaxed without symmetry. The corpus has no Hessian, so the displacement is along
the locked axis, graded so that the H moves most, as in that mode:

| state | binding O | distal O | H |
|---|---|---|---|
| *OOH | +0.050 Å | +0.075 Å | +0.100 Å |
| *OH | +0.050 Å | (none) | +0.100 Å |

All displacements are in the + direction of the locked axis (the mirror makes + and - equivalent).
Binding O = the adsorbate O nearest a metal atom; the other O of *OOH is the distal O. The amplitude
is small on purpose: it tests whether the plane is a saddle (the case where the zero hides a force
that would move the atom) and not whether a distant basin exists past a barrier. The CrO2 escape
used a larger kick (H 0.30 Å, the program's off-plane criterion, docs/43:145-147) because it
followed a measured unstable mode.

### Settings: deposited, with the deviations listed

Kept from the deposited input, byte for byte where the line exists: `calculation = 'relax'`,
`tprnfor` or `tstress` (as deposited per job), `ibrav = 0`, `nat`, `ntyp`, `nspin`, `tot_magnetization` (Cr, Mn), every
`starting_magnetization(i)`, `ecutwfc = 40`, `ecutrho = 500`, `occupations = 'smearing'`,
`smearing = 'mp'`, `degauss = 0.01`, `mixing_beta = 0.3` (plain mixing), `conv_thr` (default
1e-6 Ry; pw.x's `upscale` lowers it toward 1e-8 as the forces approach the threshold, in the deposit
and here), `K_POINTS {automatic}
4 4 1 0 0 0`, the ATOMIC_SPECIES lines (labels, masses, UPF file names), CELL_PARAMETERS, and the
if_pos flags of every atom. U = 0: the deposited four-layer inputs carry Hubbard_U(i) = 0 and never
set lda_plus_u, so they ran plain PBE.

Deviations, each the same in both arms:

| key | deposited | here | why |
|---|---|---|---|
| prefix, outdir, pseudo_dir | absent / /home/camp/zhonxu/pseudo | prefix = job name; outdir and pseudo_dir rewritten by the runner | runner contract (src/dft/research_batch_seeded.py) |
| disk_io | 'none' | default ('low') | the runner keeps the density and XML, and projwfc.x needs the wavefunctions |
| Hubbard_U(i), Hubbard_alpha(i) | all 0, lda_plus_u unset | removed | inert in the deposit; pw.x 7.5 takes DFT+U only from a HUBBARD card; the program's U = 0 decks carry no card (src/dft/build_a0cell.py) |
| &CELL | empty | removed | ignored for 'relax' (the deposited output prints "card &CELL ignored") |
| nbnd | 562-691 (about 1.5 x the occupied count) | pw.x default (1.2 x occupied) | cost: the deposited count makes even tier 1 cost more than the allocation holds (Cost); extra empty bands do not change the smeared total energy or forces |
| forc_conv_thr | default 1e-3 Ry/bohr | 1e-4 Ry/bohr | stall guard, below |
| nstep | default 50 | 100 | the tighter threshold needs more BFGS steps; the runner and Slurm walls bound the cost |

Stall guard (why forc_conv_thr is tightened). The measured CrO2 saddle has an H curvature of about
0.22 eV/Å² along the escape direction (i244.7 cm-1). At the 0.10 Å start that is a force of
8.6e-4 Ry/bohr, below the deposited 1e-3 Ry/bohr threshold, so a run at the deposited threshold could
stop next to a saddle and read as benign. At 1e-4 Ry/bohr the start force on an H saddle exceeds the
threshold for any curvature above 0.026 eV/Å² (imaginary frequency above about i84 cm-1; the
program's Hessian noise floor is i50 cm-1, docs/45 row 1).

### Pseudopotentials: the launch blocker

The decks name the deposited GBRV files, and the launch spec pins each to the MD5 that the deposited
outputs print. None of these byte streams is on Anvil ($PROJECT/pseudo, the SSSP tree under
$PROJECT/pseudo_src, a project-wide UPF search) or on this machine (C:\Users\frank and D:\ to depth 7).
results/s2_2026-09-18/xu_molecules/README.md records a bounded retrieval that failed for O and H.
The runner refuses any UPF whose MD5 differs from the pin, so nothing runs until the files are found
or a substitution is decided and recorded here.

| UPF | MD5 (deposited output headers) |
|---|---|
| o_pbe_v1.01.uspp.F.UPF | 2bcb18d16ea4b960afae9ec6d52f22d2 |
| h_pbe_v1.uspp.F.UPF | 3408e3ff4ec8b0a4e358431e7e038a48 |
| cr_pbe_v1.uspp.F.UPF | 68b6f918d1762dccfb11451fe85b0e0e |
| ir_pbe_v1.uspp.F.UPF | abf987a9674477536ede83817f8f8b70 |
| mn_pbe_v1.uspp.F.UPF | 5fd7c7b5c956fd19902447332617373a |
| mo_pbe_v1.uspp.F.UPF | 30c4dcd161f5d35cd49bb5239c51a633 |
| nb_pbe_v1.uspp.F.UPF | 573aab8a2fa660278ed4a62cd769473f |
| pt_pbe_v1.uspp.F.UPF | 4c71d6ad5ef119f1eb26a4d0b7884226 |
| re_pbe_v1.uspp.F.UPF | 6f5a5dcaf9c96c20d0ffdde0de57afc6 |
| rh_pbe_v1.uspp.F.UPF | 37b626987ad0dd8ec6bf4cc9ef289918 |
| ru_pbe_v1.uspp.F.UPF | df00be1c11b23341d9806d8f1dfa10cf |
| ti_pbe_v1.uspp.F.UPF | bcc8f6961b3b91f0cac3ca967d22d0fb |

## Comparison and decision rule (set now, before any run)

ΔE = E_escape - E_held, both the final `!` total energies of converged relaxations, in meV
(13.605693122 eV/Ry). d_off = the largest distance of an adsorbate atom from the mirror plane along
the locked axis (minimum image), in Å; the plane is the adsorbate coordinate of the held start
(x = 0.5 or y = 0.5 in crystal units on every selected case).

Validity (a case that fails any of these is reported as INVALID with the reason, never scored):

1. held: COMPLETE runner receipt, `bfgs converged`, header with the deposited symmetry count (2
   operations), and the lock reproduced: silentgate's reader and classifier label the held output
   LOCKED on the census axis.
2. escape: COMPLETE receipt, `bfgs converged`, header "No symmetry found".
3. Cr and Mn (nspin = 2): the total moment is fixed by tot_magnetization in both arms; if the final
   absolute magnetizations differ by more than 1.0 μB per cell the case is reported as a change of
   electronic state (UNRESOLVED), not as a lock cost.

Classification of a valid case:

- **HARMFUL**: ΔE < -10 meV and d_off(escape, final) > 0.10 Å. The adsorbate ended farther from the
  plane than it was placed and the energy fell.
- **BENIGN**: |ΔE| <= 10 meV and d_off(escape, final) <= 0.05 Å. The optimizer brought the adsorbate
  back toward the plane (it started at 0.10 Å) and found no lower structure.
- **UNRESOLVED**: every other valid outcome (for example a drop above 10 meV with the adsorbate still
  near its start, an outward drift with no drop, or ΔE > +10 meV), reported with its numbers.

Why 10 meV: each arm stops when the energy change per BFGS step is below etot_conv_thr = 1e-4 Ry
(1.4 meV), so two arms carry at most about 3 meV of convergence spread; repeats of one SCF state agree
within about 0.1 meV in this program (docs/research/s8-arm-c-extension-2026-10-08.md:774); the held
arm's symmetry-reduced k set and the escape's time-reversal-reduced set sample the same 4 x 4 x 1
mesh (the noinv test measured 3.2e-7 Ry); and 10 meV is the drop that the program's checked
relaxations already treat as real (delta = 10 meV, docs/research/lowtail-stall-robust-protocol-plan-2026-09-22.md:18).
The threshold is 7 times the per-arm convergence tolerance and below the 15.5 meV margin on which
the report's Ru result turns, so a lock cost at the size that would matter to the report cannot hide
under it. Why 0.10 Å: it is the H's starting offset, so a HARMFUL case must have moved the adsorbate
outward, downhill, by itself.

Readout: results/corpus_escape_2026-11-01/collect.py applies this rule to the downloaded outputs and
writes the table; the counts are reported per tier as k of n, with every case listed.

## Files

- builder: src/dft/corpus_escape_build.py (cases, decks, manifests, launch spec, Slurm script)
- decks: runs/corpus_escape_2026-11-01/<metal>__<job>__{held,escape}.in
- case table: results/corpus_escape_2026-11-01/cases.json
- launch: anvil/106_corpus_escape.slurm, results/corpus_escape_2026-11-01/launch_ops.py
- checks: results/corpus_escape_2026-11-01/verify_decks.py (independent parser), cost_estimate.py
- readout: results/corpus_escape_2026-11-01/collect.py

## Cost

Source: results/corpus_escape_2026-11-01/cost_estimate.py (cost_estimate.json). Per SCF iteration the
time is scaled from five banked pw.x 7.5 runs at 128 ranks on Anvil (two 2 x 1 Cr cells, the Mn 2 x 1
mirror relaxation, two 72-atom HEA slabs), by k-points per pool x bands^2 x plane waves (planning,
the program's envelope convention of src/dft/hea_cost_model.py) or x bands (floor); ceiling = 3 x
planning (the program's convention after the 5.8x CrO2 q333 miss). Iterations per relaxation cycle are
each case's own deposited counts (+2); cycles are 12 (held, converged deposit), 30 (held, unconverged
deposit) and 30 (escape). No four-layer slab has run on Anvil in this program, so every figure is an
extrapolation; the floor-to-ceiling range is the honest statement.

Per case: 51 atoms (*OOH) or 50 (*OH); 4 x 4 x 1 Gamma-centred mesh, 9 irreducible k-points held
(two operations plus time reversal; 18 in the list for nspin 2) and 10 escape (time reversal only);
391-461 electrons; 235-295 bands at the pw.x default (deposited 562-691).

| launch group | cases | planning SU | floor | ceiling | slowest row, planning wall (held / escape) | Slurm walls | reservation SU |
|---|---|---|---|---|---|---|---|
| tier 1a | 6 *OOH, converged deposits | 2,603 | 1,348 | 7,808 | 1.6 h / 3.9 h (RuO2) | 3 h / 6 h | 6,912 |
| tier 1b | 4 *OOH, unconverged deposits | 4,055 | 1,971 | 12,165 | 5.3 h / 5.3 h (MnO2) | 7 h / 7 h | 7,168 |
| **tier 1** | 10 | **6,658** | 3,319 | 19,973 | | | |
| tier 2 | 20 *OH | 9,173 | 4,696 | 27,519 | 1.6 h / 3.7 h | 3 h / 6 h | 23,040 |
| **tier 1 + 2** | 30 | **15,831** | 8,015 | 47,492 | | | |

At the deposited band counts the same model gives 37,687 SU planning for tier 1 alone, which is why
nbnd is the pw.x default.

Allocation: mybalance 9,963.3 CPU SU on 2026-11-01, about 300 still committed to array 21852915 (two
wholenode tasks of the S8 round 7, 3 h 50 min into a 5 h limit at the read-only check), so about
9,660 SU available. Tier 1a fits (reservation 6,912). Tier 1b's reservation (7,168) fits after tier 1a
only if tier 1a spends no more than about 2,500 SU, which is just under its planning figure. Tier 2
does not fit the allocation in any launch shape at planning cost. The launch script checks the live
balance against each group's reservation before submitting.

Partition: wholenode, one node (128 cores) per relaxation. The repo uses `shared` only for tiny probes
(anvil/88_pa_tiny_restart_probe.slurm, 4 cores); anvil/README.md records that `shared` bills
max(cores, ceil(mem_GB / 2)) SU per hour, and docs/48-anvil-sizing-2026-08-22.md measured SU per ionic
step flat from 40 to 128 ranks while the wall clock falls about 3x. Fewer cores would not save SU and
would triple the wall clock, and the pinned runner is fixed at 128 ranks. Each array runs all its rows
at once.

Time: tier 1a finishes about 4 h after its nodes start (6 h cap); tier 1b about 5.5 h (7 h cap). On
2026-11-01 sinfo showed 6 idle of 750 wholenode nodes; tier 1a needs 12 nodes at once and tier 1b 8.
For results by the evening of 3 November, tier 1a has to be submitted by the morning of 2 November;
tier 1b only adds to that if tier 1a comes in near its floor and the queue moves.

## Deck verification

1. Inputs: every deposited pwscf.in and pwscf.out used matches the sha256 the census registered for it
   (corpus_identity.files); each case's locked axis is a single axis, equal in the every-step and
   final-step census fields; the MD5 that each deposited output prints for each UPF equals the pin.
2. Builder guard (src/dft/corpus_escape_build.py, on the emitted bytes): each deck is re-parsed; every
   deposited key is either kept with its exact value or listed as dropped; the only added keys are
   the declared ones; K_POINTS, ATOMIC_SPECIES and CELL_PARAMETERS are the deposited cards byte for byte;
   species order and if_pos flags are unchanged; the held start is the deposited final geometry and is
   mirror-symmetric to 1e-6 Å with the adsorbate on the plane; the escape differs from the held deck
   only by the prefix, the nosym line and the adsorbate coordinates; noinv appears nowhere.
3. Independent check (results/corpus_escape_2026-11-01/verify_decks.py, deck_verification.json):
   ASE's namelist and espresso-in readers on the decks and the deposited inputs, ASE's espresso-out
   reader cross-read by a regex for the deposited final geometry, and spglib (symprec 1e-5 Å) for the
   symmetry each start presents. 30 of 30 cases pass: namelists equal apart from the declared lines,
   cards equal, held start equal to the deposited final geometry (largest difference 4e-15 Å), escape
   displacements equal to the recipe with no other atom moved, fixed-atom sets equal, and spglib finds
   2 operations on every held start (the deposited header count) and 1 on every escape start.
4. Runner contract: research_batch_seeded.validate() accepts all six stages of a licensed build in a
   scratch root (manifest rows, deck hashes, prefixes, calculation 'relax', nk, walls, the 126-iteration
   ceiling). It refuses the repo build as it stands ("unapproved manifest": the NOT LICENSED line), and
   it refuses UPF files whose MD5 differs from the deposited pins. Its projection validator passes all
   24 banked nspin = 1 projwfc outputs in runs/ (Ir, Ru, Ti slabs with *O, *OH, *OOH), so the eight
   non-magnetic metals should clear the step that follows each relaxation.
5. Readout: collect.py's per-arm reader and decision rule applied to the banked CrO2 2 x 1 *OOH pair
   (runs/probe/Cr_cellsym/s0_OOH__2x1v_mir.out, runs/s3/Cr/s0_OOH__2x1v_escape.out) give held LOCKED
   on y with 2 operations, escape "No symmetry found", dE = -150.82 meV, H 0.866 Å off the plane:
   HARMFUL. That is the report's Section 4.1 result (150.8 meV, 0.87 Å), so the rule recovers the one
   known positive case.

What these checks cannot show: that pw.x 7.5 with the deposited UPFs reproduces the deposited 5.0.2
energies. The held arm measures E_held in this environment for that reason; the readout reports
E_held next to the deposited final energy as context only.

## Commands (Frank runs them; nothing has been staged or submitted)

1. Obtain the 12 deposited UPF files (MD5s above) into one local folder, for example
   `D:\sts-pseudo\xu2014`. If they cannot be found, a substitution has to be decided and dated in this
   note first; it changes the decks and pins and needs a rebuild.
2. License, rebuild and re-check:
   `python src/dft/corpus_escape_build.py --decision "<your words>" --decision-date <date> --replace`,
   then `python results/corpus_escape_2026-11-01/verify_decks.py` and
   `python results/corpus_escape_2026-11-01/cost_estimate.py`.
3. Commit the package (explicit paths) and push: stage refuses an unpushed commit. `results/` is
   ignored by .gitignore, so its files need `git add -f`, as the earlier launch packages did:
   `git add -f results/corpus_escape_2026-11-01/{launch_spec.json,cases.json,launch_ops.py,collect.py,verify_decks.py,cost_estimate.py,cost_estimate.json,deck_verification.json}`
   and `git add src/dft/corpus_escape_build.py anvil/106_corpus_escape.slurm docs/research/corpus-escape-2026-11-01.md runs/corpus_escape_2026-11-01 runs/m_corpus_escape_2026-11-01_*.txt`.
   The UPF files are never committed (the repo is public); stage uploads them from the local folder.
4. `python results/corpus_escape_2026-11-01/launch_ops.py stage D:\sts-pseudo\xu2014`
5. Per group, in order tier1a, tier1b, tier2: `launch_ops.py preflight <group>`, `submit <group>`,
   `validate <group>`, `release <group>`.
6. After the arrays finish: `python results/corpus_escape_2026-11-01/collect.py`.

## Risks

- Pseudopotentials (blocking): above. A substitution (for example the current GBRV versions) would
  test the saddle question on a slightly different energy surface. Both arms would still share it, but
  the 2026-09-18 operating record refused modern substitutes for the Xu molecular references. That was
  a different use (absolute energies), and the decision is Frank's.
- Allocation: tier 1 planning (6,658 SU) is 69 % of what is available and its ceiling is twice the
  balance; tier 2 does not fit. Arrays that hit their Slurm wall are KILLED and reported, not rerun.
- Queue: 12 whole nodes at once for tier 1a with 6 idle on 2026-11-01; waiting can exceed the
  run time.
- Project space: 4.5 of 5.0 TB used (90.2 %). The retained wavefunctions are about 1.5-3 GB per run,
  so about 0.1 TB for all 60 runs; preflight requires 0.1 TB free.
- Physics: a held arm can fail to reproduce the lock if pw.x 7.5 finds a different symmetry count;
  that case is INVALID by rule. For CrO2 and MnO2 (nspin 2, fixed total moment) an escape can change
  the local moments; the rule reports that as UNRESOLVED rather than as a lock cost. A saddle softer
  than about i84 cm-1 may still stall near the 0.10 Å start; it then reads as UNRESOLVED, not
  BENIGN, because BENIGN requires the adsorbate to end within 0.05 Å of the plane.
- Post-census choice: the cases were picked after the census was read. That is stated wherever the
  results appear.

## Pseudopotential substitution (Frank, 2026-11-01, before any run)

The deposited GBRV v1/v1.01 UPF files (MD5 pins above) are no longer distributed: the September retrieval record
(`results/s2_2026-09-18/xu_molecules/README.md`) and a recheck on 2026-11-01 found no copy on Anvil, on this machine or
at the primary site. Frank's decision, 2026-11-01: run both arms of every case on the current GBRV v1.5 UPFs
(`all_pbe_UPF_v1.5.tar.gz`, https://www.physics.rutgers.edu/gbrv/). Every other deck setting is as listed above.

| Deposited file | Run file | Run MD5 |
|---|---|---|
| o_pbe_v1.01.uspp.F.UPF | o_pbe_v1.2.uspp.F.UPF | 734c27235a0248c51dbae37a1fbe46ec |
| h_pbe_v1.uspp.F.UPF | h_pbe_v1.4.uspp.F.UPF | 761ae9a214b05c3daf00ab9f6b793d6f |
| cr_pbe_v1.uspp.F.UPF | cr_pbe_v1.5.uspp.F.UPF | 0d52af634a40206e4dee301ad30da4bf |
| ir_pbe_v1.uspp.F.UPF | ir_pbe_v1.2.uspp.F.UPF | 8836f839c3459d2b385c504ce6d91f2c |
| mn_pbe_v1.uspp.F.UPF | mn_pbe_v1.5.uspp.F.UPF | 82ef2b46521d7a7d9e736dc3972e4928 |
| mo_pbe_v1.uspp.F.UPF | mo_pbe_v1.uspp.F.UPF (byte-identical) | 30c4dcd161f5d35cd49bb5239c51a633 |
| nb_pbe_v1.uspp.F.UPF | nb_pbe_v1.uspp.F.UPF (byte-identical) | 573aab8a2fa660278ed4a62cd769473f |
| pt_pbe_v1.uspp.F.UPF | pt_pbe_v1.4.uspp.F.UPF | f09d6de1a584b5a045c4fc126da2d0c4 |
| re_pbe_v1.uspp.F.UPF | re_pbe_v1.2.uspp.F.UPF | 85f993410f3e006da9d71c142b4ad953 |
| rh_pbe_v1.uspp.F.UPF | rh_pbe_v1.4.uspp.F.UPF | 761627e959a2e3a1f56b0b5fe687810e |
| ru_pbe_v1.uspp.F.UPF | ru_pbe_v1.2.uspp.F.UPF | 7158a806dd851261a58e6920c40ebe78 |
| ti_pbe_v1.uspp.F.UPF | ti_pbe_v1.4.uspp.F.UPF | 88a00a6731bd790ddea75d31a80cb452 |

What this changes: the test now asks whether each deposited locked geometry is held above a lower structure on the
GBRV v1.5 energy surface, a close but not identical surface to the deposited one. Both arms use the same files, so
ΔE = E_escape − E_held is internally consistent, and the held arm re-relaxes from the deposited final geometry with the
symmetry kept. The decision rule above is unchanged, including INVALID when the held arm no longer reproduces the lock.
Results are reported with this substitution stated. Launch scope (Frank, 2026-11-01): tier1a now; tier1b only if the
balance after tier1a covers its reservation; tier2 not launched.
