"""Execute approved fixed-geometry batches on Anvil, optionally seeded from a retained density.

Sibling of research_batch.py, kept as its own pinned file so that the batches pinned to the
original runner (the 2026-09-18 relaxation array and the 2026-09-19 diagnostic) keep their
bytes; this file adds the content-pinned scratch seed (job field "scratch_source").

The scheduler pins this file and the specification. No retries, overwrites or
scratch deletion occur here. A stage of kind "relax" runs one pw.x relaxation leg
under the same supervisor (leg wall up to RELAX_SECONDS, SCF iteration ceiling 126)
and is accepted by the canonical relaxation readout; every other kind is a
fixed-geometry SCF. A stopped leg never becomes a result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

FAIL = re.compile(r"convergence NOT achieved|Maximum (?:CPU|wall) time exceeded|"
                  r"Program stopped by user request|Error in routine|MPI_ABORT|"
                  r"SIGTERM|SIGINT|SIGSEGV|Segmentation fault|Floating point exception|"
                  r"IEEE_INVALID_FLAG|IEEE_OVERFLOW_FLAG|IEEE_DIVIDE_BY_ZERO|forrtl:\s*severe", re.I)
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"
SCF_SECONDS, RELAX_SECONDS = 19000, 60000       # per-job pw.x wall by stage kind
RELAX_MAX_ITERATIONS = 126                       # registered SCF ceiling of a relaxation leg
# Deck calculation each stage kind may run; kinds not listed are fixed-geometry SCFs.
CALCULATION = {"relax": "relax", "beef": "ensemble"}


def digest(path, algorithm="sha256"):
    return hashlib.new(algorithm, Path(path).read_bytes()).hexdigest()


def within(root, relative):
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("unsafe relative path")
    path = root / relative
    if path.is_symlink() or root.resolve() not in path.resolve().parents:
        raise ValueError("path escapes approved root")
    return path


def validate(spec, root, stage, row=None, pseudo=None):
    if spec["schema"] != "research-batch-2026-09-16" or stage not in spec["stages"]:
        raise ValueError("unsupported approved specification")
    helper = "src/dft/projection_qc.py"
    if helper not in spec["files"]:
        raise ValueError("projection validator dependency not pinned")
    # Pin both the staged dependency and the sibling source this runner executes.
    # Historical launch specifications intentionally cannot authorize this revision.
    if digest(Path(__file__).with_name("projection_qc.py")) != spec["files"][helper]:
        raise ValueError("executed projection validator differs from pin")
    for relative, expected in spec["files"].items():
        if digest(within(root, relative)) != expected:
            raise ValueError("pinned file changed: " + relative)
    group = spec["stages"][stage]
    for prerequisite in group.get("requires_complete", []):
        for prior in spec["stages"][prerequisite]["jobs"]:
            base = within(root, "runs/" + prior["dir"]) / prior["job"]
            receipt = json.loads(Path(str(base) + ".qc.json").read_text(encoding="utf-8"))
            if (receipt.get("status") != "COMPLETE" or receipt.get("input_sha256") != prior["sha256"]
                    or receipt.get("output_sha256") != digest(Path(str(base) + ".out"))
                    or receipt.get("runtime_sha256") != digest(Path(str(base) + ".run.in"))
                    or receipt.get("ensemble_check", {}).get("rc") != 0):
                raise ValueError("prerequisite not complete with verified artifacts: " + prior["job"])
    manifest = within(root, group["manifest"]).read_text(encoding="utf-8")
    if "NOT LICENSED" in manifest.upper() or "# NP=128 NCONC=1" not in manifest:
        raise ValueError("unapproved manifest or resource directive")
    expected_rows = [f"{j['dir']} {j['job']} .in {j['nk']}" for j in group["jobs"]]
    actual = [s for s in manifest.splitlines() if s.strip() and not s.startswith("#")]
    if actual != expected_rows or len(set(expected_rows)) != len(expected_rows):
        raise ValueError("manifest identity/order mismatch")
    if row is not None and (type(row) is not int or not 1 <= row <= len(expected_rows)):
        raise ValueError("invalid task index")
    relax = group["kind"] == "relax"
    calculation = CALCULATION.get(group["kind"], "scf")
    for job in group["jobs"] if row is None else [group["jobs"][row-1]]:
        if type(job["nk"]) is not int or job["nk"] <= 0 or 128 % job["nk"]:
            raise ValueError("invalid pool/rank shape")
        if (not 0 < job["scf_seconds"] <= (RELAX_SECONDS if relax else SCF_SECONDS)
                or not 0 < job["projection_seconds"] <= 1800):
            raise ValueError("invalid bounded runtime")
        if relax and job.get("max_iterations") != RELAX_MAX_ITERATIONS:
            raise ValueError("relaxation requires the registered %d-iteration SCF ceiling" % RELAX_MAX_ITERATIONS)
        directory = within(root, "runs/" + job["dir"])
        deck = directory / (job["job"] + ".in")
        if digest(deck) != job["sha256"] or b"\r" in deck.read_bytes():
            raise ValueError("input bytes differ")
        text = deck.read_text(encoding="utf-8")
        prefixes = re.findall(r"(?m)^\s*prefix\s*=\s*'([^']+)'", text)
        if prefixes != [job["job"]]:
            raise ValueError("input prefix mismatch")
        if re.findall(r"(?m)^\s*calculation\s*=\s*'([^']+)'", text) != [calculation]:
            raise ValueError("deck calculation does not match stage kind: expected '" + calculation + "'")
        for suffix in (".out", ".run.in", ".projwfc.in", ".projwfc.out", ".qc.json", ".KILLED", ".REJECTED"):
            p = directory / (job["job"] + suffix)
            if p.exists() or p.is_symlink():
                raise ValueError("prior artifact: " + str(p))
        scratch = directory / ("tmp_" + job["job"])
        if scratch.exists() or scratch.is_symlink():
            raise ValueError("prior scratch: " + str(scratch))
        source = job.get("scratch_source")
        if source is not None:
            # A retained density from an earlier run seeds this job's scratch: pinned by
            # content, copied never moved, refused on any drift before scratch exists.
            save = within(root, source["save_dir"])
            if save.is_symlink() or not save.is_dir():
                raise ValueError("scratch source missing: " + str(source["save_dir"]))
            if not {"charge-density.hdf5", "data-file-schema.xml"} <= set(source["files"]):
                raise ValueError("scratch source must pin the density and its XML")
            for name, expected in source["files"].items():
                if "/" in name or "\\" in name or name in ("", ".", "..") or (save / name).is_symlink():
                    raise ValueError("unsafe scratch source entry: " + str(name))
                if digest(save / name) != expected:
                    raise ValueError("scratch source file drifted: " + name)
            if not re.search(r"(?m)^\s*startingpot\s*=\s*'file'", deck.read_text(encoding="utf-8")):
                raise ValueError("scratch source pinned but the deck does not read it")
        if pseudo is not None:
            for name in set(re.findall(r"[A-Za-z0-9_.+-]+\.(?:UPF|upf)", text)):
                if name not in spec["pseudo_md5"] or digest(pseudo / name, "md5") != spec["pseudo_md5"][name]:
                    raise ValueError("pseudopotential mismatch: " + name)
    return group


def scf_check(text):
    failures = sorted(set(FAIL.findall(text)))
    energies = re.findall(r"^!\s+total energy\s*=\s*(" + NUM + r")\s+Ry\s*$", text, re.M)
    conv = re.findall(r"convergence has been achieved in\s+(\d+) iterations", text)
    if failures or text.count("JOB DONE") != 1 or len(energies) != 1 or len(conv) != 1:
        raise ValueError("SCF not complete/clean: " + repr(failures))
    energy = float(energies[0].replace("D", "e").replace("d", "e"))
    if not math.isfinite(energy):
        raise ValueError("nonfinite energy")
    return {"energy_Ry": energy, "iterations": int(conv[0])}


def relaxation_check(output, max_iterations):
    """Accept a relaxation leg as lowtail_batch.relaxation_check does: the canonical readout
    decides completion, then every SCF cycle must sit within the registered iteration ceiling."""
    import hea_panel_readout
    try:
        score = hea_panel_readout.parse_out(output, allow_relax=True)
    except hea_panel_readout.Fatal as error:
        raise ValueError("relaxation readout failed: " + str(error))
    if score["status"] != "CONVERGED":
        raise ValueError("relaxation not complete/clean: " + str(score["status"]))
    text = output.read_text(encoding="utf-8", errors="strict")
    iterations = [int(v) for v in re.findall(r"iteration\s*#\s*(\d+)", text)]
    if not iterations or max(iterations) > max_iterations:
        raise ValueError("relaxation SCF iteration count missing or above the %d ceiling" % max_iterations)
    energies = [float(e.replace("D", "e").replace("d", "e")) for e in
                re.findall(r"^!\s+total energy\s*=\s*(" + NUM + r")\s+Ry\s*$", text, re.M)]
    if energies and not math.isfinite(energies[-1]):
        raise ValueError("nonfinite energy")
    return {"status": score["status"], "maximum_scf_iteration": max(iterations),
            "bfgs_converged": "bfgs converged" in text,
            "final_energy_Ry": energies[-1] if energies else None, "ionic_steps": len(energies)}


def projection_check(text, nat):
    """Use the pinned validator for combined-spin and split nonmagnetic rows."""
    if __package__:
        from .projection_qc import projection_check as checked_projection
    else:
        from projection_qc import projection_check as checked_projection
    return checked_projection(text, nat)


def seed_scratch(source_dir, target_dir, expected):
    """Copy the pinned save files into a fresh <job>.save; verify each byte stream twice."""
    target_dir.mkdir()  # exclusive: a seeded directory is never overwritten
    copied, total = {}, 0
    for name, digest_expected in expected.items():
        src, dst = source_dir / name, target_dir / name
        if digest(src) != digest_expected:
            raise ValueError("scratch source file drifted: " + name)
        shutil.copyfile(src, dst)
        if digest(dst) != digest_expected:
            raise ValueError("scratch seed copy mismatch: " + name)
        copied[name] = digest_expected
        total += dst.stat().st_size
    return {"save_dir": str(source_dir), "copied": copied, "bytes": total}


def stop_process(process):
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        process.wait(timeout=20)
        return
    try:
        process.wait(timeout=20)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=20)


def execute(command, output, cwd, env, seconds, max_iterations=None, exitfile=None):
    started = time.monotonic()
    reason = None
    with output.open("xb") as handle:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdout=handle,
                                   stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                   start_new_session=True)
        try:
            while process.poll() is None:
                text = output.read_text(encoding="utf-8", errors="replace")
                iterations = [int(x) for x in re.findall(r"iteration\s*#\s*(\d+)", text)]
                if time.monotonic() - started >= seconds:
                    reason = "wall-time ceiling"
                elif max_iterations and iterations and max(iterations) > max_iterations:
                    reason = "SCF iteration ceiling"
                elif FAIL.search(text):
                    reason = "numerical failure marker"
                if reason:
                    if exitfile is not None:
                        exitfile.touch(exist_ok=False)
                    try:
                        process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        stop_process(process)
                    break
                time.sleep(2)
        finally:
            stop_process(process)
    return {"rc": process.returncode, "stop_reason": reason,
            "wall_seconds": time.monotonic() - started}


def run(spec, root, stage, row, pseudo, qe):
    group = validate(spec, root, stage, row, pseudo)
    job = group["jobs"][row-1]
    directory = within(root, "runs/" + job["dir"])
    name = job["job"]
    scratch = directory / ("tmp_" + name)
    scratch.mkdir()  # exclusive ownership; nothing is deleted on any outcome
    runtime = directory / (name + ".run.in")
    text = (directory / (name + ".in")).read_text(encoding="utf-8")
    for field, value in (("outdir", str(scratch)), ("pseudo_dir", str(pseudo))):
        text, count = re.subn(r"(?m)^(\s*" + field + r"\s*=\s*)'[^']*'", lambda m: m[1] + "'" + value + "'", text)
        if count != 1:
            raise ValueError("runtime rewrite not unique: " + field)
    with runtime.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    env = os.environ.copy()
    env.update(PATH=str(qe / "bin") + ":" + env.get("PATH", ""),
               LD_LIBRARY_PATH=str(qe / "lib") + ":" + env.get("LD_LIBRARY_PATH", ""),
               OMP_NUM_THREADS="1", ESPRESSO_PSEUDO=str(pseudo))
    base = [str(qe / "bin/mpirun"), "--oversubscribe", "-np", "128"]
    record = {"stage": stage, "row": row, "job": name, "status": "REJECTED",
              "input_sha256": job["sha256"], "scratch_retained": str(scratch)}
    output = directory / (name + ".out")
    try:
        if job.get("scratch_source") is not None:
            record["scratch_source"] = seed_scratch(within(root, job["scratch_source"]["save_dir"]),
                                                   scratch / (name + ".save"), job["scratch_source"]["files"])
        result = execute(base + [str(qe / "bin/pw.x"), "-nk", str(job["nk"]), "-in", str(runtime)],
                         output, directory, env, job["scf_seconds"], job.get("max_iterations"), scratch / (name + ".EXIT"))
        record["scf_process"] = result
        if result["stop_reason"]:
            suffix = ".KILLED" if "ceiling" in result["stop_reason"] else ".REJECTED"
            with (directory / (name + suffix)).open("x", encoding="utf-8") as handle:
                handle.write(result["stop_reason"] + "\n")
            raise ValueError(result["stop_reason"])
        if result["rc"] != 0:
            raise ValueError("pw.x failed: " + str(result["rc"]))
        if group["kind"] == "relax":
            record["relaxation"] = relaxation_check(output, job["max_iterations"])
        else:
            record["scf"] = scf_check(output.read_text(encoding="utf-8", errors="strict"))
        if group["kind"] == "beef":
            check = subprocess.run([sys.executable, str(root / "src/dft/p_beef_readout.py"),
                                    "--check-output", str(output)], capture_output=True, text=True, timeout=120)
            record["ensemble_check"] = {"rc": check.returncode, "stdout": check.stdout, "stderr": check.stderr}
            if check.returncode:
                raise ValueError("BEEF ensemble/contribution validation failed")
        else:
            if group["kind"] != "relax":
                from hea_force_audit import audit_files
                force = audit_files(runtime, output)
                if force["status"] != "VALID_SCF":
                    raise ValueError("force/SCF validation failed: " + repr(force["reasons"]))
                record["force"] = force
            projection_input = directory / (name + ".projwfc.in")
            with projection_input.open("x", encoding="utf-8") as handle:
                handle.write("&PROJWFC\n prefix = '" + name + "'\n outdir = '" + str(scratch) + "'\n lsym = .true.\n/\n")
            projection = directory / (name + ".projwfc.out")
            record["projection_process"] = execute(base + [str(qe / "bin/projwfc.x"), "-nk", str(job["nk"]), "-in", str(projection_input)],
                                                    projection, directory, env, job["projection_seconds"])
            if record["projection_process"]["rc"] or record["projection_process"]["stop_reason"]:
                raise ValueError("projection failed or exceeded bound")
            nat = int(re.search(r"(?m)^\s*nat\s*=\s*(\d+)", text)[1])
            projection_check(projection.read_text(encoding="utf-8"), nat)
            if group["kind"] == "hea":
                from hea_followup_qc import audit_files as full_audit
                record["complete_audit"] = full_audit(runtime, output, projection)
                if record["complete_audit"]["status"] != "COMPLETE":
                    raise ValueError("complete HEA QC rejected")
        save = scratch / (name + ".save")
        if not (save / "data-file-schema.xml").is_file() or not any((save / p).is_file() for p in ("charge-density.dat", "charge-density.hdf5")):
            raise ValueError("density/XML retention incomplete")
        record["status"] = "COMPLETE"
        record["output_sha256"] = digest(output)
        record["runtime_sha256"] = digest(runtime)
    except (ValueError, OSError, UnicodeError, subprocess.SubprocessError) as error:
        record["reason"] = str(error)
        rejected = directory / (name + ".REJECTED")
        if not rejected.exists() and not (directory / (name + ".KILLED")).exists():
            rejected.write_text(str(error) + "\n", encoding="utf-8")
    with (directory / (name + ".qc.json")).open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"job": name, "status": record["status"], "reason": record.get("reason")}), flush=True)
    return 0 if record["status"] == "COMPLETE" else 10


def main(argv=None):
    def interrupted(signum, frame):
        raise InterruptedError("scheduler/process signal " + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--row", type=int)
    p.add_argument("--pseudo", type=Path, required=True)
    p.add_argument("--qe", type=Path)
    p.add_argument("--preflight", action="store_true")
    a = p.parse_args(argv)
    spec = json.loads(a.spec.read_text(encoding="utf-8"))
    if a.preflight:
        validate(spec, a.root, a.stage, pseudo=a.pseudo)
        print("VALID")
        return 0
    if a.row is None or a.qe is None:
        p.error("execution requires --row and --qe")
    return run(spec, a.root, a.stage, a.row, a.pseudo, a.qe)


if __name__ == "__main__":
    raise SystemExit(main())
