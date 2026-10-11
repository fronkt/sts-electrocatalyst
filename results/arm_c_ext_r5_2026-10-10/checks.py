"""Round 5's checks, set before launch (design record, Round 5, "What a result means"), from the committed mirrors.

- energy: the converged slab against the production slab (arm C, 2026-10-07), each from its own output, with the
  Hubbard energy of each. More than 1 meV lower is the readout's rule for replacing the production slab.
- Fe 22: its occupations at convergence against every converged state at the site (the production slab, OH and OOH
  from round 3's site_occupations/, and round 4's O). It is in the slab's or OH's configuration if they lie within
  0.47 of that state's, half the 0.94 between the two; otherwise in another configuration. The distance is the
  Frobenius norm of the difference over both spins, as in the Round 3 and Round 4 readouts.
- every slab Hubbard atom's change from the production slab, with its distance to each converged state, and the
  moments QE integrates on every atom's sphere against the production slab's and OH's.
- the cell's total moment against the production slab's 41.98 uB.
- the value: the site's steps with the production slab and with this one; the shifts in E(O), and in the adsorbed
  states against the slab, over which step 1 stays limiting; and the order of the alloys before and after.
Also the run's SCF trajectory: the held iterations and each iteration's energy, accuracy and magnetization.

Writes checks.json next to this file. Offline and read-only.
"""
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R3 = ROOT / "results/arm_c_ext_r3_2026-10-09"
R4 = ROOT / "results/arm_c_ext_r4_2026-10-10"
ARM_C = ROOT / "results/arm_c_2026-10-07"
OH_MIRROR = ROOT / "results/arm_c_ext_r2_2026-10-08"
_spec = importlib.util.spec_from_file_location("r4_checks", R4 / "checks.py")
r4c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r4c)  # round 4's scf(), distance() and moment(); r4c.r3t puts src/dft on sys.path
r3t, ext = r4c.r3t, r4c.ext
import arm_c_readout as readout  # noqa: E402

PLAN = json.loads((HERE / "ext_plan.json").read_text(encoding="utf-8"))
READOUT = json.loads((HERE / "readout.json").read_text(encoding="utf-8"))
BEFORE = json.loads((R4 / "readout.json").read_text(encoding="utf-8"))
OH_PLAN = json.loads((OH_MIRROR / "ext_plan.json").read_text(encoding="utf-8"))  # round 2 converged the OH
RY_EV = r4c.RY_EV
HALF_WAY = 0.47  # design record, Round 5, set before launch
ATOM = 22
STEP_LIMIT_V = 1.23

FINAL = re.compile(r"^!\s+total energy\s+=\s+(-?[0-9.]+)\s+Ry", re.M)
HUBBARD = re.compile(r"Hubbard energy\s+=\s+(-?[0-9.]+)\s+Ry")
SITES = "Magnetic moment per site"
SITE_LINE = re.compile(r"atom\s+(\d+)\s+\(R=\s*[0-9.]+\)\s+charge=\s*(-?[0-9.]+)\s+magn=\s*(-?[0-9.]+)")


def final(out):
    """The converged energy and Hubbard energy (Ry), and each atom's sphere-integrated (charge, moment)."""
    text = out.read_text(errors="replace")
    energies, hubbard = FINAL.findall(text), HUBBARD.findall(text)
    if len(energies) != 1 or "convergence has been achieved" not in text:
        raise ValueError(f"{out}: not one converged energy")
    sites = {}
    for m in SITE_LINE.finditer(text[text.rindex(SITES):]):
        if int(m.group(1)) in sites:
            break
        sites[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    return float(energies[0]), float(hubbard[-1]), sites


def energy_check(row, site_row, run):
    first = row["first"]
    production, hub_first, _ = final(ARM_C / "raw_mirror/runs" / row["site_dir"] / (first["job"] + ".out"))
    converged, hub_new, _ = final(HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".out"))
    if abs(production * RY_EV - first["E_eV"]) > 1e-6:
        raise ValueError(f"production slab {production} Ry is not the plan's first run")
    gap = (converged - production) * RY_EV * 1e3
    recorded = site_row["states"]["slab"]["energy_vs_first_meV"]
    if abs(gap - recorded) > 1e-6:
        raise ValueError(f"energy gap {gap} meV is not the readout's {recorded}")
    hubbard = (hub_new - hub_first) * RY_EV * 1e3
    return {"production_Ry": production, "converged_Ry": converged, "difference_mRy": (converged - production) * 1e3,
            "difference_meV": gap, "rule_meV": readout.SECOND_START_MEV,
            "outcome": "lower" if gap < -readout.SECOND_START_MEV else
                       "within" if gap <= readout.SECOND_START_MEV else "higher",
            "first_iteration_below_production": next((r["iteration"] for r in run["per_iteration"]
                                                      if r["energy_Ry"] < production), None),
            "hubbard_energy_Ry": {"production": hub_first, "converged": hub_new},
            "hubbard_difference_meV": hubbard, "rest_difference_meV": gap - hubbard}


