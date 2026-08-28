#!/usr/bin/env python3
"""Rutile(110) slab + adsorbate DFT for the UMA<->DFT parity (docs/22, docs/23).

This is the heavy tier of the multi-fidelity funnel. It reuses the EXACT UMA slab
geometry and CHE referencing so the only thing that differs between UMA and DFT is
the energy method itself -> a fair parity:

  * slab + cus sites + adsorbate placement : hea_oer.surfaces_rutile (same as UMA)
  * CHE free energies / overpotential       : hea_oer.referencing.delta_G + descriptors.oer_overpotential
  * relaxer                                 : Quantum ESPRESSO pw.x (here) vs UMA MLIP (there)

Two subcommands:
  build : write QE 'relax' inputs for the clean slab, the *OH/*O/*OOH adslabs on
          each cus site, and the gas-phase H2O/H2 references, plus a manifest.
  eta   : parse the relaxed pw.x outputs, apply CHE referencing, and report the
          per-site OER overpotential distribution (eta_min/mean/std/max), matching
          the UMA backend's site_records so the two are directly comparable.

Run with PYTHONPATH=src (so `import hea_oer` resolves), e.g.
  PYTHONPATH=src python src/dft/qe_slab.py build Cr --outdir runs/CrO2_slab
Production cutoffs (locked by docs/23): ecutwfc 80 Ry, ecutrho 640 Ry. No dipole
correction -- deliberately matching the UMA setup (parity is method-vs-method).
"""
from __future__ import annotations

import argparse
import json
import os
import re

RY_EV = 13.605693122

# element -> SSSP-Efficiency pseudo (apt quantum-espresso-data-sssp, /usr/share/espresso/pseudo),
# MP-calibrated Hubbard U_eff (eV), starting magnetization, atomic mass.
ELEMENTS = {
    "O":  dict(pseudo="O.pbe-n-kjpaw_psl.0.1.UPF",          U=0.0,  mag=0.0, mass=15.999),
    "H":  dict(pseudo="H.pbe-rrkjus_psl.1.0.0.UPF",         U=0.0,  mag=0.0, mass=1.008),   # verify name on box
    # TiO2: d0 closed-shell control metal; NO U by the same MP convention that
    # sets Ru/Ir to zero (gen_rutile.py), mag=0 -> nonmagnetic; pseudo is the one
    # the S0 hp_tio2/ecut80 work verified (runs/hp_tio2/scf__atomic.in).
    "Ti": dict(pseudo="ti_pbe_v1.4.uspp.F.UPF",             U=0.0,  mag=0.0, mass=47.867),
    "Cr": dict(pseudo="cr_pbe_v1.5.uspp.F.UPF",             U=3.7,  mag=0.6, mass=51.996),
    "Mn": dict(pseudo="mn_pbe_v1.5.uspp.F.UPF",             U=3.9,  mag=0.5, mass=54.938),
    "Fe": dict(pseudo="Fe.pbe-spn-kjpaw_psl.0.2.1.UPF",     U=5.3,  mag=0.5, mass=55.845),
    "Co": dict(pseudo="Co_pbe_v1.2.uspp.F.UPF",             U=3.32, mag=0.4, mass=58.933),
    "Ni": dict(pseudo="ni_pbe_v1.4.uspp.F.UPF",             U=6.2,  mag=0.3, mass=58.693),
    "Cu": dict(pseudo="Cu.paw.z_11.ld1.psl.v1.0.0-low.upf", U=0.0,  mag=0.2, mass=63.546),
    # Benchmark-electrode anchors (docs/29 s2). No +U: RuO2/IrO2 are 4d/5d rutile
    # metals, itinerant and non-magnetic, and the rutile-OER literature we compare
    # against (Rossmeisl 2007, Man 2011) runs them at plain GGA.
    "Ru": dict(pseudo="Ru_ONCV_PBE-1.0.oncvpsp.upf",        U=0.0,  mag=0.0, mass=101.070),
    "Ir": dict(pseudo="Ir_pbe_v1.2.uspp.F.UPF",             U=0.0,  mag=0.0, mass=192.217),
}
ADSORBATES = ("OH", "O", "OOH")


def parse_formula(s: str):
    """'Cr' or 'Fe32Ni17Co34Mn18' -> hea_oer Composition (at.% or counts, normalized)."""
    from hea_oer.composition import Composition

    pairs = re.findall(r"([A-Z][a-z]?)(\d*\.?\d*)", s)
    d = {el: (float(n) if n else 1.0) for el, n in pairs if el}
    if not d:
        raise ValueError(f"could not parse composition {s!r}")
    return Composition.from_dict(d)


