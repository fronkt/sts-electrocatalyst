#!/usr/bin/env python
"""A0-cell: the registered Cr 2x1v U ladder (2026-08-27).

A6.1(b), registered verbatim (docs/43 :1198-1204):

    "A0-cell, newly registered. A Cr-only 2x1v arm: four states (`ref`, `*O`,
     `*OH`, `*OOH`) x five U points = 20 fixed-geometry SCFs, run on block 1A's
     already-relaxed 2x1v Cr geometries. The builder must take those geometries
     from the production set that defines `tier_v3`, not re-pick them -- a
     different 2x1v geometry would confound the cell comparison with a geometry
     comparison.
     U points: the four already on the ladder -- `u0.0` = 0, `u0.5` = 1.85,
     `base` = 3.70, `u1.35` = 5.00 eV -- plus 7.15 eV, which is Xu, Rossmeisl &
     Kitchin 2015 Table 1's linear-response U for CrO2. The fifth point is an
     external anchor, not a free choice made after seeing the first four."

This builds SIXTEEN of the twenty: four states x the four ladder U points. The
fifth point (7.15 eV) is NOT built here -- A7.1 gates it: "Before any A0 deck is
built on the fifth grid point", the projector pairing must run. That is array
20178163, in flight. The 7.15 rung is built after it scores.

WHY THIS MATTERS: A6.1 records that block 6A "has never been built or run; only
the inherited four-point ladders exist." P7 -- the withdrawn eta(Cr) headline,
the 1.122 V swing -- was measured in the 1x1 cell, and A6.2's registered test
I_U = span(2x1v) - span(1x1) prices whether the U error and the cell error are
separable at all. Thresholds are inherited verbatim from the block-1A
interaction bins: |I_U| < 0.05 eV additive, >= 0.30 eV not separable,
0.05-0.30 inconclusive. Prior on record: additive.

WHICH GEOMETRY IS "THE PRODUCTION SET" -- the one determination this builder had
to make, and the evidence for it.

Block 1A crossed cell x symmetry, so every 2x1v adsorbate state exists in BOTH a
`_mir` arm (symmetry ON) and an `_off` arm (`nosym` + displacement). A6.1 says
take the production geometry and do not re-pick, but does not name the arm.

It is fixed by the leg this arm is compared against. A6.2's I_U subtracts
span(1x1), and the 1x1 ladder decks -- runs/probe/Cr/{s0_O,s0_OH,s0_OOH}__*.in --
carry NO nosym and NO noinv: they are symmetry-ON, and pw.x finds 4 Sym. Ops. on
them. The symmetry-ON 2x1v counterpart is the `_mir` arm (pw.x finds 2 Sym. Ops.);
the `_off` arm sets nosym+noinv and pw.x reports "No symmetry found". Taking
`_off` would change the symmetry treatment and the cell in the same step, which
is precisely the confound A6.1 forbids. So: `_mir`.

The bare reference follows the same rule in the other direction. The 1x1 bare
deck runs/probe/Cr/slab__base.in DOES carry nosym+noinv, and so does
runs/probe/Cr_cellsym/ref__2x1v.in. They match as they stand.

*OOH IS THE EXCEPTION, AND IT IS THE LEDGER'S CALL, NOT THIS BUILDER'S.
docs/45 records: "Cr *OOH 2x1v mir arm energy of record = the escape minimum
-3188.71606 Ry (saddle -3188.70497 retained as diagnostic)". The mir relax landed
on a saddle -- docs/49 s7c confirms the mirror geometry IS a saddle -- and the
escape run found the minimum 150.8 meV below it. The geometry of record for the
mir arm is therefore the escape minimum, and this builder uses it. Its deck
carries `nosym` because the escape geometry is off-mirror by construction; that
is inherited, not chosen here.

    Scope note, stated so it cannot be over-read: the registered I_U test uses
    D(cell) = dG_O - dG_OH and does NOT involve *OOH. The *OOH rung feeds the
    full eta and the second readout (whether the volcano-apex crossing moves
    between cells), not the A6.2 threshold. So this choice cannot move the
    registered number; it is reported because it is contestable, not because it
    is load-bearing.

DECK CONSTRUCTION. Each deck is its source relax deck with exactly:
  - calculation 'relax' -> 'scf'          (fixed geometry, the A0 idiom)
  - prefix -> <source stem>__<variant>
  - ATOMIC_POSITIONS -> the source run's FINAL BFGS coordinates
  - the U value, or for u0.0 the HUBBARD card and its U line removed entirely
    (matching runs/probe/Cr/s0_O__u0.0.in, which carries no HUBBARD card at all)
Nothing else moves: cell, cutoffs, k-mesh, smearing, nspin, mixing, conv_thr and
the nosym/noinv flags are inherited byte-for-byte from the source deck. All four
sources already carry mixing_mode='local-TF' and mixing_beta=0.3, so unlike the
1x1 probe idiom this builder adds nothing.

These are FIXED-GEOMETRY SINGLE POINTS on already-relaxed structures. Relaxation
under the changed U is NOT included and these must never be reported as relaxed
(runs/probe/Cr/probe_manifest.json carries the same warning for the 1x1 ladder).
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402

DST_DIR = os.path.join(W.ROOT, "runs", "a0", "cell")

# state, source deck stem (relative to ROOT), why this source
SOURCES = [
    ("ref", "runs/probe/Cr_cellsym/ref__2x1v",
     "bare 2x1v reference; nosym+noinv, matching the 1x1 bare deck slab__base"),
    ("s0_O", "runs/probe/Cr_cellsym/s0_O__2x1v_mir",
     "mir arm = symmetry-ON, the counterpart of the symmetry-ON 1x1 ladder"),
    ("s0_OH", "runs/probe/Cr_cellsym/s0_OH__2x1v_mir",
     "mir arm = symmetry-ON, the counterpart of the symmetry-ON 1x1 ladder"),
    ("s0_OOH", "runs/s3/Cr/s0_OOH__2x1v_escape",
     "mir arm ENERGY OF RECORD is the escape minimum (docs/45); the mir relax "
     "landed on a saddle 150.8 meV above it"),
]

# variant token -> U value string, or None to drop the HUBBARD card entirely.
# Values are the ladder's own, read off the 1x1 decks rather than recomputed:
# u0.0 has no HUBBARD card, u0.5 = 1.8500, base = 3.7000, u1.35 = 4.9950.
VARIANTS = [("u0.0", None), ("u0.5", "1.8500"), ("base", "3.7000"), ("u1.35", "4.9950")]

U_LINE = re.compile(r"^U Cr-3d\s+[\d.]+\s*$", re.M)
HUBBARD_LINE = re.compile(r"^HUBBARD \(atomic\)\s*$", re.M)
NK = 8  # 9/10/16 irreducible k-points across the four states; 8 divides 128 and fits all


def ladder_u_values():
    """Read the ladder's U values off the 1x1 decks; never hard-code silently."""
    got = {}
    for tok in ("u0.0", "u0.5", "base", "u1.35"):
        p = os.path.join(W.ROOT, "runs", "probe", "Cr", "s0_O__%s.in" % tok)
        if not os.path.exists(p):
            W.die("%s: 1x1 ladder deck missing -- cannot confirm the U value" % W.rel(p))
        t = W.read(p)
        m = U_LINE.search(t)
        got[tok] = m.group(0).split()[-1] if m else None
        if (m is None) != (tok == "u0.0"):
            W.die("%s: HUBBARD card presence does not match variant %s" % (W.rel(p), tok))
    want = {tok: val for tok, val in VARIANTS}
    if got != want:
        W.die("ladder U values on disk %r differ from this builder's %r" % (got, want))
    print("  ladder U values confirmed against the 1x1 decks: %r" % got)


