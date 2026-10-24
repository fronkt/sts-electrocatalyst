"""S8 SEM-EDS readout of the six alloys (Fort Wayne Metals Phenom, 2026-10-23, 15 kV spot analyses).

Usage: python src/scripts/s8_sem_eds_readout.py "D:\\STS Electrocatalyst EDS & SEM" [--out results/s8_sem_eds_2026-10-23]

1. Spot table: metals-only renormalization (C and O dropped), compared with the weigh-sheet nominal at.%.
2. Ni check: Gaussian least-squares fit of the K lines in 5.6-9.3 keV, to test whether the Ni the
   software reports in Cu-rich spots of Ni-free alloys is a real Ni K-alpha peak.
3. BSE area fractions (multi-Otsu, pores excluded) and lever-rule bulk estimates from the spot phases.

Record: docs/research/s8-sem-eds-record-2026-10-23.md. The raw files stay outside the repo.
"""
import argparse
import csv
import glob
import json
import os

import numpy as np
from PIL import Image
from skimage.filters import threshold_multiotsu

NOMINAL = {  # weigh sheet 2026-10-08 (exact at.% of r4_gated.json)
    "149": ("Cu8", {"Cu": 7.887, "Cr": 22.634, "Mn": 34.993, "Co": 34.485}),
    "150": ("Cu26", {"Cu": 25.780, "Ni": 9.393, "Cr": 31.466, "Co": 33.362}),
    "151": ("Fe25", {"Fe": 25.0, "Co": 25.0, "Ni": 25.0, "Cr": 25.0}),
    "152": ("Ni34", {"Ni": 33.877, "Fe": 5.962, "Cu": 29.423, "Co": 30.738}),
    "153": ("Cu22", {"Cu": 22.116, "Fe": 29.974, "Co": 32.425, "Mn": 15.484}),
    "154": ("Ni31", {"Ni": 31.115, "Cr": 29.187, "Cu": 5.169, "Mn": 34.529}),
}
METALS = ["Cr", "Mn", "Fe", "Co", "Ni", "Cu"]
LINES = {  # keV
    "Mn Ka": 5.899, "Cr Kb": 5.947, "Fe Ka": 6.404, "Mn Kb": 6.490, "Co Ka": 6.930, "Fe Kb": 7.058,
    "Ni Ka": 7.478, "Co Kb": 7.649, "Cu Ka": 8.048, "Ni Kb": 8.265, "Cu Kb": 8.905, "Cu Ka esc": 8.048 - 1.740,
}
TOL = 2.0  # freeze §5, at.%


def read_spot(path):
    raw = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            raw[row["Element symbol"]] = 100 * float(row["Atomic concentration percentage"])
    tot = sum(v for k, v in raw.items() if k in METALS)
    met = {k: 100 * raw.get(k, 0.0) / tot for k in METALS}
    other = {k: v for k, v in raw.items() if k not in METALS and v > 0}
    return met, other


def read_emsa(path):
    hdr, y = {}, []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                k, _, v = line[1:].partition(":")
                hdr[k.strip()] = v.strip()
            elif line.strip():
                y.append(float(line.strip().rstrip(",")))
    y = np.array(y)
    x = (float(hdr["OFFSET"]) + float(hdr["XPERCHAN"]) * np.arange(len(y))) / 1000.0
    return x, y


def fwhm(e):  # keV; 129 eV at Mn Ka (file header), Fano scaling
    return np.sqrt(0.129 ** 2 + 2.39e-3 * (e - 5.895))


def fit_lines(path):
    """Net peak areas (counts) from a weighted linear fit: linear background + one Gaussian per line."""
    x, y = read_emsa(path)
    w = (x > 5.6) & (x < 9.3)
    xx, yy = x[w], y[w]
    cols, names = [np.ones_like(xx), xx - 7.4], ["bg0", "bg1"]
    for n, e in LINES.items():
        cols.append(np.exp(-0.5 * ((xx - e) / (fwhm(e) / 2.3548)) ** 2))
        names.append(n)
    A = np.stack(cols, 1)
    wt = 1 / np.sqrt(np.maximum(yy, 1))
    Aw = A * wt[:, None]
    coef, *_ = np.linalg.lstsq(Aw, yy * wt, rcond=None)
    chi2 = float(np.sum((yy * wt - Aw @ coef) ** 2) / (len(yy) - len(coef)))
    cov = np.linalg.inv(Aw.T @ Aw) * chi2
    dx = x[1] - x[0]
    scale = {n: fwhm(e) / 2.3548 * np.sqrt(2 * np.pi) / dx for n, e in LINES.items()}
    area = {n: float(coef[names.index(n)] * scale[n]) for n in LINES}
    err = {n: float(np.sqrt(cov[names.index(n), names.index(n)]) * scale[n]) for n in LINES}
    return area, err, chi2


def phase_fractions(path, classes):
    im = np.asarray(Image.open(path).convert("L"), dtype=float)
    im = im[: int(im.shape[0] * 0.94)]  # drop the data bar
    pores = im < 40
    v = im[~pores]
    th = threshold_multiotsu(v.astype(np.uint8), classes=classes)
    lab = np.digitize(v, th)
    return [float(np.mean(lab == k)) for k in range(classes)], float(pores.mean())


