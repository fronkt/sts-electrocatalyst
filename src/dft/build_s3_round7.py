#!/usr/bin/env python
"""S3 round 7 (2026-08-26) -- resume from the DEEPEST geometry, not the LAST one.

Round 6 failed on every relax row it ran, and scoring them exposed a defect in
how round 5 and 6 chose their restart geometry. `build_s3_round5.py` spliced from
`job + '.out'` -- the most RECENT attempt -- and never looked at
`job + '.out.attempt*'`. For `Co s0_OOH__2x1v_off` that threw away real work:

  attempt1  crashed, 0 ionic steps
  attempt2  base deck, beta 0.3   -> **14 ionic steps**, last new conv_thr 4.10e-8
  attempt3  beta 0.15 / maxstep 200 ->  0 ionic steps
  attempt4  beta 0.15 / maxstep 500 ->  0 ionic steps
  attempt5  round 5, ndim 16        ->  0 ionic steps
  round 6   ndim 16 + beta 0.05     ->  0 ionic steps

Every rung of the A8.4 ladder after attempt2 restarted from the ORIGINAL geometry
and got stuck in the first SCF, so the ladder has been re-running the hardest
step of the trajectory over and over while 14 converged ionic steps sat unused in
an archived file. `Ni s0_OOH__2x1v_off` has the same shape at a smaller scale
(attempt2: 1 ionic step; every later attempt: 0).

Note what attempt2 was actually doing when it stopped: 14 converged ionic steps,
being held by the unset `upscale` (QE default 100) to `new conv_thr = 4.10e-8`,
i.e. 24x TIGHTER than this deck's registered 1e-6, and reaching 3e-8. That is the
UNREG_THR mechanism, not a mixing failure -- so **R1 (declare `upscale`) remains
the cleaner fix for this row and is still Frank's call.** This round does what can
be done without a registered-parameter ruling: resume the trajectory that was
working, with a deeper Broyden history and the campaign-standard iteration budget.

  GROUP A  RE-RUN, DECKS UNCHANGED (2 rows). `Ni s0_OOH__2x1v_mir` and
        `Mn s0_OOH__2x1v_off__basin` were OOM-killed on node **a220** in round 6
        at MaxRSS 35.1 GB against a granted `mem=237G`. a220 shows no DRAIN and no
        NHC record -- it is the a024/a088 shape (silently bad, still in the pool),
        not the a196 shape. The two decks already carry the round-5 splices from
        their own deepest attempts (19 and 3 ionic steps), which were correct.

  GROUP B  RESUME FROM DEEPEST (2 rows). Splice the final ATOMIC_POSITIONS of the
        attempt with the most completed ionic steps into THE DECK THAT PRODUCED
        THAT ATTEMPT (asserted by the mixing beta echoed in the .out), then add
        `mixing_ndim = 16` and raise electron_maxstep to the campaign standard
        500. The deck choice matters: for both rows the deepest attempt ran at the
        ORIGINAL beta 0.3, so resuming at the ladder's escalated beta would change
        two things at once and abandon the setting that actually made progress.

  GROUP C  A8.3 CHAINS (2). Round 6 proved this remedy works and also found its
        failure mode:
          Fe s0_OOH__1x1_off__basin  replay -0.049 meV, child **+0.004 meV** and
                in the parent's branch (22.98/27.59 on all three) -- a +7.4 meV
                branch mismatch closed to 4 ueV. GATE-1 closed.
          Co s0_OOH__2x1v_mir  **CHAIN FAIL: replay non-convergent.** The parent's
                own deck, re-run, matched the parent bit-for-bit for three
                magnetization values (53.79 / 55.78 / 25.00) and then failed to
                converge at all: 500 iterations in cycle 1, min 2.477e-5, ending
                at magtot 19.98 where the parent converged cycle 1 in 135
                iterations and completed 22.
        So chain 1 is re-run with `mixing_ndim = 16` ADDED TO THE REPLAY. This is
        a deliberate deviation from a byte-identical replay and is recorded as
        such: mixing parameters are convergence-PATH parameters -- they decide
        whether the fixed point is reached, never where it is -- which is the same
        reasoning round 4 used to pick each child's most robust deck. The replay
        energy is parity evidence and is never banked (A8.8). **Scoring rule: if
        the replay converges to a different magnetization than the banked parent,
        the chain is void and the child must not be banked**, because the density
        it inherits would then be the wrong branch's.

        Chain 2 is the last owed wave-4 child, `Co ref__2x1v__g1`, which failed
        cold in round 5: 500 iterations, no convergence, magtot 24.11 against the
        parent's 21.66. Its parent is banked and converged (`bfgs converged`, 10
        cycles), so it gets the same registered remedy that just worked for Fe.
        The replay is the honest cost here: the parent took 7h47m (~996 SU).

NOT built here, and needing something this round does not have:
  `Co s0_O__2x1v_mir`   0 ionic steps in 4 attempts (200/200/500/1500 iterations)
  `Co s0_OH__2x1v_off`  0 ionic steps in 5 attempts
        Neither has ever completed a single ionic step, so there is no geometry to
        resume from and no mixing rung left in the ladder. These are R1 candidates
        or need a new registered call (starting magnetization, diagonalization,
        or accepting a NOT_CONVERGED gap under A8.4 rung (iii)).

A8.8: every deck written here is a NEW filename. Group A writes none. The four
`.out` files this round overwrites are archived to `.out.attempt<N+1>` by the
deployment step, not here.
"""
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_s3_wave2 as W  # noqa: E402  (proven geometry/deck primitives)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S3 = os.path.join(ROOT, 'runs', 's3')
NDIM = '16'
MAXSTEP = '500'

