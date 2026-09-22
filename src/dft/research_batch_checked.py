"""Execute approved batches on Anvil: fixed-geometry SCFs, seeded or not, and checked relaxations.

Sibling of research_batch_seeded.py, kept as its own pinned file so that the batches pinned to
that runner (Arm B, array 20862631, among them) keep their bytes; this file adds the stage kind
"checked_relax" and its validation on top of the seeded runner (job field "scratch_source").

The scheduler pins this file and the specification. No retries, overwrites or
scratch deletion occur here. A stage of kind "relax" runs one pw.x relaxation leg
under the same supervisor (leg wall up to RELAX_SECONDS, SCF iteration ceiling 126)
and is accepted by the canonical relaxation readout; a stage of kind "checked_relax"
runs the relaxation as one-step from-scratch segments (nstep = 1, never restart_mode
'restart'), each checked against a fresh-start SCF at the same geometry and re-seeded
from the fresh density on a stall or an energy drop (docs/research/
lowtail-stall-robust-protocol-plan-2026-09-22.md, P-A). State travels between segments
by copying the four save files and the <prefix>.bfgs history into a new scratch: QE's
bfgs module reads <prefix>.bfgs from outdir whenever it is present, so the optimizer's
history continues across from-scratch runs, and the scratch of every segment is
retained. Every other kind is a fixed-geometry SCF. A stopped SCF never becomes an energy.
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
LEG_SECONDS = 259200                             # largest admissible checked-relaxation leg wall (72 h)
RY_MEV = 13605.693                               # meV per Ry for the checked-relaxation delta
# State files a checked relaxation re-seeds from a fresh check's save directory.
SEED_FILES = ("charge-density.hdf5", "data-file-schema.xml", "occup.txt", "paw.txt")
# Deck calculation each stage kind may run; kinds not listed are fixed-geometry SCFs.
CALCULATION = {"relax": "relax", "checked_relax": "relax", "beef": "ensemble"}
RELAXING = ("relax", "checked_relax")
ATOM = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s+(" + NUM + r")\s+(" + NUM + r")\s+(" + NUM +
                  r")(?:\s+([01])\s+([01])\s+([01]))?\s*$")


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
    relax = group["kind"] in RELAXING
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
        if group["kind"] == "checked_relax":
            validate_checked(job, directory)
        if pseudo is not None:
            for name in set(re.findall(r"[A-Za-z0-9_.+-]+\.(?:UPF|upf)", text)):
                if name not in spec["pseudo_md5"] or digest(pseudo / name, "md5") != spec["pseudo_md5"][name]:
                    raise ValueError("pseudopotential mismatch: " + name)
    return group


def validate_checked(job, directory):
    """The checked relaxation adds its parameters and its first artifact names to the common checks."""
    if job.get("scratch_source") is None:
        raise ValueError("checked relaxation requires a pinned scratch source")
    checked = job.get("checked")
    if type(checked) is not dict:
        raise ValueError("checked relaxation requires the checked parameters")
    delta = checked.get("delta_meV")
    if type(delta) not in (int, float) or not 0 < delta <= 100:
        raise ValueError("delta_meV must lie in (0, 100]")
    for field, low, high in (("max_segments", 1, 60), ("max_reseeds", 0, 20)):
        if type(checked.get(field)) is not int or not low <= checked[field] <= high:
            raise ValueError("%s must be an integer in [%d, %d]" % (field, low, high))
    if type(checked.get("segment_nstep")) is not int or checked["segment_nstep"] != 1:
        raise ValueError("segment_nstep must be 1: the fresh check reads the geometry of one ionic step")
    threshold = checked.get("fresh_conv_thr")
    if (not isinstance(threshold, str) or not re.fullmatch(NUM, threshold)
            or not float(threshold.replace("D", "e").replace("d", "e")) > 0):
        raise ValueError("fresh_conv_thr must be a positive Fortran real literal")
    leg = checked.get("leg_seconds")
    if leg is not None and (type(leg) not in (int, float) or not 0 < leg <= LEG_SECONDS):
        raise ValueError("leg_seconds must lie in (0, %d]" % LEG_SECONDS)
    name = job["job"]
    for suffix in (".seg1.out", ".seg1.run.in", ".fresh1.out", ".fresh1.run.in"):
        p = directory / (name + suffix)
        if p.exists() or p.is_symlink():
            raise ValueError("prior artifact: " + str(p))
    for scratch in ("tmp_%s_fresh1" % name, "tmp_%s_r1" % name, "tmp_%s_s2" % name):
        p = directory / scratch
        if p.exists() or p.is_symlink():
            raise ValueError("prior scratch: " + str(p))


def runtime_text(text, scratch, pseudo):
    """Point the deck's outdir and pseudo_dir at the run's scratch and pseudopotentials."""
    for field, value in (("outdir", str(scratch)), ("pseudo_dir", str(pseudo))):
        text, count = re.subn(r"(?m)^(\s*" + field + r"\s*=\s*)'[^']*'", lambda m: m[1] + "'" + value + "'", text)
        if count != 1:
            raise ValueError("runtime rewrite not unique: " + field)
    return text


def set_field(text, namelist, field, literal):
    """Set one namelist field (one field per line); insert it under the &namelist header when absent."""
    text, count = re.subn(r"(?m)^([ \t]*" + field + r"[ \t]*=[ \t]*)[^\n]*$", lambda m: m[1] + literal, text)
    if count > 1:
        raise ValueError("runtime rewrite not unique: " + field)
    if count == 0:
        text, count = re.subn(r"(?mi)^([ \t]*&" + namelist + r"[ \t]*)$",
                              lambda m: m[1] + "\n " + field + " = " + literal, text)
        if count != 1:
            raise ValueError("namelist not unique: " + namelist)
    return text


def atom_lines(lines, nat, reference=None):
    """The contiguous atom lines that follow an ATOMIC_POSITIONS header, as (species, x, y, z, flags)
    tuples; species order must match the reference geometry, whose fixed-atom flags are inherited
    when the block carries none."""
    atoms = []
    for line in lines:
        match = ATOM.match(line)
        if not match:
            break
        atoms.append((match[1], match[2], match[3], match[4],
                      None if match[5] is None else (match[5], match[6], match[7])))
    if len(atoms) != nat:
        raise ValueError("atomic positions block has %d readable lines, not nat = %d" % (len(atoms), nat))
    if reference is not None:
        if [a[0] for a in atoms] != [a[0] for a in reference]:
            raise ValueError("species order changed between geometries")
        atoms = [a if a[4] is not None else a[:4] + (r[4],) for a, r in zip(atoms, reference)]
    return atoms


def render_atom(atom):
    return " ".join(atom[:4]) + ("" if atom[4] is None else " " + " ".join(atom[4]))


def geometry_digest(atoms):
    return hashlib.sha256(("\n".join(render_atom(a) for a in atoms) + "\n").encode("utf-8")).hexdigest()


def positions_header(lines):
    headers = [i for i, line in enumerate(lines) if re.match(r"^\s*ATOMIC_POSITIONS\b", line)]
    if len(headers) != 1:
        raise ValueError("deck must hold exactly one ATOMIC_POSITIONS card")
    return headers[0]


def deck_geometry(text, nat):
    lines = text.splitlines()
    return atom_lines(lines[positions_header(lines) + 1:], nat)


def render_positions(text, nat, atoms):
    """The deck with its ATOMIC_POSITIONS lines replaced by the given geometry (header and units kept)."""
    lines = text.splitlines()
    start = positions_header(lines) + 1
    atom_lines(lines[start:], nat)  # the card the deck carries must be readable before it is replaced
    lines[start:start + nat] = [render_atom(a) for a in atoms]
    return "\n".join(lines) + "\n"


def segment_readout(text, nat, reference):
    """A clean one-step segment: the last SCF energy, the geometry pw.x proposes after it, the largest
    SCF iteration number, the total force and whether BFGS reported convergence."""
    failures = sorted(set(FAIL.findall(text)))
    if failures or text.count("JOB DONE") != 1:
        raise ValueError("segment not complete/clean: " + repr(failures))
    energies = list(re.finditer(r"^!\s+total energy\s*=\s*(" + NUM + r")\s+Ry\s*$", text, re.M))
    if not energies or not re.search(r"convergence has been achieved in\s+\d+ iterations", text):
        raise ValueError("segment has no converged SCF energy")
    energy = float(energies[-1][1].replace("D", "e").replace("d", "e"))
    if not math.isfinite(energy):
        raise ValueError("nonfinite energy")
    tail = text[energies[-1].end():].splitlines()
    headers = [i for i, line in enumerate(tail) if re.match(r"^\s*ATOMIC_POSITIONS\b", line)]
    if not headers:
        raise ValueError("segment prints no geometry after its last SCF energy")
    iterations = [int(v) for v in re.findall(r"iteration\s*#\s*(\d+)", text)]
    force = re.search(r"Total force\s*=\s*(" + NUM + r")", text)
    return {"energy_Ry": energy, "iterations": max(iterations) if iterations else None,
            "total_force": float(force[1].replace("D", "e").replace("d", "e")) if force else None,
            "bfgs_converged": "bfgs converged" in text,
            "geometry": atom_lines(tail[headers[-1] + 1:], nat, reference)}


def fresh_reference(output, result):
    """The fresh check's energy, or the reason it gives no reference; a stopped SCF is never read."""
    reference = {"energy_Ry": None, "iterations": None, "converged": False, "reason": None}
    text = output.read_text(encoding="utf-8", errors="replace") if output.is_file() else ""
    iterations = [int(v) for v in re.findall(r"iteration\s*#\s*(\d+)", text)]
    reference["iterations"] = max(iterations) if iterations else None
    if result["stop_reason"]:
        reference["reason"] = "stopped: " + result["stop_reason"]
    elif result["rc"] != 0:
        reference["reason"] = "pw.x failed: " + str(result["rc"])
    else:
        try:
            scf = scf_check(text)
        except ValueError as error:
            reference["reason"] = str(error)
        else:
            reference.update(energy_Ry=scf["energy_Ry"], converged=True)
    return reference