def site_states(site):
    """Every converged state's occupations at the site: round 3's site files and round 4's O."""
    files = [f for f in json.loads((R3 / "site_occupations.json").read_text(encoding="utf-8"))["files"]
             if f["site"] == site]
    states = {f["state"]: r3t.occupations(R3 / f["local"]) for f in files}
    jobs = {f["state"]: f["job"] for f in files}
    o_row = r4c.PLAN["selection"][0]
    states["O"], jobs["O"] = r3t.occupations(r4c.saved(R4, o_row["dir"], o_row["job"])), o_row["job"]
    return states, jobs


def occupation_check(row, site, states):
    """Each slab Hubbard atom at convergence against the production slab, the start and every converged state."""
    names = sorted(states)
    end = r3t.occupations(r4c.saved(HERE, row["dir"], row["job"]))
    start = r3t.occupations(ROOT / row["bundle"] / "occup.txt")
    cell, atoms = ext.geometry((HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".run.in")).read_text())
    o_row = r4c.PLAN["selection"][0]
    _, o_atoms = ext.geometry((R4 / "raw_mirror/runs" / o_row["dir"] / (o_row["job"] + ".run.in")).read_text())
    o1, fe22 = o_atoms[ext.SLAB_ATOMS][1], atoms[ATOM - 1][1]
    rows = []
    for i in range(ext.SLAB_ATOMS):
        if not end[i].any() and not any(states[s][i].any() for s in names):
            continue
        to_state = {s: r4c.distance(end[i], states[s][i]) for s in names}
        pairs = {a + "-" + b: r4c.distance(states[a][i], states[b][i]) for k, a in enumerate(names) for b in names[k + 1:]}
        rows.append({"atom": i + 1, "species": atoms[i][0], "z": round(atoms[i][1][2], 2),
                     "distance_to_O1": round(ext.in_plane_distance(cell, o1, atoms[i][1]), 3),
                     "distance_to_fe22": round(ext.in_plane_distance(cell, fe22, atoms[i][1]), 3),
                     "end_to_production": to_state["slab"], "end_to_start": r4c.distance(end[i], start[i]),
                     "nearest_state": min(names, key=lambda s: (to_state[s], s)), "end_to_state": to_state,
                     "between_converged": pairs,
                     "moment": {"end": r4c.moment(end[i]), "start": r4c.moment(start[i]),
                                **{s: r4c.moment(states[s][i]) for s in names}}})
    rows.sort(key=lambda r: (-r["end_to_production"], r["atom"]))
    return {"states": names, "hubbard_atoms": len(rows), "atoms": rows}


def fe22_check(occupations):
    fe = next(r for r in occupations["atoms"] if r["atom"] == ATOM)
    to = fe["end_to_state"]
    configuration = "OH" if to["OH"] <= HALF_WAY else "slab" if to["slab"] <= HALF_WAY else "other"
    return {"end_to_state": to, "slab_to_OH": fe["between_converged"]["OH-slab"], "half_way": HALF_WAY,
            "configuration": configuration, "nearest_state": fe["nearest_state"], "moment": fe["moment"],
            "all_states_share_it": configuration == "OH" and all(to[s] <= HALF_WAY for s in ("OH", "O", "OOH"))}


