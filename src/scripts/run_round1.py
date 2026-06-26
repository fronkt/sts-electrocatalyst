#!/usr/bin/env python
"""Round-1 HEA OER candidate selector — CLI.

Usage (no install needed):
    PYTHONPATH=src python src/scripts/run_round1.py --top-k 4 --seed 0

Prints the top-ranked candidates + the diverse shortlist to melt, writes
results/round1_candidates.csv, and a volcano/Pareto plot (results/round1_volcano.png).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# allow `python src/scripts/run_round1.py` without installing the package
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from hea_oer import run_round1  # noqa: E402
from hea_oer.descriptors import overpotential_from_descriptor  # noqa: E402

DISPLAY_COLS = [
    "rank", "formula", "eta_V", "descriptor", "formability", "single_phase",
    "phase", "abundance", "cost_usd_kg", "score", "backend",
]


def main() -> None:
    p = argparse.ArgumentParser(description="HEA OER round-1 candidate selector")
    p.add_argument("--elements", nargs="+", default=None, help="design element set")
    p.add_argument("--n-samples", type=int, default=4000)
    p.add_argument("--top-k", type=int, default=4)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--backend", default="heuristic", choices=["heuristic", "oc22"])
    p.add_argument("--formability-min", type=float, default=0.5)
    p.add_argument("--out", default=None, help="output dir (default STS2027/results)")
    p.add_argument("--no-plot", action="store_true")
    args = p.parse_args()

    kw = dict(
        n_samples=args.n_samples, top_k=args.top_k, seed=args.seed,
        backend=args.backend, formability_min=args.formability_min,
    )
    if args.elements:
        kw["elements"] = tuple(args.elements)
    res = run_round1(**kw)

    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", None)
    fmt = lambda v: f"{v:.3f}"  # noqa: E731
    print(f"\n# Round-1 selector | backend={res.backend} | candidates={res.n_candidates}")
    print(f"# formable (single-phase) candidates: {int(res.table['formable'].sum())}")
    print("\n## Top 15 by score")
    print(res.table[DISPLAY_COLS].head(15).to_string(index=False, float_format=fmt))
    print(f"\n## Shortlist to melt (diverse top-{args.top_k})")
    print(res.shortlist[DISPLAY_COLS].to_string(index=False, float_format=fmt))

    out_dir = Path(args.out) if args.out else (ROOT / "results")
    out_dir.mkdir(parents=True, exist_ok=True)
    export = res.table.drop(columns=[c for c in res.table.columns if c.startswith("_")])
    csv = out_dir / "round1_candidates.csv"
    export.to_csv(csv, index=False)
    print(f"\n[written] {csv}")

    if not args.no_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            t = res.table
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.scatter(t.loc[~t.formable, "descriptor"], t.loc[~t.formable, "eta_V"],
                       s=8, c="lightgray", label="not single-phase")
            ax.scatter(t.loc[t.formable, "descriptor"], t.loc[t.formable, "eta_V"],
                       s=10, c="steelblue", label="single-phase")
            ax.scatter(res.shortlist["descriptor"], res.shortlist["eta_V"],
                       s=140, marker="*", c="crimson", edgecolor="k", zorder=5,
                       label="shortlist to melt")
            xs = np.linspace(0.5, 2.7, 200)
            ax.plot(xs, [overpotential_from_descriptor(x) for x in xs], "k--", lw=1,
                    label="scaling-limit volcano")
            ax.set_xlabel(r"descriptor  $\Delta G_O-\Delta G_{OH}$  (eV)")
            ax.set_ylabel(r"theoretical OER overpotential  $\eta$  (V)")
            ax.set_title("HEA OER round-1 (heuristic prior — PLACEHOLDER for OC22)")
            ax.legend(fontsize=8)
            fig.tight_layout()
            png = out_dir / "round1_volcano.png"
            fig.savefig(png, dpi=130)
            print(f"[written] {png}")
        except Exception as e:  # pragma: no cover - plotting is best-effort
            print(f"[plot skipped] {e}")


if __name__ == "__main__":
    main()
