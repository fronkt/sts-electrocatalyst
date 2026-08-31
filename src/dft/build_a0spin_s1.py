#!/usr/bin/env python3
"""A0-SPIN STAGE 1: the Ru + Ir production seed ladders (20 decks, launch-ready).

STAGE 1 — NOT LICENSED FOR SUBMISSION. docs/61 decisions 1-4 (headline census election, seed set + tolerances, P-SPIN-DELTA thresholds, docs/59 §3c countersignature) are OPEN. Seed set below is the PROPOSED set of docs/61 §A11.6 and is rebuilt trivially if re-authored. Ti is refused by this builder until docs/59 §3c is countersigned.

READ src/dft/build_a0spin.py's docstring first: this builder is its Stage-1
continuation and inherits its registration, its blocker analysis (the
state-dependent species index), and its assertion set unchanged.

WHAT THIS BUILDS
----------------
2 metals (Ru first, then Ir — docs/61 §A11.10 sequencing) x 2 adsorbate
states (s0_OH, s0_OOH) x 2 U endpoints (u000, u900 — A7.3 is span at FIXED
endpoints) x 3 PROPOSED seeds {0.10, 0.30, 0.50}, MINUS the four u000/0.50
rungs Stage 0 already banked as converged, P11-reproducing evidence at
runs/a0/spin/{Ru,Ir}/{s0_OH,s0_OOH}__u000__sp2m050.{in,out} — those are
INHERITED, never rebuilt, and this builder refuses to touch them. Net: 20
new decks under runs/a0/spin/{Ru,Ir}/, all ntyp = 3 with the metal at
starting_magnetization index 2.

NOT buildable here, by registration: slab + s0_O (docs/61 decision item 8),
the Xu anchor rungs u673 (Ru) / u591 (Ir) (docs/61 §A11.2), and every Ti
deck (docs/59 §3c uncountersigned — any Ti request is hard-refused, and a
post-build sweep dies if any non-null Ti deck exists under runs/a0/spin/Ti/).

HOW IT BUILDS, AND WHAT IS FATAL
--------------------------------
Every deck is produced by build_a0spin.build_one (imported, not copied), so
the build-time assertions A1-A10 documented in build_a0spin.py's docstring
are enforced per-deck exactly as in Stage 0. A11 (every parent under
runs/a0/main/ unchanged on disk, md5-swept before and after) and A12 (every
child under runs/a0/spin/, never runs/a0/main/) live inline in
build_a0spin.main() and are replicated inline here. build_a0spin.rederive()
is run first, so every docstring claim of the Stage-0 builder is re-read off
disk before a single Stage-1 deck is written. Stage-1 additions, all fatal:

S1-a  the plan is exactly the registered 20 (10 per metal); any drift dies
S1-b  every deck comes back ntyp = 3 with the metal at index 2 (the Stage-1
      set is adsorbate-only; a 1/3 split here means the plan leaked slab/s0_O)
S1-c  no planned stem collides with banked evidence (a .out under the repo's
      runs/a0/spin/) and nothing at the output paths is ever overwritten
      (46_a0.slurm's stale-.out refusal protects the remote; nothing protects
      a local overwrite of banked evidence except this)
S1-d  the four inherited Stage-0 rungs exist on disk with converged .out
      files (inheritance is verified, not assumed)
S1-e  no child path is written unless it ends runs/a0/spin/<M>/<stem>.in
S1-f  a Ti sweep after the build: only the two banked __sp2null controls may
      exist under runs/a0/spin/Ti/
S1-g  per-deck md5s are recorded in the manifest header; an independent
      rebuild (--sandbox <dir>) must reproduce them byte-for-byte

MANIFEST
--------
runs/a0/m_a0spin_s1.txt, same row grammar as m_a0spin_s0.txt ("dir job
suffix nk", parsed by anvil/46_a0.slurm + anvil/47_submit_a0.sh; '#' lines
are comments; trailing fields are fatal in the submitter). Stage 0 ran as
array 20221409 via  EXCLUDE=a024,a049,a050,a088,a196,a220,a223 bash
anvil/47_submit_a0.sh $PROJECT/sts/runs/a0/m_a0spin_s0.txt 1  and a licensed
Stage 1 would substitute m_a0spin_s1.txt — quoted for the record ONLY;
nothing in this stage may be staged or submitted until the
entrant discharges docs/61 decisions 1-3 (the headline census election of
§A11.5 must be dated and committed BEFORE Stage 1 submits) and docs/62 §5.2
re-registration is authorised before any Stage-1 row is SCORED.

USAGE
-----
    python src/dft/build_a0spin_s1.py                  # build into the repo
    python src/dft/build_a0spin_s1.py --sandbox DIR    # independent rebuild
                                                       # into DIR/runs/... for
                                                       # the determinism check

Any other argument is refused; "Ti" is refused with the docs/59 §3c message.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import build_a0spin as B  # origin of A1-A12: build_one, rederive, read/write/md5
import qe_qc

METALS_S1 = ("Ru", "Ir")          # Ru first, then Ir: docs/61 §A11.10
STATES_S1 = ("s0_OH", "s0_OOH")   # slab + s0_O held: docs/61 decision item 8
UTOKS_S1 = ("u000", "u900")       # fixed A7.3 endpoints; Xu anchors excluded (§A11.2)
SEEDS_S1 = B.SEEDS                # PROPOSED (0.10, 0.30, 0.50): docs/61 §A11.6

#: The verbatim not-licensed notice, extracted from this module's docstring so
#: the manifest header can never drift from it.
_notice_hits = [l for l in __doc__.splitlines() if l.startswith("STAGE 1 ")]
assert len(_notice_hits) == 1, "docstring must carry the notice exactly once"
NOTICE = _notice_hits[0]


def stem_of(state: str, utok: str, seed: float) -> str:
    return "%s__%s__sp2m%03d" % (state, utok, int(round(seed * 100)))


def refuse_ti() -> None:
    B.die("Ti is refused by this builder until docs/59 §3c is countersigned "
          "(docs/61 decision item 4; docs/59 §3c sets the denominator this "
          "arm is scored against and is the entrant's to countersign)")


def inherited(utok: str, seed: float) -> bool:
    """True for the four Stage-0-banked rungs (u000, seed 0.50) -- never rebuilt."""
    return utok == "u000" and abs(seed - 0.50) < 1e-9


def plan_s1():
    plan = []
    for m in METALS_S1:
        for st in STATES_S1:
            for u in UTOKS_S1:
                for s in SEEDS_S1:
                    if inherited(u, s):
                        continue
                    plan.append((m, st, u, s, stem_of(st, u, s)))
    if len(plan) != 20:                                          # S1-a
        B.die("plan drift: %d decks, registered Stage-1 count is 20" % len(plan))
    for m in METALS_S1:
        n = sum(1 for row in plan if row[0] == m)
        if n != 10:
            B.die("plan drift: %d %s decks, expected 10" % (n, m))
    return plan


def main(argv):
    out_root = ROOT
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--sandbox":
            if i + 1 >= len(argv):
                B.die("--sandbox needs a directory")
            out_root = os.path.abspath(argv[i + 1])
            i += 2
            continue
        if a.strip().lower() == "ti":
            refuse_ti()
        B.die("unsupported argument %r -- Stage 1 builds exactly the registered "
              "Ru+Ir 20-deck set; only --sandbox <dir> is accepted" % a)

    B.RY_EV = qe_qc.RY_EV
    out_spin = os.path.join(out_root, "runs", "a0", "spin")
    print("NOT LICENSED FOR SUBMISSION -- see the docstring notice and docs/61.")
    if os.path.normcase(out_root) != os.path.normcase(ROOT):
        print("SANDBOX rebuild into %s (parents/evidence still read from the repo)"
              % out_root)

    # A11 snapshot (origin: build_a0spin.main)
    parents = {}
    for m in B.METALS:
        d = os.path.join(B.MAIN, m)
        for f in sorted(os.listdir(d)):
            if f.endswith(".in"):
                p = os.path.join(d, f)
                parents[p] = B.md5(p)

    B.rederive()

    plan = plan_s1()

    # S1-c -- no planned stem may collide with banked evidence (any .out under
    # the repo spin tree), and nothing at the output paths may be overwritten
    # (.in or .out). 46_a0.slurm's stale-.out refusal protects the remote;
    # locally nothing else protects the bank. A repo .in for a planned stem is
    # tolerated ONLY in a --sandbox rebuild, where it is this builder's own
    # pass-1 product and the determinism compare is the point.
    for m, st, u, s, stem in plan:
        p = os.path.join(B.SPIN, m, stem + ".out")
        if os.path.exists(p):
            B.die("stem %s collides with banked evidence %s" % (stem, p))
        for ext in (".in", ".out"):
            c = os.path.join(out_spin, m, stem + ext)
            if os.path.exists(c):
                B.die("refusing to overwrite existing child %s" % c)

    # S1-d -- the four inherited rungs must actually be banked and converged
    for m in METALS_S1:
        for st in STATES_S1:
            stem = stem_of(st, "u000", 0.50)
            pin = os.path.join(B.SPIN, m, stem + ".in")
            pout = os.path.join(B.SPIN, m, stem + ".out")
            if not os.path.exists(pin):
                B.die("inherited Stage-0 deck missing: %s" % pin)
            if B.energy_ry(pout) is None:
                B.die("inherited Stage-0 run missing or unconverged: %s" % pout)
    print("  S1-d 4 inherited Stage-0 rungs present and converged")

    rows, deck_md5s, built = [], [], 0
    print("\nSTAGE 1 -- Ru + Ir production seed ladders (20 decks)")
    for m, st, u, s, stem in plan:
        if m == "Ti":
            refuse_ti()
        txt, idx, nt = B.build_one(m, st, u, s, stem)     # A1-A10 enforced inside
        if (idx, nt) != (2, 3):                           # S1-b
            B.die("%s %s %s: index %s ntyp %s, Stage 1 is adsorbate-only "
                  "(metal at 2 of 3)" % (m, st, stem, idx, nt))
        child = os.path.join(out_spin, m, stem + ".in")
        if not child.replace("\\", "/").endswith(
                "runs/a0/spin/%s/%s.in" % (m, stem)):     # S1-e / A12
            B.die("child outside runs/a0/spin: %s" % child)
        B.write(child, txt)
        rel = "a0/spin/%s/%s.in" % (m, stem)
        deck_md5s.append((rel, B.md5(child)))
        rows.append(("a0/spin/%s" % m, stem, B.NK[m]))
        built += 1
        print("  %-3s %-7s %s ntyp=%d index=%d  %s" % (m, st, u, nt, idx, stem))

    # A11 -- the banked tree is read-only by construction (origin: build_a0spin.main)
    for p, h in parents.items():
        if B.md5(p) != h:
            B.die("PARENT ALTERED: %s" % p)
    print("\n  A11 all %d parent decks unchanged on disk" % len(parents))

    # A12 -- sibling tree only (origin: build_a0spin.main)
    for d, stem, _nk in rows:
        if not d.startswith("a0/spin/"):
            B.die("child outside runs/a0/spin: %s" % d)
    print("  A12 all %d children under runs/a0/spin/" % built)

    # S1-f -- Ti sweep: only the two banked null controls may exist
    for tidir in {os.path.join(B.SPIN, "Ti"), os.path.join(out_spin, "Ti")}:
        if not os.path.isdir(tidir):
            continue
        for f in sorted(os.listdir(tidir)):
            if f.endswith(".in") and not f[:-3].endswith("__sp2null"):
                B.die("non-null Ti deck exists: %s (docs/59 §3c is not "
                      "countersigned)" % os.path.join(tidir, f))
    print("  S1-f Ti sweep clean: no Ti deck beyond the 2 banked __sp2null controls")

    man = os.path.join(out_root, "runs", "a0", "m_a0spin_s1.txt")
    hdr = [
        "# A0-SPIN STAGE 1 -- Ru + Ir production seed ladders (20 decks). Built",
        "# 2026-08-31 by src/dft/build_a0spin_s1.py -- READ ITS DOCSTRING, the",
        "# build_a0spin.py docstring (assertions A1-A12), and docs/61 (Amendment 11).",
        "#",
        "# " + NOTICE,
        "#",
        "# 10 Ru rows then 10 Ir rows (docs/61 §A11.10 Ru-first sequencing).",
        "# States s0_OH/s0_OOH only -- slab + s0_O are held (docs/61 decision item 8).",
        "# U endpoints u000/u900 only -- the Xu anchor rungs u673 (Ru) / u591 (Ir)",
        "# are registered-excluded (docs/61 §A11.2).",
        "# Ti is ABSENT pending the docs/59 §3c countersignature (docs/61 decision 4).",
        "# The 4 u000-seed-0.50 rungs are INHERITED FROM STAGE 0, banked at",
        "# runs/a0/spin/{Ru,Ir}/{s0_OH,s0_OOH}__u000__sp2m050.{in,out} -- not rebuilt",
        "# and not rows here.",
        "#",
        "# deck md5s (an independent rebuild must reproduce these byte-for-byte):",
    ] + ["# md5 %s %s" % (h, rel) for rel, h in deck_md5s] + [
        "#",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223",
        "#",
        "# row: dir job suffix nk",
        "# NP=128 NCONC=1",
    ]
    if sum(1 for l in hdr if l == "# NP=128 NCONC=1") != 1:
        B.die("manifest must carry exactly one '# NP=128 NCONC=1' line")
    body = ["%s %s .in %d" % (d, s_, nk) for d, s_, nk in rows]
    B.write(man, "\n".join(hdr + body) + "\n")
    print("  wrote %s (%d rows)" % (os.path.relpath(man, out_root), len(rows)))
    print("\nBUILD OK -- %d decks, 0 relaxations, 0 parents touched. "
          "NOT LICENSED FOR SUBMISSION." % built)


if __name__ == "__main__":
    main(sys.argv[1:])
