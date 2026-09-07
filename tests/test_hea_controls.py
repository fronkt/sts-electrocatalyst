"""DFT control invariants: element identity, spin/U/UPF splits and paired perturbations."""
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "dft"))
import build_hea_controls as hc  # noqa: E402
import build_hea_panel as panel  # noqa: E402
import hea_deck as hd  # noqa: E402


@pytest.fixture(scope="module")
def states():
    return {s["label"]: s for s in panel.collect_states()}


def test_baseline_is_exact_established_protocol_with_isolated_prefix(states):
    s = states["leader_builder"]
    g = s["geometry"]
    text, row = hc.render_control(s, "atomic", "baseline")
    assert text == hd.render_deck(row["job"], g["symbols"], g["positions_A"], g["cell_A"], g["fixed_atom_indices"], "atomic")
    assert "  tprnfor = .true.\n" in text
    assert "  calculation = 'scf'\n" in text


@pytest.mark.parametrize("projector", hc.PROJECTORS)
def test_same_element_opposite_spin_labels_preserve_every_u_and_upf(states, projector):
    s = states["leader_builder"]
    text, row = hc.render_control(s, projector, "metal_alternating")
    p = hd.parse_deck(text)
    spin = row["spin"]
    assert p["positions"] == s["geometry"]["positions_A"]
    assert p["cell"] == s["geometry"]["cell_A"]
    for element in hd.METALS:
        labels = [x for x in spin["species"] if spin["element"][x] == element]
        if len(labels) == 2:
            assert spin["magnetization"][labels[0]] == -spin["magnetization"][labels[1]]
        for label in labels:
            assert p["upfs"][p["species"].index(label)] == hd.ELEMENTS[element]["pseudo"]
            if hd.ELEMENTS[element]["U"]:
                assert p["U"][label] == hd.ELEMENTS[element]["U"]
            else:
                assert label not in p["U"]
    assert any(value < 0 for value in p["mag"].values())
    assert [spin["element"][x] for x in p["symbols"]] == s["geometry"]["symbols"]
    assert p["hubbard_card"] == hd.CARD[projector]


@pytest.mark.parametrize("label,moment", [("leader_builder", 1.0), ("leader_pull2.10", 2.0)])
def test_only_fragment_oxygen_receives_fragment_polarization(states, label, moment):
    text, row = hc.render_control(states[label], "atomic", "fragment")
    spin = row["spin"]
    assert spin["fragment_atom_indices"] == [72, 73]
    assert spin["nominal_fragment_start_muB"] == moment
    assert spin["atom_labels"][72:] == ["O2", "O2", "H"]
    assert spin["magnetization"]["O2"] == pytest.approx(moment / 12)
    assert spin["magnetization"]["O1"] == spin["magnetization"]["H"] == 0
    assert "tot_magnetization" not in text
    assert "U O" not in text


def test_fragment_start_refuses_unclassified_or_intact_state(states):
    with pytest.raises(hd.BuildError, match="classified"):
        hc.render_control(states["equiatomic_pull2.10"], "atomic", "fragment")


@pytest.mark.parametrize("variant", list(hc.NUMERICAL))
def test_numerical_variants_change_one_setting_at_fixed_geometry(states, variant):
    s = states["leader_pull2.10"]
    baseline, _ = hc.render_control(s, "ortho", "baseline")
    control, row = hc.render_control(s, "ortho", variant)
    without_prefix = lambda t: [line for line in t.splitlines() if not line.startswith("  prefix = ")]
    before, after = without_prefix(baseline), without_prefix(control)
    assert len(before) == len(after)
    differences = [(a, b) for a, b in zip(before, after) if a != b]
    assert len(differences) == 1
    assert len(row["changed_settings"]) == 1
    p, q = hd.parse_deck(baseline), hd.parse_deck(control)
    for key in ("positions", "cell", "fixed", "symbols", "species", "U", "upfs", "mag"):
        assert p[key] == q[key]
    assert row["nk"] > 0 and hd.NP % row["nk"] == 0


