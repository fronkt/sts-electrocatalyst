#!/usr/bin/env python3
"""Run a bounded, three-arm QE 7.5 tiny restart probe on an existing allocation.

This is an experiment launcher, not a production relaxation driver. It never
submits jobs or removes user data. All paths and executable/pseudopotential pins
must be supplied explicitly; the output directory must not already exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


QE_VERSION = "7.5"
QE_SHA256 = "1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1"
H_UPF_SHA256 = "27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962"
H_UPF_NAME = "H.pbe-rrkjus_psl.1.0.0.UPF"
MAX_WALL_SECONDS = 6900
MAX_ARM_SECONDS = 1200
ALLOCATED_CORES = 4
SLURM_MAX_SECONDS = 7200

# EXIT is requested during the first BFGS move; saved XML/history, not the
# output marker alone, verify a nonzero proposal and the clean-stop boundary.
USER_STOP_MARKER = "Program stopped by user request"
CONVERGED_MARKER = "bfgs converged in"
FAILURE = re.compile(r"convergence NOT achieved|Error in routine|MPI_ABORT|SIGTERM|"
                     r"SIGINT|SIGSEGV|Segmentation fault|Floating point exception|"
                     r"IEEE_(?:INVALID|OVERFLOW|DIVIDE_BY_ZERO)_FLAG|forrtl:\s*severe", re.I)


class ProbeError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_allocation(env: Dict[str, str]) -> Tuple[int, int]:
    """Require the user's single-task four-core shared allocation."""
    raw_cpus = env.get("SLURM_CPUS_PER_TASK")
    raw_time = env.get("SLURM_JOB_TIME_LIMIT") or env.get("SLURM_TIMELIMIT")
    if not raw_cpus or not raw_time:
        raise ProbeError("must run inside Slurm with SLURM_CPUS_PER_TASK and SLURM_JOB_TIME_LIMIT set")
    try:
        cpus = int(raw_cpus)
    except ValueError as exc:
        raise ProbeError("SLURM_CPUS_PER_TASK must be an integer") from exc
    seconds = parse_slurm_time(raw_time)
    if cpus != ALLOCATED_CORES:
        raise ProbeError("this probe requires exactly 4 allocated cores")
    if not env.get("SLURM_JOB_ID"):
        raise ProbeError("this probe must run inside a live Slurm job")
    if env.get("SLURM_JOB_PARTITION") != "shared":
        raise ProbeError("this probe requires the shared Slurm partition")
    if env.get("SLURM_JOB_ACCOUNT") != "che260157":
        raise ProbeError("this probe requires the che260157 Slurm account")
    if env.get("SLURM_NTASKS") != "1":
        raise ProbeError("this probe requires exactly one Slurm task")
    if env.get("SLURM_CPUS_ON_NODE") and int(env["SLURM_CPUS_ON_NODE"]) != ALLOCATED_CORES:
        raise ProbeError("allocated node CPU count does not match the four-core probe")
    if seconds <= 0 or seconds > SLURM_MAX_SECONDS:
        raise ProbeError("Slurm time limit must be positive and no more than 02:00:00")
    return cpus, seconds


