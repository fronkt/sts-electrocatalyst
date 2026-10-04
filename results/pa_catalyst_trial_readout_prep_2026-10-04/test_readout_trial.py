"""Offline tests for readout_trial.py.  Never launches QE, Slurm or any network call.

Real data: the retained tiny H2 raw outputs (job 21024848) exercise the raw
summaries, the adapter re-derivation, the mirror inventory and the scheduler/SU
parsers.  Catalyst-layout scenarios are built by running the real frozen
Trial.run() state machine with process doubles (no QE), so the receipts have the
controller's own keys, then writing raw files that agree with them.
"""
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import types
from pathlib import Path
from unittest.mock import Mock

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src/dft"))
sys.dont_write_bytecode = True
import readout_trial as R  # noqa: E402
import pa_catalyst_trial as trial  # noqa: E402
import pa_qe_adapter as adapter  # noqa: E402

PHASE = REPO / "results/s2_2026-09-25/full_text/sequential_2026-10-03"
TINY_ROOT = PHASE / "pa_tiny_raw"
TINY = TINY_ROOT / "tiny_results"
SPEC = json.loads((REPO / R.SPEC_REL).read_text(encoding="utf-8"))
JOB = "21034683"
needs_tiny = pytest.mark.skipif(not TINY.is_dir(), reason="retained tiny raw outputs absent")


# ======================================================================================
# Citations, pinned tables, drift tests against the frozen sources
# ======================================================================================
def test_every_citation_resolves_exactly_in_the_pinned_files():
    rows = R.check_citations(REPO)
    assert rows and all(r["status"] == "EXACT" for r in rows), [r for r in rows if r["status"] != "EXACT"]
    assert all(c["cites"] for c in R.CRITERIA.values())
    assert all(c["kind"] in (R.KIND_STATED, R.KIND_FROZEN) for c in R.CRITERIA.values())


def test_citation_drift_is_reported_not_hidden(tmp_path):
    (tmp_path / "doc.md").write_text("alpha\nbeta quote here\n", encoding="utf-8")
    crit = {"X": {"id": "X", "kind": R.KIND_STATED, "text": "t",
                  "cites": [{"file": "doc.md", "line": 1, "quote": "beta quote"},
                            {"file": "doc.md", "line": 2, "quote": "beta quote"},
                            {"file": "doc.md", "line": 2, "quote": "absent words"},
                            {"file": "nope.md", "line": 1, "quote": "x"}]}}
    statuses = [r["status"] for r in R.check_citations(tmp_path, crit)]
    assert statuses == ["MOVED", "EXACT", "QUOTE_NOT_FOUND", "FILE_MISSING"]


def _watcher():
    spec = importlib.util.spec_from_file_location("watch_module_for_test",
                                                  REPO / "results/pa_catalyst_trial_2026-10-03/watch_trial_readonly.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_terminal_states_and_state_parser_match_the_watcher():
    watcher = _watcher()
    assert R.TERMINAL_STATES == frozenset(watcher.TERMINAL)
    assert "--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,ReqMem,AllocTRES,CPUTimeRAW" in \
        (REPO / "results/pa_catalyst_trial_2026-10-03/watch_trial_readonly.py").read_text(encoding="utf-8")
    text = "21034683|CANCELLED by 8320357|0:15|10|128|200G|billing=128,cpu=128,mem=200G,node=1|1280\n"
    assert watcher.scheduler_state(text, JOB) == R.parse_sacct(text, JOB)["state"] == "CANCELLED"
    pending = "21034683|PENDING|0:0|0|0|200G||0\n"
    assert watcher.scheduler_state(pending, JOB) == R.parse_sacct(pending, JOB)["state"] == "PENDING"


def test_registered_call_table_matches_controller_source():
    lines = (REPO / R.CTRL).read_text(encoding="utf-8").splitlines()
    for name, reg in R.REGISTERED.items():
        window = " ".join(lines[reg["site"] - 1:reg["site"] + 1])
        assert 'self.execute("%s", kind="%s"' % (name, reg["kind"]) in window, name
        assert "expected_cycles=%s" % reg["expected_cycles"] in window, name
        assert "expected_steps=%d" % reg["expected_steps"] in window, name
    assert R.PREFIX == trial.PREFIX
    assert R.LOG_XML_ENERGY_TOL_RY == 5.1e-8
    assert "5.1e-8" in (REPO / R.ADP).read_text(encoding="utf-8").splitlines()[844]


def test_pre_stated_numbers_are_read_from_frozen_modules_not_redefined():
    # The readout defines no threshold: caps come from the pinned spec/controller, the continuity
    # tolerances and the 10 meV drop from the frozen adapter.  Only two numeric constants exist in
    # the tool's code, each cited: the adapter's log-vs-XML bound and the registered 1e-6 Ry target.
    import ast
    assert SPEC["caps"] == trial.CAPS and SPEC["allocation"]["max_cpu_su"] == 2048
    assert adapter.TOLERANCES == {"energy_Ry": 1e-6, "position_bohr": 1e-5, "force_Ry_bohr": 1e-5}
    assert adapter.contract.DELTA_MEV == 10.0
    tree = ast.parse((HERE / "readout_trial.py").read_text(encoding="utf-8"))
    numbers = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
               and not isinstance(n.value, bool)}
    floats = {n for n in numbers if isinstance(n, float)}
    ints = {n for n in numbers if isinstance(n, int)}
    assert not (floats & {1e-5, 10.0, 13605.693, 1e-8}), floats
    assert not (ints & {2048, 57600, 7200, 7320, 7080, 128, 120, 16}), ints
    assert {n for n in numbers if isinstance(n, float) and 0 < abs(n) < 1e-3} == {5.1e-8, 1e-6}


# ======================================================================================
# Clock / scheduler / SU parsing (real tiny accounting + synthetic variants)
# ======================================================================================
@pytest.mark.parametrize("text,seconds", [
    ("9.88s", 9.88), ("12m24.64s", 744.64), ("1h 3m", 3780.0), ("0h 1m", 60.0), ("2d 3h 4m", 183840.0),
    ("1h 5m 2.5s", 3902.5)])
def test_qe_clock(text, seconds):
    assert R.parse_qe_clock(text) == pytest.approx(seconds)
    assert R.parse_qe_clock("none") is None


@needs_tiny
def test_real_tiny_accounting_su_and_jobsu():
    receipt = json.loads((PHASE / "pa_tiny_final_accounting.json").read_text(encoding="utf-8"))
    inner = json.loads(receipt["stdout"])
    sched = R.parse_sacct(inner["accounting"]["stdout"], "21024848")
    assert (sched["state"], sched["exit_code"], sched["exit_signal"], sched["terminal"]) == ("FAILED", 2, 0, True)
    assert sched["elapsed_s"] == 124 and sched["alloc_cpus"] == 4 and sched["cputime_raw_s"] == 496
    assert sched["alloc_tres"] == {"billing": "4", "cpu": "4", "mem": "6G", "node": "1"}
    assert [s["id"] for s in sched["steps"]] == ["21024848.batch", "21024848.extern"]
    assert R.charged_su(sched) == pytest.approx(124 * 4 / 3600)
    jobsu = R.parse_jobsu(inner["usage"]["stdout"])
    assert jobsu["cpu_su_job"] == 0.1376 and jobsu["cpu_su_total_all_jobs"] == 0.1376
    assert jobsu["gpu_su_total_all_jobs"] == 0.0 and jobsu["used_walltime"] == "00:02:04"
    # The tiny deck is not the catalyst allocation: only the arithmetic is asserted here.
    spec = copy.deepcopy(SPEC)
    spec["allocation"].update(cpus=4, billing=4, memory_gib=6, max_cpu_su=8)
    assessed = R.assess_scheduler(sched, spec, jobsu=jobsu)
    assert assessed["charged_cpu_su"] == pytest.approx(0.13777778)
    assert assessed["cputimeraw_su"] == pytest.approx(0.13777778)
    assert assessed["jobsu_minus_computed_su"] == pytest.approx(0.1376 - 124 * 4 / 3600)
    assert assessed["all_resource_checks_ok"] is True
    assert "refusal path" in assessed["slurm_exit_vs_controller"]


def test_sacct_header_form_and_extra_columns():
    text = ("JobIDRaw|State|ExitCode|ElapsedRaw|AllocCPUS|AllocTRES|MaxRSS\n"
            "21034683|COMPLETED|0:0|7200|128|billing=128,cpu=128,mem=200G,node=1|\n"
            "21034683.batch|COMPLETED|0:0|7200|128|cpu=128|1048576K\n")
    sched = R.parse_sacct(text, JOB)
    assert sched["found"] and sched["state"] == "COMPLETED" and sched["extra"] == {"MaxRSS": ""}
    assert R.charged_su(sched) == pytest.approx(7200 * 128 / 3600)
    assert not R.parse_sacct("", JOB)["found"]
    assert not R.parse_sacct("999|COMPLETED|0:0|1|1|1G||1\n", JOB)["found"]


