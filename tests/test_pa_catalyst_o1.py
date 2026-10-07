"""Offline checks for the O1 one-boundary re-test siblings, spec, Slurm script and readout; never launch QE/Slurm."""
import copy
import difflib
import inspect
import json
import pathlib
import sys
import types
from pathlib import Path
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
sys.path.insert(0, str(ROOT / "tests"))
import pa_catalyst_o1 as o1
import pa_catalyst_retest as retest
import pa_catalyst_o1_readout as readout
import pa_qe_adapter_o1 as adapter_o1
import pa_qe_adapter_v2 as adapter_v2

PHASE = ROOT / "results/pa_catalyst_o1_2026-10-07"
SPEC = PHASE / "launch_spec.json"
RETEST_SPEC = ROOT / "results/pa_catalyst_retest_2026-10-04/launch_spec.json"
TRIAL = ROOT / "results/pa_catalyst_retest_readout_2026-10-05/raw_mirror/trial_results"
needs_mirror = pytest.mark.skipif(not (TRIAL / "candidate/stdout.log").exists(), reason="21075231 mirror absent")


def text(path):
    return path.read_bytes().decode("utf-8")


def changed(original, sibling):
    removed, added = [], []
    for line in difflib.ndiff(original.splitlines(), sibling.splitlines()):
        if line.startswith("- "):
            removed.append(line[2:])
        elif line.startswith("+ "):
            added.append(line[2:])
    return removed, added


# ---------------------------------------------------------------- diff confinement
def test_controller_differs_from_the_frozen_retest_only_in_registered_lines():
    original, sibling = text(ROOT / "src/dft/pa_catalyst_retest.py"), text(ROOT / "src/dft/pa_catalyst_o1.py")
    removed, added = changed(original, sibling)
    assert removed == [
        '"""One licensed catalyst P-A boundary re-test; no submission or production driver.',
        "Sibling of pa_catalyst_trial.py, kept as its own pinned file so that the dated trial",
        "pinned to the original controller (job 21034683) keeps its bytes.  Same registered",
        "sequence, shape and ceilings; it binds the corrected pa_qe_adapter_v2 and the dated",
        "2026-10-04 spec, and its preflight also records the canonical XML strings expected",
        "for the deck.",
        '        "cleanup_seconds": 120, "aggregate_seconds": 57600}',
        '    if not isinstance(spec, dict) or spec.get("schema") != "pa-catalyst-retest-v1":',
        '    if spec.get("date") != "2026-10-04" or spec.get("target") != TARGET:',
        '             "time_limit_seconds": 57600, "max_cpu_su": 2048}',
        '    if not {"pa_catalyst_retest.py", "pa_qe_adapter_v2.py", "pa_checked_contract.py"}.issubset(names):',
        '    if parent.name != "sts_pa_catalyst_retest_2026-10-04" or root.parent != parent or root.name != "trial_results":',
        "                from . import pa_qe_adapter_v2 as adapter",
        "                import pa_qe_adapter_v2 as adapter",
        "            if self.clock() - self.start >= 57600:",
        '                raise TrialError("aggregate elapsed time reached 16h")',
    ]
    assert len(added) == 33
    # Every behavioural addition is the carry-over rule; the rest restate the registered identity.
    assert sum("conv_thr" in line or "carry" in line or "carried" in line for line in added) == 13
    recorded = text(PHASE / "controller_o1_vs_retest.diff")
    recomputed = "".join(difflib.unified_diff(original.splitlines(True), sibling.splitlines(True),
                                              fromfile="src/dft/pa_catalyst_retest.py", tofile="src/dft/pa_catalyst_o1.py"))
    assert recorded == recomputed


def test_adapter_differs_from_v2_only_in_the_continuity_tolerances():
    original, sibling = text(ROOT / "src/dft/pa_qe_adapter_v2.py"), text(ROOT / "src/dft/pa_qe_adapter_o1.py")
    removed, added = changed(original, sibling)
    assert removed == [
        '"""Raw QE 7.5 adapter for the bounded first-boundary catalyst experiment, version 2.',
        "    maxima = dict.fromkeys(TOLERANCES, 0.0)",
        '    return {"production_accepted": False, "evaluations": len(continuous), "tolerances": TOLERANCES.copy(),',
        '            "within_tolerances": all(maxima[key] <= TOLERANCES[key] for key in maxima)}',
    ]
    assert len(added) == 10
    recorded = text(PHASE / "adapter_o1_vs_v2.diff")
    recomputed = "".join(difflib.unified_diff(original.splitlines(True), sibling.splitlines(True),
                                              fromfile="src/dft/pa_qe_adapter_v2.py", tofile="src/dft/pa_qe_adapter_o1.py"))
    assert recorded == recomputed


