#!/usr/bin/env python
"""A8.3 density-retention chain, round 2 (2026-08-24).

One chain, found by the S6 analysis block's adversarial verify pass (docs/56):
the three basin __g1 children rode WAVE 1 and were never in the wave-2 GATE-1
census. Scored today: Co s0_OH__basin_g1 +0.02 meV AGREE, Cr s0_OOH__basin_g1
+0.00 meV AGREE, but **Ni s0_OH__basin_g1 = +177.10 meV ABOVE its parent
(M 7.12 vs 4.15)** -- a refused-candidate under docs/43:1589-1592, the same
cold-start electronic-branch signature the three discharged chains showed.
Registered remedy: second attempt from the parent's converged density.

Cross-directory variant of src/dft/build_retention_chains.py: the parent of
record is runs/probe/Ni_basin/s0_OH.out (the docs/54:205 energy-of-record row)
while the child deck lives in runs/s3/Ni/. Both chain decks are emitted into
the PARENT's directory (44_chain.slurm rows are dir-scoped); the refused first
attempt stays untouched at runs/s3/Ni/s0_OH__basin_g1.out.

Extra allowance vs the original builder: the S3-built child carries
max_seconds = 165000 which the tier_v2-era parent deck lacks -- the child-deck
asserts are against the CHILD's own text (prefix change + startingpot insert
only), exactly as before, so no new degrees of freedom.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# (parent_dir, parent_deck, child_dir, child_deck)
CHAINS = [
    ('runs/probe/Ni_basin', 's0_OH.in', 'runs/s3/Ni', 's0_OH__basin_g1.in'),
]

def get_prefix(txt, path):
    m = re.search(r"^  prefix = '([^']+)'$", txt, re.M)
    assert m, path
    return m.group(1)

def only_diff(a, b):
    import difflib
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

rows = []
for pd, pdeck, cd, cdeck in CHAINS:
    pdd, cdd = ROOT / pd, ROOT / cd
    ptxt = (pdd / pdeck).read_text()
    ctxt = (cdd / cdeck).read_text()
    pout = pdd / (pdeck[:-3] + '.out')
    pot = pout.read_text(errors='replace')
    assert 'JOB DONE' in pot and 'convergence NOT achieved' not in pot, pout
    assert ('End of BFGS Geometry Optimization' in pot) or ('convergence has been achieved' in pot), pout
    pprefix = get_prefix(ptxt, pdeck)
    cprefix = get_prefix(ctxt, cdeck)
    assert re.search(r"^  calculation = 'scf'$", ctxt, re.M), cdeck

    rtxt = ptxt.replace(f"  prefix = '{pprefix}'\n", f"  prefix = '{pprefix}__replay'\n")
    ch, ins = only_diff(ptxt, rtxt)
    assert not ins and len(ch) == 1 and 'prefix' in ch[0][0], (pdeck, ch, ins)
    rname = pdeck[:-3] + '.replay.in'
    assert not (pdd / (pdeck[:-3] + '.replay.out')).exists(), 'stale replay out'
    (pdd / rname).write_text(rtxt, newline='\n')

    ftxt = ctxt.replace(f"  prefix = '{cprefix}'\n", f"  prefix = '{cprefix}__fp'\n")
    ftxt = ftxt.replace('&ELECTRONS\n', "&ELECTRONS\n  startingpot = 'file'\n")
    assert ftxt.count("startingpot = 'file'") == 1
    ch, ins = only_diff(ctxt, ftxt)
    assert len(ch) == 1 and 'prefix' in ch[0][0] and ins == ["  startingpot = 'file'"], (cdeck, ch, ins)
    fname = cdeck[:-3] + '.fromparent.in'
    assert not (pdd / (cdeck[:-3] + '.fromparent.out')).exists(), 'stale fromparent out'
    (pdd / fname).write_text(ftxt, newline='\n')

    m = re.search(r'number of k points=\s*(\d+)', pot)
    assert m, pout
    nks = int(m.group(1))
    nk = 16 if nks >= 16 else 8
    assert 128 % nk == 0 and nk <= nks

    rows.append(f'{pd} {rname} {pprefix}__replay {fname} {cprefix}__fp {nk}')
    print(f'chain: {pd}: {rname} -> {fname}  (k={nks} nk={nk})')

out = ROOT / 'runs' / 'chains'
out.mkdir(exist_ok=True)
hdr = """# A8.3 density-retention chain, round 2 -- built 2026-08-24 by
# src/dft/build_retention_chain2.py (see its docstring). Same row format and
# runner (anvil/44_chain.slurm) as m_chains.txt. The Ni s0_OH basin __g1
# child (+177.10 meV above parent, found by the docs/56 verify pass) gets its
# registered A8.3 second attempt from the parent's converged density.
# row: dir replay_deck replay_prefix fromparent_deck fp_prefix nk
# NP=128 NCONC=1
"""
(out / 'm_chains2.txt').write_text(hdr + '\n'.join(rows) + '\n', newline='\n')
print(f'wrote runs/chains/m_chains2.txt: {len(rows)} rows')
