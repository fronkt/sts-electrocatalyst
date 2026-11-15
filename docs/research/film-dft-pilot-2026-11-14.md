# Film-model DFT pilot: validation set (registered 2026-11-14, before any run)

Context: `tasks/isef-2027-master-plan-2026-11-14.md` section 5. The STS screen scored bulk-composition
rutile sites; the electrodes instead grew an oxyhydroxide film with Cr and Mn leached. This pilot
asks whether an oxyhydroxide edge-site model reproduces a trend that experiment already settles,
before any of it is used to rank alloys.

## Model
- Prototype: beta-NiOOH, P3m1 (Materials Project mp-999337, GGA+U, same U values as here),
  `data/film/NiOOH_mp-999337.cif`. CoOOH uses the same layer prototype with heterogenite's lattice
  (mp-27913: a = 2.849 A, interlayer 4.312 A), so the films differ in chemistry, not stacking.
- Surface: (012) = hexagonal (01-12) edge; termination with a 5-coordinated top metal and no metal
  below CN 5; 2x1 in-plane (48 atoms; adsorbate images ~6 A apart); bottom half fixed;
  16 A vacuum; dipole correction (sawtooth at 0.80 c, identical within a film).
- Ni(Fe)OOH: one Fe in the top edge row (1 of 12 metals; 1 of 2 edge sites).
- QE 7.5, PBE+U (Ni 6.2, Fe 5.3, Co 3.32 eV; MP values), SSSP-efficiency pseudos (md5-identical
  to the Anvil set), 80 / 640 Ry, 3x3x1 k, spin-polarized ferromagnetic start, nosym; adsorbates
  start off the mirror plane with a seeded displacement (seed 20261114).
- CHE free energies with the project's ZPE-TS corrections (OH 0.35, O 0.05, OOH 0.40 eV);
  eta = max step - 1.23 V.
- Builder: `src/dft/film_pilot_build.py`; inputs: `runs/film_pilot_2026-11-14/` (17 jobs).

## Jobs (17)
Clean slabs NiOOH, Ni(Fe)OOH, CoOOH; *OH / *O / *OOH on: NiOOH Ni site, Ni(Fe)OOH Fe site,
Ni(Fe)OOH Ni site next to Fe, CoOOH Co site; gas H2O, H2.

## Registered criteria
- **V1 (gate):** eta(Fe site, Ni(Fe)OOH) < eta(Ni site, NiOOH). Experiment: Fe incorporation
  makes NiOOH far more active, with Fe sites implicated. If the model misses this, it is not used to
  rank film compositions in its current form.
- **V2 (secondary, reported):** eta(CoOOH) < eta(NiOOH), the experimental order for Fe-free films.
- **QC (per state):** `qe_qc` trusted energy (SCF converged, forces below threshold) and
  `adsorbate_qc` integrity (adsorbate bound, not dissociated). A failed state is "not evaluable",
  never imputed. Final magnetic moments are recorded for every state.
