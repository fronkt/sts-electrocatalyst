"""Fail-closed frozen batch validation; all tests use temporary files in process."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dft import hea_followup_guard as guard


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_spec(case):
    case["spec_path"].write_text(json.dumps(case["spec"]), encoding="utf-8", newline="\n")


@pytest.fixture
def batch(tmp_path):
    runs = tmp_path / "runs"
    directory = runs / guard.DIRECTORY
    directory.mkdir(parents=True)
    jobs = []
    for name, nk in (("hc__leader_builder__atomic__fragment", 8), ("hc__leader_builder__atomic__k6x3", 4)):
        raw = ("mock frozen input " + name + "\n").encode()
        (directory / (name + ".in")).write_bytes(raw)
        jobs.append(dict(job=name, dir=guard.DIRECTORY, suffix=".in", nk=nk, sha256=digest(raw)))
    rows = [f"{r['dir']} {r['job']} {r['suffix']} {r['nk']}" for r in jobs]
    manifest = runs / guard.MANIFEST.removeprefix("runs/")
    manifest.write_bytes(("# approved test manifest\n# SUBMIT WITH EXCLUDE=a024\n" + "\n".join(rows) + "\n").encode())
    lines = Path(str(manifest) + ".lines")
    lines.write_bytes(("\n".join(rows) + "\n").encode())
    spec = dict(schema=guard.SCHEMA, manifest=guard.MANIFEST, manifest_sha256=digest(manifest.read_bytes()),
                np=128, concurrency=1, wall_hours=4, jobs=jobs)
    result = dict(runs=runs, directory=directory, manifest=manifest, lines=lines, rows=rows,
                  spec=spec, spec_path=tmp_path / "spec.json")
    write_spec(result)
    return result


def check(batch, row=None):
    return guard.validate_batch(batch["spec_path"], batch["runs"], row)


def test_valid_batch_and_exact_cli_row_output(batch, capsys):
    assert check(batch) == dict(rows=batch["rows"], selected_row=None)
    args = ["--spec", str(batch["spec_path"]), "--runs", str(batch["runs"])]
    assert guard.main(args) == 0
    assert capsys.readouterr().out == "VALID\n"
    assert guard.main(args + ["--row", "2"]) == 0
    assert capsys.readouterr().out == batch["rows"][1] + "\n"


def test_runtime_allows_finished_sibling_but_allmode_refuses_it(batch):
    first = batch["spec"]["jobs"][0]["job"]
    retained = batch["directory"] / (first + ".out")
    retained.write_bytes(b"finished earlier task\n")
    assert check(batch, 2)["selected_row"] == batch["rows"][1]
    with pytest.raises(ValueError, match="preexisting"):
        check(batch)
    with pytest.raises(ValueError, match="preexisting"):
        check(batch, 1)
    assert retained.read_bytes() == b"finished earlier task\n"


@pytest.mark.parametrize("row", [0, -1, 3, True, 1.0, "1"])
def test_row_range_and_type_refused(batch, row):
    with pytest.raises(ValueError, match="one-based"):
        check(batch, row)


@pytest.mark.parametrize("key,value", [("np", 64), ("np", "128"), ("np", True),
    ("concurrency", 2), ("concurrency", True), ("wall_hours", 48), ("wall_hours", 4.0),
    ("schema", "other"), ("manifest", "runs/../../outside.txt"), ("manifest_sha256", "F" * 64)])
def test_wrong_resources_schema_and_hash_shape_rejected(batch, key, value):
    batch["spec"][key] = value
    with pytest.raises(ValueError):
        guard.validate_spec(batch["spec"])


@pytest.mark.parametrize("key,value", [("job", "../outside"), ("job", "hc__name/../../outside"),
    ("job", "hc__name;touch_BAD"), ("job", "hc__name\\outside"), ("job", "hc__name\nextra"),
    ("dir", "hea/../outside"), ("suffix", ".out"), ("nk", 0), ("nk", 7), ("nk", True),
    ("nk", "4"), ("sha256", "0" * 63)])
def test_unsafe_or_invalid_job_fields_rejected(batch, key, value):
    batch["spec"]["jobs"][0][key] = value
    with pytest.raises(ValueError):
        guard.validate_spec(batch["spec"])


def test_duplicate_empty_and_unknown_fields_rejected(batch):
    candidate = deepcopy(batch["spec"])
    candidate["jobs"].append(deepcopy(candidate["jobs"][0]))
    with pytest.raises(ValueError, match="duplicate job"):
        guard.validate_spec(candidate)
    candidate["jobs"] = []
    with pytest.raises(ValueError, match="nonempty"):
        guard.validate_spec(candidate)
    candidate = deepcopy(batch["spec"])
    candidate["jobs"][0]["extra"] = "unexpected"
    with pytest.raises(ValueError, match="exactly"):
        guard.validate_spec(candidate)
    candidate = deepcopy(batch["spec"])
    candidate["extra"] = "unexpected"
    with pytest.raises(ValueError, match="exactly"):
        guard.validate_spec(candidate)


def test_deck_hashes_checked_for_every_job_even_in_row_mode(batch):
    second = batch["directory"] / (batch["spec"]["jobs"][1]["job"] + ".in")
    second.write_bytes(b"changed input")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        check(batch, 1)


def test_manifest_hash_catches_comment_drift(batch):
    batch["manifest"].write_bytes(batch["manifest"].read_bytes() + b"# changed\n")
    with pytest.raises(ValueError, match="SHA256 mismatch: manifest"):
        check(batch)


@pytest.mark.parametrize("mutation", ["order", "extra", "missing", "whitespace", "crlf", "no_final_lf", "not_licensed"])
def test_manifest_content_checked_even_when_its_hash_is_updated(batch, mutation):
    raw = batch["manifest"].read_bytes()
    if mutation == "order": raw = ("\n".join(reversed(batch["rows"])) + "\n").encode()
    elif mutation == "extra": raw += b"unexpected row .in 8\n"
    elif mutation == "missing": raw = (batch["rows"][0] + "\n").encode()
    elif mutation == "whitespace": raw = raw.replace(b" .in 8", b"  .in 8")
    elif mutation == "crlf": raw = raw.replace(b"\n", b"\r\n")
    elif mutation == "no_final_lf": raw = raw.rstrip(b"\n")
    elif mutation == "not_licensed": raw = b"# Not Licensed\n" + raw
    batch["manifest"].write_bytes(raw)
    batch["spec"]["manifest_sha256"] = digest(raw)
    write_spec(batch)
    with pytest.raises(ValueError):
        check(batch)


@pytest.mark.parametrize("mutation", ["order", "extra", "crlf", "no_final_lf"])
def test_lines_file_must_be_exact_canonical_snapshot(batch, mutation):
    raw = batch["lines"].read_bytes()
    if mutation == "order": raw = ("\n".join(reversed(batch["rows"])) + "\n").encode()
    elif mutation == "extra": raw += b"\n"
    elif mutation == "crlf": raw = raw.replace(b"\n", b"\r\n")
    else: raw = raw.rstrip(b"\n")
    batch["lines"].write_bytes(raw)
    with pytest.raises(ValueError, match=".lines differs"):
        check(batch)


@pytest.mark.parametrize("pattern", ["{job}.out", "{job}.projwfc.out", "{job}.run.in", "{job}.projwfc.in",
    "{job}.lowdin.txt", "{job}.scf_qc.json", "{job}.qc.json", "{job}.KILLED", "tmp_{job}", "dens/{job}.save", "dens/{job}.save.new"])
def test_every_prior_artifact_refused_and_preserved(batch, pattern):
    path = batch["directory"] / pattern.format(job=batch["spec"]["jobs"][0]["job"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"previous attempt")
    with pytest.raises(ValueError, match="preexisting"):
        check(batch, 1)
    assert path.read_bytes() == b"previous attempt"


def symlink_or_skip(link, target, is_directory=False):
    try:
        link.symlink_to(target, target_is_directory=is_directory)
    except (OSError, NotImplementedError):
        pytest.skip("OS does not permit symlinks for this test user")


def test_broken_prior_output_symlink_is_not_mistaken_for_absence(batch):
    link = batch["directory"] / (batch["spec"]["jobs"][0]["job"] + ".out")
    symlink_or_skip(link, batch["directory"] / "absent-target")
    with pytest.raises(ValueError, match="symlink"):
        check(batch)
    assert link.is_symlink()


def test_identical_deck_symlink_is_refused(batch):
    original = batch["directory"] / (batch["spec"]["jobs"][0]["job"] + ".in")
    target = batch["directory"] / "same-bytes.in"
    target.write_bytes(original.read_bytes())
    original.unlink()
    symlink_or_skip(original, target)
    with pytest.raises(ValueError, match="symlink"):
        check(batch)


def test_density_parent_symlink_cannot_escape_runs(batch, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    symlink_or_skip(batch["directory"] / "dens", outside, is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        check(batch)
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize("text", ['{"schema":"x","schema":"y"}', '{"value":NaN}', '{"value":Infinity}'])
def test_strict_json_loader(batch, text):
    batch["spec_path"].write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        guard.load_spec(batch["spec_path"])


def test_cli_refusal_is_stderr_only(batch, capsys):
    result = guard.main(["--spec", str(batch["spec_path"]), "--runs", str(batch["runs"]), "--row", "0"])
    captured = capsys.readouterr()
    assert result == 2 and captured.out == "" and captured.err.startswith("REFUSE:")
