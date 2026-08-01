"""Chemical validity of a relaxed adsorbate structure -- the gap `qe_qc` cannot see.

`qe_qc.py` answers "did pw.x converge honestly?": SCF converged, forces below
threshold, an energy exists. Every check in it is numerical. A run can pass all of
them and still be chemically meaningless, and on 2026-08-01 the R3 MLIP evaluation
surfaced two such cases in our own reference set:

  1. **Cr_slab/s0_O** -- force-converged (28 ionic steps, last energy change 5e-4 eV)
     at a Cr-O bond of **2.016 A**, while Mn/Fe/Ru/Ir all relax to 1.67-1.77 A and
     every one of them explores 1.62-1.83 A on the way down. MACE-MPA-0 finds a
     structure 1.06 eV lower at 1.609 A. A genuine stationary point, almost certainly
     not the right one -- BFGS descended from the builder's 3.07 A and stalled.
  2. **Mn_slab/s0_OOH and Fe_slab/s0_OOH** -- "converged" in 2 and 13 ionic steps
     with the adsorbate 3.83/3.95 A from the metal and 2.15/2.20 A above the slab.
     The *OOH never adsorbed; the run converged because a desorbed molecule has no
     forces on it. Both give dG_OOH > 4.92 eV, i.e. a *negative* fourth CHE step,
     which is thermodynamically impossible for a real OER intermediate.

Neither is detectable from SCF convergence or forces. Both are obvious from geometry.

The checks here are deliberately weak-but-unambiguous: they are meant to catch
"this is not the structure we think it is", not to adjudicate fine energetics.

    PYTHONPATH=src python src/dft/adsorbate_qc.py check runs
"""
from __future__ import annotations

import argparse
import glob
import math
import os
import sys

#: An adsorbate O further than this from the nearest metal is not chemisorbed.
#: Real M-O bonds here are 1.6-2.1 A; the failures sit at 3.8-4.0 A. Nothing
#: legitimate lands in between, so the exact cut is not load-bearing.
M_O_BOND_MAX = 2.40
#: Flag a bond this far from the median across metals for the same adsorbate.
#: Cr/s0_O is +0.29 A against a 1.73 A median; genuine chemistry varies far less.
BOND_OUTLIER_TOL = 0.20
#: Total OER free energy: sum of the four steps is fixed by thermodynamics.
G_TOTAL = 4.92


def m_o_distances(atoms, metal: str, n_slab: int = 18) -> list[float]:
    """Distance from each adsorbate atom to the nearest metal atom (angstrom)."""
    mets = [a.position for a in atoms[:n_slab] if a.symbol == metal]
    return [min(math.dist(a.position, p) for p in mets) for a in atoms[n_slab:]]


def check_structure(atoms, metal: str, n_slab: int = 18) -> dict:
    """Bound/unbound verdict for one relaxed adslab."""
    if len(atoms) <= n_slab:
        return dict(ok=True, reasons=[], n_ads=0, m_o_min=None, height=None)
    d = m_o_distances(atoms, metal, n_slab)
    zsurf = max(a.position[2] for a in atoms[:n_slab])
    height = min(a.position[2] for a in atoms[n_slab:]) - zsurf
    reasons = []
    if min(d) > M_O_BOND_MAX:
        reasons.append(f"adsorbate not bound: nearest {metal}-O = {min(d):.3f} A "
                       f"(> {M_O_BOND_MAX}); sits {height:+.2f} A above the slab")
    return dict(ok=not reasons, reasons=reasons, n_ads=len(atoms) - n_slab,
                m_o_min=round(min(d), 3), height=round(height, 2))


def check_thermo(dG_OOH: float) -> list[str]:
    """The fourth CHE step must be uphill at 0 V."""
    g4 = G_TOTAL - dG_OOH
    if g4 < 0:
        return [f"dG4 = {g4:+.3f} eV < 0: the final step is exergonic at zero "
                f"potential, which no real OER intermediate gives -- dG_OOH "
                f"({dG_OOH:.3f}) exceeds the {G_TOTAL} eV total"]
    return []


def cross_metal_outliers(bonds: dict, tol: float = BOND_OUTLIER_TOL) -> list[str]:
    """Flag a metal whose M-O bond deviates from the median for the same adsorbate.

    Only meaningful with >=3 metals; with fewer, the median is not a reference.
    """
    if len(bonds) < 3:
        return []
    vals = sorted(bonds.values())
    med = vals[len(vals) // 2] if len(vals) % 2 else 0.5 * (vals[len(vals) // 2 - 1] + vals[len(vals) // 2])
    out = []
    for m, v in sorted(bonds.items()):
        if abs(v - med) > tol:
            out.append(f"{m}: M-O = {v:.3f} A vs median {med:.3f} across metals "
                       f"({v - med:+.3f}) -- suspect a trapped relaxation")
    return out


def cmd_check(args):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ase.io import read
    frames = {}
    for at in read(args.frames, ":"):
        frames.setdefault(at.info["source"], []).append((int(at.info["step"]), at))

    metal_of = lambda src: src.split("/")[0].split("_")[0]  # noqa: E731
    bad, per_state = [], {}
    print(f"{'source':<22}{'n_ads':>6}{'M-O':>8}{'height':>8}  verdict")
    for src in sorted(frames):
        job = src.split("/")[-1]
        if job in ("H2", "H2O", "slab"):
            continue
        at = sorted(frames[src])[-1][1]
        m = metal_of(src)
        r = check_structure(at, m)
        per_state.setdefault(job, {})[m] = r["m_o_min"]
        v = "OK" if r["ok"] else "UNBOUND"
        print(f"{src:<22}{r['n_ads']:>6}{r['m_o_min']:>8.3f}{r['height']:>8.2f}  {v}")
        if not r["ok"]:
            bad.append((src, r["reasons"]))

    print("\ncross-metal bond outliers (same adsorbate, median reference):")
    any_out = False
    for job, bonds in sorted(per_state.items()):
        clean = {k: v for k, v in bonds.items() if v is not None and v < M_O_BOND_MAX}
        for msg in cross_metal_outliers(clean):
            print(f"  {job}: {msg}")
            any_out = True
    if not any_out:
        print("  none")

    if bad:
        print(f"\n{len(bad)} structure(s) failed the bound-adsorbate check:")
        for s, rs in bad:
            print(f"  {s}: {'; '.join(rs)}")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="structural validity of relaxed adslabs")
    c.add_argument("root", nargs="?", default="runs")
    c.add_argument("--frames", default="data/qe_frames.extxyz")
    c.set_defaults(func=cmd_check)
    a = ap.parse_args()
    raise SystemExit(a.func(a))


if __name__ == "__main__":
    main()
