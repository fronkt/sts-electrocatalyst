#!/usr/bin/env python
"""S3 round 9 (2026-08-26) -- second-generation resumes, and one genuinely SLOW replay.

Round 8 landed three wave rows on healthy nodes and produced the second win for
the resume-from-deepest recipe:

  Ni s0_OOH__2x1v_off   RESUMED from its 1 banked ionic step -> **41 ionic steps,
        bfgs converged**, min accuracy 5.0e-09 at the 1e-08 upscale floor. This
        was the row docs recorded as "BRANCH, no parent to seed from, the one row
        with no registered remedy in hand". It needed a restart, not a remedy.

and two rows that did not finish, each for its own reason.

  GROUP A  SECOND-GENERATION RESUME (2 rows).

    Mn s0_OOH__2x1v_off__basin is WORKING and simply needs more ionic steps. Its
        round-8 run resumed from attempt1's 19th step (-3617.10180292) and carried
        it three steps further to -3617.10197097 at identical magnetization
        (34.76 / 47.87), converging every SCF cycle to the 1e-08 floor (min
        6.0e-09). It stopped in cycle 4. Resume again from where it now is.

        **This breaks the round-7 selector.** `deepest_attempt()` chose by MOST
        IONIC STEPS, which would pick attempt1 (19) over the round-8 run (3) and
        throw away three steps -- because once resumes chain, step COUNT stops
        tracking depth. The correct comparison is the lowest final energy among
        runs sharing a magnetic branch, and this builder asserts exactly that
        rather than inferring it.

    Ni s0_OOH__2x1v_mir gets its `mixing_ndim = 16` REMOVED. The evidence is one
        way:

          attempt1  ndim 8   2 ionic  magtot  9.87  min 7.3e-07
          attempt2  ndim 8   2 ionic  magtot 13.72  min 3.8e-07
          attempt3  ndim 8   3 ionic  magtot 13.78  min 3.2e-07
          round 8   ndim 16  0 ionic  magtot **-0.27**  min 2.2e-04

        At ndim 8 this deck sat in a 9.9-13.8 uB branch and descended to 3.2e-07
        against an upscale-tightened 2.79e-07 -- an UNREG_THR row that is nearly
        there. At ndim 16 it collapsed into a near-compensated state (magtot
        -0.27 with magabs 25.70, i.e. large moments cancelling) and got nowhere.
        So this row resumes from attempt3's geometry using ATTEMPT3'S OWN DECK.

  GROUP B  ONE CHAIN, with electron_maxstep raised (1 row).

    Co ref__2x1v's replay failed, but unlike Co s0_OOH__2x1v_mir it failed while
    still descending monotonically:

          ... 4.56e-06  4.52e-06  4.45e-06  4.04e-06  3.81e-06   <- iteration 500

    against a 1e-06 target, where the banked parent converged cycle 1 in 324
    iterations. That is SLOW, not STALLED, and the remedy is iterations. The
    replay deck is rebuilt with electron_maxstep 500 -> 1500 and nothing else.

    Checked and DISCARDED: the hypothesis that the banked parents were warm
    started from leftover scratch, which would have explained the replay failures
    cheaply. Both parent and replay report `Initial potential from superposition
    of free atoms`, and anvil/42_s3_wave1.slurm `rm -rf`s the scratch directory
    before every job. The parents are genuine cold starts.

NOT re-run: Co s0_OOH__2x1v_mir. Two independent replays of that parent's own
deck have now failed to converge (ndim 8 -> 2.477e-05, ndim 16 -> 4.24e-04, i.e.
the deeper history made it worse). It is a reproducibility question for R3/A8.6,
not a convergence-tuning one, and is Frank's.

A8.8: every deck written here is a NEW filename. The `.out` files this round
overwrites are archived to `.out.attempt<N+1>` by the deployment step, not here.
"""
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_s3_wave2 as W  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S3 = os.path.join(ROOT, 'runs', 's3')

# (metal, job, source .out to resume FROM, deck to splice INTO, new suffix, nk)
RESUME = [
    ('Mn', 's0_OOH__2x1v_off__basin', 's0_OOH__2x1v_off__basin.out',
     's0_OOH__2x1v_off__basin.retry_ndim.in', '.resume2.in', 8),
    ('Ni', 's0_OOH__2x1v_mir', 's0_OOH__2x1v_mir.out.attempt3',
     's0_OOH__2x1v_mir.retry_ms.in', '.resume.in', 8),
]

