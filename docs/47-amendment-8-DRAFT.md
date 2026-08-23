# 47 — AMENDMENT 8, DRAFT — the S3 protocol, and the move off Vast

**Status: ADOPTED by the entrant 2026-08-23 (reviewed via docs/52; "they pass with me") and appended to docs/43 as AMENDMENT 8. The registered text is docs/43's; this file is the historical draft, kept verbatim below this line.**

This file is AI-drafted research infrastructure under A7.7 (amendments are AI-drafted
and disclosed; the report paraphrases and never copies). **Every threshold below is
marked THRESHOLD and must be re-authored by Frank in his own words before this text is
appended to docs/43 and re-deposited.** A number proposed here is a proposal. It becomes
a registration only when he writes it.

**Deadline:** Aug 24 2026, before the first S3 deck launches (docs/45 §D).
**Governs:** S3 — `tier_v3` crossed coverage × symmetry × basin over 8 metals; the dy
ladder; GATE-1 depth; the CONFOUND rule; P-SYMCOV; the convergence-failure budget; and, added
2026-08-23, block 1C's σ_F instrument question (A8.7).
**Also carries, because docs/45 §D and anvil/README.md both assign it here:** the
migration of all remaining compute from Vast box 47662258 to Purdue Anvil.

---

## A8.0 — Why this amendment is being written now, and what changed under it

A8 was scheduled on 2026-08-16 to register the S3 protocol. Between then and now three
things happened that A8 must absorb — two of them change what S3 costs, one changes what
S3 must measure.

1. **S0 closed** (2026-08-22, 25/25 jobs, 0 SCF failures). Its nine gates settled the
   open protocol questions S3 inherits: the production cell is 2×1v, `noinv` is
   droppable, the mirror arm keeps symmetry on, ortho-atomic projectors are accepted,
   1e-10 is affordable at 1.71× cost, and BEEF is reachable only through
   `calculation='ensemble'`.
2. **Vast box 47662258 was destroyed** (2026-08-22, zero instances). All remaining
   compute moves to Anvil under ACCESS allocation CHE260157. That move is an S3+
   decision and anvil/README.md already routes its registration here.
3. **Gate (g) falsified the S3 cost model** — and it did so on hardware that no longer
   exists, so the falsification itself had to be re-measured on Anvil (A8.6).

---

## A8.1 — The S3 design, restated so it can be attacked

S3 computes `tier_v3`: the corrected tier over 8 metals, crossing the three factors that
S0 and block 1A each measured in isolation.

| factor | levels | why it is crossed rather than fixed |
|---|---|---|
| coverage / cell | 1×1, 2×1v | block 1A: 7 of 9 off-arm rows moved > 0.10 eV; the 1×1 cell weakens binding through the periodic image by 0.11–0.36 eV. The 1×1 rows are not discarded — P7 was measured in 1×1, and the contrast leg is what prices error class 7. |
| symmetry | off-plane (`nosym` + displacement), mirror (symmetry ON) | S0(c) settled that the mirror arm runs sym-ON. The symmetry trap is **coverage-conditional**: 0.291 V on Ir at 1×1, −0.018 eV at 2×1v half coverage. A single-coverage symmetry measurement would have reported either number as *the* effect. |
| magnetic basin | production seed + second seed | error class 2. Restored beyond *OOH-only wherever triage allows. |

**The crossing is the point.** Each factor has already been shown to change the answer by
more than the 0.03–0.08 V separations the screen ranks. What has never been measured is
whether they are additive. S0's interaction probe found ADDITIVE ×5 with one INCONCLUSIVE
row (Ir *OOH, 0.266 eV).

**THRESHOLD (proposed):** a cell × symmetry interaction term is reported NON-ADDITIVE
where |E(both) − E(cell) − E(sym) + E(neither)| exceeds **0.10 eV** — the same bin block
1A used, so the two are comparable without a conversion.

## A8.2 — P-SYMCOV: the symmetry claim is coverage-indexed or it is not made

Registered as a wording obligation with teeth, because this campaign has already made the
mirror-image mistake once.

