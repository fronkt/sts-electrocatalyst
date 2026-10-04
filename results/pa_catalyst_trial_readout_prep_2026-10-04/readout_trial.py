#!/usr/bin/env python3
"""Read-only post-run readout for the approved catalyst P-A boundary trial.

Inputs are local only: a mirror of the trial's raw outputs plus saved scheduler
text (sacct / scontrol / jobsu).  Nothing here opens a network connection,
submits, cancels or invokes QE.  It never writes inside the mirror or the
repository; --out receives new files and refuses to overwrite.

Every criterion carries file:line citations with a verbatim quote taken from
the registered documents or the frozen controller; no threshold is defined
here.  Where the registered criteria assign no PASS/FAIL/INCONCLUSIVE label to
an observed situation the outcome is UNMAPPED and the open question is named,
rather than decided.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCHEMA = "pa-catalyst-readout-v1"
HERE = Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parents[1]
JOB_ID = "21034683"
PREFIX = "slab_c5low__pa_boundary"  # src/dft/pa_catalyst_trial.py:43
ARM_ORDER = ("control", "candidate", "fresh", "resumed", "reseed", "negative")
SPEC_REL = "results/pa_catalyst_trial_2026-10-03/launch_spec.json"
SOURCE_DECK_REL = ("runs/hea/lowtail_low_state_restart_2026-09-22/"
                   "Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in")
# results/pa_catalyst_trial_2026-10-03/watch_trial_readonly.py:11-12 (drift-tested).
TERMINAL_STATES = frozenset({"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY",
                             "NODE_FAIL", "PREEMPTED", "BOOT_FAIL", "DEADLINE"})
SACCT_COLUMNS = ("JobIDRaw", "State", "ExitCode", "ElapsedRaw", "AllocCPUS", "ReqMem",
                 "AllocTRES", "CPUTimeRAW")  # the watcher's --format, watch_trial_readonly.py:26
# Adapter's own log-vs-XML evaluated-energy agreement bound (pa_qe_adapter.py:845).
LOG_XML_ENERGY_TOL_RY = 5.1e-8
# Registered first-boundary SCF target, DOC:23 "target is1e-6Ry" (same value the adapter requires).
FIRST_THRESHOLD_RY = 1e-6
# Calls whose first printed threshold the frozen controller checks (CTRL:857); a resumed call starts
# from an already-updated optimizer state and is deliberately outside the check.
FIRST_THRESHOLD_KINDS = ("control", "candidate", "fresh", "reseed", "negative")
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"

# Registered call table; line numbers are pa_catalyst_trial.py call sites (drift-tested).
REGISTERED = {
    "control": {"kind": "control", "target_cycle": 3, "expected_cycles": [1, 2, 3],
                "expected_steps": 3, "exit": "clean_stop", "evaluations": 3, "site": 890},
    "candidate": {"kind": "candidate", "target_cycle": 1, "expected_cycles": [1],
                  "expected_steps": 1, "exit": "clean_stop", "evaluations": 1, "site": 892},
    "fresh": {"kind": "fresh", "target_cycle": None, "expected_cycles": [],
              "expected_steps": 0, "exit": "normal_scf", "evaluations": 1, "site": 913},
    "resumed": {"kind": "resumed", "target_cycle": 3, "expected_cycles": [2, 3],
                "expected_steps": 2, "exit": "clean_stop", "evaluations": 2, "site": 955},
    "reseed": {"kind": "reseed", "target_cycle": 1, "expected_cycles": [1],
               "expected_steps": 1, "exit": "clean_stop", "evaluations": 1, "site": 942},
    "negative": {"kind": "negative", "target_cycle": 3, "expected_cycles": [1, 2, 3],
                 "expected_steps": 3, "exit": "clean_stop", "evaluations": 3, "site": 966},
}
BRANCH_SEQUENCES = {
    "RESUME": ["control", "candidate", "fresh", "resumed", "negative"],
    "RESUME_NO_NEGATIVE": ["control", "candidate", "fresh", "resumed"],
    "RESEED": ["control", "candidate", "fresh", "reseed"],
    "HOLD": ["control", "candidate", "fresh"],
}

# ----------------------------------------------------------------------------------------
# Criteria registry.  Quotes are single-line verbatim substrings; line numbers are as of
# HEAD b3b64ce and are re-resolved at run time (check_citations).
# ----------------------------------------------------------------------------------------
DOC = "docs/research/pa-catalyst-trial-2026-10-03.md"
REV = "results/pa_catalyst_trial_2026-10-03/independent_launch_review_final.md"
REV1 = "results/pa_catalyst_trial_2026-10-03/independent_launch_review.md"
IMPL = "results/pa_catalyst_trial_2026-10-03/implementation_findings.md"
SBR = "results/pa_catalyst_trial_2026-10-03/source_boundary_review.md"
SPEC = "results/pa_catalyst_trial_2026-10-03/launch_spec.json"
CTRL = "src/dft/pa_catalyst_trial.py"
ADP = "src/dft/pa_qe_adapter.py"
ELIG = "docs/research/eligible-comparison-pa-readiness-2026-10-03.md"
WATCH = "results/pa_catalyst_trial_2026-10-03/watch_trial_readonly.py"
WRAP = "anvil/89_pa_catalyst_boundary_trial.slurm"
KIND_STATED, KIND_FROZEN = "PRESTATED", "FROZEN_CONTROLLER_BEHAVIOUR"


def _c(cid, kind, text, *cites):
    return cid, {"id": cid, "kind": kind, "text": text,
                 "cites": [{"file": f, "line": n, "quote": q} for f, n, q in cites]}


CRITERIA = dict([
    _c("SCHED_ALLOC", KIND_STATED,
       "One regular whole 128-core node, 16 h / 2048 CPU SU ceiling, <=200 GiB.",
       (DOC, 8, "Approval is one regular"), (SPEC, 48, '"max_cpu_su": 2048')),
    _c("SCHED_CALLS", KIND_STATED,
       "At most six sequential QE calls each <=2 h; no retry/requeue/array/chaining.",
       (DOC, 9, "at most six sequential QE calls"), (SPEC, 51, '"max_calls": 6')),
    _c("SCHED_CAP_SU", KIND_STATED,
       "The scheduler charge is capped by one 128-core 16 h allocation.",
       (DOC, 85, "The scheduler charge is capped"), (ELIG, 127, "node-exclusive billing charges the entire")),
    _c("SCHED_PER_CALL", KIND_STATED,
       "Every QE call needs actual scheduler accounting and the full registered 7200 s plus cleanup inside remaining time.",
       (DOC, 79, "Every QE call requires actual scheduler"), (DOC, 80, "within remaining aggregate time")),
    _c("SCHED_SEPARATE", KIND_STATED,
       "Scheduler and scientific outcomes are retained separately.",
       (DOC, 105, "Scheduler and scientific outcomes")),
    _c("REPORT_RULE", KIND_STATED,
       "Report a source-bound numerical pass, failure or inconclusive result and actual SU without a hidden rerun.",
       (DOC, 106, "report a source-bound numerical"), (DOC, 107, "without a hidden rerun")),
    _c("NO_PRODUCTION", KIND_STATED,
       "No production relaxation, every-step P-A, S8 ranking or melt release follows; production_accepted stays false.",
       (DOC, 10, "not approve production relaxation"), (DOC, 123, "No production or catalyst-runtime success"),
       (SPEC, 56, '"production_accepted": false')),
    _c("SEQUENCE", KIND_STATED,
       "Control(3 evaluations), stopped candidate(1), fresh SCF at the evaluated geometry, then the fresh decision before any resume.",
       (DOC, 31, "Sequence: three-evaluation"), (DOC, 33, "geometry, not its post-move proposal")),
    _c("BRANCH_RESUME", KIND_STATED,
       "Fresh state not more than 10 meV/cell lower: the copied candidate resumes with inherited optimizer state for two further evaluations.",
       (DOC, 34, "If the fresh state is not more than"), (DOC, 35, "with inherited optimizer state for two")),
    _c("BRANCH_RESEED", KIND_STATED,
       "Fresh state strictly more than 10 meV lower: intentional density reseed/history reset, reported separately; exactly 10 meV or higher does not trigger.",
       (DOC, 36, "more than10meV lower"), (DOC, 37, "reseed/history reset at the evaluated geometry"),
       (DOC, 38, "Exactly10meV or a higher fresh state")),
    _c("BRANCH_HOLD", KIND_STATED,
       "A failed/missing fresh reference holds continuation.",
       (DOC, 39, "fresh reference holds continuation")),
    _c("NEG_CONTROL", KIND_STATED,
       "Copied-history/from-scratch negative control establishes actual startup deletion and optimizer count 0.",
       (DOC, 40, "negative control establishes actual startup")),
    _c("RESEED_VALID", KIND_STATED,
       "Reseed branch is numerically validated only if its first evaluated energy is within 1e-6 Ry of the lower fresh reference and strictly >10 meV/cell below the original warm state, same geometry/settings.",
       (DOC, 41, "The reseed branch is only numerically validated"), (DOC, 42, "energy remains within1e-6Ry"),
       (DOC, 43, "below the original warm state"), (IMPL, 23, "within1e-6Ry and remain strictly")),
    _c("CONTINUITY_TOL", KIND_STATED,
       "Control and candidate+resume match all three ordered evaluations within 1e-6 Ry, 1e-5 bohr, 1e-5 Ry/bohr; no interpolation, endpoint-only comparison, remapping or dropped frames.",
       (DOC, 46, "Control and candidate+resume must match"), (DOC, 47, "1e-6Ry energy,1e-5bohr"),
       (DOC, 48, "endpoint-only comparison"), (ADP, 31, 'TOLERANCES = {"energy_Ry": 1e-6')),
    _c("NO_SPLICE", KIND_STATED,
       "A reseed branch cannot be spliced into a continuity pass; without a true lower-state trigger genuine catalyst reseed remains unvalidated.",
       (DOC, 49, "branch cannot be spliced"), (DOC, 50, "occurs, genuine catalyst reseed remains unvalidated"),
       (REV, 140, "uses new history and cannot be spliced")),
    _c("BOUNDARY_COUNTS", KIND_STATED,
       "Exact saved evaluated XML counts 1/3/2 and global SCF-cycle sequences [1]/[1,2,3]/[2,3] (candidate/control/resumed), user stop, status 255, JOB DONE, no stale EXIT.",
       (DOC, 59, "exact saved evaluated XML count"), (REV, 67, "Candidate/control/resumed require exact local XML counts"),
       (REV, 68, "global stdout sequences1")),
    _c("FIRST_THRESHOLD", KIND_STATED,
       "Warm first-boundary target and the fresh SCF target are both 1e-6 Ry, verified in the raw log (control, candidate, fresh, reseed, negative; not the resumed call).",
       (DOC, 23, "target is1e-6Ry"), (DOC, 25, "first warm target must verify"),
       (CTRL, 857, 'if kind in {"control", "candidate", "fresh", "reseed", "negative"}:')),
    _c("REJECT_LIST", KIND_STATED,
       "Reject symlinks/special files, fallback/reset on continuation, unverified consumed UPFs, failed/stalled energies or expanded allocation.",
       (DOC, 82, "symlinks/special files, fallback/reset"), (DOC, 83, "failed/stalled energies")),
    _c("SUPERVISION", KIND_STATED,
       "SCF iteration 127 supervision, clean-stop request, hard process-group deadline and no retry apply to every call.",
       (DOC, 83, "SCF iteration127 supervision")),
    _c("RAW_BINDING", KIND_STATED,
       "Raw bindings: source deck bytes, executable/MPI/UPF hashes and actual runtime parallel shape (MPI128, 1 thread, 8 pools, ELPA 4x4).",
       (DOC, 68, "Raw bindings include source deck bytes"), (REV, 137, "Actual catalyst MPI/ELPA/UPF/settings/source identity")),
    _c("INCONC_BOUNDARY", KIND_STATED,
       "Early convergence, nstep exhaustion or a missed boundary is inconclusive without retry.",
       (DOC, 61, "Early convergence, nstep exhaustion"), (REV, 70, "natural convergence, skipped boundary"),
       (SBR, 39, "Natural BFGS convergence before the registered boundary")),
    _c("INCONC_PROCESS", KIND_STATED,
       "A solver limit, HEA4 stall, resource problem or missing clean boundary is inconclusive; teardown cannot justify exceeding authority or launching a replacement.",
       (REV, 134, "A solver limit, HEA4"), (REV, 136, "justify exceeding authority"),
       (SBR, 298, "stall/timeout/OOM or missed boundary")),
    _c("INCONC_RESEED", KIND_STATED,
       "An attempted or upper-state reseed stays inconclusive, not a genuine lower-state validation.",
       (IMPL, 24, "An attempted or upper-state reseed stays"), (REV1, 36, "Failure must remain inconclusive/attempted")),
    _c("LATER_GATES", KIND_STATED,
       "Full every-step checks and terminal fresh acceptance remain later gates regardless of this trial's outcome.",
       (DOC, 51, "terminal fresh acceptance remain later gates"), (ELIG, 162, "Full every-step checking/reseeding")),
    _c("CTRL_STATUS_MAP", KIND_FROZEN,
       "Frozen controller records HOLD / RESEED_BRANCH_ONLY / PASS_ONE_BOUNDARY / INCONCLUSIVE; a continuity-tolerance miss and any raised TrialError are recorded INCONCLUSIVE.",
       (CTRL, 934, 'self.receipt["scientific_status"] = "HOLD"'),
       (CTRL, 951, 'self.receipt["scientific_status"] = "RESEED_BRANCH_ONLY"'),
       (CTRL, 964, 'raise TrialError("all three ordered evaluations did not agree")'),
       (CTRL, 970, 'self.receipt["scientific_status"] = "PASS_ONE_BOUNDARY"'),
       (CTRL, 983, 'self.receipt["scientific_status"] = "INCONCLUSIVE"')),
    _c("CTRL_NEGATIVE_BLOCKS", KIND_FROZEN,
       "Frozen controller runs the optional negative control before assigning PASS_ONE_BOUNDARY, so a failed negative control leaves the trial INCONCLUSIVE.",
       (SPEC, 55, '"optional_negative_control": true'), (CTRL, 965, 'if self.spec["optional_negative_control"]:'),
       (CTRL, 970, 'self.receipt["scientific_status"] = "PASS_ONE_BOUNDARY"')),
    _c("CTRL_EXIT_CODE", KIND_FROZEN,
       "Controller exit status: 0 only for PASS_ONE_BOUNDARY, otherwise 3; refusal before a result exits 2 printing INCONCLUSIVE/UNVERIFIED.",
       (CTRL, 1021, 'return 0 if result["scientific_status"] == "PASS_ONE_BOUNDARY" else 3'),
       (CTRL, 1023, '"scientific_status": "INCONCLUSIVE", "scheduler_status": "UNVERIFIED"'),
       (WRAP, 30, 'exec "$PYTHON"')),
    _c("CTRL_CALL_CONTRACT", KIND_FROZEN,
       "A call is VALIDATED only if not timed out, within the 7200 s cap, no supervisor/capture error, no failure marker, no HEA4 stall, no solver limit and the registered boundary stop receipt.",
       (CTRL, 840, 'if (process.get("timed_out") or process.get("within_per_call_cap") is not True'),
       (CTRL, 846, 'raise TrialError(name + " lacks the registered boundary stop receipt")'),
       (CTRL, 870, 'call["status"] = "NUMERICAL_RECEIPT_VALIDATED"')),
    _c("CTRL_AGGREGATE", KIND_FROZEN,
       "Controller refuses a call whose full 7200 s plus 120 s cleanup does not fit and records INCONCLUSIVE at 16 h aggregate.",
       (CTRL, 694, "raise TrialError(\"full registered 7200-second call plus cleanup does not fit"),
       (CTRL, 981, 'raise TrialError("aggregate elapsed time reached 16h")')),
])

# Error strings emitted by the frozen controller that distinguish a post-validation
# integrity stop (CTRL:923, CTRL:978) and the aggregate-time stop (CTRL:981).
ERR_INTEGRITY = ("immutable restart checkpoint changed", "immutable checkpoint changed")
ERR_AGGREGATE = ("aggregate elapsed time reached 16h",)

OPEN_QUESTIONS = {
    "OQ1": "Label for a clean continuity-tolerance miss. The doc names 'failure' (DOC:106) but defines only the "
           "tolerances (DOC:46-48); the frozen controller records INCONCLUSIVE (CTRL:964,983). FAIL is never "
           "defined or emitted, so this outcome is UNMAPPED with candidates FAIL/INCONCLUSIVE.",
    "OQ2": "Label when the resumed call is valid but the saved optimizer state was not consumed (consumption audit "
           "raises, CTRL:960). Same situation as OQ1.",
    "OQ3": "Label for HOLD with no process-level failure (fresh decision/checkpoint integrity). DOC:39 says only "
           "'holds continuation'.",
    "OQ4": "Whether RESEED_BRANCH_ONLY counts as a trial PASS. DOC:36-37 says report that branch separately and "
           "DOC:49-50 forbids splicing it into a continuity pass; no label is stated.",
    "OQ5": "Whether a failed optional negative control (after a numerically valid continuity pass) voids the pass. "
           "The spec calls the control optional (SPEC:55) but the frozen controller makes it blocking (CTRL:965-970).",
    "OQ6": "Which figure is the charged SU of record: sacct ElapsedRaw x billing, CPUTimeRAW, or `jobsu` (rounds "
           "used hours to 4 dp). The tiny run reported jobsu 0.1376 while the exact product is 0.1378.",
    "OQ7": "Slurm exit status is separate from the scientific outcome (DOC:105). A controller-ordered non-PASS exits 3 "
           "and Slurm shows FAILED 3:0 (CTRL:1021); the docs do not say whether that scheduler FAILED counts as a "
           "scheduler-side failure of the trial.",
    "OQ8": "Raw-validation refusals (UPF/settings/shape/XML parse) are recorded INCONCLUSIVE by the controller "
           "(CTRL:876) while the doc says 'reject' (DOC:81-83); the label is the controller's, not stated in the doc.",
}


# ----------------------------------------------------------------------------------------
# Citation verification
# ----------------------------------------------------------------------------------------
def check_citations(repo=DEFAULT_REPO, criteria=None):
    """Re-resolve every cited quote; report EXACT / MOVED / QUOTE_NOT_FOUND / FILE_MISSING."""
    repo, rows = Path(repo), []
    cache = {}
    for cid, criterion in (criteria or CRITERIA).items():
        for cite in criterion["cites"]:
            path = repo / cite["file"]
            if cite["file"] not in cache:
                cache[cite["file"]] = (path.read_text(encoding="utf-8", errors="replace").splitlines()
                                       if path.is_file() else None)
            lines = cache[cite["file"]]
            row = {"criterion": cid, "file": cite["file"], "line": cite["line"], "quote": cite["quote"]}
            if lines is None:
                row["status"] = "FILE_MISSING"
            elif cite["line"] <= len(lines) and cite["quote"] in lines[cite["line"] - 1]:
                row["status"] = "EXACT"
            else:
                now = [i + 1 for i, line in enumerate(lines) if cite["quote"] in line]
                row["status"], row["line_now"] = ("MOVED", now) if now else ("QUOTE_NOT_FOUND", [])
            rows.append(row)
    return rows


# ----------------------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------------------
def _int(value, default=None):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _float(value, default=None):
    try:
        number = float(str(value).replace("D", "e").replace("d", "e"))
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path):
    path = Path(path)
    if not path.is_file():
        return None, "absent"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return None, "unreadable: " + str(exc)


def _read_text(path):
    path = Path(path)
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


@contextlib.contextmanager
def _no_bytecode():
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        yield
    finally:
        sys.dont_write_bytecode = old


def load_modules(repo=DEFAULT_REPO):
    """Import the frozen controller/adapter read-only (no bytecode written)."""
    src = str(Path(repo) / "src" / "dft")
    with _no_bytecode():
        if src not in sys.path:
            sys.path.insert(0, src)
        import pa_catalyst_trial as trial  # noqa: WPS433
        import pa_qe_adapter as adapter  # noqa: WPS433
    return trial, adapter


# ----------------------------------------------------------------------------------------
# Scheduler record
# ----------------------------------------------------------------------------------------
def parse_tres(text):
    return dict(part.split("=", 1) for part in (text or "").split(",") if "=" in part)


def _mem_gib(text):
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)([KMGT])[nc]?", (text or "").strip())
    if not match:
        return None
    return float(match.group(1)) * {"K": 1 / 1024 ** 2, "M": 1 / 1024, "G": 1.0, "T": 1024.0}[match.group(2)]


def parse_sacct(text, job_id=JOB_ID):
    """Parse `sacct -P` text (with or without -n) for the singleton job."""
    rows = [[cell.strip() for cell in line.split("|")] for line in (text or "").splitlines() if line.strip()]
    columns = list(SACCT_COLUMNS)
    if rows and rows[0] and rows[0][0].lower() in ("jobidraw", "jobid"):
        columns = rows.pop(0)
    records = [dict(zip(columns, row)) for row in rows]
    key = "JobIDRaw" if "JobIDRaw" in columns else "JobID"
    main = next((r for r in records if r.get(key) == job_id), None)
    result = {"found": main is not None, "job_id": job_id, "rows": len(records), "columns": columns}
    if main is None:
        return result
    state_raw = main.get("State", "")
    state = state_raw.split()[0].rstrip("+") if state_raw.split() else "ACCOUNTING_PENDING"
    code, _, signal = (main.get("ExitCode", "") or "").partition(":")
    tres = parse_tres(main.get("AllocTRES", ""))
    result.update({
        "state_raw": state_raw, "state": state, "terminal": state in TERMINAL_STATES,
        "exit_code": _int(code), "exit_signal": _int(signal),
        "elapsed_s": _int(main.get("ElapsedRaw")), "alloc_cpus": _int(main.get("AllocCPUS")),
        "req_mem": main.get("ReqMem"), "alloc_tres": tres,
        "cputime_raw_s": _int(main.get("CPUTimeRAW")),
        "extra": {k: v for k, v in main.items() if k not in SACCT_COLUMNS and k != key},
        "steps": [{"id": r.get(key), "state": r.get("State"), "exit": r.get("ExitCode")}
                  for r in records if r is not main]})
    return result


def parse_scontrol(text):
    return dict(re.findall(r"(?:^|\s)([^\s=]+)=([^\s]+)", text or ""))


def parse_jobsu(text):
    text = text or ""
    def grab(pattern):
        match = re.search(pattern, text)
        return _float(match.group(1)) if match else None
    return {"cpu_su_job": grab(r"CPU SUs Already Used:\s*([0-9]*\.?[0-9]+)"),
            "cpu_su_total_all_jobs": grab(r"Total CPU SUs used for all jobs:\s*([0-9]*\.?[0-9]+)"),
            "gpu_su_total_all_jobs": grab(r"Total GPU SUs used for all jobs:\s*([0-9]*\.?[0-9]+)"),
            "used_walltime": (re.search(r"Used Walltime:\s*(\S+)", text) or [None, None])[1],
            "present": bool(text.strip())}


def charged_su(sched):
    """Whole-node billing: elapsed hours x billing CPUs (CPUTimeRAW kept as a cross-check)."""
    if not sched.get("found") or sched.get("elapsed_s") is None:
        return None
    billing = _int(sched.get("alloc_tres", {}).get("billing")) or sched.get("alloc_cpus") or 0
    return sched["elapsed_s"] * billing / 3600.0


def assess_scheduler(sched, spec, *, scontrol=None, jobsu=None):
    allocation, caps = spec["allocation"], spec["caps"]
    out = {"record": sched, "found": bool(sched.get("found")), "terminal": bool(sched.get("terminal")),
           "checks": [], "charged_cpu_su": None, "cap_su": allocation["max_cpu_su"],
           "time_limit_s": allocation["time_limit_seconds"]}
    def check(cid, ok, observed, expected):
        out["checks"].append({"id": cid, "ok": ok, "observed": observed, "expected": expected})
    if not sched.get("found"):
        out["state"] = None
        return out
    tres = sched.get("alloc_tres", {})
    out["state"], out["terminal"] = sched["state"], sched["terminal"]
    su = charged_su(sched)
    out["charged_cpu_su"] = su
    out["cputimeraw_su"] = None if sched.get("cputime_raw_s") is None else sched["cputime_raw_s"] / 3600.0
    if jobsu and jobsu.get("present"):
        out["jobsu_reported_su"] = jobsu.get("cpu_su_job", jobsu.get("cpu_su_total_all_jobs"))
        if out["jobsu_reported_su"] is None:
            out["jobsu_reported_su"] = jobsu.get("cpu_su_total_all_jobs")
        out["jobsu_minus_computed_su"] = (None if su is None or out["jobsu_reported_su"] is None
                                          else out["jobsu_reported_su"] - su)
    ran = bool(sched.get("alloc_cpus"))
    if ran:
        check("alloc_cpus", sched["alloc_cpus"] == allocation["cpus"], sched["alloc_cpus"], allocation["cpus"])
        check("tres_cpu", tres.get("cpu") == str(allocation["cpus"]), tres.get("cpu"), str(allocation["cpus"]))
        check("tres_billing", tres.get("billing") == str(allocation["billing"]), tres.get("billing"), str(allocation["billing"]))
        check("tres_node", tres.get("node") == "1", tres.get("node"), "1")
        memory = _mem_gib(tres.get("mem", ""))
        check("tres_mem_gib", memory is not None and memory <= allocation["memory_gib"], memory, "<=%d" % allocation["memory_gib"])
        check("no_gres", not any(key.startswith("gres") for key in tres), sorted(tres), "no gres/*")
        check("elapsed_within_time_limit", sched["elapsed_s"] is not None and sched["elapsed_s"] <= allocation["time_limit_seconds"],
              sched["elapsed_s"], "<=%d" % allocation["time_limit_seconds"])
        check("charged_su_within_cap", su is not None and su <= allocation["max_cpu_su"], su, "<=%d" % allocation["max_cpu_su"])
    else:
        check("ran_at_all", False, "AllocCPUS=%s" % sched.get("alloc_cpus"), ">0 (job must have been allocated)")
    if scontrol:
        fields = parse_scontrol(scontrol)
        out["scontrol"] = {k: fields.get(k) for k in ("Account", "Partition", "NumNodes", "NumCPUs", "NumTasks",
                                                       "CPUs/Task", "TimeLimit", "RunTime", "StartTime", "EndTime",
                                                       "NodeList", "Requeue", "Restarts", "Dependency", "ExitCode", "JobState")}
        for key, expected in (("Account", allocation["account"]), ("Partition", allocation["partition"]),
                              ("Requeue", "0"), ("Restarts", "0"), ("Dependency", "(null)")):
            if fields.get(key) is not None:
                check("scontrol_" + key.lower(), fields[key] == expected, fields[key], expected)
    out["all_resource_checks_ok"] = all(c["ok"] for c in out["checks"]) if out["checks"] else None
    code = sched.get("exit_code")
    out["slurm_exit_vs_controller"] = (
        {"COMPLETED:0": "controller PASS_ONE_BOUNDARY (CTRL:1021 exit 0)",
         "FAILED:3": "controller wrote a non-PASS result (CTRL:1021 exit 3)",
         "FAILED:2": "controller refusal path (CTRL:1022-1025 exit 2)"}.get("%s:%s" % (sched["state"], code),
                                                                           "no registered exit-status meaning"))
    out["aggregate_seconds_cap"] = caps["aggregate_seconds"]
    return out


# ----------------------------------------------------------------------------------------
# Raw summaries (tolerant: never raise on malformed science)
# ----------------------------------------------------------------------------------------
def parse_qe_clock(text):
    """'1d 2h 3m4.5s' style QE timer -> seconds (None when nothing parses)."""
    parts = re.findall(r"(\d+(?:\.\d+)?)\s*([dhms])", text or "")
    if not parts:
        return None
    scale = {"d": 86400.0, "h": 3600.0, "m": 60.0, "s": 1.0}
    return sum(float(value) * scale[unit] for value, unit in parts)


def summarize_stdout(text, trial=None):
    if text is None:
        return {"present": False}
    failure = getattr(trial, "FAILURE", None) or re.compile(r"convergence NOT achieved|Error in routine|MPI_ABORT", re.I)
    time_failure = getattr(trial, "TIME_FAILURE", None) or re.compile(r"Maximum (?:CPU|wall) time|maximum number of steps", re.I)
    iteration = getattr(trial, "SCF_ITERATION", None) or re.compile(r"(?m)^[ \t]*iteration[ \t]*#[ \t]*(\d+)")
    iterations = [int(m.group(1)) for m in iteration.finditer(text)]
    achieved = re.findall(r"convergence has been achieved in\s+(\d+)\s+iterations", text)
    not_achieved = re.findall(r"convergence NOT achieved after\s+(\d+)\s+iterations", text)
    bfgs_matches = list(re.finditer(r"number of bfgs steps\s*=\s*(\d+)", text))
    wall = re.search(r"PWSCF\s*:\s*(.*?)\s+CPU\s+(.*?)\s+WALL", text)
    accuracy = re.findall(r"estimated scf accuracy\s*<\s*(" + NUM + r")\s*Ry", text)
    threshold = re.findall(r"convergence threshold\s*=\s*(" + NUM + r")", text)
    startup = text[:bfgs_matches[0].start()] if bfgs_matches else text
    return {
        "present": True, "bytes": len(text.encode("utf-8", "replace")),
        "qe_banners": re.findall(r"Program PWSCF v\.([0-9.]+) starts", text),
        "mpi_processes": _int((re.search(r"Number of MPI processes:\s*(\d+)", text) or [None, None])[1]),
        "job_done": "JOB DONE." in text,
        "stopped_by_user": "Program stopped by user request" in text,
        "bfgs_converged": bool(re.search(r"bfgs converged in", text, re.I)),
        "failure_markers": sorted({m.group(0) for m in failure.finditer(text)}),
        "time_or_nstep_limit": bool(time_failure.search(text)),
        "scf_converged_count": len(achieved), "scf_not_converged_count": len(not_achieved),
        "scf_iterations_to_converge": [int(v) for v in achieved],
        "max_scf_iteration_seen": max(iterations) if iterations else None,
        "scf_cycles": [int(v) for v in re.findall(r"(?m)^[ \t]*number of scf cycles[ \t]*=[ \t]*(\d+)[ \t]*$", text)],
        "bfgs_counts": [int(m.group(1)) for m in bfgs_matches],
        "startup_history_deleted": ".bfgs deleted, as requested" in startup,
        "total_energies_Ry": [_float(v) for v in re.findall(r"(?m)^\s*!\s+total energy\s*=\s*(" + NUM + r")\s+Ry\s*$", text)],
        "first_conv_thr_Ry": _float(threshold[0]) if threshold else None,
        "last_scf_accuracy_Ry": _float(accuracy[-1]) if accuracy else None,
        "wall_seconds": parse_qe_clock(wall.group(2)) if wall else None,
        "cpu_seconds": parse_qe_clock(wall.group(1)) if wall else None,
    }


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def summarize_xml(path):
    path = Path(path)
    if not path.is_file():
        return {"present": False}
    try:
        root = ET.parse(str(path)).getroot()
    except (ET.ParseError, OSError) as exc:
        return {"present": True, "parse_ok": False, "error": str(exc)}
    def child(node, name):
        return next((c for c in node if _local(c.tag) == name), None)
    def energy_ry(node):
        total = child(node, "total_energy")
        etot = child(total, "etot") if total is not None else None
        return None if etot is None else (2.0 * _float(etot.text) if _float(etot.text) is not None else None)
    steps = []
    for node in root:
        if _local(node.tag) != "step":
            continue
        conv = child(node, "scf_conv")
        achieved = child(conv, "convergence_achieved") if conv is not None else None
        iters = child(conv, "n_scf_iterations") if conv is not None else None
        steps.append({"n_step": node.attrib.get("n_step"),
                      "converged": None if achieved is None else (achieved.text or "").strip().lower() == "true",
                      "n_scf_iterations": None if iters is None else _int(iters.text),
                      "etot_Ry": energy_ry(node)})
    status = child(root, "exit_status")
    output = child(root, "output")
    creator = child(child(root, "general_info"), "creator") if child(root, "general_info") is not None else None
    parallel = {}
    info = child(root, "parallel_info")
    if info is not None:
        parallel = {_local(n.tag): _int(n.text) for n in info}
    return {"present": True, "parse_ok": True, "units": root.attrib.get("Units"),
            "exit_status": None if status is None else _int(status.text), "steps": steps,
            "output_etot_Ry": None if output is None else energy_ry(output),
            "creator_version": None if creator is None else creator.attrib.get("VERSION"),
            "parallel": parallel, "sha256": sha256_file(path)}


def arm_paths(trial_dir, name):
    arm = Path(trial_dir) / name
    xml_options = [arm / "outdir" / (PREFIX + ".save") / "data-file-schema.xml",
                   arm / "checkpoint_copy" / "outdir" / (PREFIX + ".save") / "data-file-schema.xml"]
    existing = [p for p in xml_options if p.is_file()]
    return {"arm": arm, "input": arm / "input.in", "stdout": arm / "stdout.log", "stderr": arm / "stderr.log",
            "process_receipt": arm / "process_receipt.json", "setup_receipt": arm / "setup_receipt.json",
            "parsed_receipt": arm / "parsed_receipt.json",
            "xml": existing[0] if existing else xml_options[0], "xml_candidates_present": len(existing)}


def header_binding(text, adapter, shape):
    """Actual runtime header (MPI/threads/pools/ELPA) bound through the frozen adapter's own
    pa_qe_adapter._raw_parallel; usable on partial output of a call still running."""
    if text is None or adapter is None:
        return {"checked": False}
    source = {"path": "stdout.log", "sha256": hashlib.sha256(text.encode("utf-8", "replace")).hexdigest(),
              "line_start": 1, "line_end": max(1, len(text.splitlines()))}
    try:
        bound = adapter._raw_parallel(text, source, dict(shape))  # noqa: SLF001
    except Exception as exc:
        return {"checked": True, "ok": False, "error": "%s: %s" % (type(exc).__name__, exc)}
    return {"checked": True, "ok": True, "nprocs": bound["nprocs"], "nthreads": bound["nthreads"],
            "npool": bound["npool"], "diagonalization": bound["diagonalization_algorithm"],
            "elpa_subgroup": bound["elpa_subgroup"]}


def summarize_arm_raw(trial_dir, name, trial=None, adapter=None):
    paths = arm_paths(trial_dir, name)
    text = _read_text(paths["stdout"])
    out = {"arm_dir_present": paths["arm"].is_dir(),
           "stdout": summarize_stdout(text, trial),
           "header_binding": header_binding(text, adapter, getattr(trial, "SHAPE", {})),
           "stderr_bytes": (paths["stderr"].stat().st_size if paths["stderr"].is_file() else None),
           "xml": summarize_xml(paths["xml"]), "xml_candidates_present": paths["xml_candidates_present"]}
    out["xml_path"] = str(paths["xml"])
    energies, steps = out["stdout"].get("total_energies_Ry", []), out["xml"].get("steps", [])
    if out["stdout"].get("present") and out["xml"].get("parse_ok"):
        out["log_vs_xml_energy_max_abs_Ry"] = (
            max((abs(a - b["etot_Ry"]) for a, b in zip(energies, steps)
                 if a is not None and b["etot_Ry"] is not None), default=None)
            if len(energies) == len(steps) else None)
        out["log_xml_energy_counts"] = [len(energies), len(steps)]
    return out


# ----------------------------------------------------------------------------------------
# Mirror
# ----------------------------------------------------------------------------------------
def locate_mirror(mirror, job_id=JOB_ID):
    mirror = Path(mirror)
    if (mirror / "trial_results").is_dir():
        root, trial_dir = mirror, mirror / "trial_results"
    elif (mirror / "trial_receipt.json").is_file() or mirror.name == "trial_results":
        root, trial_dir = mirror.parent, mirror
    else:
        root, trial_dir = mirror, None
    log = root / ("trial_%s.log" % job_id)
    return {"root": root, "trial_dir": trial_dir, "slurm_log": log if log.is_file() else None}


def inventory_dir(root):
    root = Path(root)
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rows.append({"path": path.relative_to(root).as_posix(), "size": path.stat().st_size,
                     "sha256": sha256_file(path)})
    return rows


def mirror_selection(job_id=JOB_ID):
    """Lightweight remote-relative globs sufficient for this readout (binaries excluded)."""
    arms = ["trial_results/%s/%s" % (a, f) for a in ARM_ORDER
            for f in ("input.in", "stdout.log", "stderr.log", "process_receipt.json",
                      "setup_receipt.json", "parsed_receipt.json",
                      "outdir/%s.save/data-file-schema.xml" % PREFIX,
                      "checkpoint_copy/outdir/%s.save/data-file-schema.xml" % PREFIX)]
    return (["trial_%s.log" % job_id, "trial_results/trial_receipt.json",
             "trial_results/pre_resume_decision.json", "trial_results/reseed_lower_state_binding.json"]
            + ["trial_results/allocation_before_call_%02d.json" % i for i in range(1, 7)]
            + ["trial_results/common_pseudo/*", "trial_results/candidate_immutable/inventory.json",
               "trial_results/candidate_immutable/outdir/%s.bfgs" % PREFIX] + arms)


def normalize_remote_inventory(value):
    rows = value.get("files") if isinstance(value, dict) else value
    out = []
    for row in rows or []:
        if isinstance(row, dict) and isinstance(row.get("path"), str):
            out.append({"path": row["path"].replace("\\", "/").lstrip("/"), "size": row.get("size"),
                        "sha256": row.get("sha256")})
    return out


def compare_inventories(local_rows, remote_rows):
    """Remote rows with a sha256 are hash-verified; rows the remote side did not hash (large binaries)
    can only be size-checked and are counted separately, never as hash matches."""
    local = {r["path"]: r for r in local_rows}
    matched, size_only, mismatched, absent = [], [], [], []
    for row in remote_rows:
        mine = local.get(row["path"])
        if mine is None:
            absent.append(row["path"])
        elif row.get("sha256") is None:
            (size_only if row.get("size") is None or mine["size"] == row["size"] else mismatched).append(row["path"])
        elif mine["sha256"] != row["sha256"] or (row.get("size") is not None and mine["size"] != row["size"]):
            mismatched.append(row["path"])
        else:
            matched.append(row["path"])
    return {"remote_rows": len(remote_rows), "matched": len(matched), "size_only_matched": len(size_only),
            "mismatched": mismatched, "not_mirrored": absent,
            "local_only": sorted(set(local) - {r["path"] for r in remote_rows})}


# ----------------------------------------------------------------------------------------
# Re-derivation through the frozen adapter (no duplicate parser)
# ----------------------------------------------------------------------------------------
def rederive_arm(paths, *, adapter, expected_settings, expected_parallel, expected_exit,
                 expected_evaluations, upf_path_map=None):
    """Run the frozen adapter's read_qe_arm on explicit local files; never raise."""
    expected = copy.deepcopy(expected_settings)
    if upf_path_map:
        expected["upf_read_path_map"] = dict(upf_path_map)
    try:
        process, error = _load_json(paths["process_receipt"])
        if process is None:
            return {"ok": False, "error": "process receipt " + str(error), "parsed": None}
        parsed = adapter.read_qe_arm(paths["input"], paths["stdout"], paths["stderr"], paths["xml"], process,
                                     expected_settings=expected, expected_parallel=expected_parallel,
                                     expected_exit=expected_exit, expected_evaluations=expected_evaluations)
        return {"ok": True, "error": None, "parsed": parsed}
    except Exception as exc:  # the adapter fails closed with AdapterError/OSError/etc.
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, exc), "parsed": None}


