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

## Amendment 11 (2026-11-16 08:32Z, before any eta existed)
First converged relaxation and its single points:
- `u0__NiFeOOH__slab` converged at 06:09Z: 54 steps, -5118.50258 Ry. It ended in C1 (Fe +2.56;
  Ni5 -1.11, Ni29 -0.72, Ni30 -1.11; Ni28 +0.15, below the cutoff).
- C1, the slab's own configuration: -5118.50258 Ry, 0.0004 mRy from the relaxed energy, with
  pattern C1 kept (no metal moved by more than 0.01 muB). Rule 2's reproduction check passes. It
  was a cold start: 62 iterations, 66 min on 24 ranks.
- C2 left its target. It converged in 66 iterations with Fe -2.60 and Ni30 -1.18, every other Ni
  +0.25 to +1.08 (Ni5 +1.08, Ni29 +0.70). Its energy is -5118.49729 Ry, 5.29 mRy above C1. Fe and
  Ni30 are both antiparallel to the rest, which is none of C1-C4.
- Running relaxations at 08:27Z: Fe0_O step 27 in C2 (Fe -1.56, every Ni +); Fe0_OH_r4 step 13 in
  C4; Fe0_OOH step 32 in C3 (Ni29 -0.27, close to the cutoff).

Rule changes:
1. A trusted single point counts as the configuration it lands in. Rule 2's exclusion still stops
   a point that left its target from standing in for that target. Its energy is a converged SCF of
   the state at its relaxed geometry, so it bounds the landed configuration's relaxed energy from
   above, the same bound rule 3 relies on. Targets and landed patterns are both reported. The
   own-configuration check still needs target = landed = the state's configuration.
2. C5 = Fe -, Ni 30 - joins the Ni(Fe)OOH candidates (rule 1 as applied for C4: every observed
   pattern). Every converged Ni(Fe)OOH relaxation gets a C5 single point (`make_cfg_sp.sh`,
   `post_relax.sh` v4, `deploy_pr4.sh`; dry-run on the slab and the three running Fe-site states).
   The slab's C2 point stands as its C5 point, so the slab gets no separate C5 run.
3. Closure. A pattern first seen in a single point after this amendment counts for the state it
   landed in (by 1) and is reported. It adds no single points for the other states. A pattern
   that a relaxation's SCF enters still adds a candidate, as C4 did. This keeps the single-point
   set finite under the cap.

Reason: C5 is a stable SCF solution of the clean slab, one Ni flip away from C2, the configuration
Fe-site *O is relaxing in. It is a plausible lower configuration for the Fe-site states, so leaving
it out could bias "lowest" upward. The cost is three more cold single points, about 66 min on 24
ranks each. "As relaxed" (rule 4) is unchanged, so this can move only the "lowest" readout, and V1
has to pass both. `film_pilot_readout.py` labels C5 and counts each single point by where it
landed.

Slab single points complete (10:34Z). C3 (Fe +, Ni 5/29 -) and C4 (Fe +, Ni 30 -) both left their
targets and converged to C1, at -5118.50258168 and -5118.50258140 Ry (59 and 63 iterations). Both
are within 0.0004 mRy of the C1 point, and no metal is more than 0.02 muB from it. At the slab's
geometry, three of the four starts end in C1 and the C2 start ends in C5, 5.29 mRy higher. The
slab's lowest energy is its relaxed C1 energy.

NiOOH Ni-site *O (`u0__NiOOH__Ni0_O_r2`) converged at 10:22Z: 43 steps, -5173.86502 Ry, all
parallel (site Ni6 +1.16; Ni5 -0.01, below the cutoff). The *O stays atop Ni6, with d(Ni6-O) going
from 1.83 to 1.65 A. At their 10:24Z steps the other NiOOH states are all parallel under the
cutoff too, and the slab's Ni29 moment has gone from -0.30 to -0.10.

V1 before V2, automated (10:39Z, `post_relax.sh` v5, `deploy_pr5.sh`). With no V1 run waiting, the
two freed slots went to `u0__CoOOH__slab` (10:23Z) and `u0__CoOOH__Co0_O` (10:34Z). Each Fe-site
state queues five single points as soon as it converges. Now, when a V1 run is waiting and no
cores are free, `post_relax.sh` stops the most recently started CoOOH run. As `yield_co.sh` did by
hand at 01:03Z, it moves that run's dir to `runs_stopped/` so it relaunches from `co_queue.txt` (a
fresh start), and logs YIELD. It does this only while at least 75 min remain before the deadline
guard stops every run, so the single point (~66 min) can finish, and at most once per 5 min. It
was sandbox-tested with stand-in processes:
- V1 waiting with 3 h left: yields the later-started run;
- 60 min left: no yield;
- nothing waiting: no yield.

NiOOH clean slab (`u0__NiOOH__slab_r2`) converged at 12:17Z: 38 steps, -5132.43330 Ry, all parallel
(Ni5 and Ni29 -0.12, below the cutoff). At 12:18Z, Ni0_OH (step 48) and Ni0_OOH_r3 (step 50) were
also all parallel. If they end that way, every NiOOH state is all parallel, and NiOOH needs no
multi-pattern single points.

Hand-off at the deadline. `out.tgz` excludes `*/tmp`, so it carries no densities. The guard kills
each job shell before its pw.x, so `run_side.sh` never deletes tmp/, and the last-step densities of
the stopped runs survive. `density_pull.sh` waits for DEADLINE_HIT, then copies the U = 0 save
dirs (charge density, occup.txt, paw.txt, schema; about 1 GB with `keep/`) to
`D:/sts-electrocatalyst/film_pilot/out/densities` with an md5 check. That way any continuation can
restart from the last geometry with startingpot = 'file'. The script never touches PULLED, so it
cannot delay the box's release. Tested on one 86 MB density: 25 s end to end.

V2 note (12:48Z). `u0__CoOOH__slab`, a cold start (Co 0.05; local-TF, beta 0.05, ndim 20), finished
no SCF. It reached about 1e-2 Ry by iteration 40, then sat at 5e-3 to 1e-2 Ry through iteration
200, with the energy within 0.4 mRy and the total moment at -0.24 to -0.26 muB. No step finished,
so no density was kept, and `post_relax.sh` gave up the automatic rerun. Its slot went to
`u0__CoOOH__Co0_OOH`. Low-spin Co(III) is near nonmagnetic, so this looks like charge sloshing
rather than the slow magnetic modes behind the Ni(Fe)OOH stalls. A V2 continuation needs a
different SCF start for this slab, decided before any V2 eta exists.

Spend (13:10Z). Frank extended the cap from 14:00Z to 2026-11-16T22:00Z: +8 instance-hours, ~$79,
~45 instance-hours / ~$441 in all. The estimate for a complete V1 was 19:00-21:00Z (three Fe-site
relaxations still running, then five single points each). When V1's last run finishes, the
deadline is brought forward so the box stops. V2 continues off AWS, since its relaxations cannot
finish by 22:00Z.

`u0__NiOOH__Ni0_OOH_r3` is stuck (diagnosed 13:15-13:25Z). Its BFGS repeats a 4-step cycle with
energies -5216.66506, -.66453, -.66410, -.66392 Ry (steps 50-53, again at 54-57). Steps 50 and 54
agree to 1e-8 Ry. In each cycle the trust radius shrinks from 0.012 to 0.0003 bohr while the
energy stays up to 1.14 mRy above the cycle's lowest, and then the BFGS history resets (13 resets
so far). Every SCF converges cleanly (7-13 iterations, with identical total/absolute moments
10.95/11.44 muB and the Ni moments unchanged). The largest free force is 0.017-0.020 Ry/bohr on
O49, and the total force has been 0.035-0.038 since step 19. pw.x warned 54 times that the SCF
correction is large compared to the forces: the total SCF correction is 0.011-0.022 against a
total force of 0.035. Reading: at conv_thr 1e-5 (amendment 10), the forces and energies at this
geometry are too noisy for BFGS's energy-based line search. Shrinking steps hit apparent energy
differences of about 1 mRy that no 0.0003-bohr displacement can produce, so the run cannot reach
forc_conv_thr 2e-3. It needs a rerun from its lowest-energy geometry, with a cleaner SCF or a
force-only optimizer. The rerun waits on SSH access: from about 13:25Z the box stopped answering
on port 22, most likely because this machine's public IP changed (the security group admits only
the launch IP). The runs on the box continue on their own.

The other slow runs, by largest free force component (Ry/bohr) at 13:15Z:
- Fe0_O 0.0029-0.0037, -0.15 mRy/step;
- Fe0_OOH 0.0024-0.0051;
- Ni0_OH 0.0026-0.0037;
- Fe0_OH_r4 0.005-0.008, -0.4 to -0.9 mRy/step. Its adsorbed OH is reorienting (H50 0.39 A, O49
  0.30 A over 8 steps; d(Fe6-O49) 1.76 A, intact).

SSH access came back at 13:49Z after Frank's SSO login. The security group had admitted only the
launch IP (68.45.14.207/32), and this machine is now 168.102.134.128/32, which was added. The
instance had kept running throughout. `u0__NiOOH__Ni0_OH` converged at 13:45Z (55 steps).

## Amendment 12 (2026-11-16 13:53Z, before any eta existed)
Ni0_OOH reruns (`src/dft/film_box/amend12_ni0ooh.sh`). `u0__NiOOH__Ni0_OOH_r3` was stopped after 59
steps; its last energy was -5216.66453 Ry. Two reruns run side by side from its last printed
geometry (to 5e-9 A) and its last-step density (startingpot = 'file'):
- `_r4`: BFGS, conv_thr 5e-6 (the registered value; amendment 10's 1e-5 is what made its forces too
  noisy). The SCF mixing is mixing_beta 0.05 and mixing_ndim 20 (from 0.1 and 12), aimed at the
  5.1-8e-6 floor that stalled Ni0_OOH at step 8. These are SCF numerics only.
- `_r5`: FIRE (ion_dynamics = 'fire', pw.x 7.5), with r3's SCF settings (conv_thr 1e-5). FIRE steps
  on forces alone, so the energy noise that defeats BFGS's line search does not stop it.

Model, cutoffs, smearing, dipole correction, forc_conv_thr 2e-3 and etot_conv_thr are unchanged
in both. Rules:
- The first to converge stands, and the other is stopped then and reported.
- Each replaces r3 under the amendment-9 rerun rule (r3's last geometry; first energy within
  1 mRy of r3's last).
- Neither gets an automatic `post_relax.sh` rerun.

Code:
- `qe_qc.py` accepts FIRE's convergence line ("FIRE: convergence achieved in N steps") as a
  converged relaxation. Its "Final energy = ... Ry" already matched. Tested on synthetic converged,
  nstep-limited and unconverged outputs; `tests/test_qe_qc.py` and `tests/test_adsorbate_qc.py`
  pass (22).
- `film_pilot_readout.py`'s rerun chain, for runs that did not start from each other's last
  geometry, prefers a converged relaxation and otherwise takes the lower last energy.

First SCFs (14:16Z):
- `_r5`'s first energy is -5216.66409753 Ry, 0.43 mRy above r3's last, so it replaces r3. FIRE is
  running with its defaults (dt 20 a.u.). Total force 0.0365, SCF correction 0.0131.
- `_r4`'s first SCF reached 6.95e-6 Ry at iteration 17 and then sat at 7.0-7.9e-6 against 5e-6,
  with the energy constant to 0.2 microRy. `floorwatch_r4.sh` (on the box) checks each of r4's
  SCFs in turn, and stops r4 when the SCF in progress meets amendment 10's noise-floor test (its
  last 30 iterations all < 1e-5 Ry, not converged). Such an SCF would otherwise fail at
  electron_maxstep with no automatic rerun. After that, r5 alone carries Ni0_OOH.

At 14:27Z:
- r4's first SCF converged after all (25 iterations): -5216.66410077 Ry, 0.43 mRy above r3's last,
  so it too replaces r3. Its SCF correction is 0.0052 against r5's 0.0131 and r3's 0.011-0.022, so
  the forces are cleaner at 5e-6.
- r5 (FIRE) steps 1-3 run -5216.66409753, -.66464868, -.66562707 Ry. Step 3 is already 0.55 mRy
  below the lowest energy r3 reached in 59 steps.

## Fe-site *OOH converged; candidate C6 (2026-11-16 16:24Z, rule 1, before any eta existed)
`u0__NiFeOOH__Fe0_OOH` converged at 16:18Z: 69 steps, -5202.82157378 Ry, conv_thr 5e-6, total
force 0.0069 at the last step.
- Moments at the last step: Fe6 +1.38, Ni5 -0.84, Ni29 -0.19, Ni30 +0.25. Every other Ni is +0.72
  to +0.97, except Ni4 at +0.16 (below the cutoff).
- Ni29 was -0.27 at step 32 (C3 then), -0.23 at step 40, and -0.18 to -0.21 from step 50 on.
- Under rule 1's 0.25 muB cutoff, the state ended in Fe +, Ni 5 -. That is none of C1-C5: C3 needs
  Ni29 antiparallel too.
- *OOH is intact at the final geometry: O49-O50 1.387 A, O50-H 1.006 A, Fe6-O49 1.816 A. The H
  hydrogen-bonds to lattice O48 at 1.75 A. The readout's adsorbate QC applies after the pull.

C6 = Fe +, Ni 5 - joins the Ni(Fe)OOH candidates (rule 1). Every converged Ni(Fe)OOH state gets a
C6 single point:
- Fe0_OOH, where C6 is the own-configuration check: target = landed = C6, within 1 mRy of
  -5202.82157 Ry;
- the clean slab;
- Fe0_O and Fe0_OH_r4, with their C1-C5 points, when they converge.

Fe0_OOH's C3 and C6 inputs differ only in atom 29's starting sign. C3 starts it negative, so at
this geometry it may land in the relaxed solution, which counts as C6 under amendment 11 rule 1.
C6 starts it positive. Targets and landed patterns are both reported.

Code (`src/dft/film_box/deploy_pr6.sh`, deployed 16:24:50Z):
- `make_cfg_sp.sh` encodes C6 by returning atoms 29 and 30 to species Ni, so only Ni5 carries the
  negative start. Its default is now C1-C6.
- `post_relax.sh` v6 queues C1-C6 for each relaxation that converges.
- `film_pilot_readout.py` labels C6.
- Dry run first: C6 for Fe0_OOH and the slab, plus C1-C6 for the running Fe0_O and Fe0_OH_r4
  (FORCE=1). Each input encodes its target. C6 differs from the queued C3 input only in atom 29's
  species.
- C6 for Fe0_OOH and for the slab were appended to `cfg_queue.txt`.

The cost is four more cold single points (~66 min on 24 ranks each), inside the 22:00Z cap.
`post_relax.sh` stopped `u0__CoOOH__Co0_OOH` (16:20Z, step 10) and `u0__CoOOH__Co0_OH` (16:24Z,
step 6) for Fe0_OOH's C2 and C3. They restart fresh from `co_queue.txt` only if cores free up
before the deadline.

Running at 16:25Z:
- Fe0_O: step 42, C2.
- Fe0_OH_r4: step 40, C4.
- Ni0_OOH r4: step 9, BFGS.
- Ni0_OOH r5: step 11, FIRE, total force 0.030.
- Fe0_OOH single points C1-C3.

## Amendment 13 (2026-11-16 16:35Z, before any eta existed)
`u0__NiFeOOH__Fe0_O` has run since its launch (2026-11-15 19:03Z) without amendment 4's
`upscale = 1.d0`. Every other Ni(Fe)OOH and NiOOH U = 0 relaxation has it. The four CoOOH U = 0
inputs lack it too.
- pw.x's default upscale (100) tightened its SCF target from 5e-6 to 7e-8 to 1.3e-7 Ry as forces
  shrank.
- Each step then took 20-32 SCF iterations, about 60 s each. Fe0_OH_r4 takes 11-21 iterations at
  5e-6, and Ni0_OOH r4 and r5 take 8-19.
- Its step-43 SCF began after a BFGS step with trust radius 0.127 bohr, which followed a failed
  curvature check. It did not converge: after 54 iterations the accuracy still wandered between
  3e-4 and 2e-2 Ry, the total moment between 6.0 and 7.2 muB, and the energy between -5160.0288
  and -5160.0307 Ry.
- At ~60 s per iteration, reaching electron_maxstep (200) would have used about 2.5 more hours of
  the slot before the automatic rerun.

It was stopped after 42 completed steps (last E -5160.02948414 Ry; the last moments are C2). The
rerun `u0__NiFeOOH__Fe0_O_r2` (`src/dft/film_box/amend13_fe0o.sh`) starts from its last printed
geometry (to 5e-9 A) and its kept step-42 density (startingpot = 'file'). It differs from the
original in:
- `upscale = 1.d0`, so conv_thr stays at the registered 5e-6 (amendment 4);
- mixing_beta 0.05 and mixing_ndim 20, SCF numerics as in amendment 12's r4, to damp the moment
  oscillation.

The model, cutoffs, smearing, dipole correction and forc_conv_thr 2e-3 are unchanged.
- Amendment-9 rerun rule: r2 replaces Fe0_O if its first energy is at most 1 mRy above
  -5160.02948 Ry.
- r2 is in `cfg_watch.txt` (C1-C6 single points when it converges) and `rescue_watch.txt`
  (automatic rerun if an SCF fails).
- It was put at the top of `cfg_queue.txt` with its density staged, and `post_relax.sh` launched
  it into the freed slot at 16:35:50Z.
- The forces of Fe0_O's first 42 steps came from SCFs converged tighter than registered. Their
  accuracy is better, not worse, so they stand.
- CoOOH (V2): `upscale = 1.d0` was added at 16:40Z to the Co0_O, Co0_OH and Co0_OOH inputs, which
  relaunch from `co_queue.txt` if cores free up. `u0__CoOOH__slab` keeps its failed run dir and
  does not relaunch; its continuation needs a new SCF start anyway (12:48Z note) and adds upscale
  then.

## First single point at Fe0_OOH; Fe0_O_r2's first step (2026-11-16 17:50Z, before any eta existed)
`C2__u0__NiFeOOH__Fe0_OOH` finished at 17:44Z: one SCF, 5023 s, -5202.82269956 Ry, total force
0.0099.
- Landed moments: Fe6 -1.37, Ni30 -0.23, Ni29 +0.23, Ni4 +0.23, Ni5 +0.82. Every other Ni is +0.77
  to +0.96.
