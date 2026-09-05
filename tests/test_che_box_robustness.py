"""Continuous CHE sensitivity: analytic certificates and missed-grid cases."""
import itertools
import json
from pathlib import Path

import numpy as np
import pytest

from dft.che_box_robustness import analyze_pair, che_steps, main, STEP_RESPONSE


@pytest.fixture
def adopted_cell_pair():
    path = Path(__file__).resolve().parents[1] / "docs/figs/pproj_cell_readout.json"
    legs = json.loads(path.read_text(encoding="utf-8"))["legs"]
    return legs["atomic"]["dG"], legs["ortho"]["dG"]


def test_adopted_cell_thin_disagreement_missed_by_27_grid(adopted_cell_pair):
    left, right = adopted_cell_pair
    sl, sr = che_steps(left), che_steps(right)
    # Every point of the old 3x3x3 test agrees, yet the continuum does not.
    for x in itertools.product((-.1, 0., .1), repeat=3):
        assert np.argmax(sl + STEP_RESPONSE @ x) == np.argmax(sr + STEP_RESPONSE @ x)
    x = np.array((-.0525, .0525, 0.))
    assert np.argmax(sl + STEP_RESPONSE @ x) == 0
    assert np.argmax(sr + STEP_RESPONSE @ x) == 1
    result = analyze_pair(left, right, .1)
    assert result["strict_pairs"] == [[1, 1], [1, 2], [2, 2]]
    assert result["strict_disagreement_possible"]
    region = next(r for r in result["regions"] if r["pair"] == [1, 2])
    assert region["max_strict_margin_eV"] == pytest.approx(.003249379657063)
    assert region["margin_witness"]["maximizers_left"] == [1]
    assert region["margin_witness"]["maximizers_right"] == [2]
    assert result["delta_eta_range_V"] == pytest.approx(
        [.17251637919980567, .17901513851393247])


def test_registered_005_box_is_constant_and_has_no_strict_flip(adopted_cell_pair):
    result = analyze_pair(*adopted_cell_pair, .05)
    assert result["strict_pairs"] == [[1, 1]]
    assert not result["strict_disagreement_possible"]
    assert result["delta_eta_range_V"] == pytest.approx([.17251637919980567] * 2)


def test_continuous_extremum_between_all_27_grid_values():
    # Left's max is 2+|x-.04|; right's max is 2.5 for x in [-.1,.1].
    # The difference 0.5-|x-.04| therefore has a strict interior maximum.
    left = [1.96, 4., 4.46]  # steps: 1.96+x, 2.04-x, .46, .46
    right = [1., 2., 4.5]   # steps: 1+x, 1-x, 2.5, .42
    result = analyze_pair(left, right, [.1, 0., 0.])
    assert result["delta_eta_range_V"] == pytest.approx([.36, .5])
    assert result["maximum"]["correction_eV"]["OH"] == pytest.approx(.04)
    assert result["maximum"]["maximizers_left"] == [1, 2]
    grid_max = max(max(che_steps(right) + STEP_RESPONSE @ (x, 0, 0))
                   - max(che_steps(left) + STEP_RESPONSE @ (x, 0, 0))
                   for x in (-.1, 0., .1))
    assert grid_max == pytest.approx(.46)
    assert result["maximum"]["delta_eta_V"] > grid_max


def test_zero_box_ties_do_not_count_as_strict_disagreement():
    # All four steps tie in both legs; different maximizer labels are not flips.
    result = analyze_pair([1.23, 2.46, 3.69], [1.23, 2.46, 3.69], 0.)
    assert len(result["closed_pairs"]) == 16
    assert result["strict_pairs"] == []
    assert not result["strict_disagreement_possible"]
    assert result["delta_eta_range_V"] == pytest.approx([0., 0.])
    assert all(r["status"] == "tie_or_unresolved_at_tolerance" for r in result["regions"])


def test_zero_box_with_unique_steps_and_mapping_order():
    result = analyze_pair({"OOH": 4., "O": 3., "OH": 2.}, [1., 2., 4.5], 0.)
    assert result["strict_pairs"] == [[1, 3]]
    assert result["delta_eta_range_V"] == [.5, .5]
    assert result["strict_disagreement_possible"]


