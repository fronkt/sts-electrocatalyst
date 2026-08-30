#!/usr/bin/env python3
"""A0-SPIN: spin-treatment equalisation on the three nspin = 1 metals (Ru, Ir, Ti).

READ docs/61-amendment-11-DRAFT.md. This docstring is the build-side registration;
the amendment is the scoring-side registration. Both are committed BEFORE any deck
of this arm is submitted.

WHY THIS ARM EXISTS
-------------------
A7.3 (P-FLOOR-U) scored NOT MET at 3 of 6 against a registered >=4, and the audit
found the over/under split is PERFECTLY confounded with the spin convention: the
three metals over the 0.10 V floor are exactly the three whose A0 decks carry
nspin = 2, and the three under it are exactly the three that run nonmagnetic
(banked, fa46611, a7_3.conditionality.spin_confound.perfectly_confounded = true).
This arm runs the three nonmagnetic metals under nspin = 2 at FIXED GEOMETRY so
the confound can be priced.

WHAT CAN AND CANNOT MOVE (registered, A11.1)
--------------------------------------------
A7.3's quantity is span(c_M)/2 at FIXED endpoints, so

    Delta[span/2] = -D_M / 2,   D_M = Delta_c_M(U_max) - Delta_c_M(0)

A U-INDEPENDENT spin offset cancels EXACTLY. The arm can move A7.3 only through the
U-DEPENDENCE of the spin effect, never through its size. Measured at U = 0 from the
eight banked P11 SCFs (runs/probe/{Ru,Ir}_spin/, geometry byte-identical to the A0
u000 decks): Delta_c_M(0) = +7.145 meV on Ru, -8.705 meV on Ir, while individual
state energies move up to 174 meV. Ru crosses the floor iff Delta_c_M(9.0) <= -8.35
meV. Honest expectation, registered before the data: this PRICES the confound rather
than overturning it, and the as-built 3-of-6 stays the headline (A11.5).

THE BLOCKER THIS BUILDER EXISTS TO PREVENT
------------------------------------------
The metal's species index is STATE-DEPENDENT, not metal-dependent. qe_slab.py sorts
species alphabetically with O last:

    slab, s0_O    -> ntyp 2, [M, O]      -> metal at index 1
    s0_OH, s0_OOH -> ntyp 3, [H, M, O]   -> metal at index 2   (Ru/Ir/Ti/Mn)

A per-metal constant seeds OXYGEN on half of every ladder and silently returns the
nspin = 1 answer at twice the cost. ASSERTION A1 reads the index out of each deck's
own ATOMIC_SPECIES block and refuses the build otherwise. The same trap applies to
nosym/noinv, which Ru and Ir carry on `slab` but NOT on the adsorbate states -- so
the insertion anchor is the `/` closing &SYSTEM, never a symmetry line.

BUILD-TIME ASSERTIONS (all fatal)
---------------------------------
A1  index read from this deck's own ATOMIC_SPECIES; emitted nonzero index == it
A2  exactly ntyp starting_magnetization lines, contiguous 1..ntyp, zeros explicit
A3  exactly one nonzero seed, and it is not 0.0 (the two __sp2null control decks
    are the only whitelisted exemption -- by stem, never by silence)
A4  line-diff shape: inserted == 1 + ntyp, replaced == 1, deleted == 0
A5  the one replaced line is the prefix line and differs only in the stem
A6  prefix == stem == basename (46_a0.slurm rm -rf's dens/${prefix}.save; a
    colliding prefix silently wipes a banked density the repair path names)
A7  trailing-newline and CR bytes preserved from the parent
A8  insertion immediately before the `/` closing &SYSTEM; nosym/noinv unchanged
    in presence, value and position, and above the inserted block
A9  everything else byte-identical (HUBBARD card, K_POINTS, CELL_PARAMETERS,
    ATOMIC_POSITIONS incl. constraint flags, ATOMIC_SPECIES, masses, UPFs)
A10 no forbidden key introduced (tot_magnetization and nbnd are the two a
    well-meaning builder reaches for on the odd-electron states; smearing
    handles the odd count and both would constrain what we are measuring)
A11 every parent under runs/a0/main/ unchanged on disk after the build
A12 every child path under runs/a0/spin/, never runs/a0/main/

POST-RUN assertions (A13-A17: k-set, electron count, variational floor, endpoint
branch continuity, Stage-0 control pass) live in the readout, not here.

STAGING
-------
Stage 0 (10 jobs) is machinery only and gates everything else: 8 decks that must
reproduce the banked P11 energies, plus 2 null-seed decks -- deliberately one of
EACH ntyp class -- that must reproduce the banked nspin = 1 Ti energies at totmag
~ 0. An all-ntyp-3 control set is structurally blind to the index rule.

Ti is HELD beyond Stage 0 until docs/59 s3c is countersigned: it sets the
denominator this arm is scored against (A11.10).
"""
from __future__ import annotations

