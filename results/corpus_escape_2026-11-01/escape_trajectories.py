"""Tier 1a escape trajectories, step by step: every escape SCF's total energy against the held arm's final energy, the
total force, and the adsorbate's distance from the mirror plane. Descriptive only. The decision rule (collect.py)
scores converged arms; none of the six escape arms converged, so this file classifies nothing.

Pairing: each "!" energy belongs to the geometry in the ATOMIC_POSITIONS block printed before it (the first SCF uses
the deck's start). Writes escape_trajectories.json and prints a table.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
RY_MEV = 13605.693122
ENERGY = re.compile(r"^!\s+total energy\s+=\s+([-0-9.]+)\s+Ry", re.M)
FORCE = re.compile(r"Total force =\s+([0-9.]+)")
POS = re.compile(r"ATOMIC_POSITIONS [({]crystal[)}]\s*\n")


def positions(text, start, nat):
    rows = text[start:].splitlines()[:nat]
    return [[float(v) for v in r.split()[1:4]] for r in rows]


def species(text, start, nat):
    return [r.split()[0] for r in text[start:].splitlines()[:nat]]


def dist(a, b, L):
    """Minimum-image distance in A on the diagonal cell, periodic in x and y only (slab, vacuum along z)."""
    d = []
    for k in range(3):
        u = a[k] - b[k]
        if k < 2:
            u -= round(u)
        d.append(u * L[k])
    return sum(v * v for v in d) ** 0.5


def bonds(pos, spec, case):
    """O_bind-O_distal, O_distal-H, and each adsorbate atom's nearest neighbour outside the adsorbate."""
    L = case["cell_lengths_A"]
    role = {v["role"]: int(k) for k, v in case["displacement"].items()}
    ob, od, h = role["O_bind"], role["O_distal"], role["H"]
    ads = set(case["adsorbate_index1"])
    out = {"O_bind-O_distal": round(dist(pos[ob - 1], pos[od - 1], L), 3),
           "O_distal-H": round(dist(pos[od - 1], pos[h - 1], L), 3),
           "O_bind-H": round(dist(pos[ob - 1], pos[h - 1], L), 3)}
    for name, i in (("O_bind", ob), ("O_distal", od), ("H", h)):
        near = min((dist(pos[i - 1], pos[j], L), j + 1) for j in range(len(pos)) if j + 1 not in ads)
        out[name + "_nearest_slab"] = {"atom": near[1], "species": spec[near[1] - 1], "A": round(near[0], 3)}
    return out


def d_off(pos, case):
    axis = {"x": 0, "y": 1}[case["locked_axis"]]
    L = case["cell_lengths_A"][axis]
    offs = []
    for i in case["adsorbate_index1"]:
        u = pos[i - 1][axis] - case["plane_crystal"]
        offs.append(abs(u - round(u)) * L)
    return max(offs)


def slab_shift(a, b, spec, case):
    """How far the slab (every atom outside the adsorbate) sits from the held final structure: largest and RMS
    displacement, and the three atoms that moved most."""
    L = case["cell_lengths_A"]
    ads = set(case["adsorbate_index1"])
    d = sorted(((dist(a[j], b[j], L), j + 1) for j in range(len(a)) if j + 1 not in ads), reverse=True)
    return {"max_A": round(d[0][0], 3), "rms_A": round((sum(v * v for v, _ in d) / len(d)) ** 0.5, 3),
            "top3": [{"atom": j, "species": spec[j - 1], "A": round(v, 3)} for v, j in d[:3]]}


def final_energy(path):
    found = ENERGY.findall(path.read_text(encoding="utf-8", errors="replace"))
    return float(found[-1]) if found else None


