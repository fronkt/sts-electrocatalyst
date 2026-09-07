"""Complete ordered Lowdin tables, SCF validity, numerical fields and immutable raw files."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import hea_followup_qc as qc

INPUT = """&CONTROL
 calculation='scf'
/
&SYSTEM
 nat=2
/
ATOMIC_SPECIES
Cr 51.996 cr.UPF
O 15.999 o.UPF
ATOMIC_POSITIONS angstrom
Cr 0 0 0 0 0 0
O 0 0 2 1 1 1
"""
OUTPUT = """number of atoms/cell = 2
!    total energy = -10.00000000 Ry
convergence has been achieved in 3 iterations
Forces acting on atoms (cartesian axes, Ry/au):
 atom 1 type 1 force = 0.00000000 0.00000000 0.00000000
 atom 2 type 2 force = 0.10000000 0.00000000 0.00000000
 Total force = 0.10000000
 JOB DONE.
"""
PROJECTION = """Lowdin Charges:
 Atom # 1: total charge = 6.0000, s = 2.0000, d = 4.0000,
 spin up = 4.0000, s = 1.0000,
 spin up = 4.0000, d = 3.0000,
 spin down = 2.0000, s = 1.0000,
 spin down = 2.0000, d = 1.0000,
 polarization = 2.0000, s = 0.0000, d = 2.0000,
 Atom # 2: total charge = 6.0000, s = 2.0000, p = 4.0000,
 spin up = 3.0000, s = 1.0000, p = 2.0000,
 spin down = 3.0000, s = 1.0000, p = 2.0000,
 polarization = 0.0000, s = 0.0000, p = 0.0000,
 Spilling Parameter: 0.0022
 JOB DONE.
