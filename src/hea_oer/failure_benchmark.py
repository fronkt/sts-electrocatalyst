"""Prospective pre-DFT failure-screen benchmark; no fitting or DFT execution.

Scores are diagnostics, never probabilities. DFT evidence is evaluation-only.
Truth must be independently adjudicated under a named, frozen criterion; this
module checks the recorded attestations, not the underlying scientific judgment.
See docs/research/failure-benchmark-design-2026-09-07.md for the input contract.
"""
from __future__ import annotations

import argparse
from itertools import combinations, groupby
import json
import math
from pathlib import Path
import sys

SCHEMA = "screen-failure-benchmark-v1"
SCORE_RULE = "screen-failure-flags-v1"
METHODS = ("convergence_only", "geometry_only", "model_disagreement", "combined")
SPLITS = ("discovery", "audit", "heldout")
GEOMETRY_SCORE = {"intact": 0.0, "ambiguous": 0.5, "changed": 1.0}
SPREAD_SCALE_EV = 0.10
FLAG_THRESHOLD = 0.5


def _keys(obj, expected, context):
    if not isinstance(obj, dict) or set(obj) != set(expected):
        raise ValueError(f"{context}: expected exactly {sorted(expected)}")


def _text(value, context):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{context}: expected nonempty, trimmed string")


def _number(value, context, nonnegative=False):
    try:
        finite = type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{context}: expected finite number, not boolean")
    if nonnegative and value < 0:
        raise ValueError(f"{context}: expected nonnegative number")


def _features(features, context):
    _keys(features, ("converged", "geometry_status", "ensemble_spread_ev"), context)
    if features["converged"] is not None and type(features["converged"]) is not bool:
        raise ValueError(f"{context}.converged: expected boolean or null")
    geometry = features["geometry_status"]
    if geometry is not None and (not isinstance(geometry, str) or geometry not in GEOMETRY_SCORE):
        raise ValueError(f"{context}.geometry_status: invalid category")
    spread = features["ensemble_spread_ev"]
    if spread is not None:
        _number(spread, f"{context}.ensemble_spread_ev", nonnegative=True)


def validate(payload):
    """Validate the complete manifest, including rows without labels; return it.

    Every composition and group belongs exclusively to development (discovery
    and/or audit) or heldout. This deliberately prevents decoration/frame leakage.
    Unknown feature fields are refused so DFT errors cannot enter a score silently.
    """
    _keys(payload, ("schema", "protocol_id", "truth_criterion_id", "ranking_tolerance_ev", "cases"), "manifest")
    if payload["schema"] != SCHEMA:
        raise ValueError("unsupported schema")
    for key in ("protocol_id", "truth_criterion_id"):
        _text(payload[key], key)
    _number(payload["ranking_tolerance_ev"], "ranking_tolerance_ev", nonnegative=True)
    if not isinstance(payload["cases"], list):
        raise ValueError("cases must be a list")
    seen, memberships, comparison_methods = set(), {}, {}
    for case in payload["cases"]:
        _keys(case, ("case_id", "group_id", "composition_id", "split", "features", "truth", "ranking"), "case")
        for key in ("case_id", "group_id", "composition_id"):
            _text(case[key], key)
        cid = case["case_id"]
        if cid in seen:
            raise ValueError(f"duplicate case_id: {cid}")
        seen.add(cid)
        if case["split"] not in SPLITS:
            raise ValueError(f"{cid}: invalid split")
        for key in ("group_id", "composition_id"):
            memberships.setdefault((key, case[key]), set()).add(case["split"])
        _features(case["features"], cid + ".features")
        truth = case["truth"]
        if truth is not None:
            _keys(truth, ("failure", "criterion_id", "reference_method_id", "reference_qc_passed",
                          "independently_adjudicated", "adjudication_id", "dft_evidence_ids", "rationale"), cid + ".truth")
            if type(truth["failure"]) is not bool:
                raise ValueError(f"{cid}: truth.failure must be boolean")
            for key in ("reference_qc_passed", "independently_adjudicated"):
                if truth[key] is not True:
                    raise ValueError(f"{cid}: completed truth requires {key}=true; otherwise use null")
            for key in ("criterion_id", "reference_method_id", "adjudication_id", "rationale"):
                _text(truth[key], cid + ".truth." + key)
            if truth["criterion_id"] != payload["truth_criterion_id"]:
                raise ValueError(f"{cid}: truth criterion differs from manifest")
            evidence = truth["dft_evidence_ids"]
            if not isinstance(evidence, list) or not evidence:
                raise ValueError(f"{cid}: independent DFT evidence is required")
            for item in evidence:
                _text(item, cid + ".dft_evidence_ids")
            if len(evidence) != len(set(evidence)):
                raise ValueError(f"{cid}: duplicate DFT evidence id")
        ranking = case["ranking"]
        if ranking is not None:
            _keys(ranking, ("comparison_set_id", "screen_value_ev", "dft_value_ev"), cid + ".ranking")
            _text(ranking["comparison_set_id"], cid + ".comparison_set_id")
            _number(ranking["screen_value_ev"], cid + ".screen_value_ev")
            if ranking["dft_value_ev"] is not None:
                _number(ranking["dft_value_ev"], cid + ".dft_value_ev")
                if truth is None:
                    raise ValueError(f"{cid}: DFT ranking requires independently adjudicated, QC-passed truth")
                key = (case["split"], ranking["comparison_set_id"])
                comparison_methods.setdefault(key, set()).add(truth["reference_method_id"])
    for (kind, value), splits in memberships.items():
        if "heldout" in splits and len(splits) > 1:
            raise ValueError(f"split leakage: {kind}={value} spans {sorted(splits)}")
    if any(len(methods) > 1 for methods in comparison_methods.values()):
        raise ValueError("comparison_set_id mixes DFT reference methods")
    return payload


