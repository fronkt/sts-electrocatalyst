"""Aggregate the 2026-09-06 site-integrity census results (docs/91 readouts (a)-(f)).

Reads every manifest under results/site_census_2026-09-06/manifests/ and its result under
results/, classifies every retained site with hea_oer.site_integrity, and writes
readout/{per_site.csv, per_site.json, reproduction.json, ranking.json, distribution.json}.
It refuses to run while any manifest's result is missing or unfinished unless --partial is
given, in which case the missing manifests are listed in every output. Nothing here scores a
docs/43 prediction; the banked order and the banked numbers are read from the tracked LF
source copies and never rewritten. An optional --o2-records file (CENSUS-1b *O2 fragment
relaxations with the same model's O2 gas energy) adds a fragment-binding diagnostic and
changes no rule value.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from hea_oer import site_integrity as integrity  # noqa: E402
from scripts import site_census_plan as plan  # noqa: E402

REPRODUCTION_ETA_TOL_V = 1e-6
REPRODUCTION_BOND_TOL_A = 1e-3
LEADER = "Ni31Cr29Cu5Mn35"
LEADER_BANKED_SEED = 1
EXPECTED_MIN_KS = (1, 2, 3, 4, 6, 12, 24, 48, 96, 120)

PER_SITE_COLUMNS = (
    "manifest", "arm", "tag", "formula", "candidate_status", "seed", "site_index",
    "initial_metal", "eta_V", "pls", "dG_OH", "dG_O", "dG_OOH",
    "OH_m_o_A", "OH_tier", "OH_h_location", "OH_category", "O_m_o_A", "O_tier", "O_category",
    "OOH_m_o_A", "OOH_tier", "OOH_o_o_A", "OOH_o_o_class", "OOH_h_location", "OOH_h_carrier",
    "OOH_binding_O", "OOH_binding_metal", "OOH_category", "OOH_slab_rms_A", "OOH_slab_max_A",
    "unconverged_states", "weak_states", "reconstructed_states", "pathway",
    "all_states_intact", "all_states_adsorbate_intact",
)


def sha256_lf(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def collect(manifest_dir, result_dir, partial):
    stems = plan.queue_order([p.stem for p in Path(manifest_dir).glob("*.json")])
    if not stems:
        raise FileNotFoundError("no manifests under " + str(manifest_dir))
    loaded, missing = {}, []
    for stem in stems:
        out = Path(result_dir) / (stem + "_result.json")
        manifest = load_json(Path(manifest_dir) / (stem + ".json"))
        if not out.exists():
            missing.append(dict(stem=stem, reason="result missing"))
            continue
        result = load_json(out)
        if result.get("manifest_id") != manifest.get("manifest_id"):
            missing.append(dict(stem=stem, reason="result manifest_id differs from manifest"))
            continue
        if result.get("status") not in ("complete", "complete_with_errors"):
            missing.append(dict(stem=stem, reason=f"result status {result.get('status')}"))
            continue
        loaded[stem] = dict(manifest=manifest, result=result, result_path=out,
                            result_sha256_lf=sha256_lf(out))
    if missing and not partial:
        names = ", ".join(f"{m['stem']} ({m['reason']})" for m in missing)
        raise RuntimeError("census incomplete; rerun with --partial to read what exists: " + names)
    return loaded, missing


def per_site_rows(loaded, thresholds):
    rows, classified = [], {}
    for stem, item in loaded.items():
        info = plan.parse_stem(stem)
        for record in item["result"]["results"]:
            formula = record["formula"]
            row = record.get("row")
            if record.get("status") != "evaluated" or row is None:
                rows.append(dict(manifest=stem, arm=info["arm"], tag=info["tag"], formula=formula,
                                 candidate_status=record.get("status")))
                continue
            cls = integrity.classify_row(row, thresholds)
            classified[(stem, formula)] = dict(row=row, classification=cls)
            for site in cls["sites"]:
                s = site["states"]
                entry = dict(manifest=stem, arm=info["arm"], tag=info["tag"], formula=formula,
                             candidate_status="evaluated", seed=site["seed"],
                             site_index=site["site_index"], initial_metal=site["initial_binding_metal"],
                             eta_V=site["eta_V"], pls=site["pls"], dG_OH=site["dG_OH"],
                             dG_O=site["dG_O"], dG_OOH=site["dG_OOH"],
                             unconverged_states=site["n_unconverged_states"],
                             weak_states=site["n_weak_states"],
                             reconstructed_states=site["n_reconstructed_states"],
                             pathway=site["pathway"],
                             all_states_intact=site["all_states_intact"],
                             all_states_adsorbate_intact=site["all_states_adsorbate_intact"])
                for species in ("OH", "O"):
                    st = s[species]
                    entry[species + "_m_o_A"] = None if st is None else st["m_o_A"]
                    entry[species + "_tier"] = None if st is None else st["bond_tier"]
                    entry[species + "_category"] = None if st is None else st["category"]
                entry["OH_h_location"] = None if s["OH"] is None else s["OH"]["h_location"]
                st = s["OOH"]
                disp = None if st is None else st["slab_displacement"]
                entry.update(OOH_m_o_A=None if st is None else st["m_o_A"],
                             OOH_tier=None if st is None else st["bond_tier"],
                             OOH_o_o_A=None if st is None else st["o_o_A"],
                             OOH_o_o_class=None if st is None else st["o_o_class"],
                             OOH_h_location=None if st is None else st["h_location"],
                             OOH_h_carrier=None if st is None else st["h_carrier"],
                             OOH_binding_O=None if st is None else st["binding_O"],
                             OOH_binding_metal=None if st is None else st["binding_metal"],
                             OOH_category=None if st is None else st["category"],
                             OOH_slab_rms_A=None if disp is None else disp["free_atom_rms_A"],
                             OOH_slab_max_A=None if disp is None else disp["free_atom_max_A"])
                rows.append(entry)
    return rows, classified


OOH_KEYS = ("bond_tier", "m_o_A", "m_o_by_O_A", "binding_O", "o_o_A", "o_o_class", "h_location",
            "h_carrier", "binding_metal", "initial_metal", "migration", "reconstruction",
            "converged_by_force", "category", "pathway_state", "intact", "adsorbate_intact")


def reproduction(loaded, classified, banked):
    """Readout (a): per CENSUS-1 manifest, compare the min-site eta and winner with the banked row."""
    out = {}
    for stem, item in loaded.items():
        info = plan.parse_stem(stem)
        if info["arm"] != "CENSUS-1":
            continue
        formula = info["formula"]
        record = next((r for r in item["result"]["results"] if r["formula"] == formula), None)
        if record is None or record.get("status") != "evaluated":
            out[formula] = dict(verdict="NOT EVALUATED", candidate_status=None if record is None else record.get("status"))
            continue
        row = record["row"]
        bank = banked[formula]
        sites = row["per_site_records"]
        winner = min(sites, key=lambda s: s["eta"])
        eta_diff = winner["eta"] - bank["eta"]
        bonds = {sp: winner["bonds"][sp] - bank["bonds"][sp] for sp in ("OH", "O", "OOH")}
        eta_ok = abs(eta_diff) <= REPRODUCTION_ETA_TOL_V
        winner_ok = (winner["seed"] == bank["bonds"]["seed"]
                     and winner["bonds"]["site_metal"] == bank["bonds"]["site_metal"]
                     and all(abs(v) <= REPRODUCTION_BOND_TOL_A for v in bonds.values()))
        cls = classified[(stem, formula)]["classification"]["sites"]
        winner_cls = next(c for c in cls if c["seed"] == winner["seed"] and c["site_index"] == winner["site_index"])
        out[formula] = dict(
            verdict="REPRODUCED" if (eta_ok and winner_ok) else "NOT REPRODUCED",
            eta_min_V=winner["eta"], banked_eta_V=bank["eta"], eta_difference_V=eta_diff,
            eta_within_tolerance=eta_ok, eta_tolerance_V=REPRODUCTION_ETA_TOL_V,
            winner=dict(seed=winner["seed"], site_index=winner["site_index"],
                        site_metal=winner["bonds"]["site_metal"],
                        bonds={sp: winner["bonds"][sp] for sp in ("OH", "O", "OOH")},
                        starts={sp: winner["bonds"][sp + "_start"] for sp in ("OH", "O", "OOH")}),
            banked_winner=dict(seed=bank["bonds"]["seed"], site_metal=bank["bonds"]["site_metal"],
                               bonds={sp: bank["bonds"][sp] for sp in ("OH", "O", "OOH")},
                               starts={sp: bank["bonds"][sp + "_start"] for sp in ("OH", "O", "OOH")}),
            bond_differences_A=bonds, winner_within_tolerance=winner_ok,
            bond_tolerance_A=REPRODUCTION_BOND_TOL_A,
            winner_site_intact=winner_cls["all_states_intact"],
            winner_site_adsorbate_intact=winner_cls["all_states_adsorbate_intact"],
            winner_site_unconverged_states=winner_cls["n_unconverged_states"],
            winner_ooh_classification={k: winner_cls["states"]["OOH"][k] for k in OOH_KEYS}
            if winner_cls["states"]["OOH"] else None,
            n_sites=len(sites), seconds=record.get("seconds"),
            environment=item["result"].get("environment"),
        )
    return out


def decisive_site(loaded, classified):
    """Readout (d): the leader's winning site OOH classification, INTACT or its category."""
    stem = f"mpa0__{LEADER}"
    if stem not in loaded:
        return dict(status="pending", manifest=stem)
    key = (stem, LEADER)
    if key not in classified:
        return dict(status="not evaluated", manifest=stem)
    row = classified[key]["row"]
    cls = classified[key]["classification"]["sites"]
    winner = min(row["per_site_records"], key=lambda s: s["eta"])
    wc = next(c for c in cls if c["seed"] == winner["seed"] and c["site_index"] == winner["site_index"])
    ooh = wc["states"]["OOH"]
    seed1 = [c for c in cls if c["seed"] == LEADER_BANKED_SEED]
    return dict(
        status="read", manifest=stem, winner_seed=winner["seed"], winner_site_index=winner["site_index"],
        winner_site_metal=winner["bonds"]["site_metal"], winner_eta_V=winner["eta"],
        winner_seed_matches_banked=bool(winner["seed"] == LEADER_BANKED_SEED),
        ooh_readout="INTACT" if ooh is not None and ooh["intact"] else (None if ooh is None else ooh["category"]),
        ooh_classification=None if ooh is None else {k: ooh[k] for k in OOH_KEYS},
        winner_site_intact=wc["all_states_intact"], winner_pathway=wc["pathway"],
        seed1_sites=[dict(site_index=c["site_index"], initial_metal=c["initial_binding_metal"],
                          eta_V=c["eta_V"], ooh_category=c["categories"]["OOH"], pathway=c["pathway"],
                          unconverged_states=c["n_unconverged_states"],
                          all_states_intact=c["all_states_intact"]) for c in seed1],
    )


