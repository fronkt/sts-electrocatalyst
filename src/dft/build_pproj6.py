#!/usr/bin/env python
"""P-PROJ-6: the projector contrast across the closed six-metal A0 roster at U = 7.50 eV.

WHAT THIS IS FOR

A7.1 / P-PROJ is confirmed on ONE metal: Cr, at U = 7.15 eV, 1x1, atomic vs
ortho-atomic, eta 1.155 V vs 1.642 V with the potential-limiting step flipping.
The standing objection is n = 1 -- and Cr's eta(U) curve is a V with its minimum
at U = 3.5, so Cr is unusually sensitive in exactly that region.

This builds the ortho-atomic leg for all six A0 metals at a single common U, so
the split can be read as a property of the METHOD rather than of CrO2.

  {Cr, Mn, Fe, Ti, Ru, Ir} x {slab, s0_O, s0_OH, s0_OOH} = 24 SCFs.

WHY U = 7.50 AND NOT SOMETHING ELSE -- all five reasons measured, not argued:

  * cheapest common rung: the 24 banked atomic partners cost 138.7 SU total
  * ZERO non-convergence among those partners (24/24 JOB DONE). At U = 4.50 the
    Fe s0_O partner hit electron_maxstep=200 and cost 266.5 SU over four
    submissions.
  * 0.35 eV from the headline U = 7.15, the closest common rung to it
  * the atomic pls baselines at this rung span 1, 2 AND 3 (Mn 1, Ru 3, rest 2)
  * every metal carries a HUBBARD (atomic) card with its own U at u750, so the
    transformation needs NO U edit -- one keyword line, nothing else

THE TRANSFORMATION, and the guard on it

Each ortho deck differs from runs/a0/main/<M>/<state>__u750.in in EXACTLY two
lines:

    prefix = '<state>__u750'        ->  '<state>__u750_ortho'
    HUBBARD (atomic)               ->  HUBBARD (ortho-atomic)

The U value, geometry, cell, cutoffs, k-mesh, spin convention, smearing and
pseudopotentials are inherited byte-identically. build_one() diffs source
against product line by line and DIES if any third line differs, or if either
expected change is missing. That is the same discipline as build_pproj.py, and
the banked u715 Cr pair is asserted as the reference transformation before any
deck is cloned.

Only converged partners are paired: a source whose .out does not carry JOB DONE
is refused, because a projector CONTRAST against a state the campaign does not
bank is meaningless.

projwfc.in is NOT written here. anvil/46_a0.slurm generates it at runtime from
the deck's own prefix (A6.5(1)), so writing one would create a second source of
truth for the same field.

REGISTRATION -- LICENSED 2026-09-03

  The decks were built BEFORE the thresholds were adopted (c2e9a18), and the
  thresholds were adopted and committed BEFORE anything was submitted (8aba0ae),
  so the objects submitted are provably the objects built and the arm is blind.
  That ordering is the whole point; do not collapse it on a re-run.

  Amendment 12 (docs/77) closed three defects in that dated line:

    1. |Delta-eta| is the primary statistic. The residual R_M is a DIAGNOSTIC.
       A uniform offset on the cumulative dG gives R_M = 0.40 eV with
       Delta-eta = 0.0000 V exactly at pls 2 or 3.
    2. The denominator is the FIVE blind metals. Cr is calibration -- its
       result is known today and it may not also be counted.
    3. A pseudopotential-family confound clause. The PP census is ultrasoft
       {Cr, Mn, Ti, Ir}, PAW {Fe}, norm-conserving {Ru}, so a CONFIRM set of
       four has exactly the cardinality of the ultrasoft family.

  Re-running this script rewrites decks and manifest deterministically. It does
  NOT re-open the registration.

Usage:
    PYTHONPATH=src python src/dft/build_pproj6.py            # build + verify
    PYTHONPATH=src python src/dft/build_pproj6.py --check    # verify only, no write
"""

import hashlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402

SRC_ROOT = os.path.join(W.ROOT, "runs", "a0", "main")
DST_ROOT = os.path.join(W.ROOT, "runs", "a0", "pproj6")
MANIFEST = os.path.join(W.ROOT, "runs", "a0", "m_pproj6.txt")

METALS = ["Cr", "Mn", "Fe", "Ti", "Ru", "Ir"]
STATES = ["slab", "s0_O", "s0_OH", "s0_OOH"]
RUNG = "u750"

CARD_OLD = "HUBBARD (atomic)"
CARD_NEW = "HUBBARD (ortho-atomic)"

# The banked Cr pair at u715 that defines the transformation.
REF_DIR = os.path.join(W.ROOT, "runs", "a0", "p_proj")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_reference():
    """The banked u715 Cr pair defines the projector transformation. Assert it."""
    a = os.path.join(REF_DIR, "s0_OH__u715_atomic.in")
    o = os.path.join(REF_DIR, "s0_OH__u715_ortho.in")
    for p in (a, o):
        if not os.path.exists(p):
            W.die("%s: banked reference deck missing" % W.rel(p))
    at = W.read(a).replace("\r\n", "\n").split("\n")
    ot = W.read(o).replace("\r\n", "\n").split("\n")
    if len(at) != len(ot):
        W.die("reference pair differs in line count: %d vs %d" % (len(at), len(ot)))
    d = [(i, x, y) for i, (x, y) in enumerate(zip(at, ot), 1) if x != y]
    if len(d) != 2:
        W.die("reference pair differs in %d lines, expected 2: %r"
              % (len(d), [x[0] for x in d]))
    kinds = sorted("prefix" if "prefix" in x else "hubbard" if "HUBBARD" in x else "?"
                   for _, x, _ in d)
    if kinds != ["hubbard", "prefix"]:
        W.die("reference pair changes the wrong lines: %r" % (kinds,))
    print("  reference OK: the banked u715 Cr pair is prefix + HUBBARD card, 2 lines")


