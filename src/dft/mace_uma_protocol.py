#!/usr/bin/env python
"""MACE-MPA-0 under UMA's EXACT docs/29 protocol, so the two models are matched.

Why this exists
---------------
Until 2026-08-05 the project had never scored MACE and UMA the same way, and every
axis on which they differed ran in MACE's favour (docs/38 §1):

    UMA (src/dft/uma_oc22_parity.py, 2026-07-25) did:
      - read runs/<dir>/<job>.in  -- the ORIGINAL builder geometry, adsorbate
        3.06-3.14 A off the cus metal (past our own 3.00 A desorption cut)
      - SINGLE start, no pull-ins
      - FixAtoms from the QE if_pos card (the as-shipped mask)
      - ASE BFGS, fmax=0.05, steps=300
      - gas refs: ase.build.molecule('H2O'/'H2') in a 12 A cubic cell, relaxed by
        the SAME model
      - scored against a DFT reference in which Cr (trapped s0_O) and Ni (two
        unconverged adslabs) were later found defective

    Every published MACE number instead used either (a) DFT-relaxed frames, or
    (b) the CURRENT .in files -- three of which were REPLACED by repaired /
    MLIP-seeded geometries AFTER the UMA run.

This script restores the originals from their archived suffixes and re-runs MACE
single-start, so `parity_matched.py` can put both models on one footing.

Result (docs/38): MACE reproduces its published eta to within 5 mV on all seven
metals from raw builder geometries with a single start, so none of the protocol
advantages was load-bearing. The conclusion survives matching; the presentation
did not.

    python src/dft/mace_uma_protocol.py --out results/r5_matched_protocol.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ase.build import molecule                      # noqa: E402
from ase.io import read                             # noqa: E402
from ase.optimize import BFGS                       # noqa: E402

from hea_oer.descriptors import oer_overpotential   # noqa: E402
from hea_oer.referencing import delta_G             # noqa: E402

N_SLAB = 18

#: The ORIGINAL builder input for each state -- the exact file UMA read on
#: 2026-07-25. Where the live .in has since been replaced by a repaired or
#: MLIP-seeded geometry, the original survives under a dated suffix and is what
#: we restore here. Keeping this table explicit is the whole point of the script:
#: it is the difference between "matched" and "matched as far as I remembered".
ORIG = {
    "Cr": ("Cr_slab", {"slab": "slab.in", "s0_O": "s0_O.in.trapped-2026-08-02",
                       "s0_OH": "s0_OH.in", "s0_OOH": "s0_OOH.in"}),
    "Mn": ("Mn_slab", {"slab": "slab.in", "s0_O": "s0_O.in",
                       "s0_OH": "s0_OH.in", "s0_OOH": "s0_OOH.in.desorbed-2026-08-02"}),
    "Fe": ("Fe_slab", {"slab": "slab.in", "s0_O": "s0_O.in",
                       "s0_OH": "s0_OH.in", "s0_OOH": "s0_OOH.in.desorbed-2026-08-02"}),
    "Co": ("Co_slab", {"slab": "slab.in", "s0_O": "s0_O.in.missing-2026-08-04",
                       "s0_OH": "s0_OH.in", "s0_OOH": "s0_OOH.in"}),
    "Ni": ("Ni_slab", {"slab": "slab.in", "s0_O": "s0_O.in.poisoned-2026-08-04",
                       "s0_OH": "s0_OH.in.poisoned-2026-08-04",
                       "s0_OOH": "s0_OOH.in.desorbed-2026-08-04"}),
    # The anchors' .in.uma files carry UMA's own 10-free-atom mask, not the
    # canonical 11. Matching UMA means using UMA's mask, deliberately.
    "Ru": ("Ru_anchor", {"slab": "slab.in", "s0_O": "s0_O.in.uma",
                         "s0_OH": "s0_OH.in.uma", "s0_OOH": "s0_OOH.in.uma"}),
    "Ir": ("Ir_anchor", {"slab": "slab.in", "s0_O": "s0_O.in.uma",
                         "s0_OH": "s0_OH.in.uma", "s0_OOH": "s0_OOH.in.uma"}),
}


def relax(calc, atoms, fmax=0.05, steps=300):
    a = atoms.copy()
    a.calc = calc
    opt = BFGS(a, logfile=None)
    converged = opt.run(fmax=fmax, steps=steps)
    fm = max(sum(c * c for c in fv) ** 0.5 for fv in a.get_forces())
    return a, float(a.get_potential_energy()), int(opt.get_number_of_steps()), float(fm), bool(converged)


def m_o_distance(atoms, metal):
    """Shortest metal-adsorbate distance, or None for a bare slab."""
    if len(atoms) <= N_SLAB:
        return None
    return min(math.dist(atoms[N_SLAB].position, x.position)
               for x in atoms[:N_SLAB] if x.symbol == metal)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="runs")
    ap.add_argument("--backend", default="mace", choices=("mace", "uma"),
                    help="swap the calculator; the protocol is identical either way")
    ap.add_argument("--model", default=None,
                    help="default: medium-mpa-0 (mace) / uma-s-1p2 (uma)")
    ap.add_argument("--uma-task", default="omat",
                    help="UMA task head. Heads emulate different DFT references, so the "
                         "gas chain is recomputed per head and never mixed (docs/29 s2).")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dtype", default="float64")
    ap.add_argument("--out", default="results/r5_matched_protocol.json")
    a = ap.parse_args()

    # One runner, one protocol, calculator swapped. Matching is then a property of the
    # code path rather than of anyone remembering to match (docs/39 s2).
    if a.backend == "mace":
        a.model = a.model or "medium-mpa-0"
        from mace.calculators import mace_mp
        print(f"loading MACE {a.model} ({a.device}, {a.dtype}) ...", flush=True)
        calc = mace_mp(model=a.model, device=a.device, default_dtype=a.dtype)
        tag = f"mace:{a.model}"
    else:
        a.model = a.model or "uma-s-1p2"
        from fairchem.core import FAIRChemCalculator, pretrained_mlip
        print(f"loading UMA {a.model} task={a.uma_task} ({a.device}) ...", flush=True)
        calc = FAIRChemCalculator(pretrained_mlip.get_predict_unit(a.model, device=a.device),
                                  task_name=a.uma_task)
        tag = f"uma:{a.model}:{a.uma_task}"

    gas = {}
    for name in ("H2O", "H2"):
        m = molecule(name)
        m.set_cell([12.0, 12.0, 12.0])
        m.center()
        m.pbc = True
        _, e, n, fm, _ = relax(calc, m)
        gas[name] = e
        print(f"  gas {name:4s} E={e:12.4f} eV  steps={n} fmax={fm:.4f}", flush=True)

    out = {}
    for metal, (d, files) in ORIG.items():
        E, qc = {}, {}
        t0 = time.time()
        for job in ("slab", "s0_O", "s0_OH", "s0_OOH"):
            at = read(os.path.join(a.root, d, files[job]), format="espresso-in")
            d0 = m_o_distance(at, metal)
            relaxed, e, n, fm, conv = relax(calc, at)
            d1 = m_o_distance(relaxed, metal)
            E[job] = e
            qc[job] = dict(file=files[job], steps=n, fmax=round(fm, 4), converged=conv,
                           m_o_start=None if d0 is None else round(d0, 3),
                           m_o_final=None if d1 is None else round(d1, 3))
            print(f"  {metal}/{job:7s} {files[job]:32s} steps={n:3d} fmax={fm:.4f} "
                  f"M-O {d0 and round(d0, 3)} -> {d1 and round(d1, 3)}", flush=True)
        dG = {sp: delta_G(E["slab"], E["s0_" + sp], sp, gas["H2O"], gas["H2"])
              for sp in ("OH", "O", "OOH")}
        r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        out[metal] = dict(dG_OH=dG["OH"], dG_O=dG["O"], dG_OOH=dG["OOH"],
                          eta=r.overpotential, pls=r.potential_limiting_step,
                          qc=qc, wall_s=round(time.time() - t0, 1))
        print(f"  -> {metal}: eta = {r.overpotential:.3f} V  pls={r.potential_limiting_step}\n",
              flush=True)

    res = dict(model=a.model, backend=a.backend, tag=tag, dtype=a.dtype, device=a.device,
               uma_task=a.uma_task if a.backend == "uma" else None,
               protocol=("UMA-matched: ORIGINAL builder .in, SINGLE start, as-shipped mask, "
                         "BFGS fmax=0.05 steps=300, gas refs = ase.build.molecule in 12A cell"),
               gas=gas, pred=out)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=2)
    print("->", a.out)


if __name__ == "__main__":
    main()