No statement of the form "the symmetry trap is worth X V" may appear in any output of
this project without the coverage at which X was measured attached in the same sentence.
The measured pair — 0.291 V (Ir, 1×1) and −0.018 eV (Ir, 2×1v half) — is a **range across
coverage**, not a value with noise. A reader given only the first number is told the trap
is a third of a volt; a reader given only the second is told it is nothing. Both readings
are wrong, and the campaign's own withdrawn headline is what a wrong reading costs.

**THRESHOLD (proposed):** P-SYMCOV is satisfied when, for every metal in S3, the symmetry
effect is reported at **both** coverages, or the missing cell is reported as a gap. A
metal with only one coverage is **not** averaged into any symmetry statistic.

**Both outcomes, stated now (added 2026-08-23 — A9.4 found that round-2 F9's "both
outcomes … pre-written in Amendment 8" was not in fact here).** P-SYMCOV is a wording
rule, but it rides on a measurement — the coverage-dependence of the symmetry effect —
and that measurement has two outcomes. **Claim scope if the effect is coverage-dependent
on most metals** (the Ir pattern, |ΔΔE(1×1) − ΔΔE(2×1v)| large): the symmetry trap is
reported as a coverage-conditional effect, the range stated per metal, and the 1×1
numbers of the literature census (A9) are read as the high-coverage end of that range.
**Claim scope if the effect is coverage-independent** (the two cells agree within the
basin CONFOUND tolerance on most metals): the trap is reported as a property of the
placement, not the cell; the 1×1 legacy numbers stand as-is; and P-SYMCOV reduces to the
reporting rule with no "range" to state. **THRESHOLD (proposed) for "most":** ≥ 5 of the
8 metals with both cells measured; a metal with one cell is a gap, as above. Neither
outcome changes what S3 computes; they change one sentence, and the sentence is the
entrant's. The solvation × coverage non-additivity row (docs/45 §B row 9) is **carried
here** as an appendix prediction with its TRANSFERRED status and the swept ΔG_OOH band
(A9.5 flagged the ownership; A8 takes it — it is a coverage statement, not a census one).

## A8.3 — The CONFOUND rule, extended to the magnetic basin

§5 and amendment 4 already refuse a symmetry comparison whose two members relaxed into
different geometries. S3 needs the magnetic analogue, because the campaign has now
measured it twice.

**THRESHOLD (proposed):** a pair whose members differ in converged total magnetisation by
more than **0.05 µB** is **CONFOUNDED** — its energy difference mixes the intended
contrast with a basin change — and is excluded from the contrast statistics and reported
separately, exactly as a geometry confound is. The 0.05 µB figure sits far below the
drifts actually observed (11.00 → 14.90 and 11.00 → 14.71 µB) and far above SCF noise in
a converged moment.

**Evidence this is not hypothetical.** Re-scoring the LIT-3 GATE-1 family on 2026-08-22
against its own parents:

| deck | parent E (Ry) | parent µ | child E (Ry) | child µ | Δ child−parent |
|---|---|---|---|---|---|
| `oosh__1x1_off_magm` | −1636.57116531 | 11.00 | −1636.57116516 | 11.00 | +0.002 meV |
| `s0_OOH__1x1_yaw270_magm` | −1636.56955293 | 11.00 | −1636.56955277 | 11.00 | +0.002 meV |
| `s0_OOH__1x1_yaw270_magp` | −1636.56975169 | 11.00 | −1636.56975161 | 11.00 | +0.001 meV |
| `oosh__1x1_off_magp` | −1636.57118655 | 11.00 | −1636.57057718 | **14.90** | **+8.29 meV** |
| `s0_OOH__1x1_yaw90_magm` | −1636.56961270 | 11.00 | −1636.56610153 | **14.71** | **+47.77 meV** |

The three rows that held their moment reproduce to 0.002 meV. The two that changed moment
are the two that move — and both move the **wrong way**: the fixed-geometry child sits
*above* its own relaxed parent. For a re-run at the parent's own relaxed geometry that is
backwards, so it is a diagnostic, not a result.

**THRESHOLD (proposed):** a `__g1` child that lands above its parent by more than **1 meV**
is refused and re-run from the parent's converged density. If the second attempt also
lands above, the pair is recorded MULTISTABLE with both numbers, and neither is banked as
the state's energy.

## A8.4 — Convergence-failure budget (error class 5)

Co *OOH failed 4 times and Ni *OOH 5 times in earlier waves, and those failures were
dropped silently. A dropped non-convergence is a selection effect: the states that fail
are the magnetically frustrated ones — exactly the ones carrying the effect.

**THRESHOLD (proposed):** S3 records a **per-metal, per-state convergence-failure rate**
as a reported quantity, not a log artifact. The escalation ladder is A6.5's, unchanged:
restart from a converged neighbour's density → halve mixing β → record NOT_CONVERGED and
plot as a gap. A metal whose failure rate exceeds **20%** on any state has that state's
contribution to the ranking marked low-confidence in the report rather than dropped.

## A8.5 — The move to Anvil, registered as a change of machine, not of method

The QE build is pinned by an explicit conda lock to the same version and the same
libraries; the decks, the driver, and the pseudopotentials are byte-identical (md5
verified on both ends). What is not identical is the microarchitecture — Vast EPYC 7B12
(Zen 2) against Anvil EPYC 7763 (Zen 3), which dispatch different OpenBLAS kernels.

**THRESHOLD (proposed, and already applied):** an Anvil re-run of a banked deck agrees
when |ΔE| ≤ **1e-5 Ry**. The first attempt failed at −8.28 meV; the diagnosis is A8.3's —
the reference chosen was one of the two BASIN_DRIFT rows. Against its own parent, the same
Anvil number agrees to **6.7e-7 Ry (0.009 meV)**. The panel of clean spin-polarised rows
is in docs/46.

**THRESHOLD, entrant's call:** whether the migration is certified is Frank's decision,
made against the panel in docs/46, and it is enforced mechanically — no wave launches
until `$PROJECT/parity/PARITY_PASS` exists.

**What ran on Anvil before this amendment's deposit (added 2026-08-23, so the record is
in one place; every item is a run of already-DEPOSITED-amendment work under the
PARITY_PASS gate, none of it S3):** the block 1C Cr Hessian waves (jobs 20085020,
20089685 + retry 20090507 — docs/49); the parity control and 5-deck panel (20082656,
20082912 — docs/46); the S3 sizing arms (20083509–14 — docs/48); the S0 gate (i) SnO₂
arm (20094699 — **PASS**, 1.188 meV/atom, docs/51), which anvil/README.md's earlier "S0
stays on Vast" line predates — the box was destroyed with the arm still
precondition-deferred, so completing gate (i) on Anvil is the only way it completes; the
LIT-2 GATE-1 children for the two Cr termination relaxations (20094768 — both AGREE,
+0.004 meV); and the LIT-2 Ru `cov_2OH__2x1_off` **re-run of an unbanked row**
(20094762) — its Vast output reached `JOB_DONE` 2026-08-14 but was never retrieved
before the box's destruction; no number was ever banked, so A8.8's no-replacement clause
does not bite, and the manifest header (`runs/probe/m_lit2_ru_rerun.txt`) records the
loss. This paragraph is the correction-of-record for that loss.