def test_pinned_modules_are_lf_and_python39():
    import ast
    for rel in ("src/dft/pa_catalyst_o1.py", "src/dft/pa_qe_adapter_o1.py", "src/dft/pa_catalyst_o1_readout.py",
                "anvil/93_pa_catalyst_o1.slurm"):
        data = (ROOT / rel).read_bytes()
        assert b"\r" not in data and not any(b < 9 or 13 < b < 32 for b in data), rel
        if rel.endswith(".py"):
            ast.parse(data.decode(), feature_version=(3, 9))


# ---------------------------------------------------------------- tolerances
def test_continuity_tolerances_are_the_registered_o1_values_and_identity_tolerances_are_unchanged():
    assert adapter_o1.CONTINUITY_TOLERANCES == {"energy_Ry": 3e-5, "position_bohr": 1e-3, "force_Ry_bohr": 5e-4}
    assert adapter_o1.TOLERANCES == adapter_v2.TOLERANCES == {"energy_Ry": 1e-6, "position_bohr": 1e-5, "force_Ry_bohr": 1e-5}
    assert readout.O1_TOLERANCES == adapter_o1.CONTINUITY_TOLERANCES
    source = inspect.getsource(adapter_o1)
    compare = inspect.getsource(adapter_o1.compare_trajectories)
    assert "CONTINUITY_TOLERANCES" in compare and "TOLERANCES[" not in compare.replace("CONTINUITY_TOLERANCES[", "")
    # CONTINUITY_TOLERANCES is used nowhere else; the resume-geometry identity check keeps 1e-5 bohr.
    assert source.count("CONTINUITY_TOLERANCES") == compare.count("CONTINUITY_TOLERANCES") + 2  # docstring, definition
    assert 'warm["proposal_geometry"], TOLERANCES["position_bohr"])' in source


def evaluation(force=0.0, position=0.0, energy=0.0):
    return {"status": "CONVERGED", "settings_identity": "5" * 64, "energy_Ry": -100.0 + energy,
            "geometry": {"species": ["Co", "Cu"], "fixed_flags": [[0, 0, 0], [1, 1, 1]],
                         "cell": [[10, 0, 0], [0, 10, 0], [0, 0, 30]],
                         "positions": [[1.0 + position, 2.0, 3.0], [4.0, 5.0, 6.0]]},
            "forces_Ry_bohr": [[0.01 + force, 0.0, 0.0], [0.0, 0.0, 0.0]]}


@pytest.mark.parametrize("key,inside,outside", [
    ("force", 4.99e-4, 5.01e-4), ("position", 9.99e-4, 1.001e-3), ("energy", 2.999e-5, 3.001e-5)])
def test_compare_trajectories_applies_the_o1_bounds_inclusively(key, inside, outside):
    continuous = [evaluation() for _ in range(3)]
    for value, expected in ((inside, True), (outside, False)):
        split = [evaluation(), evaluation(**{key: value}), evaluation()]
        result = adapter_o1.compare_trajectories(continuous, split)
        assert result["within_tolerances"] is expected
        assert result["tolerances"] == adapter_o1.CONTINUITY_TOLERANCES
    # The same small difference fails the frozen 21075231 gate.
    assert adapter_v2.compare_trajectories(continuous, [evaluation(), evaluation(**{key: inside}), evaluation()])[
        "within_tolerances"] is False


# ---------------------------------------------------------------- spec
def posix_validate(module, spec):
    original, module.Path = module.Path, pathlib.PurePosixPath  # the spec holds Linux paths
    try:
        return module.validate_spec(spec)
    finally:
        module.Path = original


