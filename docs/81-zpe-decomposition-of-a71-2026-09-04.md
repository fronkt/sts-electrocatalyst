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
`runs/Cr_slab` gas references (H₂O −599.211013 eV, H₂ −31.745323 eV), which cancel identically
in a difference.

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

## 6. Artifacts

- `src/dft/zpe_decomposition.py` — the derivation, from raw `.out` files.
- `docs/figs/zpe_decomposition.json` — every number above, machine-readable.
