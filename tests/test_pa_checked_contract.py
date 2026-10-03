"""Offline P-A-v2 transition and checkpoint contracts; no QE execution."""
import copy
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/dft"))
import pa_checked_contract as contract


SETTINGS = "1" * 64
SOURCE = {"path": "retained/arm.out", "sha256": "a" * 64,
          "line_start": 10, "line_end": 20}
EVALUATED = {"unit": "bohr", "species": ["Cu", "O"],
             "positions": [[0.0, 0.0, 0.0], [0.0, 0.0, 2.0]],
             "cell": [[20.0, 0.0, 0.0], [0.0, 20.0, 0.0], [0.0, 0.0, 20.0]],
             "fixed_flags": [[0, 0, 0], [0, 0, 0]]}
PROPOSAL = {"unit": "bohr", "species": ["Cu", "O"],
            "positions": [[0.0, 0.0, 0.01], [0.0, 0.0, 2.01]],
            "cell": [[20.0, 0.0, 0.0], [0.0, 20.0, 0.0], [0.0, 0.0, 20.0]],
            "fixed_flags": [[0, 0, 0], [0, 0, 0]]}


def scf(status="CONVERGED", energy=-100.0, *, geometry=None, settings=SETTINGS,
        source=None, role="evaluated", proposal=None):
    return {"status": status, "energy_Ry": energy,
            "energy_unit": "Ry", "geometry_unit": "bohr",
            "geometry_role": role, "geometry": copy.deepcopy(EVALUATED if geometry is None else geometry),
            "settings_identity": settings, "source": copy.deepcopy(SOURCE if source is None else source),
            **({"proposal_geometry": copy.deepcopy(proposal or PROPOSAL)} if proposal is not None or status in {"CONVERGED", "STALLED", "FAILED"} else {})}


def optimizer_receipts(saved_bfgs=1, saved_scf=1, first_bfgs=1, first_scf=2):
    saved = {"bfgs_count": saved_bfgs, "scf_count": saved_scf,
             "source": copy.deepcopy(SOURCE)}
    observed = {"first_optimizer_bfgs_count": first_bfgs, "first_scf_count": first_scf,
                "startup_history_reset": False, "restart_fallback": False,
                "checkpoint_source_validated": True, "upf_source_validated": True,
                "settings_source_validated": True, "source": copy.deepcopy(SOURCE),
                "settings_identity": SETTINGS,
                "checkpoint_source": {"path": "retained/checkpoint.xml", "sha256": "b" * 64},
                "upf_source": {"path": "pseudo/metal.UPF", "sha256": "c" * 64},
                "settings_source": {"path": "retained/settings.json", "sha256": "d" * 64}}
    return saved, observed


def checkpoint_pair(tmp_path, *, changed_after=False, wfc=False):
    out = tmp_path / "restart-out"
    out.mkdir()
    (out / "charge-density.dat").write_bytes(b"rho")
    (out / "probe.update").write_bytes(b"sibling optimizer state")
    nested = out / "prefix.save"
    nested.mkdir()
    (nested / "data-file-schema.xml").write_bytes(b"xml")
    wf = None
    if wfc:
        wf = tmp_path / "restart-wfc"
        wf.mkdir()
        (wf / "wfc1.dat").write_bytes(b"wavefunction")
    before = contract.checkpoint_inventory(out, wf)
    if changed_after:
        (out / "prefix.save" / "data-file-schema.xml").write_bytes(b"changed xml")
    after = contract.checkpoint_inventory(out, wf)
    return before, after, out, wf


def scratch_paths(tmp_path, *, restart_wfc=None, fresh_wfc=None):
    return {"restart_outdir": tmp_path / "resume-out",
            "fresh_outdir": tmp_path / "fresh-out",
            "restart_wfcdir": restart_wfc,
            "fresh_wfcdir": fresh_wfc}


