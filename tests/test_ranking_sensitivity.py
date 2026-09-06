"""Analytical checks of hypothetical score-error sensitivity; no material validation."""
from __future__ import annotations

from itertools import product
import json
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hea_oer.ranking_sensitivity import analyze_ranking  # noqa: E402


def edge_set(scenario):
    return {(edge["before"], edge["after"]) for edge in scenario["robust_edges"]}


def test_zero_budget_recovers_distinct_order_without_calibrating_it():
    result = analyze_ranking({"C": 2, "A": 0, "B": 1}, [0])
    scenario = result["scenarios"][0]
    assert result["nominal_order"] == ["A", "B", "C"]
    assert scenario["full_strict_order"]
    assert scenario["rank_ranges"] == {
        "A": {"best": 1, "worst": 1},
        "B": {"best": 2, "worst": 2},
        "C": {"best": 3, "worst": 3},
    }
    assert scenario["possible_best"] == ["A"]
    assert result["calibrated_error_bounds"] is False
    assert result["performance_certification"] is False


def test_strict_boundary_allows_a_tie_and_next_float_can_reverse():
    scores = {"A": 0.1, "B": 0.3}
    critical = analyze_ranking(scores, [0])["pairs"][0]["critical_half_width"]
    widths = [math.nextafter(critical, 0), critical, math.nextafter(critical, math.inf)]
    before, boundary, after = analyze_ranking(scores, widths)["scenarios"]
    assert before["robust_pair_count"] == 1
    assert boundary["robust_pair_count"] == after["robust_pair_count"] == 0
    assert boundary["possible_best"] == ["A", "B"]
    assert boundary["rank_ranges"] == {
        "A": {"best": 1, "worst": 2}, "B": {"best": 1, "worst": 2},
    }


def test_nominal_ties_are_not_ordered_by_display_labels():
    result = analyze_ranking({"Z": 1, "A": 1, "C": 2}, [0])
    assert result["nominal_order"] == ["A", "Z", "C"]
    assert result["nominal_ties"] == [["A", "Z"]]
    assert result["pairs"][0]["critical_half_width"] == 0
    scenario = result["scenarios"][0]
    assert edge_set(scenario) == {("A", "C"), ("Z", "C")}
    assert scenario["possible_best"] == ["A", "Z"]
    assert scenario["rank_ranges"]["C"] == {"best": 3, "worst": 3}
    assert not scenario["full_strict_order"]


def test_separated_groups_remain_ordered_when_within_group_ranks_do_not():
    result = analyze_ranking({"A": 0, "B": 0.25, "C": 1, "D": 1.25}, [0.25])
    scenario = result["scenarios"][0]
    assert edge_set(scenario) == {("A", "C"), ("A", "D"), ("B", "C"), ("B", "D")}
    assert scenario["rank_ranges"] == {
        "A": {"best": 1, "worst": 2}, "B": {"best": 1, "worst": 2},
        "C": {"best": 3, "worst": 4}, "D": {"best": 3, "worst": 4},
    }


def test_rank_ranges_match_explicit_small_box_orderings():
    scores = {"A": 0, "B": 0.25, "C": 0.75}
    width = 0.25
    scenario = analyze_ranking(scores, [width])["scenarios"][0]
    observed = {label: set() for label in scores}
    labels = list(scores)
    for shifts in product([-width, 0, width], repeat=len(labels)):
        values = {label: scores[label] + shift for label, shift in zip(labels, shifts)}
        # Both tie orientations suffice for each label's extrema in this example.
        for reverse_ties in [False, True]:
            order = sorted(labels, key=lambda label: (
                values[label], -labels.index(label) if reverse_ties else labels.index(label)))
            for rank, label in enumerate(order, 1):
                observed[label].add(rank)
    assert scenario["rank_ranges"] == {
        label: {"best": min(ranks), "worst": max(ranks)} for label, ranks in observed.items()
    }


def test_shared_scalar_offset_cancels_while_independent_errors_do_not():
    scores = {"A": 0, "B": 0.25, "C": 1}
    base = analyze_ranking(scores, [0, 0.25, 1])
    shifted = analyze_ranking({label: value + 32 for label, value in scores.items()},
                              [0, 0.25, 1])
    assert base["pairs"] == shifted["pairs"]
    for left, right in zip(base["scenarios"], shifted["scenarios"]):
        assert left["robust_edges"] == right["robust_edges"]
        assert left["rank_ranges"] == right["rank_ranges"]
    assert base["scenarios"][0]["robust_pair_count"] == 3
    assert base["scenarios"][-1]["robust_pair_count"] == 0


def test_larger_error_budgets_can_only_remove_robust_edges():
    result = analyze_ranking({"A": -1, "B": -0.9, "C": 0.2, "D": 0.3},
                             [0, 0.01, 0.1, 0.5, 1])
    edges = [edge_set(scenario) for scenario in result["scenarios"]]
    assert all(later <= earlier for earlier, later in zip(edges, edges[1:]))


def test_reordering_inputs_does_not_change_output():
    assert analyze_ranking({"C": 2, "A": 0, "B": 1}, [0, 1]) == analyze_ranking(
        {"B": 1, "C": 2, "A": 0}, [0, 1])


def test_single_candidate_has_only_one_possible_rank():
    result = analyze_ranking({"only": -1}, [0, 3])
    assert result["pair_count"] == 0
    assert result["pairs"] == []
    for scenario in result["scenarios"]:
        assert scenario["rank_ranges"] == {"only": {"best": 1, "worst": 1}}
        assert scenario["possible_best"] == ["only"]


def test_output_is_strict_json_with_explicit_scope():
    result = analyze_ranking({"A": 0, "B": 1}, [0.5])
    assert json.loads(json.dumps(result, allow_nan=False)) == result
    assert result["analysis"] == "hypothetical_independent_bounded_score_errors"
    assert "not validated bounds or probabilities" in result["scope_note"]
    assert "adsorption corrections require CHE" in result["common_offset_note"]


@pytest.mark.parametrize("scores", [
    {}, [], [("A", 1)], {"A": None}, {"A": True}, {"A": "1"},
    {"A": math.nan}, {"A": math.inf}, {"A": -math.inf},
    {"": 1}, {" ": 1}, {1: 1},
])
def test_invalid_scores_fail_closed(scores):
    with pytest.raises(ValueError):
        analyze_ranking(scores, [0])


@pytest.mark.parametrize("budgets", [
    [], "0.1", b"0.1", 0.1, {"width": 0.1},
    [None], [True], ["0.1"], [-0.1],
    [math.nan], [math.inf], [-math.inf], [0, 0], [0, -0.0],
])
def test_invalid_or_duplicate_budgets_fail_closed(budgets):
    with pytest.raises(ValueError):
        analyze_ranking({"A": 1}, budgets)


@pytest.mark.parametrize("scores,budgets", [
    ({"A": -1e308, "B": 1e308}, [0]),
    ({"A": 1e308}, [1e308]),
    ({"A": 0, "B": math.ulp(0.0)}, [0]),
])
def test_unrepresentable_derived_quantities_fail_closed(scores, budgets):
    with pytest.raises(ValueError):
        analyze_ranking(scores, budgets)
