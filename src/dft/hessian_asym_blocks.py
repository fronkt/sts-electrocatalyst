"""Diagnostic: the Hessian-asymmetry sigma_F estimator, split by block. CHANGES NOTHING.

hessian_analyze.py derives sigma_F from |H - H^T| over ALL off-diagonal pairs (docs/43
s3-A.4). On a mirror-symmetric adsorbate the (y, xz) cross block is fixed at exactly zero by
symmetry, and with a FORWARD y-difference (am.4 s7) its row carries an O(delta) anharmonic
term, so the estimator reads anharmonicity there, not noise (docs/49 s4). This script
asks the next question: is the asymmetry in the OTHER blocks noise? A noise-driven
asymmetry gives a delta-INVARIANT sigma_F (rms asym ~ sigma_F/delta, and the estimator
multiplies by delta). A truncation-driven asymmetry does not: central differences carry
O(delta^2) asymmetry, so the recovered "sigma_F" grows as delta^3.

Run on two directories built at different delta and compare:

    PYTHONPATH=src python src/dft/hessian_asym_blocks.py runs/probe/Cr_hess runs/probe_d02/Cr_hess

Output per directory: max / rms |H_ij - H_ji| and the analyzer-convention sigma_F
(rms * delta, converted to Ry/bohr) for: all pairs, the (y,xz) cross block, the non-cross
pairs, the y-y block, the xz-xz block; plus the mode-#0 floor the analyzer's own
spectrum() would return if only the non-cross pairs fed sigma_F (arithmetic, not a verdict).
Reuses hessian_analyze.parse_scf_out / build_hessian / spectrum unchanged.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hessian_analyze as ha  # noqa: E402

RY = ha.RY_BOHR_TO_EV_A


def _sigma_ry(vals: np.ndarray, delta: float) -> float:
    rms = math.sqrt(float(np.mean(vals ** 2))) if vals.size else 0.0
    return rms * delta / RY


def analyse(d: str) -> dict:
    man = json.load(open(os.path.join(d, "hess_manifest.json"), encoding="utf-8"))
    outs = {rec["job"]: ha.parse_scf_out(os.path.join(d, rec["job"] + ".out"))
            for rec in man["jobs"]}
    hb = ha.build_hessian(man, outs, set())
    H, coords, delta = hb["H"], hb["coords"], man["delta_nominal_angstrom"]
    n = len(coords)
    A = np.abs(H - H.T)
    iu = np.triu_indices(n, 1)
    v = A[iu]
    isy = np.array([ax == "y" for _a, ax in coords])
    cross = np.array([isy[i] != isy[j] for i, j in zip(*iu)])
    yy = np.array([isy[i] and isy[j] for i, j in zip(*iu)])
    xz = np.array([(not isy[i]) and (not isy[j]) for i, j in zip(*iu)])
    blocks = {
        "all pairs": v,
        "cross (y,xz)": v[cross],
        "non-cross": v[~cross],
        "y-y block": v[yy],
        "xz-xz block": v[xz],
    }
    out = dict(dir=d, delta=delta, n=n, blocks={})
    for name, vals in blocks.items():
        out["blocks"][name] = dict(
            max_eV_A2=float(vals.max()) if vals.size else 0.0,
            rms_eV_A2=math.sqrt(float(np.mean(vals ** 2))) if vals.size else 0.0,
            sigma_F_Ry_bohr=_sigma_ry(vals, delta),
            n_pairs=int(vals.size),
        )
    # mode-0 floor if sigma_F came from the non-cross pairs only (analyzer's own formula)
    sigma_F_eV_A = _sigma_ry(v[~cross], delta) * RY
    sigma_H = sigma_F_eV_A / (math.sqrt(2) * delta)
    root_m = np.sqrt(hb["masses"])
    row_scale = np.array([2.0 if ax == "y" else 1.0 for _a, ax in coords]) \
        if man["mirror_plane"] else np.ones(n)
    sig_D = (sigma_H * row_scale[:, None]) / np.outer(root_m, root_m)
    modes = ha.spectrum(hb["D"], coords, hb["masses"], sig_D)
    m0 = modes[0]
    out["mode0_noncross_floor"] = dict(nu_cm1=m0["nu_cm1"], imaginary=m0["imaginary"],
                                       nu_floor_cm1=m0["nu_floor_cm1"],
                                       fy=m0["fy_massweighted"])
    return out


def main() -> int:
    dirs = sys.argv[1:]
    if not dirs:
        print(__doc__)
        return 2
    res = [analyse(d) for d in dirs]
    for r in res:
        print(f"== {r['dir']}  delta = {r['delta']} A  n = {r['n']}")
        for name, b in r["blocks"].items():
            print(f"  {name:14s} n={b['n_pairs']:2d}  max {b['max_eV_A2']:.3e}  "
                  f"rms {b['rms_eV_A2']:.3e} eV/A^2  -> sigma_F {b['sigma_F_Ry_bohr']:.3e} Ry/bohr")
        m = r["mode0_noncross_floor"]
        print(f"  mode #0 {'i' if m['imaginary'] else ''}{m['nu_cm1']:.1f} cm^-1, f_y {m['fy']:.3f}; "
              f"floor if sigma_F came from non-cross pairs only: i{m['nu_floor_cm1']:.1f}")
    if len(res) >= 2:
        a, b = res[0], res[1]
        ratio = b["delta"] / a["delta"]
        print(f"\nscaling from delta {a['delta']} -> {b['delta']} (x{ratio:.2f}); "
              f"noise would give x1.00, central-difference truncation x{ratio**3:.2f}, "
              f"forward-difference truncation x{ratio**2:.2f}:")
        for name in a["blocks"]:
            sa, sb = a["blocks"][name]["sigma_F_Ry_bohr"], b["blocks"][name]["sigma_F_Ry_bohr"]
            print(f"  {name:14s} sigma_F x{(sb / sa) if sa else float('nan'):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
