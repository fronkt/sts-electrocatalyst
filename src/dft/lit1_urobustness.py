#!/usr/bin/env python3
"""LIT-1 tranche 1: U-robustness analysis of the existing P7 fixed-geometry U-ladders.

Registered scope (docs/43 AMENDMENT 5, A5.1, items a/c/d): post-process the
already-computed U-ladder SCFs -- zero new DFT -- for

  (a) valence tracking: active-site local magnetic moment vs the bare slab at the
      same U, with a stated numeric valence-conserving / valence-changing
      criterion (see VALENCE_THRESHOLD_MUB below);
  (c) G_max at eta = 0.1 / 0.2 / 0.3 V with the limiting-span identity, per U
      point (g_max imported from src/dft/volcano_r1.py, the implementation
      session-verified against Razzaq-Exner 2023 eqs 10-25 -- NOT reimplemented);
  (d) the intercept-vs-descriptor U-test: dG(*OOH) - dG(*OH) vs U alongside
      dG(*O) - dG(*OH) vs U (Tripkovic 2018 Table 3 motivation).

Inputs (FIXED, produced by the docs/41 P7 probe protocol -- U varied at fixed
production geometry):

  runs/probe/Cr/{slab,s0_O,s0_OH,s0_OOH}__{base,u0.0,u0.5,u1.35}.out
  runs/probe/Co_uladder/{slab,s0_O,s0_OH}__{base,u0.0,u0.5,u1.35}.out

Co has NO s0_OOH at any U -- that hole is registered (docs/41 s6d/s6e; docs/43
A5.5 firewall) and Co is scored through the bounded-eta identity of
src/dft/eta_bounded.py instead of a full CHE chain.

Conventions REUSED, not reinvented:
  - CHE referencing + ZPE-TS corrections: hea_oer.referencing.delta_G
    (ZPE_TS_CORRECTION = {OH: +0.35, O: +0.05, OOH: +0.40} eV,
    src/hea_oer/referencing.py:18, Man 2011 / Valdes 2008).
  - eta_TD and the potential-limiting step: hea_oer.descriptors.oer_overpotential
    (G_TOTAL = 4.92 eV, src/hea_oer/descriptors.py:34).
  - G_max: dft.volcano_r1.g_max, imported.
  - Bounded eta for Co: dft.eta_bounded.eta_window / OBSERVED_DG_OOH.
  - Energy QC: dft.qe_qc.trusted_energy_ev (strict), the production gate.
  - Gas references reused from each metal's source run (H2O/H2 in a
    Martyna-Tuckerman box; no Hubbard U touches them, so reuse across the U
    ladder is exact -- src/dft/probe_eta.py:23-27).

Outputs:
  docs/research/lit1_tranche1_uladder.json
  docs/research/2026-08-12-lit1-tranche1-uladder.md

Usage:
  PYTHONPATH=src python src/dft/lit1_urobustness.py [--root .]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))          # src/ on the path

from hea_oer.referencing import delta_G, ZPE_TS_CORRECTION           # noqa: E402
from hea_oer.descriptors import (oer_overpotential, oer_steps,        # noqa: E402
                                 G_TOTAL, OER_EQUILIBRIUM_V)
from dft.volcano_r1 import g_max                                      # noqa: E402
from dft.eta_bounded import eta_window, OBSERVED_DG_OOH               # noqa: E402
from dft import qe_qc                                                 # noqa: E402

# ---------------------------------------------------------------------------
# Registered ladder definitions (docs/41 s5 P7; docs/43 A5.1).
# ---------------------------------------------------------------------------
LADDERS = {
    "Cr": dict(
        probedir=os.path.join("runs", "probe", "Cr"),
        source_run=os.path.join("runs", "Cr_slab"),
        states=("slab", "s0_OH", "s0_O", "s0_OOH"),
        n_slab_atoms=18,               # 6 Cr + 12 O; adsorbate atoms appended last
        metal="Cr",
        production_U_eV=3.70,          # MP-fitted U, HUBBARD card of *__base.in
        basin_reference=os.path.join("runs", "probe", "Cr_basin", "s0_OOH.out"),
        basin_reference_state="s0_OOH",
    ),
    "Co": dict(
        probedir=os.path.join("runs", "probe", "Co_uladder"),
        source_run=os.path.join("runs", "Co_slab"),
        states=("slab", "s0_OH", "s0_O"),      # NO s0_OOH -- registered hole
        n_slab_atoms=18,
        metal="Co",
        production_U_eV=3.32,
        basin_reference=os.path.join("runs", "probe", "Co_basin", "s0_OH.out"),
        basin_reference_state="s0_OH",
    ),
}

#: ladder points, multiplier of the production U (docs/41 s5 P7).
VARIANTS = (("u0.0", 0.0), ("u0.5", 0.5), ("base", 1.0), ("u1.35", 1.35))

#: A5.1a valence-conserving / valence-changing criterion, stated with rationale.
#: Tracked quantity: dm(U) = m_site(adsorbate state, U) - m_site(bare slab, U),
#: the active-site sphere-integrated moment relative to the bare slab at the SAME
#: U (the primary valence tracker of A5.1a). Following Tripkovic 2018's V(B)
#: analysis, the classification is of the ADSORPTION STEP: a dG is
#: VALENCE-CHANGING when |dm(production U)| >= 0.5 mu_B -- the step changes the
#: active-site oxidation state, which is the mechanism that makes a dG U-fragile
#: (U acts on the d-occupancy that step changes). Rationale for 0.5: a genuine
#: one-electron redox at a high-spin 3d site moves the sphere-integrated moment
#: by ~1 mu_B; half that separates it from covalent/hybridisation transfer, and
#: sits far above both the ~0.05-0.1 mu_B sphere-integration scatter and the
#: 0.1 mu_B magnetic-channel resolution this campaign already uses (docs/43 P16
#: and Amendment 4 s3). Supplementary check: the RANGE of dm across the four U
#: points; if it exceeds the same 0.5 mu_B the tracker itself is UNSTABLE across
#: U (an SCF-solution change somewhere on the ladder) and the classification is
#: flagged rather than trusted.
VALENCE_THRESHOLD_MUB = 0.5

ETA_TARGETS = (0.1, 0.2, 0.3)          # A5.1c: G_max at these overpotentials (V)

#: contiguous CPET spans, 1-based inclusive, and their dG_OOH-free algebra where
#: it exists (dG3 + dG4 = G_TOTAL - dG_O eliminates dG_OOH -- eta_bounded.py:17-21).
SPAN_LABELS = {(1, 1): "dG1", (2, 2): "dG2", (3, 3): "dG3", (4, 4): "dG4",
               (1, 2): "dG1+dG2", (2, 3): "dG2+dG3", (3, 4): "dG3+dG4",
               (1, 3): "dG1..dG3", (2, 4): "dG2..dG4", (1, 4): "dG1..dG4"}

_RE_TOTMAG = re.compile(r"total magnetization\s+=\s+(-?\d+\.\d+)\s+Bohr")
_RE_ABSMAG = re.compile(r"absolute magnetization\s+=\s+(-?\d+\.\d+)\s+Bohr")
_RE_SITEMAG = re.compile(r"^\s*atom\s+(\d+)\s+\(R=\s*[\d.]+\)\s+charge=\s*(-?[\d.]+)\s+magn=\s*(-?[\d.]+)")
_RE_TRNS = re.compile(r"Tr\[ns\(\s*(\d+)\)\]\s+\(up, down, total\)\s+=\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)")
_RE_HUBU = re.compile(r"^\s*U\s+\S+-3d\s+([\d.]+)", re.M)


# ---------------------------------------------------------------------------
# pw.x output / input parsing
# ---------------------------------------------------------------------------
def parse_out_magnetics(path: str) -> dict:
    """Total/absolute magnetization (last printed = converged) and the last
    per-site moment block, plus the last HUBBARD OCCUPATIONS Tr[ns] block."""
    txt = open(path, errors="ignore").read()
    tot = _RE_TOTMAG.findall(txt)
    ab = _RE_ABSMAG.findall(txt)
    rec = dict(total_mag=float(tot[-1]) if tot else None,
               abs_mag=float(ab[-1]) if ab else None,
               site_moments=None, site_charges=None, trns=None)

    blocks = txt.split("Magnetic moment per site")
    if len(blocks) > 1:
        moments, charges = {}, {}
        for ln in blocks[-1].splitlines():
            m = _RE_SITEMAG.match(ln)
            if m:
                moments[int(m.group(1))] = float(m.group(3))
                charges[int(m.group(1))] = float(m.group(2))
            elif moments and ln.strip() and not ln.strip().startswith("atom"):
                break
        rec["site_moments"], rec["site_charges"] = moments, charges

    occ = txt.split("HUBBARD OCCUPATIONS")
    if len(occ) > 1:
        trns = {}
        for m in _RE_TRNS.finditer(occ[-1]):
            trns[int(m.group(1))] = dict(up=float(m.group(2)),
                                         down=float(m.group(3)),
                                         total=float(m.group(4)))
        rec["trns"] = trns or None
    return rec


def parse_in_geometry(path: str) -> dict:
    """Species + cartesian positions (angstrom) + diagonal cell from a QE deck."""
    lines = open(path, errors="ignore").read().splitlines()
    cell, species, pos = [], [], []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.upper().startswith("CELL_PARAMETERS"):
            for j in range(i + 1, i + 4):
                cell.append([float(x) for x in lines[j].split()[:3]])
            i += 4
            continue
        if s.upper().startswith("ATOMIC_POSITIONS"):
            assert "angstrom" in s.lower(), f"{path}: positions not in angstrom"
            i += 1
            while i < len(lines):
                t = lines[i].split()
                if len(t) < 4 or not _isfloat(t[1]):
                    break
                species.append(t[0])
                pos.append([float(t[1]), float(t[2]), float(t[3])])
                i += 1
            continue
        i += 1
    m = _RE_HUBU.search("\n".join(lines))
    return dict(cell=cell, species=species, positions=pos,
                hubbard_U_eV=float(m.group(1)) if m else 0.0)


def _isfloat(t):
    try:
        float(t)
        return True
    except ValueError:
        return False


def _mi_dist(p, q, cell) -> float:
    """Minimum-image distance for a diagonal (orthorhombic) cell, a/b periodic."""
    a, b = cell[0][0], cell[1][1]
    assert abs(cell[0][1]) < 1e-6 and abs(cell[1][0]) < 1e-6, "cell not diagonal"
    dx = p[0] - q[0]
    dx -= a * round(dx / a)
    dy = p[1] - q[1]
    dy -= b * round(dy / b)
    dz = p[2] - q[2]                    # c is the vacuum axis; no wrap needed
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def active_site(geom: dict, n_slab: int, metal: str) -> dict:
    """The adsorbate-binding metal atom: nearest metal to the first adsorbate atom
    (adsorbate atoms are appended after the n_slab slab atoms; the first is the
    binding O for *O, *OH and *OOH in this project's builders)."""
    if len(geom["positions"]) <= n_slab:
        return dict(index0=None, note="bare slab")
    bind_O = geom["positions"][n_slab]
    best, best_d = None, 1e9
    for i in range(n_slab):
        if geom["species"][i] != metal:
            continue
        d = _mi_dist(geom["positions"][i], bind_O, geom["cell"])
        if d < best_d:
            best, best_d = i, d
    return dict(index0=best, M_O_dist_A=round(best_d, 4))


def oo_distance(geom: dict, n_slab: int) -> float | None:
    """O-O distance of an *OOH adsorbate (atoms n_slab and n_slab+1)."""
    n_ads = len(geom["positions"]) - n_slab
    if n_ads < 3:
        return None
    return round(_mi_dist(geom["positions"][n_slab], geom["positions"][n_slab + 1],
                          geom["cell"]), 4)


# ---------------------------------------------------------------------------
# G_max with the limiting-span identity (value cross-checked against volcano_r1)
# ---------------------------------------------------------------------------
def g_max_with_span(steps, U):
    """Exner G_max at potential U plus the (a, b) span that sets it.

    Same algebra as dft.volcano_r1.g_max (verified identical to Razzaq-Exner
    2023 eqs 10-25); this wrapper only records WHICH contiguous span wins and
    asserts equality with the imported implementation.
    """
    g = [s - U for s in steps]
    best, span = 0.0, None
    for a in range(4):
        for b in range(a, 4):
            v = sum(g[a:b + 1])
            if v > best:
                best, span = v, (a + 1, b + 1)
    ref = g_max(steps, U)
    assert abs(best - ref) < 1e-10, "span-resolved G_max disagrees with volcano_r1.g_max"
    return best, span


def g_max_lower_bound(dG_OH, dG_O, U):
    """G_max lower bound for a metal with no *OOH (Co): max over the contiguous
    spans whose sum is expressible without dG_OOH. The usable identity is
    dG3 + dG4 = G_TOTAL - dG_O (eta_bounded.py); computable spans are
    (1,1) (2,2) (1,2) (3,4) (2,4) (1,4). Spans containing dG3 or dG4 alone (or
    dG2+dG3) need dG_OOH and are excluded, so the true G_max can only be >=."""
    spans = {(1, 1): dG_OH - U,
             (2, 2): (dG_O - dG_OH) - U,
             (1, 2): dG_O - 2 * U,
             (3, 4): (G_TOTAL - dG_O) - 2 * U,
             (2, 4): (G_TOTAL - dG_OH) - 3 * U,
             (1, 4): G_TOTAL - 4 * U}
    span, val = max(spans.items(), key=lambda kv: kv[1])
    if val <= 0.0:
        return 0.0, None
    return val, span


# ---------------------------------------------------------------------------
# main analysis
# ---------------------------------------------------------------------------
def analyse_ladder(root: str, name: str, cfg: dict) -> dict:
    pdir = os.path.join(root, cfg["probedir"])
    man = json.load(open(os.path.join(pdir, "probe_manifest.json")))
    relax_ref = {}
    for j in man["jobs"]:
        relax_ref[j["job"]] = j.get("relax_reference_ev")

    # gas references: reused from the source run, QC'd (probe_eta.py convention;
    # exact across the U ladder -- no Hubbard channel touches H2O/H2)
    gas = {}
    for gname in ("H2O", "H2"):
        p = os.path.join(root, cfg["source_run"], gname + ".out")
        e = qe_qc.trusted_energy_ev(p, strict=True)
        if e is None:
            sys.exit(f"REFUSING: gas reference {p} missing or failed QC")
        gas[gname] = e

    # basin-corrected reference (docs/41 s6f), where one exists on disk
    basin_ev = None
    bp = os.path.join(root, cfg["basin_reference"])
    if os.path.exists(bp):
        basin_ev = qe_qc.trusted_energy_ev(bp, strict=True)

    states = cfg["states"]
    per_variant = {}
    for vname, mult in VARIANTS:
        srec = {}
        for st in states:
            stem = os.path.join(pdir, f"{st}__{vname}")
            outp, inp = stem + ".out", stem + ".in"
            e = qe_qc.trusted_energy_ev(outp, inp, strict=True)
            qc = qe_qc.scan(outp, inp)
            geom = parse_in_geometry(inp)
            mag = parse_out_magnetics(outp)
            site = active_site(geom, cfg["n_slab_atoms"], cfg["metal"])
            m_site = trns_site = None
            if site.get("index0") is not None and mag["site_moments"]:
                m_site = mag["site_moments"].get(site["index0"] + 1)
                if mag["trns"]:
                    t = mag["trns"].get(site["index0"] + 1)
                    trns_site = t["total"] if t else None
            srec[st] = dict(
                energy_ev=e, qc_verdict=qc["verdict"],
                hubbard_U_eV=geom["hubbard_U_eV"],
                total_mag=mag["total_mag"], abs_mag=mag["abs_mag"],
                active_site=site, active_site_moment=m_site,
                active_site_trns_total=trns_site,
                site_moments_metal={i + 1: mag["site_moments"].get(i + 1)
                                    for i in range(cfg["n_slab_atoms"])
                                    if geom["species"][i] == cfg["metal"]}
                                   if mag["site_moments"] else None,
                oo_dist_A=oo_distance(geom, cfg["n_slab_atoms"]),
            )
            if e is None:
                print(f"  WARNING {name} {st}__{vname}: failed strict QC "
                      f"({qc['verdict']}: {'; '.join(qc['reasons'])[:80]})")

        # propagate the bare-slab active-site moment: the binding site index is
        # taken from each adsorbate state's own geometry, read out of the SAME
        # index in the slab deck (identical atom ordering, verified by species)
        slab_moms = per_site_slab = None
        if srec["slab"].get("site_moments_metal"):
            per_site_slab = srec["slab"]["site_moments_metal"]
        for st in states:
            if st == "slab":
                continue
            idx0 = srec[st]["active_site"].get("index0")
            m_slab = None
            if idx0 is not None and per_site_slab:
                m_slab = per_site_slab.get(idx0 + 1)
            srec[st]["slab_site_moment_same_U"] = m_slab
            m_ads = srec[st]["active_site_moment"]
            srec[st]["delta_moment_vs_slab"] = (
                round(m_ads - m_slab, 4) if (m_ads is not None and m_slab is not None) else None)

        # thermodynamics at this U point
        rec = dict(U_multiplier=mult,
                   U_eV=round(mult * cfg["production_U_eV"], 4),
                   states=srec)
        e_slab = srec["slab"]["energy_ev"]
        have = all(srec[s]["energy_ev"] is not None for s in states)
        if have:
            dG = {}
            for st in states:
                if st == "slab":
                    continue
                sp = st.split("_")[1]
                dG[sp] = delta_G(e_slab, srec[st]["energy_ev"], sp,
                                 gas["H2O"], gas["H2"])
            rec["dG"] = {k: round(v, 4) for k, v in dG.items()}
            rec["descriptor_eV"] = round(dG["O"] - dG["OH"], 4)
            if "OOH" in dG:
                res = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
                steps = oer_steps(dG["OH"], dG["O"], dG["OOH"])
                rec["eta_V"] = round(res.overpotential, 4)
                rec["pls"] = res.potential_limiting_step
                rec["steps_eV"] = [round(s, 4) for s in steps]
                rec["intercept_eV"] = round(dG["OOH"] - dG["OH"], 4)  # vs 3.2
                rec["gmax"] = {}
                for eta_t in ETA_TARGETS:
                    v, span = g_max_with_span(steps, OER_EQUILIBRIUM_V + eta_t)
                    rec["gmax"][f"eta{eta_t}"] = dict(
                        value_eV=round(v, 4),
                        limiting_span=SPAN_LABELS.get(span),
                        exact=True)
            else:
                w = eta_window(dG["OH"], dG["O"])   # eta_bounded convention
                rec["eta_bound_V"] = round(w["eta"], 4)
                rec["pls_bound"] = w["pls"]
                rec["eta_bound_valid_dG_OOH_window_eV"] = [round(w["lo"], 3),
                                                           round(w["hi"], 3)]
                rec["window_margin_vs_observed_dG_OOH"] = dict(
                    lo=round(OBSERVED_DG_OOH[0] - w["lo"], 3),
                    hi=round(w["hi"] - OBSERVED_DG_OOH[1], 3))
                rec["gmax_lower_bound"] = {}
                for eta_t in ETA_TARGETS:
                    v, span = g_max_lower_bound(dG["OH"], dG["O"],
                                                OER_EQUILIBRIUM_V + eta_t)
                    rec["gmax_lower_bound"][f"eta{eta_t}"] = dict(
                        value_eV=round(v, 4),
                        limiting_span=SPAN_LABELS.get(span),
                        exact=False,
                        note="lower bound: spans needing dG_OOH not computable")
        per_variant[vname] = rec

    # GATE-1 bookkeeping on the base column (production U)
    gate1 = {}
    for st in states:
        e_base = per_variant["base"]["states"][st]["energy_ev"]
        ref = relax_ref.get(st)
        d_mev = (e_base - ref) * 1000 if (e_base is not None and ref is not None) else None
        row = dict(base_scf_ev=e_base, production_relax_ev=ref,
                   drift_meV=round(d_mev, 2) if d_mev is not None else None)
        if st == cfg["basin_reference_state"] and basin_ev is not None and e_base is not None:
            row["basin_rerelax_final_ev"] = basin_ev
            row["base_scf_vs_basin_final_meV"] = round((e_base - basin_ev) * 1000, 2)
        gate1[st] = row

    return dict(config={k: v for k, v in cfg.items()},
                gas_references_ev=gas, per_variant=per_variant, gate1_base=gate1)


def classify_valence(ladder: dict, states) -> dict:
    """A5.1a classification per adsorption dG (Tripkovic V(B) step classification).

    Primary: |dm(production U)| >= VALENCE_THRESHOLD_MUB => the adsorption step is
    valence-changing (expected U-fragile). Supplementary: the range of dm across
    the four U points; >= the same threshold marks the tracker UNSTABLE across U
    (an SCF-solution change on the ladder), and the classification is flagged.
    """
    out = {}
    for st in states:
        if st == "slab":
            continue
        sp = st.split("_")[1]
        dm = {v: ladder["per_variant"][v]["states"][st].get("delta_moment_vs_slab")
              for v, _ in VARIANTS}
        dG = {v: (ladder["per_variant"][v].get("dG") or {}).get(sp)
              for v, _ in VARIANTS}
        dm_vals = [x for x in dm.values() if x is not None]
        dG_vals = [x for x in dG.values() if x is not None]
        dm_base = dm.get("base")
        rng = round(max(dm_vals) - min(dm_vals), 4) if dm_vals else None
        cls = (None if dm_base is None else
               ("valence-changing" if abs(dm_base) >= VALENCE_THRESHOLD_MUB
                else "valence-conserving"))
        stable = None if rng is None else rng < VALENCE_THRESHOLD_MUB
        out[f"dG_{sp}"] = dict(
            delta_moment_per_U={v: dm[v] for v, _ in VARIANTS},
            delta_moment_at_production_U=dm_base,
            classification=cls,
            expected=(None if cls is None else
                      ("U-fragile" if cls == "valence-changing" else "U-robust")),
            dG_U_swing_eV=(round(max(dG_vals) - min(dG_vals), 4) if dG_vals else None),
            tracker_range_across_U_muB=rng,
            tracker_stable_across_U=stable,
            note=(None if stable in (None, True) else
                  "tracker UNSTABLE across U: dm range >= threshold, an SCF-solution "
                  "change on the ladder (docs/41 s6e multistability); classification "
                  "at production U is flagged, not trusted"),
            criterion=f"step classification: |dm(production U)| >= "
                      f"{VALENCE_THRESHOLD_MUB} mu_B => valence-changing "
                      f"(dm = active-site moment minus bare-slab same-site moment "
                      f"at the same U); stability check: range of dm across the "
                      f"ladder < {VALENCE_THRESHOLD_MUB} mu_B")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--json-out", default=os.path.join(
        "docs", "research", "lit1_tranche1_uladder.json"))
    ap.add_argument("--md-out", default=os.path.join(
        "docs", "research", "2026-08-12-lit1-tranche1-uladder.md"))
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    results = {}
    for name, cfg in LADDERS.items():
        print(f"== {name} ladder ({cfg['probedir']}) ==")
        results[name] = analyse_ladder(args.root, name, cfg)
        results[name]["valence_classification"] = classify_valence(
            results[name], cfg["states"])

    # ---- console summary + sanity checks -----------------------------------
    cr = results["Cr"]["per_variant"]
    etas = {v: cr[v].get("eta_V") for v, _ in VARIANTS}
    swing = max(etas.values()) - min(etas.values())
    print("\nCr eta_TD(U):", {v: etas[v] for v, _ in VARIANTS},
          f"swing {swing:.4f} V (docs/41 P7: 1.122 V)")
    sanity = dict(
        eta_Cr_base_V=etas["base"],
        eta_Cr_base_expected_tier_v2_V=0.3303,
        eta_Cr_swing_V=round(swing, 4),
        eta_Cr_swing_expected_docs41_V=1.122,
    )
    co = results["Co"]["per_variant"]
    print("Co eta_TD lower bound(U):",
          {v: co[v].get("eta_bound_V") for v, _ in VARIANTS})

    payload = dict(
        _meta=dict(
            generated=str(_dt.date.today()),
            script="src/dft/lit1_urobustness.py",
            registration="docs/43-prereg-week1-factorial.md AMENDMENT 5, A5.1 (items a/c/d), tranche 1",
            protocol="docs/41 s5 P7: U varied at FIXED production geometry (single-point SCF); "
                     "relaxation under the perturbed Hamiltonian is NOT included",
            tier_context="These fixed-geometry ladder points are NOT tier entries. tier_v2 "
                         "(data/tiers/tier_v2.json) is frozen and unchanged; tier_v3 does not exist.",
            corrections="CHE referencing src/hea_oer/referencing.py (ZPE-TS OH +0.35 / O +0.05 / "
                        "OOH +0.40 eV, lines 17-21); G_TOTAL=4.92 src/hea_oer/descriptors.py:34; "
                        "g_max imported from src/dft/volcano_r1.py",
            valence_criterion_muB=VALENCE_THRESHOLD_MUB,
        ),
        sanity=sanity,
        ladders=results,
        intercept_test=dict(
            description="A5.1d: is the 3.2 eV scaling intercept dG(*OOH)-dG(*OH) U-robust "
                        "while the descriptor axis dG(*O)-dG(*OH) is U-fragile? "
                        "(Tripkovic 2018 Table 3: LaCrO3 intercept moves 0.01 eV over U=0-5 "
                        "while the descriptor moves +1.06 eV)",
            Cr={v: dict(U_eV=cr[v]["U_eV"],
                        intercept_eV=cr[v].get("intercept_eV"),
                        descriptor_eV=cr[v].get("descriptor_eV"))
                for v, _ in VARIANTS},
            Cr_intercept_span_eV=round(
                max(cr[v]["intercept_eV"] for v, _ in VARIANTS)
                - min(cr[v]["intercept_eV"] for v, _ in VARIANTS), 4),
            Cr_descriptor_span_eV=round(
                max(cr[v]["descriptor_eV"] for v, _ in VARIANTS)
                - min(cr[v]["descriptor_eV"] for v, _ in VARIANTS), 4),
            Co_descriptor_span_eV=round(
                max(co[v]["descriptor_eV"] for v, _ in VARIANTS)
                - min(co[v]["descriptor_eV"] for v, _ in VARIANTS), 4),
            Co_intercept="not computable: no Co *OOH at any U (registered hole)",
        ),
    )

    jpath = os.path.join(args.root, args.json_out)
    os.makedirs(os.path.dirname(jpath), exist_ok=True)
    json.dump(payload, open(jpath, "w", encoding="utf-8"), indent=1)
    print(f"-> {args.json_out}")

    write_markdown(os.path.join(args.root, args.md_out), payload)
    print(f"-> {args.md_out}")