# (metal, job, nk, why) -- decks already on disk, re-queued unchanged.
RERUN = [
    ('Ni', 's0_OOH__2x1v_mir', '.retry_ndim.in', 8, 'OOM a220'),
    ('Mn', 's0_OOH__2x1v_off__basin', '.retry_ndim.in', 8, 'OOM a220'),
]

# (metal, job, deck that produced the deepest attempt, beta that .out must echo)
RESUME = [
    ('Co', 's0_OOH__2x1v_off', '.in', '0.3000', 8),
    ('Ni', 's0_OOH__2x1v_off', '.in', '0.3000', 8),
]
RESUME_SUFFIX = '.resume.in'

# (dir, parent_deck, replay_out_name, child_deck, add_ndim_to_replay)
CHAINS = [
    ('runs/s3/Co', 's0_OOH__2x1v_mir.retry_ms.in', 's0_OOH__2x1v_mir.replay_nd.in',
     's0_OOH__2x1v_mir__g1.fromparent.in', True),
    ('runs/s3/Co', 'ref__2x1v.retry_ms.in', 'ref__2x1v.replay.in',
     'ref__2x1v__g1.fromparent.in', False),
]


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


def deepest_attempt(d, job):
    """(path, n_ionic_steps, beta) of the .out with the MOST completed ionic
    steps -- the fix for round 5's 'splice from the last attempt' defect."""
    cands = []
    for fn in sorted(os.listdir(d)):
        if not (fn == job + '.out' or fn.startswith(job + '.out.attempt')):
            continue
        p = os.path.join(d, fn)
        t = W.read(p)
        n = len(re.findall(r'^!\s+total energy', t, re.M))
        bm = re.search(r'mixing beta\s+=\s+([\d.]+)', t)
        cands.append((n, fn, p, bm.group(1) if bm else None))
    if not cands:
        W.die('%s/%s: no .out at all' % (d, job))
    cands.sort(key=lambda c: (-c[0], c[1]))
    return cands[0], cands


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

# ------------------------------------------------- GROUP A: verify, don't build
for metal, job, suf, nk, why in RERUN:
    src = os.path.join(S3, metal, job + suf)
    if not os.path.exists(src):
        W.die('group A deck missing: %s' % W.rel(src))
    txt = W.read(src)
    if '  mixing_ndim = 16' not in txt:
        W.die('group A deck lost mixing_ndim: %s' % W.rel(src))
    if re.search(r'^\s*(restart_mode|startingpot|startingwfc)\s*=', txt, re.M):
        W.die('group A deck carries a restart key: %s' % W.rel(src))
    wave_rows.append('s3/%s %s %s %d' % (metal, job, suf, nk))
    notes.append('A      s3/%s/%s%s  re-run unchanged  [%s]' % (metal, job, suf, why))

