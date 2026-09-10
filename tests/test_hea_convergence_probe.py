"""Probe bounds, immutable parent lineage and informative rejected trajectories."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dft import hea_convergence_probe_guard as guard
from test_hea_followup_shell import _fake_scf, _fake_projection


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def batch(tmp_path, monkeypatch):
    spec = json.loads((ROOT / "results/hea_convergence_probe_2026-09-10/launch_spec.json").read_text())
    original = json.loads((ROOT / guard.SOURCE_SPEC).read_text())
    inventory = json.loads((ROOT / original["source_checkpoints"]).read_text())
    runs = tmp_path / "runs"
    for checkpoint in inventory["checkpoints"]:
        for entry in checkpoint["files"]:
            raw = (checkpoint["prefix"] + ":" + entry["path"]).encode()
            path = runs / checkpoint["dir"] / entry["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            entry.update(size_bytes=len(raw), sha256=digest(raw))
    dump(tmp_path / original["source_checkpoints"], inventory)
    original["source_checkpoints_sha256"] = digest((tmp_path / original["source_checkpoints"]).read_bytes())
    dump(tmp_path / guard.SOURCE_SPEC, original)
    source_hash = digest((tmp_path / guard.SOURCE_SPEC).read_bytes())
    monkeypatch.setattr(guard, "SOURCE_SPEC_SHA256", source_hash)
    spec["source_spec_sha256"] = source_hash
    paths = [guard.MANIFEST, guard.MANIFEST + ".lines"]
    paths += ["runs/" + job["dir"] + "/" + job["job"] + ".in" for job in spec["jobs"]]
    paths += ["runs/" + job["dir"] + "/" + job["job"] + ".in" for job in original["jobs"] if job["mode"] == "recovery"]
    for relative in paths:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    spec_path = tmp_path / "spec.json"
    dump(spec_path, spec)
    return dict(runs=runs, spec=spec, spec_path=spec_path, inventory=inventory)


def prepare(batch, row=1):
    return guard.prepare_row(batch["spec_path"], batch["runs"], row)


def iteration(number, accuracy=1e-4):
    return ("     iteration # %d ecut=80 beta=0.1\n" % number
            + "     ethr = 1.0D-10, avg # of iterations = 2.0\n"
            + "     total energy = -7956.3 Ry\n"
            + "     estimated scf accuracy < %.10f Ry\n" % accuracy
            + "     total magnetization = 0.06 Bohr mag/cell\n"
            + "     absolute magnetization = 58.53 Bohr mag/cell\n")


STARTUP = "The initial density is read from file\nStarting wfcs are 488 randomized atomic wfcs\n"


def seed_result(batch, row=1, capped=False):
    ctx = prepare(batch, row)
    job = guard.select(ctx, row)
    if capped:
        text = STARTUP + "".join(iteration(n) for n in range(1, 61)) + "convergence NOT achieved after 60 iterations\nJOB DONE.\n"
    else:
        text = STARTUP + "".join(iteration(n, 1e-7 if n == 7 else 1e-4) for n in range(1, 8))
        text += _fake_scf(guard.member(ctx, job, ".run.in").read_text())
        guard.member(ctx, job, ".projwfc.out").write_text(_fake_projection())
        saved = batch["runs"] / guard.receipt(ctx, job)["destination"]
        for name in guard.frozen.WFC_FILES:
            (saved / name).write_bytes(b"retained")
    guard.member(ctx, job, ".out").write_text(text)
    return ctx, job


def test_frozen_actual_decks_only_change_solver_controls():
    spec = json.loads((ROOT / "results/hea_convergence_probe_2026-09-10/launch_spec.json").read_text())
    original = json.loads((ROOT / guard.SOURCE_SPEC).read_text())
    for job in spec["jobs"]:
        source = next(j for j in original["jobs"] if j["job"] == job["source_job"])
        raw = (ROOT / "runs" / source["dir"] / (source["job"] + ".in")).read_bytes()
        new = (ROOT / "runs" / job["dir"] / (job["job"] + ".in")).read_bytes()
        assert new == guard.render_deck(raw, job)
        assert new.split(b"ATOMIC_SPECIES", 1)[1] == raw.split(b"ATOMIC_SPECIES", 1)[1]
        assert b"  electron_maxstep = 60\n" in new and b"  max_seconds = 3300\n" in new
        assert b"  degauss = 0.01\n" in new and b"  conv_thr = 1.0d-6\n" in new


def test_same_source_clones_independent_and_previous_attempt_immutable(batch):
    ctx = prepare(batch, 1)
    first = guard.select(ctx, 1)
    source = batch["runs"] / guard.receipt(ctx, first)["source"]
    before = {p.name: p.read_bytes() for p in source.iterdir()}
    clone = batch["runs"] / guard.receipt(ctx, first)["destination"]
    (clone / "charge-density.hdf5").write_bytes(b"new calculation density")
    ctx = prepare(batch, 3)
    third = guard.select(ctx, 3)
    third_clone = batch["runs"] / guard.receipt(ctx, third)["destination"]
    assert (third_clone / "charge-density.hdf5").read_bytes() == before["charge-density.hdf5"]
    assert {p.name: p.read_bytes() for p in source.iterdir()} == before
    with pytest.raises(ValueError, match="preexisting"):
        prepare(batch, 1)


@pytest.mark.parametrize("mutation", ["physics", "budget", "source"])
def test_repin_cannot_expand_frozen_scientific_contract(batch, mutation):
    job = batch["spec"]["jobs"][0]
    deck = batch["runs"] / job["dir"] / (job["job"] + ".in")
    if mutation == "physics":
        raw = deck.read_bytes().replace(b"degauss = 0.01", b"degauss = 0.02")
        deck.write_bytes(raw)
        job["sha256"] = digest(raw)
    elif mutation == "budget":
        batch["spec"]["wall_hours"] = 4
    else:
        job["source_job"] = guard.SOURCES[1]
    dump(batch["spec_path"], batch["spec"])
    with pytest.raises(ValueError):
        prepare(batch)
    assert not (batch["runs"] / guard.DIRECTORY / ("tmp_" + job["job"])).exists()


def test_changed_checkpoint_refused_before_copy(batch):
    checkpoint = next(c for c in batch["inventory"]["checkpoints"] if c["prefix"] == batch["spec"]["jobs"][0]["prefix"])
    (batch["runs"] / checkpoint["dir"] / "occup.txt").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="hash/size"):
        prepare(batch)


def test_plateau_is_preserved_as_informative_rejection(batch):
    ctx, job = seed_result(batch, capped=True)
    result = guard.summarize(batch["spec_path"], batch["runs"], 1, 0)
    assert result["scientific_status"] == "REJECTED"
    assert result["diagnostic_status"] == "CAPPED_NONCONVERGENCE"
    assert result["complete_iterations"] == 60
    assert result["original_failed_attempt_reclassified"] is False
    history = json.loads(guard.member(ctx, job, ".history.json").read_text())
    assert len(history["iterations"]) == 60
    assert history["iterations"][-1]["estimated_accuracy_ry"] == 1e-4


def test_complete_endpoint_needs_projection_and_retained_waves(batch):
    ctx, job = seed_result(batch)
    result = guard.summarize(batch["spec_path"], batch["runs"], 1, 0, 0)
    assert result["scientific_status"] == "COMPLETE"
    assert result["complete_iterations"] == 7


@pytest.mark.parametrize("failure", ["ieee", "partial_projection", "missing_wave", "startup", "runtime", "receipt", "nonzero_exit"])
def test_finite_energy_and_job_done_do_not_override_failures(batch, failure):
    ctx, job = seed_result(batch)
    if failure == "ieee":
        path = guard.member(ctx, job, ".out")
        path.write_text(path.read_text() + "IEEE_INVALID_FLAG\n")
    elif failure == "partial_projection":
        guard.member(ctx, job, ".projwfc.out").write_text(_fake_projection(74))
    elif failure == "missing_wave":
        (batch["runs"] / guard.receipt(ctx, job)["destination"] / "wfcup8.hdf5").unlink()
    elif failure == "startup":
        path = guard.member(ctx, job, ".out")
        path.write_text(path.read_text().replace("The initial density is read from file", "Cannot read rho"))
    elif failure == "runtime":
        path = guard.member(ctx, job, ".run.in")
        path.write_bytes(path.read_bytes() + b"! drift\n")
    elif failure == "receipt":
        path = guard.member(ctx, job, ".clone_receipt.json")
        data = json.loads(path.read_text())
        data["arm"] = "other"
        dump(path, data)
    result = guard.summarize(batch["spec_path"], batch["runs"], 1, 1 if failure == "nonzero_exit" else 0, 0)
    assert result["scientific_status"] == "REJECTED"


def test_iteration_parser_does_not_invent_terminal_values():
    rows = guard.history(iteration(1) + "     iteration # 2\nMaximum CPU time exceeded\nJOB DONE.\n")
    assert rows[0]["complete"] is True
    assert rows[1]["complete"] is False and rows[1]["total_energy_ry"] is None
    with pytest.raises(ValueError, match="sequence"):
        guard.history(iteration(1) + iteration(3))
    with pytest.raises(ValueError, match="bound"):
        guard.history("".join(iteration(i) for i in range(1, 62)))
