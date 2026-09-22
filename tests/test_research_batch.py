"""Spend boundaries and scientific result integrity for the bounded batch runner.

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
import research_batch as batch

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

