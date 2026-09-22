"""The checked runner: the full seeded-runner suite bound to research_batch_checked (scratch-seed
guards and the relaxation stage kind included) plus the checked relaxation stage kind.

No real process or signal is sent.  Corruption tests exercise the actual public
validation/run paths; process-lifecycle tests use deterministic process doubles.
"""
import copy
import hashlib
import json
from pathlib import Path
import signal
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import research_batch_checked as batch
import hea_panel_readout

SCF = """Program PWSCF
number of atoms/cell = 2
!    total energy = -10.00000000 Ry
convergence has been achieved in 3 iterations
JOB DONE.
"""
PROJECTION = """Lowdin Charges:
 Atom # 1: total charge = 6.0000, s = 2.0000, d = 4.0000,
 spin up = 4.0000, s = 1.0000, d = 3.0000,
 spin down = 2.0000, s = 1.0000, d = 1.0000,
 polarization = 2.0000, s = 0.0000, d = 2.0000,
 Atom # 2: total charge = 6.0000, s = 2.0000, p = 4.0000,
 spin up = 3.0000, s = 1.0000, p = 2.0000,
 spin down = 3.0000, s = 1.0000, p = 2.0000,
 polarization = 0.0000, s = 0.0000, p = 0.0000,
 Spilling Parameter: 0.0022
 JOB DONE.
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def approved(tmp_path):
    directory = tmp_path / "runs/unit"
    directory.mkdir(parents=True)
    pseudo = tmp_path / "pseudo"
    pseudo.mkdir()
    upf = pseudo / "H.UPF"
    upf.write_bytes(b"unit pseudopotential bytes")
    deck = directory / "point.in"
    deck.write_text("""&CONTROL
 calculation = 'scf'
 prefix = 'point'
 outdir = './tmp'
 pseudo_dir = './pseudo'
/
&SYSTEM
 nat = 2
