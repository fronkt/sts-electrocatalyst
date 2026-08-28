#!/usr/bin/env python
"""A0-main tranche 2: Mn + Fe eta(U) grids (2026-08-28), completing the registered
metal set. Ti follows as tranche 3 (it has no geometries yet; see TI PLAN below).

TRIGGER, DISCLOSED HEAD-ON

  The entrant directed this extension on 2026-08-28 ("Do them over Mn/Fe/Ti
  then"), AFTER the tranche-1 Cr/Ru/Ir readout was banked. That ordering is
  stated here rather than hidden. Why it is nevertheless a test and not a
  tuned grid:

  - Mn, Fe and Ti are A7.2's BLIND metals ("Blind: Mn, Fe, Ru, Ir, Ti",
    docs/43:1355-1359). Not one number for them exists anywhere in A0; nothing
    about them has been read.
  - Nothing in tranche 1 is refined, re-run, or re-allocated. This tranche
    only ADDS the metals A6.3's registered sentence always promised: "A0-main
    spans U for Ru and Ir as well as the 3d metals" (docs/43:1244). Tranche 1
    ran one 3d metal; the wave-3 audit called the shortfall MAJOR and the
    coverage_shortfall caveat has been banked since (a0main_readout.json).
  - The resolution is not new either: the tranche-1 builder's own pre-launch
    docstring recorded the uniform-coarse reading ("Five metals x 4 states x
    7 points is ALSO exactly 140 -- a uniform-coarse reading that includes Mn
    and Fe") before any A0 number existed. This tranche builds exactly that
    resolution for exactly those metals.
  - Everything decision-like below (grids, control points, the Fe *OOH branch
    protocol and its selection rule) is registered in this file and committed
    BEFORE any tranche-2 job runs. The dated correction of record covering
    both the 2026-08-27 allocation and this extension is drafted at docs/59
    for the entrant to re-author and deposit.

THE GRIDS

    Mn  4 states x (7 points 0.0-9.0 by 1.5  + 3.90 production point) = 32
    Fe  3 states x (7 points 0.0-9.0 by 1.5  + 5.30 production point) = 24
    Fe  s0_OOH: 3 branch pilots at U = 5.30 only (see protocol)       =  3
                                                                        --
                                                                        59
    (Fe s0_OOH's 8-rung ladder is built by build_a0main_w2b.py AFTER the
    pilot is scored -- the same gated-rung pattern A0-cell used for u715.)

  The extra per-metal point is each metal's own production U (Mn 3.90,
  Fe 5.30, the MP-calibrated values their entire tier runs at). It earns its
  place twice over: it puts the physically operative point ON the grid, and
  its deck is byte-identical to the banked probe audit deck except the prefix
  line, so it is the same re-run determinism check tranche 1 had at U = 0 for
  Cr/Ru/Ir (and honestly named as such -- the genuine geometry-extraction
  control remains the a0cell readout's). Tokens u390/u530 follow the
  explicit-value convention; no collision with the 1.5-step tokens.

SOURCES

  runs/probe/{Mn,Fe}_audit/{slab,s0_O,s0_OH,s0_OOH}__base.{in,out} -- the
  2026-08-08 magnetic-audit decks: fixed-geometry SCFs on the production
  relaxations' final geometries (probe_manifest geometry_provenance "final"),
  nspin=2, HUBBARD (atomic) with each metal's production U. Audit round-trips
  (docs/41 s6d): Mn all four states <=0.005 meV, digit-for-digit absolute
  magnetization; Fe slab/s0_O/s0_OH <=0.52 meV. Those seven states build cold
  with a clean conscience.

FE s0_OOH BRANCH PROTOCOL -- registered here, BEFORE the pilot is read

  The audit measured that a COLD START at Fe s0_OOH's final geometry and
  production U lands a trapped state +276.60 meV ABOVE the production
  relaxation's banked state (mag 23.86 vs 22.98; docs/41 s6d). The sign rules:
  the relaxation's state is the energy of record ("Fe's on-record number is
  the good one"), and build_basin_restarts.py deliberately excluded Fe for
  exactly that reason. So a cold-built Fe *OOH ladder would knowingly run the
  wrong branch at least near U = 5.3 -- and dG_OOH enters c_M (A7.3) and the
  pls-flip bracket (A7.2) directly, so the branch is load-bearing here even
  though eta(Fe) at production is pls-2-limited and immune.

  The relaxation's density no longer exists (Vast, July), so startingpot
  chaining cannot reach the good branch. Remedy: a THREE-DECK starting-guess
  pilot at the one U where the truth is banked (U = 5.30, relax reference
  -34804.1641 eV):

      s0_OOH__pilot530_m010   starting_magnetization(Fe) 0.5 -> 0.1
      s0_OOH__pilot530_m030   starting_magnetization(Fe) 0.5 -> 0.3
      s0_OOH__pilot530_m070   starting_magnetization(Fe) 0.5 -> 0.7

  (0.5 itself is the banked trapped control -- the audit already ran it.)

  SELECTION RULE, declared before any pilot result exists:
  - A guess is ACCEPTED iff |E_pilot - E_relax_reference| <= 5 meV (the A0
    extraction-control tolerance). If several pass, the closest in energy.
  - The accepted guess is applied uniformly to all 8 Fe s0_OOH rungs
    (build_a0main_w2b.py), each rung banking its Lowdin + magnetization.
  - If NO guess passes, the ladder runs at the default 0.5 and the entire
    Fe *OOH column carries a BRANCH-CONDITIONAL label with the measured
    +0.277 eV class attached to every quantity it feeds.
  - No further guesses beyond these three. A guess hunted after reading
    results would be a fit, not a pin.

  SEPARATE, PARKED, DISCLOSED: docs/45 records a s5-strict re-relax landing
  428.5 meV BELOW the banked Fe s0_OOH 1x1_off parent; banking a replacement
  is an entrant call parked under A8.8. This tranche freezes the CURRENT
  energy-of-record geometry; per A6.4, if a deeper relaxed point is ever
  banked, the relaxed point wins and these rows say so.

TI PLAN (tranche 3, gated on geometry)

  TiO2 has no slab or adsorbate geometry anywhere in the campaign -- only
  bulk hp.x work (runs/hp_tio2). Its chain: qe_slab.py build Ti (production
  builder, d0 / nspin=1 / U=0 by the same MP convention that set Ru/Ir to
  zero, pseudo ti_pbe_v1.4.uspp.F.UPF -- the S0-verified one) -> relax slab +
  3 adslabs on Anvil -> probe-style base SCF decks -> a 7-point REF_GRID
  ladder (28 SCFs; U = 0 IS the production point, Ru/Ir-style). Gas
  references are the campaign's single banked calculation, copied and
  disclosed as such (a0main_readout's live-md5 disclosure covers it).

MECHANICS

  Same as build_a0main.py: each deck is its source with prefix + the U line
  changed (U = 0 drops the HUBBARD card, 3-line diff); geometry, cell,
  k-mesh, species, cutoffs, smearing, nspin, mixing, conv_thr inherited
  byte-for-byte; A6.5(2) remedies are repairs, never build-time properties;
  runner anvil/46_a0.slurm (projwfc.x inline, A6.5(1)); manifest
  runs/a0/m_a0main_w2.txt.

Usage:  PYTHONPATH=src python src/dft/build_a0main_w2.py
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402
from build_a0main import (DST_ROOT, HUBBARD_LINE, REF_GRID,  # noqa: E402
                          STATES, NK, u_line_re, u_token)

FE_RELAX_REFERENCE_EV = -34804.1641   # docs/41 s6d, the banked good-branch state
MAG_LINE = re.compile(r"^(\s*starting_magnetization\(1\)\s*=\s*)0\.5\s*$", re.M)

METALS_W2 = [
    ("Mn", "3d", 3.90, "blind A7.2/A7.3 metal; audit clean all four states "
                       "(<=0.005 meV, docs/41 s6d)"),
    ("Fe", "3d", 5.30, "blind A7.2/A7.3 metal; s0_OOH cold start is a measured "
                       "trap (+276.60 meV) -> pilot protocol, see docstring"),
]
PILOT_MAGS = [0.1, 0.3, 0.7]


def build_deck(src, src_in, elem, orb, state, u, dst_dir):
    """One grid deck from its audit source; returns (stem, nat)."""
    U_LINE = u_line_re(elem, orb)
    tok = u_token(u)
    stem = "%s__%s" % (state, tok)
    dst = os.path.join(dst_dir, stem + ".in")
    for p in (dst, os.path.join(dst_dir, stem + ".out")):
        if os.path.exists(p):
            W.die("%s already exists -- refusing to overwrite (A8.8)" % W.rel(p))

    new = W.swap_scalar_line(src, src_in, "prefix", state + "__base", stem)
    if u == 0.0:
        new = HUBBARD_LINE.sub("", new)
        new = U_LINE.sub("", new)
        new = re.sub(r"\n{3,}", "\n\n", new).rstrip("\n") + "\n"
    else:
        new = U_LINE.sub("U %s-%s %.4f" % (elem, orb, u), new)

    if re.search(r"calculation\s*=\s*'scf'", new) is None:
        W.die("%s: calculation is not scf" % W.rel(dst))
    if ("prefix = '%s'" % stem) not in new:
        W.die("%s: prefix not set" % W.rel(dst))
    if u == 0.0:
        if HUBBARD_LINE.search(new) or U_LINE.search(new):
            W.die("%s: U = 0 must carry no HUBBARD card" % W.rel(dst))
    else:
        got = U_LINE.findall(new)
        if len(got) != 1 or got[0].split()[-1] != "%.4f" % u:
            W.die("%s: U value is not %.4f" % (W.rel(dst), u))
        if len(HUBBARD_LINE.findall(new)) != 1:
            W.die("%s: expected exactly one HUBBARD card" % W.rel(dst))
    if W.FORBIDDEN_RESTART.search(new):
        W.die("%s: restart directive appeared" % W.rel(dst))
    for block in ("CELL_PARAMETERS", "ATOMIC_POSITIONS", "K_POINTS",
                  "ATOMIC_SPECIES"):
        a = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, src, re.S | re.M)
        b = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, new, re.S | re.M)
        if (a is None) != (b is None) or (a and a.group(1) != b.group(1)):
            W.die("%s: %s changed" % (W.rel(dst), block))

    # production-U deck must be byte-identical to source except prefix
    if abs(u - {"Mn": 3.90, "Fe": 5.30}[elem]) < 1e-9:
        diffs = [(x, y) for x, y in zip(src.splitlines(), new.splitlines()) if x != y]
        if len(diffs) != 1 or "prefix" not in diffs[0][0]:
            W.die("%s: production-U deck must differ from source by the prefix "
                  "line alone (it is the determinism control); got %r"
                  % (W.rel(dst), diffs[:3]))

    W.write(dst, new)
    nat = int(re.search(r"^\s*nat\s*=\s*(\d+)", new, re.M).group(1))
    return stem, nat


def build_fe_pilots(src, src_in, dst_dir):
    """Three starting-guess pilots at U = 5.30, the one U with a banked truth."""
    rows = []
    for mag in PILOT_MAGS:
        stem = "s0_OOH__pilot530_m%03d" % int(round(mag * 100))
        dst = os.path.join(dst_dir, stem + ".in")
        for p in (dst, os.path.join(dst_dir, stem + ".out")):
            if os.path.exists(p):
                W.die("%s already exists -- refusing to overwrite" % W.rel(p))
        new = W.swap_scalar_line(src, src_in, "prefix", "s0_OOH__base", stem)
        new, n = MAG_LINE.subn(r"\g<1>%.1f" % mag, new)
        if n != 1:
            W.die("%s: expected exactly one starting_magnetization(1) = 0.5 "
                  "line in the source" % W.rel(src_in))
        diffs = [(x, y) for x, y in zip(src.splitlines(), new.splitlines()) if x != y]
        if len(diffs) != 2:
            W.die("%s: pilot must differ by exactly prefix + starting_mag; "
                  "got %d changed lines" % (W.rel(dst), len(diffs)))
        if W.FORBIDDEN_RESTART.search(new):
            W.die("%s: restart directive appeared" % W.rel(dst))
        W.write(dst, new)
        rows.append(stem)
    return rows


HDR = """\
# A0-main TRANCHE 2: Mn + Fe eta(U) grids + the Fe s0_OOH branch pilot.
# Built 2026-08-28 by src/dft/build_a0main_w2.py -- READ ITS DOCSTRING: the
# trigger (entrant direction, post-tranche-1), the blindness argument, the
# production-U control points, and the REGISTERED Fe s0_OOH pilot selection
# rule all live there and were committed before any of these jobs ran.
#
#   Mn  4 states x (REF_GRID 7 + u390 production point) = 32
#   Fe  3 states x (REF_GRID 7 + u530 production point) = 24
#   Fe  s0_OOH pilots at u530 (m010/m030/m070)          =  3
#
# Fe s0_OOH's 8-rung ladder is GATED on the pilot (build_a0main_w2b.py),
# the same pattern A0-cell used for its A7.1-gated u715 rung.
#
# FIXED-GEOMETRY SINGLE POINTS on already-relaxed structures; nothing here is
# relaxed and none of it may be reported as relaxed (A6.4).
#
# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""