def ranking(loaded, classified, banked, o2_records=None):
    """Readout (c): the gated six under the four rules on the twelve CENSUS-1 sites, plus the
    ensemble spread and the convergence counts per composition and per model."""
    rows_by_formula, cls_by_formula = {}, {}
    for formula in plan.GATED_SIX:
        key = (f"mpa0__{formula}", formula)
        if key in classified:
            rows_by_formula[formula] = classified[key]["row"]
            cls_by_formula[formula] = classified[key]["classification"]
    rules = integrity.ranking_rules(rows_by_formula, cls_by_formula, o2_records) if rows_by_formula else {}
    banked_order = sorted(plan.GATED_SIX, key=lambda f: banked[f]["eta"])
    orders = {}
    for rule in integrity.RULES:
        values = {f: rules[f][rule] for f in rules if rules[f][rule] is not None}
        complete = set(values) == set(plan.GATED_SIX)
        order = sorted(values, key=values.__getitem__)
        gaps = [dict(pair=[order[i], order[i + 1]], gap_V=values[order[i + 1]] - values[order[i]])
                for i in range(len(order) - 1)]
        orders[rule] = dict(
            values_V=values, order=order, complete=complete,
            kendall_tau_vs_banked=integrity.kendall_tau(order, banked_order) if complete else None,
            adjacent_gaps=gaps,
            excluded=[f for f in plan.GATED_SIX if f not in values],
        )
    ensemble, convergence = {}, {}
    for formula in plan.BOX_TWELVE:
        per_model, unconverged = {}, {}
        for tag in ("mpa0",) + plan.ENSEMBLE_TAGS:
            key = (f"{tag}__{formula}", formula)
            if key in classified:
                etas = [s["eta"] for s in classified[key]["row"]["per_site_records"]]
                per_model[tag] = min(etas) if etas else None
                cls = classified[key]["classification"]
                unconverged[tag] = dict(n_sites=cls["n_sites"], n_unconverged_sites=cls["n_unconverged_sites"],
                                        n_intact_sites=cls["n_all_states_intact"],
                                        n_adsorbate_intact_sites=cls["n_all_states_adsorbate_intact"],
                                        n_bridge_sites=cls["n_bridge_sites"],
                                        n_undefined_pathway_sites=cls["n_undefined_pathway_sites"])
        present = [v for v in per_model.values() if v is not None]
        ensemble[formula] = dict(min_site_eta_by_model_V=per_model,
                                 n_models=len(present),
                                 spread_V=(max(present) - min(present)) if present else None,
                                 banked_eta_V=banked[formula]["eta"])
        convergence[formula] = unconverged
    per_model_totals = {}
    for formula, per in convergence.items():
        for tag, counts in per.items():
            tot = per_model_totals.setdefault(tag, dict(n_sites=0, n_unconverged_sites=0))
            tot["n_sites"] += counts["n_sites"]
            tot["n_unconverged_sites"] += counts["n_unconverged_sites"]
    return dict(
        site_set="the twelve CENSUS-1 sites per composition (seeds 0, 1, 2 x site_index 0..3); "
                 "every rule is a minimum over its qualifying sites, an extreme-value statistic "
                 "that is comparable only at equal site count",
        rules=dict(banked="minimum eta over all retained sites (the screen's own aggregation)",
                   intact_only="minimum eta over sites whose OH, O and OOH states are all INTACT "
                               "(category NORMAL and force-converged; weak counts, desorbed does not)",
                   adsorbate_intact_only="minimum eta over sites whose three states are not desorbed, "
                                         "not dissociated, not migrated and force-converged; the "
                                         "reconstruction flag is ignored and reported beside",
                   two_pathway="minimum over sites whose OOH endpoint is *OOH (cus) or a bound *O2+H_b "
                               "(bridge), each under the four-step CHE on the retained dG with step 4 = "
                               "4.92 eV - dG(third state); sites with a desorbed, H-free or O-O-cleaved "
                               "endpoint are excluded as pathway-undefined"),
        banked_order=banked_order,
        banked_values_V={f: banked[f]["eta"] for f in plan.GATED_SIX},
        banked_adjacent_gaps=[dict(pair=[banked_order[i], banked_order[i + 1]],
                                   gap_V=banked[banked_order[i + 1]]["eta"] - banked[banked_order[i]]["eta"])
                              for i in range(len(banked_order) - 1)],
        per_formula=rules, orders=orders, ensemble_spread=ensemble,
        convergence=dict(per_formula=convergence, per_model=per_model_totals),
        o2_records_supplied=bool(o2_records),
        scores_docs43_prediction=False,
    )


