"""Offline checks for the fixed-geometry diagnostic decks, controller and readout; never launch QE/Slurm."""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import pa_catalyst_retest as base
import pa_fixed_geometry_decks as decks
import pa_fixed_geometry_diag as diag
import pa_fixed_geometry_readout as readout

TRIAL = ROOT / "results/pa_catalyst_retest_readout_2026-10-05/raw_mirror/trial_results"
XML = "outdir/slab_c5low__pa_boundary.save/data-file-schema.xml"
SPEC = ROOT / "results/pa_fixed_geometry_diag_2026-10-05/launch_spec.json"
needs_mirror = pytest.mark.skipif(not (TRIAL / "resumed/stdout.log").exists(), reason="terminal mirror absent")


# ---------------------------------------------------------------- decks
@needs_mirror
@pytest.mark.parametrize("arm", sorted(decks.ARMS))
def test_each_deck_differs_from_its_template_only_by_declared_edits(arm):
    deck, changes = decks.build(arm)
    template = decks.pinned_template(decks.ARMS[arm]["template"]).split("\n")
    lines = deck.split("\n")
    inserted = [c["new"] for c in changes if "inserted_after_line" in c]
    for line in inserted:
        lines.remove(line)
    expected_keys = set(decks.ARMS[arm]["set"])
    if decks.ARMS[arm]["positions"] == "G2":
        g2 = decks.positions_block(decks.pinned_template("resumed"))
        start = lines.index(g2[0])
        assert lines[start:start + 73] == g2
        old = decks.positions_block("\n".join(template))
        t0 = template.index(old[0])
        template = template[:t0] + template[t0 + 73:]
        lines = lines[:start] + lines[start + 73:]
    assert len(lines) == len(template)
    changed = {a.split("=")[0].strip() for a, b in zip(template, lines) if a != b}
    assert changed == expected_keys
    assert deck.endswith("\n") or deck == "\n".join(deck.split("\n"))
    assert "\r" not in deck


@needs_mirror
def test_replay_and_ethr_decks_are_the_resumed_call_plus_one_variable():
    resumed = decks.pinned_template("resumed")
    a, _ = decks.build("A_replay")
    b, _ = decks.build("B_ethr")
    assert a.replace("sts_pa_fixed_geometry_diag_2026-10-05/runs/A_replay/outdir",
                     "sts_pa_catalyst_retest_2026-10-04/trial_results/resumed/checkpoint_copy/outdir") == resumed
    assert b.replace("  diago_thr_init = 1.0d-6\n", "").replace("B_ethr", "A_replay") == a
    assert "restart_mode = 'restart'" in a and "calculation = 'relax'" in a


@needs_mirror
def test_ladder_and_fresh_decks_evaluate_g2_exactly():
    g2 = decks.positions_block(decks.pinned_template("resumed"))
    for arm in ("C1_warm_1e-6", "C2_warm_1e-8", "C3_warm_1e-10", "D1_fresh_1e-8", "D2_fresh_1e-10"):
        deck, _ = decks.build(arm)
        assert decks.positions_block(deck) == g2
        settings = readout.deck_settings(deck)
        assert settings["calculation"] == "scf" and settings["restart_mode"] == "from_scratch"
    assert readout.deck_settings(decks.build("D1_fresh_1e-8")[0])["startingpot"] == "atomic"
    for arm, conv in (("C2_warm_1e-8", 1e-8), ("C3_warm_1e-10", 1e-10), ("D2_fresh_1e-10", 1e-10)):
        settings = readout.deck_settings(decks.build(arm)[0])
        assert settings["conv_thr"] == conv and settings["scf_must_converge"] is False
        assert settings["startingpot"] == "file" and settings["startingwfc"] == "file"
    # QE checks max_seconds only at iteration starts: a capped rung must finish (with forces)
    # well inside 7,080 s at the measured ~75 s per tight-threshold iteration.
    caps = {arm: readout.deck_settings(decks.build(arm)[0])["electron_maxstep"]
            for arm in ("C2_warm_1e-8", "C3_warm_1e-10", "D1_fresh_1e-8", "D2_fresh_1e-10")}
    assert caps == {"C2_warm_1e-8": 80, "C3_warm_1e-10": 75, "D1_fresh_1e-8": 80, "D2_fresh_1e-10": 75}
    assert all(250 + (n - 1) * 77 <= 7080 - 600 for n in caps.values())