def lever(phases, fracs):
    return {m: float(sum(f * ph[m] for ph, f in zip(phases, fracs))) for m in METALS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", default="results/s8_sem_eds_2026-10-23")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    spots = []
    for q in sorted(glob.glob(os.path.join(args.root, "EDS", "*", "export", "*", "quantification.csv"))):
        parts = q.split(os.sep)
        met, other = read_spot(q)
        area, err, chi2 = fit_lines(os.path.join(os.path.dirname(q), "spectrum.emsa"))
        spots.append(dict(sample=parts[-4].split()[0], folder=parts[-4], analysis=parts[-2], met=met, other=other,
                          ni_ka=area["Ni Ka"], ni_ka_err=err["Ni Ka"], cu_ka=area["Cu Ka"], fit_chi2r=chi2))

    print("=== Spots, metals-only at.% (C/O dropped; non-metals raw at.%); fitted Ni Ka net counts")
    for s in spots:
        print(f"{s['folder']:10s} {s['analysis']:24s} " + " ".join(f"{m} {s['met'][m]:5.1f}" for m in METALS)
              + f" | NiKa {s['ni_ka']:7.0f}+-{s['ni_ka_err']:5.0f} | " + ", ".join(f"{k} {v:.1f}" for k, v in s["other"].items()))

    def sp(folder, an):
        return next(s["met"] for s in spots if s["folder"] == folder and s["analysis"] == an)

    # Ni reported where no Ni Ka peak exists (Cu-rich spots of the Ni-free Cu8 and Cu22): its share of Cu+Ni
    art = [sp(f, a) for f, a in (("149 EDS", "Image 1_analysis_1_spot"), ("153 EDS", "Image 1_analysis_2_spot"))]
    a_art = float(np.mean([m["Ni"] / (m["Ni"] + m["Cu"]) for m in art]))
    print(f"\nNi artifact share of the Cu signal (Ni-free Cu-rich spots): {a_art:.3f}")

    single = {}
    for sample in ("151", "152"):
        name, nom = NOMINAL[sample]
        ss = [s["met"] for s in spots if s["sample"] == sample]
        mean = {m: float(np.mean([x[m] for x in ss])) for m in METALS}
        corr = dict(mean)
        cu_true = mean["Cu"] / (1 - a_art)
        corr["Ni"] = mean["Ni"] - (cu_true - mean["Cu"])
        corr["Cu"] = cu_true
        single[sample] = dict(n=len(ss), mean=mean, ni_corrected=corr)
        print(f"{sample} {name} (n={len(ss)}): " + "  ".join(
            f"{m} {mean[m]:5.2f} ({mean[m] - nom[m]:+5.2f}; Ni-corr {corr[m] - nom[m]:+5.2f})" for m in nom))

    print("\n=== BSE area fractions (dark -> bright), pores excluded")
    fr = {}
    for p in sorted(glob.glob(os.path.join(args.root, "Images", "*.jpeg"))):
        b = os.path.basename(p)
        smp = b.split("_")[0].split("-")[0].split(".")[0]
        f, pore = phase_fractions(p, 3 if smp == "149" else 2)
        fr.setdefault(smp, []).append(dict(image=b, fractions=f, pores=pore))
        print(f"{b:45s} {[round(x, 3) for x in f]}  pores {pore:.3f}")

    def mfrac(smp):
        return list(np.mean([r["fractions"] for r in fr[smp]], axis=0))

    def avg(*ms):
        return {m: float(np.mean([x[m] for x in ms])) for m in METALS}

    est = {}
    f = mfrac("149")  # mottled Co-Mn (spots 3, 4) < smooth Cr-rich (spot 2) < Cu-rich (spot 1) in BSE grey level
    est["149"] = lever([avg(sp("149 EDS", "Image 1_analysis_3_spot"), sp("149 EDS", "Image 1_analysis_4_spot")),
                        sp("149 EDS", "Image 1_analysis_2_spot"), sp("149 EDS", "Image 1_analysis_1_spot")], f)
    f = mfrac("150")
    est["150"] = lever([avg(sp("150 EDS", "Image 1_analysis_1_spot"), sp("150 EDS", "Image 1_analysis_2_spot")),
                        avg(sp("150 EDS", "Image 1_analysis_3_spot"), sp("150 EDS", "Image 1_analysis_4_spot"))], f)
    f = mfrac("153")
    est["153"] = lever([avg(sp("153 EDS", "Image 1_analysis_1_spot"), sp("153 EDS", "Image 1_analysis_3_spot")),
                        sp("153 EDS", "Image 1_analysis_2_spot")], f)
    f = mfrac("154")  # dark Cr-rich phase read two ways: spot 2 (500x) and the 2000x spot of Image 2
    mat = sp("154 EDS", "Image 1_analysis_1_spot")
    est["154_spot2"] = lever([sp("154 EDS", "Image 1_analysis_2_spot"), mat], f)
    est["154_img2"] = lever([sp("154 EDS", "Image 2_analysis_1_spot"), mat], f)
    print("\n=== Lever-rule bulk estimates (diff from nominal)")
    for k, e in est.items():
        name, nom = NOMINAL[k[:3]]
        print(f"{k:10s} {name:5s} " + "  ".join(f"{m} {e[m]:5.1f} ({e[m] - nom.get(m, 0):+5.1f})"
                                               for m in METALS if e[m] > 0.4 or m in nom))

    with open(os.path.join(args.out, "readout.json"), "w") as fh:
        json.dump(dict(nominal=NOMINAL, tolerance_at_pct=TOL, spots=spots, ni_artifact_share=a_art,
                       single_phase=single, bse_fractions=fr, lever_estimates=est), fh, indent=1)


if __name__ == "__main__":
    main()
