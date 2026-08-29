#!/usr/bin/env python
"""A0-main tranche 3, stage 3 (2026-08-29): the TiO2 *OOH base SCF + ladder.

This is the last piece of the six-metal A0 grid, and it is the piece two
registered predictions were waiting on.

WHAT THE ESCALATION RETURNED (arrays 20214014, both tasks COMPLETED)

Tranche 2c registered two Ti s0_OOH relaxations with identical numerics and
different starting geometries, and fixed the selection rule before either ran:
"If exactly one converges it is the geometry, labelled with its provenance."
Exactly one converged.

    s0_OOH_r2   continue rung (ii)'s walk from where it stopped
                FAILED. 19 ionic steps, then an SCF that did not converge in
                400 iterations. Force stalled at 0.0738 Ry/bohr.
    s0_OOH_r3   restart from the RE-ANCHORED geometry (anchor O moved to
                1.781905 A = mean of Ti's own converged *O and *OH Ti-O bonds)
                CONVERGED. "bfgs converged in 53 scf cycles and 52 bfgs steps",
                ZERO SCF failures anywhere in the walk, final force
                0.003092 Ry/bohr, E = -1301.83147222 Ry -- 367 meV below the
                point where r2 stalled.

So the geometric diagnosis registered in tranche 2c is confirmed by the
experiment it predicted. The relaxed adsorbate sits at

    d(anchor O, nearest Ti) = 2.041 A     O-O = 1.371 A     O-H = 0.986 A

against *O at 1.735 A and *OH at 1.829 A on the same surface. TiO2 DOES bind
*OOH, a little more weakly than *O and *OH, exactly as OER scaling expects.
The original chain never found it because qe_slab.py starts every Ti adsorbate
~3.2 A out -- 1.1 A beyond the bond -- and from there the walk drifted further
out into the desorbed-radical region, where the chain's nspin=1 convention
cannot spin-split an odd-electron adsorbate (pw.x counts 157 electrons for this
state) and the SCF limit-cycles. The SCF failure was the symptom; the starting
height was the cause; and "*OOH does not bind on TiO2" would have been the
wrong conclusion, drawn from three ionic steps on a surface where the two
states that did converge needed 36 and 56.

WHAT IS BUILT

  runs/probe/Ti_audit/s0_OOH__base.in   the probe-style base SCF on r3's
                                        converged final coordinates
  runs/a0/main/Ti/s0_OOH__u{000..900}   the 7-point REF_GRID ladder

built by the SAME committed machinery as the other three Ti states --
probe_decks.write_probe for the base, then the HUBBARD-append pattern for the
rungs, u000 byte-identical to its base except the prefix line (the determinism
control). write_probe emits its own &ELECTRONS block, so tranche 2c's
escalation numerics (mixing_beta 0.15, mixing_ndim 16, electron_maxstep 400)
do NOT leak out of the relaxation into the banked SCFs: every Ti A0 point runs
the same conv_thr 1e-6 / local-TF / beta 0.3 / maxstep 200 as every other
metal's.

SELF-TEST BEFORE ANYTHING IS WRITTEN. The other three Ti bases were built
through cmd_build; this one calls write_probe directly (cmd_build reads
<job>.out, and the geometry of record is in s0_OOH_r3.out, not s0_OOH.out).
To prove that is the same machinery and not a lookalike, the builder first
REBUILDS s0_OH__base.in from s0_OH.out by the path it is about to use and
requires the result to be byte-identical to the committed deck. If the two
paths have drifted at all, nothing is written.

WHAT THIS DECIDES -- and why it is not a free hand

A7.2's census goes to 6 of 6 measured if Ti flips, and stays CONFIRMED if it
does not: "additional metals or grid points can only add flips, never remove
one." Nothing here can hurt it.

A7.3 is the one genuinely at stake. It stands at 3 of 5 against a registered
threshold of >=4 (docs/figs/a0main_readout.json, scored 2026-08-29), and Ti is
the only remaining metal:

    Cr 0.3435 EXCEEDS | Fe 0.6102 EXCEEDS | Mn 0.6307 EXCEEDS
    Ru 0.0922 below   | Ir 0.0637 below   | Ti  <- decided by these 8 jobs

If span(c_M)/2 for Ti exceeds 0.10 V, A7.3 is CONFIRMED at 4 of 6. If it does
not, A7.3 is NOT MET at 3 of 6 -- and NOT falsified either, since falsification
needs <=1. Both outcomes are recorded; the readout already prints whichever it
computes, and it computed and printed the currently-failing state BEFORE these
jobs were built, which is the property that makes the eventual number
believable. Nothing in this builder touches the floor, the threshold, the
endpoints or the denominator: all four are quoted from docs/43:1361-1379.

Usage:  PYTHONPATH=src python src/dft/build_a0main_w3b.py
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402
import probe_decks as P  # noqa: E402
from build_a0main import DST_ROOT, HUBBARD_LINE, REF_GRID, u_token  # noqa: E402
from build_a0main_w3 import NK_TI, TI_AUDIT, TI_SRC, U_LINE_TI  # noqa: E402

TI_DST = os.path.join(DST_ROOT, "Ti")
STATE = "s0_OOH"
RELAX = "s0_OOH_r3"          # the converged one; r2 failed (see docstring)
LOSER = "s0_OOH_r2"
PSEUDO = "/usr/share/espresso/pseudo"
SCRATCH = "./tmp"


def relax_outcome(name):
    """(converged?, text) for a relaxation, by the campaign's usual test."""
    txt = W.read(os.path.join(TI_SRC, name + ".out"))
    ok = "bfgs converged" in txt and "convergence NOT achieved" not in txt
    return ok, txt


