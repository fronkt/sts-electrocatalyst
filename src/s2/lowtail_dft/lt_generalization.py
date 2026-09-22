"""Generalization row 1 (2026-09-22): NOT LICENSED relaxation decks for the p10 bracketing sites. Nothing is submitted.

Row definition (docs/research/lowtail-generalization-sizing-2026-09-22.md section 2, bracket reading): under the
adsorbate_intact policy of the independent S8 review, the two sites whose eta values the linear p10 interpolates,
for each of Cu8Cr23Mn35Co34 and Cu26Ni9Cr31Co33 (results/s8_ranking_statistic_2026-09-19/independent_review/
diagnostics.json, p10.sites_at_lower_value / sites_at_upper_value). Each site gets the three legs of the
2026-09-16 set (clean slab, *O from the census endpoint, *O from the unreconstructed start), HUBBARD (atomic)
only, rendered through the lt_decks.py explicit-row CLI (--sites-json / --out-root), so every deck is
byte-consistent with runs/hea/lowtail_validation_2026-09-16.

Before rendering, every site is cross-checked in three places: the diagnostics (seed, site, eta), the census
readout per_site.csv (same eta, Cr initial metal, admitted by the policy, *O endpoint category) and the census
record itself (same eta; lt_decks.site_geometries then refuses any record that is not a Cr-bound *O on its own
clean slab). Cu26Ni9Cr31Co33 seed 17 site 1 has an intact (NORMAL) census *O endpoint; its O_recon leg therefore
starts from an unlifted census endpoint, which the manifest comment and the preparation record state.

Outputs under results/lowtail_generalization_2026-09-22: row1_sites.json (the CLI input), deck_plan.json and
relax_survey_manifest.json (from lt_decks.py), row1_cost_table.json / row1_cost_table.md, row1_preparation.json.
Costs use the lt_cost.py model of the 2026-09-18 launch spec under the current anchors, with the spec's frozen
2026-09-18 anchors beside them, and the spec's scheduler conventions (src/dft/prepare_lowtail_launch.py:63-67).

Usage:
  python src/s2/lowtail_dft/lt_generalization.py            # build the row and its records
  python src/s2/lowtail_dft/lt_generalization.py --check    # re-render, compare bytes with the built row, write nothing
"""
from __future__ import annotations

import argparse
import csv
import math
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lt_cost as cost  # noqa: E402
import lt_decks as decks  # noqa: E402
import lt_geometry as geo  # noqa: E402
import lt_qe as qe  # noqa: E402
import lt_sources as src  # noqa: E402
from lt_common import ROOT, evidence, read_json, rel, sha256_file, write_json, write_text_lf  # noqa: E402

sys.path.insert(0, str(ROOT / "src" / "dft"))
import hea_deck  # noqa: E402

DATE = "2026-09-22"
ROW = "row1"
POLICY = "adsorbate_intact"
COMPOSITIONS = ("Cu8Cr23Mn35Co34", "Cu26Ni9Cr31Co33")
DIAGNOSTICS = ROOT / "results/s8_ranking_statistic_2026-09-19/independent_review/diagnostics.json"
REVIEW = "docs/research/s8-ranking-independent-review-2026-09-19.md:97"
SIZING = "docs/research/lowtail-generalization-sizing-2026-09-22.md"
PER_SITE = ROOT / "results/site_census_2026-09-06/readout_full/per_site.csv"
CENSUS_DIR = ROOT / "results/site_census_2026-09-06/results"
SPEC = ROOT / "results/lowtail_dft_2026-09-18/launch_spec.json"
SPEC_PLAN = ROOT / "results/lowtail_dft_2026-09-18/deck_plan.json"
DECISIONS = ROOT / "results/lowtail_dft_2026-09-18/operating_decisions.json"
DECK_ROOT = ROOT / f"runs/hea/lowtail_generalization_{DATE}"
RESULTS = ROOT / f"results/lowtail_generalization_{DATE}"
SITES_JSON = RESULTS / f"{ROW}_sites.json"
MANIFEST = f"m_generalization_{ROW}_{DATE}.txt"
NOTE = (f"generalization {ROW}: p10 bracketing sites ({POLICY} policy) of {COMPOSITIONS[0]} and {COMPOSITIONS[1]}; "
        "sequenced after the discriminating SCF test on the Cu8 clean-slab stall reads out")
