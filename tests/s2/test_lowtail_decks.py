"""PREPARED relaxation decks: geometry construction, one-line relax conversion, manifests, determinism."""
import hashlib
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "s2" / "lowtail_dft"))
sys.path.insert(0, str(ROOT / "src" / "dft"))

import hea_deck  # noqa: E402
import lt_common  # noqa: E402
import lt_decks as decks  # noqa: E402
import lt_qe as qe  # noqa: E402


@pytest.fixture(scope="module")
def built():
    return decks.build(write=False)


def test_three_sites_two_projectors_three_states(built):
    plan = built["plan"]
    assert [s["tag"] for s in plan["sites"]] == ["Cu8Cr23Mn35Co34__s20_site2", "Ni31Cr29Cu5Mn35__s1_site0", "Fe25Co25Ni25Cr25__s2_site0"]
    assert len(plan["decks"]) == 18
    assert sum(d["role"] == "primary" for d in plan["decks"]) == 9
    assert all(d["kmesh"] == [4, 2, 1] and d["nk"] == 8 for d in plan["decks"])


def test_written_decks_equal_fresh_render_and_manifests_preserve_frozen_costs(built):
    for path, text in built["rendered"].items():
        assert path.exists() and path.read_bytes() == text.encode("utf-8"), path
    # New completed SCFs may change cost anchors. Historical manifests retain the
    # budgets and limits from their own frozen plan; refreshing costs cannot edit them.
    historical = lt_common.read_json(decks.RESULTS / "deck_plan.json")
    for path, role in ((decks.MANIFEST_PRIMARY, "primary"), (decks.MANIFEST_CONTROL, "paired projector control")):
        assert path.read_bytes() == decks.manifest_text(historical, role).encode("utf-8")
        assert lt_common.sha256_file(path) == historical["manifests"][lt_common.rel(path)]


def test_relax_conversion_changes_one_line_only():
    symbols = ["Cr", "O"]
    positions = [[0.0, 0.0, 5.0], [0.0, 0.0, 6.6]]
    cell = [[5.856, 0.0, 0.0], [0.0, 12.51, 0.0], [0.0, 0.0, 25.0]]
    scf = hea_deck.render_deck("p", symbols, positions, cell, [0], "atomic")
    relax = decks.render_relax("p", symbols, positions, cell, [0], "atomic")
    diff = [(a, b) for a, b in zip(scf.split("\n"), relax.split("\n")) if a != b]
    assert diff == [("  calculation = 'scf'", "  calculation = 'relax'")]
    p = qe.parse_input(relax)
    assert p["params"]["ion_dynamics"] == "bfgs" and p["params"]["forc_conv_thr"] == 2.0e-3 and p["params"]["nstep"] == 200


def test_unreconstructed_start_is_clean_slab_plus_on_top_O():
    ops = lt_common.read_json(ROOT / "results/lowtail_dft_2026-09-16/operating_decisions.json")
    h = ops["construction"]["unreconstructed_O_height_A"]
    assert 1.62 <= h <= 1.65
    for site in decks.SITES:
        sg = decks.site_geometries(site, h)
        slab, un, rec = (sg["geometries"][k] for k in ("slab", "O_unrecon", "O_recon"))
        n, s = sg["n_slab"], sg["site_index"]
        assert un["positions"][:n] == slab["positions"] and un["symbols"] == slab["symbols"] + ["O"]
        assert un["positions"][n] == [slab["positions"][s][0], slab["positions"][s][1], slab["positions"][s][2] + h]
        assert rec["site_geometry_vs_census_clean_slab"]["site_lift_z_A"] > ops["thresholds"]["lift_min_A"]
        assert rec["site_geometry_vs_census_clean_slab"]["site_to_axialO_A"] > ops["thresholds"]["axial_break_A"]
        assert un["site_geometry_vs_census_clean_slab"]["site_to_axialO_A"] < ops["thresholds"]["axial_break_A"]
        assert sg["checks"]["initial_metal"] == "Cr" and sg["checks"]["O_final_binding_index"] == s


def test_census_geometry_round_trips_in_decks(built):
    plan = built["plan"]
    for d in plan["decks"]:
        text = (ROOT / d["path"]).read_text(encoding="utf-8")
        assert hashlib.md5(text.encode("utf-8")).hexdigest() == d["md5"]
        p = qe.parse_input(text)
        site = next(s for s in plan["sites"] if s["tag"] == d["site"])
        assert p["calculation"] == "relax" and p["fixed"] == site["fixed"] and p["cell"] == site["cell_A"]
        if d["state"] in ("slab", "O_unrecon"):
            assert p["positions"][:site["n_slab"]] == site["clean_positions_A"]
        assert ("ortho-atomic" in p["hubbard_card"]) == (d["projector"] == "ortho")


