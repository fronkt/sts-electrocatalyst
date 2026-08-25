#!/usr/bin/env python3
"""S3 round-3 builder (2026-08-24): the entrant-ruled rescue + drift re-relax round.

Two deck families, both single-purpose diffs from decks already on disk:

1. `.retry_ms.in` (11): the 9 wave-1 rung-(iii) gaps + the 2 rung-(iii) __g1
   children, rebuilt from each deck's LAST-ATTEMPTED configuration
   (`.retry_bh.in`, beta already halved) with exactly ONE token changed:
   electron_maxstep 200 -> 500. This is the docs/45:122-126 registered
   suggestion ("a fresh run at beta 0.15 with electron_maxstep raised") made
   real by an entrant dated line (docs/55 decision sheet, ruling 2).
   NOT a ladder rung: A8.4's ladder is exhausted for these decks; this is a
   registered-recipe parameter change, so the results are a new attempt class.

2. `__basin.in` (2): the docs/52 C9 s5-strict arm for the two below-parent
   GATE-1 drift rows (Fe s0_OOH__1x1_off -384.30 meV, Mn s0_OOH__2x1v_off
   -20.62 meV): re-relax IN the deeper electronic state. Deck = the row's
   __g1 child (whose cold start at the parent's final geometry provably
   lands in the deeper state) with calculation 'scf' -> 'relax' and a new
   prefix. By construction the deck differs from the ORIGINAL parent relax
   deck in exactly {prefix, starting coordinates} -- same recipe, warm
   geometry, and its first SCF reproduces the child's deeper state.

Asserts are the evidence: every deck's diff against its source is checked
line-by-line; the build is deterministic (run twice -> byte-identical).
"""
import difflib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S3 = ROOT / 'runs' / 's3'

# (dir, job, nk) -- nk copied from the rows' original manifest entries
RETRY_MS = [
    ('Co', 'ref__2x1v', 16),
    ('Co', 's0_OH__1x1_off', 16),
    ('Co', 's0_O__2x1v_mir', 8),
    ('Co', 's0_OH__2x1v_mir', 8),
    ('Co', 's0_OOH__2x1v_mir', 8),
    ('Co', 's0_OH__2x1v_off', 8),
    ('Co', 's0_OOH__2x1v_off', 8),
    ('Ni', 's0_OOH__2x1v_mir', 8),
    ('Ni', 's0_OOH__2x1v_off', 8),
    ('Co', 's0_O__1x1_off__g1', 16),
    ('Ni', 's0_OH__2x1v_off__g1', 8),
]

BASIN = [
    ('Fe', 's0_OOH__1x1_off', 16),
    ('Mn', 's0_OOH__2x1v_off', 8),
]

MAXSTEP_OLD = '  electron_maxstep = 200\n'
MAXSTEP_NEW = '  electron_maxstep = 500\n'


def changed_lines(a, b):
    """Return (removed, added) line lists between two texts."""
    rem, add = [], []
    for line in difflib.unified_diff(a.splitlines(True), b.splitlines(True), n=0):
        if line.startswith('---') or line.startswith('+++'):
            continue
        if line.startswith('-'):
            rem.append(line[1:])
        elif line.startswith('+'):
            add.append(line[1:])
    return rem, add


def build_retry_ms():
    out = {}
    for d, job, nk in RETRY_MS:
        src = S3 / d / f'{job}.retry_bh.in'
        dst = S3 / d / f'{job}.retry_ms.in'
        stale = S3 / d / f'{job}.retry_ms.out'
        assert src.is_file(), f'missing source {src}'
        assert not stale.exists(), f'stale out {stale}'
        txt = src.read_text()
        assert txt.count(MAXSTEP_OLD) == 1, f'{src}: maxstep line count != 1'
        new = txt.replace(MAXSTEP_OLD, MAXSTEP_NEW)
        rem, add = changed_lines(txt, new)
        assert rem == [MAXSTEP_OLD] and add == [MAXSTEP_NEW], \
            f'{src}: diff is not exactly the maxstep line'
        out[dst] = new
    return out


def is_position_line(line):
    t = line.split()
    return len(t) in (4, 7) and t[0].isalpha() and len(t[0]) <= 2


def build_basin():
    out = {}
    for d, job, nk in BASIN:
        g1 = S3 / d / f'{job}__g1.in'
        parent = S3 / d / f'{job}.in'
        dst = S3 / d / f'{job}__basin.in'
        stale = S3 / d / f'{job}__basin.out'
        assert g1.is_file() and parent.is_file(), f'missing {g1} or {parent}'
        assert not stale.exists(), f'stale out {stale}'
        txt = g1.read_text()
        old_calc = "  calculation = 'scf'\n"
        new_calc = "  calculation = 'relax'\n"
        old_pfx = f"  prefix = '{job}__g1'\n"
        new_pfx = f"  prefix = '{job}__basin'\n"
        assert txt.count(old_calc) == 1, f'{g1}: calculation line count != 1'
        assert txt.count(old_pfx) == 1, f'{g1}: prefix line count != 1'
        new = txt.replace(old_calc, new_calc).replace(old_pfx, new_pfx)
        rem, add = changed_lines(txt, new)
        assert sorted(rem) == sorted([old_calc, old_pfx]), f'{g1}: extra removals {rem}'
        assert sorted(add) == sorted([new_calc, new_pfx]), f'{g1}: extra additions {add}'
        # vs the ORIGINAL parent relax deck: exactly prefix + coordinates
        prem, padd = changed_lines(parent.read_text(), new)
        non_pos_rem = [l for l in prem if not is_position_line(l)]
        non_pos_add = [l for l in padd if not is_position_line(l)]
        assert non_pos_rem == [f"  prefix = '{job}'\n"], \
            f'{parent}: non-coordinate removals beyond prefix: {non_pos_rem}'
        assert non_pos_add == [new_pfx], \
            f'{parent}: non-coordinate additions beyond prefix: {non_pos_add}'
        n_pos = sum(1 for l in prem if is_position_line(l))
        assert n_pos > 0, f'{parent}: no coordinate changes -- parent already at finals?'
        out[dst] = new
    return out


def build_manifest():
    rows = ['# S3 round 3 (2026-08-24): 11 maxstep-500 rescue decks (docs/55 ruling 2)\n',
            '# + 2 __basin drift re-relaxations (docs/55 ruling 1, docs/52 C9 s5-strict)\n']
    for d, job, nk in RETRY_MS:
        rows.append(f's3/{d} {job} .retry_ms.in {nk}\n')
    for d, job, nk in BASIN:
        rows.append(f's3/{d} {job}__basin .in {nk}\n')
    return {S3 / 'm_s3_round3.txt': ''.join(rows)}


def build_all():
    files = {}
    files.update(build_retry_ms())
    files.update(build_basin())
    files.update(build_manifest())
    return files


def main():
    a = build_all()
    b = build_all()
    assert set(a) == set(b) and all(a[k] == b[k] for k in a), 'non-deterministic build'
    for path, txt in sorted(a.items()):
        path.write_text(txt, newline='\n')
        print(f'wrote {path.relative_to(ROOT)} ({len(txt)} bytes)')
    print(f'OK: {len(a)-1} decks + manifest, all asserts passed')


if __name__ == '__main__':
    sys.exit(main())
