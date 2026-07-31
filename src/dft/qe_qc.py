#!/usr/bin/env python3
"""Strict QC for Quantum ESPRESSO `relax` outputs.

Closes the hole that forced the docs/26 retraction: `qe_slab.py::parse_qe_energy`
accepted **any** file containing `JOB DONE`, and pw.x prints `JOB DONE` even when a
mid-relax SCF cycle died (`convergence NOT achieved after N iterations: stopping`).
Eleven adslab relaxations — including the then-published CrO2 *OH/*OOH points —
passed that check with final forces 17-66x the threshold.

What this module checks, per output file:

  * every ionic step's SCF converged (no `convergence NOT achieved` anywhere);
  * the ionic relaxation actually converged (`bfgs converged` / `End of BFGS
    Geometry Optimization`) rather than exhausting `nstep`;
  * the residual force on the **free** atoms is below threshold.

That last one needs the `if_pos` mask from the matching `.in`: pw.x prints the
*unconstrained* forces, so a slab with its bottom half frozen legitimately shows
large forces on the fixed layers. Judging a run by pw.x's own `Total force =`
line (which sums over fixed atoms too) is what makes converged runs look broken
and broken runs look converged.

Usage
-----
    PYTHONPATH=src python src/dft/qe_qc.py audit runs                # whole tree
    PYTHONPATH=src python src/dft/qe_qc.py audit runs --all-attempts # incl. .out.attemptN
    PYTHONPATH=src python src/dft/qe_qc.py check runs/Cr_slab/s0_OH.out

Exit status of `audit` is 1 if any *primary* (`.out`) file is POISONED.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

RY_EV = 13.605693122
RY_AU_TO_EV_ANG = 25.71104309541616  # 1 Ry/bohr

# pw.x default relax force threshold used across this project (docs/23): 2e-3 Ry/au.
FORC_CONV_THR_RY_AU = 2.0e-3
# Generous audit threshold: a run whose free-atom fmax exceeds this is not usable
# for energetics regardless of what pw.x printed. 5x the relax threshold.
FMAX_AUDIT_RY_AU = 1.0e-2

_RE_SCF_OK = re.compile(r"convergence has been achieved in\s+(\d+) iterations")
_RE_SCF_BAD = re.compile(r"convergence NOT achieved after\s+(\d+) iterations")
_RE_ETOT = re.compile(r"^!\s+total energy\s+=\s+(-?\d+\.\d+)\s+Ry", re.M)
_RE_FORCE_HDR = re.compile(r"Forces acting on atoms")
_RE_FORCE_ATOM = re.compile(
    r"^\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s+=\s+"
    r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)"
)
_RE_TOTAL_FORCE = re.compile(r"Total force\s+=\s+(\d+\.\d+)")
_RE_BFGS_CONV = re.compile(r"bfgs converged in\s+(\d+) scf cycles and\s+(\d+) bfgs steps")
_RE_MAXSTEP = re.compile(r"The maximum number of steps has been reached")
_RE_FINAL_E = re.compile(r"Final energy\s+=\s+(-?\d+\.\d+)\s+Ry")
_RE_NAT = re.compile(r"number of atoms/cell\s+=\s+(\d+)")
# Third false-success mode, found 2026-07-31 when Ni_slab/s0_O was stopped on purpose:
# a `<outdir>/<prefix>.EXIT` flag makes pw.x quit gracefully AND print "JOB DONE.", so
# the run looks finished to every string test we had. The queue log for that job read
# `rc=0 JOB_DONE=1 SCF_FAIL=0` -- passing the first two clauses of the docs/30 s7
# acceptance criterion on a job that had not completed a single ionic step.
_RE_USER_STOP = re.compile(r"Program stopped by user request")


def free_mask(infile: str) -> list[bool] | None:
    """`if_pos` mask from a QE input: True where the atom is free to move.

    Returns None when the input is missing or has no per-atom flags (all free).
    """
    if not os.path.exists(infile):
        return None
    lines = open(infile, errors="ignore").read().splitlines()
    try:
        i = next(i for i, ln in enumerate(lines) if ln.strip().upper().startswith("ATOMIC_POSITIONS"))
    except StopIteration:
        return None
    mask: list[bool] = []
    for ln in lines[i + 1:]:
        s = ln.split()
        if not s:
            continue
        if s[0].isupper() and len(s) <= 2 and not _is_float(s[-1]):  # next card
            break
        if s[0].upper() in ("K_POINTS", "CELL_PARAMETERS", "ATOMIC_SPECIES", "HUBBARD",
                            "OCCUPATIONS", "CONSTRAINTS", "ATOMIC_VELOCITIES"):
            break
        if len(s) < 4 or not _is_float(s[1]):
            break
        if len(s) >= 7:
            mask.append(any(f != "0" for f in s[4:7]))
        else:
            mask.append(True)
    return mask or None


def _is_float(tok: str) -> bool:
    try:
        float(tok)
        return True
    except ValueError:
        return False


def scan(outfile: str, infile: str | None = None) -> dict:
    """Parse one pw.x output into a QC record. Never raises on malformed input."""
    rec: dict = {
        "path": outfile, "exists": os.path.exists(outfile), "job_done": False,
        "n_ionic": 0, "n_scf_ok": 0, "n_scf_fail": 0, "scf_fail_steps": [],
        "bfgs_converged": False, "max_steps_reached": False, "user_stopped": False,
        "energy_ry": None, "energy_ev": None, "n_energies": 0,
        "total_force_ry_au": None, "fmax_free_ry_au": None, "fmax_free_ev_ang": None,
        "nat": None, "n_free": None, "verdict": "MISSING", "reasons": [],
    }
    if not rec["exists"]:
        rec["reasons"].append("file does not exist")
        return rec

    txt = open(outfile, errors="ignore").read()
    rec["job_done"] = "JOB DONE" in txt
    rec["n_scf_ok"] = len(_RE_SCF_OK.findall(txt))
    rec["n_scf_fail"] = len(_RE_SCF_BAD.findall(txt))
    rec["bfgs_converged"] = bool(_RE_BFGS_CONV.search(txt))
    rec["max_steps_reached"] = bool(_RE_MAXSTEP.search(txt))
    rec["user_stopped"] = bool(_RE_USER_STOP.search(txt))
    m = _RE_NAT.search(txt)
    if m:
        rec["nat"] = int(m.group(1))

    energies = _RE_ETOT.findall(txt)
    rec["n_energies"] = len(energies)
    if energies:
        rec["energy_ry"] = float(energies[-1])
        rec["energy_ev"] = rec["energy_ry"] * RY_EV
    mf = _RE_FINAL_E.search(txt)
    if mf:  # pw.x's own final number wins when the relax finished cleanly
        rec["energy_ry"] = float(mf.group(1))
        rec["energy_ev"] = rec["energy_ry"] * RY_EV

    # walk the force blocks; remember the last one and where SCF failures landed
    lines = txt.splitlines()
    last_forces: list[tuple[float, float, float]] = []
    cur: list[tuple[float, float, float]] = []
    in_block = False
    ionic = 0
    for ln in lines:
        if _RE_SCF_BAD.search(ln):
            rec["scf_fail_steps"].append(ionic)
        if _RE_FORCE_HDR.search(ln):
            in_block, cur = True, []
            continue
        if in_block:
            am = _RE_FORCE_ATOM.match(ln)
            if am:
                cur.append((float(am.group(3)), float(am.group(4)), float(am.group(5))))
                continue
            tf = _RE_TOTAL_FORCE.search(ln)
            if tf:
                rec["total_force_ry_au"] = float(tf.group(1))
                if cur:
                    last_forces = cur
                    ionic += 1
                in_block = False
    rec["n_ionic"] = ionic

    if last_forces:
        mask = free_mask(infile) if infile else None
        if mask and len(mask) == len(last_forces):
            sel = [f for f, free in zip(last_forces, mask) if free]
            rec["n_free"] = sum(mask)
        else:
            sel = last_forces  # no mask: judge every atom (conservative)
            if mask:
                rec["reasons"].append(
                    f"if_pos mask length {len(mask)} != {len(last_forces)} atoms; used all atoms")
        if sel:
            fmax = max((fx * fx + fy * fy + fz * fz) ** 0.5 for fx, fy, fz in sel)
            rec["fmax_free_ry_au"] = fmax
            rec["fmax_free_ev_ang"] = fmax * RY_AU_TO_EV_ANG

    # verdict
    r = rec["reasons"]
    if rec["n_scf_fail"]:
        r.append(f"{rec['n_scf_fail']} SCF cycle(s) did not converge "
                 f"(ionic step(s) {rec['scf_fail_steps']})")
    if not rec["job_done"]:
        r.append("no JOB DONE (killed / still running / crashed)")
    if rec["max_steps_reached"]:
        r.append("relaxation hit nstep without converging")
    if not rec["bfgs_converged"] and rec["job_done"] and not rec["max_steps_reached"]:
        r.append("no 'bfgs converged' line (scf-only run, or relax ended abnormally)")
    if rec["user_stopped"]:
        r.append("stopped by user request (.EXIT flag) -- pw.x still printed JOB DONE")
    if rec["energy_ry"] is None:
        r.append("no '!    total energy' line: the run produced no usable energy at all")
    if rec["fmax_free_ry_au"] is not None and rec["fmax_free_ry_au"] > FMAX_AUDIT_RY_AU:
        r.append(f"free-atom fmax {rec['fmax_free_ry_au']:.4f} Ry/au "
                 f"({rec['fmax_free_ev_ang']:.3f} eV/A) > {FMAX_AUDIT_RY_AU} Ry/au")

    if rec["n_scf_fail"] or rec["max_steps_reached"] or (
            rec["fmax_free_ry_au"] is not None and rec["fmax_free_ry_au"] > FMAX_AUDIT_RY_AU):
        rec["verdict"] = "POISONED"
    # An energy is the whole point of the file. `n_ionic == 0` alone must NEVER buy a
    # TRUSTWORTHY verdict -- that clause is only meant to admit genuine scf-only runs
    # (the H2/H2O gas references), and a genuine scf-only run always has an energy.
    # A relax killed inside ionic step 1 also has n_ionic == 0, and before this guard
    # it was reported TRUSTWORTHY with a null energy.
    elif not rec["job_done"] or rec["user_stopped"] or rec["energy_ry"] is None:
        rec["verdict"] = "INCOMPLETE"
    elif rec["bfgs_converged"] or rec["n_ionic"] == 0:
        rec["verdict"] = "TRUSTWORTHY"
    else:
        rec["verdict"] = "SUSPECT"
    return rec


def trusted_energy_ev(outfile: str, infile: str | None = None, strict: bool = True):
    """Final total energy in eV, or None if the run does not pass QC.

    The strict replacement for `qe_slab.parse_qe_energy`. With `strict=False` it
    only rejects SCF failures and missing JOB DONE (used for salvage/diagnosis).
    """
    if infile is None:
        cand = outfile[:-4] + ".in" if outfile.endswith(".out") else None
        infile = cand if cand and os.path.exists(cand) else None
    rec = scan(outfile, infile)
    ok = rec["verdict"] == "TRUSTWORTHY" if strict else rec["verdict"] in ("TRUSTWORTHY", "SUSPECT")
    return rec["energy_ev"] if ok else None


def _iter_outputs(root: str, all_attempts: bool):
    pat = "**/*.out*" if all_attempts else "**/*.out"
    for p in sorted(glob.glob(os.path.join(root, pat), recursive=True)):
        if os.path.isfile(p):
            yield p


def cmd_audit(args):
    rows = []
    for out in _iter_outputs(args.root, args.all_attempts):
        base = out.split(".out")[0]
        infile = base + ".in" if os.path.exists(base + ".in") else None
        rec = scan(out, infile)
        rec["primary"] = out.endswith(".out")
        rows.append(rec)

    order = {"POISONED": 0, "INCOMPLETE": 1, "SUSPECT": 2, "TRUSTWORTHY": 3, "MISSING": 4}
    rows.sort(key=lambda r: (order[r["verdict"]], r["path"]))

    w = max((len(os.path.relpath(r["path"], args.root)) for r in rows), default=10)
    print(f"{'file'.ljust(w)}  {'verdict':<12} {'ionic':>5} {'scf_fail':>8} "
          f"{'fmax_free(eV/A)':>15}  {'E (eV)':>14}")
    for r in rows:
        f = "" if r["fmax_free_ev_ang"] is None else f"{r['fmax_free_ev_ang']:.4f}"
        e = "" if r["energy_ev"] is None else f"{r['energy_ev']:.4f}"
        print(f"{os.path.relpath(r['path'], args.root).ljust(w)}  {r['verdict']:<12} "
              f"{r['n_ionic']:>5} {r['n_scf_fail']:>8} {f:>15}  {e:>14}")

    tally: dict[str, int] = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(tally.items())))

    bad = [r for r in rows if r["primary"] and r["verdict"] == "POISONED"]
    if bad:
        print(f"\n{len(bad)} PRIMARY output(s) poisoned:")
        for r in bad:
            print(f"  {os.path.relpath(r['path'], args.root)}: {'; '.join(r['reasons'])}")

    if args.json:
        json.dump(rows, open(args.json, "w"), indent=1)
        print(f"\n-> {args.json}")
    return 1 if bad else 0


def cmd_check(args):
    base = args.outfile.split(".out")[0]
    infile = args.infile or (base + ".in" if os.path.exists(base + ".in") else None)
    print(json.dumps(scan(args.outfile, infile), indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="QC every pw.x output under a tree")
    a.add_argument("root")
    a.add_argument("--all-attempts", action="store_true",
                   help="also scan .out.attemptN / .out.restart files")
    a.add_argument("--json", help="write the full records here")
    a.set_defaults(func=cmd_audit)
    c = sub.add_parser("check", help="QC a single output file")
    c.add_argument("outfile")
    c.add_argument("--infile", help="matching .in (for the if_pos mask)")
    c.set_defaults(func=cmd_check)
    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