def decide(tmp_path, *, warm=None, fresh=None, before=None, after=None,
           paths=None, segment_index=1, reseeds=0, max_segments=4,
           max_reseeds=2, terminal=False, saved=None, resume=None,
           terminal_evidence=None):
    if before is None:
        decision_dirs = sorted(tmp_path.glob("decision-*"))
        inventory_root = tmp_path / ("decision-%d" % len(decision_dirs))
        inventory_root.mkdir()
        before, after, _, _ = checkpoint_pair(inventory_root)
    default_paths = scratch_paths(tmp_path)
    default_paths["restart_outdir"] = before["outdir"]["root"]
    if before["wfcdir"] is not None:
        default_paths["restart_wfcdir"] = before["wfcdir"]["root"]
    return contract.decide_segment(
        warm=scf() if warm is None else warm,
        fresh=scf(energy=-100.0) if fresh is None else fresh,
        checkpoint_before=before, checkpoint_after=after,
        scratch_paths=default_paths if paths is None else paths,
        segment_index=segment_index, reseeds_so_far=reseeds,
        max_segments=max_segments, max_reseeds=max_reseeds,
        terminal=terminal, saved_optimizer=saved, resume_receipt=resume,
        terminal_evidence=terminal_evidence)


def test_accept_requires_observed_consumption_and_uses_proposal(tmp_path):
    saved, observed = optimizer_receipts()
    result = decide(tmp_path, saved=saved, resume=observed)
    assert result["action"] == "ACCEPT"
    assert result["history_disposition"] == "INHERIT_VERIFIED"
    assert result["next_geometry"] == PROPOSAL
    assert result["evaluated_geometry"] == EVALUATED
    assert result["resume_receipt"]["first_optimizer_bfgs_count"] == 1
    assert result["resume_receipt"]["first_scf_count"] == 2
    assert result["status"] == "OFFLINE_CONTRACT_ONLY"
    assert result["production_accepted"] is False
    assert result["real_catalyst_test_pending"] is True


@pytest.mark.parametrize("fresh_energy", [-100.0 - 10.0 / contract.RY_MEV, -99.99])
def test_exact_delta_boundary_and_higher_fresh_state_accept(tmp_path, fresh_energy):
    saved, observed = optimizer_receipts()
    result = decide(tmp_path, fresh=scf(energy=fresh_energy), saved=saved, resume=observed)
    assert result["action"] == "ACCEPT"
    assert result["next_geometry"] == PROPOSAL


def test_strictly_lower_fresh_state_reseeds_at_evaluated_geometry(tmp_path):
    lower = -100.0 - 10.001 / contract.RY_MEV
    result = decide(tmp_path, fresh=scf(energy=lower))
    assert result["action"] == "RESEED"
    assert result["history_disposition"] == "RESET_REQUIRED_BY_ADAPTER"
    assert result["next_geometry"] == EVALUATED
    assert result["proposed_geometry"] == PROPOSAL
    assert result["next_reseeds_so_far"] == 1
    assert result["resume_receipt"] is None


def test_stalled_warm_has_no_energy_and_fresh_reference_reseeds(tmp_path):
    result = decide(tmp_path, warm=scf("STALLED", None))
    assert result["action"] == "RESEED"
    assert result["warm_minus_fresh_meV"] is None
    assert result["next_geometry"] == EVALUATED
    assert result["history_disposition"] == "RESET_REQUIRED_BY_ADAPTER"


def test_failed_warm_holds_and_failed_fresh_never_becomes_a_reference(tmp_path):
    failed_warm = decide(tmp_path, warm=scf("FAILED", None))
    assert failed_warm["action"] == "HOLD"
    assert failed_warm["next_reseeds_so_far"] == 0
    stalled_fresh = decide(tmp_path, fresh=scf("STALLED", None))
    assert stalled_fresh["action"] == "HOLD"
    assert stalled_fresh["next_geometry"] is None


