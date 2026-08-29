#!/usr/bin/env python
"""A0-main tranche 2b (2026-08-29): the pilot-gated Fe s0_OOH 8-rung ladder,
plus the two A6.5(2)(i) repair decks for Fe s0_O u300 / u450.

PILOT VERDICT -- scored 2026-08-29 against the rule REGISTERED in
build_a0main_w2.py BEFORE any pilot ran (a guess is ACCEPTED iff
|E_pilot - E_relax_reference| <= 5 meV against -34804.1641 eV; if several
pass, the closest in energy; no further guesses):

    s0_OOH__pilot530_m010  -2558.05888074 Ry   |delta| = 0.019 meV   PASS
    s0_OOH__pilot530_m030  -2558.05888102 Ry   |delta| = 0.023 meV   PASS
    s0_OOH__pilot530_m070  -2558.05888082 Ry   |delta| = 0.020 meV   PASS

  All three guesses escape the +276.60 meV cold-start trap (final total
  magnetization 22.98 Bohr mag/cell on all three -- the relax branch; the
  trapped 0.5-start state sits at 23.86) and collapse to one state within
  0.004 meV of each other. CLOSEST WINS -> m010: starting_magnetization(1)
  = 0.1, applied uniformly to all 8 rungs. The three deltas all sit inside
  the reference's own 0.1 meV quotation grain, so the choice among them is
  physically indifferent; the registered rule is applied mechanically anyway.
  This builder RE-DERIVES the verdict from the pilot outputs on disk (strict
  qe_qc energies) and refuses to build if the re-derivation disagrees with
  the record above.

  The u530 rung is byte-identical to the accepted pilot deck except the
  prefix line -- asserted below -- so it doubles as the same-machine re-run
  determinism control, the exact pattern of tranche 2's u390/u530
  production-U points.

REPAIRS -- A6.5(2), the first convergence failures of the whole A0 campaign

  Fe s0_O u300 (array 20196817): convergence NOT achieved after 200
    iterations; estimated scf accuracy oscillating ~1e-3 Ry, total
    magnetization drifting 22.44 -> 22.25 over the final iterations.
  Fe s0_O u450 (same array): same stop; accuracy oscillating 1.8e-6 ->
    1.1e-5 Ry around the 1e-6 conv_thr -- nearly converged, cycling between
    magnetic solutions at fixed geometry.
  Both sit mid-window between U = 1.5 and U = 5.3, where A6.5(2) predicted
  convergence would be worst ("precisely where the physics is").

  Escalation rung (i), verbatim: "restart from the converged neighbouring-U
  density as `startingpot`". Parents (nearest CONVERGED neighbour -- u300
  and u450 are each other's nearest neighbours but both failed):

      s0_O__u300__r1  <-  dens/s0_O__u150.save   (dU = 1.5 down; u450 failed)
      s0_O__u450__r1  <-  dens/s0_O__u530.save   (dU = 0.8 up)

  Each repair deck is its failed deck + the prefix line + ONE inserted line
  (startingpot = 'file'). The failed .out stays on disk untouched: A8.4 makes
  the per-metal, per-state convergence-failure rate a REPORTED quantity
  (Fe s0_O: 2 of 8 grid points = 25%, over A8.4's 20% line -- so if the
  repairs do not converge, Fe's s0_O contribution is marked low-confidence
  in the report; if they do, the repaired points carry the label
  "A6.5(2)-i RESTART FROM <parent> DENSITY" into every artifact).

  Runner: anvil/48_a0_repair.slurm = 46_a0.slurm + a density-seeding step
  (cp dens/<parent>.save -> scratch/<child>.save before pw.x;
  startingpot = 'file' reads only the charge density) so a repaired point
  still gets its inline projwfc (A6.5(1)). If a repair still fails: rung
  (ii), halve mixing_beta; failing that the point is recorded NOT_CONVERGED
  and plotted as a gap -- never interpolated, never dropped.

Nothing here relaxes anything; every deck is a fixed-geometry SCF on the
same audit geometry tranche 2 ran (A6.4 labels unchanged).

Usage:  PYTHONPATH=src python src/dft/build_a0main_w2b.py
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402
from build_a0main import (DST_ROOT, HUBBARD_LINE, REF_GRID,  # noqa: E402
                          NK, u_line_re, u_token)
from build_a0main_w2 import FE_RELAX_REFERENCE_EV, MAG_LINE  # noqa: E402
from qe_qc import trusted_energy_ev  # noqa: E402

FE_PROD_U = 5.30
PILOT_TOL_MEV = 5.0
EXPECTED_WINNER = "m010"           # the scored record in the docstring
ACCEPTED_MAG = {"m010": 0.1, "m030": 0.3, "m070": 0.7}
REPAIRS = [("u300", "u150"), ("u450", "u530")]

FE_DIR = os.path.join(DST_ROOT, "Fe")
U_LINE = u_line_re("Fe", "3d")


def rederive_pilot_verdict():
    """Score the three pilots from their outputs, mechanically."""
    deltas = {}
    for key in sorted(ACCEPTED_MAG):
        stem = "s0_OOH__pilot530_%s" % key
        out = os.path.join(FE_DIR, stem + ".out")
        if not os.path.exists(out):
            W.die("%s missing -- pull tranche 2 before building" % W.rel(out))
        ev = trusted_energy_ev(out)
        if ev is None:
            W.die("%s failed strict QC -- no verdict from an untrusted energy"
                  % W.rel(out))
        deltas[key] = (ev - FE_RELAX_REFERENCE_EV) * 1000.0
    passing = [k for k, d in deltas.items() if abs(d) <= PILOT_TOL_MEV]
    if not passing:
        W.die("NO pilot passed the 5 meV gate -- the registered fallback is "
              "the 0.5 ladder + BRANCH-CONDITIONAL label; this builder only "
              "builds the accepted-guess ladder. Deltas: %r" % deltas)
    winner = min(passing, key=lambda k: abs(deltas[k]))
    if winner != EXPECTED_WINNER:
        W.die("re-derived winner %s != recorded %s (deltas %r) -- the record "
              "in this docstring is wrong; fix it before building"
              % (winner, EXPECTED_WINNER, deltas))
    return winner, deltas


def build_ladder(winner):
    src_in = os.path.join(W.ROOT, "runs", "probe", "Fe_audit", "s0_OOH__base.in")
    src = W.read(src_in)
    if not HUBBARD_LINE.search(src) or len(U_LINE.findall(src)) != 1:
        W.die("%s: expected HUBBARD (atomic) + one U Fe-3d line" % W.rel(src_in))
    pilot_txt = W.read(os.path.join(FE_DIR, "s0_OOH__pilot530_%s.in" % winner))

    rows = []
    points = sorted(set(REF_GRID) | {FE_PROD_U})
    for u in points:
        tok = u_token(u)
        stem = "s0_OOH__%s" % tok
        dst = os.path.join(FE_DIR, stem + ".in")
        for p in (dst, os.path.join(FE_DIR, stem + ".out")):
            if os.path.exists(p):
                W.die("%s already exists -- refusing to overwrite (A8.8)" % W.rel(p))

        new = W.swap_scalar_line(src, src_in, "prefix", "s0_OOH__base", stem)
        new, n = MAG_LINE.subn(r"\g<1>%.1f" % ACCEPTED_MAG[winner], new)
        if n != 1:
            W.die("%s: expected exactly one starting_magnetization(1) = 0.5 "
                  "line in the source" % W.rel(src_in))
        if u == 0.0:
            new = HUBBARD_LINE.sub("", new)
            new = U_LINE.sub("", new)
            new = re.sub(r"\n{3,}", "\n\n", new).rstrip("\n") + "\n"
            if HUBBARD_LINE.search(new) or U_LINE.search(new):
                W.die("%s: U = 0 must carry no HUBBARD card" % W.rel(dst))
        else:
            new = U_LINE.sub("U Fe-3d %.4f" % u, new)
            # U_LINE's \s*$ swallows the file's final newline when the U card
            # is the last line -- restore it, or "byte-identical except the
            # prefix line" is one byte short (tranche 2's line-wise diff let
            # exactly this through on its production-U decks; ledger entry).
            if not new.endswith("\n"):
                new += "\n"
            got = U_LINE.findall(new)
            if len(got) != 1 or got[0].split()[-1] != "%.4f" % u:
                W.die("%s: U value is not %.4f" % (W.rel(dst), u))
            if len(HUBBARD_LINE.findall(new)) != 1:
                W.die("%s: expected exactly one HUBBARD card" % W.rel(dst))

        if ("prefix = '%s'" % stem) not in new:
            W.die("%s: prefix not set" % W.rel(dst))
        if W.FORBIDDEN_RESTART.search(new):
            W.die("%s: restart directive appeared" % W.rel(dst))
        for block in ("CELL_PARAMETERS", "ATOMIC_POSITIONS", "K_POINTS",
                      "ATOMIC_SPECIES"):
            a = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, src, re.S | re.M)
            b = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, new, re.S | re.M)
            if (a is None) != (b is None) or (a and a.group(1) != b.group(1)):
                W.die("%s: %s changed" % (W.rel(dst), block))

        if abs(u - FE_PROD_U) < 1e-9:
            # BYTE-level identity modulo the one prefix line (a line-wise zip
            # diff is blind to trailing-newline loss; this is not).
            expect = pilot_txt.replace(
                "prefix = 's0_OOH__pilot530_m010'", "prefix = '%s'" % stem)
            if new != expect:
                W.die("%s: u530 rung must be byte-identical to the accepted "
                      "pilot deck except the prefix line (it is the "
                      "determinism control)" % W.rel(dst))

        W.write(dst, new)
        rows.append(stem)
    return rows, points


def build_repairs():
    rows = []
    for tok_bad, tok_parent in REPAIRS:
        bad_in = os.path.join(FE_DIR, "s0_O__%s.in" % tok_bad)
        bad_out = os.path.join(FE_DIR, "s0_O__%s.out" % tok_bad)
        parent_out = os.path.join(FE_DIR, "s0_O__%s.out" % tok_parent)
        for p in (bad_in, bad_out, parent_out):
            if not os.path.exists(p):
                W.die("%s missing -- pull tranche 2 before building" % W.rel(p))
        bt = W.read(bad_out)
        if "convergence NOT achieved" not in bt:
            W.die("%s did not fail SCF -- a repair for a converged point is "
                  "a replacement, and A8.8 forbids those" % W.rel(bad_out))
        pt = W.read(parent_out)
        if "JOB DONE" not in pt or "convergence NOT achieved" in pt:
            W.die("%s: parent is not a converged run" % W.rel(parent_out))

        stem = "s0_O__%s__r1" % tok_bad
        dst = os.path.join(FE_DIR, stem + ".in")
        for p in (dst, os.path.join(FE_DIR, stem + ".out")):
            if os.path.exists(p):
                W.die("%s already exists -- refusing to overwrite (A8.8)" % W.rel(p))

        src = W.read(bad_in)
        new = W.swap_scalar_line(src, bad_in, "prefix", "s0_O__%s" % tok_bad, stem)
        new2 = new.replace("&ELECTRONS\n", "&ELECTRONS\n  startingpot = 'file'\n")
        if new2.count("startingpot = 'file'") != 1 or new2 == new:
            W.die("%s: startingpot insertion failed" % W.rel(dst))
        new = new2
        if re.search(r"startingwfc|restart_mode", new, re.I):
            W.die("%s: forbidden restart directive" % W.rel(dst))
        a, b = src.split("\n"), new.split("\n")
        if len(b) != len(a) + 1:
            W.die("%s: expected exactly one inserted line" % W.rel(dst))
        changed = [(x, y) for x, y in zip(a, [l for l in b
                   if l != "  startingpot = 'file'"]) if x != y]
        if len(changed) != 1 or "prefix" not in changed[0][0]:
            W.die("%s: repair must differ by prefix + startingpot alone; got %r"
                  % (W.rel(dst), changed[:3]))

        W.write(dst, new)
        rows.append((stem, "s0_O__%s" % tok_parent))
    return rows


HDR_LADDER = """\
# A0-main TRANCHE 2b: the Fe s0_OOH 8-rung ladder, GATED on the branch pilot
# and built only after the pilot verdict (build_a0main_w2b.py docstring: all
# three guesses PASS, m010 closest -> starting_magnetization(1) = 0.1 on every
# rung). The u530 rung is byte-identical to the accepted pilot deck except the
# prefix line -- the same-machine re-run determinism control.
#
# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""

