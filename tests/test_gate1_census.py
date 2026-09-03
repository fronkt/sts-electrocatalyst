"""Tests for src/dft/gate1_census.py — the campaign-wide GATE-1 census.

The census exists to settle a contradiction between two hand-made counts, so the thing
that matters most is that it cannot quietly drop a row. These tests pin:

  T1  the verdict ladder matches the registered thresholds exactly at the boundaries;
  T2  every `__g1` child on disk is either paired or listed as an orphan — no silent loss;
  T3  the discharge rule only ever fires on a REFUSED row that has an AGREEing
      `.fromparent` sibling;
  T4  the banked census reproduces docs/45's independently recorded Ni chain-2 discharge
      (+0.012 meV) — an external witness that the parsing is right;
  T5  the branch split is bimodal with no overlap, the property docs/45 rests the
      0.05 muB tolerance on;
  T6  parser primitives behave on real files.

Tests read runs/ and docs/figs/ but NEVER write there.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD_PATH = os.path.join(ROOT, "src", "dft", "gate1_census.py")
JSON = os.path.join(ROOT, "docs", "figs", "gate1_census.json")


def _load():
    spec = importlib.util.spec_from_file_location("gate1_census", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = _load()


def _out():
    if not os.path.exists(JSON):
        pytest.skip("census not yet generated")
    return json.load(open(JSON, encoding="utf-8"))


# ------------------------------------------------------------------------ T1 --

def test_t1_verdict_ladder_at_the_registered_boundaries():
    # docs/43:311-314 -- "lands >= 5 meV lower" is BASIN_DRIFT, so -5.0 is inclusive
    assert G.verdict(-5.0) == "BASIN_DRIFT"
    assert G.verdict(-4.999) == "AGREE"
    # docs/43:1589-1592 -- "above its parent by more than 1 meV" is REFUSED
    assert G.verdict(1.0) == "AGREE"
    assert G.verdict(1.0001) == "REFUSED"
    assert G.verdict(0.0) == "AGREE"
    assert G.verdict(None) == "UNVERIFIED"


def test_t1b_thresholds_are_the_registered_numbers():
    assert G.BASIN_DRIFT_MEV == -5.0
    assert G.REFUSE_MEV == 1.0
    assert G.BRANCH_MUB == 0.1


# ------------------------------------------------------------------------ T2 --

def test_t2_no_child_is_silently_dropped():
    out = _out()
    assert out["n_children"] == out["n_paired"] + len(out["orphans"])
    assert len(out["rows"]) == out["n_paired"]
    # and the on-disk walk agrees with the recorded total
    assert len(G.find_children()) == out["n_children"]


def test_t2b_every_row_records_how_its_parent_was_resolved():
    for r in _out()["rows"]:
        assert r["resolved_by"], r["child"]


# ------------------------------------------------------------------------ T3 --

def test_t3_discharge_only_fires_on_a_refusal_with_an_agreeing_second_attempt():
    out = _out()
    rows = out["rows"]
    by_child = {r["child"]: r for r in rows}
    for r in rows:
        if not r["discharged_by_second_attempt"]:
            continue
        assert r["verdict"] == "REFUSED", r["child"]
        assert r["attempt"] == "first (cold)", r["child"]
        # a sibling second attempt on the same parent must exist and AGREE
        sibs = [s for s in rows
                if s["parent"] == r["parent"] and "fromparent" in s["child"]
                and s["verdict"] == "AGREE"]
        assert sibs, "no agreeing fromparent sibling for %s" % r["child"]
    assert by_child  # sanity


def test_t3b_post_discharge_counts_are_a_repartition_not_a_rewrite():
    out = _out()
    assert sum(out["counts_all"].values()) == sum(
        out["counts_all_post_discharge"].values()) == out["n_paired"]


# ------------------------------------------------------------------------ T4 --

def test_t4_reproduces_the_independently_recorded_ni_chain2_discharge():
    """docs/45 records the Ni basin *OH fromparent child at +0.012 meV vs its banked
    parent, scored on Anvil in 2026-08-24 and written down by hand. The census parses
    the same file from scratch; agreeing to 1e-3 meV is an external witness."""
    rows = _out()["rows"]
    hit = [r for r in rows if r["child"].endswith(
        "probe/Ni_basin/s0_OH__basin_g1.fromparent.out")]
    if not hit:
        pytest.skip("Ni chain-2 artifact absent")
    assert hit[0]["dE_meV"] == pytest.approx(0.012, abs=1e-3)
    assert hit[0]["verdict"] == "AGREE"


# ------------------------------------------------------------------------ T5 --

def test_t5_branch_split_is_bimodal_with_no_overlap():
    b = _out()["branch_split"]
    same, diff = b["same_branch_le_0p01"], b["different_branch_ge_0p18"]
    if not (same and diff):
        pytest.skip("one band empty")
    assert same["max_abs_dE_meV"] < diff["min_abs_dE_meV"], (
        "the bimodality docs/45 rests the 0.05 muB tolerance on has closed")


# ------------------------------------------------------------------------ T6 --

def test_t6_parsers_on_a_real_pair():
    rows = _out()["rows"]
    scored = [r for r in rows if r["dE_meV"] is not None]
    if not scored:
        pytest.skip("nothing scored")
    r = scored[0]
    c = os.path.join(G.RUNS, r["child"].replace("/", os.sep))
    p = os.path.join(G.RUNS, r["parent"].replace("/", os.sep))
    ec, ep = G.final_energy_ry(c), G.final_energy_ry(p)
    assert ec is not None and ep is not None
    assert (ec - ep) * G.RY_TO_MEV == pytest.approx(r["dE_meV"], abs=1e-9)
    assert G.converged(c) and G.converged(p)
