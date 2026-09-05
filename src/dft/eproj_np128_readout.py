#!/usr/bin/env python3
"""Readout for the S0 gate-(e) pair re-realised on Anvil at np = 128 (adopted 2026-09-05).

Written and committed BEFORE the outputs landed (array 20419733).

Registered rule, inherited from A8.5 and parsed out of docs/43 at run time (never copied
into source): a leg AGREES with its banked Vast original when |dE| <= 1e-5 Ry
(docs/43:1613-1616). The paired difference E(atomic) - E(ortho) is re-formed from the
Anvil pair and printed beside the banked one. No banked value moves in any branch.

Also reports, per leg: JOB DONE, non-convergence, and whether the A6.5(1) charge
readout (.lowdin.txt) exists beside the output.

Refuses to score (exit 3) while any output is missing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREREG = os.path.join(ROOT, "docs", "43-prereg-week1-factorial.md")
BANKED_DIR = os.path.join(ROOT, "runs", "s0", "e_proj")
NEW_DIR = os.path.join(ROOT, "runs", "a0", "eproj_np128")
STEMS = ("s0_O__u715_atomic", "s0_O__u715_ortho")


class Fatal(RuntimeError):
    pass


def registered(path: str = PREREG) -> float:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"an Anvil re-run of a banked deck agrees\s*\nwhen \|ΔE\| ≤ \*\*([\d.e-]+) Ry\*\*", text)
    if not m:
        raise Fatal("could not parse A8.5's re-run tolerance from docs/43")
    return float(m.group(1))


def final_energy(out: str) -> dict:
    if not os.path.exists(out):
        return {"exists": False}
    with open(out, "rb") as fh:
        blob = fh.read().decode("utf-8", "replace")
    bang = re.findall(r"^!\s+total energy\s+=\s+([-\d.]+) Ry", blob, re.M)
    cores = re.search(r"running on\s+(\d+) processor cores", blob)
    return {
        "exists": True,
        "job_done": blob.count("JOB DONE"),
        "not_achieved": blob.count("convergence NOT achieved"),
        "E_Ry": float(bang[-1]) if bang else None,
        "cores": int(cores.group(1)) if cores else None,
    }


def score(tol: float, new_dir: str = NEW_DIR, banked_dir: str = BANKED_DIR) -> dict:
    res = {"tolerance_Ry": tol, "legs": {}, "pending": []}
    for stem in STEMS:
        new = final_energy(os.path.join(new_dir, stem + ".out"))
        old = final_energy(os.path.join(banked_dir, stem + ".out"))
        row = {"new": new, "banked": old,
               "lowdin": os.path.exists(os.path.join(new_dir, stem + ".lowdin.txt"))}
        if not new.get("exists") or new.get("E_Ry") is None or new.get("job_done", 0) < 1:
            res["pending"].append(stem)
        else:
            dE = new["E_Ry"] - old["E_Ry"]
            row["dE_Ry"] = dE
            row["verdict"] = "AGREES" if abs(dE) <= tol else "DISAGREES"
            if new["not_achieved"]:
                row["verdict"] = "NOT CONVERGED (no number)"
        res["legs"][stem] = row
    if not res["pending"]:
        a, o = res["legs"][STEMS[0]], res["legs"][STEMS[1]]
        res["pair_new_Ry"] = a["new"]["E_Ry"] - o["new"]["E_Ry"]
        res["pair_banked_Ry"] = a["banked"]["E_Ry"] - o["banked"]["E_Ry"]
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    tol = registered()
    res = score(tol)
    print("gate-(e) pair at np = 128 -- A8.5 tolerance |dE| <= %.0e Ry (docs/43:1613-1616)" % tol)
    for stem, row in res["legs"].items():
        if stem in res["pending"]:
            print("  %-20s PENDING" % stem)
            continue
        print("  %-20s Anvil %.8f  banked %.8f  dE %+.2e Ry  cores %s->%s  lowdin %s  -> %s"
              % (stem, row["new"]["E_Ry"], row["banked"]["E_Ry"], row["dE_Ry"],
                 row["banked"]["cores"], row["new"]["cores"], row["lowdin"], row["verdict"]))
    if not res["pending"]:
        print("  E(atomic) - E(ortho): Anvil %.8f Ry  beside banked %.8f Ry" % (res["pair_new_Ry"], res["pair_banked_Ry"]))
    if args.json:
        with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(res, fh, indent=2)
    return 3 if res["pending"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fatal as e:
        print("REFUSE:", e, file=sys.stderr)
        sys.exit(4)
