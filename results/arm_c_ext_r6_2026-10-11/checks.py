"""Round 6's checks, set before launch (design record, Round 6, "What a result means"), from the committed mirrors.

For each of the four second starts (the slab and the OH at Ni31 s1/0 and Cu26 s1/0, each with Cr 19 from the other
state):
- energy: the converged run against its first run (arm C, 2026-10-07), each from its own output, with the Hubbard
  energy of each. More than 1 meV lower is the readout's rule for replacing the first run.
- moments: the cell's total moment, and the moments QE integrates on every atom's sphere, against the first run's.
- Cr 19: its occupations at convergence against every converged state at the site. It is in the slab's or the OH's
  configuration if it lies within half the distance between the two, 0.21 at Ni31 s1/0 and 0.14 at Cu26 s1/0;
  otherwise in another configuration. The slab's and the OH's occupations are their saved occup.txt files
  (start_sources.json), the O's and the OOH's QE's last printed occupations (3 decimals). The distance is the
  Frobenius norm of the difference over both spins, as in the Round 3 to Round 5 readouts.
- every Hubbard atom's change from the run's own state's occupations and from its start.
- the value: each site's and alloy's against round 5's readout.
Also each run's SCF trajectory (the held iterations, any re-diagonalized with a lowered threshold, and each
iteration's energy, accuracy and magnetization) and the round's CPU SU from sacct.

Writes checks.json next to this file. Offline and read-only.
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R5 = ROOT / "results/arm_c_ext_r5_2026-10-10"
ARM_C = ROOT / "results/arm_c_2026-10-07"
_spec = importlib.util.spec_from_file_location("r5_checks", R5 / "checks.py")
r5c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r5c)  # round 5's final(); round 4's scf(), distance(), moment() and saved(); src/dft on sys.path
r4c, ext = r5c.r4c, r5c.ext
import arm_c_ext_r6_build as r6  # noqa: E402
import arm_c_readout as readout  # noqa: E402

PLAN = json.loads((HERE / "ext_plan.json").read_text(encoding="utf-8"))
READOUT = json.loads((HERE / "readout.json").read_text(encoding="utf-8"))
BEFORE = json.loads((R5 / "readout.json").read_text(encoding="utf-8"))
COLLECTION = json.loads((HERE / "terminal_collection.json").read_text(encoding="utf-8"))
RY_EV = r5c.RY_EV
HALF_WAY = {"Ni31Cr29Cu5Mn35__s1_site0": 0.21, "Cu26Ni9Cr31Co33__s1_site0": 0.14}  # design record, Round 6
ATOM = 19
STATES = ("slab", "O", "OH", "OOH")
TOP = 5
LOWERED = "Diagonalizing with lowered threshold"


def scf(out, held):
    """Round 4's scf(), except that a held iteration QE re-diagonalizes with a lowered threshold resets ns once more.

    QE then mixes again within that iteration and prints the reset a second time (the Cu26 s1/0 OH, iteration 1).
    """
    text = out.read_text(errors="replace")
    starts = [m.start() for m in r4c.ITERATION.finditer(text)] + [len(text)]
    blocks = [text[a:b] for a, b in zip(starts, starts[1:])]
    rows = []
    for k, block in enumerate(blocks, 1):
        resets, lowered = block.count(r4c.RESET), block.count(LOWERED)
        if resets != ((1 + lowered) if k <= held else 0):
            raise ValueError(f"{out}: iteration {k} printed {resets} resets with {lowered} re-diagonalizations")
        rows.append({"iteration": k, "held": resets > 0, "rediagonalized": lowered,
                     "energy_Ry": float(r4c.ENERGY.search(block).group(1)),
                     "accuracy_Ry": float(r4c.r3t.ACCURACY.search(block).group(1)),
                     "total_magnetization": float(r4c.r3t.TOTAL.search(block).group(1)),
                     "absolute_magnetization": float(r4c.r3t.ABSOLUTE.search(block).group(1))})
    if r4c.RESET in text[:starts[0]]:
        raise ValueError(f"{out}: a reset before the first iteration")
    converged = r4c.r3t.CONVERGED.search(text)
    return {"path": out.relative_to(ROOT).as_posix(), "iterations": len(rows),
            "converged_in": int(converged.group(1)) if converged else None,
            "held_iterations": [r["iteration"] for r in rows if r["held"]],
            "rediagonalized_iterations": [r["iteration"] for r in rows if r["rediagonalized"]],
            "total_magnetization_range": [min(r["total_magnetization"] for r in rows),
                                          max(r["total_magnetization"] for r in rows)],
            "per_iteration": rows}


def site_states(site_row, name):
    """Every converged state's occupations at the site, the first 72 atoms: the saved slab and OH, the printed O and OOH."""
    states, sources = {}, {}
    for state in ("slab", "OH"):
        job, layer = r6.accepted(site_row, state)
        path = HERE / "sources" / name / (job + ".occup.txt")
        states[state] = r6.matrices(path.read_bytes())[:ext.SLAB_ATOMS]
        sources[state] = {"job": job, "layer": layer, "path": path.relative_to(ROOT).as_posix(), "from": "occup.txt"}
    hubbard = {a + 1 for a in range(ext.SLAB_ATOMS) if states["slab"][a].any()}
    for state in ("O", "OOH"):
        job, layer = r6.accepted(site_row, state)
        if layer not in r6.MIRRORS:
            raise ValueError(f"{name} {state}: accepted run {job} is not arm C's")
        out = ROOT / (r6.MIRRORS[layer] + (site_row["dir"] if layer == "production" else name) + f"/{job}.out")
        printed = r6.printed_final(out.read_text(errors="replace"))
        if {a for a in printed if a <= ext.SLAB_ATOMS} != hubbard:
            raise ValueError(f"{name} {state}: printed atoms are not the slab's Hubbard atoms")
        block = states["slab"] * 0
        for a in hubbard:
            block[a - 1] = printed[a]
        states[state] = block
        sources[state] = {"job": job, "layer": layer, "path": out.relative_to(ROOT).as_posix(), "from": "printed"}
    return states, sources