def apply_selection_rule():
    """Tranche 2c's rule, re-derived from the outputs rather than remembered."""
    won, lost = [], []
    for name in (RELAX, LOSER):
        ok, txt = relax_outcome(name)
        e = P.relax_final_energy_ev(os.path.join(TI_SRC, name + ".out"))
        (won if ok else lost).append((name, e))
    if not won:
        W.die("neither Ti s0_OOH relaxation converged -- A6.5(2)(iii) stands "
              "and no base deck may be built (the registered outcome, not an "
              "error in this script)")
    if len(won) > 1:
        # The rule for that case is also registered: lower energy wins.
        won.sort(key=lambda a: a[1])
        print("NOTE both converged; lower energy wins by %.1f meV"
              % ((won[1][1] - won[0][1]) * 1000.0))
    winner = won[0][0]
    if winner != RELAX:
        W.die("the selection rule picks %s, not the %s this builder is wired "
              "for -- refusing to build on an assumption" % (winner, RELAX))
    return dict(winner=winner, winner_energy_eV=won[0][1],
                did_not_converge=[n for n, _e in lost],
                rule=("tranche 2c, fixed before either ran: exactly one "
                      "converged, so it is the geometry, labelled with its "
                      "provenance"))


def machinery_selftest():
    """The path used below must reproduce an ALREADY-COMMITTED base deck."""
    probe = "s0_OH"
    committed = os.path.join(TI_AUDIT, probe + "__base.in")
    deck = P.parse_input_deck(os.path.join(TI_SRC, probe + ".in"))
    pos, prov = P.parse_final_coordinates(os.path.join(TI_SRC, probe + ".out"))
    if prov != "final":
        W.die("%s: provenance %r" % (probe, prov))
    text, _meta = P.write_probe(deck, pos, P.parse_variant("base"),
                                "%s__base" % probe, PSEUDO, SCRATCH,
                                calculation="scf")
    if text != W.read(committed):
        W.die("write_probe no longer reproduces %s byte-for-byte; the base-deck "
              "machinery has drifted and nothing may be built through it"
              % W.rel(committed))
    print("SELFTEST ok: write_probe reproduces %s byte-for-byte" % W.rel(committed))


