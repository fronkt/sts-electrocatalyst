#!/usr/bin/env python3
"""Build the CrO2 q = 3x3x3 hp.x pair (A12b rider, adopted 2026-09-05).

Two legs, both projectors, cloned from the banked q222 decks with the smallest
possible diff, asserted at build time:

  scf__cro2_atomic_q333.in  <- runs/hp_tio2/scf__cro2.in            {prefix, outdir}
  hp__cro2_atomic_q333.in   <- runs/hp_tio2/hp__cro2_q222.in        {prefix, outdir, nq}
  scf__cro2_ortho_q333.in   <- runs/hp_cro2_ortho/scf__cro2_ortho.in {prefix, outdir}
  hp__cro2_ortho_q333.in    <- runs/hp_cro2_ortho/hp__cro2_ortho_q222.in {prefix, outdir, nq}

Outputs land in runs/hp_cro2_q333/ -- A8.8-isolated from both banked directories.
The driver (anvil/52_hp.slurm) rewrites outdir and pseudo_dir at run time, so the
outdir lines here are placeholders that only need to be distinct per leg.

The build is reproducible: running it twice yields byte-identical decks. The
manifest records the md5 of each deck and the exact diff against its source.
Nothing here is a threshold; the readout rule is the inherited 0.2 eV q-mesh
threshold (docs/43-prereg-week1-factorial.md:276, A12b.R2 at :3497-3505).
"""
from __future__ import annotations

import difflib
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "runs" / "hp_cro2_q333"

LEGS = {
    "atomic": {
        "scf_src": REPO / "runs/hp_tio2/scf__cro2.in",
        "hp_src": REPO / "runs/hp_tio2/hp__cro2_q222.in",
    },
    "ortho": {
        "scf_src": REPO / "runs/hp_cro2_ortho/scf__cro2_ortho.in",
        "hp_src": REPO / "runs/hp_cro2_ortho/hp__cro2_ortho_q222.in",
    },
}

PREFIX_RE = re.compile(r"^(\s*prefix\s*=\s*')[^']*(')", re.M)
OUTDIR_RE = re.compile(r"^(\s*outdir\s*=\s*')[^']*(')", re.M)
NQ_RE = re.compile(r"^(\s*)nq1\s*=\s*\d+\s*,\s*nq2\s*=\s*\d+\s*,\s*nq3\s*=\s*\d+\s*$", re.M)


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def read_lf(path: Path) -> str:
    text = path.read_bytes().decode("utf-8")
    if "\r" in text:
        raise SystemExit(f"{path}: source deck carries CR bytes; refuse to clone it")
    return text


def clone(text: str, prefix: str, nq: int | None) -> str:
    out, n = PREFIX_RE.subn(rf"\g<1>{prefix}\g<2>", text, count=1)
    assert n == 1, "prefix line not found exactly once"
    out, n = OUTDIR_RE.subn(rf"\g<1>./tmp_{prefix}\g<2>", out, count=1)
    assert n == 1, "outdir line not found exactly once"
    if nq is not None:
        out, n = NQ_RE.subn(rf"\g<1>nq1 = {nq}, nq2 = {nq}, nq3 = {nq}", out, count=1)
        assert n == 1, "nq line not found exactly once"
    return out


def diff_lines(a: str, b: str) -> list[str]:
    return [
        ln.rstrip("\n")
        for ln in difflib.unified_diff(a.splitlines(True), b.splitlines(True), n=0)
        if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))
    ]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for leg, src in LEGS.items():
        prefix = f"cro2_{leg}_q333"
        scf_text = read_lf(src["scf_src"])
        hp_text = read_lf(src["hp_src"])
        scf_new = clone(scf_text, prefix, None)
        hp_new = clone(hp_text, prefix, 3)

        d_scf = diff_lines(scf_text, scf_new)
        d_hp = diff_lines(hp_text, hp_new)
        # exactly {prefix, outdir} on the SCF; exactly {prefix, outdir, nq} on hp
        assert len(d_scf) == 4, d_scf
        assert len(d_hp) == 6, d_hp
        assert any("nq1 = 3, nq2 = 3, nq3 = 3" in ln for ln in d_hp), d_hp
        assert "HUBBARD" not in "\n".join(d_scf), "the projector line must not change"

        scf_path = OUT / f"scf__cro2_{leg}_q333.in"
        hp_path = OUT / f"hp__cro2_{leg}_q333.in"
        for path, text in ((scf_path, scf_new), (hp_path, hp_new)):
            data = text.encode("utf-8")
            if path.exists() and path.read_bytes() != data:
                raise SystemExit(f"{path} exists with different content; refusing to overwrite")
            path.write_bytes(data)
        rows.append((leg, scf_path, src["scf_src"], d_scf, hp_path, src["hp_src"], d_hp))

    lines = [
        "# runs/hp_cro2_q333 -- CrO2 q-mesh check, both projectors at q = 3x3x3",
        "#",
        "# A12b rider adopted 2026-09-05 (docs/43 dated addendum of that date).",
        "# Built by src/dft/build_hp_cro2_q333.py; rebuild is byte-identical.",
        "# Readout rule inherited, nothing elective: |U(q333) - U(q222)| <= 0.2 eV per leg",
        "# (docs/43-prereg-week1-factorial.md:276; A12b.R2 :3497-3505). The split is",
        "# re-formed at q333 and printed beside the q222 split.",
        "#",
        "# One 52_hp.slurm job per leg: DIR=hp_cro2_q333 SCF=<scf deck> HP=<hp deck>, np=20 nk=4.",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200",
        "#",
        "# md5 of each deck, and its exact diff against the banked source:",
    ]
    for leg, scf_path, scf_src, d_scf, hp_path, hp_src, d_hp in rows:
        for path, src, d in ((scf_path, scf_src, d_scf), (hp_path, hp_src, d_hp)):
            lines.append(f"#   {path.name:28s} {md5(path.read_bytes())}  <- {src.relative_to(REPO).as_posix()}")
            for ln in d:
                lines.append(f"#       {ln}")
    lines.append("#")
    lines.append("# Runnable rows are: leg scf hp")
    for leg, scf_path, _, _, hp_path, _, _ in rows:
        lines.append(f"{leg} {scf_path.name} {hp_path.name}")
    manifest = OUT / "MANIFEST.txt"
    data = ("\n".join(lines) + "\n").encode("utf-8")
    if manifest.exists() and manifest.read_bytes() != data:
        raise SystemExit(f"{manifest} exists with different content; refusing to overwrite")
    manifest.write_bytes(data)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