def upf_map_from_stdout(text, common_pseudo):
    """Map each logged UPF read path onto the mirrored common_pseudo copy."""
    mapping = {}
    for match in re.finditer(r"PseudoPot\.\s*#\s*\d+\s+for\s+\S+\s+read from file:[ \t]*\n?[ \t]*([^\r\n]+)", text or ""):
        logged = match.group(1).strip()
        mapping[logged] = str(Path(common_pseudo) / Path(logged).name)
    return mapping


def rederive_trial(trial_dir, receipt, *, repo, spec, source_deck, trial, adapter):
    """Re-parse every present arm from raw files, then recompute cross-arm decisions."""
    out = {"arms": {}, "derived": {}, "notes": []}
    expected = adapter.parse_deck(source_deck, spec["source_deck"]["sha256"])
    expected["upf_pins"] = {Path(p["path"]).name: p["sha256"] for p in spec["upfs"]}
    common = Path(trial_dir) / "common_pseudo"
    parsed = {}
    for name in ARM_ORDER:
        paths = arm_paths(trial_dir, name)
        if not paths["arm"].is_dir():
            continue
        if not paths["xml"].is_file():
            out["arms"][name] = {"ok": False, "error": "XML absent from mirror", "parsed": None}
            continue
        setup, _ = _load_json(paths["setup_receipt"])
        reg = REGISTERED[name]
        cycles = (setup or {}).get("expected_cycles", reg["expected_cycles"])
        steps = (setup or {}).get("expected_xml_steps", reg["expected_steps"])
        evaluations = 1 if name == "fresh" else steps
        arm_expected = copy.deepcopy(expected)
        if name != "control" and "control" in parsed:
            arm_expected["xml_settings_identity"] = parsed["control"]["xml_settings_identity"]
        result = rederive_arm(paths, adapter=adapter, expected_settings=arm_expected,
                              expected_parallel=trial.SHAPE, expected_exit=reg["exit"],
                              expected_evaluations=evaluations,
                              upf_path_map=upf_map_from_stdout(_read_text(paths["stdout"]), common))
        checks = {}
        if result["ok"]:
            arm = result["parsed"]
            checks["scf_counts_match_expected"] = arm["scf_counts"] == list(cycles)
            if name in FIRST_THRESHOLD_KINDS:
                try:
                    adapter.require_expected_first_threshold(arm, expected)
                    checks["first_threshold_1e-6"] = True
                except Exception as exc:
                    checks["first_threshold_1e-6"] = False
                    checks["first_threshold_error"] = str(exc)
            if name == "negative":
                checks["startup_deletion_then_count0"] = bool(arm["startup_history_deleted"]
                                                              and arm["optimizer_counts"][:1] == [0])
            if name == "reseed":
                checks["new_optimizer_count0"] = arm["optimizer_counts"][:1] == [0]
            parsed[name] = arm
        result["post_checks"] = checks
        out["arms"][name] = result
    d = out["derived"]
    try:
        if {"control", "candidate", "resumed"} <= set(parsed):
            d["continuity"] = adapter.compare_trajectories(
                parsed["control"]["evaluations"],
                parsed["candidate"]["evaluations"] + parsed["resumed"]["evaluations"])
    except Exception as exc:
        d["continuity_error"] = "%s: %s" % (type(exc).__name__, exc)
    if {"candidate", "fresh"} <= set(parsed):
        warm, fresh = parsed["candidate"]["evaluations"][0], parsed["fresh"]["evaluations"][0]
        conversion, delta = adapter.RY_MEV, adapter.contract.DELTA_MEV
        d["warm_minus_fresh_meV"] = (warm["energy_Ry"] - fresh["energy_Ry"]) * conversion
        # Same expression as pa_qe_adapter.py:1213 (strict inequality).
        lower = fresh["energy_Ry"] < warm["energy_Ry"] - delta / conversion
        d["fresh_strictly_more_than_10meV_lower"] = bool(lower)
        d["implied_action"] = "RESEED_CANDIDATE" if lower else "RESUME_CANDIDATE"
    if {"candidate", "fresh", "reseed"} <= set(parsed):
        d["reseed_binding"] = trial.validate_reseed_binding(parsed["candidate"], parsed["fresh"],
                                                           parsed["reseed"], adapter=adapter)
    if {"candidate", "resumed"} <= set(parsed):
        resumed, candidate = parsed["resumed"], parsed["candidate"]
        proposal = candidate["proposal_geometry"]
        first = resumed["evaluations"][0]["geometry"]
        shift = (adapter._matrix_delta(first["positions"], proposal["positions"])  # noqa: SLF001
                 if proposal else None)
        d["resumed_observed"] = {
            "first_optimizer_count": (resumed["optimizer_counts"] or [None])[0],
            "first_scf_cycle": (resumed["scf_counts"] or [None])[0],
            "startup_history_reset": resumed["startup_history_reset"],
            "restart_fallback": resumed["restart_fallback"],
            "first_resumed_vs_saved_proposal_max_bohr": shift}
    return out