def test_terminal_completion_requires_converged_fresh_reference(tmp_path):
    missing_terminal = decide(tmp_path, terminal=True)
    assert missing_terminal["action"] == "HOLD"
    assert "lacks evaluated energy/force" in missing_terminal["reason"]
    evidence = {"geometry_role": "evaluated", "geometry": copy.deepcopy(EVALUATED),
                "energy_Ry": -100.0, "maximum_force_Ry_bohr": 0.001,
                "force_threshold_Ry_bohr": 0.002, "bfgs_converged": True,
                "source": copy.deepcopy(SOURCE)}
    complete = decide(tmp_path, terminal=True, terminal_evidence=evidence)
    assert complete["action"] == "COMPLETE"
    assert complete["history_disposition"] == "NOT_APPLICABLE_TERMINAL"
    assert complete["next_geometry"] == EVALUATED
    hold = decide(tmp_path, terminal=True, fresh=scf("FAILED", None))
    assert hold["action"] == "HOLD"
    assert hold["proposed_action"] == "HOLD"
    for force in (0.002, 0.003):
        excessive_force = dict(evidence, maximum_force_Ry_bohr=force)
        hold_force = decide(tmp_path, terminal=True, terminal_evidence=excessive_force)
        assert hold_force["action"] == "HOLD"
        assert "strictly below" in hold_force["reason"]


@pytest.mark.parametrize("mutation", [
    lambda warm, fresh: fresh.update(geometry_role="proposed"),
    lambda warm, fresh: fresh["geometry"]["positions"][0].__setitem__(0, 0.0001),
    lambda warm, fresh: fresh.update(settings_identity="2" * 64),
])
def test_energy_geometry_and_settings_correspondence_are_mandatory(tmp_path, mutation):
    warm, fresh = scf(), scf()
    mutation(warm, fresh)
    with pytest.raises(ValueError):
        decide(tmp_path, warm=warm, fresh=fresh)


@pytest.mark.parametrize("field,change", [
    ("cell", lambda cell: cell[0].__setitem__(0, 21.0)),
    ("fixed_flags", lambda flags: flags[0].__setitem__(0, 1)),
])
def test_cell_and_constraints_are_part_of_geometry_identity(tmp_path, field, change):
    warm, fresh = scf(), scf()
    change(fresh["geometry"][field])
    with pytest.raises(ValueError, match="evaluated geometry"):
        decide(tmp_path, warm=warm, fresh=fresh)


@pytest.mark.parametrize("mutation", [
    lambda warm: warm.update(energy_Ry=True),
    lambda warm: warm.update(energy_Ry=float("nan")),
    lambda warm: warm.update(energy_unit="Hartree"),
    lambda warm: warm["source"].update(sha256="bad"),
    lambda warm: warm["source"].update(line_start=0),
    lambda warm: warm["geometry"].update(unit="angstrom"),
    lambda warm: warm["geometry"].pop("cell"),
    lambda warm: warm["geometry"]["fixed_flags"][0].__setitem__(0, True),
    lambda warm: warm["geometry"]["positions"][0].__setitem__(2, float("inf")),
    lambda warm: warm["proposal_geometry"]["species"].reverse(),
    lambda warm: warm.update(settings_identity="not-a-hash"),
])
def test_malformed_numeric_source_unit_and_geometry_evidence_fails(tmp_path, mutation):
    warm = scf()
    mutation(warm)
    with pytest.raises(ValueError):
        decide(tmp_path, warm=warm)


def test_fixed_flag_convention_rejects_motion_of_normalized_fixed_coordinate(tmp_path):
    warm = scf()
    warm["geometry"]["fixed_flags"][0] = [1, 0, 0]
    warm["proposal_geometry"]["fixed_flags"][0] = [1, 0, 0]
    warm["proposal_geometry"]["positions"][0][0] = 0.01
    with pytest.raises(ValueError, match="marked fixed"):
        decide(tmp_path, warm=warm)


