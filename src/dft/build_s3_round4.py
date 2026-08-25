#!/usr/bin/env python
"""S3 round 4 (2026-08-25) -- the R4 group of the docs/45 CORRECTION.

Round 3's failures were re-triaged by src/dft/scf_triage.py after `upscale`
(unset in every deck, QE default 100) was found to be tightening conv_thr toward
a 1e-8 floor during relax. The corrected classes are 1 SLOW / 4 STALLED /
2 BRANCH / 2 UNREG_THR. This builder emits ONLY the rows that need no entrant
ruling -- R1 (declare `upscale`) and R2 (electron_maxstep for the single SLOW
deck) are Frank's and are not built here.

Two chain shapes, both run by the existing anvil/44_chain.slurm (row format
`dir replay_deck replay_prefix child_deck child_prefix nk`: run the first deck
to convergence with scratch RETAINED, copy its .save under the child prefix,
run the child with startingpot='file'):

  A8.3 parent->child  -- the registered density-retention remedy for a refused
        __g1 child. Both remaining GATE-1 UNVERIFIED parents are banked and
        converged, so both children can finally take their second attempt from
        the parent's own density. This is the path that closes GATE-1
        UNVERIFIED to zero.

  STAGED SELF-SEED    -- A8.4 rung (i) for the STALLED rows. Rung (i) is
        "restart from density", but these decks died on their FIRST SCF and the
        runner deletes scratch, so there is no density to restart from. Step 1
        therefore MANUFACTURES one: the same geometry as a plain `scf` at a
        DELIBERATELY LOOSE conv_thr, which every one of these decks demonstrably
        reaches (their running minima are 1.1e-5 to 1.8e-5 Ry). Step 2 is the
        real relax reading that density with a FRESH Broyden history.

        The mechanism this attacks: all four STALLED rows have magnetization
        stable to <0.1 uB and a running minimum that improved less than 2x over
        their last 150 iterations -- a saturated mixing history, not a physics
        problem. Their converged siblings (Co s0_O__2x1v_off, Co s0_OOH__2x1v_mir,
        Co ref__2x1v) reach 1e-8 in the same cell at the same cutoffs, so the
        fixed point is reachable; these runs just cannot find it from a cold
        start.

DISCLOSED INFRASTRUCTURE VALUE (deliberately surfaced rather than buried, given
what this round was about): the seed step uses SEED_CONV_THR = 1.0d-4. It is a
density generator only -- the seed energy is parity evidence and is NEVER banked
(A8.8), exactly as the A8.3 replay energy is never banked. It sets no threshold
on any banked number. If Frank wants it registered rather than disclosed, it is
one constant at the top of this file.

A8.8: every deck written here is a NEW filename. No existing deck or .out is
touched; the failed round-3 .out files stay exactly where they are.
"""
import difflib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

SEED_CONV_THR = "1.0d-4"

# (dir, parent_deck, child_deck) -- parent .out must be banked AND converged.
#
# The child is the DECK OF RECORD for its last attempt (`.retry_ms`), NOT the
# wave-2 base deck. Both of these children have already failed three times and
# the A8.4 ladder escalated their mixing at every rung:
#
#   Co s0_O__1x1_off__g1     .in  beta 0.15 / 200  ->  .retry_bh  beta 0.075
#                                                  ->  .retry_ms  beta 0.075 / 500
#   Ni s0_OH__2x1v_off__g1   .in  beta 0.30 / 200  ->  .retry_bh  beta 0.15
#                                                  ->  .retry_ms  beta 0.15  / 500
#
# Seeding the BASE deck would hand the parent's converged density to the least
# robust of three already-failed configurations, and would make the retention
# test a two-variable one (density AND mixing changed at once). `mixing_beta`
# and `electron_maxstep` are convergence-PATH parameters: they decide whether
# the fixed point is reached, never where it is, so choosing the robust one
# costs nothing and cannot move a banked number. With this choice each child
# differs from its own last failed attempt in exactly one thing -- where it
# starts -- which is what makes a negative result here interpretable.
#
# This also makes rows 1-2 consistent with rows 3-5, which already seed the
# `.retry_ms` deck of record. base_of() strips `.retry_ms`, so the emitted
# filenames and the manifest rows are unchanged either way.
A83_CHAINS = [
    ('runs/s3/Co', 's0_O__1x1_off.retry_bh.in', 's0_O__1x1_off__g1.retry_ms.in'),
    ('runs/s3/Ni', 's0_OH__2x1v_off.in', 's0_OH__2x1v_off__g1.retry_ms.in'),
]

# (dir, deck) -- the STALLED/BRANCH rows with no parent density available.
SELF_SEED = [
    ('runs/s3/Co', 's0_OH__2x1v_mir.retry_ms.in'),
    ('runs/s3/Co', 's0_OH__2x1v_off.retry_ms.in'),
    ('runs/s3/Co', 's0_OOH__2x1v_off.retry_ms.in'),
]

