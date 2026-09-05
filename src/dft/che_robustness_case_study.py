"""Reproduce the docs/84 continuous CHE counterexample without new DFT.

Reads the immutable banked adsorption free energies, stores source hashes,
compares the old 27-point sampling to continuous LP results, and plots an
analytic one-dimensional slice. This is supporting sensitivity analysis;
it neither re-scores a registered prediction nor changes a banked readout.

Run from any directory:
    python src/dft/che_robustness_case_study.py
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from che_box_robustness import SPECIES, STEP_RESPONSE, analyze_pair, che_steps

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/figs/pproj_cell_readout.json"


def build_case_study(source: Path = SOURCE) -> dict:
    raw = source.read_bytes()
    banked = json.loads(raw)
    if (banked["cell"], banked["metal"], banked["U"]) != ("2x1v", "Cr", 7.15):
        raise ValueError("This case study requires banked Cr 2x1v at U=7.15 eV")
    left = banked["legs"]["atomic"]["dG"]
    right = banked["legs"]["ortho"]["dG"]
    sl, sr = che_steps(left), che_steps(right)
    if not np.isclose(max(sr) - max(sl), banked["d_eta_V"], atol=1e-10, rtol=0):
        raise ValueError("Banked nominal difference does not reproduce")
    x = np.array([-.0525, .0525, 0.])
    wl, wr = sl + STEP_RESPONSE @ x, sr + STEP_RESPONSE @ x
    counterexample = {
        "correction_eV": dict(zip(SPECIES, x.tolist())),
        "steps_atomic_eV": wl.tolist(), "steps_ortho_eV": wr.tolist(),
        "eta_atomic_V": float(max(wl) - 1.23),
        "eta_ortho_V": float(max(wr) - 1.23),
        "pair": [int(np.argmax(wl)) + 1, int(np.argmax(wr)) + 1],
        "delta_eta_V": float(max(wr) - max(wl)),
    }
    cases = []
    for h in (.05, .0525, .10, .15, .30):
        pairs = [
            [int(np.argmax(sl + STEP_RESPONSE @ v)) + 1,
             int(np.argmax(sr + STEP_RESPONSE @ v)) + 1]
            for v in itertools.product((-h, 0., h), repeat=3)
        ]
        cases.append({
            "half_width_eV": h,
            "grid_points": 27,
            "grid_pairs_first_max_convention": [list(p) for p in sorted(set(map(tuple, pairs)))],
            "grid_disagreements": sum(p[0] != p[1] for p in pairs),
            "continuous": analyze_pair(left, right, h),
        })
    code_paths = [Path(__file__), Path(__file__).with_name("che_box_robustness.py")]
    return {
        "status": "exploratory sensitivity analysis; no registered verdict changed",
        "source": source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else str(source),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "implementation_sha256": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in code_paths
        },
        "system": {"metal": "Cr", "cell": "2x1v", "U_eV": 7.15,
                   "geometry": "fixed atomic-relaxed geometries",
                   "left": "atomic projector", "right": "ortho-atomic projector"},
        "nominal_banked_delta_eta_V": banked["d_eta_V"],
        "one_by_one_companion": banked["one_by_one"],
        "scope": "Shared additive OH/O/OOH corrections only. Not a probability, "
                 "kinetic RDS, independent surface errors, or candidate activity claim.",
        "counterexample": counterexample,
        "slice_t_switch_eV": {"atomic": float((sl[0] - sl[1]) / 3),
                              "ortho": float((sr[0] - sr[1]) / 3)},
        "cases": cases,
    }


def plot_case_study(data: dict, output_dir: Path) -> None:
    # The plotted slice uses the banked steps embedded in the nominal LP witness.
    nominal = data["cases"][0]["continuous"]["nominal"]
    sl = np.array(nominal["steps_left_eV"])
    sr = np.array(nominal["steps_right_eV"])
    ta, to = data["slice_t_switch_eV"]["atomic"], data["slice_t_switch_eV"]["ortho"]
    t = np.sort(np.unique(np.r_[np.linspace(.045, .060, 700), ta, to, .0525]))
    corrections = np.column_stack((-t, t, np.zeros_like(t)))
    left_steps = sl + corrections @ STEP_RESPONSE.T
    right_steps = sr + corrections @ STEP_RESPONSE.T
    delta = right_steps.max(axis=1) - left_steps.max(axis=1)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.hashsalt": "che-box-case-study-2026-09-05"})
    fig, axes = plt.subplots(2, 1, figsize=(8.4, 6.4), sharex=True, layout="constrained")
    for ax in axes:
        ax.axvspan(to * 1000, ta * 1000, color="#e6a34b", alpha=.25)
        ax.axvline(50, color="#666666", linestyle=":", linewidth=1.3)
        ax.grid(axis="y", alpha=.15)
    axes[0].plot(t * 1000, (left_steps[:, 0] - left_steps[:, 1]) * 1000,
                 color="#2166ac", label="Atomic projector")
    axes[0].plot(t * 1000, (right_steps[:, 0] - right_steps[:, 1]) * 1000,
                 color="#b2182b", linestyle="--", label="Orthogonalized projector")
    axes[0].axhline(0, color="#333333", linewidth=.8)
    axes[0].set_ylabel("Step 1 minus step 2 (meV)")
    axes[0].legend(loc="upper right", frameon=False)
    axes[0].set_title("A narrow region of step disagreement missed by the 27-point grid",
                      loc="left", fontsize=12, pad=14)
    axes[0].text(.015, .06, "Positive: step 1 limits. Negative: step 2 limits.",
                 transform=axes[0].transAxes, fontsize=9)
    axes[1].plot(t * 1000, delta * 1000, color="#333333", linewidth=2)
    ce = data["counterexample"]
    axes[1].scatter([52.5], [ce["delta_eta_V"] * 1000], s=35, color="#b2182b", zorder=5)
    axes[1].annotate("Counterexample: pair (1, 2)", xy=(52.5, ce["delta_eta_V"] * 1000),
                     xytext=(54.5, 174.4), fontsize=9,
                     arrowprops={"arrowstyle": "-", "color": "#777777"})
    axes[1].set_ylabel("Paired overpotential difference (mV)")
    axes[1].set_xlabel("t (meV), with shared corrections (OH, O, OOH) = (-t, +t, 0)")
    axes[1].set_ylim(171.5, 180)
    axes[1].set_xlim(45, 60)
    fig.suptitle("Cr model phase | 2x1v | U = 7.15 eV | fixed geometry\n"
                 "Nominal difference: 172.52 mV; 1x1 companion: 486.86 mV",
                 fontsize=10)
    svg_path = output_dir / "continuous_che_counterexample.svg"
    fig.savefig(svg_path, metadata={"Date": None})
    svg_path.write_text("\n".join(line.rstrip() for line in
                                 svg_path.read_text(encoding="utf-8").splitlines())
                        + "\n", encoding="utf-8")
    fig.savefig(output_dir / "continuous_che_counterexample.png", dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/che_box_case_study_2026-09-05")
    args = parser.parse_args()
    data = build_case_study()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / "audit.json"
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    plot_case_study(data, args.output_dir)
    for case in data["cases"]:
        continuous = case["continuous"]
        print(f"h={case['half_width_eV']:.4f} eV: grid disagreements="
              f"{case['grid_disagreements']}/27; continuous strict pairs="
              f"{continuous['strict_pairs']}; delta_eta={continuous['delta_eta_range_V']}")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
