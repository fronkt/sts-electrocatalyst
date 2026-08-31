#!/usr/bin/env python3
"""CR/MN/FE SEED SEARCH: the A0-SPIN seed-grid completion on the three nspin=2 metals (28 decks).

LICENSED 2026-08-31 -- docs/43 AMENDMENT 11, section A11.R3, the dated line
[CR/MN/FE SEED SEARCH 2026-08-31: RUNS]: "exactly 28 SCFs (Cr 12: banked seed
0.6 is off-grid in every cell; Mn 8: banked 0.5 = m050 covers all four cells;
Fe 8: banked s0_OH 0.5 and s0_OOH 0.1 cover four cells)". Elections docs/66 §2
row 12. Submission remains gated on the A11.R5 deposit and the docs/66 §4
pipeline guards; this builder only builds.

READ src/dft/build_a0spin.py's docstring first: this builder imports its
machinery (read/write/md5/species_order/die) and inherits its registration
posture -- every docstring claim below is RE-DERIVED off disk before a single
deck is written, and every species index is read from each parent deck's OWN
ATOMIC_SPECIES block, never from a constant.

WHY THIS FAMILY EXISTS (docs/61 decision item 7, elected RUNS)
--------------------------------------------------------------
Without it the A0-SPIN arm equalises the spin *keyword* but not the search
*effort*: Cr ran one seed (0.6), Mn one (0.5), and only Fe *OOH got a
three-seed pilot -- so Ru/Ir/Ti would be searched harder than the three
metals they are compared against. This family completes the {0.10, 0.30,
0.50} grid (A11.6, elected AS PROPOSED) on the Cr/Mn/Fe adsorbate cells at
the A7.3 endpoints.

THE TRANSFORMATION IS REPLACEMENT, NOT INSERTION
------------------------------------------------
Every parent runs/a0/main/{Cr,Mn,Fe}/{s0_OH,s0_OOH}__{u000,u900}.in is
ALREADY nspin = 2 with an FM-uniform starting_magnetization block (one
nonzero value, on the metal; zeros explicit on H and O). A child deck
therefore differs from its parent in EXACTLY TWO LINES:

    prefix = '<stem>'                              (the A5/A6 pattern)
    starting_magnetization(<metal idx>) = <seed>   (the seed replacement)

The build_a0spin.build_one insertion path (diff shape +1+ntyp/~1/-0) is WRONG
for these parents -- it would emit a second nspin line. The metal index is
STATE-dependent and PER-DECK: in these adsorbate decks the alphabetical
species sort puts Mn at index 2 (H < Mn < O) but Cr and Fe at index 1
(Cr < H < O, Fe < H < O). CMF-b re-derives that off every parent; the
emitted index always comes from that parent's own ATOMIC_SPECIES.

FM-UNIFORM-SEED ONLY. This family never touches the A7.5 Mn AFM condition
(docs/43:1406-1407 -- the registered either/or is untouched by it, per the
A11.R3 line); no negative seed, no sublattice split, no deck outside
runs/a0/spin/{Cr,Mn,Fe}/.

THE DERIVED PLAN, AND THE COVERAGE CONVENTION (registered, A11.R3)
------------------------------------------------------------------
"A banked seed equal to a grid member covers that cell AT BOTH ENDPOINTS
(banked u900 seeds verified identical to u000)" -- re-verified here off the
parents' own starting_magnetization, per (metal, state), u000 vs u900:

    Cr s0_OH, s0_OOH  banked 0.6  off-grid   -> m010 m030 m050 x 2 U = 12
    Mn s0_OH, s0_OOH  banked 0.5  = m050     -> m010 m030      x 2 U =  8
    Fe s0_OH          banked 0.5  = m050     -> m010 m030      x 2 U =  4
    Fe s0_OOH         banked 0.1  = m010     -> m030 m050      x 2 U =  4
                                                                       ----
                                                                        28

The plan is DERIVED from each parent's own banked seed at build time and then
asserted against the registered literals above; ANY drift -- a changed parent,
a miscounted cell, a total other than 28 -- kills the build (CMF-a/CMF-e).

SELECTION (A11.6-ANALOGUE, registered in the A11.R3 line): lowest converged
total energy per (metal, state, U) across the grid seeds AND the banked FM
row as incumbent (these metals have no nspin = 1 floor; the banked FM energy
is the incumbent candidate), ties within 1 meV to the smallest |seed|.
Winners enter the a7_3_spin sensitivity census ONLY; no banked A0 row is
replaced (§A11.9). The incumbent's existence is verified at build time
(every parent .out present and converged, CMF-c).

BUILD-TIME ASSERTIONS (all fatal)
---------------------------------
CMF-a  the derived plan is exactly the registered 28 (Cr 12 / Mn 8 / Fe 8);
       any other count stops the build and flags the derived breakdown
CMF-b  metal index read from each parent's own ATOMIC_SPECIES; re-derived
       claim Mn -> 2, Cr/Fe -> 1 on all 12 parents; the emitted nonzero
       index equals the parent-read index
CMF-c  every parent is ALREADY nspin = 2 with exactly ntyp
       starting_magnetization lines, contiguous 1..ntyp, exactly one
       nonzero, on the metal; parent prefix == '<state>__<utok>'; parent
       .out present and converged (the selection rule's incumbent exists)
CMF-d  replacement diff shape: exactly 2 replaced lines (prefix + the
       metal's seed line), 0 inserted, 0 deleted; child line count equals
       parent line count; every other line byte-identical
CMF-e  coverage convention re-verified: banked u000 seed == banked u900
       seed per (metal, state); banked seed equal to a grid member skips
       exactly that member; banked-vs-registered literals match
CMF-f  the child seed block stays FM-uniform: exactly one nonzero seed,
       positive, on the metal, formatted %.2f; nspin line untouched
CMF-g  no planned stem collides with banked evidence (a .out under the
       repo's runs/a0/spin/) and nothing at the output paths is ever
       overwritten; a repo .in for a planned stem is tolerated ONLY in a
       --sandbox rebuild (the S1-c semantics, verbatim)
CMF-h  no forbidden key introduced (build_a0spin.FORBIDDEN); prefix ==
       stem == basename (46_a0.slurm rm -rf's dens/${prefix}.save);
       trailing-newline and CR bytes preserved from the parent
CMF-i  every child path ends runs/a0/spin/<M>/<stem>.in with M in
       {Cr, Mn, Fe} and stem state in {s0_OH, s0_OOH}; nothing is written
       anywhere else
CMF-j  every parent .in under runs/a0/main/ (all six metals) md5-unchanged
       after the build (the A11 sweep, widened)
CMF-k  Ti sweep: this family must not touch Ti. Delegated to the shared
       a0spin_ti_licence.ti_sweep (2026-08-31): the banked __sp2null
       controls always pass, the 24 licensed 2026-08-31 Ti stems pass
       iff docs/59 carries the executed licence line, anything else dies
CMF-l  per-deck md5s recorded in the manifest header; an independent
       rebuild (--sandbox <dir>) must reproduce them byte-for-byte
CMF-m  nk = 4 re-derived: every banked a0/main/{Cr,Mn,Fe} manifest row
       across runs/a0/m_*.txt carries nk 4 (>= 1 row required per metal)

MANIFEST
--------
runs/a0/m_cmf_seed_search.txt, same row grammar as m_a0spin_s1.txt ("dir job
suffix nk", parsed by anvil/46_a0.slurm + anvil/47_submit_a0.sh; '#' lines
are comments; trailing fields are fatal in the submitter). nk 4 (the banked
Cr/Mn/Fe A0-main mesh, CMF-m). Cr rows, then Mn, then Fe (the A11.R3 line's
own order). Submission: after the A11.R5 deposit, with the manifest EXCLUDE
list plus a120,a200 at submit time (docs/66 §4 [EXCLUDE EXTENDED
2026-08-31]).

USAGE
-----
    python src/dft/build_cmf_seed_search.py                  # build into the repo
    python src/dft/build_cmf_seed_search.py --sandbox DIR    # independent rebuild
                                                             # into DIR/runs/... for
                                                             # the determinism check

Any other argument is refused.
"""
from __future__ import annotations

