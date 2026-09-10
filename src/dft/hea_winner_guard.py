"""Check the eight fixed historical-winner SCFs without changing source evidence.

Source and destination inputs are byte-identical. Runtime changes are limited to
three operational assignments. No calculation, restart or deletion occurs here.
The caller pins this module, its shared helpers and the spec before invocation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hea_followup_guard as common

SCHEMA = "hea_winner_v1"
MANIFEST = "runs/hea/m_winner_2026-09-10.txt"
DIRECTORY = "hea/winner_2026-09-10"
SOURCE_DIRECTORY = "hea/validation_2026-09-07"
PSEUDO_DIR = "/anvil/projects/x-che260157/pseudo"
REFERENCES = (
    "results/hea_validation_2026-09-07/plan.json",
    "results/hea_validation_2026-09-07/geometry_snapshot.json",
    "runs/hea/validation_2026-09-07/inventory.json",
)
GEOMETRIES = {
    "slab": "bd2523d558a6d76f7856eae53f3de623869b6bd1fb927bed3aaea5a06b693ba1",
    "OH": "132934a8907edb7d2ce224ae46c90eab5deb73395993e300b6aa499474f3a2b6",
    "O": "80ebe76a616d61d6fecca57d1cd6c2ef27990771fbc3db9a8cfea6a4bf228e5c",
    "OOH": "9a2ae68020203b9e4530466fdcb9881c5c84ec63fec7351b2f981336d0ef6b84",
}
SPEC_KEYS = {"schema", "manifest", "manifest_sha256", "np", "concurrency",
             "wall_hours", "memory_gb", "jobs", "references", "pseudopotentials"}
ROW_KEYS = {"job", "dir", "source", "suffix", "nk", "sha256", "state", "projector"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=common._unique_object,
                      parse_constant=common._invalid_constant)


def validate_spec(spec):
    common._keys(spec, SPEC_KEYS, "winner spec")
    if spec["schema"] != SCHEMA or spec["manifest"] != MANIFEST:
        raise ValueError("unsupported winner schema or manifest")
    for key, value in (("np", 128), ("concurrency", 1), ("wall_hours", 4), ("memory_gb", 237)):
        if type(spec[key]) is not int or spec[key] != value:
            raise ValueError(key + " differs from the bounded allocation")
    common._hash(spec["manifest_sha256"], "manifest")
    if not isinstance(spec["jobs"], list) or len(spec["jobs"]) != 8:
        raise ValueError("exactly eight winner jobs required")
    for row, (state, projector) in zip(spec["jobs"],
            ((state, projector) for state in GEOMETRIES for projector in ("atomic", "ortho"))):
        common._keys(row, ROW_KEYS, "winner row")
        expected = "g_" + GEOMETRIES[state] + "__" + projector
        if (row["job"], row["state"], row["projector"], row["dir"], row["source"],
                row["suffix"]) != (expected, state, projector, DIRECTORY,
                                  SOURCE_DIRECTORY + "/" + expected + ".in", ".in"):
            raise ValueError("winner selection or source identity differs")
        if type(row["nk"]) is not int or row["nk"] != 8:
            raise ValueError("winner requires exactly eight pools")
        common._hash(row["sha256"], expected)
    if not isinstance(spec["references"], list) or len(spec["references"]) != len(REFERENCES):
        raise ValueError("exact source references required")
    for reference, expected in zip(spec["references"], REFERENCES):
        common._keys(reference, {"path", "sha256"}, "reference")
        if reference["path"] != expected:
            raise ValueError("reference identity differs")
        common._hash(reference["sha256"], expected)
    if not isinstance(spec["pseudopotentials"], list) or len(spec["pseudopotentials"]) != 6:
        raise ValueError("six pseudopotential identities required")
    names = set()
    for pseudo in spec["pseudopotentials"]:
        common._keys(pseudo, {"path", "sha256"}, "pseudopotential")
        name = pseudo["path"]
        if not isinstance(name, str) or re.fullmatch(r"[A-Za-z0-9_.-]+\.(?:UPF|upf)", name) is None:
            raise ValueError("unsafe pseudopotential filename")
        common._hash(pseudo["sha256"], name)
        if name in names:
            raise ValueError("duplicate pseudopotential")
        names.add(name)
    return spec


def runtime_bytes(raw, job):
    """Change exactly outdir, pseudo_dir and the wall-time backstop."""
    if b"\r" in raw or b"\x00" in raw or not raw.endswith(b"\n"):
        raise ValueError("source deck must be LF text")
    text = raw.decode("utf-8")
    if text.count("  prefix = '" + job + "'\n") != 1:
        raise ValueError("source prefix differs")
    replacements = {
        "  outdir = './tmp'\n": "  outdir = './tmp_" + job + "'\n",
        "  pseudo_dir = '/usr/share/espresso/pseudo'\n": "  pseudo_dir = '" + PSEUDO_DIR + "'\n",
        "  max_seconds = 165000\n": "  max_seconds = 13200\n",
    }
    for source, target in replacements.items():
        if text.count(source) != 1:
            raise ValueError("expected one operational assignment: " + source.strip())
        text = text.replace(source, target)
    return text.encode("utf-8")


def _verify_references(root, spec):
    repo = root.parent
    for reference in spec["references"]:
        raw = common._read_file(common._path(repo, reference["path"]))
        common._matches(raw, reference["sha256"], reference["path"])
    inventory = read_json(repo / REFERENCES[2])
    aliases = [a for a in inventory["aliases"] if a["slot_id"] == "historical_leader_winner"]
    if len(aliases) != 8:
        raise ValueError("winner inventory denominator differs")
    expected = {(r["state"], r["projector"]): r for r in spec["jobs"]}
    if {(a["state"], a["projector"]) for a in aliases} != set(expected):
        raise ValueError("winner inventory selection differs")
    for alias in aliases:
        row = expected[(alias["state"], alias["projector"])]
        if (alias["target"], alias["geometry_sha256"], alias["split"], alias["slot_status"]) != (
                row["source"], GEOMETRIES[row["state"]], "targeted_audit", "ready"):
            raise ValueError("winner inventory source or readiness differs")


def validate_batch(spec_path, runs, row=None, *, fresh=True):
    spec = validate_spec(read_json(spec_path))
    if row is not None and (type(row) is not int or not 1 <= row <= 8):
        raise ValueError("row must be one-based within eight jobs")
    supplied = Path(runs).absolute()
    if common._is_link(supplied) or not supplied.is_dir():
        raise ValueError("runs must be an existing real directory")
    root = supplied.resolve(strict=True)
    _verify_references(root, spec)
    manifest = common._path(root, MANIFEST[len("runs/"):])
    raw = common._read_file(manifest)
    common._matches(raw, spec["manifest_sha256"], "manifest")
    if b"\r" in raw or b"\x00" in raw or not raw.endswith(b"\n"):
        raise ValueError("manifest must be LF text")
    text = raw.decode("utf-8")
    if "NOT LICENSED" in text.upper():
        raise ValueError("manifest retains obsolete unapproved notice")
    resource_headers = [line for line in text.splitlines() if line.lstrip().startswith("#")
                        and re.search(r"\b(?:NP|NCONC)\s*=", line, re.I)]
    if resource_headers != ["# NP=128 NCONC=1"]:
        raise ValueError("exact standalone resource header required")
    rows = [f"{r['dir']} {r['job']} .in 8" for r in spec["jobs"]]
    if [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")] != rows:
        raise ValueError("manifest differs from exact ordered winner rows")
    if common._read_file(common._path(root, MANIFEST[len("runs/"):] + ".lines")) != (
            "\n".join(rows) + "\n").encode():
        raise ValueError("manifest .lines differs")
    for entry in spec["jobs"]:
        source = common._read_file(common._path(root, entry["source"]))
        common._matches(source, entry["sha256"], "source " + entry["job"])
        dest = common._read_file(common._path(root, DIRECTORY + "/" + entry["job"] + ".in"))
        if dest != source:
            raise ValueError("isolated deck differs from frozen original")
        runtime_bytes(source, entry["job"])
        # An existing original attempt must not be rerun under the new location.
        common._fresh(root, dict(entry, dir=SOURCE_DIRECTORY))
    if fresh:
        for entry in spec["jobs"] if row is None else [spec["jobs"][row - 1]]:
            common._fresh(root, entry)
    return {"rows": rows, "selected_row": None if row is None else rows[row - 1], "spec": spec}


def verify_pseudopotentials(spec, directory):
    base = Path(directory).resolve(strict=True)
    for pseudo in spec["pseudopotentials"]:
        common._matches(common._read_file(common._path(base, pseudo["path"])),
                        pseudo["sha256"], pseudo["path"])


def verify_runtime(spec_path, runs, row):
    result = validate_batch(spec_path, runs, row, fresh=False)
    if row is None:
        raise ValueError("runtime verification requires --row")
    entry = result["spec"]["jobs"][row - 1]
    root = Path(runs).resolve(strict=True)
    expected = runtime_bytes(common._read_file(common._path(root, entry["source"])), entry["job"])
    actual = common._read_file(common._path(root, DIRECTORY + "/" + entry["job"] + ".run.in"))
    if actual != expected:
        raise ValueError("runtime input changes more than the three operational fields")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--row", type=int)
    parser.add_argument("--runtime", action="store_true")
    parser.add_argument("--pseudo-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        result = (verify_runtime(args.spec, args.runs, args.row) if args.runtime else
                  validate_batch(args.spec, args.runs, args.row))
        if args.pseudo_dir is not None:
            verify_pseudopotentials(result["spec"], args.pseudo_dir)
    except (OSError, ValueError, KeyError) as exc:
        print("REFUSE: " + str(exc), file=sys.stderr)
        return 2
    print(result["selected_row"] if args.row is not None else "VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
