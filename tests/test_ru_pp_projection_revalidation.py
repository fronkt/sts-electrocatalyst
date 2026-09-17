"""Projection format correction keeps numerical and artifact identity gates strict."""
import copy
import json
from pathlib import Path
import shutil
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dft.projection_qc import projection_check
from dft import ru_pp_projection_revalidation as review
from dft import ru_pp_readout as ru

# QE 7.5 nonmagnetic formatting: repeated totals precede separate s/p/d rows.
# Values reproduce the first two atoms of slab__u000_gbrv.projwfc.out.
NONMAG = """Program PROJWFC v.7.5
state # 1: atom 1 (Ru ), wfc 3 (l=2 m= 1)
Lowdin Charges:
 Atom # 1: total charge = 15.4891, s = 2.3266,
 Atom # 1: total charge = 15.4891, p = 6.7605, pz=2.2044, px=2.2999, py=2.2563,
 Atom # 1: total charge = 15.4891, d = 6.4020, dz2=0.8555, dxz=1.5295, dyz=1.4677, dx2-y2=1.7809, dxy=0.7684,
 Atom # 2: total charge = 15.4576, s = 2.3734,
 Atom # 2: total charge = 15.4576, p = 6.9289, pz=2.2868, px=2.3233, py=2.3188,
 Atom # 2: total charge = 15.4576, d = 6.1553, dz2=1.4975, dxz=0.8699, dyz=1.3338, dx2-y2=1.0170, dxy=1.4370,
 Spilling Parameter: 0.0018
 JOB DONE.
"""
SPIN = """Program PROJWFC v.7.5
Lowdin Charges:
 Atom # 1: total charge = 15.0, s = 2.0, p = 6.0, d = 7.0,
 spin up = 8.0, s = 1.0, p = 3.0, d = 4.0,
 spin down = 7.0, s = 1.0, p = 3.0, d = 3.0,
 polarization = 1.0,
 Atom # 2: total charge = 6.0, s = 2.0, p = 4.0, d = 0.0,
 spin up = 3.0, s = 1.0, p = 2.0, d = 0.0,
 spin down = 3.0, s = 1.0, p = 2.0, d = 0.0,
 polarization = 0.0,
 Spilling Parameter: 0.0018
 JOB DONE.
"""


def test_actual_nonmagnetic_layout_is_one_group_per_atom():
    result = projection_check(NONMAG, 2)
    assert result["nat"] == 2 and result["charge_rows"] == 6
    assert result["format"] == "split-angular-channels"
    assert result["atom_groups"] == [{"atom": 1, "total_charge": 15.4891, "rows": 3},
                                     {"atom": 2, "total_charge": 15.4576, "rows": 3}]


def test_spin_layout_and_benign_underflow_remain_supported():
    assert projection_check(SPIN + "IEEE_UNDERFLOW_FLAG IEEE_DENORMAL\n", 2)["format"] == "combined"


@pytest.mark.parametrize("mutate", [
    lambda x: "\n".join(l for l in x.splitlines() if "Atom # 2" not in l),
    lambda x: x.replace("Atom # 1", "Atom # 3"),
    lambda x: x.replace("Atom # 2", "Atom # 1"),
    lambda x: x.replace("15.4891", "15.4892", 1),
    lambda x: "\n".join(l for l in x.splitlines() if " d = " not in l),
    lambda x: x.replace("p = 6.7605", "s = 6.7605"),
    lambda x: x.replace("2.3266", "NaN"),
    lambda x: x.replace("2.3266", "Inf"),
    lambda x: x.replace("2.3266", "1e999"),
    lambda x: x.replace("2.3266", "****"),
    lambda x: x.replace("JOB DONE.", ""),
    lambda x: x + "JOB DONE.\n",
    lambda x: x + "IEEE_INVALID_FLAG\n",
    lambda x: x + "Error in routine projwave (1)\n",
])
def test_nonmagnetic_correction_does_not_admit_bad_projection(mutate):
    with pytest.raises(ValueError):
        projection_check(mutate(NONMAG), 2)


def test_nonconsecutive_duplicate_group_is_rejected():
    repeated = NONMAG.replace(" Spilling Parameter:", " Atom # 1: total charge = 15.4891, s = 2.3266,\n Spilling Parameter:")
    with pytest.raises(ValueError, match="atom groups"):
        projection_check(repeated, 2)


