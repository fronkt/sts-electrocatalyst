# 81 — What the flagship 0.487 V is made of: the electronic half and the constants half

**Status: a decomposition of banked numbers. No new calculation, zero SU.** A7.1 / P-PROJ
FIRED on |Δη| > 0.10 V and **its verdict is unchanged by anything below.** What changes is
what may honestly be said about the number when it is quoted.

Reproduce with:

```
PYTHONPATH=src python src/dft/zpe_decomposition.py --json docs/figs/zpe_decomposition.json
```

The script imports its energy extraction, gas references, QC gate and state→path mapping from
`src/dft/pproj_readout.py` — the script that produced the registered readout — so there is no
second extraction path. Closure residual **−4.44 × 10⁻¹⁶ eV**; the script refuses to report
above 10⁻⁹.

---

## 1. Why a CHE overpotential is not a pure DFT number

`src/hea_oer/referencing.py:18` adds a fixed constant per adsorbate:

```python
ZPE_TS_CORRECTION = {"OH": 0.35, "O": 0.05, "OOH": 0.40}   # Man 2011 / Valdés 2008
```

Those propagate into the four ladder steps with **coefficients that are not all ±1**:

| step | definition | ZPE/TS content | value |
|---|---|---|---|
| 1 | ΔG_OH | +z_OH | **+0.35** |
| 2 | ΔG_O − ΔG_OH | z_O − z_OH | **−0.30** |
| 3 | ΔG_OOH − ΔG_O | z_OOH − z_O | **+0.35** |
| 4 | 4.92 − ΔG_OOH | −z_OOH | **−0.40** |

They sum to zero — the ladder totals 4.92 eV whatever the table says. **The constants cannot
move the total. They can only move which step is largest.** And η is defined as
`max(step) − 1.23`, so η carries the constant of the *winning* step and no other.

That is the whole mechanism of what follows: **when the projector flips the potential-limiting
step, it also swaps which constant lands in η.**

---

## 2. The decomposition, exact

Cr, U = 7.15 eV, 1×1 cell, byte-identical geometry, both legs sharing the same
`runs/Cr_slab` gas references (H₂O −599.211013 eV, H₂ −31.745323 eV). **Those references do
not both cancel — see §7, which corrects an earlier sentence here.**

| leg | pls | η (V) | step 1 | step 2 | step 3 | step 4 |
|---|---|---|---|---|---|---|
| atomic | **2** | 1.1554030 | 1.8935356 | **2.3854030** | 0.4635564 | 0.1775050 |
| ortho-atomic | **1** | 1.6422592 | **2.8722592** | 1.7328054 | 0.1453147 | 0.1696207 |

atomic is limited by step 2 → carries c₂ = **−0.30**.
ortho is limited by step 1 → carries c₁ = **+0.35**.

```
Δη = η_ortho − η_atomic                    = +0.4868562 V
  electronic (both constants set to zero)  = −0.1631438 eV   <-- ortho is LOWER
  constants  (c1 − c2)                     = +0.6500000 eV
  sum                                        +0.4868562      (residual −4.4e-16)
```

**The constants table accounts for 133.5 % of Δη, and the raw DFT difference has the opposite
sign.** Setting both tables to zero does not shrink the projector effect toward zero — it
reverses it, to −0.163 eV with ortho the *lower*-overpotential leg.

This is not an error and it is not unusual: it is what CHE does, and every paper in this
literature does it. But a sentence that says "changing one keyword moves the overpotential by
0.487 V" is, arithmetically, a sentence about a step flip interacting with a constants table.
The report says both halves or it says neither.

---

## 3. Sensitivity — and the coefficient that is easy to get wrong

With the pls assignment fixed, Δη is **exactly linear** in the three constants:

```
d(Δη)/dz_OH  = +2      <-- note: 2, not 1
d(Δη)/dz_O   = −1
d(Δη)/dz_OOH =  0      <-- exactly zero; neither leg is limited by step 3 or 4
```

