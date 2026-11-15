#!/usr/bin/env python3
"""U-ramp start for a pw.x relax input (amendment 5). Stdlib only; runs on the box.

  python3 make_ramp.py inputs/X.in [NEW_PREFIX]

Writes  inputs/X_u0.in      same geometry, calculation='scf', no HUBBARD card, conv_thr 1e-5
        inputs/X_nofile.in  the unchanged relax input (fallback if the U=0 SCF fails)
and rewrites inputs/X.in to start from the U=0 wavefunctions and density
(startingwfc/startingpot = 'file'; same prefix and outdir, so it reads X_u0's save directory).
With NEW_PREFIX the three files are written as inputs/NEW_PREFIX*.in with that prefix.
Final energies are still PBE+U; only the SCF starting point changes.
"""
import os
import re
import sys

src = sys.argv[1]
text = open(src).read()
if len(sys.argv) > 2:
    new = sys.argv[2]
    text = re.sub(r"prefix = '[^']*'", f"prefix = '{new}'", text, count=1)
    stem = os.path.join(os.path.dirname(src), new)
else:
    stem = src[:-3]
if "startingpot" in text:
    raise SystemExit(f"{src} already starts from file")

u0 = text.replace("calculation = 'relax'", "calculation = 'scf'", 1)
u0 = re.sub(r"(?s)\nHUBBARD \(atomic\)\n.*$", "\n", u0)
u0, n = re.subn(r"(?m)^(\s*)conv_thr = \S+", r"\g<1>conv_thr = 1.0d-5", u0, count=1)
if "HUBBARD" in u0 or "'scf'" not in u0 or n != 1:
    raise SystemExit(f"could not build the U=0 input from {src}")
main, n = re.subn(r"(?m)^&ELECTRONS\n", "&ELECTRONS\n  startingwfc = 'file'\n  startingpot = 'file'\n", text, count=1)
if n != 1:
    raise SystemExit("no &ELECTRONS namelist")
for path, body in ((stem + "_u0.in", u0), (stem + "_nofile.in", text), (stem + ".in", main)):
    with open(path, "w", newline="\n") as f:
        f.write(body)
print(f"ramp: {stem}_u0.in (U=0 scf) -> {stem}.in (PBE+U relax from file); fallback {stem}_nofile.in")
