"""Curated element-property tables for the earth-abundant 3d design space.

Values are hard-coded (not pulled from pymatgen) so the phase-stability metrics
reproduce the canonical Cantor-alloy numbers exactly and the package stays
dependency-light. Sources are cited per table.

Design space: Fe, Co, Ni, Cr, Mn, Cu (+ Al as an optional leachable element).
No platinum-group metals — the earth-abundance angle is the project's "so what".
"""
from __future__ import annotations

R_GAS = 8.314462618  # J / (mol K)

#: 12-coordinate metallic (Goldschmidt) atomic radii, Å.
#: Senkov & Miracle, *Materials Research Bulletin* 36 (2001); as tabulated in
#: Miracle & Senkov, *Acta Materialia* 122 (2017). Chosen because they reproduce
#: the canonical Cantor-alloy δ ≈ 3.3 %.
ATOMIC_RADIUS = {  # Å
    "Al": 1.432, "Cr": 1.249, "Mn": 1.350,
    "Fe": 1.241, "Co": 1.251, "Ni": 1.246, "Cu": 1.278,
}

#: Valence-electron concentration (s+d electrons), Guo & Liu, *Prog. Nat. Sci.* 21 (2011).
VEC = {"Al": 3, "Cr": 6, "Mn": 7, "Fe": 8, "Co": 9, "Ni": 10, "Cu": 11}

#: Melting points, K (CRC Handbook) — used for the Ω parameter (rule of mixtures).
MELTING_POINT = {  # K
    "Al": 933, "Cr": 2180, "Mn": 1519,
    "Fe": 1811, "Co": 1768, "Ni": 1728, "Cu": 1358,
}

#: Pauling electronegativity (CRC Handbook).
ELECTRONEGATIVITY = {
    "Al": 1.61, "Cr": 1.66, "Mn": 1.55,
    "Fe": 1.83, "Co": 1.88, "Ni": 1.91, "Cu": 1.90,
}

#: Crustal abundance, ppm by mass (CRC Handbook / USGS). Higher = more abundant.
CRUSTAL_ABUNDANCE_PPM = {
    "Al": 82300, "Cr": 102, "Mn": 950,
    "Fe": 56300, "Co": 25, "Ni": 84, "Cu": 60,
}

#: Rough metal price, USD/kg (order-of-magnitude, ~2024). Indicative only.
COST_USD_PER_KG = {
    "Al": 2.4, "Cr": 9.4, "Mn": 1.9,
    "Fe": 0.4, "Co": 33.0, "Ni": 18.0, "Cu": 9.0,
}

#: Oxophilicity proxy: standard oxide formation enthalpy per mole O, kJ/(mol O).
#: More negative = more oxophilic (binds O more strongly). From ΔHf° of the
#: representative oxide (CRC Handbook): Al2O3, Cr2O3, MnO, FeO, CoO, NiO, CuO.
OXOPHILICITY_KJ_PER_O = {
    "Al": -558.6, "Cr": -379.9, "Mn": -385.2,
    "Fe": -272.0, "Co": -237.9, "Ni": -239.7, "Cu": -157.3,
}

#: Binary mixing enthalpies ΔH_mix^AB, kJ/mol (regular-solution / Miedema), from
#: Takeuchi & Inoue, *Mater. Trans.* 46 (2005). Symmetric; self-pairs are 0.
_BINARY_DHMIX = {
    ("Al", "Cr"): -10, ("Al", "Mn"): -19, ("Al", "Fe"): -11, ("Al", "Co"): -19,
    ("Al", "Ni"): -22, ("Al", "Cu"): -1,
    ("Cr", "Mn"): 2, ("Cr", "Fe"): -1, ("Cr", "Co"): -4, ("Cr", "Ni"): -7,
    ("Cr", "Cu"): 12,
    ("Mn", "Fe"): 0, ("Mn", "Co"): -5, ("Mn", "Ni"): -8, ("Mn", "Cu"): 4,
    ("Fe", "Co"): -1, ("Fe", "Ni"): -2, ("Fe", "Cu"): 13,
    ("Co", "Ni"): 0, ("Co", "Cu"): 6,
    ("Ni", "Cu"): 4,
}

#: Default earth-abundant design space (no PGMs).
DEFAULT_ELEMENTS = ("Fe", "Co", "Ni", "Cr", "Mn", "Cu")


def binary_dHmix(a: str, b: str) -> float:
    """Return ΔH_mix^AB (kJ/mol) for elements a, b (0 if a == b)."""
    if a == b:
        return 0.0
    if (a, b) in _BINARY_DHMIX:
        return float(_BINARY_DHMIX[(a, b)])
    if (b, a) in _BINARY_DHMIX:
        return float(_BINARY_DHMIX[(b, a)])
    raise KeyError(f"No binary ΔH_mix tabulated for pair ({a}, {b})")
