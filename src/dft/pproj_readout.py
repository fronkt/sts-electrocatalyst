#!/usr/bin/env python3
"""P-PROJ readout: the A7.1 projector-pairing verdict (docs/43 :1325-1345).

Registered test, verbatim: "two Cr fixed-geometry SCF sets at U = 7.15 eV, 1x1
(matching A0), `HUBBARD (atomic)` vs `(ortho-atomic)`, all four states.
PREDICTION (blind): |d-eta(Cr)| > 0.10 V. FALSIFIED below 0.03 V, in which case
the projector is not a live variable at this U and Xu's supercell linear-response
value may be imported as a literature anchor."

The eight SCFs: six from runs/a0/p_proj (array 20178326, 2026-08-27) plus the
two banked S0 gate-(e) decks in runs/s0/e_proj (the *O pair). Scoring follows
runs/a0/m_pproj.txt verbatim:

  - per state: converged (no "convergence NOT achieved", a final "!" energy, no
    "Error in routine" block) -- enforced here by qe_qc.trusted_energy_ev strict,
    the same gate production energies pass;
  - dE = E_atomic - E_ortho at identical geometry and U, with the magnetization
    pair alongside; a magnetization mismatch between the legs of a pair is a
    BRANCH MISMATCH and is reported as such, never averaged away;
  - the eta consequence -- the thing A7.1 predicts on -- is assembled from all
    four states by the CHE ladder (hea_oer.referencing.delta_G +
    hea_oer.descriptors.oer_overpotential), per projector leg, NOT from any
    single dE.

Gas references are reused from runs/Cr_slab exactly as probe_eta.py reuses them:
H2O and H2 run in a Martyna-Tuckerman box with assume_isolated, so no Hubbard
card, projector choice, slab dipole or cell height touches them -- reuse across
the projector pair is exact, and both legs subtract the SAME gas numbers, so the
gas reference cancels in d-eta identically. They are still QC'd here; the script
refuses to score if they fail.

CROSS-CHECK. runs/s0/e_proj/README recorded the banked *O pair's dE as
+0.27021297 Ry (+3676.6 meV). This script re-derives that number from the .out
files; disagreement beyond 0.1 meV means an extraction bug, and the script says
so rather than reporting.

Usage:
  PYTHONPATH=src python src/dft/pproj_readout.py [--json results/pproj.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys

RY_EV = 13.605693122994  # QE's own Ry->eV
STATES = ("slab", "s0_OH", "s0_O", "s0_OOH")
LEGS = ("atomic", "ortho")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

BANKED_O_DE_RY = 0.27021297  # runs/s0/e_proj/README.md, 2026-08-16


def _qc():
    spec = importlib.util.spec_from_file_location("qe_qc", os.path.join(HERE, "qe_qc.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _outfile(state: str, leg: str) -> str:
    if state == "s0_O":
        return os.path.join(ROOT, "runs", "s0", "e_proj", f"s0_O__u715_{leg}.out")
    return os.path.join(ROOT, "runs", "a0", "p_proj", f"{state}__u715_{leg}.out")


def _magtot(path: str):
    """Final 'total magnetization' (Bohr mag/cell), None if absent."""
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
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    from hea_oer.referencing import delta_G
    from hea_oer.descriptors import oer_overpotential

    qc = _qc()

    # --- gas references, reused from the production Cr run, QC'd here ---------
    gas = {}
    for g in ("H2O", "H2"):
        p = os.path.join(ROOT, "runs", "Cr_slab", f"{g}.out")
        e = qc.trusted_energy_ev(p, strict=True) if os.path.exists(p) else None
        if e is None:
            sys.exit(f"REFUSING: gas reference {p} missing or failed QC")
        gas[g] = e
    print(f"gas references reused from runs/Cr_slab: "
          f"H2O {gas['H2O']:.4f} eV, H2 {gas['H2']:.4f} eV\n")

    # --- the eight SCFs, all QC'd ---------------------------------------------
    E, mag = {}, {}
    bad = []
    for st in STATES:
        for leg in LEGS:
            p = _outfile(st, leg)
            if not os.path.exists(p):
                bad.append((st, leg, "missing"))
                continue
            e = qc.trusted_energy_ev(p, strict=True)
            if e is None:
                rec = qc.scan(p, None)
                bad.append((st, leg, f"{rec['verdict']}: {'; '.join(rec['reasons'])[:80]}"))
                continue
            E[(st, leg)] = e
            mag[(st, leg)] = _magtot(p)
    if bad:
        for st, leg, why in bad:
            print(f"FAILED: {st}__{leg}  {why}")
        sys.exit("REFUSING: the pairing needs all 8 converged SCFs.")

    # --- per-state dE and the magnetization pair ------------------------------
    print(f"{'state':8s} {'E_atomic (eV)':>14s} {'E_ortho (eV)':>14s} "
          f"{'dE (Ry)':>11s} {'dE (meV)':>10s} {'mag at/or':>12s}  branch")
    mismatch = []
    per_state = {}
    for st in STATES:
        ea, eo = E[(st, "atomic")], E[(st, "ortho")]
        de_ev = ea - eo
        ma, mo = mag[(st, "atomic")], mag[(st, "ortho")]
        same = (ma is not None and mo is not None and abs(ma - mo) < 0.5)
        if not same:
            mismatch.append(st)
        per_state[st] = dict(E_atomic_ev=ea, E_ortho_ev=eo, dE_ev=de_ev,
                             mag_atomic=ma, mag_ortho=mo, branch_match=same)
        print(f"{st:8s} {ea:14.4f} {eo:14.4f} {de_ev/RY_EV:11.8f} {de_ev*1000:10.1f} "
              f"{ma!s:>5}/{mo!s:<5}  {'MATCH' if same else 'BRANCH MISMATCH'}")

    # --- cross-check the banked *O pair ---------------------------------------
    d = per_state["s0_O"]["dE_ev"] / RY_EV - BANKED_O_DE_RY
    if abs(d * RY_EV * 1000) > 0.1:
        sys.exit(f"EXTRACTION BUG: banked *O dE {BANKED_O_DE_RY} Ry, "
                 f"re-derived {per_state['s0_O']['dE_ev']/RY_EV:.8f} Ry "
                 f"(diff {d*RY_EV*1000:+.3f} meV > 0.1 meV). Not reporting.")
    print(f"\ncross-check: banked *O dE reproduced to {d*RY_EV*1000:+.4f} meV  OK")

    # --- the eta consequence, per projector leg -------------------------------
    legs = {}
    print(f"\n{'leg':8s} {'dG_OH':>8s} {'dG_O':>8s} {'dG_OOH':>8s} "
          f"{'dG_O-dG_OH':>11s} {'eta (V)':>8s} {'pls':>4s}")
    for leg in LEGS:
        e_slab = E[("slab", leg)]
        dG = {sp: delta_G(e_slab, E[(f"s0_{sp}", leg)], sp, gas["H2O"], gas["H2"])
              for sp in ("OH", "O", "OOH")}
        r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        legs[leg] = dict(dG_OH=dG["OH"], dG_O=dG["O"], dG_OOH=dG["OOH"],
                         descriptor=dG["O"] - dG["OH"],
                         eta=r.overpotential, pls=r.potential_limiting_step,
                         steps=[r.dG1, r.dG2, r.dG3, r.dG4])
        print(f"{leg:8s} {dG['OH']:8.3f} {dG['O']:8.3f} {dG['OOH']:8.3f} "
              f"{dG['O']-dG['OH']:11.3f} {r.overpotential:8.3f} "
              f"{r.potential_limiting_step:4d}")

    d_eta = legs["atomic"]["eta"] - legs["ortho"]["eta"]
    print(f"\nd-eta(Cr) = eta_atomic - eta_ortho = {d_eta:+.4f} V   "
          f"|d-eta| = {abs(d_eta):.4f} V")

    if abs(d_eta) > 0.10:
        verdict = "FIRES"
        note = ("|d-eta| > 0.10 V: the prediction fires. Per A7.1 the fifth grid "
                "point is labelled PROJECTOR-MISMATCHED, the whole eta(U) grid "
                "runs in ONE projector, and the projector delta becomes its own "
                "labelled sub-row.")
    elif abs(d_eta) < 0.03:
        verdict = "FALSIFIED"
        note = ("|d-eta| < 0.03 V: the projector is not a live variable at this "
                "U; Xu's supercell linear-response value may be imported as a "
                "literature anchor.")
    else:
        verdict = "NEITHER BIN"
        note = ("0.03 <= |d-eta| <= 0.10 V: the registration names no bin here; "
                "reported as-is, not rounded toward either.")
    print(f"\nA7.1 VERDICT: {verdict}")
    print(note)
    if mismatch:
        print(f"\nBRANCH MISMATCH on: {', '.join(mismatch)} -- the paired dE for "
              f"these states compares different magnetic branches; reported, not averaged.")

    if args.json:
        payload = dict(gas=gas, per_state=per_state, legs=legs,
                       d_eta_V=d_eta, abs_d_eta_V=abs(d_eta),
                       verdict=verdict, branch_mismatch=mismatch)
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
