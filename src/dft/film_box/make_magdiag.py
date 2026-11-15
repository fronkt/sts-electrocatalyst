#!/usr/bin/env python3
"""Single-point SCF input that starts a state in a chosen magnetic configuration (amendment 7).

  python3 make_magdiag.py IN.in NEW.in PREFIX [--species-mag K=V] [--relabel IDX,IDX:LABEL:MAG]

IN.in is a relax input (positions already the geometry wanted). The output is an scf input with
the same Hamiltonian, conv_thr 1e-5, cold start (any startingwfc/startingpot='file' removed).
--species-mag 2=0.05     sets starting_magnetization(2).
--relabel 3,4,27,28:Ni2:0.17  gives atoms 3, 4, 27, 28 (1-based) a new species label with its own
                         starting moment; same mass, pseudopotential and Hubbard U as the element.
Stdlib only, so it runs on the box.
"""
import re
import sys


def main():
    a = sys.argv[1:]
    src, dst, prefix = a[:3]
    opts = a[3:]
    t = open(src).read()
    t = re.sub(r"calculation = '[^']*'", "calculation = 'scf'", t, count=1)
    t = re.sub(r"prefix = '[^']*'", f"prefix = '{prefix}'", t, count=1)
    t = re.sub(r"(?m)^\s*starting(wfc|pot) = 'file'\n", "", t)
    t, n = re.subn(r"(?m)^(\s*)conv_thr = \S+", r"\g<1>conv_thr = 1.0d-5", t, count=1)
    assert n == 1, "no conv_thr line"
    i = 0
    while i < len(opts):
        if opts[i] == "--species-mag":
            k, v = opts[i + 1].split("=")
            t, n = re.subn(rf"starting_magnetization\({k}\) = \S+", f"starting_magnetization({k}) = {v}", t)
            assert n == 1, f"no starting_magnetization({k})"
        elif opts[i] == "--relabel":
            idx, label, mag = opts[i + 1].split(":")
            idx = [int(x) for x in idx.split(",")]
            elem = re.match(r"[A-Z][a-z]?", label).group(0)
            ntyp = int(re.search(r"ntyp = (\d+)", t).group(1)) + 1
            t = re.sub(r"ntyp = \d+", f"ntyp = {ntyp}", t, count=1)
            t, n = re.subn(r"(?m)^(\s*starting_magnetization\(\d+\) = \S+\n)(?!\s*starting_magnetization)",
                           rf"\g<1>  starting_magnetization({ntyp}) = {mag}\n", t, count=1)
            assert n == 1, "could not append starting_magnetization"
            # The new species must be LAST in ATOMIC_SPECIES: pw.x numbers starting_magnetization(i)
            # by species order, and (ntyp) was just appended for it.
            head, rest = t.split("ATOMIC_SPECIES\n", 1)
            lines = rest.split("\n")
            nsp = ntyp - 1
            species, tail_lines = lines[:nsp], lines[nsp:]
            sp = [s for s in species if s.split() and s.split()[0] == elem]
            assert len(sp) == 1, f"need exactly one {elem} line in ATOMIC_SPECIES, got {len(sp)}"
            _, mass, pseudo = sp[0].split()
            species.append(f"  {label}  {mass}  {pseudo}")
            t = head + "ATOMIC_SPECIES\n" + "\n".join(species + tail_lines)
            order = [s.split()[0] for s in species]
            assert order[ntyp - 1] == label, order
            hu = re.search(rf"(?m)^U {elem}-(\S+) (\S+)$", t)
            if hu:
                t = t.replace(hu.group(0), hu.group(0) + f"\nU {label}-{hu.group(1)} {hu.group(2)}", 1)
            head, tail = t.split("ATOMIC_POSITIONS angstrom\n", 1)
            rows = tail.split("\n")
            for j in idx:
                r = rows[j - 1].split()
                assert r[0] == elem, f"atom {j} is {r[0]}, not {elem}"
                rows[j - 1] = rows[j - 1].replace(f" {elem} ", f" {label} ", 1)
            t = head + "ATOMIC_POSITIONS angstrom\n" + "\n".join(rows)
        else:
            raise SystemExit(f"unknown option {opts[i]}")
        i += 2
    open(dst, "w", newline="\n").write(t)
    nt = int(re.search(r"ntyp = (\d+)", t).group(1))
    names = [s.split()[0] for s in t.split("ATOMIC_SPECIES\n", 1)[1].split("\n")[:nt]]
    mags = {int(k): v for k, v in re.findall(r"starting_magnetization\((\d+)\) = (\S+)", t)}
    print(f"{dst}: scf, prefix {prefix}, options {' '.join(opts) or 'none'}; starting moments: "
          + ", ".join(f"{s}={mags.get(i + 1, '0')}" for i, s in enumerate(names)))


if __name__ == "__main__":
    main()