# ------------------------------------------- GROUP B: resume from the deepest
for metal, job, deck_suf, want_beta, nk in RESUME:
    d = os.path.join(S3, metal)
    src = os.path.join(d, job + deck_suf)
    src_txt = W.read(src)
    ref_deck = W.parse_input_deck(src)
    deck_rows = W.selftest_formatter(src_txt, src)

    best, allc = deepest_attempt(d, job)
    nsteps, fn, out_p, beta_echoed = best
    if nsteps < 1:
        W.die('%s/%s: deepest attempt has 0 ionic steps -- nothing to resume' % (metal, job))
    if beta_echoed != want_beta:
        W.die('%s echoes beta %s, expected %s (wrong source deck?)'
              % (fn, beta_echoed, want_beta))
    dbeta = re.search(r'^  mixing_beta = (.+)$', src_txt, re.M).group(1).strip()
    if abs(float(dbeta) - float(want_beta)) > 1e-9:
        W.die('%s has beta %s, %s echoes %s' % (deck_suf, dbeta, fn, want_beta))
    if re.search(r'^\s*mixing_ndim\s*=', src_txt, re.M):
        W.die('%s: already sets mixing_ndim' % W.rel(src))
    if not re.search(r"^  calculation = 'relax'$", src_txt, re.M):
        W.die('%s: not a relax' % W.rel(src))

    txt = src_txt.replace('&ELECTRONS\n', '&ELECTRONS\n  mixing_ndim = %s\n' % NDIM)
    if txt.count('mixing_ndim = %s' % NDIM) != 1:
        W.die('%s: ndim insertion not unique' % W.rel(src))
    old_ms = re.search(r'^\s*electron_maxstep\s*=\s*(\d+)\s*$', src_txt, re.M)
    if not old_ms:
        W.die('%s: no electron_maxstep' % W.rel(src))
    changed_ms = old_ms.group(1) != MAXSTEP
    if changed_ms:
        txt = re.sub(r'^(\s*electron_maxstep\s*=\s*)\d+\s*$', r'\g<1>' + MAXSTEP,
                     txt, count=1, flags=re.M)

    pos = last_positions(out_p)
    if not pos:
        W.die('%s: no ATOMIC_POSITIONS block' % fn)
    if len(pos) != len(deck_rows):
        W.die('%s: %d atoms != %d in deck' % (fn, len(pos), len(deck_rows)))
    if [p[0] for p in pos] != [r[0] for r in deck_rows]:
        W.die('%s: species order differs from deck' % fn)
    new_rows = [(sp, '%.8f' % x, '%.8f' % y, '%.8f' % z, r[4])
                for (sp, x, y, z), r in zip(pos, deck_rows)]
    txt = W.swap_positions(txt, src, new_rows)

    ch, ins = only_diff(src_txt, txt, W.rel(src))
    if ins != ['  mixing_ndim = %s' % NDIM]:
        W.die('%s: unexpected insertions %r' % (W.rel(src), ins))
    moved = 0
    for x, y in ch:
        if re.match(r'\s*electron_maxstep\s*=', x):
            if not changed_ms:
                W.die('%s: maxstep changed unexpectedly' % W.rel(src))
            continue
        px, py = x.split(), y.split()
        same_shape = (len(px) in (4, 7) and len(py) == len(px)
                      and px[0] == py[0] and px[4:] == py[4:])
        if not same_shape:
            W.die('%s: non-coordinate change %r -> %r' % (W.rel(src), x, y))
        moved += 1

    # namelist_sanity() is scf-only; these are relax decks, so do the applicable
    # subset by hand. only_diff above already proves nothing outside
    # {ndim, maxstep, coordinates} changed, so cell/species/kpts/mags are safe.
    nat = int(re.search(r'^\s*nat\s*=\s*(\d+)', txt, re.M).group(1))
    npos = len(W.parse_pos_lines(txt[W.pos_block_span(txt, src)[0]:
                                     W.pos_block_span(txt, src)[1]], src))
    if nat != npos:
        W.die('%s: nat=%d != %d position lines' % (W.rel(src), nat, npos))
    if W.FORBIDDEN_RESTART.search(txt):
        W.die('%s: restart/startingpot key emitted' % W.rel(src))
    if moved == 0:
        W.die('%s: splice moved no atoms -- geometry is identical, pointless' % W.rel(src))

    out = os.path.join(d, job + RESUME_SUFFIX)
    if os.path.exists(out):
        W.die('A8.8: %s already exists' % W.rel(out))
    W.write(out, txt)
    wave_rows.append('s3/%s %s %s %d' % (metal, job, RESUME_SUFFIX, nk))
    notes.append('B      s3/%s/%s%s  resume from %s (%d ionic steps, beta %s), '
                 'ndim %s, maxstep %s, %d/%d atoms moved'
                 % (metal, job, RESUME_SUFFIX, fn, nsteps, want_beta, NDIM,
                    MAXSTEP, moved, len(pos)))
    notes.append('         attempts seen: '
                 + ', '.join('%s=%d' % (c[1].split('.out')[-1] or 'out', c[0])
                             for c in allc))

