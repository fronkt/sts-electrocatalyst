# Decision sheet — 2026-08-24 (post-S3-arc rulings)

**Provenance.** The four decisions parked at the S3 arc close (docs/45 records of
2026-08-24) were put to the entrant with options and recommendations. The entrant
delegated by criterion, in writing:

> "Which option has the most scientific impact and heightens my chances for STS 300?
> If it's compute, no matter, go ahead."

Rulings below were therefore selected by the AI assistant under that delegated
criterion and are disclosed as such (supporting infrastructure; the entrant may
override any ruling by a later dated line). Compute was pre-authorized by the same
message. Ruling date: 2026-08-24.

## Ruling 1 — GATE-1 below-parent drift rows: §5-strict re-relax

Fe `s0_OOH__1x1_off` (child −384.30 meV below parent) and Mn `s0_OOH__2x1v_off`
(−20.62 meV): the docs/52 C9 **§5-strict arm is taken** (the registered swap of the
am4s2 default) — re-relax IN the deeper electronic state and repeat GATE-1, rather
than quoting the child single-point. Rationale under the criterion: the child energy
is a lower bound at a geometry optimized for the *wrong* electronic state; the Fe
shift is volcano-visible (≥0.38 eV), so the true minimum of the deeper branch is the
scientifically defensible number. Both readings are still printed per row (docs/52).
Mechanics: `__basin` decks = the row's `__g1` child with `calculation scf→relax` and
a new prefix — by construction identical to the original parent deck except
{prefix, starting coordinates}; the cold start at the parent-final geometry provably
lands in the deeper state (the child did). Each converged `__basin` relax owes its
own `__g1` child (wave 4). Until that loop closes, the rows are PENDING-RERELAX in
any S6-facing table; the parent and child energies are both quoted, neither banked
as final.

## Ruling 2 — electron_maxstep 200 → 500 on the 11 rung-(iii) decks (dated recipe line)

The 9 wave-1 NOT_CONVERGED relax gaps (Co ref__2x1v, Co s0_OH__1x1_off, Co
s0_O/s0_OH/s0_OOH__2x1v_mir, Co s0_OH/s0_OOH__2x1v_off, Ni s0_OOH__2x1v_mir/off) and
the 2 rung-(iii) `__g1` children (Co s0_O__1x1_off__g1, Ni s0_OH__2x1v_off__g1) are
re-attempted with **exactly one registered-recipe token changed:
`electron_maxstep = 200 → 500`**, at each deck's last-attempted mixing_beta (the
`.retry_bh.in` values: 0.15 for the gaps; 0.075/0.15 for the children). This
follows the ledger's own registered suggestion (docs/45:122-126, the Co ref
NEAR-MISS signature: monotonic creep to 2.63e-6 vs 1e-6 at step 200, magnetization
stable). This is an entrant dated line, NOT an A8.4 ladder rung — the ladder is
exhausted for these decks and its rung-(iii) records stand as attempt history
(`.out` files preserved; new attempts run under the `.retry_ms.in` suffix).
Converged wave-1 results are untouched (A8.8 no-replacement). A deck that fails
again at maxstep 500 returns to NOT_CONVERGED with three configurations on record.
Newly converged relaxations owe `__g1` children (wave 4).

## Ruling 3 — Cr *OOH 2×1v mir arm: energy of record = the escape minimum

The arm's energy of record is **−3188.71606 Ry** (`runs/s3/Cr/s0_OOH__2x1v_escape.out`),
the genuine minimum proven by the 2026-08-24 re-Hessian (all 9 adsorbate modes real,
gate-clean, floor-robust, same magnetic state M=23.00). The mirror geometry's
−3188.70497 Ry is retained as the **saddle diagnostic** (i244.7), not a state energy —
a saddle is not a state. The off arm (−3188.79232 Ry) is unaffected; the mir-vs-off
gap remains the symmetry-trap measurement and is now quoted minimum-to-minimum
(76.3 meV) with the saddle→minimum pair as the mechanistic exhibit.

## Ruling 4 — RCAC ticket: drafted for the entrant to submit

Nodes a024 and a088 are back in Anvil's general pool (checked 2026-08-24: a024
ALLOCATED, a088 MIXED) with no evidence of repair. Ticket text with the node↔outcome
evidence is drafted at `anvil/rcac_ticket_draft_2026-08-24.md`; **submission is the
entrant's action** (nothing is sent by the assistant). Our own launches remain
protected by `EXCLUDE=a024,a088` regardless.

## Launch record

Round 3 = the 13 decks of `runs/s3/m_s3_round3.txt` (11 `.retry_ms.in` + 2
`__basin.in`), built by `src/dft/build_s3_round3.py` (single-purpose diffs
assert-verified; deterministic). Submitted via `anvil/43_submit_s3_wave1.sh` with
`EXCLUDE=a024,a088`; array ID in docs/45.