def build_state(state, stem, why):
    src_in = os.path.join(W.ROOT, stem + ".in")
    src_out = os.path.join(W.ROOT, stem + ".out")
    for p in (src_in, src_out):
        if not os.path.exists(p):
            W.die("%s: source missing" % W.rel(p))

    src = W.read(src_in)
    m = re.search(r"^\s*calculation\s*=\s*'(\w+)'", src, re.M)
    if not m or m.group(1) != "relax":
        W.die("%s: expected a relax deck, found %r" % (W.rel(src_in), m and m.group(1)))
    if W.FORBIDDEN_RESTART.search(src):
        W.die("%s: source deck carries a restart directive" % W.rel(src_in))
    if HUBBARD_LINE.search(src) is None or len(U_LINE.findall(src)) != 1:
        W.die("%s: expected exactly one HUBBARD (atomic) + one U Cr-3d line" % W.rel(src_in))

    src_rows = W.selftest_formatter(src, src_in)
    nat = int(re.search(r"^\s*nat\s*=\s*(\d+)", src, re.M).group(1))
    if nat != len(src_rows):
        W.die("%s: nat=%d but %d position lines" % (W.rel(src_in), nat, len(src_rows)))

    out = W.read(src_out)
    if "bfgs converged" not in out or out.count("Begin final coordinates") != 1:
        W.die("%s: relax not converged -- no final geometry to take" % W.rel(src_out))
    pos, prov = W.parse_final_coordinates(src_out)   # takes a PATH, not the text
    if pos is None or prov != "final":
        W.die("%s: geometry provenance %r, expected 'final'" % (W.rel(src_out), prov))
    if len(pos) != len(src_rows) or [p[0] for p in pos] != [r[0] for r in src_rows]:
        W.die("%s: species/count mismatch vs its own deck" % W.rel(src_out))

    # final coordinates, carrying each atom's if_pos flags from the source deck
    new_rows = [(sp, "%.8f" % x, "%.8f" % y, "%.8f" % z, r[4])
                for (sp, x, y, z), r in zip(pos, src_rows)]

    made = []
    for tok, uval in VARIANTS:
        stem_new = "%s__%s" % (os.path.basename(stem), tok)
        dst = os.path.join(DST_DIR, stem_new + ".in")
        dst_out = os.path.join(DST_DIR, stem_new + ".out")
        for p in (dst, dst_out):
            if os.path.exists(p):
                W.die("%s already exists -- refusing to overwrite (A8.8)" % W.rel(p))

        new = W.swap_scalar_line(src, src_in, "prefix", os.path.basename(stem), stem_new)
        new = re.sub(r"^(\s*calculation\s*=\s*)'relax'", r"\1'scf'", new, count=1, flags=re.M)
        new = W.swap_positions(new, src_in, new_rows)
        if uval is None:
            new = HUBBARD_LINE.sub("", new)
            new = U_LINE.sub("", new)
            new = re.sub(r"\n{3,}", "\n\n", new).rstrip("\n") + "\n"
        else:
            new = U_LINE.sub("U Cr-3d %s" % uval, new)

        # assertions on the product, not the process
        if re.search(r"calculation\s*=\s*'scf'", new) is None:
            W.die("%s: calculation is not scf" % W.rel(dst))
        if ("prefix = '%s'" % stem_new) not in new:
            W.die("%s: prefix not set" % W.rel(dst))
        if uval is None:
            if HUBBARD_LINE.search(new) or U_LINE.search(new):
                W.die("%s: u0.0 must carry no HUBBARD card" % W.rel(dst))
        else:
            if len(U_LINE.findall(new)) != 1 or U_LINE.search(new).group(0).split()[-1] != uval:
                W.die("%s: U value not %s" % (W.rel(dst), uval))
            if HUBBARD_LINE.search(new) is None:
                W.die("%s: HUBBARD card lost" % W.rel(dst))
        if W.FORBIDDEN_RESTART.search(new):
            W.die("%s: restart directive appeared" % W.rel(dst))
        for block in ("CELL_PARAMETERS", "K_POINTS", "ATOMIC_SPECIES"):
            a = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, src, re.S | re.M)
            b = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, new, re.S | re.M)
            if (a is None) != (b is None) or (a and a.group(1) != b.group(1)):
                W.die("%s: %s changed" % (W.rel(dst), block))
        got_rows = W.selftest_formatter(new, dst)
        if len(got_rows) != nat:
            W.die("%s: nat=%d but %d position lines" % (W.rel(dst), nat, len(got_rows)))
        if [r[4] for r in got_rows] != [r[4] for r in src_rows]:
            W.die("%s: if_pos flags changed" % W.rel(dst))

        W.write(dst, new)
        made.append((stem_new, tok, uval, nat))
        print("    built %-46s nat=%-3d U=%s" % (W.rel(dst), nat, uval or "0 (no card)"))
    return made, prov, os.path.basename(stem)