def occupation_diagonal(path, nat, nspin, atom=20, spin=2):
    """The m-resolved occupations of one atom and spin from a retained occup.txt: pw.x writes the
    array ns(ldim, ldim, nspin, nat) list-directed, column-major, so the first index runs fastest.
    None whenever the file is absent or its element count does not factor as ldim**2 * nspin * nat."""
    try:
        tokens = Path(path).read_text(encoding="ascii", errors="strict").split()
        values = []
        for token in tokens:
            repeat, _, value = token.rpartition("*")  # Fortran list-directed r*c repetition
            values.extend([float(value.replace("D", "e").replace("d", "e"))] * (int(repeat) if repeat else 1))
        ldim = math.isqrt(len(values) // (nspin * nat))
        if not values or ldim < 1 or ldim * ldim * nspin * nat != len(values) or not 1 <= atom <= nat or not 1 <= spin <= nspin:
            return None
        block = ldim * ldim * ((atom - 1) * nspin + (spin - 1))
        diagonal = [values[block + m * ldim + m] for m in range(ldim)]
        return diagonal if all(math.isfinite(v) for v in diagonal) else None
    except (OSError, ValueError, UnicodeError, ArithmeticError):
        return None


def continue_scratch(save, previous, target, name):
    """Carry the relaxation into a new scratch: the four state files of `save` (the finished
    segment's own save directory on an accepted step, the fresh reference's on a re-seed) become
    <target>/<name>.save as content-verified copies, and the BFGS history file of the previous
    scratch, when it exists, travels with them; QE's bfgs module reads <prefix>.bfgs from outdir
    whenever it is present, so the optimizer's history continues across from-scratch runs."""
    missing = [f for f in SEED_FILES if not (save / f).is_file()]
    if missing:
        raise ValueError("save directory incomplete: " + ", ".join(missing))
    target.mkdir()  # exclusive: a continuation never lands in an existing scratch
    seed = seed_scratch(save, target / (name + ".save"), {f: digest(save / f) for f in SEED_FILES})
    seed["bfgs_history"] = None
    for relative in (name + ".bfgs", name + ".save/" + name + ".bfgs"):
        source = previous / relative
        if source.is_file():
            shutil.copyfile(source, target / relative)
            if digest(target / relative) != digest(source):
                raise ValueError("BFGS history copy mismatch: " + relative)
            seed["bfgs_history"] = relative
            break
    return seed


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


def checked_relaxation(record, job, deck, directory, scratch, pseudo, env, base, qe):
    """Arm A of the stall-robust plan (P-A). Segment k runs one BFGS step of the production deck
    from scratch (nstep = 1, fresh wavefunctions, density and Hubbard occupations read from the
    scratch's seeded save directory, BFGS history from the carried <prefix>.bfgs); a fresh-start
    SCF (atomic+random wavefunctions, atomic density, the fresh threshold) is then run at the
    geometry the segment's SCF used. The step is accepted when that reference lies within delta
    of the segment's energy: the next segment runs in a new scratch seeded by this segment's own
    save files, at the proposed geometry. When the reference lies more than delta below, or when
    the segment's SCF stalled under the supervisor, the next segment runs in a new scratch seeded
    by the fresh reference's save files and the step is repeated from the checked geometry. Both
    continuations are the same copy; only the seeding save directory and the positions differ.
    One receipt per segment lands in record["segments"] as it is decided, so a leg that stops
    keeps every energy it read. Returns the last segment's output, runtime input and scratch.

    Termination: COMPLETE when a segment reports BFGS convergence and its fresh check accepts it;
    REJECTED at the segment cap, the re-seed cap, the leg wall ceiling, a non-ceiling supervisor
    stop, or a converged final step the fresh check could not reference; KILLED when a segment is
    stopped by the supervisor and the fresh check gives no reference (both reasons recorded)."""
    name, checked = job["job"], job["checked"]
    nat = int(re.search(r"(?m)^\s*nat\s*=\s*(\d+)", deck)[1])
    nspin = re.search(r"(?m)^\s*nspin\s*=\s*(\d+)", deck)
    nspin = int(nspin[1]) if nspin else 1
    delta_Ry = checked["delta_meV"] / RY_MEV
    started = time.monotonic()
    record.update(checked=checked, segments=[], reseeds=0, scratches=[scratch.name])
    geometry = deck_geometry(deck, nat)  # the geometry the first segment's SCF is computed at
    seeded_from, reseeds = record["scratch_source"]["save_dir"], 0
    pw = [str(qe / "bin/pw.x"), "-nk", str(job["nk"]), "-in"]

    def launch(prefix, text, runtime, output, outdir):
        leg = checked.get("leg_seconds")
        if leg is not None and time.monotonic() - started >= leg:
            raise ValueError("leg wall ceiling: %s s elapsed before %s" % (leg, output.name))
        with runtime.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        return execute(base + pw + [str(runtime)], output, directory, env, job["scf_seconds"],
                       job["max_iterations"], outdir / (prefix + ".EXIT"))

    for k in range(1, checked["max_segments"] + 1):
        receipt = {"k": k, "scratch": scratch.name, "seeded_from": seeded_from,
                   "geometry_sha256": geometry_digest(geometry),
                   "segment_energy_Ry": None, "segment_iterations": None, "stalled": False,
                   "fresh_energy_Ry": None, "fresh_iterations": None, "fresh_converged": False,
                   "delta_meV": None, "action": "stop", "reseeds_so_far": reseeds,
                   "atom20_spin_down_diagonal": None}
        record["segments"].append(receipt)
        # (a) the segment: one ionic step from scratch; wavefunctions fresh, density and Hubbard
        # occupations from the seeded save directory, BFGS history from the carried file
        text = runtime_text(deck, scratch, pseudo)
        for namelist, field, literal in (("CONTROL", "nstep", str(checked["segment_nstep"])),
                                         ("CONTROL", "restart_mode", "'from_scratch'"),
                                         ("ELECTRONS", "startingpot", "'file'"),
                                         ("ELECTRONS", "startingwfc", "'atomic+random'")):
            text = set_field(text, namelist, field, literal)
        runtime = directory / ("%s.seg%d.run.in" % (name, k))
        output = directory / ("%s.seg%d.out" % (name, k))
        result = launch(name, render_positions(text, nat, geometry), runtime, output, scratch)
        receipt["segment_process"] = result
        stop = result["stop_reason"]
        if stop and "ceiling" not in stop:
            raise ValueError(stop)
        segment = None
        if not stop:
            if result["rc"] != 0:
                raise ValueError("pw.x failed: " + str(result["rc"]))
            segment = segment_readout(output.read_text(encoding="utf-8", errors="strict"), nat, geometry)
            if segment["iterations"] is None:
                raise ValueError("segment prints no SCF iteration count")
            if segment["iterations"] > job["max_iterations"]:
                # (b) an SCF that ran past the registered ceiling between two polls is a stall as well
                stop, segment = "SCF iteration ceiling (post-hoc)", None
            else:
                receipt.update(segment_energy_Ry=segment["energy_Ry"], segment_iterations=segment["iterations"],
                               total_force=segment["total_force"], bfgs_converged=segment["bfgs_converged"])
        if stop:
            iterations = [int(v) for v in re.findall(r"iteration\s*#\s*(\d+)",
                                                     output.read_text(encoding="utf-8", errors="replace"))]
            receipt.update(stalled=True, stalled_reason=stop, segment_iterations=max(iterations) if iterations else None)
        receipt["atom20_spin_down_diagonal"] = occupation_diagonal(scratch / (name + ".save/occup.txt"), nat, nspin)
        # (d) the fresh check at the geometry the segment's SCF used
        fresh_prefix = "%s_fresh%d" % (name, k)
        fresh_scratch = directory / ("tmp_" + fresh_prefix)
        fresh_scratch.mkdir()
        record["scratches"].append(fresh_scratch.name)
        text = runtime_text(deck, fresh_scratch, pseudo)
        for namelist, field, literal in (("CONTROL", "calculation", "'scf'"), ("CONTROL", "prefix", "'" + fresh_prefix + "'"),
                                         ("CONTROL", "restart_mode", "'from_scratch'"),
                                         ("ELECTRONS", "conv_thr", checked["fresh_conv_thr"]),
                                         ("ELECTRONS", "startingwfc", "'atomic+random'"),
                                         ("ELECTRONS", "startingpot", "'atomic'")):
            text = set_field(text, namelist, field, literal)
        fresh_output = directory / ("%s.fresh%d.out" % (name, k))
        fresh_result = launch(fresh_prefix, render_positions(text, nat, geometry),
                              directory / ("%s.fresh%d.run.in" % (name, k)), fresh_output, fresh_scratch)
        receipt["fresh_process"] = fresh_result
        fresh = fresh_reference(fresh_output, fresh_result)
        receipt.update(fresh_energy_Ry=fresh["energy_Ry"], fresh_iterations=fresh["iterations"],
                       fresh_converged=fresh["converged"], fresh_reason=fresh["reason"],
                       fresh_atom20_spin_down_diagonal=occupation_diagonal(
                           fresh_scratch / (fresh_prefix + ".save/occup.txt"), nat, nspin))
        # (e) the comparison
        if stop:
            if not fresh["converged"]:
                reason = "segment %d stopped: %s; fresh check: %s" % (k, stop, fresh["reason"])
                with (directory / (name + ".KILLED")).open("x", encoding="utf-8") as handle:
                    handle.write(reason + "\n")
                raise ValueError(reason)
            reseed = True  # a stall re-seeds from the fresh density without a comparison
        elif fresh["converged"]:
            receipt["delta_meV"] = (fresh["energy_Ry"] - segment["energy_Ry"]) * RY_MEV
            reseed = fresh["energy_Ry"] < segment["energy_Ry"] - delta_Ry
        else:
            # Rule (f): a fresh check without a reference (stopped, failed or unreadable) cannot
            # re-seed anything, so the step is accepted unchecked only because the segment's own
            # SCF converged; the receipt keeps fresh_converged False and fresh_reason for the readout.
            reseed = False
        if reseed:
            reseeds += 1
            if reseeds > checked["max_reseeds"]:
                raise ValueError("reseed cap: re-seed %d would exceed the cap of %d" % (reseeds, checked["max_reseeds"]))
            record["reseeds"] = receipt["reseeds_so_far"] = reseeds
            receipt["action"] = "reseed"
            # the step is repeated from the checked geometry, seeded by the fresh reference's density
            target = directory / ("tmp_%s_r%d" % (name, reseeds))
            source = fresh_scratch / (fresh_prefix + ".save")
        else:
            if segment["bfgs_converged"]:
                if not fresh["converged"]:
                    raise ValueError("bfgs converged at segment %d but the fresh check gave no reference: %s"
                                     % (k, fresh["reason"]))
                receipt["action"] = "accept"
                record["completed_segment"] = k
                return output, runtime, scratch
            receipt["action"] = "accept"
            if k == checked["max_segments"]:
                break
            # the next step starts from the proposed geometry, seeded by this segment's own density
            target = directory / ("tmp_%s_s%d" % (name, k + 1))
            source = scratch / (name + ".save")
            geometry = segment["geometry"]
        seed = continue_scratch(source, scratch, target, name)
        receipt["continuation"] = dict(scratch=target.name, **seed)
        scratch, seeded_from = target, seed["save_dir"]
        record["scratches"].append(target.name)
        record["scratch_retained"] = str(scratch)
    raise ValueError("segment cap: %d segments without BFGS convergence" % checked["max_segments"])


def run(spec, root, stage, row, pseudo, qe):
    group = validate(spec, root, stage, row, pseudo)
    job = group["jobs"][row-1]
    directory = within(root, "runs/" + job["dir"])
    name = job["job"]
    scratch = directory / ("tmp_" + name)
    scratch.mkdir()  # exclusive ownership; nothing is deleted on any outcome
    runtime = directory / (name + ".run.in")
    text = (directory / (name + ".in")).read_text(encoding="utf-8")
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
        if group["kind"] == "checked_relax":
            output, runtime, scratch = checked_relaxation(record, job, text, directory, scratch, pseudo, env, base, qe)
        else:
            with runtime.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(runtime_text(text, scratch, pseudo))
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
            if group["kind"] not in RELAXING:
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
        if group["kind"] == "checked_relax":
            record["relaxation"] = relaxation_check(output, job["max_iterations"])
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
