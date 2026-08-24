#!/usr/bin/env python
"""S3 wave-1 retry builder (2026-08-24).

Two retry classes, one manifest (runs/s3/m_s3_retry1.txt):

1. OOM-11: node a024 killed 11 of the 12 tasks it received in array 20097688
   (11/12 vs 0/43 on every other node -- infrastructure, not physics). Decks
   re-run UNMODIFIED; submission carries SBATCH_EXCLUDE=a024. Rows keep the
   original .in suffix.

2. BH-7: the 7 Co/Ni SCF non-convergences on healthy nodes (a033/a035) --
   A8.4 error class 5, ladder = A6.5 unchanged. Rung (i) restart-from-
   converged-neighbour-density is UNAVAILABLE: 42_s3_wave1.slurm rm -rf's the
   scratch after every task, so no converged density survives on Anvil.
   Escalation to rung (ii): mixing_beta halved 0.3 -> 0.15, nothing else
   changed (asserted). Emitted as <job>.retry_bh.in beside the registered
   deck; the failed attempt is preserved as <job>.out.attempt1.

Failure rates (A8.4 reported quantity) are computed at analysis, not here.
"""
import re, pathlib, hashlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
S3 = ROOT / 'runs' / 's3'

OOM = [  # (dir, job, suffix, nk) -- exactly the 11 a024 kills of 20097688
    ('s3/Co', 'ref__2x1v', '.in', 16),
    ('s3/Co', 's0_OH__2x1v_off', '.in', 8),
    ('s3/Co', 's0_OOH__2x1v_off', '.in', 8),
    ('s3/Ni', 'ref__2x1v', '.in', 16),
    ('s3/Ni', 's0_O__2x1v_mir', '.in', 8),
    ('s3/Ni', 's0_OOH__2x1v_off', '.in', 8),
    ('s3/Ti', 's0_O__2x1v_mir', '.in', 8),
    ('s3/Ti', 's0_O__2x1v_off', '.in', 8),
    ('s3/Ti', 's0_OOH__2x1v_mir', '.in', 8),
    ('s3/Ti', 's0_OOH__2x1v_off', '.in', 8),
    ('s3/Mn', 's0_OH__1x1_k8', '.in', 16),
]
BH = [  # the 7 healthy-node SCF non-convergences (all Co/Ni)
    ('s3/Co', 's0_O__1x1_off', 16),
    ('s3/Co', 's0_OH__1x1_off', 16),
    ('s3/Co', 's0_O__2x1v_mir', 8),
    ('s3/Co', 's0_OH__2x1v_mir', 8),
    ('s3/Co', 's0_OOH__2x1v_mir', 8),
    ('s3/Ni', 's0_O__1x1_off', 16),
    ('s3/Ni', 's0_OOH__2x1v_mir', 8),
]

rows = []
for d, job, suf, nk in OOM:
    p = ROOT / 'runs' / d.split('/', 1)[1] if False else S3 / d.split('/')[1] / f'{job}{suf}'
    assert p.is_file(), p
    rows.append(f'{d} {job} {suf} {nk}')

for d, job, nk in BH:
    src = S3 / d.split('/')[1] / f'{job}.in'
    txt = src.read_text()
    assert txt.count('  mixing_beta = 0.3\n') == 1, src
    new = txt.replace('  mixing_beta = 0.3\n', '  mixing_beta = 0.15\n')
    # everything else byte-identical
    a = [l for l in txt.splitlines() if 'mixing_beta' not in l]
    b = [l for l in new.splitlines() if 'mixing_beta' not in l]
    assert a == b, src
    dst = S3 / d.split('/')[1] / f'{job}.retry_bh.in'
    dst.write_text(new, newline='\n')
    rows.append(f'{d} {job} .retry_bh.in {nk}')

