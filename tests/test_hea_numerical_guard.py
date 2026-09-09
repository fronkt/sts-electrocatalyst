"""Frozen numerical inputs, source integrity and independent checkpoint clones."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dft import hea_numerical_guard as guard


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle)


def update_spec(case):
    write_json(case["spec_path"], case["spec"])


def update_inventory(case):
    write_json(case["inventory_path"], case["inventory"])
    case["spec"]["source_checkpoints_sha256"] = digest(case["inventory_path"].read_bytes())
    update_spec(case)


@pytest.fixture
def numerical(tmp_path):
    runs = tmp_path / "runs"
    directory = runs / guard.DIRECTORY
    directory.mkdir(parents=True)
    jobs, checkpoints = [], []
    for index in range(6):
        mode = "tight" if index < 4 else "recovery"
        job, prefix = "hn__case_" + str(index), "hc__source_" + str(index)
        raw = ("\n".join([
            "&CONTROL", " calculation = 'scf'", " restart_mode = 'from_scratch'",
            " prefix = '" + prefix + "'", " outdir = './tmp_" + job + "'",
            " pseudo_dir = '" + guard.PSEUDO_DIRECTORY + "'", " max_seconds = 13200", "/",
            "&ELECTRONS", " startingpot = 'file'",
            " startingwfc = '" + ("file" if mode == "tight" else "atomic+random") + "'",
            " conv_thr = " + ("1.0d-8" if mode == "tight" else "1.0d-6"),
            " mixing_beta = " + ("0.3" if mode == "tight" else "0.1"), "/", ""])).encode()
        (directory / (job + ".in")).write_bytes(raw)
        jobs.append(dict(job=job, dir=guard.DIRECTORY, suffix=".in", nk=8, sha256=digest(raw),
                         prefix=prefix, mode=mode))
        source_dir = guard.SOURCE_DIRECTORY + "/tmp_" + prefix + "/" + prefix + ".save"
        source = runs / source_dir
        source.mkdir(parents=True)
        files = []
        for name in sorted(guard.PORTABLE_FILES | (guard.WFC_FILES if mode == "tight" else set())):
            content = (prefix + ":" + name + "\n").encode()
            (source / name).write_bytes(content)
            files.append(dict(path=name, size_bytes=len(content), sha256=digest(content)))
        checkpoints.append(dict(prefix=prefix, dir=source_dir, files=files))
    rows = [f"{j['dir']} {j['job']} .in 8" for j in jobs]
    manifest = runs / guard.MANIFEST[5:]
    manifest.write_bytes(("# NP=128 NCONC=1\n# SUBMIT WITH EXCLUDE=a024\n" + "\n".join(rows) + "\n").encode())
    Path(str(manifest) + ".lines").write_bytes(("\n".join(rows) + "\n").encode())
    inventory_path = tmp_path / guard.INVENTORY
    inventory = dict(schema=guard.SOURCE_SCHEMA, checkpoints=checkpoints)
    write_json(inventory_path, inventory)
    spec = dict(schema=guard.SCHEMA, manifest=guard.MANIFEST, manifest_sha256=digest(manifest.read_bytes()),
                np=128, concurrency=1, wall_hours=4, source_checkpoints=guard.INVENTORY,
                source_checkpoints_sha256=digest(inventory_path.read_bytes()), jobs=jobs)
    case = dict(runs=runs, directory=directory, manifest=manifest, inventory_path=inventory_path,
                inventory=inventory, spec=spec, spec_path=tmp_path / "spec.json")
    update_spec(case)
    return case


def check(case, row=None):
    return guard.validate_batch(case["spec_path"], case["runs"], row)


def prepare(case, row=1):
    return guard.prepare_row(case["spec_path"], case["runs"], row)


def source(case, row=1):
    return case["runs"] / case["inventory"]["checkpoints"][row - 1]["dir"]


def scratch(case, row=1):
    return case["directory"] / ("tmp_" + case["spec"]["jobs"][row - 1]["job"])


def snapshot(path):
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob("*") if p.is_file()}


def test_readonly_validation_and_exact_cli_tokens(numerical, capsys):
    assert check(numerical)["selected"] is None
    args = ["--spec", str(numerical["spec_path"]), "--runs", str(numerical["runs"])]
    assert guard.main(args) == 0
    assert capsys.readouterr().out == "VALID\n"
    assert guard.main(args + ["--row", "1"]) == 0
    assert capsys.readouterr().out == "hea/numerical_2026-09-08 hn__case_0 .in 8 hc__source_0 tight\n"
    assert not scratch(numerical).exists()


@pytest.mark.parametrize("row", [1, 5])
def test_clone_has_verified_independent_bytes_and_receipt(numerical, row):
    original = snapshot(source(numerical, row))
    result = prepare(numerical, row)
    job = result["selected"]
    clone = scratch(numerical, row) / (job["prefix"] + ".save")
    assert snapshot(clone) == original
    assert (numerical["directory"] / (job["job"] + ".run.in")).read_bytes() == (numerical["directory"] / (job["job"] + ".in")).read_bytes()
    receipt = json.loads((numerical["directory"] / (job["job"] + ".clone_receipt.json")).read_text())
    assert receipt["source"] == numerical["inventory"]["checkpoints"][row - 1]["dir"]
    assert receipt["destination"] == clone.relative_to(numerical["runs"]).as_posix()
    assert receipt["files"] == numerical["inventory"]["checkpoints"][row - 1]["files"]
    assert receipt["source_checkpoints_sha256"] == numerical["spec"]["source_checkpoints_sha256"]
    (clone / "charge-density.hdf5").write_bytes(b"changed by new SCF")
    assert snapshot(source(numerical, row)) == original
    with pytest.raises(ValueError, match="preexisting"):
        prepare(numerical, row)


def test_finished_sibling_is_allowed_only_in_selected_mode(numerical):
    prepare(numerical, 1)
    first = snapshot(scratch(numerical, 1))
    assert check(numerical, 2)["selected"]["job"] == "hn__case_1"
    prepare(numerical, 2)
    assert snapshot(scratch(numerical, 1)) == first
    with pytest.raises(ValueError, match="preexisting"):
        check(numerical)


@pytest.mark.parametrize("mutation", ["hash", "missing", "extra"])
def test_source_drift_refuses_before_destination_creation(numerical, mutation):
    target = source(numerical) / "paw.txt"
    if mutation == "hash":
        target.write_bytes(b"corrupt")
    elif mutation == "missing":
        target.unlink()
    else:
        (source(numerical) / "unexpected").write_bytes(b"unlisted")
    with pytest.raises(ValueError, match="source checkpoint"):
        prepare(numerical)
    assert not scratch(numerical).exists()


def test_selected_mode_does_not_read_irrelevant_source_but_checks_all_decks(numerical):
    (source(numerical, 6) / "paw.txt").write_bytes(b"changed sibling source")
    assert check(numerical, 1)["selected"]["job"] == "hn__case_0"
    with pytest.raises(ValueError, match="source checkpoint"):
        check(numerical)
    deck = numerical["directory"] / "hn__case_5.in"
    deck.write_bytes(deck.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="input SHA256"):
        check(numerical, 1)


def test_copy_failure_keeps_partial_clone_and_every_original(numerical, monkeypatch):
    original = snapshot(source(numerical))
    real_open = Path.open
    def failing_open(path, mode="r", *args, **kwargs):
        if mode == "xb" and path.name == "paw.txt":
            raise OSError("simulated destination failure")
        return real_open(path, mode, *args, **kwargs)
    monkeypatch.setattr(Path, "open", failing_open)
    with pytest.raises(OSError, match="destination failure"):
        prepare(numerical)
    assert scratch(numerical).exists()
    assert list(scratch(numerical).rglob("charge-density.hdf5"))
    assert snapshot(source(numerical)) == original
    assert not (numerical["directory"] / "hn__case_0.clone_receipt.json").exists()


def test_deck_changed_during_clone_is_refused_before_runtime_publication(numerical, monkeypatch):
    real_hash = guard._stream_hash
    changed = False
    def change_during_copy(path):
        nonlocal changed
        result = real_hash(path)
        if not changed and "tmp_hn__case_0" in str(path):
            changed = True
            deck = numerical["directory"] / "hn__case_0.in"
            deck.write_bytes(deck.read_bytes() + b"! changed during source copy\n")
        return result
    monkeypatch.setattr(guard, "_stream_hash", change_during_copy)
    with pytest.raises(ValueError, match="input changed during clone"):
        prepare(numerical)
    assert changed and scratch(numerical).exists()
    assert not (numerical["directory"] / "hn__case_0.run.in").exists()


def test_source_changed_after_preflight_is_caught_by_copy_hash(numerical, monkeypatch):
    real_verify = guard.verify_source
    def change_after_check(root, checkpoint):
        path = real_verify(root, checkpoint)
        (path / "charge-density.hdf5").write_bytes(b"changed after validation")
        return path
    monkeypatch.setattr(guard, "verify_source", change_after_check)
    with pytest.raises(ValueError, match="clone hash/size"):
        prepare(numerical)
    assert scratch(numerical).exists()
    assert not (numerical["directory"] / "hn__case_0.clone_receipt.json").exists()


@pytest.mark.parametrize("suffix", [".out", ".projwfc.out", ".run.in", ".projwfc.in", ".scf_qc.json",
                                    ".qc.json", ".clone_receipt.json", ".lowdin.txt", ".KILLED"])
def test_prior_artifacts_refused_without_modification(numerical, suffix):
    target = numerical["directory"] / ("hn__case_0" + suffix)
    target.write_bytes(b"previous attempt")
    with pytest.raises(ValueError, match="preexisting"):
        prepare(numerical)
    assert target.read_bytes() == b"previous attempt"
    assert not scratch(numerical).exists()


@pytest.mark.parametrize("key,value", [("np", 64), ("np", True), ("concurrency", 2), ("wall_hours", 8),
                                      ("manifest", "runs/../outside"), ("source_checkpoints", "../outside")])
def test_resource_and_path_expansion_refused(numerical, key, value):
    candidate = deepcopy(numerical["spec"])
    candidate[key] = value
    with pytest.raises(ValueError):
        guard.validate_spec(candidate)


@pytest.mark.parametrize("key,value", [("job", "../bad"), ("prefix", "hc__x/../bad"), ("nk", 4),
                                      ("nk", True), ("dir", "hea/controls_2026-09-07"), ("mode", "retry")])
def test_invalid_job_contract_refused(numerical, key, value):
    candidate = deepcopy(numerical["spec"])
    candidate["jobs"][0][key] = value
    with pytest.raises(ValueError):
        guard.validate_spec(candidate)


def test_exact_job_modes_counts_and_unique_prefixes(numerical):
    for mutation in ("count", "mode", "prefix", "unknown_key"):
        candidate = deepcopy(numerical["spec"])
        if mutation == "count": candidate["jobs"].pop()
        elif mutation == "mode": candidate["jobs"][0]["mode"] = "recovery"
        elif mutation == "prefix": candidate["jobs"][1]["prefix"] = candidate["jobs"][0]["prefix"]
        else: candidate["jobs"][0]["extra"] = "ignored"
        with pytest.raises(ValueError):
            guard.validate_spec(candidate)


@pytest.mark.parametrize("mutation", ["traversal", "duplicate", "unsorted", "empty_density", "missing_wfc",
                                     "wrong_directory", "missing_source", "recovery_extra"])
def test_inventory_structure_refused_even_after_repin(numerical, mutation):
    cp = numerical["inventory"]["checkpoints"][0]
    if mutation == "traversal": cp["files"][0]["path"] = "../outside"
    elif mutation == "duplicate": cp["files"].append(deepcopy(cp["files"][0]))
    elif mutation == "unsorted": cp["files"].reverse()
    elif mutation == "empty_density":
        next(e for e in cp["files"] if e["path"] == "charge-density.hdf5")["size_bytes"] = 0
    elif mutation == "missing_wfc": cp["files"] = [e for e in cp["files"] if e["path"] != "wfcup8.hdf5"]
    elif mutation == "wrong_directory": cp["dir"] = "hea/numerical_2026-09-08/tmp_hn__case_0"
    elif mutation == "missing_source": numerical["inventory"]["checkpoints"].pop()
    else:
        numerical["inventory"]["checkpoints"][5]["files"].append(
            dict(path="wfcup1.hdf5", size_bytes=1, sha256="0" * 64))
    update_inventory(numerical)
    with pytest.raises(ValueError):
        check(numerical)


@pytest.mark.parametrize("old,new", [
    ("calculation = 'scf'", "calculation = 'relax'"),
    ("restart_mode = 'from_scratch'", "restart_mode = 'restart'"),
    ("prefix = 'hc__source_0'", "prefix = 'hn__case_0'"),
    ("startingpot = 'file'", "startingpot = 'atomic'"),
    ("startingwfc = 'file'", "startingwfc = 'atomic+random'"),
    ("conv_thr = 1.0d-8", "conv_thr = 1.0d-6"),
    ("mixing_beta = 0.3", "mixing_beta = 0.1"),
    ("max_seconds = 13200", "max_seconds = 14400"),
    ("startingpot = 'file'", "startingpot = 'file'\n startingpot = 'file'"),
])
def test_deck_contract_refused_even_after_repin(numerical, old, new):
    path = numerical["directory"] / "hn__case_0.in"
    raw = path.read_bytes().replace(old.encode(), new.encode())
    path.write_bytes(raw)
    numerical["spec"]["jobs"][0]["sha256"] = digest(raw)
    update_spec(numerical)
    with pytest.raises(ValueError, match="input"):
        check(numerical)


@pytest.mark.parametrize("header", ["", "# NP=128 NCONC=1; four hours\n", "# NP=64 NCONC=1\n",
                                    "# NP=128 NCONC=1\n# NP=128 NCONC=1\n"])
def test_manifest_resource_header_matches_actual_driver(numerical, header):
    raw = numerical["manifest"].read_bytes().replace(b"# NP=128 NCONC=1\n", header.encode())
    numerical["manifest"].write_bytes(raw)
    numerical["spec"]["manifest_sha256"] = digest(raw)
    update_spec(numerical)
    with pytest.raises(ValueError, match="resource header"):
        check(numerical)


def symlink_or_skip(link, target):
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable for test user")


def test_source_symlink_refused_even_with_identical_bytes(numerical):
    target = source(numerical) / "paw.txt"
    copy = numerical["runs"].parent / "same_paw.txt"
    copy.write_bytes(target.read_bytes())
    target.unlink()
    symlink_or_skip(target, copy)
    with pytest.raises(ValueError, match="link"):
        prepare(numerical)
    assert not scratch(numerical).exists()


def test_broken_destination_link_is_not_absence(numerical):
    target = numerical["directory"] / "hn__case_0.out"
    symlink_or_skip(target, numerical["directory"] / "absent")
    with pytest.raises(ValueError, match="link"):
        prepare(numerical)
    assert target.is_symlink()


DENSITY = "The initial density is read from file\n"
FILE_WFC = "Starting wfcs from file\n"
ATOMIC_WFC = "Starting wfcs are  224 randomized atomic wfcs\n"


@pytest.mark.parametrize("mode,wfc", [("tight", FILE_WFC), ("recovery", ATOMIC_WFC),
                                    ("recovery", ATOMIC_WFC.rstrip() + " + 2 random wfcs\n")])
def test_positive_startup_contract(mode, wfc):
    result = guard.validate_startup(DENSITY + wfc, mode)
    assert result["status"] == "VALID_STARTUP"
    assert result["density_file_reads"] == 1


@pytest.mark.parametrize("mode,text", [
    ("tight", FILE_WFC), ("recovery", ATOMIC_WFC),
    ("tight", DENSITY), ("recovery", DENSITY),
    ("tight", DENSITY + ATOMIC_WFC), ("recovery", DENSITY + FILE_WFC),
    ("tight", DENSITY + FILE_WFC + "Cannot read rho"),
    ("recovery", DENSITY + ATOMIC_WFC + "Cannot read rho"),
    ("tight", DENSITY + FILE_WFC + "Cannot read wfcs"),
    ("tight", DENSITY + FILE_WFC + "Wavefunctions not found"),
    ("tight", DENSITY + FILE_WFC + "recomputing them from scratch"),
    ("tight", DENSITY + FILE_WFC * 2),
])
def test_startup_fallback_or_missing_positive_marker_refused(mode, text):
    with pytest.raises(ValueError, match="startup"):
        guard.validate_startup(text, mode)


def test_startup_cli_matches_shared_validator(tmp_path, capsys):
    output = tmp_path / "output"
    output.write_bytes((DENSITY + FILE_WFC).encode())
    assert guard.main(["--startup-output", str(output), "--mode", "tight"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "VALID_STARTUP"
    output.write_bytes((DENSITY + "Cannot read wfcs\n").encode())
    assert guard.main(["--startup-output", str(output), "--mode", "tight"]) == 2
    result = capsys.readouterr()
    assert result.out == "" and result.err.startswith("REFUSE:")


@pytest.mark.parametrize("row", [0, 7, True, 1.0])
def test_row_bounds_refused(numerical, row):
    with pytest.raises(ValueError, match="row"):
        check(numerical, row)


@pytest.mark.parametrize("raw", [b'{"schema":"x","schema":"y"}', b'{"x":NaN}', b'{"x":Infinity}'])
def test_strict_json_refuses_ambiguous_constants(raw):
    with pytest.raises(ValueError):
        guard._json(raw)
