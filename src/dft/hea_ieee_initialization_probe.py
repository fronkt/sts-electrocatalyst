"""Bounded QE 7.5 nstep=0 setup-only probe; NEVER an SCF endpoint.

run_pwscf.f90 returns after setup/pre_init/data_structure/summary/config-init,
before init_run (including file density/wavefunctions), electrons and forces.
The accepted source is cloned for identical file context, not claimed as read.
The full clone and every raw rank stream survive every outcome. No retries.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

try:
    from . import hea_numerical_guard as frozen
    from . import hea_sensitivity_guard as sources
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import hea_numerical_guard as frozen
    import hea_sensitivity_guard as sources

SPEC = "results/hea_ieee_init_2026-09-11/launch_spec.json"
SOURCE_SPEC = "results/hea_sensitivity_2026-09-09/launch_spec.json"
DIRECTORY = "hea/ieee_init_2026-09-11"
MANIFEST = "runs/hea/m_ieee_init_2026-09-11.txt"
JOB = "hi__leader_pull2.10__ortho__smearing_init"
SOURCE_JOB = "hn__leader_pull2.10__ortho__tight"
ORIGINAL_JOB = "hs__leader_pull2.10__ortho__smearing"
PREFIX = "hc__leader_pull2.10__ortho__fragment"
RANKS = 128
SCOPE = "setup/pre_init/data_structure/summary/config-init/shutdown; excludes init_run, electrons and forces"
SOURCE_URL = "https://github.com/QEF/q-e/blob/qe-7.5/PW/src/run_pwscf.f90#L148-L159"


def render(original):
    """Exactly two control changes; retain all scientific settings and paths."""
    for old, new in ((b"  nstep = 200\n", b"  nstep = 0\n"),
                     (b"  max_seconds = 13200\n", b"  max_seconds = 480\n")):
        if original.count(old) != 1:
            raise ValueError("original control assignment differs")
        original = original.replace(old, new)
    return original


def _member(ctx, name):
    return frozen._path(ctx["root"], DIRECTORY + "/" + name)


def _deck(ctx):
    raw = frozen._read(_member(ctx, JOB + ".in"))
    if raw != render(ctx["original"]) or frozen._digest(raw) != ctx["spec"]["input_sha256"]:
        raise ValueError("probe input differs from exact nstep=0/max_seconds=480 transformation")
    return raw


def context(runs):
    supplied = Path(runs).absolute()
    if frozen._link(supplied) or not supplied.is_dir():
        raise ValueError("runs must be an existing real directory")
    root = supplied.resolve(strict=True)
    raw = frozen._read(frozen._path(root.parent, SPEC))
    spec = frozen._json(raw)
    fixed = dict(schema="hea_ieee_setup_probe_v1", manifest=MANIFEST, dir=DIRECTORY,
                 job=JOB, source_job=SOURCE_JOB, original_job=ORIGINAL_JOB, prefix=PREFIX,
                 source_spec=SOURCE_SPEC, source_checkpoints=sources.INVENTORY,
                 np=RANKS, nk=8, concurrency=1, wall_minutes=10, nstep=0, max_seconds=480,
                 endpoint_status="DIAGNOSTIC_ONLY", checkpoint_read_claim=False)
    hashes = {"source_spec_sha256", "source_checkpoints_sha256", "manifest_sha256",
              "manifest_lines_sha256", "original_input_sha256", "input_sha256"}
    frozen._keys(spec, set(fixed) | hashes, "probe spec")
    for key, value in fixed.items():
        if type(spec[key]) is not type(value) or spec[key] != value:
            raise ValueError("frozen probe spec differs: " + key)
    for key in hashes:
        frozen._sha(spec[key])
    source_path = frozen._path(root.parent, SOURCE_SPEC)
    if frozen._digest(frozen._read(source_path)) != spec["source_spec_sha256"]:
        raise ValueError("source spec hash differs")
    checked = sources.load_bundle(source_path, root)
    if checked["spec"]["source_checkpoints_sha256"] != spec["source_checkpoints_sha256"]:
        raise ValueError("source inventory hash differs")
    jobs = [job for job in checked["spec"]["jobs"] if job["job"] == ORIGINAL_JOB]
    if len(jobs) != 1 or any(jobs[0][key] != expected for key, expected in
                            (("prefix", PREFIX), ("source_job", SOURCE_JOB), ("arm", "smearing"))):
        raise ValueError("original smearing identity differs")
    original = frozen._read(frozen._path(root, jobs[0]["dir"] + "/" + ORIGINAL_JOB + ".in"))
    if frozen._digest(original) != spec["original_input_sha256"] or jobs[0]["sha256"] != spec["original_input_sha256"]:
        raise ValueError("original smearing input hash differs")
    ctx = dict(root=root, spec=spec, spec_sha256=frozen._digest(raw), original=original,
               checkpoint=checked["checkpoints"][SOURCE_JOB])
    directory = _member(ctx, JOB + ".in").parent
    if not directory.is_dir():
        raise ValueError("isolated probe directory absent")
    manifest = frozen._read(frozen._path(root.parent, MANIFEST))
    lines = frozen._read(frozen._path(root.parent, MANIFEST + ".lines"))
    row = DIRECTORY + " " + JOB + " .in 8\n"
    if (frozen._digest(manifest) != spec["manifest_sha256"] or
            frozen._digest(lines) != spec["manifest_lines_sha256"] or lines != row.encode()):
        raise ValueError("manifest byte identity differs")
    text = manifest.decode("utf-8")
    if b"\r" in manifest or not manifest.endswith(b"\n") or "NOT LICENSED" in text.upper():
        raise ValueError("invalid manifest format/licence")
    if [line for line in text.splitlines() if line and not line.startswith("#")] != [row.rstrip("\n")]:
        raise ValueError("exact one-job manifest required")
    if [line for line in text.splitlines() if re.search(r"\b(?:NP|NCONC)\s*=", line)] != ["# NP=128 NCONC=1"]:
        raise ValueError("exact resource header required")
    _deck(ctx)
    return ctx


def names():
    return dict(stdout=JOB + ".stdout", launcher=JOB + ".launcher.stderr",
                ranks=JOB + ".rank_stderr", combined=JOB + ".out", audit=JOB + ".rank_audit.json")


def verify_pseudopotentials(ctx, pseudo_dir):
    """Check actual live UPFs, not the unchanged copies in the setup clone.

    Production shells bind pseudo_dir to the original input's absolute path.
    An explicit directory allows independent temporary test fixtures.
    """
    directory = Path(pseudo_dir).absolute()
    if not directory.is_dir() or any(frozen._link(path) for path in (directory, *directory.parents)):
        raise ValueError("live pseudopotential directory must be real and unlinked")
    directory = directory.resolve(strict=True)
    entries = [entry for entry in ctx["checkpoint"]["files"] if entry["path"].lower().endswith(".upf")]
    if len(entries) != 6 or any("/" in entry["path"] for entry in entries):
        raise ValueError("exact six accepted pseudopotential files required")
    checked = []
    for entry in entries:
        path = frozen._path(directory, entry["path"])
        raw = frozen._read(path)
        if (len(raw), frozen._digest(raw)) != (entry["size_bytes"], entry["sha256"]):
            raise ValueError("live pseudopotential hash/size mismatch: " + entry["path"])
        checked.append(dict(entry, md5=hashlib.md5(raw).hexdigest()))
    return dict(directory=directory.as_posix(), files=checked)


def verify_printed_pseudopotentials(ctx, output, live):
    """Match seven ordered summary blocks to six byte-verified live UPFs.

    QE 7.5 summary.f90 print_ps_info prints the UPF element, not the input
    species label: both O1 and O2 therefore print O. Do not collapse duplicates.
    https://github.com/QEF/q-e/blob/qe-7.5/PW/src/summary.f90#L398-L414
    """
    block = re.search(r"(?ms)^ATOMIC_SPECIES\n(.*?)^CELL_PARAMETERS", ctx["original"].decode("utf-8"))
    if block is None:
        raise ValueError("original atomic species card absent")
    species = [line.split() for line in block[1].splitlines() if line.strip()]
    if [row[0] for row in species] != ["Cr", "Cu", "Mn", "Ni", "O1", "O2", "H"] or any(len(row) != 3 for row in species):
        raise ValueError("exact seven original species rows required")
    by_name = {entry["path"]: entry for entry in live["files"]}
    expected = []
    for index, row in enumerate(species, 1):
        if row[2] not in by_name:
            raise ValueError("species UPF absent from live identity")
        expected.append(dict(index=index, element="O" if row[0] in ("O1", "O2") else row[0],
                             path=frozen.PSEUDO_DIRECTORY + "/" + row[2], md5=by_name[row[2]]["md5"]))
    pattern = (r"(?m)^\s*PseudoPot\.\s*#\s*(\d+)\s+for\s+([A-Za-z]+)\s+read from file:[ \t]*\n"
               r"[ \t]*([^\r\n]+)\n[ \t]*MD5 check sum:[ \t]*([0-9a-fA-F]{32})[ \t]*$")
    found = [dict(index=int(index), element=element, path=path.strip(), md5=md5.lower())
             for index, element, path, md5 in re.findall(pattern, output)]
    if (len(re.findall(r"PseudoPot\.\s*#", output)) != 7 or
            len(re.findall(r"MD5 check sum:", output)) != 7 or found != expected):
        raise ValueError("printed pseudopotential order/path/MD5 differs from byte-verified live files")
    return found


def validate(runs, pseudo_dir=frozen.PSEUDO_DIRECTORY):
    ctx = context(runs)
    # A new isolated directory contains only its frozen input. Any residue refuses.
    if sorted(path.name for path in _member(ctx, JOB + ".in").parent.iterdir()) != [JOB + ".in"]:
        raise ValueError("preexisting probe artifact; no automatic retry")
    ctx["live_pseudopotentials"] = verify_pseudopotentials(ctx, pseudo_dir)
    frozen.verify_source(ctx["root"], ctx["checkpoint"])
    return ctx


def _write_json(path, record):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, allow_nan=False)
        handle.write("\n")


def _receipt(ctx):
    return dict(schema="hea_ieee_setup_clone_v1", job=JOB, source_job=SOURCE_JOB,
                original_job=ORIGINAL_JOB, prefix=PREFIX, source=ctx["checkpoint"]["dir"],
                destination=DIRECTORY + "/tmp_" + ORIGINAL_JOB + "/" + PREFIX + ".save",
                launch_spec_sha256=ctx["spec_sha256"], input_sha256=ctx["spec"]["input_sha256"],
                source_spec_sha256=ctx["spec"]["source_spec_sha256"],
                source_checkpoints_sha256=ctx["spec"]["source_checkpoints_sha256"],
                checkpoint_read_claim=False, files=ctx["checkpoint"]["files"],
                live_pseudopotentials=ctx["live_pseudopotentials"])


def prepare(runs, pseudo_dir=frozen.PSEUDO_DIRECTORY):
    ctx = validate(runs, pseudo_dir)
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
        expected = entry["size_bytes"], entry["sha256"]
        if (size, digest.hexdigest()) != expected or frozen._stream_hash(dst) != expected:
            raise ValueError("clone hash/size mismatch; partial clone retained")
    if frozen._source_files(source) != [entry["path"] for entry in ctx["checkpoint"]["files"]]:
        raise ValueError("source members changed during clone")
    # Recheck all source acceptance evidence/spec/deck after the potentially long copy.
    checked = context(runs)
    checked["live_pseudopotentials"] = verify_pseudopotentials(checked, pseudo_dir)
    if _receipt(checked) != _receipt(ctx):
        raise ValueError("launch/source identity changed during clone")
    with _member(ctx, JOB + ".run.in").open("xb") as handle:
        handle.write(_deck(checked))
    _member(ctx, names()["ranks"]).mkdir()
    _write_json(_member(ctx, JOB + ".clone_receipt.json"), _receipt(ctx))
    return ctx


def capture_contents(ctx):
    """Every stdout/stderr byte is retained, including empty rank streams."""
    paths = names()
    rankdir = _member(ctx, paths["ranks"])
    expected = ["rank%03d.stderr" % rank for rank in range(RANKS)]
    if not rankdir.is_dir() or any(path.name not in expected for path in rankdir.iterdir()):
        raise ValueError("invalid rank capture directory")
    pieces, streams, ranks, missing = [], {}, [], []
    for label, key in (("STDOUT", "stdout"), ("MPI_LAUNCHER_STDERR", "launcher")):
        raw = frozen._read(_member(ctx, paths[key]))
        pieces.append((label, raw))
        streams[paths[key]] = frozen._digest(raw)
    for rank, name in enumerate(expected):
        path = frozen._path(rankdir, name)
        if not path.exists():
            missing.append(rank)
            continue
        raw = frozen._read(path)
        pieces.append(("MPI_RANK_%03d_STDERR" % rank, raw))
        ranks.append(dict(rank=rank, bytes=len(raw), sha256=frozen._digest(raw),
                          flags=sorted({flag.decode("ascii") for flag in re.findall(rb"IEEE_[A-Z_]+", raw)})))
    combined = pieces[0][1]
    if not combined.endswith(b"\n"):
        combined += b"\n"
    for label, raw in pieces[1:]:
        combined += ("\n# CAPTURE " + label + "\n").encode() + raw
        if not combined.endswith(b"\n"):
            combined += b"\n"
    return combined, dict(schema="hea_ieee_rank_capture_v1", stage="setup", expected_ranks=RANKS,
                          collection_complete=not missing, missing_ranks=missing, ranks=ranks,
                          combined_sha256=frozen._digest(combined), raw_streams=streams)


def assemble(runs):
    ctx = context(runs)
    combined, audit = capture_contents(ctx)
    with _member(ctx, names()["combined"]).open("xb") as handle:
        handle.write(combined)
    _write_json(_member(ctx, names()["audit"]), audit)
    return audit


def setup_signature(output, xml):
    """QE 7.5 source-derived positive branch evidence, never JOB DONE alone.

    punch('config-init') updates XML; pw_write_schema(only_init=True) skips
    band structure, total energy and forces. run_pwscf sets XML exit_status=255.
    stop_run's default build maps that internal status to shell rc=0.
    """
    if len(re.findall(r"Program PWSCF\s+v\.7\.5\b", output)) != 1:
        raise ValueError("expected one QE 7.5 invocation")
    if len(re.findall(r"Writing config-init to output data dir", output)) != 1 or len(re.findall(r"JOB DONE\.", output)) != 1:
        raise ValueError("QE setup-only completion signature absent")
    forbidden = (r"iteration\s*#|convergence\s+(?:has been|NOT)\s+achieved|!\s+total energy|"
                 r"^\s*(?:init_run|electrons|forces|force_hub|potinit|wfcinit)\s*:|"
                 r"The initial density is read from file|Starting wfcs|Forces acting on atoms")
    if re.search(forbidden, output, re.I | re.M):
        raise ValueError("post-setup/SCF activity detected; dry-run contract violated")
    tree = ET.fromstring(xml)
    for element in tree.iter():
        element.tag = element.tag.split("}")[-1]
    def one(path, expected):
        found = tree.findall(path)
        if len(found) != 1 or (found[0].text or "").strip() != expected:
            raise ValueError("setup XML identity differs: " + path)
    one("exit_status", "255")
    for key, expected in (("calculation", "scf"), ("prefix", PREFIX), ("nstep", "0"),
                          ("outdir", "./tmp_" + ORIGINAL_JOB)):
        one("input/control_variables/" + key, expected)
    seconds = tree.findall("input/control_variables/max_seconds")
    if len(seconds) != 1:
        raise ValueError("setup XML identity differs: max_seconds")
    value = float((seconds[0].text or "").strip().replace("D", "E").replace("d", "e"))
    if not math.isfinite(value) or value != 480:
        raise ValueError("setup XML identity differs: max_seconds")
    one("parallel_info/nprocs", "128")
    one("parallel_info/npool", "8")
    if any(tree.find("output/" + tag) is not None for tag in ("band_structure", "total_energy", "forces")):
        raise ValueError("setup XML contains computed endpoint results")
    return dict(xml_exit_status=255, nstep=0, mpi_ranks=128, kpoint_pools=8,
                scope=SCOPE, checkpoint_read_claim=False)


def summarize(runs, process_exit, pseudo_dir=frozen.PSEUDO_DIRECTORY):
    ctx = context(runs)
    if type(process_exit) is not int:
        raise ValueError("integer process exit required")
    errors, audit, output, signature, printed = [], None, "", None, None
    try:
        ctx["live_pseudopotentials"] = verify_pseudopotentials(ctx, pseudo_dir)
        if frozen._read(_member(ctx, JOB + ".run.in")) != _deck(ctx):
            raise ValueError("runtime input differs from frozen setup deck")
        if frozen._json(frozen._read(_member(ctx, JOB + ".clone_receipt.json"))) != _receipt(ctx):
            raise ValueError("clone receipt differs from source/spec identity")
        frozen.verify_source(ctx["root"], ctx["checkpoint"])
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    try:
        combined, audit = capture_contents(ctx)
        if frozen._read(_member(ctx, names()["combined"])) != combined or frozen._json(
                frozen._read(_member(ctx, names()["audit"]))) != audit:
            raise ValueError("combined capture/audit differs from raw streams")
        output = combined.decode("utf-8", errors="replace")
        if not audit["collection_complete"]:
            errors.append("incomplete rank capture")
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    if ctx.get("live_pseudopotentials") is not None:
        try:
            printed = verify_printed_pseudopotentials(ctx, output, ctx["live_pseudopotentials"])
        except ValueError as exc:
            errors.append(str(exc))
    retained = []
    try:
        destination = _member(ctx, "tmp_" + ORIGINAL_JOB + "/" + PREFIX + ".save")
        if frozen._source_files(destination) != [entry["path"] for entry in ctx["checkpoint"]["files"]]:
            raise ValueError("retained clone member list differs")
        for entry in ctx["checkpoint"]["files"]:
            path = frozen._path(destination, entry["path"])
            size, digest = frozen._stream_hash(path)
            retained.append(dict(path=entry["path"], size_bytes=size, sha256=digest))
            # config-init replaces only XML. Density/occup/paw, all 16 WFCs,
            # copied pseudopotentials and atomic projection must stay unchanged.
            if entry["path"] != "data-file-schema.xml" and (size, digest) != (entry["size_bytes"], entry["sha256"]):
                raise ValueError("unexpected setup clone mutation: " + entry["path"])
        signature = setup_signature(output, frozen._read(destination / "data-file-schema.xml"))
    except (OSError, ValueError, ET.ParseError) as exc:
        errors.append(str(exc))
    flags = sorted(set(re.findall(r"IEEE_[A-Z_]+", output)))
    if process_exit != 0:
        errors.append("nonzero process exit: " + str(process_exit))
    if re.search(r"Error in routine|MPI_ABORT|segmentation fault|SIGFPE|\bNaN\b|\bInfinity\b", output, re.I):
        errors.append("fatal/nonfinite raw output")
    if flags and flags != ["IEEE_INVALID_FLAG"]:
        errors.append("additional floating-point flags: " + ",".join(flags))
    diagnosis = ("OTHER_FAILURE" if errors else "SETUP_INVALID_REPRODUCED" if flags
                 else "SETUP_ONLY_CLEAN")
    record = dict(schema="hea_ieee_setup_diagnostic_v1", job=JOB, diagnostic_status=diagnosis,
                  new_endpoint_status="DIAGNOSTIC_ONLY", prior_flagged_run_reclassified=False,
                  checkpoint_read_claim=False, scope=SCOPE, qe_source=SOURCE_URL,
                  process_exit=process_exit, setup_signature=signature, evidence_errors=errors,
                  flags=flags, invalid_ranks=[] if audit is None else
                  [row["rank"] for row in audit["ranks"] if "IEEE_INVALID_FLAG" in row["flags"]],
                  rank_capture_complete=audit is not None and audit["collection_complete"],
                  retained_files=retained, launch_spec_sha256=ctx["spec_sha256"],
                  live_pseudopotentials=ctx.get("live_pseudopotentials"),
                  printed_pseudopotentials=printed)
    _write_json(_member(ctx, JOB + ".diagnostic.json"), record)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--pseudo-dir", type=Path, required=True,
                        help="live UPF directory, bound to the original input path by the production shells")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--assemble", action="store_true")
    action.add_argument("--summarize", action="store_true")
    parser.add_argument("--process-exit", type=int)
    args = parser.parse_args(argv)
    try:
        if args.summarize:
            record = summarize(args.runs, args.process_exit, args.pseudo_dir)
            print(json.dumps(record, sort_keys=True, allow_nan=False))
            return 0 if record["diagnostic_status"] == "SETUP_ONLY_CLEAN" else 16
        if args.assemble:
            audit = assemble(args.runs)
            print(json.dumps(audit, sort_keys=True))
            return 0 if audit["collection_complete"] else 2
        (prepare if args.prepare else validate)(args.runs, args.pseudo_dir)
        print("READY: DIAGNOSTIC ONLY" if args.prepare else "VALID: DIAGNOSTIC ONLY")
    except (OSError, ValueError, ET.ParseError) as exc:
        print("REFUSE: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
