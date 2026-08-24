#!/usr/bin/env python
"""A8.3 density-retention chains (2026-08-24).

The registered A8.3 mechanic (docs/43:1589-1592): a __g1 child landing > 1 meV
ABOVE its parent is refused and re-run FROM THE PARENT'S CONVERGED DENSITY; a
second above-parent result -> MULTISTABLE, neither number banked. No parent
density survives on Anvil (the runner deletes scratch), so each re-run is a
two-step chain in ONE Slurm task (anvil/44_chain.slurm):

  step 1  <parent>.replay.in  -- the parent's converged deck, prefix suffixed
          '__replay', run to convergence with scratch RETAINED. The replay
          energy is evidence (an A8.5-style parity datum vs the banked parent
          energy), NEVER banked as the state's energy (A8.8).
  step 2  <child>.fromparent.in -- the child deck, prefix suffixed '__fp',
          startingpot = 'file', reading the replay's .save copied under the
          child prefix. Its energy is the A8.3 second attempt.

Chains registered here:
  1. Ni s0_O__1x1_off__g1 (wave-2 REFUSED, +85.10 meV above parent; parent of
     record = the beta-0.15 .retry_bh deck)
  2. Cr_lit3 oosh__1x1_off_magp__g1 (+8.29 meV, docs/54:324 owed row)
  3. Cr_lit3 s0_OOH__1x1_yaw90_magm__g1 (+47.77 meV, docs/54:324 owed row)
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

CHAINS = [
    # (dir, parent_deck, child_deck)
    ('runs/s3/Ni', 's0_O__1x1_off.retry_bh.in', 's0_O__1x1_off__g1.in'),
    ('runs/probe/Cr_lit3', 'oosh__1x1_off_magp.in', 'oosh__1x1_off_magp__g1.in'),
    ('runs/probe/Cr_lit3', 's0_OOH__1x1_yaw90_magm.in', 's0_OOH__1x1_yaw90_magm__g1.in'),
]

def get_prefix(txt, path):
    m = re.search(r"^  prefix = '([^']+)'$", txt, re.M)
    assert m, path
    return m.group(1)

def only_diff(a, b, allowed_missing=0):
    """lines in a vs b that differ; returns (changed_pairs, inserted_lines)."""
    la, lb = a.splitlines(), b.splitlines()
    import difflib
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

rows = []
for d, pdeck, cdeck in CHAINS:
    dd = ROOT / d
    ptxt = (dd / pdeck).read_text()
    ctxt = (dd / cdeck).read_text()
    pout = dd / (pdeck.replace('.retry_bh.in', '.out').replace('.in', '.out'))
    pot = pout.read_text(errors='replace')
    # parent must be the converged run of THIS deck
    assert 'JOB DONE' in pot and 'convergence NOT achieved' not in pot, pout
    assert ('End of BFGS Geometry Optimization' in pot) or ('convergence has been achieved' in pot), pout
    pprefix = get_prefix(ptxt, pdeck)
    cprefix = get_prefix(ctxt, cdeck)
    assert re.search(r"^  calculation = 'scf'$", ctxt, re.M), cdeck

    # replay deck: prefix change ONLY
    rtxt = ptxt.replace(f"  prefix = '{pprefix}'\n", f"  prefix = '{pprefix}__replay'\n")
    ch, ins = only_diff(ptxt, rtxt)
    assert not ins and len(ch) == 1 and 'prefix' in ch[0][0], (pdeck, ch, ins)
    rname = pdeck.replace('.retry_bh.in', '.replay.in').replace('.in', '.replay.in') \
            if pdeck.endswith('.retry_bh.in') else pdeck[:-3] + '.replay.in'
    rname = (pdeck[:-len('.retry_bh.in')] + '.replay.in') if pdeck.endswith('.retry_bh.in') else pdeck[:-3] + '.replay.in'
    (dd / rname).write_text(rtxt, newline='\n')

    # fromparent child deck: prefix change + startingpot insertion ONLY
    ftxt = ctxt.replace(f"  prefix = '{cprefix}'\n", f"  prefix = '{cprefix}__fp'\n")
    ftxt = ftxt.replace('&ELECTRONS\n', "&ELECTRONS\n  startingpot = 'file'\n")
    assert ftxt.count("startingpot = 'file'") == 1
    ch, ins = only_diff(ctxt, ftxt)
    assert len(ch) == 1 and 'prefix' in ch[0][0] and ins == ["  startingpot = 'file'"], (cdeck, ch, ins)
    fname = cdeck[:-3] + '.fromparent.in'
    (dd / fname).write_text(ftxt, newline='\n')

    # nk from the parent's banked .out irreducible k count
    m = re.search(r'number of k points=\s*(\d+)', pot)
    assert m, pout
    nks = int(m.group(1))
    nk = 16 if nks >= 16 else 8
    assert 128 % nk == 0 and nk <= nks

    rows.append(f'{d} {rname} {pprefix}__replay {fname} {cprefix}__fp {nk}')
    print(f'chain: {d}: {rname} -> {fname}  (k={nks} nk={nk})')

out = ROOT / 'runs' / 'chains'
out.mkdir(exist_ok=True)
hdr = """# A8.3 density-retention chains -- built 2026-08-24 by
# src/dft/build_retention_chains.py (see its docstring). One row = one Slurm
# task in anvil/44_chain.slurm: replay parent (scratch retained) -> copy .save
# under the child __fp prefix -> child SCF with startingpot='file'.
# Replay energies are parity evidence only, never banked (A8.8). The child
# __fp energy is the A8.3 second attempt: still >1 meV above the banked
# parent -> the pair is MULTISTABLE, neither banked.
# row: dir replay_deck replay_prefix fromparent_deck fp_prefix nk
# NP=128 NCONC=1
"""
(out / 'm_chains.txt').write_text(hdr + '\n'.join(rows) + '\n', newline='\n')
print(f'wrote runs/chains/m_chains.txt: {len(rows)} rows')
