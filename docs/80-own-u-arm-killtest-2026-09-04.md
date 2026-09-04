# KILL-TEST VERDICT — the own-U arm. NOT SUBMITTED.

> **Status: the arm as designed did NOT survive. Nothing was built and nothing was submitted.**
> The entrant's sign-off was explicitly conditional — *"If it survives, you have my full sign-off
> to scale up to the 92 SU square and submit"* (2026-09-04). The condition was not met, so the
> authority it carried was never exercised. This document records why, and what replaces it.

An 80-agent adversarial pass: six investigative branches, per-finding refutation, then three
independent attempts to kill the plan (integrity / opportunity cost / technical soundness).
Verdicts: **DO NOT RUN IT**, **RUN IT MODIFIED**, **RUN IT MODIFIED — but not those eight SCFs.**

Every claim below was re-verified by hand against the tree before being written here.

## The gate that was actually asked about — PASSED

The question put was whether a comparison that changes **both** projector and U is interpretable.
It is. Under the ab-initio protocol U is a **mediator** of the projector choice, not a confounder:
the projector *determines* U, so the whole diagonal is attributable to the keyword, decomposing
into a direct effect and a U-mediated one. That reading survived.

**The arm failed on other grounds, and they are worse.**

## F1 — 134 % of the flagship's delta-eta is a table of literature constants, and the raw DFT difference has the OPPOSITE SIGN

Exact, reproduced from committed data. `src/hea_oer/referencing.py:18` hard-codes
`ZPE_TS_CORRECTION = {"OH": 0.35, "O": 0.05, "OOH": 0.40}` (Man 2011 / Valdes 2008).
The atomic leg is pls = 2, so it carries (0.05 - 0.35) = **-0.30**. The ortho leg is pls = 1, so it
carries **+0.35**. From `docs/figs/pproj_readout.json`:

```
delta-eta = 1.6422592 - 1.1554030 = +0.4868562 V
  electronic (raw DFT) : 2.5222592 - 2.6854030 = -0.1631438   <-- ortho is LOWER
  constants  (ZPE/TS)  : +0.35 - (0.05 - 0.35) = +0.6500000
  sum                                            +0.4868562   exact
```

**The projector flips the limiting step, and flipping the limiting step mechanically imports
+0.65 eV from a fixed table.** This is not an error — it is what CHE does and everyone does it.
But the headline number is dominated by the interaction of a pls flip with a constants table, not
by the DFT energy differences, and those constants were never recomputed per projector even though
the projector shifts absolute magnetisation by 0.55-1.57 muB per state.

**Zero-SU obligation: publish this decomposition beside the number, with a +/-0.05 eV sensitivity on
the two constants (approx +/-0.10 V on delta-eta).** Whoever asks this at a judging table asks it
about 0.487 V. Better it appears in our own table first.

## F2 — the pls flip is reproduced by the CELL at fixed projector, and there is no ortho calculation in the cell we adopted

From `docs/figs/a0cell_readout.json`, **atomic projector, U = 7.15 eV, both cells**:

| cell | eta (V) | pls |
|---|---|---|
| 1x1 | 1.1554 | **2** |
| 2x1v | 0.9240 | **1** |

The 2 -> 1 flip A7.1 attributes to the projector is **the same flip the cell change produces at
fixed projector and fixed U**. A7.1 is a 1x1 statement and is correctly labelled as one — this does
not falsify it. What it means is that "the rate-limiting step flips" is not a projector-unique
signature, and the honest report must say so.

Worse: block 1A closed **ADOPT_2X1V**, and `grep -rl "ortho-atomic" runs/a0/cell/` returns nothing.
**There is no ortho calculation anywhere in the production cell.** So *"does your projector flip the
limiting step in the cell you actually adopted?"* is, today, unanswerable.

## F3 — "pre-registered" is currently unbacked for this whole branch of the chain

- `grep "^# AMENDMENT" docs/43` returns 1,2,3,4,5,6,7,8,9,**11**. No A10. No A12. No A12b.
- `P-PROJ-6`, `AMENDMENT 12`, `12b`, `7.2677`, `6.1635` -> **0 hits each** in docs/43.
- `docs/deposits/` holds exactly one file, `2026-08-31-A11.manifest.txt`, scoped *A1-A11*.
- Standing rule, in registered text at `docs/43:1807`: *"every amendment goes to Zenodo before the
  first act it governs."*

