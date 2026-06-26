"""Empirical single-phase-solid-solution formability metrics for HEAs.

Implements the standard parametric criteria used to predict whether a multi-
principal-element alloy forms a disordered solid solution (meltable, single-phase
precursor) rather than intermetallics:

  VEC       valence-electron concentration -> FCC/BCC tendency (Guo 2011)
  delta     atomic-size mismatch, %                            (Zhang 2008)
  dS_mix    ideal configurational entropy, J/mol/K
  dH_mix    enthalpy of mixing (regular solution / Miedema), kJ/mol
  Omega     T_m * dS_mix / |dH_mix|                            (Yang & Zhang 2012)

Solid-solution heuristic (Yang & Zhang 2012; Guo 2011):
  Omega >= 1.1  AND  delta <= 6.6 %  (with -15 < dH_mix < 5 kJ/mol as a guard).

References
----------
Zhang et al., Adv. Eng. Mater. 10 (2008) 534.
Guo & Liu, Prog. Nat. Sci. 21 (2011) 433.
Yang & Zhang, Mater. Chem. Phys. 132 (2012) 233.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .composition import Composition
from .data import (
    ATOMIC_RADIUS, VEC, MELTING_POINT, R_GAS, binary_dHmix,
)

# Solid-solution thresholds
DELTA_MAX = 6.6      # %
OMEGA_MIN = 1.1
DHMIX_LO, DHMIX_HI = -15.0, 5.0  # kJ/mol


@dataclass(frozen=True)
class PhaseMetrics:
    vec: float
    delta: float          # %
    dS_mix: float         # J/mol/K
    dH_mix: float         # kJ/mol
    omega: float
    Tm: float             # K (rule of mixtures)
    phase_tendency: str   # "FCC" | "BCC" | "FCC+BCC"
    single_solid_solution: bool


def _mean(values: dict, comp: Composition) -> float:
    return float(sum(f * values[el] for el, f in zip(comp.elements, comp.fractions)))


def configurational_entropy(comp: Composition) -> float:
    """Ideal mixing entropy -R * Σ x ln x  (J/mol/K)."""
    x = np.array(comp.fractions, dtype=float)
    x = x[x > 0]
    return float(-R_GAS * np.sum(x * np.log(x)))


def size_mismatch(comp: Composition) -> float:
    """Atomic-size mismatch δ (%) = 100 * sqrt(Σ x_i (1 - r_i / r̄)^2)."""
    r = np.array([ATOMIC_RADIUS[el] for el in comp.elements])
    x = np.array(comp.fractions)
    r_bar = float(np.sum(x * r))
    return float(100.0 * np.sqrt(np.sum(x * (1.0 - r / r_bar) ** 2)))


def enthalpy_of_mixing(comp: Composition) -> float:
    """Regular-solution ΔH_mix = Σ_{i<j} 4 ΔH_ij x_i x_j  (kJ/mol)."""
    els, x = comp.elements, comp.fractions
    total = 0.0
    for i in range(len(els)):
        for j in range(i + 1, len(els)):
            total += 4.0 * binary_dHmix(els[i], els[j]) * x[i] * x[j]
    return float(total)


def vec_phase_tendency(vec: float) -> str:
    """Guo (2011): VEC >= 8 -> FCC; VEC < 6.87 -> BCC; else mixed FCC+BCC."""
    if vec >= 8.0:
        return "FCC"
    if vec < 6.87:
        return "BCC"
    return "FCC+BCC"


def phase_stability(comp: Composition) -> PhaseMetrics:
    """Compute all empirical solid-solution formability metrics for a composition."""
    vec = _mean(VEC, comp)
    delta = size_mismatch(comp)
    dS = configurational_entropy(comp)
    dH = enthalpy_of_mixing(comp)
    Tm = _mean(MELTING_POINT, comp)
    # Omega = Tm * dS / |dH|  ; dH converted kJ/mol -> J/mol
    dH_J = abs(dH) * 1000.0
    omega = float(Tm * dS / dH_J) if dH_J > 1e-9 else float("inf")
    ss = (omega >= OMEGA_MIN) and (delta <= DELTA_MAX) and (DHMIX_LO < dH < DHMIX_HI)
    return PhaseMetrics(
        vec=vec, delta=delta, dS_mix=dS, dH_mix=dH, omega=omega, Tm=Tm,
        phase_tendency=vec_phase_tendency(vec), single_solid_solution=ss,
    )


def _logistic(z: float) -> float:
    return 1.0 / (1.0 + np.exp(-z))


def formability_score(comp: Composition) -> float:
    """Smooth single-solid-solution formability score in [0, 1].

    Product of soft gates on the three criteria (δ small, Ω large, ΔH_mix in
    range). A continuous companion to the boolean `single_solid_solution` flag,
    suitable as a multi-objective term.
    """
    m = phase_stability(comp)
    g_delta = _logistic((DELTA_MAX - m.delta) / 1.0)            # high when δ < 6.6
    g_omega = _logistic((m.omega - OMEGA_MIN) / 0.5)            # high when Ω > 1.1
    centre = 0.5 * (DHMIX_LO + DHMIX_HI)
    half = 0.5 * (DHMIX_HI - DHMIX_LO)
    g_dh = _logistic((half - abs(m.dH_mix - centre)) / 3.0)    # high when ΔH in band
    return float(g_delta * g_omega * g_dh)
