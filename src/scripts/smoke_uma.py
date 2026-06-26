#!/usr/bin/env python
"""Smoke-test the fairchem surface backend on ONE composition.

Real run (GPU + HF access to UMA):
    python src/scripts/smoke_uma.py --model uma-s-1p1
Plumbing only (CPU, EMT stand-in — validates slab->relax->reference->dG end to end
without any gated model; restricted to EMT-supported metals Ni/Cu):
    python src/scripts/smoke_uma.py --calc emt
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hea_oer.composition import Composition  # noqa: E402
from hea_oer.adsorption import FairchemSurfaceBackend  # noqa: E402
from hea_oer.descriptors import oer_overpotential, descriptor_from_dG_OH  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--calc", choices=["uma", "emt"], default="uma")
    p.add_argument("--model", default="uma-s-1p1")
    p.add_argument("--task", default="oc20")
    p.add_argument("--device", default="cuda")
    p.add_argument("--steps", type=int, default=200)
    p.add_argument("--fmax", type=float, default=0.05)
    args = p.parse_args()

    if args.calc == "emt":
        from ase.calculators.emt import EMT

        comp = Composition.from_dict({"Ni": 0.5, "Cu": 0.5})  # EMT supports Ni/Cu/O/H
        backend = FairchemSurfaceBackend(calculator=EMT(), size=(2, 2, 3),
                                         steps=args.steps, fmax=args.fmax)
        print("[plumbing] EMT stand-in on Ni50Cu50 -- unphysical for OER, validates the pipeline")
    else:
        comp = Composition.equiatomic(["Co", "Cr", "Fe", "Mn", "Ni"])
        backend = FairchemSurfaceBackend(model=args.model, task=args.task, device=args.device,
                                         steps=args.steps, fmax=args.fmax)
        print(f"[real] {args.model} ({args.task}) on {comp.formula()}")

    t0 = time.time()
    dG_OH, dG_O, dG_OOH = backend.predict(comp)
    res = oer_overpotential(dG_OH, dG_O, dG_OOH)
    dt = time.time() - t0

    print(f"composition : {comp.formula()}")
    print(f"backend     : {backend.name}")
    print(f"dG(*OH/*O/*OOH) : {dG_OH:.3f} / {dG_O:.3f} / {dG_OOH:.3f} eV")
    print(f"descriptor (dG_O - dG_OH) : {descriptor_from_dG_OH(dG_OH, dG_O):.3f} eV")
    print(f"theoretical overpotential : {res.overpotential:.3f} V "
          f"(limiting step {res.potential_limiting_step})")
    print(f"elapsed     : {dt:.1f} s")


if __name__ == "__main__":
    main()
