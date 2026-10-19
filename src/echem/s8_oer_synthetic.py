#!/usr/bin/env python3
"""Synthetic S8 bench campaign: potentiostat files plus a manifest, for testing s8_oer_readout.py and laying out
Figure 8 before any electrode is measured.

Every manifest written here starts with '# SYNTHETIC', which the readout carries as "synthetic": true. All values in
TRUTH are invented and stand for no prediction or measurement. The key maps codes to alloys in the freeze's order
(A = Cu8 ... F = Cu22); it is not the bench key.

Physics, deliberately simple: j = 10 x 10^((eta - eta_10)/b) mA cm-2 on the true (iR-free) potential, plus a Gaussian
pre-OER redox peak at 1.38 V vs RHE and a double-layer current in the C_dl CVs. The recorded potential carries the
uncompensated (1 - instrument share) x I x R_u, so the readout's 90% correction leaves 0.10 x I x R_u in eta, by
design. Disk k of each alloy sits at eta_10 + (k - 2) x DISK_SD, so each alloy's mean and SD are exact.

Usage:
  PYTHONPATH=src python src/echem/s8_oer_synthetic.py OUT_DIR      (writes OUT_DIR/manifest.csv, key.csv, files/)
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s8_oer_readout import ALLOYS, AREA_CM2, CODES, E_EQ, MANIFEST_COLUMNS  # noqa: E402

TRUTH = {  # eta_10 (V), Tafel slope b (V/dec), C_dl (F), redox peak height (mA cm-2)
    "Cu8": dict(eta10=0.400, b=0.055, cdl=60e-6, peak=0.0),
    "Ni31": dict(eta10=0.360, b=0.045, cdl=45e-6, peak=0.6),
    "Fe25": dict(eta10=0.450, b=0.060, cdl=50e-6, peak=0.4),
    "Cu26": dict(eta10=0.380, b=0.050, cdl=55e-6, peak=0.3),
    "Ni34": dict(eta10=0.430, b=0.065, cdl=40e-6, peak=0.6),
    "Cu22": dict(eta10=0.490, b=0.070, cdl=35e-6, peak=0.0),
}
IRO2_TRUTH = dict(eta10=0.390, b=0.050, cdl=400e-6, peak=0.0)
IRO2_DAY_SHIFT = (-0.003, 0.0, 0.003)
DRIFT_TRUE_MV_H = 2.0
DISK_SD = 0.012
DAYS = ("2026-10-26", "2026-10-27", "2026-10-28")
OFFSETS = (0.9260, 0.9241, 0.9253)          # E_RHE - E_Hg/HgO per day, V
FORMATS = ("mpt", "mpt_comma", "csv")      # one export style per day, to exercise the reader
IR_HW = (0.0, 0.0, 0.85)                   # instrument iR share per day
J_STOP = 30.0                              # sweeps stop above this current density, mA cm-2
PEAK_E, PEAK_W = 1.38, 0.012
CDL_RATES = (0.010, 0.020, 0.040, 0.080)   # V/s
SYN_KEY = dict(zip(CODES, ALLOYS))


def j_model(eta, p, eta10):
    return 10 * 10 ** ((eta - eta10) / p["b"]) + p["peak"] * np.exp(-0.5 * ((eta + E_EQ - PEAK_E) / PEAK_W) ** 2)


def _recorded(E_true, I, day, R_u):
    return E_true + (1 - IR_HW[day]) * I * R_u - OFFSETS[day]


def lsv(p, eta10, day, R_u, rng, rate=0.005):
    E_true = np.arange(1.00, 1.90, 0.0005)
    j = j_model(E_true - E_EQ, p, eta10)
    keep = np.arange(len(j)) <= np.argmax(j > J_STOP) if (j > J_STOP).any() else np.ones(len(j), bool)
    E_true, j = E_true[keep], j[keep]
    I = j * AREA_CM2 / 1e3 * (1 + rng.normal(0, 0.002, len(j)))
    E = _recorded(E_true, I, day, R_u) + rng.normal(0, 5e-5, len(j))
    return {"time/s": (E_true - E_true[0]) / rate, "control/V": E_true - OFFSETS[day], "Ewe/V": E,
            "I/mA": I * 1e3, "cycle number": np.ones(len(j), int)}


def blank_lsv(day, rng):
    E_true = np.arange(1.00, 1.80, 0.0005)
    j = 0.002 + 0.01 * 10 ** ((E_true - E_EQ - 0.55) / 0.12)
    I = j * AREA_CM2 / 1e3
    return {"time/s": (E_true - E_true[0]) / 0.005, "control/V": E_true - OFFSETS[day],
            "Ewe/V": _recorded(E_true, I, day, 5.0) + rng.normal(0, 5e-5, len(j)), "I/mA": I * 1e3,
            "cycle number": np.ones(len(j), int)}


def holds(p, eta10, day, R_u, rng, step_s=120):
    cols = {k: [] for k in ("time/s", "control/V", "Ewe/V", "I/mA", "cycle number")}
    t0 = 0.0
    for eta in np.arange(eta10 - 0.12, eta10 + 0.021, 0.02):
        t = np.arange(0, step_s, 1.0)
        I_ss = 10 * 10 ** ((eta - eta10) / p["b"]) * AREA_CM2 / 1e3
        I = I_ss * (1 + 0.3 * np.exp(-t / 8)) * (1 + rng.normal(0, 0.002, len(t)))
        E_true = E_EQ + eta
        cols["time/s"] += list(t0 + t)
        cols["control/V"] += [E_true - OFFSETS[day]] * len(t)
        cols["Ewe/V"] += list(_recorded(E_true, I, day, R_u) + rng.normal(0, 5e-5, len(t)))
        cols["I/mA"] += list(I * 1e3)
        cols["cycle number"] += [1] * len(t)
        t0 += step_s
    return {k: np.array(v) for k, v in cols.items()}


def cdl_cv(cdl, rate, day, rng, lo=0.95, hi=1.05, cycles=3, n=200):
    up = np.linspace(lo, hi, n, endpoint=False)
    down = np.linspace(hi, lo, n, endpoint=False)
    E_rhe = np.tile(np.concatenate([up, down]), cycles)
    sign = np.tile(np.concatenate([np.ones(n), -np.ones(n)]), cycles)
    I = sign * cdl * rate + 2e-7 * (E_rhe - 1.0) + rng.normal(0, 0.01 * cdl * rate, len(E_rhe))
    t = np.arange(len(E_rhe)) * (hi - lo) / n / rate
    E = E_rhe - OFFSETS[day]
    return {"time/s": t, "control/V": E, "Ewe/V": E + rng.normal(0, 2e-5, len(E)), "I/mA": I * 1e3,
            "cycle number": np.repeat(np.arange(1, cycles + 1), 2 * n)}


def stability(eta10, day, R_u, rng, hours=12.0, dt=60.0):
    t = np.arange(0, hours * 3600 + dt, dt)
    I = np.full(len(t), 10 * AREA_CM2 / 1e3)
    E_true = E_EQ + eta10 + DRIFT_TRUE_MV_H / 3.6e6 * t + rng.normal(0, 3e-4, len(t))
    return {"time/s": t, "control/V": np.full(len(t), 10 * AREA_CM2), "Ewe/V": _recorded(E_true, I, day, R_u),
            "I/mA": I * 1e3, "cycle number": np.ones(len(t), int)}


def write(path, cols, style, title):
    if style != "csv" and title in ("Linear Sweep Voltammetry", "Cyclic Voltammetry"):
        cols = {("<I>/mA" if k == "I/mA" else k): v for k, v in cols.items()}   # EC-Lab's name for sweep currents
    names = list(cols)
    n = len(cols[names[0]])
    if style == "csv":
        names = [c for c in names if c != "control/V"]
        with open(path, "w", newline="") as f:
            f.write(",".join(names) + "\n")
            for i in range(n):
                f.write(",".join(f"{cols[c][i]:.8g}" for c in names) + "\n")
        return
    fmt = (lambda v: f"{v:.8g}".replace(".", ",")) if style == "mpt_comma" else (lambda v: f"{v:.8g}")
    with open(path, "w", newline="\r\n", encoding="latin-1") as f:
        f.write("EC-Lab ASCII FILE\nNb header lines : 4\n" + title + "\n")
        f.write("\t".join(names) + "\n")
        for i in range(n):
            f.write("\t".join(fmt(cols[c][i]) for c in names) + "\n")


def make_campaign(out_dir, seed=7):
    """Three bench days; each day IrO2, a blank, then disk k of every alloy (k = day index + 1), with activation,
    EIS, LSV, holds, C_dl CVs, and on day 1 a 12 h hold on disk 1. Returns the truth used."""
    rng = np.random.default_rng(seed)
    files = os.path.join(out_dir, "files")
    os.makedirs(files, exist_ok=True)
    rows = []

    def add(run_id, cols, style, day, sample, technique, title, **extra):
        ext = "csv" if style == "csv" else "mpt"
        name = f"files/{run_id}.{ext}" if cols is not None else ""
        if cols is not None:
            write(os.path.join(out_dir, name), cols, style, title)
        row = {c: "" for c in MANIFEST_COLUMNS}
        row.update(run_id=run_id, file=name, sample=sample, day=DAYS[day], technique=technique,
                   rhe_offset_V=f"{OFFSETS[day]:.4f}", ir_hw_pct=f"{IR_HW[day] * 100:g}", rpm="1600", status="ok")
        row.update({k: str(v) for k, v in extra.items()})
        rows.append(row)

    truth = {"key": SYN_KEY, "disks": {}, "iro2": {}, "R_u": {}}
    for day in range(len(DAYS)):
        style = FORMATS[day]
        eta_ir = IRO2_TRUTH["eta10"] + IRO2_DAY_SHIFT[day]
        truth["iro2"][DAYS[day]] = eta_ir
        add(f"d{day + 1}_IrO2_lsv", lsv(IRO2_TRUTH, eta_ir, day, 3.0, rng), style, day, "IrO2", "lsv",
            "Linear Sweep Voltammetry", scan_rate_mV_s=5, R_u_ohm=3.0, area_cm2=f"{AREA_CM2:.5f}")
        add(f"d{day + 1}_blank_lsv", blank_lsv(day, rng), style, day, "blank", "lsv", "Linear Sweep Voltammetry",
            scan_rate_mV_s=5, R_u_ohm=5.0)
        k = day + 1
        for code in CODES:
            p = TRUTH[SYN_KEY[code]]
            disk, eta10, R_u = f"{code}{k}", p["eta10"] + (k - 2) * DISK_SD, 4.0 + 0.5 * k
            truth["disks"][disk], truth["R_u"][disk] = eta10, R_u
            add(f"d{k}_{disk}_act", None, style, day, disk, "activation", "")
            add(f"d{k}_{disk}_eis", None, style, day, disk, "eis", "", R_u_ohm=R_u)
            add(f"d{k}_{disk}_lsv", lsv(p, eta10, day, R_u, rng), style, day, disk, "lsv",
                "Linear Sweep Voltammetry", scan_rate_mV_s=5, R_u_ohm=R_u)
            add(f"d{k}_{disk}_hold", holds(p, eta10, day, R_u, rng), style, day, disk, "hold", "Chronoamperometry",
                R_u_ohm=R_u)
            for rate in CDL_RATES:
                add(f"d{k}_{disk}_cdl{rate * 1e3:g}", cdl_cv(p["cdl"], rate, day, rng), style, day, disk, "cdl",
                    "Cyclic Voltammetry", scan_rate_mV_s=f"{rate * 1e3:g}")
            if k == 1:
                add(f"d{k}_{disk}_12h", stability(eta10, day, R_u, rng), style, day, disk, "stability",
                    "Chronopotentiometry", R_u_ohm=R_u)
    with open(os.path.join(out_dir, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
        f.write("# SYNTHETIC campaign from src/echem/s8_oer_synthetic.py: invented values, not measurements\n")
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(out_dir, "key.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed", "synthetic"])
        w.writerow(["code", "alloy", "composition_at_pct", "contains_Cr"])
        for code in CODES:
            w.writerow([code, SYN_KEY[code], "", ""])
    return truth


if __name__ == "__main__":
    make_campaign(sys.argv[1])
    print(f"synthetic campaign -> {sys.argv[1]}")
