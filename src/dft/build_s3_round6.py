#!/usr/bin/env python
"""S3 round 6 (2026-08-26) -- the round-5 remainder, in three groups.

Round 5 (array 20141568, docs/45) proved `mixing_ndim = 16` on the row that was
allowed to run cleanly: `Co s0_OH__2x1v_mir` converged in 18 BFGS steps to
8.5e-09 with the Broyden history depth as the ONLY change from its failed
attempt3 (both echo `number of iterations used` in the .out, 8 vs 16, at the
same beta / threshold / mixing mode). It also lost four rows to Anvil node a196
(ALLOCATED+DRAIN, `NHC: Terminated by signal SIGTERM`, FreeMem 384 MB) and found
two `__g1` children in the wrong magnetic branch.

  GROUP A  RE-RUN, DECKS UNCHANGED (4 rows). Tasks 3/5/6 were OOM-killed on a196
        at MaxRSS 8.65-8.70 GB while the round's healthy runs peaked at 30.8-46.8
        GB -- killed for the node's lack of memory, not their own use of it.
        Task 7 was cancelled by hand after 1h45m of zero SCF iterations on the
        same node. None of the four is evidence about anything; they are the same
        decks, re-queued away from a196. NO deck is rebuilt here: the round-5
        `.retry_ndim.in` files (including the two geometry splices) are already
        correct and are re-used byte-for-byte.

  GROUP B  NEXT LADDER RUNG (1 row). `Co s0_OOH__2x1v_off` had the full ndim=16
        treatment on a healthy node (a201, 2h00m) and still failed: one SCF
        cycle, 500 iterations, last accuracy 2.0e-3. The remaining untried piece
        of the R1 slab campaign's attempt-4 pairing is `mixing_beta` 0.15 -> 0.05,
        so that is the one line this group changes. ndim stays 16: round 5
        established it as the better setting, and un-setting it would make this a
        two-variable test again. The round-5 run completed ZERO ionic steps, so
        there is no new geometry to splice and the coordinates are untouched.

  GROUP C  A8.3 DENSITY RETENTION (2 chains). `Co s0_OOH__2x1v_mir__g1` came back
        +747.4 meV at Dmagtot +4.73 and `Fe s0_OOH__1x1_off__basin__g1` +7.4 meV
        at Dmagtot +4.00 / Dmagabs +0.03 -- the Fe one is ~2 uB flipped down-to-up
        with the local moments unchanged in size, i.e. a different magnetic
        configuration at the same geometry, not a convergence artifact. Neither
        is a GATE-1 refusal of the banked energy; both are cold SCF starts in the
        wrong basin, which is the exact failure A8.3 exists for and exactly what
        it fixed for `Ni s0_OH__2x1v_off__g1` in round 4 (three cold failures and
        the wrong branch at 12.24 vs 14.41 uB -> 12 iterations from the parent
        density, +0.005 meV). No parent .save survives, so each needs the full
        replay first.

        The parent deck replayed is the one that PRODUCED the banked .out, fixed
        by manifest provenance rather than inferred: m_s3_round3.txt:7 gives Co
        `.retry_ms.in` and m_s3_round3.txt:14 gives Fe `.in`. Asserted below
        against the beta echoed in the banked output.

A8.8: every deck written here is a NEW filename, and Group A writes none at all.
No existing deck is touched. The round-5 `.out` files that these rows will
overwrite are archived to `.out.attempt<N+1>` by the deployment step, not here.
"""
import difflib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------- group A/B
# (dir, job, suffix, nk, why) -- decks already on disk, re-queued unchanged.
RERUN = [
    ('s3/Co', 's0_OH__2x1v_off', '.retry_ndim.in', 8, 'OOM a196'),
    ('s3/Ni', 's0_OOH__2x1v_mir', '.retry_ndim.in', 8, 'OOM a196'),
    ('s3/Ni', 's0_OOH__2x1v_off', '.retry_ndim.in', 8, 'OOM a196'),
    ('s3/Mn', 's0_OOH__2x1v_off__basin', '.retry_ndim.in', 8, 'hung a196, cancelled'),
]

# (dir, job, source suffix, nk) -- one line changes: mixing_beta 0.15 -> 0.05.
BETA = [('s3/Co', 's0_OOH__2x1v_off', '.retry_ndim.in', 8)]
NEW_BETA = '0.05'
BETA_SUFFIX = '.retry_b05.in'

# ------------------------------------------------------------------ group C
# (dir, parent_deck, child_deck, beta the banked .out must echo)
A83_CHAINS = [
    ('runs/s3/Co', 's0_OOH__2x1v_mir.retry_ms.in',
     's0_OOH__2x1v_mir__g1.in', '0.1500'),
    ('runs/s3/Fe', 's0_OOH__1x1_off__basin.in',
     's0_OOH__1x1_off__basin__g1.in', '0.3000'),
]


def die(msg):
    print('REFUSE: ' + msg)
    sys.exit(1)


def get_prefix(txt, path):
    m = re.search(r"^  prefix = '([^']+)'$", txt, re.M)
    assert m, path
    return m.group(1)


