#!/usr/bin/env python3
"""A0-main readout: the registered dense eta(U) grid (block 6A / A6.1a / A6.3).

The three registered questions this script answers, and nothing else:

  1. P7 BOUND (Cr, location arm). "P7 -- the withdrawn eta(Cr) headline, the
     1.122 V swing -- was measured in the 1x1 cell. A0's registered job is to
     bound THAT claim." Reported: the eta(U) curve on the 19-point grid, the
     measured swing max-min over U in [0,9], and the volcano-apex crossing
     (D = dG_O - dG_OH = 1.6 eV) located to +/-0.25 eV (the 0.5 eV step's pin).

  2. ORDERING (Ru/Ir, A6.3). Pre-registered, falsifiable: "the reference
     ordering Ir < Ru is stable across U in [0, 9] eV. If it inverts anywhere
     in the band, then the anchors against which every 3d result in this
     campaign is reported are themselves U-conditional." Scored on the seven
     shared grid points; the Xu anchor points (Ru 6.73, Ir 5.91) are declared
     anchors, reported as their own labelled rows -- and, since A7.1 FIRED at
     |d-eta| = 0.487 V (docs/figs/pproj_readout.json), every Xu-anchor row
     carries the PROJECTOR-MISMATCHED label: Xu's U values were derived under
     a different Hubbard projector than this grid's HUBBARD (atomic).

  3. PLS FLIPS (A7.2). "The U at which each metal's pls flips is a first-class
     deliverable." Reported per metal as the bracketing grid interval(s).
     A7.2's closed form -- for pls in {2,3}, eta = (c_M/2 - 1.23) + |dG2-dG3|/2
     with c_M = dG_OOH - dG_OH -- is verified on every such point as an
     identity check on our own arithmetic; the identity breaking on a pls 1/4
     point is expected and not an error.

GATES.
  - Every point passes qe_qc.trusted_energy_ev strict; a failing point is a
    GAP, reported with the A6.5(2) escalation state -- "never interpolated
    across, never silently dropped. A grid with holes is reportable."
  - Extraction control per metal: the A0 grid's U = 0 point re-runs an SCF the
    probe campaign already banked at U = 0 (Cr: the probe u-ladder's u0.0 rung;
    Ru/Ir: the probe base itself, whose production tier carries no U). The two
    must land within 5 meV. Cr's grid steps by 0.5 eV so it has NO 3.70 point;
    an earlier revision compared a u370 token that cannot exist -- the control
    now uses the only registered-grid overlap, U = 0, all four states.
    CAVEAT (2026-08-28 adversarial review): the compared decks are byte-identical
    except the prefix line, so this measures SCF re-run determinism only. The
    genuine geometry-extraction control (base SCF vs source relaxation) is the
    a0cell readout's; this one is kept, honestly named, as a determinism check.
  - Gas references per metal from each probe's own source run (runs/Cr_slab,
    runs/Ru_anchor, runs/Ir_anchor), QC'd; legs never mix calculators.

Fixed-geometry single points everywhere: A6.4 -- "A0 measures the U-response
of energies at frozen geometry; it cannot see a U-driven geometry change.
Where A0 and a relaxed point disagree, the relaxed point wins."

Usage:  PYTHONPATH=src python src/dft/a0main_readout.py [--json docs/figs/a0main_readout.json]
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

STATES = ("slab", "s0_O", "s0_OH", "s0_OOH")
CR_GRID = [round(0.5 * i, 2) for i in range(19)]
REF_GRID = [0.0, 1.5, 3.0, 4.5, 6.0, 7.5, 9.0]
METALS = {
    "Cr": dict(grid=CR_GRID, anchor=None, gas_run="Cr_slab", production_u=3.70,
               control=("u000", "u0.0")),
    "Ru": dict(grid=REF_GRID, anchor=6.73, gas_run="Ru_anchor", production_u=0.0,
               control=("u000", "base")),
    "Ir": dict(grid=REF_GRID, anchor=5.91, gas_run="Ir_anchor", production_u=0.0,
               control=("u000", "base")),
}
APEX = 1.6      # eV, descriptor at the volcano apex
G_TOTAL = 4.92  # eV, 4 x 1.23


def u_token(u: float) -> str:
    return "u%03d" % int(round(u * 100))


def _qc():
    spec = importlib.util.spec_from_file_location("qe_qc", os.path.join(HERE, "qe_qc.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _final_ry(path):
    e = None
    if not os.path.exists(path):
        return None
    for line in open(path, errors="replace"):
        if line.startswith("!") and "total energy" in line:
            e = float(re.search(r"=\s*([-\d.]+)\s*Ry", line).group(1))
    return e


def crossings(us, ds, level=APEX):
    hits = []
    pts = [(u, d) for u, d in zip(us, ds) if d is not None]
    for (u1, d1), (u2, d2) in zip(pts[:-1], pts[1:]):
        if (d1 - level) * (d2 - level) <= 0 and d1 != d2:
            hits.append((u1 + (level - d1) * (u2 - u1) / (d2 - d1), (u1, u2)))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--tol-mev", type=float, default=5.0)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    from hea_oer.referencing import delta_G
    from hea_oer.descriptors import oer_overpotential

    qc = _qc()
    result = {"metals": {}}
    any_missing = False

    for metal, cfg in METALS.items():
        print("=" * 72)
        print(f"{metal}  ({'location arm' if metal == 'Cr' else 'ordering arm'})")
        gas = {}
        for g in ("H2O", "H2"):
            p = os.path.join(ROOT, "runs", cfg["gas_run"], f"{g}.out")
            e = qc.trusted_energy_ev(p, strict=True) if os.path.exists(p) else None
            if e is None:
                sys.exit(f"REFUSING: {metal} gas reference {p} missing or failed QC")
            gas[g] = e

        # --- extraction control ------------------------------------------------
        tok, probe_sfx = cfg["control"]
        drift = {}
        ok = True
        for st in STATES:
            a0 = _final_ry(os.path.join(ROOT, "runs", "a0", "main", metal, f"{st}__{tok}.out"))
            pb = _final_ry(os.path.join(ROOT, "runs", "probe", metal, f"{st}__{probe_sfx}.out"))
            if a0 is None or pb is None:
                drift[st] = None
                ok = False
                continue
            d = (a0 - pb) * RY_EV * 1000
            drift[st] = d
            if abs(d) > args.tol_mev:
                ok = False
        ds = ", ".join(f"{st} {('%+.2f' % d) if d is not None else 'NA'}"
                       for st, d in drift.items())
        print(f"re-run determinism check ({tok} vs probe {probe_sfx}; decks identical "
              f"except prefix, NOT a geometry round-trip control; meV): {ds}  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            print(f"  {metal}: control failed or incomplete -- this metal's rows "
                  f"are reported but marked UNTRUSTED until reconciled.")

        # --- the grid ----------------------------------------------------------
        points = list(cfg["grid"]) + ([cfg["anchor"]] if cfg["anchor"] else [])
        rows, gaps = [], []
        for u in sorted(points):
            E = {}
            why = {}
            for st in STATES:
                p = os.path.join(ROOT, "runs", "a0", "main", metal, f"{st}__{u_token(u)}.out")
                if not os.path.exists(p):
                    E[st] = None
                    why[st] = "absent"
                    continue
                E[st] = qc.trusted_energy_ev(p, strict=True)
                if E[st] is None:
                    why[st] = "qc-fail"
            missing = [st for st in STATES if E[st] is None]
            if missing:
                gaps.append((u, missing, [why[st] for st in missing]))
                any_missing = True
                rows.append(dict(u=u, gap=missing, gap_why=[why[st] for st in missing]))
                continue
            dg = {sp: delta_G(E["slab"], E[f"s0_{sp}"], sp, gas["H2O"], gas["H2"])
                  for sp in ("OH", "O", "OOH")}
            r = oer_overpotential(dg["OH"], dg["O"], dg["OOH"])
            # A7.2 closed-form identity check on pls in {2,3}
            ident = None
            if r.potential_limiting_step in (2, 3):
                c_m = dg["OOH"] - dg["OH"]
                eta_cf = (c_m / 2 - 1.23) + abs(r.dG2 - r.dG3) / 2
                ident = abs(eta_cf - r.overpotential)
            rows.append(dict(u=u, dG_OH=dg["OH"], dG_O=dg["O"], dG_OOH=dg["OOH"],
                             D=dg["O"] - dg["OH"], eta=r.overpotential,
                             pls=r.potential_limiting_step, closed_form_dev=ident,
                             anchor=(u == cfg["anchor"])))

        hdr = (f"{'U (eV)':>7s} {'dG_OH':>7s} {'dG_O':>7s} {'dG_OOH':>7s} "
               f"{'D':>7s} {'eta':>7s} {'pls':>4s}")
        print(hdr)
        for r in rows:
            if "gap" in r:
                print(f"{r['u']:7.2f}    GAP ({', '.join(r['gap'])})")
                continue
            tag = "  XU-ANCHOR [PROJECTOR-MISMATCHED]" if r["anchor"] else ""
            cf = ""
            if r["closed_form_dev"] is not None and r["closed_form_dev"] > 1e-9:
                cf = f"  CLOSED-FORM DEV {r['closed_form_dev']:.2e}"
            print(f"{r['u']:7.2f} {r['dG_OH']:7.3f} {r['dG_O']:7.3f} "
                  f"{r['dG_OOH']:7.3f} {r['D']:7.3f} {r['eta']:7.3f} "
                  f"{r['pls']:4d}{tag}{cf}")
        if gaps:
            n_fail = sum(1 for _, _, ws in gaps if "qc-fail" in ws)
            n_abs = len(gaps) - n_fail
            msg = f"GAPS: {len(gaps)} point(s)"
            if n_abs:
                msg += f" -- {n_abs} with no output banked (not yet run; not a convergence event)"
            if n_fail:
                msg += (f" -- {n_fail} QC-FAILED: A6.5(2) escalation owed: "
                        f"(i) startingpot from converged neighbour, (ii) halve beta, "
                        f"(iii) NOT_CONVERGED, plotted as a hole")
            print(msg + ".")

        full = [r for r in rows if "gap" not in r]
        m_out = dict(gas=gas, rerun_determinism_check_meV=drift, control_ok=ok,
                     control_note=("same-deck re-run: the A0 u000 decks are byte-identical "
                                   "to the probe u0.0/base decks except the prefix line, so "
                                   "this drift measures SCF re-run determinism, not a "
                                   "geometry round-trip; the genuine extraction control "
                                   "(SCF vs source relaxation) lives in the a0cell readout"),
                     rows=rows, gaps=[[u, ms, ws] for u, ms, ws in gaps])

        grid_rows = [r for r in full if not r["anchor"]]
        if metal == "Cr" and grid_rows:
            etas = [r["eta"] for r in grid_rows]
            swing = max(etas) - min(etas)
            u_max = grid_rows[max(range(len(etas)), key=lambda i: etas[i])]["u"]
            u_min = grid_rows[min(range(len(etas)), key=lambda i: etas[i])]["u"]
            # P7's withdrawn 1.122 V headline was measured on the probe ladder's
            # window U in [0, 7.15]; the grid's swing over its own [0, 9] window
            # is a different quantity and the two are never quoted as one bound.
            in_win = [r["eta"] for r in grid_rows if r["u"] <= 7.15]
            swing_w = (max(in_win) - min(in_win)) if in_win else None
            edge = grid_rows[-1]["eta"] > grid_rows[-2]["eta"] if len(grid_rows) > 1 else False
            print(f"\nP7 BOUND: eta swing = {swing:.3f} V over the grid's own window "
                  f"U in [0, 9] (max {max(etas):.3f} at U={u_max:g}, min {min(etas):.3f} "
                  f"at U={u_min:g})"
                  + (" -- ETA STILL RISING AT THE U=9 GRID EDGE: edge-limited" if edge else "")
                  + (" -- grid has holes" if gaps else ""))
            if swing_w is not None:
                print(f"  restricted to P7's own window U in [0, 7.15]: swing = "
                      f"{swing_w:.3f} V vs the withdrawn five-point headline 1.122 V "
                      f"(the 0.5-step grid straddles the eta minimum, so the windows "
                      f"and samplings differ; neither number confirms the other)")
            cx = crossings([r["u"] for r in grid_rows], [r["D"] for r in grid_rows])
            cell_cond = None
            cell_json = os.path.join(ROOT, "docs", "figs", "a0cell_readout.json")
            if os.path.exists(cell_json):
                with open(cell_json) as fh:
                    cj = json.load(fh)
                s = cj.get("crossing_shift_eV")
                if s is not None:
                    cell_cond = s > 1.0
            if cx:
                for u, (a, b) in cx:
                    if cell_cond:
                        tag = ("  [CELL-CONDITIONAL per A6.2: the 2x1v cell moves this "
                               "crossing by more than the 1.0 eV threshold -- see "
                               "a0cell_readout]")
                    elif cell_cond is None:
                        tag = "  [cell-conditionality unscored: a0cell readout not found]"
                    else:
                        tag = ""
                    print(f"apex crossing (D = 1.6): inside bracket [{a:g}, {b:g}] "
                          f"(0.5 eV grid step); linear interpolation {u:.2f} eV{tag}")
            else:
                print("apex crossing: D = 1.6 eV not crossed inside the measured band")
            m_out.update(swing_V=swing, swing_window="[0, 9]",
                         swing_p7_window_V=swing_w, swing_edge_limited=bool(edge),
                         crossings=[[u, list(br)] for u, br in cx],
                         crossing_cell_conditional=cell_cond)

        flips = []
        seq = [r for r in full if not r["anchor"]]
        for r1, r2 in zip(seq[:-1], seq[1:]):
            if r1["pls"] != r2["pls"]:
                flips.append((r1["u"], r2["u"], r1["pls"], r2["pls"]))
        if flips:
            for a, b, p1, p2 in flips:
                print(f"pls flip {p1} -> {p2} between U = {a:g} and {b:g} eV")
        else:
            print("no pls flip inside the measured band")
        m_out["pls_flips"] = [list(f) for f in flips]
        result["metals"][metal] = m_out
        print()

    # --- A6.3 ordering test ----------------------------------------------------
    print("=" * 72)
    print("A6.3 ORDERING: eta(Ir) < eta(Ru) across U in [0, 9]?")
    ru = {r["u"]: r for r in result["metals"]["Ru"]["rows"] if "gap" not in r and not r["anchor"]}
    ir = {r["u"]: r for r in result["metals"]["Ir"]["rows"] if "gap" not in r and not r["anchor"]}
    shared = sorted(set(ru) & set(ir))
    inversions = []
    for u in shared:
        rel = "<" if ir[u]["eta"] < ru[u]["eta"] else ">="
        if rel == ">=":
            inversions.append(u)
        print(f"  U = {u:4.1f}:  eta(Ir) {ir[u]['eta']:.3f} {rel} eta(Ru) {ru[u]['eta']:.3f}"
              f"{'   INVERTED' if rel == '>=' else ''}")
    have_all = len(shared) == len(REF_GRID)
    if not have_all:
        print(f"  ({len(shared)}/{len(REF_GRID)} shared points measured -- "
              f"verdict below is over the measured points only)")
    if not shared:
        verdict63 = "WITHHELD"
        print("A6.3 VERDICT WITHHELD: no shared measured points -- the registered "
              "prediction is over U in [0, 9] and cannot be scored on nothing.")
    elif inversions:
        verdict63 = "INVERTED"
        print(f"A6.3 VERDICT: INVERTED at U = {inversions} -- the reference anchors are "
              f"U-conditional; every ranking claim in the report inherits that caveat.")
    else:
        verdict63 = "stable" if have_all else "stable-partial"
        print(f"A6.3 VERDICT: ordering Ir < Ru stable on all {len(shared)} measured "
              f"shared points"
              + ("" if have_all else " (grid incomplete -- partial, not the registered verdict)")
              + ".")
    result["ordering"] = dict(shared_points=shared, inversions=inversions,
                              complete=have_all, verdict=verdict63)

    if any_missing:
        print("\nNOTE: the grid has holes; registered bounds quoted from a "
              "holed grid are lower bounds on the swing, and say so.")

    if args.json:
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w") as fh:
            json.dump(result, fh, indent=2, default=str)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
