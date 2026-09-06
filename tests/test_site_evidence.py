"""Analytical site-switching and conservative evidence-quality checks."""
from __future__ import annotations

from copy import deepcopy
import json
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hea_oer.site_evidence import analyze_site_evidence  # noqa: E402


def structure(energy=0.0):
    return dict(energy_eV=energy, converged_by_force=True, max_constrained_force_eV_A=.01,
                fmax_target_eV_A=.05, other_constraint_types=[])


def site(seed, index, oh, oxygen, ooh):
    steps = [oh, oxygen - oh, ooh - oxygen, 4.92 - ooh]
    return dict(seed=seed, site_index=index, dG_OH=oh, dG_O=oxygen, dG_OOH=ooh,
                eta=max(steps) - 1.23, pls=steps.index(max(steps)) + 1,
                relaxed_states={"OH": structure(oh - .35), "O": structure(oxygen - .05),
                                "OOH": structure(ooh - .40)},
                bonds={"OH": 1.9, "O": 1.8, "OOH": 2.0}, desorbed=[])


def example():
    a = site(0, 0, 2.0, 3.0, 4.0)
    b = site(1, 0, 1.0, 3.1, 4.1)
    return dict(formula="example", n_sites=2, n_decorations=2, eta=a["eta"],
                per_site_records=[a, b],
                decoration_records=[dict(seed=seed, relaxed_slab=structure()) for seed in (0, 1)],
                gas_reference_records={"H2O": structure(), "H2": structure()})


def correction(label, oh=0.0, oxygen=0.0, ooh=0.0):
    return dict(label=label, OH=oh, O=oxygen, OOH=ooh)


def test_shared_correction_switches_winning_site_before_selection():
    result = analyze_site_evidence(example(), [correction("switch", oh=.2)])
    assert result["baseline"]["all_observed_sites"]["winners"] == ["seed=0/site=0"]
    changed = result["scenarios"][0]
    assert changed["all_observed_sites"]["winners"] == ["seed=1/site=0"]
    assert changed["all_observed_sites"]["minimum_eta_V"] == pytest.approx(.67)
    assert changed["all_legacy_winners_lost"] is True
    assert changed["legacy_winner_gap_V"] == pytest.approx(.3)
    assert changed["site_values"][0]["eta_V"] == pytest.approx(.97)
    assert result["legacy"]["reported_eta_V"] == pytest.approx(.77)
    assert result["legacy"]["preserved"] is True


def test_all_tied_minima_are_retained():
    result = analyze_site_evidence(example(), [correction("tie", oh=.05)])
    changed = result["scenarios"][0]
    assert changed["all_observed_sites"]["winners"] == ["seed=0/site=0", "seed=1/site=0"]
    assert changed["all_legacy_winners_lost"] is False
    assert changed["legacy_winner_gap_V"] == pytest.approx(0, abs=1e-9)
    assert result["tie_tolerance_V"] == 1e-9


def test_leave_one_decoration_out_recomputes_minimum():
    changed = analyze_site_evidence(example(), [correction("switch", oh=.2)])["scenarios"][0]
    leave = changed["leave_one_decoration_out_all_observed"]
    assert leave["0"]["minimum_eta_V"] == pytest.approx(.67)
    assert leave["1"]["minimum_eta_V"] == pytest.approx(.97)


def test_complete_evidence_has_explicit_secondary_without_performance_claim():
    result = analyze_site_evidence(example(), [])
    secondary = result["baseline"]["eligible_only_secondary"]
    assert result["quality_counts"] == {"eligible": 2, "failed": 0, "unknown": 0}
    assert secondary["result"] == result["baseline"]["all_observed_sites"]
    assert secondary["all_declared_sites_eligible"] is True
    assert result["continuous_certificate"] is False
    assert result["confidence_interval"] is False
    assert result["performance_certification"] is False
    assert result["scenarios"] == []
    assert json.loads(json.dumps(result, allow_nan=False)) == result


def test_failed_original_winner_stays_visible_and_is_not_replaced():
    row = example()
    row["per_site_records"][0]["relaxed_states"]["OH"]["converged_by_force"] = False
    result = analyze_site_evidence(row, [])
    assert result["quality_counts"] == {"eligible": 1, "failed": 1, "unknown": 0}
    baseline = result["baseline"]
    assert baseline["all_observed_sites"]["winners"] == ["seed=0/site=0"]
    assert baseline["eligible_only_secondary"]["result"]["winners"] == ["seed=1/site=0"]
    assert baseline["eligible_only_secondary"]["all_declared_sites_eligible"] is False
    assert result["legacy"]["recovered_winners"] == ["seed=0/site=0"]


