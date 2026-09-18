"""Render the dated research-note tables from the track's result JSON files (no number typed by hand).

Usage: python src/s2/lowtail_dft/lt_report.py > <scratch>.md
"""
from __future__ import annotations

import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lt_common import ROOT, read_json  # noqa: E402

RES = ROOT / "results/lowtail_dft_2026-09-16"


def f(x, n=3, sign=False):
    if x is None:
        return "n/a"
    return f"{x:+.{n}f}" if sign else f"{x:.{n}f}"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(header))) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def rng(values, n=3, sign=False):
    return f"{f(min(values), n, sign)} to {f(max(values), n, sign)}"


def zero_compute() -> str:
    d = read_json(RES / "zero_compute/zero_compute_readout.json")
    p = d["population"]
    parts = []
    status = Counter(e["status"] for e in d["excluded"])
    parts.append(f"Population: {p['banked_outputs']} banked pw.x outputs under runs/hea; {p['accepted_by_own_readout']} accepted by their own readouts, "
                 f"all {p['used']} used; {p['excluded']} excluded ({', '.join(f'{k} {v}' for k, v in sorted(status.items()))}); {p['unidentified']} unidentified.")
    parts.append(table(["Excluded output", "Status", "Reason on record"],
                       [[e["job"], e["status"], "; ".join(e["reasons"][:2])] for e in d["excluded"]]))
    mg = d["mace_geometries"]
    parts.append("MACE re-evaluation at the stored coordinates, maximum |E_now - E_census| over the "
                 f"{len(mg)} geometries: {max(abs(v['energy_minus_stored_eV']) for v in mg.values()):.3g} eV.")
    rows = []
    for r in d["realizations"]:
        if r["geometry"].startswith("winner_"):
            s = r.get("site") or {}
            dft, mace = s.get("DFT", {}), s.get("MACE", {})
            g = s.get("geometry", {})
            rows.append([r["geometry"].replace("winner_", ""), r["projector"], f(r["DFT"]["fmax_free_eV_A"]), f(r["MACE"]["fmax_free_eV_A"]),
                         f(g.get("site_lift_z_A"), 3, True) if g else "reference", f(g.get("site_to_adsO_A")) if g else "n/a",
                         f(s["axial_O"]["distance_A"]),
                         f(dft.get("site_normal_eV_A"), 3, True), f(mace.get("site_normal_eV_A"), 3, True),
                         f(dft.get("adsO_normal_eV_A"), 3, True) if "adsO_normal_eV_A" in dft else "n/a",
                         f(dft.get("bond_stretch_eV_A"), 3, True) if "bond_stretch_eV_A" in dft else "n/a",
                         f(dft.get("pair_normal_eV_A"), 3, True) if "pair_normal_eV_A" in dft else "n/a",
                         f(dft.get("axial_O_normal_eV_A"), 3, True), f(dft.get("axial_stretch_eV_A"), 3, True),
                         f'{s.get("site_rank_by_DFT_free_force")} / {r["agreement_free"]["n_free_atoms"]}',
                         "{}{} {:.3f}".format(r["DFT"]["top_free_atoms"][0]["symbol"], r["DFT"]["top_free_atoms"][0]["index"],
                                              r["DFT"]["top_free_atoms"][0]["norm_eV_A"])])
    order = {"slab": 0, "OH": 1, "O": 2, "OOH": 3}
    rows.sort(key=lambda r: (order[r[0]], r[1]))
    arows = []
    for r in d["realizations"]:
        if r["geometry"].startswith("winner_"):
            s = r["site"]
            t2, m2 = s["DFT_axial_two_body"], s["MACE_axial_two_body"]
            arows.append([r["geometry"].replace("winner_", ""), r["projector"], "+".join(str(i) for i in t2["unit_members"]),
                          f(s["axial_O"]["distance_A"]), f(s["DFT"]["axial_stretch_eV_A"], 3, True),
                          f(t2["site_away_from_axial_eV_A"], 3, True), f(t2["axial_O_toward_site_eV_A"], 3, True),
                          f(t2["unit_toward_axial_eV_A"], 3, True), f(t2["relative_acceleration_eV_A_amu"], 4, True), t2["gap_first_order"],
                          f(m2["relative_acceleration_eV_A_amu"], 4, True)])
    arows.sort(key=lambda r: (order[r[0]], r[1]))
    parts.append(table(["State", "Projector", "DFT free fmax", "MACE free fmax", "Cr16 lift", "Cr16-O72", "Cr16-O40 (axial)",
                        "DFT F_z Cr16", "MACE F_z Cr16", "DFT F_z O72", "DFT bond stretch", "DFT pair F_z", "DFT F_z O40", "DFT axial stretch",
                        "Cr16 rank by DFT force / free atoms", "Largest DFT free force"], rows))
    parts.append(table(["State", "Projector", "Site unit", "Cr16-O40", "DFT axial stretch (two-atom)", "DFT Cr16 away from O40",
                        "DFT O40 toward Cr16", "DFT unit toward O40", "DFT relative accel O40-unit, eV/(A amu)", "DFT gap, first order",
                        "MACE relative accel"], arows))
    lead = [r for r in d["realizations"] if r["geometry"].startswith("leader_")]
    lrows = []
    for geom in ("leader_OOH_builder", "leader_OOH_pull2.10"):
        for proj in ("atomic", "ortho"):
            sel = [r for r in lead if r["geometry"] == geom and r["projector"] == proj]
            if not sel:
                continue
            s0 = sel[0]["site"]
            lrows.append([geom.replace("leader_OOH_", ""), proj, len(sel), rng([r["DFT"]["fmax_free_eV_A"] for r in sel]),
                          f(sel[0]["MACE"]["fmax_free_eV_A"]),
                          f"{s0['adsO_nearest_metal']['symbol']}{s0['adsO_nearest_metal']['index']} {f(s0['adsO_nearest_metal']['distance_A'])}",
                          rng([r["site"]["DFT"]["site_normal_eV_A"] for r in sel], 3, True)])
    parts.append(table(["Seed-0 OOH endpoint", "Projector", "Accepted realizations", "DFT free fmax range", "MACE free fmax",
                        "O72 nearest metal (A)", "DFT F_z Cr16 range"], lrows))
    erows = []
    for c in d["winner_chain_energies"]:
        for st, v in c["electronic_adsorption"].items():
            erows.append([c["projector"], f"dE_ads({st})", f(v["DFT_eV"], 4), f(v["MACE_eV"], 4), f(v["DFT_minus_MACE_eV"], 4, True)])
        for k, v in c["consecutive_differences"].items():
            erows.append([c["projector"], k.replace("_minus_", " - "), f(v["DFT_eV"], 4), f(v["MACE_eV"], 4), f(v["DFT_minus_MACE_eV"], 4, True)])
    parts.append(table(["Projector", "Electronic quantity (eV)", "DFT", "MACE", "DFT - MACE"], erows))
    prows = [[p["series"], p["projector"], p["variant"], "yes" if p["record_settings"] else "no", f(p["dE_DFT_eV"], 4, True),
              f(p["dE_MACE_eV"], 4, True), f(p["DFT_minus_MACE_eV"], 4, True)] for p in d["leader_OOH_pairs"]]
    parts.append(table(["Series", "Projector", "Spin start / setting", "80/640/0.01", "E(pull2.10)-E(builder) DFT", "MACE", "DFT - MACE"], prows))
    parts.append("Unpaired accepted realizations: " + ", ".join(d["leader_unpaired_realizations"]))
    parts.append(table(["Pending single point", "Census site lift (A)", "Coordinates equal census O endpoint", "In approved manifest", "Local output"],
                       [[r["deck"]["path"], f(r["census_site_lift_z_A"]), r["coordinates_equal_census_O_endpoint"], r["in_approved_manifest"],
                         r["status"]] for r in d["pending_endpoint_single_points"]]))
    return "\n\n".join(parts)


