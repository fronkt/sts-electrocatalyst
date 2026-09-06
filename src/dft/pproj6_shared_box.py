"""Shared-constants sensitivity of the six-metal P-PROJ-6 readout (A12.R11).

The docs/84 dated correction of 2026-09-05 established that a paired CHE
difference is piecewise affine in the ZPE/TS constants, so a 27-point grid
does not certify a box. This script applies the same continuous test to the
six-metal arm banked in docs/figs/pproj6_readout.json, at the +/-0.05 eV
shared-correction half-width the campaign uses everywhere else.

Two questions, answered separately because they are different:

1. Per metal: the interval of eta(ortho) - eta(atomic) over the box, the
   potential-limiting-step pairs reachable, and whether the nominal pair
   dominates at all eight vertices (in which case it dominates throughout,
   since each step difference is affine in the correction).
2. Jointly: ONE constants table serves every metal and both legs
   (src/dft/pproj6_readout.py reads `zpe.step_constants` once), so the
   count of FIRES rows must be evaluated at a single shared correction, not
   assembled from per-metal extremes. A dense grid over the box gives the
   set of counts and the A12.R3 class verdict at every point.

Reads only the banked JSON. Writes docs/figs/pproj6_shared_box.json.
No registered number, band or verdict is re-scored; this is a sensitivity
calculation, not a probability or a physical uncertainty. Cr is reported as
the calibration row and enters no count (A12.R2).

Run from any directory:
    PYTHONPATH=src python src/dft/pproj6_shared_box.py
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

try:  # under pytest `src/` is on sys.path (conftest.py); as a script `src/dft/` is
    from dft.che_box_robustness import STEP_RESPONSE, analyze_pair, che_steps
except ImportError:
    from che_box_robustness import STEP_RESPONSE, analyze_pair, che_steps

ROOT = Path(__file__).resolve().parents[2]
BANKED = ROOT / "docs/figs/pproj6_readout.json"
OUTPUT = ROOT / "docs/figs/pproj6_shared_box.json"

# A12.R3, transcribed from src/dft/pproj6_readout.py:16-20.
VERDICT = {5: "CONFIRMED", 4: "CONFIRMED", 3: "MIDDLE BAND", 2: "MIDDLE BAND",
           1: "NOT MET", 0: "FALSIFIED"}


def band(abs_d_eta: float, fire_v: float, null_v: float) -> str:
    return "FIRES" if abs_d_eta > fire_v else ("NULL" if abs_d_eta < null_v else "INTERMEDIATE")


def _grid(half_width: float, n: int) -> np.ndarray:
    g = np.linspace(-half_width, half_width, n)
    return np.array(list(itertools.product(g, g, g)))


def _vertices(half_width: float) -> np.ndarray:
    return np.array(list(itertools.product((-half_width, half_width), repeat=3)))


def build(source: Path = BANKED, half_width: float = 0.05, grid_points: int = 101) -> dict:
    raw = source.read_bytes()
    banked = json.loads(raw)
    fire_v, null_v = banked["thresholds"]["fire_V"], banked["thresholds"]["null_V"]
    metals = banked["metals"]
    blind = [m for m, r in metals.items() if r["role"] == "blind"]
    if sorted(blind) != sorted(banked["blind_denominator"]):
        raise ValueError("blind roster does not match the banked denominator")

    grid = _grid(half_width, grid_points)
    vertices = _vertices(half_width)
    shifted_grid = grid @ STEP_RESPONSE.T
    shifted_vertices = vertices @ STEP_RESPONSE.T

    per_metal, abs_on_grid = {}, {}
    for m, r in metals.items():
        sa, so = che_steps(r["dG_atomic"]), che_steps(r["dG_ortho"])
        if not (np.allclose(sa, r["steps_atomic"], atol=1e-9) and np.allclose(so, r["steps_ortho"], atol=1e-9)):
            raise ValueError(f"{m}: banked steps do not reproduce from banked dG")
        nominal = float(max(so) - max(sa))
        if abs(nominal - r["d_eta_V"]) > 1e-9:
            raise ValueError(f"{m}: banked d_eta_V does not reproduce")
        pair = [int(np.argmax(sa)) + 1, int(np.argmax(so)) + 1]
        if pair != [r["pls_atomic"], r["pls_ortho"]]:
            raise ValueError(f"{m}: banked pls pair does not reproduce")

        box = analyze_pair(r["dG_atomic"], r["dG_ortho"], half_width)
        va, vo = sa + shifted_vertices, so + shifted_vertices
        fixed_pair = bool(np.all(va.argmax(1) + 1 == pair[0]) and np.all(vo.argmax(1) + 1 == pair[1]))
        d_grid = (so + shifted_grid).max(1) - (sa + shifted_grid).max(1)
        abs_on_grid[m] = np.abs(d_grid)
        lo, hi = box["delta_eta_range_V"]
        # every interval here has one sign; assert rather than assume
        if lo * hi < 0:
            raise ValueError(f"{m}: d_eta changes sign inside the box; abs interval is not [|lo|,|hi|]")
        abs_lo, abs_hi = sorted((abs(lo), abs(hi)))
        # the interval is connected, so it reaches every band it crosses
        reachable = set()
        if abs_lo < null_v:
            reachable.add("NULL")
        if abs_hi > fire_v:
            reachable.add("FIRES")
        if abs_lo <= fire_v and abs_hi >= null_v:
            reachable.add("INTERMEDIATE")
        per_metal[m] = {
            "role": r["role"],
            "banked_d_eta_V": r["d_eta_V"],
            "banked_band": r["band"],
            "banked_pair": pair,
            "nominal_pair_dominates_all_vertices": fixed_pair,
            "closed_pairs": box["closed_pairs"],
            "strict_pairs": box["strict_pairs"],
            "d_eta_range_V": [lo, hi],
            "abs_d_eta_range_V": [abs_lo, abs_hi],
            "bands_reachable": sorted(reachable),
            "grid_abs_d_eta_range_V": [float(abs_on_grid[m].min()), float(abs_on_grid[m].max())],
            "minimum_witness_correction_eV": box["minimum"]["correction_eV"],
            "maximum_witness_correction_eV": box["maximum"]["correction_eV"],
        }

    fires = sum((abs_on_grid[m] > fire_v).astype(int) for m in blind)
    nulls = sum((abs_on_grid[m] < null_v).astype(int) for m in blind)
    norms = np.abs(grid).sum(1)
    count_witnesses = {}
    for c in sorted(set(fires.tolist())):
        idx = np.flatnonzero(fires == c)
        i = idx[np.argmin(norms[idx])]
        count_witnesses[str(c)] = {
            "grid_points": int(len(idx)),
            "smallest_norm_witness_eV": {sp: float(v) for sp, v in zip(("OH", "O", "OOH"), grid[i])},
            "abs_d_eta_V": {m: float(abs_on_grid[m][i]) for m in blind},
            "bands": {m: band(float(abs_on_grid[m][i]), fire_v, null_v) for m in blind},
        }
    verdicts = sorted({VERDICT[int(c)] for c in set(fires.tolist())})
    nominal_index = int(np.flatnonzero(norms == 0)[0])

    return {
        "status": "sensitivity calculation; no registered number, band or verdict re-scored",
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "implementation_sha256": {
            "src/dft/pproj6_shared_box.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "src/dft/che_box_robustness.py": hashlib.sha256(
                (Path(__file__).with_name("che_box_robustness.py")).read_bytes()).hexdigest(),
        },
        "arm": {"rung": banked["rung"], "U_eV": banked["U"], "cell": "1x1 (docs/83 dated addendum 2026-09-05)"},
        "half_width_eV": half_width,
        "thresholds": {"fire_V": fire_v, "null_V": null_v, "rule": "A12.R3, strict > and <"},
        "shared_correction_scope": "one OH/O/OOH correction applied to both legs of every metal at once",
        "grid_points_per_axis": grid_points,
        "per_metal": per_metal,
        "joint": {
            "blind_denominator": blind,
            "nominal_fires_count": int(fires[nominal_index]),
            "fires_count_min": int(fires.min()),
            "fires_count_max": int(fires.max()),
            "null_count_min": int(nulls.min()),
            "null_count_max": int(nulls.max()),
            "class_verdicts_reachable": verdicts,
            "count_witnesses": count_witnesses,
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--half-width", type=float, default=0.05)
    parser.add_argument("--grid", type=int, default=101)
    parser.add_argument("--json", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    data = build(half_width=args.half_width, grid_points=args.grid)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    for m, r in data["per_metal"].items():
        lo, hi = r["abs_d_eta_range_V"]
        print(f"{m:2s} {r['role']:<22s} banked {r['banked_d_eta_V']:+.4f} {r['banked_band']:<12s}"
              f" |d-eta| in [{lo:.4f}, {hi:.4f}] pairs {r['closed_pairs']}"
              f" fixed-pair={r['nominal_pair_dominates_all_vertices']} bands {r['bands_reachable']}")
    j = data["joint"]
    print(f"joint FIRES count over the box: {j['fires_count_min']}..{j['fires_count_max']} of 5"
          f" (nominal {j['nominal_fires_count']}); class verdicts reachable: {j['class_verdicts_reachable']}")
    print(args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
