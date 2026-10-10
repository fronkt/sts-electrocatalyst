"""SCF trajectories of round 3's two targets beside round 2's run of the same state from the same start; the
run-to-run control (round 2's canary and main array ran the Cu8 s16/2 slab from identical inputs); and each
round-3 run's last Hubbard occupations, as QE wrote them when it stopped itself, against its start (the seed
state's converged occupations, rebuilt for the target's atoms) and against every converged state at its site
(site_occupations.py). Read from the committed mirrors, seed files and site occupations.

Writes trajectories.json next to this file. Offline and read-only.
"""
import json
import re
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import arm_c_ext_build as ext  # noqa: E402

PLAN = json.loads((HERE / "ext_plan.json").read_text(encoding="utf-8"))
R2_RUNS = ROOT / "results/arm_c_ext_r2_2026-10-08/raw_mirror/runs"
R2_CANARY = ROOT / "results/arm_c_ext_r2_2026-10-08/canary_mirror/hea/arm_c_ext_r2_2026-10-08/canary"
SEED_RUNS = {"hea/arm_c_2026-10-07": ROOT / "results/arm_c_2026-10-07/raw_mirror/runs",
             "hea/arm_c_2026-10-07_rerun": ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror/runs"}
CONV_THR = 1e-6
CHECKPOINTS = (1, 8, 50, 100, 126, 150, 200, 250, 300)
WINDOWS = ((1, 50), (51, 100), (101, 150), (151, 200), (201, 250), (251, 300))
FIRST = 8

ACCURACY = re.compile(r"estimated scf accuracy\s+<\s+([0-9.Ee+-]+)\s+Ry")
TOTAL = re.compile(r"total magnetization\s+=\s+([-0-9.Ee+]+)")
ABSOLUTE = re.compile(r"absolute magnetization\s+=\s+([-0-9.Ee+]+)")
CONVERGED = re.compile(r"convergence has been achieved in\s+(\d+)\s+iterations")
QE_STOP = re.compile(r"convergence NOT achieved after\s+\d+\s+iterations: stopping")


def trajectory(out):
    """Per-iteration accuracy (Ry) and cell magnetizations (Bohr mag/cell) of one QE output, and how it ended."""
    text = out.read_text(errors="replace")
    accuracy = [float(x) for x in ACCURACY.findall(text)]
    totals = [float(x) for x in TOTAL.findall(text)]
    absolutes = [float(x) for x in ABSOLUTE.findall(text)]
    markers = [out.with_suffix(s) for s in (".KILLED", ".REJECTED") if out.with_suffix(s).exists()]
    if CONVERGED.search(text):
        end = "converged"
    elif markers:
        end = markers[0].suffix[1:].lower() + ": " + markers[0].read_text().strip()
    else:
        end = "no end marker"
    stop = QE_STOP.search(text)
    best = min(accuracy)
    late = totals[100:]
    return {"path": out.relative_to(ROOT).as_posix(), "end": end, "qe_stop": stop.group(0) if stop else None,
            "iterations": len(accuracy),
            "accuracy_at": {str(i): accuracy[i - 1] for i in CHECKPOINTS if len(accuracy) >= i},
            "best": best, "best_iteration": accuracy.index(best) + 1,
            "below_1e-5": [i + 1 for i, a in enumerate(accuracy) if a < 1e-5],
            "median_per_50": [statistics.median(accuracy[lo - 1:hi]) if len(accuracy) >= lo else None
                              for lo, hi in WINDOWS],
            "total_magnetization": totals[-1], "absolute_magnetization": absolutes[-1],
            "total_magnetization_range_from_101": [min(late), max(late)] if late else None,
            "accuracy": accuracy}


def first_iterations(a, b):
    """Relative difference of two runs' accuracies over their first iterations."""
    return [abs(x - y) / y for x, y in zip(a["accuracy"][:FIRST], b["accuracy"][:FIRST])]


def occupations(path):
    """ns(5, 5, nspin=2, nat) from an occup.txt, as [atom][spin] 5x5 arrays."""
    values = ext.numbers(path.read_text(encoding="ascii"))
    if len(values) % ext.NS_BLOCK:
        raise ValueError(f"{path}: {len(values)} values is not a whole number of atom blocks")
    return np.array(values).reshape(-1, 2, 5, 5).transpose(0, 1, 3, 2)  # Fortran order: m1 fastest


def occupation_change(row, site):
    """Each Hubbard atom's last occupations against its start, with its distance from the adsorbate O."""
    start = occupations(HERE / "seeds" / site / row["state"] / "occup.txt")
    end = occupations(HERE / "raw_mirror/runs" / row["dir"] / ("tmp_" + row["job"]) / (row["job"] + ".save") / "occup.txt")
    cell, atoms = ext.geometry((HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".run.in")).read_text())
    if not len(start) == len(end) == len(atoms) == ext.nat_of(row["state"]):
        raise ValueError(f"{site} {row['state']}: atom counts differ")
    if ext.ROLES[row["state"]][:1] == ("O1",):
        o1, source = atoms[ext.SLAB_ATOMS][1], "this state's O1 (atom 73)"
    else:  # the slab target: the O sat on the seed state's deck
        seed = row["seed"]
        deck = SEED_RUNS[seed["root"]] / seed["root"] / site / (seed["job"] + ".run.in")
        o1, source = ext.geometry(deck.read_text())[1][ext.SLAB_ATOMS][1], "the seed state's O1 (atom 73)"
    rows = []
    for i, (species, position) in enumerate(atoms):
        s, e = start[i], end[i]
        if not s.any() and not e.any():
            continue
        trace_s, trace_e = np.trace(s, axis1=1, axis2=2), np.trace(e, axis1=1, axis2=2)
        shift = max(float(np.max(np.abs(np.linalg.eigvalsh(e[k]) - np.linalg.eigvalsh(s[k])))) for k in (0, 1))
        rows.append({"atom": i + 1, "species": species, "z": round(position[2], 3),
                     "distance_to_O1": round(ext.in_plane_distance(cell, o1, position), 3),
                     "frobenius_up": round(float(np.linalg.norm(e[0] - s[0])), 4),
                     "frobenius_down": round(float(np.linalg.norm(e[1] - s[1])), 4),
                     "max_eigenvalue_shift": round(shift, 4),
                     "moment_start": round(float(trace_s[0] - trace_s[1]), 3),
                     "moment_end": round(float(trace_e[0] - trace_e[1]), 3)})
    rows.sort(key=lambda r: (-(r["frobenius_up"] ** 2 + r["frobenius_down"] ** 2), r["atom"]))
    return {"distance_from": source, "hubbard_atoms": len(rows), "atoms": rows}


