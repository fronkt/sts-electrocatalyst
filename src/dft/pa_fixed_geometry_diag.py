"""Fixed-geometry electronic initialization / force-convergence diagnostic (one group per job).

Licensed 2026-10-05 (docs/research/pa-fixed-geometry-diagnostic-2026-10-05.md).
Three independent singleton jobs, one per group, each running its calls in order:

  replay  A_replay  resumed deck replayed from the frozen candidate checkpoint, stopped
                    after global evaluation 2 (determinism of the restart path)
          B_ethr    the same plus diago_thr_init = 1.0d-6, stopped after evaluation 3
                    (does matching the startup threshold restore continuity?)
  ladder  C1 -> C2 -> C3   SCF-only at G2 from the checkpoint; conv_thr 1e-6, 1e-8, 1e-10,
                    each rung started from a verified copy of the previous rung's outdir
  fresh   D1 -> D2  SCF-only at G2 from the atomic start; conv_thr 1e-8, then 1e-10
  probe   P1, P2    (licensed 2026-10-07, docs/research/pa-repro-probe-2026-10-07.md)
                    two byte-identical repeats of C3, each from its own verified copy
                    of the pinned C2 outdir (the spec's "checkpoint" for this group)

Every QE call reuses run_arm, StreamCapture and the allocation validator of the
launched pa_catalyst_retest.py (staged byte-identical, hash-pinned): same MPI shape,
literal 7200-second per-call ceiling, EXIT-file boundary stop, no retry or requeue.
A failed call skips only the calls that start from its outdir. This controller makes
no scientific comparison; the offline readout does.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import stat
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pa_catalyst_retest as base  # noqa: E402  (pinned helper module, never modified)

SCHEMA = "pa-fixed-geometry-diag-v1"
PREFIX = "slab_c5low__pa_boundary"
GROUPS = {
    "replay": [("A_replay", "checkpoint", 2), ("B_ethr", "checkpoint", 3)],
    "ladder": [("C1_warm_1e-6", "checkpoint", None), ("C2_warm_1e-8", "C1_warm_1e-6", None),
               ("C3_warm_1e-10", "C2_warm_1e-8", None)],
    "fresh": [("D1_fresh_1e-8", None, None), ("D2_fresh_1e-10", "D1_fresh_1e-8", None)],
    "probe": [("P1_C3_repeat", "checkpoint", None), ("P2_C3_repeat", "checkpoint", None)],
}
CALL_SECONDS = 7200
CLEANUP_SECONDS = 120
SHAPE = ["-np", "128"]
PW_FLAGS = ["-nk", "8", "-ndiag", "16"]


class DiagError(RuntimeError):
    pass


def validate_spec(spec: dict, group: str) -> dict:
    if spec.get("schema") != SCHEMA or group not in GROUPS:
        raise DiagError("unknown spec schema or group")
    rows = spec["groups"][group]
    if [row["name"] for row in rows["calls"]] != [name for name, _, _ in GROUPS[group]]:
        raise DiagError("spec call order differs from the registered group")
    for row, (name, start, cycle) in zip(rows["calls"], GROUPS[group]):
        if row.get("start") != start or row.get("target_cycle") != cycle:
            raise DiagError(f"{name}: start/boundary differs from registration")
        base._pin(row["deck"], name + " deck")
    limit = rows["time_limit_seconds"]
    if not 0 < limit <= 57600 or limit * 128 / 3600 > rows["max_cpu_su"]:
        raise DiagError("group time limit exceeds its registered CPU-SU ceiling")
    for key in ("pw_x", "mpirun", "helper", "controller", "slurm"):
        base._pin(spec[key], key)
    for pin in spec["upfs"]:
        base._pin(pin, "UPF")
    if not base.SHA256.match(spec["checkpoint"]["tree_sha256"]):
        raise DiagError("checkpoint tree digest malformed")
    return spec


def copy_verified(source: Path, source_inventory: dict, destination: Path) -> dict:
    """Copy a plain tree, hashing source bytes while copying, then re-hash the copy."""
    if destination.exists() or destination.is_symlink():
        raise DiagError("copy destination exists")
    expected = {row["path"]: row for row in source_inventory["files"]}
    destination.mkdir(mode=0o700)
    for relative in source_inventory["directories"]:
        (destination / relative).mkdir(mode=0o700)
    for relative, row in sorted(expected.items()):
        src = source / relative
        before = src.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise DiagError("source entry is not a plain file: " + relative)
        digest = hashlib.sha256()
        fd = os.open(str(src), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "rb") as inp, (destination / relative).open("xb") as out:
            while True:
                chunk = inp.read(8 * 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                out.write(chunk)
        if digest.hexdigest() != row["sha256"] or src.lstat().st_size != row["size_bytes"]:
            raise DiagError("source bytes changed during copy: " + relative)
    copied = base.inventory(destination)
    if copied["sha256"] != source_inventory["sha256"]:
        raise DiagError("copied tree digest differs from source inventory")
    return {"source_root": str(source), "destination_root": str(destination),
            "tree_sha256": copied["sha256"], "files": len(copied["files"]),
            "bytes": sum(row["size_bytes"] for row in copied["files"])}


def live_pw_processes() -> list:
    """PIDs of this user's live pw.x processes (Linux /proc); empty where /proc is absent."""
    proc = Path("/proc")
    if not proc.is_dir():
        return []
    uid, found = os.getuid(), []
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if entry.stat().st_uid != uid:
                continue
            parts = (entry / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        if any(part == b"pw.x" or part.endswith(b"/pw.x") for part in parts):
            found.append(int(entry.name))
    return found


def call_succeeded(receipt: dict, cwd: Path, target_cycle: Optional[int]) -> tuple:
    stdout = (cwd / "stdout.log").read_text(encoding="utf-8", errors="replace") if (cwd / "stdout.log").exists() else ""
    problems = []
    if receipt.get("returncode") != 0:
        problems.append("nonzero return code")
    if receipt.get("supervisor_error") or receipt.get("capture_error"):
        problems.append("supervisor or capture error")
    if receipt.get("timed_out") or receipt.get("failure_marker_observed") or receipt.get("HEA4_stall_observed"):
        problems.append("timeout, failure marker or HEA4 stall")
    if receipt.get("solver_limit_observed") or receipt.get("within_per_call_cap") is False:
        problems.append("solver time/step limit or per-call cap exceeded")
    if target_cycle is None:
        if receipt.get("stop_reason") is not None:
            problems.append("SCF-only call was stopped: " + str(receipt.get("stop_reason")))
        if "End of self-consistent calculation" not in stdout or "Forces acting on atoms" not in stdout:
            problems.append("no completed SCF with forces")
        if "JOB DONE." not in stdout:
            problems.append("pw.x did not reach JOB DONE")
    elif receipt.get("stop_reason") != "registered-evaluated-boundary":
        problems.append("registered evaluation boundary not reached")
    return (not problems), problems


class Group:
    def __init__(self, spec: dict, group: str, *, runner=base.run_arm,
                 allocation_reader=base.read_allocation, clock=time.monotonic,
                 process_probe=live_pw_processes):
        self.spec, self.group = validate_spec(spec, group), group
        self.runner, self.allocation_reader, self.clock = runner, allocation_reader, clock
        self.process_probe = process_probe
        self.base = Path(spec["base"])
        self.root = self.base / "groups" / group
        self.start = clock()
        self.receipt = {"schema": SCHEMA, "group": group, "started_utc": base.utc_now(),
                        "calls": [], "production_accepted": False,
                        "scheduler_status": "UNVERIFIED", "new_jobs_submitted_by_controller": 0}

    def save(self):
        self.receipt["elapsed_seconds"] = self.clock() - self.start
        base.write_json(self.root / "group_receipt.json", self.receipt)

    def allocation(self, index: int, stage: str) -> dict:
        job_id = os.environ.get("SLURM_JOB_ID", "")
        if not job_id.isdigit() or os.environ.get("SLURM_ARRAY_JOB_ID"):
            raise DiagError("must run inside the live singleton Slurm allocation")
        raw = self.allocation_reader(job_id)
        base.write_json(self.root / ("allocation_%02d_%s.json" % (index, stage)), raw)
        try:
            verified = base.validate_allocation(raw["stdout"], job_id, memory_gib=200)
        except Exception:
            self.receipt["scheduler_status"] = "REFUSED"
            raise
        limit = self.spec["groups"][self.group]["time_limit_seconds"]
        if verified["time_limit_seconds"] > limit:
            self.receipt["scheduler_status"] = "REFUSED"
            raise DiagError("live TimeLimit exceeds this group's registered limit")
        self.receipt["scheduler_status"] = "COMPLIANT"
        return verified

    def verify_sources(self):
        if Path(__file__).resolve() != Path(self.spec["controller"]["path"]):
            raise DiagError("running controller is not the pinned controller path")
        if Path(base.__file__).resolve() != Path(self.spec["helper"]["path"]):
            raise DiagError("imported helper is not the pinned helper path")
        base.verify_pin(self.spec["controller"], "controller")
        base.verify_pin(self.spec["slurm"], "slurm script")
        base.verify_pin(self.spec["pw_x"], "pw.x", allow_external_hardlinks=True)
        base.verify_pin(self.spec["mpirun"], "mpirun", allow_external_hardlinks=True)
        base.verify_pin(self.spec["helper"], "helper")
        for pin in self.spec["upfs"]:
            base.verify_pin(pin, "UPF")
        for row in self.spec["groups"][self.group]["calls"]:
            base.verify_pin(row["deck"], row["name"] + " deck")

    def run(self) -> int:
        # Refuse before any write, so a refused group leaves no directory behind.
        self.verify_sources()
        self.root.mkdir(parents=True, exist_ok=False)
        try:
            return self._run()
        finally:
            self.save()

    def _run(self) -> int:
        self.receipt["sources_verified"] = True
        self.save()
        checkpoint_inventory = None
        rows = self.spec["groups"][self.group]["calls"]
        if any(row["start"] == "checkpoint" for row in rows):
            source = Path(self.spec["checkpoint"]["outdir"])
            checkpoint_inventory = base.inventory(source)
            if checkpoint_inventory["sha256"] != self.spec["checkpoint"]["tree_sha256"]:
                raise DiagError("pinned start tree (checkpoint) differs from its pinned tree digest")
            self.receipt["checkpoint_before"] = {"root": str(source), "sha256": checkpoint_inventory["sha256"],
                                                 "files": len(checkpoint_inventory["files"])}
            self.save()
        outcome = {}
        for index, row in enumerate(rows, 1):
            name, start, cycle = row["name"], row["start"], row["target_cycle"]
            cwd = self.base / "runs" / name
            record = {"name": name, "start": start, "target_cycle": cycle, "deck_sha256": row["deck"]["sha256"]}
            self.receipt["calls"].append(record)
            if start not in (None, "checkpoint") and outcome.get(start) is not True:
                record["status"] = "SKIPPED_PREDECESSOR_FAILED"
                outcome[name] = False
                self.save()
                continue
            try:
                allocation = self.allocation(index, "before_setup")
                record["remaining_before_setup_seconds"] = allocation["remaining_seconds"]
                if allocation["remaining_seconds"] < CALL_SECONDS + CLEANUP_SECONDS:
                    raise DiagError("full 7200-second call plus cleanup does not fit; no shrink-to-fit")
                cwd.mkdir(parents=True, exist_ok=False)
                if start == "checkpoint":
                    record["setup"] = copy_verified(Path(self.spec["checkpoint"]["outdir"]),
                                                    checkpoint_inventory, cwd / "outdir")
                elif start is not None:
                    previous = self.base / "runs" / start / "outdir"
                    record["setup"] = copy_verified(previous, base.inventory(previous), cwd / "outdir")
                else:
                    (cwd / "outdir").mkdir(mode=0o700)
                    record["setup"] = {"fresh_outdir": str(cwd / "outdir")}
                deck = Path(row["deck"]["path"])
                base.verify_pin(row["deck"], name + " deck")
                shutil.copyfile(str(deck), str(cwd / "input.in"))
                if base.sha256_file(cwd / "input.in") != row["deck"]["sha256"]:
                    raise DiagError("staged input differs from the pinned deck")
                base.write_json(cwd / "setup_receipt.json", record["setup"])
                allocation = self.allocation(index, "before_launch")
                record["remaining_before_launch_seconds"] = allocation["remaining_seconds"]
                if allocation["remaining_seconds"] < CALL_SECONDS + CLEANUP_SECONDS:
                    raise DiagError("full 7200-second call plus cleanup does not fit; no shrink-to-fit")
                survivors = self.process_probe()
                if survivors:
                    raise DiagError("live pw.x processes before launch: " + repr(survivors))
                self.save()
                argv = [self.spec["mpirun"]["path"], *SHAPE, self.spec["pw_x"]["path"], *PW_FLAGS,
                        "-in", str(cwd / "input.in")]
                receipt = self.runner(name=name, argv=argv, cwd=cwd, prefix=PREFIX,
                                      target_cycle=cycle, env=base.thread_environment())
                ok, problems = call_succeeded(receipt, cwd, cycle)
                record.update({"status": "COMPLETED" if ok else "FAILED", "problems": problems,
                               "elapsed_seconds": receipt.get("elapsed_seconds"),
                               "returncode": receipt.get("returncode"),
                               "stop_reason": receipt.get("stop_reason")})
                outcome[name] = ok
                teardown = receipt.get("teardown") or {}
                if teardown.get("unreaped_leader") or teardown.get("deadline_exhausted"):
                    record["stopped_group"] = "previous call's teardown was incomplete"
                    self.save()
                    break
            except Exception as exc:
                record.update({"status": "REFUSED_OR_ERROR", "error": str(exc)})
                outcome[name] = False
                self.save()
                if isinstance(exc, DiagError) and ("does not fit" in str(exc) or "live pw.x" in str(exc)):
                    break
                if self.receipt["scheduler_status"] == "REFUSED":
                    break
            self.save()
        if checkpoint_inventory is not None:
            after = base.inventory(Path(self.spec["checkpoint"]["outdir"]))
            self.receipt["checkpoint_after_sha256"] = after["sha256"]
            self.receipt["checkpoint_unchanged"] = after == checkpoint_inventory
        self.receipt["finished_utc"] = base.utc_now()
        self.receipt["all_calls_completed"] = all(outcome.get(name) for name, _, _ in GROUPS[self.group])
        self.save()
        return 0 if self.receipt["all_calls_completed"] else 3


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--group", choices=sorted(GROUPS), required=True)
    args = parser.parse_args(argv)
    def interrupted(signum, frame):
        raise KeyboardInterrupt("controller received " + signal.Signals(signum).name)
    # scancel / time limit: run_arm tears down its process group and the receipts are saved.
    for signum in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, interrupted)
    if base.sha256_file(args.spec) != args.spec_sha256:
        raise DiagError("spec bytes differ from the reviewed pin")
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    return Group(spec, args.group).run()


if __name__ == "__main__":
    raise SystemExit(main())
