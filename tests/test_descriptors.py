"""OER thermodynamics: scaling-relation floor and step bookkeeping."""
import math

from hea_oer.descriptors import (
    oer_steps, oer_overpotential, overpotential_from_descriptor,
    G_TOTAL, OPTIMAL_DESCRIPTOR,
)


def test_steps_sum_to_total():
    # ΔG1+ΔG2+ΔG3+ΔG4 == 4.92 eV for any adsorption energies
    s = oer_steps(0.8, 2.1, 4.0)
    assert math.isclose(sum(s), G_TOTAL, abs_tol=1e-9)


def test_apex_overpotential_is_037V():
    # dG_OH=1.0, descriptor 1.6 -> dG_O=2.6, dG_OOH=4.2 -> η = 1.6 - 1.23 = 0.37 V
    res = oer_overpotential(1.0, 2.6, 4.2)
    assert math.isclose(res.overpotential, 0.37, abs_tol=1e-6)


def test_scaling_floor_is_037_at_optimal_descriptor():
    # with the universal *OOH=*OH+3.2 scaling, the volcano apex is x=1.6 -> 0.37 V
    apex = overpotential_from_descriptor(OPTIMAL_DESCRIPTOR)
    assert math.isclose(apex, 0.37, abs_tol=1e-6)
    grid = [0.1 * i for i in range(5, 28)]  # 0.5 .. 2.7 eV
    etas = [overpotential_from_descriptor(x) for x in grid]
    assert min(etas) >= 0.37 - 1e-9
    # the minimum sits at the optimal descriptor
    x_min = grid[etas.index(min(etas))]
    assert abs(x_min - OPTIMAL_DESCRIPTOR) <= 0.1


def test_overpotential_increases_away_from_apex():
    apex = overpotential_from_descriptor(1.6)
    assert overpotential_from_descriptor(1.2) > apex
    assert overpotential_from_descriptor(2.0) > apex