def test_fe25_decks_equal_the_approved_pilot_geometry_except_prefix_and_calculation():
    for state, pilot in (("O_recon", "O"), ("slab", "slab")):
        for proj in ("atomic", "ortho"):
            ours = (decks.DECK_ROOT / "Fe25Co25Ni25Cr25__s2_site0" / f"{state}__{proj}.in").read_text(encoding="utf-8").split("\n")
            theirs = (ROOT / "runs/hea/pilot_retained/Fe25Co25Ni25Cr25__s2_site0" / f"{pilot}__{proj}.in").read_text(encoding="utf-8").split("\n")
            diff = [(a, b) for a, b in zip(theirs, ours) if a != b]
            assert len(ours) == len(theirs) and len(diff) == 2
            assert diff[0] == ("  calculation = 'scf'", "  calculation = 'relax'") and diff[1][0].startswith("  prefix = ")


def test_manifests_carry_the_prepared_header_and_pass_the_submitter_greps(built):
    for path, text in built["manifests"].items():
        lines = text.split("\n")
        assert lines[0] == "# PREPARED 2026-09-16 - submission sequenced after arrays 20781971/20781972 report measured per-SCF cost"
        info = hea_deck.check_manifest_text(text, expect_not_licensed=True)
        assert info["n_rows"] == 9 and info["not_licensed"] and info["np_directive"]
        rows = [ln.split() for ln in lines if ln and not ln.startswith("#")]
        for directory, job, suffix, nk in rows:
            assert (ROOT / "runs" / directory / f"{job}{suffix}").exists() and 128 % int(nk) == 0
        md5s = {ln.split()[-1] for ln in lines if ln.startswith("#   ")}
        role = "primary" if path == decks.MANIFEST_PRIMARY else "paired projector control"
        assert md5s == {d["md5"] for d in built["plan"]["decks"] if d["role"] == role}


def test_kill_rule_carried_to_every_deck_and_manifest(built):
    import math
    ops = built["decisions"]
    k = ops["kill_rule"]
    assert k["stop_when_iteration_begins"] == 127 and k["max_scf_iterations"] == 126 and k["electron_maxstep"] == 300
    assert k["source"] == "docs/research/research-decisions-2026-09-16.md:81 (HEA-4)"
    for dk in built["plan"]["decks"]:
        lim = dk["supervisor_limits"]
        assert lim["leg_wall_ceiling_s"] == math.ceil(dk["cost"]["ceiling_wall_s"]) and lim["electron_maxstep"] == 300
    for path, text in built["manifests"].items():
        assert "iteration 127" in text and "no automatic restart" in text


def test_lift_definition_is_recorded(built):
    lift = built["decisions"]["lift_definition"]
    assert "strict >" in lift["source_quantity"] and lift["used_here"].endswith("with >=")
    for z_lift, disp in lift["census_Cr_minima_lift_vs_displacement_A"]:
        assert (z_lift >= 0.5) == (disp > 0.5)


def test_survey_files_preserved_and_current_scorer_provenance_recorded(built):
    written = lt_common.read_json(decks.SURVEY_MANIFEST)
    fresh = built["survey_manifest"]
    assert {k: v for k, v in written.items() if k != "scorer"} == {k: v for k, v in fresh.items() if k != "scorer"}
    assert fresh["scorer"] == lt_common.evidence(ROOT / "src/dft/hea_panel_readout.py")
    plan = lt_common.read_json(decks.RESULTS / "deck_plan.json")
    assert plan["cost_inputs"]["survey_manifest"]["sha256"] == lt_common.sha256_file(decks.SURVEY_MANIFEST)
    for item in written["used"] + written["excluded"]:
        assert lt_common.sha256_file(ROOT / item["output"]["path"]) == item["output"]["sha256"]


def test_costs_are_positive_and_ceiling_not_below_planning(built):
    for d in built["plan"]["decks"]:
        c = d["cost"]
        assert 0 < c["planning_core_h"] <= c["ceiling_core_h"]
        assert c["fits_node"] and not c["ceiling_exceeds_deck_max_seconds"]
    t = built["plan"]["totals"]["primary"]
    assert t["planning_core_h"] == pytest.approx(sum(d["cost"]["planning_core_h"] for d in built["plan"]["decks"] if d["role"] == "primary"))
