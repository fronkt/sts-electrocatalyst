"""(b) PREPARED relaxation decks for the three decisive low-tail Cr sites. Nothing is submitted.

Per site: the clean slab, *O started from the census MACE reconstructed endpoint, and *O started
from an unreconstructed geometry (census clean slab unchanged + O on top of the site Cr at the
operating-decision height). Primary set: HUBBARD (atomic) projector (9 decks). Paired projector
control: the same geometries with HUBBARD (ortho-atomic) (9 decks, separate manifest).

Every deck is rendered by src/dft/hea_deck.py render_deck (the docs/92 settings of record: MP U set,
FM starts of record, 80/640 Ry, MV 0.01 Ry, k-mesh rule 4 2 1, nosym/noinv, coordinates that
re-parse exactly, census FixAtoms as if_pos 0 0 0) and then changed in exactly one line,
calculation = 'scf' -> 'relax'; the &IONS bfgs, forc_conv_thr and nstep of the template apply.

Usage:
  python src/s2/lowtail_dft/lt_decks.py            # build decks, plan, manifests, decisions, cost
  python src/s2/lowtail_dft/lt_decks.py --check    # re-render and compare bytes, write nothing
  python src/s2/lowtail_dft/lt_decks.py --mace-starts   # also relax each deck start with MACE-MPA-0
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lt_cost as cost  # noqa: E402
import lt_decisions as decisions  # noqa: E402
import lt_geometry as geo  # noqa: E402
import lt_qe as qe  # noqa: E402
import lt_sources as src  # noqa: E402
from lt_common import ROOT, evidence, md5_bytes, read_json, rel, sha256_bytes, sha256_file, write_json, write_text_lf  # noqa: E402

sys.path.insert(0, str(ROOT / "src" / "dft"))
import hea_deck  # noqa: E402

DATE = "2026-09-16"
SITES = (
    dict(formula="Cu8Cr23Mn35Co34", census="results/site_census_2026-09-06/results/mpa0_ext__Cu8Cr23Mn35Co34__s18-20_result.json", seed=20, site=2),
    dict(formula="Ni31Cr29Cu5Mn35", census="results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json", seed=1, site=0),
    dict(formula="Fe25Co25Ni25Cr25", census="results/site_census_2026-09-06/results/mpa0__Fe25Co25Ni25Cr25_result.json", seed=2, site=0),
)
STATES = ("slab", "O_recon", "O_unrecon")
PROJECTORS = ("atomic", "ortho")
DECK_ROOT = ROOT / "runs/hea/lowtail_validation_2026-09-16"
RESULTS = ROOT / "results/lowtail_dft_2026-09-16"
ZERO_COMPUTE = RESULTS / "zero_compute/zero_compute_readout.json"
MANIFEST_PRIMARY = DECK_ROOT / "m_lowtail_validation_2026-09-16.txt"
MANIFEST_CONTROL = DECK_ROOT / "m_lowtail_validation_projector_control_2026-09-16.txt"
SURVEY_MANIFEST = RESULTS / "relax_survey_manifest.json"
HEADER = "# PREPARED 2026-09-16 - submission sequenced after arrays 20781971/20781972 report measured per-SCF cost"


def site_tag(site: dict) -> str:
    return f"{site['formula']}__s{site['seed']}_site{site['site']}"


def site_geometries(site: dict, height_A: float) -> dict:
    c = src.census_site(ROOT / site["census"], site["seed"], site["site"])
    rec = c["site"]
    s = int(rec["initial_binding_metal_index"])
    O = rec["relaxed_states"]["O"]
    slab = c["slab"]
    checks = dict(initial_metal=rec["initial_binding_metal"], O_final_binding_index=O["final_binding_metal_index"],
                  O_state_symbols_prefix_equal_slab=O["symbols"][:len(slab["symbols"])] == slab["symbols"],
                  fixed_equal=sorted(O["fixed_atom_indices"]) == sorted(slab["fixed_atom_indices"]),
                  cell_equal=O["cell_A"] == slab["cell_A"], O_converged_by_force=O["converged_by_force"],
                  slab_converged_by_force=slab["converged_by_force"])
    if not (checks["initial_metal"] == "Cr" and checks["O_final_binding_index"] == s and checks["O_state_symbols_prefix_equal_slab"]
            and checks["fixed_equal"] and checks["cell_equal"]):
        raise ValueError(f"{site_tag(site)}: census record is not a Cr-bound *O on its own clean slab: {checks}")
    n = len(slab["symbols"])
    cell = [list(map(float, r)) for r in slab["cell_A"]]
    clean = [list(map(float, p)) for p in slab["positions_A"]]
    top = [clean[s][0], clean[s][1], clean[s][2] + height_A]
    unrecon = clean + [top]
    fixed = sorted(int(i) for i in slab["fixed_atom_indices"])
    axial = geo.axial_oxygen(slab["symbols"], clean, s, cell, n)
    geoms = dict(
        slab=dict(symbols=list(slab["symbols"]), positions=clean, source=f"decoration_records[seed={site['seed']}].relaxed_slab",
                  mace_energy_eV=slab["energy_eV"]),
        O_recon=dict(symbols=list(O["symbols"]), positions=[list(map(float, p)) for p in O["positions_A"]],
                     source=f"per_site_records[seed={site['seed']},site={site['site']}].relaxed_states.O", mace_energy_eV=O["energy_eV"]),
        O_unrecon=dict(symbols=list(slab["symbols"]) + ["O"], positions=unrecon,
                       source=f"decoration_records[seed={site['seed']}].relaxed_slab + O at site metal + {height_A} A along +z",
                       mace_energy_eV=None))
    for name in ("O_recon", "O_unrecon"):
        g = geoms[name]
        g["site_geometry_vs_census_clean_slab"] = geo.site_geometry(g["symbols"], g["positions"], cell, s, n, clean, axial["index"])
        others = [geo.distance(g["positions"], n, j, cell) for j in range(n) if j != s]
        g["adsO_nearest_non_site_atom_A"] = min(others)
    return dict(census=c, tag=site_tag(site), cell=cell, fixed=fixed, site_index=s, n_slab=n, axial_O_index=axial["index"],
                axial_O_clean_A=axial["clean_distance_A"], checks=checks, geometries=geoms)


def render_relax(prefix: str, symbols, positions, cell, fixed, projector: str) -> str:
    scf = hea_deck.render_deck(prefix, symbols, positions, cell, fixed, projector)
    old, new = "  calculation = 'scf'", "  calculation = 'relax'"
    lines = scf.split("\n")
    if lines.count(old) != 1:
        raise ValueError("template must carry exactly one calculation = 'scf' line")
    relax = "\n".join(new if line == old else line for line in lines)
    diff = [(a, b) for a, b in zip(scf.split("\n"), relax.split("\n")) if a != b]
    if diff != [(old, new)]:
        raise ValueError(f"relax conversion changed more than the calculation line: {diff}")
    parsed = qe.parse_input(relax)
    if (parsed["calculation"] != "relax" or parsed["positions"] != [list(map(float, p)) for p in positions]
            or parsed["fixed"] != sorted(fixed) or parsed["params"]["ion_dynamics"] != "bfgs"):
        raise ValueError("relax deck does not re-parse to the source geometry and bfgs relaxation")
    return relax


def build(write: bool = True) -> dict:
    ops = decisions.build()
    height = ops["construction"]["unreconstructed_O_height_A"]
    zc = read_json(ZERO_COMPUTE)
    inputs = cost.cost_model_inputs()
    measured = cost.measured_hea_scfs()
    survey = cost.relax_survey()
    fref = {}
    for r in zc["realizations"]:
        if r["geometry"] in ("winner_slab", "winner_O") and r["variant"] == "baseline":
            fref[(r["geometry"], r["projector"])] = r["DFT"]["fmax_free_eV_A"]
    kill = ops["kill_rule"]
    survey_manifest = cost.survey_manifest(survey)
    plan = dict(schema="lowtail-deck-plan-v1", date=DATE, status="PREPARED_NOT_SUBMITTED", header=HEADER,
                operating_decisions=rel(RESULTS / "operating_decisions.json"), sites=[], decks=[],
                kill_rule=dict(source=kill["source"], stop_when_iteration_begins=kill["stop_when_iteration_begins"],
                               wall_limit=kill["wall_limit"], on_stop=kill["on_stop"], readout_enforcement=kill["readout_enforcement"]),
                cost_inputs=dict(cost_model=inputs, anchors={p: cost.anchors(measured, p) for p in PROJECTORS},
                                 survey_counts=dict(n_rows=len(survey["rows"]), n_excluded=len(survey["excluded"]),
                                                    excluded=[{k: v for k, v in e.items() if k != "files"} for e in survey["excluded"]]),
                                 survey_qc=cost.survey_qc(survey),
                                 survey_manifest=dict(path=rel(SURVEY_MANIFEST), n_used=survey_manifest["n_used"],
                                                      n_excluded=survey_manifest["n_excluded"]),
                                 force_reference=dict(source=rel(ZERO_COMPUTE),
                                                      values={f"{g}|{p}": v for (g, p), v in sorted(fref.items())}),
                                 evidence=cost.evidence_list()))
    bands = {}
    for key, f in fref.items():
        bands[key] = cost.band_statistics(survey, f)
    plan["cost_inputs"]["bands"] = {f"{g}|{p}": b for (g, p), b in sorted(bands.items())}
    rendered = {}
    for site in SITES:
        sg = site_geometries(site, height)
        plan["sites"].append(dict(tag=sg["tag"], formula=site["formula"], seed=site["seed"], site=site["site"],
                                  census=evidence(ROOT / site["census"]), site_index=sg["site_index"], n_slab=sg["n_slab"],
                                  axial_O_index=sg["axial_O_index"], axial_O_clean_A=sg["axial_O_clean_A"], fixed=sg["fixed"],
                                  census_checks=sg["checks"],
                                  start_geometry={k: {kk: vv for kk, vv in v.items() if kk not in ("positions", "symbols")}
                                                  for k, v in sg["geometries"].items()},
                                  clean_positions_A=sg["geometries"]["slab"]["positions"], cell_A=sg["cell"]))
        for state in STATES:
            g = sg["geometries"][state]
            for proj in PROJECTORS:
                job = f"{state}__{proj}"
                prefix = f"lt__{sg['tag']}__{job}"
                text = render_relax(prefix, g["symbols"], g["positions"], sg["cell"], sg["fixed"], proj)
                path = DECK_ROOT / sg["tag"] / f"{job}.in"
                data = text.encode("utf-8")
                rendered[path] = text
                parsed = qe.parse_input(text)
                band = bands[("winner_slab" if state == "slab" else "winner_O", proj)]
                anchor = plan["cost_inputs"]["anchors"][proj]
                c = cost.deck_cost(g["symbols"], sg["cell"], proj, anchor, band, inputs, parsed["params"]["max_seconds"])
                if parsed["params"]["electron_maxstep"] != kill["electron_maxstep"]:
                    raise ValueError(f"{job}: electron_maxstep differs from HEA-4")
                limits = dict(stop_when_iteration_begins=kill["stop_when_iteration_begins"], max_scf_iterations=kill["max_scf_iterations"],
                              leg_wall_ceiling_s=int(math.ceil(c["ceiling_wall_s"])), electron_maxstep=parsed["params"]["electron_maxstep"],
                              source=kill["source"])
                plan["decks"].append(dict(site=sg["tag"], state=state, projector=proj, job=job, prefix=prefix,
                                          path=rel(path), manifest_dir=rel(path.parent)[len("runs/"):],
                                          md5=md5_bytes(data), sha256=sha256_bytes(data), nat=parsed["nat"],
                                          ntyp=len(parsed["species"]), kmesh=list(hea_deck.kgrid_from_cell(sg["cell"])),
                                          nk=hea_deck.choose_nk(hea_deck.kpoint_count(hea_deck.kgrid_from_cell(sg["cell"]))),
                                          site_index=sg["site_index"], adsorbate_O_index=(sg["n_slab"] if state != "slab" else None),
                                          axial_O_index=sg["axial_O_index"], fixed=sg["fixed"],
                                          forc_conv_thr_Ry_bohr=parsed["params"]["forc_conv_thr"], nstep=parsed["params"]["nstep"],
                                          max_seconds=parsed["params"]["max_seconds"], cost=c, supervisor_limits=limits,
                                          start=g["source"], role=("primary" if proj == "atomic" else "paired projector control")))
    totals = {}
    for role in ("primary", "paired projector control"):
        rows = [d for d in plan["decks"] if d["role"] == role]
        totals[role] = dict(n_decks=len(rows), planning_core_h=sum(d["cost"]["planning_core_h"] for d in rows),
                            ceiling_core_h=sum(d["cost"]["ceiling_core_h"] for d in rows),
                            max_memory_printed_GB=max(d["cost"]["memory_printed_estimate_GB"] for d in rows),
                            max_memory_maxrss_scaled_GiB=max(d["cost"]["memory_maxrss_scaled_GiB"] for d in rows),
                            any_ceiling_exceeds_max_seconds=any(d["cost"]["ceiling_exceeds_deck_max_seconds"] for d in rows))
    plan["totals"] = totals
    manifests = {MANIFEST_PRIMARY: manifest_text(plan, "primary"), MANIFEST_CONTROL: manifest_text(plan, "paired projector control")}
    for text in manifests.values():
        hea_deck.check_manifest_text(text, expect_not_licensed=True)
    if write:
        plan["cost_inputs"]["survey_manifest"]["sha256"] = write_json(SURVEY_MANIFEST, survey_manifest)
        for path, text in rendered.items():
            write_text_lf(path, text, refuse_different=True)
        for path, text in manifests.items():
            write_text_lf(path, text)
        write_json(RESULTS / "operating_decisions.json", ops)
        plan["manifests"] = {rel(p): sha256_bytes(t.encode("utf-8")) for p, t in manifests.items()}
        plan["implementation"] = [evidence(p) for p in sorted(HERE.glob("lt_*.py"))] + [evidence(ROOT / "src/dft/hea_deck.py")]
        write_json(RESULTS / "deck_plan.json", plan)
    return dict(plan=plan, rendered=rendered, manifests=manifests, decisions=ops, survey_manifest=survey_manifest)


def manifest_text(plan: dict, role: str) -> str:
    rows = [d for d in plan["decks"] if d["role"] == role]
    t = plan["totals"][role]
    lines = [HEADER,
             f"# Low-tail Cr-site DFT relaxations ({role}): per site clean slab, *O from the census MACE reconstructed endpoint,",
             "# *O from the unreconstructed start (census clean slab + O on top of the site Cr). docs/92 settings of record,",
             f"# {'HUBBARD (atomic)' if role == 'primary' else 'HUBBARD (ortho-atomic)'}, FM starts, k 4 2 1, calculation = 'relax' (bfgs; census FixAtoms as if_pos 0 0 0).",
             "# Not licensed for submission by this preparation: submission needs a dated approval line after the two arrays report.",
             f"# Plan, costs and basin rules: {rel(RESULTS / 'deck_plan.json')}, {rel(RESULTS / 'operating_decisions.json')}.",
             "# Readout: python src/s2/lowtail_dft/lt_readout.py (accepts a leg only when src/dft/hea_panel_readout.py parse_out(allow_relax=True) is CONVERGED,",
             "# read with two recorded input corrections: pw.x hour-format wall tokens and the gfortran exit note; IEEE_INVALID still rejects).",
             f"# KILL RULE ({plan['kill_rule']['source']}, carried to relaxation legs): stop once any SCF begins iteration "
             f"{plan['kill_rule']['stop_when_iteration_begins']} or the leg wall exceeds its ceiling wall s below;",
             "# record KILLED, preserve scratch, no automatic restart; a stopped leg yields no energy, geometry or basin.",
             f"# PLANNING {t['planning_core_h']:.1f} core-h, CEILING {t['ceiling_core_h']:.1f} core-h for {t['n_decks']} decks "
             f"(measured HEA per-SCF cost x banked relaxation steps; lt_cost.py). Max memory {t['max_memory_printed_GB']:.1f} GB printed-estimate basis, "
             f"{t['max_memory_maxrss_scaled_GiB']:.1f} GiB MaxRSS basis per deck.",
             "#",
             "# per deck (site  job  nat  planning core-h  ceiling core-h  planning wall h  ceiling wall h  ceiling wall s  memory GB  md5):"]
    for d in rows:
        c = d["cost"]
        lines.append(f"#   {d['site']:32s} {d['job']:18s} {d['nat']:3d}  {c['planning_core_h']:8.1f}  {c['ceiling_core_h']:8.1f}  "
                     f"{c['planning_wall_h']:6.2f}  {c['ceiling_wall_h']:6.2f}  {d['supervisor_limits']['leg_wall_ceiling_s']:6d}  "
                     f"{c['memory_printed_estimate_GB']:6.1f}  {d['md5']}")
    lines += ["#", f"# SUBMIT WITH EXCLUDE={hea_deck.EXCLUDE}", f"# NP={hea_deck.NP} NCONC=1"]
    for d in rows:
        lines.append(f"{d['manifest_dir']} {d['job']} .in {d['nk']}")
    return "\n".join(lines) + "\n"


def mace_start_check(threads: int = 2) -> dict:
    """MACE-MPA-0 relaxations from the exact deck start geometries (census protocol: fmax 0.05, 300 steps)."""
    import lt_mace
    ops = decisions.build()
    th = ops["thresholds"]
    out = dict(schema="lowtail-mace-start-check-v1", role="MACE outcome from each DFT deck start, same basin rule as the DFT readout",
               thresholds=th, operating_decisions="results/lowtail_dft_2026-09-16/operating_decisions.json", sites=[])
    calc = None
    for site in SITES:
        sg = site_geometries(site, ops["construction"]["unreconstructed_O_height_A"])
        c = sg["census"]
        if calc is None:
            calc = lt_mace.load_calculator(lt_mace.DEFAULT_CHECKPOINT, c["model"]["sha256_bytes"], threads)
        protocol = read_json(ROOT / site["census"])["manifest"]["protocol"]
        row = dict(tag=sg["tag"], census=evidence(ROOT / site["census"]), protocol=dict(fmax_eV_A=protocol["fmax_eV_A"], steps=protocol["steps"]),
                   deck_starts={state: rel(DECK_ROOT / sg["tag"] / f"{state}__atomic.in") for state in ("O_recon", "O_unrecon")}, starts={})
        clean = sg["geometries"]["slab"]["positions"]
        for state in ("O_recon", "O_unrecon"):
            g = sg["geometries"][state]
            r = lt_mace.relax(calc, g["symbols"], g["positions"], sg["cell"], sg["fixed"], protocol["fmax_eV_A"], protocol["steps"])
            s, n = sg["site_index"], sg["n_slab"]
            nearest, dmin = geo.nearest(g["symbols"], r["positions_A"], n, sg["cell"], want=lambda x: x not in ("O", "H"))
            sgeo = geo.site_geometry(g["symbols"], r["positions_A"], sg["cell"], s, n, clean, sg["axial_O_index"])
            row["starts"][state] = dict(energy_eV=r["energy_eV"], steps_taken=r["steps_taken"], converged_by_force=r["converged_by_force"],
                                        max_constrained_force_eV_A=r["max_constrained_force_eV_A"], site_geometry=sgeo,
                                        adsO_nearest_metal=dict(index=nearest, distance_A=dmin),
                                        basin=geo.basin(sgeo["site_lift_z_A"], sgeo["site_to_axialO_A"], sgeo["site_to_adsO_A"],
                                                        nearest == s, th),
                                        census_O_energy_eV=sg["geometries"]["O_recon"]["mace_energy_eV"])
        row["E_recon_minus_E_unrecon_eV"] = row["starts"]["O_recon"]["energy_eV"] - row["starts"]["O_unrecon"]["energy_eV"]
        out["sites"].append(row)
    out["checkpoint"] = dict(path=str(lt_mace.DEFAULT_CHECKPOINT), sha256=sha256_file(lt_mace.DEFAULT_CHECKPOINT))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="re-render and compare with the written decks; write nothing")
    ap.add_argument("--mace-starts", action="store_true")
    args = ap.parse_args(argv)
    if args.check:
        built = build(write=False)
        bad = [rel(p) for p, t in built["rendered"].items() if not p.exists() or p.read_bytes() != t.encode("utf-8")]
        bad += [rel(p) for p, t in built["manifests"].items() if not p.exists() or p.read_bytes() != t.encode("utf-8")]
        print("CHECK OK" if not bad else "CHECK DIFFERS: " + ", ".join(bad))
        return 0 if not bad else 2
    built = build(write=True)
    for role, t in built["plan"]["totals"].items():
        print(f"{role}: {t['n_decks']} decks, planning {t['planning_core_h']:.1f} core-h, ceiling {t['ceiling_core_h']:.1f} core-h")
    if args.mace_starts:
        write_json(RESULTS / "mace_start_check.json", mace_start_check())
        print("mace start check written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
