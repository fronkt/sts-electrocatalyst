"""Round 4's checks, set before launch (design record, Round 4, "What a result means"), from the committed mirrors.

- energy: the converged total energy against the reference set before launch, the median of round 3's last 50
  total energies (-8913.94359 Ry). More than 1 mRy above it would mark the state as metastable relative to round
  3's trajectory.
- occupations: each slab Hubbard atom's occupations at convergence against every converged state at the site
  (round 3's site_occupations/), against round 4's start (the built occup.txt) and against round 3's stop. The
  distance is the Frobenius norm of the difference over both spins, as in the Round 3 readout.
- spectator: Fe 22 between the site's slab and the configuration its OH and OOH share, and the steps that carry
  it; with the shifts in E(O), and in the adsorbed states against the slab, over which step 1 stays limiting.
Also the run's SCF trajectory: the held iterations and each iteration's energy, accuracy and magnetization.

Writes checks.json next to this file. Offline and read-only.
"""
import importlib.util
import json
import re
import statistics
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R3 = ROOT / "results/arm_c_ext_r3_2026-10-09"
_spec = importlib.util.spec_from_file_location("r3_trajectories", R3 / "trajectories.py")
r3t = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r3t)
ext = r3t.ext

PLAN = json.loads((HERE / "ext_plan.json").read_text(encoding="utf-8"))
READOUT = json.loads((HERE / "readout.json").read_text(encoding="utf-8"))
RY_EV = 13.605693122  # hea_panel_readout.RY_EV
E_REF_SET_RY = -8913.94359  # design record, Round 4, set before launch
FLAG_MRY = 1.0
LAST = 50
NAMED = (22, 20, 18)  # Fe 22, Co 20, Ni 18

ENERGY = re.compile(r"^!?\s+total energy\s+=\s+(-?[0-9.]+)\s+Ry", re.M)
ITERATION = re.compile(r"^\s+iteration #\s*(\d+)", re.M)
RESET = "RESET ns to initial values (iter <= mixing_fixed_ns)"


def saved(mirror, run_dir, job):
    return mirror / "raw_mirror/runs" / run_dir / ("tmp_" + job) / (job + ".save") / "occup.txt"


def round_3(row):
    """Round 3's run of this state: the directory and job round 4 started from."""
    return row["seed"]["root"] + "/" + Path(row["dir"]).name, row["round_3_job"]


def scf(out, held):
    """Each iteration's energy (Ry), accuracy (Ry) and cell magnetizations, and the iterations QE held."""
    text = out.read_text(errors="replace")
    starts = [m.start() for m in ITERATION.finditer(text)] + [len(text)]
    blocks = [text[a:b] for a, b in zip(starts, starts[1:])]
    rows = []
    for k, block in enumerate(blocks, 1):
        rows.append({"iteration": k, "held": RESET in block,
                     "energy_Ry": float(ENERGY.search(block).group(1)),
                     "accuracy_Ry": float(r3t.ACCURACY.search(block).group(1)),
                     "total_magnetization": float(r3t.TOTAL.search(block).group(1)),
                     "absolute_magnetization": float(r3t.ABSOLUTE.search(block).group(1))})
    converged = r3t.CONVERGED.search(text)
    held_at = [r["iteration"] for r in rows if r["held"]]
    if held_at != list(range(1, held + 1)) or text.count(RESET) != held:
        raise ValueError(f"{out}: held iterations {held_at}, expected 1-{held}")
    return {"path": out.relative_to(ROOT).as_posix(), "iterations": len(rows),
            "converged_in": int(converged.group(1)) if converged else None, "held_iterations": held_at,
            "total_magnetization_range": [min(r["total_magnetization"] for r in rows),
                                          max(r["total_magnetization"] for r in rows)],
            "per_iteration": rows}


def energy_check(r4, r3_out):
    energies = [float(x) for x in ENERGY.findall(r3_out.read_text(errors="replace"))]
    reference = statistics.median(energies[-LAST:])
    if round(reference, 5) != E_REF_SET_RY:
        raise ValueError(f"round 3 reference {reference} does not round to the value set before launch")
    final = r4["per_iteration"][-1]["energy_Ry"]
    difference = final - reference
    r3_accuracy = [float(x) for x in r3t.ACCURACY.findall(r3_out.read_text(errors="replace"))]
    return {"round_3_iterations": len(energies), "reference_Ry": reference, "reference_set_Ry": E_REF_SET_RY,
            "round_3_last_50_range_Ry": [min(energies[-LAST:]), max(energies[-LAST:])],
            "round_3_last_50_median_accuracy_Ry": statistics.median(r3_accuracy[-LAST:]),
            "converged_Ry": final, "difference_mRy": difference * 1e3, "difference_eV": difference * RY_EV,
            "first_iteration_below_reference": next(r["iteration"] for r in r4["per_iteration"]
                                                    if r["energy_Ry"] < reference),
            "flag_above_mRy": FLAG_MRY, "flag": difference * 1e3 > FLAG_MRY}


def distance(a, b):
    return round(float(np.linalg.norm(a - b)), 4)


def moment(block):
    up, down = np.trace(block, axis1=1, axis2=2)
    return round(float(up - down), 3)


