#!/usr/bin/env python
"""S3 round 10 (2026-08-26) -- re-roll the GATE-1 children, because the cheap
unit is the child SCF and not the parent replay.

Round 9 closed two rows and killed one hypothesis, and then a full census of
every GATE-1 pair on disk turned the problem inside out.

  WHAT ROUND 9 ITSELF RETURNED

    Mn s0_OOH__2x1v_off__basin   CONVERGED. 13 ionic steps, `bfgs converged`,
        JOB DONE, notconv 0, min accuracy 3.3e-09. But it converged at magtot
        35.00 / magabs 47.74, while the trajectory it resumed from sat at
        34.76 / 47.87 -- and its first ionic step came back 54.4 meV ABOVE
        that trajectory's last banked energy. A descending BFGS step cannot
        raise the energy by 54 meV, so the branch changed at step 1. The
        converged number is real; it is not the continuation it was asked for.

    Ni s0_OOH__2x1v_mir          FAILED, and informatively. Resuming from
        attempt3's own geometry with its own deck collapsed magtot from 27.94
        to 3.23 inside 41 iterations, then oscillated between 1.37 and 2.16 for
        the remaining ~460 and never completed one ionic step. Splicing a
        geometry does not carry the magnetic state.

    Co ref__2x1v (chain)         KILLED at 9 h 50 m after 3 ionic steps, ~1250
        SU spent, on evidence that it could never have succeeded -- see below.

  THE CENSUS THAT REDEFINED THE PROBLEM

  A GATE-1 child is an `scf` at its parent's FINAL relaxed geometry, so child
  and parent are at byte-identical coordinates by construction. That makes all
  35 GATE-1 pairs on disk exact replicates, and they separate perfectly:

      29 rows  dmagtot <= 0.01   ->  |dE| <= 0.044 meV
       6 rows  dmagtot >= 0.18   ->  |dE| >=  7.39 meV

  Zero overlap; the gap is a factor of 168. Magnetization agreement is not
  correlated with energy agreement, it is equivalent to it.

  And of the six mismatches, THREE have the child BELOW the parent, at the
  parent's own geometry, with both sides converged (notconv 0):

      Fe s0_OOH__1x1_off    child -384.300 meV   magtot 24.46 -> 22.98
      Co s0_O__1x1_off      child  -77.009 meV   magtot 11.69 -> 11.24
      Mn s0_OOH__2x1v_off   child  -20.616 meV   magtot 35.00 -> 34.82

  Those three banked parent relaxations converged in an EXCITED magnetic
  branch. Their energies are too high by 20-384 meV, and every dG computed
  from them inherits that error. This is a science finding, not a convergence
  nuisance, and the canonical-value decision on it is the entrant's.

  WHY RE-ROLLING THE CHILD IS THE RIGHT UNIT

  The A8.3 remedy is to seed the child from the parent's converged density.
  We delete that density after every run (anvil/42_s3_wave1.slurm did an
  unconditional `rm -rf` on the scratch), so A8.3 has to RE-DERIVE it by
  replaying the parent's whole relax. Measured on this tree:

      parent relax replay   41 min - 7 h 47 m   (Co ref__2x1v: ~1000 SU)
      GATE-1 child scf       2 min - 17 min     (median ~6 min, ~13 SU)

  and the replay lands in the parent's branch only 2 times in 5. That is the
  entire reason Co ref__2x1v and Co s0_OOH__2x1v_mir are still open: not the
  physics, but a 20-to-70x more expensive way of obtaining a density we used
  to have and threw away. It is also why the one A8.3 chain that failed
  (Co s0_O__1x1_off__g1.fromparent, -77.009 meV, dmagtot 0.45) failed --
  its replay was 0.45 off the parent and the child faithfully inherited the
  replay's branch, the same 0.45, exactly as a seeded child should.

  So this round re-rolls the CHILD, at ~13 SU a roll, and anvil/42 now retains
  <prefix>.save (~76 MB) for any run whose every SCF converged. A roll that
  lands in the wanted branch is therefore also a permanent branch anchor: the
  parent can then be RE-RELAXED from it in round 11 with no lottery at all.

  GROUP A  BANK THE ANCHOR (3 rows). Re-run the child that already found the
      lower state. Confirms the lower state reproduces, and retains its
      density as the seed for re-relaxing the parent.

  GROUP B  RE-ROLL FOR THE PARENT'S BRANCH (2 rolls of 1 row). Co
      s0_OOH__2x1v_mir is the mirror case: the PARENT is right (magtot 20.13,
      bfgs converged) and the CHILD is 747.449 meV above it at magtot 24.86.
      Two independent rolls; decks differ from the source in the prefix line
      and nothing else, so each roll samples the branch lottery afresh.

  NOT BUILT HERE, and why:

    Co ref__2x1v__g1 -- its child scf ran 500 iterations, never completed one
      SCF cycle (nE 0), and sat at magtot 24.11 against the parent's 21.66.
      The killed replay reached 23.56 and the earlier replay 23.60. The parent
      found 21.66 once, in 325 iterations, and three later attempts have all
      fallen into a 23.5-24.1 region that will not converge. Rolling this row
      costs ~400 SU a roll with no evidence the roll can win. It wants a
      starting_magnetization near the parent's converged moments, which is a
      NEW registered call and therefore the entrant's, not this script's.

    Co s0_OH__2x1v_off, Co s0_O__2x1v_mir -- zero ionic steps across 4 and 5
      attempts, no geometry to resume from, mixing ladder exhausted. Unchanged
      by anything here.

Delegated under the standing instruction of 2026-08-25, quoted in full:
"Continue to make the failures run correctly, run the wave 4 children."
Registered-parameter rulings remain the entrant's and are made by one dated
line; nothing in this round changes a threshold, a functional, or a cell.
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import build_s3_wave2 as W  # noqa: E402


# --------------------------------------------------------------------- rows ---
# (element, parent job, nk, [roll suffixes], group, the state the roll is
#  measured against, why this row is here)
ROWS = [
    ('Fe', 's0_OOH__1x1_off', 16, ['__r2'], 'A',
     dict(E=-2558.16352817, magtot=22.98, magabs=27.39),
     'parent -2558.13528265 is 384.300 meV ABOVE this state at its own geometry'),
    ('Mn', 's0_OOH__2x1v_off', 8, ['__r2'], 'A',
     dict(E=-3617.10020414, magtot=34.82, magabs=47.88),
     'parent -3617.09868891 is 20.616 meV ABOVE this state at its own geometry'),
    ('Co', 's0_O__1x1_off', 16, ['__r2'], 'A',
     dict(E=-2330.66737233, magtot=11.24, magabs=12.02),
     'parent -2330.66171228 is 77.009 meV ABOVE this state at its own geometry'),
    ('Co', 's0_OOH__2x1v_mir', 8, ['__r2', '__r3'], 'B',
     dict(E=-4662.69189747, magtot=20.13, magabs=22.91),
     'child -4662.63696095 is 747.449 meV ABOVE the parent; roll for the parent'),
]

MAG_TOL = 0.05          # Bohr mag/cell; the census puts the real boundary at
                        # 0.01 (pass side) vs 0.18 (fail side), so 0.05 sits in
                        # the empty gap and is not a tuned number.


def build():
    wave_rows = []
    for el, parent, nk, rolls, group, target, why in ROWS:
        base = '%s__g1' % parent
        src_path = os.path.join(W.ROOT, 'runs', 's3', el, base + '.in')
        if not os.path.exists(src_path):
            W.die('%s: source child deck does not exist' % W.rel(src_path))
        src = W.read(src_path)

        # The source deck must be a plain cold scf: no restart of any kind, or
        # the "independent roll" claim is false.
        if W.FORBIDDEN_RESTART.search(src):
            W.die('%s: source child deck carries a restart directive; a re-roll '
                  'of it would not be an independent sample' % W.rel(src_path))
        m = re.search(r"^\s*calculation\s*=\s*'(\w+)'", src, re.M)
        if not m or m.group(1) != 'scf':
            W.die('%s: expected a scf child deck, found %r'
                  % (W.rel(src_path), m and m.group(1)))

        # nat must equal the number of position lines (the round-7 guard).
        nat = int(re.search(r'^\s*nat\s*=\s*(\d+)', src, re.M).group(1))
        a, b = W.pos_block_span(src, src_path)
        rows_src = W.selftest_formatter(src, src_path)
        if nat != len(rows_src):
            W.die('%s: nat=%d but %d position lines'
                  % (W.rel(src_path), nat, len(rows_src)))

        for roll in rolls:
            newbase = base + roll
            dst_path = os.path.join(W.ROOT, 'runs', 's3', el, newbase + '.in')
            out_path = os.path.join(W.ROOT, 'runs', 's3', el, newbase + '.out')
            # A8.8: never write over anything, on either side.
            for p in (dst_path, out_path):
                if os.path.exists(p):
                    W.die('%s already exists -- refusing to overwrite (A8.8). '
                          'Its size is %d bytes.' % (W.rel(p), os.path.getsize(p)))

            new = W.swap_scalar_line(src, src_path, 'prefix', base, newbase)

            # Independent verifier: exactly one differing line, and it is the
            # prefix. Anything else means the roll is not a pure replicate.
            d = W.diff_lines(src, new, dst_path)
            if len(d) != 1:
                W.die('%s: expected exactly 1 differing line vs the source deck, '
                      'got %d: %r' % (W.rel(dst_path), len(d), d))
            kind = W.classify_diff(d[0][1], d[0][2], dst_path)
            if kind != 'prefix':
                W.die('%s: the single diff is %r, not the prefix' % (W.rel(dst_path), kind))
            if W.FORBIDDEN_RESTART.search(new):
                W.die('%s: restart directive appeared during the swap' % W.rel(dst_path))
            if new.count("prefix = '%s'" % newbase) != 1:
                W.die('%s: new prefix not written exactly once' % W.rel(dst_path))

            W.write(dst_path, new)
            wave_rows.append(('s3/%s' % el, newbase, '.in', nk,
                              group, target, why, el, parent))
            print('  built %-52s nk=%-3d group=%s' % (W.rel(dst_path), nk, group))
    return wave_rows


HDR_TOP = """\
# S3 round 10 wave rows (2026-08-26), built by src/dft/build_s3_round10.py.
#
# Every row is a GATE-1 child scf RE-ROLLED under a new prefix. Each deck
# differs from the child deck already on disk in exactly one line -- the
# prefix -- verified line-by-line at build time, so each row is an independent
# sample of the same calculation and nothing on disk is overwritten (A8.8).
#
# WHY THE CHILD AND NOT THE PARENT. A GATE-1 child is an scf at the parent's
# final geometry. Across all 35 GATE-1 pairs on disk, 29 agree to <= 0.044 meV
# with dmagtot <= 0.01 and 6 disagree by >= 7.39 meV with dmagtot >= 0.18 --
# zero overlap, a factor of 168. So a child that lands in the parent's magnetic
# branch reproduces its energy, and one that does not, does not. Re-rolling the
# child costs ~13 SU (median 6 min); replaying the parent to re-derive its
# density costs 500-1000 SU and lands in the parent's branch 2 times in 5.
#
# anvil/42_s3_wave1.slurm now retains <prefix>.save (~76 MB) for any run whose
# every SCF converged, so a winning roll is also a permanent branch anchor and
# round 11 can re-relax the parent from it with no lottery.
#
# SCORING. Report dE, dmagtot and dmagabs together. A magnetization mismatch is
# a BRANCH MISMATCH -- never agreement, and never a refusal to score.
#
"""

HDR_BOT = """\
#
# SUBMIT WITH EXCLUDE=a024,a088,a196,a220,a223.
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""