/
ATOMIC_SPECIES
H 1.008 H.UPF
ATOMIC_POSITIONS angstrom
H 0 0 0 0 0 0
H 0 0 1 1 1 1
""", encoding="utf-8", newline="\n")
    helper = tmp_path / "helper.py"
    helper.write_text("# pinned dependency\n", encoding="utf-8", newline="\n")
    projection_helper = tmp_path / "src/dft/projection_qc.py"
    projection_helper.parent.mkdir(parents=True)
    projection_helper.write_bytes((ROOT / "src/dft/projection_qc.py").read_bytes())
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("# approved unit fixture\n# NP=128 NCONC=1\nunit point .in 1\n", encoding="utf-8", newline="\n")
    spec = {"schema": "research-batch-2026-09-16",
            "files": {"helper.py": sha(helper), "manifest.txt": sha(manifest),
                      "src/dft/projection_qc.py": sha(projection_helper)},
            "pseudo_md5": {"H.UPF": hashlib.md5(upf.read_bytes()).hexdigest()},
            "stages": {"pilot": {"kind": "hea", "manifest": "manifest.txt", "jobs": [
                {"dir": "unit", "job": "point", "nk": 1, "sha256": sha(deck),
                 "scf_seconds": 60, "projection_seconds": 60, "max_iterations": 126}]}}}
    return spec, tmp_path, pseudo, directory


def test_approved_inputs_pass_without_modifying_any_input(approved):
    spec, root, pseudo, directory = approved
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)["kind"] == "hea"
    assert before == {p: p.read_bytes() for p in before}
    assert not (directory / "tmp_point").exists()


@pytest.mark.parametrize("target", ["helper.py", "src/dft/projection_qc.py", "runs/unit/point.in", "pseudo/H.UPF"])
def test_drift_in_any_executed_input_is_refused_before_scratch(approved, target):
    spec, root, pseudo, directory = approved
    with (root / target).open("ab") as handle:
        handle.write(b"changed")
    with pytest.raises(ValueError):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


@pytest.mark.parametrize("suffix", [".out", ".run.in", ".qc.json", ".KILLED", ".REJECTED", ".projwfc.out"])
def test_restart_never_overwrites_prior_evidence(approved, suffix):
    spec, root, pseudo, directory = approved
    artifact = directory / ("point" + suffix)
    artifact.write_bytes(b"prior evidence")
    with pytest.raises(ValueError, match="prior artifact"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert artifact.read_bytes() == b"prior evidence"


def test_preexisting_density_directory_blocks_duplicate_spend(approved):
    spec, root, pseudo, directory = approved
    (directory / "tmp_point").mkdir()
    with pytest.raises(ValueError, match="prior scratch"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)


def test_manifest_cannot_change_job_identity_even_with_new_manifest_hash(approved):
    spec, root, pseudo, _ = approved
    manifest = root / "manifest.txt"
    manifest.write_text("# NP=128 NCONC=1\nunit different .in 1\n", encoding="utf-8", newline="\n")
    spec["files"]["manifest.txt"] = sha(manifest)
    with pytest.raises(ValueError, match="identity/order"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)


@pytest.mark.parametrize("row", [0, 2, -1, True, 1.0])
def test_array_index_cannot_select_a_different_or_missing_job(approved, row):
    spec, root, pseudo, _ = approved
    with pytest.raises(ValueError, match="task index"):
        batch.validate(spec, root, "pilot", row=row, pseudo=pseudo)


def test_clean_scf_accepts_fortran_exponent():
    result = batch.scf_check(SCF.replace("-10.00000000", "-1.000000000D+01"))
    assert result == {"energy_Ry": -10.0, "iterations": 3}


@pytest.mark.parametrize("mutation", [
    lambda s: s.replace("JOB DONE.", ""),
    lambda s: s + s,
    lambda s: s + "convergence NOT achieved after 300 iterations\n",
    lambda s: s + "Error in routine electrons (1)\n",
    lambda s: s + "IEEE_INVALID_FLAG\n",
    lambda s: s.replace("-10.00000000", "1e999"),
])
def test_no_energy_is_salvaged_from_failed_or_concatenated_attempts(mutation):
    with pytest.raises(ValueError):
        batch.scf_check(mutation(SCF))


def test_complete_projection_is_accepted():
    batch.projection_check(PROJECTION, 2)


@pytest.mark.parametrize("mutation", [
    lambda s: s.replace("Atom # 2", "Atom # 1"),
    lambda s: s.replace("JOB DONE.", ""),
    lambda s: s + "Error in routine projwave\n",
    lambda s: s.replace("total charge = 6.0000", "total charge = Inf", 1),
    lambda s: s.replace("total charge = 6.0000", "total charge = 1e999", 1),
    lambda s: s.replace("Spilling Parameter: 0.0022", "Spilling Parameter: 1e999"),
    lambda s: s.replace("polarization = 2.0000", "polarization = *****"),
])
def test_projection_requires_finite_complete_numerical_results(mutation):
    with pytest.raises(ValueError):
        batch.projection_check(mutation(PROJECTION), 2)


def test_stop_process_escalates_to_kill_if_term_does_not_finish(monkeypatch):
    signals = []

    class Process:
        pid = 43210
        returncode = None

        def poll(self):
            return self.returncode

        def wait(self, timeout):
            if len(signals) == 1:
                raise batch.subprocess.TimeoutExpired("fake-mpirun", timeout)
            self.returncode = -9
            return self.returncode

    monkeypatch.setattr(batch.os, "killpg", lambda pid, sig: signals.append((pid, sig)), raising=False)
    # Windows lacks SIGKILL; this runner targets the remote Linux executor.
    monkeypatch.setattr(batch.signal, "SIGKILL", 9, raising=False)
    process = Process()
    batch.stop_process(process)
    assert signals == [(43210, signal.SIGTERM), (43210, 9)]
    assert process.returncode == -9


def test_exit_race_during_kill_is_cleaned_up_not_reported_as_runner_crash(monkeypatch):
    class Process:
        pid = 43210
        returncode = None

        def poll(self):
            return self.returncode

        def wait(self, timeout):
            self.returncode = 0
            return 0

    def disappeared(pid, sig):
        raise ProcessLookupError("exited between poll and signal")

    monkeypatch.setattr(batch.os, "killpg", disappeared, raising=False)
    process = Process()
    batch.stop_process(process)
    assert process.returncode == 0


def test_launch_error_leaves_durable_rejected_qc_and_retains_scratch(approved, monkeypatch):
    spec, root, pseudo, directory = approved

    def unavailable(*args, **kwargs):
        raise OSError("mpirun unavailable")

    monkeypatch.setattr(batch, "execute", unavailable)
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") != 0
    qc = json.loads((directory / "point.qc.json").read_text(encoding="utf-8"))
    assert qc["status"] == "REJECTED"
    assert "mpirun unavailable" in qc["reason"]
    assert (directory / "point.REJECTED").is_file()
    assert (directory / "tmp_point").is_dir()
    assert sha(directory / "point.in") == spec["stages"]["pilot"]["jobs"][0]["sha256"]


@pytest.fixture
def gated_release(approved):
    spec, root, pseudo, directory = approved
    prior_dir = root / "runs/preflight"
    prior_dir.mkdir()
    prior_jobs = []
    for name in ("slab", "H2", "H2O"):
        source = prior_dir / (name + ".in")
        source.write_text("approved prior source " + name, encoding="utf-8", newline="\n")
        runtime = prior_dir / (name + ".run.in")
        runtime.write_text("actual prior runtime " + name, encoding="utf-8", newline="\n")
        output = prior_dir / (name + ".out")
        output.write_text(SCF + "validated ensemble " + name, encoding="utf-8", newline="\n")
        prior = {"dir": "preflight", "job": name, "sha256": sha(source)}
        prior_jobs.append(prior)
        receipt = {"status": "COMPLETE", "stage": "beef_preflight", "job": name,
                   "input_sha256": sha(source), "output_sha256": sha(output),
                   "runtime_sha256": sha(runtime), "ensemble_check": {"rc": 0}}
        (prior_dir / (name + ".qc.json")).write_text(json.dumps(receipt), encoding="utf-8", newline="\n")
    spec["stages"]["beef_preflight"] = {"kind": "beef", "jobs": prior_jobs}
    spec["stages"]["pilot"]["requires_complete"] = ["beef_preflight"]
    return spec, root, pseudo, directory, prior_dir


def test_all_three_verified_preflight_results_release_production(gated_release):
    spec, root, pseudo, directory, _ = gated_release
    batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


@pytest.mark.parametrize("name", ["slab", "H2", "H2O"])
def test_each_missing_preflight_result_blocks_the_entire_release(gated_release, name):
    spec, root, pseudo, directory, prior_dir = gated_release
    (prior_dir / (name + ".qc.json")).unlink()
    with pytest.raises((ValueError, OSError)):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


@pytest.mark.parametrize("suffix", [".out", ".run.in"])
def test_complete_receipt_does_not_authorize_changed_preflight_artifacts(gated_release, suffix):
    spec, root, pseudo, directory, prior_dir = gated_release
    with (prior_dir / ("H2O" + suffix)).open("ab") as handle:
        handle.write(b"later change")
    with pytest.raises(ValueError, match="prerequisite"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


@pytest.mark.parametrize("change", [
    {"status": "REJECTED"},
    {"input_sha256": "wrong approved deck"},
    {"ensemble_check": {"rc": 2}},
    {"output_sha256": None},
    {"runtime_sha256": None},
])
def test_unverified_receipt_never_releases_the_eleven_remaining_jobs(gated_release, change):
    spec, root, pseudo, directory, prior_dir = gated_release
    path = prior_dir / "H2.qc.json"
    receipt = json.loads(path.read_text(encoding="utf-8"))
    receipt.update(change)
    path.write_text(json.dumps(receipt), encoding="utf-8", newline="\n")
    with pytest.raises(ValueError, match="prerequisite"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


@pytest.mark.parametrize("output_text,clock_values,max_iterations,expected", [
    ("iteration # 1\n", [0, 61, 62], 126, "wall-time ceiling"),
    ("iteration # 127\n", [0, 1, 2], 126, "SCF iteration ceiling"),
    ("Error in routine electrons\n", [0, 1, 2], 126, "numerical failure marker"),
])
def test_watchdog_requests_clean_exit_and_reports_reason_without_retry(
        tmp_path, monkeypatch, output_text, clock_values, max_iterations, expected):
    launches = []
    waits = []

    class Process:
        pid = 43210
        returncode = None

        def poll(self):
            return self.returncode

        def wait(self, timeout):
            waits.append(timeout)
            self.returncode = 0
            return 0

    def launch(command, **kwargs):
        launches.append(command)
        kwargs["stdout"].write(output_text.encode())
        kwargs["stdout"].flush()
        return Process()

    ticks = iter(clock_values)
    monkeypatch.setattr(batch.subprocess, "Popen", launch)
    monkeypatch.setattr(batch.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(batch.time, "sleep", lambda _: pytest.fail("watchdog failed to stop promptly"))
    exitfile = tmp_path / "point.EXIT"
    result = batch.execute(["fake-mpirun"], tmp_path / "point.out", tmp_path, {}, 60,
                           max_iterations=max_iterations, exitfile=exitfile)
    assert result["stop_reason"] == expected
    assert result["rc"] == 0  # clean process exit does not erase the stop reason
    assert exitfile.is_file()
    assert launches == [["fake-mpirun"]]
    assert waits == [30]



def test_projection_dependency_requires_an_explicit_source_pin(approved):
    spec, root, pseudo, directory = approved
    del spec["files"]["src/dft/projection_qc.py"]
    with pytest.raises(ValueError, match="projection validator dependency not pinned"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


def test_different_staged_helper_cannot_substitute_for_the_executed_helper(approved):
    spec, root, pseudo, directory = approved
    helper = root / "src/dft/projection_qc.py"
    helper.write_text("# a different approved-looking helper\n")
    spec["files"]["src/dft/projection_qc.py"] = sha(helper)
    with pytest.raises(ValueError, match="executed projection validator differs from pin"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


def test_production_projection_validator_accepts_real_nonmagnetic_shape():
    text = """state # 1: atom 1 (Ru ), wfc 3 (l=2 m= 1)
Lowdin Charges:
 Atom # 1: total charge = 15.4891, s = 2.3266,
 Atom # 1: total charge = 15.4891, p = 6.7605, pz=2.2044, px=2.2999, py=2.2563,
 Atom # 1: total charge = 15.4891, d = 6.4020, dz2=0.8555, dxz=1.5295, dyz=1.4677, dx2-y2=1.7809, dxy=0.7684,
 Spilling Parameter: 0.0018
 JOB DONE.
