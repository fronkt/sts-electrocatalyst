"""Offline checks for the same-state reproducibility probe; never launch QE/Slurm."""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
sys.path.insert(0, str(ROOT / "tests"))
import pa_catalyst_retest as base
import pa_fixed_geometry_diag as diag
import pa_fixed_geometry_readout as readout
import pa_repro_probe_decks as decks
import pa_repro_probe_readout as probe
from test_pa_fixed_geometry_diag import FakeRunner, allocation_text, local_spec

SPEC = ROOT / "results/pa_repro_probe_2026-10-07/launch_spec.json"
DIAG = ROOT / "results/pa_fixed_geometry_diag_2026-10-05/raw_mirror"
XML = "outdir/slab_c5low__pa_boundary.save/data-file-schema.xml"
needs_mirror = pytest.mark.skipif(not (DIAG / "runs/C3_warm_1e-10/stdout.log").exists(), reason="diagnostic mirror absent")


# ---------------------------------------------------------------- decks and spec
def test_probe_decks_are_the_launched_c3_deck_with_only_the_outdir_moved():
    c3 = decks.template()
    for arm in decks.ARMS:
        deck, changes = decks.build(arm)
        assert len(changes) == 1 and changes[0]["old"] == decks.TEMPLATE_OUTDIR
        assert deck.replace(f"sts_pa_repro_probe_2026-10-07/runs/{arm}/outdir",
                            "sts_pa_fixed_geometry_diag_2026-10-05/runs/C3_warm_1e-10/outdir") == c3
        data = (ROOT / "runs/hea/pa_repro_probe_2026-10-07/decks" / (arm + ".in")).read_bytes()
        assert data == deck.encode("ascii") and b"\r" not in data


def test_probe_spec_validates_pins_and_ceiling():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    assert list(spec["groups"]) == ["probe"]
    diag.validate_spec(spec, "probe")
    group = spec["groups"]["probe"]
    assert group["time_limit_seconds"] * 128 / 3600 <= group["max_cpu_su"] == spec["hard_ceiling_cpu_su"]
    # P2 launches only with CALL_SECONDS + CLEANUP_SECONDS left after P1 may use its full CALL_SECONDS.
    # What remains must cover the start-tree digest, both 15.2 GB copies and P1's teardown; the
    # diagnostic measured about 35 s for the digest and 40-50 s per copy, so require 900 s.
    slack = group["time_limit_seconds"] - (diag.CALL_SECONDS + diag.CLEANUP_SECONDS) - diag.CALL_SECONDS
    assert slack >= 900
    assert spec["controller"]["sha256"] == base.sha256_file(ROOT / "src/dft/pa_fixed_geometry_diag.py")
    assert spec["helper"]["sha256"] == base.sha256_file(ROOT / "src/dft/pa_catalyst_retest.py")
    assert spec["slurm"]["sha256"] == base.sha256_file(ROOT / "anvil/92_pa_repro_probe.slurm")
    receipt = json.loads((ROOT / "runs/hea/pa_repro_probe_2026-10-07/decks/deck_receipt.json").read_text())
    assert [row["deck"]["sha256"] for row in group["calls"]] == [receipt["decks"][a]["sha256"] for a in decks.ARMS]


@needs_mirror
def test_probe_start_tree_is_the_tree_c3_started_from():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    setup = json.loads((DIAG / "runs/C3_warm_1e-10/setup_receipt.json").read_text())
    ladder = json.loads((DIAG / "groups/ladder/group_receipt.json").read_text())
    c3 = next(row for row in ladder["calls"] if row["name"] == "C3_warm_1e-10")
    assert c3["status"] == "COMPLETED" and c3["setup"] == setup
    assert spec["checkpoint"]["outdir"] == setup["source_root"]
    assert (spec["checkpoint"]["tree_sha256"], spec["checkpoint"]["files"], spec["checkpoint"]["bytes"]) == \
        (setup["tree_sha256"], setup["files"], setup["bytes"])
    # The deck C3 actually ran is the template the probe decks are built from.
    assert base.sha256_file(DIAG / "runs/C3_warm_1e-10/input.in") == decks.TEMPLATE_SHA256


