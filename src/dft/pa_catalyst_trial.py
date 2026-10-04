"""One licensed catalyst P-A boundary trial; no submission or production driver.

The dated, externally hash-pinned spec is launch authority. Every QE call has
the same MPI shape, an independent two-hour ceiling, and a live Slurm check.
Numerical inconclusive outcomes remain distinct from allocation compliance.
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
import stat
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence


QE_SHA256 = "1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1"
MPI_SHA256 = "a256bdcef89bdc61ba870e823056c51df868b4db48ab345a14278a7fe79ed75d"
TARGET = "Cu8Cr23Mn35Co34__s20_site2"
SOURCE_DECK_SUFFIX = "runs/hea/lowtail_low_state_restart_2026-09-22/" + TARGET + "/slab_c5low__relax.in"
SOURCE_DECK_SHA256 = "dfed65abc93a5eb5ef350c31f963fd6044c5b6e68fd39904063a0292de5f8539"
SEED_ROOT = "/anvil/projects/x-che260157/sts/runs/hea/lowtail_slab_scf_diag_2026-09-19/" + TARGET + "/tmp_slab_c5__b030/slab_c5__b030.save"
SEED_FILES = {
    "charge-density.hdf5": "0aa143855c85a12e0e3ac2cc741b9b324faec9ca4ccbe85183b6550e4fe2f645",
    "data-file-schema.xml": "2360316d4d5d759bfce9e8f6dbb024acd3315df12f1039a71fb28898ae2ae0fd",
    "occup.txt": "0de270621acad688e345b1253cfef5dbe185a3deb1b65811aa3b4bbe44000f14",
    "paw.txt": "0972e5ad8882198aff44573a91144e50b370786454b68004c330330ab8a8449d",
}
CAPS = {"max_calls": 6, "per_call_seconds": 7200, "qe_max_seconds": 7080,
        "cleanup_seconds": 120, "aggregate_seconds": 57600}
SHAPE = {"nprocs": 128, "nthreads": 1, "ntasks": 1,
         "nbgrp": 1, "npool": 8, "ndiag": 16}
PREFIX = "slab_c5low__pa_boundary"
SCF_CYCLE = re.compile(r"(?m)^[ \t]*number of scf cycles[ \t]*=[ \t]*(\d+)[ \t]*$")
SCF_ITERATION = re.compile(r"(?m)^[ \t]*iteration[ \t]*#[ \t]*(\d+)")
FAILURE = re.compile(
    r"convergence NOT achieved|Error in routine|MPI_ABORT|SIGTERM|SIGINT|SIGSEGV|"
    r"Segmentation fault|Floating point exception|IEEE_(?:INVALID|OVERFLOW|DIVIDE_BY_ZERO)_FLAG|"
    r"forrtl:\s*severe|bfgs failed|history already reset.*(?:stopping|exiting)|"
    r"restart disabled", re.I)
TIME_FAILURE = re.compile(r"Maximum (?:CPU|wall) time|maximum number of steps", re.I)
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class TrialError(RuntimeError):
    """A refusal or unusable scientific outcome; never an implicit retry."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _strict_int(value, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise TrialError(label + " must be an integer in the registered range")
    return value


def _pin(value, label: str) -> dict:
    if (not isinstance(value, dict) or not isinstance(value.get("path"), str)
            or not value["path"] or not isinstance(value.get("sha256"), str)
            or not SHA256.fullmatch(value["sha256"])):
        raise TrialError(label + " requires an exact file path and lowercase SHA-256")
    return value


def validate_spec(spec: dict) -> dict:
    """Validate immutable scientific identity and all user ceilings before writes."""
    if not isinstance(spec, dict) or spec.get("schema") != "pa-catalyst-trial-v1":
        raise TrialError("wrong catalyst trial schema")
    if spec.get("date") != "2026-10-03" or spec.get("target") != TARGET:
        raise TrialError("trial date or singleton target differs")
    if spec.get("caps") != CAPS or any(type(v) is not int for v in spec["caps"].values()):
        raise TrialError("call, per-call, cleanup, or aggregate ceilings differ")
    if spec.get("parallel_shape") != SHAPE or any(type(v) is not int for v in spec["parallel_shape"].values()):
        raise TrialError("MPI/pool/thread/diagonalization shape differs")
    allocation = spec.get("allocation", {})
    exact = {"account": "che260157", "partition": "wholenode", "cpus": 128,
             "tasks": 128, "cpus_per_task": 1, "billing": 128,
             "time_limit_seconds": 57600, "max_cpu_su": 2048}
    for field, value in exact.items():
        if allocation.get(field) != value or type(allocation.get(field)) is not type(value):
            raise TrialError("allocation cap differs: " + field)
    _strict_int(allocation.get("memory_gib"), "memory_gib", 1, 200)
    if type(spec.get("optional_negative_control")) is not bool:
        raise TrialError("optional_negative_control must be an explicit bool")
    for key in ("source_deck", "pw_x", "mpirun", "source_review"):
        _pin(spec.get(key), key)
    if spec["pw_x"]["sha256"] != QE_SHA256 or spec["mpirun"]["sha256"] != MPI_SHA256:
        raise TrialError("pinned QE7.5 or OpenMPI build differs")
    if not spec["source_deck"]["path"].replace("\\", "/").endswith(SOURCE_DECK_SUFFIX):
        raise TrialError("source deck is not the registered cycle5 low-state slab")
    if spec["source_deck"]["sha256"] != SOURCE_DECK_SHA256:
        raise TrialError("registered cycle5 source-deck byte pin differs")
    dependencies = spec.get("dependencies")
    upfs = spec.get("upfs")
    if not isinstance(dependencies, list) or not dependencies:
        raise TrialError("controller dependency pins required")
    if not isinstance(upfs, list) or len(upfs) != 5:
        raise TrialError("exactly five pseudopotential pins required")
    for label, entries in (("dependency", dependencies), ("UPF", upfs)):
        for entry in entries:
            _pin(entry, label)
        paths = [entry["path"] for entry in entries]
        if len(paths) != len(set(paths)):
            raise TrialError("duplicate " + label + " paths")
    names = {Path(pin["path"]).name for pin in dependencies}
    if not {"pa_catalyst_trial.py", "pa_qe_adapter.py", "pa_checked_contract.py"}.issubset(names):
        raise TrialError("supervisor, adapter, and contract dependency pins required")
    seed = spec.get("initial_seed", {})
    if seed.get("root") != SEED_ROOT or not isinstance(seed.get("files"), list):
        raise TrialError("historical low-state initialization root differs")
    files = seed["files"]
    if len(files) != 4 or {f.get("path"): f.get("sha256") for f in files} != SEED_FILES:
        raise TrialError("historical four-file initialization pins differ")
    for entry in files:
        _strict_int(entry.get("size_bytes"), "seed size_bytes", 1, 2 ** 63 - 1)
    for key in ("trial_parent", "trial_root"):
        if not isinstance(spec.get(key), str) or not Path(spec[key]).is_absolute():
            raise TrialError(key + " must be absolute")
    parent, root = Path(spec["trial_parent"]), Path(spec["trial_root"])
    if parent.name != "sts_pa_catalyst_2026-10-03" or root.parent != parent or root.name != "trial_results":
        raise TrialError("trial output is not the isolated dated checkout child")
    return spec


