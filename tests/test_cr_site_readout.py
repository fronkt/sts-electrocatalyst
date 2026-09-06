"""Regression checks on the retained Cr-site evidence; no model execution."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "results/cr_site_chains_2026-09-06"


@pytest.fixture(scope="module")
def analyzer():
    spec = importlib.util.spec_from_file_location("cr_readout", BANK / "analyze_chains.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def pair(tmp_path):
    data = {}
    folder = tmp_path / "inputs"
    folder.mkdir()
    for arm in ("equiatomic", "leader"):
        data[arm] = json.loads((BANK / (arm + "_result.json")).read_text(encoding="utf-8"))
        assert data[arm]["status"] == "complete"
        save(folder, arm, data[arm])
    return folder, data


def save(folder, arm, payload):
    for suffix, content in (("result", payload), ("manifest", payload["manifest"])):
        (folder / (arm + "_" + suffix + ".json")).write_text(json.dumps(content), encoding="utf-8")


def seal(mod, payload):
    for result in payload["results"]:
        result["site_evidence"] = mod.analyze_site_evidence(result["row"], [])
    payload["results_sha256"] = mod.identity(payload["results"])
    manifest = payload["manifest"]
    manifest["manifest_id"] = mod.identity({k: v for k, v in manifest.items() if k != "manifest_id"})
    payload["manifest_id"] = manifest["manifest_id"]


def test_readout_preserves_failed_chain_and_roundtrips_all_coordinates(analyzer, pair, tmp_path):
    folder, data = pair
    out = tmp_path / "readout"
    result = analyzer.analyze(folder, out)
    assert json.loads((out / "readout.json").read_text()) == result
    assert all(value is False for value in result["claims"].values())
    assert result["arms"]["equiatomic"]["site_evidence"]["quality_counts"] == {"eligible": 1, "failed": 0, "unknown": 0}
    assert result["arms"]["leader"]["site_evidence"]["quality_counts"] == {"eligible": 0, "failed": 1, "unknown": 0}
    assert result["leader_minus_equiatomic"]["eta_difference_V"] == pytest.approx(0.5250223543675512)
    inventory = [item for items in result["coordinate_inventory"].values() for item in items]
    assert len(inventory) == 12
    assert all(item["roundtrip_verified"] for item in inventory)
    for item in inventory:
        assert analyzer.file_hash(out / "structures" / item["file"]) == item["sha256_lf"]


def test_existing_output_survives(analyzer, pair, tmp_path):
    folder, _ = pair
    out = tmp_path / "existing"
    out.mkdir()
    sentinel = out / "keep.txt"
    sentinel.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        analyzer.analyze(folder, out)
    assert list(out.iterdir()) == [sentinel]
    assert sentinel.read_bytes() == b"keep"


@pytest.mark.parametrize("mutation,match", [
    ("wrong_start", "selected start disagrees"),
    ("duplicate_start", "start roster"),
    ("fractions", "row composition mismatch"),
    ("gas_injection", "unexpected adsorbate or gas state roster"),
    ("checksum", "result hash mismatch"),
    ("source_hash", "source data identity mismatch"),
])
def test_resealed_corruptions_are_rejected(analyzer, pair, mutation, match):
    folder, data = pair
    payload = data["equiatomic"]
    row = payload["results"][0]["row"]
    site = row["per_site_records"][0]
    if mutation == "wrong_start":
        site["bonds"]["OH_start"] = "builder"
    elif mutation == "duplicate_start":
        site["start_records"]["OH"][1]["start"] = "builder"
    elif mutation == "fractions":
        row["fractions"][0] += .001
        row["fractions"][1] -= .001
    elif mutation == "gas_injection":
        row["gas_reference_records"]["slab"] = deepcopy(row["gas_reference_records"]["H2O"])
    elif mutation == "source_hash":
        payload["manifest"]["source"]["sha256_lf"] = "0" * 64
    seal(analyzer, payload)
    if mutation == "checksum":
        payload["results_sha256"] = "0" * 64
    save(folder, "equiatomic", payload)
    with pytest.raises(ValueError, match=match):
        analyzer.load_arm(folder, "equiatomic")


@pytest.mark.parametrize("section,key,value,match", [
    ("source", "filename", "other.json", "paired calculations differ in source"),
    ("protocol", "mode", "feasibility", "paired protocol mismatch"),
])
def test_pair_mismatch_before_output(analyzer, pair, tmp_path, section, key, value, match):
    folder, data = pair
    payload = data["leader"]
    payload["manifest"][section][key] = value
    seal(analyzer, payload)
    save(folder, "leader", payload)
    out = tmp_path / "unused"
    with pytest.raises(ValueError, match=match):
        analyzer.analyze(folder, out)
    assert not out.exists()
