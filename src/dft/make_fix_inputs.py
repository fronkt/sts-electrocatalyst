"""Build QE restart inputs for the three structures the R3 evaluation exposed.

All three passed `qe_qc` (SCF converged, forces small, energy present) and are still
wrong. See docs/33 and `adsorbate_qc.py`.

  Cr_slab/s0_O    force-converged at Cr-O = 2.016 A while Mn/Fe/Ru/Ir all reach
                  1.67-1.77 A. MACE-MPA-0 finds a structure 1.06 eV lower at 1.609 A.
                  -> restart from the MACE geometry. If DFT climbs back to 2.016 the
                     original minimum is confirmed and MACE is wrong; if it stays
                     short and lower, the original eta(Cr) = 1.726 V is superseded.
                     Either outcome settles it.

  Mn_slab/s0_OOH  "converged" in 2 ionic steps with the *OOH 3.83 A from the metal and
  Fe_slab/s0_OOH  13 steps at 3.95 A -- floating in vacuum, nearest anything 3.4-4.5 A.
                  A desorbed molecule has no forces, so BFGS stops immediately. MACE
                  does not rescue them either (3.83->3.42, 3.95->3.56): the starting
                  point sits in a flat basin with nothing pulling the adsorbate in.
                  -> rebuild from a genuinely bound geometry.

Construction for the *OOH pair: the slab comes from that metal's own relaxed `s0_OH`
frame (bound at 1.85 A, 46/51 ionic steps, so the surface is properly relaxed with an
adsorbate at the same cus site), and the adsorbate is transplanted from Cr's relaxed
`s0_OOH` as a rigid offset from the cus metal atom. Cr is the right donor: same 3d
family, same builder, bound at 2.076 A over 82 ionic steps. Offsets are taken relative
to the cus atom rather than in fractional coordinates because the three lattice
constants differ.

Only ATOMIC_POSITIONS changes. Every other namelist -- cutoffs, U, smearing, k-points,
constraints, pseudopotentials -- is copied byte-for-byte from the original input, so
the new energy stays comparable to the rest of that metal's CHE chain.

    PYTHONPATH=src python src/dft/make_fix_inputs.py --outdir runs
"""
from __future__ import annotations

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

N_SLAB = 18
CUS_INDEX = 4          # the cus metal every adsorbate binds to, verified in all frames


def load_frames(path="data/qe_frames.extxyz"):
    from ase.io import read
    fr = {}
    for at in read(path, ":"):
        fr.setdefault(at.info["source"], []).append((int(at.info["step"]), at))
    return {k: sorted(v)[-1][1] for k, v in fr.items()}