- Under the 0.25 muB cutoff that is Fe -, no Ni antiparallel: C2, so target = landed. Ni30 sits
  0.02 muB under the cutoff. At -0.25 or beyond it would read C5, so the label is close to the
  cutoff.
- It is 1.13 mRy (15 meV) below the relaxed C6 state (-5202.82157378 Ry). The readout takes each
  state in the lowest of its relaxed energy and its counted single points, so C2 is Fe0_OOH's
  energy so far. C1 and C3-C6 are still running or queued.
- Uncertainty: the single point uses the geometry relaxed in C6. A C2 relaxation could go lower, by
  an amount this pilot does not measure. Rule 1 asks only for single points.

`u0__NiFeOOH__Fe0_O_r2` finished its first SCF: -5160.03558531 Ry, total force 0.0197, total
moment 5.94 muB.
- Amendment-9 rerun rule: that is 6.10 mRy below Fe0_O's last (-5160.02948414 Ry), far inside the
  1 mRy-above limit. r2 replaces Fe0_O.
- The geometry is the same to 5e-9 A, but the magnetic state is not. Ni30 went from +0.29 to -0.46
  and Fe6 from -1.63 to -1.58, while Ni5 (+0.68) and Ni29 (+0.21) stayed. Fe -, Ni30 - is C5, the
  pattern the clean slab's C2 single point also landed in (amendment 11).
- The 6 mRy cannot come from the looser SCF threshold: at conv_thr 5e-6 the energy error is in the
  micro-Ry range. It means Fe0_O's C2 state was metastable at this geometry. Its non-converging
  step-43 SCF, with the total moment wandering 6.0-7.2 muB, was already moving between the two.
- Its C1-C6 single points follow when r2 converges, as for every Ni(Fe)OOH state.

Ni0_OOH at 17:48Z: r4 (BFGS) is at step 12, -5216.68559957 Ry, F 0.030. r5 (FIRE) is at step 20,
-5216.68332519 Ry, F 0.014. Both are all parallel, with Ni6 at +0.04.
- r5 is nearer the force threshold, but r4 is 2.27 mRy (31 meV) lower.
- The registered rule (amendment 12) stands: the first to converge is used. If that is r5 and it
  ends above r4's last energy, both are reported. The gap then bounds how much the Ni0_OOH energy
  depends on the optimizer path.

Fe0_OH_r4 at 17:48Z: step 45, -5161.31207972 Ry, F 0.020, C4 (Fe6 +1.49, Ni30 -0.32).

Fe0_OOH single points C1 and C3 (17:50Z and 18:02Z):
- C1 left its target: -5202.81930116 Ry, with Fe6 -1.32, Ni5 -0.68, Ni29 +0.18, Ni30 -0.17. That
  is Fe -, Ni 5 -, a pattern first seen here. Under amendment 11 rule 3 (closure), it counts for
  Fe0_OOH, where it is 2.27 mRy above the relaxed state, and is reported. It adds no candidate and
  no single points for the other states.
- C3 left its target and landed in C6, the relaxed solution, as expected above: -5202.82156818 Ry,
  0.006 mRy from the relaxed energy. Fe6 +1.38, Ni5 -0.84, Ni29 -0.18; the moments match the
  relaxed ones to 0.01 muB. The own-configuration check is still the C6 point, since it needs
  target = landed.
- Fe0_OOH so far: C2 lowest (-5202.82269956), C6 relaxed and C3 within 0.006 mRy of it, C1 2.27 mRy
  above. C4, C5 and C6 are running.

## Amendment 14 (2026-11-16 18:15Z, before any eta existed)
`u0__NiFeOOH__Fe0_OH_r4`'s step-46 SCF has the symptom amendment 13 stopped in Fe0_O.
- It follows BFGS steps with a growing trust radius: 0.043, 0.094, then 0.141 bohr.
- It reached 5.4e-5 Ry at iteration 22. Over the next 20 iterations it drifted back to 3e-4 to
  1e-3 Ry, with the total moment wandering 11.0-11.2 muB. Its previous 8 steps took 10-17
  iterations each.
- Unlike Fe0_O, its settings are the registered ones: conv_thr 5e-6, upscale 1, beta 0.1, ndim 12.
- The registered automatic rerun fires only at electron_maxstep (200), about 2.5 h away at ~1 min
  per iteration. That would use nearly all the time left before the 22:00Z deadline.

Rule (`src/dft/film_box/amend14_fe0oh.sh`, a box-side watcher, armed 18:15:06Z):
- If any SCF of r4 reaches 60 iterations without converging, r4 is stopped. Fe0_O was stopped at
  54.
- It is rerun as `u0__NiFeOOH__Fe0_OH_r5` (amendment-9 rerun rule) from its last printed geometry
  and its kept density. The density is the last converged SCF, now step 45: written 17:27:10, at
  its '!' at ~17:27:07Z.
- The rerun uses mixing_beta 0.05 and mixing_ndim 20, the SCF numerics of amendment 12's r4 and
  amendment 13's r2.
- The model, cutoffs, smearing, dipole correction, conv_thr 5e-6, upscale 1 and forc_conv_thr
  2e-3 are unchanged.
- If the SCF recovers, or r4 converges, nothing happens.
- r5 replaces r4 if its first energy is at most 1 mRy above r4's last.
- r5 is in `cfg_watch.txt` and `rescue_watch.txt`, and it goes to the top of `cfg_queue.txt`.
- The 60-iteration threshold is a judgment. It gives the SCF about 15 more minutes to recover,
  since Broyden mixing sometimes does, and bounds the loss at that.
- Cost: a rerun loses r4's BFGS history, so the first steps of r5 are slower.

Dry run (18:14Z): r5's input differs from r4's only in prefix, mixing_beta and mixing_ndim (r4
already had startingpot = 'file' and upscale 1). Positions match r4's last printed geometry to
4.9e-9 A.

The rule fired at ~18:28Z: the step-46 SCF reached 60 iterations with its last 10 accuracies at
2.4e-4 to 6.1e-4 Ry, never back under the 5.4e-5 of iteration 22. r4 was stopped after 45 completed
steps (last E -5161.31207972 Ry, F 0.020, C4). `u0__NiFeOOH__Fe0_OH_r5` launched at 18:28:27Z on
24 ranks and read its starting density from file.

Ni0_OOH_r4's amendment-12 noise-floor watcher reached its registered 4 h limit at 18:17:36Z
without firing. Its step-14 SCF was still improving then (30 iterations, 1.5e-5 to 5e-6 Ry,
energy -5216.68849 Ry, 2.9 mRy below its step 13). If an SCF of r4 now stalls, r4 fails at
electron_maxstep with no rerun and r5 carries Ni0_OOH, the outcome the watcher would have given.
It holds its 24-rank slot longer, which costs nothing while no run waits for a slot.

## Single points, 19:10-19:14Z (before any eta existed)
`C5__u0__NiFeOOH__Fe0_OOH` left its target: -5202.80568566 Ry, 76 iterations, force 0.031 at the
fixed geometry.
- Moments: Fe6 -0.49, Ni30 -0.22, Ni29 +0.21, Ni4 +0.22, every other Ni +0.75 to +0.96.
- Under the 0.25 muB cutoff that is Fe -, no Ni antiparallel: C2.
- It is not the C2 point's solution, though. Fe is at -0.49 against -1.37 there, and the energy is
  17.0 mRy higher. The pattern labels record only signs, so two solutions 17 mRy apart share a
  label.
- The readout takes the lowest counted energy, so Fe0_OOH's value is unchanged (the C2 point,
  -5202.82269956 Ry). Both points are reported.

`C6__u0__NiFeOOH__slab` left its target and landed in C1: Fe6 +2.56, Ni5 -1.13, Ni29 -0.72,
Ni30 -1.11. Energy -5118.50258004 Ry, 0.002 mRy from the relaxed energy; no metal is more than
0.02 muB from it.
- The slab's set is now complete. C1, C3, C4 and C6 all end in C1. C2 ends in C5, 5.29 mRy
  higher, and stands as the slab's C5 point (amendment 11).
- The slab's lowest is its relaxed C1 energy.

Still running for Fe0_OOH at 19:18Z:
- C6, the own-configuration check: 78 iterations, 3.9e-5 Ry.
- C4: 162 iterations, 2e-3 to 2e-2 Ry. It may reach electron_maxstep (200), and then it does not
  count.

`C6__u0__NiFeOOH__Fe0_OOH` finished at 19:23Z (81 iterations) and left its target.
- Fe started at +0.3 and ended at -1.33. The point landed at Fe6 -1.33, Ni5 -0.68, Ni29 +0.19,
  Ni30 -0.17: Fe -, Ni 5 -.
- This is the C1 point's solution: -5202.81929921 Ry against -5202.81930116 Ry, with the moments
  within 0.01 muB. It is 2.27 mRy above the relaxed energy.
- **Fe0_OOH's own-configuration check (rule 2) is therefore not met.** No single point has
  target = landed = C6. Rule 2 tests the procedure, a cold start at the fixed relaxed geometry.
- The C3 point is the evidence available on that question. It started with Fe + and Ni5 and Ni29
  negative, and it landed in C6, the relaxed solution. Its energy reproduces the relaxed one to
  0.006 mRy, with the moments within 0.01 muB.
- The cold-start procedure reproduces the relaxed state when it lands there. But the C6 start,
  which differs from C3's only in Ni29's starting sign, went elsewhere.
- Both are reported. Rule 2 as registered stays unmet for Fe0_OOH, and no further point is added.
- `film_pilot_readout.py` still reports rule 2's check as defined: None for Fe0_OOH. It also
  reports, for the record only, every counted point that landed in the state's own configuration
  whatever its target (`own_config_landed_mry`; Fe0_OOH: C3 0.006 mRy).

Fe0_OOH points, 5 of 6 done (C4 still running):

| Target | Landed | E (Ry) | vs relaxed (mRy) |
|---|---|---|---|
| C1 | Fe -, Ni 5 - (closure) | -5202.81930116 | +2.27 |
| C2 | C2 (Fe -1.37) | -5202.82269956 | -1.13 (lowest) |
| C3 | C6 | -5202.82156818 | +0.006 |
| C5 | C2 (Fe -0.49) | -5202.80568566 | +15.89 |
| C6 | Fe -, Ni 5 - (closure) | -5202.81929921 | +2.27 |

Fe0_OH_r5's first SCF at 19:34Z: 62 iterations in 66 min, not converged.
- It fell to 8e-4 Ry by iteration 24. It then oscillated between 6e-4 and 2.5e-3 Ry to iteration
  54, and has fallen slowly since: 3.3e-4 to 1.6e-4 Ry over iterations 55-62.
- The total moment moved between 10.92 and 11.28 muB. The SCF energy has stayed between
  -5161.3126 and -5161.3133 Ry, 0.6-1.3 mRy below r4's last energy.
- At this geometry, r4's beta 0.1 / ndim 12 SCF and r5's beta 0.05 / ndim 20 SCF both wander. That
  points to the geometry rather than the mixing: two or more magnetic solutions within about
  1 mRy, which the SCF moves between.
- Ni30, at -0.32 muB in C4 and close to the 0.25 cutoff, is the likely soft moment. Site moments
  print only at SCF end, so this is not yet checked.
- If so, which of these solutions the state settles in moves its energy by about 1 mRy (14 meV).
  That is an inference, reported as one.

No intervention. Fe0_OH could not converge, and get its single points, before the 22:00Z deadline
under any option: at -0.6 mRy and 16 min per step, plus ~85 min of single points. A rerun from
step 45's converged geometry would head back into the same region. r5 runs on.
- The end-of-run pull copies all of `keep/`, including r4's step-45 density (17:27:10).
- Any continuation can start from r5's first converged step if one exists, or from r4's step 45.

Freed slots went to `co_queue.txt`: `u0__CoOOH__Co0_O` (19:11Z) and `u0__CoOOH__Co0_OH` (19:14Z)
restarted fresh, with upscale 1 (amendment 13).

`C4__u0__NiFeOOH__Fe0_OOH` reached electron_maxstep (200) at 19:59Z without converging. It does
not count (rule 2), so Fe0_OOH has 5 of its 6 points. Lowest: C2, -5202.82269956 Ry.

## Amendment 15 (2026-11-16 20:13Z; V2, before any V2 eta exists)
Since C4 ended, one 24-rank slot is idle until the 22:00Z deadline, with no V1 run waiting. The
12:48Z V2 note left the clean CoOOH slab needing a different SCF start.
- Its cold SCF held the energy steady to 0.4 mRy and the total moment at -0.20 to -0.26 muB.
- It never got below 5e-3 Ry over iterations 40-200.
- A steady energy with a residual that will not fall is the usual sign of fractional occupations
  flipping near the Fermi level. Larger smearing damps that.

Test (`src/dft/film_box/amend15_coslab.sh`): `u0__CoOOH__slab_smear3` is the slab's input with
`calculation = 'scf'` and MV smearing 0.03 Ry (registered: 0.01).
- Numerics only. Its density is a starting density for the slab's registered relaxation
  (startingpot = 'file', degauss 0.01). Its energy enters nothing.
- Nothing else changes: positions, k-points, cutoffs, spin, dipole correction, conv_thr 5e-6,
  local-TF, beta 0.05, ndim 20.
- Its outdir is in `scratch/`, so run_side.sh's removal of the run's tmp/ cannot delete the
  density. A waiter (box pid 261287) copies the density into `keep/`, which the deadline pull
  includes, if the SCF converged.
- It goes to the top of `co_queue.txt`. `post_relax.sh` launches it, and `yield_co` stops it first
  if V1 work waits for cores.
- A converged SCF answers whether this start works, and the registered relaxation can begin from
  it wherever V2 continues. If it does not converge by 22:00Z, the SCF trace is reported.
- Dry run (20:12Z): the input differs from the slab's only in calculation, prefix, outdir and
  degauss, plus the removed &IONS namelist. Positions and k-points are identical.
- Order: it was queued at 20:13Z and launched at 20:13:54Z. This text was committed shortly after
  (the first commit carried only the script). Its first iteration was the only output then.

Spend (20:20Z). Frank extended the cap from 22:00Z to 2026-11-17T06:00Z ("a, extend to 06:00Z"):
+8 instance-hours, ~$79, about 53 instance-hours / ~$520 in all.
- The V1 estimate at 16:38Z was 23:00Z to 05:00Z: Fe0_O_r2, Fe0_OH (now r5) and Ni0_OOH still
  relaxing, then six single points (about 85 min each) for each Fe-site state.
- DEADLINE becomes 1794895200 (06:00Z). The OS shutdown moves from 01:10Z to 07:10Z, so a hard
  stop stays in place if every guard fails.
- When V1's last run finishes, the deadline is brought forward so the box stops then.
- V2 continues off AWS.

Automation for that step (`src/dft/film_box/v1done.sh`, a box-side watcher polling every 60 s).
V1 counts as done when, for 5 consecutive minutes:
- no NiOOH or Ni(Fe)OOH pw.x job runs, single points included;
- `cfg_queue.txt` has no unlaunched entry;
- every relaxation in `cfg_watch.txt` carries CFG_QUEUED or CFG_SKIPPED, so `post_relax.sh` has
  queued or skipped its single points.

The 5 minutes cover `post_relax.sh`'s 30 s cycle between a relaxation converging and its single
points being queued. When V1 is done, DEADLINE is set to now, and the registered sequence follows:
- every run stops, the CoOOH (V2) runs included;
- the outputs are packaged, pulled, and the instance terminated;
- `keep/` is copied.

The same watcher applies amendment 12's rule that the first Ni0_OOH run to converge stands. When
r4 or r5 converges, the other is stopped (RESCUE_HANDLED first, so no rerun follows), and both
last energies are logged.

Dry run (20:19Z): it lists the four running V1 relaxations, leaves out the four CoOOH runs, and
reports Fe0_O_r2 and Fe0_OH_r5 as not yet handled. In a test work dir, an unlaunched single point
and an unhandled relaxation each block "done".

The SSO access token for the final terminate expired at 18:35Z, and the cached role credentials
expire at 21:35Z. If the pull loop cannot terminate the instance at the end, the box stops itself
after the pull (shutdown behavior STOP). It then bills only its disk until it is terminated by
hand after the next `aws sso login`.

## Amendment 16 (2026-11-16 20:30Z, before any eta existed)
`u0__NiFeOOH__Fe0_OH_r5` (amendment 14) had not finished its first SCF at r4's step-46 trial
geometry after 117 iterations (19:26Z to 20:26Z).
- From iteration ~60 its accuracy sat at 3e-5 to 2e-4 Ry, and from iteration 99 at 2.9e-5 to
  7.7e-5, with no downward trend.
- Its energy stayed at -5161.31267 to -5161.31277 Ry, fixed to 0.1 mRy, and its total moment at
  10.98 to 11.07 muB.
- This floor is 3-20x above conv_thr 5e-6. Amendment 10's noise-floor rule (last 30 iterations
  below 1e-5, then conv_thr 1e-5) does not cover it.
- Relaxing conv_thr this far would touch force accuracy, not only the energy.
- At electron_maxstep (200), about 80 min on, the automatic rerun would repeat the same SCF at the
  same geometry with the same numerics.

At the step-46 trial geometry, r4's SCF (beta 0.1, ndim 12) and r5's (beta 0.05, ndim 20) both
fail to settle. r4's SCF at step 45's geometry converged in 13 iterations. Both failing SCFs
started from a density at a geometry 0.065 A away (trust radius 0.141 bohr).
- The difficulty is local to that region of geometry. A soft magnetic mode is the likely cause, an
  inference.
- Fe0_OH is V1's critical path to the 06:00Z deadline.

Rule: `u0__NiFeOOH__Fe0_OH_r6` (`src/dft/film_box/amend16_fe0oh.sh`) restarts from r4's step-45
geometry (block 44 of its output, matched to 5e-9 A). It uses that step's density (`keep/`,
written 17:27:10 at its '!' at ~17:27:07Z), with:
- ion_dynamics = 'fire', as amendment 12's Ni0_OOH_r5, which has converged steadily. FIRE's small
  steps let each SCF start from a density at a nearby geometry, so the magnetic state can be
  followed instead of jumped into.