def main():
    all_rows = []
    grids = {}
    for elem, orb, prod_u, why in METALS_W2:
        src_dir = os.path.join(W.ROOT, "runs", "probe", "%s_audit" % elem)
        dst_dir = os.path.join(DST_ROOT, elem)
        os.makedirs(dst_dir, exist_ok=True)
        points = sorted(set(REF_GRID) | {prod_u})
        if len(set(u_token(u) for u in points)) != len(points):
            W.die("%s: token collision" % elem)

        n = 0
        for state in STATES:
            src_in = os.path.join(src_dir, state + "__base.in")
            src_out = os.path.join(src_dir, state + "__base.out")
            for p in (src_in, src_out):
                if not os.path.exists(p):
                    W.die("%s: source missing" % W.rel(p))
            src = W.read(src_in)
            m = re.search(r"^\s*calculation\s*=\s*'(\w+)'", src, re.M)
            if not m or m.group(1) != "scf":
                W.die("%s: expected scf" % W.rel(src_in))
            out = W.read(src_out)
            if "JOB DONE" not in out or "convergence NOT achieved" in out:
                W.die("%s: source did not converge" % W.rel(src_out))
            if not HUBBARD_LINE.search(src) or len(u_line_re(elem, orb).findall(src)) != 1:
                W.die("%s: expected HUBBARD (atomic) + one U line" % W.rel(src_in))

            if elem == "Fe" and state == "s0_OOH":
                for stem in build_fe_pilots(src, src_in, dst_dir):
                    all_rows.append(("a0/main/Fe", stem, ".in", NK))
                    n += 1
                continue
            for u in points:
                stem, _nat = build_deck(src, src_in, elem, orb, state, u, dst_dir)
                all_rows.append(("a0/main/%s" % elem, stem, ".in", NK))
                n += 1
        grids[elem] = {"orbital": orb, "points_eV": points, "production_u": prod_u,
                       "why": why, "decks": n}
        print("  %-3s %2d decks   (%s)" % (elem, n, why))

    if len(all_rows) != 59:
        W.die("built %d decks, expected 59 (32 Mn + 24 Fe + 3 pilots)" % len(all_rows))

    hits = [l for l in HDR.splitlines() if "NP=" in l or "NCONC=" in l]
    if hits != ["# NP=128 NCONC=1"]:
        W.die("manifest header NP/NCONC check failed")
    txt = HDR + "".join("%s %s %s %d\n" % r for r in all_rows)
    path = os.path.join(W.ROOT, "runs", "a0", "m_a0main_w2.txt")
    if os.path.exists(path):
        W.die("%s already exists -- refusing to overwrite" % W.rel(path))
    W.write(path, txt)

    man = os.path.join(DST_ROOT, "manifest.json")
    with open(man, encoding="utf-8") as fh:
        j = json.load(fh)
    if "tranche_2" in j:
        W.die("manifest.json already carries tranche_2 -- refusing to overwrite")
    j["tranche_2"] = {
        "built": len(all_rows),
        "date": "2026-08-28",
        "trigger": ("entrant direction 2026-08-28, post-tranche-1 readout; "
                    "Mn/Fe/Ti are A7.2's blind metals and nothing of theirs "
                    "has been read -- full record in build_a0main_w2.py and "
                    "the dated correction docs/59"),
        "metals": grids,
        "fe_s0_OOH_protocol": ("3-pilot starting-guess selection at u530 "
                               "against the banked relax reference "
                               "%.4f eV, tolerance 5 meV, declared before "
                               "any pilot ran; ladder gated on it "
                               "(build_a0main_w2b.py)" % FE_RELAX_REFERENCE_EV),
        "ti_plan": ("tranche 3, gated on geometry: qe_slab.py build Ti, relax "
                    "slab + 3 adslabs (d0, nspin=1, U=0 MP convention), then "
                    "a 7-point REF_GRID ladder (28 SCFs)"),
    }
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(j, fh, indent=2)

    print("\nwrote %s  (%d rows)" % (W.rel(path), len(all_rows)))
    print("extended %s with tranche_2" % W.rel(man))


if __name__ == "__main__":
    main()