HDR_REPAIRS = """\
# A0-main A6.5(2)(i) REPAIRS: Fe s0_O u300/u450 failed SCF after 200
# iterations (the campaign's first A0 convergence failures; evidence in the
# failed .out files, which stay on disk -- A8.4 reports failure rates).
# Escalation rung (i): restart from the converged neighbouring-U density as
# startingpot. Runner 48_a0_repair.slurm seeds scratch/<child>.save from
# dens/<parent>.save, then runs pw.x + inline projwfc (A6.5(1)) exactly as
# 46_a0.slurm does. Record: build_a0main_w2b.py docstring.
#
# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223  (49_submit_repairs.sh)
#
# row: dir job suffix nk parent_density_prefix
# NP=128 NCONC=1
"""


def main():
    winner, deltas = rederive_pilot_verdict()
    print("pilot verdict re-derived: %s (deltas meV: %s)"
          % (winner, {k: round(v, 3) for k, v in deltas.items()}))

    ladder_rows, points = build_ladder(winner)
    repair_rows = build_repairs()

    lpath = os.path.join(W.ROOT, "runs", "a0", "m_a0main_w2b.txt")
    rpath = os.path.join(W.ROOT, "runs", "a0", "m_a0_repairs.txt")
    for p in (lpath, rpath):
        if os.path.exists(p):
            W.die("%s already exists -- refusing to overwrite" % W.rel(p))
    W.write(lpath, HDR_LADDER +
            "".join("a0/main/Fe %s .in %d\n" % (s, NK) for s in ladder_rows))
    W.write(rpath, HDR_REPAIRS +
            "".join("a0/main/Fe %s .in %d %s\n" % (s, NK, par)
                    for s, par in repair_rows))

    man = os.path.join(DST_ROOT, "manifest.json")
    with open(man, encoding="utf-8") as fh:
        j = json.load(fh)
    if "tranche_2b" in j:
        W.die("manifest.json already carries tranche_2b")
    j["tranche_2b"] = {
        "date": "2026-08-29",
        "fe_pilot_verdict": {
            "rule": ("registered in build_a0main_w2.py before any pilot ran: "
                     "accept iff |E - %.4f eV| <= %.1f meV, closest wins"
                     % (FE_RELAX_REFERENCE_EV, PILOT_TOL_MEV)),
            "deltas_meV": {k: round(v, 6) for k, v in deltas.items()},
            "all_pass": True,
            "winner": winner,
            "applied_mag": ACCEPTED_MAG[winner],
            "note": ("all three pilots escape the +276.60 meV cold-start trap "
                     "(final totmag 22.98 vs the trapped 23.86) and agree to "
                     "0.004 meV; the ladder's u530 rung is byte-identical to "
                     "the winning pilot deck except the prefix line and is the "
                     "re-run determinism control"),
        },
        "ladder": {"state": "s0_OOH", "points_eV": points,
                   "manifest": "runs/a0/m_a0main_w2b.txt"},
        "repairs_a652i": {
            "events": [
                {"point": "Fe s0_O u300", "stop": "convergence NOT achieved "
                 "after 200 iterations; accuracy ~1e-3 Ry oscillating; totmag "
                 "drifting 22.44 -> 22.25", "parent": "s0_O__u150"},
                {"point": "Fe s0_O u450", "stop": "convergence NOT achieved "
                 "after 200 iterations; accuracy oscillating 1.8e-6 -> 1.1e-5 "
                 "Ry around conv_thr 1e-6", "parent": "s0_O__u530"},
            ],
            "escalation": ("A6.5(2)(i) startingpot restart from the converged "
                           "neighbouring-U density; next rung (ii) halve "
                           "mixing_beta; then NOT_CONVERGED plotted as a gap"),
            "a84_rate": ("Fe s0_O pre-repair failure rate 2/8 = 25% (> 20% "
                         "A8.4 line); reported either way, label travels"),
            "manifest": "runs/a0/m_a0_repairs.txt",
            "runner": "anvil/48_a0_repair.slurm",
        },
    }
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(j, fh, indent=2)

    print("wrote %s (%d rows)" % (W.rel(lpath), len(ladder_rows)))
    print("wrote %s (%d rows)" % (W.rel(rpath), len(repair_rows)))
    print("extended %s with tranche_2b" % W.rel(man))


if __name__ == "__main__":
    main()
