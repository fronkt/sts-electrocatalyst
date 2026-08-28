#!/usr/bin/env python3
"""A0-cell readout: the A6.2 I_U separability test and the crossing-location shift.

Registered test (docs/43 A6.2, verbatim): "Over the five shared U points, with
D(cell) = dG_O - dG_OH -- the descriptor P7 measured -- and span(cell) =
max_U D - min_U D, define I_U = span(2x1v) - span(1x1)." Thresholds inherited
verbatim from S2's interaction bins, not re-derived:

    |I_U| < 0.05 eV   additive
    |I_U| >= 0.30 eV  not separable
    0.05-0.30 eV      inconclusive, "not rounded toward either"

Prior on record: additive. Second readout, same arm, no extra compute: if the
two cells place the volcano-apex crossing (D = 1.6 eV, the apex of the
descriptor volcano per src/hea_oer/descriptors.py) at U values differing by
more than 1.0 eV, A0's "the crossing is located rather than bracketed" claim is
cell-conditional and must be reported as such.

THE TWO LEGS.
  1x1:  the inherited four-point ladder (runs/probe/Cr, array of 2026-08's
        probe campaign) + the P-PROJ ATOMIC leg as the fifth point (U = 7.15,
        runs/a0/p_proj + the banked runs/s0/e_proj *O deck) -- same geometry,
        same protocol, asserted at P-PROJ build time against probe decks.
  2x1v: runs/a0/cell (arrays 20178325 / 20183041 / 20183150), states per
        runs/a0/m_a0cell.txt: ref__2x1v, s0_O/s0_OH __2x1v_mir, s0_OOH
        __2x1v_escape.

U = 7.15 eV carries the PROJECTOR-MISMATCHED label on BOTH legs (A7.1 fired at
0.487 V, docs/figs/pproj_readout.json); the label travels with every number
derived from that rung, including this test's fifth column.

GATES, run before any number is reported:
  - every output passes qe_qc.trusted_energy_ev strict;
  - extraction control per leg: each state's base/production-U SCF must
    reproduce its source relaxation's final energy to <= 5 meV;
  - a missing point prints as a GAP (A6.5: "a grid with holes is reportable"),
    and the verdict line refuses until all five shared points exist per leg.

Fixed-geometry single points throughout; nothing here is relaxed.

Usage:  PYTHONPATH=src python src/dft/a0cell_readout.py [--json results/a0cell.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys

RY_EV = 13.605693122994
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# the five shared U points (eV) and each leg's file naming for them
U_SHARED = [0.0, 1.85, 3.70, 4.995, 7.15]
SUFFIX = {0.0: "u0.0", 1.85: "u0.5", 3.70: "base", 4.995: "u1.35", 7.15: "u715"}

STATES_1X1 = {"slab": "slab", "s0_O": "s0_O", "s0_OH": "s0_OH", "s0_OOH": "s0_OOH"}
STATES_2X1V = {"slab": "ref__2x1v", "s0_O": "s0_O__2x1v_mir",
               "s0_OH": "s0_OH__2x1v_mir", "s0_OOH": "s0_OOH__2x1v_escape"}

# extraction controls: (state base/production SCF, source relaxation output)
CONTROLS_2X1V = {
    "slab":  ("runs/a0/cell/ref__2x1v__base.out", "runs/probe/Cr_cellsym/ref__2x1v.out"),
    "s0_O":  ("runs/a0/cell/s0_O__2x1v_mir__base.out", "runs/probe/Cr_cellsym/s0_O__2x1v_mir.out"),
    "s0_OH": ("runs/a0/cell/s0_OH__2x1v_mir__base.out", "runs/probe/Cr_cellsym/s0_OH__2x1v_mir.out"),
    "s0_OOH": ("runs/a0/cell/s0_OOH__2x1v_escape__base.out", "runs/s3/Cr/s0_OOH__2x1v_escape.out"),
}
APEX = 1.6  # eV, descriptor value at the volcano apex (universal scaling)


def _qc():
    spec = importlib.util.spec_from_file_location("qe_qc", os.path.join(HERE, "qe_qc.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _final_ry(path):
    e = None
    for line in open(path, errors="replace"):
        if line.startswith("!") and "total energy" in line:
            e = float(re.search(r"=\s*([-\d.]+)\s*Ry", line).group(1))
    return e


def _path(leg: str, state: str, u: float) -> str:
    suf = SUFFIX[u]
    if leg == "1x1":
        if u == 7.15:
            if state == "s0_O":
                return os.path.join(ROOT, "runs", "s0", "e_proj", "s0_O__u715_atomic.out")
            return os.path.join(ROOT, "runs", "a0", "p_proj", f"{state}__u715_atomic.out")
        return os.path.join(ROOT, "runs", "probe", "Cr", f"{state}__{suf}.out")
    return os.path.join(ROOT, "runs", "a0", "cell", f"{STATES_2X1V[state]}__{suf}.out")


def crossing(us, ds, level=APEX):
    """U values where the piecewise-linear D(U) crosses `level`, with brackets."""
    hits = []
    for (u1, d1), (u2, d2) in zip(list(zip(us, ds))[:-1], list(zip(us, ds))[1:]):
        if d1 is None or d2 is None:
            continue
        if (d1 - level) * (d2 - level) <= 0 and d1 != d2:
            hits.append((u1 + (level - d1) * (u2 - u1) / (d2 - d1), (u1, u2)))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    from hea_oer.referencing import delta_G
    from hea_oer.descriptors import oer_overpotential

    qc = _qc()

    gas = {}
    for g in ("H2O", "H2"):
        p = os.path.join(ROOT, "runs", "Cr_slab", f"{g}.out")
        e = qc.trusted_energy_ev(p, strict=True) if os.path.exists(p) else None
        if e is None:
            sys.exit(f"REFUSING: gas reference {p} missing or failed QC")
        gas[g] = e

    # --- extraction controls --------------------------------------------------
    print("extraction control, 2x1v leg (base SCF vs source relaxation, tol 5 meV;")
    print("  the tolerance is script-level QC, not a registered threshold; the 1x1")
    print("  leg's control is inherited from probe-time GATE 1, not re-run here)")
    ctrl_ok = True
    ctrl_drift = {}
    for st, (base, src) in CONTROLS_2X1V.items():
        eb, er = _final_ry(os.path.join(ROOT, base)), _final_ry(os.path.join(ROOT, src))
        if eb is None or er is None:
            print(f"  {st:7s} -- control not available"); ctrl_ok = False; ctrl_drift[st] = None; continue
        d = (eb - er) * RY_EV * 1000
        ok = abs(d) <= 5.0
        ctrl_ok &= ok
        ctrl_drift[st] = d
        print(f"  {st:7s} drift {d:+7.2f} meV  {'OK' if ok else 'DRIFT'}")
    # the 1x1 probe leg ran its own GATE 1 in probe_eta.py at probe time; the
    # P-PROJ fifth point was asserted byte-identical to probe decks at build time.
    if not ctrl_ok:
        sys.exit("REFUSING: extraction control failed; the cell comparison would "
                 "be confounded by a geometry round-trip error.")
    print()

    # --- energies, QC'd; gaps reported, never invented ------------------------
    E, gaps = {}, []
    for leg in ("1x1", "2x1v"):
        for st in STATES_1X1:
            for u in U_SHARED:
                p = _path(leg, st, u)
                if not os.path.exists(p):
                    gaps.append((leg, st, u, "missing")); continue
                e = qc.trusted_energy_ev(p, strict=True)
                if e is None:
                    rec = qc.scan(p, None)
                    gaps.append((leg, st, u, rec["verdict"])); continue
                E[(leg, st, u)] = e
    if gaps:
        print(f"GAPS ({len(gaps)}) -- plotted as holes, never interpolated across:")
        for leg, st, u, why in gaps:
            print(f"  {leg:5s} {st:7s} U={u:<5g} {why}")
        print()

    # --- D(U) per leg ---------------------------------------------------------
    rows = {}
    print(f"{'U (eV)':>7s} {'D 1x1':>8s} {'D 2x1v':>8s} {'dD':>8s}   "
          f"(D = dG_O - dG_OH, eV; U=7.15 is PROJECTOR-MISMATCHED)")
    for u in U_SHARED:
        d = {}
        for leg in ("1x1", "2x1v"):
            need = [(leg, "slab", u), (leg, "s0_O", u), (leg, "s0_OH", u)]
            if any(k not in E for k in need):
                d[leg] = None; continue
            es = E[(leg, "slab", u)]
            dgo = delta_G(es, E[(leg, "s0_O", u)], "O", gas["H2O"], gas["H2"])
            dgoh = delta_G(es, E[(leg, "s0_OH", u)], "OH", gas["H2O"], gas["H2"])
            d[leg] = dgo - dgoh
        rows[u] = d
        f = lambda x: f"{x:8.3f}" if x is not None else "     GAP"
        dd = (f"{d['2x1v'] - d['1x1']:+8.3f}"
              if None not in (d["1x1"], d["2x1v"]) else "        ")
        print(f"{u:7.3g} {f(d['1x1'])} {f(d['2x1v'])} {dd}")

    # --- eta(U) per leg, where the full four-state set exists -----------------
    print(f"\n{'U (eV)':>7s} {'eta 1x1':>8s} {'pls':>4s} {'eta 2x1v':>9s} {'pls':>4s}")
    etas = {}
    for u in U_SHARED:
        r = {}
        for leg in ("1x1", "2x1v"):
            need = [(leg, st, u) for st in STATES_1X1]
            if any(k not in E for k in need):
                r[leg] = None; continue
            es = E[(leg, "slab", u)]
            dg = {sp: delta_G(es, E[(leg, f"s0_{sp}", u)], sp, gas["H2O"], gas["H2"])
                  for sp in ("OH", "O", "OOH")}
            r[leg] = oer_overpotential(dg["OH"], dg["O"], dg["OOH"])
        etas[u] = r
        f = lambda x, w: (f"{x.overpotential:{w}.3f}", f"{x.potential_limiting_step:4d}") \
            if x is not None else (" " * (w - 3) + "GAP", "    ")
        a, b = f(r["1x1"], 8), f(r["2x1v"], 9)
        print(f"{u:7.3g} {a[0]} {a[1]} {b[0]} {b[1]}")

    # --- the registered verdicts ----------------------------------------------
    result = dict(gas=gas, D=rows,
                  eta={u: {leg: (None if r is None else
                                 dict(eta=r.overpotential, pls=r.potential_limiting_step))
                           for leg, r in e.items()} for u, e in etas.items()},
                  gaps=[list(g) for g in gaps],
                  extraction_control_2x1v_meV=ctrl_drift, control_ok=ctrl_ok,
                  control_note=("2x1v leg only (base SCF vs source relaxation); the 1x1 "
                                "leg's control is probe-time GATE 1; 5 meV tolerance is "
                                "script-level QC, not registered"),
                  labels={"7.15": ("PROJECTOR-MISMATCHED: U = 7.15 eV is Xu 2015's "
                                   "linear-response value, derived under a different "
                                   "Hubbard projector; A7.1 FIRED (|d-eta| = 0.487 V, "
                                   "docs/figs/pproj_readout.json). Both legs run in the "
                                   "ladder's own atomic projector; the label marks the U "
                                   "value's provenance."),
                          "u_points": ("the 4.995 eV point is the u1.35 ladder rung "
                                       "(1.35 x 3.70); the registration's '5.00 eV' at "
                                       "docs/43:1200 is a rounding of the same rung")})
    complete = all(rows[u][leg] is not None for u in U_SHARED for leg in ("1x1", "2x1v"))
    if not complete:
        print("\nVERDICT WITHHELD: the five shared points are not all banked yet; "
              "span over a subset is not the registered quantity.")
        result["verdict"] = "PENDING"
    else:
        span = {leg: max(rows[u][leg] for u in U_SHARED) - min(rows[u][leg] for u in U_SHARED)
                for leg in ("1x1", "2x1v")}
        iu = span["2x1v"] - span["1x1"]
        bin_ = ("additive" if abs(iu) < 0.05 else
                "not separable" if abs(iu) >= 0.30 else "inconclusive")
        print(f"\nspan(1x1) = {span['1x1']:.3f} eV   span(2x1v) = {span['2x1v']:.3f} eV")
        print(f"I_U = span(2x1v) - span(1x1) = {iu:+.3f} eV   |I_U| = {abs(iu):.3f} eV")
        print(f"A6.2 VERDICT: {bin_.upper()}  (bins: <0.05 additive, >=0.30 not "
              f"separable, between inconclusive; prior on record: additive)")
        result.update(span=span, I_U=iu, verdict=bin_)

        cx = {leg: crossing([u for u in U_SHARED], [rows[u][leg] for u in U_SHARED])
              for leg in ("1x1", "2x1v")}
        for leg in ("1x1", "2x1v"):
            if cx[leg]:
                s = "; ".join(f"U = {u:.2f} eV (bracket {a:g}-{b:g})" for u, (a, b) in cx[leg])
            else:
                s = "no crossing of D = 1.6 eV inside the five-point band"
            print(f"crossing({leg}): {s}")
        # robustness of the verdicts to the PROJECTOR-MISMATCHED U = 7.15 rung:
        # every quantity that depends on that rung is recomputed on the four
        # clean points so the verdict never rests silently on the labelled point.
        U_CLEAN = [u for u in U_SHARED if u != 7.15]
        span_c = {leg: max(rows[u][leg] for u in U_CLEAN) - min(rows[u][leg] for u in U_CLEAN)
                  for leg in ("1x1", "2x1v")}
        iu_c = span_c["2x1v"] - span_c["1x1"]
        bin_c = ("additive" if abs(iu_c) < 0.05 else
                 "not separable" if abs(iu_c) >= 0.30 else "inconclusive")
        print(f"robustness (clean points only, U = {{0, 1.85, 3.70, 4.995}}): "
              f"I_U = {iu_c:+.3f} eV -> {bin_c.upper()}"
              + ("  (same bin: the I_U verdict does not rest on the mismatched rung)"
                 if bin_c == bin_ else "  (BIN CHANGES if the mismatched rung is dropped)"))
        result.update(I_U_clean=iu_c, span_clean=span_c, verdict_clean=bin_c)

        if cx["1x1"] and cx["2x1v"]:
            shift = abs(cx["1x1"][0][0] - cx["2x1v"][0][0])
            cond = "CELL-CONDITIONAL" if shift > 1.0 else "not cell-conditional"
            # which crossings run through the mismatched rung?
            mm = {leg: any(7.15 in br for _, br in cx[leg]) for leg in cx}
            cx_c = {leg: crossing(U_CLEAN, [rows[u][leg] for u in U_CLEAN])
                    for leg in ("1x1", "2x1v")}
            print(f"crossing shift = {shift:.2f} eV -> the located-crossing claim is {cond} "
                  f"(threshold 1.0 eV)")
            for leg in ("1x1", "2x1v"):
                if mm[leg]:
                    print(f"  crossing({leg}) is interpolated into the PROJECTOR-MISMATCHED "
                          f"U = 7.15 rung -- the label travels with it")
            if mm["2x1v"] and not cx_c["2x1v"] and cx_c["1x1"]:
                # 2x1v never reaches the apex on clean points: the clean-point
                # statement is a bound, and it is what the verdict may rest on.
                lb = U_CLEAN[-1] - cx_c["1x1"][0][0]
                print(f"  robustness: on clean points D(2x1v) tops out at "
                      f"{max(rows[u]['2x1v'] for u in U_CLEAN):.3f} < 1.6, so the 2x1v "
                      f"crossing lies above U = {U_CLEAN[-1]:g} and the shift is >= "
                      f"{lb:.2f} eV{' > 1.0 -> CELL-CONDITIONAL stands on clean points alone' if lb > 1.0 else ' (below threshold: the verdict RESTS on the mismatched rung)'}")
                result["crossing_shift_clean_lower_bound_eV"] = lb
            result["crossing_shift_eV"] = shift
            result["crossing_shift_label"] = (
                "shift uses the 2x1v crossing interpolated into the PROJECTOR-MISMATCHED "
                "U=7.15 rung" if mm["2x1v"] else "clean")
        result["crossings"] = {leg: [[u, list(br)] for u, br in cx[leg]] for leg in cx}
        result["crossings_use_mismatched_rung"] = {
            leg: any(7.15 in br for _, br in cx[leg]) for leg in cx}

        # A7.1's "the projector delta becomes its own labelled sub-row":
        pp = os.path.join(ROOT, "docs", "figs", "pproj_readout.json")
        if os.path.exists(pp):
            with open(pp) as fh:
                ppd = json.load(fh)
            result["projector_delta_sub_row"] = dict(
                abs_d_eta_V=ppd["abs_d_eta_V"], verdict=ppd["verdict"],
                label="PROJECTOR-MISMATCHED sub-row (A7.1): eta consequence of the "
                      "projector mismatch at U = 7.15 eV, Cr 1x1")
            print(f"projector-delta sub-row (A7.1): |d-eta| = {ppd['abs_d_eta_V']:.3f} V "
                  f"[PROJECTOR-MISMATCHED]")

    if args.json:
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w") as fh:
            json.dump(result, fh, indent=2, default=str)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
