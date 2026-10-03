"""Offline contracts and adversarial fixtures, not real-QE validation."""
import copy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/dft"))
import pa_restart_diagnostic as probe

DECK = "&CONTROL\n restart_mode = 'from_scratch'\n/\n"
RESET = """Program PWSCF v.7.5 starts
File tmp/probe.bfgs deleted, as requested
number of bfgs steps = 0
new trust radius = 2.0D-2 bohr
JOB DONE.
"""


def records():
    return [{"geometry_role": "evaluated", "scf_converged": True,
             "energy_Ry": -2.0-i*.01, "species": ["H", "H"],
             "positions_bohr": [[0.,0.,0.], [0.,0.,2.-i*.1]],
             "forces_Ry_bohr": [[0.,0.,.01], [0.,0.,-.01]],
             "source": {"path": "retained/control.out", "sha256": "a"*64,
                        "line_start": 1+i*10, "line_end": 10+i*10}}
            for i in range(3)]


def test_reset_is_not_success_even_with_job_done():
    report = probe.inspect_segment(DECK, RESET)
    assert report["diagnosis"] == "HISTORY_RESET"
    assert report["trust_radii_bohr"] == [.02]
    assert report["job_done"] and not report["production_accepted"]
    assert report["real_qe_probe_pending"]


@pytest.mark.parametrize("text", ["", "restart_mode='invalid'", DECK+DECK,
                                  "restart_mode=restart", "! restart_mode='restart'"])
def test_missing_duplicate_invalid_or_commented_mode_fails(text):
    with pytest.raises(ValueError):
        probe.input_mode(text)


def test_modes_on_same_line_and_case_are_explicit():
    assert probe.input_mode("&CONTROL restart_mode=\"RESTART\" / ! comment") == "restart"


@pytest.mark.parametrize("log", [RESET.replace("7.5", "7.4"), RESET+RESET, "JOB DONE."])
def test_unpinned_or_multiple_output_versions_fail(log):
    with pytest.raises(ValueError, match="QE7.5"):
        probe.inspect_segment(DECK, log)


@pytest.mark.parametrize("log", [RESET,
    RESET.replace("File tmp/probe.bfgs deleted, as requested", "restart disabled: needed files not found"),
    RESET.replace("number of bfgs steps = 0", "number of bfgs steps = 5")])
def test_restart_cannot_pass_with_reset_or_silent_fallback(log):
    assert probe.inspect_segment(DECK.replace("from_scratch", "restart"), log)["diagnosis"] == "RESTART_REJECTED"


def test_nonzero_state_and_stop_do_not_certify_consumption():
    log = "Program PWSCF v.7.5 starts\nnumber of bfgs steps = 2\nProgram stopped by user request\nJOB DONE."
    report = probe.inspect_segment(DECK.replace("from_scratch", "restart"), log)
    assert report["diagnosis"] == "CONTINUATION_UNPROVEN"
    assert report["clean_user_stop_marker"] and not report["production_accepted"]


def test_exact_offline_comparison_is_not_production_acceptance():
    a = records()
    report = probe.compare_evaluations(a, copy.deepcopy(a))
    assert report["within_proposed_tolerances"]
    assert not report["production_accepted"] and report["real_qe_probe_pending"]
    assert report["independent_source_and_checkpoint_review_required"]


@pytest.mark.parametrize("key", ["energy_Ry", "positions_bohr", "forces_Ry_bohr"])
def test_every_intermediate_step_is_checked(key):
    a,b = records(),records()
    if key == "energy_Ry": b[1][key] += .001
    else: b[1][key][1][2] += .001
    assert not probe.compare_evaluations(a,b)["within_proposed_tolerances"]


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(geometry_role="proposed"),
    lambda r: r.update(scf_converged=False),
    lambda r: r.update(energy_Ry=float("nan")),
    lambda r: r.update(energy_Ry=True),
    lambda r: r.update(positions_bohr=[]),
    lambda r: r["forces_Ry_bohr"][0].append(0),
    lambda r: r["positions_bohr"][0].__setitem__(0,float("inf")),
    lambda r: r["positions_bohr"][0].__setitem__(0,False),
    lambda r: r.update(species=["H"]),
    lambda r: r.update(species=["He","H"]),
    lambda r: r.update(source=None),
    lambda r: r["source"].update(sha256="bad"),
    lambda r: r["source"].update(line_start=0),
    lambda r: r["source"].update(line_end=0),
])
def test_unclean_ambiguous_or_untraceable_evaluations_fail(mutate):
    a,b = records(),records()
    mutate(b[1])
    with pytest.raises(ValueError): probe.compare_evaluations(a,b)


@pytest.mark.parametrize("a,b", [([],[]), (records()[:1],records()[:1]),
                                 (records(),records()[:2])])
def test_endpoint_only_or_incomplete_trajectory_fails(a,b):
    with pytest.raises(ValueError): probe.compare_evaluations(a,b)


def test_inspect_files_retains_hashes_without_mutation(tmp_path):
    a,b = tmp_path/"probe.in",tmp_path/"probe.out"
    a.write_text(DECK,encoding="utf-8")
    b.write_text(RESET,encoding="utf-8")
    before = [a.read_bytes(),b.read_bytes()]
    report = probe.inspect_files(a,b)
    assert len(report["sources"]) == 2
    assert before == [a.read_bytes(),b.read_bytes()]