- mixing_beta 0.05 and mixing_ndim 20, as r5.
- conv_thr 5e-6 and upscale 1, the registered values.

The model, cutoffs, smearing, dipole correction and forc_conv_thr 2e-3 are unchanged.
- r5 is stopped, with RESCUE_HANDLED set first so no automatic rerun of it follows.
- Replacement: r6 replaces r4 if its first energy, at step 45's geometry, is at most 1 mRy above
  r4's step-45 energy (-5161.31207972 Ry), the same solution. r5 completed no SCF, so it replaces
  nothing.
- r6 is in `cfg_watch.txt` and `rescue_watch.txt` and goes to the top of `cfg_queue.txt` with its
  density staged.
- Cost: FIRE starts with a fresh velocity history and r4's BFGS history is lost. r5's SCF energy
  at the trial geometry was 0.65 mRy below step 45, the energy still to be recovered.

Dry run (20:29Z): r6's input differs from r4's in prefix, mixing_beta, mixing_ndim and
ion_dynamics. Its positions match block 44 to 5e-9 A and are 0.065 A from block 45, the trial
geometry.

Deployed 20:29:47Z:
- r5 was stopped after 121 iterations of its first SCF.
- r6 launched at 20:30:12Z and read its density from file.
- Readout: the rerun check (`choose_run`) compared a rerun's start only with the predecessor's
  last printed geometry. That is a never-completed trial when the predecessor was stopped
  mid-step. It now also accepts the geometry of the predecessor's last completed SCF, the one its
  last energy belongs to (`completed_positions`; tested on stopped and converged outputs). So r6
  gets the same-solution test against r4's step 45, not the fallback "lower last energy" branch.

r6's first SCF converged in 11 iterations (20:44Z): -5161.31208067 Ry, -0.0009 mRy from r4's
step-45 energy at the same geometry, total force 0.020.
- Moments: Fe6 +1.50, Ni30 -0.32, Ni5 +0.10, Ni29 +0.72. That is C4, r4's configuration, with
  every moment within 0.01 muB of r4's step 45.
- r6 replaces r4 under the amendment-9 rerun rule (same solution).
- The open question is r6's SCFs near the region where r4's step 46 and r5 stalled. FIRE's steps
  are reported as they come.

r6 at 21:18Z: 4 steps, -5161.31208067, -5161.31223519, -5161.31242626, -5161.31260204 Ry (0.15-0.19
mRy per step). Its SCFs took 11, 8, 12 and 12 iterations, and the total force is down to 0.0126.

## Amendment 15b (2026-11-16 21:20Z; V2, before any V2 eta exists)
Amendment 15's bootstrap SCF `u0__CoOOH__slab_smear3` converged at 21:13Z, in 79 iterations at
MV 0.03 Ry.
- Its energy, -4595.41595798 Ry, is numerics only and enters nothing.
- Its total magnetization is 1.33 muB (absolute 1.42). The 0.01 Ry cold SCF stalled at -0.20 to
  -0.26 muB.
- Its density is in `keep/u0__CoOOH__slab_smear3`.

The slab's registered relaxation starts from it (`src/dft/film_box/amend15b_coslab.sh`).
`u0__CoOOH__slab_r2` is `u0__CoOOH__slab`'s input with:
- `startingpot = 'file'`, from smear3's density, staged;
- `upscale = 1.d0` (amendment 4; the slab's input lacked it, as amendment 13 noted).

Everything else is the registered relaxation: MV 0.01, local-TF, beta 0.05, ndim 20, conv_thr
5e-6, forc_conv_thr 2e-3, BFGS. The slab finished no step, so it starts from its input geometry.
- Amendment-9 rerun rule: `u0__CoOOH__slab` completed no SCF, so r2 replaces it.
- Whether the registered SCF holds the bootstrap's weakly magnetic state or moves away is reported
  with its first step.
- r2 is in `rescue_watch.txt` and at the top of `co_queue.txt`. `post_relax.sh` launches it into
  the slot smear3 freed, and `yield_co` can stop it for V1 work. It stops with the other V2 runs
  when V1 is done, and its density and output are kept for the V2 continuation.
- Dry run (21:19Z): the input differs from the slab's only in prefix, startingpot and upscale.
  Positions and k-points are identical.

## Progress at 23:05Z (before any eta existed)
`u0__NiFeOOH__Fe0_OH_r6` (FIRE), steps 5-8 (21:31-22:05Z):

| Step | E (Ry) | Total force | SCF iterations | Ni30 (muB) |
|---|---|---|---|---|
| 5 | -5161.31274402 | 0.0098 | 13 | -0.30 |
| 6 | -5161.31288579 | 0.0112 | 8 | -0.29 |
| 7 | -5161.31307368 | 0.0092 | 12 | -0.27 |
| 8 | -5161.31328997 | 0.0091 | 12 | -0.24 |

- Fe6 +1.50 to +1.53, Ni5 +0.09 to +0.11 and Ni29 +0.72 throughout.
- Ni30's moment is shrinking with the relaxation, from -0.32 at step 1 to -0.24 at step 8. Under
  rule 1's 0.25 muB cutoff, step 8's pattern is Fe +, no Ni antiparallel. That pattern is none of
  C1-C6; C2 is the all-parallel pattern with Fe antiparallel. The configuration is assigned from
  the converged state, so it is not yet known whether r6 stays in C4 or ends in a pattern that rule
  1 adds as a candidate.
- Step 9's SCF is slow. At 23:05Z it had run 61 iterations, against electron_maxstep 200.
  - For about 40 iterations the accuracy oscillated near 1e-3 Ry while the total magnetization
    rose from 11.0 to 11.3.
  - It then fell to 6.5e-5 Ry, with the magnetization back at 11.09.
  - No 30-iteration run below 1e-5 has occurred, so amendment 10's floor does not apply.
  - r6 is in `rescue_watch.txt`: an SCF failure gives an automatic rerun from the kept density.

`u0__NiOOH__Ni0_OOH`, amendment 12 (the first of r4 and r5 to converge stands):
- r4 (BFGS): 23 steps, -5216.70229592 Ry, total force 0.024, falling about 1 mRy per step.
- r5 (FIRE): 48 steps, -5216.69467215 Ry, total force 0.0093, falling 0.1-0.3 mRy per step.
- Both are all-parallel: every Ni moment is positive, and the site Ni6 is +0.02 (r4) and +0.04
  (r5), below the cutoff.
- The 7.6 mRy (0.10 eV) gap is a geometry difference: r4 is further down the same descent. Both
  started near r3's last energy (-5216.664 Ry).
- The two may still end in different minima. r5 has the lower force and may converge first at a
  higher energy. The rule is unchanged, and both final energies are reported with the readout.

`u0__NiFeOOH__Fe0_O_r2`: 25 steps, -5160.04014416 Ry, total force 0.0101.

`u0__CoOOH__slab_r2` (V2), the registered relaxation from the MV 0.03 bootstrap density:
- Its first SCF converged in 41 iterations. That is the first SCF of the CoOOH slab to converge at
  MV 0.01; `u0__CoOOH__slab`'s stalled.
- The bootstrap's weakly magnetic state did not hold. Total magnetization by step:
  - step 1: 0.25 muB (absolute 0.37);
  - steps 2-6: 0.23, 0.15, 0.12, 0.10, 0.09.
- At step 6 every Co moment is within 0.02 muB of zero. That is consistent with low-spin Co(III)
  (t2g6), the expected state of CoOOH. The 1.33 muB bootstrap state was a property of the 0.03 Ry
  smearing.
- Energies, steps 1-6: -4595.46506298, -4595.46802484, -4595.51156084, -4595.51691030,
  -4595.51918224, -4595.52216108 Ry.
- Total force 0.43 to 0.046; SCFs of 41, 29, 20, 16, 14 and 14 iterations.

V2 adsorbate runs: `Co0_O` 13 steps (force 0.041), `Co0_OH` 15 (0.037), `Co0_OOH` 13 (0.044).

## Fe-site *O converged in C5 (2026-11-16 23:38Z, before any eta existed)
`u0__NiFeOOH__Fe0_O_r2` (amendment 13) converged at 23:38:27Z: 28 SCF cycles and 27 BFGS steps,
final energy -5160.04053567 Ry.
- Criteria met: energy change < 1e-4 Ry and every force component < 2e-3 Ry/Bohr. The last step
  lowered the energy by 0.09 mRy and the total force was 0.0077.
- Energy fell 4.95 mRy from the first step (-5160.03558531 Ry). It went down steadily at 0.1-0.4
  mRy per step, and the total force stayed between 0.007 and 0.020 throughout.
- Moments at the end: Fe6 -1.62, Ni30 -0.30, Ni5 +0.65, Ni29 +0.17 (below the cutoff); every other
  Ni is +0.33 to +0.87. That is C5 (Fe -, Ni30 -), the configuration the run started in (step 1:
  Fe6 -1.58, Ni30 -0.46). Rule 1 adds no candidate.
- Adsorbate: the *O sits atop Fe6 at d(Fe6-O) = 1.637 A, a terminal oxo. Its nearest O neighbours
  are 2.60 and 2.61 A away, so there is no O-O bond. The input geometry had 1.637 A too.
- `post_relax.sh` queued the C1-C6 single points at 23:38:52Z. C1 started at 23:38:57Z.
- C2 started at 23:41:09Z, in the slot of `u0__CoOOH__slab_r2`. `yield_co` stopped the slab at step
  8 (V1 before V2), moved its directory to `runs_stopped/` and left it to relaunch from
  `co_queue.txt`.
- C5 is the rule-2 own-configuration check.

At 23:41Z, r6's step-9 SCF was at 99 iterations, with accuracy near 1e-4 Ry.

## Amendment 17 (2026-11-16 23:57Z, before any eta existed)
C7 = Fe +, every Ni + joins the Ni(Fe)OOH candidates. This applies amendment 11's rule 3: a
pattern that a relaxation's SCF enters adds a candidate, as C4 did.
- r6's step-8 SCF (`u0__NiFeOOH__Fe0_OH_r6`, converged 22:05Z, -5161.31328997 Ry) has Ni30 at
  -0.2442 muB, below rule 1's 0.25 muB cutoff.
- Fe6 is +1.52, and every other Ni is either parallel to atom 1 or below the cutoff. That pattern
  is none of C1-C6.

Scan of every completed SCF of every U = 0 Ni(Fe)OOH relaxation (`patscan.py`, the readout's
pattern definition):

| Run | Steps | Patterns entered |
|---|---|---|
| slab | 54 | C1 throughout |
| Fe0_O | 42 | C2 throughout |
| Fe0_O_r2 | 28 | C5 throughout |
| Fe0_OH_r4 | 45 | C4 throughout |
| Fe0_OH_r6 | 8 | C4 for steps 1-7, C7 at step 8 |
| Fe0_OOH | 69 | C3 for steps 1-38, C6 for steps 39-69 |

Fe0_OH, Fe0_OH_r2, Fe0_OH_r3 and Fe0_OH_r5 completed no SCF. So C7 is the only pattern a relaxation
has entered that is not already a candidate.

What follows:
- Every converged Ni(Fe)OOH relaxation gets a C7 single point: the clean slab, Fe0_OOH and
  Fe0_O_r2 now, and Fe0_OH (r6) with its C1-C7 set when it converges. No existing single point
  landed in C7, so none stands in for one.
- The C7 encoding sets Fe's start to +0.3 and every Ni's to +, with the cold start and conv_thr 1e-5
  of the other single points. Each C7 input differs from the same state's queued C2 input only in
  prefix and Fe's starting sign (C2 = Fe -, every Ni +).
- `make_cfg_sp.sh` (C7, default C1-C7), `post_relax.sh` v7 (queues C1-C7) and
  `film_pilot_readout.py` (C7 label) carry it.
- `deploy_pr7.sh` stops post_relax v6, installs v7 and the new `make_cfg_sp.sh`, writes the three C7
  inputs and appends them to `cfg_queue.txt`.
- Dry run (about 23:56Z): every C7 and C2 input pair differs as stated, and the full C1-C7 set for
  r6 builds and passes the encoding check.

Cost: three cold single points now, about 66-85 min on 24 ranks each, and one more for Fe0_OH. They
run in V1 slots inside the existing 06:00Z cap, so the cap does not move.

Cutoff fragility. The scan's largest unsigned moment per run (|m| < 0.25) was 0.241-0.247 in every
run but r6's first seven steps. So the 0.25 muB cutoff sits in a band where Ni moments often lie,
and r6's step-8 crossing is 0.006 muB below it. The cutoff and rules are left as registered. This
fragility is the reason both readouts exist: "lowest" over every counted single point, and "as
relaxed".

r6 itself is unchanged by this amendment. Its step-9 SCF is still running, and an SCF failure gets
`post_relax.sh`'s automatic rerun.

Deployed 23:57:51Z. This amendment was committed at 23:57:01Z (410b08ce), the code at 23:57:31Z
(33795299). Its heading first gave 2026-11-17 00:05Z, a clock error, corrected here.
- The box copies match the committed scripts (md5).
- post_relax v7 is running.
- `cfg_queue.txt` ends C5, C6 (Fe0_O_r2), then C7 for the slab, Fe0_OOH and Fe0_O_r2.
- C5 of Fe0_O_r2 had started at 23:56:53Z, under v6.
- The header comments of `post_relax.sh` v7 and `deploy_pr7.sh` say "2026-11-17 ~00:30Z", an
  estimate written in advance. The running scripts are not edited.

## FIRE convergence was not recognized by the box scripts (found 2026-11-17 00:00Z, before any eta existed)
pw.x's FIRE optimizer (`ion_dynamics = 'fire'`) reports convergence with "FIRE: convergence achieved
in N steps" and "End of FIRE minimization". It never prints "bfgs converged". The strings are from
the running pw.x binary. Three box scripts tested only for "bfgs converged":
- `post_relax.sh`: a converged FIRE relaxation in `cfg_watch.txt` would be logged as "finished
  without a converged relaxation", marked CFG_SKIPPED and given no single points. Fe0_OH_r6
  (amendment 16) is a FIRE run.
- `make_cfg_sp.sh`: it would refuse to build that run's single points.
- `v1done.sh`: amendment 12's first-to-converge rule would miss Ni0_OOH_r5 (FIRE) converging, and
  r4 would not be stopped.

`qe_qc.py` (the readout's convergence test) and `film_pilot_readout.py` already accept both lines.
No FIRE run had converged at 00:02Z: none of r5, r6, or any CFG_SKIPPED run in `cfg_watch.txt` has
the FIRE line. Nothing had been mis-marked.

Fix: each of the three scripts accepts either line (`post_relax.sh` v8, `make_cfg_sp.sh`,
`v1done.sh` v2). `deploy_pr8.sh` does the rest:
- stops post_relax v7 and v1done v1, installs the new copies and restarts both;
- removes CFG_SKIPPED from any cfg_watch run whose output has the FIRE line (none at 00:02Z).

Dry run (00:02:57Z):
- each new script carries the two-pattern test and no BFGS-only test;
- the pattern accepts a FIRE and a BFGS convergence line and rejects an SCF convergence line;
- `v1done.sh` v2's conditions evaluate as expected:
  - V1 running: r4, r5, r6, and C1-C5 of Fe0_O_r2;
  - unlaunched: C6 of Fe0_O_r2 and the three C7 points;
  - unhandled: r6.

Deployed 00:03:38Z, after this record (9071241f) and the code (6eb2ee25; the box copies match it by
md5).
post_relax v8 and v1done v2 are running, and no CFG_SKIPPED marker was removed. The header
comments' "~00:05Z" / "~00:15Z" are advance estimates.

## Amendment 18 (2026-11-17 00:08Z, before any eta existed)
r6's step-9 SCF stalled. At 00:06Z it had run 124 iterations:
- since about iteration 65, accuracy 1.0-1.1e-4 Ry with excursions to 3e-4, against conv_thr 5e-6;
- total magnetization 11.06-11.08 muB, with excursions from 11.00 to 11.15.

This is the signature of r5's floor (amendment 16). It would fail at electron_maxstep 200, at about
01:15Z. `post_relax.sh`'s automatic rerun would then restart at the same trial geometry, where r5's
SCF floored.

Evidence that the trial step is the cause:
- FIRE's moves grew every step as its velocity built up. The largest atomic displacement between
  successive geometries was 0.0029, 0.0036, 0.0042, 0.0052, 0.0063, 0.0077 and 0.0099 A. Step 9's
  trial is the largest, 0.0071 A in the largest Cartesian component from step 8.
- pw.x prints Ni30's projected (Hubbard-projector) moment twice per step: at SCF convergence, and
  at the start of the next SCF, from the extrapolated starting density.

| Value of Ni30's projected moment | muB |
|---|---|
| Converged, step 1 | -0.328 |
| Converged, step 7 | -0.278 |
| Converged, step 8 | -0.253 |
| Start of step 8's SCF | -0.247 (0.03 from step 7's converged value) |
| Start of step 9's SCF | -0.154 (0.10 from step 8's converged value) |

So step 9's SCF began well off the branch it had followed, in a moment that is soft (it is shrinking
along the path; amendment 17).

Rule (`src/dft/film_box/amend18_fe0oh.sh`, applied by `amend18_watch.sh`):
- When the newest Fe0_OH FIRE run has completed at least 2 steps and its current SCF passes 60
  iterations, it is stopped (RESCUE_HANDLED first, so no automatic rerun at the trial geometry).
- It restarts as the next run (r6 -> r7 -> r8 -> r9, r9 last), from its last completed geometry and
  that step's kept density.
- The input is otherwise unchanged: FIRE, beta 0.05, ndim 20, conv_thr 5e-6, upscale 1, startingpot
  'file'; same model, cutoffs, smearing, dipole correction and forc_conv_thr 2e-3.
- A FIRE restart has zero velocity and the initial time step, so its first move is much smaller than
  the accelerated step that stalled.
- At least 2 completed steps are required: from 1, a restart would repeat the first FIRE move
  exactly.
- Normal SCFs of r6 took 8-13 iterations, and every stall so far (r4's step 46, r5, r6's step 9) was
  unconverged at 60.
- Each new run is in `cfg_watch.txt` and `rescue_watch.txt` and goes to the top of `cfg_queue.txt`
  with its density staged.