def decks() -> str:
    plan = read_json(RES / "deck_plan.json")
    ops = read_json(RES / "operating_decisions.json")
    parts = []
    th = ops["thresholds"]
    parts.append(table(["Operating value", "Value", "Source"], [[k, repr(v), ops["sources"][k]] for k, v in th.items()]))
    parts.append(table(["Census Cr minimum", "Site", "Axial O", "Clean Cr-O(axial)", "*O Cr-O(axial)", "Cr lift"],
                       [[f"{r['formula']} s{r['seed']}/{r['site']}", r["site_index"], r["axial_O_index"], f(r["clean_A"]), f(r["O_state_A"]),
                         f(r["site_lift_z_A"])] for r in ops["axial_minima"]["rows"]]))
    srows = []
    for s in plan["sites"]:
        g = s["start_geometry"]
        srows.append([s["tag"], s["census"]["path"], s["census"]["sha256"], s["site_index"], s["axial_O_index"],
                      f(g["O_recon"]["site_geometry_vs_census_clean_slab"]["site_lift_z_A"]),
                      f(g["O_recon"]["site_geometry_vs_census_clean_slab"]["site_to_adsO_A"]),
                      f(g["O_recon"]["site_geometry_vs_census_clean_slab"]["site_to_axialO_A"]),
                      f(g["O_unrecon"]["site_geometry_vs_census_clean_slab"]["site_to_adsO_A"]),
                      f(g["O_unrecon"]["adsO_nearest_non_site_atom_A"]), len(s["fixed"])])
    parts.append(table(["Site", "Census result", "sha256", "Cr index", "Axial O", "Recon start lift", "Recon Cr-O(ads)", "Recon Cr-O(axial)",
                        "Unrecon Cr-O(ads)", "Unrecon O nearest other atom", "Fixed atoms"], srows))
    rows = []
    for d in plan["decks"]:
        c = d["cost"]
        rows.append([d["site"], d["job"], d["nat"], c["nbnd_rule"], f(c["planning_core_h"], 1), f(c["ceiling_core_h"], 1), f(c["planning_wall_h"], 2),
                     f(c["ceiling_wall_h"], 2), f(c["memory_printed_estimate_GB"], 1), f(c["memory_maxrss_scaled_GiB"], 1), d["md5"]])
    parts.append(table(["Site", "Deck", "nat", "KS states", "Planning core-h", "Ceiling core-h", "Planning wall h", "Ceiling wall h",
                        "Memory, printed basis (GB)", "Memory, MaxRSS basis (GiB)", "md5"], rows))
    trows = []
    for role, t in plan["totals"].items():
        sel = [d["cost"] for d in plan["decks"] if d["role"] == role]
        trows.append([role, t["n_decks"], f(t["planning_core_h"], 1), f(t["ceiling_core_h"], 1),
                      rng([c["planning_core_h"] for c in sel], 1), rng([c["ceiling_core_h"] for c in sel], 1),
                      rng([c["planning_wall_h"] for c in sel], 2), rng([c["ceiling_wall_h"] for c in sel], 2),
                      rng([c["memory_printed_estimate_GB"] for c in sel], 1), rng([c["memory_maxrss_scaled_GiB"] for c in sel], 1)])
    wrows = []
    for proj in ("atomic", "ortho"):
        sel = [d["cost"] for d in plan["decks"] if d["projector"] == proj]
        wrows.append([proj, rng([c["wall_per_iteration_s"] for c in sel], 1), rng([c["wall_forces_s"] for c in sel], 1),
                      f(statistics.median(c["wall_forces_s"] for c in sel) / statistics.median(c["wall_per_iteration_s"] for c in sel), 2)])
    parts.append(table(["Projector", "Scaled wall per SCF iteration (s)", "Scaled force evaluation wall (s)", "Force / iteration"], wrows))
    parts.append(table(["Manifest", "Decks", "Planning core-h", "Ceiling core-h", "Per-deck planning", "Per-deck ceiling",
                        "Planning wall h", "Ceiling wall h", "Memory printed basis GB", "Memory MaxRSS basis GiB"], trows))
    arows = []
    for proj, a in plan["cost_inputs"]["anchors"].items():
        arows.append([proj, a["n"], f(a["per_iteration_norm"] * 1e5, 3), f(a["forces_norm"] * 1e5, 3), f(a["init_s"], 1), f(a["rest_s"], 2),
                      a["first_iterations"], a["first_iterations_p50"], a["first_iterations_p90"]])
    parts.append(table(["Projector", "Accepted HEA SCFs", "Wall/iteration per (A^3 x KS state), 1e-5 s", "Forces wall per (A^3 x KS state), 1e-5 s",
                        "init s", "remainder s", "From-scratch FM first-SCF iterations", "p50", "p90"], arows))
    brows = [[k, f(b["f_ref_eV_A"]), f"{f(b['band_eV_A'][0])}-{f(b['band_eV_A'][1])}", b["n_in_band"], b["n_bfgs_converged"], b["n_basis"],
              "; ".join(f"{Path(x['output']).as_posix()} {','.join(x['severe_failures'])}" for x in b["bfgs_converged_rejected_by_scorer"]),
              b["scf_cycles_p50"], b["scf_cycles_p90"], b["scf_cycles_max"], b["subsequent_iterations_p50"], b["subsequent_iterations_p90"],
              b["max_n_free_atoms"], b["statistics_unchanged_by_scorer_rule"]]
             for k, b in plan["cost_inputs"]["bands"].items()]
    parts.append(table(["DFT force reference", "F (eV/A)", "Band", "Relaxations in band", "BFGS-converged", "Basis (scorer CONVERGED)",
                        "BFGS-converged, scorer-rejected", "SCF cycles p50", "p90", "max", "Later-step iterations p50", "p90", "Max free atoms",
                        "Statistics unchanged by scorer rule"], brows))
    qc = plan["cost_inputs"]["survey_qc"]
    parts.append(f"Survey scorer outcomes over all {qc['n_rows']} rows: {qc['scorer_status_counts']}; BFGS-converged {qc['n_bfgs_converged']}, "
                 f"of which scorer-rejected {qc['n_bfgs_converged_scorer_rejected']}; IEEE_INVALID in {qc['n_ieee_invalid']}. "
                 f"Survey manifest {plan['cost_inputs']['survey_manifest']}.")
    k = plan["kill_rule"]
    lim = [d["supervisor_limits"]["leg_wall_ceiling_s"] for d in plan["decks"]]
    parts.append(f"Kill rule {k['source']}: stop once iteration {k['stop_when_iteration_begins']} begins; leg wall ceilings {min(lim)}-{max(lim)} s "
                 f"(atomic {rng([d['supervisor_limits']['leg_wall_ceiling_s'] for d in plan['decks'] if d['projector'] == 'atomic'], 0)}, "
                 f"ortho {rng([d['supervisor_limits']['leg_wall_ceiling_s'] for d in plan['decks'] if d['projector'] == 'ortho'], 0)}).")
    lift = ops["lift_definition"]["census_Cr_minima_lift_vs_displacement_A"]
    parts.append("Census Cr minima lift vs 3-D displacement (A): " + "; ".join(f"{f(a)} / {f(b)}" for a, b in lift))
    sc = plan["cost_inputs"]["survey_counts"]
    parts.append(f"Survey: {sc['n_rows']} banked nspin = 2 slab relaxations with a first force block; {sc['n_excluded']} excluded "
                 f"({Counter(e['reason'] for e in sc['excluded']).most_common()}).")
    return "\n\n".join(parts)


