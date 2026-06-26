#!/usr/bin/env python
"""Two-stage round-1 with the real UMA surface backend.

Stage 1 (CPU, cheap): the heuristic + empirical phase-stability prior ranks a large
composition sample and keeps the top single-phase (meltable) candidates — the
documented "ML screening prior ranks where to look" (docs/12 §3).

Stage 2 (GPU): the fairchem UMA surface backend computes physically-grounded,
CHE-referenced ΔG(*OH/*O/*OOH) -> theoretical OER overpotential η on *only* that
small pool. This avoids spending ~6 UMA relaxations on every multi-phase
composition FWM could never melt single-phase.

It also reports how much the real model re-orders the cheap prior (Spearman ρ over
the shared pool) — a first ML-vs-ML calibration, and the template for the later
ML-vs-experiment correlation that is the project's contribution.

Usage on the GPU box:
    PYTHONPATH=src python src/scripts/run_round1_uma.py \
        --n-samples 3000 --pool 24 --top-k 4 --model uma-s-1p1 --task oc20

Local orchestration test (no GPU; heuristic stands in for stage 2):
    PYTHONPATH=src python src/scripts/run_round1_uma.py --backend heuristic --pool 12 --no-plot
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from hea_oer import run_round1  # noqa: E402
from hea_oer.adsorption import get_backend  # noqa: E402
from hea_oer.objective import build_table, rank, select_shortlist  # noqa: E402
from hea_oer.data import DEFAULT_ELEMENTS  # noqa: E402
from hea_oer.descriptors import overpotential_from_descriptor  # noqa: E402

DISPLAY_COLS = [
    "rank", "formula", "eta_V", "descriptor", "formability", "single_phase",
    "phase", "abundance", "cost_usd_kg", "score", "backend",
]


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation, scipy-free fallback."""
    if len(a) < 3:
        return float("nan")
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    ra = ra - ra.mean(); rb = rb - rb.mean()  # not in-place: pandas 3 returns read-only arrays
    denom = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / denom) if denom > 1e-12 else float("nan")


def _diverse_pick(formable: pd.DataFrame, n: int, elements) -> pd.DataFrame:
    """Greedy max-min diverse subset of single-phase candidates over composition
    space (seeded by highest formability), independent of the heuristic activity
    score — the unbiased pool for a backend whose ranking the heuristic can't predict.
    """
    df = formable.sort_values("formability", ascending=False).reset_index(drop=True)
    vecs = [c.vector(elements) for c in df["_comp"]]
    chosen = [0]
    while len(chosen) < min(n, len(df)):
        best_i, best_d = None, -1.0
        for i in range(len(df)):
            if i in chosen:
                continue
            d = min(float(np.linalg.norm(vecs[i] - vecs[c])) for c in chosen)
            if d > best_d:
                best_d, best_i = d, i
        chosen.append(best_i)
    return df.iloc[chosen]


