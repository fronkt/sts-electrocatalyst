"""(a) DFT vs MACE at identical coordinates: population, pairing, energies and site projections."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "s2" / "lowtail_dft"))
sys.path.insert(0, str(ROOT / "src"))

import lt_common  # noqa: E402
import lt_mace  # noqa: E402
import lt_zero_compute as zc  # noqa: E402

RESULT = ROOT / "results/lowtail_dft_2026-09-16/zero_compute/zero_compute_readout.json"


def test_referencing_and_desorption_constants_come_from_their_sources():
    from hea_oer import data, referencing
    assert zc.ref_coefficients() == referencing._REF_COEFFS
    assert zc.desorbed_min_A() == data.M_O_DESORBED_MIN


def test_match_geometry_exact_tolerance_and_constraint_mismatch():
    geoms = dict(a=dict(symbols=["Cr", "O"], positions=[[0.0, 0.0, 1.0], [0.0, 0.0, 2.6]], cell=[[5.0, 0, 0], [0, 5.0, 0], [0, 0, 20.0]], fixed=[0]))
    parsed = dict(elements=["Cr", "O"], nat=2, positions=[[0.0, 0.0, 1.0], [0.0, 0.0, 2.6]], cell=[[5.0, 0, 0], [0, 5.0, 0], [0, 0, 20.0]], fixed=[0])
    assert zc.match_geometry(parsed, geoms) == ("a", 0.0, True)
    near = dict(parsed, positions=[[0.0, 0.0, 1.0 + 5e-9], [0.0, 0.0, 2.6]])
    name, diff, exact = zc.match_geometry(near, geoms)
    assert name == "a" and not exact and diff <= zc.MATCH_TOL_A
    assert zc.match_geometry(dict(parsed, positions=[[0.0, 0.0, 1.001], [0.0, 0.0, 2.6]]), geoms) is None
    assert zc.match_geometry(dict(parsed, fixed=[]), geoms) is None
    assert zc.match_geometry(dict(parsed, elements=["Mn", "O"]), geoms) is None


@pytest.fixture(scope="module")
def fake_run(tmp_path_factory):
    geoms, _ = zc.geometries()

    def fake_single_point(calc, symbols, positions, cell, pbc=(True, True, True)):
        g = next(v for v in geoms.values() if v["positions"] == [list(map(float, p)) for p in positions])
        return dict(energy_eV=g["stored_energy_eV"], forces_eV_A=np.zeros((len(symbols), 3)))

    original = lt_mace.single_point
    lt_mace.single_point = fake_single_point
    try:
        out = tmp_path_factory.mktemp("zc")
        result = zc.run(out, checkpoint=None, calc=object())
    finally:
        lt_mace.single_point = original
    return result, out


def test_population_on_the_face(fake_run):
    result, out = fake_run
    pop = result["population"]
    assert pop["banked_outputs"] == pop["used"] + pop["excluded"] + pop["unidentified"]
    assert pop["used"] == pop["accepted_by_own_readout"] and pop["unidentified"] == 0
    assert all(e["reasons"] for e in result["excluded"])
    assert (out / "zero_compute_readout.json").exists() and (out / "input_manifest.json").exists()
    assert result["geometry_checks"]["leader_pull2.10_equals_census_selected_OOH"]
    assert result["geometry_checks"]["replay_model_sha256_equals_census"]


def test_winner_O_site_forces_are_the_raw_dft_components(fake_run):
    result, _ = fake_run
    stem = ROOT / "runs/hea/winner_2026-09-10/g_80ebe76a616d61d6fecca57d1cd6c2ef27990771fbc3db9a8cfea6a4bf228e5c__atomic"
    stored = json.loads(stem.with_name(stem.name + ".qc.json").read_text(encoding="utf-8"))["scf"]["per_atom"]
    row = next(r for r in result["realizations"] if r["job"] == stem.name)
    site = row["site"]
    assert site["site_index"] == 16 and site["site_symbol"] == "Cr" and site["adsO_bound_to_site"]
    assert site["DFT"]["site_normal_eV_A"] == stored[16]["force_ev_A"][2]
    assert site["DFT"]["adsO_normal_eV_A"] == stored[72]["force_ev_A"][2]
    assert site["axial_O"]["index"] == 40
    assert site["geometry"]["site_lift_z_A"] == pytest.approx(0.8454922504474585, abs=1e-12)
    two = site["DFT_axial_two_body"]
    assert two["unit_members"] == [16, 72]
    assert two["site_away_from_axial_eV_A"] - two["axial_O_toward_site_eV_A"] == pytest.approx(site["DFT"]["axial_stretch_eV_A"], abs=1e-12)
    leader = next(r for r in result["realizations"] if r["geometry"] == "leader_OOH_builder")
    assert not leader["site"]["adsO_bound_to_site"] and leader["site"]["DFT_axial_two_body"]["unit_members"] == [16]


def test_energy_comparisons_reproduce_banked_readouts(fake_run):
    result, _ = fake_run
    for chain in result["winner_chain_energies"]:
        assert chain["status"] == "COMPUTED"
        for st, v in chain["electronic_adsorption"].items():
            assert v["DFT_minus_winner_readout_eV"] == pytest.approx(0.0, abs=1e-9)
    followup = lt_common.read_json(ROOT / "results/hea_followup_2026-09-07/completion_readout.json")
    banked = {(p["projector"], p["variant"]): p["gap_eV"] for p in followup["pairs"] if p.get("gap_eV") is not None}
    assert len(banked) == 6
    ours = {(p["projector"], p["variant"]): p["dE_DFT_eV"] for p in result["leader_OOH_pairs"] if p["series"] == "hc"}
    assert set(ours) == set(banked)
    for k in banked:
        assert ours[k] == pytest.approx(banked[k], abs=1e-9)
    assert all(p["dE_MACE_eV"] == pytest.approx(-2.281832858000712, abs=1e-9) for p in result["leader_OOH_pairs"])


def test_pending_endpoint_single_points_are_census_O_endpoints(fake_run):
    rows = fake_run[0]["pending_endpoint_single_points"]
    assert len(rows) == 4
    assert all(r["coordinates_equal_census_O_endpoint"] and r["in_approved_manifest"] and r["site_symbol"] == "Cr" for r in rows)
    assert sorted(r["status"] for r in rows) == ["ACCEPTED", "ACCEPTED", "ACCEPTED", "KILLED"]


def test_final_batch_all_accepted_rows_match_retained_geometries(fake_run):
    result, _ = fake_run
    final = [r for r in result["realizations"] if r["series"] == "final"]
    assert len(final) == 15
    assert all(r["coordinate_match"]["exact"] for r in final)
    reconstructed = [r for r in final if r["geometry"] in ("equiatomic_O", "leader_O")]
    assert len(reconstructed) == 3
    for row in reconstructed:
        site = row["site"]
        assert site["site_symbol"] == "Cr" and site["adsO_bound_to_site"]
        assert site["geometry"]["site_lift_z_A"] > 0.5
        assert 1.58 < site["geometry"]["site_to_adsO_A"] < 1.61


@pytest.mark.skipif(not RESULT.exists(), reason="banked zero-compute readout not present")
def test_reuse_mace_validates_old_eight_and_detects_coordinate_drift():
    geoms, checks = zc.geometries()
    reuse, proof = zc.reusable_mace(RESULT, geoms, checks["model"]["sha256_bytes"])
    assert len(reuse) == 8 and len(proof["geometries"]) == 8
    assert "winner_O" in reuse and "equiatomic_O" not in reuse and "leader_O" not in reuse
    geoms["winner_O"]["positions"][16][2] += 0.001
    with pytest.raises(ValueError, match="coordinates differ"):
        zc.reusable_mace(RESULT, geoms, checks["model"]["sha256_bytes"])


@pytest.mark.skipif(not RESULT.exists(), reason="banked zero-compute readout not present")
def test_banked_readout_mace_reproduces_census_and_hashes_are_current():
    d = json.loads(RESULT.read_text(encoding="utf-8"))
    assert d["mace_checkpoint"]["sha256"] == d["mace_checkpoint"]["census_sha256"]
    assert all(v["energy_minus_stored_eV"] == pytest.approx(0.0, abs=1e-9) for v in d["mace_geometries"].values())
    manifest = json.loads((RESULT.parent / "input_manifest.json").read_text(encoding="utf-8"))
    for item in manifest["inputs"]:
        if "path" in item and (ROOT / item["path"]).exists() and item["path"].startswith(("runs/", "results/site_census")):
            assert lt_common.sha256_file(ROOT / item["path"]) == item["sha256"], item["path"]