def test_slurm_script_admits_only_the_probe_group():
    text = (ROOT / "anvil/92_pa_repro_probe.slurm").read_text()
    assert 'in probe) ;;' in text and "replay" not in text
    assert text.count("sts_pa_repro_probe_2026-10-07") == 3 and "sts_pa_fixed_geometry_diag" not in text


# ---------------------------------------------------------------- controller
def probe_spec(tmp_path):
    spec = local_spec(tmp_path, "probe")
    real = json.loads(SPEC.read_text(encoding="utf-8"))
    spec["groups"] = copy.deepcopy(real["groups"])
    for row in spec["groups"]["probe"]["calls"]:
        path = tmp_path / "pins" / (row["name"] + ".in")
        path.write_bytes(("deck " + row["name"] + "\n").encode())
        row["deck"] = {"path": str(path), "sha256": base.sha256_file(path)}
    return spec


def run_probe(tmp_path, monkeypatch, runner):
    spec = probe_spec(tmp_path)
    monkeypatch.setenv("SLURM_JOB_ID", "123")
    monkeypatch.delenv("SLURM_ARRAY_JOB_ID", raising=False)
    reader = lambda job: {"stdout": allocation_text(limit="04:30:00"), "returncode": 0}
    g = diag.Group(spec, "probe", runner=runner, allocation_reader=reader, process_probe=lambda: [])
    code = g.run()
    receipt = json.loads((Path(spec["base"]) / "groups/probe/group_receipt.json").read_text())
    return code, receipt, spec


def test_probe_calls_each_start_from_a_fresh_verified_copy_of_the_pinned_tree(tmp_path, monkeypatch):
    runner = FakeRunner()
    code, receipt, spec = run_probe(tmp_path, monkeypatch, runner)
    assert code == 0 and runner.calls == ["P1_C3_repeat", "P2_C3_repeat"]
    p2 = Path(spec["base"]) / "runs/P2_C3_repeat/outdir"
    assert not (p2 / "P1_C3_repeat.out").exists()   # never P1's output state
    assert [c["setup"]["tree_sha256"] for c in receipt["calls"]] == [spec["checkpoint"]["tree_sha256"]] * 2
    assert receipt["checkpoint_unchanged"] is True and receipt["all_calls_completed"] is True


def test_failed_p1_does_not_block_p2(tmp_path, monkeypatch):
    code, receipt, _ = run_probe(tmp_path, monkeypatch, FakeRunner(fail={"P1_C3_repeat"}))
    assert code == 3 and [c["status"] for c in receipt["calls"]] == ["FAILED", "COMPLETED"]


# ---------------------------------------------------------------- readout
@pytest.fixture(scope="module")
def evaluations():
    c3 = readout.parse_arm(DIAG / "runs/C3_warm_1e-10", DIAG / "runs/C3_warm_1e-10" / XML)["evaluations"][0]
    d2 = readout.parse_arm(DIAG / "runs/D2_fresh_1e-10", DIAG / "runs/D2_fresh_1e-10" / XML)["evaluations"][0]
    return c3, d2


def shifted(evaluation, delta, energy=0.0):
    out = copy.deepcopy(evaluation)
    out["forces_Ry_bohr"][22][2] += delta
    out["energy_Ry"] += energy
    return out


@needs_mirror
@pytest.mark.parametrize("delta, pr1, pr2", [
    (0.0, "IDENTICAL_PATH", "PATH_SPREAD_EXCEEDS_RUN_TO_RUN_NOISE"),
    (3e-6, "REPRODUCIBLE_BELOW_HALF_GATE", "PATH_SPREAD_EXCEEDS_RUN_TO_RUN_NOISE"),
    (1.2e-5, "RUN_TO_RUN_NOISE_AT_GATE_SCALE", "PATH_SPREAD_WITHIN_RUN_TO_RUN_NOISE"),
])
def test_registered_readings_on_real_c3_and_d2(evaluations, delta, pr1, pr2):
    c3, d2 = evaluations
    runs = {"C3_warm_1e-10": c3, "P1_C3_repeat": copy.deepcopy(c3), "P2_C3_repeat": shifted(c3, delta)}
    out = probe.readings(runs, d2)
    assert out["path_pair_C3_vs_D2"]["force_Ry_bohr"] == pytest.approx(1.8418908558936282e-05)
    assert out["PR1_same_state_reproducibility"] == pr1 and out["PR2_path_vs_noise"] == pr2
    assert out["same_state_max_force_Ry_bohr"] == pytest.approx(abs(delta), abs=1e-15)