# ----------------------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------------------
PROCESS_FLAGS = ("timed_out", "supervisor_error", "capture_error", "failure_marker_observed",
                 "HEA4_stall_observed", "solver_limit_observed")


def call_failure_class(call, process):
    """Classify why a call is not VALIDATED, with the registered criterion that covers it."""
    status = call.get("status")
    if status == "NUMERICAL_RECEIPT_VALIDATED":
        return None
    if status == "STARTED":
        return "NOT_FINISHED"
    flags = [f for f in PROCESS_FLAGS if process.get(f)]
    if process.get("within_per_call_cap") is False:
        flags.append("over_per_call_cap")
    stop = process.get("stop_reason")
    if stop in ("missed-evaluated-boundary",):
        return "MISSED_BOUNDARY"
    if flags or stop in ("failure-marker", "HEA4-SCF-iteration-127", "solver-time-or-nstep-limit", "wall-soft-stop"):
        return "PROCESS_CONTRACT"
    error = (call.get("error") or "").lower()
    if any(key in error for key in ("evaluated stop boundary", "registered evaluated boundary",
                                    "scf counters miss", "boundary stop receipt", "stale exit")):
        return "MISSED_BOUNDARY"
    if "did not complete within the registered process contract" in error:
        return "PROCESS_CONTRACT"
    return "RAW_VALIDATION_REFUSED"


