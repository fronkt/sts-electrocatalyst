"""Structural validity checks — the failure class `qe_qc` is blind to.

`qe_qc` is entirely numerical (SCF converged, forces small, an energy exists). These
two real cases passed every one of its checks and are still chemically meaningless:

  * Mn_slab/s0_OOH and Fe_slab/s0_OOH — verdict TRUSTWORTHY, "converged" in 2 and 13
    ionic steps with the *OOH 3.83/3.95 A from the metal. A desorbed molecule has no
    forces on it, so it converges instantly and trivially.
  * Cr_slab/s0_O — TRUSTWORTHY and genuinely force-converged, but at a Cr-O bond of
    2.016 A where every other metal reaches 1.67-1.77 A.
"""
import math
import os
import sys

import pytest
from ase import Atoms

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dft import adsorbate_qc as aq  # noqa: E402


def _slab_with_adsorbate(metal: str, m_o: float, n_ads: int = 1):
    """6 metal + 12 O rutile-like slab (18 atoms) plus an adsorbate at height m_o."""
    pos, sym = [], []
    for i in range(6):
        pos.append([2.0 * (i % 3), 2.0 * (i // 3), 5.0]); sym.append(metal)
    for i in range(12):
        pos.append([1.0 * (i % 4), 1.5 * (i // 4), 4.0]); sym.append("O")
    # adsorbate sits directly above metal atom 0, at distance m_o
    for k in range(n_ads):
        pos.append([0.0, 0.0, 5.0 + m_o + 1.2 * k]); sym.append("O" if k < 2 else "H")
    return Atoms(symbols=sym, positions=pos, cell=[12, 12, 24], pbc=True)


def test_bound_adsorbate_passes():
    at = _slab_with_adsorbate("Ru", 1.70)
    r = aq.check_structure(at, "Ru")
    assert r["ok"], r["reasons"]
    assert r["m_o_min"] == pytest.approx(1.70, abs=1e-3)


def test_desorbed_adsorbate_is_caught():
    """The Mn/Fe s0_OOH case: converged, force-free, and 3.9 A off the surface."""
    at = _slab_with_adsorbate("Mn", 3.95, n_ads=3)
    r = aq.check_structure(at, "Mn")
    assert not r["ok"]
    assert "not bound" in r["reasons"][0]
    assert r["m_o_min"] == pytest.approx(3.95, abs=1e-3)


def test_weakly_bound_minimum_is_flagged_not_failed():
    """CORRECTION 2026-08-02. The original single 2.40 A cut assumed nothing legitimate
    sits between chemisorption and desorption. Fe_slab/s0_OOH restarted from 2.076 A
    relaxed to 2.552 A at 0.376 eV LOWER energy than the desorbed original -- a real
    minimum in the supposedly impossible gap, and within 0.013 A of MACE's independent
    2.565 A. A weakly-bound adsorbate must be surfaced, never rejected.
    """
    r = aq.check_structure(_slab_with_adsorbate("Fe", 2.552, n_ads=3), "Fe")
    assert r["tier"] == "weak"
    assert r["ok"], "a genuine weakly-bound minimum must not be failed"
    assert aq.check_structure(_slab_with_adsorbate("Cr", 2.10), "Cr")["tier"] == "bound"
    assert aq.check_structure(_slab_with_adsorbate("Cr", 3.95), "Cr")["tier"] == "desorbed"


def test_too_few_ionic_steps_is_caught_regardless_of_distance():
    """The signal that actually separated the defects: Mn/Fe stopped at 2 and 13 steps,
    their repaired counterparts took 29+. Distance alone could not do this."""
    at = _slab_with_adsorbate("Mn", 2.10, n_ads=3)          # perfectly good geometry
    assert aq.check_structure(at, "Mn", n_ionic=40)["ok"]
    bad = aq.check_structure(at, "Mn", n_ionic=2)
    assert not bad["ok"] and "barely moved" in bad["reasons"][0]


def test_negative_fourth_step_is_flagged():
    """dG_OOH > 4.92 eV makes dG4 exergonic at 0 V — impossible for a real OER path.

    Mn (4.989) and Fe (5.221) both do this, which is the thermodynamic shadow of the
    same desorption the geometry check catches directly.
    """
    assert aq.check_thermo(3.709) == []          # Ru, healthy
    assert aq.check_thermo(4.799) == []          # Cr, healthy
    assert aq.check_thermo(5.221)                # Fe pre-repair, dG4 = -0.301, real
    assert "exergonic" in aq.check_thermo(5.221)[0]


def test_dG4_tolerance_does_not_overclaim():
    """CORRECTION 2026-08-02. G_TOTAL is the experimental 4x1.23 V while dG_OOH carries
    a GGA error of order 0.1-0.2 eV, so a marginally negative dG4 is consistent with
    zero, not impossible. The repaired Mn sits at dG4 = -0.022 eV after a full 34-step
    relaxation; calling that unphysical would be overclaiming. Fe's pre-repair -0.301
    is the scale of a genuine violation.
    """
    assert aq.check_thermo(4.942) == [], "repaired Mn (dG4 = -0.022) must not be flagged"
    assert aq.check_thermo(5.221), "Fe pre-repair (dG4 = -0.301) must still be flagged"


def test_cross_metal_outlier_finds_the_trapped_relaxation():
    """Cr's real numbers against the other four."""
    bonds = {"Cr": 2.016, "Mn": 1.671, "Fe": 1.774, "Ru": 1.698, "Ir": 1.767}
    msgs = aq.cross_metal_outliers(bonds)
    assert len(msgs) == 1 and msgs[0].startswith("Cr:")
    # and it stays quiet when every metal agrees
    assert aq.cross_metal_outliers(
        {"Mn": 1.671, "Fe": 1.774, "Ru": 1.698, "Ir": 1.767}) == []


def test_outlier_check_needs_three_metals():
    """A median is not a reference with two points; must not fabricate a verdict."""
    assert aq.cross_metal_outliers({"Cr": 2.016, "Ru": 1.698}) == []


def test_clean_slab_has_nothing_to_check():
    at = _slab_with_adsorbate("Ru", 1.7)[:18]
    r = aq.check_structure(at, "Ru")
    assert r["ok"] and r["n_ads"] == 0


def test_cross_metal_test_does_not_condemn_the_verified_repairs():
    """CORRECTION 2026-08-03, the third threshold in this module falsified by real data.

    Run over the repaired tier, the median outlier test flagged Fe/s0_OOH (2.552 A) and
    Mn/s0_OOH (2.480 A) as trapped relaxations -- the two structures the 2026-08-02 DFT
    campaign was bought to verify, and which MACE independently reproduced to 0.013 and
    0.06 A. The cause is that `*OOH` binding is BIMODAL across this tier:

        Ir 1.912  Ru 1.947  Cr 2.076  |  Mn 2.480  Fe 2.552

    A median is not a reference for a bimodal distribution -- it always accuses the
    smaller mode. `*O` (span 0.202 A) and `*OH` (span 0.089 A) are genuinely uniform and
    the test remains valid there.
    """
    ooh = {"Cr": 2.076, "Mn": 2.480, "Fe": 2.552, "Ru": 1.947, "Ir": 1.912}
    assert "s0_OOH" not in aq.OUTLIER_STATES, "the median test must not run on *OOH"
    # and if it did, it would wrongly condemn both verified repairs
    wrongly = aq.cross_metal_outliers(ooh)
    assert len(wrongly) == 2 and {m.split(":")[0] for m in wrongly} == {"Fe", "Mn"}


def test_cross_metal_test_still_applies_where_binding_is_uniform():
    """*O and *OH stay in scope: their real spreads are 0.202 and 0.089 A."""
    assert set(aq.OUTLIER_STATES) == {"s0_O", "s0_OH"}
    o_verified = {"Cr": 1.572, "Mn": 1.671, "Fe": 1.774, "Ru": 1.698, "Ir": 1.767}
    assert aq.cross_metal_outliers(o_verified) == [], "repaired *O tier must be clean"
    # the failed Ni s0_O (SCF died at step 17) must still be caught
    assert any(m.startswith("Ni:") for m in
               aq.cross_metal_outliers({**o_verified, "Ni": 2.817}))
