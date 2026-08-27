#!/usr/bin/env python
"""P-PROJ: the remaining 6 of the 8 registered projector-pairing SCFs (2026-08-27).

WHAT THIS SCORES, AND WHY IT IS THE NEXT THING TO RUN

A7.1 (docs/43 :1325-1345) registers P-PROJ verbatim:

    "Test: two Cr fixed-geometry SCF sets at U = 7.15 eV, 1x1 (matching A0),
     `HUBBARD (atomic)` vs `(ortho-atomic)`, all four states.
     PREDICTION (blind): |d-eta(Cr)| > 0.10 V. FALSIFIED below 0.03 V, in which
     case the projector is not a live variable at this U and Xu's supercell
     linear-response value may be imported as a literature anchor."

Two of the eight already exist. `runs/s0/e_proj/README.md` says so in terms:

    "The full 4-state pairing (2 projector sets x {slab, *OH, *O, *OOH} = 8 SCFs)
     runs LATER under the A0 budget per A7.1 -- these 2 S0 decks are reused as 2
     of those 8; the remaining 6 SCFs are A0 jobs, NOT S0 jobs."

So the *O pair is banked and scored (both converged, no error block, both at
magtot 10.00; E_atomic - E_ortho = +0.27021297 Ry = +3676.6 meV at identical
geometry and U). This builds the OTHER SIX: {slab, *OH, *OOH} x {atomic, ortho}.

  P-PROJ gates the fifth A0 grid point (U = 7.15 eV, Xu 2015 Table 1), and
  through it S4, which the ledger lists as "clear after S0(e)/P-PROJ" and which
  has ZERO decks built. The Anvil queue is empty and 74,105 of 100,000 SU remain
  with a 2026-10-15 freeze. This is the cheapest thing on the critical path:
  ~12 min wall each on 15 irreducible k-points, ~200 SU for all six.

DECK CONSTRUCTION -- the same one-line-diff discipline as the S3 builders.

Each deck differs from `runs/probe/Cr/<state>__base.in` in exactly:
  atomic leg: 2 lines -- the prefix, and `U Cr-3d 3.7000` -> `7.1500`
  ortho  leg: 3 lines -- those two, and `HUBBARD (atomic)` -> `(ortho-atomic)`
verified by diff at build time, refusing anything else. That is precisely the
transformation the two banked e_proj decks embody (checked against them here),
so the six new decks are the same object at three more states.

Geometry provenance is inherited unchanged: ATOMIC_POSITIONS of
`runs/probe/Cr/<state>__base.in`, themselves the final BFGS geometry of
`runs/Cr_slab/<state>.out`. These are fixed-geometry single points on an
already-relaxed structure and must never be reported as relaxed.

Nothing here changes a threshold, a functional, a cell, a cutoff or a k-mesh.
U = 7.1500 and the (ortho-atomic) card ARE the registered content of A7.1, not
deviations. nk = 4 matches the registered manifest lines in
`runs/s0/e_proj/manifest.json`.
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402

SRC_DIR = os.path.join(W.ROOT, "runs", "probe", "Cr")
DST_DIR = os.path.join(W.ROOT, "runs", "a0", "p_proj")

U_OLD = "U Cr-3d 3.7000"
U_NEW = "U Cr-3d 7.1500"
CARD_OLD = "HUBBARD (atomic)"
CARD_NEW = "HUBBARD (ortho-atomic)"

# state, source stem  (the *O pair is already banked in runs/s0/e_proj)
STATES = [
    ("slab", "slab__base"),
    ("s0_OH", "s0_OH__base"),
    ("s0_OOH", "s0_OOH__base"),
]
NK = 4

# The banked pair this build must reproduce the transformation of.
REFERENCE = os.path.join(W.ROOT, "runs", "s0", "e_proj")


def check_reference():
    """The two banked decks define the transformation; assert it before cloning."""
    src = W.read(os.path.join(SRC_DIR, "s0_O__base.in")).replace("\r\n", "\n")
    for leg, card in (("atomic", CARD_OLD), ("ortho", CARD_NEW)):
        path = os.path.join(REFERENCE, "s0_O__u715_%s.in" % leg)
        if not os.path.exists(path):
            W.die("%s: banked reference deck missing" % W.rel(path))
        ref = W.read(path).replace("\r\n", "\n")
        if U_NEW not in ref:
            W.die("%s: does not carry %r" % (W.rel(path), U_NEW))
        if card not in ref:
            W.die("%s: does not carry %r" % (W.rel(path), card))
        want = 2 if leg == "atomic" else 3
        d = [
            (i, a, b)
            for i, (a, b) in enumerate(zip(src.split("\n"), ref.split("\n")), 1)
            if a != b
        ]
        if len(d) != want:
            W.die(
                "%s differs from its source in %d lines, expected %d: %r"
                % (W.rel(path), len(d), want, [x[0] for x in d])
            )
    print("  reference OK: the banked *O pair is source + %d/%d line changes" % (2, 3))


def build_one(state, src_stem, leg):
    src_path = os.path.join(SRC_DIR, src_stem + ".in")
    if not os.path.exists(src_path):
        W.die("%s: source deck missing" % W.rel(src_path))
    src = W.read(src_path)

    m = re.search(r"^\s*calculation\s*=\s*'(\w+)'", src, re.M)
    if not m or m.group(1) != "scf":
        W.die("%s: expected a fixed-geometry scf, found %r"
              % (W.rel(src_path), m and m.group(1)))
    if W.FORBIDDEN_RESTART.search(src):
        W.die("%s: source deck carries a restart directive" % W.rel(src_path))

    nat = int(re.search(r"^\s*nat\s*=\s*(\d+)", src, re.M).group(1))
    rows = W.selftest_formatter(src, src_path)
    if nat != len(rows):
        W.die("%s: nat=%d but %d position lines" % (W.rel(src_path), nat, len(rows)))

    for token, n_expected in ((U_OLD, 1), (CARD_OLD, 1)):
        if src.count(token) != n_expected:
            W.die("%s: expected exactly %d %r, found %d"
                  % (W.rel(src_path), n_expected, token, src.count(token)))

    stem = "%s__u715_%s" % (state, leg)
    dst = os.path.join(DST_DIR, stem + ".in")
    out = os.path.join(DST_DIR, stem + ".out")
    for p in (dst, out):
        if os.path.exists(p):
            W.die("%s already exists -- refusing to overwrite (A8.8), %d bytes"
                  % (W.rel(p), os.path.getsize(p)))

    new = W.swap_scalar_line(src, src_path, "prefix", src_stem, stem)
    new = new.replace(U_OLD, U_NEW)
    if leg == "ortho":
        new = new.replace(CARD_OLD, CARD_NEW)

    want = 2 if leg == "atomic" else 3
    d = W.diff_lines(src, new, dst)
    if len(d) != want:
        W.die("%s: expected exactly %d differing lines, got %d: %r"
              % (W.rel(dst), want, len(d), d))
    kinds = set()
    for _lineno, before, after in d:
        if "prefix" in before:
            kinds.add("prefix")
        elif before.strip() == U_OLD and after.strip() == U_NEW:
            kinds.add("u")
        elif before.strip() == CARD_OLD and after.strip() == CARD_NEW:
            kinds.add("card")
        else:
            W.die("%s: unexpected differing line %r -> %r" % (W.rel(dst), before, after))
    expected_kinds = {"prefix", "u"} | ({"card"} if leg == "ortho" else set())
    if kinds != expected_kinds:
        W.die("%s: changed %r, expected %r" % (W.rel(dst), kinds, expected_kinds))
    if W.FORBIDDEN_RESTART.search(new):
        W.die("%s: restart directive appeared during the swap" % W.rel(dst))

    W.write(dst, new)
    print("  built %-46s nat=%-3d nk=%-2d (from %s)"
          % (W.rel(dst), nat, NK, src_stem + ".in"))
    return ("a0/p_proj", stem, ".in", NK, state, leg, nat)


HDR = """\
# P-PROJ: the remaining 6 of the 8 registered projector-pairing SCFs.
# Built 2026-08-27 by src/dft/build_pproj.py.
#
# A7.1 (docs/43 :1325-1345), verbatim: "Test: two Cr fixed-geometry SCF sets at
# U = 7.15 eV, 1x1 (matching A0), `HUBBARD (atomic)` vs `(ortho-atomic)`, all
# four states. PREDICTION (blind): |d-eta(Cr)| > 0.10 V. FALSIFIED below 0.03 V,
# in which case the projector is not a live variable at this U and Xu's
# supercell linear-response value may be imported as a literature anchor."
#
# TWO OF THE EIGHT ARE ALREADY BANKED. runs/s0/e_proj/README.md: "the full
# 4-state pairing (2 projector sets x {slab, *OH, *O, *OOH} = 8 SCFs) runs LATER
# under the A0 budget per A7.1 -- these 2 S0 decks are reused as 2 of those 8;
# the remaining 6 SCFs are A0 jobs, NOT S0 jobs." The *O pair converged with no
# error block, both at magtot 10.00, E_atomic - E_ortho = +0.27021297 Ry
# (+3676.6 meV) at identical geometry and U. These six are the other three
# states, both legs.
#
# WHY NOW. P-PROJ gates the fifth A0 grid point and through it S4, which the
# ledger lists as "clear after S0(e)/P-PROJ" and which has zero decks built.
# The queue is empty; this is the cheapest thing on the critical path.
#
# DECKS. Each differs from runs/probe/Cr/<state>__base.in in exactly 2 lines
# (atomic: prefix, U 3.7000 -> 7.1500) or 3 (ortho: + HUBBARD (atomic) ->
# (ortho-atomic)), asserted at build time against the banked pair's own
# transformation. Fixed-geometry single points on the final BFGS geometry of
# runs/Cr_slab/<state>.out -- NEVER to be reported as relaxed.
#
# SCORING. Score per state: converged (no "convergence NOT achieved", a final
# "!" energy) and no "Error in routine" block; then dE = E_atomic - E_ortho at
# identical geometry and U, and the magnetization pair alongside. The eta
# consequence -- the thing A7.1 predicts on -- is assembled from all four states
# by the CHE ladder, not from any single dE. Report the four dE values and the
# resulting |d-eta| together; a magnetization mismatch between the legs of a
# pair is a BRANCH MISMATCH and is reported as such, never averaged away.
#
# nk = 4 matches the registered manifest lines in runs/s0/e_proj/manifest.json
# (15 irreducible k-points; NP must be an exact multiple of nk).
#
# SUBMIT WITH EXCLUDE=a024,a050,a088,a196,a220,a223
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""


