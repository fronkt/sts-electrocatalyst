#!/usr/bin/env python3
"""MN-AFM-ORDER stage 1: the A7.5 Mn AFM ordering measurement (4 decks, 2x1 frame).

LICENSED: docs/43 A11.R3 line "[MN AFM ARM 2026-08-31: IN SCOPE]" -- "Staged program and triggers per docs/67 SS5: MN-AFM-ORDER 4 (licensed now)"; that line IS the arm's licence (docs/43:2008 excludes any AFM deck in 1x1 from the gate-(h) licence, so nothing prior covers this family). Design of record: docs/67 (elections E1-E7). Submission additionally waits on the docs/43 A11.R5 Zenodo deposit; this builder builds, banks nothing.

READ src/dft/build_a0spin_s1.py FIRST: this builder is written in its style
(fatal assertions, collision/overwrite semantics, sandbox determinism
rebuild) for a different parent family, so its helpers are re-derived here
against the Mn slab anatomy rather than imported from build_a0spin (whose
plan, species map and rederive() are Ru/Ir/Ti-specific by construction).

WHAT THIS BUILDS (docs/67 SS4 E1/E2/E4, SS5 row MN-AFM-ORDER)
-------------------------------------------------------------
Four fixed-geometry SCF decks under runs/s0/mn_afm/ (a NEW tree -- never
runs/a0/main/, docs/61:89-90), all at U(Mn-3d) = 3.9 eV (u390), all on the
SAME 36-atom geometry: the banked FM production slab
runs/a0/main/Mn/slab__u390.in (frozen evidence, .out converged at
-1766.35807781 Ry) tiled x2 along its 2.876 A in-plane lattice vector.
Which vector that is is READ from the parent's own CELL_PARAMETERS (the
unique in-plane vector of length ~2.876 A -- the rutile [001] chain axis,
docs/67 SS3) and asserted to be v1 = (2.876, 0, 0) -> (5.752, 0, 0).
Atom order: the 18 parent atoms at their original coordinates (cell copy
n = 0, byte-identical x/y/z/if_pos columns), then the same 18 shifted by
+2.876 A in x (cell copy n = 1) -- the runs/s0/h_afm_anchor block-tiling
convention. K_POINTS 4 4 1 (docs/67 E2: halved along the doubled axis;
the banked 1x1 mesh is 9 4 1, odd n1, so no 2x1 mesh folds onto it and
stage 1 makes no cross-cell claim). nosym = .true. / noinv = .true. are
carried from the parent -- the same convention the split-sublattice
h_afm_anchor decks use (verified there before this was written).

THE FOUR SPIN PATTERNS (species labels assigned FROM COORDINATES)
-----------------------------------------------------------------
Geometry first, spins second: every deck's ATOMIC_POSITIONS coordinates are
identical; only the species column and the spin machinery differ.

Derived per Mn atom, from its child-frame coordinates alone (a = 2.876):
  cell copy   n(atom) = 0 if x <= 0.75*a else 1     (no Mn sits within
              0.2 A of the 0.75*a boundary -- asserted, else STOP)
  comb        r = x - n*a; CORNER if |r| < 0.05 A, BODY if |r - a/2| <
              0.05 A, else STOP (docs/67 SS2's x-mod-2.876 clustering;
              corner comb x ~ 0, body-centre comb x ~ a/2)
  chain       Mn atoms sharing (y, z) to < 1e-3 A; exactly 6 chains of
              exactly 2 members (n = 0 and n = 1), x-split exactly a --
              the edge-sharing octahedral chains along [001]

  slab__2x1__fm       all 12 Mn up (+0.5), single species 'Mn' -- the
                      in-frame E4 FM reference.
  slab__2x1__afm_pa   P-A, rutile-sublattice AFM (MnF2-type, the gate-(h)
                      Ru template): CORNER comb up, BODY comb down;
                      intra-chain FM.
  slab__2x1__afm_pb1  P-B registry B1, intra-chain AFM: in EVERY chain the
                      n = 0 member is up and the n = 1 member is down --
                      both combs' alternation phases ALIGNED in the frame
                      anchored at x = 0 (spin(atom) = up iff n = 0).
  slab__2x1__afm_pb2  P-B registry B2, intra-chain AFM: corner-comb chains
                      keep the B1 phase (up at n = 0); body-comb chains
                      take the OPPOSITE phase (up at n = 1). spin = up iff
                      (comb = CORNER and n = 0) or (comb = BODY and n = 1).
  B1 and B2 are the two inter-chain phase registries: translating a period-2
  chain pattern by a flips every chain's phase at once, so only the
  RELATIVE phase between the two combs distinguishes patterns -- aligned
  (B1) or anti-aligned (B2) -- and the assignment above is deterministic
  from coordinates.

In the three AFM decks the up sublattice is species 'Mn1' (seed +0.5) and
the down sublattice 'Mn2' (seed -0.5), h_afm_anchor's labelling; both carry
the SAME mass and pseudopotential bytes as the parent's Mn line, and the
HUBBARD card carries BOTH 'U Mn1-3d 3.9000' AND 'U Mn2-3d 3.9000' (a
one-label card silently leaves a sublattice at U = 0 -- the trap the Ru
probe build caught; docs/67 E7). Everything not enumerated here is
byte-identical to the tiled parent: same &CONTROL (calculation = 'scf'),
same &ELECTRONS, same convergence numerics, same if_pos columns.

The magnetic species is never a constant: it is read from the parent's own
ATOMIC_SPECIES as the unique species with a nonzero starting_magnetization,
then cross-checked against docs/67 (label 'Mn', seed +0.5) -- any mismatch
STOPS the build rather than guessing.

WHAT IS FATAL (MN-a parent anatomy, MN-b build, MN-c manifest)
--------------------------------------------------------------
MN-a1  parent .in exists, LF-only; its .out sibling is banked AND converged
MN-a2  parent is scf / nspin 2 / nosym+noinv; nat = 18 = position count;
       ntyp = 2 = species count
MN-a3  exactly one magnetic species, seed +0.5, label 'Mn'
MN-a4  parent HUBBARD card is exactly one line, 'U Mn-3d 3.9000'
MN-a5  parent K_POINTS automatic 9 4 1 0 0 0 (docs/67 SS2's banked mesh)
MN-a6  exactly one lattice vector has |v| ~ 2.876 A; it is v1, exactly
       in-plane along x; no other vector within 0.1 A of it
MN-a7  parent Mn count 6, comb split exactly 3 + 3 (an odd comb count
       cannot form the half/half patterns -> STOP, per the build order)
MN-a8  exactly 6 chains of exactly 2 Mn each in the 2x1, x-split = a
MN-b1  the plan is exactly the four registered stems, in docs/67 order
MN-b2  no planned stem collides with banked evidence (a .out under the
       repo's runs/s0/mn_afm/) and nothing at the output paths is ever
       overwritten; a repo .in for a planned stem is tolerated ONLY under
       --sandbox (it is this builder's own pass-1 product)
MN-b3  per deck: nat 36 = 2 x parent 18; FM 12 Mn / 24 O; AFM 6 Mn1 /
       6 Mn2 / 24 O -- the split is exactly half up, half down
MN-b4  P-A: every Mn1 on the corner comb, every Mn2 on the body comb
MN-b5  P-B1/P-B2: every chain carries exactly one Mn1 and one Mn2; B1 up
       set = {n=0}; B2 up set = corner{n=0} + body{n=1}; B1 != B2
MN-b6  all four decks' x/y/z/if_pos columns are byte-identical, line by line
MN-b7  every Mn-family species label in each deck's own ATOMIC_SPECIES
       appears exactly once in that deck's HUBBARD card at 3.9000
MN-b8  byte-minimality: outside the enumerated edits (prefix, nat, ntyp,
       starting_magnetization block, ATOMIC_SPECIES Mn line(s), species
       column, CELL v1, K_POINTS mesh, HUBBARD labels) every line equals
       the parent's, in parent order
MN-b9  every written file is LF-only; deck trailing-newline convention
       matches the parent byte-for-byte
MN-b10 every banked file under runs/a0/main/Mn/ is md5-unchanged by the
       build (the A11 sweep of build_a0spin, re-derived here)
MN-c1  manifest: exactly one '# NP=128 NCONC=1' line; exactly one
       '# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223' line
       plus the '(submit-time list additionally + a120,a200 per docs/66
       SS4)' note; the string 'NOT LICENSED' appears NOWHERE (docs/66 SS4
       guard 1 refuses such manifests)
MN-c2  manifest rows: exactly 4, exactly 4 fields each ('dir job suffix
       nk' -- trailing fields are fatal in anvil/47_submit_a0.sh), dir
       s0/mn_afm, suffix .in, nk 4 with NP=128 % nk == 0
MN-c3  manifest '# md5' lines match the written decks, recomputed from disk
MN-c4  manifest header carries the A11.R3 licence quote, the E4 adoption
       rule VERBATIM, and 'firewalled from A7.2/A7.3'

USAGE
-----
    python src/dft/build_mn_afm_order.py                  # build into the repo
    python src/dft/build_mn_afm_order.py --sandbox DIR    # independent rebuild
                                                          # (determinism check;
                                                          # parents still read
                                                          # from the repo)

Any other argument is refused. Determinism proof: two --sandbox rebuilds and
the repo build must agree md5-for-md5 on all five files.
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

PARENT = os.path.join(ROOT, "runs", "a0", "main", "Mn", "slab__u390.in")
PARENT_DIR = os.path.dirname(PARENT)
OUT_REL = os.path.join("runs", "s0", "mn_afm")
MAN_REL = os.path.join("runs", "s0", "m_mn_afm_order.txt")

NP = 128
NK = 4                      # manifest nk (docs/43 A11.R3 pre-states nk 4 for the arm)
KMESH_CHILD = (4, 4, 1)     # docs/67 E2 -- halved along the doubled axis
KMESH_PARENT = (9, 4, 1)    # docs/67 SS2 -- the banked 1x1 production mesh
A_TARGET = 2.876            # A -- the rutile [001] axis docs/67 E2 doubles
EXCLUDE = "a024,a049,a050,a088,a196,a220,a223"
E4_RULE = (">20 meV lower -> AFM ADOPTED; |dE|<=20 -> MULTISTABLE; "
           "collapse/higher -> measured null, FM stands")

#: (stem, pattern) in docs/67 SS4 E1 order. Pattern semantics live in spin_of().
PLAN = (
    ("slab__2x1__fm", "fm"),
    ("slab__2x1__afm_pa", "pa"),
    ("slab__2x1__afm_pb1", "pb1"),
    ("slab__2x1__afm_pb2", "pb2"),
)


def die(msg: str) -> None:
    sys.exit("BUILD REFUSED: " + msg)


def read(path: str) -> str:
    with io.open(path, encoding="utf-8", newline="") as fh:
        txt = fh.read()
    if "\r" in txt:
        die("%s contains CR bytes" % path)
    return txt


def write(path: str, txt: str) -> None:
    if "\r" in txt:
        die("refusing to write CR bytes into %s" % path)
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
# parent anatomy (MN-a)
# --------------------------------------------------------------------------

def parse_parent(txt: str):
    """Parse + assert the banked Mn slab deck; return its anatomy dict."""
    lines = txt.split("\n")

    def only(pred, what):
        hits = [i for i, l in enumerate(lines) if pred(l)]
        if len(hits) != 1:
            die("parent: expected exactly one %s line, found %d" % (what, len(hits)))
        return hits[0]

    i_calc = only(lambda l: l.startswith("  calculation ="), "calculation")
    if lines[i_calc] != "  calculation = 'scf'":                      # MN-a2
        die("parent calculation is not 'scf': %r" % lines[i_calc])
    i_prefix = only(lambda l: l.startswith("  prefix ="), "prefix")
    i_nat = only(lambda l: l.startswith("  nat ="), "nat")
    i_ntyp = only(lambda l: l.startswith("  ntyp ="), "ntyp")
    only(lambda l: l == "  nosym = .true.", "nosym")                  # MN-a2
    only(lambda l: l == "  noinv = .true.", "noinv")                  # MN-a2
    only(lambda l: l == "  nspin = 2", "nspin")                       # MN-a2
    nat = int(lines[i_nat].split("=")[1])
    ntyp = int(lines[i_ntyp].split("=")[1])

    sm_idx = [i for i, l in enumerate(lines)
              if l.startswith("  starting_magnetization(")]
    if not sm_idx:
        die("parent carries no starting_magnetization lines")
    if sm_idx != list(range(sm_idx[0], sm_idx[0] + len(sm_idx))):
        die("parent starting_magnetization lines are not contiguous")
    sm = {}
    for i in sm_idx:
        m = re.match(r"^  starting_magnetization\((\d+)\) = (\S+)$", lines[i])
        if not m:
            die("unparseable sm line: %r" % lines[i])
        sm[int(m.group(1))] = m.group(2)
    if sorted(sm) != list(range(1, ntyp + 1)):
        die("parent sm indices %s do not cover 1..ntyp=%d" % (sorted(sm), ntyp))

    i_spec = only(lambda l: l == "ATOMIC_SPECIES", "ATOMIC_SPECIES")
    i_cell = only(lambda l: l == "CELL_PARAMETERS angstrom", "CELL_PARAMETERS")
    i_pos = only(lambda l: l == "ATOMIC_POSITIONS angstrom", "ATOMIC_POSITIONS")
    i_kpt = only(lambda l: l == "K_POINTS automatic", "K_POINTS")
    i_hub = only(lambda l: l == "HUBBARD (atomic)", "HUBBARD")
    if not (i_spec < i_cell < i_pos < i_kpt < i_hub):
        die("parent card order is not SPECIES<CELL<POSITIONS<KPOINTS<HUBBARD")

    species = []   # (label, rest-of-line) in file order -- THE index source
    for l in lines[i_spec + 1:i_spec + 1 + ntyp]:
        m = re.match(r"^  (\S+)(  .+)$", l)
        if not m:
            die("unparseable species line: %r" % l)
        species.append((m.group(1), m.group(2)))
    if len(species) != ntyp:
        die("parent ATOMIC_SPECIES count %d != ntyp %d" % (len(species), ntyp))

    cell = []
    for l in lines[i_cell + 1:i_cell + 4]:
        cell.append([float(t) for t in l.split()])

    pos = []       # (species, x_float, y_tok, z_tok, tail, sep) per atom
    for l in lines[i_pos + 1:i_pos + 1 + nat]:
        m = re.match(r"^  (\S+)(  )(-?\d+\.\d{8})(  \S.*)$", l)
        if not m:
            die("unparseable position line: %r" % l)
        pos.append((m.group(1), m.group(3), m.group(4)))
    if len(pos) != nat:                                               # MN-a2
        die("parent position count %d != nat %d" % (len(pos), nat))
    if nat != 18 or ntyp != 2:
        die("parent is not the banked 18-atom / 2-species Mn slab "
            "(nat=%d ntyp=%d)" % (nat, ntyp))

    kline = lines[i_kpt + 1]
    km = [int(t) for t in kline.split()]
    if tuple(km[:3]) != KMESH_PARENT or km[3:] != [0, 0, 0]:          # MN-a5
        die("parent K_POINTS %r is not the banked 9 4 1 0 0 0" % kline)

    hub = [l for l in lines[i_hub + 1:] if l.strip()]
    if len(hub) != 1:                                                 # MN-a4
        die("parent HUBBARD card has %d U lines, expected exactly 1" % len(hub))
    hm = re.match(r"^U (\S+)-(\S+) (\d\.\d{4})$", hub[0])
    if not hm:
        die("unparseable parent HUBBARD line: %r" % hub[0])

    # MN-a3 -- the magnetic species, from the parent's own sm + ATOMIC_SPECIES
    magnetic = [i for i in sorted(sm) if float(sm[i]) != 0.0]
    if len(magnetic) != 1:
        die("parent has %d magnetic species, expected exactly 1" % len(magnetic))
    mag_i = magnetic[0]
    mag_label = species[mag_i - 1][0]
    if sm[mag_i] != "0.5":
        die("parent magnetic seed %r != the banked FM 0.5" % sm[mag_i])
    if mag_label != "Mn":
        die("STOP: parent magnetic species is %r, docs/67 registers Mn -- "
            "not guessing" % mag_label)
    if hm.group(1) != mag_label or hm.group(2) != "3d" or hm.group(3) != "3.9000":
        die("parent HUBBARD %r is not 'U %s-3d 3.9000'" % (hub[0], mag_label))

    # MN-a6 -- which lattice vector is the 2.876 A axis: READ, not assumed
    lens = [sum(c * c for c in v) ** 0.5 for v in cell]
    near = [i for i, L in enumerate(lens) if abs(L - A_TARGET) < 0.001]
    if len(near) != 1:
        die("STOP: %d lattice vectors have length ~%.3f A (%s); the doubled "
            "axis is ambiguous" % (len(near), A_TARGET, lens))
    if near[0] != 0:
        die("STOP: the %.3f A axis is v%d, docs/67 E2 doubles the x-length "
            "(v1) -- not guessing" % (A_TARGET, near[0] + 1))
    if cell[0][1] != 0.0 or cell[0][2] != 0.0:
        die("v1 is not exactly in-plane along x: %s" % cell[0])
    if min(abs(lens[i] - lens[0]) for i in (1, 2)) < 0.1:
        die("another lattice vector is within 0.1 A of v1 -- axis identity "
            "is ambiguous")
    a = cell[0][0]

    return {
        "lines": lines, "i_prefix": i_prefix, "i_nat": i_nat,
        "i_ntyp": i_ntyp, "sm_idx": sm_idx, "sm": sm, "i_spec": i_spec,
        "i_cell": i_cell, "i_pos": i_pos, "i_kpt": i_kpt, "i_hub": i_hub,
        "species": species, "cell": cell, "pos": pos, "nat": nat,
        "ntyp": ntyp, "a": a, "mag_label": mag_label, "mag_i": mag_i,
        "hub_val": hm.group(3), "hub_man": hm.group(2),
        "ends_nl": txt.endswith("\n"),
    }


# --------------------------------------------------------------------------
# the tiled frame: cell copy, comb, chain -- from coordinates alone
# --------------------------------------------------------------------------

def classify(x: float, a: float):
    """(n, comb) of a child-frame Mn from its x alone (docstring rules)."""
    if x < -0.05 or x >= 2 * a:
        die("Mn x=%.8f outside the 2x1 cell [0, %.3f)" % (x, 2 * a))
    if abs(x - 0.75 * a) < 0.2:
        die("STOP: Mn x=%.8f within 0.2 A of the 0.75a cell-copy boundary "
            "-- copy index ambiguous" % x)
    n = 0 if x <= 0.75 * a else 1
    r = x - n * a
    if abs(r) < 0.05:
        comb = "corner"
    elif abs(r - a / 2) < 0.05:
        comb = "body"
    else:
        die("STOP: Mn x=%.8f (residue %.5f) is on neither comb (docs/67 SS2 "
            "clustering) -- not guessing" % (x, r))
    return n, comb


def spin_of(pattern: str, n: int, comb: str) -> int:
    """+1 (up) / -1 (down) per the docstring's four registered patterns."""
    if pattern == "fm":
        return +1
    if pattern == "pa":
        return +1 if comb == "corner" else -1
    if pattern == "pb1":
        return +1 if n == 0 else -1
    if pattern == "pb2":
        return +1 if (n == 0) == (comb == "corner") else -1
    die("unknown pattern %r" % pattern)


