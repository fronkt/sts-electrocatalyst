# S8 batch-1 weigh sheet, 2026-10-07

> **Superseded 2026-10-08** by [s8-weigh-sheet-2026-10-08.md](s8-weigh-sheet-2026-10-08.md): six alloys (Ni34Fe6Cu29Co31 added) at the 200 g button Fort Wayne Metals melts. Kept because its 10 g numbers went to Fort Wayne Metals on 2026-10-07; `src/scripts/weigh_sheet_s8.py` at commit c3a4353 reproduces it.

Status: proposed; basis **10.0 g** per button and **+4% Mn** are [CONFIRM] values in the [stage-1 freeze proposal](s8-stage1-freeze-proposal-2026-10-07.md). Nothing is melted before the freeze is deposited. Compositions are the exact at.% of `results/r4_gated.json`; molar masses are IUPAC standard atomic weights (`src/scripts/weigh_sheet.py`). Reproduce with `PYTHONPATH=src/scripts python src/scripts/weigh_sheet_s8.py`.

Mass fraction w_i = x_i M_i / Σ_j x_j M_j; nominal mass = basis × w_i; the Mn weigh target adds the over-charge. The at.% is the design target: verify the actual composition by SEM-EDS after melting.

## Cu8Cr23Mn35Co34
*candidate (census leader)*  ·  mean molar mass 56.329 g/mol  ·  charge 10.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Cu | 7.887 | 63.546 | 8.898 | 0.890 | **0.890** |
| Cr | 22.634 | 51.996 | 20.893 | 2.089 | **2.089** |
| Mn | 34.993 | 54.938 | 34.130 | 3.413 | **3.549** (+4% Mn) |
| Co | 34.485 | 58.933 | 36.080 | 3.608 | **3.608** |
| **Σ** | 100.000 | — | 100.000 | 10.000 | **10.137** |

## Ni31Cr29Cu5Mn35
*candidate (August screen leader)*  ·  mean molar mass 55.693 g/mol  ·  charge 10.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Ni | 31.115 | 58.693 | 32.791 | 3.279 | **3.279** |
| Cr | 29.187 | 51.996 | 27.250 | 2.725 | **2.725** |
| Cu | 5.169 | 63.546 | 5.898 | 0.590 | **0.590** |
| Mn | 34.529 | 54.938 | 34.061 | 3.406 | **3.542** (+4% Mn) |
| **Σ** | 100.000 | — | 100.000 | 10.000 | **10.136** |

## Fe25Co25Ni25Cr25
*candidate (August screen #2)*  ·  mean molar mass 56.367 g/mol  ·  charge 10.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Fe | 25.000 | 55.845 | 24.769 | 2.477 | **2.477** |
| Co | 25.000 | 58.933 | 26.138 | 2.614 | **2.614** |
| Ni | 25.000 | 58.693 | 26.032 | 2.603 | **2.603** |
| Cr | 25.000 | 51.996 | 23.061 | 2.306 | **2.306** |
| **Σ** | 100.000 | — | 100.000 | 10.000 | **10.000** |

## Cu26Ni9Cr31Co33
*candidate (strict-policy leader)*  ·  mean molar mass 57.917 g/mol  ·  charge 10.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Cu | 25.780 | 63.546 | 28.286 | 2.829 | **2.829** |
| Ni | 9.393 | 58.693 | 9.519 | 0.952 | **0.952** |
| Cr | 31.466 | 51.996 | 28.249 | 2.825 | **2.825** |
| Co | 33.362 | 58.933 | 33.947 | 3.395 | **3.395** |
| **Σ** | 100.000 | — | 100.000 | 10.000 | **10.000** |

## Cu22Fe30Co32Mn15
*anchor (predicted poor by both MLIP arms)*  ·  mean molar mass 58.409 g/mol  ·  charge 10.0 g

| Element | at.% | Atomic weight (g/mol) | wt.% | Nominal mass (g) | **Weigh target (g)** |
|---|---|---|---|---|---|
| Cu | 22.116 | 63.546 | 24.061 | 2.406 | **2.406** |
| Fe | 29.974 | 55.845 | 28.659 | 2.866 | **2.866** |
| Co | 32.425 | 58.933 | 32.716 | 3.272 | **3.272** |
| Mn | 15.484 | 54.938 | 14.564 | 1.456 | **1.515** (+4% Mn) |
| **Σ** | 100.000 | — | 100.000 | 10.000 | **10.058** |

## Feedstock for one batch-1 melt of all five

| Element | Weigh total (g) |
|---|---|
| Co | 12.888 |
| Cr | 9.945 |
| Cu | 6.714 |
| Fe | 5.343 |
| Mn | 8.606 |
| Ni | 6.834 |
| **Σ** | **50.331** |

Allow extra for possible re-melts (one per alloy that misses ±2 at.%; most likely the two ~35 at.% Mn alloys).

**Safety:** four of the five alloys contain 22.6–31.5 at.% Cr (Cu22Fe30Co32Mn15 has none). A dated, mentor-signed Cr(VI) risk assessment is required before the first melt (freeze proposal §7).
