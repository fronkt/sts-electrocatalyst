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

## Amendment 8 (2026-11-15 16:45Z, before any eta existed)
Diagnostic results (same geometry and Hamiltonian within each pair; moments as in amendment 7;
"high-spin" Ni ~1.9 muB, low-spin ~1.3):
- NiOOH clean slab: all Ni low-spin (`slab_magLS`, 12.0 muB, every Ni 1.24-1.42) -5130.39864 Ry
  vs. `slab_r4` step 1 (16.0 muB; the z = 7.1 A Ni pair at 1.88) -5130.28714 Ry: low-spin is lower by
  0.1115 Ry = 1.52 eV. `slab_r3`'s last step (20.0 muB; the z = 5.3 and 7.1 A pairs at 1.91-1.92),
  one BFGS step before r4's start, was a further 0.1139 Ry (1.55 eV) higher. Each high-spin Ni costs
  ~0.75 eV; the slab relaxations followed a metastable configuration.
- NiOOH *OH: the middle Ni started high-spin (`Ni0_OH_magHS`; only the z = 7.1 A pair went high,
  1.87-1.88; 15.0 muB) -5173.00123 Ry vs. `Ni0_OH_r2` step 7 (all low-spin, 11.0 muB)
  -5173.12400 Ry: 1.67 eV higher. The NiOOH adslab states are all-low-spin; with r4 as the
  reference, dG(*OH) would have carried an error of ~1.5 eV.
Per-metal moments of every other state:
- Ni(Fe)OOH Fe-site *O has two solutions. The original run (14.0 muB) reached -5157.86364 Ry at step
  8 and was stopped mid-SCF at amendment 4; `_r2` restarted from exactly its last geometry
  (max |dx| = 0) and its first SCF landed at 12.0 muB, -5157.82838 Ry, 0.48 eV above the original's
  step 8; after 10 steps `_r2` is at -5157.84168 Ry, still 0.30 eV above. The metal moments of the
  two agree (sphere sums 16.45 vs. 16.42 muB), so the 2 muB differ off the metals. The readout's
  "latest rerun with a trusted energy" rule (amendment 6) would have used the higher solution.
- Ni(Fe)OOH: the trusted slab `_r2` (14.0 muB) has top-edge Ni 30 antiparallel (-1.12) and is
  6.4 mRy (86 meV) below the unflipped original's last step; *OH has the same single flip; both *O
  runs have none; *OOH `_r2` has Ni 5, 29 and 30 antiparallel.
- CoOOH: the clean slab has not finished an SCF (`slab`, `_r2`, `_r3`); the non-site top-edge Co 30
  is 1.66 / 1.75 / 0.04 muB in *O / *OH / *OOH.
- U = 0 stage SCFs (same geometries): NiOOH Ni-site *O / *OH / *OOH, every Ni 0.62-0.84 muB except
  the site Ni (0.06-0.12), no high/low-spin split, all converged (73-150 iterations); Ni(Fe)OOH
  *OOH again has Ni 5, 29, 30 antiparallel (-0.73 to -0.83).
Actions:
- Stopped as unusable under any fix: `NiOOH__slab_r4` (metastable configuration),
  `NiFeOOH__Fe0_O_r2` (the higher *O solution), `NiFeOOH__Fe0_OOH_r2` (three flips). Still running:
  `NiFeOOH__Fe0_OH`, `NiOOH__Ni0_OH_r2`.
- Provisional runs on the freed cores, pending the choice between (A) PBE+U as registered with
  magnetic control and (B) the pilot at U = 0 (`src/dft/film_box/make_variant.py`,
  `amend8_provisional.sh`): A: `NiOOH__slab_r5` (the `slab_magLS` input run as a relaxation; its
  first energy must reproduce slab_magLS), `NiOOH__Ni0_O_r3` and `NiOOH__Ni0_OOH_r3` (cold PBE+U
  start, Ni 0.05, from the input geometry; tests whether a low-spin start converges the SCFs that
  stalled). B: `u0__NiOOH__slab` (r4 start geometry) and `u0__NiFeOOH__slab` (slab_r2 final
  geometry, ferromagnetic start), U = 1e-8 as in the ramp stage. `u0__` runs are outside the
  readout's rerun chains.
