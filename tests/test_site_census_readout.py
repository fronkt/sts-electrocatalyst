"""Census readout: the two retained 2026-09-06 chains stand in for census results.

The equiatomic chain reproduces its banked row (eta within 4.6e-10 V, one Cr site); the leader
chain is a deliberately different site (seed 0 instead of the banked seed 1) and must read
NOT REPRODUCED with the number. Missing results are refused unless --partial."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import shutil
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from scripts import site_census_build_manifests as build  # noqa: E402
from scripts import site_census_plan as plan  # noqa: E402
from scripts import site_census_readout as readout  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "results/cr_site_chains_2026-09-06"
ARMS = {"equiatomic": "Fe25Co25Ni25Cr25", "leader": "Ni31Cr29Cu5Mn35"}
OUTPUTS = ("per_site.json", "reproduction.json", "ranking.json", "distribution.json")


@pytest.fixture
def census(tmp_path):
    for arm in ARMS:
        if not (BANK / f"{arm}_result.json").exists():
            pytest.skip("retained chains absent")
    manifests, results = tmp_path / "manifests", tmp_path / "results"
    manifests.mkdir()
    results.mkdir()
    for arm, formula in ARMS.items():
        shutil.copy(BANK / f"{arm}_manifest.json", manifests / f"mpa0__{formula}.json")
        shutil.copy(BANK / f"{arm}_result.json", results / f"mpa0__{formula}_result.json")
    return manifests, results, tmp_path / "readout"


def run(census, *extra):
    manifests, results, out = census
    argv = ["--manifest-dir", str(manifests), "--result-dir", str(results), "--out-dir", str(out),
            "--box-source", str(plan.BOX_SOURCE), *extra]
    assert readout.main(argv) == 0
    return {name: json.loads((out / name).read_text(encoding="utf-8")) for name in OUTPUTS}


def test_refuses_without_partial_when_a_manifest_lacks_a_result(census):
    manifests, results, out = census
    (results / "mpa0__Ni31Cr29Cu5Mn35_result.json").unlink()
    with pytest.raises(RuntimeError, match="census incomplete"):
        readout.main(["--manifest-dir", str(manifests), "--result-dir", str(results),
                      "--out-dir", str(out), "--box-source", str(plan.BOX_SOURCE)])
    assert not out.exists()
    payload = run(census, "--partial")
    assert payload["reproduction.json"]["partial"] is True
    assert [m["stem"] for m in payload["reproduction.json"]["missing"]] == ["mpa0__Ni31Cr29Cu5Mn35"]
    assert payload["reproduction.json"]["decisive_site"]["status"] == "pending"


def test_refuses_foreign_manifest_names(census):
    manifests, results, out = census
    shutil.copy(manifests / "mpa0__Fe25Co25Ni25Cr25.json", manifests / "stray__Fe25Co25Ni25Cr25.json")
    with pytest.raises(ValueError, match="outside the census layout"):
        run(census, "--partial")
    (manifests / "stray__Fe25Co25Ni25Cr25.json").unlink()
    shutil.copy(manifests / "mpa0__Fe25Co25Ni25Cr25.json", manifests / "mh1__Fe25Co25Ni25Cr25.json")
    with pytest.raises(ValueError, match="outside the census layout"):
        run(census, "--partial")


def test_refuses_a_result_whose_manifest_id_differs(census):
    manifests, results, out = census
    path = results / "mpa0__Fe25Co25Ni25Cr25_result.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["manifest_id"] = "0" * 64
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="manifest_id differs"):
        run(census)


def test_reproduction_verdicts_and_numbers(census):
    payload = run(census, "--partial")  # both results present; --partial is harmless
    repro = payload["reproduction.json"]
    assert repro["partial"] is False and repro["missing"] == []
    eq = repro["reproduction"]["Fe25Co25Ni25Cr25"]
    assert eq["verdict"] == "REPRODUCED"
    assert abs(eq["eta_difference_V"]) < 4.6e-10
    assert math.isclose(eq["eta_min_V"], 0.4530565522419163, abs_tol=1e-15)
    assert math.isclose(eq["banked_eta_V"], 0.4530565517906915, abs_tol=1e-15)
    assert eq["winner"] == dict(seed=2, site_index=0, site_metal="Cr",
                                bonds=dict(OH=1.8085509324280893, O=1.5894617507495872, OOH=1.9754136641577082),
                                starts=dict(OH="pull2.10", O="pull2.10", OOH="pull2.10"))
    assert all(abs(v) < 1e-3 for v in eq["bond_differences_A"].values())
    assert eq["winner_ooh_classification"]["category"] == "NORMAL"
    assert eq["winner_ooh_classification"]["intact"] is True
    assert eq["winner_ooh_classification"]["o_o_class"] == "OOH_LIKE"
    assert eq["winner_site_intact"] is False and eq["winner_site_adsorbate_intact"] is True  # *O reconstruction flag
    assert eq["winner_site_unconverged_states"] == 0
    lead = repro["reproduction"]["Ni31Cr29Cu5Mn35"]
    assert lead["verdict"] == "NOT REPRODUCED"
    assert math.isclose(lead["eta_difference_V"], 0.9780789066094675 - 0.43999606379672596, abs_tol=1e-15)
    assert lead["winner"]["seed"] == 0 and lead["banked_winner"]["seed"] == 1
    assert lead["winner_ooh_classification"]["category"] == "DESORPTION"
    assert lead["winner_ooh_classification"]["o_o_class"] == "O2_LIKE"
    assert lead["winner_ooh_classification"]["h_location"] == "H_TRANSFERRED"
    assert lead["winner_ooh_classification"]["pathway_state"] == "undefined"
    decisive = repro["decisive_site"]
    assert decisive["status"] == "read" and decisive["winner_seed"] == 0
    assert decisive["winner_seed_matches_banked"] is False
    assert decisive["ooh_readout"] == "DESORPTION" and decisive["winner_pathway"] == "undefined"


def test_per_site_and_ranking_outputs(census):
    payload = run(census)
    rows = [r for r in payload["per_site.json"]["rows"] if r.get("seed") is not None]
    assert len(rows) == 2
    by_formula = {r["formula"]: r for r in rows}
    eq = by_formula["Fe25Co25Ni25Cr25"]
    assert eq["all_states_intact"] is False and eq["all_states_adsorbate_intact"] is True
    assert eq["reconstructed_states"] == 1 and eq["unconverged_states"] == 0 and eq["weak_states"] == 0
    assert eq["OOH_o_o_class"] == "OOH_LIKE" and eq["OOH_h_carrier"] == "terminal_O" and eq["pathway"] == "cus"
    assert eq["arm"] == "CENSUS-1"
    lead = by_formula["Ni31Cr29Cu5Mn35"]
    assert lead["OOH_category"] == "DESORPTION" and lead["OOH_binding_metal"] == "Ni" and lead["pathway"] == "undefined"
    assert math.isclose(lead["OOH_slab_max_A"], 0.35379803260877163, abs_tol=1e-9)
    csv_text = (Path(payload["reproduction.json"]["manifests_read"]["mpa0__Fe25Co25Ni25Cr25"]["result"]).name)
    rank = payload["ranking.json"]["ranking"]
    assert rank["scores_docs43_prediction"] is False
    assert rank["banked_order"] == list(plan.GATED_SIX)
    assert "extreme-value" in rank["site_set"]
    assert [g["pair"] for g in rank["banked_adjacent_gaps"]][0] == ["Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25"]
    assert math.isclose(rank["banked_adjacent_gaps"][0]["gap_V"], 0.4530565517906915 - 0.43999606379672596, abs_tol=1e-15)
    orders = rank["orders"]
    assert set(orders) == {"banked", "intact_only", "adsorbate_intact_only", "two_pathway"}
    assert orders["banked"]["complete"] is False and orders["banked"]["kendall_tau_vs_banked"] is None
    assert orders["banked"]["values_V"]["Fe25Co25Ni25Cr25"] == 0.4530565522419163
    assert orders["intact_only"]["values_V"] == {}  # both retained *O states carry the reconstruction flag
    assert orders["adsorbate_intact_only"]["values_V"] == {"Fe25Co25Ni25Cr25": 0.4530565522419163}
    assert orders["two_pathway"]["values_V"] == {"Fe25Co25Ni25Cr25": 0.4530565522419163}
    assert "Ni31Cr29Cu5Mn35" in orders["two_pathway"]["excluded"]  # desorbed endpoint: pathway undefined
    per = rank["per_formula"]["Ni31Cr29Cu5Mn35"]
    assert per["n_undefined_pathway_sites"] == 1 and per["n_bridge_sites"] == 0 and per["n_reconstructed_sites"] == 1
    ens = rank["ensemble_spread"]["Fe25Co25Ni25Cr25"]
    assert ens["n_models"] == 1 and ens["spread_V"] == 0.0 and ens["min_site_eta_by_model_V"] == {"mpa0": 0.4530565522419163}
    conv = rank["convergence"]
    assert conv["per_formula"]["Fe25Co25Ni25Cr25"]["mpa0"]["n_unconverged_sites"] == 0
    assert conv["per_model"]["mpa0"] == dict(n_sites=2, n_unconverged_sites=0)
    assert rank["o2_records_supplied"] is False
    assert csv_text.endswith("_result.json")


def test_distribution_readout_uses_census1_and_census3_sites(census):
    payload = run(census)
    dist = payload["distribution.json"]["distribution"]["per_formula"]
    eq = dist["Fe25Co25Ni25Cr25"]
    assert eq["manifests"] == ["mpa0__Fe25Co25Ni25Cr25"] and eq["n_sites"] == 1
    assert eq["all_sites"]["n"] == 1 and eq["all_sites"]["std"] is None
    assert math.isclose(eq["all_sites"]["min"], 0.4530565522419163, abs_tol=1e-15)
    assert eq["intact_sites"]["n"] == 0
    assert eq["expected_min_vs_k"] == [dict(k=1, expected_min=0.4530565522419163)]
    assert math.isclose(eq["twelve_site_min_V"], 0.4530565522419163, abs_tol=1e-15)
    assert eq["o_o_class_counts"] == {"OOH_LIKE": 1}
    assert dist["Cu26Ni9Cr31Co33"]["n_sites"] == 0 and dist["Cu26Ni9Cr31Co33"]["twelve_site_min_V"] is None


def test_o2_records_add_a_diagnostic_and_change_no_rule(census, tmp_path):
    manifests, results, out = census
    leader = json.loads((results / "mpa0__Ni31Cr29Cu5Mn35_result.json").read_text(encoding="utf-8"))
    site = leader["results"][0]["row"]["per_site_records"][0]
    e = site["energies_eV"]
    records = {"Ni31Cr29Cu5Mn35": {"0/0": dict(energy_eV=e["OOH"] + 0.5 * e["H2"] - 0.6, E_O2_gas_eV=-9.0,
                                              converged_by_force=True)}}
    path = tmp_path / "o2.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    payload = run(census, "--o2-records", str(path))
    rank = payload["ranking.json"]["ranking"]
    assert rank["o2_records_supplied"] is True
    lead = rank["per_formula"]["Ni31Cr29Cu5Mn35"]
    assert lead["banked"] == 0.9780789066094675 and lead["two_pathway"] is None and lead["intact_only"] is None
    frag = lead["o2_fragment_diagnostics"]["0/0"]
    assert frag["status"] == "computed" and frag["role"].startswith("diagnostic")
    assert math.isclose(frag["dG_ads_O2_eV"], e["OOH"] + 0.5 * e["H2"] - 0.6 - e["slab"] + 9.0 + 0.05, abs_tol=1e-12)


def test_queue_order_and_layout():
    stems = plan.expected_stems()
    assert len(stems) == 12 + 1 + 36 + 54 == 103
    assert stems[:6] == [f"mpa0__{f}" for f in plan.GATED_SIX]
    assert stems[12] == plan.ENDMEMBER_MANIFEST
    assert stems[13:19] == [f"omat0__{f}" for f in plan.GATED_SIX]
    assert stems[-1] == "mpa0_ext__Cu22Fe30Co32Mn15__s27-29"
    assert plan.ENSEMBLE_TAGS == ("omat0", "mp0", "matpes") and "mh1" not in plan.MODEL_FILES
    assert plan.parse_stem("mpa0_ext__Fe25Co25Ni25Cr25__s03-05") == dict(arm="CENSUS-3", tag="mpa0", formula="Fe25Co25Ni25Cr25", block=(3, 5))
    assert plan.parse_stem("omat0__Fe25Co25Ni25Cr25")["arm"] == "CENSUS-2"
    assert plan.parse_stem(plan.ENDMEMBER_MANIFEST)["arm"] == "ENDMEMBER-2x2"
    assert [s for block in plan.EXT_BLOCKS for s in block] == list(range(3, 30))
    with pytest.raises(ValueError):
        plan.parse_stem("stray__Fe25Co25Ni25Cr25")
    with pytest.raises(ValueError, match="outside the expected census set"):
        plan.queue_order(["mpa0__Nope"])
    shuffled = list(reversed(stems))
    assert plan.queue_order(shuffled) == stems


def test_manifest_hash_list_matches_the_manifests_on_disk():
    if not plan.MANIFEST_HASHES.exists():
        pytest.skip("census manifests absent")
    lines = plan.MANIFEST_HASHES.read_text(encoding="utf-8").split("\n")[:-1]
    assert len(lines) == 103
    assert [line.split("  ")[1] for line in lines] == [f"manifests/{s}.json" for s in plan.expected_stems()]
    for line in lines:
        digest, name = line.split("  ")
        assert build.sha256_lf(plan.CENSUS_DIR / name) == digest


def test_hash_list_is_written_once_and_refused_when_stale(tmp_path, monkeypatch):
    monkeypatch.setattr(plan, "MANIFEST_DIR", tmp_path / "manifests")
    monkeypatch.setattr(plan, "MANIFEST_HASHES", tmp_path / "MANIFESTS.sha256")
    plan.MANIFEST_DIR.mkdir()
    (plan.MANIFEST_DIR / "mpa0__Fe25Co25Ni25Cr25.json").write_text("{}\n", encoding="utf-8")
    lines, action = build.write_hashes()
    assert action == "written" and len(lines) == 1
    assert build.write_hashes()[1] == "unchanged"
    (plan.MANIFEST_DIR / "mpa0__Fe25Co25Ni25Cr25.json").write_text("{ }\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        build.write_hashes()
    assert build.write_hashes(rehash=True)[1] == "written"
