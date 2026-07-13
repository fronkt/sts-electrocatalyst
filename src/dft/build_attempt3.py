"""Attempt-3 inputs for adslab relaxations that resisted the beta=0.1 restart.

Strategy: across ALL prior attempts' outputs, find the geometry with the lowest
evaluated force ("Total force" i corresponds to the positions it was computed at:
ATOMIC_POSITIONS block i-1, or the original input positions for i=1), splice that
into the original input, and switch to conjugate-gradient diagonalization
(diagonalization='cg', mixing_beta=0.1, electron_maxstep=500). CG is 2-3x slower
per iteration but robust against the charge/spin sloshing that kills Davidson here.

Writes <job>.in.attempt3 next to the originals.
"""
import re
from pathlib import Path

RUNS = Path(__file__).resolve().parents[2] / "runs"

# (element, job, [candidate outputs relative to <El>_slab/])
CASES = [
    ("Co", "s0_O",   ["s0_O.out.attempt1"]),
    ("Co", "s0_OOH", ["s0_OOH.out.attempt1"]),
    ("Ni", "s0_OOH", ["s0_OOH.out.attempt1", "s0_OOH.out"]),
    ("Cr", "s0_OH",  ["s0_OH.out.attempt1", "s0_OH.out"]),
    ("Mn", "s0_OOH", ["s0_OOH.out.attempt1"]),
]


def forces_and_blocks(out_path: Path):
    """Return ([force values], [ATOMIC_POSITIONS blocks as line-lists])."""
    lines = out_path.read_text(errors="replace").splitlines()
    forces, blocks = [], []
    i = 0
    while i < len(lines):
        l = lines[i]
        if "Total force" in l:
            forces.append(float(l.split("=")[1].split()[0]))
        elif l.startswith("ATOMIC_POSITIONS"):
            blk = [l]
            j = i + 1
            while j < len(lines) and re.match(r"^[A-Z][a-z]?\s+[-\d]", lines[j]):
                blk.append(lines[j].rstrip())
                j += 1
            blocks.append(blk)
            i = j - 1
        i += 1
    return forces, blocks


def robustify(text: str) -> str:
    text = re.sub(r"mixing_beta\s*=\s*[\d.]+", "mixing_beta = 0.1", text)
    text = re.sub(r"electron_maxstep\s*=\s*\d+", "electron_maxstep = 500", text)
    if "diagonalization" in text:
        text = re.sub(r"diagonalization\s*=\s*'\w+'", "diagonalization = 'cg'", text)
    else:
        text = text.replace("&ELECTRONS", "&ELECTRONS\n  diagonalization = 'cg'", 1)
    return text


def main() -> None:
    for elem, job, outs in CASES:
        d = RUNS / f"{elem}_slab"
        orig = (d / f"{job}.in").read_text()
        nat = int(re.search(r"nat\s*=\s*(\d+)", orig).group(1))

        best_force, best_block, best_src = float("inf"), None, "original input"
        for name in outs:
            p = d / name
            if not p.exists():
                print(f"  note: {elem}/{name} missing, skipped")
                continue
            forces, blocks = forces_and_blocks(p)
            for i, f in enumerate(forces):
                if f < best_force:
                    # force_i is evaluated at block_{i-1}; i==0 -> original geometry
                    blk = blocks[i - 1] if i >= 1 and i - 1 < len(blocks) else None
                    if blk is None or len(blk) - 1 == nat:
                        best_force, best_block = f, blk
                        best_src = f"{name} step {i} (F={f:.4f})" if blk else "original input"

        text = orig
        if best_block is not None:
            new = re.sub(
                r"ATOMIC_POSITIONS[^\n]*\n(?:[ \t]*[A-Z][a-z]?\s+[^\n]*\n?)+",
                "\n".join(best_block) + "\n",
                text,
            )
            assert new != text, f"{elem}/{job}: splice failed"
            text = new

        (d / f"{job}.in.attempt3").write_text(robustify(text))
        print(f"OK {elem}/{job} <- {best_src}")


if __name__ == "__main__":
    main()
