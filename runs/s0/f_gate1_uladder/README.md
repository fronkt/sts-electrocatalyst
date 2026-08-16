# S0 gate (f) — GATE-1 on the four Cr LIT-1 U-ladder points

Built 2026-08-16 from the three s0spec files (protocol.md / geometry.md / requirements.md).
6 fresh-density fixed-geometry SCF decks. Registered: docs/43 AMENDMENT 7 (A7.3 + A7.4 row f,
Zenodo 10.5281/zenodo.21963144); docs/research/2026-08-15-lit-sweep-round2-synthesis.md S0 table.

## The registered stake (quoted verbatim)

docs/43 A7.3 (P-FLOOR-U):

> **DISCLOSED NON-BLIND:** Cr measures 0.223 V (floor 0.492 -> 0.269 V across
> U = 0 -> 5.00), conditional on the S0(f) GATE-1 pass: if any of the four ladder
> points moves > 50 meV on a fresh-density restart, the number is re-derived and
> the correction recorded before this prediction is dated.

docs/43 A7.4 row (f):

> (f) GATE-1 on the four Cr LIT-1 U-ladder points (6 fresh-density SCFs) | whether the
> 0.223 V floor number survives a basin audit | registering the program's most legible
> number on ungated points

Synthesis S0 table row (f):

> 6 fresh-density fixed-geometry SCFs (4 U points + 2 second seeds at u0.0 and u1.35),
> in the cell the ladder was measured in | 5 [box-h] | The 0.223 V floor movement is the
> program's most legible number and it currently rests on points the repo's own provenance
> section flags **GATE-1 PENDING**, against documented basin drifts of the same order
> (Cr *OOH -175 meV, Co *OH -405 meV). Registering it ungated repeats exactly the failure
> round 1 called fatal.

The documented basin drifts that motivate this gate (lit1-tranche1-uladder.md GATE-1 table):
Cr *OOH production relax -175.11 meV off the corrected basin; Co *OH -404.52 meV; Co slab
+59.39 meV audit-side trap. The non-production-U ladder points (u0.0/u0.5/u1.35) are flagged
"GATE-1 status PENDING verification" in that memo — this gate discharges that flag.

## Deck list

| deck | U (eV) | HUBBARD card | mag(Cr) seed | parent reference E (Ry) | parent reference E (eV) |
|---|---|---|---|---|---|
| s0_OOH__u0.0__g1.in | 0.00 | NONE (plain PBE) | 0.6 (production) | -1637.89546422 | -22284.70305 |
| s0_OOH__u0.5__g1.in | 1.85 | U Cr-3d 1.8500 | 0.6 (production) | -1637.15837792 | -22274.67448 |
| s0_OOH__base__g1.in | 3.70 | U Cr-3d 3.7000 | 0.6 (production) | -1636.48367381 | -22265.49467 |
| s0_OOH__u1.35__g1.in | 5.00 (deck value 4.9950) | U Cr-3d 4.9950 | 0.6 (production) | -1636.04658302 | -22259.54774 |
| s0_OOH__u0.0+spin1.0__g1.in | 0.00 | NONE (plain PBE) | **1.0 (second seed)** | -1637.89546422 | (same point as u0.0) |
| s0_OOH__u1.35+spin1.0__g1.in | 5.00 (deck value 4.9950) | U Cr-3d 4.9950 | **1.0 (second seed)** | -1636.04658302 | (same point as u1.35) |

All six: Cr s0_OOH, 1x1 cell 2.91600 x 6.25223816 x 25.00895264 A, nat 21 / ntyp 3,
K_POINTS automatic 9 4 1 0 0 0, symmetry ON (no nosym/noinv — mirrors the parents' emitted
bytes exactly, per the GATE-1 child rule), nspin 2, ecutwfc 80 / ecutrho 640, mv 0.01,
local-TF beta 0.3, conv_thr 1.0d-6, constraint mask preserved (7 frozen bottom atoms
"0 0 0", 14 free "1 1 1"). Parents carry no max_seconds (LIT-1 deck class); the children
mirror that. HUBBARD (atomic) card placed AFTER K_POINTS per QE >= 7.1 syntax; u0.0 decks
carry NO card at all (genuinely plain PBE, probe_decks.py:333-339 idiom).