"""
    result = batch.projection_check(text, 1)
    assert result["format"] == "split-angular-channels"
    assert result["charge_rows"] == 3
    with pytest.raises(ValueError, match="angular channel"):
        batch.projection_check("\n".join(line for line in text.splitlines() if " p = " not in line), 1)


def test_production_projection_validator_uses_shared_failure_guards():
    for suffix in ("IEEE_UNKNOWN_EXCEPTION_FLAG\n", "IEEE_INVALID_FLAG\n", "JOB DONE.\n"):
        with pytest.raises(ValueError):
            batch.projection_check(PROJECTION + suffix, 2)


SEED = {"charge-density.hdf5": b"retained density", "data-file-schema.xml": b"<qes/>",
        "occup.txt": b"hubbard ns", "paw.txt": b"becsum"}


def seeded(approved):
    spec, root, pseudo, directory = approved
    save = root / "runs/prior/tmp_prior/prior.save"
    save.mkdir(parents=True)
    for name, data in SEED.items():
        (save / name).write_bytes(data)
    deck = directory / "point.in"
    deck.write_text(deck.read_text(encoding="utf-8").replace(" prefix = 'point'\n",
                    " prefix = 'point'\n startingpot = 'file'\n"), encoding="utf-8", newline="\n")
    job = spec["stages"]["pilot"]["jobs"][0]
    job["sha256"] = sha(deck)
    job["scratch_source"] = {"save_dir": "runs/prior/tmp_prior/prior.save",
                             "files": {name: sha(save / name) for name in SEED}}
    return spec, root, pseudo, directory, save, job


def test_scratch_source_is_copied_and_verified_before_execution(approved, monkeypatch):
    spec, root, pseudo, directory, save, job = seeded(approved)
    seen = {}

    def observe(command, output, cwd, env, seconds, max_iterations=None, exitfile=None):
        seen["copied"] = {p.name: p.read_bytes() for p in (directory / "tmp_point/point.save").iterdir()}
        raise OSError("observed, not executed")

    monkeypatch.setattr(batch, "execute", observe)
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") != 0
    assert seen["copied"] == SEED
    qc = json.loads((directory / "point.qc.json").read_text(encoding="utf-8"))
    assert qc["scratch_source"]["copied"] == job["scratch_source"]["files"]
    assert qc["scratch_source"]["bytes"] == sum(len(v) for v in SEED.values())
    assert {p.name: p.read_bytes() for p in save.iterdir()} == SEED


@pytest.mark.parametrize("name", ["charge-density.hdf5", "occup.txt"])
def test_drifted_scratch_source_is_refused_before_scratch_and_execution(approved, monkeypatch, name):
    spec, root, pseudo, directory, save, job = seeded(approved)
    (save / name).write_bytes(b"changed after pinning")
    monkeypatch.setattr(batch, "execute", lambda *a, **k: pytest.fail("executed despite drift"))
    with pytest.raises(ValueError, match="scratch source file drifted"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


def test_scratch_source_requires_a_deck_that_reads_it(approved):
    spec, root, pseudo, directory, save, job = seeded(approved)
    deck = directory / "point.in"
    deck.write_text(deck.read_text(encoding="utf-8").replace(" startingpot = 'file'\n", ""),
                    encoding="utf-8", newline="\n")
    job["sha256"] = sha(deck)
    with pytest.raises(ValueError, match="does not read it"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)


def test_missing_density_pin_is_refused(approved):
    spec, root, pseudo, directory, save, job = seeded(approved)
    del job["scratch_source"]["files"]["charge-density.hdf5"]
    with pytest.raises(ValueError, match="must pin the density"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)


RELAXATION = """Program PWSCF
number of atoms/cell = 2
iteration #  1
iteration # 20
!    total energy = -10.00000000 Ry
convergence has been achieved in 20 iterations
iteration #  1
iteration # 12
!    total energy = -1.050000000D+01 Ry
convergence has been achieved in 12 iterations
bfgs converged in 2 scf cycles and 1 bfgs steps
Final energy = -10.5000000000 Ry
JOB DONE.
"""


def relaxed(approved):
    """The unit fixture as a one-leg relaxation stage: relax deck, kind "relax", leg wall above the SCF bound."""
    spec, root, pseudo, directory = approved
    deck = directory / "point.in"
    deck.write_text(deck.read_text(encoding="utf-8").replace(" calculation = 'scf'\n", " calculation = 'relax'\n"),
                    encoding="utf-8", newline="\n")
    stage = spec["stages"]["pilot"]
    stage["kind"] = "relax"
    job = stage["jobs"][0]
    job["sha256"] = sha(deck)
    job["scf_seconds"] = 50000
    return spec, root, pseudo, directory, job


def relaxation_doubles(monkeypatch, output_text, status="CONVERGED"):
    """pw.x writes output_text and a retained density; projwfc writes PROJECTION; the readout is a stub."""
    calls, seen = [], {}

    def execute(command, output, cwd, env, seconds, max_iterations=None, exitfile=None):
        calls.append({"command": command, "seconds": seconds, "max_iterations": max_iterations})
        if len(calls) == 1:
            output.write_text(output_text, encoding="utf-8", newline="\n")
            save = exitfile.parent / "point.save"
            save.mkdir()
            (save / "data-file-schema.xml").write_text("<qes/>", encoding="utf-8")
            (save / "charge-density.dat").write_bytes(b"density")
        else:
            output.write_text(PROJECTION, encoding="utf-8", newline="\n")
        return {"rc": 0, "stop_reason": None, "wall_seconds": 11}

    def parse_out(path, *, allow_relax=False):
        seen["path"], seen["allow_relax"] = Path(path), allow_relax
        return {"status": status}

    monkeypatch.setattr(batch, "execute", execute)
    monkeypatch.setattr(hea_panel_readout, "parse_out", parse_out)
    return calls, seen


@pytest.mark.parametrize("kind,seconds,accepted", [
    ("relax", 50000, True), ("relax", 60000, True), ("relax", 60001, False),
    ("hea", 50000, False), ("hea", 19000, True),
])
def test_relaxation_leg_wall_is_admitted_only_for_the_relax_kind(approved, kind, seconds, accepted):
    spec, root, pseudo, directory = approved
    if kind == "relax":
        spec, root, pseudo, directory, _ = relaxed(approved)
    job = spec["stages"]["pilot"]["jobs"][0]
    job["scf_seconds"] = seconds
    if accepted:
        assert batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)["kind"] == kind
    else:
        with pytest.raises(ValueError, match="bounded runtime"):
            batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


def test_relax_stage_refuses_a_fixed_geometry_deck(approved):
    spec, root, pseudo, directory = approved
    spec["stages"]["pilot"]["kind"] = "relax"
    with pytest.raises(ValueError, match="calculation.*expected 'relax'"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


def test_fixed_geometry_stage_refuses_a_relaxation_deck(approved):
    spec, root, pseudo, directory, job = relaxed(approved)
    spec["stages"]["pilot"]["kind"] = "hea"
    job["scf_seconds"] = 60
    with pytest.raises(ValueError, match="calculation.*expected 'scf'"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)


def test_relax_stage_requires_the_registered_iteration_ceiling(approved):
    spec, root, pseudo, directory, job = relaxed(approved)
    job["max_iterations"] = 200
    with pytest.raises(ValueError, match="126"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)


def test_converged_relaxation_is_projected_and_banked_complete(approved, monkeypatch):
    spec, root, pseudo, directory, job = relaxed(approved)
    calls, seen = relaxation_doubles(monkeypatch, RELAXATION)
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 0
    qc = json.loads((directory / "point.qc.json").read_text(encoding="utf-8"))
    assert qc["status"] == "COMPLETE"
    assert qc["relaxation"] == {"status": "CONVERGED", "maximum_scf_iteration": 20, "bfgs_converged": True,
                                "final_energy_Ry": -10.5, "ionic_steps": 2}
    assert seen == {"path": directory / "point.out", "allow_relax": True}
    assert [c["seconds"] for c in calls] == [50000, 60] and calls[0]["max_iterations"] == 126
    assert any(str(part).endswith("projwfc.x") for part in calls[1]["command"])
    assert not {"scf", "force", "complete_audit"} & set(qc)
    assert qc["output_sha256"] == sha(directory / "point.out")
    assert (directory / "point.projwfc.in").is_file() and (directory / "tmp_point/point.save").is_dir()
    assert not (directory / "point.REJECTED").exists() and not (directory / "point.KILLED").exists()


def test_unconverged_relaxation_is_rejected_before_projection_with_scratch_retained(approved, monkeypatch):
    spec, root, pseudo, directory, job = relaxed(approved)
    calls, _ = relaxation_doubles(monkeypatch, RELAXATION, status="UNCONVERGED")
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 10
    qc = json.loads((directory / "point.qc.json").read_text(encoding="utf-8"))
    assert qc["status"] == "REJECTED" and "UNCONVERGED" in qc["reason"] and "relaxation" not in qc
    assert len(calls) == 1 and not (directory / "point.projwfc.in").exists()
    assert (directory / "point.REJECTED").read_text(encoding="utf-8") == qc["reason"] + "\n"
    assert (directory / "tmp_point/point.save/charge-density.dat").is_file()


def test_relaxation_scf_beyond_the_iteration_ceiling_is_rejected(approved, monkeypatch):
    spec, root, pseudo, directory, job = relaxed(approved)
    calls, _ = relaxation_doubles(monkeypatch, RELAXATION.replace("iteration # 12\n", "iteration # 127\n"))
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 10
    qc = json.loads((directory / "point.qc.json").read_text(encoding="utf-8"))
    assert qc["status"] == "REJECTED" and "iteration" in qc["reason"] and "relaxation" not in qc
    assert len(calls) == 1 and (directory / "point.REJECTED").is_file()
    assert (directory / "tmp_point").is_dir()


def test_relaxation_supervisor_stop_is_killed_without_consulting_the_readout(approved, monkeypatch):
    spec, root, pseudo, directory, job = relaxed(approved)

    def stopped(command, output, cwd, env, seconds, max_iterations=None, exitfile=None):
        output.write_text("iteration # 1\n", encoding="utf-8", newline="\n")
        return {"rc": 0, "stop_reason": "wall-time ceiling", "wall_seconds": seconds}

    monkeypatch.setattr(batch, "execute", stopped)
    monkeypatch.setattr(hea_panel_readout, "parse_out",
                        lambda *a, **k: pytest.fail("readout consulted after a supervisor stop"))
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 10
    qc = json.loads((directory / "point.qc.json").read_text(encoding="utf-8"))
    assert qc["status"] == "REJECTED" and qc["reason"] == "wall-time ceiling" and "relaxation" not in qc
    assert (directory / "point.KILLED").read_text(encoding="utf-8") == "wall-time ceiling\n"
    assert not (directory / "point.REJECTED").exists() and (directory / "tmp_point").is_dir()


def test_relaxation_check_uses_the_real_readout(tmp_path):
    output = tmp_path / "leg.out"
    output.write_text(RELAXATION, encoding="utf-8", newline="\n")
    assert batch.relaxation_check(output, 126) == {
        "status": "CONVERGED", "maximum_scf_iteration": 20, "bfgs_converged": True,
        "final_energy_Ry": -10.5, "ionic_steps": 2}
    for mutation, expected in (
            (lambda s: s.replace("bfgs converged in 2 scf cycles and 1 bfgs steps\n", ""), "REJECTED"),
            (lambda s: s + "convergence NOT achieved after 300 iterations\n", "NOT CONVERGED"),
            (lambda s: s.replace("JOB DONE.\n", ""), "PENDING"),
            (lambda s: s + "Error in routine electrons (1)\n", "REJECTED")):
        output.write_text(mutation(RELAXATION), encoding="utf-8", newline="\n")
        with pytest.raises(ValueError, match=expected):
            batch.relaxation_check(output, 126)


# --- the checked relaxation (Arm A of the 2026-09-22 stall-robust plan) ---------------------------

CHECKED_DECK = """&CONTROL
 calculation = 'relax'
 prefix = 'point'
 outdir = './tmp'
 pseudo_dir = './pseudo'
 nstep = 50
