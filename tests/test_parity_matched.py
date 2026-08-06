"""Tests for the matched-protocol parity scorer (docs/38).

Two things are worth locking down here, and neither is about the arithmetic:

1. `spearman` must agree with scipy, because the whole R0/R3 gate is a rank statistic
   and this module reimplements it to stay light-import.
2. `score` must not be able to report a gate as MET on a p it never checked. docs/38 §2
   turns on the fact that MACE is +0.900 at n = 5 with p = 0.0833 -- a rho ABOVE the
   0.8 threshold that still fails the gate. If `gate_met` ever ignores p, the project's
   headline claim silently loosens.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dft.parity_matched import GATE_RHO, score, spearman  # noqa: E402


def test_spearman_matches_scipy():
    scipy_stats = pytest.importorskip("scipy.stats")
    x = [0.491, 0.892, 1.263, 0.787, 0.781, 1.084, 0.544]
    y = [0.498, 1.241, 1.382, 0.646, 0.916, 1.200, 0.883]
    assert spearman(x, y) == pytest.approx(scipy_stats.spearmanr(x, y).statistic)


def test_spearman_is_perfect_on_a_monotone_map():
    x = [1.0, 2.0, 3.0, 4.0]
    assert spearman(x, [10.0, 20.0, 30.0, 40.0]) == pytest.approx(1.0)
    assert spearman(x, [40.0, 30.0, 20.0, 10.0]) == pytest.approx(-1.0)


def test_score_reproduces_the_published_n7_row():
    """The docs/38 §2 headline, from the real numbers."""
    ref = dict(Cr=0.491, Mn=0.892, Fe=1.263, Ru=0.787, Ir=0.781, Ni=1.084, Co=0.544)
    pred = dict(Cr=0.498, Mn=1.241, Fe=1.382, Ru=0.646, Ir=0.916, Ni=1.200, Co=0.883)
    s = score(pred, ref, list(ref))
    assert s["n"] == 7
    assert s["rho"] == pytest.approx(0.8571, abs=1e-4)
    assert s["p_exact"] == pytest.approx(0.0238, abs=1e-4)
    assert s["gate_met"] is True


def test_high_rho_still_fails_the_gate_when_n_is_too_small():
    """The n = 5 cut: rho +0.900 is ABOVE threshold and the gate must still fail.

    This is the disclosure docs/38 §2 exists to make -- dropping the two
    MACE-entangled metals leaves p = 0.0833.
    """
    ref = dict(Cr=0.491, Mn=0.892, Fe=1.263, Ru=0.787, Ir=0.781)
    pred = dict(Cr=0.498, Mn=1.241, Fe=1.382, Ru=0.646, Ir=0.916)
    s = score(pred, ref, list(ref))
    assert s["n"] == 5
    assert s["rho"] == pytest.approx(0.9, abs=1e-6)
    assert s["rho"] > GATE_RHO           # passes the rho threshold ...
    assert s["p_exact"] == pytest.approx(0.0833, abs=1e-4)
    assert s["gate_met"] is False        # ... and still fails the gate


def test_score_pairs_only_on_metals_present_in_both():
    ref = dict(Cr=0.491, Mn=0.892, Fe=1.263, Ru=0.787)
    pred = dict(Cr=0.498, Mn=1.241, Fe=1.382, Cu=9.9)   # Cu absent from ref
    s = score(pred, ref, list(ref) + ["Cu"])
    assert s["metals"] == ["Cr", "Fe", "Mn"]

    # a None eta (unparsed record) is dropped rather than coerced
    s2 = score(dict(pred, Ru=None), ref, list(ref))
    assert "Ru" not in s2["metals"]


def test_score_refuses_a_sample_too_small_to_mean_anything():
    ref = dict(Cr=0.491, Mn=0.892)
    assert score(dict(Cr=0.5, Mn=0.9), ref, list(ref)) is None