def main():
    if not os.path.isdir(SRC_DIR):
        W.die("%s: source directory missing" % W.rel(SRC_DIR))
    os.makedirs(DST_DIR, exist_ok=True)
    check_reference()

    rows = []
    for state, src_stem in STATES:
        for leg in ("atomic", "ortho"):
            rows.append(build_one(state, src_stem, leg))

    body = []
    for _d, job, _s, nk, state, leg, nat in rows:
        body.append("#   %-24s nat=%-3d nk=%-2d  Cr %s, U=7.1500, HUBBARD (%s)\n"
                    % (job, nat, nk, state, leg))
    hdr = HDR.rstrip("\n") + "\n#\n" + "".join(body) + "#\n"

    hits = [l for l in hdr.splitlines() if "NP=" in l or "NCONC=" in l]
    if hits != ["# NP=128 NCONC=1"]:
        W.die("manifest header must mention NP=/NCONC= exactly once; found %r" % hits)

    txt = hdr + "".join("%s %s %s %d\n" % (d, job, s, nk)
                        for d, job, s, nk, _st, _lg, _n in rows)
    path = os.path.join(W.ROOT, "runs", "a0", "m_pproj.txt")
    if os.path.exists(path):
        W.die("%s already exists -- refusing to overwrite" % W.rel(path))
    W.write(path, txt)
    print("\nwrote %s  (%d rows)" % (W.rel(path), len(rows)))
    for d, job, s, nk, _st, _lg, _n in rows:
        print("  %s %s %s %d" % (d, job, s, nk))


if __name__ == "__main__":
    main()
