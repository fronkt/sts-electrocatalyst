# 84 — READOUT: P-PROJ-CELL, Amendment 13. The projector in the cell we actually adopted.

> **COUNTERSIGNED 2026-09-04.** Decks built `5e15c10` → A13 appended to docs/43 `72aeee9` →
> deposited **10.5281/zenodo.22304889** at 12:35:26Z with **zero outputs on disk** → array
> `20388045` submitted 12:37:59Z → scorer `src/dft/pproj_cell_readout.py` committed `e0e4ea8`
> **before any output existed**, self-tested by null pairing → outputs read after that. A13 is
> clean on its own deposit rule: the registration preceded its first governed act.

## Verdict against what was registered

**4/4 converged. Zero `convergence NOT achieved`. Zero branch mismatches.** All four output md5s
byte-identical between Anvil and this machine.

**A13.2's disclosed non-blind check PASSED at +0.0000 meV.** The atomic leg re-derives to
**0.9239810 V, pls 1** — exactly the value written into the registration before the ortho leg
ran. The scorer refuses if it misses; it did not miss.

| leg | pls | η (V) | step 1 | step 2 | step 3 | step 4 |
|---|---|---|---|---|---|---|
| atomic | **1** | 0.9239810 | **2.1539810** | 1.9931610 | 0.4494759 | 0.3233821 |
| ortho | **1** | 1.0964974 | **2.3264974** | 2.1721761 | 0.1275272 | 0.2937993 |

**Δη = +0.1725164 V → FIRES** (trigger 0.10 V, inherited unchanged from A7.1).
**pls 1 → 1 — the legs AGREE.**

## The branch, named in advance

`band = FIRES`, `pls_differs = False` selects the second of A13.4's four pre-written branches,
quoted rather than re-invented:

> *"the **MAGNITUDE** survives the cell change; the **MECHANISM** does not. 'The projector flips
> the rate-limiting step' becomes a **1×1-ONLY sentence** and is scoped that way in every
> statement of A7.1 for the rest of the campaign."*

| cell | η atomic | pls | η ortho | pls | \|Δη\| |
|---|---|---|---|---|---|
| 1×1 (A7.1) | 1.1554 | **2** | 1.6423 | **1** | **0.4869** |
| **2×1v (adopted, this arm)** | 0.9240 | **1** | 1.0965 | **1** | **0.1725** |

Both cells are always printed together from here, per A13.4's anti-selection clause.

## What this costs, stated first

**The pls-flip sentence is now dead outside 1×1.** In the cell this campaign actually adopted,
the projector does not move the rate-limiting step — both legs are limited by step 1. The
mechanism claim that made A7.1 vivid is a property of the 1×1 cell, and every future statement of
it carries that scope. That was the pre-registered consequence of this branch and it is taken
without argument.

**The effect is 2.8× smaller in the production cell** — 0.4869 V → 0.1725 V. Any sentence quoting
0.487 V must say it is a 1×1 number and that the adopted-cell value is 0.17 V.

## What this buys, which is more than it costs

**The projector effect SURVIVES into the adopted cell.** 0.1725 V clears the inherited 0.10 V
trigger by 72 mV. A7.1 is not a 1×1 artifact: the headline reproduces, smaller, in the cell the
campaign runs. Had this landed below 0.03 V the registration required the headline to be re-led;
it did not.

**And the 2×1v number is EXACTLY immune to the constants table.** Both legs share pls 1, so the
ZPE/TS terms cancel identically — and so do *both* gas references, including the E_H2O that
`docs/81` §7.1 showed does **not** cancel when the legs differ. Verified by full recomputation at
all 27 corners of the ±0.05 eV cube:

| | Δη band under ±0.05 eV on each constant |
|---|---|
| A7.1, 1×1 (pls 2→1) | **±0.15 V** — and 133.5 % of the value is the table |
| **A13, 2×1v (pls 1→1)** | **[+0.1725, +0.1725] — zero width** |

**The adopted-cell measurement is more trustworthy than the flagship it tests, despite being
smaller.** It is 100 % electronic, with no constants sensitivity at all.

## The margin question, raised and resolved

The individual pls assignments here are *not* robust: atomic leads its runner-up by 0.1608 eV and
ortho by 0.1543 eV, and each flips at a uniform half-width of **0.054 / 0.052 eV** — about **1×**
the ±0.05 eV constants band, against **3.3×** and **7.6×** for the 1×1 legs. Taken alone that
would make "both legs are pls 1" a fragile conclusion.

**It is not fragile, because the table is common to both legs.** The branch turns on whether the
two legs can be made to *differ*, and they cannot:

| perturbation half-width | pls pairs reachable | corners where the legs differ |
|---|---|---|
| ±0.05 eV | (1,1) | **0 of 27** |
| ±0.10 eV | (1,1), (2,2) | **0 of 27** |
| ±0.15 eV | (1,1), (2,2) | **0 of 27** |
| ±0.30 eV | (1,1), (2,2) | **0 of 27** |

The two legs move **together** — both to pls 1 or both to pls 2 — at every corner out to ±0.30 eV,
six times the band. So the branch conclusion ("the legs agree, therefore the mechanism does not
survive the cell") holds even where the individual assignments do not. The fragility is real and
is recorded; it does not reach the verdict.

## Read alongside Amendment 12

Two independent results this day say the same thing about the criticism `docs/81` levelled at the
flagship — that 133.5 % of A7.1's 0.487 V is a fixed constants table:

1. **Ir (A12, blind):** |Δη| = 0.4596 V at pls 2→2 — the largest blind effect in the six-metal
   arm, the same size as Cr's calibration, **100 % electronic.**
2. **Cr in 2×1v (A13, this arm):** |Δη| = 0.1725 V at pls 1→1, **100 % electronic, with exactly
   zero constants sensitivity.**

**The constants dependence is a property of A7.1's particular pls flip, not of the projector
effect.** That is now shown on a different material in a blind arm, and on the same material in a
different cell. Neither was available this morning.

## Integrity and scope

- Magnetisations match between legs on all four states (24.0/24.0, 22.0/22.0, 23.0/23.0,
  23.0/23.0) — **zero branch mismatches**, reported rather than assumed.
- The four ortho decks differ from their banked atomic partners in **exactly two lines** each
  (prefix, `HUBBARD` card), verified line-by-line at build; rebuild byte-identical.
- **Inherited and disclosed, not introduced:** two of the four source decks carry `nosym`/`noinv`
  and two do not, and the `mir`/`escape` labels are the banked cell arm's own geometry
  provenance. Both are properties of the atomic legs, reproduced faithfully so the difference
  stays paired.
- Both legs are single points on geometries relaxed under the **atomic** projector; whether the
  split survives relaxation is not tested here and must not be implied (A13.5).
- **Cr-only. This arm scores no class row** and adds nothing to Amendment 12's five-metal
  denominator, where Cr is and remains CALIBRATION.

## What may be said

**May:** that the projector effect survives into the adopted 2×1v cell at 0.17 V, 2.8× smaller
than the 1×1 value; that the adopted-cell number is entirely electronic and exactly insensitive
to the ZPE/TS table; and that the rate-limiting-step flip is **a 1×1 result only**.

**May not:** "the projector flips the rate-limiting step" without the 1×1 scope; 0.487 V quoted
without its cell and without the 0.17 V adopted-cell companion; or any claim that this arm
generalises beyond Cr.