def occupation_check(row, states):
    """Each Hubbard atom at convergence against the run's own state, its start and every converged state."""
    end = r6.matrices(r4c.saved(HERE, row["dir"], row["job"]).read_bytes())[:ext.SLAB_ATOMS]
    start = r6.matrices((ROOT / row["bundle"] / "occup.txt").read_bytes())[:ext.SLAB_ATOMS]
    cell, atoms = ext.geometry((ROOT / "runs" / row["site_dir"] / "OH__atomic.in").read_text(encoding="utf-8"))
    o1 = atoms[ext.SLAB_ATOMS][1]
    rows = []
    for i in range(ext.SLAB_ATOMS):
        if not end[i].any() and not states["slab"][i].any():
            continue
        to_state = {s: r4c.distance(end[i], states[s][i]) for s in STATES}
        rows.append({"atom": i + 1, "species": atoms[i][0],
                     "distance_to_O1_A": round(ext.in_plane_distance(cell, o1, atoms[i][1]), 3),
                     "end_to_own": to_state[row["state"]], "end_to_start": r4c.distance(end[i], start[i]),
                     "nearest_state": min(STATES, key=lambda s: (to_state[s], s)), "end_to_state": to_state,
                     "moment": {"end": r4c.moment(end[i]), "start": r4c.moment(start[i]),
                                **{s: r4c.moment(states[s][i]) for s in STATES}}})
    rows.sort(key=lambda r: (-r["end_to_own"], r["atom"]))
    return {"hubbard_atoms": len(rows), "largest_change_from_own": rows[0]["end_to_own"],
            "atoms_over_0.01": [r["atom"] for r in rows if r["end_to_own"] > 0.01], "atoms": rows}


def cr19_check(row, states, occupations):
    name = Path(row["dir"]).name
    cr = next(r for r in occupations["atoms"] if r["atom"] == ATOM)
    to, half = cr["end_to_state"], HALF_WAY[name]
    configuration = "slab" if to["slab"] <= half else "OH" if to["OH"] <= half else "other"
    started_in = row["occupations"]["from"]["state"]
    pairs = {a + "-" + b: r4c.distance(states[a][ATOM - 1], states[b][ATOM - 1])
             for k, a in enumerate(STATES) for b in STATES[k + 1:]}
    return {"started_in": started_in, "end_to_state": to, "end_to_start": cr["end_to_start"],
            "slab_to_OH": pairs["slab-OH"], "half_way": half, "configuration": configuration,
            "returned": configuration == row["state"], "between_converged": pairs, "moment": cr["moment"]}


def energy_check(row, attempt, run):
    first = row["first"]
    if first["recipe"] != "production":
        raise ValueError(f"{row['job']}: first run is not arm C's production run")
    production, hub_first, _ = r5c.final(ARM_C / "raw_mirror/runs" / row["site_dir"] / (first["job"] + ".out"))
    converged, hub_new, _ = r5c.final(HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".out"))
    if abs(production * RY_EV - first["E_eV"]) > 1e-6:
        raise ValueError(f"first run {production} Ry is not the plan's")
    gap = (converged - production) * RY_EV * 1e3
    if abs(gap - attempt["energy_vs_first_meV"]) > 1e-6:
        raise ValueError(f"energy gap {gap} meV is not the readout's {attempt['energy_vs_first_meV']}")
    hubbard = (hub_new - hub_first) * RY_EV * 1e3
    return {"first_Ry": production, "converged_Ry": converged, "difference_mRy": (converged - production) * 1e3,
            "difference_meV": gap, "rule_meV": readout.SECOND_START_MEV,
            "outcome": "lower" if gap < -readout.SECOND_START_MEV else
                       "within" if gap <= readout.SECOND_START_MEV else "higher",
            "first_iteration_below_first": next((r["iteration"] for r in run["per_iteration"]
                                                 if r["energy_Ry"] < production), None),
            "hubbard_energy_Ry": {"first": hub_first, "converged": hub_new},
            "hubbard_difference_meV": hubbard, "rest_difference_meV": gap - hubbard}


