#!/usr/bin/env python3
"""S0 gate (h) — the four owed 2x1v AFM RELAXATIONS, built but deliberately not launchable.

READ docs/43 AMENDMENT 8 (A8.5, docs/43:1638-1645) and docs/63. This docstring is the
build-side registration; docs/43's is the scoring-side registration.

WHAT IS OWED, AND BY WHAT
-------------------------
docs/43:1638-1644 (A8.5, deposited): gate (h) returned 4/4 ADOPT_AFM on the RuO2
anchors (-144, -80, -85, -111 meV against NM, against a -20 meV rule) and the
adsorption energies move 33-64 meV once the anchor is AFM. Those four AFM points are
SINGLE POINTS ON NM-RELAXED GEOMETRIES -- P11 limit (ii), a lower bound. Adopting AFM
as the anchor's magnetic row therefore owes FOUR 2x1v AFM RELAXATIONS, S3-class,
priced in A8.6.

WHY THIS BUILDER REFUSES TO EMIT A LAUNCH MANIFEST
--------------------------------------------------
docs/43:1645, the ADOPTION NOTE dated 2026-08-23, is part of the deposited text:

    "still open -- this paragraph and the A8.1 magnetic-basin row collide (docs/52
    row 26; docs/51 skeptic addition iii): whether these four are the Ru second seed
    inside tier_v3's crossed magnetic-basin factor (then crossed with cell and
    symmetry, up to 16 relaxations) or four standalone S3-class jobs ... No default
    was drafted, so the blanket adoption decides nothing here; the resolution is the
    entrant's to write in a dated line. Until he does, the gate-(h) AFM relaxations
    remain HOLD (0 built -- docs/51)."

So the HOLD lives in the deposited registration and has NO DEFAULT. It is not a
scheduling note and it is not mine to resolve: the two readings differ by 4x in deck
count (4 standalone vs up to 16 crossed) and therefore in SU. This builder enforces
that mechanically -- it writes DECKS unconditionally (they are prep, they cost no SU,
and the four 2x1v/off state decks are common to BOTH readings) but writes the
MANIFEST the submit script consumes only once the resolution line exists. A HOLD a
human has to remember is a HOLD that gets forgotten at 2 a.m.

TO LIFT THE HOLD, the entrant adds one dated line to docs/43, in his own words, whose
machine-readable head is exactly one of:

    [AFM-SCOPE RESOLVED YYYY-MM-DD: STANDALONE_FOUR]
    [AFM-SCOPE RESOLVED YYYY-MM-DD: SECOND_SEED_CROSSED]

STANDALONE_FOUR   -> the four 2x1v AFM relaxations stand alone as S3-class jobs; this
                     builder's four decks are the whole family and the manifest is
                     emitted for them.
SECOND_SEED_CROSSED -> the AFM row is the Ru second seed inside tier_v3's crossed
                     magnetic-basin factor. These same four decks are then the
                     2x1v/off cell-symmetry arm of a family up to 16 relaxations, and
                     this builder emits its four with a note that the remaining arms
                     are owed from the S3 builder, not from here.

THE TRANSFORMATION
------------------
Each child is its banked gate-(h) SCF parent with EXACTLY TWO LINES CHANGED:

    calculation = 'scf'  ->  calculation = 'relax'
    prefix      = <stem> ->  prefix      = <stem>__relax

Nothing else moves. The parents already carry `&IONS ion_dynamics = 'bfgs'`,
`tprnfor`, `forc_conv_thr = 2.0d-3` and `nstep = 200`, so the SCF decks were written
one keyword away from being relaxations; ASSERTION A10 pins the diff to exactly those
two lines so that claim is checked rather than trusted.

THE TRAP THIS BUILDER INHERITS
------------------------------
The metal's species index is STATE-DEPENDENT here exactly as it is in build_a0spin.py:

    ref, s0_O      -> ntyp 3, [Ru1, Ru2, O]     -> sublattices at 1, 2
    s0_OH, s0_OOH  -> ntyp 4, [H, Ru1, Ru2, O]  -> sublattices at 2, 3

because H sorts first. A per-deck constant would seed H or O. The banked parents were
verified to have this right (all four checked, 2026-08-30); A3/A4 below re-derive the
pair from each deck's own ATOMIC_SPECIES rather than trusting that check.

BUILD-TIME ASSERTIONS (all fatal)
---------------------------------
A1  parent .in and .out exist; parent .out converged, no "convergence NOT achieved"
A2  parent .in is byte-identical to its committed blob at HEAD (no edited parent)
A3  the AFM sublattice pair is FOUND, not assumed: exactly two species labels sharing
    an identical (mass, pseudo) pair and differing only by a trailing digit
A4  exactly ntyp starting_magnetization lines, contiguous 1..ntyp; the pair carries
    +s and -s of equal magnitude at ITS OWN indices; every other species exactly 0.0
A5  nspin = 2 and NO HUBBARD card (Ru carries no U -- protocol.md section 2)
A6  nosym = .true. and noinv = .true. both present
A7  &IONS with ion_dynamics = 'bfgs'; forc_conv_thr and nstep present
A8  constraint mask preserved: same count, same order, byte-identical flags
A9  ATOMIC_POSITIONS block byte-identical to the parent's (the relaxation starts from
    exactly the banked geometry, so the AFM relax is a clean continuation of the
    single point, not a re-placement)
A10 diff shape: replaced == 2, inserted == 0, deleted == 0, and the two replaced
    lines are exactly the calculation line and the prefix line
A11 prefix == stem == basename (anvil/46_a0.slurm does `rm -rf dens/${prefix}.save`;
    a colliding prefix silently wipes a banked density)
A12 every child path is under the build's h_afm_relax/ (runs/s0/h_afm_relax/ unless
    --out-dir says otherwise), never runs/s0/h_afm_anchor/, which the gate-(h) readout
    and docs/63 address literally
A13 trailing-newline and CR bytes preserved from the parent

GATE-1 CHILDREN
---------------
The deposited GATE-1 rule (docs/43:311-314, A5.7) gives every new relaxation a
fresh-density fixed-geometry `__g1` SCF, with the >= 5 meV BASIN_DRIFT re-relax loop
and A8.3's 1 meV above-parent refusal. `--gate1` builds them from each relaxation's
converged final geometry and REFUSES while any parent is unconverged -- the same
refusal build_lit2_ruo2_ladder.py --gate1 makes. The family is therefore >= 8 decks
(docs/51:25), not four, and the manifest says so.

USAGE
-----
    PYTHONPATH=src python src/dft/build_h_afm_relax.py            # build decks, check gate
    PYTHONPATH=src python src/dft/build_h_afm_relax.py --gate1    # after the relaxations land
    PYTHONPATH=src python src/dft/build_h_afm_relax.py --out-dir DIR   # the same build with
                                  # decks under DIR/h_afm_relax/ and the manifest in DIR/;
                                  # the tracked tree is untouched (inputs still come from it)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(REPO, "runs", "s0", "h_afm_anchor")
OUT_DIR = os.path.join(REPO, "runs", "s0", "h_afm_relax")
PREREG = os.path.join(REPO, "docs", "43-prereg-week1-factorial.md")

STEMS = [
    "ref__2x1v__afm",
    "s0_O__2x1v_off__afm",
    "s0_OH__2x1v_off__afm",
    "s0_OOH__2x1v_off__afm",
]

RESOLUTION_RE = re.compile(
    r"\[AFM-SCOPE RESOLVED (\d{4}-\d{2}-\d{2}): (STANDALONE_FOUR|SECOND_SEED_CROSSED)\]"
)


class BuildRefused(SystemExit):
    """A fatal build-time assertion. Never downgraded to a warning."""


def fail(assertion: str, msg: str) -> None:
    raise BuildRefused(f"REFUSED [{assertion}] {msg}")


# ------------------------------------------------------------------ the gate ---

def afm_scope_resolution() -> tuple[str, str] | None:
    """The dated line docs/43:1645 says the entrant owes, or None while HOLD stands."""
    if not os.path.exists(PREREG):
        return None
    m = RESOLUTION_RE.search(open(PREREG, encoding="utf-8", errors="replace").read())
    return (m.group(1), m.group(2)) if m else None


# ----------------------------------------------------------------- parsing ---

def species_block(txt: str) -> list[tuple[str, str, str]]:
    m = re.search(r"ATOMIC_SPECIES\s*\n((?:[ \t]*\S+[ \t]+[\d.]+[ \t]+\S+[ \t]*\n)+)", txt)
    if not m:
        return []
    out = []
    for line in m.group(1).strip().split("\n"):
        p = line.split()
        out.append((p[0], p[1], p[2]))
    return out


def positions_block(txt: str) -> str:
    m = re.search(
        r"(ATOMIC_POSITIONS[^\n]*\n(?:.*\n)+?)(?=K_POINTS|CELL_PARAMETERS|HUBBARD|\Z)", txt
    )
    return m.group(1) if m else ""


def constraint_flags(txt: str, labels: set[str]) -> list[str]:
    flags = []
    for line in positions_block(txt).split("\n")[1:]:
        p = line.split()
        if len(p) >= 4 and p[0] in labels:
            flags.append(" ".join(p[4:7]) if len(p) >= 7 else "1 1 1")
    return flags


def find_sublattice_pair(species: list[tuple[str, str, str]]) -> tuple[str, str]:
    """A3: the AFM pair is two labels that are one element -- found, never assumed."""
    cands = []
    for i, (li, mi, pi) in enumerate(species):
        for j in range(i + 1, len(species)):
            lj, mj, pj = species[j]
            if (mi, pi) != (mj, pj):
                continue
            base_i, base_j = li.rstrip("0123456789"), lj.rstrip("0123456789")
            if base_i and base_i == base_j and li != lj:
                cands.append((li, lj))
    if len(cands) != 1:
        fail("A3", f"expected exactly one AFM sublattice pair, found {cands}")
    return cands[0]


# ------------------------------------------------------------------- build ---

def committed_blob(relpath: str) -> bytes | None:
    try:
        return subprocess.check_output(
            ["git", "show", f"HEAD:{relpath}"], cwd=REPO, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return None


def out_paths(out_root: str | None, manifest: str) -> tuple[str, str]:
    """Where a build lands: (deck directory, manifest path).

    out_root mirrors runs/s0 -- decks under <out_root>/h_afm_relax/, the manifest at
    <out_root>/<manifest>. None is the live tree, runs/s0, which the submit scripts
    consume; anything else is a rehearsal that leaves the tracked decks and manifests
    untouched. Inputs -- the banked anchors, the relaxations' .out files, the casualty
    evidence -- are always read from SRC_DIR / OUT_DIR.
    """
    root = out_root or os.path.join(REPO, "runs", "s0")
    return os.path.join(root, "h_afm_relax"), os.path.join(root, manifest)


def show(path: str) -> str:
    """Repo-relative with forward slashes when inside the repo, else as given."""
    try:
        rel = os.path.relpath(path, REPO)
    except ValueError:  # Windows: another drive
        return path
    return path if rel.startswith("..") else rel.replace(os.sep, "/")


def inside_banked_tree(dest: str) -> bool:
    """A12/G9: would dest land inside the banked gate-(h) tree?"""
    try:
        return (os.path.commonpath([os.path.abspath(dest), os.path.abspath(SRC_DIR)])
                == os.path.abspath(SRC_DIR))
    except ValueError:  # Windows: another drive -- cannot be inside
        return False


def build_one(stem: str, dest_dir: str | None = None) -> dict:
    dest_dir = dest_dir or OUT_DIR
    src_in = os.path.join(SRC_DIR, stem + ".in")
    src_out = os.path.join(SRC_DIR, stem + ".out")

    # A1 -- parent exists and converged
    for p in (src_in, src_out):
        if not os.path.exists(p):
            fail("A1", f"parent missing: {p}")
    otxt = open(src_out, errors="replace").read()
    if "convergence NOT achieved" in otxt:
        fail("A1", f"{stem}: parent .out reports a convergence failure")
    if "convergence has been achieved" not in otxt:
        fail("A1", f"{stem}: parent .out never reports convergence")
    if "JOB DONE" not in otxt:
        fail("A1", f"{stem}: parent .out has no JOB DONE")

    raw = open(src_in, "rb").read()

    # A2 -- the parent is the committed artifact, unedited
    rel = os.path.relpath(src_in, REPO).replace(os.sep, "/")
    blob = committed_blob(rel)
    if blob is None:
        fail("A2", f"{stem}: parent .in is not committed at HEAD ({rel})")
    if hashlib.md5(blob).hexdigest() != hashlib.md5(raw).hexdigest():
        fail("A2", f"{stem}: parent .in differs from its committed blob")

    txt = raw.decode()
    species = species_block(txt)
    if not species:
        fail("A3", f"{stem}: no ATOMIC_SPECIES block")
    labels = {s[0] for s in species}
    ru1, ru2 = find_sublattice_pair(species)
    idx = {label: i + 1 for i, (label, _m, _p) in enumerate(species)}

    # A4 -- seeds, at indices read from THIS deck
    mags = {int(m.group(1)): float(m.group(2))
            for m in re.finditer(r"starting_magnetization\((\d+)\)\s*=\s*([-\d.eE+]+)", txt)}
    if sorted(mags) != list(range(1, len(species) + 1)):
        fail("A4", f"{stem}: starting_magnetization indices {sorted(mags)} != 1..{len(species)}")
    s1, s2 = mags[idx[ru1]], mags[idx[ru2]]
    if s1 <= 0 or s2 >= 0 or abs(abs(s1) - abs(s2)) > 1e-12:
        fail("A4", f"{stem}: {ru1}/{ru2} seeds {s1}/{s2} are not equal and antiparallel")
    for label in labels - {ru1, ru2}:
        if mags[idx[label]] != 0.0:
            fail("A4", f"{stem}: non-metal species {label} carries seed {mags[idx[label]]}")

    # A5/A6/A7 -- treatment and machinery
    if not re.search(r"^\s*nspin\s*=\s*2", txt, re.M):
        fail("A5", f"{stem}: nspin is not 2")
    if "HUBBARD" in txt:
        fail("A5", f"{stem}: a HUBBARD card is present; Ru carries no U in this family")
    for key in ("nosym", "noinv"):
        if not re.search(rf"^\s*{key}\s*=\s*\.true\.", txt, re.M | re.I):
            fail("A6", f"{stem}: {key} is not .true.")
    if not re.search(r"ion_dynamics\s*=\s*'bfgs'", txt):
        fail("A7", f"{stem}: &IONS has no ion_dynamics = 'bfgs'")
    for key in ("forc_conv_thr", "nstep"):
        if not re.search(rf"^\s*{key}\s*=", txt, re.M):
            fail("A7", f"{stem}: {key} missing -- a relax deck needs it")

    # ---- the transformation: exactly two lines
    new_stem = stem + "__relax"
    lines = txt.split("\n")
    out_lines, changed = [], []
    for ln in lines:
        if re.match(r"^\s*calculation\s*=", ln):
            out_lines.append(ln.replace("'scf'", "'relax'"))
            changed.append(("calculation", ln, out_lines[-1]))
        elif re.match(r"^\s*prefix\s*=", ln):
            out_lines.append(ln.replace(stem, new_stem))
            changed.append(("prefix", ln, out_lines[-1]))
        else:
            out_lines.append(ln)
    new_txt = "\n".join(out_lines)

    # A10 -- diff shape
    if len(lines) != len(out_lines):
        fail("A10", f"{stem}: line count changed {len(lines)} -> {len(out_lines)}")
    replaced = [i for i, (a, b) in enumerate(zip(lines, out_lines)) if a != b]
    if len(replaced) != 2:
        fail("A10", f"{stem}: {len(replaced)} lines differ, expected exactly 2 (lines {replaced})")
    kinds = sorted(k for k, _a, _b in changed)
    if kinds != ["calculation", "prefix"]:
        fail("A10", f"{stem}: changed lines are {kinds}, expected calculation + prefix")
    if "'relax'" not in new_txt or re.search(r"calculation\s*=\s*'scf'", new_txt):
        fail("A10", f"{stem}: calculation was not switched to 'relax'")

    # A11 -- prefix == stem
    pm = re.search(r"^\s*prefix\s*=\s*'([^']+)'", new_txt, re.M)
    if not pm or pm.group(1) != new_stem:
        fail("A11", f"{stem}: prefix {pm and pm.group(1)!r} != stem {new_stem!r}")

    # A8/A9 -- geometry and mask carried verbatim
    if positions_block(new_txt) != positions_block(txt):
        fail("A9", f"{stem}: ATOMIC_POSITIONS block is not byte-identical to the parent")
    if constraint_flags(new_txt, labels) != constraint_flags(txt, labels):
        fail("A8", f"{stem}: constraint mask changed")
    nat = int(re.search(r"^\s*nat\s*=\s*(\d+)", txt, re.M).group(1))
    got = len(constraint_flags(txt, labels))
    if got != nat:
        fail("A8", f"{stem}: parsed {got} position lines, deck declares nat = {nat}")

    # A12 -- destination
    dest = os.path.join(dest_dir, new_stem + ".in")
    if inside_banked_tree(dest):
        fail("A12", f"{stem}: child would land inside the banked gate-(h) tree")

    # A13 -- byte hygiene
    new_raw = new_txt.encode()
    if raw.endswith(b"\n") != new_raw.endswith(b"\n"):
        fail("A13", f"{stem}: trailing-newline byte changed")
    if (b"\r\n" in raw) != (b"\r\n" in new_raw):
        fail("A13", f"{stem}: CR bytes changed")

    os.makedirs(dest_dir, exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(new_raw)

    n_frozen = sum(1 for f in constraint_flags(txt, labels) if f == "0 0 0")
    return dict(stem=new_stem, parent=rel, path=show(dest),
                nat=nat, ntyp=len(species), pair=(ru1, ru2),
                pair_index=(idx[ru1], idx[ru2]), seeds=(s1, s2), frozen=n_frozen,
                parent_md5=hashlib.md5(raw).hexdigest(),
                child_md5=hashlib.md5(new_raw).hexdigest())


RY_MEV = 13605.693122994  # meV per Ry


def last_magnetization(otxt: str) -> tuple[float, float]:
    """Final converged (totmag, absmag) -- the last printed pair in the .out."""
    tot = re.findall(r"total magnetization\s*=\s*([-\d.]+)", otxt)
    ab = re.findall(r"absolute magnetization\s*=\s*([-\d.]+)", otxt)
    if not tot or not ab:
        fail("G10", "no magnetization lines in .out")
    return float(tot[-1]), float(ab[-1])


def final_coordinates(otxt: str) -> list[tuple[str, tuple[float, float, float], str]]:
    """(label, xyz, flags) per atom from the LAST final-coordinates block.

    QE prints flags only on constrained atoms in this block; unconstrained rows
    come back with flags == '1 1 1' to match constraint_flags()'s convention.
    """
    if "Begin final coordinates" not in otxt:
        fail("G1", "no `Begin final coordinates` block")
    block = otxt.split("Begin final coordinates")[-1].split("End final coordinates")[0]
    rows = []
    for line in block.split("\n"):
        p = line.split()
        if len(p) >= 4 and re.match(r"^[A-Z][a-z]?[0-9]?$", p[0]):
            xyz = (float(p[1]), float(p[2]), float(p[3]))
            flags = " ".join(p[4:7]) if len(p) >= 7 else "1 1 1"
            rows.append((p[0], xyz, flags))
    if not rows:
        fail("G1", "final-coordinates block parsed to zero atoms")
    return rows


def gate1_one(stem: str, dest_dir: str | None = None) -> dict:
    """One GATE-1 child: the banked anchor SCF deck at the relaxation's final
    geometry, fresh prefix, nothing else touched.

    The deposited rule (docs/43:311-314): every relaxation gets a fresh-density
    fixed-geometry SCF at its own final coordinates. Building from the ANCHOR
    deck (already calculation = 'scf', already carrying the full AFM machinery)
    keeps the diff auditable: one prefix line + the moving-atom coordinate
    lines, and the frozen rows stay byte-identical to the committed parent.
    """
    dest_dir = dest_dir or OUT_DIR
    src_in = os.path.join(SRC_DIR, stem + ".in")
    relax_out = os.path.join(OUT_DIR, stem + "__relax.out")

    # G1 -- the relaxation is scoreable
    rtxt = open(relax_out, errors="replace").read()
    if "convergence NOT achieved" in rtxt:
        fail("G1", f"{stem}__relax: an SCF inside the relaxation failed")
    if "End of BFGS Geometry Optimization" not in rtxt:
        fail("G1", f"{stem}__relax: BFGS never converged")
    if "JOB DONE" not in rtxt:
        fail("G1", f"{stem}__relax: no JOB DONE")
    fe = re.findall(r"Final energy\s*=\s*(-\d+\.\d+)\s*Ry", rtxt)
    if len(fe) != 1:
        fail("G1", f"{stem}__relax: {len(fe)} `Final energy` lines, expected exactly 1")
    e_relax = float(fe[0])

    # G2 -- the anchor deck this child derives from is the committed artifact
    raw = open(src_in, "rb").read()
    rel = os.path.relpath(src_in, REPO).replace(os.sep, "/")
    blob = committed_blob(rel)
    if blob is None or hashlib.md5(blob).hexdigest() != hashlib.md5(raw).hexdigest():
        fail("G2", f"{stem}: anchor .in is not the committed blob at HEAD ({rel})")
    txt = raw.decode()
    labels = {s[0] for s in species_block(txt)}

    # G10 -- basin continuity BEFORE building anything: a sign flip between the
    # anchor SCF and the relaxation's final state is the A8.3 CONFOUND case and
    # a child of a flipped state would score the wrong basin.
    atot, _ = last_magnetization(open(os.path.join(SRC_DIR, stem + ".out"),
                                      errors="replace").read())
    rtot, rabs = last_magnetization(rtxt)
    if atot * rtot < 0 and (abs(atot) > 0.05 or abs(rtot) > 0.05):
        fail("G10", f"{stem}: totmag sign flipped {atot} -> {rtot} across the relaxation")

    fin = final_coordinates(rtxt)

    # G3 -- label sequence preserved
    plines = [ln for ln in positions_block(txt).split("\n")[1:]
              if len(ln.split()) >= 4 and ln.split()[0] in labels]
    if [p.split()[0] for p in plines] != [r[0] for r in fin]:
        fail("G3", f"{stem}: final-coordinates label sequence differs from the deck")

    # G4/G5 -- frozen rows unmoved, moving rows bounded
    new_plines, max_disp = [], 0.0
    for ln, (label, xyz, oflags) in zip(plines, fin):
        p = ln.split()
        old = tuple(float(v) for v in p[1:4])
        dflags = " ".join(p[4:7]) if len(p) >= 7 else "1 1 1"
        d = max(abs(a - b) for a, b in zip(old, xyz))
        if dflags == "0 0 0":
            if d > 1e-5:
                fail("G4", f"{stem}: frozen atom {label} moved {d:.2e} A")
            if oflags != "0 0 0":
                fail("G4", f"{stem}: .out flags {oflags!r} on a frozen row")
            new_plines.append(ln)  # byte-identical
        else:
            if d > 0.1:
                fail("G5", f"{stem}: {label} moved {d:.4f} A > 0.1 A in a "
                           "converged-basin relaxation")
            max_disp = max(max_disp, d)
            head = ln[: len(ln) - len(ln.lstrip())]
            tail = f"  {' '.join(p[4:7])}" if len(p) >= 7 else ""
            new_plines.append(f"{head}{p[0]}  {xyz[0]:.10f}  {xyz[1]:.10f}"
                              f"  {xyz[2]:.10f}{tail}")

    # ---- the transformation: prefix + moving coordinates, nothing else
    new_stem = stem + "__relax__g1"
    it = iter(new_plines)
    out_lines, prefix_changed = [], 0
    in_pos = False
    for ln in txt.split("\n"):
        if re.match(r"^\s*prefix\s*=", ln):
            out_lines.append(ln.replace(stem, new_stem))
            prefix_changed += 1
        elif ln.startswith("ATOMIC_POSITIONS"):
            in_pos = True
            out_lines.append(ln)
        elif in_pos and len(ln.split()) >= 4 and ln.split()[0] in labels:
            out_lines.append(next(it))
        else:
            if in_pos and ln.strip() and not ln[0].isspace():
                in_pos = False
            out_lines.append(ln)
    new_txt = "\n".join(out_lines)

    # G6 -- diff shape: the prefix line plus position lines only, and each
    # changed position line changes only its three coordinate fields
    if prefix_changed != 1:
        fail("G6", f"{stem}: {prefix_changed} prefix lines changed")
    old_lines = txt.split("\n")
    if len(old_lines) != len(out_lines):
        fail("G6", f"{stem}: line count changed")
    pos_set = set(plines)
    for a, b in zip(old_lines, out_lines):
        if a == b:
            continue
        if re.match(r"^\s*prefix\s*=", a):
            continue
        if a not in pos_set:
            fail("G6", f"{stem}: unexpected changed line {a!r}")
        pa, pb = a.split(), b.split()
        if pa[0] != pb[0] or pa[4:] != pb[4:]:
            fail("G6", f"{stem}: a position line changed label or flags: {a!r} -> {b!r}")

    # G7 -- prefix == filename stem (the runner rm -rf's dens/${prefix}.save)
    pm = re.search(r"^\s*prefix\s*=\s*'([^']+)'", new_txt, re.M)
    if not pm or pm.group(1) != new_stem:
        fail("G7", f"{stem}: prefix {pm and pm.group(1)!r} != {new_stem!r}")

    # G8 -- byte hygiene; G9 -- destination
    new_raw = new_txt.encode()
    if raw.endswith(b"\n") != new_raw.endswith(b"\n") or (b"\r\n" in raw) != (b"\r\n" in new_raw):
        fail("G8", f"{stem}: newline/CR bytes changed")
    dest = os.path.join(dest_dir, new_stem + ".in")
    if inside_banked_tree(dest):
        fail("G9", f"{stem}: child would land inside the banked gate-(h) tree")

    os.makedirs(dest_dir, exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(new_raw)

    e_anchor_m = re.findall(r"^!\s*total energy\s*=\s*(-\d+\.\d+)\s*Ry",
                            open(os.path.join(SRC_DIR, stem + ".out"),
                                 errors="replace").read(), re.M)
    return dict(stem=new_stem, e_relax_ry=e_relax,
                gain_mev=(e_relax - float(e_anchor_m[-1])) * RY_MEV,
                totmag=rtot, absmag=rabs, max_disp=max_disp,
                md5=hashlib.md5(new_raw).hexdigest())


def cmd_gate1(quarantine: list[str] | None = None, out_root: str | None = None) -> int:
    """Default: all four or none (the lit2 idiom). --quarantine STEM excuses a
    named casualty EXPLICITLY: the stem must have no scoreable .out AND must
    carry .out.attempt* evidence that it ran and failed -- a quarantine is a
    recorded casualty, never a shortcut past an unrun job. The deposited rule
    (docs/43:311-314) owes a child per RELAXATION WITH A FINAL GEOMETRY; a
    relaxation that died mid-SCF has none yet, so its child is deferred, not
    skipped -- it becomes owed the moment a repair attempt converges.
    """
    quarantine = quarantine or []
    for s in quarantine:
        if s not in STEMS:
            fail("Q1", f"--quarantine {s}: not one of this family's stems")
        if os.path.exists(os.path.join(OUT_DIR, s + "__relax.out")):
            fail("Q2", f"--quarantine {s}: a scoreable .out EXISTS -- a converged "
                       "relaxation cannot be quarantined, its child is owed")
        ev = [f for f in os.listdir(OUT_DIR)
              if f.startswith(s + "__relax.out.attempt")]
        if not ev:
            fail("Q3", f"--quarantine {s}: no .out.attempt* evidence on disk -- "
                       "quarantine records a casualty, it does not excuse an unrun job")

    live = [s for s in STEMS if s not in quarantine]
    missing = [s for s in live
               if not os.path.exists(os.path.join(OUT_DIR, s + "__relax.out"))]
    if missing:
        print("GATE-1 children: REFUSED -- "
              f"{len(missing)} of {len(live)} non-quarantined relaxations have not run yet.")
        for s in missing:
            print(f"  unrun: {s}__relax")
        print("\nThe deposited GATE-1 rule (docs/43:311-314) builds each __g1 child from its\n"
              "parent's CONVERGED final geometry. Refusing to emit a partial family --\n"
              "every non-quarantined relaxation, or none.")
        return 1

    dest_dir, man = out_paths(out_root, "m_h_afm_g1.txt")
    rows = [gate1_one(s, dest_dir) for s in live]
    print(f"Built {len(rows)} GATE-1 children under {show(dest_dir)}/\n")
    print(f"{'stem':<36}{'E_relax (Ry)':>18}{'gain (meV)':>12}{'totmag':>9}{'maxdisp A':>11}")
    for r in rows:
        print(f"{r['stem']:<36}{r['e_relax_ry']:>18.8f}{r['gain_mev']:>12.3f}"
              f"{r['totmag']:>9.2f}{r['max_disp']:>11.4f}")

    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# S0 gate (h) GATE-1 children -- src/dft/build_h_afm_relax.py --gate1\n")
        fh.write("# Deposited rule docs/43:311-314: one fresh-density fixed-geometry SCF\n")
        fh.write("# per relaxation at its own final coordinates. Scoring at landing:\n")
        fh.write("#   * >= 5 meV BELOW its relaxation -> BASIN_DRIFT, re-relax and loop;\n")
        fh.write("#   * > 1 meV ABOVE its relaxation -> A8.3 refusal (density-history\n")
        fh.write("#     artifact), the pair is quarantined;\n")
        fh.write("#   * totmag moving > 0.1 mu_B off the relaxation's final value ->\n")
        fh.write("#     CONFOUNDED (docs/43:305-309), own table, excluded from statistics.\n")
        for s in quarantine:
            ev = sorted(f for f in os.listdir(OUT_DIR)
                        if f.startswith(s + "__relax.out.attempt"))
            fh.write(f"# QUARANTINED (no child owed yet -- no converged final geometry):\n"
                     f"#   {s}__relax; evidence: {', '.join(ev)}\n")
        fh.write("# Comparators (relaxation final energy, Ry / final totmag):\n")
        for r in rows:
            fh.write(f"#   {r['stem']}: {r['e_relax_ry']:.8f} / {r['totmag']:.2f}\n")
        fh.write("#   dir job suffix nk  (nk = m_s3_wave1.txt's 2x1v convention)\n")
        for r in rows:
            nk = 16 if r["stem"].startswith("ref") else 8
            fh.write(f"s0/h_afm_relax {r['stem']} .in {nk}\n")
    print(f"\nMANIFEST WRITTEN: {show(man)}")
    return 0


def cmd_repair_mixing(stem: str, out_root: str | None = None) -> int:
    """One repair attempt on a relaxation that died mid-SCF: the committed relax
    deck with mixing_beta HALVED and a fresh prefix -- nothing else.

    This transplants rung (ii) of the A6.5(2) repair ladder ("halve the mixing
    beta"), registered for non-convergent A0 points, to this family BY ANALOGY
    -- the A0 registration does not cover S0(h), and this function does not
    claim it does. mixing_beta is solver machinery, not a registered quantity;
    halving it changes the SCF path, never the physics. If the repair also
    fails, rung (iii) is the licensed exit: the row is recorded NOT_CONVERGED
    and reported as a gap.
    """
    if stem not in STEMS:
        fail("R1", f"{stem}: not one of this family's stems")
    relax_in = os.path.join(OUT_DIR, stem + "__relax.in")
    if os.path.exists(os.path.join(OUT_DIR, stem + "__relax.out")):
        fail("R2", f"{stem}__relax.out exists and is scoreable -- a repair of a "
                   "converged relaxation is nonsense")
    if not [f for f in os.listdir(OUT_DIR)
            if f.startswith(stem + "__relax.out.attempt")]:
        fail("R3", f"{stem}: no .out.attempt* evidence -- repair follows a recorded "
                   "failure, it does not preempt one")

    raw = open(relax_in, "rb").read()
    rel = os.path.relpath(relax_in, REPO).replace(os.sep, "/")
    blob = committed_blob(rel)
    if blob is None or hashlib.md5(blob).hexdigest() != hashlib.md5(raw).hexdigest():
        fail("R4", f"{stem}: relax .in is not the committed blob at HEAD ({rel})")

    txt = raw.decode()
    old_stem, new_stem = stem + "__relax", stem + "__relax__r1"
    bm = re.search(r"^(\s*mixing_beta\s*=\s*)([\d.]+)\s*$", txt, re.M)
    if not bm:
        fail("R5", f"{stem}: no mixing_beta line to halve")
    beta = float(bm.group(2))
    out_lines, changed = [], []
    for ln in txt.split("\n"):
        if re.match(r"^\s*prefix\s*=", ln):
            out_lines.append(ln.replace(old_stem, new_stem))
            changed.append("prefix")
        elif re.match(r"^\s*mixing_beta\s*=", ln):
            out_lines.append(f"{bm.group(1)}{beta / 2:g}")
            changed.append("mixing_beta")
        else:
            out_lines.append(ln)
    new_txt = "\n".join(out_lines)

    # R6 -- diff shape: exactly prefix + mixing_beta
    if sorted(changed) != ["mixing_beta", "prefix"] or \
       sum(1 for a, b in zip(txt.split("\n"), out_lines) if a != b) != 2:
        fail("R6", f"{stem}: changed lines are {sorted(changed)}, expected exactly "
                   "mixing_beta + prefix")
    pm = re.search(r"^\s*prefix\s*=\s*'([^']+)'", new_txt, re.M)
    if not pm or pm.group(1) != new_stem:
        fail("R7", f"{stem}: prefix {pm and pm.group(1)!r} != {new_stem!r}")
    new_raw = new_txt.encode()
    if raw.endswith(b"\n") != new_raw.endswith(b"\n") or (b"\r\n" in raw) != (b"\r\n" in new_raw):
        fail("R8", f"{stem}: newline/CR bytes changed")

    dest_dir, man = out_paths(out_root, "m_h_afm_relax_repair.txt")
    dest = os.path.join(dest_dir, new_stem + ".in")
    os.makedirs(dest_dir, exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(new_raw)
    print(f"REPAIR DECK WRITTEN: {show(dest)}")
    print(f"  mixing_beta {beta:g} -> {beta / 2:g} (A6.5(2) rung (ii), BY ANALOGY -- "
          "see docstring); everything else byte-identical to the committed relax deck.")

    nk = 16 if stem.startswith("ref") else 8
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# repair attempt (r1) for {old_stem}: attempt 2 died at\n")
        fh.write("# `convergence NOT achieved after 200 iterations` in its 3rd SCF --\n")
        fh.write("# magnetic oscillation (totmag sloshing -1.6..-2.6, acc touched 1.45e-6\n")
        fh.write("# at it 21 then bounced). Rung (ii) of the A6.5(2) ladder BY ANALOGY:\n")
        fh.write("# halve mixing_beta. If this fails too, rung (iii): the row is recorded\n")
        fh.write("# NOT_CONVERGED and reported as a gap -- no third solver attempt.\n")
        fh.write(f"s0/h_afm_relax {new_stem} .in {nk}\n")
    print(f"MANIFEST WRITTEN: {show(man)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--gate1", action="store_true",
                    help="build the GATE-1 __g1 children (refuses until the relaxations converge)")
    ap.add_argument("--quarantine", action="append", default=[], metavar="STEM",
                    help="with --gate1: excuse a recorded casualty (needs .out.attempt* "
                         "evidence and no scoreable .out); its child is deferred, not skipped")
    ap.add_argument("--repair-mixing", metavar="STEM",
                    help="emit a __relax__r1 repair deck: mixing_beta halved, fresh prefix, "
                         "nothing else (A6.5(2) rung (ii) by analogy)")
    ap.add_argument("--out-dir", metavar="DIR", default=None,
                    help="build into DIR instead of runs/s0: decks under DIR/h_afm_relax/, "
                         "the manifest in DIR/. Inputs are still read from the tracked tree; "
                         "nothing tracked is written (default: runs/s0, the live tree)")
    args = ap.parse_args()

    if args.repair_mixing:
        return cmd_repair_mixing(args.repair_mixing, args.out_dir)
    if args.gate1:
        return cmd_gate1(args.quarantine, args.out_dir)

    dest_dir, man = out_paths(args.out_dir, "m_h_afm_relax.txt")
    rows = [build_one(s, dest_dir) for s in STEMS]

    print(f"Built {len(rows)} AFM relaxation decks under {show(dest_dir)}/\n")
    print(f"{'stem':<30}{'nat':>5}{'ntyp':>6}{'pair':>12}{'idx':>8}{'seeds':>14}{'frozen':>8}")
    for r in rows:
        pair = r["pair"][0] + "/" + r["pair"][1]
        seeds = f"{r['seeds'][0]:+.1f}/{r['seeds'][1]:+.1f}"
        print(f"{r['stem']:<30}{r['nat']:>5}{r['ntyp']:>6}{pair:>12}"
              f"{str(r['pair_index']):>8}{seeds:>14}{r['frozen']:>8}")

    res = afm_scope_resolution()
    print()
    if res is None:
        print("MANIFEST: NOT WRITTEN -- the gate-(h) AFM scope is on HOLD.")
        print()
        print("  docs/43:1645 (deposited, ADOPTION NOTE 2026-08-23) leaves it open whether")
        print("  these four are standalone S3-class jobs or the Ru second seed inside")
        print("  tier_v3's crossed magnetic-basin factor (up to 16 relaxations), and states")
        print("  that no default was drafted. The decks above are common to both readings")
        print("  and cost no SU; the manifest the submit script consumes is withheld.")
        print()
        print("  To lift, add one dated line to docs/43 whose machine-readable head is:")
        print("      [AFM-SCOPE RESOLVED YYYY-MM-DD: STANDALONE_FOUR]")
        print("    or")
        print("      [AFM-SCOPE RESOLVED YYYY-MM-DD: SECOND_SEED_CROSSED]")
        print("  then re-run this builder.")
        return 2

    date, scope = res
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# S0 gate (h) AFM relaxations -- built by src/dft/build_h_afm_relax.py\n")
        fh.write(f"# scope resolved {date}: {scope} (docs/43 AFM-SCOPE line)\n")
        fh.write(f"# family is >= 8 decks: these 4 relaxations + 4 GATE-1 __g1 children\n")
        fh.write("# 4-field rows for anvil/42_s3_wave1.slurm via 43_submit_s3_wave1.sh:\n")
        fh.write("#   dir job suffix nk\n")
        fh.write("# nk follows m_s3_wave1.txt's measured 2x1v convention: clean ref 16,\n")
        fh.write("# adsorbate rows 8 (same cell, same 4 4 1 mesh, same nspin = 2 class).\n")
        if scope == "SECOND_SEED_CROSSED":
            fh.write("# NOTE: these four are the 2x1v/off arm only; the remaining crossed\n"
                     "#       arms are owed from the S3 builder, not from this one.\n")
        for r in rows:
            nk = 16 if r["stem"].startswith("ref") else 8
            fh.write(f"s0/h_afm_relax {r['stem']} .in {nk}\n")
    print(f"MANIFEST WRITTEN ({scope}, resolved {date}): {show(man)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
