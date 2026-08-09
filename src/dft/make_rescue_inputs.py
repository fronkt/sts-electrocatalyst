"""Build the five QE inputs that take the tier from n = 5 to n = 7.

Targets (docs/34 §4b):

    Ni_slab/s0_O     POISONED  -- SCF died at ionic step 17, free-atom fmax 0.363 eV/A
    Ni_slab/s0_OH    POISONED  -- SCF died at ionic step 36, fmax 0.673 eV/A
    Ni_slab/s0_OOH   desorbed  -- TRUSTWORTHY but the *OOH sits 3.080 A off the surface
    Co_slab/s0_O     missing   -- three attempts, never converged
    Co_slab/s0_OOH   missing   -- same

Two independent things went wrong on these metals, and this module fixes both.

1. Geometry: the builder places every adsorbate 3.07-3.13 A out
--------------------------------------------------------------
From there DFT trapped Cr's `*O` at 2.016 A and left Mn's, Fe's and now Ni's `*OOH`
desorbed. MACE says Co's `*OOH` would go the same way -- from the builder it relaxes to
2.983 A, from a pulled-in start to 2.105 A at **0.427 eV lower**. So every input here
starts from the MLIP minimum (`data/rescue_geoms/`), which is exactly what rescued Cr
(restart at 1.609 A -> converged 1.396 eV below the trapped original). DFT still finds
its own minimum and computes its own energy; only the basin is inherited.

2. SCF: these two metals plateau above `conv_thr`
-------------------------------------------------
Ni `s0_O` sat flat at 2.1e-4 Ry against `conv_thr = 1e-6` for four iterations at ~150 s
each; Co never converged across three attempts. Both are the classic narrow-d-band-at-E_F
problem, and both already run `local-TF` mixing at beta 0.3, so simply retrying is not a
plan.

The fix is a two-stage protocol in the *smearing*, not the mixing:

    stage A   `scf`  at degauss = 0.03 Ry, conv_thr = 1e-5, beta 0.2, ndim 12
              -- a broader smearing washes out the near-E_F structure that stalls the
                 cycle. Cheap, and its only product is a converged charge density.
    stage B   `relax` at degauss = 0.01 Ry, conv_thr = 1e-6, `startingpot = 'file'`
              -- picks up stage A's density from the same outdir/prefix and refines to
                 production settings.

**Stage B must be at degauss = 0.01**, and that is not a stylistic choice: E_adslab and
E_slab both enter dG, and Ni's and Co's `slab.out` were computed at 0.01. Reporting an
adslab energy at a different smearing would put a smearing inconsistency straight into
the CHE chain. Stage A never contributes an energy to anything.

Everything else -- cutoffs, U, k-points, pseudopotentials, `if_pos` -- is copied
byte-for-byte from the original input, so the new energies stay comparable to the rest of
each metal's chain and to the other six metals.

    PYTHONPATH=src python src/dft/make_rescue_inputs.py --geomdir data/rescue_geoms
"""
from __future__ import annotations

import argparse
import math
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

N_SLAB = 18

#: (dir, state, metal). Ordered so the eta-critical three come first -- if the box
#: misbehaves, dG_O and dG_OH are what the gate needs (both metals are pls = 2).
TARGETS = [
    ("Ni_slab", "s0_O", "Ni"),
    ("Ni_slab", "s0_OH", "Ni"),
    ("Co_slab", "s0_O", "Co"),
    ("Ni_slab", "s0_OOH", "Ni"),
    ("Co_slab", "s0_OOH", "Co"),
]

STAGE_A = dict(calculation="'scf'", degauss="0.03", conv_thr="1.0d-5",
               mixing_beta="0.2", mixing_ndim="12", electron_maxstep="300")
STAGE_B = dict(calculation="'relax'", degauss="0.01", conv_thr="1.0d-6",
               mixing_beta="0.2", mixing_ndim="12", electron_maxstep="300",
               startingpot="'file'")


def _isfloat(t):
    try:
        float(t)
        return True
    except ValueError:
        return False


def read_input(path: str) -> list[str]:
    return open(path, errors="ignore").read().splitlines()


def set_key(lines: list[str], namelist: str, key: str, value: str) -> list[str]:
    """Set `key = value` inside `namelist`, adding it if absent. Order-preserving."""
    out, in_nl, done = [], False, False
    pat = re.compile(rf"^\s*{re.escape(key)}\s*=", re.I)
    for ln in lines:
        s = ln.strip()
        if s.upper().startswith("&" + namelist.upper()):
            in_nl = True
            out.append(ln)
            continue
        if in_nl and s == "/":
            if not done:
                out.append(f"  {key} = {value}")
            in_nl, done = False, False
            out.append(ln)
            continue
        if in_nl and pat.match(ln):
            out.append(f"  {key} = {value}")
            done = True
            continue
        out.append(ln)
    return out


