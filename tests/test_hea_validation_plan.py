"""Frozen DFT-label splits, pending denominators, geometry identity, and no replacement."""
import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "dft"))
import hea_validation_plan as hv


@pytest.fixture
def plan():
    return hv.prepare()


def save(path, payload):
    path.write_text(json.dumps(payload, allow_nan=False), encoding="utf-8")


def census_payload(plan, formula, sites):
    manifest = plan["bindings"][formula]["manifest"]
    candidate = manifest["candidates"][0]
    # Tiny retained geometry sufficient to test identity and routing, with appended O/H.
    slab = dict(symbols=["Cr", "O"], positions_A=[[0., 0., 0.], [0., 0., 1.]],
                cell_A=[[10., 0., 0.], [0., 10., 0.], [0., 0., 20.]], pbc=[True]*3,
                fixed_atom_indices=[0], other_constraint_types=[], converged_by_force=False,
                max_constrained_force_eV_A=0.2, energy_eV=-1.)
    site_records = []
    for seed, index in sites:
        states = {}
        for sp, additions in (("OH", ["O", "H"]), ("O", ["O"]), ("OOH", ["O", "O", "H"])):
            state = copy.deepcopy(slab)
            state["symbols"] += additions
            state["positions_A"] += [[0., 0., float(3+i)] for i in range(len(additions))]
            states[sp] = state
        site_records.append(dict(seed=seed, site_index=index, eta=99., bonds={}, relaxed_states=states,
                                 initial_binding_metal_index=0, initial_binding_metal="Cr",
                                 status="retained_with_error", error={"message": "synthetic site failure"}))
    row = dict(candidate, per_site_records=site_records,
               decoration_records=[dict(seed=s, relaxed_slab=copy.deepcopy(slab)) for s in sorted({s for s, _ in sites})])
    records = [dict(candidate_id=candidate["candidate_id"], formula=formula, status="evaluated", row=row)]
    return dict(schema="screen-diagnostic-v1", manifest_id=manifest["manifest_id"], manifest=manifest,
                status="complete", results=records, results_sha256=hv.identity(records))


def test_real_plan_reproducible_and_composition_disjoint(plan):
    assert hv.prepare() == plan
    hv.validate_plan(plan)
    assert plan["counts"]["state_slots"] == 60
    held = [a for a in plan["assignments"] if a["split"] == "heldout_dft_labels"]
    assert len(held) == 4
    assert not set(hv.KNOWN) & {a["formula"] for a in held}
    assert all(s["split"] == "targeted_audit" for s in plan["slots"] if s["arm"] != "energy_blind")
    assert plan["claims"]["calibrated_intervals"] is False
    assert plan["claims"]["historical_screen_held_out"] is False


def test_real_split_covers_all_six_elements_in_both_groups(plan):
    expected = {"Cr", "Mn", "Fe", "Co", "Ni", "Cu"}
    for split in ("discovery", "heldout_dft_labels"):
        assert set(plan["coverage"][split]["element_composition_counts"]) == expected
        assert all(n > 0 for n in plan["coverage"][split]["element_composition_counts"].values())


def test_selection_is_independent_of_energy_input_order_and_element_order(plan):
    candidates = copy.deepcopy(plan["candidates"])
    expected = hv.selection(candidates)
    candidates.reverse()
    for i, c in enumerate(candidates):
        c.update(eta=-1e8*i, results={"best_site": [2, 3]})
        c["elements"].reverse()
        c["fractions"].reverse()
    assert hv.selection(candidates) == expected


def test_missing_census_retains_denominator_and_known_audits(plan, tmp_path):
    result = hv.materialize(plan, tmp_path)
    assert result["counts"] == dict(chain_slots=15, ready_chains=2, state_slots=60,
                                    ready_state_slots=8, pending_state_slots=52, unique_ready_geometries=8)
    assert sum(r["status"] == "pending_result" for r in result["slots"]) == 13
    assert plan == hv.prepare()


def test_materialization_keeps_unconverged_geometries_and_no_site_replacement(plan, tmp_path):
    slot = next(s for s in plan["slots"] if s["split"] == "heldout_dft_labels")
    formula, sel = slot["formula"], slot["selector"]
    payload = census_payload(plan, formula, [(sel["seed"], sel["site_index"])])
    path = tmp_path / plan["bindings"][formula]["result_filename"]
    save(path, payload)
    snapshot = hv.materialize(plan, tmp_path)
    row = next(r for r in snapshot["slots"] if r["slot_id"] == slot["slot_id"])
    assert row["status"] == "ready"
    assert row["states"]["OOH"]["converged_by_force"] is False
    assert row["initial_binding_metal_index"] == 0
    assert row["initial_binding_metal"] == "Cr"
    assert row["retained_site_status"] == {"status": "retained_with_error", "error": {"message": "synthetic site failure"}}
    assert row["states"]["OOH"]["geometry_sha256"] == hv.identity(row["states"]["OOH"]["geometry"])
    # An attractive substitute elsewhere cannot fill the reserved slot.
    payload = census_payload(plan, formula, [(sel["seed"], (sel["site_index"]+1)%4)])
    payload["results"][0]["row"]["per_site_records"][0]["eta"] = -99.
    payload["results_sha256"] = hv.identity(payload["results"])
    save(path, payload)
    row = next(r for r in hv.materialize(plan, tmp_path)["slots"] if r["slot_id"] == slot["slot_id"])
    assert row["status"] == "pending_unmatched_identity"
    assert all(s["status"] == "pending_geometry" for s in row["states"].values())


