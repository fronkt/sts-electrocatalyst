#!/usr/bin/env python
"""UMA half of the UMA<->DFT parity: relax the EXACT QE initial geometries with
uma-s-1p1 and apply the same CHE referencing -> uma_eta.json (mirrors dft_eta.json).

Fair parity: same initial structures (parsed from the QE *.in, same FixAtoms),
same delta_G + oer_overpotential. The ONLY difference vs the DFT point is the
relaxer/energy method (UMA MLIP here vs QE pw.x there).
"""
from __future__ import annotations
import json, os, sys, time

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "/workspace/STS2027/runs/Cr_slab"
sys.path.insert(0, "/workspace/STS2027/src")

from ase.io import read
from hea_oer.relax import make_calculator, relax, gas_reference_energies
from hea_oer.referencing import delta_G
from hea_oer.descriptors import oer_overpotential

FMAX, STEPS = 0.05, 300  # fmax 0.05 eV/A ~ QE forc_conv_thr 2e-3 Ry/au

def n_fixed(atoms):
    from ase.constraints import FixAtoms, FixCartesian
    f = set()
    for c in atoms.constraints:
        if isinstance(c, (FixAtoms, FixCartesian)):
            f.update(int(i) for i in c.get_indices())
    return len(f)

t_all = time.time()
print(f"[uma] building calculator (downloads uma-s-1p1 on first use)...", flush=True)
calc = make_calculator("uma-s-1p1", "oc20", "cuda")

print(f"[uma] gas references (H2O, H2)...", flush=True)
e_h2o, e_h2 = gas_reference_energies(calc, fmax=FMAX, steps=STEPS)
print(f"  E_H2O={e_h2o:.4f}  E_H2={e_h2:.4f} eV", flush=True)

E = {}
for name in ("slab", "s0_OH", "s0_O", "s0_OOH"):
    atoms = read(os.path.join(OUTDIR, name + ".in"), format="espresso-in")
    nf = n_fixed(atoms)
    t0 = time.time()
    E[name], _ = relax(atoms, calc, fmax=FMAX, steps=STEPS)
    print(f"  {name:7s} nat={len(atoms):2d} fixed={nf:2d}  E={E[name]:.4f} eV  ({time.time()-t0:.1f}s)", flush=True)

dG = {sp: delta_G(E["slab"], E[f"s0_{sp}"], sp, e_h2o, e_h2) for sp in ("OH", "O", "OOH")}
res = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])

summary = dict(
    composition="Cr100", backend="uma-s-1p1", task="oc20",
    E_H2O=e_h2o, E_H2=e_h2, E_slab=E["slab"], E_O=E["s0_O"], E_OH=E["s0_OH"], E_OOH=E["s0_OOH"],
    n_sites=1,
    per_site=[dict(site=0, dG_OH=round(dG["OH"], 3), dG_O=round(dG["O"], 3),
                   dG_OOH=round(dG["OOH"], 3), eta=round(res.overpotential, 3),
                   pls=res.potential_limiting_step)],
    eta_min=round(res.overpotential, 3), eta_mean=round(res.overpotential, 3),
    eta_std=0.0, eta_max=round(res.overpotential, 3),
)
out = os.path.join(OUTDIR, "uma_eta.json")
json.dump(summary, open(out, "w"), indent=2)
print(json.dumps(summary, indent=2))
print(f"-> {out}   (total {time.time()-t_all:.1f}s)")
