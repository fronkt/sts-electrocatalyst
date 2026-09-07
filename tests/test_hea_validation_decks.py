"""Prepared inputs preserve pending slots, exact reuse, projectors, and real job counts."""
import copy
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import build_hea_validation_decks as bd
import hea_validation_plan as hp
import hea_deck as hd


@pytest.fixture
def inputs(tmp_path):
    plan = hp.prepare()
    snapshot = hp.materialize(plan, tmp_path / "absent_census")
    return plan, snapshot


def refresh(snapshot):
    states = [s for row in snapshot["slots"] for s in row["states"].values()]
    snapshot["counts"].update(ready_state_slots=sum(s["status"] == "ready" for s in states),
                               pending_state_slots=sum(s["status"] != "ready" for s in states),
                               unique_ready_geometries=len({s["geometry_sha256"] for s in states if s["status"] == "ready"}))
    hp.seal(snapshot, "snapshot_id")


def test_new_decks_counts_cost_and_check_requires_all_artifacts(inputs, tmp_path):
    plan, snapshot = inputs
    out = tmp_path / "runs/hea/validation"
    inventory = bd.build(plan, snapshot, out, repo=tmp_path)
    assert inventory["counts"] == dict(chain_slots=15, state_slots=60, projector_slots=120,
                                       pending_projector_slots=104, ready_projector_slots=16,
                                       unique_new_inputs=16, unique_reused_inputs=0)
    assert len(list(out.glob("*.in"))) == 16
    assert bd.build(plan, snapshot, out, repo=tmp_path, check=True) == inventory
    manifest = (out / "m_validation.txt").read_text()
    assert hd.check_manifest_text(manifest)["n_rows"] == 16
    for key in ("plan_coreh", "floor_coreh", "ceiling_coreh"):
        assert inventory["cost_new_inputs_only"][key] == pytest.approx(sum(r["cost"][key] for r in inventory["unique_inputs"]))
    assert all(r["cost"]["ram_total_GB"] > 0 for r in inventory["unique_inputs"])
    (out / "inventory.json").unlink()
    with pytest.raises(FileNotFoundError, match="missing prepared"):
        bd.build(plan, snapshot, out, repo=tmp_path, check=True)


def test_check_empty_destination_fails_without_writing(inputs, tmp_path):
    with pytest.raises(FileNotFoundError):
        bd.build(*inputs, tmp_path / "runs/hea/empty", repo=tmp_path, check=True)
    assert not (tmp_path / "runs").exists()


def test_existing_exact_inputs_reused_and_shared_slab_aliased(inputs, tmp_path):
    plan, snapshot = inputs
    known = next(s for s in snapshot["slots"] if s["slot_id"] == "known__equiatomic")
    blind = next(s for s in snapshot["slots"] if s["slot_id"] == "blind__Fe25Co25Ni25Cr25")
    assert blind["selector"]["seed"] == known["selector"]["seed"]  # same decoration, distinct sites
    blind["states"]["slab"] = copy.deepcopy(known["states"]["slab"])
    blind["status"] = "pending_geometry"
    refresh(snapshot)
    inventory, files = bd.render_bundle(plan, snapshot, tmp_path / "runs/hea/test", repo=tmp_path)
    assert inventory["counts"]["ready_projector_slots"] == 18
    assert inventory["counts"]["unique_new_inputs"] == 16
    assert sum(a["status"] == "alias" for a in inventory["aliases"]) == 2
    # The actual tracked originals are exact references for all eight known geometries.
    inventory, _ = bd.render_bundle(plan, snapshot, ROOT / "runs/hea/test_validation", repo=ROOT)
    assert inventory["counts"]["unique_reused_inputs"] == 16
    assert inventory["counts"]["unique_new_inputs"] == 0
    assert inventory["cost_new_inputs_only"]["plan_coreh"] == 0


def test_reuse_demands_every_byte_except_prefix(inputs, tmp_path):
    plan, snapshot = inputs
    slot = next(s for s in snapshot["slots"] if s["slot_id"] == "known__equiatomic")
    g = slot["states"]["slab"]["geometry"]
    original = hd.render_deck("old_prefix", g["symbols"], g["positions_A"], g["cell_A"], g["fixed_atom_indices"], "atomic")
    target = tmp_path / "runs/hea/branch_panel/original.in"
    target.parent.mkdir(parents=True)
    target.write_text(original, encoding="utf-8", newline="\n")
    inv, _ = bd.render_bundle(plan, snapshot, tmp_path / "runs/hea/new", repo=tmp_path)
    assert inv["counts"]["unique_reused_inputs"] == 1
    for old, new in (("  conv_thr = 1.0d-6", "  conv_thr = 1.0d-8"), ("0 0 0\n", "1 1 1\n")):
        target.write_text(original.replace(old, new, 1), encoding="utf-8", newline="\n")
        inv, _ = bd.render_bundle(plan, snapshot, tmp_path / "runs/hea/new", repo=tmp_path)
        assert inv["counts"]["unique_reused_inputs"] == 0


@pytest.mark.parametrize("mode", ["snapshot", "geometry", "denominator", "split"])
def test_snapshot_tampering_rejected_before_write(inputs, tmp_path, mode):
    plan, snapshot = inputs
    if mode == "snapshot":
        snapshot["plan_id"] = "0"*64
    elif mode == "geometry":
        next(s for r in snapshot["slots"] for s in r["states"].values() if s["status"] == "ready")["geometry"]["positions_A"][0][0] += .1
    elif mode == "denominator":
        snapshot["slots"].pop()
    elif mode == "split":
        snapshot["slots"][0]["split"] = "heldout_dft_labels"
    hp.seal(snapshot, "snapshot_id")
    with pytest.raises(ValueError):
        bd.build(plan, snapshot, tmp_path / "runs/hea/test", repo=tmp_path)
    assert not (tmp_path / "runs").exists()


def test_forces_and_both_projectors_without_force_convergence_filter(inputs, tmp_path):
    plan, snapshot = inputs
    state = next(s for r in snapshot["slots"] for s in r["states"].values() if s["status"] == "ready")
    state["converged_by_force"] = False
    hp.seal(snapshot, "snapshot_id")
    inv, files = bd.render_bundle(plan, snapshot, tmp_path / "runs/hea/test", repo=tmp_path)
    assert inv["counts"]["unique_new_inputs"] == 16
    assert sum(a.get("converged_by_force") is False for a in inv["aliases"]) == 2
    texts = [v for k, v in files.items() if k.endswith(".in")]
    assert all("  tprnfor = .true." in t for t in texts)
    assert sum("HUBBARD (atomic)" in t for t in texts) == 8
    assert sum("HUBBARD (ortho-atomic)" in t for t in texts) == 8