def tile_atoms(P):
    """The 36 child atoms: parent block (n=0), then the +a block (n=1).

    Returns [(parent_species, x_tok, tail, n, comb_or_None, chain_id)].
    chain_id indexes Mn chains only (None for non-magnetic atoms).
    """
    a = P["a"]
    atoms = []
    for n in (0, 1):
        for (sp, x_tok, tail) in P["pos"]:
            x = float(x_tok) + n * a
            x_out = x_tok if n == 0 else "%.8f" % x
            if n == 1 and not re.match(r"^-?\d+\.\d{8}$", x_out):
                die("shifted x %r broke the 8-decimal format" % x_out)
            atoms.append([sp, x_out, tail, None, None, None])

    # classify the magnetic atoms from coordinates alone
    mag = P["mag_label"]
    for at in atoms:
        if at[0] == mag:
            n, comb = classify(float(at[1]), a)
            at[3], at[4] = n, comb

    # chains: Mn sharing (y, z) to < 1e-3 A                          (MN-a8)
    mn = [at for at in atoms if at[0] == mag]
    if len(mn) != 12:
        die("2x1 frame has %d Mn, expected 12" % len(mn))
    chains = []
    for at in mn:
        ym = re.match(r"^  (-?\d+\.\d{8})  (-?\d+\.\d{8})", at[2])
        if not ym:
            die("unparseable position tail %r" % at[2])
        y, z = float(ym.group(1)), float(ym.group(2))
        for cid, (cy, cz, members) in enumerate(chains):
            if abs(y - cy) < 1e-3 and abs(z - cz) < 1e-3:
                members.append(at)
                at[5] = cid
                break
        else:
            at[5] = len(chains)
            chains.append((y, z, [at]))
    if len(chains) != 6 or any(len(c[2]) != 2 for c in chains):
        die("STOP: chain clustering found %s, expected 6 chains of 2"
            % [(len(c[2])) for c in chains])
    for cy, cz, members in chains:
        dx = abs(float(members[0][1]) - float(members[1][1]))
        if abs(dx - a) > 1e-6:
            die("chain at y=%.4f z=%.4f has x-split %.6f != a" % (cy, cz, dx))
        if {members[0][3], members[1][3]} != {0, 1}:
            die("chain at y=%.4f z=%.4f lacks one atom per cell copy" % (cy, cz))

    corner = [at for at in mn if at[4] == "corner"]
    body = [at for at in mn if at[4] == "body"]
    if len(corner) != 6 or len(body) != 6:                            # MN-a7
        die("STOP: comb split %d corner / %d body -- the half/half patterns "
            "need 6+6; not guessing" % (len(corner), len(body)))
    return atoms