def build_base():
    dst = os.path.join(TI_AUDIT, "%s__base.in" % STATE)
    for p in (dst, os.path.join(TI_AUDIT, "%s__base.out" % STATE)):
        if os.path.exists(p):
            W.die("%s already exists (A8.8)" % W.rel(p))
    deck = P.parse_input_deck(os.path.join(TI_SRC, RELAX + ".in"))
    out = os.path.join(TI_SRC, RELAX + ".out")
    pos, prov = P.parse_final_coordinates(out)
    if prov != "final":
        W.die("%s: geometry provenance %r, not the converged final block"
              % (W.rel(out), prov))
    if len(pos) != len(deck["positions"]):
        W.die("%d relaxed coords vs %d in the deck" % (len(pos), len(deck["positions"])))
    text, meta = P.write_probe(deck, pos, P.parse_variant("base"),
                               "%s__base" % STATE, PSEUDO, SCRATCH,
                               calculation="scf")
    # the escalation numerics must NOT survive into a banked SCF
    for banned in ("mixing_ndim", "electron_maxstep = 400", "mixing_beta = 0.15"):
        if banned in text:
            W.die("%s: tranche 2c's relaxation numerics (%s) leaked into a "
                  "banked SCF deck" % (W.rel(dst), banned))
    for need in ("conv_thr = 1.0d-6", "mixing_mode = 'local-TF'",
                 "mixing_beta = 0.3", "electron_maxstep = 200"):
        if need not in text:
            W.die("%s: missing the campaign's standard %r" % (W.rel(dst), need))
    if "nspin" in text:
        W.die("%s: Ti is nspin=1 by construction; a spin block appeared"
              % W.rel(dst))
    if HUBBARD_LINE.search(text) or U_LINE_TI.search(text):
        W.die("%s: the d0 base deck must carry no HUBBARD card" % W.rel(dst))
    W.write(dst, text)
    print("WROTE %s  (geometry from %s, provenance %s, relax ref %.4f eV)"
          % (W.rel(dst), RELAX, prov, meta.get("relax_reference_ev")
             if "relax_reference_ev" in meta
             else P.relax_final_energy_ev(out)))
    return dst, prov


def build_ladder():
    os.makedirs(TI_DST, exist_ok=True)
    src_in = os.path.join(TI_AUDIT, "%s__base.in" % STATE)
    src = W.read(src_in)
    if not src.endswith("\n"):
        W.die("%s: no trailing newline (docs/45 trap 6)" % W.rel(src_in))
    rows = []
    for u in REF_GRID:
        tok = u_token(u)
        stem = "%s__%s" % (STATE, tok)
        dst = os.path.join(TI_DST, stem + ".in")
        for p in (dst, os.path.join(TI_DST, stem + ".out")):
            if os.path.exists(p):
                W.die("%s already exists (A8.8)" % W.rel(p))
        new = W.swap_scalar_line(src, src_in, "prefix", "%s__base" % STATE, stem)
        if u == 0.0:
            expect = src.replace("prefix = '%s__base'" % STATE,
                                 "prefix = '%s'" % stem)
            if new != expect:
                W.die("%s: the u000 rung must be byte-identical to its base "
                      "deck except the prefix line" % W.rel(dst))
        else:
            new = new + "HUBBARD (atomic)\nU Ti-3d %.4f\n" % u
            got = U_LINE_TI.findall(new)
            if len(got) != 1 or got[0].split()[-1] != "%.4f" % u:
                W.die("%s: U value is not %.4f" % (W.rel(dst), u))
            if len(HUBBARD_LINE.findall(new)) != 1:
                W.die("%s: expected exactly one HUBBARD card" % W.rel(dst))
        if W.FORBIDDEN_RESTART.search(new):
            W.die("%s: restart directive appeared" % W.rel(dst))
        for block in ("CELL_PARAMETERS", "ATOMIC_POSITIONS", "K_POINTS",
                      "ATOMIC_SPECIES"):
            a = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, src,
                          re.S | re.M)
            b = re.search(r"^%s.*?$(.*?)(?=^[A-Z_]{3,}|\Z)" % block, new,
                          re.S | re.M)
            if (a is None) != (b is None) or (a and a.group(1) != b.group(1)):
                W.die("%s: %s changed" % (W.rel(dst), block))
        W.write(dst, new)
        rows.append(stem)
    print("WROTE %d rungs in %s" % (len(rows), W.rel(TI_DST)))
    return rows