z_OH enters twice — once as c₁ (the ortho leg's constant, +z_OH) and once through c₂
(the atomic leg's, −z_OH) — so it enters Δη with weight 2. Perturbing each constant
independently by **±0.05 eV** therefore gives a band of **±0.15 V**, not ±0.10:

| | Δη (V) | offsets (z_OH, z_O, z_OOH) |
|---|---|---|
| min | +0.3368562 | (−0.05, +0.05, −0.05) |
| **nominal** | **+0.4868562** | (0, 0, 0) |
| max | +0.6368562 | (+0.05, −0.05, +0.05) |

Computed by full recomputation at all 27 corners, not from the linear form, so a pls change
inside the cube would appear as a kink. **The pls assignment is unchanged at every corner**, so
the band is smooth and the linear coefficients are valid across it.

*(This corrects `docs/80` §F1, which estimated the band at ≈ ±0.10 V and the constants share at
134 %. The correct figures are **±0.15 V** and **133.5 %**. The z_OH coefficient of 2 is the
reason.)*

---

## 4. The half that cuts the other way: the mechanism claim is robust

The magnitude is soft. **The pls flip is not.**

| leg | pls | lead over the runner-up step |
|---|---|---|
| atomic | 2 | **0.4919 eV** |
| ortho | 1 | **1.1395 eV** |

Searching the cube at increasing half-width until any corner flips a leg's limiting step:

| leg | smallest uniform perturbation that flips its pls |
|---|---|
| atomic | **≥ 0.164 eV** — 3.3× the ±0.05 band |
| ortho | **≥ 0.380 eV** — 7.6× |

No defensible uncertainty on a ZPE/TS table is 0.164 eV. **So the secondary observable A12 §3
registers — "whether the potential-limiting step differs between legs" — survives the constants
uncertainty by a factor of at least 3.3, while the primary statistic |Δη| does not survive it
nearly as comfortably.** That is the reverse of the intuition that a counted mechanism is softer
than a measured number, and it is worth saying out loud: on this arm, **the qualitative claim is
the sturdier one.**

---

## 5. What is now owed when the 0.487 is quoted

1. The electronic/constants split, with the sign reversal named.
2. The ±0.15 V band, with the reason the coefficient is 2.
3. The pls-flip robustness margin, because it is the honest counterweight.
4. That the constants were **not recomputed per projector**, even though the projector shifts
   absolute magnetisation on these states by 0.55–1.57 μB. A per-projector ZPE recomputation
   would be a phonon calculation on four states × two projectors and is **not** proposed here;
   it is disclosed as a stated approximation, which is what every screening study in this
   literature also does without saying so.

Nothing here is a threshold, a verdict, or a new prediction. It is a disclosure, and it is
registered as one in Amendment 12's append to `docs/43`.

## 7. CORRECTION OF RECORD, 2026-09-04 — what actually carries weight in Δη

**The version of this file deposited in Zenodo 10.5281/zenodo.22304889 contains a false
sentence, and this section is the correction.** The deposited copy is frozen, as every
deposited file is; the error is named here, and the next deposit carries the corrected text.

### 7.1 The gas reference does NOT cancel

§2 originally said the two gas references "cancel identically in a difference", and
`src/dft/pproj_readout.py`'s docstring said the same. **That is true only when both legs share
a pls.** Here they do not — atomic is 2, ortho is 1 — so Δη is not a difference of like
quantities:

```
Δη = dG1_ortho − dG2_atomic
   = E_OH,ortho − E_slab,ortho − E_O,atomic + E_OH,atomic − E_H2O + 0.65
```

`dG2 = ΔG_O − ΔG_OH` cancels `E_slab` and one `E_H2O` internally, and the remaining H₂
coefficients cancel — but **one E_H2O survives, at weight exactly −1.** Measured, not argued:

| perturbation | shift in Δη |
|---|---|
| +0.1 eV on E_H2O | **−0.1000000000 V** |
| +0.1 eV on E_H2 | 0.0000000000 V |

**Consequence.** Any error in the reused H₂O energy propagates **1:1** into the 0.487 V. The
old sentence was being used to justify reusing a gas reference from a different run directory
without checking its effect on the headline; that justification does not hold, and the reuse
now needs to be defended on its own terms — which it can be, since H₂O runs in a
Martyna–Tuckerman box with `assume_isolated` and no Hubbard card, projector, dipole
correction or cell height touches it, so it is the *same number* for both legs. What is
retracted is the claim that it cancels, not the reuse.

### 7.2 Only four of the eight registered SCFs carry any weight

| SCF | weight in Δη |
|---|---|
| `slab` ortho | **−1** |
| `s0_OH` atomic | **+1** |
| `s0_OH` ortho | **+1** |
| `s0_O` atomic | **−1** |
| `slab` atomic, `s0_O` ortho, `s0_OOH` atomic, `s0_OOH` ortho | **0 — inert** |

A7.1's registered protocol is all four states × two projectors. **Half of that set does not
touch the headline**: both \*OOH runs, the atomic slab, and the ortho \*O — the last being the
one banked separately in `runs/s0/e_proj`. The other four SCFs remain load-bearing for the
*ladders*, the pls assignments and the falsification floor, so none is wasted; but a sentence
that says "eight SCFs give 0.487 V" should say **which four** it is actually a function of.

### 7.3 The slab asymmetry has no counterpart to cancel against

The two bare-slab decks set `nosym = .true.` and `noinv = .true.` and run **36 k-points**; all
six adsorbate decks set neither and run **15** irreducible points of the same `9 4 1` grid
(everything else — 80/640 Ry, nspin 2, MV smearing 0.01, `conv_thr` 1e-6, U = 7.1500, cell —
is identical across all eight).

Reducing the same grid by symmetry is standard and is not by itself an error. What §7.2 makes
newly relevant is that **`E_slab,ortho` enters Δη at weight −1 while `E_slab,atomic` is
inert.** So a slab-protocol systematic does *not* cancel between the legs the way it would in
a symmetric comparison — it lands on the ortho leg alone, at full weight. This is a stated
sensitivity, not a measured error: no size is claimed for it here, and none is measurable
without a symmetry-on slab pair that does not exist.

### 7.4 The +0.40 eV \*OOH constant is not backed by anything on disk

`referencing.py` attributes all three constants to Man 2011 / Valdés 2008. Neither table is
verifiable in this repository: `docs/research/papers/man2011.pdf` contains no "0.35", no
"0.40" and no ZPE string at all (its SI is not in the repo), and there is no Valdés 2008 PDF.
The one primary table on disk — Divanis Table SI-1 — gives **0.35 and 0.05 attributed to
Rossmeisl/Nørskov, and has no \*OOH row at all**, which `docs/43` already records at :1898.

**Mitigating for this result specifically:** `∂Δη/∂z_OOH = 0` exactly, so the unbacked
constant does not touch the 0.487 V. **It touches every other η this project reports**, and
that is where it has to be chased.

## 8. Artifacts

- `src/dft/zpe_decomposition.py` — the derivation and the weight measurements, from raw
  `.out` files.
- `docs/figs/zpe_decomposition.json` — every number above, machine-readable, including
  `gas_weights` and `scf_weights`.

---

## Dated addendum — 2026-09-05 (session 3): the tool named in §8 changed after this file was deposited; the banked JSON did not

Nothing above this line is edited. Commit `4a5efad` (2026-09-05 15:31) replaced the 27-corner envelope in
`src/dft/zpe_decomposition.py` `main()` with the continuous linear-programming envelope of
`src/dft/che_box_robustness.py`, added a guard on `--delta`, and re-worded the summary block. The method
this file describes at :98-100 and :117 ("full recomputation at all 27 corners"; the uniform-half-width
scan), and that docs/43:3769 and :3771 describe, is therefore the method of the tool at `99c7431`, the
commit that banked `docs/figs/zpe_decomposition.json`. That file is untouched.

Re-running the command at :10 with the tool at HEAD reproduces every number above — `d_eta_V`,
`electronic_eV`, `constants_eV`, the closure residual, both gas weights, all eight SCF weights, the
+2/−1/0 coefficients, the ±0.15 V band and the 0.164 / 0.380 eV margins are identical; the envelope's
min and max differ by 4 × 10⁻¹⁶ V — and differs in exactly three places: two new keys,
`sensitivity.offset_units` and `sensitivity.continuous_box`, and the maximum's witness offset on z_OOH,
reported at −1 instead of +1 with the same value, which is a flat direction since ∂Δη/∂z_OOH = 0
(:95-96 table row "max"). For this 1×1 pair the 27-corner inference at :98-100 remains valid: pair (2,1)
wins at all eight vertices of the ±0.05 eV cube, so it wins throughout it (the vertex rule,
docs/84:165-169). The 2×1v grid flaw docs/84:162-219 corrects does not reach this file. Both facts are
pinned in `tests/test_pproj6_shared_box.py`, which runs the HEAD tool against the banked JSON.

The banked JSON stays pinned to the `99c7431` tool by this line; no re-banking is done here.
Re-banking from the HEAD tool is the entrant's election and would carry a dated line of its own.
The next Zenodo version carries this addendum.

> `[ZPE TOOL-CHANGE ADDENDUM — COUNTERSIGNATURE SLOT, BLANK]` — blank until the entrant reviews this
> addendum and elects re-bank or pin by a dated line.