**A consequence worth registering explicitly.** Gate (h) returned 4/4 ADOPT_AFM on the
RuO2 anchors (−144, −80, −85, −111 meV against NM, against a −20 meV rule), and the
adsorption energies move 33–64 meV once the anchor is AFM. Those four AFM points are
single points on NM-relaxed geometries — P11 limit (ii), a lower bound. Adopting AFM as
the anchor's magnetic row therefore owes **four 2×1v AFM relaxations**, which are S3-class
jobs and are priced in A8.6, not in S0's closed budget.

## A8.6 — Measured Anvil cost

Measured 2026-08-22 on the gate (g) deck itself, five arms, docs/48. The arms are on the
same BFGS path as the banked Vast run (forces agree step for step to 4 significant
figures), so the timings compare like with like.

| shape | wall per 2×1v relax | SU per relax |
|---|---|---|
| 20 ranks, −nk 4, unbound — today's production shape | ~12 h | ~237 |
| 128 ranks, −nk 16, bound — one whole node | **~1.5–2.1 h** | ~194–269 |

Three facts the schedule now rests on, none of them estimates:

1. Zen 3 is **1.52×** Zen 2 at identical shape (Vast 2745.5 s per first ionic step,
   Anvil 1801.1 s).
2. **SU per ionic step is flat** from 40 to 128 ranks (6.6–7.5 SU) while wall-clock per
   step falls 3×. On `shared`, which bills cores × hours and nothing else, wall-clock is
   therefore nearly free to buy.
