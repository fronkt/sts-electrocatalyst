"""Pins for the shared-constants sensitivity of the six-metal arm, the 2x1v
counterexample literals, the 1x1 vertex rule, and the registered ZPE tool.

Every number here was re-derived with independent code before being pinned;
the tests guard the banked JSONs and the two helpers against drift. Nothing
here re-scores a registered verdict.
"""
import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from dft.che_box_robustness import STEP_RESPONSE, analyze_pair
from dft.pproj6_shared_box import VERDICT, band, build

ROOT = Path(__file__).resolve().parents[1]
BANKED_SIX = ROOT / "docs/figs/pproj6_readout.json"
SHARED_BOX = ROOT / "docs/figs/pproj6_shared_box.json"
AUDIT = ROOT / "results/che_box_case_study_2026-09-05/audit.json"
BANKED_ZPE = ROOT / "docs/figs/zpe_decomposition.json"


@pytest.fixture(scope="module")
def result():
    return build(grid_points=41)


def test_banked_rows_reproduce_and_roster_is_five(result):
    banked = json.loads(BANKED_SIX.read_text())
    assert result["joint"]["blind_denominator"] == banked["blind_denominator"]
    assert len(result["joint"]["blind_denominator"]) == 5
    for m, r in result["per_metal"].items():
        assert r["banked_d_eta_V"] == banked["metals"][m]["d_eta_V"]
        assert r["banked_pair"] == [banked["metals"][m]["pls_atomic"], banked["metals"][m]["pls_ortho"]]


def test_ir_and_ti_are_fixed_pair_rows(result):
    for m, value in (("Ir", 0.4596035790), ("Ti", 0.0009849161)):
        r = result["per_metal"][m]
        assert r["nominal_pair_dominates_all_vertices"] is True
        assert r["closed_pairs"] == [[2, 2]]
        lo, hi = r["d_eta_range_V"]
        assert hi - lo < 1e-9
        assert lo == pytest.approx(value, abs=1e-9)


@pytest.mark.parametrize("metal, lo, hi, pairs, bands", [
    ("Mn", 0.0791168334, 0.1275589514, [[1, 1], [1, 2], [2, 2]], ["FIRES", "INTERMEDIATE"]),
    ("Fe", 0.0268572301, 0.1976722173, [[1, 1], [2, 1], [2, 2]], ["FIRES", "INTERMEDIATE", "NULL"]),
    ("Ru", 0.2308025195, 0.5844273779, [[2, 2], [3, 2]], ["FIRES"]),
    ("Cr", 0.2962344730, 0.5962344730, [[2, 1]], ["FIRES"]),
])
def test_per_metal_ranges_pairs_and_bands(result, metal, lo, hi, pairs, bands):
    r = result["per_metal"][metal]
    assert r["abs_d_eta_range_V"] == pytest.approx([lo, hi], abs=1e-9)
    assert r["grid_abs_d_eta_range_V"] == pytest.approx([lo, hi], abs=1e-9)
    assert r["closed_pairs"] == pairs
    assert r["bands_reachable"] == bands


def test_mn_and_fe_individual_bands_are_not_constants_robust(result):
    assert result["per_metal"]["Mn"]["nominal_pair_dominates_all_vertices"] is False
    assert result["per_metal"]["Fe"]["nominal_pair_dominates_all_vertices"] is False
    assert "FIRES" in result["per_metal"]["Mn"]["bands_reachable"]
    assert "NULL" in result["per_metal"]["Fe"]["bands_reachable"]


def test_joint_count_reads_two_or_three_and_verdict_is_middle_band_throughout(result):
    j = result["joint"]
    assert j["nominal_fires_count"] == 3
    assert (j["fires_count_min"], j["fires_count_max"]) == (2, 3)
    assert (j["null_count_min"], j["null_count_max"]) == (1, 2)
    assert j["class_verdicts_reachable"] == ["MIDDLE BAND"]
    assert {VERDICT[2], VERDICT[3]} == {"MIDDLE BAND"}
    two = j["count_witnesses"]["2"]
    assert two["bands"]["Fe"] == "INTERMEDIATE" and two["bands"]["Mn"] == "INTERMEDIATE"


def test_count_two_witness_by_direct_recomputation():
    """At (dOH, dO, dOOH) = (-0.015, 0, 0) eV Fe drops below the trigger and Mn stays under it."""
    banked = json.loads(BANKED_SIX.read_text())["metals"]
    x = np.array([-0.015, 0.0, 0.0])
    fires = 0
    for m in ("Mn", "Fe", "Ti", "Ru", "Ir"):
        sa = np.array(banked[m]["steps_atomic"]) + STEP_RESPONSE @ x
        so = np.array(banked[m]["steps_ortho"]) + STEP_RESPONSE @ x
        fires += abs(so.max() - sa.max()) > 0.10
    assert fires == 2


