# S0 gate (a) — BEEF-vdW ensemble emission (4 SCFs, 1x1 Ru slab)

Built 2026-08-16 by the S0 a+e builder. Governing registrations: docs/43-prereg-week1-factorial.md
AMENDMENT 7 / A7.4 (Zenodo 10.5281/zenodo.21963144); docs/research/2026-08-15-lit-sweep-round2-synthesis.md
S0 table lines 182–202 (arm 7, F5); adjudications: scratchpad spec requirements.md gate (a).

## Registered decision rule (quoted)

> "a deck PASSES if its output contains the BEEF ensemble block (the ~2000-member
> non-self-consistent XC ensemble energies). Winner = first of (i)–(iii) that emits.
> Only after (i), (ii) AND (iii) all fail may the XC row be struck (F5, A7.4 verbatim)."

Registered jobs: 4 SCFs, 1x1, "on an existing converged Ru density", ~4 box-h.
Kill it prevents: striking the XC row on a null a grep cannot interpret (F5: one deck +
grep cannot distinguish "absent" from "not requested").

## Deck list

| deck | switch under test | HUBBARD |
|---|---|---|
| slab__beefens.in  | (i)  `ensemble_energies = .true.` in &SYSTEM | none |
| slab__beefcalc.in | (ii) `calculation = 'ensemble'` in &CONTROL (replaces 'scf') | none |
| slab__beefctl.in  | (iii) CONTROL — `input_dft = 'BEEF-vdW'` only, no emission switch | none |
| slab__beefhub.in  | (iv) SELECT-WINNER — see below | HUBBARD (atomic) / U Ru-4d 3.7000 |

All four carry `input_dft = 'BEEF-vdW'` in &SYSTEM (the XC under test). Everything else is
byte-identical to runs/probe/Ru/slab__base.in (fixed-geometry SCF, nat=18, ntyp=2, nspin=1 NM,
nosym=.true.+noinv=.true. clean-slab rule, 80/640, mv 0.01, local-TF 0.3, conv_thr 1.0d-6,
K_POINTS automatic 8 4 1 0 0 0, Ru_ONCV_PBE-1.0.oncvpsp.upf + O.pbe-n-kjpaw_psl.0.1.UPF)
except prefix and the per-deck switch lines above.

### SELECT-WINNER (deck iv)

Per the requirements.md adjudication, deck (iv) is "the WINNER of (i)–(iii) re-run with a
HUBBARD card present". The winner is unknown at build time, so slab__beefhub.in is NOT emitted
as a runnable file. Three templates are provided:

- `slab__beefhub.in.template_i`   — winner = (i): ensemble_energies + HUBBARD card
- `slab__beefhub.in.template_ii`  — winner = (ii): calculation='ensemble' + HUBBARD card
- `slab__beefhub.in.template_iii` — winner = (iii): input_dft only + HUBBARD card

AFTER decks (i)–(iii) drain and are scored: copy the winner's template to `slab__beefhub.in`
(no edits) and launch it as job 4. If (i)–(iii) all fail, deck (iv) is not run (there is no
winner to copy) and the XC row is struck at 3 of the 4 registered jobs — record that outcome.

PROBE-U: U Ru-4d 3.7000 is a capability placeholder, not a physics claim. No registered Ru U
exists anywhere in the campaign; 3.7000 is the only production U value in the frozen vocabulary
(Cr-3d). Deck (iv) energies are capability-only and may NEVER enter any science row.

## Geometry provenance (all four decks + templates)

ATOMIC_POSITIONS of runs/probe/Ru/slab__base.in, themselves the final BFGS geometry of
runs/Ru_anchor/slab.out (runs/probe/Ru/probe_manifest.json: source_run runs/Ru_anchor,
geometry_provenance "final" for slab/base). Cross-check: the slab__base fixed-geometry SCF
reproduces the anchor relax energy (-1630.66772630 vs -1630.66772646 Ry, 0.16 uRy).
Note: the adjudication's provenance shorthand "final BFGS geometry of runs/probe/Ru/
slab__base.out" is stated here precisely — slab__base is itself a fixed-geometry SCF; the BFGS
geometry it froze descends from runs/Ru_anchor/slab.out. The saved charge density of that run
is not in the repo; "existing converged Ru density" is satisfied by reusing the converged
system/geometry with each gate SCF regenerating its own density (fresh atomic-superposition
start by omission — no startingwfc/startingpot anywhere; BEEF-vdW self-consistency needs its
own density in any case).

