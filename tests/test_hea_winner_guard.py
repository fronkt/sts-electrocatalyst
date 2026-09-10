"""Winner input lineage, runtime invariance and no-rerun checks."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dft import hea_winner_guard as guard

SPEC_REL = "results/hea_winner_2026-09-10/launch_spec.json"


def stage(root):
    spec = guard.read_json(ROOT / SPEC_REL)
    paths = [SPEC_REL, guard.MANIFEST, guard.MANIFEST + ".lines", *guard.REFERENCES]
    for row in spec["jobs"]:
        paths += ["runs/" + row["source"], "runs/" + row["dir"] + "/" + row["job"] + ".in"]
    for name in paths:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return spec


@pytest.fixture
def batch(tmp_path):
    spec = stage(tmp_path)
    return {"root": tmp_path, "runs": tmp_path / "runs", "spec": spec,
            "spec_path": tmp_path / SPEC_REL}


def check(case, row=None):
    return guard.validate_batch(case["spec_path"], case["runs"], row)


def test_actual_frozen_bundle_and_all_eight_exact_sources(batch):
    result = check(batch)
    assert len(result["rows"]) == 8
    assert {r["state"] for r in batch["spec"]["jobs"]} == {"slab", "OH", "O", "OOH"}
    for index, entry in enumerate(batch["spec"]["jobs"], 1):
        assert check(batch, index)["selected_row"] == result["rows"][index - 1]
        raw = (batch["runs"] / entry["source"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]


@pytest.mark.parametrize("key,value", [
    ("np", 64), ("concurrency", 2), ("wall_hours", 48), ("memory_gb", 238),
    ("np", True), ("concurrency", 1.0), ("manifest", "runs/../elsewhere"),
])
def test_allocation_cannot_expand(batch, key, value):
    spec = deepcopy(batch["spec"])
    spec[key] = value
    with pytest.raises(ValueError):
        guard.validate_spec(spec)


def test_a_different_chain_cannot_be_substituted_even_with_matching_hash(batch):
    spec = deepcopy(batch["spec"])
    spec["jobs"][0]["job"] = spec["jobs"][2]["job"]
    with pytest.raises(ValueError, match="selection"):
        guard.validate_spec(spec)


@pytest.mark.parametrize("what", ["source", "destination", "reference", "manifest", "lines"])
def test_frozen_identity_drift_is_refused(batch, what):
    entry = batch["spec"]["jobs"][-1]
    selected = {
        "source": batch["runs"] / entry["source"],
        "destination": batch["runs"] / entry["dir"] / (entry["job"] + ".in"),
        "reference": batch["root"] / guard.REFERENCES[0],
        "manifest": batch["root"] / guard.MANIFEST,
        "lines": batch["root"] / (guard.MANIFEST + ".lines"),
    }[what]
    selected.write_bytes(selected.read_bytes() + b"\n")
    with pytest.raises(ValueError):
        check(batch, 1)


@pytest.mark.parametrize("original", [False, True])
def test_prior_attempt_at_either_location_is_preserved_and_refused(batch, original):
    entry = batch["spec"]["jobs"][0]
    directory = guard.SOURCE_DIRECTORY if original else guard.DIRECTORY
    prior = batch["runs"] / directory / (entry["job"] + ".out")
    prior.write_bytes(b"retained previous attempt")
    with pytest.raises(ValueError, match="preexisting"):
        check(batch)
    assert prior.read_bytes() == b"retained previous attempt"
    if not original:
        assert check(batch, 2)["selected_row"]


@pytest.mark.parametrize("mutation", ["cutoff", "spin", "geometry", "mask", "prefix"])
def test_runtime_scientific_mutations_are_refused(batch, mutation):
    entry = batch["spec"]["jobs"][0]
    raw = (batch["runs"] / entry["source"]).read_bytes()
    runtime = guard.runtime_bytes(raw, entry["job"])
    edits = {
        "cutoff": (b"ecutwfc = 80.0", b"ecutwfc = 100.0"),
        "spin": (b"starting_magnetization(1) = 0.6", b"starting_magnetization(1) = -0.6"),
        "geometry": (b"5.855999434240528", b"5.855999434240529"),
        "mask": (b"0 0 0\n", b"1 1 1\n"),
        "prefix": (entry["job"].encode(), b"different_prefix"),
    }
    before, after = edits[mutation]
    assert before in runtime
    target = batch["runs"] / guard.DIRECTORY / (entry["job"] + ".run.in")
    target.write_bytes(runtime.replace(before, after, 1))
    with pytest.raises(ValueError, match="runtime input"):
        guard.verify_runtime(batch["spec_path"], batch["runs"], 1)


def test_exact_runtime_changes_are_the_only_allowed_changes(batch):
    entry = batch["spec"]["jobs"][0]
    raw = (batch["runs"] / entry["source"]).read_bytes()
    runtime = guard.runtime_bytes(raw, entry["job"])
    differences = [(a, b) for a, b in zip(raw.splitlines(), runtime.splitlines()) if a != b]
    assert len(differences) == 3
    assert [a.strip().split(b" = ")[0] for a, _ in differences] == [
        b"outdir", b"pseudo_dir", b"max_seconds"]
    target = batch["runs"] / guard.DIRECTORY / (entry["job"] + ".run.in")
    target.write_bytes(runtime)
    assert guard.verify_runtime(batch["spec_path"], batch["runs"], 1)["selected_row"]
    with pytest.raises(ValueError, match="preexisting"):
        check(batch, 1)


def test_pseudopotential_content_checked_not_just_filename(batch, tmp_path):
    spec = deepcopy(batch["spec"])
    pseudo = tmp_path / "pseudo"
    pseudo.mkdir()
    for item in spec["pseudopotentials"]:
        raw = item["path"].encode()
        (pseudo / item["path"]).write_bytes(raw)
        item["sha256"] = hashlib.sha256(raw).hexdigest()
    guard.verify_pseudopotentials(spec, pseudo)
    (pseudo / spec["pseudopotentials"][-1]["path"]).write_bytes(b"changed potential")
    with pytest.raises(ValueError, match="SHA256"):
        guard.verify_pseudopotentials(spec, pseudo)


def test_shared_helpers_and_frozen_spec_are_pinned_in_both_scripts():
    paths = {
        "SPEC": ROOT / SPEC_REL, "GUARD": ROOT / "src/dft/hea_winner_guard.py",
        "COMMON_GUARD": ROOT / "src/dft/hea_followup_guard.py",
        "QC": ROOT / "src/dft/hea_followup_qc.py",
        "FORCE_AUDIT": ROOT / "src/dft/hea_force_audit.py",
    }
    for script in ("66_hea_winner.slurm", "67_submit_hea_winner.sh"):
        text = (ROOT / "anvil" / script).read_text(encoding="utf-8")
        for variable, target in paths.items():
            assert 'check_hash "$' + variable + '" ' + hashlib.sha256(target.read_bytes()).hexdigest() in text
