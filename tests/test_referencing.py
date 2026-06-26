"""CHE referencing: coefficients and an end-to-end ΔG → η check."""
import math

from hea_oer.referencing import delta_G, reference_energy, ZPE_TS_CORRECTION
from hea_oer.descriptors import oer_overpotential


def test_reference_coefficients():
    E_H2O, E_H2 = -14.0, -7.0
    assert math.isclose(reference_energy("OH", E_H2O, E_H2), E_H2O - 0.5 * E_H2)
    assert math.isclose(reference_energy("O", E_H2O, E_H2), E_H2O - E_H2)
    assert math.isclose(reference_energy("OOH", E_H2O, E_H2), 2 * E_H2O - 1.5 * E_H2)


def test_delta_G_adds_correction():
    E_slab, E_H2O, E_H2 = -100.0, -14.0, -7.0
    # make the bare electronic adsorption energy exactly +1.0 eV
    E_adslab = E_slab + reference_energy("OH", E_H2O, E_H2) + 1.0
    assert math.isclose(delta_G(E_slab, E_adslab, "OH", E_H2O, E_H2),
                        1.0 + ZPE_TS_CORRECTION["OH"], abs_tol=1e-9)


def test_referencing_recovers_apex_overpotential():
    """Construct adslab energies giving ΔG_OH=1.0, descriptor=1.6 -> η=0.37 V."""
    E_slab, E_H2O, E_H2 = 0.0, -14.0, -7.0

    def adslab(species, target_dG):
        return E_slab + reference_energy(species, E_H2O, E_H2) + (target_dG - ZPE_TS_CORRECTION[species])

    g = {
        "OH": delta_G(E_slab, adslab("OH", 1.0), "OH", E_H2O, E_H2),
        "O": delta_G(E_slab, adslab("O", 2.6), "O", E_H2O, E_H2),
        "OOH": delta_G(E_slab, adslab("OOH", 4.2), "OOH", E_H2O, E_H2),
    }
    assert math.isclose(g["OH"], 1.0, abs_tol=1e-9)
    res = oer_overpotential(g["OH"], g["O"], g["OOH"])
    assert math.isclose(res.overpotential, 0.37, abs_tol=1e-6)
