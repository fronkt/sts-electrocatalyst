"""SCF trajectories of the 11 round-2 targets beside production's and the ndim16 re-run's attempts at the same
state, read from the committed mirrors (QE's 'estimated scf accuracy' and cell magnetizations per iteration).

Writes trajectories.json next to this file. Offline and read-only.
"""
import json
import math
import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLAN = json.loads((HERE / "ext_plan.json").read_text(encoding="utf-8"))
MIRRORS = {"hea/arm_c_2026-10-07": ROOT / "results/arm_c_2026-10-07/raw_mirror/runs",
           "hea/arm_c_2026-10-07_rerun": ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror/runs"}
CONV_THR = 1e-6
CHECKPOINTS = (1, 8, 20, 50, 100, 126, 150, 200)
WINDOWS = ((1, 50), (51, 100), (101, 150), (151, 200))

ACCURACY = re.compile(r"estimated scf accuracy\s+<\s+([0-9.Ee+-]+)\s+Ry")
TOTAL = re.compile(r"total magnetization\s+=\s+([-0-9.Ee+]+)")
ABSOLUTE = re.compile(r"absolute magnetization\s+=\s+([-0-9.Ee+]+)")
CONVERGED = re.compile(r"convergence has been achieved in\s+(\d+)\s+iterations")


def trajectory(out):
    """Per-iteration accuracy (Ry) and magnetizations (Bohr mag/cell) of one QE output, and how it ended."""
    text = out.read_text(errors="replace")
    accuracy = [float(x) for x in ACCURACY.findall(text)]
    converged = CONVERGED.search(text)
    markers = [out.with_suffix(s) for s in (".KILLED", ".REJECTED") if out.with_suffix(s).exists()]
    if converged:
        end = "converged"
    elif markers:
        end = markers[0].suffix[1:].lower() + ": " + markers[0].read_text().strip()
    else:
        end = "no end marker"
    best = min(accuracy) if accuracy else None
    medians = []
    for lo, hi in WINDOWS:
        part = [math.log10(a) for a in accuracy[lo - 1:hi] if a > 0]
        medians.append(round(statistics.median(part), 2) if part else None)
    totals, absolutes = TOTAL.findall(text), ABSOLUTE.findall(text)
    return {"path": out.relative_to(ROOT).as_posix(), "end": end, "iterations": len(accuracy),
            "accuracy_at": {str(i): accuracy[i - 1] for i in CHECKPOINTS if len(accuracy) >= i},
            "best": best, "best_iteration": accuracy.index(best) + 1 if accuracy else None,
            "log10_median_per_50": medians,
            "total_magnetization": float(totals[-1]) if totals else None,
            "absolute_magnetization": float(absolutes[-1]) if absolutes else None,
            "accuracy": accuracy}


def attempts(site, state):
    """Production's and the re-run's outputs for one state at one site (projection outputs excluded)."""
    found = []
    for root in ("hea/arm_c_2026-10-07", "hea/arm_c_2026-10-07_rerun"):
        for out in sorted((MIRRORS[root] / root / site).glob(state + "__*.out")):
            if not out.name.endswith(".projwfc.out"):
                found.append(trajectory(out))
    return found


def build():
    rows = []
    for row in PLAN["selection"]:
        site = Path(row["site_dir"]).name
        seed = row["seed"]
        seed_out = MIRRORS[seed["root"]] / seed["root"] / site / (seed["job"] + ".out")
        rows.append({"formula": row["formula"], "site": site, "state": row["state"],
                     "production_failure": row["failure"],
                     "seed": {"state": seed["state"], "recipe": seed["recipe"], **{
                         k: v for k, v in trajectory(seed_out).items()
                         if k in ("path", "end", "total_magnetization", "absolute_magnetization")}},
                     "round_2": trajectory(HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".out")),
                     "earlier": attempts(site, row["state"])})
    return {"schema": "s8-arm-c-ext-r2-trajectories-v1", "plan": "results/arm_c_ext_r2_2026-10-08/ext_plan.json",
            "conv_thr_Ry": CONV_THR, "checkpoints": list(CHECKPOINTS), "windows": [list(w) for w in WINDOWS],
            "targets": rows}


def main():
    result = build()
    (HERE / "trajectories.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8", newline="\n")
    for r in result["targets"]:
        t = r["round_2"]
        print(r["formula"], r["site"], r["state"], t["end"], t["iterations"], t["best"], t["log10_median_per_50"], flush=True)


if __name__ == "__main__":
    main()