def test_verification_rejects_missing_split_u_or_changed_pseudopotential(states):
    s = states["leader_builder"]
    text, row = hc.render_control(s, "atomic", "metal_alternating_fragment")
    bad_u = re.sub(r"^U Cr2-3d .*\n", "", text, flags=re.M)
    assert bad_u != text
    with pytest.raises(hd.BuildError, match="mapping"):
        hc.verify_control(bad_u, s, row["spin"], row["settings"]["mesh"], "atomic", hc.BASE_SETTINGS)
    bad_upf = text.replace(hd.ELEMENTS["Cr"]["pseudo"], hd.ELEMENTS["Ni"]["pseudo"], 1)
    with pytest.raises(hd.BuildError, match="mapping"):
        hc.verify_control(bad_upf, s, row["spin"], row["settings"]["mesh"], "atomic", hc.BASE_SETTINGS)


def test_plan_has_complete_numeric_pairs_unique_ids_and_hashed_requests(states):
    rows = hc.plan_controls(list(states.values()))
    assert len(rows) == len({r["job"] for r in rows}) == 48
    assert sum(r["variant"] == "baseline" for r in rows) == 8
    for projector in hc.PROJECTORS:
        for variant in hc.NUMERICAL:
            assert {r["state"] for r in rows if r["projector"] == projector and r["variant"] == variant} == set(hc.NUMERICAL_LABELS)
    m = hc.manifest_text(rows)
    assert hd.check_manifest_text(m)["n_rows"] == 48
    assert "# NP=128 NCONC=1\n" in m
    assert "NOT LICENSED" in m
    doc = json.loads(hc.request_text(rows))
    assert not doc["dft_executed"]
    assert doc["n_jobs"] == len(doc["requests"])
    for r in rows:
        assert r["sha256"] == hashlib.sha256(r["text"].encode()).hexdigest()
        assert r["md5"] in m and r["sha256"] in m
        assert r["source_json_sha256_lf"] == hd.sha256_lf(ROOT / r["source_json"])
        assert "\r" not in r["text"]
    assert all("text" not in r for r in doc["requests"])


def test_refuse_duplicate_state_labels_and_unsafe_labels(states):
    with pytest.raises(hd.BuildError, match="duplicate"):
        hc.plan_controls(list(states.values()) + [next(iter(states.values()))])
    s = copy.deepcopy(states["leader_builder"])
    s["label"] = "../../outside"
    with pytest.raises(hd.BuildError, match="unsafe"):
        hc.render_control(s, "atomic", "baseline")


def test_publish_preflights_all_files_before_any_write_and_check_requires_complete_set(tmp_path):
    a, b = tmp_path / "a.in", tmp_path / "b.in"
    b.write_bytes(b"existing\n")
    with pytest.raises(hd.BuildError, match="refusing overwrite"):
        hc.publish({a: "new\n", b: "drift\n"})
    assert not a.exists() and b.read_bytes() == b"existing\n"
    with pytest.raises(hd.BuildError, match="missing expected artifact"):
        hc.publish({a: "new\n"}, check_only=True)
    assert not a.exists()
    hc.publish({a: "new\n", b: "existing\n"})
    hc.publish({a: "new\n", b: "existing\n"}, check_only=True)
    with pytest.raises(hd.BuildError, match="CR"):
        hc.publish({tmp_path / "c": "bad\r\n"})