def score_features(features):
    """Return uncalibrated diagnostic scores from pre-DFT fields only.

    A missing field remains null. Combined is null unless all three are known;
    no missing model result is interpreted as zero disagreement.
    """
    _features(features, "features")
    converged, geometry, spread = (features[k] for k in ("converged", "geometry_status", "ensemble_spread_ev"))
    scores = {
        "convergence_only": None if converged is None else float(not converged),
        "geometry_only": None if geometry is None else GEOMETRY_SCORE[geometry],
        "model_disagreement": None if spread is None else min(1.0, spread / SPREAD_SCALE_EV),
    }
    values = list(scores.values())
    scores["combined"] = None if None in values else max(values)
    return scores


def _ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def _confusion(rows, method):
    counts = dict(tp=0, fp=0, tn=0, fn=0)
    for case, scores in rows:
        flag, failure = scores[method] >= FLAG_THRESHOLD, case["truth"]["failure"]
        counts[("t" if flag == failure else "f") + ("p" if flag else "n")] += 1
    return {**counts, "precision": _ratio(counts["tp"], counts["tp"] + counts["fp"]),
            "recall": _ratio(counts["tp"], counts["tp"] + counts["fn"]),
            "specificity": _ratio(counts["tn"], counts["tn"] + counts["fp"])}


def _ranking(cases, tolerance):
    eligible = [c for c in cases if c["ranking"] is not None and c["ranking"]["dft_value_ev"] is not None]
    counts = dict(concordant_pairs=0, reversed_pairs=0, screen_unresolved_pairs=0,
                  dft_unresolved_pairs=0, incomparable_pairs=0)
    for left, right in combinations(eligible, 2):
        a, b = left["ranking"], right["ranking"]
        if a["comparison_set_id"] != b["comparison_set_id"]:
            counts["incomparable_pairs"] += 1
            continue
        dft = a["dft_value_ev"] - b["dft_value_ev"]
        screen = a["screen_value_ev"] - b["screen_value_ev"]
        if abs(dft) <= tolerance:
            key = "dft_unresolved_pairs"
        elif abs(screen) <= tolerance:
            key = "screen_unresolved_pairs"
        elif (screen > 0) == (dft > 0):
            key = "concordant_pairs"
        else:
            key = "reversed_pairs"
        counts[key] += 1
    resolved = counts["concordant_pairs"] + counts["reversed_pairs"]
    comparable = resolved + counts["screen_unresolved_pairs"]
    return {"n_ranked_cases": len(eligible), **counts, "dft_resolved_pairs": comparable,
            "resolved_pair_error_rate": _ratio(counts["reversed_pairs"], resolved),
            "screen_unresolved_fraction": _ratio(counts["screen_unresolved_pairs"], comparable)}


