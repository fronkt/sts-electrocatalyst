"""Computational-hydrogen-electrode (CHE) referencing of OER intermediates.

Adsorption free energies are referenced to H2O and H2 (so no O2 reference is
needed), with standard ZPE−TΔS corrections added per adsorbate:

    ΔG(*OH)  = [E(*OH)  − E(*)] − (E_H2O − ½ E_H2) + 0.35
    ΔG(*O)   = [E(*O)   − E(*)] − (E_H2O −   E_H2) + 0.05
    ΔG(*OOH) = [E(*OOH) − E(*)] − (2 E_H2O − 3⁄2 E_H2) + 0.40

E_H2O, E_H2 are gas-phase energies from the *same* calculator. The per-adsorbate
constants are the conventional vibrational corrections (Man et al., ChemCatChem 3
(2011) 1159; Valdés et al., J. Phys. Chem. C 112 (2008) 9872) — a standard
screening approximation that folds in reference-molecule ZPE/entropy.
"""
from __future__ import annotations

#: ZPE − TΔS corrections per adsorbate, eV (Man 2011 / Valdés 2008, conventional).
ZPE_TS_CORRECTION = {"OH": 0.35, "O": 0.05, "OOH": 0.40}

#: Stoichiometric H2O/H2 reference coefficients (E_ref = a·E_H2O + b·E_H2).
_REF_COEFFS = {"OH": (1.0, -0.5), "O": (1.0, -1.0), "OOH": (2.0, -1.5)}


def reference_energy(species: str, E_H2O: float, E_H2: float) -> float:
    """The H2O/H2 reference energy subtracted for a given adsorbate."""
    a, b = _REF_COEFFS[species]
    return a * E_H2O + b * E_H2


def delta_G(E_slab: float, E_adslab: float, species: str, E_H2O: float, E_H2: float) -> float:
    """Free energy of adsorption ΔG (eV) for *OH/*O/*OOH via the CHE scheme."""
    dE = E_adslab - E_slab - reference_energy(species, E_H2O, E_H2)
    return dE + ZPE_TS_CORRECTION[species]
