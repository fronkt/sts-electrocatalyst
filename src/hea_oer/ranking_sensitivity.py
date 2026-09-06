"""Sensitivity of a nominal score ordering to hypothetical bounded errors.

This diagnostic does not calibrate errors or validate catalyst performance. Lower scores
are preferred. In each scenario every candidate may move independently by at most the
same supplied half-width. A pair is strictly ordered throughout that box only when its
nominal gap exceeds twice the half-width. Shared scalar offsets cancel from every gap;
shared adsorption-energy corrections need their own CHE propagation and are not, in
general, scalar offsets of overpotential.

Rank ranges allow arbitrary ordering of exact ties. The deterministic nominal ordering
breaks ties by label only for display; it never converts a tie into a robust edge.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from itertools import combinations
import math
from numbers import Real


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number, not a boolean")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def analyze_ranking(scores: Mapping[str, float], budgets: Sequence[float]) -> dict:
    """Return JSON-compatible partial orders for explicit, hypothetical error budgets.

    budgets contains nonnegative, distinct common per-candidate half-widths in the
    same units as scores. It must not be silently populated from MAE, site spread,
    or an ensemble disagreement. None of those quantities is a calibrated hard bound.

    For a nominally lower score i and higher score j, the strict-order condition is
    budget < (score_j - score_i) / 2. Equality permits a tie, so is unresolved.
    A rank range is [1 + number forced before, n - number forced after]. These are
    possible ordinal positions within the independent box, with arbitrary tie order.
    """
    if not isinstance(scores, Mapping) or not scores:
        raise ValueError("scores must be a nonempty mapping of unique labels to numbers")
    clean: dict[str, float] = {}
    for label, value in scores.items():
        if not isinstance(label, str) or not label.strip():
            raise ValueError("every candidate label must be a nonempty string")
        if label in clean:
            raise ValueError(f"duplicate candidate label: {label!r}")
        clean[label] = _number(value, f"score for {label!r}")
    if not isinstance(budgets, Sequence) or isinstance(budgets, (str, bytes)) or not budgets:
        raise ValueError("budgets must be a nonempty sequence")
    widths = [_number(value, "half-width") for value in budgets]
    if any(width < 0 for width in widths):
        raise ValueError("half-widths must be nonnegative")
    if len(set(widths)) != len(widths):
        raise ValueError("half-widths must be distinct")

    order = sorted(clean, key=lambda label: (clean[label], label))
    pairs = []
    for before, after in combinations(order, 2):
        gap = clean[after] - clean[before]
        if not math.isfinite(gap):
            raise ValueError("score gaps exceed finite floating-point range")
        critical = gap / 2
        if gap > 0 and critical == 0:
            raise ValueError("score gap is too small for a finite positive half-width")
        pairs.append(dict(before=before, after=after, nominal_gap=gap,
                          critical_half_width=critical, nominal_tie=gap == 0))

    ties = []
    for value in sorted(set(clean.values())):
        labels = [label for label in order if clean[label] == value]
        if len(labels) > 1:
            ties.append(labels)

    scenarios = []
    for width in widths:
        intervals = {label: dict(lower=clean[label] - width, upper=clean[label] + width)
                     for label in order}
        if any(not math.isfinite(endpoint) for ends in intervals.values()
               for endpoint in ends.values()):
            raise ValueError("score intervals exceed finite floating-point range")
        # Compare with the reported critical width so equality remains unresolved even
        # when independently rounded interval endpoints would spuriously separate.
        edges = [dict(before=pair["before"], after=pair["after"])
                 for pair in pairs if width < pair["critical_half_width"]]
        ranks = {}
        for label in order:
            forced_before = sum(edge["after"] == label for edge in edges)
            forced_after = sum(edge["before"] == label for edge in edges)
            ranks[label] = dict(best=1 + forced_before, worst=len(order) - forced_after)
        scenarios.append(dict(
            half_width=width,
            intervals=intervals,
            robust_edges=edges,
            robust_pair_count=len(edges),
            full_strict_order=len(edges) == len(pairs),
            rank_ranges=ranks,
            possible_best=[label for label in order if ranks[label]["best"] == 1],
        ))

    return dict(
        schema_version=1,
        analysis="hypothetical_independent_bounded_score_errors",
        calibrated_error_bounds=False,
        performance_certification=False,
        lower_score_is_better=True,
        units="same as input scores",
        error_model="Each candidate may independently shift within +/- half_width.",
        common_offset_note=("A shared scalar score offset cancels from all pair gaps. "
                            "Shared adsorption corrections require CHE propagation."),
        scope_note=("Model-score sensitivity only. MAE, site standard deviation and "
                    "model disagreement are not validated bounds or probabilities. "
                    "This analysis does not establish electrode activity or melt readiness."),
        tie_policy=("Nominal ties sort by label for display. Robust edges are strict; "
                    "rank ranges allow arbitrary ordering of exact ties."),
        scores={label: clean[label] for label in order},
        nominal_order=order,
        nominal_ties=ties,
        pair_count=len(pairs),
        pairs=pairs,
        scenarios=scenarios,
    )