- No eta is computed until the fix is registered here. Under either option it includes: one
  reference configuration per film from its clean slab; every state started in it; a per-state QC
  that the non-site metals match the reference in sign and spin state; and a rule for reruns: a
  rerun replaces its predecessor only if it is the same solution (its first energy at the
  predecessor's last geometry not higher), otherwise the lower solution stands and both are
  reported. The readout gets the same rules.
- Spend guard: every run stops at 2026-11-16T08:00Z unless extended (`src/dft/film_box/deadline.sh`);
  the idle watchdog then packages, the local loop pulls, and the box stops (~31 instance-hours).

## Amendment 8b (2026-11-15 19:03Z, before any eta existed)
Provisional-run results:
- A: `NiOOH__slab_r5` step 1 = -5130.39863 Ry, reproducing `slab_magLS` to 6e-6 Ry; all Ni
  low-spin and parallel through 18 steps (-5130.41324 Ry, total force 0.013 Ry/bohr).
  `NiOOH__Ni0_O_r3` (PBE+U, Ni 0.05, cold start): first-SCF error between 0.17 and 5 Ry over 150
  iterations, the third PBE+U start of NiOOH *O that fails. `NiOOH__Ni0_OOH_r3`: first SCF converged
  with Ni 5 and 29 antiparallel (7.4 muB), inconsistent with the all-parallel slab. Both stopped.
- B: `u0__NiOOH__slab`: all Ni parallel (0.49-0.85 muB) through 5 steps. `u0__NiFeOOH__slab`
  (ferromagnetic start): Ni 5, 29, 30 antiparallel (-0.54 to -1.19) from its first SCF on, the
  pattern Ni(Fe)OOH *OOH shows at U = 0 and at PBE+U.
- `NiFeOOH__Fe0_OH` stopped itself at 16:57Z (7th SCF flat at 5.6-6.4e-6 Ry vs. 5e-6; the
  amendment-6 case). Not restarted: it is a PBE+U state.
Actions (`src/dft/film_box/amend8b_u0_adslabs.sh`): provisional U = 0 relaxations of the six V1
adslab states, each started in its film's U = 0 slab configuration (NiOOH: all Ni parallel, Ni 0.1;
Ni(Fe)OOH: Ni 5, 29, 30 relabelled with a -0.1 start, checked in the input and in pw.x's printed
starting moments). Start geometries: NiOOH *O and *OOH from their input geometries; NiOOH *OH from
`Ni0_OH_r2`'s latest; Ni(Fe)OOH *O from the original run's last (the lower PBE+U solution); *OH and
*OOH from their PBE+U runs' last. Three started; three queued (`side_queue.sh`, which never starts a
run after the deadline). Still running on the A path: `NiOOH__slab_r5`, `NiOOH__Ni0_OH_r2`. Nothing
is evaluated and the A/B choice is pending. CoOOH (V2) has no U = 0 run yet.

## Amendment 9 (2026-11-15 21:40Z, before any eta existed)
Frank chose B. From here the pilot's model is PBE with U = 0 (1e-8 eV in the HUBBARD card, as in
the ramp stage), spin-polarized; prototype, (012) edge slabs, cutoffs, k-mesh, smearing, dipole
correction, CHE corrections and the gas references (`gas__H2O`, `gas__H2`, no Hubbard species) are
as registered; conv_thr 5e-6 Ry (amendment 6), forc_conv_thr 2e-3 Ry/bohr. Evaluated runs are the
`u0__` relaxations.
- Why: at PBE+U each film state has magnetic solutions 0.3-1.7 eV apart (amendments 7-8b), larger
  than the V1 gap being tested, and NiOOH *O did not converge at PBE+U from three starts. At U = 0
  the SCFs converge and the moments differ by tenths of a muB, not by spin state.
- Cost: without U, PBE over-delocalizes the 3d electrons and shifts oxyhydroxide adsorption
  energetics relative to PBE+U. A V1 pass says the U = 0 model ranks these films in the
  experimental order; it says nothing about PBE+U.
- The PBE+U runs are kept as the record of why A was dropped; no eta is computed from them. The
  Ni(Fe)OOH Ni-site states (`Ni1`) enter no criterion and are not run at U = 0.