def parse_slurm_time(value: str) -> int:
    """Parse Slurm time limit: minutes, MM:SS, HH:MM:SS, or D-HH:MM:SS."""
    text = value.strip()
    if text.isdigit():
        return int(text) * 60
    days = 0
    if "-" in text:
        day_part, text = text.split("-", 1)
        if not day_part.isdigit():
            raise ProbeError("invalid Slurm time limit")
        days = int(day_part)
    fields = text.split(":")
    if len(fields) not in (2, 3) or not all(f.isdigit() for f in fields):
        raise ProbeError("invalid Slurm time limit")
    nums = [int(f) for f in fields]
    if len(nums) == 2:
        hours, minutes, seconds = 0, nums[0], nums[1]
    else:
        hours, minutes, seconds = nums
    if (len(nums) == 3 and minutes >= 60) or seconds >= 60:
        raise ProbeError("invalid Slurm time limit")
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def allocation_receipt(job_id: str) -> dict:
    result = subprocess.run(["scontrol", "show", "job", job_id, "-o"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, timeout=15, check=True)
    fields = dict(re.findall(r"(?:^|\s)([^\s=]+)=([^\s]+)", result.stdout))
    expected = {"JobId": job_id, "Account": "che260157", "Partition": "shared",
                "JobState": "RUNNING", "NumCPUs": "4", "NumTasks": "1", "CPUs/Task": "4"}
    if any(fields.get(k) != v for k,v in expected.items()):
        raise ProbeError("actual scheduler allocation differs from four-core shared job")
    if parse_slurm_time(fields.get("TimeLimit", "")) > SLURM_MAX_SECONDS:
        raise ProbeError("actual scheduler wall limit exceeds approved cap")
    tres = dict(item.split("=", 1) for item in fields.get("AllocTRES", "").split(",") if "=" in item)
    if tres.get("cpu") != "4" or tres.get("billing") != "4":
        raise ProbeError("actual scheduler CPU/billing allocation exceeds cap or is unverified")
    return {"command": result.args, "stdout": result.stdout, "stderr": result.stderr,
            "fields": fields, "allocated_tres": tres}


def validate_paths(output: Path, binary: Path, pseudo: Path) -> Tuple[Path, Path, Path]:
    output = output.expanduser().absolute()
    binary = binary.expanduser().resolve(strict=True)
    pseudo = pseudo.expanduser().resolve(strict=True)
    if output.exists() or output.is_symlink():
        raise ProbeError("output directory already exists; choose a fresh nonexistent directory")
    if not binary.is_file() or not os.access(str(binary), os.X_OK):
        raise ProbeError("QE binary must be an executable file")
    if not pseudo.is_file() or pseudo.name != H_UPF_NAME:
        raise ProbeError("pseudo must be the pinned H.pbe-rrkjus_psl.1.0.0.UPF file")
    return output, binary, pseudo


def input_text(prefix: str, outdir: Path, pseudo_dir: Path, restart: bool = False,
               nstep: int = 30, fresh: bool = False,
               positions: Optional[Sequence[Sequence[float]]] = None) -> str:
    """Fixed minimal H2 cell and identical settings across probe arms."""
    restart_mode = "restart" if restart else "from_scratch"
    restart_line = "    restart_mode = '{}',\n".format(restart_mode)
    pos = positions or ((0.0, 0.0, 0.0), (0.0, 0.0, 2.0))
    if len(pos) != 2 or any(len(row) != 3 for row in pos):
        raise ProbeError("H2 positions must contain exactly two three-coordinate rows")
    if any(type(v) not in (int, float) or not math.isfinite(v) for row in pos for v in row):
        raise ProbeError("finite H2 positions required")
    if type(nstep) is not int or not 1 <= nstep <= 30:
        raise ProbeError("ionic step budget must be between1 and30")
    position_lines = "\n".join("H {:.12f} {:.12f} {:.12f}".format(*row) for row in pos)
    return f"""&CONTROL
    calculation = 'relax',
{restart_line}    prefix = '{prefix}',
    outdir = '{outdir.as_posix()}/',
    pseudo_dir = '{pseudo_dir.as_posix()}/',
    tstress = .false.,
    tprnfor = .true.,
    etot_conv_thr = 1.0d-7,
    forc_conv_thr = 1.0d-4,
    nstep = {nstep},
    disk_io = 'low',
    max_seconds = {MAX_ARM_SECONDS - 20},
/
&SYSTEM
    ibrav = 0,
    nat = 2,
    ntyp = 1,
    ecutwfc = 40.0,
    ecutrho = 320.0,
    occupations = 'fixed',
    nspin = 1,
/
&ELECTRONS
    conv_thr = 1.0d-10,
    diago_thr_init = 1.0d-7,
    electron_maxstep = 100,
    mixing_beta = 0.3,
/
&IONS
    ion_dynamics = 'bfgs',
/
ATOMIC_SPECIES
H 1.00794 {H_UPF_NAME}
ATOMIC_POSITIONS bohr
{position_lines}
K_POINTS gamma
CELL_PARAMETERS bohr
20.000000 0.000000 0.000000
0.000000 20.000000 0.000000
0.000000 0.000000 20.000000
"""


def set_single_rank_environment(binary: Optional[Path] = None) -> Dict[str, str]:
    env = os.environ.copy()
    if binary is not None:
        env["PATH"] = str(binary.parent) + os.pathsep + env.get("PATH", "")
        env["LD_LIBRARY_PATH"] = str(binary.parent.parent / "lib") + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[name] = "1"
    env["OMP_DYNAMIC"] = "FALSE"
    return env


class StreamCapture:
    """Persist child output immediately while keeping a searchable live tail."""
    def __init__(self, pipe, destination: Path):
        self.pipe = pipe
        self.destination = destination
        self.text = ""
        self._lock = threading.Lock()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def _run(self) -> None:
        with self.destination.open("w", encoding="utf-8", errors="replace", buffering=1) as out:
            while True:
                data = self.pipe.readline()
                if not data:
                    break
                if isinstance(data, bytes):
                    data = data.decode("utf-8", errors="replace")
                out.write(data)
                out.flush()
                with self._lock:
                    self.text += data


def inventory(root: Path) -> List[dict]:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ProbeError("checkpoint trees containing symlinks are not accepted")
        if path.is_file():
            rows.append({"path": path.relative_to(root).as_posix(),
                         "size": path.stat().st_size,
                         "sha256": sha256_file(path)})
    return rows


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for entry in inventory(root):
        h.update(entry["path"].encode("utf-8"))
        h.update(b"\0")
        h.update(entry["sha256"].encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def output_counts(output: str) -> dict:
    """Return transparent log counts, not inferred scientific stage totals."""
    return {
        "atomic_position_blocks": len(list(re.finditer(r"(?im)^\s*ATOMIC_POSITIONS\s*\([^)]*\)", output))),
        "reported_total_energies": len(re.findall(r"(?im)^\s*!\s+total energy\s*=", output)),
        "reported_bfgs_iterations": len(re.findall(r"(?im)^\s*iteration\s+#\s*\d+", output)),
    }


def first_bfgs_trigger(output: str):
    """First optimizer call only; later Wolfe/trust markers are not boundaries."""
    match = re.search(r"(?im)^[ \t]*number of bfgs steps[ \t]*=[ \t]*(\d+)[ \t]*$", output)
    return match if match and int(match.group(1)) == 0 else None


def last_logged_h2_positions(output: str) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """Parse the last logged two-H geometry, requiring bohr units."""
    matches = list(re.finditer(r"(?im)^\s*ATOMIC_POSITIONS\s*\(bohr\)\s*\n", output))
    for match in reversed(matches):
        rows = output[match.end():].splitlines()[:2]
        try:
            parsed = []
            for row in rows:
                fields = row.split()
                if fields[0] != "H":
                    raise ValueError("expected H")
                parsed.append(tuple(float(x.replace("D", "E").replace("d", "e")) for x in fields[1:4]))
        except (ValueError, IndexError):
            continue
        if len(parsed) == 2 and all(len(row) == 3 for row in parsed):
            return parsed[0], parsed[1]
    raise ProbeError("candidate output does not contain a valid two-H bohr geometry")


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stop_child(proc: subprocess.Popen, grace_seconds: float = 8.0) -> None:
    if proc.poll() is not None:
        return
    # Only a fallback after the caller's EXIT grace period. This is a failure,
    # never a clean checkpoint or an accepted energy.
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def run_arm(name: str, argv: Sequence[str], cwd: Path, env: Dict[str, str],
            timeout: int, trigger_move: bool = False) -> dict:
    start = time.monotonic()
    result = {"arm": name, "argv": list(argv), "trigger": None,
              "returncode": None, "timed_out": False}
    proc = subprocess.Popen(argv, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1, close_fds=True)
    result["owned_pid"] = proc.pid
    stdout = StreamCapture(proc.stdout, cwd / "stdout.log")
    stderr = StreamCapture(proc.stderr, cwd / "stderr.log")
    stdout.start()
    stderr.start()
    marker_seen = False
    try:
        while proc.poll() is None:
            elapsed = time.monotonic() - start
            if elapsed >= timeout:
                result["timed_out"] = True
                result["trigger"] = "arm-timeout"
                (cwd / "h2_probe.EXIT").write_text("timeout stop; rejected result\n", encoding="utf-8")
                try:
                    proc.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    stop_child(proc)
                break
            with stdout._lock:
                captured = stdout.text
            # The first count0 marker is inside the first BFGS call, after
            # the post-SCF stop poll and XML step. QE completes that move;
            # EXIT is next polled in the following SCF. Verify saved state
            # after shutdown rather than assume observer timing succeeded.
            if trigger_move:
                first_call = first_bfgs_trigger(captured)
                if CONVERGED_MARKER.lower() in captured.lower():
                    result["trigger"] = "converged-before-trigger"
                    break
                if first_call:
                    result["trigger"] = "request-during-first-bfgs-call"
                    marker_seen = True
                    result["trigger_time_elapsed_seconds"] = round(time.monotonic() - start, 3)
                    result["trigger_observed_counts"] = output_counts(captured)
                    result["exit_receipt"] = {"path": str(cwd / "h2_probe.EXIT"),
                        "trigger_line": first_call.group(0).strip(),
                        "trigger_line_number": captured[:first_call.start()].count("\n") + 1,
                        "created_utc": datetime.now(timezone.utc).isoformat(),
                        "monotonic_seconds": time.monotonic()}
                    (cwd / "h2_probe.EXIT").write_text(
                        "requested during first BFGS call; boundary verified after stop\n", encoding="utf-8")
                    trigger_move = False
            time.sleep(0.005)
        if proc.poll() is None:
            proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        result["timed_out"] = True
        result["trigger"] = result["trigger"] or "wait-timeout"
        stop_child(proc)
    finally:
        stdout.thread.join(timeout=10)
        stderr.thread.join(timeout=10)
    result["returncode"] = proc.returncode
    result["elapsed_seconds"] = round(time.monotonic() - start, 3)
    result["move_trigger_observed"] = marker_seen
    result["output_counts"] = output_counts(stdout.text)
    return result


def nonzero_move_observed(output: str) -> bool:
    """Compare logged geometries with the exact two-angstrom-free input (bohr)."""
    sections = list(re.finditer(r"(?im)^\s*ATOMIC_POSITIONS\s*\([^)]*\)\s*\n", output))
    initial = [(0.0, 0.0, 0.0), (0.0, 0.0, 2.0)]
    for match in sections:
        lines = output[match.end():].splitlines()[:2]
        try:
            vals = []
            for line in lines:
                fields = line.split()
                vals.append(tuple(float(x.replace("D", "E").replace("d", "e")) for x in fields[1:4]))
        except (ValueError, IndexError):
            continue
        if len(vals) == 2 and any(abs(vals[i][j] - initial[i][j]) > 1e-8 for i in range(2) for j in range(3)):
            return True
    return False


def snapshot_checkpoint(source: Path, dest: Path) -> None:
    if not source.is_dir():
        raise ProbeError("continuous control did not create its QE scratch directory")
    if dest.exists():
        raise ProbeError("refusing to overwrite checkpoint snapshot")
    inventory(source)  # Refuse symlinks before copytree can follow them.
    shutil.copytree(source, dest)


def checkpoint_geometry(scratch: Path):
    """Saved post-move proposal, not the previous energy's geometry."""
    tree = ET.parse(scratch / "h2_probe.save/data-file-schema.xml")
    root = tree.getroot()
    if "Hartree atomic units" not in root.attrib.get("Units", ""):
        raise ProbeError("checkpoint unit convention is not explicit")
    def tag(node):
        return node.tag.rsplit("}", 1)[-1]
    outputs = [n for n in root if tag(n) == "output"]
    if len(outputs) != 1:
        raise ProbeError("one checkpoint output required")
    structures = [n for n in outputs[0] if tag(n) == "atomic_structure"]
    if len(structures) != 1:
        raise ProbeError("one saved atomic structure required")
    positions = [n for n in structures[0] if tag(n) == "atomic_positions"]
    if len(positions) != 1:
        raise ProbeError("one saved positions block required")
    atoms = list(positions[0])
    if len(atoms) != 2 or any(n.attrib.get("name") != "H" for n in atoms):
        raise ProbeError("saved checkpoint is not ordered H2")
    coords = [tuple(float(v.replace("D", "e")) for v in (n.text or "").split()) for n in atoms]
    if any(len(row) != 3 or any(not math.isfinite(v) for v in row) for row in coords):
        raise ProbeError("invalid saved checkpoint geometry")
    steps = [n for n in root if tag(n) == "step"]
    status = [n for n in root if tag(n) == "exit_status"]
    if len(status) != 1 or int(status[0].text) != 255:
        raise ProbeError("saved QE status must be the documented clean interruption255")
    return coords, len(steps)


def local_tag(node):
    return node.tag.rsplit("}", 1)[-1]


def checkpoint_optimizer(scratch: Path, pseudo: Path) -> dict:
    """QE7.5 H2 has3*nat+10=16 scaled optimizer dimensions, even fixed-cell."""
    saved_upf = scratch / "h2_probe.save" / H_UPF_NAME
    if not pseudo.is_file() or sha256_file(pseudo) != H_UPF_SHA256:
        raise ProbeError("external hydrogen pseudopotential pin changed")
    if saved_upf.exists() and (not saved_upf.is_file() or sha256_file(saved_upf) != H_UPF_SHA256):
        raise ProbeError("checkpoint UPF differs from pinned hydrogen pseudopotential")
    root = ET.parse(scratch / "h2_probe.save/data-file-schema.xml").getroot()
    outputs = [n for n in root if local_tag(n) == "output"]
    pseudo_names = [n.text.strip() for n in outputs[0].iter()
                    if local_tag(n) == "pseudo_file" and n.text]
    if pseudo_names != [H_UPF_NAME]:
        raise ProbeError("checkpoint XML pseudopotential identity is not pinned H")
    tokens = (scratch / "h2_probe.bfgs").read_text(encoding="utf-8").split()
    # Two16-dimensional vectors, then SCF/BFGS/GDIIS counts, then prior energy;
    # the retained full file also holds histories/Hessian/trust data.
    if len(tokens) != 326:
        raise ProbeError("unexpected QE7.5 two-H optimizer state dimensions")
    values = [float(v.replace("D", "e")) for v in tokens]
    if not all(math.isfinite(v) for v in values):
        raise ProbeError("nonfinite optimizer checkpoint")
    if values[32:35] != [1,1,0]:
        raise ProbeError("single first-move SCF/BFGS checkpoint counters not attained")
    return {"scf_iter":1, "bfgs_iter":1, "gdiis_iter":0,
            "scaled_prior_positions": values[:16], "scaled_prior_gradient": values[16:32],
            "prior_energy_Ry": values[35], "sha256": sha256_file(scratch / "h2_probe.bfgs"),
            "external_upf_sha256": sha256_file(pseudo),
            "saved_upf_present": saved_upf.is_file(),
            "saved_upf_sha256": sha256_file(saved_upf) if saved_upf.is_file() else None,
            "pinned_external_upf_fallback": not saved_upf.is_file()}


def completed_arm(arm: Path, receipt: dict, kind: str, proposal) -> dict:
    output = (arm / "stdout.log").read_text(encoding="utf-8")
    stderr = (arm / "stderr.log").read_text(encoding="utf-8")
    if (receipt["returncode"] != 0 or receipt["timed_out"] or FAILURE.search(output+stderr)
            or "JOB DONE." not in output or CONVERGED_MARKER not in output.lower()
            or USER_STOP_MARKER in output or "maximum number of steps" in output.lower()
            or "Maximum CPU time" in output or "Maximum wall time" in output):
        raise ProbeError(kind + " arm did not converge normally; no automatic retry")
    counts = [int(v) for v in re.findall(r"number of bfgs steps\s*=\s*(\d+)",output)]
    cycles = [int(v) for v in re.findall(r"number of scf cycles\s*=\s*(\d+)",output)]
    if kind == "negative":
        if ".bfgs deleted, as requested" not in output or not counts or counts[0] != 0:
            raise ProbeError("negative control did not prove copied optimizer reset")
    else:
        if ("restart disabled: needed files not found" in output.lower()
                or re.search(r"(?m)^\s*BFGS Geometry Optimization\s*$",output)
                or ".bfgs deleted, as requested" in output
                or not counts or counts[0] != 1 or not cycles or cycles[0] != 2):
            raise ProbeError("resumed arm did not prove inherited optimizer counters")
        root = ET.parse(arm / "scratch/h2_probe.save/data-file-schema.xml").getroot()
        steps = [n for n in root if local_tag(n) == "step"]
        if not steps:
            raise ProbeError("resumed evaluated trajectory missing")
        atoms = [n for n in steps[0].iter() if local_tag(n) == "atom"]
        positions = [[float(v.replace("D","e")) for v in (n.text or "").split()] for n in atoms]
        if len(positions)!=2 or any(len(p)!=3 for p in positions):
            raise ProbeError("resumed first evaluated geometry malformed")
        if any(not math.isfinite(v) for p in positions for v in p):
            raise ProbeError("resumed evaluated geometry nonfinite")
        if max(abs(a-b) for p,q in zip(positions,proposal) for a,b in zip(p,q)) > 1e-5:
            raise ProbeError("resumed first evaluated geometry differs from saved proposal")
    return {"first_bfgs_count":counts[0], "first_scf_cycle":cycles[0] if cycles else None,
            "qualitative_control_gate": True, "full_trajectory_review_required": True}


def checkpoint_files(root: Path) -> List[Path]:
    return [p for p in root.rglob("*") if p.is_file() and
            (p.name.endswith(".bfgs") or "restart" in p.name.lower() or p.suffix.lower() in {".xml", ".dat"})]


def prepare_arm_dir(root: Path, name: str, input_body: str, pseudo: Path) -> Path:
    if sha256_file(pseudo) != H_UPF_SHA256:
        raise ProbeError("external hydrogen pseudopotential pin changed before arm")
    arm = root / name
    arm.mkdir()
    (arm / "input.in").write_text(input_body, encoding="utf-8")
    shutil.copy2(pseudo, arm / H_UPF_NAME)
    if sha256_file(arm / H_UPF_NAME) != H_UPF_SHA256:
        raise ProbeError("arm-local hydrogen pseudopotential copy differs from pin")
    write_json(arm / "input_manifest.json", {"input_sha256":sha256_file(arm / "input.in"),
        "upf_path":str(arm / H_UPF_NAME), "upf_sha256":H_UPF_SHA256})
    return arm


def run_probe(args: argparse.Namespace) -> int:
    cpus, slurm_seconds = validate_allocation(os.environ)
    allocation = allocation_receipt(os.environ["SLURM_JOB_ID"])
    output, binary, pseudo = validate_paths(args.output_dir, args.qe_binary, args.pseudo)
    if sha256_file(binary).lower() != QE_SHA256:
        raise ProbeError("QE executable SHA-256 does not match the pinned QE 7.5 build")
    if sha256_file(pseudo).lower() != H_UPF_SHA256:
        raise ProbeError("H pseudopotential SHA-256 does not match the pinned file")
    if args.expected_qe_sha256.lower() != QE_SHA256 or args.expected_pseudo_sha256.lower() != H_UPF_SHA256:
        raise ProbeError("expected hash arguments must equal the pinned hashes in this runner")

    output.mkdir(parents=True, exist_ok=False)
    root_start = time.monotonic()
    metadata = {"started_utc": datetime.now(timezone.utc).isoformat(),
                "qe_version_expected": QE_VERSION, "qe_sha256": QE_SHA256,
                "pseudo_name": H_UPF_NAME, "pseudo_sha256": H_UPF_SHA256,
                "input_pseudo_strategy":"arm-local pinned copies; saved UPF preferred if present",
                "allocated_cores": cpus, "slurm_time_limit_seconds": slurm_seconds,
                "max_wall_seconds": min(MAX_WALL_SECONDS, slurm_seconds - 60),
                "experimental_only": True,
                "scheduler_receipt": allocation,
                "acceptance": "manual review required; no production acceptance flag"}
    write_json(output / "run.json", metadata)
    env = set_single_rank_environment(binary)
    # Direct execution preserves MPI singleton mode and uses one allocated CPU.
    common = dict(prefix="h2_probe")
    deadline = root_start + min(MAX_WALL_SECONDS, slurm_seconds - 60)

    def arm_timeout() -> int:
        remaining = int(deadline - time.monotonic())
        if remaining <= 0:
            raise ProbeError("global probe deadline reached before next arm")
        return min(MAX_ARM_SECONDS, remaining)
    control = prepare_arm_dir(output, "continuous", input_text(outdir=(output / "continuous" / "scratch"),
        pseudo_dir=(output / "continuous"), fresh=True, **common), pseudo)
    seed = run_arm("continuous", [str(binary), "-in", "input.in"], control, env, arm_timeout(), trigger_move=False)
    write_json(control / "receipt.json", seed)
    control_text = (control / "stdout.log").read_text(encoding="utf-8", errors="replace")
    version_lines = re.findall(r"(?m)^\s*Program PWSCF v\.7\.5 starts[^\n]*", control_text)
    (output / "qe-version.txt").write_text("\n".join(version_lines) + "\n", encoding="utf-8")
    if not version_lines:
        raise ProbeError("first QE run did not report the pinned 7.5 version banner")
    if (seed["returncode"] != 0 or seed["timed_out"] or FAILURE.search(control_text)
            or CONVERGED_MARKER not in control_text.lower() or "JOB DONE." not in control_text):
        raise ProbeError("continuous control did not converge normally")
    snapshot_checkpoint(control / "scratch", output / "checkpoint-original")
    cp_files = checkpoint_files(output / "checkpoint-original")
    checkpoint_ok = bool(cp_files)

    # Independent candidate seed: begin from pristine input, then request QE's
    # ordinary safe-point stop after the first observed nonzero ionic move.
    candidate_dir = prepare_arm_dir(output, "candidate-stop", input_text(
        outdir=(output / "candidate-stop" / "scratch"), pseudo_dir=(output / "candidate-stop"),
        fresh=True, **common), pseudo)
    candidate = run_arm("candidate-stop", [str(binary), "-in", "input.in"], candidate_dir,
                        env, arm_timeout(), trigger_move=True)
    write_json(candidate_dir / "receipt.json", candidate)
    candidate_text = (candidate_dir / "stdout.log").read_text(encoding="utf-8", errors="replace")
    candidate_clean_stop = USER_STOP_MARKER.lower() in candidate_text.lower()
    if (not candidate.get("move_trigger_observed") or not candidate_clean_stop
            or candidate["timed_out"] or candidate["returncode"] not in (0, 255)
            or "JOB DONE." not in candidate_text or FAILURE.search(candidate_text)):
        write_json(output / "report.json", {
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "candidate_stop": candidate,
            "candidate_stop_has_clean_exit_receipt": candidate_clean_stop,
            "candidate_move_trigger_observed": candidate.get("move_trigger_observed", False),
            "interpretation": "inconclusive: candidate did not show a nonzero move and QE clean user-stop receipt"})
        return 2
    proposal_positions, completed_moves = checkpoint_geometry(candidate_dir / "scratch")
    if completed_moves != 1:
        raise ProbeError("single-move stop not attained; preserve attempt without automatic retry")
    initial = ((0.,0.,0.),(0.,0.,2.))
    if max(abs(a-b) for p,q in zip(proposal_positions,initial) for a,b in zip(p,q)) <= 1e-8:
        raise ProbeError("saved proposal has no nonzero ionic displacement")
    saved_optimizer = checkpoint_optimizer(candidate_dir / "scratch", candidate_dir / H_UPF_NAME)
    snapshot_checkpoint(candidate_dir / "scratch", output / "checkpoint-stopped")
    stopped_files = checkpoint_files(output / "checkpoint-stopped")
    stopped_bfgs = [p for p in stopped_files if p.name.endswith(".bfgs") and p.stat().st_size > 0]
    if not stopped_bfgs:
        raise ProbeError("clean-stop optimizer history missing")
    stopped_digest = tree_digest(output / "checkpoint-stopped")

    # Both arms receive byte copies of one immutable checkpoint and use the
    # exact same prefix in isolated save directories.
    negative_dir = prepare_arm_dir(output, "negative-fresh", input_text(
        outdir=(output / "negative-fresh" / "scratch"), pseudo_dir=(output / "negative-fresh"), fresh=True,
        positions=proposal_positions, **common), pseudo)
    shutil.copytree(output / "checkpoint-stopped", negative_dir / "scratch")
    if tree_digest(negative_dir / "scratch") != stopped_digest:
        raise ProbeError("negative control checkpoint copy failed immutable hash verification")
    negative = run_arm("negative-fresh", [str(binary), "-in", "input.in"], negative_dir,
                       env, arm_timeout(), trigger_move=False)
    write_json(negative_dir / "receipt.json", negative)
    negative_gate = completed_arm(negative_dir, negative, "negative", proposal_positions)

    resumed_dir = prepare_arm_dir(output, "resumed", input_text(
        outdir=(output / "resumed" / "scratch"), pseudo_dir=(output / "resumed"), restart=True,
        nstep=30 - completed_moves, positions=proposal_positions, **common), pseudo)
    shutil.copytree(output / "checkpoint-stopped", resumed_dir / "scratch")
    if tree_digest(resumed_dir / "scratch") != stopped_digest:
        raise ProbeError("resumed checkpoint copy failed immutable hash verification")
    resumed = run_arm("resumed", [str(binary), "-in", "input.in"], resumed_dir,
                      env, arm_timeout(), trigger_move=False)
    write_json(resumed_dir / "receipt.json", resumed)
    resumed_gate = completed_arm(resumed_dir, resumed, "resumed", proposal_positions)

    elapsed = time.monotonic() - root_start
    report = {
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "within_global_limit": elapsed <= min(MAX_WALL_SECONDS, slurm_seconds - 60),
        "continuous": seed, "candidate_stop": candidate,
        "checkpoint_inventory": {"continuous": inventory(output / "checkpoint-original"),
                                  "candidate_stopped": inventory(output / "checkpoint-stopped")},
        "checkpoint_required_files_present": checkpoint_ok and bool(stopped_files and stopped_bfgs),
        "candidate_stop_has_clean_exit_receipt": USER_STOP_MARKER.lower() in (candidate_dir / "stdout.log").read_text(encoding="utf-8", errors="replace").lower(),
        "candidate_move_trigger_observed": candidate.get("move_trigger_observed", False),
        "candidate_post_stop_positions_bohr": proposal_positions,
        "completed_moves_at_stop": completed_moves,
        "resumed_nstep_budget": 30 - completed_moves,
        "immutable_checkpoint_sha256": stopped_digest,
        "saved_optimizer": saved_optimizer,
        "negative_gate": negative_gate, "resumed_gate": resumed_gate,
        "negative_fresh": negative, "resumed": resumed,
        "interpretation": "manual review required; this report does not establish production restart safety",
    }
    write_json(output / "report.json", report)
    return 0 if report["within_global_limit"] and checkpoint_ok else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--qe-binary", required=True, type=Path)
    parser.add_argument("--pseudo", required=True, type=Path)
    parser.add_argument("--expected-qe-sha256", required=True)
    parser.add_argument("--expected-pseudo-sha256", required=True)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        return run_probe(build_parser().parse_args(argv))
    except (ProbeError, OSError, subprocess.SubprocessError) as exc:
        print("probe error: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
