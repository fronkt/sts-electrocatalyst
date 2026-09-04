#!/usr/bin/env python3
"""How much of A7.1's projector delta-eta is DFT, and how much is a constants table.

WHY THIS EXISTS

A7.1 / P-PROJ is the campaign's flagship: Cr, U = 7.15 eV, 1x1, HUBBARD (atomic)
against (ortho-atomic) at byte-identical geometry, |d-eta| = 0.487 V with the
potential-limiting step flipping 2 -> 1. The number is correct and the
registration fired honestly.

But eta is not a pure DFT quantity. Every CHE ladder step carries an additive
constant from `hea_oer.referencing.ZPE_TS_CORRECTION` -- the conventional
ZPE - T*dS corrections {OH: 0.35, O: 0.05, OOH: 0.40} eV of Man 2011 /
Valdes 2008. Those constants are NOT recomputed per projector; they are a fixed
table. So when the projector flips WHICH step is rate-limiting, it also swaps
which constant lands in eta -- and that swap is arithmetic, not physics.

This script separates the two, from the raw .out files, and reports:

  1. the exact electronic and constants halves of d-eta;
  2. the sensitivity of d-eta to the three constants (a +/- band);
  3. how far the constants would have to move to change either leg's pls --
     which is the question that decides whether the mechanism claim is robust.

NOTHING HERE IS A NEW MEASUREMENT. It is a decomposition of banked numbers, and
it is reported as such. It does not change any verdict: A7.1 FIRED on |d-eta|
and it still does. What it changes is what may honestly be SAID about the 0.487.

ONE SOURCE OF TRUTH. Energy extraction, the gas references, the QC gate and the
state->path mapping are imported from `pproj_readout.py`, the script that
produced the registered readout. This file adds no second extraction path; if
the two ever disagreed, that would itself be the bug.

Usage:
  PYTHONPATH=src python src/dft/zpe_decomposition.py [--json docs/figs/zpe_decomposition.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def step_constants(z: dict) -> tuple[float, float, float, float]:
    """The additive ZPE/TS content of each of the four CHE ladder steps.

    dG1 = dG_OH                 ->  +z_OH
    dG2 = dG_O   - dG_OH        ->  z_O   - z_OH
    dG3 = dG_OOH - dG_O         ->  z_OOH - z_O
    dG4 = 4.92   - dG_OOH       ->  -z_OOH

    They sum to zero by construction: the ladder totals 4.92 eV whatever the
    table says. The constants can only move WHICH step is largest, and by how
    much -- never the total.
    """
    return (z["OH"], z["O"] - z["OH"], z["OOH"] - z["O"], -z["OOH"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--delta", type=float, default=0.05,
                    help="per-constant sensitivity half-width in eV (default 0.05)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    sys.path.insert(0, os.path.join(ROOT, "src"))
    from hea_oer.referencing import ZPE_TS_CORRECTION, reference_energy
    from hea_oer.descriptors import G_TOTAL, OER_EQUILIBRIUM_V, oer_overpotential

    pp = _load("pproj_readout")
    qc = _load("qe_qc")

    # ---- gas references and the eight SCFs, through pproj_readout's own gate --
    gas = {}
    for g in ("H2O", "H2"):
        p = os.path.join(ROOT, "runs", "Cr_slab", f"{g}.out")
        e = qc.trusted_energy_ev(p, strict=True) if os.path.exists(p) else None
        if e is None:
            sys.exit(f"REFUSING: gas reference {p} missing or failed QC")
        gas[g] = e

    E = {}
    for st in pp.STATES:
        for leg in pp.LEGS:
            p = pp._outfile(st, leg)
            e = qc.trusted_energy_ev(p, strict=True) if os.path.exists(p) else None
            if e is None:
                sys.exit(f"REFUSING: {st}__{leg} missing or failed QC ({p})")
            E[(st, leg)] = e

    # ---- the ELECTRONIC ladder: every constant set to zero --------------------
    # dE_X = E(adslab) - E(slab) - (a*E_H2O + b*E_H2). This is delta_G with the
    # ZPE/TS term removed, so dG_X = dE_X + z_X exactly.
    elec = {}
    for leg in pp.LEGS:
        e_slab = E[("slab", leg)]
        dE = {sp: E[(f"s0_{sp}", leg)] - e_slab - reference_energy(sp, gas["H2O"], gas["H2"])
              for sp in ("OH", "O", "OOH")}
        elec[leg] = dE

    def ladder(leg: str, z: dict):
        dE = elec[leg]
        dG = {sp: dE[sp] + z[sp] for sp in ("OH", "O", "OOH")}
        r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        return r

    z0 = dict(ZPE_TS_CORRECTION)
    zzero = {"OH": 0.0, "O": 0.0, "OOH": 0.0}

    print("=" * 78)
    print("A7.1 delta-eta: the electronic half and the constants half")
    print("=" * 78)
    print(f"\ngas references (runs/Cr_slab, shared by both legs, cancel exactly in d-eta):")
    print(f"  H2O {gas['H2O']:.6f} eV   H2 {gas['H2']:.6f} eV")

    print(f"\nZPE_TS_CORRECTION (src/hea_oer/referencing.py:18), Man 2011 / Valdes 2008:")
    print(f"  {z0}")
    c0 = step_constants(z0)
    print(f"\nper-step constants content  c1..c4 = "
          f"{c0[0]:+.4f} {c0[1]:+.4f} {c0[2]:+.4f} {c0[3]:+.4f}  (sum {sum(c0):+.4f})")

    rows = {}
    print(f"\n{'leg':7s} {'pls':>4s} {'eta (V)':>10s} | "
          f"{'step1':>10s} {'step2':>10s} {'step3':>10s} {'step4':>10s}")
    for leg in pp.LEGS:
        r = ladder(leg, z0)
        rz = ladder(leg, zzero)
        rows[leg] = dict(
            eta=r.overpotential, pls=r.potential_limiting_step,
            steps=[r.dG1, r.dG2, r.dG3, r.dG4],
            steps_electronic=[rz.dG1, rz.dG2, rz.dG3, rz.dG4],
            pls_electronic_only=rz.potential_limiting_step,
            eta_electronic_only=rz.overpotential,
        )
        print(f"{leg:7s} {r.potential_limiting_step:4d} {r.overpotential:10.7f} | "
              f"{r.dG1:10.7f} {r.dG2:10.7f} {r.dG3:10.7f} {r.dG4:10.7f}")

    pa, po = rows["atomic"]["pls"], rows["ortho"]["pls"]
    d_eta = rows["ortho"]["eta"] - rows["atomic"]["eta"]

    # eta = max step - 1.23; the winning step = electronic part + its constant.
    e_win_a = rows["atomic"]["steps_electronic"][pa - 1]
    e_win_o = rows["ortho"]["steps_electronic"][po - 1]
    electronic = e_win_o - e_win_a
    constants = c0[po - 1] - c0[pa - 1]

    print("\n" + "-" * 78)
    print("DECOMPOSITION")
    print("-" * 78)
    print(f"  atomic pls = {pa}, so eta_atomic carries constant c{pa} = {c0[pa-1]:+.4f} eV")
    print(f"  ortho  pls = {po}, so eta_ortho  carries constant c{po} = {c0[po-1]:+.4f} eV")
    print()
    print(f"  d-eta = eta_ortho - eta_atomic         = {d_eta:+.7f} V")
    print(f"    electronic (raw DFT, both constants 0) = {electronic:+.7f} eV"
          f"   <-- {'ortho LOWER' if electronic < 0 else 'ortho HIGHER'}")
    print(f"    constants  (c{po} - c{pa})                  = {constants:+.7f} eV")
    print(f"    sum                                     = {electronic + constants:+.7f}")
    resid = (electronic + constants) - d_eta
    print(f"    closure residual                        = {resid:+.2e}  "
          f"{'EXACT' if abs(resid) < 1e-9 else 'MISMATCH -- do not report'}")
    if abs(resid) >= 1e-9:
        sys.exit("REFUSING: the decomposition does not close. Extraction bug.")

    share = constants / d_eta
    print(f"\n  the constants table accounts for {share*100:.1f} % of d-eta,")
    print(f"  and the raw DFT difference has the OPPOSITE SIGN"
          if electronic * d_eta < 0 else "")

    # ---- SENSITIVITY ---------------------------------------------------------
    # d-eta = (electronic) + c[po] - c[pa]. With pls fixed this is exactly linear
    # in the three constants; the coefficients are what matter and they are not
    # obvious, so they are printed rather than asserted.
    delta = args.delta
    print("\n" + "-" * 78)
    print(f"SENSITIVITY: each constant independently perturbed by +/- {delta:.2f} eV")
    print("-" * 78)

    coeffs = {}
    for sp in ("OH", "O", "OOH"):
        zp = dict(z0); zp[sp] += 1.0
        cp = step_constants(zp)
        coeffs[sp] = (cp[po - 1] - cp[pa - 1]) - constants
    print(f"  d(d-eta)/dz_OH  = {coeffs['OH']:+.1f}")
    print(f"  d(d-eta)/dz_O   = {coeffs['O']:+.1f}")
    print(f"  d(d-eta)/dz_OOH = {coeffs['OOH']:+.1f}"
          f"   <-- zero: neither leg is limited by step 3 or 4")

    # exact envelope over the cube, computed by full recomputation (not by the
    # linear form), so a pls change inside the cube would show up as a kink.
    span = []
    for signs in itertools.product((-1, 0, +1), repeat=3):
        z = {sp: z0[sp] + s * delta for sp, s in zip(("OH", "O", "OOH"), signs)}
        ra, ro = ladder("atomic", z), ladder("ortho", z)
        span.append((ro.overpotential - ra.overpotential, signs,
                     ra.potential_limiting_step, ro.potential_limiting_step))
    lo, hi = min(span), max(span)
    pls_stable = all(s[2] == pa and s[3] == po for s in span)
    print(f"\n  d-eta over the full +/-{delta:.2f} eV cube (27 corners, recomputed):")
    print(f"    min {lo[0]:+.7f} V at (z_OH,z_O,z_OOH) offsets {lo[1]}")
    print(f"    max {hi[0]:+.7f} V at offsets {hi[1]}")
    print(f"    half-width {(hi[0]-lo[0])/2:.7f} V about the nominal {d_eta:+.7f} V")
    print(f"    pls assignment {'UNCHANGED at every corner' if pls_stable else 'CHANGES -- band is discontinuous'}")

    # ---- how far would the constants have to move to flip a pls? -------------
    print("\n" + "-" * 78)
    print("ROBUSTNESS OF THE MECHANISM CLAIM (the pls flip)")
    print("-" * 78)
    margins = {}
    for leg in pp.LEGS:
        st = rows[leg]["steps"]
        win = max(st)
        runner = max(v for i, v in enumerate(st) if i != st.index(win))
        margins[leg] = win - runner
        print(f"  {leg:7s} pls {rows[leg]['pls']} leads the runner-up by "
              f"{win - runner:.4f} eV")
    # worst case: the constants enter each step with coefficients in {-1,0,1,2}
    # of the three z; a symmetric +/-d perturbation moves a step-difference by at
    # most (sum of |coefficient differences|) * d. Computed exactly by search.
    print("\n  smallest uniform half-width d (eV) that can flip a leg's pls,")
    print("  searched over the 27 corners of the cube at increasing d:")
    for leg in pp.LEGS:
        found = None
        d = 0.0
        while d < 2.0:
            d += 0.001
            flipped = False
            for signs in itertools.product((-1, 0, +1), repeat=3):
                z = {sp: z0[sp] + s * d for sp, s in zip(("OH", "O", "OOH"), signs)}
                if ladder(leg, z).potential_limiting_step != rows[leg]["pls"]:
                    flipped = True
                    break
            if flipped:
                found = d
                break
        margins[leg + "_flip_d"] = found
        print(f"    {leg:7s} needs d >= {found:.3f} eV "
              f"({found/delta:.1f}x the {delta:.2f} eV sensitivity band)")

    print("\n" + "=" * 78)
    print("WHAT MAY BE SAID")
    print("=" * 78)
    print(f"""
  * |d-eta| = {abs(d_eta):.4f} V is correct and A7.1's verdict is unchanged.
  * {share*100:.1f} % of it is the swap of a fixed literature constant, and the raw
    DFT difference is {electronic:+.4f} eV -- the opposite sign. Both belong in
    any sentence that quotes the 0.487.
  * The magnitude carries a +/-{(hi[0]-lo[0])/2:.2f} V band under +/-{delta:.2f} eV on the
    constants. Note the coefficient on z_OH is {coeffs['OH']:+.0f}, not 1, so the band is
    wider than the per-constant perturbation.
  * The MECHANISM claim is robust: flipping either leg's pls needs the constants
    moved by >= {min(margins['atomic_flip_d'], margins['ortho_flip_d']):.3f} eV, which is far outside any
    defensible uncertainty on a ZPE table.
  * The constants were never recomputed per projector, even though the projector
    shifts absolute magnetisation on these states. That is a stated
    approximation, not a hidden one.