/
&SYSTEM
 nat = 2
 nspin = 2
/
&ELECTRONS
 conv_thr = 1.0d-7
 startingpot = 'file'
/
ATOMIC_SPECIES
H 1.008 H.UPF
ATOMIC_POSITIONS angstrom
H 0 0 0 0 0 0
H 0 0 1 1 1 1
K_POINTS gamma
"""
SEGMENT = """Program PWSCF
number of atoms/cell = 2
iteration #  1
iteration # 14
!    total energy = -10.00000000 Ry
convergence has been achieved in 14 iterations
Total force =     0.050000     Total SCF correction =     0.000010
ATOMIC_POSITIONS (angstrom)
H        0.000000000   0.000000000   0.000000000    0   0   0
H        0.000000000   0.000000000   1.100000000    1   1   1

The maximum number of steps has been reached.
End of BFGS calculation
JOB DONE.
"""
CONVERGED = """Program PWSCF
number of atoms/cell = 2
iteration #  1
iteration # 12
!    total energy = -10.00000000 Ry
convergence has been achieved in 12 iterations
Total force =     0.001000     Total SCF correction =     0.000010
bfgs converged in 1 scf cycles and 0 bfgs steps
End of BFGS calculation
Begin final coordinates
ATOMIC_POSITIONS (angstrom)
H        0.000000000   0.000000000   0.000000000    0   0   0
H        0.000000000   0.000000000   1.100000000    1   1   1
End final coordinates
Final energy = -10.0000000000 Ry
JOB DONE.
"""
FRESH = """Program PWSCF
number of atoms/cell = 2
iteration #  1
iteration # 30
!    total energy = -10.00000000 Ry
convergence has been achieved in 30 iterations
JOB DONE.
"""
FRESH_LOW = FRESH.replace("-10.00000000", "-10.00147000")   # 20.0 meV below the segment
# A stopped SCF: the supervisor ended it at the ceiling; its printed energy must never be read.
STALLED = "Program PWSCF\niteration #  1\niteration # 127\n!    total energy = -10.00000000 Ry\n"
PROPOSED = "H 0.000000000 0.000000000 1.100000000 1 1 1\n"
START = "H 0 0 1 1 1 1\n"


def checked(approved):
    """The unit fixture as a checked relaxation: a relax deck reading the seeded density, kind
    "checked_relax" with the plan's parameters (delta 10 meV, 40 segments, 10 re-seeds)."""
    spec, root, pseudo, directory = approved
    save = root / "runs/prior/tmp_prior/prior.save"
    save.mkdir(parents=True)
    for name, data in SEED.items():
        (save / name).write_bytes(data)
    deck = directory / "point.in"
    deck.write_text(CHECKED_DECK, encoding="utf-8", newline="\n")
    stage = spec["stages"]["pilot"]
    stage["kind"] = "checked_relax"
    job = stage["jobs"][0]
    job.update(sha256=sha(deck), scf_seconds=50000,
               scratch_source={"save_dir": "runs/prior/tmp_prior/prior.save",
                               "files": {name: sha(save / name) for name in SEED}},
               checked={"delta_meV": 10.0, "max_segments": 40, "max_reseeds": 10,
                        "fresh_conv_thr": "8.08d-8", "segment_nstep": 1})
    return spec, root, pseudo, directory, job