def trajectory(case):
    deck = ROOT / case["decks"]["escape"]
    held_E = final_energy((ROOT / case["decks"]["held"]).with_suffix(".out"))
    text = deck.with_suffix(".out").read_text(encoding="utf-8", errors="replace")
    deck_text = deck.read_text(encoding="utf-8")
    start_pos = positions(deck_text, POS.search(deck_text).end(), case["nat"])
    spec = species(deck_text, POS.search(deck_text).end(), case["nat"])
    held_text = (ROOT / case["decks"]["held"]).with_suffix(".out").read_text(encoding="utf-8", errors="replace")
    held_final = positions(held_text, list(POS.finditer(held_text))[-1].end(), case["nat"])
    blocks = [(m.start(), m.end()) for m in POS.finditer(text)]
    forces = [(m.start(), float(m.group(1))) for m in FORCE.finditer(text)]
    steps = []
    for k, m in enumerate(ENERGY.finditer(text), 1):
        before = [b for b in blocks if b[0] < m.start()]
        pos = positions(text, before[-1][1], case["nat"]) if before else start_pos
        f = [v for s, v in forces if s > m.start()]
        steps.append({"scf": k, "E_Ry": float(m.group(1)),
                      "dE_vs_held_final_meV": round((float(m.group(1)) - held_E) * RY_MEV, 2),
                      "total_force_Ry_bohr": f[0] if f else None, "d_off_A": round(d_off(pos, case), 4)})
    best = min(steps, key=lambda s: s["E_Ry"])
    # the last geometry with an energy (the block after the last "!" is the optimizer's next, uncomputed proposal)
    last_e = list(ENERGY.finditer(text))[-1].start()
    last_pos = positions(text, [b for b in blocks if b[0] < last_e][-1][1], case["nat"])
    last10 = steps[-10:]
    slope = (last10[-1]["E_Ry"] - last10[0]["E_Ry"]) * RY_MEV / (len(last10) - 1)
    return {"metal": case["metal"], "job": case["job"], "held_final_E_Ry": held_E, "n_scf": len(steps),
            "stop": ("nstep reached" if "maximum number of steps has been reached" in text
                     else "runner wall ceiling" if deck.with_suffix(".KILLED").exists() else "other"),
            "first": steps[0], "lowest": best, "last": steps[-1],
            "slope_last10_meV_per_step": round(slope, 3),
            "max_d_off_A": max(s["d_off_A"] for s in steps),
            "min_dE_vs_held_meV_with_d_off_above_0.10": min(
                [s["dE_vs_held_final_meV"] for s in steps if s["d_off_A"] > 0.10], default=None),
            "slab_shift_escape_last_vs_held_final_A": slab_shift(held_final, last_pos, spec, case),
            "bonds_held_final": bonds(held_final, spec, case), "bonds_escape_start": bonds(start_pos, spec, case),
            "bonds_escape_last": bonds(last_pos, spec, case), "steps": steps}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cases = [c for c in CASES["cases"] if c["launch_group"] == "tier1a"]
    out = {"schema": "corpus-escape-trajectories-v1", "classifies": False, "cases": [trajectory(c) for c in cases]}
    (HERE / "escape_trajectories.json").write_bytes((json.dumps(out, indent=1) + "\n").encode())
    print("%-5s %-14s %4s  %9s %7s  %9s %7s %4s  %9s %7s %8s  %7s" % (
        "oxide", "stop", "scf", "dE first", "d_off", "dE low", "d_off", "at", "dE last", "d_off", "F last",
        "slope"))
    for t in out["cases"]:
        f, lo, la = t["first"], t["lowest"], t["last"]
        print("%-5s %-14s %4d  %9.2f %7.3f  %9.2f %7.3f %4d  %9.2f %7.3f %8.4f  %7.3f" % (
            t["metal"], t["stop"], t["n_scf"], f["dE_vs_held_final_meV"], f["d_off_A"],
            lo["dE_vs_held_final_meV"], lo["d_off_A"], lo["scf"], la["dE_vs_held_final_meV"], la["d_off_A"],
            la["total_force_Ry_bohr"] or float("nan"), t["slope_last10_meV_per_step"]))
    print()
    for t in out["cases"]:
        for when in ("bonds_held_final", "bonds_escape_last"):
            b = t[when]
            print("%-5s %-18s O-O %5.3f  Od-H %5.3f  Ob-H %5.3f  | Ob~%s%d %5.3f  Od~%s%d %5.3f  H~%s%d %5.3f" % (
                t["metal"], when, b["O_bind-O_distal"], b["O_distal-H"], b["O_bind-H"],
                *[x for n in ("O_bind", "O_distal", "H") for x in (b[n + "_nearest_slab"]["species"],
                                                                   b[n + "_nearest_slab"]["atom"],
                                                                   b[n + "_nearest_slab"]["A"])]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
