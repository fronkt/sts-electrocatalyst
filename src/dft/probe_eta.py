#!/usr/bin/env python3
"""Score a fixed-geometry probe batch: Delta-eta per protocol variable (docs/41).

Consumes the outputs of `probe_decks.py build` and reports, for every variant,
the change in Delta-G(*OH/*O/*OOH) and in the OER overpotential relative to the
`base` control.

Two gates run before any number is reported, because a sensitivity analysis whose
control has drifted is worse than no analysis at all -- it looks quantitative.

  GATE 1 (extraction).  `base` re-runs the unperturbed SCF at the geometry pulled
  out of the relaxation. Its energy must reproduce the relaxation's own final
  energy to within `--tol-ev` (default 5 meV, comfortably above SCF noise at
  conv_thr 1e-6 and far below the ~0.2 V effects being chased). A larger drift
  means the coordinates, cell, species order, magnetisation or Hubbard card did
  not survive the round trip, and every other variant in the batch is void.

  GATE 2 (QC).  Every probe output passes `qe_qc.trusted_energy_ev`, the same
  gate that production energies pass. `pw.x` prints `JOB DONE` after
  `convergence NOT achieved`, which is how eleven silently-unconverged
  relaxations reached docs/26.

The gas-phase references are reused from the source run and are NOT recomputed:
H2O and H2 run in a Martyna-Tuckerman box with `assume_isolated`, so neither a
slab dipole correction, a slab cell height, nor a metal-3d Hubbard U touches
them. Reusing them is exact here, not an approximation -- but it is checked, and
the script refuses to proceed if the source run's gas references failed QC.

Usage
-----
  PYTHONPATH=src python src/dft/probe_eta.py runs/probe/Ru
  PYTHONPATH=src python src/dft/probe_eta.py runs/probe/Cr --json results/probe_Cr.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

ADSORBATES = ("OH", "O", "OOH")


def _qc():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qe_qc.py")
    spec = importlib.util.spec_from_file_location("qe_qc", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("probedir")
    ap.add_argument("--tol-ev", type=float, default=5e-3,
                    help="max |base - relax| drift before the batch is declared void")
    ap.add_argument("--json", default=None)
    ap.add_argument("--allow-drift", action="store_true",
                    help="report anyway after a GATE 1 failure, marked UNTRUSTED")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    from hea_oer.referencing import delta_G
    from hea_oer.descriptors import oer_overpotential

    qc = _qc()
    man = json.load(open(os.path.join(args.probedir, "probe_manifest.json")))
    src = man["source_run"]
    variants = man["variants"]
    if "base" not in variants:
        sys.exit("REFUSING: batch has no 'base' control (probe_decks.py --variants base ...)")

    # --- gas references, reused from the source run, but QC'd here -------------
    gas = {}
    for g in ("H2O", "H2"):
        p = os.path.join(src, g + ".out")
        e = qc.trusted_energy_ev(p, strict=True) if os.path.exists(p) else None
        if e is None:
            sys.exit(f"REFUSING: source run gas reference {p} missing or failed QC")
        gas[g] = e
    print(f"gas references reused from {src}: "
          f"H2O {gas['H2O']:.4f} eV, H2 {gas['H2']:.4f} eV\n")

    # --- read every probe output ----------------------------------------------
    E, missing, failed = {}, [], []
    ref_relax = {}
    for j in man["jobs"]:
        key = (j["job"], j["variant"])
        out = os.path.join(args.probedir, j["file"][:-3] + ".out")
        ref_relax[j["job"]] = j.get("relax_reference_ev")
        if not os.path.exists(out):
            missing.append(key)
            continue
        e = qc.trusted_energy_ev(out, strict=True)
        if e is None:
            failed.append(key)
            continue
        E[key] = e

    if missing:
        print(f"NOT YET RUN: {len(missing)} of {len(man['jobs'])} probe jobs have no output.")
        for k in missing[:12]:
            print(f"  {k[0]:10s} {k[1]}")
        if len(missing) > 12:
            print(f"  ... and {len(missing) - 12} more")
        if not E:
            print("\nNothing to score yet. Run the decks, then re-run this.")
            return
        print()
    if failed:
        print(f"FAILED QC: {len(failed)} probe job(s) -- excluded.")
        for k in failed:
            out = os.path.join(args.probedir, f"{k[0]}__{k[1]}.out")
            rec = qc.scan(out, None)
            print(f"  {k[0]:10s} {k[1]:16s} {rec['verdict']}: {'; '.join(rec['reasons'])[:90]}")
        print()

    # --- GATE 1: the control must reproduce the relaxation --------------------
    print("GATE 1  extraction control (base SCF vs relaxation final energy)")
    drift_ok = True
    for job in sorted({j["job"] for j in man["jobs"]}):
        e_base, e_relax = E.get((job, "base")), ref_relax.get(job)
        if e_base is None or e_relax is None:
            print(f"  {job:10s} -- not available")
            drift_ok = False
            continue
        d = e_base - e_relax
        flag = "OK" if abs(d) <= args.tol_ev else "DRIFT"
        if abs(d) > args.tol_ev:
            drift_ok = False
        print(f"  {job:10s} base {e_base:14.4f}  relax {e_relax:14.4f}  "
              f"drift {d*1000:+8.2f} meV  {flag}")
    if not drift_ok:
        print(f"\nGATE 1 FAILED (tolerance {args.tol_ev*1000:.1f} meV).")
        if not args.allow_drift:
            sys.exit("REFUSING to score. Re-check coordinate/cell/species round trip, "
                     "or pass --allow-drift to see the numbers marked UNTRUSTED.")
        print("--allow-drift set: numbers below are UNTRUSTED.\n")
    else:
        print("  -> control reproduces the relaxation; extraction is faithful.\n")

    # --- score every variant ---------------------------------------------------
    rows, base_eta = [], None
    for v in variants:
        need = [("slab", v)] + [(f"s0_{sp}", v) for sp in ADSORBATES]
        if any(k not in E for k in need):
            continue
        e_slab = E[("slab", v)]
        dG = {sp: delta_G(e_slab, E[(f"s0_{sp}", v)], sp, gas["H2O"], gas["H2"])
              for sp in ADSORBATES}
        res = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        row = dict(variant=v, dG_OH=dG["OH"], dG_O=dG["O"], dG_OOH=dG["OOH"],
                   eta=res.overpotential, pls=res.potential_limiting_step,
                   descriptor=dG["O"] - dG["OH"])
        if v == "base":
            base_eta = row
        rows.append(row)

    if not rows:
        print("No variant has a complete slab + OH + O + OOH set yet.")
        return

    print(f"{'variant':16s} {'dG_OH':>8s} {'dG_O':>8s} {'dG_OOH':>8s} "
          f"{'dG_O-dG_OH':>11s} {'eta':>7s} {'pls':>4s} {'d_eta vs base':>14s}")
    for r in rows:
        d = "" if base_eta is None or r["variant"] == "base" else \
            f"{r['eta'] - base_eta['eta']:+.4f} V"
        print(f"{r['variant']:16s} {r['dG_OH']:8.3f} {r['dG_O']:8.3f} {r['dG_OOH']:8.3f} "
              f"{r['descriptor']:11.3f} {r['eta']:7.4f} {r['pls']:4d} {d:>14s}")

    if base_eta is not None:
        print(f"\nbase eta = {base_eta['eta']:.4f} V (pls {base_eta['pls']})")
        for r in rows:
            if r["variant"] == "base":
                continue
            shifts = " ".join(f"{sp} {r['dG_'+sp] - base_eta['dG_'+sp]:+.3f}"
                              for sp in ADSORBATES)
            print(f"  {r['variant']:16s} d_eta {r['eta']-base_eta['eta']:+.4f} V   "
                  f"dG shifts: {shifts}")

    payload = dict(probedir=args.probedir, source_run=src, gate1_passed=drift_ok,
                   gas_references=gas, rows=rows,
                   note=man.get("note"), n_missing=len(missing), n_failed=len(failed))
    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        json.dump(payload, open(args.json, "w"), indent=2)
        print(f"\n-> {args.json}")


if __name__ == "__main__":
    main()
