#!/usr/bin/env python3
"""Exploratory analyses of one bench day's EC-Lab files, beside the registered readout (s8_oer_readout.py).

EXPLORATORY: nothing here is a registered endpoint. The registered numbers come from the readout alone; this script
looks at what the readout does not: impedance fits, the pre-OER redox charge, steady state against sweep, the
activation trajectory, an unregistered two-hold Tafel estimate and the check that the instrument's live iR
compensation was applied and left out of the exported Ewe (choice 4, recorded with --ir-hw-verified).

INPUT. The day's native .mpr files (read with galvani) and the RHE offset used for plotting (the day's calibration, or
0.098 + 0.059 pH when the bench has not supplied one). Areas are the 5.00 mm disk face. The file roles for each day
are listed in DAYS below.

  python src/scripts/s8_bench_exploratory.py --day 2026-10-24 --raw RAW_DIR --out OUT_DIR [--offset 0.924]

Writes OUT_DIR/exploratory.json and four figures (exploratory_*.png).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np
from galvani import BioLogic
from scipy.optimize import least_squares

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

AREA = math.pi * 0.25 ** 2      # cm2, 5.00 mm disk face
E_EQ = 1.23
F = 96485.0
IR_TOTAL = 0.90
TAFEL_WINDOW = (0.05, 10.0)     # mA cm-2, the registered window (readout)

DAYS = {
    "2026-10-24": {
        "disk": "A1",
        "activation": "SampleA_1MKOH_CECarbon_REHgHgO_CV1-BeginningActivation_C01.mpr",
        "cv_compensated": "SampleA_EIS-MIR-LSV-2-smallerwindowrepeat2_02_CV_C01.mpr",
        "lsv": "SampleA_EIS-MIR-LSV-2-smallerwindowrepeat2_03_LSV_C01.mpr",
        "eis": [("SampleA_EIS-MIR-LSV-2-smallerwindowrepeat2_05_PEIS_C01.mpr", "after the LSVs"),
                ("CVLast_01_PEIS_C01.mpr", "end of day")],
        "holds": ["CAHolds_02_CA_C01.mpr", "CAHolds_03_CA_C01.mpr", "CAHolds_04_CA_C01.mpr", "CAHolds_05_CA_C01.mpr"],
        "hold_R_u": 5.398,       # ohm, end-of-day EIS (the nearest)
        "cdl": ["EIS-CdlCVs-repeat_0%d_CV_C01.mpr" % k for k in range(2, 8)],
        "cv_last": "CVLast_03_CV_C01.mpr",
        "activation_steady_cycles": (61, 62, 63),
        "compensated_cycles": (2, 3),
        "Rcmp_cv": 6.545,
    },
}


def load(raw, name):
    d = BioLogic.MPRfile(os.path.join(raw, name)).data
    return {c: np.asarray(d[c], float) for c in d.dtype.names if c != "flags"}


def r2(x, y, slope, icpt):
    ss = float(np.sum((y - y.mean()) ** 2))
    return 1 - float(np.sum((y - (slope * x + icpt)) ** 2)) / ss if ss > 0 else None


# ---------------------------------------------------------------------------------------------------- analyses
def eis_fit(d):
    """R_s + inductance + (R_ct || CPE) fitted below 100 kHz; effective capacitance by Brug's formula."""
    fr, zr, zi = d["freq/Hz"], d["Re(Z)/Ohm"], -d["-Im(Z)/Ohm"]
    w, z, m = 2 * np.pi * fr, zr + 1j * zi, fr < 1e5

    def model(p, w):
        Rs, Rct, Q, n, Lh = p
        zc = 1.0 / (Q * (1j * w) ** n)
        return Rs + 1j * w * Lh + Rct * zc / (Rct + zc)

    def resid(p):
        r = (model(p, w[m]) - z[m]) / np.abs(z[m])
        return np.r_[r.real, r.imag]
    fit = least_squares(resid, [5.5, 6.0, 1e-3, 0.85, 1e-7], bounds=([0, 0, 1e-7, 0.4, 0], [50, 500, 1, 1, 1e-4]))
    Rs, Rct, Q, n, _ = fit.x
    o = np.argsort(-fr)
    mi, re_ = -zi[o], zr[o]
    k = np.flatnonzero((mi[:-1] <= 0) & (mi[1:] > 0))
    r_hf = float(re_[k[0]] + (re_[k[0] + 1] - re_[k[0]]) * (0 - mi[k[0]]) / (mi[k[0] + 1] - mi[k[0]])) if len(k) \
        else float(re_.min())
    out = {"E_V_vs_HgHgO": float(d["<Ewe>/V"].mean()), "I_mA": float(d["<I>/mA"].mean()), "R_hf_ohm": r_hf,
           "Rs_fit_ohm": float(Rs), "Rct_ohm": float(Rct), "Rct_ohm_cm2": float(Rct * AREA), "CPE_n": float(n),
           "C_eff_mF": float((Q * (1 / Rs + 1 / Rct) ** (n - 1)) ** (1 / n) * 1e3),
           "rms_rel_residual": float(np.sqrt(np.mean(fit.fun ** 2)))}
    return out, (zr, zi, model(fit.x, w))