@needs_mirror
def test_energy_difference_alone_breaks_identity(evaluations):
    c3, d2 = evaluations
    runs = {"C3_warm_1e-10": c3, "P1_C3_repeat": shifted(c3, 0.0, 5e-8), "P2_C3_repeat": copy.deepcopy(c3)}
    assert probe.readings(runs, d2)["PR1_same_state_reproducibility"] == "REPRODUCIBLE_BELOW_HALF_GATE"


@needs_mirror
def test_missing_probe_call_is_incomplete(evaluations):
    c3, d2 = evaluations
    out = probe.readings({"C3_warm_1e-10": c3, "P1_C3_repeat": copy.deepcopy(c3)}, d2)
    assert out["PR1_same_state_reproducibility"] == out["PR2_path_vs_noise"] == "INCOMPLETE"
    assert list(out["pairs"]) == ["C3_warm_1e-10|P1_C3_repeat"]


def test_first_divergence():
    assert probe.first_divergence([1e-3, 2e-4], [1e-3, 2e-4]) is None
    assert probe.first_divergence([1e-3, 2e-4], [1e-3, 3e-4]) == 2
    assert probe.first_divergence([1e-3], [1e-3, 3e-4]) == 2


@needs_mirror
def test_main_reads_mirrors_and_excludes_failed_probe_calls(tmp_path):
    mirror = tmp_path / "probe"
    source = DIAG / "runs/C3_warm_1e-10"
    for name in probe.PROBES:
        target = mirror / "runs" / name
        (target / "outdir/slab_c5low__pa_boundary.save").mkdir(parents=True)
        for rel in ("input.in", "stdout.log", XML):
            (target / rel).write_bytes((source / rel).read_bytes())
    (mirror / "groups/probe").mkdir(parents=True)
    (mirror / "groups/probe/group_receipt.json").write_text(json.dumps(
        {"calls": [{"name": "P1_C3_repeat", "status": "COMPLETED"}, {"name": "P2_C3_repeat", "status": "FAILED"}]}))
    allocation = DIAG / "groups/ladder/allocation_03_before_launch.json"
    (mirror / "groups/probe/allocation_01_before_launch.json").write_bytes(allocation.read_bytes())
    out = tmp_path / "readout.json"
    assert probe.main(["--probe", str(mirror), "--diag", str(DIAG), "--out", str(out)]) == 0
    result = json.loads(out.read_text())
    assert result["excluded"] == {"P2_C3_repeat": "controller status FAILED"}
    assert result["readings"]["PR1_same_state_reproducibility"] == "INCOMPLETE"
    pair = result["readings"]["pairs"]["C3_warm_1e-10|P1_C3_repeat"]
    assert pair["force_Ry_bohr"] == 0.0 and pair["nodes"] == ["a558", "a558"] and pair["same_node"] is True


@needs_mirror
def test_main_excludes_a_probe_call_without_controller_status(tmp_path):
    mirror = tmp_path / "probe"
    target = mirror / "runs/P1_C3_repeat"
    (target / "outdir/slab_c5low__pa_boundary.save").mkdir(parents=True)
    for rel in ("input.in", "stdout.log", XML):
        (target / rel).write_bytes((DIAG / "runs/C3_warm_1e-10" / rel).read_bytes())
    out = tmp_path / "readout.json"
    assert probe.main(["--probe", str(mirror), "--diag", str(DIAG), "--out", str(out)]) == 0
    excluded = json.loads(out.read_text())["excluded"]
    assert excluded["P1_C3_repeat"] == "controller status None" and excluded["P2_C3_repeat"] == "not run"


@needs_mirror
def test_node_labels_split_same_and_cross_node_pairs(evaluations):
    c3, d2 = evaluations
    runs = {"C3_warm_1e-10": c3, "P1_C3_repeat": shifted(c3, 2e-6), "P2_C3_repeat": shifted(c3, 2e-6)}
    out = probe.readings(runs, d2, {"C3_warm_1e-10": "a558", "P1_C3_repeat": "a100", "P2_C3_repeat": "a100"})
    assert out["same_node_max"] == 0.0 and out["cross_node_max"] == pytest.approx(2e-6)
    assert probe.readings(runs, d2)["same_node_max"] is None
