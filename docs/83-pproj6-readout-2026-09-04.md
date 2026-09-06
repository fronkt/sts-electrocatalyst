# 83 — READOUT: P-PROJ-6, Amendment 12. The projector across the six-metal roster.

> **COUNTERSIGNED 2026-09-04.** Thresholds adopted `8aba0ae` (2026-09-04T00:59:56Z) → array
> `20382165` submitted 01:02Z → deposited **10.5281/zenodo.22304889** 12:35:26Z, with the array
> still 24/24 PENDING and **zero outputs on disk** → outputs read after that. The scorer
> `src/dft/pproj6_readout.py` was committed at `e0e4ea8` **before any output was pulled**, and
> self-tested by null pairing. Every ordering that matters here is in git with timestamps.

## Verdict against what was registered

**24 of 24 SCFs converged. Zero `convergence NOT achieved`, zero errors, zero branch
mismatches.** All 24 output md5s verified byte-identical between Anvil and this machine
(fileset rollup `a393be276a8c6123a44c2e1ab9a26e67`).

| metal | role | η atomic | η ortho | pls | Δη (V) | band | PP family | nspin |
|---|---|---|---|---|---|---|---|---|
| **Cr** | **CALIBRATION (post-hoc)** | 1.2349 | 1.6811 | 2→1 | **+0.4462** | FIRES | ultrasoft | 2 |
| Mn | blind | 1.2930 | 1.3721 | 1→1 | +0.0791 | **INTERMEDIATE** | ultrasoft | 2 |
| Fe | blind | 1.2601 | 1.3895 | 2→1 | **+0.1293** | **FIRES** | PAW | 2 |
| Ti | blind | 1.9368 | 1.9377 | 2→2 | +0.0010 | **NULL** | ultrasoft | 1 |
| Ru | blind | 0.3577 | 0.7885 | 3→2 | **+0.4308** | **FIRES** | norm-conserving | 1 |
| Ir | blind | 0.6981 | 1.1577 | 2→2 | **+0.4596** | **FIRES** | ultrasoft | 1 |

**Cr is reported and is excluded from every count (A12.R2).** It is here because the
anti-selection clause requires it to travel with the others, labelled.

## CLASS VERDICT: MIDDLE BAND — metal-dependent. 3 of 5.

**FIRES 3/5** {Fe, Ru, Ir} · **INTERMEDIATE 1/5** {Mn} · **NULL 1/5** {Ti}

The registered wording for this band, written before the run and quoted rather than
re-invented: *"the split is real on some systems and not others; it is not universal, and the
per-metal table is the result. **No class claim.**"*

That is the finding. **The projector split is not a property of the method across this roster.**
Ti moves by 1.0 meV — the projector is, on Ti, not a live variable at all — while Ir moves by
0.46 V. Any sentence of the form "changing this keyword moves the overpotential" must now carry
"on some materials and not others," and the per-metal table is the result rather than an
illustration of one.

**This is the band A12.R3 defined in advance precisely so it could not be talked around.** A7.3
fell into an undefined band and the campaign paid for it; this one had its sentence pre-written.

## The confound clauses did not fire, and the way they failed to fire is the strongest part

A12.R5 and A12.R6 named four dangerous partitions in advance. The firing set is **{Fe, Ru, Ir}**,
which matches none of them — and it misses them in the most informative possible way:

| firing metal | pseudopotential family | nspin |
|---|---|---|
| Fe | **PAW** | 2 |
| Ru | **norm-conserving** | 1 |
| Ir | **ultrasoft** | 1 |

**The three firing metals are one from each of the three pseudopotential families**, and they
span both spin conventions. The registered clause was written to catch a verdict that lines up
with an unmeasured methodological partition; this verdict is maximally spread across both
partitions instead. The ultrasoft set {Mn, Ti, Ir} contains the NULL metal, the INTERMEDIATE
metal *and* the largest-firing metal — so pseudopotential family manifestly does not organise the
result.

Registered check, for the record: firing set ≠ {Mn, Ti, Ir}, ≠ {Fe, Ru}, ≠ {Mn, Fe},
≠ {Ti, Ru, Ir}. **Not DECLARED CONFOUNDED.**

## Ir answers the criticism A13.6 raised against A7.1

This is the most consequential row in the table and it needs stating plainly.

