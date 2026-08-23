#!/usr/bin/env python3
"""A9.7 act 3: record the stored force precision of the OC20 val_id artefact.
Format observation only — no census, no exact-zero tabulation."""
import lzma, re, sys, glob, os
d = sys.argv[1]
files = sorted(glob.glob(os.path.join(d, "*.extxyz.xz")))
idx = [0, 99, 249, 399, 499]
tok = re.compile(r"^-?\d+\.\d{8}$")
report = []
for i in idx:
    f = files[i]
    frames = 0
    checked = 0
    bad = None
    props = None
    with lzma.open(f, "rt") as fh:
        for line in fh:
            if line.startswith("Lattice="):
                frames += 1
                if props is None:
                    m = re.search(r"Properties=(\S+)", line)
                    props = m.group(1) if m else "?"
                continue
            parts = line.split()
            if len(parts) >= 9 and parts[0][0].isalpha():
                for t in parts[-3:]:
                    checked += 1
                    if not tok.match(t):
                        bad = (t, checked)
                        break
            if bad:
                break
    report.append((os.path.basename(f), frames, checked, props, bad))
for r in report:
    print(r)