def test_missing_gas_quality_is_unknown_not_eligible():
    row = example()
    row.pop("gas_reference_records")
    result = analyze_site_evidence(row, [])
    assert result["quality_counts"] == {"eligible": 0, "failed": 0, "unknown": 2}
    assert result["baseline"]["eligible_only_secondary"]["result"] is None
    assert any("H2O" in reason for reason in result["sites"][0]["unknowns"])


def test_failed_clean_slab_invalidates_only_its_decoration():
    row = example()
    row["decoration_records"][1]["relaxed_slab"]["converged_by_force"] = False
    result = analyze_site_evidence(row, [])
    assert result["sites"][0]["status"] == "eligible"
    assert result["sites"][1]["status"] == "failed"


def test_incomplete_sampling_suppresses_secondary_even_with_one_eligible_site():
    row = example()
    row["per_site_records"].pop()
    result = analyze_site_evidence(row, [])
    assert result["coverage"]["complete"] is False
    assert result["quality_counts"]["eligible"] == 1
    secondary = result["baseline"]["eligible_only_secondary"]
    assert secondary["result"] is None
    assert secondary["leave_one_decoration_out"] is None
    assert result["baseline"]["all_legacy_winners_lost"] is None


def test_missing_decoration_is_unknown_and_incomplete():
    row = example()
    row["decoration_records"].pop()
    result = analyze_site_evidence(row, [])
    assert result["coverage"]["complete"] is False
    assert result["sites"][1]["status"] == "unknown"


def test_site_index_gap_cannot_masquerade_as_complete_coverage():
    row = example()
    row["per_site_records"][1]["site_index"] = 3
    result = analyze_site_evidence(row, [])
    assert not result["coverage"]["complete"]


def test_inputs_are_not_mutated():
    row, corrections = example(), [correction("shift", oh=.2)]
    originals = deepcopy((row, corrections))
    analyze_site_evidence(row, corrections)
    assert (row, corrections) == originals


@pytest.mark.parametrize("change", [
    lambda row: row["per_site_records"].append(deepcopy(row["per_site_records"][0])),
    lambda row: row["decoration_records"].append(deepcopy(row["decoration_records"][0])),
    lambda row: row.update(per_site_records=[]),
    lambda row: row.update(decoration_records=[]),
    lambda row: row.update(n_sites=True),
    lambda row: row.update(n_decorations=0),
    lambda row: row.update(eta=99),
    lambda row: row["per_site_records"][0].update(eta=99),
    lambda row: row["per_site_records"][0].update(pls=4),
    lambda row: row["per_site_records"][0].update(dG_O=math.inf),
    lambda row: row["per_site_records"][0].update(seed=True),
    lambda row: row["per_site_records"][0].update(site_index=-1),
])
def test_structural_or_energy_contradictions_fail_closed(change):
    row = example()
    change(row)
    with pytest.raises(ValueError):
        analyze_site_evidence(row, [])


@pytest.mark.parametrize("corrections", [
    None, "baseline", {"OH": 0}, [None],
    [dict(label="missing", OH=0, O=0)],
    [dict(label="extra", OH=0, O=0, OOH=0, eta=0)],
    [correction("", 0)],
    [correction("same"), correction("same")],
    [correction("bad", oh=True)],
    [correction("bad", oh=math.nan)],
    [correction("bad", oxygen=math.inf)],
])
def test_invalid_scenarios_fail_closed(corrections):
    with pytest.raises(ValueError):
        analyze_site_evidence(example(), corrections)