# --------------------------------------------------------------------------
# deck emission (byte-minimal vs the tiled parent)
# --------------------------------------------------------------------------

def build_deck(P, atoms, stem: str, pattern: str) -> str:
    L = P["lines"]
    a = P["a"]
    mag = P["mag_label"]
    afm = pattern != "fm"

    # child species table: Mn -> (Mn1, Mn2) for AFM decks; others verbatim
    child_species = []
    for (sp, rest) in P["species"]:
        if sp == mag and afm:
            child_species.append((mag + "1", rest))
            child_species.append((mag + "2", rest))
        else:
            child_species.append((sp, rest))
    ntyp_child = len(child_species)
    label_of = {}   # role -> child label for magnetic atoms
    if afm:
        label_of = {+1: mag + "1", -1: mag + "2"}

    # child sm block, seeds byte-derived from the parent's own tokens
    up_tok = P["sm"][P["mag_i"]]              # '0.5'
    dn_tok = "-" + up_tok                     # '-0.5'
    seed = {}
    for k, (sp, _rest) in enumerate(child_species, start=1):
        if afm and sp == mag + "1":
            seed[k] = up_tok
        elif afm and sp == mag + "2":
            seed[k] = dn_tok
        elif sp == mag:
            seed[k] = up_tok
        else:
            # non-magnetic: inherit the parent token for this label
            src = [i for i, (psp, _r) in enumerate(P["species"], start=1)
                   if psp == sp]
            seed[k] = P["sm"][src[0]]

    out = []
    i = 0
    while i < len(L):
        l = L[i]
        if i == P["i_prefix"]:
            out.append("  prefix = '%s'" % stem)
        elif i == P["i_nat"]:
            out.append("  nat = %d" % (2 * P["nat"]))
        elif i == P["i_ntyp"]:
            out.append("  ntyp = %d" % ntyp_child)
        elif i == P["sm_idx"][0]:
            for k in range(1, ntyp_child + 1):
                out.append("  starting_magnetization(%d) = %s" % (k, seed[k]))
            i = P["sm_idx"][-1] + 1
            continue
        elif i == P["i_spec"]:
            out.append(l)
            for (sp, rest) in child_species:
                out.append("  %s%s" % (sp, rest))
            i += 1 + P["ntyp"]
            continue
        elif i == P["i_cell"]:
            out.append(l)
            v1 = L[P["i_cell"] + 1]
            m = re.match(r"^  (-?\d+\.\d{8})(  .+)$", v1)
            if not m or abs(float(m.group(1)) - a) > 1e-9:
                die("cell v1 line %r does not carry a in x" % v1)
            out.append("  %.8f%s" % (2 * a, m.group(2)))
            out.append(L[P["i_cell"] + 2])
            out.append(L[P["i_cell"] + 3])
            i += 4
            continue
        elif i == P["i_pos"]:
            out.append(l)
            for (sp, x_tok, tail, n, comb, _cid) in atoms:
                if sp == mag and afm:
                    lab = label_of[spin_of(pattern, n, comb)]
                else:
                    lab = sp
                out.append("  %s  %s%s" % (lab, x_tok, tail))
            i += 1 + P["nat"]
            continue
        elif i == P["i_kpt"]:
            out.append(l)
            out.append("  %d %d %d 0 0 0" % KMESH_CHILD)
            i += 2
            continue
        elif i == P["i_hub"]:
            out.append(l)
            labels = ([mag + "1", mag + "2"] if afm else [mag])
            for lab in labels:
                out.append("U %s-%s %s" % (lab, P["hub_man"], P["hub_val"]))
            i += 2
            continue
        else:
            out.append(l)
        i += 1

    txt = "\n".join(out)
    if P["ends_nl"]:
        txt += "\n"
    return txt