def checked_doubles(monkeypatch, script):
    """pw.x doubles keyed by output name -> (text, stop_reason). Every pw.x double leaves the four
    state files (bytes unique to that run) in the save directory beside its exit file, snapshots
    what that save directory and the BFGS history held before it ran, and every segment double
    writes a BFGS history file; projwfc writes PROJECTION; the canonical readout is a stub that
    records which output it was shown."""
    calls, seen = [], {}

    def execute(command, output, cwd, env, seconds, max_iterations=None, exitfile=None):
        runtime = Path(command[command.index("-in") + 1])
        call = {"output": output.name, "seconds": seconds, "max_iterations": max_iterations,
                "runtime": runtime.read_text(encoding="utf-8")}
        calls.append(call)
        if output.name.endswith(".projwfc.out"):
            output.write_text(PROJECTION, encoding="utf-8", newline="\n")
            return {"rc": 0, "stop_reason": None, "wall_seconds": 3}
        text, stop = script[output.name]
        prefix = exitfile.name[:-len(".EXIT")]
        save = exitfile.parent / (prefix + ".save")
        call["save_before"] = {p.name: p.read_bytes() for p in save.iterdir()} if save.is_dir() else None
        history = exitfile.parent / "point.bfgs"
        call["bfgs_before"] = history.read_bytes() if history.is_file() else None
        output.write_text(text, encoding="utf-8", newline="\n")
        save.mkdir(exist_ok=True)
        for name in SEED:
            (save / name).write_bytes((name + " of " + output.name).encode())
        if ".seg" in output.name and stop is None:   # a stopped SCF never reaches the optimizer
            history.write_bytes(("history after " + output.name).encode())
        return {"rc": 0, "stop_reason": stop, "wall_seconds": 7}

    def parse_out(path, *, allow_relax=False):
        seen["path"], seen["allow_relax"] = Path(path), allow_relax
        return {"status": "CONVERGED"}

    monkeypatch.setattr(batch, "execute", execute)
    monkeypatch.setattr(hea_panel_readout, "parse_out", parse_out)
    return calls, seen


def receipts(directory):
    return json.loads((directory / "point.qc.json").read_text(encoding="utf-8"))


SPECIFIED = ("k", "geometry_sha256", "segment_energy_Ry", "segment_iterations", "stalled", "fresh_energy_Ry",
             "fresh_iterations", "fresh_converged", "delta_meV", "action", "reseeds_so_far", "atom20_spin_down_diagonal")


def test_accepted_step_then_convergence_completes_with_receipts(approved, monkeypatch):
    spec, root, pseudo, directory, job = checked(approved)
    calls, seen = checked_doubles(monkeypatch, {
        "point.seg1.out": (SEGMENT, None), "point.fresh1.out": (FRESH, None),
        "point.seg2.out": (CONVERGED, None), "point.fresh2.out": (FRESH, None)})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 0
    qc = receipts(directory)
    assert qc["status"] == "COMPLETE" and qc["reseeds"] == 0 and qc["completed_segment"] == 2
    assert qc["checked"] == job["checked"]
    assert qc["scratches"] == ["tmp_point", "tmp_point_fresh1", "tmp_point_s2", "tmp_point_fresh2"]
    assert [c["output"] for c in calls] == ["point.seg1.out", "point.fresh1.out", "point.seg2.out",
                                             "point.fresh2.out", "point.projwfc.out"]
    assert [c["seconds"] for c in calls] == [50000] * 4 + [60] and all(c["max_iterations"] == 126 for c in calls[:4])
    first, second = qc["segments"]
    assert set(SPECIFIED) <= set(first) and set(SPECIFIED) <= set(second)
    assert {k: first[k] for k in SPECIFIED[2:]} == {
        "segment_energy_Ry": -10.0, "segment_iterations": 14, "stalled": False, "fresh_energy_Ry": -10.0,
        "fresh_iterations": 30, "fresh_converged": True, "delta_meV": 0.0, "action": "accept",
        "reseeds_so_far": 0, "atom20_spin_down_diagonal": None}
    assert first["k"] == 1 and first["geometry_sha256"] == batch.geometry_digest(batch.deck_geometry(CHECKED_DECK, 2))
    assert first["total_force"] == 0.05 and not first["bfgs_converged"] and first["scratch"] == "tmp_point"
    assert first["seeded_from"] == str(root / "runs/prior/tmp_prior/prior.save")
    own_save = directory / "tmp_point/point.save"
    assert first["continuation"] == {"scratch": "tmp_point_s2", "save_dir": str(own_save),
                                     "copied": {n: sha(own_save / n) for n in SEED},
                                     "bytes": sum(len(n + " of point.seg1.out") for n in SEED), "bfgs_history": "point.bfgs"}
    assert second["k"] == 2 and second["action"] == "accept" and second["bfgs_converged"]
    assert second["scratch"] == "tmp_point_s2" and second["seeded_from"] == str(own_save) and "continuation" not in second
    assert second["segment_iterations"] == 12 and second["geometry_sha256"] != first["geometry_sha256"]
    # every segment runs from scratch: k = 1 on the pinned seed, k = 2 in a new scratch seeded by
    # segment 1's own save files and BFGS history (copied, not moved), at the proposed geometry
    seg1, fresh1, seg2, fresh2 = (c["runtime"] for c in calls[:4])
    assert not any(" restart_mode = 'restart'" in c["runtime"] for c in calls)
    for seg in (seg1, seg2):
        assert " nstep = 1\n" in seg and " restart_mode = 'from_scratch'\n" in seg and " nstep = 50" not in seg
        assert " startingpot = 'file'\n" in seg and " startingwfc = 'atomic+random'\n" in seg
    assert "outdir = '" + str(directory / "tmp_point") + "'" in seg1 and START in seg1
    assert "outdir = '" + str(directory / "tmp_point_s2") + "'" in seg2 and PROPOSED in seg2 and START not in seg2
    assert calls[2]["save_before"] == {n: (n + " of point.seg1.out").encode() for n in SEED}
    assert calls[2]["bfgs_before"] == b"history after point.seg1.out"
    assert (directory / "tmp_point/point.bfgs").read_bytes() == b"history after point.seg1.out"
    assert {p.name: p.read_bytes() for p in own_save.iterdir()} == {n: (n + " of point.seg1.out").encode() for n in SEED}
    for k, fresh, geometry in ((1, fresh1, START), (2, fresh2, PROPOSED)):
        assert " calculation = 'scf'\n" in fresh and " prefix = 'point_fresh%d'\n" % k in fresh
        assert " conv_thr = 8.08d-8\n" in fresh and " conv_thr = 1.0d-7" not in fresh
        assert " startingwfc = 'atomic+random'\n" in fresh and " startingpot = 'atomic'\n" in fresh
        assert " restart_mode = 'from_scratch'\n" in fresh and geometry in fresh
        assert "outdir = '" + str(directory / ("tmp_point_fresh%d" % k)) + "'" in fresh
        assert " pseudo_dir = '" + str(pseudo) + "'\n" in fresh
    # the tail as for kind "relax", over the last segment
    assert seen == {"path": directory / "point.seg2.out", "allow_relax": True}
    assert qc["relaxation"] == {"status": "CONVERGED", "maximum_scf_iteration": 12, "bfgs_converged": True,
                                "final_energy_Ry": -10.0, "ionic_steps": 1}
    assert qc["output_sha256"] == sha(directory / "point.seg2.out")
    assert qc["runtime_sha256"] == sha(directory / "point.seg2.run.in")
    assert "outdir = '" + str(directory / "tmp_point_s2") + "'" in (directory / "point.projwfc.in").read_text(encoding="utf-8")
    assert qc["scratch_retained"] == str(directory / "tmp_point_s2")
    assert not (directory / "point.out").exists() and not (directory / "point.run.in").exists()
    assert not (directory / "point.REJECTED").exists() and not (directory / "point.KILLED").exists()
    assert not {"scf", "force", "complete_audit", "scf_process"} & set(qc)