def main() -> None:
    p = argparse.ArgumentParser(description="Two-stage (heuristic prior -> UMA) HEA OER round-1")
    p.add_argument("--elements", nargs="+", default=None, help="design element set")
    p.add_argument("--n-samples", type=int, default=3000, help="stage-1 heuristic sample size")
    p.add_argument("--pool", type=int, default=24, help="# single-phase candidates to send to UMA")
    p.add_argument("--select", default="score", choices=["score", "diverse"],
                   help="pool selection: 'score'=top heuristic score; 'diverse'=max-min "
                        "coverage of single-phase composition space (unbiased by heuristic activity)")
    p.add_argument("--top-k", type=int, default=4)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--backend", default="uma", choices=["uma", "oc22", "heuristic"],
                   help="stage-2 backend (heuristic only for local orchestration tests)")
    p.add_argument("--model", default="uma-s-1p1")
    p.add_argument("--task", default="oc20")
    p.add_argument("--device", default="cuda")
    p.add_argument("--surface", default="metal", choices=["metal", "oxide", "rutile"],
                   help="metal=fcc(111) proxy; oxide=rocksalt(100); rutile=MO2(110) multi-site (docs/13)")
    p.add_argument("--n-sites", type=int, default=4, help="cus sites sampled per composition (rutile)")
    p.add_argument("--size", type=int, nargs=3, default=None,
                   help="slab size (default: 3 3 4 metal, 2 2 4 oxide, 2 2 1 rutile supercell)")
    p.add_argument("--fmax", type=float, default=0.05)
    p.add_argument("--steps", type=int, default=300)
    p.add_argument("--formability-min", type=float, default=0.5)
    p.add_argument("--out", default=None)
    p.add_argument("--no-plot", action="store_true")
    args = p.parse_args()

    elements = tuple(args.elements) if args.elements else DEFAULT_ELEMENTS

    # --- Stage 1: cheap heuristic prior + phase-stability gate -----------------
    prior = run_round1(
        elements=elements, n_samples=args.n_samples, top_k=args.pool, seed=args.seed,
        backend="heuristic", formability_min=args.formability_min,
    )
    formable = prior.table[prior.table["formable"]].copy()
    pool = _diverse_pick(formable, args.pool, elements) if args.select == "diverse" \
        else formable.head(args.pool)
    if len(pool) == 0:
        raise SystemExit("no single-phase candidates passed the formability gate; "
                         "lower --formability-min or widen --elements")
    pool_comps = list(pool["_comp"])
    prior_eta = {r.formula: r.eta_V for r in pool.itertuples()}
    print(f"# Stage 1 (heuristic prior): {prior.n_candidates} sampled, "
          f"{int(prior.table['formable'].sum())} single-phase; "
          f"select={args.select} -> {len(pool_comps)} to stage-2 backend={args.backend}")

    # --- Stage 2: real backend on the pool only --------------------------------
    _default_size = {"oxide": (2, 2, 4), "rutile": (2, 2, 1)}.get(args.surface, (3, 3, 4))
    size = tuple(args.size) if args.size else _default_size
    be_kwargs = {}
    if args.backend in ("uma", "oc22"):
        be_kwargs = dict(model=args.model, task=args.task, device=args.device, size=size,
                         fmax=args.fmax, steps=args.steps, surface=args.surface, n_sites=args.n_sites)
    be = get_backend(args.backend, **be_kwargs)
    t0 = time.time()
    table = build_table(pool_comps, be, elements)
    # merge the per-composition cus-site eta distribution (rutile multi-site)
    if getattr(be, "site_records", None):
        rec = pd.DataFrame.from_dict(be.site_records, orient="index")
        rec.index.name = "formula"
        table = table.merge(rec.reset_index(), on="formula", how="left")
    ranked = rank(table, formability_min=args.formability_min)
    shortlist = select_shortlist(ranked, top_k=args.top_k, elements=elements)
    dt = time.time() - t0

    # record the cheap prior's eta alongside the real one (for the calibration)
    ranked["eta_prior"] = ranked["formula"].map(prior_eta)

    # --- write results FIRST so the expensive UMA energies are never lost ------
    out_dir = Path(args.out) if args.out else (ROOT / "results")
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = "" if args.surface == "metal" else f"_{args.surface}"
    export = ranked.drop(columns=[c for c in ranked.columns if c.startswith("_")])
    csv = out_dir / f"round1_uma{tag}_candidates.csv"
    export.to_csv(csv, index=False)

    pd.set_option("display.width", 170)
    pd.set_option("display.max_columns", None)
    fmt = lambda v: f"{v:.3f}"  # noqa: E731
    paired = ranked.dropna(subset=["eta_prior"])
    rho = _spearman(paired["eta_prior"].to_numpy(), paired["eta_V"].to_numpy())
    print(f"\n# Stage 2 ({be.name}) on {len(pool_comps)} candidates | {dt:.1f}s")
    print(f"# Spearman rho(eta_prior, eta_UMA) over the pool: {rho:.3f}  "
          f"(1.0 = prior already optimal; lower = UMA adds information)")
    cols = DISPLAY_COLS + (["eta_mean", "eta_std", "n_sites"] if "eta_std" in ranked.columns else [])
    print("\n## Ranked by score (real backend)")
    print(ranked[cols].to_string(index=False, float_format=fmt))
    print(f"\n## Shortlist to melt (diverse top-{args.top_k})")
    print(shortlist[cols].to_string(index=False, float_format=fmt))
    print(f"\n[written] {csv}")

    if not args.no_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(7, 5))
            ax.scatter(ranked["descriptor"], ranked["eta_V"], s=40, c="steelblue",
                       label=f"UMA pool (n={len(ranked)})")
            ax.scatter(shortlist["descriptor"], shortlist["eta_V"], s=160, marker="*",
                       c="crimson", edgecolor="k", zorder=5, label="shortlist to melt")
            xs = np.linspace(0.5, 2.7, 200)
            ax.plot(xs, [overpotential_from_descriptor(x) for x in xs], "k--", lw=1,
                    label="scaling-limit volcano")
            ax.set_xlabel(r"descriptor  $\Delta G_O-\Delta G_{OH}$  (eV)")
            ax.set_ylabel(r"theoretical OER overpotential  $\eta$  (V)")
            _surf = {"metal": "fcc(111) metal proxy", "oxide": "rocksalt(100) oxide",
                     "rutile": "rutile(110) oxide, multi-site"}.get(args.surface, args.surface)
            ax.set_title(f"HEA OER round-1 — {be.name} ({_surf})")
            ax.legend(fontsize=8)
            fig.tight_layout()
            png = out_dir / f"round1_uma{tag}_volcano.png"
            fig.savefig(png, dpi=130)
            print(f"[written] {png}")
        except Exception as e:  # pragma: no cover - plotting is best-effort
            print(f"[plot skipped] {e}")


if __name__ == "__main__":
    main()