def main():
    rows = build()

    body = []
    for group, title in (('A', 'GROUP A -- bank the anchor: the child already found a state '
                               'BELOW its parent; re-run it to confirm and to retain its density'),
                         ('B', 'GROUP B -- re-roll for the parent branch: the parent is right '
                               'and the child is the one in the excited state')):
        body.append('# %s\n#\n' % title)
        for d, job, suf, nk, g, t, why, el, parent in rows:
            if g != group:
                continue
            body.append('#   %-3s %-40s nk=%-3d\n' % (el, job, nk))
            body.append('#        %s\n' % why)
            body.append('#        target: E=%.8f Ry  magtot=%.2f  magabs=%.2f  '
                        '(mag tol %.2f)\n' % (t['E'], t['magtot'], t['magabs'], MAG_TOL))
        body.append('#\n')

    hdr = HDR_TOP + ''.join(body) + HDR_BOT
    lines = [hdr]
    for d, job, suf, nk, g, t, why, el, parent in rows:
        lines.append('%s %s %s %d\n' % (d, job, suf, nk))
    txt = ''.join(lines)

    # The driver passes NCONC positionally; the directive line must be the ONLY
    # line in the header that mentions those tokens (round-6 lesson).
    hits = [l for l in hdr.splitlines() if 'NP=' in l or 'NCONC=' in l]
    if hits != ['# NP=128 NCONC=1']:
        W.die('manifest header must mention NP=/NCONC= exactly once, on the '
              'directive line; found %r' % hits)

    path = os.path.join(W.ROOT, 'runs', 's3', 'm_s3_round10.txt')
    if os.path.exists(path):
        W.die('%s already exists -- refusing to overwrite' % W.rel(path))
    W.write(path, txt)
    print('\nwrote %s  (%d rows)' % (W.rel(path), len(rows)))
    for d, job, suf, nk, g, t, why, el, parent in rows:
        print('  %s %s %s %d' % (d, job, suf, nk))


if __name__ == '__main__':
    main()
