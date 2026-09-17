"""S5 evidence failures, common-member cancellation and nonlinear CHE estimator."""
import copy
import math
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import p_beef_readout as beef

S0 = ROOT / "runs/s0/a_beef"


def banked():
    return (S0 / "slab__beefcalc.out").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", ["slab__beefcalc", "slab__beefhub"])
def test_banked_ensemble_blocks_and_units(name):
    record = beef.check_output(S0 / (name + ".out"))
    assert record["status"] == "VALID_BEEF", record
    assert record["emitted_members"] == 2000
    assert len(record["xc_contributions_Ry"]) == 32
    assert record["xc_contributions_eV"][0] == pytest.approx(record["xc_contributions_Ry"][0] * beef.RY_EV)
    if name == "slab__beefcalc":
        assert record["energy_Ry"] == -1644.81657836
        assert record["xc_contributions_Ry"][0] == -183.99770682466055
        assert record["xc_contributions_Ry"][-1] == -15.135345834650877
        assert "IEEE_UNDERFLOW_FLAG" in record["warnings"]


@pytest.mark.parametrize("name", ["slab__beefctl", "slab__beefens"])
def test_banked_negative_controls(name):
    assert beef.check_output(S0 / (name + ".out"))["status"] == "INVALID_BEEF"


@pytest.mark.parametrize("suffix", ["convergence NOT achieved", "Error in routine foo",
    "IEEE_INVALID_FLAG", "IEEE_OVERFLOW_FLAG", "IEEE_DIVIDE_BY_ZERO", "IEEE_UNKNOWN_FLAG", "Maximum CPU time exceeded"])
def test_fatal_evidence_overrides_job_done(suffix):
    with pytest.raises(ValueError):
        beef.parse_text(banked() + "\n" + suffix)


@pytest.mark.parametrize("transform", [
    lambda t: t.replace("JOB DONE.", ""),
    lambda t: t + t,
    lambda t: t.replace("BEEFens 2000", "BEEFens 1999"),
    lambda t: t.replace("-0.149639967546234E+02", "NaN"),
    lambda t: t.replace("-0.149639967546234E+02", "1e999"),
    lambda t: t.replace("-0.149639967546234E+02", ""),
    lambda t: t.replace("-183.99770682466055", "Infinity"),
    lambda t: t.replace("32 :", "31 :"),
    lambda t: t.replace("convergence has been achieved", "convergence unknown"),
    lambda t: t.replace("!    total energy", "     total energy"),
    lambda t: t.replace("BEEF-VDW", "PBE"),
    lambda t: t.replace(" BEEF-vdW xc energy contributions", "\x00 BEEF-vdW xc energy contributions"),
])
def test_malformed_or_truncated_evidence_fails_closed(transform):
    with pytest.raises(ValueError):
        beef.parse_text(transform(banked()))


def test_missing_inputs_never_produce_sigma(tmp_path):
    report = beef.readout(tmp_path)
    assert not report["complete"]
    assert report["score"]["verdict"] == "PENDING OUTPUTS"
    assert all("sigma_eta_V" not in item for item in report["metals"].values())


def test_ase_totals_have_one_baseline_and_common_seed():
    np = pytest.importorskip("numpy")
    pytest.importorskip("ase")
    record = beef.check_output(S0 / "slab__beefcalc.out")
    absolute = beef.ensemble_totals(record)
    zero = copy.deepcopy(record)
    zero["energy_eV"] = 0.0
    delta = beef.ensemble_totals(zero)
    assert absolute.shape == (2000,)
    np.testing.assert_array_equal(absolute, delta + record["energy_eV"])
    np.testing.assert_array_equal(absolute, beef.ensemble_totals(record))


def test_member_maximum_precedes_sample_standard_deviation():
    pytest.importorskip("numpy")
    # CHE steps switch from step 2 (2 eV) to step 1 (3 eV).
    energies = dict(slab=[0, 0], H2=[0, 0], H2O=[0, 0],
                    OH=[1-.35, 3-.35], O=[3-.05, 4-.05], OOH=[4-.40, 4.5-.40])
    result = beef.summarize_members(energies)
    assert result["eta_members_V"] == pytest.approx([.77, 1.77])
    assert result["sigma_eta_V"] == pytest.approx(math.sqrt(.5))
    assert result["pls_histogram"] == {"1": 1, "2": 1, "3": 0, "4": 0}


def test_common_member_matching_includes_both_gases():
    np = pytest.importorskip("numpy")
    slab = np.array([-100., -70., -50.])
    water = np.array([-10., -6., -2.])
    h2 = np.array([-6., -1., -3.])
    energies = dict(slab=slab, H2=h2, H2O=water,
                    OH=slab+water-.5*h2+1-.35,
                    O=slab+water-h2+3-.05,
                    OOH=slab+2*water-1.5*h2+4-.40)
    result = beef.summarize_members(energies)
    assert result["sigma_eta_V"] == pytest.approx(0, abs=1e-12)
    energies["H2"] = h2[::-1]
    assert beef.summarize_members(energies)["sigma_eta_V"] > .1


def test_mismatched_member_counts_are_not_truncated():
    pytest.importorskip("numpy")
    energies = {s: [0., 0.] for s in ("slab", "OH", "O", "OOH", "H2", "H2O")}
    energies["H2"] = [0.]
    with pytest.raises(ValueError, match="member counts"):
        beef.summarize_members(energies)


@pytest.mark.parametrize("sigmas,verdict", [
    ({"Ru": .249, "Ir": .249, "Ti": .5}, "CONFIRMED"),
    ({"Ru": .25, "Ir": .249, "Ti": .299}, "MIDDLE BAND"),
    ({"Ru": .3, "Ir": .3, "Ti": .1}, "FALSIFIED"),
    ({"Ru": .249, "Ir": .249}, "CONFIRMED"),
    ({"Ru": .249, "Ir": .25}, "MIDDLE BAND"),
    ({"Ru": .3, "Ir": .3}, "FALSIFIED"),
    ({"Ru": .1}, "NOT SCOREABLE"), ({}, "WITHDRAWN-UNSCORED"),
])
def test_ladder_b_absolute_boundaries(sigmas, verdict):
    assert beef.ladder_b(sigmas)["verdict"] == verdict


def test_base_ladder_rejects_cr_extension():
    with pytest.raises(ValueError):
        beef.ladder_b({"Ru": .1, "Ir": .1, "Ti": .1, "Cr": .1})
