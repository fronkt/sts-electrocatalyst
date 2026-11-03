"""Continuation trajectories, step by step, with the tier 1a functions (results/corpus_escape_2026-11-01/
escape_trajectories.py, imported, not copied): each continuation SCF's energy against the tier 1a held arm's final
energy, the total force, d_off, and at the last geometry with an energy the adsorbate bonds and the slab's shift from
the held final structure. Descriptive only; the class of each case comes from collect.py.

Writes cont_trajectories.json and prints a table.
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
_spec = importlib.util.spec_from_file_location("traj_tier1a", ROOT / "results/corpus_escape_2026-11-01/escape_trajectories.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)


def stop(case):
    text = (ROOT / case["decks"]["escape"]).with_suffix(".out").read_text(encoding="utf-8", errors="replace")
    if "bfgs converged" in text:
        return "bfgs converged"
    if "maximum number of steps has been reached" in text:
        return "nstep reached"
    return "other"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cases = []
    for case in CASES["cases"]:
        t = T.trajectory(case)
        t["stop"] = stop(case)
        t["tier1a_last_E_Ry"] = case["continues"]["last_E_Ry"]
        t["tier1a_n_scf"] = case["continues"]["n_scf"]
        t["dE_cont_last_minus_tier1a_last_meV"] = round((t["last"]["E_Ry"] - t["tier1a_last_E_Ry"]) * T.RY_MEV, 2)
        cases.append(t)
    out = {"schema": "corpus-escape-cont-trajectories-v1", "classifies": False, "cases": cases}
    (HERE / "cont_trajectories.json").write_bytes((json.dumps(out, indent=1) + "\n").encode())
    print("%-5s %-15s %4s  %9s  %9s %7s %8s %7s  %9s  %s" % (
        "oxide", "stop", "scf", "dE first", "dE last", "d_off", "F last", "slope", "cont gain", "slab max/rms"))
    for t in cases:
        f, la, s = t["first"], t["last"], t["slab_shift_escape_last_vs_held_final_A"]
        print("%-5s %-15s %4d  %9.2f  %9.2f %7.3f %8.4f %7.3f  %9.2f  %.3f/%.3f %s" % (
            t["metal"], t["stop"], t["n_scf"], f["dE_vs_held_final_meV"], la["dE_vs_held_final_meV"], la["d_off_A"],
            la["total_force_Ry_bohr"] or float("nan"), t["slope_last10_meV_per_step"],
            t["dE_cont_last_minus_tier1a_last_meV"], s["max_A"], s["rms_A"],
            " ".join("%s%d:%.3f" % (a["species"], a["atom"], a["A"]) for a in s["top3"])))
    print()
    for t in cases:
        b = t["bonds_escape_last"]
        print("%-5s O-O %5.3f  Od-H %5.3f  Ob-H %5.3f  | Ob~%s%d %5.3f  Od~%s%d %5.3f  H~%s%d %5.3f" % (
            t["metal"], b["O_bind-O_distal"], b["O_distal-H"], b["O_bind-H"],
            *[x for n in ("O_bind", "O_distal", "H") for x in (b[n + "_nearest_slab"]["species"],
                                                               b[n + "_nearest_slab"]["atom"],
                                                               b[n + "_nearest_slab"]["A"])]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
