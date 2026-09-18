"""A complete rational partition of the delta interval; no floating-point gates."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations

from .source import ARTICLE_NAMES, Row

LOW, HIGH = Q(0), Q("0.10")
TOTAL, EQUILIBRIUM = Q("4.92"), Q("1.23")
ETA_CUT, MARGIN_CUT = Q("0.60"), Q("0.050")


@dataclass(frozen=True)
class Affine:
    intercept: Q
    slope: Q = Q(0)

    def __call__(self, delta: Q) -> Q:
        return self.intercept + self.slope * delta

    def __sub__(self, other: "Affine") -> "Affine":
        return Affine(self.intercept - other.intercept, self.slope - other.slope)

    def root(self, value: Q = Q(0)) -> Q | None:
        return (value - self.intercept) / self.slope if self.slope else None


def expressions(row: Row) -> tuple[tuple[Affine, ...], tuple[Affine, Affine]]:
    oh, oxygen, ooh, _ = row.energies
    g1, g2, g3 = oh + Q("0.35"), oxygen + Q("0.05"), ooh + Q("0.35")
    steps = (Affine(g1), Affine(g2 - g1), Affine(g3 - g2, Q(1)), Affine(TOTAL - g3, Q(-1)))
    c = g3 - g1
    # These are the two possible minimal maximum steps at fixed c, before subtracting 1.23 V.
    floors = (Affine(c / 2, Q(1, 2)), Affine((TOTAL - c) / 2, Q(-1, 2)))
    return steps, floors


def classify_count(count: int) -> str:
    if count >= 10:
        return "HELD"
    if count <= 3:
        return "FALSIFIED"
    return "SCORED — MIDDLE BAND / NOT MET"


def row_at(row: Row, delta: Q) -> dict:
    steps, floors = expressions(row)
    values, fvalues = tuple(s(delta) for s in steps), tuple(f(delta) for f in floors)
    maximum, fmaximum = max(values), max(fvalues)
    eta, floor, margin = maximum - EQUILIBRIUM, fmaximum - EQUILIBRIUM, maximum - fmaximum
    if margin < 0:
        raise ArithmeticError(f"negative own-scaling excess at {row.row_id}")
    return dict(row_id=row.row_id, article_id=row.article_id, structure_token=row.structure_token,
                steps=values, eta=eta, floor=floor, margin=margin,
                active_steps=tuple(i + 1 for i, v in enumerate(values) if v == maximum),
                active_floor_branches=tuple(i for i, v in enumerate(fvalues) if v == fmaximum),
                eta_below=eta < ETA_CUT, margin_within=margin <= MARGIN_CUT,
                selected=eta < ETA_CUT and margin <= MARGIN_CUT, negative_dg4=values[3] < 0)


def partition_events(rows: list[Row], low: Q = LOW, high: Q = HIGH) -> dict[Q, list[dict]]:
    """Every active max-branch crossing and predicate root, including endpoint roots.

    Identical affine branches remain tied on their whole interval and need no root.
    Inactive pair crossings do not partition the result. All gating arithmetic is exact.
    """
    if low >= high:
        raise ValueError("delta interval must have positive width")
    events: dict[Q, list[dict]] = {low: [{"kind": "interval_start"}], high: [{"kind": "interval_end"}]}
    for row in rows:
        steps, floors = expressions(row)

        def add(root, kind, *, active_steps=(), active_floors=()):
            if root is None or not low <= root <= high:
                return
            sv, fv = [s(root) for s in steps], [f(root) for f in floors]
            if any(sv[i] != max(sv) for i in active_steps):
                return
            if any(fv[i] != max(fv) for i in active_floors):
                return
            rec = {"row_id": row.row_id, "kind": kind}
            if active_steps:
                rec["steps"] = [i + 1 for i in active_steps]
            if active_floors:
                rec["floor_branches"] = list(active_floors)
            events.setdefault(root, []).append(rec)

        for i, j in combinations(range(4), 2):
            add((steps[i] - steps[j]).root(), "CHE_active_step_crossing", active_steps=(i, j))
        add((floors[0] - floors[1]).root(), "scaling_floor_branch_crossing", active_floors=(0, 1))
        for i, step in enumerate(steps):
            add(step.root(ETA_CUT + EQUILIBRIUM), "eta_equals_0.60", active_steps=(i,))
            for j, floor in enumerate(floors):
                add((step - floor).root(MARGIN_CUT), "margin_equals_0.050",
                    active_steps=(i,), active_floors=(j,))
        add(steps[3].root(), "dg4_equals_zero")
    return dict(sorted(events.items()))


def aggregate(rows: list[dict]) -> dict:
    selected = [r["row_id"] for r in rows if r["selected"]]
    article_rows = defaultdict(list)
    for row in rows:
        article_rows[row["article_id"]].append(row)
    per_article = {}
    for article, rr in sorted(article_rows.items()):
        yes = [r["row_id"] for r in rr if r["selected"]]
        per_article[str(article)] = dict(article=ARTICLE_NAMES.get(article, str(article)),
                                       count=len(yes), denominator=len(rr), rate=Q(len(yes), len(rr)),
                                       selected_row_ids=yes)
    count = len(selected)
    return dict(count=count, denominator=len(rows), rate=Q(count, len(rows)),
                verdict=classify_count(count), selected_row_ids=selected, per_article=per_article,
                negative_dg4_row_ids=[r["row_id"] for r in rows if r["negative_dg4"]])


def analyze(rows: list[Row], low: Q = LOW, high: Q = HIGH) -> dict:
    if not rows or len({r.row_id for r in rows}) != len(rows):
        raise ValueError("nonempty population with unique source row IDs required")
    events = partition_events(rows, low, high)
    points = list(events)
    cells = []
    for i, point in enumerate(points):
        sample = [row_at(row, point) for row in rows]
        cells.append(dict(kind="point", delta=point, left=point, right=point,
                          events=events[point], aggregate=aggregate(sample), rows=sample))
        if i + 1 < len(points):
            right = points[i + 1]
            mid = (point + right) / 2
            sample = [row_at(row, mid) for row in rows]
            cells.append(dict(kind="open_interval", delta=mid, left=point, right=right,
                              aggregate=aggregate(sample), rows=sample))
    counts = [cell["aggregate"]["count"] for cell in cells]
    memberships = {tuple(cell["aggregate"]["selected_row_ids"]) for cell in cells}
    verdicts = sorted({cell["aggregate"]["verdict"] for cell in cells})
    negative_sets = {tuple(cell["aggregate"]["negative_dg4_row_ids"]) for cell in cells}
    equations = {}
    for row in rows:
        steps, floors = expressions(row)
        equations[row.row_id] = dict(
            CHE_steps=[dict(intercept=s.intercept, slope=s.slope) for s in steps],
            floor_maximum_step_branches=[dict(intercept=f.intercept, slope=f.slope) for f in floors],
            eta="max(CHE_steps) - 1.23", floor="max(floor_maximum_step_branches) - 1.23",
            margin="max(CHE_steps) - max(floor_maximum_step_branches)")
    return dict(delta_interval=[low, high], breakpoints=points, cells=cells, row_equations=equations,
                invariance=dict(count_invariant=len(set(counts)) == 1, count_min=min(counts), count_max=max(counts),
                                membership_invariant=len(memberships) == 1,
                                verdict_invariant=len(verdicts) == 1, curve_verdicts=verdicts,
                                negative_dg4_membership_invariant=len(negative_sets) == 1),
                arithmetic="exact rational source decimals; no numerical threshold tolerance",
                floor_identity="max(c, 4.92 - c)/2 - 1.23 = abs(c - 2.46)/2",
                scope="external-corpus-arithmetic-reconstruction-2026-09-16; curve only, not electrode performance")


def serializable(value):
    """Fractions are preserved exactly; floating-point values are display-only."""
    if isinstance(value, Q):
        return {"exact": str(value), "display": float(value)}
    if isinstance(value, dict):
        return {str(k): serializable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serializable(v) for v in value]
    return value
