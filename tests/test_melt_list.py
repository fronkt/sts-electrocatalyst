"""Selection-logic tests for the frozen melt list.

Synthetic rows only — the point is that the list spans the activity/stability tension
rather than collapsing it, and that a desorbed or unscored candidate can never reach a
melt slot.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scripts.melt_list import pareto_front, select  # noqa: E402


def row(formula, eta, soluble, **kw):
    return dict(formula=formula, eta=eta, soluble_at_operating=soluble,
                elements=["Fe", "Ni"], fractions=[0.5, 0.5], **kw)


def test_pareto_front_drops_dominated_candidates():
    rows = [row("A", 0.5, 0.30), row("B", 0.9, 0.60), row("C", 0.4, 0.20)]
    # C beats both A and B on activity AND stability
    assert [r["formula"] for r in pareto_front(rows)] == ["C"]


def test_pareto_front_keeps_a_genuine_tradeoff():
    rows = [row("active", 0.4, 0.70), row("stable", 0.9, 0.20)]
    assert {r["formula"] for r in pareto_front(rows)} == {"active", "stable"}


def test_selection_spans_both_ends():
    rows = [row("active", 0.40, 0.70), row("mid", 0.60, 0.45),
            row("stable", 0.90, 0.20), row("bad", 1.80, 0.90)]
    picks = dict((role, r["formula"]) for role, r in select(rows))
    assert picks["activity end"] == "active"
    assert picks["stability end"] == "stable"
    assert picks["poor anchor"] == "bad"


def test_no_duplicate_composition_across_roles():
    """One candidate can be both ends of a degenerate front; it must not eat two slots."""
    rows = [row("only", 0.5, 0.3), row("worse", 1.2, 0.8)]
    formulas = [r["formula"] for _, r in select(rows)]
    assert len(formulas) == len(set(formulas))


def test_desorbed_candidates_never_reach_a_melt_slot():
    """A composition whose winning state never adsorbed has no meaningful eta —
    exactly the defect that put four wrong structures into the DFT tier."""
    rows = [row("ghost", 0.10, 0.10, desorbed=["OOH"]), row("real", 0.80, 0.50)]
    formulas = [r["formula"] for _, r in select(rows)]
    assert "ghost" not in formulas
    assert "real" in formulas


def test_candidates_without_a_stability_number_are_excluded():
    rows = [row("unscored", 0.10, None), row("scored", 0.80, 0.50)]
    formulas = [r["formula"] for _, r in select(rows)]
    assert formulas == ["scored"]


def test_empty_input_returns_empty_rather_than_raising():
    assert select([]) == []
    assert select([row("ghost", 0.1, 0.1, desorbed=["O"])]) == []
