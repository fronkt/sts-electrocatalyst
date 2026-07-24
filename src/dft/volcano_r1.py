#!/usr/bin/env python
"""R1 free reanalysis (docs/28 s4 F1-F2): volcano positions + G_max descriptor
for the converged DFT endmembers — no new compute, reads runs/<M>_slab/dft_eta.json.

F1: each endmember on the Man 2011 volcano (descriptor x = dG_O - dG_OH; apex
    x ~ 1.6 eV, eta ~ 0.37 V under the universal *OOH = *OH + 3.2 eV scaling),
    anchored by lit RuO2(110) 0.37-0.42 V / IrO2(110) ~0.56 V.
F2: Exner's G_max(eta) — the largest contiguous free-energy span at applied
    potential U, a kinetics-aware alternative to eta_thermo (Acc. Chem. Res.
    2024, 10.1021/acs.accounts.4c00048). Reported at U = 1.53 V (eta = 0.3 V)
    and at the thermodynamic limiting potential.

Writes docs/figs/volcano_endmembers.{json,png}.
Usage:  python src/dft/volcano_r1.py [runs_dir] [out_prefix]
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from hea_oer.descriptors import oer_steps, OER_EQUILIBRIUM_V  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else "runs"
OUT = sys.argv[2] if len(sys.argv) > 2 else "docs/figs/volcano_endmembers"
METALS = ["Cr", "Mn", "Fe", "Co", "Ni", "Cu"]
ETA_ERR = 0.3  # representative +-0.2-0.4 V method uncertainty (docs/28 s4 F3)


def g_max(steps, U):
    """Exner G_max: largest contiguous span of (dG_i - eU) over the 4 CPET steps."""
    g = np.array(steps) - U
    best = 0.0
    for a in range(4):
        for b in range(a, 4):
            best = max(best, float(g[a:b + 1].sum()))
    return best


def main():
    rows = []
    for M in METALS:
        p = os.path.join(ROOT, f"{M}_slab", "dft_eta.json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        s = d["per_site"][0]
        steps = oer_steps(s["dG_OH"], s["dG_O"], s["dG_OOH"])
        eta = d["eta_min"]
        rows.append(dict(
            metal=M, dG_OH=s["dG_OH"], dG_O=s["dG_O"], dG_OOH=s["dG_OOH"],
            descriptor_eV=round(s["dG_O"] - s["dG_OH"], 3),
            ooh_oh_offset_eV=round(s["dG_OOH"] - s["dG_OH"], 3),  # vs universal 3.2
            eta_V=eta, eta_err_V=ETA_ERR, pls=s["pls"],
            steps_eV=[round(x, 3) for x in steps],
            gmax_at_eta03_eV=round(g_max(steps, OER_EQUILIBRIUM_V + 0.3), 3),
            gmax_at_limiting_eV=round(g_max(steps, OER_EQUILIBRIUM_V + eta), 3),
        ))
    print(f"{'M':3s} {'x=dGO-dGOH':>11s} {'OOH-OH':>7s} {'eta':>6s} {'pls':>3s} "
          f"{'Gmax(0.3V)':>10s}")
    for r in rows:
        print(f"{r['metal']:3s} {r['descriptor_eV']:11.3f} {r['ooh_oh_offset_eV']:7.3f} "
              f"{r['eta_V']:6.3f} {r['pls']:3d} {r['gmax_at_eta03_eV']:10.3f}")

    summary = dict(rows=rows, eta_err_V=ETA_ERR,
                   note="differences < 0.2 V between endmembers are not meaningful "
                        "(docs/28 s4 F3; Chem. Rev. 2024 10.1021/acs.chemrev.4c00171)")
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    json.dump(summary, open(OUT + ".json", "w"), indent=2)
    print(f"-> {OUT}.json")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"[no figure] matplotlib unavailable: {e!r}")
        return
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    xs = np.linspace(0.2, 3.0, 300)
    scaling_eta = np.maximum(xs, 3.2 - xs) - OER_EQUILIBRIUM_V
    ax.plot(xs, -scaling_eta, color="0.55", lw=1.5,
            label=r"scaling volcano ($\Delta G_{OOH}=\Delta G_{OH}+3.2$)")
    ax.axhline(-0.37, color="0.8", lw=0.8, ls=":")
    ax.annotate("apex $\\eta$=0.37 V", (2.55, -0.35), fontsize=8, color="0.5")
    ax.axhspan(-0.42, -0.37, color="#2ca02c", alpha=0.15, label="RuO$_2$(110) lit. band")
    ax.axhspan(-0.62, -0.49, color="#9467bd", alpha=0.12, label="IrO$_2$(110) lit. band")
    for r in rows:
        ax.errorbar(r["descriptor_eV"], -r["eta_V"], yerr=ETA_ERR, fmt="o", ms=8,
                    color="#d62728", ecolor="0.6", capsize=3, zorder=3)
        ax.annotate(r["metal"], (r["descriptor_eV"], -r["eta_V"]),
                    xytext=(6, 4), textcoords="offset points", fontsize=10)
    ax.set_xlabel(r"$\Delta G_{O} - \Delta G_{OH}$  (eV)")
    ax.set_ylabel(r"$-\eta$  (V)")
    ax.set_title("Rutile MO$_2$(110) endmembers on the OER scaling volcano (QE PBE+U)")
    ax.legend(loc="lower left", fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT + ".png", dpi=200)
    print(f"-> {OUT}.png")


if __name__ == "__main__":
    main()
