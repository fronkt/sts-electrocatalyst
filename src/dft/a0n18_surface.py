#!/usr/bin/env python
"""A11.R9 - the n = 18 statement as seven separate n = 18 tests across the common U grid.

Registered in docs/43 **A11.R9** (2026-09-03) at commit **01a76df**, which carried no
script and no result.

WHY THIS EXISTS.  The entrant asked for the n = 18 test.  A11.R8's R8-P2 already carries
an n = 18 number and may NOT be used as one -- its own registration forecloses promotion,
because nine of its eighteen pairs were seen before it was written.  So this does not
promote it.  It rebuilds the n = 18 statement out of material that is mostly UNSEEN:

  * SEEN      -- the n = 18 correlation at u000 (A11.R7 post-hoc rho -0.3808; A11.R8
                 nspin=2 rho -0.3148).
  * NOT SEEN  -- the n = 18 correlation at u150, u300, u450, u600, u750, u900.

Post-hoc at one rung, out-of-sample at six.  That asymmetry is the evidential content and
it was written down before these numbers existed.

WHAT IS REFUSED.  The 7 x 18 = 126 pairs are NEVER pooled.  Pooling is pseudo-replication:
the response span_U(dG_i) is one number per (metal, step), so it would be repeated seven
times against seven correlated predictors and the p would fall for an arithmetic reason.
Seven separate tests are reported; one pooled n = 126 test is not computed.

ANTI-SELECTION.  All seven rungs are reported, always, as a distribution.  No rung may be
quoted alone.  Multiplicity is printed with the result.

BINDING.  CONFIRMATORY-INELIGIBLE.  Scores nothing; cannot move A7.2 or A7.3.

Usage:  python src/dft/a0n18_surface.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_R7_PATH = os.path.join(ROOT, "src", "dft", "a0lowdin_valence.py")
_spec = importlib.util.spec_from_file_location("a0lowdin_valence", _R7_PATH)
R7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R7)
Fatal = R7.Fatal

METALS = ("Cr", "Mn", "Fe", "Ti", "Ru", "Ir")
STEP_STATES = ("s0_OH", "s0_O", "s0_OOH")
POSTHOC_RUNG = "u000"          # the one rung whose value was already known
ALPHA = 0.05


def common_grid(pm):
    """Registered rule: every U token banked for ALL SIX metals, and no other."""
    sets = []
    for M in METALS:
        per_state = {}
        for key in pm[M]["dq_d"]:
            state, u = key.split("|")
            if state in STEP_STATES:
                per_state.setdefault(state, set()).add(u)
        # a rung counts for this metal only if ALL THREE step states are banked at it
        if len(per_state) != len(STEP_STATES):
            sets.append(set())
            continue
        sets.append(set.intersection(*per_state.values()))
    grid = set.intersection(*sets)
    return sorted(grid)


def steps_at(pm, M, u):
    """A11.R7's CHE step increments, unchanged."""
    d = pm[M]["dq_d"]
    need = ["%s|%s" % (s, u) for s in STEP_STATES]
    for k in need:
        if k not in d:
            return None
    oh = d["%s|%s" % ("s0_OH", u)]
    o = d["%s|%s" % ("s0_O", u)]
    ooh = d["%s|%s" % ("s0_OOH", u)]
    return {1: oh, 2: o - oh, 3: ooh - o}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="a0n18_surface.py")
    ap.add_argument("--json", default=os.path.join(ROOT, "docs", "figs",
                                                   "a0n18_surface.json"))
    ap.add_argument("--md", default=os.path.join(
        ROOT, "docs", "research", "2026-09-03-a11r9-n18-surface.md"))
    ap.add_argument("--r7-json", default=os.path.join(ROOT, "docs", "figs",
                                                      "a0lowdin_valence.json"))
    args = ap.parse_args(argv)

    r7 = json.load(open(args.r7_json, encoding="utf-8"))
    pm = r7["per_metal"]

    grid = common_grid(pm)
    if len(grid) < 2:
        raise Fatal("common grid has %d rungs; need at least 2" % len(grid))

    rungs = []
    for u in grid:
        xs, ys, pairs = [], [], []
        for M in METALS:
            st = steps_at(pm, M, u)
            if st is None:
                raise Fatal("%s missing a step state at %s -- %s is not a common rung"
                            % (M, u, u))
            for i in (1, 2, 3):
                span = pm[M].get("span_dG%d" % i)
                if span is None:
                    raise Fatal("%s has no span_dG%d" % (M, i))
                xs.append(abs(st[i]))
                ys.append(float(span))
                pairs.append({"metal": M, "step": i, "abs_dq_step": abs(st[i]),
                              "span_dG_eV": float(span)})
        if len(xs) != 18:
            raise Fatal("rung %s gave n=%d, expected 18" % (u, len(xs)))
        rho, p, method = R7.perm_p(xs, ys)
        rungs.append({"u": u, "n": 18, "rho": rho, "p_nominal": p, "method": method,
                      "seen_before": (u == POSTHOC_RUNG), "pairs": pairs})

    rhos = [r["rho"] for r in rungs]
    oos = [r for r in rungs if not r["seen_before"]]
    oos_rhos = [r["rho"] for r in oos]

    def med(v):
        s = sorted(v)
        n = len(s)
        return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])

    n_sig = sum(1 for r in rungs if r["p_nominal"] < ALPHA)
    signs = {"negative": sum(1 for r in rhos if r < 0),
             "positive": sum(1 for r in rhos if r > 0),
             "zero": sum(1 for r in rhos if r == 0)}
    sign_holds = signs["negative"] == len(rhos) or signs["positive"] == len(rhos)

    out = {
        "artifact": "a11_r9 -- the n=18 robustness surface across the common U grid",
        "registered": "docs/43 A11.R9, commit 01a76df (no script, no result in it)",
        "binding": ("CONFIRMATORY-INELIGIBLE. Scores nothing; cites as no registered test; "
                    "cannot move A7.2 or A7.3. A7.2 stays CONFIRMED 5 of 6; A7.3 stays NOT "
                    "MET at 3 of 6 at denominator 6."),
        "zero_su": True,
        "grid": {
            "rungs": grid, "n_rungs": len(grid),
            "rule": ("every U token banked for ALL SIX metals and no other; rungs present "
                     "for one metal only (Mn u390, Fe u530, Ir u591, Ru u673) and Cr's "
                     "finer ladder are excluded because a rung missing a metal is not an "
                     "n=18 test"),
            "posthoc_rung": POSTHOC_RUNG,
            "out_of_sample_rungs": [r["u"] for r in oos],
        },
        "pooling_refused": ("the 7 x 18 = 126 pairs are NEVER pooled: span_U is one number "
                            "per (metal, step), so pooling repeats the response seven times "
                            "against seven correlated predictors and the p falls for an "
                            "arithmetic reason. No pooled n=126 statistic is computed here."),
        "rungs": rungs,
        "distribution": {
            "rho_min": min(rhos), "rho_median": med(rhos), "rho_max": max(rhos),
            "signs": signs, "sign_holds_across_grid": sign_holds,
            "n_rungs_nominal_p_below_0.05": n_sig,
            "out_of_sample_only": {
                "n_rungs": len(oos), "rho_min": min(oos_rhos),
                "rho_median": med(oos_rhos), "rho_max": max(oos_rhos),
                "n_nominal_p_below_0.05": sum(1 for r in oos if r["p_nominal"] < ALPHA),
            },
        },
        "multiplicity": (
            "%d tests at alpha=%.2f give a %.0f%% chance of at least one nominal hit under "
            "the null IF they were independent. They are not: the predictor varies smoothly "
            "in U, so that figure is an UPPER BOUND and the effective number of tests is "
            "smaller than %d."
            % (len(rungs), ALPHA, 100 * (1 - (1 - ALPHA) ** len(rungs)), len(rungs))),
        "p_is_nominal": ("the three steps of one metal share that metal's slab reference and "
                         "are not independent; every p here is NOMINAL, carried from A11.R7 "
                         "unchanged"),
        "seen_before_context": {
            "u000_a11r7_posthoc": {"rho": -0.3808, "p": 0.1209,
                                   "note": "all-six post-hoc figure, already reported"},
            "u000_a11r8_nspin2": {"rho": -0.3148, "p_nominal": 0.2046,
                                  "note": "R8-P2, REPORTED NEVER SCORED, not promoted here"},
        },
        "registered_reading": (
            "A sign that FLIPS across the grid would mean the u000 result carries no "
            "information about U-robustness and the report must say so. A sign that HOLDS at "
            "every rung with comparable magnitude is consistent with A11.R7 and adds nothing "
            "to it -- the tracker still fails to explain the A7.3 split, at every U. NEITHER "
            "outcome can rescue the valence explanation: R7-P3 and R8-P1 are separation "
            "tests, this is a correlation surface, and a correlation among 18 heterogeneous "
            "(metal, step) pairs is not a mechanism."),
    }

    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    _write_md(args.md, out)

    print("A11.R9 -- %d rungs, n=18 each (NEVER pooled)" % len(rungs))
    for r in rungs:
        print("  %-5s rho = %+.4f  p_nominal = %.4f  %s"
              % (r["u"], r["rho"], r["p_nominal"],
                 "[SEEN BEFORE -- post-hoc]" if r["seen_before"] else "out-of-sample"))
    d = out["distribution"]
    print("  sign holds across grid: %s   rungs with nominal p<0.05: %d of %d"
          % (d["sign_holds_across_grid"], d["n_rungs_nominal_p_below_0.05"], len(rungs)))
    print("wrote %s" % args.json)
    print("wrote %s" % args.md)
    return 0