def distribution(loaded, classified):
    """Readout (f): the site-eta distribution per gated composition over the CENSUS-1 and
    CENSUS-3 MACE-MPA-0 sites (all sites, and intact sites), the exact expected minimum of
    k draws without replacement, the twelve-site minimum as one draw, and the O-O class counts."""
    out = {}
    for formula in plan.GATED_SIX:
        etas, intact_etas, o_o, classes, manifests = [], [], [], {}, []
        unconverged = 0
        for (stem, f), item in classified.items():
            info = plan.parse_stem(stem)
            if f != formula or info["tag"] != "mpa0" or info["arm"] not in ("CENSUS-1", "CENSUS-3"):
                continue
            manifests.append(stem)
            for site, cls in zip(item["row"]["per_site_records"], item["classification"]["sites"]):
                etas.append(site["eta"])
                if cls["all_states_intact"]:
                    intact_etas.append(site["eta"])
                if cls["n_unconverged_states"]:
                    unconverged += 1
                ooh = cls["states"]["OOH"]
                if ooh is not None and ooh["o_o_A"] is not None:
                    o_o.append(ooh["o_o_A"])
                    classes[ooh["o_o_class"]] = classes.get(ooh["o_o_class"], 0) + 1
        twelve = [s["eta"] for (stem, f), item in classified.items() if f == formula and stem == f"mpa0__{formula}"
                  for s in item["row"]["per_site_records"]]
        out[formula] = dict(
            manifests=sorted(manifests), n_sites=len(etas), n_unconverged_sites=unconverged,
            all_sites=integrity.eta_statistics(etas),
            intact_sites=integrity.eta_statistics(intact_etas),
            expected_min_vs_k=integrity.expected_minimum_curve(etas, EXPECTED_MIN_KS),
            twelve_site_min_V=min(twelve) if twelve else None,
            o_o_A=integrity.eta_statistics(o_o), o_o_class_counts=classes,
        )
    return dict(site_set="CENSUS-1 (seeds 0-2) and CENSUS-3 (seeds 3-29) MACE-MPA-0 sites of the gated six",
                statistics="mean; sample standard deviation (ddof = 1); median; 10th percentile "
                           "(linear interpolation); min; max; expected minimum of k draws without "
                           "replacement from the empirical site set, exact",
                per_formula=out)