def mace_starts() -> str:
    path = RES / "mace_start_check.json"
    if not path.exists():
        return "MACE start check not present."
    d = read_json(path)
    rows = []
    for s in d["sites"]:
        for k, v in s["starts"].items():
            g = v["site_geometry"]
            rows.append([s["tag"], k, v["basin"], f(g["site_lift_z_A"]), f(g["site_to_axialO_A"]), f(g["site_to_adsO_A"]), v["steps_taken"],
                         v["converged_by_force"], f(v["energy_eV"] - v["census_O_energy_eV"], 4, True)])
    return table(["Site", "MACE start", "Basin", "Cr lift", "Cr-O(axial)", "Cr-O(ads)", "BFGS steps", "Converged", "E - E(census *O), eV"], rows)


def queue() -> str:
    out = []
    for name in ("anvil_queue_snapshot.json", "anvil_queue_snapshot_r2.json"):
        path = RES / name
        if not path.exists():
            out.append(f"{name} not present.")
            continue
        d = read_json(path)
        out.append(f"{name} requested {d['requested_at_utc']}: " + "; ".join(
            f"{r['job']} {r['state']} exit {r.get('exit_code', 'n/a')} elapsed {r['elapsed_s']} s (start {r['start']}, end {r['end']})" for r in d["rows"]))
        for task in d.get("terminal_tasks", []):
            out.append(f"  terminal task {task['task']}: {task['dir']}/{task['deck']}")
        if d.get("terminal_task_files"):
            out.append("  files:\n" + d["terminal_task_files"]["stdout"])
    return "\n".join(out)


def scorer_crosscheck() -> str:
    path = RES / "scorer_crosscheck.json"
    if not path.exists():
        return "Scorer cross-check not present."
    c = read_json(path)
    return (f"{c['n_outputs']} banked HEA outputs; readouts {c['readout_status_counts']}; scorer unmodified {c['scorer_unmodified_counts']}; "
            f"wall-corrected only {c['scorer_wall_corrected_only_counts']}; corrected {c['scorer_corrected_counts']}; "
            f"rejected only for the exit note {c['n_rejected_only_for_exit_note']}; corrected agrees with readouts {c['n_corrected_agree_with_readout']}/{c['n_outputs']}")


if __name__ == "__main__":
    print("## zero compute\n\n" + zero_compute() + "\n\n## decks\n\n" + decks() + "\n\n## mace starts\n\n" + mace_starts()
          + "\n\n## scorer cross-check\n\n" + scorer_crosscheck() + "\n\n## queue\n\n" + queue())