Magnetic configuration. This replaces amendment 8's fixed-reference QC. At U = 0 the Ni(Fe)OOH
relaxations do not all hold the clean slab's configuration (pw.x 1-based atoms; Fe = atom 6, the
Fe site; atom 1 is a fixed bottom-layer Ni):
- the slab is in C1 (Fe +2.6; Ni 5, 29, 30 at -1.0, -1.0, -0.4; every other Ni +0.3 to +0.85);
- Fe-site *O started in C1 and was in C2 by step 4 (Fe -1.7; every Ni +0.5 to +0.8);
- *OOH was in C3 at step 1 (Fe +2.3; Ni 5 and 29 at -1.1 and -1.0; Ni 30 +0.7).

Under amendment 8's rule *O and *OOH would not be evaluable. Each state's energy is what decides
which configuration is right for it. Rule:
1. A film's candidate configurations are the sign patterns its U = 0 relaxations end in. Patterns
   are taken over metals with |m| >= 0.25 muB, relative to atom 1, so a global flip is the same
   configuration.
   - Ni(Fe)OOH: C1, C2, C3, plus any new pattern a Ni(Fe)OOH relaxation ends in. Every state then
     gets a single point in the new pattern too.
   - NiOOH: all Ni parallel (the slab and every U = 0 SCF so far).
   - CoOOH: set from its relaxations, the same way.
2. Each converged Ni(Fe)OOH relaxation gets fixed-geometry single points in C1, C2 and C3 at its
   final geometry: cold start from signed starting moments (`src/dft/film_box/make_cfg_sp.sh`),
   launched ahead of the CoOOH runs by `post_relax.sh`. Two checks apply:
   - The single point in the state's own configuration must reproduce its last relaxation energy
     within 1 mRy; this tests the procedure.
   - A single point whose SCF leaves its target pattern is recorded and does not count as that
     configuration.
3. A state's energy is the lowest of its relaxed energy and its counting single points. A single
   point at the relaxed geometry is an upper bound on that configuration's relaxed energy, so the
   error is at most the relaxation energy the other configuration would gain (reported). Each
   state's configuration is reported.
4. V1 and V2 are also computed with each state as its relaxation ended ("as relaxed"). V1 passes
   only if it passes both ways. If the two disagree, V1 is reported as configuration-sensitive,
   not a pass.

Reruns. A rerun replaces its predecessor in two cases:
- the predecessor completed no SCF;
- it started from the predecessor's last geometry and its first energy is at most 1 mRy above the
  predecessor's last (the same solution).

Otherwise the run with the lower last energy is used and both are reported. QC is otherwise as
registered: a trusted energy (SCF and relaxation converged) and adsorbate integrity. A relaxation
that the cap stops before it converges is not evaluable unless continued under this rule. Readout:
`python src/dft/film_pilot_readout.py --model u0` implements rules 1-4 and the rerun rule.

Actions (21:26-21:37Z, `src/dft/film_box/amend9_b.sh`, `amend9_launcher.sh`):
- Stopped `NiOOH__Ni0_OH_r2` (PBE+U, not needed). Stopped `u0__NiOOH__Ni0_O`: its first SCF sat
  at 2.4-3.5e-4 Ry for the last ~60 of 146 iterations.
- Started `u0__NiOOH__Ni0_O_r2`, the same input started from the converged U = 0 density at the
  same geometry: `NiOOH__Ni0_O_r2`'s ramp stage, -5173.76319 Ry, every non-site Ni parallel.
  Positions were checked identical, and the stored U was checked as 1e-8 eV. It replaces its
  predecessor under the first rerun case.
- `u0__NiFeOOH__Fe0_OH` started from the amendment-8b queue.
- CoOOH (V2): `u0__CoOOH__slab` comes from the `slab_r2` input (beta 0.05, ndim 20; not the
  tot_magnetization-constrained `_r3`). Co-site *O, *OH and *OOH come from their PBE+U runs' last
  geometries. All are cold starts with Co 0.05, queued behind the single points.
- `NiOOH__slab_r5` (PBE+U) finished at 20:09Z (30 steps, -5130.41446 Ry, all Ni low-spin and
  parallel); it is reported only.