def load_o2_records(path):
    """Optional CENSUS-1b records: {formula: {"seed/site_index": record}} -> tuple keys."""
    if path is None:
        return None
    raw = load_json(path)
    out = {}
    for formula, sites in raw.items():
        out[formula] = {}
        for key, record in sites.items():
            seed, index = key.split("/")
            out[formula][(int(seed), int(index))] = record
    return out


def write_outputs(readout_dir, rows, repro, decisive, rank, dist, loaded, missing, thresholds, sources):
    readout_dir = Path(readout_dir)
    readout_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    header = dict(generated=stamp, partial=bool(missing), missing=missing,
                  manifests_read={stem: dict(result=str(item["result_path"].relative_to(ROOT)) if str(item["result_path"]).startswith(str(ROOT)) else str(item["result_path"]),
                                             result_sha256_lf=item["result_sha256_lf"],
                                             status=item["result"]["status"])
                                  for stem, item in loaded.items()},
                  thresholds=asdict(thresholds), sources=sources)
    with (readout_dir / "per_site.csv").open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=PER_SITE_COLUMNS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in PER_SITE_COLUMNS})
    for name, payload in (("per_site.json", dict(header, rows=rows)),
                          ("reproduction.json", dict(header, reproduction=repro, decisive_site=decisive)),
                          ("ranking.json", dict(header, ranking=rank)),
                          ("distribution.json", dict(header, distribution=dist))):
        (readout_dir / name).write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n",
                                        encoding="utf-8", newline="\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-dir", type=Path, default=plan.MANIFEST_DIR)
    parser.add_argument("--result-dir", type=Path, default=plan.RESULT_DIR)
    parser.add_argument("--out-dir", type=Path, default=plan.READOUT_DIR)
    parser.add_argument("--box-source", type=Path, default=plan.BOX_SOURCE)
    parser.add_argument("--o2-records", type=Path, default=None,
                        help="CENSUS-1b *O2 fragment records JSON {formula: {'seed/site': "
                             "{energy_eV, E_O2_gas_eV, converged_by_force}}}; diagnostic only")
    parser.add_argument("--partial", action="store_true")
    args = parser.parse_args(argv)
    thresholds = integrity.DEFAULT_THRESHOLDS
    box = load_json(args.box_source)
    banked = {row["formula"]: row for row in box["rows"]}
    loaded, missing = collect(args.manifest_dir, args.result_dir, args.partial)
    rows, classified = per_site_rows(loaded, thresholds)
    repro = reproduction(loaded, classified, banked)
    decisive = decisive_site(loaded, classified)
    rank = ranking(loaded, classified, banked, load_o2_records(args.o2_records))
    dist = distribution(loaded, classified)
    sources = {"box_source": str(args.box_source), "box_source_sha256_lf": sha256_lf(args.box_source)}
    write_outputs(args.out_dir, rows, repro, decisive, rank, dist, loaded, missing, thresholds, sources)
    print(json.dumps(dict(manifests_read=len(loaded), missing=len(missing), sites=sum(1 for r in rows if "seed" in r),
                          reproduction={f: v["verdict"] for f, v in repro.items()},
                          decisive_site=decisive.get("ooh_readout", decisive.get("status")))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
