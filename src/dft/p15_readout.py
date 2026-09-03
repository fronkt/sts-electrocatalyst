#!/usr/bin/env python3
"""P15 readout: the block-1B hp.x *U*-gate verdict (docs/43 §4, as amended by §4-A).

WHY THIS SCRIPT EXISTS. Every scored family in this repo has a readout that emits
its verdict -- a0main_, a0cell_, lit2_, pproj_, s3_. Block 1B had a *builder*
(`build_hp_validation.py`, whose own header says "This file registers nothing")
and no readout, so nothing ever wrote P15's line and the gate sat undecided on
data that has been complete since 2026-08-10 (commit dc38c23). That absence, not
the physics, is why P15 was the last free row in the ledger (docs/73 §3).

THE THRESHOLDS ARE NOT WRITTEN DOWN HERE, ON PURPOSE. They are parsed out of
docs/43 at runtime and the script refuses to score if it cannot find them.

    Three builders wrote a contradicting copy of a registered rule into a source
    file on 2026-08-09 (docs/43 :1840's amendment rule; the same failure is
    recorded at runs/hp_costmodel/cost_model.json:6, which declines to copy this
    very window because "a widened acceptance window sitting in a build artifact
    is the single most damaging thing an STS judge could find").

A hardcoded window here would be that defect a fourth time. Parsing it means the
gate this script applies IS the registered gate, checkably, and a drift between
them is a crash rather than a silent mis-score.

WHAT IS GATED, AND WHAT IS NOT (docs/43 §4 and §4-A):

  external   U(Ti-3d, rutile TiO2, atomic projectors) in the registered window.
             Deliberately wide: it asks "does hp.x produce a physically sane
             number on a closed-shell system we understand," not "does it
             reproduce a literature value."
  internal 1 q-mesh convergence, dU vs the NEXT FINER mesh.
  internal 2 response-matrix symmetry -- DEMOTED by §4-A.4 to a reported
             diagnostic, "reported, not gated ... whichever way the pending
             measurement resolves". Never gates here. Reported.
  internal 3 perturbation-amplitude independence -- WITHDRAWN by §4-A.2 as
             UNPERFORMABLE (hp.x is DFPT; the binary has no amplitude keyword).
             Not a failure and not a pass: it cannot be evaluated at all.
  internal 4 symmetry-equivalent perturbed atoms agree within the registered
             tolerance. §4-A.4 makes this "now load-bearing" in place of 3.
  check 4'   §4-A.3, the magnetic/metallic arm: one bulk rutile CrO2 run must
             print a finite U with ZERO "Convergence has not been reached".
             This is the registered ESCAPE from §4-A.3's scope sentence -- "A GO
             on TiO2 alone licenses only the sentence 'hp.x validates on a
             closed-shell bulk insulator', which is not what the campaign needs."
             Pass it and the GO is a BULK GO; fail it and the GO is scoped.

THE SLAB IS A SEPARATE GATE, ALWAYS. docs/43 §4 "A separate gate for the slab":
"A successful bulk validation does not license a slab U." It is scored here as
its own line and is never folded into the bulk verdict.

LITERATURE SIDE-CHECK, REPORTED NEVER GATED. §4 is explicit that the unverified
~4.9 eV draft criterion is not the gate: "If the literature value is later
verified, the narrower comparison is reported as an additional check, not as the
gate." The Xu value is passed in with --xu-u and reported as an offset.

Usage:
  python src/dft/p15_readout.py [--json docs/figs/p15_readout.json]
                                [--md docs/research/<date>-p15-u-gate.md]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREREG = os.path.join(ROOT, "docs", "43-prereg-week1-factorial.md")

# The q-mesh ladder, coarse -> fine. "vs the next finer mesh" is a comparison
# between ADJACENT rungs, so the order here is part of the criterion.
Q_LADDER = ("q222", "q333", "q444")


class Fatal(RuntimeError):
    """Refuse to score rather than score on an assumption."""


# --------------------------------------------------------------------------
# the registered thresholds, read from the pre-registration
# --------------------------------------------------------------------------

def registered_thresholds(path: str = PREREG) -> dict:
    """Parse the gate out of docs/43. Raise rather than guess."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    out: dict = {}

    # §4-A.1 is the operative window ("The external window stays [3.0, 7.0] eV"),
    # and §4 states the same pair. Require BOTH and require them to agree -- if an
    # amendment ever moves one, this crashes instead of scoring the stale one.
    base = re.search(r"GO requires U\(Ti-3d.{0,60}?\)\s*∈\s*\*\*\[([\d.]+),\s*([\d.]+)\]\s*eV\*\*",
                     text, re.S)
    amended = re.search(r"The external window stays \[([\d.]+),\s*([\d.]+)\]\s*eV", text)
    if not base or not amended:
        raise Fatal("could not parse the external window from %s (base=%s amended=%s)"
                    % (path, bool(base), bool(amended)))
    lo_b, hi_b = float(base.group(1)), float(base.group(2))
    lo_a, hi_a = float(amended.group(1)), float(amended.group(2))
    if (lo_b, hi_b) != (lo_a, hi_a):
        raise Fatal("docs/43 §4 window [%s, %s] disagrees with §4-A.1 [%s, %s]; "
                    "an amendment moved one and this script will not choose"
                    % (lo_b, hi_b, lo_a, hi_a))
    out["window_eV"] = [lo_a, hi_a]

    m = re.search(r"q-mesh convergence \| ΔU < ([\d.]+) eV vs the next finer mesh", text)
    if not m:
        raise Fatal("could not parse the q-mesh threshold from %s" % path)
    out["q_mesh_dU_max_eV"] = float(m.group(1))

    m = re.search(r"symmetry-equivalent perturbed atoms \| agree within ([\d.]+) eV", text)
    if not m:
        raise Fatal("could not parse the perturbed-atom tolerance from %s" % path)
    out["perturbed_atom_tol_eV"] = float(m.group(1))

    # §4-A.4 restates the same tolerance on the now-load-bearing find_atpert = 4
    # test. If the two ever diverge, refuse.
    m2 = re.search(r"two independently perturbed Ti agreeing within ([\d.]+) eV", text)
    if not m2:
        raise Fatal("could not parse §4-A.4's restatement of the perturbed-atom tolerance")
    if float(m2.group(1)) != out["perturbed_atom_tol_eV"]:
        raise Fatal("§4's %.3f eV and §4-A.4's %.3f eV disagree"
                    % (out["perturbed_atom_tol_eV"], float(m2.group(1))))
    return out