def _plain_path(path: Path, *, exists: bool = True) -> Path:
    """Refuse links/junctions in the complete ancestor chain, before resolving."""
    path = Path(path).absolute()
    if ".." in path.parts or path == Path(path.anchor):
        raise TrialError("broad or traversing filesystem path refused")
    for ancestor in list(reversed(path.parents)) + [path]:
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            if ancestor == path and not exists:
                continue
            raise TrialError("missing path ancestor: " + str(ancestor))
        if stat.S_ISLNK(info.st_mode) or (getattr(info, "st_file_attributes", 0) & 0x400):
            raise TrialError("symlink/reparse path refused: " + str(ancestor))
    return path


def _regular(path: Path, *, allow_external_hardlinks: bool = False) -> Path:
    path = _plain_path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or (info.st_nlink != 1 and not allow_external_hardlinks):
        raise TrialError("regular, unaliased file required: " + str(path))
    return path


def verify_pin(pin: dict, label: str, *, allow_external_hardlinks: bool = False) -> dict:
    """Read exact pins; only immutable external executables may be hardlinked.

    Conda can hardlink its pw.x installation to its package cache. These inputs
    are never written and are rehashed before each invocation. Trial inputs and
    all mutable/snapshotted checkpoint files retain strict isolation.
    """
    path = _regular(Path(pin["path"]), allow_external_hardlinks=allow_external_hardlinks)
    digest = sha256_file(path)
    if digest != pin["sha256"]:
        raise TrialError(label + " SHA-256 changed: " + str(path))
    return {"path": str(path), "sha256": digest, "size_bytes": path.stat().st_size}


def _overlap(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def inventory(root: Path) -> dict:
    """Include every file and directory, rejecting aliases and special files."""
    root = _plain_path(root)
    if not root.is_dir():
        raise TrialError("checkpoint root is not a directory")
    files, directories, inodes = [], [], set()
    for current, dir_names, file_names in os.walk(str(root), followlinks=False):
        current_path = Path(current)
        for name in sorted(dir_names + file_names):
            path = current_path / name
            info = path.lstat()
            relative = path.relative_to(root).as_posix()
            if stat.S_ISLNK(info.st_mode) or (getattr(info, "st_file_attributes", 0) & 0x400):
                raise TrialError("checkpoint symlink/reparse entry refused")
            inode = (info.st_dev, info.st_ino)
            if inode in inodes:
                raise TrialError("checkpoint filesystem alias refused")
            inodes.add(inode)
            if stat.S_ISDIR(info.st_mode):
                directories.append(relative)
            elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                files.append({"path": relative, "size_bytes": info.st_size, "sha256": sha256_file(path)})
            else:
                raise TrialError("checkpoint special/hardlinked file refused")
    if not files:
        raise TrialError("empty checkpoint cannot establish continuity")
    body = {"directories": sorted(directories), "files": sorted(files, key=lambda row: row["path"])}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return dict(body, root=str(root), sha256=digest)


def _copy_ordinary_tree(source: Path, destination: Path) -> None:
    """Never follow a file link introduced between inventory and copying."""
    source = _plain_path(source)
    destination.mkdir(mode=0o700)
    for child in sorted(source.iterdir()):
        before = child.lstat()
        target = destination / child.name
        if stat.S_ISLNK(before.st_mode) or (getattr(before, "st_file_attributes", 0) & 0x400):
            raise TrialError("checkpoint symlink/reparse entry during copy")
        if stat.S_ISDIR(before.st_mode):
            _copy_ordinary_tree(child, target)
        elif stat.S_ISREG(before.st_mode) and before.st_nlink == 1:
            descriptor = os.open(str(child), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(descriptor, "rb") as inp:
                opened = os.fstat(inp.fileno())
                if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                        or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)):
                    raise TrialError("checkpoint source alias changed during open")
                with target.open("xb") as out:
                    shutil.copyfileobj(inp, out, 1024 * 1024)
        else:
            raise TrialError("checkpoint special/hardlinked entry during copy")


def copy_tree(source: Path, destination: Path, *, immutable: bool = False) -> dict:
    source = _plain_path(source)
    destination = _plain_path(destination, exists=False)
    if destination.exists() or _overlap(source, destination):
        raise TrialError("checkpoint destination already exists or aliases source")
    before = inventory(source)
    _copy_ordinary_tree(source, destination)
    copied = inventory(destination)
    after = inventory(source)
    if before["sha256"] != copied["sha256"] or before != after:
        raise TrialError("complete checkpoint copy mismatch or source mutation")
    for current, dirs, files in os.walk(str(destination)):
        for name in files:
            (Path(current) / name).chmod(0o444 if immutable else 0o600)
        for name in dirs:
            (Path(current) / name).chmod(0o555 if immutable else 0o700)
    destination.chmod(0o555 if immutable else 0o700)
    return {"source_before": before, "source_after": after, "destination": copied,
            "immutable": immutable, "complete_recursive_copy": True}


def checkpoint_inventory(outdir: Path, wfcdir: Optional[Path] = None) -> dict:
    outdir = _plain_path(outdir)
    if wfcdir is not None:
        wfcdir = _plain_path(wfcdir)
        if _overlap(outdir, wfcdir):
            raise TrialError("distinct WFC tree overlaps outdir")
    return {"outdir": inventory(outdir), "wfcdir": inventory(wfcdir) if wfcdir else None}