import difflib
import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAIN = os.path.join(ROOT, "runs", "a0", "main")
SPIN = os.path.join(ROOT, "runs", "a0", "spin")
PROBE = os.path.join(ROOT, "runs", "probe")

METALS = ("Ru", "Ir", "Ti")
STATES = ("slab", "s0_O", "s0_OH", "s0_OOH")
NK = {"Ru": 4, "Ir": 4, "Ti": 8}

#: PROPOSED seed set (A11.6) -- the entrant's to re-author before deposit.
SEEDS = (0.10, 0.30, 0.50)

#: Keys no deck of this arm may introduce (A10).
FORBIDDEN = ("startingpot", "startingwfc", "input_dft", "tefield", "dipfield",
             "assume_isolated", "constrained_magnetization", "tot_magnetization",
             "nbnd", "lda_plus_u", "restart_mode")

#: Banked P11 references the Stage-0 C1 decks must reproduce (Ry). Re-derived by
#: rederive(); never trusted from this literal alone.
P11_REF = {
    ("Ru", "slab"): -1630.67301371, ("Ru", "s0_O"): -1672.26143725,
    ("Ru", "s0_OH"): -1673.53455401, ("Ru", "s0_OOH"): -1715.01193102,
    ("Ir", "slab"): -1589.74818250, ("Ir", "s0_O"): -1631.35200572,
    ("Ir", "s0_OH"): -1632.64860176, ("Ir", "s0_OOH"): -1674.09243750,
}

RY_EV = None  # set from qe_qc in main(); never hard-coded here


def die(msg: str) -> None:
    sys.exit("BUILD REFUSED: " + msg)


def read(path: str) -> str:
    """Read preserving line endings exactly; refuse CRLF (the driver does too)."""
    with io.open(path, encoding="utf-8", newline="") as fh:
        txt = fh.read()
    if "\r" in txt:
        die("%s contains CR bytes" % path)
    return txt


def write(path: str, txt: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)