def test_historical_winner_requires_unique_fingerprint(plan):
    selector = plan["slots"][-1]["selector"]
    site = dict(seed=selector["seed"], site_index=0, eta=selector["eta_V"],
                bonds=dict(site_metal=selector["site_metal"], **selector["bonds_A"]))
    assert hv._site(dict(per_site_records=[site]), selector)[1] == "matched"
    twin = dict(site, site_index=1)
    assert hv._site(dict(per_site_records=[site, twin]), selector)[1] == "pending_ambiguous_identity"
    site["eta"] += .1
    assert hv._site(dict(per_site_records=[site]), selector)[1] == "pending_unmatched_identity"


def test_plan_hash_and_resealed_selection_tamper_rejected(plan):
    bad = copy.deepcopy(plan)
    bad["assignments"][0]["seed"] = (bad["assignments"][0]["seed"]+1)%3
    with pytest.raises(ValueError, match="identity"):
        hv.validate_plan(bad)
    hv.seal(bad, "plan_id")
    with pytest.raises(ValueError, match="selection"):
        hv.validate_plan(bad)


@pytest.mark.parametrize("mutation,error", [
    ("wrong_manifest", "manifest mismatch"), ("content", "content hash"),
    ("candidate", "candidate identity"), ("missing", "missing candidates"),
    ("duplicate_site", "duplicate site"), ("singular_cell", "periodic cell")])
def test_bad_results_fail_closed(plan, tmp_path, mutation, error):
    slot = next(s for s in plan["slots"] if s["split"] == "heldout_dft_labels")
    formula, sel = slot["formula"], slot["selector"]
    payload = census_payload(plan, formula, [(sel["seed"], sel["site_index"])])
    if mutation == "wrong_manifest":
        payload["manifest_id"] = "0"*64
    elif mutation == "content":
        payload["results"][0]["row"]["per_site_records"][0]["eta"] = 1.
    elif mutation == "candidate":
        payload["results"][0]["candidate_id"] = "0"*64
    elif mutation == "missing":
        payload["results"] = []
    elif mutation == "duplicate_site":
        sites = payload["results"][0]["row"]["per_site_records"]
        sites.append(copy.deepcopy(sites[0]))
    elif mutation == "singular_cell":
        payload["results"][0]["row"]["per_site_records"][0]["relaxed_states"]["OOH"]["cell_A"] = [[0., 0., 0.]]*3
    if mutation != "content":
        payload["results_sha256"] = hv.identity(payload["results"])
    save(tmp_path / plan["bindings"][formula]["result_filename"], payload)
    with pytest.raises(ValueError, match=error):
        hv.materialize(plan, tmp_path)


def test_missing_geometry_stays_pending_and_error_kept(plan, tmp_path):
    slot = next(s for s in plan["slots"] if s["split"] == "heldout_dft_labels")
    formula, sel = slot["formula"], slot["selector"]
    payload = census_payload(plan, formula, [(sel["seed"], sel["site_index"])])
    payload["results"][0]["row"]["per_site_records"][0]["relaxed_states"].pop("OOH")
    payload["results_sha256"] = hv.identity(payload["results"])
    path = tmp_path / plan["bindings"][formula]["result_filename"]
    save(path, payload)
    row = next(r for r in hv.materialize(plan, tmp_path)["slots"] if r["slot_id"] == slot["slot_id"])
    assert row["status"] == "pending_geometry"
    assert row["states"]["OOH"] == {"status": "pending_geometry"}
    payload["results"][0].update(status="error", error={"message": "failed"})
    payload["status"] = "complete_with_errors"
    payload["results_sha256"] = hv.identity(payload["results"])
    save(path, payload)
    row = next(r for r in hv.materialize(plan, tmp_path)["slots"] if r["slot_id"] == slot["slot_id"])
    assert row["status"] == "candidate_error"


def test_partial_completion_is_pending_not_early_selection(plan, tmp_path):
    slot = plan["slots"][0]
    payload = census_payload(plan, slot["formula"], [(slot["selector"]["seed"], slot["selector"]["site_index"])])
    payload["status"] = "running"
    save(tmp_path / plan["bindings"][slot["formula"]]["result_filename"], payload)
    row = next(r for r in hv.materialize(plan, tmp_path)["slots"] if r["slot_id"] == slot["slot_id"])
    assert row["status"] == "pending_completion"


def test_read_json_duplicate_nonfinite_and_exclusive_outputs(tmp_path):
    path = tmp_path / "bad.json"
    for text in ('{"a": 1, "a": 2}', '{"a": NaN}'):
        path.write_text(text, encoding="utf-8")
        with pytest.raises(ValueError):
            hv.read_json(path)
    with pytest.raises(FileExistsError):
        hv.write_new(path, {})
