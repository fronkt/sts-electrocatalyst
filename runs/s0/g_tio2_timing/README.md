# S0 gate (g) — TiO2 2x1v nspin=1 timing

Built 2026-08-16 by the S0 d+g builder. Registered under docs/43 AMENDMENT 7 (A7.4,
Zenodo 10.5281/zenodo.21963144) and the S0 table of
docs/research/2026-08-15-lit-sweep-round2-synthesis.md (line 195). 1 job.

## Registered decision rule (quoted)

Synthesis S0 table, gate (g): "TiO2 2x1v nspin=1 timing | 1 adsorbate relaxation,
2x1v | 4 [box-h] | Replaces an extrapolated 3-6 h class with a measurement before S3
is costed."

There is NO pass/fail threshold — this gate is a measurement (requirements.md:
"Decision rule: none pass/fail — a measurement. Deliverables: wall clock, BFGS step
count, per-SCF time"). "If the relaxation fails to converge, that is itself a
recorded capability result for the TiO2 addition."

## Deck

| deck | jobs | nk | est box-h |
|---|---|---|---|
| s0_OOH__2x1v_off.in | 1 | 4 | 4.0 |

TiO2(110) 2x1v + *OOH, off-plane start, calculation='relax', per the requirements.md
gate-(g) adjudication: *OOH because it is the largest adsorbate, the worst-case member
of the class being priced, and the rung every S3 metal needs; nspin = 1 by omission
(gen_rutile.py: TiO2 is d0, mag = 0.0 — emitting nspin 2 on a closed shell doubles
cost and hands the SCF a second solution branch); NO HUBBARD card (U = 0.0 for Ti,
gen_rutile.py — "Materials Project applies no Hubbard U to Ti"); nosym=.true. +
noinv=.true. + a physical off-plane displacement (the off-arm protocol).

Frozen-protocol values carried: ecutwfc 80.0 / ecutrho 640.0; occupations 'smearing'
mv / degauss 0.01; mixing_mode 'local-TF' / mixing_beta 0.3; conv_thr 1.0d-6;
forc_conv_thr 2.0d-3; nstep 200; ion_dynamics 'bfgs'; ibrav 0;
pseudo_dir '/usr/share/espresso/pseudo'; K_POINTS automatic 4 4 1 0 0 0 (the frozen
2x1v mesh; also what the production kgrid_from_cell rule yields for this cell);
species H / Ti / O with H.pbe-rrkjus_psl.1.0.0.UPF, ti_pbe_v1.4.uspp.F.UPF (the
production Ti pseudo, runs/hp_tio2/scf__*.in + build_hp_validation.TI_UPF),
O.pbe-n-kjpaw_psl.0.1.UPF. nat = 39 (2 x 18 slab + 3 adsorbate), ntyp = 3, 14 fixed
atoms (7 per half, the docs/30 mid-plane-tolerance mask — same 7-of-18 pattern as the
production Cr/Ru 1x1 slabs).

noinv basis (requirements.md, binding): this deck carries the frozen noinv=.true.
protocol. Gate (b)'s verdict does NOT apply retroactively; if (b) has REPORTED its
pass before this deck launches, dropping noinv is permitted but MUST be recorded here,
because it changes the timing measurement's protocol basis. As built: noinv ON.

## Geometry provenance

GENERATED, not reused — **no TiO2 slab geometry, mask, or ELEMENTS entry exists
anywhere in the repo** (the only Ti decks are the 6-atom bulk cells in runs/hp_tio2).
This is the one S0 gate that needs a new geometry. Construction (builder script
`build_g_tio2.py`, kept in the session scratchpad `s0build/`; every step is the
repo's own machinery):

1. Bulk rutile TiO2: a = 4.5937 A, c = 2.9587 A, u = 0.30478 from
   src/dft/gen_rutile.py RUTILE["TiO2"] — the S0 requirements adjudication's
   parameter source. PROVENANCE FLAG CARRIED from gen_rutile.py: the
   Abrahams & Bernstein 1971 / Burdett 1987 attribution of these numbers is
   UNVERIFIED in-source and must be checked before they appear in the report.
2. (110) 1x1 slab cleaved exactly as src/hea_oer/surfaces_rutile.py
   build_rutile110_hea does for the production metals: pymatgen SlabGenerator,
   min_slab_size = 8.0, min_vacuum_size = 13.0, center_slab, lll_reduce,
   primitive=False; _pick_rutile110 (stoichiometric + symmetric, smallest cell);
   supercell (1,1) — the production endmember cell. Result: 18 atoms
   (same layer count as runs/Cr_slab / runs/Ru_anchor / runs/Ir_anchor slabs),
   1x1 cell 2.95870 x 6.49647284 x 25.98589137 A (x = c, y = a*sqrt(2), vacuum z);
   bottom half fixed with the docs/30 mid-plane tolerance -> 7 fixed atoms.
3. cus site from hea_oer.surfaces_rutile.cus_site_xy (n_sites=1):
   (x, y) = (0.000000, 4.872355); y_mirror = 4.872355 A (y of the cus Ti).
4. *OOH from hea_oer.surfaces_rutile.adsorbate_starts, member "pull1.70": the
   builder placement rigidly pulled in to M-O = 1.700 A (the median M-O across the
   DFT-verified metals). BUILD DECISION, recorded: the raw builder height lands the
   binding O ~3.1 A off the cus metal, the exact start that trapped Cr *O and
   desorbed *OOH on Mn/Fe/Ni in the 2026-07 campaign (docs/33 s5b, docs/34 s4b) —
   a desorbing trajectory would corrupt the timing measurement this gate exists to
   make. The 2x1v decks this gate prices start from already-bonded relaxed
   fragments, so the pulled-in start is the class-representative one. No registered
   value pins the start distance; PULL_TO's 1.70 is the repo idiom.
5. Off-plane start: fragment yawed 90 deg about the vertical axis through the
   binding O (build_cellsym_pilot.py YAW_DEG = 90 idiom, re-implemented verbatim in
   the builder script because build_cellsym_pilot's emitter path requires 1x1
   relaxed .out sources that do not exist for TiO2). Achieved max |dy| from the
   mirror = 1.400 A >= the registered 0.30 A minimum (docs/43 s2-A.1).
6. 2x1v assembly per build_cellsym_pilot.build_metal: slab + shift_x(slab,
   a1 = 2.9587) + adsorbate fragment ("1/2 ML, neighbouring cus vacant"); mask
   duplicated, adsorbate atoms free ("1 1 1"). Since no relaxed TiO2 slab exists,
   both halves are the same generated slab (for the production metals the halves
   are relaxed geometries; recorded, not hidden). Min adsorbate x-image contact
   5.917 A (cf. the 3.983 A the Cr 1C build accepted).
7. Emitted through src/dft/qe_slab.py write_slab_input (nosym=True) with a Ti
   ELEMENTS entry injected at runtime (pseudo ti_pbe_v1.4.uspp.F.UPF, U=0.0,
   mag=0.0, mass=47.867 — gen_rutile values; qe_slab.py itself was NOT edited);
   max_seconds then inserted into &CONTROL per the cellsym emitter idiom.

Deck md5: 6d5643122c1de3077ecd7d7d43548021.

## Run

queue_r1.sh manifest line (16 k-points with nosym; nk = 4 per the >= 12 k rule; NP
must be an exact multiple of 4):

    s0/g_tio2_timing s0_OOH__2x1v_off .in 4

If the max_seconds cap fires, mark the wave `# EXPECT_CAP` on relaunch and restart
per the stale-.out rules; the summed wall clock is then the timing number.
`JOB DONE` is NEVER success by itself.

## Scoring recipe (deliverables — measurement gate)

Let OUT = s0_OOH__2x1v_off.out.

1. **Converged?** `grep -a "bfgs converged" OUT` and
   `grep -ac "End of BFGS Geometry Optimization" OUT` (must be 1);
   `grep -ac "convergence NOT achieved" OUT` (0 = no SCF failures);
   final energy `grep -a "^!" OUT | tail -1`. Non-convergence is itself the
   recorded capability result for the TiO2 addition, not a discard.
2. **Wall clock**: `grep -a "PWSCF.*WALL" OUT | tail -1`; cross-check the runner
   `DONE s0/g_tio2_timing/s0_OOH__2x1v_off ... <t>s` log line. Record NP/nk.
3. **BFGS step count**: `grep -ac "Total force" OUT` (= ionic steps, the
   build_cellsym_pilot count_ionic_steps rule).
4. **Per-SCF time**: wall clock / `grep -ac "total cpu time spent" OUT`
   (SCF-iteration count); also record wall clock / ionic steps (per-ionic-step
   time, the number the S3 cost model consumes).

Recorded either way: the measured 2x1v nspin=1 relaxation cost REPLACES the
extrapolated 3-6 h class in the S3 budget (the S3 costing input). The measured cost
includes slab-relaxation overhead absent from the S3 class (production 2x1v decks
are assembled from relaxed 1x1 halves; this deck's halves are the unrelaxed
generated slab) and is therefore an UPPER-BOUND timing; record it as such in the
S3 costing input. The GATE-1 __g1
child of this relaxation is an S3 obligation, NOT an S0 job. Gate (i)'s TiO2 cutoff
ladder is the tier-admission gate; a ladder failure voids this gate's tier relevance
(run (i)'s TiO2 arm first if scheduling allows — recommendation, not registration).

## DEVIATION lines

- DEVIATION: max_seconds = 28800 is sized from the REGISTERED ~4 box-h estimate for
  this gate via the cellsym emitter rule form max(7200, round(2.0 * est_h * 3600)),
  NOT from the build_cellsym_pilot measured-step cost model — that model requires a
  measured 1x1 ionic-step count for the metal, which does not exist for TiO2 and is
  precisely what this gate measures.
- Note (adjudicated, not a deviation — recorded for completeness): the slab was cut
  at the gen_rutile TiO2 internal parameter u = 0.30478 per the requirements.md
  adjudication, whereas the production Cr/Ru/Ir slabs were cut at
  surfaces_rutile._RUTILE_U = 0.305. No frozen TiO2 slab value existed to deviate
  from; the free layers relax and the fixed bottom retains the bulk-experimental
  positions either way.