# --------------------------------------------------------------------------
# post-write verification (MN-b, on the WRITTEN bytes)
# --------------------------------------------------------------------------

def verify_decks(P, paths):
    mag = P["mag_label"]
    a = P["a"]
    geom_cols = None
    for (stem, pattern), path in zip(PLAN, paths):
        txt = read(path)
        if txt.endswith("\n") != P["ends_nl"]:                        # MN-b9
            die("%s trailing-newline convention differs from the parent" % path)
        lines = txt.split("\n")
        afm = pattern != "fm"

        nat = int([l for l in lines if l.startswith("  nat =")][0].split("=")[1])
        ntyp = int([l for l in lines if l.startswith("  ntyp =")][0].split("=")[1])
        if nat != 2 * P["nat"]:                                       # MN-b3
            die("%s nat %d != 2x parent %d" % (path, nat, 2 * P["nat"]))
        if ntyp != (3 if afm else 2):
            die("%s ntyp %d wrong for pattern %s" % (path, ntyp, pattern))
        for want in ("  nosym = .true.", "  noinv = .true.",
                     "  calculation = 'scf'", "  nspin = 2"):
            if want not in lines:
                die("%s lacks %r" % (path, want.strip()))

        i_spec = lines.index("ATOMIC_SPECIES")
        specs = []
        for l in lines[i_spec + 1:i_spec + 1 + ntyp]:
            specs.append(l.split()[0])
        i_pos = lines.index("ATOMIC_POSITIONS angstrom")
        rows = lines[i_pos + 1:i_pos + 1 + nat]
        counts = {}
        cols = []
        spin_atoms = []
        for r in rows:
            m = re.match(r"^  (\S+)(  )(-?\d+\.\d{8})(  \S.*)$", r)
            if not m:
                die("%s unparseable position row %r" % (path, r))
            sp = m.group(1)
            counts[sp] = counts.get(sp, 0) + 1
            cols.append(m.group(3) + m.group(4))
            if sp.startswith(mag):
                spin_atoms.append((sp, float(m.group(3))))
            if sp not in specs:
                die("%s position species %r not in ATOMIC_SPECIES" % (path, sp))

        if geom_cols is None:
            geom_cols = cols
        elif cols != geom_cols:                                       # MN-b6
            die("%s coordinates differ from the first deck -- the four decks "
                "must be coordinate-identical" % path)

        if afm:
            if counts.get(mag + "1") != 6 or counts.get(mag + "2") != 6:  # MN-b3
                die("%s up/down split %s is not 6/6" % (path, counts))
        else:
            if counts.get(mag) != 12:
                die("%s Mn count %s != 12" % (path, counts))
        n_other = sum(v for k, v in counts.items() if not k.startswith(mag))
        if n_other != 24:
            die("%s non-Mn count %d != 24" % (path, n_other))

        # re-derive every spin from coordinates and check the species column
        for sp, x in spin_atoms:
            n, comb = classify(x, a)
            want = spin_of(pattern, n, comb)
            if afm:
                lab = mag + ("1" if want == +1 else "2")
                if sp != lab:                                # MN-b4 / MN-b5
                    die("%s atom x=%.6f labelled %s, pattern %s wants %s"
                        % (path, x, sp, pattern, lab))
            elif sp != mag:
                die("%s FM deck carries split label %s" % (path, sp))

        i_hub = lines.index("HUBBARD (atomic)")
        hub = [l for l in lines[i_hub + 1:] if l.strip()]
        want_hub = (["U %s1-3d %s" % (mag, P["hub_val"]),
                     "U %s2-3d %s" % (mag, P["hub_val"])] if afm
                    else ["U %s-3d %s" % (mag, P["hub_val"])])
        if hub != want_hub:                                           # MN-b7
            die("%s HUBBARD card %s != %s (a one-label card silently leaves "
                "a sublattice at U=0)" % (path, hub, want_hub))
        for sp in specs:
            if sp.startswith(mag):
                hits = [l for l in hub if l.startswith("U %s-" % sp)]
                if len(hits) != 1:
                    die("%s species %s has %d HUBBARD lines" % (path, sp, len(hits)))

        # MN-b8 -- byte-minimal namelist vs the parent
        allowed = {"  prefix = ", "  nat = ", "  ntyp = ",
                   "  starting_magnetization("}
        p_nl = [l for l in P["lines"][:P["i_spec"]]
                if not any(l.startswith(t) for t in allowed)]
        c_nl = [l for l in lines[:i_spec]
                if not any(l.startswith(t) for t in allowed)]
        if p_nl != c_nl:
            die("%s namelist deviates from the parent beyond the enumerated "
                "edits" % path)
        kline = lines[lines.index("K_POINTS automatic") + 1]
        if kline != "  4 4 1 0 0 0":
            die("%s K_POINTS %r != the E2 mesh 4 4 1 0 0 0" % (path, kline))
        i_cell = lines.index("CELL_PARAMETERS angstrom")
        if lines[i_cell + 2:i_cell + 4] != \
                P["lines"][P["i_cell"] + 2:P["i_cell"] + 4]:
            die("%s v2/v3 differ from the parent" % path)
        v1 = [float(t) for t in lines[i_cell + 1].split()]
        if abs(v1[0] - 2 * a) > 1e-9 or v1[1] != 0.0 or v1[2] != 0.0:
            die("%s v1 %s != doubled parent axis" % (path, v1))

    # MN-b5 -- B1 and B2 must actually differ (on the body comb)
    b1 = read(paths[2]).split("\n")
    b2 = read(paths[3]).split("\n")
    ndiff = sum(1 for x, y in zip(b1, b2) if x != y)
    if len(b1) != len(b2) or ndiff == 0:
        die("P-B1 and P-B2 are identical -- registry assignment broken")
    print("  MN-b   all 4 decks verified (36 atoms, 6/6 splits, combs/chains, "
          "HUBBARD both labels, coordinate-identical; B1 vs B2 differ on %d "
          "lines)" % ndiff)


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------

