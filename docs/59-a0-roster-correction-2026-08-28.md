# 59 — Correction of record: the A0-main metal roster, and its completion — 2026-08-28

**Status: DRAFT for the entrant.** AI-drafted disclosed infrastructure (per the AI-use
log convention of A7.0/A9); the entrant re-authors and deposits. Nothing in this document
invents a threshold; every rule it cites is quoted from an already-deposited registration.
**Until deposited, its authority is its commit timestamp** — committed and pushed before
any tranche-2/3 job ran, which is the property that matters.

## 1. What went wrong (the correction proper)

docs/43:279 sets the scope rule: changes happen "only through its own dated amendment."
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
