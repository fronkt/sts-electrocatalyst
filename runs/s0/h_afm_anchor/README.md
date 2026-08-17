# S0 gate (h) — AFM anchor probe (4 jobs)

Built 2026-08-16 by the S0 builder from the three spec files in scratchpad/s0spec/
(protocol.md, geometry.md, requirements.md). Governing registrations: docs/43 AMENDMENT 7
(A7.4 nine-gate table, Zenodo 10.5281/zenodo.21963144); docs/research/
2026-08-15-lit-sweep-round2-synthesis.md S0 table; docs/41 P11 (lines 402-422, closure ~499).

## Registered decision rule (quoted)

From the S0 registration (requirements.md, binding contract for this gate):

> "REGISTERED jobs: 4 nspin=2 AFM fixed-geometry SCFs on existing RuO2 2x1v geometries.
> ~8 box-h."
> "Decision rule: measurement gate — recorded whichever way it goes (A7.4 column head).
> Interpretive thresholds, from the registrations: AFM adopted as the anchor's magnetic
> row only if E_AFM < E_NM by > 20 meV (arm-4 acceptance rule); |Delta-E| <= 20 meV ->
> MULTISTABLE flag with range; moment collapse or E_AFM > E_NM -> the anchor magnetic
> row is a measured null."

## What this gate closes (P11)

P11 as registered (docs/41-prereg-anchor-offset-diagnosis.md lines 402-422, verbatim):

> "P11 — spin polarisation on the anchors (added 2026-08-06, before any result). Re-run
> all four states of Ru and Ir at fixed geometry with `nspin = 2` and
> `starting_magnetization = 0.5` on the metal only. ...
> Two limits on this test, both stated in advance: (i) it is **FM**, not the AFM ground
> state, because AFM needs the Ru sublattice split into two species — FM captures the
> *local* moment that drives Liang's mechanism, and AFM is the follow-up if FM moves the
> descriptor; (ii) it is a **single point at an NM-relaxed geometry**, so it is a lower
> bound on the effect ..."

The FM leg of P11 is CLOSED (REFUTED — it moved eta the wrong way; docs/41 §6b, line
~486-499). Gate (h) does NOT reopen that closed FM result. It discharges P11's registered
limit (i) — the AFM follow-up that "needs the Ru sublattice split into two species" —
and supplies a MEASURED magnetic row on the anchor, replacing the refuted "the anchors
are structurally incapable" wording with measured numbers (permitted status vocabulary,
A7.6 item 6; tension flag 8 of requirements.md, copied here as required).

## Deck list and geometry provenance

All four decks are fixed-geometry SCFs (calculation='scf') at the OFF-arm final BFGS
geometries (requirements.md adjudication: the off arm is the production-protocol arm;
the clean-slab ref exists only once and was itself built with the nosym/noinv idiom, so
all four sources share the same symmetry treatment — no arm mix in this set).

| deck | nat | ntyp | geometry provenance (final BFGS geometry of) | parent (NM) final E, Ry |
|---|---|---|---|---|
| ref__2x1v__afm.in        | 36 | 3 | runs/probe/Ru_cellsym/ref__2x1v.out        | -3261.33545254 |
| s0_O__2x1v_off__afm.in   | 37 | 3 | runs/probe/Ru_cellsym/s0_O__2x1v_off.out   | -3302.93178971 |
| s0_OH__2x1v_off__afm.in  | 38 | 4 | runs/probe/Ru_cellsym/s0_OH__2x1v_off.out  | -3304.19715356 |
| s0_OOH__2x1v_off__afm.in | 39 | 4 | runs/probe/Ru_cellsym/s0_OOH__2x1v_off.out | -3345.68064313 |