def build_manifest(parent_md5: str, deck_md5s) -> str:
    hdr = [
        "# MN-AFM-ORDER stage 1 -- the A7.5 Mn AFM ordering measurement, 2x1 frame",
        "# (4 decks: FM, P-A, P-B1, P-B2). Built 2026-08-31 by",
        "# src/dft/build_mn_afm_order.py -- READ ITS DOCSTRING, docs/67 (design of",
        "# record), and docs/43 A11.R3.",
        "#",
        "# LICENSED: docs/43 A11.R3 line \"[MN AFM ARM 2026-08-31: IN SCOPE]\" --",
        "# \"Staged program and triggers per docs/67 §5: MN-AFM-ORDER 4 (licensed",
        "# now)\"; that line IS the arm's licence (docs/43:2008 excludes any AFM deck",
        "# in 1x1 from the gate-(h) licence, so nothing prior covers this family).",
        "# Submission additionally waits on the docs/43 A11.R5 Zenodo deposit.",
        "#",
        "# Geometry: the banked FM production slab runs/a0/main/Mn/slab__u390.in",
        "# (frozen, md5 %s) tiled x2 along its 2.876 A in-plane" % parent_md5,
        "# [001] axis -> 5.752 A; 12 Mn / 24 O; fixed-geometry SCFs (docs/67 E3",
        "# fixed-first); K_POINTS 4 4 1 (E2); U Mn-3d 3.9 on every Mn label -- the",
        "# AFM decks carry BOTH 'U Mn1-3d 3.9000' AND 'U Mn2-3d 3.9000' (a one-label",
        "# card would silently leave a sublattice at U = 0, docs/67 E7).",
        "#",
        "# E4 adoption rule, in-frame (FM reference = slab__2x1__fm of this set),",
        "# fixed before any AFM energy exists; M_abs is the witness that an AFM",
        "# solution was actually held:",
        "#   " + E4_RULE,
        "# firewalled from A7.2/A7.3 (docs/67 §1: no number from this arm enters",
        "# the banked scores; the A7.5 strike lifts by RUNNING, on any outcome).",
        "#",
        "# deck md5s (an independent rebuild must reproduce these byte-for-byte):",
    ] + ["# md5 %s %s" % (h, rel) for rel, h in deck_md5s] + [
        "#",
        "# SUBMIT WITH EXCLUDE=" + EXCLUDE,
        "# (submit-time list additionally + a120,a200 per docs/66 §4)",
        "#",
        "# row: dir job suffix nk",
        "# NP=128 NCONC=1",
    ]
    body = ["s0/mn_afm %s .in %d" % (stem, NK) for stem, _p in PLAN]
    return "\n".join(hdr + body) + "\n"


