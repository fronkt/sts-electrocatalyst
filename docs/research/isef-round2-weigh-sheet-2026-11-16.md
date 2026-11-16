# ISEF round-2 weigh sheet, 2026-11-16

Reproduce with `PYTHONPATH=src/scripts python src/scripts/weigh_sheet_round2.py`. Basis **200 g** per charge; **+25% Mn** over-charge (round 1 used +4% and came out Mn-low). Mass fraction w_i = x_i M_i / sum_j x_j M_j; nominal mass = basis x w_i. The at.% is the aim; the as-made composition is measured after melting (chip ICP-OES or SEM-EDS area analyses).

## R0: Cu26Ni9Cr31Co33
*round-1 alloy C, fresh melt at the same aim (completes round 1)*  -  mean molar mass 57.917 g/mol  -  charge 200.0 g

| Element | at.% | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|
| Cu | 25.780 | 28.285 | 56.571 | **56.571** |
| Ni | 9.393 | 9.519 | 19.038 | **19.038** |
| Cr | 31.466 | 28.249 | 56.498 | **56.498** |
| Co | 33.362 | 33.947 | 67.894 | **67.894** |
| **Sum** | 100.000 | 100.000 | 200.000 | **200.000** |

## R1: FeCoNi
*Fe25 without Cr (Cr 0 on the Fe:Co:Ni backbone)*  -  mean molar mass 57.824 g/mol  -  charge 200.0 g

| Element | at.% | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|
| Fe | 33.333 | 32.193 | 64.385 | **64.385** |
| Co | 33.333 | 33.973 | 67.946 | **67.946** |
| Ni | 33.333 | 33.834 | 67.669 | **67.669** |
| **Sum** | 100.000 | 100.000 | 200.000 | **200.000** |

## R2: CoCr0.5FeNi
*Cr 14.3 at.%, midpoint between R1 and Fe25*  -  mean molar mass 56.991 g/mol  -  charge 200.0 g

| Element | at.% | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|
| Co | 28.571 | 29.545 | 59.090 | **59.090** |
| Cr | 14.286 | 13.034 | 26.067 | **26.067** |
| Fe | 28.571 | 27.997 | 55.994 | **55.994** |
| Ni | 28.571 | 29.425 | 58.849 | **58.849** |
| **Sum** | 100.000 | 100.000 | 200.000 | **200.000** |

## R3: Ni34Fe29Mn30Co7
*sharpest test: old screen ranked it last, film rule puts it on top*  -  mean molar mass 56.757 g/mol  -  charge 200.0 g

| Element | at.% | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|
| Ni | 34.000 | 35.160 | 70.319 | **70.319** |
| Fe | 29.000 | 28.534 | 57.068 | **57.068** |
| Mn | 30.000 | 29.038 | 58.077 | **72.596** (+25% Mn) |
| Co | 7.000 | 7.268 | 14.537 | **14.537** |
| **Sum** | 100.000 | 100.000 | 200.000 | **214.519** |

Expected Mn after melting (aim 30.0 at.%): 10% loss -> 32.5, 13% loss -> 31.8, 20% loss -> 30.0, 25% loss -> 28.7, 27% loss -> 28.1, 30% loss -> 27.3 at.%.

## R4: Ni86Cu14
*single-phase twin of Ni31's leached film*  -  mean molar mass 59.372 g/mol  -  charge 200.0 g

| Element | at.% | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|
| Ni | 86.000 | 85.016 | 170.032 | **170.032** |
| Cu | 14.000 | 14.984 | 29.968 | **29.968** |
| **Sum** | 100.000 | 100.000 | 200.000 | **200.000** |

## R5: Mn31Ni31Co33Cu6
*mid-range anchor*  -  mean molar mass 57.907 g/mol  -  charge 200.0 g

| Element | at.% | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|
| Mn | 30.693 | 29.119 | 58.239 | **72.798** (+25% Mn) |
| Ni | 30.693 | 31.110 | 62.219 | **62.219** |
| Co | 32.673 | 33.252 | 66.504 | **66.504** |
| Cu | 5.941 | 6.519 | 13.038 | **13.038** |
| **Sum** | 100.000 | 100.000 | 200.000 | **214.560** |

Expected Mn after melting (aim 30.7 at.%): 10% loss -> 33.3, 13% loss -> 32.5, 20% loss -> 30.7, 25% loss -> 29.3, 27% loss -> 28.8, 30% loss -> 27.9 at.%.

## Feedstock for all 6 charges

| Element | Weigh total (g) |
|---|---|
| Co | 276.0 |
| Cr | 82.6 |
| Cu | 99.6 |
| Fe | 177.4 |
| Mn | 145.4 |
| Ni | 448.1 |
| **Sum** | **1229.1** |

Allow extra for one re-melt of any charge that misses +/-2 at.% (most likely R3 and R5 on Mn, R0 on Cu).