def sphere_check(row, site_row):
    """QE's sphere-integrated moments (uB) of every atom: this slab against the production slab and OH."""
    first = row["first"]
    _, _, new = final(HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".out"))
    _, _, old = final(ARM_C / "raw_mirror/runs" / row["site_dir"] / (first["job"] + ".out"))
    oh_row = next(s for s in OH_PLAN["selection"]
                  if s["site_dir"] == row["site_dir"] and s["job"] == site_row["states"]["OH"]["job"])
    _, _, oh = final(OH_MIRROR / "raw_mirror/runs" / oh_row["dir"] / (oh_row["job"] + ".out"))
    _, atoms = ext.geometry((HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".run.in")).read_text())
    rows = [{"atom": a, "species": atoms[a - 1][0], "end": new[a][1], "production": old[a][1], "OH": oh[a][1],
             "change": round(new[a][1] - old[a][1], 4), "charge_change": round(new[a][0] - old[a][0], 4)}
            for a in sorted(new)]
    rows.sort(key=lambda r: (-abs(r["change"]), r["atom"]))
    metals = [r for r in rows if r["species"] != "O"]
    oxygens = [r for r in rows if r["species"] == "O"]
    state = site_row["states"]["slab"]
    return {"total_uB": state["total_magnetization"], "production_total_uB": first["total_magnetization"],
            "total_change_uB": state["magnetization_vs_first_uB"],
            "sphere_change_metals_uB": round(sum(r["change"] for r in metals), 4),
            "sphere_change_oxygen_uB": round(sum(r["change"] for r in oxygens), 4),
            "atoms": rows}


def value(site_row, before_row):
    steps = site_row["steps_eV"]
    # E(O) + d moves dG2 by +d and dG3 by -d: step 1 stays limiting for d in [dG3 - dG1, dG1 - dG2].
    # G(OH), G(O) and G(OOH) all + s against the slab move dG1 by +s and dG4 by -s: eta follows s one for one
    # down to s = dG3 - dG1, where the steps s leaves alone take over (eta_floor_V).
    return {"eta_V": site_row["eta_dft_V"], "eta_with_production_slab_V": site_row["eta_dft_V_with_first"],
            "eta_round_4_V": before_row["eta_dft_V"],
            "rise_mV": (site_row["eta_dft_V"] - site_row["eta_dft_V_with_first"]) * 1e3,
            "steps_eV": steps, "steps_with_production_slab_eV": before_row["steps_eV"],
            "potential_limiting_step": site_row["potential_limiting_step"],
            "E_O_shift_window_eV": [steps[2] - steps[0], steps[0] - steps[1]],
            "adsorbed_shift_floor_eV": steps[2] - steps[0],
            "eta_floor_V": max(steps[1], steps[2]) - STEP_LIMIT_V,
            "order_before": BEFORE["exploratory_predictions"]["order_all_with_values"],
            "order": READOUT["exploratory_predictions"]["order_all_with_values"],
            "C_V": {a: READOUT["alloys"][a]["C_V"] for a in READOUT["exploratory_predictions"]["order_all_with_values"]}}


def build():
    row = PLAN["selection"][0]
    site = Path(row["dir"]).name
    site_row = next(s for s in READOUT["sites"] if s["dir"] == row["site_dir"])
    before_row = next(s for s in BEFORE["sites"] if s["dir"] == row["site_dir"])
    states, jobs = site_states(site)
    accepted = {s: site_row["states"][s]["job"] for s in ("OH", "O", "OOH")}
    if {s: jobs[s] for s in accepted} != accepted or jobs["slab"] != row["first"]["job"]:
        raise ValueError(f"site files {jobs} are not the readout's converged states {accepted}")
    if site_row["states"]["slab"]["job"] != row["job"]:
        raise ValueError("the readout does not use round 5's slab")
    run = r4c.scf(HERE / "raw_mirror/runs" / row["dir"] / (row["job"] + ".out"), row["mixing"]["mixing_fixed_ns"])
    occupations = occupation_check(row, site, states)
    return {"schema": "s8-arm-c-ext-r5-checks-v1", "plan": "results/arm_c_ext_r5_2026-10-10/ext_plan.json",
            "readout": "results/arm_c_ext_r5_2026-10-10/readout.json", "site": site, "state": row["state"],
            "site_states": jobs, "scf": run, "energy": energy_check(row, site_row, run),
            "fe22": fe22_check(occupations), "occupations": occupations, "moments": sphere_check(row, site_row),
            "magnetization_vs_site": site_row["states"]["slab"]["magnetization_vs_site"],
            "value": value(site_row, before_row)}


def main():
    result = build()
    (HERE / "checks.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8", newline="\n")
    e, f, v = result["energy"], result["fe22"], result["value"]
    print("energy", round(e["difference_meV"], 2), "meV", e["outcome"], "| Fe 22", f["configuration"],
          "| eta", round(v["eta_V"], 4), "with production slab", round(v["eta_with_production_slab_V"], 4), flush=True)


if __name__ == "__main__":
    main()
