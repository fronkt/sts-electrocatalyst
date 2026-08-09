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


def test_dG_is_invariant_under_any_per_element_E0_shift():
    """R3 Stage 0: the CHE reference is stoichiometrically closed.

    Adding an arbitrary per-element reference energy Sum_e n_e*a_e to every energy a
    model predicts leaves all three dG exactly unchanged, because the adslab-minus-slab
    composition difference is cancelled by the H2O/H2 reference term. Consequences in
    src/dft/e0_stage0.py: refitting E0 cannot change eta or the ranking, so the oc22
    rho = -1.00 is not a reference-energy artefact, and an R3 fine-tune must be gated
    on the CHE observable rather than on total-energy MAE (which E0 alone can shrink).
    """
    a_M, a_O, a_H = -3.7591, 2.4113, -1.0827   # deliberately large and asymmetric
    n = {"slab": (6, 12, 0), "O": (6, 13, 0), "OH": (6, 13, 1), "OOH": (6, 14, 1),
         "H2O": (0, 1, 2), "H2": (0, 0, 2)}

    def sh(k):
        m, o, h = n[k]
        return m * a_M + o * a_O + h * a_H

    E = {"slab": -130.1057, "O": -134.5002, "OH": -139.7865, "OOH": -143.8517,
         "H2O": -12.8117, "H2": -6.1328}

    for species in ("OH", "O", "OOH"):
        before = delta_G(E["slab"], E[species], species, E["H2O"], E["H2"])
        after = delta_G(E["slab"] + sh("slab"), E[species] + sh(species), species,
                        E["H2O"] + sh("H2O"), E["H2"] + sh("H2"))
        assert math.isclose(before, after, abs_tol=1e-12), species
