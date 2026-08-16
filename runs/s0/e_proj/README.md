# S0 gate (e) — ortho-atomic projector acceptance (2 SCFs, Cr *O, 1x1, U = 7.15 eV)

Built 2026-08-16 by the S0 a+e builder. Governing registrations: docs/43-prereg-week1-factorial.md
AMENDMENT 7 / A7.1 (P-PROJ) and A7.4 (Zenodo 10.5281/zenodo.21963144); docs/research/
2026-08-15-lit-sweep-round2-synthesis.md S0 table lines 182–202; adjudications: scratchpad spec
requirements.md gate (e).

## Registered decision rule (quoted)

> "Decision rule (S0): capability — the ortho-atomic deck is accepted by the build and its SCF
> converges. Secondary recorded number: E(atomic) − E(ortho-atomic) at identical geometry and
> U (a projector-delta data point, not yet an eta)."

Registered jobs (S0 table): "2 SCFs, Cr at U = 7.15 eV, 1x1 (matching A0), HUBBARD (atomic) vs
HUBBARD (ortho-atomic). ~2 box-h." Kill it prevents: silent import of a projector-mismatched
fifth grid point (Xu 2015 U = 7.15 eV was produced under a different projector; the campaign
measured a +1.45 eV projector shift in U but never the eta consequence at fixed U).

## What this gate is (statement required by the registration reconciliation)

This gate is FIRST an acceptance test: does this QE build accept the `HUBBARD (ortho-atomic)`
card at all — the build behavior is recorded either way (acceptance, rejection error text, or
non-convergence). The paired dE of these two decks is ONE point of P-PROJ. The full 4-state
pairing (2 projector sets x {slab, *OH, *O, *OOH} = 8 SCFs) runs LATER under the A0 budget per
A7.1 — these 2 S0 decks are reused as 2 of those 8; the remaining 6 SCFs are A0 jobs, NOT S0
jobs (requirements.md tension flag 1, reconciled).

PREDICTION on record (A7.1, quoted): "|d-eta(Cr)| > 0.10 V, falsified < 0.03 V". That
prediction is scored by the full A0 pairing, not by this gate; the S0 pair only establishes
capability and the single-state projector delta.

## Deck list

| deck | HUBBARD card | everything else |
|---|---|---|
| s0_O__u715_atomic.in | `HUBBARD (atomic)` / `U Cr-3d 7.1500` | byte-identical to runs/probe/Cr/s0_O__base.in except prefix |
| s0_O__u715_ortho.in  | `HUBBARD (ortho-atomic)` / `U Cr-3d 7.1500` | byte-identical to runs/probe/Cr/s0_O__base.in except prefix |

Common protocol (verbatim from the source deck): calculation='scf' fixed geometry, nat=19,
ntyp=2, 80/640, smearing mv 0.01, nspin=2, starting_magnetization(1)=0.6, local-TF 0.3,
conv_thr 1.0d-6, symmetry ON (no nosym/noinv — the ladder-deck idiom), K_POINTS automatic
9 4 1 0 0 0 (15 irreducible k-pts), cr_pbe_v1.5.uspp.F.UPF + O.pbe-n-kjpaw_psl.0.1.UPF,
HUBBARD card after K_POINTS. Verified byte-diff vs source: prefix line + HUBBARD line(s) only.
Ortho-atomic card syntax precedent: runs/hp_tio2/scf__ortho.in.

Naming: `u715` = U 7.1500 eV stated explicitly — the LIT-1 `u<scale>` multiplier vocabulary has
no registered token for the A7.1 fifth grid point (7.15/3.7 is not a clean scale; protocol.md
GAP 5 directs emitting the value directly with an explicit name).

## Geometry provenance (both decks)

ATOMIC_POSITIONS of runs/probe/Cr/s0_O__base.in, themselves the final BFGS geometry of
runs/Cr_slab/s0_O.out (runs/probe/Cr/probe_manifest.json: source_run runs/Cr_slab,
geometry_provenance "final"; note field: fixed-geometry single points on already-relaxed
structures — must not be reported as relaxed). This is the production-U-relaxed *O geometry the
A0/LIT-1 ladder idiom uses; the U=7.15 points are fixed-geometry single points on it, exactly
like the existing ladder.

