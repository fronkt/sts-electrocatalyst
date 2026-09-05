#!/usr/bin/env python3
"""Re-realise the S0 gate-(e) projector pair on Anvil at np = 128 (adopted 2026-09-05).

The two banked legs in runs/s0/e_proj/ (s0_O__u715_atomic, s0_O__u715_ortho) ran on
a Vast box at np = 20 while every sibling of P-PROJ's eight ran on Anvil at np = 128
(runs/a0/m_pproj.txt), so the flagship pairing is a cross-machine composite. This
copies the two decks BYTE-IDENTICAL into runs/a0/eproj_np128/ (the diff is asserted
empty) and writes the A0 manifest runs/a0/m_eproj_np128.txt for anvil/47_submit_a0.sh,
nk = 4 to match the p_proj siblings.

Readout rule inherited from A8.5 (docs/43-prereg-week1-factorial.md:1613-1621): a leg
AGREES with its banked original when |dE| <= 1e-5 Ry. Nothing elective.

The driver rewrites outdir and pseudo_dir at run time, so the decks need no edit.
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "runs" / "s0" / "e_proj"
OUT = REPO / "runs" / "a0" / "eproj_np128"
MANIFEST = REPO / "runs" / "a0" / "m_eproj_np128.txt"
DECKS = ("s0_O__u715_atomic", "s0_O__u715_ortho")
NK = 4
EXCLUDE = "a024,a049,a050,a088,a196,a220,a223,a171,a120,a200"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for stem in DECKS:
        src = SRC / f"{stem}.in"
        dst = OUT / f"{stem}.in"
        data = src.read_bytes()
        if b"\r" in data:
            raise SystemExit(f"{src}: source deck carries CR bytes; refuse to clone it")
        if dst.exists() and dst.read_bytes() != data:
            raise SystemExit(f"{dst} exists with different content; refusing to overwrite")
        shutil.copyfile(src, dst)
        assert dst.read_bytes() == data, "copy is not byte-identical"
        rows.append((stem, md5(dst), md5(src)))
        assert rows[-1][1] == rows[-1][2]

    banked = {}
    for stem in DECKS:
        out = SRC / f"{stem}.out"
        final = [ln for ln in out.read_text(encoding="utf-8", errors="replace").splitlines() if ln.startswith("!")]
        banked[stem] = final[-1].strip() if final else "NA"

    lines = [
        "# eproj_np128 manifest -- the S0 gate-(e) pair re-realised on Anvil at np = 128.",
        "# Built by src/dft/build_eproj_np128.py. Each deck is BYTE-IDENTICAL to its",
        "# runs/s0/e_proj/<stem>.in source (md5 asserted equal at build).",
        "#",
        "# WHY. The banked legs print 'running on 20 processor cores' (Vast) while every",
        "# p_proj sibling ran at np = 128 on Anvil (runs/a0/m_pproj.txt), so the flagship",
        "# pairing is a cross-machine composite. This closes that.",
        "#",
        "# READOUT, inherited from A8.5 (docs/43:1613-1621): a leg AGREES with its banked",
        "# original when |dE| <= 1e-5 Ry. The paired difference E(atomic) - E(ortho) is",
        "# re-formed from the Anvil pair and printed beside the banked one. No banked",
        "# value moves in any branch.",
        "#",
        "# Banked final energies (the '!' line of each runs/s0/e_proj/<stem>.out):",
    ]
    for stem in DECKS:
        lines.append(f"#   {stem:22s} {banked[stem]}")
    lines += [
        "#",
        "# nk = 4 matches runs/a0/m_pproj.txt; NP = 128 is a multiple of it.",
        "#",
        f"# SUBMIT WITH EXCLUDE={EXCLUDE}",
        "#",
        "# md5 of each deck (equal to its source by construction):",
    ]
    for stem, h, _ in rows:
        lines.append(f"#   {stem:22s} {h}")
    lines += ["#", "# Runnable rows are: dir job suffix nk"]
    for stem in DECKS:
        lines.append(f"a0/eproj_np128 {stem} .in {NK}")
    data = ("\n".join(lines) + "\n").encode("utf-8")
    if MANIFEST.exists() and MANIFEST.read_bytes() != data:
        raise SystemExit(f"{MANIFEST} exists with different content; refusing to overwrite")
    MANIFEST.write_bytes(data)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