def test_checked_in_o1_spec_validates_and_pins_the_local_bytes():
    spec = posix_validate(o1, json.loads(SPEC.read_text(encoding="utf-8")))
    names = {Path(pin["path"]).name: pin["sha256"] for pin in spec["dependencies"]}
    for rel in ("src/dft/pa_catalyst_o1.py", "src/dft/pa_qe_adapter_o1.py", "src/dft/pa_checked_contract.py",
                "anvil/93_pa_catalyst_o1.slurm"):
        assert names[Path(rel).name] == o1.sha256_file(ROOT / rel), rel
    assert spec["trial_parent"] == "/anvil/projects/x-che260157/sts_pa_catalyst_o1_2026-10-07"
    assert spec["allocation"]["time_limit_seconds"] == 28800 and spec["allocation"]["max_cpu_su"] == 1024
    assert spec["caps"] == o1.CAPS and o1.CAPS["aggregate_seconds"] == 28800
    assert 28800 * 128 / 3600 == 1024 and spec["optional_negative_control"] is True


def test_o1_spec_keeps_every_scientific_pin_of_the_retest():
    spec, old = json.loads(SPEC.read_text()), json.loads(RETEST_SPEC.read_text())
    for key in ("target", "pw_x", "mpirun", "upfs", "initial_seed", "parallel_shape"):
        assert spec[key] == old[key], key
    assert spec["source_deck"]["sha256"] == old["source_deck"]["sha256"]
    assert spec["source_review"]["sha256"] == old["source_review"]["sha256"]
    assert spec["preflight_replay"]["files"] == old["preflight_replay"]["files"]
    assert spec["preflight_replay"]["expected"] == old["preflight_replay"]["expected"]
    contract_old = next(p for p in old["dependencies"] if p["path"].endswith("pa_checked_contract.py"))
    contract_new = next(p for p in spec["dependencies"] if p["path"].endswith("pa_checked_contract.py"))
    assert contract_old["sha256"] == contract_new["sha256"]
    parent = spec["trial_parent"] + "/"
    for path in [spec["source_deck"]["path"], spec["source_review"]["path"], spec["preflight_replay"]["root"]] + \
            [pin["path"] for pin in spec["dependencies"]]:
        assert path.startswith(parent), path
    assert "sts_pa_catalyst_retest_2026-10-04" not in json.dumps({k: v for k, v in spec.items() if k != "predecessor"})


@pytest.mark.parametrize("mutate", [
    lambda s: s.update(schema="pa-catalyst-retest-v1"),
    lambda s: s.update(date="2026-10-04"),
    lambda s: s.update(trial_parent="/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04",
                       trial_root="/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04/trial_results"),
    lambda s: s["allocation"].update(time_limit_seconds=57600),
    lambda s: s["allocation"].update(max_cpu_su=2048),
    lambda s: s["caps"].update(aggregate_seconds=57600),
    lambda s: [p.update(path=p["path"].replace("pa_qe_adapter_o1.py", "pa_qe_adapter_v2.py")) for p in s["dependencies"]],
    lambda s: [p.update(path=p["path"].replace("pa_catalyst_o1.py", "pa_catalyst_retest.py")) for p in s["dependencies"]],
])
def test_o1_spec_mutations_refused(mutate):
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    mutate(spec)
    with pytest.raises(o1.TrialError):
        posix_validate(o1, spec)


def test_frozen_retest_controller_refuses_the_o1_spec():
    with pytest.raises(retest.TrialError):
        posix_validate(retest, json.loads(SPEC.read_text(encoding="utf-8")))


def test_slurm_script_matches_spec_and_controller():
    script = text(ROOT / "anvil/93_pa_catalyst_o1.slurm")
    spec = json.loads(SPEC.read_text())
    assert "#SBATCH --time=08:00:00" in script and "#SBATCH --job-name=pa-catalyst-o1" in script
    assert "TRIAL_PARENT=" + spec["trial_parent"] in script
    assert 'PHASE="$TRIAL_PARENT/results/pa_catalyst_o1_2026-10-07"' in script
    assert '"$TRIAL_PARENT/src/dft/pa_catalyst_o1.py"' in script and "retest" not in script
    assert "--no-requeue" in script and "STS_PA_SPEC_SHA256" in script


# ---------------------------------------------------------------- conv_thr carry-over
@needs_mirror
def test_carry_over_on_the_real_candidate_log():
    resumed = adapter_o1.parse_deck(TRIAL / "resumed/input.in")["conv_thr_Ry"]
    carry = o1.conv_thr_carry(TRIAL / "candidate/stdout.log", resumed)
    assert carry == {"candidate_last_new_conv_thr_Ry": 1e-6, "resumed_deck_conv_thr_Ry": 1e-6,
                     "new_conv_thr_lines": 1, "equal": True}
    # The control continued past the boundary and had tightened to 6.87e-8: unequal.
    assert o1.conv_thr_carry(TRIAL / "control/stdout.log", resumed)["equal"] is False