Extraction was programmatic (scratchpad/s0spec/build_h_afm.py): the last `Begin final
coordinates`...`End final coordinates` block of each converged .out (`End of BFGS` +
`JOB DONE` verified), species sequence cross-checked line-by-line against the parent .in,
constraint flags taken from the parent mask (frozen "0 0 0" atoms verified unmoved to
< 1e-5 A). Cell, k-mesh (4 4 1 0 0 0), and nosym=.true./noinv=.true. carried verbatim
from the parent decks. IMPORTANT CONTEXT (geometry.md): the parent Ru_cellsym decks ran
nspin UNSET = 1 — the parents are NON-MAGNETIC (NM), not FM. These AFM SCFs are therefore
a new magnetic treatment evaluated on NM-relaxed geometries (single points; per P11 limit
(ii) this is a lower bound on the magnetic stabilisation).

## AFM pattern: which atoms carry which sign, and why

Adjudicated construction (requirements.md gate h): the Ru sublattice is split into TWO
SPECIES LABELS Ru1/Ru2, identical pseudo (Ru_ONCV_PBE-1.0.oncvpsp.upf) and identical
mass (101.070), with starting_magnetization(Ru1) = +0.5 and starting_magnetization(Ru2)
= -0.5 (the +/-0.5 magnitude follows the repo's P11 spin idiom, runs/probe/Ru_spin/
s0_*__spin0.5.in: nspin=2 + starting_magnetization on the Ru species). nspin = 2; total
magnetization left FREE (no tot_magnetization key); NO HUBBARD card (Ru carries no U —
protocol.md §2). H and O species carry explicit starting_magnetization = 0.0.

Sign assignment = the two bulk rutile Ru sublattices — corner (0,0,0)-type vs
body-centre (1/2,1/2,1/2)-type — which is the alternating-sublattice AFM/altermagnetic
ordering of rutile RuO2 in the directional support cited by synthesis arm 4
(10.1021/acs.jpcc.1c08700): antiparallel moments on the two sublattices related by the
4_2 screw. Trace: in the (110) slab frame used by the production builder, x = [001]
(period c = 3.10700 A, the 1x1 cell x-length), y = [1-10], z = [110]; mapping the bulk
cell through that frame, corner-sublattice Ru sit at x = 0 (mod c) and body-centre Ru
at x = c/2 = 1.5535 (mod c) in EVERY (110) layer — a rigid-translation-invariant
classification. Applied to the relaxed coordinates the assignment is unambiguous: the
largest deviation of any Ru from its comb is 0.059 A against a 1.554 A comb separation
(per-deck maxima in manifest.json). Every deck has exactly 6 Ru1 (+0.5) and 6 Ru2 (-0.5);
within each Ru (110) layer the two rows (bridge row and cus row, different y) carry
opposite signs, alternating layer by layer — the rutile c-axis alternation.

Assignment on the clean ref (identical pattern in all four decks; 1-based atom indices):

| atoms (Ru1, +0.5) | atoms (Ru2, -0.5) |
|---|---|
| 1, 3, 5, 19, 21, 23 (x ~ 0 or 3.107) | 2, 4, 6, 20, 22, 24 (x ~ 1.554 or 4.661) |

(Adsorbate decks: same 12 Ru indices; adsorbate atoms are appended at the end and carry
no moment seed.)

## Deliverable

Per state: Delta-E_mag = E_AFM - E_NM, where E_NM is the existing nspin=1 energy of the
SAME arm at the IDENTICAL final geometry — the parent .out final energies tabled above
(source paths in the table). The registration's shorthand "E_AFM - E_FM" is operationally
identical: no FM 2x1v Ru run exists on disk, and FM collapses to NM on this material by
construction (synthesis arm 4), so NM is the FM-limit reference (requirements.md tension
flag 2, restated here as required). Derived columns for the record: Delta(dG) per rung,
descriptor movement, Delta-eta(Ru); plus converged TOTAL and ABSOLUTE magnetisation per
state — the ABSOLUTE channel is the AFM witness, since M_total = 0 by construction for
a compensated AFM state (docs/43 finding U4).

## Scoring recipe (exact)

For each job (run via the queue idiom; success is NEVER `JOB DONE` alone):

