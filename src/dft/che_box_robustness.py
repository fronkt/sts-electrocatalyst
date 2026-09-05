"""Continuous shared-correction sensitivity of a pair of CHE ladders.

For corrections x = (dOH, dO, dOOH), each ladder is s + A @ x, where
A has rows (1,0,0), (-1,1,0), (0,-1,1), (0,0,-1). The paired overpotential
difference is max(right) - max(left). It is piecewise affine, not affine:
checking cube corners does not establish its extrema or limiting-step pairs.

This helper enumerates the 16 pairs of potentially limiting steps. On each
closed region their dominance conditions are linear inequalities, and their
difference is affine. Linear programming therefore finds the full continuous
box range, including boundaries and ties. A separate maximum-margin problem
distinguishes strict pairs from pairs feasible only at a tie (within the stated
numerical tolerance). No kinetic rate-limiting step is inferred.

Inputs are nominal adsorption FREE energies, already including any nominal
corrections. Perturbations are shared between the two legs and independent
between OH/O/OOH. This is sensitivity to that chosen box, not a probability
distribution or a physical uncertainty calibration. Results are numerical LP
solutions, not exact-arithmetic certificates. No registered verdict is scored.

Requires NumPy and SciPy in the research environment, outside silentgate.
Example (OH, O, OOH order throughout):
    python src/dft/che_box_robustness.py --left 2.154 4.147 4.597 \
        --right 2.326 4.499 4.626 --half-width 0.1
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import linprog

SPECIES = ("OH", "O", "OOH")
STEP_RESPONSE = np.array(((1., 0., 0.), (-1., 1., 0.),
                          (0., -1., 1.), (0., 0., -1.)))
LP_TOLERANCE = 1e-10
DEFAULT_TOLERANCE = 1e-8


def _triple(value, name: str) -> np.ndarray:
    if isinstance(value, Mapping):
        if set(value) != set(SPECIES):
            raise ValueError(f"{name} must contain exactly OH, O, OOH")
        value = [value[sp] for sp in SPECIES]
    try:
        arr = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite OH/O/OOH triple") from exc
    if arr.shape != (3,) or not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be a finite OH/O/OOH triple")
    return arr


def _positive_scalar(value, name: str, minimum: float = 0.) -> float:
    try:
        arr = np.asarray(value, dtype=float)
        if arr.shape != ():
            raise ValueError
        result = float(arr)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{name} must be a finite scalar > {minimum}") from exc
    if not np.isfinite(result) or result <= minimum:
        raise ValueError(f"{name} must be a finite scalar > {minimum}")
    return result


def che_steps(dg, *, total_eV: float = 4.92) -> np.ndarray:
    """Four CHE step free energies from nominal OH/O/OOH adsorption energies."""
    values = _triple(dg, "dg")
    total = _positive_scalar(total_eV, "total_eV")
    result = STEP_RESPONSE @ values
    result[3] += total
    return result


def _solve(objective, matrix, rhs, bounds):
    result = linprog(objective, A_ub=matrix, b_ub=rhs, bounds=bounds,
                     method="highs-ds", options={
                         "primal_feasibility_tolerance": LP_TOLERANCE,
                         "dual_feasibility_tolerance": LP_TOLERANCE,
                     })
    if result.status == 2:
        return None
    if not result.success or not np.all(np.isfinite(result.x)):
        raise RuntimeError(f"CHE region optimization failed: {result.message}")
    return result


def analyze_pair(left_dg, right_dg, half_width_eV, *, total_eV: float = 4.92,
                 tolerance_eV: float = DEFAULT_TOLERANCE) -> dict:
    """Bound right-minus-left eta and enumerate paired potential-limiting steps.

    ``half_width_eV`` is a nonnegative scalar or OH/O/OOH triple. Each shared
    correction lies in [-half_width, +half_width]. Step indices are one-based.
    Closed regions include ties. ``strict`` means both selected steps dominate
    every competitor by more than ``tolerance_eV`` at the returned witness.
    Smaller margins are labelled ``tie_or_unresolved_at_tolerance``; they do not
    count as strict disagreement. Witness maxima list all steps within tolerance.
    Extrema include closed-region boundaries regardless of strict status.

    Fixed region ordering and HiGHS dual simplex make selection deterministic
    in the same numerical environment; the SciPy version is recorded. Different
    solver versions can choose different witnesses on a flat optimum.
    """
    left = _triple(left_dg, "left_dg")
    right = _triple(right_dg, "right_dg")
    total = _positive_scalar(total_eV, "total_eV")
    tol = _positive_scalar(tolerance_eV, "tolerance_eV", 10 * LP_TOLERANCE)
    try:
        raw_width = np.asarray(half_width_eV, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("half_width_eV must be a scalar or OH/O/OOH triple") from exc
    width = _triple(np.repeat(raw_width, 3) if raw_width.shape == () else raw_width,
                    "half_width_eV")
    if np.any(width < 0):
        raise ValueError("half_width_eV must be nonnegative")
    bounds = [(-float(w), float(w)) for w in width]
    left_steps = che_steps(left, total_eV=total)
    right_steps = che_steps(right, total_eV=total)

    def witness(x, pair=None):
        x = np.asarray(x, dtype=float)
        if np.any(np.abs(x) - width > tol):
            raise RuntimeError("LP witness lies outside the correction box")
        sl = left_steps + STEP_RESPONSE @ x
        sr = right_steps + STEP_RESPONSE @ x
        ml, mr = float(max(sl)), float(max(sr))
        if pair is not None and (ml - sl[pair[0]] > tol or mr - sr[pair[1]] > tol):
            raise RuntimeError("LP witness violates its limiting-step region")
        return {
            "correction_eV": dict(zip(SPECIES, map(float, x))),
            "steps_left_eV": sl.tolist(), "steps_right_eV": sr.tolist(),
            "eta_left_V": ml - total / 4, "eta_right_V": mr - total / 4,
            "delta_eta_V": mr - ml,
            "maximizers_left": (np.flatnonzero(ml - sl <= tol) + 1).tolist(),
            "maximizers_right": (np.flatnonzero(mr - sr <= tol) + 1).tolist(),
        }

    regions = []
    for i in range(4):
        for j in range(4):
            # s_k + A_k*x <= s_i + A_i*x for each competitor k.
            rows, rhs = [], []
            for nominal, selected in ((left_steps, i), (right_steps, j)):
                for other in range(4):
                    if other != selected:
                        rows.append(STEP_RESPONSE[other] - STEP_RESPONSE[selected])
                        rhs.append(nominal[selected] - nominal[other])
            matrix, rhs = np.array(rows), np.array(rhs)
            feasible = _solve(np.zeros(3), matrix, rhs, bounds)
            if feasible is None:
                continue
            # Add t to every competitor inequality and maximize t >= 0.
            margin = _solve([0., 0., 0., -1.],
                            np.column_stack((matrix, np.ones(6))), rhs,
                            bounds + [(0., None)])
            if margin is None:
                raise RuntimeError("Feasible region failed its margin problem")
            wm = witness(margin.x[:3], (i, j))
            # Recompute the achieved margin; do not trust an optimizer flag alone.
            achieved = float(min(rhs - matrix @ margin.x[:3]))
            if abs(achieved - margin.x[3]) > tol:
                raise RuntimeError("LP strict-margin certificate failed recomputation")
            objective = STEP_RESPONSE[j] - STEP_RESPONSE[i]
            minimum = _solve(objective, matrix, rhs, bounds)
            maximum = _solve(-objective, matrix, rhs, bounds)
            if minimum is None or maximum is None:
                raise RuntimeError("Feasible region failed its extrema problem")
            wmin, wmax = witness(minimum.x, (i, j)), witness(maximum.x, (i, j))
            strict = achieved > tol
            regions.append({
                "pair": [i + 1, j + 1], "strict": strict,
                "status": "strict" if strict else "tie_or_unresolved_at_tolerance",
                "max_strict_margin_eV": achieved,
                "margin_witness": wm,
                "minimum": wmin, "maximum": wmax,
            })
    if not regions:
        raise RuntimeError("No CHE region covers the nonempty correction box")
    # Iteration order breaks ties deterministically without inventing a physical
    # preference between equally optimal limiting steps.
    minimum = min((r["minimum"] for r in regions), key=lambda w: w["delta_eta_V"])
    maximum = max((r["maximum"] for r in regions), key=lambda w: w["delta_eta_V"])
    return {
        "schema_version": 1,
        "quantity": "eta_right - eta_left under shared OH/O/OOH corrections",
        "left_dg_eV": dict(zip(SPECIES, left.tolist())),
        "right_dg_eV": dict(zip(SPECIES, right.tolist())),
        "half_width_eV": dict(zip(SPECIES, width.tolist())),
        "total_eV": total, "tolerance_eV": tol,
        "solver": {"method": "highs-ds", "scipy_version": scipy.__version__,
                   "feasibility_tolerance": LP_TOLERANCE},
        "nominal": witness(np.zeros(3)),
        "closed_pairs": [r["pair"] for r in regions],
        "strict_pairs": [r["pair"] for r in regions if r["strict"]],
        "strict_disagreement_possible": any(r["strict"] and r["pair"][0] != r["pair"][1]
                                            for r in regions),
        "delta_eta_range_V": [minimum["delta_eta_V"], maximum["delta_eta_V"]],
        "minimum": minimum, "maximum": maximum, "regions": regions,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", nargs=3, type=float, required=True,
                        metavar=("OH", "O", "OOH"))
    parser.add_argument("--right", nargs=3, type=float, required=True,
                        metavar=("OH", "O", "OOH"))
    parser.add_argument("--half-width", nargs="+", type=float, required=True,
                        help="one common half-width or three OH/O/OOH half-widths, eV")
    parser.add_argument("--output", type=Path, help="JSON path; otherwise print to stdout")
    args = parser.parse_args(argv)
    width = args.half_width[0] if len(args.half_width) == 1 else args.half_width
    try:
        result = analyze_pair(args.left, args.right, width)
    except ValueError as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