def replace_positions(infile: str, positions, outfile: str) -> None:
    """Rewrite ATOMIC_POSITIONS with new coordinates, preserving species and if_pos."""
    lines = open(infile, errors="ignore").read().splitlines()
    i = next(i for i, ln in enumerate(lines) if ln.strip().upper().startswith("ATOMIC_POSITIONS"))
    out, k = lines[: i + 1], 0
    for ln in lines[i + 1:]:
        s = ln.split()
        is_atom = len(s) >= 4 and _isfloat(s[1]) and _isfloat(s[2]) and _isfloat(s[3])
        if is_atom and k < len(positions):
            x, y, z = positions[k]
            flags = " ".join(s[4:7]) if len(s) >= 7 else ""
            out.append(f"  {s[0]:<3}{x:14.8f}{y:14.8f}{z:14.8f}" + (f"  {flags}" if flags else ""))
            k += 1
        else:
            out.append(ln)
    assert k == len(positions), f"{infile}: wrote {k} of {len(positions)} atoms"
    # LF endings: a CRLF namelist corrupts QE's Fortran reader on Linux (docs/30)
    with open(outfile, "w", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")


def _isfloat(t):
    try:
        float(t)
        return True
    except ValueError:
        return False


def species_of(infile: str):
    lines = open(infile, errors="ignore").read().splitlines()
    i = next(i for i, ln in enumerate(lines) if ln.strip().upper().startswith("ATOMIC_POSITIONS"))
    out = []
    for ln in lines[i + 1:]:
        s = ln.split()
        if len(s) >= 4 and _isfloat(s[1]):
            out.append(s[0])
        elif out:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="data/qe_frames.extxyz")
    ap.add_argument("--outdir", default="runs")
    ap.add_argument("--mace-geom", default="data/fix_geoms/Cr_slab_s0_O.mace.xyz")
    ap.add_argument("--verify", action="store_true", help="MACE-relax each new geometry")
    a = ap.parse_args()

    from ase.io import read
    fr = load_frames(a.frames)
    made = []

    # ---- 1. Cr/s0_O from the MACE short-bond geometry -----------------------
    mace = read(a.mace_geom)
    src_in = os.path.join(a.outdir, "Cr_slab", "s0_O.in")
    dst = os.path.join(a.outdir, "Cr_slab", "s0_O.in.shortbond")
    assert [x.symbol for x in mace] == species_of(src_in), "species order mismatch"
    replace_positions(src_in, mace.positions, dst)
    d = min(math.dist(mace[18].position, x.position) for x in mace[:18] if x.symbol == "Cr")
    made.append(("Cr_slab/s0_O", dst, f"Cr-O {d:.3f} A (was 2.016)"))

    # ---- 2/3. Mn, Fe /s0_OOH: relaxed s0_OH slab + Cr's bound OOH -----------
    donor = fr["Cr_slab/s0_OOH"]
    cus_d = donor[CUS_INDEX].position
    offsets = [donor[N_SLAB + k].position - cus_d for k in range(3)]
    for m, d_ in (("Mn", "Mn_slab"), ("Fe", "Fe_slab")):
        base = fr[f"{d_}/s0_OH"]                      # properly relaxed slab, same site
        pos = [p.copy() for p in base.positions[:N_SLAB]]
        cus = base[CUS_INDEX].position
        pos += [cus + o for o in offsets]
        src_in = os.path.join(a.outdir, d_, "s0_OOH.in")
        dst = os.path.join(a.outdir, d_, "s0_OOH.in.bound")
        assert len(pos) == len(species_of(src_in)), "atom count mismatch"
        replace_positions(src_in, pos, dst)
        dd = min(math.dist(pos[N_SLAB], p) for p, s in zip(pos[:N_SLAB], species_of(src_in)) if s == m)
        made.append((f"{d_}/s0_OOH", dst, f"{m}-O {dd:.3f} A (was 3.83/3.95)"))

    print(f"{'target':<18}{'new input':<40}{'geometry'}")
    for t, p, g in made:
        print(f"{t:<18}{p:<40}{g}")

    if a.verify:
        from ase.constraints import FixAtoms
        from ase.optimize import BFGS
        from mace.calculators import mace_mp
        from dft.adsorbate_qc import check_structure
        calc = mace_mp(model="medium-mpa-0", device="cpu", default_dtype="float64")
        print("\nMACE sanity check -- does the new geometry STAY bound?")
        for t, p, _ in made:
            metal = t.split("_")[0]
            atoms = read(p, format="espresso-in")
            free = [1] * len(atoms)
            atoms.set_constraint(FixAtoms(indices=[i for i, c in enumerate(atoms.constraints)]
                                          if atoms.constraints else []))
            atoms.calc = calc
            e0 = atoms.get_potential_energy()
            BFGS(atoms, logfile=None).run(fmax=0.05, steps=300)
            r = check_structure(atoms, metal)
            print(f"  {t:<18} M-O {r['m_o_min']:.3f} A  dE {atoms.get_potential_energy()-e0:+.3f} eV"
                  f"  {'BOUND' if r['ok'] else '*** STILL UNBOUND ***'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