- Amendment-9 rerun rule: it replaces its predecessor if its first energy, at the predecessor's last
  completed geometry, is at most 1 mRy above that step's energy. The readout chains `_rK` reruns
  already.

Cost: r6's step 9 is abandoned after about 2 h. Each restart repeats one SCF at an already-completed
geometry, about 11 iterations.

Dry run (00:06:36Z), r6 -> r7:
- r7's input differs from r6's only in prefix among the non-position lines.
- Positions match block 7, step 8's geometry, to 5e-9 A, and are 0.0071 A from block 8, the stalled
  trial.
- Kept density: written 22:05:31Z, step 8's '!'. Step 8 is -5161.31328997 Ry.

Deployed 00:07:51Z, after this record (ec1d9fd2) and the code (239a2d90, md5-matched on the box).
- The watcher's first poll stopped r6 at 00:07:54Z, with step 9's SCF at 125 iterations.
- r7 launched at 00:07:58Z.
- `post_relax.sh` marked r6 CFG_SKIPPED (stopped unconverged), and RESCUE_HANDLED blocked the
  automatic rerun.
- The header comments' "~00:15Z" are advance estimates.

r7's first SCF converged in 7 iterations, by 00:18Z:
- Energy -5161.31329176 Ry, -0.0018 mRy from r6's step-8 energy at the same geometry. r7 replaces r6
  under the amendment-9 rerun rule (same solution).
- Total magnetization 11.03. Moments: Fe6 +1.53, Ni30 -0.24, Ni5 +0.09, Ni29 +0.72. That is r6's
  step-8 state, pattern C7 under the cutoff.

## Fe-site *OH: r7's step-3 floor; force noise near Ni30 (2026-11-17 01:25Z, before any eta existed)

r7's step 2 converged:
- Energy -5161.31334576 Ry, -0.054 mRy from step 1.
- Total force went from 0.0111 to 0.0086 Ry/Bohr. The largest free-atom component went from 0.0061 to
  0.0031, on Ni30 both times.

Step 3's SCF then floored again. At 01:25Z it had run 53 iterations. Accuracy reached 9e-6 Ry near
iteration 24 (conv_thr 5e-6), then wandered between 1e-5 and 4.5e-4 Ry. Amendment 18's watcher
restarts it as r8 when the count passes 60, at about 01:32Z.

This floor does not fit amendment 18's explanation, which blamed an accelerated FIRE step. Step 3's
trial geometry is 0.0020 A from step 2, the largest atomic displacement, and step 2 was 0.0014 A from
step 1. Both are smaller than every r6 move (0.0029-0.0099 A). So the floor goes with where the
relaxation is, not with how big its step was.

Ni30's converged projected moment, in muB, along the whole path:

| Run, step | Converged Ni30 moment |
|---|---|
| r6, steps 1-8 | -0.328, -0.326, -0.320, -0.313, -0.305, -0.295, -0.278, -0.253 |
| r7, step 1 (r6 step 8's geometry) | -0.246 |
| r7, step 2 | -0.222 |
| r7, start of step 3's SCF (extrapolated) | -0.185 |

The moment falls faster per step even as the steps shrink. At r7's step 2 it dropped 0.024 muB over a
0.0014 A move. Ni30's moment is collapsing along the relaxation path, and the SCFs floor where it
changes fastest.

The forces near Ni30 are noisier than the force threshold:
- r6's step 8 and r7's step 1 are SCFs at the same geometry (positions agree to 5e-9 A).
- Their energies differ by 0.0018 mRy, and their Ni30 moments are -0.253 and -0.246.
- Their largest free-atom force components are 0.0033 Ry/Bohr (H35, the bulk hydroxyl H below Ni30)
  and 0.0061 (Ni30). Their total forces are 0.0091 and 0.0111.
- So at conv_thr 5e-6, free-atom forces near Ni30 are uncertain by about 0.003 Ry/Bohr. That is
  above forc_conv_thr 2e-3.
- pw.x printed "SCF correction compared to forces is large: reduce conv_thr to get better values" at
  every step of r6 (8 of 8) and r7 (2 of 2). r6's total SCF corrections were 0.004-0.013 Ry/Bohr,
  against total forces of 0.009-0.020.

Over r6 and r7's ten completed steps the energy fell 1.27 mRy (17 meV), from -5161.31208067 to
-5161.31334576 Ry. The last two steps gave 0.054 mRy.

There are three competing explanations:
1. Ni30's moment goes to zero, or changes sign, at a nearby geometry. That is a magnetic transition
   on the path, and SCFs near the crossing have two nearly degenerate solutions. The steady collapse
   and its growing rate support this.
2. The SCF numerics cannot settle a soft moment: Broyden with beta 0.05, ndim 20, local-TF, and MV
   smearing 0.01 Ry. A smaller beta or a larger ndim might converge. Not tested.
3. The C7 branch is unstable, and the relaxation would land in a different pattern (Ni30 positive
   or zero). Rule 3 (amendment 11) would then add that pattern as a candidate.

What this means for the registered process:
- Amendment 18's restarts continue as registered (r8, then r9).
- Each restart gains steps only while the SCFs of its first moves converge. r7 gained one step.
- Under explanation 1, r8 and r9 floor near the same geometry and the chain ends unconverged.
- The readout takes a state's energy only from a converged relaxation (`qe_qc.trusted_energy_ev`).
  So Fe0_OH would have no energy, and V1 would not be evaluable from this box.
- Nothing is changed tonight. Ni0_OOH (below) would not converge by 06:00Z either, so a protocol
  change for Fe0_OH could not deliver V1 tonight. The options for continuing go to Frank with the
  readout.

Other runs at 01:21-01:25Z:
- Ni0_OOH r4 (BFGS):
  - Step 29, -5216.70735955 Ry. Energy still falls 0.6-1.1 mRy per step.
  - Largest free-atom force 0.0106 Ry/Bohr, on H35, the bulk hydroxyl H below Ni30. Total force
    0.0247.
  - About 24 min per step (steps 26-29 took 00:08-01:21Z).
- Ni0_OOH r5 (FIRE):
  - Step 58, -5216.69932541 Ry. The last three steps lie within 0.1 mRy.
  - Largest free-atom force 0.0035-0.0205 Ry/Bohr, on the *OOH hydrogen (atom 51) or its O (atom 50).
  - r4 is 8.03 mRy below r5. Amendment 12 still applies: the first to converge stands, and both are
    reported.
- Fe0_O_r2's single points C1-C5 run from atomic densities and had run 82-104 iterations, all
  unconverged:
  - C2 is nearest to convergence, at an accuracy of 0.02-0.03 Ry at iterations 95-96.
  - C1 and C3 are at 1-6 Ry.
  - C4 and C5 are at 30-120 Ry. C5's total magnetization swings between +5.3 and -2.5 muB.
  - The earlier single points converged in 59-88 iterations, except C4 at Fe0_OOH, which failed at
    200.
  - C5 is the rule-2 own-configuration check for Fe0_O (relaxed in C5). If C5 reaches
    electron_maxstep 200 unconverged, at about 03:20Z (about 1 min per iteration), Fe0_O has no
    rule-2 check. Its relaxed energy
    stands either way.
- Still queued: C6 and C7 at Fe0_O_r2, and C7 at the slab and at Fe0_OOH.

## Amendment 19: one diagnostic SCF, entering no criterion (2026-11-17 02:01Z, before any eta existed)

The restart was clean. At 01:32:26Z the watcher stopped r7, with step 3's SCF at 60 iterations, and
r8 began at 01:32:52Z. r8's input differs from r7's only in the prefix. Its positions match r7's
step-2 geometry to 5e-9 A, and its density is r7's kept step-2 density (00:31:50Z).

r8's first SCF is a control, and it has not converged:
- It repeats r7's step 2 at the same geometry, from that step's converged density.
- r7 reached step 2's SCF in 13 iterations from the extrapolated density.
- At 02:00Z r8 had run 25 iterations. Its accuracy has stayed between 7.9e-6 and 3.6e-5 Ry since
  iteration 7, against conv_thr 5e-6.
- Its total magnetization wandered between 11.06 and 11.13 muB. Step 2 converged at 11.06.
- Its wavefunctions restart from atomic+random. So an SCF that started from a density converged to
  5e-6 at this geometry does not settle there again.

C2 at Fe0_O_r2 converged at 01:49:57Z (rc 0, 7728 s). Its readout comes with the pull.

Purpose: tell explanations 1 and 2 of the previous section apart. Explanation 1 is two
near-degenerate solutions as Ni30's moment collapses. Explanation 2 is SCF numerics that cannot settle
a soft moment.

Run (`src/dft/film_box/diag19.sh`):
- `diag19__NiFeOOH__Fe0_OH_r7s3` is an SCF at r7's step-3 trial geometry, the one whose SCF floored
  (r7's block 2).
- It starts from r7's step-2 kept density, with mixing_beta 0.02 in place of 0.05.
- Everything else is r7's input: local-TF, ndim 20, conv_thr 5e-6, MV 0.01 Ry, cutoffs, dipole
  correction, electron_maxstep 200, tprnfor. calculation = 'scf', so &IONS is dropped.
- It goes to the top of `co_queue.txt`. It takes the first 24 free cores after `cfg_queue.txt`'s
  entries, the three C7 points (V1 first), and ahead of CoOOH's relaunches.
- It is expected to start when Fe0_O_r2's C1-C5 points end, at about 03:00-03:20Z. The deadline
  allows it about 160 iterations.
- Its name has no `u0__` prefix. So `v1done.sh` does not count it as V1 work, and the readout never
  reads it. It enters no criterion.

How it will be read (fixed now, before it runs):
- Converges within 60 iterations: supports explanation 2. The continuation would restart Fe0_OH's
  chain from r8's state with beta 0.02. That is a mixing-only change, which amendment 2 lets stand
  for the same state, and it would be registered then.
- Floors like r7's step 3 (accuracy at or above 1e-5 past 60 iterations): supports explanation 1. The
  continuation would then need a treatment of Ni30's moment, not a mixing change.
- In-between results are reported as they are, with no verdict.
- Either way, its Ni30 moment, total magnetization and forces show which way the C7 branch goes at
  that geometry.
- The comparison is not fully controlled. r7's step-3 SCF started from the extrapolated density;
  this one starts from step 2's converged density.

Dry run (02:01:01Z, md5 6401ef81 on the box):
- The input differs from r7's in calculation, prefix and mixing_beta, and &IONS is dropped.
- Positions match r7's block 2 to 4.8e-9 A, 0.0020 A from block 1 (step 2's geometry).
- The kept density is from 00:31:50Z, r7's step 2 (-5161.31334576 Ry). All input checks passed.

Deployed 02:01:37Z, after this record (19fa74f1, 02:01:25Z) and the code (cd56b777, md5-matched on the
box):
- The input is in `inputs/`, the density in `stage/`, and the run at the top of `co_queue.txt`.
  `queue.log` has the DIAG19 line.
- This heading first read 02:05Z, and the script's header comment still does. Both were advance
  estimates; the record time is 02:01Z.

## Amendment 20: r9 with mixing_beta 0.02 if r8's first SCF stalls (2026-11-17 02:14Z, before any eta existed)

r8's first SCF, the control in amendment 19, has drifted away from convergence:

| Time | Iterations | Accuracy (Ry) |
|---|---|---|
| 02:00Z | 25 | 7.9e-6 to 1e-5 (closest approach) |
| 02:12Z | 37 | 2.5e-5 to 4.5e-5 |
| 02:14Z | 39 | 3.8e-5 |

Total magnetization has been 11.02-11.13 muB. Amendment 18's watcher cannot act on r8, because it
needs at least 2 completed steps.

If nothing is done:
- r8 runs to electron_maxstep 200, at about 04:55Z.
- `post_relax.sh`'s automatic rescue then queues an exact copy of r8 as r9: same input geometry and
  density, and conv_thr 5e-6 unless amendment 10's floor rule applies.
- So the beta-0.05 chain cannot advance tonight.

Rule (`src/dft/film_box/amend20_r9.sh`, a one-shot watcher on the box):
- If r8's first SCF passes 60 iterations unconverged (amendment 18's stall threshold), r8 is stopped.
  RESCUE_HANDLED is touched first, so no automatic rescue follows.
- r9 starts from r8's input, changing only the prefix and mixing_beta, 0.02 in place of 0.05.
  - Same geometry: r7's step 2, which is r8's input.
  - Same density: `keep/u0__NiFeOOH__Fe0_OH_r7`, r7's step-2 density (00:31:50Z), which r8 was
    staged from.
- Amendment 2 lets a mixing-only change stand for the same state.
- r9 is in `cfg_watch.txt` and `rescue_watch.txt`, at the top of `cfg_queue.txt`, and is the last
  member of amendment 18's chain, which follows it as usual.
- Readout: r8 completed no SCF, so r7 stands over r8. r9 started from r7's last completed geometry,
  so it replaces r7 if its first energy is at most 1 mRy above r7's step 2 (amendment-9 rerun rule).
- The watcher exits with no action if r8's first SCF converges first, if r8 ends, or at the deadline.

This brings forward the beta-0.02 restart that amendment 19 left for the continuation:
- r9's first SCF is a controlled A/B against r8's first SCF. They have the same geometry, the same
  starting density and the same input, except beta.
- If it converges, the FIRE relaxation continues from there.
- Amendment 19's diagnostic still runs. It covers the harder geometry, r7's step-3 trial.

How r9's first SCF will be read (fixed now):
- Converges within 60 iterations: beta 0.02 settles the step-2 geometry where 0.05 did not. That is
  one pair, so it is suggestive, not conclusive: r7's own step 2 converged with 0.05, starting from
  the extrapolated density.
- Does not converge within 60: beta 0.02 does not fix it. r9 runs on under the usual rules.

Dry run (02:14:30Z, md5 93d08203 on the box):
- r9's input differs from r8's only in the prefix and mixing_beta 0.05 -> 0.02.
- The positions are r8's exactly.
- The kept density is r7's step-2 density, from 00:31:50Z, -5161.31334576 Ry.

Deployed 02:15:04Z, after this record (16da8feb, 02:14:53Z) and the code (d85498be, md5-matched on
the box). The watcher is running, and `queue.log` has its start line. This heading first read 02:16Z,
an advance estimate; the record time is 02:14Z.

## r9's first SCF: beta 0.02 does not settle it; Fe0_O single points (2026-11-17 03:41Z, before any eta existed)

Amendment 20 acted as registered:
- At 02:34:10Z it stopped r8, with the first SCF at 60 iterations.
- r9 began at 02:34:23Z.
- `post_relax.sh` marked r8 CFG_SKIPPED, and no automatic rescue followed.

r9's first SCF had not converged at 60 iterations. This is amendment 20's second reading: beta 0.02
does not fix it.

| SCF | Iteration 1 | Best accuracy (Ry) | Then | Total magnetization (muB) |
|---|---|---|---|---|
| r8 (beta 0.05) | 5.7e-4, 11.09 | 7.9e-6, iteration 12 | wandered 8e-6 to 5.6e-5 up to iteration 60 | 11.03-11.13 |
| r9 (beta 0.02) | 5.7e-4, 11.09 (identical) | 8.6e-6, iteration 11 | wandered 1e-5 to 1.0e-4; 2.2e-5 at iteration 63 | 11.00-11.11 |

r7's own step 2 converged at this geometry in 13 iterations, from the extrapolated density, at 11.06
muB. r9 runs on under the usual rules. It cannot reach electron_maxstep 200 before the 06:00Z
deadline.

Reading:
- At r7's step-2 geometry and from that step's converged density, both betas get within a factor of
  2 of conv_thr in about 10 iterations, then wander.
- While they wander, the total magnetization moves over about 0.1 muB with residuals near 1e-5 Ry.
- So this SCF has no well-isolated fixed point at the 5e-6 level. Halving the mixing does not change
  that.
- This favors explanation 1, near-degenerate solutions, over a plain mixing problem. It is one
  geometry and one parameter. Local-TF, ndim and smearing were not varied.
- The residual bounds the energy spread among these near-solutions at roughly 0.01 mRy, far below the
  resolution eta needs. The failure is the solver's stopping test, not an undetermined energy.
- Amendment 10 already treats 1e-5 Ry as this setup's noise floor for reruns. Tonight's Fe0_OH SCFs
  floor at or just below it.

Amendment 19's diagnostic began at 03:23:48Z. It took the first free slot after cfg_queue's C7
points.
- Its first iteration has accuracy 0.46 Ry, against r9's 5.7e-4 from the same density.
- The reason: an `scf` run that reads a density at a new geometry uses it as is. A relaxation's
  trial step instead extrapolates it, swapping the old atomic superposition for the new one. So the
  diagnostic starts farther from self-consistency than r7's step-3 SCF did (9.6e-3 at its second
  iteration).
- That is a further confound for amendment 19's comparison, besides the starting density it already
  names.
- By iteration 14 it was at 1.8e-3 Ry, total magnetization 10.83-11.38. Its 60-iteration reading
  comes at about 04:30Z.

Fe0_O_r2's single points:

| Target | Result | Landed | Energy (Ry) | From relaxed Fe0_O_r2 (C5, -5160.04053567 Ry) |
|---|---|---|---|---|
| C1 | SCF failed at 200 (02:58Z) | - | - | - |
| C2 | converged in 120 iterations (01:49Z), total magnetization 5.94 | C5 (largest unsigned moment 0.177) | -5160.04053489 | +0.0008 mRy |
| C3 | converged in 194 iterations (03:06Z), total magnetization 1.75 | other: Fe -, Ni5 and Ni28 - (signs relative to atom 1; largest unsigned moment 0.213) | -5160.03324440 | +7.29 mRy |
| C4 | SCF failed at 200 (03:23Z) | - | - | - |
| C5 | SCF failed at 200 (03:20Z) | - | - | - |

What the table means:
- Rule 2: C5's point, Fe0_O's own-configuration check, did not converge, so Fe0_O has no rule-2
  check. Its relaxed energy stands; rule 2 is reported, not a gate.
- C2's point landed in C5 at +0.0008 mRy: the relaxed state, reached again from a different start.
  It is reported as landed in the state's own configuration.
- C3's point found a new pattern. Under rule 3 a pattern first seen in a single point counts only for
  that state. At +7.29 mRy it does not lower Fe0_O.
