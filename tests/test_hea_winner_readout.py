import sys
import copy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/dft"))
import hea_winner_readout as r


def energies():
    return {"atomic": dict(slab=-100, OH=-110, O=-108, OOH=-120),
            "ortho": dict(slab=-103, OH=-112.9, O=-110.8, OOH=-122.7)}


def test_shared_gas_cancellation_and_no_activity_claim():
    a = r.electronic_chains(energies(), dict(H2=-2, H2O=-10))
    b = r.electronic_chains(energies(), dict(H2=-5, H2O=-25))
    assert a["projector_delta_ortho_minus_atomic_eV"] == b["projector_delta_ortho_minus_atomic_eV"]
    assert a["projector_delta_ortho_minus_atomic_eV"] == pytest.approx(dict(OH=0.1, O=0.2, OOH=0.3))
    assert a["electronic_adsorption_eV"]["atomic"] == pytest.approx(dict(OH=-1, O=0, OOH=-3))
    assert a["overpotential"] is None
    assert not a["ranking_validated"] and not a["relaxed_free_energies"]
    assert not a["vibrational_or_entropy_corrections_added"]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), None, True])
def test_nonfinite_or_invalid_energy_refused(value):
    e = energies()
    e["atomic"]["O"] = value
    with pytest.raises(ValueError):
        r.electronic_chains(e, dict(H2=-2, H2O=-10))


@pytest.mark.parametrize("missing", ["slab", "OH", "O", "OOH"])
def test_incomplete_chain_refused(missing):
    e = energies()
    del e["ortho"][missing]
    with pytest.raises(ValueError):
        r.electronic_chains(e, dict(H2=-2, H2O=-10))


def test_reference_set_refused():
    with pytest.raises(ValueError):
        r.electronic_chains(energies(), dict(H2O=-10))


def test_printed_potential_identity():
    text = "PseudoPot. # 1 for H read from file:\nH.upf\nMD5 check sum: " + "a"*32
    assert r.printed_potentials(text) == {"H": "a"*32}
    for bad in ("", text + "\n" + text, text.replace("MD5 check sum:", "unknown:")):
        with pytest.raises(ValueError):
            r.printed_potentials(bad)


def test_geometry_preserves_coordinates_and_masks():
    t = "nat=2\nATOMIC_POSITIONS angstrom\nO 0 1 2 0 1 0\nH 1 2 3\nK_POINTS gamma\n"
    assert r.input_geometry(t) == (["O", "H"], [[0., 1., 2.], [1., 2., 3.]], [[0, 1, 0], [1, 1, 1]])
    for bad in (t.replace("angstrom", "bohr"), t.replace("H 1 2 3", "H nan 2 3"), t.replace("0 1 0", "0 2 0")):
        with pytest.raises(ValueError):
            r.input_geometry(bad)


@pytest.mark.parametrize("field,value", [("positions_A", [[0., 0., 0.1]]), ("cell_A", [[2., 0., 0.]]), ("species", ["Ni"]), ("if_pos", [[0, 0, 0]])])
def test_equal_summary_does_not_hide_geometry_difference(field, value):
    left = dict(geometry={"anomaly_class": "CLEAN SLAB"}, geometry_signature=dict(species=["Cr"], positions_A=[[0., 0., 0.]], cell_A=[[1., 0., 0.]], if_pos=[[1, 1, 1]]))
    right = copy.deepcopy(left)
    r.verify_pair_geometry(left, right)
    right["geometry_signature"][field] = value
    with pytest.raises(ValueError):
        r.verify_pair_geometry(left, right)


def test_readout_refuses_existing_destination(tmp_path):
    out = tmp_path / "readout.json"
    out.write_text("original")
    with pytest.raises(SystemExit):
        r.main(["--out", str(out)])
    assert out.read_text() == "original"


def gas_fixture(tmp_path):
    folder = tmp_path / "runs/Cr_slab"
    folder.mkdir(parents=True)
    (folder / "H2.in").write_text("calculation='relax'\nnat=2\nATOMIC_POSITIONS angstrom\nH 0 0 0\nH 0 0 0.74\n")
    text = """number of atoms/cell = 2
kinetic-energy cutoff = 80.0000 Ry
charge density cutoff = 640.0000 Ry
Exchange-correlation= PBE
PseudoPot. # 1 for H read from file:
H.upf
MD5 check sum: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
! total energy = -2.333 Ry
convergence has been achieved in 4 iterations
Forces acting on atoms
atom 1 type 1 force = 0.000000 0.000000 0.000100
atom 2 type 1 force = 0.000000 0.000000 -0.000100
Total force = 0.000141
bfgs converged in 1 scf cycles and 0 bfgs steps
Final energy = -2.333 Ry
JOB DONE.
"""
    (folder / "H2.out").write_text(text)
    return folder


def test_relax_reference_uses_relax_capable_geometry_parser(tmp_path):
    gas_fixture(tmp_path)
    row = r.gas_reference(tmp_path, "H2", {"H": "a"*32})
    assert row["status"] == "COMPATIBLE_EXISTING_REFERENCE"
    assert row["qc"]["calculation"] == "relax"


@pytest.mark.parametrize("change", ["invalid", "pseudo", "cutoff", "unconverged"])
def test_bad_reference_is_refused(tmp_path, change):
    folder = gas_fixture(tmp_path)
    p = folder / "H2.out"
    text = p.read_text()
    if change == "invalid":
        text += "IEEE_INVALID_FLAG\n"
    elif change == "pseudo":
        text = text.replace("a"*32, "b"*32)
    elif change == "cutoff":
        text = text.replace("80.0000", "60.0000")
    else:
        text += "convergence NOT achieved after 60 iterations: stopping\n"
    p.write_text(text)
    with pytest.raises(ValueError):
        r.gas_reference(tmp_path, "H2", {"H": "a"*32})