@pytest.mark.parametrize("fresh_energy,action", [
    ("-10.00050000", "accept"),   # 6.8 meV below: within delta
    ("-9.99900000", "accept"),    # above the segment
    ("-10.00147000", "reseed"),   # 20 meV below
])
def test_comparison_reseeds_only_below_delta(approved, monkeypatch, fresh_energy, action):
    spec, root, pseudo, directory, job = checked(approved)
    checked_doubles(monkeypatch, {
        "point.seg1.out": (SEGMENT, None), "point.fresh1.out": (FRESH.replace("-10.00000000", fresh_energy), None),
        "point.seg2.out": (CONVERGED, None), "point.fresh2.out": (FRESH, None)})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 0
    qc = receipts(directory)
    assert qc["segments"][0]["action"] == action and qc["reseeds"] == (action == "reseed")
    assert abs(qc["segments"][0]["delta_meV"] - (float(fresh_energy) + 10.0) * batch.RY_MEV) < 1e-6


def test_fresh_energy_below_delta_reseeds_from_the_fresh_density(approved, monkeypatch):
    spec, root, pseudo, directory, job = checked(approved)
    calls, seen = checked_doubles(monkeypatch, {
        "point.seg1.out": (SEGMENT, None), "point.fresh1.out": (FRESH_LOW, None),
        "point.seg2.out": (CONVERGED, None), "point.fresh2.out": (FRESH, None)})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 0
    qc = receipts(directory)
    assert qc["status"] == "COMPLETE" and qc["reseeds"] == 1
    first, second = qc["segments"]
    assert first["action"] == "reseed" and abs(first["delta_meV"] + 20.0) < 0.01 and first["reseeds_so_far"] == 1
    fresh_save = directory / "tmp_point_fresh1/point_fresh1.save"
    assert first["continuation"] == {"scratch": "tmp_point_r1", "save_dir": str(fresh_save),
                                     "copied": {n: sha(fresh_save / n) for n in SEED},
                                     "bytes": sum(len(n + " of point.fresh1.out") for n in SEED), "bfgs_history": "point.bfgs"}
    assert not any(" restart_mode = 'restart'" in c["runtime"] for c in calls)
    # segment 2 starts in the new scratch from the fresh density and the carried history, both copied
    assert calls[2]["output"] == "point.seg2.out"
    assert calls[2]["save_before"] == {n: (n + " of point.fresh1.out").encode() for n in SEED}
    assert calls[2]["bfgs_before"] == b"history after point.seg1.out"
    assert (fresh_save / "occup.txt").read_bytes() == b"occup.txt of point.fresh1.out"
    assert (directory / "tmp_point/point.bfgs").read_bytes() == b"history after point.seg1.out"
    # the step is repeated from the checked geometry, seeded, not restarted
    seg2 = calls[2]["runtime"]
    assert " restart_mode = 'from_scratch'\n" in seg2 and " startingpot = 'file'\n" in seg2
    assert " startingwfc = 'atomic+random'\n" in seg2 and " nstep = 1\n" in seg2
    assert START in seg2 and PROPOSED not in seg2 and "outdir = '" + str(directory / "tmp_point_r1") + "'" in seg2
    assert START in calls[3]["runtime"] and "outdir = '" + str(directory / "tmp_point_fresh2") + "'" in calls[3]["runtime"]
    assert second["scratch"] == "tmp_point_r1" and second["action"] == "accept" and second["reseeds_so_far"] == 1
    assert second["seeded_from"] == str(fresh_save) and "continuation" not in second
    assert second["geometry_sha256"] == first["geometry_sha256"]
    assert qc["scratches"] == ["tmp_point", "tmp_point_fresh1", "tmp_point_r1", "tmp_point_fresh2"]
    assert qc["scratch_retained"] == str(directory / "tmp_point_r1")
    assert "outdir = '" + str(directory / "tmp_point_r1") + "'" in (directory / "point.projwfc.in").read_text(encoding="utf-8")
    assert seen["path"] == directory / "point.seg2.out"
    assert not (directory / "point.REJECTED").exists() and not (directory / "point.KILLED").exists()


@pytest.mark.parametrize("stalled_text,stop,reason,history", [
    (STALLED, "SCF iteration ceiling", "SCF iteration ceiling", None),
    (SEGMENT.replace("iteration # 14\n", "iteration # 127\n"), None, "SCF iteration ceiling (post-hoc)", "point.bfgs"),
])
def test_stalled_segment_reseeds_from_the_fresh_density_and_reads_no_energy(
        approved, monkeypatch, stalled_text, stop, reason, history):
    spec, root, pseudo, directory, job = checked(approved)
    calls, _ = checked_doubles(monkeypatch, {
        "point.seg1.out": (stalled_text, stop), "point.fresh1.out": (FRESH, None),
        "point.seg2.out": (CONVERGED, None), "point.fresh2.out": (FRESH, None)})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 0
    qc = receipts(directory)
    assert qc["status"] == "COMPLETE" and qc["reseeds"] == 1
    first = qc["segments"][0]
    assert first["stalled"] and first["stalled_reason"] == reason and first["action"] == "reseed"
    assert first["segment_energy_Ry"] is None and first["segment_iterations"] == 127 and first["delta_meV"] is None
    assert first["fresh_energy_Ry"] == -10.0 and first["fresh_converged"] and first["reseeds_so_far"] == 1
    assert first["continuation"]["scratch"] == "tmp_point_r1" and first["continuation"]["bfgs_history"] == history
    assert qc["segments"][1]["seeded_from"] == str(directory / "tmp_point_fresh1/point_fresh1.save")
    assert calls[2]["save_before"] == {n: (n + " of point.fresh1.out").encode() for n in SEED}
    assert START in calls[2]["runtime"] and "outdir = '" + str(directory / "tmp_point_r1") + "'" in calls[2]["runtime"]
    assert not (directory / "point.KILLED").exists() and not (directory / "point.REJECTED").exists()


def test_reseed_cap_rejects_with_the_cap_in_the_reason(approved, monkeypatch):
    spec, root, pseudo, directory, job = checked(approved)
    job["checked"]["max_reseeds"] = 1
    calls, _ = checked_doubles(monkeypatch, {
        "point.seg1.out": (SEGMENT, None), "point.fresh1.out": (FRESH_LOW, None),
        "point.seg2.out": (SEGMENT, None), "point.fresh2.out": (FRESH_LOW, None)})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 10
    qc = receipts(directory)
    assert qc["status"] == "REJECTED" and "reseed cap" in qc["reason"] and "cap of 1" in qc["reason"]
    assert [s["action"] for s in qc["segments"]] == ["reseed", "stop"] and qc["reseeds"] == 1
    assert [c["output"] for c in calls] == ["point.seg1.out", "point.fresh1.out", "point.seg2.out", "point.fresh2.out"]
    assert not (directory / "tmp_point_r2").exists() and not (directory / "tmp_point_s3").exists()
    assert not (directory / "point.projwfc.in").exists()
    assert (directory / "point.REJECTED").read_text(encoding="utf-8") == qc["reason"] + "\n"
    assert not (directory / "point.KILLED").exists() and "relaxation" not in qc
    assert qc["scratch_retained"] == str(directory / "tmp_point_r1")