1. Converged? `grep -a "convergence has been achieved" <job>.out | wc -l` >= 1 AND
   `grep -ac "convergence NOT achieved" <job>.out` == 0 AND a final energy line exists.
2. Final energy (Ry): `grep -a "^!" <job>.out | tail -1`
3. Magnetisation (last printed values):
   `grep -a "total magnetization" <job>.out | tail -1`
   `grep -a "absolute magnetization" <job>.out | tail -1`
4. Delta-E_mag per state = [E_AFM(Ry) - E_NM(Ry)] * 13.605693122994 * 1000 meV, with
   E_NM from the parent energies tabled above.
5. Verdict per the registered thresholds:
   - E_AFM < E_NM by > 20 meV -> AFM ADOPTED as the anchor's magnetic row.
   - |Delta-E_mag| <= 20 meV -> MULTISTABLE flag; carry the range.
   - absolute magnetization collapsed (~0, i.e. < ~0.1 mu_B against the ~6 mu_B total
     absolute magnetization seeded, 12 Ru x |0.5|) OR E_AFM > E_NM by > 20 meV -> the
     anchor magnetic row is a MEASURED NULL.
   A collapsed moment is a RESULT, not a failed run (P11 wording, quoted above) — record
   the converged magnetisations either way.

## What is recorded on each outcome

- ADOPTED: the 4-state magnetic row (Delta-E_mag, total/absolute M), the re-derived
  Delta(dG)/descriptor/Delta-eta(Ru) columns; the S6 anchor-stratum error budget gains a
  measured magnetic row. Directional expectation on record (arm 4, non-binding): worth
  ~0.2 V on eta per JPCC 1c08700.
- MULTISTABLE: the range is carried; the anchor magnetic row is flagged, not adopted.
- NULL (collapse or E_AFM higher): the measured null replaces the refuted "structurally
  incapable" wording with a measured magnetic row on the anchor; the anchor-insensitivity
  language in the report cites this gate.
In every outcome: P11's registered limit (i) — the AFM follow-up — is DISCHARGED.
A7.5's Mn-AFM obligation is SEPARATE (S3), not this gate.

## Runner notes

nk = 4 for every deck (4 4 1 mesh with nosym+noinv -> 16 k-points >= 12; the 2x1
build_cellsym_pilot rule; NP must be an exact multiple of 4). Suggested manifest lines
(queue_r1.sh format, dir relative to RUNS):

```
s0/h_afm_anchor ref__2x1v__afm .in 4
s0/h_afm_anchor s0_O__2x1v_off__afm .in 4
s0/h_afm_anchor s0_OH__2x1v_off__afm .in 4
s0/h_afm_anchor s0_OOH__2x1v_off__afm .in 4
```

Registered budget ~8 box-h total (~2.0 box-h/job in manifest.json).

## DEVIATION lines

- DEVIATION: max_seconds is OMITTED from these four decks. The parent cellsym relax
  decks carry an emitter-computed max_seconds (protocol.md §1b), but that cost model is
  calibrated for the cellsym relax/LIT classes; the repo's other S0-class hand-built SCF
  battery (runs/probe/Cr_hess, all 19 decks) omits max_seconds entirely, and that
  precedent is followed here. Runaway protection is the runner's job-level supervision.
- NOT a deviation (recorded for clarity): ntyp increases by 1 vs the parents (Ru split
  into Ru1/Ru2) and nspin=2 + starting_magnetization(+0.5/-0.5/0.0) lines are added —
  this IS the gate's registered treatment (requirements.md adjudication), not a
  protocol change. Everything else (cutoffs, smearing, local-TF 0.3, conv_thr 1.0d-6,
  k-mesh, nosym/noinv, cell, constraint mask, pseudos) is verbatim from the parent decks.
- NOTE: the parent geometries are NM-relaxed; these are single-point AFM energies (P11
  limit (ii): a lower bound on the magnetic effect).
