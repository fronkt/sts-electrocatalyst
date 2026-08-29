#!/usr/bin/env python
"""A0-main tranche 3, stage 2 (2026-08-29): the TiO2 base SCFs + eta(U)
ladder for the three CONVERGED geometries, and the A6.5(2)(ii) repair of the
s0_OOH relax.

WHAT STAGE 1 RETURNED (array 20196856, 2026-08-28/29; QC this session):

    slab    bfgs converged, 17 SCF blocks,  E_final = -1217.61686196 Ry
    s0_O    bfgs converged, 36 SCF blocks,  E_final = -1258.96691068 Ry
    s0_OH   bfgs converged, 56 SCF blocks,  E_final = -1260.37391820 Ry
    s0_OOH  FAILED: the SCF after the first ionic step stopped at 200
            iterations (accuracy 0.42 -> 0.018 -> 0.0097 Ry, still falling
            but far from conv_thr 1e-6); zero bfgs steps banked.

THE THREE CONVERGED STATES (registered plan, build_a0main_w2.py "TI PLAN" +
docs/59 s3): probe-style base SCF decks at the final geometries -- built by
the SAME committed machinery that built the Mn/Fe audit decks
(probe_decks.py, variant "base", geometry_provenance must come back
"final") -- then the 7-point REF_GRID ladder per state. U = 0 IS TiO2's
production point (the same MP convention that sets Ru/Ir to zero), so the
u000 rung is byte-identical to its base deck except the prefix line and is
the same-machine re-run determinism control (asserted at byte level).
Nonzero rungs append the HUBBARD card (atomic projector, U Ti-3d) that the
d0 production deck deliberately lacks -- the mirror image of tranche 1's
u000 treatment for Cr, where U = 0 DROPS the card so plain PBE is genuinely
plain. nspin = 1 throughout, inherited from the production chain and
disclosed in the readout caveats.

THE s0_OOH REPAIR -- A6.5(2), applied to the geometry chain per A8.4 ("the
escalation ladder is A6.5's, unchanged"):

  Rung (i) -- restart from a converged neighbouring-U density -- does not
  exist for a relaxation: there is no neighbouring-U point (Ti has no grid
  yet) and the failed run retained no density (42_s3_wave1.slurm retains
  only on clean convergence). So rung (ii): HALVE THE MIXING BETA.

      s0_OOH_r1.in = s0_OOH.in
        + prefix 's0_OOH' -> 's0_OOH_r1'
        + mixing_beta 0.3 -> 0.15
        + ATOMIC_POSITIONS replaced by the LAST trajectory block of the
          failed run, spliced VERBATIM (pw.x's own coordinates and its own
          0 0 0 constraint flags), so the restart continues from where the
          walk stopped instead of repeating the completed first step.

  The spliced geometry is labelled for what it is -- the last step of a
  non-converged walk, not a relaxed structure; the r1 run continues the
  relaxation and must itself reach "bfgs converged" before any Ti s0_OOH
  SCF is built on it. If r1 also fails: A6.5(2)(iii), the state is recorded
  NOT_CONVERGED, A7.3's own registered text shrinks the span denominator
  ("a converged *OOH geometry" conditions it), and the A7.2 census for Ti
  runs on the states that exist. Nothing is interpolated.

  The failed s0_OOH.out stays on disk untouched (A8.4: failure rates are
  reported quantities; this is the first geometry-chain failure of the Ti
  arm and it is disclosed in the manifest and the readout).

Gas references: runs/Ti_slab/H2O, H2 are md5-identical copies of the
campaign's single banked gas calculation (verified at stage-1 build; the
readout's live-md5 disclosure covers Ti like every other metal).

Usage:  PYTHONPATH=src python src/dft/build_a0main_w3.py
"""

import argparse
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402
import probe_decks as P  # noqa: E402
from build_a0main import DST_ROOT, HUBBARD_LINE, REF_GRID, u_token  # noqa: E402

NK_TI = 8            # the stage-1 relax rows ran -nk 8 on the same 8x4x1 mesh
TI_STATES = ["slab", "s0_O", "s0_OH"]          # s0_OOH gated on the r1 relax
TI_SRC = os.path.join(W.ROOT, "runs", "Ti_slab")
TI_AUDIT = os.path.join(W.ROOT, "runs", "probe", "Ti_audit")
TI_DST = os.path.join(DST_ROOT, "Ti")
U_LINE_TI = re.compile(r"^U Ti-3d\s+[\d.]+\s*$", re.M)


def check_relax(name, want_converged=True):
    out = os.path.join(TI_SRC, name + ".out")
    txt = W.read(out)
    ok = ("JOB DONE" in txt and "bfgs converged" in txt
          and "convergence NOT achieved" not in txt)
    if want_converged and not ok:
        W.die("%s is not a cleanly converged relax" % W.rel(out))
    if not want_converged and ok:
        W.die("%s converged -- the repair would be a replacement (A8.8)"
              % W.rel(out))
    return txt


