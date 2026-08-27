#!/usr/bin/env python
"""A0-main: the registered dense eta(U) grid, 140 fixed-geometry SCFs (2026-08-27).

REGISTERED SCOPE

  §4 / block 6A: "The eta(U) grid over 0-9 eV from pw.x alone (140 fixed-geometry
  SCFs, block 6A) does not depend on hp.x at all, and it answers P7."

  A6.1(a): "A0-main, unchanged. Dense eta(U) grid, U = 0-9 eV, fixed geometry,
  1x1 cell, pw.x only, ~140 SCFs -- exactly as block 6A registered it."
  Rationale, quoted: "P7 -- the withdrawn eta(Cr) headline, the 1.122 V swing --
  was measured in the 1x1 cell. A0's registered job is to bound THAT claim."

  A6.3: "A0-main spans U for Ru and Ir as well as the 3d metals, over the same
  0-9 eV range, with Xu's computed values marked as declared anchor points."
  Pre-registered, falsifiable: "the reference ordering Ir < Ru is stable across
  U in [0, 9] eV."

THE GRID, AND WHY IT IS ALLOCATED RATHER THAN UNIFORM

The registered text fixes the range (0-9 eV), the cell (1x1), the calculation
(fixed geometry), the metals (3d plus Ru and Ir) and the scale (~140 SCFs). It
does NOT fix a step. This allocation was chosen before any A0 number existed and
is recorded here so it can be attacked:

    Cr   4 states x 19 points (0.0 to 9.0 by 0.5)                    =  76
    Ru   4 states x (7 points 0.0 to 9.0 by 1.5  + 6.73 Xu anchor)   =  32
    Ir   4 states x (7 points 0.0 to 9.0 by 1.5  + 5.91 Xu anchor)   =  32
                                                                       ---
                                                                       140

The two arms answer different questions and do not deserve the same resolution.

  Cr is a LOCATION question. A0's registered job is to bound P7's 1.122 V swing,
  which is a claim about where eta(U) moves and how sharply. 0.5 eV pins the
  transition to +/-0.25 eV, comfortably inside the 1.0 eV threshold A6.2 sets for
  "the crossing moves between cells". A coarser grid could report a bracket but
  not a location, which is the failure A6.2's second readout exists to catch.

  Ru and Ir are an ORDERING question: "the reference ordering Ir < Ru is stable
  across U in [0, 9] eV." Detecting an inversion needs coverage, not resolution
  -- an ordering flip visible only between 1.5 eV samples would not be a
  defensible claim in any case. Xu's linear-response values (Ru 6.73, Ir 5.91)
  get their own points rather than being rounded onto the grid, because A6.3
  registers them as "declared anchor points".

  METAL SET: an inference, flagged as one. A6.3 says "the 3d metals", plural.
  Only Cr, Mn and Fe have complete four-state 1x1 sets (Co and Ni have no *OOH,
  Cu has only *OOH). Five metals x 4 states x 7 points is ALSO exactly 140 -- a
  uniform-coarse reading that includes Mn and Fe. It is cleaner arithmetically
  and worse scientifically: 7 points over 0-9 eV cannot bound a 1.122 V swing.
  The entrant chose Cr 19 / Ru 7+1 / Ir 7+1 on 2026-08-27.

  NO POST-HOC REFINEMENT. A6.6's logic -- "an interaction test registered after
  the grid is read is not a test" -- applies to the grid itself. A grid refined
  where it looked interesting is a grid tuned to its answer. If a second tranche
  is wanted, its trigger is declared before this one is read, not after.

DECK CONSTRUCTION

Sources are the banked 1x1 probe decks runs/probe/<M>/{slab,s0_O,s0_OH,s0_OOH}__base.in,
which are ALREADY fixed-geometry SCFs on the final relaxed geometry of the
production run (runs/probe/<M>/probe_manifest.json: geometry_provenance "final",
with its own warning that these are leading-order sensitivity points and must
not be reported as relaxed). So each A0 deck is its source with:

  - prefix -> <state>__u<NNN>, NNN = U x 100, the explicit-value naming the
    e_proj decks already use (`u715`); the ladder's `u0.5`/`u1.35` tokens are
    MULTIPLIERS of 3.70 and are deliberately not reused here
  - Cr, U > 0 : the U value swapped                       (2 lines differ)
  - Cr, U = 0 : the HUBBARD card and its U line removed   (3 lines differ)
  - Ru/Ir, U > 0 : a HUBBARD (atomic) card APPENDED       (prefix + 2 added)
  - Ru/Ir, U = 0 : nothing but the prefix                 (1 line differs)

Ru and Ir carry no HUBBARD card at all in production -- U = 0 by the MP
convention -- so their U > 0 decks add one. Orbitals are Ru-4d and Ir-5d. The
projector is `(atomic)`, matching production and the P-PROJ production leg.

Geometry, cell, k-mesh, species, cutoffs, smearing, nspin, mixing and conv_thr
are inherited byte-for-byte. Nothing is relaxed.

A6.5 AND THIS BUILDER

  (1) "Every A0 point either retains its .save or runs projwfc.x in the same
      job." Satisfied by the RUNNER, anvil/46_a0.slurm, not by the decks.
  (2) The escalation ladder for non-convergent points -- (i) restart from the
      converged neighbouring-U density as `startingpot`; (ii) halve mixing beta;
      (iii) record NOT_CONVERGED and plot as a gap -- is a REPAIR applied after a
      failure. No deck here carries a restart directive, and this builder asserts
      that. Note that remedy (i) is registered for A0 and is exactly what S3's
      build_s3_wave2.FORBIDDEN_RESTART forbids for S3: the prohibition is
      stage-specific and must not be carried across.
  (3) The GATE-1 precondition binds the 2x1v arm (A0-cell), not this one.
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402

DST_ROOT = os.path.join(W.ROOT, "runs", "a0", "main")
STATES = ["slab", "s0_O", "s0_OH", "s0_OOH"]
NK = 4  # 15 irreducible k-points on the adsorbate states; matches the e_proj manifest

CR_GRID = [round(0.5 * i, 2) for i in range(19)]                 # 0.00 .. 9.00
REF_GRID = [0.0, 1.5, 3.0, 4.5, 6.0, 7.5, 9.0]
METALS = [
    ("Cr", "3d", CR_GRID, None,
     "location arm: bounds P7's 1.122 V swing, 0.5 eV -> transition to +/-0.25 eV"),
    ("Ru", "4d", REF_GRID, 6.73,
     "ordering arm: A6.3's Ir < Ru stability test; 6.73 eV is Xu's declared anchor"),
    ("Ir", "5d", REF_GRID, 5.91,
     "ordering arm: A6.3's Ir < Ru stability test; 5.91 eV is Xu's declared anchor"),
]

HUBBARD_LINE = re.compile(r"^HUBBARD \(atomic\)\s*$", re.M)


def u_token(u):
    """Explicit-value token, the e_proj `u715` convention. 0.5 -> u050, 6.73 -> u673."""
    n = int(round(u * 100))
    return "u%03d" % n


def u_line_re(elem, orb):
    return re.compile(r"^U %s-%s\s+[\d.]+\s*$" % (elem, orb), re.M)


def build_metal(elem, orb, grid, anchor, why):
    src_dir = os.path.join(W.ROOT, "runs", "probe", elem)
    dst_dir = os.path.join(DST_ROOT, elem)
    os.makedirs(dst_dir, exist_ok=True)
    U_LINE = u_line_re(elem, orb)

    points = list(grid) + ([anchor] if anchor is not None else [])
    if len(set(u_token(u) for u in points)) != len(points):
        W.die("%s: two grid points collide on one token" % elem)

    rows = []
    for state in STATES:
        src_in = os.path.join(src_dir, state + "__base.in")
        src_out = os.path.join(src_dir, state + "__base.out")
        for p in (src_in, src_out):
            if not os.path.exists(p):
                W.die("%s: source missing" % W.rel(p))
        src = W.read(src_in)

        m = re.search(r"^\s*calculation\s*=\s*'(\w+)'", src, re.M)
        if not m or m.group(1) != "scf":
            W.die("%s: expected a fixed-geometry scf, found %r"
                  % (W.rel(src_in), m and m.group(1)))
        if W.FORBIDDEN_RESTART.search(src):
            W.die("%s: source carries a restart directive" % W.rel(src_in))
        out = W.read(src_out)
        if "JOB DONE" not in out or "convergence NOT achieved" in out:
            W.die("%s: source run did not converge cleanly" % W.rel(src_out))

        nat = int(re.search(r"^\s*nat\s*=\s*(\d+)", src, re.M).group(1))
        src_rows = W.selftest_formatter(src, src_in)
        if nat != len(src_rows):
            W.die("%s: nat=%d but %d position lines" % (W.rel(src_in), nat, len(src_rows)))

        has_card = bool(HUBBARD_LINE.search(src))
        n_u = len(U_LINE.findall(src))
        if elem == "Cr":
            if not has_card or n_u != 1:
                W.die("%s: expected one HUBBARD (atomic) + one U %s-%s line"
                      % (W.rel(src_in), elem, orb))
        else:
            if has_card or n_u:
                W.die("%s: expected NO HUBBARD card (U = 0 production convention)"
                      % W.rel(src_in))

        for u in points:
            tok = u_token(u)
            stem = "%s__%s" % (state, tok)
            dst = os.path.join(dst_dir, stem + ".in")
            for p in (dst, os.path.join(dst_dir, stem + ".out")):
                if os.path.exists(p):
                    W.die("%s already exists -- refusing to overwrite (A8.8)" % W.rel(p))

            new = W.swap_scalar_line(src, src_in, "prefix", state + "__base", stem)
            if u == 0.0:
                if has_card:
                    new = HUBBARD_LINE.sub("", new)
                    new = U_LINE.sub("", new)
                    new = re.sub(r"\n{3,}", "\n\n", new).rstrip("\n") + "\n"
            else:
                uval = "%.4f" % u
                if has_card:
                    new = U_LINE.sub("U %s-%s %s" % (elem, orb, uval), new)
                else:
                    new = new.rstrip("\n") + "\nHUBBARD (atomic)\nU %s-%s %s\n" % (
                        elem, orb, uval)

            # assertions on the product
            if re.search(r"calculation\s*=\s*'scf'", new) is None:
                W.die("%s: calculation is not scf" % W.rel(dst))
            if ("prefix = '%s'" % stem) not in new:
                W.die("%s: prefix not set" % W.rel(dst))
            if u == 0.0:
                if HUBBARD_LINE.search(new) or U_LINE.search(new):
                    W.die("%s: U = 0 must carry no HUBBARD card" % W.rel(dst))
            else:
                got = U_LINE.findall(new)
                if len(got) != 1 or U_LINE.search(new).group(0).split()[-1] != "%.4f" % u:
                    W.die("%s: U value is not %.4f" % (W.rel(dst), u))
                if len(HUBBARD_LINE.findall(new)) != 1:
                    W.die("%s: expected exactly one HUBBARD card" % W.rel(dst))
            if W.FORBIDDEN_RESTART.search(new):
                W.die("%s: restart directive appeared -- A6.5(2) remedy (i) is a "
                      "REPAIR, never a build-time property" % W.rel(dst))
            for block in ("CELL_PARAMETERS", "ATOMIC_POSITIONS", "K_POINTS",
                          "ATOMIC_SPECIES"):
                a = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, src, re.S | re.M)
                b = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, new, re.S | re.M)
                if (a is None) != (b is None) or (a and a.group(1) != b.group(1)):
                    W.die("%s: %s changed" % (W.rel(dst), block))

            W.write(dst, new)
            rows.append(("a0/main/%s" % elem, stem, ".in", NK, elem, state, u, nat))
    print("  %-3s %-2s %2d U points x 4 states = %3d decks   (%s)"
          % (elem, orb, len(points), len(rows), why))
    return rows, points


HDR = """\
# A0-main: the registered dense eta(U) grid, 140 fixed-geometry SCFs.
# Built 2026-08-27 by src/dft/build_a0main.py.
#
# Block 6A / A6.1(a): "Dense eta(U) grid, U = 0-9 eV, fixed geometry, 1x1 cell,
# pw.x only, ~140 SCFs". Its registered job, quoted: "P7 -- the withdrawn eta(Cr)
# headline, the 1.122 V swing -- was measured in the 1x1 cell. A0's registered
# job is to bound THAT claim."
#
# A6.3 extends it: "A0-main spans U for Ru and Ir as well as the 3d metals, over
# the same 0-9 eV range, with Xu's computed values marked as declared anchor
# points", carrying the falsifiable prediction "the reference ordering Ir < Ru is
# stable across U in [0, 9] eV. If it inverts anywhere in the band, then the
# anchors against which every 3d result in this campaign is reported are
# themselves U-conditional".
#
# THE ALLOCATION, chosen before any A0 number existed. The registered text fixes
# range, cell, calculation, metals and scale (~140) but NOT a step.
#   Cr  4 states x 19 points (0.0-9.0 by 0.5)                  =  76
#   Ru  4 states x (7 points 0.0-9.0 by 1.5 + 6.73 Xu anchor)  =  32
#   Ir  4 states x (7 points 0.0-9.0 by 1.5 + 5.91 Xu anchor)  =  32
# Cr is a LOCATION question (bound P7's swing; 0.5 eV pins the transition to
# +/-0.25 eV, inside A6.2's 1.0 eV threshold). Ru/Ir are an ORDERING question,
# which needs coverage rather than resolution. Metal set is an inference from the
# ~140 budget and is flagged as one in the builder docstring.
#
# NO POST-HOC REFINEMENT. A6.6: "an interaction test registered after the grid is
# read is not a test." A second tranche's trigger is declared before this grid is
# read, not after.
#
# ESCALATION, registered at A6.5(2) and NOT built in here: on a non-convergent
# point, (i) restart from the converged neighbouring-U density as `startingpot`;
# (ii) halve mixing beta; (iii) failing both, record NOT_CONVERGED and plot as a
# gap -- "never interpolated across, never silently dropped. A grid with holes is
# reportable. A grid with invented points is not." Remedy (i) is registered FOR
# A0 and is precisely what S3 forbids; the prohibition is stage-specific.
#
# RUNNER: anvil/46_a0.slurm, which runs projwfc.x in the same job. A6.5(1)
# requires every A0 point to retain its .save or project inline, and the S3
# runner trims wavefunctions the projection needs.
#
# These are FIXED-GEOMETRY SINGLE POINTS on already-relaxed structures; nothing
# here is relaxed and none of it may be reported as relaxed.
#
# SUBMIT WITH EXCLUDE=a024,a050,a088,a196,a220,a223
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""