@pytest.mark.parametrize("change", [
    lambda row: row["per_site_records"][0].update(desorbed=["OOH"]),
    lambda row: row["per_site_records"][0]["bonds"].update(OOH=3.0),
    lambda row: row["per_site_records"][0]["bonds"].update(OOH=math.nan),
    lambda row: row["per_site_records"][0]["relaxed_states"]["OH"].update(max_constrained_force_eV_A=math.nan),
    lambda row: row["per_site_records"][0]["relaxed_states"]["OH"].update(max_constrained_force_eV_A=.05),
    lambda row: row["per_site_records"][0]["relaxed_states"]["OH"].update(converged_by_force="true"),
    lambda row: row["per_site_records"][0]["relaxed_states"]["OH"].update(energy_eV=math.inf),
])
def test_failed_quality_is_reported_without_erasing_nominal_values(change):
    row = example()
    change(row)
    result = analyze_site_evidence(row, [])
    assert result["sites"][0]["status"] == "failed"
    assert result["baseline"]["all_observed_sites"]["minimum_eta_V"] == pytest.approx(.77)
    assert json.loads(json.dumps(result, allow_nan=False)) == result


@pytest.mark.parametrize("change", [
    lambda row: row["per_site_records"][0]["relaxed_states"].pop("OH"),
    lambda row: row["per_site_records"][0]["bonds"].pop("O"),
    lambda row: row["per_site_records"][0].pop("desorbed"),
    lambda row: row["per_site_records"][0]["relaxed_states"]["OH"].pop("energy_eV"),
    lambda row: row["per_site_records"][0]["relaxed_states"]["OH"].update(converged_by_force=None),
])
def test_missing_quality_stays_unknown(change):
    row = example()
    change(row)
    result = analyze_site_evidence(row, [])
    assert result["sites"][0]["status"] == "unknown"
    assert result["sites"][1]["status"] == "eligible"


def test_absolute_energy_contradiction_is_a_quality_failure():
    row = example()
    row["per_site_records"][0]["relaxed_states"]["OH"]["energy_eV"] += .1
    result = analyze_site_evidence(row, [])
    assert result["sites"][0]["status"] == "failed"
    assert any("absolute energies" in message for message in result["sites"][0]["failures"])
    assert result["legacy"]["reported_eta_V"] == pytest.approx(.77)


def test_shared_gas_energy_change_cannot_leave_old_dg_eligible():
    row = example()
    row["gas_reference_records"]["H2O"]["energy_eV"] += .1
    result = analyze_site_evidence(row, [])
    assert result["quality_counts"]["failed"] == 2


def test_raw_energy_alias_contradiction_fails():
    row = example()
    row["per_site_records"][0]["energies_eV"] = {
        "slab": 0, "OH": 99, "O": 2.95, "OOH": 3.6, "H2O": 0, "H2": 0}
    result = analyze_site_evidence(row, [])
    assert result["sites"][0]["status"] == "failed"
    assert any("alias disagrees" in message for message in result["sites"][0]["failures"])


def test_cross_state_binding_change_is_diagnostic_not_automatic_failure():
    row = example()
    first = row["per_site_records"][0]
    first.update(initial_binding_metal_index=0, initial_binding_metal="Cr")
    for state, index, metal in (("OH", 0, "Cr"), ("O", 1, "Ni"), ("OOH", 0, "Cr")):
        first["relaxed_states"][state].update(
            final_binding_metal_index=index, final_binding_metal=metal)
    result = analyze_site_evidence(row, [])
    detail = result["sites"][0]
    assert detail["status"] == "eligible"
    assert detail["binding_identity"]["status"] == "different_final_binding_partners"
    assert detail["binding_identity"]["migrated_states"] == ["O"]


def test_absent_binding_metadata_does_not_invent_same_site_mechanism():
    detail = analyze_site_evidence(example(), [])["sites"][0]
    assert detail["binding_identity"]["status"] == "unknown"
    assert detail["binding_identity"]["cross_state_final_indices_differ"] is None


def test_nonwinning_failed_start_is_counted_without_changing_selected_chain_status():
    row = example()
    first = row["per_site_records"][0]
    first["start_records"] = {}
    for state in ("OH", "O", "OOH"):
        first["start_records"][state] = [dict(structure(), start="selected", bond_length_A=2.0)]
    failed = dict(structure(), start="other", bond_length_A=3.1, converged_by_force=False)
    first["start_records"]["OH"].append(failed)
    detail = analyze_site_evidence(row, [])["sites"][0]
    assert detail["status"] == "eligible"
    assert detail["attempted_starts"]["numerical_status_counts"] == {
        "eligible": 3, "failed": 1, "unknown": 0}
    assert detail["attempted_starts"]["by_state"]["OH"][1]["desorption_distance_flag"] is True
