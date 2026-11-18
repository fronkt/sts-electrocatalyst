#!/usr/bin/env python3
"""Amendment 23 staging checks.

  python3 a23_check.py pos OUT.out BLOCK IN.in [IN.in ...]
      every input's ATOMIC_POSITIONS equal block BLOCK (1-based; 0 = last) of OUT.out, within 1e-6 A
  python3 a23_check.py xml OUT.out BLOCK data-file-schema.xml
      the geometry stored with a saved density equals that block, within 1e-6 A
Exits 1 on a mismatch. Stdlib only.
"""
import re
import sys
import xml.etree.ElementTree as ET

BOHR = 0.529177210903


def block(out, k, nat):
    t = open(out, errors="replace").read()
    s = [m.end() for m in re.finditer(r"ATOMIC_POSITIONS \(angstrom\)\n", t)]
    if not s:
        raise SystemExit(f"{out}: no ATOMIC_POSITIONS block")
    i = s[-1] if k == 0 else s[k - 1]
    return [[float(x) for x in r.split()[1:4]] for r in t[i:].split("\n")[:nat]], len(s)


def inp_pos(path):
    t = open(path).read()
    nat = int(re.search(r"nat = (\d+)", t).group(1))
    rows = t.split("ATOMIC_POSITIONS angstrom\n", 1)[1].split("\n")[:nat]
    return [[float(v) for v in r.split()[1:4]] for r in rows]


def xml_pos(path):
    st = ET.parse(path).getroot().find("output/atomic_structure")
    return [[float(v) * BOHR for v in a.text.split()] for a in st.find("atomic_positions")]


def maxdx(a, b):
    assert len(a) == len(b), (len(a), len(b))
    return max(abs(x - y) for p, q in zip(a, b) for x, y in zip(p, q))


def main():
    mode, out, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
    ok = True
    for f in sys.argv[4:]:
        p = inp_pos(f) if mode == "pos" else xml_pos(f)
        ref, nblk = block(out, k, len(p))
        d = maxdx(p, ref)
        ok &= d < 1e-6
        print(f"{f}: max |dx| vs block {k or nblk} of {nblk} in {out.split('/')[-1]}: {d:.1e} A")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
