#!/usr/bin/env python3
"""Geometry integrity of a retained HEA adsorbate state, read from the deck itself.

For one deck (symbols, positions in angstrom, cell) whose first `n_slab` atoms are the slab
and whose remaining atoms are the adsorbate in the order the chains retain them (OOH:
proximal O, distal O, H; OH: O, H; O: O), this module reports, under the minimum-image
convention on the retained cell:

  * O-O, H-O_proximal, H-O_distal and H-nearest-slab-O distances,
  * the nearest slab metal to each adsorbate atom (distance, symbol, index) and each
    adsorbate atom's height above the topmost slab metal,
  * an ANOMALY CLASS in the vocabulary of the adsorbate-integrity screens of record: NORMAL
    (adsorbed, intact), DESORPTION (no adsorbate O within the metal-contact cut) and
    DISSOCIATION / H TRANSFER (the H bonded to a slab O, not to the adsorbate), with the
    free-species spin multiplicity that class implies for a fixed-geometry SCF (HO2 radical
    in vacuum: doublet, 1 Bohr mag; O2 in vacuum: triplet, 2 Bohr mag).

Thresholds are the exploratory geometry-audit thresholds the chains were classified with,
copied from results/cr_site_chains_2026-09-06/paired_readout/readout.json:269-277
(`thresholds_A`), whose metal-contact cut is the desorption cut of src/hea_oer/data.py:20
(M_O_DESORBED_MIN = 3.00). Nothing here scores anything; the readout prints these rows.
"""
from __future__ import annotations

import math

METALS = ("Cr", "Mn", "Fe", "Co", "Ni", "Cu")

#: results/cr_site_chains_2026-09-06/paired_readout/readout.json:269-277 (thresholds_A)
THRESHOLDS = dict(oo_min_A=1.1, oo_max_A=1.8, oh_min_A=0.7, oh_max_A=1.25,
                  h_slab_o_max_A=1.25, metal_contact_max_A=3.0)

#: Free-species ground states a desorbed fragment implies in a spin-polarised SCF.
FREE_SPECIES = {
    "HO2(g) doublet": 1.0,
    "O2(g) triplet": 2.0,
}


def _inv3(m):
    a, b, c = m
    det = (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
           + a[2] * (b[0] * c[1] - b[1] * c[0]))
    if abs(det) < 1e-12:
        raise ValueError("singular cell")
    cof = [
        [(b[1] * c[2] - b[2] * c[1]), -(a[1] * c[2] - a[2] * c[1]), (a[1] * b[2] - a[2] * b[1])],
        [-(b[0] * c[2] - b[2] * c[0]), (a[0] * c[2] - a[2] * c[0]), -(a[0] * b[2] - a[2] * b[0])],
        [(b[0] * c[1] - b[1] * c[0]), -(a[0] * c[1] - a[1] * c[0]), (a[0] * b[1] - a[1] * b[0])],
    ]
    return [[cof[i][j] / det for j in range(3)] for i in range(3)]


def mic_distance(p, q, cell) -> float:
    """Minimum-image distance between cartesian points p and q in the periodic cell."""
    inv = _inv3(cell)
    d = [q[i] - p[i] for i in range(3)]
    f = [sum(d[k] * inv[k][j] for k in range(3)) for j in range(3)]
    f = [x - round(x) for x in f]
    c = [sum(f[k] * cell[k][j] for k in range(3)) for j in range(3)]
    return math.sqrt(sum(x * x for x in c))


