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

---

## Dated addendum — 2026-09-05: the Hubbard U of the two numbers this file compares

Nothing above this line is edited. No line of this file states a Hubbard U; the table at :35-38
and the comparison at :95-107 put a 2×1v number, a 1×1 number and the six-metal result side by
side without one. The U of each is read here from docs/43 and from the decks.

**Δη = +0.1725 V (:23, :38) is a U = 7.15 eV measurement, and so is the 1×1 row it is compared
with.** A13 governs this arm at "U = 7.15 eV, in the **adopted 2×1v cell**" (docs/43:3613-3614)
and A13.5 item 3 states "One U (7.15) and one material (Cr)" (docs/43:3730). The four ortho decks
carry `HUBBARD (ortho-atomic)` / `U Cr-3d 7.1500` at `runs/a0/pproj_cell/ref__2x1v__u715_ortho.in:81-82`,
`s0_O__2x1v_mir__u715_ortho.in:80-81`, `s0_OH__2x1v_mir__u715_ortho.in:83-84` and
`s0_OOH__2x1v_escape__u715_ortho.in:85-86`; their banked atomic partners carry `HUBBARD (atomic)` /
`U Cr-3d 7.1500` at `runs/a0/cell/ref__2x1v__u715.in:81-82`, `s0_O__2x1v_mir__u715.in:80-81`,
`s0_OH__2x1v_mir__u715.in:83-84` and `s0_OOH__2x1v_escape__u715.in:85-86`. The 1×1 row (0.4869 V,
A7.1) was registered "at U = 7.15 eV, 1×1 (matching A0)" (docs/43:1333).

**The six-metal P-PROJ-6 result read alongside at :95-107 (FIRES 3 of 5, docs/83:27-29) is a
U = 7.50 eV measurement.** A12 governs that arm "at U = 7.50 eV" (docs/43:3345) and docs/83:147-148
says so. All twenty-four ortho decks `runs/a0/pproj6/<M>/<state>__u750_ortho.in` carry
`U <M>-<n>d 7.5000` — e.g. `Cr/slab__u750_ortho.in:62-63`, `Fe/s0_OOH__u750_ortho.in:67-68`,
`Ir/slab__u750_ortho.in:59-60` — and all twenty-four atomic partners
`runs/a0/main/<M>/<state>__u750.in` carry `HUBBARD (atomic)` / `7.5000` (`Cr/slab__u750.in:62-63`,
`Fe/s0_OOH__u750.in:67-68`, `Ir/slab__u750.in:59-60`). The Cr calibration row of that arm (0.4462 V,
docs/83:17 and :78) is therefore Cr at a third (cell, U) pair — 1×1, 7.50 eV — distinct from both
rows of the table at :35-38, and none of the three Cr numbers is quotable without its cell and its U.

## Dated correction — 2026-09-05: continuous correction boxes can contain missed step disagreements

This corrects the continuous-domain inference in "The margin question, raised and resolved."
The original text and banked A13 readout remain above and unchanged. A 3x3x3 grid has 27
sample points, not 27 cube vertices; the three-dimensional box has eight vertices.
Paired agreement on these sample sets does not establish continuous agreement when the
step identities change across samples. A fixed step dominating at every vertex is different:
its dominance throughout the box can be verified using affine inequalities.

From the banked Cr 2x1v U=7.15 eV adsorption free energies, the shared OH/O/OOH correction
(-0.0525, +0.0525, 0.0000) eV yields:

| leg | potential-limiting step | eta (V) | margin over runner-up (eV) |
|---|---|---|---|
| atomic | 1 | 0.871481047682 | 0.003320093150 |
| ortho | 2 | 1.047176093046 | 0.003178666165 |

Thus the legs CAN disagree within the +/-0.10, +/-0.15, and +/-0.30 eV boxes. Along
delta=(-t,+t,0), the disagreement lies between t=0.051440444612 and 0.053606697717 eV,
which all three of those 27-point grids miss. The assertion that the legs must move
together throughout these boxes is withdrawn.

Continuous paired-step-region optimization gives:

| shared half-width (eV) | strictly reachable step pairs (atomic, ortho) | delta-eta interval (V) |
|---|---|---|
| 0.05 | (1,1) | [0.1725163792, 0.1725163792] |
| 0.10 | (1,1), (1,2), (2,2) | [0.1725163792, 0.1790151385] |
| 0.15 | (1,1), (1,2), (2,2) | [0.1725163792, 0.1790151385] |
| 0.30 | (1,1), (1,2), (2,2) | [0.1725163792, 0.1790151385] |

**The nominal A13 result is unchanged.** At the nominal constants, both legs still select
step 1 and the paired difference remains +0.1725164 V, beside the 1x1 companion +0.4868562 V.
The entire +/-0.05 eV shared-correction box also retains the constant difference. The magnitude
remains above 0.10 V throughout all four tested continuous boxes; the broader guarantee of
paired step agreement does not. "Exactly insensitive to the constants table" must therefore
carry its shared-correction domain or its fixed-active-step condition.

The new supporting helper enumerates all 16 closed active-step regions and optimizes the
paired difference over their linear constraints. A separate maximum-margin problem distinguishes
unique step assignments from ties. This is an exhaustive region formulation evaluated with
floating-point linear programming and explicit tolerances, not exact symbolic arithmetic.
The independent analytic inequality and direct recomputation above agree with its result.

Reproduce with:

    python src/dft/che_robustness_case_study.py

- Implementation: src/dft/che_box_robustness.py
- Source: docs/figs/pproj_cell_readout.json (SHA-256 recorded in the new audit)
- Audit and figure: results/che_box_case_study_2026-09-05/
- Tests: tests/test_che_box_robustness.py

This is an exploratory sensitivity correction, not a new registered experiment or a changed
threshold. No claim about independent surface-specific solvation errors, U uncertainty,
electronic basins, or real catalyst performance follows from this shared-constants box.
Here and in future explanations use **potential-limiting step** for the CHE result.
The historical phrase "rate-limiting step" does not establish kinetic rate determination.