LICENCE = "the entrant's dated A11.R3 line after the discriminating SCF test reads out"
LICENCE_NOTE = "NOT LICENSED: needs the entrant's dated A11.R3 line after the discriminating SCF test reads out"
PROJECTION_SECONDS = 1800   # per-leg projwfc allowance of the 2026-09-18 launch spec (src/dft/prepare_lowtail_launch.py:30)
SLURM_MARGIN_S = 120        # wall_minutes margin of the same spec (src/dft/prepare_lowtail_launch.py:66)
ETA_TOL_V = 1e-9


def census_path(formula: str, seed: int) -> Path:
    """The census result file holding a seed: mpa0__<F> for seeds 0-2, mpa0_ext__<F>__sAA-BB for later triples."""
    if seed < 3:
        return CENSUS_DIR / f"mpa0__{formula}_result.json"
    a = 3 * (seed // 3)
    return CENSUS_DIR / f"mpa0_ext__{formula}__s{a:02d}-{a + 2:02d}_result.json"


def readout_rows() -> dict:
    """MPA-0 rows of the census readout keyed by (formula, seed, site)."""
    with open(PER_SITE, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["tag"] == "mpa0"]
    out = {}
    for r in rows:
        key = (r["formula"], int(r["seed"]), int(r["site_index"]))
        if key in out:
            raise ValueError(f"{key}: duplicate mpa0 readout row")
        out[key] = r
    return out


def bracketing_sites() -> list:
    """The p10 supports of each composition under the policy, eta cross-checked in diagnostics, readout and census."""
    diag = read_json(DIAGNOSTICS)
    readout = readout_rows()
    sites = []
    for formula in COMPOSITIONS:
        p10 = diag["policies"][POLICY]["compositions"][formula]["p10"]
        if p10["status"] != "DEFINED" or not p10["method"].startswith("linear"):
            raise ValueError(f"{formula}: p10 is not a defined linear quantile: {p10}")
        for end, weight in (("lower", 1.0 - p10["weight_upper"]), ("upper", p10["weight_upper"])):
            supports = p10[f"sites_at_{end}_value"]
            if len(supports) != 1:
                raise ValueError(f"{formula}: the {end} p10 support is tied ({len(supports)} sites); no single bracketing site")
            s = supports[0]
            seed, site = int(s["seed"]), int(s["site_index"])
            path = census_path(formula, seed)
            record = src.census_site(path, seed, site)["site"]
            row = readout[(formula, seed, site)]
            eta = float(record["eta"])
            if abs(eta - float(s["eta_V"])) > ETA_TOL_V or abs(eta - float(row["eta_V"])) > ETA_TOL_V:
                raise ValueError(f"{formula} seed {seed} site {site}: eta differs between census, readout and diagnostics")
            if row["initial_metal"] != "Cr" or row["all_states_adsorbate_intact"] != "True":
                raise ValueError(f"{formula} seed {seed} site {site}: not a Cr site admitted by the {POLICY} policy")
            sites.append(dict(formula=formula, census=rel(path), seed=seed, site=site, eta_V=eta, bracket=end,
                              interpolation_weight=weight, p10_V=p10["value_V"], n_retained=p10["n"],
                              endpoint=dict(O=row["O_category"], OH=row["OH_category"], OOH=row["OOH_category"],
                                            O_metal_O_A=float(row["O_m_o_A"]), reconstructed_states=int(row["reconstructed_states"]),
                                            all_states_intact=row["all_states_intact"] == "True",
                                            all_states_adsorbate_intact=True, readout_manifest=row["manifest"])))
    return sites


def endpoint_comment(sites: list) -> str:
    parts = []
    for s in sites:
        text = f"{s['formula']} s{s['seed']} site{s['site']} {s['endpoint']['O']}"
        if s["endpoint"]["O"] != "RECONSTRUCTION":
            text += " (intact: its O_recon leg starts from an unlifted census endpoint)"
        parts.append(text)
    return f"Census *O endpoint category per site ({rel(PER_SITE)} O_category): " + "; ".join(parts) + "."


def builder_argv(sites: list) -> list:
    """The lt_decks.py explicit-row flags of this row, repository-relative."""
    return ["--sites-json", rel(SITES_JSON), "--out-root", rel(DECK_ROOT), "--results-dir", rel(RESULTS),
            "--manifest", MANIFEST, "--projectors", "atomic", "--date", DATE, "--note", NOTE, "--licence", LICENCE,
            "--decisions", rel(DECISIONS), "--comment", endpoint_comment(sites)]


def scheduler_figures(legs: list, ceiling_key: str, ranks: int) -> dict:
    """The launch-spec conventions of src/dft/prepare_lowtail_launch.py:63-67 for n legs at concurrency one."""
    n = len(legs)
    walls = [leg[ceiling_key] for leg in legs]
    wall_minutes = math.ceil((max(walls) + PROJECTION_SECONDS + SLURM_MARGIN_S) / 60)
    return dict(n_legs=n, planning_core_h=sum(leg["planning_core_h"] for leg in legs),
                ceiling_core_h=sum(leg["ceiling_core_h"] for leg in legs),
                relaxation_ceiling_core_h=sum(walls) * ranks / 3600,
                projection_ceiling_core_h=n * PROJECTION_SECONDS * ranks / 3600,
                wall_minutes=wall_minutes, scheduler_ceiling_core_h=n * wall_minutes * ranks / 60)


def cost_table(plan: dict) -> dict:
    spec, spec_plan = read_json(SPEC), read_json(SPEC_PLAN)
    inputs = cost.cost_model_inputs()
    ranks = inputs["ranks"]
    frozen_anchor = spec_plan["cost_inputs"]["anchors"]["atomic"]
    frozen_bands = spec_plan["cost_inputs"]["bands"]
    legs = []
    for d in plan["decks"]:
        parsed = qe.parse_input(qe.read_text(ROOT / d["path"]))
        band = ("winner_slab" if d["state"] == "slab" else "winner_O") + "|atomic"
        frozen = cost.deck_cost(parsed["elements"], parsed["cell"], "atomic", frozen_anchor, frozen_bands[band], inputs,
                                parsed["params"]["max_seconds"])
        c = d["cost"]
        legs.append(dict(site=d["site"], job=d["job"], state=d["state"], nat=d["nat"], path=d["path"],
                         planning_core_h=c["planning_core_h"], ceiling_core_h=c["ceiling_core_h"],
                         p90_formula_core_h=c["p90_formula_core_h"], planning_wall_h=c["planning_wall_h"],
                         ceiling_wall_h=c["ceiling_wall_h"], leg_wall_ceiling_s=d["supervisor_limits"]["leg_wall_ceiling_s"],
                         planning_ionic_steps=c["planning_ionic_steps"], ceiling_ionic_steps_p90=c["ceiling_ionic_steps_p90"],
                         memory_printed_estimate_GB=c["memory_printed_estimate_GB"],
                         memory_maxrss_scaled_GiB=c["memory_maxrss_scaled_GiB"], fits_node=c["fits_node"],
                         ceiling_exceeds_deck_max_seconds=c["ceiling_exceeds_deck_max_seconds"],
                         spec_basis=dict(planning_core_h=frozen["planning_core_h"], ceiling_core_h=frozen["ceiling_core_h"],
                                         leg_wall_ceiling_s=int(math.ceil(frozen["ceiling_wall_s"])))))
    spec_legs = [dict(planning_core_h=leg["spec_basis"]["planning_core_h"], ceiling_core_h=leg["spec_basis"]["ceiling_core_h"],
                      leg_wall_ceiling_s=leg["spec_basis"]["leg_wall_ceiling_s"]) for leg in legs]
    cu8 = [j for j in spec["jobs"] if j["site"] == "Cu8Cr23Mn35Co34__s20_site2"]
    anchors = plan["cost_inputs"]["anchors"]["atomic"]
    return dict(
        schema="lowtail-generalization-cost-table-v1", row=ROW, date=DATE, status="PREPARED_NOT_SUBMITTED", licensed=False,
        note=LICENCE_NOTE, projector="atomic", ranks=ranks, concurrency=1,
        cost_model=dict(module="src/s2/lowtail_dft/lt_cost.py", rule="deck_cost: measured HEA per-SCF anchors x banked relaxation-step "
                        "bands; ceiling = max(3 x planning, p90 formula); force reference = winner endpoints of the "
                        "2026-09-16 zero-compute readout (no DFT force exists at any row-1 site)",
                        force_reference=plan["cost_inputs"]["force_reference"],
                        bands={k: dict(scf_cycles_p50=b["scf_cycles_p50"], scf_cycles_p90=b["scf_cycles_p90"],
                                       subsequent_iterations_p50=b["subsequent_iterations_p50"],
                                       subsequent_iterations_p90=b["subsequent_iterations_p90"], n_basis=b["n_basis"])
                               for k, b in plan["cost_inputs"]["bands"].items() if k.endswith("|atomic")}),
        anchors=dict(current=dict(n_accepted_atomic_scfs=anchors["n"], first_iterations_p50=anchors["first_iterations_p50"],
                                  first_iterations_p90=anchors["first_iterations_p90"], per_iteration_norm=anchors["per_iteration_norm"]),
                     spec_2026_09_18=dict(n_accepted_atomic_scfs=frozen_anchor["n"], first_iterations_p50=frozen_anchor["first_iterations_p50"],
                                          first_iterations_p90=frozen_anchor["first_iterations_p90"],
                                          per_iteration_norm=frozen_anchor["per_iteration_norm"], source=evidence(SPEC_PLAN))),
        legs=legs,
        totals=dict(current_anchors=scheduler_figures(legs, "leg_wall_ceiling_s", ranks),
                    spec_2026_09_18_anchors=scheduler_figures(spec_legs, "leg_wall_ceiling_s", ranks)),
        reference=dict(
            launch_spec_2026_09_18=dict(path=rel(SPEC), n_legs=len(spec["jobs"]), planning_core_h=spec["planning_core_hours"],
                                        relaxation_ceiling_core_h=spec["relaxation_ceiling_core_hours"],
                                        projection_ceiling_core_h=spec["projection_ceiling_core_hours"],
                                        wall_minutes=spec["wall_minutes"], scheduler_ceiling_core_h=spec["scheduler_ceiling_core_hours"]),
            sizing_note=dict(path=SIZING, rule="4 x the Cu8Cr23Mn35Co34 seed20 site2 legs of the 2026-09-18 spec",
                             planning_core_h=4 * sum(j["cost"]["planning_core_h"] for j in cu8),
                             ceiling_core_h=4 * sum(j["cost"]["ceiling_core_h"] for j in cu8))),
        limitations=["Planning and ceiling costs are empirical estimates, not guarantees of convergence.",
                     "No DFT force exists at any row-1 site: the Ni31 seed-1 endpoint forces of the 2026-09-16 zero-compute "
                     "readout set the step bands, as in the 2026-09-18 spec.",
                     "Array 20813525 observed a clean-slab leg fail at the SCF ceiling (538 core-h) and an adsorbate leg reach "
                     f"1,194 core-h before its kill ({SIZING} section 3); the bands do not model that failure mode."])


def cost_markdown(table: dict) -> str:
    cur, frozen = table["totals"]["current_anchors"], table["totals"]["spec_2026_09_18_anchors"]
    ref = table["reference"]
    lines = [f"# Generalization {ROW} - cost and ceiling ({DATE})", "",
             f"{LICENCE_NOTE}.", "",
             f"{cur['n_legs']} legs = 4 sites x (slab, O_recon, O_unrecon), HUBBARD (atomic), {table['ranks']} ranks, concurrency 1. "
             "Cost model: src/s2/lowtail_dft/lt_cost.py deck_cost as in results/lowtail_dft_2026-09-18/launch_spec.json "
             "(measured HEA per-SCF anchors x banked relaxation-step bands; ceiling = max(3 x planning, p90 formula)).", "",
             "| site | job | nat | planning core-h | ceiling core-h | planning wall h | ceiling wall h | leg wall ceiling s | spec-basis planning | spec-basis ceiling |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for leg in table["legs"]:
        sb = leg["spec_basis"]
        lines.append(f"| {leg['site']} | {leg['job']} | {leg['nat']} | {leg['planning_core_h']:.1f} | {leg['ceiling_core_h']:.1f} | "
                     f"{leg['planning_wall_h']:.2f} | {leg['ceiling_wall_h']:.2f} | {leg['leg_wall_ceiling_s']} | "
                     f"{sb['planning_core_h']:.1f} | {sb['ceiling_core_h']:.1f} |")
    lines.append(f"| total ({cur['n_legs']}) | | | {cur['planning_core_h']:.1f} | {cur['ceiling_core_h']:.1f} | | | | "
                 f"{frozen['planning_core_h']:.1f} | {frozen['ceiling_core_h']:.1f} |")
    a = table["anchors"]
    lines += ["",
              f"Current anchors: {a['current']['n_accepted_atomic_scfs']} accepted atomic SCFs (first-SCF iterations p50 "
              f"{a['current']['first_iterations_p50']}, p90 {a['current']['first_iterations_p90']}). Spec basis: the frozen 2026-09-18 "
              f"anchors, {a['spec_2026_09_18']['n_accepted_atomic_scfs']} accepted atomic SCFs (p50 {a['spec_2026_09_18']['first_iterations_p50']}, "
              f"p90 {a['spec_2026_09_18']['first_iterations_p90']}).", "",
              "Launch-spec scheduler conventions (src/dft/prepare_lowtail_launch.py:63-67), current anchors: relaxation ceiling "
              f"{cur['relaxation_ceiling_core_h']:.1f} core-h (rounded per-leg walls), projection ceiling {cur['projection_ceiling_core_h']:.0f} core-h "
              f"({cur['n_legs']} x {PROJECTION_SECONDS} s), wall {cur['wall_minutes']} min per task, scheduler ceiling "
              f"{cur['scheduler_ceiling_core_h']:.0f} core-h. Spec-basis anchors: relaxation ceiling {frozen['relaxation_ceiling_core_h']:.1f}, "
              f"wall {frozen['wall_minutes']} min, scheduler ceiling {frozen['scheduler_ceiling_core_h']:.0f} core-h.", "",
              f"Reference: the nine-leg 2026-09-18 spec carries {ref['launch_spec_2026_09_18']['planning_core_h']:.1f} planning / "
              f"{ref['launch_spec_2026_09_18']['relaxation_ceiling_core_h']:.1f} relaxation-ceiling / "
              f"{ref['launch_spec_2026_09_18']['scheduler_ceiling_core_h']:.0f} scheduler-ceiling core-h; the sizing note's bracket-row "
              f"proxy ({ref['sizing_note']['rule']}) is {ref['sizing_note']['planning_core_h']:.1f} planning / "
              f"{ref['sizing_note']['ceiling_core_h']:.1f} ceiling core-h.", ""]
    lines += [f"- {text}" for text in table["limitations"]]
    return "\n".join(lines) + "\n"


def preparation(plan: dict, sites: list, argv: list) -> dict:
    ops = read_json(DECISIONS)
    spec = read_json(SPEC)
    manifest = DECK_ROOT / MANIFEST
    manifest_text = manifest.read_text(encoding="utf-8")
    licence = [ln for ln in manifest_text.split("\n") if "not licensed" in ln.lower()]
    if len(licence) != 1:
        raise ValueError("the row manifest must carry exactly one NOT LICENSED line")
    if spec["exclusions"] != hea_deck.EXCLUDE:
        raise ValueError("launch-spec exclusions differ from the EXCLUDE list of record")
    by_tag = {s["tag"]: s for s in plan["sites"]}
    rows = []
    for s in sites:
        tag = decks.site_tag(s)
        ps = by_tag[tag]
        recon = ps["start_geometry"]["O_recon"]["site_geometry_vs_census_clean_slab"]
        basin = geo.basin(recon["site_lift_z_A"], recon["site_to_axialO_A"], recon["site_to_adsO_A"], True, ops["thresholds"])
        rows.append(dict(tag=tag, formula=s["formula"], seed=s["seed"], site=s["site"], eta_V=s["eta_V"], bracket=s["bracket"],
                         interpolation_weight=s["interpolation_weight"], p10_V=s["p10_V"], n_retained=s["n_retained"],
                         endpoint=s["endpoint"], census=ps["census"], site_index=ps["site_index"], n_slab=ps["n_slab"],
                         census_checks=ps["census_checks"],
                         census_O_endpoint_vs_clean_slab=recon,
                         census_O_endpoint_basin_under_operating_thresholds=basin))
    legs = [dict(site=d["site"], state=d["state"], projector=d["projector"], job=d["job"], prefix=d["prefix"], path=d["path"],
                 sha256=d["sha256"], md5=d["md5"], nat=d["nat"], kmesh=d["kmesh"], nk=d["nk"], start=d["start"],
                 supervisor_limits=d["supervisor_limits"]) for d in plan["decks"]]
    return dict(
        schema="lowtail-generalization-preparation-v1", row=ROW, date=DATE, status="PREPARED_NOT_SUBMITTED",
        licensed=False, authorization=None, note=LICENCE_NOTE,
        row_definition=dict(policy=POLICY, compositions=list(COMPOSITIONS),
                            rule="for each composition, the two sites whose eta the linear p10 interpolates (sites_at_lower_value, "
                                 "sites_at_upper_value); three legs per site, atomic projector",
                            diagnostics=evidence(DIAGNOSTICS), readout=evidence(PER_SITE), review=REVIEW, sizing_note=SIZING),
        sites=rows, n_sites=len(rows), n_legs=len(legs), states=list(decks.STATES), projector="atomic", legs=legs,
        manifest=dict(**evidence(manifest), not_licensed_line=licence[0], np=hea_deck.NP, nconc=1,
                      exclusions=hea_deck.EXCLUDE, exclusions_equal_launch_spec=True),
        operating_decisions=dict(**evidence(DECISIONS), revision=ops["revision"],
                                 unreconstructed_O_height_A=ops["construction"]["unreconstructed_O_height_A"],
                                 thresholds=ops["thresholds"], kill_rule=plan["kill_rule"]),
        deck_plan=evidence(RESULTS / "deck_plan.json"), sites_json=evidence(SITES_JSON),
        builder_argv=argv, builder_command="python src/s2/lowtail_dft/lt_decks.py " + shlex.join(argv),
        readout_command=(f"python src/s2/lowtail_dft/lt_readout.py --plan {rel(RESULTS / 'deck_plan.json')} "
                         f"--decisions {rel(DECISIONS)} --primary-only"),
        implementation=plan["implementation"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="re-render and compare with the built row; write nothing")
    args = ap.parse_args(argv)
    sites = bracketing_sites()
    sites_json = [dict(formula=s["formula"], census=s["census"], seed=s["seed"], site=s["site"]) for s in sites]
    flags = builder_argv(sites)
    if args.check:
        bad = [] if read_json(SITES_JSON) == sites_json else [rel(SITES_JSON)]
        code = decks.main(flags + ["--check"])
        prep = read_json(RESULTS / f"{ROW}_preparation.json")
        bad += [leg["path"] for leg in prep["legs"] if sha256_file(ROOT / leg["path"]) != leg["sha256"]]
        if prep["builder_argv"] != flags:
            bad.append("builder_argv")
        print("ROW CHECK OK" if code == 0 and not bad else "ROW CHECK DIFFERS: " + ", ".join(bad))
        return 0 if code == 0 and not bad else 2
    write_json(SITES_JSON, sites_json)
    code = decks.main(flags)
    if code != 0:
        return code
    plan = read_json(RESULTS / "deck_plan.json")
    table = cost_table(plan)
    write_json(RESULTS / f"{ROW}_cost_table.json", table)
    write_text_lf(RESULTS / f"{ROW}_cost_table.md", cost_markdown(table))
    write_json(RESULTS / f"{ROW}_preparation.json", preparation(plan, sites, flags))
    cur = table["totals"]["current_anchors"]
    print(f"{ROW}: {cur['n_legs']} legs, planning {cur['planning_core_h']:.1f} core-h, ceiling {cur['ceiling_core_h']:.1f} core-h; "
          f"{LICENCE_NOTE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