import difflib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import build_a0spin as B  # read/write/md5/die/species_order/ntyp_of/energy_ry

METALS_CMF = ("Cr", "Mn", "Fe")   # the A11.R3 line's own order
STATES_CMF = ("s0_OH", "s0_OOH")  # the A0-SPIN adsorbate cells (c_M needs only these)
UTOKS_CMF = ("u000", "u900")      # fixed A7.3 endpoints
SEEDS_CMF = B.SEEDS               # (0.10, 0.30, 0.50) -- A11.6, elected AS PROPOSED

#: Registered literals from the A11.R3 line -- NEVER trusted: each is re-derived
#: off the parent decks' own starting_magnetization and the build dies on drift.
REG_BANKED = {
    ("Cr", "s0_OH"): 0.6, ("Cr", "s0_OOH"): 0.6,
    ("Mn", "s0_OH"): 0.5, ("Mn", "s0_OOH"): 0.5,
    ("Fe", "s0_OH"): 0.5, ("Fe", "s0_OOH"): 0.1,
}
REG_COUNTS = {"Cr": 12, "Mn": 8, "Fe": 8}   # the registered per-metal deck counts
REG_TOTAL = 28                               # "the total MUST come out 28"

#: Registered index claim (docs/67 §2 / docs/61 §A11.8 item 2): asserted against
#: the parent-derived index, never used to build.
REG_INDEX = {"Cr": 1, "Mn": 2, "Fe": 1}