def main():
    os.makedirs(DST_ROOT, exist_ok=True)
    all_rows, grids = [], {}
    for elem, orb, grid, anchor, why in METALS:
        rows, points = build_metal(elem, orb, grid, anchor, why)
        all_rows += rows
        grids[elem] = {"orbital": orb, "points_eV": points,
                       "xu_anchor_eV": anchor, "why": why}

    if len(all_rows) != 140:
        W.die("built %d decks, expected the registered 140" % len(all_rows))

    hdr = HDR.rstrip("\n") + "\n#\n"
    for elem in ("Cr", "Ru", "Ir"):
        pts = grids[elem]["points_eV"]
        hdr += "#   %-3s %s-%s: %s\n" % (elem, elem, grids[elem]["orbital"],
                                         ", ".join("%.2f" % u for u in pts))
    hdr += "#\n"
    hits = [l for l in hdr.splitlines() if "NP=" in l or "NCONC=" in l]
    if hits != ["# NP=128 NCONC=1"]:
        W.die("manifest header must mention NP=/NCONC= exactly once; found %r" % hits)

    txt = hdr + "".join("%s %s %s %d\n" % (d, job, s, nk)
                        for d, job, s, nk, _e, _st, _u, _n in all_rows)
    path = os.path.join(W.ROOT, "runs", "a0", "m_a0main.txt")
    if os.path.exists(path):
        W.die("%s already exists -- refusing to overwrite" % W.rel(path))
    W.write(path, txt)

    man = os.path.join(DST_ROOT, "manifest.json")
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({
            "arm": "A0-main (block 6A / A6.1a, extended to Ru+Ir by A6.3)",
            "registered_at": "docs/43-prereg-week1-factorial.md:283, :1184-1204, :1236-1245",
            "built": len(all_rows), "registered_total": 140,
            "calculation": "scf",
            "cell": "1x1",
            "range_eV": [0.0, 9.0],
            "nk": NK,
            "allocation_chosen_by": "the entrant, 2026-08-27 (Cr 19 / Ru 7+1 / Ir 7+1)",
            "note": ("FIXED-GEOMETRY single points on already-relaxed structures. "
                     "Relaxation under the changed U is NOT included and these must "
                     "not be reported as relaxed."),
            "escalation_A6_5_2": ["startingpot from converged neighbouring-U density",
                                  "halve mixing_beta",
                                  "NOT_CONVERGED, plotted as a gap"],
            "metals": grids,
        }, fh, indent=2)

    print("\nwrote %s  (%d rows)" % (W.rel(path), len(all_rows)))
    print("wrote %s" % W.rel(man))


if __name__ == "__main__":
    main()
