# 59 — Correction of record: the A0-main metal roster, and its completion — 2026-08-28

**Status: DRAFT for the entrant.** supporting infrastructure (per the AI-use
log convention of A7.0/A9); the entrant re-authors and deposits. Nothing in this document
invents a threshold; every rule it cites is quoted from an already-deposited registration.
**Until deposited, its authority is its commit timestamp** — committed and pushed before
any tranche-2/3 job ran, which is the property that matters.

## 1. What went wrong (the correction proper)

docs/43:4-5 sets the rule this correction rests on: "Nothing in this document may
be edited after that deposit; corrections go in a dated addendum at the bottom with
the reason." Amendment 5 (docs/43:932) says changes happen "only through its own
dated amendment", but its subject is the five DEFERRED literature items
(D3/D5/D7/D9/D10), so it is narrower than the claim made here and is cited only as
supporting language. (Two earlier pointers are retracted: this document first cited
docs/43:279, a row of the 1B hp.x internal-gate table that says nothing about scope
-- corrected 2026-08-29 after the wave-4 audit; the replacement pointer 932 was
itself too narrow and is corrected here, 2026-08-29, after the wave-5 audit. The
finding is unchanged in both cases -- the roster allocation was chosen with no dated
amendment -- only the registration pointer moved. The same retraction is recorded at
the ledger's own copy, docs/45 "A0 wave 3".)
A6.1(a) registered A0-main's range (0–9 eV), cell (1×1), calculation (fixed-geometry
SCF), metal set ("Ru and Ir as well as the 3d metals", A6.3:1244) and scale (~140 SCFs),
but **not a step**. On 2026-08-27 the entrant chose the allocation **Cr 19 / Ru 7+1 /
Ir 7+1 = 140** — recorded only in the builder docstring and manifest, with **no dated
amendment**. That allocation spent the whole registered scale on one 3d metal: Mn, Fe
and Ti (A7.2/A7.3's blind metals) were left with no grid at all.

The 2026-08-28 wave-3 adversarial audit flagged this as MAJOR (registration verifier,
docs/figs/a0_verification_findings_2026-08-28.txt); the shortfall has been disclosed in
the banked readout (`a0main_readout.json["caveats"]["coverage_shortfall"]`) since the
same day. This document is the owed dated record of both the 2026-08-27 decision and
its remediation.

## 2. The remediation (directed 2026-08-28)

The entrant directed, verbatim: **"Do them over Mn/Fe/Ti then"** (2026-08-28, after the
tranche-1 Cr/Ru/Ir readout was banked). The ordering — extension decided after tranche 1
was read — is stated plainly. Why it remains a test and not a tuned grid:

- **Mn, Fe, Ti are blind.** A7.2 names them blind metals; no A0 number for any of them
  exists anywhere. Nothing that was read informs anything about them.
- **Nothing read is touched.** Tranche 1 (Cr/Ru/Ir) is not refined, re-run or
  re-allocated. The extension only adds the metals the registered sentence always
  promised.
- **The resolution is pre-recorded.** The tranche-1 builder's own pre-launch docstring
  recorded the uniform-coarse alternative ("Five metals × 4 states × 7 points is ALSO
  exactly 140 — a uniform-coarse reading that includes Mn and Fe") before any A0 number
  existed. Tranche 2 builds exactly that resolution.
- **Everything decision-like is registered before launch** in
  `src/dft/build_a0main_w2.py` (committed, pushed): the grids, the production-U control
  points, the Fe *OOH branch-pilot protocol **and its selection rule**, and the Ti plan.

**Scale disclosure:** the registered "~140 SCFs" is exceeded. Tranche 2 adds 59 jobs
(Mn 32, Fe 24, Fe pilots 3) + a gated 8-rung Fe *OOH ladder; tranche 3 adds 4 TiO2
relaxations + a 28-point ladder + 4 base SCFs. Total ≈ 243 jobs against "~140". The
scale clause was a budget estimate, not a cap; the overage buys exactly the registered
metal set and is stated here rather than absorbed silently.

## 3. The tranches

**Tranche 2 — Mn + Fe (launched 2026-08-28).** REF_GRID {0, 1.5, 3, 4.5, 6, 7.5, 9}
plus each metal's own production U as a declared extra point (Mn 3.90, Fe 5.30 — the
same pattern as the Xu anchors, labelled PRODUCTION-U; each doubles as the byte-identical
re-run determinism check). Sources: the 2026-08-08 magnetic-audit decks
(`runs/probe/{Mn,Fe}_audit`, geometry_provenance "final"). Audit round-trips: Mn ≤0.005
meV all four states; Fe ≤0.52 meV on slab/*O/*OH.

**Fe *OOH branch protocol** (registered in the builder before any pilot ran): the audit
measured a cold start at Fe *OOH's geometry trapping +276.60 meV above the banked
relaxation state (docs/41 §6d; the relaxation's state is the energy of record). The
relaxation's density no longer exists, so: three starting-guess pilots at U = 5.30
(mag 0.1 / 0.3 / 0.7; 0.5 is the banked trapped control), acceptance =
|E − (−34804.1641 eV)| ≤ 5 meV, closest wins, applied uniformly to the 8-rung ladder
(`build_a0main_w2b.py`, gated like A0-cell's u715). If none passes, the ladder runs at
0.5 and the whole Fe *OOH column is labelled BRANCH-CONDITIONAL (+0.277 eV measured
class). No guesses beyond the three declared. Separately disclosed: docs/45's parked
entrant call on the −428.5 meV Fe *OOH re-relax; A6.4's "the relaxed point wins" applies
if it is ever banked.

**Tranche 3 — Ti (geometry chain first).** TiO2 has no slab or adsorbate geometry
anywhere in the campaign (only bulk hp.x work). Chain: `qe_slab.py build Ti
--supercell 1` (production builder; d0, nspin=1, **U = 0 by the same MP convention that
sets Ru/Ir to zero**; pseudo `ti_pbe_v1.4.uspp.F.UPF`, S0-verified at ecut 80/640) →
relax slab + 3 adslabs → probe-style base SCFs → 7-point REF_GRID ladder (28 SCFs;
U = 0 is TiO2's production point, so the u000 rung is the determinism control). Gas
references are the campaign's single banked calculation, copied md5-identical as for
every other metal and disclosed live by the readout.

## 3b. Outcomes recorded post-launch (added 2026-08-29, after both arrays drained)

Dated additions, kept separate from the pre-launch text above so the record of what
was written before results existed stays intact:

- **Fe *OOH pilot: all three guesses PASS** (0.019–0.023 meV from the −34804.1641 eV
  reference, gate 5 meV; all at the relax branch's totmag 22.98). Closest wins → m010;
  the 8-rung ladder runs at starting_magnetization 0.1 (`build_a0main_w2b.py`, which
  re-derives the verdict from the outputs and refuses to build on disagreement). The
  ladder's u530 rung is byte-identical to the winning pilot deck except the prefix
  line — the determinism control.
- **The campaign's first A0 convergence failures:** Fe s0_O u300 and u450 stopped at
  200 iterations (magnetic oscillation, mid-U window — where A6.5(2) predicted).
  Escalation rung (i) applied: `__r1` restarts from the retained u150/u530 neighbour
  densities (runner `48_a0_repair.slurm`, which keeps the inline projwfc so the
  repaired points still carry Löwdin populations). Failed .outs retained; A8.4 reports
  the 2/8 = 25% pre-repair rate either way.
- **Ti s0_OOH relax failed** (SCF after the first ionic step; zero BFGS steps banked).
  Rung (i) is inapplicable to a relaxation, so rung (ii): `s0_OOH_r1` halves
  mixing_beta and continues from the last trajectory geometry (spliced verbatim). Its
  base + 7 rungs are gated on r1 converging; if r1 fails, rung (iii) NOT_CONVERGED and
  A7.3's own registered conditioning shrinks the span denominator.
- **Scale update:** the ≈243 above becomes ≈246 with the three repair jobs (2 Fe SCF
  restarts + 1 Ti relax continuation). Same disclosure stance: stated, not absorbed.

## 3c. The second escalation round (added 2026-08-29, before it ran)

Two of tranche 2b/3's points did not converge, for different reasons, and the
response to each is registered in `src/dft/build_a0main_w2c.py` -- committed and
pushed before either job was submitted, which is again the property that matters.

**Fe s0_O at U = 4.5 -- inside the ladder.** Rung (i) (density seed from u530)
oscillated between ~1e-4 and ~8e-2 Ry for most of its 200 iterations and settled
to ~1.2-4e-5 Ry only over the final ~17, never reaching conv_thr 1e-6, with totmag
pinned at 21.98 throughout; its sibling u300 (seeded from u150) converged in 202 s
at totmag 22.90. The measured moments say why: the s0_O ladder runs 18.91, 21.36,
22.90 up to u300 and 21.98, 21.99, 22.00, 21.99 from u530 on, so u450 sits on the
crossing between two nearly degenerate branches -- the exact failure mode A6.5(2)
was written for. Rung (ii) halves the mixing beta on top of the seed, and because
BOTH neighbours are now converged and rung (i) says "the converged neighbouring-U
density" without naming one, both legal parents run: `__r2` from u530 (21.98) and
`__r2b` from u300__r1 (22.90). The selection rule is fixed before launch: lower
converged energy is the banked point, the difference is reported as the measured
branch splitting at U = 4.5, one converged means that one (labelled with its
branch), neither means A6.5(2)(iii). Disclosed limit: the other seven s0_O rungs
were not branch-searched, and each row's totmag travels into the readout so a
reader can see which branch every point is on.

**Ti s0_OOH -- the ladder is exhausted, and the cause is geometric.** Rung (i)
never applied to a relaxation; rung (ii) banked two ionic steps and then
limit-cycled at ~1.3e-4 Ry (its two banked steps took the force 0.173 -> 0.125
Ry/bohr, continuing a walk that began at 0.281 in the failed first run).
Switching the mixer is not available -- `local-TF` is
already on for every slab deck in the campaign (`qe_slab.py:175`). What the
geometry shows: `qe_slab.py` starts every Ti adsorbate ~3.1-3.2 A off the nearest
Ti, and where *O and *OH walked DOWN into Ti-O bonds of 1.735 A and 1.829 A over
36 and 56 ionic steps, *OOH is walking UP (3.167 -> 3.263 -> 3.325 -> 3.414 A)
into the desorbed-radical region, where the chain's nspin = 1 convention cannot
spin-split the resulting half-occupied state. The SCF failure is a symptom of the
starting geometry, not a mixing problem; and three steps is far too short a walk
to conclude TiO2 does not bind *OOH.

Two relaxations run, identical numerics, different starts: `s0_OOH_r2` continues
rung (ii)'s own walk from its last geometry, and `s0_OOH_r3` restarts from the
built deck with the adsorbate rigidly translated -- orientation and internal
geometry preserved exactly -- so the anchor O begins at the mean of Ti's OWN two
converged Ti-O bond lengths (1.734553 and 1.829256 A -> 1.781905 A), read off the
relaxed outputs by the builder rather than typed in. The start DOES select which local minimum BFGS reaches -- that is the
point of r3, and it is why the selection rule has a basin gap to report at all.
What makes it not outcome-tuning is narrower: the re-anchor distance is computed
mechanically from Ti's own two converged states, the rule choosing between r2 and
r3 was fixed before either ran, and neither deck's energy was known when either
was chosen.

**The one thing here that is NOT in the registration** is `mixing_ndim` 8 -> 16
and `electron_maxstep` 200 -> 400, which A6.5(2) does not name. They are declared
as a dated extension of the ladder for relaxations: numerics only, with conv_thr,
forc_conv_thr, degauss, smearing, nspin, mixing_mode and mixing_beta untouched.
Its authority is bounded by construction -- the only thing this round can do is
FILL a gap that (iii) would otherwise leave. If both decks fail, the recorded
outcome is identical to what (iii) alone would have recorded, so the extension
cannot move a threshold, change a convergence criterion, or flip a verdict.

**An open question for the entrant, deliberately not settled here.** The Ti arm
runs nspin = 1, inherited from `qe_slab.py`'s d0 path. Running it nspin = 2
throughout would be strictly more general -- a closed-shell system converges to
the nspin = 1 answer with totmag -> 0 -- and would remove the radical-state
pathology at its root rather than routing around it. It is not done here because
it is a CONVENTION change across all four Ti states and 24 already-banked SCFs,
and conventions are the entrant's to set, not the assistant's.

**Calculation-class disclosure (added 2026-08-29, after the wave-4 audit).** The
scale overage in §2 was disclosed against A6.6's "~140 SCFs"; the same A6.6 sentence
carries a second clause that was not addressed, and is addressed here. A6.6
(docs/43:1283-1289) registers block 6A as "**~160 fixed-geometry SCFs and zero
relaxations**" and states it "does **not** license ... any relaxation in any cell."
The Ti arm is built on relaxations: 4 in tranche 3 (slab + 3 adslabs) and 3
escalation repairs (`s0_OOH_r1`/`r2`/`r3`), seven in total, all in the 1×1 cell.
A7.4's gate (g) licenses exactly ONE TiO₂ relaxation, in the 2×1v cell, for timing —
not these. So they are new compute outside A6.6's declared footprint, and are stated
here rather than absorbed.

What they are and are not: they are the geometry INPUT the Ti ladder stands on, not
A0 points. Every Ti number this campaign scores is a fixed-geometry single-point SCF,
and A6.4 is untouched. Their warrant is later and registered: A7.2/A7.3 (deposited
2026-08-16) register a six-metal A0 census that names Ti a blind metal, and A7.3
conditions its own denominator on "a converged *OOH geometry" — which presupposes
that a Ti *OOH geometry can exist. TiO₂ had none anywhere in the campaign, so the
relaxations are the only route to the rows those two predictions require. That is an
explanation of why they were run, not a licence; the licence is the entrant's to
grant or withhold when countersigning this document. If withheld, the consequence is
already registered: A7.3's denominator shrinks and the Ti rows are WITHDRAWN-UNSCORED
under A7.7.

**[§3c LICENCE 2026-08-31: GRANTED — EXECUTED UNDER DIRECTIVE, COUNTERSIGNATURE
PENDING; s0_OH@u900 FIRST among Ti compute]** — executed 2026-08-31 under the
entrant's recorded directive (docs/66 §1, quoted verbatim there; the mapping
draft and adversarially verified, docs/66 §2 row 1; the entrant may override by
a later dated line). **Because this is the one signature that MOVES A BANKED VERDICT
(the A7.3 denominator, docs/60 §6 fact 5; docs/43 A11.R2 rule (iii) makes it the
sole denominator authority), it completes only at the entrant's own dated
confirmation line in §5 below — and NO TI DECK SUBMITS BEFORE THAT LINE EXISTS.**
The grant as executed covers EXACTLY the seven named relaxations of 2026-08-28/29
(slab, s0_O, s0_OH, s0_OOH, s0_OOH_r1/r2/r3, all 1×1, all already run and banked in
`runs/Ti_slab/`) — **retroactive legitimation of those seven and NOTHING ELSE; it
sets no precedent for out-of-footprint compute and licenses no future relaxation in
any cell. No future out-of-footprint compute acquires a grant/withhold decision
point this way: this one existed because §3c registered the election with the
withhold consequence priced (:200-203); absent such a pre-registered election,
out-of-licence compute is a VIOLATION recorded in the error ledger and its rows are
unusable.** Consequences in force at confirmation: A7.3's denominator stays 6; the
banked NOT MET 3/6 stands scored; every Ti Stage-1 SCF remains additionally gated on
docs/43 A11's items 1–3 elections and the A11.R5 deposit; `s0_OH@u900` runs first
among Ti compute (docs/62 §9 item 3 — a Ti-internal ordering, not a reordering of
§A11.10's Ru-first sequencing). Ti decks may be BUILT and committed under this
executed line (building banks nothing); submission waits.

**Scale update:** the ~246 above becomes ~250 with this round (2 Fe SCF restarts
+ 2 Ti relaxations). Same disclosure stance: stated, not absorbed.

## 3d. What the escalation returned (added 2026-08-29, after it ran)

**Fe s0_O at U = 4.5 -- exactly one of the two converged.** `__r2b`, seeded from
the 22.90 branch, converged in 18 iterations at totmag 23.44 and
E = -2515.36930103 Ry. `__r2`, seeded from the 21.98 branch, failed at 200
iterations still pinned at 21.98 -- the third failure on that branch, after the
original run and the rung-(i) restart. The pre-declared rule ("if exactly one
converges it is the point, labelled with the branch it landed on") settles it
without judgement. The reading is sharper than "two branches, take the lower":
the 21.98 solution appears not to EXIST at U = 4.5, so the SCF failures were the
ladder falling off the end of a branch that terminates between 4.5 and 5.3. The
banked row lands on the ladder's own trend (dG_O 3.981 -> 4.437 -> 4.628 across
U = 3.0/4.5/5.3; eta 0.993 -> 1.196 -> 1.264) and the total energies stay smooth
and monotone across the branch change, so the two branches are near-degenerate
to within the curve's own smoothness. **Fe now scores 8 of 8 with no holes.**

**Ti s0_OOH -- the diagnosis was right, and the plain continuation was not
enough.** `s0_OOH_r2`, continuing the old walk, failed again after 19 ionic
steps. `s0_OOH_r3`, restarted from the re-anchored geometry, **converged**: 52
ionic steps, ZERO SCF failures anywhere in the walk, final force 0.003092
Ry/bohr, 367 meV below where r2 stalled. The relaxed adsorbate sits at

    d(anchor O, nearest Ti) = 2.041 A     O-O = 1.371 A     O-H = 0.986 A

against *O at 1.735 A and *OH at 1.829 A on the same surface. **TiO2 binds
*OOH**, a little more weakly than *O and *OH, as OER scaling expects. The
original chain missed it only because every Ti adsorbate starts ~3.2 A out --
1.1 A beyond the bond. Had the campaign stopped at A6.5(2)(iii), it would have
banked a gap where a bound state exists, and the *OOH-does-not-bind reading
would have been available to anyone reading the failure. It was wrong.

The numerics that made the relaxation converge do not reach any banked number:
`probe_decks.write_probe` emits its own `&ELECTRONS`, so every Ti A0 SCF runs
the campaign's standard conv_thr 1e-6 / local-TF / beta 0.3 / maxstep 200. The
builder asserts this, and separately proves the base-deck machinery has not
drifted by rebuilding an already-committed deck byte-for-byte before writing
anything.

**What the last 8 jobs decide.** A7.2 is already CONFIRMED and cannot be harmed
(more metals can only add flips). A7.3 (P-FLOOR-U) is genuinely at stake: it
stands at **3 of 5 against a registered threshold of >=4**, with Cr 0.3435,
Fe 0.6102 and Mn 0.6307 over the 0.10 V floor and Ru 0.0922 and Ir 0.0637 under
it. Ti is the only metal left. That currently-failing state was scored, printed
and banked BEFORE these decks were built (`docs/figs/a0main_readout.json`,
provenance stamp 2026-08-29), which is what makes the eventual number
believable either way.

## 4. What the extension can and cannot change

- **A6.3's ordering verdict (INVERTED) is untouched** — it is a Ru/Ir statement, scored
  2026-08-28, and Mn/Fe/Ti do not enter it. The extension completes the *span* clause
  ("the 3d metals"), not the prediction.
- **A7.2 is already CONFIRMED** (Cr, Ru, Ir all flip; ≥3 of 6 is monotone — additional
  metals can only add flips). Mn/Fe/Ti complete the census from 3/6 scored to 6/6.
- **A7.3 (span(c_M)/2 at fixed endpoints)** becomes scorable on the full 6-metal
  denominator once Ti's *OOH converges; its own text conditions the denominator on "a
  converged *OOH geometry", so a Ti convergence failure shrinks the denominator rather
  than blocking the readout.
- **η(Fe) at production is immune** to the *OOH branch question (pls = 2, ~2.0 eV
  margin, docs/41 §6d) — but c_M and the flip bracket are not, which is why the branch
  protocol exists.

## 5. The entrant's actions

1. Re-author / countersign this document (no thresholds to set — the only judgment call
   already made is the three pilot guesses, and they are launched).
2. Deposit it (own Zenodo record, or alongside A10 on Sep 18 — entrant's choice; the
   registration's own instrument is the dated deposit).
3. The RCAC ticket and the S1 CI files remain open from before (tasks/todo.md).

**[COUNTERSIGN EXECUTED UNDER DIRECTIVE 2026-08-31 — CONFIRMATION PENDING]** — act 1
was executed under the entrant's recorded directive (docs/66 §1); because the §3c
grant moves a banked verdict, the countersignature COMPLETES only at the entrant's
own dated confirmation line below. Until that line exists, the Ti rows' status stays
exactly as docs/60 §6 fact 5 left it (provisional on a signature) and no Ti deck
submits. Act 2: vehicle elected OWN VERSION NOW (docs/66 §2 row 18); the dated DOI
line below is act 2's discharge when the deposit publishes.

**[§3c CONFIRMED 2026-08-31]** — the entrant, in session, replying to the
two-acts summary that named this gate explicitly ("Confirm the §3c grant — one
dated line in docs/59 §5 … Ti's 24 decks submit the moment that line exists"):
"i published the deposit, submit everything" (verbatim). The grant stands; the
countersignature is complete; the Ti manifests may submit. (Recorded by the
scribe from the entrant's words, the docs/66 §1 instrument; override open as
always by a later dated line.)

**DOI line (2026-08-31):** **10.5281/zenodo.22213117** — docs/59 in its
countersigned state deposited as part of the A11 new version of concept record
10.5281/zenodo.21963143 (restricted access: DOI + timestamp public, files
closed until report submission; file `59-a0-roster-correction-2026-08-28.md`,
20,993 bytes, md5 `2dba12d4eb2e44e0d941038ea867bd68`, the working-tree
serialization of commit `6fe167b` per `docs/deposits/2026-08-31-A11.manifest.txt`).
Act 2 of §5 is discharged. Text added after publication; the deposited file is
the frozen artifact.