# (dir, parent deck, new replay deck, child deck, new electron_maxstep)
CHAINS = [
    ('runs/s3/Co', 'ref__2x1v.retry_ms.in', 'ref__2x1v.replay_ms.in',
     'ref__2x1v__g1.fromparent.in', '1500'),
]

MAG_TOL = 0.05


def only_diff(a, b, path):
    la, lb = a.splitlines(), b.splitlines()
    sm = difflib.SequenceMatcher(None, la, lb, autojunk=False)
    ch, ins = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        if tag == 'replace':
            ch += list(zip(la[i1:i2], lb[j1:j2]))
        elif tag == 'insert':
            ins += lb[j1:j2]
        else:
            W.die('%s: unexpected deletion %r' % (path, la[i1:i2]))
    return ch, ins


def last_positions(out_path):
    lines = W.read(out_path).splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith('ATOMIC_POSITIONS')]
    if not starts:
        return None
    out = []
    for l in lines[starts[-1] + 1:]:
        m = re.match(r'^([A-Z][a-z]?)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)', l)
        if not m:
            break
        out.append((m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4))))
    return out or None


def summarise(path):
    t = W.read(path)
    E = [float(x) for x in re.findall(r'^!\s+total energy\s+=\s+(-?[\d.]+) Ry', t, re.M)]
    M = [float(x) for x in re.findall(r'total magnetization\s+=\s+(-?[\d.]+)', t)]
    return {'n': len(E), 'E': E[-1] if E else None,
            'mag': M[-1] if M else None, 'name': os.path.basename(path)}


def census(d, job):
    out = []
    for fn in sorted(os.listdir(d)):
        if fn == job + '.out' or fn.startswith(job + '.out.attempt'):
            out.append(summarise(os.path.join(d, fn)))
    return out


def get_prefix(txt, path):
    m = re.search(r"^  prefix = '([^']+)'$", txt, re.M)
    if not m:
        W.die('%s: no prefix' % path)
    return m.group(1)


def pick_nk(out_text, path):
    m = re.search(r'number of k points=\s*(\d+)', out_text)
    if not m:
        W.die('no k-point count in %s' % path)
    nks = int(m.group(1))
    nk = 16 if nks >= 16 else 8
    if 128 % nk or nk > nks:
        W.die('bad nk for %s' % path)
    return nks, nk


wave_rows, chain_rows, notes = [], [], []

