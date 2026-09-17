"""Ru PP bands, fixed selection, and false-success rejection (docs/89)."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dft import ru_pp_readout as ru
from dft.qe_qc import RY_EV


def output(tmp_path, *, text=None, md5=ru.NEW_MD5, extra=""):
    p = tmp_path / "job.out"
    p.with_suffix(".in").write_text("&CONTROL\n calculation = 'scf'\n/\n")
    if text is None:
        text = (
            "PseudoPot. # 1 for Ru read from file:\n /pseudo/ru.UPF\n"
            f" MD5 check sum: {md5}\n"
            "!    total energy = -100.00000000 Ry\n"
            " convergence has been achieved in 12 iterations\n"
            + extra + "\n JOB DONE.\n"
        )
    p.write_text(text)
    return p


@pytest.mark.parametrize("extra", [
    "convergence NOT achieved after 200 iterations: stopping",
    "Error in routine electrons (1): failed",
    "Program stopped by user request",
    "IEEE_INVALID_FLAG",
    "MPI_ABORT was invoked",
])
def test_job_done_does_not_rescue_failed_scf(tmp_path, extra):
    rec = ru.read_energy(output(tmp_path, extra=extra), ru.NEW_MD5)
    assert rec["status"] == "UNSCORED"
    assert rec["energy_eV"] is None


def test_job_done_without_energy_or_convergence_is_rejected(tmp_path):
    rec = ru.read_energy(output(tmp_path, text="JOB DONE.\n"))
    assert rec["energy_eV"] is None
    assert "no finite total energy" in rec["reasons"]
    assert "no explicit SCF convergence" in rec["reasons"]


def test_converged_scf_reads_ev_and_hash(tmp_path):
    rec = ru.read_energy(output(tmp_path), ru.NEW_MD5)
    assert rec["status"] == "SCOREABLE"
    assert rec["energy_eV"] == pytest.approx(-100 * RY_EV)
    assert len(rec["sha256"]) == 64


def test_wrong_ru_family_is_rejected(tmp_path):
    rec = ru.read_energy(output(tmp_path, md5=ru.OLD_MD5), ru.NEW_MD5)
    assert rec["status"] == "UNSCORED"


def test_source_match_guards_geometry_and_hubbard(tmp_path):
    source = tmp_path / "slab__u900.in"
    target = tmp_path / "slab__u900_gbrv.in"
    original = (
        "prefix = 'slab__u900'\nRu 101.070 " + ru.OLD_PP + "\n"
        "ATOMIC_POSITIONS angstrom\nRu 0 0 1\nHUBBARD (atomic)\nU Ru-4d 9.0000\n"
    )
    source.write_text(original)
    changed = original.replace("slab__u900'", "slab__u900_gbrv'").replace(ru.OLD_PP, ru.NEW_PP)
    target.write_text(changed)
    assert ru.deck_pair_check(target, source) == []
    target.write_text(changed.replace("Ru 0 0 1", "Ru 0 0 2"))
    assert ru.deck_pair_check(target, source)
    target.write_text(changed.replace("9.0000", "6.7300"))
    assert ru.deck_pair_check(target, source)


@pytest.mark.parametrize("q, expected", [
    (0.0, "MIDDLE"),
    (0.08444, "MIDDLE"),
    (0.08445, "CONFIRMS-COMPARABILITY"),
    (0.09225, "CONFIRMS-COMPARABILITY"),
    (0.099999, "CONFIRMS-COMPARABILITY"),
    (0.100, "PP-SENSITIVE"),
    (0.11, "PP-SENSITIVE"),
])
def test_primary_bands_preserve_absolute_floor_and_both_shift_directions(q, expected):
    assert ru.primary_band(q) == expected


def test_primary_uses_only_four_endpoints_and_cancels_common_offsets():
    energies = {
        "u000": {"s0_OH": 10.0, "s0_OOH": 13.1801},
        "u900": {"s0_OH": 110.0, "s0_OOH": 112.9956},
        "u673": {"s0_OH": -10000, "s0_OOH": 10000},
    }
    readout = ru.primary_readout(energies)
    assert readout["span_over_2_V"] == pytest.approx(0.09225)
    assert readout["band"] == "CONFIRMS-COMPARABILITY"
    energies["u000"]["s0_OH"] += 500
    energies["u000"]["s0_OOH"] += 500
    assert ru.primary_readout(energies)["span_over_2_V"] == pytest.approx(0.09225)
    del energies["u900"]["s0_OOH"]
    missing = ru.primary_readout(energies)
    assert missing["status"] == "UNSCORED"
    assert missing["missing_or_failed"] == ["u900/s0_OOH"]


@pytest.mark.parametrize("eta, band", [
    (0.39399, "CLEARS-MEASURED-ERROR-CLASSES"),
    (0.394, "INVERTED-WITHIN-CELL-CLASS"),
    (0.554, "INVERTED-WITHIN-CELL-CLASS"),
    (0.55401, "PP-CONDITIONAL"),
    (0.9, "PP-CONDITIONAL"),
])
def test_u9_margin_sign_and_inclusive_edges(eta, band):
    assert ru.secondary_band("u900", eta)["band"] == band


@pytest.mark.parametrize("eta, band", [
    (0.587, "COMPARABLE"), (0.987, "COMPARABLE"),
    (0.58699, "PP-CONDITIONAL"), (0.98701, "PP-CONDITIONAL"),
])
def test_u0_both_directions(eta, band):
    assert ru.secondary_band("u000", eta)["band"] == band


@pytest.mark.parametrize("eta, band", [
    (0.413, "PP-ROBUST"), (0.637, "TIE-NO-CORROBORATION"), (0.8, "OPPOSITE-SIGN"),
])
def test_xu_sign_and_exact_tie(eta, band):
    assert ru.secondary_band("u673", eta)["band"] == band


def test_che_reads_all_states_and_retains_negative_fourth_step():
    # H2=-2, H2O=-10; these chosen totals independently imply
    # dG(OH,O,OOH)=(1.0, 3.0, 5.0), giving steps=(1,2,2,-.08).
    states = {"slab": -100, "s0_OH": -108.35, "s0_O": -105.05, "s0_OOH": -112.4}
    row = ru.eta_readout(states, {"H2": -2, "H2O": -10})
    assert row["steps_eV"] == pytest.approx([1, 2, 2, -0.08])
    assert row["eta_V"] == pytest.approx(0.77)
    assert ru.eta_readout(states, {"H2": -2})["status"] == "UNSCORED"
    del states["s0_O"]
    assert ru.eta_readout(states, {"H2": -2, "H2O": -10})["status"] == "UNSCORED"


def test_existing_oncv_bank_reproduces_registered_primary_and_che():
    # Fixed bank regression independent of whether the new control has run.
    energies = {}
    for u in ru.RUNGS:
        energies[u] = {}
        for state in ru.STATES:
            path = ru.ROOT / "runs/a0/main/Ru" / (state + "__" + u + ".out")
            rec = ru.read_energy(path, ru.OLD_MD5)
            assert rec["status"] == "SCOREABLE", rec
            energies[u][state] = rec["energy_eV"]
    result = ru.primary_readout(energies)
    assert result["span_over_2_V"] == pytest.approx(0.09224816402274882, abs=1e-9)
    gas = {g: ru.read_energy(ru.ROOT / "runs/Ru_anchor" / (g + ".out"))["energy_eV"]
           for g in ("H2", "H2O")}
    for u, eta in ru.ETA_RU.items():
        assert ru.eta_readout(energies[u], gas)["eta_V"] == pytest.approx(eta, abs=0.0005)


def test_empty_local_tree_is_unscored_and_historical_verdicts_stay(tmp_path):
    result = ru.build_readout(tmp_path)
    assert result["readiness"] == "INCOMPLETE"
    assert result["primary"]["status"] == "UNSCORED"
    assert result["control_scoreable_outputs"] == 0
    assert result["unchanged_banked_verdicts"] == {"A7.3": "NOT MET at 3 of 6", "A6.3": "INVERTED"}


def test_cli_refuses_historical_output_paths(tmp_path):
    for target in (tmp_path / "docs/figs/a0main_readout.json", tmp_path / "runs/new.json"):
        with pytest.raises(SystemExit) as exc:
            ru.main(["--root", str(tmp_path), "--json", str(target)])
        assert exc.value.code == 2
        assert not target.exists()


@pytest.mark.parametrize("extension", [".KILLED", ".REJECTED"])
def test_explicit_terminal_sidecar_overrides_ru_success(tmp_path, extension):
    p = output(tmp_path)
    p.with_suffix(extension).write_text("terminal failure\n")
    rec = ru.read_energy(p, ru.NEW_MD5)
    assert rec["status"] == "UNSCORED" and rec["energy_eV"] is None
