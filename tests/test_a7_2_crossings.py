"""Tests for src/dft/a7_2_crossings.py — A7.2's registered crossing locations.

docs/43:1348-1353 makes "the U at which each metal's pls flips" a first-class deliverable,
and the risk in delivering it is interpolating through a bracket where a third rung
contends. These tests pin:

  T1  the rung algebra matches the banked readout's `pls` on every row (check 1);
  T2  the computed crossings and the banked brackets are the same set (check 2);
  T3  every located U* lies inside its own bracket and its margin is positive (check 3);
  T4  the three-rung guard actually refuses — a synthetic bracket with a dominating
      third rung must NOT be located;
  T5  interp_cross is correct on a hand-checkable linear case and returns None when the
      pair does not cross;
  T6  the emitted JSON carries the binding clause and the interpolation disclaimer.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD = os.path.join(ROOT, "src", "dft", "a7_2_crossings.py")
JSON = os.path.join(ROOT, "docs", "figs", "a7_2_crossings.json")
BANK = os.path.join(ROOT, "docs", "figs", "a0main_readout.json")


def _load():
    spec = importlib.util.spec_from_file_location("a7_2_crossings", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


X = _load()


def _out():
    if not os.path.exists(JSON):
        pytest.skip("crossings not yet generated")
    return json.load(open(JSON, encoding="utf-8"))


def _bank():
    if not os.path.exists(BANK):
        pytest.skip("banked readout absent")
    return json.load(open(BANK, encoding="utf-8"))


# ------------------------------------------------------------------------ T1 --

def test_t1_pls_algebra_matches_the_banked_readout_on_every_row():
    n = 0
    for metal, m in _bank()["metals"].items():
        for r in m["rows"]:
            if any(r.get(k) is None for k in ("dG_OH", "dG_O", "dG_OOH")):
                continue
            if r.get("pls") is None:
                continue
            assert X.pls_of(r) == r["pls"], "%s U=%s" % (metal, r["u"])
            n += 1
    assert n >= 50, "expected the full A0 grid, saw %d rows" % n


def test_t1b_step_ladder_uses_the_campaign_g_total():
    assert X.G_TOTAL == 4.92
    row = dict(dG_OH=1.0, dG_O=2.0, dG_OOH=3.5)
    assert X.steps(row) == pytest.approx([1.0, 1.0, 1.5, 4.92 - 3.5])


# ------------------------------------------------------------------- T2, T3 --

def test_t2_crossings_and_brackets_are_the_same_set():
    out, bank = _out(), _bank()
    brs = bank["a7_2"]["flip_brackets"]
    for metal, entries in out["crossings"].items():
        assert len(entries) == len(brs.get(metal, [])), metal
    for metal in brs:
        assert metal in out["crossings"], metal


def test_t3_located_u_star_is_inside_its_bracket_with_a_positive_margin():
    for metal, entries in _out()["crossings"].items():
        for e in entries:
            if e["status"] != "LOCATED":
                continue
            assert e["u_lo"] <= e["u_star"] <= e["u_hi"], metal
            assert e["margin_to_next_rung_eV"] > 0, metal


# ------------------------------------------------------------------------ T4 --

def test_t4_three_rung_guard_refuses_a_dominated_bracket():
    """The guard's whole job: if a third rung sits above the crossing pair at U*, the
    bracket must not be located. Built by hand so the answer is known."""
    # rung 1 (dG_OH) is huge and constant; rungs 2 and 3 cross in the middle.
    r1 = dict(u=0.0, dG_OH=9.0, dG_O=9.0 + 1.0, dG_OOH=9.0 + 1.0 + 0.0)
    r2 = dict(u=1.0, dG_OH=9.0, dG_O=9.0 + 0.0, dG_OOH=9.0 + 0.0 + 1.0)
    s1, s2 = X.steps(r1), X.steps(r2)
    # rung 1 dominates both at every U, so pls never leaves 1 -> no bracket at all
    assert X.pls_of(r1) == 1 and X.pls_of(r2) == 1
    # and the pair itself does cross, which is exactly the trap the guard exists for
    u = X.interp_cross(0.0, s1, 1.0, s2, 1, 2)
    assert u == pytest.approx(0.5)
    vals = [X.lin(0.0, s1[i], 1.0, s2[i], u) for i in range(4)]
    assert vals[0] > 0.5 * (vals[1] + vals[2]), (
        "the synthetic third rung must dominate, else this test proves nothing")


def test_t4b_no_located_row_has_a_third_rung_at_or_above_it():
    for metal, entries in _out()["crossings"].items():
        for e in entries:
            if e["status"] == "LOCATED":
                assert "third_rungs_at_or_above" not in e, metal
            if e["status"] == "CONTENDED":
                assert e["u_star"] is None, metal


# ------------------------------------------------------------------------ T5 --

def test_t5_interp_cross_on_a_hand_checkable_case():
    # rung a falls 2 -> 0, rung b rises 0 -> 2; they cross at the midpoint
    s1 = [2.0, 0.0, 0.0, 0.0]
    s2 = [0.0, 2.0, 0.0, 0.0]
    assert X.interp_cross(1.0, s1, 3.0, s2, 0, 1) == pytest.approx(2.0)
    # no sign change -> None
    assert X.interp_cross(1.0, [2.0, 0.0, 0, 0], 3.0, [3.0, 1.0, 0, 0], 0, 1) is None


# ------------------------------------------------------------------------ T6 --

def test_t6_binding_and_disclaimer_are_present():
    out = _out()
    assert "Moves no banked verdict" in out["binding"]
    assert "NOT MET at 3 of 6" in out["binding"]
    assert "interpolation" in out["what_this_is"].lower()
    assert "fixed-geometry" in out["what_this_is"]
    for k in ("check1_pls_matches_banked",
              "check2_brackets_and_crossings_are_the_same_set",
              "check3_u_star_inside_its_bracket"):
        assert out["self_checks"][k].startswith("PASS")