@needs_mirror
def test_committed_decks_match_the_builder_and_the_spec():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    pins = {row["name"]: row["deck"]["sha256"] for g in spec["groups"].values() for row in g["calls"]}
    for arm in decks.ARMS:
        deck, _ = decks.build(arm)
        data = (ROOT / "runs/hea/pa_fixed_geometry_diag_2026-10-05/decks" / (arm + ".in")).read_bytes()
        assert data == deck.encode("ascii")
        assert decks.sha256_bytes(data) == pins[arm]


# ---------------------------------------------------------------- spec
def test_launch_spec_validates_and_ceilings_are_consistent():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    for group in diag.GROUPS:
        diag.validate_spec(spec, group)
    total = sum(g["max_cpu_su"] for g in spec["groups"].values())
    assert total == spec["hard_ceiling_cpu_su"] <= 2048
    for name, g in spec["groups"].items():
        assert g["time_limit_seconds"] * 128 / 3600 <= g["max_cpu_su"]
        h, m, s = (int(x) for x in g["time_limit"].split(":"))
        assert h * 3600 + m * 60 + s == g["time_limit_seconds"]
    assert spec["helper"]["sha256"] == base.sha256_file(ROOT / "src/dft/pa_catalyst_retest.py")
    assert spec["controller"]["sha256"] == base.sha256_file(ROOT / "src/dft/pa_fixed_geometry_diag.py")


@pytest.mark.parametrize("mutate", [
    lambda s: s["groups"]["replay"]["calls"].reverse(),
    lambda s: s["groups"]["ladder"]["calls"][1].update(start="checkpoint"),
    lambda s: s["groups"]["replay"]["calls"][0].update(target_cycle=3),
    lambda s: s["groups"]["fresh"].update(time_limit_seconds=16000),
    lambda s: s.update(schema="other"),
    lambda s: s["checkpoint"].update(tree_sha256="x"),
])
def test_spec_mutations_refused(mutate):
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    mutate(spec)
    with pytest.raises((diag.DiagError, base.TrialError)):
        for group in diag.GROUPS:
            diag.validate_spec(spec, group)


# ---------------------------------------------------------------- controller doubles
def allocation_text(limit="06:45:00", runtime="00:01:00"):
    values = {"JobId": "123", "Account": "che260157", "Partition": "wholenode",
              "JobState": "RUNNING", "NumNodes": "1", "NumCPUs": "128", "NumTasks": "128",
              "CPUs/Task": "1", "Requeue": "0", "TimeLimit": limit, "RunTime": runtime,
              "AllocTRES": "cpu=128,mem=200G,node=1,billing=128", "NodeList": "a001",
              "Restarts": "0", "BatchFlag": "1", "Dependency": "(null)"}
    return " ".join(k + "=" + v for k, v in values.items())


def local_spec(tmp_path, group):
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    spec["base"] = str(tmp_path / "base")
    def pin(name, text):
        path = tmp_path / "pins" / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(text.encode())
        return {"path": str(path), "sha256": base.sha256_file(path)}
    spec["pw_x"], spec["mpirun"] = pin("pw.x", "pw"), pin("mpirun", "mpi")
    spec["slurm"] = pin("91.slurm", "#!/bin/bash\n")
    spec["helper"] = {"path": str(ROOT / "src/dft/pa_catalyst_retest.py"), "sha256": spec["helper"]["sha256"]}
    spec["controller"] = {"path": str(Path(diag.__file__).resolve()), "sha256": base.sha256_file(Path(diag.__file__))}
    spec["upfs"] = [pin(f"u{i}.UPF", f"upf{i}") for i in range(5)]
    for g in spec["groups"].values():
        for row in g["calls"]:
            row["deck"] = pin(row["name"] + ".in", "deck " + row["name"] + "\n")
    checkpoint = tmp_path / "checkpoint/outdir"
    (checkpoint / "p.save").mkdir(parents=True)
    (checkpoint / "p.save/charge-density.hdf5").write_bytes(b"rho")
    (checkpoint / "p.wfc1").write_bytes(b"psi")
    (checkpoint / "p.mix1").write_bytes(b"")
    spec["checkpoint"]["outdir"] = str(checkpoint)
    spec["checkpoint"]["tree_sha256"] = base.inventory(checkpoint)["sha256"]
    return spec


