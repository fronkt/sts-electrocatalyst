#!/usr/bin/env python3
"""Amendment 23 B: PBE+U single point at a U = 0 state's geometry, started from that state's own
converged U = 0 density.

  python3 make_u_sp.py LAST.in NEW.in PREFIX OUTDIR PSEUDO_DIR

LAST.in is the state's U = 0 input with its final (or accepted) geometry already in ATOMIC_POSITIONS
(qe_restart_input.py). The output differs from it only in:
  calculation 'scf'; prefix; outdir; pseudo_dir; startingpot = 'file' (startingwfc removed: atomic+random);
  conv_thr 1.0d-5; electron_maxstep 200; mixing_beta 0.05; mixing_ndim 20; mixing_mode 'local-TF';
  the HUBBARD card's U values set to the registered PBE+U values (Dudarev, atomic projectors):
  Fe-3d 5.3, Ni-3d 6.2, and Ni2-3d 6.2 (Ni2 is the same element with its own starting moment).
Every other line (cell, positions, species, pseudopotentials, cutoffs, smearing, k-points, dipole
correction, starting moments) is copied unchanged. Stdlib only, so it runs on the box.
"""
import re
import sys

U_EV = {"Fe": "5.3", "Ni": "6.2"}


def sub1(pat, rep, t, what):
    t, n = re.subn(pat, rep, t, count=1)
    if n != 1:
        raise SystemExit(f"no {what} line")
    return t


def set_in_namelist(t, nl, key, val):
    """Replace KEY in namelist NL, or append it at the end of NL if absent."""
    m = re.search(rf"(?ms)^&{nl}\n(.*?)^\s*/\s*$", t)
    if not m:
        raise SystemExit(f"no &{nl} namelist")
    body = m.group(1)
    if re.search(rf"(?m)^\s*{key}\s*=", body):
        body2, n = re.subn(rf"(?m)^(\s*){key}\s*=.*$", rf"\g<1>{key} = {val}", body)
        if n != 1:
            raise SystemExit(f"{key} appears {n} times in &{nl}")
    else:
        body2 = body + f"  {key} = {val}\n"
    return t[:m.start(1)] + body2 + t[m.end(1):]


def main():
    src, dst, prefix, outdir, pseudo = sys.argv[1:6]
    t = open(src).read()
    t = sub1(r"calculation = '[^']*'", "calculation = 'scf'", t, "calculation")
    t = sub1(r"prefix = '[^']*'", f"prefix = '{prefix}'", t, "prefix")
    t = sub1(r"outdir = '[^']*'", f"outdir = '{outdir}'", t, "outdir")
    t = sub1(r"pseudo_dir = '[^']*'", f"pseudo_dir = '{pseudo}'", t, "pseudo_dir")
    t = re.sub(r"(?m)^\s*startingwfc\s*=.*\n", "", t)
    t = set_in_namelist(t, "ELECTRONS", "startingpot", "'file'")
    t = set_in_namelist(t, "ELECTRONS", "conv_thr", "1.0d-5")
    t = set_in_namelist(t, "ELECTRONS", "electron_maxstep", "200")
    t = set_in_namelist(t, "ELECTRONS", "mixing_beta", "0.05")
    t = set_in_namelist(t, "ELECTRONS", "mixing_ndim", "20")
    t = set_in_namelist(t, "ELECTRONS", "mixing_mode", "'local-TF'")
    # &IONS is kept, as in the C1-C7 single points (make_magdiag.py); pw.x ignores it for a scf
    head, card = t.split("HUBBARD (atomic)\n", 1)
    lines = card.split("\n")
    nu = 0
    for i, ln in enumerate(lines):
        m = re.fullmatch(r"U (\S+)-3d (\S+)", ln.strip())
        if not m:
            continue
        el = re.sub(r"\d+$", "", m.group(1))
        if el not in U_EV:
            raise SystemExit(f"no registered U for {m.group(1)}")
        if float(m.group(2).replace("d", "e")) > 1e-6:
            raise SystemExit(f"{ln!r}: the source is not a U = 0 input")
        lines[i] = f"U {m.group(1)}-3d {U_EV[el]}"
        nu += 1
    if nu == 0:
        raise SystemExit("no U lines in the HUBBARD card")
    t = head + "HUBBARD (atomic)\n" + "\n".join(lines)
    open(dst, "w", newline="\n").write(t)
    us = re.findall(r"(?m)^U \S+ \S+$", t)
    print(f"{dst}: scf, prefix {prefix}, start from file; " + "; ".join(us))


if __name__ == "__main__":
    main()
