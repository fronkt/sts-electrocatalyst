"""Scientific and preservation regressions for the bounded relaxation launch."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import lowtail_batch as batch


LIMITS = dict(max_scf_iterations=126, stop_when_iteration_begins=127, leg_wall_ceiling_s=20000)
BENIGN = "Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DENORMAL"


def deck_text(prefix="lt0"):
    return f"""&CONTROL
  calculation = 'relax'
  prefix = '{prefix}'
  outdir = './tmp'
  pseudo_dir = './pseudo'
  forc_conv_thr = 2.0d-3
/
&SYSTEM
  nat = 2
  ntyp = 2
/
&ELECTRONS
  electron_maxstep = 300
/
&IONS
  ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
  Cr 51.996 cr.UPF
  O 15.999 O.UPF
CELL_PARAMETERS angstrom
  10 0 0
  0 10 0
  0 0 20
ATOMIC_POSITIONS angstrom
  Cr 0 0 5 0 0 0
  O 0 0 6.6 1 1 1
K_POINTS automatic
  4 2 1 0 0 0
HUBBARD (atomic)
U Cr-3d 3.7
"""


def output_text(*, final_force="0.00050000", iterations=(20, 12), note=BENIGN, contribution=False):
    chunks = ["number of atoms/cell = 2", "total magnetization = 3.00", "absolute magnetization = 5.00"]
    for n, count in enumerate(iterations):
        chunks += [f"iteration # {count}", f"!    total energy = {-100.0 - n:.8f} Ry",
                   f"convergence has been achieved in {count} iterations",
                   "Forces acting on atoms (cartesian axes, Ry/au):", "",
                   "atom 1 type 1 force = 0.00000000 0.00000000 0.40000000",
                   f"atom 2 type 2 force = 0.00000000 0.00000000 {final_force if n else '0.04000000'}", ""]
        if contribution:
            chunks += ["The non-local contrib.  to forces",
                       "atom 1 type 1 force = 9.00000000 9.00000000 9.00000000",
                       "atom 2 type 2 force = 9.00000000 9.00000000 9.00000000", ""]
        chunks += ["Total force = 0.001000"]
    chunks += ["bfgs converged in 2 scf cycles and 1 bfgs steps", "End of BFGS Geometry Optimization",
               "Final energy = -101.0000000000 Ry", "Begin final coordinates", "", "ATOMIC_POSITIONS (angstrom)",
               "Cr 0.0000000000 0.0000000000 5.0000000000 0 0 0", "O 0.0000000000 0.0000000000 6.5900000000",
               "End final coordinates", "PWSCF : 10.00s CPU 11.00s WALL", "JOB DONE.", note]
    return "\n".join(chunks) + "\n"


def check(tmp_path, text=None, wall=11):
    out = tmp_path / "leg.out"
    out.write_text(output_text() if text is None else text, encoding="utf-8")
    job = dict(nat=2, supervisor_limits=LIMITS, forc_conv_thr_Ry_bohr=0.002)
    return batch.relaxation_check(out, deck_text(), job, dict(wall_seconds=wall))


def test_converged_relaxation_uses_free_total_forces_only(tmp_path):
    result = check(tmp_path, output_text(contribution=True))
    assert result["score"]["status"] == "CONVERGED"
    assert result["max_free_component_Ry_bohr"] == 0.0005
    assert result["fixed_shift_A"] == 0
    assert result["final_positions_A"][1] == [0, 0, 6.59]


@pytest.mark.parametrize("mutate", [
    lambda t: t.replace("IEEE_UNDERFLOW_FLAG IEEE_DENORMAL", "IEEE_INVALID_FLAG"),
    lambda t: t.replace("IEEE_UNDERFLOW_FLAG IEEE_DENORMAL", "IEEE_UNKNOWN_FLAG"),
    lambda t: t.replace("iteration # 20", "iteration # 127"),
    lambda t: t.replace("11.00s WALL", "6h WALL"),
    lambda t: t.replace("bfgs converged in 2 scf cycles", "bfgs converged in 3 scf cycles"),
    lambda t: t.replace("Final energy = -101.0000000000", "Final energy = -100.9999999500"),
    lambda t: t.replace("number of atoms/cell = 2", "number of atoms/cell = 3"),
    lambda t: t.replace("O 0.0000000000 0.0000000000 6.5900000000", "H 0.0000000000 0.0000000000 6.5900000000"),
    lambda t: t.replace("Cr 0.0000000000 0.0000000000 5.0000000000", "Cr 0.0000000000 0.0000000000 5.0010000000"),
    lambda t: t.replace("Begin final coordinates", "Begin final coordinates\nBegin final coordinates"),
    lambda t: t.replace("End final coordinates", "O 0.0 0.0 7.0\nEnd final coordinates"),
    lambda t: t.replace("ATOMIC_POSITIONS (angstrom)", "ATOMIC_POSITIONS (crystal)"),
    lambda t: t.replace("0.00050000", "0.01000000"),
    lambda t: t.replace("0.00050000", "1e999"),
    lambda t: t.replace("convergence has been achieved in 12 iterations", "convergence NOT achieved after 300 iterations"),
    lambda t: t.replace("JOB DONE.", "The maximum number of steps has been reached.\nJOB DONE."),
])
def test_rejects_unusable_or_mixed_relaxation_evidence(tmp_path, mutate):
    with pytest.raises((ValueError, batch.hea_panel_readout.Fatal)):
        check(tmp_path, mutate(output_text()))


def test_process_clock_independently_enforces_leg_ceiling(tmp_path):
    with pytest.raises(ValueError, match="limit"):
        check(tmp_path, wall=20001)


def test_real_QE_relaxation_is_accepted():
    job = dict(nat=19, supervisor_limits=LIMITS, forc_conv_thr_Ry_bohr=0.002)
    result = batch.relaxation_check(ROOT / "runs/Cr_slab/s0_O.out",
                                    (ROOT / "runs/Cr_slab/s0_O.in").read_text(encoding="utf-8"),
                                    job, dict(wall_seconds=15360))
    assert len(result["final_positions_A"]) == 19
    assert result["score"]["status"] == "CONVERGED"


@pytest.fixture
def launch(tmp_path):
    root, pseudo = tmp_path / "repo", tmp_path / "pseudo"
    root.mkdir()
    pseudo.mkdir()
    files = {}
    for relative in batch.DEPENDENCIES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
        files[relative] = batch.digest(target)
    pseudo_md5 = {}
    for name in ("cr.UPF", "O.UPF"):
        (pseudo / name).write_bytes(name.encode())
        pseudo_md5[name] = batch.digest(pseudo / name, "md5")
    jobs = []
    for i in range(9):
        job = f"O_recon_{i}__atomic"
        relative = f"runs/hea/site{i}/{job}.in"
        target = root / relative
        target.parent.mkdir(parents=True)
        target.write_text(deck_text(f"lt{i}"), encoding="utf-8", newline="\n")
        jobs.append(dict(job=job, site=f"site{i}", manifest_dir=f"hea/site{i}", path=relative,
                         prefix=f"lt{i}", nat=2, fixed=[0], nk=8, projector="atomic", role="primary",
                         sha256=batch.digest(target), supervisor_limits=copy.deepcopy(LIMITS),
                         forc_conv_thr_Ry_bohr=0.002, projection_seconds=120))
        files[relative] = batch.digest(target)
    manifest = "runs/primary.txt"
    (root / manifest).write_text("# NP=128 NCONC=1\n" + "".join(
        f"{j['manifest_dir']} {j['job']} .in {j['nk']}\n" for j in jobs), encoding="utf-8", newline="\n")
    files[manifest] = batch.digest(root / manifest)
    spec = dict(schema="lowtail-relaxation-launch-v1", authorization="USER_CONTINUE_2026-09-18",
                np=128, concurrency=1, jobs=jobs, files=files, manifest=manifest, pseudo_md5=pseudo_md5)
    return spec, root, pseudo


def test_preflight_validates_the_bounded_atomic_batch(launch):
    spec, root, pseudo = launch
    assert batch.validate(spec, root, pseudo=pseudo) is None
    assert batch.validate(spec, root, row=1, pseudo=pseudo) == spec["jobs"][0]


@pytest.mark.parametrize("suffix", [".out", ".run.in", ".KILLED", ".REJECTED", ".qc.json"])
def test_preflight_preserves_every_existing_attempt(launch, suffix):
    spec, root, pseudo = launch
    prior = (root / spec["jobs"][0]["path"]).with_suffix(suffix)
    prior.write_bytes(b"unfinished or completed evidence\n")
    with pytest.raises(ValueError, match="prior artifact"):
        batch.validate(spec, root, row=1, pseudo=pseudo)
    assert prior.read_bytes() == b"unfinished or completed evidence\n"


@pytest.mark.parametrize("mutation", [
    lambda s: s.update(concurrency=2),
    lambda s: s["jobs"][0].update(projector="ortho"),
    lambda s: s["jobs"][0]["supervisor_limits"].update(max_scf_iterations=300),
    lambda s: s["jobs"][0]["supervisor_limits"].update(leg_wall_ceiling_s=165000),
    lambda s: s["jobs"][0].update(projection_seconds=1801),
])
def test_preflight_refuses_expanded_authorization(launch, mutation):
    spec, root, pseudo = launch
    mutation(spec)
    with pytest.raises(ValueError):
        batch.validate(spec, root, pseudo=pseudo)


@pytest.mark.parametrize("reason, status, raised", [
    ("SCF iteration ceiling", "KILLED", None),
    ("wall-time ceiling", "KILLED", None),
    ("numerical failure marker", "REJECTED", None),
    (None, "REJECTED", subprocess.SubprocessError("process wait failed")),
    (None, "REJECTED", batch.hea_panel_readout.Fatal("malformed wall token")),
])
def test_failed_run_banks_receipt_and_preserves_scratch(launch, monkeypatch, reason, status, raised):
    spec, root, pseudo = launch
    job = spec["jobs"][0]
    directory = root / "runs" / job["manifest_dir"]
    calls = []
    def execute(command, output, cwd, env, seconds, max_iterations=None, exitfile=None):
        calls.append(command)
        output.write_text("partial pw.x evidence\n", encoding="utf-8")
        (exitfile.parent / "saved-wavefunctions").write_bytes(b"retain")
        if raised is not None:
            raise raised
        return dict(rc=1, stop_reason=reason, wall_seconds=5)
    monkeypatch.setattr(batch, "execute", execute)
    assert batch.run(spec, root, 1, pseudo, root / "qe") == 10
    receipt = json.loads((directory / (job["job"] + ".qc.json")).read_text(encoding="utf-8"))
    assert receipt["status"] == status and len(calls) == 1
    assert (directory / (job["job"] + "." + status)).is_file()
    assert (Path(receipt["scratch_retained"]) / "saved-wavefunctions").read_bytes() == b"retain"
    assert receipt["output_sha256"] == batch.digest(directory / (job["job"] + ".out"))
    with pytest.raises(ValueError, match="prior artifact"):
        batch.validate(spec, root, row=1, pseudo=pseudo)


def test_success_requires_projection_and_retained_density(launch, monkeypatch):
    spec, root, pseudo = launch
    job = spec["jobs"][0]
    directory = root / "runs" / job["manifest_dir"]
    calls = []
    def execute(command, output, cwd, env, seconds, max_iterations=None, exitfile=None):
        calls.append(command)
        if len(calls) == 1:
            output.write_text(output_text(), encoding="utf-8")
            save = exitfile.parent / (job["prefix"] + ".save")
            save.mkdir()
            (save / "data-file-schema.xml").write_text("<xml/>", encoding="utf-8")
            (save / "charge-density.dat").write_bytes(b"density")
        else:
            output.write_text("Lowdin Charges\nAtom # 1: total charge = 6.0, s = 2.0\n"
                              "Atom # 2: total charge = 6.0, s = 2.0\nSpilling Parameter: 0.001\nJOB DONE.\n", encoding="utf-8")
        return dict(rc=0, stop_reason=None, wall_seconds=11)
    monkeypatch.setattr(batch, "execute", execute)
    assert batch.run(spec, root, 1, pseudo, root / "qe") == 0
    receipt = json.loads((directory / (job["job"] + ".qc.json")).read_text(encoding="utf-8"))
    assert receipt["status"] == "COMPLETE" and len(calls) == 2
    assert receipt["projection"]["status"] == "VALID_PROJECTION"
    assert Path(receipt["scratch_retained"]).is_dir()
