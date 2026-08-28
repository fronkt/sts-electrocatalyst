#!/usr/bin/env python3
"""A0-cell fifth rung: the four U = 7.15 eV decks, built AFTER P-PROJ scored.

A6.1(b) registers five U points for the Cr 2x1v ladder; build_a0cell.py built
the first four and left the fifth gated on A7.1: "Before any A0 deck is built
on the fifth grid point" the projector pairing must run.

P-PROJ SCORED 2026-08-28 (docs/figs/pproj_readout.json, src/dft/pproj_readout.py):
|d-eta(Cr)| = 0.487 V, atomic 1.155 V (pls 2) vs ortho 1.642 V (pls 1), all four
pairs branch-matched. THE PREDICTION FIRES (threshold 0.10 V). Per A7.1,
verbatim: "the fifth grid point is labelled PROJECTOR-MISMATCHED before any
result exists; the whole eta(U) grid runs in ONE projector; the projector delta
becomes its own labelled sub-row."

So these four decks are built in the ladder's own projector -- HUBBARD (atomic),
the same card every other rung and the entire production tier carry -- and every
row they produce is reported under the PROJECTOR-MISMATCHED label: U = 7.15 eV
is Xu 2015's linear-response value, derived under a different projector, and
this campaign has now measured the eta consequence of that mismatch at this U to
be 0.487 V. The label is attached here, before any 2x1v result at this U exists,
exactly as the registration requires.

MECHANICS. Each deck is its state's `__base` deck with exactly two lines
changed: prefix, and `U Cr-3d 3.7000` -> `U Cr-3d 7.1500`. That is asserted
byte-by-byte at build time -- the same discipline build_pproj.py used -- so the
geometry, cell, k-grid, magnetization and everything else provably survive from
the A6.1(b)-mandated tier_v3 set. Naming follows the P-PROJ `u715` convention.

These are FIXED-GEOMETRY SINGLE POINTS. Never to be reported as relaxed.

Usage:  python src/dft/build_a0cell_u715.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CELL = os.path.join(ROOT, "runs", "a0", "cell")

STATES = ("ref__2x1v", "s0_O__2x1v_mir", "s0_OH__2x1v_mir", "s0_OOH__2x1v_escape")
U_OLD, U_NEW = "U Cr-3d 3.7000", "U Cr-3d 7.1500"

MANIFEST_HEADER = """\
# A0-cell fifth rung: the four registered U = 7.15 eV SCFs (20 = 16 + these 4).
# Built 2026-08-28 by src/dft/build_a0cell_u715.py, AFTER P-PROJ scored.
#
# P-PROJ VERDICT (docs/figs/pproj_readout.json): |d-eta(Cr)| = 0.487 V -- FIRES
# (threshold 0.10 V; atomic 1.155 V pls 2, ortho 1.642 V pls 1, all four pairs
# branch-matched). Per A7.1 this rung is labelled PROJECTOR-MISMATCHED: U=7.15
# eV is Xu 2015's linear-response value, derived under a different projector.
# The rung runs in the ladder's own projector, HUBBARD (atomic), so the ladder
# stays single-projector; the 0.487 V delta is its own labelled sub-row and any
# result at this U carries the label in every S6-facing table.
#
# Decks: each state's __base deck with exactly {prefix, U 3.7000->7.1500}
# changed, asserted at build time. Fixed-geometry single points; never to be
# reported as relaxed.
#
# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223
#
# row: dir job suffix nk
# NP=128 NCONC=1
#
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for st in STATES:
        src = os.path.join(CELL, f"{st}__base.in")
        text = open(src, newline="").read()
        assert "\r" not in text, f"{src}: CRLF would corrupt the deck"
        old_prefix = f"prefix = '{st}__base'"
        assert text.count(old_prefix) == 1, f"{src}: prefix line not unique"
        assert text.count(U_OLD) == 1, f"{src}: U line not unique"
        assert "HUBBARD (atomic)" in text, f"{src}: not an atomic-projector deck"

        new = text.replace(old_prefix, f"prefix = '{st}__u715'").replace(U_OLD, U_NEW)

        # the transformation touched exactly the two intended lines
        diffs = [(a, b) for a, b in zip(text.splitlines(), new.splitlines()) if a != b]
        assert len(diffs) == 2, f"{src}: expected exactly 2 changed lines, got {len(diffs)}"
        assert diffs[0] == (f"  {old_prefix}", f"  prefix = '{st}__u715'") or \
               diffs[0][1].strip() == f"prefix = '{st}__u715'", f"{src}: unexpected first diff {diffs[0]}"
        assert diffs[1] == (U_OLD, U_NEW), f"{src}: unexpected second diff {diffs[1]}"

        dst = os.path.join(CELL, f"{st}__u715.in")
        with open(dst, "w", newline="\n") as fh:
            fh.write(new)
        rows.append(f"a0/cell {st}__u715 .in 8")
        print(f"built {os.path.relpath(dst, ROOT)}  (2 lines changed from __base)")

    man = os.path.join(ROOT, "runs", "a0", "m_a0cell_u715.txt")
    with open(man, "w", newline="\n") as fh:
        fh.write(MANIFEST_HEADER)
        fh.write("\n".join(rows) + "\n")
    print(f"wrote {os.path.relpath(man, ROOT)}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
