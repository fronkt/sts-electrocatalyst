"""Registered Xu clauses keep their populations, witnesses and missing evidence separate."""
from collections import Counter
import copy
from decimal import Decimal
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from s2.xu import census as xu


def raw_force(steps, atoms=(2, 3), excluded=()):
    return dict(path="fixture", adsorbate_indices=list(atoms), identified_adsorbate_indices=[2, 3],
                force_steps=steps, force_issues=[], unidentified=False, excluded_indices=list(excluded),
                n_if_pos_excluded=len(excluded), n_adsorbate=2, n_symops=2, forc_conv_thr=.001, issues=[])


def rows():
    out = []
    for item in xu.population():
        axes = ["y"] if item["state"] == "OH" else ["x"] if item["state"] == "OOH" else ["x", "y"]
        energy = Decimal("-100")
        if item["u_eV"] is not None and item["state"] == "OOH" and item["metal"] in xu.METALS[:5]:
            energy += Decimal(item["u_eV"]) * Decimal("0.0025")
        out.append(dict(item, header=dict(n_symops=2), unidentified=False,
                        declared=dict(calculation="relax"),
                        force=dict(n_force_steps=2, eligible_adsorbate_indices=[31], final_clause=True,
                                   final_all_atom_zero_lateral_axes=axes, every_step_all_atom_zero_lateral_axes=axes),
                        energy=dict(usable=True, final_energy_Ry=str(energy))))
    return out


def test_population_is_exact_registered_cross_product():
    p = xu.population()
    assert len(p) == len({r["output"] for r in p}) == 810
    assert sum(r["state"] != "bare" for r in p) == 630
    assert sum(r["u_eV"] is not None for r in p) == 680
    assert Counter(r["metal"] for r in p) == {m:81 for m in xu.METALS}
    assert Counter(r["state"] for r in p) == dict(bare=180, O=210, OH=210, OOH=210)


def test_final_step_all_atoms_is_not_any_atom_or_all_steps():
    raw = raw_force([{2:[.2,.3,.4],3:[.1,.2,.3]}, {2:[0,.1,.2],3:[0,.2,.3]}])
    f = xu.force_evidence(raw)
    assert f["final_clause"] is True and f["final_all_atom_zero_lateral_axes"] == ["x"]
    assert f["every_step_all_atom_zero_lateral_axes"] == []
    raw["force_steps"][-1] = {2:[0,.1,.2],3:[.1,0,.3]}
    assert xu.force_evidence(raw)["final_clause"] is False


def test_empty_eligible_set_is_unknown_not_vacuously_zero():
    f = xu.force_evidence(raw_force([{2:[0,0,.2],3:[0,0,.3]}], atoms=(), excluded=(2,3)))
    assert f["final_clause"] is None and not f["scorable"]
    assert "NO_ELIGIBLE_ADSORBATE_ATOMS" in f["reasons"]


def test_missing_identified_atom_is_not_hidden_by_constraint_exclusion():
    f = xu.force_evidence(raw_force([{2:[0,.1,.2]}], atoms=(2,), excluded=(3,)))
    assert f["final_clause"] is None


@pytest.mark.parametrize("success,unknown,n,outcome", [(90,0,100,"HELD"),(89,0,100,"SCORED — MIDDLE BAND / NOT MET"),
    (75,0,100,"SCORED — MIDDLE BAND / NOT MET"),(74,0,100,"FALSIFIED"),(74,1,100,"INCOMPLETE EVIDENCE")])
def test_registered_fraction_boundary_is_exact(success, unknown, n, outcome):
    assert xu.fraction_clause(success,unknown,n)["outcome"] == outcome


def test_named_pair_controls_direction_score_but_other_jobs_mark_mixed():
    data = rows()
    changed = next(r for r in data if r["metal"] == "RuO2" and r["job"] == "OH-U-0.0")
    changed["force"]["every_step_all_atom_zero_lateral_axes"] = ["x"]
    result = xu.score_census(data)
    assert result["named_pair_direction"]["successes"] == 10
    mapping = next(m for m in result["direction_maps"] if m["metal"] == "RuO2")
    assert mapping["mixed"] and mapping["deviating_jobs"] == [changed["output"]]
    assert len(result["named_pair_direction"]["subsets"]["blind_by_record"]["metals"]) == 6
    assert len(result["named_pair_direction"]["subsets"]["blind_by_availability"]["metals"]) == 5


def test_only_registered_exclusions_reduce_force_denominator():
    data = rows()
    ads = [r for r in data if r["state"] != "bare"]
    ads[0]["unidentified"] = True
    ads[0]["force"]["n_force_steps"] = 0
    ads[1]["force"]["n_force_steps"] = 0
    ads[2]["force"].update(eligible_adsorbate_indices=[], final_clause=None)
    result = xu.score_census(data)["final_force"]
    assert result["original_denominator"] == 630 and result["denominator"] == 628
    assert result["excluded_union"] == 2 and result["unknown"] == 1
    assert result["no_eligible_adsorbate_outputs"] == [ads[2]["output"]]


def test_span_uses_exact_energy_differences_and_full_pair_ladders():
    result = xu.score_spans(rows())
    assert result["outcome"] == "HELD" and result["full_ladder_exceeding_count"] == 5
    first = result["metals"][0]["spans"]["cM_electronic_eV"]
    assert Decimal(first["primary_span_eV"]) == Decimal("0.020") * xu.RY_EV
    assert first["paired_usable_rungs"] == 17


def test_incomplete_span_is_only_a_lower_bound_and_cannot_manufacture_falsification():
    data = rows()
    for row in data:
        if row["metal"] in xu.METALS[:5] and row["job"] == "OOH-U-4.0":
            row["energy"].update(usable=False, final_energy_Ry=None)
    result = xu.score_spans(data)
    assert result["full_ladder_exceeding_count"] == 0 and result["possible_max_count"] == 5
    assert result["outcome"] == "INCOMPLETE EVIDENCE"
    first = result["metals"][0]["spans"]
    assert first["cM_electronic_eV"]["primary_span_eV"] is None
    assert first["cM_electronic_eV"]["observed_range_lower_bound_eV"] is not None
    assert first["dG2_electronic_eV"]["full_ladder"]


def test_job_done_alone_does_not_license_ladder_energy():
    text = "! total energy = -100.0 Ry\nJOB DONE.\n"
    assert not xu.energy_evidence(text, "relax", [-100.0])["usable"]
    text += "convergence has been achieved in 12 iterations\nbfgs converged in 1 scf cycles and 0 bfgs steps\n"
    assert xu.energy_evidence(text, "relax", [-100.0])["usable"]
    assert not xu.energy_evidence(text + "convergence NOT achieved after 300 iterations\n", "relax", [-100.0])["usable"]


def test_declared_missing_values_are_separate_from_effective_defaults():
    declared = xu.assignments("&SYSTEM\n nspin = 2\n tot_magnetization = 15\n Hubbard_U(2) = 4.0\n/\n&CONTROL\n calculation = 'relax' ! preserve type\n/\n")
    assert declared["calculation"] == "relax" and declared["nspin"] == 2 and declared["hubbard_u(2)"] == 4
    assert "forc_conv_thr" not in declared
