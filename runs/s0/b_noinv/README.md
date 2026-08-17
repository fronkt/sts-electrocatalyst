# S0 gate (b) — `noinv` exactness on an off-plane 2x1v geometry

Built 2026-08-16 from the binding registrations (docs/43 AMENDMENT 7 / Zenodo
10.5281/zenodo.21963144; docs/research/2026-08-15-lit-sweep-round2-synthesis.md §4).

## Registered decision rule (quoted)

Synthesis §4 S0 table, gate (b) row (line 190):

> **`noinv` exactness** | 2 fixed-geometry SCFs on one existing 2x1v off-plane
> geometry, `noinv` on vs off | 4 | **Highest ratio in the program.** Must agree
> < 1 meV. On agreement, drop `noinv` from every off-plane job: ~38% off the
> off-plane battery, worst single relaxation ~62 h → ~39 h, ≈ one week of
> calendar on the critical path.

docs/43 A7.4 (line 1385):

> (b) `noinv` exactness (2 fixed-geometry SCFs, one 2x1v off-plane geometry,
> must agree < 1 meV) | drop `noinv` from every off-plane job (~38% off the
> battery; worst job ~62 h → ~39 h) | a week of avoidable critical-path calendar

Registered stake: worst off-plane job **62 h → 39 h** on agreement.

## Decks (2 jobs — the registered count)

| deck | symmetry lines | k-points | nk | est box-h |
|---|---|---|---|---|
| `s0_OOH__2x1v_off__noinvT.in` | `nosym = .true.` + `noinv = .true.` (parent treatment) | 16 | 4 | ~2.3 |
| `s0_OOH__2x1v_off__noinvF.in` | `nosym = .true.` only; **noinv ABSENT** (QE default `.false.`) | 10 (time-reversal-reduced 4 4 1 mesh) | 2 | ~1.5 |

Both are fixed-geometry SCFs under the frozen production protocol: 80/640,
smearing mv 0.01, local-TF beta 0.3, conv_thr 1.0d-6, nspin=2,
starting_magnetization(1)=0.6, `HUBBARD (atomic)` / `U Cr-3d 3.7000` after
K_POINTS, K_POINTS automatic 4 4 1 0 0 0. The two decks are byte-identical
except (1) the `prefix` line (protocol requires prefix = deck basename) and
(2) the presence of the `noinv = .true.` line — verified by unified diff at
build time. Both legs must run fresh on the SAME box at the same NP
(same-build comparability, requirements.md gate b).

nk choice per the build_cellsym_pilot rule ("2 if k-count<12 else 4"):
leg-1 16 k → nk 4; leg-2 10 k → nk 2. Suggested queue_r1.sh manifest lines
are in manifest.json (NP must be a multiple of both, e.g. NP=20).

## Cell/state adjudication (requirements.md gate b — followed)

Cr s0_OOH, 2x1v off arm. requirements.md ADJUDICATES Cr over geometry.md's
Ir recommendation because the savings claim is priced on the MAGNETIC
(nspin=2 + HUBBARD) 2x1v off-plane battery — the ~39 h S3 job class — so
exactness must be demonstrated on that Hamiltonian class, not on nspin=1 Ru.
Per the task contract, the requirements.md adjudication governs; the
geometry.md Ir alternative is noted here for the record and not used.

## Geometry provenance

Both decks: **final BFGS geometry of
runs/probe/Cr_cellsym/s0_OOH__2x1v_off.out** (converged: `bfgs converged` +
`JOB DONE`; final `!  total energy = -3188.79231810 Ry`). Cell (fixed relax)
from the parent .in CELL_PARAMETERS: 5.83200 x 6.25223816 x 25.00895264 A;
nat=39, ntyp=3.

Extraction method (programmatic): scratchpad script `build_bc.py` — text
parse of the last `Begin final coordinates`...`End final coordinates`
ATOMIC_POSITIONS block of the .out (ASE's espresso-out reader crashes on
spin-polarized Cr outputs, ase 3.28.0 — geometry.md note), constraint flags
("0 0 0" frozen / "1 1 1" free) taken per atom index from the parent
s0_OOH__2x1v_off.in and asserted consistent with any flags echoed in the .out
block; frozen atoms asserted immobile (<5e-7 A) vs the parent .in.
Cross-check: the emitted leg-1 deck is byte-identical to the proven GATE-1
child runs/probe/Cr_cellsym/s0_OOH__2x1v_off__g1.in **except the prefix
line** (diff recorded in build output), so the extracted geometry is exactly
the geometry the 22/22 GATE-1 block already scored.

`max_seconds = 18833` on both decks: copied from the established cost-model
output for this exact SCF class (s0_OOH__2x1v_off__g1.in, same geometry,
same Hamiltonian, 16 k). For the 10-k leg-2 this is a conservative upper cap.
Not a DEVIATION: the value is the established emitter output, not recomputed.

## Scoring recipe (exact)

After both jobs drain (`QUEUE_ALL_DONE` in the queue log):

```bash
# convergence QC (must hold for BOTH legs; -a: outputs may contain stray binary)
grep -ac "convergence NOT achieved" s0_OOH__2x1v_off__noinvT.out   # must be 0
grep -ac "convergence NOT achieved" s0_OOH__2x1v_off__noinvF.out   # must be 0
grep -a "^!" s0_OOH__2x1v_off__noinvT.out | tail -1                # E_leg1 (Ry)
grep -a "^!" s0_OOH__2x1v_off__noinvF.out | tail -1                # E_leg2 (Ry)
# k-count witness (expect 16 vs 10)
grep -am1 "number of k points" s0_OOH__2x1v_off__noinvT.out
grep -am1 "number of k points" s0_OOH__2x1v_off__noinvF.out
# wall clocks (both recorded)
grep -a "PWSCF.*WALL" s0_OOH__2x1v_off__noinvT.out | tail -1
grep -a "PWSCF.*WALL" s0_OOH__2x1v_off__noinvF.out | tail -1
```

**PASS iff |E_leg1 − E_leg2| < 1 meV = 0.0000734986 Ry.**
(python: `abs(E1-E2) < 7.34986e-5` on the two Ry values.)

Cross-check (not a substitute for running leg-1): E_leg1 should also
reproduce the existing runs/probe/Cr_cellsym/s0_OOH__2x1v_off__g1.out
fresh-density energy to ≤5 meV (GATE-1 tolerance) — a same-deck cross-build
witness. Both k-counts and both wall clocks are recorded regardless of
verdict.

## Recorded on pass / on fail (registered)

- **PASS (< 1 meV):** `noinv` is dropped from every subsequent off-plane job
  in the program — a registered protocol change recorded here and cited by S3
  deck builders, never a silent edit. Record the measured delta and both wall
  clocks. Registered stake realised: ~38% off the off-plane battery, worst
  job 62 h → 39 h.
- **FAIL (≥ 1 meV):** `noinv` stays on every off-plane job; the delta is
  recorded as a build-capability result; S3 keeps the ~62 h worst-job pricing.

Downstream: every S3/tier_v3 off-plane deck; the S3 calendar (last safe
launch Aug 26, F2). NOTE: gate (g)'s TiO2 timing deck runs with frozen
noinv=.true. unless this gate has REPORTED its pass before that launch
(requirements.md gate g).

## DEVIATION lines

None. All namelist values are the frozen production protocol as emitted by
the established cellsym pipeline; the only degrees of freedom exercised are
the prefix and the presence/absence of `noinv` — the registered subject of
the gate.