def test_carry_over_missing_or_unequal(tmp_path):
    log = tmp_path / "stdout.log"
    log.write_text("     total energy = -1 Ry\n")
    assert o1.conv_thr_carry(log, 1e-6) == {"candidate_last_new_conv_thr_Ry": None, "resumed_deck_conv_thr_Ry": 1e-6,
                                            "new_conv_thr_lines": 0, "equal": False}
    log.write_text("     new conv_thr            =       0.0000010000 Ry\n     new conv_thr            =       0.0000000835 Ry\n")
    assert o1.conv_thr_carry(log, 1e-6)["candidate_last_new_conv_thr_Ry"] == 8.35e-8
    assert o1.conv_thr_carry(log, 1e-6)["equal"] is False


def geometry(value):
    return {"unit": "bohr", "species": ["Cu"], "positions": [[value, 0, 0]],
            "cell": [[10, 0, 0], [0, 10, 0], [0, 0, 10]], "fixed_flags": [[0, 0, 0]]}


def spec_for(tmp_path):
    parent = tmp_path / "sts_pa_catalyst_o1_2026-10-07"
    parent.mkdir()
    spec = json.loads(SPEC.read_text())
    spec["trial_parent"], spec["trial_root"] = str(parent), str(parent / "trial_results")
    return spec


class Double(o1.Trial):
    """Orchestration double: no QE, no Slurm; records the call order and writes the candidate log."""
    def __init__(self, spec, *, carry_line, within=True):
        self.spec, self.root, self.calls, self.active = spec, Path(spec["trial_root"]), 0, False
        self.clock, self.start, self.order = lambda: 1, 0, []
        self.carry_line = carry_line
        # The real Trial records the spec date (controller line ~766); the double does the same.
        self.receipt = {"date": spec["date"], "calls": [], "scientific_status": "INCONCLUSIVE",
                        "scheduler_status": "COMPLIANT", "production_accepted": False}
        self.adapter = types.SimpleNamespace(
            contract=adapter_o1.contract, _validate_arm=Mock(),
            read_bfgs=lambda *args, **kwargs: {"scf_count": 1, "bfgs_count": 1},
            checkpoint_inventory=lambda out, wave=None: o1.checkpoint_inventory(Path(out), Path(wave) if wave else None),
            pre_resume_decision=lambda *args, **kwargs: {"action": "RESUME_CANDIDATE", "production_accepted": False},
            audit_consumption=lambda *args, **kwargs: {"raw_consumption_audit": {"passed": True}},
            compare_trajectories=lambda left, right: {"within_tolerances": within, "evaluations": len(left),
                                                      "tolerances": dict(adapter_o1.CONTINUITY_TOLERANCES)},
            parse_deck=lambda path: {"conv_thr_Ry": 1e-6})

    def common_upfs(self):
        pass

    def verify_sources(self):
        pass

    def execute(self, name, **kwargs):
        self.order.append(name)
        self.calls += 1
        self.receipt["calls"].append({"name": name, "status": "NUMERICAL_RECEIPT_VALIDATED"})
        arm = self.root / name
        outdir = arm / "outdir"
        outdir.mkdir(parents=True)
        (outdir / "data.xml").write_bytes(b"xml")
        (arm / "input.in").write_text("deck\n")
        if name == "candidate":
            (arm / "stdout.log").write_text(self.carry_line)
        frames = [{"geometry": geometry(c - 1), "energy_Ry": -100 + c} for c in kwargs["expected_cycles"]] or \
            [{"geometry": geometry(0), "energy_Ry": -100}]
        return {"raw": {"evaluations": frames, "proposal_geometry": geometry(1)}, "outdir": str(outdir),
                "wfcdir": None, "input_path": str(arm / "input.in")}


def thaw(path):
    if path.exists():
        for child in path.rglob("*"):
            child.chmod(0o700 if child.is_dir() else 0o600)
        path.chmod(0o700)