def occupation_check(row, site):
    """Each slab Hubbard atom at convergence against the site's converged states, the start and round 3's stop."""
    files = [f for f in json.loads((R3 / "site_occupations.json").read_text(encoding="utf-8"))["files"]
             if f["site"] == site]
    states = {f["state"]: r3t.occupations(R3 / f["local"]) for f in files}
    names = sorted(states)
    end = r3t.occupations(saved(HERE, row["dir"], row["job"]))
    start = r3t.occupations(ROOT / row["bundle"] / "occup.txt")
    r3_stop = r3t.occupations(saved(R3, *round_3(row)))
    cell, atoms = ext.geometry((HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".run.in")).read_text())
    o1 = atoms[ext.SLAB_ATOMS][1]
    rows = []
    for i in range(ext.SLAB_ATOMS):
        if not end[i].any() and not any(states[s][i].any() for s in names):
            continue
        to_state = {s: distance(end[i], states[s][i]) for s in names}
        pairs = {a + "-" + b: distance(states[a][i], states[b][i]) for k, a in enumerate(names) for b in names[k + 1:]}
        nearest = min(names, key=lambda s: (to_state[s], s))
        r3_to_state = {s: distance(r3_stop[i], states[s][i]) for s in names}
        rows.append({"atom": i + 1, "species": atoms[i][0],
                     "distance_to_O1": round(ext.in_plane_distance(cell, o1, atoms[i][1]), 3),
                     "spread_converged": max(pairs.values()), "end_to_nearest": to_state[nearest],
                     "nearest_state": nearest, "end_to_state": to_state, "between_converged": pairs,
                     "end_to_start": distance(end[i], start[i]), "end_to_round_3_stop": distance(end[i], r3_stop[i]),
                     "round_3_stop_to_nearest": min(r3_to_state.values()), "round_3_stop_to_state": r3_to_state,
                     "moment": {"end": moment(end[i]), "start": moment(start[i]), "round_3_stop": moment(r3_stop[i]),
                                **{s: moment(states[s][i]) for s in names}}})
    rows.sort(key=lambda r: (-r["end_to_nearest"], r["atom"]))
    outside = [r["atom"] for r in rows if r["end_to_nearest"] > r["spread_converged"]]
    r3_outside = [r["atom"] for r in rows if r["round_3_stop_to_nearest"] > r["spread_converged"]]
    return {"converged_states": names, "hubbard_atoms": len(rows),
            "end_outside_spread": sorted(outside), "round_3_stop_outside_spread": sorted(r3_outside),
            "median_end_to_nearest": statistics.median(r["end_to_nearest"] for r in rows),
            "median_round_3_stop_to_nearest": statistics.median(r["round_3_stop_to_nearest"] for r in rows),
            "median_spread_converged": statistics.median(r["spread_converged"] for r in rows),
            "named": [next(r for r in rows if r["atom"] == a) for a in NAMED], "atoms": rows}


def spectator(site_row, occupations):
    """Fe 22's slab-to-adsorbate change, and the shifts over which step 1 stays limiting."""
    fe22 = next(r for r in occupations["atoms"] if r["atom"] == 22)
    steps = site_row["steps_eV"]
    # E(O) + d moves dG2 by +d and dG3 by -d: step 1 stays limiting for d in [dG3 - dG1, dG1 - dG2].
    # G(OH), G(O) and G(OOH) all + s against the slab move dG1 by +s and dG4 by -s: eta follows s one for one
    # down to s = dG3 - dG1, where the steps s leaves alone take over (eta_floor_V).
    return {"fe22_between_converged": fe22["between_converged"], "fe22_end_to_state": fe22["end_to_state"],
            "fe22_distance_to_O1": fe22["distance_to_O1"],
            "adsorbed_states_share_fe22": fe22["nearest_state"] != "slab",
            "steps_eV": steps, "potential_limiting_step": site_row["potential_limiting_step"],
            "eta_V": site_row["eta_dft_V"],
            "E_O_shift_window_eV": [steps[2] - steps[0], steps[0] - steps[1]],
            "adsorbed_shift_floor_eV": steps[2] - steps[0],
            "eta_floor_V": max(steps[1], steps[2]) - 1.23}


def build():
    row = PLAN["selection"][0]
    site = Path(row["dir"]).name
    run = scf(HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".out"), row["mixing"]["mixing_fixed_ns"])
    r3_dir, r3_job = round_3(row)
    energy = energy_check(run, R3 / "raw_mirror/runs" / r3_dir / (r3_job + ".out"))
    occupations = occupation_check(row, site)
    site_row = next(s for s in READOUT["sites"] if Path(s["dir"]).name == site)
    return {"schema": "s8-arm-c-ext-r4-checks-v1", "plan": "results/arm_c_ext_r4_2026-10-10/ext_plan.json",
            "readout": "results/arm_c_ext_r4_2026-10-10/readout.json", "site": site, "state": row["state"],
            "scf": run, "energy": energy, "occupations": occupations,
            "spectator": spectator(site_row, occupations),
            "magnetization_vs_site": site_row["states"][row["state"]]["magnetization_vs_site"]}


def main():
    result = build()
    (HERE / "checks.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8", newline="\n")
    e, o = result["energy"], result["occupations"]
    print("energy", round(e["difference_mRy"], 2), "mRy flag", e["flag"], "| outside", o["end_outside_spread"],
          "| r3 outside", o["round_3_stop_outside_spread"], flush=True)


if __name__ == "__main__":
    main()