# --------------------------------------------------------------------------
# readers
# --------------------------------------------------------------------------

def read_u(dat: str) -> list[dict]:
    """Every Hubbard U row of a .Hubbard_parameters.dat, in file order."""
    if not os.path.exists(dat):
        raise Fatal("missing %s" % dat)
    rows = []
    with open(dat, encoding="utf-8", errors="replace") as fh:
        started = False
        for line in fh:
            if "Hubbard U parameters" in line:
                started = True
                continue
            if not started:
                continue
            tok = line.split()
            # site n. | type | label | spin | new_type | new_label | manifold | U
            if len(tok) == 8 and tok[0].isdigit():
                try:
                    rows.append({"site": int(tok[0]), "label": tok[2],
                                 "manifold": tok[6], "U_eV": float(tok[7])})
                except ValueError:
                    continue
            elif rows and line.strip().startswith("="):
                break
    if not rows:
        raise Fatal("no Hubbard U rows parsed from %s" % dat)
    return rows


def hp_qc(out: str) -> dict:
    """Convergence hygiene for one hp.x run. Bytes, not grep: one file in this
    corpus carries a NUL and any text-mode line reader can drop content."""
    if not os.path.exists(out):
        return {"exists": False, "job_done": 0, "not_converged": 0, "clean": False}
    with open(out, "rb") as fh:
        blob = fh.read()
    jd = blob.count(b"JOB DONE")
    nc = blob.count(b"Convergence has not been reached")
    return {"exists": True, "job_done": jd, "not_converged": nc,
            "clean": jd >= 1 and nc == 0}


def scf_magnetisation(out: str):
    """Last total/absolute magnetisation printed by a pw.x SCF, or None."""
    if not os.path.exists(out):
        return None
    with open(out, "rb") as fh:
        blob = fh.read().decode("utf-8", "replace")
    tot = re.findall(r"total magnetization\s*=\s*([-\d.]+)", blob)
    ab = re.findall(r"absolute magnetization\s*=\s*([-\d.]+)", blob)
    if not tot:
        return None
    return {"total_muB": float(tot[-1]),
            "absolute_muB": float(ab[-1]) if ab else None}


