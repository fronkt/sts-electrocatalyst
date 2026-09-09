"""Frozen six-job numerical batch and independent checkpoint cloning.

The shell caller pins this file, the spec and QC helpers. No path in the source
checkpoint is opened for writing. A failed preparation keeps its partial clone.
Python 3.9 and the standard library suffice.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

SCHEMA = "hea_numerical_v1"
SOURCE_SCHEMA = "hea_numerical_sources_v1"
MANIFEST = "runs/hea/m_numerical_2026-09-08.txt"
INVENTORY = "results/hea_numerical_2026-09-08/source_checkpoints.json"
DIRECTORY = "hea/numerical_2026-09-08"
SOURCE_DIRECTORY = "hea/controls_2026-09-07"
PSEUDO_DIRECTORY = "/anvil/projects/x-che260157/pseudo"
SPEC_KEYS = {"schema", "manifest", "manifest_sha256", "np", "concurrency",
             "wall_hours", "source_checkpoints", "source_checkpoints_sha256", "jobs"}
JOB_KEYS = {"job", "dir", "suffix", "nk", "sha256", "prefix", "mode"}
PORTABLE_FILES = {"data-file-schema.xml", "charge-density.hdf5", "occup.txt", "paw.txt"}
WFC_FILES = {"wfc" + spin + str(k) + ".hdf5" for spin in ("up", "dw") for k in range(1, 9)}
CHUNK = 8 * 1024 * 1024


def _keys(value, expected, context):
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(context + ": unexpected keys")


def _sha(value):
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("lowercase SHA256 required")


def _token(value, prefix):
    if not isinstance(value, str) or re.fullmatch(prefix + r"[A-Za-z0-9][A-Za-z0-9_.-]*", value) is None:
        raise ValueError("unsafe job/prefix token")


def _relative(value):
    if not isinstance(value, str) or not value:
        raise ValueError("empty relative path")
    parts = value.split("/")
    if any(p in ("", ".", "..") or re.fullmatch(r"[A-Za-z0-9_.-]+", p) is None for p in parts):
        raise ValueError("unsafe relative path")
    return parts


def _link(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def _path(root, relative):
    path = root
    for part in _relative(relative):
        path = path / part
        if _link(path):
            raise ValueError("symlink/junction in checkpoint path: " + str(path))
        if path.exists():
            try:
                path.resolve(strict=True).relative_to(root)
            except ValueError as exc:
                raise ValueError("path escapes trusted root") from exc
    return path


def _read(path):
    if not path.is_file():
        raise ValueError("required regular file absent: " + str(path))
    return path.read_bytes()


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key: " + key)
        out[key] = value
    return out


def _nonfinite(value):
    raise ValueError("nonfinite JSON constant: " + value)


def _json(raw):
    return json.loads(raw, object_pairs_hook=_unique, parse_constant=_nonfinite)


def validate_spec(spec):
    _keys(spec, SPEC_KEYS, "spec")
    if spec["schema"] != SCHEMA or spec["manifest"] != MANIFEST or spec["source_checkpoints"] != INVENTORY:
        raise ValueError("unexpected frozen spec identity")
    for field, expected in (("np", 128), ("concurrency", 1), ("wall_hours", 4)):
        if type(spec[field]) is not int or spec[field] != expected:
            raise ValueError(field + " differs from approved resources")
    _sha(spec["manifest_sha256"])
    _sha(spec["source_checkpoints_sha256"])
    if not isinstance(spec["jobs"], list) or len(spec["jobs"]) != 6:
        raise ValueError("exactly six jobs required")
    jobs, prefixes, modes = set(), set(), []
    for job in spec["jobs"]:
        _keys(job, JOB_KEYS, "job")
        _token(job["job"], "hn__")
        _token(job["prefix"], "hc__")
        if job["dir"] != DIRECTORY or job["suffix"] != ".in" or type(job["nk"]) is not int or job["nk"] != 8:
            raise ValueError("unexpected job directory, suffix or nk")
        if job["mode"] not in ("tight", "recovery"):
            raise ValueError("unknown numerical mode")
        _sha(job["sha256"])
        if job["job"] in jobs or job["prefix"] in prefixes:
            raise ValueError("duplicate job or source prefix")
        jobs.add(job["job"])
        prefixes.add(job["prefix"])
        modes.append(job["mode"])
    if modes.count("tight") != 4 or modes.count("recovery") != 2:
        raise ValueError("exactly four tight and two recovery jobs required")
    return spec


def validate_inventory(inventory, spec):
    _keys(inventory, {"schema", "checkpoints"}, "inventory")
    if inventory["schema"] != SOURCE_SCHEMA or not isinstance(inventory["checkpoints"], list):
        raise ValueError("unexpected checkpoint inventory")
    expected = {job["prefix"]: job["mode"] for job in spec["jobs"]}
    found = {}
    for item in inventory["checkpoints"]:
        _keys(item, {"prefix", "dir", "files"}, "checkpoint")
        prefix = item["prefix"]
        _token(prefix, "hc__")
        if prefix not in expected or prefix in found:
            raise ValueError("unexpected or duplicate source prefix")
        if item["dir"] != SOURCE_DIRECTORY + "/tmp_" + prefix + "/" + prefix + ".save":
            raise ValueError("unexpected checkpoint directory")
        if not isinstance(item["files"], list) or not item["files"]:
            raise ValueError("checkpoint files must be nonempty")
        names = []
        for entry in item["files"]:
            _keys(entry, {"path", "size_bytes", "sha256"}, "checkpoint file")
            _relative(entry["path"])
            if type(entry["size_bytes"]) is not int or entry["size_bytes"] < 0:
                raise ValueError("invalid checkpoint file size")
            _sha(entry["sha256"])
            names.append(entry["path"])
        if names != sorted(set(names)):
            raise ValueError("checkpoint paths must be sorted and unique")
        nonempty = {e["path"] for e in item["files"] if e["size_bytes"] > 0}
        if not PORTABLE_FILES.issubset(nonempty):
            raise ValueError("nonempty XML/density/occup/paw checkpoint required")
        if expected[prefix] == "tight" and not WFC_FILES.issubset(nonempty):
            raise ValueError("all sixteen spin/k-point wavefunction files required")
        if expected[prefix] == "recovery" and set(names) != PORTABLE_FILES:
            raise ValueError("recovery source must contain exactly four portable files")
        found[prefix] = item
    if set(found) != set(expected):
        raise ValueError("inventory must match all six source prefixes")
    return found


def _assignment(text, key):
    matches = re.findall(r"(?im)^\s*" + re.escape(key) + r"\s*=\s*([^!\n]+)", text)
    if len(matches) != 1:
        raise ValueError("input requires exactly one assignment: " + key)
    return matches[0].strip().rstrip(",").strip()


def validate_deck(raw, job):
    if b"\r" in raw or b"\x00" in raw or not raw.endswith(b"\n"):
        raise ValueError("input must be LF text with final newline")
    text = raw.decode("utf-8")
    tight = job["mode"] == "tight"
    expected = {"calculation": "scf", "prefix": job["prefix"], "restart_mode": "from_scratch",
                "startingpot": "file", "startingwfc": "file" if tight else "atomic+random",
                "outdir": "./tmp_" + job["job"], "pseudo_dir": PSEUDO_DIRECTORY}
    for key, value in expected.items():
        if _assignment(text, key) != "'" + value + "'":
            raise ValueError("input differs from approved " + key)
    for key, value in (("conv_thr", 1e-8 if tight else 1e-6),
                       ("mixing_beta", 0.3 if tight else 0.1), ("max_seconds", 13200.0)):
        try:
            actual = float(_assignment(text, key).replace("d", "e").replace("D", "E"))
        except ValueError as exc:
            raise ValueError("invalid numerical assignment: " + key) from exc
        if actual != value:
            raise ValueError("input differs from approved " + key)
    for key in ("outdir", "pseudo_dir"):
        if re.fullmatch(r"'[^'\n]+'", _assignment(text, key)) is None:
            raise ValueError("input requires single quoted " + key)


def _fresh(root, job):
    base = job["dir"] + "/"
    names = [job["job"] + suffix for suffix in
             (".out", ".projwfc.out", ".run.in", ".projwfc.in", ".scf_qc.json",
              ".qc.json", ".lowdin.txt", ".clone_receipt.json", ".KILLED")]
    names += ["tmp_" + job["job"], "dens/" + job["prefix"] + ".save"]
    for name in names:
        if _path(root, base + name).exists():
            raise ValueError("preexisting numerical artifact: " + name)


def _source_files(source):
    if not source.is_dir() or _link(source):
        raise ValueError("checkpoint source must be a real directory")
    found = []
    for base, directories, files in os.walk(str(source), followlinks=False):
        for name in directories + files:
            member = Path(base) / name
            if _link(member):
                raise ValueError("link in source checkpoint")
            if member.is_file():
                found.append(member.relative_to(source).as_posix())
            elif not member.is_dir():
                raise ValueError("nonregular checkpoint member")
    return sorted(found)


def _stream_hash(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def verify_source(root, checkpoint):
    source = _path(root, checkpoint["dir"])
    if _source_files(source) != [e["path"] for e in checkpoint["files"]]:
        raise ValueError("source checkpoint members differ from inventory")
    for entry in checkpoint["files"]:
        if _stream_hash(_path(source, entry["path"])) != (entry["size_bytes"], entry["sha256"]):
            raise ValueError("source checkpoint hash/size mismatch: " + entry["path"])
    return source


def validate_batch(spec_path, runs, row=None):
    spec = validate_spec(_json(_read(Path(spec_path))))
    if row is not None and (type(row) is not int or not 1 <= row <= 6):
        raise ValueError("row must be one-based index 1..6")
    supplied = Path(runs).absolute()
    if _link(supplied) or not supplied.is_dir():
        raise ValueError("runs must be an existing real directory")
    root = supplied.resolve(strict=True)
    inventory_raw = _read(_path(root.parent, spec["source_checkpoints"]))
    if _digest(inventory_raw) != spec["source_checkpoints_sha256"]:
        raise ValueError("source inventory SHA256 mismatch")
    checkpoints = validate_inventory(_json(inventory_raw), spec)
    raw = _read(_path(root, spec["manifest"][5:]))
    if _digest(raw) != spec["manifest_sha256"]:
        raise ValueError("manifest SHA256 mismatch")
    if b"\r" in raw or b"\x00" in raw or not raw.endswith(b"\n"):
        raise ValueError("manifest must be LF text with final newline")
    text = raw.decode("utf-8")
    if "NOT LICENSED" in text.upper():
        raise ValueError("manifest is NOT LICENSED")
    headers = [line for line in text.splitlines() if line.lstrip().startswith("#")
               and re.search(r"\b(?:NP|NCONC)\s*=", line, re.I)]
    if headers != ["# NP=128 NCONC=1"]:
        raise ValueError("exactly one standalone resource header required")
    rows = [f"{j['dir']} {j['job']} {j['suffix']} {j['nk']}" for j in spec["jobs"]]
    if [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")] != rows:
        raise ValueError("manifest rows differ from exact ordered spec")
    if _read(_path(root, spec["manifest"][5:] + ".lines")) != ("\n".join(rows) + "\n").encode():
        raise ValueError("manifest .lines differs from ordered spec")
    for job in spec["jobs"]:
        deck = _read(_path(root, job["dir"] + "/" + job["job"] + ".in"))
        if _digest(deck) != job["sha256"]:
            raise ValueError("input SHA256 mismatch: " + job["job"])
        validate_deck(deck, job)
    selected = spec["jobs"] if row is None else [spec["jobs"][row - 1]]
    for job in selected:
        _fresh(root, job)
    for job in selected:
        verify_source(root, checkpoints[job["prefix"]])
    return {"spec": spec, "root": root, "checkpoints": checkpoints,
            "selected": None if row is None else selected[0]}


def prepare_row(spec_path, runs, row):
    checked = validate_batch(spec_path, runs, row)
    job, root = checked["selected"], checked["root"]
    checkpoint = checked["checkpoints"][job["prefix"]]
    source = _path(root, checkpoint["dir"])
    scratch = _path(root, job["dir"] + "/tmp_" + job["job"])
    scratch.mkdir()  # Exclusive ownership: no parents/exist_ok and no cleanup on error.
    destination = scratch / (job["prefix"] + ".save")
    destination.mkdir()
    copied = []
    for entry in checkpoint["files"]:
        src = _path(source, entry["path"])
        dst = _path(destination, entry["path"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        digest, size = hashlib.sha256(), 0
        with src.open("rb") as reader, dst.open("xb") as writer:
            for chunk in iter(lambda: reader.read(CHUNK), b""):
                writer.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        if (size, digest.hexdigest()) != (entry["size_bytes"], entry["sha256"]):
            raise ValueError("clone hash/size mismatch; partial scratch preserved")
        # A readback validates bytes on the destination, not only the source stream.
        if _stream_hash(dst) != (entry["size_bytes"], entry["sha256"]):
            raise ValueError("clone readback mismatch; partial scratch preserved")
        copied.append(dict(entry))
    if _source_files(source) != [e["path"] for e in checkpoint["files"]]:
        raise ValueError("source members changed during clone; partial scratch preserved")
    # Clone I/O can be long. Recheck the selected input and publish only those
    # verified bytes, so the runner never reopens a live unverified input for sed.
    runtime_bytes = _read(_path(root, job["dir"] + "/" + job["job"] + ".in"))
    if _digest(runtime_bytes) != job["sha256"]:
        raise ValueError("input changed during clone; partial scratch preserved")
    runtime_path = _path(root, job["dir"] + "/" + job["job"] + ".run.in")
    with runtime_path.open("xb") as handle:
        handle.write(runtime_bytes)
    receipt = {"schema": "hea_numerical_clone_v1", "job": job["job"], "prefix": job["prefix"],
               "mode": job["mode"], "source": checkpoint["dir"],
               "destination": destination.relative_to(root).as_posix(),
               "source_checkpoints_sha256": checked["spec"]["source_checkpoints_sha256"],
               "files": copied}
    receipt_path = _path(root, job["dir"] + "/" + job["job"] + ".clone_receipt.json")
    with receipt_path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    return checked


def validate_startup(text, mode):
    """Require positive QE 7.5 startup evidence matching the frozen mode."""
    if mode not in ("tight", "recovery"):
        raise ValueError("unknown startup mode")
    density = len(re.findall(r"The initial density is read from file", text))
    file_wfc = len(re.findall(r"Starting wfcs from file", text))
    atomic = len(re.findall(r"Starting wfcs are\s+\d+ randomized atomic wfcs", text))
    if density != 1 or re.search(r"Cannot\s+read\s+rho\b", text, re.I):
        raise ValueError("startup did not establish density-file read")
    if mode == "tight":
        fallback = re.search(r"Cannot\s+read\s+wfcs\b|Wavefunctions\s+not\s+found|"
                             r"recomputing\s+them\s+from\s+scratch|"
                             r"Starting wfcs?.*(?:atomic|random)", text, re.I)
        if file_wfc != 1 or atomic != 0 or fallback:
            raise ValueError("startup did not establish wavefunction-file read without fallback")
    elif atomic != 1 or file_wfc != 0:
        raise ValueError("startup did not establish randomized atomic wavefunctions")
    return {"status": "VALID_STARTUP", "mode": mode, "density_file_reads": density,
            "wavefunction_file_reads": file_wfc, "randomized_atomic_starts": atomic}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--runs", type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--row", type=int)
    selection.add_argument("--prepare-row", type=int)
    parser.add_argument("--startup-output", type=Path)
    parser.add_argument("--mode", choices=("tight", "recovery"))
    args = parser.parse_args(argv)
    try:
        if args.startup_output is not None:
            if args.mode is None or any(v is not None for v in (args.spec, args.runs, args.row, args.prepare_row)):
                raise ValueError("startup check requires only --startup-output and --mode")
            result = validate_startup(_read(args.startup_output).decode("utf-8"), args.mode)
            print(json.dumps(result, sort_keys=True))
            return 0
        if args.spec is None or args.runs is None or args.mode is not None:
            raise ValueError("--spec and --runs required for batch validation")
        checked = (prepare_row(args.spec, args.runs, args.prepare_row)
                   if args.prepare_row is not None else validate_batch(args.spec, args.runs, args.row))
    except (OSError, ValueError) as exc:
        print("REFUSE: " + str(exc), file=sys.stderr)
        return 2
    job = checked["selected"]
    print("VALID" if job is None else
          f"{job['dir']} {job['job']} {job['suffix']} {job['nk']} {job['prefix']} {job['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
