#!/usr/bin/env python
"""A11.R8 - the A11.R7 valence tracker re-read so every metal's predictor is
spin-polarised.

Registered in docs/43 **A11.R8** (2026-09-03) at commit **07cfc4f**, which carried
no script and no result.  Nothing here was chosen after seeing a value of the
predictor it computes.

The question, in one line: A7.3's 3-over/3-under split is perfectly confounded with
nspin=2 (Cr, Mn, Fe) / nspin=1 (Ti, Ru, Ir), and A11.R7's R7-P3 fired -- |dq_c|
interleaved the two groups.  Exactly one rescue survives that result: that R7-P3
failed only because Ti/Ru/Ir's valence was read from calculations never allowed to
polarise.  This script tests that rescue and nothing else, by re-reading the SAME
tracker for those three from the A0-SPIN arm, where the decks are nspin=2.

Single-variable by construction:
  * Cr, Mn, Fe    -- unchanged, from runs/a0/main (already nspin=2, 76/76, 32/32,
                     32/32 on the scoped decks); self-check 4 asserts their |dq_c|
                     reproduces A11.R7 EXACTLY, since they are the same files.
  * Ti, Ru, Ir    -- from runs/a0/spin/<M>/<state>__u000__sp2m<seed>, the new material.
  * response      -- span_U(c_M)/2 as banked in the A0 MAIN readout, identical to
                     A11.R7.  The equalised span is deliberately NOT used: the same
                     day's [D2 GUARD-3 ADJUDICATED 2026-09-03] makes Ru's and Ir's
                     equalised spans BRANCH-CONDITIONAL and not scoreable.

Registered predictions:
  R8-P1  primary, n=6.  SEPARATES iff max|dq_c| over {Ti,Ru,Ir} < min|dq_c| over
         {Cr,Mn,Fe}.  A separation proves nothing (3-vs-3 along a line still aligned
         with 3d/4d/5d identity); a FAILURE to separate falsifies the rescue.  The
         falsification is the deliverable.
  R8-P2  n=18, REPORTED NEVER SCORED -- 9 of 18 pairs are carried over from A11.R7,
         whose post-hoc value is already known, so no threshold on it would be honest.
  R8-P3  n=3, REPORTED NEVER SCORED -- the shift |dq_c|(nspin=2) - |dq_c|(nspin=1)
         for Ti/Ru/Ir, the direct measurement of how far spin convention moves the
         tracker.

Seed rule, fixed before any energy or population was read: per (metal, state) at u000
take the LOWEST-TOTAL-ENERGY CONVERGED nspin=2 seed; ties below 1e-6 Ry break to the
lowest seed label.  Deliberately not the census winner, whose pool includes the
nspin=1 row.

Witness, in its corrected like-for-like form: the spread of dq_c ACROSS SEEDS at the
same U.  A11.R7's witness compared a swing across U against a fixed-U state
difference and is disclosed as malformed in docs/45.  Cr/Mn/Fe are single-row and are
WITNESS-UNAVAILABLE, which is not a flag and does not exclude them.

Usage:  python src/dft/a0spin_valence.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- import A11.R7's module so the parser is IDENTICAL (self-check 1) -----------
_R7_PATH = os.path.join(ROOT, "src", "dft", "a0lowdin_valence.py")
_spec = importlib.util.spec_from_file_location("a0lowdin_valence", _R7_PATH)
R7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R7)

Fatal = R7.Fatal

OVER = ("Cr", "Mn", "Fe")      # the A7.3 over-floor set, and the nspin=2 main decks
UNDER = ("Ti", "Ru", "Ir")     # the under-floor set, and the no-nspin-card main decks
METALS = OVER + UNDER
STATES = ("slab", "s0_O", "s0_OH", "s0_OOH")
BASE_UTOK = "u000"
SEED_RE = re.compile(r"^(?P<state>.+?)__u000__sp2(?P<seed>m\d+|null)$")
TIE_RY = 1.0e-6                # registered tie tolerance for seed selection
PERM_SEED = 20260903


# --------------------------------------------------------------- QE readers ---

def total_energy_ry(path):
    """Final '!' total energy in Ry, or None if the run printed none."""
    e = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("!") and "total energy" in line:
                for tok in line.split():
                    try:
                        e = float(tok)
                    except ValueError:
                        continue
    return e


def converged(path):
    """True iff the run reports SCF convergence and never reports failure."""
    ok = False
    with open(path, encoding="utf-8", errors="replace") as fh:
        txt = fh.read()
    if "convergence NOT achieved" in txt:
        return False
    if "convergence has been achieved" in txt:
        ok = True
    return ok


def deck_is_nspin2(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.split("!")[0]
            if "nspin" in s and "2" in s.split("=")[-1]:
                return True
    return False


# ------------------------------------------------------------ seed selection ---

def spin_candidates(metal):
    """{state: [(seed, stem)]} for every banked u000 nspin=2 artifact of `metal`."""
    mdir = os.path.join(ROOT, "runs", "a0", "spin", metal)
    out = {}
    if not os.path.isdir(mdir):
        return out
    for fn in sorted(os.listdir(mdir)):
        if not fn.endswith(".lowdin.txt"):
            continue
        stem = fn[: -len(".lowdin.txt")]
        m = SEED_RE.match(stem)
        if not m:
            continue
        out.setdefault(m.group("state"), []).append((m.group("seed"), stem))
    return out


def pick_seed(metal, state, cands, excluded):
    """Registered rule: lowest total energy among CONVERGED nspin=2 seeds."""
    mdir = os.path.join(ROOT, "runs", "a0", "spin", metal)
    scored = []
    for seed, stem in cands:
        din = os.path.join(mdir, stem + ".in")
        dout = os.path.join(mdir, stem + ".out")
        if not (os.path.exists(din) and os.path.exists(dout)):
            excluded.append({"metal": metal, "state": state, "seed": seed,
                             "reason": "missing .in or .out beside the .lowdin.txt"})
            continue
        if not deck_is_nspin2(din):
            excluded.append({"metal": metal, "state": state, "seed": seed,
                             "reason": "deck does not carry nspin = 2"})
            continue
        if not converged(dout):
            excluded.append({"metal": metal, "state": state, "seed": seed,
                             "reason": "SCF not converged"})
            continue
        e = total_energy_ry(dout)
        if e is None:
            excluded.append({"metal": metal, "state": state, "seed": seed,
                             "reason": "no '!' total energy printed"})
            continue
        scored.append((e, seed, stem))
    if not scored:
        return None
    scored.sort(key=lambda r: (r[0], r[1]))
    best_e, best_seed, best_stem = scored[0]
    tied = [s for (e, s, _st) in scored if abs(e - best_e) < TIE_RY]
    return {"seed": best_seed, "stem": best_stem, "energy_ry": best_e,
            "n_converged_seeds": len(scored),
            "tied_within_1e-6_Ry": sorted(tied),
            "all_seeds": [{"seed": s, "energy_ry": e} for (e, s, _st) in scored]}


# ---------------------------------------------------------------- q_d reader ---

def qd_from(path_lowdin, site_idx):
    atoms = R7.parse_lowdin(path_lowdin)
    R7.check_atoms(path_lowdin, atoms)          # self-checks 2 and 3, fatal
    return R7.d_charge(atoms, site_idx)


def active_site_spin(metal, seed_stems):
    """A(M) from the spin arm's own s0_OH deck, by the registered rule."""
    mdir = os.path.join(ROOT, "runs", "a0", "spin", metal)
    slab_stem = seed_stems.get("slab")
    oh_stem = seed_stems.get("s0_OH")
    if not (slab_stem and oh_stem):
        raise Fatal("%s: need both slab and s0_OH in the spin arm to fix A(M)" % metal)
    _, slab_pos = R7.read_deck(os.path.join(mdir, slab_stem + ".in"))
    cell, oh_pos = R7.read_deck(os.path.join(mdir, oh_stem + ".in"))
    n_slab = len(slab_pos)
    if len(oh_pos) != n_slab + 2:
        raise Fatal("%s: s0_OH has %d atoms, slab has %d -- expected slab + O + H"
                    % (metal, len(oh_pos), n_slab))
    ads = [(i, s, x, y, z) for i, (s, x, y, z) in enumerate(oh_pos, 1) if i > n_slab]
    ox = [a for a in ads if a[1] == "O"]
    if len(ox) != 1:
        raise Fatal("%s: expected exactly one adsorbate O, found %d" % (metal, len(ox)))
    ob = ox[0]
    cands = [(R7.min_image_dist(cell, (ob[2], ob[3], ob[4]), (x, y, z)), i)
             for i, (s, x, y, z) in enumerate(oh_pos, 1) if s == metal]
    if not cands:
        raise Fatal("%s: no metal atoms of species %s in the deck" % (metal, metal))
    dist, idx = min(cands)
    if oh_pos[idx - 1][0] != metal:
        raise Fatal("CHECK 4 FAILED %s: A(M)=%d is species %s" % (metal, idx,
                                                                  oh_pos[idx - 1][0]))
    return idx, dist, n_slab