Spend: Frank extended the cap from 2026-11-16T08:00Z to 14:00Z (22:08Z; +6 instance-hours,
~$59, ~37 instance-hours / ~$363 in all), so the V1 single points and the CoOOH relaxations can finish.
Check (21:51Z): `u0__NiOOH__Ni0_O_r2`'s first SCF converged in 14 iterations at -5173.76326 Ry,
0.07 mRy below the ramp stage at the same geometry. Every non-site Ni is parallel and within
0.24 muB of the slab's moment.

Fe0_OH rerun (2026-11-16 00:45-01:04Z, `fe0oh_r2_test.sh`, `fe0oh_r3.sh`, `map_restart.py`, `yield_co.sh`):
- `u0__NiFeOOH__Fe0_OH` completed no SCF. Its first SCF reached 2e-4 Ry by iteration ~70, then sat at
  3.4-14e-5 Ry (conv_thr 5e-6) through iteration 200. The energy moved within 0.2 mRy of
  -5161.2657 Ry, and total/absolute magnetization was steady at 5.80/13.71 muB. `run_side.sh` deleted
  its density at exit.
- `_r2` is the same input with startingpot = 'file' from the converged `u0__NiFeOOH__slab` density
  (BFGS step 25, C1, which is the pattern the original was seeded with). It stopped in read_scf
  after 6 s because QE also reads occup.txt (Hubbard ns) and paw.txt (PAW becsum) with
  startingpot = 'file'. Both are per-atom, and the slab has 48 atoms against Fe0_OH's 50.
- `_r3` is the same restart with both files mapped onto the 50 atoms by `map_restart.py`. Each atom
  gets the nearest same-element slab atom (max 0.49 A); ns = 0 on the adsorbate O and H, and becsum
  is taken from the top hydroxyl O/H. QE read it ("starting charge 370.0, renormalised to 377.0").
  Only the starting guess differs; the input, geometry and thresholds are the original's. It
  replaces its predecessors under the first rerun case and is on the C1-C3 single-point watch list.
- V1 before V2: `u0__CoOOH__slab` (started 00:47Z, first SCF unfinished) was stopped to free r3's
  cores. Its dir is in `runs_stopped/`, and `post_relax.sh` relaunches it from `co_queue.txt` when
  cores free.

SCF plateaus inside relaxations (03:15-03:25Z, `rescue_0320.sh`, `post_relax.sh` v2, `run_side.sh` v2):
- `_r3` failed. Its first iteration was 1.4e5 Ry and -5254 Ry, with negative rho up to 3 e. After 108
  iterations it was still at 6.5 Ry and 3 Ry below the cold run's energy. The mapped occupations did
  not give a usable start, so it was stopped.
- Two more relaxations hit the same wall partway through:
  - `u0__NiOOH__slab`, step 26: 173 iterations at 4e-5 to 1.5e-3 Ry, total moment wandering
    9.29-9.65 muB.
  - `u0__NiOOH__Ni0_OOH`, step 8: about 190 iterations at 5.3-8e-6 Ry against 5e-6, energy steady
    to 0.02 mRy.
  Both finished their earlier steps at 5e-6, and nothing in the model or thresholds changed. The
  stalls look like slow magnetic (moment-sloshing) modes at particular geometries.
- `u0__NiOOH__slab_r2`: the last (step-26) geometry, startingpot = 'file' from its own step-25
  density. The density was hardlinked to `keep/` before `run_side.sh` could delete it. The atoms
  are the same, so nothing is mapped.
- `u0__NiFeOOH__Fe0_OH_r4`: the original input and geometry, startingpot = 'file' from the PBE+U
  `NiFeOOH__Fe0_OH` save. It has the same 50 atoms and its step-6 density; the U = 1e-8 run
  rebuilds the moments. Its first iterations were 0.93 and 0.35 Ry.
- `post_relax.sh` v2 keeps hardlinks to every watched relaxation's density files in `keep/`. When a
  relaxation logs DONE with SCF_FAIL > 0, it writes `RUN_rK`: the last geometry (the input geometry
  if no step finished) and startingpot = 'file' from the kept density, staged in `stage/`.
  `run_side.sh` v2 moves the staged density into tmp/. The rerun goes to the top of the queue
  (CoOOH: top of `co_queue.txt`) and takes over RUN's watch entries. The cap is three automatic
  reruns per chain, and none for an automatic rerun that again finishes no step. These are reruns
  under the amendment-9 rerun rule; model, thresholds and evaluation are unchanged. It was
  sandbox-tested on copies of the failed slab (25 steps) and of the Fe0_OH run with no completed
  step, before deployment.

