"""Run the authorized nine atomic Cr relaxations with preserved failure evidence.

This is a separate launch contract from the fixed-coordinate September 16 batch.
The existing process supervisor enforces each SCF iteration cap and leg wall;
the canonical parser and final geometry/force checks decide scientific completion.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess

import hea_deck
import hea_panel_readout
from research_batch import digest, execute, projection_check, within

NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"
DEPENDENCIES = (
    "src/dft/lowtail_batch.py", "src/dft/research_batch.py",
    "src/dft/projection_qc.py", "src/dft/hea_panel_readout.py",
    "src/dft/hea_geometry.py", "src/dft/hea_deck.py",
)


def number(value):
    result = float(value.replace("D", "e").replace("d", "e"))
    if not math.isfinite(result):
        raise ValueError("nonfinite output value")
    return result


def validate(spec, root, row=None, pseudo=None):
    root = Path(root)
    if (spec.get("schema") != "lowtail-relaxation-launch-v1"
            or spec.get("authorization") != "USER_CONTINUE_2026-09-18"
            or spec.get("np") != 128 or spec.get("concurrency") != 1
            or len(spec.get("jobs", [])) != 9):
        raise ValueError("unsupported authorized relaxation specification")
    for relative in DEPENDENCIES:
        if relative not in spec["files"]:
            raise ValueError("missing dependency pin: " + relative)
        if digest(Path(__file__).parent / Path(relative).name) != spec["files"][relative]:
            raise ValueError("executed dependency differs: " + relative)
    for relative, expected in spec["files"].items():
        if digest(within(root, relative)) != expected:
            raise ValueError("pinned file changed: " + relative)
    manifest = within(root, spec["manifest"]).read_text(encoding="utf-8")
    if "NOT LICENSED" in manifest.upper() or "# NP=128 NCONC=1" not in manifest:
        raise ValueError("manifest not authorized at registered resources")
    expected = [f"{j['manifest_dir']} {j['job']} .in {j['nk']}" for j in spec["jobs"]]
    actual = [s for s in manifest.splitlines() if s.strip() and not s.startswith("#")]
    if actual != expected or len(set(expected)) != 9:
        raise ValueError("manifest identity/order mismatch")
    if row is not None and (type(row) is not int or not 1 <= row <= 9):
        raise ValueError("invalid row")
    for job in spec["jobs"] if row is None else [spec["jobs"][row - 1]]:
        limits = job["supervisor_limits"]
        if (job["projector"] != "atomic" or job["role"] != "primary"
                or job["nk"] != 8 or limits["max_scf_iterations"] != 126
                or not 0 < limits["leg_wall_ceiling_s"] < 165000
                or not 0 < job["projection_seconds"] <= 1800):
            raise ValueError("unapproved leg or limit")
        path = within(root, job["path"])
        if path != within(root, "runs/" + job["manifest_dir"]) / (job["job"] + ".in"):
            raise ValueError("input path differs from manifest")
        if digest(path) != job["sha256"] or b"\r" in path.read_bytes():
            raise ValueError("deck bytes differ")
        text = path.read_text(encoding="utf-8")
        if (re.findall(r"(?m)^\s*calculation\s*=\s*'([^']+)'", text) != ["relax"]
                or re.findall(r"(?m)^\s*prefix\s*=\s*'([^']+)'", text) != [job["prefix"]]):
            raise ValueError("calculation/prefix mismatch")
        parsed = hea_deck.parse_deck(text)
        if parsed["nat"] != job["nat"] or parsed["fixed"] != job["fixed"]:
            raise ValueError("atom identity/constraints differ")
        for suffix in (".out", ".run.in", ".projwfc.in", ".projwfc.out", ".qc.json", ".KILLED", ".REJECTED"):
            artifact = path.with_suffix(suffix)
            if artifact.exists() or artifact.is_symlink():
                raise ValueError("prior artifact: " + str(artifact))
        scratch = path.parent / ("tmp_" + job["job"])
        if scratch.exists() or scratch.is_symlink():
            raise ValueError("prior scratch: " + str(scratch))
        if pseudo is not None:
            for name in parsed["upfs"]:
                if name not in spec["pseudo_md5"] or digest(Path(pseudo) / name, "md5") != spec["pseudo_md5"][name]:
                    raise ValueError("pseudopotential mismatch: " + name)
    return spec["jobs"][row - 1] if row is not None else None


def relaxation_check(output, input_text, job, process):
    score = hea_panel_readout.parse_out(output, allow_relax=True)
    if score["status"] != "CONVERGED":
        raise ValueError("relaxation not complete/clean: " + score["status"])
    text = output.read_text(encoding="utf-8")
    limits = job["supervisor_limits"]
    iterations = [int(v) for v in re.findall(r"iteration\s*#\s*(\d+)", text)]
    if (not iterations or max(iterations) > limits["max_scf_iterations"]
            or process["wall_seconds"] > limits["leg_wall_ceiling_s"]
            or score["wall_s"] is None or score["wall_s"] > limits["leg_wall_ceiling_s"]):
        raise ValueError("relaxation exceeded registered limit or lacks timing")
    parsed = hea_deck.parse_deck(input_text)
    blocks = re.findall(r"Begin final coordinates(.*?)End final coordinates", text, re.S)
    if len(blocks) != 1 or text.count("Begin final coordinates") != 1 or text.count("End final coordinates") != 1:
        raise ValueError("expected one complete final-coordinate block")
    lines = [line for line in blocks[0].strip().splitlines() if line.strip()]
    if not lines or not re.fullmatch(r"ATOMIC_POSITIONS\s*\(?angstrom\)?", lines[0].strip()):
        raise ValueError("unexpected final-coordinate units")
    final = []
    for line in lines[1:]:
        fields = line.split()
        if len(fields) not in (4, 7):
            raise ValueError("malformed final-coordinate row")
        final.append((fields[0], [number(v) for v in fields[1:4]]))
    if [s for s, p in final] != parsed["symbols"]:
        raise ValueError("final elements/count differ from deck")
    fixed_shift = max((abs(final[i][1][k] - parsed["positions"][i][k])
                       for i in parsed["fixed"] for k in range(3)), default=0)
    if fixed_shift > 1e-6:
        raise ValueError("fixed atoms moved")
    force_header = re.compile(r"^\s*Forces acting on atoms \(cartesian axes, Ry/au\):\s*$", re.M)
    force_row = re.compile(r"^\s*atom\s+(\d+)\s+type\s+\d+\s+force\s*=\s*(" + NUM +
                           r")\s+(" + NUM + r")\s+(" + NUM + r")\s*$")
    # Contribution blocks share the row syntax, so only contiguous rows directly
    # following each total-force header belong to the total force.
    force_blocks = []
    output_lines = text.splitlines()
    for line_no, line in enumerate(output_lines):
        if not force_header.fullmatch(line):
            continue
        index = line_no + 1
        while index < len(output_lines) and not output_lines[index].strip():
            index += 1
        rows = []
        while index < len(output_lines):
            match = force_row.fullmatch(output_lines[index])
            if match is None:
                break
            rows.append(match.groups())
            index += 1
        if len(rows) != job["nat"] or [int(r[0]) for r in rows] != list(range(1, job["nat"] + 1)):
            raise ValueError("total-force block malformed")
        for row in rows:
            for value in row[1:]:
                number(value)
        force_blocks.append(rows)
    if not force_blocks:
        raise ValueError("no total-force block")
    bfgs = re.findall(r"bfgs converged in\s+(\d+)\s+scf cycles and\s+(\d+)\s+bfgs steps", text)
    if (len(bfgs) != 1 or int(bfgs[0][0]) != score["n_energies"]
            or int(bfgs[0][0]) != score["scf_converged"] or int(bfgs[0][0]) != len(force_blocks)):
        raise ValueError("BFGS cycles, SCFs, energies and total-force blocks differ")
    nat = re.findall(r"number of atoms/cell\s*=\s*(\d+)", text)
    if nat != [str(job["nat"])]:
        raise ValueError("printed atom count differs from the deck")
    order = [text.rfind("Forces acting on atoms"), text.find("bfgs converged"),
             text.find("Final energy"), text.find("Begin final coordinates"),
             text.find("End final coordinates"), text.find("JOB DONE")]
    if any(v < 0 for v in order) or order != sorted(order):
        raise ValueError("terminal relaxation markers out of order")
    fmax = max(abs(number(v)) for i, *xyz in force_blocks[-1]
               if int(i) - 1 not in parsed["fixed"] for v in xyz)
    if fmax > job["forc_conv_thr_Ry_bohr"] + 5e-9:
        raise ValueError("final free force exceeds threshold")
    final_energy = re.findall(r"^\s*Final energy\s*=\s*(" + NUM + r")\s*Ry\s*$", text, re.M)
    if len(final_energy) != 1 or abs(number(final_energy[0]) - score["E_Ry"]) > 1e-8:
        raise ValueError("final energy does not match last SCF")
    return dict(score=score, max_free_component_Ry_bohr=fmax, fixed_shift_A=fixed_shift,
                maximum_scf_iteration=max(iterations), final_positions_A=[p for s, p in final])


def run(spec, root, row, pseudo, qe):
    job = validate(spec, root, row, pseudo)
    directory = within(root, "runs/" + job["manifest_dir"])
    name, prefix = job["job"], job["prefix"]
    scratch = directory / ("tmp_" + name)
    scratch.mkdir()
    runtime = directory / (name + ".run.in")
    text = within(root, job["path"]).read_text(encoding="utf-8")
    for field, value in (("outdir", str(scratch)), ("pseudo_dir", str(pseudo))):
        text, n = re.subn(r"(?m)^(\s*" + field + r"\s*=\s*)'[^']*'", lambda m: m[1] + "'" + value + "'", text)
        if n != 1:
            raise ValueError("runtime rewrite not unique")
    with runtime.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    env = os.environ.copy()
    env.update(PATH=str(qe / "bin") + ":" + env.get("PATH", ""),
               LD_LIBRARY_PATH=str(qe / "lib") + ":" + env.get("LD_LIBRARY_PATH", ""),
               OMP_NUM_THREADS="1", ESPRESSO_PSEUDO=str(pseudo))
    base = [str(qe / "bin/mpirun"), "--oversubscribe", "-np", "128"]
    output = directory / (name + ".out")
    record = dict(row=row, job=name, site=job["site"], status="REJECTED",
                  input_sha256=job["sha256"], scratch_retained=str(scratch))
    try:
        result = execute(base + [str(qe / "bin/pw.x"), "-nk", "8", "-in", str(runtime)],
                         output, directory, env, job["supervisor_limits"]["leg_wall_ceiling_s"], 126,
                         scratch / (prefix + ".EXIT"))
        record["relaxation_process"] = result
        if result["stop_reason"] or result["rc"]:
            if result["stop_reason"] and "ceiling" in result["stop_reason"]:
                record["status"] = "KILLED"
            raise ValueError(result["stop_reason"] or "pw.x exit " + str(result["rc"]))
        record["relaxation"] = relaxation_check(output, text, job, result)
        pin = directory / (name + ".projwfc.in")
        with pin.open("x", encoding="utf-8") as handle:
            handle.write("&PROJWFC\n prefix = '" + prefix + "'\n outdir = '" + str(scratch) + "'\n lsym = .true.\n/\n")
        pout = directory / (name + ".projwfc.out")
        record["projection_process"] = execute(base + [str(qe / "bin/projwfc.x"), "-nk", "8", "-in", str(pin)],
                                               pout, directory, env, job["projection_seconds"])
        if record["projection_process"]["rc"] or record["projection_process"]["stop_reason"]:
            raise ValueError("projection did not complete within bound")
        record["projection"] = projection_check(pout.read_text(encoding="utf-8"), job["nat"])
        save = scratch / (prefix + ".save")
        if not (save / "data-file-schema.xml").is_file() or not any((save / p).is_file() for p in ("charge-density.dat", "charge-density.hdf5")):
            raise ValueError("density/XML retention incomplete")
        record["status"] = "COMPLETE"
    except (ValueError, OSError, UnicodeError, subprocess.SubprocessError, hea_panel_readout.Fatal) as error:
        record["reason"] = str(error)
        suffix = ".KILLED" if record["status"] == "KILLED" else ".REJECTED"
        with (directory / (name + suffix)).open("x", encoding="utf-8") as handle:
            handle.write(str(error) + "\n")
    for key, path in (("output_sha256", output), ("runtime_sha256", runtime)):
        if path.exists():
            record[key] = digest(path)
    with (directory / (name + ".qc.json")).open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({k: record[k] for k in ("row", "site", "job", "status")}), flush=True)
    return 0 if record["status"] == "COMPLETE" else 10


def main(argv=None):
    def interrupted(signum, frame):
        raise InterruptedError("scheduler/process signal " + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--pseudo", required=True, type=Path)
    parser.add_argument("--qe", type=Path)
    parser.add_argument("--row", type=int)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    if args.preflight:
        validate(spec, args.root, pseudo=args.pseudo)
        print("VALID: nine primary atomic relaxations")
        return 0
    if args.row is None or args.qe is None:
        parser.error("execution requires --row and --qe")
    return run(spec, args.root, args.row, args.pseudo, args.qe)


if __name__ == "__main__":
    raise SystemExit(main())