def test_cost_uses_original_element_counts_actual_mesh_and_cutoff_scaling(states):
    s = states["leader_builder"]
    baseline_text, baseline = hc.render_control(s, "atomic", "baseline")
    c0 = hc.estimate_cost(s, baseline)
    _, split = hc.render_control(s, "atomic", "metal_alternating_fragment")
    cs = hc.estimate_cost(s, split)
    # Relabeling is not a change in electron count or physical cell volume.
    assert cs["plan_coreh"] == c0["plan_coreh"]
    assert cs["ram_GB_estimate"] == c0["ram_GB_estimate"]
    _, wfc = hc.render_control(s, "atomic", "wfc100")
    cw = hc.estimate_cost(s, wfc)
    assert cw["plan_coreh"] / c0["plan_coreh"] == pytest.approx((100 / 80) ** 1.5)
    _, dense = hc.render_control(s, "atomic", "k6x3")
    ck = hc.estimate_cost(s, dense)
    assert ck["plan_coreh"] > c0["plan_coreh"]
    assert ck["ram_GB_estimate"] > c0["ram_GB_estimate"]
    assert c0["monitoring_iteration_trigger"] == 126
    assert c0["monitoring_wall_trigger_s"] == 3 * c0["plan_wall_s"]
    assert not c0["watchdog_implemented"]
    assert c0["node_memory_GB"] == 237


def test_smoke_manifest_is_two_paired_endpoints_only(states):
    rows = hc.plan_controls(list(states.values()))
    subset = hc.smoke_rows(rows)
    assert {r["state"] for r in subset} == set(hc.NUMERICAL_LABELS)
    assert all(r["projector"] == "atomic" and r["variant"] == "baseline" for r in subset)
    assert hd.check_manifest_text(hc.manifest_text(subset))["n_rows"] == 2
    requests = json.loads(hc.request_text(rows))
    assert requests["smoke_jobs"] == [r["job"] for r in subset]


def test_metal_texture_reserves_fragment_slot_within_target_qe_species_limit(states):
    for s in states.values():
        _, plain = hc.render_control(s, "atomic", "metal_alternating")
        assert plain["ntyp"] <= 10
        if s["integrity"].get("expected_free_species_moment_muB") is not None:
            _, combined = hc.render_control(s, "atomic", "metal_alternating_fragment")
            assert combined["ntyp"] <= 10
            assert plain["spin"]["atom_labels"][:24] == combined["spin"]["atom_labels"][:24]
    _, equiatomic = hc.render_control(states["equiatomic_builder"], "atomic", "metal_alternating_fragment")
    assert equiatomic["ntyp"] == 10
    assert equiatomic["spin"]["split_metal_elements"] == ["Co", "Cr", "Fe"]
    assert equiatomic["spin"]["unsplit_eligible_metals"] == ["Ni"]


def test_dense_mesh_uses_documented_memory_fit_decomposition(states):
    for state in hc.NUMERICAL_LABELS:
        _, row = hc.render_control(states[state], "atomic", "k6x3")
        assert row["settings"]["mesh"] == [6, 3, 1]
        assert row["nk"] == row["decomposition"]["nk"] == 4
        assert row["decomposition"]["baseline_nk"] == 8
        assert row["decomposition"]["ranks_per_pool"] == 32
        c = hc.estimate_cost(states[state], row)
        assert c["planning_memory_fits_node"]
        assert c["ram_GB_estimate"] == pytest.approx(185.41183578085026)


def test_baseline_reference_hashes_exact_prefix_only_equivalence(states):
    ref = hc.baseline_reference(states["equiatomic_builder"], "ortho")
    original = (ROOT / ref["original_deck"]).read_bytes()
    assert ref["original_sha256"] == hashlib.sha256(original).hexdigest()
    companion, _ = hc.render_control(states["equiatomic_builder"], "ortho", "baseline")
    normalize = lambda t: re.sub(r"^  prefix = .*\n", "", t, flags=re.M)
    assert normalize(original.decode()) == normalize(companion)
    assert "Run one location only" in ref["reuse_policy"]
    assert ref["original_output"].endswith("equiatomic_builder__ortho.out")
    assert ref["original_lowdin"].endswith("equiatomic_builder__ortho.lowdin.txt")
