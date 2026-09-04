#!/usr/bin/env python
"""P-PROJ-CELL: does the projector still flip the limiting step in the cell we ADOPTED?

WHAT THIS ANSWERS, AND WHY IT IS THE HIGHEST-VALUE COMPUTE ON THE BOARD

A7.1 / P-PROJ is the campaign's flagship, and it is a **1x1** statement: Cr,
U = 7.15 eV, HUBBARD (atomic) 1.155 V / pls 2 against (ortho-atomic) 1.642 V /
pls 1, |d-eta| = 0.487 V. It is correctly labelled 1x1 everywhere.

Two facts about it, both banked and both uncomfortable:

  1. Block 1A ADOPTED the 2x1v cell for production.
  2. In that adopted cell, at the SAME U and the SAME atomic projector, the
     limiting step is ALREADY 1 (eta 0.9240, docs/figs/a0cell_readout.json).
     So the 2 -> 1 flip A7.1 attributes to the projector is also what the CELL
     change produces on its own, at fixed projector.

That does not falsify A7.1 -- a 1x1 statement is true of 1x1. What it means is
that "the projector flips the rate-limiting step" is not yet known to be a
projector-unique signature, and the campaign cannot say whether the effect
survives into the cell it actually runs.

`grep -rl "ortho-atomic" runs/a0/cell/` returns NOTHING. There is no
ortho-atomic calculation anywhere in the production cell. This builder makes
four, and they are the only calculation in this neighbourhood that can
**falsify the headline** rather than measure it more precisely.

WHAT RUNS

Four fixed-geometry SCFs, U = 7.15 eV, 2x1v, HUBBARD (ortho-atomic):

    ref__2x1v__u715_ortho          (bare 2x1v reference)
    s0_O__2x1v_mir__u715_ortho
    s0_OH__2x1v_mir__u715_ortho
    s0_OOH__2x1v_escape__u715_ortho

Geometry, cell, cutoffs, k-mesh (nk = 8), spin convention, smearing, U value and
pseudopotentials are inherited BYTE-IDENTICALLY from the banked
runs/a0/cell/<stem>__u715.in decks, all four of which carry JOB DONE with no
"convergence NOT achieved". The atomic legs are NOT re-run.

THE TRANSFORMATION, and the guard on it

Each ortho deck differs from its source in EXACTLY two lines:

    prefix = '<stem>__u715'   ->   '<stem>__u715_ortho'
    HUBBARD (atomic)          ->   HUBBARD (ortho-atomic)

That is the same discipline as build_pproj.py / build_pproj6.py /
build_hp_cro2_ortho.py, and the banked 1x1 u715 Cr pair in runs/a0/p_proj --
which embodies exactly this transformation and nothing else -- is asserted as
the reference before any deck is cloned. Any third differing line is fatal.

Only converged sources are cloned: a source whose .out does not carry JOB DONE
is refused, because a projector CONTRAST against a state the campaign does not
bank is meaningless.

projwfc.in is NOT written here. anvil/46_a0.slurm generates it at runtime from
the deck's own prefix (A6.5(1)); writing one would create a second source of
truth for the same field.

WHAT IS BLIND AND WHAT IS NOT -- stated here, not discovered later

The ATOMIC leg is fully banked and its value is KNOWN: eta = 0.9239810 V,
pls = 1. This arm is therefore **half non-blind by construction**, and it is
registered as such: only the ortho leg is unmeasured. Amendment 13 records the
atomic value in advance, DISCLOSED NON-BLIND, so that no reader has to wonder
whether it was looked up after the fact. This is the honest form docs/80
prescribed for any arm with a banked half.

COST, measured from the banked atomic partners at np = 128 (not estimated):

    ref 522.67 s + s0_O 381.13 s + s0_OH 472.63 s + s0_OOH 389.41 s
      = 1765.84 s WALL = 62.79 core-hours for the four atomic legs.

    Ortho/atomic ratios on the banked 1x1 pair, all FOUR states aggregated
    (1283.5 s -> 1519.0 s WALL, 1211.9 s -> 1346.9 s CPU):
        WALL 1.1834, CPU 1.1114; per state 1.313 / 1.083 / 1.609 / 0.953.
    So: ~60 SU floor (best observed ratio 0.951), ~70-74 SU central,
    ~101 SU at the worst observed pair ratio. 0.12 % of the 59,753 SU balance.

    ORTHO IS DEARER, NOT CHEAPER, ON SLABS. The hp.x TiO2 result (ortho 0.894-
    0.982 of atomic) does NOT transfer: on pw.x slabs ortho ran longer on three
    of four states, and the 1x1 s0_OH ortho leg needed 49 SCF iterations against
    its atomic partner's 30. electron_maxstep is the only backstop.

    (docs/80 estimated "~30-55 SU" for this arm. That was low -- it is below the
    banked ATOMIC cost of 62.79 core-h. Corrected here rather than quietly
    replaced.)

A8.8 ISOLATION. Output goes to runs/a0/pproj_cell/, NEVER into runs/a0/cell/.
The banked cell tree is read-only by construction.

Usage:
    PYTHONPATH=src python src/dft/build_pproj_cell.py            # build + verify
    PYTHONPATH=src python src/dft/build_pproj_cell.py --check    # verify only
"""

import hashlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402

SRC_DIR = os.path.join(W.ROOT, "runs", "a0", "cell")
DST_DIR = os.path.join(W.ROOT, "runs", "a0", "pproj_cell")
MANIFEST = os.path.join(W.ROOT, "runs", "a0", "m_pproj_cell.txt")

# The four states of the adopted 2x1v cell, at the u715 rung.
STEMS = [
    "ref__2x1v__u715",
    "s0_O__2x1v_mir__u715",
    "s0_OH__2x1v_mir__u715",
    "s0_OOH__2x1v_escape__u715",
]

CARD_OLD = "HUBBARD (atomic)"
CARD_NEW = "HUBBARD (ortho-atomic)"

NK = 8  # runs/a0/cell/manifest.json "nk": 8 -- matches the banked atomic partners

# The banked 1x1 pair that DEFINES the projector transformation.
REF_DIR = os.path.join(W.ROOT, "runs", "a0", "p_proj")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def diff_lines(a, b):
    la, lb = a.split("\n"), b.split("\n")
    if len(la) != len(lb):
        W.die("line count changed: %d -> %d" % (len(la), len(lb)))
    return [(i, x, y) for i, (x, y) in enumerate(zip(la, lb), 1) if x != y]


def check_reference():
    """The banked 1x1 u715 Cr pair is the projector transformation. Assert it."""
    a = os.path.join(REF_DIR, "s0_OH__u715_atomic.in")
    o = os.path.join(REF_DIR, "s0_OH__u715_ortho.in")
    for p in (a, o):
        if not os.path.exists(p):
            W.die("%s: banked reference deck missing" % W.rel(p))
    at = W.read(a).replace("\r\n", "\n")
    ot = W.read(o).replace("\r\n", "\n")
    d = diff_lines(at, ot)
    if len(d) != 2:
        W.die("reference pair differs in %d lines, expected 2: %r"
              % (len(d), [x[0] for x in d]))
    kinds = sorted("prefix" if "prefix" in x else "hubbard" if "HUBBARD" in x else "?"
                   for _, x, _ in d)
    if kinds != ["hubbard", "prefix"]:
        W.die("reference pair changes the wrong lines: %r" % (kinds,))
    print("  reference OK: the banked 1x1 u715 Cr pair is prefix + HUBBARD card, 2 lines")


def source_is_converged(stem):
    out = os.path.join(SRC_DIR, stem + ".out")
    if not os.path.exists(out):
        return False, "no .out"
    txt = W.read(out)
    if "JOB DONE" not in txt:
        return False, "no JOB DONE"
    if re.search(r"convergence NOT achieved", txt):
        return False, "convergence NOT achieved"
    return True, "ok"


def build_one(stem, write):
    src_path = os.path.join(SRC_DIR, stem + ".in")
    if not os.path.exists(src_path):
        W.die("%s: source deck missing" % W.rel(src_path))

    ok, why = source_is_converged(stem)
    if not ok:
        W.die("%s: atomic partner is not banked (%s) -- a projector contrast "
              "against an unbanked state is meaningless" % (stem, why))

    src = W.read(src_path).replace("\r\n", "\n")

    if CARD_OLD not in src:
        W.die("%s: does not carry %r" % (W.rel(src_path), CARD_OLD))
    if CARD_NEW in src:
        W.die("%s: already ortho-atomic" % W.rel(src_path))
    if src.count(CARD_OLD) != 1:
        W.die("%s: %d HUBBARD (atomic) lines, expected exactly 1"
              % (W.rel(src_path), src.count(CARD_OLD)))

    want_prefix_old = "prefix = '%s'" % stem
    if src.count(want_prefix_old) != 1:
        W.die("%s: %d occurrences of %r, expected exactly 1"
              % (W.rel(src_path), src.count(want_prefix_old), want_prefix_old))

    new = src.replace(want_prefix_old, "prefix = '%s_ortho'" % stem, 1)
    new = new.replace(CARD_OLD, CARD_NEW, 1)

    d = diff_lines(src, new)
    if len(d) != 2:
        W.die("%s: expected exactly 2 differing lines, got %d: %r"
              % (stem, len(d), [x[0] for x in d]))
    for _, before, after in d:
        if "prefix" in before and "prefix" in after:
            continue
        if before.strip() == CARD_OLD and after.strip() == CARD_NEW:
            continue
        W.die("%s: unexpected differing line %r -> %r" % (stem, before, after))

    # The U line must be untouched and must be the registered 7.1500 rung.
    mu = re.search(r"^U\s+(\w+)-3d\s+([0-9.]+)\s*$", new, re.M)
    if not mu:
        W.die("%s: no U line found" % stem)
    if abs(float(mu.group(2)) - 7.15) > 1e-9:
        W.die("%s: U is %s, expected 7.1500 -- wrong rung" % (stem, mu.group(2)))
    if mu.group(1) != "Cr":
        W.die("%s: U species is %s, expected Cr" % (stem, mu.group(1)))

    # calculation must be scf: this arm relaxes nothing.
    mc = re.search(r"calculation\s*=\s*'(\w+)'", new)
    if not mc or mc.group(1) != "scf":
        W.die("%s: calculation = %r, expected 'scf' -- this arm relaxes nothing"
              % (stem, mc.group(1) if mc else None))

    dst = os.path.join(DST_DIR, stem + "_ortho.in")
    if write:
        if not os.path.isdir(DST_DIR):
            os.makedirs(DST_DIR)
        W.write(dst, new)
    return dst, mu.group(2)