def copy_checkpoint(outdir: Path, destination: Path, wfcdir: Optional[Path] = None,
                    *, immutable: bool = False) -> dict:
    if destination.exists() or destination.is_symlink():
        raise TrialError("checkpoint container exists")
    _plain_path(destination, exists=False)
    before = checkpoint_inventory(outdir, wfcdir)
    destination.mkdir(mode=0o700)
    try:
        copies = {"outdir": copy_tree(outdir, destination / "outdir", immutable=immutable),
                  "wfcdir": copy_tree(wfcdir, destination / "wfcdir", immutable=immutable) if wfcdir else None}
        after = checkpoint_inventory(outdir, wfcdir)
        if before != after:
            raise TrialError("source checkpoint changed while copying")
        write_json(destination / "inventory.json", {"before": before, "after": after, "copies": copies})
        if immutable:
            (destination / "inventory.json").chmod(0o444)
            destination.chmod(0o555)
        return {"outdir": str(destination / "outdir"),
                "wfcdir": str(destination / "wfcdir") if wfcdir else None,
                "source_inventory": before, "copies": copies, "immutable": immutable}
    except Exception:
        # Preserve incomplete copies for inspection; never delete evidence.
        raise


def parse_slurm_time(text: str) -> int:
    days = 0
    if "-" in text:
        day, text = text.split("-", 1)
        if not day.isdigit():
            raise TrialError("invalid Slurm time")
        days = int(day)
    parts = text.split(":")
    if len(parts) not in (2, 3) or not all(part.isdigit() for part in parts):
        raise TrialError("explicit Slurm HH:MM:SS or MM:SS time required")
    values = [int(part) for part in parts]
    hours, minutes, seconds = ([0] + values) if len(values) == 2 else values
    if minutes >= 60 or seconds >= 60:
        raise TrialError("invalid Slurm time fields")
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def _memory_gib(text: str) -> float:
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)([KMGT])", text)
    if not match:
        raise TrialError("unverified allocation memory unit")
    return float(match.group(1)) * {"K": 1 / (1024 ** 2), "M": 1 / 1024,
                                   "G": 1, "T": 1024}[match.group(2)]


def validate_allocation(raw: str, job_id: str, *, memory_gib: int = 200) -> dict:
    fields = dict(re.findall(r"(?:^|\s)([^\s=]+)=([^\s]+)", raw))
    expected = {"JobId": job_id, "Account": "che260157", "Partition": "wholenode",
                "JobState": "RUNNING", "NumNodes": "1", "NumCPUs": "128",
                "NumTasks": "128", "CPUs/Task": "1", "Requeue": "0",
                "Restarts": "0", "BatchFlag": "1", "Dependency": "(null)"}
    if any(fields.get(key) != value for key, value in expected.items()):
        raise TrialError("live Slurm job differs from the licensed singleton allocation")
    if any(key.startswith("Array") for key in fields) or "_" in job_id or not job_id.isdigit():
        raise TrialError("arrays and non-singleton job identifiers refused")
    limit = parse_slurm_time(fields.get("TimeLimit", ""))
    elapsed = parse_slurm_time(fields.get("RunTime", ""))
    if not 0 < limit <= CAPS["aggregate_seconds"] or elapsed >= limit:
        raise TrialError("live scheduler time exceeds or exhausts approved allowance")
    tres = dict(part.split("=", 1) for part in fields.get("AllocTRES", "").split(",") if "=" in part)
    if tres.get("cpu") != "128" or tres.get("billing") != "128" or tres.get("node") != "1":
        raise TrialError("live allocated/billing CPU or node TRES differs")
    if any(key.startswith("gres") for key in tres) or _memory_gib(tres.get("mem", "")) > memory_gib:
        raise TrialError("GPU TRES or memory exceeds approved allocation")
    if limit * 128 / 3600 > 2048:
        raise TrialError("allocation CPU SU ceiling exceeded")
    if not fields.get("NodeList") or fields.get("NodeList") in {"(null)", "None"}:
        raise TrialError("running allocation has no assigned node")
    return {"fields": fields, "allocated_tres": tres, "time_limit_seconds": limit,
            "runtime_seconds": elapsed, "remaining_seconds": limit - elapsed,
            "status": "COMPLIANT"}


def read_allocation(job_id: str) -> dict:
    argv = ["scontrol", "show", "job", job_id, "-o"]
    result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, timeout=15, check=False)
    receipt = {"argv": argv, "stdout": result.stdout, "stderr": result.stderr,
               "returncode": result.returncode, "observed_utc": utc_now()}
    if result.returncode:
        raise TrialError("scontrol failed; live allocation is unverified: " + json.dumps(receipt))
    return receipt


def thread_environment() -> dict:
    env = os.environ.copy()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[key] = "1"
    env["OMP_DYNAMIC"] = "FALSE"
    env["OMP_THREAD_LIMIT"] = "1"
    env["MKL_DYNAMIC"] = "FALSE"
    env["MAX_XML_STEPS"] = "0"
    return env


class StreamCapture:
    """Drain both pipes concurrently and flush every line to retained files."""
    def __init__(self, pipe, destination: Path):
        self.pipe, self.destination = pipe, destination
        self.text = ""
        self.error = None
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._read, daemon=True)

    def _read(self):
        try:
            with self.destination.open("w", encoding="utf-8", errors="replace", buffering=1) as out:
                for row in iter(self.pipe.readline, ""):
                    out.write(row)
                    out.flush()
                    with self.lock:
                        self.text += row
        except Exception as exc:
            self.error = str(exc)

    def get(self) -> str:
        with self.lock:
            return self.text


def teardown_process_group(proc, *, grace_seconds: float = 5,
                           deadline: Optional[float] = None, clock=time.monotonic) -> dict:
    """Signal only the new session owned by this invocation, including MPI ranks."""
    receipt = {"owned_process_group": proc.pid, "signals": []}
    def allowance(maximum):
        return maximum if deadline is None else min(maximum, max(0.0, deadline - clock()))
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
            receipt["signals"].append(signal.Signals(sig).name)
        except ProcessLookupError:
            break
        if sig == signal.SIGTERM:
            budget = allowance(grace_seconds)
            if budget > 0:
                try:
                    proc.wait(timeout=budget)
                except subprocess.TimeoutExpired:
                    pass
            # A dead mpirun leader does not prove its ranks left the group.
            try:
                os.killpg(proc.pid, 0)
            except ProcessLookupError:
                break
    budget = allowance(5)
    if budget > 0:
        try:
            proc.wait(timeout=budget)
        except subprocess.TimeoutExpired:
            receipt["unreaped_leader"] = True
    elif proc.poll() is None:
        receipt["unreaped_leader"] = True
    receipt["deadline_exhausted"] = deadline is not None and clock() >= deadline
    return receipt


