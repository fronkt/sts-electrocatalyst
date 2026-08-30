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
A12 every child path is under runs/s0/h_afm_relax/, never runs/s0/h_afm_anchor/,
    which the gate-(h) readout and docs/63 address literally
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


def build_one(stem: str) -> dict:
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
    dest = os.path.join(OUT_DIR, new_stem + ".in")
    if os.path.commonpath([os.path.abspath(dest), os.path.abspath(SRC_DIR)]) == os.path.abspath(SRC_DIR):
        fail("A12", f"{stem}: child would land inside the banked gate-(h) tree")

    # A13 -- byte hygiene
    new_raw = new_txt.encode()
    if raw.endswith(b"\n") != new_raw.endswith(b"\n"):
        fail("A13", f"{stem}: trailing-newline byte changed")
    if (b"\r\n" in raw) != (b"\r\n" in new_raw):
        fail("A13", f"{stem}: CR bytes changed")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(new_raw)

    n_frozen = sum(1 for f in constraint_flags(txt, labels) if f == "0 0 0")
    return dict(stem=new_stem, parent=rel, path=os.path.relpath(dest, REPO).replace(os.sep, "/"),
                nat=nat, ntyp=len(species), pair=(ru1, ru2),
                pair_index=(idx[ru1], idx[ru2]), seeds=(s1, s2), frozen=n_frozen,
                parent_md5=hashlib.md5(raw).hexdigest(),
                child_md5=hashlib.md5(new_raw).hexdigest())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--gate1", action="store_true",
                    help="build the GATE-1 __g1 children (refuses until the relaxations converge)")
    args = ap.parse_args()

    if args.gate1:
        missing = [s for s in STEMS
                   if not os.path.exists(os.path.join(OUT_DIR, s + "__relax.out"))]
        print("GATE-1 children: REFUSED -- "
              f"{len(missing)} of {len(STEMS)} relaxations have not run yet.")
        for s in missing:
            print(f"  unrun: {s}__relax")
        print("\nThe deposited GATE-1 rule (docs/43:311-314) builds each __g1 child from its\n"
              "parent's CONVERGED final geometry. There is nothing to build from yet.")
        return 1

    rows = [build_one(s) for s in STEMS]

    print(f"Built {len(rows)} AFM relaxation decks under "
          f"{os.path.relpath(OUT_DIR, REPO).replace(os.sep, '/')}/\n")
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
    man = os.path.join(REPO, "runs", "s0", "m_h_afm_relax.txt")
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# S0 gate (h) AFM relaxations -- built by src/dft/build_h_afm_relax.py\n")
        fh.write(f"# scope resolved {date}: {scope} (docs/43 AFM-SCOPE line)\n")
        fh.write(f"# family is >= 8 decks: these 4 relaxations + 4 GATE-1 __g1 children\n")
        if scope == "SECOND_SEED_CROSSED":
            fh.write("# NOTE: these four are the 2x1v/off arm only; the remaining crossed\n"
                     "#       arms are owed from the S3 builder, not from this one.\n")
        for r in rows:
            fh.write(r["path"] + "\n")
    print(f"MANIFEST WRITTEN ({scope}, resolved {date}): "
          f"{os.path.relpath(man, REPO).replace(os.sep, '/')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
