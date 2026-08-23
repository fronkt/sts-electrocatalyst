# 49 — Block 1C on Cr: the 2×1v *OOH Hessian at two displacements

**Date:** 2026-08-23
**Jobs:** Anvil 20085020 (δ = 0.01 Å, 19 decks), 20089685 (δ = 0.02 Å, 18 of 19), 20090507
(the 19th δ = 0.02 deck, re-run after a transient node death)
**Status of this document:** measurement record. The verdict belongs to the analyzer under
docs/43 §3 + §3-A and is quoted; the one decision the record surfaces (§5) is the entrant's.
Nothing in this file changes a gate, a threshold, or a line of `hessian_analyze.py`.

---

## 1. What ran

| set | job | decks | result | SU | wall/deck |
|---|---|---|---|---|---|
| δ = 0.01 Å | 20085020 | 19 | 19/19 COMPLETED, 0 SCF_FAIL | 404 | ~1 h |
| δ = 0.02 Å | 20089685 | 19 | 18/19 COMPLETED; task 5 (`a37ym`, a −y deck) died in SCF iteration 1 on node a196 — 41 min, exit 1, no pw.x error block, 7.5 GB RSS where finished tasks reach 24 GB, 41% CPU efficiency; nothing deck-specific (its +y mirror finished cleanly) | 368 | ~1 h |
| δ = 0.02 Å retry | 20090507 | 1 (`a37ym`) | COMPLETED on a052, 37 iterations, accuracy 8.9e-11, M = 23.00; E = −3188.70493964 against its +y mirror's −3188.70493963 | 16 | 49 min |

Both sets: 20 ranks / `-nk 4` (the registered shape gate (d) timed), `conv_thr 1.0d-10`
**reached on every deck** (estimated scf accuracy 2.4e-11 … 9.9e-11), `No symmetry found`
on every deck, 16 k-points on every deck, **every deck at total magnetisation 23.00** — one
basin across all 37 completed SCFs. The same-machine multistability docs/46 measured on the
Cr_lit3 family did not appear here.

Gate (d) had timed one of these at 4h05m on Vast. Anvil delivered ~1 h at the same shape —
~4×, well past the 1.52× docs/48 measured on the relax deck. Recorded, not explained.

## 2. Gates — both sets

| gate | δ = 0.01 | δ = 0.02 (all 19) |
|---|---|---|
| Q0 energy: reference SCF vs source relaxation | −0.000 meV | −0.000 meV |
| Q0 magnetisation | 23.000 = source | 23.000 = source |
| Q3 magnetic guard (0.1 µB) | 0 of 18 excluded | 0 of 18 excluded |
| Q4a asymmetry-based σ_F (gate 5e-5, design 1e-5 Ry/bohr) | **2.99e-5 PASS** | **1.20e-4 FAIL** |
| Q4b row asymmetry vs absolute floor 3√2·σ_design/δ | pass | **a38y row 1.845e-1 > floor 5.454e-2 FAIL** |
| Q6 mirror identity (yp vs ym, atom by atom) | 3/3 pairs PASS | 3/3 pairs PASS |
| Verdict | **UNDERPOWERED** | **VOID** (2 failures: Q4a, Q4b — nothing else) |

With the 19th deck in, the δ = 0.02 set is gate-clean everywhere except the two gates that
read the asymmetry — which §4 shows is the forward-difference anharmonic term, not noise.
An 18-deck preview scored before the retry (`hessian_analysis_PREVIEW-18-of-19_…`) had
three failures; the third was the missing deck itself and it cleared as expected.

Q6 at the energy level, for the record — yp and ym energies are identical to the last
printed digit at both δ:

| pair | δ = 0.01 | δ = 0.02 |
|---|---|---|
| a37 y | −3188.70496258 / −3188.70496258 | −3188.70493963 / −3188.70493964 |
| a38 y | −3188.70496514 / −3188.70496514 | −3188.70494983 / −3188.70494983 |
| a39 y | −3188.70497063 / −3188.70497063 | −3188.70497181 / −3188.70497181 |

## 3. The spectrum — the same at both displacements

| # | δ = 0.01 ν (cm⁻¹) | δ = 0.02 ν (cm⁻¹) | y-character | atom weights (O37, O38, H39) |
|---|---|---|---|---|
| **0** | **i244.7** | **i242.8** | **1.000** | **0.11 0.11 0.78** |
| 1 | 99.8 | 100.4 | 0.999 | 0.41 0.59 0.00 |
| 2 | 115.0 | 114.3 | 0.001 | 0.21 0.74 0.05 |
| 3 | 238.4 | 238.2 | 0.000 | 0.36 0.58 0.06 |
| 4 | 281.0 | 282.2 | 1.000 | 0.48 0.31 0.22 |
| 5 | 377.6 | 376.9 | 0.000 | 0.87 0.06 0.07 |
| 6 | 1018.2 | 1018.4 | 0.000 | 0.49 0.50 0.00 |
| 7 | 1371.4 | 1369.3 | 0.000 | 0.06 0.06 0.88 |
| 8 | 3415.9 | 3417.1 | 0.000 | 0.00 0.06 0.94 |