3. `--bind-to core` is worth **18%** against the driver's inherited `--bind-to none`, and
   cannot move a number — it changes rank placement, not rank count or reduction order.

**THRESHOLD (proposed):** S3 relaxations run at **128 ranks, −nk 16, `-N 1`**, with the
walltime cap raised from 48 h to a value the entrant sets — `shared` reports
`MaxTime=UNLIMITED`, so 48 h was never a limit, and at the measured rate a 60-step relax
lands inside 4 h anyway.

**Not proposed, flagged instead:** whether `--bind-to core` becomes the driver's default.
It is free and provably number-neutral, but `queue_r1.sh` is shared with every banked run
and changing it is a decision rather than a measurement.

**Consequence for the budget.** At ~270 SU per relax the remaining 99,707 SU buys about
370 of them, eight at a time on eight of `shared`'s 250 nodes. Compute is no longer the
constraint on S3; the deck count this amendment fixes is.

## A8.7 — Block 1C's instrument question: what "measured force noise" is, and where amendment 2's escalation leads

**Written 2026-08-23 from docs/49. This section decides nothing. It puts three questions the
Cr 2×1v Hessian surfaced in front of the entrant with the measured consequences of each
answer stated — because the verdict label of block 1C turns on them, and a verdict-bearing
instrument choice is his under P-AUTHORSHIP and A7.7. It is also written with the outcome
known, and says so: docs/49 shows the spectrum under every option, so whatever is chosen
here must be chosen for a stated reason that does not reference which verdict it yields,
and the report must carry both labels if the reason is contestable.**

**What is not in question.** Block 1C ran 38 clean SCFs on Cr *OOH in the 2×1v production
cell at two displacements; one magnetic basin (M = 23.00 throughout); `conv_thr 1e-10`
reached on every deck; one out-of-plane, hydrogen-carried imaginary mode at i244.7
(δ = 0.01 Å) and i242.8 cm⁻¹ (δ = 0.02 Å), 0.8 % apart, f_y = 1.00; eight real modes
agreeing to ≤ 0.6 %; the hydrogen's out-of-plane energy curvature negative and quadratic
in δ; the mirror-identity force noise at 1.75e-7 / 2.08e-7 Ry/bohr (docs/49 §3, §4a).

**Question 1 — the σ_F instrument.** docs/43 §3-A.3 registers the floor as max(50 cm⁻¹,
3σ) "with σ propagated from the measured force noise". `hessian_analyze.py` measures σ_F
from the Hessian's own asymmetry |H − Hᵀ| (§3-A.4's observable). docs/49 §4–4b measured
that on this system that asymmetry is truncation error at every block — the (y, xz) cross
block scales exactly as a forward difference (σ_F ×4.00 when δ doubles), every other block
exactly as a central difference (×7.85 against an expected ×8) — and nowhere as noise
(×1). docs/43 §3-A.8 and am.4 §7 item 4 already classify the cross block as "structurally
zero … measure noise, not physics" and demoted Q5 on that ground; the measurement says it
is not even noise. The two readings of "measured force noise":

| reading | σ_F (δ 0.01 / 0.02) | 3σ floor on mode #0 | effective floor | block 1C label |
|---|---|---|---|---|
| (a) asymmetry-based, as coded | 2.99e-5 / 1.20e-4 | i265 / i374 | i265 / i374 | UNDERPOWERED / VOID; REFUTED and CONFIRMED unreachable at any δ |
| (b) force noise from identities the SCF does not enforce (the Q6 mirror identities; `hessian_mirror_noise.py`) | 1.75e-7 / 2.08e-7 | ≈ i21 / i15 | **i50** (the declared minimum) | scored against i50, with the mode at i243–i245 and f_y = 1.00 |
| (c) asymmetry-based on the non-cross pairs only | 1.74e-6 / 1.37e-5 | i64 / i126 | i64 / i126 | passes at δ 0.01, UNDERPOWERED (> i80) at δ 0.02 — still an anharmonicity meter |