def one_u(rows: list[dict], label: str, dat: str) -> float:
    """The single U for `label`, refusing if the symmetry-equivalent sites disagree
    beyond printing precision -- that would be a different defect than the gate."""
    vals = [r["U_eV"] for r in rows if r["label"] == label]
    if not vals:
        raise Fatal("no %s rows in %s" % (label, dat))
    if max(vals) - min(vals) > 1e-6:
        raise Fatal("%s sites disagree in %s: %s" % (label, dat, vals))
    return vals[0]


# --------------------------------------------------------------------------
# the gate
# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(prog="p15_readout.py")
    ap.add_argument("--runs", default=os.path.join(ROOT, "runs"))
    ap.add_argument("--json", default=os.path.join(ROOT, "docs", "figs", "p15_readout.json"))
    ap.add_argument("--md", default=None)
    ap.add_argument("--xu-u", type=float, default=None,
                    help="Xu Table 1 U(Ti) in eV, for the REPORTED literature "
                         "side-check. Never gates (docs/43 §4).")
    args = ap.parse_args(argv)

    T = registered_thresholds()
    tio2 = os.path.join(args.runs, "hp_tio2")
    cost = os.path.join(args.runs, "hp_costmodel")
    lo, hi = T["window_eV"]

    print("P15 -- block 1B hp.x U gate")
    print("thresholds parsed from docs/43 (never hardcoded here):")
    print("  external window        [%.1f, %.1f] eV" % (lo, hi))
    print("  q-mesh dU              < %.2f eV vs the next finer mesh" % T["q_mesh_dU_max_eV"])
    print("  perturbed-atom agree   <= %.2f eV" % T["perturbed_atom_tol_eV"])

    checks: dict = {}

    # ---- external + internal 1: the q ladder -------------------------------
    ladder = {}
    for q in Q_LADDER:
        dat = os.path.join(tio2, "hp__atomic_%s.Hubbard_parameters.dat" % q)
        qc = hp_qc(os.path.join(tio2, "hp__atomic_%s.out" % q))
        u = one_u(read_u(dat), "Ti", dat)
        ladder[q] = {"U_eV": u, "qc": qc}
        print("\n  %-6s U(Ti,3d) = %.4f eV   JOB DONE=%d  NOTCONV=%d"
              % (q, u, qc["job_done"], qc["not_converged"]))
        if not qc["clean"]:
            raise Fatal("%s is not clean; refusing to score a gate on it" % q)

    us = [ladder[q]["U_eV"] for q in Q_LADDER]
    in_window = [lo <= u <= hi for u in us]
    checks["external"] = {
        "U_eV": {q: ladder[q]["U_eV"] for q in Q_LADDER},
        "window_eV": [lo, hi],
        "all_in_window": all(in_window),
        "verdict": "MET" if all(in_window) else "NOT MET",
    }

    steps = []
    for a, b in zip(Q_LADDER, Q_LADDER[1:]):
        d = abs(ladder[b]["U_eV"] - ladder[a]["U_eV"])
        steps.append({"from": a, "to": b, "dU_eV": d,
                      "passes": d < T["q_mesh_dU_max_eV"]})
        print("  q-mesh %s -> %s  |dU| = %.4f eV  (< %.2f)  %s"
              % (a, b, d, T["q_mesh_dU_max_eV"], "PASS" if d < T["q_mesh_dU_max_eV"] else "FAIL"))
    worst = max(s["dU_eV"] for s in steps)
    checks["q_mesh"] = {
        "steps": steps, "max_dU_eV": worst,
        "threshold_eV": T["q_mesh_dU_max_eV"],
        "margin_x": (T["q_mesh_dU_max_eV"] / worst) if worst > 0 else None,
        "verdict": "PASS" if all(s["passes"] for s in steps) else "FAIL",
    }

    # ---- internal 4: symmetry-equivalent perturbed atoms -------------------
    dat = os.path.join(tio2, "hp__atomic_q333_allatoms.Hubbard_parameters.dat")
    qc = hp_qc(os.path.join(tio2, "hp__atomic_q333_allatoms.out"))
    rows = [r for r in read_u(dat) if r["label"] == "Ti"]
    spread = max(r["U_eV"] for r in rows) - min(r["U_eV"] for r in rows)
    checks["perturbed_atoms"] = {
        "deck": "hp__atomic_q333_allatoms (find_atpert = 4)",
        "U_eV": [r["U_eV"] for r in rows], "spread_eV": spread,
        "tolerance_eV": T["perturbed_atom_tol_eV"], "qc": qc,
        "verdict": "PASS" if (qc["clean"] and spread <= T["perturbed_atom_tol_eV"]) else "FAIL",
    }
    print("\n  find_atpert=4  U = %s  spread = %.4f eV (<= %.2f)  %s"
          % ([("%.4f" % r["U_eV"]) for r in rows], spread,
             T["perturbed_atom_tol_eV"], checks["perturbed_atoms"]["verdict"]))

    # ---- internal 2 and 3: demoted and withdrawn --------------------------
    checks["chi_symmetry"] = {
        "status": "DEMOTED to a reported diagnostic by docs/43 §4-A.4",
        "gated": False, "measurement": "PENDING",
        "note": ("reported, not gated, 'whichever way the pending measurement "
                 "resolves'. Settleable at 0 SU: every deck ran iverbosity = 2 and "
                 "the raw per-rung .chi*.dat are preserved, so the raw chi can be "
                 "compared against the symmetrised matrix in .Hubbard_parameters.dat. "
                 "A hard gate that cannot fail is not a gate."),
    }
    checks["amplitude_independence"] = {
        "status": "WITHDRAWN by docs/43 §4-A.2 as UNPERFORMABLE",
        "gated": False,
        "note": ("hp.x is DFPT and the binary has no perturbation-amplitude "
                 "keyword, so the check was not merely unmet but impossible. It is "
                 "neither a pass nor a failure and must not be counted as either."),
    }

    # ---- check 4': the magnetic/metallic arm ------------------------------
    dat = os.path.join(tio2, "hp__cro2_q222.Hubbard_parameters.dat")
    qc = hp_qc(os.path.join(tio2, "hp__cro2_q222.out"))
    u_cr = one_u(read_u(dat), "Cr", dat)
    mag = scf_magnetisation(os.path.join(tio2, "scf__cro2.out"))
    finite = u_cr == u_cr and abs(u_cr) != float("inf")
    checks["check_4prime"] = {
        "U_Cr_3d_eV": u_cr, "qc": qc, "scf_magnetisation": mag,
        "registered": ("one bulk rutile CrO2 arm must print a finite U with ZERO "
                       "'Convergence has not been reached' lines (docs/43 §4-A.3)"),
        "verdict": "PASS" if (finite and qc["clean"]) else "FAIL",
    }
    print("\n  check 4' CrO2  U(Cr,3d) = %.4f eV  JOB DONE=%d  NOTCONV=%d  mag=%s  %s"
          % (u_cr, qc["job_done"], qc["not_converged"],
             (mag or {}).get("total_muB"), checks["check_4prime"]["verdict"]))

    # ---- the slab: its own gate, never folded in --------------------------
    # SCOPE, and it matters. Only the `hp_1atomq_*` decks are U attempts -- they
    # are the four named in runs/hp_costmodel/cost_model.json. The `hp_qmesh_*`
    # and `hp_npert` runs are the per-(atom, q) COST MODEL and the NSCF k-count
    # probes of docs/43 §4-A.5; they never attempt a U, so counting them as gate
    # rows would report six timing probes as clean slab validations.
    slab, probes = {}, {}
    if os.path.isdir(cost):
        for fn in sorted(os.listdir(cost)):
            if not (fn.startswith("crslab_sym__hp") and fn.endswith(".out")):
                continue
            q = hp_qc(os.path.join(cost, fn))
            q["produced_U"] = os.path.exists(
                os.path.join(cost, fn[:-4] + ".Hubbard_parameters.dat"))
            (slab if "_1atomq_" in fn else probes)[fn] = q
    if not slab:
        raise Fatal("no crslab_sym__hp_1atomq_* deck found under %s; the slab gate "
                    "arm cannot be located and will not be inferred" % cost)
    n_slab = len(slab)
    n_clean = sum(1 for v in slab.values() if v["clean"])
    n_u = sum(1 for v in slab.values() if v["produced_U"])
    checks["slab"] = {
        "runs": slab, "n": n_slab, "n_clean": n_clean, "n_produced_U": n_u,
        "scope": ("U-attempt decks only (crslab_sym__hp_1atomq_*), the four named "
                  "in cost_model.json. The %d crslab_sym__hp_{qmesh,npert}_* runs "
                  "are the docs/43 §4-A.5 cost model and k-count probes, reported "
                  "separately and NOT gate rows." % len(probes)),
        "cost_model_probes": probes,
        "registered": ("docs/43 §4 'A separate gate for the slab': a successful "
                       "bulk validation does not license a slab U"),
        "verdict": "GO" if (n_clean == n_slab and n_u == n_slab) else "NO-GO",
    }
    print("\n  slab GATE arm (hp_1atomq_*): %d runs, %d clean, %d produced a U  ->  %s"
          % (n_slab, n_clean, n_u, checks["slab"]["verdict"]))
    print("  cost-model probes (not gate rows): %d runs, %d clean, %d produced a U"
          % (len(probes), sum(1 for v in probes.values() if v["clean"]),
             sum(1 for v in probes.values() if v["produced_U"])))

    # ---- literature side-check: reported, never gated ---------------------
    if args.xu_u is not None:
        off = ladder["q222"]["U_eV"] - args.xu_u
        checks["literature_side_check"] = {
            "xu_U_eV": args.xu_u, "ours_q222_eV": ladder["q222"]["U_eV"],
            "offset_eV": off, "gated": False,
            "note": ("docs/43 §4: reported as an additional check, NOT as the gate. "
                     "The ~4.9 eV draft criterion was withdrawn as unverifiable."),
        }
        print("\n  literature side-check (NOT a gate): ours - Xu = %+.4f eV" % off)

    # ---- the bulk verdict --------------------------------------------------
    gated = [checks["external"]["verdict"] == "MET",
             checks["q_mesh"]["verdict"] == "PASS",
             checks["perturbed_atoms"]["verdict"] == "PASS"]
    scoped = checks["check_4prime"]["verdict"] != "PASS"
    if all(gated):
        bulk = "GO"
        scope = ("SCOPED -- licenses only 'hp.x validates on a closed-shell bulk "
                 "insulator' (docs/43 §4-A.3), and the slab U is not attempted"
                 ) if scoped else (
                 "BULK -- check 4' passed, so the GO is NOT confined to the "
                 "closed-shell statement")
    else:
        bulk = "NO-GO"
        scope = ("docs/43 §4's declared consequence applies: A0 ships regardless; "
                 "S2 downgrades to the three-determination bracket and the report "
                 "states hp.x was attempted and did not validate, with the failing "
                 "check named")

    print("\n" + "=" * 68)
    print("P15 BULK VERDICT: %s   (%s)" % (bulk, scope.split(" -- ")[0]))
    print("P15 SLAB VERDICT: %s" % checks["slab"]["verdict"])
    print("=" * 68)
    print("\nThis readout computes the gate. The registered scoring act is the")
    print("entrant's dated line; nothing here is countersigned.")

    payload = {
        "artifact": "p15 -- block 1B hp.x U gate",
        "registered": "docs/43 §4 as amended by §4-A (AMENDMENT 1)",
        "thresholds_parsed_from": os.path.relpath(PREREG, ROOT).replace("\\", "/"),
        "thresholds": T,
        "zero_su": True,
        "checks": checks,
        "bulk_verdict": bulk,
        "bulk_scope": scope,
        "slab_verdict": checks["slab"]["verdict"],
        "binding": ("The bulk and slab gates are separate and are never combined "
                    "(docs/43 §4). The chi-symmetry diagnostic and the literature "
                    "side-check are REPORTED and never gate. Amplitude "
                    "independence is WITHDRAWN as unperformable and is neither a "
                    "pass nor a failure. This readout applies no countersignature: "
                    "the registered scoring act is the entrant's dated line."),
    }
    if args.json:
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print("\nwrote %s" % args.json)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fatal as exc:
        print("REFUSING TO SCORE: %s" % exc, file=sys.stderr)
        sys.exit(2)
