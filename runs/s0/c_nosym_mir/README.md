# S0 gate (c) — mirror-arm `nosym` invariance

Built 2026-08-16 from the binding registrations (docs/43 AMENDMENT 7 / Zenodo
10.5281/zenodo.21963144; docs/research/2026-08-15-lit-sweep-round2-synthesis.md §4).

## Registered decision rule (quoted)

Synthesis §4 S0 table, gate (c) row (line 191):

> **Mirror-arm `nosym` invariance** | 1 fixed-geometry `nosym` SCF on an
> already-relaxed 2x1v mirror geometry | 2 | `build_cellsym_pilot.py` lines
> 514–517 hard-die on a mirror arm carrying nosym/noinv, and symmetry
> reduction of an MP mesh **is exact** for a structure that possesses the
> symmetry — so 9 → 16 is a *folding*, not a sampling change. Register "the
> mirror-arm energy is invariant to `nosym` to < 1 meV" as the comparability
> control, and keep the mirror arm at symmetry ON / 9 k.

docs/43 A7.4 (line 1386):

> (c) Mirror-arm `nosym` invariance (< 1 meV) | mirror arm stays symmetry
> ON / 9 k; comparability control | conflating k-folding with a sampling change

## Deck (1 job — the registered count)

`s0_OOH__2x1v_mir__nosym.in` — fixed-geometry SCF at the mirror-arm final
geometry with `nosym = .true.` AND `noinv = .true.` (full unfolded 16-point
4 4 1 set; the mirror parent ran symmetry ON → 9 irreducible k). Everything
else is the parent's frozen protocol verbatim: 80/640, smearing mv 0.01,
local-TF 0.3, conv_thr 1.0d-6, nspin=2, starting_magnetization(1)=0.6,
`HUBBARD (atomic)` / `U Cr-3d 3.7000` after K_POINTS. Build-time diff against
the proven sym-ON GATE-1 child s0_OOH__2x1v_mir__g1.in shows exactly four
changed lines: prefix, max_seconds (10594 → 18833, the cost-model value for
the 16-k version of this same SCF class, = s0_OOH__2x1v_off__g1.in's
computed value; not a DEVIATION, not recomputed), and the two added symmetry
lines — the subject of the gate.

Because build_cellsym_pilot.py lines 514–517 hard-die on a mirror deck
carrying nosym/noinv, this deck was written by this builder, not by
re-running that script (geometry.md note).

nk = 4 (16 k → the "else 4" branch of the build_cellsym_pilot nk rule;
GATE-1 children ran nk=4). Queue line: `s0/c_nosym_mir s0_OOH__2x1v_mir__nosym .in 4`.

## Cell/state adjudication (requirements.md gate c — followed)

Cr s0_OOH, 2x1v mirror arm — same metal/state as gate (b), making (b) and
(c) a matched pair on the two symmetry arms of one system; the mirror arm at
stake is the magnetic S3 battery. This is also the exact geometry the 19
built 1C Hessian decks (runs/probe/Cr_hess) were regenerated from, so the
invariance control lands on the geometry the Hessian claim will use.

## Geometry provenance

**Final BFGS geometry of runs/probe/Cr_cellsym/s0_OOH__2x1v_mir.out**
(converged: `bfgs converged` + `JOB DONE`; GATE-1 AGREE via its __g1 child,
part of the 22/22 block). Cell (fixed relax) from the parent .in:
5.83200 x 6.25223816 x 25.00895264 A; nat=39, ntyp=3.

Extraction method (programmatic): scratchpad script `build_bc.py` — text
parse of the last `Begin final coordinates`...`End final coordinates`
ATOMIC_POSITIONS block of the .out (ASE's espresso-out reader crashes on
spin-polarized Cr outputs, ase 3.28.0), constraint flags per atom index from
the parent s0_OOH__2x1v_mir.in, asserted against flags echoed in the .out;
frozen atoms asserted immobile (<5e-7 A). Cross-check: the emitted
coordinates are byte-identical to those in the proven
s0_OOH__2x1v_mir__g1.in (and, per geometry.md, identical to 1e-6 A to
runs/probe/Cr_hess/s0_OOH__2x1v_mir__hess_ref.in).

## Scoring reference (adjudicated — requirements.md gate c)

The reference is the mirror arm's own GATE-1 child,
**runs/probe/Cr_cellsym/s0_OOH__2x1v_mir__g1.out: E_ref = -3188.70496977 Ry**
— a fresh-density symmetry-ON fixed-geometry SCF at the IDENTICAL final
geometry; both legs are then fresh fixed-geometry SCFs differing ONLY in
symmetry treatment, so the comparison isolates the k-folding with no
relax-vs-SCF hysteresis. Fallback reference (the registration's literal
reading, carrying a hysteresis caveat): the mirror relax's own final SCF
energy at that geometry, **-3188.70497020 Ry** (last `!` line of
s0_OOH__2x1v_mir.out; the two references agree to +0.43 uRy).

BOX CAVEAT (required by the adjudication): the __g1 reference ran on an
earlier box/build. If the measured delta straddles 1 meV, re-run the sym-ON
reference fresh on the same box before scoring — that re-run is a DEVIATION
line adding one SCF, taken only if needed (it is NOT built here; the
registered job count for this gate stays 1).

## Scoring recipe (exact)

```bash
grep -ac "convergence NOT achieved" s0_OOH__2x1v_mir__nosym.out   # must be 0
grep -a "^!" s0_OOH__2x1v_mir__nosym.out | tail -1                # E_nosym (Ry)
grep -am1 "number of k points" s0_OOH__2x1v_mir__nosym.out        # expect 16
grep -a "PWSCF.*WALL" s0_OOH__2x1v_mir__nosym.out | tail -1       # wall clock
```

**PASS iff |E_nosym − (−3188.70496977)| < 1 meV = 0.0000734986 Ry.**
(python: `abs(E_nosym - (-3188.70496977)) < 7.34986e-5`.)
Record the delta against BOTH references (__g1 and relax-final) and the
k-count witness (9 in the parent run vs 16 here).

## Recorded on pass / on fail (registered)

- **PASS (< 1 meV):** "the mirror-arm energy is invariant to `nosym` to
  < 1 meV" is registered as the comparability control; the mirror arm stays
  **symmetry ON / 9 irreducible k** for the whole program; the 9 → 16
  difference is confirmed exact folding.
- **FAIL (≥ 1 meV):** the delta is recorded as a capability result; the
  mirror/off comparison basis must be re-decided by a recorded DEVIATION
  (e.g. nosym mirror arms) BEFORE any S3 mirror deck launches — never
  silently.

Downstream: every S3 mirror-arm deck; the P-SYMCOV comparability claim.

## DEVIATION lines

None. The deck is the frozen mirror-arm protocol plus the two symmetry lines
that are the registered subject of the gate; max_seconds is the established
cost-model value for the 16-k SCF class, taken from the emitter's own output,
not recomputed.
