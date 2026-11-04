#!/usr/bin/env python3
"""Make explicitly simulated LSV/CV sensitivity previews, never native acquisitions.

Reads existing measured CSV/MPR pairs without modifying them. Two deterministic
current scales (0.90 and 1.10) illustrate assumptions, not disk reproducibility.
Requires numpy, matplotlib and galvani in the local electrochemistry environment.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from galvani import BioLogic


ORIGIN = "SIMULATED_NOT_MEASURED"
SCALES = (("ASSUMED_CURRENT_90_PERCENT", 0.90), ("ASSUMED_CURRENT_110_PERCENT", 1.10))
SOURCE_FILES = {
    "A": ("day1_2026-10-24_sampleA/csv",
          "SampleA_EIS-MIR-LSV-2-smallerwindowrepeat2_03_LSV_C01.csv",
          "SampleA_EIS-MIR-LSV-2-smallerwindowrepeat2_02_CV_C01.csv"),
    "B": ("day2_2026-10-30_sampleB_sampleD/csv",
          "SampleB_CVLSV_04_LSV_C01.csv", "SampleB_CVLSV_03_CV_C01.csv"),
    "D": ("day3_2026-11-03_sampleD_E_F/csv/SampleD_New",
          "EISMIRCVLSV_04_LSV_C01.csv", "EISMIRCVLSV_03_CV_C01.csv"),
    "E": ("day3_2026-11-03_sampleD_E_F/csv/SampleE_SameSetup",
          "EISMIRCVLSV_04_LSV_C01.csv", "EISMIRCVLSV_03_CV_C01.csv"),
    "F": ("day3_2026-11-03_sampleD_E_F/csv/SampleF_SameSetup",
          "EISMIRCVLSV_04_LSV_C01.csv", "EISMIRCVLSV_03_CV_C01.csv"),
}
FIELDS = ("data_origin", "reference_sample", "scenario", "technique",
          "reference_csv_row_index_zero_based", "relative_time_s",
          "potential_V_vs_HgHgO", "simulated_current_mA", "assumed_current_scale")
NUMERIC_FIELDS = FIELDS[4:]
COLORS = ("#B76A15", "#007F86")


def sha256(path):
    with path.open("rb") as fh:
        return hashlib.file_digest(fh, "sha256").hexdigest()


def read_source(path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError(f"Empty source: {path}")
    d = {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}
    parts = list(path.parts)
    parts[parts.index("csv")] = "raw"
    native = Path(*parts).with_suffix(".mpr")
    raw = BioLogic.MPRfile(str(native)).data
    columns = ["time/s", "control/V", "Ewe/V", "<I>/mA"]
    if "cycle number" in d:
        columns.append("cycle number")
    for name in columns:
        if not np.array_equal(d[name], raw[name]):
            raise ValueError(f"CSV differs from native data: {path}: {name}")
    return d, native


def select_trace(d, technique):
    control = d["control/V"]
    if technique == "LSV":
        # The first sweep only; later repeats on the same disk are not replicates.
        cuts = np.flatnonzero(np.diff(control) < -0.5) + 1
        stop = int(cuts[0]) if len(cuts) else len(control)
        idx = np.arange(stop)
        if control[idx[-1]] < 0.65 or np.median(np.diff(control[idx])) <= 0:
            raise ValueError("The first LSV sweep is incomplete or not anodic")
        label = "first source sweep"
    else:
        # A closed cycle must return to its starting potential and cover both directions.
        if np.any(np.diff(d["cycle number"]) < 0):
            raise ValueError("CV cycle IDs reset; chronological selection requires review")
        candidates = []
        for cycle in np.unique(d["cycle number"]):
            candidate = np.flatnonzero(d["cycle number"] == cycle)
            c = control[candidate]
            if (len(c) > 100 and abs(c[-1] - c[0]) < 0.005
                    and np.ptp(c) > 1.0 and (np.diff(c) > 0).sum() > 20
                    and (np.diff(c) < 0).sum() > 20):
                candidates.append((cycle, candidate))
        if not candidates:
            raise ValueError("No closed CV cycle in source")
        cycle, idx = candidates[-1]
        label = f"last closed source cycle ({int(cycle)})"
    t = d["time/s"][idx] - d["time/s"][idx[0]]
    if not np.isfinite(np.c_[t, d["Ewe/V"][idx], d["<I>/mA"][idx]]).all():
        raise ValueError("Nonfinite selected source values")
    if np.any(np.diff(t) <= 0):
        raise ValueError("Selected source time is not strictly increasing")
    dt = np.diff(t)
    dc = np.diff(control[idx])
    moving = np.abs(dc) > 1e-5
    return idx, t, label, float(np.median(np.abs(dc[moving] / dt[moving])))


def write_scenario(path, sample, technique, scenario, scale, idx, t, e, current):
    with path.open("x", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(FIELDS)
        writer.writerows((ORIGIN, sample, scenario, technique, int(k), float(tt),
                         float(ee), float(ii * scale), scale)
                        for k, tt, ee, ii in zip(idx, t, e, current))
    # Round-trip the deliverable rather than checking only in-memory arrays.
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != len(idx) or any(r["data_origin"] != ORIGIN for r in rows):
        raise ValueError("Output row count or simulation marker failed")
    numbers = np.array([[float(r[k]) for k in NUMERIC_FIELDS] for r in rows])
    expected = np.c_[idx, t, e, current * scale, np.full(len(t), scale)]
    if not np.isfinite(numbers).all() or not np.array_equal(numbers, expected):
        raise ValueError("Output numeric round-trip failed")


def plot_panel(ax, trace, technique, sample):
    _, _, e, current, label, _ = trace
    for (scenario, scale), color, style in zip(SCALES, COLORS, ("--", ":")):
        ax.plot(e, current * scale, color=color, ls=style, lw=1.4)
    ax.plot(e, current, color="#26323C", lw=1.15)
    ax.set_title(f"Sample {sample} | {technique} | {label}", fontsize=10, loc="left", pad=9)
    ax.text(0.50, 0.50, "SIMULATED SCENARIOS", transform=ax.transAxes,
            ha="center", va="center", rotation=12, color="#934719", alpha=0.17,
            fontsize=16, weight="bold")
    ax.set_xlabel("Exported Ewe (V vs Hg/HgO)", fontsize=9)
    ax.set_ylabel("Current (mA)", fontsize=9)
    ax.grid(color="#DDE1E4", lw=0.6, alpha=0.8)
    ax.axhline(0, color="#8E989F", lw=0.6)
    ax.tick_params(labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#BDC4C9")
    if technique == "LSV":
        ax.set_xlim(0.15, 0.76)
        shown = current[e >= 0.15]
        ax.set_ylim(min(-0.05, float(shown.min()) * 1.2), max(0.1, float(shown.max()) * 1.2))


def finish_figure(fig, axes, traces, samples):
    for row, sample in enumerate(samples):
        for col, technique in enumerate(("LSV", "CV")):
            plot_panel(axes[row, col], traces[(sample, technique)], technique, sample)
    fig.suptitle("LSV / CV sensitivity preview - SIMULATED scenarios", fontsize=16, weight="bold", y=0.988)
    handles = [Line2D([], [], color="#26323C", label="Measured trace (one disk)")]
    handles += [Line2D([], [], color=color, ls=style, label=f"SIMULATED: measured current x {scale:.2f}")
                for (_, scale), color, style in zip(SCALES, COLORS, ("--", ":"))]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.956), ncol=3,
               fontsize=9, frameon=False)
    fig.text(0.5, 0.015,
             "Chosen +/-10% current scales; no estimated disk SD or new experimental disks.\n"
             "Same measured scan grid; LSV panels zoom to the anodic window. No additional RHE/iR correction.",
             ha="center", va="bottom", fontsize=9, color="#444F57")
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.065 if len(samples) > 1 else 0.22,
                        top=0.925 if len(samples) > 1 else 0.81, hspace=0.55, wspace=0.24)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--zip", required=True, type=Path, dest="archive")
    args = ap.parse_args()
    root, out, archive = args.data_root.resolve(), args.out.resolve(), args.archive.resolve()
    if out.is_relative_to(root) or archive.is_relative_to(root) or archive.is_relative_to(out):
        raise ValueError("Preview and archive must be outside measured data; archive outside preview")
    if out.exists() or archive.exists():
        raise FileExistsError("Use new output paths; existing outputs are never overwritten")
    # Hash all raw files and measured CSVs, including files not selected for plotting.
    protected = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in
                 (".mpr", ".mgr", ".mps", ".csv", ".sta", ".mpt")]
    before = {p: sha256(p) for p in protected}
    traces, sources, exports = {}, [], []
    for sample, (folder, lsv_file, cv_file) in SOURCE_FILES.items():
        for technique, name in (("LSV", lsv_file), ("CV", cv_file)):
            source = root / folder / name
            d, raw = read_source(source)
            idx, t, label, rate = select_trace(d, technique)
            e, current = d["Ewe/V"][idx], d["<I>/mA"][idx]
            traces[(sample, technique)] = idx, t, e, current, label, rate
            sources.append({"sample": sample, "technique": technique,
                            "csv": source.relative_to(root).as_posix(), "csv_sha256": before[source],
                            "native_mpr": raw.relative_to(root).as_posix(), "mpr_sha256": before[raw],
                            "selection": label, "selected_rows": len(idx),
                            "median_control_scan_rate_V_per_s": rate,
                            "exported_potential_range_V": [float(e.min()), float(e.max())],
                            "csv_matches_native_time_control_Ewe_current_and_cycle_if_present": True})
    out.mkdir(parents=True, exist_ok=False)
    tables = out / "SIMULATED_CSV"
    tables.mkdir()
    for (sample, technique), (idx, t, e, current, _, _) in traces.items():
        for scenario, scale in SCALES:
            target = tables / f"SIMULATED_{sample}_{technique}_{scenario}.csv"
            write_scenario(target, sample, technique, scenario, scale, idx, t, e, current)
            exports.append({"file": target.relative_to(out).as_posix(), "sha256": sha256(target),
                            "rows": len(idx), "data_origin": ORIGIN, "assumed_current_scale": scale})
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": "white"})
    samples = list(SOURCE_FILES)
    fig, axes = plt.subplots(len(samples), 2, figsize=(13, 17), squeeze=False)
    finish_figure(fig, axes, traces, samples)
    fig.savefig(out / "SIMULATED_LSV_CV_overview.png", dpi=180, facecolor="white")
    fig.savefig(out / "SIMULATED_LSV_CV_overview.pdf", facecolor="white")
    plt.close(fig)
    for sample in samples:
        fig, axes = plt.subplots(1, 2, figsize=(13, 5), squeeze=False)
        finish_figure(fig, axes, traces, [sample])
        fig.savefig(out / f"SIMULATED_{sample}_LSV_CV.png", dpi=180, facecolor="white")
        plt.close(fig)
    changed = [str(p) for p, digest in before.items() if not p.is_file() or sha256(p) != digest]
    if changed:
        raise RuntimeError(f"Measured source files changed during preview: {changed}")
    manifest = {"data_origin": ORIGIN, "experimental_n_per_sample": 1,
                "purpose": "Deterministic visual sensitivity illustration, not predictive replication",
                "model": "I_simulated(t) = assumed_current_scale * I_measured(t)",
                "assumed_scales": [scale for _, scale in SCALES], "estimated_disk_sd": None,
                "random_noise_added": False, "native_acquisition_files_written": False,
                "source_root": str(root), "sources": sources, "exports": exports,
                "verification": {"csv_round_trips_passed": len(exports),
                                 "source_files_hashed_before_after": len(before),
                                 "source_files_changed": 0,
                                 "native_numeric_crosschecks_passed": len(sources)}}
    (out / "SIMULATED_manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (out / "README_SIMULATED.txt").write_text(
        "SIMULATED SENSITIVITY PREVIEW - NOT ADDITIONAL MEASUREMENTS\n\n"
        "Samples A, B, D, E and F: one measured disk each. Each plot overlays that measured\n"
        "trace with two deterministic illustrations: current multiplied by 0.90 and 1.10.\n"
        "These are arbitrary assumptions, not a measured standard deviation, prediction,\n"
        "confidence interval or independent experimental replicate. No noise was added.\n\n"
        "Selection: first LSV sweep and last closed pre-LSV CV cycle in each named source.\n"
        "This is a visual selection for this preview, not a change to the registered analysis.\n"
        "CSV tables contain the whole selected sweep/cycle. LSV plots zoom to 0.15-0.76 V.\n"
        "Time is elapsed from the selected trace start. Exported Ewe vs Hg/HgO is retained;\n"
        "instrument compensation, if present, is inherited without further correction.\n"
        "The scan windows and activation histories differ between samples. These plots\n"
        "are not a standardized activity ranking. Refer to the source manifest.\n\n"
        "Files: 20 explicitly marked CSVs, five per-sample PNGs, an overview PNG/PDF,\n"
        "a provenance/verification manifest and the reproduction script.\n"
        "Native MPR/MGR files were not produced; these are not EC-Lab acquisitions.\n\n"
        "Reproduce in the echem Python environment (numpy, matplotlib, galvani):\n"
        'python s8_simulation_preview.py --data-root <measured-folder> --out <new-folder> --zip <new.zip>\n',
        encoding="utf-8")
    shutil.copy2(Path(__file__), out / "s8_simulation_preview.py")
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(out.rglob("*")):
            if path.is_file():
                zf.write(path, Path(out.name) / path.relative_to(out))
    with zipfile.ZipFile(archive) as zf:
        if zf.testzip() is not None:
            raise RuntimeError("Archive integrity verification failed")
    print(json.dumps({"out": str(out), "zip": str(archive), "csvs": len(exports),
                      "selected_rows_total": sum(x["selected_rows"] for x in sources),
                      "verification": manifest["verification"]}))


if __name__ == "__main__":
    main()