# NOT self-seedable. Ni s0_OOH__2x1v_off (BRANCH, dM 2.41 uB) never reached even
# 1e-3 in 500 iterations -- its running minimum was 2.55e-3 -- so no seed step
# loose enough to converge would hand over a density worth having, and a seed
# that fails aborts the whole chain task at 44_chain.slurm's replay check.
# Its real seed is its own mirror arm: Ni s0_OOH__2x1v_mir is the SAME system
# (nelec 373.00, nat 39, same 2x1v cell; the irreducible k count differs, 9 vs
# 10, purely from adsorbate symmetry, which does not affect a real-space charge
# density). That sibling is an R1 row. So this deck is GATED ON R1, and is the
# A8.4 rung-(iii) NOT_CONVERGED gap candidate if the cross-arm seed also fails.
GATED_ON_R1 = [('runs/s3/Ni', 's0_OOH__2x1v_off.retry_ms.in',
                'seed from Ni s0_OOH__2x1v_mir once R1 converges it')]


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
            raise AssertionError(f'unexpected delete: {la[i1:i2]}')
    return ch, ins


def pick_nk(out_text, path):
    m = re.search(r'number of k points=\s*(\d+)', out_text)
    assert m, f'no k-point count in {path}'
    nks = int(m.group(1))
    nk = 16 if nks >= 16 else 8
    assert 128 % nk == 0 and nk <= nks, (path, nks, nk)
    return nks, nk


def base_of(deck):
    """strip the round suffix: s0_X.retry_ms.in -> s0_X"""
    for suf in ('.retry_ms.in', '.retry_bh.in', '.in'):
        if deck.endswith(suf):
            return deck[:-len(suf)]
    raise AssertionError(deck)


rows, notes = [], []

# ---------------------------------------------------------------- A8.3 chains
for d, pdeck, cdeck in A83_CHAINS:
    dd = ROOT / d
    ptxt = (dd / pdeck).read_text()
    ctxt = (dd / cdeck).read_text()
    pout = dd / (base_of(pdeck) + '.out')
    pot = pout.read_text(errors='replace')

    assert 'JOB DONE' in pot and 'convergence NOT achieved' not in pot, pout
    assert ('End of BFGS Geometry Optimization' in pot
            or 'bfgs converged' in pot), pout
    assert re.search(r"^  calculation = 'scf'$", ctxt, re.M), cdeck

    pprefix = get_prefix(ptxt, pdeck)
    cprefix = get_prefix(ctxt, cdeck)

    # replay deck: prefix change ONLY
    rtxt = ptxt.replace(f"  prefix = '{pprefix}'\n", f"  prefix = '{pprefix}__replay'\n")
    ch, ins = only_diff(ptxt, rtxt)
    assert not ins and len(ch) == 1 and 'prefix' in ch[0][0], (pdeck, ch, ins)
    rname = base_of(pdeck) + '.replay.in'
    assert not (dd / rname).exists(), f'A8.8: {rname} already exists'
    (dd / rname).write_text(rtxt, newline='\n')

    # child deck: prefix change + startingpot insertion ONLY
    ftxt = ctxt.replace(f"  prefix = '{cprefix}'\n", f"  prefix = '{cprefix}__fp'\n")
    ftxt = ftxt.replace('&ELECTRONS\n', "&ELECTRONS\n  startingpot = 'file'\n")
    assert ftxt.count("startingpot = 'file'") == 1
    ch, ins = only_diff(ctxt, ftxt)
    assert len(ch) == 1 and 'prefix' in ch[0][0] and ins == ["  startingpot = 'file'"], \
        (cdeck, ch, ins)
    fname = base_of(cdeck) + '.fromparent.in'
    assert not (dd / fname).exists(), f'A8.8: {fname} already exists'
    (dd / fname).write_text(ftxt, newline='\n')

    nks, nk = pick_nk(pot, pout)
    mix = ' '.join(x.strip() for x in re.findall(
        r'^  (?:mixing_beta|electron_maxstep) = .*$', ctxt, re.M))
    rows.append(f'{d} {rname} {pprefix}__replay {fname} {cprefix}__fp {nk}')
    notes.append(f'A8.3   {d}: {rname} -> {fname}  (k={nks} nk={nk})\n'
                 f'         child source {cdeck}  [{mix}]')

