#!/usr/bin/env python3
"""P-PROJ-6 readout: the Amendment 12 verdict over the six-metal roster.

WRITTEN BEFORE THE OUTPUTS LANDED. That ordering is deliberate and is the whole
point of the arm: a scorer authored while the array is still queued cannot be
tuned to the answer. Committed 2026-09-04 with the array at 14/24 JOB DONE and
the pproj_cell array not started.

WHAT IT SCORES, verbatim from the registered text (docs/43, Amendment 12):

  A12.R1  PRIMARY: d-eta_M = eta_M(ortho) - eta_M(atomic), per metal, at fixed
          geometry and U = 7.50. R_M is a DIAGNOSTIC with no verdict attached.
          SECONDARY, reported not scored: whether the pls differs between legs.
  A12.R2  DENOMINATOR IS FIVE: Mn, Fe, Ti, Ru, Ir. Cr is CALIBRATION (post-hoc),
          reported in every table, always labelled, EXCLUDED FROM EVERY COUNT.
  A12.R3  BANDS: FIRES if |d-eta| > 0.10 V; NULL if < 0.03 V; INTERMEDIATE
          between, reported as such and NEVER rounded to either side.
          Class verdict on the count of FIRES out of five:
            5 or 4 -> CONFIRMED       3 or 2 -> MIDDLE BAND (no class claim)
            1      -> NOT MET         0      -> FALSIFIED
  A12.R4  ANTI-SELECTION: all five blind metals in every table, always, with
          d-eta, band, pls comparison and R_M. No subset may be quoted alone and
          no metal may be dropped for a reason discovered after the outcome.
  A12.R5  PP CONFOUND: firing set exactly {Mn, Ti, Ir} (every ultrasoft metal and
          no other) -> DECLARED CONFOUNDED, no class claim. Symmetric case
          {Fe, Ru} carries the same declaration.
  A12.R6  SPIN CONFOUND: firing set exactly {Mn, Fe} or exactly {Ti, Ru, Ir} ->
          same declaration. k-mesh is not uniform across the roster and any
          cross-metal table must say so on its face.

  A13.6   Every d-eta whose two legs have DIFFERENT pls is decomposed into its
          electronic and ZPE/TS-constants halves, and carries the gas-reference
          note: when the pls differ, E_H2O does NOT cancel (weight -1) even
          though E_H2 does. This applies to this table, not only to A7.1.

REFUSALS, so a partial array cannot be read as a result:
  * any of the 24 ortho outputs missing or failing QC  -> REFUSE
  * any banked atomic partner missing or failing QC    -> REFUSE
  * a re-derived atomic eta disagreeing with the banked docs/figs/a0main_readout
    .json rung by more than --tol-mev                  -> REFUSE (extraction bug)
Both legs are re-derived from raw .out through ONE code path, and the atomic leg
is then cross-checked against the banked readout, so the pairing cannot silently
compare two different extractions.

Usage:
  PYTHONPATH=src python src/dft/pproj6_readout.py [--json docs/figs/pproj6_readout.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

METALS = ["Cr", "Mn", "Fe", "Ti", "Ru", "Ir"]
BLIND = ["Mn", "Fe", "Ti", "Ru", "Ir"]          # A12.R2: Cr is NOT here
CALIBRATION = "Cr"
STATES = ("slab", "s0_O", "s0_OH", "s0_OOH")
RUNG = "u750"
U_VALUE = 7.50

FIRE_V = 0.10        # A12.R3, inherited from A7.1
NULL_V = 0.03        # A12.R3, inherited from A7.1

# A12.R5 / A12.R6, from the UPF census recorded in docs/43's error ledger.
PP_FAMILY = {"Cr": "ultrasoft", "Mn": "ultrasoft", "Ti": "ultrasoft",
             "Ir": "ultrasoft", "Fe": "PAW", "Ru": "norm-conserving"}
NSPIN = {"Cr": 2, "Mn": 2, "Fe": 2, "Ti": 1, "Ru": 1, "Ir": 1}

# Gas reference directory per metal (a0main_readout.py's own mapping).
GAS_RUN = {"Cr": "Cr_slab", "Mn": "Mn_slab", "Fe": "Fe_slab",
           "Ti": "Ti_slab", "Ru": "Ru_anchor", "Ir": "Ir_anchor"}

BANKED = os.path.join(ROOT, "docs", "figs", "a0main_readout.json")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ortho_out(metal, state):
    return os.path.join(ROOT, "runs", "a0", "pproj6", metal,
                        f"{state}__{RUNG}_ortho.out")


def atomic_out(metal, state):
    return os.path.join(ROOT, "runs", "a0", "main", metal, f"{state}__{RUNG}.out")


def r_diagnostic(rows, dG_ortho):
    """A12.R1's DIAGNOSTIC R_M: RMS residual of a one-parameter U-shift fit.

    Slide the metal's own banked ATOMIC dG(U) curves along U and ask how well any
    single shift reproduces the ORTHO leg's three dG. Reported per metal with NO
    verdict attached: a small R does not license 'the projector is a
    reparameterisation of U', and a large one does not falsify anything. The
    informative part is usually not R but whether the implied shift is
    single-valued across the three observables -- so that spread is returned too.
    """
    us = sorted(r["u"] for r in rows)
    if len(us) < 2:
        return None
    lo, hi = us[0], us[-1]
    by_u = {r["u"]: r for r in rows}

    def interp(u, key):
        if u <= lo:
            return by_u[lo][key]
        if u >= hi:
            return by_u[hi][key]
        prev = max(x for x in us if x <= u)
        nxt = min(x for x in us if x >= u)
        if prev == nxt:
            return by_u[prev][key]
        f = (u - prev) / (nxt - prev)
        return by_u[prev][key] + f * (by_u[nxt][key] - by_u[prev][key])

    # dG_ortho is species-keyed ("OH"/"O"/"OOH"); the banked rows use "dG_<sp>".
    species = ("OH", "O", "OOH")
    target = {"dG_" + sp: dG_ortho[sp] for sp in species}
    keys = tuple(target)
    best = None
    steps = int(round((hi - lo) / 0.001))
    for i in range(steps + 1):
        u = lo + i * 0.001
        ss = sum((interp(u, k) - target[k]) ** 2 for k in keys)
        rms = (ss / len(keys)) ** 0.5
        if best is None or rms < best[0]:
            best = (rms, u)
    rms, u_opt = best

    # Per-observable implied shift: the U at which that ONE curve matches.
    implied = {}
    for k in keys:
        b = None
        for i in range(steps + 1):
            u = lo + i * 0.001
            d = abs(interp(u, k) - target[k])
            if b is None or d < b[0]:
                b = (d, u)
        implied[k] = dict(u=b[1], residual=b[0],
                          at_edge=(abs(b[1] - lo) < 1e-9 or abs(b[1] - hi) < 1e-9))
    span = max(v["u"] for v in implied.values()) - min(v["u"] for v in implied.values())
    return dict(rms_eV=rms, u_opt=u_opt, grid=[lo, hi],
                optimum_at_grid_edge=(abs(u_opt - lo) < 1e-9 or abs(u_opt - hi) < 1e-9),
                implied_shift_per_observable=implied,
                implied_shift_span_eV=span,
                note=("DIAGNOSTIC ONLY, no verdict attached (A12.R1). A threshold on "
                      "R would derive from its own null (0.0035 eV interpolation "
                      "floor), never from A7.1's volts."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--tol-mev", type=float, default=5.0,
                    help="atomic re-derivation vs banked readout tolerance")
    ap.add_argument("--allow-partial", action="store_true",
                    help="report what has landed WITHOUT scoring a class verdict")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    sys.path.insert(0, os.path.join(ROOT, "src"))
    from hea_oer.referencing import delta_G, ZPE_TS_CORRECTION, reference_energy
    from hea_oer.descriptors import oer_overpotential

    qc = _load("qe_qc")
    zpe = _load("zpe_decomposition")

    banked = json.load(open(BANKED))["metals"]

    # ---- collect, refusing on anything incomplete ---------------------------
    missing, badqc = [], []
    E = {}
    for m in METALS:
        for st in STATES:
            for leg, path in (("ortho", ortho_out(m, st)), ("atomic", atomic_out(m, st))):
                if not os.path.exists(path):
                    missing.append(f"{m}/{st}__{leg}")
                    continue
                e = qc.trusted_energy_ev(path, strict=True)
                if e is None:
                    badqc.append(f"{m}/{st}__{leg}")
                    continue
                E[(m, st, leg)] = e

    if missing or badqc:
        print("INCOMPLETE ARM")
        for x in missing:
            print(f"  MISSING  {x}")
        for x in badqc:
            print(f"  FAILED QC {x}")
        if not args.allow_partial:
            sys.exit("REFUSING to score: A12.R4's anti-selection clause requires all "
                     "five blind metals in every table. Re-run with --allow-partial "
                     "for a progress view that scores NOTHING.")
        print("\n--allow-partial: progress view only. NO class verdict is computed.\n")

    gas = {}
    for m in METALS:
        g = {}
        for name in ("H2O", "H2"):
            p = os.path.join(ROOT, "runs", GAS_RUN[m], f"{name}.out")
            e = qc.trusted_energy_ev(p, strict=True) if os.path.exists(p) else None
            if e is None:
                sys.exit(f"REFUSING: {m} gas reference {p} missing or failed QC")
            g[name] = e
        gas[m] = g

    # ---- per-metal ----------------------------------------------------------
    rows, drift = {}, []
    for m in METALS:
        if any((m, st, leg) not in E for st in STATES for leg in ("atomic", "ortho")):
            continue
        legs = {}
        for leg in ("atomic", "ortho"):
            dG = {sp: delta_G(E[(m, "slab", leg)], E[(m, f"s0_{sp}", leg)], sp,
                              gas[m]["H2O"], gas[m]["H2"])
                  for sp in ("OH", "O", "OOH")}
            r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
            dEl = {sp: E[(m, f"s0_{sp}", leg)] - E[(m, "slab", leg)]
                       - reference_energy(sp, gas[m]["H2O"], gas[m]["H2"])
                   for sp in ("OH", "O", "OOH")}
            rz = oer_overpotential(dEl["OH"], dEl["O"], dEl["OOH"])
            legs[leg] = dict(dG=dG, eta=r.overpotential, pls=r.potential_limiting_step,
                             steps=[r.dG1, r.dG2, r.dG3, r.dG4],
                             steps_electronic=[rz.dG1, rz.dG2, rz.dG3, rz.dG4])

        # cross-check the atomic leg against the banked registered readout
        brow = [x for x in banked[m]["rows"] if abs(x["u"] - U_VALUE) < 1e-9]
        if not brow:
            sys.exit(f"REFUSING: no banked u750 rung for {m} in {BANKED}")
        d_mev = (legs["atomic"]["eta"] - brow[0]["eta"]) * 1000.0
        drift.append((m, d_mev))
        if abs(d_mev) > args.tol_mev:
            sys.exit(f"EXTRACTION BUG: {m} atomic eta re-derives to "
                     f"{legs['atomic']['eta']:.6f} V but the banked readout says "
                     f"{brow[0]['eta']:.6f} V ({d_mev:+.3f} meV > {args.tol_mev}). "
                     "Not reporting.")

        d_eta = legs["ortho"]["eta"] - legs["atomic"]["eta"]
        a = abs(d_eta)
        band = "FIRES" if a > FIRE_V else ("NULL" if a < NULL_V else "INTERMEDIATE")

        pa, po = legs["atomic"]["pls"], legs["ortho"]["pls"]
        c = zpe.step_constants(dict(ZPE_TS_CORRECTION))
        decomp = None
        if pa != po:
            const = c[po - 1] - c[pa - 1]
            elec = (legs["ortho"]["steps_electronic"][po - 1]
                    - legs["atomic"]["steps_electronic"][pa - 1])
            decomp = dict(
                electronic_eV=elec, constants_eV=const,
                constants_share=(const / d_eta) if d_eta else None,
                closure=(elec + const) - d_eta,
                gas_note=("legs have DIFFERENT pls, so E_H2O does NOT cancel in "
                          "this d-eta (weight -1); E_H2 does. A13.6."))

        rows[m] = dict(
            role=("CALIBRATION (post-hoc)" if m == CALIBRATION else "blind"),
            eta_atomic=legs["atomic"]["eta"], eta_ortho=legs["ortho"]["eta"],
            pls_atomic=pa, pls_ortho=po, pls_differs=(pa != po),
            d_eta_V=d_eta, abs_d_eta_V=a, band=band,
            steps_atomic=legs["atomic"]["steps"], steps_ortho=legs["ortho"]["steps"],
            dG_atomic=legs["atomic"]["dG"], dG_ortho=legs["ortho"]["dG"],
            zpe_decomposition=decomp,
            R_M=r_diagnostic(banked[m]["rows"], legs["ortho"]["dG"]),
            pp_family=PP_FAMILY[m], nspin=NSPIN[m],
            banked_atomic_eta=brow[0]["eta"], rederivation_drift_meV=d_mev,
        )

    # ---- the table: A12.R4 requires all five, always -------------------------
    print("=" * 100)
    print("P-PROJ-6 -- Amendment 12. Projector contrast across the A0 roster, U = 7.50 eV.")
    print("=" * 100)
    print(f"\n{'metal':5s} {'role':22s} {'eta_at':>8s} {'eta_or':>8s} {'pls':>7s} "
          f"{'d-eta':>9s} {'band':>13s}  {'PP':<15s} nspin")
    for m in METALS:
        if m not in rows:
            print(f"{m:5s} {'-- NOT LANDED --':22s}")
            continue
        r = rows[m]
        print(f"{m:5s} {r['role']:22s} {r['eta_atomic']:8.4f} {r['eta_ortho']:8.4f} "
              f"{r['pls_atomic']:d}->{r['pls_ortho']:d}    {r['d_eta_V']:+9.4f} "
              f"{r['band']:>13s}  {r['pp_family']:<15s} {r['nspin']}")

    print(f"\n  atomic re-derivation vs banked docs/figs/a0main_readout.json:")
    for m, d in drift:
        print(f"    {m:3s} {d:+8.4f} meV")

    if any(m not in rows for m in METALS):
        print("\nARM INCOMPLETE -- no class verdict. A12.R4 forbids quoting a subset.")
        return

    # ---- class verdict over the BLIND FIVE ONLY ------------------------------
    fires = [m for m in BLIND if rows[m]["band"] == "FIRES"]
    inter = [m for m in BLIND if rows[m]["band"] == "INTERMEDIATE"]
    nulls = [m for m in BLIND if rows[m]["band"] == "NULL"]
    n = len(fires)
    verdict = ("CONFIRMED" if n >= 4 else
               "MIDDLE BAND -- metal-dependent" if n >= 2 else
               "NOT MET" if n == 1 else "FALSIFIED")

    print("\n" + "-" * 100)
    print(f"DENOMINATOR = 5 BLIND METALS (Cr excluded as CALIBRATION, A12.R2)")
    print("-" * 100)
    print(f"  FIRES        {n}/5  {fires}")
    print(f"  INTERMEDIATE {len(inter)}/5  {inter}   (never rounded to either side)")
    print(f"  NULL         {len(nulls)}/5  {nulls}")
    print(f"\n  CLASS VERDICT: {verdict}")

    # ---- confound clauses, A12.R5 / A12.R6 ----------------------------------
    fs = set(fires)
    declared = []
    if fs == {"Mn", "Ti", "Ir"}:
        declared.append("PSEUDOPOTENTIAL: firing set is exactly the ultrasoft blind "
                        "metals {Mn, Ti, Ir} and no other")
    if fs == {"Fe", "Ru"}:
        declared.append("PSEUDOPOTENTIAL: firing set is exactly the non-ultrasoft "
                        "blind metals {Fe, Ru}")
    if fs == {"Mn", "Fe"}:
        declared.append("SPIN: firing set is exactly the nspin=2 blind metals {Mn, Fe}")
    if fs == {"Ti", "Ru", "Ir"}:
        declared.append("SPIN: firing set is exactly the nspin=1 blind metals "
                        "{Ti, Ru, Ir}")
    if declared:
        print("\n  *** DECLARED CONFOUNDED -- NO CLASS CLAIM MAY BE MADE ***")
        for d in declared:
            print(f"    {d}")
        print("    Reported as an observation whose partition coincides exactly with a")
        print("    known unmeasured confound, in the same sentence, always. (A12.R5/R6)")
    else:
        print("\n  confound clauses: NOT triggered "
              f"(firing set {sorted(fs)} matches no registered partition)")

    print("\n  pls comparison (SECONDARY, reported not scored, A12.R1):")
    for m in METALS:
        r = rows[m]
        tag = " [CALIBRATION]" if m == CALIBRATION else ""
        print(f"    {m:3s} {r['pls_atomic']} -> {r['pls_ortho']}  "
              f"{'DIFFERS' if r['pls_differs'] else 'same'}{tag}")

    print("\n  A13.6 decomposition, for every metal whose legs differ in pls:")
    for m in METALS:
        d = rows[m]["zpe_decomposition"]
        if not d:
            continue
        share = d["constants_share"]
        print(f"    {m:3s} d-eta {rows[m]['d_eta_V']:+.4f} V = electronic "
              f"{d['electronic_eV']:+.4f} + constants {d['constants_eV']:+.4f}"
              + (f"   ({share*100:.1f} % constants)" if share is not None else ""))
    print("    When the pls differ, E_H2O does NOT cancel in that d-eta (weight -1).")

    print("\n  R_M (DIAGNOSTIC, no verdict -- A12.R1):")
    for m in METALS:
        R = rows[m]["R_M"]
        if not R:
            continue
        print(f"    {m:3s} RMS {R['rms_eV']:.4f} eV at U {R['u_opt']:.3f}"
              f"{' (GRID EDGE)' if R['optimum_at_grid_edge'] else ''}"
              f"   implied-shift span {R['implied_shift_span_eV']:.2f} eV")

    print("\n  DISCLOSED, not scored (A12.R6): the k-mesh is not uniform across the")
    print("  roster -- Cr and Mn slabs are 9 4 1, Fe/Ti/Ru/Ir are 8 4 1. Harmless")
    print("  within a pair (d-eta is a paired difference at byte-identical settings);")
    print("  any cross-metal table crosses two meshes and must say so on its face.")

    if args.json:
        payload = dict(
            rung=RUNG, U=U_VALUE, metals=rows,
            blind_denominator=BLIND, calibration=CALIBRATION,
            fires=fires, intermediate=inter, null=nulls,
            n_fires=n, class_verdict=verdict,
            declared_confounded=declared,
            thresholds=dict(fire_V=FIRE_V, null_V=NULL_V,
                            inherited_from="A7.1 via A12.R3"),
            rederivation_drift_meV=dict(drift),
        )
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"\n  json -> {os.path.relpath(args.json, ROOT)}")


if __name__ == "__main__":
    main()