**Both jobs submitted 2026-09-03 are governed by amendment text that is in the working tree and in
git, but not in the deposited registration.** The internal ordering is clean and the commits prove
it; what is missing is the deposit. A reviewer following the deposited chain stops at 2026-08-31 and
never reaches either U value. This is the single most urgent item on the board and it costs 0 SU.

## F4 — half the proposed arm was already known, to sub-meV

`docs/figs/a0main_readout.json`, Cr atomic ladder: eta(6.00) = 0.885653, eta(6.50) = 1.004390,
pls = 2 at both ends. Linear interpolation gives **eta_atomic(6.1635) = 0.9245 V**. The interpolant
is validated **out of sample**: the same ladder predicts A7.1's independently measured atomic leg at
U = 7.15 to **0.287 meV** (1.155116 vs 1.155403).

So four of the eight proposed SCFs had a known answer, pinned ~340x tighter than A7.1's own 0.10 V
trigger. And `docs/76:149-153` — the entrant's own governing rule, used one day earlier to withdraw
S8 — reads: *"Registering a prediction tomorrow for an outcome computable today is precisely the
violation the governance rule exists to prevent."* That rule forbids a blind label here.

The **direction** was also forced: moving atomic from 7.15 to 6.1635 drops eta by 0.231 V down a
monotone pls = 2 branch, so delta-eta was guaranteed to widen before anything ran. Only the ortho
magnitude was unmeasured — and even that expires when array 20382165 lands u750, bracketing 7.2677
inside [7.15, 7.50].

## F5 — the arm is Cr-only, and Cr scores nothing

`docs/77:116`, **adopted 2026-09-03**: Cr is *"reported in every table, always labelled
**CALIBRATION (post-hoc)**, and is excluded from every count."* A Cr-only arm cannot enter the
class claim or score a ledger row. Presenting one as evidence would contradict a counting rule
adopted the day before — the kind of flex that costs more than the finding is worth.

## F6 — the two U values are not what we have been calling them

Both hp.x parents run at `U Cr-3d 1.d-8`: these are **one-shot linear-response U evaluated about
the U ~ 0 ground state**, never iterated U_in -> U_out. The prescription docs/79 sets up as the
rebuttal to be tested is the *iterated* loop. So the phrase **"each projector's own self-consistent
U" is an overclaim** and must become **"one-shot bulk linear-response U"** everywhere, including in
docs/79's POST-HOC section.

Compounding it: `docs/43:1327` and `docs/research/2026-08-15-lit-sweep-lens-digest.md:366` both
record that Xu's U = 7.15 was itself produced under a *different* projector — and
`docs/figs/a0cell_readout.json` labels the rung `PROJECTOR-MISMATCHED` in its own metadata. If 7.15
is atomic's, then atomic's "own" ab-initio U is simultaneously 6.1635 and 7.15 — **0.99 eV apart,
which is 90 % of the entire 1.1042 eV split we are calling an effect.**

## What replaces it

**Do not run the square.** It buys the cell already known to 0.29 meV and a cell 0.118 eV from a
measured point, on a metal that scores nothing.

Ranked, and none of this needs new registration to *decide*:

1. **0 SU — close F3.** Append A12/A12b into docs/43 and re-deposit. Until then "pre-registered"
   describes a record ending 2026-08-31.
2. **0 SU — publish F1.** The ZPE decomposition, in our own table, with the sensitivity band.
3. **~30-55 SU — four ortho SCFs in 2x1v at U = 7.15.** This is the highest-value compute on the
   board. It pairs against a fully banked atomic leg, and it is the only calculation in this
   neighbourhood that can **falsify the headline** by asking whether the projector still flips the
   limiting step in the cell the campaign adopted. The own-U arm measured a 1x1 result more
   precisely; this asks whether the 1x1 result is real.
4. **<1 SU — P-XU-SPAN.** Still the only board item that converts a deposited, blind,
   threshold-carrying prediction into a **scored** one.

If an own-U arm is ever run, the only defensible form is **ortho-only** — never the eight-SCF
version, half of which carries near-zero information — with eta_atomic(6.1635) = 0.9245 V written
into the adoption text **in advance** as DISCLOSED NON-BLIND, and the arm labelled a robustness
defence of A7.1 rather than a class claim or a discovery.
