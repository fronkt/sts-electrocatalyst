#!/usr/bin/env python3
"""A0-SPIN STAGE 1: the Ru + Ir production seed ladders (20 decks, launch-ready).

STAGE 1 — LICENSED 2026-08-31. docs/61 decisions 1-4 are ELECTED: [A11.5 HEADLINE
CENSUS: AS-BUILT 3-of-6], [A11.6 SEEDS+SELECTION: AS PROPOSED + riders], [A11.3
THRESHOLD: 0.026; FALSIFICATION 0.005], [docs/59 §3c LICENCE: GRANTED-EXECUTED,
confirmation pending] — docs/43 AMENDMENT 11 (A11.R1) + docs/59 §3c + docs/66 §2.
Submission gated on the A11.R5 deposit (licence) and the docs/66 §4 pipeline
guards + EXCLUDE list (operational). Ti rows are built separately after the §3c
line (Ti manifest owed; tasks/todo.md) and submit only after the entrant's
docs/59 §5 confirmation line.

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

NOT buildable here, by registration: slab + s0_O (docs/61 decision item 8;
the licensed slab/s0_O ladders are build_a0spin_reread.py's, per docs/43
A11.R3), the Xu anchor rungs u673 (Ru) / u591 (Ir) (docs/61 §A11.2), and
every Ti deck — Ti Stage-1 is build_a0spin_s1_ti.py's under the docs/59 §3c
line of 2026-08-31; any Ti request here is still hard-refused, and the
post-build sweep dies on any Ti file beyond the banked null controls and the
2026-08-31 licensed stems (a0spin_ti_licence, the shared gate + sweep).

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
S1-f  a Ti sweep after the build — SUPERSEDED 2026-08-31: docs/59 §3c is
      granted-executed, so the sweep (now a0spin_ti_licence.ti_sweep) passes
      the two banked __sp2null controls PLUS the 24 licensed Ti stems, and
      any OTHER Ti .in still dies; absent the docs/59 licence line it
      reduces exactly to the original nulls-only refusal
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
import a0spin_ti_licence as TL  # 2026-08-31: the shared Ti gate + sweep (S1-f)
import qe_qc

METALS_S1 = ("Ru", "Ir")          # Ru first, then Ir: docs/61 §A11.10
STATES_S1 = ("s0_OH", "s0_OOH")   # slab + s0_O held: docs/61 decision item 8
UTOKS_S1 = ("u000", "u900")       # fixed A7.3 endpoints; Xu anchors excluded (§A11.2)
SEEDS_S1 = B.SEEDS                # PROPOSED (0.10, 0.30, 0.50): docs/61 §A11.6

#: The verbatim licence notice, extracted from this module's docstring so the
#: manifest header can never drift from it: the block from the "STAGE 1 " line
#: to the next blank line. Commit 6fe167b amended the BANKED manifest's notice
#: to the licensed text (so the docs/66 §4 'NOT LICENSED' pipeline guard does
#: not refuse wave A); this docstring carries the same bytes, so a --sandbox
#: rebuild reproduces the banked manifest byte-for-byte (decks AND header).
_dl = __doc__.splitlines()
_starts = [i for i, l in enumerate(_dl) if l.startswith("STAGE 1 ")]
assert len(_starts) == 1, "docstring must carry the notice exactly once"
_end = _starts[0]
while _end < len(_dl) and _dl[_end].strip():
    _end += 1
NOTICE_LINES = tuple(_dl[_starts[0]:_end])


def stem_of(state: str, utok: str, seed: float) -> str:
    return "%s__%s__sp2m%03d" % (state, utok, int(round(seed * 100)))


def refuse_ti() -> None:
    B.die("Ti is not this builder's to build: the licensed Ti Stage-1 decks "
          "are build_a0spin_s1_ti.py's, under the docs/59 section-3c line of "
          "2026-08-31 (grant executed, countersignature pending; NO Ti deck "
          "submits before the entrant's confirmation line in docs/59 section 5)")


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
    print("LICENSED 2026-08-31 (docs/43 A11.R1; docs/66 section 2) -- "
          "submission gated on the A11.R5 deposit and the docs/66 section-4 "
          "pipeline guards; see the docstring notice.")
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

    # S1-f -- Ti sweep, SUPERSEDED 2026-08-31 (docs/59 §3c granted-executed):
    # the shared sweep passes the 2 banked null controls plus the 24 licensed
    # Ti stems (a0spin_ti_licence); any OTHER Ti .in still dies, and absent
    # the docs/59 licence line it reduces to the original nulls-only refusal.
    lic = TL.ti_sweep(B.die, {os.path.join(B.SPIN, "Ti"),
                              os.path.join(out_spin, "Ti")})
    print("  S1-f Ti sweep clean: banked __sp2null controls%s only"
          % (" + 2026-08-31 licensed stems" if lic else ""))

    man = os.path.join(out_root, "runs", "a0", "m_a0spin_s1.txt")
    hdr = [
        "# A0-SPIN STAGE 1 -- Ru + Ir production seed ladders (20 decks). Built",
        "# 2026-08-31 by src/dft/build_a0spin_s1.py -- READ ITS DOCSTRING, the",
        "# build_a0spin.py docstring (assertions A1-A12), and docs/61 (Amendment 11).",
        "#",
    ] + ["# " + l for l in NOTICE_LINES] + [
        "#",
        "# 10 Ru rows then 10 Ir rows (docs/61 §A11.10 Ru-first sequencing).",
        "# States s0_OH/s0_OOH only -- slab + s0_O are held (docs/61 decision item 8).",
        "# U endpoints u000/u900 only -- the Xu anchor rungs u673 (Ru) / u591 (Ir)",
        "# are registered-excluded (docs/61 §A11.2).",
        "# Ti is ABSENT from this manifest by design -- the 12 Ti Stage-1 rows take their own",
        "# manifest under the docs/59 §3c licence (GRANTED-EXECUTED 2026-08-31, confirmation pending).",
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
    txt_man = "\n".join(hdr + body) + "\n"
    if "not licensed" in txt_man.lower():
        B.die("manifest text matches the docs/66 §4 'NOT LICENSED' refusal")
    B.write(man, txt_man)
    print("  wrote %s (%d rows)" % (os.path.relpath(man, out_root), len(rows)))
    print("\nBUILD OK -- %d decks, 0 relaxations, 0 parents touched. "
          "Submission gated on the A11.R5 deposit and the docs/66 section-4 "
          "pipeline guards." % built)


if __name__ == "__main__":
    main(sys.argv[1:])