def lsv_sweeps(d, offset):
    c = d["control/V"]
    b = [0] + list(np.flatnonzero(np.diff(c) < -0.5) + 1) + [len(c)]
    return [(d["Ewe/V"][b[k]:b[k + 1]] + offset, d["<I>/mA"][b[k]:b[k + 1]]) for k in range(len(b) - 1)]


def anodic_branch(d, cycle):
    s = d["cycle number"] == cycle
    up = np.gradient(d["control/V"][s], d["time/s"][s]) > 0
    e, i = d["Ewe/V"][s][up], d["<I>/mA"][s][up]
    keep = e > 0.5
    o = np.argsort(i[keep])
    return e[keep][o], i[keep][o]


def ir_export_check(act, comp, cfg):
    """Offset at matched current between compensated and uncompensated CVs: dE = a + R I. Applied and left out of Ewe
    gives R near Rcmp (plus any change in R_u) and a near zero; not applied gives dE near zero."""
    pts = []
    for ca in cfg["activation_steady_cycles"]:
        ea, ia = anodic_branch(act, ca)
        for cc in cfg["compensated_cycles"]:
            eb, ib = anodic_branch(comp, cc)
            for j in (5.0, 10.0, 20.0, 30.0):
                I = j * AREA
                pts.append((I, float(np.interp(I, ia, ea) - np.interp(I, ib, eb))))
    I, dE = np.array(pts).T
    R, a = np.polyfit(I / 1e3, dE, 1)
    return {"fit": "dE = a + R I over 5-30 mA cm-2", "R_ohm": float(R), "a_mV": float(a * 1e3),
            "Rcmp_ohm": cfg["Rcmp_cv"], "points": len(pts), "r2": r2(I / 1e3, dE, R, a)}


def redox_wave(d, offset, rate=0.050):
    s = d["cycle number"] == d["cycle number"].max()
    E, I, c, t = d["Ewe/V"][s] + offset, d["<I>/mA"][s], d["control/V"][s], d["time/s"][s]
    w = (np.gradient(c, t) > 0) & (E > 1.15) & (E < 1.52)
    o = np.argsort(E[w])
    Ew, Iw = E[w][o], I[w][o]
    base = np.interp(Ew, [Ew[0], Ew[-1]], [Iw[:5].mean(), Iw[-5:].mean()])
    q = float(np.trapezoid(np.clip(Iw - base, 0, None) / 1e3, Ew) / rate)
    return {"window_V_RHE": [1.15, 1.52], "peak_V_RHE": float(Ew[np.argmax(Iw - base)]), "charge_mC_cm2": q * 1e3 / AREA,
            "sites_nmol_cm2_one_electron": q / F / AREA * 1e9, "note": "linear baseline; includes a second broad wave "
            "near 1.3-1.47 V, so the charge is rough (factor of 2)"}, q / F, (Ew, Iw, base)