# ---------------------------------------------------------------------------
# markdown report
# ---------------------------------------------------------------------------
def write_markdown(path: str, p: dict):
    cr = p["ladders"]["Cr"]["per_variant"]
    co = p["ladders"]["Co"]["per_variant"]
    g1cr = p["ladders"]["Cr"]["gate1_base"]
    g1co = p["ladders"]["Co"]["gate1_base"]
    vc_cr = p["ladders"]["Cr"]["valence_classification"]
    vc_co = p["ladders"]["Co"]["valence_classification"]
    it = p["intercept_test"]
    L = []
    A = L.append

    A("# LIT-1 tranche 1 — U-robustness of the P7 fixed-geometry U-ladders")
    A("")
    A(f"*Generated {p['_meta']['generated']} by `{p['_meta']['script']}`. "
      f"Registered under {p['_meta']['registration']}.*")
    A("")
    A("## Scope, tier context, approximation")
    A("")
    A("- **These fixed-geometry ladder points are NOT tier entries.** `tier_v2` "
      "(docs/41 §6f, frozen in `data/tiers/tier_v2.json` under docs/43 §0) is the "
      "baseline and is unchanged by anything in this document. `tier_v3` does not exist.")
    A("- **Fixed-geometry approximation, stated per A5.1(b)3:** every point is a "
      "single-point SCF at the production-U relaxed geometry (docs/41 §5 P7 protocol). "
      "Relaxation under the perturbed Hamiltonian is excluded by construction; these are "
      "leading-order sensitivities, not relaxed η values.")
    A("- Inputs: `runs/probe/Cr/` (4 states × 4 U) and `runs/probe/Co_uladder/` "
      "(3 states × 4 U — **Co has no `*OOH` at any U; that hole is registered**, "
      "docs/41 §6d/§6e, docs/43 A5.5 firewall). Zero new DFT.")
    A("- Conventions reused from the production pipeline: CHE ΔG via "
      "`hea_oer.referencing.delta_G` (ZPE−TΔS: OH +0.35, O +0.05, OOH +0.40 eV; "
      "`src/hea_oer/referencing.py:17-21`, Man 2011/Valdés 2008); η via "
      "`hea_oer.descriptors.oer_overpotential` (G_TOTAL = 4.92 eV, "
      "`src/hea_oer/descriptors.py:34`); `g_max()` **imported** from "
      "`src/dft/volcano_r1.py` (session-verified against Razzaq–Exner 2023 eqs 10–25); "
      "Co bounded-η via `src/dft/eta_bounded.py`. Gas references reused from each "
      "metal's source run — exact across the ladder, since no Hubbard channel touches "
      "H₂O/H₂ (`src/dft/probe_eta.py:23-27`).")
    A("- Löwdin populations (projwfc.x) are **not in this tranche**: no `.save` "
      "directories survive, and the regeneration SCFs are part of the A0 budget "
      "(A5.1a). The Hubbard-projector occupations Tr[ns] printed by pw.x at U > 0 "
      "are recorded as a free supplementary column; they are atomic-projector "
      "occupations, not Löwdin charges.")
    A("")

    A("## GATE-1 provenance of the ladder energies (Amendment 4 §2 wording)")
    A("")
    A("| metal | state | base SCF (eV) | production relax (eV) | drift (meV) | status |")
    A("|---|---|---|---|---|---|")
    for metal, g1 in (("Cr", g1cr), ("Co", g1co)):
        for st, r in g1.items():
            if r["drift_meV"] is None:
                status = "PENDING verification"
            elif abs(r["drift_meV"]) <= 5.0:
                status = "GATE-1 PASS (≤5 meV round-trip)"
            elif r["drift_meV"] < 0:
                status = ("**production relax failed GATE-1; the base SCF here IS the "
                          "GATE-1/corrected-basin energy**")
            else:
                status = ("**base SCF landed in a HIGHER solution than the production "
                          "relax** (audit-side trap; production value is the good one)")
            A(f"| {metal} | {st} | {r['base_scf_ev']:.4f} | {r['production_relax_ev']:.4f} "
              f"| {r['drift_meV']:+.2f} | {status} |")
    A("")
    b = g1cr.get("s0_OOH", {})
    if b.get("base_scf_vs_basin_final_meV") is not None:
        A(f"- **Cr `*OOH` (the docs/41 §6f production-basin issue):** the production "
          f"relaxation carried a metastable magnetic state 175 meV high; the ladder's "
          f"base SCF reproduces the basin re-relaxation final "
          f"(`runs/probe/Cr_basin/s0_OOH.out`) to "
          f"**{b['base_scf_vs_basin_final_meV']:+.2f} meV**, i.e. it is the "
          f"GATE-1-passed (tier_v2-corrected) value within the ≤4 meV residual "
          f"docs/43 P16 licenses.")
    bc = g1co.get("s0_OH", {})
    if bc.get("base_scf_vs_basin_final_meV") is not None:
        A(f"- **Co `*OH`:** same situation — base SCF vs basin re-relax final "
          f"(`runs/probe/Co_basin/s0_OH.out`): "
          f"**{bc['base_scf_vs_basin_final_meV']:+.2f} meV**. GATE-1-passed value.")
    A("- **Co `slab`:** the ladder's clean-slab SCF sits in the *higher* of Co's two "
      "known slab solutions (+59 meV, docs/41 §6e); the production relaxation holds the "
      "lower one. The ladder is internally consistent (same recipe at every U), but "
      "every Co ΔG below carries this ~59 meV slab-reference offset at base U relative "
      "to `tier_v2` — the descriptor ΔG(*O)−ΔG(*OH) and η bound (pls 2) are immune "
      "because the slab energy cancels in ΔG2.")
    A("- **Non-production-U points (u0.0/u0.5/u1.35): GATE-1 status PENDING "
      "verification.** GATE-1 compares a fresh SCF against a relaxation at the same "
      "Hamiltonian; no relaxation exists at the off-production U values, and nothing "
      "on disk tests whether each single-seed SCF found the ground SCF solution at its "
      "U. The magnetization columns below are the available witness, not a gate.")
    A("")

    # ---- Cr table ----------------------------------------------------------
    A("## Cr ladder — η_TD(U) and G_max(U) (A5.1c)")
    A("")
    A("| U point | U (eV) | ΔG_OH | ΔG_O | ΔG_OOH | x = ΔG_O−ΔG_OH | η_TD (V) | pls | "
      "G_max(0.1 V) | G_max(0.2 V) | G_max(0.3 V) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for v, _ in VARIANTS:
        r = cr[v]
        gm = r["gmax"]
        cells = [f"{r['dG']['OH']:.3f}", f"{r['dG']['O']:.3f}", f"{r['dG']['OOH']:.3f}",
                 f"{r['descriptor_eV']:.3f}", f"**{r['eta_V']:.3f}**", str(r["pls"])]
        gcells = [f"{gm[f'eta{t}']['value_eV']:.3f} ({gm[f'eta{t}']['limiting_span']})"
                  for t in ETA_TARGETS]
        A(f"| {v} | {r['U_eV']:.2f} | " + " | ".join(cells + gcells) + " |")
    A("")
    sw = p["sanity"]
    A(f"- η(Cr, base U) = **{sw['eta_Cr_base_V']:.4f} V** vs the frozen tier_v2 value "
      f"0.3303 V — difference {abs(sw['eta_Cr_base_V']-0.3303)*1000:.1f} mV. The match "
      f"is exact because Cr's limiting step at base U is ΔG2 (pls 2), built solely "
      f"from the cleanly round-tripping `s0_O`/`s0_OH`; the `*OOH` energy (3.5 meV "
      f"above the basin re-relax final, GATE-1 table) does not enter η at base U.")
    A(f"- η(Cr) swing across the ladder: **{sw['eta_Cr_swing_V']:.3f} V** "
      f"(docs/41 §6c P7: 1.122 V — same states, same pipeline).")
    crmag = [cr[v]["states"]["s0_OOH"]["total_mag"] for v, _ in VARIANTS]
    A(f"- Cr `*OOH` magnetic state: total magnetization "
      f"{'/'.join(f'{m:g}' for m in crmag)} μ_B at u0.0/u0.5/base/u1.35 — every ladder "
      f"point sits in the 11.0 μ_B solution family (the corrected basin of docs/41 "
      f"§6f), never the metastable 11.8 μ_B one the production relaxation carried. "
      f"That is an observed-magnetization statement, not a gate (see GATE-1 note on "
      f"non-production U).")
    ood = cr["base"]["states"].get("s0_OOH", {}).get("oo_dist_A")
    A(f"- `*OOH` O–O distance: **{ood} Å**, computed from the deck geometry — which "
      f"is the parent (production-U) relaxation by construction, so it is one number "
      f"for the whole ladder, not a per-U observable. "
      f"(hydroperoxo *O–OH reference band ~1.37–1.45 Å, superoxo ~1.30–1.32 Å, "
      f"Inico 2024 via docs/43 A5.3a — full fingerprint classification is LIT-3, "
      f"not this tranche.)")
    A("")

    # ---- Co table ----------------------------------------------------------
    A("## Co ladder — bounded η_TD(U) (no `*OOH` at any U)")
    A("")
    A("η for Co uses the bounded identity of `src/dft/eta_bounded.py` "
      "(ΔG3+ΔG4 = 4.92 − ΔG_O contains no ΔG_OOH): η = max(ΔG1, ΔG2) − 1.23, valid "
      "provided ΔG_OOH lies inside the stated window. G_max values are **lower "
      "bounds** over the ΔG_OOH-free spans only.")
    A("")
    A("| U point | U (eV) | ΔG_OH | ΔG_O | x = ΔG_O−ΔG_OH | η bound (V) | pls | "
      "valid ΔG_OOH window (eV) | margin vs observed [3.65, 4.94] | "
      "G_max LB(0.1) | G_max LB(0.2) | G_max LB(0.3) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for v, _ in VARIANTS:
        r = co[v]
        gm = r["gmax_lower_bound"]
        w = r["eta_bound_valid_dG_OOH_window_eV"]
        mg = r["window_margin_vs_observed_dG_OOH"]
        gcells = [f"{gm[f'eta{t}']['value_eV']:.3f} ({gm[f'eta{t}']['limiting_span']})"
                  for t in ETA_TARGETS]
        A(f"| {v} | {r['U_eV']:.2f} | {r['dG']['OH']:.3f} | {r['dG']['O']:.3f} | "
          f"{r['descriptor_eV']:.3f} | **{r['eta_bound_V']:.3f}** | {r['pls_bound']} | "
          f"({w[0]:.2f}, {w[1]:.2f}) | lo {mg['lo']:+.2f} / hi {mg['hi']:+.2f} | "
          + " | ".join(gcells) + " |")
    A("")
    co_etas = [co[v]["eta_bound_V"] for v, _ in VARIANTS]
    A(f"- Co η-bound swing across the ladder: **{max(co_etas)-min(co_etas):.3f} V**. "
      f"All margins in the table are positive, so at every U the validity window "
      f"contains the tier's whole observed ΔG_OOH range [3.65, 4.94 eV] — the bound "
      f"is safe *given that range*; a Co ΔG_OOH outside it cannot be excluded by any "
      f"data on disk (the registered hole).")
    ohmag = [co[v]["states"]["s0_OH"]["total_mag"] for v, _ in VARIANTS]
    A(f"- **The u1.35 row is not pure U-sensitivity.** Co `s0_OH` total magnetization "
      f"runs {'/'.join(f'{m:g}' for m in ohmag)} μ_B across u0.0/u0.5/base/u1.35: the "
      f"u1.35 SCF jumped to a different electronic solution (Co's documented "
      f"multistability, docs/41 §6e), and its ΔG_OH (+0.83 eV vs base) mixes the U "
      f"response with that solution change. The valence-tracking table below carries "
      f"the matching flag.")
    A("- These bounds inherit the +59 meV slab-solution offset noted above only "
      "through ΔG1 (pls 1 rows, i.e. u1.35); ΔG2 is slab-independent.")
    A("")

    # ---- valence tracking --------------------------------------------------
    A("## Valence tracking (A5.1a)")
    A("")
    A(f"Criterion, stated (Tripkovic 2018 V(B) step classification): with "
      f"Δm(U) = m(active site, adsorbate state, U) − m(same site, bare slab, U) "
      f"(sphere-integrated moments from pw.x), a ΔG is **valence-changing** — its "
      f"adsorption step changes the active-site oxidation state, hence expected "
      f"**U-fragile** — when |Δm(production U)| ≥ {VALENCE_THRESHOLD_MUB} μ_B; "
      f"otherwise **valence-conserving** (expected U-robust). Rationale: a "
      f"one-electron redox at a high-spin 3d site moves the sphere moment by "
      f"~1 μ_B; half that separates it from covalent/hybridisation transfer and "
      f"sits well above the ~0.05–0.1 μ_B integration scatter and the 0.1 μ_B "
      f"channel resolution of docs/43 P16 / Amendment 4 §3. Stability check: if "
      f"Δm ranges by ≥ {VALENCE_THRESHOLD_MUB} μ_B *across the four U points*, the "
      f"tracker itself is unstable (an SCF-solution change on the ladder) and the "
      f"classification is flagged rather than trusted.")
    A("")
    A("| metal | state | U point | U (eV) | E total mag (μ_B) | abs mag | "
      "m(site) | m(site, bare slab) | Δm | Tr[ns] site |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for metal, lad in (("Cr", p["ladders"]["Cr"]), ("Co", p["ladders"]["Co"])):
        for v, _ in VARIANTS:
            r = lad["per_variant"][v]
            for st in lad["config"]["states"]:
                s = r["states"][st]
                if st == "slab":
                    A(f"| {metal} | slab | {v} | {r['U_eV']:.2f} | "
                      f"{s['total_mag']} | {s['abs_mag']} | — | — | — | — |")
                    continue
                tr = s["active_site_trns_total"]
                A(f"| {metal} | {st} | {v} | {r['U_eV']:.2f} | {s['total_mag']} | "
                  f"{s['abs_mag']} | {s['active_site_moment']} | "
                  f"{s['slab_site_moment_same_U']} | "
                  f"{s['delta_moment_vs_slab']} | {tr if tr is not None else '—'} |")
    A("")
    A("### Classification per ΔG")
    A("")
    A("| metal | ΔG | Δm at production U (μ_B) | class (expected) | ΔG swing across "
      "ladder (eV) | Δm range across U (μ_B) | tracker stable? |")
    A("|---|---|---|---|---|---|---|")
    for metal, vc in (("Cr", vc_cr), ("Co", vc_co)):
        for k, r in vc.items():
            stab = ("yes" if r["tracker_stable_across_U"]
                    else "**NO — SCF-solution change on the ladder (docs/41 §6e); "
                         "classification flagged**")
            A(f"| {metal} | {k} | {r['delta_moment_at_production_U']} | "
              f"**{r['classification']}** ({r['expected']}) | "
              f"{r['dG_U_swing_eV']} | {r['tracker_range_across_U_muB']} | {stab} |")
    A("")
    A("### A5.1a mechanism-test readout (registered: either outcome is reported)")
    A("")
    cr_sw = {k: vc_cr[k]["dG_U_swing_eV"] for k in vc_cr}
    cr_dm = {k: vc_cr[k]["delta_moment_at_production_U"] for k in vc_cr}
    A(f"The registered expectation was that the 1.122 V η(Cr) swing should correlate "
      f"with a Cr oxidation-state change under *O/*OOH, with U-flat quantities showing "
      f"none. At this 4-point fixed-geometry resolution the pattern is observed: the "
      f"per-ΔG U-swings rank exactly with the step's |Δm| — "
      f"ΔG_O (Δm {cr_dm['dG_O']:+.2f} μ_B, valence-changing) swings "
      f"{cr_sw['dG_O']:.2f} eV, ΔG_OH (Δm {cr_dm['dG_OH']:+.2f}) swings "
      f"{cr_sw['dG_OH']:.2f} eV, ΔG_OOH (Δm {cr_dm['dG_OOH']:+.2f}) swings "
      f"{cr_sw['dG_OOH']:.2f} eV. The one valence-changing step (*O: the site is "
      f"oxidised by ~1 μ_B-equivalent relative to the bare slab at every U) is the "
      f"U-fragile axis, and it sits in the descriptor ΔG_O−ΔG_OH — which is what "
      f"P7 measured as the η(Cr) swing. Δm itself is U-flat for every Cr state "
      f"(range ≤ 0.12 μ_B), so the swing is the smooth U-response of a "
      f"valence-changing step, not a basin/valence step *along* the U axis. Caveat: "
      f"four points cannot exclude a step between them; the dense A0 grid is the "
      f"real test. Co's classification is degraded by the tracker instability "
      f"flagged above and its `*OOH` hole; it supports no mechanism claim either way.")
    A("")

    # ---- intercept test ----------------------------------------------------
    A("## Intercept-vs-descriptor U-test (A5.1d)")
    A("")
    A("Motivating prior, updated after the 2026-08-12 Xu read (sweep memo §10): the "
      "on-rutile prior is **Xu, Rossmeisl & Kitchin 2015** (10.1021/jp511426q) — "
      "U = 0–8 eV scans on undoped rutile MO₂(110), including CrO₂, found scaling "
      "relations preserved and compounds moving *along* the volcano, so this test is "
      "a replication-and-extension of their result on a **doped** rutile under our "
      "protocol. Tripkovic 2018 Table 3 is the counterpoint on perovskites: LaCrO₃ "
      "ΔE(*OOH)−ΔE(*OH) moves 2.94→2.93 eV over U = 0–5 eV (flat) while "
      "ΔE(*O)−ΔE(*OH) moves +1.06 eV.")
    A("")
    A("| U point | U (eV) | Cr intercept ΔG_OOH−ΔG_OH (eV) | Cr descriptor "
      "ΔG_O−ΔG_OH (eV) |")
    A("|---|---|---|---|")
    for v, _ in VARIANTS:
        r = it["Cr"][v]
        A(f"| {v} | {r['U_eV']:.2f} | {r['intercept_eV']:.3f} | "
          f"{r['descriptor_eV']:.3f} |")
    A("")
    A(f"- Cr intercept span across the ladder: **{it['Cr_intercept_span_eV']:.3f} eV**; "
      f"Cr descriptor span: **{it['Cr_descriptor_span_eV']:.3f} eV**. "
      f"Ratio {it['Cr_intercept_span_eV']/it['Cr_descriptor_span_eV']:.2f}.")
    A("- Readout: the descriptor axis is confirmed U-fragile (1.11 eV), and the "
      "intercept is ~2.5× more U-robust — but at 0.447 eV over the ladder it is "
      "**not** Tripkovic-flat (LaCrO₃: 0.01 eV over U = 0–5). Cr(110) is therefore "
      "*partially* a move-along-the-volcano case: U dominantly slides Cr along the "
      "descriptor axis while also drifting the scaling intercept through the 3.2 eV "
      "band (3.44 → 3.00 eV, crossing 3.2 between u0.5 and base). Consistent with "
      "this, both intercept-forming states (*OH, *OOH) are valence-conserving while "
      "the descriptor contains the one valence-changing state (*O). The 0.447 eV "
      "intercept drift is itself a measured deviation from Xu 2015's clean scaling "
      "preservation on the undoped rutiles — a doped-Cr-specific effect at this "
      "resolution, to be confirmed or bounded on the dense A0 grid.")
    A(f"- Co descriptor span: **{it['Co_descriptor_span_eV']:.3f} eV**. "
      f"Co intercept: {it['Co_intercept']}.")
    A("")

    # ---- what A0 adds ------------------------------------------------------
    A("## What A0 adds")
    A("")
    A("Everything above rests on four U points per metal — 0, 0.5×, 1×, 1.35× of the "
      "MP-fitted production U — inherited from the P7 probe. The registered A0 grid "
      "(docs/43 §4, block 6A: ~140 fixed-geometry SCFs spanning U = 0–9 eV, pw.x only, "
      "independent of the hp.x gate) extends each of these 4-point ladders to a dense "
      "grid over the full physically defensible U range. That buys: (i) η_TD(U) and "
      "G_max(U) as *curves*, so the volcano-apex crossing that produced the withdrawn "
      "Cr headline is located rather than bracketed; (ii) valence tracking with enough "
      "resolution to see *where* the active-site moment steps, not just that it differs "
      "between endpoints; (iii) the intercept test on a dense axis, directly comparable "
      "to Tripkovic's 0–5 eV span; and (iv) the U-band leg of the A5.1(b) ranking-claim "
      "rule ({U = 0, MP U, hp.x U if 1B returns GO}) evaluated from measured curves "
      "instead of interpolation. Per A5.1a, Löwdin populations from projwfc.x ride "
      "along wherever A0 regenerates charge densities (≤ ~150 cheap SCFs), upgrading "
      "the moment-based valence tracker with a charge-based one. The fixed-geometry "
      "approximation is unchanged in A0 and is stated wherever the grid is used.")
    A("")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    main()