- **Decision:** V1 pass with all states evaluable -> U = 0 single points on the relaxed geometries
  (Hubbard-U sensitivity, Zeng's suggestion) and then production on round-1/round-2 film
  compositions. V1 fail -> stop and revisit facet, U, or solvation before spending more.

## Amendment 1 (2026-11-15 02:00Z, before any energy existed)
Attempt 1 (01:10-01:55Z) produced no converged SCF in 56-83 iterations on any slab: NiOOH stalled
near 1e-5 Ry, CoOOH oscillated at 0.1-0.4 Ry in a high-spin state (~33 muB per 12 Co; Co3+ in
CoOOH is low-spin), Ni(Fe)OOH swung between 8 and 18 Ry. Cause: starting moments inherited from
the rutile tier (Ni 0.3, Fe 0.5, Co 0.4 of valence = 5-8 muB per metal) with mixing_beta 0.3.
Attempt 2 uses Ni 0.10, Fe 0.30, Co 0.05 (about 1.8 / 4.8 / 0.85 muB), mixing_beta 0.1,
mixing_ndim 12, conv_thr 1e-6 (the project default; attempt 1 had 1e-7). Attempt-1 outputs are kept
in `attempt1/` on the box. Criteria V1/V2 and QC are unchanged. Spin states are reported for every
state (expected: Ni ~1 muB, Fe ~4-5 muB, Co ~0 muB in the bulk-like layers).

## Amendment 2 (2026-11-15 02:54Z, before any slab energy existed)
In attempt 2 every state's first SCF converged or was converging except the clean CoOOH slab, whose
SCF error oscillated between 0.01 and 0.17 Ry with no trend over 85 iterations (total moment
3.4-3.9 muB; likely the bare CN-5 edge Co hopping between spin states; the adsorbate states, where
that site is 6-coordinated, converged). It was stopped and rerun as `CoOOH__slab_r2` with
mixing_beta 0.05 and mixing_ndim 20 only (structure, smearing, moments, U unchanged, so the
converged energy is the same quantity), on 12 otherwise idle cores. The readout uses the rerun's
energy for the CoOOH clean slab.

## Amendment 3 (2026-11-15 04:45Z, before any relaxation finished)
- NiOOH clean slab: the third SCF of its relaxation sat at 2.5-3e-6 Ry for ~100 iterations against
  conv_thr 1e-6 (a noise floor; 1e-6 Ry is ~1e-5 eV). Restarted as `NiOOH__slab_r2` from the
  geometry of its last BFGS step with conv_thr 5e-6 Ry (`src/dft/film_box/qe_restart_input.py`).
- conv_thr 5e-6 Ry also for every job not yet started (8 Ni(Fe)OOH / NiOOH adslabs). The energy
  error this allows (~7e-5 eV) is far below the CHE and DFT+U uncertainties.
- CoOOH clean slab: the mixing-only rerun (`_r2`) went flat at 1.4e-4 Ry with a total moment of
  ~7.8 muB, i.e. four bare CN-5 edge Co (two per face) at ~2 muB with bulk-like Co3+ near 0. Rerun as
  `CoOOH__slab_r3` with tot_magnetization = 8 (the value the free SCF drifted to). Reported as a
  fixed-moment state; if the CoOOH sites become evaluable this is stated next to V2.
- The queue was handed to `box_run2.sh`, which schedules by live pw.x ranks and finishes only when
  no pw.x is left on the box. Criteria unchanged.

## Amendment 4 (2026-11-15 07:20Z, before any relaxation finished)
Root cause of the SCF stalls: pw.x's default `upscale` (100) lowers conv_thr as forces shrink during
a relaxation; NiOOH__slab_r2 printed `new conv_thr = 7.988e-7 Ry` and then sat at ~1.7e-6 Ry, the
SCF noise floor of these magnetic slabs. Every live relaxation (NiOOH and Ni(Fe)OOH slabs,
Ni(Fe)OOH Fe-site *O, the three CoOOH adslabs) was restarted from its last geometry with
`upscale = 1` and conv_thr 5e-6 Ry; the eight adslabs not yet started got the same settings, so
every final energy is computed under identical SCF settings. CoOOH clean slab, which never finished
an SCF: `_r4` = same geometry, CG diagonalization, mixing_beta 0.02, tot_magnetization 8.
One queue (`box_run2.sh` with `jobs3.txt`, 24 ranks x 8 jobs), V1-critical states first.
Criteria unchanged. If the CoOOH clean slab still fails, its sites are reported only through the
slab-independent steps (dG2, dG3) as a bound on eta, labelled as such, and V2 is "not evaluable".

## Amendment 5 (2026-11-15 09:25Z, before any relaxation finished)
With upscale fixed, the restarted relaxations progressed (NiOOH and Ni(Fe)OOH slabs, Fe-site *O and
*OH), but four states that had to converge a first PBE+U SCF from atomic densities did not in
120-137 iterations: NiOOH Ni-site *O (0.8-1.1 Ry), *OH (0.03-0.04 Ry), *OOH (~9e-5 Ry), and
Ni(Fe)OOH Fe-site *OOH (~1.3e-4 Ry). These four, and every job not yet started, now use a U-ramp:
a U = 0 SCF at the same geometry (conv_thr 1e-5), then the PBE+U relaxation starting from its
wavefunctions and density (`src/dft/film_box/make_ramp.py`, queue `box_run3.sh`, `jobs4.txt`).
If the U = 0 SCF fails, the relaxation starts normally. Final energies are PBE+U as registered; the
ramp changes only the SCF starting point, so a state may settle into a different magnetic solution
than a cold start would: final moments are reported per state. Criteria unchanged.

## Amendment 5b (2026-11-15 11:28Z)
The first three ramped relaxations stopped at start-up with `read_scf: Reading ldaU ns`: a PBE+U run
starting from a saved density also reads the Hubbard occupation matrices, which a run without a
HUBBARD card does not write. Stage A now keeps the card with U = 1e-8 eV (numerically zero, but the
occupations are computed and saved). A three-iteration stage A followed by a stage B reading it was
run on the box before the queue was relaunched (`src/dft/film_box/fix_ramp.sh`).

## Amendment 6 (2026-11-15 14:57Z, before any eta existed)
Trusted energies at this point: Ni(Fe)OOH clean slab (`_r2`, 18 BFGS steps), H2O, H2; no adslab
had finished, so no dG or eta could be computed.
- NiOOH clean slab: the 11th SCF of `NiOOH__slab_r3` sat at 5.06-5.18e-6 Ry for 200 iterations
  against conv_thr 5e-6 (a noise floor just above the threshold; the earlier floor was 1.7e-6) and
  pw.x stopped. Restarted as `NiOOH__slab_r4` from its last geometry with conv_thr 1e-5 Ry; nothing
  else changed. The energy precision this allows (~1e-4 eV) is still far below 1 meV. Energy over the
  r3 steps was still falling ~0.6-1.1 mRy per step (total force 0.045 -> 0.016 Ry/bohr).
- Rule from here on: a relaxation stopped by an SCF that is flat within 4x of its conv_thr is
  restarted the same way (last geometry, conv_thr 1e-5). An SCF that fails far above its threshold
  is handled case by case and recorded here.
- `NiFeOOH__Ni1_OH` (not a V1 or V2 state) was stopped 19 min into its U = 0 stage to free cores
  for the V1-critical slab and re-queued last.
- Readout (`src/dft/film_pilot_readout.py`): (a) each state is evaluated on ONE run, energy and
  adsorbate integrity alike: the latest rerun with a trusted energy, else the original (previously
  the rerun's energy was paired with the original's integrity record); (b) final geometry is read
  from the output's last ATOMIC_POSITIONS block with the input cell, because ase's espresso-out
  reader fails on these outputs; (c) ionic steps are counted over the restart chain. Tested on a
  snapshot of the live outputs. Criteria unchanged.

## Amendment 7 (2026-11-15 15:08Z, before any eta existed)
Per-metal moments (integrated in pw.x's atomic spheres) show that the states of a film are not in
one magnetic configuration, so a CHE difference between them would include a configuration-change
energy as well as the adsorption energy:
- NiOOH: clean slab 20.0 muB, with the four middle-layer Ni (z = 5.3 and 7.1 A, both columns) at
  1.92-1.94 against 1.24-1.32 in the *OH state (11.0 muB); *O and *OOH states sit at 11.4-12.3 muB.
- Ni(Fe)OOH: the finished clean slab (`_r2`, 14 muB) has one top-edge Ni antiparallel (-1.12);
  Fe-site *O has none, *OH one (the same atom), *OOH three. Across the slab's own restart
  (16 muB, no flip -> 14 muB, one flip, one BFGS step apart) the energy changed by -0.84 mRy
  (-11 meV), about one BFGS step's decrease, so a flip there is nearly free.
- CoOOH: bulk-like Co near 0 muB as expected; the second top-edge Co varies between 0.04 and 1.75.
Actions: queue-5 launches stopped (every remaining queued job would need a controlled magnetic
start); the stalled NiOOH Ni-site *O and *OOH first SCFs (no geometry yet) and NiFeOOH__Ni1_O
(not V1/V2) stopped. Relaxations making geometry progress keep running, as their geometries seed
any rerun. Two single points measure the size of the NiOOH effect at fixed geometry:
`NiOOH__slab_magLS` (r4 start geometry, all Ni started at 0.05, vs. r4's first energy) and
`NiOOH__Ni0_OH_magHS` (Ni0_OH_r2's step-7 geometry, the four middle Ni started at 0.17, vs.
Ni0_OH_r2's 7th energy) (`src/dft/film_box/make_magdiag.py`, `amend7_magdiag.sh`). A first launch of
the second had the new species out of order (0.17 put on O) and was stopped after 1.5 min; the
relaunch was checked against pw.x's printed starting moments. The fix for the whole set (one
magnetic configuration per film, imposed on every state, plus a moment-consistency QC) is to be
registered before any rerun. Criteria V1/V2 unchanged.

## Compute
- 83 Sciences AWS account (Frank, 2026-11-14), c7a.48xlarge (192 cores, 384 GiB), on-demand,
  us-east-1; 6 jobs x 30 ranks (-nk 3); gas jobs 8 ranks. Box scripts: `src/dft/film_box/`.
- Cost estimate before launch: ~8,000-13,000 core-hours (~42-68 instance-hours), uncertain by ~2x;
  the first hour's SCF timing is used to re-estimate. Hard cap 48 h (box stops itself).
- Production is intended for Anvil (CHE260157 supplement request, `access-supplement-request-2026-11-14.md`).