man = S3 / 'm_s3_retry1.txt'
hdr = f"""# S3 wave-1 RETRY manifest -- built 2026-08-24 by src/dft/build_s3_retries.py
# Parent wave: arrays 20097663 (canary, 3/3 converged) + 20097688 (52 tasks).
# Outcome of parent wave: 37/55 converged clean; 11 OOM (ALL on node a024 --
#   11/12 kill rate there vs 0/43 everywhere else: sick node, decks unmodified,
#   submit with SBATCH_EXCLUDE=a024); 7 SCF non-convergences on healthy nodes
#   (5x Co, 2x Ni -- the A8.4 error-class-5 population, as the amendment
#   predicted for the magnetically frustrated states).
# A8.4/A6.5 ladder: rung (i) neighbour-density restart UNAVAILABLE (the runner
#   rm -rf's scratch post-task; no converged density survives) -> recorded,
#   escalate to rung (ii) mixing_beta 0.3 -> 0.15 (.retry_bh.in decks, only
#   the beta line differs -- asserted at build). If a .retry_bh row fails
#   again, rung (iii): NOT_CONVERGED, plotted as a gap, never interpolated.
# Failed attempts preserved as <job>.out.attempt1 beside each deck (A8.8:
#   nothing banked is replaced; none of these produced a bankable number).
# Launch shape unchanged: 128 ranks, -N 1, 48 h, -nk per row, PARITY_PASS gate.
# NP=128 NCONC=1
"""
man.write_text(hdr + '\n'.join(rows) + '\n', newline='\n')
print(f'wrote {man.name}: {len(rows)} rows ({len(OOM)} oom + {len(BH)} bh)')
for r in rows: print('  ', r)

# --- round 2 (2026-08-24, post-retry-1 sweep) --------------------------------
# The 4 a024-OOM decks whose FIRST real attempt (beta 0.3, healthy nodes,
# array 20101963) hit electron_maxstep: fresh A8.4 class-5 members -> rung (ii).
import sys
if len(sys.argv) > 1 and sys.argv[1] == 'round2':
    R2 = [
        ('s3/Co', 'ref__2x1v', 16),
        ('s3/Co', 's0_OH__2x1v_off', 8),
        ('s3/Co', 's0_OOH__2x1v_off', 8),
        ('s3/Ni', 's0_OOH__2x1v_off', 8),
    ]
    rows2 = []
    for d, job, nk in R2:
        src = S3 / d.split('/')[1] / f'{job}.in'
        txt = src.read_text()
        assert txt.count('  mixing_beta = 0.3\n') == 1, src
        new = txt.replace('  mixing_beta = 0.3\n', '  mixing_beta = 0.15\n')
        a = [l for l in txt.splitlines() if 'mixing_beta' not in l]
        b = [l for l in new.splitlines() if 'mixing_beta' not in l]
        assert a == b, src
        (S3 / d.split('/')[1] / f'{job}.retry_bh.in').write_text(new, newline='\n')
        rows2.append(f'{d} {job} .retry_bh.in {nk}')
    m2 = S3 / 'm_s3_retry2.txt'
    hdr2 = """# S3 wave-1 RETRY-2 manifest -- 2026-08-24, build_s3_retries.py round2.
# The 4 a024-OOM decks whose first real SCF attempt (beta 0.3, healthy nodes,
# array 20101963) hit electron_maxstep -> fresh A8.4 class-5 -> rung (ii)
# beta 0.15 (rung (i) remains unavailable). Prior attempts preserved as
# .out.attempt1 (a024 kill) and .out.attempt2 (beta-0.3 non-convergence).
# A .retry_bh failure here -> rung (iii) NOT_CONVERGED gap.
# The 5 rung-(ii) failures of retry-1 are ALREADY at rung (iii): Co
# s0_OH__1x1_off, Co s0_O/s0_OH/s0_OOH__2x1v_mir, Ni s0_OOH__2x1v_mir --
# NOT_CONVERGED, plotted as gaps, no further compute under the ladder.
# NP=128 NCONC=1
"""
    m2.write_text(hdr2 + '\n'.join(rows2) + '\n', newline='\n')
    print(f'wrote {m2.name}: {len(rows2)} rows')
