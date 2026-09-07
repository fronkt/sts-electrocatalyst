"""Site-integrity classification: the two retained 2026-09-06 Cr-site chains as fixtures,
plus analytic checks of the thresholds, categories, the pathway bookkeeping and the
site-eta distribution statistics."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import sys

import numpy as np
import pytest
from ase import Atoms

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hea_oer import site_integrity as integrity  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "results/cr_site_chains_2026-09-06"
READOUT = BANK / "paired_readout/readout.json"


def load_row(arm):
    path = BANK / f"{arm}_result.json"
    if not path.exists():
        pytest.skip("retained chain absent: " + str(path))
    return json.loads(path.read_text(encoding="utf-8"))["results"][0]["row"]


def audited(arm, state):
    """The independently written geometry audit of the same state, for cross-checking distances."""
    if not READOUT.exists():
        pytest.skip("paired readout absent")
    readout = json.loads(READOUT.read_text(encoding="utf-8"))
    return readout["arms"][arm]["selected_geometry_audit"]["sites"][0]["states"][state]


# ---- the two retained chains -----------------------------------------------------------

def test_equiatomic_cr_site_ooh_is_intact_bound_ooh_like():
    row = load_row("equiatomic")
    site = integrity.classify_row(row)["sites"][0]
    assert (site["seed"], site["site_index"], site["initial_binding_metal"]) == (2, 0, "Cr")
    ooh = site["states"]["OOH"]
    ref = audited("equiatomic", "OOH")
    assert ooh["binding_metal_index"] == 16 and ooh["binding_metal"] == "Cr"
    assert ooh["binding_O"] == "proximal_O"
    assert math.isclose(ooh["m_o_A"], ref["oxygen_metal_contacts"]["proximal_O"]["distance_A"], abs_tol=1e-9)
    assert math.isclose(ooh["m_o_by_O_A"]["distal_O"], ref["oxygen_metal_contacts"]["distal_O"]["distance_A"], abs_tol=1e-9)
    assert math.isclose(ooh["m_o_A"], 1.9754136641577082, abs_tol=1e-9)
    assert ooh["bond_tier"] == "bound"
    assert math.isclose(ooh["o_o_A"], ref["distances_A"]["O_O_A"], abs_tol=1e-9)
    assert math.isclose(ooh["o_o_A"], 1.3721922129981474, abs_tol=1e-9)
    assert ooh["o_o_class"] == "OOH_LIKE"
    assert math.isclose(ooh["h_to_carrier_O_A"], ref["distances_A"]["distal_O_H_A"], abs_tol=1e-9)
    assert ooh["h_location"] == "ON_ADSORBATE" and ooh["h_carrier"] == "terminal_O"
    assert ooh["migration"] is False and ooh["dissociation"] is False
    assert ooh["reconstruction"] is False and ooh["converged_by_force"] is True
    assert ooh["category"] == "NORMAL" and ooh["intact"] is True and ooh["pathway_state"] == "*OOH"
    assert site["states"]["OH"]["pathway_state"] == "*OH" and site["states"]["OH"]["category"] == "NORMAL"
    assert site["pathway"] == "cus" and site["ooh_h_transferred"] is False
    assert site["n_unconverged_states"] == 0 and site["n_weak_states"] == 0
    # cus-pathway bookkeeping reproduces the retained eta exactly
    two = integrity.two_pathway_site(row["per_site_records"][0], site)
    assert math.isclose(two["eta_V"], 0.4530565522419163, abs_tol=1e-12)
    assert two["pls"] == 2 and two["pathway"] == "cus" and two["states"] == ["*OH", "*O", "*OOH"]


def test_equiatomic_o_state_reads_reconstruction_on_the_per_atom_bar():
    """The *O state moves the binding Cr (index 16) by 0.7991360510865592 A from the relaxed
    clean slab: above the 0.5 A per-atom bar, so the site is not all-states INTACT, while its
    adsorbate flags are clean (adsorbate-intact)."""
    site = integrity.classify_row(load_row("equiatomic"))["sites"][0]
    o_state = site["states"]["O"]
    assert math.isclose(o_state["slab_displacement"]["free_atom_max_A"], 0.7991360510865592, abs_tol=1e-9)
    assert o_state["slab_displacement"]["free_atom_max_index"] == 16
    assert o_state["reconstruction"] is True and o_state["category"] == "RECONSTRUCTION"
    assert o_state["intact"] is False and o_state["adsorbate_intact"] is True
    assert site["all_states_intact"] is False and site["all_states_adsorbate_intact"] is True
    assert site["n_reconstructed_states"] == 1


def test_leader_seed0_site0_ooh_is_desorbed_o2_like_h_transferred():
    row = load_row("leader")
    site = integrity.classify_row(row)["sites"][0]
    assert (site["seed"], site["site_index"], site["initial_binding_metal"]) == (0, 0, "Cr")
    ooh = site["states"]["OOH"]
    ref = audited("leader", "OOH")
    assert math.isclose(ooh["m_o_A"], ref["oxygen_metal_contacts"]["proximal_O"]["distance_A"], abs_tol=1e-9)
    assert math.isclose(ooh["m_o_A"], 3.400019495437414, abs_tol=1e-9)
    assert math.isclose(ooh["m_o_by_O_A"]["distal_O"], 3.9852417556640023, abs_tol=1e-9)
    assert ooh["bond_tier"] == "desorbed"
    assert ooh["binding_metal_index"] == 18 and ooh["binding_metal"] == "Ni"
    assert ooh["migration"] is True  # nearest metal Ni18 differs from the enumerated Cr16
    assert math.isclose(ooh["o_o_A"], 1.2299356375432444, abs_tol=1e-9)
    assert ooh["o_o_class"] == "O2_LIKE"
    assert ooh["h_location"] == "H_TRANSFERRED" and ooh["h_carrier"] == "slab_O"
    assert ooh["h_nearest_slab_O_index"] == 56
    assert math.isclose(ooh["h_nearest_slab_O_A"], ref["H_nearest_slab_O"]["distance_A"], abs_tol=1e-9)
    assert math.isclose(ooh["h_nearest_slab_O_A"], 0.9711344245982075, abs_tol=1e-9)
    assert ooh["dissociation"] is True
    assert ooh["category"] == "DESORPTION" and ooh["intact"] is False
    assert ooh["pathway_state"] == "undefined" and site["pathway"] == "undefined"
    assert site["ooh_h_transferred"] is True
    assert site["all_states_intact"] is False and site["all_states_adsorbate_intact"] is False
    assert site["categories"]["OH"] == "NORMAL" and site["categories"]["O"] == "RECONSTRUCTION"
    assert math.isclose(site["states"]["O"]["slab_displacement"]["free_atom_max_A"], 0.9520902671023659, abs_tol=1e-9)
    two = integrity.two_pathway_site(row["per_site_records"][0], site)
    assert math.isclose(two["eta_V"], 0.9780789066094675, abs_tol=1e-12)
    assert two["pls"] == 1 and two["pathway"] == "undefined"


def test_slab_displacement_matches_independent_audit():
    if not READOUT.exists():
        pytest.skip("paired readout absent")
    readout = json.loads(READOUT.read_text(encoding="utf-8"))
    for arm in ("equiatomic", "leader"):
        site = integrity.classify_row(load_row(arm))["sites"][0]
        for state in ("OH", "O", "OOH"):
            mine = site["states"][state]["slab_displacement"]
            ref = readout["arms"][arm]["slab_displacements"][state + "_slab_from_clean"]
            assert math.isclose(mine["free_atom_rms_A"], ref["free_atom_rms_displacement_A"], abs_tol=1e-9)
            assert math.isclose(mine["free_atom_max_A"], ref["free_atom_max_displacement_A"], abs_tol=1e-9)
            assert mine["fixed_atom_max_A"] == 0.0
            assert site["states"][state]["reconstruction"] is (mine["free_atom_max_A"] > 0.5)


def test_o2_fragment_record_is_a_diagnostic_and_moves_no_eta():
    row = load_row("leader")
    site = row["per_site_records"][0]
    cls = integrity.classify_row(row)["sites"][0]
    energies = site["energies_eV"]
    e_o2 = energies["OOH"] + 0.5 * energies["H2"] + 0.9
    e_o2_gas = -9.0
    record = dict(energy_eV=e_o2, E_O2_gas_eV=e_o2_gas, converged_by_force=True)
    two = integrity.two_pathway_site(site, cls, record, zpe_ts_O2=0.05)
    assert math.isclose(two["eta_V"], 0.9780789066094675, abs_tol=1e-12)  # unchanged
    frag = two["o2_fragment"]
    dG_ads = e_o2 - energies["slab"] - e_o2_gas + 0.05
    assert math.isclose(frag["dG_ads_O2_eV"], dG_ads, abs_tol=1e-12)
    assert math.isclose(frag["dG_O2_reference_cancelled_eV"], 4.92 + dG_ads, abs_tol=1e-12)
    assert math.isclose(frag["hb_deprotonation_step_eV"], 4.92 + dG_ads - site["dG_OOH"], abs_tol=1e-12)
    assert math.isclose(frag["o2_release_eV"], -dG_ads, abs_tol=1e-12)
    assert frag["role"].startswith("diagnostic")
    unconverged = integrity.two_pathway_site(site, cls, dict(energy_eV=e_o2, E_O2_gas_eV=e_o2_gas, converged_by_force=False))
    assert unconverged["o2_fragment"] == {"status": "unconverged_O2_record"}
    with pytest.raises(ValueError):
        integrity.two_pathway_site(site, cls, dict(energy_eV=e_o2, converged_by_force=True))


# ---- analytic checks ---------------------------------------------------------------------

def record(atoms, **extra):
    out = dict(symbols=atoms.get_chemical_symbols(), positions_A=atoms.positions.tolist(),
               cell_A=atoms.cell.array.tolist(), pbc=atoms.pbc.tolist(), fixed_atom_indices=[0],
               converged_by_force=True, energy_eV=-1.0)
    out.update(extra)
    return out


def slab():
    return Atoms(["Cr", "Ni", "O", "O"], positions=[[0, 0, 0], [5, 0, 0], [0, 3, 0], [5, 3, 0]],
                 cell=[10, 10, 20], pbc=True)


def ooh_state(prox, dist, h, base=None, **extra):
    atoms = (base or slab()).copy()
    atoms += Atoms("OOH", positions=[prox, dist, h])
    return record(atoms, **extra)


@pytest.mark.parametrize("m_o,tier", [(1.9, "bound"), (2.19999, "bound"), (2.2, "weak"),
                                      (2.99999, "weak"), (3.0, "desorbed"), (3.5, "desorbed")])
def test_bond_tiers(m_o, tier):
    assert integrity.bond_tier(m_o) == tier


@pytest.mark.parametrize("o_o,cls", [(1.21, "O2_LIKE"), (1.28, "O2_LIKE"), (1.29, "SUPEROXO_LIKE"),
                                     (1.36, "SUPEROXO_LIKE"), (1.37, "OOH_LIKE"), (1.60, "OOH_LIKE"),
                                     (1.61, "OO_CLEAVED")])
def test_o_o_classes(o_o, cls):
    assert integrity.o_o_class(o_o) == cls


def test_normal_intact_ooh():
    state = integrity.classify_state("OOH", ooh_state([0, 0, 1.9], [0, 1.4, 2.1], [0, 1.4, 3.08]), 0, record(slab()))
    assert state["category"] == "NORMAL" and state["intact"] is True and state["adsorbate_intact"] is True
    assert state["h_location"] == "ON_ADSORBATE" and state["h_carrier"] == "terminal_O"
    assert state["o_o_class"] == "OOH_LIKE" and state["pathway_state"] == "*OOH"


def test_weak_bound_ooh_is_intact_and_counted_weak():
    state = integrity.classify_state("OOH", ooh_state([0, 0, 2.55], [0, 1.4, 2.75], [0, 1.4, 3.73]), 0, record(slab()))
    assert state["bond_tier"] == "weak" and state["category"] == "NORMAL" and state["intact"] is True


def test_flipped_ooh_is_tiered_on_the_metal_bound_h_bearing_oxygen():
    """Build-order proximal O points away (2.52 A from Cr, O-O 1.41 A); the distal, H-bearing O sits on Cr."""
    state = integrity.classify_state("OOH", ooh_state([0, 1.4, 2.1], [0, 0, 1.9], [0.98, 0, 1.9]), 0, record(slab()))
    assert state["binding_O"] == "distal_O" and state["binding_metal_index"] == 0
    assert math.isclose(state["m_o_A"], 1.9, abs_tol=1e-9) and state["bond_tier"] == "bound"
    assert math.isclose(state["m_o_by_O_A"]["proximal_O"], math.sqrt(1.4 ** 2 + 2.1 ** 2), abs_tol=1e-9)
    assert state["o_o_class"] == "OOH_LIKE"
    assert state["h_location"] == "ON_ADSORBATE" and state["h_carrier"] == "binding_O"
    assert state["migration"] is False and state["category"] == "NORMAL" and state["intact"] is True


def test_h_on_the_binding_oxygen_of_an_unflipped_ooh_is_normal_not_dissociation():
    state = integrity.classify_state("OOH", ooh_state([0, 0, 1.9], [0, 1.4, 2.1], [0.98, 0, 1.9]), 0, record(slab()))
    assert state["h_location"] == "ON_ADSORBATE" and state["h_carrier"] == "binding_O"
    assert state["dissociation"] is False and state["category"] == "NORMAL"


def test_migration_when_nearest_metal_changes():
    state = integrity.classify_state("OOH", ooh_state([5, 0, 1.9], [5, 1.4, 2.1], [5, 1.4, 3.08]), 0, record(slab()))
    assert state["migration"] is True and state["binding_metal"] == "Ni"
    assert state["category"] == "MIGRATION" and state["intact"] is False and state["adsorbate_intact"] is False


def test_h_transferred_to_slab_oxygen_is_dissociation_and_a_bridge_state():
    state = integrity.classify_state("OOH", ooh_state([0, 0, 1.9], [0, 1.23, 1.9], [0, 3, 0.98]), 0, record(slab()))
    assert state["h_location"] == "H_TRANSFERRED" and state["h_nearest_slab_O_index"] == 2
    assert state["o_o_class"] == "O2_LIKE"
    assert state["category"] == "DISSOCIATION" and state["pathway_state"] == "*O2+H_b"
    oh = slab().copy()
    oh += Atoms("OH", positions=[[0, 0, 1.9], [0, 3, 0.98]])
    oh_state = integrity.classify_state("OH", record(oh), 0, record(slab()))
    assert oh_state["h_location"] == "H_TRANSFERRED" and oh_state["pathway_state"] == "*O+H_b"


def test_desorption_outranks_dissociation_and_migration():
    state = integrity.classify_state("OOH", ooh_state([5, 0, 3.4], [5, 1.23, 3.4], [5, 3, 0.98]), 0, record(slab()))
    assert state["bond_tier"] == "desorbed" and state["dissociation"] and state["migration"]
    assert state["category"] == "DESORPTION" and state["pathway_state"] == "undefined"


def test_reconstruction_from_the_largest_free_atom_displacement():
    base = slab()
    moved = base.copy()
    moved.positions[1] += [0, 0, 0.6]  # atom 1 free, atom 0 fixed in record(): max 0.6 > 0.5, rms 0.6/sqrt(3)
    state = integrity.classify_state("OOH", ooh_state([0, 0, 1.9], [0, 1.4, 2.1], [0, 1.4, 3.08], moved), 0, record(base))
    assert state["category"] == "RECONSTRUCTION" and state["adsorbate_intact"] is True and state["intact"] is False
    disp = state["slab_displacement"]
    assert math.isclose(disp["free_atom_max_A"], 0.6, abs_tol=1e-9) and disp["free_atom_max_index"] == 1
    assert math.isclose(disp["free_atom_rms_A"], 0.6 / math.sqrt(3), abs_tol=1e-9)
    small = base.copy()
    small.positions[1] += [0, 0, 0.4]
    assert integrity.classify_state("OOH", ooh_state([0, 0, 1.9], [0, 1.4, 2.1], [0, 1.4, 3.08], small), 0, record(base))["category"] == "NORMAL"
    assert integrity.classify_state("OOH", ooh_state([0, 0, 1.9], [0, 1.4, 2.1], [0, 1.4, 3.08]), 0, None)["reconstruction"] is None


def test_unconverged_state_is_never_intact():
    state = integrity.classify_state("OOH", ooh_state([0, 0, 1.9], [0, 1.4, 2.1], [0, 1.4, 3.08], converged_by_force=False), 0, record(slab()))
    assert state["category"] == "NORMAL" and state["intact"] is False and state["adsorbate_intact"] is False
    site = dict(seed=0, site_index=0, initial_binding_metal_index=0, eta=0.5,
                relaxed_states={"OH": None, "O": None, "OOH": ooh_state([0, 0, 1.9], [0, 1.4, 2.1], [0, 1.4, 3.08], converged_by_force=None)})
    cls = integrity.classify_site(site)
    assert cls["n_unconverged_states"] == 3 and cls["all_states_intact"] is False


def test_oh_state_h_free_is_dissociation():
    atoms = slab().copy()
    atoms += Atoms("OH", positions=[[0, 0, 1.9], [0, 0, 4.5]])
    state = integrity.classify_state("OH", record(atoms), 0, record(slab()))
    assert state["h_location"] == "H_FREE" and state["category"] == "DISSOCIATION" and state["pathway_state"] == "undefined"


def test_appended_order_is_enforced():
    atoms = slab().copy()
    atoms += Atoms("HOO", positions=[[0, 0, 3], [0, 0, 1.9], [0, 1.4, 2.1]])
    with pytest.raises(ValueError):
        integrity.classify_state("OOH", record(atoms), 0)


def test_minimum_image_distances_are_used():
    base = Atoms(["Cr", "O"], positions=[[0, 0, 0], [0, 3, 0]], cell=[6, 10, 20], pbc=True)
    atoms = base.copy()
    atoms += Atoms("OOH", positions=[[5.9, 0, 1.9], [5.9, 1.4, 2.1], [5.9, 1.4, 3.08]])
    state = integrity.classify_state("OOH", record(atoms), 0, record(base))
    assert math.isclose(state["m_o_A"], math.sqrt(0.1 ** 2 + 1.9 ** 2), abs_tol=1e-9)
    assert state["bond_tier"] == "bound"


def test_threshold_validation():
    with pytest.raises(ValueError):
        integrity.IntegrityThresholds(bound_max_A=3.5)
    with pytest.raises(ValueError):
        integrity.IntegrityThresholds(o2_like_max_A=1.40)


def test_four_step_bookkeeping_is_identical_under_both_labels():
    steps, eta, pls = integrity.cus_pathway(1.6, 3.28, 4.66)
    assert steps == [1.6, 3.28 - 1.6, 4.66 - 3.28, 4.92 - 4.66]
    assert math.isclose(eta, max(steps) - 1.23) and pls == 2
    bridge = integrity.bridge_pathway(1.6, 3.28, 4.66)
    assert bridge["steps_eV"] == steps and math.isclose(bridge["eta_V"], eta) and bridge["pls"] == 2
    assert bridge["states"][2] == "*O2+H_b" and math.isclose(bridge["steps_eV"][3], 4.92 - 4.66)
    with pytest.raises(ValueError):
        integrity.bridge_pathway(1.6, float("nan"), 4.66)


def test_ranking_rules_and_kendall_tau():
    def site(seed, index, eta, intact, ads_intact=None, pathway="cus", unconverged=0):
        return dict(seed=seed, site_index=index, eta=eta, dG_OH=1.5, dG_O=3.0, dG_OOH=eta + 1.23 + 3.0,
                    energies_eV=dict(slab=-100.0, H2O=-14.0, H2=-6.5, OOH=-110.0),
                    _cls=dict(all_states_intact=intact,
                              all_states_adsorbate_intact=intact if ads_intact is None else ads_intact,
                              pathway=pathway, pathway_states={"OH": "*OH", "O": "*O", "OOH": "*OOH"},
                              n_unconverged_states=unconverged, n_weak_states=0, n_reconstructed_states=0))
    rows = {"A": dict(per_site_records=[site(0, 0, 0.5, False, pathway="undefined"),
                                        site(0, 1, 0.9, True),
                                        site(0, 2, 0.6, False, ads_intact=True, pathway="bridge")]),
            "B": dict(per_site_records=[site(0, 0, 0.7, True)])}
    cls = {f: dict(sites=[s["_cls"] for s in r["per_site_records"]]) for f, r in rows.items()}
    out = integrity.ranking_rules(rows, cls)
    assert out["A"]["banked"] == 0.5 and out["A"]["intact_only"] == 0.9 and out["A"]["n_intact_sites"] == 1
    assert out["A"]["adsorbate_intact_only"] == 0.6 and out["A"]["n_adsorbate_intact_sites"] == 2
    assert out["A"]["two_pathway"] == 0.6 and out["A"]["n_pathway_defined_sites"] == 2
    assert out["A"]["n_bridge_sites"] == 1 and out["A"]["n_undefined_pathway_sites"] == 1
    assert out["B"]["banked"] == out["B"]["intact_only"] == out["B"]["two_pathway"] == 0.7
    o2 = {"A": {(0, 2): dict(energy_eV=-104.0, E_O2_gas_eV=-9.0, converged_by_force=True)}}
    with_o2 = integrity.ranking_rules(rows, cls, o2)
    assert with_o2["A"]["two_pathway"] == 0.6 and "0/2" in with_o2["A"]["o2_fragment_diagnostics"]
    assert with_o2["A"]["o2_fragment_diagnostics"]["0/2"]["status"] == "computed"
    assert integrity.kendall_tau(["a", "b", "c"], ["a", "b", "c"]) == 1.0
    assert integrity.kendall_tau(["a", "b", "c"], ["c", "b", "a"]) == -1.0
    assert math.isclose(integrity.kendall_tau(["a", "b", "c"], ["a", "c", "b"]), 1 / 3)
    with pytest.raises(ValueError):
        integrity.kendall_tau(["a", "b"], ["a", "c"])


def test_eta_statistics_and_exact_expected_minimum():
    stats = integrity.eta_statistics([0.5, 0.7, 0.9, 1.1])
    assert stats["n"] == 4 and math.isclose(stats["mean"], 0.8) and math.isclose(stats["median"], 0.8)
    assert math.isclose(stats["std"], float(np.std([0.5, 0.7, 0.9, 1.1], ddof=1)))
    assert math.isclose(stats["p10"], 0.56) and stats["min"] == 0.5 and stats["max"] == 1.1
    assert integrity.eta_statistics([])["n"] == 0 and integrity.eta_statistics([0.3])["std"] is None
    curve = {c["k"]: c["expected_min"] for c in integrity.expected_minimum_curve([0.5, 0.7, 0.9, 1.1], (1, 2, 3, 4, 5))}
    assert set(curve) == {1, 2, 3, 4}
    assert math.isclose(curve[1], 0.8) and math.isclose(curve[4], 0.5)
    # k = 2: the six pairs have minima 0.5, 0.5, 0.5, 0.7, 0.7, 0.9
    assert math.isclose(curve[2], (3 * 0.5 + 2 * 0.7 + 0.9) / 6)
    assert math.isclose(curve[3], (3 * 0.5 + 0.7) / 4)