# ------------------------------------------------------------------ the test ---

def separation(over_vals, under_vals):
    """R8-P1: SEPARATES iff max|dq_c| under-floor < min|dq_c| over-floor."""
    hi_of_under = max(under_vals)
    lo_of_over = min(over_vals)
    sep = hi_of_under < lo_of_over
    return {
        "verdict": "SEPARATES" if sep else "DOES NOT SEPARATE",
        "max_abs_dqc_under_floor": hi_of_under,
        "min_abs_dqc_over_floor": lo_of_over,
        "gap": lo_of_over - hi_of_under,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(prog="a0spin_valence.py")
    ap.add_argument("--json", default=os.path.join(ROOT, "docs", "figs",
                                                   "a0spin_valence.json"))
    ap.add_argument("--md", default=os.path.join(
        ROOT, "docs", "research", "2026-09-03-a11r8-spin-valence.md"))
    ap.add_argument("--r7-json", default=os.path.join(ROOT, "docs", "figs",
                                                      "a0lowdin_valence.json"),
                    help="A11.R7's readout; the carry-over identity (self-check 4) "
                         "is asserted against it")
    args = ap.parse_args(argv)

    r7 = json.load(open(args.r7_json, encoding="utf-8"))
    r7pm = r7["per_metal"]

    excluded = []
    per_metal = {}

    # ---- Cr, Mn, Fe: unchanged, from the MAIN arm (already nspin = 2) ----------
    for M in OVER:
        mdir = os.path.join(ROOT, "runs", "a0", "main", M)
        site, dist, n_slab = R7.active_site(M, mdir)
        q = {}
        for st in STATES:
            p = os.path.join(mdir, "%s__%s.lowdin.txt" % (st, BASE_UTOK))
            if not os.path.exists(p):
                excluded.append({"metal": M, "state": st, "seed": None,
                                 "reason": "no banked u000 artifact in the main arm"})
                continue
            q[st] = qd_from(p, site)
        if "s0_OOH" not in q or "s0_OH" not in q:
            raise Fatal("%s: missing s0_OOH or s0_OH in the main arm" % M)
        dqc = q["s0_OOH"] - q["s0_OH"]
        per_metal[M] = {
            "arm": "main", "nspin": 2, "source": "runs/a0/main/%s" % M,
            "active_site_index": site, "active_site_distance_A": dist,
            "q_d": q,
            "delta_q_d": {st: q[st] - q["slab"] for st in q if st != "slab"} if "slab" in q else {},
            "dq_c": dqc, "abs_dq_c": abs(dqc),
            "seed_witness": "WITNESS-UNAVAILABLE (single row, no seed spread; not a flag)",
            "carried_over_from_A11_R7": True,
        }

    # ---- Ti, Ru, Ir: the new material, from the SPIN arm -----------------------
    for M in UNDER:
        cands = spin_candidates(M)
        if not cands:
            raise Fatal("%s: no banked u000 nspin=2 lowdin artifacts in the spin arm" % M)
        chosen, stems = {}, {}
        for st in STATES:
            if st not in cands:
                excluded.append({"metal": M, "state": st, "seed": None,
                                 "reason": "state not banked at u000 in the spin arm"})
                continue
            pick = pick_seed(M, st, cands[st], excluded)
            if pick is None:
                excluded.append({"metal": M, "state": st, "seed": None,
                                 "reason": "zero converged nspin=2 seeds"})
                continue
            chosen[st] = pick
            stems[st] = pick["stem"]
        for need in ("s0_OH", "s0_OOH"):
            if need not in chosen:
                raise Fatal("%s: %s unavailable in the spin arm -- dq_c undefined"
                            % (M, need))
        site, dist, n_slab = active_site_spin(M, stems)
        mdir = os.path.join(ROOT, "runs", "a0", "spin", M)
        q = {st: qd_from(os.path.join(mdir, stems[st] + ".lowdin.txt"), site)
             for st in chosen}
        dqc = q["s0_OOH"] - q["s0_OH"]

        # corrected witness: spread of dq_c ACROSS SEEDS at the same U
        seed_dqc = {}
        oh_by_seed = {s: st for s, st in cands.get("s0_OH", [])}
        ooh_by_seed = {s: st for s, st in cands.get("s0_OOH", [])}
        for s in sorted(set(oh_by_seed) & set(ooh_by_seed)):
            try:
                a = qd_from(os.path.join(mdir, ooh_by_seed[s] + ".lowdin.txt"), site)
                b = qd_from(os.path.join(mdir, oh_by_seed[s] + ".lowdin.txt"), site)
            except Fatal:
                continue
            seed_dqc[s] = a - b
        spread = (max(seed_dqc.values()) - min(seed_dqc.values())) if len(seed_dqc) > 1 else None
        unstable = (spread is not None and spread > abs(dqc))

        per_metal[M] = {
            "arm": "spin", "nspin": 2, "source": "runs/a0/spin/%s" % M,
            "active_site_index": site, "active_site_distance_A": dist,
            "selected_seeds": {st: {k: chosen[st][k] for k in
                                    ("seed", "energy_ry", "n_converged_seeds",
                                     "tied_within_1e-6_Ry")} for st in chosen},
            "q_d": q,
            "delta_q_d": ({st: q[st] - q["slab"] for st in q if st != "slab"}
                          if "slab" in q else {}),
            "dq_c": dqc, "abs_dq_c": abs(dqc),
            "seed_witness": {
                "dq_c_by_seed": seed_dqc,
                "spread": spread,
                "verdict": ("SEED-UNSTABLE" if unstable else
                            ("STABLE" if spread is not None else
                             "WITNESS-UNAVAILABLE (fewer than two paired seeds)")),
            },
            "carried_over_from_A11_R7": False,
        }

    # ---- self-check 4: the carry-over must be EXACT ----------------------------
    carry = {}
    for M in OVER:
        mine = per_metal[M]["abs_dq_c"]
        theirs = r7pm[M]["abs_dq_c"] if "abs_dq_c" in r7pm[M] else abs(r7pm[M]["dq_c"])
        carry[M] = {"a11_r8": mine, "a11_r7": theirs, "delta": mine - theirs}
        if abs(mine - theirs) > 0.0:
            raise Fatal("CHECK 4 FAILED %s: |dq_c| %r != A11.R7's %r -- the reader "
                        "changed and the comparison is void" % (M, mine, theirs))

    # ---- R8-P1 ----------------------------------------------------------------
    flagged = [M for M in UNDER
               if isinstance(per_metal[M]["seed_witness"], dict)
               and per_metal[M]["seed_witness"]["verdict"] == "SEED-UNSTABLE"]
    scored_under = [M for M in UNDER if M not in flagged]
    if not scored_under:
        p1 = {"verdict": "VOID", "reason": "every under-floor metal is SEED-UNSTABLE"}
    else:
        p1 = separation([per_metal[M]["abs_dq_c"] for M in OVER],
                        [per_metal[M]["abs_dq_c"] for M in scored_under])
    p1["scored_under_floor"] = scored_under
    p1["excluded_seed_unstable"] = flagged
    p1["registered_asymmetry"] = (
        "A separation proves nothing -- 3-vs-3 along a line still aligned with 3d/4d/5d "
        "identity cannot establish a mechanism. A FAILURE to separate falsifies the "
        "rescue: R7-P3's result was then not an artifact of the unpolarised decks.")

    # ---- R8-P3 (reported, never scored) ---------------------------------------
    p3 = {}
    for M in UNDER:
        was = r7pm[M]["abs_dq_c"] if "abs_dq_c" in r7pm[M] else abs(r7pm[M]["dq_c"])
        now = per_metal[M]["abs_dq_c"]
        p3[M] = {"abs_dq_c_nspin1": was, "abs_dq_c_nspin2": now, "shift": now - was}

    # ---- R8-P2 (reported, never scored) ---------------------------------------
    # A11.R7's construction, reproduced exactly: dq_i are the CHE STEP INCREMENTS
    #   dq1 = Dq_d(*OH)            (step 1: *    -> *OH)
    #   dq2 = Dq_d(*O)  - Dq_d(*OH) (step 2: *OH  -> *O)
    #   dq3 = Dq_d(*OOH)- Dq_d(*O)  (step 3: *O   -> *OOH)
    # paired against span_dG1/2/3 from the A0 MAIN readout, unchanged (the response
    # is held fixed so A11.R8 stays a single-variable change).
    xs, ys, pairs = [], [], []
    for M in METALS:
        dq = per_metal[M].get("delta_q_d", {})
        if not all(k in dq for k in ("s0_OH", "s0_O", "s0_OOH")):
            excluded.append({"metal": M, "state": "R8-P2", "seed": None,
                             "reason": "one of *OH/*O/*OOH missing; metal omitted "
                                       "from the per-step pairing"})
            continue
        steps = {1: dq["s0_OH"],
                 2: dq["s0_O"] - dq["s0_OH"],
                 3: dq["s0_OOH"] - dq["s0_O"]}
        for i in (1, 2, 3):
            y = r7pm[M].get("span_dG%d" % i)
            if y is None:
                continue
            xs.append(abs(steps[i]))
            ys.append(float(y))
            pairs.append({"metal": M, "step": i, "abs_dq_step": abs(steps[i]),
                          "span_dG_eV": float(y)})
    if len(xs) >= 3:
        _rho, _p, _meth = R7.perm_p(xs, ys)
        p2 = {"n": len(xs), "rho": _rho, "p_nominal": _p,
              "method": _meth, "pairs": pairs,
              "note": "the three steps of one metal share that metal's slab reference "
                      "and are not independent; p is NOMINAL, exactly as in A11.R7"}
    else:
        p2 = {"n": len(xs), "rho": None, "p_nominal": None, "pairs": pairs,
              "note": "fewer than three usable pairs"}
    p2["status"] = ("REPORTED, NEVER SCORED -- 9 of 18 pairs are carried over from "
                    "A11.R7, whose post-hoc all-six value is already known "
                    "(rho -0.3808, p 0.1209); no threshold on it would be honest.")

    out = {
        "artifact": "a11_r8 -- the valence tracker with every predictor spin-polarised",
        "registered": "docs/43 A11.R8, commit 07cfc4f (no script, no result in it)",
        "zero_su": True,
        "binding": ("A11.R8 cannot move A7.2 or A7.3. A7.2 stays CONFIRMED 5 of 6; "
                    "A7.3 stays NOT MET at 3 of 6 at denominator 6 (docs/59 SS3c "
                    "granted and confirmed 2026-08-31) whatever this returns. It acts "
                    "on the EXPLANATION of the split, never on the count."),
        "design": {
            "over_floor_set": list(OVER), "under_floor_set": list(UNDER),
            "single_variable": ("only the predictor's spin treatment moves; the "
                                "response is the as-built span_U(c_M)/2 from the A0 "
                                "MAIN readout, identical to A11.R7"),
            "why_not_equalised_response": (
                "[D2 GUARD-3 ADJUDICATED 2026-09-03] makes Ru's and Ir's equalised "
                "spans BRANCH-CONDITIONAL and not scoreable into a span; using them "
                "would violate a dated line written the same day."),
            "seed_rule": ("lowest total energy among converged nspin=2 seeds; ties "
                          "below 1e-6 Ry to the lowest seed label; NOT the census "
                          "winner, whose pool includes the nspin=1 row"),
            "witness": ("corrected, like-for-like: spread of dq_c ACROSS SEEDS at the "
                        "same U. A11.R7's witness compared a swing across U against a "
                        "fixed-U state difference and is disclosed as malformed."),
        },
        "per_metal": per_metal,
        "R8_P1": p1,
        "R8_P2": p2,
        "R8_P3": p3,
        "self_checks": {
            "1_parser_identity": "A11.R7's parse_lowdin/check_atoms imported and used",
            "2_per_atom_sum": "enforced in check_atoms (fatal)",
            "3_spin_sum": "enforced in check_atoms (fatal)",
            "4_carry_over_identity": carry,
            "5_named_exclusions": excluded,
        },
        "excluded": excluded,
    }

    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    _write_md(args.md, out)
    print("R8-P1: %s" % p1.get("verdict"))
    for M in METALS:
        print("  %-3s |dq_c| = %.4f  (%s arm)" % (M, per_metal[M]["abs_dq_c"],
                                                  per_metal[M]["arm"]))
    print("wrote %s" % args.json)
    print("wrote %s" % args.md)
    return 0


def _write_md(path, out):
    L = []
    A = L.append
    pm = out["per_metal"]
    p1 = out["R8_P1"]
    A("# A11.R8 - the valence tracker with every predictor spin-polarised")
    A("")
    A("*Generated by `src/dft/a0spin_valence.py`. Registered in docs/43 **A11.R8** "
      "(2026-09-03) at commit **07cfc4f**, which carried no script and no result. "
      "Zero new DFT; zero SU.*")
    A("")
    A("## The one thing this tests")
    A("")
    A("A11.R7's R7-P3 fired: |dq_c| interleaved the A7.3 over- and under-floor sets. "
      "One rescue survived it -- that the failure was an artifact of Ti/Ru/Ir being "
      "read from decks that carry no `nspin` card (0/28, 0/32, 0/32). A11.R8 re-reads "
      "those three from the A0-SPIN arm, where the decks are `nspin = 2`, and changes "
      "**nothing else**.")
    A("")
    A("## R8-P1 (primary, n = 6): **%s**" % p1.get("verdict"))
    A("")
    A("| metal | group | arm | nspin | \\|dq_c\\| |")
    A("|---|---|---|---|---|")
    for M in ("Cr", "Mn", "Fe", "Ti", "Ru", "Ir"):
        grp = "OVER floor" if M in OVER else "under floor"
        A("| %s | %s | %s | %s | %.4f |" % (M, grp, pm[M]["arm"], pm[M]["nspin"],
                                            pm[M]["abs_dq_c"]))
    A("")
    if "max_abs_dqc_under_floor" in p1:
        A("Largest under-floor |dq_c| = **%.4f**; smallest over-floor |dq_c| = "
          "**%.4f**; gap = **%+.4f**."
          % (p1["max_abs_dqc_under_floor"], p1["min_abs_dqc_over_floor"], p1["gap"]))
        A("")
    A("**Registered asymmetry, written before the numbers existed.** %s"
      % p1["registered_asymmetry"])
    A("")
    A("## R8-P3 (reported, never scored): how far the spin convention moves the tracker")
    A("")
    A("| metal | \\|dq_c\\| at nspin=1 (A11.R7) | \\|dq_c\\| at nspin=2 (here) | shift |")
    A("|---|---|---|---|")
    for M in ("Ti", "Ru", "Ir"):
        r = out["R8_P3"][M]
        A("| %s | %.4f | %.4f | %+.4f |" % (M, r["abs_dq_c_nspin1"],
                                            r["abs_dq_c_nspin2"], r["shift"]))
    A("")
    A("## R8-P2")
    A("")
    A("%s" % out["R8_P2"]["status"])
    A("")
    A("## Self-check 4 -- the carry-over is exact")
    A("")
    A("| metal | A11.R7 | A11.R8 | delta |")
    A("|---|---|---|---|")
    for M, r in sorted(out["self_checks"]["4_carry_over_identity"].items()):
        A("| %s | %.6f | %.6f | %.1e |" % (M, r["a11_r7"], r["a11_r8"], r["delta"]))
    A("")
    A("Cr, Mn and Fe are the same files under the same rule, so any non-zero delta "
      "would mean the reader changed and the comparison is void.")
    A("")
    A("## What this cannot do")
    A("")
    A(out["binding"])
    A("")
    ex = out["excluded"]
    A("## Exclusions (%d)" % len(ex))
    A("")
    if not ex:
        A("None.")
    else:
        A("| metal | state | seed | reason |")
        A("|---|---|---|---|")
        for e in ex:
            A("| %s | %s | %s | %s |" % (e["metal"], e["state"], e.get("seed"),
                                         e["reason"]))
    A("")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