def verify_manifest(path: str, deck_paths):
    txt = read(path)
    lines = txt.split("\n")
    if "NOT LICENSED" in txt:                                         # MN-c1
        die("manifest carries 'NOT LICENSED' -- the docs/66 §4 guard would "
            "refuse it and this family IS licensed")
    if sum(1 for l in lines if l == "# NP=128 NCONC=1") != 1:
        die("manifest must carry exactly one '# NP=128 NCONC=1' line")
    if sum(1 for l in lines if l == "# SUBMIT WITH EXCLUDE=" + EXCLUDE) != 1:
        die("manifest must carry the EXCLUDE header exactly once")
    if sum(1 for l in lines
           if "a120,a200 per docs/66" in l) != 1:
        die("manifest must carry the submit-time a120,a200 note")
    if sum(1 for l in lines if l.startswith("#   ") and E4_RULE in l) != 1:
        die("manifest must quote the E4 adoption rule verbatim, once")
    if "firewalled from A7.2/A7.3" not in txt:
        die("manifest must state the A7.2/A7.3 firewall")
    if "[MN AFM ARM 2026-08-31: IN SCOPE]" not in txt:
        die("manifest must cite the A11.R3 licensing line")
    rows = [l for l in lines if l and not l.startswith("#")]
    if len(rows) != len(PLAN):                                        # MN-c2
        die("manifest has %d rows, expected %d" % (len(rows), len(PLAN)))
    for row, (stem, _p) in zip(rows, PLAN):
        f = row.split()
        if len(f) != 4:
            die("row %r is not 4-field 'dir job suffix nk' (trailing fields "
                "are fatal in anvil/47_submit_a0.sh)" % row)
        if f[0] != "s0/mn_afm" or f[1] != stem or f[2] != ".in":
            die("row %r does not match the plan (%s)" % (row, stem))
        if int(f[3]) != NK or NP % int(f[3]) != 0:
            die("row %r nk %s violates nk=%d / NP=%d divisibility"
                % (row, f[3], NK, NP))
    md5_lines = [l for l in lines if l.startswith("# md5 ")]
    if len(md5_lines) != len(deck_paths):                             # MN-c3
        die("manifest has %d md5 lines, expected %d"
            % (len(md5_lines), len(deck_paths)))
    for l, p in zip(md5_lines, deck_paths):
        toks = l.split()
        if len(toks) != 4:
            die("malformed manifest md5 line %r" % l)
        h, rel = toks[2], toks[3]
        if h != md5(p):
            die("manifest md5 %s does not match on-disk %s" % (h, p))
        if not p.replace("\\", "/").endswith("runs/" + rel):
            die("manifest md5 path %r does not name %s" % (rel, p))
    print("  MN-c   manifest verified (4-field rows, nk %d, EXCLUDE header + "
          "a120,a200 note, E4 rule verbatim, firewall + licence lines, md5s "
          "match disk)" % NK)


