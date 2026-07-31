#!/usr/bin/env python3
"""Extract MLIP training frames from archived Quantum ESPRESSO `relax` outputs.

docs/28 s5 calls the archived endmember campaign "an in-domain training set already
on disk". It is -- but not via ASE: `ase.io.read(..., format='espresso-out')` (3.28)
raises `AssertionError: len(eigenvalues[0]) == len(ibzkpts)` on every one of our
spin-polarised slab runs, because pw.x at default verbosity prints the k-point list
but not the per-k eigenvalues, so ASE collects 15 k-points and 0 eigenvalue rows.
Gas-phase outputs parse fine, which is why the failure was not obvious.

This module parses the outputs directly. Per ionic step it recovers
(positions, cell, symbols, total energy, forces) and tags the frame:

  * energies come only from `!  total energy` lines, which pw.x prints **only** for
    a converged SCF -- so a failed SCF contributes no frame at all rather than a
    silently wrong one;
  * geometry for step 0 comes from the matching `.in` (exact, angstrom); step i>0
    comes from the (i-1)-th echoed `ATOMIC_POSITIONS (angstrom)` block;
  * forces are pw.x's **unconstrained** forces. The `if_pos` mask is stored per
    frame so a trainer can either learn the true PES (use all forces, the right
    choice) or mimic the constrained relaxation (mask them).

Unconverged *geometries* are good training data -- an MLIP must learn E(R) away
from minima. Only frames from failed SCF cycles are poison, and those never
appear. This is the opposite of the rule for eta (see `qe_qc.py`), where only
force-converged geometries may be used.

Usage
-----
    PYTHONPATH=src python src/dft/qe_frames.py extract runs -o data/qe_frames.extxyz
    PYTHONPATH=src python src/dft/qe_frames.py extract runs -o out.extxyz --hold-out Ni
    PYTHONPATH=src python src/dft/qe_frames.py validate runs/Cr_slab/s0_OH.out
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

import numpy as np

RY_EV = 13.605693122
RY_AU_TO_EV_ANG = 25.71104309541616

_RE_ETOT = re.compile(r"^!\s+total energy\s+=\s+(-?\d+\.\d+)\s+Ry", re.M)
_RE_FORCE_ATOM = re.compile(
    r"^\s*atom\s+\d+\s+type\s+\d+\s+force\s+=\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)",
    re.M)


def read_input(infile: str):
    """(symbols, positions Angstrom, cell 3x3 Angstrom, free-mask) from a QE input."""
    lines = open(infile, errors="ignore").read().splitlines()
    cell, syms, pos, free = [], [], [], []
    i = 0
    while i < len(lines):
        head = lines[i].strip().upper()
        if head.startswith("CELL_PARAMETERS"):
            for j in range(1, 4):
                cell.append([float(x) for x in lines[i + j].split()[:3]])
            i += 4
            continue
        if head.startswith("ATOMIC_POSITIONS"):
            if "ANGSTROM" not in head:
                raise ValueError(f"{infile}: ATOMIC_POSITIONS not in angstrom ({head})")
            j = i + 1
            while j < len(lines):
                s = lines[j].split()
                if not s or not _isnum(s[1] if len(s) > 1 else ""):
                    break
                syms.append(s[0])
                pos.append([float(x) for x in s[1:4]])
                free.append(any(f != "0" for f in s[4:7]) if len(s) >= 7 else True)
                j += 1
            i = j
            continue
        i += 1
    if not cell:  # gas-phase molecules use ibrav=1 + celldm(1) in bohr
        m = re.search(r"celldm\(1\)\s*=\s*([\d.]+)", "\n".join(lines))
        if m:
            a = float(m.group(1)) * 0.529177210903
            cell = [[a, 0, 0], [0, a, 0], [0, 0, a]]
    return syms, np.array(pos, float), np.array(cell, float), free


def _isnum(t: str) -> bool:
    try:
        float(t)
        return True
    except ValueError:
        return False


def extract(outfile: str, infile: str | None = None) -> list[dict]:
    """All converged-SCF frames in one pw.x relax output."""
    if infile is None:
        base = outfile.split(".out")[0]
        infile = base + ".in"
    if not os.path.exists(infile):
        raise FileNotFoundError(f"need the matching input for geometry/cell: {infile}")
    syms, pos0, cell, free = read_input(infile)
    txt = open(outfile, errors="ignore").read()

    energies = [float(x) * RY_EV for x in _RE_ETOT.findall(txt)]

    forces: list[np.ndarray] = []
    for blk in re.findall(r"Forces acting on atoms[^\n]*\n\n((?:\s*atom.*\n)+)", txt):
        f = [[float(a), float(b), float(c)]
             for a, b, c in _RE_FORCE_ATOM.findall(blk)]
        if f:
            forces.append(np.array(f) * RY_AU_TO_EV_ANG)

    geoms: list[np.ndarray] = []
    for blk in re.findall(r"ATOMIC_POSITIONS \(angstrom\)\n((?:\s*\S+\s+-?\d.*\n)+)", txt):
        g = [[float(x) for x in ln.split()[1:4]] for ln in blk.strip().splitlines()]
        if len(g) == len(syms):
            geoms.append(np.array(g))

    # frame i sits at: input geometry (i=0), else the (i-1)-th echoed block
    frames = []
    n = min(len(energies), len(forces))
    for i in range(n):
        p = pos0 if i == 0 else (geoms[i - 1] if i - 1 < len(geoms) else None)
        if p is None:
            break
        frames.append(dict(symbols=syms, positions=p, cell=cell, energy=energies[i],
                           forces=forces[i], free=free, source=outfile, step=i))
    return frames


def _tag(path: str) -> tuple[str, str]:
    """(system, job) e.g. ('Ni_slab', 's0_OH') from runs/Ni_slab/s0_OH.out.attempt3."""
    d = os.path.basename(os.path.dirname(path))
    return d, os.path.basename(path).split(".out")[0]


def write_extxyz(frames: list[dict], path: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        for fr in frames:
            c = fr["cell"].reshape(-1)
            f.write(f"{len(fr['symbols'])}\n")
            f.write('Lattice="' + " ".join(f"{x:.8f}" for x in c) + '" '
                    'Properties=species:S:1:pos:R:3:forces:R:3:free:I:1 '
                    f'energy={fr["energy"]:.8f} pbc="T T T" '
                    f'source={_tag(fr["source"])[0]}/{_tag(fr["source"])[1]} step={fr["step"]}\n')
            for s, p, fo, fr_ in zip(fr["symbols"], fr["positions"], fr["forces"], fr["free"]):
                f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f} "
                        f"{fo[0]:.8f} {fo[1]:.8f} {fo[2]:.8f} {int(fr_)}\n")


def fit_e0(frames: list[dict], elements: list[str] | None = None) -> dict:
    """Least-squares per-element reference energies E0 (eV/atom) from E = sum_i n_i E0_i.

    docs/28 s5 (arXiv:2606.12704) calls E0 re-estimation the single most important
    fine-tuning knob: QE total energies carry huge pseudopotential-dependent
    offsets (~-1200 eV/atom here) that a foundation model has never seen.
    """
    els = elements or sorted({s for fr in frames for s in fr["symbols"]})
    A = np.array([[fr["symbols"].count(e) for e in els] for fr in frames], float)
    b = np.array([fr["energy"] for fr in frames], float)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    resid = b - A @ sol
    return dict(elements=els, E0_eV=dict(zip(els, sol.round(6))),
                residual_rms_eV=float(np.sqrt((resid ** 2).mean())),
                residual_rms_eV_per_atom=float(np.sqrt(
                    ((resid / A.sum(1)) ** 2).mean())), n_frames=len(frames))


def cmd_extract(args):
    pat = "**/*.out*" if args.all_attempts else "**/*.out"
    paths = [p for p in sorted(glob.glob(os.path.join(args.root, pat), recursive=True))
             if os.path.isfile(p)]
    all_frames, per_source, skipped = [], {}, []
    for p in paths:
        sysname, job = _tag(p)
        if args.hold_out and sysname.split("_")[0] in args.hold_out:
            skipped.append((p, "held out"))
            continue
        if args.skip_gas and job in ("H2", "H2O"):
            skipped.append((p, "gas"))
            continue
        try:
            fr = extract(p)
        except Exception as e:
            skipped.append((p, f"{type(e).__name__}: {e}"))
            continue
        if not fr:
            skipped.append((p, "no frames"))
            continue
        all_frames.extend(fr)
        # key on the FILE, not (system, job): s0_OH.out and s0_OH.out.attempt1 are
        # distinct trajectories and collapsing them silently under-reports the set
        per_source[f"{sysname}/{os.path.basename(p)}"] = len(fr)

    print(f"{len(all_frames)} frames from {len(per_source)} trajectories")
    for k in sorted(per_source):
        print(f"  {k:<28} {per_source[k]:>5}")
    if skipped:
        print(f"\nskipped {len(skipped)}:")
        for p, why in skipped:
            print(f"  {os.path.relpath(p, args.root):<40} {why}")

    if all_frames:
        e0 = fit_e0(all_frames)
        print("\nE0 fit (eV/atom): " + "  ".join(f"{k}={v:.4f}" for k, v in e0["E0_eV"].items()))
        print(f"residual RMS {e0['residual_rms_eV']:.4f} eV "
              f"({e0['residual_rms_eV_per_atom']:.4f} eV/atom)")
        write_extxyz(all_frames, args.out)
        json.dump(dict(n_frames=len(all_frames), per_source=per_source, e0=e0,
                       held_out=args.hold_out or [],
                       skipped=[[p, w] for p, w in skipped]),
                  open(os.path.splitext(args.out)[0] + ".meta.json", "w"), indent=2)
        print(f"-> {args.out}")
        print(f"-> {os.path.splitext(args.out)[0]}.meta.json")
    return 0


def cmd_validate(args):
    """Self-consistency checks on one trajectory (no external reference needed)."""
    fr = extract(args.outfile)
    print(f"{args.outfile}: {len(fr)} frames, {len(fr[0]['symbols'])} atoms, "
          f"{sum(fr[0]['free'])} free")
    txt = open(args.outfile, errors="ignore").read()
    ne = len(_RE_ETOT.findall(txt))
    ng = len(re.findall(r"ATOMIC_POSITIONS \(angstrom\)", txt))
    nf = len(re.findall(r"Forces acting on atoms", txt))
    print(f"  counts: energies={ne} forces={nf} echoed-geometries={ng} -> frames={len(fr)}")

    # 1. frame 0 must match the input geometry exactly
    syms, pos0, _, _ = read_input(args.outfile.split(".out")[0] + ".in")
    d0 = np.abs(fr[0]["positions"] - pos0).max()
    print(f"  frame 0 vs .in           : max|dr| = {d0:.2e} A  {'OK' if d0 < 1e-8 else 'MISMATCH'}")

    # 2. fixed atoms must never move across the whole trajectory
    free = np.array(fr[0]["free"])
    dfix = max(np.abs(f["positions"][~free] - fr[0]["positions"][~free]).max() for f in fr)
    print(f"  fixed atoms displacement : max|dr| = {dfix:.2e} A  "
          f"{'OK' if dfix < 1e-6 else 'MISMATCH -- frame alignment is off'}")

    # 3. energy must fall along a relaxation (allowing BFGS trial steps to rise)
    E = np.array([f["energy"] for f in fr])
    print(f"  energy   : E0={E[0]:.4f}  Emin={E.min():.4f}  Elast={E[-1]:.4f} eV "
          f"(drop {E[-1] - E[0]:+.4f} eV, {np.sum(np.diff(E) > 0)} uphill steps)")

    # 4. last free-atom force must agree with qe_qc's independent read
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "qe_qc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "qe_qc.py"))
    qc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qc)
    rec = qc.scan(args.outfile, args.outfile.split(".out")[0] + ".in")
    mine = np.linalg.norm(fr[-1]["forces"][free], axis=1).max()
    theirs = rec["fmax_free_ev_ang"]
    print(f"  fmax(free), this parser = {mine:.4f} eV/A ; qe_qc = {theirs:.4f} eV/A  "
          f"{'OK' if abs(mine - theirs) < 1e-6 else 'MISMATCH'}")
    print(f"  qe_qc verdict            : {rec['verdict']}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract", help="write an extxyz training set")
    e.add_argument("root")
    e.add_argument("-o", "--out", required=True)
    e.add_argument("--all-attempts", action="store_true",
                   help="include .out.attemptN / .out.restart (more, more correlated, data)")
    e.add_argument("--hold-out", nargs="*", default=[],
                   help="element prefixes to exclude, e.g. --hold-out Ni (for LOMO CV)")
    e.add_argument("--skip-gas", action="store_true", help="drop H2/H2O reference runs")
    e.set_defaults(func=cmd_extract)
    v = sub.add_parser("validate", help="self-consistency checks on one trajectory")
    v.add_argument("outfile")
    v.set_defaults(func=cmd_validate)
    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