**THRESHOLD (proposed):** reading (b) is what "measured force noise" means — σ_F is the rms
residual of force identities the SCF does not enforce (mirror identities on a
mirror-symmetric reference), measured on the same decks, reported alongside the
asymmetry diagnostic; the asymmetry is retained and reported as the truncation-error
diagnostic it is. Reason offered, independent of outcome: a noise estimator must be
δ-invariant when the noise is, and (b) is the only one of the three that is (×1.19 vs ×4
and ×7.85). The entrant may instead keep (a) — in which case block 1C is recorded as
UNDERPOWERED/VOID by instrument, not by physics, with the mode reported as a measurement
without a verdict label — or choose (c), or something else. Whatever is chosen, the
choice and its reason are written in his words.

**Question 2 — amendment 2's escalation collides with Q4.** am.2 routes UNDERPOWERED to a
rerun at δ = 0.02 Å. But the Q4b absolute floor is 3√2·σ_design/δ — it falls as 1/δ —
while the forward-difference asymmetry it is tested against grows as δ; and Q4a's σ_F
grows as δ (cross) or δ² (central). So the registered escalation fires Q4a and Q4b by
construction once they were anywhere near threshold at δ = 0.01, which is exactly what
happened (docs/49 §2). Two coherent resolutions, **both proposed, neither chosen here:**
(i) under reading (b) the floor is δ-independent and am.2's rerun keeps its registered
meaning — a harmonic-regime test (passed: 0.8 %) that does not touch the noise floor; Q4
stays a gate on a noise measurement, not on anharmonicity; (ii) alternatively the y rows
return to central differences (the ym decks enter H after Q6 passes), which zeroes the
cross-block asymmetry by construction — at the cost of the ym decks' status as an
independent control, which am.4 §7 fixed for a stated reason. (i) is the smaller change.

**Question 3 — Q4b's standing.** The analyzer labels Q4b "CODE-LEVEL, in no docs/43
clause (N32/N33) — reported, not registered" and nonetheless counts it toward VOID. Either
register it here (with its formula and the reading of σ_design it uses) or demote it to
reported, as Q5 was. **THRESHOLD (proposed):** demote to reported; the gate it duplicates
(Q4a) carries the registered meaning, and a gate that is not registered must not void a
state.

**Consequence for S3 (A8.1 "Cr 1C + re-Hessian at escape").** Every re-Hessian in S3 is on
a mirror-symmetric or near-symmetric reference and will present the same estimator
behaviour; the answer to Question 1 is therefore an S3 protocol parameter, not a Cr
footnote, and must be settled in this amendment before the first S3 Hessian is built.
`hessian_analyze.py` is NOT changed until it is; docs/49 and the banked outputs
(`runs/probe/Cr_hess`, `runs/probe_d02/Cr_hess`) carry the numbers under every reading.

## A8.8 — What this amendment does NOT license

- It does not reopen any closed S0 gate.
- It does not license a new tier, a new adsorbate, or an oxyhydroxide phase.
- It does not change the production convention U = 0 on Ru and Ir.
- It does not permit re-running a banked Vast number on Anvil and **replacing** it. A
  re-run is a new measurement reported alongside, or a correction with a stated reason —
  never a silent overwrite. The banked tree is read-only by construction: every parity and
  sizing job writes into its own isolated directory.
- It does not license loosening the parity threshold to accommodate a measurement. A gate
  widened until the data fits is the failure mode this project exists to indict.

## A8.9 — Deposit obligation

Per A7.8, docs/43 complete (A1–A8) is re-deposited to Zenodo as a new version of record
10.5281/zenodo.21963144 — restricted access, DOI and timestamp public, files closed until
report submission — **before the first S3 deck launches**. The new version DOI is recorded
here in a dated line when it exists.