class FakeRunner:
    def __init__(self, fail=(), teardown=None):
        self.fail, self.calls, self.teardown = set(fail), [], teardown or {}

    def __call__(self, *, name, argv, cwd, prefix, target_cycle, env):
        self.calls.append(name)
        assert (cwd / "input.in").read_text().startswith("deck " + name)
        assert argv[:3] == [argv[0], "-np", "128"] and argv[4:8] == ["-nk", "8", "-ndiag", "16"]
        ok = name not in self.fail
        if target_cycle is None:
            text = "End of self-consistent calculation\nForces acting on atoms\nJOB DONE.\n" if ok else "Error in routine\n"
            stop = None
        else:
            text, stop = "number of scf cycles = %d\n" % target_cycle, "registered-evaluated-boundary" if ok else "failure-marker"
        (cwd / "stdout.log").write_text(text)
        (cwd / "outdir" / (name + ".out")).write_bytes(name.encode())
        return {"returncode": 0 if ok else 1, "stop_reason": stop, "elapsed_seconds": 1.0,
                "timed_out": False, "failure_marker_observed": not ok, "HEA4_stall_observed": False,
                "solver_limit_observed": False, "within_per_call_cap": True,
                "teardown": self.teardown.get(name)}


def run_group(tmp_path, monkeypatch, group, runner, limit=None, probe=lambda: []):
    spec = local_spec(tmp_path, group)
    monkeypatch.setenv("SLURM_JOB_ID", "123")
    monkeypatch.delenv("SLURM_ARRAY_JOB_ID", raising=False)
    limit = limit or spec["groups"][group]["time_limit"]
    reader = lambda job: {"stdout": allocation_text(limit=limit), "returncode": 0}
    g = diag.Group(spec, group, runner=runner, allocation_reader=reader, process_probe=probe)
    code = g.run()
    receipt = json.loads((Path(spec["base"]) / "groups" / group / "group_receipt.json").read_text())
    return code, receipt, spec


def test_ladder_runs_in_order_from_verified_copies(tmp_path, monkeypatch):
    runner = FakeRunner()
    code, receipt, spec = run_group(tmp_path, monkeypatch, "ladder", runner)
    assert code == 0 and runner.calls == ["C1_warm_1e-6", "C2_warm_1e-8", "C3_warm_1e-10"]
    assert receipt["checkpoint_unchanged"] is True and receipt["all_calls_completed"] is True
    c3 = Path(spec["base"]) / "runs/C3_warm_1e-10/outdir"
    # C3 starts from C2's outdir, which carries C1's and C2's outputs plus the checkpoint.
    assert (c3 / "C1_warm_1e-6.out").exists() and (c3 / "C2_warm_1e-8.out").exists()
    assert (c3 / "p.save/charge-density.hdf5").read_bytes() == b"rho"


def test_failed_rung_skips_only_its_dependants(tmp_path, monkeypatch):
    runner = FakeRunner(fail={"C2_warm_1e-8"})
    code, receipt, _ = run_group(tmp_path, monkeypatch, "ladder", runner)
    assert code == 3 and runner.calls == ["C1_warm_1e-6", "C2_warm_1e-8"]
    assert [c["status"] for c in receipt["calls"]] == ["COMPLETED", "FAILED", "SKIPPED_PREDECESSOR_FAILED"]


def test_replay_failure_of_a_does_not_block_b(tmp_path, monkeypatch):
    runner = FakeRunner(fail={"A_replay"})
    code, receipt, _ = run_group(tmp_path, monkeypatch, "replay", runner)
    assert code == 3 and runner.calls == ["A_replay", "B_ethr"]
    assert [c["status"] for c in receipt["calls"]] == ["FAILED", "COMPLETED"]