HDR = """\
# A0-main TRANCHE 3, stage 3: the TiO2 *OOH base SCF + 7-point REF_GRID ladder,
# unblocked by the tranche-2c escalation. Built 2026-08-29 by
# src/dft/build_a0main_w3b.py -- READ ITS DOCSTRING.
#
# The s0_OOH relaxation converged only from the RE-ANCHORED start (s0_OOH_r3:
# bfgs converged, 52 ionic steps, ZERO SCF failures, force 0.003092 Ry/bohr);
# the plain continuation s0_OOH_r2 failed again after 19 steps. Tranche 2c's
# selection rule, fixed before either ran, says exactly-one-converged means
# that one is the geometry. The relaxed adsorbate sits at d(O,Ti) = 2.041 A
# (vs *O 1.735 and *OH 1.829 on the same surface): TiO2 binds *OOH, and the
# original chain missed it only because every Ti adsorbate starts ~3.2 A out.
#
# u000 IS TiO2's production point and is byte-identical to its base deck except
# the prefix line -- the determinism control. write_probe emits its own
# &ELECTRONS, so the relaxation's escalation numerics do not reach these SCFs.
#
# THESE 8 JOBS DECIDE A7.3 (P-FLOOR-U), which stands at 3 of 5 against a
# registered threshold of >=4 with Ti the only metal left. The currently-failing
# state was scored and banked BEFORE these decks were built
# (docs/figs/a0main_readout.json, provenance stamp 2026-08-29).
#
#   1 base SCF (probe/Ti_audit)  +  7 REF_GRID rungs = 8 rows
#
# FIXED-GEOMETRY SINGLE POINTS on the converged r3 structure (A6.4).
#
# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""


def main():
    sel = apply_selection_rule()
    print("SELECTION RULE -> %s (%.4f eV); did not converge: %s"
          % (sel["winner"], sel["winner_energy_eV"], sel["did_not_converge"]))
    machinery_selftest()
    _base, prov = build_base()
    rungs = build_ladder()

    man = os.path.join(W.ROOT, "runs", "a0", "m_a0_ti_ooh.txt")
    rows = ["probe/Ti_audit %s__base .in %d" % (STATE, NK_TI)]
    rows += ["a0/main/Ti %s .in %d" % (s, NK_TI) for s in rungs]
    W.write(man, HDR + "\n".join(rows) + "\n")
    print("WROTE %s: %d rows" % (W.rel(man), len(rows)))

    mpath = os.path.join(DST_ROOT, "manifest.json")
    m = json.load(open(mpath))
    m["tranche_3b"] = {
        "built": "2026-08-29",
        "builder": "src/dft/build_a0main_w3b.py",
        "selection_rule_outcome": sel,
        "geometry": {
            "source": "runs/Ti_slab/s0_OOH_r3.out",
            "provenance": prov,
            "d_O_Ti_final_A": 2.041,
            "O_O_A": 1.371, "O_H_A": 0.986,
            "comparison": "*O relaxed to 1.735 A, *OH to 1.829 A on the same "
                          "surface; the built start was 3.167 A and the "
                          "re-anchor moved it to 1.781905 A",
            "reading": "TiO2 binds *OOH; the earlier 'desorbing' walk was a "
                       "starting guess 1.1 A outside the bond, not a physical "
                       "unbinding",
        },
        "decks": {"base": "runs/probe/Ti_audit/s0_OOH__base.in",
                  "rungs": rungs},
        "numerics_isolation": ("write_probe emits its own &ELECTRONS, so the "
                               "relaxation's mixing_beta 0.15 / mixing_ndim 16 "
                               "/ electron_maxstep 400 do not reach any banked "
                               "SCF; asserted in the builder"),
        "decides": ("A7.3 P-FLOOR-U, which stood at 3 of 5 vs a registered >=4 "
                    "when these were built (banked "
                    "docs/figs/a0main_readout.json). A7.2 is already CONFIRMED "
                    "and cannot be harmed: more metals can only add flips."),
    }
    with open(mpath, "w", newline="\n") as fh:
        json.dump(m, fh, indent=2)
        fh.write("\n")
    print("UPDATED %s: tranche_3b" % W.rel(mpath))


if __name__ == "__main__":
    main()
