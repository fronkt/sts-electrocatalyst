"""Four bounded, matched-source HEA solver probes; Python 3.9 compatible.

The two immutable failed follow-up densities seed independent precision and
mixing probes. A useful residual history is not an accepted SCF result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

try:
    from . import hea_numerical_guard as frozen
    from . import hea_followup_qc as qc
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import hea_numerical_guard as frozen
    import hea_followup_qc as qc

DIRECTORY = "hea/convergence_probe_2026-09-10"
MANIFEST = "runs/hea/m_convergence_probe_2026-09-10.txt"
SOURCE_SPEC = "results/hea_numerical_2026-09-08/launch_spec.json"
SOURCE_SPEC_SHA256 = "3326e14e7b25ec0d84576f42b7f3eaf11bff53b36f33b8a7d9416cd96758406a"
SOURCES = (
    "hn__leader_builder__ortho__recover_metal_alternating",
    "hn__leader_pull2.10__ortho__recover_baseline",
)
EXPECTED = [("hp__" + source[4:] + "__" + arm, source, arm)
            for arm in ("precision", "mixing") for source in SOURCES]
SPEC_KEYS = {"schema", "manifest", "manifest_sha256", "np", "concurrency",
             "wall_hours", "source_spec", "source_spec_sha256", "jobs"}
JOB_KEYS = {"job", "dir", "suffix", "nk", "sha256", "prefix", "source_job", "arm"}


def render_deck(raw, job):
    """Only named solver settings, private outdir and explicit bounds may differ."""
    text = raw.decode("utf-8")
    changes = {"outdir": "'./tmp_" + job["job"] + "'",
               "max_seconds": "3300", "electron_maxstep": "60"}
    if job["arm"] == "mixing":
        changes["mixing_beta"] = "0.05"
    for key, value in changes.items():
        frozen._assignment(text, key)
        text, count = re.subn(r"(?m)^(\s*" + re.escape(key) + r"\s*=\s*)[^\n]+$",
                              lambda match: match[1] + value, text)
        if count != 1:
            raise ValueError("cannot replace unique setting: " + key)
    extra = ("  diago_thr_init = 1.0d-10\n  diago_full_acc = .true.\n"
             if job["arm"] == "precision" else "  mixing_ndim = 12\n")
    if text.count("&ELECTRONS\n") != 1:
        raise ValueError("unique ELECTRONS namelist required")
    return text.replace("&ELECTRONS\n", "&ELECTRONS\n" + extra).encode("utf-8")


def load_bundle(spec_path, runs):
    supplied = Path(runs).absolute()
    if frozen._link(supplied) or not supplied.is_dir():
        raise ValueError("real runs directory required")
    root = supplied.resolve(strict=True)
    spec = frozen._json(frozen._read(Path(spec_path)))
    frozen._keys(spec, SPEC_KEYS, "probe spec")
    if (spec["schema"] != "hea_convergence_probe_v1" or spec["manifest"] != MANIFEST
            or spec["source_spec"] != SOURCE_SPEC or spec["source_spec_sha256"] != SOURCE_SPEC_SHA256):
        raise ValueError("unexpected frozen probe identity")
    for key, expected in (("np", 128), ("concurrency", 1), ("wall_hours", 1)):
        if type(spec[key]) is not int or spec[key] != expected:
            raise ValueError("unexpected probe resources: " + key)
    frozen._sha(spec["manifest_sha256"])
    source_raw = frozen._read(frozen._path(root.parent, SOURCE_SPEC))
    if frozen._digest(source_raw) != SOURCE_SPEC_SHA256:
        raise ValueError("original numerical spec differs")
    source_spec = frozen.validate_spec(frozen._json(source_raw))
    inventory_raw = frozen._read(frozen._path(root.parent, source_spec["source_checkpoints"]))
    if frozen._digest(inventory_raw) != source_spec["source_checkpoints_sha256"]:
        raise ValueError("original source inventory differs")
    checkpoints = frozen.validate_inventory(frozen._json(inventory_raw), source_spec)
    originals = {job["job"]: job for job in source_spec["jobs"]}
    if not isinstance(spec["jobs"], list) or len(spec["jobs"]) != 4:
        raise ValueError("exactly four probe jobs required")
    for job, (name, source, arm) in zip(spec["jobs"], EXPECTED):
        frozen._keys(job, JOB_KEYS, "probe job")
        parent = originals[source]
        if (job["job"] != name or job["source_job"] != source or job["arm"] != arm
                or job["dir"] != DIRECTORY or job["suffix"] != ".in"
                or type(job["nk"]) is not int or job["nk"] != 8
                or job["prefix"] != parent["prefix"] or parent["mode"] != "recovery"):
            raise ValueError("probe job differs from ordered matched-source design")
        frozen._sha(job["sha256"])
        original = frozen._read(frozen._path(root, parent["dir"] + "/" + source + ".in"))
        if frozen._digest(original) != parent["sha256"]:
            raise ValueError("original recovery input differs")
        frozen.validate_deck(original, parent)
        deck = frozen._read(frozen._path(root, DIRECTORY + "/" + name + ".in"))
        if frozen._digest(deck) != job["sha256"] or deck != render_deck(original, job):
            raise ValueError("probe input differs from permitted exact transformation")
    raw = frozen._read(frozen._path(root.parent, MANIFEST))
    if frozen._digest(raw) != spec["manifest_sha256"] or b"\r" in raw or not raw.endswith(b"\n"):
        raise ValueError("probe manifest differs")
    text = raw.decode("utf-8")
    headers = [line for line in text.splitlines() if line.startswith("#")
               and re.search(r"\b(?:NP|NCONC)\s*=", line, re.I)]
    if "NOT LICENSED" in text.upper() or headers != ["# NP=128 NCONC=1"]:
        raise ValueError("probe resource/authorization header invalid")
    rows = [DIRECTORY + " " + j["job"] + " .in 8" for j in spec["jobs"]]
    if [line for line in text.splitlines() if line and not line.startswith("#")] != rows:
        raise ValueError("ordered manifest rows differ")
    if frozen._read(frozen._path(root.parent, MANIFEST + ".lines")) != ("\n".join(rows) + "\n").encode():
        raise ValueError("manifest lines differ")
    return dict(root=root, spec=spec, source_spec=source_spec, checkpoints=checkpoints)


def select(ctx, row):
    if type(row) is not int or not 1 <= row <= 4:
        raise ValueError("row must be one-based index 1..4")
    return ctx["spec"]["jobs"][row-1]


def member(ctx, job, suffix):
    return frozen._path(ctx["root"], DIRECTORY + "/" + job["job"] + suffix)


def validate_batch(spec_path, runs, row=None):
    ctx = load_bundle(spec_path, runs)
    selected = ctx["spec"]["jobs"] if row is None else [select(ctx, row)]
    for job in selected:
        frozen._fresh(ctx["root"], job)
        for suffix in (".history.json", ".probe.json"):
            if member(ctx, job, suffix).exists():
                raise ValueError("probe result already exists")
        frozen.verify_source(ctx["root"], ctx["checkpoints"][job["prefix"]])
    return ctx


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def receipt(ctx, job):
    checkpoint = ctx["checkpoints"][job["prefix"]]
    return dict(schema="hea_convergence_probe_clone_v1", job=job["job"],
                source_job=job["source_job"], prefix=job["prefix"], arm=job["arm"],
                source=checkpoint["dir"], destination=DIRECTORY + "/tmp_" + job["job"] + "/" + job["prefix"] + ".save",
                input_sha256=job["sha256"], source_spec_sha256=SOURCE_SPEC_SHA256,
                source_checkpoints_sha256=ctx["source_spec"]["source_checkpoints_sha256"],
                files=checkpoint["files"])


def prepare_row(spec_path, runs, row):
    ctx = validate_batch(spec_path, runs, row)
    job = select(ctx, row)
    checkpoint = ctx["checkpoints"][job["prefix"]]
    source = frozen._path(ctx["root"], checkpoint["dir"])
    scratch = frozen._path(ctx["root"], DIRECTORY + "/tmp_" + job["job"])
    scratch.mkdir()
    destination = scratch / (job["prefix"] + ".save")
    destination.mkdir()
    for entry in checkpoint["files"]:
        src, dst = frozen._path(source, entry["path"]), frozen._path(destination, entry["path"])
        digest, size = hashlib.sha256(), 0
        with src.open("rb") as reader, dst.open("xb") as writer:
            for chunk in iter(lambda: reader.read(frozen.CHUNK), b""):
                writer.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        expected = (entry["size_bytes"], entry["sha256"])
        if (size, digest.hexdigest()) != expected or frozen._stream_hash(dst) != expected:
            raise ValueError("checkpoint clone differs; partial scratch retained")
    frozen.verify_source(ctx["root"], checkpoint)
    runtime = frozen._read(member(ctx, job, ".in"))
    if frozen._digest(runtime) != job["sha256"]:
        raise ValueError("input changed during clone")
    with member(ctx, job, ".run.in").open("xb") as handle:
        handle.write(runtime)
    write_json(member(ctx, job, ".clone_receipt.json"), receipt(ctx, job))
    return ctx


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][-+]?\d+)?"


def history(text):
    """Keep incomplete terminal iterations explicit; never treat them as convergence."""
    rows = []
    for block in re.split(r"(?m)^\s*iteration #\s*", text)[1:]:
        found = re.match(r"(\d+)", block)
        if found is None:
            raise ValueError("unreadable SCF iteration number")
        row = {"iteration": int(found[1])}
        fields = {"estimated_accuracy_ry": r"estimated scf accuracy\s*<\s*",
                  "total_energy_ry": r"(?m)^\s*!?\s*total energy\s*=\s*",
                  "total_magnetization_muB": r"total magnetization\s*=\s*",
                  "absolute_magnetization_muB": r"absolute magnetization\s*=\s*",
                  "diagonalization_threshold_ry": r"ethr\s*=\s*",
                  "average_diagonalization_iterations": r"avg # of iterations\s*=\s*"}
        for key, pattern in fields.items():
            match = re.search(pattern + "(" + NUMBER + ")", block)
            value = None if match is None else float(match[1].replace("D", "e").replace("d", "e"))
            if value is not None and not math.isfinite(value):
                raise ValueError("nonfinite SCF history value")
            row[key] = value
        row["complete"] = all(row[key] is not None for key in
                               ("estimated_accuracy_ry", "total_energy_ry", "total_magnetization_muB", "absolute_magnetization_muB"))
        rows.append(row)
    numbers = [row["iteration"] for row in rows]
    if numbers != list(range(1, len(rows)+1)) or len(rows) > 60:
        raise ValueError("unexpected SCF iteration sequence or probe bound")
    return rows


def summarize(spec_path, runs, row, scf_exit, projection_exit=None):
    ctx = load_bundle(spec_path, runs)
    job = select(ctx, row)
    errors = []
    if type(scf_exit) is not int or (projection_exit is not None and type(projection_exit) is not int):
        raise ValueError("integer process exit status required")
    if frozen._digest(frozen._read(member(ctx, job, ".run.in"))) != job["sha256"]:
        errors.append("runtime input differs")
    if frozen._json(frozen._read(member(ctx, job, ".clone_receipt.json"))) != receipt(ctx, job):
        errors.append("checkpoint clone receipt differs")
    output_raw = frozen._read(member(ctx, job, ".out"))
    output = output_raw.decode("utf-8", errors="replace")
    rows = history(output)
    write_json(member(ctx, job, ".history.json"), dict(schema="hea_convergence_history_v1", job=job["job"],
               output_sha256=frozen._digest(output_raw), iterations=rows))
    if not rows or not any(row["complete"] for row in rows):
        errors.append("complete SCF iteration history absent")
    try:
        frozen.validate_startup(output, "recovery")
    except ValueError as exc:
        errors.append(str(exc))
    projection = member(ctx, job, ".projwfc.out") if projection_exit is not None else None
    audit = qc.audit_files(member(ctx, job, ".run.in"), member(ctx, job, ".out"), projection)
    saved = frozen._path(ctx["root"], DIRECTORY + "/tmp_" + job["job"] + "/" + job["prefix"] + ".save")
    missing = [name for name in sorted(frozen.PORTABLE_FILES | frozen.WFC_FILES)
               if not frozen._path(saved, name).is_file() or frozen._path(saved, name).stat().st_size <= 0]
    accepted = scf_exit == 0 and projection_exit == 0 and not errors and not missing and audit["status"] == "COMPLETE"
    capped = ("Maximum CPU time exceeded" in output
              or bool(re.search(r"convergence NOT achieved after\s+60\s+iterations", output)))
    record = dict(schema="hea_convergence_probe_result_v1", job=job["job"], source_job=job["source_job"],
                  arm=job["arm"], scientific_status="COMPLETE" if accepted else "REJECTED",
                  diagnostic_status="ACCEPTED_ENDPOINT" if accepted else "CAPPED_NONCONVERGENCE" if capped else "OTHER_REJECTION",
                  diagnostic_history_available=bool(rows), complete_iterations=sum(r["complete"] for r in rows),
                  scf_exit=scf_exit, projection_exit=projection_exit, qc_status=audit["status"],
                  qc_reasons=audit["reasons"], evidence_errors=errors, retained_missing=missing,
                  original_failed_attempt_reclassified=False)
    write_json(member(ctx, job, ".probe.json"), record)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--runs", required=True, type=Path)
    parser.add_argument("--row", type=int)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--summarize", action="store_true")
    parser.add_argument("--scf-exit", type=int)
    parser.add_argument("--projection-exit", type=int)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.require_complete and not args.summarize:
            raise ValueError("--require-complete requires --summarize")
        if args.summarize:
            result = summarize(args.spec, args.runs, args.row, args.scf_exit, args.projection_exit)
            print(json.dumps(result, sort_keys=True))
            return 2 if args.require_complete and result["scientific_status"] != "COMPLETE" else 0
        ctx = (prepare_row(args.spec, args.runs, args.row) if args.prepare
               else validate_batch(args.spec, args.runs, args.row))
        if args.row is None:
            print("VALID")
        else:
            job = select(ctx, args.row)
            print(" ".join((job["dir"], job["job"], job["suffix"], str(job["nk"]), job["prefix"], job["arm"])))
    except (OSError, ValueError) as exc:
        print("REFUSE: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