def kgrid_from_cell(cell, target=25.0):
    """Monkhorst-Pack mesh ~target Ang^-1 density in-plane, 1 along the vacuum (c) axis."""
    import numpy as np

    lengths = np.linalg.norm(np.asarray(cell), axis=1)
    n = [max(1, int(round(target / L))) for L in lengths]
    n[2] = 1  # pymatgen slabs: vacuum along the 3rd axis
    return tuple(n)


def _species_block(symbols):
    """Ordered unique species present + 1-based index map."""
    order = sorted(set(symbols), key=lambda s: (s == "O", s))  # metals first, O last
    return order, {s: i + 1 for i, s in enumerate(order)}


def _fixed_mask(atoms):
    from ase.constraints import FixAtoms

    fixed = set()
    for c in atoms.constraints:
        if isinstance(c, FixAtoms):
            fixed.update(int(i) for i in c.get_indices())
    return fixed


def write_slab_input(atoms, prefix, pseudo_dir, ecutwfc, ecutrho, outdir="./tmp",
                     *, nosym):
    """QE 'relax' input for a rutile(110) slab (ibrav=0, bottom fixed, +U if magnetic).

    `nspin` is emitted as 2 only when some species carries a non-zero starting
    magnetization. RuO2/IrO2 are non-magnetic 4d/5d rutile metals with mag = 0, and
    `nspin=2` with every `starting_magnetization` at zero is a fixed point of the
    SCF -- it reproduces the `nspin=1` answer at exactly twice the cost. That one is
    exact and stands.

    `nosym` is REQUIRED and has no default. It used to default to True here, and the
    adsorbate call site used to pass False, on the reasoning recorded in this docstring
    until 2026-08-09:

        "An adsorbate lowers the symmetry by itself, and runs/Cr_slab/s0_OH.in (no
         nosym) ran to JOB DONE at 15 k-points while runs/Mn_slab/s0_O.in (nosym) paid
         for 36 -- same physics, 2.4x the bill."

    **Both halves of that are false, and the second one is the campaign's central
    finding (docs/41 s6g).**

    The adsorbate does NOT lower the symmetry by itself. `hea_oer.surfaces._adsorbate`
    defines every OER adsorbate with y == 0 and places it at (x_cus, y_cus), i.e.
    exactly on the rutile(110) mirror plane, which is an exact symmetry of the slab.
    The adsorbate sits *in* the mirror rather than breaking it.

    So it is not the same physics. With the mirror alive, pw.x symmetrises F_y onto it:
    max|F_y| on the adsorbate is **exactly 0.0000000000 Ry/au** over every ionic step,
    and the relaxation is a constrained optimisation in a 2-D (x, z) subspace. The
    2.4x that was saved bought a different calculation, not a cheaper one -- worth
    -291 meV on Ir's *OOH, which moves eta(Ir) from 0.781 to 0.490 V.

    The audit that settled it: of 20 production adsorbate relaxations, 9 are LOCKED
    (this path) and their confinement class is predicted 20-for-20 by whether this one
    flag was set. Cr, Ir and Ru went through here; Mn, Fe, Co, Ni and Cu predate it and
    kept nosym. The tier is therefore two protocols, not one.

    Hence: no default. A caller must state which it wants, in writing, at the call site.
    And note that `nosym = True` alone is NOT a fix -- on an exactly symmetric input it
    removes the constraint without supplying any reason to move, and 6 of the 11 states
    that had it never left the plane. An off-plane search needs a *physical
    displacement* as well; see `orient_starts.py`.

    (The original reason nosym is needed on the CLEAN slab is unaffected and still
    holds: freezing the bottom half breaks the top-bottom mirror, so pw.x aborts in
    `checkallsym` without it -- docs/23 s5.)
    """
    syms = atoms.get_chemical_symbols()
    order, idx = _species_block(syms)
    fixed = _fixed_mask(atoms)
    cell = atoms.cell
    nat, ntyp = len(atoms), len(order)

    spin_polarised = any(ELEMENTS[s]["mag"] for s in order)
    if spin_polarised:
        mag = "  nspin = 2\n" + "".join(
            f"  starting_magnetization({idx[s]}) = {ELEMENTS[s]['mag']}\n" for s in order)
    else:
        mag = ""
    sym = "  nosym = .true.\n  noinv = .true.\n" if nosym else ""
    head = f"""&CONTROL
  calculation = 'relax'
  prefix = '{prefix}'
  outdir = '{outdir}'
  pseudo_dir = '{pseudo_dir}'
  tprnfor = .true.
  forc_conv_thr = 2.0d-3
  nstep = 200
/
&SYSTEM
  ibrav = 0
  nat = {nat}
  ntyp = {ntyp}
  ecutwfc = {ecutwfc}
  ecutrho = {ecutrho}
  occupations = 'smearing'
  smearing = 'mv'
  degauss = 0.01
{sym}{mag}/
&ELECTRONS
  conv_thr = 1.0d-6
  mixing_mode = 'local-TF'
  mixing_beta = 0.3
  electron_maxstep = 200
/
&IONS
  ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
"""
    spec = "".join(f"  {s}  {ELEMENTS[s]['mass']:.3f}  {ELEMENTS[s]['pseudo']}\n" for s in order)
    cellp = "CELL_PARAMETERS angstrom\n" + "".join(
        f"  {cell[i][0]:.8f}  {cell[i][1]:.8f}  {cell[i][2]:.8f}\n" for i in range(3))
    pos = "ATOMIC_POSITIONS angstrom\n"
    for i, (s, p) in enumerate(zip(syms, atoms.positions)):
        flags = "0 0 0" if i in fixed else "1 1 1"
        pos += f"  {s}  {p[0]:.8f}  {p[1]:.8f}  {p[2]:.8f}  {flags}\n"
    k1, k2, k3 = kgrid_from_cell(cell)
    kpts = f"K_POINTS automatic\n  {k1} {k2} {k3} 0 0 0\n"
    hub = "".join(f"U {s}-3d {ELEMENTS[s]['U']}\n"
                  for s in order if s != "O" and ELEMENTS[s]["U"] > 0)
    hubbard = f"HUBBARD (atomic)\n{hub}" if hub else ""
    return head + spec + cellp + pos + kpts + hubbard