def test_segment_cap_rejects_an_unconverged_relaxation(approved, monkeypatch):
    spec, root, pseudo, directory, job = checked(approved)
    job["checked"]["max_segments"] = 2
    calls, _ = checked_doubles(monkeypatch, {
        "point.seg1.out": (SEGMENT, None), "point.fresh1.out": (FRESH, None),
        "point.seg2.out": (SEGMENT, None), "point.fresh2.out": (FRESH, None)})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 10
    qc = receipts(directory)
    assert qc["status"] == "REJECTED" and "segment cap" in qc["reason"] and "2 segments" in qc["reason"]
    assert [s["action"] for s in qc["segments"]] == ["accept", "accept"] and len(calls) == 4
    assert qc["segments"][0]["continuation"]["scratch"] == "tmp_point_s2" and "continuation" not in qc["segments"][1]
    assert (directory / "tmp_point_s2").is_dir() and not (directory / "tmp_point_s3").exists()
    assert qc["scratch_retained"] == str(directory / "tmp_point_s2")
    assert not (directory / "point.projwfc.in").exists() and "relaxation" not in qc
    assert (directory / "point.REJECTED").is_file() and not (directory / "point.KILLED").exists()


def test_fresh_check_without_a_reference_accepts_only_a_converged_segment(approved, monkeypatch):
    # Rule (f): a stopped fresh check gives no reference and cannot re-seed; the step is accepted
    # only because the segment's own SCF converged, and the receipt says the check was missing.
    spec, root, pseudo, directory, job = checked(approved)
    calls, _ = checked_doubles(monkeypatch, {
        "point.seg1.out": (SEGMENT, None), "point.fresh1.out": (STALLED, "SCF iteration ceiling"),
        "point.seg2.out": (CONVERGED, None), "point.fresh2.out": (FRESH, None)})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 0
    qc = receipts(directory)
    assert qc["status"] == "COMPLETE" and qc["reseeds"] == 0
    first = qc["segments"][0]
    assert first["action"] == "accept" and not first["fresh_converged"] and first["fresh_energy_Ry"] is None
    assert first["delta_meV"] is None and first["fresh_iterations"] == 127
    assert first["fresh_reason"] == "stopped: SCF iteration ceiling" and first["fresh_process"]["stop_reason"] == "SCF iteration ceiling"
    assert PROPOSED in calls[2]["runtime"] and " restart_mode = 'from_scratch'\n" in calls[2]["runtime"]
    assert "outdir = '" + str(directory / "tmp_point_s2") + "'" in calls[2]["runtime"]
    assert first["continuation"]["save_dir"] == str(directory / "tmp_point/point.save")
    assert not (directory / "point.KILLED").exists()


def test_stalled_segment_without_a_fresh_reference_is_killed_with_both_reasons(approved, monkeypatch):
    spec, root, pseudo, directory, job = checked(approved)
    calls, _ = checked_doubles(monkeypatch, {
        "point.seg1.out": (STALLED, "SCF iteration ceiling"), "point.fresh1.out": (STALLED, "wall-time ceiling")})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 10
    qc = receipts(directory)
    assert qc["status"] == "REJECTED" and "SCF iteration ceiling" in qc["reason"] and "wall-time ceiling" in qc["reason"]
    assert (directory / "point.KILLED").read_text(encoding="utf-8") == qc["reason"] + "\n"
    assert not (directory / "point.REJECTED").exists() and len(calls) == 2
    first = qc["segments"][0]
    assert first["action"] == "stop" and first["stalled"] and first["segment_energy_Ry"] is None
    assert first["fresh_energy_Ry"] is None and not first["fresh_converged"] and qc["reseeds"] == 0
    assert not (directory / "tmp_point_r1").exists() and (directory / "tmp_point").is_dir()


def test_converged_final_step_without_a_fresh_reference_is_not_complete(approved, monkeypatch):
    spec, root, pseudo, directory, job = checked(approved)
    calls, _ = checked_doubles(monkeypatch, {
        "point.seg1.out": (CONVERGED, None), "point.fresh1.out": (STALLED, "SCF iteration ceiling")})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 10
    qc = receipts(directory)
    assert qc["status"] == "REJECTED" and "no reference" in qc["reason"] and "relaxation" not in qc
    assert qc["segments"][0]["action"] == "stop" and qc["segments"][0]["bfgs_converged"]
    assert len(calls) == 2 and (directory / "point.REJECTED").is_file() and not (directory / "point.KILLED").exists()


def test_non_ceiling_stop_on_a_segment_is_rejected_without_a_fresh_check(approved, monkeypatch):
    spec, root, pseudo, directory, job = checked(approved)
    calls, _ = checked_doubles(monkeypatch, {"point.seg1.out": ("Error in routine electrons\n", "numerical failure marker")})
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 10
    qc = receipts(directory)
    assert qc["status"] == "REJECTED" and qc["reason"] == "numerical failure marker"
    assert len(calls) == 1 and qc["segments"][0]["action"] == "stop" and not qc["segments"][0]["stalled"]
    assert (directory / "point.REJECTED").is_file() and not (directory / "point.KILLED").exists()
    assert not (directory / "tmp_point_fresh1").exists()


def test_leg_wall_ceiling_stops_before_the_next_launch(approved, monkeypatch):
    spec, root, pseudo, directory, job = checked(approved)
    job["checked"]["leg_seconds"] = 3600
    calls, _ = checked_doubles(monkeypatch, {"point.seg1.out": (SEGMENT, None)})
    ticks = iter([0, 100, 4000])  # leg start, before segment 1, before fresh check 1
    monkeypatch.setattr(batch.time, "monotonic", lambda: next(ticks))
    assert batch.run(spec, root, "pilot", 1, pseudo, root / "qe") == 10
    qc = receipts(directory)
    assert qc["status"] == "REJECTED" and "leg wall ceiling" in qc["reason"] and "point.fresh1.out" in qc["reason"]
    assert len(calls) == 1 and qc["segments"][0]["action"] == "stop" and qc["segments"][0]["segment_energy_Ry"] == -10.0
    assert not (directory / "point.fresh1.run.in").exists() and (directory / "point.REJECTED").is_file()


def test_checked_stage_validates_the_plan_parameters_without_touching_scratch(approved):
    spec, root, pseudo, directory, job = checked(approved)
    assert batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)["kind"] == "checked_relax"
    job["checked"]["leg_seconds"] = batch.LEG_SECONDS
    batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


