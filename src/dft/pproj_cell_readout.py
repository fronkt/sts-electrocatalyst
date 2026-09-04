#!/usr/bin/env python3
"""P-PROJ-CELL readout: the Amendment 13 verdict in the ADOPTED 2x1v cell.

WRITTEN BEFORE THE OUTPUTS LANDED, with the array queued and zero outputs on
disk. A scorer authored while the jobs are pending cannot be tuned to the answer.

WHAT THIS ARM ASKS. A7.1 is a 1x1 statement: atomic 1.155 V / pls 2 against
ortho 1.642 V / pls 1, |d-eta| = 0.487 V. Block 1A adopted 2x1v, and in 2x1v the
ATOMIC projector already gives pls = 1 -- so the 2 -> 1 flip A7.1 attributes to
the projector is also what the CELL change produces at fixed projector. This is
the only calculation in the neighbourhood that can FALSIFY the headline rather
than measure it more precisely.

WHAT IS REGISTERED (docs/43, Amendment 13):

  A13.2  DISCLOSED NON-BLIND: the atomic leg is banked and its value was written
         into the registration IN ADVANCE -- eta = 0.9239810 V, pls = 1. Only the
         ortho leg is unmeasured. This script asserts that banked value and
         REFUSES if the re-derivation disagrees, so the disclosure is enforced
         rather than trusted.
  A13.3  NO NEW THRESHOLD. The bands are A7.1's own, inherited unchanged:
         FIRES > 0.10 V, NULL < 0.03 V, INTERMEDIATE between and never rounded.
         The pls comparison is reported, not scored.
  A13.4  FOUR OUTCOME BRANCHES, named in advance -- see BRANCHES below. Every one
         of the four states is reported whatever the outcome, and the result goes
         in the same table as A7.1's 1x1 pair so the two cells are always read
         together. A magnetisation mismatch between paired legs is a BRANCH
         MISMATCH, reported and never averaged away.
  A13.6  When the two legs differ in pls, d-eta is decomposed into its electronic
         and ZPE/TS-constants halves, and E_H2O does NOT cancel (weight -1).

  This arm is Cr-only and adds NOTHING to Amendment 12's five-metal denominator.

Usage:
  PYTHONPATH=src python src/dft/pproj_cell_readout.py [--json docs/figs/pproj_cell_readout.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# state -> banked 2x1v stem at the u715 rung
STEMS = {
    "slab":   "ref__2x1v__u715",
    "s0_O":   "s0_O__2x1v_mir__u715",
    "s0_OH":  "s0_OH__2x1v_mir__u715",
    "s0_OOH": "s0_OOH__2x1v_escape__u715",
}

FIRE_V = 0.10          # A7.1's own trigger, inherited unchanged (A13.3)
NULL_V = 0.03          # A7.1's own falsification floor, inherited unchanged

# A13.2 -- written into the registration before the ortho leg ran.
DISCLOSED_ATOMIC_ETA = 0.9239810476816457
DISCLOSED_ATOMIC_PLS = 1

# A7.1's banked 1x1 pair, for the side-by-side A13.4 requires.
ONE_BY_ONE = dict(eta_atomic=1.1554030190314686, pls_atomic=2,
                  eta_ortho=1.6422591936558275, pls_ortho=1,
                  abs_d_eta=0.48685617462435893)

BRANCHES = [
    ("FIRES", True,
     "the projector effect reproduces in the adopted cell in BOTH magnitude and "
     "mechanism; A7.1's finding generalises from 1x1 to the production cell"),
    ("FIRES", False,
     "the MAGNITUDE survives the cell change; the MECHANISM does not. 'The "
     "projector flips the rate-limiting step' becomes a 1x1-ONLY sentence and is "
     "scoped that way in every statement of A7.1 for the rest of the campaign"),
    ("INTERMEDIATE", None,
     "reported as INTERMEDIATE and never rounded. A7.1's magnitude is "
     "cell-dependent, and the report states that the effect is substantially "
     "smaller in the cell actually adopted"),
    ("NULL", None,
     "the projector is NOT a live variable in the adopted cell. A7.1 stands as a "
     "1x1 result only, is reported that way for the rest of the campaign, and THE "
     "HEADLINE IS RE-LED rather than defended"),
]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def atomic_out(state):
    return os.path.join(ROOT, "runs", "a0", "cell", STEMS[state] + ".out")


def ortho_out(state):
    return os.path.join(ROOT, "runs", "a0", "pproj_cell", STEMS[state] + "_ortho.out")


def totmag(path):
    val = None
    with open(path, errors="replace") as fh:
        for line in fh:
            if "total magnetization" in line:
                m = re.search(r"total magnetization\s*=\s*([-\d.]+)", line)
                if m:
                    val = float(m.group(1))
    return val


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--tol-mev", type=float, default=1.0,
                    help="tolerance on the A13.2 disclosed atomic eta")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    sys.path.insert(0, os.path.join(ROOT, "src"))
    from hea_oer.referencing import delta_G, ZPE_TS_CORRECTION, reference_energy
    from hea_oer.descriptors import oer_overpotential

    qc = _load("qe_qc")
    zpe = _load("zpe_decomposition")

    gas = {}
    for g in ("H2O", "H2"):
        p = os.path.join(ROOT, "runs", "Cr_slab", f"{g}.out")
        e = qc.trusted_energy_ev(p, strict=True) if os.path.exists(p) else None
        if e is None:
            sys.exit(f"REFUSING: gas reference {p} missing or failed QC")
        gas[g] = e

    E, mag, missing = {}, {}, []
    for st in STEMS:
        for leg, path in (("atomic", atomic_out(st)), ("ortho", ortho_out(st))):
            if not os.path.exists(path):
                missing.append(f"{st}__{leg}  ({os.path.relpath(path, ROOT)})")
                continue
            e = qc.trusted_energy_ev(path, strict=True)
            if e is None:
                missing.append(f"{st}__{leg}  FAILED QC")
                continue
            E[(st, leg)] = e
            mag[(st, leg)] = totmag(path)

    if missing:
        print("ARM INCOMPLETE -- nothing is scored (A13.4 reports all four states "
              "or none):")
        for x in missing:
            print(f"  MISSING  {x}")
        sys.exit(2)

    legs = {}
    for leg in ("atomic", "ortho"):
        dG = {sp: delta_G(E[("slab", leg)], E[(f"s0_{sp}", leg)], sp,
                          gas["H2O"], gas["H2"]) for sp in ("OH", "O", "OOH")}
        r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        dEl = {sp: E[(f"s0_{sp}", leg)] - E[("slab", leg)]
                   - reference_energy(sp, gas["H2O"], gas["H2"])
               for sp in ("OH", "O", "OOH")}
        rz = oer_overpotential(dEl["OH"], dEl["O"], dEl["OOH"])
        legs[leg] = dict(dG=dG, eta=r.overpotential, pls=r.potential_limiting_step,
                         steps=[r.dG1, r.dG2, r.dG3, r.dG4],
                         steps_electronic=[rz.dG1, rz.dG2, rz.dG3, rz.dG4])

    # ---- A13.2: the disclosed non-blind atomic leg is ENFORCED ---------------
    d_mev = (legs["atomic"]["eta"] - DISCLOSED_ATOMIC_ETA) * 1000.0
    if abs(d_mev) > args.tol_mev or legs["atomic"]["pls"] != DISCLOSED_ATOMIC_PLS:
        sys.exit(f"REFUSING: the atomic leg does not reproduce the value A13.2 "
                 f"disclosed in advance. Registered eta {DISCLOSED_ATOMIC_ETA:.7f} V "
                 f"pls {DISCLOSED_ATOMIC_PLS}; re-derived {legs['atomic']['eta']:.7f} V "
                 f"pls {legs['atomic']['pls']} ({d_mev:+.4f} meV). Either the "
                 f"extraction changed or the banked leg did; both are bugs.")

    d_eta = legs["ortho"]["eta"] - legs["atomic"]["eta"]
    a = abs(d_eta)
    band = "FIRES" if a > FIRE_V else ("NULL" if a < NULL_V else "INTERMEDIATE")
    pls_differs = legs["atomic"]["pls"] != legs["ortho"]["pls"]

    mismatch = [st for st in STEMS
                if mag[(st, "atomic")] is not None and mag[(st, "ortho")] is not None
                and abs(mag[(st, "atomic")] - mag[(st, "ortho")]) >= 0.5]

    print("=" * 88)
    print("P-PROJ-CELL -- Amendment 13. Cr, U = 7.15 eV, ADOPTED 2x1v cell.")
    print("=" * 88)
    print(f"\nA13.2 disclosed-non-blind check: atomic eta re-derives to "
          f"{legs['atomic']['eta']:.7f} V, pls {legs['atomic']['pls']} "
          f"({d_mev:+.4f} meV vs the registered value)  OK")

    print(f"\n{'state':8s} {'E_atomic (eV)':>15s} {'E_ortho (eV)':>15s} "
          f"{'dE (meV)':>11s}  {'mag at/or':>11s}  branch")
    for st in STEMS:
        ea, eo = E[(st, "atomic")], E[(st, "ortho")]
        ma, mo = mag[(st, "atomic")], mag[(st, "ortho")]
        ok = st not in mismatch
        print(f"{st:8s} {ea:15.4f} {eo:15.4f} {(eo-ea)*1000:11.1f}  "
              f"{ma!s:>5}/{mo!s:<5}  {'MATCH' if ok else 'BRANCH MISMATCH'}")

    print(f"\n{'leg':8s} {'pls':>4s} {'eta (V)':>10s} | "
          f"{'step1':>10s} {'step2':>10s} {'step3':>10s} {'step4':>10s}")
    for leg in ("atomic", "ortho"):
        L = legs[leg]
        print(f"{leg:8s} {L['pls']:4d} {L['eta']:10.7f} | "
              + " ".join(f"{s:10.7f}" for s in L["steps"]))

    print(f"\n  d-eta (2x1v) = {d_eta:+.7f} V   |d-eta| = {a:.7f} V   -> {band}")
    print(f"  pls {legs['atomic']['pls']} -> {legs['ortho']['pls']}  "
          f"({'DIFFERS' if pls_differs else 'SAME'})")

    # ---- A13.4: the branch, named in advance --------------------------------
    chosen = None
    for b_band, b_pls, text in BRANCHES:
        if b_band != band:
            continue
        if b_pls is None or b_pls == pls_differs:
            chosen = (b_band, b_pls, text)
            break
    print("\n" + "-" * 88)
    print("A13.4 OUTCOME BRANCH (named in advance)")
    print("-" * 88)
    print(f"  band={band}  pls_differs={pls_differs}")
    print(f"  -> {chosen[2] if chosen else 'NO BRANCH MATCHED -- this is a bug'}")

    # ---- A13.4: the two cells, always read together -------------------------
    print("\n  THE TWO CELLS, side by side (A13.4 anti-selection):")
    print(f"    {'cell':6s} {'eta_atomic':>11s} {'pls':>4s} {'eta_ortho':>11s} "
          f"{'pls':>4s} {'|d-eta|':>9s}")
    print(f"    {'1x1':6s} {ONE_BY_ONE['eta_atomic']:11.4f} "
          f"{ONE_BY_ONE['pls_atomic']:4d} {ONE_BY_ONE['eta_ortho']:11.4f} "
          f"{ONE_BY_ONE['pls_ortho']:4d} {ONE_BY_ONE['abs_d_eta']:9.4f}   (A7.1)")
    print(f"    {'2x1v':6s} {legs['atomic']['eta']:11.4f} {legs['atomic']['pls']:4d} "
          f"{legs['ortho']['eta']:11.4f} {legs['ortho']['pls']:4d} {a:9.4f}   (this arm)")

    # ---- A13.6 decomposition ------------------------------------------------
    decomp = None
    if pls_differs:
        c = zpe.step_constants(dict(ZPE_TS_CORRECTION))
        pa, po = legs["atomic"]["pls"], legs["ortho"]["pls"]
        const = c[po - 1] - c[pa - 1]
        elec = (legs["ortho"]["steps_electronic"][po - 1]
                - legs["atomic"]["steps_electronic"][pa - 1])
        decomp = dict(electronic_eV=elec, constants_eV=const,
                      constants_share=(const / d_eta) if d_eta else None,
                      closure=(elec + const) - d_eta)
        print(f"\n  A13.6 decomposition (legs differ in pls):")
        print(f"    electronic {elec:+.7f} eV + constants {const:+.7f} eV "
              f"= {elec+const:+.7f}  (closure {decomp['closure']:+.2e})")
        print(f"    E_H2O does NOT cancel in this d-eta (weight -1); E_H2 does.")
    else:
        print(f"\n  A13.6: both legs share pls {legs['atomic']['pls']}, so the ZPE/TS "
              f"constants cancel exactly and d-eta is purely electronic.")
        print(f"    Both gas references cancel in this case.")

    if mismatch:
        print(f"\n  BRANCH MISMATCH on: {', '.join(mismatch)} -- reported, never "
              f"averaged away (A13.4).")

    print("\n  SCOPE: Cr-only. This arm scores no class row and adds NOTHING to "
          "Amendment 12's\n  five-metal denominator; Cr is CALIBRATION there and "
          "remains so. It is a robustness\n  test of A7.1 on A7.1's own material.")

    if args.json:
        payload = dict(
            cell="2x1v", U=7.15, metal="Cr",
            gas=gas, legs=legs, d_eta_V=d_eta, abs_d_eta_V=a, band=band,
            pls_differs=pls_differs, branch=(chosen[2] if chosen else None),
            disclosed_atomic=dict(eta=DISCLOSED_ATOMIC_ETA,
                                  pls=DISCLOSED_ATOMIC_PLS,
                                  rederivation_drift_meV=d_mev),
            one_by_one=ONE_BY_ONE, zpe_decomposition=decomp,
            branch_mismatch=mismatch,
            thresholds=dict(fire_V=FIRE_V, null_V=NULL_V,
                            inherited_from="A7.1 via A13.3, no new threshold"),
        )
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"\n  json -> {os.path.relpath(args.json, ROOT)}")


if __name__ == "__main__":
    main()
