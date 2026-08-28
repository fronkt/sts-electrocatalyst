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

DISCLOSURE (wave-3 audit, 2026-08-28): the U = 0 decks drop the HUBBARD card
entirely rather than carrying an explicit U = 0 -- physically equivalent (and
what makes the determinism control byte-identical), but a second silent
difference at the U = 0 endpoint, so the "one variable across the grid"
discipline is exact only for U > 0. The Ru/Ir columns are nspin=1 nonmagnetic;
Cr is nspin=2 -- see the caveats block this script prints and banks.

Usage:  PYTHONPATH=src python src/dft/a0main_readout.py [--json docs/figs/a0main_readout.json]
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
            # qc.RY_EV is THE pipeline constant (every banked eV number used
            # it); a second higher-precision literal used to live here and was
            # a drift hazard (wave-3 audit) -- delta < 1e-9 V on any dG/eta.
            d = (a0 - pb) * qc.RY_EV * 1000
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
            row = dict(u=u, dG_OH=dg["OH"], dG_O=dg["O"], dG_OOH=dg["OOH"],
                       D=dg["O"] - dg["OH"], eta=r.overpotential,
                       pls=r.potential_limiting_step, closed_form_dev=ident,
                       anchor=(u == cfg["anchor"]))
            if row["anchor"]:
                # A7.1 fired, so the label must live in the artifact, not just
                # the stdout header (docs/45 wave-2 trap 4: labels travel).
                row["label"] = "XU-ANCHOR [PROJECTOR-MISMATCHED]"
                row["label_why"] = (
                    "Xu 2015's linear-response U was derived under a different "
                    "Hubbard projector than this grid's HUBBARD (atomic); "
                    "P-PROJ measured the eta consequence at |d-eta| = 0.487 V "
                    "(A7.1 FIRED, docs/figs/pproj_readout.json). Excluded from "
                    "every single-projector claim, including the A6.3 test.")
            rows.append(row)

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
    inversions, margins = [], {}
    for u in shared:
        m = ir[u]["eta"] - ru[u]["eta"]   # > 0 (and exact tie) counts INVERTED:
        margins[u] = m                    # conservative toward firing the caveat
        rel = "<" if m < 0 else ">="
        if rel == ">=":
            inversions.append(u)
        print(f"  U = {u:4.1f}:  eta(Ir) {ir[u]['eta']:.3f} {rel} eta(Ru) {ru[u]['eta']:.3f}"
              f"   margin {m:+.3f} V{'   INVERTED' if rel == '>=' else ''}")
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
        print(f"A6.3 VERDICT: INVERTED at U = {inversions} -- per the registration, "
              f"verbatim: the anchors against which every 3d result in this campaign "
              f"is reported are themselves U-conditional, and every ranking claim in "
              f"the report -- including the ones that survived P7 -- inherits that "
              f"caveat. (Blast radius as registered: reported as a sensitivity, not "
              f"applied as a correction; production stays at each tier's own U.)")
    else:
        verdict63 = "stable" if have_all else "stable-partial"
        print(f"A6.3 VERDICT: ordering Ir < Ru stable on all {len(shared)} measured "
              f"shared points"
              + ("" if have_all else " (grid incomplete -- partial, not the registered verdict)")
              + ".")

    # Margin credibility: each margin against the campaign's MEASURED error
    # classes (no new thresholds invented here -- the classes are prior banked
    # measurements, the 0.20 eV floor is A5.1(b)'s registered one).
    ERROR_CLASSES = [
        ("1x1 cell/coverage spread, 1A verdict (docs/45, ADOPT_2X1V)", 0.11, 0.36),
        ("NM-vs-AFM adsorption sensitivity, gate (h) (re-run owed)", 0.033, 0.064),
        ("Ir *OOH mirror-plane saddle depth (docs/45 row 1)", 0.291, 0.291),
    ]
    DISTINGUISH_FLOOR = 0.20   # A5.1(b), registered (Exner 2020)
    margin_ctx = {}
    if inversions:
        print("\nINVERSION MARGINS vs measured error classes "
              "(a margin below a class top cannot individually rule that error out):")
        for u in inversions:
            m = margins[u]
            inside = [name for name, lo, hi in ERROR_CLASSES if m <= hi]
            margin_ctx[u] = dict(margin_V=m, inside_error_classes=inside)
            print(f"  U = {u:4.1f}: +{m:.3f} V -- "
                  + (f"inside: {'; '.join(inside)}" if inside
                     else "clears the top of EVERY measured error class"))
        clear = [u for u in inversions
                 if not margin_ctx[u]["inside_error_classes"]]
        carried = (f"carried outright by U = {clear}; the other inverted points "
                   f"are context, not independent evidence"
                   if clear else
                   "NOT carried outright by any single point -- every margin sits "
                   "inside at least one measured error class; the verdict is "
                   "error-class-conditional")
        print(f"  => the binary registered prediction ('inverts anywhere in the "
              f"band') is {carried}.")
    holds = [u for u in shared if u not in inversions]
    holds_below_floor = bool(holds) and all(
        abs(margins[u]) < DISTINGUISH_FLOOR for u in holds)
    if holds and holds_below_floor:
        worst = max(abs(margins[u]) for u in holds)
        print(f"  Symmetric note: every 'holds' margin (largest {worst:.3f} V) is "
              f"below A5.1(b)'s registered {DISTINGUISH_FLOOR:.2f} eV distinguishability "
              f"floor -- the ordering was never POSITIVELY resolved at any measured U, "
              f"production U = 0 included. The report may not claim Ir < Ru holds "
              f"anywhere; this strengthens the U-conditionality consequence.")
    result["ordering"] = dict(
        shared_points=shared, inversions=inversions, complete=have_all,
        verdict=verdict63, margins_V=margins,
        margin_context={str(k): v for k, v in margin_ctx.items()},
        error_classes=[list(c) for c in ERROR_CLASSES],
        inversions_clearing_every_error_class=[
            u for u in inversions if not margin_ctx[u]["inside_error_classes"]],
        holds_below_distinguishability_floor=holds_below_floor,
        distinguishability_floor_eV=DISTINGUISH_FLOOR,
        consequence=("the anchors against which every 3d result in this campaign "
                     "is reported are themselves U-conditional, and every ranking "
                     "claim in the report -- including the ones that survived P7 -- "
                     "inherits that caveat (docs/43 A6.3, verbatim; sensitivity, "
                     "not correction)") if verdict63 == "INVERTED" else None)

    # --- A7.2 prediction status (registered, already decidable) ---------------
    flips_by_metal = {m: result["metals"][m].get("pls_flips", [])
                      for m in result["metals"]}
    metals_with_flip = sorted(m for m, f in flips_by_metal.items() if f)
    A72_ROSTER = ["Cr", "Mn", "Fe", "Ru", "Ir", "Ti"]
    unrun = [m for m in A72_ROSTER if m not in result["metals"]]
    a72_status = "CONFIRMED" if len(metals_with_flip) >= 3 else "OPEN"
    print("\nA7.2 PREDICTION STATUS: registered '>=3 of 6 metals (Cr, Mn, Fe, Ru, "
          "Ir, Ti) show a pls flip inside the registered A0 grid'. Metals run with "
          f"a flip: {metals_with_flip} ({len(metals_with_flip)} of the "
          f"{len(result['metals'])} run) -> {a72_status}"
          + (f" regardless of the unrun {unrun} -- additional metals can only add "
             f"flips, never remove one." if a72_status == "CONFIRMED" else
             f"; awaiting {unrun}."))
    result["a7_2"] = dict(
        prediction=">=3 of 6 metals (Cr, Mn, Fe, Ru, Ir, Ti) show a pls flip "
                   "inside the registered A0 grid",
        status=a72_status, metals_with_flip=metals_with_flip,
        flip_brackets={m: f for m, f in flips_by_metal.items() if f},
        unrun_blind_metals=unrun,
        note="the Ir bracket is saddle-conditional (see caveats.ir_ooh_basin); "
             "the EXISTENCE of an Ir flip inside the grid survives the saddle "
             "correction, so the CONFIRMED status does not rest on the bracket")

    # --- registered + measured caveats (travel with every table above) --------
    caveats = dict(
        fixed_geometry=(
            "A6.4, registered: every point is a fixed-geometry single-point SCF "
            "on the production-tier geometry (relaxed at each tier's own U -- "
            "Ru/Ir tier carries no U, Cr tier U = 3.70). A0 measures the "
            "U-response of energies at frozen geometry and cannot see a "
            "U-driven geometry change; where A0 and a relaxed point disagree, "
            "the relaxed point wins and the discrepancy is reported, not "
            "averaged. NOTHING in this readout is a relaxed result; no relaxed "
            "Ru/Ir point at U > 0 exists anywhere in the campaign."),
        spin_state=(
            "MEASURED CONSTRAINT: the Ru/Ir columns are nspin=1 nonmagnetic by "
            "construction, while gate (h) measured 4/4 ADOPT_AFM on the RuO2 "
            "anchors with 0.033-0.064 eV adsorption-energy movement (AFM re-run "
            "owed, S0(h)). Margins smaller than that class -- the U <= 4.5 "
            "ordering rows and the Ir flip bracket's low edge -- are "
            "spin-state-conditional. Cr runs nspin=2, so any Cr-vs-anchor "
            "comparison additionally crosses spin treatments."),
        ir_ooh_basin=(
            "MEASURED: the Ir chain inherits the 1x1 *OOH geometry convicted as "
            "a mirror-plane saddle 0.291 eV high (docs/45 row 1). It CANNOT "
            "manufacture the A6.3 inversion: every inverted point has Ir on "
            "pls 2, where dG_OOH does not enter eta, and correcting the saddle "
            "LOWERS eta(Ir) at low U -- the opposite direction. It does "
            "condition Ir's pls-3 rows (U <= 3) and the Ir flip bracket "
            "[3, 4.5]: under a rigid -0.291 eV shift the flip moves earlier "
            "(approx. [0, 1.5]) but still occurs inside the grid."),
        cell=(
            "REGISTERED CHOICE: this grid lives in the 1x1 cell the campaign "
            "retired for production (1A verdict ADOPT_2X1V); A6.1(a)/A6.3 chose "
            "it knowingly, after that verdict, to bound the 1x1-era claims. The "
            "2x1v ordering at U > 0 is unmeasured."),
        coverage_shortfall=(
            "A6.3 registers the grid over 'Ru and Ir as well as the 3d metals' "
            "and A7.2/A7.3 name Mn, Fe, Ti as blind metals; as built, the arm "
            "runs Cr/Ru/Ir only (allocation Cr 19 / Ru 7+1 / Ir 7+1 chosen by "
            "the entrant 2026-08-27 with no dated amendment -- a dated "
            "correction of record is owed; docs/45). Nothing exists for "
            "Mn/Fe/Ti; their A7.2/A7.3 rows are unrun, not failed. Under "
            "A7.7's disposition rule, whatever stays unscored at freeze is "
            "WITHDRAWN-UNSCORED, not quietly dropped."),
        u000_decks=(
            "the U = 0 decks drop the HUBBARD card entirely rather than "
            "carrying U = 0 explicitly -- physically equivalent, but a second "
            "silent difference at the U = 0 endpoint (projector machinery off "
            "vs on-with-zero), disclosed here."))
    print("\nCAVEATS (registered + measured; they travel with every table above):")
    for k, v in caveats.items():
        print(f"  [{k}] {v}")
    result["caveats"] = caveats

    # --- gas-reference disclosure (owed since wave 2) -------------------------
    # The three metals' gas references are one calculation, copied: H2O.out and
    # H2.out under Cr_slab/, Ru_anchor/ and Ir_anchor/ are md5-identical files.
    # Physically that is what SHOULD be true (a gas molecule in a box knows no
    # metal), so no eta difference can come from the references -- but a reader
    # counting "independent" gas runs would over-count, so it is said here and
    # measured live rather than asserted.
    import hashlib
    sigs = {}
    for m, cfg in METALS.items():
        for g in ("H2O", "H2"):
            gp = os.path.join(ROOT, "runs", cfg["gas_run"], f"{g}.out")
            sigs.setdefault(g, {})[m] = hashlib.md5(open(gp, "rb").read()).hexdigest()
    identical = all(len(set(d.values())) == 1 for d in sigs.values())
    print("\nGAS-REFERENCE DISCLOSURE: the three metals' H2O/H2 reference outputs "
          + ("are md5-identical copies of ONE calculation each"
             if identical else
             "DIFFER across metals -- UNEXPECTED, investigate before quoting eta")
          + " (metal-independent by construction; identical references cannot "
            "CREATE a spurious cross-metal difference, and none of them is an "
            "independent replication. Scope: same-pls comparisons are "
            "reference-free; different-pls comparisons -- every INVERTED A6.3 "
            "point pairs Ir pls 2 with Ru pls 3 -- inherit the absolute H2O "
            "reference one-for-one via eta(Ir)-eta(Ru) = dG2(Ir)-dG3(Ru).)")
    for g, d in sigs.items():
        vals = sorted(set(d.values()))
        print(f"  {g}: md5 {vals[0] if len(vals) == 1 else d}")
    result["gas_reference_disclosure"] = dict(
        identical_across_metals=identical, md5=sigs,
        note=("one calculation per species, copied into each metal's reference "
              "directory; physically metal-independent, disclosed so nothing "
              "counts them as independent runs. Identical references cannot "
              "create a spurious cross-metal difference; same-pls comparisons "
              "are reference-free, but different-pls comparisons (every "
              "INVERTED A6.3 point) inherit the absolute H2O reference "
              "one-for-one"))

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
