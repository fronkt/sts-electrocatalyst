"""Candidate S8 ranking statistics over the completed site census (zero compute).

Reads ``results/site_census_2026-09-06/readout_full/per_site.csv`` and, for the
six fully sampled compositions (30 decorations x 4 sites, MACE-MPA-0), reports
the composition order under several summary statistics of the per-site
overpotential, under three admission policies, with a decoration-level
bootstrap for the stability of each order.  Cross-model leaders use the twelve
CENSUS-1 sites shared by all four models.  No value in the census is changed.

Usage:
    python src/scripts/s8_ranking_statistics.py --out results/s8_ranking_statistic_2026-09-19
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

CENSUS = Path("results/site_census_2026-09-06/readout_full/per_site.csv")
PRIMARY = "mpa0"
MODELS = ["mpa0", "omat0", "mp0", "matpes"]
POLICIES = {
    "all": lambda r: True,
    "adsorbate_intact": lambda r: r["all_states_adsorbate_intact"] == "True",
    "intact": lambda r: r["all_states_intact"] == "True",
}
STATS = {
    "min": lambda x: float(np.min(x)),
    "p10": lambda x: float(np.percentile(x, 10)),
    "p25": lambda x: float(np.percentile(x, 25)),
    "median": lambda x: float(np.median(x)),
    "mean": lambda x: float(np.mean(x)),
    "share_below_0.6V": lambda x: float(np.mean(x < 0.6)),
}
LOWER_IS_BETTER = {"min": True, "p10": True, "p25": True, "median": True, "mean": True, "share_below_0.6V": False}
BOOT = 10000
SEED = 0


def kendall_tau_a(order_a: list, order_b: list) -> float | None:
    common = [x for x in order_a if x in order_b]
    if len(common) < 2:
        return None
    ra = {x: i for i, x in enumerate([x for x in order_a if x in common])}
    rb = {x: i for i, x in enumerate([x for x in order_b if x in common])}
    c = d = 0
    for i in range(len(common)):
        for j in range(i + 1, len(common)):
            a, b = common[i], common[j]
            s = (ra[a] - ra[b]) * (rb[a] - rb[b])
            c += s > 0
            d += s < 0
    return (c - d) / (len(common) * (len(common) - 1) / 2)


def order_by(values: dict, stat: str) -> list:
    items = [(f, v) for f, v in values.items() if v is not None]
    return [f for f, _ in sorted(items, key=lambda t: t[1], reverse=not LOWER_IS_BETTER[stat])]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(CENSUS.open(encoding="utf-8")))
    counts = defaultdict(int)
    for r in rows:
        if r["tag"] == PRIMARY:
            counts[r["formula"]] += 1
    six = sorted(f for f, c in counts.items() if c == 120)
    banked_order = ["Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25", "Cu26Ni9Cr31Co33", "Ni34Fe6Cu29Co31",
                    "Cu8Cr23Mn35Co34", "Cu22Fe30Co32Mn15"]
    # site table: model -> formula -> decoration(seed) -> list of rows
    table = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for r in rows:
        if r["formula"] in six and r["tag"] in MODELS:
            table[r["tag"]][r["formula"]][int(r["seed"])].append(r)

    result = {"source": str(CENSUS), "source_sha256": hashlib.sha256(CENSUS.read_bytes()).hexdigest(),
              "compositions": six, "banked_order": banked_order, "bootstrap": {"B": BOOT, "seed": SEED, "unit": "decoration (seed)"},
              "policies": {}, "cross_model": {}}
    rng = np.random.default_rng(SEED)
    for pname, admit in POLICIES.items():
        block = {"n_sites": {}, "statistics": {}, "orders": {}, "tau_a_vs_banked": {}, "tau_a_between": {},
                 "bootstrap_p_rank1": {}, "bootstrap_p_rank_le2": {}}
        per_dec = {}
        for f in six:
            decs = table[PRIMARY][f]
            per_dec[f] = {s: np.array([float(r["eta_V"]) for r in decs[s] if admit(r)]) for s in sorted(decs)}
            allv = np.concatenate(list(per_dec[f].values())) if per_dec[f] else np.array([])
            block["n_sites"][f] = int(allv.size)
            block["statistics"][f] = {k: (fn(allv) if allv.size else None) for k, fn in STATS.items()}
        for k in STATS:
            block["orders"][k] = order_by({f: block["statistics"][f][k] for f in six}, k)
            block["tau_a_vs_banked"][k] = kendall_tau_a(block["orders"][k], banked_order)
        for k in STATS:
            block["tau_a_between"][k] = {k2: kendall_tau_a(block["orders"][k], block["orders"][k2]) for k2 in STATS}
        # decoration bootstrap
        seeds = {f: sorted(per_dec[f]) for f in six}
        wins1 = {k: defaultdict(int) for k in STATS}
        wins2 = {k: defaultdict(int) for k in STATS}
        valid = {k: 0 for k in STATS}
        for _ in range(BOOT):
            sample = {}
            for f in six:
                pick = rng.choice(seeds[f], size=len(seeds[f]), replace=True)
                vals = np.concatenate([per_dec[f][s] for s in pick]) if len(pick) else np.array([])
                sample[f] = vals
            for k, fn in STATS.items():
                vals = {f: (fn(sample[f]) if sample[f].size else None) for f in six}
                order = order_by(vals, k)
                if not order:
                    continue
                valid[k] += 1
                wins1[k][order[0]] += 1
                for f in order[:2]:
                    wins2[k][f] += 1
        for k in STATS:
            block["bootstrap_p_rank1"][k] = {f: (wins1[k][f] / valid[k] if valid[k] else None) for f in six}
            block["bootstrap_p_rank_le2"][k] = {f: (wins2[k][f] / valid[k] if valid[k] else None) for f in six}
        result["policies"][pname] = block

    # cross-model on the shared twelve CENSUS-1 sites (seeds 0-2), policy 'all' and 'adsorbate_intact'
    for pname in ("all", "adsorbate_intact"):
        admit = POLICIES[pname]
        cm = {"leaders": {}, "orders": {}, "n_sites": {}}
        for m in MODELS:
            vals = {}
            n = {}
            for f in six:
                v = np.array([float(r["eta_V"]) for s in (0, 1, 2) for r in table[m][f].get(s, []) if admit(r)])
                n[f] = int(v.size)
                vals[f] = {k: (fn(v) if v.size else None) for k, fn in STATS.items()}
            cm["n_sites"][m] = n
            cm["orders"][m] = {k: order_by({f: vals[f][k] for f in six}, k) for k in STATS}
            cm["leaders"][m] = {k: (cm["orders"][m][k][0] if cm["orders"][m][k] else None) for k in STATS}
        cm["leader_agreement"] = {k: len(set(cm["leaders"][m][k] for m in MODELS)) for k in STATS}
        result["cross_model"][pname] = cm

    (out / "ranking_statistics.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    # compact markdown
    lines = ["# Candidate ranking statistics over the census (MACE-MPA-0, 120 sites per composition)", ""]
    for pname, block in result["policies"].items():
        lines += [f"## Policy: {pname}", "", "| composition | n | min | p10 | p25 | median | mean | share<0.6 V |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for f in six:
            s = block["statistics"][f]
            fmt = lambda v: "-" if v is None else f"{v:.3f}"
            lines.append(f"| {f} | {block['n_sites'][f]} | " + " | ".join(fmt(s[k]) for k in STATS) + " |")
        lines += ["", "| statistic | order (best first) | tau-a vs banked | P(rank 1) leader | P(rank<=2) top two |", "|---|---|---:|---|---|"]
        for k in STATS:
            o = block["orders"][k]
            p1 = block["bootstrap_p_rank1"][k]
            p2 = block["bootstrap_p_rank_le2"][k]
            lead = max(p1, key=lambda f: (p1[f] or 0))
            top2 = sorted(p2, key=lambda f: -(p2[f] or 0))[:2]
            tau = block["tau_a_vs_banked"][k]
            lines.append(f"| {k} | {' < '.join(o)} | {'-' if tau is None else f'{tau:.2f}'} | {lead} {p1[lead]:.2f} | " + ", ".join(f"{f} {p2[f]:.2f}" for f in top2) + " |")
        lines.append("")
    for pname, cm in result["cross_model"].items():
        lines += [f"## Cross-model leaders on the shared twelve sites, policy {pname}", "", "| statistic | " + " | ".join(MODELS) + " | distinct leaders |", "|---|" + "---|" * (len(MODELS) + 1)]
        for k in STATS:
            lines.append(f"| {k} | " + " | ".join(str(cm['leaders'][m][k]) for m in MODELS) + f" | {cm['leader_agreement'][k]} |")
        lines.append("")
    (out / "ranking_statistics.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
