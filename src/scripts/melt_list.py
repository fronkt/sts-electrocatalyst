"""Assemble the frozen melt list from a validated screen + the stability gate.

Supersedes the docs/15 s1 melt set, whose activity ranking R0 voided (no out-of-box
UMA head ranks rutile OER; docs/29 s8).

Why this is not a scalarization
-------------------------------
The obvious move is to weight activity, stability, cost and abundance into one score
and take the top 6. That would be wrong here, for a reason the data forced:

    **Every candidate measured so far is at least 33% soluble at operating
    conditions.** (docs/15's own set runs 33-72%; `pourbaix_multi.py melt-set`.)

There is no stable-and-active corner to find. A scalarization would quietly pick one
exchange rate between "dissolves less" and "binds better", bury it in a weight vector,
and report a single winner as if the trade-off had been resolved. It has not been --
and that unresolved trade-off is precisely the thesis this project exists to attack
(docs/12 §3b: whether high-entropy disorder can break the scaling relations that tie
activity to instability).

So the list is built to **span** the tension instead: the Pareto front over
(activity, stability) plus the two anchors an honest correlation study needs. The
experiment then measures where on that front the real materials land, which is a
result whichever way it comes out.

What each slot buys
-------------------
* **activity end** -- lowest predicted eta. The optimistic pick.
* **stability end** -- least soluble. The pick that might survive a 12 h hold.
* **interior front** -- the trade-off made visible.
* **poor anchor** -- highest predicted eta among single-phase candidates. docs/15 §6
  is right that a correlation over ~6 points is meaningless without dynamic range,
  and an anchor is the cheapest way to buy it.
* **FeCoNi ablation** -- drops the high-entropy aspect entirely. Without it, "the HEA
  helped" is not a testable claim. It is also, by the stability gate, the *least*
  soluble composition in the docs/15 set -- so it is a real contender, not a foil.

    PYTHONPATH=src python src/scripts/melt_list.py build \
        --gated results/r4_gated.json --out results/r4_melt_list.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hea_oer.composition import Composition  # noqa: E402
from hea_oer.data import COST_USD_PER_KG  # noqa: E402


def cost(elements, fractions) -> float:
    return float(sum(f * COST_USD_PER_KG[el] for el, f in zip(elements, fractions)))


def pareto_front(rows) -> list:
    """Non-dominated over (low eta, low soluble fraction). Both are 'minimize'."""
    front = []
    for r in rows:
        dominated = any(
            o is not r
            and o["eta"] <= r["eta"]
            and o["soluble_at_operating"] <= r["soluble_at_operating"]
            and (o["eta"] < r["eta"]
                 or o["soluble_at_operating"] < r["soluble_at_operating"])
            for o in rows)
        if not dominated:
            front.append(r)
    return sorted(front, key=lambda r: r["eta"])


def select(rows, k_interior: int = 2) -> list:
    """Span the activity/stability front, then add the two anchors."""
    usable = [r for r in rows
              if r.get("soluble_at_operating") is not None and not r.get("desorbed")]
    if not usable:
        return []
    front = pareto_front(usable)
    picks: list[tuple[str, dict]] = []

    def add(role: str, r: dict) -> None:
        """One composition may satisfy two roles. Say so rather than dropping the role.

        Silently omitting a collapsed role loses exactly the information the reader
        needs: if the poor anchor IS the stability end, the list has no independent
        low-activity point and the correlation study's dynamic range is whatever the
        front happens to span — a limitation, not a free lunch.
        """
        if r is None:
            return
        for i, (existing, p) in enumerate(picks):
            if p["formula"] == r["formula"]:
                if role not in existing.split(" + "):
                    picks[i] = (f"{existing} + {role}", p)
                return
        picks.append((role, r))

    add("activity end", front[0])
    add("stability end", min(front, key=lambda r: r["soluble_at_operating"]))
    # interior points, spread along the front by activity
    interior = [r for r in front if all(r["formula"] != p["formula"] for _, p in picks)]
    if interior and k_interior > 0:
        step = max(1, len(interior) // k_interior)
        for r in interior[::step][:k_interior]:
            add("interior front", r)
    add("poor anchor", max(usable, key=lambda r: r["eta"]))
    return picks


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="assemble the frozen melt list")
    b.add_argument("--gated", default="results/r4_gated.json",
                   help="output of pourbaix_multi.py gate (screen + stability)")
    b.add_argument("--interior", type=int, default=2)
    b.add_argument("--out", default="")
    a = ap.parse_args()

    if not os.path.exists(a.gated):
        print(f"no gated screen at {a.gated}; run screen_mace.py screen then "
              f"pourbaix_multi.py gate")
        raise SystemExit(2)
    rows = json.load(open(a.gated))["rows"]
    picks = select(rows, a.interior)
    if not picks:
        print("no candidate carries both an activity and a stability number")
        raise SystemExit(1)

    span = max(r["eta"] for _, r in picks) - min(r["eta"] for _, r in picks)
    print(f"{'role':<32}{'composition':<26}{'eta_pred':>9}{'soluble':>9}"
          f"{'$/kg':>8}{'sites':>7}")
    out = []
    for role, r in picks:
        c = cost(r["elements"], r["fractions"])
        print(f"{role:<32}{r['formula']:<26}{r['eta']:>9.3f}"
              f"{r['soluble_at_operating']*100:>8.1f}%{c:>8.2f}"
              f"{r.get('n_sites', 0):>7}")
        out.append(dict(role=role, formula=r["formula"], elements=r["elements"],
                        fractions=r["fractions"], eta_pred=r["eta"],
                        eta_spread=r.get("eta_std"), site_metals=r.get("site_metals"),
                        soluble_at_operating=r["soluble_at_operating"],
                        cost_usd_kg=c, n_sites_sampled=r.get("n_sites"),
                        n_decorations=r.get("n_decorations")))

    collapsed = [role for role, _ in picks if " + " in role]
    if collapsed:
        print(f"\n  ROLE COLLAPSE: {collapsed[0]}. One composition satisfies both, so the")
        print("  list has no INDEPENDENT low-activity point and its dynamic range is")
        print("  whatever the Pareto front happens to span.")
    print(f"\n  Predicted-eta span across the list: {span:.3f} V, against a validated")
    print("  screener MAE of 0.130 V (docs/36 s1). docs/15 s6 is right that a")
    print("  correlation over ~6 points needs dynamic range; judge whether this span")
    print("  buys enough before freezing, and widen the screened pool if not.")
    print("\n  FeCoNi (equiatomic) is melted alongside these as the ablation -- it")
    print("  drops the high-entropy aspect, and the stability gate makes it the least")
    print("  soluble composition in the docs/15 set (33.3%), so it is a contender too.")
    print("\n  eta_pred is an ORDERING. The pre-registered out-of-sample test in")
    print("  docs/34 missed eta(Co) by +0.339 V, 2.3x the validated bar, so no single")
    print("  number here is a prediction of a measured overpotential.")
    print("  soluble% is a BULK thermodynamic statement at 1e-6 M: what decomposes if")
    print("  it can, not how fast, and blind to a passivating surface (docs/31 §7).")

    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        json.dump(dict(source=a.gated, picks=out,
                       ablation=dict(formula="FeCoNi", elements=["Fe", "Co", "Ni"],
                                     fractions=[1 / 3, 1 / 3, 1 / 3],
                                     soluble_at_operating=0.333)),
                  open(a.out, "w"), indent=2)
        print(f"\n-> {a.out}")


if __name__ == "__main__":
    main()
