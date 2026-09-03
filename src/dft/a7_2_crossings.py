#!/usr/bin/env python3
"""A7.2's first-class deliverable: where each metal's potential-limiting step flips.

docs/43:1348-1353 registers it in those words -- *"The U at which each metal's pls flips
is a first-class deliverable."*  What the campaign has banked is a set of **brackets**
(`a0main_readout.json` `a7_2.flip_brackets`), each 0.5-1.5 eV wide.  A bracket is where a
crossing is; a location is where it happens.  This produces the location, at zero cost,
from the banked ladder.

What it does NOT do
-------------------
These are **linear interpolations on a fixed-geometry U grid**, not measured crossings.
The bracket remains the measured object and is printed beside every estimate.  Nothing
here re-runs a deck, banks an energy, or moves A7.2's CONFIRMED 5-of-6 verdict.

The three-rung trap, and why this refuses instead of interpolating through it
----------------------------------------------------------------------------
A pls flip is a change in `argmax_i dG_i`, so the crossing is where the two rungs that
hold the argmax at the bracket's ends become equal.  A naive two-rung interpolation is
only valid if no THIRD rung rises above both inside the bracket -- and that is not
hypothetical here: at Cr U = 4.0 the gap dG2 - dG3 is 0.1844 eV while the true
max-minus-runner-up margin is 0.0760 eV, because the runner-up is rung 1, not rung 3
(docs/70 s8.1 C-5).  So every estimate is checked: at the interpolated U*, all four
linearly-interpolated rungs are compared, and if any third rung is at or above the
crossing pair the bracket is reported **CONTENDED** with no point estimate.

Self-checks (fatal)
-------------------
  1  the pls recomputed from the banked dG rows equals the banked `pls` on every row
     (an independent witness that the rung algebra here matches the readout's);
  2  every bracket in `a7_2.flip_brackets` is matched to a computed crossing, and every
     computed crossing to a bracket -- neither set may contain a row the other lacks;
  3  each interpolated U* lies inside its own bracket.

Usage
-----
    python src/dft/a7_2_crossings.py [--json OUT.json] [--md OUT.md]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

G_TOTAL = 4.92          # eV, src/hea_oer/descriptors.py:34 -- imported convention


class Fatal(Exception):
    pass


def steps(row):
    """The four CHE rungs, in the campaign's convention."""
    return [row["dG_OH"],
            row["dG_O"] - row["dG_OH"],
            row["dG_OOH"] - row["dG_O"],
            G_TOTAL - row["dG_OOH"]]


def pls_of(row):
    s = steps(row)
    return 1 + max(range(4), key=lambda i: s[i])


def interp_cross(u1, s1, u2, s2, a, b):
    """U at which rung a and rung b cross, by linear interpolation of their difference.

    a and b are 0-based rung indices; returns None if the difference does not change
    sign across the interval (which would mean the bracket does not hold this pair).
    """
    f1 = s1[a] - s1[b]
    f2 = s2[a] - s2[b]
    if f1 == f2 or f1 * f2 > 0:
        return None
    return u1 + (0.0 - f1) * (u2 - u1) / (f2 - f1)


