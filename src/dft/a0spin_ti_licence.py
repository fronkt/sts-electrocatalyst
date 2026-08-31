#!/usr/bin/env python3
"""The 2026-08-31 Ti licence gate and the licensed-Ti-stem sweep (shared).

SINGLE SOURCE OF TRUTH for three things every A0-SPIN builder that can see
runs/a0/spin/Ti/ must agree on, so the gate and the sweep can never drift
between builders (build_a0spin_s1.py, build_a0spin_s1_ti.py,
build_a0spin_reread.py all import this module):

(1) THE LICENCE GATE. docs/59 must carry the dated line whose literal prefix is

        [§3c LICENCE 2026-08-31: GRANTED

    (the line as executed reads "GRANTED — EXECUTED UNDER DIRECTIVE,
    COUNTERSIGNATURE PENDING; s0_OH@u900 FIRST among Ti compute"; executed
    under the entrant's recorded directive, docs/66 §1 + §2 row 1). The gate
    is a grep for that literal, and the build DIES if it is absent. This
    SUPERSEDES the pre-licence semantics of build_a0spin_s1.py (refuse_ti()
    plus the nulls-only S1-f sweep), which were written while §3c was
    unsigned.

(2) THE LICENSED TI STEM UNIVERSE, exactly 24 + the 2 banked null controls:
      - 12 Stage-1 adsorbate stems: {s0_OH, s0_OOH} x {u000, u900} x
        {m010, m030, m050}  (docs/62:215-216; docs/43 A11.R1 [A11.6
        SEEDS+SELECTION 2026-08-31]; A11.R4 prices them "Ti Stage-1 12")
      - 12 equalised re-read stems: {slab, s0_O} x {u000, u900} x
        {m010, m030, m050}  (docs/43 A11.R3 [A7.2 EQUALISED RE-READ
        2026-08-31: RE-READ], "Ti under the §3c grant (+12 ...,
        docs/62:217-218)")

(3) THE SWEEP. Under runs/a0/spin/Ti/ only the two banked __sp2null controls
    and (once the licence line exists) the 24 licensed stems may exist as
    .in files; ANY OTHER Ti .in still dies. Without the licence line the
    sweep reduces exactly to the old S1-f behaviour (nulls only).

SUBMISSION IS A SEPARATE, HUMAN GATE. Building banks nothing (docs/59 §3c:
"Ti decks may be BUILT and committed under this executed line ... submission
waits"). NO TI DECK SUBMITS before the entrant's own dated confirmation line
([§3c CONFIRMED) exists in docs/59 §5. docs/59 §5 today carries only the
RESERVED example ("[§3c CONFIRMED 2026-__-__ ...]", italicised placeholder),
so this module deliberately makes NO attempt to machine-detect confirmation:
that gate is discharged by the entrant at submit time, by reading docs/59 §5,
and every Ti manifest carries the sentence verbatim.
"""
from __future__ import annotations

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import build_a0spin as B  # SEEDS -- the A11.6 grid, elected AS PROPOSED

DOC59 = os.path.join(ROOT, "docs", "59-a0-roster-correction-2026-08-28.md")

#: The literal the gate greps for (the prefix of the dated line in docs/59 §3c).
LICENCE_PREFIX = "[§3c LICENCE 2026-08-31: GRANTED"

#: The literal the SUBMIT-time human gate looks for in docs/59 §5 (recorded in
#: every Ti manifest; never machine-checked here -- see the docstring).
CONFIRM_PREFIX = "[§3c CONFIRMED"

#: The two banked null-seed controls (Stage 0, committed with .out evidence).
NULL_STEMS = ("slab__u900__sp2null", "s0_OOH__u900__sp2null")


def _stem(state: str, utok: str, seed: float) -> str:
    return "%s__%s__sp2m%03d" % (state, utok, int(round(seed * 100)))


#: 12 Stage-1 adsorbate stems (docs/62:215-216; A11.R1).
TI_S1_STEMS = tuple(_stem(st, u, s)
                    for st in ("s0_OH", "s0_OOH")
                    for u in ("u000", "u900")
                    for s in B.SEEDS)

#: 12 equalised re-read stems (A11.R3 [A7.2 EQUALISED RE-READ], docs/62:217-218).
TI_REREAD_STEMS = tuple(_stem(st, u, s)
                        for st in ("slab", "s0_O")
                        for u in ("u000", "u900")
                        for s in B.SEEDS)

LICENSED_TI_STEMS = TI_S1_STEMS + TI_REREAD_STEMS

# the universe must be exactly 12 + 12, all distinct, disjoint from the nulls
assert len(TI_S1_STEMS) == 12 and len(TI_REREAD_STEMS) == 12
assert len(set(LICENSED_TI_STEMS)) == 24
assert not set(LICENSED_TI_STEMS) & set(NULL_STEMS)


def licence_lines():
    """Every docs/59 line carrying the literal licence prefix (the grep)."""
    txt = io.open(DOC59, encoding="utf-8", newline="").read()
    return [ln for ln in txt.split("\n") if LICENCE_PREFIX in ln]


def require_licence(die):
    """Die unless docs/59 carries the granted licence line exactly once."""
    hits = licence_lines()
    if len(hits) != 1:
        die("docs/59 licence gate FAILED: %d lines carry the literal prefix "
            "'%s' (need exactly 1). No Ti deck may be built without the "
            "executed grant (docs/59 section 3c; docs/66 section 2 row 1)."
            % (len(hits), LICENCE_PREFIX))
    return hits[0]


def ti_sweep(die, ti_dirs):
    """Sweep the given Ti directories: any .in beyond the banked nulls and
    (licence present) the 24 licensed stems dies. Returns licence presence."""
    lic = len(licence_lines()) == 1
    allowed = set(NULL_STEMS) | (set(LICENSED_TI_STEMS) if lic else set())
    for d in sorted(set(ti_dirs)):
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".in"):
                stem = f[:-3]
                if stem not in allowed:
                    die("unexpected Ti deck %s -- not a banked __sp2null "
                        "control and not a 2026-08-31 licensed stem%s"
                        % (os.path.join(d, f),
                           "" if lic else " (docs/59 licence line ABSENT: "
                           "only the null controls may exist)"))
    return lic