def only_diff(a, b):
    """(changed_pairs, inserted_lines) between a and b; deletions are fatal."""
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
            raise AssertionError('unexpected delete: %r' % (la[i1:i2],))
    return ch, ins


def pick_nk(out_text, path):
    m = re.search(r'number of k points=\s*(\d+)', out_text)
    assert m, 'no k-point count in %s' % path
    nks = int(m.group(1))
    nk = 16 if nks >= 16 else 8
    assert 128 % nk == 0 and nk <= nks, (path, nks, nk)
    return nks, nk


def base_of(deck):
    for suf in ('.retry_ndim.in', '.retry_ms.in', '.retry_bh.in', '.in'):
        if deck.endswith(suf):
            return deck[:-len(suf)]
    raise AssertionError(deck)


wave_rows, chain_rows, notes = [], [], []

# ------------------------------------------------- GROUP A: verify, don't build
for d, job, suf, nk, why in RERUN:
    deck = ROOT / 'runs' / d / (job + suf)
    if not deck.exists():
        die('group A deck missing: %s' % deck)
    txt = deck.read_text()
    if '  mixing_ndim = 16' not in txt:
        die('group A deck lost its mixing_ndim: %s' % deck)
    if re.search(r'^\s*(restart_mode|startingpot|startingwfc)\s*=', txt, re.M):
        die('group A deck carries a restart key: %s' % deck)
    wave_rows.append('%s %s %s %d' % (d, job, suf, nk))
    notes.append('A      %s/%s%s  re-run unchanged  [%s]' % (d, job, suf, why))

# ------------------------------------------------------ GROUP B: one-line rung
for d, job, suf, nk in BETA:
    src = ROOT / 'runs' / d / (job + suf)
    txt = src.read_text()
    m = re.search(r'^  mixing_beta = (.+)$', txt, re.M)
    if not m:
        die('no mixing_beta in %s' % src)
    old = m.group(1).strip()
    if old == NEW_BETA:
        die('%s is already at beta %s' % (src, NEW_BETA))
    new = txt.replace('  mixing_beta = %s\n' % old,
                      '  mixing_beta = %s\n' % NEW_BETA)
    ch, ins = only_diff(txt, new)
    if ins or len(ch) != 1 or 'mixing_beta' not in ch[0][0]:
        die('group B diff is not the single beta line: %r %r' % (ch, ins))
    if '  mixing_ndim = 16' not in new:
        die('group B deck lost mixing_ndim')
    if 'ATOMIC_POSITIONS' not in new:
        die('group B deck has no positions block')
    out = ROOT / 'runs' / d / (job + BETA_SUFFIX)
    if out.exists():
        die('A8.8: %s already exists' % out)
    out.write_text(new, newline='\n')
    wave_rows.append('%s %s %s %d' % (d, job, BETA_SUFFIX, nk))
    notes.append('B      %s/%s%s  mixing_beta %s -> %s  (ndim 16 retained)'
                 % (d, job, BETA_SUFFIX, old, NEW_BETA))

# ------------------------------------------------------- GROUP C: A8.3 chains
for d, pdeck, cdeck, want_beta in A83_CHAINS:
    dd = ROOT / d
    ptxt = (dd / pdeck).read_text()
    ctxt = (dd / cdeck).read_text()
    pout = dd / (base_of(pdeck) + '.out')
    pot = pout.read_text(errors='replace')

    if 'JOB DONE' not in pot or 'convergence NOT achieved' in pot:
        die('parent not cleanly converged: %s' % pout)
    if not ('End of BFGS Geometry Optimization' in pot or 'bfgs converged' in pot):
        die('parent is not a converged relax: %s' % pout)
    if not re.search(r"^  calculation = 'scf'$", ctxt, re.M):
        die('child is not an scf deck: %s' % cdeck)

    # provenance: the replayed deck must be the one that made the banked .out
    got = re.search(r'mixing beta\s+=\s+([\d.]+)', pot).group(1)
    if got != want_beta:
        die('%s echoes beta %s, deck %s expects %s' % (pout, got, pdeck, want_beta))
    dbeta = re.search(r'^  mixing_beta = (.+)$', ptxt, re.M).group(1).strip()
    if abs(float(dbeta) - float(want_beta)) > 1e-9:
        die('%s has beta %s, banked .out echoes %s' % (pdeck, dbeta, want_beta))

    pprefix = get_prefix(ptxt, pdeck)
    cprefix = get_prefix(ctxt, cdeck)

    # replay deck: prefix change ONLY
    rtxt = ptxt.replace("  prefix = '%s'\n" % pprefix,
                        "  prefix = '%s__replay'\n" % pprefix)
    ch, ins = only_diff(ptxt, rtxt)
    if ins or len(ch) != 1 or 'prefix' not in ch[0][0]:
        die('replay diff is not prefix-only: %s %r %r' % (pdeck, ch, ins))
    rname = base_of(pdeck) + '.replay.in'
    if (dd / rname).exists():
        die('A8.8: %s already exists' % rname)
    (dd / rname).write_text(rtxt, newline='\n')

    # child deck: prefix change + startingpot insertion ONLY
    ftxt = ctxt.replace("  prefix = '%s'\n" % cprefix,
                        "  prefix = '%s__fp'\n" % cprefix)
    ftxt = ftxt.replace('&ELECTRONS\n', "&ELECTRONS\n  startingpot = 'file'\n")
    if ftxt.count("startingpot = 'file'") != 1:
        die('startingpot insertion failed for %s' % cdeck)
    ch, ins = only_diff(ctxt, ftxt)
    if len(ch) != 1 or 'prefix' not in ch[0][0] or ins != ["  startingpot = 'file'"]:
        die('child diff is not {prefix, startingpot}: %s %r %r' % (cdeck, ch, ins))
    fname = base_of(cdeck) + '.fromparent.in'
    if (dd / fname).exists():
        die('A8.8: %s already exists' % fname)
    (dd / fname).write_text(ftxt, newline='\n')

    nks, nk = pick_nk(pot, pout)
    chain_rows.append('%s %s %s__replay %s %s__fp %d'
                      % (d, rname, pprefix, fname, cprefix, nk))
    notes.append('C      %s: %s -> %s  (k=%d nk=%d, parent beta %s)'
                 % (d, rname, fname, nks, nk, dbeta))

