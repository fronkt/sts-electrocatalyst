#!/usr/bin/env python
"""UMA half of the parity for the rutile MO2 endmembers. One model load, loop all.
Reads the canonical QE *.in geometries from runs/<M>_slab/, relaxes with uma-s-1p1,
applies the same CHE referencing -> runs/<M>_slab/uma_eta.json (mirrors CrO2)."""
from __future__ import annotations
import json, os, sys, time

sys.path.insert(0, "/workspace/STS2027/src")
from ase.io import read
from hea_oer.relax import make_calculator, relax, gas_reference_energies
from hea_oer.referencing import delta_G
from hea_oer.descriptors import oer_overpotential

ROOT = "/workspace/STS2027/runs"
ENDMEMBERS = sys.argv[1:] or ["Mn", "Fe", "Co", "Ni", "Cu"]
FMAX, STEPS = 0.05, 300

t0 = time.time()
print("[uma] loading uma-s-1p1 (offline cache)...", flush=True)
calc = make_calculator("uma-s-1p1", "oc20", "cuda")
e_h2o, e_h2 = gas_reference_energies(calc, fmax=FMAX, steps=STEPS)
print(f"[uma] gas refs: E_H2O={e_h2o:.4f}  E_H2={e_h2:.4f} eV  ({time.time()-t0:.0f}s)", flush=True)

for M in ENDMEMBERS:
    d = os.path.join(ROOT, f"{M}_slab")
    try:
        E = {}
        for name in ("slab", "s0_OH", "s0_O", "s0_OOH"):
            atoms = read(os.path.join(d, name + ".in"), format="espresso-in")
            E[name], _ = relax(atoms, calc, fmax=FMAX, steps=STEPS)
        dG = {sp: delta_G(E["slab"], E[f"s0_{sp}"], sp, e_h2o, e_h2) for sp in ("OH", "O", "OOH")}
        res = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        summary = dict(
            composition=f"{M}100", backend="uma-s-1p1", task="oc20",
            E_H2O=e_h2o, E_H2=e_h2, E_slab=E["slab"], E_O=E["s0_O"], E_OH=E["s0_OH"], E_OOH=E["s0_OOH"],
            n_sites=1,
            per_site=[dict(site=0, dG_OH=round(dG["OH"], 3), dG_O=round(dG["O"], 3),
                           dG_OOH=round(dG["OOH"], 3), eta=round(res.overpotential, 3),
                           pls=res.potential_limiting_step)],
            eta_min=round(res.overpotential, 3), eta_mean=round(res.overpotential, 3),
            eta_std=0.0, eta_max=round(res.overpotential, 3))
        json.dump(summary, open(os.path.join(d, "uma_eta.json"), "w"), indent=2)
        print(f"[OK] {M}: eta={res.overpotential:.3f} V  pls={res.potential_limiting_step}  "
              f"dG_OH/O/OOH={dG['OH']:.2f}/{dG['O']:.2f}/{dG['OOH']:.2f}", flush=True)
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"[FAIL] {M}: {e!r}", flush=True)

print(f"ALL_ENDMEMBERS_DONE  ({time.time()-t0:.0f}s)", flush=True)
