#!/usr/bin/env python3
"""A0-SPIN EQUALISED RE-READ: the 32 slab/s0_O ladder decks (Family C + Ti).

LICENSED 2026-08-31 -- docs/43 AMENDMENT 11 section A11.R3, the dated line
[A7.2 EQUALISED RE-READ 2026-08-31: RE-READ]: "per §A11.9, the equalised rows
read for A7.3 have A7.2 re-read on the same rows. Scope: Ru/Ir now -- which
requires Family C, 20 SCFs: {slab, s0_O} x {u000, u900} x {0.10, 0.30, 0.50}
x {Ru, Ir} minus the 4 already-run Stage-0 u000-seed-0.50 rungs (three
banked; the Ir slab rung is the registered REJECT, its energy recorded in
the rejection record -- a family docs/65's 76-SCF tally omitted; priced
here); Ti under the §3c grant (+12: {slab, s0_O} x {u000, u900} x 3 seeds,
docs/62:217-218)." Elections docs/66 §2 row 13. The Ru/Ir 20 submit after
the A11.R5 deposit; the Ti 12 additionally SUBMIT ONLY AFTER the entrant
confirmation line ([§3c CONFIRMED) exists in docs/59 §5 -- which is why this
builder writes TWO manifests (m_a0spin_reread.txt Ru/Ir,
m_a0spin_reread_ti.txt Ti), so the two gates never share a file.

REGISTERED LIMITATION, stated before the fact (A11.R3): an endpoint-only
re-read detects pls(0) != pls(9) but CANNOT locate the crossing U -- the
registered flip-U crossing deliverable (docs/43:1352-1353) needs the interior
ladder, a registered phase-2 decision point (docs/66 §6), outside this
family's licence. And per §A11.9 no banked A0 row is replaced; A7.2 is
re-read on the same rows the A7.3 equalised census reads (docs/66 §9's trap:
no A7.3-only re-read without A7.2 on the same rows).

THE IR-SLAB CONTINGENCY RIDES THESE ROWS (docs/66 §2 row 7; docs/43 A11.R3
[IR-SLAB CONTINGENCY 2026-08-31: EXTENDED-SEEDS(0.05) THEN
EQUALISED-BY-SELECTION(nspin=1)]): if none of {0.10, 0.30, 0.50} lands at or
below the banked nspin = 1 Ir slab energy, the pre-named extension seed 0.05
runs (Ir slab cells only, u000 + u900 = 2 SCFs); if that also lands above,
the cell resolves EQUALISED-BY-SELECTION(nspin=1) with the full rejection
record. The u000 seed-0.50 attempt is already banked REJECT (+0.583 meV,
docs/62 §4, called in advance from P11) -- inherited as a recorded attempt,
NOT rebuilt, and re-derived off disk here (R-e). The manifest's Ir slab rows
carry this contingency as a comment.

READ src/dft/build_a0spin.py's docstring first: every deck is produced by
build_a0spin.build_one (imported, not copied), so assertions A1-A10 are
enforced per deck and every species index is read from EACH PARENT DECK'S
OWN ATOMIC_SPECIES block, never from a constant (docs/61 §A11.8 item 2: the
index is STATE-dependent -- slab/s0_O put the metal at 1 of 2; the Stage-1
adsorbate decks at 2 of 3; a constant seeds oxygen on half of every ladder).
The Ti third is gated by the shared licence gate (a0spin_ti_licence): the
grep of docs/59 for the literal [§3c LICENCE 2026-08-31: GRANTED line, and
the whole build dies if it is absent -- this family is registered as 32, and
a 20-deck silent fallback would be a different, unregistered family.

WHAT THIS BUILDS
----------------
{slab, s0_O} x {u000, u900} x {0.10, 0.30, 0.50} x {Ru, Ir, Ti} = 36 MINUS
the 4 Stage-0 u000-seed-0.50 rungs for Ru/Ir only = 32 decks (Ru 10, Ir 10,
Ti 12) under runs/a0/spin/{Ru,Ir,Ti}/, all ntyp = 2 with the metal at
starting_magnetization index 1. Parents: the banked nspin = 1 decks
runs/a0/main/<M>/{slab,s0_O}__{u000,u900}.in, transformed by the same INSERT
Stage 1 used (prefix line + nspin=2 + starting_magnetization block at the
deck-derived metal index). Selection per cell: the A11.6 rule -- lowest
converged total energy across the seeds AND the banked nspin = 1 floor
("must be <= 0", equality passes), ties within 1 meV to the smallest |seed|.

BUILD-TIME ASSERTIONS (all fatal)
---------------------------------
R-a  the licence gate: docs/59 carries the literal [§3c LICENCE 2026-08-31:
     GRANTED line exactly once (the Ti third is registered into this
     family's 32; absence kills the WHOLE build, never a silent 20)
R-b  the plan is exactly the registered 32 (Ru 10 / Ir 10 / Ti 12); the Ti
     subset equals the shared TI_REREAD_STEMS universe; the plan is disjoint
     from the Stage-1 stems (TL.TI_S1_STEMS), the null controls, and every
     CMF stem (children only ever under a0/spin/{Ru,Ir,Ti})
R-c  no planned stem collides with banked evidence (a .out under the repo's
     runs/a0/spin/) and nothing at the output paths is ever overwritten; a
     repo .in for a planned stem is tolerated ONLY in a --sandbox rebuild
     (S1-c semantics, verbatim)
R-d  the 4 Stage-0 u000-seed-0.50 rungs exist on disk with converged .out
     files at runs/a0/spin/{Ru,Ir}/{slab,s0_O}__u000__sp2m050.* --
     inheritance is verified, not assumed, and they are never rebuilt
R-e  the Ir slab rung's REJECT re-derived off disk: its energy sits +0.583
     meV ABOVE the banked nspin = 1 floor (band 0.55-0.62; docs/62 §4),
     while the other three inherited rungs sit AT OR BELOW their floors
R-f  every parent .out is present and converged -- the twelve banked
     nspin = 1 rows ARE the selection rule's variational floor
R-g  every deck comes back ntyp = 2 with the metal at index 1, the index
     read from that parent's own ATOMIC_SPECIES (A1 inside build_one); a
     2-of-3 here means the plan leaked an adsorbate state
R-h  nk re-derived per metal from the banked a0/main manifest rows across
     runs/a0/m_*.txt (Ru 4, Ir 4, Ti 8; >= 1 row required per metal) and
     asserted equal to build_a0spin.NK. FLAGGED DEVIATION, never silent:
     the build directive's manifest note said "nk 4"; every banked Ti row
     carries 8, and this builder follows the banked convention
R-i  every child path ends runs/a0/spin/<M>/<stem>.in with M in {Ru, Ir,
     Ti} and stem state in {slab, s0_O}; nothing is written anywhere else
R-j  every parent .in under runs/a0/main/ (all six metals) and EVERY
     pre-existing file under runs/a0/spin/ md5-unchanged after the build --
     the 2 banked Ti null controls, the 20 committed Ru/Ir Stage-1 decks,
     the 4 inherited Stage-0 rungs and the 28 CMF siblings stay
     byte-identical (the A11/CMF-j sweep, widened to the whole bank)
R-k  the shared Ti sweep after the build: nulls + the 24 licensed stems
     only; any OTHER Ti .in dies (a0spin_ti_licence.ti_sweep)
R-l  the Ru/Ir manifest is Ru rows first then Ir (§A11.10 sequencing), its
     Ir slab rows carry the Row-7 contingency comment, and each manifest
     carries its EXCLUDE lines, exactly one '# NP=128 NCONC=1', 4-field
     rows, and no 'NOT LICENSED' match (the docs/66 §4 guard); the Ti
     manifest carries the SUBMITS-ONLY-AFTER sentence verbatim
R-m  per-deck md5s recorded in each manifest's header; an independent
     rebuild (--sandbox <dir>) must reproduce them byte-for-byte
R-n  the two manifests partition the 32 rows exactly (20 + 12, no overlap)

MANIFESTS
---------
runs/a0/m_a0spin_reread.txt   -- 20 Ru/Ir rows (Ru first), nk 4
runs/a0/m_a0spin_reread_ti.txt -- 12 Ti rows, nk 8; submits with/after
m_a0spin_s1_ti.txt, whose s0_OH__u900 rows lead (docs/59 §3c registers
's0_OH@u900 FIRST among Ti compute'; slab/s0_O rows have no s0_OH state, so
the ordering is discharged by submitting the Stage-1 Ti manifest first).
Same row grammar as m_a0spin_s1.txt ("dir job suffix nk", parsed by
anvil/46_a0.slurm + anvil/47_submit_a0.sh; '#' lines are comments; trailing
fields are fatal in the submitter).

USAGE
-----
    python src/dft/build_a0spin_reread.py                  # build into the repo
    python src/dft/build_a0spin_reread.py --sandbox DIR    # independent rebuild
                                                           # into DIR/runs/...
                                                           # for the determinism
                                                           # check

Any other argument is refused.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import build_a0spin as B          # A1-A10 build_one, read/write/md5/die, NK
import a0spin_ti_licence as TL    # the shared licence gate + Ti sweep
import qe_qc

METALS_RR = ("Ru", "Ir", "Ti")    # Ru first, then Ir (§A11.10), Ti under §3c
STATES_RR = ("slab", "s0_O")      # the A7.2 re-read states
UTOKS_RR = ("u000", "u900")       # fixed endpoints (flip-U crossing excluded)
SEEDS_RR = B.SEEDS                # (0.10, 0.30, 0.50) -- A11.6, AS PROPOSED

REG_COUNTS = {"Ru": 10, "Ir": 10, "Ti": 12}   # registered per-metal counts
REG_TOTAL = 32                                # "36 MINUS the 4 ... = 32"

#: Registered REJECT margin for the inherited Ir slab rung (docs/62 §4:
#: +0.583 meV above the banked nspin=1 floor), re-derived off disk (R-e).
REJECT_BAND_MEV = (0.55, 0.62)

SUBMIT_GATE = ("SUBMITS ONLY AFTER the entrant confirmation line "
               "([§3c CONFIRMED) exists in docs/59 §5")


def stem_of(state: str, utok: str, seed: float) -> str:
    return "%s__%s__sp2m%03d" % (state, utok, int(round(seed * 100)))


def inherited(metal: str, utok: str, seed: float) -> bool:
    """The four Stage-0-banked rungs (Ru/Ir, u000, seed 0.50) -- never rebuilt."""
    return metal in ("Ru", "Ir") and utok == "u000" and abs(seed - 0.50) < 1e-9


def rederive_nk_rr():
    """R-h: nk per metal licensed by the banked a0/main manifest rows."""
    want = {"Ru": "4", "Ir": "4", "Ti": "8"}
    seen = {m: 0 for m in METALS_RR}
    mandir = os.path.join(ROOT, "runs", "a0")
    for f in sorted(os.listdir(mandir)):
        if not (f.startswith("m_") and f.endswith(".txt")):
            continue
        for ln in B.read(os.path.join(mandir, f)).split("\n"):
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            for m in METALS_RR:
                if parts[0] == "a0/main/%s" % m:
                    if len(parts) < 4 or parts[3] != want[m]:
                        B.die("banked manifest %s row %r contradicts nk=%s "
                              "for %s" % (f, s, want[m], m))
                    seen[m] += 1
    nk = {}
    for m in METALS_RR:
        if seen[m] == 0:
            B.die("no banked a0/main/%s manifest row found -- cannot license "
                  "nk" % m)
        nk[m] = int(want[m])
        if B.NK[m] != nk[m]:
            B.die("build_a0spin.NK[%r] = %r contradicts the banked nk %d"
                  % (m, B.NK[m], nk[m]))
    print("  R-h nk re-derived from banked rows: Ru %d(x%d) Ir %d(x%d) "
          "Ti %d(x%d) (Ti's 8 is a FLAGGED deviation from the directive's "
          "'nk 4' note; banked convention followed)"
          % (nk["Ru"], seen["Ru"], nk["Ir"], seen["Ir"], nk["Ti"], seen["Ti"]))
    return nk


def plan_rr():
    """R-b: the registered 32 (Ru 10 / Ir 10 / Ti 12), in manifest order."""
    plan = []
    for m in METALS_RR:
        n = 0
        for st in STATES_RR:
            for u in UTOKS_RR:
                for s in SEEDS_RR:
                    if inherited(m, u, s):
                        continue
                    plan.append((m, st, u, s, stem_of(st, u, s)))
                    n += 1
        if n != REG_COUNTS[m]:
            B.die("plan drift: %d %s decks, registered %d" % (n, m, REG_COUNTS[m]))
    if len(plan) != REG_TOTAL:
        B.die("plan drift: %d decks, registered total is 32" % len(plan))
    ti_stems = sorted(r[4] for r in plan if r[0] == "Ti")
    if ti_stems != sorted(TL.TI_REREAD_STEMS):
        B.die("plan drift: Ti stems disagree with the shared licensed "
              "universe (a0spin_ti_licence.TI_REREAD_STEMS)")
    bad = set(r[4] for r in plan) & (set(TL.TI_S1_STEMS) | set(TL.NULL_STEMS))
    if bad:
        B.die("plan collides with Stage-1/null stems: %r" % sorted(bad))
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
              "registered 32-deck equalised re-read set; only --sandbox <dir> "
              "is accepted" % a)

    B.RY_EV = qe_qc.RY_EV
    out_spin = os.path.join(out_root, "runs", "a0", "spin")
    print("LICENSED 2026-08-31 (docs/43 A11.R3 [A7.2 EQUALISED RE-READ]); the "
          "Ru/Ir 20 submit after the A11.R5 deposit; the Ti 12 additionally "
          "wait on the docs/59 section-5 confirmation line.")
    if os.path.normcase(out_root) != os.path.normcase(ROOT):
        print("SANDBOX rebuild into %s (parents/evidence still read from the repo)"
              % out_root)

    # R-a -- the licence gate (the Ti third is registered into this family)
    lic_line = TL.require_licence(B.die)
    print("  R-a docs/59 licence line present: %s..." % lic_line[:60])

    # R-j snapshot: all parents + the whole banked spin tree
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

    plan = plan_rr()

    # R-c -- collisions and overwrites (S1-c semantics, verbatim)
    for m, st, u, s, stem in plan:
        p = os.path.join(B.SPIN, m, stem + ".out")
        if os.path.exists(p):
            B.die("stem %s collides with banked evidence %s" % (stem, p))
        for ext in (".in", ".out"):
            c = os.path.join(out_spin, m, stem + ext)
            if os.path.exists(c):
                B.die("refusing to overwrite existing child %s" % c)

    # R-d/R-e -- the four inherited Stage-0 rungs: banked, converged, and the
    # Ir slab REJECT re-derived off disk (never rebuilt)
    for m in ("Ru", "Ir"):
        for st in STATES_RR:
            stem = stem_of(st, "u000", 0.50)
            pin = os.path.join(B.SPIN, m, stem + ".in")
            pout = os.path.join(B.SPIN, m, stem + ".out")
            if not os.path.exists(pin):
                B.die("inherited Stage-0 deck missing: %s" % pin)
            e2 = B.energy_ry(pout)
            if e2 is None:
                B.die("inherited Stage-0 run missing or unconverged: %s" % pout)
            e1 = B.energy_ry(os.path.join(B.MAIN, m, "%s__u000.out" % st))
            if e1 is None:
                B.die("banked nspin=1 floor missing for %s %s u000" % (m, st))
            dmev = (e2 - e1) * B.RY_EV * 1000.0
            if m == "Ir" and st == "slab":
                if not (REJECT_BAND_MEV[0] < dmev < REJECT_BAND_MEV[1]):
                    B.die("Ir slab rung: %.4f meV vs floor, outside the "
                          "registered REJECT band %.2f-%.2f (docs/62 section 4)"
                          % (dmev, REJECT_BAND_MEV[0], REJECT_BAND_MEV[1]))
                print("  R-e Ir slab u000 m050 REJECT re-derived: %+.4f meV "
                      "above the nspin=1 floor (recorded attempt, not rebuilt)"
                      % dmev)
            else:
                if dmev > 0.0:
                    B.die("%s %s u000 m050: %.4f meV ABOVE the floor -- the "
                          "banked pass contradicts the record" % (m, st, dmev))
                print("  R-d %s %-4s u000 m050 inherited, converged, %+.4f meV "
                      "vs floor" % (m, st, dmev))

    # R-f -- the variational floor exists: every parent .out converged
    for m in METALS_RR:
        for st in STATES_RR:
            for u in UTOKS_RR:
                pout = os.path.join(B.MAIN, m, "%s__%s.out" % (st, u))
                if B.energy_ry(pout) is None:
                    B.die("selection floor missing: %s has no converged "
                          "energy (the banked nspin=1 row IS the A11.6 hard "
                          "floor)" % pout)
    print("  R-f all 12 banked nspin=1 floors present and converged")

    nk = rederive_nk_rr()

    rows, deck_md5s, built = [], [], 0
    print("\nEQUALISED RE-READ -- 32 slab/s0_O ladder decks (Ru 10, Ir 10, Ti 12)")
    for m, st, u, s, stem in plan:
        txt, idx, nt = B.build_one(m, st, u, s, stem)     # A1-A10 enforced
        if (idx, nt) != (1, 2):                           # R-g
            B.die("%s %s %s: index %s ntyp %s, slab/s0_O decks carry the "
                  "metal at 1 of 2" % (m, st, stem, idx, nt))
        child = os.path.join(out_spin, m, stem + ".in")
        if not child.replace("\\", "/").endswith(
                "runs/a0/spin/%s/%s.in" % (m, stem)) or \
                m not in METALS_RR or \
                not stem.startswith(("slab__", "s0_O__")):   # R-i
            B.die("child outside the licensed tree: %s" % child)
        B.write(child, txt)
        rel = "a0/spin/%s/%s.in" % (m, stem)
        deck_md5s.append((rel, B.md5(child)))
        rows.append((m, "a0/spin/%s" % m, stem, nk[m]))
        built += 1
        print("  %-3s %-5s %s ntyp=%d index=%d  %s" % (m, st, u, nt, idx, stem))

    # R-j -- the banked trees are read-only by construction
    for p, h in parents.items():
        if B.md5(p) != h:
            B.die("PARENT ALTERED: %s" % p)
    print("\n  R-j all %d parent decks unchanged on disk" % len(parents))
    for p, h in bank.items():
        if not os.path.exists(p) or B.md5(p) != h:
            B.die("BANKED SPIN EVIDENCE ALTERED: %s" % p)
    print("  R-j all %d pre-existing runs/a0/spin files byte-identical "
          "(nulls, committed Stage-1 decks, inherited rungs, CMF siblings)"
          % len(bank))

    # R-k -- the shared Ti sweep
    TL.ti_sweep(B.die, {os.path.join(B.SPIN, "Ti"), os.path.join(out_spin, "Ti")})
    print("  R-k Ti sweep clean: banked __sp2null controls + licensed stems only")

    # ---- manifests (R-l/R-m/R-n) -----------------------------------------
    ruir = [(d, s_, k) for m, d, s_, k in rows if m in ("Ru", "Ir")]
    ti = [(d, s_, k) for m, d, s_, k in rows if m == "Ti"]
    if (len(ruir), len(ti)) != (20, 12):                   # R-n
        B.die("manifest partition drift: %d Ru/Ir + %d Ti" % (len(ruir), len(ti)))

    common_tail = [
        "#",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223",
        "# (submit-time list additionally + a120,a200 per docs/66 §4)",
        "#",
        "# row: dir job suffix nk",
        "# NP=128 NCONC=1",
    ]

    def check_and_write(man, hdr, body_lines, nrows, ti_gate):
        if sum(1 for l in hdr if l == "# NP=128 NCONC=1") != 1:
            B.die("manifest must carry exactly one '# NP=128 NCONC=1' line")
        if sum(1 for l in hdr if l.startswith("# SUBMIT WITH EXCLUDE=")) != 1:
            B.die("manifest must carry exactly one EXCLUDE header")
        if not any("a120,a200" in l for l in hdr):
            B.die("manifest must carry the docs/66 §4 submit-time EXCLUDE note")
        if not any("[A7.2 EQUALISED RE-READ 2026-08-31" in l for l in hdr):
            B.die("manifest must cite the licensing A11.R3 line")
        if ti_gate and not any(SUBMIT_GATE in l for l in hdr):
            B.die("Ti manifest must carry the SUBMITS-ONLY-AFTER sentence")
        if ti_gate and not any(TL.LICENCE_PREFIX in l for l in hdr):
            B.die("Ti manifest must cite the docs/59 licence line")
        nb = 0
        for r in body_lines:
            if r.startswith("#"):
                continue
            if len(r.split()) != 4:
                B.die("manifest row %r is not the 4-field grammar" % r)
            nb += 1
        if nb != nrows:
            B.die("manifest %s carries %d rows, expected %d" % (man, nb, nrows))
        txt_man = "\n".join(hdr + body_lines) + "\n"
        if "not licensed" in txt_man.lower():
            B.die("manifest text matches the docs/66 §4 'NOT LICENSED' refusal")
        B.write(man, txt_man)
        print("  wrote %s (%d rows)" % (os.path.relpath(man, out_root), nb))

    # Ru/Ir manifest: Ru rows first (§A11.10); Ir slab rows carry the Row-7
    # contingency comment (R-l)
    man_a = os.path.join(out_root, "runs", "a0", "m_a0spin_reread.txt")
    hdr_a = [
        "# A0-SPIN EQUALISED RE-READ, FAMILY C -- the 20 Ru/Ir slab/s0_O ladder",
        "# decks. Built 2026-08-31 by src/dft/build_a0spin_reread.py -- READ ITS",
        "# DOCSTRING (assertions R-a..R-n), the build_a0spin.py docstring",
        "# (A1-A12), and docs/43 AMENDMENT 11.",
        "#",
        "# LICENSED 2026-08-31 -- docs/43 A11.R3, the dated line",
        "# [A7.2 EQUALISED RE-READ 2026-08-31: RE-READ]: \"Scope: Ru/Ir now --",
        "# which requires Family C, 20 SCFs: {slab, s0_O} x {u000, u900} x",
        "# {0.10, 0.30, 0.50} x {Ru, Ir} minus the 4 already-run Stage-0",
        "# u000-seed-0.50 rungs\"",
        "# (elections docs/66 §2 row 13; a family docs/65's 76-SCF tally omitted,",
        "# priced in A11.R3; the A11.R5 deposit precedes submission).",
        "# Per §A11.9 no banked A0 row is replaced, and A7.2 is re-read on the",
        "# same rows the A7.3 equalised census reads (docs/66 §9's trap).",
        "# REGISTERED LIMITATION: endpoint-only -- detects pls(0) != pls(9) but",
        "# CANNOT locate the crossing U; the interior ladder is a registered",
        "# phase-2 decision point (docs/66 §6), outside this family's licence.",
        "#",
        "# The 4 u000-seed-0.50 rungs are INHERITED FROM STAGE 0 at",
        "# runs/a0/spin/{Ru,Ir}/{slab,s0_O}__u000__sp2m050.{in,out} -- not",
        "# rebuilt and not rows here. Three are banked at-or-below their",
        "# nspin=1 floors; the Ir slab rung is the registered REJECT (+0.583",
        "# meV, docs/62 §4), inherited as a recorded attempt.",
        "#",
        "# SELECTION (A11.6, registered): lowest converged total energy per",
        "# (metal, state, U) across the seeds AND the banked nspin=1 energy as",
        "# hard variational floor (\"must be <= 0\" -- equality passes), ties",
        "# within 1 meV to the smallest |seed|; both magnetizations reported.",
        "#",
        "# 10 Ru rows then 10 Ir rows (§A11.10 Ru-first sequencing). nk 4 (the",
        "# banked Ru/Ir convention, re-derived R-h).",
        "#",
        "# deck md5s (an independent rebuild must reproduce these byte-for-byte):",
    ] + ["# md5 %s %s" % (h, rel) for rel, h in deck_md5s
         if not rel.startswith("a0/spin/Ti/")] + common_tail
    ir_slab_comment = [
        "# The 5 Ir slab rows below carry the Row-7 contingency (docs/66 §2 row",
        "# 7; docs/43 A11.R3 [IR-SLAB CONTINGENCY 2026-08-31: EXTENDED-SEEDS(0.05)",
        "# THEN EQUALISED-BY-SELECTION(nspin=1)]): if none of {0.10, 0.30, 0.50}",
        "# lands at or below the banked nspin=1 Ir slab energy, the PRE-NAMED",
        "# extension seed 0.05 runs (Ir slab cells only, u000 + u900 = 2 SCFs);",
        "# if that also lands above, the cell resolves EQUALISED-BY-",
        "# SELECTION(nspin=1) with the full rejection record. The u000 seed-0.50",
        "# attempt is already banked REJECT (+0.583 meV, docs/62 §4).",
    ]
    body_a, commented = [], False
    n_ir_slab = 0
    for d, s_, k in ruir:
        if d == "a0/spin/Ir" and s_.startswith("slab__"):
            if not commented:
                body_a.extend(ir_slab_comment)
                commented = True
            n_ir_slab += 1
        body_a.append("%s %s .in %d" % (d, s_, k))
    if not commented or n_ir_slab != 5:                    # R-l
        B.die("Ir slab contingency comment misplaced: commented=%r, %d Ir "
              "slab rows (expected 5, contiguous)" % (commented, n_ir_slab))
    check_and_write(man_a, hdr_a, body_a, 20, ti_gate=False)

    # Ti manifest (R-l: the SUBMITS-ONLY-AFTER sentence)
    man_b = os.path.join(out_root, "runs", "a0", "m_a0spin_reread_ti.txt")
    hdr_b = [
        "# A0-SPIN EQUALISED RE-READ, TI -- the 12 Ti slab/s0_O ladder decks.",
        "# Built 2026-08-31 by src/dft/build_a0spin_reread.py -- READ ITS",
        "# DOCSTRING (assertions R-a..R-n), the build_a0spin.py docstring",
        "# (A1-A12), and docs/43 AMENDMENT 11.",
        "#",
        "# LICENSED-EXECUTED 2026-08-31 -- docs/43 A11.R3, the dated line",
        "# [A7.2 EQUALISED RE-READ 2026-08-31: RE-READ]: \"Ti under the §3c grant",
        "# (+12: {slab, s0_O} x {u000, u900} x 3 seeds, docs/62:217-218)\"",
        "# (elections docs/66 §2 row 13) + the docs/59 §3c dated line",
        "# [§3c LICENCE 2026-08-31: GRANTED — EXECUTED UNDER DIRECTIVE,",
        "# COUNTERSIGNATURE PENDING; s0_OH@u900 FIRST among Ti compute]",
        "# (docs/66 §2 row 1; the A11.R5 deposit precedes submission).",
        "#",
        "# " + SUBMIT_GATE + ".",
        "# Building banks nothing (docs/59 §3c); the confirmation gate is the",
        "# entrant's, read off docs/59 §5 at submit time. This manifest submits",
        "# WITH OR AFTER m_a0spin_s1_ti.txt, whose s0_OH__u900 rows lead --",
        "# docs/59 §3c registers 's0_OH@u900 FIRST among Ti compute', and no",
        "# slab/s0_O row may run before it.",
        "#",
        "# Per §A11.9 no banked A0 row is replaced, and A7.2 is re-read on the",
        "# same rows the A7.3 equalised census reads (docs/66 §9's trap).",
        "# REGISTERED LIMITATION: endpoint-only -- detects pls(0) != pls(9) but",
        "# CANNOT locate the crossing U; the interior ladder is a registered",
        "# phase-2 decision point (docs/66 §6), outside this family's licence.",
        "#",
        "# SELECTION (A11.6, registered): lowest converged total energy per",
        "# (state, U) across the seeds AND the banked nspin=1 energy as hard",
        "# variational floor (\"must be <= 0\" -- equality passes), ties within",
        "# 1 meV to the smallest |seed|; both magnetizations reported.",
        "#",
        "# nk 8: every banked a0/{main,spin}/Ti manifest row carries nk 8,",
        "# re-derived at build time (R-h; the build directive's 'nk 4' note is a",
        "# FLAGGED deviation, banked convention followed).",
        "#",
        "# deck md5s (an independent rebuild must reproduce these byte-for-byte):",
    ] + ["# md5 %s %s" % (h, rel) for rel, h in deck_md5s
         if rel.startswith("a0/spin/Ti/")] + common_tail
    body_b = ["%s %s .in %d" % (d, s_, k) for d, s_, k in ti]
    check_and_write(man_b, hdr_b, body_b, 12, ti_gate=True)

    print("\nBUILD OK -- %d decks, 0 relaxations, 0 parents touched. Ru/Ir "
          "submission gated on the A11.R5 deposit; Ti additionally on the "
          "docs/59 section-5 confirmation line." % built)


if __name__ == "__main__":
    main(sys.argv[1:])
