#!/usr/bin/env python3
"""A0-SPIN STAGE 1, TI ARM: the 12 licensed Ti production seed-ladder decks.

LICENSED-EXECUTED 2026-08-31 -- docs/43 AMENDMENT 11 section A11.R1 (the
elections: [A11.5 HEADLINE CENSUS], [A11.6 SEEDS+SELECTION ... with two dated
riders], [A11.3 THRESHOLD 0.026 eV; FALSIFICATION 0.005 eV]; A11.R4 prices
this family "Ti Stage-1 12") under the docs/59 §3c dated line
[§3c LICENCE 2026-08-31: GRANTED — EXECUTED UNDER DIRECTIVE, COUNTERSIGNATURE
PENDING; s0_OH@u900 FIRST among Ti compute]. Enumeration source docs/62:215-216:
"s0_OH and s0_OOH at u000 and u900 = 4 decks x 3 seeds {0.10, 0.30, 0.50} =
12 SCFs, plus the banked nspin = 1 energies as the variational floor."

BUILDING BANKS NOTHING; SUBMISSION IS DOUBLY GATED. docs/59 §3c: "Ti decks
may be BUILT and committed under this executed line (building banks nothing);
submission waits." This family SUBMITS ONLY AFTER the entrant confirmation
line ([§3c CONFIRMED) exists in docs/59 §5, and after the A11.R5 deposit.
The manifest carries both sentences; the pipeline guards (docs/66 §4) enforce
the EXCLUDE list; the confirmation gate is the entrant's, discharged by
reading docs/59 §5 at submit time (its reserved example line is a placeholder,
deliberately not machine-detected -- see a0spin_ti_licence's docstring).

THE GATE THAT REPLACED refuse_ti(). The old build_a0spin_s1.refuse_ti() and
its nulls-only S1-f sweep were written while §3c was unsigned and are
SUPERSEDED 2026-08-31: the licence gate is now a grep of docs/59 for the
literal line prefix [§3c LICENCE 2026-08-31: GRANTED (a0spin_ti_licence.
require_licence -- this build DIES if the line is absent), and the shared
sweep (a0spin_ti_licence.ti_sweep) passes exactly the 2 banked __sp2null
controls + the 24 licensed Ti stems while any OTHER Ti .in still dies.

READ src/dft/build_a0spin.py's docstring first: this builder is the Ti half
of Stage 1 and reuses build_a0spin_s1's machinery (stem grammar, S1-c/S1-e
semantics) and build_a0spin.build_one (assertions A1-A10 per deck), so every
species index is read from EACH PARENT DECK'S OWN ATOMIC_SPECIES block, never
from a constant (docs/61 §A11.8 item 2: the index is STATE-dependent --
s0_OH/s0_OOH put the metal at 2 of 3; a constant seeds oxygen).

WHAT THIS BUILDS
----------------
1 metal (Ti) x 2 adsorbate states (s0_OH, s0_OOH) x 2 U endpoints (u000,
u900 -- A7.3 is span at FIXED endpoints) x 3 seeds {0.10, 0.30, 0.50} = 12
decks under runs/a0/spin/Ti/, all ntyp = 3 with the metal at
starting_magnetization index 2. No rung is inherited: Stage 0 banked no
seeded Ti deck (its two Ti rows are the __sp2null controls, untouched here).
Parents: the banked nspin = 1 decks runs/a0/main/Ti/{s0_OH,s0_OOH}__{u000,
u900}.in, transformed by the same INSERT Stage 1 used (prefix line + nspin=2
+ starting_magnetization block at the deck-derived metal index).

SELECTION (A11.6, elected AS PROPOSED with two dated riders): lowest
converged total energy per (state, U) across the three seeds AND the banked
nspin = 1 energy as hard variational floor ("must be <= 0" -- equality
passes; no additional tolerance), ties within 1 meV to the smallest |seed|;
both magnetizations reported. RIDER 2 (registered): at (s0_OOH, u900) the
banked null-seed row -1298.17043625 Ry (totmag 1.04, runs/a0/spin/Ti/
s0_OOH__u900__sp2null.out) is NAMED into the candidate pool as the free
fifth candidate -- the rule is lowest-converged-energy regardless of pool,
so a known lower converged solution can only lower, never raise, the
selected minimum. This builder re-derives that row off disk (T-e).

BUILD-TIME ASSERTIONS (all fatal)
---------------------------------
T-a  the licence gate: docs/59 carries the literal [§3c LICENCE 2026-08-31:
     GRANTED line exactly once (a0spin_ti_licence.require_licence)
T-b  the plan is exactly the registered 12 (docs/62:215-216) and equals the
     shared TI_S1_STEMS universe byte-for-byte; any drift dies
T-c  no planned stem collides with banked evidence (a .out under the repo's
     runs/a0/spin/) and nothing at the output paths is ever overwritten; a
     repo .in for a planned stem is tolerated ONLY in a --sandbox rebuild
     (S1-c semantics, verbatim)
T-d  every parent .out is present and converged -- the four banked nspin = 1
     rows ARE the selection rule's variational floor, so the floor must
     exist before a candidate is built
T-e  the rider-2 fifth candidate re-derived off disk: the banked null row
     equals -1298.17043625 Ry to 1e-6 Ry at totmag 1.04, sits BELOW its
     nspin = 1 parent (the spin-unstable 153.07 meV of docs/62 §5.2,
     re-derived within 152.9-153.3), and its stem stays outside this plan
T-f  every deck comes back ntyp = 3 with the metal at index 2, the index
     read from that parent's own ATOMIC_SPECIES (A1 inside build_one)
T-g  every child path ends runs/a0/spin/Ti/<stem>.in; nothing is written
     anywhere else (S1-e semantics)
T-h  nk = 8 re-derived: every banked a0/main/Ti and a0/spin/Ti manifest row
     across runs/a0/m_*.txt carries nk 8 (>= 1 row required), and it equals
     build_a0spin.NK["Ti"]. FLAGGED DEVIATION, never silent: the build
     directive's manifest note said "nk 4"; every banked Ti row carries 8,
     and this builder follows the banked convention, stated here and in the
     report rather than absorbed
T-i  every parent .in under runs/a0/main/ (all six metals) and EVERY
     pre-existing file under runs/a0/spin/ md5-unchanged after the build --
     the 2 banked Ti null controls and the 20 committed Ru/Ir Stage-1 decks
     stay byte-identical (the A11/CMF-j sweep, widened to the whole bank)
T-j  the shared Ti sweep after the build: nulls + the 24 licensed stems
     only; any OTHER Ti .in dies (a0spin_ti_licence.ti_sweep)
T-k  the manifest's first three rows are the s0_OH__u900 seeds -- submission
     order = row order, and docs/59 §3c registers "s0_OH@u900 FIRST among Ti
     compute" (docs/62 §9 item 3; a Ti-internal ordering) -- and the header
     carries the SUBMITS-ONLY-AFTER sentence, the EXCLUDE lines, exactly one
     '# NP=128 NCONC=1', 4-field rows, and no 'NOT LICENSED' match (the
     docs/66 §4 guard would refuse it)
T-l  per-deck md5s recorded in the manifest header; an independent rebuild
     (--sandbox <dir>) must reproduce them byte-for-byte

MANIFEST
--------
runs/a0/m_a0spin_s1_ti.txt, same row grammar as m_a0spin_s1.txt ("dir job
suffix nk", parsed by anvil/46_a0.slurm + anvil/47_submit_a0.sh; '#' lines
are comments; trailing fields are fatal in the submitter). nk 8 (the banked
Ti convention, T-h). Row order: s0_OH__u900 first (docs/59 §3c), then
s0_OH__u000, s0_OOH__u000, s0_OOH__u900, seeds ascending within each cell.

USAGE
-----
    python src/dft/build_a0spin_s1_ti.py                  # build into the repo
    python src/dft/build_a0spin_s1_ti.py --sandbox DIR    # independent rebuild
                                                          # into DIR/runs/... for
                                                          # the determinism check

Any other argument is refused.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import build_a0spin as B          # A1-A10 build_one, read/write/md5/die, NK
import build_a0spin_s1 as S1      # stem grammar + S1-c/S1-e semantics reused
import a0spin_ti_licence as TL    # the shared licence gate + Ti sweep
import qe_qc

STATES_TI = ("s0_OH", "s0_OOH")   # c_M needs only these (docs/62:215-216)
UTOKS_TI = ("u000", "u900")       # fixed A7.3 endpoints
SEEDS_TI = B.SEEDS                # (0.10, 0.30, 0.50) -- A11.6, AS PROPOSED

#: Registered rider-2 literals (docs/43 A11.R1 [A11.6] rider 2; docs/62:220-222).
#: NEVER trusted bare: T-e re-derives each off the banked .out.
RIDER2_STATE, RIDER2_UTOK = "s0_OOH", "u900"
RIDER2_E_RY = -1298.17043625
RIDER2_TOTMAG = 1.04
RIDER2_BREAK_MEV = (152.9, 153.3)   # docs/62 §5.2's ">= 153.07 meV", banded

#: Manifest row order (T-k): s0_OH@u900 FIRST among Ti compute (docs/59 §3c).
CELL_ORDER = (("s0_OH", "u900"), ("s0_OH", "u000"),
              ("s0_OOH", "u000"), ("s0_OOH", "u900"))

#: The submit-gate sentence every Ti manifest carries verbatim (docs/66's
#: audit finding; docs/59 §5).
SUBMIT_GATE = ("SUBMITS ONLY AFTER the entrant confirmation line "
               "([§3c CONFIRMED) exists in docs/59 §5")


def rederive_nk_ti() -> int:
    """T-h: nk 8 licensed by the banked Ti manifest rows, not by a constant."""
    seen = 0
    mandir = os.path.join(ROOT, "runs", "a0")
    for f in sorted(os.listdir(mandir)):
        if not (f.startswith("m_") and f.endswith(".txt")):
            continue
        for ln in B.read(os.path.join(mandir, f)).split("\n"):
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if parts[0] in ("a0/main/Ti", "a0/spin/Ti"):
                if len(parts) < 4 or parts[3] != "8":
                    B.die("banked manifest %s row %r contradicts the Ti nk=8 "
                          "convention" % (f, s))
                seen += 1
    if seen == 0:
        B.die("no banked a0/{main,spin}/Ti manifest row found -- cannot "
              "license nk")
    if B.NK["Ti"] != 8:
        B.die("build_a0spin.NK['Ti'] = %r contradicts the banked nk 8"
              % (B.NK["Ti"],))
    print("  T-h nk=8 re-derived from %d banked Ti rows (deviation from the "
          "directive's 'nk 4' note: FLAGGED, banked convention followed)" % seen)
    return 8


def plan_ti():
    """T-b: the registered 12, in manifest order, equal to TL.TI_S1_STEMS."""
    plan = []
    for st, u in CELL_ORDER:
        for s in SEEDS_TI:
            plan.append((st, u, s, S1.stem_of(st, u, s)))
    if len(plan) != 12:
        B.die("plan drift: %d decks, registered Ti Stage-1 count is 12 "
              "(docs/62:215-216)" % len(plan))
    if sorted(r[3] for r in plan) != sorted(TL.TI_S1_STEMS):
        B.die("plan drift: stems disagree with the shared licensed universe "
              "(a0spin_ti_licence.TI_S1_STEMS)")
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
        B.die("unsupported argument %r -- this builder builds exactly the "
              "registered 12-deck Ti Stage-1 set; only --sandbox <dir> is "
              "accepted" % a)

    B.RY_EV = qe_qc.RY_EV
    out_spin = os.path.join(out_root, "runs", "a0", "spin")
    print("LICENSED-EXECUTED 2026-08-31 (docs/43 A11.R1 + docs/59 section 3c). "
          "Building banks nothing; %s." % SUBMIT_GATE.replace("§", "section "))
    if os.path.normcase(out_root) != os.path.normcase(ROOT):
        print("SANDBOX rebuild into %s (parents/evidence still read from the repo)"
              % out_root)

    # T-a -- the licence gate (dies if the docs/59 line is absent)
    lic_line = TL.require_licence(B.die)
    print("  T-a docs/59 licence line present: %s..." % lic_line[:60])

    # T-i snapshot: every parent .in under runs/a0/main/ (all six metals) and
    # EVERY pre-existing file under runs/a0/spin/ (the whole bank: the 2 null
    # controls, the 20 committed Stage-1 decks, every banked .out, the CMF
    # siblings -- byte-identity asserted after the build)
    parents = {}
    for d in sorted(os.listdir(B.MAIN)):
        dd = os.path.join(B.MAIN, d)
        if not os.path.isdir(dd):
            continue
        for f in sorted(os.listdir(dd)):
            if f.endswith(".in"):
                p = os.path.join(dd, f)
                parents[p] = B.md5(p)
    bank = {}
    for dp, _dn, fns in os.walk(B.SPIN):
        for f in fns:
            p = os.path.join(dp, f)
            bank[p] = B.md5(p)

    B.rederive()

    plan = plan_ti()

    # T-c -- collisions and overwrites (S1-c semantics, verbatim)
    for st, u, s, stem in plan:
        p = os.path.join(B.SPIN, "Ti", stem + ".out")
        if os.path.exists(p):
            B.die("stem %s collides with banked evidence %s" % (stem, p))
        for ext in (".in", ".out"):
            c = os.path.join(out_spin, "Ti", stem + ext)
            if os.path.exists(c):
                B.die("refusing to overwrite existing child %s" % c)

    # T-d -- the variational floor exists: every parent .out converged
    floors = {}
    for st in STATES_TI:
        for u in UTOKS_TI:
            pout = os.path.join(B.MAIN, "Ti", "%s__%s.out" % (st, u))
            e = B.energy_ry(pout)
            if e is None:
                B.die("selection floor missing: %s has no converged energy "
                      "(the banked nspin=1 row IS the A11.6 hard floor)" % pout)
            floors[(st, u)] = e
            print("  T-d floor Ti %-6s %s  %.8f Ry (banked nspin=1)" % (st, u, e))

    # T-e -- rider 2's fifth candidate, re-derived off disk
    nullout = os.path.join(B.SPIN, "Ti",
                           "%s__%s__sp2null.out" % (RIDER2_STATE, RIDER2_UTOK))
    e_null = B.energy_ry(nullout)
    if e_null is None:
        B.die("rider-2 candidate missing or unconverged: %s" % nullout)
    if abs(e_null - RIDER2_E_RY) > 1e-6:
        B.die("rider-2 candidate %.8f != registered %.8f Ry (A11.6 rider 2)"
              % (e_null, RIDER2_E_RY))
    import io as _io, re as _re
    _txt = _io.open(nullout, encoding="utf-8", errors="replace").read()
    _tm = _re.findall(r"total magnetization\s+=\s+(-?\d+\.\d+)", _txt)
    if not _tm or abs(float(_tm[-1]) - RIDER2_TOTMAG) > 5e-3:
        B.die("rider-2 candidate totmag %r != registered %.2f"
              % (_tm[-1] if _tm else None, RIDER2_TOTMAG))
    brk = (floors[(RIDER2_STATE, RIDER2_UTOK)] - e_null) * B.RY_EV * 1000.0
    if not (RIDER2_BREAK_MEV[0] < brk < RIDER2_BREAK_MEV[1]):
        B.die("rider-2 spin-instability %.2f meV outside the registered "
              "%.1f-%.1f band (docs/62 section 5.2)"
              % (brk, RIDER2_BREAK_MEV[0], RIDER2_BREAK_MEV[1]))
    if "%s__%s__sp2null" % (RIDER2_STATE, RIDER2_UTOK) in [r[3] for r in plan]:
        B.die("rider-2 stem leaked into the build plan")
    print("  T-e rider-2 fifth candidate re-derived: %.8f Ry, totmag %s, "
          "%.2f meV below the nspin=1 floor (named into the (s0_OOH,u900) "
          "pool, not rebuilt)" % (e_null, _tm[-1], brk))

    nk_ti = rederive_nk_ti()

    rows, deck_md5s, built = [], [], 0
    print("\nSTAGE 1, TI ARM -- 12 licensed seed-ladder decks")
    for st, u, s, stem in plan:
        txt, idx, nt = B.build_one("Ti", st, u, s, stem)   # A1-A10 enforced
        if (idx, nt) != (2, 3):                            # T-f
            B.die("Ti %s %s: index %s ntyp %s, adsorbate decks carry the "
                  "metal at 2 of 3" % (st, stem, idx, nt))
        child = os.path.join(out_spin, "Ti", stem + ".in")
        if not child.replace("\\", "/").endswith(
                "runs/a0/spin/Ti/%s.in" % stem):           # T-g
            B.die("child outside runs/a0/spin/Ti: %s" % child)
        B.write(child, txt)
        rel = "a0/spin/Ti/%s.in" % stem
        deck_md5s.append((rel, B.md5(child)))
        rows.append(("a0/spin/Ti", stem, nk_ti))
        built += 1
        print("  Ti  %-7s %s ntyp=%d index=%d  %s" % (st, u, nt, idx, stem))

    # T-i -- the banked trees are read-only by construction
    for p, h in parents.items():
        if B.md5(p) != h:
            B.die("PARENT ALTERED: %s" % p)
    print("\n  T-i all %d parent decks unchanged on disk" % len(parents))
    for p, h in bank.items():
        if not os.path.exists(p) or B.md5(p) != h:
            B.die("BANKED SPIN EVIDENCE ALTERED: %s" % p)
    print("  T-i all %d pre-existing runs/a0/spin files byte-identical "
          "(nulls + committed Stage-1 decks included)" % len(bank))

    # T-j -- the shared Ti sweep (licensed stems pass; anything else dies)
    TL.ti_sweep(B.die, {os.path.join(B.SPIN, "Ti"), os.path.join(out_spin, "Ti")})
    print("  T-j Ti sweep clean: banked __sp2null controls + licensed stems only")

    man = os.path.join(out_root, "runs", "a0", "m_a0spin_s1_ti.txt")
    hdr = [
        "# A0-SPIN STAGE 1, TI ARM -- the 12 licensed Ti production seed-ladder",
        "# decks. Built 2026-08-31 by src/dft/build_a0spin_s1_ti.py -- READ ITS",
        "# DOCSTRING (assertions T-a..T-l), the build_a0spin.py docstring",
        "# (A1-A12), and docs/43 AMENDMENT 11.",
        "#",
        "# LICENSED-EXECUTED 2026-08-31 -- docs/43 A11.R1 (the elections: [A11.5",
        "# HEADLINE CENSUS 2026-08-31], [A11.6 SEEDS+SELECTION 2026-08-31: AS",
        "# PROPOSED, with two dated riders], [A11.3 THRESHOLD 2026-08-31: 0.026 eV;",
        "# FALSIFICATION 0.005 eV]; A11.R4 prices this family \"Ti Stage-1 12\";",
        "# enumeration docs/62:215-216) + the docs/59 §3c dated line",
        "# [§3c LICENCE 2026-08-31: GRANTED — EXECUTED UNDER DIRECTIVE,",
        "# COUNTERSIGNATURE PENDING; s0_OH@u900 FIRST among Ti compute]",
        "# (elections docs/66 §2 row 1; the A11.R5 deposit precedes submission).",
        "#",
        "# " + SUBMIT_GATE + ".",
        "# Building banks nothing (docs/59 §3c); the confirmation gate is the",
        "# entrant's, read off docs/59 §5 at submit time.",
        "#",
        "# ROW ORDER = SUBMISSION ORDER: the s0_OH__u900 rows come FIRST --",
        "# docs/59 §3c registers 's0_OH@u900 FIRST among Ti compute' (docs/62 §9",
        "# item 3; a Ti-internal ordering, not a reordering of §A11.10).",
        "#",
        "# SELECTION (A11.6, registered): lowest converged total energy per",
        "# (state, U) across the three seeds AND the banked nspin=1 energy as hard",
        "# variational floor (\"must be <= 0\" -- equality passes; no additional",
        "# tolerance), ties within 1 meV to the smallest |seed|; both",
        "# magnetizations reported. RIDER 2: at (s0_OOH, u900) the banked",
        "# null-seed row -1298.17043625 Ry (totmag 1.04,",
        "# runs/a0/spin/Ti/s0_OOH__u900__sp2null.out) is the NAMED free fifth",
        "# candidate under the same rule -- re-derived off disk at build time.",
        "#",
        "# nk 8: every banked a0/{main,spin}/Ti manifest row carries nk 8,",
        "# re-derived at build time (T-h; the build directive's 'nk 4' note is a",
        "# FLAGGED deviation, banked convention followed).",
        "#",
        "# deck md5s (an independent rebuild must reproduce these byte-for-byte):",
    ] + ["# md5 %s %s" % (h, rel) for rel, h in deck_md5s] + [
        "#",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223",
        "# (submit-time list additionally + a120,a200 per docs/66 §4)",
        "#",
        "# row: dir job suffix nk",
        "# NP=128 NCONC=1",
    ]
    # T-k -- manifest self-checks
    if sum(1 for l in hdr if l == "# NP=128 NCONC=1") != 1:
        B.die("manifest must carry exactly one '# NP=128 NCONC=1' line")
    if sum(1 for l in hdr if l.startswith("# SUBMIT WITH EXCLUDE=")) != 1:
        B.die("manifest must carry exactly one EXCLUDE header")
    if not any("a120,a200" in l for l in hdr):
        B.die("manifest must carry the docs/66 §4 submit-time EXCLUDE note")
    if not any(SUBMIT_GATE in l for l in hdr):
        B.die("manifest must carry the SUBMITS-ONLY-AFTER sentence verbatim")
    if not any(TL.LICENCE_PREFIX in l for l in hdr):
        B.die("manifest must cite the docs/59 licence line")
    body = ["%s %s .in %d" % (d, s_, nk) for d, s_, nk in rows]
    for r in body:
        if len(r.split()) != 4:
            B.die("manifest row %r is not the 4-field grammar" % r)
    for r in body[:3]:
        if not r.split()[1].startswith("s0_OH__u900__"):
            B.die("manifest row order broken: %r before the s0_OH__u900 rows "
                  "(docs/59 §3c)" % r)
    txt_man = "\n".join(hdr + body) + "\n"
    if "not licensed" in txt_man.lower():
        B.die("manifest text matches the docs/66 §4 'NOT LICENSED' refusal")
    B.write(man, txt_man)
    print("  wrote %s (%d rows, s0_OH__u900 first)"
          % (os.path.relpath(man, out_root), len(rows)))
    print("\nBUILD OK -- %d decks, 0 relaxations, 0 parents touched. "
          "Submission gated on the A11.R5 deposit AND the docs/59 section-5 "
          "confirmation line." % built)


if __name__ == "__main__":
    main(sys.argv[1:])
