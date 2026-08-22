# 47 — AMENDMENT 8, DRAFT — the S3 protocol, and the move off Vast

**Status: DRAFT for the entrant's review. Not registered, not deposited, not binding.**

This file is AI-drafted research infrastructure under A7.7 (amendments are AI-drafted
and disclosed; the report paraphrases and never copies). **Every threshold below is
marked THRESHOLD and must be re-authored by Frank in his own words before this text is
appended to docs/43 and re-deposited.** A number proposed here is a proposal. It becomes
a registration only when he writes it.

**Deadline:** Aug 24 2026, before the first S3 deck launches (docs/45 §D).
**Governs:** S3 — `tier_v3` crossed coverage × symmetry × basin over 8 metals; the dy
ladder; GATE-1 depth; the CONFOUND rule; P-SYMCOV; the convergence-failure budget.
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

**A consequence worth registering explicitly.** Gate (h) returned 4/4 ADOPT_AFM on the
RuO2 anchors (−144, −80, −85, −111 meV against NM, against a −20 meV rule), and the
adsorption energies move 33–64 meV once the anchor is AFM. Those four AFM points are
single points on NM-relaxed geometries — P11 limit (ii), a lower bound. Adopting AFM as
the anchor's magnetic row therefore owes **four 2×1v AFM relaxations**, which are S3-class
jobs and are priced in A8.6, not in S0's closed budget.

## A8.6 — Measured Anvil cost

*(filled from jobs 20083509–20083514; see docs/48)*

## A8.7 — What this amendment does NOT license

- It does not reopen any closed S0 gate.
- It does not license a new tier, a new adsorbate, or an oxyhydroxide phase.
- It does not change the production convention U = 0 on Ru and Ir.
- It does not permit re-running a banked Vast number on Anvil and **replacing** it. A
  re-run is a new measurement reported alongside, or a correction with a stated reason —
  never a silent overwrite. The banked tree is read-only by construction: every parity and
  sizing job writes into its own isolated directory.
- It does not license loosening the parity threshold to accommodate a measurement. A gate
  widened until the data fits is the failure mode this project exists to indict.

## A8.8 — Deposit obligation

Per A7.8, docs/43 complete (A1–A8) is re-deposited to Zenodo as a new version of record
10.5281/zenodo.21963144 — restricted access, DOI and timestamp public, files closed until
report submission — **before the first S3 deck launches**. The new version DOI is recorded
here in a dated line when it exists.
