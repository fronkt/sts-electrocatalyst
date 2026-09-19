"""Trace Quantum ESPRESSO scf/relax outputs cycle by cycle.

For each self-consistent cycle the trace records the iteration count, the
accuracy trajectory, the threshold QE announced for the next cycle
(``new conv_thr``), the total energy, total force, magnetization and wall
clock.  It reads raw output bytes only and never changes a file.

Usage:
    python src/dft/qe_relax_trace.py --out traces.json OUT1 [OUT2 ...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

RY_EV = 13.605693122


def _f(s: str | None) -> float | None:
    return float(s.replace("D", "E")) if s is not None else None


def trace(path: str | Path) -> dict:
    raw = Path(path).read_bytes()
    text = raw.decode("utf-8", errors="replace")
    rec: dict = {"file": str(path).replace("\\", "/"), "bytes": len(raw),
                 "sha256": hashlib.sha256(raw).hexdigest()}
    for key, pat in {
        "conv_thr_header": r"convergence threshold\s*=\s*([0-9.E+-]+)",
        "mixing_beta": r"mixing beta\s*=\s*([0-9.]+)",
        "nat": r"number of atoms/cell\s*=\s*(\d+)",
        "nelec": r"number of electrons\s*=\s*([0-9.]+)",
        "nbnd": r"number of Kohn-Sham states\s*=\s*(\d+)",
        "nk": r"number of k points\s*=\s*(\d+)",
    }.items():
        m = re.search(pat, text)
        rec[key] = m.group(1) if m else None
    rec["hubbard_present"] = "Hubbard" in text
    rec["calculation_relax"] = bool(re.search(r"BFGS Geometry Optimization", text))

    starts = [m.start() for m in re.finditer(r"Self-consistent Calculation", text)]
    cycles = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(text)
        seg = text[s:e]
        # Shutdown text can mention an iteration number without beginning one.
        # An actual header without an accuracy record is not a completed update.
        headers = list(re.finditer(r"(?m)^\s*iteration\s*#\s*(\d+)\b[^\n]*$", seg))
        iterations = []
        for j, header in enumerate(headers):
            end = headers[j + 1].start() if j + 1 < len(headers) else len(seg)
            block = seg[header.end():end]
            accuracy = re.findall(r"estimated scf accuracy\s*<\s*([0-9.E+-]+)\s*Ry", block)
            iterations.append({"iteration": int(header.group(1)),
                               "accuracy_Ry": _f(accuracy[-1]) if accuracy else None})
        completed = [row for row in iterations if row["accuracy_Ry"] is not None]
        accs = [row["accuracy_Ry"] for row in completed]
        conv = re.search(r"convergence has been achieved in\s*(\d+) iterations", seg)
        etot = re.search(r"!\s+total energy\s*=\s*([-0-9.]+) Ry", seg)
        tmag = re.findall(r"total magnetization\s*=\s*([-0-9.]+) Bohr mag/cell", seg)
        amag = re.findall(r"absolute magnetization\s*=\s*([-0-9.]+) Bohr mag/cell", seg)
        tf = re.search(r"Total force =\s*([0-9.]+)\s+Total SCF correction =\s*([0-9.]+)", seg)
        newthr = re.search(r"new conv_thr\s*=\s*([0-9.E+-]+)", seg)
        bfgs = re.search(r"number of bfgs steps\s*=\s*(\d+)", seg)
        trust = re.search(r"new trust radius\s*=\s*([0-9.]+) bohr", seg)
        walls = re.findall(r"total cpu time spent up to now is\s*([0-9.]+) secs", seg)
        first_below = {}
        for thr in (1e-6, 5e-7, 1e-7, 1e-8):
            hit = next((row["iteration"] for row in completed if row["accuracy_Ry"] < thr), None)
            first_below["%.0e" % thr] = hit
        plateau = [row["accuracy_Ry"] for row in completed if row["iteration"] > 40]
        cycles.append({
            "cycle": i + 1,
            "n_iter": len(completed),
            "n_iter_started": len(iterations),
            "last_iteration_started": iterations[-1]["iteration"] if iterations else None,
            "last_iteration_completed": completed[-1]["iteration"] if completed else None,
            "iteration_records": iterations,
            "converged_in": int(conv.group(1)) if conv else None,
            "acc_min_Ry": min(accs) if accs else None,
            "acc_last_Ry": accs[-1] if accs else None,
            "acc_after_iter40_min_Ry": min(plateau) if plateau else None,
            "acc_after_iter40_max_Ry": max(plateau) if plateau else None,
            "first_iter_below": first_below,
            "etot_Ry": float(etot.group(1)) if etot else None,
            "tmag_first": float(tmag[0]) if tmag else None,
            "tmag_last": float(tmag[-1]) if tmag else None,
            "amag_last": float(amag[-1]) if amag else None,
            "total_force_Ry_bohr": float(tf.group(1)) if tf else None,
            "total_scf_correction_Ry_bohr": float(tf.group(2)) if tf else None,
            "new_conv_thr_after_Ry": _f(newthr.group(1)) if newthr else None,
            "bfgs_steps_after": int(bfgs.group(1)) if bfgs else None,
            "trust_radius_after_bohr": float(trust.group(1)) if trust else None,
            "wall_end_s": float(walls[-1]) if walls else None,
            "accuracy_trajectory_Ry": accs,
        })
    rec["cycles"] = cycles
    rec["bfgs_converged"] = bool(re.search(r"bfgs converged in", text))
    rec["job_done"] = "JOB DONE" in text
    w = re.findall(r"total cpu time spent up to now is\s*([0-9.]+) secs", text)
    rec["wall_last_s"] = float(w[-1]) if w else None
    energies = [float(x) for x in re.findall(r"!\s+total energy\s*=\s*([-0-9.]+) Ry", text)]
    rec["step_energies_Ry"] = energies
    rec["step_energy_drops_meV"] = [round((energies[i] - energies[i - 1]) * RY_EV * 1000, 1)
                                    for i in range(1, len(energies))]
    ieee = re.findall(r"floating-point exceptions are signalling:\s*([A-Z_ ]+)", text)
    rec["ieee_notes"] = dict(Counter(x.strip() for x in ieee))
    rec["hubbard_occupation_lines"] = len(re.findall(r"Tr\[ns\(", text))
    return rec


def table(rec: dict) -> str:
    lines = [rec["file"],
             "conv_thr %s  beta %s  nat %s  nelec %s  nbnd %s  nk %s  relax %s  bfgs_converged %s  JOB DONE %s  wall %s s"
             % (rec["conv_thr_header"], rec["mixing_beta"], rec["nat"], rec["nelec"], rec["nbnd"], rec["nk"],
                rec["calculation_relax"], rec["bfgs_converged"], rec["job_done"], rec["wall_last_s"]),
             "%3s %4s %4s %7s %9s %9s %16s %8s %7s %9s %4s" % ("cyc", "nfin", "nbeg", "conv_in", "acc_last", "acc_min", "E(Ry)", "Ftot", "tmag", "newthr", "bfgs")]
    for c in rec["cycles"]:
        def g(v, fmt):
            return (fmt % v) if v is not None else "-"
        lines.append("%3d %4d %4d %7s %9s %9s %16s %8s %7s %9s %4s" % (
            c["cycle"], c["n_iter"], c["n_iter_started"], g(c["converged_in"], "%d"), g(c["acc_last_Ry"], "%.1e"), g(c["acc_min_Ry"], "%.1e"),
            g(c["etot_Ry"], "%.6f"), g(c["total_force_Ry_bohr"], "%.4f"), g(c["tmag_last"], "%.2f"),
            g(c["new_conv_thr_after_Ry"], "%.1e"), g(c["bfgs_steps_after"], "%d")))
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("outputs", nargs="+")
    ap.add_argument("--out", help="JSON file to write")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    recs = [trace(p) for p in args.outputs]
    if not args.quiet:
        for r in recs:
            print(table(r))
            print()
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(recs, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