def analyse(symbols, positions, cell, n_slab: int = 72) -> dict:
    """Integrity row for one state. Adsorbate atoms are those with index >= n_slab."""
    symbols = list(symbols)
    nat = len(symbols)
    ads = list(range(n_slab, nat))
    metals = [i for i in range(n_slab) if symbols[i] in METALS]
    slab_o = [i for i in range(n_slab) if symbols[i] == "O"]
    if not metals or not slab_o:
        raise ValueError("slab carries no metal or no O")
    z_top = max(positions[i][2] for i in metals)
    row = dict(nat=nat, n_adsorbate=len(ads), atoms={}, thresholds=dict(THRESHOLDS))
    for i in ads:
        dm, jm = min((mic_distance(positions[i], positions[j], cell), j) for j in metals)
        row["atoms"][i] = dict(symbol=symbols[i], nearest_metal_A=dm, nearest_metal=f"{symbols[jm]}{jm}",
                               height_above_top_metal_A=positions[i][2] - z_top)
    ads_o = [i for i in ads if symbols[i] == "O"]
    ads_h = [i for i in ads if symbols[i] == "H"]
    t = THRESHOLDS
    if len(ads_o) == 2:
        row["O_O_A"] = mic_distance(positions[ads_o[0]], positions[ads_o[1]], cell)
    if ads_h:
        h = ads_h[0]
        if ads_o:
            row["H_O_proximal_A"] = mic_distance(positions[h], positions[ads_o[0]], cell)
        if len(ads_o) == 2:
            row["H_O_distal_A"] = mic_distance(positions[h], positions[ads_o[1]], cell)
        ds, js = min((mic_distance(positions[h], positions[j], cell), j) for j in slab_o)
        row["H_nearest_slab_O_A"] = ds
        row["H_nearest_slab_O_index"] = js
    # classification
    if not ads:
        cls, free, adsorbml = "CLEAN SLAB", None, "n/a"
    else:
        metal_contact = any(row["atoms"][i]["nearest_metal_A"] <= t["metal_contact_max_A"] for i in ads_o)
        h_on_ads = bool(ads_h) and min(row.get("H_O_proximal_A", 9e9), row.get("H_O_distal_A", 9e9)) <= t["oh_max_A"]
        h_on_slab = bool(ads_h) and row.get("H_nearest_slab_O_A", 9e9) <= t["h_slab_o_max_A"]
        oo_ok = "O_O_A" not in row or t["oo_min_A"] <= row["O_O_A"] <= t["oo_max_A"]
        if len(ads_o) == 2 and ads_h:          # OOH record
            if metal_contact and h_on_ads and oo_ok:
                cls, free, adsorbml = "*OOH adsorbed, intact", None, "NORMAL"
            elif metal_contact and h_on_slab:
                cls, free, adsorbml = "*O2 + H_b (H transferred to slab O; bridge-pathway state)", None, "DISSOCIATION / H TRANSFER"
            elif not metal_contact and h_on_ads:
                cls, free, adsorbml = "HO2(g) radical in cell, no metal contact", "HO2(g) doublet", "DESORPTION"
            elif not metal_contact and h_on_slab:
                cls, free, adsorbml = "O2(g) in cell + H on slab O (H transferred)", "O2(g) triplet", "DESORPTION + DISSOCIATION / H TRANSFER"
            else:
                cls, free, adsorbml = "UNCLASSIFIED", None, "UNCLASSIFIED"
        elif len(ads_o) == 1 and ads_h:        # OH record
            if metal_contact and h_on_ads:
                cls, free, adsorbml = "*OH adsorbed, intact", None, "NORMAL"
            elif metal_contact and h_on_slab:
                cls, free, adsorbml = "*O + H_b (H transferred to slab O)", None, "DISSOCIATION / H TRANSFER"
            elif not metal_contact:
                cls, free, adsorbml = "OH fragment without metal contact", None, "DESORPTION"
            else:
                cls, free, adsorbml = "UNCLASSIFIED", None, "UNCLASSIFIED"
        elif len(ads_o) == 1 and not ads_h:    # O record
            cls, free, adsorbml = ("*O adsorbed", None, "NORMAL") if metal_contact else ("O without metal contact", None, "DESORPTION")
        else:
            cls, free, adsorbml = "UNCLASSIFIED", None, "UNCLASSIFIED"
    row["anomaly_class"] = cls
    row["screen_category"] = adsorbml
    row["free_species"] = free
    row["expected_free_species_moment_muB"] = FREE_SPECIES.get(free) if free else None
    return row


def summary(row: dict) -> str:
    """One-line rendering for manifests and the readout."""
    parts = []
    if "O_O_A" in row:
        parts.append(f"O-O {row['O_O_A']:.3f}")
    if "H_O_proximal_A" in row:
        parts.append(f"H-Op {row['H_O_proximal_A']:.3f}")
    if "H_O_distal_A" in row:
        parts.append(f"H-Od {row['H_O_distal_A']:.3f}")
    if "H_nearest_slab_O_A" in row:
        parts.append(f"H-slabO{row['H_nearest_slab_O_index']} {row['H_nearest_slab_O_A']:.3f}")
    for i, a in row["atoms"].items():
        parts.append(f"{a['symbol']}{i}-{a['nearest_metal']} {a['nearest_metal_A']:.3f} (h {a['height_above_top_metal_A']:+.2f})")
    tail = f" -> {row.get('anomaly_class')} [{row.get('screen_category')}]"
    if row.get("free_species"):
        tail += f", free species {row['free_species']} ({row['expected_free_species_moment_muB']:.0f} Bohr mag)"
    return "; ".join(parts) + tail
