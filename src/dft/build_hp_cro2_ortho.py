#!/usr/bin/env python
"""The missing cell: CrO2 bulk linear-response U under the ORTHO-ATOMIC projector.

WHAT THIS CLOSES

runs/hp_tio2 holds three of the four cells of a 2x2 grid:

              atomic                     ortho-atomic
  TiO2        4.2245 / 4.2251 eV         5.6688 / 5.6743 eV      split 1.44 eV
  CrO2        6.1635 eV (q222)           <- THIS. MISSING.

The TiO2 pair is the campaign's second projector observable: the same keyword
that moves eta by 0.487 V on the Cr slab moves the SELF-CONSISTENT U on bulk
TiO2 by 1.44 eV. It is n = 1 in materials. This deck makes it n = 2, and does so
on the FLAGSHIP material -- the same CrO2 whose slab carries A7.1.

It also crosses an axis TiO2 cannot: TiO2 is nspin = 1, closed-shell d0. CrO2 is
nspin = 2, magnetic 3d. So the arm tests whether the projector split survives
spin polarisation, on the metal the headline is about.

COST, measured from the banked atomic legs in runs/hp_tio2:
  scf__cro2.out   37.44 s   at np=20
  hp__cro2_q222   19m36.81s at np=20  = 6.54 core-h, ZERO non-convergence lines
Ortho hp.x measured CHEAPER than atomic on all three banked TiO2 q-pairs
(0.894 / 0.967 / 0.982 of atomic). ~11 SU floor, ~72 SU ceiling against
niter_max = 80. Under 0.12 % of balance.

DO NOT CONFUSE THIS WITH THE SLAB. The "108 core-hours per (atom,q) pair" and
the 4/4 "Convergence has not been reached" in the record are the CrO2 SLAB at
np=18 (runs/hp_costmodel). The BULK ran clean and 16x cheaper. docs/76 section 6
refused an hp.x arm on the strength of the slab number applied to a bulk run;
docs/78 section 1 strikes that.

THE TRANSFORMATION, and the guard

  scf__cro2_ortho.in differs from runs/hp_tio2/scf__cro2.in in EXACTLY 3 lines:
      prefix, outdir, and HUBBARD (atomic) -> (ortho-atomic)
  hp__cro2_ortho_q222.in differs from runs/hp_tio2/hp__cro2_q222.in in EXACTLY
  2 lines: prefix and outdir.

Both are asserted against the banked TiO2 atomic/ortho pair, which embodies
exactly those diffs, before anything is cloned. Any third differing line is
fatal.

A8.8 ISOLATION. Output goes to runs/hp_cro2_ortho/, NOT into runs/hp_tio2/.
queue_hp.sh's run_one writes "> ${hp}.out" unconditionally with no stale-output
refusal; pointed at the banked directory it would overwrite evidence. The banked
tree is read-only by construction.

pseudo_dir is left as the deck's own string and rewritten at run time by the
wrapper, the way queue_r1.sh:293 does for pw.x decks. Baking a machine path into
a deck is what made queue_hp.sh unportable in the first place.

Usage:
    PYTHONPATH=src python src/dft/build_hp_cro2_ortho.py [--check]
"""

import hashlib
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402

SRC = os.path.join(W.ROOT, "runs", "hp_tio2")
DST = os.path.join(W.ROOT, "runs", "hp_cro2_ortho")
MANIFEST = os.path.join(W.ROOT, "runs", "m_hp_cro2_ortho.txt")

CARD_OLD = "HUBBARD (atomic)"
CARD_NEW = "HUBBARD (ortho-atomic)"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def diff(a, b):
    la, lb = a.split("\n"), b.split("\n")
    if len(la) != len(lb):
        W.die("line count changed: %d -> %d" % (len(la), len(lb)))
    return [(i, x, y) for i, (x, y) in enumerate(zip(la, lb), 1) if x != y]


def check_reference():
    """The banked TiO2 pair embodies both transformations. Assert before cloning."""
    for stem, want in (("scf__%s.in", 3), ("hp__%s_q222.in", 2)):
        a = W.read(os.path.join(SRC, stem % "atomic")).replace("\r\n", "\n")
        o = W.read(os.path.join(SRC, stem % "ortho")).replace("\r\n", "\n")
        d = diff(a, o)
        if len(d) != want:
            W.die("%s reference pair differs in %d lines, expected %d: %r"
                  % (stem, len(d), want, [x[0] for x in d]))
    print("  reference OK: TiO2 pair is scf 3 lines / hp 2 lines")


def build(name, src_name, subs, want, write):
    src = W.read(os.path.join(SRC, src_name)).replace("\r\n", "\n")
    new = src
    for old, rep in subs:
        if old not in new:
            W.die("%s: expected %r" % (src_name, old))
        new = new.replace(old, rep, 1)
    d = diff(src, new)
    if len(d) != want:
        W.die("%s: expected exactly %d differing lines, got %d: %r"
              % (name, want, len(d), [x[0] for x in d]))
    for _, before, after in d:
        if ("prefix" in before or "outdir" in before) and \
           ("prefix" in after or "outdir" in after):
            continue
        if before.strip() == CARD_OLD and after.strip() == CARD_NEW:
            continue
        W.die("%s: unexpected differing line %r -> %r" % (name, before, after))
    dst = os.path.join(DST, name)
    if write:
        if not os.path.isdir(DST):
            os.makedirs(DST)
        W.write(dst, new)
    return dst


def main():
    check = "--check" in sys.argv
    print("CrO2 ortho-atomic hp.x builder -- %s" % ("CHECK ONLY" if check else "building"))
    check_reference()

    scf = build(
        "scf__cro2_ortho.in", "scf__cro2.in",
        [("prefix = 'cro2_atomic'", "prefix = 'cro2_ortho'"),
         ("outdir = './tmp_cro2_atomic'", "outdir = './tmp_cro2_ortho'"),
         (CARD_OLD, CARD_NEW)],
        3, not check)
    hp = build(
        "hp__cro2_ortho_q222.in", "hp__cro2_q222.in",
        [("prefix = 'cro2_atomic'", "prefix = 'cro2_ortho'"),
         ("outdir = './tmp_cro2_atomic'", "outdir = './tmp_cro2_ortho'")],
        2, not check)

    print("  2 decks %s" % ("verified" if check else "written"))
    if check:
        return

    lines = [
        "# CrO2 bulk linear-response U under the ORTHO-ATOMIC projector.",
        "# Built by src/dft/build_hp_cro2_ortho.py. Closes the missing cell of",
        "# the {TiO2, CrO2} x {atomic, ortho} grid; the other three are banked",
        "# in runs/hp_tio2 (TiO2 atomic 4.2245/4.2251, TiO2 ortho 5.6688/5.6743,",
        "# CrO2 atomic 6.1635 eV at q222).",
        "#",
        "# A8.8 ISOLATION: outputs land in runs/hp_cro2_ortho/, never in the",
        "# banked runs/hp_tio2/. Run the SCF first, then hp.x against its prefix.",
        "#",
        "# scf  %s  %s" % (md5(scf), "scf__cro2_ortho.in"),
        "# hp   %s  %s" % (md5(hp), "hp__cro2_ortho_q222.in"),
    ]
    W.write(MANIFEST, "\n".join(lines) + "\n")
    print("  manifest -> %s" % W.rel(MANIFEST))


if __name__ == "__main__":
    main()
