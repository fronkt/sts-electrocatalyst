"""Phase-stability metrics must reproduce canonical Cantor-alloy values."""
import math

from hea_oer.composition import Composition
from hea_oer.phase_stability import phase_stability, formability_score
from hea_oer.data import R_GAS


def cantor():
    return Composition.equiatomic(["Co", "Cr", "Fe", "Mn", "Ni"])


def test_cantor_entropy_is_R_ln5():
    m = phase_stability(cantor())
    assert math.isclose(m.dS_mix, R_GAS * math.log(5), rel_tol=1e-6)


def test_cantor_enthalpy_matches_literature():
    # Σ binary ΔH over the 10 pairs = -26 kJ/mol -> 4 * 0.04 * (-26) = -4.16 kJ/mol
    m = phase_stability(cantor())
    assert math.isclose(m.dH_mix, -4.16, abs_tol=0.05)


def test_cantor_size_mismatch_small():
    m = phase_stability(cantor())
    assert 3.0 < m.delta < 3.6  # canonical Cantor δ ≈ 3.27 %


def test_cantor_is_single_solid_solution_fcc():
    m = phase_stability(cantor())
    assert m.omega > 1.1
    assert m.single_solid_solution is True
    assert math.isclose(m.vec, 8.0, abs_tol=1e-9)
    assert m.phase_tendency == "FCC"


def test_cantor_formability_high():
    assert formability_score(cantor()) > 0.8


def test_immiscible_pair_not_solid_solution():
    # Fe-Cu has strongly positive ΔH_mix (4 * 13 * 0.25 = 13 kJ/mol) -> no SS
    m = phase_stability(Composition(("Fe", "Cu"), (0.5, 0.5)))
    assert math.isclose(m.dH_mix, 13.0, abs_tol=0.1)
    assert m.single_solid_solution is False
    assert formability_score(Composition(("Fe", "Cu"), (0.5, 0.5))) < 0.5
