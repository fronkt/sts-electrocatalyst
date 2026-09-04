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
