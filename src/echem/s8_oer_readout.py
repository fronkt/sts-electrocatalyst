#!/usr/bin/env python3
"""S8 electrode readout: from potentiostat files to the registered comparisons (freeze §3 and §6).

COMMITTED BEFORE ANY OER MEASUREMENT OF THE SIX ALLOYS (last recorded status: "Nothing measured yet", lock rule
docs/research/s8-electrode-lock-rule-2026-10-16.md). The freeze fixes the endpoints and the criterion; the operational
choices it leaves open are fixed here and listed in docs/research/s8-oer-analysis-2026-10-19.md. Once data exist,
change this file only to fix a bug, and record each fix with its reason in that document.

INPUT. A run manifest (CSV, one row per potentiostat file; columns in MANIFEST_COLUMNS, every field the technique
needs given explicitly), the files it names (BioLogic EC-Lab .mpt text export, or a CSV/TXT table with time,
potential and current columns), and, to unblind, the private code key. The bench measures coded disks (A1-F3, spares
AS-FS). Without the key the readout stays blinded: everything is reported per code, and nothing that needs an alloy's
identity (K1, K2, the arm comparisons) is computed.

BAD INPUT STOPS THE READOUT. A manifest field missing, an implausible or inconsistent RHE calibration, more than a few
unreadable rows in a file, a file holding more or fewer than one anodic sweep, several linked techniques in one LSV
file, no anodic current, or live iR compensation without a recorded check of how the instrument exports Ewe: each
raises with the run named. A run that genuinely failed is given a non-"ok" status in the manifest (decided blinded),
not left for the code to judge.

WHAT IS COMPUTED, PER RUN.
  Potential: E_RHE = E(Hg/HgO) + that day's calibration (one value per day, 0.85-1.00 V; or 0.098 + 0.059 pH,
    flagged). iR to IR_TOTAL (90%) in all: the code removes (0.90 - instrument share) x I x R_u.
  eta_x (LSV) = E at the LAST upward crossing of x mA cm-2 on the anodic sweep - 1.23 V; a pre-OER redox peak can
    cross first, so the first crossing is reported beside it and flagged when they differ by more than 5 mV. Primary
    x = 10, secondary x = 1 (geometric). A sweep that does not end above x gives no eta_x (reported, never imputed).
  Tafel slope (holds): steady current = mean over the last 20% of each hold of at least 30 s; slope of eta against
    log10 j over the holds between 0.05 and 10 mA cm-2 (at least 3).
  C_dl (non-faradaic CVs): half the anodic - cathodic current at the window's midpoint (inside both branches), against
    scan rate (at least 3 rates, one disk on one day). Roughness factor with C_s = 0.040 mF cm-2, the middle of the
    0.020-0.060 mF cm-2 range used for flat surfaces in alkaline electrolyte (as in arXiv:2102.08062, SI; its primary
    source is still to be confirmed before the report cites one); specific activity = j at eta = 0.35 V divided by
    the roughness factor. Reported only.
  Drift (12 h hold): slope of the iR-corrected potential after the first 10 min, mV/h. Reported only.

WHAT IS JUDGED. Only alloys complete under the lock rule, from runs on or before the lock date, in time order (day,
then manifest row).
  A bench day counts when its first ok IrO2 sweep reaches 10 mA cm-2 and it has an ok blank sweep; that IrO2 sweep is
  the day's reference.
  A disk's primary sweep is its first ok sweep on a counted day; later sweeps are reported, never averaged in.
  An alloy is complete with at least 3 disks that have eta_10, over at least 2 counted days. An incomplete alloy's
  numbers are kept under "kept_not_reported" and nowhere else.
  Criterion (freeze §6): a difference in mean eta_10 counts only if it exceeds twice the pooled disk-to-disk SD. The
  SD is pooled over the complete K-set alloys only, so Ni34 changes no primary test (freeze §2); the same yardstick
  serves every comparison.
  K1 (Cu8 against Ni31 and Fe25), K2 (Cu22 least active of the five K-set alloys), the IrO2 comparison per complete
  alloy (against the reference sweeps of the days its disks were measured), and the exploratory items: each arm's
  leader, Spearman rho of the measured order against each arm, and Ni34's position. Each needs every alloy it involves.

Usage:
  PYTHONPATH=src python src/echem/s8_oer_readout.py --manifest DATA/manifest.csv --lock 2026-10-25 \\
      [--key PATH/key.csv] [--ir-hw-verified "how the export convention was checked"] --out results/s8_oer/readout.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
from datetime import date

import numpy as np
from scipy.stats import spearmanr

REGISTERED_LOCK = "2026-10-25"   # lock rule; a different --lock is reported as such
E_EQ = 1.23                      # V vs RHE
IR_TOTAL = 0.90                  # freeze §6: 90% iR compensation
TARGETS = (10.0, 1.0)            # mA cm-2, primary then secondary
ETA_SPECIFIC = 0.35              # V, the potential at which specific activity is read
CS_F_CM2 = 40e-6                 # F cm-2, flat-surface specific capacitance in alkaline electrolyte (see header)
AREA_CM2 = math.pi * 0.25 ** 2   # 5.00 mm disk face, 0.19635 cm2 (the default for coded disks only)
PH_FORMULA = (0.098, 0.059)      # freeze §6: E_RHE = E_Hg/HgO + 0.098 + 0.059 pH
OFFSET_RANGE = (0.85, 1.00)      # V; 1 M KOH gives about 0.92
TAFEL_WINDOW = (0.05, 10.0)      # mA cm-2
HOLD_TAIL = 0.20
HOLD_MIN_S = 30.0
DRIFT_SKIP_S = 600.0
REDOX_FLAG_V = 0.005
TURN_TOL_V = 0.002               # hysteresis when splitting a potential trace into sweeps
MIN_SWEEP_V = 0.05               # an anodic run shorter than this is not a sweep
MIN_POINTS = 20
MAX_BAD_ROWS = (5, 0.01)         # a file may lose at most max(5, 1%) unreadable rows
CURVE_POINTS = 150               # downsampled sweep kept in the readout for the figure

ALLOYS = ("Cu8", "Ni31", "Fe25", "Cu26", "Ni34", "Cu22")
K_SET = ("Cu8", "Ni31", "Fe25", "Cu26", "Cu22")        # freeze §2: K1 and K2 exclude Ni34
CODES = tuple("ABCDEF")
IRO2, BLANK = "IrO2", "blank"
DISK_RE = re.compile(r"^([A-F])([123S])$")

# Freeze §3 (deposited, 10.5281/zenodo.23327000), predicted eta in V; tests/test_s8_oer_readout.py checks these
# against the freeze document's tables.
PREDICTIONS = {
    "A": {"Cu8": 0.756, "Ni31": 0.440, "Fe25": 0.453, "Cu26": 0.479, "Ni34": 0.726, "Cu22": 0.796},
    "B": {"Cu8": 0.384, "Ni31": 0.473, "Fe25": 0.554, "Cu26": 0.502, "Ni34": 0.739, "Cu22": 0.831},
    "C": {"Cu26": 0.613, "Ni31": 0.934, "Cu22": 0.942, "Ni34": 1.281},
    "C_ext": {"Cu26": 0.613, "Ni31": 0.934, "Cu22": 0.942, "Fe25": 1.152, "Ni34": 1.281},
}
B_INTERVAL = {"Cu8": (0.362, 0.404), "Ni31": (0.440, 0.835), "Fe25": (0.468, 0.834), "Cu26": (0.449, 0.703),
              "Ni34": (0.679, 0.912), "Cu22": (0.797, 0.887)}
ARM_LEADER = {"A": "Ni31", "B": "Cu8"}

TECHNIQUES = ("lsv", "hold", "cdl", "stability", "eis", "activation")
ANALYSED = ("lsv", "hold", "cdl", "stability")
MANIFEST_COLUMNS = ("run_id", "file", "sample", "day", "technique", "scan_rate_mV_s", "rhe_offset_V", "pH",
                    "R_u_ohm", "ir_hw_pct", "area_cm2", "rpm", "cycle", "status", "notes")
COLUMN_NAMES = {   # lower-cased header names accepted for each quantity; current in mA unless CURRENT_IN_A
    "t": ("time/s", "time (s)", "t/s", "t (s)", "time", "elapsed time (s)"),
    "E": ("ewe/v", "ewe (v)", "e/v", "e (v)", "potential/v", "potential (v)", "we(1).potential (v)", "vf"),
    "I": ("<i>/ma", "i/ma", "i (ma)", "current/ma", "current (ma)", "i/a", "i (a)", "current/a", "current (a)",
          "we(1).current (a)", "im"),
    "cycle": ("cycle number", "cycle", "scan"),
    "control": ("control/v", "control (v)"),
    "ns": ("ns",),
}
CURRENT_IN_A = {"i/a", "i (a)", "current/a", "current (a)", "we(1).current (a)", "im"}


class InputError(ValueError):
    """Input the readout refuses to interpret; fix the manifest or the file, or mark the run failed."""


# ------------------------------------------------------------------------------------------------------- reading
def _num(text, comma_decimal):
    text = text.strip()
    try:
        return float(text.replace(",", ".") if comma_decimal else text)
    except ValueError:
        return math.nan


def read_curve(path):
    """Columns t (s), E (V, as recorded against the reference), I (A), and cycle / control / ns when present.
    Rows with an empty or unreadable t, E or I are dropped and counted; more than MAX_BAD_ROWS raises."""
    lines = open(path, "rb").read().decode("latin-1").splitlines()
    if lines and lines[0].startswith("EC-Lab ASCII FILE"):
        m = re.match(r"Nb header lines\s*:\s*(\d+)", lines[1])
        if not m:
            raise InputError(f"{path}: EC-Lab file without 'Nb header lines'")
        head, delim = int(m.group(1)) - 1, "\t"
    else:
        head = next(i for i, line in enumerate(lines) if line.strip() and not line.startswith("#"))
        delim = "\t" if "\t" in lines[head] else (";" if ";" in lines[head] else ",")
    header = [c.strip().lower() for c in lines[head].split(delim)]
    rows = [line.split(delim) for line in lines[head + 1:] if line.strip()]
    if not rows:
        raise InputError(f"{path}: no data rows")
    comma = delim != "," and any("," in cell for cell in rows[0])
    out = {}
    for key, names in COLUMN_NAMES.items():
        name = next((n for n in names if n in header), None)
        if name is None:
            if key in ("t", "E", "I"):
                raise InputError(f"{path}: no {key} column among {header}")
            out[key] = None
            continue
        i = header.index(name)
        out[key] = np.array([_num(r[i], comma) if i < len(r) else math.nan for r in rows])
        if key == "I" and name not in CURRENT_IN_A:
            out[key] = out[key] / 1e3                # mA -> A
    good = np.ones(len(rows), bool)
    for col in out.values():                         # every column used, optional ones included
        if col is not None:
            good &= np.isfinite(col)
    bad = int((~good).sum())
    if bad > max(MAX_BAD_ROWS[0], MAX_BAD_ROWS[1] * len(good)):
        raise InputError(f"{path}: {bad} of {len(good)} rows have an empty or unreadable value")
    for key in COLUMN_NAMES:
        if out[key] is not None:
            out[key] = out[key][good]
    if out["cycle"] is not None:
        out["cycle"] = out["cycle"].astype(int)
    out["rows_dropped"] = bad
    return out


def read_manifest(path):
    text = open(path, encoding="utf-8-sig").read().splitlines()
    comments = [line for line in text if line.startswith("#")]
    rows = list(csv.DictReader([line for line in text if not line.startswith("#")]))
    missing = [c for c in MANIFEST_COLUMNS if rows and c not in rows[0]]
    if missing:
        raise InputError(f"{path}: manifest lacks columns {missing}")
    seen, out = set(), []
    for n, r in enumerate(rows, 1):
        r = {k: (v or "").strip() for k, v in r.items()}
        where = f"{path} row {n} ({r['run_id']})"

        def need(field, why):
            if not r[field]:
                raise InputError(f"{where}: {field} is required ({why})")
            return r[field]
        if r["run_id"] in seen:
            raise InputError(f"{where}: duplicate run_id")
        seen.add(r["run_id"])
        if r["technique"] not in TECHNIQUES:
            raise InputError(f"{where}: technique {r['technique']!r} not in {TECHNIQUES}")
        if not (DISK_RE.match(r["sample"]) or r["sample"] in (IRO2, BLANK)):
            raise InputError(f"{where}: sample {r['sample']!r} is not a disk code, {IRO2} or {BLANK}")
        try:
            day = date.fromisoformat(r["day"]).isoformat()
        except ValueError:
            raise InputError(f"{where}: day {r['day']!r} is not YYYY-MM-DD") from None
        status = need("status", "'ok', or the reason the run fails a check").lower()
        rec = dict(run_id=r["run_id"], file=r["file"], sample=r["sample"], day=day, technique=r["technique"],
                   status=status, ok=status == "ok", notes=r["notes"], order=n,
                   rpm=float(r["rpm"]) if r["rpm"] else None,
                   cycle=int(r["cycle"]) if r["cycle"] else None,
                   scan_rate=float(r["scan_rate_mV_s"]) / 1e3 if r["scan_rate_mV_s"] else None)
        if r["technique"] in ANALYSED:
            need("file", "an analysed technique")
            if r["area_cm2"]:
                rec["area"] = float(r["area_cm2"])
            elif r["sample"] == IRO2:
                raise InputError(f"{where}: area_cm2 is required for the lab's IrO2 electrode")
            else:
                rec["area"] = AREA_CM2
            if r["rhe_offset_V"]:
                rec["offset"], rec["offset_source"] = float(r["rhe_offset_V"]), "measured"
            elif r["pH"]:
                rec["offset"], rec["offset_source"] = PH_FORMULA[0] + PH_FORMULA[1] * float(r["pH"]), "pH formula"
            else:
                raise InputError(f"{where}: rhe_offset_V or pH is required")
            if not OFFSET_RANGE[0] <= rec["offset"] <= OFFSET_RANGE[1]:
                raise InputError(f"{where}: RHE offset {rec['offset']:.4f} V outside {OFFSET_RANGE}")
        if r["technique"] in ("lsv", "hold", "stability"):
            rec["R_u"] = float(need("R_u_ohm", "iR correction"))
            rec["ir_hw"] = float(need("ir_hw_pct", "write 0 if the instrument compensated nothing live")) / 100
            if not 0 <= rec["ir_hw"] <= IR_TOTAL:
                raise InputError(f"{where}: instrument iR share {rec['ir_hw']:.2f} outside 0-{IR_TOTAL}")
        if r["technique"] == "cdl" and rec["scan_rate"] is None:
            raise InputError(f"{where}: cdl run without scan_rate_mV_s")
        out.append(rec)
    offsets = {}
    for rec in out:
        if "offset" in rec:
            offsets.setdefault(rec["day"], set()).add(round(rec["offset"], 4))
    for day, vals in offsets.items():
        if len(vals) > 1:
            raise InputError(f"{path}: day {day} has {len(vals)} RHE calibrations {sorted(vals)}; one per day")
    return out, any("SYNTHETIC" in c for c in comments)


def read_key(path):
    """The private code key: optional leading lines, then code,alloy,... rows."""
    rows = [r for r in csv.reader(open(path, encoding="utf-8")) if r]
    h = next(i for i, r in enumerate(rows) if r[0] == "code")
    key = {r[0]: r[1] for r in rows[h + 1:]}
    if sorted(key) != list(CODES) or sorted(key.values()) != sorted(ALLOYS):
        raise InputError(f"{path}: key must map A-F one to one onto {ALLOYS}")
    return key


# ------------------------------------------------------------------------------------------------------- per run
def _corrected(curve, run):
    """iR-corrected E vs RHE (V) and j (mA cm-2)."""
    E = curve["E"] + run["offset"] - (IR_TOTAL - run.get("ir_hw", 0.0)) * curve["I"] * run.get("R_u", 0.0)
    return E, curve["I"] * 1e3 / run["area"]


def _cycle_index(curve, cycle):
    idx = np.arange(len(curve["E"]))
    if curve["cycle"] is None:
        if cycle is not None:
            raise InputError(f"cycle {cycle} requested but the file has no cycle column")
        return idx
    want = cycle if cycle is not None else int(curve["cycle"].max())
    idx = idx[curve["cycle"] == want]
    if not len(idx):
        raise InputError(f"no cycle {want}")
    return idx


def sweeps(x, tol=TURN_TOL_V):
    """Monotonic runs of x between turning points found with hysteresis tol: [(i0, i1, +1 or -1)]."""
    out, i0, ext, d = [], 0, 0, 0
    for i in range(1, len(x)):
        if d == 0:
            if abs(x[i] - x[i0]) > tol:
                d, ext = (1 if x[i] > x[i0] else -1), i
        elif d * (x[i] - x[ext]) >= 0:
            ext = i
        elif d * (x[ext] - x[i]) > tol:
            out.append((i0, ext, d))
            i0, d, ext = ext, -d, i
    if d:
        out.append((i0, ext, d))
    return out


def anodic_sweep(curve, cycle=None):
    """Indices of the one anodic sweep in the selected cycle; anything else raises."""
    if curve["ns"] is not None and len(np.unique(curve["ns"])) > 1:
        raise InputError("several linked techniques (Ns) in one file; export the LSV alone")
    idx = _cycle_index(curve, cycle)
    drive = (curve["control"] if curve["control"] is not None else curve["E"])[idx]
    ups = [(a, b) for a, b, d in sweeps(drive) if d == 1 and drive[b] - drive[a] > MIN_SWEEP_V]
    if len(ups) != 1:
        raise InputError(f"{len(ups)} anodic sweeps in the selected data; export one sweep or give its cycle")
    sel = idx[ups[0][0]:ups[0][1] + 1]
    if len(sel) < MIN_POINTS:
        raise InputError(f"anodic sweep has {len(sel)} points")
    return sel


def crossings(x, y, level):
    """y at the first and at the last upward crossing of x through level, linearly interpolated. The last one is
    None unless x ends above level (a crossing the sweep later falls back from is not sustained)."""
    above = x >= level
    ups = np.flatnonzero(~above[:-1] & above[1:])
    if not len(ups):
        return None, None

    def at(k):
        return float(y[k] + (level - x[k]) * (y[k + 1] - y[k]) / (x[k + 1] - x[k]))
    return at(ups[0]), (at(ups[-1]) if above[-1] else None)


def lsv_endpoints(curve, run):
    sel = anodic_sweep(curve, run["cycle"])
    E, j = _corrected(curve, run)
    E, j = E[sel], j[sel]
    if j.max() <= 0:
        raise InputError("no anodic (positive) current in the sweep; check the export's sign convention")
    out = {"rows_dropped": curve["rows_dropped"]}
    for target in TARGETS:
        first, last = crossings(j, E, target)
        tag = f"{target:g}"
        out[f"eta_{tag}_V"] = None if last is None else last - E_EQ
        out[f"eta_{tag}_first_V"] = None if first is None else first - E_EQ
        out[f"redox_flag_{tag}"] = bool(first is not None and last is not None and last - first > REDOX_FLAG_V)
    out["j_at_eta_specific_mA_cm2"] = crossings(E, j, E_EQ + ETA_SPECIFIC)[1]
    out["eta_max_V"] = float(E.max() - E_EQ)
    out["j_max_mA_cm2"] = float(j.max())
    keep = np.unique(np.linspace(0, len(E) - 1, min(CURVE_POINTS, len(E))).astype(int))
    out["curve"] = {"eta_V": [round(float(v), 5) for v in E[keep] - E_EQ],
                    "j_mA_cm2": [round(float(v), 5) for v in j[keep]]}
    return out


def hold_steps(curve):
    """(mean E, mean I) over the last HOLD_TAIL of each constant-potential step lasting at least HOLD_MIN_S."""
    key, tol = (curve["control"], 1e-3) if curve["control"] is not None else (curve["E"], 5e-3)
    segments = np.split(np.arange(len(key)), np.flatnonzero(np.abs(np.diff(key)) > tol) + 1)
    steps = []
    for s in segments:
        t = curve["t"][s]
        if t[-1] - t[0] < HOLD_MIN_S:
            continue
        tail = s[t >= t[-1] - HOLD_TAIL * (t[-1] - t[0])]
        steps.append((float(curve["E"][tail].mean()), float(curve["I"][tail].mean())))
    return steps


def tafel(curve, run):
    pts = []
    for E, I in hold_steps(curve):
        j = I * 1e3 / run["area"]
        if TAFEL_WINDOW[0] <= j <= TAFEL_WINDOW[1]:
            eta = E + run["offset"] - (IR_TOTAL - run["ir_hw"]) * I * run["R_u"] - E_EQ
            pts.append((math.log10(j), eta))
    if len(pts) < 3:
        return {"tafel_mV_dec": None, "tafel_points": len(pts)}
    x, y = np.array(pts).T
    slope, icpt = np.polyfit(x, y, 1)
    return {"tafel_mV_dec": float(slope * 1e3), "tafel_r2": _r2(x, y, slope, icpt), "tafel_points": len(pts)}


def _r2(x, y, slope, icpt):
    ss = float(np.sum((y - y.mean()) ** 2))
    return 1 - float(np.sum((y - (slope * x + icpt)) ** 2)) / ss if ss > 0 else None


def cdl_point(curve, run):
    """Half the anodic - cathodic current (A) at the midpoint of the CV window, or None (with the reason) when either
    branch does not span the midpoint."""
    if curve["ns"] is not None and len(np.unique(curve["ns"])) > 1:
        raise InputError("several linked techniques (Ns) in one C_dl file; export one CV per scan rate")
    idx = _cycle_index(curve, run["cycle"])
    drive = curve["control"] if curve["control"] is not None else curve["E"]
    E, I, d = curve["E"][idx], curve["I"][idx], np.sign(np.gradient(drive[idx]))
    mid = (E.min() + E.max()) / 2
    branch = []
    for sign in (1, -1):
        m = d == sign
        if m.sum() < 3 or not E[m].min() < mid < E[m].max():
            return {"cdl_half_delta_I_A": None, "cdl_note": "a branch does not span the window midpoint"}
        order = np.argsort(E[m])
        branch.append(float(np.interp(mid, E[m][order], I[m][order])))
    return {"cdl_half_delta_I_A": (branch[0] - branch[1]) / 2}


def cdl_fit(points):
    """points = [(scan rate V/s, half current difference A)]; C_dl in F."""
    points = [(v, di) for v, di in points if di is not None]
    rates = sorted({v for v, _ in points})
    if len(rates) < 3:
        return {"cdl_F": None, "cdl_rates": len(rates)}
    v, di = np.array(points).T
    slope, icpt = np.polyfit(v, di, 1)
    return {"cdl_F": float(slope), "cdl_r2": _r2(v, di, slope, icpt), "cdl_rates": len(rates)}


def drift(curve, run):
    E, _ = _corrected(curve, run)
    t = curve["t"] - curve["t"][0]
    m = t >= DRIFT_SKIP_S
    if m.sum() < 3:
        return {"drift_mV_h": None, "hold_h": float(t[-1] / 3600)}
    slope = np.polyfit(t[m], E[m], 1)[0]
    return {"drift_mV_h": float(slope * 3.6e6), "hold_h": float(t[-1] / 3600)}


# ------------------------------------------------------------------------------------------------------- judging
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def _sd(xs):
    xs = [x for x in xs if x is not None]
    return float(np.std(xs, ddof=1)) if len(xs) > 1 else None


def pooled_sd(groups):
    """Pooled SD over groups of replicate values: sqrt(sum (n-1) s^2 / sum (n-1))."""
    for g in groups:
        if not all(math.isfinite(v) for v in g):
            raise InputError(f"non-finite value in a pooled group {g}")
    num = sum((len(g) - 1) * np.var(g, ddof=1) for g in groups if len(g) > 1)
    df = sum(len(g) - 1 for g in groups if len(g) > 1)
    return (float(math.sqrt(num / df)) if df else None), df


def compare(mean_x, mean_y, threshold):
    """'lower' / 'higher' when mean eta of x is below / above y's by more than threshold, else not distinguishable.
    Lower eta = more active."""
    if not all(v is not None and math.isfinite(v) for v in (mean_x, mean_y, threshold)):
        raise InputError(f"compare needs finite values, got {mean_x}, {mean_y}, {threshold}")
    d = mean_x - mean_y
    return "lower" if d < -threshold else "higher" if d > threshold else "not_distinguishable"


def classify_k1(means, threshold):
    vs = {other: compare(means["Cu8"], means[other], threshold) for other in ("Ni31", "Fe25")}
    if all(c == "lower" for c in vs.values()):
        cls = "B-consistent"
    elif all(c == "higher" for c in vs.values()):
        cls = "A-consistent"
    else:
        cls = "mixed_or_unresolved"
    return {"class": cls, "Cu8_vs": vs}


def classify_k2(means, threshold):
    vs = {other: compare(means["Cu22"], means[other], threshold) for other in K_SET if other != "Cu22"}
    if all(c == "higher" for c in vs.values()):
        cls = "supported"
    elif any(c == "lower" for c in vs.values()):
        cls = "contradicted"
    else:
        cls = "unresolved"
    return {"class": cls, "Cu22_vs": vs}


def exploratory(means, threshold):
    out = {}
    if all(a in means for a in ALLOYS):
        order = sorted(ALLOYS, key=lambda a: means[a])
        leader, second = order[0], order[1]
        out["measured_order"] = order
        out["measured_leader"] = leader
        out["leader_distinguishable"] = compare(means[leader], means[second], threshold) == "lower"
        out["arm_leaders"] = {arm: {"predicted": a, "measured_first": a == leader,
                                    "distinguishably_first": a == leader and out["leader_distinguishable"]}
                              for arm, a in ARM_LEADER.items()}
        out["Ni34_position"] = order.index("Ni34") + 1
    rho = {}
    for arm, pred in PREDICTIONS.items():
        names = sorted(pred)
        if all(a in means for a in names):
            r = float(spearmanr([pred[a] for a in names], [means[a] for a in names])[0])
            rho[arm] = {"rho": r if math.isfinite(r) else None, "n": len(names)}
        else:
            rho[arm] = {"rho": None, "n": len(names), "missing": [a for a in names if a not in means]}
    out["spearman"] = rho
    return out


# ------------------------------------------------------------------------------------------------------- readout
def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run_endpoints(run, base):
    """Endpoints of one ok run, by technique; techniques with nothing to compute return {}."""
    if run["technique"] not in ANALYSED:
        return {}
    curve = read_curve(os.path.join(base, run["file"]))
    if run["technique"] == "lsv":
        return lsv_endpoints(curve, run)
    if run["technique"] == "hold":
        return tafel(curve, run)
    if run["technique"] == "stability":
        return drift(curve, run)
    return cdl_point(curve, run)


GROUP_STATS = ("eta_10_V", "eta_10_mean_V", "eta_10_sd_V", "eta_1_mean_V", "tafel_mV_dec_mean", "cdl_F_mean",
               "specific_activity_mean_mA_cm2", "drift_mV_h")


def _group(disks, code):
    counted = [d for d in disks.values() if d["alloy_code"] == code and d.get("eta_10_V") is not None]
    days = sorted({d["day"] for d in counted})
    eta = [d["eta_10_V"] for d in counted]
    stats = {"eta_10_V": eta, "eta_10_mean_V": _mean(eta), "eta_10_sd_V": _sd(eta),
             "eta_1_mean_V": _mean([d.get("eta_1_V") for d in counted]),
             "tafel_mV_dec_mean": _mean([d.get("tafel_mV_dec") for d in counted]),
             "cdl_F_mean": _mean([d.get("cdl_F") for d in counted]),
             "specific_activity_mean_mA_cm2": _mean([d.get("specific_activity_mA_cm2") for d in counted]),
             "drift_mV_h": [d["drift_mV_h"] for d in counted if d.get("drift_mV_h") is not None]}
    g = {"disks": [d["code"] for d in counted], "n": len(counted), "days": days,
         "complete": len(counted) >= 3 and len(days) >= 2,
         "no_eta10_disks": [d["code"] for d in disks.values() if d["alloy_code"] == code
                            and d["primary_run"] and d.get("eta_10_V") is None]}
    if g["complete"]:
        g.update(stats)
    else:                                                     # lock rule 3: kept, dated, not reported
        g.update({k: None for k in GROUP_STATS}, kept_not_reported=stats)
    return g


def readout(manifest, lock, key_path=None, ir_hw_verified=None):
    lock = date.fromisoformat(lock).isoformat()
    runs, synthetic = read_manifest(manifest)
    runs.sort(key=lambda r: (r["day"], r["order"]))
    base = os.path.dirname(os.path.abspath(manifest))
    for run in runs:
        run["after_lock"] = run["day"] > lock
        run["used"] = run["ok"] and not run["after_lock"]
        if run["used"] and run.get("ir_hw", 0) > 0 and not ir_hw_verified:
            raise InputError(f"{run['run_id']}: live iR compensation ({run['ir_hw']:.0%}) is only corrected right if "
                             "the exported Ewe excludes it; record how that was checked with --ir-hw-verified")
        if run["ok"]:
            path = os.path.join(base, run["file"])
            run["sha256"] = sha256(path) if run["file"] and os.path.isfile(path) else None
            try:
                run.update(run_endpoints(run, base))
            except InputError as e:
                raise InputError(f"{run['run_id']} ({run['file']}): {e}") from None
    usable = [r for r in runs if r["used"]]

    days, reference = {}, {}
    for d in sorted({r["day"] for r in usable}):
        iro2 = [r for r in usable if r["day"] == d and r["sample"] == IRO2 and r["technique"] == "lsv"]
        blank = [r for r in usable if r["day"] == d and r["sample"] == BLANK and r["technique"] == "lsv"]
        ref = iro2[0] if iro2 and iro2[0].get("eta_10_V") is not None else None
        days[d] = {"iro2_sweeps": len(iro2), "blank_sweeps": len(blank), "reference_run": ref and ref["run_id"],
                   "counted": bool(ref and blank)}
        if ref:
            reference[d] = ref

    disks = {}
    for code in sorted({r["sample"] for r in runs if DISK_RE.match(r["sample"])}):
        mine = [r for r in usable if r["sample"] == code]
        sweeps_ = [r for r in mine if r["technique"] == "lsv" and days.get(r["day"], {}).get("counted")]
        primary = sweeps_[0] if sweeps_ else None
        disk = {"code": code, "alloy_code": code[0], "primary_run": primary and primary["run_id"],
                "day": primary and primary["day"], "repeat_runs": [r["run_id"] for r in sweeps_[1:]]}
        if primary:
            for k in ("eta_10_V", "eta_1_V", "eta_10_first_V", "eta_1_first_V", "redox_flag_10", "redox_flag_1",
                      "j_at_eta_specific_mA_cm2", "eta_max_V", "rows_dropped"):
                disk[k] = primary.get(k)
            disk["curve"] = primary["curve"]
        holds = [r for r in mine if r["technique"] == "hold"]
        if holds:
            disk.update({k: holds[0].get(k) for k in ("tafel_mV_dec", "tafel_r2", "tafel_points")})
            disk["tafel_run"] = holds[0]["run_id"]
        cdl_days = sorted({r["day"] for r in mine if r["technique"] == "cdl"})
        if cdl_days:
            cday = disk["day"] if disk["day"] in cdl_days else cdl_days[0]
            fit = cdl_fit([(r["scan_rate"], r["cdl_half_delta_I_A"]) for r in mine
                           if r["technique"] == "cdl" and r["day"] == cday])
            disk.update(fit, cdl_day=cday)
            if fit["cdl_F"] and fit["cdl_F"] > 0:
                area = primary["area"] if primary else AREA_CM2
                rf = fit["cdl_F"] / (CS_F_CM2 * area)
                disk["roughness_factor"] = rf
                j = disk.get("j_at_eta_specific_mA_cm2")
                disk["specific_activity_mA_cm2"] = j / rf if j is not None else None
        stab = [r for r in mine if r["technique"] == "stability"]
        if stab:
            disk.update({k: stab[0].get(k) for k in ("drift_mV_h", "hold_h")}, stability_run=stab[0]["run_id"])
        disks[code] = disk

    groups = {c: _group(disks, c) for c in CODES}
    result = {
        "schema": "s8-oer-readout/1", "synthetic": synthetic, "lock_date": lock, "registered_lock": REGISTERED_LOCK,
        "lock_is_registered": lock == REGISTERED_LOCK, "ir_hw_verified": ir_hw_verified,
        "manifest": {"path": os.path.abspath(manifest), "sha256": sha256(manifest)},
        "parameters": {"E_eq_V": E_EQ, "ir_total": IR_TOTAL, "targets_mA_cm2": list(TARGETS),
                       "eta_specific_V": ETA_SPECIFIC, "C_s_F_cm2": CS_F_CM2, "default_area_cm2": AREA_CM2,
                       "tafel_window_mA_cm2": list(TAFEL_WINDOW), "hold_tail": HOLD_TAIL, "hold_min_s": HOLD_MIN_S,
                       "drift_skip_s": DRIFT_SKIP_S, "redox_flag_V": REDOX_FLAG_V},
        "days": days,
        "runs": [{k: v for k, v in r.items() if k != "curve"} for r in runs],
        "disks": disks,
        "iro2_runs": [{"run_id": r["run_id"], "day": d, "eta_10_V": r["eta_10_V"], "eta_1_V": r.get("eta_1_V"),
                       "j_at_eta_specific_mA_cm2": r.get("j_at_eta_specific_mA_cm2"), "curve": r["curve"]}
                      for d, r in reference.items() if days[d]["counted"]],
        "predictions": {"values_V": PREDICTIONS, "B_interval_V": B_INTERVAL},
    }

    def judge(names_by_code, pool_codes):
        sd_p, df = pooled_sd([groups[c]["eta_10_V"] for c in pool_codes])
        threshold = 2 * sd_p if sd_p is not None else None
        for c, g in groups.items():
            if g["complete"]:
                ref = [reference[d] for d in g["days"]]
                ir = _mean([r["eta_10_V"] for r in ref])
                g["iro2"] = {"runs": [r["run_id"] for r in ref], "eta_10_mean_V": ir,
                             "class": compare(g["eta_10_mean_V"], ir, threshold) if threshold is not None else None}
        return {"rule": "difference in mean eta_10 > 2 x pooled disk-to-disk SD (freeze §6)",
                "pooled_over": [names_by_code[c] for c in pool_codes], "pooled_sd_V": sd_p, "df": df,
                "threshold_V": threshold}, threshold

    if key_path is None:
        crit, _ = judge({c: c for c in CODES}, [c for c in CODES if groups[c]["complete"]])
        crit["note"] = ("blinded: pooled over every complete code; the keyed readout pools the complete K-set alloys "
                        "only (freeze §2), so blinded classes are provisional")
        result.update(blinded=True, criterion=crit, codes=groups, k1=None, k2=None, exploratory=None)
        return result

    key = read_key(key_path)
    code_of = {a: c for c, a in key.items()}
    crit, threshold = judge(key, [code_of[a] for a in K_SET if groups[code_of[a]]["complete"]])
    alloys = {a: dict(groups[code_of[a]], code=code_of[a]) for a in ALLOYS}
    means = {a: g["eta_10_mean_V"] for a, g in alloys.items() if g["complete"]}
    ok = threshold is not None
    result.update(
        blinded=False, key={"sha256": sha256(key_path)}, criterion=crit, alloys=alloys,
        k1=(classify_k1(means, threshold) if ok and all(a in means for a in ("Cu8", "Ni31", "Fe25"))
            else {"class": "not_evaluated", "needs": ["Cu8", "Ni31", "Fe25"]}),
        k2=(classify_k2(means, threshold) if ok and all(a in means for a in K_SET)
            else {"class": "not_evaluated", "needs": list(K_SET)}),
        exploratory=exploratory(means, threshold) if ok else None)
    return result


def _clean(x):
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        x = x.item()
    if isinstance(x, float) and not math.isfinite(x):
        raise InputError("non-finite number in the readout")
    return x


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--lock", required=True, help="data lock date, YYYY-MM-DD (runs after it are not used)")
    ap.add_argument("--key", help="private code key; omit for a blinded readout")
    ap.add_argument("--ir-hw-verified", help="how the instrument's Ewe export under live iR compensation was checked")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = _clean(readout(a.manifest, a.lock, a.key, a.ir_hw_verified))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
        f.write("\n")
    groups = res.get("codes") or res.get("alloys")
    done = [c for c, g in groups.items() if g["complete"]]
    print(f"{'BLINDED ' if res['blinded'] else ''}readout -> {a.out}; complete: {done or 'none'}; "
          f"threshold {res['criterion']['threshold_V']}")
    if not res["lock_is_registered"]:
        print(f"NOTE: lock {res['lock_date']} is not the registered {REGISTERED_LOCK}")
    for c, g in groups.items():
        if g["no_eta10_disks"]:
            print(f"NOTE: {c}: disks without eta_10 (sweep never reached 10 mA cm-2): {g['no_eta10_disks']}")
    if not res["blinded"]:
        print(f"K1 {res['k1']['class']}; K2 {res['k2']['class']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
