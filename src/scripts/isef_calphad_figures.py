"""CALPHAD figures for the ISEF round-2 plan (step P3b).

  compute: phase fractions vs temperature for every alloy in isef_calphad_check.ALLOYS,
           one database at a time -> results/isef_round2_2026-11-10/calphad_step_<db>.json
  plot:    fig_calphad_steps_<db>.png  (phase fraction vs T, one panel per alloy)
           fig_calphad_1050C.png       (predicted assemblage at 1,050 C vs the measured count)

Phases are grouped by identity, not by database name: an FCC or liquid vertex holding more
than half Cu is "Cu-rich", because pycalphad reports a miscibility gap as two vertices of
one phase.

    PY=D:/sts-electrocatalyst/.venv-isef/Scripts/python.exe
    $PY -I src/scripts/isef_calphad_figures.py compute --db mc_fe
    $PY -I src/scripts/isef_calphad_figures.py compute --db mf
    $PY -I src/scripts/isef_calphad_figures.py plot
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import isef_calphad_check as chk  # noqa: E402

OUT = "results/isef_round2_2026-11-10"
FIGS = f"{OUT}/figs"
T_C = np.arange(600.0, 1455.0, 10.0)  # includes 1,050 C exactly
HOMOG_C = 1050.0

CLASSES = ["FCC", "FCC, Cu-rich", "BCC", "Sigma", "Liquid", "Other"]
#: Reference categorical palette (dataviz skill, light mode), fixed order, by identity.
COLORS = {"FCC": "#2a78d6", "FCC, Cu-rich": "#eb6834", "BCC": "#1baf7a",
          "Sigma": "#eda100", "Liquid": "#e87ba4", "Other": "#6250d6"}
STYLES = {"FCC": "-", "FCC, Cu-rich": "--", "BCC": "-", "Sigma": "-.", "Liquid": ":",
          "Other": "-"}
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

MEASURED_N = {"Fe25": 1, "Ni34": 1, "Ni31": 2, "Cu22": 2, "Cu8": 3, "Cu26": 3}
MEASURED_TXT = {"Fe25": "1 phase (FCC)", "Ni34": "1 phase (FCC)",
                "Ni31": "2 (FCC + Cr-rich BCC)", "Cu22": "2", "Cu8": "3 (incl. sigma)",
                "Cu26": "3 (Cu-rich pools)"}
ROUND2 = ["FeCoNi", "CoCr0.5FeNi", "Ni86Cu14", "Ni34Fe29Mn30Co7", "Mn31Ni31Co33Cu6"]
ORDER = ["Fe25", "Ni34", "Ni31", "Cu22", "Cu8", "Cu26"] + ROUND2


def classify(phase: str, x_cu: float) -> str:
    p = phase.upper()
    cu_rich = x_cu > 0.5
    if p.startswith("FCC"):
        return "FCC, Cu-rich" if cu_rich else "FCC"
    if p.startswith("BCC"):
        return "BCC"
    if p.startswith("SIGMA"):
        return "Sigma"
    if p == "LIQUID":
        return "Liquid"
    return "Other"


def compute(dbkey: str) -> int:
    from pycalphad import Database, equilibrium, variables as v
    from pycalphad.core.utils import filter_phases
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        db = Database(chk.DBS[dbkey])
    out = {}
    for name in ORDER:
        comp = chk.ALLOYS[name]
        if dbkey == "mf" and "CO" in comp and "CU" in comp:
            out[name] = dict(skipped="no Co-Cu parameters in mf-steel")
            continue
        els = sorted(comp)
        tot = sum(comp.values())
        comps = els + ["VA"]
        phases = [p for p in chk.WANT[dbkey] if p in filter_phases(db, comps)]
        if "MN" not in comp:  # alpha-Mn only where Mn exists (see isef_calphad_check)
            phases = [p for p in phases if p not in chk.ALPHA_MN_NAMES]
        conds = {v.T: list(T_C + 273.15), v.P: 101325, v.N: 1}
        for el in els[1:]:
            conds[v.X(el)] = comp[el] / tot
        t0 = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            eq = equilibrium(db, comps, phases, conds)
        cu_idx = list(eq.component.values).index("CU") if "CU" in comp else None
        ph = eq.Phase.values.squeeze()   # (T, vertex)
        npf = eq.NP.values.squeeze()
        xs = eq.X.values.squeeze()       # (T, vertex, component)
        frac = {c: [0.0] * len(T_C) for c in CLASSES}
        raw = []
        for i in range(len(T_C)):
            here = []
            for j in range(ph.shape[1]):
                p = str(ph[i, j])
                f = float(npf[i, j])
                if not p or np.isnan(f) or f < 1e-4:
                    continue
                x_cu = float(xs[i, j, cu_idx]) if cu_idx is not None else 0.0
                c = classify(p, x_cu)
                frac[c][i] += f
                here.append(dict(phase=p, cls=c, f=round(f, 4), x_cu=round(x_cu, 3)))
            raw.append(here)
        out[name] = dict(T_C=list(T_C), fractions=frac, raw=raw, phases_considered=phases,
                         seconds=round(time.time() - t0, 1))
        print(f"{dbkey} {name:>16}  {time.time() - t0:6.1f} s", flush=True)
    path = f"{OUT}/calphad_step_{dbkey}.json"
    json.dump(dict(db=dbkey, path=chk.DBS[dbkey], results=out), open(path, "w"), indent=1)
    print(f"wrote {path}")
    return 0


def _style_axes(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8, length=3, color=GRID)
    ax.grid(True, axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def plot_steps(dbkey: str, title: str):
    import matplotlib.pyplot as plt
    d = json.load(open(f"{OUT}/calphad_step_{dbkey}.json"))["results"]
    names = [n for n in ORDER if "skipped" not in d.get(n, {"skipped": 1})]
    ncol = 4
    nrow = int(np.ceil((len(names) + 1) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(12, 2.75 * nrow), sharex=True, sharey=True)
    fig.patch.set_facecolor(SURFACE)
    axes = axes.ravel()
    used = set()
    for ax, name in zip(axes, names):
        _style_axes(ax)
        r = d[name]
        T = np.array(r["T_C"])
        for c in CLASSES:
            y = np.array(r["fractions"][c])
            if y.max() < 1e-3:
                continue
            used.add(c)
            ax.plot(T, y, STYLES[c], color=COLORS[c], lw=2, solid_capstyle="round")
        ax.axvline(HOMOG_C, color=INK2, lw=0.8, ls=(0, (2, 2)))
        ax.set_ylim(-0.02, 1.05)
        ax.set_xlim(T[0], T[-1])
        tag = "measured: " + MEASURED_TXT[name] if name in MEASURED_TXT else "round 2 (not melted)"
        ax.set_title(f"{name}\n{tag}", fontsize=9, color=INK, loc="left")
    for ax in axes[len(names):]:
        ax.axis("off")
    for ax in axes[::ncol]:
        ax.set_ylabel("phase fraction", fontsize=8, color=INK2)
    for ax in axes[-ncol:]:
        ax.set_xlabel("temperature (°C)", fontsize=8, color=INK2)
    for ax in axes[:len(names)]:
        ax.xaxis.set_tick_params(labelbottom=True)
    leg_ax = axes[len(names)]
    handles = [plt.Line2D([0], [0], color=COLORS[c], ls=STYLES[c], lw=2) for c in CLASSES if c in used]
    handles.append(plt.Line2D([0], [0], color=INK2, lw=0.8, ls=(0, (2, 2))))
    labels = [c for c in CLASSES if c in used] + ["homogenized, 1,050 °C"]
    leg_ax.legend(handles, labels, loc="center left", frameon=False, fontsize=9,
                  labelcolor=INK)
    fig.suptitle(title, x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    os.makedirs(FIGS, exist_ok=True)
    path = f"{FIGS}/fig_calphad_steps_{dbkey}.png"
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path}")


def plot_1050():
    import matplotlib.pyplot as plt
    d = json.load(open(f"{OUT}/calphad_step_mc_fe.json"))["results"]
    T_saved = np.array(d[ORDER[0]]["T_C"])
    i = int(np.argmin(np.abs(T_saved - HOMOG_C)))
    assert abs(T_saved[i] - HOMOG_C) < 1e-6, f"grid lacks {HOMOG_C} C (nearest {T_saved[i]})"
    names = ORDER
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    fig.patch.set_facecolor(SURFACE)
    _style_axes(ax)
    ax.grid(True, axis="x", color=GRID, lw=0.6)
    ax.grid(False, axis="y")
    ys = np.arange(len(names))[::-1].astype(float)
    ys[:6] += 0.8  # open a gap between the melted six and round 2
    used = set()
    gap = 0.004
    for y, name in zip(ys, names):
        left = 0.0
        for c in CLASSES:
            f = d[name]["fractions"][c][i]
            if f < 1e-3:
                continue
            used.add(c)
            ax.barh(y, max(f - gap, 0.0), left=left, height=0.6, color=COLORS[c],
                    edgecolor="none")
            left += f
        n_pred = sum(1 for e in d[name]["raw"][i] if e["f"] >= 1e-3)
        if name in MEASURED_N:
            ok = "match" if n_pred == MEASURED_N[name] else "MISS"
            txt = f"predicted {n_pred}, measured {MEASURED_N[name]}: {ok}"
        else:
            txt = f"predicted {n_pred}: not yet melted"
        ax.text(1.02, y, txt, va="center", fontsize=8.5, color=INK if name in MEASURED_N else INK2)
    ax.set_yticks(ys)
    ax.set_yticklabels(names, fontsize=9, color=INK)
    mid = (ys[5] + ys[6]) / 2
    ax.axhline(mid, color=GRID, lw=1)
    ax.text(0.0, mid + 0.12, "melted (round 1)", ha="left", va="bottom", fontsize=7.5,
            color=INK2)
    ax.text(0.0, mid - 0.12, "proposed (round 2)", ha="left", va="top", fontsize=7.5,
            color=INK2)
    ax.set_xlim(0, 1)
    ax.set_xlabel("phase fraction at 1,050 °C (MatCalc mc_fe)", fontsize=9, color=INK2)
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[c]) for c in CLASSES if c in used]
    ax.legend(handles, [c for c in CLASSES if c in used], ncol=len(handles), frameon=False,
              fontsize=8.5, loc="lower left", bbox_to_anchor=(0, 1.0), labelcolor=INK)
    ax.set_title("CALPHAD at the homogenization temperature vs. the six melted alloys",
                 fontsize=11, color=INK, loc="left", pad=26)
    fig.tight_layout()
    fig.subplots_adjust(right=0.70)
    path = f"{FIGS}/fig_calphad_1050C.png"
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compute")
    c.add_argument("--db", choices=list(chk.DBS), required=True)
    sub.add_parser("plot")
    a = ap.parse_args()
    if a.cmd == "compute":
        return compute(a.db)
    plot_steps("mc_fe", "CALPHAD phase fractions vs temperature: MatCalc mc_fe (all six elements; extrapolated beyond its steel range)")
    if os.path.exists(f"{OUT}/calphad_step_mf.json"):
        plot_steps("mf", "CALPHAD phase fractions vs temperature: LibreCalphad mf-steel (alloys without Co-Cu only)")
    plot_1050()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
