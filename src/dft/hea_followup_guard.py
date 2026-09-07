"""Validate a frozen HEA follow-up batch before submission or one array task.

The shell caller must pin the byte hashes of this module AND the spec before
calling it. All-mode requires every job to be fresh. --row checks freshness only
for that task, allowing earlier tasks to retain their completed artifacts.
This guard performs no submission, compute, deletion, or filesystem mutation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = "hea_followup_v1"
MANIFEST = "runs/hea/m_controls_2026-09-07_followup_approved.txt"
DIRECTORY = "hea/controls_2026-09-07"
HASH = re.compile(r"[0-9a-f]{64}\Z")
JOB = re.compile(r"hc__[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
SPEC_KEYS = {"schema", "manifest", "manifest_sha256", "np", "concurrency", "wall_hours", "jobs"}
JOB_KEYS = {"job", "dir", "suffix", "nk", "sha256"}


def _keys(value, expected, context):
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{context}: expected exactly {sorted(expected)}")


def _hash(value, context):
    if not isinstance(value, str) or HASH.fullmatch(value) is None:
        raise ValueError(f"{context}: lowercase SHA256 required")


def validate_spec(spec):
    """Reject malformed identities, unsupported resources and duplicate jobs."""
    _keys(spec, SPEC_KEYS, "spec")
    if spec["schema"] != SCHEMA or spec["manifest"] != MANIFEST:
        raise ValueError("unsupported schema or approved manifest path")
    _hash(spec["manifest_sha256"], "manifest_sha256")
    for name, expected in (("np", 128), ("concurrency", 1), ("wall_hours", 4)):
        if type(spec[name]) is not int or spec[name] != expected:
            raise ValueError(f"{name} must be integer {expected}")
    if not isinstance(spec["jobs"], list) or not spec["jobs"]:
        raise ValueError("jobs must be a nonempty list")
    seen = set()
    for row in spec["jobs"]:
        _keys(row, JOB_KEYS, "job row")
        if not isinstance(row["job"], str) or JOB.fullmatch(row["job"]) is None:
            raise ValueError("unsafe job basename")
        if row["dir"] != DIRECTORY or row["suffix"] != ".in":
            raise ValueError("unexpected job directory or input suffix")
        if type(row["nk"]) is not int or row["nk"] not in (4, 8) or spec["np"] % row["nk"]:
            raise ValueError("nk must be integer 4 or 8 dividing NP")
        _hash(row["sha256"], row["job"] + ".sha256")
        if row["job"] in seen:
            raise ValueError("duplicate job identity: " + row["job"])
        seen.add(row["job"])
    return spec


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("nonfinite JSON constant: " + value)


def load_spec(path):
    return validate_spec(json.loads(Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object, parse_constant=_invalid_constant))


def _is_link(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def _path(root, relative):
    """Resolve only trusted relative components; refuse links below the root."""
    parts = relative.split("/")
    if not parts or any(p in ("", ".", "..") or "\\" in p or ":" in p for p in parts):
        raise ValueError("unsafe relative path")
    candidate = root
    for part in parts:
        candidate = candidate / part
        if _is_link(candidate):
            raise ValueError("symlink/junction in batch path: " + str(candidate))
        if candidate.exists():
            try:
                candidate.resolve(strict=True).relative_to(root)
            except ValueError as exc:
                raise ValueError("batch path escapes runs directory") from exc
    return candidate


def _read_file(path):
    if not path.is_file():
        raise ValueError("required regular file absent: " + str(path))
    return path.read_bytes()


def _matches(raw, expected, context):
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("SHA256 mismatch: " + context)


def _fresh(root, row):
    base = row["dir"] + "/"
    job = row["job"]
    names = [job + suffix for suffix in (".out", ".projwfc.out", ".run.in", ".projwfc.in", ".lowdin.txt", ".scf_qc.json", ".qc.json", ".KILLED")]
    names += ["tmp_" + job, "dens/" + job + ".save", "dens/" + job + ".save.new"]
    for name in names:
        path = _path(root, base + name)
        if path.exists():
            raise ValueError("preexisting batch artifact: " + str(path))


def validate_batch(spec_path, runs, row=None):
    """Check the whole frozen input set; check only selected freshness at runtime.

    Root ancestors above the caller's explicit --runs directory may be ordinary
    site mount aliases. The runs directory and every relevant path below it must
    be real, contained paths, never symlinks/junctions. Shell atomic mkdir and
    noclobber remain necessary to close races after this read-only check.
    """
    spec = load_spec(spec_path)
    if row is not None and (type(row) is not int or not 1 <= row <= len(spec["jobs"])):
        raise ValueError("row must be a one-based index within jobs")
    supplied = Path(runs).absolute()
    if _is_link(supplied) or not supplied.is_dir():
        raise ValueError("runs must be an existing real directory")
    root = supplied.resolve(strict=True)
    manifest = _path(root, spec["manifest"][len("runs/"):])
    raw_manifest = _read_file(manifest)
    _matches(raw_manifest, spec["manifest_sha256"], "manifest")
    if b"\r" in raw_manifest or b"\x00" in raw_manifest or not raw_manifest.endswith(b"\n"):
        raise ValueError("manifest must be LF text with a final newline")
    text = raw_manifest.decode("utf-8")
    if "NOT LICENSED" in text.upper():
        raise ValueError("manifest is NOT LICENSED")
    expected_header = f"# NP={spec['np']} NCONC={spec['concurrency']}"
    resource_comments = [
        line for line in text.splitlines()
        if line.lstrip().startswith("#") and re.search(r"\b(?:NP|NCONC)\s*=", line, re.I)
    ]
    if resource_comments != [expected_header]:
        raise ValueError("manifest requires exactly one standalone resource header: " + expected_header)
    expected_rows = [f"{j['dir']} {j['job']} {j['suffix']} {j['nk']}" for j in spec["jobs"]]
    actual_rows = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if actual_rows != expected_rows:
        raise ValueError("manifest rows differ from the exact ordered spec")
    lines = _path(root, spec["manifest"][len("runs/"):] + ".lines")
    if _read_file(lines) != ("\n".join(expected_rows) + "\n").encode("utf-8"):
        raise ValueError("manifest .lines differs from exact canonical rows")
    for job in spec["jobs"]:
        deck = _path(root, job["dir"] + "/" + job["job"] + job["suffix"])
        _matches(_read_file(deck), job["sha256"], job["job"])
    for job in spec["jobs"] if row is None else [spec["jobs"][row - 1]]:
        _fresh(root, job)
    return {"rows": expected_rows, "selected_row": None if row is None else expected_rows[row - 1]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--row", type=int)
    args = parser.parse_args(argv)
    try:
        result = validate_batch(args.spec, args.runs, args.row)
    except (OSError, ValueError) as exc:
        print("REFUSE: " + str(exc), file=sys.stderr)
        return 2
    print(result["selected_row"] if args.row is not None else "VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