def test_witnesses_recompute_and_swapping_legs_negates_interval(adopted_cell_pair):
    left, right = adopted_cell_pair
    result = analyze_pair(left, right, [.14, .08, .2])
    reversed_result = analyze_pair(right, left, [.14, .08, .2])
    assert reversed_result["delta_eta_range_V"] == pytest.approx(
        [-result["delta_eta_range_V"][1], -result["delta_eta_range_V"][0]])
    for region in result["regions"]:
        for kind in ("margin_witness", "minimum", "maximum"):
            w = region[kind]
            x = [w["correction_eV"][s] for s in ("OH", "O", "OOH")]
            assert np.all(np.abs(x) <= np.array([.14, .08, .2]) + 1e-9)
            sl, sr = che_steps(left) + STEP_RESPONSE @ x, che_steps(right) + STEP_RESPONSE @ x
            assert sum(sl) == pytest.approx(4.92)
            assert sum(sr) == pytest.approx(4.92)
            assert w["delta_eta_V"] == pytest.approx(max(sr) - max(sl))
            i, j = region["pair"]
            assert sl[i - 1] == pytest.approx(max(sl))
            assert sr[j - 1] == pytest.approx(max(sr))
    assert analyze_pair(left, right, [.14, .08, .2]) == result


@pytest.mark.parametrize("bad", [[], [1, 2], [1, 2, 3, 4], [[1, 2, 3]],
                                  [1, float("nan"), 3], [1, 2, float("inf")],
                                  {"OH": 1, "O": 2}, "bad", None])
def test_malformed_adsorption_values_fail(bad):
    with pytest.raises(ValueError):
        analyze_pair(bad, [1, 2, 3], .1)
    with pytest.raises(ValueError):
        analyze_pair([1, 2, 3], bad, .1)


@pytest.mark.parametrize("bad", [-.1, [-.1, 0, 0], float("nan"), float("inf"),
                                  [], [1, 2], [[1, 2, 3]], "bad", None])
def test_malformed_or_negative_box_fails(bad):
    with pytest.raises(ValueError):
        analyze_pair([1, 2, 3], [1, 2, 3], bad)


@pytest.mark.parametrize("key,value", [("total_eV", 0), ("total_eV", float("inf")),
                                       ("tolerance_eV", 0), ("tolerance_eV", 1e-11),
                                       ("tolerance_eV", float("nan"))])
def test_invalid_scalar_options_fail(key, value):
    with pytest.raises(ValueError):
        analyze_pair([1, 2, 3], [1, 2, 3], .1, **{key: value})


def test_cli_roundtrip(capsys):
    assert main(["--left", "2", "3", "4", "--right", "1", "2", "4.5",
                 "--half-width", "0"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["delta_eta_range_V"] == [.5, .5]


def test_cli_invalid_box_length(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--left", "1", "2", "3", "--right", "1", "2", "3",
              "--half-width", ".1", ".2"])
    assert exc.value.code == 2
    assert "half_width_eV" in capsys.readouterr().err


def test_identical_ladders_with_nonzero_box_never_disagree_strictly():
    result = analyze_pair([1.96, 4.0, 4.46], [1.96, 4.0, 4.46], .2)
    assert not result["strict_disagreement_possible"]
    assert all(a == b for a, b in result["strict_pairs"])
    assert result["delta_eta_range_V"] == pytest.approx([0., 0.])
    # Tied boundaries can have different labels without a physical disagreement.
    assert [1, 2] in result["closed_pairs"]


def test_exact_first_switch_boundary_is_tie_not_strict(adopted_cell_pair):
    left, right = adopted_cell_pair
    sr = che_steps(right)
    radius = (sr[0] - sr[1]) / 3
    boundary = analyze_pair(left, right, radius)
    assert [1, 2] in boundary["closed_pairs"]
    assert not boundary["strict_disagreement_possible"]
    beyond = analyze_pair(left, right, radius + 1e-5)
    assert beyond["strict_disagreement_possible"]