Each __g1 deck is a byte-identical copy of its parent .in except the prefix line
(verified by diff). Each +spin1.0 deck differs from its parent in exactly two lines:
prefix and starting_magnetization(1) 0.6 -> 1.0 (verified by diff). Fresh
atomic-superposition density is achieved BY OMISSION: no startingwfc, no startingpot,
no restart_mode anywhere (the _FORBIDDEN guard; pw.x then defaults to
startingwfc='atomic+random', startingpot='atomic' — that IS the fresh start).
_build_report.json in this directory carries per-deck md5 and the parsed parent energies.

## Geometry provenance (hard rule 3)

Every deck: ATOMIC_POSITIONS of runs/probe/Cr/s0_OOH__{u0.0|u0.5|base|u1.35}.in
(byte-identical copies of the ladder decks), which are themselves FIXED single points on the
final BFGS geometry of runs/Cr_slab/s0_OOH.out (runs/probe/Cr/probe_manifest.json:
source_run runs/Cr_slab, geometry_provenance "final" for every job). One geometry for all
four U points — the U ladder never re-relaxes. Spot-check (atoms 1/11/21 of 21):
Cr 0.00000000 1.56305954 9.37835724 / O -0.00455695 1.56305954 13.78946831 /
H -1.50686676 1.56305954 18.37932825 — matches geometry.md's gate (f) spot check.

## Adjudications relied on (from s0spec/requirements.md, restated per its instruction)

1. **WHICH state (registration leaves it open): ALL SIX SCFs are Cr *OOH (s0_OOH).**
   Reasons: (i) the 0.223 V floor = span(c_M)/2 with c_M = dG_OOH - dG_OH at fixed
   endpoints U = 0 and 5.00 (A7.3); (ii) *OOH carries the documented -175 meV production
   basin failure and the known 11.0-vs-11.8 mu_B two-family multistability (docs/41 s6f)
   — it is the flagged risk; (iii) 6 jobs fit exactly one state.
   RESIDUAL RISK (recorded): the s0_OH / s0_O / slab ladder points at off-production U
   remain formally unaudited under the registered 6-job count. Mitigation on record:
   s0_OH's base-U round-trip is clean (+0.00 meV, GATE-1 PASS) and dG_OH is classified
   valence-conserving/U-robust (lit1 memo classification table).
2. **"Fresh-density" concretely:** the repo __g1 idiom (docs/43 lines 783-786) — a
   from-scratch fixed-geometry SCF, QE default atomic-superposition start, own outdir,
   no .save reuse. The original ladder SCFs were themselves atomic-start (.run.in differs
   from .in only in outdir), so the four 0.6-seed jobs are same-deck reproductions on the
   CURRENT production box/build — a cross-build basin-reproducibility audit, which is what
   GATE-1 can test where no relaxation exists at the same Hamiltonian.
3. **"Second seed" concretely:** at u0.0 and u1.35 (the two FIXED ENDPOINTS defining the
   A7.3 floor span), one extra SCF identical to the fresh-density deck except
   starting_magnetization(1) = 1.0. The documented metastable family is the HIGH-moment
   one (11.8 mu_B); a fully-polarised start is the seed most capable of reaching it, so
   0.6-seed/1.0-seed agreement is evidence of basin uniqueness at the endpoints.
   NO seed value is registered anywhere — 1.0 is this build's recorded adjudication
   (any distinct seed satisfies the registration). Naming uses the established
   parse_variant `spin<m>` token (precedent runs/probe/Ru_spin/s0_*__spin0.5.in;
   `+`-joined variant precedent runs/probe/Ir/s0_OH__dipole+vac32.in).

## EXACT scoring recipe

Run on the box via the queue_r1.sh idiom; manifest lines (nk=4, the established 1x1-adslab
pool count; NP must be an exact multiple of 4):

```
s0/f_gate1_uladder s0_OOH__u0.0__g1 .in 4
s0/f_gate1_uladder s0_OOH__u0.5__g1 .in 4
s0/f_gate1_uladder s0_OOH__base__g1 .in 4
s0/f_gate1_uladder s0_OOH__u1.35__g1 .in 4
s0/f_gate1_uladder s0_OOH__u0.0+spin1.0__g1 .in 4
s0/f_gate1_uladder s0_OOH__u1.35+spin1.0__g1 .in 4
```

