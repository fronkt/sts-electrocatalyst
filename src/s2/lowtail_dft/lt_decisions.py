"""Dated operating decisions (2026-09-16) for the low-tail relaxation decks and their readout.

docs/43 registers no threshold for this question (its A6.6 scope registers fixed-geometry
SCFs and no relaxations, docs/43-prereg-week1-factorial.md:1283-1288). Every value the
readout needs is therefore fixed here, before any relaxation output exists, and each
numerical value is read from its source file by this code:

  * lift_min_A: the value of the census per-atom reconstruction displacement threshold,
    src/hea_oer/site_integrity.py:84 (IntegrityThresholds.reconstruction_max_A; docs/91:58).
    The source quantity is the largest free-slab-atom 3-D displacement with a strict "exceeds"
    (site_integrity.py:278); here the value is re-used for the site-metal displacement along +z
    with ">=". The change of quantity is recorded in the output, and the readout prints the 3-D
    displacement beside the lift with a LIFT_DEFINITIONS_DISAGREE flag;
  * axial_break_A: midpoint between the largest clean-slab and the smallest O-state
    site-metal/axial-lattice-O distance over the four census Cr reconstruction minima named
    in docs/research/census-endpoint-chemistry-2026-09-13.md (computed from their census
    coordinates here);
  * desorbed_min_A: src/hea_oer/data.py:20 (M_O_DESORBED_MIN);
  * magnetization_flag_muB: src/dft/hea_panel_readout.py:68 (SPIN_TOL_MUB);
  * energy-order margin: the spread of the accepted matched fixed-geometry E(pull2.10) -
    E(builder) gaps across initial-spin variants at the settings of record
    (results/hea_followup_2026-09-07/completion_readout.json pairs), with the largest
    numerical-setting gap change (numerical tight + sensitivity wfc/rho readouts) printed beside it;
  * unreconstructed_O_height_A: 1.635 A, the midpoint of the 1.62-1.65 A on-top range the
    track direction specifies for the unreconstructed start (a construction choice, not a
    measured value);
  * kill rule: HEA-4 of docs/research/research-decisions-2026-09-16.md (iteration 127 / per-deck
    ceiling / KILLED / no restart ladder) carried to relaxation legs; the iteration count is
    cross-checked against runs/hea/COST_MODEL.md (ceiling SCF iterations) and the max_iterations
    of every HEA job in results/research_launch_2026-09-16/launch_spec.json.

Revision 2 (before any relaxation output exists): the lift-definition record, the kill rule and the
3-D displacement flag were added; no threshold value changed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lt_geometry as geo  # noqa: E402
import lt_sources as src  # noqa: E402
from lt_common import ROOT, evidence, read_json, rel  # noqa: E402

DATE = "2026-09-16"
UNRECONSTRUCTED_O_HEIGHT_A = 1.635
UNRECONSTRUCTED_RANGE_A = (1.62, 1.65)

CR_MINIMA = (
    ("Ni31Cr29Cu5Mn35", "results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json", 1, 0),
    ("Fe25Co25Ni25Cr25", "results/site_census_2026-09-06/results/mpa0__Fe25Co25Ni25Cr25_result.json", 2, 0),
    ("Cu26Ni9Cr31Co33", "results/site_census_2026-09-06/results/mpa0_ext__Cu26Ni9Cr31Co33__s03-05_result.json", 5, 2),
    ("Cu8Cr23Mn35Co34", "results/site_census_2026-09-06/results/mpa0_ext__Cu8Cr23Mn35Co34__s18-20_result.json", 20, 2),
)
SITE_INTEGRITY = ROOT / "src/hea_oer/site_integrity.py"
DATA = ROOT / "src/hea_oer/data.py"
PANEL_SCORER = ROOT / "src/dft/hea_panel_readout.py"
RESEARCH_DECISIONS = ROOT / "docs/research/research-decisions-2026-09-16.md"
COST_MODEL = ROOT / "runs/hea/COST_MODEL.md"
LAUNCH_SPEC = ROOT / "results/research_launch_2026-09-16/launch_spec.json"


def _float_assignment(path: Path, pattern: str) -> tuple[float, int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [(i + 1, m) for i, line in enumerate(lines) for m in [re.match(pattern, line)] if m]
    if len(hits) != 1:
        raise ValueError(f"{path}: expected one match of {pattern!r}, found {len(hits)}")
    return float(hits[0][1].group(1)), hits[0][0]


def axial_minima() -> dict:
    rows = []
    for formula, path, seed, site in CR_MINIMA:
        c = src.census_site(ROOT / path, seed, site)
        s = int(c["site"]["initial_binding_metal_index"])
        O = c["site"]["relaxed_states"]["O"]
        clean = c["slab"]["positions_A"]
        if O["symbols"][s] != "Cr" or O["final_binding_metal_index"] != s:
            raise ValueError(f"{formula} seed {seed} site {site} is not a Cr-bound O endpoint")
        ax = geo.axial_oxygen(O["symbols"], clean, s, O["cell_A"], len(clean))
        rows.append(dict(formula=formula, seed=seed, site=site, census=path, site_index=s, axial_O_index=ax["index"],
                         clean_A=ax["clean_distance_A"], O_state_A=geo.distance(O["positions_A"], s, ax["index"], O["cell_A"]),
                         site_lift_z_A=float(geo.mic(np.array(O["positions_A"][s]) - np.array(clean[s]), O["cell_A"])[2]),
                         site_displacement_A=float(np.linalg.norm(geo.mic(np.array(O["positions_A"][s]) - np.array(clean[s]), O["cell_A"]))),
                         census_sha256=evidence(ROOT / path)["sha256"]))
    clean_max = max(r["clean_A"] for r in rows)
    state_min = min(r["O_state_A"] for r in rows)
    if not clean_max < state_min:
        raise ValueError("clean and O-state axial distances overlap; no midpoint rule")
    return dict(rows=rows, clean_max_A=clean_max, O_state_min_A=state_min, midpoint_A=(clean_max + state_min) / 2)


def gap_spreads() -> dict:
    followup = read_json(src.READOUTS["followup"])
    gaps = [p["gap_eV"] for p in followup["pairs"] if p.get("gap_eV") is not None]
    numerical = read_json(src.READOUTS["numerical"])
    sensitivity = read_json(src.READOUTS["sensitivity"])
    deltas = [p["delta_gap_eV"] for p in numerical["paired_tight"] if p.get("delta_gap_eV") is not None]
    deltas += [p["delta_gap_eV"] for p in sensitivity["pairs"] if p.get("delta_gap_eV") is not None]
    return dict(spin_start_gaps_eV=gaps, spin_start_spread_eV=max(gaps) - min(gaps), n_spin_start_pairs=len(gaps),
                numerical_gap_changes_eV=deltas, numerical_max_abs_change_eV=max(abs(d) for d in deltas))


def _line_match(path: Path, pattern: str) -> tuple[re.Match, int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [(i + 1, m) for i, line in enumerate(lines) for m in [re.search(pattern, line)] if m]
    if len(hits) != 1:
        raise ValueError(f"{path}: expected one match of {pattern!r}, found {len(hits)}")
    return hits[0][1], hits[0][0]


def kill_rule() -> dict:
    """HEA-4 carried to relaxation legs; every number is read from its source and cross-checked."""
    hea4, hea4_line = _line_match(RESEARCH_DECISIONS, r"^\| HEA-4 \|.*stops once iteration (\d+) begins")
    ceiling, ceiling_line = _line_match(COST_MODEL, r"^\| ceiling SCF iterations \| (\d+) \|")
    maxstep, maxstep_line = _line_match(RESEARCH_DECISIONS, r"^\| HEA-4 \| Keep input electron_maxstep=(\d+);")
    begins, cap = int(hea4.group(1)), int(ceiling.group(1))
    spec = read_json(LAUNCH_SPEC)
    hea_jobs = [j for name, stage in spec["stages"].items() if name.startswith("hea_") for j in stage["jobs"]]
    approved = sorted({j.get("max_iterations") for j in hea_jobs})
    if begins != cap + 1 or approved != [cap]:
        raise ValueError(f"kill-rule sources disagree: begins {begins}, cost-model ceiling {cap}, launch spec {approved}")
    _, strict_line = _line_match(SITE_INTEGRITY, r'free_atom_max_A"\] > thresholds\.reconstruction_max_A')
    return dict(
        source=f"{rel(RESEARCH_DECISIONS)}:{hea4_line} (HEA-4)",
        stop_when_iteration_begins=begins, max_scf_iterations=cap, electron_maxstep=int(maxstep.group(1)),
        cross_checks=dict(cost_model=f"{rel(COST_MODEL)}:{ceiling_line} ceiling SCF iterations {cap}",
                          launch_spec=f"{rel(LAUNCH_SPEC)} max_iterations of all {len(hea_jobs)} HEA jobs = {approved}",
                          electron_maxstep=f"{rel(RESEARCH_DECISIONS)}:{maxstep_line}"),
        iteration_limit="every SCF of every ionic step: the leg stops once any SCF begins iteration "
                        f"{begins} (the maximum 'iteration #' in the output, as the supervisor in src/dft/research_batch.py counts it)",
        wall_limit="a relaxation is one pw.x process, so the per-deck SCF ceiling of HEA-4 becomes one per-leg ceiling: the leg stops once its "
                   "wall exceeds the deck's unrounded ceiling wall in deck_plan.json (cost.ceiling_wall_s), rounded upward to the next second "
                   "(supervisor_limits.leg_wall_ceiling_s)",
        on_stop="record KILLED (<job>.KILLED sidecar), preserve scratch, no automatic restart; a stopped leg yields no energy, final geometry "
                "or basin; restarting from the last ionic geometry needs its own dated decision",
        readout_enforcement="the readout applies both limits to every output whatever route ran it: an otherwise CONVERGED leg whose output "
                            f"shows iteration >= {begins} or a PWSCF wall above leg_wall_ceiling_s is KILL_RULE_EXCEEDED and not accepted",
        deck_setting=f"electron_maxstep = {int(maxstep.group(1))} stays in every deck (HEA-4)",
        lift_strict_inequality_line=f"{rel(SITE_INTEGRITY)}:{strict_line}")


def build() -> dict:
    lift, lift_line = _float_assignment(SITE_INTEGRITY, r"^\s*reconstruction_max_A:\s*float\s*=\s*([\d.]+)")
    desorbed, desorbed_line = _float_assignment(DATA, r"^M_O_DESORBED_MIN\s*=\s*([\d.]+)")
    spin_tol, spin_line = _float_assignment(PANEL_SCORER, r"^SPIN_TOL_MUB\s*=\s*([\d.]+)")
    axial = axial_minima()
    spreads = gap_spreads()
    kill = kill_rule()
    if not UNRECONSTRUCTED_RANGE_A[0] <= UNRECONSTRUCTED_O_HEIGHT_A <= UNRECONSTRUCTED_RANGE_A[1]:
        raise ValueError("unreconstructed start height outside the specified range")
    return dict(
        schema="lowtail-operating-decisions-v1", date=DATE, revision=2,
        status="PROSPECTIVE: fixed before any relaxation output exists",
        revision_note="revision 2, still before any relaxation output: lift-definition record, HEA-4 kill rule for relaxation legs and the "
                      "3-D displacement flag added; no threshold value changed",
        registration_context=dict(docs43="no registered threshold for this question; A6.6 registers fixed-geometry SCFs and zero relaxations (docs/43-prereg-week1-factorial.md:1283-1288)",
                                  authority="docs/research/research-decisions-2026-09-16.md:55 (persistence of a reconstruction requires a suitable relaxation and a basin/chemical-integrity check)"),
        thresholds=dict(lift_min_A=lift, axial_break_A=axial["midpoint_A"], desorbed_min_A=desorbed,
                        magnetization_flag_muB=spin_tol, energy_order_margin_eV=spreads["spin_start_spread_eV"]),
        sources=dict(
            lift_min_A=f"value of {rel(SITE_INTEGRITY)}:{lift_line} (IntegrityThresholds.reconstruction_max_A; docs/91-prereg-site-integrity-census-2026-09-06.md:58), "
                       "re-used for the site-metal z-lift with >= (see lift_definition)",
            axial_break_A="midpoint of max clean and min O-state site-metal/axial-O distance over the four census Cr reconstruction minima (rows below)",
            desorbed_min_A=f"{rel(DATA)}:{desorbed_line} (M_O_DESORBED_MIN)",
            magnetization_flag_muB=f"{rel(PANEL_SCORER)}:{spin_line} (SPIN_TOL_MUB)",
            energy_order_margin_eV=f"max-min of accepted matched fixed-geometry pull2.10-builder gaps across initial-spin variants, {rel(src.READOUTS['followup'])} pairs"),
        lift_definition=dict(
            source_quantity="largest single free-slab-atom minimum-image 3-D displacement from the same decoration's relaxed clean slab; "
                            f"RECONSTRUCTION when it exceeds the value (strict >, {kill['lift_strict_inequality_line']}; "
                            "docs/91-prereg-site-integrity-census-2026-09-06.md:58)",
            used_here="site-metal displacement along +z relative to the clean slab (lift), with >=",
            reason="the question is whether the site metal leaves the surface plane along the normal; lateral motion of the site metal "
                   "is not a lift",
            readout_record="site-metal 3-D displacement printed beside the lift; flag LIFT_DEFINITIONS_DISAGREE when (lift >= lift_min_A) "
                           "differs from (3-D displacement > lift_min_A); the basin label follows the lift rule",
            census_Cr_minima_lift_vs_displacement_A=[[r["site_lift_z_A"], r["site_displacement_A"]] for r in axial["rows"]]),
        kill_rule=kill,
        axial_minima=axial, gap_spreads=spreads,
        construction=dict(unreconstructed_O_height_A=UNRECONSTRUCTED_O_HEIGHT_A, specified_range_A=list(UNRECONSTRUCTED_RANGE_A),
                          unreconstructed_geometry="census relaxed clean slab of the same decoration, unchanged, plus one O at the site metal position + height along +z",
                          reconstructed_geometry="census selected *O endpoint (relaxed_states.O), unchanged"),
        basin_rule=dict(
            reference="site-metal lift = z(site metal, relaxed *O) - z(site metal, DFT-relaxed clean slab of the same site and projector) when that slab leg is accepted; otherwise the census MACE clean slab, flagged REFERENCE_MACE_SLAB",
            O_OFF_SITE="nearest metal to the appended O is not the site metal, or that distance >= desorbed_min_A",
            RECONSTRUCTED="lift >= lift_min_A and site-metal/axial-O distance >= axial_break_A",
            UNRECONSTRUCTED="lift < lift_min_A and site-metal/axial-O distance < axial_break_A",
            MIXED_UNASSIGNED="exactly one of the two criteria met"),
        site_outcomes=dict(
            RECONSTRUCTION_SUPPORTED="both *O starts accepted and RECONSTRUCTED",
            RECONSTRUCTION_NOT_SUPPORTED="both *O starts accepted and UNRECONSTRUCTED",
            TWO_LOCAL_BASINS="reconstructed start RECONSTRUCTED and unreconstructed start UNRECONSTRUCTED; energy order reported as LIFTED_LOWER / UNLIFTED_LOWER only when |E(recon) - E(unrecon)| exceeds energy_order_margin_eV, otherwise ORDER_WITHIN_SPIN_START_SPREAD; MAGNETIZATION_DIFFERS flagged when |dM_total| >= magnetization_flag_muB",
            BASINS_CROSSED="reconstructed start UNRECONSTRUCTED and unreconstructed start RECONSTRUCTED",
            UNDECIDED="any *O leg O_OFF_SITE or MIXED_UNASSIGNED, or any *O leg not accepted (PENDING / NOT CONVERGED / KILLED / REJECTED named)"),
        acceptance="a leg is accepted only when src/dft/hea_panel_readout.py parse_out(path, allow_relax=True) returns CONVERGED (read with the two input corrections recorded in src/s2/lowtail_dft/lt_readout.py: pw.x hour-format wall tokens, and the gfortran exit note that the scorer's 'floating.point exception' pattern otherwise rejects in every banked HEA output; IEEE_INVALID/DIVIDE_BY_ZERO/OVERFLOW flags still reject), the HEA-4 kill rule is respected (kill_rule), the output carries one parseable 'Begin final coordinates' block whose elements match the deck, fixed atoms are unmoved (<= 1e-6 A) and the final free-atom force components are within the deck forc_conv_thr",
        interpretation_limits=[
            "Basins are assigned under DFT+U (MP U set, FM starts, 4x2x1 k, 80/640 Ry); a different magnetic solution can change both geometry and energy order.",
            "A relaxation reaching a basin shows it is a local DFT minimum from that start; it does not exclude other basins.",
            "No overpotential or melt ranking follows from these three sites."],
        inputs=[evidence(SITE_INTEGRITY), evidence(DATA), evidence(PANEL_SCORER), evidence(src.READOUTS["followup"]),
                evidence(src.READOUTS["numerical"]), evidence(src.READOUTS["sensitivity"]), evidence(RESEARCH_DECISIONS),
                evidence(COST_MODEL), evidence(LAUNCH_SPEC)])
