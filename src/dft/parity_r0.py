#!/usr/bin/env python
"""R0 parity analysis (docs/28 s7): uma-s-1p2p1 x {oc22, oc20} vs the archived
QE PBE+U eta, with the uma-s-1p1/oc20 docs/26 points as the baseline ghost.

Reads   runs/<M>_slab/dft_eta.json                (4 converged endmembers)
        runs/<M>_slab/uma_eta_1p2p1_<task>.json   (this campaign)
        runs/<M>_slab/uma_eta.json                (archived 1p1/oc20 baseline)
        runs/{Ru,Ir}_anchor/uma_eta_1p2p1_<task>.json  (in-distribution anchors)
Writes  docs/figs/uma_oc22_parity.{json,png}

Gate (docs/28 s7): Spearman >=0.8 -> screen as-is; 0.5-0.8 -> fine-tune (R3);
~0 -> the negative result is real and becomes a headline finding.

Usage:  python src/dft/parity_r0.py [runs_dir] [out_prefix]
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else "runs"
OUT = sys.argv[2] if len(sys.argv) > 2 else "docs/figs/uma_oc22_parity"
METALS = ["Cr", "Mn", "Fe", "Co", "Ni", "Cu"]
ANCHORS = {"Ru": (0.37, 0.42), "Ir": (0.49, 0.62)}  # lit eta bands: Rossmeisl 2007 / Man 2011
TASKS = ["oc22", "oc20", "oc25"]  # oc22 = pre-registered hypothesis; oc25 exploratory


def load_eta(path):
    if not os.path.exists(path):
        return None
    try:
        return float(json.load(open(path))["eta_min"])
    except Exception as e:
        print(f"  [warn] {path}: {e!r}")
        return None


def stats(uma, dft):
    uma, dft = np.asarray(uma, float), np.asarray(dft, float)
    try:
        from scipy.stats import spearmanr, pearsonr
        rho, rho_p = spearmanr(uma, dft)
        r, r_p = pearsonr(uma, dft)
    except Exception:
        ra, rb = np.argsort(np.argsort(uma)), np.argsort(np.argsort(dft))
        rho = float(np.corrcoef(ra, rb)[0, 1]); r = float(np.corrcoef(uma, dft)[0, 1])
        rho_p = r_p = float("nan")
    return dict(spearman_rho=round(float(rho), 4), spearman_p=float(rho_p),
                pearson_r=round(float(r), 4), pearson_p=float(r_p),
                mae_eV=round(float(np.mean(np.abs(uma - dft))), 4),
                mean_uma_minus_dft_eV=round(float(np.mean(uma - dft)), 4))


def main():
    dft = {M: load_eta(os.path.join(ROOT, f"{M}_slab", "dft_eta.json")) for M in METALS}
    base = {M: load_eta(os.path.join(ROOT, f"{M}_slab", "uma_eta.json")) for M in METALS}
    summary = dict(dft_eta={m: v for m, v in dft.items() if v is not None},
                   baseline_1p1_oc20={m: v for m, v in base.items() if v is not None},
                   variants={}, anchors={})

    for task in TASKS:
        uma = {M: load_eta(os.path.join(ROOT, f"{M}_slab", f"uma_eta_1p2p1_{task}.json"))
               for M in METALS}
        paired = [(M, uma[M], dft[M]) for M in METALS
                  if uma[M] is not None and dft[M] is not None]
        block = dict(eta={m: v for m, v in uma.items() if v is not None})
        if len(paired) >= 2:
            ms = [p[0] for p in paired]
            s = stats([p[1] for p in paired], [p[2] for p in paired])
            block.update(paired_metals=ms, **s)
            print(f"[1p2p1/{task}] n={len(paired)} ({', '.join(ms)})  "
                  f"rho={s['spearman_rho']:+.3f} (p={s['spearman_p']:.3g})  "
                  f"r={s['pearson_r']:+.3f}  MAE={s['mae_eV']:.3f} eV")
        summary["variants"][task] = block

        for A, band in ANCHORS.items():
            eta = load_eta(os.path.join(ROOT, f"{A}_anchor", f"uma_eta_1p2p1_{task}.json"))
            if eta is not None:
                ok = band[0] - 0.15 <= eta <= band[1] + 0.15
                summary["anchors"][f"{A}_{task}"] = dict(eta=eta, lit_band=band, within_015V=ok)
                print(f"  anchor {A}O2(110)/{task}: eta={eta:.3f} V  lit {band[0]}-{band[1]} V"
                      f"  {'OK' if ok else 'OFF'}")

    # baseline stats for the record
    bp = [(M, base[M], dft[M]) for M in METALS if base[M] is not None and dft[M] is not None]
    if len(bp) >= 2:
        summary["baseline_stats"] = stats([p[1] for p in bp], [p[2] for p in bp])
        print(f"[1p1/oc20 baseline] rho={summary['baseline_stats']['spearman_rho']:+.3f}  "
              f"MAE={summary['baseline_stats']['mae_eV']:.3f} eV")

    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    json.dump(summary, open(OUT + ".json", "w"), indent=2)
    print(f"-> {OUT}.json")

    # ---- figure: one parity panel per task, baseline ghosted, anchors inset ----
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"[no figure] matplotlib unavailable: {e!r}")
        return
    fig, axes = plt.subplots(1, len(TASKS), figsize=(5.2 * len(TASKS), 5.2), sharey=False)
    for ax, task in zip(np.atleast_1d(axes), TASKS):
        blk = summary["variants"][task]
        pm = blk.get("paired_metals", [])
        if not pm:
            ax.set_title(f"uma-s-1p2p1 / {task} — no data")
            continue
        x = np.array([summary["dft_eta"][m] for m in pm])
        y = np.array([blk["eta"][m] for m in pm])
        gx = [summary["dft_eta"][m] for m in pm if m in summary["baseline_1p1_oc20"]]
        gy = [summary["baseline_1p1_oc20"][m] for m in pm if m in summary["baseline_1p1_oc20"]]
        lo = min(x.min(), y.min(), *(gy or [9])) - 0.25
        hi = max(x.max(), y.max(), *(gy or [0])) + 0.35  # headroom for point labels
        ax.plot([lo, hi], [lo, hi], "--", color="0.6", lw=1, zorder=1)
        if gx:
            ax.scatter(gx, gy, s=45, c="0.8", edgecolor="0.5", zorder=2,
                       label="uma-s-1p1/oc20 (docs/26)")
        ax.scatter(x, y, s=75, c="#d62728" if task == "oc22" else "#1f77b4",
                   edgecolor="k", zorder=3, label=f"uma-s-1p2p1/{task}")
        for m, xi, yi in zip(pm, x, y):
            ax.annotate(m, (xi, yi), xytext=(5, 4), textcoords="offset points", fontsize=10)
        ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
        ax.set_xlabel(r"DFT (QE PBE+U) $\eta$ (V)")
        ax.set_ylabel(rf"UMA $\eta$ (V)")
        ax.set_title(f"task_name='{task}'")
        txt = (f"$\\rho$ = {blk['spearman_rho']:.2f}\n$r$ = {blk['pearson_r']:.2f}\n"
               f"MAE = {blk['mae_eV']:.2f} eV")
        ax.text(0.04, 0.96, txt, transform=ax.transAxes, va="top", ha="left", fontsize=10,
                bbox=dict(boxstyle="round", fc="w", ec="0.7"))
        ax.legend(loc="lower right", fontsize=8, frameon=False)
    fig.suptitle("R0 re-parity: rutile MO$_2$(110) OER $\\eta$, uma-s-1p2p1 task heads vs DFT+U",
                 y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT + ".png", dpi=200, bbox_inches="tight")
    print(f"-> {OUT}.png")


if __name__ == "__main__":
    main()
