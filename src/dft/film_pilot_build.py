#!/usr/bin/env python3
"""Film-model DFT pilot: oxyhydroxide (01-12) edge slabs for the validation set.

Validation set (docs/research/film-dft-pilot-2026-11-14.md):
  NiOOH            Ni edge site
  Ni(Fe)OOH        one Fe on the top edge row: Fe site, and the Ni site next to it
  CoOOH            Co edge site
Each site gets *OH, *O, *OOH; plus the three clean slabs and the H2O / H2 references.

Structure prototype: beta-NiOOH, P3m1 (Materials Project mp-999337, GGA+U with the same
U values used here). CoOOH uses the same layer prototype with heterogenite's lattice
(mp-27913: a = 2.849 A, interlayer 12.935 / 3 = 4.312 A), so the three films differ in
chemistry only, not in stacking. Slab: (012) = hexagonal (01-12), the termination whose
top metal is 5-coordinated (edge site) and which has no metal below CN 5; 2x1 in-plane
(adsorbate images ~6 A apart); bottom half fixed; dipole correction in the vacuum.

The QE input text comes from qe_slab.write_slab_input (same pseudos, U values, cutoffs,
nosym requirement). Adsorbates start off the mirror plane with a seeded displacement,
because a start on an exact symmetry plane stays locked in it (docs/41 s6g).

Usage (from the repo root, the ISEF venv):
  python src/dft/film_pilot_build.py --outdir runs/film_pilot_2026-11-14
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
_spec = importlib.util.spec_from_file_location("qe_slab", os.path.join(HERE, "qe_slab.py"))
qe_slab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qe_slab)

ECUTWFC, ECUTRHO = 80, 640          # docs/23 production lock, same as the STS tier
KPTS = (3, 3, 1)                    # same mesh on every film: 2x1 (012) cells are 5.7-6.0 x 6.6-6.9 A
VACUUM = 16.0                       # A above the slab top
EMAXPOS = 0.80                      # sawtooth at 0.80-0.825 c (~21 A; adsorbate tops <= 13 A)
SEED = 20261114

M_O = {"O": 1.80, "OH": 1.95, "OOH": 1.95}   # starting metal-O distances (A)
D_OH, D_OO = 0.98, 1.45


def bulk_structures():
    """beta-NiOOH (mp-999337) and CoOOH in the same P3m1 layer prototype."""
    from pymatgen.core import Lattice, Structure
    cif = os.path.join(REPO, "data", "film", "NiOOH_mp-999337.cif")
    ni = Structure.from_file(cif)
    co = Structure(Lattice.hexagonal(2.84887, 12.93523 / 3.0),
                   ["Co" if s.specie.symbol == "Ni" else s.specie.symbol for s in ni],
                   ni.frac_coords)
    return {"Ni": ni, "Co": co}


def edge_slab(bulk):
    """(012) slab, top metal CN 5, no metal below CN 5; returned as orthogonal-c pymatgen Slab."""
    from pymatgen.core.surface import SlabGenerator
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
    conv = SpacegroupAnalyzer(bulk).get_conventional_standard_structure()
    gen = SlabGenerator(conv, (0, 1, 2), min_slab_size=9.0, min_vacuum_size=15.0,
                        center_slab=False, primitive=True, lll_reduce=True)
    metal = [e for e in ("Ni", "Co") if e in conv.composition][0]
    picks = []
    for sl in gen.get_slabs(bonds={("O", "H"): 1.15}, symmetrize=False):
        sl = sl.get_orthogonal_c_slab()
        z = sl.cart_coords[:, 2]
        mets = [i for i, s in enumerate(sl.species) if s.symbol == metal]
        cn = {i: sum(1 for nb in sl.get_neighbors(sl[i], 2.3) if nb.specie.symbol == "O")
              for i in mets}
        top = max(mets, key=lambda i: z[i])
        if cn[top] == 5 and min(cn.values()) >= 5:
            picks.append(sl)
    if not picks:
        raise RuntimeError("no (012) termination with a CN-5 top metal and no CN<5 metal")
    return picks[0]


def to_atoms(slab):
    """pymatgen Slab -> ASE Atoms: 2x1 in-plane, bottom at 1 A, vacuum on top, bottom half fixed."""
    from ase.constraints import FixAtoms
    from pymatgen.io.ase import AseAtomsAdaptor
    atoms = AseAtomsAdaptor.get_atoms(slab)
    atoms = atoms.repeat((2, 1, 1))
    pos = atoms.get_positions()
    pos[:, 2] -= pos[:, 2].min() - 1.0
    atoms.set_positions(pos)
    cell = atoms.get_cell().array.copy()
    top = pos[:, 2].max()
    cell[2] = [0.0, 0.0, top + VACUUM]
    atoms.set_cell(cell, scale_atoms=False)
    zmid = 0.5 * (pos[:, 2].min() + top)
    atoms.set_constraint(FixAtoms(indices=[i for i, p in enumerate(pos) if p[2] < zmid]))
    return atoms


def edge_sites(atoms, metals=("Ni", "Co", "Fe")):
    """Top-row CN-5 metals, highest first, with the unit vector to the missing octahedral vertex."""
    from ase.neighborlist import neighbor_list
    i_idx, j_idx, d_vec = neighbor_list("ijD", atoms, 2.3)
    sym = atoms.get_chemical_symbols()
    z = atoms.positions[:, 2]
    out = []
    for i, s in enumerate(sym):
        if s not in metals:
            continue
        vs = [d_vec[k] for k in np.where(i_idx == i)[0] if sym[j_idx[k]] == "O"]
        if len(vs) != 5:
            continue
        u = -np.sum([v / np.linalg.norm(v) for v in vs], axis=0)
        u /= np.linalg.norm(u)
        out.append((i, u))
    zmax = max(z[i] for i, _ in out)
    out = [(i, u) for i, u in out if z[i] > zmax - 1.0]
    out.sort(key=lambda t: (-z[t[0]], atoms.positions[t[0], 0]))
    return out


def _perp(u, rng):
    a = rng.normal(size=3)
    a -= a.dot(u) * u
    return a / np.linalg.norm(a)


def add_adsorbate(atoms, site, u, species, rng):
    """Place *O / *OH / *OOH on metal `site` along u, tilted off any mirror plane."""
    from ase import Atom
    if u[2] < 0.3:                        # keep the adsorbate pointing into the vacuum
        u = u.copy(); u[2] = max(u[2], 0.3); u /= np.linalg.norm(u)
    ads = atoms.copy()
    m = ads.positions[site]
    o1 = m + M_O[species] * u
    new = [("O", o1)]
    w = _perp(u, rng)
    if species == "OH":
        new.append(("H", o1 + D_OH * (np.cos(np.radians(70)) * u + np.sin(np.radians(70)) * w)))
    elif species == "OOH":
        o2 = o1 + D_OO * (np.cos(np.radians(65)) * u + np.sin(np.radians(65)) * w)
        w2 = _perp(o2 - o1, rng)
        h = o2 + D_OH * (0.35 * (o2 - o1) / D_OO + 0.94 * w2)
        new += [("O", o2), ("H", h)]
    for s, p in new:
        ads.append(Atom(s, p + rng.normal(scale=0.05, size=3)))
    n0 = len(atoms)
    for k in range(n0, len(ads)):
        d = np.linalg.norm(ads.positions[:n0] - ads.positions[k], axis=1)
        d[site] = 9.9
        lim = 1.4 if ads[k].symbol == "H" else 1.7
        if d.min() < lim:
            raise RuntimeError(f"{species} atom {k} is {d.min():.2f} A from atom {int(d.argmin())}")
    return ads


def finish_input(text, atoms):
    """Add the dipole correction (sawtooth in the vacuum) and the pilot k-mesh."""
    c = atoms.cell[2, 2]
    emaxpos = EMAXPOS                  # identical for clean slab and adslabs of a film
    if atoms.positions[:, 2].max() > (emaxpos - 0.10) * c:
        raise RuntimeError("an atom sits within 0.1 c of the dipole sawtooth")
    text = text.replace("  tprnfor = .true.\n",
                        "  tprnfor = .true.\n  tefield = .true.\n  dipfield = .true.\n", 1)
    text = text.replace("  degauss = 0.01\n",
                        f"  degauss = 0.01\n  edir = 3\n  emaxpos = {emaxpos:.4f}\n"
                        "  eopreg = 0.0250\n  eamp = 0.0\n", 1)
    text = text.replace("  conv_thr = 1.0d-6\n", "  conv_thr = 1.0d-7\n", 1)
    k = list(KPTS)
    head, _, tail = text.partition("K_POINTS automatic\n")
    tail = tail.split("\n", 1)[1]
    return head + f"K_POINTS automatic\n  {k[0]} {k[1]} {k[2]} 0 0 0\n" + tail, k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(REPO, "runs", "film_pilot_2026-11-14"))
    ap.add_argument("--pseudo-dir", default="/home/ubuntu/film/pseudo")   # AWS box layout
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    rng = np.random.default_rng(SEED)
    from ase.io import write

    bulks = bulk_structures()
    films = {}
    for host, bulk in bulks.items():
        films[f"{host}OOH"] = to_atoms(edge_slab(bulk))
    fe = films["NiOOH"].copy()
    sites_ni = edge_sites(fe)
    if len(sites_ni) < 2:
        raise RuntimeError(f"expected 2 top edge sites, found {len(sites_ni)}")
    fe[sites_ni[0][0]].symbol = "Fe"
    films["NiFeOOH"] = fe

    plan = {"NiOOH": [("Ni", 0)], "CoOOH": [("Co", 0)], "NiFeOOH": [("Fe", 0), ("Ni", 1)]}
    manifest = {"created": "2026-11-14", "ecutwfc": ECUTWFC, "ecutrho": ECUTRHO,
                "kpts": list(KPTS), "seed": SEED, "pseudo_dir": args.pseudo_dir,
                "u_ev": {e: qe_slab.ELEMENTS[e]["U"] for e in ("Ni", "Fe", "Co")}, "jobs": []}

    def emit(name, atoms, kind, **meta):
        txt = qe_slab.write_slab_input(atoms, name, args.pseudo_dir, ECUTWFC, ECUTRHO, nosym=True)
        txt, k = finish_input(txt, atoms)
        with open(os.path.join(args.outdir, name + ".in"), "w", newline="\n") as f:
            f.write(txt)
        write(os.path.join(args.outdir, name + ".traj"), atoms)
        manifest["jobs"].append(dict(name=name, kind=kind, nat=len(atoms), kpts=k,
                                     nfree=int(len(atoms) - len(atoms.constraints[0].index)), **meta))

    for film, atoms in films.items():
        emit(f"{film}__slab", atoms, "slab", film=film)
        sites = edge_sites(atoms)
        for metal, k in plan[film]:
            i, u = sites[k]
            assert atoms[i].symbol == metal, (film, metal, atoms[i].symbol)
            for sp in qe_slab.ADSORBATES:
                emit(f"{film}__{metal}{k}_{sp}", add_adsorbate(atoms, i, u, sp, rng),
                     "adslab", film=film, site_metal=metal, site_index=int(i), species=sp)
    for name, mol in qe_slab._gas_molecules().items():
        txt = qe_slab.write_molecule_input(name, mol, args.pseudo_dir, ECUTWFC, ECUTRHO)
        with open(os.path.join(args.outdir, f"gas__{name}.in"), "w", newline="\n") as f:
            f.write(txt.replace(f"prefix = '{name}'", f"prefix = 'gas__{name}'"))
        manifest["jobs"].append(dict(name=f"gas__{name}", kind="gas", nat=len(mol), kpts=[1, 1, 1]))

    with open(os.path.join(args.outdir, "manifest.json"), "w", newline="\n") as f:
        json.dump(manifest, f, indent=2)
    for j in manifest["jobs"]:
        print(f"{j['name']:28s} {j['kind']:6s} nat={j['nat']:3d} k={j['kpts']} free={j.get('nfree', '-')}")
    print(f"{len(manifest['jobs'])} jobs -> {args.outdir}")


if __name__ == "__main__":
    main()
