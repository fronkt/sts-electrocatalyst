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
import datetime
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

STATES = ("slab", "s0_O", "s0_OH", "s0_OOH")
CR_GRID = [round(0.5 * i, 2) for i in range(19)]
REF_GRID = [0.0, 1.5, 3.0, 4.5, 6.0, 7.5, 9.0]
# control = (a0_token, probe_dir, probe_suffix): the A0 deck at a0_token is
# byte-identical (except the prefix line; tranche 2's nonzero-U decks are also
# one trailing byte short -- docs/45 trap 6) to runs/probe/<probe_dir>/
# <state>__<probe_suffix>, so the energy drift measures re-run agreement.
# control_class says WHICH agreement: Cr/Ru/Ir and Ti re-run on the same
# machine (determinism); Mn/Fe re-run Vast audit decks on Anvil (A8.5
# cross-machine parity, threshold 1e-5 Ry = 0.136 meV using this
# pipeline's own RY_EV -- tighter than the 5 meV extraction tolerance).
# Only the 5 meV tolerance is ENFORCED here (--tol-mev); the 1e-5 Ry
# figure is quoted for scale and is not separately gated, so it is
# stated as context rather than as a second implemented check.
# control_override redirects ONE state's comparator: Fe s0_OOH's probe base is
# the MEASURED trapped branch (+276.60 meV, docs/41 s6d), so comparing the
# mag-0.1 u530 rung against it would manufacture a fake failure; the honest
# same-machine pair is the u530 rung vs the accepted pilot deck (byte-identical
# except prefix, both Anvil).
METALS = {
    "Cr": dict(grid=CR_GRID, anchor=None, gas_run="Cr_slab", production_u=3.70,
               control=("u000", "Cr", "u0.0"), control_class="same-machine"),
    "Ru": dict(grid=REF_GRID, anchor=6.73, gas_run="Ru_anchor", production_u=0.0,
               control=("u000", "Ru", "base"), control_class="same-machine"),
    "Ir": dict(grid=REF_GRID, anchor=5.91, gas_run="Ir_anchor", production_u=0.0,
               control=("u000", "Ir", "base"), control_class="same-machine"),
    "Mn": dict(grid=sorted(set(REF_GRID) | {3.90}), anchor=None,
               gas_run="Mn_slab", production_u=3.90,
               control=("u390", "Mn_audit", "base"),
               control_class="cross-machine (Vast audit deck re-run on Anvil, A8.5)"),
    "Fe": dict(grid=sorted(set(REF_GRID) | {5.30}), anchor=None,
               gas_run="Fe_slab", production_u=5.30,
               control=("u530", "Fe_audit", "base"),
               control_class="cross-machine (Vast audit deck re-run on Anvil, A8.5)",
               control_override={"s0_OOH": ("a0", "s0_OOH__pilot530_m010",
                                            "same-machine (u530 rung vs accepted "
                                            "pilot; probe base is the measured "
                                            "trapped branch, docs/41 s6d)")}),
    "Ti": dict(grid=REF_GRID, anchor=None, gas_run="Ti_slab", production_u=0.0,
               control=("u000", "Ti_audit", "base"), control_class="same-machine"),
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


def _totmag(path):
    """Final `total magnetization` in Bohr mag/cell, or None for nspin=1.

    A0's two repaired Fe points sit on a near-degenerate crossing between two
    magnetic branches (docs/59 s3c), so which branch a row landed on is part
    of the reading, not a footnote. Reported for every spin-polarised row.
    """
    if not os.path.exists(path):
        return None
    m = None
    for line in open(path, errors="replace"):
        if "total magnetization" in line:
            hit = re.search(r"=\s*([-\d.]+)", line)
            if hit:
                m = float(hit.group(1))
    return m


def _upstream_block(runsdir, state):
    """Why a state has no A0 deck: unrun, or blocked by a failed relaxation.

    Every A0 point is a fixed-geometry SCF standing on a relaxed geometry from
    runs/<metal>_slab/<state>.out. If that relaxation never converged, the A0
    deck was never built -- and calling the resulting hole "not yet run" would
    hide the campaign's most consequential non-convergence behind a queue
    position. Returns (reason, attempts) or (None, []).
    """
    base = os.path.join(ROOT, "runs", runsdir)
    if not os.path.isdir(base):
        return None, []
    attempts = []
    for fn in sorted(os.listdir(base)):
        if not fn.endswith(".out"):
            continue
        stem = fn[:-4]
        if stem != state and not stem.startswith(state + "_r"):
            continue
        txt = open(os.path.join(base, fn), errors="replace").read()
        ok = "bfgs converged" in txt and "convergence NOT achieved" not in txt
        attempts.append((stem, "converged" if ok else "NOT CONVERGED"))
    if not attempts:
        return None, []
    if any(s == "converged" for _, s in attempts):
        return None, attempts
    return ("UPSTREAM GEOMETRY BLOCKED: the %s relaxation has not converged "
            "(%s); no A0 deck can be built on it, so this is a convergence "
            "event upstream, NOT an unrun point. See runs/a0/main/manifest.json "
            "and docs/59." % (state,
                              ", ".join("%s %s" % a for a in attempts)),
            attempts)


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

    # A6.5(2)(i) repair registry: rows of runs/a0/m_a0_repairs.txt map a
    # repaired stem to the parent density it restarted from, so the label the
    # escalation requires travels into the row from the manifest itself
    # (single source; nothing hard-coded here).
    repairs = {}
    for rman in sorted(glob.glob(os.path.join(ROOT, "runs", "a0",
                                              "m_a0_repairs*.txt"))):
        for line in open(rman):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            d, job, _suf, _nk, parent = line.split()
            key = (os.path.basename(d), job)
            if key in repairs and repairs[key] != parent:
                raise SystemExit("REFUSING TO SCORE: %s registers %s twice "
                                 "with different parents (%s, %s)"
                                 % (rman, job, repairs[key], parent))
            repairs[key] = parent

    for metal, cfg in METALS.items():
        print("=" * 72)
        arm = {"Cr": "location arm", "Ru": "ordering arm", "Ir": "ordering arm"}\
            .get(metal, "blind-metal arm (A7.2/A7.3; tranche 2/3, docs/59)")
        print(f"{metal}  ({arm})")
        gas = {}
        for g in ("H2O", "H2"):
            p = os.path.join(ROOT, "runs", cfg["gas_run"], f"{g}.out")
            e = qc.trusted_energy_ev(p, strict=True) if os.path.exists(p) else None
            if e is None:
                sys.exit(f"REFUSING: {metal} gas reference {p} missing or failed QC")
            gas[g] = e

        # --- extraction control ------------------------------------------------
        tok, probe_dir, probe_sfx = cfg["control"]
        drift = {}
        override_notes = {}
        ok = True
        uncompared = {}
        control_failed = {}
        for st in STATES:
            a0p = os.path.join(ROOT, "runs", "a0", "main", metal,
                               f"{st}__{tok}.out")
            a0 = _final_ry(a0p)
            ov = cfg.get("control_override", {}).get(st)
            if ov is not None:
                # comparator redirected (see METALS comment); path under a0/main
                _, ov_stem, ov_why = ov
                cmpp = os.path.join(ROOT, "runs", "a0", "main", metal,
                                    f"{ov_stem}.out")
                override_notes[st] = f"comparator {ov_stem}: {ov_why}"
            else:
                cmpp = os.path.join(ROOT, "runs", "probe", probe_dir,
                                    f"{st}__{probe_sfx}.out")
            pb = _final_ry(cmpp)
            if a0 is None or pb is None:
                # THREE cases, not two. _final_ry returns None both for a file
                # that is absent and for one that exists but never printed a
                # final energy -- which is exactly what an SCF that hit
                # electron_maxstep leaves behind. A deck that RAN AND DIED is a
                # convergence event (A8.4), never pending data.
                drift[st] = None
                dead = [os.path.relpath(q, ROOT).replace("\\", "/")
                        for q, v in ((a0p, a0), (cmpp, pb))
                        if v is None and os.path.exists(q)]
                if dead:
                    ok = False
                    control_failed[st] = dead
                else:
                    uncompared[st] = [
                        os.path.relpath(q, ROOT).replace("\\", "/")
                        for q, v in ((a0p, a0), (cmpp, pb)) if v is None]
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
        n_cmp = len(STATES) - len(uncompared) - len(control_failed)
        if not ok:
            verdict = "FAIL"
        elif uncompared:
            verdict = f"INCOMPLETE ({n_cmp}/{len(STATES)} states compared)"
        else:
            verdict = "OK"
        print(f"re-run agreement check ({tok} vs probe {probe_dir}/{probe_sfx}; "
              f"decks identical except prefix, NOT a geometry round-trip control; "
              f"class: {cfg['control_class']}; meV): {ds}  {verdict}")
        for st, note in override_notes.items():
            print(f"  control override [{st}]: {note}")
        if control_failed:
            print(f"  {metal}: control deck(s) RAN AND PRODUCED NO ENERGY "
                  f"{sorted(control_failed)} -- an SCF failure (A8.4), not "
                  f"pending data; files: "
                  f"{sorted(f for v in control_failed.values() for f in v)}. "
                  f"This metal's rows are reported but marked UNTRUSTED until "
                  f"reconciled.")
        elif not ok:
            print(f"  {metal}: control DISAGREES beyond {args.tol_mev} meV -- "
                  f"this metal's rows are reported but marked UNTRUSTED until "
                  f"reconciled.")
        if uncompared:
            # Say WHICH side is missing. "completes when those states run" is
            # false when the comparator itself is blocked upstream.
            for st, miss in sorted(uncompared.items()):
                blocked, _att = _upstream_block(cfg["gas_run"], st)
                tail = (" BLOCKED UPSTREAM: " + blocked) if blocked else                        " -- the control completes when these run."
                print(f"  {metal}: control not evaluable for {st}; no final "
                      f"energy in {miss}.{tail}")
            print(f"  {metal}: the {n_cmp} state(s) that COULD be compared all "
                  f"agree -- not a disagreement.")

        # --- the grid ----------------------------------------------------------
        points = list(cfg["grid"]) + ([cfg["anchor"]] if cfg["anchor"] else [])
        rows, gaps = [], []
        for u in sorted(points):
            E = {}
            why = {}
            repaired = {}
            totmag = {}
            for st in STATES:
                p = os.path.join(ROOT, "runs", "a0", "main", metal, f"{st}__{u_token(u)}.out")
                if not os.path.exists(p):
                    E[st] = None
                    blocked, _att = _upstream_block(cfg["gas_run"], st)
                    why[st] = blocked or "absent"
                    continue
                E[st] = qc.trusted_energy_ev(p, strict=True)
                if E[st] is not None:
                    mg = _totmag(p)
                    if mg is not None:
                        totmag[st] = mg
                if E[st] is None:
                    why[st] = "qc-fail"
                    # A6.5(2)(i): a registered repair may stand in for a
                    # QC-failed point -- never for a passing one, and only if
                    # the repair itself passes strict QC. The failed .out
                    # stays on disk and in the A8.4 failure count.
                    stem = f"{st}__{u_token(u)}__"
                    cand = sorted(j for (m, j) in repairs
                                  if m == metal and j.startswith(stem))
                    won, lost = [], []
                    for j in cand:
                        rp = os.path.join(ROOT, "runs", "a0", "main", metal,
                                          f"{j}.out")
                        if not os.path.exists(rp):
                            lost.append((j, None, "not run"))
                            continue
                        er = qc.trusted_energy_ev(rp, strict=True)
                        if er is None:
                            lost.append((j, None, "failed QC"))
                        else:
                            won.append((er, j, _totmag(rp)))
                    if won:
                        # Pre-declared before either deck ran
                        # (build_a0main_w2c.py): where more than one registered
                        # repair converges, the LOWER total energy is the
                        # banked point and the difference is REPORTED as the
                        # measured branch splitting. Never the higher one.
                        won.sort()
                        er, j, mag = won[0]
                        E[st] = er
                        why.pop(st, None)
                        note = ("A6.5(2) REPAIR %s, RESTARTED FROM %s DENSITY "
                                "(original SCF failed at 200 iterations; "
                                "failed .out retained, A8.4)"
                                % (j, repairs[(metal, j)]))
                        if mag is not None:
                            note += "; totmag %.2f" % mag
                            totmag[st] = mag
                        if len(won) > 1:
                            gapmeV = (won[1][0] - won[0][0]) * 1000.0
                            note += ("; %d registered repairs converged, "
                                     "LOWER wins by %.1f meV over %s "
                                     "(measured branch splitting)"
                                     % (len(won), gapmeV, won[1][1]))
                        # "did not converge" and "has not run" are DIFFERENT
                        # claims. Collapsing them would report a launched-but-
                        # pending deck as a convergence failure -- an A8.4
                        # quantity -- purely because its output has not landed.
                        bad = [a for a, _b, c in lost if c == "failed QC"]
                        pend = [a for a, _b, c in lost if c == "not run"]
                        if bad:
                            note += "; did not converge: %s" % ", ".join(bad)
                        if pend:
                            note += "; still pending: %s" % ", ".join(pend)
                        repaired[st] = note
                    elif cand:
                        bad = [a for a, _b, c in lost if c == "failed QC"]
                        pend = [a for a, _b, c in lost if c == "not run"]
                        if pend:
                            # The ladder is NOT exhausted while a registered
                            # repair is still in flight, so this row must not
                            # read as rung (iii) NOT_CONVERGED.
                            why[st] = ("qc-fail (%d of %d registered repairs "
                                       "failed: %s; %d NOT YET RUN, so the "
                                       "A6.5(2) ladder is NOT exhausted: %s)"
                                       % (len(bad), len(cand),
                                          ", ".join(bad) or "none",
                                          len(pend), ", ".join(pend)))
                        else:
                            why[st] = ("qc-fail (all %d registered repairs also "
                                       "failed: %s -- A6.5(2)(iii) "
                                       "NOT_CONVERGED)"
                                       % (len(cand), ", ".join(cand)))
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
            if repaired:
                row["repaired"] = repaired
            if totmag:
                row["totmag"] = {k: round(v, 2) for k, v in totmag.items()}
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
            if r.get("repaired"):
                tag += "  [" + "; ".join(f"{st}: {note}"
                                         for st, note in r["repaired"].items()) + "]"
            cf = ""
            if r["closed_form_dev"] is not None and r["closed_form_dev"] > 1e-9:
                cf = f"  CLOSED-FORM DEV {r['closed_form_dev']:.2e}"
            elif r["closed_form_dev"] is None:
                # A7.2's identity is defined only for pls in {2,3}. On a
                # pls 1 or 4 row there is no check running at all, and
                # those are exactly the rows where the dG ladder has gone
                # non-monotonic -- including the upper endpoint of Fe's
                # contribution to the A7.2 census. Say so rather than
                # letting a blank column read as "checked and clean".
                cf = "  [no closed-form check: defined only for pls 2/3]"
            print(f"{r['u']:7.2f} {r['dG_OH']:7.3f} {r['dG_O']:7.3f} "
                  f"{r['dG_OOH']:7.3f} {r['D']:7.3f} {r['eta']:7.3f} "
                  f"{r['pls']:4d}{tag}{cf}")
        if gaps:
            # `ws` is a LIST of why-strings, so `"qc-fail" in ws` was an
            # exact-element test: it matched the bare "qc-fail" but NOT
            # "qc-fail (all 3 registered repairs also failed: ...)", which
            # silently reported a real convergence event as "not yet run".
            # A8.4 makes the failure rate a reported quantity, so this had to
            # be a substring test over the elements.
            n_fail = sum(1 for _, _, ws in gaps
                         if any("qc-fail" in w for w in ws))
            n_block = sum(1 for _, _, ws in gaps
                          if any("UPSTREAM GEOMETRY BLOCKED" in w for w in ws))
            n_abs = len(gaps) - n_fail - n_block
            msg = f"GAPS: {len(gaps)} point(s)"
            if n_abs:
                # This readout sees only runs/a0/main/<metal>; it can say a
                # deck is absent, and (via _upstream_block) that a relaxation
                # blocked it, but it may not assert WHY an otherwise-absent
                # point is absent.
                msg += (f" -- {n_abs} with no A0 deck present in "
                        f"runs/a0/main/{metal}")
            if n_block:
                msg += (f" -- {n_block} BLOCKED UPSTREAM by a non-convergent "
                        f"relaxation (a convergence event, not an unrun point)")
            if n_fail:
                msg += (f" -- {n_fail} QC-FAILED: A6.5(2) escalation owed: "
                        f"(i) startingpot from converged neighbour, (ii) halve beta, "
                        f"(iii) NOT_CONVERGED, plotted as a hole")
            print(msg + ".")

        full = [r for r in rows if "gap" not in r]
        m_out = dict(gas=gas, rerun_determinism_check_meV=drift, control_ok=ok,
                     control_uncompared_states=sorted(uncompared),
                     control_uncompared_missing_files=uncompared,
                     control_decks_ran_and_failed=control_failed,
                     control_class=cfg["control_class"],
                     control_note=("same-deck re-run: the A0 control deck is identical "
                                   "to its probe comparator except the prefix line "
                                   "(tranche-2 nonzero-U decks also one trailing byte "
                                   "short, docs/45 trap 6), so this drift measures SCF "
                                   "re-run agreement in the named class, not a geometry "
                                   "round-trip; the genuine extraction control "
                                   "(SCF vs source relaxation) lives in the a0cell "
                                   "readout for Cr/Ru/Ir and in probe_manifest "
                                   "relax_reference_ev for Mn/Fe/Ti"),
                     control_overrides=override_notes or None,
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
        elif len(seq) < 2:
            # "no flip" is a measurement; with fewer than two scored rows there
            # is nothing to measure, and banking [] would be indistinguishable
            # from a complete, genuinely flat grid.
            print(f"NO FLIP STATEMENT POSSIBLE: {len(seq)} scored non-anchor "
                  f"row(s) -- a flip needs two consecutive ones")
        else:
            print("no pls flip inside the measured band")
        m_out["pls_flips"] = [list(f) for f in flips]
        m_out["pls_flips_measurable"] = len(seq) >= 2
        m_out["scored_rows"] = len(seq)
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
    # a metal whose grid is ALL holes is configured but pending data -- it has
    # not been "run" in any sense the census may count
    pending = [m for m in A72_ROSTER if m in result["metals"] and
               not any("gap" not in r for r in result["metals"][m]["rows"])]
    measured = [m for m in A72_ROSTER
                if m in result["metals"] and m not in pending]
    a72_status = "CONFIRMED" if len(metals_with_flip) >= 3 else "OPEN"
    print("\nA7.2 PREDICTION STATUS: registered '>=3 of 6 metals (Cr, Mn, Fe, Ru, "
          "Ir, Ti) show a pls flip inside the registered A0 grid'. Metals measured "
          f"with a flip: {metals_with_flip} ({len(metals_with_flip)} of "
          f"{len(measured)} measured) -> {a72_status}"
          + (f" -- additional metals or grid points can only add flips, never "
             f"remove one" if a72_status == "CONFIRMED" else "")
          + (f"; pending data: {pending}" if pending else "")
          + (f"; unrun: {unrun}" if unrun else "") + ".")
    result["a7_2"] = dict(
        prediction=">=3 of 6 metals (Cr, Mn, Fe, Ru, Ir, Ti) show a pls flip "
                   "inside the registered A0 grid",
        status=a72_status, metals_with_flip=metals_with_flip,
        flip_brackets={m: f for m, f in flips_by_metal.items() if f},
        metals_measured=measured, pending_data=pending,
        unrun_blind_metals=unrun,
        note="the Ir bracket is saddle-conditional (see caveats.ir_ooh_basin); "
             "the EXISTENCE of an Ir flip inside the grid survives the saddle "
             "correction, so the CONFIRMED status does not rest on the bracket")

    # --- A7.3 P-FLOOR-U ------------------------------------------------------
    # docs/43:1361-1379, quoted: "Quantity: span(c_M)/2 in volts, at FIXED
    # endpoints U = 0 and U = U_max -- never max-minus-min over a grid.
    # PREDICTION: span(c_M)/2 exceeds 0.10 V on >=4 of the 6 metals with a
    # converged *OOH geometry. FALSIFIED if <=1 of 6 exceeds 0.10 V".
    # Every quantity here is registered; nothing is set locally. This block
    # exists because A7.2 and A7.3 are siblings scored off the SAME banked rows,
    # and reporting only the one that CONFIRMED would be selective.
    A73_FLOOR = 0.10          # V, registered
    A73_NEEDED = 4            # metals, registered
    A73_FALSIFY_AT = 1        # <= this many, registered
    a73_rows, a73_pending = {}, []
    for m, cfg in METALS.items():
        rows = {r["u"]: r for r in result["metals"][m]["rows"] if "gap" not in r}
        u_max = max(cfg["grid"])
        lo, hi = rows.get(0.0), rows.get(u_max)
        if lo is None or hi is None:
            a73_pending.append(m)
            continue
        c_lo = lo["dG_OOH"] - lo["dG_OH"]
        c_hi = hi["dG_OOH"] - hi["dG_OH"]
        half = abs(c_lo - c_hi) / 2.0
        a73_rows[m] = dict(u_lo=0.0, u_hi=u_max, c_M_lo=c_lo, c_M_hi=c_hi,
                           span_over_2_V=half, exceeds_floor=half > A73_FLOOR)
    over = sorted(m for m, r in a73_rows.items() if r["exceeds_floor"])
    if len(over) >= A73_NEEDED:
        a73_status = "CONFIRMED"
    elif len(a73_rows) - len(over) > len(METALS) - A73_FALSIFY_AT - 1             and len(over) <= A73_FALSIFY_AT and not a73_pending:
        a73_status = "FALSIFIED"
    elif a73_pending:
        a73_status = "NOT YET MET -- UNDECIDED (pending metals could still reach it)"
    else:
        a73_status = "NOT MET"
    print("")
    print("A7.3 P-FLOOR-U: registered 'span(c_M)/2 exceeds 0.10 V on >=4 of "
          "the 6 metals with a converged *OOH geometry' (c_M = dG_OOH - dG_OH, "
          "at the FIXED endpoints U = 0 and U = U_max, never max-minus-min).")
    for m in sorted(a73_rows):
        r = a73_rows[m]
        print("  %-3s c_M(0)=%.4f  c_M(%.1f)=%.4f  span/2=%.4f V  %s"
              % (m, r["c_M_lo"], r["u_hi"], r["c_M_hi"], r["span_over_2_V"],
                 "EXCEEDS" if r["exceeds_floor"] else "below floor"))
    for m in a73_pending:
        print("  %-3s NO ENDPOINTS SCORED -- excluded from the denominator by "
              "the registration's own conditioning ('with a converged *OOH "
              "geometry')" % m)
    print("A7.3 VERDICT: %d of %d scorable metals exceed %.2f V -> %s"
          % (len(over), len(a73_rows), A73_FLOOR, a73_status))
    if a73_pending and len(over) < A73_NEEDED:
        print("  DECIDING METAL(S): %s. With %d already over the floor and a "
              "threshold of >=%d, the prediction turns on whether the pending "
              "metal(s) clear it. Reported here NOT MET rather than omitted: "
              "A7.2 and A7.3 are scored off the same banked rows and only one "
              "of them currently passes." % (a73_pending, len(over), A73_NEEDED))
    print("  DISCLOSED NON-BLIND (registered): Cr. The registration quotes Cr "
          "at 0.223 V over U = 0 -> 5.00; this grid's registered endpoints are "
          "U = 0 -> %.1f, which is a DIFFERENT interval and gives %.4f V. The "
          "two are not the same measurement and neither replaces the other."
          % (max(METALS["Cr"]["grid"]),
             a73_rows["Cr"]["span_over_2_V"] if "Cr" in a73_rows else float("nan")))
    result["a7_3"] = dict(
        prediction="span(c_M)/2 exceeds 0.10 V on >=4 of the 6 metals with a "
                   "converged *OOH geometry; FALSIFIED if <=1 of 6 exceeds it",
        quantity="span(c_M)/2 at FIXED endpoints U = 0 and U = U_max, "
                 "c_M = dG_OOH - dG_OH",
        floor_V=A73_FLOOR, needed=A73_NEEDED, status=a73_status,
        per_metal=a73_rows, exceeds=over,
        denominator=len(a73_rows), pending_no_endpoints=a73_pending,
        blind=["Mn", "Fe", "Ru", "Ir", "Ti"], disclosed_non_blind=["Cr"],
        note="the registration's disclosed Cr value (0.223 V) is measured over "
             "U = 0 -> 5.00, not this grid's U = 0 -> 9.0 endpoints; both are "
             "reported and neither is substituted for the other")

    # --- registered + measured caveats (travel with every table above) --------
    caveats = dict(
        fixed_geometry=(
            "A6.4, registered: every point is a fixed-geometry single-point SCF "
            "on a geometry relaxed at that metal's own production U "
            "(Cr 3.70, Mn 3.90, Fe 5.30; Ru/Ir/Ti carry no U by the MP "
            "convention). For Cr/Ru/Ir/Mn/Fe that geometry is the banked "
            "production tier. Ti's is NOT inherited: TiO2 had no slab or "
            "adsorbate geometry anywhere in the campaign, so its slab, *O "
            "and *OH geometries were built and relaxed inside tranche 3 "
            "(2026-08-28/29, docs/59 s3) and its *OOH geometry does not "
            "exist at all -- which is why the Ti grid scores 0 of 7. "
            "A0 measures the "
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
            "spin-state-conditional. Cr, Mn and Fe run nspin=2, so any "
            "3d-vs-anchor comparison additionally crosses spin treatments; "
            "Fe's s0_OOH column runs at the pilot-selected starting guess "
            "(mag 0.1, the relax branch -- manifest tranche_2b; the 0.5 "
            "cold start is a measured +276.60 meV trap). Ti runs nspin=1 "
            "by construction (gen_rutile.py emits the spin block only "
            "where a species carries a non-zero starting magnetization, "
            "and TiO2 is entered mag=0.0). That is a SUBSTRATE d0 "
            "argument and it does NOT extend to the adsorbates: pw.x "
            "reports 144/150/151/157 electrons for Ti slab/*O/*OH/*OOH, "
            "so *OH and *OOH are ODD-electron and nspin=1 cannot "
            "spin-split them. docs/59 s3c registers exactly that as the "
            "diagnosis of the Ti *OOH relaxation failure and leaves "
            "nspin=2 for the Ti arm as an OPEN question for the entrant; "
            "every Ti row is spin-convention-conditional in a way the "
            "nspin=2 Cr/Mn/Fe rows are not."),
        mn_afm=(
            "REGISTERED CONDITION, CURRENTLY UNMET (A7.5, quoted): "
            "'beta-MnO2 is antiferromagnetic and gen_rutile.py initialises it FM -- either the AFM arm runs or every materials-facing Mn sentence is struck.' gen_rutile.py enters MnO2 at mag=0.5 (FM) and "
            "no AFM arm has been run, so the 8-point absolute eta(U) "
            "column banked here for Mn is FM-initialised. Under A7.5 it "
            "may be used for the within-metal, U-response claims it was "
            "registered for (A7.2's flip census, A7.3's span) but NOT "
            "as a materials-facing absolute eta for beta-MnO2. Same "
            "amendment's tier strata: TiO2/beta-MnO2/RuO2/IrO2 = "
            "REAL-AMBIENT-UNDISTORTED, CrO2 = "
            "REAL-UNDISTORTED-METASTABLE, FeO2 = MODEL PHASE (method "
            "test system only) -- so the Cr and Fe absolute eta columns "
            "are likewise not materials claims."),
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
            "and A7.2/A7.3 name Mn, Fe, Ti as blind metals; tranche 1 ran "
            "Cr/Ru/Ir only (allocation Cr 19 / Ru 7+1 / Ir 7+1 chosen by the "
            "entrant 2026-08-27 with no dated amendment -- the dated "
            "correction of record is docs/59, drafted for the entrant to "
            "countersign and deposit). REMEDIATION: the entrant directed the "
            "extension 2026-08-28 ('Do them over Mn/Fe/Ti then'); tranches "
            "2/2b/3/2c (build_a0main_w2/_w2b/_w3/_w2c, each committed "
            "pre-launch) cover the blind metals -- 2c is the escalation "
            "round that produced the banked Fe U = 4.5 point via "
            "A6.5(2)(ii), and is therefore the reason Fe can be called "
            "complete at all. Live status at scoring time: "
            + "; ".join(
                (f"{m} scored" + (f" with {len(result['metals'][m]['gaps'])} "
                                  f"hole(s)" if result['metals'][m]['gaps']
                                  else " complete"))
                if m in result["metals"] and
                   any("gap" not in r for r in result["metals"][m]["rows"])
                else f"{m} NOT YET SCORED"
                for m in ("Mn", "Fe", "Ti"))
            + ". Under A7.7's disposition rule, whatever stays unscored at "
              "freeze is WITHDRAWN-UNSCORED, not quietly dropped."),
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
    # Every metal's gas references are one calculation, copied: the H2O.out and
    # H2.out under each gas_run directory are md5-identical files (measured
    # live below over the whole METALS dict, so it extends automatically).
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
    print(f"\nGAS-REFERENCE DISCLOSURE: the {len(METALS)} metals' H2O/H2 reference outputs "
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
        # The caveats above are explicitly time-live ("Live status at
        # scoring time"), and repair arrays can land between two runs of
        # this script. An artifact that says "live" without saying WHEN
        # cannot be compared against its own successor.
        import subprocess
        def _git(*a):
            try:
                return subprocess.run(("git",) + a, cwd=ROOT,
                                      capture_output=True, text=True,
                                      timeout=30).stdout.strip() or None
            except Exception:
                return None
        result["provenance"] = dict(
            scored_at_utc=datetime.datetime.now(
                datetime.timezone.utc).replace(microsecond=0).isoformat(),
            commit=_git("rev-parse", "HEAD"),
            branch=_git("rev-parse", "--abbrev-ref", "HEAD"),
            dirty=bool(_git("status", "--porcelain")),
            scorer="src/dft/a0main_readout.py",
            note="caveats.coverage_shortfall and the A7.2/A7.3 status "
                 "fields are live at this timestamp; a later run with "
                 "more landed repairs can legitimately differ")
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w") as fh:
            json.dump(result, fh, indent=2, default=str)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
