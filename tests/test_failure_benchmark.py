"""Failure-benchmark adversarial fixtures; synthetic truth is test-only."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hea_oer import failure_benchmark as fb


def case(cid="a", split="heldout", failure=False, converged=True, geometry="intact", spread=0.0):
    return {
        "case_id": cid, "group_id": "group-" + cid, "composition_id": "composition-" + cid,
        "split": split,
        "features": {"converged": converged, "geometry_status": geometry, "ensemble_spread_ev": spread},
        "truth": {"failure": failure, "criterion_id": "test-criterion", "reference_method_id": "test-dft-method",
                  "reference_qc_passed": True, "independently_adjudicated": True,
                  "adjudication_id": "test-adjudication-" + cid, "dft_evidence_ids": ["test-evidence-" + cid],
                  "rationale": "Synthetic test label; no scientific result."},
        "ranking": None,
    }


def manifest(*cases):
    return {"schema": fb.SCHEMA, "protocol_id": "test-protocol", "truth_criterion_id": "test-criterion",
            "ranking_tolerance_ev": 0.01, "cases": list(cases)}


def test_absent_truth_and_features_are_pending_not_success():
    row = case()
    row["truth"] = None
    row["features"]["ensemble_spread_ev"] = None
    report = fb.evaluate(manifest(row))
    assert report["status"] == "PENDING"
    assert report["splits"]["heldout"]["methods"] == dict.fromkeys(fb.METHODS)
    assert report["splits"]["heldout"]["pending"] == [
        {"case_id": "a", "missing_truth": True, "missing_features": ["ensemble_spread_ev"]}]
    assert report["scores"][0]["combined"] is None
    assert report["scores"][0]["convergence_only"] == 0
    assert fb.evaluate(manifest())["status"] == "PENDING"


def test_truth_cannot_leak_into_scores():
    row = case(failure=True, converged=False, geometry="ambiguous", spread=0.02)
    first = fb.evaluate(manifest(row))["scores"]
    row["truth"]["failure"] = False
    row["truth"]["rationale"] = "A completely different adjudication"
    assert fb.evaluate(manifest(row))["scores"] == first
    assert first[0]["combined"] == 1
    row["features"]["dft_force_error"] = 0.2
    with pytest.raises(ValueError, match="expected exactly"):
        fb.evaluate(manifest(row))


def test_confusion_matrix_known_answers_and_undefined_denominators():
    rows = [case("tp", failure=True, converged=False), case("fp", converged=False),
            case("fn", failure=True), case("tn")]
    report = fb.evaluate(manifest(*rows))["splits"]["heldout"]
    cm = report["methods"]["convergence_only"]["confusion"]
    assert cm == {"tp": 1, "fp": 1, "tn": 1, "fn": 1, "precision": 0.5, "recall": 0.5, "specificity": 0.5}
    assert report["methods"]["geometry_only"]["confusion"]["precision"] is None
    cm = fb.evaluate(manifest(case()))["splits"]["heldout"]["methods"]["combined"]["confusion"]
    assert cm["recall"] is None and cm["specificity"] == 1


def test_all_methods_use_shared_cohort_missing_ensemble_not_silently_zero():
    incomplete = case("missing", failure=True)
    incomplete["features"]["ensemble_spread_ev"] = None
    report = fb.evaluate(manifest(case("complete"), incomplete))
    heldout = report["splits"]["heldout"]
    assert report["status"] == "PARTIAL"
    assert heldout["n_truth"] == 2 and heldout["n_evaluable"] == 1
    assert heldout["evaluable_case_ids"] == ["complete"]
    for method in heldout["methods"].values():
        assert method["confusion"]["tn"] == 1
        assert method["selective_risk_coverage"][-1]["retained"] == 1


def test_tied_scores_never_split_even_when_case_order_favors_labels():
    rows = [case("bad", failure=True), case("good"), case("high", converged=False)]
    one = fb.evaluate(manifest(*rows))["splits"]["heldout"]["methods"]["combined"]["selective_risk_coverage"]
    two = fb.evaluate(manifest(*reversed(rows)))["splits"]["heldout"]["methods"]["combined"]["selective_risk_coverage"]
    assert one == two
    assert [point["retained"] for point in one] == [0, 2, 3]
    assert one[1]["risk"] == 0.5 and one[1]["coverage"] == 2 / 3
    assert one[0]["risk"] is None


def test_audit_discovery_cohabit_but_metrics_never_pool():
    discovery = case("d", split="discovery", failure=True)
    audit = case("a", split="audit", converged=False)
    audit["composition_id"] = discovery["composition_id"]
    audit["group_id"] = discovery["group_id"]
    report = fb.evaluate(manifest(discovery, audit, case("h")))
    assert report["status"] == "EVALUATED"
    assert report["splits"]["audit"]["methods"]["combined"]["confusion"]["fp"] == 1
    assert report["splits"]["discovery"]["methods"]["combined"]["confusion"]["fn"] == 1
    assert report["splits"]["heldout"]["methods"]["combined"]["confusion"]["tn"] == 1
    same_composition = case("h2")
    same_composition["composition_id"] = "composition-h"
    same_composition["group_id"] = "group-h"
    heldout = fb.evaluate(manifest(case("h"), same_composition))["splits"]["heldout"]
    assert heldout["n_cases"] == 2 and heldout["n_compositions"] == 1
    assert heldout["n_evaluable_compositions"] == heldout["n_groups"] == heldout["n_evaluable_groups"] == 1
    assert fb.evaluate(manifest(audit))["status"] == "PENDING"


@pytest.mark.parametrize("key", ["composition_id", "group_id"])
@pytest.mark.parametrize("other_split", ["discovery", "audit"])
def test_split_leakage_is_rejected_even_for_unlabeled_cases(key, other_split):
    a, b = case("a"), case("b", split=other_split)
    b[key] = a[key]
    a["truth"] = b["truth"] = None
    with pytest.raises(ValueError, match="split leakage"):
        fb.evaluate(manifest(a, b))


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), True, "0.2", -0.1, 10 ** 1000])
def test_invalid_disagreement_is_refused(bad):
    row = case(spread=bad)
    with pytest.raises(ValueError):
        fb.evaluate(manifest(row))


@pytest.mark.parametrize("field,bad", [("reference_qc_passed", False), ("independently_adjudicated", False),
                                       ("failure", 1), ("dft_evidence_ids", []),
                                       ("criterion_id", "different"), ("rationale", " ")])
def test_inadmissible_truth_is_refused(field, bad):
    row = case()
    row["truth"][field] = bad
    with pytest.raises(ValueError):
        fb.evaluate(manifest(row))


def test_duplicates_and_unknown_keys_are_refused():
    row = case()
    with pytest.raises(ValueError, match="duplicate case_id"):
        fb.evaluate(manifest(row, deepcopy(row)))
    payload = manifest(row)
    payload["accidental_setting"] = 0.2
    with pytest.raises(ValueError, match="expected exactly"):
        fb.evaluate(payload)


def test_scores_are_fixed_diagnostics_and_boundary_is_inclusive():
    row = case(geometry="ambiguous", spread=0.05)
    scores = fb.score_features(row["features"])
    assert scores == {"convergence_only": 0, "geometry_only": 0.5, "model_disagreement": 0.5, "combined": 0.5}
    cm = fb.evaluate(manifest(row))["splits"]["heldout"]["methods"]["combined"]["confusion"]
    assert cm["fp"] == 1
    row["features"]["ensemble_spread_ev"] = 100
    assert fb.score_features(row["features"])["model_disagreement"] == 1


def with_rank(row, screen, dft, comparison="eta-matched-reference"):
    row["ranking"] = {"comparison_set_id": comparison, "screen_value_ev": screen, "dft_value_ev": dft}
    return row


def test_ranking_flips_and_unresolved_ties_are_distinguished():
    a = with_rank(case("a"), 0.0, 0.2)
    b = with_rank(case("b"), 0.2, 0.0)
    stats = fb.evaluate(manifest(a, b))["splits"]["heldout"]["ranking"]
    assert stats["reversed_pairs"] == 1 and stats["resolved_pair_error_rate"] == 1
    b["ranking"]["screen_value_ev"] = 0.005
    stats = fb.evaluate(manifest(a, b))["splits"]["heldout"]["ranking"]
    assert stats["screen_unresolved_pairs"] == 1 and stats["resolved_pair_error_rate"] is None
    assert stats["screen_unresolved_fraction"] == 1
    b["ranking"]["dft_value_ev"] = 0.201
    stats = fb.evaluate(manifest(a, b))["splits"]["heldout"]["ranking"]
    assert stats["dft_unresolved_pairs"] == 1 and stats["dft_resolved_pairs"] == 0


def test_ranking_comparison_groups_reference_models_and_qc():
    a = with_rank(case("a"), 0, 0.2)
    b = with_rank(case("b"), 0.2, 0, comparison="different-observable")
    stats = fb.evaluate(manifest(a, b))["splits"]["heldout"]["ranking"]
    assert stats["incomparable_pairs"] == 1 and stats["resolved_pair_error_rate"] is None
    b["ranking"]["comparison_set_id"] = a["ranking"]["comparison_set_id"]
    b["truth"]["reference_method_id"] = "different-dft"
    with pytest.raises(ValueError, match="mixes DFT reference"):
        fb.evaluate(manifest(a, b))
    b["truth"] = None
    with pytest.raises(ValueError, match="DFT ranking requires"):
        fb.evaluate(manifest(b))


def test_ranking_is_recomputed_on_whole_retained_score_groups():
    a = with_rank(case("a"), 0, 0.2)
    b = with_rank(case("b", converged=False), 0.2, 0)
    points = fb.evaluate(manifest(a, b))["splits"]["heldout"]["methods"]["combined"]["selective_risk_coverage"]
    assert points[1]["ranking"]["dft_resolved_pairs"] == 0
    assert points[2]["ranking"]["reversed_pairs"] == 1


def test_cli_pending_valid_report_no_nan_and_existing_output_preserved(tmp_path):
    source, target = tmp_path / "manifest.json", tmp_path / "report.json"
    row = case()
    row["truth"] = None
    source.write_text(json.dumps(manifest(row)), encoding="utf-8")
    assert fb.main([str(source), "--output", str(target)]) == 3
    report = json.loads(target.read_text(encoding="utf-8"))
    assert report["status"] == "PENDING"
    before = target.read_bytes()
    assert fb.main([str(source), "--output", str(target)]) == 2
    assert target.read_bytes() == before


@pytest.mark.parametrize("text", ['{"schema": "x", "schema": "y"}', '{"value": NaN}', '{"value": Infinity}'])
def test_json_loader_refuses_duplicate_keys_and_nonfinite_constants(tmp_path, text):
    source = tmp_path / "bad.json"
    source.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        fb.load_manifest(source)