# ------------------------------------------------------- GROUP C: A8.3 chains
for d, pdeck, rname, cname, add_ndim in CHAINS:
    dd = os.path.join(ROOT, d)
    ptxt = W.read(os.path.join(dd, pdeck))
    base = pdeck.split('.retry_ms.in')[0].split('.in')[0]
    pout = os.path.join(dd, base + '.out')
    pot = W.read(pout)
    if 'JOB DONE' not in pot or 'convergence NOT achieved' in pot:
        W.die('parent not cleanly converged: %s' % W.rel(pout))
    if not ('End of BFGS Geometry Optimization' in pot or 'bfgs converged' in pot):
        W.die('parent is not a converged relax: %s' % W.rel(pout))

    pprefix = get_prefix(ptxt, pdeck)
    rtxt = ptxt.replace("  prefix = '%s'\n" % pprefix,
                        "  prefix = '%s__replay'\n" % pprefix)
    want_ins = []
    if add_ndim:
        if re.search(r'^\s*mixing_ndim\s*=', ptxt, re.M):
            W.die('%s: parent already sets mixing_ndim' % pdeck)
        rtxt = rtxt.replace('&ELECTRONS\n', '&ELECTRONS\n  mixing_ndim = %s\n' % NDIM)
        want_ins = ['  mixing_ndim = %s' % NDIM]
    ch, ins = only_diff(ptxt, rtxt, pdeck)
    if ins != want_ins or len(ch) != 1 or 'prefix' not in ch[0][0]:
        W.die('replay diff wrong for %s: %r %r' % (pdeck, ch, ins))
    rp = os.path.join(dd, rname)
    if os.path.exists(rp):
        W.die('A8.8: %s already exists' % rname)
    W.write(rp, rtxt)

    cp = os.path.join(dd, cname)
    if os.path.exists(cp):
        # round 6 already built this child and it never ran -- reuse, do not rebuild
        ctxt = W.read(cp)
        if "startingpot = 'file'" not in ctxt:
            W.die('%s exists but has no startingpot' % cname)
        if os.path.exists(cp.replace('.in', '.out')):
            W.die('A8.8: %s already has an .out' % cname)
        reused = ' (reused from round 6, never ran)'
    else:
        gdeck = cname.replace('.fromparent.in', '.in')
        gtxt = W.read(os.path.join(dd, gdeck))
        if not re.search(r"^  calculation = 'scf'$", gtxt, re.M):
            W.die('%s is not an scf deck' % gdeck)
        gpre = get_prefix(gtxt, gdeck)
        ctxt = gtxt.replace("  prefix = '%s'\n" % gpre, "  prefix = '%s__fp'\n" % gpre)
        ctxt = ctxt.replace('&ELECTRONS\n', "&ELECTRONS\n  startingpot = 'file'\n")
        ch, ins = only_diff(gtxt, ctxt, gdeck)
        if len(ch) != 1 or 'prefix' not in ch[0][0] or ins != ["  startingpot = 'file'"]:
            W.die('child diff wrong for %s: %r %r' % (gdeck, ch, ins))
        W.write(cp, ctxt)
        reused = ''
    cprefix = get_prefix(ctxt, cname)

    nks, nk = pick_nk(pot, pout)
    chain_rows.append('%s %s %s__replay %s %s %d'
                      % (d, rname, pprefix, cname, cprefix, nk))
    notes.append('C      %s: %s -> %s  (k=%d nk=%d, replay ndim=%s)%s'
                 % (d, rname, cname, nks, nk, NDIM if add_ndim else 'unchanged', reused))