Mode #0 is an out-of-plane, hydrogen-carried imaginary mode — the object of block 1C's
claim — and it reproduces to **0.8 %** between two independent sets of 18 displaced SCFs at
two different step sizes. Amendment 2's own test: *"agreement between them is itself
evidence that the harmonic regime holds."* The eight real modes agree to ≤ 0.6 %.

The energy curvatures tell the same story independently of the force Hessian. With E(+dy)
− E(ref) on the three y-displaced decks:

| atom | δ = 0.01 | δ = 0.02 | ratio |
|---|---|---|---|
| O37 | +7.64e-6 Ry | +3.06e-5 Ry | 4.00 |
| O38 | +5.08e-6 Ry | +2.04e-5 Ry | 4.01 |
| **H39** | **−4.1e-7 Ry** | **−1.59e-6 Ry** | **3.9** |

Quadratic in δ, as a harmonic curvature must be; and the hydrogen's is **negative** — the
mirror-plane geometry is a maximum, not a minimum, along the H's out-of-plane coordinate.

## 4. Why the analyzer nonetheless says UNDERPOWERED / VOID

The floor rule (docs/43 §3-A.3, verbatim): *"Effective floor = max(50 cm⁻¹, 3σ), with σ
propagated from the measured force noise."* The analyzer implements "measured force noise"
as σ_F derived from the Hessian's asymmetry, H − H^T (am.4 §6 acknowledges this: a
diagonal error "contributes zero to H − H^T and zero to σ_F"). On this system:

- The largest asymmetry element **equals** the largest mirror-decoupling element
  (1.548e-1 at δ = 0.01; 3.098e-1 at δ = 0.02 — both lines in the analyzer output print
  the same number). It lives entirely in the (y, xz) block of the adsorbate Hessian.
- Mirror symmetry fixes that block at **exactly zero**. The column — in-plane displacement
  → F_y on an on-plane atom — is measured at ≤ 1e-8 Ry/bohr (§4a below). The row — y
  displacement → in-plane force, built as a **forward** difference — carries an O(δ)
  anharmonic term, because the in-plane forces are even in dy.
- It **doubled exactly** when δ doubled (×2.001). Noise does not scale with δ.

So the σ_F the floor is propagated from is not force noise here; it is the forward
difference's anharmonic truncation error in a block that symmetry zeroes. Two consequences:

1. The floor on mode #0 rises with δ (i264.6 → i373.6) while the mode itself does not move.
   Amendment 2's escalation — larger δ — inflates the very estimator that sets the floor.
2. Q4a (σ_F > 5× design) and Q4b (absolute row floor ∝ 1/δ against an anharmonic asymmetry
   ∝ δ) **fire at δ = 0.02 by construction** once they were anywhere near threshold at
   δ = 0.01. The Q4b failure will persist when the 19th deck lands: −y decks never enter H.
   Note also that the analyzer labels Q4b "CODE-LEVEL gate, reported not registered
   (N32/N33)" and yet counts it toward VOID.

### 4a. What the force noise actually is

`src/dft/hessian_mirror_noise.py` (diagnostic, changes nothing) measures σ_F from
identities the SCF does not enforce, so anharmonicity cannot enter:

| estimator | δ = 0.01 | δ = 0.02 |
|---|---|---|
| F_y on on-plane atoms, 12 in-plane decks (must be 0) — rms / max | 4.8e-9 / 1.0e-8 | 4.8e-9 / 1.0e-8 |
| F_y(i) + F_y(σ i) over off-plane pairs — rms / max | 1.6e-8 / 4.0e-8 | 1.4e-8 / 3.0e-8 |
| yp/ym mirror residual, two independent SCFs → σ_F | **1.75e-7** (3 pairs) | **2.08e-7** (3 pairs) |

QE prints forces to 1e-8 Ry/bohr; the first two rows sit at that digit. Against the design
σ_F = 1e-5, the measured SCF force noise is **~50× smaller**; against the asymmetry-based
values the analyzer used, 150–600× smaller. conv_thr 1e-10 did exactly what it was
specified to do.

Arithmetic on the registered formula, **not a verdict**: floor_ν ∝ √σ_F at fixed δ, so
with σ_F ≈ 1.9e-7 the 3σ floor on mode #0 is ≈ i21 (δ = 0.01) and ≈ i15 (δ = 0.02) — below
the declared i50 in both cases, leaving max(50, 3σ) = i50, against a mode at i243–i245.

### 4b. Addendum, same day — the asymmetry estimator, block by block