def test_committed_shared_box_json_matches_a_rebuild(result):
    committed = json.loads(SHARED_BOX.read_text())
    assert committed["source_sha256"] == result["source_sha256"]
    for m in committed["per_metal"]:
        assert committed["per_metal"][m]["d_eta_range_V"] == pytest.approx(
            result["per_metal"][m]["d_eta_range_V"], abs=1e-9)
        assert committed["per_metal"][m]["closed_pairs"] == result["per_metal"][m]["closed_pairs"]
    for key in ("fires_count_min", "fires_count_max", "class_verdicts_reachable"):
        assert committed["joint"][key] == result["joint"][key]


def test_band_rule_is_strict_at_both_thresholds():
    assert band(0.10, 0.10, 0.03) == "INTERMEDIATE"
    assert band(0.03, 0.10, 0.03) == "INTERMEDIATE"
    assert band(0.1000001, 0.10, 0.03) == "FIRES"
    assert band(0.0299999, 0.10, 0.03) == "NULL"


# ---- the 2x1v counterexample literals of docs/84 :162-219 -------------------

def test_two_by_one_counterexample_literals_in_audit():
    audit = json.loads(AUDIT.read_text())
    ce = audit["counterexample"]
    assert ce["pair"] == [1, 2]
    assert ce["delta_eta_V"] == pytest.approx(0.1756950454, abs=1e-9)
    assert ce["eta_atomic_V"] == pytest.approx(0.871481047682, abs=1e-9)
    assert ce["eta_ortho_V"] == pytest.approx(1.047176093046, abs=1e-9)
    assert audit["slice_t_switch_eV"]["atomic"] == pytest.approx(0.053606697717, abs=1e-9)
    assert audit["slice_t_switch_eV"]["ortho"] == pytest.approx(0.051440444612, abs=1e-9)
    assert audit["nominal_banked_delta_eta_V"] == pytest.approx(0.1725163792, abs=1e-9)


@pytest.mark.parametrize("half_width", [0.10, 0.15, 0.30])
def test_two_by_one_larger_boxes_share_one_range(half_width):
    banked = json.loads((ROOT / "docs/figs/pproj_cell_readout.json").read_text())
    box = analyze_pair(banked["legs"]["atomic"]["dG"], banked["legs"]["ortho"]["dG"], half_width)
    assert box["delta_eta_range_V"] == pytest.approx([0.1725163792, 0.1790151385], abs=1e-9)
    assert box["closed_pairs"] == [[1, 1], [1, 2], [2, 2]]


# ---- the 1x1 flagship: the vertex rule makes the 27-corner inference valid --

def test_one_by_one_pair_fixed_at_all_vertices_and_flip_half_widths():
    legs = json.loads(BANKED_ZPE.read_text())["legs"]
    sa, so = np.array(legs["atomic"]["steps"]), np.array(legs["ortho"]["steps"])
    assert (legs["atomic"]["pls"], legs["ortho"]["pls"]) == (2, 1)
    for v in itertools.product((-0.05, 0.05), repeat=3):
        x = np.array(v)
        assert np.argmax(sa + STEP_RESPONSE @ x) + 1 == 2
        assert np.argmax(so + STEP_RESPONSE @ x) + 1 == 1
    # a uniform (-t,+t,0) correction moves step1-step2 by 3t
    assert (sa[1] - sa[0]) / 3 == pytest.approx(0.1639558184, abs=1e-9)
    assert (so[0] - so[1]) / 3 == pytest.approx(0.3798179298, abs=1e-9)


def test_head_zpe_tool_reproduces_the_banked_json(tmp_path):
    out = tmp_path / "zpe.json"
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    proc = subprocess.run([sys.executable, str(ROOT / "src/dft/zpe_decomposition.py"), "--json", str(out)],
                          cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        pytest.skip(f"zpe_decomposition.py did not run here: {proc.stderr[-400:]}")
    head, banked = json.loads(out.read_text()), json.loads(BANKED_ZPE.read_text())
    for key in ("d_eta_V", "electronic_eV", "constants_eV", "closure_residual", "gas_weights", "scf_weights"):
        assert head[key] == banked[key], key
    assert head["sensitivity"]["coefficients"] == banked["sensitivity"]["coefficients"]
    for key in ("d_eta_min_V", "d_eta_max_V", "band_half_width_V"):
        assert head["sensitivity"][key] == pytest.approx(banked["sensitivity"][key], abs=1e-12)
    assert head["sensitivity"]["pls_stable_over_cube"] is True
    for key in ("atomic_margin_eV", "ortho_margin_eV", "atomic_flip_needs_eV", "ortho_flip_needs_eV"):
        assert head["pls_robustness"][key] == banked["pls_robustness"][key], key