# ----------------------------------------------------------- staged self-seed
for d, deck in SELF_SEED:
    dd = ROOT / d
    txt = (dd / deck).read_text()
    prefix = get_prefix(txt, deck)
    base = base_of(deck)
    fout = dd / (base + '.out')
    fot = fout.read_text(errors='replace')
    # only rows that actually failed belong here
    assert 'convergence NOT achieved' in fot, f'{fout} did not fail -- not a rung-(i) row'

    # The seed MUST be reachable or the chain aborts at 44_chain.slurm's replay
    # convergence check and the whole task is wasted. Ni s0_OOH__2x1v_off was
    # caught by exactly this: minimum 2.55e-3, never within three decades of
    # the seed threshold. Verify against the deck's own observed history.
    accs = [float(x) for x in re.findall(
        r"estimated scf accuracy\s+<\s+([0-9.Ee+-]+)\s+Ry",
        fot.split('Self-consistent Calculation')[-1])]
    seed_thr = float(SEED_CONV_THR.replace('d', 'e'))
    hit = next((i + 1 for i, v in enumerate(accs) if v < seed_thr), None)
    assert hit is not None, (
        f'{fout}: never reached the seed threshold {SEED_CONV_THR} '
        f'(best {min(accs):.2e}) -- a seed step would not converge and would '
        f'abort the chain. This row needs a different density source.')
    print(f'       seed feasible: reaches {SEED_CONV_THR} at iteration {hit}')

    # seed deck: prefix, calculation -> scf, conv_thr -> loose. Nothing else.
    stxt = txt.replace(f"  prefix = '{prefix}'\n", f"  prefix = '{prefix}__seed'\n")
    stxt = re.sub(r"^  calculation = 'relax'$", "  calculation = 'scf'", stxt, flags=re.M)
    stxt = re.sub(r"^  conv_thr = .*$", f"  conv_thr = {SEED_CONV_THR}", stxt, flags=re.M)
    ch, ins = only_diff(txt, stxt)
    assert not ins, (deck, ins)
    keys = sorted(k.strip().split(' =')[0] for k, _ in ch)
    assert keys == ['calculation', 'conv_thr', 'prefix'], (deck, keys)
    sname = base + '.seed.in'
    assert not (dd / sname).exists(), f'A8.8: {sname} already exists'
    (dd / sname).write_text(stxt, newline='\n')

    # child deck: prefix + startingpot ONLY. Same relax, same conv_thr, same
    # electron_maxstep -- the ONLY thing that changes is where it starts.
    ftxt = txt.replace(f"  prefix = '{prefix}'\n", f"  prefix = '{prefix}__fs'\n")
    ftxt = ftxt.replace('&ELECTRONS\n', "&ELECTRONS\n  startingpot = 'file'\n")
    assert ftxt.count("startingpot = 'file'") == 1
    ch, ins = only_diff(txt, ftxt)
    assert len(ch) == 1 and 'prefix' in ch[0][0] and ins == ["  startingpot = 'file'"], \
        (deck, ch, ins)
    fname = base + '.fromseed.in'
    assert not (dd / fname).exists(), f'A8.8: {fname} already exists'
    (dd / fname).write_text(ftxt, newline='\n')

    nks, nk = pick_nk(fot, fout)
    rows.append(f'{d} {sname} {prefix}__seed {fname} {prefix}__fs {nk}')
    notes.append(f'rung-i {d}: {sname} -> {fname}  (k={nks} nk={nk})')

for n in notes:
    print(n)

hdr = f"""# S3 round 4 -- the R4 group of the docs/45 CORRECTION (2026-08-25), built by
# src/dft/build_s3_round4.py. Same row format and runner (anvil/44_chain.slurm)
# as m_chains.txt / m_chains2.txt.
#
# Rows 1-2  A8.3 parent->child density retention for the two remaining GATE-1
#           UNVERIFIED children. Both parents are banked AND converged, so both
#           children finally get their registered second attempt. These two rows
#           are the path that closes GATE-1 UNVERIFIED to zero.
#           The child deck seeded is each child's OWN LAST FAILED ATTEMPT
#           (`.retry_ms`, the deck of record after three A8.4 rungs), not the
#           wave-2 base deck, so the only thing that differs from the run it is
#           remedying is where the density comes from. mixing_beta and
#           electron_maxstep cannot move a converged energy, only whether one
#           is reached.
# Rows 3-5  A8.4 rung (i) as a STAGED SELF-SEED: step 1 manufactures a density
#           (same geometry, plain scf, conv_thr = {SEED_CONV_THR} -- disclosed
#           infrastructure, energy NEVER banked, exactly like an A8.3 replay),
#           step 2 is the real relax reading it with a fresh Broyden history.
#           These decks died on their FIRST SCF with magnetization stable and a
#           running minimum that had stopped improving -- a saturated mixing
#           history, not a physics problem. Converged siblings reach 1e-8 in the
#           same cell, so the fixed point is reachable.
#
# NOT built here (Frank's registered-parameter rulings, docs/45 CORRECTION):
#   R1 `upscale` -- Ni s0_OOH__2x1v_mir, Mn s0_OOH__2x1v_off__basin
#   R2 electron_maxstep 500->1500 -- Co s0_O__2x1v_mir (the only SLOW row)
#
# GATED ON R1, deliberately not built: Ni s0_OOH__2x1v_off. It never reached
# 1e-3 (best 2.55e-3), so no self-seed converges; its seed is its own mirror
# arm Ni s0_OOH__2x1v_mir (same nelec 373.00 / nat 39 / cell), which is itself
# an R1 row. rung-(iii) NOT_CONVERGED gap candidate if that seed also fails.
#
# row: dir seed_or_replay_deck its_prefix child_deck child_prefix nk
# NP=128 NCONC=1
"""
out = ROOT / 'runs' / 'chains'
out.mkdir(exist_ok=True)
(out / 'm_round4.txt').write_text(hdr + '\n'.join(rows) + '\n', newline='\n')
print(f'\nwrote runs/chains/m_round4.txt: {len(rows)} rows')
