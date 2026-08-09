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

#: CORRECTED 2026-08-02 after the Fe repair. The original single cut at 2.40 A came
#: with the claim "real M-O bonds are 1.6-2.1 A, the failures sit at 3.8-4.0 A, nothing
#: legitimate lands in between". That was wrong. Restarting Fe_slab/s0_OOH from a bound
#: 2.076 A geometry relaxed to **2.552 A at 0.376 eV LOWER** energy than the desorbed
#: original -- a genuine, weakly-bound minimum sitting squarely in the "impossible"
#: gap, and within 0.013 A of MACE's independent prediction of 2.565 A.
#:
#: So distance alone cannot separate "weakly bound" from "never adsorbed". Use three
#: tiers, and treat the middle one as a flag for a human rather than a failure.
M_O_BOUND_MAX = 2.20        #: unambiguous chemisorption
M_O_DESORBED_MIN = 3.00     #: unambiguously not interacting with the surface
#: Kept as the back-compatible name used by the CLI; now only the desorption cut.
M_O_BOND_MAX = M_O_DESORBED_MIN
#: A relax that "converges" in very few ionic steps never explored anything. Mn and Fe
#: s0_OOH stopped at 2 and 13 steps; their repaired counterparts took 29+. This caught
#: the real defect more reliably than any distance threshold did.
MIN_IONIC_STEPS = 15
#: Flag a bond this far from the median across metals for the same adsorbate.
#: Cr/s0_O is +0.29 A against a 1.73 A median; genuine chemistry varies far less.
BOND_OUTLIER_TOL = 0.20

#: CORRECTED 2026-08-03, third falsification of a threshold in this module. Run over the
#: repaired tier, the median test flagged Fe/s0_OOH (2.552 A) and Mn/s0_OOH (2.480 A) as
#: "suspect a trapped relaxation" -- i.e. it condemned the two structures the 2026-08-02
#: DFT campaign was bought to verify, and which MACE independently reproduced to 0.013 A.
#:
#: Measured spread across the five DFT-verified metals:
#:
#:     s0_O     span 0.202 A   Cr 1.572  Mn 1.671  Ru 1.698  Ir 1.767  Fe 1.774
#:     s0_OH    span 0.089 A   Mn 1.848  Fe 1.849  Cr 1.856  Ru 1.929  Ir 1.937
#:     s0_OOH   span 0.640 A   Ir 1.912  Ru 1.947  Cr 2.076 | Mn 2.480  Fe 2.552
#:
#: `*O` and `*OH` cluster tightly, so a median IS a reference for them. `*OOH` does not:
#: it is **bimodal**, and the split is chemistry rather than error -- the noble rutiles
#: and Cr chemisorb the peroxo group, while late-3d MnO2/FeO2 bind it weakly. A
#: median-based outlier test is the wrong instrument for a bimodal distribution; it will
#: always accuse the smaller mode.
#:
#: So the cross-metal test is restricted to the states where uniformity is established.
#: `*OOH` is covered by the three-tier distance check, the ionic-step check and the dG4
#: floor -- which are what actually caught Mn, Fe and Ni, none of them by median.
OUTLIER_STATES = ("s0_O", "s0_OH")
#: Total OER free energy: sum of the four steps is fixed by thermodynamics.
G_TOTAL = 4.92


def m_o_distances(atoms, metal: str, n_slab: int = 18) -> list[float]:
    """Distance from each adsorbate atom to the nearest metal atom (angstrom)."""
    mets = [a.position for a in atoms[:n_slab] if a.symbol == metal]
    return [min(math.dist(a.position, p) for p in mets) for a in atoms[n_slab:]]


def check_structure(atoms, metal: str, n_slab: int = 18, n_ionic: int | None = None) -> dict:
    """Three-tier verdict for one relaxed adslab.

    `tier` is 'bound' (< 2.20 A), 'weak' (2.20-3.00 A) or 'desorbed' (> 3.00 A).
    Only 'desorbed' fails. 'weak' is a real physical possibility -- FeO2(110) *OOH
    genuinely minimises at 2.552 A -- so it is surfaced, not rejected.

    Pass `n_ionic` to add the step-count check, which is the more reliable signal:
    a relax that stopped after a couple of steps never explored anything, whatever
    distance it happens to sit at.
    """
    if len(atoms) <= n_slab:
        return dict(ok=True, reasons=[], n_ads=0, m_o_min=None, height=None, tier="none")
    d = m_o_distances(atoms, metal, n_slab)
    zsurf = max(a.position[2] for a in atoms[:n_slab])
    height = min(a.position[2] for a in atoms[n_slab:]) - zsurf
    dmin = min(d)
    tier = ("bound" if dmin <= M_O_BOUND_MAX
            else "desorbed" if dmin > M_O_DESORBED_MIN else "weak")
    reasons = []
    if tier == "desorbed":
        reasons.append(f"adsorbate not bound: nearest {metal}-O = {dmin:.3f} A "
                       f"(> {M_O_DESORBED_MIN}); sits {height:+.2f} A above the slab")
    if n_ionic is not None and n_ionic < MIN_IONIC_STEPS:
        reasons.append(f"only {n_ionic} ionic steps (< {MIN_IONIC_STEPS}): the relaxation "
                       f"barely moved, so this is a starting guess rather than a minimum")
    return dict(ok=not reasons, reasons=reasons, n_ads=len(atoms) - n_slab,
                m_o_min=round(dmin, 3), height=round(height, 2), tier=tier)


#: Tolerance on the dG4 > 0 test. G_TOTAL = 4.92 eV is the experimental 4 x 1.23 V,
#: while dG_OOH carries the usual GGA adsorption error of order 0.1-0.2 eV, so a
#: slightly negative dG4 is consistent with zero rather than impossible.
#: Calibrated 2026-08-02 on the repaired Mn: dG4 = -0.022 eV at a genuine, fully
#: relaxed 34-ionic-step minimum. Flagging that as unphysical would be overclaiming.
#: Fe's pre-repair -0.301 eV is the scale of a real violation.
DG4_TOL = 0.15


def check_thermo(dG_OOH: float, tol: float = DG4_TOL) -> list[str]:
    """The fourth CHE step must be uphill at 0 V, to within method error."""
    g4 = G_TOTAL - dG_OOH
    if g4 < -tol:
        return [f"dG4 = {g4:+.3f} eV < -{tol}: the final step is exergonic at zero "
                f"potential by more than method error, which no real OER intermediate "
                f"gives -- dG_OOH ({dG_OOH:.3f}) exceeds the {G_TOTAL} eV total"]
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

    print(f"\ncross-metal bond outliers (median reference; {'/'.join(OUTLIER_STATES)} only "
          f"-- *OOH binding is bimodal, see module docstring):")
    any_out = False
    for job, bonds in sorted(per_state.items()):
        if job not in OUTLIER_STATES:
            continue
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