def test_pending_record_is_not_terminal_and_not_charged():
    sched = R.parse_sacct("21034683|PENDING|0:0|0|0|200G||0\n", JOB)
    assessed = R.assess_scheduler(sched, SPEC)
    assert sched["terminal"] is False and assessed["charged_cpu_su"] == 0.0
    assert assessed["checks"][0]["id"] == "ran_at_all" and assessed["checks"][0]["ok"] is False


def test_scheduler_checks_against_the_pinned_allocation():
    good = R.parse_sacct("21034683|COMPLETED|0:0|3600|128|200G|billing=128,cpu=128,mem=200G,node=1|460800\n", JOB)
    a = R.assess_scheduler(good, SPEC, scontrol="Account=che260157 Partition=wholenode Requeue=0 Restarts=0 Dependency=(null) TimeLimit=16:00:00")
    assert a["all_resource_checks_ok"] is True and a["charged_cpu_su"] == 128.0
    assert a["slurm_exit_vs_controller"].startswith("controller PASS_ONE_BOUNDARY")
    for line in ("21034683|COMPLETED|0:0|3600|256|200G|billing=256,cpu=256,mem=200G,node=1|921600\n",
                 "21034683|COMPLETED|0:0|3600|128|201G|billing=128,cpu=128,mem=201G,node=1|460800\n",
                 "21034683|COMPLETED|0:0|3600|128|200G|billing=128,cpu=128,mem=200G,node=2|460800\n",
                 "21034683|COMPLETED|0:0|3600|128|200G|billing=128,cpu=128,mem=200G,node=1,gres/gpu=1|460800\n",
                 "21034683|TIMEOUT|0:0|57601|128|200G|billing=128,cpu=128,mem=200G,node=1|7372928\n"):
        assert R.assess_scheduler(R.parse_sacct(line, JOB), SPEC)["all_resource_checks_ok"] is False, line
    capped = R.assess_scheduler(R.parse_sacct("21034683|TIMEOUT|0:0|57600|128|200G|billing=128,cpu=128,mem=200G,node=1|7372800\n", JOB), SPEC)
    assert capped["charged_cpu_su"] == 2048.0 and capped["all_resource_checks_ok"] is True
    assert R.assess_scheduler(R.parse_sacct("21034683|FAILED|3:0|10|128|200G|billing=128,cpu=128,mem=200G,node=1|1280\n", JOB), SPEC)[
        "slurm_exit_vs_controller"].startswith("controller wrote a non-PASS")


# ======================================================================================
# Real tiny raw outputs: summaries, adapter re-derivation, mirror inventory
# ======================================================================================
@needs_tiny
def test_raw_summaries_on_the_four_real_tiny_arms():
    expected = {  # facts recorded in docs/research/pa-tiny-restart-readout-2026-10-03.md
        "continuous": dict(steps=8, status=0, first=0, deleted=False, stop=False),
        "candidate-stop": dict(steps=1, status=255, first=0, deleted=False, stop=True),
        "negative-fresh": dict(steps=5, status=0, first=0, deleted=True, stop=False),
        "resumed": dict(steps=7, status=0, first=1, deleted=False, stop=False)}
    for arm, want in expected.items():
        out = R.summarize_stdout((TINY / arm / "stdout.log").read_text(encoding="utf-8"), trial)
        xml = R.summarize_xml(TINY / arm / "scratch/h2_probe.save/data-file-schema.xml")
        assert out["qe_banners"] == ["7.5"] and out["job_done"] and not out["failure_markers"]
        assert out["scf_not_converged_count"] == 0 and out["scf_converged_count"] == want["steps"]
        assert len(xml["steps"]) == want["steps"] and all(s["converged"] for s in xml["steps"])
        assert xml["exit_status"] == want["status"] and xml["creator_version"] == "7.5"
        assert out["bfgs_counts"][0] == want["first"] and out["startup_history_deleted"] is want["deleted"]
        assert out["stopped_by_user"] is want["stop"]
        assert len(out["total_energies_Ry"]) == want["steps"]
        assert max(abs(a - b["etot_Ry"]) for a, b in zip(out["total_energies_Ry"], xml["steps"])) < R.LOG_XML_ENERGY_TOL_RY
        assert out["wall_seconds"] > 0
    cont = R.summarize_stdout((TINY / "continuous/stdout.log").read_text(encoding="utf-8"))
    assert cont["scf_cycles"] == [1, 2, 3, 4, 5, 6, 7] and cont["wall_seconds"] == pytest.approx(43.29)
    assert R.summarize_stdout(None) == {"present": False}
    assert R.summarize_xml(TINY / "absent.xml") == {"present": False}
    assert R.summarize_xml(TINY / "continuous/input.in")["parse_ok"] is False


def _tiny_candidate_paths(directory):
    return {"input": directory / "input.in", "stdout": directory / "stdout.log", "stderr": directory / "stderr.log",
            "xml": directory / "scratch/h2_probe.save/data-file-schema.xml", "process_receipt": directory / "receipt.json"}


def _tiny_expected():
    directory = TINY / "candidate-stop"
    expected = adapter.parse_deck(directory / "input.in")
    pseudo = directory / "H.pbe-rrkjus_psl.1.0.0.UPF"
    expected["upf_pins"] = {pseudo.name: "27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962"}
    logged = "/anvil/projects/x-che260157/sts_pa_probe_2026-10-03/tiny_results/candidate-stop/" + pseudo.name
    return expected, {logged: str(pseudo)}


SERIAL = {key: 1 for key in ("nprocs", "nthreads", "ntasks", "nbgrp", "npool", "ndiag")}


@needs_tiny
def test_rederive_arm_on_the_real_tiny_candidate_uses_the_frozen_adapter():
    directory = TINY / "candidate-stop"
    expected, mapping = _tiny_expected()
    result = R.rederive_arm(_tiny_candidate_paths(directory), adapter=adapter, expected_settings=expected,
                            expected_parallel=SERIAL, expected_exit="clean_stop", expected_evaluations=1,
                            upf_path_map=mapping)
    assert result["ok"], result["error"]
    parsed = result["parsed"]
    assert parsed["scf_counts"] == [1] and parsed["optimizer_counts"] == [0] and parsed["xml_exit_status"] == 255
    assert parsed["proposal_geometry"] != parsed["evaluations"][0]["geometry"]
    # Same energy the independent raw summary reads: XML etot x 2.
    xml = R.summarize_xml(directory / "scratch/h2_probe.save/data-file-schema.xml")
    assert parsed["evaluations"][0]["energy_Ry"] == xml["steps"][0]["etot_Ry"]


@needs_tiny
@pytest.mark.parametrize("change,message", [
    ({"expected_evaluations": 2}, "missed registered evaluated stop boundary"),
    ({"expected_exit": "normal_scf"}, "fresh reference did not complete normally"),
    ({"expected_parallel": dict(SERIAL, nprocs=128)}, "processor/pool/thread"),
])
def test_rederive_arm_fails_closed_without_raising(change, message):
    directory = TINY / "candidate-stop"
    expected, mapping = _tiny_expected()
    kwargs = dict(expected_settings=expected, expected_parallel=SERIAL, expected_exit="clean_stop",
                  expected_evaluations=1, upf_path_map=mapping)
    kwargs.update(change)
    result = R.rederive_arm(_tiny_candidate_paths(directory), adapter=adapter, **kwargs)
    assert result["ok"] is False and message in result["error"]


@needs_tiny
def test_rederive_arm_reports_missing_xml_and_wrong_pin(tmp_path):
    directory = TINY / "candidate-stop"
    expected, mapping = _tiny_expected()
    paths = _tiny_candidate_paths(directory)
    paths["xml"] = tmp_path / "missing.xml"
    assert R.rederive_arm(paths, adapter=adapter, expected_settings=expected, expected_parallel=SERIAL,
                          expected_exit="clean_stop", expected_evaluations=1, upf_path_map=mapping)["ok"] is False
    bad = copy.deepcopy(expected)
    bad["upf_pins"] = {k: "0" * 64 for k in bad["upf_pins"]}
    result = R.rederive_arm(_tiny_candidate_paths(directory), adapter=adapter, expected_settings=bad,
                            expected_parallel=SERIAL, expected_exit="clean_stop", expected_evaluations=1,
                            upf_path_map=mapping)
    assert result["ok"] is False and "consumed UPF" in result["error"]


@needs_tiny
def test_real_tiny_mirror_inventory_matches_the_retained_remote_pins():
    receipt = json.loads((PHASE / "pa_tiny_mirror_receipt.json").read_text(encoding="utf-8"))
    local = R.inventory_dir(TINY_ROOT)
    comparison = R.compare_inventories(local, R.normalize_remote_inventory(receipt))
    assert receipt["all_pins_match"] and comparison["remote_rows"] == 66
    assert comparison["matched"] == 66 and not comparison["mismatched"] and not comparison["not_mirrored"]


