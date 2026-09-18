"""Readout of the PREPARED low-tail relaxation decks: acceptance, basin assignment and site outcome.

A leg is accepted only when the existing HEA scorer, src/dft/hea_panel_readout.py
parse_out(path, allow_relax=True), returns CONVERGED (exactly one JOB DONE, no severe numerical
exception, no 'convergence NOT achieved' / CPU-time / max-step stop, finite energy, SCF and BFGS
convergence, no KILLED/REJECTED sidecar) AND this readout finds one parseable final-coordinate
block whose elements match the deck, unmoved fixed atoms and final free force components within the
deck forc_conv_thr, AND the output respects the HEA-4 kill rule carried to relaxation legs (no SCF
reaching the iteration at which the supervisor stops, PWSCF wall within the deck's leg ceiling);
an otherwise converged leg that breaks it is KILL_RULE_EXCEEDED. Basin rules and thresholds are
read from results/lowtail_dft_2026-09-16/operating_decisions.json (fixed before any output).

scorer_parse_out() delegates directly to the canonical HEA scorer. Its repaired wall-token
parser and conservative IEEE notice handling are used without altering output bytes or module
state. Historical status fields are retained as aliases for callers of the prepared readout.

Usage: python src/s2/lowtail_dft/lt_readout.py [--plan ...] [--decisions ...] [--runs-root runs] [--json ...]
       python src/s2/lowtail_dft/lt_readout.py --scorer-crosscheck   # canonical scorer vs every registered banked HEA output
Exit 0 when every leg is terminal, 3 while any leg is PENDING.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lt_geometry as geo  # noqa: E402
import lt_qe as qe  # noqa: E402
from lt_common import ROOT, RY_BOHR_TO_EV_A, RY_TO_EV, evidence, read_json, rel, sha256_file, write_json  # noqa: E402

sys.path.insert(0, str(ROOT / "src" / "dft"))
import hea_panel_readout as scorer  # noqa: E402

PLAN = ROOT / "results/lowtail_dft_2026-09-16/deck_plan.json"
DECISIONS = ROOT / "results/lowtail_dft_2026-09-16/operating_decisions.json"
OUT_JSON = ROOT / "results/lowtail_dft_2026-09-16/relaxation_readout.json"
FIXED_TOL_A = 1e-6
FORCE_PRINT_TOL_RY_BOHR = 5e-9
ENERGY_PRINT_TOL_RY = 1e-8  # SCF energy prints 8 decimals; Final energy prints 10.
ITERATION = re.compile(r"iteration\s*#\s*(\d+)")   # the counter src/dft/research_batch.py execute() watches


EXIT_NOTE = re.compile(r"^Note: The following floating-point exceptions are signalling:", re.M)


def scorer_parse_out(path, allow_relax: bool = True) -> dict:
    """Call the canonical scorer without transforming evidence or monkeypatching its helpers."""
    path = Path(path)
    result = scorer.parse_out(path, allow_relax=allow_relax)
    notes = len(EXIT_NOTE.findall(qe.read_text(path))) if path.exists() else 0
    return dict(result, status_unmodified=result["status"],
                severe_failures_unmodified=sorted(set(result.get("severe_failures", []))),
                exit_note_lines=notes)


def kill_rule_check(text: str, wall_s, limits: dict) -> dict:
    iterations = [int(x) for x in ITERATION.findall(text)]
    max_it = max(iterations) if iterations else None
    reasons = []
    if max_it is not None and max_it >= limits["stop_when_iteration_begins"]:
        reasons.append(f"an SCF reached iteration {max_it} (supervisor stops once {limits['stop_when_iteration_begins']} begins)")
    if wall_s is not None and wall_s > limits["leg_wall_ceiling_s"]:
        reasons.append(f"PWSCF wall {wall_s:.0f} s exceeds the leg ceiling {limits['leg_wall_ceiling_s']} s")
    return dict(max_iteration_seen=max_it, wall_s=wall_s, leg_wall_ceiling_s=limits["leg_wall_ceiling_s"],
                exceeded=bool(reasons), reasons=reasons)


def read_leg(deck: dict, runs_root: Path, deck_root: Path = ROOT) -> dict:
    out = Path(runs_root) / deck["manifest_dir"] / f"{deck['job']}.out"
    rec = dict(job=f"{deck['site']}/{deck['job']}", output=rel(out), state=deck["state"], projector=deck["projector"])
    try:
        parsed_out = scorer_parse_out(out, allow_relax=True)
    except (scorer.Fatal, ValueError) as error:
        rec.update(status="REJECTED_BY_READOUT", reasons=[f"malformed scorer evidence: {error}"])
        return rec
    rec["scorer_status"] = parsed_out["status"]
    rec["scorer"] = {k: parsed_out.get(k) for k in ("status_unmodified", "severe_failures_unmodified", "exit_note_lines",
                                                     "job_done", "not_achieved", "max_seconds_hit", "max_steps_hit",
                                                     "severe_failures", "bfgs_converged", "n_energies", "iterations", "killed",
                                                     "rejected", "wall_s", "totmag", "absmag")}
    text = qe.read_text(out) if out.exists() else None
    if text is not None:
        rec["kill_rule"] = kill_rule_check(text, parsed_out.get("wall_s"), deck["supervisor_limits"])
    if parsed_out["status"] != "CONVERGED":
        rec["status"] = parsed_out["status"]
        return rec
    if rec["kill_rule"]["exceeded"]:
        rec.update(status="KILL_RULE_EXCEEDED", reasons=rec["kill_rule"]["reasons"])
        return rec
    deck_path = Path(deck_root) / deck["path"]
    if deck.get("sha256") and sha256_file(deck_path) != deck["sha256"]:
        rec.update(status="REJECTED_BY_READOUT", reasons=["deck bytes differ from the frozen plan"])
        return rec
    try:
        deck_in = qe.parse_input(qe.read_text(deck_path))
        relax = qe.parse_relax(text, deck_in["nat"])
    except ValueError as error:
        rec.update(status="REJECTED_BY_READOUT", reasons=[f"malformed relaxation evidence: {error}"])
        return rec
    reasons = []
    if deck_in["calculation"] != "relax":
        reasons.append("the frozen input is not a relaxation")
    if relax["header"]["nat"] != deck_in["nat"]:
        reasons.append("printed nat differs from the deck")
    if parsed_out.get("wall_s") is None or rec["kill_rule"]["max_iteration_seen"] is None:
        reasons.append("wall or SCF iteration evidence missing for the kill-rule check")
    cycles = relax["bfgs_scf_cycles"]
    if (len(qe.BFGS_OK.findall(text)) != 1 or cycles != relax["n_energies"]
            or cycles != len(relax["scf_iterations"]) or cycles != len(relax["force_blocks"])):
        reasons.append("BFGS cycles, converged SCFs, energies and total-force blocks do not match")
    final_energies = qe.FINAL_ENERGY.findall(text)
    if len(final_energies) != 1 or relax["final_energy_Ry"] is None:
        reasons.append("expected exactly one finite Final energy")
    elif abs(relax["final_energy_Ry"] - parsed_out["E_Ry"]) > ENERGY_PRINT_TOL_RY:
        reasons.append("Final energy differs from the last converged SCF energy")
    if text.count("Begin final coordinates") != 1 or text.count("End final coordinates") != 1:
        reasons.append("expected exactly one final-coordinate block")
    if relax["force_blocks"] and relax["bfgs_converged"]:
        positions = [text.rfind("Forces acting on atoms"), text.find("bfgs converged"),
                     text.find("Final energy"), text.find("Begin final coordinates"),
                     text.find("End final coordinates"), text.find("JOB DONE")]
        if any(x < 0 for x in positions) or positions != sorted(positions):
            reasons.append("final force, BFGS, energy, coordinates and completion markers are out of order")
    final = relax["final_coordinates"]
    if final is None:
        reasons.append("no parseable 'Begin final coordinates' block")
    else:
        elements = [qe.element_of(s) for s in final["symbols"]]
        if elements != deck_in["elements"]:
            reasons.append("final-coordinate elements differ from the deck")
        start = np.asarray(deck_in["positions"])
        end = np.asarray(final["positions"])
        if deck_in["fixed"] and float(np.max(np.abs(end[deck_in["fixed"]] - start[deck_in["fixed"]]))) > FIXED_TOL_A:
            reasons.append("fixed atoms moved")
    if relax["force_error"] or not relax["force_blocks"]:
        reasons.append("final total-force block missing or malformed")
    else:
        thr = deck["forc_conv_thr_Ry_bohr"]
        mask = np.asarray(deck_in["if_pos"], dtype=float)
        comp = float(np.max(np.abs(relax["force_blocks"][-1] * mask))) / RY_BOHR_TO_EV_A
        rec["final_free_max_component_Ry_bohr"] = comp
        rec["final_free_fmax_eV_A"] = qe.free_fmax(relax["force_blocks"][-1], deck_in["if_pos"])
        if comp > thr + FORCE_PRINT_TOL_RY_BOHR:
            reasons.append(f"final free force component {comp:.3e} Ry/bohr exceeds forc_conv_thr {thr:.1e}")
    if reasons:
        rec.update(status="REJECTED_BY_READOUT", reasons=reasons)
        return rec
    rec.update(status="ACCEPTED", energy_eV=parsed_out["E_eV"],
               final_energy_eV=(relax["final_energy_Ry"] * RY_TO_EV if relax["final_energy_Ry"] is not None else None),
               total_magnetization_muB=parsed_out["totmag"], absolute_magnetization_muB=parsed_out["absmag"],
               bfgs_scf_cycles=relax["bfgs_scf_cycles"], bfgs_steps=relax["bfgs_steps"],
               final_positions_A=final["positions"], output_evidence=evidence(out))
    return rec


def assign(leg: dict, site: dict, reference_positions, thresholds: dict) -> dict:
    pos = leg["final_positions_A"]
    cell = site["cell_A"]
    s, n, ax = site["site_index"], site["n_slab"], site["axial_O_index"]
    disp = geo.mic(np.asarray(pos[s]) - np.asarray(reference_positions[s]), cell)
    lift, displacement = float(disp[2]), float(np.linalg.norm(disp))
    d_ads = geo.distance(pos, s, n, cell)
    d_ax = geo.distance(pos, s, ax, cell)
    metals = [j for j in range(n) if j not in site["oxygen_indices"]]
    nearest = min(metals, key=lambda j: geo.distance(pos, n, j, cell))
    label = geo.basin(lift, d_ax, d_ads, nearest == s, thresholds)
    flags = []
    if (lift >= thresholds["lift_min_A"]) != (displacement > thresholds["lift_min_A"]):
        flags.append("LIFT_DEFINITIONS_DISAGREE")
    return dict(site_lift_z_A=lift, site_displacement_A=displacement, site_to_adsO_A=d_ads, site_to_axialO_A=d_ax,
                adsO_nearest_metal_index=nearest, adsO_nearest_metal_distance_A=geo.distance(pos, n, nearest, cell),
                basin=label, flags=flags)


def site_outcome(recon: dict, unrecon: dict, thresholds: dict) -> dict:
    legs = dict(O_recon=recon, O_unrecon=unrecon)
    missing = {k: v["status"] for k, v in legs.items() if v["status"] != "ACCEPTED"}
    if missing:
        return dict(outcome="UNDECIDED", reason="O leg not accepted", legs=missing)
    b = {k: v["assignment"]["basin"] for k, v in legs.items()}
    dE = recon["energy_eV"] - unrecon["energy_eV"]
    dM = (None if recon["total_magnetization_muB"] is None or unrecon["total_magnetization_muB"] is None
          else recon["total_magnetization_muB"] - unrecon["total_magnetization_muB"])
    flags = []
    if dM is not None and abs(dM) >= thresholds["magnetization_flag_muB"]:
        flags.append("MAGNETIZATION_DIFFERS")
    common = dict(basins=b, E_recon_minus_E_unrecon_eV=dE, dM_total_muB=dM, flags=flags)
    if any(x in ("O_OFF_SITE", "MIXED_UNASSIGNED") for x in b.values()):
        return dict(common, outcome="UNDECIDED", reason="an O leg is O_OFF_SITE or MIXED_UNASSIGNED")
    if b["O_recon"] == "RECONSTRUCTED" and b["O_unrecon"] == "RECONSTRUCTED":
        return dict(common, outcome="RECONSTRUCTION_SUPPORTED")
    if b["O_recon"] == "UNRECONSTRUCTED" and b["O_unrecon"] == "UNRECONSTRUCTED":
        return dict(common, outcome="RECONSTRUCTION_NOT_SUPPORTED")
    if b["O_recon"] == "RECONSTRUCTED" and b["O_unrecon"] == "UNRECONSTRUCTED":
        margin = thresholds["energy_order_margin_eV"]
        order = ("LIFTED_LOWER" if dE < -margin else "UNLIFTED_LOWER" if dE > margin else "ORDER_WITHIN_SPIN_START_SPREAD")
        return dict(common, outcome="TWO_LOCAL_BASINS", energy_order=order, energy_order_margin_eV=margin)
    return dict(common, outcome="BASINS_CROSSED")


def primary_plan(plan: dict) -> dict:
    """Select the nine prepared primary legs without editing the historical plan."""
    decks = [d for d in plan["decks"] if d["projector"] == "atomic" and d.get("role") == "primary"]
    if len(decks) != 9 or len({d["site"] for d in decks}) != 3:
        raise ValueError("primary readout requires exactly nine atomic legs at three sites")
    for site in {d["site"] for d in decks}:
        if sorted(d["state"] for d in decks if d["site"] == site) != ["O_recon", "O_unrecon", "slab"]:
            raise ValueError("primary site lacks its slab and two O starts")
    return dict(plan, decks=decks)


TERMINAL_FAILURE_STATUSES = {"TERMINAL_OUTPUT_MISSING", "TERMINAL_QC_MISSING", "SCHEDULER_FAILED",
                             "QC_EVIDENCE_INVALID", "TERMINAL_QC_FAILED"}


def readout(plan: dict, decisions: dict, runs_root: Path, deck_root: Path = ROOT,
            terminal_failures: dict | None = None) -> dict:
    th = decisions["thresholds"]
    sites = {s["tag"]: s for s in plan["sites"]}
    legs = {}
    for deck in plan["decks"]:
        legs[(deck["site"], deck["state"], deck["projector"])] = read_leg(deck, runs_root, deck_root)
    by_job = {leg["job"]: leg for leg in legs.values()}
    for job, failure in (terminal_failures or {}).items():
        if job not in by_job or failure.get("status") not in TERMINAL_FAILURE_STATUSES:
            raise ValueError("invalid terminal evidence override: " + job)
        leg = by_job[job]
        leg["numerical_readout_status"] = leg["status"]
        leg.update(status=failure["status"], terminal_evidence=failure)
        for key in ("energy_eV", "final_energy_eV", "final_positions_A"):
            leg.pop(key, None)
    results = []
    for tag, site in sites.items():
        site = dict(site)
        slab_symbols = qe.parse_input(qe.read_text(Path(deck_root) / next(
            d["path"] for d in plan["decks"] if d["site"] == tag and d["state"] == "slab")))["elements"]
        site["oxygen_indices"] = [i for i, e in enumerate(slab_symbols) if e == "O"]
        for proj in sorted({d["projector"] for d in plan["decks"]}):
            slab = legs.get((tag, "slab", proj))
            if slab is None:
                continue
            if slab["status"] == "ACCEPTED":
                ref, ref_label = slab["final_positions_A"][:site["n_slab"]], "DFT_RELAXED_SLAB"
            else:
                ref, ref_label = site["clean_positions_A"], "REFERENCE_MACE_SLAB"
            o_legs = {}
            for state in ("O_recon", "O_unrecon"):
                leg = legs[(tag, state, proj)]
                if leg["status"] == "ACCEPTED":
                    leg["assignment"] = dict(assign(leg, site, ref, th), reference=ref_label)
                o_legs[state] = leg
            results.append(dict(site=tag, projector=proj, reference=ref_label, slab_status=slab["status"],
                                legs={k: {kk: vv for kk, vv in v.items() if kk != "final_positions_A"} for k, v in o_legs.items()},
                                outcome=site_outcome(o_legs["O_recon"], o_legs["O_unrecon"], th)))
    statuses = [leg["status"] for leg in legs.values()]
    return dict(schema="lowtail-relaxation-readout-v3",
                scorer=evidence(ROOT / "src/dft/hea_panel_readout.py"),
                scorer_input_corrections=[],
                leg_counts={s: statuses.count(s) for s in sorted(set(statuses))},
                pending=sorted(v["job"] for v in legs.values() if v["status"] == "PENDING"),
                legs=[{k: v for k, v in leg.items() if k != "final_positions_A"} for leg in legs.values()],
                sites=results, thresholds=th)


CROSSCHECK_JSON = ROOT / "results/lowtail_dft_2026-09-16/scorer_crosscheck.json"


def scorer_crosscheck() -> dict:
    """Canonical scorer against banked readouts; legacy corrected fields alias the same direct call."""
    import lt_sources as src
    reg = src.registry()
    rows = []
    for e in reg["entries"]:
        out = ROOT / e["output"]
        try:
            raw = scorer.parse_out(out, allow_relax=False)
            unmodified, fatal = raw["status"], None
        except scorer.Fatal as error:
            unmodified, fatal = "FATAL", str(error)
        corrected = scorer_parse_out(out, allow_relax=False)
        rows.append(dict(job=e["job"], output=evidence(out), readout_status=e["status"], readout=e["readout"],
                         scorer_unmodified=unmodified, scorer_unmodified_fatal=fatal,
                         scorer_wall_corrected_only=corrected["status_unmodified"],
                         severe_failures_unmodified=corrected["severe_failures_unmodified"],
                         scorer_corrected=corrected["status"], severe_failures_corrected=sorted(set(corrected["severe_failures"])),
                         exit_note_lines=corrected["exit_note_lines"],
                         agrees_with_readout=bool((e["status"] == "ACCEPTED") == (corrected["status"] == "CONVERGED"))))

    def count(key):
        return {s: sum(r[key] == s for r in rows) for s in sorted({r[key] for r in rows})}

    only_note = sum(1 for r in rows if r["scorer_wall_corrected_only"] == "REJECTED" and r["severe_failures_unmodified"]
                    and all("floating" in s.lower() for s in r["severe_failures_unmodified"]))
    return dict(schema="lowtail-scorer-crosscheck-v2", scorer=evidence(ROOT / "src/dft/hea_panel_readout.py"),
                n_outputs=len(rows), unidentified=reg["unidentified"], scorer_input_corrections=[],
                scorer_canonical_counts=count("scorer_corrected"),
                readout_status_counts=count("readout_status"), scorer_unmodified_counts=count("scorer_unmodified"),
                scorer_wall_corrected_only_counts=count("scorer_wall_corrected_only"),
                scorer_corrected_counts=count("scorer_corrected"),
                n_rejected_only_for_exit_note=only_note,
                n_corrected_agree_with_readout=sum(r["agrees_with_readout"] for r in rows), rows=rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", type=Path, default=PLAN)
    ap.add_argument("--decisions", type=Path, default=DECISIONS)
    ap.add_argument("--runs-root", type=Path, default=ROOT / "runs")
    ap.add_argument("--json", type=Path, default=OUT_JSON)
    ap.add_argument("--scorer-crosscheck", action="store_true")
    ap.add_argument("--primary-only", action="store_true", help="score the nine atomic primary legs only")
    args = ap.parse_args(argv)
    if args.scorer_crosscheck:
        c = scorer_crosscheck()
        write_json(CROSSCHECK_JSON, c)
        print(f"unmodified {c['scorer_unmodified_counts']}; corrected {c['scorer_corrected_counts']}; "
              f"agree with readouts {c['n_corrected_agree_with_readout']}/{c['n_outputs']}")
        return 0 if c["n_corrected_agree_with_readout"] == c["n_outputs"] else 2
    plan = read_json(args.plan)
    result = readout(primary_plan(plan) if args.primary_only else plan, read_json(args.decisions), args.runs_root)
    if args.primary_only:
        result["unrun_projector_controls"] = "Nine ortho controls remain conditional and are outside this readout."
    result["plan"] = evidence(args.plan)
    result["decisions"] = evidence(args.decisions)
    write_json(args.json, result)
    print(f"legs: {result['leg_counts']}")
    for s in result["sites"]:
        print(f"  {s['site']} {s['projector']}: {s['outcome']['outcome']}")
    return 3 if result["pending"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
