#!/usr/bin/env python
"""6-point UMA<->DFT parity for the rutile MO2 endmembers (Cr, Mn, Fe, Co, Ni, Cu).

The keystone calibration of the multi-fidelity funnel: UMA (MLIP screen) and QE
PBE+U DFT relax the IDENTICAL initial geometries and apply the SAME CHE
referencing; only the relaxer differs. We pair the single-site OER overpotential
eta from runs/<M>_slab/uma_eta.json vs dft_eta.json, then report Spearman rho
(does UMA rank endmembers like DFT?) + Pearson r (linear agreement) + MAE, and
draw the parity scatter.

Usage:  python src/dft/parity_plot.py [runs_dir] [out_prefix]
"""
from __future__ import annotations
import json, os, sys
import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else "runs"
OUT = sys.argv[2] if len(sys.argv) > 2 else "docs/figs/uma_dft_parity"
METALS = ["Cr", "Mn", "Fe", "Co", "Ni", "Cu"]


def load_eta(M: str, which: str):
    p = os.path.join(ROOT, f"{M}_slab", f"{which}_eta.json")
    if not os.path.exists(p):
        return None
    try:
        return float(json.load(open(p))["eta_min"])
    except Exception as e:
        print(f"  [warn] {p}: {e!r}")
        return None


def _spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    rows = [(M, load_eta(M, "uma"), load_eta(M, "dft")) for M in METALS]
    print("metal   UMA_eta   DFT_eta")
    for M, u, d in rows:
        print(f"  {M:3s}   {('%.3f' % u) if u is not None else '  -  ':>7}   "
              f"{('%.3f' % d) if d is not None else 'PENDING':>7}")

    paired = [(M, u, d) for (M, u, d) in rows if u is not None and d is not None]
    if len(paired) < 2:
        print(f"\nOnly {len(paired)} paired point(s); need >=2 for correlation. "
              "DFT still pending for some endmembers.")
        return
    metals = [r[0] for r in paired]
    uma = np.array([r[1] for r in paired], float)
    dft = np.array([r[2] for r in paired], float)

    try:
        from scipy.stats import spearmanr, pearsonr
        rho, rho_p = spearmanr(uma, dft)
        r, r_p = pearsonr(uma, dft)
    except Exception:
        rho = _spearman(uma, dft); r = float(np.corrcoef(uma, dft)[0, 1])
        rho_p = r_p = float("nan")
    mae = float(np.mean(np.abs(uma - dft)))
    bias = float(np.mean(uma - dft))  # +ve => UMA over-binds (lower eta? sign per def)

    print(f"\nPaired points: {len(paired)}/{len(METALS)}  ({', '.join(metals)})")
    print(f"Spearman rho = {rho:.3f}  (p={rho_p:.3g})   <- rank agreement")
    print(f"Pearson  r   = {r:.3f}  (p={r_p:.3g})   <- linear agreement")
    print(f"MAE = {mae:.3f} eV    mean(UMA-DFT) = {bias:+.3f} eV")

    summary = dict(
        n_paired=len(paired), metals=metals,
        uma_eta=uma.round(3).tolist(), dft_eta=dft.round(3).tolist(),
        spearman_rho=round(float(rho), 4), spearman_p=float(rho_p),
        pearson_r=round(float(r), 4), pearson_p=float(r_p),
        mae_eV=round(mae, 4), mean_uma_minus_dft_eV=round(bias, 4),
    )
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    json.dump(summary, open(OUT + ".json", "w"), indent=2)
    print(f"-> {OUT}.json")

    # ---- figure ----
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"[no figure] matplotlib unavailable: {e!r}")
        return
    lo = float(min(uma.min(), dft.min())) - 0.2
    hi = float(max(uma.max(), dft.max())) + 0.2
    fig, ax = plt.subplots(figsize=(5.2, 5.0))
    ax.plot([lo, hi], [lo, hi], "--", color="0.6", lw=1, zorder=1, label="parity (y=x)")
    ax.scatter(dft, uma, s=70, c="#1f77b4", edgecolor="k", zorder=3)
    for M, x, y in zip(metals, dft, uma):
        ax.annotate(M, (x, y), xytext=(5, 4), textcoords="offset points", fontsize=10)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
    ax.set_xlabel(r"DFT (PBE+U) OER $\eta$  (V)")
    ax.set_ylabel(r"UMA (uma-s-1p1) OER $\eta$  (V)")
    ax.set_title(f"UMA$\\leftrightarrow$DFT parity, rutile MO$_2$ ({len(paired)} endmembers)")
    txt = (f"Spearman $\\rho$ = {rho:.2f}\nPearson $r$ = {r:.2f}\n"
           f"MAE = {mae:.2f} eV")
    ax.text(0.04, 0.96, txt, transform=ax.transAxes, va="top", ha="left",
            fontsize=10, bbox=dict(boxstyle="round", fc="w", ec="0.7"))
    ax.legend(loc="lower right", fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT + ".png", dpi=200)
    print(f"-> {OUT}.png")


if __name__ == "__main__":
    main()
