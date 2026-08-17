"""OER thermodynamics: theoretical overpotential from adsorption free energies.

Standard 4-step associative alkaline/acidic OER mechanism (Rossmeisl; Man 2011),
each step a concerted proton-electron transfer with ΔG referenced to the
equilibrium potential 1.23 V:

    *  + H2O -> *OH      ΔG1 = ΔG(*OH)
    *OH      -> *O       ΔG2 = ΔG(*O)  - ΔG(*OH)
    *O + H2O -> *OOH     ΔG3 = ΔG(*OOH) - ΔG(*O)
    *OOH     -> * + O2   ΔG4 = 4.92 - ΔG(*OOH)

Theoretical overpotential:  η = max(ΔG1..4) / e  - 1.23   (V).

The well-known scaling relation ΔG(*OOH) ≈ ΔG(*OH) + 3.2 eV (≈ 0.2 eV scatter)
pins conventional catalysts to a volcano whose apex is η ≈ 0.37 V at the optimal
descriptor ΔG(*O) - ΔG(*OH) ≈ 1.6 eV. Note (docs/43 Amendment 5, A5.1e): merely
breaking the 3.2 eV relation is not itself an activity gain — Razzaq & Exner,
ACS Catal. 13 (2023) 1740, §3.1 show a broken-scaling case whose G_max worsens,
with the statistical optimum at the asymmetric intercept 2.76 eV — so this
module treats the relation as a descriptor constraint to be measured against,
not a floor to be circumvented.

References
----------
Man et al., ChemCatChem 3 (2011) 1159.
Rossmeisl et al., J. Electroanal. Chem. 607 (2007) 83.
Razzaq & Exner, ACS Catal. 13 (2023) 1740.
"""
from __future__ import annotations

from dataclasses import dataclass

# Total Gibbs free energy of 2 H2O -> O2 + 4(H+ + e-) at U=0: 4 * 1.23 eV.
G_TOTAL = 4.92
OER_EQUILIBRIUM_V = 1.23
OOH_OH_SCALING = 3.2          # ΔG(*OOH) ≈ ΔG(*OH) + 3.2 eV (universal)
OPTIMAL_DESCRIPTOR = 1.6      # ΔG(*O) - ΔG(*OH), eV, volcano apex


@dataclass(frozen=True)
class OERResult:
    dG1: float
    dG2: float
    dG3: float
    dG4: float
    overpotential: float          # V
    potential_limiting_step: int  # 1..4


def oer_steps(dG_OH: float, dG_O: float, dG_OOH: float) -> tuple[float, float, float, float]:
    """The four OER reaction free energies (eV) from the three adsorption energies."""
    dG1 = dG_OH
    dG2 = dG_O - dG_OH
    dG3 = dG_OOH - dG_O
    dG4 = G_TOTAL - dG_OOH
    return dG1, dG2, dG3, dG4


def oer_overpotential(dG_OH: float, dG_O: float, dG_OOH: float) -> OERResult:
    """Compute the theoretical OER overpotential and the potential-limiting step."""
    steps = oer_steps(dG_OH, dG_O, dG_OOH)
    gmax = max(steps)
    eta = gmax - OER_EQUILIBRIUM_V       # per electron, e factored out (eV -> V)
    pls = int(steps.index(gmax)) + 1
    return OERResult(*steps, overpotential=eta, potential_limiting_step=pls)


def descriptor_from_dG_OH(dG_OH: float, dG_O: float) -> float:
    """The activity descriptor ΔG(*O) - ΔG(*OH) (eV)."""
    return dG_O - dG_OH


def overpotential_from_descriptor(descriptor: float, dG_OH: float | None = None) -> float:
    """Overpotential assuming the universal *OOH = *OH + 3.2 eV scaling.

    With the scaling enforced the descriptor x = ΔG(*O) - ΔG(*OH) controls the two
    middle steps (ΔG2 = x, ΔG3 = 3.2 - x); the apex is x = 1.6 -> η = 0.37 V. If
    `dG_OH` is given, the (typically non-limiting) terminal steps are included too.
    """
    dG2 = descriptor
    dG3 = OOH_OH_SCALING - descriptor
    middle = max(dG2, dG3)
    if dG_OH is None:
        return middle - OER_EQUILIBRIUM_V
    dG1 = dG_OH
    dG4 = G_TOTAL - (dG_OH + OOH_OH_SCALING)
    return max(dG1, dG2, dG3, dG4) - OER_EQUILIBRIUM_V
