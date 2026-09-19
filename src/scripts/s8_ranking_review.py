"""Bounded independent diagnostics of the completed S8 census; no new gates.

No model evaluations, bootstrap reruns, melt choices, or adoption decisions.
The source CSV and original ranking outputs remain unchanged.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform

COMPOSITIONS = (
    "Cu22Fe30Co32Mn15", "Cu26Ni9Cr31Co33", "Cu8Cr23Mn35Co34",
    "Fe25Co25Ni25Cr25", "Ni31Cr29Cu5Mn35", "Ni34Fe6Cu29Co31",
)
POLICIES = {"all": None, "adsorbate_intact": "all_states_adsorbate_intact", "intact": "all_states_intact"}
SOURCE = Path("results/site_census_2026-09-06/readout_full/per_site.csv")
ORIGINAL = Path("results/s8_ranking_statistic_2026-09-19/ranking_statistics.json")


def quantile_support(rows: list[dict], q: float = 0.10) -> dict:
    """Independent NumPy method='linear' convention: h=(n-1)*q, zero-based.

    Record all sites at either bracketing value so an arbitrary within-tie
    ordering cannot imply that just one site supports the quantile.
    """
    if not 0 <= q <= 1:
        raise ValueError("q must be in [0,1]")
    if not rows:
        return {"value_V": None, "n": 0, "status": "UNDEFINED_EMPTY", "q": q}
    ordered = sorted(rows, key=lambda r: r["eta_V"])
    h = (len(ordered) - 1) * q
    lo, hi = math.floor(h), math.ceil(h)
    weight = h - lo
    low, high = ordered[lo]["eta_V"], ordered[hi]["eta_V"]
    def sites_at(value):
        return [{"seed": r["seed"], "site_index": r["site_index"], "eta_V": r["eta_V"]}
                for r in ordered if r["eta_V"] == value]
    return {"value_V": low + weight * (high - low), "n": len(ordered), "status": "DEFINED",
            "q": q, "method": "linear; h=(n-1)*q, zero-based",
            "index0_float": h, "lower_order_1based": lo + 1, "upper_order_1based": hi + 1,
            "lower_value_V": low, "upper_value_V": high, "weight_upper": weight,
            "sites_at_lower_value": sites_at(low), "sites_at_upper_value": sites_at(high)}


def tie_ranks(values: dict[str, float | None], lower_is_better: bool = True) -> dict:
    """Rank intervals among defined values, raw tie groups, explicit omissions.

    Exact numeric ties are retained. There is no tolerance-based scientific
    equivalence threshold and no alphabetical winner inside a tied group.
    """
    defined = {name: value for name, value in values.items() if value is not None}
    if any(not math.isfinite(value) for value in defined.values()):
        raise ValueError("rank values must be finite or None")
    groups = {}
    for name, value in defined.items():
        groups.setdefault(value, []).append(name)
    ordered = sorted(groups, reverse=not lower_is_better)
    ranks, ties = {}, []
    before = 0
    for value in ordered:
        names = sorted(groups[value])  # display only, never a ranking within ties
        group = {"value": value, "members": names, "rank_best": before + 1,
                 "rank_worst": before + len(names)}
        for name in names:
            ranks[name] = {"rank_best": group["rank_best"], "rank_worst": group["rank_worst"],
                           "tie_size": len(names)}
        if len(names) > 1:
            ties.append(group)
        before += len(names)
    undefined = sorted(set(values) - set(defined))
    for name in undefined:
        ranks[name] = {"rank_best": None, "rank_worst": None, "tie_size": None}
    return {"ranks": ranks, "raw_ties": ties, "undefined_compositions": undefined,
            "n_defined": len(defined), "n_requested": len(values),
            "all_compositions_defined": len(defined) == len(values),
            "ranking_population": "defined compositions only; missing values are not assigned last place"}


def empty_probability(nonempty: int, total: int, draws: int | None = None) -> float:
    """Probability every uniform decoration-bootstrap draw has zero retained sites."""
    if total <= 0 or not 0 <= nonempty <= total:
        raise ValueError("invalid decoration counts")
    draws = total if draws is None else draws
    if draws <= 0:
        raise ValueError("draws must be positive")
    return ((total - nonempty) / total) ** draws


def load_rows(path: Path) -> dict[str, list[dict]]:
    table = {formula: [] for formula in COMPOSITIONS}
    with path.open(encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            if raw["tag"] != "mpa0" or raw["formula"] not in table:
                continue
            row = {"seed": int(raw["seed"]), "site_index": int(raw["site_index"]),
                   "eta_V": float(raw["eta_V"])}
            if not math.isfinite(row["eta_V"]):
                raise ValueError("nonfinite descriptor")
            for field in ("all_states_adsorbate_intact", "all_states_intact"):
                if raw[field] not in ("True", "False"):
                    raise ValueError(f"invalid admission flag: {field}")
                row[field] = raw[field] == "True"
            table[raw["formula"]].append(row)
    expected = {(seed, site) for seed in range(30) for site in range(4)}
    for formula, rows in table.items():
        ids = [(r["seed"], r["site_index"]) for r in rows]
        if len(ids) != 120 or len(set(ids)) != 120 or set(ids) != expected:
            raise ValueError(f"{formula}: expected exactly 30 decorations x 4 unique sites")
    return table


def diagnostics(table: dict[str, list[dict]]) -> dict:
    result = {"policies": {}, "leave_one_decoration_out": []}
    for policy, flag in POLICIES.items():
        block = {"compositions": {}}
        p10_values, conditional_shares, admitted_shares = {}, {}, {}
        for formula, rows in table.items():
            seeds = sorted({r["seed"] for r in rows})
            keep = [r for r in rows if flag is None or r[flag]]
            per_dec = {str(seed): sum(r["seed"] == seed for r in keep) for seed in seeds}
            nonempty = sum(n > 0 for n in per_dec.values())
            below = sum(r["eta_V"] < 0.6 for r in keep)
            support = quantile_support(keep)
            conditional = below / len(keep) if keep else None
            unconditional = below / len(rows)
            block["compositions"][formula] = {
                "n_sampled_sites": len(rows), "n_sampled_decorations": len(seeds),
                "n_retained_sites": len(keep), "n_nonempty_decorations": nonempty,
                "retained_counts_by_decoration": per_dec,
                "empty_bootstrap_probability": empty_probability(nonempty, len(seeds)),
                "empty_probability_condition": "uniform iid draws of the observed decoration clusters, original draw count",
                "n_admitted_eta_below_0_6V": below,
                "admitted_eta_below_0_6V_over_sampled": unconditional,
                "admitted_eta_below_0_6V_over_retained": conditional,
                "p10": support,
            }
            p10_values[formula] = support["value_V"]
            conditional_shares[formula], admitted_shares[formula] = conditional, unconditional
        block["p10_ranks"] = tie_ranks(p10_values)
        block["conditional_share_ranks"] = tie_ranks(conditional_shares, lower_is_better=False)
        block["admitted_share_over_120_ranks"] = tie_ranks(admitted_shares, lower_is_better=False)
        result["policies"][policy] = block
    # Omit each cluster in one composition at a time; other compositions stay fixed.
    # Numeric seed labels across different compositions are not assumed paired units.
    flag = POLICIES["adsorbate_intact"]
    baseline = {f: result["policies"]["adsorbate_intact"]["compositions"][f]["p10"]["value_V"] for f in table}
    for formula, rows in table.items():
        for seed in sorted({r["seed"] for r in rows}):
            retained = [r for r in rows if r["seed"] != seed and r[flag]]
            support = quantile_support(retained)
            values = dict(baseline)
            values[formula] = support["value_V"]
            result["leave_one_decoration_out"].append({
                "omitted_composition": formula, "omitted_seed": seed,
                "omitted_retained_sites": sum(r["seed"] == seed and r[flag] for r in rows),
                "n_remaining_sampled_sites": sum(r["seed"] != seed for r in rows),
                "n_remaining_retained_sites": len(retained), "p10": support,
                "all_composition_p10_V": values, "ranking": tie_ranks(values),
            })
    result["leave_one_decoration_out_scope"] = (
        "Adsorbate-intact p10; omit one whole decoration in one composition at a time, "
        "holding all other compositions fixed. This is empirical influence analysis, "
        "not a confidence interval, matched-composition design or new decision gate.")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--original", type=Path, default=ORIGINAL)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = diagnostics(load_rows(args.source))
    original = json.loads(args.original.read_text(encoding="utf-8"))
    comparisons = []
    for policy, block in result["policies"].items():
        for formula, row in block["compositions"].items():
            reference = original["policies"][policy]["statistics"][formula]["p10"]
            actual = row["p10"]["value_V"]
            if (reference is None) != (actual is None):
                raise ValueError("quantile definedness mismatch")
            difference = None if actual is None else actual - reference
            if difference is not None and abs(difference) > 1e-12:
                raise ValueError(f"p10 mismatch: {policy}/{formula}")
            comparisons.append({"policy": policy, "formula": formula, "delta_V": difference})
    result["original_p10_checks"] = comparisons
    result["scope"] = {
        "status": "DESCRIPTIVE_INDEPENDENT_DIAGNOSTICS_NO_ADOPTION",
        "model": "MACE-MPA-0", "compositions": list(COMPOSITIONS), "python": platform.python_version(),
        "quantile": "Independent implementation of NumPy method='linear'; 18 existing p10 values cross-checked",
        "limitations": ["Conditioned on observed decorations and model-specific integrity classifications",
                        "No model-error, unseen-site or experimental uncertainty estimate",
                        "Admitted low-descriptor fraction is not a measured active-site fraction",
                        "No bootstrap rerun, numeric gate, composition choice or physical-performance prediction"],
    }
    result["inputs"] = [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for path in (args.source, args.original, Path(__file__))]
    if original["source_sha256"] != result["inputs"][0]["sha256"]:
        raise ValueError("original ranking and review CSV hashes differ")
    args.out.mkdir(parents=True, exist_ok=True)
    dest = args.out / "diagnostics.json"
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if dest.exists():
        raise FileExistsError(f"Preserve existing review evidence: {dest}")
    dest.write_text(payload, encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(dest), "policies": len(POLICIES),
                      "compositions": len(COMPOSITIONS), "original_p10_checks": len(comparisons),
                      "leave_one_out_cases": len(result["leave_one_decoration_out"])}))


if __name__ == "__main__":
    main()