FAILURE_CLASS_CRITERIA = {
    "NOT_FINISHED": ("INCONC_PROCESS", "PRESTATED"),
    "PROCESS_CONTRACT": ("INCONC_PROCESS", "PRESTATED"),
    "MISSED_BOUNDARY": ("INCONC_BOUNDARY", "PRESTATED"),
    "RAW_VALIDATION_REFUSED": ("REJECT_LIST", "FROZEN_CONTROLLER_RECORD_ONLY"),
}


def sequence_result(names, spec_negative, status, action):
    """MET when the executed order is exactly a registered branch; PARTIAL_PREFIX when a
    registered branch was cut short; NOT_MET when the order or branch deviates."""
    if not names:
        return "NOT_EVALUATED", None
    if action == "RESEED_CANDIDATE" or status == "RESEED_BRANCH_ONLY":
        options = [BRANCH_SEQUENCES["RESEED"]]
    elif action == "HOLD" or status == "HOLD":
        options = [BRANCH_SEQUENCES["HOLD"]]
    elif action == "RESUME_CANDIDATE" or status == "PASS_ONE_BOUNDARY":
        options = [BRANCH_SEQUENCES["RESUME" if spec_negative else "RESUME_NO_NEGATIVE"]]
    else:  # branch not reached: any registered branch may still have been in progress
        options = [BRANCH_SEQUENCES["RESUME" if spec_negative else "RESUME_NO_NEGATIVE"],
                   BRANCH_SEQUENCES["RESEED"], BRANCH_SEQUENCES["HOLD"]]
    if any(names == seq for seq in options):
        return "MET", options[0]
    if any(names == seq[:len(names)] for seq in options):
        return "PARTIAL_PREFIX", options[0]
    return "NOT_MET", options[0]


