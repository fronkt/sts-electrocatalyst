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
TiO2 is the exception on both counts -- d0 and closed-shell, so it is emitted at
nspin = 1, and it carries no MP U. It exists here as the hp.x validation target
(see the RUTILE comment and src/dft/build_hp_validation.py).

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
#
# TiO2 is here for ONE reason: it is the hp.x validation target (tasks/plan-maximal-rigor
# block 1B). It is the right FIRST target precisely because it is the boring end of this
# family -- d0 Ti(IV) against closed-shell O(2-), so it is nonmagnetic and closed-shell,
# `mag = 0.0` selects `nspin = 1`, and there is no magnetic-solution multiplicity for the
# linear response to land in. Every other entry in this dict carries the failure mode
# docs/41 s6d measured (5 of 18 audited states multistable, drifts 59-405 meV); on TiO2 a
# bad hp.x number can only be a bad hp.x number. It is also the only rutile in the table
# with a published linear-response U to compare against at all.
#
# It is NOT the only 1B target, and treating it as one was the most serious finding of the
# 2026-08-09 review (finding [15]). TiO2 differs from production in six co-varying ways at
# once -- nspin 1 vs 2, fixed vs smeared occupations, insulator vs metal, empty vs
# partially-filled 3d manifold, no U vs U, no magnetic multiplicity vs plenty -- and hp.x
# takes a different branch on gapped versus smeared systems (it hard-stops on the first).
# A GO measured only here licenses the sentence "hp.x validates on a closed-shell bulk
# insulator", which is not what blocks 2C and 3Y need. So **the CrO2 entry below is also a
# block-1B target**: docs/43 s4-A.3 registers it as the magnetic, metallic arm, built by
# `build_hp_validation.build_cro2` from this same dict at the same cutoffs and k-mesh so
# that those six differences are the only things that move.
#
# Geometry: a = 4.5937 A, c = 2.9587 A, u = 0.30478 -- the accepted room-temperature
# experimental rutile cell of Abrahams & Bernstein, J. Chem. Phys. 55, 3206 (1971)
# (single-crystal X-ray; reproduced within 0.0004 A by the 15 K neutron refinement of
# Burdett et al., J. Am. Chem. Soc. 109, 3639 (1987), a = 4.5941, c = 2.9589, u = 0.30478).
# PROVENANCE NOTE: these numbers were supplied in the block-1B task spec and match the
# values this project has seen quoted for rutile TiO2; NEITHER primary source was opened
# by the code author, so the attribution is UNVERIFIED and must be checked against the
# paper before it appears in the report (tasks/lessons.md, docs/41 provenance rules).
#
# U = 0.0: Materials Project applies no Hubbard U to Ti, so the "MP-calibrated" column is
# genuinely zero here and `make_input` emits no HUBBARD card. hp.x needs a HUBBARD card to
# run at all ("The HP code can be used only on top of DFT+Hubbard"), so
# `build_hp_validation.py` appends its own card with the from-scratch U = 1.d-8.
RUTILE = {
    "TiO2": dict(a=4.5937, c=2.9587, u=0.30478, U=0.0, mass=47.867, mag=0.0),  # real rutile, d0, NM
    "CrO2": dict(a=4.421, c=2.916, u=0.3023, U=3.7,  mass=51.996, mag=0.6),  # real rutile (FM half-metal)
    "MnO2": dict(a=4.404, c=2.876, u=0.3050, U=3.9,  mass=54.938, mag=0.5),  # beta-MnO2 pyrolusite (real rutile)
    "FeO2": dict(a=4.50,  c=3.00,  u=0.300,  U=5.3,  mass=55.845, mag=0.5),  # model rutile
    "CoO2": dict(a=4.45,  c=2.95,  u=0.300,  U=3.32, mass=58.933, mag=0.4),  # model rutile
    "NiO2": dict(a=4.45,  c=2.95,  u=0.300,  U=6.2,  mass=58.693, mag=0.3),  # model rutile
    "CuO2": dict(a=4.50,  c=3.00,  u=0.300,  U=0.0,  mass=63.546, mag=0.2),  # model rutile (Cu: no +U)
}
METAL_SYMBOL = {"TiO2": "Ti", "CrO2": "Cr", "MnO2": "Mn", "FeO2": "Fe", "CoO2": "Co",
                "NiO2": "Ni", "CuO2": "Cu"}


def make_input(formula, ecutwfc, ecutrho, kpts, pseudo_dir, m_upf, o_upf,
               prefix=None, outdir="./tmp", conv_thr=1.0e-8, degauss=0.01,
               mixing_beta=0.3, with_u=True, occupations="smearing"):
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
    # `mag = 0.0` means "this oxide has no open shell to polarise" (TiO2, d0). Emitting
    # nspin = 2 with starting_magnetization = 0 on such a system is not merely wasteful:
    # it doubles the cost, and it hands the SCF a second solution branch to get lost in --
    # the exact failure docs/41 s6d spent the campaign's largest drifts (405 meV) chasing.
    # Every other RUTILE entry has mag > 0, so this branch changes nothing for them.
    if p["mag"] > 0.0:
        spin_block = (f"  nspin = 2\n  starting_magnetization(1) = {p['mag']}\n"
                      f"  starting_magnetization(2) = 0.0\n")
    else:
        spin_block = "  nspin = 1\n"
    # hp.x REFUSES a gapped system presented as a metal. Measured on this build,
    # 2026-08-09, bulk rutile TiO2 with the campaign's smearing = 'mv', degauss = 0.01:
    #   "The DOS at the Fermi level is too small: DOS(E_Fermi) = -0.1014E-33 ... the system
    #    has a gap, and hence it should NOT be treated as a metal ... Stopping..."
    # after which hp.x still printed `JOB DONE.` -- the hp.x instance of the campaign's
    # oldest lesson. The total energy is identical either way (-405.93096624 Ry both), so
    # `occupations = 'fixed'` costs nothing and is the only setting hp.x will accept here.
    if occupations == "fixed":
        occ_block = "  occupations = 'fixed'\n"
    elif occupations == "smearing":
        occ_block = (f"  occupations = 'smearing'\n  smearing = 'mv'\n"
                     f"  degauss = {degauss}\n")
    else:
        raise ValueError(f"unsupported occupations {occupations!r}")
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
{occ_block}{spin_block}/
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
    ap.add_argument("--occupations", default="smearing", choices=["smearing", "fixed"],
                    help="'fixed' for gapped systems -- hp.x refuses a gapped system "
                         "presented as a metal (see make_input)")
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()
    txt = make_input(a.formula, a.ecutwfc, a.ecutrho, a.kpts, a.pseudo_dir,
                     a.m_upf, a.o_upf, with_u=not a.no_u, occupations=a.occupations)
    if a.out:
        with open(a.out, "w") as f:
            f.write(txt)
        print(f"wrote {a.out}")
    else:
        print(txt)


if __name__ == "__main__":
    main()