Wait for `QUEUE_ALL_DONE` in the runner log. Then, per deck (use grep -a — several prior
Cr outputs contain stray binary bytes):

```
# success check (JOB DONE is NEVER success by itself):
grep -ac "convergence NOT achieved" <job>.out     # must be 0
grep -a  "^!" <job>.out | tail -1                 # final total energy, must exist
# score inputs:
E_fresh_Ry = last "^!" line
grep -a "total magnetization"    <job>.out | tail -1
grep -a "absolute magnetization" <job>.out | tail -1
```

Per U point (fresh 0.6-seed SCF vs the ladder .out reference energy in the deck table
above): delta_Ry = E_fresh_Ry - E_parent_Ry; delta_meV = delta_Ry * 13605.693122994.

Thresholds (in the units actually compared):
- 5 meV  = 0.00036749 Ry  — GATE-1 tolerance: |delta| <= 5 meV -> AGREE; else DRIFT and
  the LOWER energy is the corrected value (GATE-1 rule, docs/43 s2-A.3(b)).
- 20 meV = 0.00146997 Ry  — second seeds: if the 1.0-seed solution is > 5 meV LOWER than
  the 0.6-seed one, that is a basin drift and the lower value is corrected-in; if two
  distinct converged solutions sit within 20 meV, flag MULTISTABLE and carry a range
  (arm-4 acceptance rule, imported by adjudication — recorded, not registered).
- **50 meV = 0.00367493 Ry — THE ONLY A7.3-REGISTERED TRIGGER**: if ANY of the four
  ladder points moves > 50 meV (fresh-density restart, taking the seed-minimum energy at
  the two endpoints), the 0.223 V number is RE-DERIVED from the corrected energies
  (span(c_M)/2 recomputed from corrected dG_OOH; dG_OH energies unchanged) and the
  correction is recorded BEFORE the P-FLOOR-U prediction is dated.

Also record per deck: converged total AND absolute magnetization (the 11.0 mu_B family
witness — every original ladder point sat at total mag 11.00; abs mag 14.59 / 17.44 /
20.09 / 21.77 across u0.0/u0.5/base/u1.35).

## What is recorded

**On pass (all four points <= 50 meV, no lower basin found by either endpoint seed):**
the 0.223 V floor number is GATE-1 cleared; P-FLOOR-U's disclosed non-blind Cr value
stands and may be dated; per-point verdicts (AGREE / <=5 meV or the measured delta),
converged total/absolute magnetizations, and any MULTISTABLE flags are recorded in the
gate readout.

**On fail (any point > 50 meV, or a seed finds a lower basin):** the corrected energies,
the re-derived span(c_M)/2, and the dated correction — the prediction is then dated
against the corrected number (a legitimate outcome, not a repair to hide). Sub-50 meV
drifts: the lower energy is corrected-in per the GATE-1 rule without triggering the A7.3
re-derivation clause; both numbers recorded.

## Notes and flags

- DEVIATION: none. Every namelist value is byte-inherited from the frozen LIT-1 parents;
  the only edits are prefix lines and the two adjudicated second-seed magnetization lines.
- Historical CRASH file: runs/probe/Cr/CRASH records a transient runner-side mkdir failure
  on the ORIGINAL s0_OOH__u0.0 run ("unable to create directory ./tmp_s0_OOH__u0.0/...");
  that job was re-run and its .out is converged (2x "convergence has been achieved",
  final E = -1637.89546422 Ry). CRASH is historical; noted per geometry.md.
- The u1.35 nominal U is 5.00 eV in A7.3's wording; the deck value is 4.9950 eV
  (= 1.35 x 3.7000, the ladder's own multiplier token, read from the parent HUBBARD line).
  The decks are authoritative; no edit.
- The '+' character in the two second-seed filenames follows the repo's established
  `+`-joined variant-token naming and is proven safe through the runner
  (runs/probe/Ir/s0_OH__dipole+vac32.* ran through the same idiom).
- Registered box-h ~5 for the gate; est_box_h in manifest.json sums to 5.0.