def run_arm(*, name: str, argv: Sequence[str], cwd: Path, prefix: str,
            target_cycle: Optional[int], env: dict, clock=time.monotonic,
            sleep=time.sleep, popen=subprocess.Popen) -> dict:
    """Observe a registered SCF-cycle boundary; a missed boundary gets no retry."""
    start = clock()
    deadline = start + 7200
    receipt = {"arm": name, "argv": list(argv), "started_utc": utc_now(),
               "target_global_scf_cycle": target_cycle, "per_call_seconds": 7200,
               "qe_max_seconds": 7080, "stop_reason": None, "timed_out": False,
               "returncode": None, "production_accepted": False}
    write_json(cwd / "process_receipt.json", receipt)
    proc = None
    stdout = stderr = None
    teardown = None
    def allowance(maximum):
        return min(maximum, max(0.0, deadline - clock()))
    try:
        proc = popen(list(argv), cwd=str(cwd), env=env, stdin=subprocess.DEVNULL,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                     bufsize=1, close_fds=True, start_new_session=True)
        receipt["owned_process_group"] = proc.pid
        stdout, stderr = StreamCapture(proc.stdout, cwd / "stdout.log"), StreamCapture(proc.stderr, cwd / "stderr.log")
        stdout.thread.start()
        stderr.thread.start()
        requested_at = None
        while proc.poll() is None:
            elapsed = clock() - start
            combined = stdout.get() + "\n" + stderr.get()
            reason = None
            cycles = [int(match.group(1)) for match in SCF_CYCLE.finditer(stdout.get())]
            if FAILURE.search(combined):
                reason = "failure-marker"
            elif any(int(match.group(1)) >= 127 for match in SCF_ITERATION.finditer(combined)):
                reason = "HEA4-SCF-iteration-127"
            elif TIME_FAILURE.search(combined):
                reason = "solver-time-or-nstep-limit"
                receipt["timed_out"] = True
            elif elapsed >= 7080 and requested_at is None:
                reason = "wall-soft-stop"
                receipt["timed_out"] = True
            elif target_cycle is not None and any(cycle > target_cycle for cycle in cycles):
                reason = "missed-evaluated-boundary"
            elif target_cycle is not None and target_cycle in cycles:
                reason = "registered-evaluated-boundary"
            if reason and requested_at is None:
                requested_at = elapsed
                receipt["stop_reason"] = reason
                receipt["stop_observed_cycles"] = cycles
                receipt["stop_requested_elapsed_seconds"] = elapsed
                exit_path = cwd / (prefix + ".EXIT")
                # One path only: duplicate EXIT files survive the first poll.
                with exit_path.open("x", encoding="utf-8") as stream:
                    stream.write(reason + "; post-stop XML determines boundary validity\n")
                receipt["exit_path"] = str(exit_path)
                write_json(cwd / "process_receipt.json", receipt)
            failed_stop = requested_at is not None and receipt["stop_reason"] != "registered-evaluated-boundary"
            if elapsed >= 7150 or (failed_stop and elapsed - requested_at >= 60):
                receipt["timed_out"] = receipt["timed_out"] or elapsed >= 7150
                teardown = teardown_process_group(proc, deadline=deadline, clock=clock)
                break
            if stdout.error or stderr.error:
                raise TrialError("output capture failed")
            sleep(0.005)
        if proc.poll() is None:
            budget = allowance(5)
            if budget <= 0:
                raise TrialError("literal process deadline exhausted before reaping mpirun")
            proc.wait(timeout=budget)
    except BaseException as exc:
        receipt["supervisor_error"] = str(exc)
        if proc is not None and teardown is None:
            teardown = teardown_process_group(proc, deadline=deadline, clock=clock)
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
    finally:
        for capture in (stdout, stderr):
            if capture is not None:
                capture.thread.join(timeout=allowance(2))
                if capture.thread.is_alive() and proc is not None:
                    if teardown is None:
                        teardown = teardown_process_group(proc, deadline=deadline, clock=clock)
                    capture.thread.join(timeout=allowance(1))
                    receipt["supervisor_error"] = "output stream remained open after mpirun exit"
                if capture.error:
                    receipt["capture_error"] = capture.error
        receipt["teardown"] = teardown
        receipt["returncode"] = proc.returncode if proc is not None else None
        final_text = (stdout.get() if stdout else "") + "\n" + (stderr.get() if stderr else "")
        receipt["failure_marker_observed"] = bool(FAILURE.search(final_text))
        receipt["HEA4_stall_observed"] = any(int(match.group(1)) >= 127 for match in SCF_ITERATION.finditer(final_text))
        receipt["solver_limit_observed"] = bool(TIME_FAILURE.search(final_text))
        receipt["elapsed_seconds"] = clock() - start
        receipt["literal_deadline_seconds"] = 7200
        receipt["within_per_call_cap"] = receipt["elapsed_seconds"] <= 7200
        receipt["finished_utc"] = utc_now()
        for key in ("stdout", "stderr"):
            path = cwd / (key + ".log")
            if path.exists():
                receipt[key + "_sha256"] = sha256_file(path)
        write_json(cwd / "process_receipt.json", receipt)
    return receipt