def site_comparison(row, site):
    """Each slab Hubbard atom's last occupations against every converged state at the site (site_occupations.py).

    distance: Frobenius norm of the occupation difference over both spins. spread_converged: the largest distance
    between two converged states; stop_to_nearest: the stalled run's distance to the nearest converged state."""
    files = [f for f in json.loads((HERE / "site_occupations.json").read_text(encoding="utf-8"))["files"]
             if f["site"] == site]
    states = {f["state"]: occupations(HERE / f["local"])[:ext.SLAB_ATOMS] for f in sorted(files, key=lambda f: f["state"])}
    end = occupations(HERE / "raw_mirror/runs" / row["dir"] / ("tmp_" + row["job"]) / (row["job"] + ".save") / "occup.txt")
    _, atoms = ext.geometry((HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".run.in")).read_text())
    names = sorted(states)
    rows = []
    for i in range(ext.SLAB_ATOMS):
        if not end[i].any() and not any(states[s][i].any() for s in names):
            continue
        to_state = {s: round(float(np.linalg.norm(end[i] - states[s][i])), 4) for s in names}
        pairs = {a + "-" + b: round(float(np.linalg.norm(states[a][i] - states[b][i])), 4)
                 for k, a in enumerate(names) for b in names[k + 1:]}
        nearest = min(names, key=lambda s: (to_state[s], s))
        rows.append({"atom": i + 1, "species": atoms[i][0], "spread_converged": max(pairs.values()),
                     "stop_to_nearest": to_state[nearest], "nearest_state": nearest, "stop_to_state": to_state,
                     "between_converged": pairs})
    rows.sort(key=lambda r: (-r["stop_to_nearest"], r["atom"]))
    return {"converged_states": names, "atoms": rows}


def build():
    targets = []
    for row in PLAN["selection"]:
        site = Path(row["dir"]).name
        r3 = trajectory(HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".out"))
        r2 = trajectory(R2_RUNS / "hea/arm_c_ext_r2_2026-10-08" / site / (row["round_2_job"] + ".out"))
        targets.append({"formula": row["formula"], "site": site, "state": row["state"], "mixing": row["mixing"],
                        "round_3": r3, "round_2": r2, "round_3_vs_round_2_first": first_iterations(r3, r2),
                        "occupations": occupation_change(row, site), "site_comparison": site_comparison(row, site)})
    site, job = "Cu8Cr23Mn35Co34__s16_site2", "slab__atomic_moved"
    canary = trajectory(R2_CANARY / site / (job + ".out"))
    main = trajectory(R2_RUNS / "hea/arm_c_ext_r2_2026-10-08" / site / (job + ".out"))
    control = {"state": site + " slab", "note": "round 2's canary and main array, identical inputs",
               "canary": canary["path"], "main": main["path"], "first": first_iterations(canary, main)}
    return {"schema": "s8-arm-c-ext-r3-trajectories-v1", "plan": "results/arm_c_ext_r3_2026-10-09/ext_plan.json",
            "conv_thr_Ry": CONV_THR, "checkpoints": list(CHECKPOINTS), "windows": [list(w) for w in WINDOWS],
            "targets": targets, "run_to_run_control": control}


def main():
    result = build()
    (HERE / "trajectories.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8", newline="\n")
    for t in result["targets"]:
        r3, r2 = t["round_3"], t["round_2"]
        print(t["formula"], t["site"], t["state"], r3["end"], r3["iterations"], r3["best"], r3["best_iteration"],
              "| r2", r2["best"], r2["best_iteration"], flush=True)


if __name__ == "__main__":
    main()