NK_CMF = {"Cr": 4, "Mn": 4, "Fe": 4}         # re-derived from banked manifests (CMF-m)

MAG_RE = r"^(\s*)starting_magnetization\((\d+)\)(\s*=\s*)(\S+)(\s*)$"


def stem_of(state: str, utok: str, seed: float) -> str:
    return "%s__%s__sp2m%03d" % (state, utok, int(round(seed * 100)))


def parent_path(metal: str, state: str, utok: str) -> str:
    return os.path.join(B.MAIN, metal, "%s__%s.in" % (state, utok))


def mag_lines(txt: str):
    """(line_index, species_index, value_string) for every starting_magnetization
    line, in file order."""
    out = []
    for i, ln in enumerate(txt.split("\n")):
        m = re.match(MAG_RE, ln)
        if m:
            out.append((i, int(m.group(2)), m.group(4)))
    return out


def banked_seed(metal: str, state: str, utok: str):
    """(seed, metal_index, ntyp) read from the parent's own bytes; CMF-c fatal."""
    p = parent_path(metal, state, utok)
    if not os.path.exists(p):
        B.die("no parent deck %s" % p)
    txt = B.read(p)
    order = B.species_order(txt)
    nt = B.ntyp_of(txt)
    if len(order) != nt:
        B.die("%s: ntyp %d but %d species" % (p, nt, len(order)))
    if metal not in order:
        B.die("%s: %s not in ATOMIC_SPECIES %r" % (p, metal, order))
    idx = order.index(metal) + 1                                   # CMF-b
    if idx != REG_INDEX[metal]:
        B.die("%s: index %d contradicts the registered claim %d -- a parent "
              "changed shape" % (p, idx, REG_INDEX[metal]))
    if not re.search(r"^\s*nspin\s*=\s*2\s*$", txt, re.M):         # CMF-c
        B.die("%s is not nspin=2 -- the replacement transformation does not "
              "apply; this family builds off ALREADY-spin-polarised parents" % p)
    mags = mag_lines(txt)
    if [s for _, s, _ in mags] != list(range(1, nt + 1)):          # CMF-c (A2)
        B.die("%s: starting_magnetization lines not exactly 1..%d in order: %r"
              % (p, nt, [(s, v) for _, s, v in mags]))
    li = [l for l, _, _ in mags]
    if li != list(range(li[0], li[0] + nt)):
        B.die("%s: starting_magnetization lines not contiguous" % p)
    nz = [(s, v) for _, s, v in mags if float(v) != 0.0]
    if len(nz) != 1:                                               # CMF-c (A3)
        B.die("%s: %d nonzero seeds, need exactly 1 (FM-uniform parent)"
              % (p, len(nz)))
    if nz[0][0] != idx:
        B.die("%s: nonzero seed on species %d, metal is %d -- the parent seeds "
              "a non-metal species" % (p, nz[0][0], idx))
    m = re.search(r"^\s*prefix\s*=\s*'([^']+)'", txt, re.M)
    if not m or m.group(1) != "%s__%s" % (state, utok):            # CMF-c
        B.die("%s: parent prefix %r != '%s__%s'"
              % (p, m and m.group(1), state, utok))
    if B.energy_ry(p[:-3] + ".out") is None:                       # CMF-c incumbent
        B.die("incumbent missing: %s has no converged .out -- the A11.6-ANALOGUE "
              "selection needs the banked FM row as a candidate" % p)
    return float(nz[0][1]), idx, nt