def write_molecule_input(name, atoms, pseudo_dir, ecutwfc, ecutrho, outdir="./tmp", box=12.0):
    """QE 'relax' input for a gas molecule in a box (Martyna-Tuckerman, Gamma, nspin=1)."""
    syms = atoms.get_chemical_symbols()
    order, _ = _species_block(syms)
    head = f"""&CONTROL
  calculation = 'relax'
  prefix = '{name}'
  outdir = '{outdir}'
  pseudo_dir = '{pseudo_dir}'
  tprnfor = .true.
  forc_conv_thr = 2.0d-3
  nstep = 100
/
&SYSTEM
  ibrav = 1
  celldm(1) = {box * 1.8897259886:.5f}
  nat = {len(atoms)}
  ntyp = {len(order)}
  ecutwfc = {ecutwfc}
  ecutrho = {ecutrho}
  assume_isolated = 'mt'
  nspin = 1
/
&ELECTRONS
  conv_thr = 1.0d-6
  mixing_beta = 0.5
/
&IONS
  ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
"""
    spec = "".join(f"  {s}  {ELEMENTS[s]['mass']:.3f}  {ELEMENTS[s]['pseudo']}\n" for s in order)
    # center the molecule in the box
    import numpy as np
    p = np.asarray(atoms.positions) - np.asarray(atoms.positions).mean(0) + box / 2.0
    pos = "ATOMIC_POSITIONS angstrom\n" + "".join(
        f"  {s}  {p[i][0]:.6f}  {p[i][1]:.6f}  {p[i][2]:.6f}\n" for i, s in enumerate(syms))
    kpts = "K_POINTS gamma\n"
    return head + spec + pos + kpts


def _gas_molecules():
    from ase import Atoms
    h2o = Atoms("OH2", positions=[(0, 0, 0), (0.758, 0.587, 0), (-0.758, 0.587, 0)])
    h2 = Atoms("H2", positions=[(0, 0, 0), (0, 0, 0.741)])
    return {"H2O": h2o, "H2": h2}


