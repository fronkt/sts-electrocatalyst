"""Tests for src/dft/a0n18_surface.py (docs/43 A11.R9, registered 2026-09-03 at 01a76df).

A11.R9's whole value is in what it REFUSES, so that is what these pin:

  T1  the common-grid rule requires ALL THREE step states per metal per rung -- the
      union-of-states reading (which the registration text originally used) is wrong
      and would silently admit a rung where a metal has no s0_O;
  T2  every rung really is n = 18, and a short rung is FATAL rather than reported;
  T3  the CHE step construction reproduces A11.R7's own dq1/dq2/dq3 at u000;
  T4  u000 reproduces A11.R7's published post-hoc rho to 4 dp -- the pipeline witness;
  T5  no pooled n = 126 statistic is emitted anywhere in the artifact;
  T6  the anti-selection contract holds: every rung on the common grid is reported, and
      the post-hoc rung is flagged as seen-before;
  T7  the binding clause and the multiplicity statement are on the face of the JSON.

Tests read docs/figs/ but NEVER write there. All writes go to tmp_path.
"""
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "dft", "a0n18_surface.py")
R9_JSON = os.path.join(ROOT, "docs", "figs", "a0n18_surface.json")
R7_JSON = os.path.join(ROOT, "docs", "figs", "a0lowdin_valence.json")


def _load():
    spec = importlib.util.spec_from_file_location("a0n18_surface", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def M():
    return _load()


@pytest.fixture(scope="module")
def out():
    if not os.path.exists(R9_JSON):
        pytest.skip("a0n18_surface.json not generated yet")
    with open(R9_JSON, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def r7():
    if not os.path.exists(R7_JSON):
        pytest.skip("a0lowdin_valence.json missing")
    with open(R7_JSON, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------ T1: the grid rule ---

def test_T1_grid_requires_all_three_states_per_metal(M):
    """A metal with s0_OH and s0_OOH at a rung but no s0_O does NOT contribute that rung.
    This is the exact defect the registration's first wording had."""
    pm = {m: {"dq_d": {}} for m in M.METALS}
    for m in M.METALS:
        for st in M.STEP_STATES:
            for u in ("u000", "u150"):
                pm[m]["dq_d"]["%s|%s" % (st, u)] = 0.1
    # every metal also has s0_OH+s0_OOH at u300, but only ONE has s0_O there
    for m in M.METALS:
        pm[m]["dq_d"]["s0_OH|u300"] = 0.1
        pm[m]["dq_d"]["s0_OOH|u300"] = 0.1
    pm[M.METALS[0]]["dq_d"]["s0_O|u300"] = 0.1

    grid = M.common_grid(pm)
    assert "u300" not in grid, \
        "a rung where five of six metals lack s0_O must not enter the common grid"
    assert grid == ["u000", "u150"]


def test_T1b_real_grid_excludes_the_Fe_gap(out, r7):
    """On the real bank, Fe has no s0_O at u300/u450, so neither is a common rung."""
    assert "u300" not in out["grid"]["rungs"]
    assert "u450" not in out["grid"]["rungs"]
    assert "s0_O|u300" not in r7["per_metal"]["Fe"]["dq_d"], \
        "the premise of this test: Fe genuinely lacks s0_O at u300"
    assert "s0_O|u300" in r7["per_metal"]["Ti"]["dq_d"], \
        "and other metals genuinely have it, so the gap is Fe's alone"


# ------------------------------------------------------------ T2: n = 18 ---

def test_T2_every_rung_is_n18(out):
    assert out["grid"]["n_rungs"] == len(out["rungs"])
    assert len(out["rungs"]) >= 2
    for r in out["rungs"]:
        assert r["n"] == 18
        assert len(r["pairs"]) == 18
        metals = {p["metal"] for p in r["pairs"]}
        steps = {p["step"] for p in r["pairs"]}
        assert len(metals) == 6 and steps == {1, 2, 3}


def test_T2b_short_rung_is_fatal(M, tmp_path, r7):
    """A rung that yields fewer than 18 pairs must raise, not be quietly reported."""
    doctored = json.loads(json.dumps(r7))
    # give every metal a bogus common rung, but delete one metal's span so n<18 path trips
    del doctored["per_metal"]["Cr"]["span_dG2"]
    p = tmp_path / "r7.json"
    p.write_text(json.dumps(doctored), encoding="utf-8")
    with pytest.raises(M.Fatal) as ei:
        M.main(["--json", str(tmp_path / "o.json"), "--md", str(tmp_path / "o.md"),
                "--r7-json", str(p)])
    assert "span_dG2" in str(ei.value)


# ---------------------------------------------- T3/T4: it is R7's instrument ---

def test_T3_step_construction_matches_R7_at_u000(M, r7):
    pm = r7["per_metal"]
    for metal in M.METALS:
        st = M.steps_at(pm, metal, "u000")
        assert st is not None
        for i in (1, 2, 3):
            assert st[i] == pytest.approx(pm[metal]["dq%d" % i], abs=1e-9), \
                "%s step %d must equal A11.R7's dq%d" % (metal, i, i)


def test_T4_u000_reproduces_the_published_posthoc_rho(out):
    """The pipeline witness: u000 must land on A11.R7's own published post-hoc figure."""
    u0 = [r for r in out["rungs"] if r["u"] == "u000"]
    assert len(u0) == 1
    assert u0[0]["rho"] == pytest.approx(-0.3808, abs=5e-5)
    assert u0[0]["seen_before"] is True
    assert out["seen_before_context"]["u000_a11r7_posthoc"]["rho"] == pytest.approx(
        u0[0]["rho"], abs=5e-5)


# ------------------------------------------------- T5: pooling is refused ---

def test_T5_no_pooled_statistic_anywhere(out):
    assert "pooling_refused" in out
    assert "NEVER pooled" in out["pooling_refused"]
    blob = json.dumps(out)
    assert '"n": 126' not in blob and '"n":126' not in blob, \
        "a pooled n=126 statistic must not exist in the artifact"
    for r in out["rungs"]:
        assert r["n"] == 18


# ------------------------------------------ T6: the anti-selection contract ---

def test_T6_all_rungs_reported_and_posthoc_flagged(out):
    reported = [r["u"] for r in out["rungs"]]
    assert reported == sorted(out["grid"]["rungs"]), \
        "every common-grid rung must be reported; selection is forbidden"
    seen = [r["u"] for r in out["rungs"] if r["seen_before"]]
    assert seen == [out["grid"]["posthoc_rung"]], \
        "exactly the post-hoc rung is flagged seen-before"
    oos = out["grid"]["out_of_sample_rungs"]
    assert out["grid"]["posthoc_rung"] not in oos
    assert len(oos) == len(reported) - 1
    d = out["distribution"]
    assert d["rho_min"] <= d["rho_median"] <= d["rho_max"]
    assert d["out_of_sample_only"]["n_rungs"] == len(oos)


# --------------------------------------------------------- T7: the binding ---

def test_T7_binding_and_multiplicity_present(out):
    b = out["binding"]
    assert "CONFIRMATORY-INELIGIBLE" in b
    assert "cannot move A7.2 or A7.3" in b
    assert "NOT MET at 3 of 6" in b
    m = out["multiplicity"]
    assert "UPPER BOUND" in m and "not" in m
    assert "NOMINAL" in out["p_is_nominal"]
    assert out["zero_su"] is True
    assert "not promoted" in json.dumps(out["seen_before_context"]).lower() or \
        "NEVER SCORED" in json.dumps(out["seen_before_context"])