def test_inventory_comparison_detects_tamper_and_missing(tmp_path):
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub/b.txt").write_text("beta", encoding="utf-8")
    local = R.inventory_dir(tmp_path)
    remote = copy.deepcopy(local) + [{"path": "gone.txt", "size": 1, "sha256": "0" * 64}]
    assert R.compare_inventories(local, remote)["not_mirrored"] == ["gone.txt"]
    (tmp_path / "a.txt").write_text("alphX", encoding="utf-8")
    cmp_ = R.compare_inventories(R.inventory_dir(tmp_path), remote)
    assert cmp_["mismatched"] == ["a.txt"] and cmp_["matched"] == 1
    assert R.normalize_remote_inventory({"files": [{"path": "\\x\\y.txt", "size": 1, "sha256": "a"}]})[0]["path"] == "x/y.txt"


def test_mirror_selection_lists_the_lightweight_readout_set():
    selection = R.mirror_selection()
    assert "trial_21034683.log" in selection and "trial_results/trial_receipt.json" in selection
    assert "trial_results/resumed/checkpoint_copy/outdir/%s.save/data-file-schema.xml" % R.PREFIX in selection
    assert "trial_results/control/outdir/%s.save/data-file-schema.xml" % R.PREFIX in selection
    assert not any("wfc" in s or "charge-density" in s for s in selection)


# ======================================================================================
# Catalyst-layout scenarios: real Trial.run() with process doubles + agreeing raw files
# ======================================================================================
def geom(value):
    return {"unit": "bohr", "species": ["Cu"], "positions": [[value, 0, 0]],
            "cell": [[10, 0, 0], [0, 10, 0], [0, 0, 10]], "fixed_flags": [[0, 0, 0]]}


