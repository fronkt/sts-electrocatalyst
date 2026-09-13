"""Rank-resolution readout for a decoration-sampled site census.

Reads screen-diagnostic-v1 result JSONs of ONE model, flattens them to one row per
(composition, seed, site), and reports: the per-composition statistic under the
banked ``min`` rule and the ``median``/``p10``/``mean`` alternatives, the
reproduction check of the census min against the banked row, cluster-bootstrap
intervals over decorations, the rank-probability matrix with STABLE ranks,
adjacent-gap order probabilities in the banked order with RESOLVED / UNRESOLVED /
INVERTED / SPREAD-DECIDED labels, the decorations needed to resolve each adjacent
gap at the target probability under the observed site spread (with its
Monte-Carlo bracket), a one-way variance decomposition (within/between
decoration), Kendall tau-a of the census order against the banked order, and a
ridge model of site quantities on nearest-neighbour cation counts.

Input selection.  ``--results`` is the census results directory
(results/site_census_2026-09-06/results/) or a glob.  Only result files whose stem
matches ``--stems`` (default ``mpa0__*,mpa0_ext__*``: the P-CENSUS-1 and
P-CENSUS-3 manifests) are read; a payload whose manifest_id differs from the
manifest of the same stem, whose stem is absent from MANIFESTS.sha256, or whose
status is not complete is refused and listed.  A table mixing two model files is
refused (exit 2).  When MANIFESTS.sha256 is present every expected stem must
have landed unless ``--partial``; a partial readout carries status ``partial``
and lists the missing stems.

Admission policies (``--admit``), the site sets of docs/91 readout (c) as
hea_oer.site_integrity defines them at readout time: ``all`` (banked rule, every
site), ``no-desorbed`` (no species reached the 3.00 A desorption cut),
``intact`` (``all_states_intact``: OH, O and OOH all NORMAL and force-converged),
``adsorbate-intact`` (``all_states_adsorbate_intact``: the same ignoring the
slab-reconstruction flag) and ``two-pathway`` (``pathway`` in {cus, bridge}: the
OOH state is *OOH or *O2+H_b; the site eta is the retained four-step value under
either label, and the P-CENSUS-1b *O2 record is a diagnostic that enters no rule).
The site eta is never replaced under any policy.  ``--compare`` takes several
readouts of the same census under different policies and labels every boundary
whose verdict differs POLICY-DEPENDENT.

Exit codes: 0 readout written (complete or partial); 2 no usable results, mixed
models, missing stems without --partial, or bad input; 3 fewer than
``--min-decorations`` usable decorations for at least one composition (the
census statistics are still written, no interval is invented).

    python src/scripts/rank_resolution_readout.py --results results/site_census_2026-09-06/results/ \\
        --gated results/ranking_adequacy_2026-09-06/inputs/r4_gated.json --B 10000 --seed 0 --admit all
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
import fnmatch
import glob
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from hea_oer import rank_resolution as rr  # noqa: E402

try:  # the site-integrity classifier (docs/91 (b)); needed only for intact / two-pathway
    from hea_oer import site_integrity as integrity  # noqa: E402
except Exception:  # pragma: no cover - the module is optional here
    integrity = None

SCHEMA = "rank-resolution-v1"
DEFAULT_OUT = ROOT / "results/site_census_2026-09-06/readout/rank_resolution.json"
DEFAULT_BOX = ROOT / "results/ranking_adequacy_2026-09-06/inputs/r4_screen_box.json"
DEFAULT_STEMS = "mpa0__*,mpa0_ext__*"
ADMIT_POLICIES = ("all", "no-desorbed", "intact", "adsorbate-intact", "two-pathway")
CLASSIFIER_POLICIES = ("intact", "adsorbate-intact", "two-pathway")
RIDGE_TARGETS = ("eta", "dG_OH", "dG_O", "dG_OOH")
COMPLETE_STATUSES = ("complete", "complete_with_errors")
#: Reproduction bar, inherited from docs/91 readout (a) (docs/91:35): |census min - banked eta| <= 1e-6 V.
REPRODUCTION_ETA_TOL_V = 1e-6


def _lf_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _clean(obj):
    """JSON-safe copy: numpy -> python, non-finite floats -> None, tuples -> lists."""
    if isinstance(obj, dict):
        return OrderedDict((str(k), _clean(v)) for k, v in obj.items())
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _clean(obj.tolist())
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        return v if math.isfinite(v) else None
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


# --------------------------------------------------------------------------- input selection
def stem_of(path: Path) -> str:
    name = path.name
    return name[: -len("_result.json")] if name.endswith("_result.json") else path.stem


def read_manifest_hashes(path: Path | None) -> "OrderedDict[str, str] | None":
    """MANIFESTS.sha256 lines ``<sha256>  manifests/<stem>.json`` -> stem -> sha256."""
    if path is None or not Path(path).exists():
        return None
    out: "OrderedDict[str, str]" = OrderedDict()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        out[Path(parts[1]).stem] = parts[0]
    return out


def stem_formula(stem: str) -> str | None:
    parts = stem.split("__")
    return parts[1] if len(parts) >= 2 else None


def collect_results(spec: str, stems: list[str], manifest_dir: Path | None, hashes: "OrderedDict[str, str] | None",
                    gated_formulas: list[str] | None) -> dict:
    """Select, verify and load result JSONs.

    Returns dict(paths, payloads, skipped, refused, expected, present, missing, unverified).
    """
    p = Path(spec)
    paths = sorted(p.glob("*.json")) if p.is_dir() else sorted(Path(s) for s in glob.glob(spec))
    kept, payloads, skipped, refused = [], [], [], []

    def selected(stem: str) -> bool:
        return any(fnmatch.fnmatchcase(stem, pat) for pat in stems)

    for path in paths:
        stem = stem_of(path)
        if not selected(stem):
            skipped.append(f"{path}: stem {stem!r} outside --stems")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            skipped.append(f"{path}: {exc}")
            continue
        if not (isinstance(data, dict) and isinstance(data.get("results"), list)):
            skipped.append(f"{path}: no 'results' list")
            continue
        if data.get("status") not in COMPLETE_STATUSES:
            refused.append(OrderedDict(stem=stem, path=str(path), reason=f"status {data.get('status')!r}"))
            continue
        if hashes is not None and stem not in hashes:
            refused.append(OrderedDict(stem=stem, path=str(path), reason="stem absent from MANIFESTS.sha256"))
            continue
        if manifest_dir is not None and (Path(manifest_dir) / f"{stem}.json").exists():
            manifest = json.loads((Path(manifest_dir) / f"{stem}.json").read_text(encoding="utf-8"))
            if manifest.get("manifest_id") != data.get("manifest_id"):
                refused.append(OrderedDict(stem=stem, path=str(path),
                                           reason="result manifest_id differs from the manifest of the same stem"))
                continue
        elif hashes is not None:
            refused.append(OrderedDict(stem=stem, path=str(path), reason="manifest file missing for a listed stem"))
            continue
        payloads.append(data)
        kept.append(path)
    present = [stem_of(x) for x in kept]
    if hashes is not None:
        expected = [s for s in hashes if selected(s)
                    and (gated_formulas is None or stem_formula(s) in set(gated_formulas))]
        missing = [s for s in expected if s not in present]
        unverified = False
    else:
        expected, missing, unverified = [], [], True
    return dict(paths=kept, payloads=payloads, skipped=skipped, refused=refused, expected=expected,
                present=present, missing=missing, unverified=unverified)


# --------------------------------------------------------------------------- admission
def make_annotate(policy: str):
    """Row annotator: attaches the site-integrity classification of docs/91 (b) to every
    row (the flags the classifier-defined policies admit on).  The eta is never changed."""
    if policy not in CLASSIFIER_POLICIES:
        return None
    if integrity is None:
        raise SystemExit(f"--admit {policy} needs hea_oer.site_integrity, which could not be imported")

    def annotate(rec: dict, site, row) -> None:
        cls = integrity.classify_site(site, row.get("decoration_records"))
        rec["all_states_intact"] = bool(cls.get("all_states_intact"))
        rec["all_states_adsorbate_intact"] = (None if "all_states_adsorbate_intact" not in cls
                                              else bool(cls["all_states_adsorbate_intact"]))
        rec["pathway"] = cls.get("pathway")
        rec["state_categories"] = dict(cls.get("categories") or {})
        rec["ooh_h_transferred"] = bool(cls.get("ooh_h_transferred"))
    return annotate


def _admit_policy(name: str):
    if name == "all":
        return None
    if name == "no-desorbed":
        return lambda r: not r["desorbed_any"]
    if name == "intact":
        return lambda r: bool(r.get("all_states_intact"))
    if name == "adsorbate-intact":
        return lambda r: bool(r.get("all_states_adsorbate_intact"))
    if name == "two-pathway":
        return lambda r: r.get("pathway") in ("cus", "bridge")
    raise ValueError(f"unknown admit policy {name!r}; choose from {ADMIT_POLICIES}")


POLICY_DEFINITIONS = OrderedDict([
    ("all", "every site (the banked rule)"),
    ("no-desorbed", "no species' winning M-O distance reached the desorption cut"),
    ("intact", "site_integrity all_states_intact: OH, O and OOH all NORMAL and force-converged"),
    ("adsorbate-intact", "site_integrity all_states_adsorbate_intact: not desorbed, not dissociated, not migrated, converged; reconstruction ignored"),
    ("two-pathway", "site_integrity pathway in {cus, bridge}: OOH state is *OOH or *O2+H_b; eta unchanged"),
])


# --------------------------------------------------------------------------- helpers
def slab_index(payloads: list[dict]) -> dict[tuple[str, int], dict]:
    """(formula, seed) -> retained relaxed_slab record."""
    index = {}
    for _, row, _ in rr.iter_result_rows(payloads):
        for dec in row.get("decoration_records") or []:
            slab = dec.get("relaxed_slab")
            if slab:
                index[(row["formula"], int(dec["seed"]))] = slab
    return index


def fmt(v, nd=4):
    if v is None:
        return "-"
    if isinstance(v, float):
        return "nan" if not math.isfinite(v) else f"{v:.{nd}f}"
    return str(v)


def md_table(header: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def need_cell(need: dict | None) -> str:
    """Decorations-needed cell: count with its Monte-Carlo bracket, or the saturated report."""
    if not need:
        return "-"
    if need.get("decorations_needed") is not None:
        b = need.get("decorations_needed_bracket") or [None, None]
        cell = str(need["decorations_needed"])
        if b[0] is not None and (b[0] != need["decorations_needed"] or b[1] != need["decorations_needed"]):
            cell += f" [{b[0]}, {b[1] if b[1] is not None else '>' + str(need.get('max_decorations'))}]"
        return cell
    if need.get("saturated"):
        return (f"saturated: P({need['max_decorations']}) = {fmt(need['prob_at_max_decorations'], 3)}, "
                f"best {fmt(need['best_prob_on_grid'], 3)} at D = {need['best_decorations_on_grid']}")
    return need.get("message", "-")


def verdict_label(gap_point: float | None, p_order: float, target: float, need: dict | None) -> str:
    if gap_point is not None and not gap_point > 0:
        return "INVERTED"
    label = "RESOLVED" if p_order >= target else "UNRESOLVED"
    if need and need.get("order_reverses_at_depth"):
        label += " / SPREAD-DECIDED"
    return label


# --------------------------------------------------------------------------- readout
def build_readout(payloads: list[dict], args, box: dict | None, gated_formulas: list[str] | None) -> dict:
    rows = rr.load_site_table(payloads, admitted=_admit_policy(args.admit), annotate=make_annotate(args.admit))
    models = rr.check_single_model(rows)
    present = list(OrderedDict.fromkeys(r["formula"] for r in rows))
    missing_gated = []
    if gated_formulas is not None:
        missing_gated = [f for f in gated_formulas if f not in present]
        rows = [r for r in rows if r["formula"] in set(gated_formulas)]
        present = [f for f in gated_formulas if f in present]
    box_rows = {r["formula"]: r for r in box["rows"]} if box is not None else {}
    if box is not None:
        banked_all = [r["formula"] for r in sorted(box["rows"], key=lambda r: r["eta"])]
        order = [f for f in banked_all if f in present] + [f for f in present if f not in banked_all]
    else:
        stat_min = rr.composition_statistic(rows, "min")
        order = sorted(present, key=lambda f: (math.isnan(stat_min[f]), stat_min[f]))
    census = rr.decoration_census(rows)
    sites_per_dec = [v["n_sites"] for e in census.values() for v in e["seeds"].values()]
    n_per_dec = args.n_sites_per_decoration or (int(np.bincount(sites_per_dec).argmax()) if sites_per_dec else 0)
    rules = [r.strip() for r in args.rules.split(",") if r.strip()]
    for rule in rules:
        if rule not in rr.RULES:
            raise SystemExit(f"unknown rule {rule!r}; choose from {rr.RULES}")
    statistics = OrderedDict((rule, rr.composition_statistic(rows, rule)) for rule in rules)
    # reproduction check (docs/91 (a) bar): census min over EVERY site of the banked seeds (cus eta,
    # regardless of admission) against the banked eta.  The minimum decreases with the number of
    # sites drawn, so the extra decorations of the second wave never enter this comparison.
    banked_seeds = set(int(s) for s in box["seeds"]) if box is not None and box.get("seeds") else None
    reproduction = OrderedDict()
    for f in present:
        etas = [r["eta_cus"] for r in rows if r["formula"] == f and (banked_seeds is None or r["seed"] in banked_seeds)]
        cmin = min(etas) if etas else None
        bank = box_rows.get(f)
        if bank is None or cmin is None:
            reproduction[f] = OrderedDict(census_min_V=cmin, banked_eta_V=None, difference_V=None, verdict="-",
                                          seeds=(sorted(banked_seeds) if banked_seeds else None), n_sites=len(etas))
        else:
            diff = cmin - float(bank["eta"])
            reproduction[f] = OrderedDict(census_min_V=cmin, banked_eta_V=float(bank["eta"]), difference_V=diff,
                                          abs_difference_V=abs(diff), tolerance_V=REPRODUCTION_ETA_TOL_V,
                                          seeds=(sorted(banked_seeds) if banked_seeds else None), n_sites=len(etas),
                                          verdict="REPRODUCED" if abs(diff) <= REPRODUCTION_ETA_TOL_V else "NOT REPRODUCED")
    # census order per rule and Kendall tau-a against the banked order
    census_orders = OrderedDict()
    for rule in rules:
        vals = statistics[rule]
        ranked = [f for f in present if math.isfinite(vals[f])]
        ranked = sorted(ranked, key=vals.__getitem__)
        excluded = [f for f in present if f not in ranked]
        banked_sub = [f for f in order if f in ranked]
        census_orders[rule] = OrderedDict(order=ranked, excluded=excluded,
                                          kendall_tau_a_vs_banked=(rr.kendall_tau_a(ranked, banked_sub) if len(ranked) >= 2 else None),
                                          complete=(not excluded and box is not None))
    out = OrderedDict(schema=SCHEMA, status="pending",
                      settings=OrderedDict(B=args.B, seed=args.seed, rules=rules, admit=args.admit, level=args.level,
                                           target_prob=args.target_prob, min_decorations=args.min_decorations,
                                           cutoff_A=args.cutoff_A, ridge_alpha=args.alpha,
                                           n_sites_per_decoration=n_per_dec, stems=args.stems,
                                           admit_definition=POLICY_DEFINITIONS[args.admit],
                                           reproduction_tolerance_V=REPRODUCTION_ETA_TOL_V),
                      model=OrderedDict(filename=models["models"][0][0] if models["models"] else None,
                                        sha256_bytes=models["models"][0][1] if models["models"] else None),
                      n_site_rows=len(rows), compositions=present, banked_order=order,
                      missing_gated_compositions=missing_gated,
                      census=OrderedDict((f, OrderedDict(n_decorations=e["n_decorations"],
                                                         n_decorations_usable=e["n_decorations_usable"],
                                                         usable_seeds=e["usable_seeds"], n_sites=e["n_sites"],
                                                         n_admitted=e["n_admitted"],
                                                         declared_n_sites=next((r["declared_n_sites"] for r in rows if r["formula"] == f), None),
                                                         declared_n_decorations=next((r["declared_n_decorations"] for r in rows if r["formula"] == f), None),
                                                         bootstrap_support=rr.bootstrap_support(e["n_decorations_usable"]),
                                                         seeds=e["seeds"]))
                                         for f, e in census.items()),
                      statistics=statistics, reproduction=reproduction, census_orders=census_orders,
                      site_rows=[OrderedDict((k, r.get(k)) for k in ("formula", "seed", "site_index", "eta", "pls", "site_metal",
                                                                     "initial_binding_metal", "desorbed", "evidence_status",
                                                                     "all_states_intact", "all_states_adsorbate_intact", "pathway",
                                                                     "state_categories", "converged", "admitted")) for r in rows])
    deficient = rr.check_decorations(rows, args.min_decorations)
    out["deficient_compositions"] = [OrderedDict(formula=f, n_decorations_usable=n) for f, n in deficient]
    out["variance_components"] = rr.variance_components(rows)
    # ridge on local environments (needs retained slabs)
    slabs = slab_index(payloads)
    envs, env_rows, env_missing = [], [], []
    for r in rows:
        slab = slabs.get((r["formula"], r["seed"]))
        if slab is None or not r["site_xy_A"]:
            env_missing.append(f"{r['formula']}/seed={r['seed']}/site={r['site_index']}")
            continue
        envs.append(rr.local_environment_features(slab, r["site_xy_A"], args.cutoff_A,
                                                  center_index=r.get("initial_binding_metal_index")))
        env_rows.append(r)
    ridge = OrderedDict(n_sites_with_environment=len(env_rows), sites_without_slab=env_missing, fits=OrderedDict())
    if env_rows:
        X, names = rr.feature_matrix(env_rows, envs)
        for target in RIDGE_TARGETS:
            ridge["fits"][target] = rr.ridge_model(env_rows, X, alpha=args.alpha, target=target, feature_names=names)
        ridge["environments"] = [OrderedDict(formula=r["formula"], seed=r["seed"], site_index=r["site_index"],
                                             center_metal=e["center_metal"], center_index=e["center_index"],
                                             n_neighbours=e["n_neighbours"], counts=e["counts"])
                                 for r, e in zip(env_rows, envs)]
    out["ridge"] = ridge
    if deficient:
        out["status"] = "insufficient_decorations"
        out["message"] = ("insufficient decorations: " + ", ".join(f"{f} ({n})" for f, n in deficient)
                          + f"; no bootstrap interval, rank matrix or order probability is reported below "
                            f"{args.min_decorations} usable decorations per composition")
        return out
    # bootstrap per rule
    boots, intervals, rank_mats, adjacent = OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict()
    vc = out["variance_components"]
    for rule in rules:
        boot = rr.cluster_bootstrap(rows, args.B, args.seed, rule, minimum=args.min_decorations)
        boots[rule] = boot
        lo, hi = 100 * (1 - args.level) / 2, 100 * (1 + args.level) / 2
        intervals[rule] = OrderedDict((f, [float(v) for v in np.percentile(boot[f], [lo, hi])]) for f in boot)
        rm = rr.rank_probability_matrix(boot)
        formulas = rm["formulas"]
        stable = OrderedDict()
        for i, f in enumerate(formulas):
            k = order.index(f) if f in order else None
            p_banked = float(rm["rank_matrix"][i][k]) if k is not None and k < len(formulas) else None
            stable[f] = OrderedDict(banked_rank=(k + 1 if k is not None else None), p_banked_rank=p_banked,
                                    stable=bool(p_banked is not None and p_banked >= args.target_prob))
        rank_mats[rule] = OrderedDict(formulas=formulas, rank_matrix=rm["rank_matrix"], pairwise=rm["pairwise"],
                                      expected_rank=rm["expected_rank"], n_replicates=rm["n_replicates"],
                                      n_dropped=rm["n_dropped"], stable=stable)
        gaps = rr.adjacent_gap_resolvability(boot, order, level=args.level, point=statistics[rule])
        for g in gaps:
            sa, sb = vc[g["better"]]["site_sd_population"], vc[g["worse"]]["site_sd_population"]
            if g["gap_point_V"] > 0 and n_per_dec > 0:
                need = rr.decorations_needed((sa, sb), g["gap_point_V"], n_per_dec, rule, args.target_prob,
                                             rng_seed=args.seed)
            else:
                need = OrderedDict(statistic=rule, decorations_needed=None, saturated=False, order_reverses_at_depth=False,
                                   message="observed gap is not positive under this rule; the banked order is inverted here")
            g["decorations_needed"] = need
            g["verdict"] = verdict_label(g["gap_point_V"], g["p_order_preserved"], args.target_prob, need)
            g["resolved"] = bool(g["verdict"].startswith("RESOLVED"))
            g["inverted"] = g["verdict"] == "INVERTED"
            g["spread_decided"] = "SPREAD-DECIDED" in g["verdict"]
        adjacent[rule] = gaps
    out["bootstrap_intervals"] = intervals
    out["rank_probability"] = rank_mats
    out["adjacent_gaps"] = adjacent
    out["resolved_boundaries"] = OrderedDict((rule, sum(1 for g in adjacent[rule] if g["resolved"])) for rule in rules)
    out["inverted_boundaries"] = OrderedDict((rule, sum(1 for g in adjacent[rule] if g["inverted"])) for rule in rules)
    out["n_boundaries"] = max(0, len(order) - 1)
    out["status"] = "complete"
    return out


def banked_reference(box: dict, formulas: list[str] | None, n_per_dec: int, rules: list[str], target: float, seed: int) -> dict:
    """The banked adjacent pairs pushed through decorations_needed with the banked
    population site spreads: each rule on its own banked gap (``min`` on the eta
    gap, ``mean`` on the eta_mean gap; ``median``/``p10`` have no box estimate),
    and every rule on a hypothetical location shift equal to the banked min gap."""
    rows = [r for r in box["rows"] if formulas is None or r["formula"] in set(formulas)]
    rows = sorted(rows, key=lambda r: r["eta"])
    table = []
    for a, b in zip(rows[:-1], rows[1:]):
        gap_min = float(b["eta"]) - float(a["eta"])
        gap_mean = (float(b["eta_mean"]) - float(a["eta_mean"])) if ("eta_mean" in a and "eta_mean" in b) else None
        sig = (float(a["eta_std"]), float(b["eta_std"]))
        entry = OrderedDict(better=a["formula"], worse=b["formula"], gap_min_V=gap_min, gap_mean_V=gap_mean,
                            sigma_a=sig[0], sigma_b=sig[1], own_gap=OrderedDict(), hypothetical_min_gap=OrderedDict())
        for rule in rules:
            if rule == "min":
                gap, source = gap_min, "banked eta (min rule)"
            elif rule == "mean":
                gap, source = gap_mean, "banked eta_mean"
            else:
                gap, source = None, "no box estimate"
            if gap is None:
                entry["own_gap"][rule] = OrderedDict(gap_V=None, gap_source=source, decorations_needed=None,
                                                     message="no box estimate of this rule's gap")
            elif gap > 0:
                need = rr.decorations_needed(sig, gap, n_per_dec, rule, target, rng_seed=seed)
                need.update(gap_source=source)
                entry["own_gap"][rule] = need
            else:
                entry["own_gap"][rule] = OrderedDict(gap_V=gap, gap_source=source, decorations_needed=None, saturated=False,
                                                     message="INVERTED: the banked gap under this rule is not positive")
            entry["hypothetical_min_gap"][rule] = rr.decorations_needed(sig, gap_min, n_per_dec, rule, target, rng_seed=seed)
        table.append(entry)
    return OrderedDict(order=[r["formula"] for r in rows], n_sites_per_decoration=n_per_dec, target_prob=target, pairs=table)


# --------------------------------------------------------------------------- policy comparison
def compare_readouts(paths: list[Path], target: float) -> dict:
    """R6: align the adjacent-gap verdicts of several readouts of one census (different
    admission policies) and label every boundary whose verdict differs POLICY-DEPENDENT."""
    reads = []
    for path in paths:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        reads.append((data["settings"]["admit"], data, Path(path)))
    policies = [p for p, _, _ in reads]
    if len(set(policies)) != len(policies):
        raise SystemExit(f"--compare needs one readout per policy; got {policies}")
    rules = reads[0][1]["settings"]["rules"]
    boundaries = []
    for rule in rules:
        keys = OrderedDict()
        for policy, data, _ in reads:
            for g in (data.get("adjacent_gaps") or {}).get(rule, []):
                keys.setdefault((g["better"], g["worse"]), OrderedDict())[policy] = g
        for (a, b), per in keys.items():
            verdicts = OrderedDict((p, per[p]["verdict"] if p in per else "ABSENT") for p in policies)
            base = [v.split(" / ")[0] for v in verdicts.values()]
            boundaries.append(OrderedDict(better=a, worse=b, rule=rule, verdicts=verdicts,
                                          p_order=OrderedDict((p, per[p]["p_order_preserved"] if p in per else None) for p in policies),
                                          gap_V=OrderedDict((p, per[p]["gap_point_V"] if p in per else None) for p in policies),
                                          policy_dependent=len(set(base)) > 1))
    return OrderedDict(schema="rank-resolution-compare-v1", target_prob=target, policies=policies,
                       inputs=[OrderedDict(policy=p, path=str(x), sha256_lf=_lf_hash(x), status=d["status"]) for p, d, x in reads],
                       n_policy_dependent=sum(1 for b in boundaries if b["policy_dependent"]), boundaries=boundaries)


def render_compare(cmp: dict) -> str:
    lines = ["# Policy comparison (R6)", "", "policies: " + ", ".join(cmp["policies"]), ""]
    body = []
    for b in cmp["boundaries"]:
        body.append([f"{b['better']} < {b['worse']}", b["rule"]]
                    + [f"{b['verdicts'][p]} ({fmt(b['p_order'][p], 3)})" for p in cmp["policies"]]
                    + ["POLICY-DEPENDENT" if b["policy_dependent"] else "-"])
    lines.append(md_table(["pair", "rule"] + [f"{p}: verdict (P)" for p in cmp["policies"]] + ["R6"], body))
    lines.append(f"\npolicy-dependent boundaries: {cmp['n_policy_dependent']} of {len(cmp['boundaries'])}")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- markdown
def render(out: dict) -> str:
    lines = [f"# Rank resolution readout ({out['status']})", ""]
    lines.append(f"site rows {out['n_site_rows']}; compositions {len(out['compositions'])}; admit policy {out['settings']['admit']}; "
                 f"rules {', '.join(out['settings']['rules'])}; B {out['settings']['B']}; seed {out['settings']['seed']}; "
                 f"model {out['model']['filename']}")
    cov = out.get("coverage") or {}
    if cov:
        lines.append(("coverage: stems unverified (no MANIFESTS.sha256); " + f"{len(cov.get('present', []))} result files read"
                      if cov.get("unverified") else
                      f"coverage: {len(cov.get('present', []))} of {len(cov.get('expected', []))} expected stems"
                      + (f"; MISSING: {', '.join(cov['missing'])}" if cov.get("missing") else ""))
                     + (f"; refused: {len(cov.get('refused', []))}" if cov.get("refused") else ""))
    if out.get("message"):
        lines += ["", "**" + out["message"] + "**"]
    lines += ["", "## T1 Decoration census", ""]
    lines.append(md_table(["composition", "decorations (usable)", "sites (admitted)", "declared", "bootstrap support C(2D-1,D)"],
                          [[f, f"{e['n_decorations']} ({e['n_decorations_usable']})", f"{e['n_sites']} ({e['n_admitted']})",
                            f"{e['declared_n_decorations']} x {e['declared_n_sites']}", e["bootstrap_support"]]
                           for f, e in out["census"].items()]))
    rules = out["settings"]["rules"]
    lines += ["", "## T2 Composition statistic per rule" + (" with %.0f %% cluster-bootstrap interval" % (100 * out["settings"]["level"]) if "bootstrap_intervals" in out else "")
              + f"; reproduction of the banked eta at {out['settings']['reproduction_tolerance_V']:g} V", ""]
    body = []
    for k, f in enumerate(out["banked_order"]):
        rep = out["reproduction"].get(f, {})
        cells = [f, k + 1, fmt(rep.get("banked_eta_V"), 6), fmt(rep.get("abs_difference_V"), 10) if rep.get("abs_difference_V") is not None else "-", rep.get("verdict", "-")]
        for rule in rules:
            v = out["statistics"][rule].get(f)
            if "bootstrap_intervals" in out:
                lo, hi = out["bootstrap_intervals"][rule][f]
                cells.append(f"{fmt(v)} [{fmt(lo)}, {fmt(hi)}]")
            else:
                cells.append(fmt(v))
        body.append(cells)
    lines.append(md_table(["composition", "banked rank", "banked eta", "abs(census min - banked)", "reproduction"] + rules, body))
    lines += ["", "census order and Kendall tau-a against the banked order: "
              + "; ".join(f"{rule}: {' < '.join(o['order'])} (tau {fmt(o['kendall_tau_a_vs_banked'], 3)}"
                          + (f", excluded {', '.join(o['excluded'])}" if o["excluded"] else "") + ")"
                          for rule, o in out["census_orders"].items())]
    if "rank_probability" in out:
        for rule in rules:
            rm = out["rank_probability"][rule]
            K = len(rm["formulas"])
            lines += ["", f"## T3 Rank-probability matrix ({rule} rule; P(rank r), rank 1 best; STABLE when P(banked rank) >= {out['settings']['target_prob']})", ""]
            lines.append(md_table(["composition"] + [f"r{r + 1}" for r in range(K)] + ["E[rank]", "banked rank", "label"],
                                  [[f] + [fmt(float(p), 3) for p in rm["rank_matrix"][i]] + [fmt(float(rm["expected_rank"][i]) + 1, 2),
                                                                                             rm["stable"][f]["banked_rank"],
                                                                                             "STABLE" if rm["stable"][f]["stable"] else "-"]
                                   for i, f in enumerate(rm["formulas"])]))
    if "adjacent_gaps" in out:
        lines += ["", f"## T4 Adjacent gaps in the banked order (RESOLVED when P(order) >= {out['settings']['target_prob']}; INVERTED when the observed gap is not positive; SPREAD-DECIDED when P falls with depth)", ""]
        body = []
        for rule in rules:
            for g in out["adjacent_gaps"][rule]:
                body.append([f"{g['better']} < {g['worse']}", rule, fmt(g["gap_point_V"], 5), fmt(g["p_order_preserved"], 3),
                             f"[{fmt(g['gap_interval_V'][0], 4)}, {fmt(g['gap_interval_V'][1], 4)}]",
                             g["verdict"], need_cell(g["decorations_needed"])])
        lines.append(md_table(["pair", "rule", "gap (V)", "P(order)", "gap interval (V)", "verdict", "decorations needed [MC bracket]"], body))
        lines += ["", "resolved boundaries: " + ", ".join(f"{rule} {out['resolved_boundaries'][rule]} of {out['n_boundaries']}" for rule in rules)
                  + "; inverted: " + ", ".join(f"{rule} {out['inverted_boundaries'][rule]}" for rule in rules)]
    lines += ["", "## T5 Variance components (site eta; within/between decoration)", ""]
    lines.append(md_table(["composition", "sites", "decorations", "site sd (pop.)", "within sd", "between sd", "ICC", "status"],
                          [[f, e["n_sites"], e["n_decorations"], fmt(e["site_sd_population"]), fmt(e["within_sd"]),
                            fmt(e["between_sd"]), fmt(e["icc"], 3), e["status"]] for f, e in out["variance_components"].items()]))
    lines += ["", f"## T6 Ridge on nearest-neighbour cation counts (cutoff {out['settings']['cutoff_A']} A, alpha {out['settings']['ridge_alpha']})", ""]
    fits = out["ridge"]["fits"]
    lines.append(md_table(["target", "sites", "status", "R2 in-sample", "R2 LOO", "sigma in-sample", "sigma LOO"],
                          [[t, m["n_sites"], m["status"], fmt(m["r2_in_sample"], 3), fmt(m["r2_loo"], 3),
                            fmt(m["sigma_in_sample"]), fmt(m["sigma_loo"])] for t, m in fits.items()]
                          or [["-", out["ridge"]["n_sites_with_environment"], "no retained slab", "-", "-", "-", "-"]]))
    if out.get("banked_reference"):
        br = out["banked_reference"]
        lines += ["", f"## T7 Decorations needed for the banked adjacent gaps (banked eta_std pairs, {br['n_sites_per_decoration']} sites per decoration, target {br['target_prob']})", ""]
        body = []
        for pair in br["pairs"]:
            for rule in out["settings"]["rules"]:
                own, hyp = pair["own_gap"][rule], pair["hypothetical_min_gap"][rule]
                own_cell = ("INVERTED" if own.get("message", "").startswith("INVERTED") else
                            ("no box estimate" if own.get("gap_V") is None else need_cell(own)))
                gumbel = (fmt(hyp.get("log10_n_sites_asymptotic"), 1) if rule == "min" and hyp.get("equal_spreads") else "-")
                body.append([f"{pair['better']} < {pair['worse']}", f"{fmt(pair['sigma_a'])}/{fmt(pair['sigma_b'])}", rule,
                             fmt(own.get("gap_V"), 5) if own.get("gap_V") is not None else "-", own_cell,
                             fmt(own.get("achieved_prob"), 3) if own.get("achieved_prob") is not None else "-",
                             need_cell(hyp), fmt(hyp.get("achieved_prob"), 3) if hyp.get("achieved_prob") is not None else "-", gumbel])
        lines.append(md_table(["pair", "sigma a/b", "rule", "own banked gap (V)", "decorations on own gap [MC bracket]", "P at that depth",
                               "decorations at the banked min gap (hypothetical shift)", "P", "log10 N Gumbel (sa = sb only)"], body))
        lines += ["", f"hypothetical shift = the banked min gap {', '.join(fmt(p['gap_min_V'], 6) for p in br['pairs'])} V applied to every rule; "
                      "own gap = min: banked eta, mean: banked eta_mean, median/p10: no box estimate."]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- main
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", default=None, help="census results directory or glob of screen-diagnostic-v1 result JSONs")
    p.add_argument("--stems", default=DEFAULT_STEMS, help="comma-separated fnmatch patterns on the result stem (default: the MACE-MPA-0 P-CENSUS-1 and P-CENSUS-3 stems)")
    p.add_argument("--manifests", type=Path, default=None, help="manifest directory (default: <results>/../manifests)")
    p.add_argument("--manifest-hashes", type=Path, default=None, help="MANIFESTS.sha256 (default: <results>/../MANIFESTS.sha256)")
    p.add_argument("--partial", action="store_true", help="read what has landed even if expected stems are missing")
    p.add_argument("--gated", type=Path, default=None, help="r4_gated.json; restricts the readout to its formulas")
    p.add_argument("--box", type=Path, default=DEFAULT_BOX if DEFAULT_BOX.exists() else None,
                   help="r4_screen_box.json for the banked order, eta, eta_mean and eta_std (default: the tracked 2026-09-06 snapshot)")
    p.add_argument("--B", type=int, default=10000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--rules", default=",".join(rr.RULES))
    p.add_argument("--admit", choices=ADMIT_POLICIES, default="all",
                   help="all = banked rule (every site); no-desorbed; intact / adsorbate-intact / two-pathway = the docs/91 (c) site sets of hea_oer.site_integrity")
    p.add_argument("--level", type=float, default=0.90)
    p.add_argument("--target-prob", type=float, default=0.95)
    p.add_argument("--min-decorations", type=int, default=rr.MIN_DECORATIONS)
    p.add_argument("--n-sites-per-decoration", type=int, default=None, help="default: modal count in the census")
    p.add_argument("--cutoff-A", type=float, default=3.8)
    p.add_argument("--alpha", type=float, default=1.0)
    p.add_argument("--compare", nargs="+", type=Path, default=None, help="readout JSONs of the same census under different --admit policies (R6)")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = p.parse_args(argv)

    if args.compare:
        cmp = compare_readouts(args.compare, args.target_prob)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(_clean(cmp), fh, indent=1, allow_nan=False)
            fh.write("\n")
        sys.stdout.write(render_compare(cmp))
        sys.stdout.write(f"\nwritten: {args.out}\n")
        return 0
    if args.results is None:
        p.error("--results is required unless --compare is given")
    results_path = Path(args.results)
    base = results_path if results_path.is_dir() else results_path.parent
    manifest_dir = args.manifests if args.manifests is not None else (base.parent / "manifests" if (base.parent / "manifests").is_dir() else None)
    hash_path = args.manifest_hashes if args.manifest_hashes is not None else (base.parent / "MANIFESTS.sha256")
    hashes = read_manifest_hashes(hash_path)
    gated_formulas = None
    if args.gated is not None:
        gated_formulas = [r["formula"] for r in json.loads(args.gated.read_text(encoding="utf-8"))["rows"]]
    stems = [s.strip() for s in args.stems.split(",") if s.strip()]
    sel = collect_results(args.results, stems, manifest_dir, hashes, gated_formulas)
    if not sel["payloads"]:
        print(f"no usable result JSON under {args.results} for stems {stems}; skipped: {sel['skipped']}; refused: {sel['refused']}",
              file=sys.stderr)
        return 2
    if sel["missing"] and not args.partial:
        print("census incomplete for the selected stems; rerun with --partial to read what exists: "
              + ", ".join(sel["missing"]), file=sys.stderr)
        return 2
    box = None
    if args.box is not None and Path(args.box).exists():
        box = json.loads(Path(args.box).read_text(encoding="utf-8"))
    try:
        out = build_readout(sel["payloads"], args, box, gated_formulas)
    except rr.MixedModelError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    out["coverage"] = OrderedDict(manifest_hashes=(str(hash_path) if hashes is not None else None),
                                  manifest_dir=(str(manifest_dir) if manifest_dir is not None else None),
                                  expected=sel["expected"], present=sel["present"], missing=sel["missing"],
                                  refused=sel["refused"], unverified=sel["unverified"], partial=bool(sel["missing"]))
    if sel["missing"] and out["status"] == "complete":
        out["status"] = "partial"
    # the banked screen's own depth (top-level n_sites per decoration) is the reference depth
    n_per_dec = (int(box["n_sites"]) if box is not None and box.get("n_sites") else out["settings"]["n_sites_per_decoration"])
    if box is not None and n_per_dec > 0:
        out["banked_reference"] = banked_reference(box, gated_formulas or out["compositions"], n_per_dec,
                                                   out["settings"]["rules"], args.target_prob, args.seed)
    out["inputs"] = OrderedDict(results=[OrderedDict(path=str(x), sha256_lf=_lf_hash(x)) for x in sel["paths"]],
                                skipped=sel["skipped"],
                                gated=(OrderedDict(path=str(args.gated), sha256_lf=_lf_hash(args.gated)) if gated_formulas is not None else None),
                                box=(OrderedDict(path=str(args.box), sha256_lf=_lf_hash(Path(args.box))) if box is not None else None))
    out["implementation_sha256_lf"] = OrderedDict((name, _lf_hash(ROOT / name)) for name in
                                                  ("src/hea_oer/rank_resolution.py", "src/scripts/rank_resolution_readout.py"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(_clean(out), fh, indent=1, allow_nan=False)
        fh.write("\n")
    sys.stdout.write(render(out))
    sys.stdout.write(f"\nwritten: {args.out}\n")
    return 3 if out["status"] == "insufficient_decorations" else 0


if __name__ == "__main__":
    sys.exit(main())
