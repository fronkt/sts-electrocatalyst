"""S8 optical micrographs of the six cast and homogenized alloys (Fort Wayne Metals, 2026-10-26): scale and sizes.

Usage: python src/scripts/s8_optical_measure.py "D:\\STS Electrocatalyst EDS & SEM\\Optical-as-cast-2026-10-26"

1. Scale: the burned-in bar (blue, or red on the 500 um images) is found by colour; um/px = bar label / bar length.
2. Cu26 (150): dark Cu-rich pools (Otsu, holes filled, features under ~20 um opened away); max Feret and
   equivalent diameter, flagging pools cut by the frame.
3. Cu22 (153) dark network and Ni31 (154) bright particles: area fractions at more than one threshold.

The fields were framed by hand, so the fractions describe these fields only, not the alloy.
Record: docs/research/s8-sem-eds-record-2026-10-23.md. The image files stay outside the repo.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import filters, measure, morphology

LABELS = {  # bar labels as printed on the images (um)
    "149-1": 100, "149-2": 40, "149-6": 200,
    "150-1": 200, "150-2": 40, "150-3": 100, "150-4": 100, "150-5": 100, "150-6": 200, "150-7": 200,
    "150-8": 200, "150-9": 400,
    "151-2": 500, "151-4": 200, "151-5": 200, "151-FC": 500,
    "152": 500, "152-2": 500, "152-3": 200, "152-4-close center": 200,
    "153": 400, "153-2": 100, "153-5": 200, "153-6": 200,
    "154": 200, "154-2": 100, "154-5": 200, "154-6": 200,
}  # 154-3 (colour) is left out: its orange background defeats the colour search; same 100 um bar as 154-2


def bar_umpx(src, name):
    rgb = np.asarray(Image.open(src / f"{name}.jpg").convert("RGB")).astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    bar = ((b > 150) & (r < 90) & (g < 90)) | ((r > 150) & (g < 90) & (b < 90))
    bar[:900] = False  # bars sit in the bottom strip
    cols = np.where(bar.any(axis=0))[0]
    length = cols.max() - cols.min() + 1
    return LABELS[name] / length, length


def gray(src, name):
    g = np.asarray(Image.open(src / f"{name}.jpg").convert("L")).astype(float)
    mask = np.ones_like(g, bool)
    mask[940:, 940:1270] = False  # bar and label box
    return g, mask


def main(src):
    print("== scale ==")
    umpx = {}
    for name in LABELS:
        umpx[name], length = bar_umpx(src, name)
        print(f"{name:22s} bar {length:4d} px = {LABELS[name]:3d} um -> {umpx[name]:.4f} um/px, "
              f"field {1384 * umpx[name]:5.0f} x {1036 * umpx[name]:5.0f} um")

    print("\n== Cu26 (150): Cu-rich pools ==")
    for name in ("150-1", "150-3", "150-4", "150-5"):
        g, mask = gray(src, name)
        dark = ndi.binary_fill_holes((g < filters.threshold_otsu(g[mask])) & mask)
        pools = morphology.opening(dark, morphology.disk(max(1, round(10 / umpx[name]))))
        print(f"{name}: pools cover {100 * pools[mask].mean():.1f}% of the field")
        props = sorted(measure.regionprops(measure.label(pools)), key=lambda p: -p.feret_diameter_max)
        for p in props[:4]:
            r0, c0, r1, c1 = p.bbox
            cut = r0 == 0 or c0 == 0 or r1 == g.shape[0] or c1 == g.shape[1]
            print(f"   max Feret {p.feret_diameter_max * umpx[name]:4.0f} um, equivalent diameter "
                  f"{p.equivalent_diameter_area * umpx[name]:4.0f} um{'  (cut by the frame: lower bound)' if cut else ''}")
    print("   (150-5: a region cut by the frame at top left is the mount, not a pool)")

    print("\n== Cu22 (153): dark network, pores and grain outlines ==")
    for name in ("153", "153-2"):
        g, mask = gray(src, name)
        print(f"{name}: {100 * ((g < filters.threshold_otsu(g[mask])) & mask)[mask].mean():.1f}% (Otsu)")

    print("\n== Ni31 (154): bright particles ==")
    for name in ("154-5", "154-6"):
        g, mask = gray(src, name)
        hist, edges = np.histogram(g[mask], bins=64, range=(0, 256))
        smooth = np.convolve(hist, np.ones(3) / 3, mode="same")
        peak = int(np.argmax(smooth))  # matrix peak
        valley = peak + int(np.argmin(smooth[peak:-2]))  # minimum between the matrix and the bright top end
        t_valley = edges[valley + 1]
        t_upper = filters.threshold_multiotsu(g[mask], classes=3)[1]
        frac = {t: 100 * ((g > t) & mask)[mask].mean() for t in (t_upper, t_valley)}
        print(f"{name}: {frac[t_upper]:.1f}% above the upper multi-Otsu level ({t_upper:.0f}), "
              f"{frac[t_valley]:.1f}% above the histogram valley ({t_valley:.0f})")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
