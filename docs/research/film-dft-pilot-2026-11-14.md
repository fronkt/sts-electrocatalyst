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

## Compute
- 83 Sciences AWS account (Frank, 2026-11-14), c7a.48xlarge (192 cores, 384 GiB), on-demand,
  us-east-1; 6 jobs x 30 ranks (-nk 3); gas jobs 8 ranks. Box scripts: `src/dft/film_box/`.
- Cost estimate before launch: ~8,000-13,000 core-hours (~42-68 instance-hours), uncertain by ~2x;
  the first hour's SCF timing is used to re-estimate. Hard cap 48 h (box stops itself).
- Production is intended for Anvil (CHE260157 supplement request, `access-supplement-request-2026-11-14.md`).