@pytest.mark.parametrize("kwargs", [
    {"segment_index": 4, "max_segments": 4},
    {"reseeds": 2, "max_reseeds": 2,
     "fresh": scf(energy=-100.0 - 11.0 / contract.RY_MEV)},
])
def test_caps_hold_without_counter_overshoot(tmp_path, kwargs):
    result = decide(tmp_path, **kwargs)
    assert result["action"] == "HOLD"
    assert result["next_segment_index"] <= result["max_segments"]
    assert result["next_reseeds_so_far"] <= result["max_reseeds"]
    if result["proposed_action"] == "RESEED":
        assert result["history_disposition"] == "RESET_BLOCKED_BY_CAP"


@pytest.mark.parametrize("field,value", [
    ("first_optimizer_bfgs_count", 0),
    ("first_scf_count", 1),
    ("startup_history_reset", True),
    ("restart_fallback", True),
    ("checkpoint_source_validated", False),
    ("upf_source_validated", False),
    ("settings_source_validated", False),
])
def test_bytes_or_counters_alone_cannot_pass_resume_gate(tmp_path, field, value):
    saved, observed = optimizer_receipts()
    observed[field] = value
    with pytest.raises(ValueError):
        decide(tmp_path, saved=saved, resume=observed)


@pytest.mark.parametrize("field", ["checkpoint_source", "upf_source", "settings_source"])
def test_resume_source_validation_needs_pinned_file_identity(tmp_path, field):
    saved, observed = optimizer_receipts()
    observed[field] = {"path": "unchecked", "sha256": "bad"}
    with pytest.raises(ValueError, match="pinned-file"):
        decide(tmp_path, saved=saved, resume=observed)


def test_resume_requires_positive_history_and_one_scf_boundary(tmp_path):
    saved, observed = optimizer_receipts(saved_bfgs=0)
    with pytest.raises(ValueError, match="nonzero"):
        decide(tmp_path, saved=saved, resume=observed)
    saved, observed = optimizer_receipts(first_scf=3)
    with pytest.raises(ValueError, match="next SCF"):
        decide(tmp_path, saved=saved, resume=observed)
    saved, observed = optimizer_receipts(saved_scf=0, first_scf=1)
    with pytest.raises(ValueError, match="nonzero saved and first-call SCF"):
        decide(tmp_path, saved=saved, resume=observed)
    saved, observed = optimizer_receipts(saved_scf=1, first_scf=0)
    with pytest.raises(ValueError, match="nonzero saved and first-call SCF"):
        decide(tmp_path, saved=saved, resume=observed)


def test_normal_terminal_bfgs_cleanup_is_not_startup_reset(tmp_path):
    saved, observed = optimizer_receipts()
    observed["terminal_cleanup_after_first_optimizer_call"] = True
    result = decide(tmp_path, saved=saved, resume=observed)
    assert result["action"] == "ACCEPT"
    assert result["resume_receipt"]["startup_history_reset"] is False


def test_resume_without_actual_receipts_cannot_accept(tmp_path):
    with pytest.raises(ValueError, match="actual saved and observed"):
        decide(tmp_path)


def test_restart_checkpoint_change_during_fresh_check_holds(tmp_path):
    before, after, _, _ = checkpoint_pair(tmp_path, changed_after=True)
    result = decide(tmp_path, before=before, after=after)
    assert result["action"] == "HOLD"
    assert not result["checkpoint_unchanged_during_fresh_check"]


def test_checkpoint_inventory_rejects_incomplete_or_tampered_manifest(tmp_path):
    before, after, _, _ = checkpoint_pair(tmp_path)
    tampered = copy.deepcopy(before)
    tampered["outdir"]["files"].pop()
    with pytest.raises(ValueError, match="digest"):
        contract.checkpoint_unchanged(tampered, after)