HDR = """\
# A0-cell: the registered Cr 2x1v U ladder, 16 of the 20 SCFs.
# Built 2026-08-27 by src/dft/build_a0cell.py.
#
# A6.1(b), verbatim: "A Cr-only 2x1v arm: four states (`ref`, `*O`, `*OH`,
# `*OOH`) x five U points = 20 fixed-geometry SCFs, run on block 1A's
# already-relaxed 2x1v Cr geometries. The builder must take those geometries
# from the production set that defines `tier_v3`, not re-pick them -- a
# different 2x1v geometry would confound the cell comparison with a geometry
# comparison."
#
# SIXTEEN HERE, NOT TWENTY. The fifth U point (7.15 eV) is gated by A7.1:
# "Before any A0 deck is built on the fifth grid point" the projector pairing
# must run. That is array 20178163, in flight. The 7.15 rung is built after it
# scores -- and if P-PROJ fires (|d-eta| > 0.10 V), :1338 says the fifth point is
# labelled PROJECTOR-MISMATCHED and the whole grid runs in ONE projector.
#
# ARM SELECTION, the one determination this builder made. Block 1A crossed
# cell x symmetry, so each adsorbate state has a `_mir` (symmetry ON) and an
# `_off` (nosym+noinv) arm, and A6.1 does not name one. It is fixed by the leg
# A6.2 subtracts: the 1x1 ladder decks carry no nosym and no noinv, so the
# like-for-like 2x1v counterpart is `_mir`. Taking `_off` would move symmetry
# and cell in one step -- the confound A6.1 forbids. The bare reference matches
# the other way: 1x1 slab__base and 2x1v ref__2x1v both carry nosym+noinv.
#
# *OOH uses the ESCAPE minimum, not the mir relax. docs/45: "Cr *OOH 2x1v mir
# arm energy of record = the escape minimum -3188.71606 Ry (saddle -3188.70497
# retained as diagnostic)". The mir relax sits on a saddle 150.8 meV above it.
# The escape deck's `nosym` is inherited, not chosen: that geometry is off-mirror
# by construction. NOTE the registered I_U test uses D = dG_O - dG_OH and does
# NOT involve *OOH, so this choice cannot move the A6.2 number.
#
# SCORING (A6.2). D(cell) = dG_O - dG_OH per U point; span = max_U D - min_U D;
# I_U = span(2x1v) - span(1x1). Thresholds inherited verbatim from the block-1A
# interaction bins and NOT re-derived: |I_U| < 0.05 eV additive; >= 0.30 eV not
# separable; 0.05-0.30 inconclusive, "not rounded toward either". Prior on
# record: additive. Second readout from the same arm, no extra compute: if the
# two cells place the volcano-apex crossing at U values differing by more than
# 1.0 eV, A0's "the crossing is located rather than bracketed" claim is
# cell-conditional and must be reported as such.
#
# These are FIXED-GEOMETRY SINGLE POINTS on already-relaxed structures.
# Relaxation under the changed U is not included; they must never be reported as
# relaxed.
#
# SUBMIT WITH EXCLUDE=a024,a050,a088,a196,a220,a223
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""


def main():
    os.makedirs(DST_DIR, exist_ok=True)
    ladder_u_values()

    rows, prov_note = [], {}
    for state, stem, why in SOURCES:
        print("  %s  <- %s" % (state, stem))
        print("      %s" % why)
        made, prov, base = build_state(state, stem, why)
        prov_note[state] = {"source_deck": stem + ".in", "source_out": stem + ".out",
                            "geometry_provenance": prov, "why": why,
                            "decks": [m[0] for m in made]}
        for stem_new, tok, uval, nat in made:
            rows.append(("a0/cell", stem_new, ".in", NK, state, tok, uval, nat))

    body = []
    for _d, job, _s, nk, state, tok, uval, nat in rows:
        body.append("#   %-38s nat=%-3d nk=%-2d  Cr 2x1v %s, %s, U=%s\n"
                    % (job, nat, nk, state, tok, uval or "0 (no HUBBARD card)"))
    hdr = HDR.rstrip("\n") + "\n#\n" + "".join(body) + "#\n"
    hits = [l for l in hdr.splitlines() if "NP=" in l or "NCONC=" in l]
    if hits != ["# NP=128 NCONC=1"]:
        W.die("manifest header must mention NP=/NCONC= exactly once; found %r" % hits)

    txt = hdr + "".join("%s %s %s %d\n" % (d, job, s, nk)
                        for d, job, s, nk, _a, _b, _c, _n in rows)
    path = os.path.join(W.ROOT, "runs", "a0", "m_a0cell.txt")
    if os.path.exists(path):
        W.die("%s already exists -- refusing to overwrite" % W.rel(path))
    W.write(path, txt)

    man = os.path.join(DST_DIR, "manifest.json")
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({
            "arm": "A0-cell (A6.1b)",
            "registered_at": "docs/43-prereg-week1-factorial.md:1198-1204",
            "built": len(rows), "registered_total": 20,
            "fifth_point_gated_by": "A7.1 P-PROJ (array 20178163); U = 7.15 eV not built here",
            "calculation": "scf",
            "note": ("FIXED-GEOMETRY single points on already-relaxed structures. "
                     "Relaxation under the changed U is NOT included and these must "
                     "not be reported as relaxed."),
            "variants": [t for t, _ in VARIANTS],
            "u_values": {t: (u or "0 (no HUBBARD card)") for t, u in VARIANTS},
            "nk": NK,
            "states": prov_note,
        }, fh, indent=2)

    print("\nwrote %s  (%d rows)" % (W.rel(path), len(rows)))
    print("wrote %s" % W.rel(man))


if __name__ == "__main__":
    main()