## Scoring recipe (exact commands)

Run on the box after each `.out` appears. All greps use `-a` (binary-safe).

1. Parse acceptance per deck (a refusal IS a result, not a broken run):
   `grep -a -A4 "Error in routine" slab__beefens.out` (repeat per deck).
   An input-parse rejection of `ensemble_energies` or `calculation='ensemble'` = that switch
   FAILS; record the exact error block. Also check for a CRASH file in the gate dir.
2. Functional acceptance (all decks):
   `grep -am2 -i -E "Exchange-correlation|beef|libbeef|Unknown" slab__beefctl.out`
   If the build rejects `input_dft='BEEF-vdW'` itself (unknown functional / no libbeef) on all
   decks, that is the capability fail: the XC row is struck under the same F5 rule; record it.
3. Ensemble detection per completed deck:
   `grep -a -n -i -E "beef|ensemble" slab__beefctl.out | head -40`
   PASS requires an actual ensemble block of ~2000 non-self-consistent XC energies — verify the
   member count (e.g. count numeric lines following the header:
   `awk '/BEEFens/{c=1;next} c&&/^ *-?[0-9]/{n++;next} c{exit} END{print n}' <out>`).
   Candidate header signatures — UNVERIFIED, no repo precedent (protocol.md GAP 2):
   "BEEFens", "BEEF-vdW xc energy contributions". CONFIRM the exact stdout signature against
   the box's QE 7.x source (beef interface in the pw.x tree) BEFORE scoring; do not score on
   an assumed string. A null grep on an unconfirmed signature is NOT a fail — that is the F5
   trap this 4-deck design exists to avoid.
4. SCF sanity for any PASSING deck:
   `grep -a "^!" <out> | tail -1` present and `grep -ac "convergence NOT achieved" <out>` = 0.
5. Winner = first of (i)-(iii) that emits (order: i, ii, iii). Then build deck (iv) per
   SELECT-WINNER above and re-apply steps 1–4 to slab__beefhub.out.

Threshold: emission is binary (block present with ~2000 members, or not). No energy threshold.

## Recorded on pass

Which switch this build honours; whether emission survives the HUBBARD card (deck iv).
S5 unlocks (Ru/Ir/Ti, 12 SCFs + 2 gas refs); the +U extension of S5 is allowed only if deck
(iv) also emits. If only (iv) fails: S5 scoped strictly to the U=0 metals; recorded.
Amendment 10 becomes owed (Sep 18) only on a pass.

## Recorded on fail ((i)–(iii) all null)

S5 struck at zero sunk cost; Finding 4's sigma stays the literature band; the capability limit
is itself reported as a result.

## DEVIATION lines

- DEVIATION: `input_dft = 'BEEF-vdW'` is on the builder `_FORBIDDEN` list
  (src/dft/build_cellsym_pilot.py:318) and is present in all four decks — it is the switch
  under test in this capability gate (registered deviation, requirements.md gate (a)).
- DEVIATION (deck ii only): `calculation = 'ensemble'` replaces the frozen `'scf'` — the
  emission switch under test.
- Note (not a deviation): `ensemble_energies` / `calculation='ensemble'` have zero repo
  precedent; the syntax rests on the prereg text only (protocol.md GAP 2). A parse rejection
  is therefore a legitimate, expected possible outcome and is recorded per step 1.
- Note (not a deviation): deck (iv) HUBBARD card `U Ru-4d 3.7000` is PROBE-U (see above).

## Runner

Manifest lines (queue_r1.sh idiom, NP must be an exact multiple of nk=4):
```
s0/a_beef slab__beefens .in 4
s0/a_beef slab__beefcalc .in 4
s0/a_beef slab__beefctl .in 4
```
then, after SELECT-WINNER: `s0/a_beef slab__beefhub .in 4`.
Drain marker: QUEUE_ALL_DONE (two lines if run as two waves). `JOB DONE` is never success by
itself.