def holds(raw, cfg, offset, Rcmp):
    out = []
    for name in cfg["holds"]:
        d = load(raw, name)
        t, E, I = d["time/s"], d["Ewe/V"], d["<I>/mA"]
        span = t[-1] - t[0]
        tail, head = t >= t[-1] - 0.2 * span, t <= t[0] + 0.2 * span
        I_tail = float(I[tail].mean())
        eta = float(E[tail].mean() + offset - (IR_TOTAL - Rcmp / cfg["hold_R_u"]) * I_tail / 1e3 * cfg["hold_R_u"] - E_EQ)
        head_i = I[head][len(I[head]) * 3 // 10:]
        out.append({"E_V_vs_HgHgO": float(E[tail].mean()), "j_tail_mA_cm2": I_tail / AREA, "eta_V_90pct_iR": eta,
                    "tail_vs_early_change_pct": (I_tail / float(head_i.mean()) - 1) * 100,
                    "tail_noise_pct": float(I[tail].std() / I_tail * 100), "_trace": (t, I / AREA)})
    return out


# ---------------------------------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--day", required=True, choices=sorted(DAYS))
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--offset", type=float, default=0.098 + 0.059 * 14,
                    help="E_RHE - E_Hg/HgO for plotting, V (default: the pH formula at pH 14)")
    a = ap.parse_args(argv)
    cfg, raw, off = DAYS[a.day], a.raw, a.offset
    os.makedirs(a.out, exist_ok=True)
    res = {"status": "EXPLORATORY, not registered endpoints", "day": a.day, "disk": cfg["disk"], "rhe_offset_V": off,
           "area_cm2": AREA}

    # impedance
    res["eis"], eis_curves = [], []
    for name, label in cfg["eis"]:
        fit, curves = eis_fit(load(raw, name))
        res["eis"].append(dict(fit, file=name, label=label))
        eis_curves.append((label, curves))

    # LSV sweeps (live Rcmp only; the registered 90% correction is the readout's)
    lsv = load(raw, cfg["lsv"])
    sw = lsv_sweeps(lsv, off)
    rcmp_lsv = float(lsv["Rcmp/Ohm"][0])
    res["lsv"] = {"Rcmp_ohm": rcmp_lsv, "sweeps": []}
    for E, I in sw:
        j = I / AREA
        m = (j > 1) & (j < 10) & (E > 1.4)
        slope = float(np.polyfit(np.log10(j[m]), E[m], 1)[0] * 1e3)
        res["lsv"]["sweeps"].append({"tafel_1to10_mA_cm2_mV_dec": slope, "j_max_mA_cm2": float(j.max())})

    # live-iR export check
    act = load(raw, cfg["activation"])
    comp = load(raw, cfg["cv_compensated"])
    res["ir_export_check"] = ir_export_check(act, comp, cfg)
    res["ir_export_check"]["max_abs_control_minus_Ewe_mV_lsv"] = float(np.max(np.abs(lsv["control/V"] - lsv["Ewe/V"])) * 1e3)
    res["ir_export_check"]["max_Rcmp_x_I_mV_lsv_anodic"] = float(lsv["<I>/mA"].max() * rcmp_lsv)
    res["ir_export_check"]["max_Rcmp_x_I_mV_lsv_cathodic"] = float(-lsv["<I>/mA"].min() * rcmp_lsv)

    # activation trajectory (uncompensated current at 0.70 V vs Hg/HgO on each anodic branch)
    traj = []
    for k in range(1, int(act["cycle number"].max()) + 1):
        s = act["cycle number"] == k
        up = np.gradient(act["control/V"][s], act["time/s"][s]) > 0
        mm = up & (np.abs(act["Ewe/V"][s] - 0.70) < 0.004)
        if mm.any():
            traj.append((k, float(act["<I>/mA"][s][mm].mean() / AREA)))
    traj = np.array(traj)
    res["activation"] = {"cycles": int(act["cycle number"].max()), "duration_min": float(act["time/s"].max() / 60),
                         "first_cycle_reaching_0.70V": int(traj[0, 0]), "j_first_mA_cm2": float(traj[0, 1]),
                         "j_peak_mA_cm2": float(traj[:, 1].max()), "cycle_of_peak": int(traj[np.argmax(traj[:, 1]), 0]),
                         "j_last_mA_cm2": float(traj[-1, 1])}

    # redox wave and TOF lower bound
    last = load(raw, cfg["cv_last"])
    res["redox_wave"], n_sites, wave = redox_wave(last, off)
    E1, I1 = sw[0]
    m1 = E1 > 1.45
    i35 = float(np.interp(E_EQ + 0.35, E1[m1], I1[m1]))
    res["tof_lower_bound"] = {"eta_V": 0.35, "I_mA": i35, "TOF_s-1": i35 / 1e3 / (4 * F * n_sites),
                              "note": "every redox-wave site assumed active, one electron each"}

    # holds: steady state, two-hold Tafel (unregistered), holds against the LSV
    rcmp_hold = float(load(raw, cfg["holds"][0])["Rcmp/Ohm"][0])
    hs = holds(raw, cfg, off, rcmp_hold)
    for h in hs:
        h["j_lsv_same_E_mA_cm2"] = float(np.interp(h["E_V_vs_HgHgO"] + off, E1[m1], I1[m1] / AREA))
        h["hold_over_lsv"] = h["j_tail_mA_cm2"] / h["j_lsv_same_E_mA_cm2"]
    inw = [(math.log10(h["j_tail_mA_cm2"]), h["eta_V_90pct_iR"]) for h in hs
           if TAFEL_WINDOW[0] <= h["j_tail_mA_cm2"] <= TAFEL_WINDOW[1]]
    res["holds"] = [{k: v for k, v in h.items() if not k.startswith("_")} for h in hs]
    res["tafel_two_hold"] = ({"mV_dec": (inw[1][1] - inw[0][1]) / (inw[1][0] - inw[0][0]) * 1e3, "holds_in_window": 2,
                              "note": "unregistered: the readout needs at least 3 holds in the window"}
                             if len(inw) == 2 else {"mV_dec": None, "holds_in_window": len(inw)})

    # figures
    fig, ax = plt.subplots(1, len(eis_curves), figsize=(4.5 * len(eis_curves), 3.8))
    for axk, (label, (zr, zi, zf)) in zip(np.atleast_1d(ax), eis_curves):
        axk.plot(zr, -zi, "o", ms=3, label="data")
        axk.plot(zf.real, -zf.imag, "-", label="Rs + (Rct||CPE)")
        axk.set(xlabel="Re Z / ohm", ylabel="-Im Z / ohm", title=f"EIS at 0.70 V vs Hg/HgO, {label}")
        axk.set_aspect("equal", "datalim")
        axk.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "exploratory_eis.png"), dpi=140); plt.close(fig)

    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    Ew, Iw, base = wave
    ax[0].plot(Ew, Iw / AREA, label="last CV, anodic"); ax[0].plot(Ew, base / AREA, "--", label="baseline")
    ax[0].fill_between(Ew, base / AREA, Iw / AREA, where=Iw > base, alpha=0.3)
    ax[0].set(xlabel="E / V vs RHE", ylabel="j / mA cm$^{-2}$", title="pre-OER redox wave"); ax[0].legend(fontsize=7)
    ax[1].semilogy(E1[m1], I1[m1] / AREA, label="LSV sweep 1 (5 mV/s, live Rcmp)")
    ax[1].semilogy([h["E_V_vs_HgHgO"] + off for h in hs], [h["j_tail_mA_cm2"] for h in hs], "o", label="holds (tail)")
    ax[1].set(xlabel="E / V vs RHE", ylabel="j / mA cm$^{-2}$", title="steady state vs sweep"); ax[1].legend(fontsize=7)
    ax[2].plot(traj[:, 0], traj[:, 1], "o-", ms=3)
    ax[2].set(xlabel="activation cycle", ylabel="j at 0.70 V vs Hg/HgO (no iR) / mA cm$^{-2}$", title="activation")
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "exploratory_redox_holds_activation.png"), dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for k, (E, I) in enumerate(sw, 1):
        m = E > 1.25
        ax[0].plot(E[m], I[m] / AREA, lw=1, label=f"sweep {k}")
    ax[0].axhline(10, ls=":", c="k", lw=0.8)
    ax[0].set(xlabel="E / V vs RHE (live Rcmp only)", ylabel="j / mA cm$^{-2}$", title="LSV, 5 mV/s"); ax[0].legend(fontsize=7)
    t0 = 0.0
    for h in hs:
        t, j = h["_trace"]
        ax[1].plot(t - t[0] + t0, j, lw=0.8)
        t0 += t[-1] - t[0]
    ax[1].set(xlabel="time / s", ylabel="j / mA cm$^{-2}$", title="15-min holds")
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "exploratory_lsv_holds.png"), dpi=140); plt.close(fig)

    rates, half = [], []
    for name in cfg["cdl"]:
        d = load(raw, name)
        s = d["cycle number"] == d["cycle number"].max()
        dd = np.gradient(d["control/V"][s], d["time/s"][s])
        rates.append(float(np.median(np.abs(dd[np.abs(dd) > 0])) * 1e3))
        E, I = d["Ewe/V"][s], d["<I>/mA"][s]
        mid = np.abs(E - (E.min() + E.max()) / 2) <= 0.1 * (E.max() - E.min())
        half.append(float((I[mid & (dd > 0)].mean() - I[mid & (dd < 0)].mean()) / 2))
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    ax.plot(rates, np.array(half) * 1e3, "o-")
    ax.set(xlabel="scan rate / mV s$^{-1}$", ylabel="half (I$_a$ - I$_c$) / uA", title="C_dl (readout gives the fit)")
    fig.tight_layout(); fig.savefig(os.path.join(a.out, "exploratory_cdl.png"), dpi=140); plt.close(fig)

    with open(os.path.join(a.out, "exploratory.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print(json.dumps({k: res[k] for k in ("ir_export_check", "tafel_two_hold", "redox_wave", "activation")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
