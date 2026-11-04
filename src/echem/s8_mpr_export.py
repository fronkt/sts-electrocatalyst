#!/usr/bin/env python3
"""Export BioLogic EC-Lab .mpr files to the CSV tables the S8 readout reads (s8_oer_readout.read_curve).

The values are written unchanged, under EC-Lab's own column names (time/s, control/V, Ewe/V, <I>/mA, cycle number,
Ns, ...). Each export is logged with the source file's SHA-256 in OUT_DIR/export_log.json.

  python src/echem/s8_mpr_export.py OUT_DIR FILE.mpr [FILE.mpr ...]
      one CSV per file, named after it
  python src/echem/s8_mpr_export.py OUT_DIR --concat NAME.csv FILE.mpr [FILE.mpr ...]
      consecutive techniques of one sequence (for example a series of constant-potential holds saved one file per
      step) joined into one table in time order; every file must have the same columns
  python src/echem/s8_mpr_export.py OUT_DIR --window LO HI FILE.mpr [FILE.mpr ...]
      only the rows whose programmed potential (control/V) lies between the CV's programmed vertices LO and HI
      (V vs reference, 1 mV tolerance), written as NAME_window.csv: for a C_dl CV that starts from and returns to open
      circuit, this drops the approach and return legs so the table holds the cycling between the vertices only

Needs galvani (pip install galvani).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys

import numpy as np
from galvani import BioLogic


def _table(path):
    data = BioLogic.MPRfile(path).data
    cols = [c for c in data.dtype.names if c != "flags"]
    return cols, {c: np.asarray(data[c]) for c in cols}


def _write(out_path, cols, arrays):
    n = len(arrays[cols[0]])
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i in range(n):
            w.writerow([repr(float(arrays[c][i])) if arrays[c].dtype.kind == "f" else int(arrays[c][i]) for c in cols])
    return n


def _sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


WINDOW_TOL_V = 0.001


def in_window(arrays, lo, hi, tol=WINDOW_TOL_V):
    """Rows whose programmed potential (control/V) lies in [lo - tol, hi + tol]."""
    if "control/V" not in arrays:
        raise ValueError("--window needs the control/V column")
    c = np.asarray(arrays["control/V"], float)
    keep = (c >= min(lo, hi) - tol) & (c <= max(lo, hi) + tol)
    return {k: v[keep] for k, v in arrays.items()}, int(keep.sum()), int((~keep).sum())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_dir")
    ap.add_argument("--concat", metavar="NAME.csv", help="join the files into one table instead")
    ap.add_argument("--window", nargs=2, type=float, metavar=("LO", "HI"),
                    help="keep only rows with control/V between the programmed vertices LO and HI (V)")
    ap.add_argument("files", nargs="+")
    a = ap.parse_args(argv)
    if a.concat and a.window:
        sys.exit("--concat and --window do not combine")
    os.makedirs(a.out_dir, exist_ok=True)
    log_path = os.path.join(a.out_dir, "export_log.json")
    log = json.load(open(log_path, encoding="utf-8")) if os.path.isfile(log_path) else {}
    if a.concat:
        parts = [(f, *_table(f)) for f in a.files]
        cols = parts[0][1]
        if any(p[1] != cols for p in parts):
            sys.exit(f"--concat: column sets differ: {[p[1] for p in parts]}")
        parts.sort(key=lambda p: float(p[2]["time/s"][0]) if "time/s" in p[2] else 0.0)
        arrays = {c: np.concatenate([p[2][c] for p in parts]) for c in cols}
        out = os.path.join(a.out_dir, a.concat)
        n = _write(out, cols, arrays)
        log[a.concat] = {"sources": [{"file": os.path.basename(p[0]), "sha256": _sha256(p[0])} for p in parts],
                         "rows": n, "columns": cols}
        print(f"{out}: {n} rows from {len(parts)} files")
    else:
        for f in a.files:
            cols, arrays = _table(f)
            stem = os.path.splitext(os.path.basename(f))[0]
            extra = {}
            if a.window:
                arrays, kept, dropped = in_window(arrays, *a.window)
                stem += "_window"
                extra = {"window_control_V": list(a.window), "tolerance_V": WINDOW_TOL_V, "rows_dropped": dropped}
            name = stem + ".csv"
            n = _write(os.path.join(a.out_dir, name), cols, arrays)
            log[name] = {"sources": [{"file": os.path.basename(f), "sha256": _sha256(f)}], "rows": n, "columns": cols,
                         **extra}
            print(f"{name}: {n} rows" + (f" ({extra['rows_dropped']} outside the window dropped)" if extra else ""))
    with open(log_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(log, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