def sphere_check(row, attempt):
    """QE's sphere-integrated moments (uB) of every atom against the first run's."""
    _, _, new = r5c.final(HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".out"))
    _, _, old = r5c.final(ARM_C / "raw_mirror/runs" / row["site_dir"] / (row["first"]["job"] + ".out"))
    if sorted(new) != sorted(old):
        raise ValueError(f"{row['job']}: atoms differ from the first run's")
    rows = [{"atom": a, "end": new[a][1], "first": old[a][1], "change": round(new[a][1] - old[a][1], 4),
             "charge_change": round(new[a][0] - old[a][0], 4)} for a in sorted(new)]
    rows.sort(key=lambda r: (-abs(r["change"]), r["atom"]))
    return {"total_uB": attempt["total_magnetization"], "first_total_uB": row["first"]["total_magnetization"],
            "total_change_uB": attempt["magnetization_vs_first_uB"], "atom_19": next(r for r in rows if r["atom"] == ATOM),
            "largest_change_uB": abs(rows[0]["change"]), "largest": rows[:TOP]}


def values():
    """Each value site's and alloy's value against round 5's readout."""
    sites = {}
    for row in PLAN["selection"]:
        now = next(s for s in READOUT["sites"] if s["dir"] == row["site_dir"])
        then = next(s for s in BEFORE["sites"] if s["dir"] == row["site_dir"])
        attempts = [a for a in now["extension_attempts"] if a.get("round") == 6]
        sites[Path(row["dir"]).name] = {
            "eta_V": now["eta_dft_V"], "eta_round_5_V": then["eta_dft_V"], "steps_eV": now["steps_eV"],
            "potential_limiting_step": now["potential_limiting_step"],
            "replaced": sorted(a["state"] for a in attempts if a["replaces"]),
            "with_first_V": now.get("eta_dft_V_with_first"), "states": {s: now["states"][s]["job"] for s in STATES}}
    alloys = {a: {"C_V": READOUT["alloys"][a]["C_V"], "C_V_round_5": BEFORE["alloys"][a]["C_V"]}
              for a in READOUT["exploratory_predictions"]["order_all_with_values"]}
    return {"sites": sites, "alloys": alloys,
            "order": READOUT["exploratory_predictions"]["order_all_with_values"],
            "order_round_5": BEFORE["exploratory_predictions"]["order_all_with_values"],
            "unchanged": all(s["eta_V"] == s["eta_round_5_V"] for s in sites.values())
                         and all(a["C_V"] == a["C_V_round_5"] for a in alloys.values())}


def cost():
    """CPU SU of round 6: the sacct CPU time of its four tasks (terminal_collection.json)."""
    rows = [line.split("|") for line in COLLECTION["sacct"].strip().splitlines()]
    tasks = {r[0]: int(r[7]) / 3600 for r in rows if "." not in r[0]}
    if len(tasks) != len(PLAN["selection"]):
        raise ValueError(f"expected {len(PLAN['selection'])} accounted tasks, found {len(tasks)}")
    return {"tasks_su": tasks, "total_su": sum(tasks.values())}


def build():
    runs = []
    for row in PLAN["selection"]:
        name = Path(row["dir"]).name
        site_row = next(s for s in READOUT["sites"] if s["dir"] == row["site_dir"])
        attempt, = [a for a in site_row["extension_attempts"] if a.get("round") == 6 and a["job"] == row["job"]]
        states, sources = site_states(site_row, name)
        run = scf(HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".out"), row["mixing"]["mixing_fixed_ns"])
        occupations = occupation_check(row, states)
        runs.append({"site": name, "state": row["state"], "job": row["job"],
                     "readout": {k: attempt[k] for k in ("accepted", "failure", "lower", "replaces", "iterations",
                                                         "energy_vs_first_meV", "magnetization_vs_first_uB")},
                     "energy": energy_check(row, attempt, run), "cr19": cr19_check(row, states, occupations),
                     "moments": sphere_check(row, attempt), "site_states": sources, "occupations": occupations,
                     "scf": run})
    return {"schema": "s8-arm-c-ext-r6-checks-v1", "plan": "results/arm_c_ext_r6_2026-10-11/ext_plan.json",
            "readout": "results/arm_c_ext_r6_2026-10-11/readout.json",
            "before": "results/arm_c_ext_r5_2026-10-10/readout.json", "runs": runs, "value": values(), "cost": cost()}


def main():
    result = build()
    (HERE / "checks.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8", newline="\n")
    for run in result["runs"]:
        e, c = run["energy"], run["cr19"]
        print(run["site"], run["state"], round(e["difference_meV"], 3), "meV", e["outcome"], "| Cr 19",
              c["configuration"], c["end_to_state"], "| largest change", run["occupations"]["largest_change_from_own"],
              flush=True)
    print("values unchanged", result["value"]["unchanged"], "| SU", round(result["cost"]["total_su"], 2), flush=True)


if __name__ == "__main__":
    main()