@pytest.mark.parametrize("line,within,status,order_tail", [
    ("     new conv_thr            =       0.0000010000 Ry\n", True, "PASS_ONE_BOUNDARY", ["resumed", "negative"]),
    ("     no threshold printed\n", True, "INCONCLUSIVE", ["resumed"]),
    ("     new conv_thr            =       0.0000000835 Ry\n", True, "INCONCLUSIVE", ["resumed"]),
    ("     new conv_thr            =       0.0000010000 Ry\n", False, "INCONCLUSIVE", ["resumed"]),
])
def test_carry_over_gates_the_verdict_before_the_negative_control(tmp_path, monkeypatch, line, within, status, order_tail):
    monkeypatch.setattr(o1, "preflight", lambda *args: {"status": "PREFLIGHT_PASS"})
    harness = Double(spec_for(tmp_path), carry_line=line, within=within)
    try:
        result = harness.run()
        assert result["scientific_status"] == status
        assert harness.order == ["control", "candidate", "fresh"] + order_tail
        assert "conv_thr_carry" in result and "continuity" in result
        if status == "PASS_ONE_BOUNDARY":
            assert result["conv_thr_carry"]["equal"] is True
        reading = readout.registered_reading(result)["reading"]
        expected = {"PASS_ONE_BOUNDARY": "CONTINUITY_PASS"}.get(status, "CONTINUITY_FAIL" if not within else "INCONCLUSIVE")
        assert reading == expected
    finally:
        thaw(harness.root)


# ---------------------------------------------------------------- readout
@needs_mirror
def test_readout_reproduces_the_historical_21075231_numbers(tmp_path):
    out = tmp_path / "historical.json"
    assert readout.main(["--trial", str(TRIAL), "--out", str(out), "--historical"]) == 0
    result = json.loads(out.read_text())
    assert result["historical"] is True and "not an O1 result" in result["label"]
    # The historical receipt has no carry record and its own (frozen) tolerances: never a PASS.
    assert result["registered"]["reading"] == "INCONCLUSIVE"
    assert result["registered"]["tolerances_in_force"] == adapter_v2.TOLERANCES
    rows = result["informative"]["evaluations"]
    assert rows[1]["metrics"]["force_Ry_bohr"] == 1.1464205365793734e-4
    assert (rows[1]["max_force_component"]["species"], rows[1]["max_force_component"]["atom"],
            rows[1]["max_force_component"]["axis"]) == ("Co", 20, "z")
    assert result["informative"]["all_within_O1"] is True
    assert all(row["same_state_by_traces"] for row in rows)


def test_registered_reading_rules():
    tolerances = dict(readout.O1_TOLERANCES)
    base = {"date": "2026-10-07", "scientific_status": "PASS_ONE_BOUNDARY",
            "continuity": {"within_tolerances": True, "tolerances": tolerances},
            "conv_thr_carry": {"equal": True}, "pre_resume_decision": {"action": "RESUME_CANDIDATE"},
            "calls": [{"name": n, "status": "NUMERICAL_RECEIPT_VALIDATED"}
                      for n in ("control", "candidate", "fresh", "resumed", "negative")]}
    assert readout.registered_reading(base)["reading"] == "CONTINUITY_PASS"
    fail = copy.deepcopy(base)
    fail.update(scientific_status="INCONCLUSIVE", continuity={"within_tolerances": False, "tolerances": tolerances})
    assert readout.registered_reading(fail)["reading"] == "CONTINUITY_FAIL"
    no_negative = copy.deepcopy(base)
    no_negative["calls"] = no_negative["calls"][:-1]
    for change in ({"conv_thr_carry": {"equal": False}}, {"conv_thr_carry": None},
                   {"pre_resume_decision": {"action": "RESEED_CANDIDATE"}, "scientific_status": "RESEED_BRANCH_ONLY"},
                   {"pre_resume_decision": {"action": "HOLD"}, "scientific_status": "HOLD"},
                   {"scientific_status": "INCONCLUSIVE", "error": "negative control lacks actual startup deletion"},
                   # A verdict is only read from this dated run under the registered O1 tolerances.
                   {"date": "2026-10-04"},
                   {"continuity": {"within_tolerances": True, "tolerances": dict(adapter_v2.TOLERANCES)}},
                   {"continuity": {"within_tolerances": True}},
                   {"calls": no_negative["calls"]}):
        value = copy.deepcopy(base)
        value.update(change)
        assert readout.registered_reading(value)["reading"] == "INCONCLUSIVE", change
    stale = copy.deepcopy(fail)
    stale["continuity"]["tolerances"] = dict(adapter_v2.TOLERANCES)
    assert readout.registered_reading(stale)["reading"] == "INCONCLUSIVE"