def test_fresh_group_needs_no_checkpoint(tmp_path, monkeypatch):
    runner = FakeRunner()
    code, receipt, _ = run_group(tmp_path, monkeypatch, "fresh", runner)
    assert code == 0 and "checkpoint_before" not in receipt


def test_checkpoint_digest_drift_refuses_before_any_call(tmp_path, monkeypatch):
    spec = local_spec(tmp_path, "replay")
    (Path(spec["checkpoint"]["outdir"]) / "p.wfc1").write_bytes(b"changed")
    monkeypatch.setenv("SLURM_JOB_ID", "123")
    runner = FakeRunner()
    g = diag.Group(spec, "replay", runner=runner,
                   allocation_reader=lambda j: {"stdout": allocation_text(limit="04:30:00"), "returncode": 0})
    with pytest.raises(diag.DiagError):
        g.run()
    assert runner.calls == []


def test_live_time_limit_above_group_registration_refused(tmp_path, monkeypatch):
    runner = FakeRunner()
    code, receipt, _ = run_group(tmp_path, monkeypatch, "fresh", runner, limit="04:30:00")
    assert code == 3 and runner.calls == [] and receipt["scheduler_status"] == "REFUSED"


def test_insufficient_remaining_time_refuses_without_shrinking(tmp_path, monkeypatch):
    spec = local_spec(tmp_path, "fresh")
    monkeypatch.setenv("SLURM_JOB_ID", "123")
    runner = FakeRunner()
    reader = lambda j: {"stdout": allocation_text(limit="04:20:00", runtime="02:30:00"), "returncode": 0}
    code = diag.Group(spec, "fresh", runner=runner, allocation_reader=reader).run()
    assert code == 3 and runner.calls == []


def test_live_pw_process_blocks_any_launch(tmp_path, monkeypatch):
    runner = FakeRunner()
    code, receipt, _ = run_group(tmp_path, monkeypatch, "replay", runner, probe=lambda: [4242])
    assert code == 3 and runner.calls == []
    assert "live pw.x" in receipt["calls"][0]["error"] and len(receipt["calls"]) == 1


def test_incomplete_teardown_stops_the_group(tmp_path, monkeypatch):
    runner = FakeRunner(fail={"A_replay"}, teardown={"A_replay": {"unreaped_leader": True}})
    code, receipt, _ = run_group(tmp_path, monkeypatch, "replay", runner)
    assert code == 3 and runner.calls == ["A_replay"]
    assert receipt["calls"][0]["stopped_group"]


def test_solver_limit_or_cap_overrun_fails_a_call(tmp_path):
    (tmp_path / "stdout.log").write_text("End of self-consistent calculation\nForces acting on atoms\nJOB DONE.\n")
    for flags in ({"solver_limit_observed": True}, {"within_per_call_cap": False}):
        receipt = dict({"returncode": 0, "stop_reason": None}, **flags)
        assert diag.call_succeeded(receipt, tmp_path, None)[0] is False


def test_source_pin_drift_refuses_before_creating_the_group_directory(tmp_path, monkeypatch):
    spec = local_spec(tmp_path, "fresh")
    Path(spec["slurm"]["path"]).write_text("#!/bin/bash\n# drift\n")
    monkeypatch.setenv("SLURM_JOB_ID", "123")
    g = diag.Group(spec, "fresh", runner=FakeRunner(),
                   allocation_reader=lambda j: {"stdout": allocation_text(limit="04:20:00"), "returncode": 0})
    with pytest.raises(base.TrialError):
        g.run()
    assert not (Path(spec["base"]) / "groups").exists()


def test_live_pw_probe_reads_nothing_without_proc():
    if not Path("/proc").is_dir():
        assert diag.live_pw_processes() == []
    else:
        assert all(isinstance(pid, int) for pid in diag.live_pw_processes())