- C6 and C7 are running: C6 at 119 iterations, C7 at 16, at 03:40Z.

Others at 03:40Z:
- Ni0_OOH r4: step 36, total force 0.0171.
- Ni0_OOH r5: step 73, total force 0.0081.
- C7 single points: the slab at 41 iterations, Fe0_OOH at 30.

## Amendment 19's reading; C7 at the slab (2026-11-17 04:34Z, before any eta existed)

The diagnostic, `diag19__NiFeOOH__Fe0_OH_r7s3`, had not converged at 60 iterations. At iteration 60
its accuracy was 1.4e-4 Ry. From iteration 39 to 68 it stayed between 1.5e-5 (best, iteration 45)
and 1.0e-3, with total magnetization 10.98-11.05 muB. That is amendment 19's second reading: it
floors like r7's step 3, which supports explanation 1.

Together with amendment 20, beta 0.02 settled neither geometry where beta 0.05 floored: r7's step-2
geometry (r9 against r8) or its step-3 trial (this run against r7's step 3). The record still carries
these limits:
- Only beta was varied. Local-TF, ndim and smearing were not.
- This run started farther from self-consistency than r7's step 3 did (see above).

For the continuation, the evidence points to treating Ni30's soft moment, not to further mixing
changes.

The slab's C7 single point converged at 04:12:05Z (4424 s):
- It landed in C1, the slab's relaxed configuration (largest unsigned moment 0.152).
- -5118.50257912 Ry, +0.003 mRy from the relaxed slab (-5118.50258211). Total magnetization 7.15 muB.
- Five of the slab's six targets (C1, C3, C4, C6, C7) now land in C1, within 0.003 mRy of the relaxed
  energy. C2 is 5.29 mRy above, at 4.85 muB, as recorded earlier.
- So rule 3's new candidate does not lower the slab.

The freed cores went, as registered, to the next entry in `co_queue.txt`: CoOOH's `slab_r2`
relaunch (V2), at 04:12:40Z.

At 04:33Z:
- Fe0_OOH's C7 point: 4.9e-5 Ry at iteration 81.
- Fe0_O_r2's C7 point: 13 Ry at iteration 75.
- Fe0_O_r2's C6 point: 0.86 Ry at iteration 177.
- r9: 116 iterations, about 2e-5 Ry.
- Ni0_OOH r4: step 39, total force 0.0100.
- Ni0_OOH r5: step 77, total force 0.020 (it has been 0.008-0.020 over its last steps).

Fe0_OOH's C7 single point converged at 04:37:49Z (5476 s):
- It landed in C2 (largest unsigned moment 0.223): -5202.80568746 Ry, total magnetization 8.93 muB.
- That is +15.89 mRy from relaxed Fe0_OOH (C6, -5202.82157378).
- It is the C5 point's solution again: the C5 point also landed in C2, at -5202.80568566 and 8.93
  muB, 0.002 mRy away.
- So it does not lower Fe0_OOH. The lowest remains the C2 point's own C2 solution, -5202.82269956 Ry
  (-1.13 mRy, 6.92 muB).
- Two different solutions both read as C2 under the 0.25 muB cutoff, 17.0 mRy apart. The pattern key
  does not tell them apart; the energies and total magnetizations do.

The next free cores went to CoOOH's `Co0_O` relaunch (V2), at 04:38:08Z.

## Deadline, pull and readout (2026-11-17; the readout is the first time any eta could exist)

The box stopped at the 06:00Z cap. Events, from `queue.log` and the pull logs:

| Time | Event |
|---|---|
| 04:55:07Z | Fe0_O_r2's C6 point failed at 200 iterations. |
| 05:58:27Z | r9's first SCF reached electron_maxstep 200 unconverged (last accuracy 1.7e-5 Ry). `post_relax.sh`'s automatic rescue queued r10, an exact copy (input geometry, kept density). |
| 05:58:45Z | r10 began. |
| 06:00:15Z | `post_relax.sh` stopped at the deadline. |
| 06:02:26Z | `deadline.sh` stopped every run. Cut short: r10 (1 iteration), Ni0_OOH r4 and r5, the diagnostic (153 iterations, 5.2e-5 Ry, never converged), Fe0_O_r2's C7 point (174 iterations, 17 Ry), and CoOOH's relaunches. |
| 06:25:55Z | Restart densities pulled to `D:/sts-electrocatalyst/film_pilot/out/densities` (4.1 GB, md5 OK). |
| 06:38:44Z | `out.tgz` pulled and extracted (md5 OK). PULLED touched. |
| After the pull | The box shut itself down. The instance is stopped, not terminated: the SSO token had expired, so `terminate-instances`, security-group and key-pair deletion still need a fresh `aws sso login`. |

Ni0_OOH at the deadline:
- r4 (BFGS): 44 steps, -5216.71414840 Ry. The last four steps fell 0.10-0.17 mRy each, against
  BFGS's default etot_conv_thr of 0.1 mRy. The largest free-atom forces were 0.0021-0.0034 Ry/Bohr,
  against forc_conv_thr 2e-3.
- r5 (FIRE): 86 steps, -5216.70419515 Ry. The last four steps fell 0.03-0.05 mRy each. The largest
  free-atom forces were 0.0031-0.0044.
- r4 is 9.95 mRy below r5. Neither converged.

Readout (`film_pilot_readout.py --model u0`, run on the pulled outputs):
- V1: not evaluable, in both the lowest and the as-relaxed readouts.
  - Ni0_OOH: r4 is INCOMPLETE. The chain notes: r3 replaced the original, r4 replaced r3, and r5
    did not start from r4's last geometry, so the lower last energy, r4, is used.
  - Fe0_OH: r7 is INCOMPLETE. r8, r9 and r10 completed no SCF, so r7 stands, with 2 steps in C7.
- V2: not evaluable. CoOOH's slab and Co0_OH are POISONED, Co0_O is INCOMPLETE, and Co0_OOH is
  missing.
- TRUSTWORTHY states:
  - NiOOH: slab_r2, Ni0_OH, Ni0_O_r2.
  - Ni(Fe)OOH:
    - slab (C1). Own check 0.0 mRy; five targets land in C1 within 0.003 mRy.
    - Fe0_O_r2 (C5). No own check; C2's point landed in C5 at +0.001 mRy.
    - Fe0_OOH (C6). The lowest is C2's point, its own C2 solution, -1.13 mRy.
  - Gas references: H2O, H2.
- No eta exists for any site.

So V1 needs exactly two more converged relaxations, Ni0_OOH and Fe0_OH. Every other V1 state is in
hand.
- Ni0_OOH r4 is a few BFGS steps from both thresholds.
- Fe0_OH is blocked by the SCF floor at Ni30's soft moment (amendments 18-20). The SCF does not
  settle below about 1e-5 Ry at its current geometry, with either beta.
- Continuing needs compute off this box (Anvil) and a registered treatment of the Fe0_OH SCF. Both are
  Frank's decision.

## Amendment 21: V1's two open relaxations continue on Anvil (2026-11-17 22:12Z, before any eta existed)

Frank, 2026-11-17: "Continue on Anvil then". That answers the continuation question in the status
report, which recommended conv_thr 1e-5 for Fe0_OH. The scope is V1. V2 (CoOOH) is not continued
here; it needs its own SU estimate and Frank's OK.

Venue and parity:
- Anvil, CHE260157 CPU allocation. `mybalance` at 22:08Z: 3,824.1 SU left.
- QE 7.5 from conda-forge (`qe-7.5-h19104ac_2`, HDF5 build, OpenMPI 5) at
  `$PROJECT/qe/env`. The AWS box installed conda-forge `qe=7.5` on 2026-11-14; its build string is
  not in the outputs.
- The four pseudopotentials on Anvil match the MD5 sums pw.x printed on the box:
  - Fe.pbe-spn-kjpaw_psl.0.2.1: e8661842...
  - H.pbe-rrkjus_psl.1.0.0: f52b6d4d...
  - ni_pbe_v1.4.uspp.F: 1ee80287...
  - O.pbe-n-kjpaw_psl.0.1: 0234752a...
- Parity check: each run's first SCF repeats the box's last completed SCF, at the same geometry and
  from that SCF's kept density. The amendment-9 rerun rule (at most 1 mRy above) decides whether it
  stands. The actual difference is reported as the cross-machine parity.

Runs (`src/dft/film_box/anvil_stage.sh`, `anvil_film.slurm`):
1. `u0__NiOOH__Ni0_OOH_r6`:
   - Restarts r4 (BFGS) from its last completed geometry (step 44, -5216.71414840 Ry) and that step's
     kept density.
   - r4's input is otherwise unchanged: conv_thr 5e-6, beta 0.05, ndim 20, upscale 1, forc_conv_thr
     2e-3.
   - BFGS restarts with a fresh Hessian.
   - Amendment 12's race between r4 and r5 ends here. Only r4's branch continues: it is 9.95 mRy
     lower and nearer both thresholds, and the budget is limited.
   - r5 is not continued. Both branches' energies are reported.
   - The readout keeps r4 over r5 (neither converged, lower last energy). r6 replaces r4 under the
     rerun rule.
2. `u0__NiFeOOH__Fe0_OH_r11`:
   - Restarts r7 (FIRE) from its last completed geometry (step 2, -5161.31334576 Ry) and that step's
     kept density.
   - conv_thr is 1e-5 in place of 5e-6. That is amendment 10's noise-floor value: amendments 18-20
     showed this SCF wanders at 1e-5 to 1e-4 Ry below about 1e-5 with either beta.
   - r7's input is otherwise unchanged: beta 0.05, ndim 20, upscale 1, forc_conv_thr 2e-3.
   - The readout keeps r7 over r8-r10, which completed no SCF. r11 replaces r7 under the rerun rule.
   - Known risk: the free-atom forces near Ni30 carry about 0.003 Ry/Bohr of SCF noise, above
     forc_conv_thr. FIRE may not meet the threshold even with every SCF converging. No other
     acceptance criterion is adopted now. If r11 has not converged when its job ends, the data goes
     back to Frank before further SU are spent on it.
3. After Fe0_OH converges:
   - The C1-C7 single points at its final geometry, as `make_cfg_sp.sh` builds them: scf, conv_thr
     1e-5, cold start, built locally from the pulled output.
   - Then the readout, unchanged.
   - Ni0_OOH has no configuration single points (NiOOH).

Rules while running:
- A run whose job ends unconverged after at least 2 completed steps is restarted from its last
  completed geometry and density as the next `_rK`, with the same input. That is amendment 18's
  restart, applied by hand.
- For Fe0_OH this happens once at most before it goes back to Frank (above).
- An SCF that fails at electron_maxstep is treated the same way.

Resources:
- Each job: `shared` partition, 48 ranks, `-nk 3` (16 per pool), 8 h limit, so at most 384 SU per job.
  Node a171 is excluded.
- Expected: about 0.5 core-h per SCF iteration, about 700-1,100 SU in all.
- Hard cap for this amendment: 1,800 SU, with single points included (7 x at most 3 h x 48).

Staging (22:11Z, local, nothing on Anvil touched):
- Both inputs differ from their predecessors only in prefix and pseudo_dir, plus conv_thr for r11.
- Positions:
  - r6 matches r4's block 43 (step 44's geometry) to 5e-9 A; the stalled trial is 0.0189 A away.
  - r11 matches r7's block 1 (step 2's geometry) to 4.7e-9 A; the trial is 0.0020 A away.
- Kept densities: r4's was written 05:45:18Z, and step 44 was reached at about 05:45:17Z. r7's was
  written 00:31:50Z, and step 2 at about 00:31:49Z.
- `anvil_stage.tar` is 171 MB, md5 3e41dffc.

Deployed 22:14Z, after this record (854cd809, 22:12:34Z) and the code (b4bf97d5):
- The tarball was md5-verified on Anvil (OK) and unpacked to `$PROJECT/film/runs/`.
- Neither input has CRLF. The pseudo paths resolve. `anvil_film.slurm` md5 3836037f matches on both
  ends.
- Jobs: 22283892 (`u0__NiOOH__Ni0_OOH_r6`) and 22283893 (`u0__NiFeOOH__Fe0_OH_r11`). Both are
  PENDING (Priority) in `shared`, with no start estimate yet. The partition had about 12,000 pending
  jobs.

AWS cleanup, after Frank's SSO login (2026-11-17 ~22:25Z):
- The stopped instance i-0fda1e34af116d88b (c7a.48xlarge, tag `Purpose=sts-film-dft-pilot`) is
  terminated. Its 150 GB root volume was deleted with it (DeleteOnTermination true).
- Its security group and key pair are deleted.
- No pilot-tagged instance remains.
- Everything was pulled to D: before this: `out.tgz` and the densities, both md5-verified.

Cross-machine parity, from r6's first SCF (job 22283892, node a201, began 22:35:26Z):
- It converged in 11 iterations, from the kept density, at -5216.71414921 Ry.
- r4's step 44 on AWS, same geometry, was -5216.71414840. The difference is -0.0008 mRy.
- Total force 0.011724 Ry/Bohr against 0.011752. Total magnetization 9.42 muB against 9.41.
- So the Anvil build reproduces the AWS box's energy to well below the amendment-9 tolerance. r6
  replaces r4 under the rerun rule (same solution).
- Speed: about 60 s per SCF iteration at 48 ranks, about 0.8 SU per iteration, not the 0.5
  estimated. An 8 h job holds about 480 iterations, roughly 25-30 BFGS steps. The 1,800 SU cap stands.

r11's first SCF (job 22283893, node a103, began 23:22:10Z):
- It converged at conv_thr 1e-5 in 7 iterations, from the kept density. The trace up to iteration
  6: 5.8e-4, 3.5e-4, 8.6e-5, 3.9e-5, 2.7e-5, 2.1e-5 Ry. It is r8's trace again (identical start).
- -5161.31335239 Ry, -0.0066 mRy from r7's step 2 (-5161.31334576). r11 replaces r7 under the rerun
  rule.
- It reached one of the nearby solutions amendment 20 described, not r7's exact one:
  - Ni30's converged projected moment -0.205 against r7's -0.222.
  - Total magnetization 11.09 against 11.06 muB.
  - Total force 0.0106 against 0.0086 Ry/Bohr. pw.x again warns that the SCF correction is large
    (0.0078).
- The energy spread between these solutions is 0.007 mRy, as amendment 20 bounded it. The force
  difference is again about 0.002.

Ni0_OOH r6 by 23:36Z: 5 steps, -5216.71457617 Ry, falling about 0.1 mRy per step; total force
0.0074-0.0093.

### Both Anvil jobs end early (2026-11-18 01:43Z and 01:47Z)