New candidate configuration C4 (03:55Z, rule 1). `u0__NiFeOOH__Fe0_OH_r4`'s first SCF converged in
36 iterations at -5161.26683 Ry. That is 1.1 mRy below the cold run's plateau energy at the same
geometry. In pw.x 1-based atoms, it has Fe6 +1.85, Ni5 +0.81 and Ni29 +1.15, and only Ni30 at
-0.69; every other Ni is +0.50 to +0.86. This is none of C1-C3. Rule 1 takes every observed
pattern, so the NiFeOOH candidates are now:
- C1: Fe +, Ni 5/29/30 -
- C2: Fe -, all Ni +
- C3: Fe +, Ni 5/29 -
- C4: Fe +, Ni 30 -

Each converged Ni(Fe)OOH relaxation gets C1-C4 single points (`make_cfg_sp.sh`, `post_relax.sh`
v3; the readout labels C4). No relaxation had converged, and no single point had been queued.

## Amendment 10 (2026-11-16 04:00Z, before any eta existed)
Noise floor. Some SCFs stall just above 5e-6 Ry with their energy fixed. `u0__NiOOH__Ni0_OOH` step
8 ran about 190 iterations at 5.3-8e-6 Ry. Its rerun at the same geometry, from that density, sat at
5.1-6.2e-6 Ry with the energy constant to 0.003 mRy. Amendment 6 met the same behaviour (5.06-5.18e-6
for 200 iterations) and set 1e-5 for that rerun. Here:
- An SCF whose last 30 iterations all lie below 1e-5 Ry is at the noise floor. Its rerun (amendment-9
  rerun rule) uses conv_thr 1e-5 Ry and changes nothing else. `post_relax.sh` v3 applies this
  automatically. `u0__NiOOH__Ni0_OOH_r3` was started by hand at 04:00Z: r2's input and geometry
  with conv_thr 1e-5, from the same density.
- The C1-C4 single points use conv_thr 1e-5. They only need to resolve the 1 mRy reproduction
  tolerance and the sub-meV-to-10s-of-meV gaps between configurations.

The cost is at most ~1e-5 Ry (0.14 meV) per energy, under 1% of the 1 mRy tolerance and far below any
eta resolution this pilot claims. Relaxation thresholds (forc_conv_thr 2e-3, upscale 1) are
unchanged.

Rerun checks (04:11Z):
- `u0__NiOOH__slab_r2`'s first energy is -5132.42380 Ry, 2.57 mRy below `u0__NiOOH__slab`'s last.
  `u0__NiOOH__Ni0_OOH_r3`'s is -5216.66508 Ry, 3.19 mRy below `u0__NiOOH__Ni0_OOH`'s last.
  Both started at their predecessor's last geometry, so both replace it.
- `slab_r2` came out with Ni29 -0.30 and Ni5 -0.17 muB, and every other Ni is +0.42 to +0.89.
  Ni29 is past the rule-1 cutoff of |m| >= 0.25, so the NiOOH slab is no longer all-parallel at this
  step. `Ni0_OOH_r3` is all-parallel (site Ni6 +0.04, below the cutoff).
- Open: if a converged NiOOH state keeps a non-parallel pattern, the NiOOH states need the same
  multi-pattern single points so that "lowest" is taken the same way on both sides of V1. This is
  to be settled when the NiOOH relaxations converge, before any eta exists.

## Compute
- 83 Sciences AWS account (Frank, 2026-11-14), c7a.48xlarge (192 cores, 384 GiB), on-demand,
  us-east-1; 6 jobs x 30 ranks (-nk 3); gas jobs 8 ranks. Box scripts: `src/dft/film_box/`.
- Cost estimate before launch: ~8,000-13,000 core-hours (~42-68 instance-hours), uncertain by ~2x;
  the first hour's SCF timing is used to re-estimate. Hard cap 48 h (box stops itself).
- Production is intended for Anvil (CHE260157 supplement request, `access-supplement-request-2026-11-14.md`).