def build_bases():
    """The Mn/Fe audit machinery, byte-for-byte: probe_decks build, variant
    base, on the converged Ti states."""
    if os.path.exists(TI_AUDIT):
        W.die("%s already exists -- refusing to overwrite" % W.rel(TI_AUDIT))
    args = argparse.Namespace(
        rundir=TI_SRC, outdir=TI_AUDIT, variants=["base"], jobs=TI_STATES,
        pseudo_dir="/usr/share/espresso/pseudo", scratch="./tmp",
        calculation="scf")
    P.cmd_build(args)
    man = json.load(open(os.path.join(TI_AUDIT, "probe_manifest.json")))
    built = {j["job"]: j for j in man["jobs"]}
    if sorted(built) != sorted(TI_STATES):
        W.die("probe build emitted %r, expected %r" % (sorted(built), TI_STATES))
    for name, j in built.items():
        if j["geometry_provenance"] != "final":
            W.die("%s: geometry provenance %r, not the converged final block"
                  % (name, j["geometry_provenance"]))
    return built


def build_ladder():
    os.makedirs(TI_DST, exist_ok=True)
    rows = []
    for state in TI_STATES:
        src_in = os.path.join(TI_AUDIT, "%s__base.in" % state)
        src = W.read(src_in)
        if HUBBARD_LINE.search(src) or U_LINE_TI.search(src):
            W.die("%s: the d0 base deck must carry no HUBBARD card" % W.rel(src_in))
        if "nspin" in src:
            W.die("%s: expected nspin absent (d0, nspin=1 default)" % W.rel(src_in))
        if not src.endswith("\n"):
            W.die("%s: no trailing newline" % W.rel(src_in))
        for u in REF_GRID:
            tok = u_token(u)
            stem = "%s__%s" % (state, tok)
            dst = os.path.join(TI_DST, stem + ".in")
            for p in (dst, os.path.join(TI_DST, stem + ".out")):
                if os.path.exists(p):
                    W.die("%s already exists (A8.8)" % W.rel(p))
            new = W.swap_scalar_line(src, src_in, "prefix", state + "__base", stem)
            if u == 0.0:
                # byte-identical except the prefix line: the determinism control
                expect = src.replace("prefix = '%s__base'" % state,
                                     "prefix = '%s'" % stem)
                if new != expect:
                    W.die("%s: u000 rung must be byte-identical to its base "
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
    return rows


TRAJ_BLOCK = re.compile(
    r"ATOMIC_POSITIONS \(angstrom\)\s*\n((?:\s*[A-Z][a-z]?\s+[-\d.eE+]+.*\n)+)")


def build_ooh_repair(failed_txt):
    src_in = os.path.join(TI_SRC, "s0_OOH.in")
    src = W.read(src_in)
    dst = os.path.join(TI_SRC, "s0_OOH_r1.in")
    for p in (dst, os.path.join(TI_SRC, "s0_OOH_r1.out")):
        if os.path.exists(p):
            W.die("%s already exists (A8.8)" % W.rel(p))

    blocks = TRAJ_BLOCK.findall(failed_txt)
    if not blocks:
        W.die("no angstrom trajectory block in the failed s0_OOH.out")
    body = blocks[-1]
    lines = [l for l in body.rstrip("\n").split("\n") if l.strip()]
    deck = P.parse_input_deck(src_in)
    if len(lines) != len(deck["positions"]):
        W.die("trajectory block has %d atoms, deck has %d"
              % (len(lines), len(deck["positions"])))
    for line, (s, _, _, _) in zip(lines, deck["positions"]):
        if line.split()[0] != s:
            W.die("species order changed in the trajectory block")

    new = W.swap_scalar_line(src, src_in, "prefix", "s0_OOH", "s0_OOH_r1")
    new2 = new.replace("  mixing_beta = 0.3\n", "  mixing_beta = 0.15\n")
    if new2 == new or new2.count("mixing_beta = 0.15") != 1:
        W.die("mixing_beta halving failed")
    new = new2
    newblock = "ATOMIC_POSITIONS angstrom\n" + "\n".join(lines) + "\n"
    new2 = re.sub(
        r"ATOMIC_POSITIONS\s+\S+\s*\n(?:\s*[A-Z][a-z]?\s+[-\d.eE+]+.*\n)+",
        lambda m: newblock, new, count=1)
    if new2 == new or newblock not in new2:
        W.die("ATOMIC_POSITIONS splice failed")
    new = new2
    if W.FORBIDDEN_RESTART.search(new):
        W.die("restart directive appeared in the repair deck")
    if new.count("ATOMIC_POSITIONS") != 1:
        W.die("repair deck must carry exactly one ATOMIC_POSITIONS block")
    W.write(dst, new)
    return dst


HDR_TI = """\
# A0-main TRANCHE 3, stage 2: TiO2 base SCFs + eta(U) ladder for the three
# CONVERGED stage-1 geometries (slab, s0_O, s0_OH). Built 2026-08-29 by
# src/dft/build_a0main_w3.py -- READ ITS DOCSTRING: the s0_OOH relax FAILED
# and is being repaired under A6.5(2)(ii) in a separate manifest
# (runs/Ti_slab/m_ti_relax_r1.txt); its base + 7 rungs are built only after
# that relax converges. u000 IS TiO2's production point (U = 0, MP
# convention) and each u000 rung is byte-identical to its base deck except
# the prefix line -- the determinism control.
#
#   3 base SCFs (probe/Ti_audit)  +  3 states x 7 REF_GRID rungs = 24 rows
#
# FIXED-GEOMETRY SINGLE POINTS on stage-1's relaxed structures (A6.4).
#
# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""

HDR_R1 = """\
# A6.5(2)(ii) repair of the TiO2 s0_OOH relax (array 20196856 task 4: the
# SCF after the first ionic step stopped at 200 iterations, accuracy 0.0097
# Ry vs conv_thr 1e-6; zero bfgs steps banked; failed .out retained --
# A8.4). s0_OOH_r1.in = same deck, mixing_beta 0.3 -> 0.15, continuing from
# the last trajectory geometry (spliced verbatim, pw.x's own constraint
# flags). Record: build_a0main_w3.py docstring. Runner 42_s3_wave1.slurm
# via 43_submit_s3_wave1.sh.
#
# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""


def main():
    for s in TI_STATES:
        check_relax(s, want_converged=True)
    failed_txt = check_relax("s0_OOH", want_converged=False)

    bases = build_bases()
    ladder = build_ladder()
    repair = build_ooh_repair(failed_txt)

    tpath = os.path.join(W.ROOT, "runs", "a0", "m_a0_ti.txt")
    rpath = os.path.join(TI_SRC, "m_ti_relax_r1.txt")
    for p in (tpath, rpath):
        if os.path.exists(p):
            W.die("%s already exists" % W.rel(p))
    rows = ["probe/Ti_audit %s__base .in %d" % (s, NK_TI) for s in TI_STATES]
    rows += ["a0/main/Ti %s .in %d" % (stem, NK_TI) for stem in ladder]
    W.write(tpath, HDR_TI + "".join(r + "\n" for r in rows))
    W.write(rpath, HDR_R1 + "Ti_slab s0_OOH_r1 .in %d\n" % NK_TI)

    man = os.path.join(DST_ROOT, "manifest.json")
    with open(man, encoding="utf-8") as fh:
        j = json.load(fh)
    if "tranche_3" in j:
        W.die("manifest.json already carries tranche_3")
    j["tranche_3"] = {
        "date": "2026-08-29",
        "stage_1": {
            "array": "20196856",
            "converged": {s: True for s in TI_STATES},
            "s0_OOH": ("FAILED -- SCF after first ionic step hit 200 "
                       "iterations at accuracy 0.0097 Ry (conv_thr 1e-6), "
                       "still falling; A6.5(2)(ii) repair s0_OOH_r1 (beta "
                       "0.15, last trajectory geometry) in "
                       "runs/Ti_slab/m_ti_relax_r1.txt; failed .out retained "
                       "per A8.4"),
        },
        "stage_2": {
            "manifest": "runs/a0/m_a0_ti.txt",
            "states": TI_STATES,
            "points_eV": REF_GRID,
            "production_u": 0.0,
            "note": ("U = 0 is the production point (MP convention, as "
                     "Ru/Ir); u000 rung byte-identical to its probe-style "
                     "base deck except the prefix line = determinism "
                     "control; nonzero rungs append HUBBARD (atomic) "
                     "U Ti-3d; d0, nspin=1 throughout"),
            "base_relax_reference_ev": {
                s: bases[s]["relax_reference_ev"] for s in TI_STATES},
        },
        "s0_OOH_gate": ("base + 7 rungs built only after s0_OOH_r1 reaches "
                        "bfgs converged; if r1 fails, A6.5(2)(iii): "
                        "NOT_CONVERGED, A7.3's denominator shrinks per its "
                        "own registered conditioning, A7.2 census runs on "
                        "the states that exist"),
    }
    with open(man, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(j, fh, indent=2)

    print("wrote %s (%d rows)" % (W.rel(tpath), len(rows)))
    print("wrote %s (1 row) + %s" % (W.rel(rpath), W.rel(repair)))
    print("extended %s with tranche_3" % W.rel(man))


if __name__ == "__main__":
    main()