def test_checkpoint_comparison_rejects_empty_supplied_tree(tmp_path):
    before, after, _, _ = checkpoint_pair(tmp_path)
    empty = copy.deepcopy(before)
    empty["outdir"]["files"] = []
    body = {"outdir": empty["outdir"], "wfcdir": empty["wfcdir"]}
    empty["sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    with pytest.raises(ValueError, match="malformed checkpoint tree"):
        contract.checkpoint_unchanged(empty, after)


def test_recursive_inventory_preserves_sibling_update_and_wfc_tree(tmp_path):
    before, after, outdir, wfcdir = checkpoint_pair(tmp_path, wfc=True)
    paths = scratch_paths(tmp_path, restart_wfc=tmp_path / "resume-wfc",
                          fresh_wfc=tmp_path / "fresh-wfc")
    assert contract.checkpoint_unchanged(before, after)
    assert {entry["path"] for entry in before["outdir"]["files"]} == {
        "charge-density.dat", "probe.update", "prefix.save/data-file-schema.xml"}
    assert before["wfcdir"]["files"][0]["path"] == "wfc1.dat"
    assert paths["restart_wfcdir"] != paths["fresh_wfcdir"]
    assert outdir.is_dir() and wfcdir.is_dir()


def test_recursive_inventory_detects_nested_mutation(tmp_path):
    before, _, outdir, _ = checkpoint_pair(tmp_path)
    (outdir / "prefix.save" / "data-file-schema.xml").write_bytes(b"mutated")
    after = contract.checkpoint_inventory(outdir)
    assert not contract.checkpoint_unchanged(before, after)


def test_tree_inventory_sorts_full_relative_paths(tmp_path):
    root = tmp_path / "ordered"
    (root / "a").mkdir(parents=True)
    (root / "a" / "z").write_bytes(b"nested")
    (root / "a.txt").write_bytes(b"sibling")
    inventory = contract.tree_inventory(root)
    assert [entry["path"] for entry in inventory["files"]] == ["a.txt", "a/z"]


def test_inventory_refuses_root_and_nested_symlinks(tmp_path):
    root = tmp_path / "tree"
    root.mkdir()
    (root / "data").write_bytes(b"safe")
    nested_link = root / "link"
    try:
        nested_link.symlink_to(root / "data")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    with pytest.raises(ValueError, match="symlink"):
        contract.tree_inventory(root)
    nested_link.unlink()
    root_link = tmp_path / "tree-link"
    root_link.symlink_to(root, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        contract.tree_inventory(root_link)


@pytest.mark.parametrize("paths", [
    {"restart_outdir": "same", "fresh_outdir": "same"},
    {"restart_outdir": "parent", "fresh_outdir": "parent/child"},
    {"restart_outdir": "left", "fresh_outdir": "right",
     "restart_wfcdir": "wave", "fresh_wfcdir": "wave"},
])
def test_overlapping_or_aliased_scratch_roots_fail(tmp_path, paths):
    expanded = {key: (None if value is None else tmp_path / value)
                for key, value in paths.items()}
    expanded.setdefault("restart_wfcdir", None)
    expanded.setdefault("fresh_wfcdir", None)
    with pytest.raises(ValueError, match="overlap|alias"):
        contract.validate_scratch_separation(**expanded)


@pytest.mark.parametrize("field,value", [
    ("segment_index", True), ("reseeds_so_far", True),
    ("max_segments", True), ("max_reseeds", True), ("terminal", 1),
])
def test_counter_and_terminal_bool_types_are_strict(tmp_path, field, value):
    kwargs = {"warm": scf(), "fresh": scf()}
    if field == "reseeds_so_far":
        kwargs["reseeds"] = value
    else:
        kwargs[field] = value
    with pytest.raises(ValueError):
        decide(tmp_path, **kwargs)


def test_terminal_lower_state_requests_reseed_and_never_completes(tmp_path):
    lower = -100.0 - 11.0 / contract.RY_MEV
    result = decide(tmp_path, fresh=scf(energy=lower), terminal=True)
    assert result["action"] == "RESEED"
    assert result["proposed_action"] == "RESEED"
    assert result["history_disposition"] == "RESET_REQUIRED_BY_ADAPTER"