Outputs pulled to `D:\sts-electrocatalyst\film_pilot\out\runs\` (md5 equal to Anvil's). Forces below
are on free atoms only. pw.x prints the fixed bottom-layer forces too; atom 25's 0.088 Ry/Bohr is one
of those. `mybalance` at 01:52Z: 3,557.3 SU, so 266.8 SU since 22:08Z (r6 150.3, r11 116.4). That
leaves 1,533 of the 1,800 cap.

r6 (`u0__NiOOH__Ni0_OOH_r6`, job 22283892, a201, 3:07:53):
- It had 12 SCFs and 11 completed BFGS steps. It stopped at 01:43:13Z on a write error, after step 12's
  SCF converged (-5216.71565881 Ry, 26 iterations) and before step 12's forces:
  `create_directory: ./tmp/u0__NiOOH__Ni0_OOH_r6.save/ non existent or non writable`, error 28.
  16 ranks wrote it to `CRASH`. The directory existed and still exists.
- The cause is not established:
  - pw.x sums each rank's I/O status for this check. Under gfortran that status is errno, so 28 is
    ENOSPC on one rank, or ENOENT on 14 ranks.
  - The project fileset is at 4.5 of 5.0 TB (92%) and is shared with other jobs.
  - A pxrd-diff array task in the same project failed at 01:36-01:37Z. Its log was not found.
  - r11 wrote its 6.6 GB final state to the same fileset at 01:46:57Z without error.
  - Most likely, then, a transient write failure on the project fileset. Neither pw.x nor the input
    is at fault.
- Trajectory:
  - The energy fell monotonically, from -5216.71414921 (step 1) to -5216.71565881 (step 12): -1.51
    mRy in 11 steps. It fell 0.09-0.13 mRy per step through step 9, and 0.20-0.22 since.
  - BFGS energy error was 0.8-2.2e-4 Ry, against etot_conv_thr 1e-4 (the default). Gradient error was
    2.1-3.5e-3 Ry/Bohr, against 2e-3.
  - Max |F| was 0.0021-0.0035 (H35, O50, Ni5/Ni6, O22/O23). At step 7 only one atom was above 2e-3.
  - The largest move each step is H11, the hydroxyl H on O23, and it grows: 0.007 A at step 6, about
    0.020 A at steps 10-11.
  - So this is a slow, soft rearrangement under flat forces, not SCF noise: the energy only falls and
    every SCF converges. Ni0_OOH is not near convergence on the energy criterion.

r11 (`u0__NiFeOOH__Fe0_OH_r11`, job 22283893, a103, 2:25:30):
- It completed 2 FIRE steps.
- Step 2: -5161.31337660 Ry (-0.024 mRy from step 1), converged at 1e-5 in 28 iterations. Total force
  0.0086. Max |F| 0.0031 (H35 z), down from step 1's 0.0060 (Ni30 z). 3 atoms were above 2e-3.
- Step 3's trial geometry is at most 0.0019 A (H35) from step 2's. Its SCF did not reach 1e-5 in 200
  iterations (electron_maxstep):
  - The accuracy bottomed at 3.6e-5 (iteration 22), then wandered between 5.7e-5 and 5.1e-4 to the
    end (8.0e-5 at iteration 200).
  - Total magnetization was 11.01-11.20 muB after iteration 50.
  - pw.x stopped, wrote its unconverged state, and ended normally at 01:47:00Z.
- That final write replaced step 2's density in r11's save directory, so step 2's own density no
  longer exists.
- This is r7's step-3 floor again, now at conv_thr 1e-5: 0.002 A away from a geometry whose SCF
  converged in 28 iterations. At this site, whether the SCF reaches 1e-5 depends on which nearby
  magnetic solution the mixing falls into, not on the geometry.

Under amendment 21's rules:
- r6 ended unconverged after 11 completed steps, so it restarts as r7 (below).
- r11 ended unconverged on an SCF at electron_maxstep. Item 2 sends its data back to Frank before
  further SU are spent on it, so no r12 is started.

### Restart: `u0__NiOOH__Ni0_OOH_r7` (registered before deploy, 2026-11-18 ~02:00Z)

- r7 restarts r6 from step 11, the last step with forces (-5216.71545856 Ry), and step 11's density.
  That density was written 01:16:57.49Z (Anvil mtime), when step 11's SCF ended by the pw.x clock.
  Step 12's density was never written.
- Staging (`src/dft/film_box/anvil_restart.sh stage`, local): positions match r6's block 10 (step
  11's geometry) to 4.9e-9 A. Step 12's geometry is 0.0161 A away. `u0__NiOOH__Ni0_OOH_r7.in` md5
  7f38ae79.
- The input differs from r6's only in prefix and outdir. outdir moves off the shared, 92%-full
  project fileset, so the per-step density writes no longer depend on it: from `./tmp` to
  `/anvil/scratch/x-fcai3/film/u0__NiOOH__Ni0_OOH_r7/tmp` (user scratch, 100 TB quota, 0% used). The
  `.out` stays in `$PROJECT/film/runs/`. The physics is unchanged, and the first SCF's parity against
  step 11 tests that.
- BFGS restarts with a fresh Hessian, as r6 did.
- Expected: about 16 min per step, at most 384 SU (8 h). That leaves at most about 650 of the 1,800
  cap used after r7.
- If r7 ends unconverged after at least 2 steps, the same rule restarts it as r8, within the cap.

Deployed 01:57Z, after this record (c6a6d62a) and the code (efaa37a3):
- On Anvil, the `.in` md5 matched and the input has no CRLF.
- r6's step-11 `charge-density.hdf5`, `occup.txt` and `paw.txt` were copied to r7's scratch save
  directory and compared byte for byte. `anvil_film.slurm` md5 3836037f is unchanged.
- Job 22286398 is PENDING (Priority) in `shared`.

## Amendment 22: noise-aware acceptance for Fe0_OH (2026-11-18 ~02:20Z, before any eta existed)

Frank, 2026-11-18, shortly after 02:00Z: "b". That picks option (b) of the three put to him after r11 ended: accept
Fe0_OH under a criterion set by the measured SCF force noise. The other two were (a), a second
restart at the same settings, and (c), a change of electronic setup that would rerun every state.

Why pw.x's own test cannot be met here:
- r7's step 2 and r11's step 1 share one geometry (positions equal to output precision). Both SCFs
  converged at conv_thr 1e-5, into neighbouring solutions:
  - The energies differ by 0.0066 mRy.
  - Free-atom force components differ by up to 0.0028 Ry/Bohr (Ni30 z), with 0.0019 on Fe z and at
    most 0.0012 elsewhere.
- That noise exceeds forc_conv_thr (2e-3). Which solution the mixing lands in is not controlled, so a
  relaxation can sit at a minimum and still fail the force test. At the next geometry the SCF may also
  not converge at all, as at r7's and r11's step 3.

The criterion, for `NiFeOOH__Fe0_OH` only. A relaxation that pw.x did not converge is accepted at its
last completed step k (an SCF energy and forces) if all of these hold:
1. k >= 2;
2. |E_k - E_(k-1)| < 1e-4 Ry (etot_conv_thr, pw.x's own energy test);
3. the largest free-atom force component is at most 3.5e-3 Ry/Bohr: the measured 0.0028, rounded up.

The state's energy, moments, configuration label and adsorbate integrity are then step k's. Every other
state, Ni0_OOH included, keeps pw.x's convergence. Ni0_OOH's energy still falls 0.2 mRy per step, so
it would fail test 2 anyway.

Applied to the Fe0_OH chain (the rerun rule picks r11):
- r11's step 2 qualifies: -5161.31337660 Ry, dE -0.024 mRy. The largest component is 0.00306 (H35 z).
  Components above 2e-3: H11 0.00225, Ni29 0.00234, H35 0.00306. Configuration C7 (Ni30 -0.224 muB);
  *OH bound, d(Fe-O) 1.768 A.
- Caveat: H35's 0.00306 is not noise. Its force differs by under 0.0007 between the two solutions, so
  it is a small real residual. For a mode stiffness of at least 0.1 Ry/Bohr^2, the energy left in
  forces this size is F^2/2k <= 0.05 mRy per atom, under 1 meV. The FIRE steps since r6 lowered the
  energy by only 0.054 mRy (r7) and 0.024 mRy (r11).
- The chain has 54 distinct steps (r4 45 BFGS, r6 8 FIRE, r7 2, r11 2; each restart repeats one SCF).
  Over them the energy fell from -5161.26683 to -5161.31338 Ry. The adsorbate-QC warning "only 2
  ionic steps" counts r11 alone, because the U = 0 readout passes no chain count. It is report-only.
- r7's step 2 would also qualify (dE -0.054 mRy, 0.00314 on Ni30), but r11 replaces r7.

Readout (`src/dft/film_pilot_readout.py`):
- Adds `A22_STATES`, `a22_accept`, `step_positions`, `magnetics(upto_step)` and
  `state_record(accept=...)`. They apply only where the strict QC energy is None.
- Tested on the pulled outputs through these functions only, not `main_u0`, so no eta was computed:
  - r11 is accepted at step 2, as above.
  - r6 and r4 (Ni0_OOH) and r8 do not qualify.
  - The rerun chain still ends at r11.

Single points (amendment 21 item 3, now at the accepted geometry; `src/dft/film_box/anvil_cfg_sp.sh`):
- C1-C7 at r11's step-2 geometry, with `make_cfg_sp.sh`'s recipe unchanged:
  - scf, conv_thr 1e-5, cold start.
  - The same seven starting configurations and the same encoding check (all seven pass).
  - Positions equal r11's block 1 to 5e-9 A.
  - Mixing comes from r11's input (beta 0.05, ndim 20), since `make_cfg_sp.sh` copies the
    relaxation's own input.
  - outdir is on user scratch.
- Each job: 48 ranks, `-nk 3`, 4 h limit (electron_maxstep 200 at about 60 s per iteration is about
  3.3 h).
- Expected cost:
  - Cold starts on AWS took 59-194 iterations, and 5 of the 20 that finished hit 200.
  - At about 0.8 SU per iteration, the seven cost 340-1,120 SU.
  - With 266.8 SU spent and r7's at most 384, the worst case comes to about 1,770 of the 1,800 cap.
  - So if r7 needs an r8, or any spend would pass 1,800 SU, it goes back to Frank first.
- Single points that end unconverged do not count (amendment 11), as before. They are not rerun.

The readout runs once, when the single points have ended and Ni0_OOH has converged. V1 needs both
sites. It is not run before then.

Deployed 02:19Z, after this record (ab7c45b7) and the code (82099f96):
- The seven inputs' md5 on Anvil equal the staged ones: C1 e19960fb, C2 081b3003, C3 4a85c61d, C4
  15b4ef41, C5 8374c0d7, C6 5676a360, C7 91e12f2c.
- Jobs 22286624 (C1), 22286627 (C2), 22286628 (C3), 22286630 (C4), 22286631 (C5), 22286633 (C6) and
  22286634 (C7) are PENDING (Priority) in `shared`, 4 h each. Ni0_OOH r7 (22286398) is still PENDING.

### r7's first SCF: parity with r6 step 11 (2026-11-18 04:30Z, before any eta existed)

- Job 22286398 started 04:23:16Z on a211. Its first SCF converged in 12 iterations (restart from
  step 11's density) at -5216.71545978 Ry, total magnetization 9.46 muB.
- r6's step 11 was -5216.71545856 Ry, so r7 starts 0.0012 mRy lower. That is well within the
  rerun rule's 1 mRy (amendment 9), so r7 replaces r6.
- The parity also checks the outdir move: scratch instead of the project fileset changed nothing in
  the physics.
- The seven single points are still PENDING (Priority). Slurm's estimated starts are 05:13-05:48Z.
- SU balance 3,554.2 at 04:31Z.

### C5-C7 failed at launch; relaunched from scratch (2026-11-18 ~05:10Z, before any eta existed)

What happened:
- C5 (22286631, a173), C6 (22286633, a133) and C7 (22286634, a133) ended FAILED with exit 0:53. They
  ran 5, 32 and 73 s, between 04:54 and 04:58Z.
- Neither a Slurm log nor a `.out` exists for any of them. Slurm could not create the log on the
  project fileset, so the batch script never ran and pw.x never started. No SCF exists for these three.
- C1-C4 started 04:37-04:51Z and are running. C4's log was created at 04:51:46Z.

The cause, as far as tested (05:02Z):
- `touch` in `$PROJECT/film/logs` and in `$PROJECT` returns "No space left on device".
- `myquota` shows the project at 4.5 of 5.0 TB (91.7%) and 37.6% of its file limit; `df` shows 423 GB
  free.
- Creating files on user scratch works.
- So the project fileset refuses new files below its nominal quota. Why is not established.
- r6's error 28 at 01:43Z is consistent with the same condition.

Risk to the running jobs:
- Files already open keep growing: the `.out` files of r7 and C1-C4 were appended at 05:02Z.
- If appends also start failing, those runs could die at a write. That cannot be prevented without
  stopping them. Their densities and wavefunctions go to scratch, so a restart point would survive.

The relaunch:
- These are launch failures, not single points that ended unconverged. Amendment 11's no-rerun rule
  covers SCFs that ran and did not converge, so it does not apply here.
- The same three inputs run unchanged: md5 C5 8374c0d7, C6 5676a360, C7 91e12f2c, matching the deploy
  record.
- The new script `src/dft/film_box/anvil_film_scr.slurm` writes nothing to the project fileset:
  - The run directory is `/anvil/scratch/x-fcai3/film/NAME`. It holds NAME.in and the outdir `tmp/`
    that the inputs already name.
  - The log goes to `/anvil/scratch/x-fcai3/film/logs/`.
  - Reads (the QE env and pseudopotentials) stay on the project fileset.
  - It is otherwise identical to `anvil_film.slurm`, which the running jobs use (md5 3836037f,
    unchanged).
- `sbatch -t 04:00:00` as before. The outputs are pulled to the same local directories, so the readout
  is unaffected.
- Cost: the failed launches used about 1.5 SU. The relaunch stays inside the registered estimate for
  the seven single points (340-1,120 SU), so the worst case stays about 1,770 of the 1,800 cap.

Deployed ~05:15Z, after this record (ea84777a):
- `anvil_film_scr.slurm` is on scratch; its md5 29c8144b matches the repo copy.
- The three inputs were copied from the project run directories into the scratch run directories:
  md5 unchanged, no CRLF.
- Jobs 22289317 (C5), 22289319 (C6) and 22289320 (C7) are PENDING (Priority), 4 h each.

r7 at 05:02Z: 5 BFGS steps, about 8 min each. E -5216.71582631 Ry, falling 0.08-0.10 mRy per step;
total force 0.0085.

## Ni0_OOH converged; C1 and C4 single points (2026-11-18 06:30Z, before any eta existed)

Pulled to `D:/sts-electrocatalyst/film_pilot/out/runs/`. The md5 of every `.in` and `.out` matches
Anvil: r7 7f38ae79 / 361aca0a, C1 e19960fb / 0d9e62bd, C4 15b4ef41 / 8b094638. QC below uses the
readout's own functions (`qe_qc.trusted_energy_ev`, `state_record`, `choose_run`, `nife_label`), not
`main_u0`, so no eta was computed.

**`u0__NiOOH__Ni0_OOH_r7` converged** (job 22286398, 04:23-05:05Z, 42 min):
- "bfgs converged in 6 scf cycles and 5 bfgs steps". Final energy -5216.71588713 Ry; last dE -0.061
  mRy.
- The largest free-atom force component is 0.00168 (atom 11, the H of the *OOH; it was 0.002-0.0035
  in r6). Total force 0.0063. Every SCF converged, in 7-22 iterations.
- QC: TRUSTWORTHY. *OOH bound and intact (d(Ni-O) 1.867 A, d(O-O) 1.375 A, d(O-H) 0.987 A).
  Total magnetization 9.44 muB, every Ni parallel (smallest moment -0.020 on the site Ni).
- The "only 6 ionic steps" warning counts r7 alone; the U = 0 readout passes no chain count. It is
  report-only. The chain behind it is the first run, then r3, r4 (44 BFGS steps), r6 (11) and r7 (6).
- Rerun chain: the readout uses r7. Its note says r7 "did not start from r6's last geometry". That is
  because r6's last completed SCF, step 12 (-5216.71565881 Ry), has no forces: the density write
  failed right after it. r7 restarted from step 11, the last step with forces, as registered. The
  readout then takes the branch for sibling reruns (amendment 12) and uses the converged run, r7. Its
  final energy is 0.23 mRy below r6's step 12 and 0.43 mRy below step 11, so the parity branch would
  pick r7 too.

**C1 (job 22286624) did not converge:** 200 iterations; last estimated accuracy 0.12 Ry; total
magnetization 8.34. It does not count and is not rerun (amendment 11).

**C4 (job 22286630) converged in 147 iterations and left its target (Fe +, Ni30 -). It landed in C7,
the relaxed state's own label:**
- -5161.31668723 Ry. That is 3.311 mRy (45 meV) below the accepted relaxed energy at the same
  geometry, r11 step 2 at -5161.31337660.
- Only Ni30 changes materially. It is +0.299 here and -0.224 in the relaxation; every other metal is
  within 0.07 muB. Total magnetization 11.74 vs 11.05 muB.
- So at this geometry, the label C7 covers two distinct SCF solutions:
  - Ni30 weakly antiparallel, below the 0.25 muB cutoff: the relaxation's solution.
  - Ni30 weakly parallel: this point's solution, 3.3 mRy lower.
  - The settings are identical (the single point copies r11's input, cold start, conv_thr 1e-5). The
    difference is which solution the SCF reached.
- Its forces are larger: the largest free-atom component is 0.00515 (Fe) vs 0.00306. So the geometry
  is not relaxed for this solution, and its energy is an upper bound on that solution's relaxed
  energy (rule 3).

What the registered rules do with C4 (no rule changes):
- It counts as C7 (amendment 11 rule 1). Under rule 3, Fe0_OH's "lowest" energy is this point's,
  unless a later point lands lower.
- "As relaxed" (rule 4) keeps -5161.31337660. V1 passes only if it passes in both readouts; if they
  disagree, it is configuration-sensitive, not a pass.
- Rule 2's own check needs a point with target = landed = C7. That is the C7 point, still running.
- The readout reports C4's landing in C7 at -3.311 mRy (report-only). That is outside the 1 mRy
  tolerance, so the relaxed solution is not the lowest C7-labelled solution at this geometry.
- No re-relaxation in the lower solution is added (closure, amendment 11 rule 3; the cap).

Still running at 06:25Z: C2 (153 iterations), C3 (167), C5 (90), C6 (81) and C7 (36).

SU: balance 3,120.3 at 06:27Z, so 703.8 of the 1,800 cap has been spent on Anvil. C1 took 200
iterations in 108 min, about 0.43 SU per iteration, so the five running points need at most about
200 SU more.

The readout runs once, when these five end.

### C2 and C3 (2026-11-18 06:55Z, before any eta existed)

Pulled. The md5s match Anvil: C2 081b3003 / c45b9699, C3 4a85c61d / 664d5966.

**C2 (job 22286627) converged in 157 iterations, left its target (Fe -) and landed in C7:**
- -5161.31338924 Ry, 0.013 mRy below the accepted relaxed energy.
- Ni30 -0.202 (relaxed -0.224); every metal within 0.03 muB of the relaxation; total magnetization
  11.08 vs 11.05.
- From a different cold start, the SCF reached the relaxation's own solution and reproduced its
  energy well inside 1 mRy. This is the report-only "landed in own configuration" entry. Rule 2
  proper still needs target = landed = C7, which is the C7 point.
- So both C7-labelled solutions at this geometry were reached from cold starts: the relaxation's
  (C2's start) and the one 3.3 mRy lower (C4's start).

**C3 (job 22286628) did not converge:** 200 iterations, stuck at 3-4e-4 Ry estimated accuracy with
total magnetization 5.37, a low-moment region none of the converged points is in. It does not count
and is not rerun.

**C7 (job 22289320) is slow:**
- It shares node a094 with other users' jobs (load about 96 of 128 cores).
- Its iterations take 30-217 s and are getting slower, against a steady 29 s for C6. Davidson
  averages 1.1-1.3 sub-iterations, so the extra time comes from the node, not the SCF.
- At 46 iterations (06:50Z) the estimated accuracy is still 2-7 Ry.
- At this rate the 4 h limit (09:43Z) stops it before 200 iterations. It would then have ended
  unconverged, so it does not count and is not rerun (amendment 11).
- Rule 2 (reported, not a gate) would then have no own-configuration check for Fe0_OH. C2 still
  reproduces the relaxed energy from another start, reported as above.

C5 (135 iterations) and C6 (131) are running at 29-39 s per iteration.

SU: balance 3,037.3 at 06:51Z (786.8 spent). At most about 190 more: C5 and C6 to 200 iterations,
and C7 to its time limit.

### C5 (2026-11-18 07:05Z, before any eta existed)

Pulled from scratch. The md5s match Anvil: `.in` 8374c0d7 (the deploy record's), `.out` 4215cc97.

**C5 (job 22289317, a188, 05:37-06:58Z) converged in 147 iterations and kept its target, C5 (Fe -,
Ni30 -):**
- -5161.31854339 Ry. That is 5.167 mRy (70 meV) below the accepted relaxed C7 energy at the same
  geometry, and 1.86 mRy below the C4 point's C7 solution.
- Moments: Fe -1.535, Ni30 -0.358, every other Ni parallel. Total magnetization 6.94 muB.
- Forces are larger than at the relaxed solution. The largest free-atom component is 0.00911 on Fe;
  the next are O45 0.00538, O21 0.00391 and Ni29 0.00390. So the geometry is not relaxed for C5. Its
  energy is an upper bound on Fe0_OH's relaxed C5 energy (rule 3).
- C5 is the configuration that Fe-site *O relaxed in (Fe0_O_r2). It is also where the clean slab's
  C2 point landed (amendment 11).
- Under the registered rules it counts. Fe0_OH's "lowest" energy is now this point's, unless C6 or C7
  lands lower. "As relaxed" (rule 4) keeps the C7 relaxation.
- So for Fe0_OH the two readouts now differ by at least 5.17 mRy (0.070 eV). Rule 4 is the guard for
  this: V1 must pass in both.

Still running at 07:02Z: C6 (153 iterations, estimated accuracy 1.9 Ry) and C7 (54 iterations, 2.0
Ry). SU balance 3,004.2 (819.9 spent).

### C6 (2026-11-18 07:35Z, before any eta existed)

**C6 (job 22289319, a083, 05:43-07:26Z) did not converge.**
- md5 `.in` 5676a360 (the deploy record's), `.out` d8cb690e, matching Anvil.
- 200 iterations; the best estimated accuracy was 0.21 Ry, and the last was 0.87 Ry. Total
  magnetization wandered near 9.2-9.3 muB.
- It does not count and is not rerun (amendment 11).

C7 at 07:33Z: 77 iterations (2.1 Ry), now about 63 s per iteration. That pace reaches 200 iterations
close to the 4 h limit at 09:43Z. SU balance 2,961.1 (863.0 spent).

### C7; the single points have ended (2026-11-18 09:50Z, before any eta existed)

**C7 (job 22289320, a094, 05:43-09:43Z) hit its 4 h wall limit at iteration 188 without converging.**
- md5 `.in` 91e12f2c (the deploy record's), `.out` 39a1e8a1, matching Anvil.
- The best estimated accuracy was 3.6e-3 Ry, and the last was 4.8e-3 Ry. Total magnetization was
  near 9.6 muB at the end.
- Slurm killed the job, so the output has no "convergence NOT achieved" line. It has no converged
  SCF either, so `trusted_energy_ev` returns None.
- It does not count and is not rerun (amendment 11).

**Fe0_OH single points at r11 step 2 (accepted energy -5161.31337660 Ry), final tally:**

| Point | Iterations | Result | Landed in | E - accepted (mRy) | Counts |
|---|---|---|---|---|---|
| C1 | 200 | unconverged | - | - | no |
| C2 | 157 | converged | C7 | -0.013 | yes |
| C3 | 200 | unconverged | - | - | no |
| C4 | 147 | converged | C7 | -3.311 | yes |
| C5 | 147 | converged | C5 | -5.167 | yes |
| C6 | 200 | unconverged | - | - | no |
| C7 | 188 (timeout) | unconverged | - | - | no |

All three conditions for the readout now hold:
- the single points have ended;
- Ni0_OOH has converged (r7);
- Fe0_OH is accepted under amendment 22.

The readout runs next, once, with the registered command (`--model u0`, default paths).

`results/` is gitignored, and the readout writes `results/film_pilot_2026-11-14/readout_u0.json`. That
path still holds the AWS readout of 2026-11-17 16:43 local, which is copied to
`readout_u0_aws-2026-11-17.json` first so it is kept.

SU: balance 2,855.9. The film jobs on Anvil, summed from sacct, used 20.17 h x 48 cores = 968.1 SU,
which matches the balance drop of 968.2 since the start. That leaves 832 of the 1,800 cap.

## Readout: V1 passes (2026-11-18 ~09:55Z; the first eta of the Anvil continuation)

**Run:**
- Command: `film_pilot_readout.py --model u0 --runs D:/sts-electrocatalyst/film_pilot/out/runs`. It ran
  once and exited 0.
- Results: `results/film_pilot_2026-11-14/readout_u0.json`, md5 4b2d683e.
  - Copies on D: `film_pilot/out/readout_u0_anvil-2026-11-18.json` and its console log `.log`
    (md5 404fbc21).
  - The AWS readout of 2026-11-17 is kept as `readout_u0_aws-2026-11-17.json` (md5 6c5464cf), in both
    places.

**Runs used:**
- Ni0_OOH: r7, TRUSTWORTHY, 6 steps, *OOH intact, all parallel.
  - The chain note says r7 "did not start from r6's last geometry". The reason is that r6's step-12 SCF
    completed without forces (see "r7's first SCF").
  - r7 is the converged run, so it is used under either branch of the rerun rule.
- Fe0_OH: r11, accepted at step 2 under amendment 22 (dE -0.0242 mRy, largest free-atom force
  component 0.00306 on H35). C7, *OH intact.
  - The output's QC label is POISONED, which comes from step 3's unconverged SCF. The readout uses the
    accepted step-2 energy, as amendment 22 registers.
- The other V1 states are unchanged since the AWS readout, all TRUSTWORTHY:
  - NiOOH: slab_r2, Ni0_OH, Ni0_O_r2.
  - Ni(Fe)OOH: slab (C1), Fe0_O_r2 (C5), Fe0_OOH (C6).
  - Gas references: H2O, H2.

**Energies entering each readout:**
- Fe0_OH: the lowest readout uses C5's point, -70223.31621 eV, 0.0703 eV below the relaxed C7 energy.
- Fe0_OOH: the lowest readout uses C2's point, its own C2 solution, 0.0153 eV below the relaxed C6
  energy.
- Every other state uses its relaxed energy in both readouts.

| Site | Readout | dG *OH | dG *O | dG *OOH | Steps 1-4 (eV) | eta (V) | Limiting step |
|---|---|---|---|---|---|---|---|
| NiOOH Ni0 | both | 1.619 | 3.808 | 4.481 | 1.619 / 2.189 / 0.673 / 0.439 | **0.959** | 2 (*OH -> *O) |
| Ni(Fe)OOH Fe0 | lowest | 1.148 | 2.363 | 3.970 | 1.148 / 1.215 / 1.607 / 0.950 | **0.377** | 3 (*O -> *OOH) |
| Ni(Fe)OOH Fe0 | as relaxed | 1.218 | 2.363 | 3.986 | 1.218 / 1.145 / 1.623 / 0.934 | **0.393** | 3 (*O -> *OOH) |

**Verdicts:**
- V1 holds in the lowest readout (0.377 < 0.959) and in the as-relaxed readout (0.393 < 0.959).
- The two readouts agree, so under rule 4 the registered V1 is **pass**.
- V2 is not evaluable (CoOOH, out of scope).

**Own-configuration checks** (rule 2; reported, not a gate):
- Ni(Fe)OOH slab: 0.0 mRy. Five targets land in C1 within 0.003 mRy.
- Fe0_OH: there is no own check, because the C7 point did not converge. Two other points landed in
  C7:
  - C2, at -0.012 mRy, reproduces the relaxed solution.
  - C4, at -3.31 mRy, is a second C7-labelled solution. Its Ni30 moment is +0.30 against -0.20 in the
    relaxed solution; the 0.25 muB cutoff gives both the same label.
- Fe0_O: C2 landed in C5 at +0.001 mRy.
- Fe0_OOH: C3 landed in C6 at +0.006 mRy.

**Arithmetic check:** dG and eta were recomputed from the JSON energies with plain computational
hydrogen electrode references (`verify_readout.py`, outside the repo). The implied ZPE - TS terms are
the same at both sites: 0.35, 0.05 and 0.40 eV. Every eta is reproduced to 1 meV.

**How robust the margin is:**
- eta_Ni - eta_Fe is 0.582 V in the lowest readout and 0.566 V in the as-relaxed readout.
- Fe0_OH does not set eta_Fe. That state needed amendment 22 and is configuration-sensitive at 0.070
  eV.
  - It enters only steps 1 and 2.
  - dG *OH would have to move by +0.41 or -0.39 eV before either step limits.
  - It would have to move by about +/-1.0 eV to change V1.
- Fe0_OOH's lowest-vs-relaxed difference (-15 meV) moves eta_Fe by 0.016 V.
- Most of the difference comes from *O. It binds 1.45 eV more strongly at Fe0 than at Ni0 (dG 2.363
  vs 3.808 eV).
  - That shortens the Fe site's *OH -> *O step and moves its limit to *O -> *OOH.
  - *OH is also 0.40-0.47 eV more strongly bound at Fe0.

**What this does not establish:**
- One level of theory: PBE, U = 0 (amendment 9). Absolute eta values depend on U, and the PBE+U runs
  were superseded. V1 is an ordering claim at this level only.
- One cell, one Fe position and one coverage.
- The NiOOH states were not probed with configuration single points; they are all parallel
  throughout.
  - Among the Ni(Fe)OOH points, the energies of other configurations spread up to 0.23 eV.
  - Flipping V1 through Ni0 would take a configuration effect of about 0.57 eV on its *OH -> *O step.
    That is not ruled out by a calculation, only by scale.
- Fe0_OH is accepted at 3.06e-3 against forc_conv_thr 2e-3, under amendment 22's noise-aware bound.
  C5's energy is an upper bound, since its Fe force is 0.0091.
- dG *OOH - dG *OH is 2.86 eV at Ni0 and 2.77-2.82 eV at Fe0. That is below the commonly quoted
  *OH/*OOH scaling value of about 3.2 eV. Hydrogen bonding of *OOH to lattice O would be one
  explanation; it was not tested here.

**Closure:** amendment 11 ends the pilot's V1 with this readout. There are no new relaxations, and the
unconverged single points (C1, C3, C6, C7) are not rerun. Anvil: 968.1 of 1,800 SU.

## Amendment 23: two follow-up checks of V1 (2026-11-18 ~15:45Z, before any follow-up energy existed)

Frank, 2026-11-18: "go ahead with the follow ups". These are the two follow-ups named after the readout:
(A) the NiOOH states in other magnetic configurations, and (B) the ordering with Hubbard U. Both are
fixed-geometry single points. Neither reruns an SCF that ran, and neither adds a relaxation. The
readout above (891cc664) and its verdict stand until A or B changes them under the rules below.

### A. NiOOH configuration single points (U = 0)

Which states. At Ni0 the steps are s1 = dG(*OH) = 1.619, s2 = dG(*O) - dG(*OH) = 2.189,
s3 = dG(*OOH) - dG(*O) = 0.673 and s4 = 4.92 - dG(*OOH) = 0.439 eV. A single point can only lower a
state's lowest energy, by some delta >= 0:
- Lowering the slab raises every dG by delta: s1 rises, s4 falls, s2 and s3 do not change.
- Lowering *OOH lowers s3 and raises s4. s2 does not change.
- Neither can lower eta_Ni0 below s2 - 1.23 = 0.959 V, so the slab and *OOH are not probed.
- Lowering *O lowers s2 and raises s3. Lowering *OH lowers s1 and raises s2.
- The as-relaxed readout does not use single points, so V1 can change only in the lowest readout.
  There eta_Fe0 is 0.377 V (largest step 1.607 eV), and eta_Ni0 drops below it only if all four
  steps fall below 1.607 eV:
  - *OH must drop by more than 0.012 eV (s1);
  - *O must drop by more than 0.582 eV plus *OH's drop (s2), and by less than 0.934 eV (s3).
  So V1 changes only if *OH and *O both have lower configurations, *O's by about 0.6 eV or more.

Configurations. These are the Ni(Fe)OOH candidates C1-C7 (`make_cfg_sp.sh`) carried over to NiOOH, with
the site Ni (atom 6) taking Fe's role:
- C1: site +, Ni 5, 29, 30 -
- C2: site -
- C3: site +, Ni 5, 29 -
- C4: site +, Ni 30 -
- C5: site -, Ni 30 -
- C6: site +, Ni 5 -
- C7: all parallel, which is both relaxed states' own pattern

A start is skipped when it equals the relaxed pattern on the metals that carry a sign in the relaxed
state (|m| >= 0.25 muB, rule 1's cutoff):
- Ni5's moment is -0.01 muB in both states, so C6 is the same as C7.
- The site's moment is -0.01 in *OH, so there C2 equals C7 and C5 equals C4.
- The site carries +1.16 in *O, and Ni30 +0.29 / +0.28 in the two states, so those starts are kept.

That leaves 8 single points:
- `u0__NiOOH__Ni0_OH`: C1, C3 and C4.
- `u0__NiOOH__Ni0_O_r2`: C1, C2, C3, C4 and C5.

Recipe: `make_cfg_sp.sh`'s, unchanged in substance:
- scf, conv_thr 1e-5, electron_maxstep 200, cold start, at the relaxed geometry;
- the relaxation's own mixing (beta 0.1, ndim 12, local-TF);
- Ni starts at +0.1 as in the relaxations. The antiparallel atoms, the site included where it is
  negative, are relabelled Ni2 at -0.1, with the same pseudopotential and U (1e-8).

Counting follows amendment 11. A converged point counts as the pattern it landed in. An unconverged
point does not count and is not rerun. Each state's lowest energy is the minimum of its relaxed energy
and its counting points.

Rule:
- The lowest-readout eta_Ni0 is recomputed from these energies; every other energy is the readout's.
- If V1 still holds in the lowest readout, V1 stays a pass.
- If it does not, V1 is configuration-sensitive under rule 4, and the pass is withdrawn.

### B. PBE+U single points at the U = 0 geometries

Why this check. The registered decision step was a Hubbard-U sensitivity check by single points on the
relaxed geometries (Zeng's suggestion). Since amendment 9 the model is U = 0, so the mirror of that
check is PBE+U single points on the U = 0 relaxed geometries.

States: the eight V1 states as the readout used them. The gas references are unchanged (no Hubbard
species).

| State | Run | Density the SCF starts from (U = 0, same geometry) |
|---|---|---|
| NiOOH slab | `u0__NiOOH__slab_r2` | kept final density (written 2 s before the run ended; no stored geometry) |
| NiOOH *OH | `u0__NiOOH__Ni0_OH` | kept final density (stored geometry = final block to 5e-11 A) |
| NiOOH *O | `u0__NiOOH__Ni0_O_r2` | kept final density (5e-11 A) |
| NiOOH *OOH | `u0__NiOOH__Ni0_OOH_r7` | r7's final save on Anvil scratch (5e-11 A) |
| Ni(Fe)OOH slab | `u0__NiFeOOH__slab` | kept final density (5e-11 A) |
| Ni(Fe)OOH *OH | `u0__NiFeOOH__Fe0_OH_r11`, accepted step 2 | the C2 point's save: the relaxed C7 solution at that geometry (-0.013 mRy; 5e-9 A) |
| Ni(Fe)OOH *O | `u0__NiFeOOH__Fe0_O_r2` | kept final density (written 2 s before the run ended) |
| Ni(Fe)OOH *OOH | `u0__NiFeOOH__Fe0_OOH` | kept final density (5e-11 A) |

Input (`src/dft/film_box/make_u_sp.py`): the state's U = 0 input at its final geometry (accepted, for
Fe0_OH). The staging diff shows it differs only in:
- calculation 'scf', prefix, outdir and pseudo_dir;
- startingpot = 'file', with the density's occup.txt and paw.txt;
- conv_thr 1e-5;
- mixing beta 0.05, ndim 20, local-TF for all eight. This is the setting that converged the hardest
  U = 0 SCFs. It changes only the path to the solution (amendment 2's precedent). The only earlier PBE+U
  SCF of NiOOH *O that started from a U = 0 density (`NiOOH__Ni0_O_r2`'s PBE+U stage, beta 0.1,
  ndim 12) was at 7e-5 Ry when amendment 7 stopped it at iteration 63;
- the U values, set to the registered PBE+U values (Dudarev, atomic projectors): Ni 6.2 eV (Ni2 6.2) and
  Fe 5.3 eV.

Starting from the state's own density carries its U = 0 moment pattern into the PBE+U SCF.

QC per state:
1. The SCF converged.
2. Every Ni is low-spin, |m| < 1.6 muB. At PBE+U, low-spin Ni is 1.24-1.42 and high-spin about 1.9, and
   each high-spin Ni costs about 0.75 eV (amendment 8).

A state that fails either is not evaluable at PBE+U and is not rerun. The sign pattern and the Fe
moment are reported. A pattern different from the state's U = 0 pattern is reported, and the energy is
still used.

Readout:
- CHE as registered: the same ZPE - TS terms and the same gas references.
- One readout: each state in its U = 0 relaxed solution, carried to PBE+U. The lowest-readout solutions
  of Fe0_OH (C5) and Fe0_OOH (C2's) are not carried over.
- A site whose slab is not evaluable is reported through its slab-independent steps (s2, s3), as a lower
  bound on its eta (amendment 4).
- The result is one of three: "ordering kept at PBE+U" (eta_Fe0 < eta_Ni0), "ordering reversed", or
  "not determined".

Interpretation:
- B does not change V1's verdict, which is a U = 0 claim.
- If the ordering is kept, V1 is reported as holding at U = 0, with the ordering kept in PBE+U single
  points at the U = 0 geometries.
- If it is reversed, V1 is reported as holding at U = 0 only, and the ordering is U-sensitive.
- B is not a PBE+U V1:
  - the geometries are not relaxed at U;
  - each state has one PBE+U solution, inherited from U = 0;
  - amendments 7-8b found PBE+U solutions 0.3-1.7 eV apart, so a PBE+U ground state is not established.

### Resources, cap, staging

- 16 jobs on `shared`: 48 ranks, `-nk 3`, a 2 h limit each, `anvil_film_scr.slurm` (scratch only).
- Rate on Anvil: 31-33 s and 0.43 SU per iteration (C1, C5, C6), so 200 iterations take about 110 min.
- Expected cost:
  - A: cold starts took 147-200 iterations on Anvil and 73-150 for NiOOH at U = 0 on AWS. At 30-86 SU
    each, the eight cost 240-690 SU.
  - B: warm starts, about 40-200 iterations. At 17-86 SU each, the eight cost 140-690 SU.
  - About 380-1,380 SU in all, most likely 700-800.
- The time limits bound the spend at 16 x 2 h x 48 = 1,536 SU.
  - That would take the CPU balance from 2,855.9 to no less than 1,320.
  - It passes amendment 21's 1,800 SU cap, which these checks were not part of.
  - Nothing beyond these 16 jobs runs without Frank: no reruns, relaxations or further configurations.

Readout (`src/dft/film_followup_readout.py`):
- It runs once, after all 16 jobs have ended, and writes `results/film_pilot_2026-11-14/followup_a23.json`.
- Every other energy comes from `readout_u0.json` (md5 4b2d683e). It first checks that it recomputes that
  readout's four etas from its energies.
- It was tested on stand-in outputs, so no follow-up energy exists yet:
  - With each U = 0 output standing in for its own PBE+U point, and the relaxed outputs standing in for two
    A points, it returns eta_Ni0 0.959 V, eta_Fe0 0.393 V (as relaxed) and 0.377 V (lowest). The
    ordering is "kept", and V1 "pass".
  - With the NiOOH slab missing and Fe0_OH unconverged, Ni0 becomes the bound s2 = 2.189 (0.959 V), Fe0
    is not evaluable, and the ordering is "not determined".

Staging (`src/dft/film_box/anvil_a23.sh stage`, local; nothing on Anvil has been written):
- Every check passed:
  - The configuration encodings are correct: atoms relabelled Ni2 at -0.1, every other Ni at +0.1.
  - Every input appears exactly once: prefix, calculation, conv_thr, outdir, pseudo_dir, mixing, maxstep
    and U lines.
  - A is a cold start, and B starts from file. No input has CRLF.
  - Positions equal the final block, or for Fe0_OH the accepted block 1, to 5e-9 A.
  - The densities' stored geometries match where they were stored.
- md5 of the inputs:
  - A23C1/C3/C4 `__u0__NiOOH__Ni0_OH`: 181ed28e, a2bf0578, 0b7129d1.
  - A23C1-C5 `__u0__NiOOH__Ni0_O_r2`: d1e2b7bf, 3f059bc7, 72e42322, 468c8d42, c4b5160b.
  - A23U `__u0__NiOOH__`: slab_r2 7c4228cb, Ni0_OH e2e3fdde, Ni0_O_r2 176cab55, Ni0_OOH_r7 7073dbea.
  - A23U `__u0__NiFeOOH__`: slab 9e0447b4, Fe0_OH_r11 eb267801, Fe0_O_r2 1a35ff60, Fe0_OOH 62b2bf55.
- At deploy:
  - The six kept densities are uploaded and checked by md5 (charge-density.hdf5, occup.txt, paw.txt).
  - The two Anvil densities are copied in place and checked with cmp.
  - Each input's md5 is checked on Anvil before its sbatch.

### Deployed (2026-11-18 15:44-15:47Z, after this record, 3e95b933, and the code, bd7e1d63)

- A: jobs 22297447 (C1), 22297450 (C3) and 22297453 (C4) for Ni0_OH, and 22297454-22297459 (C1, C2, C3,
  C4, C5) for Ni0_O, submitted at the first pass.
- B: the first pass stopped at its first density check, `A23U__u0__NiOOH__slab_r2`. The hashes were
  equal; the check compared whole lines, and Windows md5sum writes `*name` where Linux writes `name`.
  - That job had not been submitted. Its scratch directory held only the uploaded input and density, and
    it was removed.
  - The comparison now strips the `*`, and `ONLY=` deploys a subset.
  - The eight B jobs were then deployed: 22297464 (NiOOH slab), 22297469 (Ni0_OH), 22297476 (Ni0_O),
    22297477 (Ni0_OOH), 22297480 (Ni(Fe)OOH slab), 22297482 (Fe0_OH), 22297491 (Fe0_O) and 22297492
    (Fe0_OOH).
  - Every density md5 matched, and the two Anvil copies passed cmp.
- On Anvil, all 16 input md5s equal the staged ones above. All 16 jobs are PENDING (Priority).
- `mybalance` at 15:47Z: 2,855.9 SU.

### A's eight points have ended (2026-11-18 17:20Z; no follow-up readout yet)

All eight converged. Each is pulled to `D:/sts-electrocatalyst/film_pilot/out/runs/`, and the md5s of
the `.in` and `.out` match Anvil. Energies are relative to the state's relaxed U = 0 energy at the same
geometry. Patterns use the 0.25 muB cutoff, relative to atom 1.

| State | Point | Iterations | Landed in | E - relaxed (meV) | `.out` md5 |
|---|---|---|---|---|---|
| Ni0_OH | C1 | 107 | Ni29, Ni30 antiparallel (-0.67, -0.27) | +11.0 | 0106d38c |
| Ni0_OH | C3 | 89 | Ni29 antiparallel (-0.70) | +18.4 | 73e56f32 |
| Ni0_OH | C4 | 77 | Ni30 antiparallel (-0.33), its target | **-16.0** | cf59bd1c |
| Ni0_O | C1 | 53 | Ni29 antiparallel (-0.67) | +56.5 | 9b2dac6b |
| Ni0_O | C2 | 63 | all parallel, the relaxed pattern (site +1.17) | 0.0 | 845ce332 |
| Ni0_O | C3 | 51 | Ni29 antiparallel (-0.69) | +34.2 | cbf21dac |
| Ni0_O | C4 | 52 | all parallel (Ni30 -0.17, below the cutoff) | +9.5 | db8bcc57 |
| Ni0_O | C5 | 52 | site -1.08, Ni30 -0.35, its target | +6.2 | 9a690beb |

- Every point counts (amendment 11).
  - Ni0_OH's lowest energy is now C4's, 16.0 meV below the relaxed one.
  - Ni0_O's lowest energy stays the relaxed one: no point lands below it.
- C2's start had the site antiparallel, yet it landed back in the relaxed solution at 0.0 meV. That
  reproduces the relaxed energy from a different cold start.
- Under A's rule, V1 can change only if *O drops by more than 0.582 eV plus *OH's drop. *O did not drop,
  so A cannot change V1.
  - The recomputed lowest-readout eta_Ni0 is the follow-up readout's job. It runs once, after B ends.
- Run times were 28-77 min (C1 for Ni0_OH, 107 iterations), well under the estimate.
- B at 17:19Z:
  - The NiOOH slab converged (46 iterations).
  - Ni0_OH is at 5.2e-4 Ry after 128 iterations, flat for the last tens of iterations.
  - Ni0_O started at 17:15Z.
  - The five Ni(Fe)OOH-side and Ni0_OOH points are pending.
- `mybalance` at 16:49Z: 2,570.7 SU (285.2 spent since deploy).

## Follow-up readout (2026-11-18 ~20:20Z): A keeps V1 a pass; B is not determined

**Run.** All 16 jobs had ended by 20:04Z, and every output is pulled with md5s equal to Anvil's.
- Command: `film_followup_readout.py` with the default paths. It ran once and exited 0.
- Its base is `readout_u0.json` (md5 4b2d683e).
- Result: `results/film_pilot_2026-11-14/followup_a23.json`, md5 de45dace. A copy and the console log
  are in `D:/sts-electrocatalyst/film_pilot/out/` as `followup_a23_anvil-2026-11-18.{json,log}`.

**A (NiOOH configurations, U = 0).**
- Ni0_OH: the lowest is C4's point, -15.97 meV. Ni0_O: the lowest stays the relaxed energy, since C2 lands
  in it at +0.02 meV and no point lies below it.
- At Ni0 (lowest readout) the steps are 1.603 / 2.205 / 0.673 / 0.439 eV, so eta_Ni0 is **0.975 V**
  (it was 0.959). The limiting step is still 2 (*OH -> *O).
- eta_Fe0 (lowest) is 0.377 V. **V1 holds in the lowest readout (0.377 < 0.975) and as relaxed (0.393 <
  0.959), so V1 stays a pass.**
- The lower *OH raises eta_Ni0. The margin in the lowest readout grows from 0.582 to 0.598 V; the
  as-relaxed margin is unchanged at 0.566 V.

**B (PBE+U single points at the U = 0 geometries).** Three of the eight are evaluable.

| State | Job end | Iterations | Result | Last 50 iterations: SCF accuracy (Ry), E range |
|---|---|---|---|---|
| NiOOH slab | COMPLETED | 46 | converged; all parallel, Ni max 1.41 | - |
| NiOOH *OH | COMPLETED | 200 | **not converged** | 2.6e-4 to 8.2e-4; 0.46 mRy |
| NiOOH *O | COMPLETED | 200 | **not converged** | 2.1e-5 to 4.9e-5; 0.64 mRy |
| NiOOH *OOH | COMPLETED | 200 | **not converged** | 2.1e-4 to 4.5e-4; 0.63 mRy |
| Ni(Fe)OOH slab | COMPLETED | 39 | converged; C1 kept, Fe +3.08, Ni max 1.53 (Ni30) | - |
| Fe0_OH | TIMEOUT (2 h) | 78 | **not converged** (slow node, ~70 s per iteration) | 8.8e-5 to 2.5e-2; 2.07 mRy |
| Fe0_O | COMPLETED | 76 | converged; Fe -2.08, Ni max 1.40; Ni30 -0.30 -> -0.14, so the pattern goes from C5 to C2 (reported) | - |
| Fe0_OOH | TIMEOUT (2 h) | 173 | **not converged** | 1.9e-4 to 5.6e-4; 2.06 mRy |

- Both sites are not evaluable. Every adsorbate state at Ni0 failed, as did *OH and *OOH at Fe0. **The
  ordering at PBE+U is "not determined".**
- Under amendment 23, V1 (U = 0) is unchanged. No B point is rerun.
- The unconverged energies are not used, and no PBE+U dG has been computed from them.
- pw.x prints per-site moments only for a converged SCF. So the low-spin QC cannot be applied to the five
  failed points; only their total magnetization is known, and it was steady over the last 50 iterations.

What B's failure shows:
- Started from the U = 0 densities, the PBE+U SCFs of the adsorbate states sit on floors of 2e-5 to 8e-4
  Ry. Those floors are 2-80 times conv_thr, while the two slabs and Fe0_O converge in 39-76 iterations.
- The registered conv_thr (1e-5, the U = 0 value) was too strict for PBE+U here. Amendments 3-7 had
  already shown PBE+U floors of 1e-6 to 1e-4 Ry in these slabs.
- The 2 h limit also stopped two points before 200 iterations, Fe0_OH on a node running at about half
  speed.
- This is the fourth PBE+U attempt on NiOOH *O that does not converge (cold, ramped and low-spin starts
  in amendments 5-8b, and this one). It came closest: 2-5e-5 Ry.

**Spend.** The 16 jobs used 785.6 core-hours (sacct), and `mybalance` reads 2,070.4 SU, so 785.5 since
deploy. That is inside the expected 700-800 SU and under the 1,536 bound. The CPU allocation has 2,070.4
SU left.

**What happens to B goes back to Frank.** Nothing further runs without his decision.

## Amendment 24: B's five failed states rerun to a 1e-3 Ry target from settled densities (2026-11-18 ~20:55Z, before any PBE+U dG or eta existed)

Frank, 2026-11-18: "c". He chose to rerun the five failed points with a looser target, under a rule
fixed before any eta is seen, and a cap of 600 SU. The three options went to him after the follow-up
readout. No PBE+U dG or eta has been computed from any B energy.

### One change to (c) as offered

The offer was conv_thr 1e-3 Ry from the same U = 0 starts, with a 2.5 h wall. Before staging, the
amendment-23 traces of the five failed SCFs were checked: per-iteration energies only, no dG. Each SCF
falls below 1e-3 Ry at some iteration, and pw.x would stop there. The table shows how far that energy
sits from what the same SCF reached later:

| State | First < 1e-3 at iteration | Later iterations, relative to that energy |
|---|---|---|
| NiOOH *OH | 44 of 200 | -0.86 to 0 mRy |
| NiOOH *O | 39 of 200 | -0.91 to 0 mRy |
| NiOOH *OOH | 25 of 200 | -1.41 to 0 mRy |
| Fe0_OH | 39 of 77 | -0.41 to +0.75 mRy |
| Fe0_OOH | 25 of 172 | **-7.79 to 0 mRy**, still falling about 0.3 mRy per 15 iterations at the end |

So a 1e-3 stop from the U = 0 start would put Fe0_OOH about 0.1 eV above where its SCF was heading.
The rerun therefore starts the 1e-3 SCF from a density that has already settled.

### Rerun

Stage 1, a settling run. It is the amendment-23 input unchanged (conv_thr 1e-5), run until it reaches
its electron_maxstep and writes its density:
- NiOOH *OH, *O and *OOH: stage 1 is the amendment-23 run itself. Each ran 200 iterations, and its save
  now holds that final density (md5 9d366f22, 97eaa8ee, 93cba936; the U = 0 starts were bb380348,
  525afdfa and r7's).
- Fe0_OH and Fe0_OOH timed out in amendment 23 and wrote nothing. They start again from the same U = 0
  densities: the C2 point's save, cmp-equal to amendment 23's copy; and Fe0_OOH's kept density,
  e1baf5e0 / 5ba13638 / d4d5444e, unchanged on Anvil.
  - `A24S__u0__NiFeOOH__Fe0_OH_r11`: electron_maxstep 200, 4 h wall.
  - `A24S__u0__NiFeOOH__Fe0_OOH`: electron_maxstep 400, 6 h wall. It was still falling at 172.

Stage 2, the measurement. For each of the five, `A24U__RUN` is the amendment-23 input with conv_thr
1.0d-3 and electron_maxstep 100. It restarts from stage 1's written density, with a 30 min wall.
Nothing else changes: U, mixing, smearing and geometry are as in amendment 23.

QC per state (`src/dft/film_a24_readout.py`):
1. If stage 1 converged at 1e-5, its energy is used with a band of 0. Otherwise stage 1 must have run to
   its electron_maxstep, and its last 50 energies must span at most 2 mRy.
2. Stage 2 converged.
3. |E(stage 2) - mean of stage 1's last 50| <= 2 mRy.
4. Every Ni is low-spin, |m| < 1.6 muB, from stage 2's printed moments.

A state that fails any of these is not evaluable, and nothing is rerun. The sign pattern and Fe moment
are reported. The three states that converged in amendment 23 (both slabs and Fe0_O) are used as they
are, with a band of 0.

Band and decision:
- Each rerun state carries +/- 2 mRy (27.2 meV). That is the largest last-50 span seen in amendment 23
  (2.07 mRy), rounded down to the stationarity limit. It replaces the +/- 14 meV offered with (c).
- A step's band is the sum of the bands of the two states in it; the gas references are exact.
- eta is an interval: from the largest lower step end to the largest upper step end, minus 1.23.
- The ordering is "kept" if eta_Fe0's upper end is below eta_Ni0's lower end, and "reversed" if
  eta_Fe0's lower end is at or above eta_Ni0's upper end. Otherwise it is "not determined".
- Resolution, if the limiting steps stay where they are at U = 0:
  - Ni0's *OH -> *O step involves two rerun states, so it carries +/- 54 meV.
  - Fe0's *O -> *OOH step involves one rerun state (Fe0_O converged), so it carries +/- 27 meV.
  - The ordering can then be called if the PBE+U margin exceeds about 0.08 V. With other limiting steps
    the threshold would lie between 0.05 and 0.11 V.
- Amendment 23's interpretation stands. V1 (U = 0) is unchanged. A "kept" or "reversed" is the ordering
  with U at the U = 0 geometries, with each state's configuration inherited from U = 0.

Tests of the readout. They use U = 0 stand-ins only, so no PBE+U energy was read:
- Every point a converged U = 0 output: eta 0.959 / 0.393 V, "kept".
- The banded path, with synthetic stage-1 traces spanning 0.8 mRy and U = 0 stage-2 points:
  - Ni0 0.959 [0.905, 1.013] V, step bands 27 / 54 / 54 / 27 meV.
  - Fe0 0.393 [0.365, 0.420] V, "kept".
- Fe0_OOH's synthetic trace widened to 3 mRy: Fe0 is not evaluable, and the ordering "not determined".

Cost:
- Expected: stage 1 about 107 SU (Fe0_OH) and 215 SU (Fe0_OOH), and stage 2 about 10 SU each, so about
  370 SU.
- Bound by the walls: 192 + 288 + 5 x 24 = 600 SU, Frank's cap. Balance 2,070.4.

Order:
- `anvil_a24.sh deploy1` submits both stage-1 runs and the three NiOOH stage-2 runs.
- `deploy2 RUN` submits a Fe-side stage 2 only after its stage 1 has ended at its maxstep (or
  converged). Its density is copied and checked with cmp.
- The readout runs once, after all seven have ended.

Staging (`src/dft/film_box/anvil_a24.sh stage`, local, from the staged amendment-23 inputs). Each input
differs only in prefix and outdir, plus electron_maxstep 400 for Fe0_OOH's stage 1, or conv_thr
1.0d-3 and electron_maxstep 100 for the stage-2 runs. md5:
- A24S Fe0_OH_r11 16332440, Fe0_OOH 346d2b9c.
- A24U Ni0_OH 8ab2f0c6, Ni0_O_r2 2321674a, Ni0_OOH_r7 a4656e98, Fe0_OH_r11 a23b4032, Fe0_OOH f175a386.
- Code: `fb89ac23`.

Deployed with `deploy1`, after this record (75c09cb9). Every density was copied on Anvil and cmp-equal
to its source (charge-density / occup / paw md5 below), and each input's md5 was checked before its
sbatch.
- 22302575: `A24S__u0__NiFeOOH__Fe0_OH_r11`, 4 h (f5b03178 / 61eeb3a1 / 50593fe8, the C2 point's save).
- 22302578: `A24S__u0__NiFeOOH__Fe0_OOH`, 6 h (e1baf5e0 / 5ba13638 / d4d5444e).
- 22302579: `A24U__u0__NiOOH__Ni0_OH`, 30 min (9d366f22 / fd4d249c / d10f97c8).
- 22302580: `A24U__u0__NiOOH__Ni0_O_r2`, 30 min (97eaa8ee / 4c7927e6 / 87ee8589).
- 22302586: `A24U__u0__NiOOH__Ni0_OOH_r7`, 30 min (93cba936 / e42bd0d9 / f4cafa97).

## Compute
- 83 Sciences AWS account (Frank, 2026-11-14), c7a.48xlarge (192 cores, 384 GiB), on-demand,
  us-east-1; 6 jobs x 30 ranks (-nk 3); gas jobs 8 ranks. Box scripts: `src/dft/film_box/`.
- Cost estimate before launch: ~8,000-13,000 core-hours (~42-68 instance-hours), uncertain by ~2x;
  the first hour's SCF timing is used to re-estimate. Hard cap 48 h (box stops itself).
- Production is intended for Anvil (CHE260157 supplement request, `access-supplement-request-2026-11-14.md`).