def rederive_nk():
    """CMF-m: nk 4 licensed by the banked manifests, not by this file's constant."""
    seen = {m: 0 for m in METALS_CMF}
    mandir = os.path.join(ROOT, "runs", "a0")
    for f in sorted(os.listdir(mandir)):
        if not (f.startswith("m_") and f.endswith(".txt")):
            continue
        for ln in B.read(os.path.join(mandir, f)).split("\n"):
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            for metal in METALS_CMF:
                if parts[0] == "a0/main/%s" % metal:
                    # nk is field 4 in every banked grammar (the repair
                    # manifests carry a 5th, 49_submit_repairs.sh's seed job;
                    # that grammar is not this builder's to police -- only nk).
                    if len(parts) < 4 or parts[3] != "4":
                        B.die("banked manifest %s row %r contradicts nk=4"
                              % (f, s))
                    seen[metal] += 1
    for metal, n in seen.items():
        if n == 0:
            B.die("no banked a0/main/%s manifest row found -- cannot license nk"
                  % metal)
    print("  CMF-m nk=4 re-derived from banked rows: Cr %d, Mn %d, Fe %d"
          % (seen["Cr"], seen["Mn"], seen["Fe"]))


def rederive_cmf():
    """Every docstring claim read off disk, not trusted (die on disagreement)."""
    print("REDERIVE -- every claim below is read off disk, not trusted")
    banked = {}
    for metal in METALS_CMF:
        for state in STATES_CMF:
            s0, i0, n0 = banked_seed(metal, state, "u000")
            s9, i9, n9 = banked_seed(metal, state, "u900")
            if (s0, i0, n0) != (s9, i9, n9):                       # CMF-e
                B.die("%s %s: u900 (seed %s idx %d) != u000 (seed %s idx %d) -- "
                      "the registered both-endpoints coverage convention fails"
                      % (metal, state, s9, i9, s0, i0))
            if abs(s0 - REG_BANKED[(metal, state)]) > 1e-9:        # CMF-e
                B.die("%s %s: banked seed %s contradicts the registered literal "
                      "%s (A11.R3)" % (metal, state, s0, REG_BANKED[(metal, state)]))
            banked[(metal, state)] = (s0, i0, n0)
            print("  CMF-c/e %s %-6s banked seed %.1f at index %d (u000==u900), "
                  "incumbent .out converged" % (metal, state, s0, i0))
    print("  CMF-b index rule re-derived on all 12 parents: Mn -> 2, Cr/Fe -> 1")
    rederive_nk()
    return banked


