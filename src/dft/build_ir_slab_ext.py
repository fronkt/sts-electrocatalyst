#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IR-SLAB CONTINGENCY stage A -- the pre-named extension seed 0.05.

Registration: docs/43 A11.R3 [IR-SLAB CONTINGENCY 2026-08-31: EXTENDED-SEEDS(0.05)
THEN EQUALISED-BY-SELECTION(nspin=1)] and A11.R1 [A11.6 SEEDS+SELECTION] Rider 1
("extension seed 0.05 is pre-named NOW, for the Ir-slab contingency only ... it is
not a member of S for any other cell"). Built 2026-09-01 after the A11 wave-1 drain
(docs/68).

X-a  TRIGGER RE-DERIVED FROM DISK, NEVER ASSUMED. A cell (Ir, slab, U) fires iff EVERY
     grid seed {0.10, 0.30, 0.50} landed ABOVE the banked nspin = 1 energy
     (runs/a0/main/Ir/slab__<U>.out; the 0.50 rung at u000 is the Stage-0 banked
     REJECT). Measured 2026-09-01: u000 +0.590 / +0.597 / +0.583 meV -> FIRES;
     u900 -15.14 / -15.15 / +2835 meV -> two admitted seeds -> does NOT fire, and by
     Rider 1 the 0.05 seed is not a member of S there, so NO u900 deck is built. The
     registration's "u000 + u900 = 2 SCFs" is read as the worst-case count; the
     trigger sentence is per (Ir, slab, U) cell. This builder DIES if the disk
     disagrees with either verdict.
X-b  The deck is build_a0spin.build_one (assertions A1-A10 unchanged): parent
     runs/a0/main/Ir/slab__u000.in, stem slab__u000__sp2m005, exactly one nonzero
     seed on Ir's own species index, prefix = stem, nothing else changed.
X-c  Census acceptance proven before the manifest is written: the census's own
     check_candidate_deck (CEN-d, incl. its Rider-1 'Ir slab only' rule) passes on
     the written deck.
X-d  Refuses to overwrite an existing deck or collide with banked evidence.
X-e  Manifest runs/a0/m_ir_slab_ext005.txt: EXCLUDE header (the standing list plus
     a171, the node that killed or hung every task placed on it on 2026-08-31),
     NP=128, nk 4 (the banked Ir convention).
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_a0spin as B          # noqa: E402
import a0spin_census as ac        # noqa: E402

METAL, STATE = "Ir", "slab"
EXT = 0.05
GRID = (0.10, 0.30, 0.50)
RY_MEV = 13605.693123
EXCLUDE = "a024,a049,a050,a088,a196,a220,a223,a171"


def stem(utok, seed):
    return "%s__%s__sp2m%03d" % (STATE, utok, int(round(seed * 100)))


def de_mev(utok, seed):
    inc = B.energy_ry(os.path.join(B.MAIN, METAL, "%s__%s.out" % (STATE, utok)))
    if inc is None:
        B.die("banked nspin=1 floor missing: Ir slab %s" % utok)
    p = os.path.join(B.SPIN, METAL, stem(utok, seed) + ".out")
    e = B.energy_ry(p)
    if e is None:
        B.die("grid seed not terminal/converged on disk: %s" % p)
    return (e - inc) * RY_MEV


def fires(utok):
    des = [de_mev(utok, s) for s in GRID]
    verdict = all(d > 0.0 for d in des)
    print("  X-a %s: dE vs floor = %s meV -> %s"
          % (utok, ", ".join("%+.3f" % d for d in des),
             "FIRES" if verdict else "does not fire"))
    return verdict


def main(argv):
    if argv:
        B.die("this builder takes no arguments")
    print("IR-SLAB CONTINGENCY stage A builder (docs/43 A11.R3; A11.R1 Rider 1)")
    if not fires("u000"):
        B.die("u000 did not fire -- the contingency is not open; nothing to build")
    if fires("u900"):
        B.die("u900 ALSO fires -- this builder was written for the measured "
              "u000-only case; re-derive before extending it")
    st = stem("u000", EXT)
    out_in = os.path.join(B.SPIN, METAL, st + ".in")
    if os.path.exists(out_in) or os.path.exists(out_in[:-3] + ".out"):
        B.die("X-d refusing to overwrite %s" % out_in)
    ctxt, idx, nt = B.build_one(METAL, STATE, "u000", EXT, st)
    if "starting_magnetization(%d) = 0.05" % idx not in ctxt:
        B.die("seed line not found on Ir's index %d" % idx)
    B.write(out_in, ctxt)
    chk = ac.check_candidate_deck(METAL, out_in, st)     # X-c (dies on failure)
    if abs(chk["stem_parse"]["seed"] - EXT) > 1e-9:
        B.die("census parsed seed %r" % chk["stem_parse"]["seed"])
    md5 = hashlib.md5(open(out_in, "rb").read()).hexdigest()
    print("  X-b/X-c built %s (ntyp %d, Ir index %d) md5 %s -- census CEN-d PASS"
          % (os.path.relpath(out_in, B.ROOT), nt, idx, md5))
    man = os.path.join(B.ROOT, "runs", "a0", "m_ir_slab_ext005.txt")
    if os.path.exists(man):
        B.die("X-d refusing to overwrite %s" % man)
    lines = [
        "# IR-SLAB CONTINGENCY stage A -- the pre-named extension seed 0.05, u000 cell",
        "# only (1 deck). Built 2026-09-01 by src/dft/build_ir_slab_ext.py -- READ ITS",
        "# DOCSTRING (X-a..X-e), docs/43 A11.R3 [IR-SLAB CONTINGENCY 2026-08-31] and",
        "# A11.R1 [A11.6 SEEDS+SELECTION] Rider 1, and docs/68 (the wave-1 drain).",
        "#",
        "# TRIGGER (re-derived from disk by the builder): every grid seed at (Ir, slab,",
        "# u000) landed ABOVE the banked nspin=1 energy -1589.74822617 Ry --",
        "# 0.10 +0.590 meV, 0.30 +0.597 meV, 0.50 +0.583 meV (Stage-0 banked REJECT) --",
        "# so stage A runs the pre-named 0.05 seed. (Ir, slab, u900) did NOT fire",
        "# (0.10 -15.14 meV and 0.30 -15.15 meV are admitted; 0.50 +2835 meV rejected),",
        "# and Rider 1 keeps 0.05 out of S there: no u900 deck. If this deck also lands",
        "# above the floor, the cell resolves EQUALISED-BY-SELECTION(nspin=1) with the",
        "# full rejection record; the census (src/dft/a0spin_census.py) applies that",
        "# rule itself.",
        "#",
        "# LICENCE: docs/43 A11.R3 [IR-SLAB CONTINGENCY 2026-08-31] (pre-named, counted",
        "# in the 2-SCF worst case); A11.R5 deposit published (10.5281/zenodo.22213117).",
        "#",
        "# deck md5 (an independent rebuild must reproduce it byte-for-byte):",
        "# md5 %s a0/spin/Ir/%s.in" % (md5, st),
        "#",
        "# SUBMIT WITH EXCLUDE=%s" % EXCLUDE,
        "# (submit-time list additionally + a120,a200 per docs/66 section 4)",
        "#",
        "# row: dir job suffix nk",
        "# NP=128 NCONC=1",
        "a0/spin/Ir %s .in %d" % (st, B.NK[METAL]),
    ]
    B.write(man, "\n".join(lines) + "\n")
    print("  X-e wrote %s" % os.path.relpath(man, B.ROOT))
    print("BUILD OK -- 1 deck, 1 manifest; NOTHING submitted.")


if __name__ == "__main__":
    main(sys.argv[1:])