# ------------------------------------------------------------------- manifests
WAVE_HDR = """\
# S3 round 7 wave rows (2026-08-26), built by src/dft/build_s3_round7.py.
#
# Rows 1-2  GROUP A: the two rows node a220 OOM-killed in round 6, at MaxRSS
#           35.1 GB against a granted mem=237G. a220 carries no DRAIN and no NHC
#           record, so it is the a024/a088 shape rather than the a196 shape.
#           Decks are UNCHANGED and already carry their round-5 splices.
#           SUBMIT WITH EXCLUDE=a024,a088,a196,a220.
# Rows 3-4  GROUP B: resume from the DEEPEST attempt rather than the last one.
#           Round 5's builder spliced from `job.out` and never scanned
#           `job.out.attempt*`, so `Co s0_OOH__2x1v_off` had 14 converged ionic
#           steps sitting in attempt2 while four later rungs each restarted from
#           the original geometry and stalled in the first SCF. Both rows resume
#           from the deck that produced their deepest attempt -- the ORIGINAL
#           beta 0.3 in both cases -- plus mixing_ndim = 16 and the campaign
#           standard electron_maxstep = 500.
#
#           On row 3, note that attempt2 stopped while being held to
#           `new conv_thr = 4.10e-8` by the unset `upscale`, 24x tighter than its
#           registered 1e-6, having reached 3e-8. R1 remains the cleaner fix and
#           is still Frank's call; this row is what can be done without it.
#
# row: dir job suffix nk
# NP=128 NCONC=1
"""

CHAIN_HDR = """\
# S3 round 7 chains (2026-08-26), built by src/dft/build_s3_round7.py. Same row
# format and runner (anvil/44_chain.slurm) as m_round4.txt / m_round6.txt.
#
# Round 6 established both what this remedy does and how it fails:
#   Fe s0_OOH__1x1_off__basin  replay -0.049 meV, child +0.004 meV, magnetization
#         22.98/27.59 identical across banked / replay / child. A +7.4 meV branch
#         mismatch closed to 4 ueV. GATE-1 closed.
#   Co s0_OOH__2x1v_mir  CHAIN FAIL: replay non-convergent. The parent's own deck
#         matched it bit-for-bit for three magnetization values and then failed to
#         converge at all (500 iterations in cycle 1, min 2.477e-5, magtot 19.98;
#         the parent converged cycle 1 in 135 iterations and completed 22).
#
# Chain 1 therefore adds `mixing_ndim = 16` TO THE REPLAY. This is a deliberate
# deviation from a byte-identical replay: mixing parameters decide whether the
# fixed point is reached, never where it is, which is the same reasoning round 4
# used when picking each child's most robust deck. The replay energy is parity
# evidence and is never banked (A8.8).
#
# SCORING RULE for chain 1: if the replay converges at a different magnetization
# than the banked parent, the chain is VOID and the child must not be banked --
# the density it inherits would be the wrong branch's.
#
# Chain 2 is the last owed wave-4 child, Co ref__2x1v__g1, which failed cold in
# round 5 (500 iterations, no convergence, magtot 24.11 vs the parent's 21.66).
# Its parent is banked and converged, so it gets the remedy that just worked for
# Fe. The replay is the honest cost: that parent took 7h47m, about 996 SU.
#
# SUBMIT WITH EXCLUDE=a024,a088,a196,a220.
#
# row: dir replay_deck replay_prefix child_deck child_prefix nk
# NP=128 NCONC=1
"""

for hdr, rows, path in ((WAVE_HDR, wave_rows, 'runs/s3/m_s3_round7.txt'),
                        (CHAIN_HDR, chain_rows, 'runs/chains/m_round7.txt')):
    hits = [l for l in hdr.splitlines() if 'NP=' in l or 'NCONC=' in l]
    if hits != ['# NP=128 NCONC=1']:
        W.die('%s: directive must be the only line naming it: %r' % (path, hits))
    p = os.path.join(ROOT, path)
    with open(p, 'w', newline='\n', encoding='utf-8') as f:
        f.write(hdr + '\n'.join(rows) + '\n')
    print('wrote %s: %d rows' % (path, len(rows)))

print()
for n in notes:
    print(n)