def source_is_converged(metal, state):
    out = os.path.join(SRC_ROOT, metal, "%s__%s.out" % (state, RUNG))
    if not os.path.exists(out):
        return False, "no .out"
    txt = W.read(out)
    if "JOB DONE" not in txt:
        return False, "no JOB DONE"
    if re.search(r"convergence NOT achieved", txt):
        return False, "convergence NOT achieved"
    return True, "ok"


def build_one(metal, state, write):
    stem = "%s__%s" % (state, RUNG)
    src_path = os.path.join(SRC_ROOT, metal, stem + ".in")
    if not os.path.exists(src_path):
        W.die("%s: source deck missing" % W.rel(src_path))

    ok, why = source_is_converged(metal, state)
    if not ok:
        W.die("%s/%s: atomic partner is not banked (%s) -- a projector contrast "
              "against an unbanked state is meaningless" % (metal, stem, why))

    src = W.read(src_path).replace("\r\n", "\n")

    if CARD_OLD not in src:
        W.die("%s: does not carry %r" % (W.rel(src_path), CARD_OLD))
    if CARD_NEW in src:
        W.die("%s: already ortho-atomic" % W.rel(src_path))

    want_prefix_old = "prefix = '%s'" % stem
    if want_prefix_old not in src:
        W.die("%s: expected %r" % (W.rel(src_path), want_prefix_old))

    new = src.replace(want_prefix_old, "prefix = '%s_ortho'" % stem, 1)
    new = new.replace(CARD_OLD, CARD_NEW, 1)

    a = src.split("\n")
    b = new.split("\n")
    if len(a) != len(b):
        W.die("%s: line count changed %d -> %d" % (W.rel(src_path), len(a), len(b)))
    d = [(i, x, y) for i, (x, y) in enumerate(zip(a, b), 1) if x != y]
    if len(d) != 2:
        W.die("%s/%s: expected exactly 2 differing lines, got %d: %r"
              % (metal, stem, len(d), [x[0] for x in d]))
    for _, before, after in d:
        if "prefix" in before and "prefix" in after:
            continue
        if before.strip() == CARD_OLD and after.strip() == CARD_NEW:
            continue
        W.die("%s/%s: unexpected differing line %r -> %r" % (metal, stem, before, after))

    # The U line must be untouched and must be this metal's own U at 7.5000.
    mu = re.search(r"^U\s+(\w+)-3d\s+([0-9.]+)\s*$", new, re.M)
    if not mu:
        mu = re.search(r"^U\s+(\w+)-[45]d\s+([0-9.]+)\s*$", new, re.M)
    if not mu:
        W.die("%s/%s: no U line found" % (metal, stem))
    if abs(float(mu.group(2)) - 7.5) > 1e-9:
        W.die("%s/%s: U is %s, expected 7.5000 -- wrong rung"
              % (metal, stem, mu.group(2)))

    dst_dir = os.path.join(DST_ROOT, metal)
    dst = os.path.join(dst_dir, stem + "_ortho.in")
    if write:
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        W.write(dst, new)
    return dst, mu.group(1), float(mu.group(2))


def main():
    check_only = "--check" in sys.argv
    print("P-PROJ-6 builder -- %s" % ("CHECK ONLY, no files written" if check_only
                                      else "building"))
    check_reference()

    rows = []
    for metal in METALS:
        for state in STATES:
            dst, species, u = build_one(metal, state, write=not check_only)
            rows.append((metal, state, dst, species, u))

    print("  %d decks %s" % (len(rows), "verified" if check_only else "written"))

    if check_only:
        return

    lines = [
        "# P-PROJ-6 manifest -- ortho-atomic leg, six metals, U = 7.50 eV.",
        "# Built by src/dft/build_pproj6.py. Each deck differs from its",
        "# runs/a0/main/<M>/<state>__u750.in source in exactly 2 lines:",
        "#   prefix, and HUBBARD (atomic) -> (ortho-atomic).",
        "#",
        "# LICENSED 2026-09-03. Amendment 12 (docs/77) ADOPTED by the entrant's",
        "# dated decision of record, committed at 8aba0ae BEFORE any deck was",
        "# submitted and before any output existed: |Delta-eta| primary, R_M a",
        "# diagnostic only, denominator = the FIVE blind metals with Cr as",
        "# labelled calibration, four count bands including the middle band, the",
        "# anti-selection clause, and the pseudopotential and spin confound",
        "# clauses. The decks themselves were built and md5-manifested at",
        "# c2e9a18, before those thresholds were adopted.",
        "#",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171",
        "#",
        "# nk = 4 matches the banked atomic partners at this rung, and NP = 128",
        "# is a multiple of it. Runnable rows are: dir job suffix nk",
        "#",
        "# md5 of each deck, for the record:",
    ]
    for metal, state, dst, species, u in rows:
        lines.append("#   %-6s %-9s %6.4f  %s" % (metal, state, u, md5(dst)))
    lines.append("#")
    for metal, state, dst, species, u in rows:
        lines.append("a0/pproj6/%s %s__%s_ortho .in 4" % (metal, state, RUNG))
    W.write(MANIFEST, "\n".join(lines) + "\n")
    print("  manifest -> %s" % W.rel(MANIFEST))
    print()
    print("  LICENSED per docs/77, adopted 2026-09-03 at 8aba0ae.")
    print("  Submit: bash anvil/47_submit_a0.sh $PROJECT/sts/runs/a0/m_pproj6.txt 6")


if __name__ == "__main__":
    main()
