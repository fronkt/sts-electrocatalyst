#!/usr/bin/env python3
"""Readout for the CrO2 q = 3x3x3 hp.x pair (A12b rider, adopted 2026-09-05).

Written and committed BEFORE the outputs landed (jobs 20419730 atomic, 20419731 ortho).

Registered rule, inherited and parsed out of docs/43 at run time (never copied into
source): a leg PASSES the q-mesh check if |U(q333) - U(q222)| < the deposited q-mesh
threshold (docs/43:276, "dU < 0.2 eV vs the next finer mesh"; A12b.R2 :3497-3505).
No threshold exists on the size of the split; it is re-formed at q333 and printed
beside the banked q222 split.

The A12b.R4 isolation check is repeated on the SCFs (U Cr-3d 1.d-8 on both legs):
  * ortho: the q222 leg ran on Anvil at np = 20 (job 20382206) -> the printed total
    energy string, total magnetisation and iteration count must MATCH;
  * atomic: the q222 leg ran on the Vast box -> A8.5's |dE| <= 1e-5 Ry applies
    (docs/43:1613-1616), parsed at run time as well.

Refuses to score (exit 3) while any output is missing; scores on assumption never.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p15_readout import Fatal, hp_qc, one_u, read_u, scf_magnetisation  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREREG = os.path.join(ROOT, "docs", "43-prereg-week1-factorial.md")
NEW = os.path.join(ROOT, "runs", "hp_cro2_q333")

BANKED = {
    "atomic": {
        "dat": os.path.join(ROOT, "runs", "hp_tio2", "hp__cro2_q222.Hubbard_parameters.dat"),
        "scf": os.path.join(ROOT, "runs", "hp_tio2", "scf__cro2.out"),
        "machine": "vast",
    },
    "ortho": {
        "dat": os.path.join(ROOT, "runs", "hp_cro2_ortho", "cro2_ortho.Hubbard_parameters.dat"),
        "scf": os.path.join(ROOT, "runs", "hp_cro2_ortho", "scf__cro2_ortho.out"),
        "machine": "anvil",
    },
}


def registered(path: str = PREREG) -> dict:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"q-mesh convergence \| ΔU < ([\d.]+) eV vs the next finer mesh", text)
    if not m:
        raise Fatal("could not parse the q-mesh threshold from docs/43")
    m2 = re.search(r"an Anvil re-run of a banked deck agrees\s*\nwhen \|ΔE\| ≤ \*\*([\d.e-]+) Ry\*\*", text)
    if not m2:
        raise Fatal("could not parse A8.5's re-run tolerance from docs/43")
    return {"q_mesh_dU_max_eV": float(m.group(1)), "rerun_dE_max_Ry": float(m2.group(1))}


def scf_facts(out: str) -> dict:
    """Final '!' energy (as printed string and float), iterations, JOB DONE, non-convergence."""
    if not os.path.exists(out):
        return {"exists": False}
    with open(out, "rb") as fh:
        blob = fh.read().decode("utf-8", "replace")
    bang = re.findall(r"^!\s+total energy\s+=\s+([-\d.]+) Ry", blob, re.M)
    it = re.findall(r"convergence has been achieved in\s+(\d+) iterations", blob)
    return {
        "exists": True,
        "job_done": blob.count("JOB DONE"),
        "not_achieved": blob.count("convergence NOT achieved"),
        "E_str": bang[-1] if bang else None,
        "E_Ry": float(bang[-1]) if bang else None,
        "iterations": int(it[-1]) if it else None,
        "mag": scf_magnetisation(out),
    }


def find_dat(leg: str) -> str | None:
    hits = sorted(glob.glob(os.path.join(NEW, "*cro2_%s_q333*Hubbard_parameters.dat" % leg)))
    return hits[-1] if hits else None


def score(reg: dict, new_dir: str = NEW, banked: dict = BANKED) -> dict:
    res = {"registered": reg, "legs": {}, "pending": []}
    for leg in ("atomic", "ortho"):
        hp_out = os.path.join(new_dir, "hp__cro2_%s_q333.out" % leg)
        scf_out = os.path.join(new_dir, "scf__cro2_%s_q333.out" % leg)
        dat = find_dat(leg) if new_dir == NEW else (sorted(glob.glob(os.path.join(new_dir, "*cro2_%s_q333*Hubbard_parameters.dat" % leg))) or [None])[-1]
        qc = hp_qc(hp_out)
        row = {"hp_out": os.path.relpath(hp_out, ROOT), "hp_qc": qc, "dat": dat and os.path.relpath(dat, ROOT)}
        if not qc["exists"] or dat is None:
            res["pending"].append(leg)
            res["legs"][leg] = row
            continue
        U333 = one_u(read_u(dat), "Cr", dat)
        U222 = one_u(read_u(banked[leg]["dat"]), "Cr", banked[leg]["dat"])
        dU = U333 - U222
        row.update({"U_q333_eV": U333, "U_q222_eV": U222, "dU_eV": dU})
        if not qc["clean"]:
            row["q_mesh"] = "NO U (hp.x did not converge; a methods limit, not a dU)"
        else:
            row["q_mesh"] = "PASS" if abs(dU) < reg["q_mesh_dU_max_eV"] else "UNCONVERGED (absolute U reported as q-mesh-unconverged)"
        # isolation check on the SCF
        new = scf_facts(scf_out)
        old = scf_facts(banked[leg]["scf"])
        iso = {"new": new, "banked": old, "banked_machine": banked[leg]["machine"]}
        if new.get("E_Ry") is not None and old.get("E_Ry") is not None:
            dE = new["E_Ry"] - old["E_Ry"]
            iso["dE_Ry"] = dE
            same_mag = (new["mag"] or {}).get("total_muB") == (old["mag"] or {}).get("total_muB")
            same_it = new["iterations"] == old["iterations"]
            if banked[leg]["machine"] == "anvil":
                iso["verdict"] = "MATCH" if (new["E_str"] == old["E_str"] and same_mag and same_it) else "DIFFERS (printed decimals)"
            else:
                iso["verdict"] = "AGREES (A8.5)" if abs(dE) <= reg["rerun_dE_max_Ry"] else "DISAGREES (A8.5 %.1e Ry)" % reg["rerun_dE_max_Ry"]
        row["scf_isolation"] = iso
        res["legs"][leg] = row
    if not res["pending"]:
        a, o = res["legs"]["atomic"], res["legs"]["ortho"]
        res["split_q333_eV"] = o["U_q333_eV"] - a["U_q333_eV"]
        res["split_q222_eV"] = o["U_q222_eV"] - a["U_q222_eV"]
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the readout here as well")
    args = ap.parse_args(argv)
    reg = registered()
    res = score(reg)
    print("CrO2 q333 pair -- q-mesh threshold dU < %.2f eV (docs/43:276); A8.5 re-run tolerance %.0e Ry"
          % (reg["q_mesh_dU_max_eV"], reg["rerun_dE_max_Ry"]))
    for leg, row in res["legs"].items():
        if leg in res["pending"]:
            print("  %-6s PENDING (no hp output / no Hubbard_parameters.dat yet)" % leg)
            continue
        print("  %-6s U(q333) %.4f  U(q222) %.4f  dU %+.4f eV  -> %s" % (leg, row["U_q333_eV"], row["U_q222_eV"], row["dU_eV"], row["q_mesh"]))
        iso = row["scf_isolation"]
        print("         SCF isolation vs %s q222 leg: %s (dE %s Ry)" % (iso["banked_machine"], iso.get("verdict", "n/a"), ("%.2e" % iso["dE_Ry"]) if "dE_Ry" in iso else "n/a"))
    if not res["pending"]:
        print("  split ortho-atomic: q333 %+.4f eV  beside q222 %+.4f eV" % (res["split_q333_eV"], res["split_q222_eV"]))
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
