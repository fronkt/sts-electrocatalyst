"""Separate raw-text parser and algebraic verification, without importing the scorer.

The verifier over-partitions at every affine candidate root, including inactive
branches. It uses the absolute-value scaling-floor identity and checks every
point/open interval of that independent partition against the primary partition.
"""
from __future__ import annotations

import hashlib
import re
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

EXPECTED_SHA256 = "88bfcda9a5e70da10d3b2565af7cc09b7377578e4aac4dd5d9a74b42c0bd8bda"


def read_raw(path: Path) -> list[dict]:
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise ValueError("independent verifier: source hash mismatch")
    selected = []
    for i, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        tokens = line.split()
        if 106 <= i <= 644 and len(tokens) == 6 and tokens[0].isdigit() and \
                re.fullmatch("[A-Z][a-z]?O2b?", tokens[1]):
            energy = tuple(F(token) for token in tokens[2:])
            if energy[-1] != F(123, 25):
                raise ValueError("independent verifier: cycle column changed")
            selected.append(dict(row_id="divanis-si2-L" + str(i), article_id=int(tokens[0]),
                                 token=tokens[1], energies=energy))
    if len(selected) != 38:
        raise ValueError("independent verifier: expected 38 raw rows")
    return selected


def evaluate_raw(raw: dict, delta: F) -> dict:
    a, b, c, total = raw["energies"]
    levels = [F(0), a + F(7, 20), b + F(1, 20), c + F(7, 20) + delta, total]
    transitions = [levels[i + 1] - levels[i] for i in range(4)]
    limit = max(transitions)
    eta = limit - total / 4
    span = levels[3] - levels[1]
    floor = abs(span - total / 2) / 2
    margin = eta - floor
    return dict(row_id=raw["row_id"], steps=tuple(transitions), eta=eta, floor=floor, margin=margin,
                active_steps=tuple(i + 1 for i in range(4) if transitions[i] == limit),
                active_floor_branches=(0, 1) if span == total / 2 else (0,) if span > total / 2 else (1,),
                eta_below=eta < F(3, 5), margin_within=margin <= F(1, 20),
                selected=eta < F(3, 5) and margin <= F(1, 20), negative_dg4=transitions[3] < 0)


def candidate_points(raw_rows: list[dict], low: F, high: F) -> list[F]:
    candidates = {low, high}

    def root(a, b):
        if b:
            value = -a / b
            if low <= value <= high:
                candidates.add(value)

    for row in raw_rows:
        a, b, c, total = row["energies"]
        zero = evaluate_raw(row, F(0))["steps"]
        slopes = (F(0), F(0), F(1), F(-1))
        span = c - a
        floor_limits = ((span / 2, F(1, 2)), ((total - span) / 2, F(-1, 2)))
        root(span - total / 2, F(1))
        for i, j in combinations(range(4), 2):
            root(zero[i] - zero[j], slopes[i] - slopes[j])
        for v, slope in zip(zero, slopes):
            root(v - total / 4 - F(3, 5), slope)
            for intercept, fslope in floor_limits:
                root(v - intercept - F(1, 20), slope - fslope)
        root(zero[3], slopes[3])
    return sorted(candidates)


NUMERICAL_KEYS = ("steps", "eta", "floor", "margin")
STATE_KEYS = ("active_steps", "active_floor_branches", "eta_below", "margin_within", "selected", "negative_dg4")


def verify(primary: dict, source_path: Path) -> dict:
    rows = read_raw(source_path)
    source_ids = [row["row_id"] for row in rows]
    cells = primary["cells"]
    comparisons = 0
    for cell in cells:
        if [r["row_id"] for r in cell["rows"]] != source_ids:
            raise AssertionError("primary rows differ from independent raw source selection")
        for original, observed in zip(rows, cell["rows"]):
            check = evaluate_raw(original, cell["delta"])
            for key in NUMERICAL_KEYS + STATE_KEYS:
                if check[key] != observed[key]:
                    raise AssertionError(f"independent arithmetic mismatch: {original['row_id']} {key}")
            comparisons += 1
        selected = [r["row_id"] for r in cell["rows"] if r["selected"]]
        agg = cell["aggregate"]
        if agg["selected_row_ids"] != selected or agg["count"] != len(selected) or agg["denominator"] != 38:
            raise AssertionError("primary aggregation is inconsistent")
        if agg["negative_dg4_row_ids"] != [r["row_id"] for r in cell["rows"] if r["negative_dg4"]]:
            raise AssertionError("primary negative fourth-step enumeration is inconsistent")
        expected_class = "HELD" if len(selected) >= 10 else \
            "FALSIFIED" if len(selected) <= 3 else "SCORED — MIDDLE BAND / NOT MET"
        if agg["verdict"] != expected_class or agg["rate"] != F(len(selected), 38):
            raise AssertionError("primary rate or verdict is inconsistent")
        for article in (1, 7, 9):
            rr = [r for r in rows if r["article_id"] == article]
            ids = [r["row_id"] for r in rr if evaluate_raw(r, cell["delta"])["selected"]]
            reported = agg["per_article"][str(article)]
            if (reported["selected_row_ids"] != ids or reported["count"] != len(ids) or
                    reported["denominator"] != len(rr) or reported["rate"] != F(len(ids), len(rr))):
                raise AssertionError("primary per-article rate differs from raw source computation")

    low, high = primary["delta_interval"]
    independently_partitioned = candidate_points(rows, low, high)
    probes = sorted(set(independently_partitioned) | {
        (left + right) / 2 for left, right in zip(independently_partitioned, independently_partitioned[1:])})
    for delta in probes:
        owners = [cell for cell in cells if (cell["kind"] == "point" and delta == cell["delta"]) or
                  (cell["kind"] == "open_interval" and cell["left"] < delta < cell["right"])]
        if len(owners) != 1:
            raise AssertionError("primary partition has a gap or overlap")
        by_id = {r["row_id"]: r for r in owners[0]["rows"]}
        for raw in rows:
            check = evaluate_raw(raw, delta)
            for key in STATE_KEYS:
                if check[key] != by_id[raw["row_id"]][key]:
                    raise AssertionError(f"missed state boundary: {raw['row_id']} {key} at {delta}")
    return dict(passed=True, source_sha256=EXPECTED_SHA256, raw_rows=len(rows),
                exact_row_sample_comparisons=comparisons,
                independent_candidate_breakpoints=len(independently_partitioned),
                independent_point_and_open_interval_probes=len(probes),
                independent_state_comparisons=len(probes) * len(rows) * len(STATE_KEYS),
                method="separate raw-text parser; absolute-value floor; all candidate roots including inactive branches")