`docs/81` / A13.6 found that **133.5 % of A7.1's flagship 0.487 V is a fixed ZPE/TS constants
table**, and that the raw DFT difference has the opposite sign — because the projector flips the
limiting step and flipping the limiting step swaps which constant lands in η.

**Ir shows the same effect at the same magnitude with none of that:**

| | Δη | pls | constants contribution |
|---|---|---|---|
| Cr (A7.1, 1×1, calibration) | 0.4869 V | 2→1 | **+0.65 eV — 133.5 %** |
| Cr (here, u750, calibration) | 0.4462 V | 2→1 | +0.65 eV — 145.7 % |
| **Ir (blind)** | **0.4596 V** | **2→2** | **0.00 — the constants cancel exactly** |

**Ir's 0.4596 V is 100 % electronic.** Both legs are limited by step 2, so the ZPE/TS terms
cancel identically, *and* both gas references cancel with them. The largest blind projector
effect in the arm owes **nothing** to the constants table.

So the honest reading of A13.6 changes: the constants dependence is a property of **A7.1's
particular pls flip**, not of the projector effect itself. A reviewer who asks "isn't your
headline just a constants swap?" is answered by Ir, in the blind arm, at the same size.

## The three caveats that must travel with individual rows

**Fe fires on the constants, and its electronic part points the other way.** Δη = +0.1293 V
clears the 0.10 V trigger by 29 meV, and decomposes as **electronic −0.5207 eV + constants
+0.6500 eV = 502.6 % constants**. Fe is a FIRES row whose raw DFT difference is large and
*negative*. It counts — the registration scores |Δη| and Fe's |Δη| is over the line — but no
sentence may quote Fe as evidence of a large electronic projector effect.

**Ru's constants work against it.** electronic **+1.0808 eV** − constants 0.6500 eV = +0.4308 V.
Ru's reported Δη *understates* an electronic difference of over 1 eV.

**Mn is INTERMEDIATE and is not rounded.** +0.0791 V sits between the 0.03 and 0.10 V bounds. It
is reported as INTERMEDIATE, it is not a FIRES, and it is not a NULL. Had it been rounded up the
verdict would have been 4/5 CONFIRMED — which is exactly why the band was defined in advance.

## R_M — the diagnostic, with an artifact named

Reported per A12.R1 with **no verdict attached**.

| metal | RMS (eV) | U_opt | implied-shift span |
|---|---|---|---|
| Cr | 0.5059 | 9.000 **(grid edge)** | 1.17 eV |
| Mn | 0.0324 | 8.314 | 0.62 eV |
| Fe | 0.0422 | 9.000 **(edge)** | 0.42 eV |
| Ti | 0.0469 | 5.515 | **5.80 eV** |
| Ru | 0.2446 | 9.000 **(edge)** | 1.08 eV |
| Ir | 0.6883 | 9.000 **(edge)** | 0.00 eV — **artifact, see below** |

**Four of six optima are pinned at the grid edge**, which is the same signature the Cr
calibration showed and is the substance of "the projector is not a reparameterisation of U": no
single U shift reproduces the ortho leg.

**Ti is the cleanest case.** Its three observables demand U = 0.933, 5.803 and 0.000 eV — a
**5.80 eV spread from one calculation.** One number cannot be three numbers.

**Ir's 0.00 eV span is an edge-clamping artifact and must not be read as consistency.** All three
of its per-observable fits are clamped at the U = 9.0 boundary with residuals 0.5341, 0.9377 and
0.5069 eV. They agree only because they are all pressed against the same wall. Recorded here so
the table is not misread — this is a limitation of a bounded fit, not a finding.

## Integrity checks

- **Re-derivation drift vs the banked registered readout: +0.0000 meV on all six metals.** Both
  legs go through one extraction path, and the atomic leg reproduces
  `docs/figs/a0main_readout.json` exactly. The scorer refuses above 5 meV.
- **Zero branch mismatches.** Every nspin = 2 pair (Cr, Mn, Fe) matches in total magnetisation
  between legs; Ti/Ru/Ir are nspin = 1 and print none.
- **The scorer refuses to score a partial arm at all** — A12.R4's anti-selection clause is
  enforced structurally, not by discipline.
- Atomic pls at u750 spans **1, 2 and 3** (Mn 1, Ru 3, rest 2), exactly as A12 claimed when it
  justified this rung. Verified, not assumed.

## Disclosed, not scored

