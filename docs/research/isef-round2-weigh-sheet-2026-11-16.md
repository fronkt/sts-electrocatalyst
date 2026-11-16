# ISEF round-2 weigh sheet, 2026-11-16

Reproduce with `PYTHONPATH=src/scripts python src/scripts/weigh_sheet_round2.py`. Basis **200 g** per charge; **+25% Mn** over-charge (round 1 used +4% and came out Mn-low). Mass fraction w_i = x_i M_i / sum_j x_j M_j; nominal mass = basis x w_i. The at.% is the aim; the as-made composition is measured after melting (chip ICP-OES or SEM-EDS area analyses).

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

## Feedstock for all 3 charges

| Element | Weigh total (g) |
|---|---|
| Co | 141.6 |
| Cr | 26.1 |
| Fe | 177.4 |
| Mn | 72.6 |
| Ni | 196.8 |
| **Sum** | **614.5** |

Allow extra for one re-melt of any charge that misses +/-2 at.% (most likely R3 on Mn).