# --------------------------------------------- GROUP A: second-generation resume
for metal, job, src_out, deck, new_suf, nk in RESUME:
    d = os.path.join(S3, metal)
    out_p = os.path.join(d, src_out)
    src = os.path.join(d, deck)
    if not os.path.exists(out_p):
        W.die('source .out missing: %s' % W.rel(out_p))
    chosen = summarise(out_p)
    if not chosen['n']:
        W.die('%s has 0 ionic steps -- nothing to resume from' % src_out)

    # AUDIT the choice rather than trusting it: among runs in the SAME magnetic
    # branch, the resume source must have the lowest final energy. Step COUNT is
    # not depth once resumes chain (Mn: 19 steps then 3 more, and the 3 are deeper).
    all_runs = census(d, job)
    same_branch = [r for r in all_runs
                   if r['E'] is not None and r['mag'] is not None
                   and abs(r['mag'] - chosen['mag']) <= MAG_TOL]
    deeper = [r for r in same_branch if r['E'] < chosen['E'] - 1e-9]
    if deeper:
        W.die('%s/%s: %s is deeper than the chosen %s (%s < %s)'
              % (metal, job, deeper[0]['name'], chosen['name'],
                 deeper[0]['E'], chosen['E']))

    src_txt = W.read(src)
    deck_rows = W.selftest_formatter(src_txt, src)
    if not re.search(r"^  calculation = 'relax'$", src_txt, re.M):
        W.die('%s: not a relax' % W.rel(src))

    pos = last_positions(out_p)
    if not pos:
        W.die('%s: no ATOMIC_POSITIONS block' % src_out)
    if len(pos) != len(deck_rows):
        W.die('%s: %d atoms != %d in deck' % (src_out, len(pos), len(deck_rows)))
    if [p[0] for p in pos] != [r[0] for r in deck_rows]:
        W.die('%s: species order differs from deck' % src_out)
    new_rows = [(sp, '%.8f' % x, '%.8f' % y, '%.8f' % z, r[4])
                for (sp, x, y, z), r in zip(pos, deck_rows)]
    txt = W.swap_positions(src_txt, src, new_rows)

    ch, ins = only_diff(src_txt, txt, W.rel(src))
    if ins:
        W.die('%s: resume must insert nothing, got %r' % (W.rel(src), ins))
    moved = 0
    for x, y in ch:
        px, py = x.split(), y.split()
        if not (len(px) in (4, 7) and len(py) == len(px)
                and px[0] == py[0] and px[4:] == py[4:]):
            W.die('%s: non-coordinate change %r -> %r' % (W.rel(src), x, y))
        if px[4:] and px[4:] != ['1', '1', '1']:
            W.die('%s: a FROZEN atom moved: %r' % (W.rel(src), x))
        moved += 1
    if not moved:
        W.die('%s: splice moved no atoms' % W.rel(src))
    nat = int(re.search(r'^\s*nat\s*=\s*(\d+)', txt, re.M).group(1))
    if nat != len(new_rows):
        W.die('%s: nat=%d != %d rows' % (W.rel(src), nat, len(new_rows)))
    if W.FORBIDDEN_RESTART.search(txt):
        W.die('%s: restart key emitted' % W.rel(src))

    out = os.path.join(d, job + new_suf)
    if os.path.exists(out):
        W.die('A8.8: %s already exists' % W.rel(out))
    W.write(out, txt)
    has_nd = 'yes' if re.search(r'^\s*mixing_ndim\s*=\s*16', txt, re.M) else 'no'
    wave_rows.append('s3/%s %s %s %d' % (metal, job, new_suf, nk))
    notes.append('A      s3/%s/%s%s  from %s (%d ionic, E=%s, mag=%s), ndim16=%s, '
                 '%d/%d atoms moved'
                 % (metal, job, new_suf, chosen['name'], chosen['n'], chosen['E'],
                    chosen['mag'], has_nd, moved, len(pos)))
    for r in all_runs:
        notes.append('         %-46s ionic=%-3d E=%-18s mag=%s'
                     % (r['name'], r['n'], r['E'], r['mag']))

# ------------------------------------------------ GROUP B: SLOW replay, more steps
for d, pdeck, rname, cname, new_ms in CHAINS:
    dd = os.path.join(ROOT, d)
    ptxt = W.read(os.path.join(dd, pdeck))
    base = pdeck.split('.retry_ms.in')[0]
    pot = W.read(os.path.join(dd, base + '.out'))
    if 'JOB DONE' not in pot or 'convergence NOT achieved' in pot:
        W.die('parent not cleanly converged: %s.out' % base)

    pprefix = get_prefix(ptxt, pdeck)
    rtxt = ptxt.replace("  prefix = '%s'\n" % pprefix,
                        "  prefix = '%s__replay'\n" % pprefix)
    old_ms = re.search(r'^\s*electron_maxstep\s*=\s*(\d+)\s*$', ptxt, re.M)
    if not old_ms:
        W.die('%s: no electron_maxstep' % pdeck)
    if old_ms.group(1) == new_ms:
        W.die('%s: already at maxstep %s' % (pdeck, new_ms))
    rtxt = re.sub(r'^(\s*electron_maxstep\s*=\s*)\d+\s*$', r'\g<1>' + new_ms,
                  rtxt, count=1, flags=re.M)
    ch, ins = only_diff(ptxt, rtxt, pdeck)
    if ins or len(ch) != 2:
        W.die('replay diff must be exactly {prefix, maxstep}: %r %r' % (ch, ins))
    keys = sorted('prefix' if 'prefix' in x else
                  ('maxstep' if 'electron_maxstep' in x else 'OTHER') for x, _ in ch)
    if keys != ['maxstep', 'prefix']:
        W.die('replay diff touched something else: %r' % ch)
    rp = os.path.join(dd, rname)
    if os.path.exists(rp):
        W.die('A8.8: %s already exists' % rname)
    W.write(rp, rtxt)

    cp = os.path.join(dd, cname)
    ctxt = W.read(cp)
    if "startingpot = 'file'" not in ctxt:
        W.die('%s has no startingpot' % cname)
    if os.path.exists(cp.replace('.in', '.out')):
        W.die('A8.8: %s already has an .out' % cname)
    cprefix = get_prefix(ctxt, cname)

    nks, nk = pick_nk(pot, base + '.out')
    chain_rows.append('%s %s %s__replay %s %s %d'
                      % (d, rname, pprefix, cname, cprefix, nk))
    notes.append('B      %s: %s -> %s  (k=%d nk=%d, maxstep %s -> %s)'
                 % (d, rname, cname, nks, nk, old_ms.group(1), new_ms))

