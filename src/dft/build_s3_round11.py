#!/usr/bin/env python
"""S3 round 11 (2026-08-27) -- re-anchor the two open wave-4 parents so their
children can be seeded, now that a converged density survives the run.

Round 10 closed the diagnosis on `Co s0_OOH__2x1v_mir`, and the answer is not
the one this ledger has been carrying.

  THE CHILDREN ARE NOT LOSING A LOTTERY. THEY CANNOT WIN IT.

  Three independent cold `scf` runs at that parent's FINAL relaxed geometry:

      s0_OOH__2x1v_mir__g1        magtot 24.86   +747.449 meV vs parent
      s0_OOH__2x1v_mir__g1__r2    OOM-killed on a050 at 13 iterations
      s0_OOH__2x1v_mir__g1__r3    magtot 23.95   +870.768 meV vs parent

  and the SCF magnetization trajectories show why. Every cold start at the
  relaxed geometry is locked into the 23-25 uB region by roughly iteration 30
  and never leaves it. Meanwhile the parent reached magtot **19.81 at ionic
  step 1** -- cold, first try, from the ORIGINAL geometry -- and then relaxed
  19.81 -> 20.13 over 22 ionic steps carrying its own density forward. Co
  ref__2x1v is the same shape: magtot 22.50 at step 1 from the original
  geometry, relaxing to 21.66 by step 10.

  So the reachable magnetic branch is a property of the geometry the SCF
  COLD-STARTS from. At the original geometry the low branch is reachable and
  has been reached repeatedly:

      mir  .out 19.81 | .attempt2 19.79 | .replay 19.98    (low, 3 of 5)
           .attempt1 22.80 | .replay_nd 22.93              (high)
      ref  .out 22.50 | .replay 22.58                      (2 of 3)
           .replay_ms 23.56                                (high)

  At the relaxed geometry it has never been reached, in three tries. Rolling
  the child again is not a plan; it is the one move the evidence rules out.

  WHAT THIS ROUND DOES

  Re-run each parent's own relax deck under a NEW prefix. Nothing is replaced
  (A8.8): the banked `.out` files are untouched and these runs are named
  `__reanchor`. Their purpose is not to restate the parent's energy -- it is to
  produce, and this time KEEP, a converged density at the relaxed geometry in
  the low branch. `anvil/42_s3_wave1.slurm` now retains `<prefix>.save` minus
  the wavefunctions for any run whose every SCF converged, so a re-anchor that
  lands low leaves a 40-75 MB seed on disk permanently.

  Round 12 then runs the `__g1.fromparent` children, which already exist on
  disk with `startingpot='file'`, against those seeds -- and a seeded child
  inherits its seed's branch, which is exactly what the two A8.3 successes
  showed (Fe -2558.16677325 at magtot 22.98 matching its parent's 22.98 to
  0.004 meV; Ni likewise to 0.019 meV).

  Two rolls of `mir` because it is cheap (2 h 39 m, ~340 SU) and historically
  lands low 3 times in 5; one roll of `ref__2x1v` because it is not (7 h 47 m,
  ~1000 SU). If a roll lands high it is banked as evidence and costs nothing
  further; the child is simply not run from it.

  Decks differ from the deck that produced each banked parent in exactly one
  line, the prefix. Verified at build time: `s0_OOH__2x1v_mir.run.in` and
  `ref__2x1v.run.in` are both byte-identical to their `retry_ms.in` apart from
  outdir/pseudo_dir, so `retry_ms.in` IS the deck of record for both.

Delegated under the standing instruction of 2026-08-25, quoted in full:
"Continue to make the failures run correctly, run the wave 4 children."
Nothing here changes a threshold, a functional, a cell, a cutoff or a k-mesh.
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402


# (element, source deck stem, banked parent stem, new stem, nk, rolls, target)
ROWS = [
    ('Co', 's0_OOH__2x1v_mir.retry_ms', 's0_OOH__2x1v_mir',
     's0_OOH__2x1v_mir__reanchor', 8, ['', '__b'],
     dict(E=-4662.69189747, magtot=20.13, magabs=22.91, step1=19.81,
          note='3 of 5 runs from this geometry landed low (19.79-19.98)')),
    ('Co', 'ref__2x1v.retry_ms', 'ref__2x1v',
     'ref__2x1v__reanchor', 16, [''],
     dict(E=-4578.38410421, magtot=21.66, magabs=24.38, step1=22.50,
          note='2 of 3 runs from this geometry landed near 22.5')),
]

MAG_TOL = 0.05


def build():
    rows = []
    for el, srcstem, parent, newstem, nk, rolls, target in ROWS:
        src_path = os.path.join(W.ROOT, 'runs', 's3', el, srcstem + '.in')
        if not os.path.exists(src_path):
            W.die('%s: source deck missing' % W.rel(src_path))
        src = W.read(src_path)

        # This must be a relax, cold, with no restart of any kind -- a re-anchor
        # that warm-started would prove nothing about branch reachability.
        m = re.search(r"^\s*calculation\s*=\s*'(\w+)'", src, re.M)
        if not m or m.group(1) != 'relax':
            W.die('%s: expected a relax deck, found %r' % (W.rel(src_path), m and m.group(1)))
        if W.FORBIDDEN_RESTART.search(src):
            W.die('%s: source deck carries a restart directive' % W.rel(src_path))

        nat = int(re.search(r'^\s*nat\s*=\s*(\d+)', src, re.M).group(1))
        rows_src = W.selftest_formatter(src, src_path)
        if nat != len(rows_src):
            W.die('%s: nat=%d but %d position lines' % (W.rel(src_path), nat, len(rows_src)))

        # The prefix in the source deck is the PARENT's, since retry_ms.in is
        # the deck of record. Assert that before swapping it.
        if src.count("prefix = '%s'" % parent) != 1:
            W.die("%s: expected exactly one prefix = '%s'" % (W.rel(src_path), parent))

        for roll in rolls:
            stem = newstem + roll
            dst = os.path.join(W.ROOT, 'runs', 's3', el, stem + '.in')
            out = os.path.join(W.ROOT, 'runs', 's3', el, stem + '.out')
            for p in (dst, out):
                if os.path.exists(p):
                    W.die('%s already exists -- refusing to overwrite (A8.8), %d bytes'
                          % (W.rel(p), os.path.getsize(p)))

            new = W.swap_scalar_line(src, src_path, 'prefix', parent, stem)
            d = W.diff_lines(src, new, dst)
            if len(d) != 1:
                W.die('%s: expected exactly 1 differing line, got %d: %r' % (W.rel(dst), len(d), d))
            if W.classify_diff(d[0][1], d[0][2], dst) != 'prefix':
                W.die('%s: the single diff is not the prefix' % W.rel(dst))
            if W.FORBIDDEN_RESTART.search(new):
                W.die('%s: restart directive appeared during the swap' % W.rel(dst))

            W.write(dst, new)
            rows.append(('s3/%s' % el, stem, '.in', nk, el, parent, target))
            print('  built %-50s nk=%-3d (from %s)' % (W.rel(dst), nk, srcstem + '.in'))

    # The children that will be seeded in round 12 must already exist.
    for el, srcstem, parent, newstem, nk, rolls, target in ROWS:
        ch = os.path.join(W.ROOT, 'runs', 's3', el, parent + '__g1.fromparent.in')
        if not os.path.exists(ch):
            W.die('%s: the round-12 child deck does not exist; re-anchoring is '
                  'pointless without it' % W.rel(ch))
        t = W.read(ch)
        if "startingpot='file'" not in t.replace(' ', ''):
            W.die("%s: child deck does not carry startingpot='file'" % W.rel(ch))
        print('  child ready %-46s (startingpot=file)' % W.rel(ch))
    return rows


HDR = """\
# S3 round 11 wave rows (2026-08-27), built by src/dft/build_s3_round11.py.
#
# RE-ANCHOR RUNS. Each row re-runs the deck of record for one banked wave-4
# parent under a NEW prefix. Nothing is replaced: the banked .out files are
# untouched and these are named __reanchor. The point is not to restate the
# parent's energy -- it is to produce, and this time KEEP, a converged density
# at the relaxed geometry in the parent's own magnetic branch.
#
# WHY. Three independent cold scf runs at Co s0_OOH__2x1v_mir's FINAL geometry
# (__g1 24.86, __r2 OOM, __r3 23.95) all locked into the 23-25 uB region by
# iteration 30 and none reached the parent's 20.13. But the parent itself hit
# magtot 19.81 at ionic step 1, cold, from the ORIGINAL geometry, and relaxed
# to 20.13 carrying its density forward. The reachable branch is a property of
# the geometry the SCF cold-starts from: low is reachable from the original
# geometry (mir 3 of 5, ref 2 of 3) and has never been reached from the relaxed
# one in three tries. Re-rolling the child is the one move the evidence rules
# out; re-anchoring the parent is the one that has worked before.
#
# anvil/42_s3_wave1.slurm now retains <prefix>.save minus wavefunctions (40-75
# MB) for any run whose every SCF converged, so a roll that lands low leaves a
# permanent seed. Round 12 runs the existing __g1.fromparent children, which
# already carry startingpot='file', against those seeds.
#
# SCORING. Score on magtot FIRST. A roll landing near the parent's step-1 value
# is a usable anchor; one landing high is banked as evidence and no child is run
# from it. Report dE, dmagtot and dmagabs together; a magnetization mismatch is
# a BRANCH MISMATCH, never agreement and never a refusal to score.
#
"""

HDR_BOT = """\
#
# SUBMIT WITH EXCLUDE=a024,a050,a088,a196,a220,a223   (a050 added 2026-08-26,
# MaxRSS 33.62 GB at kill -- the sixth node, and it was not previously excluded).
#
# row: dir job suffix nk
# NP=128 NCONC=3
"""


def main():
    rows = build()
    body = []
    for d, job, suf, nk, el, parent, t in rows:
        body.append('#   %-3s %-34s nk=%-3d  seeks magtot ~%.2f (parent step 1); '
                    'parent final magtot %.2f / magabs %.2f, E=%.8f\n'
                    % (el, job, nk, t['step1'], t['magtot'], t['magabs'], t['E']))
        body.append('#        %s\n' % t['note'])
    hdr = HDR + ''.join(body) + HDR_BOT

    hits = [l for l in hdr.splitlines() if 'NP=' in l or 'NCONC=' in l]
    if hits != ['# NP=128 NCONC=3']:
        W.die('manifest header must mention NP=/NCONC= exactly once, on the '
              'directive line; found %r' % hits)

    txt = hdr + ''.join('%s %s %s %d\n' % (d, job, suf, nk)
                        for d, job, suf, nk, el, parent, t in rows)
    path = os.path.join(W.ROOT, 'runs', 's3', 'm_s3_round11.txt')
    if os.path.exists(path):
        W.die('%s already exists -- refusing to overwrite' % W.rel(path))
    W.write(path, txt)
    print('\nwrote %s  (%d rows)' % (W.rel(path), len(rows)))
    for d, job, suf, nk, el, parent, t in rows:
        print('  %s %s %s %d' % (d, job, suf, nk))


if __name__ == '__main__':
    main()