"""


@pytest.fixture
def files(tmp_path):
    paths = [tmp_path / name for name in ("test.run.in", "test.out", "test.projwfc.out")]
    for path, text in zip(paths, (INPUT, OUTPUT, PROJECTION)):
        path.write_text(text, encoding="utf-8")
    return paths


def test_high_residual_is_valid_and_projection_retains_correct_fields(files, tmp_path):
    infile, outfile, projection = files
    first = qc.audit_files(infile, outfile)
    assert first["status"] == "VALID_SCF"
    assert first["scf"]["geometry_stationarity"] == "ABOVE_THRESHOLD"
    assert first["scf"]["fmax_free_ev_A"] > 2
    before = [p.read_bytes() for p in files]
    target = tmp_path / "qc.json"
    assert qc.main(["--input", str(infile), "--output", str(outfile), "--projection", str(projection), "--json", str(target)]) == 0
    result = json.loads(target.read_text())
    assert result["status"] == "COMPLETE"
    atoms = result["projection"]["atoms"]
    assert [(a["index"], a["species"], a["charge_e"], a["moment_muB"]) for a in atoms] == [(0, "Cr", 6., 2.), (1, "O", 6., 0.)]
    assert atoms[0]["spin_up_e"] == 4 and atoms[0]["spin_down_e"] == 2
    assert atoms[0]["orbital_populations"]["spin up"] == {"s": 1., "d": 3.}
    assert result["projection_file"]["sha256_bytes"] == hashlib.sha256(before[2]).hexdigest()
    assert before == [p.read_bytes() for p in files]
    with pytest.raises(FileExistsError):
        qc.main(["--input", str(infile), "--output", str(outfile), "--json", str(target)])


@pytest.mark.parametrize("change", [
    lambda s: s.replace("JOB DONE.", ""),
    lambda s: s + "JOB DONE.\n",
    lambda s: s + "Error in routine\n",
    lambda s: s.replace("Lowdin Charges:", "Lowdin Charges:\nLowdin Charges:"),
    lambda s: s.replace("Spilling Parameter: 0.0022", ""),
    lambda s: s.replace("Spilling Parameter: 0.0022", "Spilling Parameter: NaN"),
    lambda s: s.replace("Spilling Parameter: 0.0022", "Spilling Parameter: 1e999"),
    lambda s: s.replace("Atom # 2", "Atom # 1"),
    lambda s: s.replace("Atom # 2", "Atom # 3"),
    lambda s: s.replace("total charge = 6.0000", "total charge = NaN", 1),
    lambda s: s.replace("total charge = 6.0000", "total charge = 1e999", 1),
    lambda s: s.replace("polarization = 2.0000", "polarization = *****"),
    lambda s: s.replace("polarization = 2.0000, s = 0.0000, d = 2.0000,\n", ""),
    lambda s: s.replace("polarization = 2.0000", "polarization = 3.0000"),
    lambda s: s.replace("spin up = 4.0000, d", "spin up = 5.0000, d"),
    lambda s: s.replace("spin down = 2.0000, d = 1.0000,\n", ""),
    lambda s: s.replace("spin down = 2.0000, d = 1.0000,\n", "").replace("spin up = 4.0000, d = 3.0000,\n", ""),
    lambda s: s.replace("spin up = 4.0000, d = 3.0000", "spin up = 4.0000, d = Inf"),
    lambda s: s.replace("polarization = 0.0000, s = 0.0000, p = 0.0000,", "polarization = 0.0000, s = 0.0000, p = 0.0000,\npolarization = 0.0000,"),
    lambda s: s.replace(" Spilling Parameter:", " Atom # 3: total charge = 1.0,\n Spilling Parameter:"),
    lambda s: s.replace("JOB DONE.", "JOB DONE.\n Atom # 3: total charge = 1.0,"),
    lambda s: s.replace(" Atom # 2:", " malformed line\n Atom # 2:"),
])
def test_partial_malformed_nonfinite_or_inconsistent_projection_rejected(change):
    with pytest.raises(ValueError):
        qc.projection_text(change(PROJECTION), ["Cr", "O"])


def test_nonconvergence_and_truncation_return_rejected_json(files, tmp_path):
    infile, outfile, projection = files
    outfile.write_text(OUTPUT + "convergence NOT achieved\n")
    result = tmp_path / "rejected.json"
    assert qc.main(["--input", str(infile), "--output", str(outfile), "--projection", str(projection), "--json", str(result)]) == 2
    assert json.loads(result.read_text())["status"] == "REJECTED"
    outfile.write_text(OUTPUT)
    projection.write_text(PROJECTION.replace("JOB DONE.", ""))
    assert qc.audit_files(infile, outfile, projection)["status"] == "REJECTED"
    outfile.unlink()
    assert qc.audit_files(infile, outfile)["status"] == "REJECTED"


def test_raw_path_cannot_be_json_target(files):
    infile, outfile, _ = files
    before = outfile.read_bytes()
    with pytest.raises(SystemExit):
        qc.main(["--input", str(infile), "--output", str(outfile), "--json", str(outfile)])
    assert outfile.read_bytes() == before


def test_fortran_exponents_and_decimal_rounding_are_accepted():
    text = PROJECTION.replace("6.0000", "6.0000D+00").replace("2.0000", "2.0000d0")
    assert qc.projection_text(text, ["Cr", "O"])["atoms"][0]["moment_muB"] == 2
    # Three separately printed totals need not sum to an exact last decimal.
    text = PROJECTION.replace("total charge = 6.0000", "total charge = 6.0001", 1)
    assert qc.projection_text(text, ["Cr", "O"])["atoms"][0]["charge_e"] == 6.0001


@pytest.mark.parametrize("job", ["hc__leader_builder__atomic__baseline", "hc__leader_pull2.10__atomic__baseline"])
def test_banked_pilot_scf_and_all_75_projection_rows(job):
    folder = ROOT / "runs/hea/controls_2026-09-07"
    paths = [folder / (job + suffix) for suffix in (".run.in", ".out", ".projwfc.out")]
    if not all(p.is_file() for p in paths):
        pytest.skip("banked pilot output files are not present in this checkout")
    result = qc.audit_files(*paths)
    assert result["status"] == "COMPLETE", result["reasons"]
    assert result["scf"]["geometry_stationarity"] == "ABOVE_THRESHOLD"
    assert len(result["projection"]["atoms"]) == 75
    assert [a["index"] for a in result["projection"]["atoms"]] == list(range(75))
    assert result["projection"]["atoms"][-1]["species"] == "H"


def test_overflowing_derived_force_rejected_with_finite_json(files, tmp_path):
    infile, outfile, _ = files
    outfile.write_text(OUTPUT.replace("0.10000000 0.00000000 0.00000000", "1e308 0.00000000 0.00000000"))
    target = tmp_path / "overflow.json"
    assert qc.main(["--input", str(infile), "--output", str(outfile), "--json", str(target)]) == 2
    assert json.loads(target.read_text())["status"] == "REJECTED"