def _selective(rows, method, tolerance):
    """Retain low-risk cases only at complete tied-score group boundaries."""
    points = [{"max_retained_score": None, "retained": 0, "coverage": 0.0,
               "failures": 0, "risk": None, "ranking": _ranking([], tolerance)}]
    retained = []
    ordered = sorted(rows, key=lambda row: (row[1][method], row[0]["case_id"]))
    for score, tied in groupby(ordered, key=lambda row: row[1][method]):
        retained.extend(case for case, _ in tied)
        failures = sum(case["truth"]["failure"] for case in retained)
        points.append({"max_retained_score": score, "retained": len(retained),
                       "coverage": len(retained) / len(rows), "failures": failures,
                       "risk": failures / len(retained), "ranking": _ranking(retained, tolerance)})
    return points


def evaluate(payload):
    """Evaluate each split separately on a shared complete-case cohort.

    PENDING means there are no evaluable heldout labels. PARTIAL explicitly
    exposes missing features/truth; EVALUATED is descriptive, not validation of
    sample size, calibration, scientific labels, or physical surface relevance.
    """
    validate(payload)
    scored = [(case, score_features(case["features"])) for case in payload["cases"]]
    splits = {}
    for split in SPLITS:
        rows = [(case, scores) for case, scores in scored if case["split"] == split]
        evaluable = [(case, scores) for case, scores in rows
                     if case["truth"] is not None and scores["combined"] is not None]
        pending = [{"case_id": case["case_id"], "missing_truth": case["truth"] is None,
                    "missing_features": [key for key, value in case["features"].items() if value is None]}
                   for case, scores in rows if case["truth"] is None or scores["combined"] is None]
        methods = {}
        for method in METHODS:
            methods[method] = None if not evaluable else {
                "threshold": FLAG_THRESHOLD, "confusion": _confusion(evaluable, method),
                "selective_risk_coverage": _selective(evaluable, method, payload["ranking_tolerance_ev"]),
                "accepted_at_threshold": sum(scores[method] < FLAG_THRESHOLD for _, scores in evaluable),
            }
        splits[split] = {
            "status": "EMPTY" if not rows else "PENDING" if not evaluable else "PARTIAL" if pending else "EVALUATED",
            "n_cases": len(rows),
            "n_groups": len({case["group_id"] for case, _ in rows}),
            "n_compositions": len({case["composition_id"] for case, _ in rows}),
            "n_evaluable_groups": len({case["group_id"] for case, _ in evaluable}),
            "n_evaluable_compositions": len({case["composition_id"] for case, _ in evaluable}),
            "n_truth": sum(case["truth"] is not None for case, _ in rows),
            "n_evaluable": len(evaluable), "evaluable_case_ids": [case["case_id"] for case, _ in evaluable],
            "pending": pending, "methods": methods,
            "ranking": None if not evaluable else _ranking([case for case, _ in evaluable], payload["ranking_tolerance_ev"]),
        }
    status = "PENDING" if not splits["heldout"]["n_evaluable"] else (
        "PARTIAL" if any(s["pending"] for s in splits.values()) else "EVALUATED")
    return {
        "schema": SCHEMA + "-report", "status": status, "protocol_id": payload["protocol_id"],
        "truth_criterion_id": payload["truth_criterion_id"], "score_rule_id": SCORE_RULE,
        "score_parameters": {"ensemble_spread_scale_ev": SPREAD_SCALE_EV, "flag_threshold": FLAG_THRESHOLD,
                             "geometry_scores": GEOMETRY_SCORE, "combined_rule": "maximum"},
        "ranking_tolerance_ev": payload["ranking_tolerance_ev"],
        "interpretation": "Uncalibrated prespecified diagnostics; no DFT-cost savings measured. "
                          "All method comparisons use the same complete-feature, adjudicated-truth cohort within each split.",
        "scores": [{"case_id": case["case_id"], "split": case["split"], **scores} for case, scores in scored],
        "splits": splits,
    }


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def _invalid_constant(value):
    raise ValueError(f"nonfinite JSON constant: {value}")


def load_manifest(path):
    """Read strict JSON, refusing duplicate keys and nonfinite constants."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object,
                         parse_constant=_invalid_constant)
    return validate(payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, help="new output path; existing files are refused")
    args = parser.parse_args(argv)
    try:
        report = evaluate(load_manifest(args.manifest))
        rendered = json.dumps(report, indent=2, allow_nan=False) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(rendered)
        else:
            print(rendered, end="")
    except (OSError, ValueError) as exc:
        print(f"failure benchmark: {exc}", file=sys.stderr)
        return 2
    return 0 if report["status"] == "EVALUATED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