def _write_md(path, out):
    L = []
    A = L.append
    d = out["distribution"]
    A("# A11.R9 - the n = 18 surface across the common U grid")
    A("")
    A("*Generated by `src/dft/a0n18_surface.py`. Registered in docs/43 **A11.R9** "
      "(2026-09-03) at commit **01a76df**, which carried no script and no result. "
      "Zero new DFT; zero SU.*")
    A("")
    A("> **%s**" % out["binding"])
    A("")
    A("## The seven tests")
    A("")
    A("Each row is its own n = 18 test. **They are never pooled** - %s"
      % out["pooling_refused"])
    A("")
    A("| U rung | n | rho | nominal p | status |")
    A("|---|---|---|---|---|")
    for r in out["rungs"]:
        A("| %s | 18 | %+.4f | %.4f | %s |"
          % (r["u"], r["rho"], r["p_nominal"],
             "**SEEN BEFORE - post-hoc**" if r["seen_before"] else "out-of-sample"))
    A("")
    A("## The distribution, which is the only thing that may be quoted")
    A("")
    A("- rho across all seven rungs: **min %+.4f, median %+.4f, max %+.4f**"
      % (d["rho_min"], d["rho_median"], d["rho_max"]))
    A("- sign: %d negative, %d positive, %d zero - **sign holds across the grid: %s**"
      % (d["signs"]["negative"], d["signs"]["positive"], d["signs"]["zero"],
         d["sign_holds_across_grid"]))
    A("- rungs reaching nominal p < 0.05: **%d of %d**"
      % (d["n_rungs_nominal_p_below_0.05"], len(out["rungs"])))
    o = d["out_of_sample_only"]
    A("- **out-of-sample rungs only** (the six never computed before): n = %d, rho min "
      "%+.4f, median %+.4f, max %+.4f; %d reach nominal p < 0.05"
      % (o["n_rungs"], o["rho_min"], o["rho_median"], o["rho_max"],
         o["n_nominal_p_below_0.05"]))
    A("")
    A("**Multiplicity.** %s" % out["multiplicity"])
    A("")
    A("**Every p is nominal.** %s" % out["p_is_nominal"])
    A("")
    A("## What was already known, and is not re-presented as new")
    A("")
    A("| source | rung | rho | p |")
    A("|---|---|---|---|")
    s = out["seen_before_context"]
    A("| A11.R7 post-hoc all-six | u000 | %+.4f | %.4f |"
      % (s["u000_a11r7_posthoc"]["rho"], s["u000_a11r7_posthoc"]["p"]))
    A("| A11.R8 R8-P2 (nspin=2) | u000 | %+.4f | %.4f |"
      % (s["u000_a11r8_nspin2"]["rho"], s["u000_a11r8_nspin2"]["p_nominal"]))
    A("")
    A("R8-P2 is **REPORTED, NEVER SCORED** by its own registration and **is not promoted "
      "here**. It appears above only so the reader can see what was known before this ran.")
    A("")
    A("## Registered reading, written before the numbers existed")
    A("")
    A(out["registered_reading"])
    A("")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
