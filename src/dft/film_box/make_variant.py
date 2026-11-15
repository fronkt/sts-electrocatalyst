#!/usr/bin/env python3
"""Variant of a pw.x input for the amendment-8 runs: cold start, chosen moments, optional U = 0.

  python3 make_variant.py IN.in NEW.in PREFIX [--calc relax|scf] [--u0] [--conv-thr 5.0d-6]
                          [--species-mag K=V] ...

Always removes startingwfc/startingpot = 'file' (cold start). --u0 sets every Hubbard U in the
HUBBARD card to 1.0d-8 eV (numerically zero, as in the U-ramp stage). --species-mag K=V sets
starting_magnetization(K). Positions and everything else are copied unchanged. Prints the
species -> starting-moment map and the U lines so the result can be checked before launch.
Stdlib only, so it runs on the box.
"""
import re
import sys


def main():
    a = sys.argv[1:]
    src, dst, prefix = a[:3]
    opts = a[3:]
    t = open(src).read()
    t, n = re.subn(r"prefix = '[^']*'", f"prefix = '{prefix}'", t, count=1)
    assert n == 1, "no prefix line"
    t = re.sub(r"(?m)^\s*starting(wfc|pot) = 'file'\n", "", t)
    i = 0
    while i < len(opts):
        o = opts[i]
        if o == "--calc":
            t, n = re.subn(r"calculation = '[^']*'", f"calculation = '{opts[i + 1]}'", t, count=1)
            assert n == 1, "no calculation line"
            i += 2
        elif o == "--u0":
            head, card = t.split("HUBBARD (atomic)\n", 1)
            card, n = re.subn(r"(?m)^U (\S+) \S+$", r"U \1 1.0d-8", card)
            assert n >= 1, "no U lines in the HUBBARD card"
            t = head + "HUBBARD (atomic)\n" + card
            i += 1
        elif o == "--conv-thr":
            t, n = re.subn(r"(?m)^(\s*)conv_thr = \S+", rf"\g<1>conv_thr = {opts[i + 1]}", t, count=1)
            assert n == 1, "no conv_thr line"
            i += 2
        elif o == "--species-mag":
            k, v = opts[i + 1].split("=")
            t, n = re.subn(rf"starting_magnetization\({k}\) = \S+", f"starting_magnetization({k}) = {v}", t)
            assert n == 1, f"no starting_magnetization({k})"
            i += 2
        else:
            raise SystemExit(f"unknown option {o}")
    assert "startingwfc" not in t and "startingpot" not in t, "a file start survived"
    open(dst, "w", newline="\n").write(t)
    nt = int(re.search(r"ntyp = (\d+)", t).group(1))
    names = [s.split()[0] for s in t.split("ATOMIC_SPECIES\n", 1)[1].split("\n")[:nt]]
    mags = {int(k): v for k, v in re.findall(r"starting_magnetization\((\d+)\) = (\S+)", t)}
    calc = re.search(r"calculation = '([^']*)'", t).group(1)
    thr = re.search(r"(?m)^\s*conv_thr = (\S+)", t).group(1)
    us = re.findall(r"(?m)^U \S+ \S+$", t)
    print(f"{dst}: {calc}, prefix {prefix}, conv_thr {thr}, cold start; moments "
          + ", ".join(f"{s}={mags.get(j + 1, '0')}" for j, s in enumerate(names)) + "; " + "; ".join(us))


if __name__ == "__main__":
    main()