def md5(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def energy_ry(path: str):
    txt = io.open(path, encoding="utf-8", errors="replace").read()
    if "JOB DONE" not in txt or "convergence NOT achieved" in txt:
        return None
    hits = re.findall(r"^!\s+total energy\s+=\s+(-?\d+\.\d+)\s+Ry", txt, re.M)
    return float(hits[-1]) if hits else None


# --------------------------------------------------------------------------
# deck anatomy
# --------------------------------------------------------------------------

def species_order(txt: str):
    """ATOMIC_SPECIES symbols in file order. The ONLY source of the index (A1)."""
    out, on = [], False
    for ln in txt.split("\n"):
        s = ln.strip()
        if s.startswith("ATOMIC_SPECIES"):
            on = True
            continue
        if on:
            if not s or s.split()[0] in ("CELL_PARAMETERS", "ATOMIC_POSITIONS",
                                         "K_POINTS", "HUBBARD"):
                break
            out.append(s.split()[0])
    return out


def system_close_index(lines):
    """Index of the `/` line closing &SYSTEM -- the only legal insertion anchor."""
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().upper().startswith("&SYSTEM"):
            start = i
            break
    if start is None:
        die("no &SYSTEM namelist")
    for j in range(start + 1, len(lines)):
        if lines[j].strip() == "/":
            return j
    die("&SYSTEM is not closed by a bare '/'")


def ntyp_of(txt: str) -> int:
    m = re.search(r"^\s*ntyp\s*=\s*(\d+)", txt, re.M)
    if not m:
        die("no ntyp")
    return int(m.group(1))


# --------------------------------------------------------------------------
# the transformation
# --------------------------------------------------------------------------

def spin_block(order, metal, seed):
    """The lines to insert. Zeros are written EXPLICITLY (A2) -- this is the
    qe_slab.py convention the Cr/Mn/Fe comparator decks use."""
    if metal not in order:
        die("%s not in ATOMIC_SPECIES %r" % (metal, order))
    idx = order.index(metal) + 1                                   # A1
    out = ["  nspin = 2"]
    for i, sym in enumerate(order, start=1):
        val = seed if i == idx else 0.0
        out.append("  starting_magnetization(%d) = %s"
                   % (i, ("%.1f" % val) if val in (0.0,) else ("%.2f" % val)))
    return out, idx


def build_one(metal, state, utok, seed, stem, null=False):
    parent = os.path.join(MAIN, metal, "%s__%s.in" % (state, utok))
    if not os.path.exists(parent):
        die("no parent deck %s" % parent)
    ptxt = read(parent)
    order = species_order(ptxt)
    nt = ntyp_of(ptxt)
    if len(order) != nt:
        die("%s: ntyp %d but %d species" % (parent, nt, len(order)))

    plines = ptxt.splitlines(keepends=True)
    close = system_close_index([l.rstrip("\n") for l in plines])

    if null:
        block = ["  nspin = 2"] + ["  starting_magnetization(%d) = 0.0" % i
                                   for i in range(1, nt + 1)]
        idx = None
    else:
        block, idx = spin_block(order, metal, seed)

    # A3 -- exactly one nonzero seed, and not 0.0; null decks whitelisted by stem
    nz = [b for b in block if "starting_magnetization" in b
          and float(b.split("=")[1]) != 0.0]
    if null:
        if not stem.endswith("__sp2null"):
            die("null deck stem must end __sp2null: %s" % stem)
        if nz:
            die("null control %s has a nonzero seed" % stem)
    else:
        if len(nz) != 1:
            die("%s: %d nonzero seeds, need exactly 1" % (stem, len(nz)))

    clines = list(plines)
    clines[close:close] = [b + "\n" for b in block]

    # the prefix line (A5)
    done = False
    for i, ln in enumerate(clines):
        if re.match(r"^\s*prefix\s*=", ln):
            clines[i] = re.sub(r"=.*$", "= '%s'" % stem, ln.rstrip("\n")) + "\n"
            done = True
            break
    if not done:
        die("%s: no prefix line" % parent)

    ctxt = "".join(clines)
    if not ptxt.endswith("\n"):                                     # A7
        ctxt = ctxt.rstrip("\n")

    # ---- A4: line-diff shape -------------------------------------------
    ops = difflib.SequenceMatcher(None, plines, ctxt.splitlines(keepends=True),
                                  autojunk=False).get_opcodes()
    ins = sum(o[4] - o[3] for o in ops if o[0] == "insert")
    rep = sum(o[2] - o[1] for o in ops if o[0] == "replace")
    dele = sum(o[2] - o[1] for o in ops if o[0] == "delete")
    if (ins, rep, dele) != (1 + nt, 1, 0):
        die("%s: diff shape +%d/~%d/-%d, expected +%d/~1/-0"
            % (stem, ins, rep, dele, 1 + nt))

    # ---- A8/A9: everything outside the inserted block is byte-identical --
    stripped = [l for l in ctxt.splitlines(keepends=True)
                if not re.match(r"^\s*(nspin|starting_magnetization\()", l)]
    if "".join(stripped) != re.sub(r"(?m)^(\s*prefix\s*=).*$",
                                   lambda m: m.group(1) + " '%s'" % stem, ptxt):
        die("%s: a line outside the spin block changed" % stem)

    # ---- A10 -------------------------------------------------------------
    for key in FORBIDDEN:
        if re.search(r"^\s*%s\s*=" % re.escape(key), ctxt, re.M) and \
           not re.search(r"^\s*%s\s*=" % re.escape(key), ptxt, re.M):
            die("%s: introduced forbidden key %s" % (stem, key))

    # ---- A6 --------------------------------------------------------------
    m = re.search(r"^\s*prefix\s*=\s*'([^']+)'", ctxt, re.M)
    if not m or m.group(1) != stem:
        die("%s: prefix does not equal stem" % stem)

    return ctxt, idx, nt


# --------------------------------------------------------------------------
# re-derivation of every docstring claim (dies on disagreement)
# --------------------------------------------------------------------------

def rederive():
    print("REDERIVE -- every claim below is read off disk, not trusted")

    # the state-dependent index, the whole reason this builder exists
    for m in METALS:
        for st in STATES:
            p = os.path.join(MAIN, m, "%s__u000.in" % st)
            order = species_order(read(p))
            idx = order.index(m) + 1
            want = 1 if st in ("slab", "s0_O") else 2
            if idx != want:
                die("index rule broken: %s %s -> %r gives %d, expected %d"
                    % (m, st, order, idx, want))
    print("  A1 index rule holds on all %d decks (slab/s0_O -> 1, "
          "s0_OH/s0_OOH -> 2)" % (len(METALS) * len(STATES)))

    # nosym/noinv is state-dependent on Ru and Ir
    for m in ("Ru", "Ir"):
        sl = read(os.path.join(MAIN, m, "slab__u000.in"))
        ad = read(os.path.join(MAIN, m, "s0_OOH__u000.in"))
        if not ("nosym" in sl and "nosym" not in ad):
            die("%s: nosym pattern is not slab-only as recorded" % m)
    print("  nosym/noinv confirmed slab-only on Ru and Ir")

    # the banked P11 arm, and Delta c_M at U = 0
    for (m, st), ref in sorted(P11_REF.items()):
        p = os.path.join(PROBE, "%s_spin" % m, "%s__spin0.5.out" % st)
        e = energy_ry(p)
        if e is None:
            die("banked P11 run missing or unconverged: %s" % p)
        if abs(e - ref) > 1e-6:
            die("%s %s: banked %.8f != docstring %.8f" % (m, st, e, ref))
    print("  8 banked P11 nspin=2 energies reproduce the registered literals")

    for m in ("Ru", "Ir"):
        for st in STATES:
            a = os.path.join(PROBE, "%s_spin" % m, "%s__spin0.5.in" % st)
            b = os.path.join(MAIN, m, "%s__u000.in" % st)
            ga = re.search(r"ATOMIC_POSITIONS.*?(?=\nK_POINTS)", read(a), re.S)
            gb = re.search(r"ATOMIC_POSITIONS.*?(?=\nK_POINTS)", read(b), re.S)
            if not ga or not gb or ga.group(0) != gb.group(0):
                die("%s %s: P11 geometry is NOT byte-identical to the A0 u000 deck"
                    % (m, st))
    print("  P11 geometries byte-identical to the A0 u000 decks (8/8)")

    for m in ("Ru", "Ir"):
        o2 = energy_ry(os.path.join(PROBE, "%s_spin" % m, "s0_OOH__spin0.5.out"))
        h2 = energy_ry(os.path.join(PROBE, "%s_spin" % m, "s0_OH__spin0.5.out"))
        o1 = energy_ry(os.path.join(MAIN, m, "s0_OOH__u000.out"))
        h1 = energy_ry(os.path.join(MAIN, m, "s0_OH__u000.out"))
        d = ((o2 - h2) - (o1 - h1)) * RY_EV * 1000
        print("  Delta c_M(0) %s = %+.3f meV" % (m, d))
        if m == "Ru" and not (7.0 < d < 7.3):
            die("Ru Delta c_M(0) = %.3f, docstring says +7.145" % d)
        if m == "Ir" and not (-8.8 < d < -8.6):
            die("Ir Delta c_M(0) = %.3f, docstring says -8.705" % d)


# --------------------------------------------------------------------------

def main():
    global RY_EV
    sys.path.insert(0, HERE)
    import qe_qc
    RY_EV = qe_qc.RY_EV

    parents = {}
    for m in METALS:
        for f in os.listdir(os.path.join(MAIN, m)):
            if f.endswith(".in"):
                p = os.path.join(MAIN, m, f)
                parents[p] = md5(p)

    rederive()

    rows, built = [], 0
    print("\nSTAGE 0 -- machinery controls (10 jobs); gates everything else")

    # C1: the eight that must reproduce the banked P11 energies. Seed 0.50 is
    # P11's own seed, so these are also this arm's production U=0 rungs.
    for m in ("Ru", "Ir"):
        for st in STATES:
            stem = "%s__u000__sp2m050" % st
            txt, idx, nt = build_one(m, st, "u000", 0.50, stem)
            write(os.path.join(SPIN, m, stem + ".in"), txt)
            rows.append(("a0/spin/%s" % m, stem, NK[m]))
            built += 1
            print("  %-3s %-7s ntyp=%d index=%d  %s" % (m, st, nt, idx, stem))

    # C2: null-seed controls, deliberately ONE OF EACH ntyp CLASS. An
    # all-ntyp-3 control set is structurally blind to the index rule.
    for st in ("slab", "s0_OOH"):
        stem = "%s__u900__sp2null" % st
        txt, idx, nt = build_one("Ti", st, "u900", 0.0, stem, null=True)
        write(os.path.join(SPIN, "Ti", stem + ".in"), txt)
        rows.append(("a0/spin/Ti", stem, NK["Ti"]))
        built += 1
        print("  Ti  %-7s ntyp=%d NULL-SEED     %s" % (st, nt, stem))

    # A11 -- the banked tree is read-only by construction
    for p, h in parents.items():
        if md5(p) != h:
            die("PARENT ALTERED: %s" % p)
    print("\n  A11 all %d parent decks unchanged on disk" % len(parents))

    # A12 -- sibling tree only
    for d, stem, _nk in rows:
        if not d.startswith("a0/spin/"):
            die("child outside runs/a0/spin: %s" % d)
    print("  A12 all %d children under runs/a0/spin/" % built)

    man = os.path.join(ROOT, "runs", "a0", "m_a0spin_s0.txt")
    hdr = [
        "# A0-SPIN STAGE 0 -- machinery controls. Built 2026-08-29 by",
        "# src/dft/build_a0spin.py -- READ ITS DOCSTRING and docs/61 (Amendment 11).",
        "#",
        "# 8 jobs must reproduce the banked P11 nspin=2 energies at",
        "# runs/probe/{Ru,Ir}_spin/<state>__spin0.5.out (also a cross-machine",
        "# determinism control on a spin-polarised code path, which this campaign",
        "# does not otherwise have). 2 null-seed decks -- ONE OF EACH ntyp CLASS --",
        "# must reproduce the banked nspin=1 Ti energies at totmag ~ 0; an",
        "# all-ntyp-3 control set would be structurally blind to the index rule.",
        "#",
        "# NOTHING HERE IS A SCORED A7.3 ROW. Stage 1 is held until these are read,",
        "# and Ti beyond this stage is held until docs/59 s3c is countersigned.",
        "#",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223",
        "#",
        "# row: dir job suffix nk",
        "# NP=128 NCONC=1",
    ]
    body = ["%s %s .in %d" % (d, s, nk) for d, s, nk in rows]
    write(man, "\n".join(hdr + body) + "\n")
    print("  wrote %s (%d rows)" % (os.path.relpath(man, ROOT), len(rows)))
    print("\nBUILD OK -- %d decks, 0 relaxations, 0 parents touched." % built)


if __name__ == "__main__":
    main()