def preflight(spec: dict, adapter) -> dict:
    validate_spec(spec)
    parent = _plain_path(Path(spec["trial_parent"]))
    root = _plain_path(Path(spec["trial_root"]), exists=False)
    if not parent.is_dir() or root.exists():
        raise TrialError("trial parent absent or new output already exists")
    if hasattr(os, "getuid") and parent.stat().st_uid != os.getuid():
        raise TrialError("trial parent is not owned by the invoking user")
    pins = {}
    for key in ("source_deck", "pw_x", "mpirun", "source_review"):
        pins[key] = verify_pin(spec[key], key, allow_external_hardlinks=key in {"pw_x", "mpirun"})
    for key in ("pw_x", "mpirun"):
        if not os.access(spec[key]["path"], os.X_OK):
            raise TrialError(key + " is not executable")
    pins["dependencies"] = [verify_pin(pin, "dependency") for pin in spec["dependencies"]]
    source_path = Path(__file__).absolute()
    if not any(Path(pin["path"]).absolute() == source_path for pin in spec["dependencies"]):
        raise TrialError("executing supervisor is not one of the dependency pins")
    adapter_path = Path(adapter.__file__).absolute()
    if not any(Path(pin["path"]).absolute() == adapter_path for pin in spec["dependencies"]):
        raise TrialError("executing adapter is not one of the dependency pins")
    contract_path = Path(adapter.contract.__file__).absolute()
    if not any(Path(pin["path"]).absolute() == contract_path for pin in spec["dependencies"]):
        raise TrialError("imported contract is not one of the dependency pins")
    pins["upfs"] = [verify_pin(pin, "UPF") for pin in spec["upfs"]]
    if len({Path(pin["path"]).name for pin in spec["upfs"]}) != 5:
        raise TrialError("UPF basenames alias one another")
    deck = Path(spec["source_deck"]["path"]).read_text(encoding="utf-8")
    deck_evidence = adapter.parse_deck(spec["source_deck"]["path"], spec["source_deck"]["sha256"])
    system = deck_evidence["settings"]["namelists"]["system"]
    if (deck_evidence["nat"] != 72 or deck_evidence["ntyp"] != 5
            or system.get("nspin") != 2 or system.get("ecutwfc") != 80
            or system.get("ecutrho") != 640 or deck_evidence["conv_thr_Ry"] != 1e-6
            or deck_evidence["settings"].get("hubbard", {}).get("unit") != "atomic"):
        raise TrialError("registered 72-atom spin-PBE80/640 atomic-U deck differs")
    deck_upfs = set(re.findall(r"\b[A-Za-z0-9_.+-]+\.(?:UPF|upf)\b", deck))
    if deck_upfs != {Path(pin["path"]).name for pin in spec["upfs"]}:
        raise TrialError("deck UPFs do not exactly match the five dependency pins")
    seed_root = _plain_path(Path(spec["initial_seed"]["root"]))
    pins["initial_seed"] = []
    for pin in spec["initial_seed"]["files"]:
        path = seed_root / pin["path"]
        checked = verify_pin({"path": str(path), "sha256": pin["sha256"]}, "initial seed")
        if checked["size_bytes"] != pin["size_bytes"]:
            raise TrialError("initial seed size differs")
        pins["initial_seed"].append(checked)
    for pin in [spec["source_deck"], spec["pw_x"], spec["mpirun"], spec["source_review"]] + spec["upfs"] + spec["dependencies"]:
        if _overlap(Path(pin["path"]).absolute(), root):
            raise TrialError("output aliases a pinned input")
    if _overlap(seed_root, root):
        raise TrialError("output aliases historical initialization")
    return {"status": "PREFLIGHT_PASS", "pins": pins, "deck": deck_evidence,
            "initialization_is_full_continuity_checkpoint": False}


def validate_reseed_binding(warm: dict, fresh: dict, reseed: dict, *, adapter) -> dict:
    """Bind a new optimizer's first evaluation to the observed lower fresh state.

    Successful density copying and a clean SCF alone do not establish which
    metastable electronic state the reseed actually reached. Retain both raw
    energy comparisons and their deciding XML sources, including on refusal.
    """
    result = {"passed": False, "production_accepted": False,
              "energy_tolerance_Ry": 1e-6, "strict_drop_meV_per_cell": 10.0,
              "raw_source_binding_validated": False, "same_evaluated_geometry": False,
              "same_raw_settings": False}
    try:
        records = []
        for label, arm in (("warm", warm), ("fresh", fresh), ("reseed", reseed)):
            adapter._validate_arm(arm)
            frames = arm["evaluations"]
            if len(frames) != 1:
                raise TrialError(label + " must have exactly one first evaluated state")
            frame = frames[0]
            if (frame.get("status") != "CONVERGED" or frame.get("geometry_role") != "evaluated"
                    or frame.get("energy_unit") != "Ry" or frame.get("geometry_unit") != "bohr"):
                raise TrialError(label + " lacks a converged source-bound evaluated state")
            energy = frame.get("energy_Ry")
            if type(energy) not in (int, float) or not math.isfinite(energy):
                raise TrialError(label + " first evaluated energy is nonfinite or invalid")
            source = _pin(frame.get("source"), label + " evaluated XML")
            xml_source = arm["sources"]["xml"]
            if source["path"] != xml_source["path"] or source["sha256"] != xml_source["sha256"]:
                raise TrialError(label + " evaluated energy is not bound to its actual raw XML")
            first, last = source.get("line_start"), source.get("line_end")
            if type(first) is not int or type(last) is not int or first < 1 or last < first:
                raise TrialError(label + " evaluated XML source range is invalid")
            verify_pin(source, label + " first evaluated XML")
            records.append(frame)
            result[label + "_first_energy_Ry"] = energy
            result[label + "_first_evaluation_source"] = source
        result["raw_source_binding_validated"] = True
        if (len({arm["settings_identity"] for arm in (warm, fresh, reseed)}) != 1
                or len({arm["xml_settings_identity"] for arm in (warm, fresh, reseed)}) != 1
                or any(frame["settings_identity"] != warm["settings_identity"] for frame in records)):
            raise TrialError("reseed first evaluation has different raw physical/solver settings")
        result["same_raw_settings"] = True
        if any(not adapter._geometry_matches(records[0]["geometry"], frame["geometry"])
               for frame in records[1:]):
            raise TrialError("reseed first evaluation is not at the same evaluated geometry")
        result["same_evaluated_geometry"] = True
        warm_energy, fresh_energy, reseed_energy = [frame["energy_Ry"] for frame in records]
        difference = abs(reseed_energy - fresh_energy)
        conversion = adapter.contract.RY_MEV
        result["reseed_minus_fresh_abs_Ry"] = difference
        result["warm_minus_reseed_meV"] = (warm_energy - reseed_energy) * conversion
        result["matches_fresh_energy"] = difference <= 1e-6
        result["still_strictly_lower_than_warm"] = reseed_energy < warm_energy - 10.0 / conversion
        if not result["matches_fresh_energy"]:
            raise TrialError("reseed first energy does not match the lower fresh reference within1e-6 Ry")
        if not result["still_strictly_lower_than_warm"]:
            raise TrialError("reseed first state is not still strictly more than10meV below the original warm state")
        result["passed"] = True
        result["reason"] = "first reseed evaluation is bound to the observed lower fresh state"
    except (TrialError, ValueError, OSError, KeyError, TypeError) as exc:
        result["reason"] = str(exc)
    return result


