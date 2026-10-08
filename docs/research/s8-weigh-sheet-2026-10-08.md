# S8 batch-1 weigh sheet, 2026-10-08

Status: proposed; basis **200.0 g** per button (the button Fort Wayne Metals melts; Song Cai, 2026-10-07) and **+4% Mn** are [CONFIRM] values in the [stage-1 freeze proposal](s8-stage1-freeze-proposal-2026-10-07.md). Nothing is melted before the freeze is deposited. Supersedes the 10 g, five-alloy [sheet of 2026-10-07](s8-weigh-sheet-2026-10-07.md). Compositions are the exact at.% of `results/r4_gated.json`; molar masses are IUPAC standard atomic weights (`src/scripts/weigh_sheet.py`). Reproduce with `PYTHONPATH=src/scripts python src/scripts/weigh_sheet_s8.py`.

Mass fraction w_i = x_i M_i / Σ_j x_j M_j; nominal mass = basis × w_i; the Mn weigh target adds the over-charge. The at.% is the design target: verify the actual composition by SEM-EDS after melting.

## Cu8Cr23Mn35Co34
*candidate (census leader)*  ·  mean molar mass 56.329 g/mol  ·  charge 200.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Cu | 7.887 | 63.546 | 8.898 | 17.795 | **17.795** |
| Cr | 22.634 | 51.996 | 20.893 | 41.786 | **41.786** |
| Mn | 34.993 | 54.938 | 34.130 | 68.259 | **70.989** (+4% Mn) |
| Co | 34.485 | 58.933 | 36.080 | 72.159 | **72.159** |
| **Σ** | 100.000 | — | 100.000 | 200.000 | **202.730** |

## Ni31Cr29Cu5Mn35
*candidate (August screen leader)*  ·  mean molar mass 55.693 g/mol  ·  charge 200.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Ni | 31.115 | 58.693 | 32.791 | 65.582 | **65.582** |
| Cr | 29.187 | 51.996 | 27.250 | 54.500 | **54.500** |
| Cu | 5.169 | 63.546 | 5.898 | 11.796 | **11.796** |
| Mn | 34.529 | 54.938 | 34.061 | 68.122 | **70.847** (+4% Mn) |
| **Σ** | 100.000 | — | 100.000 | 200.000 | **202.725** |

## Fe25Co25Ni25Cr25
*candidate (August screen #2)*  ·  mean molar mass 56.367 g/mol  ·  charge 200.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Fe | 25.000 | 55.845 | 24.769 | 49.537 | **49.537** |
| Co | 25.000 | 58.933 | 26.138 | 52.276 | **52.276** |
| Ni | 25.000 | 58.693 | 26.032 | 52.063 | **52.063** |
| Cr | 25.000 | 51.996 | 23.061 | 46.123 | **46.123** |
| **Σ** | 100.000 | — | 100.000 | 200.000 | **200.000** |

## Cu26Ni9Cr31Co33
*candidate (strict-policy leader)*  ·  mean molar mass 57.917 g/mol  ·  charge 200.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Cu | 25.780 | 63.546 | 28.286 | 56.571 | **56.571** |
| Ni | 9.393 | 58.693 | 9.519 | 19.037 | **19.037** |
| Cr | 31.466 | 51.996 | 28.249 | 56.498 | **56.498** |
| Co | 33.362 | 58.933 | 33.947 | 67.894 | **67.894** |
| **Σ** | 100.000 | — | 100.000 | 200.000 | **200.000** |

## Ni34Fe6Cu29Co31
*set member (sixth gated alloy; no Cr or Mn; added 2026-10-08)*  ·  mean molar mass 60.025 g/mol  ·  charge 200.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Ni | 33.877 | 58.693 | 33.126 | 66.251 | **66.251** |
| Fe | 5.962 | 55.845 | 5.546 | 11.093 | **11.093** |
| Cu | 29.423 | 63.546 | 31.149 | 62.297 | **62.297** |
| Co | 30.738 | 58.933 | 30.179 | 60.358 | **60.358** |
| **Σ** | 100.000 | — | 100.000 | 200.000 | **200.000** |

## Cu22Fe30Co32Mn15
*anchor (predicted poor by both MLIP arms)*  ·  mean molar mass 58.409 g/mol  ·  charge 200.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Cu | 22.116 | 63.546 | 24.061 | 48.122 | **48.122** |
| Fe | 29.974 | 55.845 | 28.659 | 57.317 | **57.317** |
| Co | 32.425 | 58.933 | 32.716 | 65.432 | **65.432** |
| Mn | 15.484 | 54.938 | 14.564 | 29.128 | **30.293** (+4% Mn) |
| **Σ** | 100.000 | — | 100.000 | 200.000 | **201.165** |

## Feedstock for one batch-1 melt of all six

| Element | Weigh total (g) |
|---|---|
| Co | 318.120 |
| Cr | 198.907 |
| Cu | 196.583 |
| Fe | 117.947 |
| Mn | 172.130 |
| Ni | 202.934 |
| **Σ** | **1206.620** |

Allow extra for possible re-melts (one per alloy that misses ±2 at.%; most likely the two ~35 at.% Mn alloys).

**Safety:** four of the six alloys contain 22.6–31.5 at.% Cr (Cu22Fe30Co32Mn15 and Ni34Fe6Cu29Co31 have none). A dated, mentor-signed Cr(VI) risk assessment is required before the first melt (freeze proposal §7).