# ------------------------------------------------------------------- manifests
WAVE_HDR = """\
# S3 round 9 wave rows (2026-08-26), built by src/dft/build_s3_round9.py.
#
# Row 1  Mn s0_OOH__2x1v_off__basin -- SECOND-generation resume. Its round-8 run
#        picked up attempt1's 19th step (-3617.10180292) and carried it three
#        steps further to -3617.10197097 at identical magnetization (34.76 /
#        47.87), converging every cycle to the 1e-08 floor. It stopped in cycle 4.
#
#        Note this breaks round 7's selector: `deepest_attempt()` chose by MOST
#        IONIC STEPS and would have picked attempt1 (19) over the round-8 run (3),
#        discarding three steps. Once resumes chain, step count stops tracking
#        depth. This builder selects by LOWEST FINAL ENERGY WITHIN A MAGNETIC
#        BRANCH and asserts no same-branch run is deeper than the one chosen.
#
# Row 2  Ni s0_OOH__2x1v_mir -- resume from attempt3 using ATTEMPT3'S OWN DECK,
#        which means mixing_ndim = 16 is REMOVED. At ndim 8 this deck sat in a
#        9.9-13.8 uB branch across three attempts and descended to 3.2e-07 against
#        an upscale-tightened 2.79e-07. At ndim 16 it collapsed to magtot -0.27
#        with magabs 25.70 -- large moments cancelling -- and completed no ionic
#        steps at all. R1 (`upscale`) remains the clean fix for this row.
#
# SUBMIT WITH EXCLUDE=a024,a088,a196,a220,a223.
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""

CHAIN_HDR = """\
# S3 round 9 chains (2026-08-26), built by src/dft/build_s3_round9.py.
#
# Co ref__2x1v, the last owed wave-4 child. Round 8's replay failed, but unlike
# Co s0_OOH__2x1v_mir it failed while still descending monotonically:
#
#     ... 4.56e-06  4.52e-06  4.45e-06  4.04e-06  3.81e-06   <- iteration 500
#
# against a 1e-06 target, where the banked parent converged cycle 1 in 324
# iterations. That is SLOW, not STALLED. This replay deck differs from the parent
# in exactly two lines: prefix, and electron_maxstep 500 -> 1500.
#
# Checked and DISCARDED before building this: the hypothesis that the banked
# parents were warm started from leftover scratch, which would have explained the
# replay failures cheaply. Both parent and replay report `Initial potential from
# superposition of free atoms`, and anvil/42_s3_wave1.slurm rm -rf's the scratch
# directory before every job. The parents are genuine cold starts.
#
# NOT re-run: Co s0_OOH__2x1v_mir. Two independent replays of that parent's own
# deck have failed to converge, and the deeper Broyden history made it worse
# (ndim 8 -> 2.477e-05, ndim 16 -> 4.24e-04). That is a reproducibility question
# for R3 / A8.6, not a convergence-tuning one.
#
# SUBMIT WITH EXCLUDE=a024,a088,a196,a220,a223.
#
# row: dir replay_deck replay_prefix child_deck child_prefix nk
# NP=128 NCONC=1
"""

for hdr, rows, path in ((WAVE_HDR, wave_rows, 'runs/s3/m_s3_round9.txt'),
                        (CHAIN_HDR, chain_rows, 'runs/chains/m_round9.txt')):
    hits = [l for l in hdr.splitlines() if 'NP=' in l or 'NCONC=' in l]
    if hits != ['# NP=128 NCONC=1']:
        W.die('%s: directive must be the only line naming it: %r' % (path, hits))
    with open(os.path.join(ROOT, path), 'w', newline='\n', encoding='utf-8') as f:
        f.write(hdr + '\n'.join(rows) + '\n')
    print('wrote %s: %d rows' % (path, len(rows)))

print()
for n in notes:
    print(n)