# --------------------------------------------------------------------------

def main(argv):
    out_root = ROOT
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--sandbox":
            if i + 1 >= len(argv):
                die("--sandbox needs a directory")
            out_root = os.path.abspath(argv[i + 1])
            i += 2
            continue
        die("unsupported argument %r -- this builder builds exactly the four "
            "registered MN-AFM-ORDER decks; only --sandbox <dir> is accepted" % a)
    sandbox = os.path.normcase(out_root) != os.path.normcase(ROOT)

    print("MN-AFM-ORDER stage 1 build (docs/67; licence docs/43 A11.R3 "
          "[MN AFM ARM 2026-08-31: IN SCOPE])")
    if sandbox:
        print("SANDBOX rebuild into %s (parent/evidence still read from the repo)"
              % out_root)

    # MN-b10 snapshot -- every banked Mn production file, before anything else
    banked = {}
    for f in sorted(os.listdir(PARENT_DIR)):
        p = os.path.join(PARENT_DIR, f)
        if os.path.isfile(p):
            banked[p] = md5(p)

    # MN-a1 -- the parent and its banked, converged evidence
    if not os.path.exists(PARENT):
        die("parent deck missing: %s" % PARENT)
    e = energy_ry(PARENT[:-3] + ".out")
    if e is None:
        die("parent evidence %s.out missing or unconverged" % PARENT[:-3])
    parent_md5 = md5(PARENT)
    P = parse_parent(read(PARENT))
    print("  MN-a   parent anatomy verified (nat 18, ntyp 2, 9 4 1, "
          "U Mn-3d 3.9000, v1=%.3f A; .out banked at %.8f Ry, md5 %s)"
          % (P["a"], e, parent_md5))

    atoms = tile_atoms(P)
    print("  MN-a   2x1 frame derived: 12 Mn (6 corner / 6 body; 6 chains "
          "of 2) + 24 O")

    out_dir = os.path.join(out_root, OUT_REL)
    # MN-b2 -- collision/overwrite sweep before any write
    for stem, _p in PLAN:
        repo_out = os.path.join(ROOT, OUT_REL, stem + ".out")
        if os.path.exists(repo_out):
            die("stem %s collides with banked evidence %s" % (stem, repo_out))
        for ext in (".in", ".out"):
            c = os.path.join(out_dir, stem + ext)
            if os.path.exists(c) and not (sandbox and ext == ".in"):
                die("refusing to overwrite existing %s" % c)
    man_path = os.path.join(out_root, MAN_REL)
    if os.path.exists(man_path) and not sandbox:
        die("refusing to overwrite existing manifest %s" % man_path)

    paths, deck_md5s = [], []
    for stem, pattern in PLAN:
        txt = build_deck(P, atoms, stem, pattern)
        child = os.path.join(out_dir, stem + ".in")
        if not child.replace("\\", "/").endswith(
                "runs/s0/mn_afm/%s.in" % stem):
            die("child outside runs/s0/mn_afm: %s" % child)
        write(child, txt)
        paths.append(child)
        deck_md5s.append(("s0/mn_afm/%s.in" % stem, md5(child)))
        print("  wrote  %-22s pattern %-3s md5 %s"
              % (stem + ".in", pattern, deck_md5s[-1][1]))

    verify_decks(P, paths)

    # MN-b10 -- the banked tree is untouched
    for p, h in banked.items():
        if md5(p) != h:
            die("BANKED FILE ALTERED: %s" % p)
    print("  MN-b10 all %d banked files under runs/a0/main/Mn/ unchanged"
          % len(banked))

    write(man_path, build_manifest(parent_md5, deck_md5s))
    verify_manifest(man_path, paths)
    print("  wrote  %s" % os.path.relpath(man_path, out_root))
    print("\nBUILD OK -- 4 decks, 0 relaxations, 0 banked files touched. "
          "Submission waits on the A11.R5 deposit (docs/43).")


if __name__ == "__main__":
    main(sys.argv[1:])