def main():
    check_only = "--check" in sys.argv
    print("P-PROJ-CELL builder -- %s"
          % ("CHECK ONLY, no files written" if check_only else "building"))
    check_reference()

    rows = []
    for stem in STEMS:
        dst, u = build_one(stem, write=not check_only)
        rows.append((stem, dst, u))

    print("  %d decks %s" % (len(rows), "verified" if check_only else "written"))
    if check_only:
        return

    lines = [
        "# P-PROJ-CELL manifest -- ortho-atomic leg, Cr, U = 7.15 eV, 2x1v.",
        "# Built by src/dft/build_pproj_cell.py. Each deck differs from its",
        "# runs/a0/cell/<stem>.in source in exactly 2 lines: prefix, and",
        "# HUBBARD (atomic) -> (ortho-atomic). Everything else is byte-identical.",
        "#",
        "# WHAT THIS ARM IS. A7.1 is a 1x1 statement. Block 1A adopted 2x1v, and in",
        "# 2x1v the ATOMIC projector already gives pls = 1 (eta 0.9239810,",
        "# docs/figs/a0cell_readout.json), so the 2 -> 1 flip A7.1 reports is also",
        "# what the cell change produces at fixed projector. No ortho-atomic",
        "# calculation exists anywhere in the adopted cell. These four are it.",
        "#",
        "# HALF NON-BLIND BY CONSTRUCTION, disclosed: the atomic leg is banked at",
        "# eta = 0.9239810 V, pls = 1, and that value is written into Amendment 13",
        "# IN ADVANCE. Only the ortho leg is unmeasured.",
        "#",
        "# nk = %d matches runs/a0/cell/manifest.json; NP = 128 is a multiple of it" % NK,
        "# and is the shape the banked atomic partners ran at.",
        "#",
        "# COST, measured not estimated: the four atomic partners cost 1765.84 s WALL",
        "# at np = 128 = 62.79 core-h. Aggregated over all four banked 1x1 states the",
        "# ortho/atomic ratio is 1.1834 WALL / 1.1114 CPU (per state 1.313 / 1.083 /",
        "# 1.609 / 0.953), so ~60 SU floor, ~70-74 SU central, ~101 SU at the worst",
        "# observed pair ratio. Ortho is DEARER than atomic on pw.x slabs; the hp.x",
        "# TiO2 result that ortho runs cheaper does not transfer.",
        "#",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171",
        "#",
        "# md5 of each deck, for the record:",
    ]
    for stem, dst, u in rows:
        lines.append("#   %-28s %s  %s" % (stem + "_ortho", u, md5(dst)))
    lines.append("#")
    lines.append("# Runnable rows are: dir job suffix nk")
    for stem, dst, u in rows:
        lines.append("a0/pproj_cell %s_ortho .in %d" % (stem, NK))
    W.write(MANIFEST, "\n".join(lines) + "\n")
    print("  manifest -> %s" % W.rel(MANIFEST))
    print()
    print("  Submission is gated on Amendment 13 being appended to docs/43 AND")
    print("  deposited (A7.8: every amendment goes to Zenodo before the first act")
    print("  it governs). Then:")
    print("  bash anvil/47_submit_a0.sh $PROJECT/sts/runs/a0/m_pproj_cell.txt 4")


if __name__ == "__main__":
    main()