## Recorded spec-text discrepancy (not a DEVIATION)

requirements.md gate (e) parenthetically says "the runs/probe/Cr deck idiom, K_POINTS 8 4 1".
The on-disk deck idiom is K_POINTS automatic 9 4 1 0 0 0 (runs/probe/Cr/s0_O__base.in, and
protocol.md's k-table: Cr 1x1 production = 9 4 1; 8 4 1 is the Cr `__1x1_k8` folded-mesh bridge
control). Decks are authoritative; 9 4 1 is kept verbatim. Matching A0 means matching the
ladder decks byte-for-byte, which these do.

## Scoring recipe (exact commands)

All greps `-a` (binary-safe).

1. ACCEPTANCE (the gate's primary question), on s0_O__u715_ortho.out:
   `grep -a -A6 "Error in routine" s0_O__u715_ortho.out` ; also `ls CRASH` in this dir.
   - Empty + SCF runs -> the build ACCEPTS `(ortho-atomic)`. Record "this build accepts
     (ortho-atomic)".
   - Card rejected -> record the exact error block. Capability FAIL: the fifth A0 grid point is
     labelled PROJECTOR-UNVERIFIABLE rather than silently imported (A7.1 verbatim); P-PROJ
     cannot run and that is the finding.
2. CONVERGENCE, per deck:
   `grep -ac "convergence NOT achieved" <out>` must be 0 and
   `grep -a "^!" <out> | tail -1` must exist (final total energy).
   Ortho accepted but unconvergeable within electron_maxstep 200 = capability FAIL, same
   recording as card rejection (the rule says "accepted by the build AND its SCF converges").
3. PROJECTOR DELTA (secondary recorded number, only if both decks converge):
   E_atomic and E_ortho from the final `!    total energy` lines (Ry);
   dE = (E_atomic - E_ortho) * 13605.693122994 meV, recorded at identical geometry and U as a
   projector-delta data point — NOT an eta, NOT a pass/fail threshold at S0.
4. Magnetization witness, per deck:
   `grep -a "total magnetization" <out> | tail -1` and
   `grep -a "absolute magnetization" <out> | tail -1` (context: the source-deck base-U run
   converged at total magnetization 10.00 Bohr mag/cell; *O is the U-fragile, valence-changing
   state — LIT-1 Delta-m = -1.06 mu_B, dG_O swings 1.80 eV across the ladder).

Thresholds: none at S0 beyond convergence itself — this is a capability gate. The A0-stage
threshold on record for the full pairing is the A7.1 prediction quoted above.

## Recorded on pass

"This build accepts (ortho-atomic)"; P-PROJ may run under A0; the single-state delta (step 3)
and magnetizations (step 4) recorded.

## Recorded on fail (card rejected / SCF unconvergeable)

Recorded as a capability result; the fifth A0 grid point is labelled PROJECTOR-UNVERIFIABLE
rather than silently imported (A7.1 verbatim); P-PROJ cannot run and that is the finding.

## DEVIATION lines

None. U = 7.1500 eV and the (ortho-atomic) card ARE the registered gate content (A7.4/A7.1),
not deviations from the frozen protocol; every other byte matches the frozen ladder deck.

## Runner

Manifest lines (queue_r1.sh idiom, NP must be an exact multiple of nk=4):
```
s0/e_proj s0_O__u715_atomic .in 4
s0/e_proj s0_O__u715_ortho .in 4
```
Drain marker: QUEUE_ALL_DONE. `JOB DONE` is never success by itself. NOTE: the ortho deck may
legitimately die at input parse — preflight STALE-.out logic never applies to it (no prior
.out), but if the runner marks it DONE with rc!=0 and an Error block, that IS the gate's
recorded answer, not a job to retry.