def plan_cmf(banked):
    """The derived plan; CMF-a/CMF-e fatal."""
    plan = []
    for metal in METALS_CMF:
        n_metal = 0
        for state in STATES_CMF:
            bank, idx, nt = banked[(metal, state)]
            covered = [s for s in SEEDS_CMF if abs(s - bank) < 1e-9]
            if len(covered) > 1:
                B.die("%s %s: banked %s matches %d grid members" %
                      (metal, state, bank, len(covered)))
            build = [s for s in SEEDS_CMF if abs(s - bank) > 1e-9]
            for utok in UTOKS_CMF:
                for seed in build:
                    plan.append((metal, state, utok, seed,
                                 stem_of(state, utok, seed)))
                    n_metal += 1
            cov = ("banked %.1f covers m%03d at both endpoints"
                   % (bank, int(round(covered[0] * 100)))) if covered else \
                  ("banked %.1f off-grid, all three seeds build" % bank)
            print("  plan %s %-6s %s" % (metal, state, cov))
        if n_metal != REG_COUNTS[metal]:                           # CMF-a
            B.die("STOP AND FLAG: derived %d %s decks, registered %d -- the "
                  "banked seeds on disk do not reproduce the A11.R3 count"
                  % (n_metal, metal, REG_COUNTS[metal]))
    if len(plan) != REG_TOTAL:                                     # CMF-a
        B.die("STOP AND FLAG: derived total %d != registered 28" % len(plan))
    return plan


