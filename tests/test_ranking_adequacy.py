"""Evidence-integrity and sampling tests for the R4 ranking audit."""
import copy
import json

import pytest

from scripts.ranking_adequacy import INPUT_NAMES, build_audit, main


def row(label, score, fraction, desorbed=None):
    oh = score + 1.23
    return {"formula": label, "elements": ["Fe", "Ni"], "fractions": [fraction, 1 - fraction],
            "dG_OH": oh, "dG_O": oh + 1, "dG_OOH": oh + 2, "eta": score, "pls": 1,
            "eta_min": score, "eta_mean": score, "eta_max": score, "eta_std": 0.0,
            "n_sites": 2, "n_decorations": 2, "bonds": {"site_metal": "Fe"},
            "desorbed": desorbed or [], "soluble_at_operating": 1 - fraction,
            "phase": "FCC", "single_phase": True}


@pytest.fixture
def inputs():
    rows = [row("A", .4, .1), row("B", .5, .2), row("C", .8, .3, ["OOH"])]
    screen = {"rows": rows, "n_screened": 3, "model": "toy"}
    gated = {"rows": copy.deepcopy(rows[:2])}
    pred = row("Fe100", .6, .4)
    validation = {"pred": {"Fe": pred}, "dft": {"Fe": .7}, "mae_eta": .1,
                  "n": 1, "model": "toy", "gate_met": False}
    melt = {"picks": [{"formula": "A", "eta_pred": .4}, {"formula": "B", "eta_pred": .5}]}
    tier = {"version": "toy", "tier": {"Fe": {"eta": .65, "source": "chain", "dG_OOH": 4.0}}}
    return screen, gated, validation, melt, tier


def test_audit_preserves_inputs_and_separates_error_semantics(inputs):
    before = copy.deepcopy(inputs)
    result = build_audit(*inputs, budgets=[0, .05])
    assert inputs == before
    assert result["counts"] == {"screened": 3, "legacy_retained": 2, "legacy_excluded": 1}
    assert result["reference_audit"]["historical_MAE_V"] == pytest.approx(.1)
    assert result["reference_audit"]["tier_nominal_MAE_V"] == pytest.approx(.05)
    assert result["claims"]["iridium_beating_melt_established"] is False
    assert result["ranking_sensitivity"]["calibrated_error_bounds"] is False
    assert all(not card["per_site_evidence"]["available"] for card in result["candidate_cards"])
    assert len(result["ranking_sensitivity"]["scenarios"]) == 2


@pytest.mark.parametrize("field,value", [("eta_mean", .42), ("eta_std", .01), ("eta_max", .45),
                                         ("fractions", [.15, .85]), ("per_site_records", [])])
def test_refuses_inconsistent_gated_evidence(inputs, field, value):
    inputs[1]["rows"][0][field] = value
    with pytest.raises(ValueError):
        build_audit(*inputs)


def test_refuses_invalid_chemistry_in_gated_roster(inputs):
    inputs[1]["rows"].append(copy.deepcopy(inputs[0]["rows"][2]))
    with pytest.raises(ValueError, match="desorption"):
        build_audit(*inputs)


def test_refuses_silently_dropped_valid_candidate(inputs):
    inputs[1]["rows"].pop()
    with pytest.raises(ValueError, match="roster"):
        build_audit(*inputs)


@pytest.mark.parametrize("field,value", [("eta", float("nan")), ("eta", .7), ("pls", 4),
                                         ("fractions", [.1, .8]), ("n_sites", True)])
def test_refuses_invalid_source_records(inputs, field, value):
    inputs[0]["rows"][0][field] = value
    with pytest.raises(ValueError):
        build_audit(*inputs)


def test_refuses_stale_validation_metrics(inputs):
    inputs[2]["mae_eta"] = .2
    with pytest.raises(ValueError, match="MAE"):
        build_audit(*inputs)


def test_site_records_support_decoration_removal_without_error_calibration(inputs):
    r = inputs[0]["rows"][0]
    a, b = copy.deepcopy(r), row("A", .6, .1)
    a.update(seed=0, site_index=0)
    b.update(seed=1, site_index=0)
    r.update(per_site_records=[a, b], eta_mean=.5, eta_max=.6, eta_std=.1)
    inputs[1]["rows"][0] = copy.deepcopy(r)
    result = build_audit(*inputs)
    evidence = result["candidate_cards"][0]["per_site_evidence"]
    assert evidence["available"] is True
    assert evidence["leave_one_decoration_out"] == {"0": .6, "1": .4}
    assert result["claims"]["hypothetical_budgets_are_calibrated"] is False


def test_refuses_site_count_mismatch(inputs):
    inputs[0]["rows"][0]["per_site_records"] = []
    inputs[1]["rows"][0]["per_site_records"] = []
    with pytest.raises(ValueError, match="site-record count"):
        build_audit(*inputs)


def test_cli_never_overwrites_an_input(inputs, tmp_path):
    for name, payload in zip(INPUT_NAMES, inputs[:4]):
        (tmp_path / name).write_text(json.dumps(payload))
    tier = tmp_path / "tier.json"
    tier.write_text(json.dumps(inputs[4]))
    original = (tmp_path / INPUT_NAMES[0]).read_bytes()
    with pytest.raises(SystemExit) as error:
        main(["--input-dir", str(tmp_path), "--tier", str(tier), "--out", str(tmp_path / INPUT_NAMES[0])])
    assert error.value.code == 2
    assert (tmp_path / INPUT_NAMES[0]).read_bytes() == original


def test_cli_roundtrip_hashes_and_no_absolute_source_paths(inputs, tmp_path):
    for name, payload in zip(INPUT_NAMES, inputs[:4]):
        (tmp_path / name).write_text(json.dumps(payload))
    tier = tmp_path / "tier.json"
    tier.write_text(json.dumps(inputs[4]))
    output = tmp_path / "audit.json"
    assert main(["--input-dir", str(tmp_path), "--tier", str(tier), "--out", str(output)]) == 0
    audit = json.loads(output.read_text())
    assert len(audit["sources"][INPUT_NAMES[0]]["sha256_lf"]) == 64
    assert str(tmp_path) not in output.read_text()
