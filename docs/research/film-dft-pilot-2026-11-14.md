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

## Compute
- 83 Sciences AWS account (Frank, 2026-11-14), c7a.48xlarge (192 cores, 384 GiB), on-demand,
  us-east-1; 6 jobs x 30 ranks (-nk 3); gas jobs 8 ranks. Box scripts: `src/dft/film_box/`.
- Cost estimate before launch: ~8,000-13,000 core-hours (~42-68 instance-hours), uncertain by ~2x;
  the first hour's SCF timing is used to re-estimate. Hard cap 48 h (box stops itself).
- Production is intended for Anvil (CHE260157 supplement request, `access-supplement-request-2026-11-14.md`).