def drop_key(lines: list[str], namelist: str, key: str) -> list[str]:
    out, in_nl = [], False
    pat = re.compile(rf"^\s*{re.escape(key)}\s*=", re.I)
    for ln in lines:
        s = ln.strip()
        if s.upper().startswith("&" + namelist.upper()):
            in_nl = True
        elif in_nl and s == "/":
            in_nl = False
        elif in_nl and pat.match(ln):
            continue
        out.append(ln)
    return out


def replace_positions(lines: list[str], positions) -> list[str]:
    """Rewrite ATOMIC_POSITIONS, preserving species labels and if_pos flags."""
    i = next(i for i, ln in enumerate(lines)
             if ln.strip().upper().startswith("ATOMIC_POSITIONS"))
    out, k = lines[: i + 1], 0
    for ln in lines[i + 1:]:
        s = ln.split()
        is_atom = len(s) >= 4 and all(_isfloat(t) for t in s[1:4])
        if is_atom and k < len(positions):
            x, y, z = positions[k]
            flags = " ".join(s[4:7]) if len(s) >= 7 else ""
            out.append(f"  {s[0]:<3}{x:14.8f}{y:14.8f}{z:14.8f}" + (f"  {flags}" if flags else ""))
            k += 1
        else:
            out.append(ln)
    assert k == len(positions), f"wrote {k} of {len(positions)} atoms"
    return out


def species_of(lines: list[str]) -> list[str]:
    i = next(i for i, ln in enumerate(lines)
             if ln.strip().upper().startswith("ATOMIC_POSITIONS"))
    out = []
    for ln in lines[i + 1:]:
        s = ln.split()
        if len(s) >= 4 and all(_isfloat(t) for t in s[1:4]):
            out.append(s[0])
        elif out:
            break
    return out


def write_lf(path: str, lines: list[str]) -> None:
    # LF only: a CRLF namelist corrupts QE's Fortran reader on Linux (docs/30)
    with open(path, "w", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


def build(dirname: str, state: str, metal: str, geomdir: str, outdir: str):
    src = os.path.join(outdir, dirname, state + ".in")
    base = read_input(src)
    from ase.io import read
    g = os.path.join(geomdir, f"{dirname}_{state}.mace.xyz")
    atoms = read(g)
    assert [a.symbol for a in atoms] == species_of(base), f"{g}: species order mismatch"

    base = replace_positions(base, atoms.positions)
    # stage A is an scf: nstep/ion_dynamics are meaningless and forc_conv_thr misleading
    a = list(base)
    for k, v in STAGE_A.items():
        nl = "CONTROL" if k == "calculation" else ("SYSTEM" if k == "degauss" else "ELECTRONS")
        a = set_key(a, nl, k, v)
    b = list(base)
    for k, v in STAGE_B.items():
        nl = ("CONTROL" if k == "calculation" else
              "SYSTEM" if k == "degauss" else "ELECTRONS")
        b = set_key(b, nl, k, v)

    pa = os.path.join(outdir, dirname, state + ".in.stageA")
    pb = os.path.join(outdir, dirname, state + ".in.stageB")
    write_lf(pa, a)
    write_lf(pb, b)
    d = (min(math.dist(atoms[N_SLAB].position, p.position)
             for p in atoms[:N_SLAB] if p.symbol == metal) if len(atoms) > N_SLAB else None)
    return pa, pb, d


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--geomdir", default="data/rescue_geoms")
    ap.add_argument("--outdir", default="runs")
    a = ap.parse_args()

    from dft.adsorbate_qc import check_structure
    from ase.io import read
    print(f"{'target':<20}{'M-O (A)':>10}  {'tier':<9} stage inputs")
    for dirname, state, metal in TARGETS:
        pa, pb, d = build(dirname, state, metal, a.geomdir, a.outdir)
        atoms = read(os.path.join(a.geomdir, f"{dirname}_{state}.mace.xyz"))
        r = check_structure(atoms, metal)
        assert r["tier"] != "desorbed", f"{dirname}/{state}: starting geometry is DESORBED"
        print(f"{dirname+'/'+state:<20}{d:>10.3f}  {r['tier']:<9} {os.path.basename(pa)}, {os.path.basename(pb)}")
    print(f"\n{len(TARGETS)} jobs. Stage A: scf, degauss 0.03, conv_thr 1e-5 (density only).")
    print("Stage B: relax, degauss 0.01, conv_thr 1e-6, startingpot='file' -- production.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
