"""Attempt-4 inputs: Davidson with very conservative mixing, seeded from the best
available geometry (for Co s0_O, the CG-refined attempt-3 geometry — it came from
an actually-converged electronic state, unlike the Davidson seeds that failed).

Settings: diagonalization='david', mixing_beta=0.05, mixing_ndim=16,
electron_maxstep=800. Davidson iterations are ~3x cheaper than CG, so even a
failure costs ~5 h, not ~30 h.
"""
import re
from pathlib import Path

from build_attempt3 import forces_and_blocks

RUNS = Path(__file__).resolve().parents[2] / "runs"

CASES = [
    ("Co", "s0_O",   ["s0_O.out.attempt3"]),
    ("Co", "s0_OOH", ["s0_OOH.out.attempt1"]),
    ("Ni", "s0_OOH", ["s0_OOH.out.attempt1", "s0_OOH.out"]),
    ("Cr", "s0_OH",  ["s0_OH.out.attempt1", "s0_OH.out"]),
    ("Mn", "s0_OOH", ["s0_OOH.out.attempt1"]),
]


def robustify(text: str) -> str:
    text = re.sub(r"mixing_beta\s*=\s*[\d.]+", "mixing_beta = 0.05", text)
    text = re.sub(r"electron_maxstep\s*=\s*\d+", "electron_maxstep = 800", text)
    if "diagonalization" in text:
        text = re.sub(r"diagonalization\s*=\s*'\w+'", "diagonalization = 'david'", text)
    else:
        text = text.replace("&ELECTRONS", "&ELECTRONS\n  diagonalization = 'david'", 1)
    if "mixing_ndim" not in text:
        text = text.replace("&ELECTRONS", "&ELECTRONS\n  mixing_ndim = 16", 1)
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
            for i, f in enumerate(forces, start=1):
                if f < best_force:
                    blk = blocks[i - 2] if i >= 2 and i - 2 < len(blocks) else None
                    if blk is None or len(blk) - 1 == nat:
                        best_force, best_block = f, blk
                        best_src = f"{name} step {i} (F={f:.4f})" if blk else f"{name} step 1 geometry=input (F={f:.4f})"

        text = orig
        if best_block is not None:
            new = re.sub(
                r"ATOMIC_POSITIONS[^\n]*\n(?:[ \t]*[A-Z][a-z]?\s+[^\n]*\n?)+",
                "\n".join(best_block) + "\n",
                text,
            )
            assert new != text, f"{elem}/{job}: splice failed"
            text = new

        (d / f"{job}.in.attempt4").write_text(robustify(text))
        print(f"OK {elem}/{job} <- {best_src}")


if __name__ == "__main__":
    main()
