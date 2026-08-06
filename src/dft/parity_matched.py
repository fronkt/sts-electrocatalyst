#!/usr/bin/env python
"""MACE vs UMA on ONE footing: the repaired n = 7 tier, matched protocol (docs/38).

What this supersedes and why
----------------------------
`parity_r0.py` is the historical R0 record and stays as it is -- it reports what was
measured in July 2026. But it cannot produce the comparison this project actually
needs, for two structural reasons:

1. It reads `runs/<M>_slab/dft_eta.json`, which **does not exist for Ni or Co**. Their
   eta comes from the bounded `*OH`/`*O` identity in `eta_bounded.py`. So parity_r0
   tops out at n = 5 and cannot reach the n = 7 tier docs/35 quotes.
2. Its output (`docs/figs/uma_oc22_parity.json`) was written against the DFT reference
   later found defective -- Cr = 1.726 V (trapped `s0_O`) and Ni = 1.751 V (retracted,
   docs/30 s2). Those files are correct as a record of the July campaign and are kept,
   but they carry a `SUPERSEDED_BY` banner pointing here.

This script scores every stored UMA head AND the matched-protocol MACE run against
`eta_bounded.reference_tier()` -- the single call that returns the tier of record
however each metal's eta was established.

Two cuts are reported, deliberately:

* **n = 7** -- the full tier, the headline.
* **n = 5** -- dropping Ni and Co, whose DFT restarts were commissioned from MACE's
  own minima (docs/34 s4b) and whose eta comes from the bounded identity rather than
  a complete CHE chain. MACE is +0.900 here at p = 0.0833, so **the gate is not met
  at n = 5**. Reporting only n = 7 would hide that the two MACE-entangled points are
  what carry significance.

    python src/dft/parity_matched.py
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from dft.eta_bounded import reference_tier          # noqa: E402
from dft.mlip_eval import exact_two_sided_p         # noqa: E402

#: Dropped for the n = 5 cut: bounded eta, and DFT restarts seeded from MACE minima.
MACE_ENTANGLED = ("Ni", "Co")
GATE_RHO = 0.8


def spearman(x, y) -> float:
    n = len(x)
    rx, ry = _rank(x), _rank(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def _rank(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0] * len(v)
    for pos, i in enumerate(order):
        r[i] = pos + 1
    return r


def score(pred: dict, ref: dict, metals) -> dict | None:
    ms = sorted(m for m in metals if m in pred and pred[m] is not None and m in ref)
    if len(ms) < 3:
        return None
    p = [pred[m] for m in ms]
    d = [ref[m] for m in ms]
    rho = spearman(d, p)
    return dict(n=len(ms), metals=ms, rho=round(rho, 4),
                p_exact=round(exact_two_sided_p(rho, len(ms)), 4),
                mae_eta=round(sum(abs(a - b) for a, b in zip(d, p)) / len(ms), 4),
                gate_met=bool(rho >= GATE_RHO and exact_two_sided_p(rho, len(ms)) < 0.05))


def load_uma(root: str) -> dict:
    """Every stored UMA eta, keyed 'checkpoint/head'."""
    heads: dict[str, dict] = {}
    for f in glob.glob(os.path.join(root, "*", "uma_eta*.json")):
        rec = json.load(open(f))
        metal = os.path.basename(os.path.dirname(f)).split("_")[0]
        tag = f"{rec.get('backend', 'uma-s-1p1')}/{rec.get('task', 'oc20')}"
        heads.setdefault(tag, {})[metal] = rec.get("eta_min")
    return heads


def main() -> None:
    root = sys.argv[1] if len(sys.argv) > 1 else "runs"
    matched_path = sys.argv[2] if len(sys.argv) > 2 else "results/r5_matched_protocol.json"
    out = sys.argv[3] if len(sys.argv) > 3 else "docs/figs/parity_matched"

    ref = {m: v["eta"] for m, v in reference_tier(root).items()}
    src = {m: v.get("source") for m, v in reference_tier(root).items()}
    models = load_uma(root)

    full = sorted(ref)
    cut5 = [m for m in full if m not in MACE_ENTANGLED]
    summary: dict = dict(
        reference_tier={m: dict(eta=round(ref[m], 4), source=src[m]) for m in full},
        note=("All models scored against eta_bounded.reference_tier(). Rows marked "
              "'(matched)' come from mace_uma_protocol.py -- original builder geometries, "
              "single start, as-shipped masks, one runner with the calculator swapped, so "
              "they are comparable by construction rather than by discipline (docs/39 s2)."),
        n7={}, n5={}, adsorbate_qc={})

    # Every matched-protocol run, whatever backend produced it.
    found = sorted(glob.glob(os.path.join(os.path.dirname(matched_path) or ".",
                                          "r5_matched_*.json")))
    if not found:
        print("[warn] no results/r5_matched_*.json -- run mace_uma_protocol.py first")
    for f in found:
        rec = json.load(open(f))
        label = f"{rec.get('tag') or rec.get('model', os.path.basename(f))} (matched)"
        models[label] = {m: r["eta"] for m, r in rec["pred"].items()}
        desorbed = [m for m, r in rec["pred"].items()
                    if (r["qc"]["s0_OOH"]["m_o_final"] or 0) >= 3.0]
        # A desorbed *OOH only contaminates eta when the potential-limiting step actually
        # touches dG_OOH, i.e. pls in {3, 4}. Recording both is the difference between
        # "QC flag" and "this number is wrong" -- and the distinction is load-bearing:
        # omat desorbs *OOH on 5 of 7 metals but only ONE of them is pls=3 (docs/39 s6).
        summary["adsorbate_qc"][label] = dict(
            desorbed_OOH=sorted(desorbed),
            eta_contaminated=sorted(m for m in desorbed if rec["pred"][m]["pls"] in (3, 4)))

    print(f"{'model / head':<30}{'n':>3}{'rho':>9}{'p_exact':>10}{'MAE V':>9}  gate")
    for tag, pred in sorted(models.items()):
        for key, metals in (("n7", full), ("n5", cut5)):
            s = score(pred, ref, metals)
            if s:
                summary[key][tag] = s
        s = summary["n7"].get(tag)
        if s:
            print(f"{tag:<30}{s['n']:>3}{s['rho']:>+9.3f}{s['p_exact']:>10.4f}"
                  f"{s['mae_eta']:>9.3f}  {'MET' if s['gate_met'] else '--'}")

    print(f"\n  n = 5 cut (drop {', '.join(MACE_ENTANGLED)}):")
    for tag, s in sorted(summary["n5"].items()):
        print(f"    {tag:<28}{s['n']:>3}{s['rho']:>+9.3f}{s['p_exact']:>10.4f}"
              f"{s['mae_eta']:>9.3f}  {'MET' if s['gate_met'] else 'NOT MET'}")

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump(summary, open(out + ".json", "w"), indent=2)
    print(f"\n-> {out}.json")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"[no figure] matplotlib unavailable: {e!r}")
        return

    tags = [t for t in sorted(models) if t in summary["n7"]]
    fig, axes = plt.subplots(1, len(tags), figsize=(4.3 * len(tags), 4.6))
    for ax, tag in zip([axes] if len(tags) == 1 else axes, tags):
        s = summary["n7"][tag]
        x = [ref[m] for m in s["metals"]]
        y = [models[tag][m] for m in s["metals"]]
        lo, hi = min(x + y) - 0.2, max(x + y) + 0.3
        ax.plot([lo, hi], [lo, hi], "--", color="0.6", lw=1)
        is_mace = "mace" in tag.lower()
        ax.scatter(x, y, s=70, c="#d62728" if is_mace else "#1f77b4", edgecolor="k", zorder=3)
        for m, xi, yi in zip(s["metals"], x, y):
            ax.annotate(m, (xi, yi), xytext=(5, 4), textcoords="offset points", fontsize=9)
        ax.set_xlim(lo, hi), ax.set_ylim(lo, hi)
        ax.set_aspect("equal")
        ax.set_xlabel(r"DFT (QE PBE+U) $\eta$ (V), repaired n=7 tier")
        ax.set_ylabel(r"model $\eta$ (V)")
        ax.set_title(tag, fontsize=10)
        ax.text(0.04, 0.96, f"$\\rho$ = {s['rho']:+.3f}\np = {s['p_exact']:.4f}\n"
                            f"MAE = {s['mae_eta']:.3f} V",
                transform=ax.transAxes, va="top", fontsize=9,
                bbox=dict(boxstyle="round", fc="w", ec="0.7"))
    fig.suptitle("Matched protocol: every model relaxed from the ORIGINAL builder "
                 "geometries, single start, vs the repaired n=7 tier", y=1.0, fontsize=11)
    fig.tight_layout()
    fig.savefig(out + ".png", dpi=200, bbox_inches="tight")
    print(f"-> {out}.png")


if __name__ == "__main__":
    main()