**The k-mesh is not uniform across the roster** — Cr and Mn slabs are `9 4 1`, Fe/Ti/Ru/Ir are
`8 4 1`. Harmless *within* a pair, since Δη is a paired difference at byte-identical settings,
but this table crosses two meshes and says so on its face (A12.R6).

**Both legs are single points on geometries relaxed under the atomic projector**, at one U
(7.50 eV), and this arm does not say which projector is right (A12.R7).

## What may be said, and what may not

**May:** the projector split is **metal-dependent** — real and large on Fe, Ru and Ir,
intermediate on Mn, absent on Ti; that it crosses every pseudopotential family and both spin
conventions, so no named methodological partition explains it; and that on Ir it reaches 0.46 V
with **zero** contribution from the ZPE/TS table.

**May not:** any class claim about DFT+U; any statement that the projector "moves the
overpotential" without "on some materials"; Fe quoted as a large electronic effect; Ir's R_M span
quoted as consistency; or any subset of the five quoted without the other four (A12.R4).

---

## Dated addendum — 2026-09-05: the cell of the P-PROJ-6 decks

Nothing above this line is edited. This file names a cell once, in the A7.1 comparison row at :77
("Cr (A7.1, 1×1, calibration)"); the six-metal table at :15-22 and the class verdict at :27-29
carry none, and neither does Amendment 12: docs/43:3344-3347 governs the arm and names the atomic
partners by path (`runs/a0/main/<M>/<state>__u750.in`, :3347) without a cell, and the only lines
of A12 (docs/43:3331-3600) matching `1×1|1x1|2×1|2x1|cell` are :3504 (a 2×2 contingency table),
:3568 ("non-cancellation") and :3587 (the filename `a0cell_readout.json`).

**Every one of the twenty-four P-PROJ-6 decks is the 1×1 rutile(110) cell, and so is every one
of its twenty-four atomic partners.** Read from the decks `runs/a0/pproj6/<M>/<state>__u750_ortho.in`:
`nat = 18` on all six slab decks and 19 / 20 / 21 on \*O / \*OH / \*OOH (line 12 of each), and a
first cell vector of one lattice constant along the metal's c axis — Cr 2.91600000, Mn 2.87600000,
Fe 3.00000000, Ti 2.95870000, Ru 3.10700000, Ir 3.15400000 Å — e.g.
`runs/a0/pproj6/Cr/slab__u750_ortho.in:37-40` (`CELL_PARAMETERS angstrom`, 2.91600000 × 6.25223816 ×
25.00895264 Å), `runs/a0/pproj6/Ir/slab__u750_ortho.in:34-37` (3.15400000 × 6.36113260 ×
25.44453041 Å), `runs/a0/pproj6/Fe/s0_OOH__u750_ortho.in:39-42` (3.00000000 × 6.36396103 ×
25.45584412 Å). Each ortho deck differs from its atomic partner in exactly two lines, the prefix
and the `HUBBARD` card (`runs/a0/main/Cr/slab__u750.in` vs `runs/a0/pproj6/Cr/slab__u750_ortho.in`,
likewise Fe/s0_OOH and Ir/slab), so the partners carry the identical `nat` and cell lines
(`runs/a0/main/Cr/slab__u750.in:12,37-40`, `Ir/slab__u750.in:12,34-37`, `Fe/s0_OOH__u750.in:12,39-42`).
For contrast, the adopted 2×1v cell of the A13 arm is `nat = 36` with a 5.83200000 Å first vector
(`runs/a0/pproj_cell/ref__2x1v__u715_ortho.in:13,38-41`).

The 1×1 scope is on the record for A7.1 at docs/43:3618-3619 ("a **1×1** statement") and for the
A0 grid these u750 decks belong to at docs/43:1333 ("1×1 (matching A0)"). Consequence: the 3-of-5
verdict at :27 is a 1×1, U = 7.50 eV result, and the cell test A13 ran on Cr (docs/84:35-38, 1×1
against 2×1v) has no counterpart in this arm for any other metal.

---

## Dated addendum — 2026-09-05 (session 3): the six-metal count under one shared ZPE/TS correction

