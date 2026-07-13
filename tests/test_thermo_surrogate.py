"""Surrogate v0 must reproduce the docs/24 SS2 literature anchors and behave
monotonically before it is allowed anywhere near a BO loop."""
import pytest

from thermo.surrogate_v0 import ANCHORS, predict, wt_to_at


def test_pure_cu_annealed_is_iacs_100():
    p = predict({}, eta=0.0)
    assert p["iacs_pct"] == pytest.approx(100.0, abs=0.5)
    assert 390 <= p["kappa_W_mK"] <= 415          # handbook Cu ~ 401 W/mK


def test_hard_drawn_cu_anchor():
    p = predict({}, eta=5.0)
    assert p["iacs_pct"] == pytest.approx(97.0, abs=1.5)
    assert p["uts_MPa"] == pytest.approx(430.0, rel=0.08)


def test_cu14fe_published_anchor():
    p = predict({"Fe": 14.0}, eta=5.0)
    assert p["uts_MPa"] == pytest.approx(907.0, rel=0.10)
    assert p["iacs_pct"] == pytest.approx(54.3, abs=5.0)


def test_more_fe_is_stronger_and_less_conductive():
    spine = [predict({"Fe": x}, eta=3.0) for x in (2.0, 6.0, 10.0, 14.0)]
    uts = [p["uts_MPa"] for p in spine]
    iacs = [p["iacs_pct"] for p in spine]
    assert uts == sorted(uts)
    assert iacs == sorted(iacs, reverse=True)


def test_more_draw_is_stronger_and_less_conductive():
    curve = [predict({"Fe": 10.0}, eta=e) for e in (1.0, 2.0, 3.0, 4.0, 5.0)]
    uts = [p["uts_MPa"] for p in curve]
    iacs = [p["iacs_pct"] for p in curve]
    assert uts == sorted(uts)
    assert iacs == sorted(iacs, reverse=True)


def test_anneal_knob_trades_strength_for_conductivity():
    # precipitating Fe out of solution (lower c_ss) must raise IACS
    hi = predict({"Fe": 10.0}, eta=4.0, c_ss_fe_wt=0.3)
    lo = predict({"Fe": 10.0}, eta=4.0, c_ss_fe_wt=0.02)
    assert lo["iacs_pct"] > hi["iacs_pct"]


def test_ag_probe_is_gentler_than_fe_on_conductivity():
    base = predict({"Fe": 10.0}, eta=4.0)
    ag = predict({"Fe": 10.0, "Ag": 0.5}, eta=4.0)
    # same +0.5 wt.% but as Fe left in solid solution instead
    fe = predict({"Fe": 10.0}, eta=4.0, c_ss_fe_wt=0.55)
    assert ag["uts_MPa"] > base["uts_MPa"]
    ag_drop = base["iacs_pct"] - ag["iacs_pct"]
    fe_drop = base["iacs_pct"] - fe["iacs_pct"]
    # the Linde-coefficient ratio (0.355 vs 9.3 per at.%) is the whole reason
    # Ag is microalloy probe #1 - the model must preserve it
    assert 0 < ag_drop < fe_drop / 10.0


def test_wt_to_at_matches_weigh_sheet():
    at = wt_to_at({"Fe": 2.0})
    assert at["Fe"] == pytest.approx(2.27, abs=0.02)  # docs/27 Cu-2Fe row


def test_win_condition_is_inside_model_reach():
    # docs/24 win: >=700 MPa @ >=60 %IACS. The surrogate should place SOME
    # (composition, schedule) point in that box, else round-1 BO can't aim there.
    hits = [
        p for x in (4, 6, 8, 10, 12) for e in (3.5, 4.5, 5.5)
        if (p := predict({"Fe": float(x)}, eta=e, c_ss_fe_wt=0.02))["uts_MPa"] >= 700
        and p["iacs_pct"] >= 60
    ]
    assert hits, "no (x_Fe, eta) reaches the docs/24 win box - recalibrate"


def test_anchor_table_shape():
    assert len(ANCHORS) == 5 and all(len(a) == 3 for a in ANCHORS)