class Trial:
    """A sequential state machine; fresh-check branch is decided before resume."""
    def __init__(self, spec: dict, *, adapter=None, allocation_reader=read_allocation,
                 runner=run_arm, clock=time.monotonic):
        if adapter is None:
            try:
                from . import pa_qe_adapter as adapter
            except ImportError:
                import pa_qe_adapter as adapter
        self.spec = validate_spec(spec)
        self.adapter, self.allocation_reader, self.runner, self.clock = adapter, allocation_reader, runner, clock
        self.root = Path(spec["trial_root"])
        self.source_text = Path(spec["source_deck"]["path"]).read_text(encoding="utf-8")
        self.expected_settings = adapter.parse_deck(spec["source_deck"]["path"], spec["source_deck"]["sha256"])
        self.expected_settings["upf_pins"] = {Path(pin["path"]).name: pin["sha256"] for pin in spec["upfs"]}
        self.start = clock()
        self.calls = 0
        self.active = False
        self.receipt = {"date": spec["date"], "target": TARGET, "production_accepted": False,
                        "every_step_pa_validated": False, "terminal_fresh_acceptance_validated": False,
                        "genuine_lower_state_reseed_validated": False,
                        "scheduler_status": "UNVERIFIED", "scientific_status": "INCONCLUSIVE",
                        "calls": [], "started_utc": utc_now()}

    def save(self):
        self.receipt["call_count"] = self.calls
        self.receipt["elapsed_seconds"] = self.clock() - self.start
        write_json(self.root / "trial_receipt.json", self.receipt)

    def budget(self, allocation: dict):
        remaining = min(CAPS["aggregate_seconds"] - (self.clock() - self.start),
                        allocation["remaining_seconds"])
        if self.calls >= 6 or remaining < 7200 + 120:
            raise TrialError("full registered 7200-second call plus cleanup does not fit; no shrink-to-fit")
        if self.active:
            raise TrialError("parallel QE invocation refused")

    def allocation(self) -> dict:
        job_id = os.environ.get("SLURM_JOB_ID", "")
        if not job_id.isdigit() or os.environ.get("SLURM_ARRAY_JOB_ID"):
            raise TrialError("must run in the licensed live singleton Slurm allocation")
        raw = self.allocation_reader(job_id)
        # Retain the raw receipt before validating it.
        write_json(self.root / ("allocation_before_call_%02d.json" % (self.calls + 1)), raw)
        try:
            verified = validate_allocation(raw["stdout"], job_id,
                                           memory_gib=self.spec["allocation"]["memory_gib"])
        except Exception:
            self.receipt["scheduler_status"] = "REFUSED"
            raise
        self.receipt["scheduler_status"] = "COMPLIANT"
        return verified

    def verify_sources(self):
        for key in ("source_deck", "pw_x", "mpirun", "source_review"):
            verify_pin(self.spec[key], key, allow_external_hardlinks=key in {"pw_x", "mpirun"})
        for pin in self.spec["dependencies"] + self.spec["upfs"]:
            verify_pin(pin, "dependency")
        for pin in self.spec["upfs"]:
            verify_pin({"path": str(self.root / "common_pseudo" / Path(pin["path"]).name),
                        "sha256": pin["sha256"]}, "trial-local UPF")
        for pin in self.spec["initial_seed"]["files"]:
            verify_pin({"path": str(Path(SEED_ROOT) / pin["path"]), "sha256": pin["sha256"]}, "historical seed")

    def common_upfs(self):
        destination = self.root / "common_pseudo"
        destination.mkdir(mode=0o700)
        for pin in self.spec["upfs"]:
            verify_pin(pin, "UPF before copy")
            target = destination / Path(pin["path"]).name
            shutil.copy2(pin["path"], str(target))
            verify_pin({"path": str(target), "sha256": pin["sha256"]}, "common UPF copy")
            target.chmod(0o444)
        destination.chmod(0o555)

    def initialize_density(self, outdir: Path):
        """Intentional density initialization, never a full optimizer restart."""
        saved = outdir / (PREFIX + ".save")
        saved.mkdir(parents=True, mode=0o700)
        rows = []
        for pin in self.spec["initial_seed"]["files"]:
            source = Path(SEED_ROOT) / pin["path"]
            before = verify_pin({"path": str(source), "sha256": pin["sha256"]}, "initial seed")
            target = saved / pin["path"]
            shutil.copy2(str(source), str(target))
            copied = verify_pin({"path": str(target), "sha256": pin["sha256"]}, "initial seed copy")
            after = verify_pin({"path": str(source), "sha256": pin["sha256"]}, "initial seed after copy")
            if before != after:
                raise TrialError("historical initialization changed during copy")
            rows.append({"source_before": before, "copy": copied, "source_after": after})
        return {"files": rows, "mode": "INTENTIONAL_DENSITY_INITIALIZATION",
                "full_continuity_checkpoint": False, "optimizer_history_inherited": False}

    def execute(self, name: str, *, kind: str, target_cycle: Optional[int],
                expected_cycles: Sequence[int], expected_steps: int,
                geometry=None, checkpoint=None, seed_fresh=None) -> dict:
        allocation = self.allocation()
        self.budget(allocation)
        self.verify_sources()
        arm = self.root / name
        arm.mkdir(mode=0o700)
        outdir = arm / "outdir"
        wfcdir = None
        setup = {}
        if checkpoint is not None:
            source_out = Path(checkpoint["outdir"])
            source_wfc = Path(checkpoint["wfcdir"]) if checkpoint.get("wfcdir") else None
            copied = copy_checkpoint(source_out, arm / "checkpoint_copy", source_wfc)
            outdir = Path(copied["outdir"])
            wfcdir = Path(copied["wfcdir"]) if copied["wfcdir"] else None
            setup["copied_full_checkpoint"] = copied
        elif seed_fresh is not None:
            # Only the clean fresh electronic files seed a brand-new optimizer.
            outdir.mkdir(mode=0o700)
            source_save = Path(seed_fresh["outdir"]) / (PREFIX + ".save")
            before = inventory(source_save)
            destination_save = outdir / (PREFIX + ".save")
            destination_save.mkdir(mode=0o700)
            selected = []
            for filename in SEED_FILES:
                source = source_save / filename
                if not source.exists():
                    raise TrialError("fresh density seed lacks " + filename)
                source = _regular(source)
                target = destination_save / filename
                digest = sha256_file(source)
                shutil.copy2(str(source), str(target))
                if sha256_file(target) != digest:
                    raise TrialError("fresh density copy differs")
                selected.append({"path": filename, "sha256": digest})
            if inventory(source_save) != before:
                raise TrialError("fresh seed source changed")
            setup["intentional_history_reset"] = True
            setup["density_seed_files"] = selected
        elif kind in {"control", "candidate"}:
            setup["initialization"] = self.initialize_density(outdir)
        else:
            outdir.mkdir(mode=0o700)
        deck = self.adapter.render_trial_deck(self.source_text, arm_kind=kind, prefix=PREFIX,
            outdir=outdir, pseudo_dir=self.root / "common_pseudo", wfcdir=wfcdir,
            geometry=geometry, max_seconds=7080, nstep=30)
        deck_path = arm / "input.in"
        deck_path.write_text(deck, encoding="utf-8")
        input_pin = sha256_file(deck_path)
        parsed_input = self.adapter.parse_deck(deck_path, input_pin)
        if parsed_input["settings_identity"] != self.expected_settings["settings_identity"]:
            raise TrialError("runtime physical or solver controls changed")
        operations = parsed_input["operations"]
        if (operations["outdir"] != str(outdir).replace("\\", "/")
                or operations["pseudo_dir"] != str(self.root / "common_pseudo").replace("\\", "/")
                or operations["prefix"] != PREFIX or operations["max_seconds"] != 7080
                or operations["nstep"] < 30 or operations["restart_mode"] != ("restart" if kind == "resumed" else "from_scratch")
                or operations["startingwfc"] != ("file" if kind == "resumed" else "atomic+random")
                or operations["startingpot"] != ("atomic" if kind == "fresh" else "file")):
            raise TrialError("runtime operational deck differs from the registered arm")
        upf_reads = self.adapter.validate_upfs(parsed_input, self.root / "common_pseudo",
                                              self.expected_settings["upf_pins"])
        write_json(arm / "setup_receipt.json", dict(setup, input_sha256=sha256_file(deck_path),
            common_pseudo_dir=str(self.root / "common_pseudo"), kind=kind,
            expected_cycles=list(expected_cycles), expected_xml_steps=expected_steps,
            upf_reads=upf_reads, environment={key: thread_environment()[key] for key in
                ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "BLIS_NUM_THREADS", "OMP_DYNAMIC", "MAX_XML_STEPS")}))
        argv = [self.spec["mpirun"]["path"], "-np", "128", self.spec["pw_x"]["path"],
                "-nk", "8", "-ndiag", "16", "-in", str(deck_path)]
        # Recheck live time immediately before pw.x, including copy/hash overhead.
        allocation = self.allocation()
        self.budget(allocation)
        self.verify_sources()
        if sha256_file(deck_path) != input_pin:
            raise TrialError("arm input changed between validation and launch")
        self.calls += 1
        self.active = True
        call = {"name": name, "kind": kind, "status": "STARTED", "setup": setup}
        self.receipt["calls"].append(call)
        self.save()
        try:
            process = self.runner(name=name, argv=argv, cwd=arm, prefix=PREFIX,
                                  target_cycle=target_cycle, env=thread_environment())
            call["process"] = process
            if (process.get("timed_out") or process.get("within_per_call_cap") is not True
                    or process.get("supervisor_error") or process.get("capture_error")
                    or process.get("failure_marker_observed") or process.get("HEA4_stall_observed")
                    or process.get("solver_limit_observed")):
                raise TrialError(name + " did not complete within the registered process contract")
            if target_cycle is not None and process.get("stop_reason") != "registered-evaluated-boundary":
                raise TrialError(name + " lacks the registered boundary stop receipt")
            if any(path.exists() or path.is_symlink() for path in
                   (arm / (PREFIX + ".EXIT"), outdir / (PREFIX + ".EXIT"))):
                raise TrialError("stale EXIT file after shutdown; checkpoint cannot be copied")
            parsed = self.adapter.read_qe_arm(deck_path, arm / "stdout.log", arm / "stderr.log",
                outdir / (PREFIX + ".save") / "data-file-schema.xml", process,
                expected_settings=self.expected_settings, expected_parallel=SHAPE,
                expected_exit="normal_scf" if kind == "fresh" else "clean_stop",
                expected_evaluations=1 if kind == "fresh" else expected_steps)
            if parsed["scf_counts"] != list(expected_cycles):
                raise TrialError("ordered global SCF counters miss the registered boundary")
            if kind in {"control", "candidate", "fresh", "reseed", "negative"}:
                self.adapter.require_expected_first_threshold(parsed, self.expected_settings)
            if kind == "control":
                self.expected_settings["xml_settings_identity"] = parsed["xml_settings_identity"]
            if kind == "negative":
                text = (arm / "stdout.log").read_text(encoding="utf-8", errors="replace")
                first = re.search(r"(?m)^[ \t]*number of bfgs steps[ \t]*=[ \t]*(\d+)[ \t]*$", text)
                if (first is None or int(first.group(1)) != 0
                        or ".bfgs deleted, as requested" not in text[:first.start()]):
                    raise TrialError("negative control lacks actual startup deletion and optimizer count0")
            if kind == "reseed" and (not parsed["optimizer_counts"] or parsed["optimizer_counts"][0] != 0):
                raise TrialError("intentional reseed did not start a new optimizer")
            call["parsed"] = parsed
            call["status"] = "NUMERICAL_RECEIPT_VALIDATED"
            write_json(arm / "parsed_receipt.json", parsed)
            self.verify_sources()
            return {"raw": parsed, "outdir": str(outdir), "wfcdir": str(wfcdir) if wfcdir else None,
                    "input_path": str(deck_path), "bfgs_path": str(outdir / (PREFIX + ".bfgs"))}
        except BaseException as exc:
            call["status"] = "INCONCLUSIVE"
            call["error"] = str(exc)
            raise
        finally:
            self.active = False
            self.save()

    def run(self) -> dict:
        checked = preflight(self.spec, self.adapter)
        self.root.mkdir(mode=0o700)
        self.receipt["preflight"] = checked
        self.save()
        try:
            self.common_upfs()
            control = self.execute("control", kind="control", target_cycle=3,
                                   expected_cycles=[1, 2, 3], expected_steps=3)
            candidate = self.execute("candidate", kind="candidate", target_cycle=1,
                                     expected_cycles=[1], expected_steps=1)
            candidate_raw = candidate["raw"]
            evaluated = candidate_raw["evaluations"][0]
            proposal = candidate_raw["proposal_geometry"]
            if (proposal is None or max(abs(a-b) for row, prior in zip(proposal["positions"], evaluated["geometry"]["positions"])
                for a, b in zip(row, prior)) <= 1e-8):
                raise TrialError("candidate checkpoint lacks a nonzero saved proposal")
            stopped = copy_checkpoint(Path(candidate["outdir"]), self.root / "candidate_immutable",
                Path(candidate["wfcdir"]) if candidate.get("wfcdir") else None, immutable=True)
            self.receipt["candidate_checkpoint"] = stopped
            saved_optimizer = self.adapter.read_bfgs(Path(stopped["outdir"]) / (PREFIX + ".bfgs"),
                nat=72, cell_bohr=evaluated["geometry"]["cell"], evaluated=evaluated)
            if saved_optimizer["scf_count"] != 1 or saved_optimizer["bfgs_count"] != 1:
                raise TrialError("first candidate saved optimizer counters differ")
            self.receipt["saved_optimizer"] = saved_optimizer
            before_full = checkpoint_inventory(Path(stopped["outdir"]),
                Path(stopped["wfcdir"]) if stopped.get("wfcdir") else None)
            before = self.adapter.checkpoint_inventory(stopped["outdir"], stopped.get("wfcdir"))
            fresh = None
            try:
                fresh = self.execute("fresh", kind="fresh", target_cycle=None,
                    expected_cycles=[], expected_steps=0, geometry=evaluated["geometry"])
            except (TrialError, ValueError, OSError) as exc:
                self.receipt["fresh_failure"] = str(exc)
            after_full = checkpoint_inventory(Path(stopped["outdir"]),
                Path(stopped["wfcdir"]) if stopped.get("wfcdir") else None)
            after = self.adapter.checkpoint_inventory(stopped["outdir"], stopped.get("wfcdir"))
            self.receipt["immutable_checkpoint_before_fresh"] = before
            self.receipt["immutable_checkpoint_after_fresh"] = after
            if before != after or before_full != after_full:
                raise TrialError("immutable restart checkpoint changed during isolated fresh SCF")
            scratch_paths = {"restart_outdir": stopped["outdir"], "restart_wfcdir": stopped.get("wfcdir"),
                "fresh_outdir": fresh["outdir"] if fresh else str(self.root / "fresh" / "outdir"),
                "fresh_wfcdir": fresh.get("wfcdir") if fresh else None}
            decision = self.adapter.pre_resume_decision(candidate_raw, fresh["raw"] if fresh else None,
                before, after, scratch_paths=scratch_paths)
            self.receipt["pre_resume_decision"] = decision
            write_json(self.root / "pre_resume_decision.json", decision)
            self.save()
            action = decision["action"]
            if action == "HOLD":
                self.receipt["scientific_status"] = "HOLD"
            elif action == "RESEED_CANDIDATE":
                self.receipt["reseed_branch_attempted"] = True
                self.receipt["reseed_branch_status"] = "RESEED_ATTEMPT"
                self.receipt["continuity_validated"] = False
                self.receipt["intentional_history_reset"] = True
                self.receipt["genuine_lower_state_reseed_validated"] = False
                self.save()
                reseed = self.execute("reseed", kind="reseed", target_cycle=1,
                    expected_cycles=[1], expected_steps=1,
                    geometry=evaluated["geometry"], seed_fresh=fresh)
                self.receipt["reseed"] = reseed
                binding = validate_reseed_binding(candidate_raw, fresh["raw"], reseed["raw"], adapter=self.adapter)
                self.receipt["reseed_lower_state_binding"] = binding
                write_json(self.root / "reseed_lower_state_binding.json", binding)
                if binding["passed"] is not True:
                    raise TrialError(binding["reason"])
                self.receipt["scientific_status"] = "RESEED_BRANCH_ONLY"
                self.receipt["reseed_branch_status"] = "LOWER_FRESH_STATE_BOUND"
                self.receipt["genuine_lower_state_reseed_validated"] = True
            elif action == "RESUME_CANDIDATE":
                resumed = self.execute("resumed", kind="resumed", target_cycle=3,
                    expected_cycles=[2, 3], expected_steps=2, checkpoint=stopped, geometry=proposal)
                self.receipt["consumption_audit"] = self.adapter.audit_consumption(candidate_raw, fresh["raw"],
                    saved_optimizer, resumed["raw"], before, after, scratch_paths=scratch_paths)
                if self.receipt["consumption_audit"].get("raw_consumption_audit", {}).get("passed") is not True:
                    raise TrialError("actual resumed checkpoint consumption failed")
                self.receipt["continuity"] = self.adapter.compare_trajectories(control["raw"]["evaluations"],
                    candidate_raw["evaluations"] + resumed["raw"]["evaluations"])
                if self.receipt["continuity"].get("within_tolerances") is not True:
                    raise TrialError("all three ordered evaluations did not agree")
                if self.spec["optional_negative_control"]:
                    negative = self.execute("negative", kind="negative", target_cycle=3,
                        expected_cycles=[1, 2, 3], expected_steps=3,
                        geometry=proposal, checkpoint=stopped)
                    self.receipt["negative_control"] = negative
                self.receipt["scientific_status"] = "PASS_ONE_BOUNDARY"
                self.receipt["continuity_validated"] = True
                self.receipt["genuine_lower_state_reseed_validated"] = False
            else:
                raise TrialError("adapter returned an unregistered branch")
            final = checkpoint_inventory(Path(stopped["outdir"]),
                Path(stopped["wfcdir"]) if stopped.get("wfcdir") else None)
            if final != before_full:
                raise TrialError("immutable checkpoint changed during subsequent arms")
            self.verify_sources()
            if self.clock() - self.start >= 57600:
                raise TrialError("aggregate elapsed time reached 16h")
        except BaseException as exc:
            self.receipt["scientific_status"] = "INCONCLUSIVE"
            self.receipt["error"] = str(exc)
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
        finally:
            self.receipt["finished_utc"] = utc_now()
            self.save()
        return self.receipt


def load_spec(path: Path, expected_sha256: str) -> dict:
    if not SHA256.fullmatch(expected_sha256 or ""):
        raise TrialError("exact dated spec SHA-256 is required")
    verify_pin({"path": str(path), "sha256": expected_sha256}, "dated JSON spec")
    return validate_spec(json.loads(path.read_text(encoding="utf-8")))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args(argv)
    def interrupted(signum, frame):
        raise KeyboardInterrupt("supervisor received " + signal.Signals(signum).name)
    # Ensure externally requested termination unwinds the process-group owner.
    for signum in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, interrupted)
    try:
        spec = load_spec(args.spec, args.spec_sha256)
        trial = Trial(spec)
        if args.preflight:
            print(json.dumps(preflight(spec, trial.adapter), sort_keys=True))
            return 0
        result = trial.run()
        print(json.dumps({"scientific_status": result["scientific_status"],
                          "scheduler_status": result["scheduler_status"],
                          "production_accepted": False, "call_count": result["call_count"]}))
        return 0 if result["scientific_status"] == "PASS_ONE_BOUNDARY" else 3
    except (TrialError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"scientific_status": "INCONCLUSIVE", "scheduler_status": "UNVERIFIED",
                          "production_accepted": False, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
