"""One bounded smearing IEEE reproduction from the original accepted tight source.

The shell pins this module and the immutable sensitivity spec/helpers. Rank capture
changes logging only. Every stderr stream remains part of unchanged strict QC.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

try:
    from . import hea_numerical_guard as frozen
    from . import hea_followup_qc as qc
    from . import hea_sensitivity_guard as sources
except ImportError:  # Frozen QC also supports direct script invocation.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import hea_numerical_guard as frozen
    import hea_followup_qc as qc
    import hea_sensitivity_guard as sources

SPEC = "results/hea_sensitivity_2026-09-09/launch_spec.json"
DIRECTORY = "hea/ieee_smearing_2026-09-10"
MANIFEST = "runs/hea/m_ieee_smearing_2026-09-10.txt"
JOB = "hd__leader_pull2.10__ortho__smearing_repro"
SOURCE_JOB = "hn__leader_pull2.10__ortho__tight"
ORIGINAL_JOB = "hs__leader_pull2.10__ortho__smearing"
PREFIX = "hc__leader_pull2.10__ortho__fragment"
RANKS = 128


def context(runs):
    supplied = Path(runs).absolute()
    if frozen._link(supplied) or not supplied.is_dir():
        raise ValueError("runs must be an existing real directory")
    root = supplied.resolve(strict=True)
    spec_path = frozen._path(root.parent, SPEC)
    spec_raw = frozen._read(spec_path)
    # Validate frozen sensitivity decks, accepted input/XML/raw/QC hashes and
    # metadata. This does not require the earlier completed jobs to be fresh.
    checked = sources.load_bundle(spec_path, root)
    spec = checked["spec"]
    candidates = [job for job in spec["jobs"] if job["job"] == ORIGINAL_JOB]
    if len(candidates) != 1:
        raise ValueError("exact original smearing source job required")
    original_job = candidates[0]
    if (original_job["prefix"] != PREFIX or original_job["source_job"] != SOURCE_JOB
            or original_job["arm"] != "smearing"):
        raise ValueError("exact original smearing job and tight checkpoint required")
    checkpoint = checked["checkpoints"][SOURCE_JOB]
    directory = frozen._path(root, DIRECTORY)
    if not directory.is_dir():
        raise ValueError("isolated diagnostic directory absent")
    source_raw = frozen._read(frozen._path(root.parent, checkpoint["source_input"]))
    return dict(root=root, directory=directory, spec=spec, original_job=original_job,
                checkpoint=checkpoint, source_spec_sha256=frozen._digest(spec_raw),
                source_input=source_raw)


def _deck(ctx):
    raw = frozen._read(frozen._path(ctx["root"], DIRECTORY + "/" + JOB + ".in"))
    if frozen._digest(raw) != ctx["original_job"]["sha256"]:
        raise ValueError("diagnostic input must be byte-identical to original smearing input")
    sources.validate_deck(raw, ctx["source_input"], ctx["original_job"])
    return raw


def _manifest(ctx):
    raw = frozen._read(frozen._path(ctx["root"], MANIFEST[5:]))
    if b"\r" in raw or b"\x00" in raw or not raw.endswith(b"\n"):
        raise ValueError("manifest must use LF with final newline")
    text = raw.decode("utf-8")
    if "NOT LICENSED" in text.upper():
        raise ValueError("manifest is NOT LICENSED")
    headers = [line for line in text.splitlines() if line.lstrip().startswith("#")
               and re.search(r"\b(?:NP|NCONC)\s*=", line, re.I)]
    if headers != ["# NP=128 NCONC=1"]:
        raise ValueError("exact standalone resource header required")
    row = DIRECTORY + " " + JOB + " .in 8"
    if [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")] != [row]:
        raise ValueError("exactly one frozen diagnostic row required")
    if frozen._read(frozen._path(ctx["root"], MANIFEST[5:] + ".lines")) != (row + "\n").encode():
        raise ValueError("manifest .lines differs from exact row")


def stage_names(stage):
    if stage == "scf":
        return dict(stdout=JOB + ".stdout", launcher=JOB + ".launcher.stderr",
                    ranks=JOB + ".rank_stderr", combined=JOB + ".out",
                    audit=JOB + ".rank_audit.json")
    if stage == "projection":
        return dict(stdout=JOB + ".projwfc.stdout", launcher=JOB + ".projwfc.launcher.stderr",
                    ranks=JOB + ".projwfc.rank_stderr", combined=JOB + ".projwfc.out",
                    audit=JOB + ".projwfc.rank_audit.json")
    raise ValueError("unknown capture stage")


def _member(ctx, name):
    return frozen._path(ctx["root"], DIRECTORY + "/" + name)


def _fresh(ctx):
    names = [JOB + suffix for suffix in (".run.in", ".projwfc.in", ".scf_qc.json", ".qc.json",
                                        ".clone_receipt.json", ".diagnostic.json", ".KILLED")]
    names.append("tmp_" + ORIGINAL_JOB)
    for stage in ("scf", "projection"):
        names.extend(stage_names(stage).values())
    for name in names:
        if _member(ctx, name).exists():
            raise ValueError("preexisting diagnostic artifact: " + name)


def validate(runs):
    ctx = context(runs)
    _manifest(ctx)
    _deck(ctx)
    _fresh(ctx)
    frozen.verify_source(ctx["root"], ctx["checkpoint"])
    return ctx


def _write_json(path, record):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")


def prepare(runs):
    ctx = validate(runs)
    source = frozen._path(ctx["root"], ctx["checkpoint"]["dir"])
    scratch = _member(ctx, "tmp_" + ORIGINAL_JOB)
    scratch.mkdir()
    destination = scratch / (PREFIX + ".save")
    destination.mkdir()
    for entry in ctx["checkpoint"]["files"]:
        src = frozen._path(source, entry["path"])
        dst = frozen._path(destination, entry["path"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        digest, size = hashlib.sha256(), 0
        with src.open("rb") as reader, dst.open("xb") as writer:
            for chunk in iter(lambda: reader.read(frozen.CHUNK), b""):
                writer.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        expected = (entry["size_bytes"], entry["sha256"])
        if (size, digest.hexdigest()) != expected or frozen._stream_hash(dst) != expected:
            raise ValueError("clone hash/size mismatch; partial clone retained")
    if frozen._source_files(source) != [entry["path"] for entry in ctx["checkpoint"]["files"]]:
        raise ValueError("source members changed during clone")
    # Long copy operations must not reopen an unchecked live input for execution.
    runtime = _deck(ctx)
    with _member(ctx, JOB + ".run.in").open("xb") as handle:
        handle.write(runtime)
    _member(ctx, stage_names("scf")["ranks"]).mkdir()
    receipt = dict(schema="hea_ieee_smearing_clone_v1", job=JOB, source_job=SOURCE_JOB, original_job=ORIGINAL_JOB, prefix=PREFIX,
                   source=ctx["checkpoint"]["dir"],
                   destination=destination.relative_to(ctx["root"]).as_posix(),
                   input_sha256=frozen._digest(runtime),
                   source_spec_sha256=ctx["source_spec_sha256"],
                   source_checkpoints_sha256=ctx["spec"]["source_checkpoints_sha256"],
                   files=ctx["checkpoint"]["files"])
    _write_json(_member(ctx, JOB + ".clone_receipt.json"), receipt)
    return ctx


def capture_contents(ctx, stage):
    """Read every raw stream and reconstruct its exact combined view in memory."""
    names = stage_names(stage)
    rank_directory = _member(ctx, names["ranks"])
    if not rank_directory.is_dir():
        raise ValueError("rank stderr directory absent")
    expected_names = ["rank%03d.stderr" % rank for rank in range(RANKS)]
    actual_names = sorted(path.name for path in rank_directory.iterdir())
    if any(name not in expected_names for name in actual_names):
        raise ValueError("unexpected member in rank stderr directory")
    missing, rank_records, pieces = [], [], []
    raw_streams = {}
    for label, key in (("STDOUT", "stdout"), ("MPI_LAUNCHER_STDERR", "launcher")):
        raw = frozen._read(_member(ctx, names[key]))
        pieces.append((label, raw))
        raw_streams[names[key]] = frozen._digest(raw)
    for rank, name in enumerate(expected_names):
        path = frozen._path(rank_directory, name)
        if not path.exists():
            missing.append(rank)
            continue
        raw = frozen._read(path)
        pieces.append(("MPI_RANK_%03d_STDERR" % rank, raw))
        flags = sorted(set(re.findall(rb"IEEE_[A-Z_]+", raw)))
        rank_records.append(dict(rank=rank, bytes=len(raw), sha256=frozen._digest(raw),
                                 flags=[flag.decode("ascii") for flag in flags]))
    combined = pieces[0][1]
    if not combined.endswith(b"\n"):
        combined += b"\n"
    for label, raw in pieces[1:]:
        combined += ("\n# CAPTURE " + label + "\n").encode() + raw
        if not combined.endswith(b"\n"):
            combined += b"\n"
    record = dict(schema="hea_ieee_rank_capture_v1", stage=stage, expected_ranks=RANKS,
                  collection_complete=not missing, missing_ranks=missing, ranks=rank_records,
                  combined_sha256=frozen._digest(combined), raw_streams=raw_streams)
    return combined, record


def assemble(runs, stage):
    """Combine raw streams without removing any exception or warning line."""
    ctx = context(runs)
    names = stage_names(stage)
    combined, record = capture_contents(ctx, stage)
    with _member(ctx, names["combined"]).open("xb") as handle:
        handle.write(combined)
    _write_json(_member(ctx, names["audit"]), record)
    return record


def verify_capture(ctx, stage):
    combined, expected = capture_contents(ctx, stage)
    names = stage_names(stage)
    if frozen._read(_member(ctx, names["combined"])) != combined:
        raise ValueError(stage + " combined output differs from raw streams")
    stored = frozen._json(frozen._read(_member(ctx, names["audit"])))
    if stored != expected:
        raise ValueError(stage + " rank audit differs from raw streams")
    return combined, expected


def verify_clone_receipt(ctx):
    runtime = frozen._read(_member(ctx, JOB + ".run.in"))
    if frozen._digest(runtime) != ctx["original_job"]["sha256"]:
        raise ValueError("runtime input differs from frozen original")
    expected = dict(schema="hea_ieee_smearing_clone_v1", job=JOB, source_job=SOURCE_JOB, original_job=ORIGINAL_JOB, prefix=PREFIX,
                    source=ctx["checkpoint"]["dir"],
                    destination=DIRECTORY + "/tmp_" + ORIGINAL_JOB + "/" + PREFIX + ".save",
                    input_sha256=frozen._digest(runtime),
                    source_spec_sha256=ctx["source_spec_sha256"],
                    source_checkpoints_sha256=ctx["spec"]["source_checkpoints_sha256"],
                    files=ctx["checkpoint"]["files"])
    if frozen._json(frozen._read(_member(ctx, JOB + ".clone_receipt.json"))) != expected:
        raise ValueError("clone receipt differs from frozen source/input")


def summarize(runs, scf_exit, projection_exit=None):
    """Recheck raw evidence; keep diagnosis separate from new endpoint acceptance."""
    ctx = context(runs)
    if type(scf_exit) is not int or (projection_exit is not None and type(projection_exit) is not int):
        raise ValueError("integer process exits required")
    scf_errors, projection_errors = [], []
    try:
        verify_clone_receipt(ctx)
    except (OSError, ValueError, ET.ParseError) as exc:
        scf_errors.append(str(exc))
    output, rank_audit = "", None
    try:
        raw, rank_audit = verify_capture(ctx, "scf")
        output = raw.decode("utf-8", errors="replace")
        if rank_audit["collection_complete"] is not True:
            scf_errors.append("SCF rank capture incomplete")
    except (OSError, ValueError, ET.ParseError) as exc:
        scf_errors.append(str(exc))
    outpath = _member(ctx, JOB + ".out")
    try:
        scf_audit = qc.audit_files(_member(ctx, JOB + ".run.in"), outpath)
    except (OSError, ValueError, ET.ParseError) as exc:
        scf_audit = dict(status="REJECTED", reasons=[str(exc)])
    startup = None
    try:
        startup = frozen.validate_startup(output, "tight")
    except ValueError as exc:
        scf_errors.append(str(exc))
    clean = scf_exit == 0 and not scf_errors and scf_audit["status"] == "VALID_SCF"
    reproduced = "IEEE_INVALID_FLAG" in output
    diagnosis = "IEEE_INVALID_REPRODUCED" if reproduced else "CLEAN_REPRODUCTION" if clean else "OTHER_FAILURE"
    retained_missing = []
    for name in sorted(frozen.PORTABLE_FILES | frozen.WFC_FILES):
        try:
            path = _member(ctx, "tmp_" + ORIGINAL_JOB + "/" + PREFIX + ".save/" + name)
            if not path.is_file() or path.stat().st_size <= 0:
                retained_missing.append(name)
        except (OSError, ValueError):
            retained_missing.append(name)
    complete = False
    if clean and projection_exit == 0:
        try:
            _, projection_record = verify_capture(ctx, "projection")
            if projection_record["collection_complete"] is not True:
                projection_errors.append("projection rank capture incomplete")
            final_qc = qc.audit_files(_member(ctx, JOB + ".run.in"), outpath,
                                      _member(ctx, JOB + ".projwfc.out"))
            complete = not projection_errors and not retained_missing and final_qc["status"] == "COMPLETE"
            if final_qc["status"] != "COMPLETE":
                projection_errors.extend(final_qc["reasons"])
        except (OSError, ValueError, ET.ParseError) as exc:
            projection_errors.append(str(exc))
    record = dict(schema="hea_ieee_smearing_diagnostic_v1", job=JOB, diagnostic_status=diagnosis,
                  new_endpoint_status="COMPLETE" if complete else "INCOMPLETE" if clean else "REJECTED",
                  prior_flagged_run_reclassified=False, scf_exit=scf_exit, projection_exit=projection_exit,
                  scf_reasons=scf_audit["reasons"], startup=startup,
                  evidence_errors=scf_errors, projection_errors=projection_errors,
                  invalid_ranks=[] if rank_audit is None else
                    [row["rank"] for row in rank_audit["ranks"] if "IEEE_INVALID_FLAG" in row["flags"]],
                  rank_capture_complete=rank_audit is not None and rank_audit["collection_complete"] is True,
                  retention_complete=not retained_missing, retained_missing=retained_missing)
    _write_json(_member(ctx, JOB + ".diagnostic.json"), record)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--assemble", choices=("scf", "projection"))
    action.add_argument("--summarize", action="store_true")
    parser.add_argument("--scf-exit", type=int)
    parser.add_argument("--projection-exit", type=int)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.require_complete and not args.summarize:
            raise ValueError("--require-complete requires --summarize")
        if args.summarize:
            record = summarize(args.runs, args.scf_exit, args.projection_exit)
            print(json.dumps(record, sort_keys=True))
            if args.require_complete and record["new_endpoint_status"] != "COMPLETE":
                return 2
        elif args.assemble:
            record = assemble(args.runs, args.assemble)
            print(json.dumps(dict(collection_complete=record["collection_complete"],
                                 missing_ranks=record["missing_ranks"])))
            return 0 if record["collection_complete"] else 2
        else:
            (prepare if args.prepare else validate)(args.runs)
            print("READY" if args.prepare else "VALID")
    except (OSError, ValueError, ET.ParseError) as exc:
        print("REFUSE: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
