"""eta from a bound when the *OOH job never converged.

Both `*OOH` jobs of the 2026-08-03/04 campaign failed (Ni: SCF diverged three times;
Co: credit exhausted at 16 ionic steps). eta is still determined for both, because
dG3 + dG4 = G_TOTAL - dG_O contains no dG_OOH -- so once dG_OH and dG_O are measured,
steps 3 and 4 can only be limiting if dG_OOH falls outside a computable window.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dft import eta_bounded as eb  # noqa: E402


def test_ni_window_is_wide_and_eta_is_determined():
    w = eb.eta_window(2.314, 4.556)
    assert w["eta"] == pytest.approx(1.084, abs=1e-3)
    assert w["pls"] == 1
    # window must contain the whole observed dG_OOH range with room to spare
    assert w["lo"] < eb.OBSERVED_DG_OOH[0] and w["hi"] > eb.OBSERVED_DG_OOH[1]
    assert w["margin_lo"] > 1.0 and w["margin_hi"] > 1.0


def test_co_window_is_tight_and_needs_the_partial_relaxation():
    """Co's high edge sits only 0.21 eV above the largest dG_OOH on record, so the
    observed-range argument alone is NOT enough -- the partial relax supplies an upper
    bound (a run stopped early sits above its own minimum) that closes it rigorously."""
    w = eb.eta_window(1.774, 3.382)
    assert w["eta"] == pytest.approx(0.544, abs=1e-3)
    assert w["pls"] == 1
    assert w["margin_hi"] < 0.25, "if this were comfortable, the partial would be unnecessary"
    assert 4.571 < w["hi"], "the measured upper bound must close the high edge"


def test_identity_dG3_plus_dG4_is_independent_of_dG_OOH():
    """The whole argument rests on this; pin it."""
    for dG_OH, dG_O in ((2.314, 4.556), (1.774, 3.382), (0.529, 1.692)):
        w = eb.eta_window(dG_OH, dG_O)
        assert w["dG3_plus_dG4"] == pytest.approx(eb.G_TOTAL - dG_O, abs=1e-12)


def test_a_step3_limited_metal_is_not_falsely_bounded():
    """Ru is pls=3 in the real tier: dG_OOH 3.709, dG_O 1.692 -> dG3 = 2.017 > dG1/dG2.
    The window must EXCLUDE its true dG_OOH, i.e. refuse to claim eta without it."""
    w = eb.eta_window(0.529, 1.692)
    assert not (w["lo"] < 3.709 < w["hi"]), \
        "Ru's real dG_OOH must fall outside the window, so the bound declines to apply"