def build_one_replace(metal, state, utok, seed, stem):
    """Seed REPLACEMENT off the parent's own bytes; CMF-b/d/f/h fatal."""
    p = parent_path(metal, state, utok)
    ptxt = B.read(p)                                # refuses CR (CMF-h)
    order = B.species_order(ptxt)
    idx = order.index(metal) + 1                    # CMF-b: from THIS deck
    plines = ptxt.splitlines(keepends=True)

    pref_i = [i for i, l in enumerate(plines) if re.match(r"^\s*prefix\s*=", l)]
    if len(pref_i) != 1:
        B.die("%s: %d prefix lines" % (p, len(pref_i)))
    pref_i = pref_i[0]
    seed_i = [i for i, l in enumerate(plines)
              if re.match(MAG_RE, l.rstrip("\n"))
              and int(re.match(MAG_RE, l.rstrip("\n")).group(2)) == idx]
    if len(seed_i) != 1:
        B.die("%s: %d starting_magnetization(%d) lines" % (p, len(seed_i), idx))
    seed_i = seed_i[0]
    for i in (pref_i, seed_i):
        if not plines[i].endswith("\n"):
            B.die("%s: replaced line %d lacks a trailing newline" % (p, i))

    m = re.match(MAG_RE, plines[seed_i].rstrip("\n"))
    if abs(float(m.group(4)) - seed) < 1e-9:
        B.die("%s: cell is covered (banked %s == grid %.2f) yet reached the "
              "build loop" % (stem, m.group(4), seed))
    if not seed > 0.0:                                             # CMF-f
        B.die("%s: non-positive seed %r (FM-uniform-seed only)" % (stem, seed))

    clines = list(plines)
    clines[pref_i] = re.sub(r"=.*$", "= '%s'" % stem,
                            plines[pref_i].rstrip("\n")) + "\n"
    clines[seed_i] = "%sstarting_magnetization(%d)%s%.2f%s\n" % (
        m.group(1), idx, m.group(3), seed, m.group(5))
    ctxt = "".join(clines)
    if not ptxt.endswith("\n"):                                    # CMF-h (A7)
        ctxt = ctxt.rstrip("\n")

    # ---- CMF-d: replacement diff shape, and byte-identity elsewhere ------
    cl = ctxt.splitlines(keepends=True)
    if len(cl) != len(plines):
        B.die("%s: line count changed %d -> %d (insertion leaked in)"
              % (stem, len(plines), len(cl)))
    ops = difflib.SequenceMatcher(None, plines, cl, autojunk=False).get_opcodes()
    ins = sum(o[4] - o[3] for o in ops if o[0] == "insert")
    rep = sum(o[2] - o[1] for o in ops if o[0] == "replace")
    dele = sum(o[2] - o[1] for o in ops if o[0] == "delete")
    if (ins, rep, dele) != (0, 2, 0):
        B.die("%s: diff shape +%d/~%d/-%d, replacement requires +0/~2/-0"
              % (stem, ins, rep, dele))
    changed = sorted(i for i in range(len(plines)) if plines[i] != cl[i])
    if changed != sorted((pref_i, seed_i)):
        B.die("%s: changed lines %r, expected prefix %d + seed %d"
              % (stem, changed, pref_i, seed_i))

    # ---- CMF-f: child block still FM-uniform, one nonzero on the metal ---
    cmags = mag_lines(ctxt)
    nt = B.ntyp_of(ctxt)
    if [s for _, s, _ in cmags] != list(range(1, nt + 1)):
        B.die("%s: child starting_magnetization block malformed" % stem)
    nz = [(s, v) for _, s, v in cmags if float(v) != 0.0]
    if nz != [(idx, "%.2f" % seed)]:
        B.die("%s: child nonzero seeds %r, expected [(%d, '%.2f')]"
              % (stem, nz, idx, seed))
    if not re.search(r"^\s*nspin\s*=\s*2\s*$", ctxt, re.M):
        B.die("%s: nspin=2 lost" % stem)

    # ---- CMF-h: forbidden keys, prefix == stem ---------------------------
    for key in B.FORBIDDEN:
        if re.search(r"^\s*%s\s*=" % re.escape(key), ctxt, re.M) and \
           not re.search(r"^\s*%s\s*=" % re.escape(key), ptxt, re.M):
            B.die("%s: introduced forbidden key %s" % (stem, key))
    pm = re.search(r"^\s*prefix\s*=\s*'([^']+)'", ctxt, re.M)
    if not pm or pm.group(1) != stem:
        B.die("%s: prefix does not equal stem" % stem)

    return ctxt, idx, nt


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
              "registered 28-deck Cr/Mn/Fe set; only --sandbox <dir> is "
              "accepted" % a)

    out_spin = os.path.join(out_root, "runs", "a0", "spin")
    print("LICENSED 2026-08-31 (docs/43 A11.R3 [CR/MN/FE SEED SEARCH]); "
          "submission still gated on the A11.R5 deposit -- this builder only builds.")
    if os.path.normcase(out_root) != os.path.normcase(ROOT):
        print("SANDBOX rebuild into %s (parents/evidence still read from the repo)"
              % out_root)

    # CMF-j snapshot: every parent .in under runs/a0/main/ (all six metals)
    parents = {}
    for d in sorted(os.listdir(B.MAIN)):
        dd = os.path.join(B.MAIN, d)
        if not os.path.isdir(dd):
            continue
        for f in sorted(os.listdir(dd)):
            if f.endswith(".in"):
                pth = os.path.join(dd, f)
                parents[pth] = B.md5(pth)

    banked = rederive_cmf()
    plan = plan_cmf(banked)

    # CMF-g -- no planned stem may collide with banked evidence (any .out under
    # the repo spin tree), and nothing at the output paths may be overwritten
    # (.in or .out). A repo .in for a planned stem is tolerated ONLY in a
    # --sandbox rebuild, where it is this builder's own pass-1 product and the
    # determinism compare is the point.  (S1-c semantics, verbatim.)
    for metal, state, utok, seed, stem in plan:
        pth = os.path.join(B.SPIN, metal, stem + ".out")
        if os.path.exists(pth):
            B.die("stem %s collides with banked evidence %s" % (stem, pth))
        for ext in (".in", ".out"):
            c = os.path.join(out_spin, metal, stem + ext)
            if os.path.exists(c):
                B.die("refusing to overwrite existing child %s" % c)

    rows, deck_md5s, built = [], [], 0
    print("\nCR/MN/FE SEED SEARCH -- 28 seed-replacement decks")
    for metal, state, utok, seed, stem in plan:
        txt, idx, nt = build_one_replace(metal, state, utok, seed, stem)
        if idx != REG_INDEX[metal] or nt != 3:                     # CMF-b
            B.die("%s %s: index %d ntyp %d, adsorbate decks carry the metal at "
                  "%d of 3" % (metal, stem, idx, nt, REG_INDEX[metal]))
        child = os.path.join(out_spin, metal, stem + ".in")
        if not child.replace("\\", "/").endswith(
                "runs/a0/spin/%s/%s.in" % (metal, stem)) or \
                metal not in METALS_CMF or \
                not stem.startswith(("s0_OH__", "s0_OOH__")):      # CMF-i
            B.die("child outside the licensed tree: %s" % child)
        B.write(child, txt)
        rel = "a0/spin/%s/%s.in" % (metal, stem)
        deck_md5s.append((rel, B.md5(child)))
        rows.append(("a0/spin/%s" % metal, stem, NK_CMF[metal]))
        built += 1
        print("  %-2s %-7s %s ntyp=%d index=%d  %s"
              % (metal, state, utok, nt, idx, stem))

    # CMF-j -- the banked tree is read-only by construction
    for pth, h in parents.items():
        if B.md5(pth) != h:
            B.die("PARENT ALTERED: %s" % pth)
    print("\n  CMF-j all %d parent decks unchanged on disk" % len(parents))

    # CMF-i -- licensed tree only
    for d, stem, _nk in rows:
        if d not in ("a0/spin/Cr", "a0/spin/Mn", "a0/spin/Fe"):
            B.die("child outside runs/a0/spin/{Cr,Mn,Fe}: %s" % d)
    print("  CMF-i all %d children under runs/a0/spin/{Cr,Mn,Fe}/" % built)

    # CMF-k -- Ti sweep: this family must not touch Ti. Shared licence-aware
    # sweep (a0spin_ti_licence, 2026-08-31): banked nulls always pass; the 24
    # licensed Ti stems pass iff docs/59 carries the executed licence line.
    import a0spin_ti_licence as TIL
    TIL.ti_sweep(B.die, {os.path.join(B.SPIN, "Ti"), os.path.join(out_spin, "Ti")})
    print("  CMF-k Ti sweep clean (shared licence-aware sweep; this family "
          "wrote nothing under Ti)")

    man = os.path.join(out_root, "runs", "a0", "m_cmf_seed_search.txt")
    hdr = [
        "# CR/MN/FE SEED SEARCH -- the A0-SPIN seed-grid completion on the three",
        "# nspin=2 metals (28 decks). Built 2026-08-31 by",
        "# src/dft/build_cmf_seed_search.py -- READ ITS DOCSTRING (assertions",
        "# CMF-a..CMF-m), the build_a0spin.py docstring, and docs/43 AMENDMENT 11.",
        "#",
        "# LICENSED 2026-08-31 -- docs/43 A11.R3, the dated line [CR/MN/FE SEED SEARCH",
        "# 2026-08-31: RUNS]: \"exactly 28 SCFs (Cr 12: banked seed 0.6 is off-grid in",
        "# every cell; Mn 8: banked 0.5 = m050 covers all four cells; Fe 8: banked",
        "# s0_OH 0.5 and s0_OOH 0.1 cover four cells)\" (elections docs/66 §2 row 12;",
        "# the A11.R5 deposit precedes submission).",
        "# winners enter the a7_3_spin sensitivity census ONLY; no banked A0 row is replaced (§A11.9)",
        "#",
        "# TRANSFORMATION: seed REPLACEMENT, not insertion -- every parent",
        "# runs/a0/main/{Cr,Mn,Fe}/{s0_OH,s0_OOH}__{u000,u900}.in is ALREADY nspin=2",
        "# FM-uniform; each child differs from its parent in EXACTLY 2 lines (prefix +",
        "# starting_magnetization(<metal idx>), the index read from EACH PARENT'S OWN",
        "# ATOMIC_SPECIES: Mn at 2, Cr/Fe at 1 -- asserted, never assumed).",
        "# FM-uniform-seed only; this family never touches the A7.5 Mn AFM condition",
        "# (docs/43:1406-1407 untouched, per the A11.R3 line).",
        "#",
        "# COVERAGE (registered): a banked seed equal to a grid member covers that cell",
        "# AT BOTH ENDPOINTS; banked u900 seeds re-verified identical to u000 at build",
        "# time, off the parents' own starting_magnetization. Derived plan (die-on-drift",
        "# against the registered literals):",
        "#   Cr s0_OH,s0_OOH banked 0.6 off-grid -> m010 m030 m050 x u000/u900 = 12",
        "#   Mn s0_OH,s0_OOH banked 0.5 (=m050)  -> m010 m030      x u000/u900 =  8",
        "#   Fe s0_OH        banked 0.5 (=m050)  -> m010 m030      x u000/u900 =  4",
        "#   Fe s0_OOH       banked 0.1 (=m010)  -> m030 m050      x u000/u900 =  4",
        "#",
        "# SELECTION (A11.6-ANALOGUE, registered): lowest converged total energy per",
        "# (metal, state, U) across the grid seeds AND the banked FM row as incumbent",
        "# (no nspin=1 floor on these metals; incumbent .out convergence verified at",
        "# build time), ties within 1 meV to the smallest |seed|.",
        "#",
        "# deck md5s (an independent rebuild must reproduce these byte-for-byte):",
    ] + ["# md5 %s %s" % (h, rel) for rel, h in deck_md5s] + [
        "#",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223",
        "# (submit-time list additionally + a120,a200 per [EXCLUDE EXTENDED 2026-08-31], docs/66 §4)",
        "#",
        "# row: dir job suffix nk",
        "# NP=128 NCONC=1",
    ]
    if sum(1 for l in hdr if l == "# NP=128 NCONC=1") != 1:
        B.die("manifest must carry exactly one '# NP=128 NCONC=1' line")
    if sum(1 for l in hdr if l.startswith("# SUBMIT WITH EXCLUDE=")) != 1:
        B.die("manifest must carry exactly one EXCLUDE header")
    if not any("a120,a200" in l for l in hdr):
        B.die("manifest must carry the docs/66 §4 submit-time EXCLUDE note")
    if not any("[CR/MN/FE SEED SEARCH" in l for l in hdr):
        B.die("manifest must cite the licensing A11.R3 line")
    if not any("winners enter the a7_3_spin sensitivity census ONLY" in l
               for l in hdr):
        B.die("manifest must carry the §A11.9 winners-only sentence")
    body = ["%s %s .in %d" % (d, s_, nk) for d, s_, nk in rows]
    for r in body:
        if len(r.split()) != 4:
            B.die("manifest row %r is not the 4-field grammar" % r)
    B.write(man, "\n".join(hdr + body) + "\n")
    print("  wrote %s (%d rows)" % (os.path.relpath(man, out_root), len(rows)))
    print("\nBUILD OK -- %d decks, 0 relaxations, 0 parents touched. "
          "Submission gated on the A11.R5 deposit." % built)


if __name__ == "__main__":
    main(sys.argv[1:])
