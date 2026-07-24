#!/usr/bin/env python
"""R0 re-parity (docs/28 s2/s7): uma-s-1p2p1 with the oc22 (PBE+U oxide) task head
vs the archived QE PBE+U eta on the rutile MO2(110) endmembers.

The 2026-07 verdict "UMA cannot rank rutile OER" (docs/26) ran uma-s-1p1 with the
oc20 head (RPBE metals) -- the wrong task for correlated oxides. This runner
replays the IDENTICAL QE initial geometries (runs/<M>_slab/*.in) through
uma-s-1p2p1 under BOTH heads (oc22 = the correct one, oc20 = the ablation), plus
two in-distribution literature anchors, RuO2(110) and IrO2(110), built by the
same slab code path (runs/{Ru,Ir}_anchor/, see docs/29). Literature expectation
for the anchors: eta(RuO2) ~ 0.37-0.42 V, eta(IrO2) ~ 0.56 V (Rossmeisl 2007;
Man 2011).

Reference-chain rule: gas-phase H2O/H2 are computed with the SAME model+head as
the slabs. Heads emulate different DFT references (oc22 = PBE+U totals, oc20 =
RPBE adsorption), so cross-head mixing would break the CHE chain; each head is
self-consistent, mirroring how the QE side uses its own gas references.

Writes per dir:  uma_eta_1p2p1_<task>.json  (+ relaxed_1p2p1_<task>_<job>.extxyz)
Never touches the archived uma_eta.json (uma-s-1p1/oc20, docs/26 provenance).
Combined:        <runs_root>/uma_1p2p1_summary.json

Usage (on the GPU box, HF_TOKEN set, fairchem-core installed):
  python src/dft/uma_oc22_parity.py runs --tasks oc22,oc20
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

JOBS = ("slab", "s0_OH", "s0_O", "s0_OOH")
FMAX, STEPS = 0.05, 300  # identical to the docs/26 UMA leg


def relax_diag(atoms, calc, fmax=FMAX, steps=STEPS):
    """BFGS relax (same recipe as hea_oer.relax.relax) + QC diagnostics."""
    from ase.optimize import BFGS

    atoms = atoms.copy()
    atoms.calc = calc
    opt = BFGS(atoms, logfile=None)
    converged = opt.run(fmax=fmax, steps=steps)
    f = atoms.get_forces()
    fmax_final = float(np.sqrt((f ** 2).sum(axis=1)).max())
    return (float(atoms.get_potential_energy()), atoms,
            dict(steps=int(opt.nsteps), fmax_final=round(fmax_final, 4),
                 converged=bool(converged)))


def gas_refs(calc):
    from ase.build import molecule

    out = {}
    for name in ("H2O", "H2"):
        m = molecule(name)
        m.set_cell([12.0, 12.0, 12.0])
        m.center()
        m.pbc = True
        e, _, qc = relax_diag(m, calc)
        out[name] = (e, qc)
    return out


def discover_dirs(root):
    hits = []
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if os.path.isdir(p) and all(os.path.exists(os.path.join(p, j + ".in")) for j in JOBS):
            hits.append(d)
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("runs_root", nargs="?", default="runs")
    ap.add_argument("--model", default="uma-s-1p2p1")
    ap.add_argument("--tasks", default="oc22,oc20")
    ap.add_argument("--dirs", default=None, help="comma list; default: auto-discover")
    ap.add_argument("--device", default="cuda")
    args = ap.parse_args()

    from ase.io import read, write
    from fairchem.core import FAIRChemCalculator, pretrained_mlip
    from hea_oer.referencing import delta_G
    from hea_oer.descriptors import oer_overpotential

    dirs = args.dirs.split(",") if args.dirs else discover_dirs(args.runs_root)
    tasks = args.tasks.split(",")
    print(f"[r0] model={args.model} tasks={tasks} dirs={dirs}", flush=True)

    t_all = time.time()
    print(f"[r0] loading predict unit (downloads {args.model} on first use)...", flush=True)
    try:
        predict_unit = pretrained_mlip.get_predict_unit(args.model, device=args.device)
    except Exception as e:
        avail = getattr(pretrained_mlip, "available_models", None)
        print(f"FATAL: get_predict_unit failed: {e!r}\navailable_models={avail}", flush=True)
        raise

    summary = dict(model=args.model, tasks={}, started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    for task in tasks:
        calc = FAIRChemCalculator(predict_unit, task_name=task)
        print(f"\n[r0:{task}] gas references...", flush=True)
        gas = gas_refs(calc)
        e_h2o, e_h2 = gas["H2O"][0], gas["H2"][0]
        print(f"  E_H2O={e_h2o:.4f}  E_H2={e_h2:.4f} eV", flush=True)
        task_block = dict(E_H2O=e_h2o, E_H2=e_h2,
                          gas_qc={k: v[1] for k, v in gas.items()}, dirs={})

        for d in dirs:
            p = os.path.join(args.runs_root, d)
            comp = d.split("_")[0]
            E, qc, err = {}, {}, None
            for job in JOBS:
                atoms = read(os.path.join(p, job + ".in"), format="espresso-in")
                t0 = time.time()
                try:
                    E[job], relaxed, qc[job] = relax_diag(atoms, calc)
                except Exception as ex:  # keep going; record the failure
                    err = f"{job}: {ex!r}"
                    print(f"  [{d}] {job} FAILED: {ex!r}", flush=True)
                    break
                write(os.path.join(p, f"relaxed_1p2p1_{task}_{job}.extxyz"), relaxed)
                print(f"  [{d}] {job:7s} E={E[job]:12.4f} eV  "
                      f"steps={qc[job]['steps']:3d} fmax={qc[job]['fmax_final']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            if err:
                task_block["dirs"][d] = dict(composition=comp, error=err, qc=qc)
                continue

            dG = {sp: delta_G(E["slab"], E[f"s0_{sp}"], sp, e_h2o, e_h2)
                  for sp in ("OH", "O", "OOH")}
            res = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
            rec = dict(
                composition=comp, backend=args.model, task=task,
                E_H2O=e_h2o, E_H2=e_h2, E_slab=E["slab"],
                E_O=E["s0_O"], E_OH=E["s0_OH"], E_OOH=E["s0_OOH"],
                n_sites=1,
                per_site=[dict(site=0, dG_OH=round(dG["OH"], 3), dG_O=round(dG["O"], 3),
                               dG_OOH=round(dG["OOH"], 3), eta=round(res.overpotential, 3),
                               pls=res.potential_limiting_step)],
                eta_min=round(res.overpotential, 3), eta_mean=round(res.overpotential, 3),
                eta_std=0.0, eta_max=round(res.overpotential, 3),
                qc=qc,
            )
            with open(os.path.join(p, f"uma_eta_1p2p1_{task}.json"), "w") as f:
                json.dump(rec, f, indent=2)
            task_block["dirs"][d] = rec
            print(f"  [{d}] eta={rec['eta_min']:.3f} V  pls={res.potential_limiting_step}  "
                  f"dG_OH/O/OOH={dG['OH']:.2f}/{dG['O']:.2f}/{dG['OOH']:.2f}", flush=True)

        summary["tasks"][task] = task_block

    summary["wall_s"] = round(time.time() - t_all, 1)
    out = os.path.join(args.runs_root, "uma_1p2p1_summary.json")
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[r0] DONE in {summary['wall_s']}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