@pytest.fixture
def real_job(tmp_path):
    retrieval = ru.ROOT / review.EVIDENCE / "retrieval_initial.json"
    full = ru.ROOT / "runs/a0/ru_pp/Ru/slab__u000_gbrv.projwfc.out"
    if not retrieval.is_file() or not full.is_file():
        pytest.skip("full local run artifacts are not part of the compact test checkout")
    spec = json.loads((ru.ROOT / review.SPEC).read_text())
    job = spec["stages"]["ru_pp"]["jobs"][0]
    dest = tmp_path / "runs" / job["dir"]
    dest.mkdir(parents=True)
    for suffix in review.SUFFIXES + (".in",):
        shutil.copyfile(ru.ROOT / "runs" / job["dir"] / (job["job"] + suffix), dest / (job["job"] + suffix))
    source = tmp_path / "runs/a0/main/Ru/slab__u000.in"
    source.parent.mkdir(parents=True)
    shutil.copyfile(ru.ROOT / "runs/a0/main/Ru/slab__u000.in", source)
    retrieved = json.loads(retrieval.read_text())
    retained = json.loads((ru.ROOT / review.EVIDENCE / "retained_scratch_initial.json").read_text())
    return tmp_path, job, spec, retrieved, retained


def test_raw_run_revalidation_preserves_original_rejection_bytes(real_job):
    root, job, spec, retrieved, retained = real_job
    base = root / "runs" / job["dir"] / job["job"]
    original = {ext: ru.checksum(Path(str(base) + ext)) for ext in (".REJECTED", ".qc.json")}
    result = review.review_job(root, job, 1, spec, retrieved, retained)
    assert result["review_status"] == "VALIDATED_FORMAT_CORRECTION", result["reasons"]
    assert result["runner_status"] == "REJECTED"
    assert result["projection"]["nat"] == 18
    assert result["scf"]["energy_Ry"] == -1664.98147102
    assert {ext: ru.checksum(Path(str(base) + ext)) for ext in original} == original


@pytest.mark.parametrize("change", ["changed_raw", "missing_retention", "killed", "other_rejection"])
def test_review_fails_closed_when_required_evidence_changes(real_job, change):
    root, job, spec, retrieved, retained = real_job
    base = root / "runs" / job["dir"] / job["job"]
    if change == "changed_raw":
        with Path(str(base) + ".out").open("a") as handle:
            handle.write("unverified change\n")
    elif change == "missing_retention":
        retained = copy.deepcopy(retained)
        retained["rows"] = [r for r in retained["rows"] if r["stage"] != "ru_pp"]
    elif change == "killed":
        Path(str(base) + ".KILLED").write_text("wall limit\n")
    else:
        path = Path(str(base) + ".qc.json")
        receipt = json.loads(path.read_text())
        receipt["reason"] = "SCF iteration ceiling"
        path.write_text(json.dumps(receipt))
        retrieved = copy.deepcopy(retrieved)
        for row in retrieved["files"]:
            if row["path"] == path.relative_to(root).as_posix():
                row["sha256"] = ru.checksum(path)
    result = review.review_job(root, job, 1, spec, retrieved, retained)
    assert result["review_status"] == "UNSCORED" and result["energy_eV"] is None
    assert result["reasons"]



def test_one_partial_atom_cannot_hide_among_complete_split_groups():
    partial = "\n".join(line for line in NONMAG.splitlines()
                        if not ("Atom # 1" in line and (" p = " in line or " d = " in line)))
    with pytest.raises(ValueError, match="angular channel"):
        projection_check(partial, 2)


def test_job_done_before_lowdin_is_not_completion():
    misplaced = "JOB DONE.\n" + NONMAG.replace(" JOB DONE.\n", "")
    with pytest.raises(ValueError, match="out of order"):
        projection_check(misplaced, 2)



def test_all_single_s_rows_cannot_masquerade_as_combined_output():
    partial = "\n".join(line for line in NONMAG.splitlines() if " p = " not in line and " d = " not in line)
    with pytest.raises(ValueError, match="combined angular"):
        projection_check(partial, 2)


def test_combined_layout_checks_channels_against_basis():
    with_basis = SPIN.replace("Lowdin Charges:", "state # 1: atom 1 (Ru ), wfc 3 (l=2 m= 1)\nLowdin Charges:")
    assert projection_check(with_basis, 2)["format"] == "combined"
    with pytest.raises(ValueError, match="combined angular"):
        projection_check(with_basis.replace(", d = 7.0", "", 1), 2)


def test_unknown_ieee_flag_is_not_treated_as_benign_underflow():
    with pytest.raises(ValueError, match="unknown IEEE"):
        projection_check(NONMAG + "IEEE_UNKNOWN_EXCEPTION_FLAG\n", 2)