`src/dft/hessian_asym_blocks.py` (diagnostic, changes nothing) splits the analyzer's own
|H − Hᵀ| sample by block and asks the scaling question directly. A noise-driven asymmetry
returns a δ-invariant σ_F under the analyzer's convention (σ_F = rms·δ); truncation does
not — a forward difference's asymmetry grows as δ (σ_F ×4 when δ doubles), a central
difference's as δ² (σ_F ×8).

| pairs | δ = 0.01 σ_F | δ = 0.02 σ_F | ratio | noise would give |
|---|---|---|---|---|
| all 36 (the analyzer's sample) | 2.99e-5 | 1.20e-4 | **×4.01** | ×1 |
| (y, xz) cross, 18 | 4.22e-5 | 1.69e-4 | **×4.00** | ×1 |
| non-cross, 18 | 1.74e-6 | 1.37e-5 | **×7.85** | ×1 |
| y–y, 3 | 1.07e-7 | 8.34e-7 | ×7.77 | ×1 |
| xz–xz, 15 | 1.91e-6 | 1.50e-5 | ×7.85 | ×1 |
| mirror identities (§4a), for comparison | 1.75e-7 | 2.08e-7 | ×1.19 | ×1 |

Every block of the asymmetry sample scales as truncation error — the cross block exactly
as a forward difference, the rest exactly as central differences — and none as noise. At a
true force noise of ~2e-7 Ry/bohr there is no usable δ at which |H − Hᵀ| is noise-limited:
the estimator is an anharmonicity meter on this system, at every block. Dropping the
cross block (the "non-cross only" arithmetic, last line of the script) does not rescue it:
the mode-#0 floor would read i64 at δ = 0.01 and i126 at δ = 0.02, still growing with δ
and crossing the i80 UNDERPOWERED threshold at the registered escalation. The one
δ-invariant measurement is the mirror-identity one. Banked at
`runs/probe/Cr_hess/asym_blocks_sigmaF_2026-08-23.txt`.

## 5. The decision this surfaces — the entrant's

Under the analyzer as written, the block returns UNDERPOWERED at δ = 0.01 and VOID at
δ = 0.02, and its own text says REFUTED/CONFIRMED are unreachable at the design settings.
Under the registered rule's words, with σ measured as force noise rather than as Hessian
asymmetry, the same 37 SCFs would be scored against an i50 floor. The two readings differ
in what the analyzer *means* by "measured force noise", and that is an instrument question
with verdict consequences — which is exactly the kind of question P-AUTHORSHIP and A7.7
reserve for Frank. It most naturally lands in A8 (docs/47), alongside the am.2 / Q4a–Q4b
collision in §4 item 2, which needs resolving regardless. **Drafted the same day as
docs/47 §A8.7** — three questions, the measured consequence of each answer, proposals
tagged THRESHOLD for the entrant to re-author or reject; §4b's block table is the reason
offered for the proposed reading.

What is **not** in question, and is banked: 37 clean SCFs in one basin at 1e-10; a
reproducible out-of-plane H-carried imaginary mode at i243–i245 cm⁻¹ at 2×1v, 0.5 ML,
q = 0, with the image H-bond that held this block (1.338 Å at 1×1) gone (3.983 Å); force
noise at 1e-8 Ry/bohr. Whatever the verdict label, the numbers are these.

## 6. Provenance

- δ = 0.01: `runs/probe/Cr_hess/*.out` (tarball md5 `b8a3c935702d91a75ff9a42252862166`),
  `hessian_result_2026-08-23.json`, `hessian_analysis_2026-08-23.txt`.
- δ = 0.02: `runs/probe_d02/Cr_hess/*.out` (18 in tarball md5
  `23419426b6877d1bf8bca4c27963c7d0`, the 19th — `a37ym`, job 20090507 — in tarball md5
  `f34e20fe546cde7e6b865daf947f34c7`; the first attempt's partial output is kept on Anvil
  as `*.out.attempt1-died-in-scf-iter1-node-a196-job-20089685_5`), scored as
  `hessian_result_2026-08-23.json` / `hessian_analysis_2026-08-23.txt`, with the 18-deck
  `hessian_analysis_PREVIEW-18-of-19_2026-08-23.txt` retained. The builder's hardcoded
  `probe/` manifest prefix was fixed the same day so the 0.02 build could live in a separate
  root without overwriting the 0.01 decks (same filenames).
- Noise diagnostics: `src/dft/hessian_mirror_noise.py` (output banked at
  `runs/probe/Cr_hess/mirror_noise_sigmaF_2026-08-23.txt`) and
  `src/dft/hessian_asym_blocks.py` (`runs/probe/Cr_hess/asym_blocks_sigmaF_2026-08-23.txt`).
- Parity and sizing context: docs/46, docs/48.