# ------------------------------------------------------------------- manifests
WAVE_HDR = """\
# S3 round 6 wave rows (2026-08-26), built by src/dft/build_s3_round6.py.
#
# Rows 1-4  GROUP A: the four rows Anvil node a196 destroyed in round 5. a196 was
#           ALLOCATED+DRAIN with `NHC: Terminated by signal SIGTERM` and 384 MB
#           free; three rows were OOM-killed at MaxRSS 8.65-8.70 GB while the
#           round's healthy runs peaked at 30.8-46.8 GB, and the fourth wrote a
#           header and then produced zero SCF iterations for 1h45m before I
#           cancelled it. The decks are UNCHANGED round-5 `.retry_ndim.in` files,
#           re-used byte-for-byte, including the Mn and Ni geometry splices.
#           SUBMIT WITH EXCLUDE=a024,a088,a196.
# Row 5     GROUP B: `Co s0_OOH__2x1v_off` failed the full ndim=16 treatment on a
#           healthy node (a201, 2h00m, one SCF cycle, 500 iterations, last
#           accuracy 2.0e-3). This row changes exactly one line, mixing_beta
#           0.15 -> 0.05, the last untried piece of the R1 slab campaign's
#           attempt-4 pairing. ndim stays 16. Zero ionic steps completed in round
#           5, so the coordinates are untouched.
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""

CHAIN_HDR = """\
# S3 round 6 chains (2026-08-26), built by src/dft/build_s3_round6.py. Same row
# format and runner (anvil/44_chain.slurm) as m_round4.txt.
#
# GROUP C: A8.3 density retention for the two round-5 `__g1` children that came
# back in the wrong magnetic branch -- Co s0_OOH__2x1v_mir__g1 at +747.4 meV /
# Dmagtot +4.73, and Fe s0_OOH__1x1_off__basin__g1 at +7.4 meV / Dmagtot +4.00
# with Dmagabs only +0.03 (about 2 uB flipped down-to-up at unchanged local
# moment size: a different magnetic configuration at the same geometry). Neither
# refuses its banked parent's energy; both are cold SCF starts landing in the
# wrong basin, the failure A8.3 exists for. It fixed exactly this for
# Ni s0_OH__2x1v_off__g1 in round 4: three cold failures in the wrong branch,
# then 12 iterations from the parent density and +0.005 meV.
#
# No parent .save survives a completed job, so step 1 replays the parent deck --
# the one that produced the banked .out, fixed by manifest provenance
# (m_s3_round3.txt:7 Co `.retry_ms.in`, m_s3_round3.txt:14 Fe `.in`) and asserted
# against the mixing beta echoed in that .out. The replay energy is parity
# evidence and is NEVER banked (A8.8), as in every prior chain round.
#
# SUBMIT WITH EXCLUDE=a024,a088,a196.
#
# row: dir replay_deck replay_prefix child_deck child_prefix nk
# NP=128 NCONC=1
"""

for hdr, rows, path in ((WAVE_HDR, wave_rows, 'runs/s3/m_s3_round6.txt'),
                        (CHAIN_HDR, chain_rows, 'runs/chains/m_round6.txt')):
    # the driver parses `NP=<n> NCONC=<n>` and refuses if any OTHER line mentions
    # those tokens -- round 5 was refused twice for exactly this.
    hits = [l for l in hdr.splitlines() if 'NP=' in l or 'NCONC=' in l]
    if hits != ['# NP=128 NCONC=1']:
        die('%s: directive must be the only line naming it: %r' % (path, hits))
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(hdr + '\n'.join(rows) + '\n', newline='\n')
    print('wrote %s: %d rows' % (path, len(rows)))

print()
for n in notes:
    print(n)
