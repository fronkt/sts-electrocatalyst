#!/usr/bin/env python3
"""Generate a Quantum ESPRESSO pw.x SCF input for a rutile MO2 endmember.

Part of the multi-fidelity DFT calibration tier (docs/22): the ordered rutile-oxide
endmembers anchor the UMA<->DFT parity plot, and the convergence test (ecutwfc/ecutrho/
k-points) is run on one of these before any SQS HEA cell is touched.

Geometry is the experimental rutile structure (space group P4_2/mnm, ibrav=6):
  M at 2a: (0,0,0), (1/2,1/2,1/2)
  O at 4f: +-(u,u,0), +-(1/2+u,1/2-u,1/2)
held FIXED (scf, no relax) so energy differences reflect only basis/k-point
convergence, not structural changes. PBE+U (Dudarev), spin-polarized, SSSP pseudos.

Usage:
  python gen_rutile.py CrO2 --ecutwfc 80 --ecutrho 640 --kpts 6 6 8 \
      --pseudo-dir /path --m-upf cr_pbe_v1.5.uspp.F.UPF --o-upf O.pbe-n-kjpaw_psl.0.1.UPF
"""
import argparse

ANG2BOHR = 1.8897259886

# a (Ang), c/a, internal parameter u, Hubbard U_eff (eV, MP-calibrated), mass, start mag.
# CrO2 and MnO2 are genuine ground-state rutiles (experimental geometry).
# The other 3d MO2 are NON-ground-state model rutiles (same modelling choice UMA used,
# docs/16 s8); a/c/u are reasonable rutile estimates, refine by relaxation in production.
RUTILE = {
    "CrO2": dict(a=4.421, c=2.916, u=0.3023, U=3.7,  mass=51.996, mag=0.6),  # real rutile (FM half-metal)
    "MnO2": dict(a=4.404, c=2.876, u=0.3050, U=3.9,  mass=54.938, mag=0.5),  # beta-MnO2 pyrolusite (real rutile)
    "FeO2": dict(a=4.50,  c=3.00,  u=0.300,  U=5.3,  mass=55.845, mag=0.5),  # model rutile
    "CoO2": dict(a=4.45,  c=2.95,  u=0.300,  U=3.32, mass=58.933, mag=0.4),  # model rutile
    "NiO2": dict(a=4.45,  c=2.95,  u=0.300,  U=6.2,  mass=58.693, mag=0.3),  # model rutile
    "CuO2": dict(a=4.50,  c=3.00,  u=0.300,  U=0.0,  mass=63.546, mag=0.2),  # model rutile (Cu: no +U)
}
METAL_SYMBOL = {"CrO2": "Cr", "MnO2": "Mn", "FeO2": "Fe", "CoO2": "Co", "NiO2": "Ni", "CuO2": "Cu"}


def make_input(formula, ecutwfc, ecutrho, kpts, pseudo_dir, m_upf, o_upf,
               prefix=None, outdir="./tmp", conv_thr=1.0e-8, degauss=0.01,
               mixing_beta=0.3, with_u=True):
    p = RUTILE[formula]
    M = METAL_SYMBOL[formula]
    prefix = prefix or formula.lower()
    u = p["u"]
    celldm1 = p["a"] * ANG2BOHR
    celldm3 = p["c"] / p["a"]
    # QE >= 7.1: DFT+U is set via the HUBBARD card (atomic projectors), not the old
    # lda_plus_u / Hubbard_U(i) namelist keys. Card appended after K_POINTS below.
    hubbard_card = ""
    if with_u and p["U"] > 0:
        hubbard_card = f"HUBBARD (atomic)\nU {M}-3d {p['U']}\n"
    lines = f"""&CONTROL
  calculation = 'scf'
  prefix = '{prefix}'
  outdir = '{outdir}'
  pseudo_dir = '{pseudo_dir}'
  verbosity = 'high'
  tprnfor = .true.
  tstress = .false.
/
&SYSTEM
  ibrav = 6
  celldm(1) = {celldm1:.5f}
  celldm(3) = {celldm3:.5f}
  nat = 6
  ntyp = 2
  ecutwfc = {ecutwfc}
  ecutrho = {ecutrho}
  occupations = 'smearing'
  smearing = 'mv'
  degauss = {degauss}
  nspin = 2
  starting_magnetization(1) = {p['mag']}
  starting_magnetization(2) = 0.0
/
&ELECTRONS
  conv_thr = {conv_thr}
  mixing_beta = {mixing_beta}
  electron_maxstep = 200
/
ATOMIC_SPECIES
  {M}  {p['mass']:.3f}  {m_upf}
  O   15.999  {o_upf}
ATOMIC_POSITIONS (crystal)
  {M}  0.000000  0.000000  0.000000
  {M}  0.500000  0.500000  0.500000
  O   {u:.6f}  {u:.6f}  0.000000
  O   {(-u) % 1.0:.6f}  {(-u) % 1.0:.6f}  0.000000
  O   {(0.5 + u):.6f}  {(0.5 - u):.6f}  0.500000
  O   {(0.5 - u):.6f}  {(0.5 + u):.6f}  0.500000
K_POINTS (automatic)
  {kpts[0]} {kpts[1]} {kpts[2]} 0 0 0
{hubbard_card}"""
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("formula", choices=sorted(RUTILE))
    ap.add_argument("--ecutwfc", type=float, default=80.0)
    ap.add_argument("--ecutrho", type=float, default=640.0)
    ap.add_argument("--kpts", type=int, nargs=3, default=[6, 6, 8])
    ap.add_argument("--pseudo-dir", default="../pseudo")
    ap.add_argument("--m-upf", required=True, help="metal pseudopotential UPF filename")
    ap.add_argument("--o-upf", required=True, help="oxygen pseudopotential UPF filename")
    ap.add_argument("--no-u", action="store_true", help="disable +U (plain PBE)")
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()
    txt = make_input(a.formula, a.ecutwfc, a.ecutrho, a.kpts, a.pseudo_dir,
                     a.m_upf, a.o_upf, with_u=not a.no_u)
    if a.out:
        with open(a.out, "w") as f:
            f.write(txt)
        print(f"wrote {a.out}")
    else:
        print(txt)


if __name__ == "__main__":
    main()