def qe_stdout(*, energies, cycles, bfgs, stop=False, converged=True, wall=120.0, thr="1.0E-06",
              startup_deleted=False, bfgs_converged=False, extra="", iterations=6, job_done=True):
    lines = ["     Program PWSCF v.7.5 starts on  4Oct2026 at 20: 0",
             "     Parallel version (MPI & OpenMP), running on     128 processor cores",
             "     Number of MPI processes:               128", "     Threads/MPI process:                     1",
             "     K-points division:     npool     =       8",
             "     R & G space division:  proc/nbgrp/npool/nimage =      16",
             "     ELPA distributed-memory algorithm (size of sub-group:  4*  4 procs)",
             "     convergence threshold     =      " + thr]
    for index, energy in enumerate(energies):
        if index == 0 and startup_deleted:
            lines.append("     .bfgs deleted, as requested")
        for k in range(1, iterations + 1):
            lines.append("     iteration # %2d     ecut=    80.00 Ry     beta= 0.30" % k)
        if converged or index < len(energies) - 1:
            lines.append("!    total energy              =  %.8f Ry" % energy)
            lines.append("     convergence has been achieved in %3d iterations" % iterations)
        else:
            lines.append("     convergence NOT achieved after 127 iterations: stopping")
        if index < len(cycles):
            lines.append("     number of scf cycles    =   %d" % cycles[index])
            lines.append("     number of bfgs steps    =   %d" % bfgs[index])
    if bfgs_converged:
        lines.append("     bfgs converged in   3 scf cycles and   2 bfgs steps")
    if stop:
        lines.append("     Program stopped by user request")
    lines.append(extra)
    lines.append("     PWSCF        :     5m 0.00s CPU    %dm%05.2fs WALL" % (wall // 60, wall % 60))
    if job_done:
        lines.append("   JOB DONE.")
    return "\n".join(lines) + "\n"


def qe_xml(energies_ry, *, status, output_energy_ry, converged=True):
    steps = "".join(
        '<step n_step="%d"><scf_conv><convergence_achieved>%s</convergence_achieved><n_scf_iterations>6</n_scf_iterations></scf_conv>'
        "<total_energy><etot>%r</etot></total_energy></step>" % (i + 1, "true" if converged else "false", e / 2.0)
        for i, e in enumerate(energies_ry))
    return ('<?xml version="1.0"?><qes:espresso xmlns:qes="http://www.quantum-espresso.org/ns/qes/qes-1.0" Units="Hartree atomic units">'
            '<general_info><creator NAME="PWSCF" VERSION="7.5"/></general_info>'
            "<parallel_info><nprocs>128</nprocs><nthreads>1</nthreads><ntasks>1</ntasks><nbgrp>1</nbgrp><npool>8</npool><ndiag>16</ndiag></parallel_info>"
            + steps + "<output><total_energy><etot>%r</etot></total_energy></output><exit_status>%d</exit_status></qes:espresso>"
            % (output_energy_ry / 2.0, status))


def allocation_text(runtime_seconds):
    hh, rem = divmod(runtime_seconds, 3600)
    mm, ss = divmod(rem, 60)
    values = {"JobId": JOB, "Account": "che260157", "Partition": "wholenode", "JobState": "RUNNING", "NumNodes": "1",
              "NumCPUs": "128", "NumTasks": "128", "CPUs/Task": "1", "Requeue": "0", "TimeLimit": "16:00:00",
              "RunTime": "%02d:%02d:%02d" % (hh, mm, ss), "AllocTRES": "cpu=128,mem=200G,node=1,billing=128",
              "NodeList": "a544", "Restarts": "0", "BatchFlag": "1", "Dependency": "(null)"}
    return " ".join("%s=%s" % kv for kv in values.items())


class Double(trial.Trial):
    """Real Trial.run() state machine; solver/adapter replaced by agreeing doubles."""

    def __init__(self, spec, *, action="RESUME_CANDIDATE", fail=None, fresh_energy=None, reseed_energy=-100.0,
                 continuity_ok=True, audit_ok=True, call_seconds=900.0):
        self.spec, self.root, self.calls, self.active = spec, Path(spec["trial_root"]), 0, False
        self.clock, self.start = lambda: 1, 0
        self.order, self.fail = [], fail or {}
        self.action, self.reseed_energy, self.call_seconds = action, reseed_energy, call_seconds
        self.fresh_energy = (-99.0 if action != "RESEED_CANDIDATE" else -100.0) if fresh_energy is None else fresh_energy
        self.receipt = {"date": spec["date"], "target": trial.TARGET, "production_accepted": False,
                        "every_step_pa_validated": False, "terminal_fresh_acceptance_validated": False,
                        "genuine_lower_state_reseed_validated": False, "scheduler_status": "UNVERIFIED",
                        "scientific_status": "INCONCLUSIVE", "calls": [], "started_utc": trial.utc_now()}
        def audit(*a, **k):
            if not audit_ok:
                raise adapter.AdapterError("observed continuation did not consume saved optimizer counters")
            return {"raw_consumption_audit": {"passed": True}}
        def compare(left, right):
            deltas = {"energy_Ry": 0.0 if continuity_ok else 1e-3, "position_bohr": 0.0, "force_Ry_bohr": 0.0}
            return {"within_tolerances": continuity_ok, "evaluations": len(left), "max_abs_deltas": deltas}
        self.adapter = types.SimpleNamespace(
            contract=adapter.contract, _validate_arm=Mock(), _geometry_matches=adapter._geometry_matches,
            read_bfgs=lambda *a, **k: {"scf_count": 1, "bfgs_count": 1},
            checkpoint_inventory=lambda out, wave=None: trial.checkpoint_inventory(Path(out), Path(wave) if wave else None),
            pre_resume_decision=self.decide, audit_consumption=audit, compare_trajectories=compare)

    def common_upfs(self):
        (self.root / "common_pseudo").mkdir()
        for pin in self.spec["upfs"]:
            (self.root / "common_pseudo" / Path(pin["path"]).name).write_text("upf", encoding="utf-8")

    def verify_sources(self):
        pass

    def decide(self, warm, fresh, *args, **kwargs):
        action = "HOLD" if fresh is None else self.action
        out = {"action": action, "production_accepted": False, "reason": "double"}
        if fresh is not None:
            out["warm_minus_fresh_meV"] = (warm["evaluations"][0]["energy_Ry"] - fresh["evaluations"][0]["energy_Ry"]) * adapter.RY_MEV
        return out

    def execute(self, name, *, kind, target_cycle, expected_cycles, expected_steps,
                geometry=None, checkpoint=None, seed_fresh=None):
        self.order.append(name)
        elapsed = 300 + 1000 * self.calls
        trial.write_json(self.root / ("allocation_before_call_%02d.json" % (self.calls + 1)),
                         {"argv": ["scontrol"], "stdout": allocation_text(elapsed), "stderr": "", "returncode": 0,
                          "observed_utc": trial.utc_now()})
        self.receipt["scheduler_status"] = "COMPLIANT"
        arm = self.root / name
        arm.mkdir(mode=0o700)
        copied = checkpoint is not None
        outdir = (arm / "checkpoint_copy" / "outdir") if copied else (arm / "outdir")
        self.calls += 1
        call = {"name": name, "kind": kind, "status": "STARTED", "setup": {}}
        self.receipt["calls"].append(call)
        self.save()
        mode = self.fail.get(name)
        try:
            frames_energy = [-100.0 + cycle for cycle in (expected_cycles or [1])]
            if name == "fresh":
                frames_energy = [self.fresh_energy]
            elif name == "reseed":
                frames_energy = [self.reseed_energy]
            first = {"control": 0, "candidate": 0, "negative": 0, "resumed": 1, "reseed": 0, "fresh": None}[name]
            bfgs = [] if name == "fresh" else [first + i for i in range(len(expected_cycles))]
            stop = name != "fresh"
            converged_run = mode not in ("failure_marker",)
            text = qe_stdout(energies=frames_energy, cycles=list(expected_cycles), bfgs=bfgs, stop=stop,
                             converged=converged_run, wall=self.call_seconds * 0.9, startup_deleted=(name == "negative"),
                             bfgs_converged=(mode == "early_convergence"), job_done=mode != "no_job_done",
                             extra="     iteration # 127" if mode == "hea4" else "")
            (arm / "stdout.log").write_text(text, encoding="utf-8")
            (arm / "stderr.log").write_text("", encoding="utf-8")
            (arm / "input.in").write_text("&control\n/\n", encoding="utf-8")
            process = {"arm": name, "returncode": 255 if stop else 0, "timed_out": mode == "timeout",
                       "within_per_call_cap": mode != "timeout", "stop_reason": "registered-evaluated-boundary" if stop else None,
                       "elapsed_seconds": self.call_seconds, "failure_marker_observed": mode == "failure_marker",
                       "HEA4_stall_observed": mode == "hea4", "solver_limit_observed": mode == "solver_limit",
                       "production_accepted": False}
            if mode == "missed_boundary":
                process["stop_reason"] = "missed-evaluated-boundary"
            xml_path = outdir / (trial.PREFIX + ".save") / "data-file-schema.xml"
            xml_path.parent.mkdir(parents=True)
            if mode not in ("missing_xml", "hea4", "failure_marker"):
                xml_path.write_text(qe_xml(frames_energy if name != "fresh" else [], status=0 if name == "fresh" else 255,
                                           output_energy_ry=frames_energy[-1] if name == "fresh" else -90.0), encoding="utf-8")
            (outdir / (trial.PREFIX + ".bfgs")).write_bytes(b"history")
            trial.write_json(arm / "process_receipt.json", process)
            trial.write_json(arm / "setup_receipt.json", {"kind": kind, "expected_cycles": list(expected_cycles),
                                                          "expected_xml_steps": expected_steps})
            call["process"] = process
            if (process.get("timed_out") or process.get("within_per_call_cap") is not True or process.get("supervisor_error")
                    or process.get("capture_error") or process.get("failure_marker_observed")
                    or process.get("HEA4_stall_observed") or process.get("solver_limit_observed")):
                raise trial.TrialError(name + " did not complete within the registered process contract")
            if target_cycle is not None and process.get("stop_reason") != "registered-evaluated-boundary":
                raise trial.TrialError(name + " lacks the registered boundary stop receipt")
            if mode == "early_convergence":
                raise adapter.AdapterError("relaxation ended before the registered evaluated boundary")
            if mode == "validation":
                raise adapter.AdapterError("actual consumed UPF path/hash differs")
            if mode == "negative_validation":
                raise trial.TrialError("negative control lacks actual startup deletion and optimizer count0")
            source = adapter._source(xml_path) if xml_path.exists() else {"path": str(xml_path), "sha256": "0" * 64, "line_start": 1, "line_end": 1}
            frames = []
            for cycle, energy in zip(expected_cycles or [1], frames_energy):
                frames.append({"geometry": geometry_for(name, cycle), "energy_Ry": energy, "status": "CONVERGED",
                               "geometry_role": "evaluated", "energy_unit": "Ry", "geometry_unit": "bohr",
                               "settings_identity": "5" * 64, "source": copy.deepcopy(source)})
            parsed = {"evaluations": frames, "proposal_geometry": geom(1), "settings_identity": "5" * 64,
                      "xml_settings_identity": "6" * 64, "sources": {"xml": source},
                      "scf_counts": list(expected_cycles), "optimizer_counts": bfgs,
                      "xml_exit_status": 0 if name == "fresh" else 255, "evidence_sha256": "4" * 64}
            call["parsed"] = parsed
            call["status"] = "NUMERICAL_RECEIPT_VALIDATED"
            trial.write_json(arm / "parsed_receipt.json", parsed)
            return {"raw": parsed, "outdir": str(outdir), "wfcdir": None}
        except BaseException as exc:
            call["status"] = "INCONCLUSIVE"
            call["error"] = str(exc)
            raise
        finally:
            self.save()


def geometry_for(name, cycle):
    return geom(0 if name in ("fresh", "reseed") else cycle - 1)


@pytest.fixture
def thaw_all(tmp_path):
    yield tmp_path
    for current, dirs, files in os.walk(str(tmp_path)):
        for name in dirs + files:
            try:
                (Path(current) / name).chmod(0o700)
            except OSError:
                pass


def make_mirror(tmp_path, monkeypatch, **kwargs):
    monkeypatch.setattr(trial, "preflight", lambda *args: {"status": "PREFLIGHT_PASS"})
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    spec = copy.deepcopy(SPEC)
    spec["trial_parent"], spec["trial_root"] = str(mirror), str(mirror / "trial_results")
    harness = Double(spec, **kwargs)
    result = harness.run()
    return mirror, result, harness


def sacct(state="COMPLETED", exit_code="0:0", elapsed=9000, cpus=128, tres="billing=128,cpu=128,mem=200G,node=1"):
    return ("%s|%s|%s|%d|%d|200G|%s|%d\n%s.batch|%s|%s|%d|%d||cpu=128|%d\n%s.extern|COMPLETED|0:0|%d|%d||%s|%d\n"
            % (JOB, state, exit_code, elapsed, cpus, tres, elapsed * cpus, JOB, state, exit_code, elapsed, cpus,
               elapsed * cpus, JOB, elapsed, cpus, tres, elapsed * cpus))


def read(mirror, **kwargs):
    kwargs.setdefault("sacct_text", sacct())
    return R.analyze(mirror=mirror, rederive=False, repo=REPO, **kwargs)


def result_of(verdict, cid):
    return verdict["criteria_results"][cid]["result"]


def test_pass_branch_is_corroborated_by_every_gate(tmp_path, monkeypatch, thaw_all):
    mirror, receipt, harness = make_mirror(tmp_path, monkeypatch)
    assert receipt["scientific_status"] == "PASS_ONE_BOUNDARY"
    verdict = read(mirror)
    out = verdict["outcome"]
    assert out["label"] == "PASS" and out["label_basis"] == "PRESTATED" and out["corroboration"] == "RECEIPT_ONLY"
    assert all(out["pass_gates"].values()), out["pass_gates"]
    assert [c["name"] for c in verdict["calls"]] == ["control", "candidate", "fresh", "resumed", "negative"]
    assert verdict["scheduler"]["charged_cpu_su"] == pytest.approx(320.0)
    assert result_of(verdict, "SEQUENCE") == "MET" and result_of(verdict, "CONTINUITY_TOL") == "MET"
    assert result_of(verdict, "BOUNDARY_COUNTS") == "MET" and result_of(verdict, "NEG_CONTROL") == "MET"
    assert result_of(verdict, "BRANCH_RESUME") == "MET" and result_of(verdict, "BRANCH_RESEED") == "NOT_APPLICABLE"
    assert result_of(verdict, "SCHED_PER_CALL") == "MET" and result_of(verdict, "NO_PRODUCTION") == "MET"
    assert result_of(verdict, "INCONC_PROCESS") == "NOT_TRIGGERED" and verdict["integrity_flags"] == []
    assert verdict["production_accepted"] is False and verdict["qe_executed"] is False
    assert verdict["citation_check"] == []
    assert not out["open_questions"]
    md = R.render_markdown(verdict)
    assert "TRIAL OUTCOME: PASS" in md and "320" in md and "independent_launch_review_final.md:67" in md
    json.dumps(verdict)  # serialisable


def test_pass_without_negative_control_when_spec_says_optional_false(tmp_path, monkeypatch, thaw_all):
    monkeypatch.setattr(trial, "preflight", lambda *args: {})
    mirror = tmp_path / "m"
    mirror.mkdir()
    spec = copy.deepcopy(SPEC)
    spec["optional_negative_control"] = False
    spec["trial_parent"], spec["trial_root"] = str(mirror), str(mirror / "trial_results")
    Double(spec).run()
    custom = tmp_path / "spec.json"
    custom.write_text(json.dumps(spec), encoding="utf-8")
    verdict = R.analyze(mirror=mirror, rederive=False, repo=REPO, sacct_text=sacct(), spec_path=custom)
    assert verdict["outcome"]["label"] == "PASS" and result_of(verdict, "NEG_CONTROL") == "NOT_APPLICABLE"


def test_scheduler_failed_3_0_does_not_change_a_corroborated_scientific_pass(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    verdict = read(mirror, sacct_text=sacct("FAILED", "3:0"))
    assert verdict["outcome"]["label"] == "PASS"  # scheduler and scientific outcomes stay separate (DOC:105)
    assert verdict["scheduler"]["slurm_exit_vs_controller"].startswith("controller wrote a non-PASS")


def test_pass_is_withheld_when_resource_caps_are_not_corroborated(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    verdict = read(mirror, sacct_text=sacct("COMPLETED", "0:0", elapsed=57601))
    out = verdict["outcome"]
    assert out["label"] == "UNMAPPED" and out["candidate_labels"] == ["PASS", "INCONCLUSIVE"]
    assert "resource_caps" in out["reasons"][0] and result_of(verdict, "SCHED_CAP_SU") == "NOT_MET"
    over_alloc = read(mirror, sacct_text=sacct(cpus=256, tres="billing=256,cpu=256,mem=200G,node=1"))
    assert over_alloc["outcome"]["label"] == "UNMAPPED" and result_of(over_alloc, "SCHED_ALLOC") == "NOT_MET"


def test_missing_xml_in_mirror_blocks_the_pass_and_is_an_integrity_gap(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    next((mirror / "trial_results/resumed").rglob("data-file-schema.xml")).unlink()
    verdict = read(mirror)
    assert verdict["outcome"]["label"] == "UNMAPPED"
    assert any("resumed" in f and "XML" in f for f in verdict["integrity_flags"])
    assert any("resumed: xml missing" in g for g in verdict["mirror"]["required_gaps"])


def test_tampered_energy_in_raw_xml_is_flagged_against_the_receipt(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    xml = mirror / "trial_results/control/outdir" / (trial.PREFIX + ".save") / "data-file-schema.xml"
    xml.write_text(xml.read_text(encoding="utf-8").replace("<etot>-49.5</etot>", "<etot>-49.4</etot>", 1), encoding="utf-8")
    verdict = read(mirror)
    assert any("control: receipt energies differ" in f for f in verdict["integrity_flags"])
    assert verdict["outcome"]["label"] == "UNMAPPED"


def test_remote_inventory_mismatch_blocks_pass(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    inventory = R.inventory_dir(mirror)
    clean = read(mirror, remote_inventory={"files": inventory})
    assert clean["outcome"]["label"] == "PASS"
    assert clean["mirror"]["remote_inventory_comparison"]["mismatched"] == []
    inventory[0] = dict(inventory[0], sha256="f" * 64)
    broken = read(mirror, remote_inventory={"files": inventory})
    assert broken["outcome"]["label"] == "UNMAPPED"
    assert broken["mirror"]["remote_inventory_comparison"]["mismatched"] == [inventory[0]["path"]]


def test_reseed_validated_is_reported_as_its_own_branch(tmp_path, monkeypatch, thaw_all):
    mirror, receipt, _ = make_mirror(tmp_path, monkeypatch, action="RESEED_CANDIDATE")
    assert receipt["scientific_status"] == "RESEED_BRANCH_ONLY"
    verdict = read(mirror)
    out = verdict["outcome"]
    assert out["label"] == "RESEED_BRANCH_ONLY" and out["open_questions"] == ["OQ4"]
    assert out["candidate_labels"] == ["PASS (reseed branch only)"]
    assert result_of(verdict, "RESEED_VALID") == "MET" and result_of(verdict, "BRANCH_RESEED") == "MET"
    assert result_of(verdict, "CONTINUITY_TOL") == "NOT_EVALUATED" and result_of(verdict, "NO_SPLICE") == "MET"
    assert [c["name"] for c in verdict["calls"]] == ["control", "candidate", "fresh", "reseed"]


def test_upper_state_reseed_is_prestated_inconclusive(tmp_path, monkeypatch, thaw_all):
    mirror, receipt, _ = make_mirror(tmp_path, monkeypatch, action="RESEED_CANDIDATE", reseed_energy=-99.0)
    assert receipt["scientific_status"] == "INCONCLUSIVE" and receipt["reseed_branch_attempted"] is True
    verdict = read(mirror)
    out = verdict["outcome"]
    assert out["label"] == "INCONCLUSIVE" and out["label_basis"] == "PRESTATED"
    assert "INCONC_RESEED" in out["criteria"] and result_of(verdict, "INCONC_RESEED") == "TRIGGERED"
    assert result_of(verdict, "RESEED_VALID") == "NOT_MET"


def test_hold_with_a_failed_fresh_stall_is_inconclusive_by_the_process_rule(tmp_path, monkeypatch, thaw_all):
    mirror, receipt, _ = make_mirror(tmp_path, monkeypatch, fail={"fresh": "hea4"})
    assert receipt["scientific_status"] == "HOLD" and receipt["fresh_failure"]
    verdict = read(mirror)
    out = verdict["outcome"]
    assert out["label"] == "INCONCLUSIVE" and out["label_basis"] == "PRESTATED"
    assert out["controller_scientific_status"] == "HOLD" and "INCONC_PROCESS" in out["criteria"]
    assert result_of(verdict, "BRANCH_HOLD") == "TRIGGERED" and result_of(verdict, "INCONC_PROCESS") == "TRIGGERED"
    fresh = next(c for c in verdict["calls"] if c["name"] == "fresh")
    assert fresh["failure_class"] == "PROCESS_CONTRACT" and fresh["raw"]["stdout"]["max_scf_iteration_seen"] == 127
    assert fresh["raw"]["xml"] == {"present": False}


def test_hold_without_a_call_failure_is_unmapped(tmp_path, monkeypatch, thaw_all):
    mirror, receipt, _ = make_mirror(tmp_path, monkeypatch, action="HOLD")
    assert receipt["scientific_status"] == "HOLD" and all(c["status"] == "NUMERICAL_RECEIPT_VALIDATED" for c in receipt["calls"])
    verdict = read(mirror)
    assert verdict["outcome"]["label"] == "UNMAPPED" and verdict["outcome"]["open_questions"] == ["OQ3"]
    assert verdict["outcome"]["candidate_labels"] == ["INCONCLUSIVE"] and result_of(verdict, "SEQUENCE") == "MET"


def test_continuity_tolerance_miss_is_unmapped_with_fail_as_a_candidate(tmp_path, monkeypatch, thaw_all):
    mirror, receipt, _ = make_mirror(tmp_path, monkeypatch, continuity_ok=False)
    assert receipt["scientific_status"] == "INCONCLUSIVE" and "did not agree" in receipt["error"]
    verdict = read(mirror)
    out = verdict["outcome"]
    assert out["label"] == "UNMAPPED" and out["candidate_labels"] == ["FAIL", "INCONCLUSIVE"]
    assert out["open_questions"] == ["OQ1"] and result_of(verdict, "CONTINUITY_TOL") == "NOT_MET"
    assert "FAIL" not in {out["label"]}
    md = R.render_markdown(verdict)
    assert "OQ1" in md and "FAIL, INCONCLUSIVE" in md


def test_unconsumed_checkpoint_after_valid_resume_is_unmapped(tmp_path, monkeypatch, thaw_all):
    mirror, receipt, _ = make_mirror(tmp_path, monkeypatch, audit_ok=False)
    assert receipt["scientific_status"] == "INCONCLUSIVE" and "consume saved optimizer" in receipt["error"]
    verdict = read(mirror)
    out = verdict["outcome"]
    assert out["label"] == "UNMAPPED" and out["open_questions"] == ["OQ2"] and out["candidate_labels"] == ["FAIL", "INCONCLUSIVE"]
    assert [c["name"] for c in verdict["calls"]][-1] == "resumed"


@pytest.mark.parametrize("fail,klass,criterion,scf_not,flag", [
    ({"resumed": "hea4"}, "PROCESS_CONTRACT", "INCONC_PROCESS", 0, "HEA4_stall_observed"),
    ({"resumed": "timeout"}, "PROCESS_CONTRACT", "INCONC_PROCESS", 0, "timed_out"),
    ({"resumed": "failure_marker"}, "PROCESS_CONTRACT", "INCONC_PROCESS", 1, "failure_marker_observed"),
    ({"resumed": "solver_limit"}, "PROCESS_CONTRACT", "INCONC_PROCESS", 0, "solver_limit_observed"),
    ({"candidate": "missed_boundary"}, "MISSED_BOUNDARY", "INCONC_BOUNDARY", 0, None),
    ({"control": "early_convergence"}, "MISSED_BOUNDARY", "INCONC_BOUNDARY", 0, None),
])
def test_call_level_failures_are_prestated_inconclusive(tmp_path, monkeypatch, thaw_all, fail, klass, criterion, scf_not, flag):
    mirror, receipt, _ = make_mirror(tmp_path, monkeypatch, fail=fail)
    assert receipt["scientific_status"] == "INCONCLUSIVE"
    verdict = read(mirror)
    out = verdict["outcome"]
    assert out["label"] == "INCONCLUSIVE" and out["label_basis"] == "PRESTATED" and criterion in out["criteria"]
    bad = [c for c in verdict["calls"] if c["status"] != "NUMERICAL_RECEIPT_VALIDATED"]
    assert len(bad) == 1 and bad[0]["name"] == next(iter(fail)) and bad[0]["failure_class"] == klass
    assert bad[0]["raw"]["stdout"]["scf_not_converged_count"] == scf_not
    if flag:
        assert bad[0]["process_flags"][flag] is True
    assert result_of(verdict, criterion) == "TRIGGERED"
    assert verdict["calls"][-1]["name"] == next(iter(fail))  # no call after the failure: no retry, no continuation


def test_raw_validation_refusal_and_failed_negative_control_surface_their_questions(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch, fail={"candidate": "validation"})
    out = read(mirror)["outcome"]
    assert out["label"] == "INCONCLUSIVE" and out["label_basis"] == "FROZEN_CONTROLLER_RECORD_ONLY" and out["open_questions"] == ["OQ8"]
    second = tmp_path / "second"
    second.mkdir()
    mirror2, receipt, _ = make_mirror(second, monkeypatch, fail={"negative": "negative_validation"})
    verdict = read(mirror2)
    assert receipt["scientific_status"] == "INCONCLUSIVE" and "continuity" in receipt
    assert receipt["continuity"]["within_tolerances"] is True  # continuity itself was numerically fine
    assert verdict["outcome"]["label"] == "INCONCLUSIVE" and "OQ5" in verdict["outcome"]["open_questions"]


def test_killed_call_at_the_time_limit_is_inconclusive_not_finished(tmp_path, monkeypatch, thaw_all):
    mirror, receipt, _ = make_mirror(tmp_path, monkeypatch)
    path = mirror / "trial_results/trial_receipt.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["calls"] = data["calls"][:4]  # the resumed call never recorded its end
    data["calls"][3]["status"] = "STARTED"
    for key in ("process", "parsed"):
        data["calls"][3].pop(key, None)
    data["scientific_status"] = "INCONCLUSIVE"
    for key in ("continuity", "consumption_audit", "negative_control"):
        data.pop(key, None)
    path.write_text(json.dumps(data), encoding="utf-8")
    verdict = read(mirror, sacct_text=sacct("TIMEOUT", "0:15", elapsed=57600))
    out = verdict["outcome"]
    assert out["label"] == "INCONCLUSIVE" and out["label_basis"] == "PRESTATED"
    assert verdict["calls"][3]["failure_class"] == "NOT_FINISHED" and verdict["scheduler"]["charged_cpu_su"] == 2048.0
    assert result_of(verdict, "INCONC_PROCESS") == "TRIGGERED" and result_of(verdict, "SCHED_CAP_SU") == "MET"
    assert "TIMEOUT" in R.render_markdown(verdict)


def test_aggregate_time_cap_error_is_inconclusive(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    path = mirror / "trial_results/trial_receipt.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(scientific_status="INCONCLUSIVE", error="aggregate elapsed time reached 16h")
    path.write_text(json.dumps(data), encoding="utf-8")
    out = read(mirror, sacct_text=sacct("FAILED", "3:0", elapsed=57600))["outcome"]
    assert out["label"] == "INCONCLUSIVE" and "CTRL_AGGREGATE" in out["criteria"]


def test_refused_allocation_is_a_resource_problem(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch, fail={"candidate": "timeout"})
    path = mirror / "trial_results/trial_receipt.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["scheduler_status"] = "REFUSED"
    path.write_text(json.dumps(data), encoding="utf-8")
    # The controller writes allocation_before_call_NN.json before it validates it, so a refusal ahead of
    # a call leaves a receipt with no call entry; its reason must survive in the readout.
    trial.write_json(mirror / "trial_results/allocation_before_call_03.json",
                     {"stdout": allocation_text(3600).replace("billing=128", "billing=256"), "stderr": "", "returncode": 0})
    verdict = read(mirror)
    out = verdict["outcome"]
    assert out["label"] == "INCONCLUSIVE" and any("REFUSED" in r for r in out["reasons"])
    assert verdict["allocation_receipts"]["unstarted_call_03"]["compliant"] is False
    assert any("unstarted_call_03" in r and "TRES" in r for r in out["reasons"])


def test_inventory_rows_the_remote_did_not_hash_are_size_checked_only(tmp_path):
    (tmp_path / "big.bin").write_bytes(b"x" * 10)
    local = R.inventory_dir(tmp_path)
    same = R.compare_inventories(local, [{"path": "big.bin", "size": 10, "sha256": None}])
    assert same["size_only_matched"] == 1 and same["matched"] == 0 and not same["mismatched"]
    wrong = R.compare_inventories(local, [{"path": "big.bin", "size": 11, "sha256": None}])
    assert wrong["mismatched"] == ["big.bin"]


def test_not_terminal_is_not_ready(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    assert read(mirror, sacct_text=sacct("RUNNING", "0:0", elapsed=500))["outcome"]["label"] == "NOT_READY"
    assert read(mirror, sacct_text="21034683|PENDING|0:0|0|0|200G||0\n")["outcome"]["label"] == "NOT_READY"
    assert R.analyze(mirror=mirror, rederive=False, repo=REPO)["outcome"]["label"] == "NOT_READY"


def test_missing_receipt_distinguishes_refusal_from_incomplete_mirror(tmp_path):
    empty = tmp_path / "m"
    (empty / "trial_results").mkdir(parents=True)
    gap = read(empty)["outcome"]
    assert gap["label"] == "EVIDENCE_GAP"
    (empty / ("trial_%s.log" % JOB)).write_text("REFUSE: prior trial output\n", encoding="utf-8")
    refusal = read(empty, sacct_text=sacct("FAILED", "2:0", elapsed=3))["outcome"]
    assert refusal["label"] == "INCONCLUSIVE" and refusal["open_questions"] == ["OQ8"]
    no_dir = read(tmp_path / "absent")["outcome"]
    assert no_dir["label"] == "EVIDENCE_GAP"


def test_analysis_is_read_only_and_cli_refuses_to_overwrite(tmp_path, monkeypatch, thaw_all, capsys):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    before = R.inventory_dir(mirror)
    (tmp_path / "sacct.txt").write_text(sacct(), encoding="utf-8")
    (tmp_path / "jobsu.txt").write_text("CPU SUs Already Used:  320.0000\nTotal CPU SUs used for all jobs: 320.0000\n", encoding="utf-8")
    out = tmp_path / "out"
    args = ["--mirror", str(mirror), "--sacct", str(tmp_path / "sacct.txt"), "--jobsu", str(tmp_path / "jobsu.txt"),
            "--no-rederive", "--out", str(out), "--balance-before", "36878.2"]
    assert R.main(args) == 0
    assert R.inventory_dir(mirror) == before
    verdict = json.loads((out / "readout_verdict.json").read_text(encoding="utf-8"))
    assert verdict["outcome"]["label"] == "PASS" and verdict["scheduler"]["jobsu_minus_computed_su"] == pytest.approx(0.0)
    assert verdict["scheduler"]["balance_after_su_exact_product"] == pytest.approx(36878.2 - 320.0)
    assert "TRIAL OUTCOME: PASS" in (out / "readout_table.md").read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        R.main(args)
    capsys.readouterr()
    assert R.main(["--print-mirror-selection"]) == 0 and "trial_receipt.json" in capsys.readouterr().out
    assert R.main(["--check-citations"]) == 0


def test_observations_jsonl_supplies_the_accounting_row(tmp_path, monkeypatch, thaw_all, capsys):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    row = {"observed_utc": "x", "returncode": 0, "stdout": json.dumps({"commands": {"accounting": {"stdout": sacct()}}})}
    (tmp_path / "obs.jsonl").write_text(json.dumps({"observed_utc": "old", "stdout": "{}"}) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
    assert R.main(["--mirror", str(mirror), "--observations", str(tmp_path / "obs.jsonl"), "--no-rederive"]) == 0
    assert "TRIAL OUTCOME: PASS" in capsys.readouterr().out


# ======================================================================================
# Real 72-atom / 128-rank catalyst log (retained September relaxation, killed at the SCF ceiling)
# ======================================================================================
REAL_CATALYST_LOG = (REPO / "results/lowtail_low_state_restart_2026-09-22/relax2/outputs/"
                     "Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.out")


@pytest.mark.skipif(not REAL_CATALYST_LOG.is_file(), reason="retained catalyst log absent")
def test_real_catalyst_log_summary_and_header_binding():
    # sha256 is the pin recorded in source_boundary_review.md (line 294).
    assert R.sha256_file(REAL_CATALYST_LOG) == "6a99fcd94e2b9b5756aa5a9ee905dc16b330deab69c43bff414f50b2aeb24082"
    text = REAL_CATALYST_LOG.read_text(encoding="utf-8", errors="replace")
    out = R.summarize_stdout(text, trial)
    assert out["mpi_processes"] == 128 and out["qe_banners"] == ["7.5"]
    assert out["scf_cycles"] == [1, 2, 3, 4, 5, 6] and out["bfgs_counts"] == [0, 1, 2, 3, 4, 5]
    assert out["first_conv_thr_Ry"] == 1e-6 and out["scf_iterations_to_converge"][:5] == [3, 12, 26, 31, 34]
    assert out["max_scf_iteration_seen"] == 127 and out["job_done"] is False  # killed at iteration 127, no clean shutdown
    assert out["scf_not_converged_count"] == 0 and out["wall_seconds"] is None
    header = R.header_binding(text, adapter, trial.SHAPE)
    assert header == {"checked": True, "ok": True, "nprocs": 128, "nthreads": 1, "npool": 8,
                      "diagonalization": "ELPA", "elpa_subgroup": [4, 4]}
    # Mutated headers fail closed instead of passing silently.
    assert R.header_binding(text.replace("npool     =       8", "npool     =       4"), adapter, trial.SHAPE)["ok"] is False
    assert R.header_binding(text.replace("4*  4 procs", "2*  2 procs"), adapter, trial.SHAPE)["ok"] is False
    assert R.header_binding(None, adapter, trial.SHAPE) == {"checked": False}


def test_catalyst_header_rows_in_the_scenario_table(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    verdict = read(mirror)
    assert all(c["raw"]["header_binding"]["ok"] for c in verdict["calls"])
    assert result_of(verdict, "RAW_BINDING") == "PARTIAL_HEADERS_ONLY"
    assert "MPI128/thr1/npool8/ELPA[4, 4]" in R.render_markdown(verdict)
    # A header that is not the registered shape blocks the pass.
    stdout = mirror / "trial_results/resumed/stdout.log"
    stdout.write_text(stdout.read_text(encoding="utf-8").replace("4*  4 procs", "2*  2 procs"), encoding="utf-8")
    broken = read(mirror)
    assert result_of(broken, "RAW_BINDING") == "NOT_MET" and broken["outcome"]["label"] == "UNMAPPED"


def test_requested_rederivation_that_cannot_corroborate_blocks_the_pass(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    verdict = R.analyze(mirror=mirror, rederive=True, repo=REPO, sacct_text=sacct())
    # The synthetic raw files are not real QE decks, so the frozen adapter must refuse them -> no PASS.
    assert verdict["rederivation"]["arms"]["control"]["ok"] is False
    assert result_of(verdict, "RAW_BINDING") == "NOT_MET"
    assert verdict["outcome"]["label"] == "UNMAPPED" and "raw_binding" in verdict["outcome"]["reasons"][0]
    assert verdict["outcome"]["corroboration"] == "RECEIPT_ONLY"


def test_refusal_before_the_first_call_is_inconclusive(tmp_path, monkeypatch, thaw_all):
    monkeypatch.setattr(trial, "preflight", lambda *args: (_ for _ in ()).throw(trial.TrialError("seed pin drift")))
    mirror = tmp_path / "m"
    mirror.mkdir()
    spec = copy.deepcopy(SPEC)
    spec["trial_parent"], spec["trial_root"] = str(mirror), str(mirror / "trial_results")
    harness = Double(spec)
    with pytest.raises(trial.TrialError):
        harness.run()
    # preflight raises before trial_results exists; emulate the post-mkdir refusal the controller records
    (mirror / "trial_results").mkdir()
    trial.write_json(mirror / "trial_results/trial_receipt.json", dict(
        harness.receipt, scientific_status="INCONCLUSIVE", error="seed pin drift", call_count=0))
    out = read(mirror, sacct_text=sacct("FAILED", "3:0", elapsed=20))["outcome"]
    assert out["label"] == "INCONCLUSIVE" and out["label_basis"] == "FROZEN_CONTROLLER_RECORD_ONLY"
    assert out["open_questions"] == ["OQ8"]


def _edit_receipt(mirror, mutate):
    path = mirror / "trial_results/trial_receipt.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data), encoding="utf-8")


def _edit_text(path, old, new):
    text = path.read_text(encoding="utf-8")
    assert old in text, (path, old)
    path.write_text(text.replace(old, new), encoding="utf-8")


@pytest.mark.parametrize("name", [
    "continuity_flag_false", "production_flag_true", "negative_call_dropped", "threshold_changed",
    "scf_cycle_sequence_changed", "allocation_receipt_missing", "negative_startup_deletion_removed",
    "call_over_cap", "branch_decision_hold"])
def test_every_pass_gate_independently_blocks_a_pass(tmp_path, monkeypatch, thaw_all, name):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    arm = mirror / "trial_results"
    gate = {
        "continuity_flag_false": "continuity_within_tolerances", "production_flag_true": "production_flags_false",
        "negative_call_dropped": "registered_sequence", "threshold_changed": "first_threshold",
        "scf_cycle_sequence_changed": "boundary_counts", "allocation_receipt_missing": "per_call_allocation_receipts",
        "negative_startup_deletion_removed": "negative_control", "call_over_cap": "resource_caps",
        "branch_decision_hold": "registered_sequence"}[name]
    if name == "continuity_flag_false":
        _edit_receipt(mirror, lambda d: d["continuity"].update(within_tolerances=False))
    elif name == "production_flag_true":
        _edit_receipt(mirror, lambda d: d.update(production_accepted=True))
    elif name == "negative_call_dropped":
        _edit_receipt(mirror, lambda d: d.update(calls=d["calls"][:4]))
    elif name == "threshold_changed":
        _edit_text(arm / "control/stdout.log", "1.0E-06", "1.0E-08")
    elif name == "scf_cycle_sequence_changed":
        _edit_text(arm / "control/stdout.log", "number of scf cycles    =   3", "number of scf cycles    =   4")
    elif name == "allocation_receipt_missing":
        (arm / "allocation_before_call_03.json").unlink()
    elif name == "negative_startup_deletion_removed":
        _edit_text(arm / "negative/stdout.log", ".bfgs deleted, as requested", "")
    elif name == "call_over_cap":
        _edit_receipt(mirror, lambda d: d["calls"][2]["process"].update(within_per_call_cap=False))
    elif name == "branch_decision_hold":
        _edit_receipt(mirror, lambda d: d["pre_resume_decision"].update(action="HOLD"))
    verdict = read(mirror)
    out = verdict["outcome"]
    assert out["label"] != "PASS", name
    assert out["pass_gates"] is None or out["pass_gates"][gate] is False, (name, out["pass_gates"])


def test_remote_inventory_snippet_runs_from_stdin_and_matches_the_local_inventory(tmp_path):
    import subprocess
    root = tmp_path / "parent"
    (root / "trial_results/control").mkdir(parents=True)
    (root / "trial_results/control/stdout.log").write_text("log", encoding="utf-8")
    (root / "trial_results/control/wfc1.dat").write_bytes(b"w" * 2048)
    (root / "trial_21034683.log").write_text("slurm", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src/unrelated.py").write_text("x", encoding="utf-8")
    script = (HERE / "remote_inventory_snippet.py").read_text(encoding="utf-8")
    run = subprocess.run([sys.executable, "-B", "-", str(root), "--include", "trial_results", "--include", "trial_21034683.log",
                          "--max-hash-mb", "0.001"], input=script, capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
    remote = json.loads(run.stdout)
    paths = [r["path"] for r in remote["files"]]
    assert paths == ["trial_21034683.log", "trial_results/control/stdout.log", "trial_results/control/wfc1.dat"]
    by_path = {r["path"]: r for r in remote["files"]}
    assert by_path["trial_results/control/wfc1.dat"]["sha256"] is None  # above the hash limit: size only
    assert by_path["trial_results/control/stdout.log"]["sha256"] == hashlib.sha256(b"log").hexdigest()
    comparison = R.compare_inventories(R.inventory_dir(root), R.normalize_remote_inventory(remote))
    assert comparison["matched"] == 2 and comparison["size_only_matched"] == 1 and not comparison["mismatched"]
    assert "src/unrelated.py" in comparison["local_only"]
    bad = subprocess.run([sys.executable, "-B", "-", str(tmp_path / "absent")], input=script, capture_output=True, text=True, timeout=60)
    assert bad.returncode != 0
    # Read-only by construction: no write-mode open anywhere in the snippet.
    assert "'w'" not in script and '"w"' not in script and "open(path, \"rb\")" in script


def test_resumed_call_threshold_is_outside_the_first_threshold_check(tmp_path, monkeypatch, thaw_all):
    # QE tightens conv_thr after the first ionic step; the frozen controller therefore never checks the
    # resumed call's printed threshold (CTRL:857), and neither does the readout.
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    _edit_text(mirror / "trial_results/resumed/stdout.log", "1.0E-06", "8.3E-08")
    verdict = read(mirror)
    assert verdict["outcome"]["label"] == "PASS" and "resumed" not in verdict["criteria_results"]["FIRST_THRESHOLD"]["evidence"]
    assert R.FIRST_THRESHOLD_KINDS == ("control", "candidate", "fresh", "reseed", "negative")


def test_locate_mirror_accepts_parent_or_trial_results_directory(tmp_path):
    parent = tmp_path / "parent"
    (parent / "trial_results").mkdir(parents=True)
    (parent / "trial_results/trial_receipt.json").write_text("{}", encoding="utf-8")
    (parent / ("trial_%s.log" % JOB)).write_text("log", encoding="utf-8")
    a = R.locate_mirror(parent, JOB)
    b = R.locate_mirror(parent / "trial_results", JOB)
    assert a["trial_dir"] == b["trial_dir"] == parent / "trial_results"
    assert a["root"] == b["root"] == parent and a["slurm_log"] == b["slurm_log"] == parent / ("trial_%s.log" % JOB)
    assert R.locate_mirror(tmp_path / "nothing", JOB)["trial_dir"] is None


@needs_tiny
def test_rederive_trial_plumbing_on_a_real_tiny_arm_placed_in_the_catalyst_layout(tmp_path):
    # The tiny deck is not the catalyst deck, so only the candidate arm exists and the registered 1e-6 Ry
    # threshold cannot hold (the tiny deck uses 1e-10): this exercises rederive_trial's real adapter calls
    # and shows its post-checks fail closed instead of passing.
    src = TINY / "candidate-stop"
    trial_dir = tmp_path / "trial_results"
    arm = trial_dir / "candidate"
    xml = arm / "outdir" / (R.PREFIX + ".save") / "data-file-schema.xml"
    xml.parent.mkdir(parents=True)
    for name in ("input.in", "stdout.log", "stderr.log"):
        shutil.copy2(src / name, arm / name)
    shutil.copy2(src / "receipt.json", arm / "process_receipt.json")
    shutil.copy2(src / "scratch/h2_probe.save/data-file-schema.xml", xml)
    (arm / "setup_receipt.json").write_text(json.dumps({"expected_cycles": [1], "expected_xml_steps": 1}), encoding="utf-8")
    (trial_dir / "common_pseudo").mkdir()
    upf = "H.pbe-rrkjus_psl.1.0.0.UPF"
    shutil.copy2(src / upf, trial_dir / "common_pseudo" / upf)
    spec = {"source_deck": {"sha256": R.sha256_file(src / "input.in")},
            "upfs": [{"path": "/anvil/x/" + upf, "sha256": "27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962"}]}
    stub = types.SimpleNamespace(SHAPE=SERIAL)
    out = R.rederive_trial(trial_dir, {}, repo=REPO, spec=spec, source_deck=src / "input.in", trial=stub, adapter=adapter)
    assert list(out["arms"]) == ["candidate"] and out["arms"]["candidate"]["ok"], out["arms"]["candidate"]["error"]
    checks = out["arms"]["candidate"]["post_checks"]
    assert checks["scf_counts_match_expected"] is True and checks["first_threshold_1e-6"] is False
    assert "1e-6" in checks["first_threshold_error"] or "threshold" in checks["first_threshold_error"]
    assert out["derived"] == {}
    # The same data blocks a PASS through the RAW_BINDING criterion when it belongs to a validated call.
    row = {"name": "candidate", "status": "NUMERICAL_RECEIPT_VALIDATED", "failure_class": None,
           "raw": {"header_binding": {"checked": False}, "stdout": {}, "xml": {}}, "process_flags": {},
           "receipt_energies_Ry": [], "error": None, "within_per_call_cap": True}
    results, outcome, integrity, _ = R.evaluate(
        receipt={"scientific_status": "PASS_ONE_BOUNDARY", "calls": [row], "production_accepted": False,
                 "every_step_pa_validated": False, "terminal_fresh_acceptance_validated": False},
        calls=[row], sched=R.assess_scheduler(R.parse_sacct(sacct(), JOB), SPEC), spec=SPEC, trial_dir=trial_dir,
        slurm_log_text=None, mirror_gaps=[], rederived=out, allocation_receipts={}, repo=REPO)
    assert results["RAW_BINDING"]["result"] == "NOT_MET" and outcome["label"] == "UNMAPPED"


def test_interim_readout_while_running_shows_the_live_table_and_no_result(tmp_path, monkeypatch, thaw_all):
    mirror, _, _ = make_mirror(tmp_path, monkeypatch)
    _edit_receipt(mirror, lambda d: (d.update(calls=d["calls"][:2], scientific_status="INCONCLUSIVE"),
                                     d["calls"][1].update(status="STARTED"),
                                     [d["calls"][1].pop(k, None) for k in ("process", "parsed")]))
    verdict = read(mirror, sacct_text=sacct("RUNNING", "0:0", elapsed=2400))
    md = R.render_markdown(verdict)
    assert verdict["outcome"]["label"] == "NOT_READY" and verdict["scheduler"]["charged_cpu_su"] == pytest.approx(2400 * 128 / 3600)
    assert "initial placeholder" in md and "Controller scientific_status" not in md
    assert [c["name"] for c in verdict["calls"]] == ["control", "candidate"]
    assert verdict["calls"][0]["raw"]["header_binding"]["ok"] and "MPI128/thr1/npool8/ELPA[4, 4]" in md
    assert verdict["allocation_receipts"]["control"]["compliant"] is True and verdict["calls"][1]["failure_class"] == "NOT_FINISHED"


@pytest.mark.parametrize("drop_meV,expected", [(9.999999, "RESUME_CANDIDATE"), (10.0, "RESUME_CANDIDATE"),
                                              (10.000001, "RESEED_CANDIDATE"), (-30.0, "RESUME_CANDIDATE")])
def test_recomputed_branch_uses_the_strict_ten_meV_rule(tmp_path, drop_meV, expected):
    # Stub adapter: the readout's own fresh-vs-warm recomputation (same expression as pa_qe_adapter.py:1213)
    # is isolated from the parser so the exact-10-meV boundary can be tested.
    conversion, delta = adapter.contract.RY_MEV, adapter.contract.DELTA_MEV
    energies = {"candidate": 0.0, "fresh": -drop_meV / conversion}
    for name in energies:
        (tmp_path / name / "outdir" / (R.PREFIX + ".save")).mkdir(parents=True)
        (tmp_path / name / "outdir" / (R.PREFIX + ".save") / "data-file-schema.xml").write_text("<x/>", encoding="utf-8")
    def read_qe_arm(input_path, *args, **kwargs):
        name = Path(input_path).parent.name
        return {"evaluations": [{"energy_Ry": energies[name], "geometry": geom(0)}], "scf_counts": [], "xml_settings_identity": "x",
                "optimizer_counts": [0], "startup_history_deleted": False, "startup_history_reset": False,
                "restart_fallback": False, "proposal_geometry": geom(1), "first_conv_thr_Ry": 1e-6}
    stub = types.SimpleNamespace(parse_deck=lambda *a, **k: {"settings_identity": "s"}, read_qe_arm=read_qe_arm,
                                 require_expected_first_threshold=lambda *a: True, RY_MEV=conversion,
                                 contract=types.SimpleNamespace(DELTA_MEV=delta))
    for name in energies:
        (tmp_path / name / "process_receipt.json").write_text("{}", encoding="utf-8")
    spec = {"source_deck": {"sha256": "0" * 64}, "upfs": []}
    out = R.rederive_trial(tmp_path, {}, repo=REPO, spec=spec, source_deck=tmp_path / "deck.in",
                           trial=types.SimpleNamespace(SHAPE=SERIAL), adapter=stub)
    assert out["derived"]["implied_action"] == expected
    assert out["derived"]["warm_minus_fresh_meV"] == pytest.approx(drop_meV)
    assert out["derived"]["fresh_strictly_more_than_10meV_lower"] is (expected == "RESEED_CANDIDATE")
