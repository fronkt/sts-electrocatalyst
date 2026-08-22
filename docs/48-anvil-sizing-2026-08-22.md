# 48 — What an S3 relax actually costs on Anvil

**Date:** 2026-08-22
**Jobs:** Anvil 20083509, 20083510, 20083511, 20083513, 20083514 (`anvil/50_scaling.slurm`)
**Deck:** `runs/s0/g_tio2_timing/s0_OOH__2x1v_off.in` — the gate (g) TiO2 2×1v relax,
39 atoms, ecut 80/640 Ry, 4×4×1 mesh = 16 k-points with `nosym`.
**Status of this document:** measurement record. Nothing here is banked science; every
arm wrote into `$PROJECT/scaling/`, which is not mirrored into the runs tree. No
threshold is set here — the schedule consequences are the entrant's to accept or reject.

## Why this was measured

Every S3 schedule and SU figure in the project descends from an estimate of ~4 h per
2×1v relax. S0 gate (g) already falsified it: 8h00m WALL on 20 ranks and **still not
converged** — 11 ionic steps, total force 0.0298 against a 0.005 target, clean stop on
`max_seconds`. But that measurement was taken on Vast box 47662258 (EPYC 7B12, Zen 2),
which no longer exists, so it could not be used to size anything on Anvil (EPYC 7763,
Zen 3) either.

Second question, worth asking once: `shared` bills `TRESBillingWeights=CPU=1.0`, i.e.
cores × hours and nothing else. Wall-clock and cost are therefore **separate knobs**. If
`pw.x` scales, a wider job is not much more expensive — it is mostly just sooner. The
deck has 16 k-points under `nosym`, so `-nk` can go to 16: one pool per k-point, the
cheapest parallel axis there is.

## The arms

Five arms, identical deck, `max_seconds = 2400`, one node each, `-n` matched to the rank
count so no arm is billed for cores it does not use.

| arm | ranks | −nk | binding | step 1 | later steps (mean) | complete steps in 40 min |
|---|---|---|---|---|---|---|
| A | 20 | 4 | none | **1801.1 s** | — (cap hit mid-step-2) | 1 |
| B | 40 | 8 | none | 1078.9 s | 635.2 s | 3 |
| C | 80 | 16 | none | 786.8 s | 319.0 s | 6 |
| D | 80 | 16 | core | **643.5 s** | 298.2 s | 6 |
| E | 128 | 16 | core | **431.9 s** | **209.5 s** | 10 |

**The arms are on the same BFGS path.** Force at each ionic step, Anvil arm E against the
banked Vast run: 0.432004/0.432021, 0.256210/0.256221, 0.157043/0.156790,
0.078165/0.078070, 0.065832/0.065592, 0.046138/0.046225. The parallel layout changes the
clock and not the trajectory, so these timings compare like with like.

## Three results

**1. Zen 3 is 1.52× Zen 2 at the same shape.** Same deck, same 20 ranks, same `-nk 4`:
Vast's first ionic step took 2745.5 s, Anvil's took 1801.1 s. That is the pure hardware
term, and it is the only part of the speedup that costs nothing at all.

**2. Rank binding is worth 18% and is free.** Arms C and D differ in one flag. `--bind-to
none` — the driver's setting, inherited from a Vast container where binding failed — costs
786.8 s per first step against 643.5 s pinned, on a dual-socket 64-core-per-socket EPYC
where unpinned ranks migrate across NUMA domains. Binding changes placement, not rank
count or reduction order, so it cannot change a number; it only changes the clock.

**3. Wall-clock is nearly free to buy.** SU per ionic step, which is what the allocation
is actually spent on:

| arm | ranks | SU for step 1 | SU per later step | wall per later step |
|---|---|---|---|---|
| B | 40 | 11.99 | 7.06 | 635.2 s |
| C | 80 | 17.48 | 7.09 | 319.0 s |
| D | 80 | 14.30 | 6.63 | 298.2 s |
| E | 128 | 15.36 | 7.45 | 209.5 s |

**The SU column is flat — 6.6 to 7.5 — while the wall column falls 3×.** Going from 40
ranks to 128 costs about 5% more SU per ionic step and finishes each one three times
sooner. Arm E is the whole node, which is also why it beats arm C on both axes at once:
no other job sharing its memory bandwidth.

## What one full relax costs

The force sequence decays ~0.93 per step in its tail (0.0369 → 0.0348 → 0.0321 →
0.0298), so reaching the 0.005 target from step 10 needs roughly 25 more steps — call the
total **25–35 ionic steps**, and treat the upper end as the planning number since BFGS
crawling near the minimum is exactly what the tail already shows.

| shape | wall per relax | SU per relax |
|---|---|---|
| 20 ranks, −nk 4, unbound (today's production shape) | **~12 h** | ~237 |
| 128 ranks, −nk 16, bound | **~1.5–2.1 h** | ~194–269 |

Roughly the same spend, between five and six times sooner. For comparison, the same relax
on the destroyed Vast box was on track for ~18 h and never finished one.

## What this means for the schedule

At ~2 h and ~270 SU per 2×1v relax, the remaining balance of **99,707 SU buys about 370
of them**, and eight can run at once on eight of `shared`'s 250 nodes without any special
arrangement. Compute is not the binding constraint on S3 — the deck count and the Oct 15
freeze are.

Two caveats that are not about speed:

- **`shared` reports `MaxTime=UNLIMITED`**, so the 48 h cap in `40_wave.slurm` is a choice
  and not a limit. At arm E's rate a relax that needs 60 ionic steps still lands inside
  4 h, so the cap is no longer the risk it was at 20 ranks.
- **Widening a wave is a two-step act by design.** `queue_r1.sh` refuses any NP that
  disagrees with a manifest's `# NP=<n> NCONC=<n>` directive, because a manifest's
  `max_seconds` were sized at its declared NP. `41_submit_wave.sh` now takes ranks as its
  third argument and passes the same number to both `sbatch -n` and the driver, so the
  guard still fires. A manifest that is widened without editing its directive is refused,
  which is correct.

## Not measured here

- Whether `--bind-to core` should become the driver's default. It is an 18% gain and
  provably cannot move a number, but the driver is shared with every banked run and
  changing it is a decision, not a measurement.
- Scaling past one node. Every arm here is `-N 1`; 128 ranks is the whole node and the
  point at which inter-node latency would enter.
- Whether the Cr Hessian decks want a wider shape. They are fixed-geometry SCFs, not
  relaxes: gate (d) measured 4h05m at 20 ranks on Vast, which is ~2.7 h on Anvil at the
  same shape, and all 19 can run concurrently as an array. At ~1,030 SU for the set there
  is no case for widening them.

## Cost of this measurement

281 SU. Balance after: 99,707 of 100,000.
