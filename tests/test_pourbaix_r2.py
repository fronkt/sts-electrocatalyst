"""R2 stability gate: the hand-entered table must be right, and the integrity
rule (no dG_pbx for a phase that does not exist) must hold in code, not just prose.

Everything here runs offline. The Materials-Project-dependent tests skip cleanly
when `results/r2_mp_cache.json` is absent, because `results/` is gitignored - run
`PYTHONPATH=src python src/dft/pourbaix_r2.py run` once to populate it.
"""
import importlib.util
import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SPEC = importlib.util.spec_from_file_location(
    "pourbaix_r2", os.path.join(REPO, "src", "dft", "pourbaix_r2.py"))
pbx_r2 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pbx_r2)

CACHE = os.path.join(REPO, "results", "r2_mp_cache.json")
needs_mp = pytest.mark.skipif(not os.path.exists(CACHE),
                              reason="MP cache absent; run `pourbaix_r2.py run` first")


def _windows(conc=pbx_r2.DEFAULT_CONC_M):
    return {w["pH"]: w for w in pbx_r2.beta_mno2_report(conc)["windows"]}


def test_literature_table_reproduces_analytic_nernst_lines():
    # If the Delta_Gf table were wired in with a wrong sign, unit, H2O reference or
    # concentration term, these residuals would be volts, not millivolts.
    for check in pbx_r2.analytic_checks():
        assert abs(check["lower_edge_residual_mV"]) < 2.0
        assert abs(check["upper_edge_residual_mV"]) < 2.0


def test_beta_mno2_window_at_ph0():
    w = _windows()[0.0]
    assert w["stable"]
    assert w["lower_V_rhe"] == pytest.approx(1.407, abs=2e-3)
    assert w["upper_V_rhe"] == pytest.approx(1.583, abs=2e-3)
    assert w["reduces_to"] == "Mn[+2]"
    assert w["oxidises_to"] == "MnO4[-1]"


def test_beta_mno2_upper_edge_at_ph14_is_barely_above_the_oer_equilibrium():
    # The headline result: 41 mV of overpotential headroom in 1 M KOH at 1e-6 M Mn.
    w = _windows()[14.0]
    assert w["oxidises_to"] == "MnO4[-2]"
    assert 0.0 < w["max_eta_before_upper_edge_V"] < 0.06


def test_upper_edge_falls_monotonically_with_ph():
    ws = _windows()
    edges = [ws[p]["upper_V_rhe"] for p in (0.0, 7.0, 13.0, 14.0)]
    assert edges == sorted(edges, reverse=True)


def test_window_moves_59mV_per_decade_of_concentration():
    """A window without its concentration is meaningless - prove the sensitivity.

    Raising dissolved Mn from 1e-6 to 1e-5 M pushes the reductive edge
    (MnO2 + 4H+ + 2e- -> Mn2+ + 2H2O, n=2, one ion) DOWN by 0.0591/2 V and the
    oxidative edge (MnO4- + 4H+ + 3e- -> MnO2 + 2H2O, n=3, one ion) UP by 0.0591/3 V.
    """
    lo6, hi6 = (_windows(1e-6)[0.0][k] for k in ("lower_V_rhe", "upper_V_rhe"))
    lo5, hi5 = (_windows(1e-5)[0.0][k] for k in ("lower_V_rhe", "upper_V_rhe"))
    assert lo5 - lo6 == pytest.approx(-pbx_r2.PREFAC_V / 2, abs=2e-3)
    assert hi5 - hi6 == pytest.approx(+pbx_r2.PREFAC_V / 3, abs=2e-3)


@needs_mp
def test_phase_gate_verdicts():
    gate = pbx_r2.phase_gate(json.load(open(CACHE)))
    assert gate["MnO2"]["rutile_material_id"] == "mp-510408"
    assert gate["CrO2"]["rutile_material_id"] == "mp-19177"
    assert gate["RuO2"]["rutile_material_id"] == "mp-825"
    assert gate["IrO2"]["rutile_material_id"] == "mp-2723"
    assert gate["FeO2"]["curated_verdict"] == "HYPOTHETICAL"
    for absent in ("CoO2", "NiO2", "CuO2"):
        assert gate[absent]["curated_verdict"] == "ABSENT"
        assert gate[absent]["rutile_material_id"] is None
    realisable = [f for f, g in gate.items() if g["realisable_electrode"]]
    assert set(realisable) == {"MnO2", "CrO2", "RuO2", "IrO2"}  # 2 of 6 endmembers + 2 anchors


@needs_mp
def test_no_dg_pbx_is_produced_for_a_nonexistent_phase():
    """The integrity rule, enforced: absent phases get a refusal, not a number."""
    cache = json.load(open(CACHE))
    res = pbx_r2.mp_anchors(cache, pbx_r2.phase_gate(cache))
    for absent in ("CoO2", "NiO2", "CuO2"):
        assert absent in res["refused"]
        assert absent not in res["gated"]
        assert absent not in res["hypothetical_structures"]
    # a hypothetical structure may be reported, but only in the labelled block
    assert "FeO2" not in res["gated"]
    assert "NOT AN AMBIENT PHASE" in res["hypothetical_structures"]["FeO2"]["label"]


@needs_mp
def test_iro2_is_the_only_endmember_stable_across_the_acid_oer_band():
    """External validation: the pipeline must reproduce why IrO2 is the acid anode."""
    cache = json.load(open(CACHE))
    res = pbx_r2.mp_anchors(cache, pbx_r2.phase_gate(cache))
    ir = {w["pH"]: w for w in res["gated"]["IrO2"]["windows"]}[0.0]
    assert ir["lower_V_rhe"] < 1.229 < 1.529 < ir["upper_V_rhe"]
    ru = {w["pH"]: w for w in res["gated"]["RuO2"]["windows"]}[0.0]
    assert ru["upper_V_rhe"] < 1.229  # RuO2 -> RuO4 before the OER even starts