""")

    if args.json:
        payload = dict(
            gas=gas,
            zpe_ts_correction=z0,
            step_constants=list(c0),
            legs=rows,
            d_eta_V=d_eta,
            abs_d_eta_V=abs(d_eta),
            electronic_eV=electronic,
            constants_eV=constants,
            constants_share_of_d_eta=share,
            closure_residual=resid,
            sensitivity=dict(
                half_width_eV=delta,
                coefficients={k: v for k, v in coeffs.items()},
                d_eta_min_V=lo[0], d_eta_min_offsets=list(lo[1]),
                d_eta_max_V=hi[0], d_eta_max_offsets=list(hi[1]),
                band_half_width_V=(hi[0] - lo[0]) / 2,
                pls_stable_over_cube=pls_stable,
            ),
            pls_robustness={
                "atomic_margin_eV": margins["atomic"],
                "ortho_margin_eV": margins["ortho"],
                "atomic_flip_needs_eV": margins["atomic_flip_d"],
                "ortho_flip_needs_eV": margins["ortho_flip_d"],
            },
            note=("Decomposition of banked numbers; no new calculation. A7.1's "
                  "verdict is unchanged. G_TOTAL=%.2f, U_eq=%.2f."
                  % (G_TOTAL, OER_EQUILIBRIUM_V)),
        )
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"  json -> {os.path.relpath(args.json, ROOT)}")


if __name__ == "__main__":
    main()
