# S0 gate (d) — Hessian timing + sigma_F probe in 2x1v

Built 2026-08-16 by the S0 d+g builder. Registered under docs/43 AMENDMENT 7 (A7.4,
Zenodo 10.5281/zenodo.21963144) and the S0 table of
docs/research/2026-08-15-lit-sweep-round2-synthesis.md (line 192). 1 job.

## Registered decision rule (quoted)

Synthesis S0 table, gate (d): "1 displacement SCF, 2x1v, `conv_thr 1e-10`, `nosym` ...
Must report three things, not one: wall clock (validates the ~2.4 h repricing),
**whether `conv_thr 1e-10` is actually REACHED in 2x1v**, and the sigma_F it delivers
there. `build_hessian_pilot.py`'s table was measured at 21 atoms / 32 k / 1x1; the 19
built 1C decks are 2x1v (42 atoms, 16 k). If 1e-10 is not reached, the minimum claim
is struck **before** decks launch."

docs/43 A7.4 row (line 1387): "(d) Hessian timing AND sigma_F in 2x1v (`conv_thr
1e-10`) | wall clock; whether 1e-10 is REACHED at 42 atoms/16 k; sigma_F delivered |
launching 19 decks whose minimum claim is unscorable"

Recorded tension (requirements.md flag 3, carried verbatim): the S0 table row says
"42 atoms, 16 k"; the built Cr_hess decks have nat = 39. The decks are authoritative;
the discrepancy is recorded, not repaired. (16 k is correct: 4 4 1 with nosym/noinv.)

## Deck

| deck | jobs | nk | est box-h |
|---|---|---|---|
| s0_OOH__2x1v_mir__hess_a37xp.in | 1 | 4 | 2.5 |

VERBATIM BYTE COPY of runs/probe/Cr_hess/s0_OOH__2x1v_mir__hess_a37xp.in — zero
edits. md5 of source and copy both 9a8ec3b6f6e16b3808e3b2756d0a71e6.

WHY THIS DECK (requirements.md gate-(d) adjudication): a true DISPLACED deck — atom 37
(the *OOH binding O, adsorbate_indices_1based = [37,38,39]), +x, displacement
+0.0099999965 A per runs/probe/Cr_hess/hess_manifest.json — because the displaced
decks are the representative job class (18 of the 19); the undisplaced hess_ref sits
at the parent minimum, starts its SCF closer to the converged density, and would
understate displaced-deck SCF cost.

Deck class parameters (hess class, all frozen — see s0spec protocol section 1, class E):
calculation='scf', nat=39, ntyp=3, 80/640, smearing mv 0.01, nosym=.true. +
noinv=.true. (all 19 hess decks including the ref), nspin=2 with
starting_magnetization(1)=0.6, conv_thr=1.0d-10, local-TF 0.3, electron_maxstep=120,
NO max_seconds (absent on all 19 hess decks by design), K_POINTS automatic 4 4 1 0 0 0
(-> 16 k with nosym), HUBBARD (atomic) / U Cr-3d 3.7000 after K_POINTS.

## Geometry provenance

s0_OOH__2x1v_mir__hess_a37xp.in: verbatim copy of
runs/probe/Cr_hess/s0_OOH__2x1v_mir__hess_a37xp.in (commit 51c36a6 build, HOLD
RELEASED 2026-08-13 on ADOPT_2X1V), itself frozen from the **final BFGS geometry of
runs/probe/Cr_cellsym/s0_OOH__2x1v_mir.out** (converged, E = -3188.70497020 Ry,
GATE-1 AGREE via its __g1 child, part of the 22/22 block; image contact
3.983 A at 2x1v vs 1.338 A at 1x1), with atom 37 displaced +0.01 A (nominal) in x.

## Run

queue_r1.sh manifest line (NP must be an exact multiple of nk = 4):

    s0/d_hess_timing s0_OOH__2x1v_mir__hess_a37xp .in 4

`JOB DONE` is NEVER success by itself. Drain marker: QUEUE_ALL_DONE.

## Scoring recipe (three recorded deliverables — this gate is a measurement, not pass/fail on one number)

Let OUT = s0_OOH__2x1v_mir__hess_a37xp.out. Use `grep -a` throughout (Cr outputs can
contain stray binary bytes).

1. **Wall clock** vs the ~2.4 h repricing (round-1 synthesis line 71: "19 pre-built
   Cr 1C Hessian decks ... repriced at ~2.4 h each ~= 46 box-h"):
   - `grep -a "PWSCF.*WALL" OUT | tail -1`  (final "PWSCF : ... CPU ... WALL" line)
   - cross-check: the runner `DONE s0/d_hess_timing/s0_OOH__2x1v_mir__hess_a37xp ... <t>s` log line.
   - Record: measured wall clock, NP/nk used, and the implied 19-deck battery cost
     (19 x measured) replacing the ~46 box-h estimate.

2. **Is conv_thr 1.0d-10 REACHED** within electron_maxstep = 120 (yes/no):
   - `grep -ac "convergence NOT achieved" OUT`  -> MUST be 0
   - `grep -a "convergence has been achieved in" OUT`  -> must print (iteration count recorded)
   - achieved accuracy: `grep -a "estimated scf accuracy" OUT | tail -1`  -> < 1.0E-10 Ry
   - final energy present: `grep -a "^!" OUT | tail -1`

3. **sigma_F delivered** at 1e-10 in 2x1v:
   - Record the full final force block:
     `grep -a -A 45 "Forces acting on atoms" OUT | tail -50` (per-atom fx fy fz, Ry/au)
     and `grep -a "Total force" OUT | tail -1`.
   - Single-SCF estimate (the registered order-of-magnitude model,
     build_hessian_pilot.py "Trap 1": sigma_F ~ C*sqrt(eps), C ~ 1 Ry/bohr):
     sigma_F_est = sqrt(eps_final) Ry/bohr with eps_final from recipe 2. Design value
     to compare: sigma_F = 1.0e-5 Ry/bohr at conv_thr 1e-10 (18 cm^-1 one-sigma on O;
     the verdict scores at 3 sigma, i111 cm^-1 floor on an H-carried mode).
   - The DEFINITIVE measured sigma_F remains hessian_analyze.py Q4a (rms of the
     Hessian asymmetry H_ij - H_ji x delta) over the full battery; this gate records
     the single-SCF feasibility read, not a substitute.

## Recorded on each outcome (requirements.md, binding)

- **"1e-10 reached"**: the 1C battery (remaining 18 decks in runs/probe/Cr_hess) may
  launch after the LIT drain; the repriced wall clock is recorded. Because this deck
  is byte-identical to the battery's own a37xp deck, its converged .out may be copied
  to runs/probe/Cr_hess/ so the battery does not re-run this job (record if done).
- **"1e-10 NOT reached"**: the Hessian MINIMUM claim is struck BEFORE the decks launch
  (F6 verbatim); the deliverable narrows to "the mirror-breaking mode is real";
  recorded as a capability result. The battery may still launch under the narrowed
  claim only via a recorded decision.

## DEVIATION lines

None. The deck is run verbatim as built; conv_thr 1.0d-10, electron_maxstep 120,
nosym+noinv on a mirror-arm-derived geometry, and the absence of max_seconds are the
frozen hess-class values (all 19 built decks), not deviations.