def test_existing_run_directory_is_never_reused(tmp_path, monkeypatch):
    spec = local_spec(tmp_path, "fresh")
    (Path(spec["base"]) / "runs/D1_fresh_1e-8").mkdir(parents=True)
    monkeypatch.setenv("SLURM_JOB_ID", "123")
    runner = FakeRunner()
    code = diag.Group(spec, "fresh", runner=runner,
                      allocation_reader=lambda j: {"stdout": allocation_text(limit="04:20:00"), "returncode": 0}).run()
    assert code == 3 and runner.calls == []


def test_copy_verified_detects_source_mutation(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a").write_bytes(b"one")
    inv = base.inventory(src)
    (src / "a").write_bytes(b"two")
    with pytest.raises(diag.DiagError):
        diag.copy_verified(src, inv, tmp_path / "dst")


@pytest.mark.parametrize("receipt,stdout,cycle,ok", [
    ({"returncode": 0, "stop_reason": "registered-evaluated-boundary"}, "", 2, True),
    ({"returncode": 0, "stop_reason": "missed-evaluated-boundary"}, "", 2, False),
    ({"returncode": 0, "stop_reason": None}, "End of self-consistent calculation\nForces acting on atoms\nJOB DONE.\n", None, True),
    ({"returncode": 0, "stop_reason": None}, "End of self-consistent calculation\nJOB DONE.\n", None, False),
    ({"returncode": 0, "stop_reason": "wall-soft-stop", "timed_out": True}, "Forces acting on atoms\n", None, False),
    ({"returncode": 2, "stop_reason": None}, "End of self-consistent calculation\nForces acting on atoms\nJOB DONE.\n", None, False),
])
def test_call_success_rules(tmp_path, receipt, stdout, cycle, ok):
    (tmp_path / "stdout.log").write_text(stdout)
    assert diag.call_succeeded(receipt, tmp_path, cycle)[0] is ok


# ---------------------------------------------------------------- readout on real QE 7.5 evidence
@needs_mirror
def test_readout_reproduces_the_banked_trial_comparisons():
    control = readout.parse_arm(TRIAL / "control", TRIAL / "control" / XML)
    candidate = readout.parse_arm(TRIAL / "candidate", TRIAL / "candidate" / XML)
    resumed = readout.parse_arm(TRIAL / "resumed", TRIAL / "resumed/checkpoint_copy" / XML)
    fresh = readout.parse_arm(TRIAL / "fresh", TRIAL / "fresh" / XML)
    banked = json.loads((ROOT / "results/pa_catalyst_retest_readout_2026-10-05/independent_analysis.json").read_text())
    for i, (a, b) in enumerate(zip(control["evaluations"], candidate["evaluations"] + resumed["evaluations"])):
        assert readout.compare(a, b)["metrics"] == banked["ordered_comparison"][i]["metrics"]
    second = readout.compare(control["evaluations"][1], resumed["evaluations"][0])["max_force_component"]
    assert (second["atom"], second["axis"]) == (20, "z")
    spread = readout.compare(candidate["evaluations"][0], fresh["evaluations"][0])["max_force_component"]
    assert spread["absolute"] == banked["warm_fresh_force_comparison"]["absolute"]
    assert fresh["evaluations"][0]["xml_scf_error_Ry"] == pytest.approx(9.80071310431723e-07, abs=1e-20)
    assert [e["first_ethr_Ry"] for e in control["evaluations"]] == [1e-5, 1e-6, 1e-6]
    assert resumed["evaluations"][0]["first_ethr_Ry"] == 1e-5
    assert control["evaluations"][1]["total_scf_correction_Ry_bohr"] == 0.003105
    # Real start records: resumed read file wfcs+density; fresh read neither; no fallback anywhere.
    assert resumed["start"] == {"wfc_from_file": True, "wfc_fallback": False, "density_from_file": True, "valid": True}
    assert fresh["start"]["valid"] and not fresh["start"]["wfc_from_file"] and not fresh["start"]["density_from_file"]
    assert candidate["start"]["valid"] and candidate["start"]["density_from_file"]


@needs_mirror
def test_readings_on_synthetic_arms_built_from_real_evaluations():
    control = readout.parse_arm(TRIAL / "control", TRIAL / "control" / XML)
    resumed = readout.parse_arm(TRIAL / "resumed", TRIAL / "resumed/checkpoint_copy" / XML)
    trial = {"control": control, "resumed": resumed}
    arms = {"A_replay": {"evaluations": resumed["evaluations"][:1]},
            "B_ethr": {"evaluations": control["evaluations"][1:3]}}
    r = readout.readings(arms, trial)
    assert r["R1_restart_path_reproducibility"]["reading"] == "REPRODUCIBLE"
    assert r["R2_startup_threshold"]["reading"] == "ETHR_RESTORES_IDENTICAL_PATH"
    arms["B_ethr"] = {"evaluations": resumed["evaluations"]}
    assert readout.readings(arms, trial)["R2_startup_threshold"]["reading"] == "ETHR_INSUFFICIENT"
    # A B that stopped after evaluation 2 is incomplete, never a scientific verdict.
    arms["B_ethr"] = {"evaluations": control["evaluations"][1:2]}
    assert readout.readings(arms, trial)["R2_startup_threshold"]["reading"] == "INCOMPLETE"


@needs_mirror
def test_readout_main_excludes_failed_or_unparseable_arms(tmp_path):
    import shutil
    runs, groups = tmp_path / "runs", tmp_path / "groups"
    a = runs / "A_replay"
    (a / "outdir/slab_c5low__pa_boundary.save").mkdir(parents=True)
    for name in ("input.in", "stdout.log"):
        shutil.copyfile(TRIAL / "resumed" / name, a / name)
    shutil.copyfile(TRIAL / "resumed/checkpoint_copy" / XML, a / XML)
    # A failed rung keeps its copied predecessor XML but has no completed SCF.
    c2 = runs / "C2_warm_1e-8"
    (c2 / "outdir/slab_c5low__pa_boundary.save").mkdir(parents=True)
    shutil.copyfile(TRIAL / "resumed/input.in", c2 / "input.in")
    (c2 / "stdout.log").write_text("Error in routine\n")
    shutil.copyfile(TRIAL / "resumed/checkpoint_copy" / XML, c2 / XML)
    for group, calls in (("replay", [{"name": "A_replay", "status": "COMPLETED"}]),
                         ("ladder", [{"name": "C2_warm_1e-8", "status": "COMPLETED"}])):
        (groups / group).mkdir(parents=True)
        (groups / group / "group_receipt.json").write_text(json.dumps({"calls": calls}))
    out = tmp_path / "readout.json"
    assert readout.main(["--trial", str(TRIAL), "--runs", str(runs), "--groups", str(groups), "--out", str(out)]) == 0
    result = json.loads(out.read_text())
    assert result["readings"]["R1_restart_path_reproducibility"]["reading"] == "REPRODUCIBLE"
    assert "C2_warm_1e-8" in result["excluded_arms"] and "C2_warm_1e-8" not in result["arms"]
    # A controller FAILED status excludes an arm even if its files would parse.
    (groups / "replay/group_receipt.json").write_text(json.dumps({"calls": [{"name": "A_replay", "status": "FAILED"}]}))
    out2 = tmp_path / "readout2.json"
    readout.main(["--trial", str(TRIAL), "--runs", str(runs), "--groups", str(groups), "--out", str(out2)])
    assert json.loads(out2.read_text())["readings"] == {}


def test_capped_rung_is_classified_from_xml_residual():
    text = "calculation = 'scf'\nconv_thr = 1.0d-10\nelectron_maxstep = 90\nscf_must_converge = .false.\n"
    s = readout.deck_settings(text)
    assert s["electron_maxstep"] == 90 and s["scf_must_converge"] is False and s["conv_thr"] == 1e-10
    # QE prints "convergence has been achieved" for a capped rung; only the XML residual tells.
    assert readout.rung_status("scf", s, 90, 2.4e-10) == "CAPPED_UNCONVERGED"
    assert readout.rung_status("scf", s, 90, 9.9e-11) == "CONVERGED"
    assert readout.rung_status("scf", s, 41, 9.9e-11) == "CONVERGED"
    assert readout.rung_status("relax", s, 90, 2.4e-10) == "CONVERGED"