def lin(u1, v1, u2, v2, u):
    return v1 + (v2 - v1) * (u - u1) / (u2 - u1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="a7_2_crossings.py")
    ap.add_argument("--json", default=os.path.join(ROOT, "docs", "figs",
                                                   "a7_2_crossings.json"))
    ap.add_argument("--md", default=os.path.join(
        ROOT, "docs", "research", "2026-09-03-a7-2-crossing-locations.md"))
    args = ap.parse_args(argv)

    bank = json.load(open(os.path.join(ROOT, "docs", "figs",
                                       "a0main_readout.json"), encoding="utf-8"))
    brackets = bank["a7_2"]["flip_brackets"]

    results = {}
    check1 = 0
    for metal, m in bank["metals"].items():
        rows = [r for r in m["rows"]
                if all(r.get(k) is not None for k in ("dG_OH", "dG_O", "dG_OOH"))]
        rows.sort(key=lambda r: r["u"])
        # --- self-check 1 ------------------------------------------------------
        for r in rows:
            if r.get("pls") is not None:
                if pls_of(r) != r["pls"]:
                    raise Fatal("CHECK 1 FAILED %s U=%.2f: recomputed pls %d != banked "
                                "%d" % (metal, r["u"], pls_of(r), r["pls"]))
                check1 += 1
        found = []
        for r1, r2 in zip(rows[:-1], rows[1:]):
            p1, p2 = pls_of(r1), pls_of(r2)
            if p1 == p2:
                continue
            s1, s2 = steps(r1), steps(r2)
            a, b = p1 - 1, p2 - 1
            ustar = interp_cross(r1["u"], s1, r2["u"], s2, a, b)
            entry = dict(u_lo=r1["u"], u_hi=r2["u"], pls_lo=p1, pls_hi=p2,
                         bracket_width_eV=r2["u"] - r1["u"])
            if ustar is None:
                entry.update(u_star=None, status="NO SIGN CHANGE IN THE PAIR",
                             note="the two argmax rungs do not cross inside the "
                                  "bracket; a third rung carries the change")
                found.append(entry)
                continue
            # --- the three-rung contention check -------------------------------
            vals = [lin(r1["u"], s1[i], r2["u"], s2[i], ustar) for i in range(4)]
            pair_val = 0.5 * (vals[a] + vals[b])
            others = [(i + 1, vals[i]) for i in range(4) if i not in (a, b)]
            contenders = [(i, v) for i, v in others if v >= pair_val - 1e-12]
            margin = pair_val - max(v for _, v in others)
            if contenders:
                entry.update(u_star=None, status="CONTENDED",
                             third_rungs_at_or_above=contenders,
                             note="a third rung is at or above the crossing pair at the "
                                  "interpolated U*, so a two-rung interpolation is not "
                                  "valid here; the bracket stands as the deliverable")
            else:
                entry.update(u_star=ustar, status="LOCATED",
                             margin_to_next_rung_eV=margin,
                             note="linear interpolation of dG_%d - dG_%d on a "
                                  "fixed-geometry grid; nearest other rung is %.4f eV "
                                  "below the crossing" % (p1, p2, margin))
            found.append(entry)
        results[metal] = found

    # --- self-checks 2 and 3 -------------------------------------------------
    for metal, brs in brackets.items():
        got = results.get(metal, [])
        if len(got) != len(brs):
            raise Fatal("CHECK 2 FAILED %s: banked brackets %d, computed crossings %d"
                        % (metal, len(brs), len(got)))
        for br, e in zip(sorted(brs, key=lambda b: b[0]),
                         sorted(got, key=lambda e: e["u_lo"])):
            if abs(br[0] - e["u_lo"]) > 1e-9 or abs(br[1] - e["u_hi"]) > 1e-9:
                raise Fatal("CHECK 2 FAILED %s: bracket %r does not match computed "
                            "%r" % (metal, br, (e["u_lo"], e["u_hi"])))
            if e["u_star"] is not None and not (e["u_lo"] <= e["u_star"] <= e["u_hi"]):
                raise Fatal("CHECK 3 FAILED %s: U* %.4f outside its bracket [%s, %s]"
                            % (metal, e["u_star"], e["u_lo"], e["u_hi"]))
    for metal, got in results.items():
        if got and metal not in brackets:
            raise Fatal("CHECK 2 FAILED %s: computed %d crossings but the banked "
                        "readout lists no bracket" % (metal, len(got)))

    out = dict(
        registered_as="docs/43:1348-1353 -- 'The U at which each metal's pls flips is a "
                      "first-class deliverable.'",
        what_this_is="Linear interpolations on the banked fixed-geometry U grid. The "
                     "BRACKET remains the measured object and is printed beside every "
                     "estimate. Nothing here re-runs a deck, banks an energy, or moves "
                     "A7.2's CONFIRMED 5-of-6 verdict.",
        self_checks=dict(
            check1_pls_matches_banked="PASS (%d rows)" % check1,
            check2_brackets_and_crossings_are_the_same_set="PASS",
            check3_u_star_inside_its_bracket="PASS"),
        crossings=results,
        disclosed_non_blind_cr="docs/43:1356 discloses the Cr flip 3->2 between "
                               "U = 1.85 and 3.70 from the probe ladder; the A0-grid "
                               "row below is a separate, coarser measurement of the "
                               "same crossing and the two are not the same experiment.",
        binding="Moves no banked verdict. A7.2 stays CONFIRMED 5 of 6 on exactly 3 "
                "robust members; A7.3 stays NOT MET at 3 of 6.")
    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")

    L = []
    A = L.append
    A("# A7.2's crossing locations — the pls flip, located (2026-09-03)")
    A("")
    A("*Generated by `src/dft/a7_2_crossings.py`. **0 SU, zero new DFT.** "
      "docs/43:1348-1353 registers this in its own words: \"The U at which each metal's "
      "pls flips is a **first-class deliverable**.\" Until now the campaign had banked "
      "**brackets** 0.5–1.5 eV wide. A bracket says where a crossing is; this says where "
      "it happens.*")
    A("")
    A("**Read this as an interpolation, not a measurement.** Every U\\* below is a linear "
      "interpolation of the two contending rungs on a **fixed-geometry** U grid. The "
      "bracket is the measured object and is printed beside each estimate.")
    A("")
    A("| metal | bracket (eV) | width | flip | **U\\*** | margin to the next rung | status |")
    A("|---|---|---|---|---|---|---|")
    for metal in sorted(results):
        for e in sorted(results[metal], key=lambda e: e["u_lo"]):
            A("| %s | [%.2f, %.2f] | %.2f | %d → %d | %s | %s | **%s** |"
              % (metal, e["u_lo"], e["u_hi"], e["bracket_width_eV"],
                 e["pls_lo"], e["pls_hi"],
                 "—" if e["u_star"] is None else "**%.3f**" % e["u_star"],
                 "—" if e.get("margin_to_next_rung_eV") is None
                 else "%.4f eV" % e["margin_to_next_rung_eV"],
                 e["status"]))
    A("")
    A("## The three-rung check, and why it is not decoration")
    A("")
    A("A pls flip is a change in `argmax_i ΔG_i`, so the crossing is where the two rungs "
      "holding the argmax at the bracket's ends become equal. A two-rung interpolation is "
      "valid only if no **third** rung rises above both inside the bracket — and that is "
      "not hypothetical: at Cr U = 4.0 the gap ΔG₂ − ΔG₃ is 0.1844 eV while the true "
      "max-minus-runner-up margin is 0.0760 eV, because the runner-up is rung 1 "
      "(docs/70 §8.1 C-5). Every U\\* above is therefore checked against all four "
      "interpolated rungs, and a bracket where a third rung contends is reported "
      "**CONTENDED** with no point estimate rather than interpolated through.")
    A("")
    A("## Three conditionalities each of these rows carries")
    A("")
    A("1. **Ru's U\\* = %.3f sits in the equalised region.** Every (Ru, state, u900) cell "
      "is EQUALISED-BY-SELECTION(nspin = 1): 0 of 16 spin-polarised Ru SCFs converge at "
      "U = 9 across three pre-registered mixing settings (docs/68 §2, §11), so the upper "
      "end of Ru's bracket rests on the nspin = 1 convention. The crossing is located on "
      "the ladder the campaign actually ran, and that ladder's Ru endpoint is a "
      "convention, not a free solution."
      % (results["Ru"][0]["u_star"] if results.get("Ru") and results["Ru"][0]["u_star"]
         else float("nan")))
    A("2. **Cr's margin is the smallest by an order of magnitude** — %.4f eV against "
      "0.4385–2.4420 eV everywhere else. It clears the three-rung check, but it is the "
      "one row where a small change in the ladder could turn a LOCATED into a CONTENDED, "
      "and it is also the metal docs/43:1356 already discloses non-blind."
      % (results["Cr"][0]["margin_to_next_rung_eV"] if results.get("Cr")
         and results["Cr"][0].get("margin_to_next_rung_eV") else float("nan")))
    A("3. **Ir's bracket is saddle-conditional.** The banked readout flags it "
      "(`caveats.ir_ooh_basin`) and records that the EXISTENCE of an Ir flip inside the "
      "grid survives the saddle correction — so A7.2's CONFIRMED status does not rest on "
      "the bracket, but this row's U\\* does.")
    A("")
    A("The Cr row is also **not** the crossing docs/43:1356 discloses. That disclosure "
      "puts the Cr flip between U = 1.85 and 3.70 **on the probe ladder**; the row above "
      "is the A0 grid's own coarser measurement of the same physical crossing, and the "
      "two are different experiments that happen to agree (3.674 lies inside [1.85, "
      "3.70]).")
    A("")
    A("## Self-checks")
    A("")
    for k in sorted(out["self_checks"]):
        A("- `%s`: %s" % (k, out["self_checks"][k]))
    A("")
    A("Check 1 is the load-bearing one: the pls is recomputed here from the banked ΔG "
      "rows and compared against the `pls` the A0 readout wrote, on every row. Agreement "
      "means this file's rung algebra is the readout's, not a second opinion about it.")
    A("")
    A("## What this does not do")
    A("")
    A(out["binding"])
    A("")
    A("Locating a crossing is not verifying one. A registered verification would need "
      "fresh SCFs at each U\\*, and that spike (docs/70 §6 S-4) is **not** proposed here: "
      "docs/70 §8.1 C-7 records four defects in it as written, including that it "
      "registers a ninth ledger claimant against a cap of eight and that its own "
      "prediction is not evaluable by its own decks.")
    A("")
    with open(args.md, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))

    print(json.dumps({k: out[k] for k in ("self_checks", "crossings")},
                     indent=1, sort_keys=True))
    print("\nwrote %s\nwrote %s" % (args.json, args.md))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fatal as e:
        print("FATAL: %s" % e, file=sys.stderr)
        sys.exit(2)