Nothing above this line is edited. The dated correction at docs/84:162-219 established that a paired
CHE difference is piecewise affine in the ZPE/TS constants, so a grid of sample points does not certify
a box, while a step that dominates at all eight vertices dominates throughout (docs/84:165-169). This
file's rows were never tested that way: Amendment 12 registered no constants box for the count (the
only sensitivity lines in docs/43:3331-3600 are the q-mesh bar at :3375 and :3531), and docs/43:4046-4050
states Ir's "100 % electronic" at the nominal constants. Here the same ±0.05 eV shared box is applied to
every pair banked in `docs/figs/pproj6_readout.json`, with **one** correction (δ_OH, δ_O, δ_OOH) serving
both legs of all six metals — the physical situation, since `src/dft/pproj6_readout.py:175, :253` reads
one table. Script `src/dft/pproj6_shared_box.py`; output `docs/figs/pproj6_shared_box.json`; tests
`tests/test_pproj6_shared_box.py`. The continuous envelope is the linear-programming helper of
`src/dft/che_box_robustness.py`; a 101³ grid agrees with it to 10⁻¹⁰ V on every row.

| metal | banked Δη (band) | pls pairs reachable | \|Δη\| over the box (V) | bands reachable | nominal pair wins at all 8 vertices |
|---|---|---|---|---|---|
| Cr (calibration) | +0.4462 (FIRES) | (2,1) | [0.2962, 0.5962] | FIRES | yes |
| Mn | +0.0791 (INTERMEDIATE) | (1,1), (1,2), (2,2) | [0.0791, 0.1276] | INTERMEDIATE, FIRES | no |
| Fe | +0.1293 (FIRES) | (1,1), (2,1), (2,2) | [0.0269, 0.1977] | NULL, INTERMEDIATE, FIRES | no |
| Ti | +0.0010 (NULL) | (2,2) | [0.0010, 0.0010] | NULL | yes |
| Ru | +0.4308 (FIRES) | (2,2), (3,2) | [0.2308, 0.5844] | FIRES | no |
| Ir | +0.4596 (FIRES) | (2,2) | [0.4596, 0.4596] | FIRES | yes |

**Three statements follow, and only these.**

1. **Ir and Ti are fixed-pair rows: their Δη is the same number at every point of the box.** Ir's
   "100 % electronic" (:79-83; docs/43:4046-4050) therefore holds as a statement about the whole ±0.05 eV
   shared box, not only at the nominal constants — the fixed-active-step condition docs/84:197-198 asks
   for is met. Ti's NULL is likewise box-wide.

2. **Mn's and Fe's individual bands are not constants-robust.** Mn crosses the 0.10 V trigger inside the
   box; Fe can leave FIRES and fall below 0.03 V. This is the quantitative form of the caveat already at
   :91-95 and docs/43:4051-4053 (502.6 % constants): a row whose Δη is mostly constants table moves with
   that table. Ru stays FIRES throughout, though its pair changes.

3. **The class verdict is constants-robust even though those two rows are not.** Because one table serves
   every metal, the count must be read at one shared correction, not assembled from per-metal extremes.
   Over the whole box the FIRES count is **2 or 3 of 5 — never 4** — and A12.R3 maps both to MIDDLE BAND.
   The same combination of constants, 2δ_OH − δ_O, governs the step-1/step-2 switch in Mn and in Fe, in
   opposite senses for the count: Mn enters FIRES only where Fe has already left it. Witness: at
   (δ_OH, δ_O, δ_OOH) = (−0.015, 0, 0) eV the count reads 2 (Fe 0.0993 V, INTERMEDIATE); at the nominal, 3.
   The NULL count reads 1 or 2 (Fe can join Ti) and enters no verdict.

**What this changes in how rows are quoted.** "FIRES 3 of 5" (:27; docs/43:4030) is the nominal count;
under the same ±0.05 eV shared box it reads "2 or 3 of 5, MIDDLE BAND throughout". docs/87:155 already
forbids quoting the count without Fe's caveat; this addendum supplies the number for that caveat. Nothing
here re-scores Amendment 12: the registered count, bands and verdict were formed at the nominal constants
as A12 requires, and the verdict is the same at every point of the box. The box is a sensitivity to a
shared correction, not a probability and not a calibrated uncertainty of the constants.

> `[SIX-METAL SHARED-BOX ADDENDUM — COUNTERSIGNATURE SLOT, BLANK]` — blank until the entrant reviews this
> addendum and adopts or strikes it by a dated line; until then it is a sensitivity calculation on the
> record, not a statement of Amendment 12.
