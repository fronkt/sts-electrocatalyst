#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A11.R6 rung builder -- the two pre-named rungs for the sixteen unconverged Ru
U = 9 spin rows (docs/43 A11.R6, registered 2026-09-02 BEFORE this file existed).

    python src/dft/build_ru_rung.py 1        # rung 1: beta 0.15, maxstep 400
    python src/dft/build_ru_rung.py 2        # rung 2: beta 0.075, ndim 16, maxstep 600
                                             #         only on rows rung 1 left unconverged

Assertions (each fatal):
  R-a  scope: exactly the sixteen registered rows, listed here verbatim from A11.R6;
       the builder refuses to touch any other stem.
  R-b  trigger re-derived from disk: the previous rung's .out exists and carries
       'convergence NOT achieved'; a row whose previous rung CONVERGED is skipped with
       a printed line (rung 2 runs only on rung-1 failures; for rung 1 all sixteen must
       be unconverged, else the registration's premise is false and the builder dies).
  R-c  transform = exactly the licensed lines: prefix -> <stem>__rungN; mixing_beta
       0.3 -> table; electron_maxstep 200 -> table; rung 2 additionally inserts
       mixing_ndim = 16 directly under mixing_beta (parent must carry none). Every
       replaced line must exist exactly once; every other line is byte-identical.
  R-d  census acceptance for the twelve a0 rows: a0spin_census.check_candidate_deck
       (its A11.R6 rung check) passes on the written deck.
  R-e  refuses to overwrite; refuses if the child .out already exists.
  R-f  manifests: runs/a0/m_ru_rung<N>.txt (12 rows, nk 4, submit via 47_submit_a0.sh
       so projwfc.x runs inline on converged points, A6.5(1)) and
       runs/s0/m_h_afm_rung<N>.txt (4 rows, nk 4, submit via 41_submit_wave.sh, the
       S0(h) family's runner); EXCLUDE header carries a171.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_a0spin as B          # noqa: E402  (ROOT, read, write, die)
import a0spin_census as ac        # noqa: E402  (check_candidate_deck, RUNG_TABLE)

A0 = [("a0/spin/Ru", "%s__u900__sp2m%03d" % (st, int(s * 100)))
      for st in ("slab", "s0_O", "s0_OH", "s0_OOH") for s in (0.10, 0.30, 0.50)]
S0 = [("s0/h_afm_probe", "s0_OH__2x1v_off__afm__u900"),
      ("s0/h_afm_probe", "s0_OOH__2x1v_off__afm__u900"),
      ("s0/h_afm_robust", "s0_OH__2x1v_off__afm__afmgeo__u900"),
      ("s0/h_afm_robust", "s0_OOH__2x1v_off__afm__afmgeo__u900")]
EXCLUDE = "a024,a049,a050,a088,a196,a220,a223,a171"
LIC = re.compile(r"^\s*(prefix|mixing_beta|mixing_ndim|electron_maxstep)\s*=")


def unconverged(path):
    if not os.path.exists(path):
        B.die("R-b previous-rung output missing: %s" % path)
    txt = B.read(path)
    if "convergence NOT achieved" in txt:
        return True
    if "convergence has been achieved" in txt:
        return False
    B.die("R-b %s is neither converged nor 'NOT achieved' -- not terminal" % path)


def transform(ptxt, stem, rung):
    want = ac.RUNG_TABLE[rung]
    lines = ptxt.splitlines(keepends=True)
    out, n_prefix, n_beta, n_max, n_ndim = [], 0, 0, 0, 0
    for ln in lines:
        s = ln.rstrip("\r\n")
        if re.match(r"^\s*prefix\s*=", s):
            out.append("  prefix = '%s__rung%d'\n" % (stem, rung)); n_prefix += 1
        elif re.match(r"^\s*mixing_beta\s*=\s*0\.3\s*$", s):
            out.append("  mixing_beta = %s\n" % ("%g" % want["beta"])); n_beta += 1
            if rung == 2:
                out.append("  mixing_ndim = %d\n" % int(want["ndim"]))
        elif re.match(r"^\s*electron_maxstep\s*=\s*200\s*$", s):
            out.append("  electron_maxstep = %d\n" % int(want["maxstep"])); n_max += 1
        elif re.match(r"^\s*mixing_ndim\s*=", s):
            n_ndim += 1; out.append(ln)
        else:
            out.append(ln)
    if (n_prefix, n_beta, n_max, n_ndim) != (1, 1, 1, 0):
        B.die("R-c %s: prefix/beta/maxstep/ndim counts %r, need (1,1,1,0)"
              % (stem, (n_prefix, n_beta, n_max, n_ndim)))
    ctxt = "".join(out)
    if [l for l in ctxt.splitlines() if not LIC.match(l)] != \
            [l for l in ptxt.splitlines() if not LIC.match(l)]:
        B.die("R-c %s: a non-licensed line changed" % stem)
    return ctxt


def main(argv):
    if len(argv) != 1 or argv[0] not in ("1", "2"):
        B.die("usage: build_ru_rung.py <1|2>")
    rung = int(argv[0])
    print("A11.R6 rung %d builder -- %s" % (rung, ac.RUNG_TABLE[rung]))
    built, skipped, rows = [], [], {"a0": [], "s0": []}
    for family, lst in (("a0", A0), ("s0", S0)):
        for d, stem in lst:
            ddir = os.path.join(B.ROOT, "runs", d)
            parent = os.path.join(ddir, stem + ".in")
            if not os.path.exists(parent):
                B.die("R-a parent deck missing: %s" % parent)
            prev = os.path.join(ddir, stem + (".out" if rung == 1 else "__rung1.out"))
            if not unconverged(prev):
                if rung == 1:
                    B.die("R-b %s CONVERGED at rung 0 -- not one of the sixteen" % stem)
                skipped.append(stem); print("  skip %s (rung 1 converged)" % stem)
                continue
            child = os.path.join(ddir, "%s__rung%d.in" % (stem, rung))
            if os.path.exists(child) or os.path.exists(child[:-3] + ".out"):
                B.die("R-e refusing to overwrite %s" % child)
            ctxt = transform(B.read(parent), stem, rung)
            B.write(child, ctxt)
            if family == "a0":
                ac.check_candidate_deck("Ru", child, "%s__rung%d" % (stem, rung))  # R-d
            md5 = hashlib.md5(open(child, "rb").read()).hexdigest()
            rows[family].append((d, "%s__rung%d" % (stem, rung), md5))
            built.append(stem)
            print("  built %s/%s__rung%d md5 %s%s"
                  % (d, stem, rung, md5, "  census CEN-d PASS" if family == "a0" else ""))
    if rung == 1 and len(built) != 16:
        B.die("R-a built %d, registered sixteen" % len(built))

    hdr = [
        "# A11.R6 RUNG %d -- %s. Built %s by src/dft/build_ru_rung.py (READ ITS" % (
            rung, "beta 0.15 / maxstep 400" if rung == 1 else
            "beta 0.075 / mixing_ndim 16 / maxstep 600", "2026-09-02"),
        "# DOCSTRING, R-a..R-f) under docs/43 A11.R6 [RU U9 SPIN RUNG LADDER 2026-09-02:",
        "# LICENSED], registered before any rung deck existed. Scope: the unconverged Ru",
        "# U = 9 spin rows only; every deck differs from its rung-0 parent in exactly the",
        "# licensed lines (prefix, mixing_beta, electron_maxstep%s)." % (
            ", mixing_ndim" if rung == 2 else ""),
        "# Interpretation of every outcome is fixed in A11.R6; a converged candidate enters",
        "# the a7_3_spin SENSITIVITY census only (a0 rows) or the S0(h) readout (s0 rows);",
        "# the as-built A7.3 headline cannot move (A11.5).",
        "#",
    ]
    for family, path, note in (("a0", "runs/a0/m_ru_rung%d.txt" % rung,
                                "submit via anvil/47_submit_a0.sh (projwfc inline, A6.5(1))"),
                               ("s0", "runs/s0/m_h_afm_rung%d.txt" % rung,
                                "submit via anvil/41_submit_wave.sh (40_wave.slurm, NP=128)")):
        if not rows[family]:
            print("  no %s rows at rung %d -- no manifest written" % (family, rung))
            continue
        man = os.path.join(B.ROOT, path)
        if os.path.exists(man):
            B.die("R-e refusing to overwrite %s" % man)
        lines = list(hdr) + ["# %s" % note, "#",
                             "# deck md5s (an independent rebuild must reproduce them byte-for-byte):"]
        lines += ["# md5 %s %s/%s.in" % (m, d, s) for d, s, m in rows[family]]
        lines += ["#", "# SUBMIT WITH EXCLUDE=%s" % EXCLUDE,
                  "# (submit-time list additionally + a120,a200 per docs/66 section 4)",
                  "#", "# row: dir job suffix nk", "# NP=128 NCONC=1"]
        lines += ["%s %s .in 4" % (d, s) for d, s, _m in rows[family]]
        B.write(man, "\n".join(lines) + "\n")
        print("  wrote %s (%d rows)" % (path, len(rows[family])))
    print("BUILD OK -- rung %d: %d decks built, %d skipped; NOTHING submitted."
          % (rung, len(built), len(skipped)))


if __name__ == "__main__":
    main(sys.argv[1:])