def test_checked_stage_refuses_a_fixed_geometry_deck(approved):
    spec, root, pseudo, directory, job = checked(approved)
    deck = directory / "point.in"
    deck.write_text(CHECKED_DECK.replace("calculation = 'relax'", "calculation = 'scf'"), encoding="utf-8", newline="\n")
    job["sha256"] = sha(deck)
    with pytest.raises(ValueError, match="calculation.*expected 'relax'"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


def test_checked_stage_requires_its_parameters_and_a_scratch_source(approved):
    spec, root, pseudo, directory, job = checked(approved)
    checked_parameters = job.pop("checked")
    with pytest.raises(ValueError, match="checked parameters"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    job["checked"] = checked_parameters
    del job["scratch_source"]
    with pytest.raises(ValueError, match="scratch source"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


@pytest.mark.parametrize("change,message", [
    ({"delta_meV": 0}, "delta_meV"), ({"delta_meV": 100.5}, "delta_meV"), ({"delta_meV": True}, "delta_meV"),
    ({"delta_meV": "10"}, "delta_meV"),
    ({"max_segments": 0}, "max_segments"), ({"max_segments": 61}, "max_segments"), ({"max_segments": 1.0}, "max_segments"),
    ({"max_reseeds": -1}, "max_reseeds"), ({"max_reseeds": 21}, "max_reseeds"),
    ({"segment_nstep": 2}, "segment_nstep"), ({"segment_nstep": True}, "segment_nstep"),
    ({"fresh_conv_thr": 8e-8}, "fresh_conv_thr"), ({"fresh_conv_thr": "loose"}, "fresh_conv_thr"),
    ({"fresh_conv_thr": "-8.08d-8"}, "fresh_conv_thr"),
    ({"leg_seconds": 0}, "leg_seconds"), ({"leg_seconds": 259201}, "leg_seconds"),
])
def test_checked_parameters_are_bounded(approved, change, message):
    spec, root, pseudo, directory, job = checked(approved)
    job["checked"].update(change)
    with pytest.raises(ValueError, match=message):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert not (directory / "tmp_point").exists()


def test_checked_stage_keeps_the_relaxation_bounds(approved):
    spec, root, pseudo, directory, job = checked(approved)
    job["scf_seconds"] = 60001
    with pytest.raises(ValueError, match="bounded runtime"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    job["scf_seconds"] = 60000
    job["max_iterations"] = 200
    with pytest.raises(ValueError, match="126"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)


@pytest.mark.parametrize("prior", ["point.seg1.out", "point.seg1.run.in", "point.fresh1.out", "point.fresh1.run.in",
                                   "tmp_point_fresh1", "tmp_point_r1", "tmp_point_s2"])
def test_checked_stage_never_overwrites_a_prior_segment_or_scratch(approved, prior):
    spec, root, pseudo, directory, job = checked(approved)
    path = directory / prior
    if prior.startswith("tmp_"):
        path.mkdir()
    else:
        path.write_bytes(b"prior evidence")
    with pytest.raises(ValueError, match="prior"):
        batch.validate(spec, root, "pilot", row=1, pseudo=pseudo)
    assert path.exists() and not (directory / "tmp_point").exists()


def test_set_field_replaces_or_inserts_exactly_one_line():
    text = "&CONTROL\n calculation = 'relax'\n nstep = 50\n/\n&ELECTRONS\n conv_thr = 1.0d-7\n/\n"
    assert batch.set_field(text, "CONTROL", "nstep", "1") == text.replace(" nstep = 50\n", " nstep = 1\n")
    assert batch.set_field(text, "CONTROL", "restart_mode", "'restart'").startswith(
        "&CONTROL\n restart_mode = 'restart'\n calculation = 'relax'\n")
    assert batch.set_field(text, "ELECTRONS", "startingwfc", "'atomic+random'").endswith(
        "&ELECTRONS\n startingwfc = 'atomic+random'\n conv_thr = 1.0d-7\n/\n")
    with pytest.raises(ValueError, match="namelist not unique"):
        batch.set_field(text, "IONS", "ion_dynamics", "'bfgs'")
    with pytest.raises(ValueError, match="rewrite not unique"):
        batch.set_field(text.replace("/\n&ELECTRONS", " nstep = 3\n/\n&ELECTRONS"), "CONTROL", "nstep", "1")


def test_segment_readout_reads_the_geometry_after_the_last_energy_and_inherits_flags():
    reference = batch.deck_geometry(CHECKED_DECK, 2)
    assert [batch.render_atom(a) for a in reference] == ["H 0 0 0 0 0 0", "H 0 0 1 1 1 1"]
    result = batch.segment_readout(SEGMENT, 2, reference)
    assert result["energy_Ry"] == -10.0 and result["iterations"] == 14 and result["total_force"] == 0.05
    assert not result["bfgs_converged"]
    assert [batch.render_atom(a) for a in result["geometry"]] == [
        "H 0.000000000 0.000000000 0.000000000 0 0 0", "H 0.000000000 0.000000000 1.100000000 1 1 1"]
    assert batch.segment_readout(CONVERGED, 2, reference)["bfgs_converged"]
    unflagged = SEGMENT.replace("    0   0   0", "").replace("    1   1   1", "")
    assert [a[4] for a in batch.segment_readout(unflagged, 2, reference)["geometry"]] == [("0", "0", "0"), ("1", "1", "1")]
    rendered = batch.render_positions(CHECKED_DECK, 2, result["geometry"])
    assert rendered.count("ATOMIC_POSITIONS angstrom\n" + PROPOSED.replace("1.100000000", "0.000000000").replace(" 1 1 1", " 0 0 0") + PROPOSED + "K_POINTS gamma\n") == 1
    for mutation, message in (
            (lambda s: s.replace("JOB DONE.", ""), "not complete"),
            (lambda s: s + "Error in routine electrons\n", "not complete"),
            (lambda s: s.replace("ATOMIC_POSITIONS (angstrom)", "positions"), "no geometry"),
            (lambda s: s.replace("H        0.000000000   0.000000000   1.100000000", "O        0.000000000   0.000000000   1.100000000"), "species order"),
            (lambda s: s.replace("!    total energy = -10.00000000 Ry\n", ""), "no converged"),
            (lambda s: s.replace("-10.00000000", "1e999"), "nonfinite")):
        with pytest.raises(ValueError, match=message):
            batch.segment_readout(mutation(SEGMENT), 2, reference)


def test_occupation_diagonal_reads_atom_20_spin_down_column_major(tmp_path):
    nat, nspin, ldim = 20, 2, 5
    values = [0.0] * (ldim * ldim * nspin * nat)
    block = ldim * ldim * ((20 - 1) * nspin + 1)   # atom 20, spin down, in ns(m1, m2, spin, atom)
    diagonal = [0.321, 0.974, 0.139, 0.903, 0.408]
    for m, value in enumerate(diagonal):
        values[block + m * ldim + m] = value
    values[block + 1] = 0.5   # ns(2, 1) of the same block: off-diagonal, must not leak in
    tokens, i = [], 0
    while i < len(values):   # Fortran list-directed output may compress repeats as r*c
        j = i
        while j < len(values) and values[j] == values[i]:
            j += 1
        tokens.append(("%d*%.17G" % (j - i, values[i])) if j - i > 1 else "%.17G" % values[i])
        i = j
    path = tmp_path / "occup.txt"
    path.write_text("\n".join(" ".join(tokens[n:n + 4]) for n in range(0, len(tokens), 4)) + "\n", encoding="ascii")
    assert batch.occupation_diagonal(path, nat, nspin) == diagonal
    assert batch.occupation_diagonal(path, nat, nspin, atom=1, spin=1) == [0.0] * 5
    assert batch.occupation_diagonal(path, nat - 1, nspin) is None       # element count does not factor
    assert batch.occupation_diagonal(path, nat, nspin, atom=21) is None
    assert batch.occupation_diagonal(tmp_path / "absent.txt", nat, nspin) is None
    path.write_bytes(b"hubbard ns")
    assert batch.occupation_diagonal(path, 2, 2) is None