def build_call_rows(trial_dir, receipt, trial=None, adapter=None):
    rows = []
    receipt_calls = receipt.get("calls", []) if receipt else []
    for index, call in enumerate(receipt_calls, 1):
        name = call.get("name")
        process = call.get("process") or {}
        raw = summarize_arm_raw(trial_dir, name, trial, adapter) if name else {}
        if not process:
            loaded, _ = _load_json(arm_paths(trial_dir, name)["process_receipt"]) if name else (None, None)
            process = loaded or {}
        parsed = call.get("parsed") or {}
        row = {"index": index, "name": name, "kind": call.get("kind"), "status": call.get("status"),
               "failure_class": call_failure_class(call, process), "error": call.get("error"),
               "stop_reason": process.get("stop_reason"), "returncode": process.get("returncode"),
               "elapsed_seconds": process.get("elapsed_seconds"),
               "within_per_call_cap": process.get("within_per_call_cap"),
               "timed_out": process.get("timed_out"),
               "process_flags": {f: process.get(f) for f in PROCESS_FLAGS + ("within_per_call_cap",)
                                 if f in process},
               "receipt_scf_counts": parsed.get("scf_counts"),
               "receipt_optimizer_counts": parsed.get("optimizer_counts"),
               "receipt_xml_exit_status": parsed.get("xml_exit_status"),
               "receipt_energies_Ry": [e.get("energy_Ry") for e in parsed.get("evaluations", [])],
               "receipt_eval_status": [e.get("status") for e in parsed.get("evaluations", [])],
               "raw": raw}
        reg = REGISTERED.get(name)
        if reg:
            row["registered_expected_cycles"] = reg["expected_cycles"]
            row["registered_evaluations"] = reg["evaluations"]
        rows.append(row)
    return rows


