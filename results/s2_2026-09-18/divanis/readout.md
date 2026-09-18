# P-DIVANIS exact correction-sensitivity readout

This is an external-table arithmetic reconstruction, not a prediction of electrode performance. The primary result covers the full delta interval [0, 0.10] eV; no single correction value is elected.

The scored count ranges from **1 to 1 of 38**. Curve outcome(s): **FALSIFIED**. Count invariant: True; selected membership invariant: True; verdict invariant: True.

Population: Man 26, Mom 11, Frydendal 1, across three articles. The historical 24-article label belongs to the entire ESI. Repeated material rows and the unlegended b suffix are retained. The lexical selection does not independently establish phase identity or stability.

Corrections to the source adsorption-energy columns are OH +0.35 eV, O +0.05 eV, and OOH +(0.35 + delta) eV. The imposed cycle total is 4.92 eV. At each row's own scaling intercept c, the exact floor is max(c, 4.92-c)/2 - 1.23 V. Numerator requires eta <0.60 V and excess above that floor <=0.050 eV; denominator remains 38. Counts >=10 are HELD, <=3 FALSIFIED, and 4–9 SCORED — MIDDLE BAND / NOT MET.

All source decimals, intersections and inequalities use rational arithmetic. The partition includes active CHE-step and floor-branch crossings, both predicate roots and fourth-step zero crossings. Boundary points are evaluated separately from open intervals; ties remain explicit. Decimal coordinates below are display values; exact fractions and all row values are in readout.json.

| Delta region (eV) | Selected /38 | Man /26 | Mom /11 | Frydendal /1 | Curve outcome | Negative fourth steps |
|---|---:|---:|---:|---:|---|---:|
| {0} | 1 | 1 | 0 | 0 | FALSIFIED | 7 |
| (0, 0.005) | 1 | 1 | 0 | 0 | FALSIFIED | 7 |
| {0.005} | 1 | 1 | 0 | 0 | FALSIFIED | 7 |
| (0.005, 0.01) | 1 | 1 | 0 | 0 | FALSIFIED | 7 |
| {0.01} | 1 | 1 | 0 | 0 | FALSIFIED | 7 |
| (0.01, 0.04) | 1 | 1 | 0 | 0 | FALSIFIED | 8 |
| {0.04} | 1 | 1 | 0 | 0 | FALSIFIED | 8 |
| (0.04, 0.05) | 1 | 1 | 0 | 0 | FALSIFIED | 8 |
| {0.05} | 1 | 1 | 0 | 0 | FALSIFIED | 8 |
| (0.05, 0.06) | 1 | 1 | 0 | 0 | FALSIFIED | 8 |
| {0.06} | 1 | 1 | 0 | 0 | FALSIFIED | 8 |
| (0.06, 0.08) | 1 | 1 | 0 | 0 | FALSIFIED | 8 |
| {0.08} | 1 | 1 | 0 | 0 | FALSIFIED | 8 |
| (0.08, 0.1) | 1 | 1 | 0 | 0 | FALSIFIED | 8 |
| {0.1} | 1 | 1 | 0 | 0 | FALSIFIED | 8 |

## Negative fourth-step free energies

These rows are retained in the denominator. A downhill fourth step under the imposed CHE cycle does not establish a physically impossible material or an incorrect paper. Their exact interval memberships, including equality cases, are in the JSON.

| Source row | Article | Structure token | DeltaG4 at delta=0 (eV) | DeltaG4 at delta=0.10 (eV) |
|---|---:|---|---:|---:|
| divanis-si2-L109 | 1 | TiO2 | -0.29 | -0.39 |
| divanis-si2-L151 | 1 | MnO2 | 0.01 | -0.09 |
| divanis-si2-L152 | 1 | CrO2 | -0.41 | -0.51 |
| divanis-si2-L296 | 7 | SnO2 | -0.35 | -0.45 |
| divanis-si2-L299 | 7 | PbO2 | -0.65 | -0.75 |
| divanis-si2-L304 | 7 | TiO2 | -0.29 | -0.39 |
| divanis-si2-L309 | 7 | PbO2 | -0.16 | -0.26 |
| divanis-si2-L321 | 7 | PbO2 | -0.12 | -0.22 |

## Historical arithmetic guard

At delta=0.05 solely to reproduce the registered source-row guard, divanis-si2-L152 reconstructs eta=1.96 V and DeltaG4=-0.46 eV. This external-table check neither selects a correction convention nor makes a Cr electrode-performance claim. The high-coverage attribution is external to the ESI row label.

## Verification

Source SHA-256: `88bfcda9a5e70da10d3b2565af7cc09b7377578e4aac4dd5d9a74b42c0bd8bda`. Selection re-derived from raw text: 38/38 identities match. The independent raw-source verifier uses a separate parser and the absolute-value floor formula, and checks an over-partition containing even inactive branch roots.

Independent verification passed: True; 570 exact row/sample comparisons and 23 independently constructed point/open-interval probes. Input/code hashes, all roots, active-step ties, negative-step sets and per-row threshold decisions are included in readout.json.