def cmd_build(args):
    from hea_oer.surfaces_rutile import build_rutile110_hea, cus_site_xy, add_oer_adsorbate_at

    os.makedirs(args.outdir, exist_ok=True)
    comp = parse_formula(args.composition)
    slab = build_rutile110_hea(comp, supercell=(args.supercell, args.supercell), seed=args.seed)
    sites = cus_site_xy(slab, n_sites=args.n_sites)
    manifest = {"composition": comp.formula(), "ecutwfc": args.ecutwfc, "ecutrho": args.ecutrho,
                "n_sites": len(sites), "jobs": []}

    def emit(name, text, **meta):
        path = os.path.join(args.outdir, name + ".in")
        # newline="\n" unconditionally: these inputs are written on Windows and read by
        # pw.x on Linux, and a stray \r inside a Fortran namelist is the same trap that
        # .gitattributes already guards for *.sh (tasks/lessons.md).
        with open(path, "w", newline="\n") as f:
            f.write(text)
        manifest["jobs"].append(dict(name=name, **meta))

    emit("slab", write_slab_input(slab, "slab", args.pseudo_dir, args.ecutwfc, args.ecutrho,
                                  nosym=True), kind="slab")
    for si, xy in enumerate(sites):
        for sp in ADSORBATES:
            ads = add_oer_adsorbate_at(slab, sp, xy)
            # nosym=True, reversing the 2026-07-31 cost optimisation that produced the
            # LOCKED half of the tier (docs/41 s6g; the refutation is in
            # write_slab_input's docstring). This alone does not make the search
            # three-dimensional -- see docs/43 s0a -- it only stops pw.x from
            # symmetrising F_y to exactly zero. The physical displacement that makes it
            # a real search is supplied by orient_starts.py / build_cellsym_pilot.py.
            emit(f"s{si}_{sp}", write_slab_input(ads, f"s{si}_{sp}", args.pseudo_dir,
                 args.ecutwfc, args.ecutrho, nosym=True),
                 kind="adslab", site=si, species=sp)
    for name, mol in _gas_molecules().items():
        emit(name, write_molecule_input(name, mol, args.pseudo_dir, args.ecutwfc, args.ecutrho),
             kind="gas")

    with open(os.path.join(args.outdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote {len(manifest['jobs'])} QE inputs + manifest.json to {args.outdir} "
          f"(composition {comp.formula()}, {len(sites)} cus site(s))")


def parse_qe_energy(outfile, strict=True):
    """Final total energy (eV) from a pw.x run that PASSES QC; None otherwise.

    Delegates to `qe_qc.trusted_energy_ev`. The old implementation accepted any
    file containing `JOB DONE`, which is exactly how eleven silently-unconverged
    relaxations reached docs/26 (pw.x prints `JOB DONE` after
    `convergence NOT achieved ... stopping`). `strict=False` restores the loose
    behaviour for diagnosis only -- never for published energies.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "qe_qc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "qe_qc.py"))
    qc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qc)
    return qc.trusted_energy_ev(outfile, strict=strict)


def cmd_eta(args):
    import numpy as np
    from hea_oer.referencing import delta_G
    from hea_oer.descriptors import oer_overpotential

    manifest = json.load(open(os.path.join(args.outdir, "manifest.json")))
    E = {}
    for job in manifest["jobs"]:
        E[job["name"]] = parse_qe_energy(os.path.join(args.outdir, job["name"] + ".out"))
    missing = [n for n, e in E.items() if e is None]
    if missing:
        print(f"WARNING: {len(missing)} job(s) failed QC or are unfinished: {missing}")
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "qe_qc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "qe_qc.py"))
        qc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(qc)
        for n in missing:
            out = os.path.join(args.outdir, n + ".out")
            rec = qc.scan(out, out[:-4] + ".in" if os.path.exists(out[:-4] + ".in") else None)
            print(f"  {n}: {rec['verdict']} -- {'; '.join(rec['reasons']) or 'no reason recorded'}")

    e_slab, e_h2o, e_h2 = E.get("slab"), E.get("H2O"), E.get("H2")
    if None in (e_slab, e_h2o, e_h2):
        print("ERROR: need finished slab + H2O + H2 to compute eta."); return

    rows, etas = [], []
    for si in range(manifest["n_sites"]):
        try:
            dG = {sp: delta_G(e_slab, E[f"s{si}_{sp}"], sp, e_h2o, e_h2) for sp in ADSORBATES}
        except (KeyError, TypeError):
            continue
        res = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        etas.append(res.overpotential)
        rows.append(dict(site=si, dG_OH=round(dG["OH"], 3), dG_O=round(dG["O"], 3),
                         dG_OOH=round(dG["OOH"], 3), eta=round(res.overpotential, 3),
                         pls=res.potential_limiting_step))
    if not etas:
        print("ERROR: no complete site found."); return
    etas = np.array(etas)
    summary = dict(composition=manifest["composition"], n_sites=len(etas),
                   eta_min=float(etas.min()), eta_mean=float(etas.mean()),
                   eta_std=float(etas.std()) if len(etas) > 1 else 0.0,
                   eta_max=float(etas.max()), per_site=rows)
    out = os.path.join(args.outdir, "dft_eta.json")
    json.dump(summary, open(out, "w"), indent=2)
    print(json.dumps(summary, indent=2))
    print(f"-> {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="write QE relax inputs + manifest")
    b.add_argument("composition", help="endmember 'Cr' or HEA 'Fe32Ni17Co34Mn18'")
    b.add_argument("--outdir", required=True)
    b.add_argument("--pseudo-dir", default="/usr/share/espresso/pseudo")
    b.add_argument("--n-sites", type=int, default=1, help="cus sites (1 for endmembers)")
    b.add_argument("--supercell", type=int, default=2)
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--ecutwfc", type=float, default=80.0)
    b.add_argument("--ecutrho", type=float, default=640.0)
    b.set_defaults(func=cmd_build)
    e = sub.add_parser("eta", help="parse outputs -> OER overpotential")
    e.add_argument("--outdir", required=True)
    e.set_defaults(func=cmd_eta)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