def evaluate(*, receipt, calls, sched, spec, trial_dir, slurm_log_text, mirror_gaps,
             rederived, allocation_receipts, repo):
    """Compute criteria results and the trial-level outcome."""
    results, notes, integrity = {}, [], []
    gates = {}
    def setr(cid, result, evidence=None):
        results[cid] = {"result": result, "evidence": evidence}
    spec_negative = bool(spec.get("optional_negative_control"))
    status = receipt.get("scientific_status") if receipt else None
    names = [c["name"] for c in calls]

    # --- scheduler/resource criteria ------------------------------------------------------
    checks = {c["id"]: c for c in sched.get("checks", [])}
    shape_ids = ("alloc_cpus", "tres_cpu", "tres_billing", "tres_node", "tres_mem_gib", "no_gres")
    if sched.get("found") and all(i in checks for i in shape_ids):
        setr("SCHED_ALLOC", "MET" if all(checks[i]["ok"] for i in shape_ids) and
             checks.get("elapsed_within_time_limit", {"ok": True})["ok"] else "NOT_MET",
             {i: checks[i]["observed"] for i in shape_ids})
    else:
        setr("SCHED_ALLOC", "NOT_EVALUATED", "no allocated sacct record")
    if "charged_su_within_cap" in checks:
        setr("SCHED_CAP_SU", "MET" if checks["charged_su_within_cap"]["ok"] else "NOT_MET",
             {"charged_cpu_su": sched.get("charged_cpu_su"), "cap": sched.get("cap_su")})
    else:
        setr("SCHED_CAP_SU", "NOT_EVALUATED", None)
    over_cap = [c["name"] for c in calls if c.get("within_per_call_cap") is False]
    setr("SCHED_CALLS", "NOT_MET" if (len(calls) > 6 or over_cap or len(set(names)) != len(names)) else "MET",
         {"calls": len(calls), "over_7200s": over_cap, "duplicate_names": len(set(names)) != len(names)})
    alloc_ok, alloc_detail = True, {}
    for call in calls:
        row = allocation_receipts.get(call["name"])
        if row is None:
            alloc_ok = False
            alloc_detail[call["name"]] = "no allocation_before_call receipt in mirror"
        else:
            alloc_detail[call["name"]] = row
            alloc_ok = alloc_ok and row.get("compliant") is True and row.get("remaining_ge_7320") is True
    setr("SCHED_PER_CALL", ("MET" if alloc_ok else "NOT_MET") if calls else "NOT_EVALUATED", alloc_detail)
    setr("SCHED_SEPARATE", "MET", "scheduler and scientific outcomes are separate fields")
    setr("REPORT_RULE", "MET", "outcome label + charged SU reported; this tool never launches anything")
    flags_false = bool(receipt) and all(receipt.get(k) is False for k in
        ("production_accepted", "every_step_pa_validated", "terminal_fresh_acceptance_validated")) and \
        spec.get("production_accepted") is False
    setr("NO_PRODUCTION", "MET" if flags_false else ("NOT_EVALUATED" if not receipt else "NOT_MET"),
         {k: (receipt or {}).get(k) for k in ("production_accepted", "every_step_pa_validated",
                                              "terminal_fresh_acceptance_validated")})
    setr("LATER_GATES", "INFORMATIONAL", "unchanged by any outcome")

    # --- sequence / branch -----------------------------------------------------------------
    decision = (receipt or {}).get("pre_resume_decision") or {}
    action = decision.get("action")
    seq_result, expected_sequence = sequence_result(names, spec_negative, status, action)
    setr("SEQUENCE", seq_result,
         {"observed": names, "registered_for_branch": expected_sequence, "branch_action": action})
    d = (rederived or {}).get("derived", {})
    drop = d.get("warm_minus_fresh_meV", decision.get("warm_minus_fresh_meV"))
    implied = d.get("implied_action")
    branch_ok = None if implied is None or action is None else implied == action
    def branch(target):
        if action is None:
            return "NOT_EVALUATED"
        if action != target:
            return "NOT_APPLICABLE"
        return "NOT_MET" if branch_ok is False else "MET"
    branch_evidence = {"controller_action": action, "recomputed_action": implied, "warm_minus_fresh_meV": drop}
    setr("BRANCH_RESUME", branch("RESUME_CANDIDATE"), branch_evidence)
    setr("BRANCH_RESEED", branch("RESEED_CANDIDATE"), branch_evidence)
    fresh_call = next((c for c in calls if c["name"] == "fresh"), None)
    setr("BRANCH_HOLD", "TRIGGERED" if (status == "HOLD" or action == "HOLD") else "NOT_TRIGGERED",
         {"fresh_status": None if fresh_call is None else fresh_call["status"],
          "fresh_failure": (receipt or {}).get("fresh_failure")})

    # --- per-call contract criteria --------------------------------------------------------
    bad = [c for c in calls if c["status"] != "NUMERICAL_RECEIPT_VALIDATED"]
    setr("SUPERVISION", "MET" if calls and not any(c["failure_class"] in ("PROCESS_CONTRACT", "NOT_FINISHED")
                                                  for c in calls) else ("NOT_EVALUATED" if not calls else "NOT_MET"),
         {c["name"]: c["process_flags"] for c in calls})
    boundary_ok, boundary_detail = True, {}
    for call in calls:
        reg = REGISTERED.get(call["name"])
        raw = call["raw"]
        scf = raw.get("stdout", {}).get("scf_cycles")
        steps = raw.get("xml", {}).get("steps")
        xml_status = raw.get("xml", {}).get("exit_status")
        if reg is None or call["status"] != "NUMERICAL_RECEIPT_VALIDATED":
            continue
        want_status = 0 if reg["exit"] == "normal_scf" else 255
        ok = (scf == reg["expected_cycles"] and steps is not None and len(steps) == reg["expected_steps"]
              and xml_status == want_status)
        boundary_detail[call["name"]] = {"scf_cycles": scf, "xml_steps": None if steps is None else len(steps),
                                         "xml_exit_status": xml_status, "registered_cycles": reg["expected_cycles"]}
        boundary_ok = boundary_ok and ok
    setr("BOUNDARY_COUNTS", ("MET" if boundary_ok else "NOT_MET") if boundary_detail else "NOT_EVALUATED", boundary_detail)
    thr = {c["name"]: c["raw"].get("stdout", {}).get("first_conv_thr_Ry") for c in calls
           if c["status"] == "NUMERICAL_RECEIPT_VALIDATED" and c["name"] in FIRST_THRESHOLD_KINDS}
    setr("FIRST_THRESHOLD", ("MET" if all(v == FIRST_THRESHOLD_RY for v in thr.values()) else "NOT_MET") if thr else "NOT_EVALUATED", thr)
    reject_hits = [c["name"] for c in calls if c["failure_class"] == "RAW_VALIDATION_REFUSED"]
    setr("REJECT_LIST", "NOT_MET" if reject_hits else ("MET" if calls else "NOT_EVALUATED"), {"refused_calls": reject_hits})
    validated_names = {c["name"] for c in calls if c["status"] == "NUMERICAL_RECEIPT_VALIDATED"}
    headers = {c["name"]: c["raw"].get("header_binding", {}) for c in calls if c["name"] in validated_names}
    if rederived:
        arms = rederived["arms"]
        failed = {n: a["error"] for n, a in arms.items() if not a["ok"] and n in validated_names}
        failed.update({n + " post-check": a["post_checks"] for n, a in arms.items()
                       if a["ok"] and n in validated_names and not all(
                           v is True for k, v in a["post_checks"].items() if not k.endswith("_error"))})
        missing = sorted(validated_names - set(arms))
        setr("RAW_BINDING", "NOT_MET" if failed or missing else ("MET" if arms else "NOT_EVALUATED"),
             {"raw_rederivation_failures_on_validated_calls": failed, "validated_calls_not_rederived": missing,
              "arms_rederived_ok": [n for n, a in arms.items() if a["ok"]]})
    elif headers and all(h.get("checked") for h in headers.values()):
        setr("RAW_BINDING", "PARTIAL_HEADERS_ONLY" if all(h.get("ok") for h in headers.values()) else "NOT_MET",
             {"header_binding": headers, "note": "raw re-derivation not run; only MPI/thread/pool/ELPA headers bound"})
    else:
        setr("RAW_BINDING", "NOT_EVALUATED", "raw re-derivation not run")
    # --- negative / reseed / continuity -----------------------------------------------------
    neg = next((c for c in calls if c["name"] == "negative"), None)
    if neg is None:
        setr("NEG_CONTROL", "NOT_APPLICABLE" if not spec_negative or status != "PASS_ONE_BOUNDARY" else "NOT_MET",
             "negative control not executed")
    else:
        raw = neg["raw"].get("stdout", {})
        ok = neg["status"] == "NUMERICAL_RECEIPT_VALIDATED" and raw.get("startup_history_deleted") and raw.get("bfgs_counts", [None])[:1] == [0]
        setr("NEG_CONTROL", "MET" if ok else "NOT_MET",
             {"startup_deleted": raw.get("startup_history_deleted"), "first_bfgs_count": (raw.get("bfgs_counts") or [None])[0]})
    continuity = (receipt or {}).get("continuity")
    d_cont = d.get("continuity")
    cont_eval = d_cont or continuity
    if cont_eval is None:
        setr("CONTINUITY_TOL", "NOT_EVALUATED" if status != "PASS_ONE_BOUNDARY" else "NOT_MET", "no trajectory comparison available")
    else:
        setr("CONTINUITY_TOL", "MET" if cont_eval.get("within_tolerances") is True and cont_eval.get("evaluations") == 3 else "NOT_MET",
             {"max_abs_deltas": cont_eval.get("max_abs_deltas"), "evaluations": cont_eval.get("evaluations"),
              "source": "raw re-derivation" if d_cont else "controller receipt only"})
    binding = (receipt or {}).get("reseed_lower_state_binding")
    d_bind = d.get("reseed_binding")
    bind_eval = d_bind or binding
    if bind_eval is None:
        setr("RESEED_VALID", "NOT_APPLICABLE" if action != "RESEED_CANDIDATE" else "NOT_EVALUATED", None)
    else:
        setr("RESEED_VALID", "MET" if bind_eval.get("passed") is True else "NOT_MET",
             {k: bind_eval.get(k) for k in ("reseed_minus_fresh_abs_Ry", "warm_minus_reseed_meV", "matches_fresh_energy",
                                            "still_strictly_lower_than_warm", "reason")})
    setr("NO_SPLICE", "MET" if not ((receipt or {}).get("continuity") and (receipt or {}).get("reseed")) else "NOT_MET",
         {"genuine_lower_state_reseed_validated": (receipt or {}).get("genuine_lower_state_reseed_validated")})
    setr("INCONC_BOUNDARY", "TRIGGERED" if any(c["failure_class"] == "MISSED_BOUNDARY" for c in calls) else "NOT_TRIGGERED", None)
    setr("INCONC_PROCESS", "TRIGGERED" if any(c["failure_class"] in ("PROCESS_CONTRACT", "NOT_FINISHED") for c in calls)
         or (receipt or {}).get("scheduler_status") == "REFUSED" or sched.get("state") in
         ("TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "BOOT_FAIL", "PREEMPTED", "DEADLINE") else "NOT_TRIGGERED",
         {"scheduler_status": (receipt or {}).get("scheduler_status"), "slurm_state": sched.get("state")})
    setr("INCONC_RESEED", "TRIGGERED" if ((receipt or {}).get("reseed_branch_attempted") and
                                          (bind_eval or {}).get("passed") is not True) else "NOT_TRIGGERED", None)
    for cid in ("CTRL_STATUS_MAP", "CTRL_NEGATIVE_BLOCKS", "CTRL_EXIT_CODE", "CTRL_CALL_CONTRACT", "CTRL_AGGREGATE"):
        setr(cid, "INFORMATIONAL", "frozen controller behaviour used to read the receipt")

    # --- integrity cross-checks (receipt vs raw) ------------------------------------------
    for call in calls:
        raw = call["raw"]
        if call["status"] == "NUMERICAL_RECEIPT_VALIDATED":
            if raw.get("xml", {}).get("present") is not True:
                integrity.append("%s: validated in receipt but XML absent from mirror" % call["name"])
            else:
                xml_energies = [s["etot_Ry"] for s in raw["xml"]["steps"]]
                recv = call["receipt_energies_Ry"]
                if call["name"] == "fresh":
                    xml_energies = [raw["xml"].get("output_etot_Ry")]
                if recv and (len(recv) != len(xml_energies) or any(
                        a is None or b is None or a != b for a, b in zip(recv, xml_energies))):
                    integrity.append("%s: receipt energies differ from raw XML energies" % call["name"])
            if (raw.get("log_vs_xml_energy_max_abs_Ry") or 0.0) > LOG_XML_ENERGY_TOL_RY:
                integrity.append("%s: log vs XML energies differ by more than %g Ry" % (call["name"], LOG_XML_ENERGY_TOL_RY))
    if rederived:
        for call in calls:
            arm = rederived["arms"].get(call["name"])
            if arm and arm["ok"] and call["status"] == "NUMERICAL_RECEIPT_VALIDATED":
                again = [e["energy_Ry"] for e in arm["parsed"]["evaluations"]]
                if call["receipt_energies_Ry"] and again != call["receipt_energies_Ry"]:
                    integrity.append("%s: re-derived energies differ from receipt" % call["name"])
        if d.get("implied_action") and action and d["implied_action"] != action:
            integrity.append("recomputed fresh-vs-warm branch %s differs from controller action %s" % (d["implied_action"], action))
        if d.get("continuity") and continuity and d["continuity"].get("within_tolerances") != continuity.get("within_tolerances"):
            integrity.append("re-derived continuity verdict differs from controller receipt")
    if mirror_gaps:
        integrity.extend("mirror: " + g for g in mirror_gaps)

    outcome = classify(receipt=receipt, calls=calls, sched=sched, results=results, integrity=integrity,
                       rederived=rederived, status=status, action=action, slurm_log_text=slurm_log_text,
                       bad=bad, spec_negative=spec_negative, allocation_receipts=allocation_receipts)
    return results, outcome, integrity, notes


def classify(*, receipt, calls, sched, results, integrity, rederived, status, action, slurm_log_text, bad, spec_negative,
             allocation_receipts=None):
    out = {"label": None, "label_basis": None, "candidate_labels": [], "reasons": [], "open_questions": [],
           "criteria": [], "controller_scientific_status": status, "corroboration": None,
           "pass_gates": None}
    def done(label, basis, reasons, criteria, questions=(), candidates=()):
        out.update(label=label, label_basis=basis, reasons=list(reasons), criteria=list(criteria),
                   open_questions=list(questions), candidate_labels=list(candidates))
        return out
    if not sched.get("found") or not sched.get("terminal"):
        return done("NOT_READY", None, ["scheduler state %s is not terminal / no sacct record" % sched.get("state")], ["REPORT_RULE"])
    if receipt is None:
        text = slurm_log_text or ""
        if re.search(r"REFUSE:|\"scientific_status\":\s*\"INCONCLUSIVE\"", text) and not calls:
            return done("INCONCLUSIVE", "FROZEN_CONTROLLER_RECORD_ONLY",
                        ["controller refused before any QE call (Slurm log carries a REFUSE/INCONCLUSIVE line); no scientific evidence"],
                        ["CTRL_EXIT_CODE", "INCONC_PROCESS"], ["OQ8"])
        return done("EVIDENCE_GAP", None, ["trial_results/trial_receipt.json is absent from the mirror and the Slurm log "
                                           "shows no refusal; re-mirror before classifying"], ["REPORT_RULE"])
    failing = [c for c in bad]
    if failing:
        classes = sorted({c["failure_class"] for c in failing})
        crit = [FAILURE_CLASS_CRITERIA[k][0] for k in classes]
        basis = "PRESTATED" if all(FAILURE_CLASS_CRITERIA[k][1] == "PRESTATED" for k in classes) else "FROZEN_CONTROLLER_RECORD_ONLY"
        reasons = ["call %s: status %s, class %s%s" % (c["name"], c["status"], c["failure_class"],
                                                      (" (" + c["error"] + ")") if c.get("error") else "") for c in failing]
        qs = []
        if "RAW_VALIDATION_REFUSED" in classes:
            qs.append("OQ8")
        if any(c["name"] == "negative" for c in failing) and not any(c["name"] != "negative" for c in failing):
            qs.append("OQ5")
        if receipt.get("scheduler_status") == "REFUSED":
            reasons.append("scheduler_status REFUSED: live allocation check failed before a call (resource problem)")
            crit.append("INCONC_PROCESS")
            reasons += ["%s: %s" % (k, v.get("error")) for k, v in (allocation_receipts or {}).items()
                        if k.startswith("unstarted_call") and not v.get("compliant")]
        return done("INCONCLUSIVE", basis, reasons, crit + ["CTRL_STATUS_MAP"], qs)
    error = receipt.get("error") or ""
    if receipt.get("scheduler_status") == "REFUSED":
        return done("INCONCLUSIVE", "PRESTATED", ["scheduler_status REFUSED (resource problem)"]
                    + ["%s: %s" % (k, v.get("error")) for k, v in (allocation_receipts or {}).items()
                       if k.startswith("unstarted_call") and not v.get("compliant")], ["INCONC_PROCESS"])
    if status == "PASS_ONE_BOUNDARY":
        required = {"all_calls_validated": all(c["status"] == "NUMERICAL_RECEIPT_VALIDATED" for c in calls) and bool(calls),
                    "registered_sequence": results["SEQUENCE"]["result"] == "MET",
                    "resource_caps": results["SCHED_ALLOC"]["result"] == "MET" and results["SCHED_CAP_SU"]["result"] == "MET"
                                     and results["SCHED_CALLS"]["result"] == "MET",
                    "per_call_allocation_receipts": results["SCHED_PER_CALL"]["result"] == "MET",
                    "boundary_counts": results["BOUNDARY_COUNTS"]["result"] == "MET",
                    "raw_binding": results["RAW_BINDING"]["result"] in ("MET", "PARTIAL_HEADERS_ONLY", "NOT_EVALUATED"),
                    "first_threshold": results["FIRST_THRESHOLD"]["result"] == "MET",
                    "continuity_within_tolerances": results["CONTINUITY_TOL"]["result"] == "MET",
                    "negative_control": results["NEG_CONTROL"]["result"] in ("MET", "NOT_APPLICABLE"),
                    "production_flags_false": results["NO_PRODUCTION"]["result"] == "MET",
                    "no_integrity_flags": not integrity}
        out["pass_gates"] = required
        out["corroboration"] = "RAW_REDERIVED" if rederived and results["RAW_BINDING"]["result"] == "MET" else "RECEIPT_ONLY"
        if all(required.values()):
            return done("PASS", "PRESTATED", ["controller PASS_ONE_BOUNDARY corroborated by every listed gate"],
                        ["SEQUENCE", "BRANCH_RESUME", "CONTINUITY_TOL", "BOUNDARY_COUNTS", "NEG_CONTROL", "SCHED_ALLOC",
                         "SCHED_CAP_SU", "NO_PRODUCTION", "CTRL_STATUS_MAP"])
        miss = [k for k, v in required.items() if not v]
        return done("UNMAPPED", None, ["controller says PASS_ONE_BOUNDARY but these gates do not corroborate it: " + ", ".join(miss)]
                    + integrity, ["CTRL_STATUS_MAP"], [], ["PASS", "INCONCLUSIVE"])
    if status == "RESEED_BRANCH_ONLY":
        return done("RESEED_BRANCH_ONLY", "FROZEN_CONTROLLER_RECORD_ONLY",
                    ["controller recorded RESEED_BRANCH_ONLY: reseed first energy bound to the lower fresh state; continuity not validated"],
                    ["BRANCH_RESEED", "RESEED_VALID", "NO_SPLICE"], ["OQ4"], ["PASS (reseed branch only)"])
    if status == "HOLD":
        why = (receipt.get("pre_resume_decision") or {}).get("reason") or receipt.get("fresh_failure") or "no reason recorded"
        return done("UNMAPPED", None, ["controller HOLD without a call-level process failure: " + str(why)],
                    ["BRANCH_HOLD", "CTRL_STATUS_MAP"], ["OQ3"], ["INCONCLUSIVE"])
    if status == "INCONCLUSIVE" and not calls:
        return done("INCONCLUSIVE", "FROZEN_CONTROLLER_RECORD_ONLY",
                    ["controller recorded INCONCLUSIVE before any QE call (refusal ahead of the first call): " + (error or "no error text")],
                    ["REJECT_LIST", "CTRL_STATUS_MAP"], ["OQ8"])
    if status == "INCONCLUSIVE":
        if receipt.get("reseed_branch_attempted") and (results["RESEED_VALID"]["result"] == "NOT_MET"):
            return done("INCONCLUSIVE", "PRESTATED", ["reseed attempted; first evaluated energy did not bind to the lower fresh state / strict drop"],
                        ["INCONC_RESEED", "RESEED_VALID"])
        if any(s in error for s in ERR_AGGREGATE):
            return done("INCONCLUSIVE", "PRESTATED", [error], ["INCONC_PROCESS", "CTRL_AGGREGATE"])
        if any(s in error for s in ERR_INTEGRITY):
            return done("UNMAPPED", None, ["post-validation integrity stop: " + error], ["REJECT_LIST", "CTRL_STATUS_MAP"], [], ["INCONCLUSIVE"])
        continuity = receipt.get("continuity")
        resumed_ok = any(c["name"] == "resumed" and c["status"] == "NUMERICAL_RECEIPT_VALIDATED" for c in calls)
        if results["CONTINUITY_TOL"]["result"] == "NOT_MET" and (continuity is not None or resumed_ok):
            return done("UNMAPPED", None, ["all executed calls validated; control vs candidate+resumed not within the registered tolerances: "
                                           + json.dumps((continuity or {}).get("max_abs_deltas"))],
                        ["CONTINUITY_TOL", "CTRL_STATUS_MAP"], ["OQ1"], ["FAIL", "INCONCLUSIVE"])
        if resumed_ok and continuity is None:
            return done("UNMAPPED", None, ["resumed call validated but the continuation audit/continuity step did not complete: " + error],
                        ["CONTINUITY_TOL", "CTRL_STATUS_MAP"], ["OQ2"], ["FAIL", "INCONCLUSIVE"])
        return done("UNMAPPED", None, ["controller INCONCLUSIVE with all calls validated and no registered cause: " + error],
                    ["CTRL_STATUS_MAP"], [], ["INCONCLUSIVE"])
    return done("UNMAPPED", None, ["unrecognised controller scientific_status %r" % status], ["CTRL_STATUS_MAP"])


# ----------------------------------------------------------------------------------------
# Top-level analysis
# ----------------------------------------------------------------------------------------
def _allocation_receipts(trial_dir, calls, trial, job_id, spec):
    out = {}
    for index, call in enumerate(calls, 1):
        data, error = _load_json(Path(trial_dir) / ("allocation_before_call_%02d.json" % index))
        if data is None:
            continue
        row = {"observed_utc": data.get("observed_utc")}
        try:
            verified = trial.validate_allocation(data.get("stdout", ""), job_id, memory_gib=spec["allocation"]["memory_gib"])
            row.update(compliant=True, runtime_seconds=verified["runtime_seconds"],
                       remaining_seconds=verified["remaining_seconds"],
                       remaining_ge_7320=verified["remaining_seconds"] >= trial.CAPS["per_call_seconds"] + trial.CAPS["cleanup_seconds"],
                       node=verified["fields"].get("NodeList"))
        except Exception as exc:
            row.update(compliant=False, error=str(exc), remaining_ge_7320=False)
        out[call["name"]] = row
    # A refusal ahead of a call leaves a receipt for a call that never started; keep its reason.
    for path in sorted(Path(trial_dir).glob("allocation_before_call_*.json")):
        index = _int(path.stem.rsplit("_", 1)[-1])
        if index is not None and index > len(calls):
            data, _ = _load_json(path)
            try:
                trial.validate_allocation((data or {}).get("stdout", ""), job_id, memory_gib=spec["allocation"]["memory_gib"])
                out["unstarted_call_%02d" % index] = {"compliant": True, "note": "receipt without a call entry"}
            except Exception as exc:
                out["unstarted_call_%02d" % index] = {"compliant": False, "error": str(exc)}
    return out


def analyze(*, mirror, job_id=JOB_ID, sacct_text=None, scontrol_text=None, jobsu_text=None,
            remote_inventory=None, repo=DEFAULT_REPO, rederive=True, spec_path=None,
            source_deck=None, balance_before=None, hash_mirror=True):
    repo = Path(repo)
    trial, adapter = load_modules(repo)
    spec_path = Path(spec_path) if spec_path else repo / SPEC_REL
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    located = locate_mirror(mirror, job_id)
    trial_dir = located["trial_dir"]
    sched = assess_scheduler(parse_sacct(sacct_text, job_id), spec, scontrol=scontrol_text,
                             jobsu=parse_jobsu(jobsu_text) if jobsu_text else None)
    if balance_before is not None and sched.get("charged_cpu_su") is not None:
        sched["balance_before_su"] = balance_before
        sched["balance_after_su_exact_product"] = balance_before - sched["charged_cpu_su"]
    verdict = {"schema": SCHEMA, "job_id": job_id, "readonly": True, "qe_executed": False,
               "network_or_ssh_used": False, "production_accepted": False,
               "spec_sha256": sha256_file(spec_path), "mirror_root": str(located["root"]),
               "trial_dir_found": trial_dir is not None, "scheduler": sched}
    mirror_gaps, receipt, calls = [], None, []
    if trial_dir is not None:
        receipt, error = _load_json(Path(trial_dir) / "trial_receipt.json")
        if error and error != "absent":
            mirror_gaps.append("trial_receipt.json " + error)
        calls = build_call_rows(trial_dir, receipt, trial, adapter) if receipt else []
        for call in calls:
            if call["status"] == "NUMERICAL_RECEIPT_VALIDATED":
                paths = arm_paths(trial_dir, call["name"])
                for key in ("input", "stdout", "stderr", "process_receipt", "setup_receipt", "parsed_receipt", "xml"):
                    if not Path(paths[key]).is_file():
                        mirror_gaps.append("%s: %s missing (%s)" % (call["name"], key, Path(paths[key]).name))
        orphans = [a for a in ARM_ORDER if (Path(trial_dir) / a).is_dir() and a not in [c["name"] for c in calls]]
        if orphans and receipt:
            mirror_gaps.append("arm directories without a receipt call entry: " + ", ".join(orphans))
    verdict["mirror"] = {"trial_dir": None if trial_dir is None else str(trial_dir),
                         "slurm_log": None if located["slurm_log"] is None else str(located["slurm_log"]),
                         "required_gaps": mirror_gaps}
    if hash_mirror and located["root"].is_dir():
        local = inventory_dir(located["root"])
        verdict["mirror"]["local_inventory_files"] = len(local)
        verdict["mirror"]["local_inventory_sha256_of_rows"] = hashlib.sha256(
            json.dumps(local, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        verdict["mirror"]["local_inventory"] = local
        if remote_inventory is not None:
            cmp_ = compare_inventories(local, normalize_remote_inventory(remote_inventory))
            verdict["mirror"]["remote_inventory_comparison"] = cmp_
            if cmp_["mismatched"]:
                mirror_gaps.append("hash/size mismatch against remote inventory: " + ", ".join(cmp_["mismatched"][:5]))
    log_text = _read_text(located["slurm_log"]) if located["slurm_log"] else None
    verdict["slurm_log_tail"] = None if log_text is None else log_text[-1500:]
    rederived = None
    if rederive and trial_dir is not None and receipt:
        deck = Path(source_deck) if source_deck else repo / SOURCE_DECK_REL
        try:
            rederived = rederive_trial(trial_dir, receipt, repo=repo, spec=spec, source_deck=deck,
                                       trial=trial, adapter=adapter)
        except Exception as exc:
            rederived = None
            verdict["rederivation_error"] = "%s: %s" % (type(exc).__name__, exc)
    allocation = _allocation_receipts(trial_dir, calls, trial, job_id, spec) if trial_dir is not None else {}
    results, outcome, integrity, notes = evaluate(
        receipt=receipt, calls=calls, sched=sched, spec=spec, trial_dir=trial_dir, slurm_log_text=log_text,
        mirror_gaps=mirror_gaps, rederived=rederived, allocation_receipts=allocation, repo=repo)
    verdict.update({
        "controller": None if receipt is None else {k: receipt.get(k) for k in (
            "scientific_status", "scheduler_status", "call_count", "elapsed_seconds", "error", "fresh_failure",
            "production_accepted", "every_step_pa_validated", "terminal_fresh_acceptance_validated",
            "genuine_lower_state_reseed_validated", "continuity_validated", "reseed_branch_status")},
        "calls": calls, "allocation_receipts": allocation,
        "pre_resume_decision": None if receipt is None else receipt.get("pre_resume_decision"),
        "reseed_binding_receipt": None if receipt is None else receipt.get("reseed_lower_state_binding"),
        "continuity_receipt": None if receipt is None else receipt.get("continuity"),
        "rederivation": None if rederived is None else {
            "arms": {n: {"ok": a["ok"], "error": a["error"], "post_checks": a.get("post_checks")}
                     for n, a in rederived["arms"].items()},
            "derived": rederived["derived"]},
        "criteria_results": results, "integrity_flags": integrity, "outcome": outcome,
        "open_questions_text": {k: OPEN_QUESTIONS[k] for k in outcome["open_questions"]},
        "criteria_registry_ref": "see criteria[] below",
    })
    verdict["criteria"] = [dict(CRITERIA[cid], result=results.get(cid, {}).get("result"),
                                evidence=results.get(cid, {}).get("evidence")) for cid in CRITERIA]
    verdict["citation_check"] = [r for r in check_citations(repo) if r["status"] != "EXACT"]
    return verdict


# ----------------------------------------------------------------------------------------
# Markdown
# ----------------------------------------------------------------------------------------
def _md(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def _table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(_md("" if v is None else v) for v in row) + " |" for row in rows]
    return "\n".join(lines)


def _fmt(value, digits=10):
    if isinstance(value, float):
        return ("%." + str(digits) + "g") % value
    return value


def render_markdown(verdict):
    o, s = verdict["outcome"], verdict["scheduler"]
    out = ["# Catalyst P-A boundary trial readout, job %s" % verdict["job_id"], ""]
    headline = "**TRIAL OUTCOME: %s**" % o["label"]
    if o.get("corroboration"):
        headline += " (%s)" % o["corroboration"]
    out += [headline, ""]
    legend = {"UNMAPPED": "UNMAPPED means the registered criteria assign no PASS / FAIL / INCONCLUSIVE label to what was observed.",
              "RESEED_BRANCH_ONLY": "RESEED_BRANCH_ONLY is reported separately from a continuity pass (DOC:36-37, DOC:49-50).",
              "NOT_READY": "NOT_READY means the scheduler record is missing or not terminal; nothing is classified yet.",
              "EVIDENCE_GAP": "EVIDENCE_GAP means required files are missing from the mirror; re-mirror before classifying."}.get(o["label"])
    if legend:
        out += [legend, ""]
    if o["label"] == "NOT_READY":
        out += ["Controller receipt status `%s` is the controller's initial placeholder until it finishes "
                "(pa_catalyst_trial.py:682); it is not a result. The tables below are an interim view." % o.get("controller_scientific_status")]
    else:
        out += ["Controller scientific_status: `%s`. Label basis: `%s`." % (o.get("controller_scientific_status"), o.get("label_basis") or "n/a")]
    if o["candidate_labels"]:
        out.append("Candidate labels the registered criteria do not choose between: %s." % ", ".join(o["candidate_labels"]))
    for reason in o["reasons"]:
        out.append("- " + _md(reason))
    if o["open_questions"]:
        out += ["", "Open questions for Frank (the registered criteria are silent or ambiguous):"]
        out += ["- **%s** %s" % (q, OPEN_QUESTIONS[q]) for q in o["open_questions"]]
    out += ["", "No production, every-step P-A, S8 ranking or melt release follows from any outcome; "
            "no automatic rerun (DOC:9-11, DOC:107).", "", "## Scheduler and SU", ""]
    rec = s["record"]
    su_rows = [["state", rec.get("state_raw") or s.get("state")], ["exit", "%s:%s" % (rec.get("exit_code"), rec.get("exit_signal"))],
               ["elapsed_s", rec.get("elapsed_s")], ["AllocCPUS", rec.get("alloc_cpus")],
               ["AllocTRES", json.dumps(rec.get("alloc_tres"), sort_keys=True)],
               ["charged CPU SU (ElapsedRaw x billing / 3600)", _fmt(s.get("charged_cpu_su"), 8)],
               ["CPUTimeRAW / 3600", _fmt(s.get("cputimeraw_su"), 8)],
               ["jobsu reported", s.get("jobsu_reported_su")], ["jobsu minus computed", _fmt(s.get("jobsu_minus_computed_su"), 6)],
               ["cap (CPU SU)", s.get("cap_su")], ["Slurm exit vs controller", s.get("slurm_exit_vs_controller")]]
    controller = verdict.get("controller") or {}
    su_rows.append(["controller elapsed_seconds / sum of per-call process seconds",
                    "%s / %s" % (_fmt(controller.get("elapsed_seconds"), 8),
                                 _fmt(sum(c.get("elapsed_seconds") or 0 for c in verdict["calls"]), 8))])
    if "balance_before_su" in s:
        su_rows.append(["balance before / after (exact product)", "%s / %s" % (s["balance_before_su"], _fmt(s["balance_after_su_exact_product"], 8))])
    out += [_table(["quantity", "value"], su_rows), "", "Resource checks: " +
            ", ".join("%s=%s" % (c["id"], "ok" if c["ok"] else "FAIL(%s)" % c["observed"]) for c in s.get("checks", [])), ""]
    out += ["## Per-call table", ""]
    rows = []
    for c in verdict["calls"]:
        raw = c["raw"].get("stdout", {})
        xml = c["raw"].get("xml", {})
        steps = xml.get("steps") or []
        conv = "%s/%s XML steps converged" % (sum(1 for x in steps if x["converged"]), len(steps)) if steps else (
            "XML absent" if not xml.get("present") else "no steps")
        energies = ", ".join(_fmt(x["etot_Ry"], 12) for x in steps if x["etot_Ry"] is not None) or (
            _fmt(xml.get("output_etot_Ry"), 12) if xml.get("output_etot_Ry") is not None else "")
        hb = c["raw"].get("header_binding", {})
        header = ("MPI%s/thr%s/npool%s/%s%s" % (hb.get("nprocs"), hb.get("nthreads"), hb.get("npool"), hb.get("diagonalization"),
                                                  hb.get("elpa_subgroup") or "") if hb.get("ok") else
                  ("FAIL: " + str(hb.get("error"))[:60] if hb.get("checked") else "n/a"))
        rows.append([c["index"], c["name"], c["status"], c.get("failure_class") or "", c.get("stop_reason") or "",
                     c.get("returncode"), _fmt(c.get("elapsed_seconds"), 6), c.get("within_per_call_cap"),
                     conv, "ok %s / NOT %s / max it %s" % (raw.get("scf_converged_count"), raw.get("scf_not_converged_count"), raw.get("max_scf_iteration_seen")),
                     "%s vs reg %s" % (raw.get("scf_cycles"), c.get("registered_expected_cycles")),
                     xml.get("exit_status"), raw.get("wall_seconds"), energies, header, c.get("error") or ""])
    out += [_table(["#", "call", "controller status", "failure class", "stop reason", "rc", "process s", "<=7200 s",
                    "SCF (XML)", "SCF (log)", "SCF cycles", "XML exit", "PWSCF WALL s", "energies Ry (XML x2)",
                    "raw header", "error"], rows), ""]
    dec = verdict.get("pre_resume_decision") or {}
    der = (verdict.get("rederivation") or {}).get("derived", {})
    out += ["## Decisions and comparisons", ""]
    cont = der.get("continuity") or verdict.get("continuity_receipt") or {}
    drows = [["fresh decision (controller)", dec.get("action"), dec.get("reason")],
             ["warm - fresh (meV/cell)", _fmt(der.get("warm_minus_fresh_meV", dec.get("warm_minus_fresh_meV")), 8), "strict >10 meV lower triggers reseed (DOC:36-38)"],
             ["recomputed action", der.get("implied_action"), "same expression as pa_qe_adapter.py:1213"],
             ["continuity max |dE| Ry / |dx| bohr / |dF| Ry/bohr",
              json.dumps(cont.get("max_abs_deltas")), "tolerances 1e-6 / 1e-5 / 1e-5 (DOC:46-47); within=%s" % cont.get("within_tolerances")],
             ["reseed binding", json.dumps({k: (verdict.get("reseed_binding_receipt") or der.get("reseed_binding") or {}).get(k)
                                           for k in ("passed", "reseed_minus_fresh_abs_Ry", "warm_minus_reseed_meV")}), "DOC:41-43"],
             ["resumed observed", json.dumps(der.get("resumed_observed")), "first optimizer count must equal saved count 1; first SCF cycle 2"]]
    out += [_table(["item", "value", "note"], drows), ""]
    out += ["## Criteria (each with file:line and verbatim quote)", ""]
    crit_rows = []
    for c in verdict["criteria"]:
        cites = "<br>".join("%s:%s \"%s\"" % (x["file"], x["line"], x["quote"]) for x in c["cites"])
        crit_rows.append([c["id"], c["kind"], c["text"], c.get("result"), cites])
    out += [_table(["id", "kind", "criterion", "result", "citations"], crit_rows), ""]
    if verdict["integrity_flags"]:
        out += ["## Integrity flags", ""] + ["- " + _md(f) for f in verdict["integrity_flags"]] + [""]
    mir = verdict["mirror"]
    out += ["## Mirror", "", "- trial_results: `%s`; Slurm log: `%s`" % (mir.get("trial_dir"), mir.get("slurm_log")),
            "- files hashed: %s; remote inventory comparison: %s" % (mir.get("local_inventory_files"), json.dumps(mir.get("remote_inventory_comparison"))),
            "- required-file gaps: %s" % (mir.get("required_gaps") or "none")]
    if verdict["citation_check"]:
        out += ["", "## Citation drift", ""] + ["- %s %s:%s -> %s" % (r["status"], r["file"], r["line"], r.get("line_now")) for r in verdict["citation_check"]]
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mirror", type=Path, help="local mirror of the remote trial parent (contains trial_results/)")
    parser.add_argument("--sacct", type=Path, help="saved `sacct -n -P -j JOB --format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,ReqMem,AllocTRES,CPUTimeRAW` text")
    parser.add_argument("--observations", type=Path, help="alternative: watcher trial_observations.jsonl (last accounting row is used)")
    parser.add_argument("--scontrol", type=Path, help="saved `scontrol show job JOB -o` text")
    parser.add_argument("--jobsu", type=Path, help="saved `jobsu -j JOB` text")
    parser.add_argument("--remote-inventory", type=Path, help="JSON list/{files:[{path,size,sha256}]} from the remote side")
    parser.add_argument("--job-id", default=JOB_ID)
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--balance-before", type=float)
    parser.add_argument("--spec", type=Path, help="launch spec JSON (default: the pinned results/pa_catalyst_trial_2026-10-03/launch_spec.json)")
    parser.add_argument("--source-deck", type=Path, help="local copy of the registered 72-atom source deck (default: the repo copy)")
    parser.add_argument("--no-rederive", action="store_true", help="skip raw re-derivation through the frozen adapter")
    parser.add_argument("--out", type=Path, help="new directory for readout_verdict.json and readout_table.md (must not exist)")
    parser.add_argument("--print-mirror-selection", action="store_true", help="print the lightweight remote paths this readout needs, then exit")
    parser.add_argument("--check-citations", action="store_true", help="re-resolve every cited quote, then exit")
    args = parser.parse_args(argv)
    if args.print_mirror_selection:
        print(json.dumps(mirror_selection(args.job_id), indent=1))
        return 0
    if args.check_citations:
        rows = check_citations(args.repo)
        print(json.dumps([r for r in rows if r["status"] != "EXACT"], indent=1))
        return 0 if all(r["status"] == "EXACT" for r in rows) else 1
    if args.mirror is None:
        parser.error("--mirror is required")
    sacct_text = args.sacct.read_text(encoding="utf-8") if args.sacct else None
    if sacct_text is None and args.observations:
        last = None
        for line in args.observations.read_text(encoding="utf-8").splitlines():
            if line.strip():
                last = line
        if last:
            try:
                sacct_text = json.loads(json.loads(last)["stdout"])["commands"]["accounting"]["stdout"]
            except (KeyError, ValueError, TypeError):
                sacct_text = None
    verdict = analyze(
        mirror=args.mirror, job_id=args.job_id, sacct_text=sacct_text,
        scontrol_text=args.scontrol.read_text(encoding="utf-8") if args.scontrol else None,
        jobsu_text=args.jobsu.read_text(encoding="utf-8") if args.jobsu else None,
        remote_inventory=json.loads(args.remote_inventory.read_text(encoding="utf-8")) if args.remote_inventory else None,
        repo=args.repo, rederive=not args.no_rederive, balance_before=args.balance_before,
        spec_path=args.spec, source_deck=args.source_deck)
    markdown = render_markdown(verdict)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
        (args.out / "readout_verdict.json").write_text(json.dumps(verdict, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
        (args.out / "readout_table.md").write_text(markdown, encoding="utf-8")
    sys.stdout.write(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
